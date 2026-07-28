import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD
import joblib
import os


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

courses = pd.read_sql("SELECT * FROM courses", engine)

enrollments = pd.read_sql("""
SELECT student_id, course_id, rating
FROM enrollments
""", engine)


# Content-Based Model
 
courses["features"] = (
    courses["category"] + " " +
    courses["difficulty_level"]
)

vectorizer = CountVectorizer()

feature_matrix = vectorizer.fit_transform(courses["features"])

content_similarity = cosine_similarity(feature_matrix)


# Collaborative Filtering Model

reader = Reader(rating_scale=(1,5))

data = Dataset.load_from_df(
    enrollments[["student_id","course_id","rating"]],
    reader
)

trainset = data.build_full_trainset()

svd_model = SVD()

svd_model.fit(trainset)

print("✅ Hybrid Recommendation Model Built Successfully")


def recommend(student_id, course_name):

    idx = courses[courses["course_name"] == course_name].index[0]

    distances = list(enumerate(content_similarity[idx]))

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
            "predicted_rating": round(predicted_rating, 2)
        })

    recommendations = sorted(
        recommendations,
        key=lambda x: x["predicted_rating"],
        reverse=True
    )

    return recommendations 


if __name__ == "__main__":

    result = recommend(
        student_id=1,
        course_name=courses.iloc[0]["course_name"]
    )

    print("\nTop Recommendations:\n")

    for course in result:
        print(course)


    svd_model.fit(trainset)

    import joblib
import os

os.makedirs("models", exist_ok=True)

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

print("✅ Recommendation model artifacts saved successfully!")