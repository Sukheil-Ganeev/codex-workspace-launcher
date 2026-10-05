---
name: whatsapp-bot-spravochnik
description: "Production-ready руководство по WhatsApp Bot / Business API (Cloud API) для туристического бизнеса ОАЭ. Автоматизация сообщений, шаблоны HSM, Flows, webhooks. Используй когда нужно создать WhatsApp бота, настроить Cloud API, отправлять шаблоны."
---
# WhatsApp Bot / Business API — Production Guide 2026

## 1. Quick Start — Первое сообщение за 15 минут

### Что понадобится

- Meta Business Account (business.facebook.com)
- Номер телефона (не привязанный к WhatsApp/WA Business App)
- Meta App (developers.facebook.com)

### Шаг 1: Создание приложения (5 минут)

1. developers.facebook.com → My Apps → Create App
2. Тип: **Business** → указать Meta Business Account
3. Добавить продукт **WhatsApp** → Setup
4. Скопировать: **Phone Number ID**, **WhatsApp Business Account ID**, **Temporary Token**

### Шаг 2: Отправить тестовое сообщение (3 минуты)

```bash
curl -X POST 'https://graph.facebook.com/v21.0/PHONE_NUMBER_ID/messages' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "messaging_product": "whatsapp",
    "to": "971501234567",
    "type": "text",
    "text": {"body": "Привет из WhatsApp Cloud API!"}
  }'
```

**Ответ:**
```json
{
  "messaging_product": "whatsapp",
  "contacts": [{"wa_id": "971501234567"}],
  "messages": [{"id": "wamid.HBxxxxxx"}]
}
```

### Шаг 3: Настроить Webhook (7 минут)

1. App Dashboard → WhatsApp → Configuration
2. Callback URL: `https://yourdomain.com/webhook`
3. Verify Token: ваш секрет (например `my_wa_verify_2026`)
4. Подписка на события: `messages`, `message_template_status_update`

**Для локальной разработки:**
```bash
npx ngrok http 3000
# Получите URL: https://abc123.ngrok-free.app
```

---

## 2. Архитектура

### Cloud API vs On-Premise

| Параметр | Cloud API | On-Premise |
|----------|-----------|------------|
| Хостинг | Meta | Ваш сервер |
| Статус 2026 | **Активен** | **Закрыт (окт. 2025)** |
| Обновления | Автоматические | Нет |
| Throughput | 80 msg/sec (до 1000) | Зависит от сервера |
| Рекомендация | **Для всех** | Недоступен |

**Вывод:** С октября 2025 On-Premise API закрыт. Используйте только Cloud API.

### Схема обмена сообщениями

```
Клиент (WhatsApp) ←→ Meta Cloud API ←→ Webhook (ваш сервер)
                                        ↓
                                    Бизнес-логика
                                    (бот, CRM, БД)
```

### BSP (Business Solution Providers) — когда нужны

| Провайдер | Для кого | Дополнительно |
|-----------|----------|---------------|
| Meta Cloud API напрямую | Разработчики | Бесплатно, полный контроль |
| Twilio | Средний бизнес | SDK, поддержка 24/7 |
| 360dialog | Малый бизнес | Дешевле, простой интерфейс |
| MessageBird | Enterprise | Омниканальность |

---

## 3. Аутентификация и безопасность

### Temporary Token (24 часа)

Для тестирования. Генерируется в App Dashboard → WhatsApp → API Setup.

### Permanent Token (System User) — для production

1. Business Settings → Users → System Users → Add
2. Имя: `wa-bot-production`, роль: **Admin**
3. Назначить Assets → Apps → ваше приложение → Full Control
4. Generate Token → выбрать permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. Скопировать токен — он показывается **один раз**

