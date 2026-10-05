# =============================================================================
# app.py — WhatsApp Webhook бот для бронирования туров ОАЭ
# FastAPI + WhatsApp Cloud API | Февраль 2026
# =============================================================================

import os
import hmac
import hashlib
import httpx
from fastapi import FastAPI, Request, Response, HTTPException

# --- Конфигурация ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "webhook_secret_token")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
CURRENCY = os.getenv("TOURS_CURRENCY", "AED")
LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ru")
APP_SECRET = os.getenv("APP_SECRET", "")

# --- Каталог туров ---
TOURS = [
    {"id": 1, "name": "Desert Safari Premium", "price": 250, "duration": "6 часов"},
    {"id": 2, "name": "Dubai City Tour", "price": 180, "duration": "4 часа"},
    {"id": 3, "name": "Abu Dhabi Full Day", "price": 220, "duration": "10 часов"},
    {"id": 4, "name": "Burj Khalifa At The Top", "price": 260, "duration": "1.5 часа"},
    {"id": 5, "name": "Dubai Marina Yacht", "price": 350, "duration": "3 часа"},
]

app = FastAPI(title="WhatsApp Booking Bot", version="1.0.0")


@app.get("/health")
async def health():
    """Эндпоинт здоровья для Docker HEALTHCHECK."""
    return {"status": "ok", "currency": CURRENCY, "language": LANGUAGE}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Верификация webhook от Meta (GET-запрос с challenge)."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


def verify_signature(payload: bytes, signature: str) -> bool:
    """HMAC-SHA256 верификация подписи от Meta."""
    if not APP_SECRET or not signature:
        return True  # Пропускаем в dev-режиме
    expected = hmac.new(
        APP_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@app.post("/webhook")
async def handle_webhook(request: Request):
    """Обработка входящих сообщений от WhatsApp."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()

    # Извлекаем сообщение
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        message = value["messages"][0]
        from_number = message["from"]
        text = message.get("text", {}).get("body", "").strip().lower()
    except (KeyError, IndexError):
        return {"status": "no_message"}

    # Маршрутизация команд
    if text in ("туры", "tours", "список", "start"):
        response_text = format_tours_list()
    elif text.startswith("бронь") or text.startswith("book"):
        response_text = (
            f"Для бронирования напишите номер тура (1-{len(TOURS)}).\n"
            f"Например: 1"
        )
    elif text.isdigit() and 1 <= int(text) <= len(TOURS):
        tour = TOURS[int(text) - 1]
        response_text = (
            f"*{tour['name']}*\n"
            f"Цена: {tour['price']} {CURRENCY}\n"
            f"Длительность: {tour['duration']}\n\n"
            f"Для подтверждения свяжитесь с менеджером.\n"
            f"Офис: Дубай, Tecom (Barsha Heights)"
        )
    else:
        response_text = (
            f"Привет! Я бот бронирования туров по ОАЭ.\n\n"
            f"Напишите *туры* для списка экскурсий."
        )

    # Отправляем ответ через WhatsApp Cloud API
    await send_whatsapp_message(from_number, response_text)
    return {"status": "ok"}


def format_tours_list() -> str:
    """Форматирование списка туров для WhatsApp."""
    lines = [f"*Экскурсии и билеты ОАЭ:*\n"]
    for t in TOURS:
        lines.append(f"{t['id']}. *{t['name']}*")
        lines.append(f"   {t['price']} {CURRENCY} | {t['duration']}\n")
    lines.append(f"Напишите номер тура для подробностей.")
    return "\n".join(lines)


async def send_whatsapp_message(to: str, text: str):
    """Отправка текстового сообщения через WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print(f"[DEV] -> {to}: {text}")
        return

    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"WhatsApp API error: {response.status_code} {response.text}")
