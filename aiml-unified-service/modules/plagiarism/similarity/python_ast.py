import ast


def parse_python(code: str):

    try:

        return ast.parse(
            code
        )

    except SyntaxError as error:

        raise ValueError(
            f"Python parsing failed: {error}"
        )