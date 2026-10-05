"""
Stripe Payment Flow
Полный пример интеграции платежей через Stripe

Функционал:
1. Создание платёжной сессии
2. Обработка webhook событий
3. Отправка подтверждения после оплаты

Использование:
    uvicorn stripe_payment_flow:app --reload --port 8000

Тестирование webhooks локально:
    stripe listen --forward-to localhost:8000/webhooks/stripe
"""

import os
import stripe
import logging
from datetime import datetime
from typing import Optional, Dict
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests

# ============= Configuration =============

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_xxx")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_xxx")

# WhatsApp для уведомлений
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")

app = FastAPI(title="Stripe Payment Flow")

# ============= Models =============

class PaymentRequest(BaseModel):
    booking_id: str
    amount: float  # в AED
    currency: str = "aed"
    customer_email: str
    customer_phone: str
    description: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class RefundRequest(BaseModel):
    payment_intent_id: str
    amount: Optional[float] = None  # Если не указано - полный refund
    reason: Optional[str] = None

# ============= Fake Database =============

PAYMENTS_DB = {}
BOOKINGS_DB = {
    "BK-001234": {
        "id": "BK-001234",
        "tour_name": "Дубай Сафари",
        "date": "2026-03-15",
        "price": 450,
        "customer_email": "ivan@example.com",
        "customer_phone": "+971501234567",
        "status": "pending_payment"
    }
}

# ============= WhatsApp Notifications =============

def send_whatsapp(to: str, message: str):
    """Отправить WhatsApp сообщение"""
    if not WHATSAPP_TOKEN:
        logger.info(f"WhatsApp disabled, would send to {to}: {message[:50]}...")
        return

    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"WhatsApp sent to {to}: {response.status_code}")
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")

# ============= Stripe Functions =============

def create_checkout_session(
    booking_id: str,
    amount: float,
    currency: str,
    customer_email: str,
    description: str,
    success_url: str,
    cancel_url: str
) -> Dict:
    """Создать Stripe Checkout Session"""

    # Конвертация в минимальные единицы (для AED - филсы)
    amount_cents = int(amount * 100)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": description,
                        "description": f"Booking ID: {booking_id}"
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                "booking_id": booking_id,
                "source": "tourism_api"
            },
            payment_intent_data={
                "metadata": {
                    "booking_id": booking_id
                }
            }
        )

        logger.info(f"Created checkout session: {session.id} for booking {booking_id}")

        return {
            "session_id": session.id,
            "payment_url": session.url,
            "expires_at": session.expires_at
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def create_payment_intent(
    amount: float,
    currency: str,
    customer_email: str,
    booking_id: str
) -> Dict:
    """Создать Payment Intent (для кастомных форм)"""

    amount_cents = int(amount * 100)

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            receipt_email=customer_email,
            metadata={
                "booking_id": booking_id
            }
        )

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def create_payment_link(
    amount: float,
    currency: str,
    description: str,
    booking_id: str
) -> Dict:
    """Создать Payment Link (многоразовый)"""

    amount_cents = int(amount * 100)

    try:
        # Сначала создаём Product и Price
        product = stripe.Product.create(
            name=description,
            metadata={"booking_id": booking_id}
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount_cents,
            currency=currency,
        )

        # Создаём Payment Link
        link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
            metadata={"booking_id": booking_id}
        )

        return {
            "payment_link": link.url,
            "link_id": link.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def process_refund(
    payment_intent_id: str,
    amount: Optional[float] = None,
    reason: Optional[str] = None
) -> Dict:
    """Создать возврат"""

    try:
        refund_data = {
            "payment_intent": payment_intent_id
        }

        if amount:
            refund_data["amount"] = int(amount * 100)

        if reason:
            refund_data["reason"] = reason

        refund = stripe.Refund.create(**refund_data)

        logger.info(f"Refund created: {refund.id}")

        return {
            "refund_id": refund.id,
            "status": refund.status,
            "amount": refund.amount / 100
        }

    except stripe.error.StripeError as e:
        logger.error(f"Refund error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============= Event Handlers =============

async def handle_payment_succeeded(payment_intent: Dict):
    """Обработка успешного платежа"""
    booking_id = payment_intent.get("metadata", {}).get("booking_id")
    amount = payment_intent.get("amount", 0) / 100
    currency = payment_intent.get("currency", "").upper()

    logger.info(f"Payment succeeded: {booking_id}, {amount} {currency}")

    # Сохранить в базу
    PAYMENTS_DB[payment_intent["id"]] = {
        "id": payment_intent["id"],
        "booking_id": booking_id,
        "amount": amount,
        "currency": currency,
        "status": "succeeded",
        "created_at": datetime.now().isoformat()
    }

    # Обновить статус бронирования
    if booking_id in BOOKINGS_DB:
        BOOKINGS_DB[booking_id]["status"] = "confirmed"
        BOOKINGS_DB[booking_id]["payment_id"] = payment_intent["id"]

        # Отправить уведомление
        booking = BOOKINGS_DB[booking_id]
        message = f"""
✅ Оплата получена!

Бронирование: {booking_id}
Тур: {booking['tour_name']}
Дата: {booking['date']}
Сумма: {amount} {currency}

Ваучер будет отправлен отдельным сообщением.

Спасибо за бронирование! 🙏
""".strip()

        send_whatsapp(booking["customer_phone"], message)


async def handle_payment_failed(payment_intent: Dict):
    """Обработка неудачного платежа"""
    booking_id = payment_intent.get("metadata", {}).get("booking_id")
    error = payment_intent.get("last_payment_error", {})
    error_message = error.get("message", "Unknown error")

    logger.warning(f"Payment failed: {booking_id}, error: {error_message}")

    if booking_id in BOOKINGS_DB:
        booking = BOOKINGS_DB[booking_id]

        message = f"""
❌ Оплата не прошла

Бронирование: {booking_id}
Причина: {error_message}

Пожалуйста, попробуйте ещё раз или используйте другую карту.

Если проблема повторяется, свяжитесь с нами.
""".strip()

        send_whatsapp(booking["customer_phone"], message)


async def handle_checkout_completed(session: Dict):
    """Обработка завершения Checkout Session"""
    booking_id = session.get("metadata", {}).get("booking_id")
    payment_intent_id = session.get("payment_intent")

    logger.info(f"Checkout completed: {booking_id}, payment_intent: {payment_intent_id}")

    # Платёж уже обработан в payment_intent.succeeded
    # Здесь можно добавить дополнительную логику

# ============= API Endpoints =============

@app.post("/payments/checkout")
async def create_checkout(request: PaymentRequest):
    """Создать Checkout Session для оплаты"""

    success_url = request.success_url or "https://example.com/success"
    cancel_url = request.cancel_url or "https://example.com/cancel"

    session = create_checkout_session(
        booking_id=request.booking_id,
        amount=request.amount,
        currency=request.currency,
        customer_email=request.customer_email,
        description=request.description,
        success_url=success_url,
        cancel_url=cancel_url
    )

    return session


@app.post("/payments/link")
async def create_link(request: PaymentRequest):
    """Создать Payment Link"""

    link = create_payment_link(
        amount=request.amount,
        currency=request.currency,
        description=request.description,
        booking_id=request.booking_id
    )

    return link


@app.post("/payments/refund")
async def refund_payment(request: RefundRequest):
    """Создать возврат"""

    refund = process_refund(
        payment_intent_id=request.payment_intent_id,
        amount=request.amount,
        reason=request.reason
    )

    return refund


@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    """Получить информацию о платеже"""

    if payment_id in PAYMENTS_DB:
        return PAYMENTS_DB[payment_id]

    # Запросить у Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(payment_id)
        return {
            "id": intent.id,
            "amount": intent.amount / 100,
            "currency": intent.currency.upper(),
            "status": intent.status,
            "booking_id": intent.metadata.get("booking_id")
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=404, detail="Payment not found")


# ============= Webhook Endpoint =============

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook endpoint для Stripe"""
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Stripe event: {event_type}")

    # Обработка событий в фоне
    if event_type == "payment_intent.succeeded":
        background_tasks.add_task(handle_payment_succeeded, data)
    elif event_type == "payment_intent.payment_failed":
        background_tasks.add_task(handle_payment_failed, data)
    elif event_type == "checkout.session.completed":
        background_tasks.add_task(handle_checkout_completed, data)

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "stripe-payments"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
