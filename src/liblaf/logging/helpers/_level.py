import logging

_DEFAULT_LEVELS: list[tuple[int, str]] = [
    (25, "ICECREAM"),
    (5, "TRACE"),
]


def add_levels() -> None:
    """Register the package's custom logging level names.

    The numeric levels are intentionally lightweight additions to the standard
    logging registry: `TRACE` is below `DEBUG`, and `ICECREAM` is available for
    diagnostic values emitted by projects that integrate icecream-style output.

    Examples:
        >>> add_levels()
        >>> logging.getLevelName(5)
        'TRACE'
        >>> logging.getLevelName(25)
        'ICECREAM'
    """
    for level, name in _DEFAULT_LEVELS:
        logging.addLevelName(level, name)
