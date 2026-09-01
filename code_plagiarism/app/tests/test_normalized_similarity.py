
from app.similarity.token_normalizer import (
    normalize_tokens
)

from app.similarity.normalized_token_similarity import (
    calculate_normalized_token_similarity
)


tokens_a = [
    "function",
    "calculateSum",
    "(",
    "a",
    ",",
    "b",
    ")",
    "{",
    "let",
    "result",
    "=",
    "a",
    "+",
    "b",
    ";",
    "return",
    "result",
    ";",
    "}"
]


tokens_b = [
    "function",
    "addValues",
    "(",
    "x",
    ",",
    "y",
    ")",
    "{",
    "let",
    "total",
    "=",
    "x",
    "+",
    "y",
    ";",
    "return",
    "total",
    ";",
    "}"
]


normalized_a = normalize_tokens(tokens_a)
normalized_b = normalize_tokens(tokens_b)


score = calculate_normalized_token_similarity(
    normalized_a,
    normalized_b
)


print("Normalized Student A:")
print(normalized_a)

print("\nNormalized Student B:")
print(normalized_b)

print(
    "\nNormalized Token Similarity:",
    score,
    "%"
)
