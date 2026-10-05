# Cheatsheet — Instagram Messenger API

## Базовые URL

```
Base URL:     https://graph.facebook.com/v21.0/
Send API:     POST /me/messages
Profile API:  POST /me/messenger_profile
Webhook:      GET/POST /webhook (ваш сервер)
```

## Endpoints

| Метод | Endpoint | Назначение |
|-------|---------|-----------|
| `POST` | `/me/messages` | Отправка сообщений |
| `POST` | `/me/messenger_profile` | Ice Breakers, Persistent Menu |
| `GET` | `/me/messenger_profile?fields=...` | Получение настроек профиля |
| `DELETE` | `/me/messenger_profile` | Удаление Ice Breakers / Menu |
| `POST` | `/{comment-id}/private_replies` | Private Reply на комментарий |
| `POST` | `/{comment-id}` | Скрыть комментарий (`hide: true`) |
| `DELETE` | `/{comment-id}` | Удалить комментарий |
| `GET` | `/{page-id}?fields=instagram_business_account` | IG Business Account ID |

## Permissions

| Permission | Назначение | App Review |
|-----------|-----------|------------|
| `instagram_basic` | Профиль, медиа | Нет |
| `instagram_manage_messages` | DM (чтение/отправка) | Да |
| `instagram_manage_comments` | Комментарии | Да |
| `pages_messaging` | Отправка сообщений | Да |
| `pages_manage_metadata` | Webhook подписки | Да |

## Отправка сообщений — Шаблоны

### Текст

```json
{
  "recipient": { "id": "IGSID" },
  "message": { "text": "Текст сообщения" }
}
```

### Изображение

```json
{
  "recipient": { "id": "IGSID" },
  "message": {
    "attachment": {
      "type": "image",
      "payload": { "url": "https://..." }
    }
  }
}
```

### Quick Replies (до 13)

```json
{
  "recipient": { "id": "IGSID" },
  "message": {
    "text": "Выберите:",
    "quick_replies": [
      { "content_type": "text", "title": "Вариант 1", "payload": "OPT_1" },
      { "content_type": "text", "title": "Вариант 2", "payload": "OPT_2" }
    ]
  }
}
```

### Generic Template (до 10 карточек)

```json
{
  "recipient": { "id": "IGSID" },
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [
          {
            "title": "Заголовок",
            "subtitle": "Описание",
            "image_url": "https://...",
            "buttons": [
              { "type": "web_url", "url": "https://...", "title": "Открыть" },
              { "type": "postback", "title": "Выбрать", "payload": "SELECT_1" }
            ]
          }
        ]
      }
    }
  }
}
```

### Human Agent Tag (7 дней)

```json
{
  "recipient": { "id": "IGSID" },
  "message": { "text": "Менеджер на связи" },
  "messaging_type": "MESSAGE_TAG",
  "tag": "HUMAN_AGENT"
}
```

## Настройка профиля

### Ice Breakers (до 4)

```json
POST /me/messenger_profile
{
  "platform": "instagram",
  "ice_breakers": [
    { "question": "Вопрос 1", "payload": "ICE_1" },
    { "question": "Вопрос 2", "payload": "ICE_2" }
  ]
}
```

### Persistent Menu (до 20 пунктов)

```json
POST /me/messenger_profile
{
  "platform": "instagram",
  "persistent_menu": [
    {
      "locale": "default",
      "call_to_actions": [
        { "type": "postback", "title": "Пункт 1", "payload": "MENU_1" },
        { "type": "web_url", "title": "Сайт", "url": "https://..." }
      ]
    }
  ]
}
```

### Удаление настроек

```json
DELETE /me/messenger_profile
{
  "platform": "instagram",
  "fields": ["ice_breakers"]
}
```

## Private Reply

```json
POST /{comment-id}/private_replies
{
  "message": "Текст DM-ответа"
}
```

## Webhook Events

### Структура входящего сообщения

```json
{
  "object": "instagram",
  "entry": [{
    "id": "PAGE_ID",
    "time": 1234567890,
    "messaging": [{
      "sender": { "id": "USER_IGSID" },
      "recipient": { "id": "IG_BUSINESS_ID" },
      "timestamp": 1234567890,
      "message": {
        "mid": "MESSAGE_ID",
        "text": "Текст сообщения",
        "is_echo": false
      }
    }]
  }]
}
```

### Postback (нажатие кнопки)

```json
{
  "sender": { "id": "USER_IGSID" },
  "postback": {
    "title": "Текст кнопки",
    "payload": "PAYLOAD_STRING"
  }
}
```

### Quick Reply

```json
{
  "sender": { "id": "USER_IGSID" },
  "message": {
    "text": "Текст кнопки",
    "quick_reply": {
      "payload": "QR_PAYLOAD"
    }
  }
}
```

### Story Mention

```json
{
  "sender": { "id": "USER_IGSID" },
  "message": {
    "attachments": [{
      "type": "story_mention",
      "payload": { "url": "CDN_URL_OF_STORY" }
    }]
  }
}
```

### Story Reply

```json
{
  "sender": { "id": "USER_IGSID" },
  "message": {
    "text": "Ответ на story",
    "reply_to": {
      "story": { "url": "STORY_URL", "id": "STORY_ID" }
    }
  }
}
```

## Webhook подписки

```
Поля для Instagram DM:
- messages
- messaging_postbacks
- messaging_referrals
- message_reactions
- messaging_seen
```

## Rate Limits

| Параметр | Лимит |
|---------|-------|
| API вызовов | 200/час на аккаунт |
| Messaging Window | 24 часа |
| Human Agent Tag | 7 дней |
| Private Reply | 1 на комментарий |
| Ice Breakers | 4 вопроса |
| Persistent Menu | 20 пунктов, 1 уровень |
| Quick Replies | 13 на сообщение |
| Generic Template | 10 карточек |
| Фото | 8 MB (JPEG/PNG/GIF) |
| Видео/аудио/файлы | 25 MB |

## Типичные ошибки

| Код | Описание | Решение |
|-----|----------|---------|
| `#10` | Outside allowed window | 24ч окно истекло |
| `#100` | Invalid parameter / No matching user | Неверный IGSID |
| `#190` | Invalid access token | Токен истёк/невалидный |
| `#200` | Requires permission | Нужен App Review |
| `#613` | Rate limit exceeded | Подождите 1 час |

## Webhook верификация

### GET (проверка от Meta)

```
hub.mode = subscribe
hub.verify_token = YOUR_VERIFY_TOKEN
hub.challenge = CHALLENGE_STRING
→ Ответ: 200 + challenge
```

### POST (подпись)

```
Заголовок: X-Hub-Signature-256: sha256=HASH
HMAC-SHA256(raw_body, APP_SECRET)
```

## Checklist деплоя

- [ ] HTTPS с валидным SSL
- [ ] Webhook верификация (GET) работает
- [ ] Подписка на events (messages, messaging_postbacks)
- [ ] App Review пройден (instagram_manage_messages)
- [ ] Page Access Token получен и сохранён
- [ ] Instagram аккаунт = Business/Creator
- [ ] Привязан к Facebook Page
- [ ] X-Hub-Signature-256 проверяется
- [ ] is_echo фильтруется (нет бесконечного цикла)
- [ ] 200 OK возвращается быстро (обработка async)
- [ ] Rate limit обработка (очередь + retry)
- [ ] Ice Breakers настроены
- [ ] Persistent Menu настроено
- [ ] Human Agent handover реализован
