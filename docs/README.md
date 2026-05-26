# liblaf-logging

`liblaf-logging` is a compact logging setup for Python applications, scripts,
and notebooks. It combines Rich output, caller-aware helper logging, optional
Rich-formatted files, per-record rate limits, warning and exception capture, and
release-aware defaults.

## Quick Start

```python
import liblaf.logging

liblaf.logging.init(force=True)
liblaf.logging.info("ready")
```

`init()` configures process-wide logging. When it manages handlers itself, it
installs a Rich console handler, optionally adds a `FileHandler`, and attaches
`LimitsFilter` to the managed handlers. It also captures warnings, installs
hooks for uncaught and unraisable exceptions, registers the custom `TRACE` and
`ICECREAM` level names, and applies release-aware logger defaults.

## Caller-Aware Logging

Use the module-level helpers when shared code should log as its caller instead
of as the helper module.

```python
import liblaf.logging


def announce() -> None:
    liblaf.logging.info("starting")
```

Frames can opt out of attribution with `_logging_hide = True` or
`__tracebackhide__ = True`. The first visible frame supplies the logger name,
function name, and line number.

## Rate Limits

Add a `limits` value to a record with `extra` to suppress repeated messages at
the same call site.

```python
import liblaf.logging

liblaf.logging.warning(
    "still waiting",
    extra={"limits": "1/minute"},
)
```

Use `LimitOptions` when several call sites should share a bucket or when one
record should spend more than one hit.

```python
from liblaf.logging.filters import LimitOptions

liblaf.logging.warning(
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

Runtime settings use the `LOG_` environment prefix through `liblaf-conf`.

```bash
LOG_LEVEL=INFO LOG_FILE=logs/app.log python app.py
```

The configuration object controls the default root level, optional file path,
timestamp format, relative timestamp display, hidden-frame prefixes, and whether
stable installed code is hidden from Rich tracebacks and warning locations.

## API Reference

Start with [liblaf.logging](reference/liblaf/logging/README.md), then browse the
generated reference for [filters](reference/liblaf/logging/filters/README.md),
[handlers](reference/liblaf/logging/handlers/README.md), helper APIs, and frame
or release-type utilities.
