import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CONTENT-BASED RECOMMENDATION
# ============================================================

class ContentBasedRecommender:
    """
    Content-based course recommendation model.

    The model does NOT connect directly to PostgreSQL.
    Course data must be supplied by the calling service/API.
    """

    def __init__(self, courses):

        if courses is None or courses.empty:

            raise ValueError(
                "Course dataset cannot be empty."
            )

        self.courses = courses.copy()

        self._prepare_data()

        self.vectorizer = CountVectorizer(
            stop_words="english"
        )

        self.feature_matrix = (
            self.vectorizer.fit_transform(
                self.courses["features"]
            )
        )

        self.similarity_matrix = cosine_similarity(
            self.feature_matrix
        )

        print(
            "✅ Content-based similarity matrix "
            "created successfully"
        )

        print(
            f"Courses loaded: {len(self.courses)}"
        )


    # ========================================================
    # PREPARE DATA
    # ========================================================

    def _prepare_data(self):

        required_columns = [
            "id",
            "title",
            "description",
            "provider",
            "category",
            "difficulty",
            "status",
            "educator_id"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.courses.columns
        ]

        if missing_columns:

            raise ValueError(
                f"Missing course columns: "
                f"{missing_columns}"
            )

        self.courses["title"] = (
            self.courses["title"]
            .fillna("")
            .astype(str)
        )

        self.courses["description"] = (
            self.courses["description"]
            .fillna("")
            .astype(str)
        )

        self.courses["category"] = (
            self.courses["category"]
            .fillna("")
            .astype(str)
        )

        self.courses["difficulty"] = (
            self.courses["difficulty"]
            .fillna("")
            .astype(str)
        )

        self.courses["features"] = (
            self.courses["title"] + " " +
            self.courses["description"] + " " +
            self.courses["category"] + " " +
            self.courses["difficulty"]
        )


    # ========================================================
    # RECOMMEND COURSES
    # ========================================================

    def recommend(
        self,
        course_name,
        number_of_recommendations=5
    ):

        matches = self.courses[
            self.courses["title"].str.lower()
            == course_name.lower()
        ]

        if matches.empty:

            raise ValueError(
                f"Course not found: {course_name}"
            )

        course_index = matches.index[0]

        matrix_index = (
            self.courses.index
            .get_loc(course_index)
        )

        distances = list(
            enumerate(
                self.similarity_matrix[
                    matrix_index
                ]
            )
        )

        distances = sorted(
            distances,
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = []

        for matrix_position, score in distances:

            if matrix_position == matrix_index:
                continue

            course = self.courses.iloc[
                matrix_position
            ]

            recommendations.append({

                "course_id": str(
                    course["id"]
                ),

                "course_name": course[
                    "title"
                ],

                "similarity_score": round(
                    float(score),
                    4
                )

            })

            if (
                len(recommendations)
                >= number_of_recommendations
            ):
                break

        return recommendations


# ============================================================
# FACTORY
# ============================================================

def create_content_recommender(courses):

    return ContentBasedRecommender(
        courses
    )