# DEC-007: Shell commands stored redacted, at most 200 characters

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | NFR-014, FR-052 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner preference stated earlier as OD-3 |

## Context

Shell commands show which tests ran, but may contain secrets.

## Decision

Shell commands are stored only after secret redaction and truncated to 200 characters.

## Alternatives considered

Not storing commands (loses observed test-run evidence, FR-052); storing them in full (secret exposure).

## Impact

Architecture §6.3. Tasks TASK-052, TASK-053, TASK-068.

## Follow-up tasks

None.
