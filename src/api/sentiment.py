from typing import List
import os

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.sentiment.sentiment_service import sentiment_service
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"]
)


# ---------------------------------------
# Request Schemas
# ---------------------------------------

class SentimentRequest(BaseModel):

    student_id: int = Field(
        ...,
        json_schema_extra={"example": 101}
    )

    course_id: int = Field(
        ...,
        json_schema_extra={"example": 15}
    )

    discussion_id: int = Field(
        ...,
        json_schema_extra={"example": 5001}
    )

    post_text: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        json_schema_extra={
            "example": "This course is amazing."
        }
    )


class BatchSentimentRequest(BaseModel):

    requests: List[SentimentRequest]


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

            "model": "DistilBERT",

            "version": os.getenv("MODEL_VERSION")

        }

    }


# ---------------------------------------
# Predict Sentiment
# ---------------------------------------

@router.post("/predict-sentiment")
def predict_sentiment(request: SentimentRequest):

    try:

        result = sentiment_service.predict(

            student_id=request.student_id,

            course_id=request.course_id,

            discussion_id=request.discussion_id,

            post_text=request.post_text

        )

        return {

            "success": True,

            "message": "Sentiment prediction completed successfully.",

            "data": result

        }

    except Exception as e:

        raise EduAIException(str(e))


# ---------------------------------------
# Batch Prediction
# ---------------------------------------

@router.post("/batch-predict")
def batch_predict(request: BatchSentimentRequest):

    try:

        results = []

        for item in request.requests:

            prediction = sentiment_service.predict(

                student_id=item.student_id,

                course_id=item.course_id,

                discussion_id=item.discussion_id,

                post_text=item.post_text

            )

            results.append(prediction)

        return {

            "success": True,

            "message": "Batch prediction completed successfully.",

            "data": {

                "total_predictions": len(results),

                "results": results

            }

        }

    except Exception as e:

        raise EduAIException(str(e))