from fastapi import APIRouter
from pydantic import BaseModel

from src.fraud.fraud_service import fraud_service


router = APIRouter(
    prefix="/fraud",
    tags=["Fraud Detection"]
)


class FraudRequest(BaseModel):

    student_id: int

    completion_percentage: float

    watch_time_minutes: int

    quiz_score: float

    rating: int

    sessions_last_30_days: int

    avg_session_minutes: float

    videos_watched: int

    assignments_attempted: int

    discussion_interactions: int

    login_count: int

    device_count: int

    ip_changes: int

    payment_status: str = "PAID"

    enrollment_source: str = "WEB"

    enrollment_status: str = "ACTIVE"


@router.post("/predict")
def predict_fraud(request: FraudRequest):

    return fraud_service.predict(

        request.model_dump()

    )