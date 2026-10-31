"""Tester-agent tests (T-20261030-002-TST): backup, retention and restore edge cases.

FR-009, FR-010, FR-011.
"""

import hashlib
import sqlite3
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import app.database.backup as backup_module
from app.database.backup import (
    BackupError,
    create_backup,
    list_backups,
    list_restorable,
    prune_backups,
    resolve_backup_name,
    restore_backup,
)
from app.main import create_app
from tests.conftest import BASE_URL, query


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def agentdesk_files(settings):
    return sorted(p.name for p in settings.backups_dir.glob("agentdesk-*.db"))


def put(settings, key, value):
    conn = sqlite3.connect(settings.db_path)
    with conn:
        conn.execute("INSERT OR REPLACE INTO app_settings VALUES (?, ?, 't')", (key, value))
    conn.close()


@pytest.fixture
def started(settings):
    create_app(settings)
    return settings


def freeze_time(monkeypatch, when=None):
    when = when or datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(backup_module, "utc_now", lambda: when)
    return when


# ---------- creating and retention ----------

def test_tst_backup_names_follow_the_documented_pattern(started):
    info = create_backup(started, "manual")
    assert info.name.startswith("agentdesk-") and info.name.endswith("-manual.db")
    assert len(info.name) == len("agentdesk-20261031-120000-manual.db")
    assert info.reason == "manual" and info.created_at.tzinfo is not None


def test_tst_unknown_reason_is_rejected(started):
    with pytest.raises(ValueError):
        create_backup(started, "bogus")
    assert agentdesk_files(started) == []


def test_tst_three_backups_in_one_second_all_kept_and_distinct(started, monkeypatch):
    freeze_time(monkeypatch)
    names = [create_backup(started, "manual").name for _ in range(3)]
    assert len(set(names)) == 3
    assert agentdesk_files(started) == sorted(names)
    assert [b.sequence for b in list_backups(started.backups_dir)] == [3, 2, 1]


def test_tst_twelve_backups_in_one_second_keep_the_newest_ten(started, monkeypatch):
    """Retention must hold even when many backups share one second (a script in a loop)."""
    freeze_time(monkeypatch)
    last = None
    for _ in range(12):
        last = create_backup(started, "manual")  # must never raise
        assert last.path.is_file(), "the backup that was just made must still exist"
    files = agentdesk_files(started)
    assert len(files) == 10
    assert last.name in files


def test_tst_retention_keeps_ten_newest_by_time_and_spares_other_files(started):
    started.backups_dir.mkdir(exist_ok=True)
    for day in range(1, 16):
        (started.backups_dir / f"agentdesk-202601{day:02d}-000000-startup.db").write_bytes(b"old")
    spared = [
        "pre-restore-20250101-000000.db", "failed-agentdesk-20250101-000000-manual.db",
        "notes.txt", "agentdesk-20250101-000000-unknown.db", "agentdesk-2025.db",
        "agentdesk-20250101-000000-manual.db.partial", "AGENTDESK-20250101-000000-manual.db",
    ]
    for name in spared:
        (started.backups_dir / name).write_bytes(b"keep me")
    create_backup(started, "manual")
    files = [b.name for b in list_backups(started.backups_dir)]
    assert len(files) == 10
    assert "agentdesk-20260115-000000-startup.db" in files          # newest old file kept
    assert "agentdesk-20260101-000000-startup.db" not in files      # oldest removed
    for name in spared:
        assert (started.backups_dir / name).read_bytes() == b"keep me", name


def test_tst_prune_with_fewer_than_ten_removes_nothing(started):
    for _ in range(3):
        create_backup(started, "manual")
    assert prune_backups(started.backups_dir) == []
    assert len(agentdesk_files(started)) == 3


def test_tst_backup_is_a_consistent_copy_taken_while_database_is_in_use(started):
    put(started, "marker", "before")
    writer = sqlite3.connect(started.db_path)
    try:
        writer.execute("PRAGMA journal_mode=WAL")
        info = create_backup(started, "manual")
        assert query(info.path, "SELECT value FROM app_settings WHERE key='marker'") == [("before",)]
    finally:
        writer.close()


def test_tst_backup_of_damaged_source_fails_cleanly(started):
    started.db_path.write_bytes(b"not a database" * 100)
    with pytest.raises(BackupError):
        create_backup(started, "manual")
    assert agentdesk_files(started) == []
    assert not list(started.backups_dir.glob("*.partial"))


