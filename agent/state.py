"""
State management for ClaimFlow AI Agent
Defines the state structure used throughout the LangGraph workflow
"""
from typing import Annotated, Sequence, Any
from langchain_core.messages import BaseMessage
from operator import add


class ClaimState(dict):
    """
    State object that flows through the LangGraph workflow.
    
    Phase 1 (Conversational): Gathers information through chat
    Phase 2 (Autonomous): Processes claim through 9 sequential steps
    """
    
    # Chat history with automatic message accumulation
    messages: Annotated[Sequence[BaseMessage], add]
    
    # All other fields as dict - more flexible for Gradio compatibility
    claim_data: Any
    missing_fields: Any
    asked_questions: Any  # Track questions already asked to prevent repeats
    conversation_complete: Any
    conversation_turn_count: Any
    current_question: Any
    processing_step: Any
    extracted_data: Any
    detected_claim_category: Any  # Motor, Home, or Health (auto-detected)
    policy_data: Any
    coverage_check: Any
    exclusions: Any
    payout_calculation: Any
    document_status: Any
    claim_history: Any
    decision: Any
    decision_reasoning: Any
    final_report: Any
    claim_id: Any
    session_id: Any
    processing_time: Any
    error: Any
