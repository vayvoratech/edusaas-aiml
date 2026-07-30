from src.recommendation.hybrid_recommendation import (
    recommend,
    courses
)


def test_recommendation():

    # Use the first course from the database
    course_name = courses.iloc[0]["course_name"]

    result = recommend(
        student_id=1,
        course_name=course_name
    )

    assert result is not None

    assert isinstance(result, list)

    assert len(result) > 0

    first_course = result[0]

    assert "course_id" in first_course
    assert "course_name" in first_course
    assert "predicted_rating" in first_course

    assert isinstance(
        first_course["course_id"],
        int
    )

    assert isinstance(
        first_course["course_name"],
        str
    )

    assert isinstance(
        first_course["predicted_rating"],
        float
    )