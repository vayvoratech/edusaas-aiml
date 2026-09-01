import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PARSER_PATH = (
    PROJECT_ROOT
    / "ast_parser"
    / "parser.js"
)


def parse_javascript(code: str) -> dict:

    result = subprocess.run(
        ["node", str(PARSER_PATH)],
        input=code,
        text=True,
        capture_output=True,
        timeout=10
    )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        raise ValueError(
            f"JavaScript parsing failed: {error_message}"
        )

    return json.loads(result.stdout)