### App Secret — верификация webhook

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(req, appSecret) {
  const signature = req.headers['x-hub-signature-256'];
  const body = JSON.stringify(req.body);
  const hash = 'sha256=' + crypto
    .createHmac('sha256', appSecret)
    .update(body)
    .digest('hex');
  return signature === hash;
}
```

### Верификация бизнеса в Meta

**Зачем:** Повышение tier-лимитов, доступ к 100K сообщений/день.

**Документы:** Свидетельство о регистрации, лицензия, счёт за коммунальные услуги.

**Срок проверки:** 1-5 рабочих дней.

**Business Settings → Security Center → Start Verification.**

---

## 4. Типы сообщений

### Текст (до 4096 символов)

```json
{"type": "text", "text": {"body": "Здравствуйте! Чем могу помочь?", "preview_url": true}}
```

### Изображение

```json
{"type": "image", "image": {"link": "https://cdn.example.com/burj-khalifa.jpg", "caption": "Burj Khalifa Tour"}}
```

### Видео (до 16 MB)

```json
{"type": "video", "video": {"link": "https://cdn.example.com/safari-promo.mp4", "caption": "Desert Safari"}}
```

### Документ (PDF ваучер)

```json
{"type": "document", "document": {"link": "https://cdn.example.com/voucher.pdf", "filename": "Safari_Voucher.pdf", "caption": "Ваш ваучер"}}
```

### Аудио (OGG/Opus, до 16 MB)

```json
{"type": "audio", "audio": {"link": "https://cdn.example.com/welcome.ogg"}}
```

### Стикер (WebP, до 100 KB static / 500 KB animated)

```json
{"type": "sticker", "sticker": {"link": "https://cdn.example.com/welcome.webp"}}
```

### Локация

```json
{"type": "location", "location": {"latitude": 25.0997, "longitude": 55.1724, "name": "Dubai Tours Office", "address": "Tecom, Barsha Heights"}}
```

### Контакт

```json
{"type": "contacts", "contacts": [{"name": {"formatted_name": "Dubai Tours Support"}, "phones": [{"phone": "+971501234567", "type": "WORK"}]}]}
```

### Реакция

```json
{"type": "reaction", "reaction": {"message_id": "wamid.HBxxx", "emoji": "\u2705"}}
```

---

## 5. Интерактивные элементы

### Reply Buttons (до 3 кнопок)

```json
{
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {"text": "Выберите категорию тура:"},
    "action": {
      "buttons": [
        {"type": "reply", "reply": {"id": "desert", "title": "Пустыня"}},
        {"type": "reply", "reply": {"id": "city", "title": "Город"}},
        {"type": "reply", "reply": {"id": "yacht", "title": "Яхта"}}
      ]
    }
  }
}
```

### List Message (до 10 секций, до 10 элементов каждая)

```json
{
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {"text": "Наши экскурсии по Дубаю:"},
    "action": {
      "button": "Посмотреть туры",
      "sections": [
        {
          "title": "Пустыня",
          "rows": [
            {"id": "safari_morning", "title": "Morning Safari", "description": "4ч, AED 199 — дюны, верблюды, завтрак"},
            {"id": "safari_sunset", "title": "Sunset Safari", "description": "5ч, AED 249 — BBQ ужин, шоу"}
          ]
        },
        {
          "title": "Город",
          "rows": [
            {"id": "burj", "title": "Burj Khalifa Tour", "description": "4ч, AED 149 — смотровая + Dubai Mall"},
            {"id": "old_dubai", "title": "Old Dubai", "description": "3ч, AED 79 — базар, история"}
          ]
        }
      ]
    }
  }
}
```

### CTA URL Button

```json
{
  "type": "interactive",
  "interactive": {
    "type": "cta_url",
    "body": {"text": "Забронируйте онлайн:"},
    "action": {"name": "cta_url", "parameters": {"display_text": "Открыть сайт", "url": "https://dubaitours.ae/book"}}
  }
}
```

### Product / Multi-Product Message

```json
{
  "type": "interactive",
  "interactive": {
    "type": "product_list",
    "header": {"type": "text", "text": "Популярные туры"},
    "body": {"text": "Выберите тур из каталога:"},
    "action": {
      "catalog_id": "YOUR_CATALOG_ID",
      "sections": [
        {"title": "Топ-экскурсии", "product_items": [
          {"product_retailer_id": "safari_sunset"},
          {"product_retailer_id": "burj_khalifa_tour"}
        ]}
      ]
    }
  }
}
```

---

## 6. Шаблоны (Template Messages / HSM)

### Когда нужны

- Первое сообщение клиенту (бизнес-инициированное)
- После истечения 24ч окна
- Массовые рассылки

### Категории (с июля 2025)

| Категория | Назначение | Цена UAE | Пример |
|-----------|-----------|----------|--------|
| **Marketing** | Промо, акции | ~$0.15-0.18 | "Скидка 20% на Desert Safari!" |
| **Utility** | Транзакции, уведомления | ~$0.08-0.12 | "Бронирование #123 подтверждено" |
| **Authentication** | OTP, верификация | ~$0.04-0.06 | "Ваш код: 123456" |

### Структура шаблона

```json
{
  "name": "booking_confirmed_ru",
  "category": "UTILITY",
  "language": "ru",
  "components": [
    {"type": "HEADER", "format": "TEXT", "text": "Бронирование подтверждено"},
    {"type": "BODY", "text": "Здравствуйте, {{1}}!\n\nТур: {{2}}\nДата: {{3}}\nСумма: {{4}} AED\n\nВаучер отправим за день до тура."},
    {"type": "FOOTER", "text": "Dubai Tours — лучшие цены"},
    {"type": "BUTTONS", "buttons": [
      {"type": "QUICK_REPLY", "text": "Детали"},
      {"type": "PHONE_NUMBER", "text": "Позвонить", "phone_number": "+971501234567"},
      {"type": "URL", "text": "Мои брони", "url": "https://dubaitours.ae/bookings/{{1}}"}
    ]}
  ]
}
```

### Создание через API

```bash
curl -X POST 'https://graph.facebook.com/v21.0/WABA_ID/message_templates' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "booking_confirmed_ru",
    "category": "UTILITY",
    "language": "ru",
    "components": [
      {"type": "BODY", "text": "Бронирование {{1}} подтверждено на {{2}}. Сумма: {{3}} AED."}
    ]
  }'
