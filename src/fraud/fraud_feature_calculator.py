import pandas as pd


class FraudFeatureCalculator:
    """
    Calculate engineered features for Fraud Detection.
    """

    @staticmethod
    def calculate(
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:

        dataframe = dataframe.copy()

        # ----------------------------------------
        # Engagement Score
        # ----------------------------------------

        dataframe["engagement_score"] = (

            dataframe["videos_watched"] * 0.30 +

            dataframe["assignments_attempted"] * 0.30 +

            dataframe["discussion_interactions"] * 0.20 +

            dataframe["completion_percentage"] * 0.20

        )

        # ----------------------------------------
        # Login Frequency Score
        # ----------------------------------------

        dataframe["login_frequency_score"] = (

            dataframe["login_count"] /

            dataframe["sessions_last_30_days"].replace(0, 1)

        ).round(2)

        # ----------------------------------------
        # Device Risk Score
        # ----------------------------------------

        dataframe["device_risk_score"] = (

            dataframe["device_count"] +

            dataframe["ip_changes"]

        )

        # ----------------------------------------
        # Learning Consistency Score
        # ----------------------------------------

        dataframe["learning_consistency_score"] = (

            dataframe["completion_percentage"] +

            dataframe["quiz_score"]

        ) / 2

        # ----------------------------------------
        # Suspicious Activity Score
        # ----------------------------------------

        score = (

            dataframe["login_count"] * 0.30 +

            dataframe["device_count"] * 10 +

            dataframe["ip_changes"] * 5

        )

        if "payment_status" in dataframe.columns:

            score += (

                dataframe["payment_status"] == "FAILED"

            ).astype(int) * 20

        if "enrollment_source" in dataframe.columns:

            score += (

                dataframe["enrollment_source"].isin(

                    ["BOT", "API"]

                )

            ).astype(int) * 15

        if "enrollment_status" in dataframe.columns:

            score += (

                dataframe["enrollment_status"] == "SUSPICIOUS"

            ).astype(int) * 15

        dataframe["suspicious_activity_score"] = score.round(2)

        # ----------------------------------------
        # Fraud Risk Score
        # ----------------------------------------

        dataframe["fraud_risk_score"] = (

            dataframe["suspicious_activity_score"] * 0.50 +

            dataframe["device_risk_score"] * 2 +

            dataframe["login_frequency_score"] * 1.50

        ).round(2)

        return dataframe