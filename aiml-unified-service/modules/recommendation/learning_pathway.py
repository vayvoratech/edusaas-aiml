# ============================================================
# LEARNING PATHWAY
# ============================================================

class LearningPathway:

    @staticmethod
    def generate(
        recommendations: list,
        completed_courses: list | None = None
    ) -> list:
        """
        Generate a personalized learning pathway using
        completed courses supplied by the calling service
        and recommended courses.

        This module does NOT connect directly to PostgreSQL.
        """

        pathway = []

        completed_courses = (
            completed_courses or []
        )

        # ====================================================
        # COMPLETED COURSES
        # ====================================================

        for course in completed_courses:

            if isinstance(course, dict):

                course_id = course.get(
                    "course_id",
                    course.get("id")
                )

                course_name = course.get(
                    "course_name",
                    course.get("title", "")
                )

            else:

                course_id = getattr(
                    course,
                    "id",
                    None
                )

                course_name = getattr(
                    course,
                    "title",
                    ""
                )

            if course_id is None:
                continue

            pathway.append(
                {
                    "course_id": str(
                        course_id
                    ),

                    "course_name": str(
                        course_name
                    ),

                    "status": "COMPLETED"
                }
            )

        # ====================================================
        # RECOMMENDED COURSES
        # ====================================================

        for course in recommendations:

            pathway.append(
                {
                    "course_id": str(
                        course["course_id"]
                    ),

                    "course_name": str(
                        course["course_name"]
                    ),

                    "status": "RECOMMENDED"
                }
            )

        return pathway