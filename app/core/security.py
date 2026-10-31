"""Security middleware for every request.

1. Host allowlist: only 127.0.0.1:<port>, localhost:<port> and [::1]:<port> (blocks DNS rebinding).
2. CSRF protection for every method except GET, HEAD and OPTIONS: the Origin header must be absent
   or our own address, the X-AgentDesk-CSRF header must hold this server run's token, and the body
   must be JSON.
3. Security headers (Content-Security-Policy and friends) on every response; no CORS headers.
   A HEAD answer never has a body.
4. Unhandled errors become a JSON 500 response without a stack trace; details go to the log.
5. WebSocket connections are refused: AgentDesk has no WebSocket endpoint.
Request text in log lines is escaped and shortened, and refusal lines are limited to 20 a minute,
so a web page cannot forge or flood log lines (SEC-001).
"""

import json
import logging
import secrets

from starlette.datastructures import Headers

from app.core.log_setup import LogRateLimiter

logger = logging.getLogger(__name__)

CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
PERMISSIONS_POLICY = (
    "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
)
SECURITY_HEADERS = {
    "content-security-policy": CSP,
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "permissions-policy": PERMISSIONS_POLICY,
}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}  # every other method is checked as state-changing
CSRF_HEADER = "x-agentdesk-csrf"
LOGGED_PATH_LENGTH = 200


def new_csrf_token() -> str:
    """A new random token (32 random bytes, URL-safe text). Created at every server start."""
    return secrets.token_urlsafe(32)


def allowed_hosts(port: int) -> set[str]:
    return {f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}"}


def error_body(code: str, message: str) -> bytes:
    """The JSON body used for every AgentDesk error response."""
    return json.dumps({"error": {"code": code, "message": message}}).encode("utf-8")


def for_log(text: str, limit: int = LOGGED_PATH_LENGTH) -> str:
    """Request text for a log line: at most `limit` characters, escaped like repr(), so CR, LF and
    other control characters are shown as \\r, \\n, ... and can never start a forged log line."""
    shown = repr(text[:limit])
    return shown if len(text) <= limit else f"{shown}... ({len(text)} characters)"


def _method_for_log(method: str) -> str:
    return method if method.isascii() and method.isalpha() and len(method) <= 20 else for_log(method, 20)


def _is_api_path(path: str) -> bool:
    return path == "/api" or path.startswith("/api/")


def _with_security_headers(raw_headers, is_api: bool) -> list[tuple[bytes, bytes]]:
    """Return the response headers with the security headers added (replacing duplicates)."""
    extra = dict(SECURITY_HEADERS)
    # API answers must never be cached. Pages and static files are revalidated on each load,
    # so a browser always picks up a newer AgentDesk version.
    extra["cache-control"] = "no-store" if is_api else "no-cache"
    names = {name.encode("latin-1") for name in extra}
    headers = [(name, value) for name, value in raw_headers if name.lower() not in names]
    headers.extend((name.encode("latin-1"), value.encode("latin-1")) for name, value in extra.items())
    return headers


class SecurityMiddleware:
    """Pure ASGI middleware (see the module docstring)."""

    def __init__(self, app, port: int, csrf_token: str):
        self.app = app
        self.port = port
        self.allowed_hosts = allowed_hosts(port)
        self.csrf_token = csrf_token.encode("latin-1")
        self._refusal_log = LogRateLimiter("refused requests")

    def _log_refusal(self, message: str, *args) -> None:
        log_it, note = self._refusal_log.allow()
        if note:
            logger.warning(note)
        if log_it:
            logger.warning(message, *args)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            await self._refuse_websocket(scope, receive, send)
            return
        if scope["type"] != "http":  # "lifespan": the server's startup and shutdown events
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        method = scope["method"]
        is_api = _is_api_path(path)
        headers = Headers(scope=scope)

        host = headers.get("host", "").lower()
        if host not in self.allowed_hosts:
            self._log_refusal("Refused a request with a foreign Host header %r", host[:100])
            await self._send_error(
                send, 400, "host_not_allowed",
                f"This address is not allowed. Open AgentDesk at http://127.0.0.1:{self.port}/ instead.",
                is_api,
            )
            return

        if method not in SAFE_METHODS:
            refusal = self._check_state_changing(headers, host)
            if refusal:
                status, code, message = refusal
                self._log_refusal("Refused %s %s: %s", _method_for_log(method), for_log(path), code)
                await self._send_error(send, status, code, message, is_api)
                return

        response_started = False

        async def send_with_headers(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                message["headers"] = _with_security_headers(message.get("headers", []), is_api)
            elif message["type"] == "http.response.body" and method == "HEAD":
                message = {**message, "body": b""}  # a HEAD answer has headers only
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        except Exception:
            # Full details (including the stack trace) go to the log file only.
            logger.exception("Unhandled error while handling %s %s", _method_for_log(method), for_log(path))
            if response_started:
                raise
            await self._send_error(
                send, 500, "internal_error",
                "Something went wrong inside AgentDesk. Try again; if it keeps happening, "
                "look at the log file in the data\\logs folder.",
                is_api,
            )

    async def _refuse_websocket(self, scope, receive, send):
        """Close a WebSocket connection before it reaches the application (the server answers 403)."""
        self._log_refusal("Refused a WebSocket connection to %s", for_log(scope.get("path", "")))
        message = await receive()
        if message["type"] == "websocket.connect":
            await send({"type": "websocket.close", "code": 1008})

    def _check_state_changing(self, headers: Headers, host: str):
        """Return (status, code, message) if the request must be refused, otherwise None."""
        origin = headers.get("origin")
        if origin is not None and origin.lower() != f"http://{host}":
            return 403, "origin_not_allowed", "Request refused: it did not come from the AgentDesk page."

        token = headers.get(CSRF_HEADER, "").encode("latin-1")
        if not secrets.compare_digest(token, self.csrf_token):
            return (
                403, "csrf_token_invalid",
                "Request refused: the security token is missing or out of date. Reload the page and try again.",
            )

        content_type = headers.get("content-type", "").split(";")[0].strip().lower()
        if content_type != "application/json":
            return 415, "unsupported_media_type", "Request refused: the data must be sent as JSON."
        return None

    async def _send_error(self, send, status: int, code: str, message: str, is_api: bool):
        body = error_body(code, message)
        raw_headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("latin-1")),
        ]
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": _with_security_headers(raw_headers, is_api),
        })
        await send({"type": "http.response.body", "body": body})
