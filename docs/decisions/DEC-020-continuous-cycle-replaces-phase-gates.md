# DEC-020: The continuous improvement cycle replaces per-phase owner approval

| Field | Value |
|---|---|
| Type | Requirement change |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-006, CON-010, CON-014, CON-015 (changed); CON-019 (new); plan §1.1, §1.2, §1.5, §1.6, TASK-020 to TASK-022, Appendix A; DEC-013, DEC-014 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530), relayed verbatim by the orchestrator: "Do not ask me for phase-by-phase approval. Do not pause after completing an individual phase." |

## Context

Version 0.1 stopped after every phase for the owner's approval. The owner authorized all phases at once and set a
13-step cycle (plan §1.2) ending with "Automatically proceed to the next phase", plus verification rules: "Do not
mark a task complete merely because code was written. Require verification evidence. Do not hide, suppress, skip,
or weaken tests ... Do not downgrade security findings without a documented technical justification."

## Decision

Each phase follows the 13-step cycle. The phase gate becomes an internal verification gate (plan §1.6): a phase
ends only when its acceptance criteria are met with evidence; the next phase then starts automatically. The owner's
manual browser checklist and decision happen once, at the end (TASK-092). Routine clarifications may be approved
under the owner's delegated authority, and a Should or Could item may be rescheduled to a later phase before
final acceptance with a recorded reason. The owner still decides on weakening security requirements, leaving any
requirement out of version 1 (Deferred or Rejected), new direct dependencies, Critical or High risk acceptances,
and anything that would write outside `D:\agentdesk` or into an owner's project. SRS §1.3 (Priority, Changes)
is updated to match.

| ID | Old text (v0.1) | New text (v1.0) |
|---|---|---|
| CON-006 | "... each phase follows the 10-step cycle in implementation-plan.md §1.2 and ends with the owner's approval before the next phase begins." Acceptance: "The activity log shows the owner's approval of phase N before any task of phase N+1." | "... follows the 13-step continuous improvement cycle ... ends only at the internal verification gate (§1.6) ...; the next phase then starts automatically, without an owner approval gate. The owner's manual browser checklist and final decision take place once, after Phase 6." Acceptance: TST reports, ORC-recorded security reports and the PLN gate check precede the next phase's first DEV task. |
| CON-010 | Acceptance: "Planner scope check at each phase start; owner review at each phase end." | Acceptance: "Planner scope check at each phase start and at each phase gate; owner review at final acceptance (TASK-092)." |
| CON-014 | "GUI checks shall be done by the owner with a manual browser verification checklist ..." Acceptance: the Phase 1 checklist returned by the owner. | GUI behaviour verified each phase by automated HTTP/API and static-file tests, and visually by one consolidated owner checklist (Appendices A and B) at final acceptance; no browser automation. |
| CON-015 | "Each phase shall end with a completion report containing the 10 items ..." | "... a completion summary from ORC ... The summary is a record, not an approval request ..." |
| CON-019 | (new) | Verification integrity: evidence from an agent other than the author; no hidden, removed, suppressed, skipped or weakened tests; findings never downgraded without documented justification. |

Plan: step 10 of the old cycle ("Stop and wait for the owner's approval before starting the next phase") is
removed; TASK-022 (owner's Phase 1 checklist) is superseded by TASK-092.

## Alternatives considered

Keeping per-phase owner gates (rejected by the owner).

## Impact

SRS v1.0 §1.3, §4.1; plan v1.0 §1, §3, Appendices; architecture §16. Every phase has a triage-and-gate task.
Security requirements are not weakened.

## Follow-up tasks

None beyond the tasks in plan §3 to §8.
