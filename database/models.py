"""
Database models for ClaimFlow AI
Using SQLAlchemy ORM for SQLite database
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


class ClaimStatus(enum.Enum):
    """Claim processing status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    DOCUMENTS_PENDING = "documents_pending"
    PAYMENT_PROCESSING = "payment_processing"
    CLOSED = "closed"


class PolicyType(enum.Enum):
    """Insurance policy types"""
    MOTOR = "motor"
    HOME = "home"
    HEALTH = "health"


class ClaimType(enum.Enum):
    """Specific claim types"""
    # Motor
    MOTOR_ACCIDENT = "motor_accident"
    MOTOR_THEFT = "motor_theft"
    MOTOR_FIRE = "motor_fire"
    MOTOR_VANDALISM = "motor_vandalism"
    
    # Home
    HOME_FIRE = "home_fire"
    HOME_THEFT = "home_theft"
    HOME_FLOOD = "home_flood"
    HOME_EARTHQUAKE = "home_earthquake"
    HOME_STORM = "home_storm"
    
    # Health
    HEALTH_ACCIDENT = "health_accident"
    HEALTH_HOSPITALIZATION = "health_hospitalization"
    HEALTH_SURGERY = "health_surgery"
    HEALTH_CRITICAL_ILLNESS = "health_critical_illness"


class Customer(Base):
    """Customer/Policyholder information"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200))
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policies = relationship("Policy", back_populates="customer", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(customer_id='{self.customer_id}', name='{self.name}')>"


class Policy(Base):
    """Insurance policy details"""
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Policy details
    policy_type = Column(Enum(PolicyType), nullable=False)
    coverage_type = Column(String(100))  # comprehensive, third_party, etc.
    sum_insured = Column(Float, nullable=False)
    premium = Column(Float)
    
    # Specific identifiers
    vehicle_registration = Column(String(50))  # For motor
    property_id = Column(String(50))  # For home
    policy_holder_age = Column(Integer)  # For health
    
    # Coverage details
    idv = Column(Float)  # Insured Declared Value for motor
    deductible = Column(Float, default=0)
    zero_depreciation = Column(Boolean, default=False)
    ncb_percentage = Column(Float, default=0)  # No Claim Bonus
    copay_percentage = Column(Float, default=0)  # For health
    
    # Policy period
    policy_start = Column(DateTime, nullable=False)
    policy_end = Column(DateTime, nullable=False)
    status = Column(String(20), default="active")  # active, expired, cancelled
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="policies")
    claims = relationship("Claim", back_populates="policy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Policy(policy_number='{self.policy_number}', type='{self.policy_type.value}')>"


class Claim(Base):
    """Insurance claim details"""
    __tablename__ = 'claims'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    
    # Claim type and status
    claim_type = Column(Enum(ClaimType), nullable=False)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    
    # Incident details
    incident_date = Column(DateTime, nullable=False)
    incident_location = Column(String(500))
    incident_description = Column(Text)
    
    # Damage/Medical details
    damage_description = Column(Text)
    estimated_cost = Column(Float)
    approved_amount = Column(Float)
    
    # Motor-specific
    vehicle_registration = Column(String(50))
    repair_garage = Column(String(200))
    
    # Home-specific
    property_id = Column(String(50))
    affected_items = Column(Text)
    
    # Health-specific
    hospital_name = Column(String(200))
    treatment_type = Column(String(200))
    hospitalization_date = Column(DateTime)
    discharge_date = Column(DateTime)
    treatment_cost = Column(Float)
    
    # Documents
    documents_submitted = Column(Text)  # JSON string of document list
    documents_verified = Column(Boolean, default=False)
    
    # Processing details
    coverage_verified = Column(Boolean, default=False)
    fraud_check_passed = Column(Boolean, default=False)
    claim_history_checked = Column(Boolean, default=False)
    
    # Decision
    decision = Column(String(20))  # approved, rejected, under_review
    decision_reason = Column(Text)
    payout_amount = Column(Float)
    depreciation_applied = Column(Float)
    copay_applied = Column(Float)
    
    # Report
    final_report = Column(Text)
    
    # Timestamps
    filed_date = Column(DateTime, default=datetime.utcnow)
    decision_date = Column(DateTime)
    closed_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    
    def __repr__(self):
        return f"<Claim(claim_id='{self.claim_id}', type='{self.claim_type.value}', status='{self.status.value}')>"


class ClaimHistory(Base):
    """Historical claim records for reference"""
    __tablename__ = 'claim_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), nullable=False, index=True)
    claim_id = Column(String(50), nullable=False)
    claim_type = Column(String(100))
    claim_amount = Column(Float)
    filed_date = Column(DateTime)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ClaimHistory(customer_id='{self.customer_id}', claim_id='{self.claim_id}')>"


# Database connection and session management
class DatabaseManager:
    """Manages database connection and sessions"""
    
    def __init__(self, database_url: str = "sqlite:///data/claimflow.db"):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},  # For SQLite
            echo=False  # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def reset_database(self):
        """Reset the database by dropping and recreating all tables"""
        self.drop_tables()
        self.create_tables()


# Singleton instance
_db_manager = None

def get_db_manager(database_url: str = "sqlite:///data/claimflow.db") -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def get_db_session():
    """Get a database session (for dependency injection)"""
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
