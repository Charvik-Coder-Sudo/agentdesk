# AgentDesk: Software Requirements Specification (SRS)

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Draft (revision 1.1 of the 1.0 baseline: adds NFR-024 as Proposed; no Approved requirement text changed; the 1.0 baseline stays in force) |
| Last updated | 2026-10-31 |
| Task ID | T-20261030-002-PLN (previous: T-20261030-001-PLN-2, T-20261030-001-PLN) |
| Maintained by | planner-agent (OD-9, OD-10) |
| Related documents | [architecture.md](architecture.md), [database-schema.md](database-schema.md), [implementation-plan.md](implementation-plan.md), [traceability-matrix.md](traceability-matrix.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-PLN | First draft with stable requirement IDs (OD-9, E9). Phase 1 requirements and all constraints Proposed; later-phase requirements Draft. Includes the owner's corrections OC-1 to OC-3. | FR-001 to FR-062, NFR-001 to NFR-023, CON-001 to CON-016 | Pending |
| 1.0 | 2026-10-30 | T-20261030-001-PLN-2 | Baseline. Every requirement Approved (§5.0). Phase gates replaced by the 13-step cycle and automatic progression (DEC-020: CON-006, CON-010, CON-014, CON-015 changed; CON-019 added). User manuals and final acceptance added (DEC-021: FR-063 to FR-067, CON-017, CON-018). Dependency files (DEC-018: CON-004, A-8). Q12 and Q13 closed (DEC-019: A-6, A-7). Test and sandbox locations (DEC-023: CON-008, NFR-023). Q10, Q12, Q13 closed. | All; changed CON-004, CON-006, CON-008, CON-010, CON-014, CON-015, NFR-023; new FR-063 to FR-067, CON-017 to CON-019 | The owner, 2026-10-30 (blanket authorization of all phases, OA); DEC-018, DEC-019, DEC-023 under the owner's delegated authority |
| 1.1 | 2026-10-31 | T-20261030-002-PLN | Phase 1 triage: new NFR-024 (owner-only access for secret files such as the ingest token, Phase 3, Must), from security finding SEC-005 ([DEC-024](decisions/DEC-024-local-data-privacy.md), Proposed). No existing requirement text changed. §1.3, §5.0, §6 and §7 updated to match. | NFR-024 (new) | Pending user approval (NFR-024 Proposed; it strengthens security and adds no dependency, so it may be recorded under the owner's delegated authority, SRS §1.3) |

---

## 1. Purpose and scope

### 1.1 Purpose

This document lists what AgentDesk must do, each item with a stable ID, so that the design, the plan tasks
(TASK-###), the tests and the security findings can be traced back to it
([traceability-matrix.md](traceability-matrix.md)). It follows the IEEE 29148 structure, shortened to suit a
small personal tool (FU-1).

### 1.2 Product scope

AgentDesk is a lightweight, local, personal Windows GUI that lets one owner supervise four Claude Code agents
(planner, developer, testing, security audit) across the owner's own software projects. It shows, with
evidence, what the agents did: activity, file changes and their reasons, tests actually run, security
findings, decisions waiting for the owner, and release readiness (Brief §1).

- **In scope**: a browser dashboard served by a local FastAPI server; SQLite storage; Claude Code hooks;
  read-only Git inspection; reading the agents' tracking files; manual report paste; recording the owner's
  decisions.
- **Out of scope**: running, prompting or chatting with agents; approving, staging, committing, pushing or
  deploying anything; editing monitored projects (except the confirmed hook-settings write of the connection
  wizard); several users, logins, remote access, cloud hosting, Docker (Brief §2, R8, R9, FU-1, FU-2).

### 1.3 How to read this document

- **Priority**: Must (needed for the phase to be useful), Should (valuable), Could (only if cheap). A Should or
  Could item may move to a later phase, still delivered before final acceptance, by a recorded PLN decision with
  its reason (DEC-020). Leaving any requirement out of version 1 (status Deferred or Rejected) needs the
  owner's agreement.
- **Phase**: the phase (1 to 6, [implementation-plan.md](implementation-plan.md) §2) that delivers the
  requirement. `1-6` means it applies to every phase.
- **Source**: Brief §N = owner brief section; R1-R12 = owner refinements; OD-n = owner decisions;
  E1-E10 = review findings; FU-n = owner follow-up principles; OC-1 to OC-3 = owner corrections relayed by the
  orchestrator during T-20261030-001-PLN (OC-1: the Security Audit Agent is strictly read-only and returns its
  report for the orchestrator to record, replacing the write permissions in OD-16; OC-2: contents of the
  end-of-phase completion report; OC-3: beginner-friendly explanation after each significant task).
  OA = the owner's authorization of 2026-10-30T18:56+0530: blanket approval of all phases, the 13-step
  continuous improvement cycle without phase-by-phase approval, the user manuals and the final acceptance list
  (relayed verbatim by the orchestrator in the T-20261030-001-PLN-2 delegation).
  All are dated 2026-10-30.
- **Status**: Draft (written, not yet put to the owner), Proposed (put to the owner for approval), Approved
  (only after the owner explicitly confirms it; who and when are recorded, §5.0), Deferred, Rejected. IDs are
  never renumbered or reused; removed items stay as Rejected or Deferred. In version 1.0 every requirement is
  Approved; version 1.1 adds NFR-024 with status Proposed.
- **Changes**: a change to an Approved requirement starts as a Proposed change and is recorded in
  `docs/decisions/DEC-###-<slug>.md` before this document's version is raised. Under OA, a clarification that
  resolves a minor ambiguity with the simplest maintainable solution may be approved under the owner's delegated
  authority, with that basis stated in the decision record (DEC-020). The owner must still decide: weakening a
  security requirement (NFR-001 to NFR-020, CON-012), setting any requirement to Deferred or Rejected, adding a
  direct dependency (CON-004), and accepting the risk of a Critical or High security finding.

## 2. Definitions

| Term | Meaning |
|---|---|
| Owner | The one person who uses AgentDesk and makes every decision. |
| Orchestrator | The main Claude Code session that delegates work to the four agents and records the owner's decisions. |
| Agent | One of `planner-agent`, `developer-agent`, `testing-agent`, `security-audit-agent` (Claude Code subagents). |
| Monitored project | A folder the owner has registered in AgentDesk. |
| Work item, task ID | `T-YYYYMMDD-NNN` is a work item; `T-YYYYMMDD-NNN-ROLE` (ROLE = PLN, DEV, TST, SEC, ORC) is one agent's task on it. |
| Hook | A small program that Claude Code runs on events such as SessionStart or PostToolUse. AgentDesk's hook script forwards a sanitized copy of the event. |
| Git checkpoint | A stored snapshot of Git facts for a project at one moment: branch, HEAD commit, changed files, change types, line counts and content fingerprints. No file contents. |
| Baseline | The checkpoint at the start of a window (project registration or session start) that later changes are compared with. |
| Evidence label | One of the five labels below that tell the owner how strong the evidence about a file change is. |
| Verification value | The evidence strength of other records: `observed`, `verified`, `agent_reported`, `human`, `system`, and for test runs only `file_origin_unverified`. |
| Test-runner file | A result file written by a test tool, for example JUnit XML (E1). |
| No attribution by timing | The rule that a change is never linked to an agent only because it happened while the agent was running (R6, FU-6). |
| Review request | A record AgentDesk creates from facts to ask the owner for a decision. Only the owner decides. |
| File-change review | The owner's mark on a Git-verified change: accepted, or changes requested (E2). |
| Release readiness | A list of blockers derived from records. Never a claim that a project is secure or ready on its own. |
| Refused folder | A location AgentDesk never registers as a project (FR-022). |
| Placeholder page | A Phase 1 page that states its purpose and the phase in which its content arrives. It shows no data. |
| Spool | A local file where the hook script stores events while the AgentDesk server is unavailable. |
| CSRF token | A random value the browser must send with every state-changing request, so other websites cannot trigger actions. |
| Ingest token | A random value the hook script must send with events, so other programs cannot post fake events. |

### 2.1 The five evidence labels (R5, FU-6)

| Label | Meaning | What it does not mean |
|---|---|---|
| OBSERVED | A Claude Code hook reported a successful file tool call (Write, Edit, MultiEdit, NotebookEdit) on this path, by a named agent or the main session. | That this agent wrote the file's final content. |
| GIT-VERIFIED | Git shows the file differs from the last commit or from the selected baseline. | Who made the change. |
| AGENT-REPORTED | An agent's report (tracking file, pasted report or final message) says it changed this file. | That the change happened. |
| UNATTRIBUTED | A Git-verified change with no observed tool call and no report naming the file. | That nobody is responsible. There is no evidence either way. |
| PRE-EXISTING | The file's current content already existed at the start of the selected window. | That the content is safe or approved. |

## 3. Users and environment

- **User**: the owner, a single person on their own Windows PC. Beginner-friendly wording is expected (Brief §11).
- **Data producers, not users**: the orchestrator and the four agents, through hooks, tracking files and reports.
- **Environment** (planner input §F):

| Item | Value |
|---|---|
| Operating system | Windows 11 |
| Python | 3.15.2 installed (3.14 also present); minimum supported 3.12 |
| SQLite | 3.53.4, bundled with Python 3.15.2 |
| Git | 2.53 |
| Claude Code | 2.1.314 |
| Browser | A current desktop browser on the same PC (assumption A-2) |
| Network | Loopback only (127.0.0.1); no internet access needed at runtime |

## 4. Constraints and assumptions

### 4.1 Constraints

| ID | Statement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| CON-001 | AgentDesk shall use Python with FastAPI (REST), SQLite through Python's `sqlite3` with plain SQL (no ORM), and HTML5, CSS3 and vanilla JavaScript modules without a build step. | Must | 1-6 | Brief §2, R1 | Approved | Dependency files and code contain no other framework, ORM or build tool. |
| CON-002 | AgentDesk shall work without Claude API keys, the Anthropic Console, cloud hosting, paid services, external databases or Docker, and shall make no requests to external hosts at runtime. | Must | 1-6 | Brief §2, Brief §11, FU-2 | Approved | The app runs with the network cable unplugged; the CSP allows `'self'` only; code review finds no external URLs. |
| CON-003 | AgentDesk shall run on Windows 11 with Python 3.12 or newer (developed on 3.15.2). | Must | 1-6 | Brief §2, planner input §F | Approved | `scripts\setup.bat` refuses Python older than 3.12 with guidance; the app starts on the owner's PC. |
| CON-004 | AgentDesk shall limit its direct dependencies to FastAPI and Uvicorn at runtime and pytest and httpx for development, at fixed versions, with no frontend libraries, no chart or diagram libraries and no custom Markdown renderer in version 1. Any new direct dependency needs the owner's approval. Dependency files follow DEC-018: `requirements.txt` pins the top-level runtime packages; `requirements.lock.txt` holds the exact runtime versions (including sub-dependencies) from `pip freeze` in a fresh `.venv` and is what `scripts\setup.bat` installs; `requirements-dev.txt` adds the development packages. | Must | 1-6 | R10, OD-6, OD-14, FU-2, DEC-018 | Approved | `requirements.txt` lists exactly `fastapi==0.162.0` and `uvicorn==0.54.0`; `requirements-dev.txt` adds exactly `pytest==9.2.0` and `httpx==0.28.1`; installing `requirements.lock.txt` into a fresh `.venv` gives a `pip freeze` output identical to the lock file, and the lock file adds no package that fastapi or uvicorn does not require; `scripts\setup.bat` installs from the lock file. |
| CON-005 | AgentDesk's database schema shall grow by phase: each feature's tables arrive in that feature's migration, and Phase 1 creates only `schema_migrations` and `app_settings`. | Must | 1-6 | R2, OD-7 | Approved | After the first Phase 1 start the database holds exactly these two tables and schema version 1. |
| CON-006 | AgentDesk shall be built one phase at a time. Each phase follows the 13-step continuous improvement cycle in implementation-plan.md §1.2 and ends only at the internal verification gate (§1.6), when its acceptance criteria are met with verification evidence; the next phase then starts automatically, without an owner approval gate. The owner's manual browser checklist and final decision take place once, after Phase 6 (DEC-020). | Must | 1-6 | Brief §9, R11, OD-1, FU-4, FU-5, OA, DEC-020 | Approved | For every phase N the activity log shows, before the first DEV task of phase N+1: the TST report(s), the security report(s) recorded by ORC, and the PLN gate check stating that every Must requirement of phase N is Tested and passed or listed as Blocked on an owner decision (§1.6). |
| CON-007 | AgentDesk shall follow the modular structure in architecture.md §13 (never one large Python file) with straightforward code and no unnecessary abstractions. | Should | 1-6 | Brief §8, FU-2 | Approved | Code review at each phase. |
| CON-008 | No agent and no part of AgentDesk shall stage, commit, push, deploy or discard changes; the owner decides when to commit. Test fixtures and the Phase 4 real-event check may create commits only in throwaway repositories inside the Git-ignored `.pytest_tmp/` and `.sandbox/` folders, never in AgentDesk's repository or an owner's project (DEC-023). | Must | 1-6 | Brief §11, OD-12, DEC-023 | Approved | `git log` and the index of AgentDesk's repository are unchanged by agent tasks (orchestrator's `git status` checks); test review finds no Git write command aimed outside those two folders. |
| CON-009 | Development shall create or modify files only inside this repository. | Must | 1-6 | Brief §11 | Approved | Setup and start scripts write only inside the repository; the security review confirms it. |
| CON-010 | AgentDesk shall stay proportionate to a personal tool: no login system, analytics, separate background services, Docker or enterprise deployment unless an approved requirement needs it, and the basic security protections (NFR-001 to NFR-007) shall never be weakened to save effort. | Must | 1-6 | FU-1, FU-2, DEC-020 | Approved | Planner scope check at each phase start and at each phase gate; owner review at final acceptance (TASK-092). |
| CON-011 | The developer shall write the initial tests; the Testing Agent shall independently review them, add edge cases and execute the suite. The developer's own test results are not independent verification. | Must | 1-6 | OD-11, E8 | Approved | Each phase has a testing report with the exact commands and actual results from the Testing Agent. |
| CON-012 | The security review shall be strictly read-only: for AgentDesk work the Security Audit Agent modifies no file at all (no application code, documentation, its own audit report, the findings register, the activity log, configuration, global agent definitions or project settings) and returns its full audit report in its final answer; the orchestrator saves that report verbatim, updates the findings register and adds the log entry, each labelled "recorded by orchestrator from security-audit-agent's returned report"; the orchestrator compares `git status` before and after each security task and reports any change to the owner as a discrepancy. | Must | 1-6 | OD-16, OC-1 | Approved | Each security task has both `git status` outputs, identical or with every difference reported as a discrepancy; the audit report, register update and log entry carry the "recorded by orchestrator" label. |
| CON-013 | Every delegation to the developer agent shall cite the owner's explicit approval and the approved requirement and TASK IDs. | Must | 1-6 | E10 | Approved | Each developer change report quotes the approval and the IDs it implements. |
| CON-014 | GUI behaviour shall be verified in each phase by automated HTTP/API and static-file tests, and visually by the owner with one consolidated manual browser checklist (implementation-plan.md Appendices A and B) run once, at final acceptance; no Chrome extension or browser automation is used. | Must | 1-6 | OD-2, OA, DEC-020 | Approved | Each phase's TST report lists the GUI checks it automated and the manual steps it added to Appendix B; at final acceptance (TASK-092) the owner returns Appendices A and B with Pass, Fail or Notes for every step. |
| CON-015 | Each phase shall end with a completion summary from ORC containing the 10 items in implementation-plan.md §1.6, with every result classified as Implemented, Tested and passed, Tested and failed, Not tested, or Planned for a future phase. The summary is a record, not an approval request; a phase is never called complete while a required acceptance criterion is unmet. | Must | 1-6 | OC-2, FU-4, DEC-020 | Approved | Each phase's completion summary contains all 10 items, classifies every requirement of the phase and lists unmet acceptance criteria explicitly. |
| CON-016 | After each significant implementation task the orchestrator shall give the owner a short, beginner-friendly explanation: files changed, what each important file does, how the feature flows from GUI to backend to database, why this approach was chosen, which tests verify it, and what the owner should understand. | Must | 1-6 | OC-3, Brief §11 | Approved | Each significant Phase 1 DEV task is followed by such an explanation in the conversation, covering all six points. |
| CON-017 | Before the final report, the final acceptance shall verify with recorded evidence: (1) the full automated suite; (2) integration and regression tests; (3) a final independent security audit; (4) migrations, backup and restore; (5) the Windows scripts; (6) all pages and GUI workflows, by HTTP/API tests (visual checks are the owner's manual checklist); (7) hook installation, event collection, and shutdown and restart; (8) Git evidence and classification; (9) documentation reviewed; (10) the final Git diff checked; (11) no unrelated or global files modified. | Must | 6 | OA, DEC-021 | Approved | Each of the 11 items points to a saved TST report, security report recorded by ORC, or ORC record with the exact commands and actual results (implementation-plan.md §1.8, TASK-085 to TASK-090). |
| CON-018 | AgentDesk development shall end with a final report from ORC containing 12 items: executive summary; phases and features; traceability report; agent activity and task summary; test report; security report; limitations and risks; database and backup information; installation and launch; documentation locations; final Git status and changed files; manual verification checklist. | Must | 6 | OA, DEC-021 | Approved | The final report (TASK-091) contains all 12 items; every claim refers to a saved report or record; results are classified as in CON-015. |
| CON-019 | No task or phase shall be called complete because code was written: completion needs verification evidence (exact commands and observed results from an agent other than the author). Tests shall never be hidden, removed, suppressed, skipped or weakened to make a run pass; a test is changed only with a recorded reason (the test was wrong, or a requirement changed by a DEC), and a skip is allowed only for a missing optional tool with a visible reason (DEC-022), never counting as evidence. Security findings shall never be downgraded or closed without a documented technical justification, and a fix is Verified only after an independent security recheck. | Must | 1-6 | OA, DEC-020 | Approved | TST reports list every skipped test with its reason and every changed test with the recorded reason; the findings register shows a justification for every severity or status change; no task is marked Completed by an agent. |

### 4.2 Assumptions

| ID | Assumption | Affects |
|---|---|---|
| A-1 | One owner, one Windows PC, no remote access and no other users (FU-1). | All |
| A-2 | The owner uses a current desktop browser (for example Chrome or Edge) that supports ES modules and Content-Security-Policy. | FR-004 to FR-009, NFR-004 |
| A-3 | Port 8765 is free; `AGENTDESK_PORT` can change it. | FR-002, NFR-001 |
| A-4 | Agents follow the shared Change tracking protocol and its default paths. A project that overrides the paths shows "tracking files not found" (architecture §15). | FR-032, FR-061 |
| A-5 | Hook field names follow the official hook reference checked on 2026-10-30 against Claude Code 2.1.314; Phase 4 confirms them with real events. | FR-035 to FR-047 |
| A-6 | A test-runner file's modification time is compared with the observed command's run window with a fixed tolerance of 2 seconds either side (E1 "small tolerance"). Confirmed by DEC-019 (Q13 closed). | FR-054 |
| A-7 | A file-change review marked "changes requested" keeps the release-readiness blocker; only an "accepted" review of the current version clears it (E2). Confirmed by DEC-019 (Q12 closed). | FR-059, FR-060 |
| A-8 | Package versions are fixed as listed in CON-004; the file format is decided by DEC-018 (Q10 closed). | CON-004, TASK-003 |
| A-9 | Stored times are ISO 8601 UTC; the GUI shows local time. | All |

## 5. Requirements

### 5.0 Approval record

Every requirement in this version has status **Approved**, except NFR-024 (**Proposed**, added in version 1.1).
Who approved each one and when:

| Requirement IDs | Approved by | When | Basis |
|---|---|---|---|
| FR-001 to FR-062, NFR-001 to NFR-023, CON-001 to CON-016 (v0.1 text, as changed below) | The owner | 2026-10-30 (authorization of 18:56 +0530) | OA, blanket authorization of all phases: "Treat all previously approved requirements, architecture decisions, constraints, and Planner corrections as approved." Recorded by planner-agent in T-20261030-001-PLN-2 from the orchestrator's verbatim relay |
| CON-006, CON-010, CON-014, CON-015 (changed); CON-019 (new) | The owner | 2026-10-30 | OA: the 13-step cycle replaces phase-by-phase approval ([DEC-020](decisions/DEC-020-continuous-cycle-replaces-phase-gates.md)) |
| FR-063 to FR-067, CON-017, CON-018 (new) | The owner | 2026-10-30 | OA: user manuals, final acceptance and final report ([DEC-021](decisions/DEC-021-user-manuals-and-final-report.md)) |
| CON-004 (changed) | Orchestrator, under the owner's delegated authority (OA) | 2026-10-30 | Dependency files ([DEC-018](decisions/DEC-018-dependency-files-and-lock.md)) |
| CON-008, NFR-023 (clarified) | Under the owner's delegated authority (OA); orchestrator decision DEC-023, clarification drafted by planner-agent | 2026-10-30 | Test and sandbox locations ([DEC-023](decisions/DEC-023-sandbox-real-event-verification.md)) |
| NFR-024 (new, **Proposed**, not yet approved) | Not yet approved. Proposed by planner-agent in T-20261030-002-PLN, 2026-10-31 | - | Security finding SEC-005 ([DEC-024](decisions/DEC-024-local-data-privacy.md), Proposed). It strengthens security and adds no dependency; under §1.3 the orchestrator may record its approval under the owner's delegated authority. It must be approved before TASK-038 (Phase 3) starts |

The `Status` column below therefore reads `Approved` everywhere except NFR-024 (`Proposed`). Implementation
progress is tracked in [traceability-matrix.md](traceability-matrix.md), not here.

### 5.1 Phase 1 functional requirements

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-001 | AgentDesk shall provide `scripts\setup.bat`, which checks the Python version, creates a virtual environment `.venv` in the repository and installs the pinned runtime dependencies (and, with the `dev` argument, the development dependencies). | Must | 1 | Brief §2, Brief §9, FU-3 | Approved | (1) With Python 3.12+ on PATH, `scripts\setup.bat` creates `.venv` if missing, installs the runtime packages at the CON-004 versions and exits with code 0. (2) `scripts\setup.bat dev` also installs pytest and httpx. (3) With no Python, or Python older than 3.12, it prints the required version and exits non-zero without creating `.venv`. (4) A second run succeeds. (5) It writes nothing outside the repository folder (script review). |
| FR-002 | AgentDesk shall provide `scripts\start.bat`, which starts the server on the configured loopback address and opens the dashboard in the default browser. | Must | 1 | Brief §9, FU-3 | Approved | (1) After setup, `scripts\start.bat` starts the server on http://127.0.0.1:8765 and opens the browser at that address. (2) Without `.venv` it prints "run scripts\setup.bat first" and exits non-zero without starting. (3) `python -m app` without `--open` starts the server without opening a browser. (4) Ctrl+C stops the server. |
| FR-003 | AgentDesk shall provide a health endpoint `GET /api/v1/health`. | Must | 1 | Brief §9, FU-3 | Approved | Returns 200 with JSON fields `status`, `version` (equal to the application version) and `uptime` in seconds (0 or more); needs no CSRF token. |
| FR-004 | AgentDesk shall show the server status in the page header, checking health every 10 seconds while the browser tab is visible. | Must | 1 | FU-3 | Approved | (1) Shows "Server OK" while health returns 200. (2) After the server stops, shows "Server unreachable" within about 10 seconds (at most 15). (3) After a restart, returns to "Server OK" within about 10 seconds without a page reload. (4) No health requests while the tab is hidden. (5) Status uses text and an icon, not colour alone. |
| FR-005 | AgentDesk shall provide navigation with 11 entries (Overview, Projects, Agents, Activity, File changes, Reports, Documents, Testing, Security, Approvals, Settings), each opening its own deep-linkable page. | Must | 1 | Brief §3, FU-3 | Approved | (1) Each entry opens its hash route (`#/overview` ... `#/settings`); `#/overview` is the default. (2) The active entry has `aria-current="page"` and the browser title names the page. (3) Loading a route URL directly opens that page; Back and Forward work. (4) An unknown route shows "Page not found" with a link to Overview. |
| FR-006 | AgentDesk shall show, on every page except Settings, a clearly labelled placeholder that states the page's purpose and the future phase that will deliver it, without any data. | Must | 1 | FU-3, Brief §4A | Approved | (1) Each of the 10 pages shows its title, a one-sentence purpose and "Arrives in Phase N" with the phase from architecture.md §10.1. (2) No numbers, sample rows or invented data appear. |
| FR-007 | AgentDesk shall let the owner choose a light, dark or follow-system theme, remembered by the browser. | Must | 1 | Brief §3, FU-3 | Approved | (1) A control offers Light, Dark and System; System is the default and follows the operating system setting. (2) The choice is kept in the browser's local storage and restored after a page reload and after a server restart. |
| FR-008 | AgentDesk shall show system and database status on the Settings page. | Must | 1 | FU-3, E3 | Approved | Settings shows real values from `GET /api/v1/system`: application version; Python and SQLite versions; schema version (1 after Phase 1) and the applied migrations (version, name, time); database file size; data folder path; integrity check result and time; last backup time; the backup list (name, size, time, reason). It has no owner-name or profile field. |
| FR-009 | AgentDesk shall let the owner create a database backup from the Settings page. | Must | 1 | Brief §6, FU-3 | Approved | (1) "Create backup now" sends `POST /api/v1/system/backups` with the CSRF token. (2) On success a new entry appears in the list without a page reload and a status message is announced. (3) The file `data/backups/agentdesk-YYYYMMDD-HHMMSS-manual.db` exists and passes `PRAGMA integrity_check`. (4) Without a valid CSRF token the API returns 403 and creates no file. (5) A failure shows a plain error message. |
| FR-010 | AgentDesk shall back up the database automatically at startup when the newest backup is more than 24 hours old, and before applying migrations to an existing database, keeping the newest 10 AgentDesk backups. | Must | 1 | Brief §6 | Approved | (1) Starting with an existing database and no backup newer than 24 hours creates a `startup` backup. (2) Pending migrations on an existing database are preceded by a `pre-migration` backup. (3) After any backup only the 10 newest `agentdesk-*.db` files remain; other files in `data/backups/` (for example `pre-restore-*`) are never deleted. (4) Each backup is integrity-checked and a failed check is logged and shown. |
| FR-011 | AgentDesk shall provide command-line backup and restore: `scripts\backup_db.py` (`create`, `list`) and `scripts\restore_db.py` (`list`, `restore <file>`). | Must | 1 | Brief §6, FU-3 | Approved | (1) `create` makes a backup and prints its path; `list` prints the backups. (2) `restore` refuses while AgentDesk is running (port in use) with a clear message. (3) It asks the user to type `RESTORE`; any other input cancels with no change. (4) It accepts only a backup file name inside `data/backups/` and refuses a candidate that fails the integrity check. (5) It moves the current database to `data/backups/pre-restore-<time>.db` before copying the candidate in. (6) After restart, the restored data is present. |
| FR-012 | AgentDesk shall apply numbered SQL migrations at startup, in order, each in its own transaction, and record them with a checksum. | Must | 1 | Brief §6, R2 | Approved | (1) A new database reaches schema version 1. (2) A second start applies nothing and changes no rows. (3) Each applied migration is recorded with version, name, SHA-256 checksum and time. (4) Editing an applied migration file stops startup with a message naming the file and leaves the database unchanged. (5) A failing migration is rolled back, not recorded, and stops startup with a clear message. (6) `app_settings` holds `instance_id` and `created_at` after the first start, unchanged on later starts. |
| FR-013 | AgentDesk shall check database integrity at startup and refuse to start on a damaged database without changing it. | Must | 1 | Brief §7, FU-3 | Approved | (1) An existing database is checked with `PRAGMA quick_check`. (2) On failure the server does not start, logs the result and prints how to restore with `scripts\restore_db.py`. (3) The damaged file's SHA-256 is identical before and after. |
| FR-014 | AgentDesk shall include startup instructions in `README.md`. | Must | 1 | Brief §9, Brief §11 | Approved | The README explains in plain language: what AgentDesk is; requirements (Windows 11, Python 3.12+, Git); setup; start; running the tests; where data is stored; backup and restore commands; that the server is local-only and must not be exposed; the current phase and its limits. |

### 5.2 Functional requirements for Phases 2 to 6

#### Phase 2: Dashboard UI

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-015 | AgentDesk shall provide an Overview page with connected projects, active sessions, active agent tasks, completed and failed tasks, pending approvals, recent file changes, testing status and security status. | Must | 2 | Brief §4A, R4 | Approved | Every tile and row opens its filtered list or item; every number comes from stored records; empty states when there is no data; no fabricated statistics. Real data arrives in Phases 3 to 5. |
| FR-016 | AgentDesk shall show a profile for each of the four agents with name, responsibilities, current task, status, last activity and recent reports. | Must | 2 | Brief §4B, R4 | Approved | Four profiles listed; an agent with no recorded activity shows "Never seen"; a definition existing never implies activity. |
| FR-017 | AgentDesk shall provide a chronological activity timeline in which each event shows event ID, project, session, task ID, agent (when known), event type, time, description, related file, source and verification value, with filters for project, agent, event type, source, date range and status. | Must | 2 | Brief §4C, R4 | Approved | Newest first with "Load more"; filters combine and are kept in the URL; unknown fields show "unknown". Real data from Phase 3. |
| FR-018 | AgentDesk shall link every ID it shows (event, session, task, agent, file, report, finding) to a detail view with breadcrumbs, keeping filters in the URL. | Must | 2 | R4 | Approved | Each ID type has a detail route; reloading a detail URL shows the same view; Back restores the previous filters. |
| FR-019 | AgentDesk shall offer a sample-data preview mode for reviewing the Phase 2 UI, off by default, with a fixed "SAMPLE DATA, not real activity" banner on every page while it is on. | Should | 2 | Brief §9, Brief §4A | Approved | With preview off, only real data or empty states appear; no sample value can appear without the banner. |
| FR-020 | AgentDesk shall refresh visible lists every 5 seconds while the tab is visible, with a pause control. | Should | 2 | R4 | Approved | No refresh requests while the tab is hidden; Pause stops refreshing until Resume. |

#### Phase 3: Tracking

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-021 | AgentDesk shall let the owner register an existing folder as a monitored project through connection wizard steps 1 and 2 (choose a folder, see its Git status, confirm), recording a baseline Git checkpoint. | Must | 3 | R3, Brief §5, Brief §9 | Approved | The folder browser returns folder names only; the resolved final path is shown; an already registered folder links to its project; branch, last commit and uncommitted change counts are shown with "N uncommitted changes will be labelled PRE-EXISTING"; a non-Git folder can be registered with a notice; project files and `git status` are unchanged afterwards. |
| FR-022 | AgentDesk shall refuse to register as a project any drive root, `C:\Users`, any user-profile root (for example `C:\Users\Charvik`), the Windows and program folders or anything inside them, and its own data folder or anything inside it; and it shall not use an enclosing Git repository whose root is such a location. | Must | 3 | OD-17, E6 | Approved | Each location is refused with a reason, also when reached through a junction, symlink, `..`, trailing slash or different letter case; a folder inside a profile (for example `C:\Users\Charvik\projects\app`) is accepted; a folder whose Git root is refused is registered as "Not a Git repository" with an explanation and no Git command is run for it; nothing is written anywhere. |
| FR-023 | AgentDesk shall not create, modify or delete any file in a monitored project, except the hook-settings write of the connection wizard after the owner previews and confirms it (FR-040, FR-042) and future features the owner separately authorizes. | Must | 3 | R8, Brief §4D, Brief §11 | Approved | Tests show registration, checkpoints, diff viewing, rescans and report ingestion leave project files and `.git` unchanged (hashes and `git status` identical); the Git allowlist holds read-only subcommands only. |
| FR-024 | AgentDesk shall never approve, stage, commit, push, deploy or discard anything, and shall never modify global Claude Code settings or agent definitions. | Must | 3 | R9, Brief §4H, OD-12 | Approved | No code path runs a Git write subcommand (allowlist test and review); the database refuses `agentdesk` as a decider; no code writes under `~/.claude/` or any `.claude/agents/` folder. Re-checked in Phase 6. |
| FR-025 | AgentDesk shall accept structured JSON activity events at `POST /api/v1/events`, validate them and store them with their source and verification value. | Must | 3 | Brief §2, Brief §5, Brief §7 | Approved | Malformed, wrongly typed, incomplete or oversized events are rejected with a clear 4xx error and no partial rows; a repeated `event_uuid` is stored once; the request needs the ingest token or the CSRF token; an event that matches no project is stored as "project unknown". |
| FR-026 | AgentDesk shall take read-only Git checkpoints of each registered Git project at registration and on "Refresh from Git". | Must | 3 | Brief §5, Brief §9 | Approved | Checkpoints match `git status` in temporary test repositories for added, modified, deleted, untracked, binary, staged-rename and conflicted files; nothing is written to `.git`; more than 5,000 changed files are marked truncated. |
| FR-027 | AgentDesk shall provide a File Change Explorer listing Git-verified changes with change type, first-detected time, associated task and agent (only when evidence exists), evidence labels and the change explanation from real sources, with filters for project, window, label and change type. | Must | 3 | Brief §4D | Approved | Renames shown only when Git establishes them; the explanation stays empty when no real source exists; filters combine. |
| FR-028 | AgentDesk shall show a readable before-and-after diff (unified or split) of a changed file, read live from the project. | Must | 3 | Brief §4D, Brief §7 | Approved | The diff matches `git diff`; binary files show "binary, not displayed"; oversized files show a notice; diff content is never stored in the database. |
| FR-029 | AgentDesk shall label every file change with one or more of the five evidence labels, computed from stored facts when viewed, shown as icon plus text with what the label does not mean. | Must | 3 | R5, FU-6, Brief §4D | Approved | One test per classification rule R-A to R-F (architecture.md §5.3); a report that arrives later changes the label on the next view; OBSERVED becomes possible in Phase 4 (FR-043). |
| FR-030 | AgentDesk shall never attribute a file change to an agent or session only because the change happened while that agent or session was active. | Must | 3 | R6, FU-6, Brief §4D, Brief §5 | Approved | A file changed during a session with no file tool event and no report is UNATTRIBUTED; the GUI says "Observed edit by ...", never "Changed by ..."; time overlap shows only neutral context; shell commands never produce OBSERVED. |
| FR-031 | AgentDesk shall flag, without resolving them: reported but not in Git; observed but not in that agent's report; Git change not reported; observed edit with no Git change. | Should | 3 | R5, FU-6 | Approved | Each flag is produced in a test scenario and worded as a prompt to review. |
| FR-032 | AgentDesk shall read the agents' activity log and change reports from each project's default tracking paths, read-only, and store parsed fields as agent-reported records. | Must | 3 | Brief §10, R5 | Approved | Template-format fixtures are parsed; a non-matching file is kept as "fields not recognized" and stays viewable; unchanged files are not re-parsed; a changed file creates a new version and keeps the old one; status text is shown exactly as written. |
| FR-033 | AgentDesk shall let the owner paste a report (template Markdown, an `agentdesk-report` JSON block, or plain text), preview what will be recorded, and save it as an agent-reported record submitted by the typed name. | Must | 3 | R7 | Approved | Format detected; nothing stored before Save; label "AGENT-REPORTED, submitted manually by <name> on <date>"; reports over 64 KB refused; redaction applied; text displayed escaped; file claims cross-checked with Git; a copyable instruction snippet offered; agent definitions never edited. |
| FR-034 | AgentDesk shall remove sample data and the preview toggle from the running application. | Must | 3 | Brief §9 | Approved | No sample fixture is served; test fixtures exist only under `tests/`. |

#### Phase 4: Claude Code integration

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-035 | AgentDesk shall provide a standard-library Python hook script that reads each hook event, sanitizes it locally, adds a unique event ID and capture time, posts it to the local server, and stores it in a local spool when the server is unavailable. | Must | 4 | Brief §5, Brief §2 | Approved | Fields handled as in architecture.md §6.3 (contents, prompts and tool output never sent); missing or incomplete fields handled safely; spool capped at 50 MB; the server address is fixed in the script. |
| FR-036 | AgentDesk's hook script shall never block or alter normal Claude Code work: it shall always exit with code 0, print nothing to standard output and finish within about 2 seconds when AgentDesk is unavailable. | Must | 4 | Brief §5 (item 7) | Approved | Exit code 0 and empty stdout when the server is down, the token is wrong, stdin is malformed, empty or oversized, or an internal error occurs; network timeout 1.5 s; its own errors go to `data/logs/hook.log` only. |
| FR-037 | AgentDesk shall map the hook events supported by the installed Claude Code version to sessions, subagent runs and tool activity, identifying subagents when the event supplies `agent_id` and `agent_type`, and shall verify this with real events. | Must | 4 | Brief §5, Brief §9 | Approved | Unit tests use recorded payload shapes; the real-event run records the payload shapes actually received; documented fields that did not appear are reported as findings; unknown fields never cause a crash. |
| FR-038 | AgentDesk shall replay spooled events at startup and every 60 seconds without duplicates, and show sessions as active, idle, stale or ended and runs without a stop event as unknown. | Must | 4 | Brief §9, Brief §4B | Approved | Events captured while the server was stopped appear exactly once after restart; idle after 30 minutes without events; stale after 12 hours without SessionEnd; "last event N ago" shown. |
| FR-039 | AgentDesk shall check a project's Claude Code configuration read-only in wizard step 3, and shall read user-level Claude settings and agent files only there, limited to `disableAllHooks`, hook counts and agent names. | Must | 4 | R3, OD-13 | Approved | Results as in architecture.md §7 step 3; no file modified; code review confirms no other module reads `~/.claude/`; invalid JSON is reported and blocks installing into that file. |
| FR-040 | AgentDesk shall install its hook entries into the project's `.claude/settings.local.json` (default) or `.claude/settings.json` only after showing a preview and receiving the owner's explicit confirmation with a typed name, preserving all existing settings and hooks. | Must | 4 | R3, OD-8, Brief §5 (items 8, 9) | Approved | Existing content preserved except the appended AgentDesk groups; a file changed after the preview aborts the install; the original is backed up in AgentDesk's data folder; atomic write; invalid JSON, comments or a non-object `hooks` value refused; re-install is idempotent; connection, approver name and time recorded. |
| FR-041 | AgentDesk shall show each project's connection health and run a self-test with a synthetic event. | Must | 4 | R3 | Approved | States Not connected, Awaiting first event, Connected, Attention needed, Not a Git repository (architecture.md §7 step 5); self-test events labelled SELF-TEST and excluded from statistics; Connected only after a real event. |
| FR-042 | AgentDesk shall remove only its own hook entries after a preview and confirmation, with backup and atomic write, and the README shall describe manual removal. | Must | 4 | Brief §5 (item 8) | Approved | Other entries unchanged; a settings file is deleted only if AgentDesk created it and nothing else remains, after confirmation. |
| FR-043 | AgentDesk shall label a file change OBSERVED only when a successful file tool event for the same project and path exists after the window's baseline. | Must | 4 | R5, Brief §5 | Approved | Successful Write or Edit gives "Observed edit by <agent or Main session>"; a failed tool call does not; a shell command never does. |
| FR-044 | AgentDesk shall link subagent runs to work items through the `Task ID:` line of the delegation and the report path in the final message, labelling inferred links as inferred. | Should | 4 | Brief §4C, Brief §5 | Approved | Matching task IDs give a direct link; otherwise the link shows "inferred"; only the task ID line is extracted from prompts. |
| FR-045 | AgentDesk shall store at most 1 KB (1,024 characters) of a subagent's final message, redacted, with its task ID and report path, as an agent-reported record. | Should | 4 | OD-4 | Approved | Longer messages are cut to 1,024 characters; the database refuses a longer summary for this source; task ID and report path are extracted when present. |
| FR-046 | AgentDesk shall take at most one automatic Git checkpoint per project per 10 seconds, merging further requests in that window into one trailing checkpoint, while always taking the registration and SessionStart baselines. | Must | 4 | E7 | Approved | 20 Stop events within 10 seconds give one immediate and one trailing checkpoint; registration and SessionStart checkpoints are taken at once even inside a window; no separate background worker. |
| FR-047 | AgentDesk shall derive each agent's status, current task and last activity only from received events and reports. | Must | 4 | Brief §4B | Approved | No events gives "Never seen"; status follows SubagentStart and SubagentStop; a run without a stop event in an ended or stale session shows "unknown (no stop event)". |
| FR-048 | AgentDesk shall provide clear instructions for connecting additional projects, in the wizard and in the README. | Should | 4 | Brief §5 (item 10) | Approved | README has a "Connect a project" section and manual hook removal steps; each wizard step explains itself in plain language. |

#### Phase 5: Engineering reports

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-049 | AgentDesk shall list project documents by type and show each as escaped plain text (monospace, wrapped) with its type, declared version and status, Git history and approval state, without Markdown rendering in version 1. | Must | 5 | Brief §4E, OD-6 | Approved | HTML, scripts and `javascript:` links in a document appear as literal text and create no elements; Mermaid blocks appear as source; content is read live, not stored. |
| FR-050 | AgentDesk shall index requirement IDs (FR-, NFR-, CON-) found in the SRS with their priority and status as written. | Could | 5 | Brief §4E | Approved | IDs listed with a link to the SRS; status shown exactly as written. |
| FR-051 | AgentDesk shall show test plans, proposed tests, executed runs and per-test results, clearly separating proposed tests from executed ones. | Must | 5 | Brief §4F | Approved | The database refuses a proposed test linked to a run; Proposed and Executed are separate tabs; each run shows its source and verification badge. |
| FR-052 | AgentDesk shall record shell commands that match known test runners, with their exit status, as observed test runs. | Should | 5 | Brief §4F, R5 | Approved | `pytest` and `npm test` style commands recognized; exit code taken from the failure event; command stored redacted, at most 200 characters. |
| FR-053 | AgentDesk shall import test-runner result files (for example JUnit XML) chosen by the owner from inside a registered project. | Could | 5 | E1, Brief §4F | Approved | Size-capped; path confined to the project; parse errors reported; only counts and per-test results stored. |
| FR-054 | AgentDesk shall label an imported test-runner file `verified` only when a hook observed a test-runner shell command complete in the same project and the file was modified within that command's run window (tolerance A-6), and otherwise label it "Test-runner file, origin not verified". | Could | 5 | E1 | Approved | Tests cover: matching command; no command; command in another project; file modified outside the window; the database refuses `verified` without a linked observed command. |
| FR-055 | AgentDesk shall compare agent-reported test commands with observed commands in the same session. | Should | 5 | Brief §4F, FU-6 | Approved | Shows "observed run matches" or "no matching observed run". |
| FR-056 | AgentDesk shall show security findings with severity (Critical, High, Medium, Low, Informational), affected files, description, remediation, remediation status as written in the findings register, verification status and audit reports, and shall never declare a project secure. | Must | 5 | Brief §4G | Approved | Statuses match the register's wording; a permanent "never declared secure" notice; the latest verdict labelled agent-reported. |
| FR-057 | AgentDesk shall create review requests from facts and record each owner decision with the typed name, time, exact subject version and optional comment. | Must | 5 | Brief §4H, OD-5 | Approved | No decision without a typed name; the Windows account name is never recorded; AgentDesk never decides; "Copy decision" gives a one-line statement; AgentDesk never writes decisions into project files. |
| FR-058 | AgentDesk shall keep decided approval records immutable and show when the decided subject has changed since. | Must | 5 | Brief §4H | Approved | Database triggers block updates and deletes of decided approvals; a changed decision is a new record; "approved version is outdated" shown when the hash or commit differs. |
| FR-059 | AgentDesk shall let the owner mark a Git-verified file change as Reviewed (accepted, or changes requested) with typed name, time and optional note, stored as an approval record pinned to project, path and content fingerprint (deleted files: a deletion marker plus the HEAD commit), without changing the evidence label. | Must | 5 | E2 | Approved | An UNATTRIBUTED change stays UNATTRIBUTED and shows "Reviewed by <name> on <date> for this version"; changed content shows the review as outdated; the record is immutable. |
| FR-060 | AgentDesk shall show release readiness on the Overview as blockers derived from records, and never show a project as ready or secure without a human release approval. | Must | 5 | Brief §1, Brief §4G, Brief §4H, E1, E2 | Approved | Blockers: open Critical or High findings without risk acceptance; no `verified` or `observed` test run, or a failed latest one; pending approvals; UNATTRIBUTED changes without an accepted review of their current version (A-7); missing audit or a NOT READY verdict. Agent-reported runs and unverified test-runner files do not clear the tests blocker. Never "secure". |
| FR-061 | AgentDesk shall parse test reports, audit reports, the findings register, decision records and CHANGELOG entries from the default tracking paths, read-only. | Should | 5 | Brief §10, Brief §4F, Brief §4G | Approved | Template fixtures parsed; unrecognized files kept and viewable; nothing written to the files. |
| FR-062 | AgentDesk shall show approvals recorded in project files separately and flag mismatches with its own approval records. | Could | 5 | Brief §4H | Approved | A mismatch between a project-file approval and AgentDesk's record is flagged, never resolved automatically. |

#### Phase 6: User manuals (DEC-021)

All five documents live in `docs/user-manual/`, are written after the features exist, and must match the
implemented application. Common acceptance for FR-063 to FR-067: every command, route, page name, button
label, status, evidence label, file path and error message quoted exists in the implemented application or
repository (checked by TST against the running app and the code, TASK-087); plain language with technical
terms explained at first use (NFR-012); no secrets.

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-063 | AgentDesk shall include `AGENT_OPERATING_MANUAL.md`, explaining how to use the four agents with AgentDesk. | Must | 6 | OA | Approved | Has a section for each topic: agent roles; when to use each agent; starting tasks in Claude Code; coordinating agents; exchanging reports and evidence; structuring tasks (task IDs, requirement IDs); monitoring in AgentDesk; reviewing agent claims against Git evidence; handling failed tests, rejected changes and security findings; repeating the cycle; safe use on existing projects; what agents can and cannot do; example workflows; copy-paste prompts that use the task-ID format and tracking paths. |
| FR-064 | AgentDesk shall include `AGENTDESK_USER_MANUAL.md`, a complete GUI manual for readers who do not know FastAPI, SQLite, Git hooks or Claude Code internals. | Must | 6 | OA | Approved | Has a section for each topic: architecture overview; Windows installation; launch and stop; connecting a project; hooks through the wizard; every navigation page; statuses and logs; evidence classifications; reports, tests and audits; approvals; settings; backup and restore; troubleshooting (link to FR-065); updates and maintenance; locally stored data; security limitations (from architecture.md §15). |
| FR-065 | AgentDesk shall include `TROUBLESHOOTING.md`. | Must | 6 | OA | Approved | Covers installation, startup, port, database, migration, hook, Git, testing and agent-report problems, each entry with symptom, cause and solution; a solution that touches the database starts with a backup step; none tells the reader to edit `.git` internals. |
| FR-066 | AgentDesk shall include `ARCHITECTURE_AND_MAINTENANCE.md`. | Must | 6 | OA | Approved | Covers project structure, important files, database and migrations, event flow, security boundaries, backups, testing, and how to maintain and extend (for example add a migration or a page); the migration list matches `migrations/`; the test commands run as written. |
| FR-067 | AgentDesk shall include `GETTING_STARTED.md`, a short quick start. | Must | 6 | OA | Approved | At most about 150 lines: requirements, setup, start, open the dashboard, connect a first project, stop, where to go next (links to FR-063 to FR-066); the commands run as written on a fresh copy of the working tree (TASK-086). |

### 5.3 Non-functional requirements

| ID | Requirement | Priority | Phase | Source | Status | Acceptance criteria |
|---|---|---|---|---|---|---|
| NFR-001 | AgentDesk shall bind only to a loopback address (default 127.0.0.1, port 8765). | Must | 1 | Brief §7, FU-3 | Approved | `AGENTDESK_HOST` accepts only `127.0.0.1`, `localhost` or `::1`; any other value (for example `0.0.0.0`) stops startup with a clear message and a non-zero exit; a port outside 1024-65535 or not a number stops startup the same way. |
| NFR-002 | AgentDesk shall reject requests whose Host header is not its own loopback address. | Must | 1 | Brief §7, FU-3 | Approved | Any Host other than `127.0.0.1:<port>`, `localhost:<port>` or `[::1]:<port>` (for example `evil.example`) gets 400, for pages and API alike. |
| NFR-003 | AgentDesk shall protect every state-changing request against cross-site request forgery. | Must | 1 | FU-3, FU-2 | Approved | For POST, PUT, PATCH and DELETE under `/api`: non-JSON content type gives 415; a foreign `Origin` gives 403; a missing or wrong `X-AgentDesk-CSRF` token gives 403; a valid request succeeds. The token is 32 random bytes, new at each start, served by `GET /api/v1/session`; a token from an earlier run is refused. No response carries CORS headers. GET requests change nothing. |
| NFR-004 | AgentDesk shall send security headers on every response. | Must | 1 | FU-3 | Approved | Pages and API responses carry `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` and `X-Frame-Options: DENY`; `/api` responses also carry `Cache-Control: no-store`. |
| NFR-005 | AgentDesk shall insert all data into pages as text, never as HTML, and use no inline scripts or styles. | Must | 1 | Brief §7 | Approved | `index.html` has no inline script, style or event-handler attribute; code review and a search find no `innerHTML`, `outerHTML`, `insertAdjacentHTML` or `document.write` used with data; the browser console shows no CSP violation. |
| NFR-006 | AgentDesk shall return errors as JSON without stack traces. | Must | 1 | Brief §7 | Approved | An unknown `/api` path gives a JSON 404; an unhandled error gives a JSON 500 with a generic message and no stack trace or file path; details go to the log. |
| NFR-007 | AgentDesk shall keep a rotating log for troubleshooting without request bodies or secrets. | Must | 1 | Brief §7 | Approved | `data/logs/agentdesk.log` rotates at 1 MB and keeps 5 files; request bodies and tokens never appear in it (test with a known token value). |
| NFR-008 | AgentDesk shall be fully usable with the keyboard. | Must | 1 | Brief §3 | Approved | The skip link is the first focusable element and moves focus to the main content; every control is reachable with Tab in visual order with a visible focus indicator; Enter opens a navigation entry; focus moves to the page heading after navigation; no keyboard trap. |
| NFR-009 | AgentDesk shall meet WCAG 2.1 AA contrast in both themes, never show status by colour alone, and respect reduced-motion settings. | Must | 1 | Brief §3 | Approved | Theme colour pairs reach 4.5:1 for normal text and 3:1 for large text and controls (checked on the design tokens); status shows text and an icon; animations are off under `prefers-reduced-motion`. |
| NFR-010 | AgentDesk shall be usable from about 400 px window width upwards. | Must | 1 | Brief §3 | Approved | At about 400 px every Phase 1 page works without horizontal scrolling; navigation is a top menu below 960 px and a sidebar from 960 px. |
| NFR-011 | AgentDesk shall store all its data locally in its data folder, which Git ignores. | Must | 1 | Brief §6, Brief §2 | Approved | Database, backups and logs are under the data folder (default `<repo>/data`, changeable with `AGENTDESK_DATA_DIR`); `.gitignore` covers `data/` and `.venv/`; `git status` shows neither. |
| NFR-012 | AgentDesk shall use plain, beginner-friendly language in its pages, messages and README, and every error message shall say what to do next. | Should | 1 | Brief §11, FU-1 | Approved | Owner's review during the manual checklist; startup errors (port, host, integrity) name the fix. |
| NFR-013 | AgentDesk shall never store passwords, API keys, private keys, secret values, file contents, prompts, tool output or transcripts, and shall redact and length-limit free text before storing it. | Must | 3 | Brief §5 (item 4), Brief §7 | Approved | Redaction tests for the token formats in architecture.md §6.3; content fields dropped (tests on API and hook inputs); length CHECKs in the schema. |
| NFR-014 | AgentDesk shall store shell commands only after secret redaction, truncated to 200 characters. | Must | 4 | OD-3 | Approved | A command containing a token is stored with `[REDACTED]`; a 500-character command is stored as 200 characters. |
| NFR-015 | AgentDesk shall read a project file only when its resolved path lies inside a registered project root. | Must | 3 | Brief §7 | Approved | `..`, absolute paths, symlinks, junctions and Windows alternate-stream paths (`name:stream`) that leave the root are refused. |
| NFR-016 | AgentDesk shall refuse to display sensitive files and any file inside its own data folder. | Must | 3 | Brief §7 | Approved | `.env*`, `*.pem`, `*.key`, `*.pfx`, `*.p12`, `id_rsa*`, `id_ed25519*`, `credentials*`, `secrets.*` and files under AgentDesk's data folder (for example `ingest_token`) are refused with a notice. |
| NFR-017 | AgentDesk shall never execute commands received from events, reports or browser input. | Must | 3 | Brief §7 | Approved | The only programs run are `git` with fixed read-only subcommands, `claude --version` and AgentDesk's own hook script for the self-test (code review and tests). |
| NFR-018 | AgentDesk shall run Git with an allowlist of read-only subcommands, argument lists without a shell, `GIT_OPTIONAL_LOCKS=0`, `core.fsmonitor=false`, `--no-ext-diff`, `--no-textconv` and timeouts. | Must | 3 | Brief §7, R8 | Approved | A test repository whose config sets an fsmonitor or external diff program runs no program; no `index.lock` is created. |
| NFR-019 | AgentDesk shall validate all API input (types, sizes, allowed values) and handle malformed input and database errors without crashing or storing partial data. | Must | 3 | Brief §5 (item 6), Brief §7 | Approved | Malformed, oversized, deeply nested and wrongly typed payloads get 4xx and the server keeps running; a database error gives a JSON error and a log entry. |
| NFR-020 | AgentDesk shall accept hook events only with the ingest token created at first start in `data/ingest_token`. | Must | 4 | Brief §7 | Approved | A missing or wrong token is refused; the token never appears in logs or pages. |
| NFR-021 | AgentDesk shall ingest events from several concurrent sessions without losing or duplicating events or showing database lock errors. | Must | 6 | Brief §9 | Approved | A test with at least 4 parallel senders stores every event exactly once with no lock error. |
| NFR-022 | AgentDesk shall stay responsive on the owner's PC with realistic data. | Should | 6 | Brief §3 | Approved | With 10,000 stored events, list pages show their first page within 1 second. |
| NFR-023 | AgentDesk shall be validated end-to-end before release: the complete application, malformed events, multiple projects, concurrent sessions, Windows startup from a fresh copy of the working tree (a true fresh clone needs the owner's commit and is a final manual checklist step, DEC-023), Git tracking scenarios, database recovery, and a security and permissions review. | Must | 6 | Brief §9, DEC-023 | Approved | Phase 6 testing and audit reports cover each area with executed commands and actual results. |
| NFR-024 | AgentDesk shall create secret files in its data folder (from Phase 3 the ingest token `data/ingest_token`) so that only the Windows account running AgentDesk, SYSTEM and the Administrators group can read or change them. It shall use only the Python standard library and shall never read or store the account name (DEC-009). If owner-only access cannot be applied, it shall not create the secret and shall say why and what to do. | Must | 3 | SEC-005 (T-20261030-002-SEC), DEC-024 | Proposed | (1) A test reads the token file's access list by SID: it is protected (not inherited) and holds entries only for the current user's SID, SYSTEM (S-1-5-18) and Administrators (S-1-5-32-544); there is no entry for Everyone (S-1-1-0), Authenticated Users (S-1-5-11) or Users (S-1-5-32-545). (2) Code review and a source scan find no call that reads the account name (for example `getpass.getuser`, `USERNAME`, `GetUserName`, `LookupAccountSid`). (3) When applying owner-only access fails (simulated), no token file is created and the message names the fix. (4) `requirements.lock.txt` is unchanged (no new dependency). (5) The token path stays `data/ingest_token` (NFR-020) unless a decision record changes it. |

## 6. Open questions

No question is open in version 1.1.

| ID | Question | Status | Resolution |
|---|---|---|---|
| Q10 | Which dependency file format should AgentDesk use (OD-14)? | Closed 2026-10-30 | Option B: `requirements.txt` (top-level pins), `requirements.lock.txt` (exact runtime versions, installed by `scripts\setup.bat`), `requirements-dev.txt` ([DEC-018](decisions/DEC-018-dependency-files-and-lock.md)) |
| Q12 | Should a file-change review marked "changes requested" keep the release-readiness blocker? | Closed 2026-10-30 | Yes; only an "accepted" review of the current version clears it (A-7, [DEC-019](decisions/DEC-019-review-blocker-and-file-tolerance.md)) |
| Q13 | Is a 2-second tolerance right for matching a test-runner file to an observed command (A-6)? | Closed 2026-10-30 | Yes, 2 seconds either side ([DEC-019](decisions/DEC-019-review-blocker-and-file-tolerance.md)) |

Question numbers Q1 to Q11 were used in the owner's earlier decisions (OD-9 to OD-15) and are not reused. New
questions continue from Q14.

## 7. Requirement counts

### 7.1 By status

| Type | Draft status | Proposed status | Approved status | Deferred status | Rejected status | Total |
|---|---|---|---|---|---|---|
| FR | 0 | 0 | 67 | 0 | 0 | 67 |
| NFR | 0 | 1 | 23 | 0 | 0 | 24 |
| CON | 0 | 0 | 19 | 0 | 0 | 19 |
| **Total** | **0** | **1** | **109** | **0** | **0** | **110** |

### 7.2 By priority

| Type | Must | Should | Could | Total |
|---|---|---|---|---|
| FR | 54 | 9 | 4 | 67 |
| NFR | 22 | 2 | 0 | 24 |
| CON | 18 | 1 | 0 | 19 |
| **Total** | **94** | **12** | **4** | **110** |

### 7.3 By phase

| Phase | FR | NFR | CON | Total |
|---|---|---|---|---|
| 1 | 14 | 12 | - | 26 |
| 2 | 6 | 0 | - | 6 |
| 3 | 14 | 7 | - | 21 |
| 4 | 14 | 2 | - | 16 |
| 5 | 14 | 0 | - | 14 |
| 6 | 5 | 3 | 2 | 10 |
| 1-6 (all phases) | - | - | 17 | 17 |
| **Total** | **67** | **24** | **19** | **110** |
