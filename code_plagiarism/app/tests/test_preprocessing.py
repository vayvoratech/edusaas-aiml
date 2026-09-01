from app.preprocessing.code_cleaner import clean_code
from app.preprocessing.code_normalizer import normalize_code


code1 = """
// Calculate sum

function calculateSum(a, b) {

    let result = a + b;

    return result;
}
"""


code2 = """
/* Add two values */

function addValues(x, y) {

    let total = x + y;

    return total;
}
"""


print("========== CLEAN CODE ==========")

print("CODE 1:")
print(clean_code(code1))

print("\nCODE 2:")
print(clean_code(code2))


print("\n========== NORMALIZED CODE ==========")

print("CODE 1:")
print(normalize_code(code1))

print("\nCODE 2:")
print(normalize_code(code2))