---
name: facebook-messenger-bot-spravochnik
description: Production-ready руководство по Facebook Messenger Platform для создания ботов. Send API, шаблоны, кнопки, Handover Protocol, платежи. Используй когда нужно создать Facebook Messenger бота или автоматизировать переписку.
---

# Facebook Messenger Bot — Справочник

## 1. Quick Start — Первый бот за 15 минут

### Шаг 1: Создание Meta App

1. Перейди на [developers.facebook.com](https://developers.facebook.com)
2. **My Apps** → **Create App** → тип **Business**
3. Укажи название (например, `Dubai Tours Bot`) и email
4. В дашборде приложения: **Add Product** → **Messenger** → **Set Up**

### Шаг 2: Подключение Facebook Page

1. В разделе **Access Tokens** выбери свою Facebook Page (или создай новую)
2. Нажми **Generate Token** — скопируй **Page Access Token**
3. Сохрани токен — он понадобится для отправки сообщений

### Шаг 3: Настройка Webhook

```bash
# Минимальный сервер (Node.js)
npm init -y && npm install express

# server.js
const express = require('express');
const app = express();
app.use(express.json());

const VERIFY_TOKEN = 'my_verify_token_123';
const PAGE_ACCESS_TOKEN = 'EAAxxxxxxxxx...';

// Верификация webhook
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

// Получение сообщений
app.post('/webhook', (req, res) => {
  const body = req.body;
  if (body.object === 'page') {
    body.entry.forEach(entry => {
      const event = entry.messaging[0];
      const senderId = event.sender.id;
      if (event.message) {
        console.log(`Message from ${senderId}: ${event.message.text}`);
        // Здесь обработка и ответ
      }
    });
    res.status(200).send('EVENT_RECEIVED');
  } else {
    res.sendStatus(404);
  }
});

app.listen(3000, () => console.log('Webhook running on :3000'));
```

4. Разверни сервер (ngrok для теста: `ngrok http 3000`)
5. В Meta App Dashboard: **Webhooks** → **Edit Callback URL**
   - URL: `https://your-domain.com/webhook`
   - Verify Token: `my_verify_token_123`
6. Подпишись на события: `messages`, `messaging_postbacks`

### Шаг 4: Отправка первого сообщения

```bash
curl -X POST "https://graph.facebook.com/v22.0/me/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": {"id": "USER_PSID"},
    "messaging_type": "RESPONSE",
    "message": {"text": "Добро пожаловать в Dubai Tours!"}
  }' \
  -G --data-urlencode "access_token=PAGE_ACCESS_TOKEN"
```

---

## 2. Архитектура Messenger Platform

### Компоненты системы

```
Пользователь ←→ Messenger App ←→ Meta Servers ←→ Webhook (твой сервер)
                                        ↑
                                   Send API (POST)
                                   Graph API v22.0
```

### Основные API

| API | Назначение | Метод |
|-----|-----------|-------|
| **Send API** | Отправка сообщений | POST `/me/messages` |
| **Messenger Profile** | Настройка бота (меню, приветствие) | POST `/me/messenger_profile` |
| **User Profile** | Получение данных пользователя | GET `/{PSID}` |
| **Broadcast API** (deprecated) | Массовая рассылка | Заменён на Recurring Notifications |

### Идентификаторы

- **PSID** (Page-Scoped ID) — уникальный ID пользователя для конкретной Page. Разные Pages видят разные PSID одного человека
- **ASID** (App-Scoped ID) — ID в контексте приложения
- **App ID** — идентификатор твоего Meta App
- **Page ID** — идентификатор Facebook Page

---

## 3. Аутентификация

### Page Access Token

```bash
# Получение долгоживущего токена (60 дней)
GET https://graph.facebook.com/v22.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={APP_ID}&
  client_secret={APP_SECRET}&
  fb_exchange_token={SHORT_LIVED_TOKEN}

# Получение бессрочного Page Token
GET https://graph.facebook.com/v22.0/me/accounts?access_token={LONG_LIVED_USER_TOKEN}
```

### Необходимые permissions

| Permission | Назначение |
|-----------|-----------|
| `pages_messaging` | Отправка/получение сообщений |
| `pages_manage_metadata` | Подписка на webhook events |
| `pages_read_engagement` | Чтение данных Page |
| `pages_show_list` | Список Pages аккаунта |

### App Secret

- Используется для верификации webhook (X-Hub-Signature-256)
- Находится в **App Dashboard** → **Settings** → **Basic**
- Никогда не храни в коде — используй переменные окружения

---

## 4. Получение сообщений (Webhooks)

### Webhook Events

| Event | Описание | Поле |
|-------|---------|------|
| `messages` | Текст, вложения, quick reply | `event.message` |
| `messaging_postbacks` | Нажатие кнопки/меню | `event.postback` |
| `messaging_referrals` | Переход по m.me ссылке | `event.referral` |
| `messaging_optins` | Подписка (Send to Messenger) | `event.optin` |
| `message_deliveries` | Подтверждение доставки | `event.delivery` |
| `message_reads` | Сообщение прочитано | `event.read` |
| `messaging_handovers` | Передача диалога | `event.pass_thread_control` |

### Структура входящего сообщения

```json
{
  "object": "page",
  "entry": [{
    "id": "PAGE_ID",
    "time": 1708900000000,
    "messaging": [{
      "sender": {"id": "USER_PSID"},
      "recipient": {"id": "PAGE_ID"},
      "timestamp": 1708900000000,
      "message": {
        "mid": "m_xxx",
        "text": "Хочу экскурсию по Дубаю",
        "nlp": {
          "intents": [{"name": "book_tour", "confidence": 0.92}],
          "entities": {"wit$location:location": [{"value": "Дубай"}]}
        }
      }
    }]
  }]
}
```

### Верификация подписи (X-Hub-Signature-256)

```javascript
const crypto = require('crypto');

function verifySignature(req, appSecret) {
  const signature = req.headers['x-hub-signature-256'];
  if (!signature) return false;

  const expected = 'sha256=' + crypto
    .createHmac('sha256', appSecret)
    .update(req.rawBody)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}
```

### Retry Policy

- Meta повторяет доставку webhook при ошибке (не 200 OK)
- Повторы: через 1 мин, 5 мин, 30 мин, затем раз в час до 24 часов
- После 24ч неуспешных попыток webhook отключается
- Всегда возвращай `200 OK` как можно быстрее, обрабатывай асинхронно

---

## 5. Отправка сообщений (Send API)

### Базовый запрос

```
POST https://graph.facebook.com/v22.0/me/messages?access_token={TOKEN}
Content-Type: application/json
```

### messaging_type — обязательное поле

| Тип | Когда использовать |
|-----|-------------------|
| `RESPONSE` | Ответ на сообщение пользователя (в пределах 24ч) |
| `UPDATE` | Проактивное обновление (в пределах 24ч) |
| `MESSAGE_TAG` | Сообщение вне 24ч окна (с тегом) |

### Sender Actions — индикаторы

```json
{
  "recipient": {"id": "USER_PSID"},
  "sender_action": "typing_on"
}
```

| Action | Эффект |
|--------|--------|
| `typing_on` | Показать "печатает..." (20 сек) |
| `typing_off` | Убрать индикатор |
| `mark_seen` | Отметить как прочитанное |

### Отправка вложений

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "image",
      "payload": {
        "url": "https://example.com/dubai-tour.jpg",
        "is_reusable": true
      }
    }
  }
}
```

Типы вложений: `image`, `audio`, `video`, `file`.

---

## 6. Шаблоны (Templates)

### Generic Template — карусель карточек

До 10 элементов, горизонтальная прокрутка. Идеально для каталога экскурсий.

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [
          {
            "title": "Desert Safari Dubai",
            "subtitle": "Джип-сафари, BBQ-ужин, танец живота. 180 AED",
            "image_url": "https://example.com/safari.jpg",
            "default_action": {
              "type": "web_url",
              "url": "https://example.com/safari"
            },
            "buttons": [
              {
                "type": "postback",
                "title": "Забронировать",
                "payload": "BOOK_SAFARI"
              },
              {
                "type": "phone_number",
                "title": "Позвонить",
                "payload": "+971501234567"
              }
            ]
          },
          {
            "title": "Burj Khalifa At The Top",
            "subtitle": "Смотровая площадка 124-125 этаж. 260 AED",
            "image_url": "https://example.com/burj.jpg",
            "buttons": [
              {
                "type": "postback",
                "title": "Забронировать",
                "payload": "BOOK_BURJ"
              }
            ]
          }
        ]
      }
    }
  }
}
```

### Button Template — текст + кнопки

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "button",
        "text": "Чем могу помочь?",
        "buttons": [
          {"type": "postback", "title": "Каталог экскурсий", "payload": "CATALOG"},
          {"type": "postback", "title": "Мои бронирования", "payload": "MY_BOOKINGS"},
          {"type": "web_url", "title": "Наш сайт", "url": "https://example.com"}
        ]
      }
    }
  }
}
```

### Receipt Template — чек бронирования

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "receipt",
        "recipient_name": "Aleksei Ivanov",
        "order_number": "DXB-2026-0142",
        "currency": "AED",
        "payment_method": "Cash on arrival",
        "order_url": "https://example.com/order/142",
        "summary": {
          "subtotal": 1040,
          "shipping_cost": 0,
          "total_tax": 52,
          "total_cost": 1092
        },
        "elements": [
          {
            "title": "Burj Khalifa At The Top",
            "subtitle": "4 билета x 260 AED",
            "quantity": 4,
            "price": 1040,
            "currency": "AED",
            "image_url": "https://example.com/burj-ticket.jpg"
          }
        ],
        "address": {
          "street_1": "1 Sheikh Mohammed bin Rashid Blvd",
          "city": "Dubai",
          "state": "Dubai",
          "postal_code": "00000",
          "country": "AE"
        }
      }
    }
  }
}
```

