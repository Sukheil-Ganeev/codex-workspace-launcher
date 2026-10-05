#!/usr/bin/env python3
"""Build thin domain-pack manifests without duplicating skill folders."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


PACK_DEFINITIONS = {
    "design-ui-pack": {
        "categories": ["design_ui", "security_qa", "docs_ops"],
        "anchors": [
            "frontend-design",
            "web-design-guidelines",
            "design-an-interface",
            "frontend-app-builder",
            "frontend-patterns",
            "frontend-testing-debugging",
            "e2e-testing",
            "playwright",
            "quality-loop",
            "figma",
            "figma-implement-design",
            "brand-design-skill",
            "brand-guidelines",
            "html-css-справочник",
            "imagegen",
        ],
        "keywords": ["design", "ui", "ux", "frontend", "figma", "interface", "html", "css", "visual", "дизайн", "интерфейс"],
    },
    "docs-ops-pack": {
        "categories": ["docs_ops", "agent_automation"],
        "anchors": [
            "doc-ops",
            "docs:update-docs",
            "docs-optimizer",
            "delivery-docs",
            "changelog-generator",
            "readme-проекты",
            "grill-with-docs",
            "openai-docs",
            "documentation-lookup",
            "create-adr",
            "mermaid",
            "architecture-status",
        ],
        "keywords": ["docs", "documentation", "readme", "changelog", "runbook", "markdown", "docops", "документация", "отчет"],
    },
    "security-qa-pack": {
        "categories": ["security_qa", "devops_backend"],
        "anchors": [
            "quality-loop",
            "e2e-testing",
            "frontend-testing-debugging",
            "codex-security:security-scan",
            "codex-security:threat-model",
            "codex-security:validation",
            "code-review:review-local-changes",
            "code-review:review-pr",
            "integration-guardian",
            "break-trace",
            "architecture-review",
            "security-scan",
            "threat-model",
        ],
        "keywords": ["security", "audit", "test", "qa", "review", "threat", "validation", "e2e", "verify", "безопасность", "аудит", "тест"],
    },
    "content-growth-pack": {
        "categories": ["content_growth", "business_strategy", "design_ui"],
        "anchors": [
            "content-engine",
            "content-strategy",
            "content-trend-researcher",
            "copywriting",
            "copy-editing",
            "social-content",
            "social-media-analyzer",
            "ad-creative",
            "ai-seo",
            "instagram-competitor-analysis",
            "marketing-ideas",
            "marketing-psychology",
            "x-content-growth-master",
            "x-phoenix-score",
        ],
        "keywords": ["content", "copy", "smm", "marketing", "seo", "brand", "post", "twitter", "контент", "пост", "маркетинг"],
    },
    "agent-automation-pack": {
        "categories": ["agent_automation", "docs_ops", "security_qa"],
        "anchors": [
            "skill-orchestrator-master",
            "skill-creator",
            "skill-installer",
            "plugin-creator",
            "agent-factory",
            "agent-talk",
            "browser-use-cli",
            "browser-use-ops",
            "customaize-agent:prompt-engineering",
            "customaize-agent:create-agent",
            "customaize-agent:create-skill",
            "customaize-agent:test-skill",
            "context-engineering-advisor",
            "codex-cli-bridge",
            "handoff",
        ],
        "keywords": ["agent", "skill", "plugin", "mcp", "automation", "workflow", "browser", "агент", "навык", "плагин"],
    },
    "business-strategy-pack": {
        "categories": ["business_strategy", "content_growth", "data_finance"],
        "anchors": [
            "business-health-diagnostic",
            "company-research",
            "competitive-analysis",
            "customer-research",
            "customer-journey-map",
            "jobs-to-be-done",
            "market-research",
            "pricing-strategy",
            "product-strategy-session",
            "roadmap-planning",
            "sales-enablement",
            "revops",
            "gtm-strategy",
            "lean-canvas",
        ],
        "keywords": ["business", "strategy", "market", "customer", "sales", "pricing", "product", "gtm", "бизнес", "стратегия"],
    },
}

SOURCE_RANK = {
    "codex_user": 0,
    "plugin_pack": 1,
    "codex_plugin_cache": 2,
    "claude_user": 3,
    "gemini_user": 4,
    "agents_shared": 5,
    "hermes_mirror": 8,
    "openclaw_mirror": 9,
}


def load_inventory(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")).get("skills", [])


def quality_penalty(row: dict) -> int:
    issues = set(row.get("issues", []))
    penalty = 0
    if "missing_description" in issues:
        penalty += 50
    if "weak_description" in issues:
        penalty += 20
    if "missing_frontmatter" in issues:
        penalty += 40
    if "name_folder_mismatch" in issues:
        penalty += 3
    return penalty


def text_tokens(row: dict) -> set[str]:
    text = " ".join([row.get("name", ""), row.get("description", ""), row.get("category", "")]).lower()
    raw = []
    current = []
    for char in text:
        if char.isalnum() or char in {"-", "_", ":"}:
            current.append(char)
        elif current:
            raw.append("".join(current))
            current = []
    if current:
        raw.append("".join(current))
    return set(raw)


def canonicalize(rows: list[dict]) -> dict[str, dict]:
    by_name: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_name[row["name"].lower()].append(row)
    canonical = {}
    for name, variants in by_name.items():
        canonical[name] = sorted(
            variants,
            key=lambda row: (
                quality_penalty(row),
                SOURCE_RANK.get(row.get("source", "other"), 99),
                row.get("path", "").lower(),
            ),
        )[0]
    return canonical


def pack_score(row: dict, definition: dict) -> int:
    name = row["name"].lower()
    anchors = [value.lower() for value in definition["anchors"]]
    categories = definition["categories"]
    keywords = {value.lower() for value in definition["keywords"]}
    tokens = text_tokens(row)
    score = 0

    if name in anchors:
        score += 1000 - anchors.index(name)
    if row.get("category") in categories:
        score += 120 - categories.index(row["category"]) * 20
    score += len(tokens & keywords) * 18
    if any(keyword in name for keyword in keywords):
        score += 20
    score -= quality_penalty(row)
    score -= SOURCE_RANK.get(row.get("source", "other"), 99)
    return score


def build_pack(name: str, definition: dict, rows: list[dict], limit: int) -> dict:
    categories = definition["categories"]
    canonical = canonicalize(rows)
    selected = sorted(
        canonical.values(),
        key=lambda row: (
            -pack_score(row, definition),
            SOURCE_RANK.get(row.get("source", "other"), 99),
            row["name"].lower(),
        ),
    )
    selected = [row for row in selected if pack_score(row, definition) > 0][:limit]
    return {
        "name": name,
        "kind": "thin-routing-pack",
        "categories": categories,
        "anchors": definition["anchors"],
        "skill_count": len(selected),
        "skills": [
            {
                "name": row["name"],
                "category": row["category"],
                "source": row["source"],
                "path": row["path"],
                "pack_score": pack_score(row, definition),
                "issues": row.get("issues", []),
                "description": row["description"],
            }
            for row in selected
        ],
    }


def write_markdown(packs: list[dict], path: Path) -> None:
    lines = [
        "# Domain Skill Packs",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "These are thin routing packs: they point to canonical skills instead of copying every folder.",
        "",
    ]
    for pack in packs:
        lines.extend([f"## {pack['name']}", "", f"Skill count: `{pack['skill_count']}`", ""])
        for skill in pack["skills"]:
            lines.append(f"- `{skill['name']}` [{skill['category']}, {skill['source']}] — `{skill['path']}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/skill-routing/skills_inventory.json")
    parser.add_argument("--out", default="data/skill-routing/domain_skill_packs.json")
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()

    rows = load_inventory(Path(args.inventory))
    packs = [build_pack(name, definition, rows, args.limit) for name, definition in PACK_DEFINITIONS.items()]
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pack_count": len(packs),
        "packs": packs,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(packs, out.with_suffix(".md"))
    print(json.dumps({"out": str(out), "packs": len(packs)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
