"""Rich logging setup, handlers, filters, and caller-aware helpers."""

from . import filters, handlers, helpers, magic
from ._config import config
from ._func import critical, debug, error, exception, get_logger, info, log, warning
from ._init import init
from ._version import __commit_id__, __version__, __version_tuple__
from .filters import LimitsFilter
from .handlers import FileHandler, RichHandler
from .helpers import LazyRepr

__all__ = [
    "FileHandler",
    "LazyRepr",
    "LimitsFilter",
    "RichHandler",
    "__commit_id__",
    "__version__",
    "__version_tuple__",
    "autolog",
    "config",
    "critical",
    "debug",
    "error",
    "exception",
    "filters",
    "get_logger",
    "handlers",
    "helpers",
    "info",
    "init",
    "log",
    "magic",
    "warning",
]
