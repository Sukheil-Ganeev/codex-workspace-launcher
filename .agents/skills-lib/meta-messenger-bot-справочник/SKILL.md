---
name: meta-messenger-bot-справочник
description: "Production-ready руководство по Meta Messenger Platform для Instagram и Facebook ботов. Send API, Webhooks, шаблоны, Handover Protocol, Recurring Notifications. Используй когда нужно создать бота для Instagram DM, Facebook Messenger, автоматизировать переписку в мессенджерах Meta, настроить webhook для IG/FB, отправлять шаблоны (Generic, Receipt, Button), Ice Breakers, Quick Replies, Private Replies, Story Mentions."
---
# Meta Messenger Bot — Справочник (Instagram + Facebook)

## 1. Обзор платформы

Instagram DM и Facebook Messenger работают через **одну платформу** — Meta Messenger Platform (Graph API **v22.0**). Один Meta App обслуживает оба канала, различие — в webhook object (`page` vs `instagram`) и доступных фичах.

### Сравнительная таблица IG vs FB

| Аспект | Instagram | Facebook Messenger |
|--------|-----------|-------------------|
| Webhook object | `instagram` | `page` |
| Писать первым | **Нет** | Да (m.me ссылки) |
| Массовые рассылки | **Нет** | Recurring Notifications |
| Persistent Menu | 1 уровень, 20 пунктов | 3 уровня, 3 пункта/уровень |
| Get Started button | **Нет** (Ice Breakers) | Да (payload) |
| Greeting text | **Нет** | Да (`{{user_first_name}}`) |
| Button Template | **Нет** | Да |
| Receipt Template | **Нет** | Да |
| Airline Templates | **Нет** | Да |
| Media Template | **Нет** | Да |
| WebView | **Нет** | Да (compact/tall/full) |
| phone_number кнопка | **Нет** | Да |
| OTN (One-Time Notif) | **Нет** | Да |
| Recurring Notifications | **Нет** | Да (daily/weekly/monthly) |
| wit.ai NLP | **Нет** | Да (intents + entities) |
| Handover Protocol | **Нет** (Quick Reply) | Да (Primary/Secondary) |
| Sender Actions | **Нет** | Да (typing_on/off, mark_seen) |
| messaging_type | Не требуется | Обязателен (RESPONSE/UPDATE/TAG) |
| Private Replies | Да (комментарий -> DM) | **Нет** |
| Story Mentions | Да | **Нет** |
| Модерация комментариев | Да (hide/delete) | **Нет** |
| Rate limit | 200/час на аккаунт | 200 * followers/час |
| PSID/IGSID | IGSID | PSID (+ ASID) |
| User Profile API | **Нет** | Да (name, photo) |
| 24ч окно | Да | Да |
| Human Agent Tag (7 дней) | Да | Да |

---

## 2. Quick Start — Первый бот за 30 минут

### 2.1 Создание Meta App

1. [developers.facebook.com](https://developers.facebook.com) -> **My Apps** -> **Create App** -> тип **Business**
2. Название: `Dubai Tours Bot`, указать email
3. **Add Product** -> **Messenger** -> **Set Up**
4. **Add Product** -> **Webhooks**

### 2.2 Подключение Page + Instagram

1. Messenger Settings -> **Access Tokens** -> выбрать Facebook Page -> **Generate Token**
2. Для Instagram: привязать Instagram Business/Creator аккаунт к Facebook Page
3. Получить IG Business Account ID:

```bash
curl "https://graph.facebook.com/v22.0/PAGE_ID?fields=instagram_business_account&access_token=TOKEN"
# -> {"instagram_business_account":{"id":"17841405309211844"}}
```

### 2.3 Permissions (App Review)

| Permission | Назначение |
|-----------|-----------|
| `pages_messaging` | Отправка/получение сообщений (IG + FB) |
| `pages_manage_metadata` | Подписка на webhook events |
| `instagram_basic` | Профиль и медиа IG |
| `instagram_manage_messages` | DM Instagram (App Review) |
| `instagram_manage_comments` | Комментарии IG (App Review) |

### 2.4 Page Access Token (бессрочный)

```bash
# Short-lived -> Long-lived (60 дней)
GET https://graph.facebook.com/v22.0/oauth/access_token?
  grant_type=fb_exchange_token&client_id={APP_ID}&
  client_secret={APP_SECRET}&fb_exchange_token={SHORT_TOKEN}

# Long-lived User Token -> бессрочный Page Token
GET https://graph.facebook.com/v22.0/me/accounts?access_token={LONG_LIVED_USER_TOKEN}
```

### 2.5 Webhook Setup

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

const VERIFY_TOKEN = process.env.VERIFY_TOKEN;
const APP_SECRET = process.env.APP_SECRET;

// Верификация подписи X-Hub-Signature-256
app.use(express.json({
  verify: (req, res, buf) => {
    const sig = req.headers['x-hub-signature-256'];
    if (!sig) throw new Error('Missing signature');
    const expected = 'sha256=' + crypto
      .createHmac('sha256', APP_SECRET).update(buf).digest('hex');
    if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected)))
      throw new Error('Invalid signature');
  }
}));

