# Airline Customer Service Assistant

A web application that allows airline customers to upload airline documents (policies, manuals, schedules, etc.) and get instant answers to their questions using AI-powered retrieval-augmented generation (RAG).

## Features

- **Multi-Format Document Upload**: Upload PDF, DOCX, TXT, and RTF files through a drag-and-drop interface
- **Text Extraction**: Automatically extract text from various document formats
- **Text Chunking**: Split document content into manageable chunks for better retrieval
- **Vector Search**: Use embeddings to find relevant content for user questions
- **AI Chat**: Chat with airline documents using OpenAI's GPT models
- **Context-Aware**: Only answers questions based on the uploaded airline documents
- **Airline-Specific**: Specialized for airline customer service questions about policies, procedures, schedules, and services

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key**:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Application**:
   - Open your browser and go to `http://localhost:5001`
   - Upload airline documents (policies, manuals, schedules, etc.)
   - Start asking questions about flights, bookings, policies, and services!

## How It Works

1. **Document Processing**: When you upload airline documents, the system extracts all text content
2. **Text Chunking**: The text is split into overlapping chunks (1000 characters with 200 character overlap)
3. **Vector Indexing**: Each chunk is converted to embeddings and stored in a vector database
4. **Question Processing**: When you ask a question, the system:
   - Converts your question to an embedding
   - Searches for the most relevant text chunks
   - Uses those chunks as context for the AI model
   - Generates an answer based only on the airline document content

## API Endpoints

- `GET /` - Serve the main web interface
- `POST /upload` - Upload and process airline documents (PDF, DOCX, TXT, RTF)
- `POST /chat` - Send a message and get AI response
- `GET /status` - Check if documents are loaded and system status

## Architecture

The application uses the `aimakerspace` library which provides:
- `PDFLoader`: Extract text from PDF files
- `TextFileLoader`: Extract text from TXT files
- `CharacterTextSplitter`: Split text into chunks
- `VectorDatabase`: Store and search embeddings
- `ChatOpenAI`: Interface with OpenAI's chat models
- `EmbeddingModel`: Generate embeddings for text

Additional libraries for multi-format support:
- `python-docx`: Extract text from DOCX files
- `striprtf`: Extract text from RTF files

## Requirements

- Python 3.8+
- OpenAI API key
- Flask
- PyPDF2 for PDF processing
- NumPy for vector operations
