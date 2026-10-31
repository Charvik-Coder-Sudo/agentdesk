# DEC-005: Diffs and reports are read live; the database stores facts only

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-028, FR-032, FR-049, NFR-013 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator |

## Context

Stored file contents could hold secrets and would grow without limit (brief §7).

## Decision

Diffs, full reports and documents are read live from the project when viewed. The database keeps facts,
content fingerprints and short redacted summaries only.

## Alternatives considered

Storing snapshots of changed files or full report texts (secret exposure, size, a second copy to protect).

## Impact

Architecture §2 P8, §8. Tasks TASK-042, TASK-043, TASK-067. Known limitation: diffs are cumulative
(architecture §15 item 4).

## Follow-up tasks

None.
