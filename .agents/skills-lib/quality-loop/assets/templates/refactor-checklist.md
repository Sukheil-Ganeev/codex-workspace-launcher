# Refactor Checklist — Quality Loop

Чеклист ПЕРЕД и ПОСЛЕ рефакторинга. Заполнять честно — каждый пропущенный пункт = риск.

---

## ПЕРЕД рефакторингом

### Безопасность

- [ ] Snapshot создан: `quality-loop: snapshot / module: "..."`
- [ ] Базовое число тестов записано: `pytest --collect-only -q` → _______ тестов
- [ ] Coverage baseline записан: _______ % для целевого модуля
- [ ] Baseline commit SHA записан: _______

### Масштаб изменений

- [ ] Затрагиваемые файлы перечислены (не больше 3 за один PR)
- [ ] Side effects идентифицированы (что может сломаться рядом)
- [ ] DB-миграций нет, ИЛИ они идемпотентны (`IF NOT EXISTS`)
- [ ] Изменение затрагивает > 3 файлов? → нужен `feature-blueprint: plan` сначала

### Feature flag (если live traffic)

- [ ] Feature flag нужен? Если да — добавлен до начала изменений
- [ ] Rollout план записан: 0% → 5% → 25% → 50% → 100%
- [ ] Legacy path останется нетронутым до Stage 4 (100%)

---

## ВО ВРЕМЯ рефакторинга

### Правила работы

- [ ] Один логический commit за раз (не "переделал всё")
- [ ] После каждого изменения — `pytest tests/ --lf -v` (только упавшие)
- [ ] Cleanup коммиты отдельно от refactor коммитов
- [ ] Не смешивать: рефакторинг + новая фича + фикс бага в одном PR

### Commit messages

```
refactor: extract format_block_card() from catalog handler
cleanup: remove debug print statements in catalog.py
fix: handle empty blocks list in catalog pagination
```

---

## ПОСЛЕ рефакторинга

### Тесты и coverage

- [ ] `pytest tests --collect-only -q` → >= _______ тестов (не меньше baseline)
- [ ] Нет новых FAIL тестов (были зелёные — остались зелёными)
- [ ] Coverage целевого модуля: _______ % (не ниже baseline)
- [ ] Все characterization tests проходят: `pytest tests/ -k "snapshot" -v`

### Качество кода

- [ ] `python -m pyflakes [module]` → 0 неиспользуемых импортов
- [ ] `mypy [module] --ignore-missing-imports` → 0 новых type errors
- [ ] Нет debug print/pdb/breakpoint в изменённых файлах
- [ ] Нет закомментированного кода старше 30 дней (проверить `git blame`)

### Документация

- [ ] `CLAUDE.md` обновлён (если изменилось поведение / архитектура / паттерн)
- [ ] Платформенный `*_bot/CLAUDE.md` обновлён (если затронута платформа)
- [ ] `AGENTS.md` обновлён (если изменились правила для автоматических агентов)
- [ ] Новый фокусный мемо в `docs/` создан (если контекст повторится в будущем)

### Финальный verify

- [ ] `quality-loop: verify / feature: "..."` выполнен
- [ ] VERIFY REPORT статус: **SAFE TO DEPLOY** или причина почему нет

---

## Быстрые команды

```bash
# Smoke check (без БД, ~30 сек)
pytest tests --collect-only -q

# Только упавшие в прошлый раз
pytest tests/ --lf -v

# Coverage изменённого модуля
pytest tests/ --cov=bot/handlers/catalog --cov-report=term-missing -q

# Full run с реальной БД (Windows + Docker)
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres \
  pytest tests -q -p no:cacheprovider
```
