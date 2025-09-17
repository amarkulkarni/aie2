#!/usr/bin/env python3
"""
Test script for metadata support in VectorDatabase.
Demonstrates how to use metadata with the enhanced vector database.
"""

import sys
import os
import asyncio
sys.path.append('.')

def test_metadata_support():
    """Test the metadata functionality of VectorDatabase."""
    print("🧪 Testing VectorDatabase Metadata Support\n")
    
    try:
        from aimakerspace.vectordatabase import VectorDatabase
        from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
        
        # Test 1: Basic metadata insertion
        print("1. Testing basic metadata insertion...")
        vector_db = VectorDatabase()
        
        # Insert vectors with metadata
        vector_db.insert_with_metadata(
            "Document 1", 
            [1, 2, 3], 
            source="PDF", 
            page=1, 
            category="technical",
            author="John Doe"
        )
        
        vector_db.insert_with_metadata(
            "Document 2", 
            [4, 5, 6], 
            source="TXT", 
            page=2, 
            category="research",
            author="Jane Smith"
        )
        
        print("   ✅ Vectors inserted with metadata")
        
        # Test 2: Search with metadata
        print("\n2. Testing search with metadata...")
        results = vector_db.search([1, 2, 3], k=2, include_metadata=True)
        print(f"   ✅ Search results with metadata: {results}")
        
        # Test 3: Metadata filtering
        print("\n3. Testing metadata filtering...")
        pdf_docs = vector_db.filter_by_metadata(source="PDF")
        research_docs = vector_db.filter_by_metadata(category="research")
        print(f"   ✅ PDF documents: {pdf_docs}")
        print(f"   ✅ Research documents: {research_docs}")
        
        # Test 4: Metadata retrieval and update
        print("\n4. Testing metadata retrieval and update...")
        metadata = vector_db.get_metadata("Document 1")
        print(f"   ✅ Original metadata: {metadata}")
        
        vector_db.update_metadata("Document 1", {"updated": True, "version": "1.1"})
        updated_metadata = vector_db.get_metadata("Document 1")
        print(f"   ✅ Updated metadata: {updated_metadata}")
        
        # Test 5: Build from list with metadata
        print("\n5. Testing build from list with metadata...")
        texts = [
            "This is a technical document about AI.",
            "This is a research paper on machine learning.",
            "This is a user manual for the software."
        ]
        
        metadata_list = [
            {"type": "technical", "domain": "AI", "difficulty": "advanced"},
            {"type": "research", "domain": "ML", "difficulty": "expert"},
            {"type": "manual", "domain": "software", "difficulty": "beginner"}
        ]
        
        vector_db_2 = VectorDatabase()
        vector_db_2 = asyncio.run(vector_db_2.abuild_from_list(texts, metadata_list))
        
        # Search with metadata
        search_results = vector_db_2.search_by_text("artificial intelligence", k=2, include_metadata=True)
        print(f"   ✅ Search results with metadata: {search_results}")
        
        # Filter by metadata
        technical_docs = vector_db_2.filter_by_metadata(type="technical")
        print(f"   ✅ Technical documents: {technical_docs}")
        
        print("\n🎉 All metadata tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_with_metadata():
    """Test PDF loading with metadata support."""
    print("\n📄 Testing PDF with Metadata Support\n")
    
    try:
        from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
        from aimakerspace.vectordatabase import VectorDatabase
        
        # Load PDF
        pdf_loader = PDFLoader("data/ai_research_paper.pdf", method="pdfplumber")
        pdf_docs = pdf_loader.load_documents()
        
        # Split into chunks
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_texts(pdf_docs)
        
        # Create metadata for each chunk
        metadata_list = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": "ai_research_paper.pdf",
                "chunk_id": i,
                "chunk_size": len(chunk),
                "domain": "artificial_intelligence",
                "type": "research_paper",
                "page_estimate": (i // 3) + 1  # Rough page estimate
            }
            metadata_list.append(metadata)
        
        # Build vector database with metadata
        vector_db = VectorDatabase()
        vector_db = asyncio.run(vector_db.abuild_from_list(chunks, metadata_list))
        
        print(f"   ✅ Created vector database with {len(chunks)} chunks and metadata")
        
        # Test search with metadata
        results = vector_db.search_by_text("What is artificial intelligence?", k=3, include_metadata=True)
        print(f"   ✅ Search results with metadata:")
        for i, (text, score, metadata) in enumerate(results, 1):
            print(f"      Result {i}: Score {score:.3f}, Chunk {metadata.get('chunk_id', 'N/A')}, Size {metadata.get('chunk_size', 'N/A')}")
        
        # Test filtering
        large_chunks = vector_db.filter_by_metadata(chunk_size=lambda x: x > 400)
        print(f"   ✅ Large chunks (>400 chars): {len(large_chunks)} found")
        
        print("\n🎉 PDF with metadata test passed!")
        return True
        
    except Exception as e:
        print(f"❌ PDF with metadata test failed: {e}")
        return False

def main():
    """Run all metadata tests."""
    print("=" * 60)
    print("🧪 VectorDatabase Metadata Support Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Metadata Support", test_metadata_support),
        ("PDF with Metadata", test_pdf_with_metadata)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All metadata tests passed! VectorDatabase now supports metadata!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
