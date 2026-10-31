"""Tester-agent tests (T-20261030-002-TST): configuration and the command-line scripts.

NFR-001, NFR-011, CON-003, FR-011. The scripts run as real subprocesses against a temporary data
folder, started from a different working folder, with a free port in AGENTDESK_PORT.
"""

import hashlib
import os
import socket
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.config import ConfigError, REPO_ROOT, Settings, is_port_free, load_settings
from app.database.backup import create_backup
from app.main import StartupError, create_app
from tests.conftest import query

SCRIPTS = REPO_ROOT / "scripts"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run_script(script, args, data_dir, port, cwd, stdin=None, extra_env=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(data_dir), "AGENTDESK_PORT": str(port), "PYTHONUTF8": "1"})
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        input=stdin if stdin is not None else "", capture_output=True, text=True, cwd=str(cwd), env=env, timeout=60,
    )


@pytest.fixture
def world(tmp_path):
    """A started data folder with one backup, a free port and a neutral working folder."""
    settings = Settings(port=free_port(), data_dir=tmp_path / "data")
    create_app(settings)
    conn = sqlite3.connect(settings.db_path)
    with conn:
        conn.execute("INSERT INTO app_settings VALUES ('marker', 'old', 't')")
    conn.close()
    info = create_backup(settings, "manual")
    conn = sqlite3.connect(settings.db_path)
    with conn:
        conn.execute("INSERT OR REPLACE INTO app_settings VALUES ('marker', 'new', 't')")
    conn.close()
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    return settings, info, cwd


def marker(settings):
    return query(settings.db_path, "SELECT value FROM app_settings WHERE key='marker'")[0][0]


# ---------- load_settings (NFR-001, CON-003) ----------

@pytest.mark.parametrize(
    "host", ["0.0.0.0", "::", "192.168.1.5", "example.com", "", " ", "LOCALHOST", "127.0.0.2", "127.0.0.1:8765",
            "[::1]", "localhost.", "0", "*", "127.0.0.1 evil", "::ffff:127.0.0.1"],
)
def test_tst_hosts_other_than_the_three_loopback_names_refused(host):
    with pytest.raises(ConfigError) as raised:
        load_settings({"AGENTDESK_HOST": host})
    assert "AGENTDESK_HOST" in str(raised.value)


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1", " 127.0.0.1 ", "\t::1\n"])
def test_tst_loopback_hosts_accepted_with_surrounding_whitespace_trimmed(host):
    assert load_settings({"AGENTDESK_HOST": host}).host == host.strip()


@pytest.mark.parametrize("port", ["1024", "1025", "8765", "65534", "65535", " 8765 "])
def test_tst_port_boundaries_accepted(port):
    assert load_settings({"AGENTDESK_PORT": port}).port == int(port)


@pytest.mark.parametrize(
    "port", ["0", "1", "80", "1023", "65536", "65537", "99999", "-1", "-8765", "", " ", "abc", "8765abc",
            "8765.5", "8,765", "1e4", "0x2000", "NaN", "inf", "8765\x00"],
)
def test_tst_port_outside_bounds_or_not_a_number_refused(port):
    with pytest.raises(ConfigError) as raised:
        load_settings({"AGENTDESK_PORT": port})
    assert "AGENTDESK_PORT" in str(raised.value)
    assert "1024" in str(raised.value) and "65535" in str(raised.value)  # says what to do


def test_tst_every_config_error_names_the_variable_and_the_fix():
    for env in ({"AGENTDESK_HOST": "0.0.0.0"}, {"AGENTDESK_PORT": "1"}, {"AGENTDESK_LOG_LEVEL": "LOUD"}):
        with pytest.raises(ConfigError) as raised:
            load_settings(env)
        text = str(raised.value)
        assert next(iter(env)) in text
        assert "Use" in text or "use" in text


@pytest.mark.parametrize("level", ["debug", "Info", "WARNING", " error "])
def test_tst_log_level_is_case_insensitive(level):
    assert load_settings({"AGENTDESK_LOG_LEVEL": level}).log_level == level.strip().upper()


@pytest.mark.parametrize("level", ["", "TRACE", "CRITICAL", "10", "NOTSET"])
def test_tst_unknown_log_levels_refused(level):
    with pytest.raises(ConfigError):
        load_settings({"AGENTDESK_LOG_LEVEL": level})


def test_tst_environment_overrides_combine(tmp_path):
    settings = load_settings(
        {"AGENTDESK_HOST": "localhost", "AGENTDESK_PORT": "9001", "AGENTDESK_DATA_DIR": str(tmp_path / "d"),
         "AGENTDESK_LOG_LEVEL": "warning"}
    )
    assert (settings.host, settings.port, settings.log_level) == ("localhost", 9001, "WARNING")
    assert settings.db_path == (tmp_path / "d").resolve() / "agentdesk.db"
    assert settings.backups_dir.parent == settings.logs_dir.parent == settings.data_dir
    assert settings.base_url == "http://localhost:9001"