def test_tst_failed_integrity_check_keeps_a_failed_file_and_is_not_counted(started, monkeypatch):
    freeze_time(monkeypatch)
    real = backup_module.integrity_check
    monkeypatch.setattr(backup_module, "integrity_check", lambda path: "row 1 missing from index (simulated)")
    with pytest.raises(BackupError) as raised:
        create_backup(started, "manual")
    assert "integrity" in str(raised.value) and "failed-agentdesk-20261031-120000-manual.db" in str(raised.value)
    assert (started.backups_dir / "failed-agentdesk-20261031-120000-manual.db").is_file()
    assert agentdesk_files(started) == []
    assert not list(started.backups_dir.glob("*.partial"))
    assert list_backups(started.backups_dir) == []
    monkeypatch.setattr(backup_module, "integrity_check", real)
    for _ in range(11):  # retention never removes the failed file
        create_backup(started, "manual")
    assert (started.backups_dir / "failed-agentdesk-20261031-120000-manual.db").is_file()


def test_tst_api_reports_a_failed_backup_as_plain_json_error(started, monkeypatch):
    app = create_app(started)
    before = agentdesk_files(started)  # the second start made one automatic startup backup
    monkeypatch.setattr(backup_module, "integrity_check", lambda path: "malformed (simulated)")
    with TestClient(app, base_url=BASE_URL) as client:
        token = client.get("/api/v1/session").json()["csrf_token"]
        response = client.post("/api/v1/system/backups", json={}, headers={"X-AgentDesk-CSRF": token})
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "backup_failed"
    assert "Traceback" not in response.text
    assert agentdesk_files(started) == before


def test_tst_api_backup_list_and_create_roundtrip(started):
    app = create_app(started)
    with TestClient(app, base_url=BASE_URL) as client:
        token = client.get("/api/v1/session").json()["csrf_token"]
        baseline = len(client.get("/api/v1/system/backups").json()["backups"])  # one automatic startup backup
        for _ in range(2):
            assert client.post("/api/v1/system/backups", json={}, headers={"X-AgentDesk-CSRF": token}).status_code == 201
        listing = client.get("/api/v1/system/backups").json()["backups"]
        assert len(listing) == baseline + 2
        assert all(set(item) == {"name", "reason", "created_at", "size_bytes"} for item in listing)
        assert client.get("/api/v1/system").json()["last_backup"]["name"] == listing[0]["name"]


# ---------- restore name validation ----------

BAD_NAMES = [
    "", ".", "..", ".db", "../agentdesk.db", "..\\agentdesk.db", "sub/file.db", "sub\\file.db",
    "C:\\Windows\\win.ini", "C:/x.db", "\\\\localhost\\c$\\x.db", "//server/share/x.db",
    "/etc/passwd", "CON", "CON.db.", "x.db.", "x.db ", " x.db", "x.db:stream", "x.db::$DATA",
    "a..b.db", "x.txt", "x.DB.txt", "-rf.db ", "x\x00.db", "x?.db", "x*.db", "x<.db", "x|.db",
    "file name.db", "ünïcode.db", "a" * 300 + ".db",
]


@pytest.mark.parametrize("name", BAD_NAMES)
def test_tst_restore_refuses_bad_names(started, name):
    create_backup(started, "manual")
    before = sha(started.db_path)
    with pytest.raises(BackupError):
        restore_backup(started, name)
    assert sha(started.db_path) == before
    assert not list(started.backups_dir.glob("pre-restore-*"))


@pytest.mark.parametrize("name", ["CON.db", "NUL.db", "PRN.db", "AUX.db", "COM1.db", "LPT1.db", "con.db", "nul.db"])
def test_tst_restore_refuses_windows_reserved_device_names(started, name):
    create_backup(started, "manual")
    with pytest.raises(BackupError):
        resolve_backup_name(started.backups_dir, name)


def test_tst_restore_name_must_exist_and_be_a_file(started):
    create_backup(started, "manual")
    (started.backups_dir / "adir.db").mkdir()
    for name in ("adir.db", "missing.db"):
        with pytest.raises(BackupError):
            resolve_backup_name(started.backups_dir, name)


def test_tst_restore_refuses_absolute_path_to_a_real_backup(started):
    info = create_backup(started, "manual")
    for given in (str(info.path), str(info.path).replace("\\", "/"), "\\\\?\\" + str(info.path)):
        with pytest.raises(BackupError):
            resolve_backup_name(started.backups_dir, given)


def test_tst_restore_refuses_non_string_names(started):
    for bad in (None, 5, b"x.db", ["x.db"]):
        with pytest.raises(BackupError):
            resolve_backup_name(started.backups_dir, bad)


