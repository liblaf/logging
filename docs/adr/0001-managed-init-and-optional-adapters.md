# Managed initialization and optional adapters

`init()` owns at most one root stderr handler, records equivalent setup, and
rejects incompatible repeated setup unless `force=True`. Exception and object
formatters are resolved once, preferring optional liblaf siblings and falling
back to stdlib/Rich. `restore()` only restores hooks it still owns.
