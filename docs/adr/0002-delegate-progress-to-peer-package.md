# Delegate progress ownership to `liblaf.progress`

`liblaf.logging` accepts structured progress records and offers a lazy
compatibility facade, but the task state machine belongs to the optional
`liblaf.progress` package. Keeping one progress owner avoids two implementations
drifting while preserving a convenient integration path. Applications that do
not install `liblaf-progress` retain the complete logging API except for the
explicit progress facade.
