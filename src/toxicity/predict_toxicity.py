import numpy as np

from src.toxicity.model_loader import ToxicityModelLoader
from src.toxicity.preprocessing import clean_text


LABELS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]

THRESHOLD = 0.5


class ToxicityPredictor:
    """
    Handles toxicity prediction using the trained
    multi-label DistilBERT model.
    """

    def __init__(
        self,
        model_path="models/toxicity",
        threshold=THRESHOLD,
    ):

        self.threshold = threshold

        self.loader = ToxicityModelLoader(
            model_path=model_path
        )

        self.loader.load()

    def predict(self, text):
        """
        Predict toxicity labels for a single text.
        """

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if text is None:

            raise ValueError(
                "Text cannot be None."
            )

        text = str(text).strip()

        if not text:

            raise ValueError(
                "Text cannot be empty."
            )

        # ----------------------------------------------------
        # IMPORTANT:
        # Use exactly the same preprocessing as training.
        # ----------------------------------------------------

        cleaned_text = clean_text(
            text
        )

        if not cleaned_text:

            raise ValueError(
                "Text became empty after preprocessing."
            )

        # ----------------------------------------------------
        # Model prediction
        # ----------------------------------------------------

        probabilities = self.loader.predict(
            cleaned_text
        )

        probabilities = np.asarray(
            probabilities,
            dtype=float,
        )

        # ----------------------------------------------------
        # Convert probabilities to predictions
        # ----------------------------------------------------

        predictions = (
            probabilities >= self.threshold
        ).astype(int)

        # ----------------------------------------------------
        # Build result
        # ----------------------------------------------------

        label_results = {}

        for index, label in enumerate(LABELS):

            label_results[label] = {
                "prediction": int(
                    predictions[index]
                ),
                "probability": float(
                    probabilities[index]
                ),
            }

        # ----------------------------------------------------
        # Overall toxicity
        # ----------------------------------------------------

        toxic_probability = float(
            probabilities[0]
        )

        is_toxic = (
            toxic_probability >= self.threshold
        )

        return {
            "text": text,

            "cleaned_text": cleaned_text,

            "is_toxic": bool(
                is_toxic
            ),

            "toxicity_score": toxic_probability,

            "labels": label_results,

            "threshold": self.threshold,
        }


# ------------------------------------------------------------
# Local execution
# ------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Toxicity predictor module loaded."
    )

    print(
        "A trained model is required to run prediction."
    )