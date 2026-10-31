r"""List backups or restore one, replacing the AgentDesk database.

Usage (in the AgentDesk folder, with AgentDesk stopped):
    .venv\Scripts\python scripts\restore_db.py list
    .venv\Scripts\python scripts\restore_db.py restore <file name>

Restore refuses to run while AgentDesk is running (on any port: the running server holds the data
folder's lock), asks you to type RESTORE, accepts only a file name from data\backups, checks the
backup's integrity before and after, and keeps the current database (with its -wal, -shm and
-journal files) as data\backups\pre-restore-<time>.db so nothing is lost.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make the "app" package importable

from app.core.config import ConfigError, is_port_free, load_settings  # noqa: E402
from app.core.instance_lock import DataFolderLock, LockHeld  # noqa: E402
from app.database.backup import (  # noqa: E402
    BackupError,
    integrity_check,
    list_restorable,
    resolve_backup_name,
    restore_backup,
)


def print_restorable(settings) -> None:
    files = list_restorable(settings.backups_dir)
    if not files:
        print(f"There are no backups in {settings.backups_dir}.")
        return
    print(f"Backups in {settings.backups_dir} (newest first):")
    for path in files:
        modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {path.name}  {path.stat().st_size:>10} bytes  saved {modified} (local time)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="restore_db.py", description="List or restore AgentDesk database backups.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list the backups that can be restored")
    restore = sub.add_parser("restore", help="replace the database with a backup")
    restore.add_argument("file", help="file name of the backup, as shown by 'list'")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.command == "list":
        print_restorable(settings)
        return 0

    try:
        candidate = resolve_backup_name(settings.backups_dir, args.file)
    except BackupError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not is_port_free(settings.host, settings.port):
        print(
            f"Error: AgentDesk seems to be running (port {settings.port} is in use). "
            "Stop it first (press Ctrl+C in its window), then run this command again.",
            file=sys.stderr,
        )
        return 1

    # A running AgentDesk holds the data folder's lock, whatever port it uses. Holding the lock from
    # here until the database has been replaced also stops AgentDesk from starting in the meantime.
    lock = DataFolderLock(settings.data_dir)
    try:
        lock.acquire()
    except LockHeld:
        print(
            f"Error: AgentDesk seems to be running with the data folder {settings.data_dir} "
            "(possibly on another port), or another restore is in progress. "
            "Stop it first (press Ctrl+C in its window), then run this command again.",
            file=sys.stderr,
        )
        return 1
    except OSError as exc:
        print(f"Error: could not create the lock file {lock.path} ({exc.strerror or exc}).", file=sys.stderr)
        return 1
    try:
        return _confirm_and_restore(settings, candidate)
    finally:
        lock.release()


def _confirm_and_restore(settings, candidate) -> int:
    """Check the backup, ask for RESTORE and replace the database. The caller holds the lock."""
    result = integrity_check(candidate)
    if result != "ok":
        print(f"Error: {candidate.name} failed its integrity check ({result}). Choose another backup.", file=sys.stderr)
        return 1

    print(f"This replaces the AgentDesk database with {candidate.name}.")
    print("The current database will be kept in data\\backups as pre-restore-<time>.db.")
    try:
        answer = input("Type RESTORE to continue, or anything else to cancel: ")
    except EOFError:
        answer = ""
    if answer.strip() != "RESTORE":
        print("Cancelled. Nothing was changed.")
        return 1

    try:
        kept = restore_backup(settings, candidate.name)
    except BackupError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if kept:
        print(f"The previous database was kept as {kept}.")
    print(f"Restored {candidate.name}. Start AgentDesk again with scripts\\start.bat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
