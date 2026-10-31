# DEC-018: Dependency files: top-level pins, runtime lock file, development file

| Field | Value |
|---|---|
| Type | Design decision (includes a clarification of CON-004) |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (decided by the orchestrator and relayed in this delegation) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-004, FR-001, A-8; closes SRS question Q10 (OD-14) |
| Approved by and when | The orchestrator, 2026-10-30, under the owner's delegated authority (OA: "Resolve minor ambiguities using the simplest maintainable solution consistent with the approved architecture. Record significant decisions in the documentation.") |

## Context

Q10 asked how the fixed package versions are written down and kept reproducible.

## Decision

Option B. `requirements.txt` pins the top-level runtime packages (`fastapi==0.162.0`, `uvicorn==0.54.0`).
`requirements.lock.txt` holds the exact runtime versions from `pip freeze` in a fresh `.venv`, and
`scripts\setup.bat` installs from it. `requirements-dev.txt` adds `pytest==9.2.0` and `httpx==0.28.1`.
Upkeep: regenerate the lock file only when a dependency changes (fresh `.venv`, install `requirements.txt`,
`pip freeze`, run the full suite). Limitation: sub-dependencies of the development packages are not locked; they
never ship with AgentDesk.

| CON-004 | Text |
|---|---|
| Old | "... Any new dependency needs the owner's approval. The dependency file format is decided by the owner (Q10) before anything is installed." Acceptance: "Dependency files list only `fastapi==0.162.0`, `uvicorn==0.54.0` and, for development, `pytest==9.2.0`, `httpx==0.28.1`; Q10 is answered before TASK-003 starts." |
| New | "... Any new direct dependency needs the owner's approval. Dependency files follow DEC-018: ..." Acceptance: the two top-level files list exactly the four pins; a fresh `.venv` installed from the lock file reproduces it exactly under `pip freeze`; the lock adds no package that fastapi or uvicorn does not require; `setup.bat` installs from the lock file. |

## Alternatives considered

A: `requirements.txt` with top-level pins only (sub-dependencies float, less reproducible). C: pip-tools, hashes
or `pyproject.toml` (another tool or more upkeep).

## Impact

SRS CON-004, A-8, Q10; architecture §13, §14; plan §1.5, §3 status note. Tasks TASK-003, TASK-013; every SEC task
checks the dependency files.

## Follow-up tasks

None.
