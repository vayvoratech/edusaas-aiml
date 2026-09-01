from app.preprocessing.code_cleaner import (
    clean_code
)


# ============================================================
# TOKENIZATION
# ============================================================

from app.similarity.token_similarity import (
    tokenize_code,
    jaccard_similarity
)


# ============================================================
# JAVASCRIPT NORMALIZER
# ============================================================

from app.similarity.token_normalizer import (
    normalize_tokens
)


# ============================================================
# PYTHON NORMALIZER
# ============================================================

from app.similarity.python_token_normalizer import (
    normalize_python_tokens
)


# ============================================================
# JAVA NORMALIZER
# ============================================================

from app.similarity.java_token_normalizer import (
    tokenize_java,
    normalize_java_tokens
)


# ============================================================
# NORMALIZED TOKEN SIMILARITY
# ============================================================

from app.similarity.normalized_token_similarity import (
    calculate_normalized_token_similarity
)


# ============================================================
# PYTHON AST
# ============================================================

from app.similarity.python_ast import (
    parse_python
)


from app.similarity.python_ast_features import (
    extract_python_node_types
)


from app.similarity.python_weights import (
    PYTHON_NODE_WEIGHTS
)


# ============================================================
# JAVASCRIPT AST
# ============================================================

from app.similarity.javascript_ast import (
    parse_javascript
)


from app.similarity.ast_features import (
    extract_node_types
)


from app.similarity.weighted_ast import (
    NODE_WEIGHTS
)


# ============================================================
# JAVA AST
# ============================================================

from app.similarity.java_ast import (
    parse_java
)


from app.similarity.java_ast_features import (
    extract_java_node_types
)


from app.similarity.java_ast_weights import (
    JAVA_NODE_WEIGHTS
)


# ============================================================
# WEIGHTED AST
# ============================================================

from app.similarity.weighted_ast_similarity import (
    calculate_weighted_ast_similarity
)


# ============================================================
# FINAL SCORE
# ============================================================

from app.similarity.score_calculator import (
    calculate_final_score,
    classify_risk
)


# ============================================================
# LANGUAGE DETECTOR
# ============================================================

from app.similarity.language_detector import (
    detect_language
)


# ============================================================
# LANGUAGE NORMALIZATION
# ============================================================

def normalize_language(
    language: str
) -> str:

    if not language:

        raise ValueError(
            "Programming language is required"
        )


    language = (
        language
        .strip()
        .lower()
    )


    aliases = {

        # ----------------------------------------------------
        # Python
        # ----------------------------------------------------

        "py": "python",
        "python3": "python",


        # ----------------------------------------------------
        # JavaScript
        # ----------------------------------------------------

        "js": "javascript",
        "node": "javascript",
        "nodejs": "javascript",
        "ecmascript": "javascript",


        # ----------------------------------------------------
        # Java
        # ----------------------------------------------------

        "java": "java",
        "spring": "java",
        "springboot": "java",
        "spring boot": "java"
    }


    language = aliases.get(
        language,
        language
    )


    supported_languages = {
        "python",
        "javascript",
        "java"
    }


    if language not in supported_languages:

        raise ValueError(
            f"Unsupported programming language: {language}"
        )


    return language


# ============================================================
# TOKENIZATION
# ============================================================

def get_tokens(
    code: str,
    language: str
):

    language = normalize_language(
        language
    )


    # --------------------------------------------------------
    # Java
    # --------------------------------------------------------

    if language == "java":

        return tokenize_java(
            code
        )


    # --------------------------------------------------------
    # Python / JavaScript
    # --------------------------------------------------------

    return tokenize_code(
        code
    )


# ============================================================
# NORMALIZATION
# ============================================================

def get_normalized_tokens(
    tokens,
    language: str
):

    language = normalize_language(
        language
    )


    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    if language == "python":

        return normalize_python_tokens(
            tokens
        )


    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    if language == "javascript":

        return normalize_tokens(
            tokens
        )


    # --------------------------------------------------------
    # Java
    # --------------------------------------------------------

    if language == "java":

        return normalize_java_tokens(
            tokens
        )


    raise ValueError(
        f"Unsupported programming language: {language}"
    )


# ============================================================
# AST PARSER
# ============================================================

def parse_code(
    code: str,
    language: str
):

    language = normalize_language(
        language
    )


    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    if language == "python":

        return (
            parse_python(code),
            language
        )


    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    if language == "javascript":

        return (
            parse_javascript(code),
            language
        )


    # --------------------------------------------------------
    # Java
    # --------------------------------------------------------

    if language == "java":

        return (
            parse_java(code),
            language
        )


    raise ValueError(
        f"Unsupported programming language: {language}"
    )


# ============================================================
# AST FINGERPRINT
# ============================================================

def extract_fingerprint(
    tree,
    language: str
):

    language = normalize_language(
        language
    )


    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    if language == "python":

        return extract_python_node_types(
            tree
        )


    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    if language == "javascript":

        return extract_node_types(
            tree
        )


    # --------------------------------------------------------
    # Java
    # --------------------------------------------------------

    if language == "java":

        return extract_java_node_types(
            tree
        )


    raise ValueError(
        f"Unsupported programming language: {language}"
    )


