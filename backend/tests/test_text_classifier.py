"""Tests for Nirnaya ML text classifier."""

import pytest
from app.ml.text_classifier import predict_fraud_probability

def test_predict_scam_high_prob():
    text = "Dear customer, your bank account will be blocked. Click here http://kyc-update.com to update."
    prob = predict_fraud_probability(text)
    assert prob > 0.8

def test_predict_legit_low_prob():
    text = "Your salary of Rs.50,000 has been credited to your account. Available balance is Rs.75,000."
    prob = predict_fraud_probability(text)
    assert prob < 0.4

def test_empty_string_zero_prob():
    prob = predict_fraud_probability("")
    assert prob == 0.0

def test_robustness_variation():
    text = "URGENT! A/C suspension in 24 hrs. Pls share OTP to verify identity immediately."
    prob = predict_fraud_probability(text)
    assert prob > 0.6  # Even with slight wording variations, it should catch it