```

### Отправка шаблона

```python
import requests

def send_template(phone, tour, date, amount):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "booking_confirmed_ru",
            "language": {"code": "ru"},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": tour},
                    {"type": "text", "text": date},
                    {"type": "text", "text": str(amount)}
                ]
            }]
        }
    }
    return requests.post(url, headers=headers, json=payload).json()

# Использование
send_template("971501234567", "Desert Safari", "15.02.2026", 249)
```

### Утверждение шаблонов

- **Срок:** 2-24 часа (обычно минуты)
- **Частые причины отказа:** промо-контент в Utility, отсутствие opt-out в Marketing, спам-слова (FREE!!!, BUY NOW)
- **Лимит:** до 100 шаблонов на WABA
- **Языки:** создавайте на EN, RU, AR для аудитории ОАЭ

---

## 7. WhatsApp Flows — Интерактивные формы

### Что это

Многоэкранные формы внутри WhatsApp — клиент заполняет данные, не покидая чат.

### Элементы UI

- TextInput, TextArea, DatePicker, RadioButtons, CheckboxGroup
- Dropdown, OptIn, Image, EmbeddedLink, Footer

### Структура JSON

```json
{
  "version": "5.0",
  "screens": [
    {
      "id": "BOOKING_FORM",
      "title": "Бронирование тура",
      "data": {},
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          {"type": "TextInput", "name": "full_name", "label": "Ваше имя", "required": true},
          {"type": "DatePicker", "name": "tour_date", "label": "Дата тура", "required": true},
          {"type": "Dropdown", "name": "guests", "label": "Кол-во гостей", "data-source": [
            {"id": "1", "title": "1"}, {"id": "2", "title": "2"},
            {"id": "3", "title": "3"}, {"id": "4", "title": "4+"}
          ]},
          {"type": "RadioButtonsGroup", "name": "tour_type", "label": "Тип тура", "data-source": [
            {"id": "morning", "title": "Morning Safari (AED 199)"},
            {"id": "sunset", "title": "Sunset Safari (AED 249)"},
            {"id": "night", "title": "Night Safari (AED 299)"}
          ]},
          {"type": "Footer", "label": "Забронировать", "on-click-action": {
            "name": "complete",
            "payload": {"full_name": "${form.full_name}", "tour_date": "${form.tour_date}", "guests": "${form.guests}", "tour_type": "${form.tour_type}"}
          }}
        ]
      }
    }
  ]
}
```

### Отправка Flow

```json
{
  "type": "interactive",
  "interactive": {
    "type": "flow",
    "body": {"text": "Заполните форму бронирования:"},
    "action": {
      "name": "flow",
      "parameters": {
        "flow_message_version": "3",
        "flow_id": "FLOW_ID",
        "flow_cta": "Забронировать",
        "mode": "published"
      }
    }
  }
}
```

### Endpoint для обработки данных

Flow может вызывать ваш endpoint для динамических данных (доступные даты, расчёт цены).

---

## 8. Webhooks — Получение и обработка сообщений

### Verification (GET)

```javascript
const express = require('express');
const app = express();
app.use(express.json());

