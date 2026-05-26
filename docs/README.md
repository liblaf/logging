# liblaf-logging

`liblaf-logging` gives Python applications and notebooks a compact logging
setup built around Rich output, caller-aware helpers, warning and exception
capture, optional file output, and per-record rate limits.

## Start Logging

```python
import liblaf.logging

liblaf.logging.init(force=True)
liblaf.logging.autolog.info("ready")
```

`init()` installs the process defaults. Managed handlers use Rich rendering and
receive `LimitsFilter`; explicitly supplied handlers are passed through to
`logging.basicConfig` unchanged. The initializer also captures Python warnings,
installs hooks for uncaught and unraisable exceptions, registers the custom
`TRACE` and `ICECREAM` level names, and applies release-aware logger defaults.

## Caller-Aware Helpers

`autolog` behaves like a logger for common methods such as `info`, `warning`,
`error`, and `exception`, but it resolves the logger name from the first visible
caller frame. Helper wrappers can hide themselves with `_logging_hide = True` or
`__tracebackhide__ = True`, keeping record names and line numbers pointed at the
code that actually asked to log.

## Rate Limits

Attach a limit to a record with `extra`.

```python
liblaf.logging.autolog.warning(
    "still waiting",
    extra={"limits": "1/minute"},
)
```

Use `LimitOptions` when several call sites should share a bucket or when one
record should charge more than one hit.

```python
from liblaf.logging.filters import LimitOptions

liblaf.logging.autolog.warning(
    "sync retry",
    extra={
        "limits": LimitOptions(
            "5/minute",
            namespace=("sync",),
            identifiers=("account-42",),
            cost=1,
        )
    },
)
```

## Handlers

`RichHandler` renders a timestamp, abbreviated level, caller location, message,
and optional Rich traceback. `FileHandler` uses the same rendering for files and
opens the target lazily by default, creating parent directories on first emit.

The generated API reference starts at `reference/liblaf/logging/README.md`.
