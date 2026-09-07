from tree_sitter import Language, Parser
import tree_sitter_java


# ---------------------------------------------------------
# Java language
# ---------------------------------------------------------

JAVA_LANGUAGE = Language(
    tree_sitter_java.language()
)


# ---------------------------------------------------------
# Parser
# ---------------------------------------------------------

parser = Parser(JAVA_LANGUAGE)


# ---------------------------------------------------------
# Parse Java code
# ---------------------------------------------------------

def parse_java(code: str):
    """
    Parse Java source code and return the Tree-sitter AST.
    """

    if not isinstance(code, str):
        raise ValueError("Java code must be a string")

    if not code.strip():
        raise ValueError("Java code cannot be empty")

    try:

        tree = parser.parse(
            code.encode("utf-8")
        )

        return tree

    except Exception as error:

        raise ValueError(
            f"Java parsing failed: {error}"
        )