from psycopg2.extras import Json

from src.database.database_connection import get_connection
from src.logs.logger import logger


class ToxicityRepository:
    """
    Repository for storing toxicity predictions.
    """

    def save_prediction(
        self,
        student_id: int,
        discussion_id: int,
        post_text: str,
        predictions: list
    ) -> None:

        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()

            query = """
                INSERT INTO toxicity_predictions
                (
                    student_id,
                    discussion_id,
                    post_text,
                    predictions
                )
                VALUES
                (%s, %s, %s, %s)
            """

            cursor.execute(

                query,

                (

                    student_id,

                    discussion_id,

                    post_text,

                    Json(predictions)

                )

            )

            connection.commit()

            logger.info(
                f"Toxicity prediction saved successfully for Student ID: {student_id}"
            )

        except Exception as e:

            if connection:

                connection.rollback()

            logger.exception(
                f"Failed to save toxicity prediction: {str(e)}"
            )

            raise

        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()


toxicity_repository = ToxicityRepository()
