#!/usr/bin/env python3
"""
Simple test script for metadata support in VectorDatabase.
Tests basic metadata functionality without requiring OpenAI API key.
"""

import sys
import os
import numpy as np
sys.path.append('.')

def test_metadata_basic():
    """Test basic metadata functionality without API calls."""
    print("🧪 Testing VectorDatabase Metadata Support (No API Required)\n")
    
    try:
        from aimakerspace.vectordatabase import VectorDatabase
        
        # Create a simple vector database without embedding model
        vector_db = VectorDatabase(embedding_model=None)
        
        # Test 1: Basic metadata insertion
        print("1. Testing basic metadata insertion...")
        
        # Insert vectors with metadata
        vector_db.insert_with_metadata(
            "Document 1", 
            np.array([1, 2, 3]), 
            source="PDF", 
            page=1, 
            category="technical",
            author="John Doe"
        )
        
        vector_db.insert_with_metadata(
            "Document 2", 
            np.array([4, 5, 6]), 
            source="TXT", 
            page=2, 
            category="research",
            author="Jane Smith"
        )
        
        vector_db.insert_with_metadata(
            "Document 3", 
            np.array([7, 8, 9]), 
            source="PDF", 
            page=3, 
            category="technical",
            author="Bob Wilson"
        )
        
        print("   ✅ Vectors inserted with metadata")
        
        # Test 2: Search with metadata
        print("\n2. Testing search with metadata...")
        results = vector_db.search(np.array([1, 2, 3]), k=2, include_metadata=True)
        print(f"   ✅ Search results with metadata: {len(results)} results")
        for i, (key, score, metadata) in enumerate(results, 1):
            print(f"      Result {i}: {key[:20]}... (score: {score:.3f}) - {metadata}")
        
        # Test 3: Metadata filtering
        print("\n3. Testing metadata filtering...")
        pdf_docs = vector_db.filter_by_metadata(source="PDF")
        research_docs = vector_db.filter_by_metadata(category="research")
        technical_docs = vector_db.filter_by_metadata(category="technical")
        
        print(f"   ✅ PDF documents: {pdf_docs}")
        print(f"   ✅ Research documents: {research_docs}")
        print(f"   ✅ Technical documents: {technical_docs}")
        
        # Test 4: Metadata retrieval and update
        print("\n4. Testing metadata retrieval and update...")
        metadata = vector_db.get_metadata("Document 1")
        print(f"   ✅ Original metadata: {metadata}")
        
        vector_db.update_metadata("Document 1", {"updated": True, "version": "1.1"})
        updated_metadata = vector_db.get_metadata("Document 1")
        print(f"   ✅ Updated metadata: {updated_metadata}")
        
        # Test 5: Insert with metadata dictionary
        print("\n5. Testing insert with metadata dictionary...")
        metadata_dict = {
            "source": "web",
            "category": "news",
            "date": "2024-01-15",
            "relevance": "high"
        }
        vector_db.insert("Document 4", np.array([10, 11, 12]), metadata_dict)
        
        doc4_metadata = vector_db.get_metadata("Document 4")
        print(f"   ✅ Document 4 metadata: {doc4_metadata}")
        
        # Test 6: Complex filtering
        print("\n6. Testing complex filtering...")
        high_relevance = vector_db.filter_by_metadata(relevance="high")
        print(f"   ✅ High relevance documents: {high_relevance}")
        
        print("\n🎉 All basic metadata tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metadata_operations():
    """Test various metadata operations."""
    print("\n🔧 Testing Metadata Operations\n")
    
    try:
        from aimakerspace.vectordatabase import VectorDatabase
        
        vector_db = VectorDatabase(embedding_model=None)
        
        # Create test data
        test_data = [
            ("chunk_1", np.array([1, 0, 0]), {"type": "introduction", "page": 1, "section": "overview"}),
            ("chunk_2", np.array([0, 1, 0]), {"type": "methodology", "page": 2, "section": "methods"}),
            ("chunk_3", np.array([0, 0, 1]), {"type": "results", "page": 3, "section": "findings"}),
            ("chunk_4", np.array([1, 1, 0]), {"type": "discussion", "page": 4, "section": "analysis"}),
            ("chunk_5", np.array([1, 0, 1]), {"type": "conclusion", "page": 5, "section": "summary"}),
        ]
        
        for key, vector, metadata in test_data:
            vector_db.insert(key, vector, metadata)
        
        print("   ✅ Test data inserted")
        
        # Test filtering by type
        intro_chunks = vector_db.filter_by_metadata(type="introduction")
        method_chunks = vector_db.filter_by_metadata(type="methodology")
        print(f"   ✅ Introduction chunks: {intro_chunks}")
        print(f"   ✅ Methodology chunks: {method_chunks}")
        
        # Test filtering by page range (simulated)
        early_pages = vector_db.filter_by_metadata(page=lambda x: x <= 2)
        print(f"   ✅ Early pages (1-2): {early_pages}")
        
        # Test search with metadata
        query_vector = np.array([1, 0, 0])
        results = vector_db.search(query_vector, k=3, include_metadata=True)
        print(f"   ✅ Search results with metadata:")
        for key, score, metadata in results:
            print(f"      {key}: {metadata['type']} (page {metadata['page']}) - score: {score:.3f}")
        
        print("\n🎉 Metadata operations test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Metadata operations test failed: {e}")
        return False

def main():
    """Run all metadata tests."""
    print("=" * 60)
    print("🧪 VectorDatabase Metadata Support Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Metadata Support", test_metadata_basic),
        ("Metadata Operations", test_metadata_operations)
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
        print("\n📋 New Features Added:")
        print("   ✅ insert() with metadata parameter")
        print("   ✅ insert_with_metadata() for keyword arguments")
        print("   ✅ search() with include_metadata option")
        print("   ✅ search_by_text() with include_metadata option")
        print("   ✅ get_metadata() to retrieve metadata")
        print("   ✅ update_metadata() to update existing metadata")
        print("   ✅ filter_by_metadata() to filter by criteria")
        print("   ✅ abuild_from_list() with metadata_list parameter")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
