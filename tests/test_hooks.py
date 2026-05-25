from __future__ import annotations

import dataclasses
import logging
import sys
import types
from typing import cast

import pytest

from liblaf.logging.helpers import _excepthook as excepthook_module
from liblaf.logging.helpers import _unraisablehook as unraisablehook_module


@dataclasses.dataclass
class RecordingLogger:
    calls: list[tuple[int, object, tuple[object, ...], dict[str, object]]] = (
        dataclasses.field(default_factory=list)
    )

    def log(self, level: int, msg: object, *args: object, **kwargs: object) -> None:
        self.calls.append((level, msg, args, kwargs))


def test_install_excepthook_logs_uncaught_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = RecordingLogger()
    original = sys.excepthook
    monkeypatch.setattr(excepthook_module, "logger", recorder)

    try:
        excepthook_module.install_excepthook(level=logging.ERROR)
        exc = RuntimeError("boom")
        sys.excepthook(type(exc), exc, exc.__traceback__)
    finally:
        sys.excepthook = original

    assert recorder.calls == [
        (
            logging.ERROR,
            exc,
            (),
            {"exc_info": (RuntimeError, exc, None)},
        )
    ]


def test_install_unraisablehook_logs_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = RecordingLogger()
    original = sys.unraisablehook
    monkeypatch.setattr(unraisablehook_module, "logger", recorder)

    try:
        unraisablehook_module.install_unraisablehook(level=logging.WARNING)
        sys.unraisablehook(
            cast(
                "sys.UnraisableHookArgs",
                types.SimpleNamespace(
                    exc_type=None,
                    exc_value=None,
                    exc_traceback=None,
                    err_msg="ignored",
                    object="unused",
                ),
            )
        )
        exc = ValueError("broken cleanup")
        sys.unraisablehook(
            cast(
                "sys.UnraisableHookArgs",
                types.SimpleNamespace(
                    exc_type=ValueError,
                    exc_value=exc,
                    exc_traceback=exc.__traceback__,
                    err_msg="during cleanup",
                    object="resource",
                ),
            )
        )
    finally:
        sys.unraisablehook = original

    assert recorder.calls == [
        (
            logging.WARNING,
            "%s: %r",
            ("during cleanup", "resource"),
            {"exc_info": (ValueError, exc, None)},
        )
    ]
