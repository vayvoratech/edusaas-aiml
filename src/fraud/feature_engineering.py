import pandas as pd

from src.fraud.fraud_feature_calculator import FraudFeatureCalculator


class FraudFeatureEngineering:
    """
    Create engineered features for Fraud Detection.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.dataframe = dataframe.copy()

    def create_features(
        self
    ) -> pd.DataFrame:

        print("\nCreating Fraud Features...\n")

        self.dataframe = FraudFeatureCalculator.calculate(

            self.dataframe

        )

        print(

            f"Final Dataset Shape : {self.dataframe.shape}"

        )

        return self.dataframe


if __name__ == "__main__":

    from src.fraud.preprocessing import FraudPreprocessor

    processor = FraudPreprocessor()

    dataframe = processor.preprocess()

    engineer = FraudFeatureEngineering(

        dataframe

    )

    dataframe = engineer.create_features()

    print("\nFeature Preview\n")

    print(

        dataframe[
            [
                "engagement_score",
                "login_frequency_score",
                "device_risk_score",
                "learning_consistency_score",
                "suspicious_activity_score",
                "fraud_risk_score"
            ]
        ].head()

    )