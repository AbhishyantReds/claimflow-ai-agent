"""
Simple Gradio Chat Interface for ClaimFlow AI (Standalone)
Simplified version that avoids Gradio schema parsing issues
"""
import gradio as gr
import logging
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from agent.workflow import graph
import config

logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Global session storage - persist across messages
CURRENT_SESSION = {"session_id": None}


def process_message(message, history):
    """
    Simple chat processor that works with Gradio ChatInterface
    """
    try:
        # Use persistent session ID for the entire conversation
        # Reset if history is empty (user clicked clear)
        if not history or CURRENT_SESSION["session_id"] is None:
            # Start new conversation
            CURRENT_SESSION["session_id"] = f"session_{int(time.time() * 1000)}"
            logger.info(f"Starting new conversation: {CURRENT_SESSION['session_id']}")
        
        session_id = CURRENT_SESSION["session_id"]
        config_dict = {"configurable": {"thread_id": session_id}}
        
        # First message - initialize
        if not history:
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "claim_data": {},
                "missing_fields": [],
                "conversation_complete": False,
                "conversation_turn_count": 0,
                "processing_step": "gathering",
                "processing_start_time": time.time()
            }
            
            # Execute workflow
            events = list(graph.stream(initial_state, config_dict, stream_mode="values"))
        else:
            # Continue conversation
            input_state = {"messages": [HumanMessage(content=message)]}
            events = list(graph.stream(input_state, config_dict, stream_mode="values"))
        
        # Extract bot response
        if events:
            final_state = events[-1]
            messages = final_state.get("messages", [])
            
            # Get last AI message
            for msg in reversed(messages):
                if hasattr(msg, 'content') and not isinstance(msg, HumanMessage):
                    return msg.content
        
        return "I'm processing your request..."
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return f"Error: {str(e)}"


def reset_session():
    """Reset the session when starting a new conversation"""
    CURRENT_SESSION["session_id"] = None
    return []


# Create simple interface with custom components
with gr.Blocks() as demo:
    gr.Markdown("# 🛡️ ClaimFlow AI - Insurance Claims Assistant")
    gr.Markdown("""
    Welcome! I'm your AI assistant for processing insurance claims.  
    
    **I can help you with:**
    - 🚗 **Motor Insurance** - Accidents, theft, fire damage
    - 🏠 **Home Insurance** - Fire, theft, natural disasters  
    - 🏥 **Health Insurance** - Medical claims
    
    Just tell me what happened in simple words, and I'll guide you through!
    """)
    
    chatbot = gr.Chatbot(height=500)
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Describe your claim...", 
            show_label=False,
            scale=7
        )
        submit = gr.Button("Send", scale=1)
    
    with gr.Row():
        clear = gr.Button("🔄 Start New Claim")
        
    gr.Examples(
        examples=[
            "Hi, my car got damaged in a parking lot",
            "My house caught fire yesterday",
            "I need to file a claim for vehicle theft",
        ],
        inputs=msg
    )
    
    def respond(message, chat_history):
        # Convert chat history from messages format to tuples for process_message
        history_list = []
        if chat_history:
            # Gradio 6.x uses messages format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            for i in range(0, len(chat_history), 2):
                if i + 1 < len(chat_history):
                    user_content = chat_history[i].get("content", "")
                    bot_content = chat_history[i + 1].get("content", "")
                    history_list.append((user_content, bot_content))
        
        bot_message = process_message(message, history_list)
        
        # Append new messages in Gradio 6.x format
        if chat_history is None:
            chat_history = []
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: (reset_session(), []), None, [msg, chatbot])



if __name__ == "__main__":
    logger.info("Starting ClaimFlow AI (Simple Mode)...")
    
    if not config.OPENAI_API_KEY:
        print("\n⚠️  ERROR: OPENAI_API_KEY not found!")
        print("Please create a .env file with your OpenAI API key\n")
    else:
        # Use environment variable for port, default to 7865
        port = int(os.environ.get("PORT", 7865))
        demo.launch(server_name="0.0.0.0", server_port=port)
