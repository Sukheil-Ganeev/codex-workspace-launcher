# docs-optimizer

Комбинированный скилл оптимизации документации проектов для Claude Code.

## Что делает
- Аудит документации (размер, дублирование, актуальность)
- Оптимизация CLAUDE.md (сжатие, cache-ordering, single source of truth)
- Tiered loading (essential/on-demand/archive)
- Cross-file deduplication
- Anti-pattern detection (20 паттернов)

## Как использовать
В Claude Code набрать `/docs-optimizer` или активировать скилл.

Режимы:
- `analyze` — аудит-отчёт (по умолчанию)
- `optimize` — оптимизированная версия CLAUDE.md
- `apply` — применить изменения
- `audit` — полный аудит экосистемы
- `tiered` — классификация по тирам + .claudeignore

## Источники
Создан на основе:
- kojott/claude-docu-optimizer (15 anti-patterns, metrics, cache ordering)
- alonw0/llm-docs-optimizer (question-driven, transformation patterns)
- nadimtuhin/claude-token-optimizer (tiered loading, .claudeignore)
- Собственный опыт аудита vipdxbrus-website (43K строк -> 28% полезного)

## Файлы
- `SKILL.md` — основная логика
- `references/anti-patterns.md` — полный список 20 анти-паттернов
- `references/templates.md` — шаблоны CLAUDE.md и docs/ структуры
- `references/cheatsheet.md` — быстрая справка
