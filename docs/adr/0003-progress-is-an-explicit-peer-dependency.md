---
status: accepted
supersedes: ADR-0002
---

# Make progress an explicit peer dependency

Applications import `liblaf.progress` directly to create and manage progress; `liblaf.logging` only renders its structured progress records. This removes a second, compatibility-shaped public route while preserving the integration and making task-state ownership and installation requirements explicit.
