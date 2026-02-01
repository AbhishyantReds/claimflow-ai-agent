"""
Tests for database models, CRUD operations, and persistence
"""
import pytest
from datetime import datetime, timedelta
from database.models import (
    Customer, Policy, Claim, ClaimHistory,
    PolicyType, ClaimType, ClaimStatus,
    DatabaseManager
)
from database.crud import (
    create_customer, get_customer, update_customer,
    create_policy, get_policy, get_policy_by_identifier,
    create_claim, get_claim, update_claim_status,
    get_customer_claim_history
)


class TestDatabaseManager:
    """Test DatabaseManager class"""
    
    def test_initialization(self):
        """Test database manager initialization"""
        db_manager = DatabaseManager("sqlite:///:memory:")
        assert db_manager is not None
        assert db_manager.engine is not None
    
    def test_create_tables(self):
        """Test table creation"""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.create_tables()
        
        # Check that tables exist
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        
        assert 'customers' in tables
        assert 'policies' in tables
        assert 'claims' in tables
        assert 'claim_history' in tables
    
    def test_session_creation(self):
        """Test session creation"""
        db_manager = DatabaseManager("sqlite:///:memory:")
        session = db_manager.get_session()
        
        assert session is not None
        session.close()


class TestCustomerCRUD:
    """Test Customer CRUD operations"""
    
    def test_create_customer(self, db_session):
        """Test creating a customer"""
        customer = create_customer(
            db_session,
            customer_id="CUST-TEST-001",
            name="Test User",
            email="test@example.com",
            phone="+91-9999999999"
        )
        
        assert customer.id is not None
        assert customer.customer_id == "CUST-TEST-001"
        assert customer.name == "Test User"
        assert customer.email == "test@example.com"
    
    def test_get_customer(self, db_session, sample_customer):
        """Test retrieving a customer"""
        customer = get_customer(db_session, sample_customer.customer_id)
        
        assert customer is not None
        assert customer.id == sample_customer.id
        assert customer.name == sample_customer.name
    
    def test_update_customer(self, db_session, sample_customer):
        """Test updating customer details"""
        updated = update_customer(
            db_session,
            sample_customer.customer_id,
            email="newemail@example.com",
            phone="+91-8888888888"
        )
        
        assert updated is not None
        assert updated.email == "newemail@example.com"
        assert updated.phone == "+91-8888888888"
    
    def test_customer_not_found(self, db_session):
        """Test getting non-existent customer"""
        customer = get_customer(db_session, "NONEXISTENT")
        assert customer is None


class TestPolicyCRUD:
    """Test Policy CRUD operations"""
    
    def test_create_policy(self, db_session, sample_customer):
        """Test creating a policy"""
        policy = create_policy(
            db_session,
            policy_number="POL-TEST-001",
            customer_id=sample_customer.id,
            policy_type=PolicyType.MOTOR,
            sum_insured=1000000,
            policy_start=datetime.now(),
            policy_end=datetime.now() + timedelta(days=365),
            vehicle_registration="KA-01-TEST-1234",
            idv=1000000
        )
        
        assert policy.id is not None
        assert policy.policy_number == "POL-TEST-001"
        assert policy.policy_type == PolicyType.MOTOR
        assert policy.vehicle_registration == "KA-01-TEST-1234"
    
    def test_get_policy(self, db_session, sample_motor_policy):
        """Test retrieving a policy"""
        policy = get_policy(db_session, sample_motor_policy.policy_number)
        
        assert policy is not None
        assert policy.id == sample_motor_policy.id
    
    def test_get_policy_by_identifier(self, db_session, sample_motor_policy):
        """Test retrieving policy by vehicle registration"""
        policy = get_policy_by_identifier(
            db_session,
            sample_motor_policy.vehicle_registration
        )
        
        assert policy is not None
        assert policy.id == sample_motor_policy.id
    
    def test_policy_types(self, db_session, sample_customer):
        """Test different policy types"""
        # Motor policy
        motor_policy = create_policy(
            db_session,
            policy_number="MOTOR-001",
            customer_id=sample_customer.id,
            policy_type=PolicyType.MOTOR,
            sum_insured=1000000,
            policy_start=datetime.now(),
            policy_end=datetime.now() + timedelta(days=365),
            vehicle_registration="KA-01-AB-1234"
        )
        
        # Home policy
        home_policy = create_policy(
            db_session,
            policy_number="HOME-001",
            customer_id=sample_customer.id,
            policy_type=PolicyType.HOME,
            sum_insured=5000000,
            policy_start=datetime.now(),
            policy_end=datetime.now() + timedelta(days=365),
            property_id="PROP-001"
        )
        
        # Health policy
        health_policy = create_policy(
            db_session,
            policy_number="HEALTH-001",
            customer_id=sample_customer.id,
            policy_type=PolicyType.HEALTH,
            sum_insured=500000,
            policy_start=datetime.now(),
            policy_end=datetime.now() + timedelta(days=365),
            policy_holder_age=35,
            copay_percentage=10
        )
        
        assert motor_policy.vehicle_registration is not None
        assert home_policy.property_id is not None
        assert health_policy.copay_percentage == 10


