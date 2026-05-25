"""Rich-formatted file logging."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, override

from rich.console import Console

from ._rich import RichHandler
from .columns import RichHandlerColumn

if TYPE_CHECKING:
    from _typeshed import StrPath


class FileHandler(RichHandler):
    """Write Rich-rendered log records to a file.

    The handler creates parent directories automatically. With the default
    `delay=True`, the file is opened only when the first record is emitted.

    Args:
        filename: Destination file path.
        columns: Optional Rich columns used before each message.
        delay: Defer opening the file until first emit.
        level: Initial handler level.
        time_relative: Override relative timestamp rendering for default
            columns.
        mode: File open mode.
        encoding: File encoding passed to `Path.open`.
        errors: Encoding error policy passed to `Path.open`.
    """

    console: Console | None
    encoding: str | None
    filename: Path
    mode: str
    errors: str | None

    def __init__(
        self,
        filename: StrPath,
        *,
        columns: Iterable[RichHandlerColumn] | None = None,
        delay: bool = True,
        level: int = logging.NOTSET,
        time_relative: bool | None = None,
        # open() options
        mode: str = "w",
        encoding: str | None = None,
        errors: str | None = None,
    ) -> None:
        self.encoding = encoding
        self.filename = Path(filename)
        self.mode = mode
        self.errors = errors
        if delay:
            console: None = None
        else:
            console: Console = self._open()
        super().__init__(
            console=console, columns=columns, level=level, time_relative=time_relative
        )
        if delay:
            self.console = None

    @override
    def close(self) -> None:
        """Close the backing file when it has been opened."""
        if self.console:
            self.console.file.close()
        super().close()

    @override
    def emit(self, record: logging.LogRecord) -> None:
        """Open the file if needed and emit `record`."""
        try:
            if self.console is None:
                self.console = self._open()
            super().emit(record)
        except Exception:  # noqa: BLE001
            self.handleError(record)

    def _open(self) -> Console:
        """Open the destination file and wrap it in a Rich console."""
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        return Console(
            file=self.filename.open(
                self.mode, encoding=self.encoding, errors=self.errors
            )
        )
