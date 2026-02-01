"""
Test database integration with claim processing tools
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agent.tools import retrieve_policy, check_claim_history


def test_retrieve_policy():
    """Test policy retrieval from database"""
    print("="*60)
    print("TEST: retrieve_policy() with Database")
    print("="*60)
    
    test_identifiers = [
        "KA-01-AB-1234",  # Motor policy in database
        "DL-01-XY-5678",  # Motor policy in database
        "PROP-AHM-001",   # Home policy in database
        "HE-2024-001",    # Health policy in database
        "UNKNOWN-123"     # Not in database (fallback)
    ]
    
    for identifier in test_identifiers:
        print(f"\n🔍 Retrieving policy: {identifier}")
        result = retrieve_policy(identifier)
        
        if "error" not in result:
            print(f"   ✅ Policy Number: {result.get('policy_number')}")
            print(f"   📋 Type: {result.get('policy_type', 'N/A')}")
            print(f"   💰 Coverage: {result.get('coverage_type')}")
            print(f"   💵 Sum Insured: ₹{result.get('sum_insured', result.get('idv', 0)):,}")
            
            if 'customer_name' in result:
                print(f"   👤 Customer: {result['customer_name']}")
                print(f"   📊 Source: DATABASE")
            else:
                print(f"   📊 Source: MOCK DATA")
            
            if 'rag_context' in result:
                print(f"   🔍 RAG Context: {len(result['rag_context'])} sections")
        else:
            print(f"   ❌ Error: {result['error']}")


def test_check_claim_history():
    """Test claim history retrieval from database"""
    print("\n" + "="*60)
    print("TEST: check_claim_history() with Database")
    print("="*60)
    
    test_customers = [
        "CUST-001",  # In database with claims
        "CUST-002",  # In database with claims
        "CUST-003",  # In database with claims
        "CUST-999"   # Not in database
    ]
    
    for customer_id in test_customers:
        print(f"\n🔍 Checking history: {customer_id}")
        result = check_claim_history(customer_id)
        
        if "error" not in result:
            found = result.get('customer_found')
            print(f"   {'✅' if found else '❌'} Customer Found: {found}")
            
            if found:
                print(f"   👤 Name: {result.get('customer_name', 'N/A')}")
                print(f"   📋 Total Claims: {result['total_claims']}")
                print(f"   🎯 NCB: {result['ncb_percentage']}%")
                print(f"   ⚠️  Risk Level: {result['risk_level']}")
                print(f"   📊 Source: {result.get('source', 'unknown').upper()}")
                
                if result['past_claims']:
                    print(f"   📜 Past Claims:")
                    for claim in result['past_claims'][:3]:  # Show first 3
                        print(f"      - {claim.get('claim_id')}: {claim.get('claim_type')} ({claim.get('status')})")
        else:
            print(f"   ❌ Error: {result['error']}")


def test_database_stats():
    """Show database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    try:
        from database.models import get_db_manager, Customer, Policy, Claim
        
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            customers = session.query(Customer).all()
            policies = session.query(Policy).all()
            claims = session.query(Claim).all()
            
            print(f"\n📊 Records:")
            print(f"   Customers: {len(customers)}")
            print(f"   Policies: {len(policies)}")
            print(f"   Claims: {len(claims)}")
            
            print(f"\n👥 Customers:")
            for customer in customers:
                print(f"   {customer.customer_id}: {customer.name}")
                print(f"      Policies: {len(customer.policies)}")
                print(f"      Claims: {len(customer.claims)}")
            
            print(f"\n📋 Policies:")
            for policy in policies:
                identifier = policy.vehicle_registration or policy.property_id or policy.policy_number
                print(f"   {policy.policy_number}: {policy.policy_type.value.upper()}")
                print(f"      Identifier: {identifier}")
                print(f"      Coverage: {policy.coverage_type}")
                print(f"      Sum Insured: ₹{policy.sum_insured:,}")
            
            print(f"\n📝 Claims:")
            for claim in claims:
                print(f"   {claim.claim_id}: {claim.claim_type.value}")
                print(f"      Customer: {claim.customer.name}")
                print(f"      Status: {claim.status.value}")
                print(f"      Amount: ₹{claim.estimated_cost or 0:,}")
                
        finally:
            session.close()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "🧪 TESTING DATABASE INTEGRATION WITH TOOLS" + "\n")
    
    # Show database contents
    test_database_stats()
    
    # Test policy retrieval
    test_retrieve_policy()
    
    # Test claim history
    test_check_claim_history()
    
    print("\n" + "="*60)
    print("✅ DATABASE INTEGRATION TESTS COMPLETE")
    print("="*60)
