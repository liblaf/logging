# liblaf-logging

`liblaf-logging` is an opinionated layer over Python's standard `logging`
package. It installs Rich console output, optional Rich-formatted log files,
caller-aware logger proxies, warning and exception hooks, per-record rate
limits, and release-aware default levels for development or prerelease modules.

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

`init()` configures the process once. When the root logger needs handlers, it
creates a Rich console handler, optionally creates a file handler, and attaches
`LimitsFilter` to those managed handlers. It also captures Python warnings,
installs exception hooks, registers custom level names, and switches newly
created loggers to the package `Logger` class.

`autolog` resolves the logger from the visible caller frame, so helper functions
can log as their caller without threading `logging.getLogger(__name__)` through
every call.

## Rate-Limited Records

Attach a limit with `extra`.

```python
liblaf.logging.autolog.warning(
    "still waiting",
    extra={"limits": "1/minute"},
)
```

For shared buckets or custom costs, use `LimitOptions`.

```python
from liblaf.logging.filters import LimitOptions

liblaf.logging.autolog.warning(
    "sync retry",
    extra={
        "limits": LimitOptions(
            "5/minute",
            namespace=("sync",),
            identifiers=("account-42",),
        )
    },
)
```

Without an explicit namespace, the filter keys records by pathname, line number,
and level name, so nearby log sites are limited independently.

## Configuration

Runtime configuration is backed by `liblaf-conf` with the `LOG_` environment
prefix. The current settings control the default level, optional log file path,
timestamp format, relative timestamp display, frame-hiding prefixes, and whether
stable-release frames are hidden from Rich tracebacks and warning locations.

Generated API documentation is available at <https://liblaf.github.io/logging/>.