// GET — верификация от Meta
app.get('/webhook', (req, res) => {
  const { 'hub.mode': mode, 'hub.verify_token': token, 'hub.challenge': challenge } = req.query;
  mode === 'subscribe' && token === VERIFY_TOKEN
    ? res.status(200).send(challenge)
    : res.sendStatus(403);
});

// POST — входящие события (IG + FB)
app.post('/webhook', (req, res) => {
  const { object, entry } = req.body;
  if (object === 'page' || object === 'instagram') {
    entry.forEach(e => e.messaging?.forEach(event => {
      if (event.message) handleMessage(event, object);
      else if (event.postback) handlePostback(event, object);
    }));
    res.status(200).send('EVENT_RECEIVED');
  } else res.sendStatus(404);
});
```

### 2.6 Отправка сообщения (Send API)

```bash
POST https://graph.facebook.com/v22.0/me/messages?access_token={TOKEN}
Content-Type: application/json

{
  "recipient": {"id": "USER_ID"},
  "message": {"text": "Добро пожаловать в Dubai Tours!"}
}
```

Для FB добавить `"messaging_type": "RESPONSE"` (обязательно). Для IG не требуется.

---

## 3. Webhooks — получение сообщений

### 3.1 Webhook Events

| Event | Поле | IG | FB |
|-------|------|----|----|
| Сообщения | `messages` | + | + |
| Нажатие кнопок | `messaging_postbacks` | + | + |
| Реферальные ссылки | `messaging_referrals` | + | + |
| Подписки (optin) | `messaging_optins` | - | + |
| Доставка | `message_deliveries` | - | + |
| Прочтение | `message_reads` | + | + |
| Реакции | `message_reactions` | + | - |
| Handover | `messaging_handovers` | - | + |

### 3.2 Структура webhook payload

**Instagram** — `body.object === 'instagram'`, sender ID = IGSID.
**Facebook** — `body.object === 'page'`, sender ID = PSID. Содержит `nlp` (если wit.ai включён).

### 3.3 Retry Policy (FB)

Meta повторяет доставку: 1 мин -> 5 мин -> 30 мин -> 1 час -> каждый час до 24ч. После — webhook отключается. Всегда возвращай `200 OK` за <5 секунд, обрабатывай асинхронно.

### 3.4 Дедупликация

Проверяй `message.mid` — Meta может повторно отправить то же событие.

---

## 4. Общие интерактивные элементы (IG + FB)

### 4.1 Quick Replies (до 13 кнопок)

Кнопки под сообщением, исчезают после нажатия.

```json
{
  "recipient": {"id": "USER_ID"},
  "message": {
    "text": "Что интересует?",
    "quick_replies": [
      {"content_type": "text", "title": "Экскурсии", "payload": "TOURS"},
      {"content_type": "text", "title": "Яхты", "payload": "YACHTS"},
      {"content_type": "text", "title": "Трансферы", "payload": "TRANSFERS"},
      {"content_type": "user_email"},
      {"content_type": "user_phone_number"}
    ]
  }
}
```

`user_email` и `user_phone_number` запрашивают контакт с согласия пользователя.

### 4.2 Generic Template (до 10 карточек)

Горизонтальная карусель с изображениями и кнопками.

```json
{
  "recipient": {"id": "USER_ID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [{
          "title": "Desert Safari — 200 AED",
          "subtitle": "Джип 4x4, верблюды, BBQ ужин, шоу",
          "image_url": "https://example.com/safari.jpg",
          "buttons": [
            {"type": "postback", "title": "Забронировать", "payload": "BOOK_SAFARI"},
            {"type": "web_url", "url": "https://example.com/safari", "title": "Подробнее"}
          ]
        }]
      }
    }
  }
}
```

### 4.3 Ice Breakers (до 4 вопросов)

Приветственные вопросы при первом открытии чата.

```bash
POST /me/messenger_profile?access_token={TOKEN}
# Для IG добавить "platform": "instagram"

