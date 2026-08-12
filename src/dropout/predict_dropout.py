import joblib
import pandas as pd

# --------------------------------
# Load Model and Feature Columns
# --------------------------------

MODEL_PATH = "models/dropout_random_forest.pkl"
FEATURES_PATH = "models/dropout_feature_columns.pkl"

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURES_PATH)


# --------------------------------
# Dropout Prediction Function
# --------------------------------

def predict_dropout(student_data):

    # Convert input into DataFrame
    student_df = pd.DataFrame([student_data])

    # --------------------------------
    # Feature Engineering
    # Must match training logic
    # --------------------------------

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

    # Ensure exact same feature order as training
    student_df = student_df[feature_columns]

    # --------------------------------
    # Prediction
    # --------------------------------

    prediction = model.predict(student_df)[0]

    probability = model.predict_proba(student_df)[0][1]

    # --------------------------------
    # Risk Classification
    # --------------------------------

    if probability >= 0.7:
        risk_level = "HIGH"

    elif probability >= 0.4:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "dropout_prediction": int(prediction),
        "dropout_probability": round(float(probability), 4),
        "risk_level": risk_level
    }