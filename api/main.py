"""
FastAPI Backend for ClaimFlow AI
Provides REST API endpoints for chat and claim processing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import time
from typing import Dict
import requests

from langchain_core.messages import HumanMessage
from agent.workflow import graph
import config
from api.models import (
    ChatRequest, ChatResponse,
    ClaimStatusResponse,
    ProcessClaimRequest, ProcessClaimResponse,
    HealthResponse
)

# Configure logging
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClaimFlow AI API",
    description="Autonomous insurance claims processing with conversational AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, dict] = {}


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ClaimFlow AI",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/agent/chat",
            "status": "/agent/session/{session_id}",
            "process_claim": "/agent/process-claim",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check if RAG system is available
    rag_available = False
    try:
        response = requests.get(f"{config.INSURANCE_RAG_URL}/health", timeout=5)
        rag_available = response.status_code == 200
    except:
        rag_available = False
    
    return HealthResponse(
        status="healthy" if config.OPENAI_API_KEY else "degraded",
        timestamp=datetime.now(),
        rag_available=rag_available,
        message="ClaimFlow AI is running. RAG integration: " + ("available" if rag_available else "unavailable (using fallback)")
    )


@app.post("/agent/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for conversational claim processing.
    
    Args:
        request: ChatRequest with message and session_id
        
    Returns:
        ChatResponse with bot's response
    """
    try:
        logger.info(f"Chat request - Session: {request.session_id}, Message: {request.message[:50]}...")
        
        # Initialize session if new
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "messages": [],
                "claim_data": {},
                "missing_fields": [],
                "conversation_complete": False,
                "conversation_turn_count": 0,
                "processing_step": "gathering",
                "session_id": request.session_id,
                "processing_start_time": time.time(),
                "created_at": datetime.now().isoformat()
            }
        
        # Prepare config for LangGraph
        config_dict = {"configurable": {"thread_id": request.session_id}}
        
        # Prepare input state
        input_state = {
            "messages": [HumanMessage(content=request.message)]
        }
        
        # Execute workflow
        events = []
        for event in graph.stream(input_state, config_dict, stream_mode="values"):
            events.append(event)
        
        # Get final state
        final_state = events[-1] if events else {}
        
        # Update session with final state
        sessions[request.session_id].update({
            "claim_data": final_state.get("claim_data", {}),
            "conversation_complete": final_state.get("conversation_complete", False),
            "processing_step": final_state.get("processing_step", "gathering"),
            "claim_id": final_state.get("claim_id"),
            "decision": final_state.get("decision"),
            "final_report": final_state.get("final_report"),
        })
        
        # Extract bot's response
        messages = final_state.get("messages", [])
        bot_response = ""
        
        # Get last AI message
        for msg in reversed(messages):
            if hasattr(msg, 'content') and not isinstance(msg, HumanMessage):
                bot_response = msg.content
                break
        
        if not bot_response:
            bot_response = "I'm processing your request..."
        
        # Determine if processing has started
        processing_started = final_state.get("processing_step") == "processing"
        
        return ChatResponse(
            response=bot_response,
            session_id=request.session_id,
            conversation_complete=final_state.get("conversation_complete", False),
            processing_started=processing_started
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/agent/session/{session_id}", response_model=ClaimStatusResponse)
async def get_session_status(session_id: str):
    """
    Get status of a claim processing session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        ClaimStatusResponse with current status
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Get state from graph checkpoint
        config_dict = {"configurable": {"thread_id": session_id}}
        
        try:
            # Get current state from checkpointer
            state_snapshot = graph.get_state(config_dict)
            current_state = state_snapshot.values if state_snapshot else {}
        except:
            current_state = session
        
        # Extract relevant information
        payout_calc = current_state.get("payout_calculation", {})
        doc_status = current_state.get("document_status", {})
        
        return ClaimStatusResponse(
            claim_id=current_state.get("claim_id"),
            status=current_state.get("processing_step", "gathering"),
            decision=current_state.get("decision"),
            decision_reasoning=current_state.get("decision_reasoning"),
            payable_amount=payout_calc.get("payable_amount"),
            missing_documents=doc_status.get("missing", []),
            processing_time=current_state.get("processing_time"),
            final_report=current_state.get("final_report"),
            conversation_complete=current_state.get("conversation_complete", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")


@app.post("/agent/process-claim", response_model=ProcessClaimResponse)
async def process_claim_direct(request: ProcessClaimRequest):
    """
    Direct claim processing endpoint (legacy - processes entire claim in one shot).
    Note: The chat endpoint is recommended for better user experience.
    
    Args:
        request: ProcessClaimRequest with claim details
        
    Returns:
        ProcessClaimResponse with processing results
    """
    try:
        logger.info(f"Direct claim processing: {request.claim_input[:50]}...")
        
        # Create a temporary session
        session_id = f"direct_{int(time.time())}"
        start_time = time.time()
        
        # Simulate conversation with all info provided
        # This is a simplified version - the chat interface is recommended
        
        # You could implement direct processing here or redirect to use the chat flow
        # For now, return a message indicating to use the chat endpoint
        
        return ProcessClaimResponse(
            claim_id=f"CLM-{datetime.now().strftime('%Y%m%d')}-DIRECT",
            status="REVIEW",
            payable_amount=0,
            decision_reasoning="Please use the /agent/chat endpoint for interactive claim processing",
            missing_documents=[],
            processing_time=time.time() - start_time,
            detailed_report="Direct processing endpoint - Use /agent/chat for full conversational experience"
        )
        
    except Exception as e:
        logger.error(f"Error in direct claim processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")


@app.delete("/agent/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session (cleanup).
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting ClaimFlow AI FastAPI server...")
    
    if not config.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set!")
        print("\n⚠️  ERROR: OPENAI_API_KEY not found!")
        print("Please create a .env file with your OpenAI API key\n")
    else:
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8001,  # Using 8001 since RAG is on 8000
            reload=True
        )