{"ice_breakers": [
  {"question": "Экскурсии и билеты", "payload": "ICE_TOURS"},
  {"question": "Аренда яхты", "payload": "ICE_YACHTS"},
  {"question": "Трансферы", "payload": "ICE_TRANSFERS"},
  {"question": "Связаться с менеджером", "payload": "ICE_HUMAN"}
]}
```

### 4.4 Persistent Menu

**Instagram:** 1 уровень, до 20 пунктов. Добавить `"platform": "instagram"`.
**Facebook:** до 3 уровней, 3 пункта/уровень. Поддержка `nested` type и `locale`.

```json
// Facebook — вложенное меню с локализацией
{"persistent_menu": [{
  "locale": "default",
  "composer_input_disabled": false,
  "call_to_actions": [
    {"type": "postback", "title": "Каталог", "payload": "CATALOG"},
    {"type": "nested", "title": "Услуги", "call_to_actions": [
      {"type": "postback", "title": "Яхты", "payload": "YACHTS"},
      {"type": "postback", "title": "Авто", "payload": "CARS"}
    ]},
    {"type": "web_url", "title": "Сайт", "url": "https://example.com"}
  ]
}]}
```

### 4.5 Вложения

| Тип | Формат | Макс. размер |
|-----|--------|-------------|
| `image` | JPEG, PNG, GIF | 8 MB |
| `video` | MP4 | 25 MB |
| `audio` | AAC, MP4, WAV | 25 MB |
| `file` | PDF и др. | 25 MB |

FB: `is_reusable: true` для кеширования вложений.

---

## 5. Instagram-специфичные фичи

### 5.1 Критические ограничения IG

- **Нельзя писать первым** — только ответы на DM, комментарий, Story mention, Ice Breaker
- **Нет массовых рассылок** — нет broadcast/newsletter API
- **Нет Sponsored Messages, Get Started, Greeting**
- **Нет Button/Receipt/Media/Airline шаблонов**
- **Нет WebView, phone_number кнопки**
- **Стикеры** — получать можно, отправлять нельзя
- **Нет inline-кнопок в тексте** — только Quick Replies, Generic Template, Persistent Menu
- **Нет оплаты в чате**
- **Только Business/Creator аккаунты**

### 5.2 Private Replies (комментарий -> DM)

Автоматическая отправка DM пользователю, оставившему комментарий к вашему посту.

```javascript
async function handleComment(comment) {
  if (comment.text.match(/скольк|цен|price/i)) {
    await axios.post(
      `https://graph.facebook.com/v22.0/${comment.id}/private_replies`,
      { message: 'Спасибо за интерес! Вот наши цены...' },
      { params: { access_token: PAGE_TOKEN } }
    );
  }
}
```

Ограничения: 1 reply на комментарий, 24ч на отправку, не для Live-комментариев.

### 5.3 Story Mentions & Replies

```javascript
function handleStoryMention(event) {
  sendMessage(event.sender.id, {
    text: 'Спасибо за упоминание в Stories! Скидка 10%: STORY10'
  });
}

// Ответы на Story приходят с event.message.reply_to.story
```

### 5.4 Модерация комментариев

```javascript
// Скрыть
await axios.post(`https://graph.facebook.com/v22.0/${commentId}`,
  { hide: true }, { params: { access_token: TOKEN } });

// Удалить
await axios.delete(`https://graph.facebook.com/v22.0/${commentId}`,
  { params: { access_token: TOKEN } });

// Автомодерация спама
const spamPatterns = [/dm me for/i, /check bio/i, /free followers/i, /bit\.ly/i];
```

---

## 6. Facebook-специфичные фичи

### 6.1 Get Started + Greeting

```json
POST /me/messenger_profile
{"get_started": {"payload": "GET_STARTED"}}

