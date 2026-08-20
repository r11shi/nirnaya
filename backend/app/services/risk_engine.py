"""Nirnaya — Risk Scoring, Fusion and Policy Engine.

This module combines fraud signals into a calibrated risk score
and determines the policy action (SAFE/WARN/PAUSE).

The scoring is transparent and documented. No hidden weights.
"""

from app.schemas import (
    FraudSignals, ExtractedEntities, RiskLevel, PolicyAction,
    EvidenceItem, RiskExplanation, TransactionContext,
)
from app.config import settings
from typing import Optional, Dict, List, Tuple


# ─── Signal Weights ──────────────────────────────────────────
# These weights are explicitly documented.
# They represent prior knowledge about signal importance,
# NOT learned weights. A learned fusion model (P1) will replace this.

SIGNAL_WEIGHTS: Dict[str, float] = {
    "urgency": 0.08,
    "threat_language": 0.10,
    "authority_impersonation": 0.06,
    "kyc_request": 0.10,
    "otp_request": 0.12,
    "credential_request": 0.14,
    "payment_request": 0.08,
    "url_present": 0.02,
    "phone_present": 0.01,
    "upi_present": 0.02,
    "suspicious_domain": 0.08,
    "domain_mismatch": 0.12,
    "reward_language": 0.06,
    "refund_language": 0.05,
    "remote_access_request": 0.14,
    "shortened_url": 0.04,
}

# Co-occurrence boosts: certain signal combinations are much riskier together
COOCCURRENCE_BOOSTS: List[Tuple[List[str], float]] = [
    (["urgency", "credential_request"], 0.10),
    (["urgency", "kyc_request", "url_present"], 0.08),
    (["otp_request", "authority_impersonation"], 0.10),
    (["remote_access_request", "payment_request"], 0.12),
    (["reward_language", "payment_request"], 0.08),
    (["domain_mismatch", "kyc_request"], 0.10),
    (["threat_language", "credential_request"], 0.10),
]


def calculate_signal_score(signals: FraudSignals) -> float:
    """Calculate weighted signal score from fraud signals.
    
    Returns a score between 0.0 and 1.0.
    """
    signals_dict = signals.model_dump()
    
    # Base weighted sum
    score = sum(
        SIGNAL_WEIGHTS.get(key, 0.0)
        for key, value in signals_dict.items()
        if value is True
    )

    # Co-occurrence boosts
    for required_signals, boost in COOCCURRENCE_BOOSTS:
        if all(signals_dict.get(s, False) for s in required_signals):
            score += boost

    # Clamp to [0, 1]
    return min(max(score, 0.0), 1.0)


def fuse_risk_scores(
    signal_score: float,
    text_model_score: Optional[float] = None,
    semantic_similarity_score: Optional[float] = None,
    behaviour_anomaly_score: Optional[float] = None,
    entity_reputation_score: Optional[float] = None,
) -> float:
    """Fuse multiple risk scores into a single risk score.
    
    Currently uses weighted average. P1 will replace with a learned meta-model.
    Only non-None scores contribute.
    """
    scores_and_weights = [
        (signal_score, 0.40),  # Structured signals (always available)
    ]

    if text_model_score is not None:
        scores_and_weights.append((text_model_score, 0.25))
    if semantic_similarity_score is not None:
        scores_and_weights.append((semantic_similarity_score, 0.15))
    if behaviour_anomaly_score is not None:
        scores_and_weights.append((behaviour_anomaly_score, 0.10))
    if entity_reputation_score is not None:
        scores_and_weights.append((entity_reputation_score, 0.10))

    # Normalize weights to sum to 1
    total_weight = sum(w for _, w in scores_and_weights)
    if total_weight == 0:
        return 0.0

    fused = sum(s * w for s, w in scores_and_weights) / total_weight
    return min(max(fused, 0.0), 1.0)


def classify_risk_level(score: float) -> RiskLevel:
    """Map a calibrated risk score to a risk level.
    
    Thresholds are configurable via settings.
    """
    if score >= settings.RISK_HIGH_THRESHOLD:
        return RiskLevel.HIGH
    elif score >= settings.RISK_SUSPICIOUS_THRESHOLD:
        return RiskLevel.SUSPICIOUS
    elif score >= settings.RISK_LOW_THRESHOLD:
        return RiskLevel.UNCERTAIN
    else:
        return RiskLevel.LOW


