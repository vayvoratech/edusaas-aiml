from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_sentiment_prediction():

    response = client.post(
        "/sentiment/predict-sentiment",
        json={
            "student_id": 101,
            "course_id": 15,
            "discussion_id": 5001,
            "post_text": "This course is amazing."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "confidence" in data
    assert "scores" in data