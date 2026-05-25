"""Timestamp column rendering."""

from datetime import datetime
from logging import LogRecord
from typing import override

import attrs
from rich.text import Text

from liblaf.logging._config import config

from ._base import RichHandlerColumn


@attrs.define
class RichHandlerColumnTime(RichHandlerColumn):
    """Render either relative or absolute record time."""

    fmt: str = attrs.field(factory=config.datefmt.get)
    relative: bool = attrs.field(factory=config.time_relative.get)

    @override
    def render(self, record: LogRecord) -> Text:
        """Render the timestamp for `record`."""
        if self.relative:
            plain: str = self._render_relative(record)
        else:
            plain: str = self._render_absolute(record)
        return Text(plain, "log.time")

    def _render_absolute(self, record: LogRecord) -> str:
        """Render an absolute local timestamp."""
        time: datetime = datetime.fromtimestamp(record.created).astimezone()
        return time.strftime(self.fmt)

    def _render_relative(self, record: LogRecord) -> str:
        """Render elapsed logging time as `DDd,HH:MM:SS.mmm` when needed."""
        milliseconds: int = round(record.relativeCreated)
        days, milliseconds = divmod(milliseconds, 86400000)
        hours, milliseconds = divmod(milliseconds, 3600000)
        minutes, milliseconds = divmod(milliseconds, 60000)
        seconds, milliseconds = divmod(milliseconds, 1000)
        text: str = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
        return f"{days}d,{text}" if days > 0 else text
