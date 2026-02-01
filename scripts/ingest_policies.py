"""
Script to ingest insurance policy documents into ChromaDB vector database.
Run this once to populate the RAG system with policy documents.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agent.rag import VectorStore


def ingest_policies():
    """
    Read all policy documents from data/policies/ and add them to ChromaDB.
    """
    # Initialize vector store
    print("Initializing vector store...")
    vector_store = VectorStore()
    
    # Reset existing data (optional - comment out to append)
    print("Resetting existing data...")
    vector_store.reset()
    
    # Path to policy documents
    policies_dir = Path(__file__).parent.parent / "data" / "policies"
    
    if not policies_dir.exists():
        print(f"❌ Error: Policies directory not found at {policies_dir}")
        return
    
    # Get all .txt files
    policy_files = list(policies_dir.glob("*.txt"))
    
    if not policy_files:
        print(f"❌ Error: No .txt files found in {policies_dir}")
        return
    
    print(f"\nFound {len(policy_files)} policy documents to ingest...")
    
    # Process each policy file
    total_chunks = 0
    for policy_file in policy_files:
        print(f"\n📄 Processing: {policy_file.name}")
        
        # Read file content
        try:
            with open(policy_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            continue
        
        # Determine policy type from filename
        filename = policy_file.stem.lower()
        if 'motor' in filename:
            policy_type = 'motor'
        elif 'home' in filename:
            policy_type = 'home'
        elif 'health' in filename:
            policy_type = 'health'
        else:
            policy_type = 'general'
        
        # Extract policy name for better identification
        policy_name = policy_file.stem.replace('_', ' ').title()
        
        # Add document to vector store
        try:
            num_chunks = vector_store.add_document(
                document_text=content,
                document_id=policy_file.stem,
                metadata={
                    'policy_type': policy_type,
                    'policy_name': policy_name,
                    'filename': policy_file.name,
                    'file_size': len(content)
                }
            )
            total_chunks += num_chunks
            print(f"   ✅ Created {num_chunks} chunks")
        except Exception as e:
            print(f"   ❌ Error processing document: {e}")
            continue
    
    # Summary
    print("\n" + "="*60)
    print(f"✅ Ingestion Complete!")
    print(f"   Documents processed: {len(policy_files)}")
    print(f"   Total chunks created: {total_chunks}")
    print(f"   Average chunks per document: {total_chunks // len(policy_files)}")
    print(f"   Database location: {vector_store.persist_directory}")
    print("="*60)
    
    # Test search
    print("\n🔍 Testing semantic search...")
    test_queries = [
        "What is covered under zero depreciation?",
        "What are the exclusions for health insurance?",
        "How to file a flood damage claim?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vector_store.search(query, n_results=2)
        if results:
            top_result = results[0]
            print(f"   → Best match: {top_result['metadata']['policy_name']}")
            print(f"   → Relevance: {(1 - top_result['distance']):.2%}")
            print(f"   → Preview: {top_result['text'][:150]}...")
        else:
            print("   → No results found")
    
    print("\n✅ RAG system ready to use!")


if __name__ == "__main__":
    ingest_policies()
