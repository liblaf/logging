"""Rate-limit filtering for log records."""

import functools
import logging
import types
from collections.abc import Iterable, Sequence
from typing import Any

import attrs
import limits


@functools.singledispatch
def _parse_item(item: str | limits.RateLimitItem | None) -> limits.RateLimitItem | None:
    raise ValueError(item)


@_parse_item.register(types.NoneType)
def _(item: None) -> None:
    del item


@_parse_item.register(str)
def _(item: str) -> limits.RateLimitItem:
    return limits.parse(item)


@_parse_item.register(limits.RateLimitItem)
def _(item: limits.RateLimitItem) -> limits.RateLimitItem:
    return item


@attrs.frozen
class LimitOptions:
    """Options used by [`LimitsFilter`][liblaf.logging.filters.LimitsFilter].

    `item` may be a limit string, `limits.RateLimitItem`, or `None`. When
    `namespace` is omitted, the record pathname, line number, and level name are
    used; `identifiers` are appended to that namespace, and `cost` is charged to
    the limiter for each accepted record.

    Examples:
        >>> LimitOptions("2/minute", namespace=("worker",), identifiers=("sync",))
        LimitOptions(item=2 per 1 minute, namespace=('worker',), identifiers=('sync',), cost=1)
    """

    item: limits.RateLimitItem | None = attrs.field(converter=_parse_item)
    namespace: tuple[str, ...] | None = attrs.field(
        default=None, converter=attrs.converters.optional(tuple)
    )
    identifiers: tuple[str, ...] = attrs.field(default=(), converter=tuple)
    cost: int = 1

    def make_identifiers(self, record: logging.LogRecord) -> tuple[str, ...]:
        """Build the limiter identifiers for `record`.

        Examples:
            >>> record = logging.LogRecord(
            ...     "demo", logging.INFO, "app.py", 7, "msg", (), None
            ... )
            >>> LimitOptions("1/minute").make_identifiers(record)
            ('app.py', '7', 'INFO')
        """
        namespace: Iterable[str] = (
            self._default_namespace(record)
            if self.namespace is None
            else self.namespace
        )
        return (*namespace, *self.identifiers)

    @staticmethod
    def _default_namespace(record: logging.LogRecord) -> tuple[str, ...]:
        return record.pathname, str(record.lineno), record.levelname


@functools.singledispatch
def _parse_args(args: Any) -> LimitOptions:
    raise ValueError(args)


_parse_args_cache = functools.lru_cache(_parse_args)


@_parse_args.register(str)
@_parse_args.register(limits.RateLimitItem)
def _(args: str | limits.RateLimitItem) -> LimitOptions:
    return LimitOptions(item=args)


@_parse_args.register(LimitOptions)
def _(args: LimitOptions) -> LimitOptions:
    return args


@attrs.define
class LimitsFilter:
    """Suppress repeated records using the `limits` package.

    The filter is inactive unless the record has a `limits` attribute. The
    attribute may be a limit string, a `limits.RateLimitItem`, or a
    [`LimitOptions`][liblaf.logging.filters.LimitOptions] instance.

    Examples:
        >>> record = logging.LogRecord(
        ...     "demo", logging.INFO, "app.py", 7, "msg", (), None
        ... )
        >>> record.limits = "1/minute"
        >>> limiter = LimitsFilter()
        >>> limiter.filter(record)
        True
        >>> limiter.filter(record)
        False
    """

    @staticmethod
    def _default_limiter() -> limits.strategies.RateLimiter:
        return limits.strategies.FixedWindowRateLimiter(limits.storage.MemoryStorage())

    limiter: limits.strategies.RateLimiter = attrs.field(factory=_default_limiter)

    def filter(self, record: logging.LogRecord) -> bool:
        """Return whether `record` should be emitted."""
        args: Any = getattr(record, "limits", None)
        if args is None:
            return True
        opts: LimitOptions = _parse_args_cache(args)
        if opts.item is None:
            return True
        identifiers: Sequence[str] = opts.make_identifiers(record)
        return self.limiter.hit(opts.item, *identifiers, cost=opts.cost)
