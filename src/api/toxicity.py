import os
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.toxicity.toxicity_service import toxicity_service


router = APIRouter(
    prefix="/toxicity",
    tags=["Toxicity Detection"]
)


class ToxicityRequest(BaseModel):

    student_id: str = Field(
        ...,
        examples=["2789a8b8-8ed0-496b-a38a-db56b91859ff"]
    )

    discussion_id: str = Field(
        ...,
        examples=["21de70eb-efcd-47d0-99e3-72928628d228"]
    )

    post_text: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        examples=["You are stupid."]
    )


class BatchToxicityRequest(BaseModel):

    requests: List[ToxicityRequest]


@router.get("/")
def home():

    return {
        "success": True,
        "message": "EduSaaS Toxicity Detection API is Running"
    }


@router.get("/health")
def health():

    return {
        "success": True,
        "status": "healthy",
        "service": "Toxicity Detection API",
        "model": "DistilBERT",
        "version": os.getenv(
            "MODEL_VERSION",
            "1.0.0"
        )
    }


@router.post("/predict")
def predict(request: ToxicityRequest):

    try:

        result = toxicity_service.predict(
            student_id=request.student_id,
            discussion_id=request.discussion_id,
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
            "success": True,
            "message": "Batch toxicity prediction completed successfully.",
            "data": {
                "total_predictions": len(results),
                "results": results
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )