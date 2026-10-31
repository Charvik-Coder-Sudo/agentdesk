"""FR-009, FR-010 and FR-011: backups, retention, the startup backup and restore."""

import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
from datetime import timedelta

import pytest

from app.core.config import REPO_ROOT
from app.core.timeutil import utc_now
from app.database.backup import (
    BackupError,
    create_backup,
    integrity_check,
    list_backups,
    restore_backup,
)
from app.main import create_app
from tests.conftest import query

NAME_PATTERN = re.compile(r"^agentdesk-\d{8}-\d{6}-manual(-\d+)?\.db$")


def set_marker(db_path, value):
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('test_marker', ?, 'now')",
            (value,),
        )
    conn.close()


def get_marker(db_path):
    rows = query(db_path, "SELECT value FROM app_settings WHERE key = 'test_marker'")
    return rows[0][0] if rows else None


def old_backup_name(minutes_ago, reason="manual"):
    stamp = (utc_now() - timedelta(days=30, minutes=minutes_ago)).strftime("%Y%m%d-%H%M%S")
    return f"agentdesk-{stamp}-{reason}.db"


# ---------- Creating backups (FR-009, FR-010) ----------

def test_backup_file_created_and_passes_integrity_check(settings):
    create_app(settings)
    info = create_backup(settings, "manual")
    assert NAME_PATTERN.match(info.name)
    assert info.path.parent == settings.backups_dir
    assert integrity_check(info.path) == "ok"
    assert query(info.path, "PRAGMA integrity_check") == [("ok",)]
    assert query(info.path, "SELECT version FROM schema_migrations") == [(1,)]


def test_api_backup_appears_in_list(client, settings, csrf_token):
    response = client.post("/api/v1/system/backups", json={}, headers={"X-AgentDesk-CSRF": csrf_token})
    assert response.status_code == 201
    data = response.json()
    assert data["integrity"] == "ok"
    name = data["backup"]["name"]
    assert NAME_PATTERN.match(name)
    assert (settings.backups_dir / name).is_file()
    listed = client.get("/api/v1/system/backups").json()["backups"]
    assert listed[0]["name"] == name
    assert listed[0]["reason"] == "manual"
    assert client.get("/api/v1/system").json()["last_backup"]["name"] == name


def test_two_backups_in_the_same_second_get_different_names(settings):
    create_app(settings)
    names = {create_backup(settings, "manual").name for _ in range(3)}
    assert len(names) == 3


def test_only_newest_10_kept_and_other_files_untouched(settings):
    create_app(settings)
    settings.backups_dir.mkdir(exist_ok=True)
    old_names = [old_backup_name(minutes) for minutes in range(12, 0, -1)]  # oldest first
    for name in old_names:
        shutil.copy(settings.db_path, settings.backups_dir / name)
    foreign = ["pre-restore-20200101-000000.db", "notes.txt", "agentdesk-foreign.db", "failed-agentdesk-x.db"]
    for name in foreign:
        (settings.backups_dir / name).write_bytes(b"keep me")

    newest = create_backup(settings, "manual")

    remaining = [info.name for info in list_backups(settings.backups_dir)]
    assert len(remaining) == 10
    assert remaining[0] == newest.name
    assert remaining[1:] == list(reversed(old_names))[:9]  # the 9 newest old ones
    for name in foreign:
        assert (settings.backups_dir / name).read_bytes() == b"keep me"


def test_startup_backup_when_newest_is_older_than_24_hours(settings):
    create_app(settings)  # new database: no backup
    assert list_backups(settings.backups_dir) == []
    create_app(settings)  # existing database, no backup yet -> startup backup
    backups = list_backups(settings.backups_dir)
    assert [b.reason for b in backups] == ["startup"]
    assert integrity_check(backups[0].path) == "ok"

    create_app(settings)  # newest backup is recent -> no new backup
    assert len(list_backups(settings.backups_dir)) == 1

    # Make the only backup look 25 hours old: a new startup backup is taken.
    old = backups[0].path
    stamp = (utc_now() - timedelta(hours=25)).strftime("%Y%m%d-%H%M%S")
    old.rename(old.with_name(f"agentdesk-{stamp}-startup.db"))
    create_app(settings)
    assert len(list_backups(settings.backups_dir)) == 2


def test_backup_without_database_refused(settings):
    with pytest.raises(BackupError):
        create_backup(settings, "manual")


# ---------- Restore (FR-011) ----------

def test_restore_brings_back_earlier_data_and_keeps_replaced_database(settings):
    create_app(settings)
    set_marker(settings.db_path, "before")
    backup = create_backup(settings, "manual")
    set_marker(settings.db_path, "after")

    kept = restore_backup(settings, backup.name)

    assert get_marker(settings.db_path) == "before"
    assert kept is not None and kept.parent == settings.backups_dir
    assert kept.name.startswith("pre-restore-")
    assert get_marker(kept) == "after"
    # The app starts normally on the restored database.
    create_app(settings)
    assert get_marker(settings.db_path) == "before"


@pytest.mark.parametrize(
    "name",
    [
        "../agentdesk.db",
        "..\\agentdesk.db",
        "sub/agentdesk.db",
        "sub\\agentdesk.db",
        "C:agentdesk.db",
        "C:\\Windows\\agentdesk.db",
        "/etc/agentdesk.db",
        ".hidden.db",
        "agentdesk.txt",
        "",
    ],
)
def test_restore_refuses_names_outside_backups_folder(settings, name):
    create_app(settings)
    set_marker(settings.db_path, "current")
    with pytest.raises(BackupError):
        restore_backup(settings, name)
    assert get_marker(settings.db_path) == "current"


def test_restore_refuses_missing_file(settings):
    create_app(settings)
    with pytest.raises(BackupError, match="no backup named"):
        restore_backup(settings, "agentdesk-20200101-000000-manual.db")


def test_restore_refuses_damaged_backup(settings):
    create_app(settings)
    set_marker(settings.db_path, "current")
    bad = settings.backups_dir / "agentdesk-20200101-000000-manual.db"
    bad.write_bytes(b"this is not a database" * 100)
    with pytest.raises(BackupError, match="integrity"):
        restore_backup(settings, bad.name)
    assert get_marker(settings.db_path) == "current"


# ---------- Command-line scripts (FR-011) ----------

def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run_script(script, args, settings, port, stdin=""):
    env = dict(os.environ, AGENTDESK_DATA_DIR=str(settings.data_dir), AGENTDESK_PORT=str(port))
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script), *args],
        cwd=REPO_ROOT, env=env, input=stdin, capture_output=True, text=True, timeout=60,
    )


def test_backup_script_create_and_list(settings):
    create_app(settings)
    port = free_port()
    created = run_script("backup_db.py", ["create"], settings, port)
    assert created.returncode == 0, created.stderr
    assert "Backup created" in created.stdout
    listed = run_script("backup_db.py", ["list"], settings, port)
    assert listed.returncode == 0
    assert list_backups(settings.backups_dir)[0].name in listed.stdout


def test_restore_script_refuses_while_running(settings):
    create_app(settings)
    backup = create_backup(settings, "manual")
    with socket.socket() as busy:  # pretend AgentDesk is running on this port
        busy.bind(("127.0.0.1", 0))
        busy.listen()
        port = busy.getsockname()[1]
        result = run_script("restore_db.py", ["restore", backup.name], settings, port, stdin="RESTORE\n")
    assert result.returncode != 0
    assert "running" in result.stderr
    assert not list(settings.backups_dir.glob("pre-restore-*"))


def test_restore_script_cancels_without_typed_restore(settings):
    create_app(settings)
    set_marker(settings.db_path, "before")
    backup = create_backup(settings, "manual")
    set_marker(settings.db_path, "after")
    result = run_script("restore_db.py", ["restore", backup.name], settings, free_port(), stdin="yes\n")
    assert result.returncode != 0
    assert "Cancelled" in result.stdout
    assert get_marker(settings.db_path) == "after"


def test_restore_script_restores_after_typed_restore(settings):
    create_app(settings)
    set_marker(settings.db_path, "before")
    backup = create_backup(settings, "manual")
    set_marker(settings.db_path, "after")
    result = run_script("restore_db.py", ["restore", backup.name], settings, free_port(), stdin="RESTORE\n")
    assert result.returncode == 0, result.stderr
    assert get_marker(settings.db_path) == "before"
    assert len(list(settings.backups_dir.glob("pre-restore-*.db"))) == 1


def test_restore_script_refuses_path_outside_backups(settings):
    create_app(settings)
    result = run_script("restore_db.py", ["restore", "..\\agentdesk.db"], settings, free_port(), stdin="RESTORE\n")
    assert result.returncode != 0
    assert "file name" in result.stderr