### Media Template — медиа с кнопкой

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "media",
        "elements": [{
          "media_type": "video",
          "url": "https://www.facebook.com/video_url",
          "buttons": [
            {"type": "web_url", "title": "Подробнее", "url": "https://example.com"}
          ]
        }]
      }
    }
  }
}
```

### Airline Boarding Pass Template

Ключевая фича для туристического бизнеса — отправка посадочного талона прямо в Messenger.

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "airline_boardingpass",
        "intro_message": "Ваш посадочный талон готов!",
        "locale": "ru_RU",
        "boarding_pass": [{
          "passenger_name": "IVANOV/ALEKSEI",
          "pnr_number": "ABC123",
          "seat": "12A",
          "logo_image_url": "https://example.com/airline-logo.png",
          "header_image_url": "https://example.com/header.jpg",
          "qr_code": "M1IVANOV/ALEKSEI  ABC123 DXBSVO...",
          "above_bar_code_image_url": "https://example.com/barcode.png",
          "auxiliary_fields": [
            {"label": "Terminal", "value": "3"},
            {"label": "Gate", "value": "D42"}
          ],
          "secondary_fields": [
            {"label": "Boarding", "value": "10:30"},
            {"label": "Departure", "value": "11:15"}
          ],
          "flight_info": {
            "flight_number": "SU 521",
            "departure_airport": {
              "airport_code": "DXB",
              "city": "Dubai",
              "terminal": "3",
              "gate": "D42"
            },
            "arrival_airport": {
              "airport_code": "SVO",
              "city": "Moscow",
              "terminal": "D"
            },
            "flight_schedule": {
              "departure_time": "2026-03-15T11:15",
              "arrival_time": "2026-03-15T16:45"
            }
          }
        }]
      }
    }
  }
}
```

