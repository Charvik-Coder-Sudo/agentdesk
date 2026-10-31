"""Tester-agent tests (T-20261030-002-TST): database startup, migrations and integrity edge cases.

FR-010, FR-012, FR-013, CON-005.
"""

import hashlib
import shutil
import sqlite3
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.timeutil import utc_now
from app.database.backup import BackupError, create_backup, list_backups
from app.database.connection import connect, transaction
from app.database.migrations import MIGRATIONS_DIR, file_checksum
from app.main import StartupError, create_app
from tests.conftest import BASE_URL, query, table_names

FOUNDATION = (MIGRATIONS_DIR / "0001_foundation.sql").read_bytes()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(delta):
    return (utc_now() - delta).strftime("%Y%m%d-%H%M%S")


@pytest.fixture
def mdir(tmp_path):
    folder = tmp_path / "migrations"
    folder.mkdir()
    (folder / "0001_foundation.sql").write_bytes(FOUNDATION)
    return folder


def backups_of(settings):
    return sorted(p.name for p in settings.backups_dir.glob("agentdesk-*.db"))


# ---------- migration folder problems ----------

def test_tst_empty_migrations_folder_gives_a_clean_startup_error(settings, tmp_path):
    empty = tmp_path / "empty-migrations"
    empty.mkdir()
    with pytest.raises(StartupError):
        create_app(settings, migrations_dir=empty)


def test_tst_missing_migrations_folder_gives_startup_error(settings, tmp_path):
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=tmp_path / "nope")
    assert "missing" in str(raised.value)


def test_tst_wrongly_named_files_are_ignored(settings, mdir, caplog):
    for name in ("0002_Upper.sql", "2_short.sql", "00002_long.sql", "0002-dash.sql", "0002_x.sql.txt",
                 "0002_x.SQL", "readme.md", "0002 space.sql", "0002_.sql"):
        (mdir / name).write_text("CREATE TABLE should_not_exist (x);", encoding="utf-8")
    (mdir / "subfolder.sql").mkdir()  # a folder with a migration-like name
    create_app(settings, migrations_dir=mdir)
    assert "should_not_exist" not in table_names(settings.db_path)
    assert "readme.md" in caplog.text


def test_tst_version_zero_stops_startup(settings, mdir):
    (mdir / "0000_zero.sql").write_text("CREATE TABLE z (x);", encoding="utf-8")
    with pytest.raises(StartupError):
        create_app(settings, migrations_dir=mdir)
    assert not settings.db_path.exists()


def test_tst_non_utf8_migration_stops_startup(settings, mdir):
    (mdir / "0002_bad.sql").write_bytes(b"CREATE TABLE t (x); -- \xff\xfe\x80")
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=mdir)
    assert "0002_bad.sql" in str(raised.value)


def test_tst_duplicate_version_stops_startup_without_touching_existing_database(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    before = sha(settings.db_path)
    (mdir / "0002_a.sql").write_text("CREATE TABLE a (x);", encoding="utf-8")
    (mdir / "0002_b.sql").write_text("CREATE TABLE b (x);", encoding="utf-8")
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=mdir)
    assert "0002" in str(raised.value) and "0002_a.sql" in str(raised.value) and "0002_b.sql" in str(raised.value)
    assert table_names(settings.db_path) == {"schema_migrations", "app_settings"}
    assert backups_of(settings) == []  # refused before any backup was needed
    assert sha(settings.db_path) == before


def test_tst_edited_applied_migration_leaves_database_and_backups_unchanged(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    before = sha(settings.db_path)
    (mdir / "0001_foundation.sql").write_bytes(FOUNDATION + b"\n-- edited\n")
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=mdir)
    assert "0001_foundation.sql" in str(raised.value)
    assert sha(settings.db_path) == before
    assert backups_of(settings) == []


