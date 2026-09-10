#!/usr/bin/env python3
"""Codex Workspace Launcher — pick a project and open an AI tool in it.

Cross-platform (macOS / Linux / Windows). Python 3.8+, stdlib only.

Commands
--------
  pick                  interactive picker (web UI; --cli for terminal picker)
  list                  registered projects with health status
  add PATH [--label]    register a project folder
  rename ID LABEL       rename a project
  remove ID             remove a project from the list
  open ID               open a project (--tool, --mode, --dry-run)
  tools                 show every AI tool with availability and version
  doctor [ID]           health check for projects and tools
  catalog               projects + tools in one JSON document

Projects can also be auto-discovered from CODEX_WORKSPACE_ROOTS (a
platform-separated list of parent directories to scan).

Nothing personal leaves your machine: the small registry lives in your user
state directory (see cwl/registry.py).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cwl import __version__  # noqa: E402
from cwl.discovery import discover  # noqa: E402
from cwl.doctor import check_workspace  # noqa: E402
from cwl.launch import build_plan, execute  # noqa: E402
from cwl.picker import run_cli_picker, run_web_picker  # noqa: E402
from cwl.registry import Registry  # noqa: E402
from cwl.tools import (MODES, MODE_LABELS, mode_flags, probe_all,  # noqa: E402
                       tool_by_id, validate_mode_id, validate_tool_id)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-workspace",
        description="Codex Workspace Launcher — pick a project and open an "
                    "AI tool in it.")
    parser.add_argument("--version", action="version",
                        version=f"codex-workspace {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    pick = sub.add_parser("pick", help="Interactive picker (web UI)")
    pick.add_argument("--tool", help="Preselect a tool")
    pick.add_argument("--mode", choices=MODES, help="Preselect a mode")
    pick.add_argument("--cli", action="store_true",
                      help="Use the terminal picker instead of the browser")

    lst = sub.add_parser("list", help="List registered projects")
    lst.add_argument("--json", action="store_true")
    lst.add_argument("--fresh", action="store_true",
                     help="Bypass the cached tool probes")

    add = sub.add_parser("add", help="Register a project folder")
    add.add_argument("path")
    add.add_argument("--label", help="Display name")

    rename = sub.add_parser("rename", help="Rename a registered project")
    rename.add_argument("id")
    rename.add_argument("label")

    remove = sub.add_parser("remove", help="Remove a project from the list")
    remove.add_argument("id")

    open_p = sub.add_parser("open", help="Open a project directly")
    open_p.add_argument("id")
    open_p.add_argument("--tool", default="codex", help="Tool/agent to launch")
    open_p.add_argument("--mode", default="safe", choices=MODES)
    open_p.add_argument("--dry-run", action="store_true",
                        help="Print the launch plan without launching")

    tools_p = sub.add_parser("tools", help="List available AI tools")
    tools_p.add_argument("--json", action="store_true")
    tools_p.add_argument("--fresh", action="store_true")

    doctor_p = sub.add_parser("doctor", help="Health check")
    doctor_p.add_argument("id", nargs="?")
    doctor_p.add_argument("--tool", default="codex")
    doctor_p.add_argument("--json", action="store_true")

    catalog_p = sub.add_parser("catalog",
                               help="Projects and tools in one document")
    catalog_p.add_argument("--json", action="store_true")
    catalog_p.add_argument("--fresh", action="store_true")
    return parser


def _tool_id(value: str) -> str | None:
    try:
        return validate_tool_id(value)
    except ValueError:
        return None


def _mode_id(value: str) -> str | None:
    try:
        return validate_mode_id(value)
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    registry = Registry()

    # -- pick ----------------------------------------------------------------
    if args.command == "pick":
        discover(registry)
        if args.cli:
            return run_cli_picker(registry, args.tool, args.mode)
        return run_web_picker(registry, args.tool, args.mode)

    # -- list ----------------------------------------------------------------
    if args.command == "list":
        rows = []
        for workspace in registry.list():
            report = check_workspace(registry, workspace["path"], "codex")
            rows.append({**workspace, "doctor": report.to_dict()})
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                print(f"{row['id'][:8]}  {row['label']}  {row['path']}  "
                      f"{row['doctor']['state']}")
        return 0

    # -- add -------------------------------------------------------------------
    if args.command == "add":
        row = registry.upsert(args.path, args.label)
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return 0

    # -- rename ------------------------------------------------------------------
    if args.command == "rename":
        try:
            row = registry.rename(args.id, args.label)
        except KeyError:
            print(f"Unknown project: {args.id}", file=sys.stderr)
            return 2
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return 0

    # -- remove -----------------------------------------------------------------
    if args.command == "remove":
        try:
            registry.archive(args.id)
        except KeyError:
            print(f"Unknown project: {args.id}", file=sys.stderr)
            return 2
        print("Removed.")
        return 0

    # -- tools -------------------------------------------------------------------
    if args.command == "tools":
        reports = [r.to_dict() for r in probe_all(registry, fresh=args.fresh)]
        if args.json:
            print(json.dumps(reports, ensure_ascii=False, indent=2))
        else:
            for report in reports:
                version = f" ({report['version']})" if report.get("version") else ""
                surface = "APP" if report["launch_mode"] == "app" else "CLI"
                print(f"{report['id']}\t{report['label']}\t{surface}\t"
                      f"{report['state']}\t{report['message']}{version}")
        return 0

    # -- doctor -------------------------------------------------------------------
    if args.command == "doctor":
        tool_id = _tool_id(args.tool)
        if tool_id is None:
            print(f"Invalid tool id: {args.tool}", file=sys.stderr)
            return 2
        workspaces = registry.list()
        if args.id:
            workspace = registry.get(args.id)
            if workspace is None:
                print(f"Unknown project: {args.id}", file=sys.stderr)
                return 2
            workspaces = [workspace]
        payload = [{
            "workspace": workspace,
            "doctor": check_workspace(registry, workspace["path"],
                                      tool_id).to_dict(),
        } for workspace in workspaces]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for item in payload:
                d = item["doctor"]
                print(f"{item['workspace']['label']}: {d['state']} — "
                      f"{d['message']}")
        return 0

    # -- catalog --------------------------------------------------------------------
    if args.command == "catalog":
        discover(registry)
        projects = []
        for workspace in registry.list():
            report = check_workspace(registry, workspace["path"], "codex")
            projects.append({**workspace, "doctor": report.to_dict()})
        payload = {
            "projects": projects,
            "tools": [r.to_dict()
                      for r in probe_all(registry, fresh=args.fresh)],
            "modes": [{"id": m, "label": MODE_LABELS[m]} for m in MODES],
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for row in projects:
                print(f"{row['id'][:8]}  {row['label']}  {row['path']}  "
                      f"{row['doctor']['state']}")
            for tool in payload["tools"]:
                version = f" ({tool['version']})" if tool.get("version") else ""
                print(f"tool: {tool['id']}\t{tool['label']}\t"
                      f"{tool['state']}\t{tool['message']}{version}")
        return 0

    # -- open ------------------------------------------------------------------------
    if args.command == "open":
        tool_id = _tool_id(args.tool)
        mode_id = _mode_id(args.mode)
        if tool_id is None:
            print(f"Invalid tool id: {args.tool}", file=sys.stderr)
            return 2
        if mode_id is None:
            print(f"Invalid mode id: {args.mode}", file=sys.stderr)
            return 2
        workspace = registry.get(args.id)
        if workspace is None:
            print(f"Unknown project: {args.id}", file=sys.stderr)
            return 2
        report = check_workspace(registry, workspace["path"], tool_id)
        if not report.ready:
            print(report.message, file=sys.stderr)
            return 3
        tool = tool_by_id(tool_id, registry)
        plan = build_plan(workspace["path"], tool, mode_id,
                          mode_flags(tool_id, mode_id))
        if args.dry_run:
            print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))
            return 0
        execute(plan)
        registry.mark_opened(workspace["id"], tool_id, mode_id)
        print(f"Opened {tool.label} in {workspace['label']} "
              f"({plan.target}, mode={mode_id})")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
