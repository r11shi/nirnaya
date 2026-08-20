"""Nirnaya Backend — Pydantic Schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────

class InputType(str, Enum):
    TEXT = "text"
    SCREENSHOT = "screenshot"
    URL = "url"


class RiskLevel(str, Enum):
    LOW = "LOW"
    UNCERTAIN = "UNCERTAIN"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH = "HIGH"


class PolicyAction(str, Enum):
    SAFE = "SAFE"
    WARN = "WARN"
    PAUSE = "PAUSE"


class FeedbackAction(str, Enum):
    CANCELLED = "cancelled"
    PROCEEDED = "proceeded"
    REPORTED_SCAM = "reported_scam"
    MARKED_SAFE = "marked_safe"


# ─── Fraud Schemas ───────────────────────────────────────────

class FraudSignals(BaseModel):
    """Structured binary/float fraud signals extracted from a message."""
    urgency: bool = False
    threat_language: bool = False
    authority_impersonation: bool = False
    kyc_request: bool = False
    otp_request: bool = False
    credential_request: bool = False
    payment_request: bool = False
    url_present: bool = False
    phone_present: bool = False
    upi_present: bool = False
    suspicious_domain: bool = False
    domain_mismatch: bool = False
    reward_language: bool = False
    refund_language: bool = False
    remote_access_request: bool = False
    shortened_url: bool = False

    @property
    def signal_count(self) -> int:
        """Number of active (True) signals."""
        return sum(1 for v in self.model_dump().values() if v is True)

    @property
    def signal_score(self) -> float:
        """Fraction of active signals (0-1)."""
        fields = self.model_dump()
        return self.signal_count / len(fields) if fields else 0.0


class ExtractedEntities(BaseModel):
    """Entities extracted from a financial message."""
    claimed_organization: Optional[str] = None
    urls: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    upis: List[str] = Field(default_factory=list)
    amounts: List[float] = Field(default_factory=list)
    action_requested: Optional[str] = None
    language: Optional[str] = None


class EvidenceItem(BaseModel):
    """A single piece of evidence supporting risk assessment."""
    signal: str
    present: bool = True
    value: Optional[Any] = None
    weight: Optional[float] = None
    detail: Optional[str] = None


class RiskExplanation(BaseModel):
    """Structured explanation of risk assessment."""
    summary: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    financial_impact: Optional[str] = None


class TransactionContext(BaseModel):
    """Optional transaction context for fraud analysis."""
    amount: Optional[float] = None
    payee: Optional[str] = None
    is_new_payee: bool = False
    transaction_time: Optional[str] = None


class FraudAnalyzeRequest(BaseModel):
    """Request to analyze a message/screenshot for fraud."""
    input_type: InputType = InputType.TEXT
    text: Optional[str] = None
    image_base64: Optional[str] = None
    url: Optional[str] = None
    transaction_context: Optional[TransactionContext] = None
    user_id: Optional[str] = None


class FraudAnalyzeResponse(BaseModel):
    """Response from fraud analysis."""
    analysis_id: str
    input_type: str
    risk_score: float
    risk_level: RiskLevel
    policy_action: PolicyAction
    pause_duration_seconds: Optional[int] = None
    explanation: RiskExplanation
    extracted_entities: ExtractedEntities
    fraud_signals: FraudSignals
    raw_scores: Dict[str, Optional[float]] = Field(default_factory=dict)
    created_at: datetime


class FeedbackRequest(BaseModel):
    """User feedback on a fraud analysis."""
    analysis_id: str
    user_id: Optional[str] = None
    action: FeedbackAction
    is_correct: Optional[bool] = None
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    analysis_id: str
    action: str
    created_at: datetime


# ─── Finance Schemas ─────────────────────────────────────────

class TransactionSchema(BaseModel):
    id: Optional[str] = None
    amount: float
    category: Optional[str] = None
    payee: Optional[str] = None
    description: Optional[str] = None
    transaction_date: datetime
    source: str = "manual"
    is_income: bool = False


class TransactionUploadResponse(BaseModel):
    imported: int
    skipped: int
    categories: Dict[str, int]
    date_range: Dict[str, str]
    user_id: str


class SpendingSummary(BaseModel):
    user_id: str
    period: str  # "monthly", "weekly"
    total_income: float
    total_expenses: float
    monthly_surplus: float
    by_category: Dict[str, float]
    monthly_trends: List[Dict[str, Any]] = Field(default_factory=list)
    top_payees: List[Dict[str, Any]] = Field(default_factory=list)


class GoalCreateRequest(BaseModel):
    user_id: str
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None
    priority: int = 1


class GoalResponse(BaseModel):
    id: str
    user_id: str
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime]
    priority: int
    progress_pct: float
    monthly_required: Optional[float] = None
    months_remaining: Optional[int] = None
    on_track: Optional[bool] = None
    created_at: datetime


class GoalSimulateRequest(BaseModel):
    user_id: str
    scenario: Dict[str, Any]  # e.g. {"reduce_category": "dining", "reduce_by": 1000}


class GoalSimulateResponse(BaseModel):
    goal_id: str
    goal_name: str
    current_monthly_savings: float
    new_monthly_savings: float
    current_months_to_goal: Optional[int]
    new_months_to_goal: Optional[int]
    savings_difference: float
    projected_goal_date: Optional[str]
    scenario_description: str


# ─── Connected Experience ────────────────────────────────────

class InterventionResponse(BaseModel):
    """Combined fraud + financial impact for the connected experience."""
    fraud_analysis: FraudAnalyzeResponse
    financial_impact: Optional[GoalSimulateResponse] = None
    impact_summary: Optional[str] = None


# ─── Health ──────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    database: str = "connected"
    llm_provider: str = "mock"
