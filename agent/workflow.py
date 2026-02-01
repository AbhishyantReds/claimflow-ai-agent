"""
LangGraph Workflow for ClaimFlow AI
Implements dual-phase conversational + autonomous processing
Updated: 2026-02-01
"""
import json
import logging
import logging.config
import time
import uuid
from typing import Literal
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

import config
from agent.state import ClaimState
from agent import prompts
from agent import tools

# Configure logging
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# Initialize LLM
llm = ChatOpenAI(
    model=config.MODEL_NAME,
    temperature=config.MODEL_TEMPERATURE,
    api_key=config.OPENAI_API_KEY
)


# ============ Node Functions ============

def intake_node(state: ClaimState) -> ClaimState:
    """
    Intake node: Extracts information from conversation and updates claim_data.
    """
    logger.info("Running intake node...")
    
    try:
        # Get conversation history
        messages = state.get("messages", [])
        if not messages:
            return state
        
        # Format conversation for extraction
        conv_text = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in messages[-10:]  # Last 10 messages
        ])
        
        # Extract structured data using LLM
        extraction_prompt = prompts.FIELD_EXTRACTION_PROMPT.format(
            conversation_history=conv_text
        )
        
        response = llm.invoke([SystemMessage(content=extraction_prompt)])
        
        # Parse JSON response
        try:
            extracted = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            extracted = json.loads(content.strip())
        
        # Merge with existing claim_data
        current_data = state.get("claim_data", {})
        current_data.update({k: v for k, v in extracted.items() if v})
        
        state["claim_data"] = current_data
        logger.info(f"Extracted fields: {list(extracted.keys())}")
        
    except Exception as e:
        logger.error(f"Error in intake_node: {e}")
        state["error"] = str(e)
    
    return state


def check_completeness(state: ClaimState) -> Literal["continue", "process"]:
    """
    Conditional edge: Determines if conversation should continue or processing should start.
    """
    claim_data = state.get("claim_data", {})
    turn_count = state.get("conversation_turn_count", 0)
    
    # Check if we've hit the turn limit
    if turn_count >= config.MAX_CONVERSATION_TURNS:
        logger.warning(f"Hit conversation turn limit ({config.MAX_CONVERSATION_TURNS})")
        return "process"
    
    # Determine required fields based on claim type
    claim_type = claim_data.get("claim_type", "")
    
    # Universal required fields
    required = ["claim_type", "incident_date"]
    
    if claim_type.startswith("motor_"):
        required.extend(["damage_description", "vehicle_registration", "repair_estimate"])
    elif claim_type.startswith("home_"):
        required.extend(["damage_description", "property_id", "repair_estimate"])
    elif claim_type.startswith("health_"):
        required.extend(["treatment_type", "hospital_name", "treatment_cost"])
        if claim_type in ["health_hospitalization", "health_surgery", "health_critical_illness"]:
            required.append("hospitalization_date")
    else:
        # Unknown type - ask for basic info
        required.extend(["damage_description"])
    
    # Check what's missing
    missing = [field for field in required if not claim_data.get(field)]
    
    state["missing_fields"] = missing
    
    if not missing or len(missing) == 0:
        logger.info("All critical information collected, proceeding to processing")
        return "process"
    else:
        logger.info(f"Still need: {', '.join(missing)}")
        return "continue"


