from __future__ import annotations

import io
import logging
import sys
import types
import uuid
from pathlib import Path

import pytest

from liblaf.logging.helpers import (
    SanitizedLogger,
    add_levels,
    sanitize_loggers,
    set_logger_level_by_release_type,
)
from liblaf.logging.helpers import _logger as logger_module
from liblaf.logging.helpers import _setup_rich as setup_rich_module


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

    monkeypatch.setattr(SanitizedLogger, "dev_level", logging.INFO)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = SanitizedLogger(module.__name__)

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

    monkeypatch.setattr(SanitizedLogger, "pre_level", logging.WARNING)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = SanitizedLogger(module.__name__)

    assert logger.level == logging.WARNING


def test_logger_keeps_notset_for_stable_modules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module("sample.stable", "sample-stable.py")

    monkeypatch.setattr(
        logger_module.magic,
        "is_dev_release",
        lambda _file=None, _name=None: False,
    )
    monkeypatch.setattr(
        logger_module.magic,
        "is_pre_release",
        lambda _file=None, _name=None: False,
    )
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = SanitizedLogger(module.__name__)

    assert logger.level == logging.NOTSET


def test_explicit_logger_level_bypasses_release_detection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_release_probe(_file: object = None, _name: str | None = None) -> bool:
        msg = "release probes should not run for explicit logger levels"
        raise AssertionError(msg)

    monkeypatch.setattr(logger_module.magic, "is_dev_release", fail_release_probe)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", fail_release_probe)

    logger = SanitizedLogger("sample.explicit", level=logging.ERROR)

    assert logger.level == logging.ERROR


def test_logger_falls_back_to_visible_caller_frame_when_module_has_no_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = types.ModuleType("sample.no_file")
    calls: list[tuple[object, str | None]] = []

    def is_dev_release(file: object = None, name: str | None = None) -> bool:
        calls.append((file, name))
        return True

    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        msg = "pre-release probe should not run after a development match"
        raise AssertionError(msg)

    monkeypatch.setattr(SanitizedLogger, "dev_level", logging.INFO)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = SanitizedLogger(module.__name__)

    assert logger.level == logging.INFO
    assert calls == [(__file__, "sample.no_file")]


def test_logger_keeps_notset_when_no_module_file_or_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = types.ModuleType("sample.no_context")
    calls: list[tuple[object, str | None]] = []

    def is_dev_release(file: object = None, name: str | None = None) -> bool:
        calls.append((file, name))
        return False

    def is_pre_release(file: object = None, name: str | None = None) -> bool:
        calls.append((file, name))
        return False

    monkeypatch.setattr(logger_module.magic, "get_frame", lambda **_kwargs: None)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)
    monkeypatch.setitem(sys.modules, module.__name__, module)

    logger = SanitizedLogger(module.__name__)

    assert logger.level == logging.NOTSET
    assert calls == [(None, "sample.no_context"), (None, "sample.no_context")]


def test_logger_keeps_notset_when_module_is_missing_and_no_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    name = f"sample.missing.{uuid.uuid4().hex}"
    calls: list[tuple[object, str | None]] = []

    def is_dev_release(file: object = None, name: str | None = None) -> bool:
        calls.append((file, name))
        return False

    def is_pre_release(file: object = None, name: str | None = None) -> bool:
        calls.append((file, name))
        return False

    monkeypatch.setattr(logger_module.magic, "get_frame", lambda **_kwargs: None)
    monkeypatch.setattr(logger_module.magic, "is_dev_release", is_dev_release)
    monkeypatch.setattr(logger_module.magic, "is_pre_release", is_pre_release)

    logger = SanitizedLogger(name)

    assert logger.level == logging.NOTSET
    assert calls == [(None, name), (None, name)]


def test_logger_propagate_cannot_be_disabled() -> None:
    logger = SanitizedLogger("sample.propagate", level=logging.INFO)

    logger.propagate = False

    assert logger.propagate is True


def test_non_root_logger_rejects_stream_handlers() -> None:
    logger = SanitizedLogger("sample.non_root", level=logging.INFO)
    handler = logging.StreamHandler()

    logger.addHandler(handler)

    assert handler not in logger.handlers


def test_non_root_logger_accepts_non_stream_handlers() -> None:
    logger = SanitizedLogger("sample.non_root", level=logging.INFO)
    handler = logging.NullHandler()

    logger.addHandler(handler)

    assert handler in logger.handlers


def test_root_logger_accepts_stream_handlers() -> None:
    logger = SanitizedLogger("root", level=logging.INFO)
    handler = logging.StreamHandler()

    logger.addHandler(handler)

    assert handler in logger.handlers


