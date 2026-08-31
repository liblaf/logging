"""Icecream-style structured debug events."""

from __future__ import annotations

import ast
import os
import textwrap
import types
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import executing
from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from ._adapters import ObjectFormatter

ICECREAM = 25
ICON = "🍦"


@dataclass(frozen=True, slots=True)
class DebugEvent:
    """Values plus best-effort source expressions for one `ic()` call.

    Examples:
        >>> str(DebugEvent((("answer", 42),), prefix="debug"))
        'debug answer: 42'
    """

    pairs: tuple[tuple[str | None, Any], ...]
    context: str | None = None
    prefix: str = ICON

    def __str__(self) -> str:
        if self.context is not None:
            return f"{self.prefix} {self.context}"
        values = ", ".join(
            repr(value) if name is None else f"{name}: {value!r}"
            for name, value in self.pairs
        )
        return f"{self.prefix} {values}".rstrip()

    def render(self, formatter: ObjectFormatter) -> RenderableType:
        """Render values with the handler's once-resolved object adapter."""
        if self.context is not None:
            return Text(f"{self.prefix} {self.context}")
        rows = Table.grid(padding=(0, 0))
        rows.add_column(no_wrap=True)
        rows.add_column(no_wrap=True)
        rows.add_column(overflow="fold")
        for index, (name, value) in enumerate(self.pairs):
            rows.add_row(
                Text(f"{self.prefix} " if index == 0 else " " * (len(self.prefix) + 1)),
                Text("" if name is None else f"{name}: ", style="repr.attrib_name"),
                formatter(value),
            )
        return Group(rows)


def build_debug_event(
    values: Sequence[Any], frame: types.FrameType | None, *, prefix: str = ICON
) -> DebugEvent:
    """Capture a diagnostic event without making source recovery mandatory."""
    if not values:
        return DebugEvent((), context=_context(frame), prefix=prefix)
    return DebugEvent(
        tuple(zip(_argument_names(frame, len(values)), values, strict=False)),
        prefix=prefix,
    )


def _argument_names(frame: types.FrameType | None, count: int) -> list[str | None]:
    if frame is None:
        return [None] * count
    try:
        execution = executing.Source.executing(frame)
        node = execution.node
        if not isinstance(node, ast.Call) or len(node.args) != count:
            return [None] * count
        tokens = executing.Source.for_frame(frame).asttokens()
        result: list[str | None] = []
        for argument in node.args:
            source = tokens.get_text(argument).strip()
            if "\n" in source:
                source = textwrap.dedent(source)
            result.append(None if _is_literal(source) else source)
    except Exception:  # noqa: BLE001
        return [None] * count
    else:
        return result


def _context(frame: types.FrameType | None) -> str | None:
    if frame is None:
        return None
    filename = os.path.relpath(frame.f_code.co_filename)
    name = frame.f_code.co_name
    if name != "<module>":
        name += "()"
    return f"{filename}:{frame.f_lineno} in {name}"


def _is_literal(source: str) -> bool:
    try:
        ast.literal_eval(source)
    except Exception:  # noqa: BLE001
        return False
    return True
