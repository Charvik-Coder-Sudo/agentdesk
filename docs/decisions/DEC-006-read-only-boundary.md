# DEC-006: Read-only boundary toward monitored projects

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-023, FR-040, FR-042 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator |

## Context

AgentDesk monitors the owner's projects and must not change them (R8).

## Decision

AgentDesk never creates, modifies or deletes files in a monitored project. The only exception is the wizard's
hook-settings write and removal, after the owner previews the exact change and confirms it.

## Alternatives considered

Letting AgentDesk write tracking files or decisions into projects (rejected: the agents and the owner own those files).

## Impact

Architecture §2 P3, §3.1. Read-only proofs in TASK-046; checked by every security task and TASK-088.

## Follow-up tasks

None.
