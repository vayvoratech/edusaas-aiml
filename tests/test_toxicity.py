from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_toxicity_prediction():

    payload = {

        "student_id": 101,

        "discussion_id": 5001,

        "post_text": "You are an idiot."

    }

    response = client.post(

        "/toxicity/predict",

        json=payload

    )

    assert response.status_code == 200

    data = response.json()

    # ----------------------------------------
    # Validate Response Structure
    # ----------------------------------------

    assert "student_id" in data

    assert "discussion_id" in data

    assert "post_text" in data

    assert "predictions" in data

    # ----------------------------------------
    # Validate Values
    # ----------------------------------------

    assert data["student_id"] == 101

    assert data["discussion_id"] == 5001

    assert data["post_text"] == "You are an idiot."

    assert isinstance(data["predictions"], list)

    # ----------------------------------------
    # Validate Prediction Format
    # ----------------------------------------

    if len(data["predictions"]) > 0:

        prediction = data["predictions"][0]

        assert "label" in prediction

        assert "confidence" in prediction