#!/usr/bin/env python3
"""Build a local skill inventory for Codex/Claude/Gemini style SKILL.md folders."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


HOME = Path.home()

DEFAULT_ROOTS = [
    Path.cwd() / "plugins",
    HOME / ".codex" / "skills",
    HOME / ".codex" / "plugins" / "cache",
    HOME / ".claude" / "skills",
    HOME / ".gemini" / "skills",
    HOME / ".agents" / "skills",
    HOME / "plugins",
    HOME / "AppData" / "Local" / "hermes" / "skills",
    HOME / ".openclaw" / "workspace" / "skills",
    HOME / ".openclaw" / "agents" / "main" / "agent" / "codex-home" / "skills",
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

CATEGORY_RULES = {
    "design_ui": ["design", "ui", "ux", "frontend", "figma", "visual", "interface", "html", "css", "react", "дизайн", "интерфейс", "визуал", "сайт"],
    "docs_ops": ["docs", "documentation", "readme", "changelog", "runbook", "doc", "markdown", "документация", "доки", "отчет"],
    "content_growth": ["content", "copy", "smm", "marketing", "x", "twitter", "post", "brand", "seo", "контент", "пост", "бренд"],
    "security_qa": ["security", "audit", "test", "qa", "review", "threat", "validation", "e2e", "tdd", "verify", "refactoring", "безопасность", "тест", "аудит", "проверка"],
    "agent_automation": ["agent", "skill", "plugin", "mcp", "automation", "workflow", "browser", "агент", "навык", "плагин", "автоматизация"],
    "business_strategy": ["business", "strategy", "market", "customer", "pricing", "gtm", "sales", "product", "бизнес", "стратегия", "продажи"],
    "data_finance": ["data", "sql", "analytics", "finance", "spreadsheet", "excel", "model", "данные", "финансы", "таблица"],
    "devops_backend": ["api", "backend", "cloud", "docker", "deploy", "database", "server", "infra", "сервер", "деплой"],
}


def normalize_text(value: str) -> str:
    return " ".join((value or "").replace("\r", " ").replace("\n", " ").split())


def tokenize(value: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[\wа-яА-ЯёЁ#.+-]{2,}", value or "")}


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    issues: list[str] = []
    if not text.startswith("---"):
        return {}, ["missing_frontmatter"]
    lines = text.splitlines()
    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
    if end is None:
        return {}, ["unterminated_frontmatter"]

    raw = lines[1:end]
    data: dict[str, str] = {}
    key = None
    folded: list[str] = []
    for line in raw:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            if key and folded:
                data[key] = normalize_text(" ".join(folded))
                folded = []
            left, right = line.split(":", 1)
            key = left.strip()
            value = right.strip().strip("'\"")
            if value in {">", "|"}:
                folded = []
            else:
                data[key] = value
                key = None
        elif key:
            folded.append(stripped.strip("'\""))
    if key and folded:
        data[key] = normalize_text(" ".join(folded))

    if not data.get("name"):
        issues.append("missing_name")
    if not data.get("description"):
        issues.append("missing_description")
    return data, issues


def source_for(path: Path) -> str:
    p = str(path).lower()
    if "\\.codex\\skills\\" in p:
        return "codex_user"
    if "\\.codex\\plugins\\cache\\" in p:
        return "codex_plugin_cache"
    if "\\.claude\\skills\\" in p:
        return "claude_user"
    if "\\.gemini\\skills\\" in p:
        return "gemini_user"
    if "\\.agents\\skills\\" in p:
        return "agents_shared"
    if "\\plugins\\" in p and "\\skills\\" in p:
        return "plugin_pack"
    if "\\appdata\\local\\hermes\\skills\\" in p:
        return "hermes_mirror"
    if "\\.openclaw\\" in p:
        return "openclaw_mirror"
    return "other"


def category_for(name: str, description: str) -> str:
    haystack = tokenize(f"{name} {description}")
    scores = {
        category: sum(1 for word in words if word in haystack)
        for category, words in CATEGORY_RULES.items()
    }
    best, score = max(scores.items(), key=lambda item: item[1])
    return best if score else "uncategorized"


def iter_skill_files(roots: Iterable[Path]) -> Iterable[Path]:
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            if "SKILL.md" not in files:
                continue
            path = Path(current) / "SKILL.md"
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            yield path


def build_inventory(roots: list[Path]) -> dict:
    rows = []
    for path in iter_skill_files(roots):
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            meta, issues = parse_frontmatter(text)
        except Exception as exc:  # noqa: BLE001 - inventory should continue.
            meta, issues = {}, [f"read_error:{type(exc).__name__}"]

        folder_name = path.parent.name
        name = normalize_text(meta.get("name") or folder_name)
        description = normalize_text(meta.get("description") or "")
        if name.lower() != folder_name.lower():
            issues.append("name_folder_mismatch")
        if len(description) < 30:
            issues.append("weak_description")

        rows.append(
            {
                "name": name,
                "folder": folder_name,
                "description": description,
                "category": category_for(name, description),
                "source": source_for(path),
                "path": str(path),
                "modified": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                "issues": sorted(set(issues)),
            }
        )

    duplicate_counts = Counter(row["name"].lower() for row in rows)
    for row in rows:
        row["duplicate_count"] = duplicate_counts[row["name"].lower()]
        if row["duplicate_count"] > 1:
            row["issues"] = sorted(set(row["issues"] + ["duplicate_name"]))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roots": [str(root) for root in roots],
        "total": len(rows),
        "source_counts": dict(Counter(row["source"] for row in rows)),
        "category_counts": dict(Counter(row["category"] for row in rows)),
        "issue_counts": dict(Counter(issue for row in rows for issue in row["issues"])),
        "skills": sorted(rows, key=lambda row: (row["name"].lower(), row["source"], row["path"].lower())),
    }


def write_outputs(inventory: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "skills_inventory.json"
    csv_path = out_dir / "skills_inventory.csv"
    summary_path = out_dir / "skills_inventory_summary.md"

    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = ["name", "folder", "description", "category", "source", "path", "modified", "duplicate_count", "issues"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in inventory["skills"]:
            writer.writerow({**row, "issues": ";".join(row["issues"])})

    lines = [
        "# Skills Inventory Summary",
        "",
        f"Generated: `{inventory['generated_at']}`",
        f"Total SKILL.md files: `{inventory['total']}`",
        "",
        "## Sources",
        "",
    ]
    for source, count in sorted(inventory["source_counts"].items()):
        lines.append(f"- `{source}`: `{count}`")
    lines.extend(["", "## Categories", ""])
    for category, count in sorted(inventory["category_counts"].items()):
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(["", "## Issues", ""])
    if inventory["issue_counts"]:
        for issue, count in sorted(inventory["issue_counts"].items()):
            lines.append(f"- `{issue}`: `{count}`")
    else:
        lines.append("- no issues found")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="data/skill-routing")
    parser.add_argument("--root", action="append", default=[])
    args = parser.parse_args()

    roots = [Path(value).expanduser() for value in args.root] if args.root else DEFAULT_ROOTS
    inventory = build_inventory(roots)
    write_outputs(inventory, Path(args.out_dir))
    print(json.dumps({
        "out_dir": str(Path(args.out_dir)),
        "total": inventory["total"],
        "sources": inventory["source_counts"],
        "issues": inventory["issue_counts"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
