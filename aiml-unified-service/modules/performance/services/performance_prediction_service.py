import os
from pathlib import Path
import joblib
import pandas as pd


# ==========================================
# Dynamic Candidate Path Resolution
# ==========================================

current_dir = Path(__file__).resolve().parent

# Candidates for models and encoder
xgb_candidates = [
    current_dir.parent.parent / "models" / "xgboost_model.pkl",      # Root /models/
    Path("/app/models/xgboost_model.pkl"),                           # Container root /app/models/
    Path("models/xgboost_model.pkl"),                                # CWD /models/
    current_dir / "models" / "xgboost_model.pkl",                    # Subfolder ./models/
    current_dir / "xgboost_model.pkl",                               # Same directory
]
XGBOOST_MODEL_PATH = next((p for p in xgb_candidates if p.is_file()), xgb_candidates[0])

rf_candidates = [
    current_dir.parent.parent / "models" / "random_forest_model.pkl",
    Path("/app/models/random_forest_model.pkl"),
    Path("models/random_forest_model.pkl"),
    current_dir / "models" / "random_forest_model.pkl",
    current_dir / "random_forest_model.pkl",
]
RANDOM_FOREST_MODEL_PATH = next((p for p in rf_candidates if p.is_file()), rf_candidates[0])

encoder_candidates = [
    current_dir.parent.parent / "models" / "performance_encoder.pkl",
    Path("/app/models/performance_encoder.pkl"),
    Path("models/performance_encoder.pkl"),
    current_dir / "models" / "performance_encoder.pkl",
    current_dir / "performance_encoder.pkl",
]
ENCODER_PATH = next((p for p in encoder_candidates if p.is_file()), encoder_candidates[0])

print("\n" + "=" * 55)
print("PERFORMANCE SERVICE: PATH RESOLUTION")
print("=" * 55)
print(f"XGBoost file   : {XGBOOST_MODEL_PATH} (exists: {XGBOOST_MODEL_PATH.is_file()})")
print(f"Random Forest  : {RANDOM_FOREST_MODEL_PATH} (exists: {RANDOM_FOREST_MODEL_PATH.is_file()})")
print(f"Encoder file   : {ENCODER_PATH} (exists: {ENCODER_PATH.is_file()})")
print("=" * 55 + "\n")


# ==========================================
# Load XGBoost - Primary
# ==========================================

xgb_model = None

if XGBOOST_MODEL_PATH.is_file():
    try:
        xgb_model = joblib.load(str(XGBOOST_MODEL_PATH))
        print("XGBoost model loaded successfully.")
    except Exception as e:
        print(f"XGBoost model loading failed: {e}")
else:
    print(f"XGBoost artifact not found at: {XGBOOST_MODEL_PATH}")


# ==========================================
# Load Random Forest - Fallback
# ==========================================

rf_model = None

if RANDOM_FOREST_MODEL_PATH.is_file():
    try:
        rf_model = joblib.load(str(RANDOM_FOREST_MODEL_PATH))
        print("Random Forest model loaded successfully.")
    except Exception as e:
        print(f"Random Forest model loading failed: {e}")
else:
    print(f"Random Forest artifact not found at: {RANDOM_FOREST_MODEL_PATH}")


# ==========================================
# Load Performance Encoder
# ==========================================

performance_encoder = None

if ENCODER_PATH.is_file():
    try:
        performance_encoder = joblib.load(str(ENCODER_PATH))
        print("Performance encoder loaded successfully.")
    except Exception as e:
        print(f"Performance encoder loading failed: {e}")
else:
    print(f"Performance encoder artifact not found at: {ENCODER_PATH}")


# ==========================================
# Prediction Function
# ==========================================

def predict_performance(
    avg_quiz_score: float,
    avg_assignment_score: float,
    assignment_submission_rate: float,
    attendance_percentage: float
):
    if performance_encoder is None:
        raise RuntimeError("Performance encoder is not loaded.")

    input_data = pd.DataFrame([
        {
            "avg_quiz_score": avg_quiz_score,
            "avg_assignment_score": avg_assignment_score,
            "assignment_submission_rate": assignment_submission_rate,
            "attendance_percentage": attendance_percentage
        }
    ])

    # Primary: XGBoost
    if xgb_model is not None:
        try:
            prediction = xgb_model.predict(input_data)
            performance = performance_encoder.inverse_transform(prediction)[0]
            return {
                "prediction": performance,
                "model": "XGBoost"
            }
        except Exception as e:
            print(f"XGBoost prediction failed: {e}")

    # Fallback: Random Forest
    if rf_model is not None:
        try:
            prediction = rf_model.predict(input_data)
            performance = performance_encoder.inverse_transform(prediction)[0]
            return {
                "prediction": performance,
                "model": "Random Forest"
            }
        except Exception as e:
            print(f"Random Forest prediction failed: {e}")

    raise RuntimeError("Both XGBoost and Random Forest models failed or are not loaded.")