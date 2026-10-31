"""Tester-agent tests (T-20261030-002-TST): scripts\\setup.bat and scripts\\start.bat.

FR-001 (criteria 3 and 5), FR-002 (criterion 2), NFR-011, CON-009, CON-004.
The scripts are copied into a private folder under .sandbox\\ (ignored by Git) and run there with
`cmd /c`. Nothing is installed and no server is started: only the failure paths and the script text
are checked here. The full setup run (which needs the internet) is recorded in the test report.
"""

import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from app.core.config import REPO_ROOT

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows batch files")

SCRIPTS = REPO_ROOT / "scripts"
SANDBOX = REPO_ROOT / ".sandbox"
SYSTEM32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")


@pytest.fixture
def sandbox():
    """A copy of the scripts folder (and requirement files) in .sandbox\\tst-<id>\\ ."""
    root = SANDBOX / f"tst-{uuid.uuid4().hex[:8]}"
    (root / "scripts").mkdir(parents=True)
    for name in ("setup.bat", "start.bat"):
        shutil.copy(SCRIPTS / name, root / "scripts" / name)
    for name in ("requirements.txt", "requirements.lock.txt", "requirements-dev.txt"):
        shutil.copy(REPO_ROOT / name, root / name)
    yield root
    shutil.rmtree(root, ignore_errors=True)


def run_bat(root, script, args=(), path=None, timeout=60):
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("PATH",)}
    env["PATH"] = path if path is not None else os.environ["PATH"]
    return subprocess.run(
        ["cmd", "/c", str(root / "scripts" / script), *args],
        capture_output=True, text=True, cwd=str(root), env=env, timeout=timeout,
    )


def snapshot(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*"))


# ---------- FR-001: setup.bat failure paths ----------

def test_tst_setup_without_python_exits_nonzero_and_creates_nothing(sandbox):
    before = snapshot(sandbox)
    result = run_bat(sandbox, "setup.bat", path=SYSTEM32)
    assert result.returncode != 0
    assert "3.12" in result.stdout
    assert "python.org" in result.stdout
    assert not (sandbox / ".venv").exists()
    assert snapshot(sandbox) == before, "nothing may be created when Python is missing"


def test_tst_setup_version_check_expression_accepts_3_12_and_newer_only(tmp_path):
    """The check inside setup.bat, run with a pretend version (a fake python.cmd cannot be used:
    cmd does not return from a .cmd that is called without `call`)."""
    expression = re.search(r'python -c "([^"]+)"', SETUP).group(1)
    for version, expected in (((3, 11, 9), 1), ((3, 12, 0), 0), ((3, 12, 7), 0), ((3, 15, 2), 0), ((3, 9, 0), 1),
                              ((2, 7, 18), 1), ((4, 0, 0), 0), ((3, 0, 0), 1)):
        code = f"import sys; sys.version_info = {version!r}; " + expression.replace("import sys; ", "", 1)
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=30)
        assert result.returncode == expected, (version, result.returncode, result.stderr)


def test_tst_setup_with_dev_argument_also_checks_python_first(sandbox):
    result = run_bat(sandbox, "setup.bat", args=["dev"], path=SYSTEM32)
    assert result.returncode != 0 and not (sandbox / ".venv").exists()


# ---------- FR-002: start.bat without .venv ----------

def test_tst_start_without_venv_says_run_setup_first_and_exits_nonzero(sandbox):
    result = run_bat(sandbox, "start.bat")
    assert result.returncode != 0
    assert "scripts\\setup.bat" in result.stdout and "not set up" in result.stdout


def test_tst_start_works_from_any_current_folder_and_still_finds_the_repository(sandbox, tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()
    env = dict(os.environ)
    result = subprocess.run(
        ["cmd", "/c", str(sandbox / "scripts" / "start.bat")], capture_output=True, text=True, cwd=str(other), env=env, timeout=60
    )
    assert result.returncode != 0 and "setup.bat" in result.stdout  # it resolved the repository root, not the cwd


# ---------- script review (text) ----------

SETUP = (SCRIPTS / "setup.bat").read_text(encoding="utf-8")
START = (SCRIPTS / "start.bat").read_text(encoding="utf-8")


def test_tst_setup_script_text_installs_pinned_packages_inside_the_repository():
    assert 'cd /d "%~dp0.."' in SETUP
    assert "requirements.lock.txt" in SETUP and "requirements-dev.txt" in SETUP
    assert SETUP.count("--no-cache-dir") >= 2 and "PIP_NO_CACHE_DIR=1" in SETUP
    assert 'if /i "%~1"=="dev"' in SETUP
    assert "python -m venv .venv" in SETUP and 'if not exist ".venv\\Scripts\\python.exe"' in SETUP  # second run reuses it
    assert "sys.version_info >= (3, 12)" in SETUP
    for forbidden in ("%USERPROFILE%", "%APPDATA%", "%LOCALAPPDATA%", "%HOMEPATH%", "C:\\Users", "--user", "setx", "reg add",
                      "pip install -r requirements.txt", "git "):
        assert forbidden.lower() not in SETUP.lower(), forbidden
    assert re.search(r"set \"TEMP=%CD%\\\.sandbox\\tmp\"", SETUP) and re.search(r"set \"TMP=%CD%\\\.sandbox\\tmp\"", SETUP)


def test_tst_setup_script_exits_zero_only_on_success_and_nonzero_on_each_failure():
    assert SETUP.count("exit /b 1") == 4 and SETUP.rstrip().endswith("exit /b 0")
    assert SETUP.count("if errorlevel 1") == 4


def test_tst_start_script_text():
    assert 'cd /d "%~dp0.."' in START
    assert '".venv\\Scripts\\python.exe" -m app --open' in START
    assert "exit /b %errorlevel%" in START and "exit /b 1" in START
    assert "setup.bat" in START


def test_tst_requirement_files_are_pinned_and_dev_has_test_tools():
    lock = (REPO_ROOT / "requirements.lock.txt").read_text(encoding="utf-8").split()
    assert lock and all("==" in line for line in lock), "the lock file must pin every package"
    top = dict(line.split("==") for line in (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").split())
    locked = dict(line.split("==") for line in lock)
    for name, version in top.items():
        assert locked[name] == version
    dev = (REPO_ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "-r requirements.lock.txt" in dev and re.search(r"^pytest==", dev, re.M) and re.search(r"^httpx==", dev, re.M)
    assert dict(line.split("==") for line in lock if line.startswith(("fastapi", "uvicorn", "starlette"))) == {
        "fastapi": "0.162.0", "uvicorn": "0.54.0", "starlette": "1.10.0"}


def test_tst_the_sandbox_folder_is_ignored_by_git():
    assert ".sandbox/" in (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
