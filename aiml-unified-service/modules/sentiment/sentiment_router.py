from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from modules.sentiment.sentiment_service import sentiment_service


# ---------------------------------------
# Initialize Router
# ---------------------------------------

router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"]
)


# ---------------------------------------
# Request Schema
# ---------------------------------------

class SentimentRequest(BaseModel):
    post_id: Optional[str] = Field(
        default="1", 
        description="Identifier for the post or message"
    )
    post_text: str = Field(
        ..., 
        min_length=1, 
        description="Raw text content to analyze"
    )


# ---------------------------------------
# Home / Root Endpoint
# ---------------------------------------

@router.get("/")
def home():
    return {
        "success": True,
        "message": "EduSaaS Sentiment Analysis API Running",
        "data": {
            "service": "sentiment"
        }
    }


# ---------------------------------------
# Health Check Endpoint
# ---------------------------------------

@router.get("/health")
def health():
    return {
        "success": True,
        "message": "Sentiment Analysis Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


# ---------------------------------------
# Prediction Endpoint
# ---------------------------------------

@router.post("/predict")
def predict_sentiment(request: SentimentRequest):
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
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        )