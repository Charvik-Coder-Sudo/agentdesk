# DEC-001: Stack: FastAPI, SQLite with plain SQL, vanilla JavaScript

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-001, CON-004, CON-007 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (SRS source OA), relayed verbatim by the orchestrator |

## Context

The owner brief (§2) and refinement R1 ask for a lightweight local tool with few dependencies and no build step.

## Decision

Python with FastAPI for the REST API; SQLite through Python's `sqlite3` with plain SQL (no ORM); one static HTML
page with CSS and vanilla JavaScript ES modules, without a build step.

## Alternatives considered

An ORM such as SQLAlchemy (extra dependency and abstraction); a frontend framework with a build step (more tools
and packages); server-side templates such as Jinja2 (a dependency for a single static page).

## Impact

Architecture §4, §13, §14. Dependency files are checked by every security task. No document change needed.

## Follow-up tasks

None beyond TASK-003 and the developer tasks of each phase.
