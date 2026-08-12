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

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Final database currently being used
DB_NAME = "eduai_db"

# Finalized AI recommendation schema
SCHEMA = "education"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# LOAD COURSES
# ============================================================

logger.info("Loading courses...")

courses = pd.read_sql(
    f"""
    SELECT
        id,
        title,
        description,
        provider,
        category,
        difficulty,
        status,
        educator_id
    FROM {SCHEMA}.courses
    WHERE status = 'active'
    """,
    engine
)

if courses.empty:
    raise ValueError(
        "No active courses found in education.courses"
    )

logger.info(
    f"Loaded {len(courses)} active courses."
)


# ============================================================
# LOAD COURSE RATINGS
# ============================================================

logger.info("Loading course ratings...")

ratings = pd.read_sql(
    f"""
    SELECT
        user_id,
        course_id,
        rating
    FROM {SCHEMA}.course_ratings
    WHERE rating IS NOT NULL
    """,
    engine
)

if ratings.empty:
    raise ValueError(
        "No ratings found in education.course_ratings"
    )

logger.info(
    f"Loaded {len(ratings)} course ratings."
)


# ============================================================
# LOAD USERS + DOMAIN ROLES
# ============================================================

logger.info("Loading users...")

users = pd.read_sql(
    f"""
    SELECT
        u.id,
        u.name,
        u.email,
        u.role_id,
        u.domain_role_id,
        dr.domain_name,
        dr.category AS domain_category
    FROM {SCHEMA}.users u
    LEFT JOIN {SCHEMA}.domain_roles dr
        ON u.domain_role_id = dr.domain_role_id
    """,
    engine
)

if users.empty:
    raise ValueError(
        "No users found in education.users"
    )

logger.info(
    f"Loaded {len(users)} users."
)


# ============================================================
# CONTENT-BASED FEATURES
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
# CONTENT VECTOR REPRESENTATION
# ============================================================

vectorizer = CountVectorizer(
    stop_words="english"
)

feature_matrix = vectorizer.fit_transform(
    courses["features"]
)


# ============================================================
# CONTENT SIMILARITY
# ============================================================

content_similarity = cosine_similarity(
    feature_matrix
)

logger.info(
    "Content similarity matrix created successfully."
)


# ============================================================
# COLLABORATIVE FILTERING
# ============================================================

reader = Reader(
    rating_scale=(1, 5)
)

dataset = Dataset.load_from_df(
    ratings[
        [
            "user_id",
            "course_id",
            "rating"
        ]
    ],
    reader
)

trainset = dataset.build_full_trainset()

svd_model = SVD(
    random_state=42
)

svd_model.fit(
    trainset
)

