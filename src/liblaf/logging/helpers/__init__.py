"""Helper APIs for caller-aware logging and process hooks."""

from ._excepthook import install_excepthook
from ._lazy import LazyRepr
from ._level import add_levels
from ._logger import SanitizedLogger, set_logger_level_by_release_type
from ._sanitize_loggers import sanitize_loggers
from ._setup_rich import setup_rich
from ._unraisablehook import install_unraisablehook

__all__ = [
    "LazyRepr",
    "SanitizedLogger",
    "add_levels",
    "install_excepthook",
    "install_unraisablehook",
    "sanitize_loggers",
    "set_logger_level_by_release_type",
    "setup_rich",
]
