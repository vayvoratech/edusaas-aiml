import keyword


PYTHON_KEYWORDS = set(
    keyword.kwlist
)


def normalize_python_tokens(
    tokens
):

    normalized = []

    variable_map = {}

    variable_counter = 0


    for token in tokens:

        if token in PYTHON_KEYWORDS:

            normalized.append(
                token
            )

            continue


        if token.isidentifier():

            if token not in variable_map:

                variable_map[token] = (
                    f"VAR{variable_counter}"
                )

                variable_counter += 1

            normalized.append(
                variable_map[token]
            )

        else:

            normalized.append(
                token
            )


    return normalized