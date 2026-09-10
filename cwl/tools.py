"""Tool catalog: AI tools/agents with detection, probing and launch modes.

Each tool is probed for real (binary exists + `--version` runs) and cached.
Tools are divided into:
  - CLI  agents (terminal): launched inside a terminal in the project folder;
  - APP  surfaces (desktop apps): opened directly, folder passed when possible.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

TOOL_ID_PATTERN = "abcdefghijklmnopqrstuvwxyz0123456789_-"


def validate_tool_id(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized or any(c not in TOOL_ID_PATTERN for c in normalized):
        raise ValueError("invalid tool id")
    return normalized


@dataclass(frozen=True)
class ToolReport:
    """Read-only health result for one tool."""

    id: str
    label: str
    state: str            # ready | degraded | missing
    message: str
    executable_path: str | None = None
    version: str | None = None
    description: str = ""
    launch_mode: str = "terminal"   # terminal | app
    probe_kind: str = "version"     # version | files
    launch_arguments: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        return self.state == "ready"

    def display_label(self) -> str:
        status = "ready" if self.ready else "unavailable"
        surface = "APP" if self.launch_mode == "app" else "CLI"
        return f"{surface} · {self.label} · {status}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "state": self.state,
            "message": self.message,
            "executable_path": self.executable_path,
            "version": self.version,
            "description": self.description,
            "launch_mode": self.launch_mode,
            "probe_kind": self.probe_kind,
            "launch_arguments": list(self.launch_arguments),
            "ready": self.ready,
        }

    @staticmethod
    def from_dict(payload: dict) -> "ToolReport":
        return ToolReport(
            id=str(payload.get("id", "")),
            label=str(payload.get("label", "")),
            state=str(payload.get("state", "missing")),
            message=str(payload.get("message", "")),
            executable_path=payload.get("executable_path"),
            version=payload.get("version"),
            description=str(payload.get("description", "")),
            launch_mode=str(payload.get("launch_mode", "terminal")),
            probe_kind=str(payload.get("probe_kind", "version")),
            launch_arguments=tuple(payload.get("launch_arguments", ())),
        )


@dataclass(frozen=True)
class ToolDefinition:
    id: str
    label: str
    command_names: tuple[str, ...] = ()      # candidates on PATH/user bin
    description: str = ""
    probe_kind: str = "version"              # version | files
    launch_mode: str = "terminal"            # terminal | app
    macos_app: str = ""                      # /Applications/<Name>.app (macOS)
    version_args: tuple[str, ...] = ("--version",)
    output_marker: str | None = None
    launch_arguments: tuple[str, ...] = ()
    env: tuple[tuple[str, str], ...] = ()


def _user_bin_candidates(name: str) -> tuple[str, ...]:
    home = Path.home()
    return (str(home / ".local" / "bin" / name), str(home / "bin" / name))


def tool_definitions() -> tuple[ToolDefinition, ...]:
    """Static catalog; candidates are resolved per machine at probe time."""
    return (
        ToolDefinition("codex", "Codex", ("codex", *map(str, _user_bin_candidates("codex"))),
                       "OpenAI Codex CLI", output_marker="codex"),
        ToolDefinition("claude", "Claude", ("claude", *map(str, _user_bin_candidates("claude"))),
                       "Anthropic Claude Code"),
        ToolDefinition("muse", "Muse", ("muse", *map(str, _user_bin_candidates("muse"))),
                       "Meta Muse Code"),
        ToolDefinition("qwen", "Qwen", ("qwen",),
                       "Qwen Code"),
        ToolDefinition("grok", "Grok", ("grok",),
                       "xAI Grok CLI"),
        ToolDefinition("opencode", "OpenCode", ("opencode",),
                       "OpenCode agent"),
        ToolDefinition("gemini", "Gemini", ("gemini",),
                       "Gemini CLI"),
        ToolDefinition("copilot", "Copilot", ("copilot",),
                       "GitHub Copilot CLI"),
        # Desktop apps (macOS: opened via `open -a`; Windows: via start)
        ToolDefinition("codex-app", "Codex App", (), "OpenAI Codex desktop app",
                       probe_kind="files", launch_mode="app",
                       macos_app="Codex"),
        ToolDefinition("claude-app", "Claude App", (), "Anthropic Claude desktop app",
                       probe_kind="files", launch_mode="app",
                       macos_app="Claude"),
    )


def _resolve_command(name: str) -> str | None:
    exe = shutil.which(name)
    if exe:
        return exe
    for candidate in (Path.home() / ".local" / "bin" / name,
                      Path.home() / "bin" / name):
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _command_wrapper(exe: str, args: tuple[str, ...]) -> tuple[list[str], tuple[str, ...]]:
    """Wrap .cmd/.bat/.ps1 shims on Windows so they can run headless."""
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/d", "/c", exe], args
    if os.name == "nt" and exe.lower().endswith(".ps1"):
        return ["powershell.exe", "-NoProfile", "-NonInteractive",
                "-ExecutionPolicy", "Bypass", "-File", exe], args
    return [exe], args


def _macos_app_exists(name: str) -> bool:
    return (Path("/Applications") / (name + ".app")).exists()


def probe_tool(definition: ToolDefinition,
               cached: dict | None = None) -> ToolReport:
    if cached is not None:
        return ToolReport.from_dict(cached)

    if definition.probe_kind == "files":
        if sys.platform == "darwin" and definition.macos_app:
            ok = _macos_app_exists(definition.macos_app)
        else:
            ok = False
        if ok:
            return ToolReport(
                id=definition.id, label=definition.label, state="ready",
                message="Ready", executable_path=None,
                version="desktop app", description=definition.description,
                launch_mode="app", probe_kind="files")
        return ToolReport(
            id=definition.id, label=definition.label, state="missing",
            message="Desktop app not found", description=definition.description,
            launch_mode="app", probe_kind="files")

    exe: str | None = None
    for name in definition.command_names:
        exe = _resolve_command(name)
        if exe:
            break
    if not exe:
        return ToolReport(
            id=definition.id, label=definition.label, state="missing",
            message=f"{definition.label} not found", description=definition.description)

    command, command_args = _command_wrapper(exe, definition.version_args)
    try:
        completed = subprocess.run(
            [*command, *command_args], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=12, check=False)
    except (OSError, subprocess.SubprocessError):
        return ToolReport(
            id=definition.id, label=definition.label, state="degraded",
            message=f"{definition.label} found but does not run",
            executable_path=exe, description=definition.description)

    output = (completed.stdout or completed.stderr).strip()
    if completed.returncode == 0 and (
            definition.output_marker is None
            or definition.output_marker in output.lower()):
        return ToolReport(
            id=definition.id, label=definition.label, state="ready",
            message="Ready", executable_path=exe,
            version=output.splitlines()[0] if output else None,
            description=definition.description,
            launch_arguments=definition.launch_arguments)
    return ToolReport(
        id=definition.id, label=definition.label, state="degraded",
        message=f"{definition.label} found but does not run",
        executable_path=exe, description=definition.description)


def probe_all(registry=None, fresh: bool = False,
              reports_only: bool = False) -> list[ToolReport]:
    """Probe every tool. Uses the registry probe cache unless fresh=True."""
    definitions = tool_definitions()
    results: list[ToolReport] = []
    for definition in definitions:
        cached = None
        if registry is not None and not fresh:
            cached = registry.get_probe(definition.id)
        report = probe_tool(definition, cached=cached)
        if registry is not None and cached is None:
            registry.set_probe(definition.id, report.to_dict())
        results.append(report)
    return results


def tool_by_id(tool_id: str, registry=None) -> ToolReport | None:
    normalized = validate_tool_id(tool_id)
    for definition in tool_definitions():
        if definition.id == normalized:
            cached = registry.get_probe(normalized) if registry else None
            report = probe_tool(definition, cached=cached)
            if registry and cached is None:
                registry.set_probe(normalized, report.to_dict())
            return report
    return None


# -- launch modes ------------------------------------------------------------

MODES: tuple[str, ...] = ("safe", "free", "yolo")

MODE_LABELS: dict[str, str] = {
    "safe": "Normal",
    "free": "No sandbox",
    "yolo": "Full (YOLO)",
}

MODE_DESCRIPTIONS: dict[str, str] = {
    "safe": "Обычный запуск со штатными ограничениями",
    "free": "Без песочницы, подтверждения остаются",
    "yolo": "Полные права без подтверждений — осторожно",
}

# Grounded in each tool's official CLI reference.
MODE_FLAGS: dict[str, dict[str, tuple[str, ...]]] = {
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


def validate_mode_id(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in MODES:
        raise ValueError("invalid mode id")
    return normalized


def mode_flags(tool_id: str, mode: str) -> tuple[str, ...]:
    return MODE_FLAGS.get(tool_id, {}).get(validate_mode_id(mode), ())
