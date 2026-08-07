import os
import logging
import joblib
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from surprise import Dataset
from surprise import Reader
from surprise import SVD

from src.recommendation.confidence_calculator import ConfidenceCalculator
from src.recommendation.explanation_engine import ExplanationEngine
from src.recommendation.learning_pathway import LearningPathway
from src.recommendation.prerequisite_validator import PrerequisiteValidator


# -------------------------------------------------------
# Logging
# -------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Environment Variables
# -------------------------------------------------------

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


# -------------------------------------------------------
# Load Data
# -------------------------------------------------------

logger.info("Loading courses...")

courses = pd.read_sql(
    """
    SELECT *
    FROM courses
    """,
    engine
)

logger.info("Loading enrollments...")

enrollments = pd.read_sql(
    """
    SELECT
        student_id,
        course_id,
        rating
    FROM enrollments
    """,
    engine
)

logger.info("Loading students...")

students = pd.read_sql(
    """
    SELECT
        student_id,
        skill_level,
        interest_area,
        career_goal
    FROM students
    """,
    engine
)


# -------------------------------------------------------
# Content-Based Recommendation
# -------------------------------------------------------

courses["features"] = (
    courses["category"].fillna("") + " " +
    courses["difficulty_level"].fillna("")
)

vectorizer = CountVectorizer()

feature_matrix = vectorizer.fit_transform(
    courses["features"]
)

content_similarity = cosine_similarity(
    feature_matrix
)

logger.info("Content similarity matrix created successfully.")


# -------------------------------------------------------
# Collaborative Filtering (SVD)
# -------------------------------------------------------

reader = Reader(rating_scale=(1, 5))

dataset = Dataset.load_from_df(
    enrollments[
        [
            "student_id",
            "course_id",
            "rating"
        ]
    ],
    reader
)

trainset = dataset.build_full_trainset()

svd_model = SVD()

svd_model.fit(trainset)

logger.info("Collaborative filtering model trained successfully.")

# -------------------------------------------------------
# Hybrid Recommendation Function
# -------------------------------------------------------

def recommend(
    student_id: int,
    course_name: str
):

    logger.info(
        f"Generating recommendations for Student {student_id}"
    )

    matched_course = courses[
        courses["course_name"].str.lower()
        == course_name.lower()
    ]

    if matched_course.empty:

        raise ValueError(
            f"Course '{course_name}' not found."
        )

    student = students[
        students["student_id"] == student_id
    ]

    if student.empty:

        raise ValueError(
            f"Student '{student_id}' not found."
        )

    student = student.iloc[0]

    student_skill = student["skill_level"]
    student_interest = student["interest_area"]
    student_career = student["career_goal"]

    idx = matched_course.index[0]

    distances = list(
        enumerate(
            content_similarity[idx]
        )
    )

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for item in distances[1:11]:

        course = courses.iloc[item[0]]

        similarity_score = float(item[1])

        predicted_rating = (
            svd_model.predict(
                student_id,
                course["course_id"]
            ).est
        )

        # -----------------------------------
        # Student Profile Matching
        # -----------------------------------

        profile_score = 0

        if (
            course["category"]
            == student_interest
        ):
            profile_score += 0.20

        if (
            course["difficulty_level"]
            == student_skill
        ):
            profile_score += 0.20

        if (
            student_career.lower()
            in course["category"].lower()
        ):
            profile_score += 0.20

        confidence_score = (
            ConfidenceCalculator.calculate(
                predicted_rating,
                similarity_score
            )
        )

        confidence_score = min(
            confidence_score + profile_score,
            1.0
        )

        prerequisite_completed = True

        explanation = (
            ExplanationEngine.generate(
                course_name=course["course_name"],
                predicted_rating=predicted_rating,
                confidence_score=confidence_score,
                prerequisite_completed=prerequisite_completed
            )
        )

        recommendations.append(

            {

                "course_id":
                int(course["course_id"]),

                "course_name":
                course["course_name"],

                "category":
                course["category"],

                "difficulty":
                course["difficulty_level"],

                "predicted_rating":
                round(predicted_rating,2),

                "similarity_score":
                round(similarity_score,2),

                "confidence_score":
                round(confidence_score,2),

                "recommendation_reason":
                explanation,

                "prerequisite_completed":
                prerequisite_completed

            }

        )

    recommendations = sorted(

        recommendations,

        key=lambda x:(

            x["confidence_score"],

            x["predicted_rating"],

            x["similarity_score"]

        ),

        reverse=True

    )[:5]

    learning_pathway = (

        LearningPathway.generate(

            student_id,

            recommendations

        )

    )

    return {

        "student_id": student_id,

        "course_name": course_name,

        "recommendations": recommendations,

        "learning_pathway": learning_pathway

    }


    # -------------------------------------------------------
# Save Model Artifacts
# -------------------------------------------------------

def save_models():

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

    logger.info(
        "Recommendation model artifacts saved successfully."
    )


# -------------------------------------------------------
# Main
# -------------------------------------------------------

if __name__ == "__main__":

    try:

        logger.info(
            "Hybrid Recommendation System Started"
        )

        sample_course = courses.iloc[0]["course_name"]

        result = recommend(

            student_id=1,

            course_name=sample_course

        )

        print("\n==================================================")
        print("Hybrid Recommendation Result")
        print("==================================================")

        print(f"Student ID : {result['student_id']}")
        print(f"Course     : {result['course_name']}")

        print("\nRecommended Courses\n")

        for recommendation in result["recommendations"]:

            print(
                recommendation
            )

        print("\nLearning Pathway\n")

        for pathway in result["learning_pathway"]:

            print(
                pathway
            )

        save_models()

        logger.info(
            "Recommendation System Completed Successfully."
        )

    except Exception as e:

        logger.exception(e)