def test_tst_restore_refuses_backup_outside_folder_even_if_named_like_one(started, tmp_path):
    outside = tmp_path / "outside.db"
    outside.write_bytes(b"x")
    with pytest.raises(BackupError):
        resolve_backup_name(started.backups_dir, "outside.db")


# ---------- restore behaviour ----------

def test_tst_restore_keeps_previous_database_and_replaces_with_backup(started):
    put(started, "marker", "old")
    info = create_backup(started, "manual")
    put(started, "marker", "new")
    kept = restore_backup(started, info.name)
    assert kept.name.startswith("pre-restore-") and kept.name.endswith(".db")
    assert query(started.db_path, "SELECT value FROM app_settings WHERE key='marker'") == [("old",)]
    assert query(kept, "SELECT value FROM app_settings WHERE key='marker'") == [("new",)]
    assert info.path.is_file(), "the backup used must stay in place"


def test_tst_restore_moves_wal_and_shm_sidecars_with_the_old_database(started):
    info = create_backup(started, "manual")
    wal = started.db_path.with_name("agentdesk.db-wal")
    shm = started.db_path.with_name("agentdesk.db-shm")
    wal.write_bytes(b"stale-wal-content")
    shm.write_bytes(b"stale-shm-content")
    kept = restore_backup(started, info.name)
    assert not wal.exists() and not shm.exists(), "stale sidecars would corrupt the restored database"
    assert kept.with_name(kept.name + "-wal").read_bytes() == b"stale-wal-content"
    assert kept.with_name(kept.name + "-shm").read_bytes() == b"stale-shm-content"
    assert query(started.db_path, "SELECT count(*) FROM schema_migrations") == [(1,)]


def test_tst_two_restores_in_one_second_keep_both_old_databases(started, monkeypatch):
    freeze_time(monkeypatch)
    info = create_backup(started, "manual")
    put(started, "marker", "one")
    first = restore_backup(started, info.name)
    put(started, "marker", "two")
    second = restore_backup(started, info.name)
    assert first != second and first.is_file() and second.is_file()
    assert query(first, "SELECT count(*) FROM app_settings WHERE key='marker'") == [(1,)]


def test_tst_pre_restore_files_survive_later_backups_and_pruning(started, monkeypatch):
    from datetime import timedelta
    start = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)
    ticks = iter(range(1000))
    monkeypatch.setattr(backup_module, "utc_now", lambda: start + timedelta(seconds=next(ticks)))  # a new second each call
    info = create_backup(started, "manual")
    kept = restore_backup(started, info.name)
    for _ in range(12):
        create_backup(started, "manual")
    assert kept.is_file()


def test_tst_restore_when_no_current_database_returns_none(started):
    info = create_backup(started, "manual")
    started.db_path.unlink()
    for sidecar in started.data_dir.glob("agentdesk.db-*"):
        sidecar.unlink()
    assert restore_backup(started, info.name) is None
    assert started.db_path.is_file()


def test_tst_restore_of_damaged_backup_changes_nothing(started):
    put(started, "marker", "keep")
    bad = started.backups_dir / "agentdesk-20200101-000000-manual.db"
    bad.write_bytes(b"garbage" * 500)
    before = sha(started.db_path)
    with pytest.raises(BackupError) as raised:
        restore_backup(started, bad.name)
    assert "integrity" in str(raised.value)
    assert sha(started.db_path) == before
    assert not list(started.backups_dir.glob("pre-restore-*"))
    assert not list(started.data_dir.glob("*.restoring"))


def test_tst_restored_database_starts_and_serves_old_data(started):
    put(started, "marker", "old")
    info = create_backup(started, "manual")
    put(started, "marker", "new")
    restore_backup(started, info.name)
    app = create_app(started)
    with TestClient(app, base_url=BASE_URL) as client:
        assert client.get("/api/v1/system").json()["schema_version"] == 1
    assert query(started.db_path, "SELECT value FROM app_settings WHERE key='marker'") == [("old",)]


def test_tst_list_restorable_shows_only_accepted_names(started):
    create_backup(started, "manual")
    (started.backups_dir / "notes.txt").write_bytes(b"x")
    (started.backups_dir / "bad name.db").write_bytes(b"x")
    (started.backups_dir / "sub.db").mkdir()
    names = [p.name for p in list_restorable(started.backups_dir)]
    assert "notes.txt" not in names and "bad name.db" not in names and "sub.db" not in names
    assert len(names) == 1
