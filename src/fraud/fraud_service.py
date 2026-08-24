import pandas as pd

from src.fraud.model_loader import fraud_model_loader
from src.fraud.fraud_feature_calculator import FraudFeatureCalculator


class FraudService:
    """
    Fraud Detection Inference Service.

    Uses pre-trained Random Forest and Isolation Forest
    models. No database connection is used here.
    """

    def __init__(self):

        self.random_forest = (
            fraud_model_loader.random_forest_model
        )

        self.isolation_forest = (
            fraud_model_loader.isolation_forest_model
        )

        self.feature_columns = (
            fraud_model_loader.feature_columns
        )

    def predict(self, student_data: dict):

        try:

            # ----------------------------------------
            # Convert request to DataFrame
            # ----------------------------------------

            dataframe = pd.DataFrame(
                [student_data]
            )

            # ----------------------------------------
            # Calculate engineered features
            # ----------------------------------------

            dataframe = (
                FraudFeatureCalculator.calculate(
                    dataframe
                )
            )

            # ----------------------------------------
            # Ensure exact training feature order
            # ----------------------------------------

            missing_features = [
                column
                for column in self.feature_columns
                if column not in dataframe.columns
            ]

            if missing_features:

                raise ValueError(
                    f"Missing Fraud features: "
                    f"{missing_features}"
                )

            dataframe = dataframe[
                self.feature_columns
            ]

            # ----------------------------------------
            # Random Forest Prediction
            # ----------------------------------------

            fraud_prediction = int(
                self.random_forest.predict(
                    dataframe
                )[0]
            )

            fraud_probability = float(
                self.random_forest.predict_proba(
                    dataframe
                )[0][1]
            )

            # ----------------------------------------
            # Isolation Forest Prediction
            # ----------------------------------------

            anomaly_prediction = int(
                self.isolation_forest.predict(
                    dataframe
                )[0]
            )

            # ----------------------------------------
            # Risk Level
            # ----------------------------------------

            if fraud_probability >= 0.80:

                risk_level = "HIGH"

            elif fraud_probability >= 0.50:

                risk_level = "MEDIUM"

            else:

                risk_level = "LOW"

            # ----------------------------------------
            # Human-readable labels
            # ----------------------------------------

            fraud_label = (
                "FRAUD"
                if fraud_prediction == 1
                else "NORMAL"
            )

            anomaly_status = (
                "ANOMALY"
                if anomaly_prediction == -1
                else "NORMAL"
            )

            # ----------------------------------------
            # Response
            # ----------------------------------------

            return {

                "student_id":
                    student_data["student_id"],

                "fraud_probability":
                    round(
                        fraud_probability,
                        4
                    ),

                "risk_level":
                    risk_level,

                "fraud_prediction":
                    fraud_label,

                "anomaly_status":
                    anomaly_status
            }

        except Exception as e:

            print(
                f"Fraud Prediction Failed: {e}"
            )

            raise


fraud_service = FraudService()