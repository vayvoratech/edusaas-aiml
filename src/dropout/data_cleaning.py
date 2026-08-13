import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL Configuration
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
# Load and Join Dropout Data
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


# --------------------------------
# Basic EDA
# --------------------------------

print("\nDataset Shape:")
print(df.shape)

print("\nFirst 5 Rows:")
print(df.head())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nDropout Distribution:")
print(df["dropout_status"].value_counts())

print("\nDropout Percentage:")
print(
    df["dropout_status"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# --------------------------------
# Data Cleaning
# --------------------------------

# Remove duplicate rows
df = df.drop_duplicates()

# Fill numeric missing values with median
numeric_columns = df.select_dtypes(
    include=["int64", "float64"]
).columns

for column in numeric_columns:

    if df[column].isnull().sum() > 0:

        df[column] = df[column].fillna(
            df[column].median()
        )


# --------------------------------
# Validate Ranges
# --------------------------------

df["completion_percentage"] = (
    df["completion_percentage"].clip(0, 100)
)

df["quiz_average"] = (
    df["quiz_average"].clip(0, 100)
)

df["assignment_completion_rate"] = (
    df["assignment_completion_rate"].clip(0, 100)
)


print("\n✅ Dropout data cleaning completed")

print("\nFinal Dataset Shape:")
print(df.shape)

print("\nFinal Missing Values:")
print(df.isnull().sum())