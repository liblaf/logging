"""Rich rendering for log records."""

import logging
from collections.abc import Iterable
from typing import override

import attrs
import rich
import rich.protocol
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.highlighter import Highlighter, ReprHighlighter
from rich.pretty import Pretty
from rich.segment import Segment
from rich.text import Text
from rich.traceback import Traceback

from liblaf.logging._config import config

from .columns import (
    RichHandlerColumn,
    RichHandlerColumnLevel,
    RichHandlerColumnLocation,
    RichHandlerColumnTime,
)


@attrs.frozen
class _Prefix:
    """Renderable that prefixes every rendered line."""

    prefix: RenderableType
    renderable: RenderableType

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        prefix: list[Segment] = list(console.render(self.prefix, options))
        prefix_width: int = sum(segment.cell_length for segment in prefix)
        options: ConsoleOptions = options.update_width(options.max_width - prefix_width)
        options.max_width = max(options.max_width, 1)
        segments: Iterable[Segment] = console.render(self.renderable, options)
        for line in Segment.split_lines(segments):
            yield from prefix
            yield from line
            yield Segment.line()


class RichHandler(logging.Handler):
    """Render log records with Rich.

    The default layout includes relative or absolute time, an abbreviated level,
    and a `logger:function:line` location column before the message. Renderable
    messages are passed through, formatted string messages are highlighted, and
    exception information is rendered as a Rich traceback.

    Args:
        console: Rich console used for output. Defaults to `rich.get_console()`.
        columns: Optional columns to render before each message.
        level: Initial handler level.
        time_relative: Override relative timestamp rendering for default
            columns.
    """

    columns: list[RichHandlerColumn]
    console: Console
    highlighter: Highlighter

    @staticmethod
    def _default_columns(
        *, time_relative: bool | None = None
    ) -> list[RichHandlerColumn]:
        if time_relative is None:
            time_relative: bool = config.time_relative.get()
        return [
            RichHandlerColumnTime(relative=time_relative),
            RichHandlerColumnLevel(),
            RichHandlerColumnLocation(),
        ]

    def __init__(
        self,
        console: Console | None = None,
        *,
        columns: Iterable[RichHandlerColumn] | None = None,
        level: int = logging.NOTSET,
        time_relative: bool | None = None,
    ) -> None:
        super().__init__(level=level)
        if console is None:
            console: Console = rich.get_console()
        if columns is None:
            columns: list[RichHandlerColumn] = self._default_columns(
                time_relative=time_relative
            )
        else:
            columns: list[RichHandlerColumn] = list(columns)
        self.columns = columns
        self.console = console
        self.highlighter = ReprHighlighter()

    @override
    def emit(self, record: logging.LogRecord) -> None:
        """Render and print `record`, delegating failures to `handleError`."""
        try:
            self.console.print(
                self._render(record), sep="", highlight=False, soft_wrap=True
            )
            if (exception := self._render_exception(record)) is not None:
                self.console.print(exception)
        except Exception:  # noqa: BLE001
            self.handleError(record)

    def _render(self, record: logging.LogRecord) -> RenderableType:
        """Build the Rich renderable for a log record."""
        columns: list[Text] = [
            result
            for column in self.columns
            if (result := column.render(record)) is not None
        ]
        prefix: Text = Text(" ", end=" ").join(columns)
        return _Prefix(prefix, self._render_message(record))

    def _render_exception(self, record: logging.LogRecord) -> Traceback | None:
        """Render exception information attached to `record`."""
        if record.exc_info is None:
            return None
        exc_type, exc_value, traceback = record.exc_info
        if exc_type is None or exc_value is None:
            return None
        return Traceback.from_exception(
            exc_type,
            exc_value,
            traceback,
            width=None,
            extra_lines=1,
            show_locals=True,
            locals_max_length=6,
            locals_max_string=30,
            locals_max_depth=6,
            locals_hide_sunder=True,
        )

    def _render_message(self, record: logging.LogRecord) -> RenderableType:
        """Render the record message body."""
        if record.args:
            message: str = record.getMessage()
            return self._render_str(message)
        if rich.protocol.is_renderable(record.msg):
            if isinstance(record.msg, str):
                return self._render_str(record.msg)
            return record.msg
        return Pretty(
            record.msg, indent_guides=True, max_length=6, max_string=30, max_depth=6
        )

    def _render_str(self, message: str) -> Text:
        if "\x1b" in message:
            return Text.from_ansi(message)
        return self.highlighter(message)