def test_tst_trailing_space_edit_is_detected(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    (mdir / "0001_foundation.sql").write_bytes(FOUNDATION.replace(b"TEXT PRIMARY KEY", b"TEXT  PRIMARY KEY"))
    with pytest.raises(StartupError):
        create_app(settings, migrations_dir=mdir)


def test_tst_failing_second_migration_rolls_back_only_itself(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    (mdir / "0002_bad.sql").write_text(
        "CREATE TABLE half_done (x INTEGER);\nINSERT INTO half_done VALUES (1);\nTHIS IS NOT SQL;\n",
        encoding="utf-8",
    )
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=mdir)
    assert "0002_bad.sql" in str(raised.value) and "rolled back" in str(raised.value)
    assert table_names(settings.db_path) == {"schema_migrations", "app_settings"}
    assert [r[0] for r in query(settings.db_path, "SELECT version FROM schema_migrations")] == [1]
    # The pre-migration backup was made before the attempt and is a valid database.
    names = backups_of(settings)
    assert len(names) == 1 and names[0].endswith("-pre-migration.db")
    # A never-applied migration may be fixed: the next start applies it.
    (mdir / "0002_bad.sql").write_text("CREATE TABLE fixed (x INTEGER);", encoding="utf-8")
    create_app(settings, migrations_dir=mdir)
    assert "fixed" in table_names(settings.db_path)


def test_tst_failing_first_migration_on_new_database_is_not_recorded(settings, mdir):
    (mdir / "0001_foundation.sql").write_text("CREATE TABLE ok (x);\nSELECT * FROM nothing_here;\n", encoding="utf-8")
    with pytest.raises(StartupError):
        create_app(settings, migrations_dir=mdir)
    assert "ok" not in table_names(settings.db_path)
    assert query(settings.db_path, "SELECT count(*) FROM schema_migrations") == [(0,)]


def test_tst_bom_and_crlf_migration_applies_and_checksum_is_stable(settings, mdir):
    sql = "CREATE TABLE extra (\n  x INTEGER\n);\n"
    (mdir / "0002_extra.sql").write_bytes(b"\xef\xbb\xbf" + sql.replace("\n", "\r\n").encode("utf-8"))
    create_app(settings, migrations_dir=mdir)
    assert "extra" in table_names(settings.db_path)
    (stored,) = query(settings.db_path, "SELECT checksum FROM schema_migrations WHERE version = 2")[0]
    assert stored == hashlib.sha256(sql.encode("utf-8")).hexdigest() == file_checksum(sql)
    # The same text without BOM and with LF endings is not an edit.
    (mdir / "0002_extra.sql").write_bytes(sql.encode("utf-8"))
    create_app(settings, migrations_dir=mdir)


def test_tst_migration_numbers_may_have_gaps(settings, mdir):
    (mdir / "0005_later.sql").write_text("CREATE TABLE later (x);", encoding="utf-8")
    create_app(settings, migrations_dir=mdir)
    assert [r[0] for r in query(settings.db_path, "SELECT version FROM schema_migrations ORDER BY 1")] == [1, 5]


def test_tst_database_from_newer_version_is_refused(settings, mdir):
    (mdir / "0002_x.sql").write_text("CREATE TABLE x (a);", encoding="utf-8")
    create_app(settings, migrations_dir=mdir)
    (mdir / "0002_x.sql").unlink()
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=mdir)
    assert "0002" in str(raised.value)


