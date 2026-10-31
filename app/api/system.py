"""System endpoints: health, system information, CSRF session token and backups."""

import platform
import sqlite3
import time

from fastapi import APIRouter, Depends, Request

from app import __version__
from app.api.errors import ApiError
from app.core.timeutil import to_iso
from app.database.backup import BackupError, BackupInfo, create_backup, list_backups
from app.database.connection import get_db
from app.models.system import (
    BackupCreatedResponse,
    BackupItem,
    BackupListResponse,
    HealthResponse,
    IntegrityItem,
    MigrationItem,
    SessionResponse,
    SystemResponse,
)

router = APIRouter(prefix="/api/v1")


def _backup_item(info: BackupInfo) -> BackupItem:
    return BackupItem(
        name=info.name,
        reason=info.reason,
        created_at=to_iso(info.created_at),
        size_bytes=info.size_bytes,
    )


# HEAD is answered too (status and headers only), for monitoring tools that use it.
@router.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse)
def health(request: Request):
    uptime = time.monotonic() - request.app.state.started_at
    return HealthResponse(status="ok", version=__version__, uptime=round(max(uptime, 0.0), 1))


@router.get("/session", response_model=SessionResponse)
def session(request: Request):
    """The CSRF token the page must send with every state-changing request."""
    return SessionResponse(csrf_token=request.app.state.csrf_token)


@router.get("/system", response_model=SystemResponse)
def system_info(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    settings = request.app.state.settings
    migrations = conn.execute(
        "SELECT version, name, applied_at FROM schema_migrations ORDER BY version"
    ).fetchall()
    stored = dict(
        conn.execute("SELECT key, value FROM app_settings WHERE key IN ('instance_id', 'created_at')").fetchall()
    )
    backups = list_backups(settings.backups_dir)
    return SystemResponse(
        version=__version__,
        python_version=platform.python_version(),
        sqlite_version=sqlite3.sqlite_version,
        data_dir=str(settings.data_dir),
        database_path=str(settings.db_path),
        database_size_bytes=settings.db_path.stat().st_size,
        schema_version=max((row["version"] for row in migrations), default=0),
        migrations=[MigrationItem(**dict(row)) for row in migrations],
        last_backup=_backup_item(backups[0]) if backups else None,
        integrity=IntegrityItem(**request.app.state.integrity),
        instance_id=stored.get("instance_id"),
        created_at=stored.get("created_at"),
        backup_warning=request.app.state.backup_warning,
    )


@router.get("/system/backups", response_model=BackupListResponse)
def backups(request: Request):
    settings = request.app.state.settings
    return BackupListResponse(backups=[_backup_item(info) for info in list_backups(settings.backups_dir)])


@router.post("/system/backups", response_model=BackupCreatedResponse, status_code=201)
def create_manual_backup(request: Request):
    """Create a manual backup. CSRF-protected by the security middleware."""
    try:
        info = create_backup(request.app.state.settings, "manual")
    except BackupError as exc:
        # A fixed message per kind of failure, never exception text or paths; details are in the log.
        raise ApiError(500, "backup_failed", f"The backup failed. {exc.public_message}")
    return BackupCreatedResponse(
        backup=_backup_item(info),
        integrity="ok",
        message=f"Backup created: {info.name}",
    )
