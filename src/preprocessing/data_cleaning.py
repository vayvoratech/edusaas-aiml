import pandas as pd
from sqlalchemy import create_engine

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

# Load Data
students = pd.read_sql("SELECT * FROM students", engine)
courses = pd.read_sql("SELECT * FROM courses", engine)
enrollments = pd.read_sql("SELECT * FROM enrollments", engine)

# Remove Duplicates

students.drop_duplicates(inplace=True)
courses.drop_duplicates(inplace=True)
enrollments.drop_duplicates(inplace=True)


# Handle Missing Values

students.dropna(inplace=True)
courses.dropna(inplace=True)
enrollments.dropna(inplace=True)


# Standardize Text Columns

students["skill_level"] = students["skill_level"].str.strip().str.title()
students["interest_area"] = students["interest_area"].str.strip().str.title()

courses["category"] = courses["category"].str.strip().str.title()
courses["difficulty_level"] = courses["difficulty_level"].str.strip().str.title()

# Remove Invalid Data

students = students[(students["age"] >= 18) & (students["age"] <= 60)]

print("✅ Data Cleaning Completed")

print("\nStudents Shape:", students.shape)
print("Courses Shape:", courses.shape)
print("Enrollments Shape:", enrollments.shape)