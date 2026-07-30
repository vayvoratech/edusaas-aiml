import os
import joblib
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD

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
# Load Data
# ---------------------------------------

courses = pd.read_sql(
    "SELECT * FROM courses",
    engine
)

enrollments = pd.read_sql(
    """
    SELECT student_id,
           course_id,
           rating
    FROM enrollments
    """,
    engine
)

# ---------------------------------------
# Content-Based Recommendation
# ---------------------------------------

courses["features"] = (
    courses["category"] + " " +
    courses["difficulty_level"]
)

vectorizer = CountVectorizer()

feature_matrix = vectorizer.fit_transform(
    courses["features"]
)

content_similarity = cosine_similarity(
    feature_matrix
)

# ---------------------------------------
# Collaborative Filtering
# ---------------------------------------

reader = Reader(
    rating_scale=(1, 5)
)

data = Dataset.load_from_df(
    enrollments[
        ["student_id", "course_id", "rating"]
    ],
    reader
)

trainset = data.build_full_trainset()

svd_model = SVD()

svd_model.fit(trainset)

print("✅ Hybrid Recommendation Model Built Successfully")

# ---------------------------------------
# Recommendation Function
# ---------------------------------------

def recommend(student_id: int, course_name: str):

    matched_course = courses[
        courses["course_name"].str.lower() ==
        course_name.lower()
    ]

    if matched_course.empty:
        raise ValueError(
            f"Course '{course_name}' not found."
        )

    idx = matched_course.index[0]

    distances = list(
        enumerate(content_similarity[idx])
    )

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for i in distances[1:6]:

        course = courses.iloc[i[0]]

        predicted_rating = svd_model.predict(
            student_id,
            course["course_id"]
        ).est

        recommendations.append({

            "course_id": int(course["course_id"]),

            "course_name": course["course_name"],

            "predicted_rating": round(
                predicted_rating,
                2
            )

        })

    recommendations.sort(
        key=lambda x: x["predicted_rating"],
        reverse=True
    )

    return recommendations

# ---------------------------------------
# Save Artifacts
# ---------------------------------------

if __name__ == "__main__":

    print("\nAvailable Courses:\n")

    print(
        courses["course_name"].tolist()
    )

    result = recommend(
        student_id=1,
        course_name=courses.iloc[0]["course_name"]
    )

    print("\nTop Recommendations:\n")

    for course in result:
        print(course)

    os.makedirs(
        "models",
        exist_ok=True
    )

    joblib.dump(
        svd_model,
        "models/svd_recommendation_model.pkl"
    )

    joblib.dump(
        vectorizer,
        "models/content_vectorizer.pkl"
    )

    joblib.dump(
        content_similarity,
        "models/content_similarity.pkl"
    )

    print(
        "✅ Recommendation model artifacts saved successfully!"
    )