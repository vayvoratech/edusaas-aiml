from src.recommendation.hybrid_recommendation import recommend

def get_recommendations(student_id, course_name):
    return recommend(student_id, course_name)