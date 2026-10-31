"""One AgentDesk per data folder (SEC-002).

The running server holds an exclusive lock on data/agentdesk.lock for its whole lifetime.
scripts/restore_db.py takes the same lock before it asks for confirmation and keeps it until the
database has been replaced, so a restore can never run while AgentDesk uses the database, and a
second AgentDesk on the same data folder (on any port) is refused. The operating system releases
the lock when the process ends, even after a crash. The lock file itself stays in place.
"""

import os
from pathlib import Path

try:
    import msvcrt  # Windows
except ImportError:  # pragma: no cover - AgentDesk runs on Windows; this keeps other systems working
    msvcrt = None
    import fcntl

LOCK_FILE_NAME = "agentdesk.lock"


class LockHeld(Exception):
    """Another process (a running AgentDesk or a restore) holds the data folder's lock."""


class DataFolderLock:
    def __init__(self, data_dir: Path):
        self.path = Path(data_dir) / LOCK_FILE_NAME
        self._fd = None

    def acquire(self) -> None:
        """Take the lock without waiting. Raises LockHeld if another process holds it, or OSError if
        the lock file cannot be opened."""
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            if msvcrt:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)  # lock the first byte of the file
            else:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise LockHeld(str(self.path)) from exc
        self._fd = fd

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            if msvcrt:
                os.lseek(self._fd, 0, os.SEEK_SET)
                msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass  # closing the file below releases the lock anyway
        finally:
            os.close(self._fd)
            self._fd = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc_info):
        self.release()
