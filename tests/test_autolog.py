from __future__ import annotations

import inspect
import logging
from typing import Any

import pytest

from liblaf.logging.helpers import AutoLogger
from liblaf.logging.helpers import _autolog as autolog_module


def _log_from_helper(logger: Any) -> None:
    logger.warning("wrapped", stacklevel=2)


def test_proxy_methods_use_caller_logger_and_location(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = AutoLogger()

    with caplog.at_level(logging.INFO, logger=__name__):
        frame = inspect.currentframe()
        assert frame is not None
        lineno = frame.f_lineno + 1
        logger.info("hello")

    record = caplog.records[-1]
    assert record.name == __name__
    assert record.funcName == "test_proxy_methods_use_caller_logger_and_location"
    assert record.lineno == lineno


def test_proxy_methods_honor_user_stacklevel(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = AutoLogger()

    with caplog.at_level(logging.WARNING, logger=__name__):
        frame = inspect.currentframe()
        assert frame is not None
        lineno = frame.f_lineno + 1
        _log_from_helper(logger)

    record = caplog.records[-1]
    assert record.name == __name__
    assert record.funcName == "test_proxy_methods_honor_user_stacklevel"
    assert record.lineno == lineno


def test_non_proxy_attributes_are_resolved_from_caller_logger() -> None:
    assert AutoLogger().name == __name__


def test_get_logger_falls_back_to_root_when_no_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(autolog_module.magic, "get_frame", lambda **_kwargs: None)

    assert autolog_module.get_logger() is logging.getLogger()


def test_proxy_methods_fall_back_to_root_when_no_frame(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(
        autolog_module.magic,
        "get_frame_with_stacklevel",
        lambda **_kwargs: (None, 1),
    )

    with caplog.at_level(logging.WARNING):
        AutoLogger().warning("from root")

    assert caplog.records[-1].name == "root"
