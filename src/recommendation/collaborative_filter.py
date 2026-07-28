import pandas as pd
from sqlalchemy import create_engine
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

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

# Load Enrollment Data
enrollments = pd.read_sql(
    """
    SELECT student_id, course_id, rating
    FROM enrollments
    """,
    engine
)

print(enrollments.head())

# Reader for rating scale
reader = Reader(rating_scale=(1, 5))

# Convert DataFrame to Surprise Dataset
data = Dataset.load_from_df(
    enrollments[["student_id", "course_id", "rating"]],
    reader
)

# Split Data
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# Train SVD Model
model = SVD()

model.fit(trainset)

# Predict
predictions = model.test(testset)

# Accuracy
rmse = accuracy.rmse(predictions)

print(f"RMSE: {rmse:.4f}")