# liblaf-logging

`liblaf-logging` is a small logging layer for Python applications and
notebooks. It configures Rich output, optional Rich-formatted log files,
rate-limited records, caller-aware logging proxies, and release-aware default
levels for development and prerelease modules.

## Install

```bash
uv add liblaf-logging
```

## Quick Start

```python
import liblaf.logging

liblaf.logging.init(force=True)

log = liblaf.logging.autolog
log.info("started")
log.warning("retrying noisy operation", extra={"limits": "1/minute"})
```

`autolog` resolves the logger from the calling module, so library code can log
without passing `logging.getLogger(__name__)` through every helper. `init()`
installs Rich console output, exception and unraisable-exception hooks, Python
warning capture, rate-limit filtering, and the package's release-aware logger
class.

## Useful Pieces

- `liblaf.logging.init()` configures the root logging setup.
- `liblaf.logging.autolog` delegates common logging methods to the caller's
  logger and preserves caller locations with `stacklevel`.
- `liblaf.logging.filters.LimitsFilter` suppresses repeated records when a log
  record carries `extra={"limits": "1/minute"}` or a `LimitOptions` object.
- `liblaf.logging.handlers.RichHandler` renders records with Rich columns.
- `liblaf.logging.handlers.FileHandler` writes the same Rich rendering to a
  lazily opened file.

## Configuration

Runtime settings are backed by `liblaf-conf` and use the `LOG_` environment
prefix. The current options control timestamp formatting, default frame-hiding
prefixes, stable-release traceback hiding, default log level text, and relative
time display.

See the documentation site for API details and generated reference pages.
