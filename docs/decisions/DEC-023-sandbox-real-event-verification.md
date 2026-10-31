# DEC-023: Real-event verification in a sandbox; test files stay inside the repository

| Field | Value |
|---|---|
| Type | Design decision (development process; includes clarifications of CON-008 and NFR-023) |
| Status | Approved |
| Task ID | T-20261030-001-PLN-2 (decided by the orchestrator and relayed in this delegation) |
| Date | 2026-10-30 |
| Requirements / findings affected | CON-008, CON-009, NFR-023, FR-035 to FR-043 (TASK-061) |
| Approved by and when | The orchestrator, 2026-10-30, under the owner's delegated authority (OA). Items 4 to 7 were drafted by planner-agent as direct consequences, under the same authority |

## Context

Plan task 4.7 (v0.3) connected AgentDesk's own repository to test real hook events, which would put hooks into the
orchestrating session's project. Nothing may be written outside `D:\agentdesk` (CON-009).

## Decision

1. Phase 4 real-event verification (TASK-061) uses a throwaway Git project inside `D:\agentdesk\.sandbox\`
   (Git-ignored). Hooks are installed there through the wizard API; a short `claude -p` run starts a subagent and
   edits a file. This replaces "connect this repository".
2. AgentDesk's own repository is not connected during development, so the orchestrating session is never affected.
3. Tests write temporary files only inside the repository: pytest `--basetemp=.pytest_tmp` (Git-ignored).
4. The verification instance uses its own data folder (`.sandbox\data`) and a non-default port, so the owner's
   `data\` folder gets no test records; the wizard confirmation uses the typed name `sandbox-test`; the run never
   uses `--dangerously-skip-permissions`.
5. Test Git repositories set `GIT_CEILING_DIRECTORIES` and pass author details per command; global Git
   configuration is never changed.
6. CON-008. Old: "No agent and no part of AgentDesk shall stage, commit, push, deploy or discard changes; the
   owner decides when to commit." New: the same, plus "Test fixtures and the Phase 4 real-event check may create
   commits only in throwaway repositories inside the Git-ignored `.pytest_tmp/` and `.sandbox/` folders, never in
   AgentDesk's repository or an owner's project."
7. NFR-023. Old: "... Windows startup from a fresh clone ...". New: "... Windows startup from a fresh copy of the
   working tree (a true fresh clone needs the owner's commit and is a final manual checklist step) ...", because
   agents never commit (CON-008), so a clone would lack all work done since the owner's last commit (the owner
   committed `44afe9f` on 2026-10-30 while this record was being written; later work is uncommitted).

Note: during the `claude -p` run, Claude Code itself keeps its usual session records under the user profile, as
it does for every session including the orchestrator's. No agent or AgentDesk code writes there, and AgentDesk
never reads transcripts.

## Alternatives considered

Connecting AgentDesk's own repository (affects the orchestrating session); a project outside `D:\agentdesk`
(violates CON-009); the system temporary folder for tests (outside the repository).

## Impact

SRS CON-008, NFR-023; plan §1.3, §1.5, TASK-024, TASK-061, TASK-086; architecture §6, §13.

## Follow-up tasks

TASK-024 adds `.pytest_tmp/` and `.sandbox/` to `.gitignore` if missing.
