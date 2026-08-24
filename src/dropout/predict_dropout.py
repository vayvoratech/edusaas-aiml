import joblib
import pandas as pd


# ============================================================
# Model Paths
# ============================================================

MODEL_PATH = "models/dropout_random_forest.pkl"
FEATURES_PATH = "models/dropout_feature_columns.pkl"


# ============================================================
# Load Model Once
# ============================================================

model = joblib.load(MODEL_PATH)

feature_columns = joblib.load(
    FEATURES_PATH
)


# ============================================================
# Prediction
# ============================================================

def predict_dropout(student_data):

    # --------------------------------------------------------
    # Convert Node JSON to DataFrame
    # --------------------------------------------------------

    student_df = pd.DataFrame(
        [student_data]
    )


    # --------------------------------------------------------
    # Required Raw Features
    # --------------------------------------------------------

    required_features = [
        "sessions_last_30_days",
        "avg_session_minutes",
        "videos_watched",
        "assignments_attempted",
        "discussion_interactions",
        "logins_last_30_days",
        "days_since_last_login",
        "completion_percentage",
        "quiz_average",
        "assignment_completion_rate"
    ]


    missing_features = [
        feature
        for feature in required_features
        if feature not in student_df.columns
    ]


    if missing_features:

        raise ValueError(
            "Missing required dropout features: "
            + ", ".join(missing_features)
        )


    # --------------------------------------------------------
    # Feature Engineering
    # Must match training exactly
    # --------------------------------------------------------

    student_df["engagement_score"] = (
        student_df["sessions_last_30_days"]
        + student_df["logins_last_30_days"]
        + student_df["videos_watched"]
        + student_df["discussion_interactions"]
    )


    student_df["learning_score"] = (
        student_df["completion_percentage"]
        + student_df["quiz_average"]
        + student_df["assignment_completion_rate"]
    ) / 3


    student_df["inactivity_score"] = (
        student_df["days_since_last_login"]
    )


    # --------------------------------------------------------
    # Ensure Exact Training Feature Order
    # --------------------------------------------------------

    missing_model_features = [
        feature
        for feature in feature_columns
        if feature not in student_df.columns
    ]


    if missing_model_features:

        raise ValueError(
            "Missing model features: "
            + ", ".join(missing_model_features)
        )


    student_df = student_df[
        feature_columns
    ]


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        student_df
    )[0]


    probability = model.predict_proba(
        student_df
    )[0][1]


    # --------------------------------------------------------
    # Risk Level
    # --------------------------------------------------------

    if probability >= 0.70:

        risk_level = "HIGH"

    elif probability >= 0.40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "dropout_prediction": int(
            prediction
        ),

        "dropout_probability": round(
            float(probability),
            4
        ),

        "risk_level": risk_level
    }