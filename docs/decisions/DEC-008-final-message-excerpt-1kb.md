# DEC-008: At most 1 KB of a subagent's final message is stored

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-045 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner preference stated earlier as OD-4 |

## Context

A subagent's final message links its run to its report, but full messages can be long and contain sensitive text.

## Decision

At most 1,024 characters of the SubagentStop final message are stored, redacted, together with the extracted
task ID and report path, labelled agent-reported. The database refuses a longer summary for this source.

## Alternatives considered

Storing nothing (loses the run-to-report link); storing the full message (size and exposure).

## Impact

Architecture §5.1, §6.3; schema `agent_reports` CHECK. Task TASK-053.

## Follow-up tasks

None.
