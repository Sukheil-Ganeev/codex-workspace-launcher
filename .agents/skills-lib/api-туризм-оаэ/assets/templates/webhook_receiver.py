"""
Webhook Receiver Template (FastAPI)
Шаблон для приёма webhooks от различных сервисов

Использование:
    uvicorn webhook_receiver:app --reload --port 8000

Для локального тестирования:
    ngrok http 8000
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from typing import Optional
import hmac
import hashlib
import os
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Webhook Receiver")

# ============= Secrets =============

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "test_secret")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_verify_token")

# ============= Signature Verification =============

def verify_stripe_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Проверка подписи Stripe webhook"""
    try:
        import stripe
        stripe.Webhook.construct_event(payload, signature, secret)
        return True
    except Exception as e:
        logger.error(f"Stripe signature verification failed: {e}")
        return False

def verify_whatsapp_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Проверка подписи WhatsApp webhook"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature or "")

def verify_generic_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Общая проверка HMAC-SHA256 подписи"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")

# ============= Event Handlers =============

async def handle_stripe_payment_succeeded(payment: dict):
    """Обработка успешного платежа Stripe"""
    booking_id = payment.get("metadata", {}).get("booking_id")
    amount = payment.get("amount", 0) / 100  # центы в валюту
    currency = payment.get("currency", "").upper()

    logger.info(f"Payment succeeded: {booking_id}, {amount} {currency}")

    # TODO: Ваша логика
    # 1. Обновить статус бронирования в БД
    # 2. Сгенерировать ваучер
    # 3. Отправить клиенту через WhatsApp

async def handle_stripe_payment_failed(payment: dict):
    """Обработка неудачного платежа Stripe"""
    booking_id = payment.get("metadata", {}).get("booking_id")
    error = payment.get("last_payment_error", {}).get("message", "Unknown error")

    logger.warning(f"Payment failed: {booking_id}, error: {error}")

    # TODO: Уведомить клиента о проблеме с оплатой

async def handle_whatsapp_message(message: dict, from_number: str):
    """Обработка входящего сообщения WhatsApp"""
    message_type = message.get("type")

    if message_type == "text":
        text = message.get("text", {}).get("body", "")
        logger.info(f"WhatsApp message from {from_number}: {text}")

        # TODO: Ваша логика обработки сообщений
        # Например, передать в GPT для понимания намерения

    elif message_type == "image":
        logger.info(f"WhatsApp image from {from_number}")

    elif message_type == "document":
        logger.info(f"WhatsApp document from {from_number}")

# ============= Stripe Webhook =============

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook endpoint для Stripe"""
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature", "")

    # Верификация подписи
    if not verify_stripe_signature(payload, signature, STRIPE_WEBHOOK_SECRET):
        logger.warning("Invalid Stripe signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    event = json.loads(payload)
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    logger.info(f"Stripe event: {event_type}")

    # Обработка событий в фоне (чтобы быстро вернуть 200)
    if event_type == "payment_intent.succeeded":
        background_tasks.add_task(handle_stripe_payment_succeeded, data)
    elif event_type == "payment_intent.payment_failed":
        background_tasks.add_task(handle_stripe_payment_failed, data)
    elif event_type == "checkout.session.completed":
        background_tasks.add_task(handle_stripe_payment_succeeded, data)

    return {"status": "ok"}

# ============= WhatsApp Webhook =============

@app.get("/webhooks/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """Верификация WhatsApp webhook (GET запрос при настройке)"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified")
        return int(challenge)

    logger.warning("WhatsApp webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook endpoint для WhatsApp Business API"""
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Верификация подписи
    if not verify_whatsapp_signature(payload, signature, WHATSAPP_APP_SECRET):
        logger.warning("Invalid WhatsApp signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = json.loads(payload)

    # Извлечение сообщений
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])

            for message in messages:
                from_number = message.get("from")
                background_tasks.add_task(handle_whatsapp_message, message, from_number)

    return {"status": "ok"}

# ============= Generic Webhook =============

@app.post("/webhooks/{service}")
async def generic_webhook(
    service: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Универсальный webhook endpoint"""
    payload = await request.body()

    logger.info(f"Webhook received from {service}")
    logger.debug(f"Payload: {payload[:500]}")  # Первые 500 символов

    data = json.loads(payload)

    # Сохранить для отладки
    # TODO: Обработать в зависимости от сервиса

    return {"status": "ok", "service": service}

# ============= Health Check =============

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