# ============================================================
# AST WEIGHTS
# ============================================================

def get_node_weights(
    language: str
):

    language = normalize_language(
        language
    )


    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    if language == "python":

        return PYTHON_NODE_WEIGHTS


    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    if language == "javascript":

        return NODE_WEIGHTS


    # --------------------------------------------------------
    # Java
    # --------------------------------------------------------

    if language == "java":

        return JAVA_NODE_WEIGHTS


    raise ValueError(
        f"Unsupported programming language: {language}"
    )


# ============================================================
# COMPARE CODE
# ============================================================

def compare_code(
    submission_code: str,
    comparison_code: str,
    language: str | None = None
):

    """
    Compare two source-code submissions.

    Supported:

        Python
        JavaScript / Node.js
        Java / Spring Boot

    Analysis:

        Original Token Similarity
        Normalized Token Similarity
        Weighted AST Similarity
        Final Similarity
        Risk Level

    Code is NEVER executed.
    """


    # ========================================================
    # 1. VALIDATE
    # ========================================================

    if not isinstance(
        submission_code,
        str
    ):

        raise ValueError(
            "Submission code must be a string"
        )


    if not isinstance(
        comparison_code,
        str
    ):

        raise ValueError(
            "Comparison code must be a string"
        )


    if not submission_code.strip():

        raise ValueError(
            "Submission code cannot be empty"
        )


    if not comparison_code.strip():

        raise ValueError(
            "Comparison code cannot be empty"
        )


    # ========================================================
    # 2. LANGUAGE
    # ========================================================

    if language is None:

        language = detect_language(
            submission_code
        )


    language = normalize_language(
        language
    )


    # ========================================================
    # 3. TOKEN SOURCE
    # ========================================================
    #
    # We can clean source for token processing.
    #
    # IMPORTANT:
    # We DO NOT use this cleaned source for AST parsing.
    #
    # ========================================================

    clean_submission = clean_code(
        submission_code
    )

    clean_comparison = clean_code(
        comparison_code
    )


    # ========================================================
    # 4. TOKENIZATION
    # ========================================================

    tokens_a = get_tokens(
        clean_submission,
        language
    )


    tokens_b = get_tokens(
        clean_comparison,
        language
    )


    # ========================================================
    # 5. ORIGINAL TOKEN SIMILARITY
    # ========================================================

    original_token_score = (
        jaccard_similarity(
            tokens_a,
            tokens_b
        )
    )


    # ========================================================
    # 6. NORMALIZED TOKENS
    # ========================================================

    normalized_a = (
        get_normalized_tokens(
            tokens_a,
            language
        )
    )


    normalized_b = (
        get_normalized_tokens(
            tokens_b,
            language
        )
    )


    # ========================================================
    # 7. NORMALIZED TOKEN SIMILARITY
    # ========================================================

    normalized_token_score = (
        calculate_normalized_token_similarity(
            normalized_a,
            normalized_b
        )
    )


    # ========================================================
    # 8. AST PARSING
    # ========================================================
    #
    # IMPORTANT:
    # Use ORIGINAL source code here.
    #
    # This prevents Python syntax destruction and preserves
    # JavaScript module syntax and Java formatting.
    #
    # ========================================================

    ast_a, parsed_language_a = (
        parse_code(
            submission_code,
            language
        )
    )


    ast_b, parsed_language_b = (
        parse_code(
            comparison_code,
            language
        )
    )


    # ========================================================
    # 9. LANGUAGE SAFETY CHECK
    # ========================================================

    if (
        parsed_language_a
        !=
        parsed_language_b
    ):

        raise ValueError(
            "Both submissions must use the same "
            "programming language"
        )


    # ========================================================
    # 10. AST FINGERPRINT
    # ========================================================

    fingerprint_a = (
        extract_fingerprint(
            ast_a,
            language
        )
    )


    fingerprint_b = (
        extract_fingerprint(
            ast_b,
            language
        )
    )


    # ========================================================
    # 11. LANGUAGE-SPECIFIC WEIGHTS
    # ========================================================

    node_weights = (
        get_node_weights(
            language
        )
    )


    # ========================================================
    # 12. WEIGHTED AST SIMILARITY
    # ========================================================

    weighted_ast_score = (
        calculate_weighted_ast_similarity(
            fingerprint_a,
            fingerprint_b,
            node_weights
        )
    )


    # ========================================================
    # 13. FINAL SCORE
    # ========================================================

    final_score = (
        calculate_final_score(
            original_token_score,
            normalized_token_score,
            weighted_ast_score
        )
    )


    # ========================================================
    # 14. RISK
    # ========================================================

    risk_level = (
        classify_risk(
            final_score
        )
    )


    # ========================================================
    # 15. RESPONSE
    # ========================================================

    return {

        "language":
            language,

        "original_token_similarity":
            original_token_score,

        "normalized_token_similarity":
            normalized_token_score,

        "weighted_ast_similarity":
            weighted_ast_score,

        "final_similarity":
            final_score,

        "risk_level":
            risk_level
    }