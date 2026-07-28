from faker import Faker
import random
import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL Configuration
DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"      # <-- Replace with your password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

fake = Faker()

skill_levels = ["Beginner", "Intermediate", "Advanced"]

interest_areas = [
    "Machine Learning",
    "Data Science",
    "Python",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "SQL",
    "Power BI"
]

students = []

for _ in range(1000):
    students.append({
        "full_name": fake.name(),
        "email": fake.unique.email(),
        "age": random.randint(18, 35),
        "gender": random.choice(["Male", "Female"]),
        "skill_level": random.choice(skill_levels),
        "interest_area": random.choice(interest_areas),
        "registration_date": fake.date_between("-2y", "today")
    })

df = pd.DataFrame(students)

print(df.head())

df.to_sql(
    "students",
    engine,
    if_exists="append",
    index=False
)

print("✅ 1000 Students Inserted Successfully!")

