import pandas as pd

from sqlalchemy import text

from src.database.database_connection import engine


class FraudPreprocessor:
    """
    Load and preprocess fraud detection dataset.
    """

    def load_data(self) -> pd.DataFrame:

        print("\nLoading Fraud Dataset...\n")

        query = """
        SELECT

            e.student_id,

            e.course_id,

            e.completion_percentage,

            e.watch_time_minutes,

            e.quiz_score,

            e.rating,

            e.payment_status,

            e.enrollment_source,

            e.enrollment_status,

            e.is_fraud,

            a.sessions_last_30_days,

            a.avg_session_minutes,

            a.videos_watched,

            a.assignments_attempted,

            a.discussion_interactions,

            a.login_count,

            a.device_count,

            a.ip_changes,

            a.suspicious_activity_score

        FROM enrollments e

        INNER JOIN activity_logs a

        ON e.student_id = a.student_id
        """

        dataframe = pd.read_sql(

            text(query),

            engine

        )

        print(f"Original Shape : {dataframe.shape}")

        return dataframe

    def preprocess(self) -> pd.DataFrame:

        dataframe = self.load_data()

        print("\nPreprocessing Dataset...\n")

        dataframe.drop_duplicates(

            inplace=True

        )

        dataframe.dropna(

            inplace=True

        )

        dataframe.reset_index(

            drop=True,

            inplace=True

        )

        print(f"Processed Shape : {dataframe.shape}")

        return dataframe


if __name__ == "__main__":

    processor = FraudPreprocessor()

    dataframe = processor.preprocess()

    print("\nDataset Preview\n")

    print(dataframe.head())