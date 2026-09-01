
"""
Normalize JavaScript tokens for code plagiarism detection.

The goal is to reduce superficial differences such as:
    calculateSum -> addValues
    result       -> total
    a             -> x

while preserving important programming constructs such as:
    function
    return
    if
    for
    +
    -
    =
    ===
    etc.
"""

# JavaScript reserved keywords.
# These must never be converted into generic identifiers.

JAVASCRIPT_KEYWORDS = {
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "debugger",
    "default",
    "delete",
    "do",
    "else",
    "export",
    "extends",
    "finally",
    "for",
    "from",
    "function",
    "if",
    "import",
    "in",
    "instanceof",
    "let",
    "new",
    "return",
    "super",
    "switch",
    "this",
    "throw",
    "try",
    "typeof",
    "var",
    "void",
    "while",
    "with",
    "yield",

    # Modern JavaScript
    "async",
    "await",
    "of",
    "static",
    "get",
    "set",

    # Literals
    "true",
    "false",
    "null",
    "undefined"
}


# Common JavaScript/Node.js built-ins.
# We preserve these because they carry useful semantic information.

JAVASCRIPT_BUILTINS = {
    "console",
    "Math",
    "JSON",
    "Array",
    "Object",
    "String",
    "Number",
    "Boolean",
    "Date",
    "Promise",
    "Set",
    "Map",
    "RegExp",
    "Error",
    "Buffer",
    "process",
    "require",
    "module",
    "exports",
    "setTimeout",
    "setInterval",
    "clearTimeout",
    "clearInterval"
}


def is_identifier(token: str) -> bool:
    """
    Determine whether a token looks like a JavaScript identifier.

    Examples:
        calculateSum -> True
        result       -> True
        _value       -> True
        $element     -> True
        function     -> False
        +            -> False
    """

    if not token:
        return False

    first = token[0]

    if not (
        first.isalpha()
        or first in {"_", "$"}
    ):
        return False

    for char in token[1:]:
        if not (
            char.isalnum()
            or char in {"_", "$"}
        ):
            return False

    return True


def normalize_identifiers(tokens):
    """
    Replace user-defined identifiers with generic identifiers.

    Example:

        function calculateSum(a, b) {
            let result = a + b;
            return result;
        }

    becomes approximately:

        function FUNC0(VAR0, VAR1) {
            let VAR2 = VAR0 + VAR1;
            return VAR2;
        }

    The same identifiers receive the same normalized name.
    """

    normalized_tokens = []

    identifier_map = {}

    variable_counter = 0

    for token in tokens:

        # Preserve JavaScript keywords.
        if token in JAVASCRIPT_KEYWORDS:
            normalized_tokens.append(token)
            continue

        # Preserve JavaScript/Node.js built-ins.
        if token in JAVASCRIPT_BUILTINS:
            normalized_tokens.append(token)
            continue

        # Normalize identifiers.
        if is_identifier(token):

            if token not in identifier_map:

                identifier_map[token] = (
                    f"VAR{variable_counter}"
                )

                variable_counter += 1

            normalized_tokens.append(
                identifier_map[token]
            )

        else:
            # Operators, punctuation, numbers, strings, etc.
            normalized_tokens.append(token)

    return normalized_tokens


def normalize_tokens(tokens):
    """
    Main token normalization function.
    """

    if not tokens:
        return []

    return normalize_identifiers(tokens)
