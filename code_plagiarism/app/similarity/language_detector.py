import re


# ============================================================
# LANGUAGE DETECTOR
# ============================================================

def detect_language(
    code: str
) -> str:

    if not isinstance(code, str):

        raise ValueError(
            "Code must be a string"
        )

    if not code.strip():

        raise ValueError(
            "Code cannot be empty"
        )

    # --------------------------------------------------------
    # Java indicators
    # --------------------------------------------------------

    java_patterns = [

        r"\bpackage\s+[a-zA-Z_][\w.]*\s*;",

        r"\bimport\s+java\.",

        r"\bimport\s+javax\.",

        r"\bimport\s+jakarta\.",

        r"\bimport\s+org\.springframework\.",

        r"\bpublic\s+class\s+\w+",

        r"\bprivate\s+class\s+\w+",

        r"\bprotected\s+class\s+\w+",

        r"\bpublic\s+static\s+void\s+main\s*\(",

        r"@RestController\b",

        r"@Controller\b",

        r"@Service\b",

        r"@Repository\b",

        r"@Component\b",

        r"@SpringBootApplication\b",

        r"@RequestMapping\b",

        r"@GetMapping\b",

        r"@PostMapping\b",

        r"@PutMapping\b",

        r"@DeleteMapping\b",

        r"\bSystem\.out\.println\s*\(",

        r"\bString\s+\w+\s*=",

        r"\bInteger\s+\w+\s*=",

        r"\bboolean\s+\w+\s*=",

        r"\bpublic\s+\w+\s+\w+\s*\("

    ]


    # --------------------------------------------------------
    # JavaScript indicators
    # --------------------------------------------------------

    javascript_patterns = [

        r"\bconst\s+\w+\s*=",

        r"\blet\s+\w+\s*=",

        r"\bvar\s+\w+\s*=",

        r"\brequire\s*\(",

        r"\bmodule\.exports\b",

        r"\bexports\.",

        r"=>",

        r"\bfunction\s+\w+\s*\(",

        r"\bconsole\.log\s*\(",

        r"\basync\s+function\b",

        r"\bawait\s+",

        r"\bexpress\s*\(",

        r"\bapp\.(get|post|put|delete)\s*\("

    ]


    # --------------------------------------------------------
    # Python indicators
    # --------------------------------------------------------

    python_patterns = [

        r"^\s*def\s+\w+\s*\(",

        r"^\s*class\s+\w+.*:",

        r"^\s*from\s+\w+",

        r"^\s*import\s+\w+",

        r"\bimport\s+pandas\b",

        r"\bimport\s+numpy\b",

        r"\bfrom\s+sklearn\b",

        r"\bfrom\s+xgboost\b",

        r"\bif\s+__name__\s*==\s*[\"']__main__[\"']",

        r"^\s*elif\s+",

        r"^\s*except\s+",

        r"\bprint\s*\("

    ]


    # --------------------------------------------------------
    # Count matches
    # --------------------------------------------------------

    java_score = sum(
        bool(
            re.search(
                pattern,
                code,
                re.MULTILINE
            )
        )
        for pattern in java_patterns
    )

    javascript_score = sum(
        bool(
            re.search(
                pattern,
                code,
                re.MULTILINE
            )
        )
        for pattern in javascript_patterns
    )

    python_score = sum(
        bool(
            re.search(
                pattern,
                code,
                re.MULTILINE
            )
        )
        for pattern in python_patterns
    )


    scores = {

        "java":
            java_score,

        "javascript":
            javascript_score,

        "python":
            python_score
    }


    detected_language = max(
        scores,
        key=scores.get
    )


    # --------------------------------------------------------
    # Confidence / ambiguity check
    # --------------------------------------------------------

    sorted_scores = sorted(
        scores.values(),
        reverse=True
    )


    if sorted_scores[0] == 0:

        raise ValueError(
            "Unable to detect programming language"
        )


    if (
        len(sorted_scores) > 1
        and sorted_scores[0] == sorted_scores[1]
    ):

        raise ValueError(
            "Programming language could not be determined confidently"
        )


    return detected_language