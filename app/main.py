"""Application factory and startup sequence.

create_app() runs the startup steps before the server accepts requests:
  1. create the data folders (a new data folder is owner-only); log the data folder in use and warn
     if other Windows accounts can change the AgentDesk folder or the data folder;
  2. if the database exists, run PRAGMA quick_check read-only; on failure stop without touching it;
  3. take at most one automatic backup: "pre-migration" if migrations are pending on an existing
     database, otherwise "startup" if the newest backup is missing or older than 24 hours;
  4. apply pending migrations;
  5. make sure app_settings holds instance_id and created_at;
  6. create a new CSRF token for this server run.
"""

import logging
import mimetypes
import os
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.errors import register_error_handlers
from app.api.system import router as system_router
from app.core.config import REPO_ROOT, Settings, load_settings
from app.core.folder_access import check_shared_folders, create_private_folder
from app.core.security import SecurityMiddleware, new_csrf_token
from app.core.timeutil import utc_now, utc_now_iso
from app.database.backup import BackupError, create_backup, list_backups
from app.database.connection import connect, connect_readonly, transaction
from app.database.migrations import (
    MIGRATIONS_DIR,
    MigrationError,
    apply_migrations,
    discover_migrations,
    pending_migrations,
    read_applied,
)

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STARTUP_BACKUP_MAX_AGE = timedelta(hours=24)
# A backup dated further ahead than this is ignored by the 24-hour rule, so a wrong clock
# can delay automatic startup backups by a day at most, never stop them.
STARTUP_BACKUP_FUTURE_LIMIT = timedelta(hours=24)

# Windows can map file types oddly in its registry; set the ones AgentDesk serves explicitly.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


class StartupError(Exception):
    """AgentDesk must not start. The message explains why and what to do."""


@dataclass
class StartupResult:
    integrity: dict  # result, check, checked_at
    backup_name: str | None
    backup_warning: str | None


def _restore_instructions() -> str:
    return (
        "To restore a backup, run in the AgentDesk folder:\n"
        "  .venv\\Scripts\\python scripts\\restore_db.py list\n"
        "  .venv\\Scripts\\python scripts\\restore_db.py restore <file name>\n"
        "The damaged file is kept as data\\backups\\pre-restore-<time>.db."
    )


def _data_folder_error(folder: Path, exc: OSError) -> StartupError:
    """A plain message for a data folder that cannot be created or used."""
    blocker = folder
    while not blocker.exists() and blocker.parent != blocker:
        blocker = blocker.parent
    if blocker.exists() and not blocker.is_dir():
        reason = f"{blocker} is a file, not a folder"
    else:
        reason = exc.strerror or str(exc)
    return StartupError(
        f"AgentDesk cannot use the folder {folder}: {reason}.\n"
        "The data folder must be a folder that you can write to. It is set by AGENTDESK_DATA_DIR "
        "(default: the data folder inside AgentDesk). Move the file that is in the way, choose another "
        "folder with set AGENTDESK_DATA_DIR=<folder>, or remove the AGENTDESK_DATA_DIR setting to use the default."
    )


def create_data_folders(settings: Settings) -> None:
    """Create the data, backups and logs folders. A new data folder is created owner-only (TASK-096).
    Raises StartupError with a plain message if a folder cannot be created (D-2)."""
    folder = settings.data_dir
    try:
        create_private_folder(folder)
        for folder in (settings.backups_dir, settings.logs_dir):
            folder.mkdir(exist_ok=True)
    except OSError as exc:
        raise _data_folder_error(folder, exc) from exc


def _same_folder(first: Path, second: Path) -> bool:
    return os.path.normcase(str(Path(first).resolve())) == os.path.normcase(str(Path(second).resolve()))


def log_data_folder(settings: Settings) -> None:
    """Log the data folder in use; warn if Git's data/ ignore rule does not cover it (SEC-013)."""
    logger.info("Data folder: %s", settings.data_dir)
    if not _same_folder(settings.data_dir, REPO_ROOT / "data"):
        logger.warning(
            "The data folder %s is not the default data folder inside AgentDesk (it is set by AGENTDESK_DATA_DIR). "
            "Git's data/ ignore rule does not cover it: inside the AgentDesk folder only the file patterns in "
            ".gitignore (such as *.db and *.log) keep its files out of Git. Never add this folder to a Git repository.",
            settings.data_dir,
        )


def _quick_check(conn: sqlite3.Connection) -> str:
    rows = conn.execute("PRAGMA quick_check").fetchall()
    messages = [row[0] for row in rows]
    return "ok" if messages == ["ok"] else "; ".join(messages[:5])


