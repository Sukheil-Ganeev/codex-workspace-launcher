---
name: api-туризм-оаэ
description: "Работа с API для туристического бизнеса в ОАЭ. Используй когда нужно интегрировать API (REST, Webhooks, GraphQL, WebSocket), автоматизировать бронирование, платежи, уведомления через WhatsApp/Telegram/Stripe/Booking/Viator/Google Maps. Включает примеры кода, шаблоны, troubleshooting."
---
# API для туристического бизнеса ОАЭ

## Когда использовать этот скилл

**Триггеры:**
- "интегрируй API", "подключи Stripe", "настрой WhatsApp Business API"
- "автоматизируй бронирование", "синхронизируй цены"
- "webhook для платежей", "real-time уведомления"
- "как работает API", "пример REST запроса"
- "отправь сообщение WhatsApp", "создай платёж Stripe"

**НЕ использовать для:**
- Общих вопросов программирования без API контекста
- Работы с базами данных напрямую
- Frontend разработки без API интеграции

## Философия

API — это интерфейс для автоматизации коммуникации между системами. В туристическом бизнесе ОАЭ API позволяет:
- Автоматизировать бронирование из мессенджеров
- Синхронизировать цены с поставщиками
- Принимать платежи онлайн (AED, USD, криптовалюта)
- Отправлять подтверждения клиентам через WhatsApp/Telegram
- Отслеживать трансферы в реальном времени

## Бизнес-контекст

| Направление | Ответственный | API интеграции |
|-------------|---------------|----------------|
| Экскурсии и билеты | Сухейль | Viator, GetYourGuide, WhatsApp |
| Аренда автомобилей | Марсель | Своя система, Stripe, GPS |
| Яхты (Paramount Yachts) | Муфамад | Booking system, Calendar, Catering |

**Офис:** Дубай, Tecom (Barsha Heights)
**Клиенты:** Туристы из СНГ
**Языки:** Русский, Английский

---

## Раздел 1: Quick Start

### 1.1 Первый REST запрос (5 минут)

```bash
# Проверка API (публичный пример)
curl https://jsonplaceholder.typicode.com/posts/1

# С аутентификацией (ваш API)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.viator.com/tours?city=dubai
```

### 1.2 Первый webhook (10 минут)

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("type")

    if event_type == "payment_intent.succeeded":
        booking_id = payload["data"]["object"]["metadata"]["booking_id"]
        print(f"Payment received for booking: {booking_id}")
        # TODO: Отправить ваучер клиенту

    return {"status": "ok"}
```

### 1.3 Отправка WhatsApp сообщения

```python
import requests

def send_whatsapp(to: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Использование
send_whatsapp("+971501234567", "Ваше бронирование подтверждено!")
```

---

## Раздел 2: REST API

### 2.1 HTTP методы

| Метод | Действие | Пример из туризма |
|-------|----------|-------------------|
| GET | Получить | Список туров в Дубае |
| POST | Создать | Новое бронирование |
| PUT | Заменить | Полное обновление брони |
| PATCH | Изменить | Изменить дату брони |
| DELETE | Удалить | Отменить бронирование |

### 2.2 Структура запроса

```bash
curl -X POST "https://api.viator.com/bookings" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tour_id": "dubai-safari-001",
    "date": "2026-03-15",
    "adults": 2,
    "children": 1,
    "customer": {
      "name": "Иван Иванов",
      "email": "ivan@example.com",
      "phone": "+971501234567"
    }
  }'
```

**Компоненты:**
- **URL**: `https://api.viator.com/bookings`
- **Method**: `POST`
- **Headers**: `Authorization`, `Content-Type`
- **Body**: JSON с данными бронирования

### 2.3 Обработка ответа

```python
import requests

response = requests.post(
    "https://api.viator.com/bookings",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=booking_data
)

if response.status_code == 201:
    booking = response.json()
    print(f"Booking created: {booking['id']}")
    # Отправить подтверждение клиенту
elif response.status_code == 400:
    error = response.json()
    print(f"Error: {error['message']}")
elif response.status_code == 401:
    print("Invalid API key")
elif response.status_code == 429:
    print("Rate limit exceeded, retry later")
```

### 2.4 Аутентификация

**API Key в headers:**
```python
headers = {"X-API-Key": "your-api-key"}
```

**Bearer Token (JWT):**
```python
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1..."}
```

