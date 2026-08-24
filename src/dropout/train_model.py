import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

from src.dropout.feature_engineering import (
    engineer_dropout_features
)


MODEL_PATH = "models/dropout_random_forest.pkl"
FEATURES_PATH = "models/dropout_feature_columns.pkl"


def train_dropout_model(df: pd.DataFrame):

    # ========================================================
    # Feature Engineering
    # ========================================================

    df = engineer_dropout_features(df)


    # ========================================================
    # Features and Target
    # ========================================================

    X = df.drop(
        columns=[
            "student_id",
            "course_id",
            "dropout_status"
        ],
        errors="ignore"
    )

    y = df["dropout_status"]


    # ========================================================
    # Train / Test Split
    # ========================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )


    print(
        f"Training records: {len(X_train)}"
    )

    print(
        f"Testing records: {len(X_test)}"
    )


    # ========================================================
    # Random Forest
    # ========================================================

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )


    print(
        "\nRandom Forest trained successfully"
    )


    # ========================================================
    # Evaluation
    # ========================================================

    y_pred = model.predict(X_test)

    y_probability = (
        model.predict_proba(X_test)[:, 1]
    )


    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    roc_auc = roc_auc_score(
        y_test,
        y_probability
    )


    print(
        "\nAccuracy:",
        round(accuracy, 4)
    )

    print(
        "ROC-AUC:",
        round(roc_auc, 4)
    )


    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )


    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred
        )
    )


    # ========================================================
    # Feature Importance
    # ========================================================

    importance_df = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )

    print(
        "\nFeature Importances:"
    )

    print(
        importance_df
    )


    # ========================================================
    # Save Model
    # ========================================================

    os.makedirs(
        "models",
        exist_ok=True
    )


    joblib.dump(
        model,
        MODEL_PATH
    )


    joblib.dump(
        X.columns.tolist(),
        FEATURES_PATH
    )


    print(
        "\nDropout model saved successfully"
    )

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Features: {FEATURES_PATH}"
    )


    return model


if __name__ == "__main__":

    raise RuntimeError(
        "Training requires a prepared DataFrame. "
        "Load training data separately and call "
        "train_dropout_model(df)."
    )