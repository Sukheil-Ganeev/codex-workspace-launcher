"""
Production-ready FastAPI webhook handler template.
Integration Guardian — assets/templates/webhook-handler.py

Использование:
    Скопируй этот файл как основу для нового платформенного webhook endpoint.
    Замени PLATFORM_NAME, PLATFORM, SECRET_ENV_VAR, SIGNATURE_HEADER
    на конкретные значения для нужной платформы.

Поддерживаемые платформы "из коробки":
    - Meta (Instagram, WhatsApp, Facebook): META_APP_SECRET, X-Hub-Signature-256
    - Viber: VIBER_AUTH_TOKEN, X-Viber-Content-Signature
    - GitHub: GITHUB_WEBHOOK_SECRET, X-Hub-Signature-256

Таблицы в PostgreSQL (добавить в миграции data/database.py):
    - processed_webhook_events  — idempotency
    - webhook_dlq               — dead letter queue
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
from typing import Any, Callable, Coroutine

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI()

# ---------------------------------------------------------------------------
# КОНФИГУРАЦИЯ: заменить под конкретную платформу
# ---------------------------------------------------------------------------

PLATFORM = "whatsapp"                       # "instagram" | "whatsapp" | "facebook" | "viber"
SECRET_ENV_VAR = "META_APP_SECRET"          # Имя переменной окружения с секретом
SIGNATURE_HEADER = "X-Hub-Signature-256"    # Заголовок с подписью
HMAC_PREFIX = "sha256="                     # Префикс перед hex-дайджестом ("" для Viber)
EXPECTED_RESPONSE = {"status": "ok"}       # {"status": 0} для Viber


# ---------------------------------------------------------------------------
# HMAC VERIFICATION
# ---------------------------------------------------------------------------

def verify_hmac(
    raw_body: bytes,
    signature_header: str,
    secret: str,
    prefix: str = "sha256=",
) -> bool:
    """
    Timing-safe HMAC-SHA256 верификация.

    ВАЖНО:
    - raw_body должен быть СЫРЫМ телом запроса (до json.loads)
    - hmac.compare_digest() защищает от timing attack
    - secret никогда не хардкодить — только os.getenv()
    """
    if not signature_header or not secret:
        return False

    received = signature_header[len(prefix):] if signature_header.startswith(prefix) else signature_header

    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, received)


def verify_platform_signature(raw_body: bytes, signature_header: str) -> bool:
    """Верификация для конкретной платформы (настраивается через константы выше)."""
    secret = os.getenv(SECRET_ENV_VAR, "")
    if not secret:
        logger.error(f"[{PLATFORM}] {SECRET_ENV_VAR} not set — rejecting request")
        return False
    return verify_hmac(raw_body, signature_header, secret, prefix=HMAC_PREFIX)


async def get_verified_body(request: Request) -> bytes:
    """
    FastAPI dependency.
    Верифицирует подпись и возвращает raw body.
    Вызывается через Depends() — гарантирует, что тело читается один раз.
    """
    raw_body = await request.body()
    signature = request.headers.get(SIGNATURE_HEADER, "")

    if not verify_platform_signature(raw_body, signature):
        logger.warning(
            f"[{PLATFORM}] HMAC verification failed "
            f"from={request.client.host} "
            f"path={request.url.path} "
            f"signature_present={'yes' if signature else 'no'}"
        )
        raise HTTPException(status_code=403, detail="Invalid signature")

    return raw_body


# ---------------------------------------------------------------------------
# IDEMPOTENCY — PostgreSQL
# ---------------------------------------------------------------------------

async def is_already_processed(db_pool, message_id: str, platform: str) -> bool:
    """
    Проверить, было ли сообщение уже обработано.
    Окно проверки: 24 часа (защита от retry провайдера).

    Использует CatalogDB._pool из data/database.py.
    """
    result = await db_pool.fetchval(
        """
        SELECT 1 FROM processed_webhook_events
        WHERE message_id = $1 AND platform = $2
          AND processed_at > NOW() - INTERVAL '24 hours'
        """,
        message_id,
        platform,
    )
    return result is not None


async def mark_as_processed(
    db_pool,
    message_id: str,
    platform: str,
    payload_summary: str = "",
) -> None:
    """
    Пометить сообщение как обработанное.
    ON CONFLICT DO NOTHING — безопасно при concurrent запросах.
    """
    await db_pool.execute(
        """
        INSERT INTO processed_webhook_events
            (message_id, platform, payload_summary, processed_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (message_id, platform) DO NOTHING
        """,
        message_id,
        platform,
        payload_summary[:500] if payload_summary else "",  # Обрезаем длинные payload'ы
    )


# SQL для миграции (добавить в CatalogDB._migrate_vXX_idempotency):
MIGRATION_IDEMPOTENCY_SQL = """
CREATE TABLE IF NOT EXISTS processed_webhook_events (
    id           SERIAL PRIMARY KEY,
    message_id   TEXT        NOT NULL,
    platform     TEXT        NOT NULL,
    payload_summary TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (message_id, platform)
);
CREATE INDEX IF NOT EXISTS idx_pwe_processed_at
    ON processed_webhook_events (processed_at);
"""


# ---------------------------------------------------------------------------
# RETRY WITH EXPONENTIAL BACKOFF
# ---------------------------------------------------------------------------

async def retry_with_backoff(
    func: Callable[..., Coroutine[Any, Any, Any]],
    *args: Any,
    max_attempts: int = 5,
    base_delay: float = 3.0,
    backoff_multiplier: float = 3.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> Any:
    """
    Retry с exponential backoff.

    Задержки по умолчанию: 3s → 9s → 27s → 81s → 243s
    Итого максимальное ожидание ~6 минут.

    При исчерпании попыток — сохраняет в DLQ и перебрасывает исключение.
    """
    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as exc:
            last_exc = exc
            if attempt == max_attempts:
                break

            delay = base_delay * (backoff_multiplier ** (attempt - 1))
            logger.warning(
                f"[{PLATFORM}] retry attempt {attempt}/{max_attempts} failed: {exc}. "
                f"Retrying in {delay:.0f}s"
            )
            await asyncio.sleep(delay)

    # Все попытки исчерпаны
    logger.error(
        f"[{PLATFORM}] All {max_attempts} attempts exhausted: {last_exc}. Sending to DLQ."
    )
    await send_to_dlq(
        handler_name=func.__name__,
        error_message=str(last_exc),
        platform=PLATFORM,
    )
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DEAD LETTER QUEUE — PostgreSQL
# ---------------------------------------------------------------------------

async def send_to_dlq(
    handler_name: str,
    error_message: str,
    platform: str,
    payload: dict | None = None,
) -> None:
    """
    Сохранить неудачное событие в Dead Letter Queue.
    Используется для ручного разбора или повторной обработки.

    Если DLQ тоже недоступен — логируем как CRITICAL.
    """
    from data.database import CatalogDB  # noqa: PLC0415 — lazy import

    db = CatalogDB.instance()
    if db is None or db._pool is None:
        logger.critical(
            f"[dlq] Cannot save to DLQ (no DB pool): "
            f"{platform} {handler_name} — {error_message}"
        )
        return

    try:
        await db._pool.execute(
            """
            INSERT INTO webhook_dlq
                (platform, handler_name, payload, error_message, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            """,
            platform,
            handler_name,
            json.dumps(payload) if payload else None,
            error_message[:2000],
        )
        logger.error(
            f"[dlq] Saved: platform={platform} handler={handler_name} "
            f"error={error_message[:200]}"
        )
    except Exception as dlq_exc:
        logger.critical(
            f"[dlq] FAILED to save to DLQ: {dlq_exc}. "
            f"Original error: {platform} {handler_name} — {error_message}"
        )


# SQL для миграции DLQ:
MIGRATION_DLQ_SQL = """
CREATE TABLE IF NOT EXISTS webhook_dlq (
    id           SERIAL PRIMARY KEY,
    platform     TEXT        NOT NULL,
    handler_name TEXT        NOT NULL,
    payload      JSONB,
    error_message TEXT,
    resolved     BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_dlq_platform_resolved
    ON webhook_dlq (platform, resolved, created_at DESC);
"""


# ---------------------------------------------------------------------------
# WEBHOOK ENDPOINT — основной handler
# ---------------------------------------------------------------------------

@app.get(f"/webhook/{PLATFORM}")
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> int | str:
    """
    Meta webhook verification handshake (GET).
    Meta вызывает этот endpoint при настройке webhook в Developer Portal.
    Нужно вернуть hub_challenge.
    """
    verify_token = os.getenv(f"{PLATFORM.upper()}_VERIFY_TOKEN", "")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info(f"[{PLATFORM}] Webhook verified successfully")
        return int(hub_challenge)  # type: ignore[arg-type]
    logger.error(f"[{PLATFORM}] Webhook verification failed: token mismatch")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post(f"/webhook/{PLATFORM}")
async def webhook_handler(
    background_tasks: BackgroundTasks,
    raw_body: bytes = Depends(get_verified_body),  # HMAC проверен здесь
) -> JSONResponse:
    """
    Основной POST webhook handler.

    Принцип работы:
    1. HMAC верификация (через Depends — до этой функции)
    2. Немедленный 200 OK (провайдер ждёт max 20 сек для Meta)
    3. Тяжёлая обработка — в BackgroundTasks
    """
    # Логируем входящий размер (не содержимое — может быть sensitive)
    logger.info(
        f"[{PLATFORM}] Incoming webhook: "
        f"size={len(raw_body)} bytes"
    )

    # Запустить обработку в фоне — endpoint уже вернёт 200
    background_tasks.add_task(_process_safe, raw_body)

    return JSONResponse(EXPECTED_RESPONSE)


async def _process_safe(raw_body: bytes) -> None:
    """
    Обёртка с перехватом всех исключений для фоновой обработки.
    Ошибки НЕ должны выходить наружу — 200 уже отправлен провайдеру.
    """
    try:
        await _process_event(raw_body)
    except Exception as exc:
        logger.error(
            f"[{PLATFORM}] Unhandled error in background processing: {exc}",
            exc_info=True,
        )
        # Можно добавить алерт в Telegram:
        # await notify_owner_telegram(f"[{PLATFORM}] webhook error: {exc}")


async def _process_event(raw_body: bytes) -> None:
    """
    Основная бизнес-логика обработки события.

    Шаблон для WhatsApp (адаптировать под конкретную платформу).
    """
    # Безопасный парсинг JSON
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        logger.error(f"[{PLATFORM}] Invalid JSON: {exc}")
        return  # 200 уже отправлен — просто логируем

    # Базовая валидация структуры
    if payload.get("object") != "whatsapp_business_account":
        logger.debug(f"[{PLATFORM}] Unexpected object: {payload.get('object')} — skipping")
        return

    # Обработка каждого entry
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for message in value.get("messages", []):
                message_id = message.get("id", "")
                sender = message.get("from", "unknown")

                if not message_id:
                    logger.warning(f"[{PLATFORM}] Message without ID — skipping")
                    continue

                logger.info(
                    f"[{PLATFORM}] Processing: "
                    f"mid={message_id} from={sender}"
                )

                # Idempotency check
                from data.database import CatalogDB  # noqa: PLC0415
                db = CatalogDB.instance()
                if db and await is_already_processed(db._pool, message_id, PLATFORM):
                    logger.info(f"[{PLATFORM}] Duplicate skipped: {message_id}")
                    continue

                # Основная обработка с retry
                await retry_with_backoff(
                    _handle_single_message,
                    message,
                    value,
                    max_attempts=3,
                    base_delay=2.0,
                    exceptions=(ConnectionError, TimeoutError, OSError),
                )

                # Пометить как обработанное
                if db:
                    await mark_as_processed(
                        db._pool,
                        message_id,
                        PLATFORM,
                        payload_summary=f"from={sender} type={message.get('type')}",
                    )

                logger.info(f"[{PLATFORM}] Processed: mid={message_id}")


async def _handle_single_message(message: dict, value: dict) -> None:
    """
    Обработка одного сообщения.
    Здесь вызвать omni_service, handler или другую бизнес-логику.

    Для Omni Inbox:
        await omni_service.on_incoming_message(
            platform=PLATFORM,
            platform_user_id=message["from"],
            text=message.get("text", {}).get("body", ""),
            raw_payload=message,
        )
    """
    msg_type = message.get("type", "unknown")
    sender = message.get("from", "unknown")

    logger.info(f"[{PLATFORM}] handle: type={msg_type} from={sender}")

    # TODO: вставить вызов платформенного handler'а или omni_service
    # Пример:
    # from bot.services.omni_inbox import get_omni_service
    # omni = get_omni_service()
    # await omni.on_incoming_message(
    #     platform=PLATFORM,
    #     platform_user_id=sender,
    #     text=...,
    # )

    logger.info(f"[{PLATFORM}] handled: type={msg_type} from={sender}")


# ---------------------------------------------------------------------------
# STARTUP — регистрация webhook (для Viber)
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup() -> None:
    """
    Для Viber: set_webhook вызывается при каждом старте.
    Для Meta: webhook регистрируется вручную в Developer Portal.
    Для Telegram: setWebhook вызывается вручную или в скрипте деплоя.
    """
    if PLATFORM == "viber":
        viber_token = os.getenv("VIBER_AUTH_TOKEN")
        viber_url = os.getenv("VIBER_WEBHOOK_URL")
        if viber_token and viber_url:
            import httpx  # noqa: PLC0415

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://chatapi.viber.com/pa/set_webhook",
                    headers={"X-Viber-Auth-Token": viber_token},
                    json={
                        "url": viber_url,
                        "event_types": [
                            "delivered", "seen", "failed",
                            "subscribed", "unsubscribed",
                            "conversation_started",
                        ],
                        "send_name": True,
                        "send_photo": True,
                    },
                )
                result = resp.json()
                if result.get("status") == 0:
                    logger.info("[viber] Webhook registered successfully")
                else:
                    logger.error(f"[viber] set_webhook failed: {result}")
