# 🤖 ClaimFlow AI - Intelligent Insurance Claims Processor

> Transform insurance claim processing with conversational AI and autonomous agents - Process insurance claims end-to-end through natural dialogue, powered by LangGraph, GPT-4o, and dual-database architecture.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Hugging_Face-yellow)](https://huggingface.co/spaces/abhireds/claimflow-ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-2.0+-green.svg)](https://github.com/langchain-ai/langgraph)
[![GPT-4o](https://img.shields.io/badge/GPT--4o-OpenAI-orange.svg)](https://openai.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-purple.svg)](https://www.trychroma.com/)
[![Tests](https://img.shields.io/badge/tests-31%2F31_passing-brightgreen.svg)](tests/)

---

## 🎯 Overview

ClaimFlow AI is an intelligent conversational AI agent that processes insurance claims through natural dialogue. It combines deterministic conversation intake with autonomous agentic processing to deliver instant claim decisions.

**Key Capabilities:**
- 🗣️ Natural language claim submission via chat interface
- 🤖 9 autonomous tools orchestrated by LangGraph agent
- 📚 Dual database architecture (ChromaDB vector store + SQLite relational DB)
- ⚡ Real-time claim processing with instant approval/denial
- 🔍 Fraud detection through historical claim analysis
- 📊 Comprehensive claim reports with detailed breakdowns

**Supported Insurance Types:**
- 🚗 **Motor**: Accident, Theft, Fire, Vandalism
- 🏥 **Health**: Hospitalization, Surgery, Critical Illness  
- 🏠 **Home**: Fire, Theft, Flood, Earthquake, Storm

**Live Demo:** [https://huggingface.co/spaces/abhireds/claimflow-ai](https://huggingface.co/spaces/abhireds/claimflow-ai)

---

## ✨ Features

### Intelligent Conversation Flow
- **Auto-Detection**: Automatically identifies claim type from natural language
- **Contextual Questions**: Asks relevant follow-ups based on claim category
- **Greeting Recognition**: Handles casual greetings naturally
- **Empathetic Responses**: Shows understanding and support throughout the conversation
- **Turn Limiting**: 10-turn maximum to prevent infinite loops

### Autonomous Agent Processing
- **Hybrid Architecture**: Two-phase approach (Conversation → Processing)
- **9 Specialized Tools**: Each tool handles specific claim processing tasks
- **Dependency Management**: Tools validate prerequisites before execution
- **Parallel Execution**: Independent operations run concurrently for speed
- **ReAct Reasoning**: Agent thinks, acts, and observes in a loop
- **Complete Audit Trail**: Full transparency with execution logs

### Enterprise-Grade Infrastructure
- **Vector Database**: ChromaDB for semantic policy document retrieval
- **Relational Database**: SQLite with SQLAlchemy 2.0 ORM
- **State Persistence**: LangGraph checkpointing for conversation continuity
- **Comprehensive Testing**: 31/31 tests passing (100% coverage on core modules)
- **Docker Ready**: Containerized with docker-compose for easy deployment
- **Production Tested**: Deployed on Hugging Face Spaces

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│              Gradio Chat Interface (UI)                    │
│          http://localhost:7865 (Local)                     │
│   https://huggingface.co/spaces/abhireds/claimflow-ai     │
└─────────────────────┬──────────────────────────────────────┘
                      │ User Message
                      ▼
┌────────────────────────────────────────────────────────────┐
│         LangGraph StateGraph Workflow (GPT-4o)             │
│                                                            │
│  ══════════════════════════════════════════════════════  │
│  📍 PHASE 1: CONVERSATIONAL INTAKE                        │
│  ══════════════════════════════════════════════════════  │
│                                                            │
│    ┌─────────┐       ┌──────────────┐                    │
│ ┌─→│ Intake  │──────→│ Complete?    │                    │
│ │  │  Node   │       │  (Check)     │                    │
│ │  └─────────┘       └───┬──────────┘                    │
│ │                        │                                │
│ │              ┌─────────┴─────────┐                     │
│ │              │                   │                      │
│ │         [continue]          [process]                   │
│ │              │                   │                      │
│ │              ▼                   │                      │
│ │      ┌──────────────┐            │                      │
│ └──────│ Ask Question │            │                      │
│  (loop)│     Node     │            │                      │
│        └──────────────┘            │                      │
│               │                    │                      │
│          [END - wait]              │                      │
│                                    │                      │
│  ══════════════════════════════════════════════════════  │
│  🤖 PHASE 2: AUTONOMOUS PROCESSING                        │
│  ══════════════════════════════════════════════════════  │
│                                    │                      │
│                                    ▼                      │
│               ┌──────────────────────────┐               │
│               │    Agent Node (LLM)      │               │
│               │  • Analyzes state        │               │
│               │  • Selects tools         │               │
│               │  • Generates arguments   │               │
│               └──────┬───────────────────┘               │
│                      │                                    │
│             ┌────────┴────────┐                          │
│             │                 │                           │
│      [call tools]      [finalize]                         │
│             │                 │                           │
│             ▼                 ▼                           │
│     ┌──────────────┐  ┌────────────┐                    │
│     │ Tool Executor│  │  Finalize  │                    │
│  ┌──│  (9 Tools)   │  │    Node    │                    │
│  │  └──────┬───────┘  └─────┬──────┘                    │
│  │         │                 │                            │
│  └─────────┘                 ▼                            │
│    (loop)                  [END]                          │
│                                                            │
└────────────────────────────────────────────────────────────┘
           │                           │
           │ (Tools access databases)  │
           ▼                           ▼
┌──────────────────┐       ┌────────────────────────┐
│ ChromaDB (RAG)   │       │  SQLite + SQLAlchemy   │
│ Vector Database  │       │  Relational Database   │
├──────────────────┤       ├────────────────────────┤
│ • 10 Policy Docs │       │ • Customers (3 rows)   │
│ • 38 Chunks      │       │ • Policies (5 rows)    │
│ • MiniLM-L6-v2   │       │ • Claims (history)     │
│ • Persistent     │       │ • Relationships (FKs)  │
│ • Semantic Search│       │ • Enums & Validations  │
└──────────────────┘       └────────────────────────┘
```

**Tech Stack:** LangGraph 2.0+ • LangChain 0.3+ • GPT-4o • ChromaDB 0.4+ • SQLAlchemy 2.0 • sentence-transformers • Gradio 6.5 • Docker

---

## 🔧 The 9 Autonomous Tools

ClaimFlow's agent intelligently orchestrates **9 specialized tools**:

| # | Tool | Function | Dependencies | Data Source |
|---|------|----------|--------------|-------------|
| 1️⃣ | **extract_claim_data** | Normalize & structure conversation data | None (runs first) | Conversation state |
| 2️⃣ | **retrieve_policy** | Fetch policy details by identifier | None (parallel) | SQLite → ChromaDB |
| 3️⃣ | **check_coverage** | Verify claim type is covered | retrieve_policy | RAG + Rules |
| 4️⃣ | **check_exclusions** | Check policy exclusions | extract_claim_data + retrieve_policy | JSON rules |
| 5️⃣ | **calculate_payout** | Compute payable amount | check_coverage | Depreciation rules |
| 6️⃣ | **verify_documents** | List required documents | extract_claim_data | document_rules.json |
| 7️⃣ | **check_claim_history** | Review past claims & fraud | None (parallel) | SQLite database |
| 8️⃣ | **make_decision** | Approve/Deny/Review decision | ALL tools 1-7 | business_rules.json |
| 9️⃣ | **generate_report** | Create comprehensive report | make_decision (last) | All previous results |

**Tool Features:**
- 🔄 Dependency validation before execution
- ⚡ Parallel execution for independent operations  
- 📊 Complete audit trail with timing metrics
- ⛓️ Graceful error handling and fallbacks
- 🎯 LLM autonomously decides execution order

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Installation (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/AbhishyantReds/claimflow-ai-agent.git
cd claimflow-ai-agent

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create .env file and add:
# OPENAI_API_KEY=your-api-key-here

# 5. Initialize database (auto-creates sample data)
python scripts/init_database.py

# 6. Ingest policy documents to vector store
python scripts/ingest_policies.py

# 7. Launch the application
python app.py
```

**🎉 Open http://localhost:7865 and start chatting!**

---

## 💬 Example Conversation

```
👤 User: hey there

🤖 Agent: Hello! I'm your ClaimFlow AI assistant. I'm here to help 
         you file your insurance claim. To get started, could you 
         tell me what happened?

👤 User: my car got damaged in an accident

🤖 Agent: I'm sorry to hear about your accident. Can you describe 
         what damage occurred to your vehicle?

👤 User: front bumper is completely damaged, happened in a parking lot

🤖 Agent: Thank you for that information. To proceed with your motor 
         claim, I'll need your vehicle registration number.

👤 User: TS 09 EF 5678

🤖 Agent: Got it. Do you have an estimate for the repair cost?

👤 User: around 45000 rupees

🤖 Agent: Perfect! I have all the information I need. Let me process 
         your claim now...

         ⚙️ Processing your claim through 9 autonomous steps...

         ✅ CLAIM PROCESSED SUCCESSFULLY

         📋 Claim Report:
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         Claim ID: CLM-2026-001234
         Type: Motor Accident
         Status: ✅ APPROVED
         
         💰 Financial Summary:
         • Claimed Amount: ₹45,000
         • Deductible: ₹3,000
         • Depreciation: ₹2,000
         • Payable Amount: ₹40,000
         
         📄 Required Documents:
         • Vehicle Registration Certificate
         • Driving License
         • FIR Copy (if applicable)
         • Repair Estimate
         • Damage Photos
         
         ⏱️ Next Steps:
         Upload documents at: [portal link]
         Expected payout: 5-7 business days
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_database.py -v
pytest tests/test_rag.py -v
pytest tests/test_workflow.py -v

# Run with coverage
pytest --cov=agent --cov=database --cov-report=html

# Quick system test
python test_system.py
```

**Test Results:** ✅ **31/31 Tests Passing**
- Database Operations: 20/20 ✅
- RAG System: 11/11 ✅
- Coverage: 85%+ on core modules

---

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Access at http://localhost:7865
```

### Using Makefile

```bash
# Build image
make build

# Run container
make run

# Run tests in container
make test

# Interactive shell
make shell

# Clean up
make clean
```

### Environment Variables

Create a `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
PORT=7865
MAX_CONVERSATION_TURNS=10
LOG_LEVEL=INFO
```

---

## 📁 Project Structure

```
claimflow-ai/
├── agent/                    # 🤖 Agentic AI Core
│   ├── workflow_agent.py    # Hybrid LangGraph workflow (MAIN)
│   ├── workflow.py          # Alternative linear workflow
│   ├── tools_agent.py       # 9 tools with @tool decorator
│   ├── tools.py             # Legacy tool implementations
│   ├── prompts.py           # LLM prompt engineering
│   ├── rag.py               # ChromaDB vector store & RAG
│   └── state.py             # TypedDict state schema
│
├── database/                 # 🗄️ Data Layer
│   ├── models.py            # SQLAlchemy ORM models
│   └── crud.py              # CRUD operations
│
├── data/                     # 📊 Data Storage
│   ├── policies/            # 10 insurance policy documents
│   ├── chroma_db/           # ChromaDB vector store (persistent)
│   ├── claimflow.db         # SQLite database (auto-generated)
│   ├── business_rules.json  # Decision rules
│   ├── document_rules.json  # Document requirements
│   ├── repair_costs.json    # Repair cost estimates
│   └── claims_history.json  # Historical claims data
│
├── ui/                       # 🎨 User Interface
│   ├── simple_app.py        # Main Gradio chat interface
│   └── gradio_app.py        # Alternative UI with more features
│
├── api/                      # 🌐 REST API
│   ├── main.py              # FastAPI application
│   └── models.py            # Pydantic models for API
│
├── scripts/                  # 🔧 Utilities
│   ├── init_database.py     # Database initialization
│   ├── ingest_policies.py   # Vector store setup
│   ├── test_rag.py          # RAG system testing
│   └── test_database_integration.py  # Integration tests
│
├── tests/                    # ✅ Test Suite
│   ├── test_database.py     # Database tests (20 tests)
│   ├── test_rag.py          # RAG tests (11 tests)
│   ├── test_workflow.py     # Workflow tests
│   ├── test_tools.py        # Tool tests
│   └── conftest.py          # Pytest fixtures
│
├── docs/                     # 📚 Documentation
│   ├── DOCKER.md            # Container deployment guide
│   ├── RAG_DOCUMENTATION.md # Vector store architecture
│   ├── TESTING.md           # Test suite guide
│   └── TEST_RESULTS.md      # Test execution logs
│
├── app.py                    # 🚀 Main entry point (HF Spaces)
├── config.py                 # ⚙️ Configuration settings
├── requirements.txt          # 📦 Python dependencies
├── Dockerfile                # 🐳 Container definition
├── docker-compose.yml        # 🐳 Multi-container setup
├── docker-entrypoint.sh      # 🐳 Container entrypoint
├── Makefile                  # 🛠️ Build automation
└── .env.example             # 📝 Environment template
```

---

## 🛠️ Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
MAX_CONVERSATION_TURNS=10
LOG_LEVEL=INFO
PORT=7865
INSURANCE_RAG_URL=http://localhost:8000
```

### Model Configuration

Edit `config.py`:

```python
# Conversation LLM (creative for dialogue)
MODEL_NAME = "gpt-4o"
MODEL_TEMPERATURE = 0.7

# Agent LLM (deterministic for processing)
# Uses temperature=0.1 with tools bound

# Database paths
DATABASE_URL = "sqlite:///data/claimflow.db"
CHROMA_DB_PATH = "data/chroma_db"
```

---

## 🌐 Live Demo

**Try ClaimFlow AI on Hugging Face Spaces:**

🔗 **[https://huggingface.co/spaces/abhireds/claimflow-ai](https://huggingface.co/spaces/abhireds/claimflow-ai)**

- No installation required
- Free to use
- Powered by GPT-4o
- Deployed on Hugging Face infrastructure

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [RAG System](docs/RAG_DOCUMENTATION.md) | Vector store architecture and RAG implementation |
| [Docker Guide](docs/DOCKER.md) | Complete container deployment guide |
| [Testing Guide](docs/TESTING.md) | Test suite details and coverage reports |
| [Test Results](docs/TEST_RESULTS.md) | Execution logs and test outputs |
| [HF Deployment](HUGGINGFACE_DEPLOYMENT.md) | Hugging Face Spaces deployment guide |

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more insurance types (travel, life, pet insurance)
- [ ] Multi-language support (Hindi, Spanish, etc.)
- [ ] Voice interface integration  
- [ ] Enhanced fraud detection with ML models
- [ ] Real-time policy API integration
- [ ] Mobile app development
- [ ] Advanced analytics dashboard

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👨‍💻 Author

**Abhishyant Reddy**

📧 Email: abhireds22@gmail.com  
🌐 GitHub: [@AbhishyantReds](https://github.com/AbhishyantReds)  
🤗 Hugging Face: [@abhireds](https://huggingface.co/abhireds)

For doubts, improvements, or collaboration opportunities, feel free to reach out!

---

## 🙏 Acknowledgments

Built with:
- **LangGraph 2.0+** - Agentic workflow orchestration
- **LangChain 0.3+** - LLM application framework
- **OpenAI GPT-4o** - Language model
- **ChromaDB 0.4+** - Vector database
- **SQLAlchemy 2.0** - SQL toolkit and ORM
- **Gradio 6.5** - Web UI framework
- **sentence-transformers** - Embedding models
- **Docker** - Containerization

---

<div align="center">

**⭐ Star this repo if you find it useful!**

**Made with ❤️ using Agentic AI**

[Live Demo](https://huggingface.co/spaces/abhireds/claimflow-ai) • [Documentation](docs/) • [Report Bug](https://github.com/AbhishyantReds/claimflow-ai-agent/issues) • [Request Feature](https://github.com/AbhishyantReds/claimflow-ai-agent/issues)

</div>
