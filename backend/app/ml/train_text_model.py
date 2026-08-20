"""Nirnaya Text Classifier Training Script.

Trains a TF-IDF + Logistic Regression model on the augmented dataset.
Evaluates performance and saves the model artifact.
"""

import os
import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "augmented_dataset.jsonl"
MODELS_DIR = BASE_DIR / "models"


def load_dataset() -> pd.DataFrame:
    """Load augmented dataset from JSONL."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Run augment_dataset.py first.")
        
    records = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line.strip()))
            
    df = pd.DataFrame(records)
    logger.info(f"Loaded {len(df)} records from {DATA_PATH}")
    logger.info(f"Class distribution:\n{df['label'].value_counts(normalize=True)}")
    return df


def train_and_evaluate(df: pd.DataFrame):
    """Train the model and print evaluation metrics."""
    # We want a model that is fast, explainable, and calibrates well to probabilities.
    # TF-IDF + LogisticRegression is the standard baseline that often outperforms small LLMs
    # on constrained tasks like this, and is 1000x faster.
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )),
        ('clf', LogisticRegression(
            class_weight='balanced',
            C=1.0,
            solver='liblinear',
            random_state=42
        ))
    ])
    
    X = df['text']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    logger.info(f"Accuracy: {acc:.4f}")
    logger.info(f"ROC AUC:  {auc:.4f}")
    logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=['Legitimate', 'Scam'])}")
    
    return pipeline


def save_model(model: Pipeline):
    """Save the trained pipeline to disk."""
    MODELS_DIR.mkdir(exist_ok=True)
    model_path = MODELS_DIR / "fraud_text_model_v1.joblib"
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")


def main():
    logger.info("Starting text model training pipeline...")
    df = load_dataset()
    model = train_and_evaluate(df)
    save_model(model)
    logger.info("Training pipeline complete.")


if __name__ == "__main__":
    main()
