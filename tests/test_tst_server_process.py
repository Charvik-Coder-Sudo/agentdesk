"""Tester-agent tests (T-20261030-002-TST): the real server process (uvicorn) on a free port.

FR-002, FR-003, NFR-001..NFR-004. `python -m app` runs against a temporary data folder. Requests are
written to a raw socket so that nothing normalises the path or the Host header. The server is always
stopped at the end and the port is checked to be free again.
"""

import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

from app.core.config import REPO_ROOT, is_port_free

CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def raw_request(port, text: bytes, timeout=10):
    """Send raw bytes, return (status, headers dict, body bytes)."""
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as sock:
        sock.sendall(text)
        chunks = []
        while True:
            try:
                data = sock.recv(65536)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)
    blob = b"".join(chunks)
    head, _, body = blob.partition(b"\r\n\r\n")
    lines = head.split(b"\r\n")
    status = int(lines[0].split()[1]) if lines and lines[0].startswith(b"HTTP/") else 0
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(b":")
        headers[name.decode("latin-1").lower()] = value.strip().decode("latin-1")
    return status, headers, body


def get(port, path, host=None, extra="", method="GET", version="1.1"):
    host = host or f"127.0.0.1:{port}"
    request = f"{method} {path} HTTP/{version}\r\nHost: {host}\r\n{extra}Connection: close\r\n\r\n"
    return raw_request(port, request.encode("latin-1"))


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    data = tmp_path_factory.mktemp("serverdata")
    port = free_port()
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(data), "AGENTDESK_PORT": str(port), "PYTHONUTF8": "1"})
    log = open(data / "server-output.txt", "wb")
    process = subprocess.Popen(
        [sys.executable, "-m", "app"], cwd=str(REPO_ROOT), env=env, stdout=log, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + 30
    ready = False
    while time.monotonic() < deadline and process.poll() is None:
        try:
            with opener.open(f"http://127.0.0.1:{port}/api/v1/health", timeout=2) as response:
                ready = response.status == 200
                if ready:
                    break
        except OSError:
            time.sleep(0.3)
    info = {"port": port, "data": data, "process": process, "output": data / "server-output.txt"}
    try:
        assert ready, "server did not become ready: " + (data / "server-output.txt").read_text(errors="replace")
        yield info
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        log.close()
        deadline = time.monotonic() + 10
        while not is_port_free("127.0.0.1", port) and time.monotonic() < deadline:
            time.sleep(0.2)
        assert is_port_free("127.0.0.1", port), "the test server left something listening"


def test_tst_server_listens_on_loopback_only(server):
    port = server["port"]
    addresses = {ip for ip in _local_ips() if ip != "127.0.0.1"}
    for ip in addresses:
        with socket.socket() as sock:
            sock.settimeout(2)
            assert sock.connect_ex((ip, port)) != 0, f"server answered on non-loopback address {ip}"


def _local_ips():
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return ips


def test_tst_health_over_real_http(server):
    status, headers, body = get(server["port"], "/api/v1/health")
    assert status == 200 and b'"status":"ok"' in body
    assert headers["content-security-policy"] == CSP and headers["cache-control"] == "no-store"
    assert "server" not in headers, "the Server header must not announce uvicorn"
    assert "access-control-allow-origin" not in headers


@pytest.mark.parametrize(
    "host",
    ["localhost.:{p}", "evil.example", "127.0.0.1:{q}", "127.0.0.1", "user@127.0.0.1:{p}", "[::1]", "0.0.0.0:{p}",
     "a" * 8000, "127.0.0.1:{p}.evil.example"],
)
def test_tst_foreign_host_refused_over_real_http(server, host):
    port = server["port"]
    status, headers, body = get(port, "/api/v1/health", host=host.format(p=port, q=port + 1))
    assert status == 400, (host[:40], status)
    assert b"host_not_allowed" in body
    assert headers["content-security-policy"] == CSP


@pytest.mark.parametrize("host", ["localhost:{p}", "LOCALHOST:{p}", "[::1]:{p}", "127.0.0.1:{p}"])
def test_tst_own_host_spellings_accepted_over_real_http(server, host):
    port = server["port"]
    assert get(port, "/api/v1/health", host=host.format(p=port))[0] == 200


def test_tst_http10_request_without_host_is_refused(server):
    status, _, body = raw_request(server["port"], b"GET /api/v1/health HTTP/1.0\r\n\r\n")
    assert status == 400 and b"host_not_allowed" in body


@pytest.mark.parametrize(
    "path",
    [
        "/static/..%2fapp%2fmain.py", "/static/%2e%2e/app/main.py", "/static/%2e%2e%2f%2e%2e%2fapp%2fmain.py",
        "/static/..%5capp%5cmain.py", "/static/%5c..%5capp%5cmain.py", "/static/..%252fapp%252fmain.py",
        "/static/js/..%2f..%2f..%2fapp%2fmain.py", "/static/%2e%2e%5c%2e%2e%5capp%5cmain.py",
        "/static/C:%5cWindows%5cwin.ini", "/static/%00", "/static/js/app.js%00.png", "/static/..;/app/main.py",
        "/%2e%2e/app/main.py", "/static/js/pages/..%2f..%2f..%2f..%2fpytest.ini",
    ],
)
def test_tst_encoded_path_traversal_never_serves_files_outside_static(server, path):
    status, headers, body = get(server["port"], path)
    assert status in (400, 404), (path, status)
    assert b"create_app" not in body and b"[pytest]" not in body and b"[fonts]" not in body.lower()


def test_tst_unencoded_dot_segments_are_not_a_way_out(server):
    status, _, body = raw_request(
        server["port"], f"GET /static/../app/main.py HTTP/1.1\r\nHost: 127.0.0.1:{server['port']}\r\nConnection: close\r\n\r\n".encode()
    )
    assert b"create_app" not in body


def test_tst_head_has_no_body_and_options_has_no_cors(server):
    port = server["port"]
    for path in ("/", "/api/v1/health", "/static/js/app.js"):
        status, headers, body = get(port, path, method="HEAD")
        assert body == b"" and headers["content-security-policy"] == CSP, (path, status)
    status, headers, body = get(port, "/api/v1/system/backups", method="OPTIONS", extra="Origin: http://evil.example\r\n")
    assert status == 405
    assert not any(name.startswith("access-control-") for name in headers)


def test_tst_unknown_and_error_responses_over_real_http(server):
    port = server["port"]
    for path, expected in (("/api/v1/nope", 404), ("/nope", 404), ("/static/nope.js", 404), ("/docs", 404),
                           ("/openapi.json", 404)):
        status, headers, body = get(port, path)
        assert status == expected and headers["content-security-policy"] == CSP, path
        assert b"Traceback" not in body and b'"error"' in body


def test_tst_csrf_flow_over_real_http_creates_a_backup(server):
    port = server["port"]
    status, _, body = get(port, "/api/v1/session")
    assert status == 200
    token = body.decode().split('"csrf_token":"')[1].split('"')[0]
    before = list((server["data"] / "backups").glob("agentdesk-*.db"))

    def post(extra, content_type="application/json"):
        text = (
            f"POST /api/v1/system/backups HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n{extra}"
            f"Content-Type: {content_type}\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{{}}"
        )
        return raw_request(port, text.encode())

    assert post("")[0] == 403
    assert post("X-AgentDesk-CSRF: nope\r\n")[0] == 403
    assert post(f"X-AgentDesk-CSRF: {token}\r\nOrigin: http://evil.example\r\n")[0] == 403
    assert post(f"X-AgentDesk-CSRF: {token}\r\n", content_type="text/plain")[0] == 415
    assert len(list((server["data"] / "backups").glob("agentdesk-*.db"))) == len(before)
    status, _, body = post(f"X-AgentDesk-CSRF: {token}\r\nOrigin: http://127.0.0.1:{port}\r\n")
    assert status == 201, body
    assert len(list((server["data"] / "backups").glob("agentdesk-*.db"))) == len(before) + 1


def test_tst_log_file_is_written_without_the_token(server):
    port = server["port"]
    _, _, body = get(port, "/api/v1/session")
    token = body.decode().split('"csrf_token":"')[1].split('"')[0]
    get(port, "/api/v1/health", host="evil.example")
    time.sleep(0.5)
    log_path = server["data"] / "logs" / "agentdesk.log"
    text = log_path.read_text(encoding="utf-8")
    assert "Refused a request with a foreign Host" in text
    assert token not in text
    assert token not in server["output"].read_text(errors="replace")


def test_tst_second_instance_on_the_same_port_refuses_to_start(server, tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(tmp_path / "other"), "AGENTDESK_PORT": str(server["port"])})
    result = subprocess.run(
        [sys.executable, "-m", "app"], cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 1
    assert "already in use" in result.stderr and "AGENTDESK_PORT" in result.stderr
    assert not (tmp_path / "other").exists(), "nothing may be created when the port is taken"


def test_tst_restore_refused_while_the_real_server_runs(server, tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(server["data"]), "AGENTDESK_PORT": str(server["port"])})
    backups = sorted((server["data"] / "backups").glob("agentdesk-*.db"))
    assert backups
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "restore_db.py"), "restore", backups[0].name],
        input="RESTORE\n", cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 1 and "running" in result.stderr
    assert not list((server["data"] / "backups").glob("pre-restore-*"))


