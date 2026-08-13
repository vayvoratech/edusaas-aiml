import pandas as pd


class FraudDataset:
    """
    Prepare dataset for Fraud Detection models.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.dataframe = dataframe.copy()

    def prepare(self):

        feature_columns = [

            # Learning Features
            "completion_percentage",
            "watch_time_minutes",
            "quiz_score",
            "rating",

            # Activity Features
            "sessions_last_30_days",
            "avg_session_minutes",
            "videos_watched",
            "assignments_attempted",
            "discussion_interactions",

            # Security Features
            "login_count",
            "device_count",
            "ip_changes",

            # Engineered Feature
            "suspicious_activity_score"

        ]

        X = self.dataframe[feature_columns]

        y = self.dataframe["is_fraud"]

        return X, y


if __name__ == "__main__":

    from src.fraud.preprocessing import FraudPreprocessor
    from src.fraud.feature_engineering import FraudFeatureEngineering

    processor = FraudPreprocessor()

    dataframe = processor.preprocess()

    engineer = FraudFeatureEngineering(dataframe)

    dataframe = engineer.create_features()

    X, y = FraudDataset(
        dataframe
    ).prepare()

    print("\nFeatures Shape :", X.shape)

    print("Labels Shape :", y.shape)

    print("\nFeature Columns\n")

    print(X.columns.tolist())