{"greeting": [
  {"locale": "default", "text": "Welcome, {{user_first_name}}! Best tours in UAE."},
  {"locale": "ru_RU", "text": "Добро пожаловать, {{user_first_name}}! Лучшие экскурсии ОАЭ."}
]}
```

### 6.2 Button Template (текст + 3 кнопки)

```json
{"template_type": "button", "text": "Чем помочь?", "buttons": [
  {"type": "postback", "title": "Каталог", "payload": "CATALOG"},
  {"type": "phone_number", "title": "Позвонить", "payload": "+971501234567"},
  {"type": "web_url", "title": "Сайт", "url": "https://example.com"}
]}
```

### 6.3 Receipt Template (чек бронирования)

```json
{"template_type": "receipt",
 "recipient_name": "Aleksei Ivanov",
 "order_number": "DXB-2026-0142",
 "currency": "AED",
 "payment_method": "Cash on arrival",
 "summary": {"subtotal": 1040, "total_tax": 52, "total_cost": 1092},
 "elements": [{
   "title": "Burj Khalifa At The Top",
   "subtitle": "4 x 260 AED", "quantity": 4, "price": 1040, "currency": "AED"
 }]
}
```

### 6.4 Airline Templates

- **Boarding Pass** — `airline_boardingpass`: QR, gate, terminal, flight info
- **Itinerary** — `airline_itinerary`: маршрут, рейсы, класс, цена

### 6.5 WebView (URL Button)

```json
{"type": "web_url", "url": "https://example.com/booking",
 "title": "Оформить заказ", "webview_height_ratio": "tall",
 "messenger_extensions": true}
```

Размеры: `compact` (50%), `tall` (75%), `full` (100%).

### 6.6 Sender Actions

```json
{"recipient": {"id": "PSID"}, "sender_action": "typing_on"}
```

`typing_on` (20 сек), `typing_off`, `mark_seen`.

### 6.7 messaging_type (обязательно для FB)

| Тип | Использование |
|-----|--------------|
| `RESPONSE` | Ответ на сообщение (24ч) |
| `UPDATE` | Проактивное обновление (24ч) |
| `MESSAGE_TAG` | Вне 24ч окна с тегом |

### 6.8 One-Time Notification (OTN)

Одноразовое сообщение вне 24ч окна с согласия пользователя. Токен живёт до 1 года.

```json
// Запрос
{"template_type": "one_time_notif_req",
 "title": "Уведомить о скидке на Safari?", "payload": "SAFARI_NOTIFY"}

// Отправка (по токену из webhook optin)
{"recipient": {"one_time_notif_token": "TOKEN"}, "message": {"text": "Скидка 25%!"}}
```

### 6.9 Recurring Notifications (замена Broadcast)

```json
{"template_type": "notification_messages",
 "title": "Еженедельные спецпредложения",
 "payload": "WEEKLY_DEALS",
 "notification_messages_frequency": "WEEKLY",
 "notification_messages_reoptin": "ENABLED"}
```

Частоты: `DAILY`, `WEEKLY`, `MONTHLY`. Токен обновляется после каждого использования.

### 6.10 wit.ai NLP

Включить: App Dashboard -> Messenger Settings -> Built-in NLP.

```json
// Автоматически в webhook event.message.nlp
{"intents": [{"name": "book_tour", "confidence": 0.95}],
 "entities": {"wit$datetime:datetime": [{"value": "2026-03-15"}],
              "wit$number:number": [{"value": 4}]}}
```

### 6.11 Message Tags (вне 24ч окна)

| Тег | Назначение |
|-----|-----------|
| `CONFIRMED_EVENT_UPDATE` | Обновление подтверждённого события |
| `POST_PURCHASE_UPDATE` | Обновление после покупки |
| `ACCOUNT_UPDATE` | Обновление аккаунта |
| `HUMAN_AGENT` | Ответ живого оператора (7 дней) |

---

## 7. Human Agent Handover

### 7.1 Instagram — Quick Reply подход

```javascript
async function offerHuman(userId) {
  await sendMessage(userId, {
    text: 'Подключить менеджера?',
    quick_replies: [
      {content_type: "text", title: "Да", payload: "HUMAN_AGENT"},
      {content_type: "text", title: "Нет", payload: "CONTINUE_BOT"}
    ]
  });
}
// При выборе "Да" -> уведомить команду, отправить с тегом HUMAN_AGENT (7 дней)
```

### 7.2 Facebook — Handover Protocol

```json
// Бот передаёт оператору (Secondary Receiver)
POST /me/pass_thread_control
{"recipient": {"id": "PSID"}, "target_app_id": 123456, "metadata": "Тема: яхта"}

