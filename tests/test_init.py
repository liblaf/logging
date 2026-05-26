from __future__ import annotations

import logging
import types
from pathlib import Path
from typing import Any

import pytest

from liblaf.logging import _init as init_module


class DummyHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        del record


class Field:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls = 0

    def get(self) -> object:
        self.calls += 1
        return self.value


class FakeLimitsFilter(logging.Filter):
    pass


def patch_init_side_effects(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str, Any]]:
    calls: list[tuple[str, Any]] = []

    monkeypatch.setattr(
        init_module, "setup_rich", lambda: calls.append(("setup_rich", None))
    )
    monkeypatch.setattr(
        init_module, "add_levels", lambda: calls.append(("add_levels", None))
    )
    monkeypatch.setattr(
        init_module,
        "install_excepthook",
        lambda: calls.append(("install_excepthook", None)),
    )
    monkeypatch.setattr(
        init_module,
        "install_unraisablehook",
        lambda: calls.append(("install_unraisablehook", None)),
    )
    monkeypatch.setattr(
        init_module,
        "remove_non_root_stream_handlers",
        lambda: calls.append(("remove_non_root_stream_handlers", None)),
    )
    monkeypatch.setattr(
        init_module,
        "set_logger_level_by_release_type",
        lambda: calls.append(("set_logger_level_by_release_type", None)),
    )
    monkeypatch.setattr(
        init_module.logging,
        "basicConfig",
        lambda **kwargs: calls.append(("basicConfig", kwargs)),
    )
    monkeypatch.setattr(
        init_module.logging,
        "captureWarnings",
        lambda value: calls.append(("captureWarnings", value)),
    )
    monkeypatch.setattr(
        init_module.rich.pretty,
        "install",
        lambda: calls.append(("rich.pretty.install", None)),
    )
    monkeypatch.setattr(init_module, "_DEFAULT_LEVELS", {})
    return calls


def test_init_creates_managed_rich_and_file_handlers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = patch_init_side_effects(monkeypatch)
    created: list[tuple[str, DummyHandler, bool | None, Path | None]] = []

    class FakeRichHandler(DummyHandler):
        def __init__(self, *, time_relative: bool | None = None) -> None:
            super().__init__()
            created.append(("rich", self, time_relative, None))

    class FakeFileHandler(DummyHandler):
        def __init__(
            self, filename: str | Path, *, time_relative: bool | None = None
        ) -> None:
            super().__init__()
            created.append(("file", self, time_relative, Path(filename)))

    monkeypatch.setattr(init_module, "RichHandler", FakeRichHandler)
    monkeypatch.setattr(init_module, "FileHandler", FakeFileHandler)
    monkeypatch.setattr(init_module, "LimitsFilter", FakeLimitsFilter)

    path = tmp_path / "logs" / "app.log"

    init_module.init(file=path, force=True, level="INFO", time_relative=False)

    handlers = [handler for _, handler, _, _ in created]
    assert [kind for kind, _, _, _ in created] == ["rich", "file"]
    assert [time_relative for _, _, time_relative, _ in created] == [False, False]
    assert created[1][3] == path
    assert all(
        len(handler.filters) == 1 and isinstance(handler.filters[0], FakeLimitsFilter)
        for handler in handlers
    )
    assert (
        "basicConfig",
        {"level": "INFO", "handlers": handlers, "force": True},
    ) in calls
    assert [name for name, _ in calls] == [
        "setup_rich",
        "add_levels",
        "install_excepthook",
        "install_unraisablehook",
        "basicConfig",
        "captureWarnings",
        "remove_non_root_stream_handlers",
        "rich.pretty.install",
        "set_logger_level_by_release_type",
    ]


def test_init_creates_only_rich_handler_without_file_and_sets_default_levels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = patch_init_side_effects(monkeypatch)
    created: list[DummyHandler] = []
    logger_name = "tests.init.noisy_library"
    logger = logging.getLogger(logger_name)
    previous_level = logger.level

    class FakeRichHandler(DummyHandler):
        def __init__(self, *, time_relative: bool | None = None) -> None:
            super().__init__()
            self.time_relative = time_relative
            created.append(self)

    monkeypatch.setattr(init_module, "RichHandler", FakeRichHandler)
    monkeypatch.setattr(
        init_module,
        "FileHandler",
        lambda *_args, **_kwargs: pytest.fail("FileHandler should not be created"),
    )
    monkeypatch.setattr(init_module, "LimitsFilter", FakeLimitsFilter)
    monkeypatch.setattr(init_module, "_DEFAULT_LEVELS", {logger_name: "ERROR"})
    monkeypatch.setattr(
        init_module,
        "config",
        types.SimpleNamespace(file=Field(None), level=Field("DEBUG")),
    )

    try:
        init_module.init(force=True)

        assert len(created) == 1
        assert created[0].filters
        assert isinstance(created[0].filters[0], FakeLimitsFilter)
        assert (
            "basicConfig",
            {"level": "DEBUG", "handlers": created, "force": True},
        ) in calls
        assert logger.level == logging.ERROR
    finally:
        logger.setLevel(previous_level)
        logging.root.manager.loggerDict.pop(logger_name, None)


def test_init_uses_explicit_handlers_without_managing_filters(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = patch_init_side_effects(monkeypatch)
    file_field = Field(tmp_path / "configured.log")
    level_field = Field("WARNING")
    provided = DummyHandler()

    monkeypatch.setattr(
        init_module,
        "config",
        types.SimpleNamespace(file=file_field, level=level_field),
    )
    monkeypatch.setattr(
        init_module,
        "RichHandler",
        lambda **_kwargs: pytest.fail("RichHandler should not be created"),
    )
    monkeypatch.setattr(
        init_module,
        "FileHandler",
        lambda *_args, **_kwargs: pytest.fail("FileHandler should not be created"),
    )

    init_module.init(handlers=[provided])

    assert provided.filters == []
    assert file_field.calls == 1
    assert level_field.calls == 1
    assert (
        "basicConfig",
        {"level": "WARNING", "handlers": [provided], "force": False},
    ) in calls
