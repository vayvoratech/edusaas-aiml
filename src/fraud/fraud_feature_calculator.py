import pandas as pd


class FraudFeatureCalculator:
    """
    Calculate engineered features for Fraud Detection.
    Uses the finalized education schema fields.
    """

    @staticmethod
    def calculate(
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:

        dataframe = dataframe.copy()

        # ----------------------------------------
        # Fill missing values
        # ----------------------------------------

        numeric_columns = [
            "completion_percentage",
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
        ]

        for column in numeric_columns:

            if column not in dataframe.columns:
                dataframe[column] = 0

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            ).fillna(0)

        # ----------------------------------------
        # Engagement Score
        # ----------------------------------------

        dataframe["engagement_score"] = (
            dataframe["videos_watched"] * 0.30
            + dataframe["assignments_attempted"] * 0.30
            + dataframe["discussion_interactions"] * 0.20
            + dataframe["completion_percentage"] * 0.20
        )

        # ----------------------------------------
        # Login Frequency Score
        # ----------------------------------------

        dataframe["login_frequency_score"] = (
            dataframe["login_count"]
            / dataframe["sessions_last_30_days"].replace(0, 1)
        ).round(2)

        # ----------------------------------------
        # Device Risk Score
        # ----------------------------------------

        dataframe["device_risk_score"] = (
            dataframe["device_count"]
            + dataframe["ip_changes"]
        )

        # ----------------------------------------
        # Learning Consistency Score
        # ----------------------------------------

        dataframe["learning_consistency_score"] = (
            dataframe["completion_percentage"]
            + dataframe["quiz_score"]
        ) / 2

        # ----------------------------------------
        # Suspicious Activity Score
        # ----------------------------------------

        calculated_score = (
            dataframe["login_count"] * 0.30
            + dataframe["device_count"] * 10
            + dataframe["ip_changes"] * 5
        )

        # Use DB-provided suspicious score when available.
        if "suspicious_activity_score" in dataframe.columns:

            db_score = pd.to_numeric(
                dataframe["suspicious_activity_score"],
                errors="coerce"
            )

            dataframe["suspicious_activity_score"] = (
                db_score.fillna(calculated_score)
            ).round(2)

        else:

            dataframe["suspicious_activity_score"] = (
                calculated_score.round(2)
            )

        # ----------------------------------------
        # Fraud Risk Score
        # ----------------------------------------

        dataframe["fraud_risk_score"] = (
            dataframe["suspicious_activity_score"] * 0.50
            + dataframe["device_risk_score"] * 2
            + dataframe["login_frequency_score"] * 1.50
        ).round(2)

        return dataframe