# ClaimFlow AI - Quick Start Guide

## 🚀 Getting Started

### 1. Configure Environment

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
INSURANCE_RAG_URL=http://localhost:8000
```

### 2. Verify Installation

Check that all dependencies are installed:

```bash
pip list | findstr "langchain langgraph gradio fastapi"
```

### 3. Run the Application

#### Option A: Gradio Chat Interface (Recommended)

```bash
python ui/gradio_app.py
```

Then open: http://localhost:7860

#### Option B: FastAPI Backend

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

API docs at: http://localhost:8001/docs

### 4. Test the System

Run tests to verify everything works:

```bash
python tests/test_workflow.py
```

Or with pytest:

```bash
pytest tests/ -v
```

## 📝 Example Usage

### Chat Interface

1. Open http://localhost:7860
2. Start conversation: "Hi, my car got damaged"
3. Answer questions: "Front bumper damaged in parking lot"
4. Provide details: "TS 09 EF 5678"
5. Give estimate: "Around 45000"
6. Watch autonomous processing (9 steps)
7. Get instant decision and report!

### API Usage

```bash
# Health check
curl http://localhost:8001/health

# Chat endpoint
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My car was damaged", "session_id": "test123"}'

# Get session status
curl http://localhost:8001/agent/session/test123
```

## 🎯 Features

- ✅ **Conversational Interface** - Natural dialogue, not forms
- ✅ **10-turn limit** - Prevents infinite loops
- ✅ **Off-topic detection** - Redirects users back to claim
- ✅ **Step-by-step progress** - Visual updates during processing
- ✅ **9-step autonomous processing**:
  1. Extract claim data
  2. Retrieve policy (RAG)
  3. Check coverage (RAG)
  4. Check exclusions
  5. Calculate payout
  6. Verify documents
  7. Check claim history
  8. Make decision
  9. Generate report
- ✅ **Instant decisions** - APPROVED/DENIED/REVIEW
- ✅ **Detailed reports** - Complete breakdown

## 🔧 Troubleshooting

### "OPENAI_API_KEY not found"
- Edit `.env` file and add your actual API key
- Make sure `.env` is in the root directory

### "RAG unavailable"
- The Insurance RAG system should run on http://localhost:8000
- System works without RAG (uses fallback mock data)

### Import errors
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

### Port already in use
- Change port in code or stop other services
- Gradio: Edit `ui/gradio_app.py` (line with `server_port=7860`)
- FastAPI: Use `uvicorn api.main:app --port 8002`

## 📂 Project Structure

```
claimflow-ai/
├── agent/              # LangGraph workflow
│   ├── workflow.py     # Main graph definition
│   ├── tools.py        # 9 processing tools
│   ├── prompts.py      # LLM prompts
│   └── state.py        # State management
├── data/               # Mock data
│   ├── claims_history.json
│   ├── repair_costs.json
│   ├── business_rules.json
│   └── document_rules.json
├── api/                # FastAPI backend
│   ├── main.py         # REST endpoints
│   └── models.py       # Pydantic models
├── ui/                 # Gradio frontend
│   └── gradio_app.py   # Chat interface
├── tests/              # Test suite
│   └── test_workflow.py
├── config.py           # Configuration
├── .env                # Environment variables
└── requirements.txt    # Dependencies
```

## 🎬 Example Conversations

### Approved Claim
```
User: Hi my car got damaged
Bot: I'm sorry to hear that. Can you tell me what type of damage occurred?
User: Front bumper damaged in parking lot
Bot: What is your vehicle registration number?
User: TS 09 EF 5678
Bot: Do you have a repair estimate?
User: 45000
Bot: Thank you! Processing your claim now...
[9 steps execute autonomously]
Bot: [Detailed report with APPROVED status, ₹43,000 payable]
```

### Need More Info
```
User: I need insurance help
Bot: I can help you file a claim. What type of damage occurred?
User: Car damage
Bot: Can you describe the damage in more detail?
...
```

## 💡 Tips

1. **Be specific** - "Front bumper damaged" is better than "damage"
2. **Provide vehicle reg** - Format: "TS 09 EF 5678"
3. **Include estimate** - Amount in rupees
4. **Natural language** - Talk normally, don't use forms
5. **Off-topic?** - Bot will redirect you back

## 🛠️ Development

### Add new claim types
Edit: `data/document_rules.json` and `data/business_rules.json`

### Modify decision logic
Edit: `agent/tools.py` → `make_decision()` function

### Change conversation flow
Edit: `agent/workflow.py` → `check_completeness()` function

### Customize prompts
Edit: `agent/prompts.py`

## 📊 Monitoring

Check logs in console for:
- Step-by-step processing
- Error messages
- Decision reasoning
- API calls to RAG system

## 🎉 You're Ready!

Start with: `python ui/gradio_app.py`

Enjoy using ClaimFlow AI! 🚀
