class ExplanationEngine:

    @staticmethod
    def generate(
        course_name: str,
        predicted_rating: float,
        confidence_score: float,
        prerequisite_completed: bool
    ) -> str:
        """
        Generate a human-readable explanation for the recommendation.
        """

        reasons = []

        if predicted_rating >= 4.5:
            reasons.append("high predicted learner interest")

        elif predicted_rating >= 3.5:
            reasons.append("good predicted learner interest")

        if confidence_score >= 0.90:
            reasons.append("strong recommendation confidence")

        elif confidence_score >= 0.75:
            reasons.append("good recommendation confidence")

        if prerequisite_completed:
            reasons.append("prerequisite requirements satisfied")

        if not reasons:
            reasons.append("matches your learning profile")

        return (
            f"{course_name} is recommended because "
            + ", ".join(reasons)
            + "."
        )