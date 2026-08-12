import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# LOAD COURSES
# ============================================================

QUERY = """
SELECT
    id,
    title,
    description,
    provider,
    category,
    difficulty,
    status,
    educator_id
FROM education.courses
WHERE status = 'active'
"""

courses = pd.read_sql(
    QUERY,
    engine
)


# ============================================================
# VALIDATE DATA
# ============================================================

if courses.empty:
    raise ValueError(
        "No active courses found in education.courses"
    )


# ============================================================
# PREPARE FEATURES
# ============================================================

courses["title"] = courses["title"].fillna("")
courses["description"] = courses["description"].fillna("")
courses["category"] = courses["category"].fillna("")
courses["difficulty"] = courses["difficulty"].fillna("")


courses["features"] = (
    courses["title"] + " " +
    courses["description"] + " " +
    courses["category"] + " " +
    courses["difficulty"]
)


# ============================================================
# TEXT VECTORIZATION
# ============================================================

vectorizer = CountVectorizer(
    stop_words="english"
)

feature_matrix = vectorizer.fit_transform(
    courses["features"]
)


# ============================================================
# COSINE SIMILARITY
# ============================================================

similarity = cosine_similarity(
    feature_matrix
)

print(
    "✅ Content-based similarity matrix "
    "created successfully"
)

print(
    f"Courses loaded: {len(courses)}"
)


# ============================================================
# RECOMMEND COURSES
# ============================================================

def recommend(course_name, number_of_recommendations=5):

    matches = courses[
        courses["title"].str.lower()
        == course_name.lower()
    ]

    if matches.empty:
        raise ValueError(
            f"Course not found: {course_name}"
        )

    idx = matches.index[0]

    distances = list(
        enumerate(similarity[idx])
    )

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for index, score in distances[1:]:
        recommendations.append(
            {
                "course_id": courses.iloc[index]["id"],
                "course_name": courses.iloc[index]["title"],
                "similarity_score": round(
                    float(score),
                    4
                )
            }
        )

        if len(recommendations) >= number_of_recommendations:
            break

    return recommendations


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_course = courses.iloc[0]["title"]

    recommendations = recommend(
        test_course,
        5
    )

    print()
    print(
        f"Recommendations for: {test_course}"
    )
    print("-" * 60)

    for recommendation in recommendations:

        print(
            f"{recommendation['course_name']} "
            f"(similarity: "
            f"{recommendation['similarity_score']})"
        )