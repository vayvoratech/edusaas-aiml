import re

from app.preprocessing.code_cleaner import clean_code


KEYWORDS = {
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
    "function",
    "if",
    "import",
    "in",
    "instanceof",
    "let",
    "new",
    "return",
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
    "async",
    "await"
}


def normalize_identifiers(code: str) -> str:
    """
    Replace user-defined identifiers with generic names.

    Example:

    calculateSum(a, b)
    result

    becomes:

    FUNC(VAR, VAR)
    VAR
    """

    identifiers = {}
    variable_count = 0
    function_count = 0

    def replace_identifier(match):
        nonlocal variable_count, function_count

        identifier = match.group(0)

        # Preserve JavaScript keywords
        if identifier in KEYWORDS:
            return identifier

        # Preserve common built-in objects/functions
        builtins = {
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
            "Map"
        }

        if identifier in builtins:
            return identifier

        if identifier not in identifiers:

            # Detect whether identifier is followed by "("
            # to approximately identify a function call/name.
            identifiers[identifier] = f"VAR{variable_count}"
            variable_count += 1

        return identifiers[identifier]

    code = re.sub(
        r"\b[A-Za-z_$][A-Za-z0-9_$]*\b",
        replace_identifier,
        code
    )

    return code


def normalize_code(code: str) -> str:
    """
    Complete normalization pipeline.
    """

    code = clean_code(code)
    code = normalize_identifiers(code)

    return code