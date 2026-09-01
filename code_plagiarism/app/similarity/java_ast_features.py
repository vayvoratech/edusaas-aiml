def extract_java_node_types(tree):
    """
    Extract Tree-sitter Java AST node types.
    """

    node_types = []

    def walk(node):

        node_types.append(
            node.type
        )

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return node_types