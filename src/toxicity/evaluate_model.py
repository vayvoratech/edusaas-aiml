import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


def evaluate_model(eval_pred):
    """
    Compute evaluation metrics for a multi-label
    toxicity classification model.

    The model outputs logits for six independent labels:

        toxic
        severe_toxic
        obscene
        threat
        insult
        identity_hate

    Logits are converted to probabilities using sigmoid,
    then thresholded at 0.5.
    """

    logits, labels = eval_pred

    # ---------------------------------------------------------
    # Convert logits to probabilities
    # ---------------------------------------------------------

    probabilities = 1.0 / (
        1.0 + np.exp(-logits)
    )

    # ---------------------------------------------------------
    # Convert probabilities to binary predictions
    # ---------------------------------------------------------

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    labels = np.asarray(
        labels
    ).astype(int)

    # ---------------------------------------------------------
    # Exact-match accuracy
    # ---------------------------------------------------------
    #
    # A sample is correct only when ALL six labels
    # are predicted correctly.
    #
    # Kept for reference, but should not be the
    # primary metric for this problem.
    # ---------------------------------------------------------

    exact_match_accuracy = accuracy_score(
        labels,
        predictions,
    )

    # ---------------------------------------------------------
    # Micro metrics
    # ---------------------------------------------------------

    precision_micro = precision_score(
        labels,
        predictions,
        average="micro",
        zero_division=0,
    )

    recall_micro = recall_score(
        labels,
        predictions,
        average="micro",
        zero_division=0,
    )

    f1_micro = f1_score(
        labels,
        predictions,
        average="micro",
        zero_division=0,
    )

    # ---------------------------------------------------------
    # Macro metrics
    # ---------------------------------------------------------

    precision_macro = precision_score(
        labels,
        predictions,
        average="macro",
        zero_division=0,
    )

    recall_macro = recall_score(
        labels,
        predictions,
        average="macro",
        zero_division=0,
    )

    f1_macro = f1_score(
        labels,
        predictions,
        average="macro",
        zero_division=0,
    )

    # ---------------------------------------------------------
    # Return metrics
    # ---------------------------------------------------------

    return {
        "exact_match_accuracy": exact_match_accuracy,

        "precision_micro": precision_micro,
        "recall_micro": recall_micro,
        "f1_micro": f1_micro,

        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
    }