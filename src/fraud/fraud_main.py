from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.fraud.fraud_service import fraud_service


app = FastAPI(
    title="EduSaaS Fraud Detection API",
    version="1.0.0"
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


@app.get("/")
def home():

    return {
        "success": True,
        "message": "Fraud Detection API is Running"
    }


@app.get("/health")
def health():

    return {
        "success": True,
        "message": "Fraud Detection Service Healthy",
        "model": "Random Forest + Isolation Forest",
        "version": "1.0.0"
    }


@app.post("/fraud/predict")
def predict_fraud(request: FraudRequest):

    result = fraud_service.predict(
        request.model_dump()
    )

    return {
        "success": True,
        "message": "Fraud prediction completed successfully.",
        "data": result
    }