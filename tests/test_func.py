from __future__ import annotations

import inspect
import logging

import pytest

import liblaf.logging
from liblaf.logging import _func as func_module


def _log_from_helper() -> None:
    liblaf.logging.warning("wrapped", stacklevel=2)


def test_module_level_helpers_use_caller_logger_and_location(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger=__name__):
        frame = inspect.currentframe()
        assert frame is not None
        lineno = frame.f_lineno + 1
        _log_from_helper()

    record = caplog.records[-1]
    assert record.name == __name__
    assert record.funcName == "test_module_level_helpers_use_caller_logger_and_location"
    assert record.lineno == lineno


def test_get_logger_uses_caller_module() -> None:
    assert liblaf.logging.get_logger().name == __name__


def test_get_logger_falls_back_to_root_when_no_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(func_module.magic, "get_frame", lambda **_kwargs: None)

    assert liblaf.logging.get_logger() is logging.getLogger()


def test_module_level_helpers_fall_back_to_root_when_no_frame(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(
        func_module.magic,
        "get_frame_with_stacklevel",
        lambda **_kwargs: (None, 1),
    )

    with caplog.at_level(logging.WARNING):
        liblaf.logging.warning("from root")

    assert caplog.records[-1].name == "root"
