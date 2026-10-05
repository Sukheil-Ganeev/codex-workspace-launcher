# doc-ops -- Cheatsheet

Быстрая справка. Все метрики, правила и чеклисты в одном месте.
Покрывает ВСЕ режимы: ship, optimize, audit.

---

## Ship Mode — быстрая справка

### SemVer правила (MAJOR.MINOR.PATCH)

| Триггер | Версия | Пример |
|---------|--------|--------|
| Breaking change в API/DB | **MAJOR** | v10.x.x → v11.0.0 |
| Новый бот / крупная фича / новая фаза | **MINOR** | v10.8.0 → v10.9.0 |
| Bug fix / hotfix | **PATCH** | v10.8.0 → v10.8.1 |

### CHANGELOG.md формат (Keep a Changelog)

```markdown
## [X.Y.Z] - YYYY-MM-DD HH:MM (Dubai)

### Added
- Новая фича (что даёт пользователю)

### Fixed
- Баг (что было не так → что теперь правильно)

### Changed
- Изменённое поведение (было → стало)

### Removed
- Удалённый код/фича
```

**Категории:** Added, Changed, Deprecated, Removed, Fixed, Security
**Пропускать:** chore, ci, docs-only, typo фиксы

### CLAUDE.md Changelog таблица

```markdown
## Changelog (последние 6)

| Дата | Фаза | Что сделано |
|------|------|------------|
| YYYY-MM-DD | Phase N: Name | Краткое описание, N тестов. |
```

- **Максимум 6 строк** — при добавлении новой удалять самую старую
- Всегда включать количество тестов если они добавлялись
- Дата в формате `YYYY-MM-DD` (Dubai timezone)

### Release Notes шаблон

Шаблон: `assets/templates/release-notes-ru.md`

Структура:
1. **Одним предложением** — что изменилось и для кого
2. **Что нового** — 3-5 пунктов, язык пользователя (не разработчика)
3. **Что улучшено** — было X, стало Y
4. **Что исправлено** — баги
5. **Для менеджеров** — если есть изменения в их работе
6. **Для клиентов** — если есть видимые изменения

