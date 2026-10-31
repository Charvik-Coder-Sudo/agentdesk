# AgentDesk: implementation plan

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Draft (revision 1.1 of the 1.0 baseline: corrective tasks TASK-093 to TASK-098 and DEC-022 Amendment 1, pending recording; the 1.0 baseline stays in force) |
| Last updated | 2026-10-31 |
| Task ID | T-20261030-002-PLN (previous: T-20261030-001-PLN-2; maintained by planner-agent, OD-10) |
| Related documents | [srs.md](srs.md), [architecture.md](architecture.md), [database-schema.md](database-schema.md), [traceability-matrix.md](traceability-matrix.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-ORC | Six-phase plan, presented in conversation | - | Accepted in principle by the project owner |
| 0.2 | 2026-10-30 | T-20261030-001-ORC | Refinements R1-R12: phased migrations, Connection Wizard split across Phases 3-4, evidence model, manual reports, tracking-file ingestion, interactive detail views; exact Phase 1 checklist | R1-R12 | Pending |
| 0.3 | 2026-10-30 | T-20261030-001-PLN | Status Draft (E4, OD-18). §1 rewritten: Option B (OD-1), 10-step phase cycle (FU-4), test responsibilities (OD-11, E8), strictly read-only security review with `git status` check (OD-16 as corrected by OC-1), developer delegations cite approval and IDs (E10), Planner confirms each phase, no automatic Git actions (OD-12), no Chrome extension (OD-2), completion report contents (OC-2), beginner explanations (OC-3), dependency format open (Q10, OD-14). §3: Phase 1 checklist A-H turned into TASK-001 to TASK-022 linked to requirement IDs (E9); evidence badges and project selector moved out of Phase 1; one placeholder module instead of ten. New Appendix A: manual browser checklist (E5). Phases 3-6 updated for E1, E2, E6, E7, OD-4, OD-6, OD-13. | E1, E2, E4-E10; OD-1, OD-2, OD-4, OD-6, OD-11 to OD-14, OD-16; OC-1 to OC-3; FR-001 to FR-014, NFR-001 to NFR-012, CON-001 to CON-016 | Pending |
| 1.0 | 2026-10-30 | T-20261030-001-PLN-2 | Baseline. §1: 13-step continuous improvement cycle replaces the 10-step cycle and the owner gates between phases (DEC-020); internal verification gate, finding triage, standard phase tasks, final acceptance and 12-item final report (new §1.8, §1.9; DEC-021). §3: Phase 1 technical content unchanged; TASK-002 done, Q10 closed (DEC-018), TASK-020/021 reworded for the cycle, TASK-022 superseded by TASK-092. §4-§8: Phases 2-6 broken into TASK-023 to TASK-092. Real-event check in `.sandbox/` (DEC-023); JavaScript checks with Node (DEC-022). New Appendix B (later-phase manual checks, compiled in TASK-089). | All; CON-004, CON-006, CON-008, CON-010, CON-014, CON-015, CON-017 to CON-019, FR-063 to FR-067, NFR-023 | The owner, 2026-10-30 (blanket authorization, OA); DEC-018, DEC-019, DEC-022, DEC-023 under the owner's delegated authority |
| 1.1 | 2026-10-31 | T-20261030-002-PLN | Phase 1 triage (cycle step 7). New §3.3: corrective tasks TASK-093 to TASK-098 for D-1 to D-3, SEC-001 to SEC-009, SEC-011 to SEC-015 and the cheap TST and DEV observations. Phase 1 gate check recorded as not met (§3 status). §1.3 and TASK-024: JavaScript syntax check in module mode with a negative control (DEC-022 Amendment 1). §1.4: SEC writes no file anywhere. §1.6: triage classes Hardening, Accepted with justification and Owner action. TASK-025: theme applied before first paint (rescheduled DEV observation). Phase 3 and TASK-038, TASK-048: owner-only ingest token (new NFR-024, Proposed, DEC-024). | FR-001 to FR-014, NFR-001 to NFR-012, NFR-024 (new, Proposed), CON-002, CON-009, CON-011, CON-019; DEC-022, DEC-024, DEC-025 | Pending user approval (corrective tasks for Approved requirements fall under OA, §1.6; DEC-022 Amendment 1, DEC-024 and DEC-025 are Proposed) |

## 1. Working rules

### 1.1 Execution model: Option B (OD-1, DEC-013)

The owner chose Option B. The main session orchestrates; each agent does its own part with a role task ID
(`-PLN`, `-DEV`, `-TST`, `-SEC`). On 2026-10-30 the owner authorized all phases at once (OA, DEC-020): phases run
one after another through the cycle in §1.2 without phase-by-phase approval. The owner remains the final
decision-maker: one manual checklist and decision at the end (TASK-092), plus the few decisions in §1.6.

| Role | Who | Does | Never does |
|---|---|---|---|
| Owner | The project owner | Gave the blanket authorization (OA); decides the items listed in §1.6 when they arise; runs the consolidated manual browser checklist and makes the final decision once (TASK-092); commits when they choose | - |
| ORC | Orchestrator (main session) | Delegates tasks with task IDs; records Git state; records the owner's decisions; records the security agent's returned report; collects findings; writes the phase completion summaries and the final report; explains work to the owner | Approves for the owner; stages, commits or pushes |
| PLN | planner-agent | Maintains the SRS, traceability matrix, architecture, schema and this plan; creates and confirms each phase's tasks; classifies findings and assigns corrective tasks; runs the phase gate check | Writes application code |
| DEV | developer-agent | Implements the approved tasks of the current phase; writes the initial tests; runs the relevant checks; writes its change report | Starts without a delegation that cites approval and IDs (§1.5) |
| TST | testing-agent | Independently reviews the tests, adds edge cases, executes the suite, writes its test report | Changes application code (fixes go back to DEV) |
| SEC | security-audit-agent | Strictly read-only security review; returns its full audit report in its final answer | Modifies any file (§1.4) |

### 1.2 The continuous improvement cycle for every phase (OA, DEC-020, CON-006)

The owner's 13 steps apply to every phase and to every significant feature. Step texts are the owner's wording.

| Step | What happens | Who | Record |
|---|---|---|---|
| 1 | Planner reviews requirements and creates tasks. (ORC first records the initial Git state with `git status --porcelain=v1`, identifies pre-existing changes and opens the work item.) | PLN; ORC | Phase-start task; PLN change report |
| 2 | Developer implements the approved scope. | DEV | Code, initial tests |
| 3 | Developer runs initial checks and tests. | DEV | DEV change report with actual output |
| 4 | Testing Agent independently reviews, adds tests, and runs them. | TST | Test report |
| 5 | Security Audit Agent performs an independent read-only audit (§1.4). | SEC; ORC records | Audit report, findings register, both `git status` outputs |
| 6 | Collect all implementation, testing, and security findings. | ORC | List handed to PLN |
| 7 | Planner classifies findings and assigns corrective tasks (§1.6). | PLN | Triage table in the PLN change report |
| 8 | Developer fixes confirmed issues. | DEV (repeat pass, e.g. `T-...-DEV-2`) | DEV change report |
| 9 | Testing Agent reruns relevant tests and the full regression suite. | TST (repeat pass) | Test report |
| 10 | Security Audit Agent rechecks affected security findings. | SEC (repeat pass); ORC records | Audit report, register update |
| 11 | Repeat the cycle until the phase satisfies its acceptance criteria. | ORC, PLN | Gate check (§1.6) |
| 12 | Update traceability, reports, changelog, and documentation. | PLN (matrix), DEV (CHANGELOG, README), ORC (Summary row, completion summary) | Matrix, CHANGELOG, completion summary |
| 13 | Automatically proceed to the next phase. | ORC | Next phase-start task |

Steps 7 to 10 repeat until the gate in §1.6 is met. Each repeat pass gets the next role-task suffix
(`-DEV-2`, `-TST-2`, `-SEC-2`, `-PLN-3`, ...). Nobody waits for the owner between phases.

### 1.3 Test responsibilities (OD-11, E8, CON-011)

- DEV writes the initial automated tests together with the code and runs them. These results show that the
  code works for the developer; they are **not** independent verification.
- TST reviews DEV's tests against each requirement's acceptance criteria, adds missing edge cases and executes
  the whole suite. Its test report, with exact commands and actual results, is the phase's test evidence.
- GUI behaviour is checked automatically through HTTP/API and static-file tests (CON-014). Checks that cannot
  be automated (appearance, keyboard use, narrow windows) are listed in the TST report and collected into
  Appendix B, which the owner runs once at final acceptance with Appendix A.
- Nobody claims a test passed unless it was executed and its result observed.
- **Verification integrity (CON-019).** A task is never complete because code was written. Tests are never
  hidden, removed, suppressed, skipped or weakened to make a run pass; a test changes only with a recorded
  reason (wrong test, or a requirement changed by a DEC), reviewed by TST. The only allowed skip is a missing
  optional tool with a visible reason (Node.js, DEC-022), and a skipped test is never counted as evidence.
- **Where tests write (DEC-023).** pytest runs with `--basetemp=.pytest_tmp` (Git-ignored), so temporary files
  stay inside the repository. Test Git repositories set `GIT_CEILING_DIRECTORIES` to the temporary folder, so Git
  never discovers AgentDesk's own repository from inside them, and give author details per command (`-c user.name=...`)
  instead of changing any global Git configuration. Refused-folder tests simulate profile and system paths
  through configuration or environment variables and never touch the real folders.
- **JavaScript checks (DEC-022 as amended by Amendment 1).** Every JS file under `app/static/js/` is
  syntax-checked as an ES module with its content on standard input: `node --input-type=module --check < <file>`.
  Plain `node --check <file>` is not evidence: on Node 24.18.0 it exited 0 for broken module files
  (T-20261030-002-DEV, Defect 2). Every run includes a negative control: a deliberately broken module source (for
  example `export const x = ;`) given to the same command in the same run must exit non-zero, otherwise the check
  fails. `node --test` covers pure functions (route parsing, formatting). Both run from the pytest suite when
  Node.js is installed.

### 1.4 Security review: strictly read-only (OD-16 as corrected by the owner, OC-1; DEC-016; CON-012)

- For AgentDesk work, SEC must not modify anything: no application code, no documentation (including its own
  audit report, `docs/security/findings-register.md` and the activity log), no configuration, no global agent
  definitions and no project settings.
- SEC creates no file anywhere, inside or outside the repository, including session scratchpad and temporary
  folders: comparisons such as the before and after `git status` are made in its own output. (Added by
  T-20261030-002-PLN after T-20261030-002-SEC wrote one scratchpad file, which ORC recorded and deleted.)
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
  approval it relies on: for Phases 1-6 this is the owner's blanket authorization of 2026-10-30 (OA, DEC-020);
  (2) the approved requirement IDs; (3) the TASK IDs to implement (planned or corrective). Without all three, the
  developer does not start. This matches the developer-agent rule against creating a new application unless
  explicitly asked.
- **Planner confirmation.** All phases already have TASK IDs (§3 to §8). At the start of each phase PLN confirms
  them against the code as it stands, finalizes that phase's migration DDL in database-schema.md, and flags
  anything unclear before DEV starts. Minor ambiguities are resolved with the simplest maintainable solution
  consistent with the approved architecture and recorded (a DEC file when significant).
- **Only the owner approves.** No agent marks a requirement, decision or phase Approved; ORC records the owner's
  decisions. Phase gates are internal verification gates (§1.6), not approvals, and nothing is approval to commit.
- **No automatic Git actions (OD-12, DEC-015, CON-008).** Nobody stages, commits, pushes, deploys or discards
  changes in AgentDesk's repository or an owner's project. The owner decides when to commit. Test fixtures may
  commit only in throwaway repositories under `.pytest_tmp/` and `.sandbox/` (DEC-023).
- **Nothing outside this repository** is created or modified during development (CON-009). AgentDesk's own
  repository is never connected to AgentDesk during development, so the orchestrating session is never affected.
  Phase 4's real-event check uses a throwaway Git project under `D:\agentdesk\.sandbox\` (Git-ignored), with its
  own AgentDesk data folder and port (TASK-061, DEC-023). Claude Code itself keeps its usual session records under
  the user profile for that short `claude -p` run, as it does for every session including the orchestrator's;
  no agent or AgentDesk code writes there.
- **No Chrome extension** or other browser automation (OD-2, DEC-014, CON-014). The owner runs one consolidated
  manual browser checklist (Appendices A and B) at final acceptance.
- **Global Claude Code settings** are read only by the Phase 4 wizard's configuration check, read-only and
  limited to `disableAllHooks`, hook counts and agent names (OD-13, DEC-017). No phase writes them; no other phase reads them.
- **Task IDs** follow the change-tracking protocol: each phase is one work item `T-YYYYMMDD-NNN`, numbered when it
  starts. Plan tasks are numbered TASK-### and link to requirement IDs in [srs.md](srs.md).
- **Dependencies.** Package versions are fixed (architecture.md §14). Dependency files follow DEC-018 (Q10
  closed): `requirements.txt`, `requirements.lock.txt` (installed by `scripts\setup.bat`), `requirements-dev.txt`.
  Any new direct dependency needs the owner's approval (CON-004).

### 1.6 Internal verification gate, finding triage and completion summary (DEC-020, CON-006, CON-015, CON-019)

**Finding triage (step 7).** PLN classifies every collected finding (failed test, TST observation, SEC finding,
DEV remaining issue) in a triage table: finding ID, source report, class, requirement IDs, corrective TASK ID.

| Class | Meaning | Action |
|---|---|---|
| Confirmed defect | The product or a script does not meet an approved requirement | Corrective task for DEV in this phase |
| Test defect | The test itself is wrong | Corrective task to fix the test, with the reason recorded (CON-019); TST reviews it |
| Requirement gap | The requirement is unclear or missing | Minor: clarified under delegated authority with a DEC file; otherwise owner decision |
| Rescheduled with justification | A Medium, Low or Informational finding, or a Should/Could item, that fits a named later phase better (still before final acceptance) | Corrective task in that phase, technical justification recorded; never for Critical or High findings or Must requirements; leaving anything out of version 1 is an owner decision |
| Not a defect / false positive | Investigated and not a problem | Written technical justification; SEC agrees for security findings |
| Owner decision needed | See the list below | ORC asks the owner; the item is Blocked until answered |

Triage tables may also use these classes, added in T-20261030-002-PLN:

| Class | Meaning | Action |
|---|---|---|
| Hardening | Defence in depth, or a robustness gain beyond an approved requirement's acceptance criteria | Corrective task in the current phase when cheap; otherwise rescheduled with justification as above |
| Accepted with justification | A real but minor residual (Low or Informational) that an existing decision already accepts | Cite the DEC and the technical reason; severity unchanged; SEC confirms the justification in its recheck; never for Critical or High findings |
| Owner action | A step only the owner can take, and already scheduled (for example the manual checklist in TASK-092) | No routine question; the step is listed where the owner will meet it |

Corrective tasks take the next free TASK number (from TASK-093 upward), list the finding and requirement IDs,
and use the same definition of done as the planned task they correct.

**Gate (step 11).** A phase ends only when all of these hold, with evidence in saved reports:

1. every Must requirement of the phase is **Tested and passed** in a TST report (Should and Could items too,
   unless rescheduled with justification);
2. the full regression suite passes in TST's latest run, with any skipped tests listed with their reasons;
3. no Critical or High security finding of the phase is open: each is Verified by an SEC recheck;
4. every Medium finding is Verified or rescheduled with justification to a named phase before final acceptance;
5. ORC's `git status` comparison around every SEC task shows no unexplained change;
6. traceability, CHANGELOG and the completion summary are updated (step 12).

**Owner decisions (the only reasons to stop).** Weakening a security requirement; setting any requirement to
Deferred or Rejected (leaving it out of version 1); adding a direct dependency; accepting the risk of a Critical or High finding; anything that would
write outside `D:\agentdesk` or into an owner's project. ORC asks the owner, marks the affected tasks Blocked,
and continues with work that does not depend on the answer.

**Completion summary (OC-2, CON-015).** At each gate ORC writes a summary (a record, not an approval request)
containing:

1. completion summary;
2. requirement IDs completed and incomplete;
3. files created, modified and deleted (from `git status` and `git diff`, including untracked files);
4. developer change report (which also covers the reporting points of Brief §10);
5. testing report with executed results;
6. security report and unresolved findings;
7. known limitations;
8. exact Windows launch and verification commands;
9. manual browser checks added to Appendix B for the final checklist;
10. Git status, with confirmation that no commits or pushes were made.

Every requirement and check is classified as **Implemented**, **Tested and passed**, **Tested and failed**,
**Not tested** or **Planned for a future phase**. A phase is never called complete while a required acceptance
criterion remains unmet. The activity log, its Summary row and `CHANGELOG.md` are updated, and the next phase
starts automatically (step 13).

### 1.7 Explanations for the owner (OC-3, CON-016)

After each significant implementation task (in practice, after each developer delegation that adds or changes
application behaviour), ORC gives the owner a short, beginner-friendly explanation covering:

- the files changed;
- what each important file does;
- how the feature flows from the GUI to the backend to the database;
- why this approach was chosen;
- which tests verify it;
- what the owner should understand, including its limits.

The explanation is a progress note in the conversation; work does not pause for it (DEC-020).

### 1.8 Final acceptance and final report (DEC-021, CON-017, CON-018)

Final acceptance happens once, at the end of Phase 6. Each item needs saved evidence (exact commands and actual
results):

| # | Item (owner's list) | Evidence from |
|---|---|---|
| 1 | Full automated suite | TASK-085, TASK-090 (final rerun) |
| 2 | Integration and regression tests | TASK-085, TASK-086 |
| 3 | Final independent security audit | TASK-088 |
| 4 | Migrations, backup and restore verified | TASK-086 |
| 5 | Windows scripts verified | TASK-086 (fresh copy of the working tree, DEC-023) |
| 6 | All pages and GUI workflows verified (by HTTP/API tests; visual checks are the owner's manual checklist) | TASK-086; Appendices A and B in TASK-092 |
| 7 | Hook installation, event collection and shutdown/restart verified | TASK-061, TASK-086 |
| 8 | Git evidence and classification verified | TASK-085 |
| 9 | Documentation reviewed | TASK-087 |
| 10 | Final Git diff checked | TASK-090 |
| 11 | No unrelated or global files modified | TASK-090 |

The **final report** (TASK-091) contains 12 items: (1) executive summary; (2) phases and features;
(3) traceability report; (4) agent activity and task summary; (5) test report; (6) security report;
(7) limitations and risks; (8) database and backup information; (9) installation and launch;
(10) documentation locations; (11) final Git status and changed files; (12) manual verification checklist.
Results are classified as in §1.6. The owner then runs the checklist and decides (TASK-092).

### 1.9 Standard phase tasks

Every phase from 2 to 6 has the same opening and closing tasks. Their definition of done:

| Kind | Role | Cycle steps | Done when |
|---|---|---|---|
| Phase start | ORC, PLN | 1 | ORC has recorded `git status --porcelain=v1` and opened the work item `T-YYYYMMDD-NNN`; PLN has confirmed the phase's TASK list against the current code, finalized the phase's DDL (if any) in database-schema.md, and written its change report and log entry |
| Developer tests and change report | DEV | 2, 3 | Initial tests written; `.venv\Scripts\python -m pytest -v` run with actual output in the change report; CHANGELOG and README updated for the phase; the report lists the TASK IDs and the authorization relied on (CON-013) |
| Independent verification | TST | 4, 9 | Test report with exact commands, exit codes and counts; every requirement of the phase mapped to tests or Appendix B steps; edge cases added; full regression suite run; skips listed with reasons |
| Read-only security audit | SEC; ORC records | 5, 10 | §1.4 procedure followed; report saved by ORC; findings in the register; recheck of each fixed finding |
| Triage, traceability and gate | PLN | 7, 11, 12 | Triage table (§1.6) with corrective tasks; traceability matrix filled from saved reports; gate check result recorded |
| Completion summary and progression | ORC | 12, 13 | Completion summary (§1.6), Summary row and CHANGELOG checked; next phase-start task opened |

## 2. Phase overview

| Phase | Goal | Migrations | Main deliverables | Owner can see |
|---|---|---|---|---|
| 1 | Foundation | `0001` | FastAPI app, security middleware, SQLite + migrations + integrity check + backup and restore, GUI shell, Windows scripts, tests | `scripts\start.bat` opens a working GUI: navigation, theme selection, server health, database status and backup controls; other pages show labelled future-phase placeholders (FU-3) |
| 2 | Dashboard UI | none | Interactive Overview, Agents, Activity, Session and Task views on clearly labelled sample data | Navigation, filters, detail views, themes, keyboard use |
| 3 | Tracking | `0002`-`0004` | Ingestion API, Git checkpoints, wizard steps 1-2, File Change Explorer with live diffs and evidence badges, tracking-file parser, manual report paste; sample data removed | Register a real project and see its real changes and agent reports |
| 4 | Claude Code | `0005` | Hook script, spool, wizard steps 3-5 (check, install, health, disconnect), sessions, subagent runs, OBSERVED evidence | Live agent activity from real Claude Code sessions |
| 5 | Engineering reports | `0006`-`0009` | Documentation (plain text), Testing, Security and Approval centres; file-change reviews; release readiness | Documents, tests, findings, decisions, reviews and readiness |
| 6 | Validation, user manuals, final acceptance | none | End-to-end, robustness, recovery and security validation; the five user manuals; final acceptance (§1.8) and final report | Evidence-based final report, user manuals, the consolidated manual checklist |

TASK IDs: Phase 1 TASK-001 to TASK-022; Phase 2 TASK-023 to TASK-035; Phase 3 TASK-036 to TASK-050; Phase 4
TASK-051 to TASK-065; Phase 5 TASK-066 to TASK-078; Phase 6 TASK-079 to TASK-092; corrective tasks from TASK-093
(Phase 1: TASK-093 to TASK-098, §3.3; the next free number is TASK-099).
In the task tables, "Std" refers to the standard definition of done in §1.9, and DEV feature tasks are done when
their listed criteria are met and their initial tests pass in the phase's developer test task.

## 3. Phase 1: Foundation (TASK-001 to TASK-022; corrective TASK-093 to TASK-098)

**Goal (FU-3).** At the end of Phase 1 the owner launches AgentDesk locally with `scripts\start.bat` and uses a
working GUI: navigation, theme selection, server health, database status and backup controls. Every other page
shows a clearly labelled placeholder naming its future phase. Underneath: the foundation security baseline
(localhost-only binding, Host check, CSRF protection for state-changing requests, security headers), migrations,
integrity check, backup and restore, and the Windows setup and start scripts.

**Requirements:** FR-001 to FR-014, NFR-001 to NFR-012 and the constraints CON-001 to CON-016 ([srs.md](srs.md)).

**Out of scope:** projects, the connection wizard, events, hooks, Git tracking, reports, sample data, evidence badges.

**Dependencies:** `fastapi==0.162.0`, `uvicorn==0.54.0`; development only: `pytest==9.2.0`, `httpx==0.28.1`.
The file format is decided by DEC-018 (Q10 closed): `requirements.txt`, `requirements.lock.txt` (installed by
`scripts\setup.bat`), `requirements-dev.txt`.

**Status (2026-10-30, T-20261030-001-PLN-2):** all Phase 1 requirements Approved by the owner (OA). TASK-002 is
done by this planner task; Phase 1 runs as work item T-20261030-002. The cycle in §1.2 applies; the owner's
manual checks for Phase 1 (Appendix A) move to final acceptance (TASK-092).

**Status (2026-10-31, T-20261030-002-PLN):** cycle steps 2 to 6 done (T-20261030-002-DEV, -TST, -SEC). Triage
(step 7) done: corrective tasks TASK-093 to TASK-098 in §3.3. **Gate check (§1.6): not met.**

| Gate condition (§1.6) | Result | Evidence |
|---|---|---|
| 1. Every Must requirement Tested and passed | Not met: FR-010 failed (D-1); FR-012 failed for one edge case (D-3); NFR-011 failed (D-2). FR-004, FR-007, FR-014, NFR-005, NFR-008 passed in their automatable parts, with the rest in Appendix A (DEC-020); NFR-010 has only media-query checks, with the layout check in Appendix A step 22 | T-20261030-002-TST §7 |
| 2. Full regression suite passes | Not met: 598 passed, 4 failed, 0 skipped | T-20261030-002-TST E11 |
| 3. No open Critical or High finding | Met: none reported | T-20261030-002-SEC |
| 4. Every Medium finding Verified or rescheduled | Not met: SEC-001 is Open (fix in TASK-094) | T-20261030-002-SEC |
| 5. No unexplained change around SEC tasks | Met. Repository unchanged (hash manifest and `git status` identical); one file written outside the repository (session scratchpad) was self-reported, recorded and deleted by ORC; §1.4 tightened | Activity log, T-20261030-002-SEC entry |
| 6. Traceability, CHANGELOG, completion summary | Partly: matrix updated by T-20261030-002-PLN; CHANGELOG lines for the fixes come with TASK-098; completion summary follows the gate (TASK-021) | docs/traceability-matrix.md v1.1 |

Next: DEV repeat pass `T-20261030-002-DEV-2` (TASK-093 to TASK-098), then `T-20261030-002-TST-2`
(repeat of TASK-018), `T-20261030-002-SEC-2` (repeat of TASK-019, ORC records) and `T-20261030-002-PLN-2`
(repeat of TASK-020: gate check and matrix).

### 3.1 Task summary

| Task | Title | Role | Requirements | Depends on |
|---|---|---|---|---|
| TASK-001 | Record initial Git state and open the work item | ORC | CON-006, CON-008 | Owner's explicit approval to start Phase 1 (given 2026-10-30, OA) |
| TASK-002 | Confirm Phase 1 scope, Q10 and approvals (done: T-20261030-001-PLN-2) | PLN (Owner decided) | CON-004, CON-006, CON-010, CON-013 | TASK-001 |
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
| TASK-020 | Findings triage, traceability update and Phase 1 gate check | PLN | All Phase 1 requirements, CON-019 | TASK-019 |
| TASK-021 | Phase 1 completion summary and automatic progression | ORC | CON-006, CON-008, CON-014, CON-015, CON-016 | TASK-020 |
| TASK-022 | Superseded by DEC-020: the owner's Phase 1 checklist (Appendix A) is run at final acceptance in TASK-092 | - | (moved to TASK-092) | - |

DEV tasks may be delegated together in one or a few developer delegations; each delegation lists its TASK IDs
(§1.5). ORC gives the owner the explanation in §1.7 after each such delegation, without pausing.

Corrective tasks from the first Phase 1 cycle (TASK-093 to TASK-098) are listed in §3.3.

### 3.2 Task details

#### TASK-001 Record initial Git state and open the work item (ORC)

- **Requirements:** CON-006, CON-008. **Depends on:** the owner's explicit approval to start Phase 1 (given
  2026-10-30 through the blanket authorization, OA).
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
- **Status:** done in T-20261030-001-PLN-2 (2026-10-30): all requirements Approved (OA), documents baselined at
  1.0, DEC-001 to DEC-023 recorded, Q10 closed by DEC-018.

#### TASK-003 Repository scaffolding (DEV)

- **Requirements:** FR-001, NFR-011, CON-001, CON-002, CON-004. **Depends on:** TASK-002 (including Q10).

| File | Content |
|---|---|
| `.gitignore` | `.venv/`, `data/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.db`, `*.db-wal`, `*.db-shm`, `*.log`, `.claude/settings.local.json` |
| Dependency files (format per Q10; working names from v0.2: `requirements.txt`, `requirements-dev.txt`) | Runtime: `fastapi==0.162.0`, `uvicorn==0.54.0`. Development: the runtime set plus `pytest==9.2.0`, `httpx==0.28.1` |
| `pytest.ini` | `testpaths = tests` |

- **Done when:** the files exist with exactly these entries and no other dependency.
- **Status note (Q10 closed, DEC-018):** the dependency files are `requirements.txt` (the two runtime pins),
  `requirements.lock.txt` (exact runtime versions from `pip freeze` in a fresh `.venv`, which `scripts\setup.bat`
  installs; it holds only fastapi, uvicorn and their sub-dependencies) and `requirements-dev.txt` (adds pytest
  and httpx). `.pytest_tmp/` and `.sandbox/` are added to `.gitignore` by TASK-024 if not already present (DEC-023).

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
  register; Critical or High findings are fixed by a DEV repeat pass and rechecked by SEC before TASK-021, or put
  to the owner for a recorded risk acceptance (§1.6).

#### TASK-020 Findings triage, traceability update and Phase 1 gate check (PLN)

- **Requirements:** all Phase 1 requirements, CON-019. **Depends on:** TASK-019.
- **Work:** classify the collected DEV, TST and SEC findings and assign corrective tasks (§1.6, cycle step 7);
  after the fix passes, fill the Implementation, Tests and Security findings columns of
  [traceability-matrix.md](traceability-matrix.md) from the saved DEV, TST and SEC reports only, and record the
  gate check (§1.6). Repeat passes use `-PLN-n`.
- **Files:** `docs/traceability-matrix.md`; planner change report and log entry.
- **Done when:** every finding has a class and, where needed, a corrective task; every Phase 1 row is filled, or
  shows `-` with the reason in the planner's report; the gate result is recorded.
- **Status (2026-10-31):** first pass done in T-20261030-002-PLN: triage table in its change report, corrective
  tasks in §3.3, matrix columns filled from the saved DEV, TST and SEC reports, gate not met (§3 status). The
  repeat pass `T-20261030-002-PLN-2` follows TST-2 and SEC-2.

#### TASK-021 Phase 1 completion summary and automatic progression (ORC)

- **Requirements:** CON-006, CON-008, CON-014, CON-015, CON-016. **Depends on:** TASK-020 (gate met).
- **Work:** the completion summary with all 10 items of §1.6 and the result classification for every Phase 1
  requirement; the launch and verification commands:

  ```bat
  cd /d D:\agentdesk
  scripts\setup.bat dev
  .venv\Scripts\python -m pytest -v
  scripts\start.bat
  ```

  a note that Appendix A is kept for final acceptance; `git status` with confirmation that no commits or pushes
  were made; the Summary row; then the Phase 2 start task (TASK-023) is opened.
- **Done when:** the summary is delivered with no item missing and no claim beyond the recorded results, and
  TASK-023 has started.

#### TASK-022 Superseded (DEC-020)

The owner's Phase 1 manual browser checklist (Appendix A) and decision are no longer a gate between Phases 1 and
2. Appendix A is run once, with Appendix B, at final acceptance (TASK-092). The ID is kept and not reused.

**Phase 1 is complete only when** the gate in §1.6 is met: every Must requirement of Phase 1 is "Tested and
passed" in a TST report (or the owner has explicitly deferred it), no Critical or High finding is open, and the
completion summary is delivered. Phase 2 then starts automatically.

### 3.3 Corrective tasks from the first Phase 1 cycle (TASK-093 to TASK-098)

Assigned by T-20261030-002-PLN (cycle step 7) from the findings in T-20261030-002-DEV, T-20261030-002-TST and
T-20261030-002-SEC. The triage table (every finding, its class, decision and task) is in
`docs/agent-activity/change-reports/T-20261030-002-PLN.md`. Authority: the owner's blanket authorization (OA,
DEC-020); these are corrective tasks for Approved requirements (§1.6). No new dependency: standard-library Python,
the existing JavaScript modules, the scripts and documentation only (CON-004, CON-010).

