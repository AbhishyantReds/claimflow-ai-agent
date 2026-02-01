"""
CRUD (Create, Read, Update, Delete) operations for ClaimFlow database
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.models import (
    Customer, Policy, Claim, ClaimHistory,
    ClaimStatus, PolicyType, ClaimType
)


# ============ Customer CRUD ============

def create_customer(
    session: Session,
    customer_id: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None
) -> Customer:
    """Create a new customer"""
    customer = Customer(
        customer_id=customer_id,
        name=name,
        email=email,
        phone=phone,
        address=address
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def get_customer(session: Session, customer_id: str) -> Optional[Customer]:
    """Get customer by customer_id"""
    return session.query(Customer).filter(Customer.customer_id == customer_id).first()


def get_customer_by_id(session: Session, id: int) -> Optional[Customer]:
    """Get customer by primary key id"""
    return session.query(Customer).filter(Customer.id == id).first()


def update_customer(session: Session, customer_id: str, **kwargs) -> Optional[Customer]:
    """Update customer details"""
    customer = get_customer(session, customer_id)
    if customer:
        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        customer.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(customer)
    return customer


def list_customers(session: Session, limit: int = 100) -> List[Customer]:
    """List all customers"""
    return session.query(Customer).limit(limit).all()


# ============ Policy CRUD ============

def create_policy(
    session: Session,
    policy_number: str,
    customer_id: int,
    policy_type: PolicyType,
    sum_insured: float,
    policy_start: datetime,
    policy_end: datetime,
    **kwargs
) -> Policy:
    """Create a new policy"""
    policy = Policy(
        policy_number=policy_number,
        customer_id=customer_id,
        policy_type=policy_type,
        sum_insured=sum_insured,
        policy_start=policy_start,
        policy_end=policy_end,
        **kwargs
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


def get_policy(session: Session, policy_number: str) -> Optional[Policy]:
    """Get policy by policy number"""
    return session.query(Policy).filter(Policy.policy_number == policy_number).first()


def get_policy_by_identifier(session: Session, identifier: str) -> Optional[Policy]:
    """Get policy by vehicle registration, property ID, or policy number"""
    return session.query(Policy).filter(
        or_(
            Policy.policy_number == identifier,
            Policy.vehicle_registration == identifier,
            Policy.property_id == identifier
        )
    ).first()


def get_customer_policies(session: Session, customer_id: int) -> List[Policy]:
    """Get all policies for a customer"""
    return session.query(Policy).filter(Policy.customer_id == customer_id).all()


def update_policy(session: Session, policy_number: str, **kwargs) -> Optional[Policy]:
    """Update policy details"""
    policy = get_policy(session, policy_number)
    if policy:
        for key, value in kwargs.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        policy.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(policy)
    return policy


def list_policies(session: Session, policy_type: Optional[PolicyType] = None, limit: int = 100) -> List[Policy]:
    """List policies, optionally filtered by type"""
    query = session.query(Policy)
    if policy_type:
        query = query.filter(Policy.policy_type == policy_type)
    return query.limit(limit).all()


# ============ Claim CRUD ============

def create_claim(
    session: Session,
    claim_id: str,
    customer_id: int,
    policy_id: int,
    claim_type: ClaimType,
    incident_date: datetime,
    **kwargs
) -> Claim:
    """Create a new claim"""
    claim = Claim(
        claim_id=claim_id,
        customer_id=customer_id,
        policy_id=policy_id,
        claim_type=claim_type,
        incident_date=incident_date,
        **kwargs
    )
    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim


def get_claim(session: Session, claim_id: str) -> Optional[Claim]:
    """Get claim by claim ID"""
    return session.query(Claim).filter(Claim.claim_id == claim_id).first()


def get_customer_claims(session: Session, customer_id: int) -> List[Claim]:
    """Get all claims for a customer"""
    return session.query(Claim).filter(Claim.customer_id == customer_id).all()


def get_policy_claims(session: Session, policy_id: int) -> List[Claim]:
    """Get all claims for a policy"""
    return session.query(Claim).filter(Claim.policy_id == policy_id).all()


def update_claim(session: Session, claim_id: str, **kwargs) -> Optional[Claim]:
    """Update claim details"""
    claim = get_claim(session, claim_id)
    if claim:
        for key, value in kwargs.items():
            if hasattr(claim, key):
                setattr(claim, key, value)
        claim.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(claim)
    return claim


def update_claim_status(session: Session, claim_id: str, status: ClaimStatus) -> Optional[Claim]:
    """Update claim status"""
    claim = get_claim(session, claim_id)
    if claim:
        claim.status = status
        claim.updated_at = datetime.utcnow()
        
        # Set decision date when approved/rejected
        if status in [ClaimStatus.APPROVED, ClaimStatus.REJECTED]:
            claim.decision_date = datetime.utcnow()
        
        # Set closed date when closed
        if status == ClaimStatus.CLOSED:
            claim.closed_date = datetime.utcnow()
        
        session.commit()
        session.refresh(claim)
    return claim


def list_claims(
    session: Session,
    status: Optional[ClaimStatus] = None,
    claim_type: Optional[ClaimType] = None,
    limit: int = 100
) -> List[Claim]:
    """List claims with optional filters"""
    query = session.query(Claim)
    if status:
        query = query.filter(Claim.status == status)
    if claim_type:
        query = query.filter(Claim.claim_type == claim_type)
    return query.order_by(Claim.filed_date.desc()).limit(limit).all()


# ============ Claim History CRUD ============

def create_claim_history(
    session: Session,
    customer_id: str,
    claim_id: str,
    claim_type: str,
    claim_amount: float,
    filed_date: datetime,
    status: str
) -> ClaimHistory:
    """Create a claim history record"""
    history = ClaimHistory(
        customer_id=customer_id,
        claim_id=claim_id,
        claim_type=claim_type,
        claim_amount=claim_amount,
        filed_date=filed_date,
        status=status
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


def get_customer_claim_history(session: Session, customer_id: str) -> List[ClaimHistory]:
    """Get claim history for a customer"""
    return session.query(ClaimHistory).filter(
        ClaimHistory.customer_id == customer_id
    ).order_by(ClaimHistory.filed_date.desc()).all()


# ============ Helper Functions ============

def get_or_create_customer(
    session: Session,
    customer_id: str,
    name: str,
    **kwargs
) -> Customer:
    """Get existing customer or create new one"""
    customer = get_customer(session, customer_id)
    if not customer:
        customer = create_customer(session, customer_id, name, **kwargs)
    return customer


def get_claim_with_details(session: Session, claim_id: str) -> Optional[Dict]:
    """Get claim with customer and policy details"""
    claim = session.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        return None
    
    return {
        'claim': claim,
        'customer': claim.customer,
        'policy': claim.policy
    }


def search_claims(
    session: Session,
    customer_id: Optional[str] = None,
    policy_number: Optional[str] = None,
    status: Optional[ClaimStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Claim]:
    """Advanced claim search with multiple filters"""
    query = session.query(Claim)
    
    if customer_id:
        query = query.join(Customer).filter(Customer.customer_id == customer_id)
    
    if policy_number:
        query = query.join(Policy).filter(Policy.policy_number == policy_number)
    
    if status:
        query = query.filter(Claim.status == status)
    
    if from_date:
        query = query.filter(Claim.filed_date >= from_date)
    
    if to_date:
        query = query.filter(Claim.filed_date <= to_date)
    
    return query.order_by(Claim.filed_date.desc()).all()
