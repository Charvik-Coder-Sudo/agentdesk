@echo off
rem Start AgentDesk on http://127.0.0.1:8765 and open it in the default browser.
rem Press Ctrl+C in this window to stop it.
setlocal
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo AgentDesk is not set up yet: run scripts\setup.bat first.
    exit /b 1
)

".venv\Scripts\python.exe" -m app --open
exit /b %errorlevel%
