# Redis Patterns — Расширенный справочник

Практические рецепты для VIP-DXB-CatalogBot (Python / asyncio / redis[asyncio]).

---

## 1. Connection Pool с Graceful Shutdown

```python
# core/redis_client.py

import os
import logging
from typing import Optional
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

_redis_pool: Optional[aioredis.Redis] = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


async def get_redis() -> aioredis.Redis:
    """
    Singleton Redis connection pool.
    Вызывай в начале каждой операции — возвращает пул, не создаёт новое соединение.
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_timeout=2.0,        # не блокируем надолго
            socket_connect_timeout=2.0
        )
        logger.info(f"[redis] connection pool created: {REDIS_URL}")
    return _redis_pool


async def close_redis() -> None:
    """Вызывать при shutdown приложения — корректно закрывает все соединения."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("[redis] connection pool closed")
```

### Инициализация в FastAPI (webhook-боты)

```python
# instagram_bot/app.py, whatsapp_bot/app.py, facebook_bot/app.py, viber_bot/app.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.redis_client import get_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis()          # прогрев соединения при старте
    yield
    await close_redis()        # корректное закрытие при shutdown

app = FastAPI(lifespan=lifespan)
```

### Инициализация в aiogram (Telegram bot)

```python
# bot/main.py

async def main():
    await get_redis()          # инициализируем пул
    dp = Dispatcher()
    # ... setup routers ...
    try:
        await dp.start_polling(bot)
    finally:
        await close_redis()
```

---

## 2. @cached Декоратор — полная версия с L1+L2

```python
# core/cache.py

import json
import inspect
import functools
import logging
import time
from typing import Any, Callable, Optional

from core.redis_client import get_redis

logger = logging.getLogger(__name__)

CACHE_NONE = "__none__"    # sentinel для кэширования "не найдено"
CACHE_NONE_TTL = 60        # None кэшируем ненадолго — блок могут добавить


async def cache_get(key: str) -> tuple[bool, Any]:
    """
    Возвращает (found, value).
    found=True даже если value=None (кэшированный None).
    Graceful: при ошибке Redis → (False, None), продолжаем без кэша.
    """
    try:
        r = await get_redis()
        raw = await r.get(key)
        if raw is None:
            return False, None
        if raw == CACHE_NONE:
            return True, None          # кэшированный "не существует"
        return True, json.loads(raw)
    except Exception as e:
        logger.warning(f"[redis] cache_get error key={key}: {e}")
        return False, None


async def cache_set(key: str, value: Any, ttl: int = 1800) -> None:
    """Graceful: при ошибке Redis — молча пропускаем."""
    try:
        r = await get_redis()
        if value is None:
            await r.setex(key, CACHE_NONE_TTL, CACHE_NONE)
        else:
            await r.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=str))
    except Exception as e:
        logger.warning(f"[redis] cache_set error key={key}: {e}")


async def cache_delete(key: str) -> None:
    try:
        r = await get_redis()
        await r.delete(key)
    except Exception as e:
        logger.warning(f"[redis] cache_delete error key={key}: {e}")


async def cache_delete_pattern(pattern: str) -> int:
    """Удаление ключей по паттерну. Осторожно на проде с большим числом ключей."""
    try:
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            deleted = await r.delete(*keys)
            logger.info(f"[redis] deleted {deleted} keys matching {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.warning(f"[redis] cache_delete_pattern error pattern={pattern}: {e}")
        return 0


def cached(key_template: str, ttl: int = 1800):
    """
    Декоратор cache-aside (L2 Redis) для async методов класса и функций.

    key_template: шаблон с {arg_name} плейсхолдерами
    ttl: время жизни в секундах

    Примеры:
        @cached("block:{block_id}", ttl=1800)
        async def get_block(self, block_id: int): ...

        @cached("catalog:cats:{emirate}", ttl=3600)
        async def get_categories(self, emirate: str): ...

    Поддерживает:
    - CACHE_NONE_SENTINEL (None значения не вызывают повторный PostgreSQL)
    - Graceful degradation при Redis down
    - Structured logging cache hits/misses
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = dict(bound.arguments)
            params.pop("self", None)
            params.pop("cls", None)

            try:
                key = key_template.format(**params)
            except KeyError as e:
                logger.warning(f"[redis] cache key format error {key_template}: {e}")
                return await func(*args, **kwargs)

            found, value = await cache_get(key)
            if found:
                logger.debug(f"[redis] cache hit: {key}")
                return value

            logger.debug(f"[redis] cache miss: {key}")
            result = await func(*args, **kwargs)
            await cache_set(key, result, ttl=ttl)
            return result

        return wrapper
    return decorator
```

---

## 3. RedisFSMManager — полная реализация

Подробный код: `assets/templates/redis-fsm-manager.py`

```python
# Быстрая справка: singleton экземпляры для каждой платформы
from core.fsm_redis import RedisFSMManager

ig_fsm = RedisFSMManager("ig")   # instagram
wa_fsm = RedisFSMManager("wa")   # whatsapp
fb_fsm = RedisFSMManager("fb")   # facebook
vb_fsm = RedisFSMManager("vb")   # viber

# API идентичен core/fsm.py FSMManager:
state = await ig_fsm.get_state(sender_id)
await ig_fsm.set_state(sender_id, "WAITING_NAME")
data  = await ig_fsm.get_data(sender_id)
await ig_fsm.update_data(sender_id, name="Иван", date="15.03.2026")
await ig_fsm.clear(sender_id)
```

---

## 4. Sliding Window Rate Limiter

```python
# core/rate_limiter.py

import time
import logging
from core.redis_client import get_redis

logger = logging.getLogger(__name__)


async def is_rate_limited(
    user_id: int,
    platform: str = "tg",
    limit: int = 3,
    window: int = 1
) -> bool:
    """
    Sliding window rate limiter через Redis sorted set.

    limit: максимум запросов за window секунд
    window: размер окна в секундах

    Работает across instances (несколько воркеров FastAPI).
    При Redis down: возвращает False (пропускаем, не блокируем).
    """
    try:
        r = await get_redis()
        key = f"ratelimit:{platform}:{user_id}"
        now = time.time()
        window_start = now - window

        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)  # удаляем старые записи
        pipe.zadd(key, {str(now): now})              # добавляем текущий
        pipe.zcard(key)                              # считаем в окне
        pipe.expire(key, window * 2)                 # TTL = 2x window

        results = await pipe.execute()
        count = results[2]

        if count > limit:
            logger.debug(f"[ratelimit] {platform}:{user_id} limited: {count}/{limit} in {window}s")
            return True
        return False

    except Exception as e:
        logger.warning(f"[ratelimit] Redis error: {e}")
        return False  # при сбое Redis — не блокируем
```

---

## 5. Distributed Lock (Stampede Protection)

```python
# core/redis_lock.py

import asyncio
import logging
from contextlib import asynccontextmanager
from core.redis_client import get_redis

logger = logging.getLogger(__name__)

LOCK_TTL = 30  # 30 секунд максимум на операцию


@asynccontextmanager
async def redis_lock(lock_name: str, timeout: int = LOCK_TTL):
    """
    Distributed lock через Redis SET NX.
    Предотвращает параллельный re-import каталога несколькими воркерами.

    Использование:
        async with redis_lock("catalog_import"):
            await seed_catalog()

        async with redis_lock("currency_update", timeout=10):
            await update_currency_rates()
    """
    r = await get_redis()
    key = f"lock:{lock_name}"
    acquired = False

    try:
        acquired = await r.set(key, "1", ex=timeout, nx=True)
        if not acquired:
            raise RuntimeError(f"[lock] '{lock_name}' already held by another process")
        logger.debug(f"[lock] acquired: {lock_name}")
        yield
    finally:
        if acquired:
            await r.delete(key)
            logger.debug(f"[lock] released: {lock_name}")


async def get_with_stampede_protection(cache_key: str, fetch_fn, ttl: int = 1800):
    """
    Cache-aside с защитой от stampede.
    Только один запрос идёт в PostgreSQL при промахе, остальные ждут.
    """
    from core.cache import cache_get, cache_set

    found, value = await cache_get(cache_key)
    if found:
        return value

    lock_key = f"lock:populating:{cache_key}"
    r = await get_redis()

    if await r.set(lock_key, "1", ex=5, nx=True):
        try:
            result = await fetch_fn()
            await cache_set(cache_key, result, ttl=ttl)
            return result
        finally:
            await r.delete(lock_key)
    else:
        # Ждём пока первый запрос заполнит кэш (max 500ms)
        for _ in range(5):
            await asyncio.sleep(0.1)
            found, value = await cache_get(cache_key)
            if found:
                return value
        # Не дождались — идём в PostgreSQL напрямую
        return await fetch_fn()
```

---

## 6. Webhook Dedup через SET NX

```python
# core/webhook_dedup.py

import logging
from core.redis_client import get_redis

logger = logging.getLogger(__name__)
DEDUP_TTL = 86400  # 24 часа — Meta ретраит до 24ч


async def mark_processed(platform: str, message_id: str) -> bool:
    """
    Атомарно отмечает message_id как обработанный через Redis SET NX.

    Возвращает True  — это ПЕРВЫЙ раз (надо обрабатывать).
    Возвращает False — дубликат (пропустить без ошибки).

    При Redis down: возвращает True (лучше дубль, чем потеря сообщения).
    """
    try:
        r = await get_redis()
        key = f"dedup:{platform}:{message_id}"
        # SET key "1" EX 86400 NX — атомарно, только если не существует
        result = await r.set(key, "1", ex=DEDUP_TTL, nx=True)
        if result is True:
            logger.debug(f"[dedup] new: {platform}:{message_id}")
            return True
        else:
            logger.info(f"[dedup] duplicate skipped: {platform}:{message_id}")
            return False
    except Exception as e:
        logger.warning(f"[dedup] Redis error for {platform}:{message_id}: {e} — allowing through")
        return True  # graceful: при сбое обрабатываем
```

