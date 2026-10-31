"""Database backups (SQLite online backup API) and offline restore.

Backups are written to data/backups/agentdesk-YYYYMMDD-HHMMSS-<reason>.db (time in UTC). Several
backups within one second get -2, -3, ... after the reason. Every copy is integrity-checked. Only the
newest 10 AgentDesk backups are kept, and never the one just made; any other file in data/backups
(for example pre-restore-*.db or failed-*.db) is never touched.
"""

import logging
import os
import re
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import Settings
from app.core.folder_access import create_private_folder
from app.core.timeutil import utc_now
from app.database.connection import connect_readonly, database_uri

logger = logging.getLogger(__name__)

REASONS = ("manual", "startup", "pre-migration")
KEEP_BACKUPS = 10
# \Z (not $) so that a name ending in a newline never matches (SEC-015).
BACKUP_PATTERN = re.compile(r"^agentdesk-(\d{8}-\d{6})-(manual|startup|pre-migration)(?:-(\d+))?\.db\Z")
# Every file name that uses up a backup sequence number for its second, including failed and unfinished copies.
_USED_NAME = re.compile(
    r"^(?:failed-)?agentdesk-(\d{8}-\d{6})-(?:manual|startup|pre-migration)(?:-(\d+))?\.db(?:\.partial)?\Z"
)
# A restore accepts only a plain file name: letters, digits, dot, dash and underscore.
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.db\Z")
# A backup name dated more than this after the current time is "future-dated" (the PC clock was wrong).
FUTURE_TOLERANCE = timedelta(minutes=5)
SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")

# Messages for the API and the Settings page: fixed text, never exception details or paths (SEC-012).
WRITE_FAILED = (
    "The backup could not be written. Check that the disk has free space and that the data folder can be "
    "written to, then try again. Details are in the log file."
)
INTEGRITY_FAILED = (
    "The backup copy failed its integrity check, so it was kept as a failed-* file for inspection and is "
    "not counted as a backup. Details are in the log file."
)

_lock = threading.Lock()  # one backup at a time inside this process
_reported_future: set[str] = set()  # future-dated names already logged in this run


class BackupError(Exception):
    """A backup or restore could not be done.

    str(error) is the full message for the console and the log; it may name files.
    public_message is what the API and the Settings page show. It defaults to the full message, so
    code that raises with exception text or paths in the message must pass a fixed public_message.
    """

    def __init__(self, message: str, public_message: str | None = None):
        super().__init__(message)
        self.public_message = public_message or message


@dataclass(frozen=True)
class BackupInfo:
    name: str
    path: Path
    reason: str
    created_at: datetime  # UTC, from the file name
    size_bytes: int
    sequence: int = 1  # 2, 3, ... when several backups were made within the same second
    future_dated: bool = False  # dated more than 5 minutes after the current time
    modified_ns: int = 0  # file modification time, the last tie-breaker when sorting


def parse_backup_name(path: Path, now: datetime | None = None) -> BackupInfo | None:
    """Return details for an AgentDesk backup file name, or None for any other file."""
    match = BACKUP_PATTERN.fullmatch(path.name)
    if not match:
        return None
    created_at = datetime.strptime(match.group(1), "%Y%m%d-%H%M%S").replace(tzinfo=timezone.utc)
    now = now or utc_now()
    stat = path.stat()
    return BackupInfo(
        name=path.name,
        path=path,
        reason=match.group(2),
        created_at=created_at,
        size_bytes=stat.st_size,
        sequence=int(match.group(3) or 1),
        future_dated=created_at > now + FUTURE_TOLERANCE,
        modified_ns=stat.st_mtime_ns,
    )


def list_backups(backups_dir: Path) -> list[BackupInfo]:
    """AgentDesk backups in the folder, newest first. Future-dated backups count as the oldest."""
    if not backups_dir.is_dir():
        return []
    now = utc_now()
    backups = []
    for path in backups_dir.iterdir():
        try:
            info = parse_backup_name(path, now) if path.is_file() else None
        except FileNotFoundError:  # deleted meanwhile, for example by another process's pruning
            continue
        if info:
            backups.append(info)
            if info.future_dated and info.name not in _reported_future:
                _reported_future.add(info.name)
                logger.warning(
                    "The backup %s is dated in the future (the PC clock may have been wrong). "
                    "It is treated as the oldest backup and does not count as a recent backup.",
                    info.name,
                )
    backups.sort(key=lambda b: (not b.future_dated, b.created_at, b.sequence, b.modified_ns), reverse=True)
    return backups