**Rules for the corrective pass**

- DEV implements TASK-093 to TASK-098 in one repeat pass, `T-20261030-002-DEV-2`. Its change report cites OA,
  the requirement IDs and these TASK IDs (CON-013).
- The four failing TST tests must pass **unchanged**:
  - `test_tst_backups.py::test_tst_twelve_backups_in_one_second_keep_the_newest_ten`;
  - `test_tst_config_cli.py::test_tst_data_dir_that_is_a_file_gives_startup_error_not_a_traceback`;
  - `test_tst_config_cli.py::test_tst_data_dir_below_a_file_gives_startup_error_not_a_traceback`;
  - `test_tst_database.py::test_tst_empty_migrations_folder_gives_a_clean_startup_error`.
  DEV changes no TST test. If DEV believes a test is wrong, it says so in its report and TST decides (CON-019).
- Each task lists the regression tests DEV must add, including every gap in SEC's "Test-quality gaps"
  (mapping below). TST reviews them, adds edge cases and runs the full suite.
- Severities are not changed by fixing. A fix moves a finding at most to "Fixed - pending verification".
  Only the SEC repeat pass can verify it (CON-019).
- **Common definition of done (every task):**
  - `.venv\Scripts\python -m pytest -q` shows 0 failed. With Node installed it also shows 0 skipped; any skip is
    listed with its reason.
  - `node --test tests/js/*.test.mjs` passes.
  - The module-mode JavaScript check (DEC-022 Amendment 1) passes for every file under `app/static/js/`, and its
    negative control fails as expected.
  - `python -W error` compiles every `.py` file under `app/`, `scripts/` and `tests/`.
  - Commands and actual output are in the DEV-2 change report.
