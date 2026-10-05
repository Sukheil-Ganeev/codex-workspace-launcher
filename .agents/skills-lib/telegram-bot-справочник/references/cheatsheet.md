# Cheatsheet — Telegram Bot API

## API Endpoint

```
https://api.telegram.org/bot<TOKEN>/<METHOD>
```

---

## Основные методы

### Информация
| Метод | Описание |
|-------|----------|
| `getMe` | Информация о боте |
| `getUpdates` | Получить обновления (long polling) |
| `getWebhookInfo` | Статус webhook |
| `getChat` | Информация о чате |
| `getChatMember` | Информация об участнике чата |
| `getChatMemberCount` | Количество участников |

### Отправка контента
| Метод | Описание | Лимит |
|-------|----------|-------|
| `sendMessage` | Текст | 4096 символов |
| `sendPhoto` | Фото | 10 MB |
| `sendVideo` | Видео | 50 MB |
| `sendDocument` | Файл | 50 MB |
| `sendAudio` | Аудио | 50 MB |
| `sendVoice` | Голосовое | 50 MB |
| `sendVideoNote` | Видеосообщение (кружок) | - |
| `sendLocation` | Геолокация | - |
| `sendContact` | Контакт | - |
| `sendPoll` | Опрос | до 12 вариантов |
| `sendDice` | Случайное значение | - |
| `sendSticker` | Стикер | - |
| `sendMediaGroup` | Группа медиа | 2-10 элементов |
| `sendInvoice` | Счёт на оплату | - |

### Управление сообщениями
| Метод | Описание |
|-------|----------|
| `editMessageText` | Изменить текст |
| `editMessageCaption` | Изменить подпись |
| `editMessageMedia` | Изменить медиа |
| `editMessageReplyMarkup` | Изменить кнопки |
| `deleteMessage` | Удалить сообщение |
| `forwardMessage` | Переслать |
| `copyMessage` | Копировать (без "Forwarded") |
| `pinChatMessage` | Закрепить |
| `unpinChatMessage` | Открепить |

### Webhook
| Метод | Описание |
|-------|----------|
| `setWebhook` | Установить webhook |
| `deleteWebhook` | Удалить webhook |
| `getWebhookInfo` | Проверить webhook |

### Команды
| Метод | Описание |
|-------|----------|
| `setMyCommands` | Задать список команд |
| `getMyCommands` | Получить список команд |
| `deleteMyCommands` | Удалить команды |

### Callback
| Метод | Описание |
|-------|----------|
| `answerCallbackQuery` | Ответить на нажатие кнопки |
| `answerInlineQuery` | Ответить на inline-запрос |
| `answerPreCheckoutQuery` | Ответить на pre-checkout |

### Администрирование
| Метод | Описание |
|-------|----------|
| `banChatMember` | Забанить участника |
| `unbanChatMember` | Разбанить |
| `restrictChatMember` | Ограничить права |
| `promoteChatMember` | Дать права админа |
| `setChatTitle` | Изменить название чата |
| `setChatDescription` | Изменить описание |
| `setChatPhoto` | Изменить фото чата |

---

## Форматирование (HTML)

```html
<b>жирный</b>
<i>курсив</i>
<u>подчёркнутый</u>
<s>зачёркнутый</s>
<code>моноширинный</code>
<pre>блок кода</pre>
<pre language="python">код с подсветкой</pre>
<a href="https://example.com">ссылка</a>
<tg-spoiler>спойлер</tg-spoiler>
<blockquote>цитата</blockquote>
```

---

## Типы кнопок (InlineKeyboard)

```json
{"text": "Текст", "callback_data": "data"}
{"text": "Ссылка", "url": "https://..."}
{"text": "Mini App", "web_app": {"url": "https://..."}}
{"text": "Оплатить", "pay": true}
{"text": "Inline поиск", "switch_inline_query": "запрос"}
{"text": "Inline в текущем чате", "switch_inline_query_current_chat": ""}
{"text": "Войти", "login_url": {"url": "https://..."}}
```

---

## Коды ошибок

| Код | Описание | Действие |
|-----|----------|----------|
| 400 | Bad Request | Проверить параметры |
| 401 | Unauthorized | Проверить токен |
| 403 | Forbidden | Бот заблокирован / нет прав |
| 404 | Not Found | Неверный метод |
| 409 | Conflict | Конфликт polling/webhook |
| 429 | Too Many Requests | Подождать `retry_after` сек |