class TestClaimCRUD:
    """Test Claim CRUD operations"""
    
    def test_create_claim(self, db_session, sample_customer, sample_motor_policy):
        """Test creating a claim"""
        claim = create_claim(
            db_session,
            claim_id="CLM-TEST-001",
            customer_id=sample_customer.id,
            policy_id=sample_motor_policy.id,
            claim_type=ClaimType.MOTOR_ACCIDENT,
            incident_date=datetime.now(),
            incident_location="Test Location",
            vehicle_registration=sample_motor_policy.vehicle_registration,
            estimated_cost=75000
        )
        
        assert claim.id is not None
        assert claim.claim_id == "CLM-TEST-001"
        assert claim.claim_type == ClaimType.MOTOR_ACCIDENT
        assert claim.status == ClaimStatus.PENDING
    
    def test_get_claim(self, db_session, sample_claim):
        """Test retrieving a claim"""
        claim = get_claim(db_session, sample_claim.claim_id)
        
        assert claim is not None
        assert claim.id == sample_claim.id
    
    def test_update_claim_status(self, db_session, sample_claim):
        """Test updating claim status"""
        updated = update_claim_status(
            db_session,
            sample_claim.claim_id,
            ClaimStatus.APPROVED
        )
        
        assert updated is not None
        assert updated.status == ClaimStatus.APPROVED
        assert updated.decision_date is not None
    
    def test_claim_relationships(self, db_session, sample_claim):
        """Test claim relationships with customer and policy"""
        claim = get_claim(db_session, sample_claim.claim_id)
        
        assert claim.customer is not None
        assert claim.policy is not None
        assert claim.customer.name == "Test Customer"
    
    def test_claim_types(self, db_session, sample_customer, sample_motor_policy):
        """Test different claim types"""
        claim_types = [
            ClaimType.MOTOR_ACCIDENT,
            ClaimType.MOTOR_THEFT,
            ClaimType.HOME_FIRE,
            ClaimType.HEALTH_HOSPITALIZATION
        ]
        
        for idx, claim_type in enumerate(claim_types):
            claim = create_claim(
                db_session,
                claim_id=f"CLM-TYPE-{idx}",
                customer_id=sample_customer.id,
                policy_id=sample_motor_policy.id,
                claim_type=claim_type,
                incident_date=datetime.now()
            )
            
            assert claim.claim_type == claim_type


class TestRelationships:
    """Test model relationships"""
    
    def test_customer_policies_relationship(self, db_session, sample_customer):
        """Test customer -> policies relationship"""
        # Create multiple policies
        for i in range(3):
            create_policy(
                db_session,
                policy_number=f"POL-{i}",
                customer_id=sample_customer.id,
                policy_type=PolicyType.MOTOR,
                sum_insured=1000000,
                policy_start=datetime.now(),
                policy_end=datetime.now() + timedelta(days=365)
            )
        
        customer = get_customer(db_session, sample_customer.customer_id)
        assert len(customer.policies) == 3
    
    def test_customer_claims_relationship(self, db_session, sample_customer, sample_motor_policy):
        """Test customer -> claims relationship"""
        # Create multiple claims
        for i in range(2):
            create_claim(
                db_session,
                claim_id=f"CLM-{i}",
                customer_id=sample_customer.id,
                policy_id=sample_motor_policy.id,
                claim_type=ClaimType.MOTOR_ACCIDENT,
                incident_date=datetime.now()
            )
        
        customer = get_customer(db_session, sample_customer.customer_id)
        assert len(customer.claims) == 2
    
    def test_policy_claims_relationship(self, db_session, sample_motor_policy):
        """Test policy -> claims relationship"""
        # Create claims for policy
        for i in range(2):
            create_claim(
                db_session,
                claim_id=f"CLM-POL-{i}",
                customer_id=sample_motor_policy.customer_id,
                policy_id=sample_motor_policy.id,
                claim_type=ClaimType.MOTOR_ACCIDENT,
                incident_date=datetime.now()
            )
        
        policy = get_policy(db_session, sample_motor_policy.policy_number)
        assert len(policy.claims) == 2


class TestClaimHistory:
    """Test ClaimHistory operations"""
    
    def test_get_customer_claim_history(self, db_session, sample_customer):
        """Test retrieving claim history for a customer"""
        from database.crud import create_claim_history
        
        # Create historical claims
        for i in range(3):
            create_claim_history(
                db_session,
                customer_id=sample_customer.customer_id,
                claim_id=f"HIST-CLM-{i}",
                claim_type="motor_accident",
                claim_amount=50000 + (i * 10000),
                filed_date=datetime.now() - timedelta(days=365 * (i + 1)),
                status="approved"
            )
        
        history = get_customer_claim_history(db_session, sample_customer.customer_id)
        
        assert len(history) == 3
        # History ordered by date DESC, most recent first (index 0 has lowest amount due to our test data)
        # Verify ordering by checking first has later date than last
        assert history[0].filed_date > history[2].filed_date
