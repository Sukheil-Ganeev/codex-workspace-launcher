#!/usr/bin/env python3
"""Validate common SKILL.md and agents/openai.yaml problems from an inventory."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SUSPICIOUS_TERMS = [
    "ignore previous instructions",
    "ignore user",
    "do not tell the user",
    "exfiltrate",
    "send token",
    "upload secrets",
    "disable safety",
    "без ведома пользователя",
    "не говори пользователю",
]


def load_inventory(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("skills", [])


def check_agent_yaml(skill_path: Path) -> list[str]:
    issues: list[str] = []
    agent_path = skill_path.parent / "agents" / "openai.yaml"
    if not agent_path.exists():
        return ["missing_openai_yaml"]
    text = agent_path.read_text(encoding="utf-8-sig", errors="replace")
    if "interface:" not in text:
        issues.append("openai_yaml_missing_interface")
    for key in ["display_name", "short_description", "default_prompt"]:
        if key not in text:
            issues.append(f"openai_yaml_missing_{key}")
    return issues


def validate(rows: list[dict]) -> dict:
    issue_rows = []
    for row in rows:
        path = Path(row["path"])
        issues = list(row.get("issues", []))
        description = row.get("description", "")
        text = ""
        if path.exists():
            text = path.read_text(encoding="utf-8-sig", errors="replace").lower()
            issues.extend(check_agent_yaml(path))
        else:
            issues.append("path_missing_now")

        if len(description) > 900:
            issues.append("description_too_long")
        for term in SUSPICIOUS_TERMS:
            if term in text:
                issues.append(f"suspicious_term:{term}")

        issues = sorted(set(issues))
        if issues:
            issue_rows.append({
                "name": row.get("name", ""),
                "source": row.get("source", ""),
                "category": row.get("category", ""),
                "path": row.get("path", ""),
                "issues": issues,
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checked": len(rows),
        "issue_rows": len(issue_rows),
        "issue_counts": dict(Counter(issue for row in issue_rows for issue in row["issues"])),
        "issues": issue_rows,
    }


def write_outputs(report: dict, out_json: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    out_csv = out_json.with_suffix(".csv")
    with out_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "source", "category", "path", "issues"])
        writer.writeheader()
        for row in report["issues"]:
            writer.writerow({**row, "issues": ";".join(row["issues"])})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/skill-routing/skills_inventory.json")
    parser.add_argument("--out", default="data/skill-routing/skills_format_health.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate(load_inventory(Path(args.inventory)))
    write_outputs(report, Path(args.out))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            "checked": report["checked"],
            "issue_rows": report["issue_rows"],
            "issue_counts": report["issue_counts"],
            "out": args.out,
        }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
