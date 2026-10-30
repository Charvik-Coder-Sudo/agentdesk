"""Logging to the console and to a rotating file data/logs/agentdesk.log.

AgentDesk never logs request bodies, tokens or other secrets.
"""

import logging
from logging.handlers import RotatingFileHandler

from app.core.config import Settings

LOG_FILE_NAME = "agentdesk.log"
MAX_BYTES = 1_000_000  # rotate at 1 MB
BACKUP_COUNT = 5  # keep agentdesk.log.1 ... agentdesk.log.5

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_installed_handlers: list[logging.Handler] = []


def setup_logging(settings: Settings) -> list[logging.Handler]:
    """Install the console and file handlers on the root logger (idempotent)."""
    close_logging()
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(_FORMAT)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        settings.logs_dir / LOG_FILE_NAME,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.log_level)
    for handler in (console, file_handler):
        root.addHandler(handler)
        _installed_handlers.append(handler)
    return list(_installed_handlers)


def close_logging() -> None:
    """Remove and close the handlers installed by setup_logging."""
    root = logging.getLogger()
    while _installed_handlers:
        handler = _installed_handlers.pop()
        root.removeHandler(handler)
        handler.close()
