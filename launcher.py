#!/usr/bin/env python3
"""Codex Workspace Launcher — pick a project and open an AI tool in it.

Cross-platform (Windows, Linux, macOS). Stdlib only, no dependencies.

What it does
------------
1. Finds your registered projects (folders you work in).
2. Shows a picker (native dialog on macOS, numbered list elsewhere).
3. Opens the chosen AI tool (Codex, Claude, Muse, Qwen, ...) in that folder,
   in a terminal.

Setup
-----
  launcher.py add /path/to/project --label "My project"
  launcher.py pick                 # interactive picker
  launcher.py list                 # list projects
  launcher.py open <id>            # open project directly

Projects can also be auto-discovered from the CODEX_WORKSPACE_ROOTS env var
(a colon-separated list of directories to scan).

This file stores its small registry under your user state directory:
  Linux/macOS: ~/.local/state/codex-workspace-launcher/registry.json
  Windows:     %LOCALAPPDATA%/codex-workspace-launcher/registry.json
Nothing personal ever leaves your machine.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

APP_NAME = "codex-workspace-launcher"

# ---------------------------------------------------------------------------
# Registry (small JSON file, portable)
# ---------------------------------------------------------------------------


def state_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
        return Path(base) / APP_NAME
    return Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state"))) / APP_NAME


def registry_path() -> Path:
    return state_dir() / "registry.json"


class Registry:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path) if path else registry_path()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.rows = {}
            return
        try:
            self.rows = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.rows = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.rows, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        os.replace(tmp, self.path)

    def list(self) -> list[dict]:
        return [r for r in self.rows.values() if not r.get("archived")]

    def get(self, wid: str) -> dict | None:
        return self.rows.get(wid)

    def add(self, path: str, label: str | None = None) -> dict:
        p = str(Path(path).expanduser().resolve(strict=False))
        wid = str(uuid.uuid5(uuid.NAMESPACE_URL, "codex-workspace:" + p))
        row = self.rows.get(wid, {"id": wid, "path": p, "created_at": 0})
        row["path"] = p
        if label:
            row["label"] = label
        else:
            row.setdefault("label", Path(p).name)
        row.setdefault("created_at", 0)
        self.rows[wid] = row
        self._save()
        return row

    def remove(self, wid: str) -> None:
        if wid in self.rows:
            self.rows[wid]["archived"] = True
            self._save()


# ---------------------------------------------------------------------------
# Tools (CLI agents detected via PATH)
# ---------------------------------------------------------------------------

TOOLS = [
    ("codex", "Codex", "codex"),
    ("claude", "Claude", "claude"),
    ("muse", "Muse", "muse"),
    ("qwen", "Qwen", "qwen"),
    ("grok", "Grok", "grok"),
    ("opencode", "OpenCode", "opencode"),
    ("gemini", "Gemini", "gemini"),
    ("copilot", "Copilot", "copilot"),
]

MODES = ("safe", "free", "yolo")
MODE_LABELS = {"safe": "Normal", "free": "No sandbox", "yolo": "Full (YOLO)"}
MODE_FLAGS = {
    "muse": {"free": ("--disable-sandbox",), "yolo": ("--yolo",)},
    "claude": {"free": ("--permission-mode", "acceptEdits"),
               "yolo": ("--dangerously-skip-permissions",)},
    "codex": {"free": ("--sandbox", "workspace-write",
                       "--ask-for-approval", "on-request"),
              "yolo": ("--yolo",)},
    "gemini": {"free": ("--approval-mode", "auto_edit"),
               "yolo": ("--approval-mode", "yolo")},
    "opencode": {"yolo": ("--yolo",)},
    "copilot": {"yolo": ("--allow-all",)},
}


def which_tool(tool_id: str) -> str | None:
    """Return the executable path for a tool, or None."""
    exe = shutil.which(tool_id)
    if exe:
        return exe
    # Common non-PATH locations (Linux/macOS user installs)
    for candidate in (Path.home() / ".local" / "bin" / tool_id,
                      Path.home() / "bin" / tool_id):
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def tool_version(tool_id: str) -> str | None:
    exe = which_tool(tool_id)
    if not exe:
        return None
    try:
        proc = subprocess.run([exe, "--version"], capture_output=True,
                              text=True, timeout=8)
        out = (proc.stdout or proc.stderr).strip()
        if proc.returncode == 0 and out:
            return out.splitlines()[0]
    except (OSError, subprocess.SubprocessError):
        return None
    return None


def mode_flags(tool_id: str, mode: str) -> tuple[str, ...]:
    return MODE_FLAGS.get(tool_id, {}).get(mode, ())


# ---------------------------------------------------------------------------
# Project discovery
# ---------------------------------------------------------------------------

def discover_projects(registry: Registry) -> list[dict]:
    """Registered projects + directories from CODEX_WORKSPACE_ROOTS."""
    seen: dict[str, dict] = {}
    for row in registry.list():
        seen[row["id"]] = row
    roots = os.environ.get("CODEX_WORKSPACE_ROOTS", "")
    if roots:
        for root in roots.split(os.pathsep):
            root = root.strip()
            if not root:
                continue
            base = Path(root).expanduser()
            if not base.is_dir():
                continue
            # Scan one level of subdirectories as candidate projects.
            for child in sorted(base.iterdir()):
                if child.is_dir():
                    row = registry.add(str(child))
                    seen.setdefault(row["id"], row)
    return list(seen.values())


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def _applescript_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def detect_os() -> str:
    if sys.platform == "darwin":
        return "macos"
    if os.name == "nt":
        return "windows"
    return "linux"


def build_tool_command(exe: str, args: tuple[str, ...]) -> str:
    parts = [_shell_quote(exe), *args]
    return " ".join(parts)


def launch(project_path: str, tool_id: str, mode: str) -> None:
    exe = which_tool(tool_id)
    if not exe:
        raise SystemExit(f"Tool not found: {tool_id}")
    args = mode_flags(tool_id, mode)
    os_name = detect_os()
    path = str(Path(project_path).expanduser().resolve(strict=False))
    if os_name == "macos":
        _launch_macos(path, exe, args)
    elif os_name == "windows":
        _launch_windows(path, exe, args)
    else:
        _launch_linux(path, exe, args)


def _launch_macos(path: str, exe: str, args: tuple[str, ...]) -> None:
    terminal = os.environ.get("CODEX_TERMINAL", "Terminal")
    cmd = "cd " + _shell_quote(path) + " && " + build_tool_command(exe, args)
    if terminal.lower() == "iterm2":
        script = ('tell application "iTerm2" to create window with '
                  "default profile command " + _applescript_string(cmd))
    else:
        script = ('tell application "Terminal" to do script ' +
                  _applescript_string(cmd))
    subprocess.Popen(["osascript", "-e", script], start_new_session=True)


def _launch_linux(path: str, exe: str, args: tuple[str, ...]) -> None:
    terminal = os.environ.get("CODEX_TERMINAL") or _find_linux_terminal()
    if not terminal:
        raise SystemExit("No terminal found. Set CODEX_TERMINAL.")
    base = os.path.basename(terminal)
    argv: list[str]
    if base == "gnome-terminal":
        argv = [terminal, "--working-directory", path, "--", exe, *args]
    elif base == "kitty":
        argv = [terminal, "--directory", path, exe, *args]
    elif base == "alacritty":
        argv = [terminal, "--working-directory", path, "-e", exe, *args]
    elif base == "wezterm":
        argv = [terminal, "start", "--cwd", path, "--", exe, *args]
    else:
        argv = [terminal, "-e", exe, *args]
    subprocess.Popen(argv, cwd=path, start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def _find_linux_terminal() -> str | None:
    for name in ("gnome-terminal", "kitty", "alacritty", "wezterm",
                 "xterm", "konsole"):
        exe = shutil.which(name)
        if exe:
            return exe
    return None


def _launch_windows(path: str, exe: str, args: tuple[str, ...]) -> None:
    # Prefer Windows Terminal, else open the tool directly in its folder.
    wt = shutil.which("wt.exe")
    if wt:
        subprocess.Popen([wt, "-d", path, exe, *args], start_new_session=True)
    else:
        subprocess.Popen([exe, *args], cwd=path, start_new_session=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Picker
# ---------------------------------------------------------------------------

def pick_project(projects: list[dict]) -> dict | None:
    if not projects:
        print("No projects yet. Add one with: launcher.py add /path")
        return None
    if detect_os() == "macos" and shutil.which("osascript"):
        return _pick_macos(projects)
    return _pick_terminal(projects)


def _pick_macos(projects: list[dict]) -> dict | None:
    labels = [f"{p.get('label')}  ({p['path']})" for p in projects]
    list_literal = "{" + ", ".join(_applescript_string(l) for l in labels) + "}"
    script = ("set _c to choose from list " + list_literal +
              ' with prompt "Select a project"')
    proc = subprocess.run(["osascript", "-e", script], capture_output=True,
                          text=True, timeout=60)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    chosen = proc.stdout.strip().splitlines()[0]
    for p in projects:
        if f"{p.get('label')}  ({p['path']})" == chosen:
            return p
    return None


def _pick_terminal(projects: list[dict]) -> dict | None:
    for index, p in enumerate(projects, start=1):
        print(f"{index}. {p.get('label')}  ({p['path']})")
    try:
        choice = input("Choose a number: ").strip()
        index = int(choice) - 1
    except (ValueError, EOFError):
        return None
    if 0 <= index < len(projects):
        return projects[index]
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="codex-workspace-launcher")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("pick", help="Interactive project picker")
    sub.add_parser("list", help="List projects")
    add = sub.add_parser("add", help="Register a project folder")
    add.add_argument("path")
    add.add_argument("--label")
    rem = sub.add_parser("remove", help="Remove a project")
    rem.add_argument("id")
    op = sub.add_parser("open", help="Open a project directly")
    op.add_argument("id")
    op.add_argument("--tool", default="codex")
    op.add_argument("--mode", default="safe", choices=MODES)
    return p


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    registry = Registry()

    if args.command == "list":
        for p in registry.list():
            print(f"{p['id'][:8]}  {p.get('label')}  {p['path']}")
        return 0

    if args.command == "add":
        row = registry.add(args.path, args.label)
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return 0

    if args.command == "remove":
        registry.remove(args.id)
        return 0

    if args.command == "pick":
        projects = discover_projects(registry)
        chosen = pick_project(projects)
        if chosen is None:
            return 1
        launch(chosen["path"], "codex", "safe")
        return 0

    if args.command == "open":
        row = registry.get(args.id)
        if row is None:
            print(f"Unknown project: {args.id}", file=sys.stderr)
            return 2
        launch(row["path"], args.tool, args.mode)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
