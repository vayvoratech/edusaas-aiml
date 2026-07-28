import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder

# PostgreSQL Configuration
DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# Load Tables
students = pd.read_sql("SELECT * FROM students", engine)
courses = pd.read_sql("SELECT * FROM courses", engine)
enrollments = pd.read_sql("SELECT * FROM enrollments", engine)

# Merge Tables
df = enrollments.merge(students, on="student_id")
df = df.merge(courses, on="course_id")

print("Merged Dataset Shape:", df.shape)

# Encode Categorical Columns
label_encoder = LabelEncoder()

df["skill_level"] = label_encoder.fit_transform(df["skill_level"])
df["interest_area"] = label_encoder.fit_transform(df["interest_area"])
df["category"] = label_encoder.fit_transform(df["category"])
df["difficulty_level"] = label_encoder.fit_transform(df["difficulty_level"])
df["gender"] = label_encoder.fit_transform(df["gender"])

print(df.head())

# Save Processed Dataset
df.to_csv("data/processed_recommendation_data.csv", index=False)

print("✅ Feature Engineering Completed")
print("Processed dataset saved to data/processed_recommendation_data.csv")