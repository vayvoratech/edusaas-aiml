from app.similarity.javascript_ast import parse_javascript
from app.similarity.ast_features import extract_node_types
from app.similarity.structure_similarity import (
    calculate_structure_similarity
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


ast_a = parse_javascript(code_a)
ast_b = parse_javascript(code_b)


fingerprint_a = extract_node_types(ast_a)
fingerprint_b = extract_node_types(ast_b)


score = calculate_structure_similarity(
    fingerprint_a,
    fingerprint_b
)


print("Student A:")
print(fingerprint_a)

print("\nStudent B:")
print(fingerprint_b)

print("\nStructural Similarity:", score, "%")