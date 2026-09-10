@echo off
REM Remove the Codex Workspace Launcher from this Windows machine.
del /q "%USERPROFILE%\bin\codex-workspace.cmd" 2>nul
echo Removed the codex-workspace command wrapper.
echo Your project registry stays in %LOCALAPPDATA%\codex-workspace-launcher
echo (delete that folder to forget all projects).
pause
