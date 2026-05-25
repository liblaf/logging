"""Lazy string and repr wrappers."""

import functools
from collections.abc import Callable


class LazyRepr[**P]:
    """Compute `repr()` text only once.

    Args:
        func: Callable that builds the representation text.
        *args: Positional arguments passed to `func`.
        **kwargs: Keyword arguments passed to `func`.

    Examples:
        >>> calls = []
        >>> text = LazyRepr(lambda value: calls.append(value) or value.upper(), "demo")
        >>> repr(text)
        'DEMO'
        >>> repr(text)
        'DEMO'
        >>> calls
        ['demo']
    """

    func: Callable[P, str]

    def __init__(
        self, func: Callable[P, str], /, *args: P.args, **kwargs: P.kwargs
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return self.__wrapped__

    @functools.cached_property
    def __wrapped__(self) -> str:
        return self.func(*self.args, **self.kwargs)


class LazyStr[**P]:
    """Compute `str()` text only once.

    Args:
        func: Callable that builds the string text.
        *args: Positional arguments passed to `func`.
        **kwargs: Keyword arguments passed to `func`.

    Examples:
        >>> calls = []
        >>> text = LazyStr(lambda value: calls.append(value) or value.upper(), "demo")
        >>> str(text)
        'DEMO'
        >>> str(text)
        'DEMO'
        >>> calls
        ['demo']
    """

    func: Callable[P, str]

    def __init__(
        self, func: Callable[P, str], /, *args: P.args, **kwargs: P.kwargs
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return self.__wrapped__

    @functools.cached_property
    def __wrapped__(self) -> str:
        return self.func(*self.args, **self.kwargs)