### Airline Itinerary Template

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "airline_itinerary",
        "intro_message": "Маршрут вашего путешествия",
        "locale": "ru_RU",
        "pnr_number": "ABC123",
        "passenger_info": [{
          "passenger_id": "p001",
          "name": "Aleksei Ivanov"
        }],
        "flight_info": [{
          "connection_id": "c001",
          "segment_id": "s001",
          "flight_number": "SU 521",
          "aircraft_type": "Boeing 777-300ER",
          "departure_airport": {"airport_code": "SVO", "city": "Moscow"},
          "arrival_airport": {"airport_code": "DXB", "city": "Dubai"},
          "flight_schedule": {
            "departure_time": "2026-03-15T06:30",
            "arrival_time": "2026-03-15T13:45"
          },
          "travel_class": "business"
        }],
        "passenger_segment_info": [{
          "segment_id": "s001",
          "passenger_id": "p001",
          "seat": "2A",
          "seat_type": "Business"
        }],
        "total_price": 3200,
        "currency": "AED"
      }
    }
  }
}
```

---

## 7. Кнопки (Buttons)

| Тип | Назначение | Пример |
|-----|-----------|--------|
| `web_url` | Открыть URL | `{"type":"web_url","url":"https://...","title":"Сайт"}` |
| `postback` | Отправить payload боту | `{"type":"postback","title":"Меню","payload":"MAIN_MENU"}` |
| `phone_number` | Позвонить | `{"type":"phone_number","title":"Звонок","payload":"+971501234567"}` |
| `log_in` | Вход через Account Linking | `{"type":"account_link","url":"https://auth.example.com"}` |
| `log_out` | Выход | `{"type":"account_unlink"}` |

### URL Button с WebView

```json
{
  "type": "web_url",
  "url": "https://example.com/booking",
  "title": "Оформить заказ",
  "webview_height_ratio": "tall",
  "messenger_extensions": true,
  "fallback_url": "https://example.com/booking"
}
```

`webview_height_ratio`: `compact` (50%), `tall` (75%), `full` (100%).

---

## 8. Quick Replies — быстрые ответы

До 13 Quick Replies. Исчезают после нажатия.

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "text": "Какой тип экскурсии вас интересует?",
    "quick_replies": [
      {
        "content_type": "text",
        "title": "Городские туры",
        "payload": "CITY_TOURS",
        "image_url": "https://example.com/city-icon.png"
      },
      {
        "content_type": "text",
        "title": "Джип-сафари",
        "payload": "SAFARI"
      },
      {
        "content_type": "text",
        "title": "Яхты",
        "payload": "YACHTS"
      },
      {
        "content_type": "user_email"
      },
      {
        "content_type": "user_phone_number"
      }
    ]
  }
}
```

Специальные типы: `user_email`, `user_phone_number` — запрашивают контакт с согласия пользователя.

---

## 9. Persistent Menu — постоянное меню

До 3 уровней вложенности, до 3 элементов на уровне.

```json
POST /me/messenger_profile?access_token={TOKEN}

{
  "persistent_menu": [
    {
      "locale": "default",
      "composer_input_disabled": false,
      "call_to_actions": [
        {
          "type": "postback",
          "title": "Каталог экскурсий",
          "payload": "CATALOG"
        },
        {
          "type": "nested",
          "title": "Услуги",
          "call_to_actions": [
            {"type": "postback", "title": "Аренда авто", "payload": "CAR_RENTAL"},
            {"type": "postback", "title": "Яхты", "payload": "YACHTS"},
            {"type": "postback", "title": "Трансфер", "payload": "TRANSFER"}
          ]
        },
        {
          "type": "web_url",
          "title": "Контакты",
          "url": "https://example.com/contacts"
        }
      ]
    },
    {
      "locale": "ru_RU",
      "composer_input_disabled": false,
      "call_to_actions": [
        {"type": "postback", "title": "Экскурсии", "payload": "CATALOG"},
        {"type": "postback", "title": "Помощь", "payload": "HELP"}
      ]
    }
  ]
}
```

- `composer_input_disabled: true` — скрывает поле ввода (только кнопки)
- Поддержка локализации по `locale`

