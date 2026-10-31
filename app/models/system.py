"""Response models for the system endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float  # seconds since the server started


class SessionResponse(BaseModel):
    csrf_token: str


class MigrationItem(BaseModel):
    version: int
    name: str
    applied_at: str


class BackupItem(BaseModel):
    name: str
    reason: str
    created_at: str  # ISO 8601 UTC
    size_bytes: int


class IntegrityItem(BaseModel):
    result: str  # "ok" or the problem found
    check: str  # which SQLite check was run
    checked_at: str


class SystemResponse(BaseModel):
    version: str
    python_version: str
    sqlite_version: str
    data_dir: str
    database_path: str
    database_size_bytes: int
    schema_version: int
    migrations: list[MigrationItem]
    last_backup: BackupItem | None
    integrity: IntegrityItem
    instance_id: str | None
    created_at: str | None
    backup_warning: str | None  # set when the automatic startup backup failed


class BackupListResponse(BaseModel):
    backups: list[BackupItem]


class BackupCreatedResponse(BaseModel):
    backup: BackupItem
    integrity: str
    message: str
