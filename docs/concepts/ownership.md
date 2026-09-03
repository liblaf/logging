# Ownership boundaries

`liblaf.logging` owns only the hooks it installs during `init()`. It restores a
hook only when that exact hook is still active, so another library can replace a
hook after initialization without being overwritten by `restore()`.

Handlers follow the same boundary. Package-created handlers receive the shared
formatters and rate-limit filter. Explicit `handlers=` are application-owned:
they are passed to `logging.basicConfig()` unchanged and receive no implicit
filters. Progress state is likewise owned by optional `liblaf.progress`; this
package only renders the structured records it emits.
