# liblaf-logging

`liblaf-logging` wraps the standard `logging` package with the defaults this
project family expects: Rich console output, optional Rich-formatted log files,
caller-aware logging helpers, warning and exception capture, and per-record rate
limits.

## Start Logging

```python
import liblaf.logging

liblaf.logging.init(force=True)
liblaf.logging.autolog.info("ready")
```

Calling `init()` installs a Rich handler on the root logger when one is needed,
adds `LimitsFilter` to managed handlers, captures Python warnings, installs
exception hooks, and switches new loggers to the package `Logger` class. The
custom logger keeps records propagating to the root handler and gives
development or prerelease modules lower default thresholds.

## Caller-Aware Logging

`autolog` behaves like a logger for common methods such as `info`, `warning`,
`error`, and `exception`, but it resolves the real logger name from the visible
caller frame. Hidden helper frames can opt out with `_logging_hide = True` or
`__tracebackhide__ = True`, so wrapper functions can keep record names and line
numbers useful.

## Rate-Limited Records

Attach a limit to a record with `extra`.

```python
liblaf.logging.autolog.warning(
    "still waiting",
    extra={"limits": "1/minute"},
)
```

`LimitsFilter` parses strings and `limits.RateLimitItem` values with the
`limits` package. By default, the record pathname, line number, and level form
the namespace, so nearby log sites are limited independently.

## Handlers

`RichHandler` renders a time column, abbreviated level column, caller location,
message, and optional Rich traceback. `FileHandler` reuses the same rendering for
files and opens the target lazily, creating parent directories on first emit.

The generated API reference starts at `reference/liblaf/logging/README.md`.
