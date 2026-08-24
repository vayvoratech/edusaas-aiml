import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.toxicity.toxicity_service import toxicity_service


app = FastAPI(
    title="EduSaaS Toxicity Detection API",
    version="1.0.0"
)


class ToxicityRequest(BaseModel):

    post_id: str = Field(
        ...,
        examples=[
            "21de70eb-efcd-47d0-99e3-72928628d228"
        ]
    )

    post_text: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        examples=[
            "You are a stupid idiot."
        ]
    )


@app.get("/")
def home():

    return {
        "success": True,
        "message": "EduSaaS Toxicity Detection API is Running"
    }


@app.get("/health")
def health():

    return {
        "success": True,
        "message": "Toxicity Detection Service Healthy",
        "model": "DistilBERT",
        "version": os.getenv(
            "MODEL_VERSION",
            "1.0.0"
        )
    }


@app.post("/toxicity/predict")
def predict_toxicity(
    request: ToxicityRequest
):

    try:

        result = toxicity_service.predict(
            student_id=request.post_id,
            discussion_id=request.post_id,
            post_text=request.post_text
        )

        return {
            "success": True,
            "message": "Toxicity prediction completed successfully.",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )