---
name: webhook-processor
description: "Use when building or improving webhook receivers, adding HMAC signature verification, implementing retry logic with exponential backoff, ensuring idempotent webhook processing, or debugging webhook delivery failures across Meta API (Instagram/WhatsApp/Facebook), Telegram, and Viber platforms"
---
# Webhook Processor

## Overview

Production-ready система приёма webhook'ов строится на четырёх принципах:

1. **Немедленный 200 OK** — ответить провайдеру в течение 5 секунд, обрабатывать в фоне. Иначе провайдер считает доставку неудачной и ретраит.
2. **HMAC верификация** — каждый входящий запрос проверяется по подписи до начала обработки. Невалидные — отклоняются с 403.
3. **Idempotency** — одно и то же сообщение может прийти несколько раз (retry провайдера). Повторная обработка должна быть безопасной.
4. **Retry с exponential backoff + Dead Letter Queue** — временные сбои (БД недоступна, внешний API не отвечает) не должны терять сообщения.

## When to Use

- Добавляешь новый webhook endpoint (Meta/Telegram/Viber/Stripe/GitHub)
- Webhook'и дублируются или теряются
- Провайдер помечает доставку как failed (нет 200 в 5 сек)
- Нужна верификация подписи
- Обработка занимает >1 секунды (DB writes, внешние API calls)
- Нужен audit trail входящих событий

---

## Core Patterns

### Pattern 1: Immediate 200 OK + Async Processing

Самая частая ошибка — обрабатывать запрос синхронно в теле webhook endpoint'а. Meta API ждёт 200 максимум 20 секунд, после чего считает доставку неудачной и будет ретраить. Telegram ждёт 60 секунд.

**Правильный подход с FastAPI BackgroundTasks:**

```python
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/webhook/meta")
async def meta_webhook(request: Request, background_tasks: BackgroundTasks):
    """Принять -> проверить подпись -> ответить 200 -> обработать в фоне."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # 1. Верификация — быстро, до ответа
    if not verify_meta_signature(raw_body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 2. Немедленно ответить 200
    # BackgroundTasks выполняются ПОСЛЕ отправки ответа
    background_tasks.add_task(process_meta_event, raw_body)

    return JSONResponse({"status": "ok"})  # Telegram ожидает именно {"ok": true}


async def process_meta_event(raw_body: bytes):
    """Асинхронная обработка после того, как 200 уже ушёл провайдеру."""
    try:
        import json
        payload = json.loads(raw_body)
        # ... обработка событий
    except Exception as e:
        logger.error(f"[webhook] process_meta_event failed: {e}", exc_info=True)
        # Не поднимаем исключение — 200 уже отправлен, провайдер не узнает
        # Вместо этого — DLQ или retry queue
```

**Важно для Meta API:**
- GET-запрос — верификация webhook при настройке (hub.challenge)
- POST-запрос — реальные события
- Никогда не возвращать 4xx/5xx на валидный payload — Meta отключит webhook

```python
@app.get("/webhook/meta")
async def meta_webhook_verify(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None,
):
    """Meta webhook verification handshake."""
    import os
    if hub_mode == "subscribe" and hub_verify_token == os.getenv("META_VERIFY_TOKEN"):
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")
```

---

### Pattern 2: HMAC-SHA256 Verification

Timing-safe comparison обязателен — обычное `==` уязвимо к timing attacks (атакующий может угадать ключ по времени ответа).

**Универсальный верификатор:**

```python
import hmac
import hashlib

def verify_hmac(
    raw_body: bytes,
    signature_header: str,
    secret: str,
    prefix: str = "sha256=",
    algorithm: str = "sha256",
) -> bool:
    """
    Универсальная HMAC верификация.

    Args:
        raw_body: сырое тело запроса (до json.loads!)
        signature_header: значение заголовка подписи
        secret: секретный ключ
        prefix: префикс перед hex-дайджестом ("sha256=", "v0=", "")
        algorithm: "sha256" или "sha1"
    """
    if not signature_header:
        return False

    # Убираем префикс
    if prefix and signature_header.startswith(prefix):
        received_digest = signature_header[len(prefix):]
    else:
        received_digest = signature_header

    # Вычисляем ожидаемую подпись
    hash_func = hashlib.sha256 if algorithm == "sha256" else hashlib.sha1
    expected_digest = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hash_func,
    ).hexdigest()

    # Timing-safe сравнение — ОБЯЗАТЕЛЬНО
    return hmac.compare_digest(expected_digest, received_digest)
```

**Meta API (Instagram / WhatsApp / Facebook):**

```python
import os

def verify_meta_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Заголовок: X-Hub-Signature-256: sha256=<hex>
    Ключ: META_APP_SECRET (один на все три платформы)
    """
    secret = os.getenv("META_APP_SECRET", "")
    return verify_hmac(raw_body, signature_header, secret, prefix="sha256=")
```

**Telegram:**

```python
def verify_telegram_signature(raw_body: bytes, secret_token_header: str) -> bool:
    """
    Заголовок: X-Telegram-Bot-Api-Secret-Token: <token>
    Telegram не использует HMAC — просто сравнивает токен напрямую.
    Токен задаётся при setWebhook через secret_token параметр.
    """
    expected = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not expected:
        return True  # Если токен не настроен — пропускаем (не рекомендуется)
    return hmac.compare_digest(expected, secret_token_header or "")
```

**Viber:**

```python
def verify_viber_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Заголовок: X-Viber-Content-Signature: <hex>  (БЕЗ префикса)
    Ключ: VIBER_AUTH_TOKEN (не app_secret!)
    Алгоритм: SHA256, без префикса
    """
    auth_token = os.getenv("VIBER_AUTH_TOKEN", "")
    return verify_hmac(raw_body, signature_header, auth_token, prefix="")
```

**Пример FastAPI dependency для верификации:**

```python
from fastapi import Depends

async def require_meta_signature(request: Request) -> bytes:
    """FastAPI dependency — верифицирует подпись и возвращает raw body."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_meta_signature(raw_body, signature):
        logger.warning(f"[webhook] Invalid Meta signature from {request.client.host}")
        raise HTTPException(status_code=403, detail="Invalid signature")
    return raw_body

@app.post("/webhook/instagram")
async def instagram_webhook(
    background_tasks: BackgroundTasks,
    raw_body: bytes = Depends(require_meta_signature),
):
    background_tasks.add_task(process_instagram_event, raw_body)
    return {"status": "ok"}
```

---

### Pattern 3: Idempotency

Провайдеры гарантируют доставку at-least-once. Одно событие может прийти 2-3 раза при сбоях сети. Без idempotency — дублирующиеся бронирования, двойные уведомления.

**Вариант A: PostgreSQL (рекомендуется для проектов уже на PostgreSQL):**

```python
from data.database import CatalogDB
import json

async def is_already_processed(db: CatalogDB, message_id: str, platform: str) -> bool:
    """Проверить, было ли сообщение уже обработано."""
    result = await db._pool.fetchval(
        """
        SELECT 1 FROM processed_webhook_events
        WHERE message_id = $1 AND platform = $2
          AND processed_at > NOW() - INTERVAL '24 hours'
        """,
        message_id, platform,
    )
    return result is not None


async def mark_as_processed(db: CatalogDB, message_id: str, platform: str, payload_summary: str = ""):
    """Пометить сообщение как обработанное."""
    await db._pool.execute(
        """
        INSERT INTO processed_webhook_events (message_id, platform, payload_summary, processed_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (message_id, platform) DO NOTHING
        """,
        message_id, platform, payload_summary,
    )


# Таблица (добавить в миграции):
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS processed_webhook_events (
    id SERIAL PRIMARY KEY,
    message_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    payload_summary TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (message_id, platform)
);
CREATE INDEX IF NOT EXISTS idx_pwe_processed_at ON processed_webhook_events (processed_at);
"""


# Использование в обработчике:
async def process_instagram_event(raw_body: bytes):
    payload = json.loads(raw_body)

    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            message_id = messaging.get("message", {}).get("mid", "")

            if not message_id:
                continue

            # Idempotency check
            if await is_already_processed(db, message_id, "instagram"):
                logger.info(f"[instagram] Duplicate message skipped: {message_id}")
                continue

            # Обработка
            await handle_instagram_message(messaging)

            # Пометить как обработанное
            await mark_as_processed(db, message_id, "instagram")
```

**Вариант B: In-memory (для разработки / малого трафика):**

```python
from collections import OrderedDict
import time

class IdempotencyCache:
    """LRU-подобный кэш с TTL для idempotency checks."""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 86400):
        self._cache: OrderedDict[str, float] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds

    def is_processed(self, key: str) -> bool:
        if key not in self._cache:
            return False
        if time.time() - self._cache[key] > self._ttl:
            del self._cache[key]
            return False
        return True

    def mark(self, key: str):
        self._cache[key] = time.time()
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)  # Удалить самый старый

# Синглтон
_idempotency_cache = IdempotencyCache()
```

---

### Pattern 4: Retry с Exponential Backoff

Когда обработка упала из-за временного сбоя (БД перегружена, внешний API вернул 503), нужно повторить позже — не терять событие.

**Паттерн с asyncio (без внешних зависимостей):**

```python
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

async def retry_with_backoff(
    func: Callable,
    *args,
    max_attempts: int = 5,
    base_delay: float = 3.0,
    backoff_multiplier: float = 3.0,
    exceptions: tuple = (Exception,),
    **kwargs,
) -> Any:
    """
    Retry с exponential backoff.

    Задержки по умолчанию: 3s → 9s → 27s → 81s → 243s
    Итого максимальное ожидание: ~363 секунды (~6 минут)
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt == max_attempts:
                break

            delay = base_delay * (backoff_multiplier ** (attempt - 1))
            logger.warning(
                f"[retry] Attempt {attempt}/{max_attempts} failed: {e}. "
                f"Retrying in {delay:.0f}s..."
            )
            await asyncio.sleep(delay)

    # Все попытки исчерпаны — отправить в DLQ
    logger.error(f"[retry] All {max_attempts} attempts failed. Sending to DLQ.")
    await send_to_dlq(func.__name__, args, kwargs, str(last_exception))
    raise last_exception


# Использование:
async def process_with_retry(raw_body: bytes):
    await retry_with_backoff(
        process_instagram_event,
        raw_body,
        max_attempts=5,
        exceptions=(ConnectionError, TimeoutError, OSError),
    )
```

**Dead Letter Queue (PostgreSQL):**

```python
import json

async def send_to_dlq(
    handler_name: str,
    args: tuple,
    kwargs: dict,
    error_message: str,
):
    """Сохранить неудачное событие для ручного разбора или повторной обработки."""
    try:
        await db._pool.execute(
            """
            INSERT INTO webhook_dlq (handler_name, payload, error_message, created_at)
            VALUES ($1, $2, $3, NOW())
            """,
            handler_name,
            json.dumps({"args_repr": str(args), "kwargs": kwargs}),
            error_message,
        )
        logger.error(f"[dlq] Event saved to DLQ: {handler_name} — {error_message}")
    except Exception as dlq_error:
        # DLQ тоже упал — записать в лог как последний рубеж
        logger.critical(f"[dlq] Failed to save to DLQ: {dlq_error}")


# Таблица DLQ:
CREATE_DLQ_TABLE = """
CREATE TABLE IF NOT EXISTS webhook_dlq (
    id SERIAL PRIMARY KEY,
    handler_name TEXT NOT NULL,
    payload JSONB,
    error_message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
"""
```

---

### Pattern 5: Structured Error Handling

**Никогда не возвращать 5xx на невалидный payload.** Meta отключит webhook при нескольких 5xx подряд.

```python
import json
from fastapi.responses import JSONResponse

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()

    # 1. Проверка подписи — единственное место, где 403 допустим
    if not verify_meta_signature(raw_body, request.headers.get("X-Hub-Signature-256", "")):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 2. Попытка распарсить JSON — ошибки не поднимаем
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as e:
        logger.error(f"[whatsapp] Invalid JSON payload: {e}")
        # Отвечаем 200 — Meta не виновата в нашем коде
        return JSONResponse({"status": "ok"})

    # 3. Базовая валидация структуры
    if payload.get("object") != "whatsapp_business_account":
        logger.warning(f"[whatsapp] Unexpected object type: {payload.get('object')}")
        return JSONResponse({"status": "ok"})

    # 4. Обработка в фоне — ошибки там не влияют на ответ провайдеру
    background_tasks.add_task(process_whatsapp_safe, raw_body, payload)

    return JSONResponse({"status": "ok"})


async def process_whatsapp_safe(raw_body: bytes, payload: dict):
    """Обёртка с перехватом всех исключений."""
    try:
        await process_whatsapp_event(payload)
    except Exception as e:
        logger.error(f"[whatsapp] Unhandled error in background processing: {e}", exc_info=True)
        # Здесь можно добавить алерт в Telegram или запись в DLQ
```

---

## Platform-Specific Notes

### Meta (Instagram / WhatsApp / Facebook)

| Параметр | Значение |
|----------|----------|
| Заголовок подписи | `X-Hub-Signature-256: sha256=<hex>` |
| Ключ | `META_APP_SECRET` (один на все три платформы) |
| Верификация | GET с `hub.mode`, `hub.verify_token`, `hub.challenge` |
| Таймаут | 20 секунд до retry |
| Retry при 4xx/5xx | Да, несколько попыток с backoff |
| Отключение | После нескольких 5xx подряд Meta отключает webhook |

```python
# Полная структура Meta webhook handler:
@app.post("/webhook/{platform}")
async def meta_webhook(
    platform: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    if platform not in ("instagram", "whatsapp", "facebook"):
        raise HTTPException(status_code=404)

    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_meta_signature(raw_body, signature):
        logger.warning(f"[{platform}] Invalid signature from {request.client.host}")
        raise HTTPException(status_code=403)

    # Логируем входящий payload для дебага (только в dev)
    import os
    if os.getenv("WEBHOOK_DEBUG", "0") == "1":
        logger.debug(f"[{platform}] Incoming: {raw_body[:500]}")

    handlers = {
        "instagram": process_instagram_event,
        "whatsapp": process_whatsapp_event,
        "facebook": process_facebook_event,
    }
    background_tasks.add_task(handlers[platform], raw_body)

    return JSONResponse({"status": "ok"})
```

### Telegram

```python
# Telegram webhook setup:
import aiohttp

async def set_telegram_webhook(bot_token: str, webhook_url: str, secret_token: str):
    """Зарегистрировать webhook при старте приложения."""
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            json={
                "url": webhook_url,
                "secret_token": secret_token,  # Будет в X-Telegram-Bot-Api-Secret-Token
                "allowed_updates": ["message", "callback_query", "inline_query"],
                "drop_pending_updates": True,
            }
        )
        result = await resp.json()
        if not result.get("ok"):
            raise RuntimeError(f"setWebhook failed: {result}")


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    # Telegram шлёт секрет в этом заголовке (не HMAC — просто токен)
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not verify_telegram_signature(b"", secret):
        raise HTTPException(status_code=403)

    raw_body = await request.body()
    background_tasks.add_task(process_telegram_update, raw_body)

    # Telegram ожидает пустой 200 или {"ok": true}
    return JSONResponse({"ok": True})
```

