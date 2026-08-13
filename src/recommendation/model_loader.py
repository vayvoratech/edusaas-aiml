from pathlib import Path
import joblib


# ============================================================
# MODEL DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = BASE_DIR / "models"


# ============================================================
# MODEL PATHS
# ============================================================

SVD_MODEL_PATH = (
    MODEL_DIR / "svd_recommendation_model.pkl"
)

CONTENT_VECTORIZER_PATH = (
    MODEL_DIR / "content_vectorizer.pkl"
)

CONTENT_SIMILARITY_PATH = (
    MODEL_DIR / "content_similarity.pkl"
)


# ============================================================
# LOAD MODELS ONCE
# ============================================================

_svd_model = None
_content_vectorizer = None
_content_similarity = None


def load_recommendation_models():
    """
    Load recommendation artifacts once and cache them
    in memory.

    This prevents model loading/training on every
    recommendation request.
    """

    global _svd_model
    global _content_vectorizer
    global _content_similarity

    if (
        _svd_model is not None
        and _content_vectorizer is not None
        and _content_similarity is not None
    ):
        return (
            _svd_model,
            _content_vectorizer,
            _content_similarity
        )

    if not SVD_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"SVD model not found: "
            f"{SVD_MODEL_PATH}"
        )

    if not CONTENT_VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Content vectorizer not found: "
            f"{CONTENT_VECTORIZER_PATH}"
        )

    if not CONTENT_SIMILARITY_PATH.exists():
        raise FileNotFoundError(
            f"Content similarity matrix not found: "
            f"{CONTENT_SIMILARITY_PATH}"
        )

    _svd_model = joblib.load(
        SVD_MODEL_PATH
    )

    _content_vectorizer = joblib.load(
        CONTENT_VECTORIZER_PATH
    )

    _content_similarity = joblib.load(
        CONTENT_SIMILARITY_PATH
    )

    return (
        _svd_model,
        _content_vectorizer,
        _content_similarity
    )


# ============================================================
# HEALTH / VALIDATION
# ============================================================

def models_loaded() -> bool:
    """
    Return whether recommendation artifacts
    are currently loaded in memory.
    """

    return (
        _svd_model is not None
        and _content_vectorizer is not None
        and _content_similarity is not None
    )