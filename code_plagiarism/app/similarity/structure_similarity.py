from difflib import SequenceMatcher


def calculate_structure_similarity(
    fingerprint_a,
    fingerprint_b
):

    if not fingerprint_a or not fingerprint_b:
        return 0.0

    similarity = SequenceMatcher(
        None,
        fingerprint_a,
        fingerprint_b
    ).ratio()

    return round(
        similarity * 100,
        2
    )