# Security findings register

Maintained by security-audit-agent. One row per finding; IDs are stable, never renumber or delete rows.

Status: Open | In remediation | Fixed - pending verification | Verified | Risk accepted | False positive

- A developer's fix moves a finding at most to Fixed - pending verification.
- Verified requires an independent re-check (a task other than the one that made the fix) with recorded evidence.
- Risk accepted requires a user decision recorded in `docs/decisions/` (cite the DEC ID).
- False positive requires a written justification.

For AgentDesk the security agent is strictly read-only (DEC-016), so the orchestrator records its rows here from the agent's returned reports.

| ID | Title | Severity | Location | Found in | Status | Fixed in | Verified by | Verification evidence | Last updated |
|---|---|---|---|---|---|---|---|---|---|
| SEC-001 | Log forging and flooding through the decoded request path in refusal and error log lines | Medium | app/core/security.py:92, :109 | T-20261030-002-SEC | In remediation (TASK-094) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-002 | Restore can run while a server is running; a request during the swap can create an empty database | Low | scripts/restore_db.py:64-88; app/database/backup.py:183-224; app/database/connection.py:18 | T-20261030-002-SEC | In remediation (TASK-093) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-003 | Restore leaves stale -wal/-shm/-journal beside the restored database when no current database exists | Low | app/database/backup.py:208-218 | T-20261030-002-SEC | In remediation (TASK-093) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-004 | Backup naming and retention trust file-name timestamps and can prune the new backup (includes TST D-1) | Low | app/database/backup.py:72-156; app/main.py:104-106 | T-20261030-002-SEC | In remediation (TASK-093) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-005 | Project and data folders inherit write access for all authenticated local users | Low | D:\agentdesk and data\ ACLs; app/main.py:121-122 | T-20261030-002-SEC | In remediation (TASK-096 (token part: TASK-038, NFR-024)) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-006 | Non-HTTP (WebSocket) scopes bypass the Host and Origin checks | Info | app/core/security.py:69-71 | T-20261030-002-SEC | In remediation (TASK-094) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-007 | Additional browser isolation headers absent (COOP, CORP, Permissions-Policy) | Info | app/core/security.py:18-24 | T-20261030-002-SEC | In remediation (TASK-094) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-008 | CSRF method coverage is a denylist | Info | app/core/security.py:25, :88 | T-20261030-002-SEC | In remediation (TASK-094) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-009 | DOM builder attribute guard is a denylist | Info | app/static/js/dom.js:6-20 | T-20261030-002-SEC | In remediation (TASK-097) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-010 | Supply chain: pins without hashes, dev sub-dependencies unpinned, no local scanner | Info | requirements.lock.txt; requirements-dev.txt; scripts/setup.bat | T-20261030-002-SEC | Open (Info; accepted with justification DEC-018/DEC-025, owner to confirm at TASK-092) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-011 | FastAPI built-in telemetry can be switched on by environment variables | Info | app/main.py:177 | T-20261030-002-SEC | In remediation (TASK-094) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-012 | Handled backup errors echo exception text to the API and page | Info | app/api/system.py:88; app/database/backup.py | T-20261030-002-SEC | In remediation (TASK-093) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-013 | CON-009 / NFR-011 residuals: data-folder override, .gitignore gaps, SQLite temp files | Info | app/core/config.py:72-73; .gitignore; app/database/connection.py | T-20261030-002-SEC | In remediation (TASK-095) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-014 | setup.bat looks for Python in the current folder first and does not show the interpreter used | Info | scripts/setup.bat:11, :28 | T-20261030-002-SEC | In remediation (TASK-098) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
| SEC-015 | `$` regex anchors accept a trailing newline | Info | app/database/backup.py:25, :27; app/database/migrations.py:23 | T-20261030-002-SEC | In remediation (TASK-093) | - | - | - | T-20261030-002-PLN (recorded by orchestrator) |
