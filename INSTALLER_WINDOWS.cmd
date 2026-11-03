@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALLER_WINDOWS.ps1"
if errorlevel 1 echo Installation incomplete. Lire le message ci-dessus.
pause
