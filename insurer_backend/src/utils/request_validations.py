def check_secondary_filters(filters):
    if not isinstance(filters, dict):
        raise ValueError("Secondary filters is not a dictionary")
    if not all(
        isinstance(k, str) and isinstance(v, float)
        for k, v in filters.items()
    ):
        raise ValueError("Secondary filters must be a dictionary of <string>:<float>")