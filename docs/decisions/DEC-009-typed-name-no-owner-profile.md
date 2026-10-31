# DEC-009: Decisions record a typed name; no owner profile

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-008, FR-040, FR-057, FR-059 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner preference stated earlier as OD-5; review finding E3 |

## Context

Approvals need a named person, but a stored profile or the Windows account name adds personal data for no benefit.

## Decision

Approvals, reviews and wizard confirmations record the name the owner types each time. AgentDesk stores no owner
profile and never reads the Windows account name. The browser may remember the last typed name in its own local
storage.

## Alternatives considered

An owner-name setting in the database (removed in schema v0.3); the Windows account name (not chosen by the owner).

## Impact

Schema §3 and `approvals.decided_by`; architecture §7 step 4, §11. Tasks TASK-012, TASK-057, TASK-071, TASK-072.

## Follow-up tasks

None.