def ask_question_node(state: ClaimState) -> ClaimState:
    """
    Ask Question node: Generates next question based on missing information.
    """
    logger.info("Generating next question...")
    
    try:
        messages = state.get("messages", [])
        claim_data = state.get("claim_data", {})
        missing_fields = state.get("missing_fields", [])
        turn_count = state.get("conversation_turn_count", 0)
        asked_questions = state.get("asked_questions", [])
        detected_category = state.get("detected_claim_category", "")
        
        # Check if this is the first message (greeting)
        human_messages = [m for m in messages if isinstance(m, HumanMessage)]
        if len(human_messages) == 1:
            # First interaction - check if it's just a greeting
            user_msg = human_messages[0].content.lower().strip()
            
            # Is it just a greeting?
            if user_msg in ["hi", "hello", "hey", "hi there", "hello there"]:
                response = "Hello! I'm your ClaimFlow AI assistant. I'm here to help you file your insurance claim today. To get started, could you tell me what happened? For example, 'My car was damaged' or 'I had a medical emergency'."
                state["messages"] = state["messages"] + [AIMessage(content=response)]
                state["conversation_turn_count"] = turn_count + 1
                return state
            
            # Not just greeting - try to detect claim category
            if not detected_category:
                detection_prompt = prompts.CLAIM_TYPE_DETECTION_PROMPT.format(
                    user_description=user_msg
                )
                detection_response = llm.invoke([SystemMessage(content=detection_prompt)])
                detected_category = detection_response.content.strip().lower()
                state["detected_claim_category"] = detected_category
                logger.info(f"Auto-detected claim category: {detected_category}")
            
            # Generate empathetic first response
            if detected_category == "health":
                response = "I'm sorry to hear about that. Let me help you file your health insurance claim. Could you tell me what type of treatment or injury you had?"
            elif detected_category == "motor":
                response = "I'm sorry to hear about that. Let me help you file your motor insurance claim. Can you describe what damage occurred to your vehicle?"
            elif detected_category == "home":
                response = "I'm sorry to hear about that. Let me help you file your home insurance claim. Can you describe what damage occurred to your property?"
            else:
                response = "I'm here to help you file your insurance claim. Could you tell me more about what happened?"
            
            state["messages"] = state["messages"] + [AIMessage(content=response)]
            state["conversation_turn_count"] = turn_count + 1
            state["asked_questions"] = asked_questions + [response]
            return state
        
        # Auto-detect claim category if not already done
        if not detected_category and len(human_messages) > 0:
            recent_user_msgs = " ".join([m.content for m in human_messages[:3]])
            detection_prompt = prompts.CLAIM_TYPE_DETECTION_PROMPT.format(
                user_description=recent_user_msgs
            )
            detection_response = llm.invoke([SystemMessage(content=detection_prompt)])
            detected_category = detection_response.content.strip().lower()
            state["detected_claim_category"] = detected_category
            logger.info(f"Auto-detected claim category: {detected_category}")
        
        # Generate next question based on missing fields
        collected_info = json.dumps(claim_data, indent=2)
        recent_msgs = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in messages[-4:]
        ])
        
        # Format asked questions for prompt
        asked_q_str = "\n".join([f"- {q}" for q in asked_questions[-5:]]) if asked_questions else "None"
        
        question_prompt = prompts.NEXT_QUESTION_PROMPT.format(
            claim_category=detected_category or "unknown",
            collected_info=collected_info,
            missing_fields=", ".join(missing_fields) if missing_fields else "None",
            asked_questions=asked_q_str,
            recent_messages=recent_msgs
        )
        
        # Use CONVERSATION_SYSTEM_PROMPT for better conversational flow
        response = llm.invoke([
            SystemMessage(content=prompts.CONVERSATION_SYSTEM_PROMPT),
            SystemMessage(content=question_prompt)
        ])
        next_question = response.content.strip()
        
        # Add to conversation and track
        state["messages"] = state["messages"] + [AIMessage(content=next_question)]
        state["conversation_turn_count"] = turn_count + 1
        state["asked_questions"] = asked_questions + [next_question]
        state["current_question"] = next_question
        
        logger.info(f"Asked: {next_question[:50]}...")
        
    except Exception as e:
        logger.error(f"Error in ask_question_node: {e}", exc_info=True)
        # Debug mode - show actual error
        fallback_question = f"❌ DEBUG ERROR: {str(e)}\n\nCheck: 1) OPENAI_API_KEY in HF Secrets, 2) HF logs for stack trace."
        state["messages"] = state["messages"] + [AIMessage(content=fallback_question)]
        state["error"] = str(e)
    
    return state


def transition_node(state: ClaimState) -> ClaimState:
    """
    Transition node: Moves from conversation to autonomous processing.
    """
    logger.info("Transitioning to autonomous processing...")
    
    # Add transition message
    transition_msg = prompts.PROCESSING_TRANSITION_MESSAGE
    state["messages"] = state["messages"] + [AIMessage(content=transition_msg)]
    state["processing_step"] = "processing"
    state["conversation_complete"] = True
    
    # Generate claim ID
    state["claim_id"] = f"CLM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    return state


def step_1_extract_data(state: ClaimState) -> ClaimState:
    """Step 1: Extract and structure claim data"""
    msg = "📝 Step 1/9: Extracting claim data..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = tools.extract_claim_data_from_conversation(state.get("claim_data", {}))
    state["extracted_data"] = extracted
    
    return state


def step_2_retrieve_policy(state: ClaimState) -> ClaimState:
    """Step 2: Retrieve policy from RAG"""
    msg = "🔍 Step 2/9: Retrieving policy information..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = state.get("extracted_data", {})
    identifier = extracted.get("vehicle_registration") or extracted.get("property_id") or extracted.get("customer_id", "")
    
    policy = tools.retrieve_policy(identifier)
    state["policy_data"] = policy
    
    return state


def step_3_check_coverage(state: ClaimState) -> ClaimState:
    """Step 3: Check coverage"""
    msg = "✅ Step 3/9: Verifying coverage..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = state.get("extracted_data", {})
    policy = state.get("policy_data", {})
    
    coverage = tools.check_coverage(
        extracted.get("claim_type", ""),
        policy,
        extracted.get("vehicle_registration", "")
    )
    state["coverage_check"] = coverage
    
    return state


def step_4_check_exclusions(state: ClaimState) -> ClaimState:
    """Step 4: Check exclusions"""
    msg = "⚠️ Step 4/9: Checking policy exclusions..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = state.get("extracted_data", {})
    policy = state.get("policy_data", {})
    
    exclusions = tools.check_exclusions(extracted, policy)
    state["exclusions"] = exclusions
    
    return state


