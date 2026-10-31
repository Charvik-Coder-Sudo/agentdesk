"""SQLite connections with AgentDesk's standard settings."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fastapi import Request

from app.api.errors import ApiError


def database_uri(db_path: Path, mode: str) -> str:
    """A file: URI for SQLite. mode "rw" opens an existing database only; "ro" also cannot write."""
    return Path(db_path).resolve().as_uri() + f"?mode={mode}"


def connect(db_path: Path, create: bool = True) -> sqlite3.Connection:
    """Open a read-write connection.

    create=False opens the database only if the file exists: a missing file gives an error
    instead of a new, empty database. Only the startup sequence may create the database.
    autocommit=True means Python never opens transactions on its own: we start them
    explicitly with transaction() (or BEGIN in the migration runner).
    check_same_thread=False lets FastAPI open and close the connection in different worker
    threads; each connection is still used by only one request at a time.
    """
    if create:
        conn = sqlite3.connect(db_path, timeout=5, autocommit=True, check_same_thread=False)
    else:
        conn = sqlite3.connect(
            database_uri(db_path, "rw"), uri=True, timeout=5, autocommit=True, check_same_thread=False
        )
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA temp_store=MEMORY")  # no temporary files in the Windows temp folder
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
    except BaseException:
        conn.close()
        raise
    return conn


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    """Open a connection that cannot change the database file (used for checks)."""
    conn = sqlite3.connect(database_uri(db_path, "ro"), uri=True, timeout=5, autocommit=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    """BEGIN IMMEDIATE ... COMMIT, or ROLLBACK if anything goes wrong."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")


def get_db(request: Request):
    """FastAPI dependency: one connection per request, always closed afterwards.

    The database must already exist (it is created at startup). If it is missing, for example
    because a restore is replacing it, the request gets a plain JSON error and no file is created.
    """
    try:
        conn = connect(request.app.state.settings.db_path, create=False)
    except sqlite3.Error:
        raise ApiError(
            503, "database_unavailable",
            "The AgentDesk database cannot be opened right now. Restart AgentDesk; if this keeps happening, "
            "see \"Backup and restore\" in README.md.",
        )
    try:
        yield conn
    finally:
        conn.close()
