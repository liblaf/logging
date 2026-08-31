"""Optional compatibility facade for the peer `liblaf.progress` package."""

from __future__ import annotations

import importlib
from typing import Any


def _peer() -> Any:
    try:
        return importlib.import_module("liblaf.progress")
    except ModuleNotFoundError as error:
        if error.name == "liblaf.progress":
            message = "install liblaf-progress to use liblaf.logging.progress"
            raise ModuleNotFoundError(message) from error
        raise


def get_progress(*args: Any, **kwargs: Any) -> Any:
    return _peer().get_progress(*args, **kwargs)


def __getattr__(name: str) -> Any:
    if name in {"Progress", "SpeedColumn"}:
        return getattr(_peer(), name)
    raise AttributeError(name)


__all__ = ["get_progress"]
