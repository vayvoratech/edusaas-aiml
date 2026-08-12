from sqlalchemy import text

from src.database.database_connection import engine


class SentimentRepository:

    def save_prediction(
        self,
        student_id,
        course_id,
        discussion_id,
        post_text,
        prediction,
        confidence,
        negative_score,
        neutral_score,
        positive_score
    ):

        query = text("""

        INSERT INTO sentiment_predictions
        (
            student_id,
            course_id,
            discussion_id,
            post_text,
            prediction,
            confidence,
            negative_score,
            neutral_score,
            positive_score
        )

        VALUES
        (
            :student_id,
            :course_id,
            :discussion_id,
            :post_text,
            :prediction,
            :confidence,
            :negative_score,
            :neutral_score,
            :positive_score
        )

        """)

        with engine.begin() as connection:

            connection.execute(

                query,

                {

                    "student_id": student_id,

                    "course_id": course_id,

                    "discussion_id": discussion_id,

                    "post_text": post_text,

                    "prediction": prediction,

                    "confidence": confidence,

                    "negative_score": negative_score,

                    "neutral_score": neutral_score,

                    "positive_score": positive_score

                }

            )


repository = SentimentRepository()