- **Verification:**
  - `T-20261030-002-TST-2` (repeat of TASK-018);
  - `T-20261030-002-SEC-2` (repeat of TASK-019, read-only, ORC records), which rechecks SEC-001 to SEC-015
    including the SEC-010 disposition;
  - `T-20261030-002-PLN-2` (repeat of TASK-020), which records the gate.

| SEC test-quality gap (T-20261030-002-SEC) | Covered by |
|---|---|
| 1. CR/LF and very long paths in the log (SEC-001) | TASK-094 tests (a) to (d) |
| 2. ASGI `websocket` scope (SEC-006) | TASK-094 test (e) |
| 3. Restore next to a real, uncheckpointed WAL (SEC-003) | TASK-093 tests (i), (j) |
| 4. Server started on another port during restore; request on a missing database (SEC-002) | TASK-093 tests (f) to (h) |
| 5. Ten or more future-dated names; prune `PermissionError` (SEC-004) | TASK-093 tests (b) to (d) |
| 6. Arbitrary HTTP method such as `PURGE` (SEC-008) | TASK-094 test (f) |

| Task | Title | Role | Findings | Requirements | Depends on |
|---|---|---|---|---|---|
| TASK-093 | Backup naming, retention and restore safety | DEV; verify TST-2, SEC-2 | D-1, SEC-002, SEC-003, SEC-004, SEC-012, SEC-015; DEV limitations 5 and 8 | FR-009, FR-010, FR-011, FR-012, NFR-006, NFR-012 | TASK-020 (this triage) |
| TASK-094 | Security middleware and log hardening | DEV; verify TST-2, SEC-2 | SEC-001, SEC-006, SEC-007, SEC-008, SEC-011, O-2; TST proposal "500 with a body is not logged" | NFR-002, NFR-003, NFR-004, NFR-006, NFR-007, FR-003, CON-002 | TASK-020 |
| TASK-095 | Startup and migration robustness; data-folder hygiene | DEV; verify TST-2, SEC-2 | D-2, D-3, O-7, SEC-013 | FR-012, NFR-011, NFR-012, CON-009 | TASK-093 (lock-file name for `.gitignore`) |
| TASK-096 | Folder-permission warning and owner-only new data folder | DEV; verify TST-2, SEC-2 | SEC-005 (Phase 1 part) | NFR-011, NFR-012 (prepares NFR-024) | TASK-095 (folder creation code) |
| TASK-097 | Frontend hardening and testability | DEV; verify TST-2, SEC-2 | SEC-009, O-4, O-5; TST proposal "app.js cannot be imported" | NFR-005, FR-004, FR-005, FR-008 | TASK-020 |
| TASK-098 | Setup script, README and CHANGELOG for the corrective pass | DEV; verify TST-2, SEC-2 | SEC-014, O-3, DEV limitation 7 | FR-001, FR-002, FR-014, NFR-012, CON-009 | TASK-093 to TASK-097 |

