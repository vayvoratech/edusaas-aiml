from src.dropout.predict_dropout import predict_dropout


def test_dropout_prediction():

    sample = {

        "sessions_last_30_days": 30,
        "avg_session_minutes": 60,
        "videos_watched": 50,
        "assignments_attempted": 12,
        "discussion_interactions": 15,
        "logins_last_30_days": 28,
        "days_since_last_login": 1,
        "completion_percentage": 90,
        "quiz_average": 85,
        "assignment_completion_rate": 95

    }

    result = predict_dropout(sample)

    assert result is not None

    assert "dropout_prediction" in result

    assert "dropout_probability" in result

    assert "risk_level" in result

    assert result["risk_level"] in [
        "LOW",
        "MEDIUM",
        "HIGH"
    ]