def test_tst_no_migration_backup_when_nothing_is_pending(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    create_app(settings, migrations_dir=mdir)
    assert all(not n.endswith("pre-migration.db") for n in backups_of(settings))


def test_tst_instance_settings_survive_restarts_and_a_new_migration(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    first = query(settings.db_path, "SELECT key, value, updated_at FROM app_settings ORDER BY key")
    (mdir / "0002_extra.sql").write_text("CREATE TABLE extra (x);", encoding="utf-8")
    create_app(settings, migrations_dir=mdir)
    assert query(settings.db_path, "SELECT key, value, updated_at FROM app_settings ORDER BY key") == first
    assert {row[0] for row in first} == {"instance_id", "created_at"}


# ---------- damaged or unusual database files (FR-013) ----------

def _make_db_with_data(settings):
    create_app(settings)
    conn = sqlite3.connect(settings.db_path)
    with conn:
        for i in range(400):
            conn.execute("INSERT INTO app_settings VALUES (?, ?, ?)", (f"k{i}", "v" * 500, "t"))
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    for extra in settings.db_path.parent.glob("agentdesk.db-*"):
        extra.unlink()


@pytest.mark.parametrize("cut", ["header-only", "one-page", "mid-page", "one-page-short"])
def test_tst_truncated_database_stops_startup_and_is_left_alone(settings, cut):
    _make_db_with_data(settings)
    full = settings.db_path.read_bytes()
    size = {"header-only": 100, "one-page": 4096, "mid-page": 4096 * 3 + 123, "one-page-short": len(full) - 4097}[cut]
    settings.db_path.write_bytes(full[:size])
    before = sha(settings.db_path)
    with pytest.raises(StartupError) as raised:
        create_app(settings)
    assert "restore_db.py" in str(raised.value)
    assert sha(settings.db_path) == before
    assert settings.db_path.stat().st_size == size
    assert backups_of(settings) == []
    wal = settings.data_dir / "agentdesk.db-wal"
    assert not wal.exists() or wal.stat().st_size == 0, "a refused file must not get log content"


def test_tst_zero_byte_database_is_handled_without_a_crash(settings):
    settings.data_dir.mkdir(parents=True)
    settings.db_path.write_bytes(b"")
    try:
        app = create_app(settings)
    except StartupError:
        assert settings.db_path.stat().st_size == 0
        return
    # SQLite treats an empty file as a new database: it must then be fully usable.
    assert table_names(settings.db_path) == {"schema_migrations", "app_settings"}
    with TestClient(app, base_url=BASE_URL) as client:
        assert client.get("/api/v1/system").json()["schema_version"] == 1


def test_tst_database_path_that_is_a_folder_gives_startup_error(settings):
    settings.db_path.mkdir(parents=True)
    with pytest.raises(StartupError):
        create_app(settings)


def test_tst_damaged_database_with_leftover_wal_is_not_modified(settings):
    _make_db_with_data(settings)
    full = settings.db_path.read_bytes()
    settings.db_path.write_bytes(full[:5000])
    wal = settings.db_path.with_name("agentdesk.db-wal")
    wal.write_bytes(b"\x00" * 100)
    before_db, before_wal = sha(settings.db_path), sha(wal)
    with pytest.raises(StartupError):
        create_app(settings)
    assert sha(settings.db_path) == before_db
    assert sha(wal) == before_wal


def test_tst_wal_data_is_seen_by_startup_check_and_included_in_backup(settings):
    create_app(settings)
    writer = connect(settings.db_path)  # a second process would hold the database like this
    try:
        with transaction(writer):
            writer.execute("INSERT INTO app_settings VALUES ('wal_marker', 'only-in-wal', 't')")
        assert settings.db_path.with_name("agentdesk.db-wal").stat().st_size > 0
        create_app(settings)  # startup check with an uncheckpointed WAL
        info = create_backup(settings, "manual")
        assert query(info.path, "SELECT value FROM app_settings WHERE key = 'wal_marker'") == [("only-in-wal",)]
        assert not list(settings.backups_dir.glob("*-wal")) and not list(settings.backups_dir.glob("*-shm"))
    finally:
        writer.close()


def test_tst_healthy_database_is_not_altered_by_the_readonly_check(settings):
    create_app(settings)
    for sidecar in settings.data_dir.glob("agentdesk.db-*"):
        sidecar.unlink(missing_ok=True)
    # a cleanly closed WAL database: checked read-only, then migrated (nothing pending)
    conn = sqlite3.connect(settings.db_path)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    before_rows = query(settings.db_path, "SELECT key, value FROM app_settings ORDER BY key")
    create_app(settings)
    assert query(settings.db_path, "SELECT key, value FROM app_settings ORDER BY key") == before_rows


def test_tst_data_folder_with_special_characters(tmp_path):
    from app.core.config import Settings
    folder = tmp_path / "my data #1 100% x 'q' données-日本"
    settings = Settings(data_dir=folder)
    create_app(settings)
    create_app(settings)  # second start goes through the read-only URI path
    assert table_names(folder / "agentdesk.db") == {"schema_migrations", "app_settings"}
    assert create_backup(settings, "manual").path.is_file()


# ---------- startup backup timing and precedence (FR-010) ----------

def _dummy_backup(settings, delta, reason="manual", name_prefix="agentdesk"):
    settings.backups_dir.mkdir(parents=True, exist_ok=True)
    path = settings.backups_dir / f"{name_prefix}-{stamp(delta)}-{reason}.db"
    path.write_bytes(b"placeholder")
    return path


def test_tst_no_startup_backup_when_newest_is_23h59_old(settings):
    create_app(settings)
    _dummy_backup(settings, timedelta(hours=23, minutes=59))
    create_app(settings)
    assert [n for n in backups_of(settings) if n.endswith("-startup.db")] == []


def test_tst_startup_backup_when_newest_is_24h01_old(settings):
    create_app(settings)
    _dummy_backup(settings, timedelta(hours=24, minutes=1))
    create_app(settings)
    startup = [n for n in backups_of(settings) if n.endswith("-startup.db")]
    assert len(startup) == 1


def test_tst_newest_backup_decides_not_the_oldest(settings):
    create_app(settings)
    _dummy_backup(settings, timedelta(days=30))
    _dummy_backup(settings, timedelta(hours=1), reason="startup")
    create_app(settings)
    assert len(backups_of(settings)) == 2


def test_tst_other_files_do_not_count_as_a_recent_backup(settings):
    create_app(settings)
    _dummy_backup(settings, timedelta(days=2))
    for prefix in ("pre-restore", "failed-agentdesk"):
        _dummy_backup(settings, timedelta(minutes=1), name_prefix=prefix)
    (settings.backups_dir / "agentdesk-recent.db").write_bytes(b"x")
    create_app(settings)
    assert len([n for n in backups_of(settings) if n.endswith("-startup.db")]) == 1


def test_tst_future_dated_backup_counts_as_recent(settings):
    create_app(settings)
    _dummy_backup(settings, -timedelta(hours=2))
    create_app(settings)
    assert [n for n in backups_of(settings) if n.endswith("-startup.db")] == []


def test_tst_pre_migration_backup_takes_precedence_and_only_one_is_made(settings, mdir):
    create_app(settings, migrations_dir=mdir)
    _dummy_backup(settings, timedelta(days=3))  # a startup backup would also be due
    (mdir / "0002_extra.sql").write_text("CREATE TABLE extra (x);", encoding="utf-8")
    create_app(settings, migrations_dir=mdir)
    new = [n for n in backups_of(settings) if "-pre-migration" in n or "-startup" in n]
    assert len(new) == 1 and new[0].endswith("-pre-migration.db")
    # the pre-migration copy has the OLD schema
    path = settings.backups_dir / new[0]
    assert "extra" not in table_names(path)


def test_tst_new_database_gets_no_startup_backup_even_with_old_backups_present(settings):
    settings.backups_dir.mkdir(parents=True)
    _dummy_backup(settings, timedelta(days=10))
    create_app(settings)
    assert len(backups_of(settings)) == 1


def test_tst_failed_startup_backup_warns_and_starts(settings, monkeypatch):
    create_app(settings)
    _dummy_backup(settings, timedelta(days=5))
    import app.main as main

    def broken(settings, reason):
        raise BackupError("disk full (simulated)")

    monkeypatch.setattr(main, "create_backup", broken)
    app = create_app(settings)
    assert "disk full" in app.state.backup_warning
    with TestClient(app, base_url=BASE_URL) as client:
        body = client.get("/api/v1/system").json()
    assert "disk full" in body["backup_warning"]


def test_tst_failed_pre_migration_backup_stops_startup_without_migrating(settings, mdir, monkeypatch):
    create_app(settings, migrations_dir=mdir)
    (mdir / "0002_extra.sql").write_text("CREATE TABLE extra (x);", encoding="utf-8")
    import app.main as main

    def broken(settings, reason):
        raise BackupError("disk full (simulated)")

    monkeypatch.setattr(main, "create_backup", broken)
    before = sha(settings.db_path)
    with pytest.raises(StartupError) as raised:
        create_app(settings, migrations_dir=mdir)
    assert "did not start" in str(raised.value)
    assert "extra" not in table_names(settings.db_path)
    assert sha(settings.db_path) == before


def test_tst_backups_are_listed_newest_first_by_name_time(settings):
    create_app(settings)
    for hours in (5, 1, 3):
        _dummy_backup(settings, timedelta(hours=hours))
    created = [b.created_at for b in list_backups(settings.backups_dir)]
    assert created == sorted(created, reverse=True)


def test_tst_copy_of_database_is_independent_of_original(settings, tmp_path):
    create_app(settings)
    info = create_backup(settings, "manual")
    shutil.copy(info.path, tmp_path / "copy.db")
    conn = sqlite3.connect(tmp_path / "copy.db")
    assert conn.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
    assert conn.execute("PRAGMA journal_mode").fetchone() == ("delete",)
    conn.close()
