# DEC-019: "Changes requested" keeps the release blocker; 2-second test-runner file tolerance

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (decided by the orchestrator and relayed in this delegation) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-054, FR-059, FR-060; assumptions A-6, A-7; closes SRS questions Q12 and Q13 |
| Approved by and when | The orchestrator, 2026-10-30, under the owner's delegated authority (OA: "Resolve minor ambiguities using the simplest maintainable solution consistent with the approved architecture.") |

## Context

Q12 and Q13 were left open for the start of Phase 5.

## Decision

- **Q12:** a file-change review marked "changes requested" keeps the release-readiness blocker. Only an
  "accepted" review of the change's current version clears it (assumption A-7 confirmed).
- **Q13:** a test-runner file counts as `verified` only if its modification time is within the observed test
  command's run window with a tolerance of 2 seconds either side (assumption A-6 confirmed).

No requirement text changes; the assumptions become confirmed decisions.

## Alternatives considered

Q12: letting "changes requested" clear the blocker (would hide unresolved changes). Q13: no tolerance (false
negatives from file-time granularity) or a larger window (weaker evidence).

## Impact

SRS A-6, A-7, §6; architecture §10.3; schema `0007` notes and file-change reviews. Tasks TASK-069, TASK-072, TASK-073.

## Follow-up tasks

None.
