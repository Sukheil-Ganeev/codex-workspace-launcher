# FAQ — Часто задаваемые вопросы

## Общие вопросы

### Q: Что такое API key и где его взять?

**A:** API key — это уникальный идентификатор для доступа к API. Получить его можно:
- **Stripe:** Dashboard → Developers → API keys
- **WhatsApp:** Meta Business → App → WhatsApp → Access Token
- **Google Maps:** Google Cloud Console → APIs & Services → Credentials
- **Viator:** Partner Hub → API Settings

### Q: В чём разница между REST и GraphQL?

**A:**
| REST | GraphQL |
|------|---------|
| Фиксированные endpoints | Один endpoint |
| Фиксированный формат ответа | Вы выбираете поля |
| Несколько запросов для связанных данных | Один запрос |
| Проще в освоении | Гибче, но сложнее |

**Для туризма:** Используйте REST (90% API так работают).

### Q: Как тестировать webhook локально?

**A:**
1. Установите ngrok: `npm install -g ngrok`
2. Запустите сервер: `uvicorn app:app --port 8000`
3. Запустите туннель: `ngrok http 8000`
4. Используйте URL типа `https://abc123.ngrok.io/webhooks/stripe`

### Q: Сколько стоят API вызовы?

**A:**
| Сервис | Стоимость |
|--------|-----------|
| WhatsApp Business | $0.05-0.15/сообщение |
| Stripe | 2.9% + $0.30/транзакция |
| Google Maps | $0.005/запрос (первые $200 бесплатно) |
| Viator | Комиссия от продаж |

### Q: Как защитить API ключи?

**A:**
1. Храните в `.env` файле
2. Добавьте `.env` в `.gitignore`
3. Никогда не коммитьте ключи
4. Используйте разные ключи для test/production

```python
# .env
STRIPE_API_KEY=sk_live_xxx

# Python
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("STRIPE_API_KEY")
```

## Технические вопросы

### Q: Почему получаю 401 Unauthorized?

**A:** Проверьте:
1. API key правильный (скопируйте заново)
2. Key не истёк (особенно для WhatsApp tokens)
3. Правильный header (`Authorization: Bearer` vs `X-API-Key`)
4. Test vs Live ключи (для Stripe)

### Q: Почему webhook не получает события?

**A:** Проверьте:
1. URL публично доступен (используйте ngrok для localhost)
2. Возвращаете 200 OK быстро (< 30 сек)
3. HTTPS обязателен
4. Signature verification правильная

### Q: Как обработать rate limit (429)?

**A:**
```python
import time

if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    time.sleep(retry_after)
    # Повторить запрос
```

### Q: Как отправить файл через WhatsApp API?

**A:**
```python
# 1. Загрузить файл
upload_url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/media"
files = {"file": open("voucher.pdf", "rb")}
data = {"messaging_product": "whatsapp", "type": "document"}
media = requests.post(upload_url, headers=headers, files=files, data=data).json()

# 2. Отправить сообщение с media_id
message_data = {
    "messaging_product": "whatsapp",
    "to": phone,
    "type": "document",
    "document": {"id": media["id"], "filename": "voucher.pdf"}
}
```

### Q: Как сделать запрос асинхронно?

**A:**
```python
import aiohttp
import asyncio

async def fetch_tours():
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()

# Запуск
tours = asyncio.run(fetch_tours())
```

## Бизнес-вопросы

### Q: Какой API использовать для бронирования экскурсий?

**A:**
- **Viator** — крупнейшая платформа, хороший API
- **GetYourGuide** — альтернатива, меньше комиссия
- **Прямые поставщики** — лучшие цены, но сложнее интегрировать

### Q: Как принимать платежи в AED?

**A:** Stripe поддерживает AED напрямую:
```python
stripe.PaymentIntent.create(
    amount=45000,  # 450 AED в филсах
    currency="aed"
)
```

### Q: Нужен ли мне сервер для webhooks?

**A:** Да, нужен публичный сервер. Варианты:
- **VPS** (DigitalOcean, Linode) — от $5/мес
- **Serverless** (AWS Lambda, Vercel) — pay per use
- **PaaS** (Railway, Render) — бесплатный tier

### Q: Как автоматизировать всё без программирования?

**A:** Используйте no-code платформы:
- **Make.com** — визуальная автоматизация
- **n8n** — self-hosted альтернатива
- **Zapier** — простейший вариант

Но для сложных сценариев код эффективнее.
