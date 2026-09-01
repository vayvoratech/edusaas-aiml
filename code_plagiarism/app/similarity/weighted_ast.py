
from collections import Counter


# Higher weight = more important for detecting
# structural similarity.

NODE_WEIGHTS = {

    # Program structure
    "Program": 0.5,
    "BlockStatement": 0.5,

    # Functions
    "FunctionDeclaration": 3.0,
    "FunctionExpression": 3.0,
    "ArrowFunctionExpression": 3.0,

    # Control flow
    "IfStatement": 4.0,
    "ForStatement": 4.0,
    "ForInStatement": 4.0,
    "ForOfStatement": 4.0,
    "WhileStatement": 4.0,
    "DoWhileStatement": 4.0,
    "SwitchStatement": 4.0,

    # Important operations
    "CallExpression": 3.0,
    "NewExpression": 3.0,
    "BinaryExpression": 3.0,
    "LogicalExpression": 3.0,
    "AssignmentExpression": 3.0,
    "UpdateExpression": 2.5,
    "UnaryExpression": 2.5,

    # Variables
    "VariableDeclaration": 2.5,
    "VariableDeclarator": 2.0,

    # Return / throw
    "ReturnStatement": 3.0,
    "ThrowStatement": 3.0,

    # Objects / arrays
    "ObjectExpression": 2.0,
    "ArrayExpression": 2.0,
    "Property": 1.5,

    # Classes
    "ClassDeclaration": 3.0,
    "MethodDefinition": 3.0,

    # Identifiers and literals
    "Identifier": 0.5,
    "Literal": 0.5,
}


def weighted_ast_features(
    fingerprint
):
    """
    Convert an AST fingerprint into
    weighted node counts.
    """

    counts = Counter(fingerprint)

    weighted = {}

    for node_type, count in counts.items():

        weight = NODE_WEIGHTS.get(
            node_type,
            1.0
        )

        weighted[node_type] = (
            count * weight
        )

    return weighted
