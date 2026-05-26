"""Custom logger class for release-aware defaults."""

import logging
import sys
import types
from typing import ClassVar, override

from liblaf.logging import magic


class SanitizedLogger(logging.Logger):
    """Logger with package release-aware default levels.

    When a logger is created without an explicit level, its module file is
    checked against selected installed distributions. Files from `.devN`
    distributions use
    [`dev_level`][liblaf.logging.helpers.SanitizedLogger.dev_level], prerelease
    files use [`pre_level`][liblaf.logging.helpers.SanitizedLogger.pre_level],
    and stable files keep the standard `NOTSET` default. `.pth` files inside
    selected distributions contribute source prefixes; installer-specific
    `direct_url.json` metadata is intentionally ignored.
    """

    dev_level: ClassVar[int | str] = 1
    """Default level for development modules."""

    pre_level: ClassVar[int | str] = logging.DEBUG
    """Default level for prerelease modules."""

    def __init__(self, name: str, level: int | str = logging.NOTSET) -> None:
        _logging_hide = True
        super().__init__(name, level)
        if level != logging.NOTSET:
            return
        module: types.ModuleType | None = sys.modules.get(name)
        file: None = None
        if module is not None:
            file: str | None = getattr(module, "__file__", None)
        if file is None:
            frame: types.FrameType | None = magic.get_frame(
                hidden=magic.hidden_from_logging
            )
            if frame is not None:
                file: str = frame.f_code.co_filename
        if magic.is_dev_release(file, name):
            self.setLevel(self.dev_level)
        elif magic.is_pre_release(file, name):
            self.setLevel(self.pre_level)

    @property
    def propagate(self) -> bool:
        """Always propagate records to the root handler."""
        return True

    @propagate.setter
    def propagate(self, value: bool) -> None:
        """Ignore attempts to disable propagation."""

    @override
    def addHandler(self, hdlr: logging.Handler) -> None:
        """Attach handlers, ignoring non-root stream handlers."""
        if (
            self.name != "root"
            and isinstance(hdlr, logging.StreamHandler)
            and (hdlr.stream is sys.stdout or hdlr.stream is sys.stderr)
        ):
            return
        super().addHandler(hdlr)


def set_logger_level_by_release_type(
    dev_level: int | str | None = None, pre_level: int | str | None = None
) -> None:
    """Install [`SanitizedLogger`][liblaf.logging.helpers.SanitizedLogger] globally.

    Args:
        dev_level: Optional replacement level for development modules.
        pre_level: Optional replacement level for prerelease modules.
    """
    if dev_level is not None:
        SanitizedLogger.dev_level = dev_level
    if pre_level is not None:
        SanitizedLogger.pre_level = pre_level
    logging.setLoggerClass(SanitizedLogger)
