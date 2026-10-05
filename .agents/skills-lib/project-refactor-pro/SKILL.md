---
name: project-refactor-pro
description: "Skill project-refactor-pro"
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

 +---------+    +---------+    +----------+    +---------+
 |  SCAN   |--->|  PLAN   |--->| EXECUTE  |--->|  SYNC   |
 | Phase 1 |    | Phase 2 |    | Phase 3  |    | Phase 4 |
 +---------+    +---------+    +----------+    +---------+
   Analyse        Design        Refactor        Update
   deps,          migration     files,          docs,
   files,         plan with     move,           CLAUDE.md,
   docs,          user          rename,         changelog,
   health         approval      delete          indexes

 Modes:
   scan ------> Phase 1 only (read-only)
   plan ------> Phase 1 + 2 (read-only)
   full ------> Phase 1 + 2 + 3 + 4 (destructive)
   sync ------> Phase 4 only (docs update)
   score -----> Phase 1 + health report (read-only)
```

**Что объединяет (6 скиллов-доноров):**

1. `data-structure-protocol` -- граф зависимостей (.dsp/), маппинг сущностей
2. `file-organizer` -- организация файлов, категоризация, naming conventions
3. `code-sync-cleanup` -- поиск дрейфа код<->документация, мёртвых ссылок
4. `doc-ops` -- аудит документации, anti-patterns, health score
5. `docs-optimizer` -- DUP-коды, tier-таблица, оптимизация CLAUDE.md
6. `improve-codebase-architecture` -- Deep Modules, архитектурный анализ

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
| `scan` | Phase 1 | No | Read-only анализ: зависимости, файлы, ссылки, документация |
| `plan` | Phase 1 + 2 | No | Scan + миграционный план. Показывает что и куда, ждёт одобрения |
| `full` | Phase 1-4 | Yes | Полный pipeline. Scan, план, выполнение, синхронизация |
| `sync` | Phase 4 | Partial | Только обновление документации: CLAUDE.md, CHANGELOG, INDEX.md |
| `score` | Phase 1 + report | No | Scan + числовая оценка здоровья проекта (0-100) |

---

## Phase 1: SCAN -- Анализ проекта

> Полное сканирование проекта. Результат -- структурированный отчёт о найденных проблемах.
> Детали: `references/phase-1-scan.md`

### Шаги

1. **Инициализация графа зависимостей** -- создать/обновить `.dsp/` через `dsp-cli.py`
2. **Маппинг сущностей** -- обойти проект от entrypoints через DFS по imports; зарегистрировать объекты, функции, связи
3. **Поиск осиротевших файлов** -- файлы без входящих/исходящих связей -> кандидаты на удаление или интеграцию
4. **Обнаружение циклов** -- циклические зависимости -> приоритетные цели рефакторинга
5. **Drift Detection** -- проверка документации против кода по 4 категориям:
   - **STALE** -- документ описывает изменённое/удалённое
   - **GHOST** -- документ ссылается на несуществующий символ
   - **SHADOW** -- код без документации
   - **MISMATCH** -- верная идея, неверная деталь
6. **Поиск дубликатов** -- hash-based, block-based (5+ одинаковых строк), structural
7. **Генерация SCAN Report** -- структурированный отчёт с severity (CRITICAL/HIGH/MEDIUM/LOW)

### Severity

| Level | Criteria |
|-------|----------|
| CRITICAL | Ошибочное поведение при следовании, security hole, потеря данных |
| HIGH | Значительная путаница, потеря времени разработчика |
| MEDIUM | Вводит в заблуждение, но выживаемо с проверкой исходников |
| LOW | Косметика -- старый badge, устаревший screenshot |

### Чеклист выхода

- `.dsp/` граф инициализирован, файлы замаплены
- Orphans и cycles обнаружены
- Drift detection пройден по всем doc-источникам
- Duplicate scan завершён
- SCAN Report сохранён в `{project}/.refactor/scan_report.md`

---

## Phase 2: PLAN -- Миграционный план

> На основе SCAN Report -- конкретный план действий для одобрения.
> Детали: `references/phase-2-plan.md`

### Шаги

1. **Извлечь данные из SCAN Report** -- файлы, проблемы, текущее дерево каталогов
2. **Группировка по назначению** -- code, docs, assets, config, archive, unknown
3. **Целевая структура папок** -- ASCII-дерево, snake_case, макс. 3 уровня вложенности
4. **Таблица перемещений** -- для каждого файла: текущий путь, новый путь, действие (move/rename/archive/delete/merge/keep)
5. **Определить ссылки для обновления** -- HTML src/href, CSS url(), MD links, Python/JS imports, config paths
6. **Архитектурный анализ** -- Deep Modules (Ousterhout): оценить глубину модулей, найти кандидатов на объединение; RFC для тяжёлых рефакторингов (>5 файлов / >500 строк)
7. **Показать план пользователю** -- текущее состояние, целевая структура, таблица перемещений, ссылки для обновления, файлы требующие решения

### Критические правила

- НИКОГДА не выполнять перемещения без явного "да"
- Unknown файлы -- всегда спрашивать
- Удаления показывать отдельным списком
- Архивировать вместо удаления при сомнении
- Git rename detection работает при >50% совпадении содержимого

---

## Phase 3: EXECUTE -- Выполнение рефакторинга

> Пошаговое выполнение одобренного плана.
> Детали: `references/phase-3-execute.md`

### Шаги

1. **Подготовка** -- чистая рабочая директория, отдельная ветка `refactor/restructure-YYYYMMDD`
2. **Создать все целевые папки** -- mkdir -p вся структура ДО начала перемещений
3. **Переместить файлы** -- по одному, без wildcards; при конфликте -- СТОП и вопрос
4. **Обновить ссылки** -- HTML src/href, CSS url(), MD links, Python/JS imports, CLAUDE.md
5. **Удалить дубликаты** -- ТОЛЬКО с явного подтверждения; rmdir для пустых папок
6. **Обновить .dsp/ граф** -- если используется
7. **Создать move_log.md** -- таблица перемещений и обновлённых ссылок

### Правила безопасности

- НИКОГДА не удалять без подтверждения
- Логировать ВСЁ в move_log.md сразу
- При конфликте имён -- остановиться и спросить
- НЕ коммитить автоматически -- дать пользователю проверить diff
- Перемещать инкрементально: группами по 5-10 файлов

### Rollback

- **Через Git** (рекомендуется): `git checkout main && git branch -D refactor/...`
- **Через move_log.md**: обратные перемещения в обратном порядке

---

## Phase 4: SYNC -- Синхронизация документации

> Гарантия что документация отражает новую структуру.
> Детали: `references/phase-4-sync.md`

### Принципы

1. CLAUDE.md = навигационный хаб, не энциклопедия
2. Свежесть > Полнота
3. Archive != Delete -- перемещать в `docs/archive/`
4. Cache-optimized -- статическое вверху CLAUDE.md
5. SSOT -- каждый факт в ОДНОМ файле

### Шаги

1. **Пересканировать .md файлы** -- пути могли измениться после Phase 3
2. **Проверить 20 anti-patterns** -- AP-01..AP-20 (context stuffing, stale docs, orphan docs, code-doc drift...)
3. **Найти дублирование** -- DUP-XX коды; одинаковая строка (>10 слов) в 2+ файлах = SSOT violation
4. **Tier-таблица** -- Essential (в CLAUDE.md), On-demand (docs/), Archive (docs/archive/)
5. **Оптимизировать CLAUDE.md** -- целевой размер 200-250 строк, cache-ordered layout
6. **Обновить служебные файлы** -- INDEX.md, CHANGELOG.md, ISSUES.md, .claudeignore
7. **Drift check** -- все пути в документации -> файлы реально существуют; AP-F0X коды
8. **Health Score** -- (Completeness*0.3 + Efficiency*0.3 + Freshness*0.2 + Structure*0.2), порог >= 3/5
9. **Before/after метрики** -- обязательный вывод: строки, токены, дубли, stale, score

### Что НЕЛЬЗЯ в Phase 4

- Удалять CHANGELOG, ISSUES, WHY-LOG -- журналы растут всегда
- Удалять dormant docs -- пометить `// DORMANT`
- Применять без diff и подтверждения

---

## Output Format

### Mode: `scan`
```
## SCAN Report: {project_name}
- Files analyzed: N
- Issues found: N (critical: N, warning: N, info: N)
### Critical
- [list]
### Warnings
- [list]
### Info
- [list]
```

### Mode: `plan`
```
## Migration Plan: {project_name}
Based on SCAN report (N issues found)
### Step 1: {category}
- [ ] Action 1 (file_a -> file_b)
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
```

---

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
- `--focus=files|deps|docs|refs` -- сузить фокус на одну категорию
- `--path=<dir>` -- сканировать только указанную директорию
- `--dry-run` -- в режиме `full` показать что будет сделано, но не выполнять
- `--verbose` -- детальный вывод для каждого шага
- `--auto-approve` -- пропустить подтверждения (для CI/автоматизации)
