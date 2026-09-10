"""Health checks: is a project folder ready for a given tool?"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .launch import find_terminal, os_name
from .registry import Registry
from .tools import ToolReport, tool_by_id


@dataclass(frozen=True)
class DoctorReport:
    state: str          # ready | degraded | missing | blocked
    message: str
    workspace_exists: bool
    workspace_readable: bool
    tool_id: str
    tool_label: str
    executable_path: str | None = None
    tool_version: str | None = None
    terminal: str | None = None
    launch_mode: str = "terminal"
    tool_arguments: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        return self.state == "ready"

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "message": self.message,
            "workspace_exists": self.workspace_exists,
            "workspace_readable": self.workspace_readable,
            "tool_id": self.tool_id,
            "tool_label": self.tool_label,
            "executable_path": self.executable_path,
            "tool_version": self.tool_version,
            "terminal": self.terminal,
            "launch_mode": self.launch_mode,
            "tool_arguments": list(self.tool_arguments),
            "ready": self.ready,
        }


def check_workspace(registry: Registry, path: str | Path,
                    tool_id: str = "codex") -> DoctorReport:
    """Check one project folder for one tool."""
    workspace = Path(path).expanduser()
    tool: ToolReport | None = tool_by_id(tool_id, registry)
    if tool is None:
        tool = ToolReport(id=tool_id, label=tool_id.title(), state="missing",
                          message="Unknown tool")

    exists = workspace.is_dir()
    readable = exists and os.access(workspace, os.R_OK | os.X_OK)
    terminal = None
    if tool.launch_mode == "terminal":
        terminal = find_terminal()

    if not exists:
        state, message = "missing", "Project folder not found"
    elif not readable:
        state, message = "blocked", "No read/execute permission on the folder"
    elif not tool.ready:
        state, message = "degraded", tool.message
    elif tool.launch_mode == "terminal" and not terminal:
        state, message = "degraded", "No terminal found on this system"
    else:
        state = "ready"
        message = ("Ready — folder is passed to the desktop app"
                   if tool.launch_mode == "app" else "Ready to launch")

    return DoctorReport(
        state=state, message=message,
        workspace_exists=exists, workspace_readable=readable,
        tool_id=tool.id, tool_label=tool.label,
        executable_path=tool.executable_path,
        tool_version=tool.version,
        terminal=terminal,
        launch_mode=tool.launch_mode,
        tool_arguments=tool.launch_arguments,
    )
