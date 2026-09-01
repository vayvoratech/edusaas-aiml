from app.services.plagiarism_service import (
    compare_code
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


result = compare_code(
    code_a,
    code_b
)


print("====================================")
print("CODE PLAGIARISM TEST")
print("====================================")

for key, value in result.items():

    print(
        f"{key}: {value}"
    )