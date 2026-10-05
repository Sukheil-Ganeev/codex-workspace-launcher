# HMAC Patterns — Platform-specific Reference

Справочник по HMAC верификации для каждой платформы, используемой в VIP-DXB-CatalogBot.

---

## Универсальный Python паттерн

Базовая функция, от которой наследуются все платформенные верификаторы:

```python
import hmac
import hashlib
import os

def verify_hmac(
    raw_body: bytes,
    signature_header: str,
    secret: str,
    prefix: str = "sha256=",
    algorithm: str = "sha256",
) -> bool:
    """
    Timing-safe HMAC верификация для любой платформы.

    ВАЖНО:
    - raw_body должен быть СЫРЫМ телом запроса (до json.loads!)
    - Использовать hmac.compare_digest() — не обычное ==
    - secret берётся из os.getenv(), никогда не хардкодить

    Args:
        raw_body:           сырое тело запроса (bytes)
        signature_header:   значение заголовка подписи (str)
        secret:             секретный ключ (str)
        prefix:             префикс перед hex-дайджестом ("sha256=", "v1=", "")
        algorithm:          "sha256" (для большинства) или "sha1" (legacy)
    """
    if not signature_header or not secret:
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

    # Timing-safe сравнение — ОБЯЗАТЕЛЬНО (защита от timing attack)
    return hmac.compare_digest(expected_digest, received_digest)
```

**Почему `hmac.compare_digest()`?**
Обычное `==` сравнивает строки побайтово и возвращает результат при первом несовпадении. Атакующий может измерить время ответа и угадать ключ побайтово. `hmac.compare_digest()` всегда сравнивает всю строку за константное время.

---

## Meta API — Instagram / WhatsApp / Facebook

Один секрет (`META_APP_SECRET`) используется для всех трёх платформ Meta.

```python
# Заголовок: X-Hub-Signature-256: sha256=<hex>
# Ключ: META_APP_SECRET (один на IG + WA + FB)
# Алгоритм: HMAC-SHA256
# Префикс: "sha256="

def verify_meta_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Верификация для Instagram DM, WhatsApp Cloud API, Facebook Messenger.
    Все три платформы используют одинаковый механизм и один ключ.
    """
    secret = os.getenv("META_APP_SECRET", "")
    if not secret:
        raise RuntimeError("META_APP_SECRET not set in environment")
    return verify_hmac(raw_body, signature_header, secret, prefix="sha256=")


# FastAPI usage:
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_verified_body_meta(request: Request) -> bytes:
    """FastAPI dependency — верифицирует Meta подпись и возвращает raw body."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_meta_signature(raw_body, signature):
        logger.warning(
            f"[meta-webhook] Invalid signature from {request.client.host} "
            f"path={request.url.path}"
        )
        raise HTTPException(status_code=403, detail="Invalid Meta signature")
    return raw_body
```

**Meta Webhook Verification Handshake (GET request):**
```python
from fastapi import Query

@app.get("/webhook/{platform}")
async def meta_verify(
    platform: str,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Meta вызывает этот GET endpoint при настройке webhook в Developer Portal.
    Нужно вернуть hub_challenge как число.
    """
    verify_token = os.getenv(f"{platform.upper()}_VERIFY_TOKEN", "")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info(f"[{platform}] Webhook verification successful")
        return int(hub_challenge)
    logger.error(f"[{platform}] Webhook verification failed: token mismatch")
    raise HTTPException(status_code=403, detail="Verification failed")
```

**Env vars:**
```
META_APP_SECRET=your_app_secret_from_meta_developer_portal
INSTAGRAM_VERIFY_TOKEN=ig_verify_token_2026
WHATSAPP_VERIFY_TOKEN=wa_verify_token_2026
FB_VERIFY_TOKEN=fb_verify_token_2026
```

---

## Viber

Viber использует `VIBER_AUTH_TOKEN` как ключ (не app_secret!), и заголовок без префикса.

```python
# Заголовок: X-Viber-Content-Signature: <hex>  (БЕЗ "sha256=" префикса!)
# Ключ: VIBER_AUTH_TOKEN (НЕ META_APP_SECRET!)
# Алгоритм: HMAC-SHA256
# Префикс: "" (пустой)

def verify_viber_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Viber использует другой заголовок и другой ключ — не путать с Meta!
    """
    auth_token = os.getenv("VIBER_AUTH_TOKEN", "")
    if not auth_token:
        raise RuntimeError("VIBER_AUTH_TOKEN not set in environment")
    return verify_hmac(raw_body, signature_header, auth_token, prefix="")


# FastAPI usage:
@app.post("/webhook/viber")
async def viber_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()
    signature = request.headers.get("X-Viber-Content-Signature", "")

    if not verify_viber_signature(raw_body, signature):
        logger.warning(f"[viber] Invalid signature from {request.client.host}")
        raise HTTPException(status_code=403)

    background_tasks.add_task(process_viber_event, raw_body)
    return {"status": 0}  # Viber ожидает именно status: 0 (число, не строка)
```

**Типичная ошибка Viber:** использовать `META_APP_SECRET` вместо `VIBER_AUTH_TOKEN`. Оба — HMAC-SHA256, но с разными ключами.

---

## Telegram

Telegram не использует HMAC для webhook — вместо этого проверяется секретный токен напрямую.

```python
# Заголовок: X-Telegram-Bot-Api-Secret-Token: <token>
# Механизм: прямое сравнение (не HMAC)
# Токен задаётся при setWebhook через параметр secret_token

def verify_telegram_webhook_secret(secret_token_header: str) -> bool:
    """
    Telegram не использует HMAC — просто сравнивает токен напрямую.
    Токен задаётся в setWebhook и должен быть случайной строкой.
    """
    expected = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not expected:
        # Если секрет не настроен — в dev это OK, в prod — нет
        return True
    # Timing-safe comparison даже для прямого токена
    return hmac.compare_digest(expected, secret_token_header or "")


# Установка webhook с секретом:
import aiohttp

async def set_telegram_webhook(bot_token: str, webhook_url: str):
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            json={
                "url": webhook_url,
                "secret_token": secret,
                "allowed_updates": ["message", "callback_query", "inline_query"],
                "drop_pending_updates": True,
            }
        )
```

**Важно:** VIP-DXB-CatalogBot использует Long Polling для Telegram, не webhook. Секретный токен нужен только при переключении на webhook режим.

---

## GitHub Webhooks

```python
# Заголовок: X-Hub-Signature-256: sha256=<hex>
# Ключ: произвольный secret, заданный в GitHub repo settings -> Webhooks
# Алгоритм: HMAC-SHA256 (точно такой же как Meta!)
# Префикс: "sha256="

def verify_github_signature(raw_body: bytes, signature_header: str) -> bool:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    return verify_hmac(raw_body, signature_header, secret, prefix="sha256=")
```

---

## Stripe

Stripe добавляет timestamp для защиты от replay attacks.

```python
# Заголовок: Stripe-Signature: t=1614556800,v1=<hex>,v0=<hex>
# Алгоритм: HMAC-SHA256 от строки "timestamp.payload"
# Ключ: webhook signing secret из Stripe Dashboard

import time

def verify_stripe_signature(
    raw_body: bytes,
    signature_header: str,
    tolerance_seconds: int = 300,
) -> bool:
    """
    Stripe подписывает: HMAC("timestamp.payload")
    И проверяет freshness по timestamp (защита от replay).
    """
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not secret or not signature_header:
        return False

    # Парсим заголовок: t=...,v1=...,v0=...
    parts = dict(p.split("=", 1) for p in signature_header.split(",") if "=" in p)
    timestamp = parts.get("t", "")
    received_sig = parts.get("v1", "")

    if not timestamp or not received_sig:
        return False

    # Проверка freshness (защита от replay attack)
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > tolerance_seconds:
            return False  # Слишком старый запрос
    except ValueError:
        return False

    # Вычислить подпись: HMAC(timestamp + "." + payload)
    signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}".encode()
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, received_sig)
```

---

## Сводная таблица

| Платформа | Заголовок | Алгоритм | Ключ (.env) | Префикс | Особенность |
|-----------|-----------|----------|-------------|---------|-------------|
| Meta (IG/WA/FB) | `X-Hub-Signature-256` | HMAC-SHA256 | `META_APP_SECRET` | `sha256=` | Один ключ на 3 платформы |
| Viber | `X-Viber-Content-Signature` | HMAC-SHA256 | `VIBER_AUTH_TOKEN` | нет | Не `META_APP_SECRET`! |
| Telegram (webhook) | `X-Telegram-Bot-Api-Secret-Token` | Прямое сравнение | `TELEGRAM_WEBHOOK_SECRET` | нет | Не HMAC |
| GitHub | `X-Hub-Signature-256` | HMAC-SHA256 | `GITHUB_WEBHOOK_SECRET` | `sha256=` | Как Meta, но другой ключ |
| Stripe | `Stripe-Signature` | HMAC-SHA256 + timestamp | `STRIPE_WEBHOOK_SECRET` | `v1=` | Replay protection |

---

## Антипаттерны

```python
# ПЛОХО: обычное == — уязвимость к timing attack
if expected == received:
    ...

# ПЛОХО: проверка только префикса
if signature.startswith("sha256="):
    return True  # Принять без реальной проверки!

# ПЛОХО: secret захардкожен
SECRET = "my_secret_key_123"

# ПЛОХО: читать тело дважды
body_for_verify = await request.body()
payload = await request.json()  # Второй вызов → пустые bytes!

# ХОРОШО:
raw_body = await request.body()  # Один раз
verify_hmac(raw_body, header, os.getenv("SECRET"))
payload = json.loads(raw_body)  # Из переменной, не из request
```

---

## Дополнительно

- [OWASP: Testing for Weak Cryptography](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/)
- [Python hmac module docs](https://docs.python.org/3/library/hmac.html)
- [Meta Webhooks — Validating Payloads](https://developers.facebook.com/docs/messenger-platform/webhooks#validate-payloads)
- [Viber REST API — Callbacks](https://developers.viber.com/docs/api/rest-bot-api/#callbacks)
