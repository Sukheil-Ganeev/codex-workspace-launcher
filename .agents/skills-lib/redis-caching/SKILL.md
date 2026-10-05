---
name: redis-caching
description: "Redis caching patterns для Python ботов и FastAPI. Cache-aside, TTL стратегии, webhook idempotency, FSM session store, cache invalidation. Используй при оптимизации горячих callback-путей, хранении FSM-состояний, дедупликации webhook-сообщений или кэшировании каталога."
license: Apache-2.0
metadata:
---
# Redis Caching — Скилл для Python ботов и FastAPI

## Overview

**Redis рядом с PostgreSQL — не замена, а дополнение.**

PostgreSQL — источник правды (данные хранятся вечно, транзакции, надёжность).
Redis — скорость доступа (миллисекунды, in-memory, временные данные).

Правило: если данные меняются редко, читаются часто, и потеря при перезапуске не критична — Redis.

### Почему нужен Redis в VIP-DXB-CatalogBot

| Проблема | Сейчас | С Redis |
|---|---|---|
| Каждый тап кнопки меню → запрос в PostgreSQL | ~10-30ms | ~0.5ms |
| FSM состояния IG/WA/FB/Viber в памяти | теряются при рестарте | persist |
| Дедупликация Meta webhook | нет механизма | idempotency key |
| Курсы валют в PostgreSQL | лишний round-trip | sub-ms |
| 285 блоков каталога читаются при каждом просмотре | N запросов/сек | 1 warm hit |

---

## When to Use

### Используй Redis, если:

**1. Callback hot paths (кнопки меню)**
- Пользователь нажимает кнопку Emirates → Categories → Block
- Каждый шаг сейчас делает запрос в PostgreSQL
- Данные меняются раз в день (максимум)
- Сигнал: `callback_query` приходит сотни раз в минуту

**2. FSM состояния webhook-ботов (IG/WA/FB/Viber)**
- Сейчас: in-memory dict в `core/fsm.py` → теряется при рестарте сервиса
- При падении FastAPI-сервиса пользователь теряет шаг бронирования
- Redis даёт persist FSM без PostgreSQL overhead

**3. Webhook idempotency (дедупликация)**
- Meta (Instagram, WhatsApp, Facebook) повторно присылает webhook при timeout
- Если обработчик не ответил за 20 секунд — Meta шлёт повтор
- Без дедупликации: дублирующиеся бронирования
- Redis SET с NX (only if not exists) — стандартное решение

**4. Каталог (285 блоков)**
- `get_block(id)`, `get_blocks_by_category(cat_id)` вызываются при каждом просмотре
- Блоки меняются только когда владелец редактирует через owner panel
- TTL: 30 минут + инвалидация по событию

**5. Курсы валют**
- Сейчас кэшируются в PostgreSQL таблице `currency_cache`
- Redis быстрее для read-heavy данных без ACID требований
- TTL: 6 часов

**6. Rate limiting**
- ThrottleMiddleware сейчас in-memory
- Redis sliding window работает across instances (если несколько воркеров)

---

## Modes

### `cache-design`
Проектирование стратегии кэширования для конкретного случая.

Вопросы для режима:
- Что кэшируем? (объект, список, счётчик)
- Как часто меняется?
- Что произойдёт если кэш устарел? (stale data acceptable?)
- Нужна ли инвалидация по событию?

Выход: ключ Redis, TTL, стратегия (cache-aside / write-through / write-behind).

### `session-store`
FSM состояния через Redis вместо in-memory dict.

Использовать когда:
- Webhook-боты (IG/WA/FB/Viber) с multi-step FSM
- Нужна устойчивость к рестарту сервиса
- Несколько воркеров FastAPI

Ключ: `fsm:{platform}:{user_id}` → JSON с state + data + updated_at

### `webhook-dedup`
Дедупликация входящих webhook-сообщений по idempotency key.

Использовать когда:
- Meta Webhooks (Instagram, WhatsApp, Facebook)
- Viber (может дублировать при network issues)
- Любой webhook без гарантии exactly-once delivery

Ключ: `dedup:{platform}:{message_id}` → "1", TTL 24h

### `invalidation`
Стратегии инвалидации кэша.

Три подхода:
1. **TTL-only** — истекает сам, допустимо stale на период TTL
2. **Event-based** — при изменении данных явно удаляем ключ
3. **Versioned keys** — `catalog:v{version}:block:{id}`, смена версии = инвалидация всего

### `benchmark`
Оценка где Redis даст прирост.

Метрика: замерить время `db.get_block(id)` × число вызовов в час.
Формула прироста: `(db_time - redis_time) × calls_per_hour / 1000 = saved_seconds_per_hour`

---

## Patterns

### Cache-Aside (Read-Through)

Самый распространённый паттерн. Логика: сначала Redis, при промахе — PostgreSQL + запись в Redis.

```python
import json
import asyncio
from typing import Optional, Any
import aioredis

redis: aioredis.Redis = None

async def get_redis() -> aioredis.Redis:
    global redis
    if redis is None:
        redis = await aioredis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
    return redis

async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    value = await r.get(key)
    if value:
        return json.loads(value)
    return None

async def cache_set(key: str, value: Any, ttl: int = 1800) -> None:
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value, ensure_ascii=False))

async def cache_delete(key: str) -> None:
    r = await get_redis()
    await r.delete(key)
```

#### Декоратор cache-aside для asyncio функций

```python
import functools
from typing import Callable, Optional

def cached(key_template: str, ttl: int = 1800):
    """
    Декоратор кэширования для async функций.

    key_template: шаблон ключа с {arg_name} плейсхолдерами

    Пример:
        @cached("block:{block_id}", ttl=1800)
        async def get_block(self, block_id: int) -> dict:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Строим ключ из аргументов
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = dict(bound.arguments)
            # убираем self
            params.pop("self", None)

            key = key_template.format(**params)

            # Попытка из кэша
            cached_value = await cache_get(key)
            if cached_value is not None:
                return cached_value

            # Промах — идём в источник
            result = await func(*args, **kwargs)

            if result is not None:
                await cache_set(key, result, ttl=ttl)

            return result
        return wrapper
    return decorator
```

#### Применение в CatalogDB

```python
# В data/database.py

@cached("catalog:block:{block_id}", ttl=1800)
async def get_block(self, block_id: int) -> Optional[dict]:
    async with self.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM blocks WHERE id = $1", block_id
        )
        return dict(row) if row else None

@cached("catalog:category:{category}", ttl=3600)
async def get_blocks_by_category(self, category: str) -> list:
    async with self.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM blocks WHERE category = $1 AND is_active = true",
            category
        )
        return [dict(r) for r in rows]
```

---

### Write-Through

Записываем одновременно в Redis и PostgreSQL. Гарантирует актуальность кэша.
Используй для данных, которые обновляются редко но читаются очень часто.

```python
async def update_block_price(self, block_id: int, price: float) -> None:
    # 1. Обновляем PostgreSQL (источник правды)
    async with self.pool.acquire() as conn:
        await conn.execute(
            "UPDATE blocks SET price = $1 WHERE id = $2",
            price, block_id
        )

    # 2. Инвалидируем кэш (проще, чем write-through)
    await cache_delete(f"catalog:block:{block_id}")

    # Или write-through: обновляем кэш новым значением
    updated_block = await self._fetch_block_raw(block_id)
    if updated_block:
        await cache_set(f"catalog:block:{block_id}", updated_block, ttl=1800)
```

---

### FSM Session Store в Redis

Замена in-memory dict для webhook-ботов (IG/WA/FB/Viber).

```python
# core/fsm_redis.py

import json
from datetime import datetime
from typing import Optional, Any

FSM_TTL = 3600  # 1 час — совпадает с текущим timeout в core/fsm.py

class RedisFSMManager:
    """
    Redis-backed FSM manager для webhook-ботов.
    Drop-in замена для core/fsm.py FSMManager.

    Ключи: fsm:{platform}:{user_id}
    """

    def __init__(self, platform: str):
        self.platform = platform

    def _key(self, user_id: str) -> str:
        return f"fsm:{self.platform}:{user_id}"

    async def get_state(self, user_id: str) -> Optional[str]:
        data = await cache_get(self._key(user_id))
        return data.get("state") if data else None

    async def set_state(self, user_id: str, state: str) -> None:
        data = await cache_get(self._key(user_id)) or {}
        data["state"] = state
        data["updated_at"] = datetime.utcnow().isoformat()
        await cache_set(self._key(user_id), data, ttl=FSM_TTL)

    async def get_data(self, user_id: str) -> dict:
        data = await cache_get(self._key(user_id))
        return data.get("form_data", {}) if data else {}

    async def update_data(self, user_id: str, **kwargs) -> None:
        data = await cache_get(self._key(user_id)) or {}
        form_data = data.get("form_data", {})
        form_data.update(kwargs)
        data["form_data"] = form_data
        data["updated_at"] = datetime.utcnow().isoformat()
        await cache_set(self._key(user_id), data, ttl=FSM_TTL)

    async def clear(self, user_id: str) -> None:
        await cache_delete(self._key(user_id))

    async def get_full(self, user_id: str) -> Optional[dict]:
        return await cache_get(self._key(user_id))

# Использование в instagram_bot/fsm.py:
# ig_fsm = RedisFSMManager("ig")
# wa_fsm = RedisFSMManager("wa")
# fb_fsm = RedisFSMManager("fb")
# vb_fsm = RedisFSMManager("vb")
```

---

### Webhook Idempotency (Meta + Viber)

```python
# Middleware для FastAPI webhook-ботов

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

DEDUP_TTL = 86400  # 24 часа

async def is_duplicate_webhook(platform: str, message_id: str) -> bool:
    """
    Возвращает True если это повторный webhook.
    Атомарно устанавливает ключ (SET NX).
    """
    r = await get_redis()
    key = f"dedup:{platform}:{message_id}"
    # SET key "1" EX 86400 NX — атомарно, только если не существует
    result = await r.set(key, "1", ex=DEDUP_TTL, nx=True)
    # result = True если ключ был создан (первый раз)
    # result = None если ключ уже существовал (дубликат)
    return result is None

# В обработчике Instagram/WhatsApp/Facebook:
async def handle_message(messaging: dict) -> None:
    message_id = messaging.get("message", {}).get("mid", "")
    sender_id = messaging.get("sender", {}).get("id", "")

    if not message_id:
        return

    # Дедупликация
    if await is_duplicate_webhook("ig", message_id):
        logger.info(f"[instagram] duplicate webhook ignored: {message_id}")
        return

    # Обрабатываем первый раз
    await process_message(sender_id, messaging)
```

---

### Sliding Window Rate Limiter

```python
import time

async def is_rate_limited(user_id: int, platform: str = "tg",
                          limit: int = 3, window: int = 1) -> bool:
    """
    Sliding window rate limiter.
    limit: максимум запросов
    window: за сколько секунд
    """
    r = await get_redis()
    key = f"ratelimit:{platform}:{user_id}"
    now = time.time()
    window_start = now - window

    pipe = r.pipeline()
    # Удаляем старые записи вне окна
    pipe.zremrangebyscore(key, 0, window_start)
    # Добавляем текущий запрос
    pipe.zadd(key, {str(now): now})
    # Считаем запросы в окне
    pipe.zcard(key)
    # Устанавливаем TTL
    pipe.expire(key, window * 2)

    results = await pipe.execute()
    count = results[2]

    return count > limit
```

---

### Distributed Lock (для обновления каталога)

Предотвращает одновременный re-import каталога несколькими воркерами.

```python
import asyncio
from contextlib import asynccontextmanager

LOCK_TTL = 30  # 30 секунд максимум на операцию

@asynccontextmanager
async def redis_lock(lock_name: str, timeout: int = LOCK_TTL):
    """
    Distributed lock через Redis SET NX.

    Использование:
        async with redis_lock("catalog_import"):
            await seed_catalog()
    """
    r = await get_redis()
    key = f"lock:{lock_name}"
    acquired = False

    try:
        acquired = await r.set(key, "1", ex=timeout, nx=True)
        if not acquired:
            raise RuntimeError(f"Lock '{lock_name}' already held")
        yield
    finally:
        if acquired:
            await r.delete(key)
```

---

## TTL Стратегии

### Рекомендуемые TTL для VIP-DXB-CatalogBot

| Данные | Ключ | TTL | Инвалидация |
|--------|------|-----|------------|
| Главное меню (эмираты) | `menu:emirates` | 1 час | при изменении блока |
| Список категорий | `menu:cats:{emirate}` | 1 час | при изменении блока |
| Карточка блока | `catalog:block:{id}` | 30 минут | при обновлении owner'ом |
| Список блоков категории | `catalog:category:{cat}` | 30 минут | при изменении любого блока |
| FSM состояние (IG/WA/FB/VB) | `fsm:{platform}:{user_id}` | 1 час | при clear() |
| Idempotency key (webhook) | `dedup:{platform}:{msg_id}` | 24 часа | не нужна |
| Курсы валют | `currency:{pair}` | 6 часов | при обновлении |
| Сессия пользователя | `session:{platform}:{user_id}` | 24 часа | при logout |
| Rate limit bucket | `ratelimit:{platform}:{user_id}` | ~2 секунды | auto-expire |
| Distributed lock | `lock:{name}` | 30 секунд | при release |
| Bestsellers список | `catalog:bestsellers` | 15 минут | при новом бронировании |

### Правило выбора TTL

- **Секунды (1-60)**: rate limiting, locks
- **Минуты (5-60)**: данные каталога с частыми изменениями
- **Часы (1-6)**: FSM, курсы валют, профили пользователей
- **Сутки (24)**: idempotency keys, сессии

---

## Docker Compose

Добавить Redis в `deploy/docker-compose.prod.yml`:

```yaml
services:
  # ... существующие сервисы ...

  redis:
    image: redis:7-alpine
    container_name: catalog-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - catalog-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  # ... существующие volumes ...
  redis_data:
```

### Переменная окружения

Добавить в `.env` и `.env.prod`:
```
REDIS_URL=redis://redis:6379  # в Docker (имя сервиса)
# REDIS_URL=redis://localhost:6379  # локально
```

### Инициализация в боте

```python
# bot/main.py или core/config.py

import aioredis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def init_redis():
    return await aioredis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20
    )
```

---

## Common Mistakes

### 1. Кэшировать изменяемые данные без инвалидации
**Проблема**: бронирование изменилось в PostgreSQL, но пользователь видит старый статус из кэша.
**Решение**: при каждом update/delete — `await cache_delete(key)` или write-through.

### 2. Кэшировать None
**Проблема**: если объекта нет в БД, декоратор снова идёт в PostgreSQL при каждом запросе.
**Решение**: кэшировать специальный sentinel (`"__none__"`) с коротким TTL.

```python
CACHE_NONE_SENTINEL = "__none__"
CACHE_NONE_TTL = 60  # 1 минута

async def cache_get_with_none(key: str) -> tuple[bool, Any]:
    value = await cache_get(key)
    if value == CACHE_NONE_SENTINEL:
        return True, None  # кэшированный None
    if value is not None:
        return True, value  # кэшированные данные
    return False, None  # промах
```

### 3. Гонки при параллельных промахах (Cache Stampede)
**Проблема**: 100 запросов одновременно промахнулись по кэшу → 100 запросов в PostgreSQL.
**Решение**: distributed lock на время первого запроса, остальные ждут.

```python
async def get_with_lock(key: str, fetch_fn, ttl: int = 1800):
    value = await cache_get(key)
    if value:
        return value

    lock_key = f"populating:{key}"
    r = await get_redis()

    # Пробуем захватить lock
    if await r.set(lock_key, "1", ex=5, nx=True):
        try:
            value = await fetch_fn()
            if value:
                await cache_set(key, value, ttl=ttl)
            return value
        finally:
            await r.delete(lock_key)
    else:
        # Ждём пока lock освободится
        for _ in range(10):
            await asyncio.sleep(0.1)
            value = await cache_get(key)
            if value:
                return value
        return await fetch_fn()
```

### 4. Хранить в Redis то, что там не должно быть
**Не кэшировать**:
- Данные бронирований (критичны, нужны транзакции)
- Финансовые данные (точность важнее скорости)
- Данные, которые ВСЕГДА должны быть актуальными
- Большие объекты (>1MB) — Redis не для этого

### 5. Забыть про сериализацию
Redis хранит строки. Python dict/list нужно сериализовать через `json.dumps`.
Всегда указывать `ensure_ascii=False` для кириллицы.

### 6. Не обрабатывать недоступность Redis
Redis может быть недоступен. Используй graceful degradation:

```python
async def safe_cache_get(key: str) -> Optional[Any]:
    try:
        return await cache_get(key)
    except Exception:
        return None  # Работаем без кэша

async def safe_cache_set(key: str, value: Any, ttl: int = 1800) -> None:
    try:
        await cache_set(key, value, ttl=ttl)
    except Exception:
        pass  # Молча пропускаем — данные придут из PostgreSQL
```

---

## Quick Reference

### Команды Redis CLI (диагностика)

```bash
# Посмотреть все ключи (осторожно на проде!)
redis-cli keys "*"

# Посмотреть ключи по паттерну
redis-cli keys "catalog:*"
redis-cli keys "fsm:ig:*"

# TTL ключа
redis-cli ttl "catalog:block:42"

# Значение ключа
redis-cli get "catalog:block:42"

# Удалить ключ
redis-cli del "catalog:block:42"

# Удалить по паттерну (осторожно!)
redis-cli keys "catalog:*" | xargs redis-cli del

# Статистика
redis-cli info memory
redis-cli info stats
```

### Зависимости

```
# requirements.txt
aioredis>=2.0.0
# или более новый вариант:
redis[asyncio]>=5.0.0
```

### Выбор библиотеки

| Библиотека | Когда использовать |
|---|---|
| `aioredis>=2.0` | Python 3.8+, asyncio, рекомендуется |
| `redis[asyncio]>=5.0` | Новый unified клиент (redis-py 5.0+) |
| `redis-py` (sync) | Только если нет async контекста |

`aioredis` с версии 2.0 объединён с `redis-py`. В новых проектах используй `redis[asyncio]`.

### Паттерн выбора

```
Данные часто читаются, редко меняются?
  → cache-aside + TTL

Данные меняются — нужно обновить кэш сразу?
  → write-through или инвалидация при изменении

Webhook может прийти дважды?
  → idempotency key (SET NX)

FSM состояние нужно пережить рестарт?
  → Redis session store

Несколько воркеров, нужна координация?
  → distributed lock
```
