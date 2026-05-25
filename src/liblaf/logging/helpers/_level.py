import logging

_DEFAULT_LEVELS: list[tuple[int, str]] = [
    (25, "ICECREAM"),
    (5, "TRACE"),
]


def add_levels() -> None:
    for level, name in _DEFAULT_LEVELS:
        logging.addLevelName(level, name)
