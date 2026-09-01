import re


def clean_code(code: str) -> str:

    if not code:
        return ""

    # Remove single-line comments
    code = re.sub(
        r"#.*?$",
        "",
        code,
        flags=re.MULTILINE
    )

    # Remove JavaScript single-line comments
    code = re.sub(
        r"//.*?$",
        "",
        code,
        flags=re.MULTILINE
    )

    # Remove block comments
    code = re.sub(
        r"/\*.*?\*/",
        "",
        code,
        flags=re.DOTALL
    )

    # Remove trailing spaces from each line
    lines = [
        line.rstrip()
        for line in code.splitlines()
    ]

    # Remove empty lines
    lines = [
        line
        for line in lines
        if line.strip()
    ]

    # IMPORTANT:
    # Preserve newlines because Python uses
    # indentation and line structure.

    return "\n".join(lines).strip()