const VERIFY_TOKEN = process.env.WA_VERIFY_TOKEN;

app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === VERIFY_TOKEN) {
    res.status(200).send(challenge);
  } else {
    res.sendStatus(403);
  }
});
```

### Обработка входящих сообщений (POST)

```javascript
app.post('/webhook', (req, res) => {
  res.sendStatus(200); // СРАЗУ ответить 200 (до обработки!)

  const body = req.body;
  if (body.object !== 'whatsapp_business_account') return;

  for (const entry of body.entry) {
    const changes = entry.changes;
    for (const change of changes) {
      const value = change.value;

      // Входящие сообщения
      if (value.messages) {
        for (const msg of value.messages) {
          handleIncomingMessage(msg, value.metadata.phone_number_id);
        }
      }

      // Статусы доставки
      if (value.statuses) {
        for (const status of value.statuses) {
          handleStatus(status); // sent → delivered → read → failed
        }
      }
    }
  }
});

async function handleIncomingMessage(msg, phoneNumberId) {
  const from = msg.from;
  const type = msg.type;

  switch (type) {
    case 'text':
      await routeTextMessage(from, msg.text.body, phoneNumberId);
      break;
    case 'interactive':
      // Нажатие кнопки или выбор из списка
      const reply = msg.interactive.button_reply || msg.interactive.list_reply;
      await handleInteractiveReply(from, reply.id, phoneNumberId);
      break;
    case 'image':
    case 'document':
    case 'audio':
    case 'video':
      await handleMedia(from, msg[type], phoneNumberId);
      break;
    case 'location':
      await handleLocation(from, msg.location, phoneNumberId);
      break;
  }
}
```

### Подпись X-Hub-Signature-256

```javascript
const crypto = require('crypto');

function verifySignature(rawBody, signature, appSecret) {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', appSecret)
    .update(rawBody)
    .digest('hex');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}

// Middleware
app.use('/webhook', (req, res, next) => {
  const sig = req.headers['x-hub-signature-256'];
  if (!sig || !verifySignature(JSON.stringify(req.body), sig, APP_SECRET)) {
    return res.sendStatus(401);
  }
  next();
});
```

---

## 9. Состояния диалога (FSM)

### Простой конечный автомат

```javascript
// Redis / Map для хранения состояния
const sessions = new Map();

function getSession(userId) {
  return sessions.get(userId) || { step: 'MENU', data: {} };
}

function setSession(userId, session) {
  sessions.set(userId, { ...session, updatedAt: Date.now() });
}

