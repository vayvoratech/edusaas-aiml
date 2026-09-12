from pathlib import Path
from transformers import (
    AutoTokenizer,
    DistilBertForSequenceClassification
)
import torch


# ==========================================
# Dynamic Candidate Path Resolution
# ==========================================

current_dir = Path(__file__).resolve().parent

# Check potential locations where models/sentiment might reside
sentiment_candidates = [
    current_dir.parent.parent / "models" / "sentiment",  # Root project models/sentiment
    Path("/app/models/sentiment"),                       # Container root /app/models/sentiment
    Path("models/sentiment"),                            # Working directory relative
    current_dir / "models" / "sentiment",                # Module local models/sentiment
    current_dir / "sentiment",                           # Direct subfolder sentiment
]

# Pick the first existing candidate folder, otherwise fallback to standard default
MODEL_PATH = next(
    (p for p in sentiment_candidates if p.is_dir()), 
    sentiment_candidates[0]
)

print("\n" + "=" * 55)
print("SENTIMENT SERVICE: PATH RESOLUTION")
print("=" * 55)
print(f"Target Directory : {MODEL_PATH} (exists: {MODEL_PATH.is_dir()})")
print("=" * 55 + "\n")


# ==========================================
# Model Loader Singleton
# ==========================================

class SentimentModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tokenizer = None
            cls._instance.model = None

            if not MODEL_PATH.is_dir():
                print(f"[SentimentModel ERROR] Directory not found: {MODEL_PATH}")
                return cls._instance

            try:
                # String conversion is required for HuggingFace from_pretrained
                model_path_str = str(MODEL_PATH)

                cls._instance.tokenizer = AutoTokenizer.from_pretrained(
                    model_path_str
                )

                cls._instance.model = DistilBertForSequenceClassification.from_pretrained(
                    model_path_str
                )

                cls._instance.model.eval()
                print("Sentiment DistilBERT model and tokenizer loaded successfully.")
            except Exception as e:
                print(f"[SentimentModel ERROR] Failed to load model weights: {e}")

        return cls._instance


model_loader = SentimentModel()