Parts of Phase 1 findings that belong to a later phase's feature:

- **SEC-005, ingest-token part:** in Phase 3 (TASK-038, new NFR-024, Proposed, DEC-024). The token is created by
  TASK-038, not in Phase 1 or Phase 4.
- **DEV limitation 2 (theme flash on load):** in Phase 2 (TASK-025), which reworks the theme and design system and
  their static tests.

#### TASK-093 Backup naming, retention and restore safety (DEV)

- **Findings:** D-1; SEC-004, including DEV limitation 8 (cross-process same-second race); SEC-002, including DEV
  limitation 5; SEC-003; SEC-012; SEC-015.
- **Requirements:** FR-009, FR-010, FR-011, FR-012 (pattern anchors), NFR-006, NFR-012.
- **Files:** `app/database/backup.py`, `app/database/connection.py`, `app/database/migrations.py` (pattern only),
  `app/main.py` (24-hour rule), `app/__main__.py` (server lock), `app/api/system.py` (error messages),
  `scripts/restore_db.py`, tests (extend `tests/test_backup_restore.py` or add a new DEV test file).
- **Work:**
  1. **Naming (D-1, SEC-004):** a new backup takes the next sequence after the highest one already used for that
     UTC second. Used names include `.db`, `.db.partial` and `failed-*` files. The `.partial` file is created
     exclusively (it fails if it exists, and the next sequence is tried) before the SQLite copy, so two processes
     never write one file.
  2. **Retention (D-1, SEC-004):** pruning never deletes the backup just created. An `OSError` while deleting an
     old backup is logged and does not turn a good backup into a failure.
  3. **Future-dated names (SEC-004):** a backup name dated more than 5 minutes after the current UTC time is
     logged as future-dated (once per run). It counts as the oldest for retention and is ignored by the 24-hour
     startup rule, so it can neither displace real backups nor stop startup backups.
  4. **Server lock (SEC-002):**
     - The running server (`python -m app`) holds an exclusive operating-system lock on a lock file in the data
       folder for its whole lifetime, using the standard library (for example `msvcrt.locking`).
     - `scripts\restore_db.py` takes that lock before its prompt and holds it until the swap is finished. If the
       lock is held, it refuses with the existing "AgentDesk seems to be running" guidance. The port check stays.
     - A second `python -m app` on the same data folder (any port) is refused with a plain message.
     - Tests that build several apps on one data folder through `create_app()` keep working; DEV decides where
       the lock is taken.
  5. **No silent database creation (SEC-002):** request connections open the existing database without creating
     it (SQLite URI `mode=rw`); only the startup sequence may create a new database. A request while the file is
     missing gets a JSON error with a plain message and creates no file.
  6. **Sidecars (SEC-003):** restore always moves `-wal`, `-shm` and `-journal` files beside the target into the
     `pre-restore-<time>` set, also when no main database file exists. After the swap it runs
     `PRAGMA integrity_check` (read-only) on the restored database and reports a failure plainly.
  7. **Error text (SEC-012):** backup and restore errors returned by the API and shown on the Settings page use a
     fixed plain message per error kind, with no exception text or paths (FR-009 (5) still met); details go to the
     log. The command-line scripts may still name files and folders on the owner's console.
  8. **Anchors (SEC-015):** the backup, safe-name and migration file-name patterns match the whole string
     (`re.fullmatch` or `\Z`).
- **Done when:**
  - The common definition of done is met, and the TST test for twelve same-second backups passes unchanged.
  - DEV has added these regression tests, and they pass:
    - (a) 12 and 25 backups within one frozen second: every call returns an existing file; 10 remain; the newest
      is among them.
    - (b) 10 or more future-dated names: a new backup succeeds and survives; future-dated files are pruned first.
    - (c) One far-future name (year 2099) and a real backup older than 24 hours: the startup backup is still taken.
    - (d) An old backup held open by another handle while a new backup is made: the new backup succeeds, a warning
      is logged and the held file remains.
    - (e) A pre-existing `.partial` file with the next name: `create_backup` uses another name and leaves that file
      unchanged.
    - (f) Restore while a real `python -m app` runs on the same data folder with a different `AGENTDESK_PORT`: exit
      code non-zero; database and backups unchanged.
    - (g) A second `python -m app` on the same data folder and another port: refused with a plain message, exit
      code 1.
    - (h) A database-backed request while `agentdesk.db` is missing: JSON error; no `agentdesk.db` created.
    - (i) Restore with no main database but a real, uncheckpointed WAL from another database beside the target:
      sidecars moved into the pre-restore set; the restored database holds exactly the backup's rows and passes
      `integrity_check`.
    - (j) The same for a `-journal` file.
    - (k) Names ending in a newline are refused by every pattern.
    - (l) A backup failure whose exception text contains a path: the API response and the page message contain
      neither.
  - Every existing FR-009 to FR-011 test (DEV and TST) still passes.

#### TASK-094 Security middleware and log hardening (DEV)

- **Findings:** SEC-001 (Medium), SEC-006, SEC-007, SEC-008, SEC-011, O-2; TST proposal "a 500 error with a
  request body never logs the body".
- **Requirements:** NFR-002, NFR-003, NFR-004, NFR-006, NFR-007, FR-003, CON-002.
- **Files:** `app/core/security.py`, `app/core/log_setup.py`, `app/main.py`, `app/api/system.py`, tests (extend
  `tests/test_security.py` or add a new DEV test file).
- **Work:**
  1. **Log forging and flooding (SEC-001):**
     - Request-derived values (path; Host is already safe) are escaped (`%r` style) and cut to at most 200
       characters, on the refusal line and on the unhandled-error line.
     - Refusal lines are rate-limited: at most 20 full lines per minute, then one summary line with the number
       suppressed.
     - uvicorn's per-request upgrade warnings ("Unsupported upgrade request", "No supported WebSocket library")
       are limited or filtered the same way. DEV checks which messages uvicorn 0.54.0 actually emits.
  2. **WebSocket scopes (SEC-006):** the middleware refuses (closes) every `websocket` scope before it reaches the
     app; `lifespan` scopes still pass through.
  3. **Method allow-list (SEC-008):** the Origin, CSRF-token and JSON checks apply to every method except GET,
     HEAD and OPTIONS.
  4. **Isolation headers (SEC-007):** every response also carries `Cross-Origin-Opener-Policy: same-origin`,
     `Cross-Origin-Resource-Policy: same-origin` and a `Permissions-Policy` that disables device features (for
     example camera, microphone, geolocation). The CSP string stays exactly as NFR-004 states.
  5. **Telemetry (SEC-011):** FastAPI's built-in telemetry auto-configuration is switched off in code, so
     environment variables cannot enable it. DEV confirms the parameter in the installed FastAPI 0.162.0 source.
  6. **HEAD on health (O-2):** `HEAD /api/v1/health` answers 200 with the security headers and no body.
