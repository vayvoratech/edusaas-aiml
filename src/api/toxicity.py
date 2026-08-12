from typing import List
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.toxicity.toxicity_service import toxicity_service


router = APIRouter(
    prefix="/toxicity",
    tags=["Toxicity Detection"]
)


# ---------------------------------------
# Request Schemas
# ---------------------------------------

class ToxicityRequest(BaseModel):

    student_id: int = Field(
        ...,
        examples=[101]
    )

    discussion_id: int = Field(
        ...,
        examples=[5001]
    )

    post_text: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        examples=["You are stupid."]
    )


class BatchToxicityRequest(BaseModel):

    requests: List[ToxicityRequest]


# ---------------------------------------
# Home
# ---------------------------------------

@router.get("/")
def home():

    return {

        "message": "EduSaaS Toxicity Detection API is Running"

    }


# ---------------------------------------
# Health Check
# ---------------------------------------

@router.get("/health")
def health():

    return {

        "status": "healthy",

        "service": "Toxicity Detection API",

        "model": "DistilBERT",

        "version": os.getenv(
            "MODEL_VERSION",
            "1.0.0"
        )

    }


# ---------------------------------------
# Predict Toxicity
# ---------------------------------------

@router.post("/predict")
def predict(request: ToxicityRequest):

    try:

        return toxicity_service.predict(

            student_id=request.student_id,

            discussion_id=request.discussion_id,

            post_text=request.post_text

        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ---------------------------------------
# Batch Prediction
# ---------------------------------------

@router.post("/batch-predict")
def batch_predict(
    request: BatchToxicityRequest
):

    try:

        results = []

        for item in request.requests:

            prediction = toxicity_service.predict(

                student_id=item.student_id,

                discussion_id=item.discussion_id,

                post_text=item.post_text

            )

            results.append(prediction)

        return {

            "total_predictions": len(results),

            "results": results

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )