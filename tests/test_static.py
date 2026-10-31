"""FR-005, FR-008, NFR-005 and NFR-006: the page, its modules, the system endpoint and JSON 404s."""

import re
from pathlib import Path

from app.main import STATIC_DIR

JS_MIME = ("text/javascript", "application/javascript")
IMPORT_PATTERN = re.compile(r"""(?:import|export)\s[^'"]*?from\s+['"]([^'"]+)['"]|import\s*\(\s*['"]([^'"]+)['"]""")


def index_html(client):
    response = client.get("/")
    assert response.status_code == 200
    return response.text


def test_root_serves_index_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.content == (STATIC_DIR / "index.html").read_bytes()


def test_index_has_no_inline_scripts_styles_or_handlers(client):
    html = index_html(client)
    for tag in re.findall(r"<script\b[^>]*>", html, flags=re.IGNORECASE):
        assert "src=" in tag, f"inline script found: {tag}"
    assert re.search(r"<script\b[^>]*>(?!\s*</script>)", html) is None  # no code between script tags
    assert "<style" not in html.lower()
    assert re.search(r"\sstyle\s*=", html, flags=re.IGNORECASE) is None
    assert re.search(r"\son[a-z]+\s*=", html, flags=re.IGNORECASE) is None


def test_index_has_eleven_navigation_entries(client):
    html = index_html(client)
    links = re.findall(r'<li><a href="#/([a-z]+)">([^<]+)</a></li>', html)
    assert [label for _, label in links] == [
        "Overview", "Projects", "Agents", "Activity", "File changes", "Reports",
        "Documents", "Testing", "Security", "Approvals", "Settings",
    ]
    assert 'class="skip-link"' in html
    assert 'aria-live="polite"' in html
    assert "<noscript>" in html


def _module_url(base: str, specifier: str) -> str:
    """Resolve a relative import like ./dom.js or ../api.js against a module URL."""
    parts = base.split("/")[:-1]
    for piece in specifier.split("/"):
        if piece == "..":
            parts.pop()
        elif piece != ".":
            parts.append(piece)
    return "/".join(parts)


def test_every_referenced_module_is_served_as_javascript(client):
    html = index_html(client)
    pending = re.findall(r'<script type="module" src="([^"]+)"', html)
    assert pending == ["/static/js/app.js"]
    seen = set()
    while pending:
        url = pending.pop()
        if url in seen:
            continue
        seen.add(url)
        response = client.get(url)
        assert response.status_code == 200, url
        assert response.headers["content-type"].split(";")[0] in JS_MIME, url
        for static_import, dynamic_import in IMPORT_PATTERN.findall(response.text):
            pending.append(_module_url(url, static_import or dynamic_import))
    expected = {
        "/static/js/app.js", "/static/js/api.js", "/static/js/router.js", "/static/js/dom.js",
        "/static/js/theme.js", "/static/js/pages/placeholder.js", "/static/js/pages/settings.js",
    }
    assert seen == expected


def test_stylesheet_and_icon_served(client):
    css = client.get("/static/css/app.css")
    assert css.status_code == 200 and css.headers["content-type"].startswith("text/css")
    icon = client.get("/static/favicon.svg")
    assert icon.status_code == 200 and icon.headers["content-type"].startswith("image/svg+xml")


def test_javascript_never_inserts_html():
    forbidden = re.compile(r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function")
    for path in Path(STATIC_DIR, "js").rglob("*.js"):
        assert not forbidden.search(path.read_text(encoding="utf-8")), path


def test_unknown_api_path_returns_json_404(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": {"code": "not_found", "message": "There is nothing at this address."}}


def test_unknown_static_file_returns_json_404(client):
    response = client.get("/static/js/missing.js")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_static_path_traversal_refused(client):
    response = client.get("/static/..%2F..%2Fapp%2Fmain.py")
    assert response.status_code == 404


def test_system_endpoint_returns_every_settings_field(client, settings):
    data = client.get("/api/v1/system").json()
    for field in [
        "version", "python_version", "sqlite_version", "data_dir", "database_path", "database_size_bytes",
        "schema_version", "migrations", "last_backup", "integrity", "instance_id", "created_at",
    ]:
        assert field in data, field
    assert data["version"] == "0.1.0"
    assert data["schema_version"] == 1
    assert data["migrations"][0]["version"] == 1
    assert data["migrations"][0]["name"] == "foundation"
    assert data["migrations"][0]["applied_at"]
    assert data["data_dir"] == str(settings.data_dir)
    assert data["database_size_bytes"] > 0
    assert data["integrity"]["result"] == "ok" and data["integrity"]["checked_at"]
    assert data["last_backup"] is None  # a brand-new database has no backup yet
    assert "owner" not in " ".join(data).lower()  # no owner-name field (E3)


def test_session_returns_token(client):
    assert len(client.get("/api/v1/session").json()["csrf_token"]) >= 43


def test_api_docs_disabled(client):
    for path in ["/docs", "/redoc", "/openapi.json"]:
        assert client.get(path).status_code == 404
