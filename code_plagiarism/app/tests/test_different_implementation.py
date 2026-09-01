
from app.similarity.javascript_ast import parse_javascript
from app.similarity.ast_features import extract_node_types
from app.similarity.weighted_ast import NODE_WEIGHTS
from app.similarity.structure_similarity import (
    calculate_structure_similarity
)

from app.similarity.token_normalizer import (
    normalize_tokens
)

from app.similarity.normalized_token_similarity import (
    calculate_normalized_token_similarity
)

from app.similarity.token_similarity import (
    tokenize_code
)
from app.similarity.weighted_ast_similarity import (
    calculate_weighted_ast_similarity
)



code_a = """
function calculateSum(a, b) {
    let result = a + b;
    return result;
}
"""


code_b = """
function calculateSum(a, b) {
    let sum = 0;

    sum = a;
    sum += b;

    return sum;
}
"""


# --------------------------------------------------
# AST SIMILARITY
# --------------------------------------------------

ast_a = parse_javascript(code_a)
ast_b = parse_javascript(code_b)

fingerprint_a = extract_node_types(ast_a)
fingerprint_b = extract_node_types(ast_b)

ast_score = calculate_structure_similarity(
    fingerprint_a,
    fingerprint_b
)


# --------------------------------------------------
# ORIGINAL TOKEN SIMILARITY
# --------------------------------------------------

tokens_a = tokenize_code(code_a)
tokens_b = tokenize_code(code_b)

original_token_score = (
    __import__(
        "app.similarity.token_similarity",
        fromlist=["jaccard_similarity"]
    )
    .jaccard_similarity(
        tokens_a,
        tokens_b
    )
)


# --------------------------------------------------
# NORMALIZED TOKEN SIMILARITY
# --------------------------------------------------

normalized_a = normalize_tokens(tokens_a)
normalized_b = normalize_tokens(tokens_b)

normalized_token_score = (
    calculate_normalized_token_similarity(
        normalized_a,
        normalized_b
    )
)

weighted_ast_score = (
    calculate_weighted_ast_similarity(
        fingerprint_a,
        fingerprint_b,
        NODE_WEIGHTS
    )
)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("====================================")
print("DIFFERENT IMPLEMENTATION TEST")
print("====================================")

print("\nStudent A AST:")
print(fingerprint_a)

print("\nStudent B AST:")
print(fingerprint_b)

print(
    "\nAST Similarity:",
    ast_score,
    "%"
)

print(
    "\nOriginal Token Similarity:",
    original_token_score,
    "%"
)

print(
    "\nNormalized Token Similarity:",
    normalized_token_score,
    "%"
)
print(
    "\nWeighted AST Similarity:",
    weighted_ast_score,
    "%"
)