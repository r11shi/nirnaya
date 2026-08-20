# NIRNAYA — Project Specification v1.0

## 1. What Is Nirnaya

Nirnaya is a multimodal personal financial risk and decision-support system.

**Core thesis:** People make poor financial decisions at moments when they lack context or are vulnerable to fraud. Nirnaya provides a second opinion before the decision is completed.

**Two connected capabilities:**
1. Fraud/scam awareness and intervention
2. Personal financial intelligence and decision support

**Core loop:** Problem → Measurement → Intelligence → Action → Measurable Improvement

---

## 2. Architecture

```
Frontend (Next.js + TypeScript)
       │
       ▼
Backend (FastAPI + Python)
       │
  ┌────┼────────────────┐
  ▼    ▼                ▼
 API  Services         ML/AI
  │    │                │
  │    ├─ FraudEngine   ├─ TextClassifier
  │    ├─ FinanceEngine ├─ Embeddings
  │    ├─ OCRService    ├─ RiskFusion
  │    ├─ Explanation   ├─ BehaviourModel
  │    └─ PolicyEngine  └─ LLMRouter
  │
  ▼
Database (SQLite dev / PostgreSQL prod)
```

### Rules

1. LLMs extract, classify, retrieve, reason, explain. They do NOT decide fraud, calculate finances, or invent evidence.
2. Every external dependency has a local/deterministic fallback.
3. Financial calculations are deterministic Python functions.
4. All important data is typed via Pydantic schemas.

---

## 3. Modules

### Module A — Fraud Engine
- Input: text, screenshot, URL, transaction context
- Pipeline: OCR/VLM → Entity extraction → Signal detection → Classifier → Semantic retrieval → Behaviour check → Risk fusion → Policy → Explanation
- Output: Calibrated risk score, risk level, policy action, structured evidence, natural-language explanation

### Module B — Finance Engine  
- Input: CSV transactions, manual entries, goals
- Pipeline: Parse → Categorize → Analyze → Goal calculation → Scenario simulation
- Output: Spending summary, goal progress, scenario projections

### Module C — Connected Experience
- When fraud is detected on a transaction, calculate financial impact on goals
- Show contextual intervention with evidence + financial consequence

---

## 4. API Contracts

### Health
```
GET /api/health → {"status": "ok", "version": "1.0.0"}
```

### Fraud
```
POST /api/fraud/analyze
  Body: {input_type, text?, image_base64?, url?, transaction_context?, user_id?}
  Response: {analysis_id, risk_score, risk_level, policy_action, explanation, extracted_entities}

GET /api/fraud/analysis/{id}
POST /api/fraud/feedback
```

### Finance
```
POST /api/finance/transactions/upload (multipart CSV)
GET  /api/finance/transactions/{user_id}
GET  /api/finance/spending/{user_id}
POST /api/finance/goals
GET  /api/finance/goals/{user_id}
POST /api/finance/goals/{id}/simulate
```

---

## 5. Database Schema

### users
- id (UUID PK), name, created_at

### transactions
- id (UUID PK), user_id (FK), amount, category, payee, description, transaction_date, source, created_at

### fraud_analyses
- id (UUID PK), user_id (FK), input_type, raw_input, image_path, extracted_text, extracted_entities (JSON), fraud_signals (JSON), text_model_score, semantic_similarity_score, behaviour_anomaly_score, fused_risk_score, calibrated_risk, risk_level, policy_action, explanation (JSON), explanation_text, created_at

### goals
- id (UUID PK), user_id (FK), name, target_amount, current_amount, deadline, priority, created_at

### feedback
- id (UUID PK), analysis_id (FK), user_id (FK), action, is_correct, notes, created_at

### scam_entities (P1)
- id (UUID PK), entity_type, entity_hash, report_count, risk_score, first_seen, last_seen

---

## 6. Model Strategy

### Fraud Classifier
- Baseline: TF-IDF + Logistic Regression
- Benchmark: MiniLM + small transformer
- Meta-model: LightGBM risk fusion (if data supports)

### Embeddings
- Sentence Transformers (local, no API)

### Vector Search
- FAISS (dev), Qdrant (optional)

### OCR
- PaddleOCR (CPU-friendly)

### LLM Router
- Gemini (multimodal/reasoning) → Groq (fast structured) → Local → Deterministic fallback

---

## 7. Fallback Strategy

| Dependency | Fallback |
|---|---|
| Gemini | Groq → Local → Deterministic |
| Groq | Local → Deterministic |
| Vector DB | FAISS in-memory |
| OCR | Manual text input |
| LLM explanation | Template-based explanation |
| Database | SQLite |

---

## 8. Evaluation Strategy

### Fraud
- Precision, Recall, F1, PR-AUC, FPR
- Legitimate message benchmark (OTP, bank alerts, delivery)
- Robustness: scam variations

### Semantic Retrieval
- Recall@K, Precision@K

### Finance
- Unit tests for all calculations
- Scenario verification

### Connected Experience
- End-to-end scenario tests

---

## 9. Deployment

- Frontend: Vercel / static export
- Backend: Docker container (FastAPI)
- Database: SQLite (demo) / PostgreSQL (production)
- Cost: ₹0 mandatory. Free tiers + student credits.