// Оператор возвращает боту (Primary Receiver)
POST /me/take_thread_control
{"recipient": {"id": "PSID"}, "metadata": "Вопрос решён"}
```

Webhook events: `pass_thread_control`, `take_thread_control`, `request_thread_control`.

---

## 8. Состояния диалога (FSM)

```javascript
const sessions = new Map();

async function handleMessage(event, platform) {
  const userId = event.sender.id;
  const text = event.message?.text || '';
  const session = sessions.get(userId) || { state: 'IDLE', data: {} };
  sessions.set(userId, session);

  switch (session.state) {
    case 'IDLE':
      if (text.match(/экскурс|тур|safari|сафари/i)) {
        session.state = 'CHOOSING_TOUR';
        await sendGenericTemplate(userId, tourCatalog);
      } else await sendWelcomeQuickReplies(userId);
      break;
    case 'CHOOSING_TOUR':
      session.data.tour = text;
      session.state = 'CHOOSING_DATE';
      await sendMessage(userId, {text: 'На какую дату?'});
      break;
    case 'CHOOSING_DATE':
      session.data.date = text;
      session.state = 'CHOOSING_GUESTS';
      await sendMessage(userId, {text: 'Сколько гостей?',
        quick_replies: [
          {content_type:'text', title:'1-2', payload:'G_2'},
          {content_type:'text', title:'3-4', payload:'G_4'},
          {content_type:'text', title:'5+', payload:'G_5'}
        ]});
      break;
    case 'CHOOSING_GUESTS':
      session.data.guests = text;
      session.state = 'IDLE';
      await sendMessage(userId, {text:
        `Заявка: ${session.data.tour}, ${session.data.date}, ${session.data.guests} гостей.\nМенеджер скоро свяжется!`});
      notifyTeam(session.data);
      session.data = {};
      break;
  }
}
```

---

## 9. Rate Limits

| Параметр | Instagram | Facebook |
|----------|-----------|---------|
| API вызовов | 200/час (аккаунт) | 200 * followers/час |
| Messaging Window | 24 часа | 24 часа |
| Human Agent Tag | 7 дней | 7 дней |
| Quick Replies | 13 | 13 |
| Generic Template | 10 карточек | 10 карточек |
| Ice Breakers | 4 | 4 |
| Private Reply | 1/комментарий | N/A |
| Persistent Menu | 20 (1 уровень) | 3x3 (3 уровня) |
| Медиа | 8/25 MB | 25 MB |

Ошибка 613 = rate limit. Решение: очередь сообщений с retry через 1 час.

---

## 10. Деплой

### Node.js + Express

```bash
npm install express axios dotenv
# .env: PAGE_ACCESS_TOKEN, APP_SECRET, VERIFY_TOKEN, PORT
# Production: VPS + Nginx + PM2 + Let's Encrypt ($5-10/мес)
```

### Python (FastAPI)

```python
from fastapi import FastAPI, Request, HTTPException
import httpx, os

app = FastAPI()

@app.get("/webhook")
async def verify(hub_mode: str = "", hub_verify_token: str = "", hub_challenge: str = ""):
    if hub_mode == "subscribe" and hub_verify_token == os.getenv("VERIFY_TOKEN"):
        return int(hub_challenge)
    raise HTTPException(403)

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    if body.get("object") not in ("page", "instagram"):
        raise HTTPException(404)
    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            if "message" in event:
                await handle_message(event, body["object"])
    return "OK"
