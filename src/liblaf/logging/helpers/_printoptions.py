"""Scoped print settings for optional array and tensor libraries."""

import contextlib
import sys
from collections.abc import Generator
from typing import TypedDict, Unpack

import rich
from rich.console import Console


class PrintOptions(TypedDict, total=False):
    """Print settings shared by supported scientific libraries.

    Attributes:
        precision: Number of digits rendered after the decimal point.
        threshold: Total item count before summarizing large arrays or tensors.
        edgeitems: Number of leading and trailing items shown in summarized
            dimensions.
        linewidth: Target output width. When omitted,
            [`printoptions`][liblaf.logging.helpers.printoptions] uses the
            current Rich console width.
    """

    precision: int | None
    threshold: int | None
    edgeitems: int | None
    linewidth: int | None


@contextlib.contextmanager
def printoptions(**kwargs: Unpack[PrintOptions]) -> Generator[None]:
    """Temporarily compact optional array and tensor rendering.

    The context manager applies the same print options to NumPy, Torch, and JAX
    only when those packages are already imported. It does not import optional
    dependencies by itself, so normal logging remains lightweight for projects
    that do not use them.

    Args:
        **kwargs: Overrides for `precision`, `threshold`, `edgeitems`, and
            `linewidth`. Defaults are `precision=2`, `threshold=16`,
            `edgeitems=2`, and the current Rich console width.

    Examples:
        >>> from liblaf.logging.helpers import printoptions
        >>> with printoptions(linewidth=40):
        ...     pass
    """
    kwargs.setdefault("precision", 2)
    kwargs.setdefault("threshold", 16)
    kwargs.setdefault("edgeitems", 2)
    if "linewidth" not in kwargs:
        console: Console = rich.get_console()
        kwargs["linewidth"] = console.width
    with contextlib.ExitStack() as stack:
        stack.enter_context(_torch_printoptions(**kwargs))
        stack.enter_context(_numpy_printoptions(**kwargs))
        stack.enter_context(_jax_printoptions(**kwargs))
        yield


def _torch_printoptions(
    **kwargs: Unpack[PrintOptions],
) -> contextlib.AbstractContextManager:
    if "torch" not in sys.modules:
        return contextlib.nullcontext()
    from torch import _tensor_str

    return _tensor_str.printoptions(**kwargs)


def _numpy_printoptions(
    **kwargs: Unpack[PrintOptions],
) -> contextlib.AbstractContextManager:
    if "numpy" not in sys.modules:
        return contextlib.nullcontext()
    import numpy as np

    return np.printoptions(**kwargs)


def _jax_printoptions(
    **kwargs: Unpack[PrintOptions],
) -> contextlib.AbstractContextManager:
    if "jax" not in sys.modules:
        return contextlib.nullcontext()
    import jax.numpy as jnp

    return jnp.printoptions(**kwargs)
