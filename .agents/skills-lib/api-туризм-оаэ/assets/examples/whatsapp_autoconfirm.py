"""
WhatsApp Auto-Confirmation System
Полный пример автоматического подтверждения бронирований через WhatsApp

Функционал:
1. Получение входящих сообщений через webhook
2. Парсинг запроса (номер бронирования, намерение)
3. Отправка подтверждения с деталями
4. Отправка ваучера (документ)

Использование:
    uvicorn whatsapp_autoconfirm:app --reload --port 8000

Для локального тестирования:
    ngrok http 8000
    Затем настроить webhook URL в Meta Business Suite
"""

import os
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import requests

# ============= Configuration =============

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "your_token")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID", "your_phone_id")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "your_app_secret")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_verify_token")

WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

app = FastAPI(title="WhatsApp Auto-Confirmation")

# ============= Fake Database =============

BOOKINGS_DB = {
    "BK-001234": {
        "id": "BK-001234",
        "tour_name": "Дубай Сафари",
        "date": "2026-03-15",
        "time": "15:00",
        "adults": 2,
        "children": 1,
        "price": 450,
        "currency": "AED",
        "status": "confirmed",
        "customer": {
            "name": "Иван Иванов",
            "phone": "+971501234567",
            "email": "ivan@example.com"
        },
        "pickup": {
            "location": "Atlantis The Palm",
            "time": "14:30",
            "notes": "Встреча у главного входа"
        }
    },
    "BK-005678": {
        "id": "BK-005678",
        "tour_name": "Абу-Даби Тур",
        "date": "2026-03-20",
        "time": "08:00",
        "adults": 4,
        "children": 0,
        "price": 800,
        "currency": "AED",
        "status": "pending_payment",
        "customer": {
            "name": "Мария Петрова",
            "phone": "+971509876543",
            "email": "maria@example.com"
        },
        "pickup": {
            "location": "JBR Beach",
            "time": "07:30",
            "notes": "Напротив отеля Hilton"
        }
    }
}

# ============= WhatsApp API Functions =============

def send_text_message(to: str, text: str) -> Dict:
    """Отправить текстовое сообщение"""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    logger.info(f"Sent message to {to}: {response.status_code}")
    return response.json()


def send_template_message(to: str, template_name: str, params: list) -> Dict:
    """Отправить шаблонное сообщение"""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "ru"},
            "components": [{
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in params]
            }]
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    logger.info(f"Sent template to {to}: {response.status_code}")
    return response.json()


def send_document(to: str, document_url: str, filename: str, caption: str = "") -> Dict:
    """Отправить документ (ваучер)"""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "link": document_url,
            "filename": filename,
            "caption": caption
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    logger.info(f"Sent document to {to}: {response.status_code}")
    return response.json()


def send_interactive_buttons(to: str, body_text: str, buttons: list) -> Dict:
    """Отправить сообщение с кнопками"""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"]}}
                    for btn in buttons
                ]
            }
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

# ============= Message Processing =============

