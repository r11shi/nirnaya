# NIRNAYA — AI-Based Personalized Financial Decision & Digital Fraud-Awareness Assistant

> **SIH Problem Statement**: AI-Based Personalized Financial Decision and Digital Fraud-Awareness Assistant  
> **Team Repository**: [github.com/r11shi/nirnaya](https://github.com/r11shi/nirnaya)

---

## 1. Executive Summary

Nirnaya is a multimodal, agent-assisted personal financial risk and decision-support system. It acts as a **"second opinion" at the moment of a financial decision** — detecting fraud risk, explaining evidence, creating an intelligent pause, and helping users make better financial choices.

**Core Loop:**
```
Problem → Measurement → Intelligence/Algorithm → Action → Measurable Improvement
```

The LLM is **not** the source of truth for fraud decisions. Instead:
> VLM/OCR for perception → Tools for verification → ML/Risk engine for scoring → Policy engine for action → LLM for reasoning/explanation

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                    │
│         Chat UI · Dashboard · Risk Visualizations        │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                  BACKEND (FastAPI)                        │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           LangGraph Orchestrator                 │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │    │
│  │  │ Gather   │→ │ Score    │→ │ Explain      │  │    │
│  │  │ Evidence │  │ Risk     │  │ (Gemini LLM) │  │    │
│  │  └──────────┘  └──────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  Intelligence Layers:                                    │
│  ┌───────────┐ ┌───────────┐ ┌──────────┐ ┌─────────┐  │
│  │ 16 Regex  │ │ TF-IDF +  │ │ FAISS    │ │ RAG     │  │
│  │ Signal    │ │ LogReg    │ │ Semantic │ │ (RBI    │  │
│  │ Rules     │ │ Classifier│ │ Search   │ │ Guide)  │  │
│  └───────────┘ └───────────┘ └──────────┘ └─────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Risk Fusion Engine (Weighted: 0.4R + 0.4ML +    │   │
│  │  0.2Sem) → Risk Level → Policy Action            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Storage: SQLite (async) · FAISS Indexes · Joblib Models │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js, TypeScript | UI, Chat, Dashboard |
| Backend | FastAPI, Python 3.11 | API, Business Logic |
| Orchestration | LangGraph | Agentic workflow graph |
| LLM | Google Gemini (via LangChain) | Explanation generation |
| ML Classifier | scikit-learn (TF-IDF + LogReg) | Fraud text classification |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Semantic similarity |
| Vector Store | FAISS | Fast similarity search |
| RAG | LangChain + FAISS | Grounded knowledge retrieval |
| Database | SQLite + SQLAlchemy (async) | Persistence |
| Validation | Pydantic v2 | Schema enforcement |

---

## 4. Current System Progress

### ✅ Completed

| Stage | Component | Status |
|-------|----------|--------|
| Stage 1 | Dataset Augmentation (80 templates → ~1200 samples) | ✅ Done |
| Stage 1 | Knowledge Base (RBI Guidelines, Cybercrime FAQs) | ✅ Done |
| Stage 2 | TF-IDF + Logistic Regression Classifier | ✅ Trained & Saved |
| Stage 2 | FAISS Semantic Index (scam corpus) | ✅ Built |
| Stage 2 | Semantic Engine (similarity search) | ✅ Working |
| Stage 3 | RAG Engine (LangChain + FAISS) | ✅ Working |
| Stage 4 | LLM Router (Gemini abstraction) | ✅ Working |
| Stage 4 | Agent Tools (evidence gathering + risk fusion) | ✅ Working |
| Stage 4 | LangGraph Orchestrator (3-node graph) | ✅ Working |
| Stage 5 | API Integration (fraud_engine → orchestrator) | ✅ Working |
| Stage 5 | End-to-end API smoke test | ✅ Passing |
| P0 | 16-rule Regex Signal Extraction | ✅ Working |
| P0 | Risk Scoring & Fusion Engine | ✅ Working |
| P0 | Policy Engine (SAFE/WARN/PAUSE) | ✅ Working |
| P0 | FastAPI with full CRUD | ✅ Working |
| P0 | Transaction Analysis (finance_engine) | ✅ Working |

### 🔲 Remaining

| Component | Priority |
|----------|----------|
| Next.js Frontend | 🔴 Critical |
| Real-world dataset integration | 🔴 Critical |
| Screenshot/Image analysis (VLM) | 🟡 High |
| Behavioral baseline model | 🟡 High |
| URL safety checking | 🟡 Medium |
| Dockerization | 🟢 Nice-to-have |

---

## 5. Evaluation Results

### ML Classifier (TF-IDF + Logistic Regression)

**On synthetic augmented dataset (1248 samples):**

| Metric | Legitimate | Scam |
|--------|-----------|------|
| Precision | 1.00 | 1.00 |
| Recall | 1.00 | 1.00 |
| F1-Score | 1.00 | 1.00 |

> ⚠️ **Important caveat**: These metrics are on synthetic data generated from 80 templates via entity-swapping. Real-world performance will be lower. We plan to re-evaluate on held-out real data (see Section 8).

### End-to-End API Test

**Scam message**: *"Dear customer, your bank account will be blocked. Click here http://kyc-update.com to update urgently."*

| Score | Value |
|-------|-------|
| ML Classifier Score | 0.934 |
| Semantic Similarity Score | 0.866 |
| Fused Risk Score | 0.755 |
| Risk Level | SUSPICIOUS |
| Policy Action | WARN |

### System Characteristics

| Property | Value |
|----------|-------|
| Cold-start time | ~15s (model loading) |
| Inference time (warm) | <200ms |
| Graceful degradation | ✅ Works without API keys |
| Deterministic fallback | ✅ If LLM fails, hardcoded explanation |

---

## 6. Addressing the Problem Statement

| PS Requirement | Our Implementation |
|---|---|
| **Analyse spending patterns** | `finance_engine.py` — Transaction categorization, trend analysis, anomaly detection |
| **Categorize financial requirements** | Intent classification via LLM Router |
| **Compare relevant products** | RAG retrieval of financial product guidelines |
| **Detect suspicious communication** | 16-rule regex + TF-IDF classifier + semantic search + risk fusion |
| **Explain financial concepts simply** | Gemini LLM generates grounded explanations from evidence |
| **Personalized guidance** | Risk-adaptive policy actions (SAFE/WARN/PAUSE) |
| **Budget alerts** | Transaction analysis with threshold-based alerts |
| **Fraud warnings** | Multi-signal fraud detection with evidence-backed warnings |
| **Track financial goals** | Goal tracking in finance engine |

---

## 7. Real-World Scam Datasets (For Model Improvement)

| Dataset | Source | Size | Languages |
|---------|--------|------|-----------|
| Indian Social Media Fraud & Scam Detection | Kaggle | 3,200 messages | English, Hinglish |
| India Spam SMS Classification | Kaggle | ~5,000 SMS | English |
| Financial Scams Detection Dataset | Mendeley Data | Varied | Bangla-English |
| CloveAI/india-spam-sms | Hugging Face | Real-world Indian SMS | Multiple |
| SMS Spam Collection (UCI) | UCI ML Repo | 5,574 SMS | English |

**Community Sources:**
- r/IndianScams (Reddit) — Real user-reported scam messages
- CERT-In advisories — Official Indian cybersecurity bulletins
- I4C (Indian Cyber Crime Coordination Centre) — Complaint patterns
- Twitter/X #DigitalArrest — Trending scam reports

---

## 8. Future Scope & Team Contribution Areas (2026 Tech)

### 🔴 Immediate (Pre-Demo)

| Task | Owner | Description |
|------|-------|-------------|
| **Frontend (Next.js)** | Frontend Dev | Chat interface, risk dashboard, goal tracker |
| **Real Dataset Integration** | ML Engineer | Download Kaggle Indian Scam dataset (3,200 msgs), retrain model |
| **Screenshot Analysis** | Backend Dev | Integrate Gemini Vision API for OCR from scam screenshots |
| **Honest Eval Report** | ML Engineer | Re-run eval on held-out real data, report true F1 |

### 🟡 Advanced Improvements

| Technique | Why It Matters in 2026 |
|-----------|----------------------|
| **IndicBERT/MURIL Classifier** | Handles Hindi, Hinglish, Tamil — covers 60%+ of Indian users. Replace TF-IDF with fine-tuned transformer. |
| **Graph Neural Networks (GNN)** | Model transaction networks to detect money mule patterns and coordinated fraud rings. Industry standard at PayPal/Stripe. |
| **Agentic Tool Use** | Let the LangGraph agent dynamically decide which tools to call (URL checker, UPI reputation, RAG) based on the input — not hardcoded. |
| **Multi-Modal Fusion** | Combine text + image + metadata signals in a single fusion layer. Research frontier in 2026. |
| **Federated Learning** | Banks can improve the shared model without sharing customer data. Privacy-preserving ML. |
| **Adversarial Robustness** | Test against Unicode tricks, Hinglish obfuscation, homoglyph attacks ("0TP" instead of "OTP"). |
| **SHAP/LIME Explainability** | Visual feature importance for each prediction. Regulatory requirement in EU/UK, coming to India. |
| **Real-time Streaming** | Kafka/Flink for processing transaction streams. Currently batch/request-response only. |
| **Behavioral Biometrics** | Typing speed, device fingerprinting, session anomaly detection (BioCatch-style). |
| **Cross-Encoder Reranking** | Improve RAG precision with `cross-encoder/ms-marco-MiniLM-L-6-v2` reranker. |
| **Calibrated Probabilities** | Platt scaling or isotonic regression for well-calibrated risk scores. |

### 🟢 Deployment & Scale

| Area | Action |
|------|--------|
| **Docker Compose** | One-command deployment: `docker-compose up` |
| **CI/CD** | GitHub Actions: lint → test → build → deploy |
| **Monitoring** | Prometheus + Grafana for API latency, model drift |
| **Model Registry** | MLflow for versioned model tracking |
| **A/B Testing** | Compare model versions on real traffic |

---

## 9. Constraint Compliance

> *"The solution should provide decision support/education and should not claim to be a regulated investment advisor."*

✅ **Nirnaya is explicitly a decision-support tool.** It:
- Provides risk scores and evidence, not buy/sell recommendations
- Explains concepts, does not advise investment actions
- Creates intelligent pauses, does not block transactions
- Uses the phrase "We recommend you verify" not "You must not proceed"

---

## 10. Repository Structure

```
nirnaya/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── ml/           # ML models, training, evaluation
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   └── services/     # Business logic & orchestration
│   ├── data/             # Knowledge base documents
│   ├── tests/            # Unit & integration tests
│   └── pyproject.toml    # Dependencies
├── frontend/             # Next.js (planned)
├── docs/                 # Architecture documentation
├── AGENTS.md             # Agent rules & conventions
└── README.md
```

---

*Document generated: August 21, 2026*  
*System version: MVP v0.1 (Backend Complete, Frontend Pending)*
