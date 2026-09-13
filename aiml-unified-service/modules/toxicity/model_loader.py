from pathlib import Path
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
)

# ============================================================
# Dynamic Candidate Path Resolution
# ============================================================

current_dir = Path(__file__).resolve().parent

# Candidates to check for the models/toxicity directory
toxicity_candidates = [
    current_dir.parent.parent / "models" / "toxicity",  # Repo root (../../models/toxicity)
    Path("/app/models/toxicity"),                       # Docker/Render default root (/app)
    Path("models/toxicity").resolve(),                  # CWD relative (current terminal root)
    current_dir / "models" / "toxicity",                # Local subfolder (modules/toxicity/models/toxicity)
    current_dir / "toxicity",                           # Local toxicity folder
    current_dir.parent / "models" / "toxicity",         # One level up (../models/toxicity)
]

# Pick the first directory that actually contains the model config or exists
MODEL_PATH = next(
    (p for p in toxicity_candidates if (p / "config.json").is_file() or p.is_dir()),
    toxicity_candidates[0]
)


class ToxicityModelLoader:
    """
    Loads the trained DistilBERT toxicity model and tokenizer.
    """

    def __init__(self, model_path=MODEL_PATH):
        self.model_path = Path(model_path)
        self.tokenizer = None
        self.model = None

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print("\n" + "=" * 55)
        print("TOXICITY MODEL LOADER: PATH RESOLUTION")
        print("=" * 55)
        print(f"Target Directory : {self.model_path} (exists: {self.model_path.is_dir()})")
        print(f"Inference Device : {self.device}")
        print("=" * 55 + "\n")

    def load(self):
        if not self.model_path.is_dir():
            raise FileNotFoundError(
                f"Toxicity model directory not found at: {self.model_path}"
            )

        # from_pretrained requires a string path in several Transformers versions
        model_path_str = str(self.model_path)

        print(f"Loading toxicity model from: {model_path_str}")

        # ----------------------------------------------------
        # Load tokenizer
        # ----------------------------------------------------
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(
            model_path_str
        )

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------
        self.model = DistilBertForSequenceClassification.from_pretrained(
            model_path_str
        )

        # ----------------------------------------------------
        # Move model to available device
        # ----------------------------------------------------
        self.model.to(self.device)

        # ----------------------------------------------------
        # Evaluation mode
        # ----------------------------------------------------
        self.model.eval()

        print(f"Toxicity model loaded successfully on: {self.device}")
        return self

    def predict(self, text):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError(
                "Model is not loaded. Call load() first."
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
            outputs = self.model(**inputs)

        probabilities = torch.sigmoid(
            outputs.logits
        )

        return probabilities.cpu().numpy()[0]