---

## 10. Get Started — приветственный экран

```json
POST /me/messenger_profile?access_token={TOKEN}

{
  "get_started": {
    "payload": "GET_STARTED"
  }
}
```

Приветственный текст (Greeting):

```json
{
  "greeting": [
    {
      "locale": "default",
      "text": "Welcome to Dubai Tours! We offer the best excursions in the UAE."
    },
    {
      "locale": "ru_RU",
      "text": "Добро пожаловать в Dubai Tours! Лучшие экскурсии по ОАЭ."
    }
  ]
}
```

Переменные подстановки: `{{user_first_name}}`, `{{user_last_name}}`, `{{user_full_name}}`.

---

## 11. Ice Breakers — часто задаваемые вопросы

Кликабельные вопросы на стартовом экране (до 4 штук).

```json
POST /me/messenger_profile?access_token={TOKEN}

{
  "ice_breakers": [
    {
      "question": "Какие экскурсии есть в Дубае?",
      "payload": "CATALOG"
    },
    {
      "question": "Сколько стоит сафари?",
      "payload": "SAFARI_PRICE"
    },
    {
      "question": "Как арендовать яхту?",
      "payload": "YACHT_INFO"
    },
    {
      "question": "Контакты и офис",
      "payload": "CONTACTS"
    }
  ]
}
```

---

## 12. Handover Protocol — передача живому оператору

Позволяет нескольким приложениям обрабатывать диалоги одной Page.

### Роли

- **Primary Receiver** — основное приложение (обычно бот), получает все входящие
- **Secondary Receiver** — резервное приложение (обычно live chat)

### Передача управления

```json
// Бот передаёт диалог оператору (Secondary Receiver)
POST /me/pass_thread_control?access_token={TOKEN}

{
  "recipient": {"id": "USER_PSID"},
  "target_app_id": 123456789,
  "metadata": "Клиент запросил живого оператора. Тема: бронирование яхты."
}
```

```json
// Оператор возвращает диалог боту (Primary Receiver)
POST /me/take_thread_control?access_token={TOKEN}

{
  "recipient": {"id": "USER_PSID"},
  "metadata": "Вопрос решён, возвращаю боту."
}
```

### Webhook события Handover

| Event | Описание |
|-------|---------|
| `pass_thread_control` | Управление передано |
| `take_thread_control` | Управление забрано |
| `request_thread_control` | Запрос на получение управления |
| `app_roles` | Изменение ролей |

### Настройка

1. Meta App Dashboard → Messenger Settings → Handover Protocol
2. Назначь Primary и Secondary Receiver
3. Подпишись на `messaging_handovers` webhook event

---

## 13. One-Time Notification (OTN)

Позволяет отправить одно сообщение вне 24ч окна с согласия пользователя.

### Запрос разрешения

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "one_time_notif_req",
        "title": "Уведомить о скидке на Desert Safari?",
        "payload": "SAFARI_DISCOUNT_NOTIFY"
      }
    }
  }
}
```

### Получение токена (webhook optin)

```json
{
  "sender": {"id": "USER_PSID"},
  "recipient": {"id": "PAGE_ID"},
  "optin": {
    "type": "one_time_notif_req",
    "payload": "SAFARI_DISCOUNT_NOTIFY",
    "one_time_notif_token": "TOKEN_FROM_OPTIN"
  }
}
```

### Отправка уведомления

```json
{
  "recipient": {
    "one_time_notif_token": "TOKEN_FROM_OPTIN"
  },
  "message": {
    "text": "Скидка 25% на Desert Safari! Только сегодня: 135 AED вместо 180 AED. Напишите 'Бронь' для оформления."
  }
}
```

Ограничения: токен одноразовый, срок жизни до 1 года.

---

## 14. Recurring Notifications — регулярные уведомления

Подписка на периодические уведомления (заменяет старый Broadcast API).

### Запрос подписки

```json
{
  "recipient": {"id": "USER_PSID"},
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "notification_messages",
        "title": "Еженедельные спецпредложения Dubai Tours",
        "image_url": "https://example.com/promo.jpg",
        "payload": "WEEKLY_DEALS",
        "notification_messages_frequency": "WEEKLY",
        "notification_messages_reoptin": "ENABLED"
      }
    }
  }
}
```

### Частоты

| Значение | Описание |
|----------|---------|
| `DAILY` | Ежедневно |
| `WEEKLY` | Еженедельно |
| `MONTHLY` | Ежемесячно |

### Отправка по подписке

```json
{
  "recipient": {
    "notification_messages_token": "TOKEN_FROM_SUBSCRIPTION"
  },
  "message": {
    "text": "Новая экскурсия: Abu Dhabi Grand Mosque + Louvre за 250 AED!"
  }
}
```

Пользователь может отписаться в любой момент. Токен обновляется после каждого использования.

---

## 15. Webhooks — детали настройки

### Полная настройка

```
POST /me/subscribed_apps?access_token={TOKEN}

