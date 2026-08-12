import pandas as pd
import joblib
import os

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)


# --------------------------------
# PostgreSQL Configuration
# --------------------------------

DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# --------------------------------
# Load Data
# --------------------------------

query = """
SELECT
    a.student_id,
    a.sessions_last_30_days,
    a.avg_session_minutes,
    a.videos_watched,
    a.assignments_attempted,
    a.discussion_interactions,

    l.logins_last_30_days,
    l.days_since_last_login,

    p.course_id,
    p.completion_percentage,
    p.quiz_average,
    p.assignment_completion_rate,
    p.dropout_status

FROM activity_logs a

JOIN login_history l
    ON a.student_id = l.student_id

JOIN learning_progress p
    ON a.student_id = p.student_id
"""

df = pd.read_sql(query, engine)

print("Dataset loaded:", df.shape)


# --------------------------------
# Feature Engineering
# --------------------------------

df["engagement_score"] = (
    df["sessions_last_30_days"]
    + df["logins_last_30_days"]
    + df["videos_watched"]
    + df["discussion_interactions"]
)

df["learning_score"] = (
    df["completion_percentage"]
    + df["quiz_average"]
    + df["assignment_completion_rate"]
) / 3

df["inactivity_score"] = df["days_since_last_login"]


# --------------------------------
# Features and Target
# --------------------------------

X = df.drop(
    columns=[
        "student_id",
        "course_id",
        "dropout_status"
    ]
)

y = df["dropout_status"]


# --------------------------------
# Train-Test Split
# --------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------
# Train Random Forest
# --------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

print("\n✅ Random Forest trained successfully")


# --------------------------------
# Evaluation
# --------------------------------

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(
    y_test,
    y_pred
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

print("\nAccuracy:")
print(round(accuracy, 4))

print("\nROC-AUC:")
print(round(roc_auc, 4))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# --------------------------------
# Feature Importance
# --------------------------------

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

print("\nTop Feature Importances:")
print(importance_df)


# --------------------------------
# Save Model
# --------------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/dropout_random_forest.pkl"
)

joblib.dump(
    X.columns.tolist(),
    "models/dropout_feature_columns.pkl"
)

print("\n✅ Dropout model saved successfully")


# _______________________________________


import joblib

# Save trained Random Forest model
joblib.dump(
    model,
    "models/dropout_random_forest.pkl"
)

# Save exact feature columns used during training
joblib.dump(
    X.columns.tolist(),
    "models/dropout_feature_columns.pkl"
)

print("\nDropout model saved successfully")
print("Feature columns saved successfully")