### Использование в Instagram

```python
# instagram_bot/handlers/common.py

from core.webhook_dedup import mark_processed

async def process_messaging_event(messaging: dict) -> None:
    sender_id = messaging.get("sender", {}).get("id", "")
    message = messaging.get("message", {})
    message_id = message.get("mid", "")   # формат: mid.xxx...

    if message_id and not await mark_processed("ig", message_id):
        return  # дубль — молча пропускаем

    text = message.get("text", "")
    await handle_text_message(sender_id, text)
```

### Использование в WhatsApp

```python
# whatsapp_bot/handlers/common.py

async def process_wa_message(msg: dict) -> None:
    msg_id = msg.get("id", "")     # формат: wamid.xxx...

    if msg_id and not await mark_processed("wa", msg_id):
        return

    # ... обработка ...
```

### Использование в Viber

```python
# viber_bot/handlers/common.py

async def process_viber_message(body: dict) -> None:
    msg_token = str(body.get("message_token", ""))  # число как строка

    if msg_token and not await mark_processed("vb", msg_token):
        return

    # ... обработка ...
```

---

## 7. Pub/Sub для Cache Invalidation Broadcast

**Когда нужно:** несколько воркеров FastAPI с L1 LRU кэшем. Один воркер обновил блок — все остальные должны сбросить L1.

```python
# core/cache_pubsub.py

import asyncio
import logging
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

INVALIDATION_CHANNEL = "cache:invalidate"

# L1 кэши, которые нужно сбрасывать по сигналу
_l1_caches: dict = {}  # name -> cache_clear функция


def register_l1_cache(name: str, clear_fn) -> None:
    """Регистрировать при старте приложения."""
    _l1_caches[name] = clear_fn


async def publish_invalidation(key_prefix: str) -> None:
    """Публикуем событие инвалидации — все воркеры услышат."""
    from core.redis_client import get_redis
    r = await get_redis()
    await r.publish(INVALIDATION_CHANNEL, key_prefix)
    logger.debug(f"[pubsub] published invalidation: {key_prefix}")


async def listen_invalidations() -> None:
    """
    Запускать как asyncio.create_task при старте приложения.
    Слушаем события инвалидации и очищаем L1 кэши.
    """
    from core.redis_client import get_redis
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(INVALIDATION_CHANNEL)

    logger.info("[pubsub] listening for cache invalidation events")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        key_prefix = message["data"]
        logger.debug(f"[pubsub] received invalidation: {key_prefix}")

        # Сбрасываем соответствующие L1 кэши
        for name, clear_fn in _l1_caches.items():
            if key_prefix in name or name in key_prefix:
                clear_fn()
                logger.debug(f"[pubsub] cleared L1 cache: {name}")
```

---

## Быстрый старт: что добавить в проект

### Зависимости

```
# requirements.txt
redis[asyncio]>=5.0.0
```

### Файловая структура

```
core/
├── redis_client.py      # connection pool, get_redis(), close_redis()
├── cache.py             # cache_get/set/delete, @cached decorator
├── fsm_redis.py         # RedisFSMManager + singleton ig/wa/fb/vb_fsm
├── webhook_dedup.py     # mark_processed() — Redis SET NX + PG fallback
├── rate_limiter.py      # is_rate_limited() — sliding window
├── redis_lock.py        # redis_lock(), get_with_stampede_protection()
└── cache_invalidator.py # on_block_updated() / on_currency_updated()
```

### .env

```
REDIS_URL=redis://redis:6379        # в Docker (имя сервиса)
# REDIS_URL=redis://localhost:6379  # локально
```

### Порядок внедрения (от быстрого к сложному)

1. `webhook_dedup.py` для IG/WA/FB/Viber — 30 мин, защита от дублей
2. `cache.py` + `@cached` для блоков каталога — 1-2 ч, -80% запросов к PG
3. `fsm_redis.py` для IG/WA/FB/Viber — 2-3 ч, FSM переживает деплой
4. `rate_limiter.py` — 30 мин, если нужен multi-instance лимит
5. L1 LRU через `async_lru_cache` для горячих ключей — 1 ч

### Диагностика через Redis CLI

```bash
# Посмотреть ключи по паттерну
redis-cli keys "catalog:*"
redis-cli keys "fsm:ig:*"
redis-cli keys "dedup:*"

# TTL ключа
redis-cli ttl "catalog:block:42"

# Значение ключа
redis-cli get "catalog:block:42"

# Удалить ключ
redis-cli del "catalog:block:42"

# Статистика памяти
redis-cli info memory

# Hit rate
redis-cli info stats | grep keyspace
```
