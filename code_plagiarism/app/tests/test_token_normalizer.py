
from app.similarity.token_normalizer import normalize_tokens


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


print("Student A:")
print(normalized_a)

print("\nStudent B:")
print(normalized_b)
