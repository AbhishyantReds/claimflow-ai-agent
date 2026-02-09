"""
Gradio Chat Interface for ClaimFlow AI
Provides conversational UI for insurance claim submission

Updated to use hybrid agent workflow.
"""
import gradio as gr
import logging
import time
from langchain_core.messages import HumanMessage
from agent.workflow_agent import graph, get_reasoning_trace, get_processing_summary
from agent.state import create_initial_state
import config

logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def chat(message: str, history: list, session_id: str = "default"):
    """
    Process a chat message through the LangGraph workflow.
    
    Args:
        message: User's message
        history: Gradio chat history (list of {"role": str, "content": str} dicts) - Gradio 6.x format
        session_id: Session identifier for checkpointing
        
    Yields:
        Updated history with bot responses in Gradio 6.x dict format
    """
    try:
        # Config for LangGraph checkpointing
        config_dict = {"configurable": {"thread_id": session_id}}
        
        # For first message, initialize state using the new factory function
        if not history:
            initial_state = create_initial_state(session_id)
            initial_state["messages"] = [HumanMessage(content=message)]
            
            logger.info(f"Starting new conversation: {message[:50]}...")
            
            # Stream the workflow execution
            events = []
            for event in graph.stream(initial_state, config_dict, stream_mode="values"):
                events.append(event)
        else:
            # Continue existing conversation - just send the new message
            input_state = {
                "messages": [HumanMessage(content=message)]
            }
            
            logger.info(f"Processing message: {message[:50]}...")
            
            # Stream the workflow execution
            events = []
            for event in graph.stream(input_state, config_dict, stream_mode="values"):
                events.append(event)
        
        # Get final state
        final_state = events[-1] if events else {}
        
        # Extract bot responses from messages
        messages = final_state.get("messages", [])
        
        # Get only new messages (after the user's latest message)
        new_messages = []
        found_user_message = False
        
        for msg in reversed(messages):
            if hasattr(msg, 'content'):
                if isinstance(msg, HumanMessage):
                    if msg.content == message and not found_user_message:
                        found_user_message = True
                        break
                else:
                    # AI message
                    new_messages.insert(0, msg.content)
        
        # Build history in Gradio 6.x format (list of {"role": ..., "content": ...} dicts)
        current_history = list(history) if history else []
        
        # Add user message first
        current_history.append({"role": "user", "content": message})
        
        if new_messages:
            # For processing steps, yield them one by one with delay for visual effect
            for bot_msg in new_messages:
                current_history.append({"role": "assistant", "content": bot_msg})
                yield current_history
                
                # Small delay for step-by-step visualization during processing
                if "Step" in bot_msg:
                    time.sleep(0.3)
        else:
            # Fallback if no response
            current_history.append({"role": "assistant", "content": "I'm processing your request..."})
            yield current_history
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        error_msg = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try again or rephrase your message."
        current_history = list(history) if history else []
        current_history.append({"role": "user", "content": message})
        current_history.append({"role": "assistant", "content": error_msg})
        yield current_history


def create_ui():
    """
    Creates and returns the Gradio interface.
    """
    
    # Example scenarios
    examples = [
        ["Hi, my car got damaged in a parking lot yesterday"],
        ["I need to file a claim for my car. Front bumper is damaged"],
        ["My vehicle was hit while parked. Need insurance help"],
    ]
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .message.bot {
        background-color: #f0f0f0 !important;
    }
    """
    
    with gr.Blocks(title="ClaimFlow AI - Insurance Claims Assistant") as demo:
        gr.Markdown(
            """
            # 🛡️ ClaimFlow AI - Insurance Claims Assistant
            
            Welcome! I'm your AI assistant for processing insurance claims. Just tell me what happened,
            and I'll guide you through the process step by step.
            
            **I can help with:**
            - Motor vehicle claims (accidents, theft, fire)
            - Home insurance claims (fire, theft, damage)
            - Policy verification and coverage checks
            
            Start by describing your situation in simple terms!
            """
        )
        
        # Session state
        session_id = gr.State(value=lambda: f"session_{int(time.time())}")
        
        # Chat interface
        chatbot = gr.Chatbot(
            height=500,
            placeholder="Start chatting by typing below...",
            label="Conversation",
            show_label=True
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Type your message here... (e.g., 'My car was damaged')",
                label="Your Message",
                scale=4,
                show_label=False
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("🔄 Clear & Start New Claim", variant="secondary")
        
        gr.Markdown("### 💡 Example Scenarios")
        gr.Examples(
            examples=examples,
            inputs=msg_input,
            label="Click an example to try:"
        )
        
        gr.Markdown(
            """
            ---
            ### How it works:
            1. **Tell me what happened** - Describe your claim in simple terms
            2. **Answer my questions** - I'll ask for specific details I need
            3. **Autonomous processing** - Once I have all info, I'll process your claim through 9 steps
            4. **Get your report** - Receive instant decision and detailed breakdown
            
            ### Features:
            - ✅ Real-time conversational assistance
            - ✅ Automatic policy verification via RAG system
            - ✅ Instant approval/denial decisions
            - ✅ Detailed claim reports
            - ✅ Step-by-step processing visibility
            """
        )
        
        # Event handlers
        def submit_message(message, history, session):
            """Handle message submission"""
            if not message.strip():
                return history, ""
            
            # Stream responses
            for updated_history in chat(message, history, session):
                yield updated_history, ""
        
        def clear_chat():
            """Clear chat and start new session"""
            new_session = f"session_{int(time.time())}"
            return [], new_session  # Empty list works for both formats
        
        # Wire up events
        submit_btn.click(
            submit_message,
            inputs=[msg_input, chatbot, session_id],
            outputs=[chatbot, msg_input],
        )
        
        msg_input.submit(
            submit_message,
            inputs=[msg_input, chatbot, session_id],
            outputs=[chatbot, msg_input],
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, session_id]
        )
    
    return demo


def main():
    """Launch the Gradio application"""
    logger.info("Starting ClaimFlow AI Gradio Interface...")
    
    # Check configuration
    if not config.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set in .env file!")
        print("\n⚠️  ERROR: OPENAI_API_KEY not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("  OPENAI_API_KEY=your_key_here\n")
        return
    
    demo = create_ui()
    
    # Launch
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
