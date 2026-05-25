from __future__ import annotations

from liblaf.logging.helpers import LazyRepr, LazyStr


def test_lazy_str_evaluates_once_on_first_string_conversion() -> None:
    calls: list[str] = []

    def build(value: str) -> str:
        calls.append(value)
        return f"{value}:{len(calls)}"

    text = LazyStr(build, "message")

    assert str(text) == "message:1"
    assert str(text) == "message:1"
    assert calls == ["message"]


def test_lazy_repr_evaluates_once_on_first_repr_conversion() -> None:
    calls: list[str] = []

    def build(value: str) -> str:
        calls.append(value)
        return f"{value}:{len(calls)}"

    text = LazyRepr(build, "message")

    assert repr(text) == "message:1"
    assert repr(text) == "message:1"
    assert calls == ["message"]
