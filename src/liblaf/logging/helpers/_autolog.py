"""Caller-aware logger proxy."""

import functools
import logging
import types
from typing import Any, cast

from liblaf.logging import magic

_PROXY_METHODS: set[str] = {
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "log",
    "exception",
}


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


class AutoLogger:
    """Proxy common logging methods to the caller's logger.

    `AutoLogger` is useful for small helper functions that should log as their
    caller rather than as the helper module. Proxy methods preserve caller
    attribution by adjusting `stacklevel` after hidden-frame skipping.
    """

    def __getattr__(self, name: str) -> Any:
        """Resolve logging attributes from the caller's logger."""
        __tracebackhide__ = True
        if name in _PROXY_METHODS:
            return functools.partial(self._delegate, name)
        logger: logging.Logger = get_logger()
        return getattr(logger, name)

    def _delegate(self, method: str, *args, **kwargs) -> Any:
        """Call a logging method on the visible caller's logger."""
        __tracebackhide__ = True
        depth: int = kwargs.get("stacklevel", 1)
        frame, stacklevel = magic.get_frame_with_stacklevel(
            depth=depth, hidden=magic.hidden_from_logging
        )
        name: None = None
        if frame is not None:
            name: str | None = frame.f_globals.get("__name__", None)
        logger: logging.Logger = logging.getLogger(name)
        kwargs["stacklevel"] = stacklevel
        return getattr(logger, method)(*args, **kwargs)


autolog: logging.Logger = cast("logging.Logger", AutoLogger())
"""Caller-aware logger proxy for module-level use."""
