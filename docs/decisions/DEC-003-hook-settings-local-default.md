# DEC-003: Hook settings go to settings.local.json by default

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-040 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator |

## Context

Hook entries contain machine-specific absolute paths. Writing them into a shared file would affect everyone who
clones the project (brief §5, R3).

## Decision

The wizard writes AgentDesk's hook entries to the project's `.claude/settings.local.json` by default.
`.claude/settings.json` is used only when the owner explicitly chooses it in the wizard, shown with a warning.

## Alternatives considered

`settings.json` as the default (shared, committed paths); user-level settings (global, ruled out by DEC-017 and R9).

## Impact

Architecture §7 step 4. Task TASK-057.

## Follow-up tasks

None.
