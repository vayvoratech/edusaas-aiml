import re


# ============================================================
# JAVA KEYWORDS
# ============================================================

JAVA_KEYWORDS = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
    "true",
    "false",
    "null"
}


# ============================================================
# COMMON JAVA TYPES
# ============================================================

JAVA_TYPES = {
    "String",
    "Integer",
    "Long",
    "Double",
    "Float",
    "Boolean",
    "Character",
    "Byte",
    "Short",
    "Object",

    "List",
    "ArrayList",
    "LinkedList",

    "Set",
    "HashSet",

    "Map",
    "HashMap",

    "Collection",
    "Collections",

    "Optional",

    "Exception",
    "RuntimeException",

    "File",
    "Scanner"
}


# ============================================================
# JAVA BUILT-INS / IMPORTANT CLASSES
# ============================================================

JAVA_BUILTINS = {
    "System",
    "Math",
    "StringBuilder",
    "StringBuffer",
    "Arrays",

    "Integer",
    "Long",
    "Double",
    "Float",
    "Boolean",

    "Object",

    "List",
    "ArrayList",
    "LinkedList",

    "Set",
    "HashSet",

    "Map",
    "HashMap",

    "Optional",

    "Exception",
    "RuntimeException"
}


# ============================================================
# SPRING BOOT / SPRING WEB
# ============================================================

SPRING_ANNOTATIONS = {
    "RestController",
    "Controller",
    "Service",
    "Repository",
    "Component",
    "Configuration",

    "SpringBootApplication",

    "RequestMapping",
    "GetMapping",
    "PostMapping",
    "PutMapping",
    "DeleteMapping",
    "PatchMapping",

    "RequestBody",
    "RequestParam",
    "PathVariable",
    "RequestHeader",

    "Autowired",
    "Bean",

    "Transactional",

    "Entity",
    "Table",
    "Id",
    "GeneratedValue",
    "Column"
}


# ============================================================
# SPRING / JAVA FRAMEWORK IDENTIFIERS
# ============================================================

FRAMEWORK_IDENTIFIERS = {
    "ResponseEntity",
    "HttpStatus",

    "ApplicationContext",

    "Logger",
    "LoggerFactory",

    "ObjectMapper",

    "JpaRepository",
    "CrudRepository",

    "EntityManager"
}


# ============================================================
# TOKENIZE JAVA
# ============================================================

def tokenize_java(code: str):
    """
    Tokenize Java source code.

    Comments are detected and removed.
    Strings and characters are preserved as tokens.
    """

    if not isinstance(code, str):
        raise ValueError(
            "Java code must be a string"
        )

    if not code.strip():
        return []

    pattern = r"""
        //[^\n]*                  # single-line comments
        |/\*[\s\S]*?\*/           # multi-line comments

        |"(?:\\.|[^"\\])*"        # string literals
        |'(?:\\.|[^'\\])*'        # character literals

        |\b\d+(?:\.\d+)?\b        # numbers

        |[A-Za-z_$][A-Za-z0-9_$]* # identifiers

        |==|!=|<=|>=|&&|\|\|
        |\+\+|--|\+=|-=|\*=|/=|%=
        |->|::|<<|>>|>>>

        |\+|-|\*|/|%|=|<|>
        |!|~|\?|:

        |[{}()\[\];,.]
    """

    tokens = re.findall(
        pattern,
        code,
        re.VERBOSE
    )

    return [
        token
        for token in tokens
        if not token.startswith("//")
        and not token.startswith("/*")
    ]


# ============================================================
# JAVA TOKEN NORMALIZATION
# ============================================================

def normalize_java_tokens(tokens):
    """
    Normalize Java tokens.

    Preserves:
        - Java keywords
        - Java types
        - Java built-ins
        - Spring annotations
        - Framework identifiers
        - operators
        - punctuation

    Normalizes:
        - user-defined identifiers
        - variable names
        - class names
        - method names
        - parameter names
    """

    normalized = []

    identifier_map = {}

    counter = 0

    for token in tokens:

        # ----------------------------------------------------
        # Java keyword
        # ----------------------------------------------------

        if token in JAVA_KEYWORDS:

            normalized.append(token)

            continue


        # ----------------------------------------------------
        # Java type
        # ----------------------------------------------------

        if token in JAVA_TYPES:

            normalized.append(token)

            continue


        # ----------------------------------------------------
        # Java built-in
        # ----------------------------------------------------

        if token in JAVA_BUILTINS:

            normalized.append(token)

            continue


        # ----------------------------------------------------
        # Spring annotation / framework
        # ----------------------------------------------------

        if token in SPRING_ANNOTATIONS:

            normalized.append(token)

            continue


        if token in FRAMEWORK_IDENTIFIERS:

            normalized.append(token)

            continue


        # ----------------------------------------------------
        # Number
        # ----------------------------------------------------

        if re.fullmatch(
            r"\d+(?:\.\d+)?",
            token
        ):

            normalized.append("NUM")

            continue


        # ----------------------------------------------------
        # String
        # ----------------------------------------------------

        if (
            token.startswith('"')
            and token.endswith('"')
        ):

            normalized.append("STRING")

            continue


        # ----------------------------------------------------
        # Character
        # ----------------------------------------------------

        if (
            token.startswith("'")
            and token.endswith("'")
        ):

            normalized.append("CHAR")

            continue


        # ----------------------------------------------------
        # Identifier
        # ----------------------------------------------------

        if re.fullmatch(
            r"[A-Za-z_$][A-Za-z0-9_$]*",
            token
        ):

            if token not in identifier_map:

                identifier_map[token] = (
                    f"VAR{counter}"
                )

                counter += 1

            normalized.append(
                identifier_map[token]
            )

            continue


        # ----------------------------------------------------
        # Operators / punctuation
        # ----------------------------------------------------

        normalized.append(token)


    return normalized


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def normalize_java_code(code: str):

    tokens = tokenize_java(code)

    return normalize_java_tokens(tokens)