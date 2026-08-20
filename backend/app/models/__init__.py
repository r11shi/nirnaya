"""Nirnaya Backend — SQLAlchemy ORM Models."""

from sqlalchemy import Column, String, Float, Boolean, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    payee = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(50), default="manual")  # csv, sms, manual
    is_income = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FraudAnalysis(Base):
    __tablename__ = "fraud_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    input_type = Column(String(50), nullable=False)  # text, screenshot, url
    raw_input = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    extracted_text = Column(Text, nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    fraud_signals = Column(JSON, nullable=True)
    text_model_score = Column(Float, nullable=True)
    semantic_similarity_score = Column(Float, nullable=True)
    behaviour_anomaly_score = Column(Float, nullable=True)
    entity_reputation_score = Column(Float, nullable=True)
    fused_risk_score = Column(Float, nullable=True)
    calibrated_risk = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # LOW, UNCERTAIN, SUSPICIOUS, HIGH
    policy_action = Column(String(20), nullable=True)  # SAFE, WARN, PAUSE
    pause_duration_seconds = Column(Integer, nullable=True)
    explanation = Column(JSON, nullable=True)
    explanation_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("fraud_analyses.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)  # cancelled, proceeded, reported_scam, marked_safe
    is_correct = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScamEntity(Base):
    __tablename__ = "scam_entities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)  # phone, upi, url, domain
    entity_hash = Column(String(64), nullable=False, unique=True)
    entity_value = Column(String(500), nullable=True)  # raw value (dev only)
    report_count = Column(Integer, default=1)
    risk_score = Column(Float, nullable=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
