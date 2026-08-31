"""Module-level caller-aware logging helpers."""

import functools
import logging
import types
from collections.abc import Callable
from typing import Any, cast

from . import magic
from ._debug import ICECREAM, ICON, build_debug_event


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
        name: str | None = frame.f_globals.get("__name__")
    return logging.getLogger(name)


def _wraps[F: Callable[..., Any]](func: F) -> F:
    name: str = func.__name__  # ty:ignore[unresolved-attribute]

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        __tracebackhide__ = True
        depth: int = cast("int", kwargs.get("stacklevel", 1))
        frame, stacklevel = magic.get_frame_with_stacklevel(
            depth=depth, hidden=magic.hidden_from_logging
        )
        logger_name: None = None
        if frame is not None:
            logger_name: str | None = frame.f_globals.get("__name__")
        logger: logging.Logger = logging.getLogger(logger_name)
        kwargs["stacklevel"] = stacklevel
        return getattr(logger, name)(*args, **kwargs)

    return cast("F", wrapper)


debug = _wraps(logging.debug)
info = _wraps(logging.info)
warning = _wraps(logging.warning)
error = _wraps(logging.error)
critical = _wraps(logging.critical)
exception = _wraps(logging.exception)
log = _wraps(logging.log)


def make_log(level: int = logging.INFO) -> Callable[..., None]:
    """Return a caller-aware function shaped like `Logger.log` without `level`."""

    def emit(message: object, *args: object, **kwargs: Any) -> None:
        kwargs.setdefault("stacklevel", 2)
        get_logger(depth=2).log(level, message, *args, **kwargs)

    return emit


def make_print(level: int = logging.INFO) -> Callable[..., None]:
    """Return a print-shaped logging function."""

    def emit(*values: Any, sep: str = " ", end: str = "") -> None:
        message = sep.join(map(str, values)) + end
        get_logger(depth=2).log(level, message, stacklevel=2)

    return emit


def ic(*values: Any, level: int = ICECREAM, prefix: str = ICON) -> Any:
    """Log source-annotated diagnostic values and return them unchanged."""
    frame = magic.get_frame(depth=2)
    name = frame.f_globals.get("__name__") if frame is not None else None
    event = build_debug_event(values, frame, prefix=prefix)
    logging.getLogger(name).log(level, event, stacklevel=2)
    if len(values) == 0:
        return None
    if len(values) == 1:
        return values[0]
    return values
