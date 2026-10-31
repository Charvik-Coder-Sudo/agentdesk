# DEC-002: Hook transport: standard-library Python command hook with offline spool

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-035, FR-036, FR-038 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator |

## Context

Claude Code hooks must never block or alter the owner's work (brief §5), and events must survive server downtime.

## Decision

A standard-library Python command hook. Tool events run async; lifecycle events (SessionStart, SessionEnd,
SubagentStart, SubagentStop, Stop) run synchronously with a 5-second timeout. When the server is unreachable, the
sanitized event is appended to a local spool (`data/spool/`) and replayed later without duplicates.

## Alternatives considered

Posting straight from a shell command (quoting problems on Windows, no spool); a heavier integration such as an
MCP server (out of scope for a monitoring tool).

## Impact

Architecture §6.1, §6.2, §6.5. Tasks TASK-052, TASK-054; verified with real events in TASK-061.

## Follow-up tasks

None.
