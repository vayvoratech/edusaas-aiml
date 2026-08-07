from sqlalchemy import text

from src.database.database_connection import engine


class PrerequisiteValidator:

    @staticmethod
    def has_completed_prerequisite(
        student_id: int,
        prerequisite_course_id: int | None
    ) -> bool:

        # No prerequisite required
        if prerequisite_course_id is None:
            return True

        with engine.begin() as connection:

            result = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM enrollments
                    WHERE student_id = :student_id
                      AND course_id = :course_id
                      AND completion_percentage >= 80
                    """
                ),
                {
                    "student_id": student_id,
                    "course_id": prerequisite_course_id
                }
            ).scalar()

        return result > 0