- **Done when:**
  - The common definition of done is met.
  - DEV has added these regression tests, and they pass:
    - (a) A POST to `/x%0D%0AFAKE` with a foreign Origin gets 403 and adds exactly one log line, with CR and LF
      shown escaped.
    - (b) A request path of about 10 KB is logged with at most 200 characters of path (before escaping).
    - (c) 100 refused requests in a row give at most 20 full lines plus summary lines.
    - (d) An unhandled error on a path containing CR and LF logs one escaped line.
    - (e) A `websocket` scope with an allowed Host is closed without calling the app, and the same with a foreign
      Host; app startup through `lifespan` still works.
    - (f) `PURGE` and `PROPFIND` without a token get 403. With a valid token, same Origin and JSON they reach
      routing (JSON 404 or 405). GET, HEAD and OPTIONS behave as before.
    - (g) The three new headers are present, and the CSP is unchanged, on the 13 response kinds TST covers.
    - (h) With `FASTAPI_OTEL_AUTO_CONFIGURE=true` set (set inside the test), `create_app()` starts normally and
      configures no telemetry.
    - (i) `HEAD /api/v1/health` returns 200, an empty body and the security headers.
    - (j) A request with a JSON body that triggers a 500: the log holds neither the body nor the token.
  - Every existing NFR-002 to NFR-007 test still passes.

#### TASK-095 Startup and migration robustness; data-folder hygiene (DEV)

- **Findings:** D-2, D-3, O-7, SEC-013.
- **Requirements:** FR-012, NFR-011, NFR-012, CON-009.
- **Files:** `app/main.py`, `app/__main__.py` (log setup runs before `create_app()`), `app/core/log_setup.py`,
  `app/database/migrations.py`, `app/database/connection.py`, `.gitignore`, `README.md` (one sentence), tests.
- **Work:**
  1. **Data folder errors (D-2):** if the data, backups or logs folder cannot be created (an `OSError`: the path is
     a file or lies below a file, or access is denied), startup stops with a plain message naming the folder,
     `AGENTDESK_DATA_DIR` and what to do. This also covers the log setup that `python -m app` runs before
     `create_app()`. Exit code 1, no traceback on the console.
  2. **Missing migrations (D-3):** if no migration file is found, startup stops before any database file is
     created, with a message saying so and that the `migrations` folder of AgentDesk must be restored. An
     unexpected `sqlite3.Error` in the migration or instance-settings step becomes a plain startup error; details
     go to the log.
  3. **Transaction control in migrations (O-7, DEC-025):** a migration file that contains a transaction-control
     statement (`BEGIN`, `COMMIT`, `END`, `ROLLBACK`, `SAVEPOINT` or `RELEASE` as a statement of its own) is refused
     before anything is applied, with a message naming the file. `CREATE TRIGGER ... BEGIN ... END;` bodies remain
     allowed. For example, statements can be split with `sqlite3.complete_statement`.
  4. **Data-folder hygiene (SEC-013):**
     - `.gitignore` also ignores, anywhere in the repository: `*.log.*`, `*.db.partial`, `*.db.restoring`,
       `*.db-journal` and the TASK-093 lock file.
     - At startup, the data folder in use is logged at INFO. If it is not the default `<repo>/data`, a WARNING says
       that Git's `data/` rule does not cover it (the patterns above still apply inside the repository).
     - Database connections set `PRAGMA temp_store=MEMORY`, so SQLite writes no temporary files to `%TEMP%`.
- **Done when:**
  - The common definition of done is met, and the three TST tests for D-2 and D-3 pass unchanged.
  - DEV has added these regression tests, and they pass:
    - (a) `python -m app` as a subprocess with `AGENTDESK_DATA_DIR` set to an existing file: exit code 1; the
      message names the variable; no "Traceback" in the output.
    - (b) An empty migrations folder: a startup error, and no `agentdesk.db` is created.
    - (c) Migration files containing `COMMIT;`, `BEGIN TRANSACTION;` or `SAVEPOINT x;` are refused with the file
      named, and the database is unchanged.
    - (d) A migration containing `CREATE TRIGGER ... BEGIN ... END;` applies normally.
    - (e) `.gitignore` contains the new patterns (text check, no Git command).
    - (f) `PRAGMA temp_store` returns 2 (MEMORY) on a request connection and on the startup connection.
    - (g) A non-default data folder produces the WARNING; the default does not.

#### TASK-096 Folder-permission warning and owner-only new data folder (DEV)

- **Findings:** SEC-005, Phase 1 part. (The ingest-token part is NFR-024 in TASK-038; DEC-024.)
- **Requirements:** NFR-011, NFR-012. Constraints: DEC-009 (the Windows account name is never read or stored),
  CON-004 (no new dependency), NFR-017 (AgentDesk runs no program such as `icacls`).
- **Files:**
  - a new standard-library module for the check (for example `app/core/folder_access.py`, using `ctypes` and
    Windows only);
  - `app/main.py`; `scripts/restore_db.py` and `scripts/backup_db.py` where they create the data folder;
  - `README.md`, new section "Keep AgentDesk private on a shared PC";
  - tests.
- **Work:**
  1. **Startup check (read-only):**
     - Read the access list of the AgentDesk folder and of the data folder through the Windows security API
       (`ctypes`).
     - If an allow entry grants any write-type access to Everyone (S-1-1-0), Authenticated Users (S-1-5-11) or
       Users (S-1-5-32-545), print and log one WARNING per folder. The warning names the folder and the README
       section.
     - SIDs are compared only. Account names are never looked up or recorded.
     - If the check itself fails, one INFO line says the permissions could not be checked, and startup continues.
     - AgentDesk never changes the permissions of an existing folder.
  2. **New data folder:** a data folder that does not exist yet is created with owner-only access using the
     standard library: `os.mkdir(path, 0o700)`, which Windows applies as access for the current user, SYSTEM and
     Administrators in the supported Python versions. DEV confirms this on the installed Python with a test.
     Subfolders inherit it.
  3. **README:** when this matters (other Windows accounts on the PC); the commands to restrict `D:\agentdesk` to
     the owner, SYSTEM and Administrators; how to check the result before closing the window; how to undo
     (`icacls ... /reset`). It also says that AgentDesk shows the warning but never changes existing permissions.
- **Done when:**
  - The common definition of done is met.
  - DEV has added these regression tests, and they pass:
    - (a) A folder created with `os.mkdir(..., 0o700)` is reported as having no broad write access.
    - (b) A test folder under `.pytest_tmp` given an allow entry for S-1-5-11 is reported, and startup logs the
      warning and still succeeds. The test may run `icacls <folder> /grant *S-1-5-11:(OI)(CI)M`, which names the
      SID, not an account.
    - (c) A failing check (simulated) gives the INFO line, and startup succeeds.
    - (d) A new data folder created by startup has a protected access list with no entry for S-1-1-0, S-1-5-11 or
      S-1-5-32-545.
    - (e) A source scan finds no `getpass.getuser`, `USERNAME`, `GetUserName` or `LookupAccountSid` in `app/` and
      `scripts/`.
    - (f) `requirements.lock.txt` is unchanged.

#### TASK-097 Frontend hardening and testability (DEV)

- **Findings:** SEC-009, O-4, O-5; TST proposal: `app.js` runs `boot()` on import and cannot be unit-tested.
- **Requirements:** NFR-005, FR-004, FR-005, FR-008.
- **Files:** `app/static/js/dom.js`, `app/static/js/router.js`, `app/static/js/app.js` (and a small entry module
  if DEV moves `boot()`; `index.html` then loads that module, still with no inline script), new DEV test files under
  `tests/js/`. TST's test files are not changed.
- **Work:**
  1. **DOM builder (SEC-009):** `h()` refuses `on*` attributes whose value is not a function, and refuses
     `srcdoc`. URL attributes (`href`, `src`, `action`, `formaction`, `xlink:href`) accept only relative URLs
     (starting with `#`, `/`, `./`, `../` or `?`) and `http:` or `https:` URLs. Other schemes (`javascript:`,
     `data:`, `vbscript:`, ...) are refused, after trimming and in any letter case.
  2. **Formatter (O-4):** `formatBytes` returns "unknown" for anything that is not a finite number of 0 or more.
  3. **Router (O-5):** a malformed percent escape in a route parameter shows the not-found view instead of
     throwing.
  4. **Testability:** the health-polling and status functions of `app.js` can be imported by Node tests without
     running `boot()`. Browser behaviour is unchanged.
- **Done when:**
  - The common definition of done is met.
  - DEV has added these Node regression tests, and they pass:
    - string `onclick` refused, and a function listener still works;
    - `srcdoc` refused;
    - `javascript:alert(1)`, `  JaVaScRiPt:x` and `data:text/html,x` refused in `href`; `#/settings` and
      `/static/x` accepted;
    - `formatBytes` of NaN, Infinity, -1 and undefined gives "unknown";
    - a route parameter `%E0%A4%A` shows the not-found view without an exception;
    - FR-004 with a fake DOM and fake timers: "Server unreachable" after a failed poll, "Server OK" after a
      successful one, no poll while `document.hidden`, status shown as text plus icon.
  - TST's 39 Node tests still pass.

#### TASK-098 Setup script, README and CHANGELOG for the corrective pass (DEV)

- **Findings:** SEC-014, O-3, DEV limitation 7 (possible `.pyc` writes into the Python installation folder).
  Also the user-facing documentation for TASK-093 to TASK-097.
- **Requirements:** FR-001, FR-002, FR-014, NFR-012, CON-009.
- **Files:** `scripts/setup.bat`, `README.md`, `CHANGELOG.md`, tests (TST-style sandbox copy).
- **Work:**
  1. **setup.bat (SEC-014, DEV limitation 7):**
     - Set `NoDefaultCurrentDirectoryInExePath=1` before looking for Python, so a `python` program in the current
       folder is never run.
     - Print the full path and version of the interpreter used (`sys.executable`).
     - Set `PYTHONDONTWRITEBYTECODE=1` for the steps that run the system Python (version check, `venv` creation),
       so nothing is compiled into the Python installation folder.
  2. **README:**
     - Ctrl+C in the `start.bat` window can ask "Terminate batch job (Y/N)?"; answer Y (O-3).
     - Restore refuses while AgentDesk runs with the same data folder on any port; a second AgentDesk on the same
       data folder is refused (TASK-093).
     - A custom data folder is covered only by the ignore patterns (TASK-095).
     - The folder-permission warning and the "Keep AgentDesk private on a shared PC" section (TASK-096).
  3. **CHANGELOG:** one line per user-visible fix under `## [Unreleased]` ("Fixed" or "Security"), tagged with the
     DEV task ID.
