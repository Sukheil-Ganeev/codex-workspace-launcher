# Cheatsheet — Facebook Messenger Bot API

## Endpoints

```
BASE = https://graph.facebook.com/v22.0

Send Message:      POST {BASE}/me/messages?access_token={TOKEN}
Messenger Profile: POST {BASE}/me/messenger_profile?access_token={TOKEN}
User Profile:      GET  {BASE}/{PSID}?fields=first_name,last_name&access_token={TOKEN}
Upload Attachment:  POST {BASE}/me/message_attachments?access_token={TOKEN}
Pass Thread:       POST {BASE}/me/pass_thread_control?access_token={TOKEN}
Take Thread:       POST {BASE}/me/take_thread_control?access_token={TOKEN}
Subscribe:         POST {BASE}/me/subscribed_apps?access_token={TOKEN}
```

## messaging_type (обязательно)

| Тип | Когда |
|-----|-------|
| `RESPONSE` | Ответ на сообщение (24ч) |
| `UPDATE` | Проактивное обновление (24ч) |
| `MESSAGE_TAG` | Вне 24ч окна (с тегом) |

## Message Tags (вне 24ч)

| Тег | Использование |
|-----|--------------|
| `CONFIRMED_EVENT_UPDATE` | Обновление события |
| `POST_PURCHASE_UPDATE` | После покупки |
| `ACCOUNT_UPDATE` | Изменения аккаунта |
| `HUMAN_AGENT` | Живой оператор (7 дней) |

## Быстрые шаблоны

### Текст
```json
{"recipient":{"id":"PSID"},"messaging_type":"RESPONSE","message":{"text":"Привет!"}}
```

### Картинка
```json
{"recipient":{"id":"PSID"},"message":{"attachment":{"type":"image","payload":{"url":"https://...","is_reusable":true}}}}
```

### Typing indicator
```json
{"recipient":{"id":"PSID"},"sender_action":"typing_on"}
```

### Generic Template (карусель)
```json
{
  "recipient":{"id":"PSID"},
  "message":{"attachment":{"type":"template","payload":{
    "template_type":"generic",
    "elements":[{
      "title":"Title",
      "subtitle":"Subtitle",
      "image_url":"https://...",
      "buttons":[{"type":"postback","title":"Click","payload":"ACTION"}]
    }]
  }}}
}
```

### Button Template
```json
{
  "recipient":{"id":"PSID"},
  "message":{"attachment":{"type":"template","payload":{
    "template_type":"button",
    "text":"Choose:",
    "buttons":[
      {"type":"postback","title":"Option 1","payload":"OPT1"},
      {"type":"web_url","title":"Website","url":"https://..."}
    ]
  }}}
}
```

### Receipt Template
```json
{
  "recipient":{"id":"PSID"},
  "message":{"attachment":{"type":"template","payload":{
    "template_type":"receipt",
    "recipient_name":"Name",
    "order_number":"ORD-001",
    "currency":"AED",
    "payment_method":"Cash",
    "summary":{"total_cost":260},
    "elements":[{"title":"Item","quantity":1,"price":260,"currency":"AED"}]
  }}}
}
```

### Quick Replies
```json
{
  "recipient":{"id":"PSID"},
  "message":{
    "text":"Выберите:",
    "quick_replies":[
      {"content_type":"text","title":"Вариант 1","payload":"V1"},
      {"content_type":"text","title":"Вариант 2","payload":"V2"},
      {"content_type":"user_phone_number"}
    ]
  }
}
```

## Messenger Profile

### Get Started
```json
POST /me/messenger_profile
{"get_started":{"payload":"GET_STARTED"}}
```

### Greeting
```json
{"greeting":[{"locale":"default","text":"Welcome! {{user_first_name}}"}]}
```

### Persistent Menu
```json
{"persistent_menu":[{"locale":"default","composer_input_disabled":false,
  "call_to_actions":[
    {"type":"postback","title":"Menu","payload":"MENU"},
    {"type":"web_url","title":"Site","url":"https://..."}
  ]}]}
```