def step_5_calculate_payout(state: ClaimState) -> ClaimState:
    """Step 5: Calculate payout"""
    msg = "💰 Step 5/9: Calculating payout..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = state.get("extracted_data", {})
    policy = state.get("policy_data", {})
    claim_type = extracted.get("claim_type", "")
    
    # Use treatment_cost for health claims, repair_estimate for motor/home
    if claim_type.startswith("health_"):
        claim_amount = extracted.get("treatment_cost", 0)
    else:
        claim_amount = extracted.get("repair_estimate", 0)
    
    payout = tools.calculate_payout(
        claim_amount,
        policy,
        vehicle_age_years=1,
        claim_type=claim_type
    )
    state["payout_calculation"] = payout
    
    return state


def step_6_verify_documents(state: ClaimState) -> ClaimState:
    """Step 6: Verify documents"""
    msg = "📄 Step 6/9: Verifying documents..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = state.get("extracted_data", {})
    
    doc_status = tools.verify_documents(
        extracted.get("claim_type", ""),
        extracted.get("submitted_documents", [])
    )
    state["document_status"] = doc_status
    
    return state


def step_7_check_history(state: ClaimState) -> ClaimState:
    """Step 7: Check claim history"""
    msg = "📊 Step 7/9: Checking claim history..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    extracted = state.get("extracted_data", {})
    
    history = tools.check_claim_history(
        extracted.get("customer_id", ""),
        extracted.get("vehicle_registration", "")
    )
    state["claim_history"] = history
    
    return state


def step_8_make_decision(state: ClaimState) -> ClaimState:
    """Step 8: Make decision"""
    msg = "⚖️ Step 8/9: Making decision..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    decision, reasoning = tools.make_decision(
        state.get("coverage_check", {}),
        state.get("exclusions", []),
        state.get("payout_calculation", {}),
        state.get("document_status", {}),
        state.get("claim_history", {}),
        state.get("extracted_data", {}).get("repair_estimate", 0)
    )
    
    state["decision"] = decision
    state["decision_reasoning"] = reasoning
    
    return state


def step_9_generate_report(state: ClaimState) -> ClaimState:
    """Step 9: Generate final report"""
    msg = "📋 Step 9/9: Generating final report..."
    state["messages"] = state["messages"] + [AIMessage(content=msg)]
    
    start_time = state.get("processing_start_time", time.time())
    processing_time = time.time() - start_time
    
    report = tools.generate_report(
        state.get("claim_id", ""),
        state.get("extracted_data", {}),
        state.get("coverage_check", {}),
        state.get("exclusions", []),
        state.get("payout_calculation", {}),
        state.get("document_status", {}),
        state.get("claim_history", {}),
        state.get("decision", ""),
        state.get("decision_reasoning", ""),
        processing_time
    )
    
    state["final_report"] = report
    state["processing_time"] = processing_time
    state["processing_step"] = "complete"
    
    # Add report to messages
    state["messages"] = state["messages"] + [AIMessage(content=report)]
    
    return state


# ============ Build Graph ============

def create_workflow() -> StateGraph:
    """
    Creates the LangGraph workflow with conversational + autonomous phases.
    """
    workflow = StateGraph(ClaimState)
    
    # Add nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("ask_question", ask_question_node)
    workflow.add_node("transition", transition_node)
    workflow.add_node("step_1", step_1_extract_data)
    workflow.add_node("step_2", step_2_retrieve_policy)
    workflow.add_node("step_3", step_3_check_coverage)
    workflow.add_node("step_4", step_4_check_exclusions)
    workflow.add_node("step_5", step_5_calculate_payout)
    workflow.add_node("step_6", step_6_verify_documents)
    workflow.add_node("step_7", step_7_check_history)
    workflow.add_node("step_8", step_8_make_decision)
    workflow.add_node("step_9", step_9_generate_report)
    
    # Set entry point
    workflow.set_entry_point("intake")
    
    # Add edges
    # Phase 1: Conversational loop
    workflow.add_conditional_edges(
        "intake",
        check_completeness,
        {
            "continue": "ask_question",
            "process": "transition"
        }
    )
    
    workflow.add_edge("ask_question", END)  # Wait for user response
    
    # Phase 2: Autonomous processing (linear)
    workflow.add_edge("transition", "step_1")
    workflow.add_edge("step_1", "step_2")
    workflow.add_edge("step_2", "step_3")
    workflow.add_edge("step_3", "step_4")
    workflow.add_edge("step_4", "step_5")
    workflow.add_edge("step_5", "step_6")
    workflow.add_edge("step_6", "step_7")
    workflow.add_edge("step_7", "step_8")
    workflow.add_edge("step_8", "step_9")
    workflow.add_edge("step_9", END)
    
    return workflow


# Create the compiled graph with checkpointing
memory = MemorySaver()
workflow = create_workflow()
graph = workflow.compile(checkpointer=memory)

logger.info("LangGraph workflow compiled successfully")