- **Done when:**
  - The common definition of done is met, and TST's Windows-script tests pass.
  - DEV has added this regression test, and it passes: in a `.sandbox` copy, a `python.bat` placed in the copy's
    root (it writes a marker file) is not run by `cmd /c scripts\setup.bat`.
  - A `.sandbox` run of `setup.bat` prints the interpreter path line.
  - The README covers the four items above, and FR-014's criteria are still met.

## 4. Phase 2: Dashboard UI on preview data (TASK-023 to TASK-035)

**Goal.** Interactive Overview, Agents, Activity, event, session and task views on clearly labelled sample data
(preview mode, off by default). No migration and no new backend tables. **Requirements:** FR-015 to FR-020
(layout and preview), NFR-005, NFR-008 to NFR-010. **Out of scope:** real data (Phase 3 onward). Old outline
numbers (2.1 to 2.7) are shown in brackets.

| Task | Title | Role | Requirements | Files | Depends on | Done when |
|---|---|---|---|---|---|---|
| TASK-023 | Phase 2 start | ORC, PLN | CON-006, CON-010, CON-009 | Activity log, PLN report | TASK-021 | Std (§1.9). ORC also records a metadata baseline (size and last-write time only, contents not read) of the global Claude Code settings and agent definition files and the global Git config, for TASK-090 |
| TASK-024 | Development checks: in-repository temp files and JavaScript checks (DEC-022, DEC-023) | DEV | CON-009, CON-011, CON-019, NFR-005 | `pytest.ini` (`--basetemp=.pytest_tmp`), `.gitignore` (`.pytest_tmp/`, `.sandbox/`, if missing), `tests/test_js_checks.py`, `tests/js/` | TASK-023 | pytest temp files appear only under `.pytest_tmp/`; `node --input-type=module --check` (file content on standard input) runs on every file under `app/static/js/` (visible skip without Node); in the same run a deliberately broken module source fails the check (negative control), otherwise the check fails (DEC-022 Amendment 1). Plain `node --check <file>` is not used. Note (T-20261030-002-PLN): `--basetemp=.pytest_tmp` and the `.pytest_tmp/` and `.sandbox/` ignore entries already exist from Phase 1, and TST's `test_tst_javascript_syntax_check_with_negative_control` already follows the amended form; TASK-024 confirms or reuses them rather than duplicating |
| TASK-025 | Design system completion (2.1) | DEV | NFR-005, NFR-009, FR-017, FR-029 (badge presentation only); FR-007 (theme before first paint) | `app/static/css/app.css`, `app/static/js/ui.js`; `app/static/index.html` and a small external theme script if needed | TASK-023 | Evidence labels and verification values render as icon plus text with what they do not mean; status pills, tables, loading, empty and error states; AA contrast in both themes (checked on tokens); data inserted as text only. The saved theme is applied before the first paint, with no inline script (CSP unchanged), so no flash of the other theme appears on load (DEV limitation 2 of T-20261030-002-DEV, rescheduled by T-20261030-002-PLN because this task reworks the theme and its static tests) |
| TASK-026 | Router: breadcrumbs, URL-held filters, detail routes (2.2) | DEV | FR-018, NFR-008 | `app/static/js/router.js`, `app/static/js/ui.js` | TASK-025 | Detail routes for event, session, task and agent; filters in the query string; reloading a detail URL shows the same view; Back restores filters; focus moves to the page heading |
| TASK-027 | Data layer, preview mode and auto-refresh (2.3) | DEV | FR-019, FR-020, NFR-005 | `app/static/js/data.js`, `app/static/preview/sample.json`, `app/static/js/pages/settings.js` (toggle kept in browser local storage, off by default), `app/static/js/refresh.js` | TASK-025 | Preview off: only empty states. Preview on: fixed "SAMPLE DATA, not real activity" banner on every page. Lists refresh every 5 s only while the tab is visible, with Pause and Resume |
| TASK-028 | Overview page (2.4) | DEV | FR-015 | `app/static/js/pages/overview.js` | TASK-026, TASK-027 | Every tile and row opens its filtered list or item; every number comes from the data layer; empty states without data |
| TASK-029 | Agents list and detail (2.5) | DEV | FR-016 | `app/static/js/pages/agents.js` | TASK-026, TASK-027 | Four profiles; "Never seen" without recorded activity; a profile never implies activity |
| TASK-030 | Activity timeline; event, session and task detail views (2.6) | DEV | FR-017, FR-018 | `app/static/js/pages/activity.js`, `event.js`, `session.js`, `task.js` | TASK-026, TASK-027 | Newest first with Load more; filters combine and live in the URL; unknown fields show "unknown"; every ID links to its view |
| TASK-031 | Developer tests and change report, with keyboard and 400 px self-check (2.7) | DEV | FR-015 to FR-020, NFR-005, NFR-008 to NFR-010, CON-011, CON-013 | `tests/test_static.py` (extend), `tests/js/*.test.mjs`, change report, CHANGELOG | TASK-024 to TASK-030 | Std. Static tests show every new module is served with a JavaScript MIME type and `index.html` stays free of inline script; `node --test` covers route parsing, formatters and "fixture data only with preview on" |
| TASK-032 | Independent verification | TST | FR-015 to FR-020, NFR-005, NFR-008 to NFR-010, CON-011, CON-014, CON-019 | `tests/`, test report | TASK-031 | Std; Phase 2 manual steps listed for Appendix B |
| TASK-033 | Read-only security audit | SEC (ORC records) | NFR-004, NFR-005, FR-019, CON-002, CON-012 | None written by SEC | TASK-032 | Std. Scope: unsafe DOM use, CSP unchanged, no external requests, no sample data without the banner |
| TASK-034 | Triage, traceability and gate | PLN | All Phase 2 requirements, CON-019 | `docs/traceability-matrix.md`, PLN report | TASK-033 | Std |
| TASK-035 | Completion summary and progression | ORC | CON-006, CON-008, CON-015, CON-016 | Activity log | TASK-034 | Std; TASK-036 opened |

## 5. Phase 3: Tracking (TASK-036 to TASK-050)

**Goal.** Register real projects, take read-only Git checkpoints, show Git-verified changes with live diffs and
evidence labels, read agent tracking files and pasted reports, and remove sample data. Migrations `0002` to
`0004`. **Requirements:** FR-021 to FR-034, NFR-013, NFR-015 to NFR-019, the ingest-token part of NFR-020,
NFR-024 (owner-only ingest token; Proposed in T-20261030-002-PLN, DEC-024; TASK-036 confirms that its approval
is recorded before TASK-038 starts), and real data for FR-015 and FR-017. Old outline numbers (3.1 to 3.9) are shown in brackets.

| Task | Title | Role | Requirements | Files | Depends on | Done when |
|---|---|---|---|---|---|---|
| TASK-036 | Phase 3 start; finalize DDL `0002`-`0004` | ORC, PLN | CON-005, CON-006, CON-010 | `docs/database-schema.md`, PLN report | TASK-035 | Std |
| TASK-037 | Migration `0002` and project and event data access (3.1) | DEV | FR-025, CON-005 | `migrations/0002_projects_activity.sql`, `app/services/projects.py`, `app/services/events.py` | TASK-036 | Applies to a new database and to a Phase 1 database (after a `pre-migration` backup); schema version 2; CHECK limits enforced |
| TASK-038 | Redaction, ingest token and event ingestion API (3.2) | DEV | FR-025, NFR-003, NFR-013, NFR-019, NFR-020, NFR-024 | `app/core/redaction.py`, `app/models/events.py`, `app/api/events.py`, ingest token created at first start in `data/ingest_token`; `.gitignore` pattern for `ingest_token` anywhere in the repository | TASK-037 | `POST /api/v1/events`: malformed, oversized, wrongly typed and duplicate events rejected or deduplicated with a clear 4xx and no partial rows; ingest token or CSRF token required; token never logged or shown; redaction covers the formats in architecture §6.3. NFR-024 (SEC-005 token part, DEC-024): the token file grants access only to the current Windows user, SYSTEM and Administrators (protected access list checked by SID in a test, no entry for S-1-1-0, S-1-5-11 or S-1-5-32-545); standard library only; the account name is never read; if owner-only access cannot be applied, no token is created and a plain message says why and what to do |
| TASK-039 | Safe Git runner and parsers (3.3) | DEV | FR-024, FR-026, NFR-017, NFR-018 | `app/integrations/git/runner.py`, `app/integrations/git/parsers.py` | TASK-036 | Read-only allowlist; argument lists, no shell; `GIT_OPTIONAL_LOCKS=0`, `core.fsmonitor=false`, `--no-ext-diff`, `--no-textconv`, timeouts; parsers for `status --porcelain=v2 -z`, `diff --numstat -z`, `hash-object` without `-w`, including unusual names |
| TASK-040 | Migration `0003`; checkpoint service; "Refresh from Git" (3.4) | DEV | FR-023, FR-026, CON-005 | `migrations/0003_git_tracking.sql`, `app/services/checkpoints.py`, `app/api/projects.py` | TASK-037, TASK-039 | Checkpoints match `git status` in temporary repositories (added, modified, deleted, untracked, binary, staged rename, conflicted); no `index.lock` created; more than 5,000 changes marked truncated |
| TASK-041 | Wizard steps 1-2 and Projects pages (3.5) | DEV | FR-021, FR-022, FR-023, NFR-015 | `app/services/folders.py` (refused folders, Git root rule), `app/api/folders.py`, `app/api/projects.py`, `app/static/js/pages/projects.js`, `connect.js`, `project.js` | TASK-040 | Folder browser returns folder names only; refused locations rejected, also through junctions, symlinks, `..`, letter case and trailing slashes; Git root rule applied with no Git command for a refused root; registration takes the baseline; project files and `git status` unchanged |
| TASK-042 | File Change Explorer and live diff (3.6) | DEV | FR-027, FR-028, NFR-015, NFR-016 | `app/services/diffs.py`, `app/api/files.py`, `app/static/js/pages/files.js`, `file.js` | TASK-040, TASK-041 | Diff matches `git diff`; binary and oversized notices; sensitive files and AgentDesk's data folder refused; diff content never stored |
| TASK-043 | Migration `0004`; tracking-file parser; Reports page and paste form (3.7) | DEV | FR-031, FR-032, FR-033, NFR-013, CON-005 | `migrations/0004_agent_reports.sql`, `app/integrations/tracking/`, `app/services/reports.py`, `app/api/reports.py`, `app/static/js/pages/reports.js` | TASK-037, TASK-041 | Template fixtures parsed; unrecognized files kept and viewable; a changed file creates a new version; paste preview before Save; 64 KB limit; text shown escaped; "reported, not found in Git" and "Git change not reported" flags |
| TASK-044 | Evidence classification and discrepancy flags (3.8) | DEV | FR-029, FR-030, FR-031 | `app/services/evidence.py` | TASK-040, TASK-043 | One test per rule R-A to R-F; a change during a session with no file tool event and no report is UNATTRIBUTED; computed on read, never stored |
| TASK-045 | Real data on Overview and Activity; sample data removed (3.9) | DEV | FR-015, FR-017, FR-034 | List endpoints in `app/api/`, `app/static/js/data.js`, `pages/overview.js`, `pages/activity.js`, `pages/settings.js`; delete `app/static/preview/` | TASK-042 to TASK-044 | No sample fixture or preview toggle remains; pages show stored records or empty states; filters work through the API |
| TASK-046 | Developer tests and change report | DEV | FR-021 to FR-034, NFR-013, NFR-015 to NFR-019, CON-008, CON-011 | `tests/` (temporary Git repositories under `.pytest_tmp/` with `GIT_CEILING_DIRECTORIES`), change report, CHANGELOG, README | TASK-037 to TASK-045 | Std. Read-only proof: project file hashes and `git status` identical before and after registration, checkpoint, diff, rescan and report ingestion |
| TASK-047 | Independent verification | TST | FR-015, FR-017, FR-021 to FR-034, NFR-013, NFR-015 to NFR-019, CON-014, CON-019 | `tests/`, test report | TASK-046 | Std |
| TASK-048 | Read-only security audit | SEC (ORC records) | FR-022 to FR-024, FR-028, FR-033, NFR-013, NFR-015 to NFR-020, NFR-024, CON-012 | None written by SEC | TASK-047 | Std. Scope: path traversal, refused folders, Git hardening, redaction, ingestion authentication, script injection through reports and diffs, ingest-token file access (NFR-024; closes the SEC-005 token part) |
| TASK-049 | Triage, traceability and gate | PLN | All Phase 3 requirements, CON-019 | `docs/traceability-matrix.md`, PLN report | TASK-048 | Std |
| TASK-050 | Completion summary and progression | ORC | CON-006, CON-008, CON-015, CON-016 | Activity log | TASK-049 | Std; TASK-051 opened |

