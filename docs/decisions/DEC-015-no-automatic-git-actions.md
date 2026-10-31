# DEC-015: No automatic Git actions; the owner commits

| Field | Value |
|---|---|
| Type | Design decision (development process and product) |
| Status | Approved; test-fixture scope clarified by DEC-023 |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-008, FR-024 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner choice OD-12 |

## Context

The owner wants full control over what enters the project history.

## Decision

Neither AgentDesk nor any agent stages, commits, pushes, deploys or discards changes. The owner decides when to
commit. AgentDesk's Git runner allows read-only subcommands only. Clarification (DEC-023): test fixtures may
create commits only in throwaway repositories under the Git-ignored `.pytest_tmp/` and `.sandbox/` folders.

## Alternatives considered

Automatic commits per phase (rejected by the owner).

## Impact

Implementation plan §1.5; architecture §3.2. Tasks TASK-039 (allowlist), TASK-090 (final Git check).

## Follow-up tasks

None.
