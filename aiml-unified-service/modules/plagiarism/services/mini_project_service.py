from collections import defaultdict

from modules.plagiarism.preprocessing.mini_project_filter import (
    filter_source_files
)

from modules.plagiarism.services.plagiarism_service import (
    compare_code,
    normalize_language,
    classify_risk
)


# ============================================================
# CONFIGURATION
# ============================================================

SUPPORTED_LANGUAGES = {
    "python",
    "javascript",
    "java"
}

# Ignore weak file matches.
# A file pair must reach this score before it can
# become plagiarism evidence.
MIN_FILE_SIMILARITY = 20.0


# ============================================================
# LANGUAGE NORMALIZATION
# ============================================================

def _safe_normalize_language(language: str) -> str | None:
    """
    Normalize a language using the existing plagiarism
    service language normalization.

    Returns None if the language is unsupported.
    """

    if not language:
        return None

    try:
        normalized = normalize_language(language)
    except ValueError:
        return None

    if normalized not in SUPPORTED_LANGUAGES:
        return None

    return normalized


# ============================================================
# GROUP FILES BY LANGUAGE
# ============================================================

def _group_by_language(files: list[dict]) -> dict[str, list[dict]]:
    """
    Group source files by programming language.

    Different programming languages are never compared.
    """

    grouped = defaultdict(list)

    for file in files:

        language = _safe_normalize_language(
            file.get("language")
        )

        if language is None:
            continue

        grouped[language].append({
            "path": file["path"],
            "language": language,
            "code": file["code"]
        })

    return dict(grouped)


# ============================================================
# COMPARE TWO FILES
# ============================================================

def _compare_files(
    submission_file: dict,
    comparison_file: dict
) -> dict | None:
    """
    Compare two source files.

    Files with different programming languages are rejected.
    """

    language_a = _safe_normalize_language(
        submission_file.get("language")
    )

    language_b = _safe_normalize_language(
        comparison_file.get("language")
    )

    # --------------------------------------------------------
    # Language safety
    # --------------------------------------------------------

    if language_a is None or language_b is None:
        return None

    if language_a != language_b:
        return None

    try:

        result = compare_code(
            submission_file["code"],
            comparison_file["code"],
            language_a
        )

    except Exception:
        # One bad file should not fail the entire project.
        return None

    return {
        "submission_file": submission_file["path"],
        "comparison_file": comparison_file["path"],
        "language": language_a,

        "original_token_similarity": round(
            float(result["original_token_similarity"]),
            2
        ),

        "normalized_token_similarity": round(
            float(result["normalized_token_similarity"]),
            2
        ),

        "weighted_ast_similarity": round(
            float(result["weighted_ast_similarity"]),
            2
        ),

        "similarity": round(
            float(result["final_similarity"]),
            2
        ),

        "risk_level": result["risk_level"]
    }


# ============================================================
# BUILD FILE CANDIDATES
# ============================================================

def _build_candidates(
    submission_files: list[dict],
    comparison_files: list[dict]
) -> list[dict]:
    """
    Compare compatible files and produce candidate matches.
    """

    candidates = []

    submission_by_language = _group_by_language(
        submission_files
    )

    comparison_by_language = _group_by_language(
        comparison_files
    )

    # --------------------------------------------------------
    # Only compare the same programming language.
    # --------------------------------------------------------

    common_languages = (
        set(submission_by_language.keys())
        &
        set(comparison_by_language.keys())
    )

    for language in common_languages:

        source_files = submission_by_language[
            language
        ]

        target_files = comparison_by_language[
            language
        ]

        for source_file in source_files:

            for target_file in target_files:

                result = _compare_files(
                    source_file,
                    target_file
                )

                if result is None:
                    continue

                # ------------------------------------------------
                # Ignore weak evidence.
                # ------------------------------------------------

                if result["similarity"] < MIN_FILE_SIMILARITY:
                    continue

                candidates.append(result)

    return candidates


# ============================================================
# ONE-TO-ONE FILE MATCHING
# ============================================================

