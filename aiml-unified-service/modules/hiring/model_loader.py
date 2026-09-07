from pathlib import Path
import joblib

# ============================================================
# Dynamic Model Directory Resolution
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

# Check candidate directories across repo root, subdirectories, and container /app
CANDIDATE_DIRS = [
    CURRENT_DIR.parent.parent / "models" / "hiring",  # aiml-unified-service/models/hiring
    CURRENT_DIR.parent.parent / "models",             # aiml-unified-service/models
    Path("/app/models/hiring"),                       # Docker subfolder
    Path("/app/models"),                              # Docker root models directory
    Path("models/hiring"),                            # Working directory relative subfolder
    Path("models"),                                   # Working directory relative
]

# Locate the directory containing the hiring model artifacts
MODEL_DIR = next(
    (d for d in CANDIDATE_DIRS if (d / "hiring_random_forest.pkl").is_file()),
    None
)

if MODEL_DIR is None:
    raise FileNotFoundError(
        "Predictive Hiring model artifacts not found. "
        f"Searched paths: {[str(d) for d in CANDIDATE_DIRS]}"
    )

MODEL_PATH = MODEL_DIR / "hiring_random_forest.pkl"
FEATURES_PATH = MODEL_DIR / "hiring_feature_columns.pkl"


# ============================================================
# Model Loader Class
# ============================================================

class HiringModelLoader:
    """
    Load trained Predictive Hiring model and expected feature columns.
    """

    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.load_models()

    def load_models(self):
        print(f"\nLoading Predictive Hiring Model from: {MODEL_DIR}")

        self.model = joblib.load(MODEL_PATH)
        self.feature_columns = joblib.load(FEATURES_PATH)

        print("Predictive Hiring Model Loaded Successfully")
        print(f"Features: {self.feature_columns}")


hiring_model_loader = HiringModelLoader()