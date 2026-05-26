"""Log-record location column rendering."""

from logging import LogRecord
from typing import override

from rich.text import Text

from ._base import RichHandlerColumn


class RichHandlerColumnLocation(RichHandlerColumn):
    """Render `logger:function:line` for normal records."""

    @override
    def render(self, record: LogRecord) -> Text | None:
        """Render a location label for `record`."""
        if record.name == "py.warnings":
            return Text(record.name, "log.path")
        plain: str = f"{record.name}:{record.funcName}:{record.lineno}"
        return Text(plain, "log.path")
