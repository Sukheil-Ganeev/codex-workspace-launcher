"""
Универсальный @cached декоратор с поддержкой L1 (in-process LRU) + L2 (Redis).

Иерархия кэширования:
    L1: async_lru_cache (in-process dict, ~1ms)  ← для горячих глобальных данных
    L2: Redis (@cached decorator, ~5ms)           ← для всех остальных
    L3: PostgreSQL (источник правды, ~20ms)

Использование:

    # L2 только (Redis):
    from core.cache import cached

    @cached("catalog:block:{block_id}", ttl=1800)
    async def get_block(self, block_id: int) -> Optional[dict]:
        ...

    # L1+L2 (in-process LRU + Redis):
    from core.cache import cached, async_lru_cache

    @async_lru_cache(maxsize=10, ttl=60)          # L1: 60 сек, max 10 entries
    @cached("menu:emirates", ttl=3600)            # L2: 1 час в Redis
    async def get_emirates(self) -> list:
        ...

    # Инвалидация L2 при обновлении:
    from core.cache import cache_delete, cache_delete_pattern

    await cache_delete(f"catalog:block:{block_id}")
    await cache_delete_pattern("menu:cats:*")
"""

import json
import time
import inspect
import functools
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

CACHE_NONE = "__none__"    # sentinel для кэширования "не найдено"
CACHE_NONE_TTL = 60        # None кэшируем ненадолго


# ------------------------------------------------------------------
# L1: In-Process LRU Cache (для горячих глобальных данных)
# ------------------------------------------------------------------

def async_lru_cache(maxsize: int = 128, ttl: int = 60):
    """
    LRU cache для async функций с TTL.

    Подходит для:
    - Список эмиратов (7 items, меняется раз в год)
    - Глобальные настройки бота
    - Список категорий (меняется редко)

    НЕ подходит для:
    - User-specific данных (кэш не разделяется между пользователями)
    - Данных с частой инвалидацией (сложно сбрасывать точечно)

    Ограничение: при нескольких воркерах FastAPI — каждый воркер имеет
    свой L1 кэш. Для синхронизации воркеров используй Pub/Sub.
    """
    cache: dict = {}
    timestamps: dict = {}

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Строим ключ из аргументов (исключаем self/cls)
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = {k: v for k, v in bound.arguments.items() if k not in ("self", "cls")}
            cache_key = str(sorted(params.items()))

            now = time.monotonic()

            # Проверяем L1
            if cache_key in cache and (now - timestamps[cache_key]) < ttl:
                logger.debug(f"[L1] hit: {func.__name__}({params})")
                return cache[cache_key]

            logger.debug(f"[L1] miss: {func.__name__}({params})")

            # Вызываем следующий уровень (L2 Redis или L3 PostgreSQL)
            result = await func(*args, **kwargs)

            # Сохраняем в L1
            cache[cache_key] = result
            timestamps[cache_key] = now

            # LRU eviction: удаляем самый старый при превышении maxsize
            if len(cache) > maxsize:
                oldest_key = min(timestamps, key=lambda k: timestamps[k])
                del cache[oldest_key]
                del timestamps[oldest_key]

            return result

        def cache_clear():
            """Сброс всего L1 кэша функции. Вызывать при инвалидации."""
            cache.clear()
            timestamps.clear()
            logger.debug(f"[L1] cleared: {func.__name__}")

        wrapper.cache_clear = cache_clear
        return wrapper
    return decorator


# ------------------------------------------------------------------
# L2: Redis Cache Utilities
# ------------------------------------------------------------------

async def cache_get(key: str) -> tuple[bool, Any]:
    """
    Получить значение из Redis.
    Возвращает (found, value).
    found=True даже если value=None (кэшированный CACHE_NONE sentinel).
    При ошибке Redis → (False, None).
    """
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        raw = await r.get(key)
        if raw is None:
            return False, None
        if raw == CACHE_NONE:
            return True, None          # кэшированный "не существует"
        return True, json.loads(raw)
    except Exception as e:
        logger.warning(f"[redis] cache_get error key={key}: {e}")
        return False, None             # graceful degradation


async def cache_set(key: str, value: Any, ttl: int = 1800) -> None:
    """
    Сохранить значение в Redis.
    None → CACHE_NONE sentinel с коротким TTL.
    При ошибке Redis → молча игнорируем.
    """
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        if value is None:
            await r.setex(key, CACHE_NONE_TTL, CACHE_NONE)
        else:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            await r.setex(key, ttl, serialized)
    except Exception as e:
        logger.warning(f"[redis] cache_set error key={key}: {e}")


async def cache_delete(key: str) -> None:
    """Удалить ключ из Redis. При ошибке → молча игнорируем."""
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        await r.delete(key)
        logger.debug(f"[redis] deleted: {key}")
    except Exception as e:
        logger.warning(f"[redis] cache_delete error key={key}: {e}")


async def cache_delete_pattern(pattern: str) -> int:
    """
    Удалить ключи по паттерну.
    Осторожно на проде с большим числом ключей (KEYS блокирует Redis).
    Для продакшн с миллионами ключей использовать SCAN вместо KEYS.
    """
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            deleted = await r.delete(*keys)
            logger.info(f"[redis] deleted {deleted} keys matching {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.warning(f"[redis] cache_delete_pattern error {pattern}: {e}")
        return 0


# ------------------------------------------------------------------
# L2: @cached Декоратор
# ------------------------------------------------------------------

def cached(key_template: str, ttl: int = 1800):
    """
    Декоратор cache-aside (L2 Redis) для async методов и функций.

    key_template: шаблон с {arg_name} плейсхолдерами
    ttl: время жизни в секундах

    Поддерживает:
    - CACHE_NONE_SENTINEL (None не вызывает повторный PostgreSQL)
    - Graceful degradation при Redis down (работаем напрямую с PG)
    - Structured logging: [redis] cache hit/miss: key

    Примеры:
        @cached("catalog:block:{block_id}", ttl=1800)
        async def get_block(self, block_id: int): ...

        @cached("catalog:cats:{emirate}", ttl=3600)
        async def get_categories_by_emirate(self, emirate: str): ...

        @cached("currency:{pair}", ttl=21600)
        async def get_currency_rate(self, pair: str): ...

    Комбинирование L1+L2:
        @async_lru_cache(maxsize=10, ttl=60)   # L1: быстрый in-process
        @cached("menu:emirates", ttl=3600)     # L2: Redis 1 час
        async def get_emirates(self): ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Строим ключ из аргументов функции
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = dict(bound.arguments)
            params.pop("self", None)
            params.pop("cls", None)

            try:
                key = key_template.format(**params)
            except KeyError as e:
                logger.warning(f"[redis] key format error {key_template}: {e}")
                return await func(*args, **kwargs)

            # Проверяем L2 Redis
            found, value = await cache_get(key)
            if found:
                logger.debug(f"[redis] cache hit: {key}")
                return value

            logger.debug(f"[redis] cache miss: {key}")

            # Промах — идём в L3 PostgreSQL
            result = await func(*args, **kwargs)

            # Сохраняем в L2 Redis
            await cache_set(key, result, ttl=ttl)
            return result

        return wrapper
    return decorator


# ------------------------------------------------------------------
# Batch Operations (pipeline для эффективности)
# ------------------------------------------------------------------

async def cache_delete_batch(keys: list[str]) -> int:
    """
    Удалить несколько ключей одним pipeline запросом.
    Использовать при инвалидации 5+ ключей одновременно.
    """
    if not keys:
        return 0
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        pipe = r.pipeline()
        for key in keys:
            pipe.delete(key)
        results = await pipe.execute()
        deleted = sum(1 for r in results if r)
        logger.info(f"[redis] batch deleted {deleted}/{len(keys)} keys")
        return deleted
    except Exception as e:
        logger.warning(f"[redis] cache_delete_batch error: {e}")
        return 0


async def cache_get_batch(keys: list[str]) -> dict[str, Any]:
    """
    Получить несколько значений одним MGET запросом.
    Возвращает dict: {key: value} только для найденных ключей.
    """
    if not keys:
        return {}
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        values = await r.mget(*keys)
        result = {}
        for key, raw in zip(keys, values):
            if raw is not None and raw != CACHE_NONE:
                try:
                    result[key] = json.loads(raw)
                except Exception:
                    pass
        return result
    except Exception as e:
        logger.warning(f"[redis] cache_get_batch error: {e}")
        return {}
