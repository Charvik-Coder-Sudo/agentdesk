# DEC-016: The security review is strictly read-only

| Field | Value |
|---|---|
| Type | Design decision (development process) |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-012, CON-019 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner choice OD-16 as corrected by OC-1 |

## Context

An independent audit is only credible if the auditor changes nothing.

## Decision

For AgentDesk work, `security-audit-agent` modifies no file at all and returns its full audit report in its final
answer. The orchestrator saves it verbatim, updates the findings register and adds the log entry, each labelled
"recorded by orchestrator from security-audit-agent's returned report", and compares `git status` before and after
each security task, reporting any difference as a discrepancy.

**Limitation.** The agent's global definition keeps the Write and Edit tools and is not changed, so the boundary
rests on instructions and is checked by Git afterwards, not prevented. Changes Git cannot see are not detected.

## Alternatives considered

Letting the agent write its own report and register (OD-16 before correction OC-1).

## Impact

Implementation plan §1.4; architecture §11.1, §15 item 17. Every SEC task (TASK-019, -033, -048, -063, -076, -088).

## Follow-up tasks

None.
