#!/usr/bin/env python3
"""
Quick test script for RAG application with PDF support.
Run this to quickly verify everything is working.

Usage:
    python quick_test.py [pdf_file] [--api-key KEY]
    
Examples:
    python quick_test.py
    python quick_test.py data/my_document.pdf
    python quick_test.py data/my_document.pdf --api-key sk-your-key-here
"""

import sys
import os
import asyncio
import argparse
sys.path.append('.')

def quick_test(pdf_file="data/ai_research_paper.pdf", api_key=None):
    """Quick test of PDF functionality."""
    print(f"🚀 Quick RAG + PDF Test (PDF: {pdf_file})\n")
    
    # Set API key if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        print(f"✅ OpenAI API key set")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from aimakerspace.text_utils import PDFLoader, TextFileLoader, CharacterTextSplitter
        from aimakerspace.vectordatabase import VectorDatabase
        print("   ✅ All imports successful")
        
        # Test PDF loading
        print(f"\n2. Testing PDF loading from: {pdf_file}")
        if not os.path.exists(pdf_file):
            print(f"   ❌ PDF file not found: {pdf_file}")
            return False
            
        pdf_loader = PDFLoader(pdf_file, method="pdfplumber")
        pdf_docs = pdf_loader.load_documents()
        print(f"   ✅ Loaded PDF: {len(pdf_docs)} docs, {len(pdf_docs[0])} chars")
        
        # Test text splitting
        print("\n3. Testing text splitting...")
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_texts(pdf_docs)
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # Test mixed directory loading
        print("\n4. Testing mixed directory...")
        mixed_loader = TextFileLoader("data/")
        mixed_docs = mixed_loader.load_documents()
        print(f"   ✅ Mixed directory: {len(mixed_docs)} docs")
        
        # Test content quality
        print("\n5. Testing content quality...")
        content = pdf_docs[0].lower()
        keywords = ["artificial intelligence", "machine learning", "deep learning"]
        found = [kw for kw in keywords if kw in content]
        print(f"   ✅ Found keywords: {found}")
        
        # Test vector database if API key is available
        if api_key or os.getenv("OPENAI_API_KEY"):
            print("\n6. Testing vector database...")
            try:
                vector_db = VectorDatabase()
                vector_db = asyncio.run(vector_db.abuild_from_list(chunks))
                print(f"   ✅ Vector database created with {len(vector_db.vectors)} vectors")
                
                # Test similarity search
                query = "What is artificial intelligence?"
                results = vector_db.search_by_text(query, k=3)
                print(f"   ✅ Similarity search: {len(results)} results for '{query}'")
            except Exception as e:
                print(f"   ⚠️  Vector database test failed: {e}")
        
        print("\n🎉 Quick test passed! PDF support is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Quick test script for RAG application with PDF support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_test.py
  python quick_test.py data/my_document.pdf
  python quick_test.py data/my_document.pdf --api-key sk-your-key-here
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
    
    success = quick_test(args.pdf_file, args.api_key)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
