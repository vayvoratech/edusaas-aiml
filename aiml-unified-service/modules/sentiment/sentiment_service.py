import os
import torch
from dotenv import load_dotenv

from modules.sentiment.model_loader import model_loader


load_dotenv()


MODEL_VERSION = os.getenv(
    "MODEL_VERSION",
    "1.0.0"
)

# 3-Class Mapping
LABELS_3 = {
    0: "NEGATIVE",
    1: "NEUTRAL",
    2: "POSITIVE"
}

# 2-Class Fallback Mapping (Standard SST-2 / Binary)
LABELS_2 = {
    0: "NEGATIVE",
    1: "POSITIVE"
}


class SentimentService:

    def __init__(self):
        self.model = model_loader.model
        self.tokenizer = model_loader.tokenizer

    def predict(
        self,
        post_id,
        post_text
    ):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Sentiment model or tokenizer is not loaded.")

        # ---------------------------------------
        # Tokenization
        # ---------------------------------------
        encoding = self.tokenizer(
            post_text,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        # ---------------------------------------
        # Model Inference
        # ---------------------------------------
        with torch.no_grad():
            outputs = self.model(
                **encoding
            )

        # ---------------------------------------
        # Probabilities
        # ---------------------------------------
        probabilities = torch.softmax(
            outputs.logits,
            dim=1
        )

        # ---------------------------------------
        # Prediction
        # ---------------------------------------
        confidence, prediction = torch.max(
            probabilities,
            dim=1
        )

        # Use batch index 0 instead of .squeeze() to prevent scalar reduction
        scores = probabilities[0].tolist()
        num_classes = len(scores)

        # ---------------------------------------
        # Dynamic Class Output Resolution
        # ---------------------------------------
        if num_classes >= 3:
            prediction_label = LABELS_3.get(
                prediction.item(), 
                "UNKNOWN"
            )
            neg_score = round(scores[0] * 100, 2)
            neu_score = round(scores[1] * 100, 2)
            pos_score = round(scores[2] * 100, 2)
        else:
            prediction_label = LABELS_2.get(
                prediction.item(), 
                "UNKNOWN"
            )
            neg_score = round(scores[0] * 100, 2)
            neu_score = 0.0
            pos_score = round(scores[1] * 100, 2)

        # ---------------------------------------
        # Result
        # ---------------------------------------
        return {
            "post_id": post_id,
            "prediction": prediction_label,
            "confidence": round(
                confidence.item() * 100,
                2
            ),
            "negative_score": neg_score,
            "neutral_score": neu_score,
            "positive_score": pos_score,
            "model_version": MODEL_VERSION
        }


sentiment_service = SentimentService()