"""FR-012 and CON-005: migrations, checksums, rollback and the backup before migrating."""

import logging
import shutil

import pytest

from app.database.migrations import MIGRATIONS_DIR, file_checksum
from app.main import StartupError, create_app
from tests.conftest import query, table_names


@pytest.fixture
def migrations_dir(tmp_path):
    """A private copy of the real migrations folder that a test may change."""
    target = tmp_path / "migrations"
    shutil.copytree(MIGRATIONS_DIR, target)
    return target


def snapshot(db_path):
    return (
        query(db_path, "SELECT version, name, checksum, applied_at FROM schema_migrations ORDER BY version"),
        query(db_path, "SELECT key, value, updated_at FROM app_settings ORDER BY key"),
        table_names(db_path),
    )


def test_new_database_reaches_version_1_with_two_tables(settings):
    create_app(settings)
    assert table_names(settings.db_path) == {"schema_migrations", "app_settings"}
    rows = query(settings.db_path, "SELECT version, name, checksum, applied_at FROM schema_migrations")
    assert len(rows) == 1
    version, name, checksum, applied_at = rows[0]
    assert (version, name) == (1, "foundation")
    expected = file_checksum((MIGRATIONS_DIR / "0001_foundation.sql").read_text(encoding="utf-8"))
    assert checksum == expected and len(checksum) == 64
    assert applied_at.endswith("Z")


def test_instance_settings_created_once(settings):
    create_app(settings)
    keys = dict(query(settings.db_path, "SELECT key, value FROM app_settings"))
    assert set(keys) == {"instance_id", "created_at"}
    assert len(keys["instance_id"]) == 32


def test_second_start_changes_nothing(settings):
    create_app(settings)
    before = snapshot(settings.db_path)
    create_app(settings)
    assert snapshot(settings.db_path) == before


def test_edited_applied_migration_stops_startup(settings, migrations_dir):
    create_app(settings, migrations_dir)
    before = snapshot(settings.db_path)
    path = migrations_dir / "0001_foundation.sql"
    path.write_text(path.read_text(encoding="utf-8") + "\n-- edited\n", encoding="utf-8")
    with pytest.raises(StartupError, match="0001_foundation.sql"):
        create_app(settings, migrations_dir)
    assert snapshot(settings.db_path) == before


def test_line_ending_change_is_not_an_edit(settings, migrations_dir):
    create_app(settings, migrations_dir)
    path = migrations_dir / "0001_foundation.sql"
    text = path.read_bytes().replace(b"\r\n", b"\n")
    path.write_bytes(text.replace(b"\n", b"\r\n"))  # what a Git checkout with autocrlf does
    create_app(settings, migrations_dir)  # must not raise


def test_failing_migration_is_rolled_back_and_not_recorded(settings, migrations_dir):
    create_app(settings, migrations_dir)
    (migrations_dir / "0002_broken.sql").write_text(
        "CREATE TABLE half_done (x INTEGER) STRICT;\nINSERT INTO no_such_table VALUES (1);\n",
        encoding="utf-8",
    )
    with pytest.raises(StartupError, match="0002_broken.sql"):
        create_app(settings, migrations_dir)
    assert "half_done" not in table_names(settings.db_path)
    assert query(settings.db_path, "SELECT version FROM schema_migrations") == [(1,)]


def test_backup_taken_before_migrating_existing_database(settings, migrations_dir):
    create_app(settings, migrations_dir)
    (migrations_dir / "0002_extra.sql").write_text("CREATE TABLE extra (x INTEGER) STRICT;\n", encoding="utf-8")
    create_app(settings, migrations_dir)

    backups = list(settings.backups_dir.glob("agentdesk-*-pre-migration.db"))
    assert len(backups) == 1
    # The backup holds the state from before the migration.
    assert query(backups[0], "SELECT version FROM schema_migrations") == [(1,)]
    assert query(settings.db_path, "SELECT version FROM schema_migrations ORDER BY version") == [(1,), (2,)]
    # At most one automatic backup per start: no extra "startup" backup.
    assert list(settings.backups_dir.glob("agentdesk-*-startup.db")) == []


def test_new_database_gets_no_backup(settings):
    create_app(settings)
    assert list(settings.backups_dir.iterdir()) == []


def test_wrongly_named_files_are_ignored(settings, migrations_dir, caplog):
    (migrations_dir / "2-bad-name.sql").write_text("CREATE TABLE nope (x INTEGER);", encoding="utf-8")
    (migrations_dir / "notes.txt").write_text("not a migration", encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        create_app(settings, migrations_dir)
    assert "nope" not in table_names(settings.db_path)
    assert "2-bad-name.sql" in caplog.text


def test_duplicate_migration_number_stops_startup(settings, migrations_dir):
    (migrations_dir / "0001_other.sql").write_text("CREATE TABLE other (x INTEGER);", encoding="utf-8")
    with pytest.raises(StartupError, match="0001"):
        create_app(settings, migrations_dir)


def test_applied_migration_missing_file_stops_startup(settings, migrations_dir):
    (migrations_dir / "0002_extra.sql").write_text("CREATE TABLE extra (x INTEGER) STRICT;\n", encoding="utf-8")
    create_app(settings, migrations_dir)
    (migrations_dir / "0002_extra.sql").unlink()
    with pytest.raises(StartupError, match="0002"):
        create_app(settings, migrations_dir)
