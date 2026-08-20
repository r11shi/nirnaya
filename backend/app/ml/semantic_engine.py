"""Nirnaya Semantic Scam Retrieval Engine.

Embeds known scam messages using SentenceTransformers and indexes
them in FAISS for fast similarity search.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "augmented_dataset.jsonl"
INDEX_DIR = BASE_DIR / "models"
INDEX_PATH = INDEX_DIR / "scam_faiss.index"
METADATA_PATH = INDEX_DIR / "scam_metadata.json"

MODEL_NAME = 'all-MiniLM-L6-v2'

_model = None
_index = None
_metadata = None


def get_model():
    global _model
    if _model is None:
        logger.info(f"Loading SentenceTransformer: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _build_index():
    """Build the FAISS index from the augmented dataset."""
    if not DATA_PATH.exists():
        logger.warning(f"Cannot build semantic index, {DATA_PATH} not found.")
        return False
        
    logger.info("Building semantic scam index...")
    scam_texts = []
    scam_categories = []
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line.strip())
            if record["label"] == 1:  # Only index scams
                scam_texts.append(record["text"])
                scam_categories.append(record["category"])
                
    if not scam_texts:
        logger.warning("No scam records found to index.")
        return False
        
    model = get_model()
    embeddings = model.encode(scam_texts, convert_to_numpy=True, show_progress_bar=False)
    
    # L2 normalized vectors for Cosine Similarity via Inner Product
    faiss.normalize_L2(embeddings)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    INDEX_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump({"texts": scam_texts, "categories": scam_categories}, f)
        
    logger.info(f"Successfully built and saved FAISS index with {len(scam_texts)} scams.")
    return True


def load_index():
    """Load the FAISS index and metadata into memory."""
    global _index, _metadata
    
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        success = _build_index()
        if not success:
            return False
            
    if _index is None:
        _index = faiss.read_index(str(INDEX_PATH))
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
        logger.info("Loaded FAISS semantic scam index.")
        
    return True


def find_similar_scams(text: str, top_k: int = 3) -> List[Dict]:
    """Find known scams semantically similar to the input text.
    
    Returns:
        List of dicts containing 'text', 'category', and 'similarity' score [0, 1]
    """
    if not text or not load_index():
        return []
        
    model = get_model()
    query_vector = model.encode([text], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    
    similarities, indices = _index.search(query_vector, top_k)
    
    results = []
    for i in range(top_k):
        idx = int(indices[0][i])
        score = float(similarities[0][i])
        
        if idx != -1:  # -1 means not enough results
            results.append({
                "text": _metadata["texts"][idx],
                "category": _metadata["categories"][idx],
                "similarity": max(0.0, score)  # Clamp lower bound
            })
            
    return results


def get_max_semantic_score(text: str) -> float:
    """Convenience function returning just the top similarity score."""
    results = find_similar_scams(text, top_k=1)
    if results:
        return results[0]["similarity"]
    return 0.0

if __name__ == "__main__":
    # Test script if run directly
    _build_index()
    test_msg = "Your bank a/c is blocked. Complete KYC at this link urgently."
    res = find_similar_scams(test_msg)
    print(f"\nQuery: {test_msg}")
    for i, r in enumerate(res):
        print(f"[{i+1}] Score {r['similarity']:.3f} | {r['category']} | {r['text']}")
