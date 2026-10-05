---
name: performance-layer
description: "Горячие пути быстрые, webhook без дублей, каталог в памяти. Объединяет Redis caching, DB optimization и webhook reliability в единый performance workflow. Используй при оптимизации callback hot paths, хранении FSM в Redis, дедупликации Meta/Viber webhook, добавлении Redis в проект или настройке performance мониторинга. Режимы: benchmark, cache-design, session-store, webhook-dedup, monitoring."
license: Apache-2.0
metadata:
---
# Performance Layer — Горячие пути быстрые, webhook без дублей

## Overview

### Проблема

В VIP-DXB-CatalogBot три хронических узких места:

1. **Callback hot paths медленные.** Каждый тап кнопки меню (Emirates → Categories → Block) делает 1-3 запроса в PostgreSQL. При 100 одновременных пользователях это 300 round-trip в секунду. PostgreSQL справляется, но задержка 10-30ms ощутима — Telegram показывает "загрузка".

2. **FSM webhook-ботов теряется при рестарте.** IG/WA/FB/Viber хранят состояние бронирования в `core/fsm.py` in-memory. При перезапуске FastAPI-сервиса (деплой, падение, OOM) пользователь на шаге 5 из 8 теряет весь прогресс формы.

3. **Meta/Viber дублируют webhook.** Если обработчик не ответил за 20 секунд — Meta повторяет доставку. Без дедупликации одно сообщение клиента создаёт несколько бронирований.

### Архитектура решения: 3 уровня

```
Запрос → L1 (in-process LRU, 1ms) → L2 (Redis, 5ms) → L3 (PostgreSQL, 20ms)

PostgreSQL = источник правды (данные хранятся вечно, транзакции, надёжность)
Redis      = скорость доступа (миллисекунды, in-memory, временные данные)
L1 LRU     = нулевые задержки для самых горячих данных (меню, списки эмиратов)
```

Правило: если данные меняются редко, читаются часто, и потеря при перезапуске не критична — Redis.

### L1 + L2 + L3 Cache Architecture

```
Request
   │
   ▼
L1: functools.lru_cache (in-process)
   │  Ёмкость: 50-200 items
   │  TTL: 30-60 секунд (через time-based wrapper)
   │  Задержка: ~1ms (RAM)
   │  Промах ↓
   ▼
L2: Redis (сетевой кэш)
   │  Ёмкость: 256MB (allkeys-lru eviction)
   │  TTL: 30 минут — 24 часа (по типу данных)
   │  Задержка: ~5ms (локальный Docker)
   │  Промах ↓
   ▼
L3: PostgreSQL
      Источник правды
      Задержка: ~20ms (asyncpg pool)

Инвалидация (owner обновил блок):
  → DELETE L1 entry (cache_clear() для lru_cache группы)
  → DELETE Redis key (cache_delete)
  → Следующий запрос repopulates L1 + L2 автоматически

Graceful degradation (Redis down):
  → L1 + PostgreSQL напрямую (без retry loop, без крэша)
  → Логируем warning, продолжаем работу
```

---

## When to Use

Активируй этот скилл, если:

- **Callback hot paths** — кнопки меню каталога, главное меню, список эмиратов дают видимую задержку
- **FSM потеря при деплое** — пользователи на IG/WA/FB/Viber жалуются что форма "сбросилась"
- **Дублирующиеся бронирования** — одно сообщение создаёт 2-3 записи в таблице `bookings`
- **Добавляешь Redis в проект** — нужна архитектура, TTL таблица, порядок внедрения
- **Performance review** — перед деплоем крупного релиза хочешь знать текущие задержки
- **Omni Inbox расширение** — добавляешь новый платформенный коннектор, нужна надёжная дедупликация
- **DLQ мониторинг** — видишь нарастающую очередь в `webhook_dlq`, нужны метрики

---

## Modes

### `benchmark`

**Назначение:** замерить текущие задержки перед оптимизацией. Без данных нет смысла оптимизировать.

**Промт:**
```
performance-layer: benchmark / target: "callback меню каталога"
performance-layer: benchmark / target: "get_block + get_categories"
performance-layer: benchmark / target: "FSM operations для IG booking"
```

**Что делает:**
1. Добавляет `time.perf_counter()` измерения на ключевые пути
2. Запускает простой нагрузочный тест (50-100 последовательных вызовов)
3. Строит таблицу задержек: метод, p50, p95, p99, вызовов/сек
4. Рассчитывает формулу прироста: `(db_time - redis_time) × calls_per_hour / 1000 = saved_seconds_per_hour`
5. Рекомендует: если p95 > 10ms → `cache-design`; если FSM ошибки при рестарте → `session-store`

**Вывод:** таблица задержек + автоматические рекомендации по следующему режиму.

**Инструменты:**
```python
import time
import cProfile
import asyncio

# Простой замер
start = time.perf_counter()
result = await db.get_block(block_id)
elapsed_ms = (time.perf_counter() - start) * 1000
print(f"[benchmark] get_block({block_id}): {elapsed_ms:.2f}ms")

# Нагрузочный тест (50 вызовов)
times = []
for _ in range(50):
    start = time.perf_counter()
    await db.get_block(block_id)
    times.append((time.perf_counter() - start) * 1000)

import statistics
print(f"p50={statistics.median(times):.1f}ms  p95={sorted(times)[int(len(times)*0.95)]:.1f}ms")
```

**Synergy:** после замера → автоматически предлагает следующий режим:
- p95 > 10ms для DB calls → `cache-design`
- FSM errors при рестарте → `session-store`
- Duplicate webhook events → `webhook-dedup`

---

### `cache-design`

**Назначение:** разработать стратегию кэширования для конкретного случая.

**Промт:**
```
performance-layer: cache-design / what: "285 блоков каталога + главное меню"
performance-layer: cache-design / what: "курсы валют + bestsellers"
performance-layer: cache-design / what: "get_categories_by_emirate"
```

**Вопросы для режима:**
- Что кэшируем? (объект, список, счётчик)
- Как часто меняется? (разы в день / разы в час / в реальном времени)
- Что произойдёт если кэш устарел на 30 минут? (stale data acceptable?)
- Нужна ли инвалидация по событию? (owner panel обновляет блок)

**Вывод:** ключ Redis, TTL, стратегия (cache-aside / write-through), план инвалидации, graceful degradation.

**TTL таблица для VIP-DXB-CatalogBot:**

| Данные | Ключ Redis | TTL | Инвалидация |
|--------|-----------|-----|-------------|
| Главное меню (эмираты) | `menu:emirates` | 1 час | при изменении блока |
| Список категорий | `menu:cats:{emirate}` | 1 час | при изменении блока |
| Карточка блока | `catalog:block:{id}` | 30 мин | owner обновил блок |
| Список блоков категории | `catalog:category:{cat}` | 30 мин | при изменении любого блока |
| Bestsellers | `catalog:bestsellers` | 15 мин | при новом бронировании |
| Курсы валют | `currency:{pair}` | 6 часов | при обновлении |
| FSM состояние (webhook) | `fsm:{platform}:{user_id}` | 1 час | при clear() |
| Idempotency key | `dedup:{platform}:{msg_id}` | 24 часа | не нужна |
| Rate limit bucket | `ratelimit:{platform}:{user_id}` | 2 сек | auto-expire |
| Сессия пользователя | `session:{platform}:{user_id}` | 24 часа | при logout |
| Distributed lock | `lock:{name}` | 30 сек | при release |

**Synergy:** cache-design завершён → предлагает добавить `webhook-dedup` (они независимы, высокий impact).

---

### `session-store`

**Назначение:** мигрировать FSM webhook-ботов из in-memory dict в Redis (drop-in замена `core/fsm.py`).

**Промт:**
```
performance-layer: session-store / platforms: "IG, WA, FB, Viber"
performance-layer: session-store / platforms: "instagram"
performance-layer: session-store / recovery: true
```

**Проблема текущего решения:**
- `core/fsm.py` — in-memory dict `_states: Dict[str, Dict]`
- При перезапуске FastAPI (деплой, OOM kill, crash) все активные сессии теряются
- Пользователь на шаге 5/8 бронирования получает сброс без объяснения

**RedisFSMManager (drop-in замена):**
- Ключ: `fsm:{platform}:{user_id}` → JSON `{state, form_data, updated_at}`
- TTL: 3600s (1 час — совпадает с текущим timeout в core/fsm.py)
- Graceful degradation: если Redis down → in-memory fallback автоматически
- Recovery: при старте сканирует потерянные сессии → уведомляет пользователя

**Полный шаблон:** `assets/templates/redis-fsm-manager.py`

**Синтаксис замены:**
```python
# Было в instagram_bot/fsm.py:
from core.fsm import FSMManager
ig_fsm = FSMManager("ig")

# Стало:
from core.fsm_redis import RedisFSMManager
ig_fsm = RedisFSMManager("ig")

# API идентичен — замена без изменения обработчиков:
state = await ig_fsm.get_state(sender_id)         # то же
await ig_fsm.set_state(sender_id, "WAITING_DATE") # то же
await ig_fsm.update_data(sender_id, name=text)    # то же
await ig_fsm.clear(sender_id)                     # то же
```

**Recovery mechanism (при крэше сервиса):**
```python
# При старте FastAPI app (on_event "startup"):
async def recover_interrupted_sessions():
    # Сканируем ключи fsm:ig:* fsm:wa:* и т.д.
    # Для каждой активной сессии (state != None):
    # Отправляем пользователю: "Ваша сессия была прервана. /start для нового бронирования"
    # Очищаем состояние
    pass
```

**Synergy:** session-store готов → `benchmark` для верификации улучшения, затем `monitoring` для отслеживания FSM hit rate.

---

### `webhook-dedup`

**Назначение:** Redis + PostgreSQL идемпотентность для Meta/Viber webhook — два разных слоя, оба нужны.

**Промт:**
```
performance-layer: webhook-dedup / platform: "instagram"
performance-layer: webhook-dedup / platform: "all"   (IG + WA + FB + Viber)
performance-layer: webhook-dedup / with_dlq: true
```

**Почему нужны оба слоя:**

| Слой | Инструмент | Зачем |
|------|-----------|-------|
| L1: Redis SET NX | `dedup:{platform}:{msg_id}` TTL 24h | Скорость: дедупликация за <1ms, до DB |
| L2: PostgreSQL `processed_webhook_events` | INSERT ON CONFLICT DO NOTHING | Надёжность: audit trail, история всего |

Redis: быстро отклонить дубль до обработки. PostgreSQL: надёжно сохранить что обрабатывали (для audit, replay, debugging).

**Как определить message_id по платформе:**
```python
# Meta Instagram/Facebook:
message_id = entry["messaging"][0]["message"]["mid"]     # формат: mid.xxx

# WhatsApp:
message_id = messages[0]["id"]                           # формат: wamid.xxx

# Viber:
message_id = str(request_body.get("message_token", "")) # число как строка
```

**Поведение при Redis down:**
- Не падаем, не блокируем обработку
- Fallback: проверяем только PostgreSQL `processed_webhook_events`
- Логируем warning: `[dedup] Redis unavailable, falling back to PG for {platform}:{msg_id}`

**Полный middleware шаблон:** `assets/templates/idempotency-middleware.py`

**DLQ мониторинг:** после внедрения → `monitoring` для dashboard `webhook_dlq` items.

**Synergy:** webhook-dedup готов → `monitoring` для DLQ dashboard + Redis hit rate.

---

### `monitoring`

**Назначение:** настроить performance метрики для всего performance layer.

**Промт:**
```
performance-layer: monitoring / scope: "все боты"
performance-layer: monitoring / scope: "redis only"
performance-layer: monitoring / alerts: true
```

**Ключевые метрики:**

| Метрика | Что показывает | Норма | Тревога |
|---------|---------------|-------|---------|
| Cache hit rate L2 (Redis) | % запросов отвеченных из кэша | >80% | <60% |
| p95 callback latency | 95-й перцентиль задержки кнопок | <10ms | >50ms |
| DLQ items | необработанные webhook в очереди | 0 | >10 |
| Redis memory usage | занятая память Redis | <200MB | >240MB |
| FSM active sessions | активные сессии по платформам | мониторинг | резкий рост |
| Dedup hit rate | % пойманных дублей | 1-5% | >20% (Meta нестабилен) |

**Минимальный мониторинг (без внешних систем):**
```python
# Логировать cache hit/miss с счётчиком (раз в 5 минут в stdout):
# [monitoring] cache: hits=1240 misses=87 hit_rate=93.4% period=5min
# [monitoring] redis_memory: used=45MB maxmemory=256MB
# [monitoring] dlq: pending=0 processed_last_hour=142
# [monitoring] fsm_sessions: ig=3 wa=1 fb=0 vb=2 active
```

**Интеграция с ops-sentinel:**
```
performance-layer: monitoring + ops-sentinel: alert-design
```
Передать метрики в `ops-sentinel` скилл для настройки:
- Alert: DLQ > 10 items → Telegram notify owner
- Alert: Redis memory > 90% → автоматическая инвалидация cold keys
- Alert: p95 latency > 100ms → пора добавить L1 LRU для горячих ключей

**Synergy:** monitoring настроен → интегрирует с `ops-sentinel: alert-design` для автоматических уведомлений.

---

## Synergy Rules

Правила автоматических связей между режимами:

| Триггер | Автоматическое действие |
|---------|------------------------|
| `benchmark` выявил p95 > 10ms для DB calls | Предлагает `cache-design` для этого пути |
| `benchmark` выявил FSM ошибки при рестарте | Предлагает `session-store` |
| `benchmark` выявил дублирующиеся webhook | Предлагает `webhook-dedup` |
| `cache-design` завершён | Предлагает добавить `webhook-dedup` (независимо, высокий impact) |
| `session-store` готов | Предлагает `benchmark` для верификации + `monitoring` |
| `webhook-dedup` работает | Предлагает `monitoring` для DLQ dashboard |
| `monitoring` настроен | Интегрирует с `ops-sentinel: alert-design` |
| Добавляешь новый коннектор Omni Inbox | Всегда запускать `webhook-dedup` + `session-store` |

**Рекомендуемый порядок внедрения (от быстрого к сложному):**
1. `webhook-dedup` для IG/WA/FB/Viber — 30 минут, защита от дублей немедленно
2. `cache-design` + кэш блоков каталога — 1-2 часа, -80% запросов к PG на hot paths
3. `session-store` — 2-3 часа, FSM переживает деплой
4. `monitoring` — 1 час, видимость системы
5. `benchmark` до и после каждого шага — 15 минут, доказательство улучшений

---

## Quick Reference

### Таблица режимов

| Режим | Триггер | Время | Результат |
|-------|---------|-------|-----------|
| `benchmark` | Перед оптимизацией, диагностика | 15-30 мин | Таблица задержек + рекомендации |
| `cache-design` | Медленные DB calls, горячие пути | 1-2 часа | Архитектура L1+L2, TTL, инвалидация |
| `session-store` | FSM теряется при рестарте | 2-3 часа | RedisFSMManager drop-in замена |
| `webhook-dedup` | Дублирующиеся бронирования | 30-60 мин | Idempotency middleware Redis+PG |
| `monitoring` | После внедрения Redis | 1 час | Метрики + alerts |

### TTL Quick Reference

| Данные | TTL |
|--------|-----|
| Блок каталога | 30 мин |
| Список категорий / эмиратов | 1 час |
| Bestsellers | 15 мин |
| Курсы валют | 6 часов |
| FSM состояние | 1 час |
| Webhook dedup key | 24 часа |
| Rate limit bucket | 2 сек |
| Distributed lock | 30 сек |

### Ключевые файлы для внедрения

```
core/
├── redis_client.py      # connection pool, get_redis(), close_redis()
├── cache.py             # cache_get/set/delete, @cached decorator
├── fsm_redis.py         # RedisFSMManager + singleton ig_fsm/wa_fsm/fb_fsm/vb_fsm
├── webhook_dedup.py     # mark_processed() — Redis SET NX + PG fallback
└── cache_invalidator.py # on_block_updated / on_currency_updated
```

---

## Telegram & AI Performance Patterns

Паттерны оптимизации, специфичные для Telegram callback hot paths, webhook дедупликации без Redis и AI provider latency cascade.

### 1. Early callback.answer() — HOT vs COLD paths

```python
# HOT PATH: Menu callback (target: < 200ms)
@dp.callback_query(F.data.startswith("menu:"))
async def menu_callback(callback: CallbackQuery):
    await callback.answer()  # IMMEDIATELY — clears spinner
    # Now safe to do slower work
    await show_menu(callback)  # Can take 500ms+ for DB query

# COLD PATH: Booking confirm (needs show_alert)
@dp.callback_query(F.data == "booking:confirm")
async def confirm_booking(callback: CallbackQuery):
    # DON'T answer early — need show_alert=True after DB write
    booking = await db.create_booking(...)
    await callback.answer(f"Bronj #{booking.id}", show_alert=True)
```

**Правило:** если callback не использует `show_alert=True` и не зависит от DB-результата для текста ответа -- answer() сразу. Иначе -- answer() после операции.

### 2. Webhook dedup без Redis (in-memory + DB fallback)

Когда Redis ещё не внедрён, два уровня дедупликации уже закрывают 99% проблем:

```python
# Level 1: In-memory dedup (covers 99% of retries within seconds)
_recent_events: dict[str, float] = {}

# Level 2: DB dedup (covers retries after container restart)
# processed_webhook_events table (already exists in project)

async def is_duplicate(event_id: str, platform: str) -> bool:
    # L1: check memory
    if event_id in _recent_events:
        return True
    # L2: check DB
    if await db.is_webhook_processed(event_id):
        _recent_events[event_id] = time.time()
        return True
    # Mark as processed
    _recent_events[event_id] = time.time()
    await db.mark_webhook_processed(event_id, platform)
    return False
```

**Периодическая очистка in-memory:** удалять записи старше 5 минут каждые 60 секунд через `asyncio.create_task`.

### 3. AI provider latency cascade — adaptive timeout

```python
# Pattern: adaptive timeout per provider
PROVIDER_TIMEOUTS = {
    "gemini": 5.0,    # Fast but quota-limited
    "openai": 8.0,    # Slower but reliable
}

async def ai_with_fallback(prompt: str) -> str | None:
    # Try primary (Gemini)
    try:
        async with asyncio.timeout(PROVIDER_TIMEOUTS["gemini"]):
            return await gemini_call(prompt)
    except (asyncio.TimeoutError, httpx.HTTPStatusError):
        logger.warning("gemini_timeout_or_error, falling back to openai")

    # Fallback (OpenAI)
    try:
        async with asyncio.timeout(PROVIDER_TIMEOUTS["openai"]):
            return await openai_call(prompt)
    except (asyncio.TimeoutError, httpx.HTTPStatusError):
        logger.error("both_ai_providers_failed")
        return None  # Graceful degradation
```

**Правило:** общий бюджет одного AI-запроса не должен превышать 13 секунд (5 Gemini + 8 OpenAI). Для Telegram callback handler, где пользователь ждёт ответа, это максимально допустимая задержка.

### 4. N+1 prevention для Comparison / Bestsellers

```python
# BAD: N+1 query pattern
for block_id in comparison_ids:
    block = await db.get_block(block_id)  # 3 separate queries!

# GOOD: Batch load
blocks = await db.get_blocks_by_ids(comparison_ids)  # 1 query with IN clause
```

Применяется к: bestsellers feed, comparison cards, cross-sell recommendations, search results carousel.

---

## Common Mistakes

### 1. Cache Stampede (гонка при промахе)

**Проблема:** 100 запросов одновременно промахнулись по кэшу → 100 запросов в PostgreSQL.

**Решение:** distributed lock на время первого запроса, остальные ждут.
Шаблон: `references/redis-patterns.md` — раздел "Distributed Lock + Stampede Protection".

### 2. Нет graceful degradation

**Проблема:** Redis упал → бот не отвечает (exception не перехвачен).

**Решение:** ALL cache operations в try/except. Redis down → работаем с PostgreSQL напрямую, без retry loop.
```python
async def safe_cache_get(key):
    try:
        return await cache_get(key)
    except Exception:
        return None  # Молча — следующий слой ответит
```

### 3. PII в ключах кэша

**Проблема:** `cache:user:+79161234567` — номер телефона в Redis key.

**Решение:** только ID, никогда не email/phone/имя в ключах. Например: `session:wa:-1042`.

### 4. Кэшировать финансовые данные

**Не кэшировать:**
- Данные бронирований (нужны транзакции)
- Финансовые расчёты (точность > скорость)
- Данные оплаты/статуса платежа

### 5. Не кэшировать None (cache stampede на несуществующих объектах)

**Проблема:** блок не существует → каждый запрос идёт в PostgreSQL.

**Решение:** кэшировать sentinel `"__none__"` с коротким TTL (60 сек).
Реализовано в `core/cache.py` паттерне из `references/redis-patterns.md`.

### 6. Хранить PG-ориентированные объекты в Redis без сериализации

**Проблема:** asyncpg `Record` объект не сериализуется в JSON напрямую.

**Решение:** всегда `dict(row)` перед `json.dumps`. Декоратор `@cached` в шаблонах делает это автоматически.

---

## Подробные справочники

- `references/cache-strategies.md` — L1+L2+L3 архитектура, TTL таблица, invalidation strategies
- `references/redis-patterns.md` — все паттерны: connection pool, @cached, RedisFSMManager, rate limiter, distributed lock, webhook dedup, pub/sub
- `assets/templates/redis-fsm-manager.py` — полный RedisFSMManager drop-in
- `assets/templates/idempotency-middleware.py` — FastAPI middleware для webhook dedup
- `assets/templates/cache-decorator.py` — универсальный @cached декоратор с L1+L2
- `assets/docker/redis-compose.yml` — Redis конфиг для docker-compose.prod.yml