def integrity_check(path: Path) -> str:
    """Run PRAGMA integrity_check on a database file without changing it. Returns 'ok' or the problem."""
    try:
        conn = connect_readonly(path)
        try:
            rows = conn.execute("PRAGMA integrity_check").fetchall()
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return f"cannot be read as a database: {exc}"
    messages = [row[0] for row in rows]
    return "ok" if messages == ["ok"] else "; ".join(messages[:5])


def _name_taken(path: Path) -> bool:
    """True if the name, or an unfinished copy or database side file of it, already exists."""
    return any(
        path.with_name(path.name + suffix).exists() for suffix in ("", ".partial", *SIDECAR_SUFFIXES)
    )


def _unique_path(directory: Path, stem: str) -> Path:
    """directory/stem.db, or stem-2.db, stem-3.db ... if that name is taken."""
    candidate = directory / f"{stem}.db"
    number = 2
    while _name_taken(candidate):
        candidate = directory / f"{stem}-{number}.db"
        number += 1
    return candidate


def _backup_name(stamp: str, reason: str, sequence: int) -> str:
    suffix = "" if sequence == 1 else f"-{sequence}"
    return f"agentdesk-{stamp}-{reason}{suffix}.db"


def _reserve_backup_path(directory: Path, stamp: str, reason: str) -> tuple[Path, Path]:
    """Choose the name for a new backup and create its .partial file exclusively.

    The sequence number is the next one after the highest already used in that second (by any
    backup, unfinished copy or failed copy), so a new backup never reuses a freed name and always
    sorts as the newest. The .partial file is created with exclusive access: if another process
    created it first, the next number is tried, so two processes never write the same file.
    """
    highest = 0
    for path in directory.iterdir():
        match = _USED_NAME.fullmatch(path.name)
        if match and match.group(1) == stamp:
            highest = max(highest, int(match.group(2) or 1))
    sequence = highest + 1
    while True:
        final_path = directory / _backup_name(stamp, reason, sequence)
        partial_path = final_path.with_name(final_path.name + ".partial")
        if not final_path.exists() and not final_path.with_name("failed-" + final_path.name).exists():
            try:
                with open(partial_path, "xb"):
                    pass
                return final_path, partial_path
            except FileExistsError:
                pass
        sequence += 1


def _copy_database(source: sqlite3.Connection, target_path: Path) -> None:
    """Copy a database with the online backup API into one self-contained file."""
    target = sqlite3.connect(target_path)
    try:
        source.backup(target)
        target.execute("PRAGMA journal_mode=DELETE")  # no -wal/-shm files next to the copy
    finally:
        target.close()


def create_backup(settings: Settings, reason: str) -> BackupInfo:
    """Back up the database, check the copy and apply the retention rule."""
    if reason not in REASONS:
        raise ValueError(f"unknown backup reason {reason!r}")
    if not settings.db_path.is_file():
        raise BackupError("There is no database to back up yet. Start AgentDesk once first.")

    with _lock:
        partial_path = None
        try:
            settings.backups_dir.mkdir(parents=True, exist_ok=True)
            stamp = utc_now().strftime("%Y%m%d-%H%M%S")
            final_path, partial_path = _reserve_backup_path(settings.backups_dir, stamp, reason)
            # mode=rw: the database must exist; a missing file is an error, never a new empty database.
            source = sqlite3.connect(database_uri(settings.db_path, "rw"), uri=True, timeout=5)
            try:
                _copy_database(source, partial_path)
            finally:
                source.close()
        except (sqlite3.Error, OSError) as exc:
            if partial_path is not None:
                partial_path.unlink(missing_ok=True)
            logger.error("Backup (%s) failed: %s", reason, exc)
            raise BackupError(f"The backup could not be written: {exc}", WRITE_FAILED) from exc

        result = integrity_check(partial_path)
        if result != "ok":
            failed_path = final_path.with_name("failed-" + final_path.name)
            os.replace(partial_path, failed_path)
            logger.error("Backup %s failed its integrity check: %s", final_path.name, result)
            raise BackupError(
                f"The backup copy failed its integrity check ({result}). It was kept as "
                f"{failed_path.name} for inspection and is not counted as a backup.",
                INTEGRITY_FAILED,
            )

        try:
            os.replace(partial_path, final_path)
            info = parse_backup_name(final_path)
        except OSError as exc:
            partial_path.unlink(missing_ok=True)
            logger.error("Backup %s could not be completed: %s", final_path.name, exc)
            raise BackupError(f"The backup could not be completed: {exc}", WRITE_FAILED) from exc
        logger.info("Created backup %s (integrity check: ok)", final_path.name)
        try:
            prune_backups(settings.backups_dir, protect=final_path)
        except OSError as exc:  # the new backup is good; old ones are removed next time
            logger.warning("Could not remove old backups this time (%s).", exc)
    return info


