@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Lancez INSTALLER_WINDOWS.cmd / Run INSTALLER_WINDOWS.cmd first.
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0did_talisman.py" --lang en
