import torch

from src.sentiment.model_loader import model_loader
from src.database.sentiment_repository import repository


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
        student_id,
        course_id,
        discussion_id,
        post_text
    ):

        encoding = self.tokenizer(
            post_text,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**encoding)

        probabilities = torch.softmax(
            outputs.logits,
            dim=1
        )

        confidence, prediction = torch.max(
            probabilities,
            dim=1
        )

        scores = probabilities.squeeze().tolist()

        result = {
            "student_id": student_id,
            "course_id": course_id,
            "discussion_id": discussion_id,
            "post_text": post_text,
            "prediction": LABELS[prediction.item()],
            "confidence": round(confidence.item() * 100, 2),
            "scores": {
                "negative": round(scores[0] * 100, 2),
                "neutral": round(scores[1] * 100, 2),
                "positive": round(scores[2] * 100, 2)
            }
        }

        repository.save_prediction(
            student_id,
            course_id,
            discussion_id,
            post_text,
            result["prediction"],
            result["confidence"],
            result["scores"]["negative"],
            result["scores"]["neutral"],
            result["scores"]["positive"]
        )

        return result


sentiment_service = SentimentService()