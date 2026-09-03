# Logging

This context describes application-owned routing of diagnostic events to
human-readable destinations.

## Language

**Managed handler**:
A root logging destination created and configured by this library.
_Avoid_: Global handler, default logger

**Presentation adapter**:
An interchangeable callable that turns an exception or Python value into a
human-readable presentation.
_Avoid_: Formatter dependency, renderer backend

**Owned hook**:
A process hook installed by this library and still bound to the exact callable
it installed.
_Avoid_: Global hook, captured hook

**Progress record**:
A log record carrying a renderable presentation emitted by `liblaf.progress`.
_Avoid_: Progress bar, logging-owned task
