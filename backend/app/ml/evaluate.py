"""Nirnaya ML Evaluation Script."""
import joblib
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import os

def evaluate_model():
    model_path = "e:/SIH/nirnaya/backend/app/ml/models/fraud_text_model_v1.joblib"
    dataset_path = "e:/SIH/nirnaya/backend/app/ml/data/augmented_dataset.jsonl"
    
    if not os.path.exists(model_path) or not os.path.exists(dataset_path):
        print(f"Model or dataset not found. {model_path} | {dataset_path}")
        return
        
    print("Loading model and dataset...")
    clf = joblib.load(model_path)
    
    records = []
    import json
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line.strip()))
    df = pd.DataFrame(records)
    
    # Simple split to just run it on the whole set (for this prototype eval)
    # Ideally we'd have a held-out test set, but we trained on augmented data
    X = df["text"]
    y_true = df["label"]
    
    print("Running predictions...")
    y_pred = clf.predict(X)
    
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Legitimate", "Scam"]))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_true, y_pred)
    print(f"True Negatives (Legit->Legit): {cm[0][0]}")
    print(f"False Positives (Legit->Scam): {cm[0][1]}")
    print(f"False Negatives (Scam->Legit): {cm[1][0]}")
    print(f"True Positives (Scam->Scam): {cm[1][1]}")

if __name__ == "__main__":
    evaluate_model()
