# liblaf-logging

`liblaf-logging` is a small, opinionated layer on top of Python's standard
`logging` package. It combines Rich output, caller-aware helper functions,
optional Rich-formatted file logs, per-record rate limits, warning and exception
capture, and release-aware logger defaults.

## Quick Start

```python
import liblaf.logging

liblaf.logging.init(force=True)
liblaf.logging.info("ready")
```

`init()` configures process-wide logging. By default it uses `INFO` as the root
level, installs Rich console output, registers the `TRACE` and `ICECREAM` level
names, captures warnings, installs hooks for uncaught and unraisable exceptions,
and applies release-aware logger defaults. If it creates handlers itself, it also
attaches a `LimitsFilter` to each managed handler.

## Caller-Aware Helpers

Use the module-level helpers when reusable code should log as the application
frame that called it.

```python
import liblaf.logging


def announce() -> None:
    liblaf.logging.info("starting")
```

Frames can opt out of attribution with `_logging_hide = True` or
`__tracebackhide__ = True`. The first visible frame supplies the logger name,
function name, and line number.

## Handlers

`RichHandler` renders compact columns before each message: time, level, and
`logger:function:line`. String messages are highlighted, Rich renderables pass
through unchanged, arbitrary objects are rendered with `Pretty`, and attached
exception information is shown as a Rich traceback.

During each emit, the handler scopes NumPy, Torch, and JAX print options to
compact summaries when those optional libraries are already imported. The
defaults are `precision=2`, `threshold=16`, `edgeitems=2`, and the current Rich
console width; the settings are restored immediately after rendering the record.

`FileHandler` uses the same rendering model for files. It creates parent
directories automatically and opens the file lazily by default, so configuring a
file destination does not touch the filesystem until the first emitted record.

## Rate Limits

Add a `limits` value through `extra` to suppress repeated records at the same
call site.

```python
import liblaf.logging

liblaf.logging.warning("still waiting", extra={"limits": "1/minute"})
```

Use `LimitOptions` when multiple records should share a bucket or when a record
should charge a custom cost.

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
level name, so nearby call sites keep independent buckets.

## Configuration

Runtime settings use the `LOG_` environment prefix through `liblaf-conf`.

```bash
LOG_LEVEL=DEBUG LOG_FILE=logs/app.log python app.py
```

The configuration object controls the default root level, optional file path,
timestamp format, relative timestamp display, hidden-frame prefixes, and whether
stable installed code is hidden from Rich tracebacks and warning locations.

## Release-Aware Defaults

`SanitizedLogger` can give development and prerelease distributions louder
defaults without making stable dependencies noisy. Files from `.devN`
distributions use the development level, files from prerelease distributions use
the prerelease level, and stable distributions keep the standard `NOTSET`
logger default.

The classifier expands metadata only for those selected distributions. Exact
files are matched directly, and `.pth` files from selected distributions add
source-tree prefixes for editable-style layouts. Stable distribution metadata is
not expanded, and installer-specific `direct_url.json` metadata is intentionally
ignored.

The `__main__` module is always classified as development and prerelease code so
directly executed scripts get verbose defaults while they are being run.

## API Reference

Start with [liblaf.logging](reference/liblaf/logging/README.md), then browse the
generated reference for [filters](reference/liblaf/logging/filters/README.md),
[handlers](reference/liblaf/logging/handlers/README.md), helper APIs, and frame
or release-type utilities.
