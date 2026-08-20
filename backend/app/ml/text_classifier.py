"""Nirnaya Text Classifier Inference Wrapper.

Loads the trained TF-IDF + Logistic Regression model and provides
a simple API for scoring text.
"""

import logging
from pathlib import Path

import joblib

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "fraud_text_model_v1.joblib"

_model = None

def get_model():
    """Lazy load the trained model."""
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            logger.warning(f"Model not found at {MODEL_PATH}. Returning 0.0 scores.")
            return None
        _model = joblib.load(MODEL_PATH)
        logger.info("Loaded TF-IDF fraud text model.")
    return _model


def predict_fraud_probability(text: str) -> float:
    """Predict the probability that the given text is a scam.
    
    Args:
        text: The message content
        
    Returns:
        float: Probability [0.0, 1.0]
    """
    if not text:
        return 0.0
        
    model = get_model()
    if model is None:
        return 0.0
        
    try:
        # predict_proba returns [[P(Legit), P(Scam)]]
        prob = model.predict_proba([text])[0][1]
        return float(prob)
    except Exception as e:
        logger.error(f"Text classification failed: {e}", exc_info=True)
        return 0.0
