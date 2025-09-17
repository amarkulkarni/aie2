#!/usr/bin/env python3
"""
Example script showing how to use metadata support in the RAG application.
Demonstrates practical usage of metadata with PDF documents and RAG pipeline.
"""

import sys
import os
import asyncio
sys.path.append('.')

def example_metadata_with_pdf():
    """Example of using metadata with PDF documents in RAG pipeline."""
    print("📄 Example: Metadata with PDF Documents\n")
    
    try:
        from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
        from aimakerspace.vectordatabase import VectorDatabase
        from aimakerspace.openai_utils.embedding import EmbeddingModel
        
        # Check if API key is available
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  No OpenAI API key found. This example requires an API key.")
            print("   Set OPENAI_API_KEY environment variable to run this example.")
            return False
        
        # Load PDF document
        print("1. Loading PDF document...")
        pdf_loader = PDFLoader("data/ai_research_paper.pdf", method="pdfplumber")
        pdf_docs = pdf_loader.load_documents()
        print(f"   ✅ Loaded {len(pdf_docs)} PDF documents")
        
        # Split into chunks
        print("\n2. Splitting document into chunks...")
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_texts(pdf_docs)
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # Create metadata for each chunk
        print("\n3. Creating metadata for chunks...")
        metadata_list = []
        for i, chunk in enumerate(chunks):
            # Extract some basic metadata from chunk content
            is_technical = any(term in chunk.lower() for term in ['algorithm', 'model', 'neural', 'network', 'learning'])
            is_intro = any(term in chunk.lower() for term in ['introduction', 'overview', 'abstract'])
            is_conclusion = any(term in chunk.lower() for term in ['conclusion', 'summary', 'final'])
            
            metadata = {
                "chunk_id": i,
                "source_file": "ai_research_paper.pdf",
                "chunk_size": len(chunk),
                "is_technical": is_technical,
                "section_type": "introduction" if is_intro else "conclusion" if is_conclusion else "body",
                "page_estimate": (i // 3) + 1,
                "domain": "artificial_intelligence",
                "keywords": [word for word in chunk.lower().split() if len(word) > 5][:5]  # First 5 long words
            }
            metadata_list.append(metadata)
        
        print(f"   ✅ Created metadata for {len(metadata_list)} chunks")
        
        # Build vector database with metadata
        print("\n4. Building vector database with metadata...")
        vector_db = VectorDatabase()
        vector_db = asyncio.run(vector_db.abuild_from_list(chunks, metadata_list))
        print(f"   ✅ Vector database created with {len(vector_db.vectors)} vectors")
        
        # Demonstrate metadata filtering
        print("\n5. Demonstrating metadata filtering...")
        technical_chunks = vector_db.filter_by_metadata(is_technical=True)
        intro_chunks = vector_db.filter_by_metadata(section_type="introduction")
        large_chunks = [key for key in vector_db.vectors.keys() 
                       if vector_db.get_metadata(key).get('chunk_size', 0) > 400]
        
        print(f"   ✅ Technical chunks: {len(technical_chunks)}")
        print(f"   ✅ Introduction chunks: {len(intro_chunks)}")
        print(f"   ✅ Large chunks (>400 chars): {len(large_chunks)}")
        
        # Demonstrate search with metadata
        print("\n6. Demonstrating search with metadata...")
        query = "What is artificial intelligence?"
        results = vector_db.search_by_text(query, k=3, include_metadata=True)
        
        print(f"   Query: '{query}'")
        print(f"   Results with metadata:")
        for i, (text, score, metadata) in enumerate(results, 1):
            print(f"      Result {i}:")
            print(f"         Score: {score:.3f}")
            print(f"         Chunk ID: {metadata.get('chunk_id', 'N/A')}")
            print(f"         Section: {metadata.get('section_type', 'N/A')}")
            print(f"         Technical: {metadata.get('is_technical', 'N/A')}")
            print(f"         Size: {metadata.get('chunk_size', 'N/A')} chars")
            print(f"         Keywords: {metadata.get('keywords', [])[:3]}")
            print(f"         Text preview: {text[:100]}...")
            print()
        
        # Demonstrate metadata-based filtering before search
        print("\n7. Demonstrating filtered search...")
        # Only search in technical chunks
        technical_vector_db = VectorDatabase()
        for chunk_id in technical_chunks:
            chunk_text = chunks[int(chunk_id.split('_')[-1])]  # Extract chunk index
            metadata = vector_db.get_metadata(chunk_id)
            technical_vector_db.insert(chunk_id, vector_db.retrieve_from_key(chunk_id), metadata)
        
        # Add embedding model for search
        technical_vector_db.embedding_model = vector_db.embedding_model
        
        filtered_results = technical_vector_db.search_by_text(query, k=2, include_metadata=True)
        print(f"   Filtered search (technical chunks only):")
        for i, (text, score, metadata) in enumerate(filtered_results, 1):
            print(f"      Result {i}: {metadata.get('section_type', 'N/A')} - Score: {score:.3f}")
        
        print("\n🎉 Metadata with PDF example completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def example_metadata_operations():
    """Example of various metadata operations."""
    print("\n🔧 Example: Metadata Operations\n")
    
    try:
        from aimakerspace.vectordatabase import VectorDatabase
        import numpy as np
        
        # Create vector database without embedding model for this example
        vector_db = VectorDatabase()
        
        # Simulate document chunks with metadata
        documents = [
            ("doc1_chunk1", "Introduction to machine learning concepts", 
             {"type": "introduction", "topic": "ml", "difficulty": "beginner", "page": 1}),
            ("doc1_chunk2", "Deep learning algorithms and neural networks", 
             {"type": "technical", "topic": "dl", "difficulty": "advanced", "page": 2}),
            ("doc2_chunk1", "Data preprocessing techniques", 
             {"type": "technical", "topic": "data", "difficulty": "intermediate", "page": 1}),
            ("doc2_chunk2", "Conclusion and future work", 
             {"type": "conclusion", "topic": "general", "difficulty": "beginner", "page": 3}),
        ]
        
        # Insert documents with metadata
        for i, (key, text, metadata) in enumerate(documents):
            # Create a simple vector (in real usage, this would be an embedding)
            vector = np.random.rand(10)  # 10-dimensional random vector
            vector_db.insert(key, vector, metadata)
        
        print("1. Basic metadata operations:")
        print(f"   Total documents: {len(vector_db.vectors)}")
        
        # Filter by topic
        ml_docs = vector_db.filter_by_metadata(topic="ml")
        technical_docs = vector_db.filter_by_metadata(type="technical")
        beginner_docs = vector_db.filter_by_metadata(difficulty="beginner")
        
        print(f"   ML documents: {ml_docs}")
        print(f"   Technical documents: {technical_docs}")
        print(f"   Beginner documents: {beginner_docs}")
        
        # Update metadata
        print("\n2. Metadata updates:")
        original_metadata = vector_db.get_metadata("doc1_chunk1")
        print(f"   Original metadata: {original_metadata}")
        
        vector_db.update_metadata("doc1_chunk1", {"updated": True, "reviewed_by": "AI Assistant"})
        updated_metadata = vector_db.get_metadata("doc1_chunk1")
        print(f"   Updated metadata: {updated_metadata}")
        
        # Search with metadata
        print("\n3. Search with metadata:")
        query_vector = np.random.rand(10)
        results = vector_db.search(query_vector, k=3, include_metadata=True)
        
        for i, (key, score, metadata) in enumerate(results, 1):
            print(f"   Result {i}: {key} (score: {score:.3f})")
            print(f"      Type: {metadata.get('type', 'N/A')}")
            print(f"      Topic: {metadata.get('topic', 'N/A')}")
            print(f"      Difficulty: {metadata.get('difficulty', 'N/A')}")
        
        print("\n🎉 Metadata operations example completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False

def main():
    """Run metadata examples."""
    print("=" * 70)
    print("📚 VectorDatabase Metadata Support - Usage Examples")
    print("=" * 70)
    
    examples = [
        ("Metadata Operations", example_metadata_operations),
        ("Metadata with PDF", example_metadata_with_pdf),
    ]
    
    passed = 0
    total = len(examples)
    
    for example_name, example_func in examples:
        print(f"\n--- {example_name} ---")
        if example_func():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Results: {passed}/{total} examples completed")
    
    if passed == total:
        print("🎉 All examples completed successfully!")
        print("\n📋 Key Features Demonstrated:")
        print("   ✅ Storing metadata with vectors")
        print("   ✅ Filtering by metadata criteria")
        print("   ✅ Searching with metadata inclusion")
        print("   ✅ Updating existing metadata")
        print("   ✅ Using metadata for document organization")
        print("   ✅ Filtered search based on metadata")
    else:
        print("⚠️  Some examples failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