logger.info(
    "Collaborative filtering SVD model trained successfully."
)


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def recommend(
    user_id,
    course_name
):

    logger.info(
        f"Generating recommendations for User {user_id}"
    )

    # --------------------------------------------------------
    # Find input course
    # --------------------------------------------------------

    matched_course = courses[
        courses["title"].str.lower()
        == course_name.lower()
    ]

    if matched_course.empty:

        raise ValueError(
            f"Course '{course_name}' not found."
        )

    matched_course = matched_course.iloc[0]

    idx = matched_course.name


    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = users[
        users["id"] == user_id
    ]

    if user.empty:

        raise ValueError(
            f"User '{user_id}' not found."
        )

    user = user.iloc[0]


    # --------------------------------------------------------
    # User profile
    # --------------------------------------------------------

    domain_name = (
        str(user["domain_name"])
        if pd.notna(user["domain_name"])
        else ""
    )

    domain_category = (
        str(user["domain_category"])
        if pd.notna(user["domain_category"])
        else ""
    )


    # --------------------------------------------------------
    # Content similarity
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Generate candidates
    # --------------------------------------------------------

    recommendations = []

    for item in distances[1:21]:

        course_index = item[0]

        course = courses.iloc[
            course_index
        ]

        similarity_score = float(
            item[1]
        )


        # ----------------------------------------------------
        # Collaborative filtering prediction
        # ----------------------------------------------------

        predicted_rating = svd_model.predict(
            str(user_id),
            str(course["id"])
        ).est


        # ----------------------------------------------------
        # Profile matching
        # ----------------------------------------------------

        profile_score = 0.0

        course_category = str(
            course["category"]
        )

        course_difficulty = str(
            course["difficulty"]
        )


        # Domain category match
        if (
            domain_category
            and domain_category.lower()
            in course_category.lower()
        ):
            profile_score += 0.20


        # Domain/role match
        if (
            domain_name
            and domain_name.lower()
            in course_category.lower()
        ):
            profile_score += 0.20


        # ----------------------------------------------------
        # Confidence score
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Prerequisite validation
        # ----------------------------------------------------

        prerequisite_completed = True

        try:

            prerequisite_result = (
                PrerequisiteValidator.validate(
                    user_id,
                    course["id"]
                )
            )

            if isinstance(
                prerequisite_result,
                bool
            ):
                prerequisite_completed = (
                    prerequisite_result
                )

        except Exception as exc:

            logger.warning(
                "Prerequisite validation skipped "
                "for course %s: %s",
                course["id"],
                exc
            )

            prerequisite_completed = True


        # ----------------------------------------------------
        # Explanation
        # ----------------------------------------------------

        explanation = (
            ExplanationEngine.generate(
                course_name=course["title"],
                predicted_rating=predicted_rating,
                confidence_score=confidence_score,
                prerequisite_completed=(
                    prerequisite_completed
                )
            )
        )


        # ----------------------------------------------------
        # Recommendation object
        # ----------------------------------------------------

        recommendations.append(
            {
                "course_id": str(
                    course["id"]
                ),

                "course_name": (
                    course["title"]
                ),

                "category": (
                    course["category"]
                ),

                "difficulty": (
                    course["difficulty"]
                ),

                "predicted_rating": round(
                    float(predicted_rating),
                    2
                ),

                "similarity_score": round(
                    float(similarity_score),
                    2
                ),

                "confidence_score": round(
                    float(confidence_score),
                    2
                ),

                "recommendation_reason": (
                    explanation
                ),

                "prerequisite_completed": (
                    prerequisite_completed
                )
            }
        )


    # ========================================================
    # FINAL RANKING
    # ========================================================

    recommendations = sorted(
        recommendations,
        key=lambda x: (
            x["confidence_score"],
            x["predicted_rating"],
            x["similarity_score"]
        ),
        reverse=True
    )[:5]


    # ========================================================
    # LEARNING PATHWAY
    # ========================================================

    try:

        learning_pathway = (
            LearningPathway.generate(
                user_id,
                recommendations
            )
        )

    except Exception as exc:

        logger.warning(
            "Learning pathway generation failed: %s",
            exc
        )

        learning_pathway = []


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "user_id": str(
            user_id
        ),

        "course_name": (
            course_name
        ),

        "recommendations": (
            recommendations
        ),

        "learning_pathway": (
            learning_pathway
        )
    }


# ============================================================
# SAVE MODEL ARTIFACTS
# ============================================================

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


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        logger.info(
            "Hybrid Recommendation System Started"
        )


        # ----------------------------------------------------
        # Pick a real user from the database
        # ----------------------------------------------------

        sample_user_id = users.iloc[0]["id"]

        sample_course = courses.iloc[0]["title"]


        # ----------------------------------------------------
        # Generate recommendations
        # ----------------------------------------------------

        result = recommend(
            user_id=sample_user_id,
            course_name=sample_course
        )


        # ----------------------------------------------------
        # Print result
        # ----------------------------------------------------

        print()
        print(
            "=" * 60
        )

        print(
            "Hybrid Recommendation Result"
        )

        print(
            "=" * 60
        )

        print(
            f"User ID    : "
            f"{result['user_id']}"
        )

        print(
            f"Course     : "
            f"{result['course_name']}"
        )


        print()
        print(
            "Recommended Courses"
        )

        print(
            "-" * 60
        )


        for recommendation in (
            result["recommendations"]
        ):

            print(
                recommendation
            )


        print()
        print(
            "Learning Pathway"
        )

        print(
            "-" * 60
        )


        for pathway in (
            result["learning_pathway"]
        ):

            print(
                pathway
            )


        # ----------------------------------------------------
        # Save artifacts
        # ----------------------------------------------------

        save_models()


        logger.info(
            "Recommendation System Completed Successfully."
        )


    except Exception as e:

        logger.exception(
            "Recommendation System Failed: %s",
            e
        )

        raise