def test_tst_empty_or_blank_data_dir_means_default():
    for value in ("", "   "):
        assert load_settings({"AGENTDESK_DATA_DIR": value}).data_dir == REPO_ROOT / "data"
    assert load_settings({}).data_dir == REPO_ROOT / "data"


def test_tst_relative_data_dir_is_resolved_to_an_absolute_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = load_settings({"AGENTDESK_DATA_DIR": "rel\\folder"})
    assert settings.data_dir.is_absolute()
    assert settings.data_dir == (tmp_path / "rel" / "folder").resolve()


def test_tst_default_data_dir_is_ignored_by_git():
    ignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for entry in ("data/", ".venv/", "*.db", "*.db-wal", "*.db-shm", "*.log", ".sandbox/", ".pytest_tmp/"):
        assert entry in ignore, entry


def test_tst_data_dir_that_is_a_file_gives_startup_error_not_a_traceback(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    with pytest.raises(StartupError):
        create_app(Settings(data_dir=blocker))


def test_tst_data_dir_below_a_file_gives_startup_error_not_a_traceback(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(StartupError):
        create_app(Settings(data_dir=blocker / "data"))


def test_tst_is_port_free_detects_a_listener_and_free_ports():
    port = free_port()
    assert is_port_free("127.0.0.1", port)
    assert is_port_free("localhost", port)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", port))
        listener.listen()
        assert not is_port_free("127.0.0.1", port)
        assert not is_port_free("localhost", port)
    assert is_port_free("127.0.0.1", port)


def test_tst_settings_are_immutable():
    settings = Settings()
    with pytest.raises(Exception):
        settings.port = 1


# ---------- backup_db.py ----------

def test_tst_backup_script_create_prints_path_and_list_shows_it(world):
    settings, info, cwd = world
    created = run_script("backup_db.py", ["create"], settings.data_dir, settings.port, cwd)
    assert created.returncode == 0, created.stderr
    printed = created.stdout.strip().split(": ", 1)[1]
    assert Path(printed).is_file() and Path(printed).parent == settings.backups_dir
    listed = run_script("backup_db.py", ["list"], settings.data_dir, settings.port, cwd)
    assert listed.returncode == 0
    assert Path(printed).name in listed.stdout and info.name in listed.stdout


def test_tst_backup_script_without_database_fails_with_a_message(tmp_path):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    result = run_script("backup_db.py", ["create"], tmp_path / "nodata", free_port(), cwd)
    assert result.returncode == 1
    assert "no database" in result.stderr.lower() and "Traceback" not in result.stderr


def test_tst_backup_script_list_with_no_backups(tmp_path):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    result = run_script("backup_db.py", ["list"], tmp_path / "nodata", free_port(), cwd)
    assert result.returncode == 0 and "no backups" in result.stdout.lower()


def test_tst_backup_script_on_damaged_database_fails_cleanly(world):
    settings, _, cwd = world
    settings.db_path.write_bytes(b"junk" * 500)
    for sidecar in settings.data_dir.glob("agentdesk.db-*"):
        sidecar.unlink()
    result = run_script("backup_db.py", ["create"], settings.data_dir, settings.port, cwd)
    assert result.returncode == 1 and "Traceback" not in result.stderr
    assert len(list(settings.backups_dir.glob("agentdesk-*.db"))) == 1  # only the fixture's backup


def test_tst_scripts_refuse_invalid_environment(tmp_path):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    for script, args in (("backup_db.py", ["list"]), ("restore_db.py", ["list"])):
        result = run_script(script, args, tmp_path / "d", 80, cwd)
        assert result.returncode == 1 and "AGENTDESK_PORT" in result.stderr and "Traceback" not in result.stderr
        result = run_script(script, args, tmp_path / "d", 8765, cwd, extra_env={"AGENTDESK_HOST": "0.0.0.0"})
        assert result.returncode == 1 and "AGENTDESK_HOST" in result.stderr


def test_tst_scripts_reject_unknown_commands(world):
    settings, _, cwd = world
    for script, args in (("backup_db.py", ["delete"]), ("backup_db.py", []), ("restore_db.py", []),
                         ("restore_db.py", ["restore"]), ("restore_db.py", ["wipe"])):
        result = run_script(script, args, settings.data_dir, settings.port, cwd)
        assert result.returncode == 2, (script, args)
    assert marker(settings) == "new"


# ---------- restore_db.py ----------

def test_tst_restore_script_list_names_the_backup(world):
    settings, info, cwd = world
    result = run_script("restore_db.py", ["list"], settings.data_dir, settings.port, cwd)
    assert result.returncode == 0 and info.name in result.stdout


def test_tst_restore_script_success_keeps_previous_database(world):
    settings, info, cwd = world
    result = run_script("restore_db.py", ["restore", info.name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode == 0, result.stderr
    assert marker(settings) == "old"
    kept = list(settings.backups_dir.glob("pre-restore-*.db"))
    assert len(kept) == 1 and query(kept[0], "SELECT value FROM app_settings WHERE key='marker'") == [("new",)]
    assert kept[0].name in result.stdout
    assert info.path.is_file()


@pytest.mark.parametrize(
    "answer", ["", "\n", "restore\n", "Restore\n", "RESTORE now\n", "RESTOR\n", "yes\n", "y\n", "RESTORE RESTORE\n",
              "R E S T O R E\n", "NO\n", "\x1b\n"],
)
def test_tst_restore_prompt_cancels_on_anything_but_the_word(world, answer):
    settings, info, cwd = world
    before = sha(settings.db_path)
    result = run_script("restore_db.py", ["restore", info.name], settings.data_dir, settings.port, cwd, stdin=answer)
    assert result.returncode == 1
    assert "Cancelled" in result.stdout and "Nothing was changed" in result.stdout
    assert sha(settings.db_path) == before and marker(settings) == "new"
    assert not list(settings.backups_dir.glob("pre-restore-*"))


def test_tst_restore_prompt_eof_with_closed_stdin_cancels(world):
    settings, info, cwd = world
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(settings.data_dir), "AGENTDESK_PORT": str(settings.port)})
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "restore_db.py"), "restore", info.name],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=str(cwd), env=env, timeout=60,
    )
    assert result.returncode == 1 and "Cancelled" in result.stdout and "Traceback" not in result.stderr
    assert marker(settings) == "new"


