"""Tester-agent tests (T-20261030-002-TST): CON-009 and NFR-011, tests and code stay inside the repository.

CON-009: no file is written outside the AgentDesk folder, and the home folder (which is itself a Git
repository) is never touched.
"""

import re
from pathlib import Path

from app.core.config import REPO_ROOT, Settings

HOME_TOUCHING = re.compile(
    r"expanduser|Path\.home\(|gettempdir|tempfile\.|mkdtemp|NamedTemporaryFile|"
    r"environ\[\s*['\"](USERPROFILE|HOME|TEMP|TMP|APPDATA|LOCALAPPDATA)['\"]|"
    r"getenv\(\s*['\"](USERPROFILE|HOME|TEMP|TMP|APPDATA|LOCALAPPDATA)['\"]"
)
GIT_CALLS = re.compile(r"""subprocess[^\n]*['"]git['"]|os\.system\(\s*['"]git|\bgit\s+(init|add|commit|push|reset|clean|checkout|config)\b""")


def _sources(folder: Path):
    return [p for p in folder.rglob("*.py") if "__pycache__" not in p.parts]


def test_tst_temporary_test_folders_are_inside_the_repository(tmp_path, settings):
    base = (REPO_ROOT / ".pytest_tmp").resolve()
    assert base in tmp_path.resolve().parents, tmp_path
    assert base in settings.data_dir.resolve().parents


def test_tst_pytest_ini_keeps_temporary_files_in_the_repository():
    ini = (REPO_ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert "--basetemp=.pytest_tmp" in ini
    assert ".pytest_tmp/" in (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_tst_no_test_or_source_file_reaches_the_home_or_temp_folder():
    offenders = []
    for folder in (REPO_ROOT / "tests", REPO_ROOT / "app", REPO_ROOT / "scripts"):
        for path in _sources(folder):
            text = path.read_text(encoding="utf-8")
            if path.name == Path(__file__).name:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if HOME_TOUCHING.search(line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
    assert offenders == []


def test_tst_no_test_or_source_file_runs_git_commands():
    offenders = []
    for folder in (REPO_ROOT / "tests", REPO_ROOT / "app", REPO_ROOT / "scripts"):
        for path in _sources(folder):
            if path.name == Path(__file__).name:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if GIT_CALLS.search(line) and not line.lstrip().startswith(("#", '"""', "r\"\"\"")):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
    assert offenders == []


def test_tst_default_settings_point_into_the_repository_not_the_home_folder():
    home = Path.home().resolve()
    assert Settings().data_dir == REPO_ROOT / "data"
    assert REPO_ROOT != home and home not in REPO_ROOT.parents
    assert not (REPO_ROOT / "data").resolve().is_relative_to(home)


def test_tst_hard_coded_absolute_paths_are_absent_from_the_application():
    for folder in (REPO_ROOT / "app", REPO_ROOT / "scripts"):
        for path in list(_sources(folder)) + list(folder.rglob("*.bat")):
            text = path.read_text(encoding="utf-8")
            assert not re.search(r"[A-Za-z]:\\\\?Users", text), path
            assert "AppData" not in text, path
