@echo off
rem AgentDesk setup: creates the virtual environment .venv in this repository and installs
rem the pinned packages from requirements.lock.txt.
rem   scripts\setup.bat        runtime packages only
rem   scripts\setup.bat dev    also the test tools from requirements-dev.txt
rem Everything is written inside the repository: pip's download cache is disabled and
rem temporary files go to .sandbox\tmp (ignored by Git) instead of the Windows temp folder.
setlocal
cd /d "%~dp0.."

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
if errorlevel 1 (
    echo AgentDesk needs Python 3.12 or newer, and the "python" command did not provide it.
    echo Install Python 3.12 or newer from https://www.python.org/downloads/ and tick
    echo "Add python.exe to PATH" during installation. Then open a new Command Prompt and
    echo run scripts\setup.bat again.
    exit /b 1
)

if not exist ".sandbox\tmp" mkdir ".sandbox\tmp"
set "TEMP=%CD%\.sandbox\tmp"
set "TMP=%CD%\.sandbox\tmp"
set "PIP_NO_CACHE_DIR=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

if not exist ".venv\Scripts\python.exe" (
    echo Creating the virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo Could not create the virtual environment. See the messages above.
        exit /b 1
    )
)

echo Installing the AgentDesk packages from requirements.lock.txt ...
".venv\Scripts\python.exe" -m pip install --no-cache-dir -r requirements.lock.txt
if errorlevel 1 (
    echo Installing the packages failed. Check your internet connection and run scripts\setup.bat again.
    exit /b 1
)

if /i "%~1"=="dev" (
    echo Installing the test tools from requirements-dev.txt ...
    ".venv\Scripts\python.exe" -m pip install --no-cache-dir -r requirements-dev.txt
    if errorlevel 1 (
        echo Installing the test tools failed. Check your internet connection and run scripts\setup.bat dev again.
        exit /b 1
    )
)

echo.
echo Setup complete. Start AgentDesk with: scripts\start.bat
exit /b 0