def _check_existing_database(db_path: Path) -> tuple[dict, dict]:
    """Integrity check and applied migrations, read-only, so a damaged file stays unchanged."""
    if not db_path.is_file():
        raise StartupError(f"{db_path} exists but is not a file. Move it away, then start AgentDesk again.")
    try:
        conn = connect_readonly(db_path)
        try:
            result = _quick_check(conn)
            applied = read_applied(conn) if result == "ok" else {}
        finally:
            conn.close()
    except sqlite3.Error as exc:
        result = f"cannot be read as a database: {exc}"
        applied = {}
    if result != "ok":
        logger.error("Database integrity check failed for %s: %s", db_path, result)
        raise StartupError(
            f"The database {db_path} failed its integrity check ({result}).\n"
            "AgentDesk did not start and did not change the file.\n" + _restore_instructions()
        )
    integrity = {"result": "ok", "check": "quick_check", "checked_at": utc_now_iso()}
    return integrity, applied


def _startup_backup_due(settings: Settings) -> bool:
    """True if no backup is younger than 24 hours. Backups dated more than a day ahead are ignored."""
    now = utc_now()
    latest_allowed = now + STARTUP_BACKUP_FUTURE_LIMIT
    times = [b.created_at for b in list_backups(settings.backups_dir) if b.created_at <= latest_allowed]
    return not times or now - max(times) > STARTUP_BACKUP_MAX_AGE


def _ensure_instance_settings(conn: sqlite3.Connection) -> None:
    now = utc_now_iso()
    with transaction(conn):
        for key, value in (("instance_id", uuid.uuid4().hex), ("created_at", now)):
            conn.execute(
                "INSERT OR IGNORE INTO app_settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, now),
            )


def _database_error(settings: Settings) -> StartupError:
    logger.exception("Unexpected database error during startup")
    return StartupError(
        f"AgentDesk could not prepare the database {settings.db_path} because of an unexpected database error, "
        f"so it did not start. Details are in the log file {settings.logs_dir / 'agentdesk.log'}.\n"
        + _restore_instructions()
    )


def run_startup(settings: Settings, migrations_dir: Path = MIGRATIONS_DIR) -> StartupResult:
    """Steps 1 to 5 of the startup sequence (see the module docstring)."""
    create_data_folders(settings)
    log_data_folder(settings)
    check_shared_folders([("AgentDesk folder", REPO_ROOT), ("data folder", settings.data_dir)])

    db_path = settings.db_path
    db_existed = db_path.exists()
    integrity, applied = _check_existing_database(db_path) if db_existed else (None, {})

    try:
        pending = pending_migrations(applied, discover_migrations(migrations_dir))
    except MigrationError as exc:
        raise StartupError(str(exc)) from exc

    backup_name = None
    backup_warning = None
    if db_existed and pending:
        try:
            backup_name = create_backup(settings, "pre-migration").name
        except BackupError as exc:
            raise StartupError(
                f"AgentDesk could not back up the database before updating it, so it did not start: {exc}"
            ) from exc
    elif db_existed and _startup_backup_due(settings):
        try:
            backup_name = create_backup(settings, "startup").name
        except BackupError as exc:
            logger.error("The automatic startup backup failed: %s", exc)
            # Shown on the Settings page: the fixed public text, never exception details (SEC-012).
            backup_warning = f"The automatic startup backup failed: {exc.public_message}"

    try:
        conn = connect(db_path)
    except sqlite3.Error as exc:
        raise _database_error(settings) from exc
    try:
        apply_migrations(conn, pending)
        _ensure_instance_settings(conn)
        if integrity is None:  # a new database: check it once it exists
            integrity = {"result": _quick_check(conn), "check": "quick_check", "checked_at": utc_now_iso()}
    except MigrationError as exc:
        raise StartupError(str(exc)) from exc
    except sqlite3.Error as exc:
        raise _database_error(settings) from exc
    finally:
        conn.close()

    logger.info(
        "Database ready: %s (%s, integrity %s%s)",
        db_path,
        "existing" if db_existed else "new",
        integrity["result"],
        f", backup {backup_name}" if backup_name else "",
    )
    return StartupResult(integrity=integrity, backup_name=backup_name, backup_warning=backup_warning)


def create_app(settings: Settings | None = None, migrations_dir: Path = MIGRATIONS_DIR) -> FastAPI:
    """Build the AgentDesk application. Raises StartupError if it must not start."""
    settings = settings or load_settings()
    startup = run_startup(settings, migrations_dir)
    csrf_token = new_csrf_token()

    # No interactive API docs: they would load scripts from the internet, which the CSP forbids.
    # Telemetry auto-configuration is switched off in code, so environment variables such as
    # FASTAPI_OTEL_AUTO_CONFIGURE cannot turn it on (CON-002, SEC-011).
    app = FastAPI(
        title="AgentDesk", version=__version__, docs_url=None, redoc_url=None, openapi_url=None,
        telemetry={"auto_configure": False},
    )
    app.state.settings = settings
    app.state.csrf_token = csrf_token
    app.state.started_at = time.monotonic()
    app.state.integrity = startup.integrity
    app.state.backup_warning = startup.backup_warning

    register_error_handlers(app)
    app.include_router(system_router)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.add_middleware(SecurityMiddleware, port=settings.port, csrf_token=csrf_token)
    return app
