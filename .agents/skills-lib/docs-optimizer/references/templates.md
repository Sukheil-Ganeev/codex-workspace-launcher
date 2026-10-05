# Templates: шаблоны документации

Готовые шаблоны для оптимизированной документации.

---

## A) Оптимальная структура CLAUDE.md (cache-optimized)

Порядок секций оптимизирован для prompt caching: статика сверху (кэшируется), динамика внизу (не ломает кэш).

```markdown
# Project Name

## Quick Reference                    <- STATIC (кэшируется первым)
[Однострочное описание проекта]
[Стек, версия, URL]

### Ключевые команды
npm run dev              # Dev-сервер
npm run build            # Production-сборка
npm run typecheck        # Проверка типов
npm test                 # Тесты

## Architecture                       <- STATIC
[3-5 bullets: основные папки, модули, паттерны]
[Ссылка на docs/COMPONENT-LIBRARY.md для деталей]

| Папка | Назначение |
|-------|-----------|
| src/components/ | UI-компоненты |
| src/data/ | Данные и типы |
| src/lib/ | Утилиты |

## Conventions                        <- STATIC
[Стиль кода, именование, паттерны]
- Компоненты: PascalCase
- Файлы данных: kebab-case.ts
- CSS: Tailwind utility-first

## Workflow                           <- STATIC
1. Показать план -> ждать подтверждения
2. Выполнить работу
3. Обновить документацию
4. Отчёт с результатами

## Verification                       <- STATIC
npm run typecheck        # 0 ошибок
npm run build            # <3 мин
npm test                 # все pass

## Deep Dive (read on demand)         <- STATIC (только ссылки)
| Тема | Файл |
|------|------|
| Компоненты | docs/COMPONENT-LIBRARY.md |
| Бренд | docs/brand/brand-identity.md |
| Roadmaps | docs/roadmaps/README.md |
| Решения | docs/WHY-LOG.md |
| Проблемы | ISSUES.md |

## Current Status                     <- SEMI-DYNAMIC
| Метрика | Значение |
|---------|----------|
| Версия | v0.31.0 |
| Роуты | 65+ |
| Компоненты | 50 |
| Тесты | 2374 |

Ключевые фичи: [5-7 bullet points]

## Open Threads                       <- DYNAMIC
| Тема | Что нужно |
|------|-----------|
| ... | ... |

## Learnings                          <- DYNAMIC (внизу для кэша)
- 2026-03-12: [урок]
- 2026-03-11: [урок]
```

**Целевой размер:** 100-150 строк, ~2.5k токенов.

---

## B) Single Source of Truth таблица

Решает AP-16 (Cross-File Duplication). Один файл-владелец для каждого типа информации.

```markdown
## Single Source of Truth

| Информация | Единственный источник | Ссылаются |
|------------|----------------------|-----------|
| Бренд (цвета, шрифты) | docs/brand/brand-identity.md | CLAUDE.md, tailwind.config.ts |
| Компоненты (список, API) | docs/COMPONENT-LIBRARY.md | CLAUDE.md |
| История изменений | CHANGELOG.md | — |
| Проблемы и задачи | ISSUES.md | CLAUDE.md |
| Архитектурные решения | docs/WHY-LOG.md | — |
| Дизайн (мудборд, варианты) | docs/design/ | CLAUDE.md |
| Структура проекта | CLAUDE.md | — |
| Деплой | docs/deployment.md или CLAUDE.md | deploy/ |
| Персонализация (UX) | docs/personalization.md | CLAUDE.md |
| Roadmap фич | docs/roadmaps/*.md | CLAUDE.md (ссылка на индекс) |
```

**Правило:** Если факт дублируется в 2+ файлах, выбрать один владелец. В остальных файлах — только ссылка: `"Бренд: см. docs/brand/brand-identity.md"`.

---

## C) Tiered Loading структура

Три тира загрузки. Essential загружается всегда, On-Demand по запросу, Archive игнорируется.

```markdown
## Essential (~800 токенов, автозагрузка)
Загружается в КАЖДОЙ сессии автоматически:
- CLAUDE.md (<300 строк, оптимизирован)
- .claude/rules/*.md (модульные правила)
- MEMORY.md (только уникальное)

## On-Demand (~500 токенов каждый, по запросу)
Загружается когда Claude работает с конкретной темой:
- docs/roadmaps/*.md — при работе с фичей
- docs/brand/brand-identity.md — при визуальной работе
- docs/COMPONENT-LIBRARY.md — при работе с компонентами
- docs/personalization.md — при UX-решениях
- CHANGELOG.md — при обновлении версии
- ISSUES.md — при проверке задач

## Archive (0 токенов, .claudeignore)
Не загружается никогда автоматически:
- docs/archive/plans/ — выполненные планы
- docs/archive/audits/ — устаревшие аудиты
- docs/archive/research/ — завершённые исследования
- docs/SESSION-LOG.md — история сессий (журнал)
- docs/design/wireframes/ — утверждённые каркасы
```

**Миграция:**
1. Создать `docs/archive/`
2. Переместить завершённые файлы
3. Добавить в .claudeignore
4. Обновить ссылки в CLAUDE.md

---

## D) .claudeignore шаблон

```
# ===== Archive (0 tokens) =====
docs/archive/**

# ===== Completed tasks =====
.claude/completions/**

# ===== Past sessions =====
.claude/sessions/**

# ===== Build artifacts =====
node_modules/**
dist/**
build/**
.next/**
out/**

# ===== Git internals =====
.git/**

# ===== Environment (secrets) =====
.env
.env.*
!.env.example

# ===== Large data files =====
*.jsonl
*.csv
*.sql

# ===== Media =====
*.mp4
*.mov
*.avi
*.zip
*.tar.gz

# ===== IDE =====
.vscode/**
.idea/**

# ===== Backups =====
backups/**
*.backup
*.bak
```

**Как применять:**
1. Создать `.claudeignore` в корне проекта
2. Добавить паттерны из шаблона
3. Добавить проектоспецифические исключения
4. Проверить: `git status` не должен показывать `.claudeignore` как untracked, если не нужен в репо

---

## E) docs/README.md шаблон (индекс)

Решает AP-08 (Missing Index).

```markdown
# Documentation Index

| Файл | Назначение | Обновлён |
|------|-----------|----------|
| ALWAYS-READ.md | Чеклист чтения в начале сессии | 2026-03-10 |
| COMPONENT-LIBRARY.md | Справочник компонентов (50 шт.) | 2026-03-11 |
| SESSION-LOG.md | История сессий 1-28 | 2026-03-11 |
| personalization.md | Предпочтения владельца | 2026-03-09 |
| ENV-VARIABLES.md | Переменные окружения | 2026-03-01 |

## Подпапки
| Папка | Назначение | Файлов |
|-------|-----------|--------|
| roadmaps/ | Roadmap каждой фичи | 11 |
| brand/ | Фирменный стиль | 1 |
| design/ | Дизайн-система, мудборд | 6 |
| research/ | Конкуренты, референсы | 20+ |
| plans/ | Планы и стратегии | 6 |
| audits/ | Аудиты качества | 1 |
```
