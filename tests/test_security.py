"""NFR-002 to NFR-004, NFR-006 and NFR-007: Host check, CSRF protection, headers, safe errors, logging."""

import base64
import logging

import pytest
from fastapi.testclient import TestClient

from app.core.log_setup import BACKUP_COUNT, MAX_BYTES, close_logging, setup_logging
from app.core.security import CSP
from app.main import create_app
from tests.conftest import BASE_URL

BACKUPS = "/api/v1/system/backups"
EXPECTED_CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"


def backup_files(settings):
    return sorted(p.name for p in settings.backups_dir.glob("agentdesk-*.db"))


# ---------- Host allowlist (NFR-002) ----------

@pytest.mark.parametrize("path", ["/", "/api/v1/health", "/static/js/app.js"])
@pytest.mark.parametrize(
    "host", ["evil.example", "evil.example:8765", "127.0.0.1:9999", "127.0.0.1", "0.0.0.0:8765"]
)
def test_foreign_host_refused(client, path, host):
    response = client.get(path, headers={"Host": host})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "host_not_allowed"


@pytest.mark.parametrize("host", ["127.0.0.1:8765", "localhost:8765", "[::1]:8765", "LOCALHOST:8765"])
def test_own_host_accepted(client, host):
    assert client.get("/api/v1/health", headers={"Host": host}).status_code == 200


# ---------- CSRF protection (NFR-003, FR-009 criterion 4) ----------

def test_post_without_token_refused_and_creates_nothing(client, settings):
    response = client.post(BACKUPS, json={})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_token_invalid"
    assert backup_files(settings) == []


def test_post_without_token_or_content_type_refused(client, settings):
    response = client.post(BACKUPS, content=b"")
    assert response.status_code == 403
    assert backup_files(settings) == []


def test_post_with_wrong_token_refused(client, settings):
    response = client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": "wrong-token"})
    assert response.status_code == 403
    assert backup_files(settings) == []


@pytest.mark.parametrize(
    "origin", ["http://evil.example", "null", "http://localhost:8765", "https://127.0.0.1:8765"]
)
def test_post_with_foreign_origin_refused(client, settings, csrf_token, origin):
    response = client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": csrf_token, "Origin": origin})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "origin_not_allowed"
    assert backup_files(settings) == []


def test_post_with_non_json_content_type_refused(client, settings, csrf_token):
    response = client.post(
        BACKUPS,
        content=b"x=1",
        headers={"X-AgentDesk-CSRF": csrf_token, "Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media_type"
    assert backup_files(settings) == []


def test_valid_post_succeeds(client, settings, csrf_token):
    response = client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": csrf_token, "Origin": BASE_URL})
    assert response.status_code == 201
    assert len(backup_files(settings)) == 1


def test_valid_post_without_origin_succeeds(client, csrf_token):
    response = client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": csrf_token})
    assert response.status_code == 201


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_other_state_changing_methods_need_token(client, method):
    assert client.request(method, BACKUPS, json={}).status_code == 403


def test_token_is_32_random_bytes_and_new_each_start(settings):
    first = create_app(settings).state.csrf_token
    second = create_app(settings).state.csrf_token
    assert first != second
    assert len(base64.urlsafe_b64decode(first + "=")) == 32


def test_token_from_earlier_run_refused(settings):
    with TestClient(create_app(settings), base_url=BASE_URL) as old_client:
        old_token = old_client.get("/api/v1/session").json()["csrf_token"]
    with TestClient(create_app(settings), base_url=BASE_URL) as new_client:
        assert new_client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": old_token}).status_code == 403
        new_token = new_client.get("/api/v1/session").json()["csrf_token"]
        assert new_client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": new_token}).status_code == 201


def test_no_cors_headers(client, csrf_token):
    responses = [
        client.get("/api/v1/health", headers={"Origin": "http://evil.example"}),
        client.options(BACKUPS, headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"}),
        client.post(BACKUPS, json={}, headers={"X-AgentDesk-CSRF": csrf_token}),
    ]
    for response in responses:
        assert not any(name.lower().startswith("access-control-") for name in response.headers)


# ---------- Security headers (NFR-004) ----------

@pytest.mark.parametrize(
    "path", ["/", "/static/js/app.js", "/static/css/app.css", "/api/v1/health", "/api/v1/nope"]
)
def test_security_headers_present(client, path):
    response = client.get(path)
    assert CSP == EXPECTED_CSP
    assert response.headers["content-security-policy"] == EXPECTED_CSP
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-frame-options"] == "DENY"


def test_api_responses_not_cached(client):
    for path in ["/api/v1/health", "/api/v1/session", "/api/v1/system", "/api/v1/nope"]:
        assert client.get(path).headers["cache-control"] == "no-store"


def test_refused_requests_also_carry_security_headers(client):
    refused = [client.get("/api/v1/health", headers={"Host": "evil.example"}), client.post(BACKUPS, json={})]
    for response in refused:
        assert response.headers["content-security-policy"] == EXPECTED_CSP
        assert response.headers["cache-control"] == "no-store"


# ---------- JSON errors without stack traces (NFR-006) ----------

def test_unhandled_error_returns_generic_json_500(app):
    def explode():
        raise RuntimeError("secret detail C:\\internal\\module.py")

    app.add_api_route("/api/v1/test-explode", explode)
    with TestClient(app, base_url=BASE_URL) as client:
        response = client.get("/api/v1/test-explode")
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["error"]["code"] == "internal_error"
    assert "Traceback" not in response.text
    assert "secret detail" not in response.text
    assert ".py" not in response.text
    assert response.headers["content-security-policy"] == EXPECTED_CSP


def test_method_not_allowed_is_json(client, csrf_token):
    response = client.post("/api/v1/health", json={}, headers={"X-AgentDesk-CSRF": csrf_token})
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


# ---------- Log file (NFR-007) ----------

def test_log_rotation_settings_and_no_token_or_body_in_log(settings, client, csrf_token):
    handlers = setup_logging(settings)
    try:
        file_handler = [handler for handler in handlers if hasattr(handler, "maxBytes")][0]
        assert file_handler.maxBytes == MAX_BYTES == 1_000_000
        assert file_handler.backupCount == BACKUP_COUNT == 5

        client.post(BACKUPS, json={"note": "body-marker-123"}, headers={"X-AgentDesk-CSRF": csrf_token})
        client.post(BACKUPS, json={"note": "body-marker-123"}, headers={"X-AgentDesk-CSRF": "wrong"})
        logging.getLogger("test").info("a log line")
        for handler in handlers:
            handler.flush()
        log_text = (settings.logs_dir / "agentdesk.log").read_text(encoding="utf-8")
        assert "a log line" in log_text
        assert "Refused POST" in log_text  # the refusal is logged ...
        assert csrf_token not in log_text  # ... but never the token
        assert "body-marker-123" not in log_text  # ... and never the request body
    finally:
        close_logging()


def test_log_file_rotates(settings):
    setup_logging(settings)
    try:
        logger = logging.getLogger("rotation-test")
        for _ in range(1100):  # a little over 1 MB
            logger.warning("x" * 1000)
    finally:
        close_logging()
    assert (settings.logs_dir / "agentdesk.log.1").exists()
