from fastapi import APIRouter
from pydantic import BaseModel

from src.dropout.predict_dropout import predict_dropout
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/dropout",
    tags=["Dropout Prediction"]
)


# ---------------------------------------
# Input Schema
# ---------------------------------------

class DropoutInput(BaseModel):

    sessions_last_30_days: int
    avg_session_minutes: float
    videos_watched: int
    assignments_attempted: int
    discussion_interactions: int

    logins_last_30_days: int
    days_since_last_login: int

    completion_percentage: float
    quiz_average: float
    assignment_completion_rate: float


# ---------------------------------------
# Home Endpoint
# ---------------------------------------

@router.get("/")
def home():

    return {
        "success": True,
        "message": "Dropout Prediction API is Running",
        "data": None
    }


# ---------------------------------------
# Health Check
# ---------------------------------------

@router.get("/health")
def health():

    return {

        "success": True,

        "message": "Dropout Prediction Service Healthy",

        "data": {
            "status": "healthy"
        }

    }


# ---------------------------------------
# Prediction Endpoint
# ---------------------------------------

@router.post("/predict")
def dropout_prediction(data: DropoutInput):

    try:

        result = predict_dropout(
            data.model_dump()
        )

        return {

            "success": True,

            "message": "Dropout prediction completed successfully.",

            "data": result

        }

    except Exception as e:

        raise EduAIException(str(e))