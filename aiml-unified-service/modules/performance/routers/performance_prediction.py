from fastapi import APIRouter
from pydantic import BaseModel

from modules.performance.services.performance_prediction_service import predict_performance


router = APIRouter(
    prefix="/performance",
    tags=["Performance Prediction"]
)


class PerformanceRequest(BaseModel):

    avg_quiz_score: float
    avg_assignment_score: float
    assignment_submission_rate: float
    attendance_percentage: float


@router.post("/predict")
def performance_prediction(
    data: PerformanceRequest
):

    result = predict_performance(
        avg_quiz_score=data.avg_quiz_score,
        avg_assignment_score=data.avg_assignment_score,
        assignment_submission_rate=data.assignment_submission_rate,
        attendance_percentage=data.attendance_percentage
    )

    return {
        "success": True,
        "prediction": result["prediction"],
        "model": result["model"]
    }