```

### Serverless (AWS Lambda)

```javascript
exports.handler = async (event) => {
  if (event.httpMethod === 'GET') {
    const p = event.queryStringParameters;
    if (p['hub.verify_token'] === process.env.VERIFY_TOKEN)
      return { statusCode: 200, body: p['hub.challenge'] };
    return { statusCode: 403 };
  }
  // POST -> SQS для асинхронной обработки
  await sqs.sendMessage({QueueUrl: QUEUE_URL, MessageBody: event.body}).promise();
  return { statusCode: 200, body: 'EVENT_RECEIVED' };
};
```

---

## 11. Библиотеки и инструменты

| Инструмент | Язык | Назначение |
|-----------|------|-----------|
| Bottender | Node.js/TS | Мультиплатформенный фреймворк (IG + FB + TG) |
| Botpress | Node.js | Visual flow builder + NLU |
| messenger-node | Node.js | Минималистичная обёртка Send API |
| pymessenger | Python | Обёртка Send API |
| Claudia Bot Builder | Node.js | AWS Lambda-native |
| ManyChat / Chatfuel | No-code | Визуальные конструкторы ботов |
| ngrok | Любой | Туннель для локальной разработки |

---

## Ресурсы

| Ресурс | URL |
|--------|-----|
| Messenger Platform Docs | https://developers.facebook.com/docs/messenger-platform |
| Instagram Messaging Docs | https://developers.facebook.com/docs/instagram-messaging |
| Send API Reference | https://developers.facebook.com/docs/messenger-platform/reference/send-api |
| Template Reference | https://developers.facebook.com/docs/messenger-platform/send-messages/templates |
| Webhook Reference | https://developers.facebook.com/docs/messenger-platform/webhook |
| Messenger Profile API | https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api |
| Graph API Explorer | https://developers.facebook.com/tools/explorer |
| wit.ai (NLP) | https://wit.ai |
| Bottender Framework | https://bottender.js.org |
| Graph API Changelog | https://developers.facebook.com/docs/graph-api/changelog |

---

## 12. Production Implementation Patterns (VIP-DXB CatalogBot)

Реальные паттерны из production Facebook Messenger бота для туристического бизнеса в ОАЭ (Phase 20, февраль 2026).

### 12.1 Архитектура: один FastAPI сервер на платформу

```
VIP-DXB-CatalogBot/
├── bot/                 # Telegram (aiogram, порт не нужен)
├── instagram_bot/       # Instagram DM (FastAPI, порт 8081)
├── whatsapp_bot/        # WhatsApp Cloud API (FastAPI, порт 8082)
├── facebook_bot/        # Facebook Messenger (FastAPI, порт 8083)
│   ├── app.py           # FastAPI + webhook endpoints + lifespan
│   ├── config.py        # Re-export shared config + FB-specific vars
│   ├── webhook_verify.py # HMAC-SHA256 (re-uses instagram_bot)
│   ├── meta_api.py      # FacebookAPI class (Send API wrapper)
│   ├── fsm.py           # FBState enum + FSMManager (in-memory)
│   ├── formatters.py    # Plain text + emoji (no HTML in Messenger)
│   ├── templates.py     # Quick Reply + Generic Template builders
│   └── handlers/
│       ├── common.py    # process_webhook + route_event
│       ├── catalog.py   # Emirates -> Categories -> Blocks carousel
│       ├── booking.py   # 7-step FSM + Telegram notification
│       └── search.py    # Text search with carousel results
├── data/
│   └── catalog.db       # Shared SQLite DB (WAL mode)
└── core/                # Shared business logic
```

**Shared SQLite DB с WAL mode** для concurrent access из 4+ процессов.

### 12.2 messaging_type ОБЯЗАТЕЛЕН (Facebook, не IG)

Каждый вызов Send API для Facebook ОБЯЗАН включать `messaging_type`. Без него API вернёт 400 ошибку.

```python
class FacebookAPI:
    async def send_text(self, recipient_id: str, text: str,
                        messaging_type: str = "RESPONSE") -> dict:
        return await self._send({
            "messaging_type": messaging_type,  # ОБЯЗАТЕЛЬНО!
            "recipient": {"id": recipient_id},
            "message": {"text": text[:2000]},
        })
```

| Тип | Когда использовать |
|-----|-------------------|
| `RESPONSE` | Ответ на сообщение пользователя (default, внутри 24ч) |
| `UPDATE` | Проактивное обновление (внутри 24ч) |
| `MESSAGE_TAG` + tag | После 24ч окна (CONFIRMED_EVENT_UPDATE, POST_PURCHASE_UPDATE, HUMAN_AGENT) |

**Gotcha:** Для `sender_action` (typing_on/off, mark_seen) `messaging_type` НЕ нужен.

### 12.3 Sender Actions для UX

В отличие от Instagram, Facebook поддерживает Sender Actions. Отправляй `mark_seen` при КАЖДОМ входящем сообщении и `typing_on` перед длинными операциями.

```python
async def process_webhook(db, api, fsm, data):
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            # 1. Mark as seen (immediate)
            await api.send_sender_action(sender_id, "mark_seen")
            # 2. Process and respond
            await route_event(db, api, fsm, sender_id, event)
