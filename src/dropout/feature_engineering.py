import pandas as pd
from sqlalchemy import create_engine

# --------------------------------
# PostgreSQL Configuration
# --------------------------------

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


# --------------------------------
# Load Dropout Data
# --------------------------------

query = """
SELECT
    a.student_id,
    a.sessions_last_30_days,
    a.avg_session_minutes,
    a.videos_watched,
    a.assignments_attempted,
    a.discussion_interactions,

    l.logins_last_30_days,
    l.days_since_last_login,

    p.course_id,
    p.completion_percentage,
    p.quiz_average,
    p.assignment_completion_rate,
    p.dropout_status

FROM activity_logs a

JOIN login_history l
    ON a.student_id = l.student_id

JOIN learning_progress p
    ON a.student_id = p.student_id
"""

df = pd.read_sql(query, engine)

print("Dataset loaded successfully:", df.shape)


# --------------------------------
# Feature Engineering
# --------------------------------

# Overall platform engagement
df["engagement_score"] = (
    df["sessions_last_30_days"]
    + df["logins_last_30_days"]
    + df["videos_watched"]
    + df["discussion_interactions"]
)

# Overall academic/learning progress
df["learning_score"] = (
    df["completion_percentage"]
    + df["quiz_average"]
    + df["assignment_completion_rate"]
) / 3

# Inactivity indicator
df["inactivity_score"] = df["days_since_last_login"]


# --------------------------------
# Prepare Features and Target
# --------------------------------

X = df.drop(
    columns=[
        "student_id",
        "course_id",
        "dropout_status"
    ]
)

y = df["dropout_status"]


# --------------------------------
# Verify Results
# --------------------------------

print("\nFeature Engineering Completed Successfully")

print("\nInput Features:")
print(X.columns.tolist())

print("\nX Shape:")
print(X.shape)

print("\nTarget Distribution:")
print(y.value_counts())

print("\nSample Engineered Features:")
print(
    df[
        [
            "student_id",
            "engagement_score",
            "learning_score",
            "inactivity_score",
            "dropout_status"
        ]
    ].head()
)