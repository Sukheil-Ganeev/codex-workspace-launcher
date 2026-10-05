# Cache Strategies — Подробный справочник

## L1 + L2 + L3 Архитектура

### Три уровня и их роли

```
┌─────────────────────────────────────────────────────────────┐
│  L1: In-Process LRU Cache                                   │
│  functools.lru_cache / кастомный TTL wrapper                │
│  Ёмкость: 50–200 items   Задержка: ~1ms   TTL: 30–60 сек   │
│  Хранит: горячие данные текущего процесса                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ промах
┌──────────────────────────▼──────────────────────────────────┐
│  L2: Redis                                                  │
│  aioredis / redis[asyncio]                                  │
│  Ёмкость: 256MB (allkeys-lru)   Задержка: ~5ms              │
│  TTL: 30 мин – 24 ч   Хранит: каталог, FSM, dedup          │
└──────────────────────────┬──────────────────────────────────┘
                           │ промах
┌──────────────────────────▼──────────────────────────────────┐
│  L3: PostgreSQL                                             │
│  asyncpg connection pool                                    │
│  Задержка: ~20ms   Источник правды, транзакции, надёжность │
└─────────────────────────────────────────────────────────────┘
```

### Когда использовать каждый уровень

| Данные | L1 | L2 Redis | L3 PG |
|--------|----|----|------|
| Список эмиратов (7 элементов) | да, 60 сек | да, 1 ч | источник |
| Карточка блока (285 шт.) | нет — много | да, 30 мин | источник |
| FSM состояние | нет — userspecific | да, 1 ч | нет |
| Бронирование | никогда | никогда | только |
| Платёжные данные | никогда | никогда | только |

### L1 TTL-aware LRU wrapper для asyncio

Стандартный `functools.lru_cache` не поддерживает async и TTL. Обходное решение:

```python
import time
import asyncio
from functools import wraps
from typing import Any, Callable, Optional

def async_lru_cache(maxsize: int = 128, ttl: int = 60):
    """
    LRU cache для async функций с TTL.
    Для маленьких горячих наборов данных (список эмиратов, список категорий).
    """
    cache: dict = {}
    timestamps: dict = {}

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = args + tuple(sorted(kwargs.items()))
            now = time.monotonic()

            if key in cache and (now - timestamps[key]) < ttl:
                return cache[key]

            result = await func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = now

            # LRU eviction
            if len(cache) > maxsize:
                oldest_key = min(timestamps, key=lambda k: timestamps[k])
                del cache[oldest_key]
                del timestamps[oldest_key]

            return result

        def cache_clear():
            cache.clear()
            timestamps.clear()

        wrapper.cache_clear = cache_clear
        return wrapper
    return decorator


# Применение:
@async_lru_cache(maxsize=10, ttl=60)
async def get_emirates_list(db) -> list:
    return await db.get_all_emirates()
```

---

## TTL Таблица для 12 типов данных

| Тип данных | Ключ Redis | TTL | Инвалидация | Обоснование |
|-----------|-----------|-----|-------------|-------------|
| Список эмиратов | `menu:emirates` | 1 ч | при изм. блока | Меняется раз в год |
| Категории по эмирату | `menu:cats:{emirate}` | 1 ч | при изм. блока | Меняется редко |
| Карточка блока | `catalog:block:{id}` | 30 мин | owner обновил | Может меняться в день |
| Блоки категории | `catalog:category:{cat}` | 30 мин | при изм. блока | Зависит от блоков |
| Bestsellers | `catalog:bestsellers` | 15 мин | при бронировании | Обновляются чаще |
| Курсы валют | `currency:{pair}` | 6 ч | при обновлении | API обновляется редко |
| Профиль пользователя | `user:{platform}:{uid}` | 24 ч | при изм. профиля | Меняется редко |
| FSM состояние | `fsm:{platform}:{uid}` | 1 ч | при clear() | Timeout сессии |
| Idempotency key | `dedup:{platform}:{mid}` | 24 ч | не нужна | Meta ретраит 24ч |
| Rate limit bucket | `ratelimit:{platform}:{uid}` | 2 сек | auto-expire | Sliding window |
| Distributed lock | `lock:{name}` | 30 сек | при release | Max операция |
| Promocode lookup | `promo:{code}` | 15 мин | при изм. промо | Может исчерпаться |

