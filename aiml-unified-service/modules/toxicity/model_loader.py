from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ============================================================
# Dynamic Candidate Path Resolution
# ============================================================

current_dir = Path(__file__).resolve().parent

toxicity_candidates = [
    current_dir.parent.parent / "models" / "toxicity",  # Repo root (../../models/toxicity)
    Path("/app/models/toxicity"),                       # Docker/Render default root (/app)
    Path("models/toxicity").resolve(),                  # CWD relative (current terminal root)
    current_dir / "models" / "toxicity",                # Local subfolder (src/toxicity/models/toxicity)
    current_dir / "toxicity",                           # Local toxicity folder
    current_dir.parent / "models" / "toxicity",         # One level up (../models/toxicity)
]

DEFAULT_MODEL_PATH = next(
    (p for p in toxicity_candidates if (p / "config.json").is_file() or p.is_dir()),
    toxicity_candidates[0]
)


class ToxicityModelLoader:
    """
    Loads the trained toxicity model and tokenizer with dynamic quantization for low-RAM limits.
    """

    def __init__(self, model_path=None):
        # Fallback to dynamic candidate if None is passed
        self.model_path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH
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

        model_path_str = str(self.model_path)
        print(f"Loading tokenizer and model from: {model_path_str}")

        # AutoTokenizer and AutoModel automatically resolve the architecture from config.json
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_str)
        raw_model = AutoModelForSequenceClassification.from_pretrained(model_path_str)

        raw_model.to(self.device)
        raw_model.eval()

        # Dynamic quantization for Render 512MB RAM optimization
        if self.device.type == "cpu":
            try:
                self.model = torch.quantization.quantize_dynamic(
                    raw_model, {torch.nn.Linear}, dtype=torch.qint8
                )
                print("Applied dynamic 8-bit quantization (qint8).")
            except Exception as e:
                print(f"Quantization fallback: {e}")
                self.model = raw_model
        else:
            self.model = raw_model

        print(f"Toxicity model loaded successfully on: {self.device}")
        return self

    def predict(self, text: str):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model is not loaded. Call load() first.")

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        )

        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Multi-label probability via Sigmoid activation
        probabilities = torch.sigmoid(outputs.logits)
        return probabilities.cpu().numpy()[0]