"""Nirnaya Agent Tools.

Wraps the existing deterministic and ML-based intelligence layers
into callable functions for the LangGraph orchestrator.
"""

import logging
from typing import Dict, List, Any

from app.services.fraud_signals import extract_entities, extract_fraud_signals
from app.ml.text_classifier import predict_fraud_probability
from app.ml.semantic_engine import find_similar_scams
from app.services.rag_engine import retrieve_knowledge

logger = logging.getLogger(__name__)

def run_evidence_gathering(text: str) -> Dict[str, Any]:
    """Runs all evidence gathering modules on the text.
    
    This is called by the GatherEvidence node in the LangGraph.
    It executes the regex extractors, text classifier, semantic search,
    and RAG retrieval in a single pass to populate the state.
    """
    logger.info("Gathering evidence for text analysis...")
    
    # 1. Deterministic Signals
    entities = extract_entities(text)
    signals = extract_fraud_signals(text, entities)
    signals_dict = signals.model_dump()
    
    # 2. ML Probability
    ml_prob = predict_fraud_probability(text)
    
    # 3. Semantic Matches
    similar_scams = find_similar_scams(text, top_k=2)
    
    # 4. RAG Guidelines (only if there are strong fraud signals or high ML prob)
    # This saves time and token space for clearly legitimate messages
    rag_context = ""
    if ml_prob > 0.4 or any(signals_dict.values()):
        # Generate a query based on the text
        query = "fraud patterns"
        if "kyc" in text.lower():
            query = "kyc guidelines"
        elif "otp" in text.lower() or "pin" in text.lower():
            query = "otp sharing liability"
        elif "app" in text.lower() or "download" in text.lower():
            query = "remote access app screen sharing"
            
        rag_context = retrieve_knowledge(query)
        
    return {
        "rule_signals": signals_dict,
        "ml_score": ml_prob,
        "semantic_matches": similar_scams,
        "rag_context": rag_context
    }


def calculate_final_risk(rule_signals: Dict[str, bool], ml_score: float, semantic_matches: List[Dict]) -> Dict[str, Any]:
    """Fuses the evidence into a final risk score and policy action."""
    logger.info("Calculating final risk score...")
    
    from app.schemas import FraudSignals
    from app.services.risk_engine import calculate_signal_score, determine_policy_action
    
    # Calculate base rule score
    signals_model = FraudSignals(**rule_signals)
    rule_score = calculate_signal_score(signals_model)
    
    # Simple Fusion: weighted average
    # We trust ML more if it's high, but if rules catch something explicit, we boost it.
    semantic_score = semantic_matches[0]["similarity"] if semantic_matches else 0.0
    
    # Weights
    w_rule = 0.4
    w_ml = 0.4
    w_sem = 0.2
    
    final_score = (rule_score * w_rule) + (ml_score * w_ml) + (semantic_score * w_sem)
    
    # Cap at 1.0
    final_score = min(1.0, final_score)
    
    from app.services.risk_engine import classify_risk_level
    risk_level = classify_risk_level(final_score)
    action, _ = determine_policy_action(risk_level, final_score)
    
    return {
        "final_risk_score": final_score,
        "policy_action": action.value
    }
