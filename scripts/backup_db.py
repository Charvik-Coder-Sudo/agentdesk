r"""Create or list AgentDesk database backups from the command line.

Usage (in the AgentDesk folder):
    .venv\Scripts\python scripts\backup_db.py create
    .venv\Scripts\python scripts\backup_db.py list

Creating a backup is safe while AgentDesk is running.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make the "app" package importable

from app.core.config import ConfigError, load_settings  # noqa: E402
from app.core.timeutil import to_iso  # noqa: E402
from app.database.backup import BackupError, create_backup, list_backups  # noqa: E402


def print_backups(settings) -> None:
    backups = list_backups(settings.backups_dir)
    if not backups:
        print(f"There are no backups in {settings.backups_dir}.")
        return
    print(f"Backups in {settings.backups_dir} (newest first, times in UTC):")
    for info in backups:
        print(f"  {info.name}  {info.reason:<13}  {info.size_bytes:>10} bytes  {to_iso(info.created_at)}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="backup_db.py", description="Create or list AgentDesk database backups.")
    parser.add_argument("command", choices=["create", "list"], help="create a new backup, or list the backups")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.command == "list":
        print_backups(settings)
        return 0

    try:
        info = create_backup(settings, "manual")
    except BackupError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Backup created and integrity-checked: {info.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
