from __future__ import annotations

import logging
import sys
import types
import warnings
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from rich.text import Text

from liblaf.logging import (
    DebugEvent,
    _adapters,
    _func,
    _init,
    ic,
    make_log,
    make_print,
)
from liblaf.logging.handlers import FileHandler, RichHandler


@pytest.fixture(autouse=True)
def reset_init() -> Iterator[None]:
    _init.restore()
    yield
    _init.restore()


def test_optional_traceback_adapter_wraps_the_peer_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[BaseException, object]] = []
    peer = types.ModuleType("liblaf.traceback")

    def render_exception(exc: BaseException, *, traceback: object) -> Text:
        calls.append((exc, traceback))
        return Text("peer")

    peer.__dict__["render_exception"] = render_exception
    monkeypatch.setitem(sys.modules, "liblaf.traceback", peer)
    formatter = _adapters.default_exception_formatter()
    exc = ValueError("x")

    result = formatter(ValueError, exc, None)
    assert isinstance(result, Text)
    assert result.plain == "peer"
    assert calls == [(exc, None)]


def test_optional_pprint_adapter_is_resolved_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    peer = types.ModuleType("liblaf.pprint")

    def render(value: Any) -> Text:
        return Text(f"peer:{value}")

    peer.__dict__["render"] = render
    monkeypatch.setitem(sys.modules, "liblaf.pprint", peer)

    assert _adapters.default_object_formatter() is render


def test_init_is_idempotent_rejects_difference_and_force_rebuilds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(_init, "sanitize_loggers", lambda: None)
    monkeypatch.setattr(_init, "set_logger_level_by_release_type", lambda: None)
    monkeypatch.setattr(_init, "setup_rich", lambda: None)

    _init.init(force=True, level="INFO")
    _init.init(level="INFO")
    with pytest.raises(RuntimeError, match="force=True"):
        _init.init(level="DEBUG")
    _init.init(force=True, level="DEBUG")

    assert len(calls) == 2


def test_managed_handlers_share_resolved_formatters(tmp_path: Path) -> None:
    def exception(
        _exc_type: type[BaseException],
        _exc: BaseException,
        _traceback: types.TracebackType | None,
    ) -> Text:
        return Text("exception")

    def object_(_value: Any) -> Text:
        return Text("object")

    handlers = _init._configured_handlers(  # noqa: SLF001
        file=tmp_path / "app.log",
        force=True,
        handlers=None,
        time_relative=None,
        exception_formatter=exception,
        object_formatter=object_,
    )
    assert handlers is not None
    assert (
        sum(
            isinstance(handler, RichHandler)
            and getattr(handler, "managed_stderr", False)
            for handler in handlers
        )
        == 1
    )
    assert isinstance(handlers[1], FileHandler)
    assert all(
        getattr(handler, "exception_formatter", None) is exception
        for handler in handlers
    )
    assert all(
        getattr(handler, "object_formatter", None) is object_ for handler in handlers
    )


def test_restore_does_not_clobber_replaced_global_hooks() -> None:
    original_exception, original_unraisable = sys.excepthook, sys.unraisablehook
    original_warning, original_display = warnings.showwarning, sys.displayhook
    _init.init(force=True)

    def replacement(*_args: object) -> None:
        return None

    sys.excepthook = replacement
    sys.unraisablehook = replacement
    warnings.showwarning = cast("Any", replacement)
    sys.displayhook = replacement
    _init.restore()
    assert sys.excepthook is replacement
    assert sys.unraisablehook is replacement
    assert warnings.showwarning is replacement
    assert sys.displayhook is replacement
    sys.excepthook, sys.unraisablehook = original_exception, original_unraisable
    warnings.showwarning, sys.displayhook = original_warning, original_display


def test_warning_capture_preserves_an_existing_logging_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = warnings.showwarning
    monkeypatch.setattr(logging, "_warnings_showwarning", existing, raising=False)

    restore = _init._capture_warnings()  # noqa: SLF001
    restore()

    assert warnings.showwarning is existing
    assert vars(logging)["_warnings_showwarning"] is existing


def test_warning_restore_releases_bookkeeping_without_clobbering_replacement() -> None:
    previous = warnings.showwarning
    restore = _init._capture_warnings()  # noqa: SLF001

    def replacement(*_args: object) -> None:
        return None

    warnings.showwarning = cast("Any", replacement)
    restore()

    assert warnings.showwarning is replacement
    assert vars(logging)["_warnings_showwarning"] is None
    warnings.showwarning = previous


def test_ic_and_factories_return_or_emit(monkeypatch: pytest.MonkeyPatch) -> None:
    records: list[tuple[int, object]] = []

    class Logger:
        def log(
            self, level: int, message: object, *_args: object, **_kwargs: object
        ) -> None:
            records.append((level, message))

    monkeypatch.setattr(_func, "get_logger", lambda **_kwargs: Logger())
    assert ic() is None
    assert ic(1) == 1
    assert ic(1, 2) == (1, 2)
    make_log(17)("ready")
    make_print(18)("a", "b", sep="-")
    assert [level for level, _ in records[-2:]] == [17, 18]
    assert records[-1][1] == "a-b"


def test_ic_captures_names_but_omits_literal_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records: list[logging.LogRecord] = []
    logger = logging.getLogger(__name__)

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = Capture()
    monkeypatch.setattr(logger, "handlers", [handler])
    monkeypatch.setattr(logger, "propagate", False)
    monkeypatch.setattr(logger, "level", 1)
    value = {"answer": 42}

    assert ic(value, 1) == (value, 1)

    event = records[-1].msg
    assert isinstance(event, DebugEvent)
    assert event.pairs == (("value", value), (None, 1))


def test_progress_facade_is_optional() -> None:
    from liblaf.logging import progress

    assert progress.__all__ == ["get_progress"]
    with pytest.raises(ModuleNotFoundError, match="liblaf-progress"):
        progress.get_progress()
