"""
LangGraph Workflow for ClaimFlow AI
Hybrid Architecture: Deterministic Conversation + Agentic Processing

Phase 1 (Deterministic): intake → check_completeness → ask_question (loop)
Phase 2 (Agentic): transition → agent ↔ tool_executor → finalize

Updated: 2026-02-04
"""
import json
import logging
import logging.config
import time
import uuid
from typing import Literal, Sequence, List
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

import config
from agent.state import ClaimState, create_initial_state, ReasoningStep
from agent import prompts
from agent.tools_agent import PROCESSING_TOOLS, TOOL_MAP

# Configure logging
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# ============ LLM Setup ============

# Conversation LLM (slightly creative for natural dialogue)
conversation_llm = ChatOpenAI(
    model=config.MODEL_NAME,
    temperature=0.7,
    api_key=config.OPENAI_API_KEY
)

# Agent LLM with tools bound (more deterministic for processing)
agent_llm = ChatOpenAI(
    model=config.MODEL_NAME,
    temperature=0.1,
    api_key=config.OPENAI_API_KEY
).bind_tools(PROCESSING_TOOLS)


# ============================================================================
# PHASE 1: CONVERSATION NODES (DETERMINISTIC - UNCHANGED)
# ============================================================================

def intake_node(state: ClaimState) -> ClaimState:
    """
    Intake node: Extracts information from conversation and updates claim_data.
    DETERMINISTIC - Uses LLM only for structured extraction.
    """
    logger.info("Running intake node...")
    
    try:
        messages = state.get("messages", [])
        if not messages:
            return state
        
        # Format conversation for extraction
        conv_text = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in messages[-10:]
        ])
        
        # Extract structured data using LLM
        extraction_prompt = prompts.FIELD_EXTRACTION_PROMPT.format(
            conversation_history=conv_text
        )
        
        response = conversation_llm.invoke([SystemMessage(content=extraction_prompt)])
        
        # Parse JSON response
        try:
            extracted = json.loads(response.content)
        except json.JSONDecodeError:
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
    DETERMINISTIC decision based on field presence.
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
    DETERMINISTIC question generation based on missing fields.
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
                detection_response = conversation_llm.invoke([SystemMessage(content=detection_prompt)])
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
            detection_response = conversation_llm.invoke([SystemMessage(content=detection_prompt)])
            detected_category = detection_response.content.strip().lower()
            state["detected_claim_category"] = detected_category
            logger.info(f"Auto-detected claim category: {detected_category}")
        
        # Generate next question based on missing fields
        collected_info = json.dumps(claim_data, indent=2)
        recent_msgs = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in messages[-4:]
        ])
        
        asked_q_str = "\n".join([f"- {q}" for q in asked_questions[-5:]]) if asked_questions else "None"
        
        question_prompt = prompts.NEXT_QUESTION_PROMPT.format(
            claim_category=detected_category or "unknown",
            collected_info=collected_info,
            missing_fields=", ".join(missing_fields) if missing_fields else "None",
            asked_questions=asked_q_str,
            recent_messages=recent_msgs
        )
        
        response = conversation_llm.invoke([
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
        fallback_question = "Could you please provide more details about your claim?"
        state["messages"] = state["messages"] + [AIMessage(content=fallback_question)]
        state["error"] = str(e)
    
    return state


# ============================================================================
# PHASE 2: TRANSITION NODE
# ============================================================================

def transition_node(state: ClaimState) -> ClaimState:
    """
    Transition node: Moves from conversation to autonomous agent processing.
    Sets up agent context and initial messages.
    """
    logger.info("Transitioning to autonomous agent processing...")
    
    # Add transition message to user
    transition_msg = prompts.PROCESSING_TRANSITION_MESSAGE
    state["messages"] = state["messages"] + [AIMessage(content=transition_msg)]
    
    # Set processing flags
    state["processing_step"] = "agent_processing"
    state["conversation_complete"] = True
    state["claim_id"] = f"CLM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Initialize agent messages with system prompt
    claim_data = state.get("claim_data", {})
    agent_system = prompts.AGENT_SYSTEM_PROMPT.format(
        claim_data=json.dumps(claim_data, indent=2),
        claim_id=state["claim_id"]
    )
    
    state["agent_messages"] = [
        SystemMessage(content=agent_system),
        HumanMessage(content="Begin processing this insurance claim. Start by extracting and structuring the claim data, then proceed through all verification steps.")
    ]
    
    # Initialize counters and timing
    state["tool_call_count"] = 0
    state["max_tool_calls"] = 20
    state["processing_start_time"] = time.time()
    
    # Update reasoning trace
    if state.get("reasoning_trace"):
        state["reasoning_trace"]["claim_id"] = state["claim_id"]
    
    return state


# ============================================================================
# PHASE 2: AGENT NODES (NEW - AGENTIC PROCESSING)
# ============================================================================

def agent_node(state: ClaimState) -> ClaimState:
    """
    Agent node: LLM decides which tool(s) to call next.
    Uses bound tools to make autonomous decisions.
    """
    logger.info("Agent deciding next action...")
    
    # Check tool call limit
    if state.get("tool_call_count", 0) >= state.get("max_tool_calls", 20):
        logger.warning("Tool call limit reached, forcing finalization")
        state["agent_messages"] = state["agent_messages"] + [
            AIMessage(content="Tool call limit reached. Proceeding to finalization with available data.")
        ]
        return state
    
    # Get agent's response (may include tool calls)
    messages = state.get("agent_messages", [])
    
    try:
        response = agent_llm.invoke(messages)
        
        # Record reasoning step if the agent provided thoughts
        if response.content and state.get("reasoning_trace"):
            step_count = len(state["reasoning_trace"].get("reasoning_steps", []))
            step = ReasoningStep(
                step_number=step_count + 1,
                thought=response.content[:500] if response.content else "",
                action="tool_call" if hasattr(response, "tool_calls") and response.tool_calls else "response",
                observation=""
            )
            if "reasoning_steps" not in state["reasoning_trace"]:
                state["reasoning_trace"]["reasoning_steps"] = []
            state["reasoning_trace"]["reasoning_steps"].append(step.model_dump())
        
        # Add response to agent messages
        state["agent_messages"] = state["agent_messages"] + [response]
        
        logger.info(f"Agent response: {response.content[:100] if response.content else 'Tool calls only'}...")
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"Agent wants to call {len(response.tool_calls)} tool(s): {[tc['name'] for tc in response.tool_calls]}")
        
    except Exception as e:
        logger.error(f"Error in agent_node: {e}")
        state["error"] = str(e)
        state["agent_messages"] = state["agent_messages"] + [
            AIMessage(content=f"Error occurred: {str(e)}. Attempting to continue.")
        ]
    
    return state


def should_continue(state: ClaimState) -> Literal["tools", "finalize"]:
    """
    Conditional edge: Check if agent wants to call more tools or is done.
    """
    messages = state.get("agent_messages", [])
    if not messages:
        return "finalize"
    
    last_message = messages[-1]
    
    # If the last message has tool calls, route to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Check if processing is complete (report generated)
    if state.get("final_report"):
        logger.info("Final report exists, proceeding to finalize")
        return "finalize"
    
    # Check if we have a decision but no report yet
    if state.get("decision") and not state.get("final_report"):
        # The agent finished deciding but didn't call generate_report
        # We should finalize and generate the report there
        logger.info("Decision made but no report, proceeding to finalize")
        return "finalize"
    
    # Check tool call count
    if state.get("tool_call_count", 0) >= state.get("max_tool_calls", 20):
        logger.warning("Tool call limit reached")
        return "finalize"
    
    # Default: finalize if no tool calls
    return "finalize"


def tool_executor_node(state: ClaimState) -> ClaimState:
    """
    Execute tools called by the agent.
    Extracts tool calls from last message and executes them.
    """
    logger.info("Executing agent tool calls...")
    
    messages = state.get("agent_messages", [])
    if not messages:
        return state
    
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        logger.warning("No tool calls in last message")
        return state
    
    tool_results = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        logger.info(f"Executing tool: {tool_name} with args: {list(tool_args.keys())}")
        
        # Find the tool
        tool_fn = TOOL_MAP.get(tool_name)
        
        if tool_fn:
            try:
                start_time = time.time()
                
                # Execute the tool with provided args
                result = tool_fn.invoke(tool_args)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Store result in state based on tool name
                if tool_name == "extract_claim_data":
                    state["extracted_data"] = result
                elif tool_name == "retrieve_policy":
                    state["policy_data"] = result
                elif tool_name == "check_coverage":
                    state["coverage_check"] = result
                elif tool_name == "check_exclusions":
                    state["exclusions"] = result
                elif tool_name == "calculate_payout":
                    state["payout_calculation"] = result
                elif tool_name == "verify_documents":
                    state["document_status"] = result
                elif tool_name == "check_claim_history":
                    state["claim_history"] = result
                elif tool_name == "make_decision":
                    state["decision"] = result.get("decision", "")
                    state["decision_reasoning"] = result.get("reasoning", "")
                elif tool_name == "generate_report":
                    state["final_report"] = result
                
                # Create tool result message
                result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                tool_results.append(ToolMessage(
                    content=result_str,
                    tool_call_id=tool_id
                ))
                
                # Record in reasoning trace
                if state.get("reasoning_trace"):
                    if "tool_invocations" not in state["reasoning_trace"]:
                        state["reasoning_trace"]["tool_invocations"] = []
                    state["reasoning_trace"]["tool_invocations"].append({
                        "tool_name": tool_name,
                        "tool_input": tool_args,
                        "tool_output": result_str[:500],
                        "timestamp": datetime.now().isoformat(),
                        "duration_ms": duration_ms,
                        "success": True
                    })
                    
                    # Update last reasoning step observation
                    if state["reasoning_trace"].get("reasoning_steps"):
                        state["reasoning_trace"]["reasoning_steps"][-1]["observation"] = result_str[:200]
                
                logger.info(f"✓ Tool {tool_name} completed in {duration_ms:.0f}ms")
                
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                error_msg = f"Error executing {tool_name}: {str(e)}"
                tool_results.append(ToolMessage(
                    content=error_msg,
                    tool_call_id=tool_id
                ))
                
                # Record failure in trace
                if state.get("reasoning_trace"):
                    if "tool_invocations" not in state["reasoning_trace"]:
                        state["reasoning_trace"]["tool_invocations"] = []
                    state["reasoning_trace"]["tool_invocations"].append({
                        "tool_name": tool_name,
                        "tool_input": tool_args,
                        "tool_output": "",
                        "timestamp": datetime.now().isoformat(),
                        "duration_ms": 0,
                        "success": False,
                        "error": str(e)
                    })
        else:
            logger.warning(f"Tool {tool_name} not found in TOOL_MAP")
            tool_results.append(ToolMessage(
                content=f"Tool {tool_name} not found",
                tool_call_id=tool_id
            ))
        
        state["tool_call_count"] = state.get("tool_call_count", 0) + 1
    
    # Add all tool results to agent messages
    state["agent_messages"] = state["agent_messages"] + tool_results
    
    return state


def finalize_node(state: ClaimState) -> ClaimState:
    """
    Finalize processing: Generate report if not done, add to user messages.
    This ensures we always have a complete report.
    """
    logger.info("Finalizing claim processing...")
    
    # Calculate processing time
    start_time = state.get("processing_start_time", time.time())
    processing_time = time.time() - start_time
    state["processing_time"] = processing_time
    
    # If no report generated, create one from available data
    if not state.get("final_report"):
        logger.info("Generating final report from finalize node...")
        
        from agent.tools_agent import generate_report
        
        # Get all the data we have
        claim_data = state.get("extracted_data") or state.get("claim_data", {})
        coverage = state.get("coverage_check", {})
        exclusions = state.get("exclusions", [])
        payout = state.get("payout_calculation", {})
        docs = state.get("document_status", {})
        history = state.get("claim_history", {})
        decision = state.get("decision", "REVIEW")
        reasoning = state.get("decision_reasoning", "Processing incomplete - manual review required")
        
        # If we don't have a decision, make one
        if not decision or decision == "":
            if coverage.get("covered", False):
                decision = "REVIEW"
                reasoning = "Claim requires manual review - automated processing incomplete"
            else:
                decision = "DENIED" if coverage else "REVIEW"
                reasoning = coverage.get("section", "Coverage status unknown")
            state["decision"] = decision
            state["decision_reasoning"] = reasoning
        
        try:
            report = generate_report.invoke({
                "claim_id": state.get("claim_id", "UNKNOWN"),
                "claim_data": claim_data,
                "coverage_check": coverage,
                "exclusions": exclusions,
                "payout_calculation": payout,
                "document_status": docs,
                "claim_history": history,
                "decision": decision,
                "decision_reasoning": reasoning,
                "processing_time": processing_time
            })
            state["final_report"] = report
        except Exception as e:
            logger.error(f"Error generating report in finalize: {e}")
            state["final_report"] = f"""
===== CLAIM PROCESSING REPORT =====
Claim ID: {state.get('claim_id', 'UNKNOWN')}
Status: {decision}
Reasoning: {reasoning}

Note: Full report generation failed. Please review manually.
Processing Time: {processing_time:.2f} seconds
=====================================
"""
    
    # Add report to user messages
    state["messages"] = state["messages"] + [AIMessage(content=state["final_report"])]
    state["processing_step"] = "complete"
    
    # Finalize reasoning trace
    if state.get("reasoning_trace"):
        state["reasoning_trace"]["end_time"] = datetime.now().isoformat()
        state["reasoning_trace"]["final_decision"] = state.get("decision", "UNKNOWN")
    
    logger.info(f"Claim processing complete. Decision: {state.get('decision')}, Time: {processing_time:.2f}s")
    
    return state


# ============================================================================
# BUILD GRAPH
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Creates the hybrid LangGraph workflow.
    
    Phase 1 (Deterministic): intake → [check_completeness] → ask_question (loop)
    Phase 2 (Agentic): transition → agent ↔ tool_executor → finalize
    """
    workflow = StateGraph(ClaimState)
    
    # ===== PHASE 1: Conversation Nodes (Deterministic) =====
    workflow.add_node("intake", intake_node)
    workflow.add_node("ask_question", ask_question_node)
    
    # ===== TRANSITION =====
    workflow.add_node("transition", transition_node)
    
    # ===== PHASE 2: Agent Nodes (Agentic) =====
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_executor_node)
    workflow.add_node("finalize", finalize_node)
    
    # ===== EDGES =====
    
    # Entry point
    workflow.set_entry_point("intake")
    
    # Phase 1: Conversation loop
    workflow.add_conditional_edges(
        "intake",
        check_completeness,
        {
            "continue": "ask_question",
            "process": "transition"
        }
    )
    workflow.add_edge("ask_question", END)  # Wait for user input
    
    # Phase 2: Transition to agent
    workflow.add_edge("transition", "agent")
    
    # Agent decision loop
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "finalize": "finalize"
        }
    )
    
    # After tools, go back to agent for next decision
    workflow.add_edge("tools", "agent")
    
    # Final node ends the graph
    workflow.add_edge("finalize", END)
    
    return workflow


# ============================================================================
# COMPILE GRAPH
# ============================================================================

memory = MemorySaver()
workflow = create_workflow()
graph = workflow.compile(checkpointer=memory)

logger.info("Hybrid LangGraph workflow (agent version) compiled successfully")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_reasoning_trace(session_id: str) -> dict:
    """
    Retrieve the reasoning trace for audit purposes.
    Can be called after processing to inspect agent decisions.
    """
    try:
        config_dict = {"configurable": {"thread_id": session_id}}
        state = graph.get_state(config_dict)
        
        if state and state.values.get("reasoning_trace"):
            trace = state.values["reasoning_trace"]
            return trace
        return {}
    except Exception as e:
        logger.error(f"Error retrieving reasoning trace: {e}")
        return {}


def get_processing_summary(session_id: str) -> dict:
    """
    Get a summary of the claim processing for a session.
    """
    try:
        config_dict = {"configurable": {"thread_id": session_id}}
        state = graph.get_state(config_dict)
        
        if state:
            return {
                "claim_id": state.values.get("claim_id"),
                "decision": state.values.get("decision"),
                "reasoning": state.values.get("decision_reasoning"),
                "processing_time": state.values.get("processing_time"),
                "tool_calls": state.values.get("tool_call_count"),
                "complete": state.values.get("processing_step") == "complete"
            }
        return {}
    except Exception as e:
        logger.error(f"Error getting processing summary: {e}")
        return {}
