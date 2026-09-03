from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.dropout.predict_dropout import predict_dropout
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/dropout",
    tags=["Dropout Prediction"]
)


# ============================================================
# Input Schema
# ============================================================

class DropoutInput(BaseModel):

    student_id: UUID

    sessions_last_30_days: int = Field(
        ge=0
    )

    avg_session_minutes: float = Field(
        ge=0
    )

    videos_watched: int = Field(
        ge=0
    )

    assignments_attempted: int = Field(
        ge=0
    )

    discussion_interactions: int = Field(
        ge=0
    )

    logins_last_30_days: int = Field(
        ge=0
    )

    days_since_last_login: int = Field(
        ge=0
    )

    completion_percentage: float = Field(
        ge=0,
        le=100
    )

    quiz_average: float = Field(
        ge=0,
        le=100
    )

    assignment_completion_rate: float = Field(
        ge=0,
        le=100
    )


# ============================================================
# Root
# ============================================================

@router.get("/")
def home():

    return {
        "success": True,
        "message": "Dropout Prediction API is Running",
        "data": {
            "service": "dropout"
        }
    }


# ============================================================
# Health Check
# ============================================================

@router.get("/health")
def health():

    return {
        "success": True,
        "message": "Dropout Prediction Service Healthy",
        "data": {
            "status": "healthy",
            "models_loaded": True
        }
    }


# ============================================================
# Prediction
# ============================================================

@router.post("/predict")
def dropout_prediction(
    data: DropoutInput
):

    try:

        # student_id is used by Node/DB,
        # not by the ML model itself.
        prediction_input = data.model_dump(
            exclude={
                "student_id"
            }
        )

        result = predict_dropout(
            prediction_input
        )

        return {
            "success": True,
            "message": (
                "Dropout prediction "
                "completed successfully."
            ),
            "data": {
                "student_id": str(
                    data.student_id
                ),
                **result
            }
        }

    except Exception as e:

        raise EduAIException(
            str(e)
        )