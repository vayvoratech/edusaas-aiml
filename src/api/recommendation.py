from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.recommendation.recommend import get_recommendations
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation System"]
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class RecommendationRequest(BaseModel):

    user_id: UUID

    course_name: str

    courses: list[dict[str, Any]] = Field(
        default_factory=list
    )

    ratings: list[dict[str, Any]] = Field(
        default_factory=list
    )

    user: dict[str, Any] | None = None

    prerequisites: list[dict[str, Any]] = Field(
        default_factory=list
    )

    completed_courses: list[dict[str, Any]] = Field(
        default_factory=list
    )


# ============================================================
# HOME
# ============================================================

@router.get("/")
def home():

    return {
        "success": True,
        "message": "Recommendation API Running",
        "data": None
    }


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def health():

    return {
        "success": True,
        "message": "Recommendation Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


# ============================================================
# RECOMMENDATION
# ============================================================

@router.post("/recommend")
def recommendation_api(
    request: RecommendationRequest
):

    try:

        result = get_recommendations(

            user_id=request.user_id,

            course_name=request.course_name,

            courses=request.courses,

            user=request.user,

            prerequisites=request.prerequisites,

            completed_courses=(
                request.completed_courses
            )
        )

        return {
            "success": True,

            "message":
                "Recommendations generated successfully.",

            "data": result
        }

    except Exception as e:

        raise EduAIException(
            str(e)
        )