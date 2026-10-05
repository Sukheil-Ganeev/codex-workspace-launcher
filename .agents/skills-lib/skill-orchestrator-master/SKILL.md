---
name: skill-orchestrator-master
description: Русский meta-skill/router для больших локальных библиотек навыков. Use for any non-trivial task when the user asks to use skills, plugins, subagents, maximum quality, plan a complex workflow, choose the right skill, create a skill catalog, validate SKILL.md/frontmatter, sync skills between Codex/Claude/Gemini/Grok/Cursor, build thematic skill packs, or when the user is unsure which local skills should apply.
---

# Skill Orchestrator Master

## Зачем включаться

Пользователь не должен помнить тысячу названий навыков и правильные trigger-слова. Твоя задача - сначала коротко распознать тип работы, выбрать 1-5 подходящих навыков, объяснить порядок, а потом выполнять задачу.

Не превращай каждую мелочь в бюрократию. Для простого вопроса ответь напрямую. Для сложной задачи включай routing.

## Быстрый рабочий цикл

1. Классифицируй задачу:
   - UI/дизайн;
   - код/архитектура;
   - тесты/QA/безопасность;
   - документы/docops;
   - контент/SMM/бренд;
   - исследование/стратегия;
   - agent-system/skills/plugins/automation;
   - эксплуатация/runbook/backup.
2. Если есть актуальный индекс, подбери кандидатов:

```powershell
python .\plugins\skills-orchestrator\skills\skill-orchestrator-master\scripts\recommend_skills.py --query "USER_REQUEST" --limit 8
```

3. Для сложной задачи строй не просто список skills, а порядок работы:

```powershell
python .\plugins\skills-orchestrator\skills\skill-orchestrator-master\scripts\plan_skill_workflow.py --query "USER_REQUEST"
```

4. Если индекс устарел или отсутствует, пересобери:

```powershell
python .\plugins\skills-orchestrator\skills\skill-orchestrator-master\scripts\build_skill_inventory.py --out-dir .\data\skill-routing
```

5. Открой только 1-3 `SKILL.md` из выбранных навыков. Больше открывай только если задача явно многослойная.
6. Скажи пользователю одной строкой: какие навыки используются и зачем.
7. Выполни работу, проверь результат, важные решения сохрани в `.md`/`.json`.

## Правила выбора

- Главный сигнал - `description` из frontmatter: именно она чаще всего решает, активируется ли навык.
- При равных условиях выбирай навык из пользовательского корня `C:\Users\londo\.codex\skills`, затем официальные/curated plugin skills, затем зеркала Claude/Gemini/OpenClaw.
- Если есть несколько похожих навыков, выбирай самый конкретный под задачу, а общий навык оставляй как вспомогательный.
- Для UI задач почти всегда проверяй не только дизайн-навык, но и тест/visual QA навык.
- Для больших задач с "максимально качественно" добавляй planning/checklist/docops слой.
- Для небезопасных навыков, внешних установок и неизвестных GitHub источников сначала делай provenance/security check.

## Форматы платформ

Используй `references/platform-format-matrix.md`, когда нужно переносить навыки между Codex, Claude, Gemini, Cursor, Grok или OpenClaw.

Коротко:

- Codex/Claude: `SKILL.md` с YAML frontmatter `name` и `description`.
- Codex UI metadata: `agents/openai.yaml` с `interface.display_name`, `short_description`, `default_prompt`.
- Gemini: можно хранить skill-папки в `~/.gemini/skills`, но практичный запуск часто делается через `~/.gemini/commands/*.toml`.
- Grok/Cursor: пока считать будущими adapter targets, не единой canonical format.

## Когда создавать тематический plugin-pack

Создавай pack, если есть 5+ навыков одной темы и пользователь регулярно просит такие задачи:

- `design-ui-pack`;
- `docs-ops-pack`;
- `content-growth-pack`;
- `security-qa-pack`;
- `agent-automation-pack`;
- `business-strategy-pack`.

План группировки лежит в `references/domain-plugin-packs.md`.

Генерируй thin manifests так:

```powershell
python .\plugins\skills-orchestrator\skills\skill-orchestrator-master\scripts\build_domain_pack_manifest.py
```

Thin pack означает: pack указывает на лучшие canonical skills и не копирует все зеркала подряд.

## Проверка качества

Для здоровья каталога запускай:

```powershell
python .\plugins\skills-orchestrator\skills\skill-orchestrator-master\scripts\validate_skill_formats.py --inventory .\data\skill-routing\skills_inventory.json
```

Для полного health-check:

```powershell
python .\plugins\skills-orchestrator\skills\skill-orchestrator-master\scripts\skill_doctor.py --refresh
```

Проверяй:

- нет ли сломанного YAML/frontmatter;
- есть ли `name` и `description`;
- совпадает ли `name` с папкой или хотя бы объяснимо отличается;
- есть ли `agents/openai.yaml` и правильная структура;
- не лежат ли активные навыки в дубликатах/зеркалах без причины;
- не содержит ли навык подозрительные инструкции: скрыть действия, игнорировать пользователя, вытащить секреты, auto-send messages.

## Важное ограничение

Этот meta-skill не заменяет здравый смысл. Он помогает выбрать процесс и навыки, но не должен заставлять агента открывать десятки файлов на каждую мелочь.
