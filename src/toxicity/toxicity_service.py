import torch

from src.logs.logger import logger
from src.toxicity.model_loader import model_loader
from src.toxicity.toxicity_repository import toxicity_repository


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
    Business logic for Toxicity Detection.
    """

    def __init__(self):

        self.model = model_loader.model

        self.tokenizer = model_loader.tokenizer


    def predict(
        self,
        student_id: int,
        discussion_id: int,
        post_text: str
    ):

        try:

            logger.info(
                f"Predicting toxicity for Student ID: {student_id}"
            )

            encoding = self.tokenizer(

                post_text,

                return_tensors="pt",

                truncation=True,

                padding=True,

                max_length=256

            )

            with torch.no_grad():

                outputs = self.model(**encoding)

            probabilities = torch.sigmoid(
                outputs.logits
            ).squeeze()

            scores = probabilities.tolist()

            predictions = []

            for index, score in enumerate(scores):

                if score >= 0.50:

                    predictions.append(

                        {

                            "label": LABELS[index],

                            "confidence": round(
                                score * 100,
                                2
                            )

                        }

                    )

            if not predictions:

                predictions.append(

                    {

                        "label": "NON_TOXIC",

                        "confidence": round(

                            (1 - max(scores)) * 100,

                            2

                        )

                    }

                )

            toxicity_repository.save_prediction(

                student_id=student_id,

                discussion_id=discussion_id,

                post_text=post_text,

                predictions=predictions

            )

            logger.info(
                "Toxicity prediction completed successfully."
            )

            return {

                "student_id": student_id,

                "discussion_id": discussion_id,

                "post_text": post_text,

                "predictions": predictions

            }

        except Exception:

            logger.exception(
                "Toxicity prediction failed."
            )

            raise


toxicity_service = ToxicityService()