# AgentDesk: requirements traceability matrix

| Field | Value |
|---|---|
| Version | 0.1 |
| Status | Draft |
| Last updated | 2026-10-30 |
| Task ID | T-20261030-001-PLN |
| Maintained by | planner-agent |
| Related documents | [srs.md](srs.md), [architecture.md](architecture.md), [database-schema.md](database-schema.md), [implementation-plan.md](implementation-plan.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-PLN | First matrix: design element for every requirement; plan tasks for Phase 1 (E9) | FR-001 to FR-062, NFR-001 to NFR-023, CON-001 to CON-016 | Pending |

## How to read this matrix

- **Design element**: `arch` = [architecture.md](architecture.md), `schema` = [database-schema.md](database-schema.md),
  `plan` = [implementation-plan.md](implementation-plan.md); § = section. File names are planned files.
- **Plan task**: TASK-### from implementation-plan.md §3 (Phase 1 only). "verify" lists the tasks that check the requirement.
  Later phases get TASK IDs when the Planner confirms their scope at the start of that phase.
- **Implementation, Tests, Security findings**: filled only from saved developer, testing and security reports.
  `-` means no such report exists yet. No code has been written.
- Status is copied from [srs.md](srs.md). No requirement is Approved.

## Phase 1 requirements

| Requirement | Status | Design element | Plan task (TASK-###) | Implementation (files, DEV task ID) | Tests (test IDs, result, TST task ID) | Security findings (SEC-###) | Last updated (task ID) |
|---|---|---|---|---|---|---|---|
| FR-001 | Proposed | arch §4.4 `scripts/setup.bat`; §14 | TASK-003, TASK-013; verify TASK-017, TASK-018 | - | - | - | T-20261030-001-PLN |
| FR-002 | Proposed | arch §4.4 `scripts/start.bat`; `app/__main__.py` (plan TASK-009) | TASK-009, TASK-013; verify TASK-017, TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-003 | Proposed | arch §4.1 `app/api/system.py` (`GET /api/v1/health`) | TASK-008; verify TASK-015, TASK-018 | - | - | - | T-20261030-001-PLN |
| FR-004 | Proposed | arch §4.3 `app/static/js/app.js` (health polling) | TASK-011; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-005 | Proposed | arch §10.1, §10.2; `index.html`, `js/router.js` | TASK-010, TASK-011; verify TASK-015, TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-006 | Proposed | arch §2 P9, §10.1 (phase column); `js/pages/*.js` | TASK-012; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-007 | Proposed | arch §10.2 (themes); `js/theme.js`, `css/app.css` | TASK-010, TASK-011; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-008 | Proposed | arch §10.1 `#/settings`, §12; `GET /api/v1/system`, `js/pages/settings.js` | TASK-008, TASK-012; verify TASK-015, TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-009 | Proposed | arch §12 (backups); `app/database/backup.py`, `POST /api/v1/system/backups` | TASK-007, TASK-008, TASK-012; verify TASK-015, TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| FR-010 | Proposed | arch §12 (backups); `backup.py`, `app/main.py` startup sequence | TASK-007, TASK-009; verify TASK-015, TASK-018 | - | - | - | T-20261030-001-PLN |
| FR-011 | Proposed | arch §4.4, §12 (recovery); `scripts/backup_db.py`, `scripts/restore_db.py` | TASK-007, TASK-014; verify TASK-015, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| FR-012 | Proposed | arch §12 (migrations); schema §1, §2, §3; `app/database/migrations.py`, `migrations/0001_foundation.sql` | TASK-006, TASK-009; verify TASK-015, TASK-018 | - | - | - | T-20261030-001-PLN |
| FR-013 | Proposed | arch §12 (recovery); `app/main.py` startup sequence | TASK-009; verify TASK-015, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| FR-014 | Proposed | plan §3 TASK-016; `README.md` | TASK-016; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| NFR-001 | Proposed | arch §11 Network; `app/core/config.py` | TASK-004, TASK-009; verify TASK-015, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-002 | Proposed | arch §11 DNS rebinding; `app/core/security.py` | TASK-005; verify TASK-015, TASK-017, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-003 | Proposed | arch §11 Cross-site requests; `security.py`, `GET /api/v1/session`, `js/api.js` | TASK-005, TASK-008, TASK-011; verify TASK-015, TASK-017, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-004 | Proposed | arch §11 Browser hardening; `security.py` | TASK-005; verify TASK-015, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-005 | Proposed | arch §4.3, §11 Browser hardening; `js/dom.js`, `index.html` | TASK-010, TASK-011, TASK-012; verify TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-006 | Proposed | arch §11 Errors; `app/main.py` | TASK-009; verify TASK-015, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-007 | Proposed | arch §12 Logs; `app/core/log_setup.py` | TASK-004; verify TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-008 | Proposed | arch §10.2 Keyboard; `index.html`, `js/router.js` | TASK-010, TASK-011; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| NFR-009 | Proposed | arch §10.2 Themes; `css/app.css` | TASK-010; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| NFR-010 | Proposed | arch §10.2; `css/app.css` (layout) | TASK-010; verify TASK-018, TASK-022 | - | - | - | T-20261030-001-PLN |
| NFR-011 | Proposed | arch §3.1, §13 (`data/`); `.gitignore`, `config.py` | TASK-003, TASK-004; verify TASK-017, TASK-018, TASK-019 | - | - | - | T-20261030-001-PLN |
| NFR-012 | Proposed | arch §1; `js/pages/*.js`, `README.md` | TASK-012, TASK-016; verify TASK-022 | - | - | - | T-20261030-001-PLN |

## Constraints (all phases)

| Requirement | Status | Design element | Plan task (TASK-###) | Implementation (files, DEV task ID) | Tests (test IDs, result, TST task ID) | Security findings (SEC-###) | Last updated (task ID) |
|---|---|---|---|---|---|---|---|
| CON-001 | Proposed | arch §4, §14; DEC-001 | TASK-003 to TASK-014; verify TASK-019 | - | - | - | T-20261030-001-PLN |
| CON-002 | Proposed | arch §2 P6 | TASK-003; verify TASK-019 | - | - | - | T-20261030-001-PLN |
| CON-003 | Proposed | arch §14 | TASK-013; verify TASK-017 | - | - | - | T-20261030-001-PLN |
| CON-004 | Proposed | arch §2 P7, §14; DEC-010; SRS Q10 | TASK-002, TASK-003; verify TASK-019 | - | - | - | T-20261030-001-PLN |
| CON-005 | Proposed | schema §2, §3; DEC-011 | TASK-006; verify TASK-015, TASK-018 | - | - | - | T-20261030-001-PLN |
| CON-006 | Proposed | plan §1.2; DEC-013 | TASK-001, TASK-002, TASK-021, TASK-022 | - | - | - | T-20261030-001-PLN |
| CON-007 | Proposed | arch §13 | TASK-004 to TASK-012; verify TASK-018 | - | - | - | T-20261030-001-PLN |
| CON-008 | Proposed | plan §1.5; DEC-015 | TASK-001, TASK-017, TASK-021 | - | - | - | T-20261030-001-PLN |
| CON-009 | Proposed | plan §1.5 | TASK-013, TASK-017; verify TASK-019 | - | - | - | T-20261030-001-PLN |
| CON-010 | Proposed | arch §2 P10 | TASK-002; verify TASK-022 | - | - | - | T-20261030-001-PLN |
| CON-011 | Proposed | plan §1.3; DEC-013 | TASK-015, TASK-018 | - | - | - | T-20261030-001-PLN |
| CON-012 | Proposed | arch §11.1, §15; plan §1.4; DEC-016 | TASK-019 | - | - | - | T-20261030-001-PLN |
| CON-013 | Proposed | plan §1.5 | TASK-002; every delegation of TASK-003 to TASK-017 | - | - | - | T-20261030-001-PLN |
| CON-014 | Proposed | plan §1.5, Appendix A; DEC-014 | TASK-021, TASK-022 | - | - | - | T-20261030-001-PLN |
| CON-015 | Proposed | plan §1.6 | TASK-021 | - | - | - | T-20261030-001-PLN |
| CON-016 | Proposed | plan §1.7 | ORC after each developer delegation for TASK-003 to TASK-016; TASK-021 | - | - | - | T-20261030-001-PLN |

## Later-phase requirements (Draft)

| Requirement | Status | Design element | Plan task (TASK-###) | Implementation (files, DEV task ID) | Tests (test IDs, result, TST task ID) | Security findings (SEC-###) | Last updated (task ID) |
|---|---|---|---|---|---|---|---|
| FR-015 | Draft | arch §10.1 `#/overview`, §2 P9; plan §4 task 2.4 | - | - | - | - | T-20261030-001-PLN |
| FR-016 | Draft | arch §10.1 `#/agents`; schema §5 `agents`; plan §4 task 2.5 | - | - | - | - | T-20261030-001-PLN |
| FR-017 | Draft | arch §10.1 `#/activity`; schema §4 `activity_events`; plan §4 task 2.6 | - | - | - | - | T-20261030-001-PLN |
| FR-018 | Draft | arch §10.1, §10.2; plan §4 task 2.2 | - | - | - | - | T-20261030-001-PLN |
| FR-019 | Draft | arch §2 P9; plan §4 task 2.3 | - | - | - | - | T-20261030-001-PLN |
| FR-020 | Draft | arch §10.2 (auto-refresh) | - | - | - | - | T-20261030-001-PLN |
| FR-021 | Draft | arch §7 steps 1-2; schema §4 `projects`, `git_checkpoints`; plan §5 task 3.5 | - | - | - | - | T-20261030-001-PLN |
| FR-022 | Draft | arch §7 step 1 (refused folders), §11 Project folders, §15 item 15; plan §5 task 3.5 | - | - | - | - | T-20261030-001-PLN |
| FR-023 | Draft | arch §2 P3, §3.1, §3.2 | - | - | - | - | T-20261030-001-PLN |
| FR-024 | Draft | arch §2 P4, §3.2; schema §6 `approvals.decided_by` CHECK | - | - | - | - | T-20261030-001-PLN |
| FR-025 | Draft | arch §4.1, §11; schema §4 `activity_events`; plan §5 task 3.2 | - | - | - | - | T-20261030-001-PLN |
| FR-026 | Draft | arch §4.1 `app/integrations/git/`, §11 Git; schema §4 `0003_git_tracking.sql`; plan §5 tasks 3.3, 3.4 | - | - | - | - | T-20261030-001-PLN |
| FR-027 | Draft | arch §10.1 `#/files`; schema §4 `file_changes`; plan §5 task 3.6 | - | - | - | - | T-20261030-001-PLN |
| FR-028 | Draft | arch §10.1 `#/files/:projectId/:path`, §11 File access; plan §5 task 3.6 | - | - | - | - | T-20261030-001-PLN |
| FR-029 | Draft | arch §5.2, §5.3; schema §4 (derivation notes); plan §5 task 3.8 | - | - | - | - | T-20261030-001-PLN |
| FR-030 | Draft | arch §2 P2, §5.3 rules R-E and R-F; plan §5 task 3.8 | - | - | - | - | T-20261030-001-PLN |
| FR-031 | Draft | arch §5.3 (discrepancy flags); plan §5 task 3.7 | - | - | - | - | T-20261030-001-PLN |
| FR-032 | Draft | arch §8; schema §4 `agent_reports`, `report_items`; plan §5 task 3.7 | - | - | - | - | T-20261030-001-PLN |
| FR-033 | Draft | arch §9; schema §4 `agent_reports` (`manual_paste`); plan §5 task 3.7 | - | - | - | - | T-20261030-001-PLN |
| FR-034 | Draft | arch §2 P9; plan §5 task 3.9 | - | - | - | - | T-20261030-001-PLN |
| FR-035 | Draft | arch §4.2, §6.2, §6.3; plan §6 task 4.1 | - | - | - | - | T-20261030-001-PLN |
| FR-036 | Draft | arch §2 P5, §6.2; plan §6 task 4.1 | - | - | - | - | T-20261030-001-PLN |
| FR-037 | Draft | arch §6.1, §6.4; schema §5 `sessions`, `tasks`; plan §6 tasks 4.2, 4.7 | - | - | - | - | T-20261030-001-PLN |
| FR-038 | Draft | arch §6.5; plan §6 task 4.3 | - | - | - | - | T-20261030-001-PLN |
| FR-039 | Draft | arch §7 step 3, §3.1; DEC-017; plan §6 task 4.4 | - | - | - | - | T-20261030-001-PLN |
| FR-040 | Draft | arch §7 step 4; schema §5 `project_connections`; DEC-003, DEC-012; plan §6 task 4.4 | - | - | - | - | T-20261030-001-PLN |
| FR-041 | Draft | arch §7 step 5; plan §6 task 4.4 | - | - | - | - | T-20261030-001-PLN |
| FR-042 | Draft | arch §7 (Disconnect); plan §6 task 4.4 | - | - | - | - | T-20261030-001-PLN |
| FR-043 | Draft | arch §5.2, §5.3 rules R-B and R-F; plan §6 task 4.5 | - | - | - | - | T-20261030-001-PLN |
| FR-044 | Draft | arch §6.4; schema §5 `tasks.link_confidence`; plan §6 task 4.5 | - | - | - | - | T-20261030-001-PLN |
| FR-045 | Draft | arch §6.1, §6.3; schema §4 `agent_reports.summary` CHECK; DEC-008; plan §6 task 4.2 | - | - | - | - | T-20261030-001-PLN |
| FR-046 | Draft | arch §6.6; plan §6 task 4.8 | - | - | - | - | T-20261030-001-PLN |
| FR-047 | Draft | arch §10.1 `#/agents`, §6.5; plan §6 task 4.6 | - | - | - | - | T-20261030-001-PLN |
| FR-048 | Draft | arch §7; README; plan §6 task 4.4 | - | - | - | - | T-20261030-001-PLN |
| FR-049 | Draft | arch §10.3 Documentation; schema §6 `documents`; DEC-010; plan §7 task 5.1 | - | - | - | - | T-20261030-001-PLN |
| FR-050 | Draft | arch §10.3 Documentation; schema §6 `requirements`; plan §7 task 5.1 | - | - | - | - | T-20261030-001-PLN |
| FR-051 | Draft | arch §10.3 Testing; schema §6 `test_runs`, `test_cases`; plan §7 task 5.2 | - | - | - | - | T-20261030-001-PLN |
| FR-052 | Draft | arch §10.3 Testing; schema §6 `test_runs` (`hook_observed`); plan §7 task 5.2 | - | - | - | - | T-20261030-001-PLN |
| FR-053 | Draft | arch §10.3 Testing; schema §6 `test_runs` (`test_runner_file`); plan §7 task 5.2 | - | - | - | - | T-20261030-001-PLN |
| FR-054 | Draft | arch §10.3 Testing (test-runner file rule), §15 item 16; schema §6 `test_runs` CHECKs; plan §7 task 5.2 | - | - | - | - | T-20261030-001-PLN |
| FR-055 | Draft | arch §10.3 Testing; plan §7 task 5.2 | - | - | - | - | T-20261030-001-PLN |
| FR-056 | Draft | arch §10.3 Security; schema §6 `security_findings`; plan §7 task 5.3 | - | - | - | - | T-20261030-001-PLN |
| FR-057 | Draft | arch §10.3 Approvals; schema §6 `approvals`; DEC-009; plan §7 task 5.4 | - | - | - | - | T-20261030-001-PLN |
| FR-058 | Draft | arch §10.3 Approvals; schema §6 approvals triggers; plan §7 task 5.4 | - | - | - | - | T-20261030-001-PLN |
| FR-059 | Draft | arch §10.3 File-change reviews; schema §6 `approvals` (`file_change_review`); plan §7 task 5.4 | - | - | - | - | T-20261030-001-PLN |
| FR-060 | Draft | arch §10.3 Release readiness; plan §7 task 5.5 | - | - | - | - | T-20261030-001-PLN |
| FR-061 | Draft | arch §8 (Phase 5 rows); plan §7 tasks 5.2, 5.3 | - | - | - | - | T-20261030-001-PLN |
| FR-062 | Draft | arch §10.3 Approvals; plan §7 task 5.4 | - | - | - | - | T-20261030-001-PLN |
| NFR-013 | Draft | arch §2 P8, §6.3, §11 Data at rest; plan §5 task 3.2 | - | - | - | - | T-20261030-001-PLN |
| NFR-014 | Draft | arch §6.3 (shell command); DEC-007 | - | - | - | - | T-20261030-001-PLN |
| NFR-015 | Draft | arch §11 File access; plan §5 tasks 3.5, 3.6 | - | - | - | - | T-20261030-001-PLN |
| NFR-016 | Draft | arch §11 Sensitive files; plan §5 task 3.6 | - | - | - | - | T-20261030-001-PLN |
| NFR-017 | Draft | arch §3.2, §11 Commands | - | - | - | - | T-20261030-001-PLN |
| NFR-018 | Draft | arch §11 Git; plan §5 task 3.3 | - | - | - | - | T-20261030-001-PLN |
| NFR-019 | Draft | arch §6.2, §11; schema §1 (CHECK limits); plan §5 task 3.2 | - | - | - | - | T-20261030-001-PLN |
| NFR-020 | Draft | arch §11 Hook ingestion; plan §6 task 4.1 | - | - | - | - | T-20261030-001-PLN |
| NFR-021 | Draft | arch §12 SQLite; plan §8 item 6.4 | - | - | - | - | T-20261030-001-PLN |
| NFR-022 | Draft | arch §10.2 (pagination); plan §8 | - | - | - | - | T-20261030-001-PLN |
| NFR-023 | Draft | plan §8 (items 6.1 to 6.8) | - | - | - | - | T-20261030-001-PLN |