{
  "subscribed_fields": [
    "messages",
    "messaging_postbacks",
    "messaging_optins",
    "messaging_referrals",
    "messaging_handovers",
    "message_deliveries",
    "message_reads"
  ]
}
```

### Безопасность

1. **Всегда проверяй X-Hub-Signature-256** — без этого можно получить поддельные запросы
2. **Отвечай 200 OK за 5 секунд** — иначе Meta считает доставку неудачной
3. **Обрабатывай асинхронно** — помести в очередь (Redis, RabbitMQ), отвечай мгновенно
4. **Дедупликация** — проверяй `message.mid` для защиты от повторных доставок

### Структура ответа

Всегда возвращай строку `EVENT_RECEIVED` с кодом 200:

```javascript
app.post('/webhook', (req, res) => {
  res.status(200).send('EVENT_RECEIVED');
  // Асинхронная обработка
  processEvents(req.body).catch(console.error);
});
```

---

## 16. Состояния диалога (FSM)

### Конечный автомат

```javascript
const states = {
  IDLE: 'idle',
  CHOOSING_TOUR: 'choosing_tour',
  ENTERING_DATE: 'entering_date',
  ENTERING_GUESTS: 'entering_guests',
  CONFIRMING: 'confirming',
  LIVE_AGENT: 'live_agent'
};

// Хранение состояний (Redis рекомендуется)
const userStates = new Map();

