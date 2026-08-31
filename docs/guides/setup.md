# Application setup

Call `init()` once from the application entry point. An identical later call is
a no-op; a different call raises `RuntimeError` unless it uses `force=True`.

```python
import liblaf.logging

liblaf.logging.init(file="logs/app.log")
liblaf.logging.info("service ready")
```

With package-created handlers, output goes to stderr and, when `file` is set,
to a lazily opened file. Supply `handlers=` when the application owns handler
construction. `restore()` removes only warning, exception, unraisable, and
display hooks still owned by the most recent initialization; it intentionally
does not remove root handlers.

`liblaf.traceback` and `liblaf.pprint` are optional presentation adapters. They
are resolved once during setup when installed, otherwise Rich and the standard
library provide the fallback presentation.
