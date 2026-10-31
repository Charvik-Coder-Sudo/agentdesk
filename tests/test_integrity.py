"""FR-013: a damaged database stops startup and is left byte-for-byte unchanged."""

import hashlib
import sqlite3

import pytest

from app.main import StartupError, create_app


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_garbage_database_file_stops_startup_unchanged(settings):
    settings.data_dir.mkdir(parents=True)
    settings.db_path.write_bytes(b"this is not an SQLite database " * 200)
    before = sha256(settings.db_path)
    with pytest.raises(StartupError) as raised:
        create_app(settings)
    assert "restore_db.py" in str(raised.value)
    assert sha256(settings.db_path) == before
    assert list(settings.backups_dir.glob("agentdesk-*.db")) == []  # no backup of a damaged file


def test_damaged_page_stops_startup_unchanged(settings):
    create_app(settings)
    # Add some rows so the database has several pages, then overwrite the pages after the first.
    conn = sqlite3.connect(settings.db_path)
    with conn:
        for number in range(200):
            conn.execute(
                "INSERT INTO app_settings (key, value, updated_at) VALUES (?, ?, 'now')",
                (f"filler_{number}", "x" * 200),
            )
    conn.close()
    data = bytearray(settings.db_path.read_bytes())
    assert len(data) > 3 * 4096
    page_size = int.from_bytes(data[16:18], "big")
    data[page_size:] = b"\xff" * (len(data) - page_size)
    settings.db_path.write_bytes(bytes(data))
    before = sha256(settings.db_path)

    with pytest.raises(StartupError, match="integrity check"):
        create_app(settings)
    assert sha256(settings.db_path) == before


def test_healthy_database_reports_ok(client):
    integrity = client.get("/api/v1/system").json()["integrity"]
    assert integrity["result"] == "ok"
    assert integrity["check"] == "quick_check"
