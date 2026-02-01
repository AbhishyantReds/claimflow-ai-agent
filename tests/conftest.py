"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    from database.models import DatabaseManager, Base
    
    # Use in-memory database for tests
    db_manager = DatabaseManager("sqlite:///:memory:")
    db_manager.create_tables()
    
    session = db_manager.get_session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=db_manager.engine)


@pytest.fixture(scope="function")
def sample_customer(db_session):
    """Create a sample customer"""
    from database.crud import create_customer
    
    customer = create_customer(
        db_session,
        customer_id="TEST-001",
        name="Test Customer",
        email="test@example.com",
        phone="+91-9999999999"
    )
    
    return customer


@pytest.fixture(scope="function")
def sample_motor_policy(db_session, sample_customer):
    """Create a sample motor policy"""
    from database.crud import create_policy
    from database.models import PolicyType
    from datetime import datetime, timedelta
    
    policy = create_policy(
        db_session,
        policy_number="TEST-MI-001",
        customer_id=sample_customer.id,
        policy_type=PolicyType.MOTOR,
        coverage_type="comprehensive",
        sum_insured=1000000,
        premium=30000,
        vehicle_registration="TEST-KA-1234",
        idv=1000000,
        deductible=2000,
        zero_depreciation=True,
        ncb_percentage=20,
        policy_start=datetime.now(),
        policy_end=datetime.now() + timedelta(days=365),
        status="active"
    )
    
    return policy


@pytest.fixture(scope="function")
def sample_claim(db_session, sample_customer, sample_motor_policy):
    """Create a sample claim"""
    from database.crud import create_claim
    from database.models import ClaimType
    from datetime import datetime
    
    claim = create_claim(
        db_session,
        claim_id="TEST-CLM-001",
        customer_id=sample_customer.id,
        policy_id=sample_motor_policy.id,
        claim_type=ClaimType.MOTOR_ACCIDENT,
        incident_date=datetime.now(),
        incident_location="Test Location",
        incident_description="Test accident",
        vehicle_registration="TEST-KA-1234",
        estimated_cost=50000
    )
    
    return claim


@pytest.fixture(scope="function")
def mock_openai_response(monkeypatch):
    """Mock OpenAI API responses"""
    class MockCompletion:
        def __init__(self, content):
            self.content = content
            
        class Choice:
            def __init__(self, content):
                self.message = type('obj', (object,), {'content': content})()
        
        def __init__(self, content):
            self.choices = [self.Choice(content)]
    
    def mock_create(*args, **kwargs):
        # Return a simple mock response
        return MockCompletion('{"claim_type": "motor_accident", "vehicle_registration": "KA-01-AB-1234"}')
    
    # Mock the OpenAI client
    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create
    
    monkeypatch.setattr("langchain_openai.ChatOpenAI", lambda *args, **kwargs: mock_client)
    
    return mock_client


@pytest.fixture(scope="session")
def vector_store_test():
    """Create a test vector store"""
    from agent.rag import VectorStore
    import tempfile
    
    # Use temporary directory for test vector store
    with tempfile.TemporaryDirectory() as tmpdir:
        vector_store = VectorStore(persist_directory=tmpdir)
        
        # Add sample document
        vector_store.add_document(
            document_text="This is a test policy document about motor insurance.",
            document_id="test_policy",
            metadata={"policy_type": "motor", "policy_name": "Test Policy"}
        )
        
        yield vector_store
