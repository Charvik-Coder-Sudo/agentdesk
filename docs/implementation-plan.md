# AgentDesk: implementation plan

| Field | Value |
|---|---|
| Version | 0.3 |
| Status | Draft |
| Last updated | 2026-10-30 |
| Task ID | T-20261030-001-PLN (maintained by planner-agent, OD-10) |
| Related documents | [srs.md](srs.md), [architecture.md](architecture.md), [database-schema.md](database-schema.md), [traceability-matrix.md](traceability-matrix.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-ORC | Six-phase plan, presented in conversation | - | Accepted in principle by the project owner |
| 0.2 | 2026-10-30 | T-20261030-001-ORC | Refinements R1-R12: phased migrations, Connection Wizard split across Phases 3-4, evidence model, manual reports, tracking-file ingestion, interactive detail views; exact Phase 1 checklist | R1-R12 | Pending |
| 0.3 | 2026-10-30 | T-20261030-001-PLN | Status Draft (E4, OD-18). §1 rewritten: Option B (OD-1), 10-step phase cycle (FU-4), test responsibilities (OD-11, E8), strictly read-only security review with `git status` check (OD-16 as corrected by OC-1), developer delegations cite approval and IDs (E10), Planner confirms each phase, no automatic Git actions (OD-12), no Chrome extension (OD-2), completion report contents (OC-2), beginner explanations (OC-3), dependency format open (Q10, OD-14). §3: Phase 1 checklist A-H turned into TASK-001 to TASK-022 linked to requirement IDs (E9); evidence badges and project selector moved out of Phase 1; one placeholder module instead of ten. New Appendix A: manual browser checklist (E5). Phases 3-6 updated for E1, E2, E6, E7, OD-4, OD-6, OD-13. | E1, E2, E4-E10; OD-1, OD-2, OD-4, OD-6, OD-11 to OD-14, OD-16; OC-1 to OC-3; FR-001 to FR-014, NFR-001 to NFR-012, CON-001 to CON-016 | Pending |

## 1. Working rules

### 1.1 Execution model: Option B (OD-1, DEC-013)

The owner chose Option B. The main session orchestrates; each agent does its own part with a role task ID
(`-PLN`, `-DEV`, `-TST`, `-SEC`). The owner is the final decision-maker and approves each phase before the next begins.

| Role | Who | Does | Never does |
|---|---|---|---|
| Owner | The project owner | Approves requirements, documents, decisions and each phase; runs the manual browser checklist; commits when they choose | - |
| ORC | Orchestrator (main session) | Delegates tasks with task IDs; records Git state; records the owner's decisions; records the security agent's returned report; writes the completion report; explains work to the owner | Approves for the owner; stages, commits or pushes |
| PLN | planner-agent | Maintains the SRS, traceability matrix, architecture, schema and this plan; confirms each phase's requirement and TASK IDs | Writes application code |
| DEV | developer-agent | Implements the approved tasks of the current phase; writes the initial tests; runs the relevant checks; writes its change report | Starts without a delegation that cites approval and IDs (§1.5) |
| TST | testing-agent | Independently reviews the tests, adds edge cases, executes the suite, writes its test report | Changes application code (fixes go back to DEV) |
| SEC | security-audit-agent | Strictly read-only security review; returns its full audit report in its final answer | Modifies any file (§1.4) |

### 1.2 The cycle for every phase (FU-4, CON-006)

| Step | What happens | Who |
|---|---|---|
| 1 | Record the initial Git state (`git status --porcelain=v1`, which includes untracked files) and identify pre-existing changes | ORC |
| 2 | Confirm the approved requirements and TASK IDs for the phase; assign the work item ID | PLN confirms, ORC assigns |
| 3 | Implement only the scope of the current phase | DEV |
| 4 | Run the relevant automated checks and record their actual output | DEV |
| 5 | Independently verify the work: review the tests, add edge cases, execute the suite | TST |
| 6 | Review the applicable security risks, read-only (§1.4) | SEC, with ORC's `git status` check |
| 7 | Produce the change report, test report, security report and remaining-issues list; update the traceability matrix | DEV, TST, ORC (records the SEC report), PLN |
| 8 | Give the owner the exact commands to launch the application and verify the GUI | ORC |
| 9 | Summarize what works, what does not, and what the owner should check manually (the completion report, §1.6) | ORC |
| 10 | Stop and wait for the owner's approval before starting the next phase | ORC, Owner |

If TST or SEC find problems, ORC delegates the fixes to DEV as a repeat pass (for example `T-...-DEV-2`), and TST
(and SEC, when security is affected) checks again before steps 8 to 10.

### 1.3 Test responsibilities (OD-11, E8, CON-011)

- DEV writes the initial automated tests together with the code and runs them. These results show that the
  code works for the developer; they are **not** independent verification.
- TST reviews DEV's tests against each requirement's acceptance criteria, adds missing edge cases and executes
  the whole suite. Its test report, with exact commands and actual results, is the phase's test evidence.
- Checks that cannot be automated (appearance, keyboard use, narrow windows) go into the owner's manual
  browser checklist.
- Nobody claims a test passed unless it was executed and its result observed.

### 1.4 Security review: strictly read-only (OD-16 as corrected by the owner, OC-1; DEC-016; CON-012)

- For AgentDesk work, SEC must not modify anything: no application code, no documentation (including its own
  audit report, `docs/security/findings-register.md` and the activity log), no configuration, no global agent
  definitions and no project settings.
- SEC returns its full audit report in its final answer. ORC saves it verbatim to
  `docs/security/audit-reports/<TaskID>.md`, updates the findings register and adds the log entry, each
  labelled "recorded by orchestrator from security-audit-agent's returned report".
- ORC records `git status --porcelain=v1` immediately before and immediately after each security task. Any
  difference counts as a discrepancy and is reported to the owner.
- **Limitation.** SEC's global definition still includes the Write and Edit tools and is not changed. The
  boundary rests on instructions and is checked by Git after the fact; it is not prevented
  (architecture.md §11.1 and §15 item 17).

### 1.5 Delegation, approval and repository rules

- **Developer delegations (E10, CON-013).** Every delegation to developer-agent states: (1) the owner's explicit
  approval it relies on (who, when, what was approved); (2) the approved requirement IDs; (3) the TASK IDs to
  implement. Without all three, the developer does not start. This matches the developer-agent rule against
  creating a new application unless explicitly asked.
- **Planner confirmation.** At the start of each phase PLN confirms the phase's approved requirement IDs and TASK
  IDs (later phases receive TASK IDs at that point) and flags anything unclear before DEV starts.
- **Only the owner approves.** No agent marks a requirement, decision or phase Approved; ORC records the owner's
  decision. Approving a phase is not approval to commit.
- **No automatic Git actions (OD-12, DEC-015, CON-008).** Nobody stages, commits, pushes, deploys or discards
  changes. The owner decides when to commit.
- **Nothing outside this repository** is created or modified during development (CON-009). Phase 4's real-event
  test writes only this repository's own `.claude/settings.local.json`, through the wizard, with the owner's confirmation.
- **No Chrome extension** or other browser automation (OD-2, DEC-014, CON-014). The owner runs a manual browser
  checklist (Appendix A for Phase 1).
- **Global Claude Code settings** are read only by the Phase 4 wizard's configuration check, read-only and
  limited to `disableAllHooks`, hook counts and agent names (OD-13, DEC-017). No phase writes them; no other phase reads them.
- **Task IDs** follow the change-tracking protocol: each phase is one work item `T-YYYYMMDD-NNN`, numbered when it
  starts. Plan tasks are numbered TASK-### and link to requirement IDs in [srs.md](srs.md).
- **Dependencies.** Package versions are fixed (architecture.md §14). The dependency file format is open question
  Q10 (OD-14) and must be decided by the owner before Phase 1 installs anything (TASK-002).

### 1.6 Phase gate: the completion report (OC-2, CON-015)

Each phase ends with a completion report from ORC containing:

1. completion summary;
2. requirement IDs completed and incomplete;
3. files created, modified and deleted (from `git status` and `git diff`, including untracked files);
4. developer change report (which also covers the reporting points of Brief §10);
5. testing report with executed results;
6. security report and unresolved findings;
7. known limitations;
8. exact Windows launch and verification commands;
9. manual browser checklist;
10. Git status, with confirmation that no commits or pushes were made.

Every requirement and check is classified as **Implemented**, **Tested and passed**, **Tested and failed**,
**Not tested** or **Planned for a future phase**. A phase is never called complete while a required acceptance
criterion remains unmet. The activity log, its Summary row and `CHANGELOG.md` are updated, and then the owner decides.

### 1.7 Explanations for the owner (OC-3, CON-016)

After each significant implementation task (in practice, after each developer delegation that adds or changes
application behaviour), ORC gives the owner a short, beginner-friendly explanation covering:

- the files changed;
- what each important file does;
- how the feature flows from the GUI to the backend to the database;
- why this approach was chosen;
- which tests verify it;
- what the owner should understand, including its limits.

## 2. Phase overview

| Phase | Goal | Migrations | Main deliverables | Owner can see |
|---|---|---|---|---|
| 1 | Foundation | `0001` | FastAPI app, security middleware, SQLite + migrations + integrity check + backup and restore, GUI shell, Windows scripts, tests | `scripts\start.bat` opens a working GUI: navigation, theme selection, server health, database status and backup controls; other pages show labelled future-phase placeholders (FU-3) |
| 2 | Dashboard UI | none | Interactive Overview, Agents, Activity, Session and Task views on clearly labelled sample data | Navigation, filters, detail views, themes, keyboard use |
| 3 | Tracking | `0002`-`0004` | Ingestion API, Git checkpoints, wizard steps 1-2, File Change Explorer with live diffs and evidence badges, tracking-file parser, manual report paste; sample data removed | Register a real project and see its real changes and agent reports |
| 4 | Claude Code | `0005` | Hook script, spool, wizard steps 3-5 (check, install, health, disconnect), sessions, subagent runs, OBSERVED evidence | Live agent activity from real Claude Code sessions |
| 5 | Engineering reports | `0006`-`0009` | Documentation (plain text), Testing, Security and Approval centres; file-change reviews; release readiness | Documents, tests, findings, decisions, reviews and readiness |
| 6 | Validation | none | End-to-end, robustness, recovery and security validation | Evidence-based validation report |

## 3. Phase 1: Foundation (TASK-001 to TASK-022)

**Goal (FU-3).** At the end of Phase 1 the owner launches AgentDesk locally with `scripts\start.bat` and uses a
working GUI: navigation, theme selection, server health, database status and backup controls. Every other page
shows a clearly labelled placeholder naming its future phase. Underneath: the foundation security baseline
(localhost-only binding, Host check, CSRF protection for state-changing requests, security headers), migrations,
integrity check, backup and restore, and the Windows setup and start scripts.

**Requirements:** FR-001 to FR-014, NFR-001 to NFR-012 and the constraints CON-001 to CON-016 ([srs.md](srs.md)).

**Out of scope:** projects, the connection wizard, events, hooks, Git tracking, reports, sample data, evidence badges.

**Dependencies:** `fastapi==0.162.0`, `uvicorn==0.54.0`; development only: `pytest==9.2.0`, `httpx==0.28.1`.
The file format is decided by the owner (Q10) in TASK-002, before TASK-003 installs anything.

### 3.1 Task summary

| Task | Title | Role | Requirements | Depends on |
|---|---|---|---|---|
| TASK-001 | Record initial Git state and open the work item | ORC | CON-006, CON-008 | Owner's explicit approval to start Phase 1 |
| TASK-002 | Confirm Phase 1 scope, Q10 and approvals | PLN (Owner decides) | CON-004, CON-006, CON-010, CON-013 | TASK-001 |
| TASK-003 | Repository scaffolding | DEV | FR-001, NFR-011, CON-001, CON-002, CON-004 | TASK-002 |
| TASK-004 | Configuration, logging and time utilities | DEV | NFR-001, NFR-007, NFR-011, CON-007 | TASK-003 |
| TASK-005 | Security middleware | DEV | NFR-002, NFR-003, NFR-004 | TASK-004 |
| TASK-006 | Database connection, migration runner, first migration | DEV | FR-012, CON-005 | TASK-004 |
| TASK-007 | Backup and restore module | DEV | FR-009, FR-010, FR-011 | TASK-006 |
| TASK-008 | System API and response models | DEV | FR-003, FR-008, FR-009, NFR-003 | TASK-005, TASK-007 |
| TASK-009 | Application factory, startup sequence, entry point | DEV | FR-002, FR-010, FR-012, FR-013, NFR-001, NFR-006 | TASK-008 |
| TASK-010 | HTML shell, stylesheet, icon | DEV | FR-005, FR-007, NFR-005, NFR-008, NFR-009, NFR-010 | TASK-003 |
| TASK-011 | Frontend core modules | DEV | FR-004, FR-005, FR-007, NFR-003, NFR-005, NFR-008 | TASK-010 |
| TASK-012 | Pages: placeholders and Settings | DEV | FR-006, FR-008, FR-009, NFR-005, NFR-012 | TASK-008, TASK-011 |
| TASK-013 | Windows setup and start scripts | DEV | FR-001, FR-002, CON-003, CON-009 | TASK-009 |
| TASK-014 | Command-line backup and restore | DEV | FR-011 | TASK-007 |
| TASK-015 | Developer initial tests | DEV | FR-003, FR-005, FR-008 to FR-013, NFR-001 to NFR-004, NFR-006, CON-005, CON-011 | TASK-009, TASK-012, TASK-014 |
| TASK-016 | README and CHANGELOG | DEV | FR-014, NFR-012 | TASK-013, TASK-014 |
| TASK-017 | Developer validation run and change report | DEV | FR-001, FR-002, NFR-002, NFR-003, NFR-011, CON-003, CON-008, CON-009 | TASK-015, TASK-016 |
| TASK-018 | Independent test review, edge cases and execution | TST | FR-001 to FR-014, NFR-001 to NFR-012, CON-005, CON-007, CON-011 | TASK-017 |
| TASK-019 | Read-only security review | SEC (ORC records) | NFR-001 to NFR-007, NFR-011, FR-011, FR-013, CON-001, CON-002, CON-004, CON-009, CON-012 | TASK-018 |
| TASK-020 | Traceability update from saved reports | PLN | All Phase 1 requirements | TASK-019 |
| TASK-021 | Phase 1 completion report and handover | ORC | CON-006, CON-008, CON-014, CON-015, CON-016 | TASK-020 |
| TASK-022 | Owner's manual browser checklist and Phase 1 decision | Owner | FR-002, FR-004 to FR-009, FR-014, NFR-008 to NFR-010, NFR-012, CON-006, CON-010, CON-014 | TASK-021 |

DEV tasks may be delegated together in one or a few developer delegations; each delegation lists its TASK IDs
(§1.5). ORC gives the owner the explanation in §1.7 after each such delegation.

### 3.2 Task details

#### TASK-001 Record initial Git state and open the work item (ORC)

- **Requirements:** CON-006, CON-008. **Depends on:** the owner's explicit approval to start Phase 1.
- **Work:** run `git status --porcelain=v1` (lists untracked files too) and `git log -1 --oneline`; record the
  output as the pre-existing state; assign the work item `T-YYYYMMDD-NNN`; add an "In progress" log entry.
- **Files:** `docs/agent-activity/activity-log.md` (ORC entry and Summary row).
- **Done when:** the pre-existing state and the work item ID are in the activity log.

#### TASK-002 Confirm Phase 1 scope, Q10 and approvals (PLN; the owner decides)

- **Requirements:** CON-004, CON-006, CON-010, CON-013. **Depends on:** TASK-001.
- **Work:** the owner answers Q10 and approves, changes or defers the Phase 1 requirements, these documents and the
  decisions. PLN then sets each approved requirement to Approved with who and when; writes
  `docs/decisions/DEC-###-<slug>.md` only for decisions the owner explicitly approved; baselines the documents
  (next MAJOR version) only if the owner approves a baseline (OD-18); confirms the TASK list; updates the matrix.
- **Files:** `docs/srs.md`, `docs/traceability-matrix.md`, `docs/architecture.md`, `docs/database-schema.md`,
  this plan, approved `docs/decisions/DEC-*.md`, the planner's change report and log entry.
- **Done when:** every Phase 1 requirement carries the owner's decision; Q10 is answered; the developer delegation
  can cite the approval and the IDs.

#### TASK-003 Repository scaffolding (DEV)

- **Requirements:** FR-001, NFR-011, CON-001, CON-002, CON-004. **Depends on:** TASK-002 (including Q10).

| File | Content |
|---|---|
| `.gitignore` | `.venv/`, `data/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.db`, `*.db-wal`, `*.db-shm`, `*.log`, `.claude/settings.local.json` |
| Dependency files (format per Q10; working names from v0.2: `requirements.txt`, `requirements-dev.txt`) | Runtime: `fastapi==0.162.0`, `uvicorn==0.54.0`. Development: the runtime set plus `pytest==9.2.0`, `httpx==0.28.1` |
| `pytest.ini` | `testpaths = tests` |

- **Done when:** the files exist with exactly these entries and no other dependency.

#### TASK-004 Configuration, logging and time utilities (DEV)

- **Requirements:** NFR-001, NFR-007, NFR-011, CON-007. **Depends on:** TASK-003.

| File | Content |
|---|---|
| `app/__init__.py` | `__version__ = "0.1.0"` |
| `app/core/__init__.py`, `app/core/config.py` | Settings from environment: `AGENTDESK_HOST` (default `127.0.0.1`; only `127.0.0.1`, `localhost`, `::1` accepted, anything else stops startup with a clear message), `AGENTDESK_PORT` (default `8765`, range 1024-65535), `AGENTDESK_DATA_DIR` (default `<repo>/data`), `AGENTDESK_LOG_LEVEL` (default `INFO`) |
| `app/core/log_setup.py` | Console logging plus rotating file `data/logs/agentdesk.log` (1 MB x 5). Request bodies and tokens are never logged. |
| `app/core/timeutil.py` | `utc_now_iso()` producing `YYYY-MM-DDTHH:MM:SS.fffZ` |

- **Done when:** an invalid host or port stops startup with a clear message and a non-zero exit; the log rotates as specified.

#### TASK-005 Security middleware (DEV)

- **Requirements:** NFR-002, NFR-003, NFR-004. **Depends on:** TASK-004.

| File | Content |
|---|---|
| `app/core/security.py` | Host allowlist (`127.0.0.1:<port>`, `localhost:<port>`, `[::1]:<port>`; otherwise 400). Security headers: CSP `default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, `Cache-Control: no-store` for `/api`. For POST, PUT, PATCH and DELETE under `/api`: JSON content type (otherwise 415), same-origin or absent `Origin` (otherwise 403), valid `X-AgentDesk-CSRF` token (otherwise 403). Token: 32 random bytes generated at each server start. No CORS headers. |

- **Done when:** the behaviour matches the acceptance criteria of NFR-002 to NFR-004.

#### TASK-006 Database connection, migration runner and first migration (DEV)

- **Requirements:** FR-012, CON-005. **Depends on:** TASK-004.

| File | Content |
|---|---|
| `app/database/__init__.py`, `app/database/connection.py` | `connect()`: `timeout=5`, explicit transactions, `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`, row factory. `transaction()` context manager (BEGIN IMMEDIATE, COMMIT, ROLLBACK on error). One connection per request through a FastAPI dependency. |
| `app/database/migrations.py` | Creates `schema_migrations` if missing. Discovers `migrations/NNNN_<name>.sql` (strict file-name pattern; other files are ignored with a log warning). Verifies the checksums of applied migrations; a mismatch stops startup with a message naming the file. Reports whether migrations are pending (the startup sequence in TASK-009 takes the backup first). Applies each pending file in its own transaction and records version, name, checksum and time. |
| `migrations/0001_foundation.sql` | The `app_settings` table, exactly as in [database-schema.md](database-schema.md) §3 |

- **Done when:** FR-012 criteria 1 to 5 and CON-005 are met.

#### TASK-007 Backup and restore module (DEV)

- **Requirements:** FR-009, FR-010, FR-011. **Depends on:** TASK-006.

| File | Content |
|---|---|
| `app/database/backup.py` | `create_backup(reason)` with the SQLite online backup API into `data/backups/agentdesk-YYYYMMDD-HHMMSS-<reason>.db` (reasons `manual`, `startup`, `pre-migration`). Runs `PRAGMA integrity_check` on the copy. Keeps the newest 10 `agentdesk-*.db` files and never touches other files. `list_backups()`. `restore_backup(name)` (offline only): accepts only a file name inside `data/backups/`, checks the candidate's integrity, moves the current database to `data/backups/pre-restore-<time>.db`, copies the candidate in. |

- **Done when:** the functions behave as FR-010 criteria 3-4 and FR-011 criteria 4-5 require.

#### TASK-008 System API and response models (DEV)

- **Requirements:** FR-003, FR-008, FR-009, NFR-003. **Depends on:** TASK-005, TASK-007.

| File | Content |
|---|---|
| `app/models/__init__.py`, `app/models/system.py` | Pydantic response models: health, system information, backup information |
| `app/api/__init__.py`, `app/api/system.py` | `GET /api/v1/health` (status, version, uptime). `GET /api/v1/system` (version, Python and SQLite versions, data folder, database size, schema version and applied migrations, last backup, integrity result and time, instance id). `GET /api/v1/session` (CSRF token). `GET /api/v1/system/backups` (list). `POST /api/v1/system/backups` (create a manual backup; CSRF-protected). |

- **Done when:** every endpoint returns the documented fields; the POST is refused without a valid token.

#### TASK-009 Application factory, startup sequence and entry point (DEV)

- **Requirements:** FR-002, FR-010, FR-012, FR-013, NFR-001, NFR-006. **Depends on:** TASK-008.

| File | Content |
|---|---|
| `app/main.py` | `create_app(settings)` factory. Startup sequence: create data folders → if the database exists, run `PRAGMA quick_check` (on failure: log, refuse to start with restore instructions, leave the file untouched) → at most one backup: `pre-migration` if migrations are pending on an existing database, otherwise `startup` if the database existed and the newest backup is missing or over 24 hours old → migrations → ensure `instance_id` and `created_at` → generate the CSRF token. Serves `index.html` at `/` and the static files. Unknown `/api` paths return JSON 404. Unhandled errors return JSON without stack traces. |
| `app/__main__.py` | `python -m app [--open]`: validates settings, prints the URL, runs uvicorn on the configured loopback host and port (no auto-reload). With `--open`, opens the browser once the server is ready. |

- **Done when:** `python -m app` starts on 127.0.0.1:8765; a damaged database stops startup unchanged; errors are JSON without stack traces.

#### TASK-010 HTML shell, stylesheet and icon (DEV)

- **Requirements:** FR-005, FR-007, NFR-005, NFR-008, NFR-009, NFR-010. **Depends on:** TASK-003.

| File | Content |
|---|---|
| `app/static/index.html` | Skip link. Header: name, server status indicator, theme control. Navigation with 11 entries: Overview, Projects, Agents, Activity, File changes, Reports, Documents, Testing, Security, Approvals, Settings. Main region; polite live region for status messages; `<noscript>` notice. Loads `js/app.js` as a module. No inline scripts or styles (CSP). (The project selector arrives with projects in Phase 3.) |
| `app/static/css/app.css` | Design tokens for light and dark (via `data-theme` and `prefers-color-scheme`); type and spacing scales; layout (sidebar at 960 px and wider, top menu below); buttons, cards, tables, status pills; empty, loading and error states; visible focus; `prefers-reduced-motion`; WCAG AA contrast. (Evidence and verification badges arrive in Phase 2, task 2.1.) |
| `app/static/favicon.svg` | Simple monochrome icon |

- **Done when:** the page loads with no CSP violation; layout and focus behave as NFR-008 to NFR-010 require.

#### TASK-011 Frontend core modules (DEV)

- **Requirements:** FR-004, FR-005, FR-007, NFR-003, NFR-005, NFR-008. **Depends on:** TASK-010.

| File | Content |
|---|---|
| `app/static/js/app.js` | Boot: theme, router, server health polling every 10 s while the tab is visible, shown in the header as "Server OK" or "Server unreachable" (text plus icon) |
| `app/static/js/router.js` | Hash routes with `:params` and query strings; not-found view; updates the page title and `aria-current`; moves focus to the page heading after navigation |
| `app/static/js/api.js` | Fetch wrapper: JSON, 10 s timeout, CSRF header on state-changing requests (token from `GET /api/v1/session`; after a server restart the old token is refused, so on a CSRF 403 it fetches a new token and retries once), uniform error objects |
| `app/static/js/dom.js` | `h(tag, attributes, ...children)` element builder using `textContent` (never raw HTML with data); formatters for local time and byte sizes |
| `app/static/js/theme.js` | Light, dark or follow-system, remembered in `localStorage` |

- **Done when:** FR-004, FR-005 and FR-007 work in the browser; no module inserts data as HTML.

#### TASK-012 Pages: placeholders and Settings (DEV)

- **Requirements:** FR-006, FR-008, FR-009, NFR-005, NFR-012. **Depends on:** TASK-008, TASK-011.

| File | Content |
|---|---|
| `app/static/js/pages/placeholder.js` | One module for the 10 placeholder pages, driven by a small table of title, one-sentence purpose and phase text (below). Later phases replace entries with real page modules. |
| `app/static/js/pages/settings.js` | Functional Settings page: version, Python and SQLite versions, schema version and applied migrations, database size, data folder, integrity result and time, last backup, backup list, "Create backup now" (result announced in the live region). No owner-name field (E3). |

| Page | Placeholder text names |
|---|---|
| Overview | Phase 2 (preview layout), real data from Phase 3 |
| Projects | Phase 3 |
| Agents | Phase 2 (preview), live data in Phase 4 |
| Activity | Phase 2 (preview), real data from Phase 3 |
| File changes | Phase 3 |
| Reports | Phase 3 |
| Documents | Phase 5 |
| Testing | Phase 5 |
| Security | Phase 5 |
| Approvals | Phase 5 |

- **Done when:** every page renders; placeholders show no numbers or sample data; Settings shows real values.

#### TASK-013 Windows setup and start scripts (DEV)

- **Requirements:** FR-001, FR-002, CON-003, CON-009. **Depends on:** TASK-009.

| File | Content |
|---|---|
| `scripts/setup.bat` | Checks that `python` is 3.12 or newer (clear guidance otherwise); creates `.venv` if missing; installs the runtime dependencies; `setup.bat dev` also installs the development dependencies. Changes nothing outside the repository. |
| `scripts/start.bat` | Stops with "run scripts\setup.bat first" if `.venv` is missing; runs `.venv\Scripts\python -m app --open` |

- **Done when:** FR-001 and FR-002 acceptance criteria are met on the owner's PC.

#### TASK-014 Command-line backup and restore (DEV)

- **Requirements:** FR-011. **Depends on:** TASK-007.

| File | Content |
|---|---|
| `scripts/backup_db.py` | `create` and `list` backups |
| `scripts/restore_db.py` | `list` and `restore <file>`. Refuses while AgentDesk is running (port in use); asks the user to type `RESTORE`; accepts only names inside `data/backups/`; keeps the current database as `pre-restore-<time>.db` |

- **Done when:** FR-011 acceptance criteria are met.

#### TASK-015 Developer initial tests (DEV)

- **Requirements:** FR-003, FR-005, FR-008 to FR-013, NFR-001 to NFR-004, NFR-006, CON-005, CON-011.
  **Depends on:** TASK-009, TASK-012, TASK-014.

| File | Checks |
|---|---|
| `tests/conftest.py` | Temporary data folder per test; app built with `create_app()`; test client using base URL `http://127.0.0.1:8765` |
| `tests/test_health.py` | `/api/v1/health` returns 200 with the version |
| `tests/test_config.py` | Non-loopback host refused; out-of-range port refused; defaults correct |
| `tests/test_security.py` | Wrong Host header → 400; security headers on HTML and API responses; POST without CSRF token → 403; foreign `Origin` → 403; non-JSON content type → 415; valid request → 2xx; no CORS header |
| `tests/test_migrations.py` | New database reaches schema version 1 with only `schema_migrations` and `app_settings`; a second start changes nothing; an edited applied migration stops startup; a failing migration is rolled back and not recorded; a backup is taken before migrating an existing database |
| `tests/test_backup_restore.py` | A backup file is created and passes the integrity check; only the newest 10 are kept and other files are untouched; restore brings back earlier data and keeps the replaced database as `pre-restore-*`; a name outside `data/backups/` is refused |
| `tests/test_integrity.py` | A corrupted database file stops startup, and the file is left byte-for-byte unchanged |
| `tests/test_static.py` | `/` serves `index.html`; every JavaScript module it references is served with a JavaScript MIME type; unknown `/api` path returns JSON 404; `GET /api/v1/system` returns every field FR-008 lists |

- **Done when:** `.venv\Scripts\python -m pytest -v` has been run and its actual output is in the change report.
  These results are the developer's own; they are not independent verification (OD-11).

#### TASK-016 README and CHANGELOG (DEV)

- **Requirements:** FR-014, NFR-012. **Depends on:** TASK-013, TASK-014.

| File | Content |
|---|---|
| `README.md` (modify) | What AgentDesk is; requirements (Windows 11, Python 3.12+, Git); setup; start; running tests; folder layout; where data lives; backup and restore; security notes (local only, never expose it); current phase and its limits |
| `CHANGELOG.md` (modify) | Phase 1 entries under `[Unreleased]`, tagged with the task ID |

- **Done when:** FR-014 acceptance criteria are met.

#### TASK-017 Developer validation run and change report (DEV)

- **Requirements:** FR-001, FR-002, NFR-002, NFR-003, NFR-011, CON-003, CON-008, CON-009.
  **Depends on:** TASK-015, TASK-016.

| # | Check | Pass condition |
|---|---|---|
| V1 | `scripts\setup.bat dev` on a fresh `.venv` | Completes; output recorded |
| V2 | `.venv\Scripts\python -m pytest -v` | Real counts recorded; failures reported as they are |
| V3 | Start with `scripts\start.bat`, then `curl.exe` | `/api/v1/health` → 200; `Host: evil.example` → 400; POST backup without token → 403 |
| V4 | Data check after two starts | `data/agentdesk.db` exists; `schema_migrations` holds version 1 only; a `startup` backup exists and passes the integrity check |
| V5 | `git status --porcelain=v1` | Only the expected files are new or modified; `data/` and `.venv/` are ignored; nothing staged or committed |

- **Files:** `docs/agent-activity/change-reports/<TaskID>.md`, the DEV entry in `docs/agent-activity/activity-log.md`.
- **Done when:** the change report (from the template) has the file table from `git status` and `git diff`, the
  reporting points of Brief §10, the owner's approval and IDs it relied on (CON-013), and V1 to V5 with actual results.

#### TASK-018 Independent test review, edge cases and execution (TST)

- **Requirements:** FR-001 to FR-014, NFR-001 to NFR-012, CON-005, CON-007, CON-011. **Depends on:** TASK-017.
- **Work:**
  - Review DEV's tests against every Phase 1 acceptance criterion.
  - Add missing edge cases, for example: a CSRF token from an earlier server run; `Origin: null`; Host
    `[::1]:8765`; ports 1023, 1024, 65535 and 65536; backup retention with more than 10 backups plus foreign files
    in the folder; a restore name containing `..`; a migration file with a wrong name; an empty database file.
  - Execute the whole suite.
  - Check by inspection what can be inspected (no inline scripts, no `innerHTML` with data, contrast of the design
    tokens) and list the rest for the owner's checklist.
- **Files:** new or extended tests under `tests/`; `docs/testing/test-reports/<TaskID>.md`; TST log entry.
- **Done when:** the test report has exact commands, exit codes and actual counts; every Phase 1 requirement is
  mapped to tests or to an Appendix A step; failures are reported for a DEV repeat pass.

#### TASK-019 Read-only security review (SEC; ORC records)

- **Requirements:** NFR-001 to NFR-007, NFR-011, FR-011, FR-013, CON-001, CON-002, CON-004, CON-009, CON-012.
  **Depends on:** TASK-018 and any DEV repeat passes.
- **Scope:** loopback binding and configuration checks; Host check; CSRF and `Origin` handling; security headers and
  CSP; no inline scripts or unsafe DOM use; error responses and log content; backup and restore path handling;
  startup integrity behaviour; scripts writing only inside the repository; dependencies limited to the pinned set.
- **Procedure (§1.4):**
  1. ORC records `git status --porcelain=v1` immediately before delegating.
  2. SEC reviews read-only and modifies no file. It returns its full audit report (findings with severity,
     location and remediation; a deployment-readiness note) in its final answer.
  3. ORC records `git status --porcelain=v1` immediately afterwards. Any difference is a discrepancy, reported to the owner.
  4. ORC saves the report verbatim to `docs/security/audit-reports/<TaskID>.md`, updates
     `docs/security/findings-register.md` and adds the log entry, each labelled "recorded by orchestrator from
     security-audit-agent's returned report".
- **Files:** none written by SEC. ORC writes the three records in step 4.
- **Done when:** the report, both `git status` outputs and their comparison are recorded; findings are in the
  register; Critical or High findings are put to the owner (DEV fix pass or a recorded risk acceptance) before TASK-021.

#### TASK-020 Traceability update from saved reports (PLN)

- **Requirements:** all Phase 1 requirements. **Depends on:** TASK-019.
- **Work:** fill the Implementation, Tests and Security findings columns of
  [traceability-matrix.md](traceability-matrix.md) from the saved DEV, TST and SEC reports only.
- **Files:** `docs/traceability-matrix.md`; planner change report and log entry.
- **Done when:** every Phase 1 row is filled, or shows `-` with the reason in the planner's report.

#### TASK-021 Phase 1 completion report and handover (ORC)

- **Requirements:** CON-006, CON-008, CON-014, CON-015, CON-016. **Depends on:** TASK-020.
- **Work:** the completion report with all 10 items of §1.6 and the result classification for every Phase 1
  requirement; the launch and verification commands:

  ```bat
  cd /d D:\agentdesk
  scripts\setup.bat dev
  .venv\Scripts\python -m pytest -v
  scripts\start.bat
  ```

  the Appendix A checklist; `git status` with confirmation that no commits or pushes were made; the Summary row.
- **Done when:** the report is delivered with no item missing and no claim beyond the recorded results.

#### TASK-022 Owner's manual browser checklist and Phase 1 decision (Owner)

- **Requirements:** FR-002, FR-004 to FR-009, FR-014, NFR-008 to NFR-010, NFR-012, CON-006, CON-010, CON-014.
  **Depends on:** TASK-021.
- **Work:** run Appendix A and return Pass, Fail or Notes for each step; then approve Phase 1, ask for fixes, or
  defer items.
- **Done when:** the checklist is returned and ORC has recorded the owner's decision.

**Phase 1 is complete only when** every Must requirement of Phase 1 is "Tested and passed" (or the owner has
explicitly deferred it), the completion report is delivered, and the owner approves (§1.6).

## 4. Phase 2: Dashboard UI (preview data)

| # | Task | Acceptance |
|---|---|---|
| 2.1 | Finish the design system: evidence and verification badges, status pills, tables, loading, empty and error states | Every state renders in light and dark themes with AA contrast |
| 2.2 | Router: breadcrumbs, URL-held filters, not-found handling, focus management | Back and Forward restore filters and position |
| 2.3 | Data layer `js/data.js` with a preview fixture `static/preview/sample.json`; preview toggle in Settings (off by default); a fixed "SAMPLE DATA, not real activity" banner on every page while it is on | No sample value can appear without the banner; with preview off, honest empty states |
| 2.4 | Overview: tiles linking to filtered lists; agents, activity and file-change panels | Every tile and row navigates somewhere meaningful |
| 2.5 | Agents list and agent detail | Status "Never seen" when there is no activity; profile existence never implies activity |
| 2.6 | Activity timeline with filters; event, session and task detail views | All filters combine; every ID links to its view |
| 2.7 | Accessibility and responsive pass | Keyboard-only walkthrough and a 400 px width check, recorded in the report |

Tests: static asset tests extended; a manual UI checklist with recorded results (no JavaScript test framework, to stay lightweight).

## 5. Phase 3: Tracking

| # | Task | Acceptance |
|---|---|---|
| 3.1 | Migration `0002`; project and event data access | Migration tests extended |
| 3.2 | Redaction module; event validation; `POST /api/v1/events` (generic structured events, ingest token or CSRF) | Malformed, oversized, wrong-type and duplicate events rejected or deduplicated with clear errors |
| 3.3 | Safe Git runner (read-only allowlist, hardened flags, timeouts) and parsers (`status --porcelain=v2 -z`, `diff --numstat -z`, `hash-object` without `-w`) | Unit tests on recorded Git outputs, including unusual file names |
| 3.4 | Migration `0003`; checkpoint service; "Refresh from Git" | Checkpoints match Git in temporary test repositories |
| 3.5 | Wizard steps 1-2: folder browser API (folder names only), path validation with the refused-folder list (architecture §7, E6, OD-17), Git detection with the Git root rule, registration with a baseline checkpoint | Drive roots, `C:\Users`, user-profile roots, Windows and program folders and AgentDesk's data folder refused, also through junctions, `..` and letter case; a folder whose Git root is refused is registered as "Not a Git repository" and no Git command runs for it; nothing written to the project |
| 3.6 | File Change Explorer: list with badges, window selector, file detail with live unified or split diff, sensitive-file refusal (including AgentDesk's data folder), size caps, binary handling | Correct badges for added, modified, deleted, untracked, binary, staged rename and pre-existing cases |
| 3.7 | Migration `0004`; tracking-file parser (activity log, change reports); Reports page with paste form (preview, then save); cross-check flags | Parser tests on template-format fixtures and malformed files; "reported, not found in Git" and "Git change not reported" flags shown |
| 3.8 | Evidence classification service (rules R-A to R-F, computed on read) | One test per rule, including "changed during a session but no observed event → UNATTRIBUTED" |
| 3.9 | Remove sample data from operational views (delete the fixture and toggle; test fixtures stay under `tests/`) | No sample data reachable in the running app |

## 6. Phase 4: Claude Code integration

| # | Task | Acceptance |
|---|---|---|
| 4.1 | `hooks/agentdesk_hook.py` (standard library only): sanitize, post, spool; ingest token | Exits 0 and prints nothing when the server is down, the token is wrong, stdin is malformed, empty or oversized |
| 4.2 | Migration `0005`; mapping of each hook event to events, sessions and tasks; task ID extraction; SubagentStop excerpt of at most 1,024 characters (DEC-008) | Unit tests with recorded payload shapes; a longer final message is stored as 1,024 characters and the database refuses more |
| 4.3 | Spool replay; idle, stale and unknown detection | Events captured while AgentDesk was stopped appear after restart, without duplicates |
| 4.4 | Wizard steps 3-5: configuration inspector (read-only; the only code that reads `~/.claude/`, limited to `disableAllHooks`, hook counts and agent names, OD-13), merge planner (preview diff and hash), apply with backup and atomic write after typed-name confirmation, self-test, health states, disconnect | Existing hooks and settings preserved exactly; invalid JSON refused; a file changed after preview aborts the install; disconnect removes only AgentDesk's entries; no other module reads `~/.claude/` |
| 4.5 | OBSERVED evidence; "observed, not in that agent's report" flag; SubagentStop report linking | Evidence tests extended |
| 4.6 | Agents, sessions and Overview pages on live data | Real counts only |
| 4.7 | **Real-event verification**: connect this repository through the wizard (writes only `D:\agentdesk\.claude\settings.local.json`, with owner confirmation), run a real Claude Code session that starts a subagent, and record the sanitized payload shapes actually received. Repeat with AgentDesk stopped (spool), then restarted (replay). | Report quotes the actual events received; any documented field that did not appear is listed as a finding |
| 4.8 | Automatic checkpoint scheduling with the rate limit (architecture §6.6, E7): at most one automatic checkpoint per project per 10 seconds, one trailing checkpoint per window, baselines always taken; simple in-process timer | 20 Stop events within 10 seconds give one immediate and one trailing checkpoint; registration and SessionStart checkpoints are taken at once inside a window |

## 7. Phase 5: Engineering reports

| # | Task | Acceptance |
|---|---|---|
| 5.1 | Migration `0006`; Documentation Centre: discovery, types, documents shown as escaped plain text (monospace, wrapped; no Markdown renderer, DEC-010), metadata panel (type, declared version and status, live Git history, approval state), requirements index (Could) | A document containing HTML, `<script>` or `javascript:` links shows them as literal text and creates no elements; Mermaid blocks appear as source |
| 5.2 | Migration `0007`; Testing Centre: test-report parser, observed test commands, Proposed vs Executed; test-runner file import (size-capped, Could) with the verification rule (architecture §10.3, E1) | The database refuses a proposed test linked to a run, a source/verification mismatch, and `verified` without an observed command; a file with no matching command is labelled "Test-runner file, origin not verified"; a reported run without a matching observed command is flagged |
| 5.3 | Migration `0008`; Security Centre: findings register and audit report parsers, severity summary, verdict display, finding detail | Statuses match the register's wording; "never declared secure" notice always present |
| 5.4 | Migration `0009`; Approval Centre: review-request generation, decision form with typed name (no Windows account name), immutable history, outdated-approval detection, "Copy decision"; file-change reviews in the File Change Explorer (E2) | Database triggers block edits and deletes of decided approvals; AgentDesk cannot be recorded as the decider; a review keeps the evidence label unchanged and shows as outdated after the file changes; a deleted-file review is pinned to `deleted@<commit>` |
| 5.5 | Overview: release readiness, testing and security summaries | Readiness never shows ready without a human release approval; only `verified` and `observed` test runs clear the tests blocker; UNATTRIBUTED changes block until accepted for their current version |

## 8. Phase 6: Validation

| # | Area | Method |
|---|---|---|
| 6.1 | Complete application | End-to-end walkthrough on a sample project with all four agents |
| 6.2 | Malformed events | Generated invalid, oversized, deeply nested and wrongly typed payloads against the ingestion endpoints and the hook script |
| 6.3 | Multiple projects | Three registered projects, events routed correctly, cross-project isolation of file access |
| 6.4 | Concurrent sessions | Parallel event ingestion from several threads and sessions; no lost or duplicated events, no database lock errors |
| 6.5 | Windows startup | Fresh clone → `setup.bat` → `start.bat` on this machine |
| 6.6 | Git tracking | Scenario suite: renames, deletes, binaries, large files, unusual names, commits during a session, non-Git folders |
| 6.7 | Database recovery | Corrupted database → refusal → restore from backup; failed migration → rollback |
| 6.8 | Security and permissions | Strictly read-only `security-audit-agent` review (§1.4, report recorded by ORC, `git status` compared before and after), plus checks for path traversal, CSRF, Host header, sensitive-file refusal, refused folders, and confirmation that nothing outside the registered projects is ever written |

## 9. Reporting and records

| Record | Location | When |
|---|---|---|
| Completion report (§1.6) | Conversation | End of each phase |
| Owner explanation (§1.7) | Conversation | After each significant developer delegation |
| Development report (Brief §10 points) | Change report | Each implementation task |
| Change report | `docs/agent-activity/change-reports/<TaskID>.md` | Each planner and developer task |
| Activity log entry and Summary row | `docs/agent-activity/activity-log.md` | Each task and each owner decision |
| Changelog | `CHANGELOG.md` (`[Unreleased]`) | User-visible changes |
| SRS and traceability matrix | `docs/srs.md`, `docs/traceability-matrix.md` | Maintained by PLN; matrix updated from saved reports at each phase end |
| Decision records | `docs/decisions/DEC-###-<slug>.md` | Only after the owner explicitly approves: design decisions, requirement changes, risk acceptances, validation waivers |
| Test reports | `docs/testing/test-reports/` | Written by TST |
| Audit reports, findings register | `docs/security/` | Recorded by ORC from the security agent's returned report (§1.4) |

## Appendix A. Phase 1 manual browser verification checklist

Run by the owner (TASK-022; OD-2, CON-014). No browser automation. Before starting, `scripts\setup.bat` must have
been run once (TASK-017 does this). Use a desktop browser on the same PC. Write Pass or Fail for each step, and
notes for anything unexpected.

| # | Step | Expected result | Pass/Fail | Notes |
|---|---|---|---|---|
| 1 | Open Command Prompt, run `cd /d D:\agentdesk`, then `scripts\start.bat` | The window shows the address http://127.0.0.1:8765 and the browser opens it | | |
| 2 | Look at the page (or open http://127.0.0.1:8765 yourself) | AgentDesk header, 11 navigation entries, the header shows "Server OK" | | |
| 3 | Click **Overview** | Title, one-sentence purpose, placeholder naming Phase 2 (preview layout) and real data from Phase 3; no numbers | | |
| 4 | Click **Projects** | Placeholder naming Phase 3; no data | | |
| 5 | Click **Agents** | Placeholder naming Phase 2 (preview) and live data in Phase 4; no data | | |
| 6 | Click **Activity** | Placeholder naming Phase 2 (preview) and real data from Phase 3; no data | | |
| 7 | Click **File changes** | Placeholder naming Phase 3; no data | | |
| 8 | Click **Reports** | Placeholder naming Phase 3; no data | | |
| 9 | Click **Documents** | Placeholder naming Phase 5; no data | | |
| 10 | Click **Testing** | Placeholder naming Phase 5; no data | | |
| 11 | Click **Security** | Placeholder naming Phase 5; no data | | |
| 12 | Click **Approvals** | Placeholder naming Phase 5; no data | | |
| 13 | Click **Settings** | Shows version 0.1.0, schema version 1, the database size, integrity "OK" and the backup list; no owner-name field | | |
| 14 | Click **Create backup now** | A success message appears and a new entry (reason "manual", current time) is added to the list without reloading | | |
| 15 | Choose the **Light** theme, then press F5 | The page is still light after reloading | | |
| 16 | Choose **Dark**, then press F5 | The page is still dark | | |
| 17 | Choose **System**, then press F5 | The page follows the Windows colour setting (Settings > Personalization > Colors) | | |
| 18 | In both light and dark, read the header, navigation and Settings | Text is clearly readable; the server status shows text and an icon, not colour alone | | |
| 19 | Reload, then press Tab once | A "Skip to main content" link appears; pressing Enter moves focus to the main content | | |
| 20 | Keep pressing Tab through the navigation | Each entry gets a visible focus outline, in order | | |
| 21 | With **Testing** focused, press Enter | The Testing page opens and focus is on its page heading | | |
| 22 | Make the window about 400 px wide (or press F12, then Ctrl+Shift+M, and set the width to 400) | Navigation becomes a top menu; no horizontal scrolling on Overview and Settings; all text and buttons usable | | |
| 23 | In the Command Prompt window press Ctrl+C (answer Y if asked "Terminate batch job"), then wait | Within about 10 seconds the header shows "Server unreachable" | | |
| 24 | Run `scripts\start.bat` again, then go back to the first browser tab | Within about 10 seconds the header returns to "Server OK", without reloading | | |
| 25 | Open http://localhost:8765 | The app loads, shows "Server OK", and Settings shows data | | |
| 26 | Open http://127.0.0.1:8765/#/no-such-page | "Page not found" with a link to Overview | | |
| 27 | Open `README.md` | Setup, start, backup and restore instructions are understandable | | |
