import pandas as pd
from sqlalchemy import text

from src.database.database_connection import engine


class FraudPreprocessor:
    """
    Load and preprocess Fraud Detection training data
    from the finalized education schema.
    """

    def load_data(self) -> pd.DataFrame:

        print("\nLoading Fraud Dataset...\n")

        query = """
        SELECT
            e.user_id,
            e.course_id,
            e.completion_percentage,

            p.watched_duration AS watch_time_minutes,
            p.quiz_score,

            cr.rating,

            e.status AS enrollment_status,

            a.sessions_last_30_days,
            a.avg_session_minutes,
            a.videos_watched,
            a.assignments_attempted,
            a.discussion_interactions,

            a.login_count,
            a.device_count,
            a.ip_changes,
            a.suspicious_activity_score

        FROM education.enrollments e

        LEFT JOIN education.progress p
            ON e.user_id = p.user_id
            AND e.course_id = p.course_id

        LEFT JOIN education.course_ratings cr
            ON e.user_id = cr.user_id
            AND e.course_id = cr.course_id

        LEFT JOIN education.activity_logs a
            ON e.user_id = a.user_id
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

        # Numeric columns
        numeric_columns = [
            "completion_percentage",
            "watch_time_minutes",
            "quiz_score",
            "rating",
            "sessions_last_30_days",
            "avg_session_minutes",
            "videos_watched",
            "assignments_attempted",
            "discussion_interactions",
            "login_count",
            "device_count",
            "ip_changes",
            "suspicious_activity_score"
        ]

        for column in numeric_columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

        dataframe[numeric_columns] = (
            dataframe[numeric_columns]
            .fillna(0)
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