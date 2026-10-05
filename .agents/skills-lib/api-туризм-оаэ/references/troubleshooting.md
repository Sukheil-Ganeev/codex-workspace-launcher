# Troubleshooting — Решение проблем

## HTTP ошибки

### 400 Bad Request

**Симптомы:** API возвращает 400 с сообщением об ошибке

**Причины:**
- Неверный формат JSON
- Отсутствуют обязательные поля
- Неверный тип данных (строка вместо числа)

**Решения:**
```python
# Проверить JSON
import json
try:
    json.loads(your_data)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")

# Валидировать данные перед отправкой
required_fields = ["tour_id", "date", "adults"]
for field in required_fields:
    if field not in data:
        raise ValueError(f"Missing required field: {field}")
```

### 401 Unauthorized

**Симптомы:** "Invalid API key" или "Unauthorized"

**Причины:**
- Неверный API key
- Истёк token
- Неправильный header

**Решения:**
```python
# 1. Проверить что ключ загружается
print(f"Key loaded: {bool(API_KEY)}")
print(f"Key prefix: {API_KEY[:10]}...")

# 2. Проверить header
# Правильно:
headers = {"Authorization": f"Bearer {token}"}  # Для JWT
headers = {"X-API-Key": api_key}  # Для API Key

# Неправильно:
headers = {"Authorization": api_key}  # Забыли "Bearer "

# 3. Для JWT проверить expiration
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
import time
if decoded["exp"] < time.time():
    print("Token expired!")
```

### 403 Forbidden

**Симптомы:** "Access denied" или "Forbidden"

**Причины:**
- Нет прав на этот ресурс
- IP не в whitelist
- Аккаунт заблокирован

**Решения:**
1. Проверить права API key в dashboard сервиса
2. Проверить IP restrictions
3. Связаться с поддержкой сервиса

### 404 Not Found

**Симптомы:** "Resource not found"

**Причины:**
- Неверный URL
- Ресурс удалён
- Неверный ID

**Решения:**
```python
# Проверить URL
print(f"Request URL: {response.url}")

# Проверить ID существует
booking = get_booking(booking_id)
if not booking:
    print(f"Booking {booking_id} not found")
```

### 429 Too Many Requests

**Симптомы:** "Rate limit exceeded"

**Причины:** Слишком много запросов за период

**Решения:**
```python
import time
from functools import wraps

def rate_limited(max_per_second):
    min_interval = 1.0 / max_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait = min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limited(10)  # Max 10 запросов в секунду
def make_api_call(url):
    return requests.get(url)
```

### 500 Internal Server Error

**Симптомы:** Сервер вернул 500

**Причины:** Ошибка на стороне API провайдера

**Решения:**
```python
# Retry с exponential backoff
import time

def retry_request(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code != 500:
            return response
        wait = 2 ** attempt  # 1, 2, 4 секунды
        print(f"Server error, retrying in {wait}s...")
        time.sleep(wait)
    raise Exception("Max retries exceeded")
```

## Webhook проблемы

### Webhook не получает события

**Диагностика:**
1. Проверить URL доступен публично
2. Проверить логи сервера
3. Использовать webhook.site для тестирования

```bash
# Тест доступности
curl -X POST https://your-domain.com/webhooks/test -d '{"test": true}'
```

### Signature verification fails

**Причины:**
- Неверный секрет
- Payload изменён
- Неправильный алгоритм

**Решения:**
```python
# Stripe
import stripe
try:
    event = stripe.Webhook.construct_event(
        payload, sig_header, webhook_secret
    )
except stripe.error.SignatureVerificationError:
    # Проверить webhook_secret в Stripe Dashboard
    print("Invalid signature")

# WhatsApp (SHA256)
import hmac
import hashlib

expected = hmac.new(
    app_secret.encode(),
    payload,
    hashlib.sha256
).hexdigest()

if not hmac.compare_digest(f"sha256={expected}", signature):
    print("Invalid WhatsApp signature")
```

### Webhook timeout

**Симптомы:** Webhook получает событие, но сервис помечает как failed

**Причина:** Обработка занимает > 30 секунд

**Решение:**
```python
from fastapi import BackgroundTasks

@app.post("/webhooks/stripe")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    # Сразу вернуть 200
    background_tasks.add_task(process_payment, payload)

    return {"status": "ok"}  # Вернуть быстро!

async def process_payment(payload):
    # Долгая обработка в фоне
    await send_voucher(payload["booking_id"])
    await update_crm(payload)
```

## WhatsApp API проблемы

### "Message failed to send"

**Причины:**
- Номер не в правильном формате
- Пользователь не начал диалог (для non-template)
- Шаблон не одобрен

**Решения:**
```python
# Формат номера: только цифры с кодом страны
phone = "+971501234567"  # ОАЭ
phone = phone.replace("+", "").replace(" ", "").replace("-", "")
# Результат: 971501234567

# Для первого сообщения используйте template
send_whatsapp_template(phone, "hello_template", [name])
```

### "Template not found"

**Причины:**
- Шаблон не создан в Meta Business
- Неверное имя шаблона
- Шаблон на модерации

**Решения:**
1. Проверить в Meta Business Suite → WhatsApp → Message Templates
2. Убедиться что статус "Approved"
3. Использовать точное имя (case-sensitive)

## Stripe проблемы

### "No such payment_intent"

**Причина:** Используете test ID в live mode или наоборот

**Решение:**
```python
# Test ключи начинаются с sk_test_
# Live ключи начинаются с sk_live_

# Проверить режим
if API_KEY.startswith("sk_test_"):
    print("Using TEST mode")
else:
    print("Using LIVE mode")
```

### Webhook события не приходят

**Решения:**
1. Stripe Dashboard → Webhooks → проверить endpoint
2. Проверить события в логе webhook
3. Использовать Stripe CLI для локального тестирования:
```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

## Общие советы

### Логирование

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def make_request(url, data):
    logger.debug(f"Request: {url}")
    logger.debug(f"Data: {data}")

    response = requests.post(url, json=data)

    logger.debug(f"Status: {response.status_code}")
    logger.debug(f"Response: {response.text[:500]}")

    return response
```

### Тестирование в изоляции

```python
# Тест отдельного компонента
def test_stripe_connection():
    stripe.api_key = os.getenv("STRIPE_TEST_KEY")
    try:
        stripe.Account.retrieve()
        print("Stripe connection OK")
    except stripe.error.AuthenticationError:
        print("Stripe auth failed")
```