**Загрузка из .env:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("VIATOR_API_KEY")
```

---

## Раздел 3: Webhooks

### 3.1 Что такое Webhooks

Webhooks — это "обратные API вызовы" (Push модель):
- Вы регистрируете URL endpoint
- Внешний сервис отправляет POST при событии
- Вы обрабатываете событие

### 3.2 Настройка endpoint

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature")

    # Верификация подписи
    if not verify_stripe_signature(payload, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    event = await request.json()

    # Обработка событий
    if event["type"] == "payment_intent.succeeded":
        await handle_payment_success(event["data"]["object"])
    elif event["type"] == "payment_intent.payment_failed":
        await handle_payment_failed(event["data"]["object"])

    return {"status": "ok"}

async def handle_payment_success(payment):
    booking_id = payment["metadata"]["booking_id"]
    # 1. Обновить статус бронирования
    # 2. Сгенерировать ваучер
    # 3. Отправить клиенту через WhatsApp
```

### 3.3 WhatsApp Webhooks

```python
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()

    # Проверяем что есть сообщения
    messages = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [])

    for message in messages:
        from_number = message["from"]
        text = message.get("text", {}).get("body", "")

        # Простая обработка команд
        if "бронирование" in text.lower():
            await send_booking_info(from_number, text)
        elif "цена" in text.lower():
            await send_price_info(from_number, text)
        else:
            await send_whatsapp(from_number, "Напишите 'бронирование' или 'цена'")

    return {"status": "ok"}

@app.get("/webhooks/whatsapp")
async def verify_whatsapp(request: Request):
    """Верификация webhook при настройке в Meta Business"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403)
```

---

## Раздел 4: Популярные сервисы

### 4.1 WhatsApp Business API

**Регистрация:**
1. Meta Business Manager → Create App
2. Add WhatsApp product
3. Get access token (временный на 24 часа или постоянный)
4. Verify phone number

**Отправка сообщения:**
```python
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID")

def send_whatsapp_text(to: str, text: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    return requests.post(url, headers=headers, json=data).json()

def send_whatsapp_template(to: str, template_name: str, params: list):
    """Отправка шаблонного сообщения (для бизнес-уведомлений)"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
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
    return requests.post(url, headers=headers, json=data).json()
```

### 4.2 Stripe API

**Создание платежа:**
```python
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_payment(amount_aed: int, booking_id: str, customer_email: str):
    """Создать платёжную сессию"""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "aed",
                "product_data": {"name": "Booking Payment"},
                "unit_amount": amount_aed * 100,  # в филсах
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://yoursite.com/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://yoursite.com/cancel",
        customer_email=customer_email,
        metadata={"booking_id": booking_id}
    )
    return session.url

# Использование
payment_url = create_payment(450, "booking-123", "client@example.com")
# Отправить payment_url клиенту в WhatsApp
```

**Webhook для подтверждения:**
```python
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=403, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = session["metadata"]["booking_id"]

        # Платёж прошёл → отправляем ваучер
        await send_voucher(booking_id)
        await send_whatsapp_text(
            get_customer_phone(booking_id),
            f"Оплата получена! Ваш ваучер отправлен."
        )

    return {"status": "ok"}
```

### 4.3 Google Maps API

**Маршрут от отеля до достопримечательности:**
```python
import requests

GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_route(origin: str, destination: str):
    """Получить маршрут и время в пути"""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "departure_time": "now",
        "language": "ru",
        "key": GOOGLE_MAPS_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        route = data["routes"][0]["legs"][0]
        return {
            "distance": route["distance"]["text"],
            "duration": route["duration_in_traffic"]["text"],
            "start_address": route["start_address"],
            "end_address": route["end_address"]
        }
    return None

# Пример
route = get_route("Atlantis The Palm, Dubai", "Burj Khalifa, Dubai")
print(f"Расстояние: {route['distance']}, Время: {route['duration']}")
```

---

## Раздел 5: Обработка ошибок

### 5.1 HTTP статусы

| Код | Значение | Действие |
|-----|----------|----------|
| 200 | OK | Всё хорошо |
| 201 | Created | Ресурс создан |
| 400 | Bad Request | Проверить параметры запроса |
| 401 | Unauthorized | Проверить API key |
| 403 | Forbidden | Нет прав доступа |
| 404 | Not Found | Неверный URL или ID |
| 429 | Too Many Requests | Rate limit, подождать |
| 500 | Server Error | Retry через 30 сек |

### 5.2 Retry logic

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

