# DEC-004: Evidence model: five labels, computed on read, no attribution by timing

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-029, FR-030, FR-031, FR-043 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator |

## Context

The owner must see how strong the evidence about each file change is, without false blame (R5, R6, FU-6).

## Decision

Five labels: OBSERVED, GIT-VERIFIED, AGENT-REPORTED, UNATTRIBUTED, PRE-EXISTING, on two axes (Git, source).
Labels are computed from stored facts each time a page is viewed (rules R-A to R-F, architecture §5.3), never
stored as conclusions. A change is never attributed to an agent because of timing alone; shell commands never
produce OBSERVED.

## Alternatives considered

Storing attribution (becomes stale when a later report arrives); timing-based attribution (rejected by R6).

## Impact

Architecture §5. Tasks TASK-025 (badges), TASK-044, TASK-058; validated in TASK-085.

## Follow-up tasks

None.