### Docstring формат (Google-style)

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Краткое описание (одна строка).

    Детальное описание если нужно (опционально).

    Args:
        param1: Описание первого параметра.
        param2: Описание второго параметра.

    Returns:
        Описание возвращаемого значения.

    Raises:
        ValueError: Когда param1 пустой.
    """
```

### Conventional Commits

```
<type>(<scope>): <description>
```

Типы: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `security`

---

## Целевые метрики

| Метрика | Идеал | Максимум | Danger |
|---------|-------|----------|--------|
| CLAUDE.md токены | ~2.5k (~100-150 строк) | 4k (~200 строк) | 5k+ |
| CLAUDE.md строки | ~150 | ~300 | 500+ |
| Инструкций (суммарно) | <100 | <150 | 200+ |
| Verification score | 5/5 | 4/5 | <3/5 |
| Дублирование | 0% | <5% | >10% |
| Актуальность docs | >90% | >70% | <50% |
| Essential tier | ~800 токенов | ~1.5k | 3k+ |

---

## Подсчёт токенов (приблизительно)

```
~4 символа = 1 токен (латиница)
~2-3 символа = 1 токен (кириллица)
Строка Markdown ~ 20-30 токенов
100 строк ~ 2-3k токенов
```

Быстрая оценка: `wc -c CLAUDE.md` / 4 ~ токенов (для латиницы).

---

## Cache-Optimized порядок CLAUDE.md

```
1. Quick Reference (static)       <- кэшируется
2. Architecture (static)          <- кэшируется
3. Conventions (static)           <- кэшируется
4. Workflow (static)              <- кэшируется
5. Verification (static)          <- кэшируется
6. Deep Dive links (static)       <- кэшируется
7. Current Status (semi-dynamic)
8. Open Threads (dynamic)
9. Learnings (dynamic)            <- внизу
```

**Принцип:** Статика сверху кэшируется по prefix. Динамика внизу не ломает кэш предыдущих секций.

---

## Правило тиров

| Тир | Загрузка | Стоимость | Что включать |
|-----|----------|-----------|-------------|
| Essential | Всегда | ~800 токенов | CLAUDE.md + .claude/rules/ |
| On-Demand | По запросу | ~500/файл | docs/roadmaps/, brand/, components |
| Archive | Никогда авто | 0 | Выполненные планы, старые аудиты |

**Цель:** Essential < 1.5k токенов. On-Demand читается только при работе с конкретной темой.

---

## Severity анти-паттернов

| Severity | Что значит | Действие |
|----------|-----------|----------|
| Critical | Ломает работу Claude, тратит 30%+ токенов впустую | Исправить немедленно |
| High | Снижает качество, вызывает повторные ошибки | Исправить в текущей сессии |
| Medium | Неудобство, лишние токены | Исправить при рефакторинге |
| Low | Косметическое, nice-to-have | По желанию |

**Critical (исправить первыми):** AP-07, AP-12, AP-16
**High (исправить далее):** AP-01, AP-04, AP-10, AP-11, AP-13, AP-17, AP-19, AP-20

---

## Чеклист оптимизации

```
[ ] CLAUDE.md < 300 строк?
[ ] Нет дублирования между файлами?
[ ] Все ссылки на файлы валидны? (grep + проверить существование)
[ ] ISSUES.md -- нет стухших issues?
[ ] MEMORY.md -- нет дублей с CLAUDE.md?
[ ] docs/archive/ создан для мёртвых файлов?
[ ] .claudeignore исключает архивы?
[ ] Static sections сверху CLAUDE.md?
[ ] Verification секция с конкретными командами?
[ ] Single Source of Truth таблица есть?
[ ] Инструкций суммарно < 150?
[ ] docs/README.md (индекс) существует?
```

---

## Что НЕЛЬЗЯ удалять

| Файл | Почему |
|------|--------|
| CHANGELOG.md | Журнал, растёт со временем |
| WHY-LOG.md | Журнал решений — контекст для будущих сессий |
| ISSUES.md | Трекер проблем — единственный источник правды |
| Dormant code/docs | Может быть подготовкой к фиче — спросить владельца |
| TODO/FIXME комментарии | Намеренные маркеры — не мусор |
| .env.example | Документирует нужные переменные |

---

## Быстрые команды аудита

```bash
# Размер CLAUDE.md (строки и символы)
wc -l CLAUDE.md
wc -c CLAUDE.md

# Все файлы, на которые ссылается CLAUDE.md
grep -oP '[\w/.-]+\.md' CLAUDE.md | sort -u

# Проверить что файлы существуют
grep -oP '[\w/.-]+\.md' CLAUDE.md | sort -u | while read f; do
  [ -f "$f" ] || echo "MISSING: $f"
done

# Дублирование строк между файлами
comm -12 <(sort CLAUDE.md) <(sort MEMORY.md) | wc -l

# Размер docs/
find docs/ -name "*.md" | wc -l
find docs/ -name "*.md" -exec wc -l {} + | tail -1

# Orphan docs (файлы без ссылок)
for f in docs/*.md; do
  grep -rl "$(basename $f)" CLAUDE.md .claude/ > /dev/null 2>&1 || echo "ORPHAN: $f"
done
```

---

## Формула оценки

```
Score = (Completeness * 0.3) + (Efficiency * 0.3) + (Freshness * 0.2) + (Structure * 0.2)

Completeness: все критичные секции присутствуют (Quick Ref, Arch, Verify)
Efficiency: токены CLAUDE.md / полезная информация (ближе к 1.0 = лучше)
Freshness: % файлов docs/ обновлённых за последние 30 дней
Structure: cache ordering + tiering + no duplication
```
