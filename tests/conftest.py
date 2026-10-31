"""Shared fixtures: a temporary data folder per test and a test client for the app."""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

BASE_URL = "http://127.0.0.1:8765"


@pytest.fixture
def settings(tmp_path) -> Settings:
    """Default settings, but with the data folder inside this test's temporary folder."""
    return Settings(host="127.0.0.1", port=8765, data_dir=tmp_path / "data", log_level="INFO")


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app, base_url=BASE_URL) as test_client:
        yield test_client


@pytest.fixture
def csrf_token(client) -> str:
    return client.get("/api/v1/session").json()["csrf_token"]


def query(db_path: Path, sql: str, params=()):
    """Run a read query on a database file and close the connection."""
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def table_names(db_path: Path) -> set[str]:
    rows = query(db_path, "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
    return {row[0] for row in rows}
