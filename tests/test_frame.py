from __future__ import annotations

import inspect
import types
from typing import Any

import pytest

from liblaf.logging.magic import _frame as frame_module


def _visible_logging_frame() -> types.FrameType | None:
    return _logging_hidden_frame()


def _logging_hidden_frame() -> types.FrameType | None:
    _logging_hide = True
    return frame_module.get_frame(hidden=frame_module.hidden_from_logging)


def _visible_stacklevel_frame() -> tuple[types.FrameType | None, int]:
    return _stacklevel_hidden_frame()


def _stacklevel_hidden_frame() -> tuple[types.FrameType | None, int]:
    _logging_hide = True
    return frame_module.get_frame_with_stacklevel(
        hidden=frame_module.hidden_from_logging
    )


def _warnings_hidden_frame() -> types.FrameType:
    _warnings_hide = True
    frame = inspect.currentframe()
    assert frame is not None
    return frame


def _current_frame() -> types.FrameType:
    frame = inspect.currentframe()
    assert frame is not None
    return frame


class Field:
    def __init__(self, value: Any) -> None:
        self.value = value

    def get(self) -> Any:
        return self.value


def test_get_frame_skips_logging_hidden_frames() -> None:
    frame = _visible_logging_frame()

    assert frame is not None
    assert frame.f_code.co_name == "_visible_logging_frame"


def test_get_frame_without_hidden_predicate_walks_visible_depth() -> None:
    def inner() -> types.FrameType | None:
        return frame_module.get_frame()

    frame = inner()

    assert frame is not None
    assert frame.f_code.co_name == "inner"


def test_get_frame_with_stacklevel_counts_hidden_frames() -> None:
    frame, stacklevel = _visible_stacklevel_frame()

    assert frame is not None
    assert frame.f_code.co_name == "_visible_stacklevel_frame"
    assert stacklevel == 2


def test_get_frame_with_stacklevel_without_hidden_predicate() -> None:
    def inner() -> tuple[types.FrameType | None, int]:
        return frame_module.get_frame_with_stacklevel()

    frame, stacklevel = inner()

    assert frame is not None
    assert frame.f_code.co_name == "inner"
    assert stacklevel == 1


def test_hidden_from_logging_honors_configured_module_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        frame_module,
        "config",
        types.SimpleNamespace(hide_frame=Field([__name__])),
    )

    assert frame_module.hidden_from_logging(_current_frame()) is True


def test_hidden_from_warnings_honors_explicit_hide_marker() -> None:
    frame = _warnings_hidden_frame()

    assert frame_module.hidden_from_warnings(frame, hide_stable_release=False) is True


def test_hidden_from_warnings_hides_stable_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        return False

    monkeypatch.setattr(frame_module, "is_pre_release", is_pre_release)

    assert frame_module.hidden_from_warnings(_current_frame()) is True


def test_hidden_from_traceback_can_keep_stable_release_frames(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        msg = "release type should not be inspected when stable frames are visible"
        raise AssertionError(msg)

    monkeypatch.setattr(frame_module, "is_pre_release", is_pre_release)

    assert (
        frame_module.hidden_from_traceback(_current_frame(), hide_stable_release=False)
        is False
    )


def test_hidden_from_traceback_hides_stable_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        return False

    monkeypatch.setattr(frame_module, "is_pre_release", is_pre_release)

    assert frame_module.hidden_from_traceback(_current_frame()) is True


def test_hidden_from_traceback_keeps_pre_release_frames(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def is_pre_release(_file: object = None, _name: str | None = None) -> bool:
        return True

    monkeypatch.setattr(frame_module, "is_pre_release", is_pre_release)

    assert frame_module.hidden_from_traceback(_current_frame()) is False