```

```python
# Перед длинной операцией (DB query, carousel build):
await api.send_sender_action(sender_id, "typing_on")
await handle_category(db, api, fsm, sender_id, emirate, parent_id)
```

### 12.4 FastAPI webhook паттерн (Python)

```python
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB, API client, FSM on startup; cleanup on shutdown."""
    db = CatalogDB(DB_PATH)
    await db.init()
    api = FacebookAPI(FB_PAGE_ACCESS_TOKEN)
    fsm = FSMManager()
    app.state.db = db
    app.state.api = api
    app.state.fsm = fsm
    yield
    await api.close()
    await db.close()

app = FastAPI(lifespan=lifespan)

# GET — Meta verification challenge
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
) -> PlainTextResponse:
    if hub_mode == "subscribe" and hub_verify_token == FB_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(403)

# POST — incoming messages
@app.post("/webhook")
async def receive_webhook(request: Request) -> dict:
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if META_APP_SECRET and not verify_hmac(META_APP_SECRET, body, signature):
        raise HTTPException(403, "Invalid signature")
    data = json.loads(body)
    # object="page" для Facebook (не "instagram")
    await process_webhook(request.app.state.db, request.app.state.api,
                          request.app.state.fsm, data)
    return {"status": "ok"}
```

**Ключевое:** `object="page"` для Facebook, `object="instagram"` для Instagram.

### 12.5 Get Started + Persistent Menu + Greeting

```python
# При старте бота настроить через Messenger Profile API:
await api.set_get_started("GET_STARTED")

await api.set_persistent_menu([
    {"type": "postback", "title": "Dubai", "payload": "MENU_EMIRATE_DXB"},
    {"type": "postback", "title": "Abu Dhabi", "payload": "MENU_EMIRATE_AD"},
    {"type": "postback", "title": "Search", "payload": "MENU_SEARCH"},
    {"type": "postback", "title": "WhatsApp", "payload": "MENU_WHATSAPP"},
])

await api.set_greeting([
    {"locale": "default", "text": "Welcome, {{user_first_name}}! Best tours in UAE."},
    {"locale": "ru_RU", "text": "{{user_first_name}}, лучшие экскурсии ОАЭ!"},
])
```

**Gotcha:** Get Started button не отображается, пока не настроен через Messenger Profile API. Это НЕ автоматическая фича.

### 12.6 User Profile API

Facebook позволяет получить имя и фото пользователя (Instagram — нет):

```python
async def get_user_profile(self, psid: str) -> dict:
    url = f"{self.BASE_URL}/{psid}"
    resp = await self._client.get(url, params={
        "fields": "first_name,last_name,profile_pic",
        "access_token": self._token,
    })
    return resp.json()
    # {"first_name": "Aleksei", "last_name": "Ivanov", "profile_pic": "https://..."}
```

### 12.7 Synthetic user_id для общей БД

Все 5 платформ (Telegram, VK, Instagram, WhatsApp, Facebook) используют одну SQLite БД. Для избежания коллизий ID:

| Платформа | Диапазон user_id | Offset |
|-----------|-----------------|--------|
| Telegram | Как есть (positive) | 0 |
| VK | +10,000,000,000 | VK_ID_OFFSET |
| Instagram | -1 .. -999 | Negative synthetic |
| WhatsApp | -1000 .. -1999 | Negative synthetic |
| **Facebook** | **-2000 .. -2999** | **Negative synthetic** |

```python
# database.py
async def get_or_create_fb_user(self, psid: str, fb_name: str = "") -> dict:
    """Get or create Facebook user, returning synthetic_user_id."""
    # SELECT ... WHERE psid = ?
    # INSERT ... VALUES (?, ?, next_synthetic_id)
    # synthetic_user_id starts at -2000, decrements: -2001, -2002, ...
```

Позволяет переиспользовать `add_booking()`, `get_loyalty()`, `get_user_payments()` без изменений.

### 12.8 Booking FSM (7 шагов)

```
BOOK:{id} → BOOKING_NAME → BOOKING_PHONE → BOOKING_DATE
         → BOOKING_ADULTS → BOOKING_CHILDREN → BOOKING_PROMO
         → BOOKING_CONFIRM → confirm → DB + Telegram notification
```

```python
class FBState(str, Enum):
    IDLE = "idle"
    SEARCH_WAITING = "search_waiting"
    BOOKING_NAME = "booking_name"
    BOOKING_PHONE = "booking_phone"
    BOOKING_DATE = "booking_date"
    BOOKING_ADULTS = "booking_adults"
    BOOKING_CHILDREN = "booking_children"
    BOOKING_PROMO = "booking_promo"
    BOOKING_CONFIRM = "booking_confirm"
```

**In-memory FSM** с 1h timeout — достаточно для Messenger (24ч окно, процесс рестартует → пользователь нажимает Get Started).

### 12.9 form_type для аналитики по платформам

| Платформа | form_type |
|-----------|-----------|
| Telegram | `GT`, `PT`, `Buggy`, etc. |
| Instagram | `IG_GT` |
| WhatsApp | `WA_GT` |
| **Facebook** | **`FB_GT`** |
| VK | `GT` (+ VK_ID_OFFSET) |

### 12.10 Telegram notification при бронировании

```python
async def _notify_telegram(booking_id: int, data: dict, block: dict):
    """Send notification to Telegram admin via direct HTTP (no aiogram)."""
    from facebook_bot.config import CATALOG_BOT_TOKEN, ADMIN_CHAT_ID
    url = f"https://api.telegram.org/bot{CATALOG_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=5.0) as client:
        await client.post(url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": f"New booking from Facebook Messenger: #{booking_id}",
            "parse_mode": "HTML",
        })
```

**Паттерн:** Все non-Telegram боты (Instagram, WhatsApp, Facebook) уведомляют менеджеров через прямой HTTP POST к Telegram Bot API.

### 12.11 HMAC-SHA256 verification (shared)

Один `META_APP_SECRET` для всех Meta-платформ (Instagram, WhatsApp, Facebook):

```python
# facebook_bot/webhook_verify.py — re-uses Instagram implementation
from instagram_bot.webhook_verify import verify_hmac  # Same HMAC logic

# Verification:
import hashlib, hmac
expected = "sha256=" + hmac.new(
    META_APP_SECRET.encode(), body, hashlib.sha256
).hexdigest()
is_valid = hmac.compare_digest(signature, expected)
```

### 12.12 Carousel pagination (Generic Template)

```python
PAGE_SIZE = 9  # 9 blocks + 1 "See more" = max 10 elements

def build_carousel(blocks, page=0, emirate="", category=""):
    start = page * PAGE_SIZE
    page_blocks = blocks[start:start + PAGE_SIZE]
    elements = [build_generic_element(b) for b in page_blocks]

    total_pages = (len(blocks) + PAGE_SIZE - 1) // PAGE_SIZE
    if page + 1 < total_pages:
        elements.append({
            "title": "See more...",
            "subtitle": f"Page {page + 2} of {total_pages}",
            "buttons": [{
                "type": "postback",
                "title": "Next Page",
                "payload": f"PAGE:{emirate}:{category}:{page + 1}",
            }],
        })
    return elements  # Max 10 elements
```

**Stateless пагинация** — номер страницы в payload.

### 12.13 Envars (.env)

```
# Facebook Messenger Bot
FB_PAGE_ACCESS_TOKEN=EAA...    # Page Access Token (бессрочный)
FB_PAGE_ID=123456789            # Facebook Page ID
FB_VERIFY_TOKEN=fb_verify_2026  # Webhook verification token
FB_WEBHOOK_PORT=8083            # FastAPI server port

# Shared with Instagram/WhatsApp
META_APP_SECRET=abc123...       # HMAC signature verification
CATALOG_BOT_TOKEN=...           # Telegram bot token (for notifications)
ADMIN_CHAT_ID=...               # Telegram chat for notifications
DB_PATH=data/catalog.db         # Shared SQLite database
```

### 12.14 Gotchas и Best Practices

| Проблема | Решение |
|----------|---------|
| 400 error от API | Проверь `messaging_type` — обязателен в каждом сообщении |
| PSID is Page-Scoped | Один пользователь = разные ID для разных Pages. Не путай с ASID |
| Get Started не появляется | Настрой через `POST /me/messenger_profile` (Messenger Profile API) |
| Echo loop | Фильтруй `sender.id == recipient.id` (page sending to itself) |
| Webhook timeout | Отвечай 200 OK за <5 сек, обрабатывай асинхронно |
| Rate limit (613) | Очередь сообщений + retry через 1 час; FB: 200 * followers/час |
| Shared DB concurrency | WAL mode (`PRAGMA journal_mode=WAL`) при init() |
| No HTML in Messenger | Plain text + emoji formatting (как Instagram и WhatsApp) |

---

| Файл | Описание |
|------|----------|
| README.md | Описание структуры скилла |
| references/faq.md | Часто задаваемые вопросы |
| references/cheatsheet.md | Шпаргалка по API |
| experience/_index.md | Журнал опыта реализации |
