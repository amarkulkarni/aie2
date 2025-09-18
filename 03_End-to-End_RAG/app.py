import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import asyncio

from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter, TextFileLoader
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
from aimakerspace.openai_utils.prompts import SystemRolePrompt, UserRolePrompt

# Additional imports for file processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import striprtf
    RTF_AVAILABLE = True
except ImportError:
    RTF_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables to store the RAG system state
vector_db = None
chat_model = None
pdf_text_chunks = []

# Initialize the chat model
try:
    chat_model = ChatOpenAI(model_name="gpt-4o-mini")
except ValueError as e:
    print(f"Warning: {e}")
    print("Make sure to set your OPENAI_API_KEY environment variable")

# System prompt for Airline Customer Service RAG
RAG_SYSTEM_PROMPT = """You are a professional Airline Customer Service Assistant. You help customers with questions about airline policies, procedures, schedules, bookings, baggage, and services based ONLY on the provided context from airline documents.

IMPORTANT RULES:
1. Only use information from the provided context to answer questions
2. If the context doesn't contain enough information to answer a question, say "I don't have enough information in the provided documents to answer that question. Please contact our customer service team for assistance."
3. Do not make up or hallucinate information
4. If asked about something not related to airline services, politely redirect to airline-related questions
5. Be professional, helpful, and accurate based on the provided context
6. Use airline industry terminology appropriately
7. Always maintain a friendly and professional tone

Context from airline documents:
{context}"""

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    allowed_extensions = {'pdf', 'docx', 'txt', 'rtf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """Extract text from various file types."""
    file_path_obj = Path(file_path)
    
    if file_extension == 'pdf':
        pdf_loader = PDFLoader(file_path)
        pdf_loader.load_file()
        return pdf_loader.documents[0] if pdf_loader.documents else ""
    
    elif file_extension == 'txt':
        text_loader = TextFileLoader(file_path)
        text_loader.load_file()
        return text_loader.documents[0] if text_loader.documents else ""
    
    elif file_extension == 'docx':
        if not DOCX_AVAILABLE:
            raise ValueError("python-docx library not available. Install with: pip install python-docx")
        
        doc = docx.Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    
    elif file_extension == 'rtf':
        if not RTF_AVAILABLE:
            raise ValueError("striprtf library not available. Install with: pip install striprtf")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            rtf_content = file.read()
        return striprtf.striprtf(rtf_content)
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def process_document(file_path: str) -> List[str]:
    """Process any supported document file and return text chunks."""
    global vector_db, pdf_text_chunks
    
    # Get file extension
    file_extension = Path(file_path).suffix.lower().lstrip('.')
    
    # Extract text from file
    document_text = extract_text_from_file(file_path, file_extension)
    
    if not document_text.strip():
        raise ValueError("No text content found in the document")
    
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split(document_text)
    pdf_text_chunks = chunks
    
    # Create vector database and index chunks
    vector_db = VectorDatabase()
    
    # Build vector database asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        vector_db = loop.run_until_complete(vector_db.abuild_from_list(chunks))
    finally:
        loop.close()
    
    return chunks

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle document file upload and processing."""
    global vector_db, pdf_text_chunks
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF, DOCX, TXT, and RTF files are allowed'}), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        file_extension = Path(filename).suffix.lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        # Process the document
        chunks = process_document(temp_path)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'chunks_count': len(chunks),
            'status': 'ready'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing document: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with RAG."""
    global vector_db, chat_model, pdf_text_chunks
    
    if not vector_db:
        return jsonify({'error': 'No documents uploaded yet. Please upload airline documents first.'}), 400
    
    if not chat_model:
        return jsonify({'error': 'Chat model not initialized. Check OPENAI_API_KEY.'}), 500
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Search for relevant chunks
        relevant_chunks = vector_db.search_by_text(
            user_message, 
            k=3,  # Get top 3 most relevant chunks
            return_as_text=True
        )
        
        # Combine relevant chunks as context
        context = "\n\n".join(relevant_chunks)
        
        # Create system prompt with context
        system_prompt = SystemRolePrompt(RAG_SYSTEM_PROMPT.format(context=context))
        user_prompt = UserRolePrompt(user_message)
        
        # Generate response
        messages = [
            system_prompt.create_message(),
            user_prompt.create_message()
        ]
        
        response = chat_model.run(messages)
        
        return jsonify({
            'response': response,
            'context_used': len(relevant_chunks)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating response: {str(e)}'}), 500

@app.route('/status')
def status():
    """Get the current status of the RAG system."""
    global vector_db, pdf_text_chunks
    
    return jsonify({
        'pdf_loaded': vector_db is not None,
        'chunks_count': len(pdf_text_chunks) if pdf_text_chunks else 0,
        'chat_ready': chat_model is not None,
        'supported_formats': ['PDF', 'DOCX', 'TXT', 'RTF']
    })

# For Vercel deployment
if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)

# Vercel entry point
app = app
