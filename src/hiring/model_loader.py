import os
import joblib


MODEL_DIR = "models/hiring"


class HiringModelLoader:
    """
    Load trained Predictive Hiring model.
    """

    def __init__(self):

        self.model = None

        self.feature_columns = None

        self.load_models()

    def load_models(self):

        print(
            "\nLoading Predictive Hiring Model...\n"
        )

        self.model = joblib.load(
            os.path.join(
                MODEL_DIR,
                "hiring_random_forest.pkl"
            )
        )

        self.feature_columns = joblib.load(
            os.path.join(
                MODEL_DIR,
                "hiring_feature_columns.pkl"
            )
        )

        print(
            "Predictive Hiring Model Loaded Successfully"
        )

        print(
            f"Features: {self.feature_columns}"
        )


hiring_model_loader = HiringModelLoader()