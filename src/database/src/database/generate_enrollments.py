import random
from datetime import date, timedelta
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

enrollments = []

today = date.today()

for _ in range(5000):

    student_id = random.randint(1, 1000)
    course_id = random.randint(1, 50)

    completion = round(random.uniform(20, 100), 2)

    enrollments.append({
        "student_id": student_id,
        "course_id": course_id,
        "enrollment_date": today - timedelta(days=random.randint(1, 730)),
        "completion_percentage": completion,
        "watch_time_minutes": random.randint(60, 5000),
        "quiz_score": round(random.uniform(40, 100), 2),
        "rating": random.randint(1, 5)
    })

df = pd.DataFrame(enrollments)

print(df.head())

df.to_sql(
    "enrollments",
    engine,
    if_exists="append",
    index=False
)

print("✅ 5000 Enrollments Inserted Successfully!")