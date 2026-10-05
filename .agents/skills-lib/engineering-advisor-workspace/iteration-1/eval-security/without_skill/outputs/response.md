# Добавление Stripe webhook в Telegram-бот

Вот расширенный код обработчика с сохранением заказа в базу и отправкой уведомления:

```python
import sqlite3
import asyncio
from aiogram import Bot
from fastapi import FastAPI, Request

app = FastAPI()
bot = Bot(token="YOUR_BOT_TOKEN")

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("orders.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT,
            amount INTEGER,
            currency TEXT,
            customer_email TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_order(data):
    payment_intent = data.get("data", {}).get("object", {})
    conn = sqlite3.connect("orders.db")
    conn.execute("""
        INSERT INTO orders (payment_id, amount, currency, customer_email, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        payment_intent.get("id"),
        payment_intent.get("amount"),
        payment_intent.get("currency"),
        payment_intent.get("receipt_email"),
        payment_intent.get("status")
    ))
    conn.commit()
    conn.close()

async def send_notification(chat_id: int, message: str):
    await bot.send_message(chat_id=chat_id, text=message)

@app.post('/webhook')
async def handle(request: Request):
    data = await request.json()

    event_type = data.get("type")

    if event_type == "payment_intent.succeeded":
        # Сохраняем заказ в базу
        save_order(data)

        # Получаем chat_id из метаданных (нужно передавать при создании PaymentIntent)
        payment_intent = data.get("data", {}).get("object", {})
        metadata = payment_intent.get("metadata", {})
        chat_id = metadata.get("telegram_chat_id")

        # Отправляем уведомление пользователю
        if chat_id:
            amount = payment_intent.get("amount", 0) / 100
            currency = payment_intent.get("currency", "").upper()
            await send_notification(
                int(chat_id),
                f"Оплата прошла успешно!\nСумма: {amount} {currency}\nСпасибо за заказ!"
            )

    return {"status": "ok"}
```

## Что нужно сделать дополнительно

1. **Передавать `telegram_chat_id` при создании PaymentIntent** на стороне вашего бота:

```python
import stripe
stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

payment_intent = stripe.PaymentIntent.create(
    amount=5000,  # в центах
    currency="usd",
    metadata={"telegram_chat_id": str(chat_id)}
)
```

2. **Настроить webhook в Stripe Dashboard** → Developers → Webhooks → Add endpoint, указать URL вашего сервера.

3. Заменить `YOUR_BOT_TOKEN` и `YOUR_STRIPE_SECRET_KEY` на реальные значения.
