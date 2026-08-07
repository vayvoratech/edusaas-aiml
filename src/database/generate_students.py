import os
import random

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ---------------------------------------
# Load Environment Variables
# ---------------------------------------

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# ---------------------------------------
# Career Goals
# ---------------------------------------

career_goals = [
    "AI Engineer",
    "Data Scientist",
    "Data Analyst",
    "Machine Learning Engineer",
    "Backend Developer",
    "Full Stack Developer",
    "Cloud Engineer",
    "Cyber Security Engineer"
]

# ---------------------------------------
# Update Career Goals
# ---------------------------------------

def update_student_career_goals():

    with engine.begin() as connection:

        students = connection.execute(
            text(
                """
                SELECT student_id
                FROM students
                """
            )
        ).fetchall()

        for student in students:

            connection.execute(
                text(
                    """
                    UPDATE students
                    SET career_goal = :career_goal
                    WHERE student_id = :student_id
                    """
                ),
                {
                    "student_id": student.student_id,
                    "career_goal": random.choice(career_goals)
                }
            )

    print("✅ Student career goals updated successfully!")

# ---------------------------------------
# Main
# ---------------------------------------

if __name__ == "__main__":

    update_student_career_goals()