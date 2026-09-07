import ast


def extract_python_node_types(
    tree
):

    nodes = []

    for node in ast.walk(tree):

        nodes.append(
            type(node).__name__
        )

    return nodes