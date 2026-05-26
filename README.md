# liblaf-logging

`liblaf-logging` is a compact, opinionated layer over Python's standard
`logging` package. It installs Rich console output, optional Rich-formatted log
files, caller-aware helper logging, warning and exception hooks, per-record rate
limits, and release-aware defaults for development and prerelease code.

## Install

```bash
uv add liblaf-logging
```

## Quick Start

```python
import liblaf.logging

liblaf.logging.init(force=True)
liblaf.logging.autolog.info("ready")
```

`init()` configures process-wide logging. When it manages handlers itself, it
creates a Rich console handler, optionally creates a Rich file handler, and
adds `LimitsFilter` to those managed handlers. It also captures Python warnings,
installs hooks for uncaught and unraisable exceptions, registers the `TRACE` and
`ICECREAM` level names, and switches future loggers to the package `Logger`
class.

Use `autolog` when helper functions should log as their caller. It resolves the
first visible caller frame, so wrappers do not need to pass
`logging.getLogger(__name__)` through every layer.

## Rate-Limited Records

Attach a limit to a record with `extra`.

```python
liblaf.logging.autolog.warning(
    "still waiting",
    extra={"limits": "1/minute"},
)
```

For shared buckets or custom costs, pass `LimitOptions`.

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

Without an explicit namespace, records are limited by pathname, line number, and
level name, so nearby log sites keep independent buckets.

## Configuration

Runtime settings are backed by `liblaf-conf` and the `LOG_` environment prefix.
They control the default level, optional log file path, timestamp format,
relative timestamp display, frame-hiding prefixes, and whether stable installed
code is hidden from Rich tracebacks and warning locations.

Generated API documentation is available at <https://liblaf.github.io/logging/>.
