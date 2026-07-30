from fastapi import APIRouter

from src.recommendation.hybrid_recommendation import recommend
from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation System"]
)


# ---------------------------------------
# Home
# ---------------------------------------

@router.get("/")
def home():

    return {
        "success": True,
        "message": "Recommendation API is Running",
        "data": None
    }


# ---------------------------------------
# Health
# ---------------------------------------

@router.get("/health")
def health():

    return {
        "success": True,
        "message": "Recommendation Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


# ---------------------------------------
# Get Recommendations
# ---------------------------------------

@router.get("/recommend")
def get_recommendations(
    student_id: int,
    course_name: str
):

    try:

        recommendations = recommend(
            student_id,
            course_name
        )

        return {

            "success": True,

            "message": "Recommendations generated successfully.",

            "data": {

                "student_id": student_id,

                "course_name": course_name,

                "recommendations": recommendations

            }

        }

    except Exception as e:

        raise EduAIException(str(e))