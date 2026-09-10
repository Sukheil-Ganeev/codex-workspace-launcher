@echo off
setlocal
REM Codex Workspace Launcher installer (Windows). Run by double-clicking.

for %%I in ("%~dp0..") do set "REPO=%%~fI"
set "LAUNCHER=%REPO%\launcher.py"

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python not found. Install from https://python.org
  echo        and tick "Add python.exe to PATH", then re-run this file.
  pause
  exit /b 1
)

REM Create a command wrapper in the user's bin folder
if not exist "%USERPROFILE%\bin" mkdir "%USERPROFILE%\bin"
set "WRAPPER=%USERPROFILE%\bin\codex-workspace.cmd"
> "%WRAPPER%" echo @echo off
>> "%WRAPPER%" echo python "%LAUNCHER%" %%*

echo OK: command wrapper created: %WRAPPER%
echo.
echo Use in a terminal:
echo   codex-workspace pick
echo   codex-workspace add C:\path\to\project --label "Name"
echo.
echo If "%USERPROFILE%\bin" is not on PATH, add it manually.
pause
