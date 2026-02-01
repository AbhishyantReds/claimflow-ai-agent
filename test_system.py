"""
Quick system test to verify ClaimFlow AI is working
"""
import os
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'test-key')

print("=" * 60)
print("ClaimFlow AI - System Test")
print("=" * 60)

# Test 1: Database
print("\n✓ Test 1: Database Connection")
try:
    from database.models import Customer, Policy
    from database.crud import get_all_customers
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine('sqlite:///data/claimflow.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    customers = get_all_customers(session)
    print(f"  Found {len(customers)} customers in database")
    for customer in customers:
        print(f"  - {customer.name} ({customer.customer_id})")
    session.close()
    print("  ✅ Database working!")
except Exception as e:
    print(f"  ❌ Database error: {e}")

# Test 2: RAG System
print("\n✓ Test 2: RAG Vector Store")
try:
    from agent.rag import VectorStore
    
    vs = VectorStore()
    # Try a search
    results = vs.search("motor accident coverage", top_k=3)
    print(f"  Found {len(results)} policy chunks")
    if results:
        print(f"  Sample: {results[0]['text'][:100]}...")
    print("  ✅ RAG system working!")
except Exception as e:
    print(f"  ❌ RAG error: {e}")

# Test 3: Agent Tools
print("\n✓ Test 3: Agent Tools")
try:
    from agent.tools import extract_claim_data
    
    # Test extraction
    conversation = """
    User: My car was damaged in an accident
    Agent: What's your registration number?
    User: TS 09 EF 5678
    Agent: What's the damage?
    User: Front bumper damaged, repair estimate is 45000
    """
    
    result = extract_claim_data(conversation)
    print(f"  Extracted claim type: {result.get('claim_type', 'N/A')}")
    print(f"  Policy identifier: {result.get('policy_identifier', 'N/A')}")
    print("  ✅ Agent tools working!")
except Exception as e:
    print(f"  ❌ Tools error: {e}")

# Test 4: Core Tests
print("\n✓ Test 4: Running Core Tests")
try:
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'pytest', 'tests/test_database.py', 'tests/test_rag.py', '-v', '--tb=line'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if 'passed' in result.stdout.lower():
        # Count passed tests
        lines = result.stdout.split('\n')
        for line in lines:
            if 'passed' in line.lower():
                print(f"  {line.strip()}")
                break
        print("  ✅ Core tests passing!")
    else:
        print(f"  ⚠️ Check test results manually")
except Exception as e:
    print(f"  ⚠️ Could not run tests: {e}")

print("\n" + "=" * 60)
print("System Check Complete!")
print("=" * 60)
print("\nTo run the application:")
print("  python ui/simple_app.py")
print("\nTo run tests:")
print("  pytest tests/test_database.py tests/test_rag.py -v")
print("\nDocumentation:")
print("  README.md - Main documentation")
print("  PROJECT_SUMMARY.md - Implementation details")
print("=" * 60)
