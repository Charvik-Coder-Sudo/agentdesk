# DEC-011: The database schema grows by phase

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-005, FR-012 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner preference stated earlier as OD-7; refinement R2 |

## Context

Creating every table up front would fix designs before each feature is understood.

## Decision

Each feature's tables arrive in that feature's numbered migration. Phase 1 creates only `schema_migrations` and
`app_settings`. Each later migration is finalized at its phase start; an applied migration file is never edited.

## Alternatives considered

One up-front schema (schema v0.1; replaced by refinement R2).

## Impact

Schema §2. Tasks TASK-006, TASK-037, TASK-040, TASK-043, TASK-053, TASK-067 to TASK-071; DDL finalized in
TASK-036, TASK-051, TASK-066.

## Follow-up tasks

None.
