from src.recommendation.hybridrecommendation import (
    recommend,
    courses
)


def test_recommendation():

    course_name = courses.iloc[0]["course_name"]

    result = recommend(
        student_id=1,
        course_name=course_name
    )

    assert result is not None

    assert "recommendations" in result

    assert "learning_pathway" in result

    recommendations = result["recommendations"]

    assert len(recommendations) > 0

    first = recommendations[0]

    assert "course_id" in first
    assert "course_name" in first
    assert "predicted_rating" in first
    assert "similarity_score" in first
    assert "confidence_score" in first
    assert "recommendation_reason" in first

    assert isinstance(first["course_id"], int)
    assert isinstance(first["course_name"], str)