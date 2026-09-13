import numpy as np

from modules.toxicity.model_loader import ToxicityModelLoader
from modules.toxicity.preprocessing import clean_text

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
    Handles toxicity prediction across 6 Jigsaw multi-label categories.
    """

    def __init__(self, model_path=None, threshold=THRESHOLD):
        self.threshold = threshold
        self.loader = ToxicityModelLoader(model_path=model_path)
        self.loader.load()

    def predict(self, text: str):
        if text is None:
            raise ValueError("Text cannot be None.")

        text = str(text).strip()
        if not text:
            raise ValueError("Text cannot be empty.")

        cleaned_text = clean_text(text)
        if not cleaned_text:
            raise ValueError("Text became empty after preprocessing.")

        raw_probs = self.loader.predict(cleaned_text)
        probabilities = np.asarray(raw_probs, dtype=float)

        predictions = (probabilities >= self.threshold).astype(int)

        label_results = {}
        for index, label in enumerate(LABELS):
            label_results[label] = {
                "prediction": int(predictions[index]),
                "probability": round(float(probabilities[index]), 4),
            }

        # Considered toxic if ANY category triggers
        is_toxic = bool(np.any(predictions == 1))
        # Headline score is the maximum probability across all 6 labels
        max_score = float(np.max(probabilities))

        return {
            "text": text,
            "cleaned_text": cleaned_text,
            "is_toxic": is_toxic,
            "toxicity_score": round(max_score, 4),
            "labels": label_results,
            "threshold": self.threshold,
        }


if __name__ == "__main__":
    predictor = ToxicityPredictor()
    test_result = predictor.predict("You are an idiot and I hate you.")
    print(test_result)