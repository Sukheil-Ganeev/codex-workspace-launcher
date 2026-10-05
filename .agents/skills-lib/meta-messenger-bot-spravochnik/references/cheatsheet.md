# Meta Messenger Bot — Шпаргалка

## API Endpoints (Graph API v22.0)

| Действие | Метод | Endpoint |
|----------|-------|----------|
| Отправить сообщение | POST | `/me/messages` |
| Настроить профиль (меню, Ice Breakers) | POST | `/me/messenger_profile` |
| Получить профиль пользователя | GET | `/{USER_ID}?fields=name,profile_pic` |
| Private Reply (IG) | POST | `/{COMMENT_ID}/private_replies` |
| Скрыть комментарий (IG) | POST | `/{COMMENT_ID}` с `{hide: true}` |
| Удалить комментарий (IG) | DELETE | `/{COMMENT_ID}` |
| Передать управление (FB) | POST | `/me/pass_thread_control` |
| Забрать управление (FB) | POST | `/me/take_thread_control` |
| Подписка на webhook events | POST | `/me/subscribed_apps` |
| IG Business Account ID | GET | `/{PAGE_ID}?fields=instagram_business_account` |
| Long-lived token | GET | `/oauth/access_token?grant_type=fb_exchange_token` |
| Page token (бессрочный) | GET | `/me/accounts` |

Базовый URL: `https://graph.facebook.com/v22.0/`

## Webhook Object

| Платформа | `body.object` | ID пользователя |
|-----------|--------------|-----------------|
| Instagram | `instagram` | IGSID |
| Facebook | `page` | PSID |

## Шаблоны (template_type)

| Шаблон | IG | FB | Макс. элементов |
|--------|----|----|----------------|
| `generic` | + | + | 10 карточек, 3 кнопки/карточка |
| `button` | - | + | 3 кнопки |
| `receipt` | - | + | N позиций |
| `media` | - | + | 1 медиа + 1 кнопка |
| `airline_boardingpass` | - | + | N посадочных |
| `airline_itinerary` | - | + | N рейсов |
| `one_time_notif_req` | - | + | 1 запрос |
| `notification_messages` | - | + | 1 подписка |

## Типы кнопок

| Тип | IG | FB | Действие |
|-----|----|----|----------|
| `web_url` | + | + | Открыть URL |
| `postback` | + | + | Отправить payload |
| `phone_number` | - | + | Позвонить |
| `account_link` | - | + | Вход через Account Linking |
| `account_unlink` | - | + | Выход |

## Quick Replies content_type

| Тип | Описание |
|-----|----------|
| `text` | Текстовая кнопка с payload |
| `user_email` | Запрос email (с согласия) |
| `user_phone_number` | Запрос телефона (с согласия) |

## Лимиты

| Параметр | Instagram | Facebook |
|----------|-----------|---------|
| API calls | 200/час | 200 * followers/час |
| Quick Replies | 13 | 13 |
| Generic Template | 10 | 10 |
| Ice Breakers | 4 | 4 |
| Persistent Menu | 20 пунктов, 1 уровень | 3 пункта, 3 уровня |
| Button Template кнопки | N/A | 3 |
| Messaging Window | 24ч | 24ч |
| Human Agent Tag | 7 дней | 7 дней |
| Вложения (image) | 8 MB | 25 MB |
| Вложения (video/audio/file) | 25 MB | 25 MB |

## messaging_type (только FB)

| Тип | Когда |
|-----|-------|
| `RESPONSE` | Ответ на сообщение (24ч) |
| `UPDATE` | Проактивное обновление (24ч) |
| `MESSAGE_TAG` | Вне 24ч окна |

## Message Tags (FB, вне 24ч)

| Тег | Назначение |
|-----|-----------|
| `CONFIRMED_EVENT_UPDATE` | Обновление события |
| `POST_PURCHASE_UPDATE` | После покупки |
| `ACCOUNT_UPDATE` | Обновление аккаунта |
| `HUMAN_AGENT` | Живой оператор (7 дней) |

## Sender Actions (только FB)

| Action | Эффект |
|--------|--------|
| `typing_on` | "Печатает..." (20 сек) |
| `typing_off` | Убрать индикатор |
| `mark_seen` | Прочитано |

## Webhook Retry Policy (FB)

1 мин -> 5 мин -> 30 мин -> 1 час -> каждый час до 24ч -> webhook отключается.

## Recurring Notifications (FB)

| Частота | Значение |
|---------|---------|
| Ежедневно | `DAILY` |
| Еженедельно | `WEEKLY` |
| Ежемесячно | `MONTHLY` |

## Permissions (App Review)

| Permission | IG | FB |
|-----------|----|----|
| `pages_messaging` | + | + |
| `pages_manage_metadata` | + | + |
| `instagram_basic` | + | - |
| `instagram_manage_messages` | + | - |
| `instagram_manage_comments` | + | - |
| `pages_read_engagement` | - | + |

## Минимальный .env

```
PAGE_ACCESS_TOKEN=EAA...
APP_SECRET=abc123...
VERIFY_TOKEN=my_custom_token
PORT=3000
```

## Быстрый curl — отправка сообщения

```bash
# Facebook (messaging_type ОБЯЗАТЕЛЕН)
curl -X POST "https://graph.facebook.com/v22.0/me/messages" \
  -H "Content-Type: application/json" \
  -d '{"messaging_type":"RESPONSE","recipient":{"id":"PSID"},"message":{"text":"Hello!"}}' \
  -G --data-urlencode "access_token=TOKEN"

# Instagram (messaging_type НЕ нужен)
curl -X POST "https://graph.facebook.com/v22.0/me/messages" \
  -H "Content-Type: application/json" \
  -d '{"recipient":{"id":"IGSID"},"message":{"text":"Hello!"}}' \
  -G --data-urlencode "access_token=TOKEN"
```

## Порты webhook серверов (конвенция)

| Платформа | Порт | Фреймворк |
|-----------|------|-----------|
| Mini App | 8080 | FastAPI |
| Instagram DM | 8081 | FastAPI |
| WhatsApp | 8082 | FastAPI |
| Facebook Messenger | 8083 | FastAPI |

## Synthetic user_id (multi-platform shared DB)

| Платформа | Диапазон | Offset |
|-----------|---------|--------|
| Telegram | Positive (как есть) | 0 |
| VK | +10,000,000,000 | VK_ID_OFFSET |
| Instagram | -1 .. -999 | Negative |
| WhatsApp | -1000 .. -1999 | Negative |
| Facebook | -2000 .. -2999 | Negative |

## form_type по платформам

| Платформа | form_type |
|-----------|-----------|
| Telegram | GT, PT, Buggy, etc. |
| Instagram | IG_GT |
| WhatsApp | WA_GT |
| Facebook | FB_GT |
| VK | GT (+ VK_ID_OFFSET) |

## Facebook .env

```
FB_PAGE_ACCESS_TOKEN=EAA...
FB_PAGE_ID=123456789
FB_VERIFY_TOKEN=fb_verify_token_2026
FB_WEBHOOK_PORT=8083
META_APP_SECRET=abc123...        # Shared IG/WA/FB
```
