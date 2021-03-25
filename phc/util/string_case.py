def snake_to_title_case(snake_case: str):
    """Convert snake_case to TitleCase"""
    if len(snake_case) == 0:
        return snake_case

    return "".join([w[0].upper() + w[1:] for w in snake_case.split("_")])