### Viber

```python
# Viber auto set_webhook при старте:
import httpx

async def set_viber_webhook(auth_token: str, webhook_url: str):
    """
    Viber требует вызвать set_webhook при каждом старте приложения.
    Иначе вебхук может стать неактивным.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://chatapi.viber.com/pa/set_webhook",
            headers={"X-Viber-Auth-Token": auth_token},
            json={
                "url": webhook_url,
                "event_types": [
                    "delivered", "seen", "failed",
                    "subscribed", "unsubscribed",
                    "conversation_started",
                ],
                "send_name": True,
                "send_photo": True,
            }
        )
        result = resp.json()
        if result.get("status") != 0:
            raise RuntimeError(f"Viber set_webhook failed: {result}")


@app.post("/webhook/viber")
async def viber_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()
    signature = request.headers.get("X-Viber-Content-Signature", "")

    if not verify_viber_signature(raw_body, signature):
        raise HTTPException(status_code=403)

    background_tasks.add_task(process_viber_event, raw_body)
    return JSONResponse({"status": 0})  # Viber ожидает status: 0
```

---

## Debugging Webhooks

### ngrok для локальной разработки

```bash
# Установка
brew install ngrok  # macOS
# или скачать с ngrok.com

# Запуск для конкретного порта
ngrok http 8081  # Instagram
ngrok http 8082  # WhatsApp
ngrok http 8083  # Facebook
ngrok http 8084  # Viber

# Получить публичный URL (меняется каждый перезапуск без платного аккаунта)
# Например: https://abc123.ngrok-free.app

# Полезные команды
ngrok http 8081 --subdomain mybot  # Фиксированный subdomain (платный план)
```

После получения URL:
- Meta: вставить в Developer Portal -> Webhooks -> Edit -> Callback URL
- Viber: установить в `VIBER_WEBHOOK_URL` и перезапустить (set_webhook вызывается автоматически)
- Telegram: вызвать `setWebhook` с новым URL

### Логирование входящих payload'ов

```python
# Middleware для логирования всех входящих webhook запросов
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

class WebhookLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/webhook"):
            start = time.time()
            # Кешируем body (FastAPI читает его один раз)
            body = await request.body()

            logger.info(
                f"[webhook-in] {request.method} {request.url.path} "
                f"from {request.client.host} "
                f"body_size={len(body)}"
            )

            # В dev режиме — полный payload
            if os.getenv("WEBHOOK_DEBUG") == "1":
                try:
                    logger.debug(f"[webhook-in] body: {body[:1000].decode()}")
                except Exception:
                    pass

        response = await call_next(request)

        if request.url.path.startswith("/webhook"):
            elapsed = time.time() - start
            logger.info(
                f"[webhook-out] {request.url.path} "
                f"status={response.status_code} "
                f"elapsed={elapsed:.3f}s"
            )

        return response

app.add_middleware(WebhookLoggingMiddleware)
```

### Типичные проблемы и решения

**Проблема: Meta отключила webhook ("webhook is not working")**
- Причина: несколько подряд 5xx или таймаут >20 сек
- Решение: проверить endpoint на синхронную блокировку, добавить немедленный 200

**Проблема: Дублирующиеся сообщения**
- Причина: нет idempotency, провайдер ретраит из-за медленного ответа
- Решение: Pattern 3 (idempotency) + Pattern 1 (быстрый 200)

**Проблема: Signature verification fails**
- Причина чаще всего: тело запроса прочитано дважды (FastAPI кешировки нет)
- Решение: `raw_body = await request.body()` один раз, передавать дальше как bytes

```python
# НЕПРАВИЛЬНО — тело будет пустым при повторном чтении
async def bad_handler(request: Request):
    body1 = await request.body()  # OK
    body2 = await request.body()  # Пустой bytes в некоторых версиях!

# ПРАВИЛЬНО — читаем один раз
async def good_handler(request: Request):
    raw_body = await request.body()
    verify_signature(raw_body, ...)
    process(raw_body)
```

**Проблема: Viber не доставляет события**
- Причина: set_webhook не был вызван после перезапуска
- Решение: вызывать `set_viber_webhook()` в `@app.on_event("startup")`

```python
@app.on_event("startup")
async def startup():
    viber_token = os.getenv("VIBER_AUTH_TOKEN")
    viber_url = os.getenv("VIBER_WEBHOOK_URL")
    if viber_token and viber_url:
        await set_viber_webhook(viber_token, viber_url)
```

**Проблема: Telegram webhook не получает updates**
- Проверить: `getWebhookInfo` — показывает last_error_message
- Частая причина: SSL сертификат не валиден (ngrok — OK, самоподписанный — нет без явной передачи)

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

---

## Quick Reference

| Платформа | Заголовок подписи | Алгоритм | Ключ | Префикс |
|-----------|------------------|----------|------|---------|
| Meta (IG/WA/FB) | `X-Hub-Signature-256` | HMAC-SHA256 | `META_APP_SECRET` | `sha256=` |
| Telegram | `X-Telegram-Bot-Api-Secret-Token` | Прямое сравнение | `TELEGRAM_WEBHOOK_SECRET` | нет |
| Viber | `X-Viber-Content-Signature` | HMAC-SHA256 | `VIBER_AUTH_TOKEN` | нет |
| GitHub | `X-Hub-Signature-256` | HMAC-SHA256 | webhook secret | `sha256=` |
| Stripe | `Stripe-Signature` | HMAC-SHA256 + timestamp | webhook signing secret | `v1=` |

| Платформа | Таймаут | Ожидаемый ответ | Retry при ошибке |
|-----------|---------|-----------------|-----------------|
| Meta | 20 сек | 200 OK | Да, с backoff |
| Telegram | 60 сек | 200 OK / `{"ok":true}` | Нет (polling fallback) |
| Viber | 5 сек | `{"status":0}` | Нет |
| GitHub | 10 сек | 200 OK | Да, 3 попытки |

---

## Common Mistakes

1. **Синхронная тяжёлая обработка в endpoint** — самая частая причина timeouts и retry-дублей. Всегда использовать BackgroundTasks или очередь.

2. **Нет HMAC верификации** — любой может слать произвольные POST запросы на ваш endpoint.

3. **Нет idempotency** — при retry провайдера будут дублирующиеся бронирования/уведомления.

4. **Возврат 5xx на невалидный payload** — Meta отключит webhook. Всегда 200 на структурные ошибки.

5. **Читать `request.body()` дважды** — второй вызов вернёт пустые bytes. Кешировать в переменной.

6. **Обычное `==` вместо `hmac.compare_digest()`** — уязвимость к timing attack.

7. **Хранить секреты в коде** — только через `os.getenv()` из `.env` файла.

8. **Не логировать входящие payload'ы в dev** — без логов невозможно дебажить проблемы доставки.

---

## Sources

- [Meta Webhooks Developer Docs](https://developers.facebook.com/docs/graph-api/webhooks/)
- [Telegram Bot API: setWebhook](https://core.telegram.org/bots/api#setwebhook)
- [Viber REST API: Callbacks](https://developers.viber.com/docs/api/rest-bot-api/#callbacks)
- [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- TerminalSkills/skills webhook-processor (Apache-2.0): https://github.com/TerminalSkills/skills
- Оригинальная концепция: Node.js/BullMQ паттерны адаптированы для Python/FastAPI

**Размер скилла:** ~350 строк, ~14 KB
**Платформы:** Meta (IG/WA/FB), Telegram, Viber, GitHub, Stripe
**Язык:** Python 3.10+ / FastAPI
