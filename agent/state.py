"""
State management for ClaimFlow AI Agent
Defines the state structure used throughout the LangGraph workflow

Updated for hybrid agent architecture with reasoning traces for auditability.
"""
from typing import Annotated, Sequence, Any, Optional, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, AnyMessage
from langgraph.graph.message import add_messages
from datetime import datetime
from pydantic import BaseModel, Field


# ============ Reasoning Trace Models (for Auditability) ============

class ToolInvocation(BaseModel):
    """Record of a single tool call for auditability"""
    tool_name: str
    tool_input: dict
    tool_output: Any
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class ReasoningStep(BaseModel):
    """Captures agent's reasoning for each decision"""
    step_number: int
    thought: str  # What the agent was thinking
    action: str   # What action it decided to take
    observation: str  # What it observed from the action
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AgentTrace(BaseModel):
    """Complete trace of agent processing for audit"""
    session_id: str
    claim_id: str
    start_time: str
    end_time: Optional[str] = None
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)
    tool_invocations: List[ToolInvocation] = Field(default_factory=list)
    total_tokens_used: int = 0
    final_decision: Optional[str] = None


# ============ Validation State ============

class ValidationResult(BaseModel):
    """Result of tool dependency validation"""
    valid: bool
    missing_dependencies: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


# ============ Main State Schema ============

class ClaimState(TypedDict):
    """
    State object for hybrid LangGraph workflow.
    
    Phase 1 (Deterministic): Conversational information gathering
    Phase 2 (Agentic): LLM-driven processing with dynamic tool calls
    """
    
    # === Message History (shared between phases) ===
    # Use add_messages reducer for proper message handling
    messages: Annotated[Sequence[AnyMessage], add_messages]
    
    # === Conversation Phase Fields (deterministic) ===
    claim_data: dict                    # Collected user information
    missing_fields: List[str]           # Fields still needed
    asked_questions: List[str]          # Track asked questions
    conversation_complete: bool         # Transition trigger
    conversation_turn_count: int        # Turn counter
    current_question: str               # Current question being asked
    detected_claim_category: str        # Motor/Home/Health
    
    # === Agent Phase Fields (NEW) ===
    agent_messages: Annotated[Sequence[AnyMessage], add_messages]  # Agent-specific messages
    agent_scratchpad: str               # Agent's working memory
    
    # === Processing Results (populated by tools) ===
    extracted_data: dict
    policy_data: dict
    coverage_check: dict
    exclusions: List[dict]
    payout_calculation: dict
    document_status: dict
    claim_history: dict
    decision: str
    decision_reasoning: str
    final_report: str
    
    # === Metadata ===
    claim_id: str
    session_id: str
    processing_step: str
    processing_time: float
    processing_start_time: float
    error: Optional[str]
    
    # === Auditability (NEW) ===
    reasoning_trace: Optional[dict]     # Serialized AgentTrace
    tool_call_count: int                # Track tool calls for safety limits
    max_tool_calls: int                 # Safety limit (default: 20)
    validation_errors: List[str]        # Track any validation failures


def create_initial_state(session_id: str) -> dict:
    """Factory function to create properly initialized state"""
    return {
        "messages": [],
        "claim_data": {},
        "missing_fields": [],
        "asked_questions": [],
        "conversation_complete": False,
        "conversation_turn_count": 0,
        "current_question": "",
        "detected_claim_category": "",
        "agent_messages": [],
        "agent_scratchpad": "",
        "extracted_data": {},
        "policy_data": {},
        "coverage_check": {},
        "exclusions": [],
        "payout_calculation": {},
        "document_status": {},
        "claim_history": {},
        "decision": "",
        "decision_reasoning": "",
        "final_report": "",
        "claim_id": "",
        "session_id": session_id,
        "processing_step": "conversation",
        "processing_time": 0.0,
        "processing_start_time": 0.0,
        "error": None,
        "reasoning_trace": AgentTrace(
            session_id=session_id,
            claim_id="",
            start_time=datetime.now().isoformat()
        ).model_dump(),
        "tool_call_count": 0,
        "max_tool_calls": 20,
        "validation_errors": []
    }
