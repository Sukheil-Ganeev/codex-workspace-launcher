@echo off
setlocal
REM Codex Workspace Launcher installer (Windows). Run by double-clicking.

for %%I in ("%~dp0..") do set "REPO=%%~fI"
set "LAUNCHER=%REPO%\launcher.py"

REM Find Python: prefer "python" on PATH, then the "py" launcher, then common paths.
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
  where py >nul 2>nul && set "PY=py -3"
)
if not defined PY (
  if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if not defined PY (
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY (
  echo ERROR: Python not found. Install from https://python.org
  echo        and tick "Add python.exe to PATH", then re-run this file.
  pause
  exit /b 1
)

REM Command wrapper in the user's bin folder
if not exist "%USERPROFILE%\bin" mkdir "%USERPROFILE%\bin"
set "WRAPPER=%USERPROFILE%\bin\codex-workspace.cmd"
> "%WRAPPER%" echo @echo off
>> "%WRAPPER%" echo %PY% "%LAUNCHER%" %%*

echo OK: command wrapper created: %WRAPPER%
echo.
echo Use in a terminal:
echo   codex-workspace pick
echo   codex-workspace list
echo   codex-workspace add C:\path\to\project --label "Name"
echo   codex-workspace open ^<id^> --tool claude --mode safe
echo   codex-workspace tools
echo.
where codex-workspace >nul 2>nul
if errorlevel 1 (
  echo NOTE: "%USERPROFILE%\bin" is not on your PATH yet.
  echo Add it in Settings ^> System ^> About ^> Advanced system settings ^>
  echo Environment Variables, then reopen the terminal.
  echo Or open a terminal and run:  setx PATH "%PATH%;%USERPROFILE%\bin"
)
echo To remove: run install\windows-uninstall.bat
pause
