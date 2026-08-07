class ConfidenceCalculator:

    @staticmethod
    def calculate(
        predicted_rating: float,
        similarity_score: float
    ) -> float:
        """
        Calculate recommendation confidence score.

        Parameters
        ----------
        predicted_rating : float
            Rating predicted by collaborative filtering.

        similarity_score : float
            Cosine similarity score from content-based recommendation.

        Returns
        -------
        float
            Confidence score between 0.00 and 1.00
        """

        # Normalize predicted rating (1-5) to (0-1)
        rating_score = predicted_rating / 5.0

        # Weighted confidence
        confidence = (
            (0.6 * rating_score) +
            (0.4 * similarity_score)
        )

        return round(min(confidence, 1.0), 2)