def extract_booking_id(text: str) -> Optional[str]:
    """Извлечь номер бронирования из текста"""
    import re
    # Ищем паттерны: BK-123456, #123456, номер 123456
    patterns = [
        r'BK-(\d{6})',
        r'#(\d{6})',
        r'(?:номер|бронь|бронирование)\s*[#:]?\s*(\d{6})',
        r'(\d{6})'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            booking_num = match.group(1)
            return f"BK-{booking_num}" if not booking_num.startswith("BK-") else booking_num

    return None


def detect_intent(text: str) -> str:
    """Определить намерение пользователя"""
    text_lower = text.lower()

    if any(word in text_lower for word in ["подтверд", "статус", "бронирование", "booking"]):
        return "check_booking"
    elif any(word in text_lower for word in ["ваучер", "voucher", "билет", "ticket"]):
        return "get_voucher"
    elif any(word in text_lower for word in ["отмен", "cancel"]):
        return "cancel_booking"
    elif any(word in text_lower for word in ["изменить", "перенес", "change", "reschedule"]):
        return "modify_booking"
    elif any(word in text_lower for word in ["привет", "здравствуй", "hello", "hi"]):
        return "greeting"
    elif any(word in text_lower for word in ["цена", "стоимость", "price", "cost"]):
        return "price_inquiry"
    elif any(word in text_lower for word in ["помощь", "help"]):
        return "help"
    else:
        return "unknown"


def format_booking_confirmation(booking: Dict) -> str:
    """Форматировать подтверждение бронирования"""
    status_emoji = {
        "confirmed": "✅",
        "pending_payment": "⏳",
        "cancelled": "❌"
    }

    status_text = {
        "confirmed": "Подтверждено",
        "pending_payment": "Ожидает оплаты",
        "cancelled": "Отменено"
    }

    emoji = status_emoji.get(booking["status"], "📋")
    status = status_text.get(booking["status"], booking["status"])

    return f"""
{emoji} *Ваше бронирование {booking['id']}*

📍 *Тур:* {booking['tour_name']}
📅 *Дата:* {booking['date']}
🕐 *Время:* {booking['time']}

👥 *Гости:*
   Взрослые: {booking['adults']}
   Дети: {booking['children']}

💰 *Сумма:* {booking['price']} {booking['currency']}
📊 *Статус:* {status}

🚐 *Встреча:*
   📍 {booking['pickup']['location']}
   🕐 {booking['pickup']['time']}
   📝 {booking['pickup']['notes']}

Если у вас есть вопросы, напишите нам!
""".strip()

# ============= Message Handlers =============

async def handle_message(from_number: str, text: str):
    """Обработать входящее сообщение"""
    logger.info(f"Message from {from_number}: {text}")

    intent = detect_intent(text)
    booking_id = extract_booking_id(text)

    if intent == "greeting":
        await handle_greeting(from_number)
    elif intent == "help":
        await handle_help(from_number)
    elif intent == "check_booking":
        if booking_id:
            await handle_check_booking(from_number, booking_id)
        else:
            send_text_message(from_number, "Пожалуйста, укажите номер бронирования.\n\nПример: BK-001234")
    elif intent == "get_voucher":
        if booking_id:
            await handle_get_voucher(from_number, booking_id)
        else:
            send_text_message(from_number, "Для получения ваучера укажите номер бронирования.\n\nПример: Ваучер BK-001234")
    elif intent == "price_inquiry":
        await handle_price_inquiry(from_number, text)
    else:
        await handle_unknown(from_number)


async def handle_greeting(phone: str):
    """Приветствие"""
    message = """
Здравствуйте! 👋

Я бот для управления бронированиями. Вот что я умею:

📋 *Проверить бронирование* - напишите номер брони
📄 *Получить ваучер* - напишите "ваучер" + номер брони
💰 *Узнать цены* - напишите "цены"
❓ *Помощь* - напишите "помощь"

Чем могу помочь?
""".strip()

    send_text_message(phone, message)


async def handle_help(phone: str):
    """Справка"""
    message = """
📚 *Справка*

*Команды:*
• Отправьте номер бронирования (например: BK-001234) для проверки статуса
• "Ваучер BK-001234" - получить ваучер
• "Цены" - узнать стоимость туров

*Контакты:*
📞 +971 50 123 4567
📍 Дубай, Tecom (Barsha Heights)

Наши услуги:
🏜 Экскурсии и туры
🚗 Аренда автомобилей
🛥 Яхты
""".strip()

    send_text_message(phone, message)


async def handle_check_booking(phone: str, booking_id: str):
    """Проверка бронирования"""
    booking = BOOKINGS_DB.get(booking_id)

    if booking:
        confirmation = format_booking_confirmation(booking)
        send_text_message(phone, confirmation)

        # Предложить получить ваучер если статус confirmed
        if booking["status"] == "confirmed":
            send_interactive_buttons(
                phone,
                "Хотите получить ваучер?",
                [
                    {"id": f"voucher_{booking_id}", "title": "📄 Получить ваучер"},
                    {"id": "help", "title": "❓ Другой вопрос"}
                ]
            )
    else:
        send_text_message(
            phone,
            f"❌ Бронирование {booking_id} не найдено.\n\nПроверьте номер и попробуйте снова."
        )


async def handle_get_voucher(phone: str, booking_id: str):
    """Отправка ваучера"""
    booking = BOOKINGS_DB.get(booking_id)

    if not booking:
        send_text_message(phone, f"❌ Бронирование {booking_id} не найдено.")
        return

    if booking["status"] != "confirmed":
        send_text_message(
            phone,
            f"⚠️ Ваучер недоступен.\n\nСтатус бронирования: {booking['status']}\n\nОплатите бронирование для получения ваучера."
        )
        return

    # В реальном приложении здесь генерация PDF и загрузка на CDN
    voucher_url = f"https://example.com/vouchers/{booking_id}.pdf"

    send_document(
        phone,
        voucher_url,
        f"Voucher_{booking_id}.pdf",
        f"📄 Ваш ваучер для {booking['tour_name']}"
    )

    send_text_message(
        phone,
        f"✅ Ваучер отправлен!\n\nНе забудьте сохранить его на телефон.\n\nДо встречи {booking['date']} в {booking['pickup']['time']}!"
    )


async def handle_price_inquiry(phone: str, text: str):
    """Запрос цен"""
    prices = """
💰 *Наши туры и цены*

🏜 *Дубай Сафари*
   От 150 AED/чел
   6 часов, включён ужин

🏛 *Абу-Даби Тур*
   От 200 AED/чел
   10 часов, мечеть + дворец

🌊 *Яхта на полдня*
   От 1500 AED (до 10 чел)
   4 часа, включены напитки

🚗 *Аренда авто*
   От 150 AED/день
   Все классы

Для бронирования напишите название тура и дату!
""".strip()

    send_text_message(phone, prices)


async def handle_unknown(phone: str):
    """Неизвестная команда"""
    send_text_message(
        phone,
        "Не совсем понял ваш запрос 🤔\n\nНапишите:\n• Номер бронирования (BK-123456)\n• \"Цены\" для списка туров\n• \"Помощь\" для справки"
    )


async def handle_button_click(phone: str, button_id: str):
    """Обработка нажатия кнопки"""
    if button_id.startswith("voucher_"):
        booking_id = button_id.replace("voucher_", "")
        await handle_get_voucher(phone, booking_id)
    elif button_id == "help":
        await handle_help(phone)

# ============= Webhook Endpoints =============

def verify_signature(payload: bytes, signature: str) -> bool:
    """Проверка подписи webhook"""
    expected = hmac.new(
        WHATSAPP_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature or "")


@app.get("/webhooks/whatsapp")
async def verify_webhook(request: Request):
    """Верификация webhook при настройке"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhooks/whatsapp")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Получение webhook событий"""
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Верификация подписи (в production обязательно!)
    # if not verify_signature(payload, signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()

    # Извлечение сообщений
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            # Обработка текстовых сообщений
            for message in value.get("messages", []):
                from_number = message.get("from")

                if message.get("type") == "text":
                    text = message.get("text", {}).get("body", "")
                    background_tasks.add_task(handle_message, from_number, text)

                elif message.get("type") == "interactive":
                    # Нажатие кнопки
                    button_reply = message.get("interactive", {}).get("button_reply", {})
                    button_id = button_reply.get("id", "")
                    background_tasks.add_task(handle_button_click, from_number, button_id)

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "whatsapp-autoconfirm"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
