import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy


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
# LOAD COURSE RATINGS
# ============================================================

QUERY = """
SELECT
    user_id,
    course_id,
    rating
FROM education.course_ratings
WHERE rating IS NOT NULL
"""

ratings = pd.read_sql(
    QUERY,
    engine
)


# ============================================================
# VALIDATE DATA
# ============================================================

if ratings.empty:
    raise ValueError(
        "No ratings found in education.course_ratings"
    )

print("✅ Course ratings loaded successfully")
print(f"Total ratings: {len(ratings)}")

print()
print("Sample ratings:")
print(ratings.head())


# ============================================================
# RATING SCALE
# ============================================================

reader = Reader(
    rating_scale=(1, 5)
)


# ============================================================
# CONVERT TO SURPRISE DATASET
# ============================================================

data = Dataset.load_from_df(
    ratings[
        [
            "user_id",
            "course_id",
            "rating"
        ]
    ],
    reader
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

trainset, testset = train_test_split(
    data,
    test_size=0.20,
    random_state=42
)


print()
print("✅ Training/test split completed")
print(
    f"Training ratings: "
    f"{trainset.n_ratings}"
)
print(
    f"Testing ratings: "
    f"{len(testset)}"
)


# ============================================================
# SVD COLLABORATIVE FILTERING MODEL
# ============================================================

model = SVD(
    random_state=42
)


# ============================================================
# TRAIN MODEL
# ============================================================

model.fit(
    trainset
)

print()
print(
    "✅ Collaborative filtering "
    "SVD model trained successfully"
)


# ============================================================
# PREDICTIONS
# ============================================================

predictions = model.test(
    testset
)


# ============================================================
# EVALUATION
# ============================================================

rmse = accuracy.rmse(
    predictions,
    verbose=True
)

print()
print(
    f"✅ Collaborative Filtering RMSE: "
    f"{rmse:.4f}"
)


# ============================================================
# RECOMMEND COURSES FOR USER
# ============================================================

def recommend_courses(
    user_id,
    number_of_recommendations=5
):

    # Load all available courses
    courses = pd.read_sql(
        """
        SELECT
            id,
            title
        FROM education.courses
        WHERE status = 'active'
        """,
        engine
    )

    # Courses already rated by the user
    rated_courses = set(
        ratings[
            ratings["user_id"] == user_id
        ]["course_id"]
        .tolist()
    )

    # Candidate courses
    candidate_courses = courses[
        ~courses["id"].isin(
            rated_courses
        )
    ]

    predictions = []

    for _, course in candidate_courses.iterrows():

        prediction = model.predict(
            user_id,
            course["id"]
        )

        predictions.append(
            {
                "course_id": course["id"],
                "course_name": course["title"],
                "predicted_rating": round(
                    float(
                        prediction.est
                    ),
                    4
                )
            }
        )

    recommendations = sorted(
        predictions,
        key=lambda x: x[
            "predicted_rating"
        ],
        reverse=True
    )

    return recommendations[
        :number_of_recommendations
    ]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_user_id = ratings.iloc[0]["user_id"]

    recommendations = recommend_courses(
        test_user_id,
        5
    )

    print()
    print(
        f"Recommendations for user: "
        f"{test_user_id}"
    )

    print("-" * 60)

    for recommendation in recommendations:

        print(
            f"{recommendation['course_name']} "
            f"-> predicted rating: "
            f"{recommendation['predicted_rating']}"
        )
        