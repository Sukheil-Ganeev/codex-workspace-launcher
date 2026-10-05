# project-refactor-pro

> Суперскилл для комплексного рефакторинга проектов. Один скилл вместо шести.

## Что делает

Управляемый pipeline рефакторинга в 4 фазы: анализ зависимостей, организация файлов, выполнение миграции, синхронизация документации.

## Quick Start

```bash
# Найти проблемы в проекте (read-only)
/project-refactor-pro scan

# Получить план рефакторинга без выполнения
/project-refactor-pro plan

# Полный рефакторинг с подтверждениями на каждом шаге
/project-refactor-pro full
```

## Modes

| Mode | Phases | Destructive? | Description |
|------|--------|-------------|-------------|
| `scan` | Phase 1 | No | Read-only анализ: зависимости, файлы, ссылки, документация |
| `plan` | Phase 1 + 2 | No | Scan + миграционный план с одобрением пользователя |
| `full` | Phase 1-4 | Yes | Полный pipeline: scan, plan, execute, sync |
| `sync` | Phase 4 | Partial | Только синхронизация документации |
| `score` | Phase 1 + report | No | Health score проекта (0-100) |

## Pipeline

```
 SCAN --> PLAN --> EXECUTE --> SYNC
  |        |        |          |
  v        v        v          v
 Analyse  Design   Refactor   Update
 deps,    migration files,    docs,
 files,   plan     move,     CLAUDE.md,
 docs     (approve) rename   changelog
```

## Что объединяет (6 скиллов-доноров)

| # | Скилл | Что взято |
|---|-------|-----------|
| 1 | `data-structure-protocol` | Граф зависимостей (.dsp/), маппинг сущностей |
| 2 | `file-organizer` | Организация файлов, категоризация, naming conventions |
| 3 | `code-sync-cleanup` | Поиск дрейфа код<->документация, мёртвых ссылок |
| 4 | `doc-ops` | Аудит документации, anti-patterns, health score |
| 5 | `docs-optimizer` | DUP-коды, tier-таблица, оптимизация CLAUDE.md |
| 6 | `improve-codebase-architecture` | Deep Modules, архитектурный анализ |

## Flags

- `--focus=files|deps|docs|refs` -- сузить фокус на одну категорию
- `--path=<dir>` -- сканировать только указанную директорию
- `--dry-run` -- показать что будет сделано, но не выполнять
- `--verbose` -- детальный вывод
- `--auto-approve` -- пропустить подтверждения (CI)

## Structure

```
project-refactor-pro/
  SKILL.md              -- Основной файл скилла (workflow)
  README.md             -- Этот файл
  references/
    phase-1-scan.md     -- Полная детализация Phase 1
    phase-2-plan.md     -- Полная детализация Phase 2
    phase-3-execute.md  -- Полная детализация Phase 3
    phase-4-sync.md     -- Полная детализация Phase 4
    cheatsheet.md       -- Quick reference на 1 странице
  parts/                -- Исходные части (build artifacts)
```

## Version

1.0.0
