from fastapi import APIRouter
from pydantic import BaseModel

from src.fraud.fraud_service import fraud_service


router = APIRouter(
    prefix="/fraud",
    tags=["Fraud Detection"]
)


class FraudRequest(BaseModel):

    student_id: str

    completion_percentage: float = 0

    watch_time_minutes: float = 0

    quiz_score: float = 0

    rating: float = 0

    sessions_last_30_days: int = 0

    avg_session_minutes: float = 0

    videos_watched: int = 0

    assignments_attempted: int = 0

    discussion_interactions: int = 0

    login_count: int = 0

    device_count: int = 0

    ip_changes: int = 0

    suspicious_activity_score: float = 0


@router.post("/predict")
def predict_fraud(request: FraudRequest):

    result = fraud_service.predict(
        request.model_dump()
    )

    return {
        "success": True,
        "message": "Fraud prediction completed successfully.",
        "data": result
    }