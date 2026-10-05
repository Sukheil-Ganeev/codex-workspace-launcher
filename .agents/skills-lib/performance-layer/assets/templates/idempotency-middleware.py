"""
IdempotencyMiddleware — FastAPI middleware для webhook idempotency.

Два слоя защиты:
  L1 Redis SET NX  — быстро (< 1ms), 24ч TTL
  L2 PostgreSQL    — надёжно (audit trail), при Redis down

Использование в webhook-боте:
    from core.idempotency import IdempotencyMiddleware, extract_message_id

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(IdempotencyMiddleware, platform="instagram")

    # Или напрямую в обработчике (без middleware):
    from core.idempotency import check_and_mark_idempotent

    async def handle_message(messaging: dict):
        mid = messaging.get("message", {}).get("mid", "")
        if mid and not await check_and_mark_idempotent("ig", mid):
            return  # дубль
        await process(messaging)
"""

import json
import logging
from typing import Callable, Optional

import redis.asyncio as aioredis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

DEDUP_TTL = 86400  # 24 часа — Meta ретраит до 24ч


# ------------------------------------------------------------------
# Утилиты извлечения message_id по платформе
# ------------------------------------------------------------------

def extract_message_id(platform: str, payload: dict) -> Optional[str]:
    """
    Извлечь уникальный message_id из payload по платформе.

    Meta Instagram/Facebook:
      entry[0].messaging[0].message.mid  →  "mid.xxx..."
      entry[0].messaging[0].read или delivery не имеют mid — пропускаем

    WhatsApp:
      entry[0].changes[0].value.messages[0].id  →  "wamid.xxx..."

    Viber:
      message_token  →  число (строковая версия)
    """
    try:
        if platform in ("ig", "fb"):
            entry = payload.get("entry", [{}])[0]
            messaging = entry.get("messaging", [{}])[0]
            message = messaging.get("message", {})
            return message.get("mid")  # None для read/delivery событий

        elif platform == "wa":
            entry = payload.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            messages = value.get("messages", [])
            if messages:
                return messages[0].get("id")
            return None  # status updates — не дедуплицируем

        elif platform == "vb":
            token = payload.get("message_token")
            return str(token) if token else None

    except (IndexError, KeyError, TypeError):
        return None

    return None


# ------------------------------------------------------------------
# Основная функция дедупликации
# ------------------------------------------------------------------

async def check_and_mark_idempotent(platform: str, message_id: str) -> bool:
    """
    Проверить и пометить message_id как обработанный.

    Возвращает True  — первый раз (обрабатывать).
    Возвращает False — дубликат (пропустить).

    Слой 1: Redis SET NX (быстро)
    Слой 2: PostgreSQL processed_webhook_events (надёжно, при Redis down)
    """
    # Слой 1: Redis
    redis_result = await _check_redis(platform, message_id)
    if redis_result is not None:
        return redis_result

    # Слой 2: PostgreSQL fallback (Redis недоступен)
    return await _check_postgres(platform, message_id)


async def _check_redis(platform: str, message_id: str) -> Optional[bool]:
    """Redis SET NX. None — если Redis недоступен."""
    try:
        from core.redis_client import get_redis
        r = await get_redis()
        key = f"dedup:{platform}:{message_id}"
        result = await r.set(key, "1", ex=DEDUP_TTL, nx=True)
        if result is True:
            logger.debug(f"[dedup] new via Redis: {platform}:{message_id}")
            return True
        else:
            logger.info(f"[dedup] duplicate via Redis: {platform}:{message_id}")
            return False
    except Exception as e:
        logger.warning(f"[dedup] Redis unavailable, falling back to PG for {platform}:{message_id}: {e}")
        return None  # сигнал: нужен PG fallback


async def _check_postgres(platform: str, message_id: str) -> bool:
    """PostgreSQL INSERT ON CONFLICT. Fallback при Redis down."""
    try:
        from data.database import CatalogDB
        db = CatalogDB.get_instance()
        async with db.pool.acquire() as conn:
            result = await conn.fetchval(
                """
                INSERT INTO processed_webhook_events (platform, message_id, processed_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (platform, message_id) DO NOTHING
                RETURNING message_id
                """,
                platform, message_id
            )
            if result is not None:
                logger.info(f"[dedup] new via PG: {platform}:{message_id}")
                return True
            else:
                logger.info(f"[dedup] duplicate via PG: {platform}:{message_id}")
                return False
    except Exception as e:
        logger.error(f"[dedup] PG error for {platform}:{message_id}: {e}")
        return True  # при полном сбое — обрабатываем (лучше дубль, чем потеря)


# ------------------------------------------------------------------
# FastAPI Middleware (опционально — удобно для сквозной дедупликации)
# ------------------------------------------------------------------

class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware для автоматической дедупликации webhook.
    Подключать только к webhook endpoints, не ко всему приложению.

    Пример:
        # Лучше использовать check_and_mark_idempotent() напрямую в обработчике,
        # так как извлечение message_id зависит от конкретного payload формата.
        # Middleware подходит если у тебя единый webhook endpoint для одной платформы.

        app.add_middleware(IdempotencyMiddleware, platform="instagram")
    """

    def __init__(self, app: ASGIApp, platform: str):
        super().__init__(app)
        self.platform = platform

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Только для webhook POST запросов
        if request.method != "POST" or "webhook" not in request.url.path:
            return await call_next(request)

        # Читаем тело запроса один раз
        try:
            raw_body = await request.body()
            payload = json.loads(raw_body)
        except Exception:
            return await call_next(request)

        # Извлекаем message_id
        message_id = extract_message_id(self.platform, payload)
        if not message_id:
            return await call_next(request)  # не можем определить ID — пропускаем

        # Проверяем дедупликацию
        is_first = await check_and_mark_idempotent(self.platform, message_id)
        if not is_first:
            # Дубль — отвечаем 200 (Meta не должна видеть ошибок)
            return Response(
                content='{"status":"ok","dedup":"duplicate"}',
                status_code=200,
                media_type="application/json"
            )

        return await call_next(request)


# ------------------------------------------------------------------
# SQL для создания таблицы processed_webhook_events
# ------------------------------------------------------------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS processed_webhook_events (
    platform    VARCHAR(20)  NOT NULL,
    message_id  VARCHAR(255) NOT NULL,
    processed_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    PRIMARY KEY (platform, message_id)
);

-- Индекс для поиска по времени (для очистки старых записей)
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed_at
    ON processed_webhook_events (processed_at);

-- Опционально: автоматическая очистка через pg_cron (удалять записи старше 30 дней)
-- SELECT cron.schedule('clean-webhook-events', '0 2 * * *',
--   'DELETE FROM processed_webhook_events WHERE processed_at < NOW() - INTERVAL ''30 days''');
"""
