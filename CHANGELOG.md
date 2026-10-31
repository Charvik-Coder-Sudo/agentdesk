# Changelog

All notable changes to this project are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Each entry cites its task ID, for example `(T-20261030-001-DEV)`.

## [Unreleased]

### Added

- Architecture, database schema and implementation plan documents, version 0.2, proposed for approval (T-20261030-001-ORC).
- Change-tracking structure for agent activity, test and security records (T-20261030-001-ORC).
- Draft SRS (version 0.1) with stable requirement IDs, a traceability matrix and the Phase 1 task list; design documents revised to version 0.3, Draft (T-20261030-001-PLN).
- Phase 1 foundation, version 0.1.0: local FastAPI server started with `scripts\start.bat` (or `python -m app [--open]`) on http://127.0.0.1:8765 (T-20261030-002-DEV).
- SQLite database `data/agentdesk.db` with numbered, checksummed migrations (`0001_foundation`) and an integrity check at every start (T-20261030-002-DEV).
- Automatic backups at startup (when the newest is over 24 hours old) and before migrations; "Create backup now" on the Settings page; `scripts\backup_db.py` and `scripts\restore_db.py`; the newest 10 backups are kept (T-20261030-002-DEV).
- Dashboard shell: 11-entry navigation, light/dark/system theme, server status in the header, Settings page with system and database status; the other ten pages are labelled placeholders naming their future phase (T-20261030-002-DEV).
- `scripts\setup.bat` (with `dev` for the test tools), dependency files `requirements.txt`, `requirements.lock.txt`, `requirements-dev.txt`, initial automated tests and README instructions (T-20261030-002-DEV).

### Changed

### Fixed

### Security

- Loopback-only binding, Host header allowlist, CSRF token plus Origin and JSON checks for state-changing requests, Content-Security-Policy and other security headers, JSON errors without stack traces, logs without request bodies or tokens (T-20261030-002-DEV).

### Removed
