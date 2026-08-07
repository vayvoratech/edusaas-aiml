import os
import joblib


MODEL_PATH = "models/fraud"


class FraudModelLoader:
    """
    Load trained Fraud Detection models.
    """

    def __init__(self):

        self.random_forest_model = None

        self.isolation_forest_model = None

        self.feature_columns = None

        self.load_models()

    def load_models(self):

        print("\nLoading Fraud Detection Models...\n")

        self.random_forest_model = joblib.load(

            os.path.join(

                MODEL_PATH,

                "fraud_random_forest.pkl"

            )

        )

        self.isolation_forest_model = joblib.load(

            os.path.join(

                MODEL_PATH,

                "fraud_isolation_forest.pkl"

            )

        )

        self.feature_columns = joblib.load(

            os.path.join(

                MODEL_PATH,

                "fraud_feature_columns.pkl"

            )

        )

        print("Fraud Models Loaded Successfully")


fraud_model_loader = FraudModelLoader()