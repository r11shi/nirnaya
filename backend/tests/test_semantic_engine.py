"""Tests for Nirnaya semantic scam retrieval."""

import pytest
from app.ml.semantic_engine import find_similar_scams, get_max_semantic_score

def test_semantic_match_kyc():
    text = "Dear user, your bank account is suspended. Do KYC urgently."
    results = find_similar_scams(text, top_k=1)
    
    # Even if wording is slightly different, it should find a KYC phishing scam
    assert len(results) == 1
    assert results[0]["category"] == "kyc_phishing"
    assert results[0]["similarity"] > 0.5

def test_semantic_match_otp():
    text = "Please share the OTP to process your refund."
    results = find_similar_scams(text, top_k=1)
    
    assert len(results) == 1
    assert "otp" in results[0]["category"]
    assert results[0]["similarity"] > 0.5

def test_max_score():
    text = "Congratulations, you won a lottery!"
    score = get_max_semantic_score(text)
    assert score > 0.5

def test_empty_string():
    results = find_similar_scams("")
    assert len(results) == 0
    
    score = get_max_semantic_score("")
    assert score == 0.0
