import os

import torch
from dotenv import load_dotenv

from src.sentiment.model_loader import model_loader


load_dotenv()


MODEL_VERSION = os.getenv(
    "MODEL_VERSION",
    "1.0.0"
)


LABELS = {
    0: "NEGATIVE",
    1: "NEUTRAL",
    2: "POSITIVE"
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


        scores = (
            probabilities
            .squeeze()
            .tolist()
        )


        # ---------------------------------------
        # Result
        # ---------------------------------------

        return {

            "post_id": post_id,

            "prediction": LABELS[
                prediction.item()
            ],

            "confidence": round(
                confidence.item() * 100,
                2
            ),

            "negative_score": round(
                scores[0] * 100,
                2
            ),

            "neutral_score": round(
                scores[1] * 100,
                2
            ),

            "positive_score": round(
                scores[2] * 100,
                2
            ),

            "model_version": MODEL_VERSION
        }


sentiment_service = SentimentService()