function handleMessage(senderId, message) {
  const state = userStates.get(senderId) || states.IDLE;

  switch (state) {
    case states.IDLE:
      if (message.text.match(/экскурс|тур|tour/i)) {
        userStates.set(senderId, states.CHOOSING_TOUR);
        return sendGenericTemplate(senderId, tourCatalog);
      }
      break;
    case states.CHOOSING_TOUR:
      userStates.set(senderId, states.ENTERING_DATE);
      return sendMessage(senderId, 'На какую дату? (дд.мм.гггг)');
    case states.ENTERING_DATE:
      userStates.set(senderId, states.ENTERING_GUESTS);
      return sendMessage(senderId, 'Сколько гостей?');
    case states.ENTERING_GUESTS:
      userStates.set(senderId, states.CONFIRMING);
      return sendReceiptTemplate(senderId, bookingData);
  }
}
```

### Интеграция с wit.ai (NLP от Meta)

В App Dashboard → Messenger Settings → Built-in NLP → включить.

```json
// Автоматически добавляется в webhook event
"message": {
  "text": "Хочу сафари на завтра для 4 человек",
  "nlp": {
    "intents": [{"name": "book_tour", "confidence": 0.95}],
    "entities": {
      "wit$datetime:datetime": [{"value": "2026-02-13"}],
      "wit$number:number": [{"value": 4}],
      "tour_type": [{"value": "safari", "confidence": 0.89}]
    }
  }
}
```

---

## 17. Rate Limits — ограничения

### API Rate Limits

| Параметр | Лимит |
|----------|-------|
| Calls per hour | 200 * кол-во подписчиков Page |
| Messages per second | до 250 (зависит от уровня) |
| Batch API | до 50 запросов в одном batch |
| Attachment upload | 25 MB макс |
| Generic Template elements | 10 |
| Quick Replies | 13 |
| Persistent Menu items | 3 на уровне, 3 уровня |
| Button Template buttons | 3 |
| Ice Breakers | 4 |

### 24-Hour Messaging Policy

- **Standard Messaging** — свободная отправка в течение 24 часов после последнего сообщения пользователя
- **Message Tags** — разрешены вне 24ч окна только для:
  - `CONFIRMED_EVENT_UPDATE` — обновление подтверждённого события
  - `POST_PURCHASE_UPDATE` — обновление после покупки
  - `ACCOUNT_UPDATE` — обновление аккаунта
  - `HUMAN_AGENT` — ответ живого оператора (в течение 7 дней)
- **One-Time Notification** — одно сообщение по согласию (до 1 года)
- **Recurring Notifications** — по подписке (daily/weekly/monthly)

Нарушение политики тегов ведёт к ограничению Page.

---

## 18. Примеры для туризма ОАЭ

### Каталог экскурсий (Generic Template)

```javascript
function sendTourCatalog(senderId) {
  return callSendAPI({
    recipient: { id: senderId },
    message: {
      attachment: {
        type: 'template',
        payload: {
          template_type: 'generic',
          elements: [
            {
              title: 'Desert Safari Premium',
              subtitle: 'Джип-сафари + BBQ ужин + шоу. 180 AED/чел',
              image_url: IMG_SAFARI,
              buttons: [
                { type: 'postback', title: 'Забронировать', payload: 'BOOK_SAFARI' },
                { type: 'phone_number', title: 'Позвонить', payload: '+971501234567' }
              ]
            },
            {
              title: 'Burj Khalifa At The Top',
              subtitle: '124-125 этаж, панорамный вид. 260 AED/чел',
              image_url: IMG_BURJ,
              buttons: [
                { type: 'postback', title: 'Забронировать', payload: 'BOOK_BURJ' }
              ]
            },
            {
              title: 'Abu Dhabi Full Day',
              subtitle: 'Grand Mosque + Louvre + Emirates Palace. 250 AED/чел',
              image_url: IMG_ABUDHABI,
              buttons: [
                { type: 'postback', title: 'Забронировать', payload: 'BOOK_ABUDHABI' }
              ]
            },
            {
              title: 'Dubai Marina Yacht',
              subtitle: '2 часа, яхта 42ft, до 10 гостей. От 600 AED',
              image_url: IMG_YACHT,
              buttons: [
                { type: 'postback', title: 'Подробнее', payload: 'YACHT_DETAILS' }
              ]
            }
          ]
        }
      }
    }
  });
}
```

### FAQ через Quick Replies

```javascript
function sendFAQ(senderId) {
  return callSendAPI({
    recipient: { id: senderId },
    message: {
      text: 'Часто задаваемые вопросы:',
      quick_replies: [
        { content_type: 'text', title: 'Способы оплаты', payload: 'FAQ_PAYMENT' },
        { content_type: 'text', title: 'Где офис?', payload: 'FAQ_OFFICE' },
        { content_type: 'text', title: 'Отмена бронирования', payload: 'FAQ_CANCEL' },
        { content_type: 'text', title: 'Детские цены', payload: 'FAQ_KIDS' },
        { content_type: 'text', title: 'Связаться с нами', payload: 'FAQ_CONTACT' }
      ]
    }
  });
}
```

### Чек бронирования (Receipt Template)

```javascript
function sendBookingReceipt(senderId, booking) {
  return callSendAPI({
    recipient: { id: senderId },
    message: {
      attachment: {
        type: 'template',
        payload: {
          template_type: 'receipt',
          recipient_name: booking.clientName,
          order_number: `DXB-${Date.now()}`,
          currency: 'AED',
          payment_method: booking.paymentMethod,
          summary: {
            subtotal: booking.subtotal,
            total_tax: booking.tax,
            total_cost: booking.total
          },
          elements: booking.items.map(item => ({
            title: item.name,
            subtitle: item.description,
            quantity: item.quantity,
            price: item.price,
            currency: 'AED',
            image_url: item.image
          }))
        }
      }
    }
  });
}
```

---

## 19. Деплой

### Node.js (Express)

```bash
# Зависимости
npm install express axios dotenv

