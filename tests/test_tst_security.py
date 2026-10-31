"""Tester-agent tests (T-20261030-002-TST): security middleware edge cases.

NFR-001..NFR-006. The requests are sent straight to the ASGI application so that header values
that an HTTP client library would normalise or refuse (missing Host, bytes above 127, very long
values, unusual path spellings) reach the middleware exactly as written.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import BASE_URL

BACKUPS = "/api/v1/system/backups"
CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
GOOD_HOST = "127.0.0.1:8765"


def asgi(app, method, path, headers=(), body=b""):
    """Send one request to the ASGI app. headers: list of (name, value) as str or bytes."""
    raw = []
    for name, value in headers:
        raw.append((name.lower().encode("latin-1"), value if isinstance(value, bytes) else value.encode("latin-1")))
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method,
        "scheme": "http", "path": path, "raw_path": path.encode("utf-8"), "query_string": b"",
        "root_path": "", "headers": raw, "client": ("127.0.0.1", 50000), "server": ("127.0.0.1", 8765),
    }
    sent = []
    state = {"done": False}

    async def receive():
        if not state["done"]:
            state["done"] = True
            return {"type": "http.request", "body": body, "more_body": False}
        await asyncio.Event().wait()  # like a live connection: never "disconnects" while answering

    async def send(message):
        sent.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(m for m in sent if m["type"] == "http.response.start")
    payload = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    response_headers = {}
    for name, value in start["headers"]:
        response_headers[name.decode("latin-1").lower()] = value.decode("latin-1")
    return start["status"], response_headers, payload


def token_of(app):
    return app.state.csrf_token


def good(app, extra=(), method="POST", path=BACKUPS, host=GOOD_HOST, content_type="application/json", token=None):
    headers = [("host", host)]
    if content_type is not None:
        headers.append(("content-type", content_type))
    headers.append(("x-agentdesk-csrf", token_of(app) if token is None else token))
    headers.extend(extra)
    return asgi(app, method, path, headers, b"{}")


# ---------- Host header (NFR-002) ----------

HOST_REFUSED = [
    "localhost.:8765",            # trailing dot (FQDN form)
    "127.0.0.1",                  # no port
    "[::1]",                      # IPv6 without port
    "[::1]:9999",                 # wrong port
    "[0:0:0:0:0:0:0:1]:8765",     # long IPv6 spelling is not on the allowlist
    "[::1",                       # malformed bracket
    "::1:8765",                   # IPv6 without brackets
    "user@127.0.0.1:8765",        # userinfo
    "127.0.0.1:8765@evil.example",
    "127.0.0.1:8765, evil.example",
    "127.0.0.1:08765",            # leading zero
    "127.0.0.1:8765.",
    " 127.0.0.1:8765",
    "127.0.0.1:8765 ",
    "127.1:8765",
    "2130706433:8765",            # decimal spelling of 127.0.0.1
    "localhost:8765:8765",
    "a" * 10000,                  # very long value
    "127.0.0.1:" + "9" * 5000,
    "",
]


@pytest.mark.parametrize("host", HOST_REFUSED)
@pytest.mark.parametrize("path", ["/", "/api/v1/health", "/api/v1/session", "/static/js/app.js"])
def test_tst_host_variants_refused_everywhere(app, host, path):
    status, headers, body = asgi(app, "GET", path, [("host", host)])
    assert status == 400
    assert b"host_not_allowed" in body
    assert headers["content-security-policy"] == CSP
    assert b"csrf_token" not in body.lower() or b"csrf_token_invalid" in body  # the token is never leaked
    assert b"Traceback" not in body


def test_tst_missing_host_header_refused(app):
    status, headers, body = asgi(app, "GET", "/api/v1/health", [])
    assert status == 400 and b"host_not_allowed" in body
    assert headers["content-security-policy"] == CSP


def test_tst_non_ascii_host_bytes_refused_not_500(app):
    status, _, body = asgi(app, "GET", "/api/v1/health", [("host", b"127.0.0.1:\xff\xfe")])
    assert status == 400 and b"host_not_allowed" in body


@pytest.mark.parametrize(
    "host", ["127.0.0.1:8765", "localhost:8765", "LocalHost:8765", "LOCALHOST:8765", "[::1]:8765"]
)
def test_tst_allowed_host_spellings_accepted(app, host):
    status, _, _ = asgi(app, "GET", "/api/v1/health", [("host", host)])
    assert status == 200


def test_tst_session_token_not_served_to_foreign_host(app):
    status, _, body = asgi(app, "GET", "/api/v1/session", [("host", "evil.example")])
    assert status == 400
    assert token_of(app).encode() not in body


def test_tst_two_host_headers_do_not_crash_and_never_serve_evil(app):
    status, _, _ = asgi(app, "GET", "/api/v1/health", [("host", GOOD_HOST), ("host", "evil.example")])
    assert status in (200, 400)
    status, _, _ = asgi(app, "GET", "/api/v1/health", [("host", "evil.example"), ("host", GOOD_HOST)])
    assert status == 400, "the first Host header must decide"


def test_tst_wrong_host_refused_for_state_changing_requests_too(app):
    status, _, body = good(app, host="evil.example")
    assert status == 400 and b"host_not_allowed" in body


# ---------- CSRF token (NFR-003) ----------

@pytest.mark.parametrize("bad", ["", " ", "x", "TOKEN", "../", "\u00e9\u00e9"])
def test_tst_wrong_or_empty_token_refused(app, bad):
    status, _, body = good(app, token=bad)
    assert status == 403 and b"csrf_token_invalid" in body


def test_tst_token_variations_refused(app):
    token = token_of(app)
    for bad in (token + "x", token[:-1], token.upper(), token.lower() if token.lower() != token else token + "0",
                " " + token, token + " "):
        status, _, _ = good(app, token=bad)
        assert status == 403, bad


def test_tst_token_with_high_bytes_refused_not_500(app):
    status, _, body = asgi(
        app, "POST", BACKUPS,
        [("host", GOOD_HOST), ("content-type", "application/json"), ("x-agentdesk-csrf", b"\xff\xfe\x80")], b"{}",
    )
    assert status == 403 and b"csrf_token_invalid" in body


def test_tst_missing_token_header_refused(app):
    status, _, body = asgi(app, "POST", BACKUPS, [("host", GOOD_HOST), ("content-type", "application/json")], b"{}")
    assert status == 403 and b"csrf_token_invalid" in body


def test_tst_token_from_previous_server_run_refused_by_new_instance(settings):
    first = create_app(settings)
    second = create_app(settings)  # a restart = a new application instance
    old_token = first.state.csrf_token
    status, _, _ = good(second, token=old_token)
    assert status == 403
    status, _, _ = good(second)
    assert status == 201
    status, _, _ = good(first)  # and the old instance still accepts its own token
    assert status == 201


# ---------- Origin (NFR-003) ----------

@pytest.mark.parametrize(
    "origin",
    [
        "http://127.0.0.1:8766", "https://127.0.0.1:8765", "null", "", "http://127.0.0.1",
        "http://127.0.0.1:8765/", "http://127.0.0.1:8765@evil.example", "http://evil.example",
        "http://localhost:8765",  # does not match the Host 127.0.0.1:8765 of this request
        "file://", "http://[::1]:8765", "http://127.0.0.1:8765 ",
    ],
)
def test_tst_foreign_origin_refused(app, origin):
    status, _, body = good(app, extra=[("origin", origin)])
    assert status == 403 and b"origin_not_allowed" in body


@pytest.mark.parametrize("origin", ["http://127.0.0.1:8765", "HTTP://127.0.0.1:8765"])
def test_tst_own_origin_accepted(app, origin):
    status, _, _ = good(app, extra=[("origin", origin)])
    assert status == 201


def test_tst_origin_matches_the_host_used(app):
    status, _, _ = good(app, host="localhost:8765", extra=[("origin", "http://localhost:8765")])
    assert status == 201
    status, _, _ = good(app, host="[::1]:8765", extra=[("origin", "http://[::1]:8765")])
    assert status == 201


def test_tst_origin_checked_before_token(app):
    status, _, body = good(app, token="wrong", extra=[("origin", "http://evil.example")])
    assert status == 403 and b"origin_not_allowed" in body


# ---------- Content type (NFR-003) ----------

@pytest.mark.parametrize(
    "content_type",
    ["application/json; charset=utf-8", "application/json;charset=UTF-8", "APPLICATION/JSON", " application/json "],
)
def test_tst_json_content_type_variants_accepted(app, content_type):
    status, _, _ = good(app, content_type=content_type)
    assert status == 201


@pytest.mark.parametrize(
    "content_type",
    [None, "", "text/plain", "application/x-www-form-urlencoded", "multipart/form-data; boundary=x",
     "application/jsonp", "application/json-patch+json", "text/json", "application/xml"],
)
def test_tst_other_content_types_refused(app, content_type):
    status, _, body = good(app, content_type=content_type)
    assert status == 415 and b"unsupported_media_type" in body


def test_tst_no_backup_file_when_refused(app, settings):
    good(app, content_type="text/plain")
    good(app, token="wrong")
    good(app, extra=[("origin", "null")])
    assert list(settings.backups_dir.glob("agentdesk-*.db")) == []


# ---------- Methods ----------

@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_tst_state_changing_methods_refused_without_token(app, method):
    status, _, body = asgi(app, method, BACKUPS, [("host", GOOD_HOST), ("content-type", "application/json")], b"{}")
    assert status == 403 and b"csrf_token_invalid" in body


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_tst_state_changing_methods_with_token_reach_the_router_as_405(app, method):
    status, headers, body = good(app, method=method)
    assert status == 405 and b"method_not_allowed" in body
    assert headers["content-security-policy"] == CSP


@pytest.mark.parametrize("path", ["/", "/api/v1/nope", "/static/js/app.js"])
@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
def test_tst_state_changing_requests_to_any_path_need_token(app, path, method):
    status, _, _ = asgi(app, method, path, [("host", GOOD_HOST), ("content-type", "application/json")], b"{}")
    assert status == 403


@pytest.mark.parametrize("path", ["/api/v1/health", BACKUPS, "/", "/static/js/app.js", "/api/v1/nope"])
def test_tst_head_and_options_are_safe_and_carry_headers(app, path):
    for method in ("HEAD", "OPTIONS"):
        status, headers, body = asgi(app, method, path, [("host", GOOD_HOST), ("origin", "http://evil.example")])
        assert status in (200, 404, 405), (method, path, status)
        assert headers["content-security-policy"] == CSP
        assert headers["x-content-type-options"] == "nosniff"
        assert not any(name.startswith("access-control-") for name in headers)
        # (The HTTP server, not the application, drops the body of a HEAD answer: see the server-process tests.)


def test_tst_head_never_creates_a_backup(app, settings):
    asgi(app, "HEAD", BACKUPS, [("host", GOOD_HOST)])
    asgi(app, "OPTIONS", BACKUPS, [("host", GOOD_HOST)])
    assert list(settings.backups_dir.glob("agentdesk-*.db")) == []


def test_tst_get_requests_change_nothing(app, settings):
    for path in ("/api/v1/health", "/api/v1/session", "/api/v1/system", BACKUPS, "/"):
        asgi(app, "GET", path, [("host", GOOD_HOST)])
    assert list(settings.backups_dir.glob("agentdesk-*.db")) == []


# ---------- Security headers on every kind of response ----------

def _expect_headers(headers, api):
    assert headers["content-security-policy"] == CSP
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["referrer-policy"] == "no-referrer"
    assert headers["x-frame-options"] == "DENY"
    if api:
        assert headers["cache-control"] == "no-store"
    assert not any(name.startswith("access-control-") for name in headers)


def test_tst_headers_on_every_response_kind(app):
    cases = [
        ("GET", "/api/v1/health", [("host", GOOD_HOST)], 200, True),
        ("GET", "/api/v1/nope", [("host", GOOD_HOST)], 404, True),
        ("GET", "/api/v1/health/extra", [("host", GOOD_HOST)], 404, True),
        ("GET", "/nope", [("host", GOOD_HOST)], 404, False),
        ("GET", "/static/nope.js", [("host", GOOD_HOST)], 404, False),
        ("GET", "/", [("host", GOOD_HOST)], 200, False),
        ("POST", "/api/v1/health", [("host", GOOD_HOST), ("content-type", "application/json"),
                                    ("x-agentdesk-csrf", token_of(app))], 405, True),
        ("GET", "/api/v1/health", [("host", "evil.example")], 400, True),
        ("POST", BACKUPS, [("host", GOOD_HOST)], 403, True),
        ("POST", BACKUPS, [("host", GOOD_HOST), ("x-agentdesk-csrf", token_of(app))], 415, True),
        ("GET", "/api/docs", [("host", GOOD_HOST)], 404, True),
        ("GET", "/docs", [("host", GOOD_HOST)], 404, False),
        ("GET", "/openapi.json", [("host", GOOD_HOST)], 404, False),
    ]
    for method, path, headers, expected, api in cases:
        status, response_headers, body = asgi(app, method, path, headers, b"{}")
        assert status == expected, (method, path, status)
        _expect_headers(response_headers, api)
        if expected >= 400:
            assert response_headers["content-type"].startswith("application/json"), (method, path)
            assert b'"error"' in body and b"Traceback" not in body


def test_tst_static_and_pages_are_revalidated(app):
    for path in ("/", "/static/js/app.js", "/static/css/app.css"):
        _, headers, _ = asgi(app, "GET", path, [("host", GOOD_HOST)])
        assert headers["cache-control"] == "no-cache"


def test_tst_unhandled_error_variants_have_no_trace_or_path(settings):
    app = create_app(settings)

    def boom_value():
        raise ValueError("C:\\Users\\secret\\file.py line 3 token=abc123")

    def boom_zero():
        return 1 / 0

    app.add_api_route("/api/v1/boom-value", boom_value)
    app.add_api_route("/api/v1/boom-zero", boom_zero)
    app.add_api_route("/boom-page", boom_value)
    for path in ("/api/v1/boom-value", "/api/v1/boom-zero", "/boom-page"):
        status, headers, body = asgi(app, "GET", path, [("host", GOOD_HOST)])
        text = body.decode()
        assert status == 500
        assert headers["content-type"].startswith("application/json")
        assert "internal_error" in text
        for leak in ("Traceback", "File \"", ".py", "secret", "abc123", "ZeroDivision", "ValueError", "C:\\"):
            assert leak not in text, (path, leak)
        _expect_headers(headers, path.startswith("/api"))


def test_tst_404_and_405_bodies_do_not_echo_the_path(app):
    status, _, body = asgi(app, "GET", "/api/v1/<script>alert(1)</script>", [("host", GOOD_HOST)])
    assert status == 404
    assert b"script" not in body


# ---------- Static path traversal (NFR-002/NFR-006 hardening) ----------

TRAVERSAL = [
    "/static/../app/main.py",
    "/static/../../app/main.py",
    "/static/js/../../main.py",
    "/static/js/../../../app/main.py",
    "/static/..\\app\\main.py",
    "/static/..\\..\\app\\main.py",
    "/static/js\\..\\..\\main.py",
    "/static/%2e%2e/main.py",              # literal text: a decoding server would already have decoded it
    "/static/%2e%2e%2fapp%2fmain.py",
    "/static/..%5capp%5cmain.py",
    "/static//app/main.py",
    "/static/C:/Windows/win.ini",
    "/static/C:\\Windows\\win.ini",
    "/static/\\\\localhost\\c$\\Windows\\win.ini",
    "/static/js/app.js/../../../main.py",
    "/static/app.css::$DATA",
    "/static/js/app.js\x00.png",
    "/static/",
    "/static/js/",
    "/static/js",
    "/static/.",
    "/static/..",
]


@pytest.mark.parametrize("path", TRAVERSAL)
def test_tst_static_traversal_never_serves_source_code(app, path):
    status, headers, body = asgi(app, "GET", path, [("host", GOOD_HOST)])
    assert status in (404, 307, 308, 400), (path, status)
    assert b"create_app" not in body and b"SecurityMiddleware" not in body
    assert b"[fonts]" not in body.lower()  # win.ini marker
    assert headers["content-security-policy"] == CSP


def test_tst_static_directory_listing_not_offered(app):
    for path in ("/static/", "/static/js/", "/static/js/pages/"):
        status, _, body = asgi(app, "GET", path, [("host", GOOD_HOST)])
        assert status == 404
        assert b"app.js" not in body


def test_tst_static_serves_only_files_inside_static(app):
    status, _, body = asgi(app, "GET", "/static/js/pages/settings.js", [("host", GOOD_HOST)])
    assert status == 200 and b"renderSettings" in body
    for private in ("/static/../main.py", "/main.py", "/app/main.py", "/migrations/0001_foundation.sql",
                    "/static/agentdesk.db", "/data/agentdesk.db", "/pytest.ini", "/.git/config"):
        status, _, body = asgi(app, "GET", private, [("host", GOOD_HOST)])
        assert status == 404, private


# ---------- TestClient level checks that need a real client ----------

def test_tst_cookie_free_and_no_set_cookie(client):
    for path in ("/", "/api/v1/health", "/api/v1/session"):
        assert "set-cookie" not in client.get(path).headers


def test_tst_valid_flow_with_client_charset_json_content_type(client, csrf_token, settings):
    response = client.post(
        BACKUPS, content=b"{}",
        headers={"X-AgentDesk-CSRF": csrf_token, "Content-Type": "application/json; charset=utf-8", "Origin": BASE_URL},
    )
    assert response.status_code == 201
    assert response.json()["integrity"] == "ok"


def test_tst_validation_errors_do_not_echo_input(app):
    # No Phase 1 endpoint takes input, but a 422 must never echo submitted values (secrets).
    from pydantic import BaseModel

    class Body(BaseModel):
        n: int

    def takes(body: Body):
        return {"ok": True}

    app.add_api_route("/api/v1/test-takes", takes, methods=["POST"])
    with TestClient(app, base_url=BASE_URL) as client:
        token = client.get("/api/v1/session").json()["csrf_token"]
        response = client.post("/api/v1/test-takes", json={"n": "secret-value-xyz"}, headers={"X-AgentDesk-CSRF": token})
    assert response.status_code == 422
    assert "secret-value-xyz" not in response.text
    assert response.json()["error"]["code"] == "invalid_request"
