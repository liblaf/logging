from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from liblaf.logging import _config as config_module


def test_config_file_converts_environment_value_to_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOG_FILE", "logs/app.log")
    config = config_module.Config()

    try:
        config.file.load_env()

        assert config.file.get() == Path("logs/app.log")
    finally:
        config.file.set(None)


def test_config_file_defaults_to_none() -> None:
    assert config_module.Config().file.get() is None


def test_config_level_defaults_to_info() -> None:
    assert config_module.Config().level.get() == "INFO"


def test_path_field_preserves_custom_converter() -> None:
    calls: list[Any] = []

    def converter(value: Any) -> Path | None:
        calls.append(value)
        return Path("custom.log") if value is not None else None

    field = config_module._field_path_or_none(converter=converter)  # noqa: SLF001

    assert field.converter("ignored.log") == Path("custom.log")
    assert calls == ["ignored.log"]
