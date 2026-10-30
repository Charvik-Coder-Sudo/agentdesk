"""Settings read from environment variables, with safe defaults.

AGENTDESK_HOST       loopback address to listen on: 127.0.0.1 (default), localhost or ::1
AGENTDESK_PORT       port number, 1024-65535 (default 8765)
AGENTDESK_DATA_DIR   folder for the database, backups and logs (default <repo>/data)
AGENTDESK_LOG_LEVEL  DEBUG, INFO (default), WARNING or ERROR
"""

import os
import socket
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_HOSTS = ("127.0.0.1", "localhost", "::1")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
DEFAULT_PORT = 8765


class ConfigError(Exception):
    """A setting has an invalid value. The message says how to fix it."""


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = DEFAULT_PORT
    data_dir: Path = REPO_ROOT / "data"
    log_level: str = "INFO"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "agentdesk.db"

    @property
    def backups_dir(self) -> Path:
        return self.data_dir / "backups"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def base_url(self) -> str:
        host = f"[{self.host}]" if self.host == "::1" else self.host
        return f"http://{host}:{self.port}"


def load_settings(env=None) -> Settings:
    """Read and validate settings. Raises ConfigError with a clear message."""
    env = os.environ if env is None else env

    host = env.get("AGENTDESK_HOST", "127.0.0.1").strip()
    if host not in ALLOWED_HOSTS:
        raise ConfigError(
            f"AGENTDESK_HOST is set to {host!r}, but AgentDesk only listens on this computer. "
            "Use 127.0.0.1, localhost or ::1, or remove the AGENTDESK_HOST setting."
        )

    port_text = env.get("AGENTDESK_PORT", str(DEFAULT_PORT)).strip()
    try:
        port = int(port_text)
    except ValueError:
        port = -1
    if not 1024 <= port <= 65535:
        raise ConfigError(
            f"AGENTDESK_PORT is set to {port_text!r}. Use a whole number from 1024 to 65535 "
            f"(the default is {DEFAULT_PORT}), or remove the AGENTDESK_PORT setting."
        )

    data_dir_text = env.get("AGENTDESK_DATA_DIR", "").strip()
    data_dir = Path(data_dir_text).resolve() if data_dir_text else REPO_ROOT / "data"

    log_level = env.get("AGENTDESK_LOG_LEVEL", "INFO").strip().upper()
    if log_level not in LOG_LEVELS:
        raise ConfigError(
            f"AGENTDESK_LOG_LEVEL is set to {log_level!r}. Use one of: {', '.join(LOG_LEVELS)}."
        )

    return Settings(host=host, port=port, data_dir=data_dir, log_level=log_level)


def is_port_free(host: str, port: int) -> bool:
    """True if nothing is listening on host:port (tested by binding briefly)."""
    family = socket.AF_INET6 if host == "::1" else socket.AF_INET
    address = "127.0.0.1" if host == "localhost" else host
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((address, port))
        except OSError:
            return False
    return True
