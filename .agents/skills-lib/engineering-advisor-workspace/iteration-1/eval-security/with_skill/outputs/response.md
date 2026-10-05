# Ответ Engineering Advisor

> Engineering Advisor активирован. Загружено 12 уроков из опыта. Буду проверять код с учётом накопленных ошибок.

---

## 🎯 Как я понял задачу:

Добавить в Stripe webhook-обработчик:
1. Сохранение данных заказа в базу данных
2. Отправку уведомления пользователю в Telegram

---

## СТОП — перед тем как писать код

Я проверил твой webhook и нашёл критические проблемы. Если добавить код прямо сейчас "как есть" — получится дыра в безопасности, через которую любой желающий сможет:

- Имитировать оплату и получить товар бесплатно
- Записать фиктивные заказы в базу
- Засыпать бота фальшивыми уведомлениями

---

```
=== Engineering Advisor ===
BLOCK (2):
  webhook.py:3 — Отсутствует верификация Stripe-подписи (Stripe-Signature header).
                 Любой HTTP-запрос на /webhook будет обработан как настоящий платёж.
  webhook.py:4 — process_payment(data) вызывается без await и без try/except.
                 Если упадёт — пользователь не узнает, деньги списаны, заказ не создан.

WARN (3):
  webhook.py — Нет валидации структуры data перед обращением к полям (KeyError).
  webhook.py — Нет идемпотентности: если Stripe пришлёт событие дважды (это нормально!),
               заказ запишется в базу два раза.
  webhook.py — Нет логирования: при ошибке невозможно понять что пришло и что упало.

INFO (1):
  webhook.py — process_payment() — синхронная функция в async-обработчике.
               Если она делает запросы к БД или сети — это блокирует весь event loop.

Опыт: применено 3 урока (EXP-046 XSS в Telegram HTML, EXP-053 async-блокировки, Trigger #23 webhook без верификации)
===========================
```

---

## Что нужно сделать — в правильном порядке

Это не просто "добавить строчку". Здесь 3 слоя, и каждый важен:

### Слой 1: Верификация подписи (ОБЯЗАТЕЛЬНО — без этого ничего не делаем)

Stripe подписывает каждый webhook заголовком `Stripe-Signature`. Нужно:
1. Получить RAW тело запроса (до JSON-парсинга)
2. Проверить подпись через `stripe.Webhook.construct_event()`
3. Только после проверки — работать с данными

**Почему raw body, а не data?** Stripe считает подпись по исходным байтам. Если сначала распарсить JSON, а потом `json.dumps()` — байты могут не совпасть (другой порядок ключей, пробелы). Это одна из самых частых ошибок при интеграции Stripe.

### Слой 2: Идемпотентность (защита от дублей)

Stripe гарантирует "at least once delivery" — одно событие может прийти 2-3 раза (сетевые ретраи). Нужно:
- Сохранять `event.id` в базе
- При повторном событии с тем же ID — пропустить, вернуть 200

### Слой 3: Обработка ошибок и логирование

- Каждый шаг в try/except
- Логировать что пришло (тип события) и что произошло (успех/ошибка)
- При ошибке возвращать 400 (Stripe повторит попытку), при успехе — 200

---

## Правильный код

```python
import stripe
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

WEBHOOK_SECRET = "whsec_..."  # Из Stripe Dashboard → Webhooks → Signing secret

@app.post('/webhook')
async def handle(request):
    # Шаг 1: Получаем RAW байты — до любого парсинга
    payload = await request.read()
    sig_header = request.headers.get('Stripe-Signature')

    # Шаг 2: Верификация подписи
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        logger.warning("[webhook] Невалидная подпись — запрос отклонён")
        return web.Response(status=400, text="Invalid signature")
    except Exception as e:
        logger.error(f"[webhook] Ошибка парсинга события: {e}")
        return web.Response(status=400, text="Parse error")

    # Шаг 3: Логируем что пришло
    logger.info(f"[webhook] Событие: {event['type']}, id: {event['id']}")

    # Шаг 4: Идемпотентность — проверяем не обрабатывали ли уже
    if await is_event_processed(event['id']):
        logger.info(f"[webhook] Событие {event['id']} уже обработано — пропуск")
        return web.Response(status=200, text="Already processed")

    # Шаг 5: Обрабатываем нужные типы событий
    try:
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            await save_order_to_db(payment_intent)
            await notify_user(payment_intent)
            await mark_event_processed(event['id'])
            logger.info(f"[webhook] Заказ сохранён, пользователь уведомлён. PaymentIntent: {payment_intent['id']}")

        else:
            logger.info(f"[webhook] Событие {event['type']} — не обрабатываем")

    except Exception as e:
        logger.error(f"[webhook] Ошибка обработки события {event['id']}: {e}")
        # Возвращаем 400 — Stripe повторит попытку позже
        return web.Response(status=400, text="Processing error")

    return web.Response(status=200, text="OK")
```

```python
# Вспомогательные функции — заполни под свою БД

async def is_event_processed(event_id: str) -> bool:
    # SELECT 1 FROM processed_events WHERE stripe_event_id = event_id
    ...

async def mark_event_processed(event_id: str):
    # INSERT INTO processed_events (stripe_event_id, processed_at) VALUES (event_id, NOW())
    ...

async def save_order_to_db(payment_intent: dict):
    order_id = payment_intent.get('metadata', {}).get('order_id')
    amount = payment_intent['amount']  # в центах
    currency = payment_intent['currency']
    # INSERT INTO orders ...
    ...

async def notify_user(payment_intent: dict):
    user_id = payment_intent.get('metadata', {}).get('telegram_user_id')
    if not user_id:
        logger.warning(f"[webhook] Нет telegram_user_id в metadata для {payment_intent['id']}")
        return
    # await bot.send_message(user_id, "Оплата получена!")
    ...
```

---

## Что нужно от тебя для продолжения

Прежде чем писать реальный код под твой проект — ответь:

1. **Какой фреймворк?** (aiohttp, FastAPI, aiogram webhooks, или что-то ещё)
2. **Какая база данных?** (aiosqlite, PostgreSQL+asyncpg, SQLAlchemy, или другая)
3. **Какие типы Stripe-событий** тебя интересуют? (`payment_intent.succeeded`, `checkout.session.completed`, `charge.refunded`?)
4. **Что должно быть в уведомлении** пользователю? (сумма, ссылка на заказ, что-то ещё?)
5. **Есть ли таблица processed_events** в базе, или нужно создать?

Как только ответишь — напишу точный код под твой стек, с сохранением заказа и уведомлением.

---

## Аналогия

Твой текущий webhook — это касса в магазине, у которой нет кассира. Любой может подойти, сказать "я заплатил" и забрать товар. Нам нужно добавить кассира (верификация подписи), кассовый журнал (идемпотентность) и чек (логирование) — и только потом учить кассира звонить клиенту (уведомление).

---

```
=== Engineering Advisor Summary ===
Файлы изменены: 0 (специально — до подтверждения не пишем код)
Триггеры сработали: #4 (Оплата/Stripe — MANDATORY), #13 (API endpoint), #23 (Webhook без верификации — MANDATORY)
Проверки: 0/6 — ожидаем ответы пользователя
BLOCK: 2 — отсутствие верификации подписи, синхронный вызов без error handling
WARN: 3 — нет валидации структуры, нет идемпотентности, нет логирования
INFO: 1 — sync function в async context
Опыт применён: Trigger #23, EXP-046 (async/logging patterns)
Новый опыт: не записан (сессия не завершена)
===================================
```
