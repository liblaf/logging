from __future__ import annotations

import io
import logging
from pathlib import Path

from rich.console import Console
from rich.text import Text

from liblaf.logging.handlers import FileHandler, RichHandler
from liblaf.logging.handlers.columns import (
    RichHandlerColumnLevel,
    RichHandlerColumnLocation,
    RichHandlerColumnTime,
)


def make_record(
    *,
    name: str = "tests.handlers",
    level: int = logging.INFO,
    lineno: int = 42,
    msg: object = "hello",
    args: tuple[object, ...] = (),
    func: str = "test_func",
) -> logging.LogRecord:
    return logging.LogRecord(name, level, __file__, lineno, msg, args, None, func)


def render_location_plain(record: logging.LogRecord) -> str:
    text = RichHandlerColumnLocation().render(record)
    assert text is not None
    return text.plain


def test_level_column_abbreviates_known_levels_and_unknown_numbers() -> None:
    assert RichHandlerColumnLevel().render(make_record()).plain == "INF"

    unknown = make_record(level=9)
    assert RichHandlerColumnLevel().render(unknown).plain == "  9"

    icecream = make_record(level=15)
    icecream.levelname = "ICECREAM"
    assert RichHandlerColumnLevel(width=1).render(icecream).plain == "M"


def test_location_column_uses_warning_logger_name_only() -> None:
    assert render_location_plain(make_record()) == "tests.handlers:test_func:42"
    assert render_location_plain(make_record(name="py.warnings")) == "py.warnings"


def test_time_column_renders_relative_and_absolute_times() -> None:
    record = make_record()
    record.relativeCreated = 90_061_002
    record.created = 0

    assert (
        RichHandlerColumnTime(relative=True).render(record).plain == "1d,01:01:01.002"
    )
    assert (
        RichHandlerColumnTime(fmt="%Y", relative=False).render(record).plain == "1970"
    )


def test_rich_handler_writes_renderable_messages() -> None:
    stream = io.StringIO()
    console = Console(file=stream, force_terminal=False, width=80)
    handler = RichHandler(console=console, columns=[])

    handler.emit(make_record(msg=Text("ready")))

    assert stream.getvalue() == " ready\n"


def test_file_handler_opens_lazily_and_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "logs" / "app.log"
    handler = FileHandler(path, columns=[], delay=True)

    assert handler.console is None

    handler.emit(make_record(msg="hello %s", args=("world",)))
    handler.close()

    assert "hello world" in path.read_text()
