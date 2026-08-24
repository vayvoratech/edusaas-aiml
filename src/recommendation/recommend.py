from src.recommendation.hybrid_recommendation import recommend


def get_recommendations(
    user_id,
    course_name: str,
    courses,
    user=None,
    prerequisites=None,
    completed_courses=None
):
    """
    Generate hybrid course recommendations.

    Database access is handled outside the recommendation
    model. This function only passes prepared data to the
    recommendation engine.
    """

    return recommend(
        user_id=user_id,
        course_name=course_name,
        courses=courses,
        user=user,
        prerequisites=prerequisites,
        completed_courses=completed_courses
    )