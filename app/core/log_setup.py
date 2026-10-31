"""Logging to the console and to a rotating file data/logs/agentdesk.log.

AgentDesk never logs request bodies, tokens or other secrets. Lines that any web page can cause
(refused requests, uvicorn's warnings about upgrade or invalid requests) are limited to 20 a
minute, so they cannot flood the log and push out the history (SEC-001).
"""

import logging
import threading
import time
from logging.handlers import RotatingFileHandler

from app.core.config import Settings

LOG_FILE_NAME = "agentdesk.log"
MAX_BYTES = 1_000_000  # rotate at 1 MB
BACKUP_COUNT = 5  # keep agentdesk.log.1 ... agentdesk.log.5
LINES_PER_MINUTE = 20

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_installed_handlers: list[logging.Handler] = []
logger = logging.getLogger(__name__)


class LogRateLimiter:
    """Allows at most `limit` lines of one kind per `window` seconds.

    allow() counts one line and returns (log_it, note). note is an extra summary line to log first,
    or None: when the limit is reached ("further ... are not logged") and, in the next window, how many
    lines were left out.
    """

    def __init__(self, what: str, limit: int = LINES_PER_MINUTE, window: float = 60.0, clock=time.monotonic):
        self.what = what
        self.limit = limit
        self.window = window
        self._clock = clock
        self._lock = threading.Lock()
        self._start = None
        self._count = 0
        self._suppressed = 0

    def allow(self) -> tuple[bool, str | None]:
        now = self._clock()
        with self._lock:
            note = None
            if self._start is None or now - self._start >= self.window:
                if self._suppressed:
                    note = (f"{self._suppressed} more {self.what} were not logged in the last minute "
                            f"(at most {self.limit} are logged per minute).")
                self._start, self._count, self._suppressed = now, 0, 0
            self._count += 1
            if self._count <= self.limit:
                return True, note
            self._suppressed += 1
            if self._suppressed == 1:
                note = f"More than {self.limit} {self.what} within a minute: further ones are not logged this minute."
            return False, note


class UvicornRequestWarningFilter(logging.Filter):
    """Limits uvicorn's per-request warnings. uvicorn 0.54.0 (h11) logs these for every upgrade request
    (for example a WebSocket attempt) and every malformed request, which any web page or local program
    can send in bulk."""

    MESSAGES = (
        "Unsupported upgrade request.",
        "No supported WebSocket library detected.",
        "Invalid HTTP request received.",
    )

    def __init__(self):
        super().__init__()
        self.limiter = LogRateLimiter("uvicorn request warnings")

    def filter(self, record: logging.LogRecord) -> bool:
        if not str(record.msg).startswith(self.MESSAGES):
            return True
        log_it, note = self.limiter.allow()
        if note:
            logger.warning(note)  # a different logger, so this filter does not see the note
        return log_it


_uvicorn_filter = UvicornRequestWarningFilter()


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
    uvicorn_logger = logging.getLogger("uvicorn.error")
    if _uvicorn_filter not in uvicorn_logger.filters:
        uvicorn_logger.addFilter(_uvicorn_filter)
    return list(_installed_handlers)


def close_logging() -> None:
    """Remove and close the handlers installed by setup_logging."""
    root = logging.getLogger()
    while _installed_handlers:
        handler = _installed_handlers.pop()
        root.removeHandler(handler)
        handler.close()
