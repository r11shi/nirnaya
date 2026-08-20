"""Tests for Nirnaya risk engine."""

import pytest
from app.schemas import FraudSignals, ExtractedEntities, RiskLevel, PolicyAction, TransactionContext
from app.services.risk_engine import (
    calculate_signal_score, fuse_risk_scores,
    classify_risk_level, determine_policy_action, build_explanation,
)


class TestSignalScoring:
    """Test signal score calculation."""

    def test_no_signals_zero_score(self):
        signals = FraudSignals()  # all False
        score = calculate_signal_score(signals)
        assert score == 0.0

    def test_single_signal(self):
        signals = FraudSignals(urgency=True)
        score = calculate_signal_score(signals)
        assert score > 0.0
        assert score < 1.0

    def test_multiple_signals_higher_score(self):
        single = FraudSignals(urgency=True)
        multiple = FraudSignals(urgency=True, kyc_request=True, credential_request=True)
        assert calculate_signal_score(multiple) > calculate_signal_score(single)

    def test_cooccurrence_boost(self):
        """Urgency + credential_request together should score higher than sum of parts."""
        urgency_only = FraudSignals(urgency=True)
        cred_only = FraudSignals(credential_request=True)
        both = FraudSignals(urgency=True, credential_request=True)
        sum_individual = calculate_signal_score(urgency_only) + calculate_signal_score(cred_only)
        assert calculate_signal_score(both) > sum_individual * 0.9  # boost effect

    def test_score_clamped_to_one(self):
        signals = FraudSignals(**{k: True for k in FraudSignals.model_fields})
        score = calculate_signal_score(signals)
        assert score <= 1.0


class TestRiskFusion:
    """Test risk score fusion."""

    def test_signal_only(self):
        score = fuse_risk_scores(signal_score=0.5)
        assert score == 0.5

    def test_with_text_model(self):
        score = fuse_risk_scores(signal_score=0.5, text_model_score=0.8)
        assert score > 0.5  # text model pulls it up

    def test_all_sources(self):
        score = fuse_risk_scores(
            signal_score=0.5,
            text_model_score=0.8,
            semantic_similarity_score=0.7,
            behaviour_anomaly_score=0.6,
            entity_reputation_score=0.9,
        )
        assert 0.0 <= score <= 1.0


class TestRiskClassification:
    """Test risk level classification."""

    def test_low_risk(self):
        assert classify_risk_level(0.1) == RiskLevel.LOW

    def test_uncertain(self):
        assert classify_risk_level(0.5) == RiskLevel.UNCERTAIN

    def test_suspicious(self):
        assert classify_risk_level(0.75) == RiskLevel.SUSPICIOUS

    def test_high_risk(self):
        assert classify_risk_level(0.95) == RiskLevel.HIGH


class TestPolicyEngine:
    """Test policy action determination."""

    def test_low_risk_safe(self):
        action, pause = determine_policy_action(RiskLevel.LOW, 0.1)
        assert action == PolicyAction.SAFE
        assert pause is None

    def test_high_risk_pause(self):
        action, pause = determine_policy_action(RiskLevel.HIGH, 0.95)
        assert action == PolicyAction.PAUSE
        assert pause is not None
        assert pause > 0

    def test_high_risk_large_amount_longer_pause(self):
        ctx = TransactionContext(amount=100000, is_new_payee=True)
        action, pause = determine_policy_action(RiskLevel.HIGH, 0.95, ctx)
        assert pause >= 60

    def test_uncertain_warns(self):
        action, pause = determine_policy_action(RiskLevel.UNCERTAIN, 0.5)
        assert action == PolicyAction.WARN


class TestExplanation:
    """Test explanation generation."""

    def test_explanation_only_active_signals(self):
        signals = FraudSignals(urgency=True, kyc_request=True)
        entities = ExtractedEntities()
        explanation = build_explanation(
            signals=signals, entities=entities,
            risk_score=0.5, risk_level=RiskLevel.UNCERTAIN,
            policy_action=PolicyAction.WARN,
        )
        # Should have evidence items for active signals
        signal_names = [e.signal for e in explanation.evidence]
        assert "urgency" in signal_names
        assert "kyc_request" in signal_names
        # Should NOT have inactive signals
        assert "remote_access_request" not in signal_names

    def test_explanation_has_summary(self):
        signals = FraudSignals()
        entities = ExtractedEntities()
        explanation = build_explanation(
            signals=signals, entities=entities,
            risk_score=0.1, risk_level=RiskLevel.LOW,
            policy_action=PolicyAction.SAFE,
        )
        assert "LOW RISK" in explanation.summary

    def test_high_risk_explanation(self):
        signals = FraudSignals(
            urgency=True, credential_request=True,
            domain_mismatch=True, otp_request=True,
        )
        entities = ExtractedEntities(claimed_organization="SBI")
        explanation = build_explanation(
            signals=signals, entities=entities,
            risk_score=0.92, risk_level=RiskLevel.HIGH,
            policy_action=PolicyAction.PAUSE,
        )
        assert "HIGH RISK" in explanation.summary
        assert len(explanation.evidence) >= 4