### Ice Breakers
```json
{"ice_breakers":[{"question":"FAQ question?","payload":"FAQ_1"}]}
```

### Удалить настройку
```json
DELETE /me/messenger_profile
{"fields":["persistent_menu","get_started","greeting","ice_breakers"]}
```

## Webhook Events

```
messages            → event.message.text / .attachments
messaging_postbacks → event.postback.payload
messaging_referrals → event.referral.ref
messaging_optins    → event.optin.one_time_notif_token
message_deliveries  → event.delivery.mids[]
message_reads       → event.read.watermark
messaging_handovers → event.pass_thread_control / .take_thread_control
```

## Кнопки — типы

```json
// URL (с WebView)
{"type":"web_url","title":"Open","url":"https://...","webview_height_ratio":"tall"}

// Postback
{"type":"postback","title":"Click","payload":"ACTION"}

// Phone
{"type":"phone_number","title":"Call","payload":"+971501234567"}

// Login
{"type":"account_link","url":"https://auth.example.com"}

// Logout
{"type":"account_unlink"}
```

## Handover Protocol

```json
// Передать оператору
POST /me/pass_thread_control
{"recipient":{"id":"PSID"},"target_app_id":123456,"metadata":"reason"}

// Забрать обратно
POST /me/take_thread_control
{"recipient":{"id":"PSID"},"metadata":"resolved"}
```

## One-Time Notification

```json
// Запрос
{"recipient":{"id":"PSID"},"message":{"attachment":{"type":"template","payload":{
  "template_type":"one_time_notif_req","title":"Notify?","payload":"TOPIC"}}}}

// Отправка (токен из optin)
{"recipient":{"one_time_notif_token":"TOKEN"},"message":{"text":"Update!"}}
```

## Recurring Notifications

```json
// Запрос подписки
{"recipient":{"id":"PSID"},"message":{"attachment":{"type":"template","payload":{
  "template_type":"notification_messages","title":"Weekly deals",
  "payload":"WEEKLY","notification_messages_frequency":"WEEKLY"}}}}

// Отправка
{"recipient":{"notification_messages_token":"TOKEN"},"message":{"text":"New deal!"}}
```

## Лимиты

| Параметр | Значение |
|----------|---------|
| API calls/hour | 200 * кол-во подписчиков |
| Generic elements | 10 |
| Quick Replies | 13 |
| Buttons per template | 3 |
| Persistent Menu levels | 3 |
| Persistent Menu items/level | 3 |
| Ice Breakers | 4 |
| Title length | 80 символов |
| Subtitle length | 80 символов |
| Button title | 20 символов |
| Quick Reply title | 20 символов |
| Payload | 1000 символов |
| Attachment size | 25 MB |
| Webhook response time | 5 секунд |
| OTN token lifetime | 1 год |

## Permissions для App Review

| Permission | Зачем |
|-----------|-------|
| `pages_messaging` | Отправка/получение сообщений |
| `pages_manage_metadata` | Подписка webhook |
| `pages_read_engagement` | Чтение данных Page |
| `pages_show_list` | Список Pages |

## Полезные curl-команды

```bash
# Отправить текст
curl -X POST "https://graph.facebook.com/v22.0/me/messages?access_token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient":{"id":"PSID"},"messaging_type":"RESPONSE","message":{"text":"Hello"}}'

# Проверить подписку
curl "https://graph.facebook.com/v22.0/PAGE_ID/subscribed_apps?access_token=TOKEN"

# Подписаться на events
curl -X POST "https://graph.facebook.com/v22.0/PAGE_ID/subscribed_apps?access_token=TOKEN" \
  -d 'subscribed_fields=messages,messaging_postbacks,messaging_optins,messaging_handovers'

# Установить Get Started
curl -X POST "https://graph.facebook.com/v22.0/me/messenger_profile?access_token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"get_started":{"payload":"GET_STARTED"}}'

# Профиль пользователя
curl "https://graph.facebook.com/v22.0/PSID?fields=first_name,last_name,profile_pic&access_token=TOKEN"
```
