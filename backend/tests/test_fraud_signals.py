"""Tests for Nirnaya fraud signal extraction."""

import pytest
from app.services.fraud_signals import extract_entities, extract_fraud_signals


class TestEntityExtraction:
    """Test entity extraction from financial messages."""

    def test_extract_url(self):
        text = "Click here: http://sbi-kyc-verify.com/update"
        entities = extract_entities(text)
        assert len(entities.urls) > 0
        assert any("sbi-kyc-verify" in u for u in entities.urls)

    def test_extract_phone(self):
        text = "Call us at 9876543210 for assistance"
        entities = extract_entities(text)
        assert len(entities.phones) > 0

    def test_extract_upi(self):
        text = "Pay to merchant@upi for your order"
        entities = extract_entities(text)
        assert len(entities.upis) > 0

    def test_extract_amount_rupee_symbol(self):
        text = "Pay ₹48,000 immediately"
        entities = extract_entities(text)
        assert 48000.0 in entities.amounts

    def test_extract_amount_rs(self):
        text = "Transfer Rs.25000 to this account"
        entities = extract_entities(text)
        assert 25000.0 in entities.amounts

    def test_detect_claimed_org_sbi(self):
        text = "Dear SBI customer, your account needs KYC update"
        entities = extract_entities(text)
        assert entities.claimed_organization == "SBI"

    def test_detect_claimed_org_rbi(self):
        text = "As per RBI guidelines, update your PAN immediately"
        entities = extract_entities(text)
        assert entities.claimed_organization == "RBI"

    def test_no_entities_in_clean_text(self):
        text = "Meeting at 3pm tomorrow"
        entities = extract_entities(text)
        assert len(entities.urls) == 0
        assert len(entities.upis) == 0
        assert len(entities.amounts) == 0


class TestFraudSignals:
    """Test individual fraud signal detection."""

    def test_urgency_detection(self):
        text = "Your account will be blocked within 24 hours"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.urgency is True

    def test_threat_detection(self):
        text = "Your account will be suspended permanently"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.threat_language is True

    def test_kyc_request(self):
        text = "Update your KYC details immediately"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.kyc_request is True

    def test_otp_request(self):
        text = "Please share your OTP for verification"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.otp_request is True

    def test_credential_request(self):
        text = "Enter your password and PIN to verify"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.credential_request is True

    def test_payment_request(self):
        text = "Pay Rs.500 as processing fee"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.payment_request is True

    def test_reward_language(self):
        text = "Congratulations! You have won a prize of Rs.50,000"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.reward_language is True

    def test_remote_access(self):
        text = "Please install AnyDesk and share the code"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.remote_access_request is True

    def test_domain_mismatch(self):
        text = "Dear SBI customer, visit http://sbi-updates.xyz for KYC"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.domain_mismatch is True

    def test_shortened_url(self):
        text = "Click here: https://bit.ly/abc123"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.shortened_url is True

    def test_legitimate_message_low_signals(self):
        """A genuine bank alert should have minimal fraud signals."""
        text = "Your SBI account XX1234 has been credited with Rs.5000. Available balance: Rs.25000."
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        # Should NOT trigger high-risk signals
        assert signals.otp_request is False
        assert signals.credential_request is False
        assert signals.remote_access_request is False
        assert signals.payment_request is False

    def test_scam_message_multiple_signals(self):
        """A typical scam message should trigger multiple signals."""
        text = (
            "URGENT: Dear SBI customer, your account will be blocked. "
            "Update KYC immediately at http://sbi-kyc-update.tk "
            "Share OTP sent to your number. Call 9876543210."
        )
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.urgency is True
        assert signals.threat_language is True
        assert signals.kyc_request is True
        assert signals.otp_request is True
        assert signals.domain_mismatch is True
        assert signals.signal_count >= 5

    def test_signal_count(self):
        text = "Share your OTP now. Enter your password. Your account will be blocked immediately."
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert signals.otp_request is True
        assert signals.credential_request is True
        assert signals.threat_language is True
        assert signals.signal_count >= 3

    def test_signal_score_range(self):
        text = "Any message"
        entities = extract_entities(text)
        signals = extract_fraud_signals(text, entities)
        assert 0.0 <= signals.signal_score <= 1.0