@pytest.mark.parametrize(
    "env_extra,needle",
    [({"AGENTDESK_HOST": "0.0.0.0"}, "AGENTDESK_HOST"), ({"AGENTDESK_PORT": "1023"}, "AGENTDESK_PORT"),
     ({"AGENTDESK_PORT": "abc"}, "AGENTDESK_PORT"), ({"AGENTDESK_LOG_LEVEL": "LOUD"}, "AGENTDESK_LOG_LEVEL")],
)
def test_tst_bad_environment_stops_the_server_with_exit_1(tmp_path, env_extra, needle):
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(tmp_path / "d")})
    env.update(env_extra)
    result = subprocess.run([sys.executable, "-m", "app"], cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 1 and needle in result.stderr and "Traceback" not in result.stderr
    assert not (tmp_path / "d").exists()


def test_tst_damaged_database_stops_real_server_and_names_the_restore_command(tmp_path):
    data = tmp_path / "d"
    data.mkdir()
    (data / "agentdesk.db").write_bytes(b"not sqlite " * 300)
    before = (data / "agentdesk.db").read_bytes()
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(data), "AGENTDESK_PORT": str(free_port())})
    result = subprocess.run([sys.executable, "-m", "app"], cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 1
    output = result.stdout + result.stderr
    assert "restore_db.py" in output and "integrity" in output
    assert (data / "agentdesk.db").read_bytes() == before


def test_tst_ctrl_break_stops_the_server_and_frees_the_port(tmp_path):
    """FR-002 (4): Ctrl+C stops the server. Uses Ctrl+Break on a separate process group (same handler path)."""
    import signal

    port = free_port()
    data = tmp_path / "d"
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTDESK_")}
    env.update({"AGENTDESK_DATA_DIR": str(data), "AGENTDESK_PORT": str(port), "PYTHONUTF8": "1"})
    process = subprocess.Popen(
        [sys.executable, "-m", "app"], cwd=str(REPO_ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                with opener.open(f"http://127.0.0.1:{port}/api/v1/health", timeout=2):
                    break
            except OSError:
                time.sleep(0.3)
        else:
            pytest.fail("server did not start")
        process.send_signal(signal.CTRL_BREAK_EVENT)
        process.wait(timeout=20)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        process.stdout.close()
    deadline = time.monotonic() + 10
    while not is_port_free("127.0.0.1", port) and time.monotonic() < deadline:
        time.sleep(0.2)
    assert is_port_free("127.0.0.1", port)
