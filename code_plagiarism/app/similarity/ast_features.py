IGNORED_FIELDS = {
    "start",
    "end",
    "loc",
    "range",
    "raw"
}


def extract_node_types(node, result=None):

    if result is None:
        result = []

    if isinstance(node, dict):

        node_type = node.get("type")

        if node_type:
            result.append(node_type)

        for key, value in node.items():

            if key in IGNORED_FIELDS:
                continue

            extract_node_types(value, result)

    elif isinstance(node, list):

        for item in node:
            extract_node_types(item, result)

    return result