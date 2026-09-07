from collections import Counter
from difflib import SequenceMatcher


# ============================================================
# WEIGHTS
# ============================================================

FREQUENCY_WEIGHT = 0.60
SEQUENCE_WEIGHT = 0.40


# ============================================================
# NORMALIZED TOKEN SIMILARITY
# ============================================================

def calculate_normalized_token_similarity(
    tokens_a,
    tokens_b
):
    """
    Calculate similarity between normalized token sequences.

    Uses:

        1. Token frequency similarity
        2. Token sequence similarity

    Final score:

        60% frequency
        40% sequence

    Returns a score between 0 and 100.
    """

    if not tokens_a or not tokens_b:
        return 0.0


    # ========================================================
    # FREQUENCY SIMILARITY
    # ========================================================

    counter_a = Counter(tokens_a)
    counter_b = Counter(tokens_b)

    all_tokens = (
        set(counter_a)
        |
        set(counter_b)
    )

    if not all_tokens:
        return 0.0


    intersection = sum(
        min(
            counter_a[token],
            counter_b[token]
        )
        for token in all_tokens
    )


    total = (
        sum(counter_a.values())
        +
        sum(counter_b.values())
    )


    if total == 0:
        return 0.0


    frequency_similarity = (
        (2 * intersection) / total
    ) * 100


    # ========================================================
    # SEQUENCE SIMILARITY
    # ========================================================

    sequence_similarity = (
        SequenceMatcher(
            None,
            tokens_a,
            tokens_b
        ).ratio()
        * 100
    )


    # ========================================================
    # FINAL NORMALIZED TOKEN SCORE
    # ========================================================

    final_score = (
        frequency_similarity
        * FREQUENCY_WEIGHT
        +
        sequence_similarity
        * SEQUENCE_WEIGHT
    )


    return round(
        final_score,
        2
    )