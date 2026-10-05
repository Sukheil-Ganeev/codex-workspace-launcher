#!/usr/bin/env python3
"""Create an owner-facing workflow plan from recommended local skills."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import recommend_skills


PROFILE_ORDER = [
    "agent_automation",
    "business_strategy",
    "docs_ops",
    "design_ui",
    "devops_backend",
    "security_qa",
    "content_growth",
    "data_finance",
]

STAGE_LABELS = {
    "agent_automation": "Оркестрация и выбор навыков",
    "business_strategy": "Бизнес-логика и критерии успеха",
    "docs_ops": "Документация и след решений",
    "design_ui": "Дизайн и реализация интерфейса",
    "devops_backend": "Техническая реализация",
    "security_qa": "Проверка качества и рисков",
    "content_growth": "Контент, упаковка и рост",
    "data_finance": "Данные, таблицы и аналитика",
    "uncategorized": "Дополнительные кандидаты",
}

PROFILE_HINTS = {
    "design_ui": ["сайт", "ui", "ux", "дизайн", "frontend", "страница", "панель", "интерфейс"],
    "security_qa": ["проверь", "тест", "qa", "безопасно", "ошибка", "качество", "verify"],
    "docs_ops": ["доки", "документация", "отчет", "зафиксируй", "readme", "runbook"],
    "agent_automation": ["навык", "skills", "plugin", "плагин", "агент", "автоматизация", "workflow"],
    "content_growth": ["контент", "smm", "пост", "twitter", "x", "маркетинг", "бренд"],
    "business_strategy": ["бизнес", "стратегия", "оффер", "продажи", "лиды", "рынок"],
    "data_finance": ["csv", "json", "таблица", "данные", "analytics", "финансы"],
    "devops_backend": ["api", "backend", "сервер", "деплой", "docker", "database"],
}


def detect_profiles(query: str, rows: Iterable[dict]) -> list[str]:
    query_lower = query.lower()
    profiles = {
        row.get("category", "uncategorized")
        for row in rows
        if row.get("category") != "uncategorized"
    }
    for profile, hints in PROFILE_HINTS.items():
        if any(hint in query_lower for hint in hints):
            profiles.add(profile)
    return [profile for profile in PROFILE_ORDER if profile in profiles] + sorted(profiles - set(PROFILE_ORDER))


def stage_profile_for(row: dict, query: str) -> str:
    name = row.get("name", "").lower()
    query_lower = query.lower()
    if name in {"playwright", "playwright-interactive"} and any(word in query_lower for word in ["ui", "ux", "сайт", "дизайн", "проверь", "тест"]):
        return "security_qa"
    if name in {"quality-loop", "e2e-testing", "frontend-testing-debugging"}:
        return "security_qa"
    if name in {"skill-orchestrator-master", "skill-creator", "plugin-creator", "skill-installer"}:
        return "agent_automation"
    return row.get("category", "uncategorized")


def pick_stage_skills(profile: str, ranked: list[dict], max_per_stage: int) -> list[dict]:
    return [row for row in ranked if row.get("_stage_profile", row.get("category")) == profile][:max_per_stage]


def create_plan(query: str, inventory_path: Path, limit: int, max_per_stage: int) -> dict:
    rows = recommend_skills.load_inventory(inventory_path)
    ranked = recommend_skills.recommend(query, rows, limit)
    for row in ranked:
        row["_stage_profile"] = stage_profile_for(row, query)
    profiles = detect_profiles(query, ranked)
    stages = []
    used: set[str] = set()
    for profile in profiles:
        skills = pick_stage_skills(profile, ranked, max_per_stage)
        if not skills:
            continue
        for skill in skills:
            used.add(skill["name"].lower())
        stages.append({
            "stage": STAGE_LABELS.get(profile, profile),
            "profile": profile,
            "skills": [
                {
                    "name": skill["name"],
                    "source": skill["source"],
                    "score": skill["score"],
                    "path": skill["path"],
                    "why": skill["description"][:240],
                }
                for skill in skills
            ],
        })

    extras = [
        skill for skill in ranked
        if skill["name"].lower() not in used
    ][: max(0, limit - sum(len(stage["skills"]) for stage in stages))]

    return {
        "query": query,
        "mode": "complex" if len(stages) > 1 else "simple",
        "open_limit": "Open 1-3 SKILL.md first; open more only when stages require it.",
        "stages": stages,
        "extra_candidates": [
            {
                "name": skill["name"],
                "category": skill["category"],
                "source": skill["source"],
                "score": skill["score"],
                "path": skill["path"],
            }
            for skill in extras
        ],
        "operator_prompt_ru": build_operator_prompt(query, stages),
    }


def build_operator_prompt(query: str, stages: list[dict]) -> str:
    skill_names = []
    for stage in stages:
        skill_names.extend(skill["name"] for skill in stage["skills"])
    selected = ", ".join(dict.fromkeys(skill_names))
    return (
        "Сначала примените skills-routing: определите тип задачи, откройте только нужные SKILL.md, "
        f"начните с: {selected}. Потом выполните задачу и зафиксируйте результат. "
        f"Исходный запрос: {query}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--inventory", default="data/skill-routing/skills_inventory.json")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--max-per-stage", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan = create_plan(args.query, Path(args.inventory), args.limit, args.max_per_stage)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(f"Запрос: {plan['query']}")
        print(f"Режим: {plan['mode']}")
        for index, stage in enumerate(plan["stages"], start=1):
            print(f"\n{index}. {stage['stage']}")
            for skill in stage["skills"]:
                print(f"   - {skill['name']} ({skill['source']}, score={skill['score']})")
                print(f"     {skill['path']}")
        if plan["extra_candidates"]:
            print("\nДополнительно:")
            for skill in plan["extra_candidates"]:
                print(f"   - {skill['name']} ({skill['category']}, score={skill['score']})")
        print("\nГотовый meta-prompt:")
        print(plan["operator_prompt_ru"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