---

## Rate Limits

| Операция | Лимит |
|----------|-------|
| Разным чатам | 30 msg/sec |
| Одному чату (ЛС) | 1 msg/sec |
| Группа | 20 msg/min |
| Inline-результаты | 50 за ответ |
| Webhook timeout | 60 sec |
| getUpdates хранение | 24 часа |
| callback_data | 64 байта |
| Текст сообщения | 4096 символов |
| Caption | 1024 символа |

---

## Telegram Stars (XTR)

```
currency: "XTR"
provider_token: НЕ указывать
1000 Stars ≈ $13 USD (для создателя)
Минимум для вывода: 1000 Stars
Вывод доступен через: 21 день
Вывод: конвертация в TON
```

---

## Платежи (провайдер)

```
currency: "USD" / "EUR" / "AED" / ...
provider_token: "STRIPE_TOKEN" / "YOOKASSA_TOKEN"
amount: в минимальных единицах (центы для USD)
$70.00 → amount: 7000
```

---

## Webhook параметры setWebhook

| Параметр | Описание | По умолчанию |
|----------|----------|-------------|
| `url` | HTTPS URL | - |
| `certificate` | Публичный ключ (self-signed) | - |
| `ip_address` | Фиксированный IP | auto |
| `max_connections` | Макс. соединений | 40 (1-100) |
| `allowed_updates` | Типы обновлений | все |
| `drop_pending_updates` | Удалить старые | false |
| `secret_token` | Секретный токен | - |

**Допустимые порты:** 443, 80, 88, 8443

---

## Объект Update — основные поля

```
update_id           — уникальный ID
message             — новое сообщение
edited_message      — отредактированное
callback_query      — нажатие inline-кнопки
inline_query        — @bot запрос
chosen_inline_result — выбранный inline-результат
pre_checkout_query  — подтверждение оплаты
successful_payment  — (внутри message)
my_chat_member      — бот добавлен/удалён
chat_join_request   — запрос на вступление
```

---

## Объект Message — ключевые поля

```
message_id    — ID сообщения
from          — кто отправил (User)
chat          — куда отправлено (Chat)
date          — timestamp
text          — текст
photo         — массив PhotoSize
document      — Document
video         — Video
location      — Location
contact       — Contact
reply_markup  — клавиатура
web_app_data  — данные из Mini App
```

---

## Быстрые команды curl

```bash
# Проверить бота
curl "https://api.telegram.org/bot<T>/getMe"

# Отправить текст
curl -X POST "https://api.telegram.org/bot<T>/sendMessage" \
  -d "chat_id=ID&text=Hello"

# Установить webhook
curl -X POST "https://api.telegram.org/bot<T>/setWebhook" \
  -d "url=https://domain.com/webhook"

# Проверить webhook
curl "https://api.telegram.org/bot<T>/getWebhookInfo"

# Удалить webhook
curl -X POST "https://api.telegram.org/bot<T>/deleteWebhook"

# Задать команды
curl -X POST "https://api.telegram.org/bot<T>/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{"commands":[{"command":"start","description":"Запуск"}]}'
```

---

## Библиотеки — быстрый выбор

| Язык | Библиотека | Установка |
|------|------------|-----------|
| Python | aiogram 3 | `pip install aiogram` |
| Python | python-telegram-bot | `pip install python-telegram-bot` |
| Node.js | grammY | `npm install grammy` |
| Node.js | Telegraf | `npm install telegraf` |
| PHP | telegram-bot-sdk | `composer require irazasyed/telegram-bot-sdk` |
| Go | tgbotapi | `go get github.com/go-telegram-bot-api/telegram-bot-api/v5` |

---

## Деплой — быстрый выбор

| Платформа | Тип | Бесплатный план | Webhook |
|-----------|-----|-----------------|---------|
| Railway | PaaS | $5 кредит/мес | Да |
| Render | PaaS | Да (sleep) | Да |
| Vercel | Serverless | Да | Да (только) |
| Cloudflare Workers | Serverless | Да | Да (только) |
| Hetzner VPS | VPS | Нет ($4/мес) | Да |
| Docker (любой) | Container | - | Да |

---

**Версия:** 1.0
**Дата:** 12.02.2026
