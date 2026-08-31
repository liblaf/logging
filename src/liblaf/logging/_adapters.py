"""Optional presentation adapters resolved once at logging setup time."""

from __future__ import annotations

import importlib
import traceback as stdlib_traceback
import types
from collections.abc import Callable
from typing import Any

from rich.console import RenderableType
from rich.pretty import Pretty
from rich.text import Text

ExceptionFormatter = Callable[
    [type[BaseException], BaseException, types.TracebackType | None], RenderableType
]
ObjectFormatter = Callable[[Any], RenderableType]


def default_exception_formatter() -> ExceptionFormatter:
    """Resolve the traceback adapter once, preferring the optional sibling."""
    try:
        module = importlib.import_module("liblaf.traceback")
    except ModuleNotFoundError as error:
        if error.name != "liblaf.traceback":
            raise
    else:
        render = module.render_exception

        def format_with_liblaf(
            _exc_type: type[BaseException],
            exc: BaseException,
            tb: types.TracebackType | None,
        ) -> RenderableType:
            return render(exc, traceback=tb)

        return format_with_liblaf

    def format_exception(
        exc_type: type[BaseException],
        exc: BaseException,
        tb: types.TracebackType | None,
    ) -> Text:
        return Text("".join(stdlib_traceback.format_exception(exc_type, exc, tb)))

    return format_exception


def default_object_formatter() -> ObjectFormatter:
    """Resolve the object adapter once, preferring the optional sibling."""
    try:
        return importlib.import_module("liblaf.pprint").render
    except ModuleNotFoundError as error:
        if error.name != "liblaf.pprint":
            raise
    return lambda value: Pretty(
        value, indent_guides=True, max_length=6, max_string=30, max_depth=6
    )
