# Redis Caching — Patterns Cookbook

Практические рецепты для VIP-DXB-CatalogBot (Python / asyncio / aioredis).

---

## 1. aioredis Connection Pool Setup

```python
# core/redis_client.py

import os
import aioredis
from typing import Optional

_redis_pool: Optional[aioredis.Redis] = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def get_redis() -> aioredis.Redis:
    """
    Singleton Redis connection pool.
    Вызывай в начале каждой операции.
    """
    global _redis_pool
    if _redis_pool is None or _redis_pool.closed:
        _redis_pool = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_timeout=2.0,       # не блокируем надолго
            socket_connect_timeout=2.0
        )
    return _redis_pool

async def close_redis() -> None:
    """Вызывать при shutdown приложения."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
```

### Инициализация в FastAPI (webhook-боты)

```python
# instagram_bot/app.py, whatsapp_bot/app.py и т.д.

from fastapi import FastAPI
from core.redis_client import get_redis, close_redis

app = FastAPI()

@app.on_event("startup")
async def startup():
    await get_redis()  # прогрев соединения

@app.on_event("shutdown")
async def shutdown():
    await close_redis()
```

### Инициализация в aiogram (Telegram)

```python
# bot/main.py

async def main():
    await get_redis()  # инициализируем пул
    dp = Dispatcher()
    # ... setup routers ...
    try:
        await dp.start_polling(bot)
    finally:
        await close_redis()
```

---

## 2. Cache-Aside Decorator для asyncio функций

Универсальный декоратор. Принимает шаблон ключа с именами аргументов функции.

```python
# core/cache.py

import json
import inspect
import functools
import logging
from typing import Any, Callable, Optional
from core.redis_client import get_redis

logger = logging.getLogger(__name__)

CACHE_NONE = "__none__"   # sentinel для кэширования "не найдено"

async def cache_get(key: str) -> tuple[bool, Any]:
    """
    Возвращает (found, value).
    found=True даже если value=None (кэшированный None).
    """
    try:
        r = await get_redis()
        raw = await r.get(key)
        if raw is None:
            return False, None
        if raw == CACHE_NONE:
            return True, None
        return True, json.loads(raw)
    except Exception as e:
        logger.warning(f"[redis] cache_get error key={key}: {e}")
        return False, None

async def cache_set(key: str, value: Any, ttl: int = 1800) -> None:
    try:
        r = await get_redis()
        if value is None:
            await r.setex(key, min(ttl, 60), CACHE_NONE)  # None кэшируем ненадолго
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
            return await r.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"[redis] cache_delete_pattern error pattern={pattern}: {e}")
        return 0


def cached(key_template: str, ttl: int = 1800):
    """
    Декоратор cache-aside для async методов класса и функций.

    Примеры:
        @cached("block:{block_id}", ttl=1800)
        async def get_block(self, block_id: int): ...

        @cached("category:{emirate}:{category}", ttl=3600)
        async def get_blocks(self, emirate: str, category: str): ...
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
                return value

            result = await func(*args, **kwargs)
            await cache_set(key, result, ttl=ttl)
            return result

        return wrapper
    return decorator
```

### Применение в CatalogDB

```python
# data/database.py — фрагмент

from core.cache import cached, cache_delete, cache_delete_pattern

class CatalogDB:

    @cached("catalog:block:{block_id}", ttl=1800)
    async def get_block(self, block_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM blocks WHERE id = $1", block_id
            )
            return dict(row) if row else None

    @cached("catalog:cats:{emirate}", ttl=3600)
    async def get_categories_by_emirate(self, emirate: str) -> list:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT DISTINCT category FROM blocks WHERE emirate = $1 AND is_active = true",
                emirate
            )
            return [r["category"] for r in rows]

    async def update_block(self, block_id: int, **kwargs) -> None:
        # ... update logic ...
        # Инвалидируем кэш блока и связанные списки
        await cache_delete(f"catalog:block:{block_id}")
        await cache_delete_pattern("catalog:cats:*")  # категории могли измениться
        await cache_delete_pattern("catalog:category:*")
```

---

## 3. FSM Session в Redis (пример для IG/WA/FB/Viber)

Заменяет in-memory dict в `core/fsm.py`. При рестарте сервиса состояние сохраняется.

