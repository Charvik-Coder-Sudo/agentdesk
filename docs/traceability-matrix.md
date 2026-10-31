# AgentDesk: requirements traceability matrix

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Draft (revision 1.1 of the 1.0 baseline: Phase 1 results and corrective tasks added; the 1.0 baseline stays in force) |
| Last updated | 2026-10-31 |
| Task ID | T-20261030-002-PLN (previous: T-20261030-001-PLN-2, T-20261030-001-PLN) |
| Maintained by | planner-agent |
| Related documents | [srs.md](srs.md), [architecture.md](architecture.md), [database-schema.md](database-schema.md), [implementation-plan.md](implementation-plan.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-PLN | First matrix: design element for every requirement; plan tasks for Phase 1 (E9) | FR-001 to FR-062, NFR-001 to NFR-023, CON-001 to CON-016 | Pending |
| 1.0 | 2026-10-30 | T-20261030-001-PLN-2 | Baseline. All requirements Approved; new rows FR-063 to FR-067, CON-017 to CON-019; plan tasks for Phases 2-6 (TASK-023 to TASK-092) on every row; new Impl. status column; TASK-022 references replaced by TASK-092 (DEC-020) | All 109 requirements | The owner, 2026-10-30 (blanket authorization, OA) |
| 1.1 | 2026-10-31 | T-20261030-002-PLN | Phase 1 triage. Implementation, Tests and Security findings columns filled for the Phase 1 rows and the affected constraints, from the saved reports T-20261030-002-DEV, T-20261030-002-TST and T-20261030-002-SEC. Corrective tasks TASK-093 to TASK-098 linked; TASK-025 and TASK-038 links for rescheduled parts. New row NFR-024 (Proposed). Phase 1 rows stay In progress until verified. | FR-001 to FR-014, NFR-001 to NFR-012, NFR-024 (new), CON-002, CON-004, CON-005, CON-008, CON-009, CON-011, CON-012, CON-019 | Pending user approval |

## How to read this matrix

- **Design element**: `arch` = [architecture.md](architecture.md), `schema` = [database-schema.md](database-schema.md),
  `plan` = [implementation-plan.md](implementation-plan.md); § = section; DEC = `docs/decisions/`. File names are planned files.
- **Plan task**: TASK-### from implementation-plan.md §3 to §8. Tasks before "verify" implement the requirement;
  tasks after "verify" check it. Corrective tasks (TASK-093 onward) are added here when PLN assigns them.
- **Impl. status**: Not started (no developer task begun); In progress (developer task delegated and no saved report
  shows it implemented, or corrective tasks on it are still open); Implemented (a saved DEV report shows it implemented
  and no corrective task on it is open); Verified (a saved TST report shows its acceptance criteria passed and, where
  security applies, the latest security report raises no open Critical or High finding on it). For constraints, In
  progress means the rule is being applied and not yet verified.
  On 2026-10-31 (T-20261030-002-PLN) the first Phase 1 cycle has saved DEV, TST and SEC reports. All Phase 1 rows stay
  In progress until TASK-093 to TASK-098 are verified by the repeat passes (T-20261030-002-TST-2, -SEC-2) and the
  gate is recorded (T-20261030-002-PLN-2).
- **Implementation, Tests, Security findings**: filled only from saved developer, testing and security reports.
  `-` means no such report exists yet, or the saved reports name nothing for that row.
  - Test group names (TST-SEC, TST-SRV, TST-DB, TST-BAK, TST-CFG, TST-GUI, TST-JS, TST-WIN, TST-ISO) and manual
    runs (M1 to M8) are those of T-20261030-002-TST §2 and §3.
  - "Passed (partly)" means the automatable part passed and the rest is in Appendix A (owner, TASK-092).
  - Security findings show the status in the findings register at the time of this update.
- **Status** is copied from [srs.md](srs.md): 109 requirements are Approved and NFR-024 is Proposed (SRS §5.0).

## Phase 1 requirements

| Requirement | Status | Impl. status | Design element | Plan task (TASK-###) | Implementation (files, DEV task ID) | Tests (test IDs, result, TST task ID) | Security findings (SEC-###) | Last updated (task ID) |
|---|---|---|---|---|---|---|---|---|
| FR-001 | Approved | In progress | arch §4.4 `scripts/setup.bat`; §14; DEC-018 | TASK-003, TASK-013; corrective TASK-098; verify TASK-017, TASK-018, TASK-086 | `scripts/setup.bat`, `requirements.txt`, `requirements.lock.txt`, `requirements-dev.txt` (T-20261030-002-DEV) | TST-WIN, M1-M3: Passed; criterion 5 by script review only (T-20261030-002-TST) | SEC-014 (Open), SEC-010 (Open) | T-20261030-002-PLN |
| FR-002 | Approved | In progress | arch §4.4 `scripts/start.bat`; `app/__main__.py` (plan TASK-009) | TASK-009, TASK-013; corrective TASK-098 (README, O-3); verify TASK-017, TASK-018, TASK-086, TASK-092 | `scripts/start.bat`, `app/__main__.py` (T-20261030-002-DEV) | TST-WIN, TST-SRV, M4: Passed; a fake browser launcher received the URL, so a real browser was not observed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-003 | Approved | In progress | arch §4.1 `app/api/system.py` (`GET /api/v1/health`) | TASK-008; corrective TASK-094 (HEAD, O-2); verify TASK-015, TASK-018 | `app/api/system.py`, `app/models/system.py` (T-20261030-002-DEV) | test_health, TST-SRV, TST-SEC: Passed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-004 | Approved | In progress | arch §4.3 `app/static/js/app.js` (health polling) | TASK-011; corrective TASK-097 (testability); verify TASK-018, TASK-092 | `app/static/js/app.js` (T-20261030-002-DEV) | TST-GUI, TST-JS: Passed (partly); browser timing in Appendix A steps 2, 23, 24 (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-005 | Approved | In progress | arch §10.1, §10.2; `index.html`, `js/router.js` | TASK-010, TASK-011; corrective TASK-097 (O-5); verify TASK-015, TASK-018, TASK-092 | `app/static/index.html`, `app/static/js/router.js` (T-20261030-002-DEV) | TST-GUI, TST-JS router, test_static: Passed; Back and Forward in Appendix A (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-006 | Approved | In progress | arch §2 P9, §10.1 (phase column); `js/pages/placeholder.js` | TASK-012; verify TASK-018 (placeholders are replaced by real pages in Phases 2-5) | `app/static/js/pages/placeholder.js` (T-20261030-002-DEV) | TST-GUI, TST-JS placeholder: Passed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-007 | Approved | In progress | arch §10.2 (themes); `js/theme.js`, `css/app.css` | TASK-010, TASK-011; TASK-025 (theme before first paint, rescheduled DEV limitation 2); verify TASK-018, TASK-092 | `app/static/js/theme.js`, `app/static/css/app.css` (T-20261030-002-DEV) | TST-JS theme, TST-GUI: Passed (partly); persistence across real reloads in Appendix A steps 15-17 (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-008 | Approved | In progress | arch §10.1 `#/settings`, §12; `GET /api/v1/system`, `js/pages/settings.js`; DEC-009 | TASK-008, TASK-012; corrective TASK-097 (O-4); verify TASK-015, TASK-018, TASK-092 | `app/api/system.py`, `app/models/system.py`, `app/static/js/pages/settings.js` (T-20261030-002-DEV) | TST-GUI, TST-JS settings, test_static: Passed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-009 | Approved | In progress | arch §12 (backups), §11 Errors; `app/database/backup.py`, `POST /api/v1/system/backups` | TASK-007, TASK-008, TASK-012; corrective TASK-093; verify TASK-015, TASK-018, TASK-086, TASK-092 | `app/database/backup.py`, `app/api/system.py`, `app/static/js/pages/settings.js` (T-20261030-002-DEV) | TST-BAK, TST-SRV, TST-JS settings: Passed (T-20261030-002-TST) | SEC-004 (Open), SEC-012 (Open) | T-20261030-002-PLN |
| FR-010 | Approved | In progress | arch §12 (backups); `backup.py`, `app/main.py` startup sequence | TASK-007, TASK-009; corrective TASK-093; verify TASK-015, TASK-018, TASK-086 | `app/database/backup.py`, `app/main.py` (T-20261030-002-DEV) | TST-DB, TST-BAK: **Failed**: D-1, `test_tst_twelve_backups_in_one_second_keep_the_newest_ten` (T-20261030-002-TST) | SEC-004 (Open) | T-20261030-002-PLN |
| FR-011 | Approved | In progress | arch §4.4, §12 (recovery), §11 Database files; `scripts/backup_db.py`, `scripts/restore_db.py` | TASK-007, TASK-014; corrective TASK-093; verify TASK-015, TASK-018, TASK-019, TASK-086 | `scripts/backup_db.py`, `scripts/restore_db.py`, `app/database/backup.py` (T-20261030-002-DEV) | TST-CFG, TST-BAK: Passed (T-20261030-002-TST) | SEC-002 (Open), SEC-003 (Open), SEC-015 (Open) | T-20261030-002-PLN |
| FR-012 | Approved | In progress | arch §12 (migrations); schema §1, §2, §3; `app/database/migrations.py`, `migrations/0001_foundation.sql`; DEC-011, DEC-025 | TASK-006, TASK-009; corrective TASK-093 (anchors), TASK-095; verify TASK-015, TASK-018, TASK-086 | `app/database/migrations.py`, `migrations/0001_foundation.sql`, `app/main.py` (T-20261030-002-DEV) | TST-DB: criteria (1)-(6) passed; **Failed** for the empty-folder edge case: D-3, `test_tst_empty_migrations_folder_gives_a_clean_startup_error` (T-20261030-002-TST) | SEC-015 (Open) | T-20261030-002-PLN |
| FR-013 | Approved | In progress | arch §12 (recovery); `app/main.py` startup sequence | TASK-009; verify TASK-015, TASK-018, TASK-019, TASK-086 | `app/main.py`, `app/database/connection.py` (read-only check) (T-20261030-002-DEV) | TST-DB, TST-SRV, test_integrity: Passed; observation O-1 is not a defect (T-20261030-002-TST) | - | T-20261030-002-PLN |
| FR-014 | Approved | In progress | plan TASK-016; `README.md` | TASK-016, TASK-059, TASK-084; corrective TASK-098; verify TASK-018, TASK-087, TASK-092 | `README.md` (T-20261030-002-DEV) | M7: Passed (partly), keyword check only; owner review in Appendix A step 27 (T-20261030-002-TST) | - | T-20261030-002-PLN |
| NFR-001 | Approved | In progress | arch §11 Network; `app/core/config.py` | TASK-004, TASK-009; verify TASK-015, TASK-018, TASK-019, TASK-088 | `app/core/config.py`, `app/__main__.py` (T-20261030-002-DEV) | TST-CFG, TST-SRV, test_config: Passed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| NFR-002 | Approved | In progress | arch §11 DNS rebinding, Cross-site requests; `app/core/security.py` | TASK-005; corrective TASK-094 (SEC-006); verify TASK-015, TASK-017, TASK-018, TASK-019, TASK-088 | `app/core/security.py` (T-20261030-002-DEV) | TST-SEC, TST-SRV, test_security: Passed (T-20261030-002-TST) | SEC-006 (Open) | T-20261030-002-PLN |
| NFR-003 | Approved | In progress | arch §11 Cross-site requests; `security.py`, `GET /api/v1/session`, `js/api.js`; DEC-025 | TASK-005, TASK-008, TASK-011, TASK-038; corrective TASK-094 (SEC-006, SEC-008); verify TASK-015, TASK-017, TASK-018, TASK-019, TASK-088 | `app/core/security.py`, `app/api/system.py`, `app/static/js/api.js` (T-20261030-002-DEV) | TST-SEC, TST-SRV, TST-JS api: Passed (T-20261030-002-TST) | SEC-006 (Open), SEC-008 (Open) | T-20261030-002-PLN |
| NFR-004 | Approved | In progress | arch §11 Browser hardening; `security.py`; DEC-025 | TASK-005; corrective TASK-094 (SEC-007); verify TASK-015, TASK-018, TASK-019, TASK-033, TASK-088 | `app/core/security.py` (T-20261030-002-DEV) | TST-SEC (13 response kinds), TST-SRV: Passed (T-20261030-002-TST) | SEC-007 (Open) | T-20261030-002-PLN |
| NFR-005 | Approved | In progress | arch §4.3, §11 Browser hardening; `js/dom.js`, `index.html`; DEC-010 | TASK-010, TASK-011, TASK-012, TASK-025, TASK-067; corrective TASK-097 (SEC-009); verify TASK-018, TASK-019, TASK-033, TASK-076, TASK-088 | `app/static/js/dom.js`, `app/static/index.html` (T-20261030-002-DEV) | TST-GUI scans, TST-JS: Passed; the CSP console check is in Appendix A (T-20261030-002-TST) | SEC-009 (Open) | T-20261030-002-PLN |
| NFR-006 | Approved | In progress | arch §11 Errors; `app/main.py` | TASK-009; corrective TASK-093 (SEC-012), TASK-094; verify TASK-015, TASK-018, TASK-019, TASK-088 | `app/core/security.py`, `app/api/errors.py`, `app/main.py` (T-20261030-002-DEV) | TST-SEC (500 variants), TST-SRV: Passed (T-20261030-002-TST) | SEC-012 (Open) | T-20261030-002-PLN |
| NFR-007 | Approved | In progress | arch §12 Logs, §11 Logs; `app/core/log_setup.py` | TASK-004; corrective TASK-094 (SEC-001); verify TASK-018, TASK-019, TASK-088 | `app/core/log_setup.py`, `app/core/security.py` (T-20261030-002-DEV) | test_security, TST-SRV (token absent from log): Passed (T-20261030-002-TST) | **SEC-001 (Medium, Open)** | T-20261030-002-PLN |
| NFR-008 | Approved | In progress | arch §10.2 Keyboard; `index.html`, `js/router.js` | TASK-010, TASK-011, TASK-026; verify TASK-018, TASK-032, TASK-092 | `app/static/index.html`, `app/static/js/router.js`, `app/static/js/app.js` (T-20261030-002-DEV) | TST-GUI, TST-JS router focus: Passed (partly); keyboard walk in Appendix A steps 19-21 (T-20261030-002-TST) | - | T-20261030-002-PLN |
| NFR-009 | Approved | In progress | arch §10.2 Themes; `css/app.css` | TASK-010, TASK-025; verify TASK-018, TASK-032, TASK-092 | `app/static/css/app.css` (T-20261030-002-DEV) | TST-GUI (token contrast in both themes, reduced motion): Passed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| NFR-010 | Approved | In progress | arch §10.2; `css/app.css` (layout) | TASK-010; verify TASK-018, TASK-032, TASK-092 | `app/static/css/app.css` (T-20261030-002-DEV) | TST-GUI: media queries only; not tested in a layout engine; Appendix A step 22 (T-20261030-002-TST) | - | T-20261030-002-PLN |
| NFR-011 | Approved | In progress | arch §3.1, §13 (`data/`), §11 Local data privacy; `.gitignore`, `config.py` | TASK-003, TASK-004; corrective TASK-095, TASK-096; verify TASK-017, TASK-018, TASK-019 | `.gitignore`, `app/core/config.py`, `app/main.py` (T-20261030-002-DEV) | TST-CFG, TST-ISO: ignore entries Passed; **Failed** for D-2 (data folder that is a file, or lies below a file) (T-20261030-002-TST) | SEC-005 (Open), SEC-013 (Open) | T-20261030-002-PLN |
| NFR-012 | Approved | In progress | arch §1; `js/pages/*.js`, `README.md`, `docs/user-manual/` | TASK-012, TASK-016, TASK-081 to TASK-083; corrective TASK-095, TASK-098; verify TASK-018, TASK-087, TASK-092 | Page modules, `README.md`, startup messages (T-20261030-002-DEV) | Passed (partly): messages checked in tests; D-2 and D-3 give raw errors; owner review in Appendix A (T-20261030-002-TST) | - | T-20261030-002-PLN |

## Constraints (all phases)

SEC tasks = TASK-019, TASK-033, TASK-048, TASK-063, TASK-076, TASK-088. TST tasks = TASK-018, TASK-032, TASK-047,
TASK-061, TASK-062, TASK-075, TASK-085 to TASK-087. Phase-start tasks = TASK-023, TASK-036, TASK-051, TASK-066,
TASK-079. Gate tasks (PLN) = TASK-020, TASK-034, TASK-049, TASK-064, TASK-077, TASK-089. Completion summaries
(ORC) = TASK-021, TASK-035, TASK-050, TASK-065, TASK-078.

| Requirement | Status | Impl. status | Design element | Plan task (TASK-###) | Implementation (files, DEV task ID) | Tests (test IDs, result, TST task ID) | Security findings (SEC-###) | Last updated (task ID) |
|---|---|---|---|---|---|---|---|---|
| CON-001 | Approved | In progress | arch §4, §14; DEC-001 | All DEV tasks; verify SEC tasks | - | - | - | T-20261030-001-PLN-2 |
| CON-002 | Approved | In progress | arch §2 P6, §11 Network | TASK-003; corrective TASK-094 (SEC-011); verify SEC tasks | No external runtime URL (T-20261030-002-DEV, V8) | - | SEC-011 (Open) | T-20261030-002-PLN |
| CON-003 | Approved | In progress | arch §14 | TASK-013; verify TASK-017, TASK-086 | - | - | - | T-20261030-001-PLN-2 |
| CON-004 | Approved | In progress | arch §2 P7, §14, §15 item 21; DEC-010, DEC-018, DEC-025 | TASK-002 (done), TASK-003; verify SEC tasks | `requirements.txt`, `requirements.lock.txt` (from `pip freeze`, reproduced exactly, V1a), `requirements-dev.txt` (T-20261030-002-DEV) | TST-WIN (pins), M3: Passed (T-20261030-002-TST) | SEC-010 (Open; proposed Accepted with justification, DEC-025) | T-20261030-002-PLN |
| CON-005 | Approved | In progress | schema §2, §3; DEC-011 | TASK-006, TASK-037, TASK-040, TASK-043, TASK-053, TASK-067 to TASK-071 (DDL finalized in TASK-036, TASK-051, TASK-066); verify TST tasks | `migrations/0001_foundation.sql` (T-20261030-002-DEV) | test_migrations, TST-DB: Passed; exactly two tables, schema version 1 (T-20261030-002-TST) | - | T-20261030-002-PLN |
| CON-006 | Approved | In progress | plan §1.2, §1.6; DEC-013, DEC-020 | TASK-001, phase-start tasks, gate tasks, completion summaries | - | - | - | T-20261030-001-PLN-2 |
| CON-007 | Approved | In progress | arch §13 | All DEV tasks; verify TST tasks | - | - | - | T-20261030-001-PLN-2 |
| CON-008 | Approved | In progress | plan §1.5; DEC-015, DEC-023 | TASK-001, TASK-017, TASK-046, TASK-061, completion summaries; verify TASK-090 | DEV ran no Git write command; commit `44afe9f` was made by the owner outside the agents (recorded in T-20261030-001-ORC-3) (T-20261030-002-DEV) | - | - | T-20261030-002-PLN |
| CON-009 | Approved | In progress | plan §1.5; DEC-023; arch §11 Logs and Database files | TASK-013, TASK-017, TASK-024, TASK-061, TASK-086; corrective TASK-095 (SEC-013), TASK-098 (SEC-014, DEV limitation 7); verify SEC tasks, TASK-090 | `scripts/setup.bat` (TEMP/TMP in `.sandbox\tmp`, no pip cache), `pytest.ini` (`--basetemp`) (T-20261030-002-DEV) | TST-ISO, M6: Passed (T-20261030-002-TST) | SEC-013 (Open), SEC-014 (Open) | T-20261030-002-PLN |
| CON-010 | Approved | In progress | arch §2 P10; DEC-020 | TASK-002, phase-start tasks, gate tasks; verify TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| CON-011 | Approved | In progress | plan §1.3; DEC-013 | TASK-015, TASK-031, TASK-046, TASK-060, TASK-074, TASK-084; verify TST tasks | 122 developer tests (T-20261030-002-DEV) | Developer tests reviewed and re-run (122 passed); 480 pytest and 39 Node tests added; full suite 598 passed, 4 failed (T-20261030-002-TST) | - | T-20261030-002-PLN |
| CON-012 | Approved | In progress | arch §11.1, §15; plan §1.4 (tightened by T-20261030-002-PLN); DEC-016 | SEC tasks | - | - | T-20261030-002-SEC recorded by ORC; repository unchanged; one scratchpad file outside the repository self-reported and deleted by ORC (activity log) | T-20261030-002-PLN |
| CON-013 | Approved | In progress | plan §1.5; DEC-020 | Every DEV delegation (TASK-003 to TASK-017 and all Phase 2-6 DEV tasks) | - | - | - | T-20261030-001-PLN-2 |
| CON-014 | Approved | In progress | plan §1.3, §1.5, Appendices A and B; DEC-014, DEC-020 | TST tasks (GUI through HTTP/API), TASK-089; verify TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| CON-015 | Approved | In progress | plan §1.6; DEC-020 | Completion summaries; TASK-091 | - | - | - | T-20261030-001-PLN-2 |
| CON-016 | Approved | In progress | plan §1.7 | ORC after each developer delegation; completion summaries | - | - | - | T-20261030-001-PLN-2 |
| CON-017 | Approved | Not started | plan §1.8; DEC-021 | TASK-061, TASK-085 to TASK-090; verify TASK-091 | - | - | - | T-20261030-001-PLN-2 |
| CON-018 | Approved | Not started | plan §1.8; DEC-021 | TASK-091 | - | - | - | T-20261030-001-PLN-2 |
| CON-019 | Approved | In progress | plan §1.3, §1.6, §3.3; DEC-020, DEC-022 (Amendment 1) | TASK-024; corrective pass rules in plan §3.3; verify TST tasks, SEC tasks, gate tasks | Two developer test fixes recorded with reasons; nothing skipped (T-20261030-002-DEV) | No existing test changed; 0 skipped; the 4 failing tests stay failing until fixed (T-20261030-002-TST) | No severity changed (T-20261030-002-PLN triage) | T-20261030-002-PLN |

## Phase 2 to 6 requirements

| Requirement | Status | Impl. status | Design element | Plan task (TASK-###) | Implementation (files, DEV task ID) | Tests (test IDs, result, TST task ID) | Security findings (SEC-###) | Last updated (task ID) |
|---|---|---|---|---|---|---|---|---|
| FR-015 | Approved | Not started | arch §10.1 `#/overview`, §2 P9 | TASK-028, TASK-045, TASK-058, TASK-073; verify TASK-032, TASK-047, TASK-062, TASK-075, TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| FR-016 | Approved | Not started | arch §10.1 `#/agents`; schema §5 `agents` | TASK-029, TASK-058; verify TASK-032, TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-017 | Approved | Not started | arch §10.1 `#/activity`; schema §4 `activity_events` | TASK-025, TASK-030, TASK-045; verify TASK-032, TASK-047 | - | - | - | T-20261030-001-PLN-2 |
| FR-018 | Approved | Not started | arch §10.1, §10.2 | TASK-026, TASK-030; verify TASK-032, TASK-086 | - | - | - | T-20261030-001-PLN-2 |
| FR-019 | Approved | Not started | arch §2 P9 | TASK-027 (removed again by TASK-045); verify TASK-032, TASK-033 | - | - | - | T-20261030-001-PLN-2 |
| FR-020 | Approved | Not started | arch §10.2 (auto-refresh) | TASK-027; verify TASK-032 | - | - | - | T-20261030-001-PLN-2 |
| FR-021 | Approved | Not started | arch §7 steps 1-2; schema §4 `projects`, `git_checkpoints` | TASK-040, TASK-041; verify TASK-047 | - | - | - | T-20261030-001-PLN-2 |
| FR-022 | Approved | Not started | arch §7 step 1 (refused folders), §11 Project folders, §15 item 15 | TASK-041; verify TASK-047, TASK-048, TASK-088 | - | - | - | T-20261030-001-PLN-2 |
| FR-023 | Approved | Not started | arch §2 P3, §3.1, §3.2; DEC-006 | TASK-040 to TASK-043, TASK-057; verify TASK-046, TASK-047, TASK-048, TASK-063, TASK-088 | - | - | - | T-20261030-001-PLN-2 |
| FR-024 | Approved | Not started | arch §2 P4, §3.2; schema §6 `approvals.decided_by` CHECK; DEC-015, DEC-017 | TASK-039, TASK-056, TASK-071; verify TASK-048, TASK-063, TASK-088 | - | - | - | T-20261030-001-PLN-2 |
| FR-025 | Approved | Not started | arch §4.1, §11; schema §4 `activity_events` | TASK-037, TASK-038; verify TASK-047, TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| FR-026 | Approved | Not started | arch §4.1 `app/integrations/git/`, §11 Git; schema §4 `0003_git_tracking.sql` | TASK-039, TASK-040; verify TASK-047, TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| FR-027 | Approved | Not started | arch §10.1 `#/files`; schema §4 `file_changes` | TASK-042; verify TASK-047 | - | - | - | T-20261030-001-PLN-2 |
| FR-028 | Approved | Not started | arch §10.1 `#/files/:projectId/:path`, §11 File access; DEC-005 | TASK-042; verify TASK-047, TASK-048 | - | - | - | T-20261030-001-PLN-2 |
| FR-029 | Approved | Not started | arch §5.2, §5.3; schema §4 (derivation notes); DEC-004 | TASK-025, TASK-044; verify TASK-047, TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| FR-030 | Approved | Not started | arch §2 P2, §5.3 rules R-E and R-F; DEC-004 | TASK-044; verify TASK-047, TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| FR-031 | Approved | Not started | arch §5.3 (discrepancy flags) | TASK-043, TASK-044, TASK-058; verify TASK-047, TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-032 | Approved | Not started | arch §8; schema §4 `agent_reports`, `report_items` | TASK-043; verify TASK-047 | - | - | - | T-20261030-001-PLN-2 |
| FR-033 | Approved | Not started | arch §9; schema §4 `agent_reports` (`manual_paste`) | TASK-043; verify TASK-047, TASK-048 | - | - | - | T-20261030-001-PLN-2 |
| FR-034 | Approved | Not started | arch §2 P9 | TASK-045; verify TASK-047 | - | - | - | T-20261030-001-PLN-2 |
| FR-035 | Approved | Not started | arch §4.2, §6.2, §6.3; DEC-002 | TASK-052; verify TASK-061, TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-036 | Approved | Not started | arch §2 P5, §6.2; DEC-002 | TASK-052; verify TASK-061, TASK-062, TASK-063 | - | - | - | T-20261030-001-PLN-2 |
| FR-037 | Approved | Not started | arch §6.1, §6.4; schema §5 `sessions`, `tasks` | TASK-051 (reference recheck), TASK-053; verify TASK-061, TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-038 | Approved | Not started | arch §6.5; DEC-002 | TASK-054; verify TASK-061, TASK-062, TASK-086 | - | - | - | T-20261030-001-PLN-2 |
| FR-039 | Approved | Not started | arch §7 step 3, §3.1; DEC-017 | TASK-056; verify TASK-062, TASK-063 | - | - | - | T-20261030-001-PLN-2 |
| FR-040 | Approved | Not started | arch §7 step 4; schema §5 `project_connections`; DEC-003, DEC-012 | TASK-057; verify TASK-061, TASK-062, TASK-063, TASK-086 | - | - | - | T-20261030-001-PLN-2 |
| FR-041 | Approved | Not started | arch §7 step 5; DEC-012 | TASK-057; verify TASK-061, TASK-062, TASK-086 | - | - | - | T-20261030-001-PLN-2 |
| FR-042 | Approved | Not started | arch §7 (Disconnect); DEC-012 | TASK-057, TASK-059; verify TASK-062, TASK-063, TASK-086 | - | - | - | T-20261030-001-PLN-2 |
| FR-043 | Approved | Not started | arch §5.2, §5.3 rules R-B and R-F; DEC-004 | TASK-058; verify TASK-061, TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-044 | Approved | Not started | arch §6.4; schema §5 `tasks.link_confidence` | TASK-053, TASK-058; verify TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-045 | Approved | Not started | arch §6.1, §6.3; schema §4 `agent_reports.summary` CHECK; DEC-008 | TASK-053; verify TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-046 | Approved | Not started | arch §6.6 | TASK-055; verify TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-047 | Approved | Not started | arch §10.1 `#/agents`, §6.5 | TASK-058; verify TASK-062 | - | - | - | T-20261030-001-PLN-2 |
| FR-048 | Approved | Not started | arch §7; README | TASK-057, TASK-059; verify TASK-062, TASK-087 | - | - | - | T-20261030-001-PLN-2 |
| FR-049 | Approved | Not started | arch §10.3 Documentation; schema §6 `documents`; DEC-010 | TASK-067; verify TASK-075, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| FR-050 | Approved | Not started | arch §10.3 Documentation; schema §6 `requirements` | TASK-067; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-051 | Approved | Not started | arch §10.3 Testing; schema §6 `test_runs`, `test_cases` | TASK-068; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-052 | Approved | Not started | arch §10.3 Testing; schema §6 `test_runs` (`hook_observed`); DEC-007 | TASK-068; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-053 | Approved | Not started | arch §10.3 Testing; schema §6 `test_runs` (`test_runner_file`) | TASK-069; verify TASK-075, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| FR-054 | Approved | Not started | arch §10.3 Testing (test-runner file rule), §15 item 16; schema §6 `test_runs` CHECKs; DEC-019 | TASK-069; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-055 | Approved | Not started | arch §10.3 Testing | TASK-068; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-056 | Approved | Not started | arch §10.3 Security; schema §6 `security_findings` | TASK-070; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-057 | Approved | Not started | arch §10.3 Approvals; schema §6 `approvals`; DEC-009 | TASK-071; verify TASK-075, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| FR-058 | Approved | Not started | arch §10.3 Approvals; schema §6 approvals triggers | TASK-071; verify TASK-075, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| FR-059 | Approved | Not started | arch §10.3 File-change reviews; schema §6 `approvals` (`file_change_review`); DEC-019 | TASK-072; verify TASK-075, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| FR-060 | Approved | Not started | arch §10.3 Release readiness; DEC-019 | TASK-073; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-061 | Approved | Not started | arch §8 (Phase 5 rows) | TASK-068, TASK-070, TASK-071; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-062 | Approved | Not started | arch §10.3 Approvals | TASK-071; verify TASK-075 | - | - | - | T-20261030-001-PLN-2 |
| FR-063 | Approved | Not started | `docs/user-manual/AGENT_OPERATING_MANUAL.md`; plan §1.8; DEC-021 | TASK-083; verify TASK-087, TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| FR-064 | Approved | Not started | `docs/user-manual/AGENTDESK_USER_MANUAL.md`; DEC-021 | TASK-081; verify TASK-087, TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| FR-065 | Approved | Not started | `docs/user-manual/TROUBLESHOOTING.md`; DEC-021 | TASK-082; verify TASK-087, TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| FR-066 | Approved | Not started | `docs/user-manual/ARCHITECTURE_AND_MAINTENANCE.md`; DEC-021 | TASK-082; verify TASK-087, TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| FR-067 | Approved | Not started | `docs/user-manual/GETTING_STARTED.md`; DEC-021 | TASK-081; verify TASK-086, TASK-087, TASK-092 | - | - | - | T-20261030-001-PLN-2 |
| NFR-013 | Approved | Not started | arch §2 P8, §6.3, §11 Data at rest; DEC-005 | TASK-038, TASK-043, TASK-052, TASK-053; verify TASK-047, TASK-048, TASK-062, TASK-063 | - | - | - | T-20261030-001-PLN-2 |
| NFR-014 | Approved | Not started | arch §6.3 (shell command); DEC-007 | TASK-052, TASK-053; verify TASK-062, TASK-063 | - | - | - | T-20261030-001-PLN-2 |
| NFR-015 | Approved | Not started | arch §11 File access | TASK-041, TASK-042, TASK-067, TASK-069; verify TASK-047, TASK-048, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| NFR-016 | Approved | Not started | arch §11 Sensitive files | TASK-042, TASK-067; verify TASK-047, TASK-048, TASK-076 | - | - | - | T-20261030-001-PLN-2 |
| NFR-017 | Approved | Not started | arch §3.2, §11 Commands | TASK-039, TASK-056, TASK-057; verify TASK-048, TASK-063, TASK-088 | - | - | - | T-20261030-001-PLN-2 |
| NFR-018 | Approved | Not started | arch §11 Git | TASK-039; verify TASK-047, TASK-048 | - | - | - | T-20261030-001-PLN-2 |
| NFR-019 | Approved | Not started | arch §6.2, §11; schema §1 (CHECK limits) | TASK-038, TASK-053; verify TASK-047, TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| NFR-020 | Approved | Not started | arch §11 Hook ingestion | TASK-038 (token), TASK-052, TASK-053; verify TASK-062, TASK-063 | - | - | - | T-20261030-001-PLN-2 |
| NFR-021 | Approved | Not started | arch §12 SQLite | TASK-080; verify TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| NFR-022 | Approved | Not started | arch §10.2 (pagination) | TASK-080; verify TASK-085 | - | - | - | T-20261030-001-PLN-2 |
| NFR-023 | Approved | Not started | plan §8, §1.8; DEC-023 | TASK-084; verify TASK-085 to TASK-088, TASK-090 | - | - | - | T-20261030-001-PLN-2 |
| NFR-024 | Proposed | Not started | arch §11 Local data privacy, Hook ingestion; §15 item 20; DEC-024, DEC-009 | TASK-038 (amended; Phase 1 groundwork in TASK-096); verify TASK-047, TASK-048, TASK-088 | - | - | SEC-005 (Open; token part) | T-20261030-002-PLN |

## Coverage check (T-20261030-001-PLN-2, updated T-20261030-002-PLN)

Every one of the 110 requirements has at least one implementing or verifying task above. Rows: Phase 1
FR-001 to FR-014 and NFR-001 to NFR-012 (26); constraints CON-001 to CON-019 (19); Phases 2 to 6 FR-015 to
FR-067 and NFR-013 to NFR-024 (65).

Corrective tasks of the first Phase 1 cycle (T-20261030-002-PLN), each linked from the rows above:

| Corrective task | Findings | Requirement rows |
|---|---|---|
| TASK-093 | D-1, SEC-002, SEC-003, SEC-004, SEC-012, SEC-015 | FR-009, FR-010, FR-011, FR-012, NFR-006 |
| TASK-094 | SEC-001, SEC-006, SEC-007, SEC-008, SEC-011, O-2 | FR-003, NFR-002, NFR-003, NFR-004, NFR-006, NFR-007, CON-002 |
| TASK-095 | D-2, D-3, O-7, SEC-013 | FR-012, NFR-011, NFR-012, CON-009 |
| TASK-096 | SEC-005 (Phase 1 part) | NFR-011 (groundwork for NFR-024) |
| TASK-097 | SEC-009, O-4, O-5, app.js testability | FR-004, FR-005, FR-008, NFR-005 |
| TASK-098 | SEC-014, O-3, DEV limitation 7 | FR-001, FR-002, FR-014, NFR-012, CON-009 |
| TASK-025 (Phase 2, rescheduled part) | DEV limitation 2 (theme flash) | FR-007 |
| TASK-038 (Phase 3, rescheduled part) | SEC-005 (ingest-token part) | NFR-024 |
