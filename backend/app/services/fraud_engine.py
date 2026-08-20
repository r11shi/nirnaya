"""Nirnaya — Fraud Analysis Engine.

Orchestrates: signal extraction → risk scoring → policy → explanation.
This is the main entry point for fraud analysis.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import (
    FraudAnalyzeRequest, FraudAnalyzeResponse,
    FraudSignals, ExtractedEntities, RiskExplanation,
    RiskLevel, PolicyAction, TransactionContext,
    FeedbackRequest, FeedbackResponse,
)
from app.models import FraudAnalysis, Feedback
from app.services.fraud_signals import extract_entities, extract_fraud_signals
from app.services.risk_engine import (
    calculate_signal_score, fuse_risk_scores,
    classify_risk_level, determine_policy_action, build_explanation,
)

logger = logging.getLogger(__name__)


async def analyze_fraud(
    request: FraudAnalyzeRequest,
    db: AsyncSession,
) -> FraudAnalyzeResponse:
    """Run the full fraud analysis pipeline on input text.
    
    Pipeline:
    1. Extract entities (URLs, phones, UPIs, amounts, claimed org)
    2. Extract fraud signals (16 binary signals)
    3. Calculate signal score (weighted sum with co-occurrence boosts)
    4. Fuse with other scores if available (text model, semantic, behaviour)
    5. Classify risk level (LOW/UNCERTAIN/SUSPICIOUS/HIGH)
    6. Determine policy action (SAFE/WARN/PAUSE) and pause duration
    7. Build structured explanation from actual evidence
    8. Persist to database
    9. Return typed response
    """
    text = request.text or ""
    
    # If screenshot, text will come from OCR (Phase 4)
    # For now, require text input
    if request.input_type.value == "screenshot" and request.image_base64:
        # TODO: Phase 4 — OCR extraction
        # For now, use any text that was provided alongside
        if not text:
            text = "[Screenshot uploaded — OCR not yet implemented]"
    
    if request.input_type.value == "url" and request.url:
        # Include URL in text for analysis
        text = f"{text} {request.url}".strip()

    # Step 1: Extract entities
    entities = extract_entities(text)

    # Step 2: Extract fraud signals
    signals = extract_fraud_signals(text, entities)

    # Step 3: Calculate signal score
    signal_score = calculate_signal_score(signals)

    # Step 4: Fuse scores
    # In P0, only signal_score is available.
    # text_model_score, semantic_similarity_score, etc. come in later phases.
    fused_score = fuse_risk_scores(
        signal_score=signal_score,
        text_model_score=None,  # Phase 2b: ML classifier
        semantic_similarity_score=None,  # Phase 5: semantic retrieval
        behaviour_anomaly_score=None,  # Phase 6: behaviour model
        entity_reputation_score=None,  # Phase 5: entity reputation
    )

    # Step 5: Risk level
    risk_level = classify_risk_level(fused_score)

    # Step 6: Policy action
    policy_action, pause_duration = determine_policy_action(
        risk_level, fused_score, request.transaction_context
    )

    # Step 7: Explanation
    explanation = build_explanation(
        signals=signals,
        entities=entities,
        risk_score=fused_score,
        risk_level=risk_level,
        policy_action=policy_action,
        transaction_context=request.transaction_context,
    )

    # Step 8: Persist
    analysis = FraudAnalysis(
        user_id=request.user_id,
        input_type=request.input_type.value,
        raw_input=text,
        extracted_text=text,
        extracted_entities=entities.model_dump(),
        fraud_signals=signals.model_dump(),
        text_model_score=None,
        semantic_similarity_score=None,
        behaviour_anomaly_score=None,
        entity_reputation_score=None,
        fused_risk_score=fused_score,
        calibrated_risk=fused_score,  # Will be calibrated in Phase 7
        risk_level=risk_level.value,
        policy_action=policy_action.value,
        pause_duration_seconds=pause_duration,
        explanation=explanation.model_dump(),
        explanation_text=explanation.summary,
    )
    db.add(analysis)
    await db.flush()

    logger.info(
        f"Fraud analysis completed: id={analysis.id} "
        f"risk={fused_score:.3f} level={risk_level.value} "
        f"action={policy_action.value} signals={signals.signal_count}"
    )

    # Step 9: Response
    return FraudAnalyzeResponse(
        analysis_id=analysis.id,
        input_type=request.input_type.value,
        risk_score=round(fused_score, 4),
        risk_level=risk_level,
        policy_action=policy_action,
        pause_duration_seconds=pause_duration,
        explanation=explanation,
        extracted_entities=entities,
        fraud_signals=signals,
        raw_scores={
            "signal_score": round(signal_score, 4),
            "text_model_score": None,
            "semantic_similarity_score": None,
            "behaviour_anomaly_score": None,
            "entity_reputation_score": None,
            "fused_risk_score": round(fused_score, 4),
        },
        created_at=datetime.now(timezone.utc),
    )


async def get_analysis(analysis_id: str, db: AsyncSession) -> Optional[FraudAnalysis]:
    """Retrieve a fraud analysis by ID."""
    result = await db.execute(
        select(FraudAnalysis).where(FraudAnalysis.id == analysis_id)
    )
    return result.scalar_one_or_none()


async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession,
) -> FeedbackResponse:
    """Store user feedback on a fraud analysis."""
    feedback = Feedback(
        analysis_id=request.analysis_id,
        user_id=request.user_id,
        action=request.action.value,
        is_correct=request.is_correct,
        notes=request.notes,
    )
    db.add(feedback)
    await db.flush()

    logger.info(
        f"Feedback received: analysis={request.analysis_id} "
        f"action={request.action.value} correct={request.is_correct}"
    )

    return FeedbackResponse(
        feedback_id=feedback.id,
        analysis_id=request.analysis_id,
        action=request.action.value,
        created_at=datetime.now(timezone.utc),
    )
