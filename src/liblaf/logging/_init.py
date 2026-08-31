"""Application-owned logging setup and hook restoration."""

from __future__ import annotations

import logging
import sys
import warnings
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import rich.pretty

from ._adapters import (
    ExceptionFormatter,
    ObjectFormatter,
    default_exception_formatter,
    default_object_formatter,
)
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


@dataclass(slots=True)
class _InitState:
    fingerprint: tuple[object, ...] | None = None
    restorers: list[Callable[[], None]] = field(default_factory=list)


_state = _InitState()


def restore() -> None:
    """Restore hooks owned by the last `init()` call without touching others.

    Root handlers are deliberately left alone. In particular, restoring hooks
    must not silently discard a file destination or another handler installed
    by the application after initialization.
    """
    while _state.restorers:
        _state.restorers.pop()()
    _state.fingerprint = None


def init(
    *,
    file: StrPath | None = None,
    force: bool = False,
    handlers: Iterable[logging.Handler] | None = None,
    level: int | str | None = None,
    time_relative: bool | None = None,
    exception_formatter: ExceptionFormatter | None = None,
    object_formatter: ObjectFormatter | None = None,
) -> None:
    """Configure logging once; reject incompatible reconfiguration.

    An equivalent repeated call is a no-op. A call with different arguments
    fails visibly unless `force=True`; forced setup restores package-owned
    hooks and rebuilds logging even when its arguments are equivalent.

    When this function creates handlers, it creates exactly one stderr handler
    and shares the same once-resolved exception and object formatters with its
    optional file handler. Explicit application handlers remain application
    owned and are passed directly to `logging.basicConfig`.
    """
    normalized_file = Path(file) if file is not None else config.file.get()
    normalized_level = level if level is not None else config.level.get()
    explicit_handlers = tuple(handlers) if handlers is not None else None
    fingerprint = (
        normalized_file,
        normalized_level,
        time_relative,
        tuple(map(id, explicit_handlers or ())),
        id(exception_formatter),
        id(object_formatter),
    )

    if _state.fingerprint == fingerprint and not force:
        return
    if _state.fingerprint is not None and not force:
        message = "liblaf.logging is already initialized differently; pass force=True"
        raise RuntimeError(message)
    if force:
        restore()

    logging.setLoggerClass(SanitizedLogger)
    setup_rich()
    configured_handlers = _configured_handlers(
        file=normalized_file,
        force=force,
        handlers=explicit_handlers,
        time_relative=time_relative,
        exception_formatter=exception_formatter,
        object_formatter=object_formatter,
    )

    add_levels()
    restorers = [install_excepthook(), install_unraisablehook()]
    try:
        logging.basicConfig(
            level=normalized_level,
            handlers=configured_handlers,
            force=force,
        )
        restorers.extend([_capture_warnings(), _install_pretty_displayhook()])
        sanitize_loggers()
        set_logger_level_by_release_type()
        for name, default_level in _DEFAULT_LEVELS.items():
            logging.getLogger(name).setLevel(default_level)
    except BaseException:
        while restorers:
            restorers.pop()()
        raise

    _state.restorers.extend(restorers)
    _state.fingerprint = fingerprint


def _configured_handlers(
    *,
    file: Path | None,
    force: bool,
    handlers: tuple[logging.Handler, ...] | None,
    time_relative: bool | None,
    exception_formatter: ExceptionFormatter | None,
    object_formatter: ObjectFormatter | None,
) -> list[logging.Handler] | None:
    if handlers is not None:
        return list(handlers)
    if not force and logging.root.hasHandlers():
        return None

    resolved_exception_formatter = (
        default_exception_formatter()
        if exception_formatter is None
        else exception_formatter
    )
    resolved_object_formatter = (
        default_object_formatter() if object_formatter is None else object_formatter
    )
    stderr = RichHandler(
        time_relative=time_relative,
        exception_formatter=resolved_exception_formatter,
        object_formatter=resolved_object_formatter,
    )
    stderr.managed_stderr = True
    configured: list[logging.Handler] = [stderr]
    if file is not None:
        configured.append(
            FileHandler(
                file,
                time_relative=time_relative,
                exception_formatter=resolved_exception_formatter,
                object_formatter=resolved_object_formatter,
            )
        )
    for handler in configured:
        handler.addFilter(LimitsFilter())
    return configured


def _capture_warnings() -> Callable[[], None]:
    previous_capture = getattr(logging, "_warnings_showwarning", None)
    if previous_capture is not None:
        return lambda: None

    previous = warnings.showwarning
    logging.captureWarnings(True)  # noqa: FBT003
    installed = warnings.showwarning

    def restore_warnings() -> None:
        if warnings.showwarning is installed:
            logging.captureWarnings(False)  # noqa: FBT003
            if warnings.showwarning is not previous:
                warnings.showwarning = previous
        elif getattr(logging, "_warnings_showwarning", None) is previous:
            # Another owner replaced the public hook. Release only our private
            # logging bookkeeping so a future capture does not inherit stale
            # state, without overwriting the replacement hook.
            vars(logging)["_warnings_showwarning"] = None

    return restore_warnings


def _install_pretty_displayhook() -> Callable[[], None]:
    previous = sys.displayhook
    rich.pretty.install()
    installed = sys.displayhook

    def restore_displayhook() -> None:
        if sys.displayhook is installed:
            sys.displayhook = previous

    return restore_displayhook
