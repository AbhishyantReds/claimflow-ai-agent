"""
Database initialization and seeding script
Creates tables and populates with sample data
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import (
    get_db_manager, Customer, Policy, Claim, ClaimHistory,
    PolicyType, ClaimType, ClaimStatus
)
from database.crud import (
    create_customer, create_policy, create_claim, create_claim_history
)


def initialize_database(reset: bool = False):
    """Initialize database and create tables"""
    print("="*60)
    print("DATABASE INITIALIZATION")
    print("="*60)
    
    # Get database manager
    db_manager = get_db_manager()
    
    if reset:
        print("\n⚠️  Resetting database (dropping all tables)...")
        db_manager.reset_database()
        print("✅ Database reset complete")
    else:
        print("\n📊 Creating database tables...")
        db_manager.create_tables()
        print("✅ Tables created successfully")
    
    return db_manager


def seed_sample_data():
    """Populate database with sample data"""
    print("\n" + "="*60)
    print("SEEDING SAMPLE DATA")
    print("="*60)
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        # Sample customers
        print("\n📝 Creating customers...")
        customers = []
        
        customer1 = create_customer(
            session,
            customer_id="CUST-001",
            name="Rajesh Kumar",
            email="rajesh.kumar@email.com",
            phone="+91-9876543210",
            address="123, MG Road, Bangalore, Karnataka - 560001"
        )
        customers.append(customer1)
        print(f"   ✅ Created: {customer1.name} ({customer1.customer_id})")
        
        customer2 = create_customer(
            session,
            customer_id="CUST-002",
            name="Priya Sharma",
            email="priya.sharma@email.com",
            phone="+91-9876543211",
            address="456, Nehru Place, New Delhi - 110019"
        )
        customers.append(customer2)
        print(f"   ✅ Created: {customer2.name} ({customer2.customer_id})")
        
        customer3 = create_customer(
            session,
            customer_id="CUST-003",
            name="Amit Patel",
            email="amit.patel@email.com",
            phone="+91-9876543212",
            address="789, SG Highway, Ahmedabad, Gujarat - 380015"
        )
        customers.append(customer3)
        print(f"   ✅ Created: {customer3.name} ({customer3.customer_id})")
        
        # Sample motor policies
        print("\n🚗 Creating motor policies...")
        motor_policy1 = create_policy(
            session,
            policy_number="MI-2024-001",
            customer_id=customer1.id,
            policy_type=PolicyType.MOTOR,
            coverage_type="comprehensive",
            sum_insured=1500000,
            premium=45000,
            vehicle_registration="KA-01-AB-1234",
            idv=1500000,
            deductible=2000,
            zero_depreciation=True,
            ncb_percentage=20,
            policy_start=datetime(2024, 1, 1),
            policy_end=datetime(2025, 1, 1),
            status="active"
        )
        print(f"   ✅ Created: {motor_policy1.policy_number} (Motor - {motor_policy1.vehicle_registration})")
        
        motor_policy2 = create_policy(
            session,
            policy_number="MI-2024-002",
            customer_id=customer2.id,
            policy_type=PolicyType.MOTOR,
            coverage_type="comprehensive",
            sum_insured=800000,
            premium=28000,
            vehicle_registration="DL-01-XY-5678",
            idv=800000,
            deductible=2000,
            zero_depreciation=False,
            ncb_percentage=0,
            policy_start=datetime(2024, 3, 15),
            policy_end=datetime(2025, 3, 15),
            status="active"
        )
        print(f"   ✅ Created: {motor_policy2.policy_number} (Motor - {motor_policy2.vehicle_registration})")
        
        # Sample home policies
        print("\n🏠 Creating home policies...")
        home_policy1 = create_policy(
            session,
            policy_number="HI-2024-001",
            customer_id=customer3.id,
            policy_type=PolicyType.HOME,
            coverage_type="comprehensive",
            sum_insured=5000000,
            premium=15000,
            property_id="PROP-AHM-001",
            deductible=5000,
            policy_start=datetime(2024, 2, 1),
            policy_end=datetime(2025, 2, 1),
            status="active"
        )
        print(f"   ✅ Created: {home_policy1.policy_number} (Home - {home_policy1.property_id})")
        
        # Sample health policies
        print("\n🏥 Creating health policies...")
        health_policy1 = create_policy(
            session,
            policy_number="HE-2024-001",
            customer_id=customer1.id,
            policy_type=PolicyType.HEALTH,
            coverage_type="individual",
            sum_insured=500000,
            premium=12000,
            policy_holder_age=35,
            copay_percentage=10,
            policy_start=datetime(2024, 1, 1),
            policy_end=datetime(2025, 1, 1),
            status="active"
        )
        print(f"   ✅ Created: {health_policy1.policy_number} (Health - Individual)")
        
        health_policy2 = create_policy(
            session,
            policy_number="HE-2024-002",
            customer_id=customer2.id,
            policy_type=PolicyType.HEALTH,
            coverage_type="family_floater",
            sum_insured=1000000,
            premium=25000,
            policy_holder_age=32,
            copay_percentage=10,
            policy_start=datetime(2024, 4, 1),
            policy_end=datetime(2025, 4, 1),
            status="active"
        )
        print(f"   ✅ Created: {health_policy2.policy_number} (Health - Family Floater)")
        
        # Sample claims
        print("\n📋 Creating sample claims...")
        
        # Motor accident claim
        claim1 = create_claim(
            session,
            claim_id="CLM-2024-001",
            customer_id=customer1.id,
            policy_id=motor_policy1.id,
            claim_type=ClaimType.MOTOR_ACCIDENT,
            status=ClaimStatus.APPROVED,
            incident_date=datetime(2024, 6, 15, 14, 30),
            incident_location="Outer Ring Road, Bangalore",
            incident_description="Collision with another vehicle at traffic signal",
            damage_description="Front bumper damaged, headlight broken, fender dented",
            vehicle_registration="KA-01-AB-1234",
            repair_garage="SafeDrive Service Center",
            estimated_cost=85000,
            approved_amount=85000,
            payout_amount=85000,
            depreciation_applied=0,
            documents_verified=True,
            coverage_verified=True,
            fraud_check_passed=True,
            decision="approved",
            decision_reason="Valid claim, zero depreciation cover applicable",
            filed_date=datetime(2024, 6, 15, 16, 0),
            decision_date=datetime(2024, 6, 16, 10, 0)
        )
        print(f"   ✅ Created: {claim1.claim_id} (Motor Accident - Approved)")
        
        # Home fire claim
        claim2 = create_claim(
            session,
            claim_id="CLM-2024-002",
            customer_id=customer3.id,
            policy_id=home_policy1.id,
            claim_type=ClaimType.HOME_FIRE,
            status=ClaimStatus.UNDER_REVIEW,
            incident_date=datetime(2024, 11, 20, 2, 0),
            incident_location="PROP-AHM-001, Ahmedabad",
            incident_description="Electrical short circuit caused fire in living room",
            damage_description="Furniture, electronics, and wall damage",
            property_id="PROP-AHM-001",
            affected_items="Sofa set, TV, AC unit, wall paint",
            estimated_cost=250000,
            documents_verified=True,
            coverage_verified=True,
            fraud_check_passed=True,
            decision="under_review",
            filed_date=datetime(2024, 11, 20, 10, 0)
        )
        print(f"   ✅ Created: {claim2.claim_id} (Home Fire - Under Review)")
        
        # Health hospitalization claim
        claim3 = create_claim(
            session,
            claim_id="CLM-2024-003",
            customer_id=customer2.id,
            policy_id=health_policy2.id,
            claim_type=ClaimType.HEALTH_HOSPITALIZATION,
            status=ClaimStatus.PENDING,
            incident_date=datetime(2024, 12, 1),
            incident_location="Apollo Hospital, Delhi",
            incident_description="Hospitalized for severe pneumonia",
            hospital_name="Apollo Hospital",
            treatment_type="hospitalization",
            hospitalization_date=datetime(2024, 12, 1),
            discharge_date=datetime(2024, 12, 5),
            treatment_cost=120000,
            estimated_cost=120000,
            documents_verified=False,
            filed_date=datetime(2024, 12, 6)
        )
        print(f"   ✅ Created: {claim3.claim_id} (Health Hospitalization - Pending)")
        
        # Sample claim history
        print("\n📚 Creating claim history records...")
        
        history1 = create_claim_history(
            session,
            customer_id="CUST-001",
            claim_id="CLM-2023-099",
            claim_type="motor_accident",
            claim_amount=45000,
            filed_date=datetime(2023, 8, 10),
            status="approved"
        )
        print(f"   ✅ Created history: {history1.claim_id} for {history1.customer_id}")
        
        history2 = create_claim_history(
            session,
            customer_id="CUST-003",
            claim_id="CLM-2023-150",
            claim_type="home_theft",
            claim_amount=80000,
            filed_date=datetime(2023, 5, 15),
            status="approved"
        )
        print(f"   ✅ Created history: {history2.claim_id} for {history2.customer_id}")
        
        print("\n" + "="*60)
        print("✅ SAMPLE DATA SEEDED SUCCESSFULLY")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   Customers: 3")
        print(f"   Policies: 5 (2 Motor, 1 Home, 2 Health)")
        print(f"   Active Claims: 3")
        print(f"   Historical Claims: 2")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def show_database_stats():
    """Display database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        customer_count = session.query(Customer).count()
        policy_count = session.query(Policy).count()
        claim_count = session.query(Claim).count()
        history_count = session.query(ClaimHistory).count()
        
        print(f"\n📊 Records:")
        print(f"   Customers: {customer_count}")
        print(f"   Policies: {policy_count}")
        print(f"   Claims: {claim_count}")
        print(f"   Claim History: {history_count}")
        
        # Breakdown by type
        motor_policies = session.query(Policy).filter(Policy.policy_type == PolicyType.MOTOR).count()
        home_policies = session.query(Policy).filter(Policy.policy_type == PolicyType.HOME).count()
        health_policies = session.query(Policy).filter(Policy.policy_type == PolicyType.HEALTH).count()
        
        print(f"\n📋 Policies by Type:")
        print(f"   Motor: {motor_policies}")
        print(f"   Home: {home_policies}")
        print(f"   Health: {health_policies}")
        
        # Claims by status
        pending_claims = session.query(Claim).filter(Claim.status == ClaimStatus.PENDING).count()
        approved_claims = session.query(Claim).filter(Claim.status == ClaimStatus.APPROVED).count()
        rejected_claims = session.query(Claim).filter(Claim.status == ClaimStatus.REJECTED).count()
        review_claims = session.query(Claim).filter(Claim.status == ClaimStatus.UNDER_REVIEW).count()
        
        print(f"\n📋 Claims by Status:")
        print(f"   Pending: {pending_claims}")
        print(f"   Under Review: {review_claims}")
        print(f"   Approved: {approved_claims}")
        print(f"   Rejected: {rejected_claims}")
        
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    reset = "--reset" in sys.argv
    seed = "--seed" in sys.argv or "--reset" in sys.argv
    
    # Initialize database
    initialize_database(reset=reset)
    
    # Seed sample data if requested
    if seed:
        seed_sample_data()
    
    # Show statistics
    show_database_stats()
    
    print("\n✅ Database initialization complete!")
    print(f"\n💾 Database location: data/claimflow.db")
