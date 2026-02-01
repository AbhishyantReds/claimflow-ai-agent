"""
Pydantic models for FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message")
    session_id: str = Field(..., description="Unique session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Bot's response message")
    session_id: str
    conversation_complete: bool = Field(default=False, description="Whether conversation is complete")
    processing_started: bool = Field(default=False, description="Whether autonomous processing has started")


class ClaimStatusResponse(BaseModel):
    """Response model for claim status endpoint"""
    claim_id: Optional[str] = None
    status: Optional[str] = None  # "gathering", "processing", "complete"
    decision: Optional[str] = None  # "APPROVED", "DENIED", "REVIEW"
    decision_reasoning: Optional[str] = None
    payable_amount: Optional[float] = None
    missing_documents: List[str] = []
    processing_time: Optional[float] = None
    final_report: Optional[str] = None
    conversation_complete: bool = False


class ProcessClaimRequest(BaseModel):
    """Request model for direct claim processing (legacy/alternative endpoint)"""
    claim_input: str = Field(..., description="Unstructured claim description")
    customer_id: Optional[str] = None
    submitted_documents: List[str] = Field(default_factory=list)


class ProcessClaimResponse(BaseModel):
    """Response model for direct claim processing"""
    claim_id: str
    status: str  # "APPROVED", "DENIED", "REVIEW"
    payable_amount: float
    decision_reasoning: str
    missing_documents: List[str]
    processing_time: float
    detailed_report: str


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: datetime
    rag_available: bool
    message: str
