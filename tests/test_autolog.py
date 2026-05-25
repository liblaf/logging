from __future__ import annotations

import inspect
import logging
from typing import Any

import pytest

from liblaf.logging.helpers import AutoLogger


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
