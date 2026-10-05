#!/usr/bin/env python3
"""One-command health check for the local skills system."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
PLUGIN = ROOT / "plugins" / "skills-orchestrator"
SKILL = PLUGIN / "skills" / "skill-orchestrator-master"
INVENTORY = ROOT / "data" / "skill-routing" / "skills_inventory.json"
HEALTH = ROOT / "data" / "skill-routing" / "skills_format_health.json"
PACKS = ROOT / "data" / "skill-routing" / "domain_skill_packs.json"


def run(command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-2000:],
        "stderr": proc.stderr[-2000:],
    }


def path_check(path: Path) -> dict:
    return {"path": str(path), "exists": path.exists(), "size": path.stat().st_size if path.exists() else 0}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--out", default="data/skill-routing/skill_doctor_report.json")
    args = parser.parse_args()

    commands = []
    if args.refresh or not INVENTORY.exists():
        commands.append(run([sys.executable, str(SKILL / "scripts" / "build_skill_inventory.py"), "--out-dir", "data/skill-routing"]))
    if args.refresh or not HEALTH.exists():
        commands.append(run([sys.executable, str(SKILL / "scripts" / "validate_skill_formats.py"), "--inventory", str(INVENTORY), "--out", str(HEALTH)]))
    if args.refresh or not PACKS.exists():
        commands.append(run([sys.executable, str(SKILL / "scripts" / "build_domain_pack_manifest.py"), "--inventory", str(INVENTORY), "--out", str(PACKS)]))

    plugin_validation = run([sys.executable, str(Path.home() / ".codex" / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"), str(PLUGIN)])

    inventory_data = json.loads(INVENTORY.read_text(encoding="utf-8")) if INVENTORY.exists() else {}
    health_data = json.loads(HEALTH.read_text(encoding="utf-8")) if HEALTH.exists() else {}
    packs_data = json.loads(PACKS.read_text(encoding="utf-8")) if PACKS.exists() else {}

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if plugin_validation["returncode"] == 0 and INVENTORY.exists() and HEALTH.exists() else "warning",
        "paths": {
            "plugin": path_check(PLUGIN),
            "skill": path_check(SKILL / "SKILL.md"),
            "inventory": path_check(INVENTORY),
            "health": path_check(HEALTH),
            "domain_packs": path_check(PACKS),
            "codex_install": path_check(Path.home() / ".codex" / "skills" / "skill-orchestrator-master" / "SKILL.md"),
            "claude_install": path_check(Path.home() / ".claude" / "skills" / "skill-orchestrator-master" / "SKILL.md"),
            "gemini_install": path_check(Path.home() / ".gemini" / "skills" / "skill-orchestrator-master" / "SKILL.md"),
            "gemini_command": path_check(Path.home() / ".gemini" / "commands" / "skills-orchestrator" / "route.toml"),
        },
        "inventory": {
            "total": inventory_data.get("total"),
            "source_counts": inventory_data.get("source_counts"),
            "issue_counts": inventory_data.get("issue_counts"),
        },
        "format_health": {
            "checked": health_data.get("checked"),
            "issue_rows": health_data.get("issue_rows"),
            "issue_counts": health_data.get("issue_counts"),
        },
        "domain_packs": {
            "pack_count": packs_data.get("pack_count"),
            "packs": [pack.get("name") for pack in packs_data.get("packs", [])],
        },
        "plugin_validation": plugin_validation,
        "commands": commands,
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "inventory_total": report["inventory"]["total"],
        "format_issue_rows": report["format_health"]["issue_rows"],
        "domain_packs": report["domain_packs"]["pack_count"],
        "out": str(out),
    }, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
