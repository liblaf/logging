from __future__ import annotations

import logging
import sys
import types

import pytest

from liblaf.logging.helpers import Logger, set_logger_level_by_release_type
from liblaf.logging.helpers import _logger as logger_module


def _module(name: str, file: str) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__file__ = file
    return module


def test_logger_uses_dev_level_for_development_modules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module("sample.dev", "sample-dev.py")
    calls: list[tuple[object, str | None]] = []

    def is_dev_release(file: object = None, name: str | None = None) -> bool:
        calls.append((file, name))
        return True

    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        msg = "pre-release probe should not run after a development match"
        raise AssertionError(msg)

    monkeypatch.setattr(Logger, "dev_level", logging.INFO)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = Logger(module.__name__)

    assert logger.level == logging.INFO
    assert calls == [("sample-dev.py", "sample.dev")]


def test_logger_uses_pre_level_for_prerelease_modules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module("sample.pre", "sample-pre.py")

    def is_dev_release(_file: object = None, _name: str | None = None) -> bool:
        return False

    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        return True

    monkeypatch.setattr(Logger, "pre_level", logging.WARNING)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = Logger(module.__name__)

    assert logger.level == logging.WARNING


def test_explicit_logger_level_bypasses_release_detection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_release_probe(_file: object = None, _name: str | None = None) -> bool:
        msg = "release probes should not run for explicit logger levels"
        raise AssertionError(msg)

    monkeypatch.setattr(logger_module.magic, "is_dev_release", fail_release_probe)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", fail_release_probe)

    logger = Logger("sample.explicit", level=logging.ERROR)

    assert logger.level == logging.ERROR


def test_non_root_logger_rejects_stream_handlers() -> None:
    logger = Logger("sample.non_root", level=logging.INFO)
    handler = logging.StreamHandler()

    logger.addHandler(handler)

    assert handler not in logger.handlers


def test_root_logger_accepts_stream_handlers() -> None:
    logger = Logger("root", level=logging.INFO)
    handler = logging.StreamHandler()

    logger.addHandler(handler)

    assert handler in logger.handlers


def test_set_logger_level_by_release_type_updates_global_logger_class() -> None:
    previous_class = logging.getLoggerClass()
    previous_dev_level = Logger.dev_level
    previous_pre_level = Logger.pre_level

    try:
        set_logger_level_by_release_type(dev_level=logging.INFO, pre_level="WARNING")

        assert logging.getLoggerClass() is Logger
        assert Logger.dev_level == logging.INFO
        assert Logger.pre_level == "WARNING"
    finally:
        logging.setLoggerClass(previous_class)
        Logger.dev_level = previous_dev_level
        Logger.pre_level = previous_pre_level
