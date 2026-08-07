import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


def evaluate_model(eval_pred):
    """
    Compute evaluation metrics for Hugging Face Trainer.
    """

    logits, labels = eval_pred

    predictions = (logits > 0).astype(int)

    accuracy = accuracy_score(
        labels,
        predictions
    )

    precision = precision_score(
        labels,
        predictions,
        average="micro",
        zero_division=0
    )

    recall = recall_score(
        labels,
        predictions,
        average="micro",
        zero_division=0
    )

    f1 = f1_score(
        labels,
        predictions,
        average="micro",
        zero_division=0
    )

    return {

        "accuracy": accuracy,

        "precision": precision,

        "recall": recall,

        "f1": f1

    }