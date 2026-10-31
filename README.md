# AgentDesk

AgentDesk is a small dashboard that runs on your own Windows PC. It will let you supervise the four Claude Code
agents (planner, developer, testing and security audit) that work on your software projects: what they did, which
files changed and why, which tests really ran, security findings and the decisions waiting for you.

It is a personal tool for one person on one PC. It runs only on your computer (`127.0.0.1`), needs no account, no
API key, no cloud service and no internet connection while it runs.

## Current phase and its limits

**Phase 1 (foundation), version 0.1.0.** What works now:

- the server, its security protections and the SQLite database with automatic updates (migrations);
- the dashboard shell: navigation with 11 pages, light, dark or system theme, and the server status in the header;
- the **Settings** page: versions, database status, integrity check result, the backup list and "Create backup now";
- backups (automatic and manual) and restore from the command line.

The other ten pages (Overview, Projects, Agents, Activity, File changes, Reports, Documents, Testing, Security,
Approvals) are clearly labelled placeholders that say in which phase their content arrives. AgentDesk does not
monitor any project yet: connecting projects, Claude Code hooks, Git tracking and reports come in Phases 2 to 5.

## Requirements

- Windows 11
- Python 3.12 or newer, available as `python` in the Command Prompt
  ([python.org/downloads](https://www.python.org/downloads/); tick "Add python.exe to PATH" when installing)
- Git (to get and update this repository)
- A current desktop browser, for example Edge or Chrome

## Setup (once)

Open a Command Prompt and run:

```bat
cd /d D:\agentdesk
scripts\setup.bat
```

This creates a private Python environment in the `.venv` folder inside the repository and installs the exact
package versions listed in `requirements.lock.txt`. It changes nothing outside the repository: pip's download
cache is turned off and temporary files go to `.sandbox\tmp`. Running it again is safe.

To also install the test tools (pytest and httpx), run `scripts\setup.bat dev` instead.

## Start and stop

```bat
cd /d D:\agentdesk
scripts\start.bat
```

The window shows the address and your browser opens http://127.0.0.1:8765. To stop AgentDesk, press **Ctrl+C**
in the Command Prompt window (answer `Y` if asked "Terminate batch job").

To start without opening the browser: `.venv\Scripts\python -m app`.

### Settings you can change (optional)

Set these in the Command Prompt before `scripts\start.bat`, for example `set AGENTDESK_PORT=8766`:

| Variable | Default | Allowed values |
|---|---|---|
| `AGENTDESK_HOST` | `127.0.0.1` | `127.0.0.1`, `localhost` or `::1` only. Anything else is refused. |
| `AGENTDESK_PORT` | `8765` | 1024 to 65535 |
| `AGENTDESK_DATA_DIR` | the `data` folder in the repository | any folder |
| `AGENTDESK_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

If AgentDesk cannot start, the message says why and what to do (for example "port 8765 is already in use").

## Where your data is stored

Everything AgentDesk stores is in the `data` folder of the repository. Git ignores this folder, so it is never
committed.

| Path | Contents |
|---|---|
| `data\agentdesk.db` | the database |
| `data\backups\` | backups (`agentdesk-YYYYMMDD-HHMMSS-<reason>.db`, time in UTC) and databases kept by a restore (`pre-restore-*.db`) |
| `data\logs\agentdesk.log` | the log file (renewed at 1 MB, the last 5 are kept); it never contains request contents or security tokens |

## Backup and restore

AgentDesk makes backups by itself:

- when it starts and the newest backup is more than 24 hours old (`startup`);
- before it updates the database structure (`pre-migration`).

You can also make one at any time: on the **Settings** page click **Create backup now**, or run:

```bat
.venv\Scripts\python scripts\backup_db.py create
.venv\Scripts\python scripts\backup_db.py list
```

Every backup is checked with SQLite's integrity check. The newest 10 backups are kept; older ones are deleted
automatically. Other files in `data\backups` (such as `pre-restore-*.db`) are never deleted.

**To restore a backup:**

1. Stop AgentDesk (Ctrl+C in its window). Restore refuses to run while AgentDesk is running.
2. See the backups: `.venv\Scripts\python scripts\restore_db.py list`
3. Restore one by its file name, for example:
   `.venv\Scripts\python scripts\restore_db.py restore agentdesk-20261030-120000-manual.db`
4. Type `RESTORE` when asked. Anything else cancels without changing anything.
5. Start AgentDesk again with `scripts\start.bat`.

The database you replaced is not lost: it is kept as `data\backups\pre-restore-<time>.db`, and you can restore it
the same way.

If AgentDesk ever says the database **failed its integrity check**, it refuses to start and leaves the damaged file
untouched. Restore the newest backup with the steps above.

## Running the tests

After `scripts\setup.bat dev`:

```bat
.venv\Scripts\python -m pytest -v
```

Test files are written only to `.pytest_tmp\` inside the repository (ignored by Git).

## Security notes

- AgentDesk listens only on your own computer (`127.0.0.1`). Do not expose it to a network: do not change it to
  listen on other addresses, and do not forward its port or put it behind a proxy.
- It refuses requests that use a different host name (protection against DNS rebinding attacks).
- Every action that changes something (for example creating a backup) needs a security token that only the
  AgentDesk page can read, so other websites you visit cannot trigger actions.
- Pages are sent with strict browser security headers (Content-Security-Policy and others).
- Error messages never include program internals; details go to `data\logs\agentdesk.log`.

## Folder layout

| Path | Purpose |
|---|---|
| `app\` | the AgentDesk server (Python, FastAPI) |
| `app\core\` | settings, logging, security protections, time helpers |
| `app\database\` | database connection, migrations, backup and restore |
| `app\api\`, `app\models\` | the web API under `/api/v1` and its response formats |
| `app\static\` | the dashboard: `index.html`, `css\app.css`, `js\` modules (no build step) |
| `migrations\` | numbered SQL files that create and update the database structure |
| `scripts\` | `setup.bat`, `start.bat`, `backup_db.py`, `restore_db.py` |
| `tests\` | automated tests (pytest) |
| `docs\` | requirements, architecture, plans, decisions and agent activity records |
| `requirements.txt`, `requirements.lock.txt`, `requirements-dev.txt` | package versions (see below) |

`requirements.txt` names the two packages AgentDesk uses (FastAPI and Uvicorn) with fixed versions.
`requirements.lock.txt` lists every package version exactly as installed (made with `pip freeze`; do not edit it by
hand). `requirements-dev.txt` adds the test tools.
