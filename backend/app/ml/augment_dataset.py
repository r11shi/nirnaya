"""Nirnaya Dataset Augmentation Script.

Generates hundreds of synthetic variations from our core templates
by swapping entities (banks, amounts, URLs, phones) to create a 
sufficiently large dataset for TF-IDF training and FAISS indexing.
"""

import os
import json
import random
import re
from pathlib import Path

# Need to append backend to path if run directly
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ml.dataset import SCAM_MESSAGES, LEGITIMATE_MESSAGES, MessageCategory, LabeledMessage

BANKS = ["SBI", "HDFC", "ICICI", "Axis Bank", "Kotak", "PNB", "Bank of Baroda", "Union Bank", "Yes Bank", "IndusInd"]
AUTHORITIES = ["RBI", "Income Tax Dept", "UIDAI", "Cyber Police", "TRAI", "NPCI"]
URLS = [
    "http://{bank}-update.tk", "https://{bank}-kyc.in", "http://update-pan-{bank}.xyz",
    "http://bit.ly/kyc-{bank}", "https://tinyurl.com/{bank}-verify", "http://{bank}-support.co"
]
PHONES = ["9876543210", "8899776655", "7766554433", "9988776655", "8877665544", "1800111222", "1800222333"]
AMOUNTS = ["500", "1,500", "5,000", "10,000", "25,000", "50,000", "1,00,000", "2,50,000"]
DATES = ["24 hours", "12 hours", "today", "tomorrow", "tonight at 8 PM"]


def augment_scams(num_variations: int = 15) -> list[LabeledMessage]:
    """Generate variations of scam messages."""
    augmented = []
    
    # regex patterns for easy swapping
    bank_pattern = re.compile(r'\b(SBI|HDFC|ICICI|Axis|PNB|Kotak|UBI)\b', re.IGNORECASE)
    phone_pattern = re.compile(r'\b\d{10}\b')
    amount_pattern = re.compile(r'(?:Rs\.?|₹)\s*([\d,]+)')
    
    for base in SCAM_MESSAGES:
        augmented.append(base)  # keep original
        
        for _ in range(num_variations):
            text = base.text
            
            # Swap Bank
            if bank_pattern.search(text):
                new_bank = random.choice(BANKS)
                text = bank_pattern.sub(new_bank, text)
                
            # Swap Phone
            if phone_pattern.search(text):
                text = phone_pattern.sub(random.choice(PHONES), text)
                
            # Swap Amount
            if amount_pattern.search(text):
                text = amount_pattern.sub(f"Rs.{random.choice(AMOUNTS)}", text)
                
            # Swap URLs specifically for scams
            # Simple heuristic: find http* and replace
            text = re.sub(r'https?://[^\s]+', random.choice(URLS).format(bank=random.choice(BANKS).lower().replace(" ", "")), text)
            
            augmented.append(LabeledMessage(
                text=text,
                is_scam=base.is_scam,
                category=base.category,
                tags=base.tags.copy()
            ))
            
    return augmented

def augment_legit(num_variations: int = 15) -> list[LabeledMessage]:
    """Generate variations of legitimate messages."""
    augmented = []
    
    bank_pattern = re.compile(r'\b(SBI|HDFC|ICICI|Axis|PNB|Kotak|UBI)\b', re.IGNORECASE)
    amount_pattern = re.compile(r'(?:Rs\.?|₹)\s*([\d,]+(?:\.\d{2})?)')
    
    for base in LEGITIMATE_MESSAGES:
        augmented.append(base)
        
        for _ in range(num_variations):
            text = base.text
            
            # Swap Bank
            if bank_pattern.search(text):
                new_bank = random.choice(BANKS)
                text = bank_pattern.sub(new_bank, text)
                
            # Swap Amount
            if amount_pattern.search(text):
                text = amount_pattern.sub(f"Rs.{random.choice(AMOUNTS)}.00", text)
                
            augmented.append(LabeledMessage(
                text=text,
                is_scam=base.is_scam,
                category=base.category,
                tags=base.tags.copy()
            ))
            
    return augmented


if __name__ == "__main__":
    print("Augmenting Dataset...")
    scams = augment_scams(15)
    legits = augment_legit(15)
    
    total = scams + legits
    random.shuffle(total)
    
    # Save to JSONL
    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "augmented_dataset.jsonl"
    
    with open(out_path, "w", encoding="utf-8") as f:
        for msg in total:
            f.write(json.dumps({
                "text": msg.text,
                "label": 1 if msg.is_scam else 0,
                "category": msg.category.value,
                "tags": msg.tags
            }) + "\n")
            
    print(f"Original size: {len(SCAM_MESSAGES) + len(LEGITIMATE_MESSAGES)}")
    print(f"Augmented size: {len(total)} ({len(scams)} scams, {len(legits)} legits)")
    print(f"Saved to {out_path}")
