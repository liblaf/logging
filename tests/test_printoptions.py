from __future__ import annotations

import types
from collections.abc import Callable
from typing import NamedTuple

import pytest

from liblaf.logging.helpers import _printoptions as printoptions_module


class Call(NamedTuple):
    event: str
    backend: str
    options: dict[str, object]


class RecorderContext:
    def __init__(
        self, calls: list[Call], backend: str, options: dict[str, object]
    ) -> None:
        self.calls = calls
        self.backend = backend
        self.options = dict(options)

    def __enter__(self) -> None:
        self.calls.append(Call("enter", self.backend, self.options))

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.calls.append(Call("exit", self.backend, {}))


def _recorder(calls: list[Call], backend: str) -> Callable[..., RecorderContext]:
    def printoptions(**kwargs: object) -> RecorderContext:
        return RecorderContext(calls, backend, kwargs)

    return printoptions


def _install_fake_backends(monkeypatch: pytest.MonkeyPatch, calls: list[Call]) -> None:
    torch = types.ModuleType("torch")
    vars(torch)["_tensor_str"] = types.SimpleNamespace(
        printoptions=_recorder(calls, "torch")
    )
    numpy = types.ModuleType("numpy")
    vars(numpy)["printoptions"] = _recorder(calls, "numpy")
    jax = types.ModuleType("jax")
    vars(jax)["__path__"] = []
    jax_numpy = types.ModuleType("jax.numpy")
    vars(jax_numpy)["printoptions"] = _recorder(calls, "jax")
    vars(jax)["numpy"] = jax_numpy

    monkeypatch.setitem(printoptions_module.sys.modules, "torch", torch)
    monkeypatch.setitem(printoptions_module.sys.modules, "numpy", numpy)
    monkeypatch.setitem(printoptions_module.sys.modules, "jax", jax)
    monkeypatch.setitem(printoptions_module.sys.modules, "jax.numpy", jax_numpy)


def test_printoptions_uses_rich_console_width_and_scopes_backends(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Call] = []
    _install_fake_backends(monkeypatch, calls)
    monkeypatch.setattr(
        printoptions_module.rich,
        "get_console",
        lambda: types.SimpleNamespace(width=37),
    )

    with printoptions_module.printoptions():
        assert calls == [
            Call(
                "enter",
                "torch",
                {"precision": 2, "threshold": 16, "edgeitems": 2, "linewidth": 37},
            ),
            Call(
                "enter",
                "numpy",
                {"precision": 2, "threshold": 16, "edgeitems": 2, "linewidth": 37},
            ),
            Call(
                "enter",
                "jax",
                {"precision": 2, "threshold": 16, "edgeitems": 2, "linewidth": 37},
            ),
        ]

    assert calls[-3:] == [
        Call("exit", "jax", {}),
        Call("exit", "numpy", {}),
        Call("exit", "torch", {}),
    ]


def test_printoptions_skips_console_lookup_when_linewidth_is_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Call] = []
    _install_fake_backends(monkeypatch, calls)
    monkeypatch.setattr(
        printoptions_module.rich,
        "get_console",
        lambda: pytest.fail("explicit linewidth should not read the console width"),
    )

    with printoptions_module.printoptions(linewidth=12):
        pass

    assert calls[0].options == {
        "linewidth": 12,
        "precision": 2,
        "threshold": 16,
        "edgeitems": 2,
    }


def test_printoptions_is_a_noop_for_absent_optional_backends(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(printoptions_module.sys.modules, "torch", raising=False)
    monkeypatch.delitem(printoptions_module.sys.modules, "numpy", raising=False)
    monkeypatch.delitem(printoptions_module.sys.modules, "jax", raising=False)

    with printoptions_module.printoptions(linewidth=10):
        pass