## 6. Phase 4: Claude Code integration (TASK-051 to TASK-065)

**Goal.** Live agent activity from real Claude Code sessions: hook script, spool, wizard steps 3-5, sessions,
subagent runs and OBSERVED evidence. Migration `0005`. **Requirements:** FR-035 to FR-048, NFR-014, NFR-020,
and live data for FR-015 and FR-016. Old outline numbers (4.1 to 4.8) are shown in brackets.

| Task | Title | Role | Requirements | Files | Depends on | Done when |
|---|---|---|---|---|---|---|
| TASK-051 | Phase 4 start; finalize DDL `0005`; recheck the hook reference against the installed Claude Code | ORC, PLN | CON-005, CON-006, CON-010, FR-037 | `docs/database-schema.md`; `docs/architecture.md` §6 if fields differ | TASK-050 | Std; any difference between the official hook reference and architecture §6 recorded |
| TASK-052 | Hook script (4.1) | DEV | FR-035, FR-036, NFR-013, NFR-014, NFR-020 | `hooks/agentdesk_hook.py` (standard library only) | TASK-051 | Exit code 0 and empty stdout in every failure case; 1.5 s network timeout; spool capped at 50 MB; content fields dropped; port and data folder taken from the wizard-written arguments (defaults 8765 and `<repo>/data`), never from event input |
| TASK-053 | Migration `0005`; Claude Code ingestion endpoint and event mapping (4.2) | DEV | FR-037, FR-044, FR-045, NFR-013, NFR-014, NFR-019, NFR-020, CON-005 | `migrations/0005_claude_code.sql`, `app/integrations/claude_code/normalizer.py`, `app/api/ingest.py` (`POST /api/v1/ingest/claude-code`), `app/services/sessions.py` | TASK-051 | Recorded payload shapes map to events, sessions and tasks; unknown fields never crash; only the `Task ID:` line is extracted from prompts; final-message excerpt at most 1,024 characters and the database refuses more; server-side re-sanitizing |
| TASK-054 | Spool replay and session states (4.3) | DEV | FR-038 | `app/services/spool.py`, timer in `app/main.py` | TASK-052, TASK-053 | Replay at startup and every 60 s, each event exactly once; idle after 30 minutes, stale after 12 hours; a run without a stop event in an ended or stale session shows "unknown (no stop event)" |
| TASK-055 | Rate-limited automatic checkpoints (4.8) | DEV | FR-046 | `app/services/checkpoint_scheduler.py` | TASK-053 | 20 Stop events within 10 s give one immediate and one trailing checkpoint; registration and SessionStart baselines taken at once; in-process timer only |
| TASK-056 | Wizard step 3: configuration check (4.4) | DEV | FR-039, FR-024, NFR-017 | `app/integrations/claude_code/inspector.py`, `app/api/connection.py` | TASK-051 | Results as architecture §7 step 3; the only module that reads `~/.claude/`, limited to `disableAllHooks`, hook counts and agent names; nothing written; invalid JSON reported and blocks installing into that file |
| TASK-057 | Wizard steps 4-5: install, self-test, health, disconnect (4.4) | DEV | FR-023, FR-040, FR-041, FR-042, FR-048 | `app/integrations/claude_code/merge.py`, `app/services/connection.py`, `app/static/js/pages/connect.js`, `project.js` | TASK-052, TASK-056 | Preview diff and hash; typed-name confirmation; original backed up in `data/connection-backups/`; atomic write; existing content preserved; idempotent; a file changed after the preview aborts; disconnect removes only AgentDesk's entries; health states as architecture §7 step 5; each step explains itself |
| TASK-058 | OBSERVED evidence, run linking, live Agents, Sessions and Overview (4.5, 4.6) | DEV | FR-015, FR-016, FR-031, FR-043, FR-044, FR-047 | `app/services/evidence.py`, `app/api/agents.py`, `app/api/sessions.py`, `app/static/js/pages/agents.js`, `session.js`, `overview.js` | TASK-053, TASK-054 | A successful file tool event gives "Observed edit by ..."; failed calls and shell commands never do; "observed, not in that agent's report" flag; inferred links labelled; agent status only from events and reports |
| TASK-059 | README: connect a project and remove hooks manually | DEV | FR-042, FR-048 | `README.md` | TASK-057 | README has a "Connect a project" section and manual hook removal steps |
| TASK-060 | Developer tests and change report | DEV | FR-035 to FR-048, NFR-014, NFR-020, CON-011 | `tests/` (payload fixtures; hook run as a subprocess with a temporary data folder), change report, CHANGELOG | TASK-052 to TASK-059 | Std |
| TASK-061 | Real-event verification in the sandbox (4.7, DEC-023) | TST (ORC runs the `claude -p` step if a subagent cannot) | FR-035 to FR-038, FR-040, FR-041, FR-043, CON-008, CON-009 | `.sandbox/` only (Git-ignored); results in the test report | TASK-060 | A throwaway Git project under `D:\agentdesk\.sandbox\` is registered and connected through the wizard API (typed name `sandbox-test`, never the owner's name) on an AgentDesk instance using data folder `.sandbox\data` and a non-default port; a short `claude -p` run (never `--dangerously-skip-permissions`) starts a subagent and edits a file; the report quotes the sanitized payload shapes received and lists documented fields that did not appear (A-5); repeated with AgentDesk stopped (spool) and restarted (replay, no duplicates); AgentDesk's own repository is never connected |
| TASK-062 | Independent verification | TST | FR-015, FR-016, FR-035 to FR-048, NFR-014, NFR-020, CON-014, CON-019 | `tests/`, test report | TASK-061 | Std |
| TASK-063 | Read-only security audit | SEC (ORC records) | FR-023, FR-024, FR-036, FR-039, FR-040, FR-042, NFR-013, NFR-014, NFR-017, NFR-020, CON-012 | None written by SEC | TASK-062 | Std. Scope: hook never blocks, settings merge safety, the only allowed project write, global settings read scope, ingest token handling, self-test runs only AgentDesk's own script |
| TASK-064 | Triage, traceability and gate | PLN | All Phase 4 requirements, CON-019 | `docs/traceability-matrix.md`, PLN report | TASK-063 | Std |
| TASK-065 | Completion summary and progression | ORC | CON-006, CON-008, CON-015, CON-016 | Activity log | TASK-064 | Std; TASK-066 opened |

## 7. Phase 5: Engineering reports (TASK-066 to TASK-078)

**Goal.** Documentation, Testing, Security and Approval centres, file-change reviews and release readiness.
Migrations `0006` to `0009`. **Requirements:** FR-049 to FR-062 and the readiness and summary parts of FR-015.
Old outline numbers (5.1 to 5.5) are shown in brackets.

| Task | Title | Role | Requirements | Files | Depends on | Done when |
|---|---|---|---|---|---|---|
| TASK-066 | Phase 5 start; finalize DDL `0006`-`0009` | ORC, PLN | CON-005, CON-006, CON-010 | `docs/database-schema.md`, PLN report | TASK-065 | Std |
| TASK-067 | Migration `0006`; Documentation Centre (5.1) | DEV | FR-049, FR-050, NFR-005, NFR-015, NFR-016, CON-005 | `migrations/0006_documents.sql`, `app/services/documents.py`, `app/api/documents.py`, `app/static/js/pages/documents.js` | TASK-066 | Documents shown as escaped plain text (DEC-010): HTML, `<script>` and `javascript:` links appear literally and create no elements; Mermaid as source; content read live; Git history read-only; requirements index (Could) |
| TASK-068 | Migration `0007`; Testing Centre (5.2) | DEV | FR-051, FR-052, FR-055, FR-061, CON-005 | `migrations/0007_testing.sql`, `app/integrations/tracking/test_reports.py`, `app/services/testing.py`, `app/api/testing.py`, `app/static/js/pages/testing.js` | TASK-066 | Proposed and Executed separated, and the database refuses a proposed test linked to a run or a source/verification mismatch; observed test commands recorded with exit status; reported versus observed comparison shown |
| TASK-069 | Test-runner file import and verification rule (5.2, Could) | DEV | FR-053, FR-054, NFR-015 | `app/services/test_runner_files.py`, `app/api/testing.py` | TASK-068 | Size-capped; path confined to the project; `verified` only with an observed command and a modification time inside its window with 2 s tolerance (DEC-019), otherwise "Test-runner file, origin not verified"; the database refuses `verified` without a linked event |
| TASK-070 | Migration `0008`; Security Centre (5.3) | DEV | FR-056, FR-061, CON-005 | `migrations/0008_security.sql`, `app/integrations/tracking/security.py`, `app/services/security.py`, `app/api/security.py`, `app/static/js/pages/security.js` | TASK-066 | Statuses match the register's wording; permanent "never declared secure" notice; verdict labelled agent-reported |
| TASK-071 | Migration `0009`; Approval Centre (5.4) | DEV | FR-024, FR-057, FR-058, FR-061, FR-062, CON-005 | `migrations/0009_approvals.sql`, `app/integrations/tracking/decisions.py`, `app/services/approvals.py`, `app/api/approvals.py`, `app/static/js/pages/approvals.js` | TASK-066 | Review requests from facts; typed name required and the Windows account name never read; triggers block edits and deletes of decided approvals; `agentdesk` refused as decider; outdated-approval detection; "Copy decision"; project-file approvals shown separately with mismatches flagged; nothing written to project files |
| TASK-072 | File-change reviews (5.4) | DEV | FR-059 | `app/services/approvals.py`, `app/static/js/pages/file.js` | TASK-071 | Review pinned to the fingerprint or `deleted@<commit>`; evidence label unchanged; shown as outdated after the content changes; immutable |
| TASK-073 | Release readiness and Overview summaries (5.5) | DEV | FR-015, FR-060 | `app/services/readiness.py`, `app/api/overview.py`, `app/static/js/pages/overview.js` | TASK-068 to TASK-072 | Blockers as FR-060; only `verified` and `observed` runs clear the tests blocker; "changes requested" keeps the blocker (DEC-019); never "secure", never ready without a human release approval |
| TASK-074 | Developer tests and change report | DEV | FR-049 to FR-062, CON-011 | `tests/`, change report, CHANGELOG, README | TASK-067 to TASK-073 | Std |
| TASK-075 | Independent verification | TST | FR-015, FR-049 to FR-062, CON-014, CON-019 | `tests/`, test report | TASK-074 | Std |
| TASK-076 | Read-only security audit | SEC (ORC records) | FR-049, FR-053, FR-057 to FR-059, NFR-005, NFR-015, NFR-016, CON-012 | None written by SEC | TASK-075 | Std. Scope: script injection through documents, approval immutability, identity handling, import path confinement |
| TASK-077 | Triage, traceability and gate | PLN | All Phase 5 requirements, CON-019 | `docs/traceability-matrix.md`, PLN report | TASK-076 | Std |
| TASK-078 | Completion summary and progression | ORC | CON-006, CON-008, CON-015, CON-016 | Activity log | TASK-077 | Std; TASK-079 opened |

## 8. Phase 6: Validation, user manuals and final acceptance (TASK-079 to TASK-092)

**Goal.** Evidence that the whole application works on the owner's PC, the five user manuals written from the
implemented application, and final acceptance (§1.8). No migration. **Requirements:** NFR-021 to NFR-023,
FR-063 to FR-067, CON-017, CON-018, and regression of every earlier requirement. Old outline numbers (6.1 to 6.8)
are shown in brackets.

| Task | Title | Role | Requirements | Files | Depends on | Done when |
|---|---|---|---|---|---|---|
| TASK-079 | Phase 6 start | ORC, PLN | CON-006, CON-010 | Activity log, PLN report | TASK-078 | Std |
| TASK-080 | Concurrency and performance hardening (6.4) | DEV | NFR-021, NFR-022 | `app/database/connection.py` and services if needed, `tests/test_concurrency.py`, `tests/test_performance.py` | TASK-079 | With at least 4 parallel senders every event is stored exactly once with no lock error; with 10,000 stored events the first page of each list API returns within 1 s on the owner's PC |
| TASK-081 | User manual and quick start | DEV | FR-064, FR-067, NFR-012 | `docs/user-manual/AGENTDESK_USER_MANUAL.md`, `docs/user-manual/GETTING_STARTED.md` | TASK-079 | Written from the implemented code and running app; every FR-064 topic present; quick start at most about 150 lines |
| TASK-082 | Troubleshooting and architecture and maintenance guides | DEV | FR-065, FR-066 | `docs/user-manual/TROUBLESHOOTING.md`, `docs/user-manual/ARCHITECTURE_AND_MAINTENANCE.md` | TASK-079 | Error messages quoted from the code; migration list matches `migrations/`; test commands run as written |
| TASK-083 | Agent operating manual | DEV | FR-063 | `docs/user-manual/AGENT_OPERATING_MANUAL.md` | TASK-079 | Every FR-063 topic present; prompts use the task-ID format and the tracking paths in use; AgentDesk screens described as implemented |
| TASK-084 | Developer validation run and change report | DEV | NFR-023, FR-014, CON-011 | Change report, CHANGELOG, `README.md` (links to `docs/user-manual/`, final status) | TASK-080 to TASK-083 | Std; full suite run with actual output |
| TASK-085 | Validation A: functional end-to-end (6.1 to 6.4, 6.6) | TST | NFR-021, NFR-022, NFR-023, FR-015 to FR-062, CON-017 items 1, 2 and 8 | `tests/`, test report | TASK-084 | Through the API on sandbox projects with agent tracking files: the complete workflow; malformed, oversized, deeply nested and wrongly typed payloads against the ingestion endpoints and the hook script; three projects with correct routing and file-access isolation; concurrency and performance; the Git scenario suite (renames, deletes, binaries, large files, unusual names, commits during a session, non-Git folders) with evidence classification; full suite |
| TASK-086 | Validation B: operations (6.5, 6.7) | TST | FR-001, FR-002, FR-009 to FR-013, FR-018, FR-038, FR-040 to FR-042, FR-067, NFR-023, CON-003, CON-017 items 4 to 7 | `.sandbox/` only; test report | TASK-084 | Windows scripts on a fresh copy of the working tree under `.sandbox\` (tracked and untracked non-ignored files; own data folder and port, DEC-023): `setup.bat`, `start.bat`, `backup_db.py`, `restore_db.py`; migrations on a new database and as an upgrade from a Phase 1 database; backup and restore round trip; corrupted database refused, then restored; failed migration rolled back; hook install, event collection, shutdown and restart with spool replay in the sandbox; every page route and GUI workflow exercised through HTTP/API; GETTING_STARTED commands run as written |
| TASK-087 | Documentation check against the running application | TST | FR-014, FR-063 to FR-067, NFR-012, CON-017 item 9 | Test report | TASK-084 | Every command, route, page, label, status and message quoted in the five manuals and the README checked against the app and code; each mismatch reported as a finding |
| TASK-088 | Final independent security audit (6.8) | SEC (ORC records) | NFR-001 to NFR-020, FR-022 to FR-024, CON-002, CON-004, CON-009, CON-012, CON-017 item 3 | None written by SEC | TASK-085 to TASK-087 | Std. Full-product scope (architecture §11): dependency set, scripts, hook, wizard writes, path traversal, CSRF, Host header, sensitive files, refused folders, nothing written outside registered projects and `D:\agentdesk` |
| TASK-089 | Final triage, traceability and gate; consolidated manual checklist | PLN | All requirements, CON-014, CON-019 | `docs/traceability-matrix.md`, this plan (Appendix B), PLN report | TASK-088 | Std; every requirement row filled from saved reports; Appendix B compiled from the TST reports and matching the implemented app |
| TASK-090 | Final verification: regression rerun, Git diff, no unrelated or global files | ORC (TST runs the final suite) | CON-008, CON-009, CON-017 items 1, 10 and 11 | Activity log | TASK-089 | Final full-suite run recorded by a TST repeat pass if code changed after TASK-085; `git status --porcelain=v1 -uall` and `git diff --stat` reviewed file by file against the reports; nothing staged or committed; the TASK-023 metadata baseline compared and any change explained |
| TASK-091 | Final report (12 items) | ORC | CON-015, CON-018 | Conversation; activity log entry | TASK-090 | All 12 items of §1.8; every claim refers to a saved report |
| TASK-092 | Owner's consolidated manual checklist and final decision | Owner (ORC records) | CON-010, CON-014, CON-017, FR-002, FR-004 to FR-009, FR-014, FR-063 to FR-067, NFR-008 to NFR-010, NFR-012 | Appendices A and B | TASK-091 | The owner returns Pass, Fail or Notes for every step and decides; ORC records it; each Fail becomes a corrective task and the cycle repeats for it |

## 9. Reporting and records

| Record | Location | When |
|---|---|---|
| Completion summary (§1.6) | Conversation | End of each phase (a record, not an approval request) |
| Final report (§1.8) | Conversation, with an activity log entry | End of Phase 6 (TASK-091) |
| Owner explanation (§1.7) | Conversation | After each significant developer delegation, without pausing |
| Development report (Brief §10 points) | Change report | Each implementation task |
| Change report | `docs/agent-activity/change-reports/<TaskID>.md` | Each planner and developer task |
| Activity log entry and Summary row | `docs/agent-activity/activity-log.md` | Each task and each owner decision |
| Changelog | `CHANGELOG.md` (`[Unreleased]`) | User-visible changes |
| SRS and traceability matrix | `docs/srs.md`, `docs/traceability-matrix.md` | Maintained by PLN; matrix updated from saved reports at each phase end |
| Decision records | `docs/decisions/DEC-###-<slug>.md` | After the owner approves, or, for routine design decisions and minor clarifications, under the owner's delegated authority (OA) with that basis stated. Risk acceptances for Critical or High findings and validation waivers always need the owner |
| Test reports | `docs/testing/test-reports/` | Written by TST |
| Audit reports, findings register | `docs/security/` | Recorded by ORC from the security agent's returned report (§1.4) |

