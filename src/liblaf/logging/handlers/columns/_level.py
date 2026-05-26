"""Log-level column rendering."""

import logging
from typing import override

import attrs
from rich.align import AlignMethod
from rich.text import Text

from ._base import RichHandlerColumn

_LEVEL_ALIASES: dict[int, dict[str, str]] = {
    1: {"ICECREAM": "M"},
    3: {
        "NOTSET": "NST",
        "TRACE": "TRC",
        "DEBUG": "DBG",
        "ICECREAM": "ICM",
        "INFO": "INF",
        "SUCCESS": "SUC",
        "WARNING": "WRN",
        "ERROR": "ERR",
        "CRITICAL": "CRT",
    },
}


@attrs.define
class RichHandlerColumnLevel(RichHandlerColumn):
    """Render an aligned, abbreviated log level."""

    align: AlignMethod = "right"
    width: int = 3

    @override
    def render(self, record: logging.LogRecord) -> Text:
        """Render the level name for `record`."""
        level: str = self._get_abbr(record)
        text = Text(level, f"logging.level.{record.levelname.lower()}")
        text.align(self.align, self.width)
        return text

    def _get_abbr(self, record: logging.LogRecord) -> str:
        """Return the display abbreviation for `record`."""
        if record.levelname == f"Level {record.levelno}":
            return str(record.levelno)
        aliases: dict[str, str] = _LEVEL_ALIASES.get(self.width, {})
        return aliases.get(record.levelname, record.levelname)
