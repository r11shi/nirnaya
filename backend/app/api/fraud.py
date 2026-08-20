"""Nirnaya — Fraud Analysis API Routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    FraudAnalyzeRequest, FraudAnalyzeResponse,
    FeedbackRequest, FeedbackResponse,
)
from app.services.fraud_engine import analyze_fraud, get_analysis, submit_feedback

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fraud", tags=["fraud"])


@router.post("/analyze", response_model=FraudAnalyzeResponse)
async def analyze(
    request: FraudAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyze text/screenshot/URL for fraud indicators.
    
    Returns risk score, risk level, policy action, and structured explanation.
    """
    if not request.text and not request.image_base64 and not request.url:
        raise HTTPException(
            status_code=400,
            detail="At least one of text, image_base64, or url is required",
        )
    
    try:
        result = await analyze_fraud(request, db)
        return result
    except Exception as e:
        logger.error(f"Fraud analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analysis/{analysis_id}")
async def get_analysis_by_id(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a previous fraud analysis by ID."""
    analysis = await get_analysis(analysis_id, db)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": analysis.id,
        "input_type": analysis.input_type,
        "risk_level": analysis.risk_level,
        "policy_action": analysis.policy_action,
        "fused_risk_score": analysis.fused_risk_score,
        "explanation": analysis.explanation,
        "fraud_signals": analysis.fraud_signals,
        "extracted_entities": analysis.extracted_entities,
        "created_at": str(analysis.created_at),
    }


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit user feedback on a fraud analysis."""
    # Verify analysis exists
    analysis = await get_analysis(request.analysis_id, db)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        return await submit_feedback(request, db)
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")
