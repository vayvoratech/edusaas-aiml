from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.hiring.hiring_service import hiring_service


app = FastAPI(
    title="EduSaaS Predictive Hiring API",
    version="1.0.0"
)


class HiringRequest(BaseModel):

    experience_years: float = Field(
        0,
        ge=0
    )

    required_experience_years: float = Field(
        0,
        ge=0
    )

    skill_match_score: float = Field(
        ...,
        ge=0,
        le=1
    )

    experience_match_score: float = Field(
        ...,
        ge=0,
        le=1
    )

    domain_match: int = Field(
        ...,
        ge=0,
        le=1
    )

    profile_score: float = Field(
        ...,
        ge=0,
        le=100
    )


@app.get("/")
def home():

    return {
        "success": True,
        "message": "Predictive Hiring API is Running"
    }


@app.get("/health")
def health():

    return {
        "success": True,
        "message": "Predictive Hiring Service Healthy",
        "model": "Random Forest",
        "version": "1.0.0"
    }


@app.post("/hiring/predict")
def predict_hiring(
    request: HiringRequest
):

    try:

        result = hiring_service.predict(
            request.model_dump()
        )

        return {
            "success": True,
            "message": "Hiring prediction completed successfully.",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )