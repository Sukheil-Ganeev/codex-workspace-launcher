# =============================================================================
# app.py — WhatsApp Bot (FastAPI webhook) для бронирования туров ОАЭ
# Meta Cloud API + shared core (PostgreSQL + Redis)
# =============================================================================

import os
import json
from fastapi import FastAPI, Request, Response

app = FastAPI(title="WhatsApp Bot - UAE Tours")

# --- Конфигурация ---
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "webhook_verify_token")
WA_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
CURRENCY = os.getenv("TOURS_CURRENCY", "AED")
LANGUAGE = os.getenv("BOT_LANGUAGE", "ru")

# --- Каталог туров ---
TOURS = [
    {"id": 1, "name": "Джип-сафари Премиум", "price": 250},
    {"id": 2, "name": "Обзорная экскурсия по Дубаю", "price": 180},
    {"id": 3, "name": "Абу-Даби полный день", "price": 220},
    {"id": 4, "name": "Бурдж-Халифа -- на вершине", "price": 260},
    {"id": 5, "name": "Круиз на яхте по Марине", "price": 350},
]


@app.get("/health")
async def health():
    """Health check для Docker и nginx."""
    return {
        "status": "ok",
        "service": "whatsapp-bot",
        "currency": CURRENCY,
        "tours_count": len(TOURS),
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Верификация webhook от Meta (GET запрос)."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")

    return Response(content="Forbidden", status_code=403)


@app.post("/webhook")
async def handle_webhook(request: Request):
    """Обработка входящих сообщений WhatsApp."""
    body = await request.json()

    # Извлечение сообщения из webhook payload
    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
    except (IndexError, KeyError):
        return {"status": "no messages"}

    for message in messages:
        sender = message.get("from", "")
        msg_type = message.get("type", "")
        text = ""

        if msg_type == "text":
            text = message.get("text", {}).get("body", "").lower().strip()

        # Простая логика ответов
        if text in ["туры", "tours", "экскурсии", "меню"]:
            reply = format_tours_list()
        elif text in ["помощь", "help", "start"]:
            reply = (
                "Привет! Я бот бронирования туров по ОАЭ.\n\n"
                "Команды:\n"
                "- *туры* -- список экскурсий\n"
                "- *помощь* -- это сообщение\n\n"
                f"Валюта: {CURRENCY}"
            )
        else:
            reply = "Напишите *туры* для просмотра экскурсий или *помощь* для списка команд."

        # В production здесь отправка через WhatsApp Cloud API
        print(f"[WhatsApp] {sender}: {text} -> Ответ: {reply[:50]}...")

    return {"status": "ok"}


def format_tours_list() -> str:
    """Форматирование списка туров для WhatsApp."""
    lines = ["*Экскурсии по ОАЭ:*\n"]
    for tour in TOURS:
        lines.append(f"  {tour['id']}. {tour['name']} -- *{tour['price']} {CURRENCY}*")
    lines.append(f"\nДля бронирования напишите номер тура.")
    return "\n".join(lines)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
