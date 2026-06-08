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

- **Caller-aware helpers**: `liblaf.logging.info()` and friends attribute shared helper logs to the first visible caller frame.
- **Rich console and file output**: Handlers render compact time, level, location, highlighted messages, Rich renderables, pretty objects, and tracebacks.
- **Scoped array and tensor summaries**: NumPy, Torch, and JAX output is compacted while records are rendered when those libraries are already imported.
- **Per-record rate limits**: Add `extra={"limits": "1/minute"}` or a `LimitOptions` object to suppress noisy repeat logs.
- **Process hooks**: `init()` captures warnings, uncaught exceptions, and unraisable exceptions through the standard logging pipeline.
- **Release-aware defaults**: Development and prerelease distributions can get louder logger defaults while stable installed modules stay at `NOTSET`.

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

`init()` configures the root logger at `INFO` by default, installs Rich output,
registers `TRACE` and `ICECREAM` level names, captures warnings, and adds
exception hooks. When it creates handlers itself, each managed handler receives
a `LimitsFilter`. While a record is rendered, NumPy, Torch, and JAX print
options are scoped to compact summaries if those libraries are already loaded.

Use the module-level helpers when library or framework glue should log as the
application code that called it.

```python
import liblaf.logging


def announce() -> None:
    liblaf.logging.info("starting")
```

## 🚦 Rate Limits

Attach a `limits` value to an individual record.

```python
import liblaf.logging

liblaf.logging.warning("still waiting", extra={"limits": "1/minute"})
```

For shared buckets, custom identifiers, or non-default costs, pass
`LimitOptions`.

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

Settings use the `LOG_` environment prefix through
[`liblaf-conf`](https://github.com/liblaf/conf). The most common options are
`LOG_LEVEL`, `LOG_FILE`, `LOG_TIME_RELATIVE`, `LOG_HIDE_FRAME`, and
`LOG_HIDE_STABLE_RELEASE`.

```bash
LOG_LEVEL=DEBUG LOG_FILE=logs/app.log python app.py
```

## 🧭 Release-Aware Defaults

`SanitizedLogger` checks module files against selected installed distributions
when a logger is created without an explicit level. `.devN` distributions use
the development level, prerelease distributions use the prerelease level, and
stable distributions keep the normal `NOTSET` logger default.

The classifier expands metadata only for those selected distributions. Exact
files are matched directly, and `.pth` files from selected distributions add
source-tree prefixes for editable-style layouts. Stable distribution metadata is
not expanded, and `direct_url.json` is not followed.

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
