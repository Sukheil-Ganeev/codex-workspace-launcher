#!/usr/bin/env python3
"""Recommend local skills for a user request from a generated inventory."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_INVENTORY = Path("data/skill-routing/skills_inventory.json")
SOURCE_PRIORITY = {
    "codex_user": 1.0,
    "plugin_pack": 0.9,
    "codex_plugin_cache": 0.8,
    "claude_user": 0.65,
    "gemini_user": 0.6,
    "agents_shared": 0.55,
    "hermes_mirror": 0.35,
    "openclaw_mirror": 0.3,
    "other": 0.2,
}

PROFILE_HINTS = {
    "design_ui": ["design", "ui", "ux", "frontend", "figma", "сайт", "интерфейс", "дизайн", "визуал"],
    "docs_ops": ["docs", "documentation", "readme", "docops", "документация", "доки", "отчет"],
    "content_growth": ["content", "copy", "smm", "x", "twitter", "пост", "контент", "маркетинг"],
    "security_qa": ["security", "audit", "test", "qa", "review", "безопасность", "тест", "аудит"],
    "agent_automation": ["agent", "skill", "plugin", "mcp", "automation", "навык", "плагин", "агент"],
    "business_strategy": ["business", "strategy", "market", "customer", "sales", "бизнес", "стратегия"],
    "data_finance": ["data", "sql", "analytics", "finance", "csv", "json", "таблица", "данные"],
    "devops_backend": ["api", "backend", "cloud", "docker", "deploy", "server", "сервер"],
}


def tokens(text: str) -> set[str]:
    return {part.lower() for part in re.findall(r"[\wа-яА-ЯёЁ#.+-]{3,}", text or "")}


def load_inventory(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("skills", [])


def score_skill(query: str, row: dict) -> float:
    query_tokens = tokens(query)
    text_tokens = tokens(" ".join([row.get("name", ""), row.get("description", ""), row.get("category", "")]))
    overlap = len(query_tokens & text_tokens)
    score = overlap * 5

    query_lower = query.lower()
    if row.get("name", "").lower() in query_lower:
        score += 20
    for profile, hints in PROFILE_HINTS.items():
        hint_tokens = {hint for hint in hints if " " not in hint}
        phrase_hints = [hint for hint in hints if " " in hint]
        if (query_tokens & hint_tokens or any(hint in query_lower for hint in phrase_hints)) and row.get("category") == profile:
            score += 10
    if "weak_description" in row.get("issues", []):
        score -= 4
    if "missing_description" in row.get("issues", []):
        score -= 10
    score += SOURCE_PRIORITY.get(row.get("source", "other"), 0) * 3

    name_lower = row.get("name", "").lower()
    category = row.get("category")
    if {"навык", "skills", "skill", "плагин", "plugin", "каталог", "синхронизируй", "yaml"} & query_tokens:
        if "skill-orchestrator" in name_lower:
            score += 45
        if name_lower in {"skill-creator", "skill-installer", "plugin-creator"}:
            score += 18
    if {"сайт", "ui", "ux", "дизайн", "frontend", "web"} & query_tokens:
        if name_lower in {"frontend-design", "frontend-app-builder", "web-design-guidelines"}:
            score += 24
        if name_lower in {"frontend-testing-debugging", "e2e-testing", "playwright", "quality-loop"}:
            score += 14
        if name_lower.startswith("api-") and "api" not in query_tokens:
            score -= 12
    if {"тесты", "тест", "qa", "verify", "проверь", "проверка"} & query_tokens:
        if name_lower in {"quality-loop", "e2e-testing", "frontend-testing-debugging", "playwright"}:
            score += 18
    if {"документация", "доки", "отчет", "docs", "docops"} & query_tokens:
        if name_lower in {"doc-ops", "docs:update-docs", "docs-optimizer", "delivery-docs"} or category == "docs_ops":
            score += 16
    if {"максимально", "качественно", "quality"} & query_tokens:
        if name_lower in {"quality-loop", "skill-orchestrator-master", "engineering-advisor"}:
            score += 14
    return score


def recommend(query: str, rows: list[dict], limit: int) -> list[dict]:
    best_by_name: dict[str, dict] = {}
    for row in rows:
        score = score_skill(query, row)
        if score <= 0:
            continue
        key = row.get("name", "").lower()
        candidate = {**row, "score": round(score, 2)}
        previous = best_by_name.get(key)
        if previous is None or candidate["score"] > previous["score"]:
            best_by_name[key] = candidate
    ranked = sorted(best_by_name.values(), key=lambda row: (-row["score"], row["name"].lower()))
    return ranked[:limit]


def group_by_category(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row.get("category", "uncategorized")].append(row)
    return dict(groups)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    if not inventory_path.exists():
        raise SystemExit(f"Inventory not found: {inventory_path}. Run build_skill_inventory.py first.")

    rows = load_inventory(inventory_path)
    ranked = recommend(args.query, rows, args.limit)
    result = {
        "query": args.query,
        "count": len(ranked),
        "recommendations": ranked,
        "by_category": group_by_category(ranked),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Query: {args.query}")
        for index, row in enumerate(ranked, start=1):
            print(f"{index}. {row['name']} [{row['category']}, {row['source']}, score={row['score']}]")
            print(f"   {row['description']}")
            print(f"   {row['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
