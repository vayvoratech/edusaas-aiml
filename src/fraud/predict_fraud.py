from src.fraud.fraud_service import fraud_service


def predict_fraud(
    student_data: dict
):
    """
    Predict fraud for a student.
    """

    return fraud_service.predict(
        student_data
    )


if __name__ == "__main__":

    sample_student = {

        "student_id": 101,

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

        "payment_status": "PAID",

        "enrollment_source": "WEB",

        "enrollment_status": "ACTIVE"

    }

    result = predict_fraud(
        sample_student
    )

    print("\nPrediction Result\n")

    print(result)