# DEC-010: No chart libraries and no Markdown renderer in version 1

| Field | Value |
|---|---|
| Type | Design decision |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (proposed in T-20261030-001-PLN) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-004, FR-049 |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530): blanket authorization of all phases (OA), relayed verbatim by the orchestrator. Owner preference stated earlier as OD-6 |

## Context

Rendering Markdown from agent-written documents is a script-injection risk and would add a dependency or custom code.

## Decision

No chart or diagram libraries and no custom Markdown renderer in version 1. Documents are shown as escaped plain
text (monospace, wrapped) with a metadata panel. Adding a renderer later needs a separate owner decision with its
own security tests.

## Alternatives considered

A Markdown library (dependency and sanitizing burden); a hand-written renderer (security risk, maintenance).

## Impact

Architecture §2 P7, §10.3. Task TASK-067; security check in TASK-076.

## Follow-up tasks

None.