## Appendix A. Phase 1 manual browser verification checklist

Run by the owner once, at final acceptance, together with Appendix B (TASK-092; OD-2, DEC-020, CON-014). No
browser automation. Before starting, `scripts\setup.bat` must have been run once (TASK-017 does this). Use a
desktop browser on the same PC. Write Pass or Fail for each step, and notes for anything unexpected. Steps 3 to 12
describe Phase 1 placeholders; at final acceptance those pages show real content, so TASK-089 updates their
expected results to match the implemented pages.

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

## Appendix B. Later-phase manual browser checks

Compiled by PLN in TASK-089 from the manual-check lists in the Phase 2 to 6 testing reports, with expected results
that match the implemented application. Run by the owner with Appendix A in TASK-092. Until TASK-089, only the
planned areas are listed; they are not yet steps.

| Phase | Planned manual check areas (from the TST reports) |
|---|---|
| 2 | Evidence and verification badges, status pills and empty, loading and error states readable in light and dark themes; keyboard-only use of the new pages and detail views; 400 px width on Overview, Agents and Activity |
| 3 | Connection wizard steps 1-2 on a test folder, including a refused folder message; File Change Explorer and diff readability (unified and split); Reports paste preview |
| 4 | Wizard steps 3-5 wording, install preview and confirmation; connection health states; live agent and session views |
| 5 | Documents shown as plain text; Testing, Security and Approvals pages; decision form and file-change review; release readiness wording on the Overview |
| 6 | Following `GETTING_STARTED.md` from a stopped server; a true fresh clone after the owner commits (DEC-023); a quick read of the user manual against the screens |
