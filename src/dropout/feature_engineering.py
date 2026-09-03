import pandas as pd


def engineer_dropout_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # ========================================================
    # Engagement Score
    # ========================================================

    df["engagement_score"] = (
        df["sessions_last_30_days"]
        + df["logins_last_30_days"]
        + df["videos_watched"]
        + df["discussion_interactions"]
    )

    # ========================================================
    # Learning Score
    # ========================================================

    df["learning_score"] = (
        df["completion_percentage"]
        + df["quiz_average"]
        + df["assignment_completion_rate"]
    ) / 3

    # ========================================================
    # Inactivity Score
    # ========================================================

    df["inactivity_score"] = (
        df["days_since_last_login"]
    )

    return df