def _best_one_to_one_matches(
    submission_files: list[dict],
    comparison_files: list[dict]
) -> list[dict]:
    """
    Select the strongest one-to-one file matches.

    A source file can match only one comparison file.
    A comparison file can match only one source file.

    Matching is based on content similarity, not path/name.
    """

    candidates = _build_candidates(
        submission_files,
        comparison_files
    )

    # --------------------------------------------------------
    # Highest similarity first.
    # --------------------------------------------------------

    candidates.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    used_submission_files = set()
    used_comparison_files = set()

    selected = []

    for candidate in candidates:

        submission_path = candidate[
            "submission_file"
        ]

        comparison_path = candidate[
            "comparison_file"
        ]

        # ----------------------------------------------------
        # One-to-one constraint.
        # ----------------------------------------------------

        if submission_path in used_submission_files:
            continue

        if comparison_path in used_comparison_files:
            continue

        selected.append(candidate)

        used_submission_files.add(
            submission_path
        )

        used_comparison_files.add(
            comparison_path
        )

    return selected


# ============================================================
# PROJECT SIMILARITY
# ============================================================

def _project_similarity(
    matched_files: list[dict]
) -> float:
    """
    Calculate project-level similarity.

    Current implementation uses the average similarity
    of the matched source files.

    This can later be upgraded to a token/size-weighted
    aggregation when stable file-size metrics are exposed
    by the underlying plagiarism engine.
    """

    if not matched_files:
        return 0.0

    total = sum(
        file_match["similarity"]
        for file_match in matched_files
    )

    return round(
        total / len(matched_files),
        2
    )


# ============================================================
# COMPARE ONE PROJECT AGAINST ANOTHER
# ============================================================

def _compare_projects(
    submission_files: list[dict],
    comparison_submission: dict
) -> dict:
    """
    Compare the current project against one comparison project.
    """

    comparison_files = filter_source_files(
        comparison_submission.get("files", [])
    )

    matched_files = _best_one_to_one_matches(
        submission_files,
        comparison_files
    )

    project_similarity = _project_similarity(
        matched_files
    )

    return {
        "comparison_submission_id":
            comparison_submission["submission_id"],

        "similarity":
            project_similarity,

        "risk_level":
            classify_risk(project_similarity),

        "matched_files":
            matched_files
    }


# ============================================================
# MAIN MINI PROJECT COMPARISON
# ============================================================

def compare_mini_project(
    submission: dict,
    comparison_submissions: list[dict]
) -> dict:
    """
    Compare one complete mini-project against
    multiple comparison projects.

    Python performs analysis only.

    It does NOT:
        - access the database
        - clone GitHub repositories
        - resolve commits
        - select assignment groups
        - determine users
    """

    submission_id = submission["submission_id"]

    # --------------------------------------------------------
    # Filter current project files.
    # --------------------------------------------------------

    submission_files = filter_source_files(
        submission.get("files", [])
    )

    # --------------------------------------------------------
    # No comparison projects.
    #
    # This is a valid completed analysis with zero
    # comparisons.
    # --------------------------------------------------------

    if not comparison_submissions:

        return {
            "submission_id": submission_id,
            "status": "COMPLETED",
            "comparison_count": 0,
            "overall_similarity": 0.0,
            "risk_level": classify_risk(0.0),
            "matches": []
        }

    matches = []

    # --------------------------------------------------------
    # Compare against every comparison project.
    # --------------------------------------------------------

    for comparison_submission in comparison_submissions:

        comparison_id = (
            comparison_submission.get(
                "submission_id"
            )
        )

        if not comparison_id:
            continue

        try:

            project_result = _compare_projects(
                submission_files,
                comparison_submission
            )

        except Exception:
            # A single comparison project should not
            # fail the complete analysis.
            continue

        matches.append(
            project_result
        )

    # --------------------------------------------------------
    # Overall project similarity.
    #
    # The strongest comparison is used as the overall
    # plagiarism indicator.
    # --------------------------------------------------------

    overall_similarity = 0.0

    if matches:
        overall_similarity = max(
            match["similarity"]
            for match in matches
        )

    return {
        "submission_id": submission_id,

        "status": "COMPLETED",

        "comparison_count":
            len(comparison_submissions),

        "overall_similarity":
            round(overall_similarity, 2),

        "risk_level":
            classify_risk(overall_similarity),

        "matches":
            matches
    }