### Правила выбора TTL

```
Данные меняются?
  └─ Никогда / раз в год     → 24ч или никогда (список эмиратов)
  └─ Раз в день максимум     → 1–6 ч (категории, курсы)
  └─ Может изменить владелец → 15–30 мин + event invalidation (блоки)
  └─ Каждую минуту           → не кэшировать (live цены, счётчики)
  └─ Пользовательская сессия → 1 ч (FSM)
  └─ Security/dedup          → 24 ч (idempotency)
```

---

## Cache-Aside vs Write-Through — когда что

### Cache-Aside (Read-Through)

**Когда использовать:** данные читаются намного чаще чем обновляются, допустимо stale на период TTL.

```
READ:  cache miss → PostgreSQL → write to cache → return
WRITE: update PostgreSQL → DELETE cache key (не update!)
```

**Для VIP-DXB-CatalogBot:** каталог блоков, категории, курсы валют.

**Плюсы:** простота, cache содержит только востребованные данные.
**Минусы:** первый запрос после промаха медленный (cold start).

### Write-Through

**Когда использовать:** данные обновляются и мгновенно нужны в кэше актуальными.

```
WRITE: update PostgreSQL → immediately write new value to cache → return
READ:  always hits cache (если не expired)
```

**Для VIP-DXB-CatalogBot:** курсы валют (обновляются раз в 6 часов, нужны сразу).

**Плюсы:** кэш всегда актуален, нет cold start после обновления.
**Минусы:** каждая запись = 2 операции (PG + Redis).

### Write-Behind (Write-Back)

**Когда НЕ использовать в этом проекте:**
- Сначала пишем в Redis, потом асинхронно в PostgreSQL
- Риск потери данных при падении Redis
- Бронирования, платежи, финансы — НИКОГДА write-behind

---

## Invalidation Strategies

### 1. TTL-only (самая простая)

```python
await cache_set(f"catalog:block:{block_id}", data, ttl=1800)
# Данные устаревают сами через 30 минут
```

**Когда:** допустимо stale на период TTL (курсы валют, списки категорий).

**Риск:** если owner обновил цену блока — пользователи видят старую 30 минут.

### 2. Event-based (рекомендуется для каталога)

```python
# После update блока в БД:
async def on_block_updated(block_id: int, category: str, emirate: str):
    await cache_delete(f"catalog:block:{block_id}")
    await cache_delete(f"catalog:category:{category}")
    await cache_delete(f"menu:cats:{emirate}")
    await cache_delete("catalog:bestsellers")
```

**Когда:** важна актуальность, есть чёткие события изменения (owner panel).

### 3. Versioned Keys

```python
# Вместо cache:block:42 используем cache:v{ver}:block:42
version = await redis.get("catalog:version") or "1"
key = f"catalog:v{version}:block:{block_id}"

# Инвалидация всего каталога сразу:
await redis.incr("catalog:version")  # все старые ключи становятся "мёртвыми"
```

**Когда:** нужно атомарно инвалидировать весь каталог (после seed_catalog.py reimport).

**Минус:** старые ключи остаются в памяти до TTL (Redis сам вытеснит через allkeys-lru).

### 4. Pub/Sub для нескольких воркеров

```python
# Если несколько FastAPI воркеров (несколько инстансов):
# Один воркер обновил блок → публикует событие → все воркеры очищают L1 LRU

import asyncio

async def publish_invalidation(block_id: int):
    r = await get_redis()
    await r.publish("cache:invalidate", f"block:{block_id}")

# В каждом воркере при старте:
async def listen_invalidations():
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("cache:invalidate")
    async for message in pubsub.listen():
        if message["type"] == "message":
            key = message["data"]  # "block:42"
            # Очищаем L1 LRU для этого ключа
            get_emirates_list.cache_clear()  # пример
```

**Когда:** несколько воркеров FastAPI с L1 LRU кэшем (каждый воркер — свой процесс).

---

## Cache Stampede — защита от гонок

