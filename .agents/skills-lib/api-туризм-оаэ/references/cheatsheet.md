# Cheatsheet — Быстрая справка

## cURL

```bash
# GET запрос
curl https://api.example.com/tours

# GET с headers
curl -H "Authorization: Bearer TOKEN" https://api.example.com/tours

# POST с JSON
curl -X POST https://api.example.com/bookings \
  -H "Content-Type: application/json" \
  -d '{"tour_id": "123"}'

# POST с файлом
curl -X POST https://api.example.com/upload \
  -F "file=@document.pdf"

# Показать headers ответа
curl -i https://api.example.com/tours

# Verbose (debug)
curl -v https://api.example.com/tours

# Сохранить в файл
curl -o response.json https://api.example.com/tours

# Follow redirects
curl -L https://api.example.com/tours
```

## HTTP статусы

| Код | Значение | Что делать |
|-----|----------|------------|
| 200 | OK | Успех |
| 201 | Created | Ресурс создан |
| 204 | No Content | Успех без данных |
| 400 | Bad Request | Проверить параметры |
| 401 | Unauthorized | Проверить API key |
| 403 | Forbidden | Нет прав |
| 404 | Not Found | Проверить URL/ID |
| 429 | Rate Limit | Подождать, retry |
| 500 | Server Error | Retry позже |

## Python requests

```python
import requests

# GET
response = requests.get(url, headers=headers, params=params)

# POST
response = requests.post(url, headers=headers, json=data)

# PUT
response = requests.put(url, headers=headers, json=data)

# DELETE
response = requests.delete(url, headers=headers)

# Обработка ответа
if response.ok:  # status_code < 400
    data = response.json()
else:
    print(f"Error: {response.status_code}")
    print(response.text)

# Timeout
response = requests.get(url, timeout=10)  # 10 секунд

# Session (для нескольких запросов)
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})
response = session.get(url)
```

## JavaScript fetch

```javascript
// GET
const response = await fetch(url, {
  headers: { "Authorization": `Bearer ${token}` }
});
const data = await response.json();

// POST
const response = await fetch(url, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ tour_id: "123" })
});

// Обработка ошибок
if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}
```

## FastAPI (webhook receiver)

```python
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhooks/{service}")
async def webhook(service: str, request: Request):
    payload = await request.json()

    if service == "stripe":
        # Верификация
        sig = request.headers.get("Stripe-Signature")
        # ... verify signature

    return {"status": "ok"}

# Запуск
# uvicorn main:app --reload --port 8000
```

## Аутентификация

```python
# API Key
headers = {"X-API-Key": "your-key"}
# или
headers = {"Authorization": "ApiKey your-key"}

# Bearer Token (JWT)
headers = {"Authorization": f"Bearer {jwt_token}"}

# Basic Auth
import base64
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {credentials}"}
# или проще:
response = requests.get(url, auth=(username, password))
```

## WhatsApp Business API

```python
PHONE_ID = "your_phone_number_id"
TOKEN = "your_access_token"

# Отправить текст
def send_text(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    return requests.post(url,
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
    ).json()

# Отправить template
def send_template(to, template_name, params):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    return requests.post(url,
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
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
    ).json()
```

## Stripe

```python
import stripe
stripe.api_key = "sk_test_xxx"

# Создать checkout session
session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[{
        "price_data": {
            "currency": "aed",
            "product_data": {"name": "Tour Booking"},
            "unit_amount": 45000,  # 450 AED
        },
        "quantity": 1,
    }],
    mode="payment",
    success_url="https://site.com/success",
    cancel_url="https://site.com/cancel",
    metadata={"booking_id": "123"}
)
# session.url - ссылка для оплаты

# Webhook
event = stripe.Webhook.construct_event(
    payload, sig_header, webhook_secret
)
```

## Google Maps

```python
API_KEY = "your_google_maps_key"

# Directions
def get_directions(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "key": API_KEY,
        "language": "ru"
    }
    return requests.get(url, params=params).json()

# Distance Matrix
def get_distance(origins, destinations):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "key": API_KEY
    }
    return requests.get(url, params=params).json()
```

## .env файл

```bash
# .env
STRIPE_API_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
WHATSAPP_TOKEN=EAAxx
WHATSAPP_PHONE_ID=123456
GOOGLE_MAPS_KEY=AIzaxx

# Python загрузка
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("STRIPE_API_KEY")
```

## Retry logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def make_api_call(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```
