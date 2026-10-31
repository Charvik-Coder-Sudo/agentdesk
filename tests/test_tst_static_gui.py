"""Tester-agent tests (T-20261030-002-TST): static files and the GUI shell, checked from the files.

FR-004..FR-008, NFR-005, NFR-008..NFR-010. Browser behaviour itself is only covered by the owner's
manual checklist (DEC-014); these tests check the files the browser will load.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app.main import STATIC_DIR

JS_FILES = sorted(STATIC_DIR.rglob("*.js"))
HTML = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
CSS = (STATIC_DIR / "css" / "app.css").read_text(encoding="utf-8")
NAV = [
    ("overview", "Overview"), ("projects", "Projects"), ("agents", "Agents"), ("activity", "Activity"),
    ("files", "File changes"), ("reports", "Reports"), ("documents", "Documents"), ("testing", "Testing"),
    ("security", "Security"), ("approvals", "Approvals"), ("settings", "Settings"),
]
# architecture.md section 10.1, column "Real data from": the phase in which the page's content arrives.
PHASE_OF = {"overview": 2, "projects": 3, "agents": 2, "activity": 2, "files": 3, "reports": 3,
            "documents": 5, "testing": 5, "security": 5, "approvals": 5}


# ---------- index.html ----------

def test_tst_every_local_reference_in_index_exists():
    refs = re.findall(r'(?:src|href)="(/static/[^"]+)"', HTML)
    assert refs
    for ref in refs:
        assert (STATIC_DIR / ref.removeprefix("/static/")).is_file(), ref


def test_tst_index_loads_only_local_resources():
    for url in re.findall(r'(?:src|href|action)="([^"#][^"]*)"', HTML):
        assert url.startswith("/static/"), url
    assert "http://" not in HTML and "https://" not in HTML


def test_tst_index_has_no_inline_code_or_style_in_any_form():
    lowered = HTML.lower()
    assert "<style" not in lowered and "javascript:" not in lowered
    assert not re.search(r"<script(?![^>]*\bsrc=)", lowered)
    assert not re.search(r"\b(style|on[a-z]+|srcdoc)\s*=", lowered)
    assert re.findall(r'<script[^>]*type="module"[^>]*src="/static/js/app.js"', HTML)


def test_tst_navigation_has_eleven_entries_in_order_with_matching_routes():
    nav = re.search(r'<nav class="app-nav"[^>]*>(.*?)</nav>', HTML, re.S).group(1)
    items = re.findall(r'<a href="#/([a-z]+)">([^<]+)</a>', nav)
    assert items == NAV
    assert len(re.findall(r"<li>", nav)) == 11
    assert 'aria-label="Main"' in HTML


def test_tst_skip_link_is_the_first_focusable_element_and_targets_main():
    body = HTML.split("<body>", 1)[1]
    first = re.search(r"<(a|button|input|select|textarea)\b[^>]*>", body)
    assert 'class="skip-link"' in first.group(0) and 'href="#main"' in first.group(0)
    assert re.search(r'<main id="main"[^>]*tabindex="-1"', HTML)


def test_tst_page_basics_for_accessibility():
    assert '<html lang="en">' in HTML
    assert 'name="viewport" content="width=device-width, initial-scale=1"' in HTML
    assert re.search(r"<title>[^<]+</title>", HTML)
    assert 'aria-live="polite"' in HTML and "<noscript>" in HTML
    assert re.search(r'<label for="theme-select">', HTML)
    assert re.findall(r'<option value="(system|light|dark)"', HTML) == ["system", "light", "dark"]


def test_tst_server_status_uses_icon_and_text_not_colour_alone():
    assert 'class="status-icon"' in HTML and 'class="status-text"' in HTML
    app_js = (STATIC_DIR / "js" / "app.js").read_text(encoding="utf-8")
    for state, icon, text in (("ok", "✓", "Server OK"), ("down", "✕", "Server unreachable")):
        assert re.search(rf'{state}: \{{ icon: "{icon}", text: "{text}" \}}', app_js)


def test_tst_health_polling_is_every_10_seconds_and_only_while_visible():
    app_js = (STATIC_DIR / "js" / "app.js").read_text(encoding="utf-8")
    assert "HEALTH_INTERVAL_MS = 10000" in app_js
    assert 'document.visibilityState === "visible"' in app_js
    assert "visibilitychange" in app_js
    assert "HEALTH_TIMEOUT_MS = 4000" in app_js  # 10 s + 4 s < 15 s for FR-004 (2)


# ---------- JavaScript sources (NFR-005) ----------

FORBIDDEN = [
    r"\binnerHTML\b", r"\bouterHTML\b", r"insertAdjacentHTML", r"document\.write", r"\beval\s*\(", r"new\s+Function",
    r"createContextualFragment", r"\bDOMParser\b", r"\bsrcdoc\b", r"setAttribute\(\s*['\"]style['\"]",
    r"setTimeout\(\s*['\"`]", r"setInterval\(\s*['\"`]", r"javascript:", r"\bimportScripts\b", r"\bWebSocket\b",
    r"\bXMLHttpRequest\b", r"https?://", r"localStorage\.setItem\([^)]*token", r"\bdocument\.cookie\b",
]


@pytest.mark.parametrize("path", JS_FILES, ids=lambda p: p.relative_to(STATIC_DIR).as_posix())
def test_tst_javascript_uses_no_html_injection_or_dynamic_code(path):
    text = path.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", text)  # comments may mention the forbidden names
    for pattern in FORBIDDEN:
        assert not re.search(pattern, code), f"{path.name}: {pattern}"


def test_tst_there_are_exactly_the_expected_js_modules():
    names = [p.relative_to(STATIC_DIR / "js").as_posix() for p in JS_FILES]
    assert names == ["api.js", "app.js", "dom.js", "pages/placeholder.js", "pages/settings.js", "router.js", "theme.js"]


def test_tst_css_and_svg_load_nothing_external_and_svg_has_no_script():
    assert not re.search(r"@import|url\(\s*['\"]?https?:|url\(\s*['\"]?//", CSS)
    svg = (STATIC_DIR / "favicon.svg").read_text(encoding="utf-8").lower()
    assert "<script" not in svg and "onload" not in svg and "href=" not in svg


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed (DEC-022)")
def test_tst_javascript_syntax_check_with_negative_control(tmp_path):
    """DEC-022: the reliable form is `node --input-type=module --check < file` (plain --check can false-pass)."""

    def check(source: bytes):
        return subprocess.run(
            ["node", "--input-type=module", "--check"], input=source, capture_output=True, timeout=60
        ).returncode

    assert check(b"export const x = ;\n") != 0, "negative control: a broken file must fail the check"
    assert check(b"export const x = 1;\n") == 0
    for path in JS_FILES:
        assert check(path.read_bytes()) == 0, path.name


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed (DEC-022)")
def test_tst_node_unit_tests_for_the_javascript_modules():
    """Runs tests/js/*.test.mjs with `node --test` (no npm packages)."""
    root = Path(__file__).resolve().parent / "js"
    files = sorted(str(p) for p in root.glob("*.test.mjs"))
    assert files, "no JavaScript tests found"
    result = subprocess.run(["node", "--test", *files], capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
    assert re.search(r"^ℹ fail 0$", result.stdout, re.M), result.stdout[-2000:]


# ---------- Placeholder and Settings modules (FR-005, FR-006, FR-008) ----------

PLACEHOLDER = (STATIC_DIR / "js" / "pages" / "placeholder.js").read_text(encoding="utf-8")
SETTINGS = (STATIC_DIR / "js" / "pages" / "settings.js").read_text(encoding="utf-8")


def test_tst_ten_placeholder_pages_with_title_purpose_and_the_right_phase():
    blocks = re.findall(
        r'path: "/(\w+)",\s*title: "([^"]+)",\s*purpose: "([^"]+)",\s*phase: "([^"]+)"', PLACEHOLDER
    )
    assert [b[0] for b in blocks] == [route for route, _ in NAV[:-1]]
    titles = dict(NAV)
    for route, title, purpose, phase in blocks:
        assert title == titles[route]
        assert purpose.endswith(".") and purpose.count(". ") == 0, f"one sentence expected: {purpose}"
        assert not re.search(r"\d", purpose), "no numbers or invented data in the purpose"
        assert re.match(r"Arrives in Phase %d\b" % PHASE_OF[route], phase), (route, phase)


def test_tst_placeholder_page_shows_no_data_elements():
    assert "Placeholder" in PLACEHOLDER and "shows no data" in PLACEHOLDER
    assert not re.search(r'h\("(table|ul|ol|li|img|canvas|svg)"', PLACEHOLDER)
    assert "api." not in PLACEHOLDER and "fetch(" not in PLACEHOLDER, "placeholders must not call the server"


def test_tst_settings_page_calls_system_and_backup_endpoints_with_csrf_aware_client():
    assert 'api.get("/api/v1/system")' in SETTINGS
    assert 'api.get("/api/v1/system/backups")' in SETTINGS
    assert 'api.post("/api/v1/system/backups"' in SETTINGS
    assert "fetch(" not in SETTINGS, "all calls must go through api.js (CSRF header)"


def test_tst_settings_page_shows_every_required_field_and_no_profile():
    for label in ("AgentDesk version", "Python version", "SQLite version", "Data folder", "Schema version",
                  "Applied migrations", "Database file size", "Integrity check", "Last backup", "Create backup now"):
        assert label in SETTINGS, label
    for column in ('"Version", "Name", "Applied"', '"Name", "Reason", "Size", "Created"'):
        assert column in SETTINGS
    assert not re.search(r"owner|profile|\bh\(\"input\"", SETTINGS, re.I), "no owner-name or profile field (E3)"
    assert "aria-disabled" in SETTINGS and "announce(" in SETTINGS


def test_tst_api_client_sends_csrf_only_for_state_changing_requests_and_retries_once():
    api_js = (STATIC_DIR / "js" / "api.js").read_text(encoding="utf-8")
    assert '"X-AgentDesk-CSRF"' in api_js and "retry: false" in api_js
    assert "credentials: \"same-origin\"" in api_js and 'cache: "no-store"' in api_js


# ---------- Stylesheet: contrast, responsiveness, motion, focus (NFR-008..NFR-010) ----------

def _tokens(block: str) -> dict:
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", block))


def _blocks():
    light = _tokens(re.search(r":root \{(.*?)\n\}", CSS, re.S).group(1))
    dark = _tokens(re.search(r':root\[data-theme="dark"\] \{(.*?)\n\}', CSS, re.S).group(1))
    system_dark = _tokens(
        re.search(r"@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme=\"light\"\]\) \{(.*?)\n  \}", CSS, re.S).group(1)
    )
    return light, dark, system_dark


def _luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


TEXT_PAIRS = [
    ("text", "bg"), ("text", "surface"), ("text", "surface-alt"), ("text-muted", "bg"), ("text-muted", "surface"),
    ("text-muted", "surface-alt"), ("accent", "bg"), ("accent", "surface"), ("on-accent", "accent"),
    ("text", "nav-active-bg"), ("accent", "nav-active-bg"), ("ok", "ok-bg"), ("error", "error-bg"), ("warn", "warn-bg"),
    ("ok", "surface"), ("error", "surface"), ("warn", "surface"),
]
UI_PAIRS = [("control-border", "surface"), ("control-border", "bg"), ("focus", "bg"), ("focus", "surface")]


@pytest.mark.parametrize("theme", [0, 1], ids=["light", "dark"])
def test_tst_text_contrast_is_at_least_4_5_to_1(theme):
    tokens = _blocks()[theme]
    for fg, bg in TEXT_PAIRS:
        ratio = contrast(tokens[fg], tokens[bg])
        assert ratio >= 4.5, f"{fg} on {bg}: {ratio:.2f}"


@pytest.mark.parametrize("theme", [0, 1], ids=["light", "dark"])
def test_tst_control_and_focus_contrast_is_at_least_3_to_1(theme):
    tokens = _blocks()[theme]
    for fg, bg in UI_PAIRS:
        ratio = contrast(tokens[fg], tokens[bg])
        assert ratio >= 3.0, f"{fg} on {bg}: {ratio:.2f}"


def test_tst_system_dark_theme_uses_the_same_colours_as_explicit_dark():
    _, dark, system_dark = _blocks()
    for name, value in system_dark.items():
        assert dark[name].lower() == value.lower(), name


def test_tst_stylesheet_has_responsive_motion_and_focus_rules():
    assert "@media (min-width: 960px)" in CSS
    assert re.search(r"@media \(prefers-reduced-motion: reduce\)", CSS)
    reduced = CSS.split("prefers-reduced-motion: reduce", 1)[1]
    assert "animation" in reduced and "transition" in reduced
    focus = re.search(r":focus-visible\s*\{([^}]*)\}", CSS).group(1)
    assert "outline" in focus and "none" not in focus.split("outline")[1].split(";")[0]
    assert "overflow-wrap" in CSS or "word-break" in CSS, "long paths must wrap at narrow widths"
    assert ".visually-hidden" in CSS and ".skip-link" in CSS


def test_tst_outline_is_removed_only_from_script_focused_headings_and_main():
    """Controls must keep a visible focus indicator (NFR-008). Only h1 and main, which are focused by script
    after navigation and cannot be reached with Tab, may have the outline removed."""
    for selector_text, body in re.findall(r"([^{}]+)\{([^{}]*)\}", CSS):
        if re.search(r"outline\s*:\s*(none|0)", body):
            selectors = [part.strip() for part in selector_text.split(",")]
            assert selectors == ["h1:focus", "main:focus"], selectors


# ---------- Served files ----------

def test_tst_static_files_are_served_with_correct_types(client):
    expected = {
        "/static/js/app.js": "text/javascript", "/static/js/router.js": "text/javascript",
        "/static/css/app.css": "text/css", "/static/favicon.svg": "image/svg+xml",
    }
    for path, mime in expected.items():
        response = client.get(path)
        assert response.status_code == 200 and response.headers["content-type"].startswith(mime), path
        assert response.headers["x-content-type-options"] == "nosniff"


def test_tst_every_file_in_static_is_served_unchanged(client):
    for path in STATIC_DIR.rglob("*"):
        if path.is_file():
            url = "/static/" + path.relative_to(STATIC_DIR).as_posix()
            assert client.get(url).content == path.read_bytes(), url
