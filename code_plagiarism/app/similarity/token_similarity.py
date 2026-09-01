from collections import Counter


def tokenize_code(code: str):
    """
    Basic JavaScript tokenization.
    """

    tokens = []
    current = ""

    for char in code:

        if char.isalnum() or char in "_$":

            current += char

        else:

            if current:
                tokens.append(current)
                current = ""

            if not char.isspace():
                tokens.append(char)

    if current:
        tokens.append(current)

    return tokens
def jaccard_similarity(tokens_a, tokens_b):

    set_a = set(tokens_a)
    set_b = set(tokens_b)

    if not set_a and not set_b:
        return 100.0

    if not set_a or not set_b:
        return 0.0

    intersection = len(
        set_a.intersection(set_b)
    )

    union = len(
        set_a.union(set_b)
    )

    return round(
        (intersection / union) * 100,
        2
    )