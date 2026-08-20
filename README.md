# NIRNAYA

> **AI-Based Personalized Financial Decision & Digital Fraud-Awareness Assistant**

Nirnaya is a multimodal, agent-assisted personal financial risk and decision-support system. It acts as a **second opinion at the moment of a financial decision** — detecting fraud, explaining evidence, creating an intelligent pause, and helping users make better choices.

## Architecture

```
User Input → LangGraph Orchestrator → [Regex Rules + ML Classifier + Semantic Search + RAG] → Risk Fusion → LLM Explanation → Response
```

**Core Principle:** Deterministic systems first. AI for reasoning, not decisions.

## Tech Stack

- **Backend:** FastAPI (Python 3.11) + SQLAlchemy + Pydantic v2
- **Orchestration:** LangGraph (agentic workflow)
- **LLM:** Google Gemini (via LangChain)
- **ML:** scikit-learn (TF-IDF + LogReg), sentence-transformers, FAISS
- **RAG:** LangChain + FAISS over RBI guidelines & cybercrime FAQs
- **Frontend:** Next.js + TypeScript (in progress)

## Quick Start

```bash
# Backend
cd backend
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload

# API Docs
open http://localhost:8000/docs
```

## Features

- 🔍 **16-Rule Fraud Signal Detection** — Regex-based pattern matching for urgency, OTP requests, credential phishing, etc.
- 🤖 **ML Text Classifier** — TF-IDF + Logistic Regression for scam probability scoring
- 🧠 **Semantic Scam Matching** — FAISS vector search against known scam patterns
- 📚 **RAG Knowledge Base** — Grounded retrieval from RBI guidelines and cybercrime FAQs
- ⚙️ **LangGraph Orchestration** — Graph-based pipeline: Evidence → Score → Explain
- 📊 **Risk Fusion Engine** — Weighted multi-signal fusion (Rules 40% + ML 40% + Semantic 20%)
- 💡 **LLM Explanations** — Gemini generates evidence-based, user-friendly explanations
- 💰 **Transaction Analysis** — Spending categorization, budget tracking, anomaly detection

## Project Structure

```
nirnaya/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── ml/           # ML models & training
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── data/             # Knowledge base
│   └── tests/            # Test suites
├── frontend/             # Next.js (in progress)
└── docs/                 # Documentation
```

## Documentation

See [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) for full architecture, evaluation results, and future scope.

## License

MIT