def determine_policy_action(
    risk_level: RiskLevel,
    risk_score: float,
    transaction_context: Optional[TransactionContext] = None,
) -> Tuple[PolicyAction, Optional[int]]:
    """Determine the policy action and optional pause duration.
    
    Returns (action, pause_duration_seconds or None).
    """
    if risk_level == RiskLevel.LOW:
        return PolicyAction.SAFE, None
    elif risk_level == RiskLevel.UNCERTAIN:
        return PolicyAction.WARN, None
    elif risk_level == RiskLevel.SUSPICIOUS:
        # Base pause: 15 seconds
        pause = 15
        # Increase for large transactions
        if transaction_context and transaction_context.amount:
            if transaction_context.amount > 10000:
                pause = 20
            if transaction_context.amount > 50000:
                pause = 30
        if transaction_context and transaction_context.is_new_payee:
            pause += 5
        return PolicyAction.WARN, pause
    else:  # HIGH
        pause = 30
        if transaction_context and transaction_context.amount:
            if transaction_context.amount > 10000:
                pause = 45
            if transaction_context.amount > 50000:
                pause = 60
        if transaction_context and transaction_context.is_new_payee:
            pause += 10
        return PolicyAction.PAUSE, pause


def build_explanation(
    signals: FraudSignals,
    entities: ExtractedEntities,
    risk_score: float,
    risk_level: RiskLevel,
    policy_action: PolicyAction,
    text_model_score: Optional[float] = None,
    semantic_similarity_score: Optional[float] = None,
    behaviour_anomaly_score: Optional[float] = None,
    transaction_context: Optional[TransactionContext] = None,
) -> RiskExplanation:
    """Build a structured explanation from actual evidence.
    
    The explanation only references signals/evidence that are actually present.
    It does not fabricate evidence.
    """
    evidence: List[EvidenceItem] = []
    signals_dict = signals.model_dump()

    # Human-readable signal descriptions
    signal_descriptions = {
        "urgency": "Urgent action or deadline detected",
        "threat_language": "Threatening language about account consequences",
        "authority_impersonation": "Claims to be from an authority or financial institution",
        "kyc_request": "KYC/identity verification request detected",
        "otp_request": "Request to share OTP or one-time password",
        "credential_request": "Request for sensitive credentials (password, PIN, CVV)",
        "payment_request": "Advance payment or fee requested",
        "url_present": "Contains a URL link",
        "phone_present": "Contains a phone number",
        "upi_present": "Contains a UPI ID",
        "suspicious_domain": "URL domain does not match known legitimate domains",
        "domain_mismatch": f"Claimed organization ({entities.claimed_organization}) domain does not match URL",
        "reward_language": "Reward, prize, or lottery language detected",
        "refund_language": "Refund-related language detected",
        "remote_access_request": "Request to install remote access software",
        "shortened_url": "URL shortener detected (may hide true destination)",
    }

    for signal_name, is_active in signals_dict.items():
        if is_active:
            evidence.append(EvidenceItem(
                signal=signal_name,
                present=True,
                weight=SIGNAL_WEIGHTS.get(signal_name, 0.0),
                detail=signal_descriptions.get(signal_name, signal_name),
            ))

    # Add entity-based evidence
    if entities.claimed_organization:
        evidence.append(EvidenceItem(
            signal="claimed_organization",
            present=True,
            detail=f"Message claims to be from {entities.claimed_organization}",
        ))

    # Add ML-based evidence if available
    if text_model_score is not None and text_model_score > 0.5:
        evidence.append(EvidenceItem(
            signal="text_classification",
            present=True,
            value=round(text_model_score, 3),
            detail=f"Text classifier confidence: {text_model_score:.1%}",
        ))

    if semantic_similarity_score is not None and semantic_similarity_score > 0.5:
        evidence.append(EvidenceItem(
            signal="known_scam_similarity",
            present=True,
            value=round(semantic_similarity_score, 3),
            detail=f"Similarity to known scam patterns: {semantic_similarity_score:.1%}",
        ))

    if behaviour_anomaly_score is not None and behaviour_anomaly_score > 0.5:
        evidence.append(EvidenceItem(
            signal="behaviour_anomaly",
            present=True,
            value=round(behaviour_anomaly_score, 3),
            detail="Transaction is unusual compared to your normal behaviour",
        ))

    # Transaction-specific evidence
    if transaction_context:
        if transaction_context.is_new_payee:
            evidence.append(EvidenceItem(
                signal="new_payee",
                present=True,
                detail="This is a new recipient you haven't transacted with before",
            ))
        if transaction_context.amount and transaction_context.amount > 10000:
            evidence.append(EvidenceItem(
                signal="large_amount",
                present=True,
                value=transaction_context.amount,
                detail=f"Transaction amount ₹{transaction_context.amount:,.0f} is significant",
            ))

    # Build summary
    active_count = len([e for e in evidence if e.present])
    if risk_level == RiskLevel.HIGH:
        summary = f"HIGH RISK — {active_count} fraud indicators detected. We strongly recommend not proceeding."
    elif risk_level == RiskLevel.SUSPICIOUS:
        summary = f"SUSPICIOUS — {active_count} potential fraud indicators detected. Please verify before proceeding."
    elif risk_level == RiskLevel.UNCERTAIN:
        summary = f"UNCERTAIN — Some indicators detected. Exercise caution."
    else:
        summary = "LOW RISK — No significant fraud indicators detected."

    return RiskExplanation(
        summary=summary,
        evidence=evidence,
    )
