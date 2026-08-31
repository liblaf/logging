"""Rich logging setup, handlers, filters, and caller-aware helpers."""

from typing import Any

from . import filters, handlers, helpers, magic, progress
from ._config import config
from ._debug import ICECREAM, ICON, DebugEvent
from ._func import (
    critical,
    debug,
    error,
    exception,
    get_logger,
    ic,
    info,
    log,
    make_log,
    make_print,
    warning,
)
from ._init import init, restore
from ._version import __commit_id__, __version__, __version_tuple__
from .filters import LimitsFilter
from .handlers import FileHandler, RichHandler
from .helpers import LazyRepr
from .progress import get_progress

__all__ = [
    "ICECREAM",
    "ICON",
    "DebugEvent",
    "FileHandler",
    "LazyRepr",
    "LimitsFilter",
    "RichHandler",
    "__commit_id__",
    "__version__",
    "__version_tuple__",
    "config",
    "critical",
    "debug",
    "error",
    "exception",
    "filters",
    "get_logger",
    "get_progress",
    "handlers",
    "helpers",
    "ic",
    "info",
    "init",
    "log",
    "magic",
    "make_log",
    "make_print",
    "progress",
    "restore",
    "warning",
]


def __getattr__(name: str) -> Any:
    if name in {"Progress", "SpeedColumn"}:
        return getattr(progress, name)
    raise AttributeError(name)
