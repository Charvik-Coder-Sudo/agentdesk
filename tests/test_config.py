"""NFR-001: loopback-only settings with clear errors."""

import os
import subprocess
import sys

import pytest

from app.core.config import REPO_ROOT, ConfigError, Settings, load_settings


def test_defaults():
    settings = load_settings({})
    assert settings.host == "127.0.0.1"
    assert settings.port == 8765
    assert settings.data_dir == REPO_ROOT / "data"
    assert settings.log_level == "INFO"
    assert settings.db_path == REPO_ROOT / "data" / "agentdesk.db"


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1"])
def test_loopback_hosts_accepted(host):
    assert load_settings({"AGENTDESK_HOST": host}).host == host


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.10", "example.com", "::", ""])
def test_non_loopback_host_refused(host):
    with pytest.raises(ConfigError, match="AGENTDESK_HOST"):
        load_settings({"AGENTDESK_HOST": host})


@pytest.mark.parametrize("port", ["1024", "8765", "65535"])
def test_valid_ports_accepted(port):
    assert load_settings({"AGENTDESK_PORT": port}).port == int(port)


@pytest.mark.parametrize("port", ["1023", "65536", "0", "-1", "abc", "80.5", ""])
def test_invalid_port_refused(port):
    with pytest.raises(ConfigError, match="AGENTDESK_PORT"):
        load_settings({"AGENTDESK_PORT": port})


def test_invalid_log_level_refused():
    with pytest.raises(ConfigError, match="AGENTDESK_LOG_LEVEL"):
        load_settings({"AGENTDESK_LOG_LEVEL": "LOUD"})


def test_data_dir_setting(tmp_path):
    assert load_settings({"AGENTDESK_DATA_DIR": str(tmp_path)}).data_dir == tmp_path.resolve()


def test_base_url_for_ipv6():
    assert Settings(host="::1").base_url == "http://[::1]:8765"


def _run_app(env_changes, tmp_path):
    env = dict(os.environ, AGENTDESK_DATA_DIR=str(tmp_path / "data"), **env_changes)
    return subprocess.run(
        [sys.executable, "-m", "app"], cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=60
    )


def test_server_refuses_to_start_on_non_loopback_host(tmp_path):
    result = _run_app({"AGENTDESK_HOST": "0.0.0.0"}, tmp_path)
    assert result.returncode != 0
    assert "AGENTDESK_HOST" in result.stderr
    assert not (tmp_path / "data").exists()  # stopped before creating anything


def test_server_refuses_to_start_on_invalid_port(tmp_path):
    result = _run_app({"AGENTDESK_PORT": "99999"}, tmp_path)
    assert result.returncode != 0
    assert "AGENTDESK_PORT" in result.stderr
    assert not (tmp_path / "data").exists()
