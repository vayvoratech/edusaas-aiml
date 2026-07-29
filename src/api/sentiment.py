from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.sentiment.sentiment_service import sentiment_service


app = FastAPI(
    title="EduSaaS Sentiment Analysis API",
    version="2.0.0",
    description="Production Ready Sentiment Analysis API"
)


# ---------------------------------------
# Request Schema
# ---------------------------------------

class SentimentRequest(BaseModel):

    student_id: int = Field(
        ...,
        example=101
    )

    course_id: int = Field(
        ...,
        example=15
    )

    discussion_id: int = Field(
        ...,
        example=5001
    )

    post_text: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        example="This course is amazing."
    )


# ---------------------------------------
# Home Endpoint
# ---------------------------------------

@app.get("/")
def home():

    return {
        "message": "EduSaaS Sentiment Analysis API is Running"
    }


# ---------------------------------------
# Health Check
# ---------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "DistilBERT",
        "version": "1.0"
    }


# ---------------------------------------
# Predict Sentiment
# ---------------------------------------

@app.post("/predict-sentiment")
def predict(request: SentimentRequest):

    try:

        result = sentiment_service.predict(

            request.student_id,

            request.course_id,

            request.discussion_id,

            request.post_text

        )

        return result

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )