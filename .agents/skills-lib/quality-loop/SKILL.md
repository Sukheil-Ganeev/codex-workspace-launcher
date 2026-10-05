---
name: quality-loop
description: "Полный цикл написать фичу правильно с первого раза. Объединяет TDD, planning и safe refactoring. Используй когда начинаешь новую фичу, пишешь тесты, рефакторишь код или нужен финальный verify перед деплоем. Режимы: plan-test, cycle, snapshot, cleanup, verify."
license: Apache-2.0
metadata:
---
# Quality Loop — Написать фичу правильно с первого раза

## Overview

**Проблема:** Фичи пишутся без тестов. Тесты пишутся после кода, когда уже поздно — они описывают реализацию, а не поведение. Рефакторинг страшен, потому что нет baseline. Deploy страшен, потому что нет verify.

**Результат:** Каждый новый хэндлер — риск. Каждое изменение в `data/database.py` — страх. Каждый деплой — надежда на лучшее.

**Решение — единый workflow:**

```
Задача / запрос
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  quality-loop                                                    │
│                                                                  │
│  plan-test ──► Разбить на тестируемые единицы + stub-тесты      │
│                │                                                 │
│                ▼                                                 │
│  cycle     ──► RED → GREEN → REFACTOR для каждой функции        │
│                │                                                 │
│                ▼                                                 │
│  [если рефакторинг существующего кода — сначала snapshot]       │
│  snapshot  ──► Characterization tests + baseline commit          │
│                │                                                 │
│                ▼                                                 │
│  cleanup   ──► Debug → dead code → over-engineering             │
│                │                                                 │
│                ▼                                                 │
│  verify    ──► Coverage + type check + regression + doc-sync    │
└──────────────────────────────────────────────────────────────────┘
      │
      ▼
Фича задеплоена. Тесты зелёные. CLAUDE.md обновлён.
```

**Почему это важно для VIP-DXB-CatalogBot:**
- 2930 тестов защищают 7 платформ от регрессий при деплое
- asyncpg + aiogram + FastAPI + 7 webhook-ботов = три разных слоя со своими паттернами
- Один упавший хэндлер на production = потерянный клиент в Дубае
- Omni Inbox строится поверх уже работающих платформ — нарушить существующие интеграции легко

---

## When to Use

Активируй `quality-loop` когда:

| Ситуация | Рекомендуемый старт |
|----------|-------------------|
| Новый хэндлер (TG/VK/IG/WA/FB/Viber) | `plan-test` → `cycle` |
| Новый DB-метод в `data/database.py` | `plan-test` → `cycle` |
| Новый Omni Inbox коннектор | `plan-test` → `cycle` |
| Новый webhook endpoint (FastAPI) | `plan-test` → `cycle` |
| Рефакторинг существующего модуля | `snapshot` → `cleanup` → `verify` |
| Фикс бага (сначала тест, потом фикс) | `cycle` (RED = тест воспроизводящий баг) |
| Финальная проверка перед деплоем | `verify` |
| Новая платформа (например, Max Bot) | `plan-test` (после `feature-blueprint: plan`) |

### Конкретные примеры из VIP-DXB-CatalogBot

**Пример 1 — Добавление Max Bot:**
```
После blueprint: plan для "Max Bot Integration"
→ quality-loop: plan-test / task: "Реализовать MaxConnector в Omni Inbox"
→ quality-loop: cycle / function: "MaxConnector.handle_message()"
→ quality-loop: cycle / function: "get_or_create_max_user()"
→ quality-loop: verify / feature: "Max Bot Phase 22"
```

**Пример 2 — Рефакторинг catalog.py:**
```
→ quality-loop: snapshot / module: "bot/handlers/catalog.py"
→ quality-loop: cleanup / scope: "bot/handlers/catalog.py"
→ quality-loop: verify / feature: "catalog.py refactor"
```

**Пример 3 — Фикс бага в booking FSM:**
```
→ quality-loop: cycle / function: "handle_booking_confirm()"
  (RED = тест воспроизводит баг → GREEN = фикс → REFACTOR)
```

---

## Modes

### Mode: `plan-test` — Bridge между Planning и TDD

**Цель:** взять задачу из breakdown и превратить её в конкретные тестируемые единицы + готовый stub-файл. Это мост между `feature-blueprint: breakdown` (что делать) и `cycle` (как тестировать).

**Вызов:**
```
quality-loop: plan-test / task: "Реализовать get_or_create_max_user() для Max Bot"
```

**Шаги:**

1. **Определить тестируемые единицы** — для каждой функции/метода три вопроса:
   - **Input** — что принимает? (аргументы, типы, edge cases)
   - **Output** — что возвращает? (тип, структура, None/empty cases)
   - **Side effects** — что меняет в БД/состоянии?

2. **Определить стратегию: unit vs integration:**
   - Unit (< 10ms): логика без БД, с mock_db → быстро, запускается всегда
   - Integration (< 1s): реальный asyncpg с TEST_DATABASE_URL → критичные DB-пути
   - E2e: полный webhook flow с TestClient → только для критичных входных точек

3. **Создать stub-файл** с заготовками pytest-тестов (все `pytest.skip("not implemented")`)

**Пример — spec для `get_or_create_max_user()`:**

```
plan-test output:

ТЕСТИРУЕМАЯ ЕДИНИЦА: get_or_create_max_user(max_id, max_name)

Inputs:
  - max_id: str (валидный, первый вызов)  → unit
  - max_id: str (тот же, повторный вызов)  → unit
  - max_id: "" (пустая строка)             → unit (edge case)
  - max_name: None (опциональное поле)     → unit

Outputs:
  - (synthetic_user_id: int, created: bool)
  - synthetic_user_id в диапазоне -4000..-4999
  - created=True при первом, False при повторном

Side effects:
  - INSERT в max_users (первый вызов)  → integration
  - UPDATE last_active (повторный)     → integration
  - loyalty-запись создаётся авто      → integration

Edge cases (unit):
  - конкурентный вызов с одним max_id  → asyncio.gather тест
  - max_id с unicode-символами

Stub файл: → tests/test_max_user.py (см. assets/templates/test-stub-async.py)
```

**Автопредложение:** после plan-test → предлагает `cycle` для первой задачи.

---

### Mode: `cycle` — Полный TDD Цикл

**Цель:** провести полный RED → GREEN → REFACTOR цикл для одной функции или хэндлера. Работает для новых фич и для фиксов багов.

**Вызов:**
```
quality-loop: cycle / function: "MaxConnector.on_incoming_message()"
```

#### Шаг 1 — RED: Пишем падающий тест

Тест должен упасть по правильной причине (ImportError или AssertionError, не SyntaxError).

```python
# tests/test_max_connector.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_max_connector_routes_to_omni_inbox():
    """MaxConnector.handle_message() → вызывает omni_service.on_incoming_message()."""
    from bot.services.omni_inbox import OmniInboxService

    omni_service = AsyncMock(spec=OmniInboxService)

    # Это упадёт: MaxConnector ещё не существует
    from max_bot.connector import MaxConnector  # ImportError → RED

    connector = MaxConnector(omni_service=omni_service)
    await connector.handle_message(
        platform_user_id="user123",
        text="Хочу экскурсию"
    )

    omni_service.on_incoming_message.assert_called_once()
    kwargs = omni_service.on_incoming_message.call_args[1]
    assert kwargs["platform"] == "max"
    assert kwargs["text"] == "Хочу экскурсию"
```

Запуск: `pytest tests/test_max_connector.py -v` → **FAIL** (ImportError)

#### Шаг 2 — GREEN: Минимальный код для прохождения

Правило: только то, что нужно для прохождения теста. Не добавлять логирование, i18n, fallback — это после.

```python
# max_bot/connector.py
class MaxConnector:
    def __init__(self, omni_service):
        self.omni_service = omni_service

    async def handle_message(self, platform_user_id: str, text: str):
        await self.omni_service.on_incoming_message(
            platform="max",
            platform_user_id=platform_user_id,
            text=text
        )
```

Запуск: `pytest tests/test_max_connector.py -v` → **PASS**

#### Шаг 3 — REFACTOR: Улучшаем без ломания тестов

- Добавляем type hints
- Добавляем логирование: `logger.info(f"[max_connector] incoming: {platform_user_id}")`
- Добавляем обработку ошибок
- Прогоняем тест — должен остаться GREEN

**Async concurrency паттерн** (для edge case concurrent вызовов):

```python
@pytest.mark.asyncio
async def test_concurrent_get_or_create_max_user(mock_db):
    """Конкурентные вызовы с одним max_id — не должно быть дублирования."""
    mock_db.get_or_create_max_user = AsyncMock(return_value=(-4000, True))

    # Запускаем 5 одновременных вызовов
    results = await asyncio.gather(*[
        mock_db.get_or_create_max_user("user123", "Test User")
        for _ in range(5)
    ])

    # Все должны вернуть один и тот же synthetic_user_id
    synthetic_ids = [r[0] for r in results]
    assert len(set(synthetic_ids)) == 1, "Разные synthetic_id для одного max_id!"
```

**Webhook endpoint паттерн** (для IG/WA/FB/Viber):

```python
import pytest
from fastapi.testclient import TestClient

def test_max_webhook_requires_valid_hmac(max_client):
    """POST без корректной HMAC подписи → 403."""
    response = max_client.post(
        "/webhook/max",
        json={"type": "message", "sender": {"id": "user123"}},
        headers={"X-Hub-Signature-256": "sha256=invalid"}
    )
    assert response.status_code == 403

def test_max_webhook_processes_message(max_client, valid_hmac_headers):
    """POST с верной HMAC и message event → 200 + message processed."""
    payload = {"type": "message", "sender": {"id": "user123"}, "text": "Привет"}
    response = max_client.post(
        "/webhook/max",
        json=payload,
        headers=valid_hmac_headers(payload)
    )
    assert response.status_code == 200
```

**Автопредложение:** `cycle` зелёный → если найден dead code при рефакторе → предлагает `cleanup`.

---

### Mode: `snapshot` — Регрессионный Baseline

**Цель:** зафиксировать текущее поведение перед рефакторингом. Это страховочная сетка. Используется ТОЛЬКО при рефакторинге существующего кода — не при написании нового.

**Вызов:**
```
quality-loop: snapshot / module: "bot/handlers/catalog.py"
```

#### Шаг 1 — Запустить существующие тесты, записать baseline

```bash
# Записать baseline
pytest tests/ --tb=short -q 2>&1 | tee baseline_output.txt

# Покрытие конкретного модуля
pytest tests/ --cov=bot/handlers/catalog --cov-report=term-missing -q
```

Записать: количество тестов, passed/failed, coverage %.

#### Шаг 2 — Characterization tests (golden-master)

Для непокрытых критичных путей — написать тесты, которые фиксируют текущий вывод. Цель: обнаружить ИЗМЕНЕНИЕ, не проверить КОРРЕКТНОСТЬ.

```python
def test_catalog_handler_snapshot_current_behavior():
    """Characterization test — фиксирует текущее поведение как baseline.
    НЕ проверяет корректность, только что поведение не изменилось при рефакторе.
    Baseline: 2026-03-12, commit abc1234"""
    # Текущий вывод на вход "dubai" — записываем как есть
    result = format_block_card(block_id=1, lang="ru")
    assert "Дубай" in result  # фиксируем что ключевое слово присутствует
    assert len(result) > 50   # фиксируем что карточка не пустая
```

#### Шаг 3 — Записать snapshot

```
BASELINE SNAPSHOT — 2026-03-12
Модуль: bot/handlers/catalog.py
Тесты: 2930 passed
Покрытие catalog.py: 78%
Baseline commit: [git SHA]
Feature flag: не нужен (локальный рефакторинг)
Ключевые поведения:
  - handle_catalog_start(): возвращает inline-клавиатуру с эмиратами
  - handle_catalog_category(): пагинирует блоки по 5
  - handle_block_card(): форматирует карточку с ценой через catalog_price_display.py
```

#### Шаг 4 — Feature flag (для больших миграций)

Если рефакторинг затрагивает live traffic:

```python
USE_NEW_CATALOG_HANDLER = os.getenv("USE_NEW_CATALOG_HANDLER", "false") == "true"

async def handle_catalog_start(callback: CallbackQuery):
    if USE_NEW_CATALOG_HANDLER:
        return await _new_handle_catalog_start(callback)
    return await _legacy_handle_catalog_start(callback)
```

Rollout: 0% → 5% → 25% → 50% → 100% → убрать legacy path после одного полного цикла.

### Large File Strategy (>500 lines)

Для больших файлов полный golden-master snapshot нецелесообразен: сотни хрупких тестов, которые ломаются при любом изменении форматирования и которые никто не поддерживает.

#### Дерево решений

```
Файл < 200 строк
  → полный golden-master snapshot (все public функции)

Файл 200–500 строк
  → function-level snapshots (топ-10 по риску)

Файл > 500 строк
  → chunked: registry + interface + metrics + топ-5 критичных функций
```

#### Chunked Approach — 4 типа snapshot'ов

**1. Callback Registry Snapshot** — для файлов с роутерами/хэндлерами. Фиксирует СПИСОК зарегистрированных callbacks, а не их поведение:

```python
def test_omni_callback_registry_snapshot():
    """Verify all expected callbacks are registered — detect accidental removal."""
    from bot.handlers.omni import omni_router

    # Собираем имена всех зарегистрированных callback handlers
    cb_names = [
        h.callback.__name__
        for h in omni_router.callback_query.handlers
    ]

    # Baseline: эти callbacks ОБЯЗАНЫ существовать
    expected = [
        "cmd_inbox", "cmd_inbox_platform", "cmd_inbox_page",
        "cmd_all_today", "cmd_all_page", "cmd_conversation",
        "cmd_claim", "cmd_reply_menu", "cmd_quick_reply",
        "cmd_custom_reply_start", "cmd_close", "cmd_close_confirm",
        "cmd_client_card", "cmd_settings", "cmd_stats_default",
        "cmd_export",
        # ... полный список при создании snapshot
    ]
    missing = set(expected) - set(cb_names)
    assert not missing, f"Missing callbacks: {missing}"
```

**2. Interface Snapshot** — фиксирует сигнатуры public-функций, не поведение:

```python
import inspect

def test_omni_public_interface_snapshot():
    """Public API must not shrink unexpectedly."""
    import bot.handlers.omni as omni

    public = [
        name for name in dir(omni)
        if not name.startswith("_") and callable(getattr(omni, name))
    ]
    # Baseline count — если уменьшилось, что-то удалено
    assert len(public) >= 35, (
        f"Public interface shrunk to {len(public)} — was something removed?"
    )
```

**3. Metrics Snapshot** — сигнал о неконтролируемом росте:

```python
import inspect

def test_omni_complexity_guard():
    """File complexity must not grow unchecked."""
    import bot.handlers.omni as omni

    source = inspect.getsource(omni)
    line_count = len(source.splitlines())
    func_count = source.count("async def ")

    # Baselines — обновлять ТОЛЬКО при осознанном рефакторинге
    assert line_count < 3000, (
        f"omni.py grew to {line_count} lines — consider splitting"
    )
    assert func_count < 50, (
        f"omni.py has {func_count} functions — consider splitting"
    )
```

**4. Top-N Critical Functions** — полный golden-master snapshot ТОЛЬКО для 5 самых рисковых функций. Выбирать по:
  - git blame частота изменений (чаще меняется = выше риск)
  - количество branch/if (больше ветвей = больше шансов сломать)
  - число зависимостей/импортов (больше coupling = больше side effects)

```python
# Пример: cmd_claim — критичная функция (atomic claim + race condition risk)
@pytest.mark.asyncio
async def test_cmd_claim_snapshot():
    """Characterization: cmd_claim assigns conversation to manager."""
    # ... полный golden-master test для ОДНОЙ конкретной функции
```

#### Конкретный пример: omni.py (2291 строк, 40 async функций, 39 callbacks)

```
quality-loop: snapshot / module: "bot/handlers/omni.py"

→ Файл > 500 строк → chunked approach

Snapshot plan:
  1. Registry snapshot    — 39 callbacks зарегистрированы
  2. Interface snapshot   — >= 35 public callables
  3. Metrics snapshot     — < 3000 строк, < 50 функций
  4. Top-5 critical:
     - cmd_claim (atomic claim, race condition)
     - cmd_conversation (thread view, pagination)
     - cmd_reply_menu + cmd_quick_reply (response flow)
     - cmd_close_confirm (state transition)
     - handle_reply_text (FSM, cross-platform send)

Total: ~12-15 тестов вместо 200+
```

**Автопредложение:** после snapshot → предлагает `cleanup` или `refactor` (из code-refactor-pro).

---

### Mode: `cleanup` — Безопасная Очистка

**Цель:** убрать шум после написания кода: debug statements, dead code, over-engineering. Отдельные коммиты от рефакторинга — для чистоты git history.

**Вызов:**
```
quality-loop: cleanup / scope: "bot/handlers/omni.py"
```

#### Phase 1 — Debug removal (HIGH certainty → авто-fix)

```python
# Искать и удалять:
print("debug", ...)          # Python debug
print(f"TEST: {variable}")   # временные логи
import pdb; pdb.set_trace()  # Python debugger
breakpoint()                 # Python 3.7+ debugger
logger.debug(f"TEMP: ...")   # временные DEBUG-логи с TEMP/TEST метками
```

Для каждого найденного: удалить строку → запустить тесты → если зелёные → коммит:
```
cleanup: remove debug print statements in omni.py
```

#### Phase 2 — Commented-out code (MEDIUM certainty → требует review)

Удалять если:
- Закомментированный код старше 30 дней (проверить `git blame`)
- Закомментированный импорт который никогда не использовался
- Секции `#####` без содержимого

Оставлять если:
- Комментарий объясняет ПОЧЕМУ (не ЧТО)
- Ссылается на внешний тикет или ADR
- Документирует нестандартное бизнес-правило

#### Phase 3 — Dead code (MEDIUM certainty → проверить перед удалением)

```bash
# Python: неиспользуемые импорты
python -m pyflakes bot/handlers/omni.py

# Найти все места использования функции
grep -r "function_name" . --include="*.py"
```

Перед удалением: проверить через `git log --all -S "function_name"` — вдруг недавно использовалась? Проверить динамическую диспетчеризацию (callbacks через строки в VK/Telegram).

#### Phase 4 — Over-engineering (LOW certainty → только флагировать)

Не удалять автоматически. Отметить для обсуждения:
- Абстракция с единственной реализацией без планов на вторую
- Factory pattern, оборачивающий один класс
- Сложная конфигурация для трёх строк кода

**Commit convention:**
```
cleanup: remove debug print in omni.py
cleanup: delete commented-out legacy catalog handler (unused 45 days)
cleanup: remove unused import asyncio in booking.py
```

**Автопредложение:** cleanup завершён → автоматически запускает `verify`.

---

### Mode: `verify` — Финальная Проверка

**Цель:** убедиться, что фича или рефакторинг не сломал ничего существующего. Последний шаг перед PR и деплоем.

**Вызов:**
```
quality-loop: verify / feature: "Max Bot Phase 22"
```

#### Шаг 1 — Полный тест-сьют

```bash
# Быстрый smoke-check (без БД)
pytest tests --collect-only -q  # должно быть >= 2930 тестов

# Полный прогон с реальной БД
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres \
  pytest tests -q -p no:cacheprovider
```

Сравнить с baseline: тестов стало больше или столько же? Нет новых падений?

#### Шаг 2 — Type check и lint

```bash
# Python type check
mypy bot/handlers/ --ignore-missing-imports --no-error-summary

# Pyflakes (неиспользуемые импорты)
python -m pyflakes bot/handlers/omni.py

# Нет новых ошибок по сравнению с baseline
```

#### Шаг 3 — Coverage check

```bash
# Покрытие новых файлов (цель: >= 80%)
pytest tests/ --cov=max_bot --cov-report=term-missing -q

# Покрытие не должно упасть ниже baseline для изменённых файлов
pytest tests/ --cov=bot/handlers/catalog --cov-fail-under=78 -q
```

#### Шаг 4 — Regression: characterization tests

Если snapshot создавался → все characterization tests должны пройти:
```bash
pytest tests/ -k "snapshot" -v
```

#### Шаг 5 — Doc-sync check

Проверить нужно ли обновить документацию:
- [ ] `CLAUDE.md` — изменилось поведение, архитектура, DB-схема?
- [ ] Платформенный `CLAUDE.md` (например `bot/CLAUDE.md`) — новые паттерны?
- [ ] `AGENTS.md` — изменилось что-то для автоматических агентов?
- [ ] `docs/` — нужен новый фокусный мемо?

#### Шаг 6 — Финальный отчёт

```
VERIFY REPORT — Max Bot Phase 22
==================================
Baseline:    2930 тестов passed, catalog.py 78%
После:       2930 + 45 новых = 2975 тестов passed
New files:   max_bot/ → 87% coverage
Type errors: 0 новых
Lint errors: 0 новых
Characterization: N/A (новый код, не рефакторинг)
CLAUDE.md:   ТРЕБУЕТ ОБНОВЛЕНИЯ (новая платформа Max Bot)
Feature flag: N/A
Статус:      SAFE TO DEPLOY
```

**Автопредложение:** verify зелёный → предлагает `delivery-docs release` (если скилл доступен).

---

## Synergy Rules — Автоматические Цепочки

Режимы designed to work together. Правила автосвязей:

### Новая фича (с нуля)
```
blueprint: breakdown          → получаем список задач по 15-60 мин
    │
    ▼
quality-loop: plan-test       → для каждой задачи: input/output/edge cases + stub
    │
    ▼
quality-loop: cycle           → RED → GREEN → REFACTOR для каждой функции
    │ [если найден dead code при рефакторе]
    ▼
quality-loop: cleanup         → убираем шум, отдельные коммиты
    │ [автоматически]
    ▼
quality-loop: verify          → coverage + types + regression + doc-sync
    │ [если verify зелёный]
    ▼
delivery-docs: release        → changelog + версия (если скилл доступен)
```

### Рефакторинг существующего кода
```
code-refactor-pro: analyze    → P0/P1/P2 debt report
    │
    ▼
quality-loop: snapshot        → baseline + characterization tests
    │
    ▼
code-refactor-pro: refactor   → инкрементальная миграция (1 файл за раз)
    │
    ▼
quality-loop: cleanup         → debug/dead code/over-engineering
    │ [автоматически]
    ▼
quality-loop: verify          → регрессия + doc-sync
```

### Фикс бага
```
quality-loop: cycle           → RED (тест воспроизводит баг) → GREEN (фикс) → REFACTOR
    │
    ▼
quality-loop: verify          → убедиться что другие тесты не сломались
```

### Правило: snapshot обязателен при рефакторинге
Любой момент + рефакторинг существующего кода → сначала `snapshot`, потом что угодно другое.

---

## Test Strategy

Полная стратегия: `references/test-strategy.md`. Краткая версия здесь.

### Пирамида тестов для VIP-DXB-CatalogBot

```
         /\
        /E2E\          10% — полный webhook flow
       /──────\
      /Integra-\       20% — asyncpg + реальная БД
     / tion     \
    /────────────\
   /  Unit Tests  \    70% — mock_db + AsyncMock, < 10ms
  /────────────────\
```

**Правило:** если функция — чистая логика без БД → unit test. Если функция пишет в БД → integration test с TEST_DATABASE_URL. Если функция — точка входа webhook → e2e с TestClient + HMAC.

### Async test паттерны

```python
# Базовый async тест
@pytest.mark.asyncio
async def test_something():
    result = await some_async_function()
    assert result is not None

# Concurrency test
@pytest.mark.asyncio
async def test_concurrent_calls():
    results = await asyncio.gather(*[
        func(user_id=i) for i in range(10)
    ])
    assert all(r is not None for r in results)

# yield для cooperative multitasking в тестах
@pytest.mark.asyncio
async def test_race_condition():
    await asyncio.sleep(0)  # уступить event loop другим coroutines
    assert state_is_consistent()
```

### Платформенная стратегия тестирования

| Платформа | Unit | Integration | E2E |
|-----------|------|------------|-----|
| Telegram (aiogram) | AsyncMock(spec=Message) | asyncpg pool | aiogram test utils |
| VK (vkbottle) | AsyncMock handlers | asyncpg pool | Long Poll mock |
| IG/WA/FB/Viber | мок FSM + formatter | asyncpg pool | TestClient + HMAC |
| Mini App | router мок | asyncpg pool | TestClient REST |
| Omni Inbox | мок connectors | asyncpg pool | full flow |

---

## Quick Reference — Таблица Режимов

| Режим | Команда | Когда использовать | Вывод |
|-------|---------|-------------------|-------|
| `plan-test` | `quality-loop: plan-test / task: "..."` | Перед написанием кода | Spec + stub-файл |
| `cycle` | `quality-loop: cycle / function: "..."` | Для каждой функции | RED→GREEN→REFACTOR |
| `snapshot` | `quality-loop: snapshot / module: "..."` | Перед рефакторингом | Baseline + characterization tests |
| `cleanup` | `quality-loop: cleanup / scope: "..."` | После кодинга перед PR | Cleanup commits |
| `verify` | `quality-loop: verify / feature: "..."` | Перед деплоем | VERIFY REPORT |

**Быстрые команды:**

```bash
# Smoke check (2930 тестов без БД)
pytest tests --collect-only -q

# Полный прогон с реальной БД (Windows/Docker)
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres \
  pytest tests -q -p no:cacheprovider

# Только падавшие в прошлый раз
pytest tests/ --lf -v

# Coverage нового модуля
pytest tests/ --cov=max_bot --cov-report=term-missing -q

# Только тесты по имени
pytest tests/ -k "max_bot or omni" -v
```

---

## Common Mistakes

### 1. Пропустить plan-test и сразу писать код

```
ПЛОХО:
"Добавить MaxConnector" → сразу открыть max_bot/connector.py → начать писать

ХОРОШО:
"Добавить MaxConnector" → plan-test → получить список тестируемых единиц
→ stub-файл → потом писать код
```

Почему: без plan-test пишется код, который тестировать сложно. После кода тест превращается в описание реализации, а не поведения.

### 2. Рефакторинг без snapshot

```
ПЛОХО:
"Порефакторим catalog.py" → начать менять код

ХОРОШО:
quality-loop: snapshot / module: "bot/handlers/catalog.py"
→ baseline зафиксирован → теперь можно менять
```

Почему: без baseline невозможно знать, что именно сломалось. Characterization tests — единственный способ.

### 3. GREEN код слишком большой

```python
# ПЛОХО — сразу пишем полный хэндлер
async def handle_max_message(event):
    user = await db.get_or_create_max_user(event.sender_id, event.sender_name)
    lang = await get_user_lang(user["synthetic_user_id"])
    text = t("welcome.greeting", lang=lang)
    await max_api.send_text(event.sender_id, text)
    logger.info(f"[max] message handled: {event.sender_id}")
    # ... ещё 20 строк

# ХОРОШО — минимальный GREEN, потом REFACTOR добавит остальное
async def handle_max_message(event):
    await omni_service.on_incoming_message(
        platform="max",
        platform_user_id=event.sender_id,
        text=event.text
    )
```

### 4. Cleanup и рефакторинг в одном коммите

```
ПЛОХО:
git commit -m "refactor: cleanup catalog handler + fix logic + remove debug"

ХОРОШО:
git commit -m "cleanup: remove debug print in catalog.py"
git commit -m "refactor: extract format_block_card() in catalog.py"
git commit -m "fix: handle empty blocks list in catalog pagination"
```

Почему: смешанные коммиты нельзя bisect. Регрессия будет найдена, но непонятно в каком именно изменении.

### 5. Verify пропущен потому что "и так понятно что работает"

```
ПЛОХО:
cycle → GREEN → деплой (без verify)

ХОРОШО:
cycle → GREEN → quality-loop: verify → VERIFY REPORT зелёный → деплой
```

Почему: `cycle` проверяет один тест. `verify` проверяет 2930+ тестов, type check, coverage, doc-sync. Разница существенная.

### 6. Full snapshot на гигантском файле

```
ПЛОХО:
"Снимем snapshot omni.py (2291 строка)" → 200+ characterization тестов
→ Каждый хрупкий, ломается при смене форматирования
→ Никто не поддерживает, все пропускают

ХОРОШО:
"Снимем snapshot omni.py" → chunked approach (registry + interface + metrics + top-5)
→ 12-15 целевых тестов, каждый с чёткой целью
→ Ломаются только при реальных изменениях
```

Почему: файл > 500 строк — это не одна единица. Полный golden-master превращается в тесты-реализации, которые ловят шум вместо регрессий. Chunked approach фиксирует структуру (что существует) и поведение (как работают самые рисковые части).

---

## Telegram-Specific Test Patterns

Telegram callback handlers, FSM state machines и AI service fallback — три области, которые стандартный TDD-цикл покрывает плохо. Ниже — готовые паттерны для VIP-DXB-CatalogBot.

### 1. Callback timing tests — callback.answer() до тяжёлой работы

```python
@pytest.mark.asyncio
async def test_callback_answered_early():
    """Callback must be answered before DB/AI work to clear Telegram spinner."""
    callback = AsyncMock(spec=CallbackQuery)
    callback.data = "book:42"
    callback.from_user = MagicMock(id=123)

    await handler(callback, state=MockFSMContext())

    # answer() must be called (clears loading spinner)
    callback.answer.assert_called()
```

### 2. FSM state isolation — два пользователя не мешают друг другу

```python
@pytest.mark.asyncio
async def test_fsm_state_isolation():
    """Two users in booking FSM must not see each other's data."""
    state_user_1 = MockFSMContext(user_id=111)
    state_user_2 = MockFSMContext(user_id=222)

    await state_user_1.set_state(BookingForm.waiting_date)
    await state_user_1.update_data(block_id=42)

    await state_user_2.set_state(BookingForm.waiting_name)
    await state_user_2.update_data(block_id=99)

    # User 1's data must be intact
    data1 = await state_user_1.get_data()
    assert data1["block_id"] == 42
```

### 3. FSM timeout — очистка зависших сессий

```python
@pytest.mark.asyncio
async def test_fsm_clears_after_timeout():
    """FSM state must reset after SESSION_TIMEOUT (3600s)."""
    fsm = FSMManager()
    fsm.set_state("user:123", "booking_name", block_id=42)

    # Simulate timeout
    fsm._states["user:123"]["last_active"] = time.time() - 3700

    state = fsm.get_state("user:123")
    assert state == "IDLE"  # Should be cleared
```

### 4. AI fallback — Gemini 429 переключает на OpenAI

```python
@pytest.mark.asyncio
async def test_ai_fallback_on_gemini_failure():
    """When Gemini returns 429, should fallback to OpenAI."""
    adapter = AIAdapter()
    adapter._gemini_client = AsyncMock(
        side_effect=httpx.HTTPStatusError("429", request=..., response=...))
    adapter._openai_client = AsyncMock(return_value="OpenAI response")

    result = await adapter.search("desert safari")
    assert result == "OpenAI response"
    adapter._openai_client.assert_called_once()
```

### 5. Concurrent callback — нет race condition при дубль-тапе

```python
@pytest.mark.asyncio
async def test_concurrent_callbacks_no_race():
    """Multiple simultaneous callbacks must not create duplicate bookings."""
    results = await asyncio.gather(
        handle_confirm(mock_callback(user_id=123)),
        handle_confirm(mock_callback(user_id=123)),  # duplicate tap
    )
    # Only one booking should be created
    bookings = await db.get_bookings(user_id=123)
    assert len(bookings) == 1
```

### Telegram-specific в пирамиде тестов

| Что тестируем | Уровень | Инструмент |
|---------------|---------|------------|
| Callback answer timing | Unit | mock CallbackQuery |
| FSM isolation | Unit | MockFSMContext per user |
| FSM timeout | Unit | manipulate timestamps |
| AI fallback | Integration | mock HTTP clients |
| Concurrent callbacks | Integration | asyncio.gather |
| Full webhook flow | E2E | TestClient + HMAC |

---

## References

- `references/test-strategy.md` — полная стратегия тестирования, async паттерны, платформенная матрица
- `references/refactor-safety.md` — characterization tests, strangler fig, feature flags, rollback
- `assets/templates/test-stub-async.py` — production-ready шаблон stub-файла
- `assets/templates/refactor-checklist.md` — чеклист before/after рефакторинга
- `assets/checklists/done-definition.md` — Definition of Done для VIP-DXB-CatalogBot

**Source skills:**
- `tdd` v1.0.0 — TDD workflow (spec, stub, cycle, coverage)
- `feature-blueprint` v1.0.0 — Planning (plan, adr, diagram, db-design, breakdown)
- `code-refactor-pro` — Safe refactoring (analyze, snapshot, refactor, cleanup, verify)

**Project docs:**
- `docs/WINDOWS_LOCAL_DB_VERIFICATION.md` — Docker Postgres для локальных тестов
- `docs/TEST_DATABASE_ACCESS.md` — TEST_DATABASE_URL стратегия
- `docs/OMNI_INBOX_ROLLOUT_BACKLOG.md` — Omni Inbox P0–P3 задачи
- `data/database.py` — CatalogDB (460 async методов, паттерны миграций)
