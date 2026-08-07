import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


def evaluate_model(
    model,
    X_test,
    y_test
):
    """
    Evaluate Fraud Detection Model
    """

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(

        y_test,

        predictions

    )

    precision = precision_score(

        y_test,

        predictions,

        zero_division=0

    )

    recall = recall_score(

        y_test,

        predictions,

        zero_division=0

    )

    f1 = f1_score(

        y_test,

        predictions,

        zero_division=0

    )

    roc_auc = roc_auc_score(

        y_test,

        probabilities

    )

    confusion = confusion_matrix(

        y_test,

        predictions

    )

    report = classification_report(

        y_test,

        predictions,

        zero_division=0

    )

    print("\nFraud Detection Evaluation")

    print("-" * 50)

    print(f"Accuracy      : {accuracy:.4f}")

    print(f"Precision     : {precision:.4f}")

    print(f"Recall        : {recall:.4f}")

    print(f"F1 Score      : {f1:.4f}")

    print(f"ROC AUC Score : {roc_auc:.4f}")

    print("\nConfusion Matrix")

    print(confusion)

    print("\nClassification Report")

    print(report)

    return {

        "accuracy": accuracy,

        "precision": precision,

        "recall": recall,

        "f1_score": f1,

        "roc_auc": roc_auc,

        "confusion_matrix": confusion.tolist()

    }