# Использование
session = create_session_with_retry()
response = session.get("https://api.example.com/tours")
```

### 5.3 Обработка 429 (Rate Limit)

```python
def make_request_with_rate_limit(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        print(f"Rate limited, waiting {retry_after} seconds")
        time.sleep(retry_after)
        response = requests.get(url, headers=headers)

    return response
```

---

## Раздел 6: Безопасность

### 6.1 Хранение API ключей

**НИКОГДА не делайте:**
```python
# ❌ ПЛОХО
API_KEY = "sk_live_abc123"  # Ключ в коде
url = f"https://api.com?key={API_KEY}"  # Ключ в URL (видно в логах)
```

**ВСЕГДА делайте:**
```python
# ✅ ХОРОШО
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}"}
```

### 6.2 .env файл

```bash
# .env (добавить в .gitignore!)
STRIPE_API_KEY=sk_live_xxxxxxxxxxxx
WHATSAPP_TOKEN=EAAxxxxxxxxx
GOOGLE_MAPS_KEY=AIzaxxxxxxxxx
WEBHOOK_SECRET=whsec_xxxxxxxxx
```

### 6.3 Верификация webhook signature

```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Раздел 7: Типичные ошибки и решения

### 7.1 "401 Unauthorized"

**Причина:** Неверный API key или истёк token

**Решение:**
```python
# Проверить что ключ загружен
print(f"API Key (first 10): {API_KEY[:10]}...")

# Для JWT: проверить expiration
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(f"Expires: {decoded.get('exp')}")
```

### 7.2 "429 Too Many Requests"

**Причина:** Превышен rate limit

**Решение:**
- Использовать retry logic с exponential backoff
- Кэшировать повторяющиеся запросы
- Проверить rate limits в документации API

### 7.3 Webhook не получает события

**Причины и решения:**
1. **URL недоступен** → Использовать ngrok для локальной разработки
2. **Signature не проходит** → Проверить WEBHOOK_SECRET
3. **HTTPS required** → Webhooks работают только через HTTPS
4. **Firewall блокирует** → Открыть порт 443

```bash
# Локальная разработка с ngrok
ngrok http 8000
# Получаете https://abc123.ngrok.io → используйте этот URL в настройках webhook
```

### 7.4 CORS ошибки

**Причина:** Browser блокирует запросы к другому домену

**Решение:** Делать запросы с backend, не с frontend
```python
# Backend делает запрос к API
@app.get("/api/tours")
async def get_tours():
    response = requests.get("https://api.viator.com/tours", headers=headers)
    return response.json()
```

---

## Краткая памятка

| Задача | Метод | Пример |
|--------|-------|--------|
| Получить данные | GET | `curl https://api.com/tours` |
| Создать бронь | POST | `curl -X POST -d '{"tour":"123"}' https://api.com/bookings` |
| Обновить бронь | PATCH | `curl -X PATCH -d '{"date":"2026-03-20"}' https://api.com/bookings/123` |
| Удалить | DELETE | `curl -X DELETE https://api.com/bookings/123` |
| Получить webhook | POST endpoint | `@app.post("/webhooks/stripe")` |
| Отправить WhatsApp | POST | `requests.post(whatsapp_url, json=message_data)` |
| Создать платёж | Stripe SDK | `stripe.checkout.Session.create(...)` |

---

## Дополнительные ресурсы

| Ресурс | Путь | Описание |
|--------|------|----------|
| **FAQ** | [references/faq.md](references/faq.md) | Часто задаваемые вопросы |
| **Troubleshooting** | [references/troubleshooting.md](references/troubleshooting.md) | Решение проблем |
| **Cheatsheet** | [references/cheatsheet.md](references/cheatsheet.md) | Быстрая справка |
| **Глоссарий** | [references/glossary.md](references/glossary.md) | Термины |
| **Шаблоны** | [assets/templates/](assets/templates/) | Готовые шаблоны кода |
| **Примеры** | [assets/examples/](assets/examples/) | Полные рабочие примеры |
| **Справочник** | `D:/Downloads/API_СПРАВОЧНИК/` | Детальный справочник |

---

## Связанные скиллы

- `туризм-оаэ-автоматизация` — Общая автоматизация бизнеса
- `whatsapp-парсер` — Парсинг WhatsApp чатов
- `генератор-инвойсов` — Создание инвойсов

---

## НАКОПЛЕННЫЙ ОПЫТ

**Перед началом работы прочитай:** `experience/_index.md`

Скилл готов к накоплению опыта. Ожидаемые категории:
- API интеграции (GetYourGuide, Viator, TripAdvisor)
- Webhooks и обработка событий
- Аутентификация и rate limiting

При завершении — скажи "запиши это в опыт" если был полезный урок.