def prune_backups(backups_dir: Path, keep: int = KEEP_BACKUPS, protect: Path | None = None) -> list[str]:
    """Delete AgentDesk backups beyond the newest `keep`. Other files are never touched.

    `protect` (the backup just made) is never deleted. A backup that cannot be deleted, for example
    because another program has it open, is logged and left in place: it never turns a good new
    backup into a failure.
    """
    removed = []
    for info in list_backups(backups_dir)[keep:]:
        if protect is not None and info.path == protect:
            continue
        try:
            info.path.unlink()
        except FileNotFoundError:
            continue
        except OSError as exc:
            logger.warning("Could not remove the old backup %s (%s); it was left in place.", info.name, exc)
            continue
        removed.append(info.name)
        logger.info("Removed old backup %s (keeping the newest %d)", info.name, keep)
    return removed


def resolve_backup_name(backups_dir: Path, name: str) -> Path:
    """Accept only the plain name of an existing .db file directly inside the backups folder."""
    if not isinstance(name, str) or not SAFE_NAME.fullmatch(name) or ".." in name:
        raise BackupError(
            "Give only the file name of a backup in data\\backups (no folders), "
            "for example agentdesk-20261030-120000-manual.db."
        )
    try:
        resolved = (backups_dir / name).resolve(strict=True)
    except (FileNotFoundError, OSError):
        raise BackupError(f"There is no backup named {name} in data\\backups. Use 'list' to see the backups.")
    if resolved.parent != backups_dir.resolve() or not resolved.is_file():
        raise BackupError(f"{name} is not a backup file inside data\\backups.")
    return resolved


def list_restorable(backups_dir: Path) -> list[Path]:
    """Every .db file in the backups folder that restore accepts, newest first."""
    if not backups_dir.is_dir():
        return []
    files = [p for p in backups_dir.iterdir() if p.is_file() and SAFE_NAME.fullmatch(p.name)]
    return sorted(files, key=lambda p: p.stat().st_mtime_ns, reverse=True)


def restore_backup(settings: Settings, name: str) -> Path | None:
    """Replace the database with a backup. Only while AgentDesk is stopped (scripts/restore_db.py
    holds the data folder's lock while it calls this).

    The current database is moved to data/backups/pre-restore-<time>.db first. Its -wal, -shm and
    -journal files are always moved with it, also when there is no database file, so that SQLite can
    never replay them into the restored copy. Returns the kept database's path, or None if there was
    no database.
    """
    candidate = resolve_backup_name(settings.backups_dir, name)
    result = integrity_check(candidate)
    if result != "ok":
        raise BackupError(f"{name} failed its integrity check ({result}), so it was not restored.")

    db_path = settings.db_path
    create_private_folder(settings.data_dir)
    restoring_path = db_path.with_name(db_path.name + ".restoring")
    restoring_path.unlink(missing_ok=True)
    try:
        source = connect_readonly(candidate)
        try:
            _copy_database(source, restoring_path)
        finally:
            source.close()
    except (sqlite3.Error, OSError) as exc:
        restoring_path.unlink(missing_ok=True)
        raise BackupError(f"{name} could not be copied: {exc}") from exc

    kept_path = None
    try:
        side_files = [db_path.with_name(db_path.name + s) for s in SIDECAR_SUFFIXES]
        if db_path.exists() or any(side.exists() for side in side_files):
            stamp = utc_now().strftime("%Y%m%d-%H%M%S")
            kept_base = _unique_path(settings.backups_dir, f"pre-restore-{stamp}")
            if db_path.exists():
                os.replace(db_path, kept_base)
                kept_path = kept_base
            for suffix, side_file in zip(SIDECAR_SUFFIXES, side_files):
                if side_file.exists():
                    os.replace(side_file, kept_base.with_name(kept_base.name + suffix))
                    if kept_path is None:
                        logger.warning(
                            "Moved the leftover file %s (there was no database file) to %s.",
                            side_file.name, kept_base.name + suffix,
                        )
        os.replace(restoring_path, db_path)
    except OSError as exc:
        raise BackupError(
            f"The database could not be replaced ({exc}). Make sure AgentDesk is stopped and try again."
        ) from exc

    result = integrity_check(db_path)
    if result != "ok":
        raise BackupError(
            f"The restored database failed its integrity check ({result}). Restore another backup"
            + (f"; the previous database is kept as {kept_path.name}." if kept_path else ".")
        )
    logger.info("Restored %s; previous database kept as %s", name, kept_path.name if kept_path else "(none)")
    return kept_path
