from collections import Counter


def calculate_weighted_ast_similarity(
    fingerprint_a,
    fingerprint_b,
    node_weights
):
    if not fingerprint_a or not fingerprint_b:
        return 0.0

    counts_a = Counter(fingerprint_a)
    counts_b = Counter(fingerprint_b)

    all_nodes = set(counts_a) | set(counts_b)

    common_weight = 0.0
    total_weight = 0.0

    for node_type in all_nodes:

        weight = node_weights.get(
            node_type,
            1.0
        )

        count_a = counts_a.get(node_type, 0)
        count_b = counts_b.get(node_type, 0)

        common = min(count_a, count_b)
        maximum = max(count_a, count_b)

        common_weight += common * weight
        total_weight += maximum * weight

    if total_weight == 0:
        return 0.0

    return round(
        (common_weight / total_weight) * 100,
        2
    )