# Структура
src/
  server.js          # Express + webhook
  handlers/
    message.js       # Обработка сообщений
    postback.js      # Обработка кнопок
  services/
    sendApi.js       # Обёртка Send API
    templates.js     # Генерация шаблонов
  state/
    fsm.js           # Конечный автомат
  .env               # Токены
```

### Python (Flask)

```python
from flask import Flask, request
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for event in entry.get('messaging', []):
                handle_event(event)
    return 'EVENT_RECEIVED', 200

def send_message(recipient_id, text):
    requests.post(
        f'https://graph.facebook.com/v22.0/me/messages',
        params={'access_token': PAGE_ACCESS_TOKEN},
        json={
            'recipient': {'id': recipient_id},
            'messaging_type': 'RESPONSE',
            'message': {'text': text}
        }
    )
```

### Serverless (AWS Lambda + API Gateway)

```javascript
// handler.js
exports.handler = async (event) => {
  if (event.httpMethod === 'GET') {
    // Verification
    const params = event.queryStringParameters;
    if (params['hub.verify_token'] === process.env.VERIFY_TOKEN) {
      return { statusCode: 200, body: params['hub.challenge'] };
    }
    return { statusCode: 403 };
  }

  const body = JSON.parse(event.body);
  // Обработка в фоне через SQS для быстрого ответа
  await sqs.sendMessage({
    QueueUrl: process.env.QUEUE_URL,
    MessageBody: JSON.stringify(body)
  }).promise();

  return { statusCode: 200, body: 'EVENT_RECEIVED' };
};
```

---

## 20. Библиотеки и фреймворки

| Библиотека | Язык | Особенности |
|-----------|------|------------|
| **Bottender** | Node.js/TS | Мультиплатформенный, event-based routing, TypeScript |
| **Botpress** | Node.js | Visual flow builder, NLU, open-source |
| **messenger-node** | Node.js | Минималистичная обёртка Send API |
| **fb-messenger-bot-api** | Node.js | Полная обёртка Platform API |
| **pymessenger** | Python | Простая обёртка Send API |
| **fbchat** | Python | Неофициальный, для автоматизации |
| **Claudia Bot Builder** | Node.js | AWS Lambda-native, простой синтаксис |

### Рекомендации по выбору

- **Быстрый старт** → `messenger-node` или `pymessenger`
- **Production с NLU** → Botpress + wit.ai
- **Мультиплатформенный бот** → Bottender (Messenger + Telegram + WhatsApp)
- **Serverless** → Claudia Bot Builder (Lambda)

---

## Таблица ресурсов

| Ресурс | URL |
|--------|-----|
| Messenger Platform Docs | https://developers.facebook.com/docs/messenger-platform |
| Send API Reference | https://developers.facebook.com/docs/messenger-platform/reference/send-api |
| Webhook Reference | https://developers.facebook.com/docs/messenger-platform/webhook |
| Template Reference | https://developers.facebook.com/docs/messenger-platform/send-messages/templates |
| Messenger Profile API | https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api |
| Graph API Explorer | https://developers.facebook.com/tools/explorer |
| Meta App Dashboard | https://developers.facebook.com/apps |
| wit.ai (NLP) | https://wit.ai |
| Bottender Framework | https://bottender.js.org |
| Botpress | https://botpress.com |
| Official Samples (GitHub) | https://github.com/fbsamples/messenger-platform-samples |
| Graph API Changelog | https://developers.facebook.com/docs/graph-api/changelog |
| Messenger Policy | https://developers.facebook.com/docs/messenger-platform/policy |
