from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_fraud_prediction():

    payload = {

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

    response = client.post(

        "/fraud/predict",

        json=payload

    )

    assert response.status_code == 200

    data = response.json()

    assert "student_id" in data

    assert "fraud_probability" in data

    assert "risk_level" in data

    assert "fraud_prediction" in data

    assert "anomaly_prediction" in data