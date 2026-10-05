# doc-ops — Documentation Operations

> Полный цикл документации: генерация после шипа + аудит + оптимизация + чистка.
> Объединяет delivery-docs + docs-optimizer в один скилл.

## Quick Start

| Задача | Команда |
|--------|---------|
| Отшипил фичу — обновить все доки | `doc-ops ship` или `doc-ops ship: Phase 22 Max Bot` |
| Обновить OpenAPI спеку | `doc-ops api` или `doc-ops api: Instagram webhook` |
| Проверить здоровье доков | `doc-ops audit` |
| Оптимизировать раздутые доки | `doc-ops clean` |
| Быстрый score | `doc-ops score` |

## Файлы скилла

| Файл | Назначение |
|------|-----------|
| `SKILL.md` | Основная логика и инструкции |
| `references/changelog-advanced.md` | Keep a Changelog + SemVer + Conventional Commits |
| `references/openapi-patterns.md` | FastAPI OpenAPI паттерны + drift detection |
| `references/anti-patterns.md` | 20 антипаттернов документации с примерами |
| `references/cheatsheet.md` | Быстрая справка: метрики, чеклисты, команды |
| `references/templates.md` | Шаблоны CLAUDE.md, SSOT, tiered loading, .claudeignore |
| `assets/templates/release-notes-ru.md` | Шаблон release notes на русском |
| `assets/templates/openapi-base.yaml` | Базовый OpenAPI 3.x YAML шаблон |

## Режимы

### ship — Post-ship документация
После завершения фазы/фичи: CHANGELOG + CLAUDE.md + release notes + docstrings + Mermaid диаграмма + health score.

### api — OpenAPI спецификация
Генерация/обновление OpenAPI 3.x из FastAPI кода + drift detection.

### audit — Аудит документации
20 антипаттернов + дупликация + freshness + content drift + tier-классификация → score N/5.

### clean — Оптимизация + применение
audit → генерация оптимизированных версий → diff → одобрение → применение → backup.

### score — Быстрая проверка
Ключевые метрики: строки/токены/дупликаты/свежесть → оценка N/5. Без полного сканирования антипаттернов.

## Происхождение

Объединение двух скиллов:
- **delivery-docs v1.0.0** (2026-03-12) — post-ship документация
- **docs-optimizer v1.0.0** (2026-03-12) — аудит и оптимизация

## Связанные файлы

- Опыт использования: `experience/_index.md`
- Тесты: `evals/evals.json`
