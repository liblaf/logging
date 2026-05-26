"""Utilities for cleaning up duplicate stream handlers."""

import logging
import sys


def remove_non_root_stream_handlers() -> None:
    """Remove duplicate stdout/stderr handlers from named loggers.

    Root handlers are left alone. Non-stdio stream handlers, such as in-memory
    streams or file-backed handlers, are also preserved.
    """
    # loggerDict is not documented, but it's widely used.
    for logger in logging.root.manager.loggerDict.values():
        if not isinstance(logger, logging.Logger):
            continue
        if logger.name == "root":
            continue
        for handler in logger.handlers[:]:  # slice to freeze the list during iteration
            if isinstance(handler, logging.StreamHandler) and (
                handler.stream is sys.stdout or handler.stream is sys.stderr
            ):
                logger.removeHandler(handler)
