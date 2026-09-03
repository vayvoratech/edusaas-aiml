from pathlib import Path

import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
)


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = Path("models/toxicity")


class ToxicityModelLoader:
    """
    Loads the trained DistilBERT toxicity model and tokenizer.
    """

    def __init__(self, model_path=MODEL_PATH):

        self.model_path = Path(model_path)

        self.tokenizer = None
        self.model = None

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    def load(self):

        if not self.model_path.exists():

            raise FileNotFoundError(
                f"Toxicity model not found at: "
                f"{self.model_path}"
            )

        print(
            f"Loading toxicity model from: "
            f"{self.model_path}"
        )

        # ----------------------------------------------------
        # Load tokenizer
        # ----------------------------------------------------

        self.tokenizer = (
            DistilBertTokenizerFast.from_pretrained(
                self.model_path
            )
        )

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------

        self.model = (
            DistilBertForSequenceClassification.from_pretrained(
                self.model_path
            )
        )

        # ----------------------------------------------------
        # Move model to available device
        # ----------------------------------------------------

        self.model.to(
            self.device
        )

        # ----------------------------------------------------
        # Evaluation mode
        # ----------------------------------------------------

        self.model.eval()

        print(
            f"Toxicity model loaded on: "
            f"{self.device}"
        )

        return self

    def predict(self, text):

        if self.model is None or self.tokenizer is None:

            raise RuntimeError(
                "Model is not loaded. "
                "Call load() first."
            )

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        probabilities = torch.sigmoid(
            outputs.logits
        )

        return probabilities.cpu().numpy()[0]