```python
# core/fsm_redis.py

import json
import logging
from datetime import datetime
from typing import Optional
from core.redis_client import get_redis

logger = logging.getLogger(__name__)
FSM_TTL = 3600  # 1 час


class RedisFSMManager:
    """
    Redis-backed FSM manager. Drop-in замена для core/fsm.py.

    Ключ: fsm:{platform}:{user_id}
    Значение: JSON {"state": "...", "form_data": {...}, "updated_at": "..."}
    """

    def __init__(self, platform: str):
        self.platform = platform

    def _key(self, user_id: str) -> str:
        return f"fsm:{self.platform}:{user_id}"

    async def get_state(self, user_id: str) -> Optional[str]:
        try:
            r = await get_redis()
            raw = await r.get(self._key(user_id))
            if raw:
                data = json.loads(raw)
                return data.get("state")
        except Exception as e:
            logger.warning(f"[fsm:{self.platform}] get_state error user={user_id}: {e}")
        return None

    async def set_state(self, user_id: str, state: str) -> None:
        try:
            r = await get_redis()
            raw = await r.get(self._key(user_id))
            data = json.loads(raw) if raw else {}
            data["state"] = state
            data["updated_at"] = datetime.utcnow().isoformat()
            await r.setex(self._key(user_id), FSM_TTL, json.dumps(data))
        except Exception as e:
            logger.warning(f"[fsm:{self.platform}] set_state error user={user_id}: {e}")

    async def get_data(self, user_id: str) -> dict:
        try:
            r = await get_redis()
            raw = await r.get(self._key(user_id))
            if raw:
                data = json.loads(raw)
                return data.get("form_data", {})
        except Exception as e:
            logger.warning(f"[fsm:{self.platform}] get_data error user={user_id}: {e}")
        return {}

    async def update_data(self, user_id: str, **kwargs) -> None:
        try:
            r = await get_redis()
            raw = await r.get(self._key(user_id))
            data = json.loads(raw) if raw else {}
            form_data = data.get("form_data", {})
            form_data.update(kwargs)
            data["form_data"] = form_data
            data["updated_at"] = datetime.utcnow().isoformat()
            await r.setex(self._key(user_id), FSM_TTL, json.dumps(data))
        except Exception as e:
            logger.warning(f"[fsm:{self.platform}] update_data error user={user_id}: {e}")

    async def clear(self, user_id: str) -> None:
        try:
            r = await get_redis()
            await r.delete(self._key(user_id))
        except Exception as e:
            logger.warning(f"[fsm:{self.platform}] clear error user={user_id}: {e}")

    async def get_all(self, user_id: str) -> Optional[dict]:
        """Получить всё: state + form_data."""
        try:
            r = await get_redis()
            raw = await r.get(self._key(user_id))
            return json.loads(raw) if raw else None
        except Exception:
            return None


# Singleton экземпляры для каждой платформы
ig_fsm = RedisFSMManager("ig")
wa_fsm = RedisFSMManager("wa")
fb_fsm = RedisFSMManager("fb")
vb_fsm = RedisFSMManager("vb")
```

### Использование в обработчике

```python
# instagram_bot/handlers/booking.py — фрагмент

from core.fsm_redis import ig_fsm

async def handle_booking_step(sender_id: str, text: str) -> str:
    state = await ig_fsm.get_state(sender_id)

    if state == "WAITING_NAME":
        await ig_fsm.update_data(sender_id, name=text)
        await ig_fsm.set_state(sender_id, "WAITING_DATE")
        return "Введите дату (ДД.ММ.ГГГГ):"

    elif state == "WAITING_DATE":
        await ig_fsm.update_data(sender_id, date=text)
        await ig_fsm.set_state(sender_id, "WAITING_GUESTS")
        return "Количество гостей?"

    # ...
```

---

## 4. Idempotency Middleware для FastAPI Webhook

Предотвращает двойную обработку повторных webhook-запросов от Meta.

```python
# core/webhook_dedup.py

import logging
from typing import Optional
from core.redis_client import get_redis

logger = logging.getLogger(__name__)
DEDUP_TTL = 86400  # 24 часа


async def mark_processed(platform: str, message_id: str) -> bool:
    """
    Атомарно отмечает message_id как обработанный.
    Возвращает True если это ПЕРВЫЙ раз (надо обрабатывать).
    Возвращает False если дубликат (пропустить).
    """
    try:
        r = await get_redis()
        key = f"dedup:{platform}:{message_id}"
        # SET NX EX — атомарно, только если не существует
        result = await r.set(key, "1", ex=DEDUP_TTL, nx=True)
        return result is True
    except Exception as e:
        # Если Redis недоступен — обрабатываем (лучше дубль, чем потеря)
        logger.warning(f"[dedup] Redis error for {platform}:{message_id}: {e}")
        return True
```

### Применение в обработчике Instagram

```python
# instagram_bot/handlers/common.py — фрагмент

from core.webhook_dedup import mark_processed

async def process_messaging_event(messaging: dict) -> None:
    sender_id = messaging.get("sender", {}).get("id", "")
    message = messaging.get("message", {})
    message_id = message.get("mid", "")

    # Дедупликация — пропускаем повторы
    if message_id:
        is_first = await mark_processed("ig", message_id)
        if not is_first:
            logger.info(f"[instagram] duplicate message skipped: {message_id}")
            return

    # Обрабатываем впервые
    text = message.get("text", "")
    if text:
        await handle_text_message(sender_id, text)
```

### Применение в WhatsApp

```python
# whatsapp_bot/handlers/common.py — фрагмент

async def process_wa_message(msg: dict) -> None:
    msg_id = msg.get("id", "")
    from_number = msg.get("from", "")

    if msg_id:
        if not await mark_processed("wa", msg_id):
            logger.info(f"[whatsapp] duplicate skipped: {msg_id}")
            return

    # ... обработка ...
```

---

## 5. Cache Invalidation при изменении блока каталога

Когда владелец редактирует блок через owner panel — нужно сбросить кэш.

```python
# bot/handlers/owner_catalog.py — фрагмент

from core.cache import cache_delete, cache_delete_pattern

async def handle_block_updated(block_id: int, category: str, emirate: str) -> None:
    """Вызывается после успешного UPDATE блока в PostgreSQL."""

    # Инвалидируем конкретный блок
    await cache_delete(f"catalog:block:{block_id}")

    # Инвалидируем список категорий для эмирата
    await cache_delete(f"catalog:cats:{emirate}")

    # Инвалидируем список блоков категории
    await cache_delete(f"catalog:category:{category}")

    # Инвалидируем bestsellers (блок мог там быть)
    await cache_delete("catalog:bestsellers")

    logger.info(f"[cache] invalidated block={block_id}, category={category}, emirate={emirate}")
```

### Централизованный invalidator

```python
# core/cache_invalidator.py

from core.cache import cache_delete, cache_delete_pattern
import logging

logger = logging.getLogger(__name__)

async def on_block_updated(block_id: int, **kwargs) -> None:
    """
    Вызывать после любого изменения блока (price, is_active, title, ...).
    kwargs: category, emirate — для точечной инвалидации списков.
    """
    await cache_delete(f"catalog:block:{block_id}")
    await cache_delete("catalog:bestsellers")

    if category := kwargs.get("category"):
        await cache_delete(f"catalog:category:{category}")

    if emirate := kwargs.get("emirate"):
        await cache_delete(f"catalog:cats:{emirate}")

    logger.info(f"[cache_invalidator] block={block_id} cache cleared")

async def on_currency_updated() -> None:
    """После обновления курсов валют."""
    await cache_delete_pattern("currency:*")
    logger.info("[cache_invalidator] currency cache cleared")

async def on_catalog_full_reload() -> None:
    """После импорта seed_catalog.py — сброс всего каталожного кэша."""
    count = await cache_delete_pattern("catalog:*")
    logger.info(f"[cache_invalidator] full catalog cache cleared: {count} keys")
```

---

## Быстрый старт: что добавить в проект

### 1. Зависимости

```
# requirements.txt
aioredis>=2.0.0
```

### 2. Файлы

```
core/
├── redis_client.py     # connection pool
├── cache.py            # cache_get / cache_set / cache_delete / @cached
├── fsm_redis.py        # RedisFSMManager + singleton instances
├── webhook_dedup.py    # mark_processed() для Meta webhooks
└── cache_invalidator.py # on_block_updated / on_currency_updated
```

### 3. .env

```
REDIS_URL=redis://redis:6379        # в Docker
# REDIS_URL=redis://localhost:6379  # локально
```

### 4. docker-compose.prod.yml

```yaml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
  volumes:
    - redis_data:/data
  networks:
    - catalog-network
```

### 5. Порядок внедрения (от быстрого к сложному)

1. Webhook dedup для Instagram/WhatsApp/Facebook (5 минут, высокий impact)
2. Кэш курсов валют (замена PostgreSQL round-trip)
3. Кэш блоков каталога + инвалидация из owner panel
4. FSM через Redis для IG/WA/FB/Viber (замена in-memory)
5. Rate limiting через Redis (если нужно multi-instance)