async function routeTextMessage(from, text, phoneId) {
  const session = getSession(from);

  switch (session.step) {
    case 'MENU':
      await sendTourCategories(from, phoneId); // Reply Buttons: Пустыня, Город, Яхта
      setSession(from, { step: 'CHOOSE_CATEGORY', data: {} });
      break;

    case 'AWAITING_NAME':
      session.data.name = text;
      await sendMessage(from, phoneId, `Спасибо, ${text}! Выберите дату:`);
      setSession(from, { ...session, step: 'AWAITING_DATE' });
      break;

    case 'AWAITING_DATE':
      session.data.date = text;
      await sendBookingSummary(from, phoneId, session.data);
      setSession(from, { ...session, step: 'CONFIRM_BOOKING' });
      break;

    default:
      await sendMainMenu(from, phoneId);
      setSession(from, { step: 'MENU', data: {} });
  }
}
```

### Очистка старых сессий

```javascript
// Удалять сессии старше 24 часов
setInterval(() => {
  const cutoff = Date.now() - 24 * 60 * 60 * 1000;
  for (const [userId, session] of sessions) {
    if (session.updatedAt < cutoff) sessions.delete(userId);
  }
}, 60 * 60 * 1000); // каждый час
```

---

## 10. Каталог продуктов (Commerce API)

### Создание каталога

1. Meta Commerce Manager → Create Catalog → тип: **Other**
2. Добавить товары/услуги (туры) вручную или через Data Feed
3. Привязать каталог к WABA: Business Settings → WhatsApp Accounts → Settings → Cart

### Отправка одного продукта

```json
{
  "type": "interactive",
  "interactive": {
    "type": "product",
    "body": {"text": "Рекомендуем:"},
    "action": {"catalog_id": "CATALOG_ID", "product_retailer_id": "safari_sunset"}
  }
}
```

### Отправка мультипродуктового сообщения

```json
{
  "type": "interactive",
  "interactive": {
    "type": "product_list",
    "header": {"type": "text", "text": "Экскурсии по Дубаю"},
    "body": {"text": "Выберите тур:"},
    "action": {
      "catalog_id": "CATALOG_ID",
      "sections": [
        {"title": "Пустыня", "product_items": [
          {"product_retailer_id": "safari_morning"},
          {"product_retailer_id": "safari_sunset"}
        ]},
        {"title": "Город", "product_items": [
          {"product_retailer_id": "burj_khalifa"},
          {"product_retailer_id": "old_dubai"}
        ]}
      ]
    }
  }
}
```

---

## 11. Ценообразование 2025-2026

### Ключевые изменения (1 июля 2025)

**Было:** Оплата за 24-часовую беседу (conversation-based).
**Стало:** Оплата **за каждое template-сообщение** (per-message).

### Стоимость для ОАЭ (ориентировочно)

| Категория | Цена за сообщение | Когда |
|-----------|-------------------|-------|
| Marketing | $0.15-0.18 | Промо, акции |
| Utility | $0.08-0.12 | Подтверждения, уведомления |
| Authentication | $0.04-0.06 | OTP, верификация |
| Service | **$0 (бесплатно)** | Ответ в 24ч окне |

### Бесплатные окна

**24-часовое окно (Customer Service Window):**
- Клиент написал первым → все ваши ответы бесплатны 24 часа
- Каждое новое сообщение клиента = новые 24 часа
- Количество ваших сообщений не ограничено

**72-часовое окно (Click-to-WhatsApp Ads):**
- Клиент пришёл из рекламы Facebook/Instagram → 72 часа бесплатно
- Все сообщения бесплатны, включая Template Messages

**Utility в активном окне — бесплатно:**
Если Utility-шаблон отправлен внутри активного 24ч/72ч окна, он **бесплатен**.

### Объёмные скидки

Автоматические скидки при росте объёма Utility и Authentication за месяц. Чем больше отправляете — тем дешевле.

### Стратегия экономии для туризма

1. **Стимулируйте ответы** — задавайте вопросы, чтобы держать 24ч окно открытым
2. **Utility вместо Marketing** — подтверждения вместо промо (экономия 40-50%)
3. **Click-to-WhatsApp реклама** — 72ч бесплатной переписки
4. **Группируйте информацию** — одно сообщение вместо трёх

---

## 12. Rate Limits и качество

### Tier-система 2026

| Tier | Лимит уникальных получателей / 24ч | Как получить |
|------|-------------------------------------|-------------|
| Начальный | 250 | По умолчанию (новый аккаунт) |
| Стандарт | **100,000** | Верификация бизнеса |
| Unlimited | Без лимитов | Enterprise-партнёры Meta |

**Изменение 2026:** Meta убирает промежуточные уровни 1K и 10K. После верификации бизнеса — сразу 100K.

### Portfolio-Level Limits (с окт. 2025)

Лимиты теперь на уровне **бизнес-портфолио**, а не отдельного номера. Все номера аккаунта делят общий лимит.

### Throughput (пропускная способность)

- По умолчанию: **80 сообщений/секунду**
- После автоматического апгрейда: до **1000 сообщений/секунду**

### Quality Rating

- **Green:** Отличное качество → лимиты растут
- **Yellow:** Среднее → лимиты не меняются
- **Red:** Низкое → риск блокировки, отправка ограничена

**Факторы:** процент доставки, прочтения, жалобы на спам, блокировки.

### Коды ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| 131026 | Message undeliverable | Номер не в WhatsApp или заблокировал вас |
| 131047 | Re-engagement message | 24ч окно закрыто, нужен Template |
| 131051 | Unsupported message type | Проверьте тип сообщения |
| 130429 | Rate limit hit | Exponential backoff, подождите |
| 132000 | Template param count | Неверное количество переменных |
| 132012 | Template not found | Проверьте имя и язык шаблона |
| 133010 | Phone not registered | Номер не зарегистрирован в Cloud API |
| 368 | Temporarily blocked | Quality rating слишком низкий |

---

## 13. Примеры для туризма ОАЭ

### Пример 1: Бот подтверждения бронирования

```javascript
async function confirmBooking(booking) {
  // 1. Отправить Utility Template с подтверждением
  await sendTemplate(booking.phone, 'booking_confirmed_ru', [
    booking.customerName,
    booking.tourName,
    booking.date,
    String(booking.amount)
  ]);

  // 2. За 24ч до тура — напоминание
  scheduleAt(booking.date - 24*60*60*1000, async () => {
    await sendTemplate(booking.phone, 'tour_reminder_ru', [
      booking.tourName,
      booking.time,
      booking.driverPhone
    ]);
  });

  // 3. После тура — запрос отзыва (Marketing)
  scheduleAt(booking.date + 6*60*60*1000, async () => {
    await sendTemplate(booking.phone, 'request_review_ru', [
      booking.tourName,
      'https://g.page/dubaitours/review'
    ]);
  });
}
```

### Пример 2: Каталог экскурсий через интерактивный список

```javascript
async function sendTourCatalog(to, phoneId) {
  await sendInteractiveList(to, phoneId, {
    body: "Экскурсии по Дубаю и ОАЭ. Выберите категорию:",
    buttonText: "Каталог туров",
    sections: [
      {title: "Пустыня", rows: [
        {id: "safari_m", title: "Morning Safari", description: "4ч, 199 AED"},
        {id: "safari_s", title: "Sunset Safari", description: "5ч, 249 AED"},
      ]},
      {title: "Город", rows: [
        {id: "burj", title: "Burj Khalifa", description: "4ч, 149 AED"},
        {id: "marina", title: "Dubai Marina", description: "3ч, 99 AED"},
      ]},
      {title: "Яхты", rows: [
        {id: "yacht_2h", title: "Sunset Cruise", description: "2ч, 349 AED"},
        {id: "yacht_4h", title: "Dinner Cruise", description: "4ч, 449 AED"},
      ]},
      {title: "Авто", rows: [
        {id: "car_eco", title: "Аренда эконом", description: "от 150 AED/день"},
        {id: "car_lux", title: "Аренда люкс", description: "от 800 AED/день"},
      ]}
    ]
  });
}
```

### Пример 3: Мультиязычность (RU/EN)

```javascript
const i18n = {
  welcome: {
    ru: "Добро пожаловать! Выберите язык:",
    en: "Welcome! Choose your language:"
  },
  choose_tour: {
    ru: "Выберите категорию тура:",
    en: "Choose tour category:"
  },
  booking_confirmed: {
    ru: "Бронирование подтверждено! Тур: {{tour}}, Дата: {{date}}",
    en: "Booking confirmed! Tour: {{tour}}, Date: {{date}}"
  }
};

