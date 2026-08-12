from psycopg2.extras import Json

from src.database.database_connection import get_connection
from src.logs.logger import logger


class FraudRepository:
    """
    Repository for storing fraud prediction results.
    """

    def save_prediction(
        self,
        student_id: int,
        fraud_probability: float,
        risk_level: str,
        fraud_prediction: int,
        anomaly_prediction: int
    ) -> None:

        connection = None

        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()

            cursor.execute(

                """
                INSERT INTO fraud_predictions
                (
                    student_id,
                    fraud_probability,
                    risk_level,
                    fraud_prediction,
                    anomaly_prediction
                )
                VALUES
                (%s, %s, %s, %s, %s)
                """,

                (

                    student_id,

                    fraud_probability,

                    risk_level,

                    fraud_prediction,

                    anomaly_prediction

                )

            )

            connection.commit()

            logger.info(

                f"Fraud prediction saved for Student ID: {student_id}"

            )

        except Exception as e:

            if connection:

                connection.rollback()

            logger.exception(

                f"Failed to save fraud prediction: {str(e)}"

            )

            raise

        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()


fraud_repository = FraudRepository()