import functools
import logging
import types
from collections.abc import Callable
from typing import Any, cast

from . import magic


def get_logger(*, depth: int = 1) -> logging.Logger:
    """Return the logger for the first visible caller frame.

    Args:
        depth: Number of visible frames to skip before selecting a logger.

    Returns:
        The logger named by the caller frame's `__name__`, or the root logger
        when no frame name is available.
    """
    __tracebackhide__ = True
    frame: types.FrameType | None = magic.get_frame(
        depth=depth, hidden=magic.hidden_from_logging
    )
    name: None = None
    if frame is not None:
        name: str | None = frame.f_globals.get("__name__", None)
    return logging.getLogger(name)


def _wraps[F: Callable[..., Any]](func: F) -> F:
    name: str = func.__name__  # ty:ignore[unresolved-attribute]

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        __tracebackhide__ = True
        logger: logging.Logger = get_logger()
        return getattr(logger, name)(*args, **kwargs)

    return cast("F", wrapper)


debug = _wraps(logging.debug)
info = _wraps(logging.info)
warning = _wraps(logging.warning)
error = _wraps(logging.error)
critical = _wraps(logging.critical)
exception = _wraps(logging.exception)
log = _wraps(logging.log)
