# ClaimFlow AI - Autonomous Insurance Claims Processor

An intelligent conversational AI agent that processes insurance claims end-to-end through natural dialogue. Built with LangGraph, ChromaDB, and GPT-4o.

## Features

- **Conversational Interface**: Natural chat-based claim submission
- **Auto-detection**: Automatically identifies claim type (motor/health/home)
- **RAG Integration**: Semantic policy retrieval using ChromaDB vector store
- **Database Layer**: SQLite for customers, policies, and claim history
- **Autonomous Processing**: 9-step automated evaluation pipeline
- **Multi-turn Dialogue**: Smart follow-up questions for complete information
- **Docker Ready**: Containerized deployment

**Supported Claims**: Motor (accident, theft, fire), Health (hospitalization, surgery), Home (fire, theft, flood)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│              User Interface (Gradio)                │
│              http://localhost:7865                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         LangGraph Agent Workflow (GPT-4o)           │
│                                                     │
│  Phase 1: Conversation (Multi-turn)                │
│  ├─ Greeting Detection                             │
│  ├─ Claim Type Auto-detection                      │
│  └─ Smart Follow-up Questions                      │
│                                                     │
│  Phase 2: Processing (9 Autonomous Steps)          │
│  1. Extract Claim Data                             │
│  2. Retrieve Policy (RAG) ─────┐                   │
│  3. Check Coverage (RAG) ──────┤                   │
│  4. Check Exclusions           │                   │
│  5. Calculate Payout           │                   │
│  6. Verify Documents           │                   │
│  7. Check History ─────────────┼────┐              │
│  8. Make Decision              │    │              │
│  9. Generate Report            │    │              │
└────────────────────────────────┼────┼──────────────┘
                                 │    │
                    ┌────────────┘    └────────────┐
                    ▼                              ▼
         ┌──────────────────┐         ┌─────────────────┐
         │   ChromaDB RAG   │         │ SQLite Database │
         │  (Vector Store)  │         │  (Relational)   │
         │                  │         │                 │
         │ • 10 Policies    │         │ • Customers     │
         │ • 38 Chunks      │         │ • Policies      │
         │ • Embeddings     │         │ • Claims        │
         │ • Semantic Search│         │ • History       │
         └──────────────────┘         └─────────────────┘
```

**Tech Stack**: LangGraph 1.0+ | GPT-4o | ChromaDB | SQLAlchemy | Gradio | FastAPI | Pytest | Docker

## Workflow

### Phase 1: Conversational Gathering
1. User starts conversation (greeting detection)
2. Agent auto-detects claim type from description
3. Agent asks smart follow-up questions
4. Conversation continues until sufficient info gathered

### Phase 2: Autonomous Processing
1. **Extract Data**: Parse claim details from conversation
2. **Retrieve Policy**: Search vector store for policy info
3. **Check Coverage**: Verify claim type is covered
4. **Check Exclusions**: Ensure no exclusions apply
5. **Calculate Payout**: Apply deductibles, depreciation, co-pay
6. **Verify Documents**: List required documentation
7. **Check History**: Review customer's past claims (fraud risk)
8. **Make Decision**: Approve/Reject/Review based on rules
9. **Generate Report**: Create detailed claim report

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Setup (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/abhishyantreddy/claimflow-ai.git
cd claimflow-ai

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your-key-here

# 5. Initialize database
python scripts/init_database.py

# 6. Ingest policies to vector store
python scripts/ingest_policies.py

# 7. Run application
python ui/simple_app.py
```

Open http://localhost:7865 and start chatting!

### Docker Deployment

```bash
# Build and run
docker-compose up --build

# Or using Makefile
make run
```

## Usage

### Chat Interface

```bash
# Activate environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run Gradio UI
python ui/simple_app.py
```

Browser opens at http://localhost:7860

### Example Conversation

```
User: Hi, my car got damaged in an accident

Agent: I'm sorry to hear that. Could you tell me what type 
       of damage occurred?

User: Front bumper is damaged, happened in parking lot

Agent: I understand. To process your claim, I'll need your 
       vehicle registration number.

User: TS 09 EF 5678

Agent: Thank you! Do you have a repair estimate?

User: Around 45000 rupees

Agent: Perfect! Processing your claim now...

[9-step autonomous processing...]

✅ CLAIM APPROVED
Claim ID: CLM-2026-001234
Payable Amount: ₹40,000 (after deductible & depreciation)
Status: Pending documentation
```

## Testing

```bash
# Run core tests (Database + RAG)
pytest tests/test_database.py tests/test_rag.py -v

# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=agent --cov=database --cov-report=html
```

**Test Results**: 31/31 core tests passing (100%)
- Database: 20/20 ✅
- RAG: 11/11 ✅

## Project Structure

```
claimflow-ai/
├── agent/              # LangGraph agent
│   ├── workflow.py     # Main workflow graph
│   ├── tools.py        # 9 processing steps
│   ├── prompts.py      # LLM prompts
│   ├── rag.py          # Vector store integration
│   └── state.py        # State management
├── database/           # SQLAlchemy ORM
│   ├── models.py       # Customer, Policy, Claim tables
│   └── crud.py         # Database operations
├── data/               # Data storage
│   ├── policies/       # 10 policy documents
│   ├── chroma_db/      # Vector store
│   └── claimflow.db    # SQLite database
├── ui/                 # User interfaces
│   └── simple_app.py   # Gradio chat
├── tests/              # Test suite
├── scripts/            # Utility scripts
├── docs/               # Documentation
└── requirements.txt    # Dependencies
```

## Configuration

**Environment Variables** (`.env` file):
```env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o
TEMPERATURE=0.7
DATABASE_URL=sqlite:///./data/claimflow.db
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

## Documentation

- [Docker Deployment](docs/DOCKER.md) - Container setup and deployment
- [RAG System](docs/RAG_DOCUMENTATION.md) - Vector store details
- [Testing Guide](docs/TESTING.md) - Test suite documentation
- [Project Summary](PROJECT_SUMMARY.md) - Complete implementation details

## Author

**Abhishyant Reddy**

- GitHub: [@abhishyantreddy](https://github.com/abhishyantreddy)
- Project: ClaimFlow AI - Autonomous Insurance Claims Processor
- Built with: LangGraph, GPT-4o, ChromaDB, SQLAlchemy
- Date: February 2026

---

**License**: MIT  
**Status**: Production Ready ✅




