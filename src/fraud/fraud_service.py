import pandas as pd

from src.fraud.model_loader import fraud_model_loader
from src.fraud.fraud_repository import fraud_repository
from src.fraud.fraud_feature_calculator import FraudFeatureCalculator
from src.logs.logger import logger


class FraudService:
    """
    Fraud Detection Service
    """

    def __init__(self):

        self.random_forest = fraud_model_loader.random_forest_model

        self.isolation_forest = fraud_model_loader.isolation_forest_model

        self.feature_columns = fraud_model_loader.feature_columns

    def predict(
        self,
        student_data: dict
    ):

        try:

            logger.info(
                f"Fraud Prediction | Student={student_data['student_id']}"
            )

            # ----------------------------------------
            # Convert Request to DataFrame
            # ----------------------------------------

            dataframe = pd.DataFrame([student_data])

            # ----------------------------------------
            # Calculate Engineered Features
            # ----------------------------------------

            dataframe = FraudFeatureCalculator.calculate(
                dataframe
            )

            # ----------------------------------------
            # Keep Only Training Features
            # ----------------------------------------

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
            # Save Prediction
            # ----------------------------------------

            fraud_repository.save_prediction(

                student_id=student_data["student_id"],

                fraud_probability=round(
                    fraud_probability,
                    4
                ),

                risk_level=risk_level,

                fraud_prediction=fraud_prediction,

                anomaly_prediction=anomaly_prediction

            )

            # ----------------------------------------
            # Human Readable Labels
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

            logger.info(
                "Fraud Prediction Completed"
            )

            # ----------------------------------------
            # Response
            # ----------------------------------------

            return {

                "student_id": student_data["student_id"],

                "fraud_probability": round(
                    fraud_probability,
                    4
                ),

                "risk_level": risk_level,

                "fraud_prediction": fraud_label,

                "anomaly_status": anomaly_status

            }

        except Exception as e:

            logger.exception(
                "Fraud Prediction Failed"
            )

            raise


fraud_service = FraudService()