def test_tst_restore_refused_while_port_in_use_even_with_typed_word(world):
    settings, info, cwd = world
    before = sha(settings.db_path)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", settings.port))
        listener.listen()
        result = run_script("restore_db.py", ["restore", info.name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode == 1
    assert "running" in result.stderr and str(settings.port) in result.stderr
    assert "Type RESTORE" not in result.stdout, "must refuse before asking"
    assert sha(settings.db_path) == before
    assert not list(settings.backups_dir.glob("pre-restore-*"))


@pytest.mark.parametrize(
    "name",
    ["..\\agentdesk.db", "../agentdesk.db", "C:\\Windows\\System32\\config.db", "\\\\localhost\\c$\\x.db", "//localhost/c$/x.db",
     "CON.db", "NUL.db", "x.db.", "x.db ", "sub\\x.db", "missing.db", "agentdesk.db", "..", ".", "x.db:stream"],
)
def test_tst_restore_script_refuses_bad_names_before_prompting(world, name):
    settings, _, cwd = world
    before = sha(settings.db_path)
    result = run_script("restore_db.py", ["restore", name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode in (1, 2)
    assert "Type RESTORE" not in result.stdout
    assert "Traceback" not in result.stderr
    assert sha(settings.db_path) == before and marker(settings) == "new"
    assert not list(settings.backups_dir.glob("pre-restore-*"))


def test_tst_restore_script_refuses_an_absolute_path_to_a_real_backup(world):
    settings, info, cwd = world
    result = run_script("restore_db.py", ["restore", str(info.path)], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode == 1 and marker(settings) == "new"


def test_tst_restore_script_refuses_a_damaged_backup_before_prompting(world):
    settings, _, cwd = world
    bad = settings.backups_dir / "agentdesk-20200101-000000-manual.db"
    bad.write_bytes(b"x" * 9000)
    result = run_script("restore_db.py", ["restore", bad.name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode == 1 and "integrity" in result.stderr
    assert "Type RESTORE" not in result.stdout
    assert marker(settings) == "new"


def test_tst_restore_then_start_serves_the_restored_data(world):
    settings, info, cwd = world
    run_script("restore_db.py", ["restore", info.name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    create_app(settings)
    assert marker(settings) == "old"


def test_tst_restore_works_when_there_is_no_current_database(world):
    settings, info, cwd = world
    settings.db_path.unlink()
    for sidecar in settings.data_dir.glob("agentdesk.db-*"):
        sidecar.unlink()
    result = run_script("restore_db.py", ["restore", info.name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode == 0, result.stderr
    assert marker(settings) == "old"


def test_tst_restore_script_leaves_leftover_sidecars_with_the_old_database(world):
    settings, info, cwd = world
    settings.db_path.with_name("agentdesk.db-wal").write_bytes(b"stale")
    result = run_script("restore_db.py", ["restore", info.name], settings.data_dir, settings.port, cwd, stdin="RESTORE\n")
    assert result.returncode == 0, result.stderr
    assert not settings.db_path.with_name("agentdesk.db-wal").exists()
    assert list(settings.backups_dir.glob("pre-restore-*.db-wal"))
    create_app(settings)  # the restored database opens cleanly
