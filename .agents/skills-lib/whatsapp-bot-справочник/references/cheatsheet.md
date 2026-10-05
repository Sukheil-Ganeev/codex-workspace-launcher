# WhatsApp Bot / Business API — Cheatsheet

## Base URL

```
https://graph.facebook.com/v21.0
```

---

## Основные endpoints

| Действие | Метод | Endpoint |
|----------|-------|----------|
| Отправить сообщение | POST | `/{PHONE_NUMBER_ID}/messages` |
| Загрузить media | POST | `/{PHONE_NUMBER_ID}/media` |
| Скачать media | GET | `/{MEDIA_ID}` |
| Удалить media | DELETE | `/{MEDIA_ID}` |
| Создать template | POST | `/{WABA_ID}/message_templates` |
| Список templates | GET | `/{WABA_ID}/message_templates` |
| Удалить template | DELETE | `/{WABA_ID}/message_templates?name=xxx` |
| Информация о номере | GET | `/{PHONE_NUMBER_ID}` |
| Регистрация номера | POST | `/{PHONE_NUMBER_ID}/register` |
| Business Profile | GET/POST | `/{PHONE_NUMBER_ID}/whatsapp_business_profile` |

---

## Headers (для всех запросов)

```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

---

## Типы сообщений — минимальный payload

### Text
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"text","text":{"body":"Текст"}}
```

### Image
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"image","image":{"link":"https://url.jpg","caption":"Описание"}}
```

### Video
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"video","video":{"link":"https://url.mp4"}}
```

### Document
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"document","document":{"link":"https://url.pdf","filename":"file.pdf"}}
```

### Audio
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"audio","audio":{"link":"https://url.ogg"}}
```

### Location
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"location","location":{"latitude":25.0997,"longitude":55.1724,"name":"Office","address":"Dubai"}}
```

### Sticker
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"sticker","sticker":{"link":"https://url.webp"}}
```

### Contacts
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"contacts","contacts":[{"name":{"formatted_name":"Support"},"phones":[{"phone":"+971501234567"}]}]}
```

### Reaction
```json
{"messaging_product":"whatsapp","to":"971501234567","type":"reaction","reaction":{"message_id":"wamid.xxx","emoji":"\u2705"}}
```

### Mark as Read
```json
{"messaging_product":"whatsapp","status":"read","message_id":"wamid.xxx"}
```

---

## Interactive Messages

### Reply Buttons (max 3)
```json
{"type":"interactive","interactive":{"type":"button","body":{"text":"Выберите:"},"action":{"buttons":[{"type":"reply","reply":{"id":"opt1","title":"Вариант 1"}},{"type":"reply","reply":{"id":"opt2","title":"Вариант 2"}}]}}}
```

### List Message (max 10 sections x 10 rows)
```json
{"type":"interactive","interactive":{"type":"list","body":{"text":"Меню:"},"action":{"button":"Открыть","sections":[{"title":"Секция","rows":[{"id":"row1","title":"Элемент 1","description":"Описание"}]}]}}}
```

### CTA URL
```json
{"type":"interactive","interactive":{"type":"cta_url","body":{"text":"Ссылка:"},"action":{"name":"cta_url","parameters":{"display_text":"Открыть","url":"https://example.com"}}}}
```

### Single Product
```json
{"type":"interactive","interactive":{"type":"product","body":{"text":"Рекомендуем:"},"action":{"catalog_id":"CAT_ID","product_retailer_id":"PRODUCT_ID"}}}
```

### Multi-Product
```json
{"type":"interactive","interactive":{"type":"product_list","header":{"type":"text","text":"Каталог"},"body":{"text":"Выберите:"},"action":{"catalog_id":"CAT_ID","sections":[{"title":"Секция","product_items":[{"product_retailer_id":"P1"},{"product_retailer_id":"P2"}]}]}}}
```

---

## Template Message

### Отправка
```json
{
  "messaging_product":"whatsapp","to":"971501234567","type":"template",
  "template":{
    "name":"template_name",
    "language":{"code":"en"},
    "components":[
      {"type":"header","parameters":[{"type":"image","image":{"link":"https://img.jpg"}}]},
      {"type":"body","parameters":[{"type":"text","text":"value1"},{"type":"text","text":"value2"}]},
      {"type":"button","sub_type":"quick_reply","index":"0","parameters":[{"type":"payload","payload":"btn_data"}]}
    ]
  }
}
```

### Категории templates
| Категория | Назначение | Цена |
|-----------|-----------|------|
| MARKETING | Промо, акции, рассылки | $$$ |
| UTILITY | Подтверждения, уведомления, напоминания | $$ |
| AUTHENTICATION | OTP, коды верификации | $ |

### Компоненты template
| Компонент | Обязательный | Форматы | Max переменных |
|-----------|-------------|---------|---------------|
| HEADER | Нет | TEXT, IMAGE, VIDEO, DOCUMENT | 1 |
| BODY | **Да** | TEXT | 10 |
| FOOTER | Нет | TEXT | 0 |
| BUTTONS | Нет | QUICK_REPLY, URL, PHONE_NUMBER | 1 (в URL) |

---

## Webhook — структура входящего сообщения

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WABA_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {"phone_number_id": "PHONE_ID", "display_phone_number": "971501234567"},
        "contacts": [{"profile": {"name": "Client"}, "wa_id": "971501234567"}],
        "messages": [{
          "from": "971501234567",
          "id": "wamid.xxx",
          "timestamp": "1707750000",
          "type": "text",
          "text": {"body": "Привет"}
        }]
      },
      "field": "messages"
    }]
  }]
}
```

