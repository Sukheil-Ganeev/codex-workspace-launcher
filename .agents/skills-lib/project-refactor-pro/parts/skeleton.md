---
name: project-refactor-pro
description: >-
  Суперскилл для рефакторинга проектов. Объединяет анализ зависимостей, организацию файлов,
  синхронизацию документации. 4 фазы: SCAN->PLAN->EXECUTE->SYNC. 5 режимов: scan, plan, full, sync, score.
  Триггеры: рефакторинг проекта, наведи порядок, организуй файлы, найди мёртвые ссылки,
  почисти проект, project refactor, reorganize, file structure, dead references, orphaned files, code drift
version: 1.0.0
---

# project-refactor-pro

> Суперскилл для комплексного рефакторинга проектов.
> Один скилл вместо шести: анализ зависимостей, организация файлов, синхронизация документации.

## Overview

**Философия:** Рефакторинг -- это не разовое действие, а управляемый pipeline.
Каждый проект со временем накапливает дрейф: мёртвые ссылки, осиротевшие файлы,
рассинхронизированная документация, устаревшие зависимости. `project-refactor-pro`
превращает хаос в порядок за 4 последовательные фазы.

**Принцип:** Сначала понять (SCAN), потом спланировать (PLAN), потом сделать (EXECUTE),
потом синхронизировать всё вокруг (SYNC). Никогда не менять код без плана.
Никогда не планировать без полной картины.

```
 Pipeline:

 ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
 │  SCAN   │───>│  PLAN   │───>│ EXECUTE  │───>│  SYNC   │
 │ Phase 1 │    │ Phase 2 │    │ Phase 3  │    │ Phase 4 │
 └─────────┘    └─────────┘    └──────────┘    └─────────┘
   Analyse        Design        Refactor        Update
   deps,          migration     files,          docs,
   files,         plan with     move,           CLAUDE.md,
   docs,          user          rename,         changelog,
   health         approval      delete          indexes

 Modes:
   scan ──────> Phase 1 only (read-only)
   plan ──────> Phase 1 + 2 (read-only)
   full ──────> Phase 1 + 2 + 3 + 4 (destructive)
   sync ──────> Phase 4 only (docs update)
   score ─────> Phase 1 + health report (read-only)
```

**Что объединяет:**
1. Анализ зависимостей и ссылок (мёртвые imports, broken refs)
2. Файловая организация (orphaned files, naming conventions)
3. Документация (CLAUDE.md drift, stale indexes)
4. Code health scoring (метрики порядка проекта)
5. Миграционные планы (что куда двигать, переименовывать)
6. Post-refactor sync (обновление всего окружения)

## When to Use

| Trigger (user says) | Mode | What happens |
|---------------------|------|-------------|
| "рефакторинг проекта" | `full` | Полный pipeline SCAN->PLAN->EXECUTE->SYNC |
| "наведи порядок" | `full` | Полный pipeline с фокусом на файловую структуру |
| "организуй файлы" | `plan` | Сканирование + план реорганизации (без выполнения) |
| "найди мёртвые ссылки" | `scan` | Только анализ: битые ссылки, imports, refs |
| "почисти проект" | `full` | Полный pipeline с фокусом на удаление мусора |
| "project refactor" | `full` | Full pipeline SCAN->PLAN->EXECUTE->SYNC |
| "reorganize" | `plan` | Scan + plan (no execution) |
| "file structure" | `scan` | Analyse current file structure, report issues |
| "dead references" | `scan` | Find broken links, orphaned files, stale imports |
| "orphaned files" | `scan` | Find files not referenced anywhere |
| "code drift" | `score` | Health score: how far has the project drifted |
| "синхронизируй документацию" | `sync` | Phase 4 only: update all docs to match current state |
| "оценка проекта" / "health check" | `score` | Phase 1 + health score report |

## Modes

| Mode | Phases | Destructive? | Description |
|------|--------|-------------|-------------|
| `scan` | Phase 1 | No | Read-only анализ: зависимости, файлы, ссылки, документация. Выдаёт отчёт о проблемах |
| `plan` | Phase 1 + 2 | No | Scan + миграционный план. Показывает что и куда двигать, ждёт одобрения |
| `full` | Phase 1-4 | Yes | Полный pipeline. Scan, план, выполнение (с подтверждениями), синхронизация документации |
| `sync` | Phase 4 | Partial | Только обновление документации: CLAUDE.md, CHANGELOG, INDEX.md, README |
| `score` | Phase 1 + report | No | Scan + числовая оценка здоровья проекта (0-100) с разбивкой по категориям |

## Phase Overview

### Phase 1: SCAN -- Анализ проекта

Полное сканирование проекта: файловая структура, зависимости, ссылки между файлами,
состояние документации. Результат -- структурированный отчёт о найденных проблемах.

[SEE references/phase-1-scan.md for details]

### Phase 2: PLAN -- Миграционный план

На основе результатов SCAN формируется план действий: что переименовать, переместить,
удалить, объединить. План показывается пользователю для одобрения перед выполнением.

[SEE references/phase-2-plan.md for details]

### Phase 3: EXECUTE -- Выполнение рефакторинга

Пошаговое выполнение одобренного плана. Каждая группа изменений -- отдельный шаг
с подтверждением. Файлы перемещаются, переименовываются, ссылки обновляются.

[SEE references/phase-3-execute.md for details]

### Phase 4: SYNC -- Синхронизация документации

Обновление всей документации проекта: CLAUDE.md, CHANGELOG.md, INDEX.md, README.md,
и любых других индексных файлов. Гарантирует что документация отражает текущее состояние.

[SEE references/phase-4-sync.md for details]

## Output Format

### Mode: `scan`
```
## SCAN Report: {project_name}
- Files analyzed: N
- Issues found: N (critical: N, warning: N, info: N)

### Critical
- [list of critical issues]

### Warnings
- [list of warnings]

### Info
- [list of informational findings]
```

### Mode: `plan`
```
## Migration Plan: {project_name}
Based on SCAN report (N issues found)

### Step 1: {category}
- [ ] Action 1 (file_a -> file_b)
- [ ] Action 2 (delete orphaned_file)
...

### Step 2: {category}
...

Awaiting approval before execution.
```

### Mode: `full`
```
## Refactor Complete: {project_name}

### SCAN: N issues found
### PLAN: N steps planned
### EXECUTE: N/N steps completed
### SYNC: N docs updated

### Summary of changes
- Moved: N files
- Renamed: N files
- Deleted: N files
- Updated refs: N files
- Docs synced: N files
```

### Mode: `sync`
```
## Documentation Sync: {project_name}
- CLAUDE.md: updated (N changes)
- CHANGELOG.md: updated
- INDEX.md: updated (N entries)
- Other: [list]
```

### Mode: `score`
```
## Project Health Score: {project_name}

Overall: NN/100

| Category           | Score | Issues |
|--------------------|-------|--------|
| File organization  | NN/20 | N      |
| Dependencies       | NN/20 | N      |
| Documentation sync | NN/20 | N      |
| Naming conventions | NN/20 | N      |
| Dead references    | NN/20 | N      |

Top 3 recommendations:
1. ...
2. ...
3. ...
```

## Quick Reference

```bash
# Read-only analysis
/project-refactor-pro scan

# Scan + migration plan (no changes)
/project-refactor-pro plan

# Full pipeline (with confirmations)
/project-refactor-pro full

# Update docs only
/project-refactor-pro sync

# Health score
/project-refactor-pro score
```

**Flags:**
- `--focus=files|deps|docs|refs` -- сузить фокус анализа на одну категорию
- `--path=<dir>` -- сканировать только указанную директорию (по умолчанию -- весь проект)
- `--dry-run` -- в режиме `full` показать что будет сделано, но не выполнять
- `--verbose` -- детальный вывод для каждого шага
- `--auto-approve` -- пропустить подтверждения (для CI/автоматизации)
