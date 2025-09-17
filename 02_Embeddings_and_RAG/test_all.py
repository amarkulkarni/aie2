#!/usr/bin/env python3
"""
Comprehensive test script for RAG application with PDF support.
Tests both with and without OpenAI API key.

Usage:
    python test_all.py [pdf_file] [--api-key KEY]
    
Examples:
    python test_all.py
    python test_all.py data/my_document.pdf
    python test_all.py data/my_document.pdf --api-key sk-your-key-here
"""

import sys
import os
import asyncio
import argparse
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

def test_pdf_loading(pdf_file="data/ai_research_paper.pdf"):
    """Test PDF loading functionality."""
    print(f"📄 Testing PDF Loading (PDF: {pdf_file})...")
    
    try:
        from aimakerspace.text_utils import PDFLoader, TextFileLoader
        
        # Test different PDF methods
        methods = ["pdfplumber", "pymupdf", "pypdf2"]
        for method in methods:
            loader = PDFLoader(pdf_file, method=method)
            docs = loader.load_documents()
            print(f"   ✅ {method}: {len(docs)} docs, {len(docs[0])} chars")
        
        # Test TextFileLoader with PDF
        text_loader = TextFileLoader(pdf_file)
        pdf_docs = text_loader.load_documents()
        print(f"   ✅ TextFileLoader: {len(pdf_docs)} docs")
        
        # Test mixed directory
        mixed_loader = TextFileLoader("data/")
        mixed_docs = mixed_loader.load_documents()
        print(f"   ✅ Mixed directory: {len(mixed_docs)} docs")
        
        return True
        
    except Exception as e:
        print(f"   ❌ PDF loading failed: {e}")
        return False

def test_text_processing(pdf_file="data/ai_research_paper.pdf"):
    """Test text processing functionality."""
    print("\n✂️  Testing Text Processing...")
    
    try:
        from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
        
        # Load PDF
        pdf_loader = PDFLoader(pdf_file, method="pdfplumber")
        pdf_docs = pdf_loader.load_documents()
        
        # Test text splitting
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_texts(pdf_docs)
        print(f"   ✅ Created {len(chunks)} chunks")
        print(f"   ✅ Chunk sizes: {[len(chunk) for chunk in chunks[:3]]}...")
        
        # Test content quality
        content = pdf_docs[0].lower()
        keywords = ["artificial intelligence", "machine learning", "deep learning", "neural networks"]
        found = [kw for kw in keywords if kw in content]
        print(f"   ✅ Found keywords: {found}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Text processing failed: {e}")
        return False

def test_vector_database(pdf_file="data/ai_research_paper.pdf"):
    """Test vector database functionality."""
    print("\n🔍 Testing Vector Database...")
    
    try:
        from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
        from aimakerspace.vectordatabase import VectorDatabase
        
        # Load and split PDF
        pdf_loader = PDFLoader(pdf_file, method="pdfplumber")
        pdf_docs = pdf_loader.load_documents()
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_texts(pdf_docs)
        
        # Create vector database
        vector_db = VectorDatabase()
        vector_db = asyncio.run(vector_db.abuild_from_list(chunks))
        print(f"   ✅ Vector database created with {len(vector_db.vectors)} vectors")
        
        # Test similarity search
        query = "What is artificial intelligence?"
        results = vector_db.search_by_text(query, k=3)
        print(f"   ✅ Similarity search: {len(results)} results for '{query}'")
        
        for i, (chunk, score) in enumerate(results, 1):
            print(f"      Result {i} (score: {score:.3f}): {chunk[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Vector database failed: {e}")
        return False

def test_rag_pipeline(pdf_file="data/ai_research_paper.pdf"):
    """Test complete RAG pipeline."""
    print("\n🤖 Testing RAG Pipeline...")
    
    try:
        from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
        from aimakerspace.vectordatabase import VectorDatabase
        from aimakerspace.openai_utils.chatmodel import ChatOpenAI
        from aimakerspace.openai_utils.prompts import SystemRolePrompt, UserRolePrompt
        
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   ⚠️  No OpenAI API key found. Skipping RAG pipeline test.")
            return True
        
        # Load and process PDF
        pdf_loader = PDFLoader(pdf_file, method="pdfplumber")
        pdf_docs = pdf_loader.load_documents()
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_texts(pdf_docs)
        
        # Create vector database
        vector_db = VectorDatabase()
        vector_db = asyncio.run(vector_db.abuild_from_list(chunks))
        
        # Create RAG pipeline
        class SimpleRAGPipeline:
            def __init__(self, llm, vector_db):
                self.llm = llm
                self.vector_db = vector_db
            
            def ask(self, question, k=3):
                # Get relevant chunks
                results = self.vector_db.search_by_text(question, k=k)
                
                # Create context
                context = "\\n\\n".join([chunk for chunk, _ in results])
                
                # Create messages
                system_msg = {
                    "role": "system", 
                    "content": "Answer the question based only on the provided context. If the context doesn't contain enough information, say 'I don't know'."
                }
                user_msg = {
                    "role": "user", 
                    "content": f"Context: {context}\\n\\nQuestion: {question}"
                }
                
                # Get response
                response = self.llm.run([system_msg, user_msg])
                return response, results
        
        # Initialize LLM and pipeline
        llm = ChatOpenAI()
        rag = SimpleRAGPipeline(llm, vector_db)
        
        # Test question
        question = "What is artificial intelligence?"
        response, sources = rag.ask(question)
        
        print(f"   ✅ Question: {question}")
        print(f"   ✅ Answer: {response[:150]}...")
        print(f"   ✅ Sources used: {len(sources)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ RAG pipeline failed: {e}")
        return False

def main():
    """Run all tests with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test script for RAG application with PDF support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_all.py
  python test_all.py data/my_document.pdf
  python test_all.py data/my_document.pdf --api-key sk-your-key-here
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
    
    print(f"🧪 Comprehensive RAG + PDF Test Suite (PDF: {args.pdf_file})")
    print("=" * 50)
    
    tests = [
        ("PDF Loading", lambda: test_pdf_loading(args.pdf_file)),
        ("Text Processing", lambda: test_text_processing(args.pdf_file)),
        ("Vector Database", lambda: test_vector_database(args.pdf_file)),
        ("RAG Pipeline", lambda: test_rag_pipeline(args.pdf_file))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your RAG application with PDF support is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
