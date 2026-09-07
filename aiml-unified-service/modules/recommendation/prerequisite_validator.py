# ============================================================
# PREREQUISITE VALIDATOR
# ============================================================


class PrerequisiteValidator:
    """
    Validates course prerequisites without directly
    connecting to PostgreSQL.

    Database data must be supplied by the calling
    service/API.
    """

    @staticmethod
    def has_completed_prerequisite(
        prerequisite_course_id,
        completed_courses
    ) -> bool:
        """
        Check whether a prerequisite course has been
        completed by the user.

        completed_courses should contain course IDs
        that the user has completed with the required
        completion threshold.
        """

        # No prerequisite required
        if prerequisite_course_id is None:
            return True

        if completed_courses is None:
            return False

        completed_courses = {
            str(course_id)
            for course_id in completed_courses
        }

        return (
            str(prerequisite_course_id)
            in completed_courses
        )


    # ========================================================
    # VALIDATE COURSE PREREQUISITES
    # ========================================================

    @staticmethod
    def validate(
        course_id,
        prerequisites,
        completed_courses
    ) -> bool:
        """
        Validate whether all prerequisites for a course
        have been completed by the user.

        Parameters
        ----------
        course_id:
            Course being recommended.

        prerequisites:
            Mapping or list containing prerequisite
            course relationships.

        completed_courses:
            Course IDs completed by the user.
        """

        if not prerequisites:
            return True

        # ----------------------------------------------------
        # Support list of prerequisite records
        # ----------------------------------------------------

        prerequisite_ids = []

        for prerequisite in prerequisites:

            if isinstance(
                prerequisite,
                dict
            ):

                current_course_id = (
                    prerequisite.get(
                        "course_id"
                    )
                )

                if (
                    current_course_id is not None
                    and str(current_course_id)
                    != str(course_id)
                ):
                    continue

                prerequisite_id = (
                    prerequisite.get(
                        "prerequisite_course_id"
                    )
                )

            else:

                prerequisite_id = prerequisite

            if prerequisite_id is not None:

                prerequisite_ids.append(
                    prerequisite_id
                )

        # ----------------------------------------------------
        # Check every prerequisite
        # ----------------------------------------------------

        for prerequisite_course_id in (
            prerequisite_ids
        ):

            completed = (
                PrerequisiteValidator
                .has_completed_prerequisite(
                    prerequisite_course_id,
                    completed_courses
                )
            )

            if not completed:
                return False

        return True