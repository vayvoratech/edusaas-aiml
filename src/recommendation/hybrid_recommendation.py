import logging
import pandas as pd

from src.recommendation.model_loader import (
    load_recommendation_models
)

from src.recommendation.confidence_calculator import (
    ConfidenceCalculator
)

from src.recommendation.explanation_engine import (
    ExplanationEngine
)

from src.recommendation.learning_pathway import (
    LearningPathway
)

from src.recommendation.prerequisite_validator import (
    PrerequisiteValidator
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def recommend(
    user_id,
    course_name: str,
    courses,
    user=None,
    prerequisites=None,
    completed_courses=None
):
    """
    Generate hybrid course recommendations.

    This function does NOT connect directly to PostgreSQL.

    Parameters
    ----------
    user_id:
        User UUID.

    course_name:
        Course from which recommendations are generated.

    courses:
        Course DataFrame supplied by the calling service.

    user:
        User profile dictionary/DataFrame row.

    prerequisites:
        Course prerequisite relationships.

    completed_courses:
        Courses completed by the user.
    """

    logger.info(
        "Generating recommendations for user %s",
        user_id
    )

    # ========================================================
    # VALIDATE COURSES
    # ========================================================

    if courses is None:

        raise ValueError(
            "Course data is required."
        )

    if isinstance(courses, list):

        courses = pd.DataFrame(
            courses
        )

    if courses.empty:

        raise ValueError(
            "No course data supplied."
        )

    required_columns = [
        "id",
        "title",
        "category",
        "difficulty"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in courses.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing course columns: "
            f"{missing_columns}"
        )

    courses = courses.copy()

    courses["title"] = (
        courses["title"]
        .fillna("")
        .astype(str)
    )

    courses["category"] = (
        courses["category"]
        .fillna("")
        .astype(str)
    )

    courses["difficulty"] = (
        courses["difficulty"]
        .fillna("")
        .astype(str)
    )

    # ========================================================
    # LOAD TRAINED ARTIFACTS
    # ========================================================

    (
        svd_model,
        content_vectorizer,
        content_similarity
    ) = load_recommendation_models()

    # ========================================================
    # FIND INPUT COURSE
    # ========================================================

    matched_course = courses[
        courses["title"].str.lower()
        == course_name.lower()
    ]

    if matched_course.empty:

        raise ValueError(
            f"Course '{course_name}' not found."
        )

    matched_course = matched_course.iloc[0]

    course_index = matched_course.name

    # DataFrame position is required for similarity matrix
    matrix_index = (
        courses.index
        .get_loc(course_index)
    )

    # ========================================================
    # USER PROFILE
    # ========================================================

    domain_name = ""
    domain_category = ""

    if user is not None:

        if isinstance(user, pd.DataFrame):

            if not user.empty:

                user = user.iloc[0].to_dict()

        elif not isinstance(user, dict):

            try:

                user = dict(user)

            except Exception:

                user = None

    if user:

        domain_name = str(
            user.get(
                "domain_name",
                ""
            ) or ""
        )

        domain_category = str(
            user.get(
                "domain_category",
                ""
            ) or ""
        )

    # ========================================================
    # CONTENT SIMILARITY
    # ========================================================

    try:

        similarity_scores = (
            content_similarity[
                matrix_index
            ]
        )

    except Exception as exc:

        logger.error(
            "Content similarity lookup failed: %s",
            exc
        )

        raise ValueError(
            "Content similarity artifact does not "
            "match the supplied course dataset."
        )

    distances = list(
        enumerate(
            similarity_scores
        )
    )

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )

    # ========================================================
    # GENERATE CANDIDATES
    # ========================================================

    recommendations = []

    for matrix_position, similarity_score in (
        distances[1:21]
    ):

        course = courses.iloc[
            matrix_position
        ]

        course_id = str(
            course["id"]
        )

        # ====================================================
        # COLLABORATIVE FILTERING
        # ====================================================

        prediction = svd_model.predict(
            str(user_id),
            course_id
        )

        predicted_rating = float(
            prediction.est
        )

        # ====================================================
        # PROFILE MATCHING
        # ====================================================

        profile_score = 0.0

        course_category = str(
            course["category"]
        )

        if (
            domain_category
            and domain_category.lower()
            in course_category.lower()
        ):

            profile_score += 0.20

        if (
            domain_name
            and domain_name.lower()
            in course_category.lower()
        ):

            profile_score += 0.20

        # ====================================================
        # CONFIDENCE
        # ====================================================

        confidence_score = (
            ConfidenceCalculator.calculate(
                predicted_rating,
                float(similarity_score)
            )
        )

        confidence_score = min(
            confidence_score + profile_score,
            1.0
        )

        # ====================================================
        # PREREQUISITE VALIDATION
        # ====================================================

        prerequisite_completed = True

        try:

            prerequisite_completed = (
                PrerequisiteValidator.validate(
                    course_id=course_id,
                    prerequisites=(
                        prerequisites or []
                    ),
                    completed_courses=(
                        completed_courses or []
                    )
                )
            )

        except Exception as exc:

            logger.warning(
                "Prerequisite validation failed "
                "for course %s: %s",
                course_id,
                exc
            )

            prerequisite_completed = True

        # ====================================================
        # EXPLANATION
        # ====================================================

        explanation = (
            ExplanationEngine.generate(
                course_name=str(
                    course["title"]
                ),
                predicted_rating=(
                    predicted_rating
                ),
                confidence_score=(
                    confidence_score
                ),
                prerequisite_completed=(
                    prerequisite_completed
                )
            )
        )

        # ====================================================
        # RECOMMENDATION OBJECT
        # ====================================================

        recommendations.append({

            "course_id":
                course_id,

            "course_name":
                str(course["title"]),

            "category":
                str(course["category"]),

            "difficulty":
                str(course["difficulty"]),

            "predicted_rating":
                round(
                    predicted_rating,
                    2
                ),

            "similarity_score":
                round(
                    float(similarity_score),
                    2
                ),

            "confidence_score":
                round(
                    float(confidence_score),
                    2
                ),

            "recommendation_reason":
                explanation,

            "prerequisite_completed":
                prerequisite_completed
        })

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
                recommendations=(
                    recommendations
                ),
                completed_courses=(
                    completed_courses or []
                )
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

        "user_id":
            str(user_id),

        "course_name":
            course_name,

        "recommendations":
            recommendations,

        "learning_pathway":
            learning_pathway
    }