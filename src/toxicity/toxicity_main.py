from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.toxicity.toxicity_service import ToxicityService


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Toxicity Detection API",
    description="Multi-label toxicity detection using DistilBERT",
    version="1.0.0",
)


# ============================================================
# Request Schema
# ============================================================

class ToxicityRequest(BaseModel):
    student_id: str = Field(
        ...,
        description="Student identifier",
    )

    discussion_id: str = Field(
        ...,
        description="Discussion/post identifier",
    )

    post_text: str = Field(
        ...,
        min_length=1,
        description="Discussion post text",
    )


# ============================================================
# Service
# ============================================================

toxicity_service = None


def get_toxicity_service():
    """
    Load the toxicity model lazily.

    The model is loaded only when the API receives
    its first prediction request.
    """

    global toxicity_service

    if toxicity_service is None:

        toxicity_service = ToxicityService()

    return toxicity_service


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "toxicity",
    }


# ============================================================
# Toxicity Prediction
# ============================================================

@app.post("/predict-toxicity")
def predict_toxicity(
    request: ToxicityRequest,
):

    try:

        service = get_toxicity_service()

        result = service.predict(
            student_id=request.student_id,
            discussion_id=request.discussion_id,
            post_text=request.post_text,
        )

        return {
            "success": True,
            "data": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Toxicity prediction failed: {exc}",
        )