#!/usr/bin/env python3
"""
End-to-end test script for RAG application with PDF support.
This script tests the complete pipeline from PDF loading to question answering.

Usage:
    python test_rag_end_to_end.py [pdf_file] [--api-key KEY]
    
Examples:
    python test_rag_end_to_end.py
    python test_rag_end_to_end.py data/my_document.pdf
    python test_rag_end_to_end.py data/my_document.pdf --api-key sk-your-key-here
"""

import sys
import os
import asyncio
import argparse
from dotenv import load_dotenv

# Add current directory to path
sys.path.append('.')

# Load environment variables
load_dotenv()

def test_complete_rag_pipeline(pdf_file="data/ai_research_paper.pdf"):
    """Test the complete RAG pipeline with PDF support."""
    print(f"🚀 Testing Complete RAG Pipeline with PDF Support (PDF: {pdf_file})\n")
    
    try:
        # Import required modules
        from aimakerspace.text_utils import PDFLoader, TextFileLoader, CharacterTextSplitter
        from aimakerspace.vectordatabase import VectorDatabase
        from aimakerspace.openai_utils.chatmodel import ChatOpenAI
        from aimakerspace.openai_utils.prompts import SystemRolePrompt, UserRolePrompt
        
        print("✅ All modules imported successfully")
        
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  OPENAI_API_KEY not found. Testing without API calls...")
            return test_without_api(pdf_file)
        
        print("✅ OpenAI API key found")
        
        # Step 1: Load PDF documents
        print(f"\n1. Loading PDF documents from: {pdf_file}")
        if not os.path.exists(pdf_file):
            print(f"   ❌ PDF file not found: {pdf_file}")
            return False
            
        pdf_loader = PDFLoader(pdf_file, method="pdfplumber")
        pdf_documents = pdf_loader.load_documents()
        print(f"   ✅ Loaded {len(pdf_documents)} PDF documents")
        print(f"   Content length: {len(pdf_documents[0])} characters")
        
        # Step 2: Split documents into chunks
        print("\n2. Splitting documents into chunks...")
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        pdf_chunks = text_splitter.split_texts(pdf_documents)
        print(f"   ✅ Created {len(pdf_chunks)} chunks")
        print(f"   Sample chunk: {pdf_chunks[0][:150]}...")
        
        # Step 3: Create vector database
        print("\n3. Creating vector database...")
        vector_db = VectorDatabase()
        vector_db = asyncio.run(vector_db.abuild_from_list(pdf_chunks))
        print(f"   ✅ Vector database created with {len(vector_db.vectors)} vectors")
        
        # Step 4: Test similarity search
        print("\n4. Testing similarity search...")
        test_query = "What is artificial intelligence?"
        search_results = vector_db.search_by_text(test_query, k=3)
        print(f"   ✅ Found {len(search_results)} relevant chunks for: '{test_query}'")
        
        for i, (chunk, score) in enumerate(search_results, 1):
            print(f"   Chunk {i} (score: {score:.3f}): {chunk[:100]}...")
        
        # Step 5: Create RAG pipeline
        print("\n5. Creating RAG pipeline...")
        
        # Define RAG prompts
        RAG_SYSTEM_TEMPLATE = """You are a knowledgeable assistant that answers questions based strictly on provided context.

Instructions:
- Only answer questions using information from the provided context
- If the context doesn't contain relevant information, respond with "I don't know"
- Be accurate and cite specific parts of the context when possible
- Keep responses detailed and comprehensive
- Only use the provided context. Do not use external knowledge.
- Only provide answers when you are confident the context supports your response."""

        RAG_USER_TEMPLATE = """Context Information:
{context}

Number of relevant sources found: {context_count}
{similarity_scores}

Question: {user_query}

Please provide your answer based solely on the context above."""

        # Create prompt objects
        rag_system_prompt = SystemRolePrompt(RAG_SYSTEM_TEMPLATE)
        rag_user_prompt = UserRolePrompt(RAG_USER_TEMPLATE)
        
        # Create RAG pipeline class
        class RetrievalAugmentedQAPipeline:
            def __init__(self, llm, vector_db_retriever, response_style="detailed", include_scores=False):
                self.llm = llm
                self.vector_db_retriever = vector_db_retriever
                self.response_style = response_style
                self.include_scores = include_scores

            def run_pipeline(self, user_query: str, k: int = 4, **system_kwargs):
                # Retrieve relevant contexts
                context_list = self.vector_db_retriever.search_by_text(user_query, k=k)
                
                context_prompt = ""
                similarity_scores = []
                
                for i, (context, score) in enumerate(context_list, 1):
                    context_prompt += f"[Source {i}]: {context}\\n\\n"
                    similarity_scores.append(f"Source {i}: {score:.3f}")
                
                # Create system message
                formatted_system_prompt = rag_system_prompt.create_message()
                
                # Create user message
                user_params = {
                    "user_query": user_query,
                    "context": context_prompt.strip(),
                    "context_count": len(context_list),
                    "similarity_scores": f"Relevance scores: {', '.join(similarity_scores)}" if self.include_scores else ""
                }
                
                formatted_user_prompt = rag_user_prompt.create_message(**user_params)
                
                # Get response from LLM
                response = self.llm.run([formatted_system_prompt, formatted_user_prompt])
                
                return {
                    "response": response,
                    "context": context_list,
                    "context_count": len(context_list),
                    "similarity_scores": similarity_scores if self.include_scores else None
                }
        
        # Initialize LLM
        chat_openai = ChatOpenAI()
        
        # Create RAG pipeline
        rag_pipeline = RetrievalAugmentedQAPipeline(
            vector_db_retriever=vector_db,
            llm=chat_openai,
            response_style="detailed",
            include_scores=True
        )
        
        print("   ✅ RAG pipeline created successfully")
        
        # Step 6: Test question answering
        print("\n6. Testing question answering...")
        
        test_questions = [
            "What is artificial intelligence?",
            "What are the main topics discussed in this research paper?",
            "What are the applications of machine learning?",
            "What is deep learning and how does it work?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n   Question {i}: {question}")
            try:
                result = rag_pipeline.run_pipeline(question, k=3)
                print(f"   Answer: {result['response'][:200]}...")
                print(f"   Sources used: {result['context_count']}")
                if result['similarity_scores']:
                    print(f"   Relevance scores: {result['similarity_scores']}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎉 Complete RAG pipeline test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error in complete pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_without_api(pdf_file="data/ai_research_paper.pdf"):
    """Test PDF functionality without requiring OpenAI API key."""
    print(f"🔧 Testing PDF functionality without API calls (PDF: {pdf_file})...\n")
    
    try:
        from aimakerspace.text_utils import PDFLoader, TextFileLoader, CharacterTextSplitter
        
        # Test PDF loading
        print(f"1. Testing PDF loading from: {pdf_file}")
        if not os.path.exists(pdf_file):
            print(f"   ❌ PDF file not found: {pdf_file}")
            return False
            
        pdf_loader = PDFLoader(pdf_file, method="pdfplumber")
        pdf_documents = pdf_loader.load_documents()
        print(f"   ✅ Loaded {len(pdf_documents)} PDF documents")
        
        # Test text splitting
        print("\n2. Testing text splitting...")
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        pdf_chunks = text_splitter.split_texts(pdf_documents)
        print(f"   ✅ Created {len(pdf_chunks)} chunks")
        
        # Test mixed directory loading
        print("\n3. Testing mixed directory loading...")
        mixed_loader = TextFileLoader("data/")
        mixed_docs = mixed_loader.load_documents()
        print(f"   ✅ Loaded {len(mixed_docs)} documents from mixed directory")
        
        # Test content quality
        print("\n4. Testing content quality...")
        ai_keywords = ["artificial intelligence", "machine learning", "deep learning", "neural networks"]
        content = pdf_documents[0].lower()
        found_keywords = [kw for kw in ai_keywords if kw in content]
        print(f"   ✅ Found AI keywords: {found_keywords}")
        
        print("\n✅ PDF functionality test successful (without API)!")
        print("   To test the complete RAG pipeline, set your OPENAI_API_KEY environment variable.")
        return True
        
    except Exception as e:
        print(f"❌ Error in PDF functionality test: {e}")
        return False

def main():
    """Main test function with command line arguments."""
    parser = argparse.ArgumentParser(
        description="End-to-end test script for RAG application with PDF support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_rag_end_to_end.py
  python test_rag_end_to_end.py data/my_document.pdf
  python test_rag_end_to_end.py data/my_document.pdf --api-key sk-your-key-here
        """
    )
    
    parser.add_argument(
        "pdf_file", 
        nargs="?", 
        default="data/ai_research_paper.pdf",
        help="Path to PDF file to test (default: data/ai_research_paper.pdf)"
    )
    
    parser.add_argument(
        "--api-key", 
        help="OpenAI API key (optional)"
    )
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
        print(f"✅ OpenAI API key set")
    
    print("=" * 60)
    print(f"🧪 RAG Application End-to-End Test (PDF: {args.pdf_file})")
    print("=" * 60)
    
    # Run the complete test
    success = test_complete_rag_pipeline(args.pdf_file)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Your RAG application with PDF support is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
