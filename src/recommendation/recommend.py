from src.recommendation.hybrid_recommendation import recommend


def get_recommendations(
    user_id,
    course_name: str
):
    """
    Generate hybrid course recommendations
    for a user and a selected course.
    """

    return recommend(
        user_id,
        course_name
    )