from src.fraud.fraud_service import fraud_service


def predict_fraud(student_data: dict):
    """
    Predict fraud using the pre-trained Fraud Detection models.
    """

    return fraud_service.predict(student_data)


if __name__ == "__main__":

    sample_student = {

        "student_id": "2789a8b8-8ed0-496b-a38a-db56b91859ff",

        "completion_percentage": 82,

        "watch_time_minutes": 2100,

        "quiz_score": 86,

        "rating": 5,

        "sessions_last_30_days": 25,

        "avg_session_minutes": 42,

        "videos_watched": 65,

        "assignments_attempted": 12,

        "discussion_interactions": 18,

        "login_count": 32,

        "device_count": 1,

        "ip_changes": 0,

        "suspicious_activity_score": 0

    }

    result = predict_fraud(sample_student)

    print("\nPrediction Result\n")
    print(result)