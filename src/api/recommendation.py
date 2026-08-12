from uuid import UUID

from fastapi import APIRouter

from src.recommendation.recommend import get_recommendations
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation System"]
)


@router.get("/")
def home():

    return {
        "success": True,
        "message": "Recommendation API Running",
        "data": None
    }


@router.get("/health")
def health():

    return {
        "success": True,
        "message": "Recommendation Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


@router.get("/recommend")
def recommendation_api(
    user_id: UUID,
    course_name: str
):

    try:

        result = get_recommendations(
            user_id,
            course_name
        )

        return {
            "success": True,
            "message": (
                "Recommendations generated successfully."
            ),
            "data": result
        }

    except Exception as e:

        raise EduAIException(
            str(e)
        )