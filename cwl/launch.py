"""Launch plans for macOS / Linux / Windows.

Terminal CLI tools open inside a terminal with the working directory set to
the project folder. Desktop apps open directly (`open -a` on macOS, `start`
on Windows); when a tool supports receiving the folder, it is passed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


def os_name() -> str:
    if sys.platform == "darwin":
        return "macos"
    if os.name == "nt":
        return "windows"
    return "linux"


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


@dataclass(frozen=True)
class LaunchPlan:
    """A validated, executable launch plan (also printable for --dry-run)."""

    command: tuple[str, ...]
    cwd: str | None
    target: str          # human description: terminal/app name
    platform: str        # macos | linux | windows
    environment: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict:
        return {
            "command": list(self.command),
            "cwd": self.cwd,
            "target": self.target,
            "platform": self.platform,
            "environment": dict(self.environment),
        }


def find_terminal() -> str | None:
    """Best available terminal for this platform."""
    configured = os.environ.get("CODEX_TERMINAL")
    if configured:
        exe = shutil.which(configured)
        if exe:
            return exe
        path = Path(configured)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    if os_name() == "macos":
        # Terminal.app is always present; iTerm2 is preferred if installed.
        if Path("/Applications/iTerm.app").exists():
            return "iTerm2"
        return "Terminal"
    if os_name() == "windows":
        for name in ("wt.exe", "cmd.exe"):
            exe = shutil.which(name)
            if exe:
                return exe
        return None
    for name in ("gnome-terminal", "kitty", "alacritty", "wezterm",
                 "xterm", "konsole", "x-terminal-emulator"):
        exe = shutil.which(name)
        if exe:
            return exe
    return None


def build_plan(workspace: str | Path,
               tool_report,
               mode: str,
               mode_arguments: tuple[str, ...]) -> LaunchPlan:
    """Build the launch plan for one tool in one project folder."""
    workspace_str = str(Path(workspace).expanduser().resolve(strict=False))
    platform = os_name()

    if tool_report.launch_mode == "app":
        return _app_plan(platform, workspace_str, tool_report)

    executable = tool_report.executable_path or ""
    if not executable:
        raise ValueError("tool executable is empty")
    args = (*tool_report.launch_arguments, *mode_arguments)

    if platform == "macos":
        terminal = find_terminal() or "Terminal"
        return _macos_terminal_plan(terminal, workspace_str,
                                    executable, args)
    if platform == "windows":
        return _windows_terminal_plan(find_terminal(), workspace_str,
                                      executable, args)
    return _linux_terminal_plan(find_terminal(), workspace_str,
                                executable, args)


def _app_plan(platform: str, workspace: str, tool_report) -> LaunchPlan:
    app_name = tool_report.id.replace("-app", "").title()
    if platform == "macos":
        return LaunchPlan(
            command=("open", "-a", app_name, workspace),
            cwd=None, target=app_name, platform=platform)
    if platform == "windows":
        return LaunchPlan(
            command=("cmd.exe", "/c", "start", "", "explorer.exe", workspace),
            cwd=None, target=app_name, platform=platform)
    return LaunchPlan(
        command=("xdg-open", workspace), cwd=None, target=app_name,
        platform=platform)


def _macos_terminal_plan(terminal: str, workspace: str,
                         executable: str,
                         args: tuple[str, ...]) -> LaunchPlan:
    """Run the tool via a temporary .command file opened in the terminal.

    No AppleScript and no automation permission prompt: `open -a <terminal>
    <file>.command` starts the terminal app with our script. The temp file
    lives in the system temp dir and is cleaned by the OS.
    """
    script = ("#!/bin/bash\n"
              "cd " + _shell_quote(workspace) + " && exec " +
              _shell_quote(executable) +
              (" " + " ".join(args) if args else "") + "\n")
    fd, path = tempfile.mkstemp(suffix=".command",
                                prefix="codex-workspace-")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(script)
    os.chmod(path, 0o755)
    return LaunchPlan(command=("open", "-a", terminal, path),
                      cwd=None, target=terminal, platform="macos")


def _linux_terminal_plan(terminal: str | None, workspace: str,
                         executable: str,
                         args: tuple[str, ...]) -> LaunchPlan:
    if not terminal:
        raise ValueError("no terminal found; set CODEX_TERMINAL")
    base = os.path.basename(terminal)
    if base == "gnome-terminal":
        command = (terminal, "--working-directory", workspace, "--",
                   executable, *args)
    elif base == "kitty":
        command = (terminal, "--directory", workspace, executable, *args)
    elif base == "alacritty":
        command = (terminal, "--working-directory", workspace, "-e",
                   executable, *args)
    elif base == "wezterm":
        command = (terminal, "start", "--cwd", workspace, "--",
                   executable, *args)
    else:
        command = (terminal, "-e", executable, *args)
    return LaunchPlan(command=command, cwd=workspace, target=base,
                      platform="linux")


def _windows_terminal_plan(terminal: str | None, workspace: str,
                           executable: str,
                           args: tuple[str, ...]) -> LaunchPlan:
    exe = executable
    # Windows Terminal runs the command in a new tab at the given directory.
    if terminal and os.path.basename(terminal).lower() == "wt.exe":
        return LaunchPlan(
            command=(terminal, "-d", workspace, exe, *args),
            cwd=None, target="Windows Terminal", platform="windows")
    # No Windows Terminal: open a fresh console window with the working
    # directory set via `start /D`. Works for .exe, .cmd and .bat tools.
    return LaunchPlan(
        command=("cmd.exe", "/c", "start", "", "/D", workspace, exe, *args),
        cwd=None, target="cmd.exe", platform="windows")


def execute(plan: LaunchPlan) -> None:
    """Run the plan detached, so the picker/CLI can exit immediately."""
    kwargs = {
        "cwd": plan.cwd,
        "start_new_session": True,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if plan.environment:
        env = os.environ.copy()
        env.update(dict(plan.environment))
        kwargs["env"] = env
    subprocess.Popen(list(plan.command), **kwargs)
