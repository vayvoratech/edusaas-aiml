from app.similarity.token_similarity import (
    tokenize_code,
    jaccard_similarity
)


code_a = """
function calculateSum(a, b) {
    let result = a + b;
    return result;
}
"""


code_b = """
function addValues(x, y) {
    let total = x + y;
    return total;
}
"""


tokens_a = tokenize_code(code_a)
tokens_b = tokenize_code(code_b)


print("Student A tokens:")
print(tokens_a)

print("\nStudent B tokens:")
print(tokens_b)


score = jaccard_similarity(
    tokens_a,
    tokens_b
)


print("\nToken Similarity:", score, "%")