"""Application-level logging initialization."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

import rich
import rich.pretty

from ._config import config
from .filters import LimitsFilter
from .handlers import FileHandler, RichHandler
from .helpers import (
    SanitizedLogger,
    add_levels,
    install_excepthook,
    install_unraisablehook,
    sanitize_loggers,
    set_logger_level_by_release_type,
    setup_rich,
)

if TYPE_CHECKING:
    from _typeshed import StrPath

_DEFAULT_LEVELS: dict[str, int | str] = {
    "__main__": 1,
    "IPKernelApp": logging.WARNING,
    "liblaf": logging.DEBUG,
    "nox": logging.CRITICAL,
    "urllib3.connectionpool": logging.CRITICAL,
}


def init(
    *,
    file: StrPath | None = None,
    force: bool = False,
    handlers: Iterable[logging.Handler] | None = None,
    level: int | str | None = None,
    time_relative: bool | None = None,
) -> None:
    """Configure process-wide logging defaults.

    The initializer installs the package logger class, Rich formatting,
    exception hooks, warning capture, default noisy-library levels, and optional
    file output. When no explicit `handlers` are provided and the root logger
    needs handlers, `init` creates a Rich console handler, optionally creates a
    Rich-formatted file handler, and attaches a
    [`LimitsFilter`][liblaf.logging.filters.LimitsFilter] to each managed
    handler.

    Args:
        file: Optional file path for a Rich-formatted file handler.
        force: Pass `True` to replace existing root handlers.
        handlers: Explicit handlers for `logging.basicConfig`. When provided,
            no default Rich or file handlers are created.
        level: Root logging level passed to `logging.basicConfig`. Defaults to
            `config.level`.
        time_relative: Override whether Rich handler timestamps are relative.
    """
    if file is None:
        file: Path | None = config.file.get()
    if level is None:
        level: str = config.level.get()
    logging.setLoggerClass(SanitizedLogger)
    setup_rich()
    if handlers is None and (force or not logging.root.hasHandlers()):
        handlers: list[logging.Handler] = [RichHandler(time_relative=time_relative)]
        if file is not None:
            handlers.append(FileHandler(file, time_relative=time_relative))
        for handler in handlers:
            handler.addFilter(LimitsFilter())
    add_levels()
    install_excepthook()
    install_unraisablehook()
    logging.basicConfig(level=level, handlers=handlers, force=force)
    logging.captureWarnings(True)  # noqa: FBT003
    rich.pretty.install()
    sanitize_loggers()
    set_logger_level_by_release_type()
    for name, level_ in _DEFAULT_LEVELS.items():
        logger: logging.Logger = logging.getLogger(name)
        logger.setLevel(level_)