**Проблема:** 100 запросов одновременно промахнулись по кэшу → 100 запросов в PostgreSQL за 1мс.

### Решение 1: Distributed Lock + короткое ожидание

```python
async def get_with_lock(cache_key: str, fetch_fn, ttl: int = 1800):
    """
    Только один запрос идёт в PostgreSQL при промахе.
    Остальные ждут и берут из кэша.
    """
    found, value = await cache_get(cache_key)
    if found:
        return value

    lock_key = f"lock:populating:{cache_key}"
    r = await get_redis()

    if await r.set(lock_key, "1", ex=5, nx=True):
        # Мы получили lock — идём в PostgreSQL
        try:
            result = await fetch_fn()
            await cache_set(cache_key, result, ttl=ttl)
            return result
        finally:
            await r.delete(lock_key)
    else:
        # Кто-то уже заполняет кэш — ждём 500мс
        for _ in range(5):
            await asyncio.sleep(0.1)
            found, value = await cache_get(cache_key)
            if found:
                return value
        # Если не дождались — идём в PostgreSQL напрямую (без кэша)
        return await fetch_fn()
```

### Решение 2: Stale-While-Revalidate (продвинутый)

Возвращаем устаревший кэш немедленно, обновляем в фоне:

```python
async def get_stale_while_revalidate(cache_key: str, fetch_fn, ttl: int = 1800):
    r = await get_redis()
    raw = await r.get(cache_key)
    remaining_ttl = await r.ttl(cache_key)

    if raw is not None:
        # Данные есть — возвращаем немедленно
        if remaining_ttl < ttl * 0.1:  # меньше 10% TTL осталось
            # Тихо обновляем в фоне
            asyncio.create_task(_background_refresh(cache_key, fetch_fn, ttl))
        return json.loads(raw)
    else:
        # Промах — ждём
        result = await fetch_fn()
        await cache_set(cache_key, result, ttl=ttl)
        return result

async def _background_refresh(cache_key: str, fetch_fn, ttl: int):
    try:
        result = await fetch_fn()
        await cache_set(cache_key, result, ttl=ttl)
    except Exception as e:
        logger.warning(f"[cache] background refresh failed {cache_key}: {e}")
```

---

## Batch Invalidation

Когда владелец редактирует 10+ блоков за раз (например, меняет цену всем экскурсиям Dubai):

```python
async def on_batch_blocks_updated(block_ids: list[int], category: str, emirate: str):
    """Эффективная batch инвалидация — один pipeline вместо N запросов."""
    r = await get_redis()
    pipe = r.pipeline()

    for block_id in block_ids:
        pipe.delete(f"catalog:block:{block_id}")

    pipe.delete(f"catalog:category:{category}")
    pipe.delete(f"menu:cats:{emirate}")
    pipe.delete("catalog:bestsellers")

    await pipe.execute()
    logger.info(f"[cache] batch invalidated {len(block_ids)} blocks, cat={category}")
```

**Правило:** если инвалидируешь 5+ ключей — используй pipeline.

---

## CACHE_NONE_SENTINEL Pattern

**Проблема:** блок с id=9999 не существует → каждый запрос идёт в PostgreSQL.

**Решение:** кэшировать факт "не существует" с коротким TTL.

```python
CACHE_NONE = "__none__"
CACHE_NONE_TTL = 60  # 1 минута — не долго, блок могут добавить

async def cache_get_with_none(key: str) -> tuple[bool, Any]:
    """
    Возвращает (found, value).
    found=True означает "ответ из кэша" — даже если value=None.
    found=False означает "промах — надо идти в PostgreSQL".
    """
    try:
        r = await get_redis()
        raw = await r.get(key)
        if raw is None:
            return False, None        # промах
        if raw == CACHE_NONE:
            return True, None         # кэшированный "не существует"
        return True, json.loads(raw)  # кэшированные данные
    except Exception:
        return False, None            # Redis down — промах

async def cache_set_with_none(key: str, value: Any, ttl: int = 1800):
    if value is None:
        await cache_set_raw(key, CACHE_NONE, min(ttl, CACHE_NONE_TTL))
    else:
        await cache_set_raw(key, json.dumps(value, ensure_ascii=False), ttl)
```