### Типы входящих сообщений (message.type)
`text` | `image` | `video` | `audio` | `document` | `sticker` | `location` | `contacts` | `interactive` | `button` | `order` | `system` | `reaction`

### Interactive reply
```json
{"type": "interactive", "interactive": {
  "type": "button_reply",  // или "list_reply"
  "button_reply": {"id": "opt1", "title": "Вариант 1"}
}}
```

---

## Статусы доставки

```json
{"value":{"statuses":[{"id":"wamid.xxx","status":"sent","timestamp":"...","recipient_id":"971501234567"}]}}
```

| Статус | Описание |
|--------|----------|
| `sent` | Отправлено на сервер Meta |
| `delivered` | Доставлено на устройство |
| `read` | Прочитано |
| `failed` | Не доставлено (error в payload) |

---

## Rate Limits

| Параметр | Значение |
|----------|----------|
| Throughput (default) | 80 msg/sec |
| Throughput (upgraded) | 1000 msg/sec |
| Tier (новый аккаунт) | 250 уникальных / 24ч |
| Tier (верифицированный, 2026) | 100,000 уникальных / 24ч |
| Tier (Unlimited) | Enterprise-партнёры |
| API calls / min | 200,000 |
| Templates на WABA | до 100 |

---

## Коды ошибок (ключевые)

| Код | Описание | Действие |
|-----|----------|----------|
| 0 | AuthException | Проверить токен |
| 4 | API Too Many Calls | Backoff + retry |
| 100 | Invalid parameter | Проверить payload |
| 131026 | Undeliverable | Номер не в WA / заблокирован |
| 131047 | Re-engagement | 24ч окно закрыто → Template |
| 131051 | Unsupported msg type | Проверить type |
| 130429 | Rate limit hit | Backoff |
| 132000 | Template param count | Проверить переменные |
| 132012 | Template not found | Проверить name + language |
| 133010 | Phone not registered | Зарегистрировать номер |
| 368 | Temporarily blocked | Подождать 24-72ч |

---

## Ценообразование UAE (с июля 2025)

| Категория | Цена/сообщение | Бесплатно в 24ч окне |
|-----------|---------------|---------------------|
| Marketing | ~$0.15-0.18 | Нет |
| Utility | ~$0.08-0.12 | **Да** (если в активном окне) |
| Authentication | ~$0.04-0.06 | Нет |
| Service | $0 | **Да** (всегда) |

---

## Media лимиты

| Тип | Форматы | Max размер |
|-----|---------|-----------|
| Image | JPEG, PNG | 5 MB |
| Video | MP4, 3GPP | 16 MB |
| Audio | AAC, AMR, OGG, Opus | 16 MB |
| Document | PDF, DOC, XLSX, PPT, TXT | 100 MB |
| Sticker (static) | WebP | 100 KB |
| Sticker (animated) | WebP | 500 KB |

---

## Полезные ссылки

- Cloud API Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
- Template Docs: https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates
- Flows Docs: https://developers.facebook.com/docs/whatsapp/flows
- Pricing: https://business.whatsapp.com/products/platform-pricing
- Postman Collection: https://www.postman.com/meta/whatsapp-business-platform
- Error Codes: https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes
