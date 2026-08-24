import pandas as pd

from src.hiring.model_loader import hiring_model_loader


class HiringService:
    """
    Predictive Hiring Service.

    Matches a student profile against a job
    using the trained Random Forest model.
    """

    def __init__(self):

        self.model = (
            hiring_model_loader.model
        )

        self.feature_columns = (
            hiring_model_loader.feature_columns
        )

    def predict(
        self,
        student_data: dict
    ):

        # ----------------------------------------
        # Convert input to DataFrame
        # ----------------------------------------

        dataframe = pd.DataFrame(
            [student_data]
        )

        # ----------------------------------------
        # Validate required features
        # ----------------------------------------

        missing_columns = [

            column

            for column in self.feature_columns

            if column not in dataframe.columns

        ]

        if missing_columns:

            raise ValueError(
                f"Missing features: {missing_columns}"
            )

        # ----------------------------------------
        # Keep training features
        # ----------------------------------------

        dataframe = dataframe[
            self.feature_columns
        ]

        # ----------------------------------------
        # Model prediction
        # ----------------------------------------

        prediction = int(
            self.model.predict(
                dataframe
            )[0]
        )

        probability = float(
            self.model.predict_proba(
                dataframe
            )[0][1]
        )

        # ----------------------------------------
        # Match percentage
        # ----------------------------------------

        match_percentage = round(
            probability * 100,
            2
        )

        # ----------------------------------------
        # Match level
        # ----------------------------------------

        if probability >= 0.80:

            match_level = "EXCELLENT"

        elif probability >= 0.60:

            match_level = "GOOD"

        elif probability >= 0.40:

            match_level = "MODERATE"

        else:

            match_level = "LOW"

        # ----------------------------------------
        # Final response
        # ----------------------------------------

        return {

            "match_prediction":
                "MATCHED"
                if prediction == 1
                else "NOT_MATCHED",

            "match_probability":
                round(
                    probability,
                    4
                ),

            "match_percentage":
                match_percentage,

            "match_level":
                match_level

        }


hiring_service = HiringService()