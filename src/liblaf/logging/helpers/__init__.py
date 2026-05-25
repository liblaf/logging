"""Helper APIs for caller-aware logging and process hooks."""

from ._autolog import AutoLogger, autolog
from ._excepthook import install_excepthook
from ._lazy import LazyRepr, LazyStr
from ._level import add_levels
from ._logger import Logger, set_logger_level_by_release_type
from ._remove_handlers import remove_non_root_stream_handlers
from ._setup_rich import setup_rich
from ._unraisablehook import install_unraisablehook

__all__ = [
    "AutoLogger",
    "LazyRepr",
    "LazyStr",
    "Logger",
    "add_levels",
    "autolog",
    "install_excepthook",
    "install_unraisablehook",
    "remove_non_root_stream_handlers",
    "set_logger_level_by_release_type",
    "setup_rich",
]
