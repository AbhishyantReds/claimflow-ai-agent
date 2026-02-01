"""
Test script to verify RAG integration with the claim processing workflow.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agent.rag import VectorStore, retrieve_policy_info


def test_rag_search():
    """Test basic RAG search functionality"""
    print("="*60)
    print("RAG SYSTEM TEST")
    print("="*60)
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Check database status
    chunk_count = vector_store.get_document_count()
    print(f"\n📊 Database Status:")
    print(f"   Total chunks: {chunk_count}")
    
    if chunk_count == 0:
        print("\n❌ Database is empty! Run scripts/ingest_policies.py first.")
        return
    
    # Test queries
    test_queries = [
        ("What is zero depreciation coverage?", "motor"),
        ("What are the exclusions in health insurance?", "health"),
        ("How to claim for flood damage?", "home"),
        ("What is covered in critical illness insurance?", "health"),
        ("What documents are required for motor accident claim?", "motor")
    ]
    
    print("\n" + "="*60)
    print("TESTING SEMANTIC SEARCH")
    print("="*60)
    
    for query, policy_type in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print(f"   Filter: {policy_type}")
        
        results = vector_store.search(
            query=query,
            n_results=2,
            filter_metadata={"policy_type": policy_type}
        )
        
        if results:
            for i, result in enumerate(results, 1):
                relevance = (1 - result['distance']) * 100
                policy_name = result['metadata']['policy_name']
                preview = result['text'][:200].replace('\n', ' ')
                
                print(f"\n   Result {i}:")
                print(f"   → Policy: {policy_name}")
                print(f"   → Relevance: {relevance:.1f}%")
                print(f"   → Preview: {preview}...")
        else:
            print("   → No results found")
    
    # Test the helper function
    print("\n" + "="*60)
    print("TESTING retrieve_policy_info() FUNCTION")
    print("="*60)
    
    result = retrieve_policy_info("What is IDV in motor insurance?", policy_type="motor", n_results=1)
    print(result)
    
    print("\n✅ RAG system test complete!")


def test_tools_integration():
    """Test RAG integration with tools.py"""
    print("\n" + "="*60)
    print("TESTING TOOLS.PY INTEGRATION")
    print("="*60)
    
    try:
        from agent.tools import retrieve_policy
        
        print("\nTesting retrieve_policy() with RAG...")
        result = retrieve_policy("DL-01-AB-1234")
        
        print(f"\n✅ Policy retrieved successfully!")
        print(f"   Policy Number: {result.get('policy_number')}")
        print(f"   Coverage Type: {result.get('coverage_type')}")
        
        if 'rag_context' in result:
            print(f"\n   RAG Context Retrieved:")
            for i, ctx in enumerate(result['rag_context'], 1):
                print(f"      {i}. {ctx['source']} (Relevance: {ctx['relevance']*100:.1f}%)")
        else:
            print("\n   ⚠️ No RAG context in result (using mock data only)")
            
    except Exception as e:
        print(f"\n❌ Error testing tools integration: {e}")


if __name__ == "__main__":
    test_rag_search()
    test_tools_integration()
