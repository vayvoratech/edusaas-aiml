from pathlib import Path
import gc
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ============================================================
# Dynamic Candidate Path Resolution
# ============================================================

current_dir = Path(__file__).resolve().parent

toxicity_candidates = [
    current_dir.parent.parent / "models" / "toxicity",
    Path("/app/models/toxicity"),
    Path("models/toxicity").resolve(),
    current_dir / "models" / "toxicity",
    current_dir / "toxicity",
    current_dir.parent / "models" / "toxicity",
]

DEFAULT_MODEL_PATH = next(
    (p for p in toxicity_candidates if (p / "config.json").is_file() or p.is_dir()),
    toxicity_candidates[0]
)


class ToxicityModelLoader:
    """
    Loads the trained toxicity model with memory-safe loading for 512MB RAM containers.
    """

    def __init__(self, model_path=None):
        self.model_path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu")

    def load(self):
        if self.model is not None and self.tokenizer is not None:
            return self

        if not self.model_path.is_dir():
            raise FileNotFoundError(
                f"Toxicity model directory not found at: {self.model_path}"
            )

        model_path_str = str(self.model_path)
        print(f"Loading toxicity tokenizer and model from: {model_path_str}")

        # Clean up memory before loading
        gc.collect()

        self.tokenizer = AutoTokenizer.from_pretrained(model_path_str)

        # low_cpu_mem_usage avoids creating double-buffered copies of weights in RAM
        raw_model = AutoModelForSequenceClassification.from_pretrained(
            model_path_str,
            low_cpu_mem_usage=True
        )
        raw_model.to(self.device)
        raw_model.eval()

        # Immediately convert linear layers to 8-bit ints
        try:
            self.model = torch.quantization.quantize_dynamic(
                raw_model, {torch.nn.Linear}, dtype=torch.qint8
            )
            del raw_model
            gc.collect()
            print("Applied dynamic 8-bit quantization (qint8) to Toxicity Model.")
        except Exception as e:
            print(f"Quantization fallback: {e}")
            self.model = raw_model

        print(f"Toxicity model loaded successfully on: {self.device}")
        return self

    def predict(self, text: str):
        if self.model is None or self.tokenizer is None:
            self.load()

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,  # Truncate to 128 tokens to reduce tensor memory
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.sigmoid(outputs.logits)
        return probabilities.cpu().numpy()[0]