function t(key, lang, params = {}) {
  let text = i18n[key]?.[lang] || i18n[key]?.en || key;
  for (const [k, v] of Object.entries(params)) {
    text = text.replace(`{{${k}}}`, v);
  }
  return text;
}

// Определение языка по первому сообщению или по номеру телефона
function detectLanguage(phone, text) {
  if (/^(7|77|375|996|998|992|993)/.test(phone)) return 'ru'; // СНГ
  if (/[а-яА-ЯёЁ]/.test(text)) return 'ru';
  return 'en';
}
```

---

## 14. Деплой

### Node.js + Express (рекомендуется)

```bash
# package.json
npm init -y
npm install express dotenv axios

# .env
WA_PHONE_NUMBER_ID=123456
WA_ACCESS_TOKEN=your_permanent_token
WA_VERIFY_TOKEN=my_wa_verify_2026
WA_APP_SECRET=your_app_secret
PORT=3000
```

### Python + FastAPI

```python
from fastapi import FastAPI, Request, Response
import httpx, os

app = FastAPI()
TOKEN = os.getenv("WA_ACCESS_TOKEN")
PHONE_ID = os.getenv("WA_PHONE_NUMBER_ID")

@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == os.getenv("WA_VERIFY_TOKEN"):
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    # Обработка аналогично Node.js примеру
    return {"status": "ok"}

