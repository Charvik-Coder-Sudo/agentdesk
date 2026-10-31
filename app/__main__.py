"""Start AgentDesk: python -m app [--open]

Validates the settings, runs the startup sequence and serves the dashboard on the configured
loopback address (default http://127.0.0.1:8765). Press Ctrl+C to stop. While it runs it holds the
data folder's lock (data/agentdesk.lock), so a restore or a second AgentDesk on the same data
folder is refused.
"""

import argparse
import logging
import sys
import threading
import time
import urllib.request
import webbrowser

import uvicorn

from app.core.config import ConfigError, is_port_free, load_settings
from app.core.instance_lock import DataFolderLock, LockHeld
from app.core.log_setup import setup_logging
from app.main import StartupError, create_app, create_data_folders

logger = logging.getLogger("app")


def _open_browser_when_ready(url: str) -> None:
    """Wait until the health endpoint answers, then open the dashboard once."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never use a proxy for localhost
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            with opener.open(url + "api/v1/health", timeout=2) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except OSError:
            pass
        time.sleep(0.3)
    logger.warning("The server did not answer within 20 seconds. Open %s in your browser yourself.", url)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app", description="Start the AgentDesk server.")
    parser.add_argument("--open", action="store_true", help="open the dashboard in the default browser")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"AgentDesk cannot start: {exc}", file=sys.stderr)
        return 1

    url = settings.base_url + "/"
    if not is_port_free(settings.host, settings.port):
        print(
            f"AgentDesk cannot start: port {settings.port} is already in use.\n"
            f"AgentDesk may already be running: open {url} in your browser.\n"
            "Otherwise close the program using that port, or choose another port with "
            "set AGENTDESK_PORT=8766 before starting.",
            file=sys.stderr,
        )
        return 1

    # The data folders come first: the log file and the lock file live in them.
    try:
        create_data_folders(settings)
    except StartupError as exc:
        print(f"AgentDesk cannot start: {exc}", file=sys.stderr)
        return 1

    lock = DataFolderLock(settings.data_dir)
    try:
        lock.acquire()
    except LockHeld:
        print(
            f"AgentDesk cannot start: another AgentDesk, or a restore, is already using the data folder "
            f"{settings.data_dir}.\n"
            "Only one AgentDesk can use a data folder at a time. If AgentDesk is already running, use that one "
            "(its window shows the address). Otherwise wait until the restore has finished and try again.",
            file=sys.stderr,
        )
        return 1
    except OSError as exc:
        print(
            f"AgentDesk cannot start: it could not create its lock file {lock.path} ({exc.strerror or exc}). "
            "Make sure the data folder can be written to.",
            file=sys.stderr,
        )
        return 1

    try:
        return _serve(settings, url, args.open)
    finally:
        lock.release()


def _serve(settings, url: str, open_browser: bool) -> int:
    """Set up logging, run the startup sequence and serve until Ctrl+C. The caller holds the lock."""
    try:
        setup_logging(settings)
    except OSError as exc:
        print(
            f"AgentDesk cannot start: it could not open its log file in {settings.logs_dir} "
            f"({exc.strerror or exc}). Make sure that folder can be written to.",
            file=sys.stderr,
        )
        return 1
    try:
        app = create_app(settings)
    except StartupError as exc:
        logger.error("AgentDesk did not start.\n%s", exc)
        return 1

    print(f"AgentDesk is starting at {url}  (press Ctrl+C to stop)", flush=True)
    if open_browser:
        threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()
    try:
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            log_config=None,  # use AgentDesk's logging setup
            access_log=False,  # health checks every 10 s would flood the log
            server_header=False,
            proxy_headers=False,  # there is no proxy in front of AgentDesk
        )
    except KeyboardInterrupt:
        pass
    logger.info("AgentDesk stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
