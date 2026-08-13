from src.sentiment.sentiment_service import sentiment_service


def test_sentiment_service():

    result = sentiment_service.predict(
        student_id=101,
        course_id=15,
        discussion_id=5001,
        post_text="This course is amazing."
    )

    assert result is not None

    assert result["prediction"] in [
        "POSITIVE",
        "NEGATIVE",
        "NEUTRAL"
    ]

    assert 0 <= result["confidence"] <= 100

    assert "scores" in result

    assert "negative" in result["scores"]
    assert "neutral" in result["scores"]
    assert "positive" in result["scores"]

    assert "model_version" in result