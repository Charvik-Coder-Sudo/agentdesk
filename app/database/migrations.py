"""Migration runner: applies migrations/NNNN_<name>.sql files in order, once each.

- Each file runs in its own transaction together with its schema_migrations record,
  so a failing migration leaves no trace.
- The SHA-256 checksum of every applied file is stored. If an applied file is edited later,
  AgentDesk refuses to start and names the file.
- Migration files must not contain transaction-control statements (BEGIN, COMMIT, END, ROLLBACK,
  SAVEPOINT, RELEASE): such a file is refused before anything is applied (DEC-025).
  CREATE TRIGGER ... BEGIN ... END bodies are allowed.
"""

import hashlib
import logging
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.core.config import REPO_ROOT
from app.core.timeutil import utc_now_iso

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = REPO_ROOT / "migrations"
# \Z (not $) so that a name ending in a newline never matches (SEC-015).
FILE_PATTERN = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql\Z")
TRANSACTION_CONTROL = ("BEGIN", "COMMIT", "END", "ROLLBACK", "SAVEPOINT", "RELEASE")

# Created by the runner itself, before any migration file (database-schema.md section 3).
BOOTSTRAP_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    checksum    TEXT    NOT NULL,
    applied_at  TEXT    NOT NULL
) STRICT
"""


class MigrationError(Exception):
    """A migration problem that must stop startup. The message says what to do."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    filename: str
    sql: str
    checksum: str


def file_checksum(text: str) -> str:
    """SHA-256 of the file text. Line endings are normalized, so a Git checkout that turns
    LF into CRLF does not count as an edit."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def discover_migrations(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    """Find migration files, ordered by version. Wrongly named files are ignored with a warning."""
    if not directory.is_dir():
        raise MigrationError(f"The migrations folder {directory} is missing. Restore it from Git.")

    found: dict[int, Migration] = {}
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        match = FILE_PATTERN.fullmatch(path.name)
        if not match:
            logger.warning(
                "Ignoring %s in the migrations folder: migration files must be named like 0001_name.sql",
                path.name,
            )
            continue
        version = int(match.group(1))
        if version == 0:
            raise MigrationError(f"{path.name}: migration numbers start at 0001.")
        if version in found:
            raise MigrationError(
                f"Two migration files have the number {version:04d}: "
                f"{found[version].filename} and {path.name}. Each number may be used only once."
            )
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise MigrationError(f"{path.name} is not a UTF-8 text file.") from exc
        keyword = transaction_control_keyword(text)
        if keyword:
            raise MigrationError(
                f"The migration file {path.name} contains a {keyword} statement. Migration files must not contain "
                "BEGIN, COMMIT, END, ROLLBACK, SAVEPOINT or RELEASE statements, because AgentDesk runs each "
                "migration in its own transaction. Remove the statement. Nothing was applied."
            )
        found[version] = Migration(version, match.group(2), path.name, text, file_checksum(text))
    if not found:
        raise MigrationError(
            f"No migration files were found in {directory}. AgentDesk needs the files of its migrations folder "
            "(for example 0001_foundation.sql) to create and check the database. Restore the migrations folder "
            "of AgentDesk (from Git, or from a fresh copy of AgentDesk), then start AgentDesk again. "
            "No database file was created or changed."
        )
    return [found[version] for version in sorted(found)]


def split_statements(sql: str) -> list[str]:
    """Split SQL text into statements. sqlite3.complete_statement understands strings, comments and
    CREATE TRIGGER ... BEGIN ... END bodies, so semicolons inside them do not end a statement."""
    statements = []
    current = ""
    pieces = sql.split(";")
    for piece in pieces[:-1]:
        current += piece + ";"
        if sqlite3.complete_statement(current):
            statements.append(current)
            current = ""
    current += pieces[-1]
    if current.strip():
        statements.append(current)  # text after the last semicolon
    return statements


def _first_keyword(statement: str) -> str:
    """The first word of a statement in upper case, skipping leading comments."""
    text = statement
    while True:
        text = text.lstrip()
        if text.startswith("--"):
            end = text.find("\n")
            text = "" if end < 0 else text[end + 1:]
        elif text.startswith("/*"):
            end = text.find("*/")
            text = "" if end < 0 else text[end + 2:]
        else:
            break
    match = re.match(r"[A-Za-z]+", text)
    return match.group(0).upper() if match else ""


def transaction_control_keyword(sql: str) -> str | None:
    """The keyword of the first transaction-control statement in the SQL text, or None."""
    for statement in split_statements(sql):
        keyword = _first_keyword(statement)
        if keyword in TRANSACTION_CONTROL:
            return keyword
    return None


def read_applied(conn: sqlite3.Connection) -> dict[int, dict]:
    """The applied migrations recorded in the database (empty for a new database)."""
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
    ).fetchone()
    if table is None:
        return {}
    rows = conn.execute(
        "SELECT version, name, checksum, applied_at FROM schema_migrations ORDER BY version"
    ).fetchall()
    return {row["version"]: dict(row) for row in rows}


def pending_migrations(applied: dict[int, dict], available: list[Migration]) -> list[Migration]:
    """Check the applied migrations against the files and return those not yet applied."""
    by_version = {migration.version: migration for migration in available}
    for version, row in applied.items():
        migration = by_version.get(version)
        if migration is None:
            raise MigrationError(
                f"The database has migration {version:04d} ({row['name']}) applied, but its file is "
                "missing from the migrations folder. The database was probably created by a newer "
                "AgentDesk version: use that version, or restore an older backup with scripts\\restore_db.py."
            )
        if migration.checksum != row["checksum"]:
            raise MigrationError(
                f"The migration file {migration.filename} was changed after it was applied to the database. "
                f"Applied migration files must never be edited: undo the change to migrations\\{migration.filename} "
                "(for example with 'git diff migrations'), then start AgentDesk again. The database was not changed."
            )
    return [migration for migration in available if migration.version not in applied]


def apply_migrations(conn: sqlite3.Connection, pending: list[Migration]) -> None:
    """Apply each pending migration in its own transaction. Raises MigrationError on failure."""
    conn.execute(BOOTSTRAP_SQL)
    for migration in pending:
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.executescript(migration.sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES (?, ?, ?, ?)",
                (migration.version, migration.name, migration.checksum, utc_now_iso()),
            )
            conn.execute("COMMIT")
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise MigrationError(
                f"The migration {migration.filename} failed and was rolled back ({exc}). "
                "Nothing from this migration was saved and AgentDesk did not start."
            ) from exc
        logger.info("Applied migration %s", migration.filename)


def schema_version(conn: sqlite3.Connection) -> int:
    """The highest applied migration version (0 if none)."""
    return max(read_applied(conn), default=0)
