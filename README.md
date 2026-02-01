# 🤖 ClaimFlow AI Agent - Agentic Insurance Claims Processor

> **Transform insurance claim processing with intelligent agentic AI** - A conversational AI system that autonomously processes insurance claims end-to-end through natural dialogue and multi-step reasoning.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Hugging_Face-yellow)](https://huggingface.co/spaces/abhireds/claimflow-ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green.svg)](https://github.com/langchain-ai/langgraph)
[![GPT-4o](https://img.shields.io/badge/GPT--4o-OpenAI-orange.svg)](https://openai.com)
[![Tests](https://img.shields.io/badge/tests-31%2F31_passing-brightgreen.svg)](tests/)

---

## 🎯 What Is This?

ClaimFlow AI is an **agentic AI system** that revolutionizes insurance claim processing by combining:

- 🗣️ **Natural Conversations** - Talk to the AI like a human agent
- 🧠 **Autonomous Decision-Making** - AI independently processes claims through 9 intelligent steps
- 📚 **RAG-Powered Intelligence** - Retrieves and reasons over policy documents
- 🔍 **Fraud Detection** - Analyzes claim history and patterns
- ⚡ **Real-Time Processing** - From conversation to approval in seconds

**Try it live:** [https://huggingface.co/spaces/abhireds/claimflow-ai](https://huggingface.co/spaces/abhireds/claimflow-ai)

---

## ✨ Key Features

### 🎭 Intelligent Conversation
- **Greeting Detection** - Recognizes casual greetings and responds naturally
- **Auto Claim-Type Detection** - Identifies motor/health/home claims from description
- **Contextual Follow-ups** - Asks smart questions based on claim type
- **Empathetic Responses** - Shows understanding and support

### 🤖 Agentic AI Workflow
- **9-Step Autonomous Processing** - AI agent independently executes complex workflow
- **Dynamic Decision Making** - Adapts based on policy rules and claim data
- **Multi-Tool Orchestration** - Coordinates RAG, database, calculations, and rules
- **State Management** - Maintains context across conversation and processing

### 🔒 Enterprise-Grade
- **Vector Search (ChromaDB)** - Semantic policy document retrieval
- **Relational Database (SQLite)** - Customer, policy, and claim persistence
- **Comprehensive Testing** - 31/31 tests passing (100% coverage on core)
- **Docker Ready** - Containerized deployment with docker-compose

**Supported Insurance Types:**
- 🚗 **Motor**: Accident, Theft, Fire, Vandalism
- 🏥 **Health**: Hospitalization, Surgery, Critical Illness
- 🏠 **Home**: Fire, Theft, Flood, Earthquake, Storm

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  Gradio Chat Interface                       │
│              http://localhost:7865 (Local)                   │
│      https://huggingface.co/spaces/abhireds/claimflow-ai    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│           LangGraph Agentic AI Workflow (GPT-4o)             │
│                                                              │
│  📍 PHASE 1: CONVERSATIONAL INTELLIGENCE                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Greeting Detection & Warm Welcome              │    │
│  │  2. Claim Type Auto-Detection (Motor/Health/Home)  │    │
│  │  3. Smart Contextual Follow-up Questions           │    │
│  │  4. Information Completeness Validation            │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  🤖 PHASE 2: AUTONOMOUS 9-STEP PROCESSING                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Step 1: Extract Structured Data from Conversation│    │
│  │  Step 2: Retrieve Policy Documents (RAG) ────────┐│    │
│  │  Step 3: Validate Coverage Eligibility           ││    │
│  │  Step 4: Check Policy Exclusions                 ││    │
│  │  Step 5: Calculate Claim Amount (Auto)           ││    │
│  │  Step 6: Determine Required Documents            ││    │
│  │  Step 7: Analyze Claim History (Fraud Check) ────┼┼─┐ │
│  │  Step 8: Make Approval/Rejection Decision        ││ │ │
│  │  Step 9: Generate Detailed Claim Report          ││ │ │
│  └───────────────────────────────────────────────────┼┼─┼─┘
└──────────────────────────────────────────────────────┼┼─┼──┘
                                                       ││ │
                    ┌──────────────────────────────────┘│ │
                    │  ┌────────────────────────────────┘ │
                    ▼  ▼                                   ▼
         ┌─────────────────────┐           ┌────────────────────┐
         │   ChromaDB RAG      │           │  SQLite Database   │
         │   Vector Store      │           │   Relational DB    │
         ├─────────────────────┤           ├────────────────────┤
         │ • 10 Policy Docs    │           │ • Customers Table  │
         │ • 38 Chunks         │           │ • Policies Table   │
         │ • MiniLM Embeddings │           │ • Claims Table     │
         │ • Semantic Search   │           │ • History Tracking │
         └─────────────────────┘           └────────────────────┘
```

**Tech Stack:**  
`LangGraph 1.0+` • `GPT-4o` • `ChromaDB` • `SQLAlchemy` • `Gradio 6.5` • `Pytest` • `Docker`

---

## 🔄 The 9-Step Agentic Workflow

ClaimFlow's AI agent autonomously executes these steps **without human intervention**:

| Step | Agent Action | Intelligence Applied |
|------|--------------|---------------------|
| **1️⃣ Data Extraction** | Parse conversation into structured claim data | NLP + Entity Recognition |
| **2️⃣ Policy Retrieval** | Semantic search through policy documents | RAG + Vector Similarity |
| **3️⃣ Coverage Check** | Verify claim type matches policy coverage | Rule-Based Logic |
| **4️⃣ Exclusion Check** | Identify any policy exclusions | Pattern Matching |
| **5️⃣ Amount Calculation** | Apply deductibles, depreciation, co-pay | Mathematical Computation |
| **6️⃣ Document Verification** | List required supporting documents | Conditional Logic |
| **7️⃣ History Analysis** | Check past claims for fraud patterns | Database Query + ML |
| **8️⃣ Decision Making** | Approve/Reject/Review based on rules | Multi-Factor Analysis |
| **9️⃣ Report Generation** | Create comprehensive claim report | Structured Output |

**Each step is autonomous** - the AI agent decides what to do, retrieves information, makes decisions, and proceeds to the next step without human oversight.

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
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Initialize database (auto-creates sample data)
python scripts/init_database.py

# 6. Ingest policy documents to vector store
python scripts/ingest_policies.py

# 7. Launch the application
python ui/simple_app.py
```

Open **http://localhost:7865** and start chatting! 🎉

---

## 💬 Example Conversation

```
👤 User: hey there

🤖 Agent: Hello! I'm your ClaimFlow AI assistant. I'm here to help 
         you file your insurance claim today. To get started, could 
         you tell me what happened? For example, 'My car was damaged' 
         or 'I had a medical emergency'.

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
# Run core tests (Database + RAG)
pytest tests/test_database.py tests/test_rag.py -v

# Run all tests with coverage
pytest --cov=agent --cov=database --cov-report=html

# Quick test
python test_system.py
```

**Test Results:** ✅ **31/31 Tests Passing (100%)**
- Database Operations: 20/20
- RAG System: 11/11
- Coverage: 85%+ on core modules

---

## 🐳 Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or use Makefile
make run

# Access at http://localhost:7865
```

**Environment Variables for Docker:**
```env
OPENAI_API_KEY=your-key-here
PORT=7865
```

---

## 📁 Project Structure

```
claimflow-ai-agent/
├── agent/                    # 🤖 Agentic AI Core
│   ├── workflow.py          # LangGraph multi-phase workflow
│   ├── tools.py             # 9-step processing tools
│   ├── prompts.py           # LLM prompt engineering
│   ├── rag.py               # Vector store RAG integration
│   └── state.py             # State management schema
├── database/                 # 🗄️ Data Layer
│   ├── models.py            # SQLAlchemy ORM models
│   └── crud.py              # CRUD operations
├── data/                     # 📊 Data Storage
│   ├── policies/            # 10 insurance policy documents
│   ├── chroma_db/           # ChromaDB vector store
│   └── claimflow.db         # SQLite database (auto-generated)
├── ui/                       # 🎨 User Interface
│   ├── simple_app.py        # Gradio chat interface
│   └── gradio_app.py        # Alternative UI
├── scripts/                  # 🔧 Utilities
│   ├── init_database.py     # Database initialization
│   ├── ingest_policies.py   # Vector store setup
│   └── test_*.py            # Integration tests
├── tests/                    # ✅ Test Suite
│   ├── test_database.py     # DB tests (20 tests)
│   ├── test_rag.py          # RAG tests (11 tests)
│   ├── test_workflow.py     # Workflow tests
│   └── conftest.py          # Pytest fixtures
├── docs/                     # 📚 Documentation
│   ├── DOCKER.md            # Container deployment
│   ├── RAG_DOCUMENTATION.md # Vector store details
│   └── TESTING.md           # Test guide
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
└── docker-compose.yml       # Multi-container setup
```

---

## 🌐 Live Demo

**Try ClaimFlow AI on Hugging Face Spaces:**

🔗 **https://huggingface.co/spaces/abhireds/claimflow-ai**

- No installation required
- Free to use
- Powered by GPT-4o
- Deployed on HF's infrastructure

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [Docker Guide](docs/DOCKER.md) | Container deployment |
| [RAG System](docs/RAG_DOCUMENTATION.md) | Vector store architecture |
| [Testing](docs/TESTING.md) | Test suite details |
| [Project Summary](PROJECT_SUMMARY.md) | Complete implementation |
| [HF Deployment](HUGGINGFACE_DEPLOYMENT.md) | Spaces deployment guide |

---

## 🛠️ Configuration

**`.env` File:**
```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Settings
MAX_CONVERSATION_TURNS=10
LOG_LEVEL=INFO

# Optional
INSURANCE_RAG_URL=http://localhost:8000
```

**Model Settings (`config.py`):**
```python
MODEL_NAME = "gpt-4o"
MODEL_TEMPERATURE = 0.7
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Add more insurance types (travel, life, etc.)
- [ ] Multi-language support
- [ ] Voice interface integration
- [ ] Enhanced fraud detection ML models
- [ ] Real-time policy API integration

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 👨‍💻 Author

**Abhishyant Reddy**

- 🌐 GitHub: [@AbhishyantReds](https://github.com/AbhishyantReds)
- 🤗 Hugging Face: [@abhireds](https://huggingface.co/abhireds)
- 📧 Project: ClaimFlow AI Agent
- 🛠️ Built with: LangGraph • GPT-4o • ChromaDB • Python
- 📅 Date: February 2026

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ using Agentic AI

[Live Demo](https://huggingface.co/spaces/abhireds/claimflow-ai) • [Documentation](docs/) • [Report Bug](https://github.com/AbhishyantReds/claimflow-ai-agent/issues)

</div>





