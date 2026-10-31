# DEC-014: GUI verification by the owner's manual browser checklist

| Field | Value |
|---|---|
| Type | Design decision (development process) |
| Status | Approved; amended by DEC-020 (one consolidated checklist, at final acceptance) |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-014 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner choice OD-2 |

## Context

Visual and keyboard behaviour cannot be fully checked by HTTP tests, and the owner does not want a browser
extension or browser automation.

## Decision

The owner checks the GUI with a manual browser checklist; no Chrome extension or other browser automation is
used. Amendment (DEC-020): automated HTTP/API and static-file tests check GUI behaviour in every phase, and the
owner runs one consolidated checklist (implementation plan Appendices A and B) at final acceptance.

## Alternatives considered

Browser automation or a Chrome extension (rejected by the owner, OD-2).

## Impact

Implementation plan §1.3, §1.5, Appendices A and B. Tasks TASK-089, TASK-092.

## Follow-up tasks

None.
