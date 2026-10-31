# DEC-017: Global Claude Code settings are read only by the Phase 4 wizard check

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-039, FR-024 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner choice OD-13 |

## Context

User-level Claude Code files are global and personal. AgentDesk should touch them as little as possible.

## Decision

AgentDesk reads `~/.claude/settings.json` and agent definition files only in the Phase 4 wizard configuration
check, read-only, limited to `disableAllHooks`, hook counts and agent names. No module writes them; no other
module reads them.

Development-process note: the orchestrator's baseline in TASK-023 and comparison in TASK-090 record only file
size and last-write time of these files (no content is read). That is a process check, not an AgentDesk feature.

## Alternatives considered

Reading global settings in other features (not needed; more exposure).

## Impact

Architecture §3.1, §7 step 3. Task TASK-056; security checks TASK-063, TASK-088.

## Follow-up tasks

None.
