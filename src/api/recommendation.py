from fastapi import FastAPI, HTTPException

from src.recommendation.hybrid_recommendation import recommend


app = FastAPI(
    title="EduAI Recommendation API",
    description="Course Recommendation API",
    version="1.0"
)


@app.get("/")
def home():
    return {
        "message": "EduAI Recommendation API is running 🚀"
    }


@app.get("/recommend")
def get_recommendations(student_id: int, course_name: str):

    try:
        recommendations = recommend(student_id, course_name)

        return {
            "student_id": student_id,
            "course_name": course_name,
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )