# EXP-067 (PAT-034): Wave-based parallel agent execution with dependency graph

**Date:** 2026-02-28
**Severity:** high
**Type:** pattern
**Project:** Spy Bot v3 -> v4 (MLCR Leads Bot)
**Times applied:** 1

## Context

Spy Bot v3 -> v4 upgrade: 47 -> 72 файла, 5788 -> 10264 строк, 10 новых фич, 25 новых файлов. Нужно было реализовать 8 волн с 10 фичами за одну сессию (~30 минут), с 98/98 тестами.

## Pattern: Dependency-Aware Wave Parallelization

### Шаг 1: Построить граф зависимостей

```
Wave 0 (Foundation)
  ├── 0A: config.py extensions
  ├── 0B: database schema (new tables)
  ├── 0C: models.py (new Pydantic models)
  └── 0D: ai_client.py refactoring
         ↓
Wave 1,2,4,6 (PARALLEL — no shared files)
  ├── Wave 1: Feature A (own files only)
  ├── Wave 2: Feature B (own files only)
  ├── Wave 4: Feature C (own files only)
  └── Wave 6: Feature D (own files only)
         ↓
Wave 3,5,7 (DEPENDENT — need outputs from above)
  ├── Wave 3: Integration of Wave 1+2
  ├── Wave 5: Integration of Wave 2+4
  └── Wave 7: Final wiring + run.py
         ↓
Wave 8: Tests (all features complete)
```

### Шаг 2: Запустить до 4 субагентов одновременно

Каждый агент получает:
1. **Полный список файлов** для создания/редактирования
2. **Точные code snippets** — не описание, а конкретный код для вставки
3. **Verification commands** — `python -c "import module"` или `pytest test_file.py`
4. **Запрет на чужие файлы** — каждый агент работает ТОЛЬКО со своими файлами

### Шаг 3: Commit + test + fix после каждой группы волн

```
[Parallel group 1: Waves 1,2,4,6]
  → git commit
  → pytest (fix failures)
[Parallel group 2: Waves 3,5,7]
  → git commit
  → pytest (fix failures)
[Wave 8: Tests]
  → git commit
  → pytest --tb=short (final verification)
```

## Key Insight: File Conflicts = Bottleneck

Параллелизм ограничен НЕ количеством агентов, а **конфликтами файлов**.

Файлы-узлы конфликтов (редактируются всеми):
- `config.py` — каждая фича добавляет свои переменные
- `schema.py` / database migrations — каждая фича добавляет таблицы
- `__init__.py` — реэкспорты
- `run.py` — точка входа

**Решение:** Эти файлы редактируются ТОЛЬКО в Wave 0 (foundation) и Wave 7 (final wiring). Параллельные агенты в Waves 1-6 НЕ ТРОГАЮТ shared files.

## Метрики Spy Bot v4

| Метрика | Значение |
|---------|----------|
| Волн | 8 |
| Новых фич | 10 |
| Новых файлов | 25 |
| Строк кода | 5788 → 10264 (+77%) |
| Тестов | 98/98 passing |
| Время | ~30 минут |
| Параллельных агентов (макс) | 4 |
| Конфликтов файлов | 0 |

## Сравнение с другими подходами

| Подход | Время | Риск конфликтов | Тестируемость |
|--------|-------|-----------------|---------------|
| Последовательный (1 агент) | ~2 часа | 0 | Высокая |
| Полный параллелизм (8 агентов) | ~15 мин | Высокий | Низкая |
| **Wave-based (данный паттерн)** | **~30 мин** | **0** | **Высокая** |

## Правила для промптов субагентам

1. Указать ТОЧНЫЕ имена файлов (не "создай сервис", а "создай `core/rate_limiter.py`")
2. Указать ТОЧНЫЕ импорты которые нужно использовать
3. Указать ТОЧНЫЕ имена функций и сигнатуры
4. НЕ давать свободу в именовании — иначе конфликт имён (см. EXP-INV-001)
5. Включить verification command в промпт

## Когда использовать

- 5+ новых файлов / фич в одной сессии
- Фичи можно разделить на независимые группы
- Есть чёткий граф зависимостей

## Связанные уроки

- EXP-015 (PAT-004): Параллельные агенты без конфликтов = правило "свои файлы"
- EXP-022 (PAT-011): Wiring = отдельная волна
- EXP-056 (PAT-027): Feature-based агенты эффективнее layer-based при 3+ фичах
- EXP-064 (PAT-032): Strict file ownership при крупном рефакторинге

## Keywords

wave-based, parallel-agents, dependency-graph, spy-bot-v4, subagents, file-conflicts, bottleneck, foundation-wave, wiring-wave
