from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.sentiment.sentiment_service import sentiment_service
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"]
)


# ---------------------------------------
# Request Schema
# ---------------------------------------

class SentimentRequest(BaseModel):

    post_id: UUID = Field(
        ...,
        json_schema_extra={
            "example": "21de70eb-efcd-47d0-99e3-72928628d228"
        }
    )

    post_text: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        json_schema_extra={
            "example": "This course is amazing."
        }
    )


# ---------------------------------------
# Home
# ---------------------------------------

@router.get("/")
def home():

    return {
        "success": True,
        "message": "Sentiment Analysis API is Running",
        "data": None
    }


# ---------------------------------------
# Health Check
# ---------------------------------------

@router.get("/health")
def health():

    return {
        "success": True,
        "message": "Sentiment Analysis Service Healthy",
        "data": {
            "status": "healthy",
            "model": "DistilBERT"
        }
    }


# ---------------------------------------
# Prediction
# ---------------------------------------

@router.post("/predict-sentiment")
def predict_sentiment(
    request: SentimentRequest
):

    try:

        result = sentiment_service.predict(
            post_id=request.post_id,
            post_text=request.post_text
        )

        return {
            "success": True,
            "message": "Sentiment prediction completed successfully.",
            "data": result
        }

    except Exception as e:

        raise EduAIException(
            str(e)
        )