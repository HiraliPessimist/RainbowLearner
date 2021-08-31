MAX_CHARACTERS = 5_000


def is_limited(text: str) -> bool:
    """
    When the text over the MAX_CHARACTERS, it return True.

    Args:
        text(str): Original text

    Returns:
        (bool)
    """
    if len(text) > MAX_CHARACTERS:
        return True
    return False


def limit_characters(text: str) -> str:
    """
    Limit to the number of characters.

    Args:
        text(str): Original text

    Returns:
        (str) The text is limited to the number of characters.
    """
    return text[:MAX_CHARACTERS]
