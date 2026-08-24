import torch

from src.toxicity.model_loader import model_loader


LABELS = [
    "TOXIC",
    "SEVERE_TOXIC",
    "OBSCENE",
    "THREAT",
    "INSULT",
    "IDENTITY_HATE"
]


class ToxicityService:
    """
    Toxicity Detection Inference Service.

    Uses the pre-trained DistilBERT model.
    Database persistence is handled by Node.
    """

    def __init__(self):

        self.model = model_loader.model
        self.tokenizer = model_loader.tokenizer

    def predict(
        self,
        student_id: str,
        discussion_id: str,
        post_text: str
    ):

        try:

            encoding = self.tokenizer(
                post_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=256
            )

            with torch.no_grad():

                outputs = self.model(
                    **encoding
                )

            probabilities = torch.sigmoid(
                outputs.logits
            ).squeeze()

            scores = probabilities.tolist()

            predictions = []

            for index, score in enumerate(scores):

                if score >= 0.50:

                    predictions.append({
                        "label": LABELS[index],
                        "confidence": round(
                            score * 100,
                            2
                        )
                    })

            if not predictions:

                predictions.append({
                    "label": "NON_TOXIC",
                    "confidence": round(
                        (1 - max(scores)) * 100,
                        2
                    )
                })

            return {
                "student_id": student_id,
                "discussion_id": discussion_id,
                "post_text": post_text,
                "predictions": predictions
            }

        except Exception as e:

            print(
                f"Toxicity Prediction Failed: {e}"
            )

            raise


toxicity_service = ToxicityService()