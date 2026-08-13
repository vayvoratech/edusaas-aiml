from sqlalchemy import create_engine, text
import os

from dotenv import load_dotenv


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
# LEARNING PATHWAY
# ============================================================

class LearningPathway:

    @staticmethod
    def generate(
        user_id,
        recommendations: list
    ) -> list:
        """
        Generate a personalized learning pathway
        based on the user's completed courses and
        recommended courses.
        """

        with engine.begin() as connection:

            completed_courses = connection.execute(
                text(
                    f"""
                    SELECT
                        c.id,
                        c.title
                    FROM {SCHEMA}.enrollments e
                    JOIN {SCHEMA}.courses c
                        ON e.course_id = c.id
                    WHERE e.user_id = :user_id
                      AND e.completion_percentage >= 80
                    ORDER BY e.enrolled_at
                    """
                ),
                {
                    "user_id": user_id
                }
            ).fetchall()


        pathway = []


        # ====================================================
        # COMPLETED COURSES
        # ====================================================

        for course in completed_courses:

            pathway.append(
                {
                    "course_id": str(
                        course.id
                    ),

                    "course_name": (
                        course.title
                    ),

                    "status": "COMPLETED"
                }
            )


        # ====================================================
        # RECOMMENDED COURSES
        # ====================================================

        for course in recommendations:

            pathway.append(
                {
                    "course_id": str(
                        course["course_id"]
                    ),

                    "course_name": (
                        course["course_name"]
                    ),

                    "status": "RECOMMENDED"
                }
            )


        return pathway