# DEC-021: User manuals, final acceptance and the 12-item final report

| Field | Value |
|---|---|
| Type | Requirement change (new requirements) |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 |
| Date | 2026-10-30 |
| Requirements / findings affected | FR-063 to FR-067, CON-017, CON-018 (new) |
| Approved by and when | The owner, 2026-10-30 (authorization of 18:56 +0530), relayed verbatim by the orchestrator (list of documents A to E, final acceptance list, final report list) |

## Context

The owner asked for five user-manual documents, written at the end against the implemented application, a final
acceptance verification and a final report with 12 items.

## Decision

Old text: none (new IDs; no existing ID reused). New requirements:

| ID | Summary |
|---|---|
| FR-063 | `docs/user-manual/AGENT_OPERATING_MANUAL.md` (owner's item A) |
| FR-064 | `docs/user-manual/AGENTDESK_USER_MANUAL.md` (item B), for readers who do not know FastAPI, SQLite, Git hooks or Claude Code internals |
| FR-065 | `docs/user-manual/TROUBLESHOOTING.md` (item C) |
| FR-066 | `docs/user-manual/ARCHITECTURE_AND_MAINTENANCE.md` (item D) |
| FR-067 | `docs/user-manual/GETTING_STARTED.md` (item E) |
| CON-017 | Final acceptance: the owner's 11 verification items, each with saved evidence |
| CON-018 | Final report from ORC with the owner's 12 items |

All five documents must match the implemented application; TST checks them against the running app (TASK-087).

## Alternatives considered

Writing the manuals earlier (would describe features before they exist).

## Impact

SRS §4.1, §5.2 (Phase 6 table), §7 counts; plan §1.8, Phase 6 tasks TASK-081 to TASK-092; architecture §13.

## Follow-up tasks

TASK-081 to TASK-083 (DEV), TASK-087 (TST), TASK-090 to TASK-092 (ORC, owner).
