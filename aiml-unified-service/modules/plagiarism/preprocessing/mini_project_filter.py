from pathlib import PurePosixPath


# ============================================================
# IGNORED DIRECTORIES
# ============================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",

    "node_modules",
    "vendor",

    "build",
    "dist",
    "coverage",

    ".cache",
    "cache",
    ".next",
    ".nuxt",

    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",

    "target",
    "out",
    "bin",
    "obj",

    ".gradle",
}


# ============================================================
# IGNORED FILES
# ============================================================

IGNORED_FILES = {
    # JavaScript / Node
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",

    # Python
    "Pipfile.lock",
    "poetry.lock",

    # PHP
    "composer.lock",

    # Java / Gradle
    "gradle.lockfile",

    # Common generated files
    ".DS_Store",
    "Thumbs.db",
}


# ============================================================
# IGNORED FILE EXTENSIONS
# ============================================================

IGNORED_EXTENSIONS = {
    # Minified / source maps
    ".min.js",
    ".min.css",
    ".map",

    # Compiled / bytecode
    ".class",
    ".pyc",
    ".pyo",

    # Binary / media
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",

    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",

    ".mp3",
    ".mp4",
    ".wav",

    ".zip",
    ".tar",
    ".gz",
    ".7z",

    # Build artifacts
    ".o",
    ".obj",
}


# ============================================================
# SUPPORTED SOURCE EXTENSIONS
# ============================================================

SUPPORTED_SOURCE_EXTENSIONS = {
    # Python
    ".py": "python",

    # JavaScript
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",

    # Java
    ".java": "java",
}


# ============================================================
# CHECK DIRECTORY
# ============================================================

def is_ignored_directory(path: str) -> bool:
    """
    Check whether any directory in the file path
    belongs to the ignored directory list.
    """

    normalized_path = path.replace("\\", "/")

    parts = PurePosixPath(normalized_path).parts

    return any(
        part in IGNORED_DIRECTORIES
        for part in parts
    )


# ============================================================
# CHECK FILE
# ============================================================

def should_ignore_file(path: str) -> bool:
    """
    Determine whether a repository file should be excluded
    from mini-project plagiarism analysis.
    """

    normalized_path = path.replace("\\", "/")

    file_name = PurePosixPath(normalized_path).name

    # --------------------------------------------------------
    # Ignored directories
    # --------------------------------------------------------

    if is_ignored_directory(normalized_path):
        return True

    # --------------------------------------------------------
    # Ignored file names
    # --------------------------------------------------------

    if file_name in IGNORED_FILES:
        return True

    # --------------------------------------------------------
    # Ignored extensions
    # --------------------------------------------------------

    lower_name = file_name.lower()

    for extension in IGNORED_EXTENSIONS:
        if lower_name.endswith(extension):
            return True

    return False


# ============================================================
# LANGUAGE FROM EXTENSION
# ============================================================

def get_language_from_path(path: str) -> str | None:
    """
    Determine the supported programming language from
    the source file extension.

    Returns:
        python
        javascript
        java
        None
    """

    suffix = PurePosixPath(
        path.replace("\\", "/")
    ).suffix.lower()

    return SUPPORTED_SOURCE_EXTENSIONS.get(
        suffix
    )


# ============================================================
# FILTER SOURCE FILES
# ============================================================

def filter_source_files(files: list[dict]) -> list[dict]:
    """
    Filter repository files so that only supported,
    non-generated source files are sent for plagiarism analysis.

    The language supplied by Node is preserved when valid.
    """

    filtered_files = []

    for file in files:

        if not isinstance(file, dict):
            continue

        path = file.get("path")
        code = file.get("code")
        language = file.get("language")

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        if not path or not isinstance(path, str):
            continue

        if not isinstance(code, str):
            continue

        if not code.strip():
            continue

        # ----------------------------------------------------
        # Binary detection
        # ----------------------------------------------------

        if "\x00" in code:
            continue

        # ----------------------------------------------------
        # Ignore generated/vendor files
        # ----------------------------------------------------

        if should_ignore_file(path):
            continue

        # ----------------------------------------------------
        # Language
        # ----------------------------------------------------

        if language:
            language = language.strip().lower()

        else:
            language = get_language_from_path(path)

        # ----------------------------------------------------
        # Only supported languages
        # ----------------------------------------------------

        if language not in {
            "python",
            "javascript",
            "java"
        }:
            continue

        filtered_files.append({
            "path": path.replace("\\", "/"),
            "language": language,
            "code": code
        })

    return filtered_files