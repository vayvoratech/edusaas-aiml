ORIGINAL_TOKEN_WEIGHT = 0.15
NORMALIZED_TOKEN_WEIGHT = 0.25
WEIGHTED_AST_WEIGHT = 0.60


def calculate_final_score(
    original_token_score,
    normalized_token_score,
    weighted_ast_score
):
    """
    Calculate the final code similarity score.

    Returns a value between 0 and 100.
    """

    final_score = (
        original_token_score
        * ORIGINAL_TOKEN_WEIGHT
        +
        normalized_token_score
        * NORMALIZED_TOKEN_WEIGHT
        +
        weighted_ast_score
        * WEIGHTED_AST_WEIGHT
    )

    return round(final_score, 2)


def classify_risk(score):
    """
    Classify similarity risk.

    These thresholds are initial project thresholds.
    We will tune them after testing real submissions.
    """

    if score < 29.99:
        return "LOW"

    if score < 59.99:
        return "MEDIUM"

    if score < 79.99:
        return "HIGH"

    return "VERY_HIGH"