async def send_message(to: str, text: str):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    async with httpx.AsyncClient() as client:
        return await client.post(url, headers=headers, json=payload)
```

### Serverless (Vercel / Railway)

```javascript
// api/webhook.js (Vercel)
export default async function handler(req, res) {
  if (req.method === 'GET') {
    // Verification
    const token = req.query['hub.verify_token'];
    if (token === process.env.WA_VERIFY_TOKEN) {
      return res.status(200).send(req.query['hub.challenge']);
    }
    return res.status(403).end();
  }

  if (req.method === 'POST') {
    res.status(200).end(); // Сразу 200
    // Обработка в background
    await processWebhook(req.body);
  }
}
```

---

## 15. Интеграции

### Google Sheets (через Apps Script)

```javascript
// Apps Script — запись заявок в таблицу
function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const sheet = SpreadsheetApp.openById('SHEET_ID').getActiveSheet();
  sheet.appendRow([new Date(), data.phone, data.name, data.tour, data.date, data.amount]);
  return ContentService.createTextOutput('ok');
}
```

### Notion (через API)

```javascript
const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_TOKEN });

async function addBookingToNotion(booking) {
  await notion.pages.create({
    parent: { database_id: 'DATABASE_ID' },
    properties: {
      'Name': { title: [{ text: { content: booking.name } }] },
      'Tour': { select: { name: booking.tour } },
      'Date': { date: { start: booking.date } },
      'Phone': { phone_number: booking.phone },
      'Amount': { number: booking.amount },
      'Status': { select: { name: 'Confirmed' } }
    }
  });
}
```

### Make.com (Webhook)

1. Создать сценарий: **Webhook** → Custom webhook
2. Скопировать URL Make.com webhook
3. Из вашего бота → `POST` на URL Make.com при событиях (новая заявка, оплата)
4. Make.com → Google Sheets / Notion / Email / Telegram

---

## 16. Библиотеки и SDK

### Официальные / рекомендуемые

| Библиотека | Язык | Тип | Описание |
|-----------|------|-----|----------|
| Meta WhatsApp Business SDK | Node.js | Официальный | `npm install whatsapp-business-api-sdk` |
| requests / httpx | Python | HTTP | Прямые вызовы Cloud API |
| axios / node-fetch | Node.js | HTTP | Прямые вызовы Cloud API |

### Неофициальные (альтернативные)

| Библиотека | Описание | Статус |
|-----------|----------|--------|
| whatsapp-web.js | Работа через WhatsApp Web (puppeteer) | Неофициальный, риск бана |
| Baileys | Lightweight WhatsApp Web API | Неофициальный, для экспериментов |
| venom-bot | Node.js WA Web библиотека | Неофициальный |

**Рекомендация:** Для production ВСЕГДА используйте официальный Cloud API. Неофициальные библиотеки нарушают ToS и рискуют баном номера.

---

**Версия:** 2.0
**Дата:** 12.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль — экскурсии/билеты, Марсель — авто/трансферы, Муфамад — яхты)

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
