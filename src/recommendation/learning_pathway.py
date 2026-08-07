from sqlalchemy import text

from src.database.database_connection import engine


class LearningPathway:

    @staticmethod
    def generate(student_id: int, recommendations: list) -> list:
        """
        Generate a personalized learning pathway
        based on student's completed courses
        and recommended courses.
        """

        with engine.begin() as connection:

            completed_courses = connection.execute(
                text(
                    """
                    SELECT c.course_name
                    FROM enrollments e
                    JOIN courses c
                    ON e.course_id = c.course_id
                    WHERE e.student_id = :student_id
                    AND e.completion_percentage >= 80
                    ORDER BY e.enrollment_date
                    """
                ),
                {
                    "student_id": student_id
                }
            ).fetchall()

        pathway = []

        # Completed Courses
        for course in completed_courses:
            pathway.append(
                {
                    "course_name": course.course_name,
                    "status": "COMPLETED"
                }
            )

        # Recommended Courses
        for course in recommendations:
            pathway.append(
                {
                    "course_name": course["course_name"],
                    "status": "RECOMMENDED"
                }
            )

        return pathway