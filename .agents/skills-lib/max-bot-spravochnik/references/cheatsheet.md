# Cheatsheet — Max Bot API

## Base URL и Auth

```
Base URL: https://platform-api.max.ru
Auth:     Authorization: YOUR_TOKEN  (header only!)
Format:   JSON (Content-Type: application/json)
```

---

## Все Endpoints

### Бот
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/me` | Информация о боте |
| PATCH | `/me` | Обновить информацию бота |

### Сообщения
| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/messages` | Отправить сообщение |
| PUT | `/messages?message_id={mid}` | Редактировать сообщение |
| DELETE | `/messages?message_id={mid}` | Удалить сообщение |
| GET | `/messages?chat_id={id}` | Получить сообщения из чата |

### Callback
| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/answers` | Ответ на callback кнопку |

### Чаты
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/chats` | Список чатов бота |
| GET | `/chats/{chatId}` | Информация о чате |
| PATCH | `/chats/{chatId}` | Редактировать чат |
| GET | `/chats/{chatId}/members` | Участники чата |
| POST | `/chats/{chatId}/members` | Добавить участника |
| DELETE | `/chats/{chatId}/members` | Удалить участника |
| GET | `/chats/{chatId}/members/me` | Бот в этом чате |

### Подписки (Webhook / Long Poll)
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/subscriptions` | Текущие подписки |
| POST | `/subscriptions` | Создать webhook |
| DELETE | `/subscriptions` | Удалить webhook |

### Обновления (Long Polling)
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/updates` | Получить обновления |

### Загрузка файлов
| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/uploads?type={type}` | Получить upload URL |

---

## Типы событий (update_type)

```
message_created      — новое сообщение
message_callback     — нажата inline-кнопка
message_edited       — сообщение отредактировано
message_removed      — сообщение удалено
bot_added            — бот добавлен в чат
bot_removed          — бот удалён из чата
bot_started          — пользователь нажал "Начать"
user_added           — пользователь добавлен
user_removed         — пользователь удалён
chat_title_changed   — название чата изменено
message_chat_created — создан чат с ботом
```

---

## Типы вложений (attachments)

```
image            — фото (JPEG, PNG), до 50 MB
video            — видео (MP4), до 2 GB
audio            — аудио (MP3, OGG), до 100 MB
file             — файл, до 100 MB
location         — геолокация (latitude, longitude)
contact          — контакт (name, vcf_phone)
sticker          — стикер
share            — карусель / карточка
inline_keyboard  — клавиатура с кнопками
```

---

## Типы кнопок

```
callback              — callback с payload (default/positive/negative intent)
link                  — открыть URL
request_contact       — запросить контакт пользователя
request_geo_location  — запросить геолокацию
chat                  — создать/открыть чат
```

---

## Лимиты

```
Rate limit:           30 RPS
Текст сообщения:      4000 символов
Кнопок в клавиатуре:  210 (30 рядов x 7)
Кнопок link в ряду:   3 макс.
Фото:                 50 MB
Видео:                2 GB
Аудио/файл:           100 MB
Long Poll timeout:    90 сек макс.
Long Poll limit:      100 обновлений
Webhook:              только HTTPS
Никнейм бота:         мин. 11 символов, суффикс _bot/bot
```

---

## HTTP-коды ответов

```
200 — Успех
400 — Неверный запрос (проверь параметры / файл не обработан)
401 — Неавторизован (проверь токен в Authorization header)
403 — Доступ запрещён (бот не в чате / нет прав)
404 — Не найдено (чат/сообщение не существует)
429 — Rate limit (подожди, снизь частоту)
500 — Ошибка сервера (повтори через 5 сек)
```

---

## Quick Recipes

### Проверить бота
```bash
curl -X GET "https://platform-api.max.ru/me" \
  -H "Authorization: TOKEN"
```

### Отправить текст
```bash
curl -X POST "https://platform-api.max.ru/messages" \
  -H "Authorization: TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123, "text": "Привет!"}'
```

### Отправить с клавиатурой
```bash
curl -X POST "https://platform-api.max.ru/messages" \
  -H "Authorization: TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123,
    "text": "Выберите:",
    "attachments": [{
      "type": "inline_keyboard",
      "payload": {
        "buttons": [
          [{"type": "callback", "text": "Да", "payload": "yes", "intent": "positive"},
           {"type": "callback", "text": "Нет", "payload": "no", "intent": "negative"}]
        ]
      }
    }]
  }'
```

### Ответить на callback
```bash
curl -X POST "https://platform-api.max.ru/answers" \
  -H "Authorization: TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"callback_id": "cb_123", "notification": "Принято!"}'
```

### Установить webhook
```bash
curl -X POST "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://my-server.com/webhook"}'
```

### Удалить webhook (вернуться к Long Polling)
```bash
curl -X DELETE "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: TOKEN"
```

### Long Polling цикл (Python)
```python
import requests, time

TOKEN = "YOUR_TOKEN"
URL = "https://platform-api.max.ru"
H = {"Authorization": TOKEN}
marker = None

while True:
    p = {"timeout": 30, "limit": 100}
    if marker: p["marker"] = marker
    r = requests.get(f"{URL}/updates", headers=H, params=p, timeout=35)
    data = r.json()
    marker = data.get("marker", marker)
    for u in data.get("updates", []):
        print(u["update_type"], u)
```

---

## Библиотеки (pip install / npm install)

```bash
# Python
pip install git+https://github.com/max-messenger/max-botapi-python.git

# TypeScript / Node.js
npm install @maxhub/max-bot-api

# Go
go get github.com/max-messenger/max-bot-api-client-go

# PHP
composer require bushlanovdev/max-bot-api-client-php
```

---

## Регистрация бота

```
1. Откройте Max → найдите @MasterBot
2. /start → /create
3. Никнейм: мин. 11 символов, суффикс _bot или bot
4. Имя бота: отображаемое имя в чате
5. Получите токен → сохраните
```
