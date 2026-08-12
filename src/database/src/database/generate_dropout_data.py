import random
import pandas as pd
from sqlalchemy import create_engine, text

# -----------------------------
# PostgreSQL Configuration
# -----------------------------

DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# -----------------------------
# Load existing IDs
# -----------------------------

with engine.connect() as connection:

    student_ids = pd.read_sql(
        text("SELECT student_id FROM students"),
        connection
    )["student_id"].tolist()

    course_ids = pd.read_sql(
        text("SELECT course_id FROM courses"),
        connection
    )["course_id"].tolist()


print(f"Students found: {len(student_ids)}")
print(f"Courses found: {len(course_ids)}")


# -----------------------------
# Generate Synthetic Data
# -----------------------------

activity_data = []
login_data = []
progress_data = []

for student_id in student_ids:

    # Give each student an engagement profile
    engagement = random.choice([
        "high",
        "medium",
        "low"
    ])

    if engagement == "high":

        sessions = random.randint(20, 35)
        avg_session = random.randint(35, 90)
        videos = random.randint(15, 40)
        assignments = random.randint(8, 15)
        discussions = random.randint(5, 20)

        logins = random.randint(20, 30)
        days_since_login = random.randint(0, 3)

        completion = random.uniform(70, 100)
        quiz_average = random.uniform(70, 100)
        assignment_rate = random.uniform(75, 100)

        dropout_status = 0

    elif engagement == "medium":

        sessions = random.randint(8, 20)
        avg_session = random.randint(15, 50)
        videos = random.randint(5, 20)
        assignments = random.randint(3, 10)
        discussions = random.randint(1, 10)

        logins = random.randint(8, 20)
        days_since_login = random.randint(3, 14)

        completion = random.uniform(35, 75)
        quiz_average = random.uniform(45, 80)
        assignment_rate = random.uniform(40, 80)

        # Some medium-engagement students may drop out
        dropout_status = random.choices(
            [0, 1],
            weights=[80, 20]
        )[0]

    else:

        sessions = random.randint(0, 8)
        avg_session = random.randint(1, 25)
        videos = random.randint(0, 8)
        assignments = random.randint(0, 4)
        discussions = random.randint(0, 3)

        logins = random.randint(0, 7)
        days_since_login = random.randint(15, 60)

        completion = random.uniform(0, 40)
        quiz_average = random.uniform(20, 60)
        assignment_rate = random.uniform(0, 45)

        # Low engagement = higher dropout probability
        dropout_status = random.choices(
            [0, 1],
            weights=[20, 80]
        )[0]


    # Activity table
    activity_data.append({
        "student_id": student_id,
        "sessions_last_30_days": sessions,
        "avg_session_minutes": avg_session,
        "videos_watched": videos,
        "assignments_attempted": assignments,
        "discussion_interactions": discussions
    })


    # Login table
    login_data.append({
        "student_id": student_id,
        "logins_last_30_days": logins,
        "days_since_last_login": days_since_login
    })


    # Assign one course for initial dropout training
    course_id = random.choice(course_ids)

    progress_data.append({
        "student_id": student_id,
        "course_id": course_id,
        "completion_percentage": round(completion, 2),
        "quiz_average": round(quiz_average, 2),
        "assignment_completion_rate": round(
            assignment_rate, 2
        ),
        "dropout_status": dropout_status
    })


# -----------------------------
# Convert to DataFrames
# -----------------------------

activity_df = pd.DataFrame(activity_data)
login_df = pd.DataFrame(login_data)
progress_df = pd.DataFrame(progress_data)


# -----------------------------
# Insert into PostgreSQL
# -----------------------------

activity_df.to_sql(
    "activity_logs",
    engine,
    if_exists="append",
    index=False
)

login_df.to_sql(
    "login_history",
    engine,
    if_exists="append",
    index=False
)

progress_df.to_sql(
    "learning_progress",
    engine,
    if_exists="append",
    index=False
)


print("✅ Dropout synthetic data generated successfully!")
print(f"Activity records: {len(activity_df)}")
print(f"Login records: {len(login_df)}")
print(f"Progress records: {len(progress_df)}")

print("\nDropout distribution:")
print(progress_df["dropout_status"].value_counts())