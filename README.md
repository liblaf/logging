<div align="center" markdown>

![liblaf-logging](https://socialify.git.ci/liblaf/logging/image?description=1&forks=1&issues=1&language=1&name=1&owner=1&pattern=Transparent&pulls=1&stargazers=1&theme=Auto)

**[Explore the docs »](https://liblaf.github.io/logging/)**

[![PyPI - Version](https://img.shields.io/pypi/v/liblaf-logging?logo=PyPI)](https://pypi.org/project/liblaf-logging/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/liblaf-logging?logo=Python)](https://pypi.org/project/liblaf-logging/)
[![PyPI - Types](https://img.shields.io/pypi/types/liblaf-logging?logo=PyPI)](https://pypi.org/project/liblaf-logging/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/liblaf-logging?logo=PyPI)](https://pypi.org/project/liblaf-logging/)
[![Test](https://github.com/liblaf/logging/actions/workflows/python-test.yaml/badge.svg)](https://github.com/liblaf/logging/actions/workflows/python-test.yaml)
[![Docs](https://github.com/liblaf/logging/actions/workflows/python-docs.yaml/badge.svg)](https://github.com/liblaf/logging/actions/workflows/python-docs.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

[Documentation](https://liblaf.github.io/logging/) · [Source](https://github.com/liblaf/logging) · [Issues](https://github.com/liblaf/logging/issues) · [Releases](https://github.com/liblaf/logging/releases)

![Rule](https://cdn.jsdelivr.net/gh/andreasbm/readme/assets/lines/rainbow.png)

</div>

## ✨ Features

- **Caller-aware helpers**: Module-level helpers resolve the first visible caller so log records keep useful logger names, functions, and line numbers.
- **Rich output everywhere**: Console and file handlers share Rich rendering, compact columns, highlighted messages, and Rich tracebacks.
- **Per-record rate limits**: Add `extra={"limits": "1/minute"}` or `LimitOptions` to suppress noisy repeated records.
- **Process hooks**: `init()` captures warnings and installs hooks for uncaught and unraisable exceptions.
- **Release-aware defaults**: Development and prerelease code can log more verbosely while stable installed packages stay quiet.

## 📦 Installation

```bash
uv add liblaf-logging
```

## 🚀 Quick Start

```python
import liblaf.logging

liblaf.logging.init(force=True)
liblaf.logging.info("ready")
```

`init()` configures process-wide logging. When it manages handlers itself, it
creates a Rich console handler, optionally creates a Rich-formatted file handler,
and attaches `LimitsFilter` to those managed handlers.

Use the module-level helpers when shared helpers should log as their caller.

```python
import liblaf.logging


def announce() -> None:
    liblaf.logging.info("starting")
```

## 🚦 Rate-Limited Records

```python
import liblaf.logging

liblaf.logging.warning(
    "still waiting",
    extra={"limits": "1/minute"},
)
```

For shared buckets or custom costs, pass `LimitOptions`.

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

## ⚙️ Configuration

Runtime settings are backed by `liblaf-conf` and the `LOG_` environment prefix.

```bash
LOG_LEVEL=INFO LOG_FILE=logs/app.log python app.py
```

Settings control the default level, optional file path, timestamp format,
relative timestamp display, hidden-frame prefixes, and release-aware traceback or
warning filtering.

## ⌨️ Local Development

```bash
git clone https://github.com/liblaf/logging.git
cd logging
uv sync
uv run pytest
mise run docs:build
```

#### 📝 License

Copyright © 2026 [liblaf](https://github.com/liblaf). <br />
This project is [MIT](https://github.com/liblaf/logging/blob/main/LICENSE) licensed.
