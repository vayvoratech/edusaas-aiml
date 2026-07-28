from faker import Faker
import random
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

fake = Faker()

categories = [
    "Machine Learning",
    "Deep Learning",
    "Data Science",
    "Python",
    "SQL",
    "NLP",
    "Computer Vision",
    "Power BI"
]

difficulties = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

courses = []

for i in range(1, 51):

    courses.append({
        "course_name": f"{random.choice(categories)} Course {i}",
        "category": random.choice(categories),
        "difficulty_level": random.choice(difficulties),
        "duration_hours": random.randint(10, 80)
    })

df = pd.DataFrame(courses)

print(df.head())

df.to_sql(
    "courses",
    engine,
    if_exists="append",
    index=False
)

print("✅ 50 Courses Inserted Successfully!")