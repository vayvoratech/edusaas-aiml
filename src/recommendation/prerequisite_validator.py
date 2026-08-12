import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DB_NAME = "eduai_db"
SCHEMA = "education"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# PREREQUISITE VALIDATOR
# ============================================================

class PrerequisiteValidator:

    @staticmethod
    def has_completed_prerequisite(
        user_id,
        prerequisite_course_id
    ) -> bool:
        """
        Check whether a user has completed the
        prerequisite course with at least 80%
        completion.
        """

        # No prerequisite required
        if prerequisite_course_id is None:
            return True

        with engine.begin() as connection:

            result = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM {SCHEMA}.enrollments
                    WHERE user_id = :user_id
                      AND course_id = :course_id
                      AND completion_percentage >= 80
                    """
                ),
                {
                    "user_id": user_id,
                    "course_id": prerequisite_course_id
                }
            ).scalar()

        return result > 0


    # ========================================================
    # VALIDATE COURSE PREREQUISITES
    # ========================================================

    @staticmethod
    def validate(
        user_id,
        course_id
    ) -> bool:
        """
        Validate whether all prerequisites for a course
        have been completed by the user.
        """

        with engine.begin() as connection:

            prerequisites = connection.execute(
                text(
                    f"""
                    SELECT
                        prerequisite_course_id
                    FROM {SCHEMA}.course_prerequisites
                    WHERE course_id = :course_id
                    """
                ),
                {
                    "course_id": course_id
                }
            ).fetchall()


        # No prerequisites
        if not prerequisites:
            return True


        # Check every prerequisite
        for prerequisite in prerequisites:

            completed = (
                PrerequisiteValidator
                .has_completed_prerequisite(
                    user_id,
                    prerequisite.prerequisite_course_id
                )
            )

            if not completed:
                return False


        return True