# DEC-012: Hooks are installed through the dashboard wizard with preview and confirmation

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-039, FR-040, FR-041, FR-042 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner preference stated earlier as OD-8; refinement R3 |

## Context

Connecting a project should be easy for a beginner and must never damage existing Claude Code settings.

## Decision

The Project Connection Wizard installs hooks: read-only configuration check, preview diff with a file hash,
typed-name confirmation, backup of the original inside AgentDesk's data folder, atomic write, re-validation, and a
matching disconnect. This replaces the earlier command-line-only proposal.

## Alternatives considered

A command-line installer only (less visible to the owner); manual editing instructions only (error-prone).

## Impact

Architecture §7. Tasks TASK-056, TASK-057; real-event check TASK-061 (in the sandbox, DEC-023).

## Follow-up tasks

None.