def test_set_logger_level_by_release_type_updates_global_logger_class() -> None:
    previous_class = logging.getLoggerClass()
    previous_dev_level = SanitizedLogger.dev_level
    previous_pre_level = SanitizedLogger.pre_level

    try:
        set_logger_level_by_release_type(dev_level=logging.INFO, pre_level="WARNING")

        assert logging.getLoggerClass() is SanitizedLogger
        assert SanitizedLogger.dev_level == logging.INFO
        assert SanitizedLogger.pre_level == "WARNING"
    finally:
        logging.setLoggerClass(previous_class)
        SanitizedLogger.dev_level = previous_dev_level
        SanitizedLogger.pre_level = previous_pre_level


def test_set_logger_level_by_release_type_can_update_one_level() -> None:
    previous_class = logging.getLoggerClass()
    previous_dev_level = SanitizedLogger.dev_level
    previous_pre_level = SanitizedLogger.pre_level

    try:
        set_logger_level_by_release_type(dev_level=logging.INFO)

        assert logging.getLoggerClass() is SanitizedLogger
        assert SanitizedLogger.dev_level == logging.INFO
        assert SanitizedLogger.pre_level == previous_pre_level
    finally:
        logging.setLoggerClass(previous_class)
        SanitizedLogger.dev_level = previous_dev_level
        SanitizedLogger.pre_level = previous_pre_level


def test_set_logger_level_by_release_type_can_update_pre_level_only() -> None:
    previous_class = logging.getLoggerClass()
    previous_dev_level = SanitizedLogger.dev_level
    previous_pre_level = SanitizedLogger.pre_level

    try:
        set_logger_level_by_release_type(pre_level=logging.ERROR)

        assert logging.getLoggerClass() is SanitizedLogger
        assert SanitizedLogger.dev_level == previous_dev_level
        assert SanitizedLogger.pre_level == logging.ERROR
    finally:
        logging.setLoggerClass(previous_class)
        SanitizedLogger.dev_level = previous_dev_level
        SanitizedLogger.pre_level = previous_pre_level


def test_add_levels_registers_trace_and_icecream_names() -> None:
    add_levels()

    assert logging.getLevelName(5) == "TRACE"
    assert logging.getLevelName("TRACE") == 5
    assert logging.getLevelName(25) == "ICECREAM"
    assert logging.getLevelName("ICECREAM") == 25


def test_sanitize_loggers_preserves_root_and_non_stdio_handlers(
    tmp_path: Path,
) -> None:
    name = f"tests.remove_handlers.{uuid.uuid4().hex}"
    previous_class = logging.getLoggerClass()
    logging.setLoggerClass(logging.Logger)
    logger = logging.getLogger(name)
    root = logging.getLogger()
    root_handler = logging.StreamHandler(sys.stderr)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stdout_handler = logging.StreamHandler(sys.stdout)
    memory_handler = logging.StreamHandler(io.StringIO())
    file_handler = logging.FileHandler(tmp_path / "app.log")

    try:
        root.addHandler(root_handler)
        logger.handlers[:] = []
        logger.addHandler(stderr_handler)
        logger.addHandler(stdout_handler)
        logger.addHandler(memory_handler)
        logger.addHandler(file_handler)

        sanitize_loggers()

        assert root_handler in root.handlers
        assert stderr_handler not in logger.handlers
        assert stdout_handler not in logger.handlers
        assert memory_handler in logger.handlers
        assert file_handler in logger.handlers
    finally:
        for handler in [root_handler, stderr_handler, stdout_handler, memory_handler]:
            root.removeHandler(handler)
            logger.removeHandler(handler)
            handler.close()
        logger.removeHandler(file_handler)
        file_handler.close()
        logging.root.manager.loggerDict.pop(name, None)
        logging.setLoggerClass(previous_class)


def test_sanitize_loggers_skips_root_named_logger() -> None:
    root_like = logging.getLogger()
    handler = logging.StreamHandler(sys.stderr)
    key = f"tests.root_like.{uuid.uuid4().hex}"

    try:
        root_like.addHandler(handler)
        logging.root.manager.loggerDict[key] = root_like

        sanitize_loggers()

        assert handler in root_like.handlers
    finally:
        root_like.removeHandler(handler)
        handler.close()
        logging.root.manager.loggerDict.pop(key, None)


def test_setup_rich_reconfigures_rich_to_use_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        setup_rich_module.rich,
        "reconfigure",
        lambda **kwargs: calls.append(kwargs),
    )

    setup_rich_module.setup_rich()

    assert calls == [{"stderr": True}]
