---
name: max-bot-spravochnik
description: "Руководство по Max (ex-TamTam) Bot API для туристического бизнеса ОАЭ. REST API, Long Poll, Webhooks, клавиатуры, карусели, медиа. Триггеры - max bot, макс бот."
version: 2.0.0
author: Claude Code Agent
created: 2026-02-12
---
# Max Bot API — Справочник для туристического бизнеса ОАЭ

## 1. Quick Start

### Что такое Max Bot API

Max (бывший TamTam, бывший ICQ) — российский мессенджер от VK. Bot API позволяет создавать ботов, которые принимают и отправляют сообщения, обрабатывают callback-кнопки, работают с медиа и управляют чатами.

**Важно:** Max Bot API базируется на TamTam Bot API (НЕ на VK Bot API). Это отдельный REST API со своим форматом запросов.

### Регистрация бота

1. Откройте Max и найдите **@MasterBot**
2. Отправьте `/start`, затем `/create`
3. Придумайте никнейм бота:
   - Минимум **11 символов** (включая суффикс)
   - Должен заканчиваться на `bot` или `_bot`
   - Пример: `dubaitours_bot`, `safariuae_bot`
4. Введите отображаемое имя бота (видно в шапке чата)
5. MasterBot выдаст **токен** — сохраните его

**Пример токена:**
```
AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

### Первый запрос — проверка бота

```bash
curl -X GET "https://platform-api.max.ru/me" \
  -H "Authorization: AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"
```

**Ответ:**
```json
{
  "user_id": 123456789,
  "name": "Dubai Tours Bot",
  "username": "dubaitours_bot",
  "is_bot": true,
  "last_activity_time": 1707753600
}
```

### Отправка первого сообщения

```bash
curl -X POST "https://platform-api.max.ru/messages" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Добро пожаловать! Я помогу подобрать экскурсию в Дубае."
  }'
```

---

## 2. Архитектура

### Обзор

```
Пользователь Max  <-->  Max Server  <-->  Bot API (platform-api.max.ru)  <-->  Ваш сервер
```

**Протокол:** HTTPS REST API
**Формат данных:** JSON (Content-Type: application/json)
**Кодировка:** UTF-8

### Два режима получения обновлений

| Режим | Описание | Когда использовать |
|-------|----------|--------------------|
| **Long Polling** | GET /updates, бот сам запрашивает | Разработка, тесты, простые боты |
| **Webhook** | POST на ваш URL от Max сервера | Продакшен, высокие нагрузки |

Одновременно может быть активен только один режим.

### Base URL

```
https://platform-api.max.ru
```

**Важно:** Старый домен `botapi.max.ru` больше НЕ поддерживается. Используйте только `platform-api.max.ru`.

---

## 3. Аутентификация

### Передача токена

Токен передаётся **только в заголовке Authorization** (query parameter больше не работает):

```
Authorization: YOUR_BOT_TOKEN
```

**Неправильно (устарело):**
```
GET /me?access_token=YOUR_TOKEN   # НЕ РАБОТАЕТ
```

**Правильно:**
```
GET /me
Authorization: YOUR_TOKEN
```

### Проверка токена — GET /me

```bash
curl -X GET "https://platform-api.max.ru/me" \
  -H "Authorization: YOUR_TOKEN"
```

Возвращает информацию о боте: user_id, name, username, is_bot, avatar_url, commands (если заданы).

---

## 4. Обработка сообщений

### Получение обновлений — GET /updates

```bash
curl -X GET "https://platform-api.max.ru/updates?limit=100&timeout=30" \
  -H "Authorization: YOUR_TOKEN"
```

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `limit` | int | Макс. число обновлений (1-100, по умолчанию 100) |
| `timeout` | int | Таймаут long polling в секундах (макс. 90) |
| `marker` | long | Маркер последнего обновления (для пагинации) |
| `types` | string[] | Фильтр типов событий |

**Ответ:**
```json
{
  "updates": [
    {
      "update_type": "message_created",
      "timestamp": 1707753600000,
      "message": {
        "sender": {"user_id": 111, "name": "Анна"},
        "recipient": {"chat_id": 222},
        "body": {
          "mid": "mid.abc123",
          "seq": 1,
          "text": "Хочу экскурсию на яхте"
        },
        "timestamp": 1707753600000
      }
    }
  ],
  "marker": 1707753600001
}
```

### Типы событий (update_type)

| Тип | Описание |
|-----|----------|
| `message_created` | Новое сообщение |
| `message_callback` | Нажатие inline-кнопки |
| `message_edited` | Сообщение отредактировано |
| `message_removed` | Сообщение удалено |
| `bot_added` | Бот добавлен в чат |
| `bot_removed` | Бот удалён из чата |
| `user_added` | Пользователь добавлен в чат |
| `user_removed` | Пользователь удалён из чата |
| `bot_started` | Пользователь нажал "Начать" |
| `chat_title_changed` | Изменено название чата |
| `message_chat_created` | Создан новый чат с ботом |

### Отправка сообщения — POST /messages

```bash
curl -X POST "https://platform-api.max.ru/messages" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Пустынное сафари — от $80 с человека!",
    "attachments": [],
    "notify": true
  }'
```

**Параметры тела запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| `chat_id` | long | ID чата (обязательно) |
| `text` | string | Текст сообщения (до 4000 символов) |
| `attachments` | array | Вложения (медиа, клавиатуры) |
| `link` | object | Ответ/пересылка сообщения |
| `notify` | bool | Уведомить получателя (по умолчанию true) |
| `format` | string | Формат текста: `markdown` или `html` |

### Редактирование сообщения — PUT /messages

```bash
curl -X PUT "https://platform-api.max.ru/messages?message_id=mid.abc123" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Цена обновлена: пустынное сафари — от $75!"
  }'
```

### Удаление сообщения — DELETE /messages

```bash
curl -X DELETE "https://platform-api.max.ru/messages?message_id=mid.abc123" \
  -H "Authorization: YOUR_TOKEN"
```

### Ответ на callback — POST /answers

Когда пользователь нажимает inline-кнопку, Max отправляет событие `message_callback`. Бот должен ответить:

```bash
curl -X POST "https://platform-api.max.ru/answers" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "callback_id": "callback_abc123",
    "notification": "Экскурсия добавлена в корзину!",
    "message": {
      "text": "Вы выбрали: Burj Khalifa Tour",
      "attachments": []
    }
  }'
```

**Поля:**
| Поле | Описание |
|------|----------|
| `callback_id` | ID из события message_callback (обязательно) |
| `notification` | Всплывающее уведомление (опционально, до 64 символов) |
| `message` | Обновлённое сообщение (заменяет текущее) |

---

## 5. Клавиатуры (Inline Keyboard)

### Структура

Клавиатура — это attachment типа `InlineKeyboardAttachment`. Ограничения:
- До **30 рядов**
- До **7 кнопок** в ряду
- До **3 кнопок** для типов: `link`, `open_app`, `request_contact`, `request_geo_location`

### Типы кнопок

| Тип | Описание | Поля |
|-----|----------|------|
| `callback` | Callback-кнопка | text, payload, intent |
| `link` | Открыть URL | text, url |
| `request_contact` | Запросить контакт | text |
| `request_geo_location` | Запросить геолокацию | text |
| `chat` | Открыть/создать чат | text, chat_title, chat_description |

### Intent (стиль кнопки callback)

| Значение | Стиль |
|----------|-------|
| `default` | Стандартный (синий/белый) |
| `positive` | Зелёный |
| `negative` | Красный |

### Пример: меню экскурсий

```json
{
  "chat_id": 123456789,
  "text": "Выберите экскурсию в Дубае:",
  "attachments": [
    {
      "type": "inline_keyboard",
      "payload": {
        "buttons": [
          [
            {"type": "callback", "text": "Burj Khalifa", "payload": "tour_burj"},
            {"type": "callback", "text": "Desert Safari", "payload": "tour_safari"}
          ],
          [
            {"type": "callback", "text": "Yacht Tour", "payload": "tour_yacht"},
            {"type": "callback", "text": "City Tour", "payload": "tour_city"}
          ],
          [
            {"type": "callback", "text": "Abu Dhabi Day Trip", "payload": "tour_abudhabi", "intent": "positive"}
          ],
          [
            {"type": "link", "text": "Наш сайт", "url": "https://example.com"}
          ]
        ]
      }
    }
  ]
}
```

### Обработка callback

Когда пользователь нажимает кнопку, приходит событие:

```json
{
  "update_type": "message_callback",
  "timestamp": 1707753600000,
  "callback": {
    "callback_id": "cb_123",
    "payload": "tour_burj",
    "user": {"user_id": 111, "name": "Анна"}
  },
  "message": {
    "sender": {"user_id": 999, "name": "Dubai Tours Bot"},
    "body": {"mid": "mid.abc123", "text": "Выберите экскурсию:"}
  }
}
```

---

## 6. Медиа — загрузка и отправка

### Процесс загрузки (3 шага)

**Шаг 1: Получить URL для загрузки**

```bash
curl -X POST "https://platform-api.max.ru/uploads?type=photo" \
  -H "Authorization: YOUR_TOKEN"
```

**Типы:** `photo`, `video`, `audio`, `file`

**Ответ:**
```json
{
  "url": "https://upload.max.ru/..."
}
```

**Шаг 2: Загрузить файл**

```bash
curl -X POST "https://upload.max.ru/..." \
  -F "data=@burj_khalifa.jpg"
```

**Ответ:**
```json
{
  "token": "upload_token_abc123"
}
```

**Шаг 3: Отправить сообщение с вложением**

```json
{
  "chat_id": 123456789,
  "text": "Burj Khalifa — 828 метров!",
  "attachments": [
    {
      "type": "image",
      "payload": {
        "token": "upload_token_abc123"
      }
    }
  ]
}
```

### Типы вложений

| Тип attachment | Описание | Макс. размер |
|----------------|----------|-------------|
| `image` | Фото (JPEG, PNG) | 50 MB |
| `video` | Видео (MP4) | 2 GB |
| `audio` | Аудио (MP3, OGG) | 100 MB |
| `file` | Любой файл | 100 MB |
| `location` | Геолокация | — |
| `contact` | Контакт | — |
| `sticker` | Стикер | — |
| `share` | Карусель (см. раздел 7) | — |
| `inline_keyboard` | Клавиатура | — |

### Отправка геолокации

```json
{
  "chat_id": 123456789,
  "text": "Наш офис в Dubai:",
  "attachments": [
    {
      "type": "location",
      "latitude": 25.0975,
      "longitude": 55.1712
    }
  ]
}
```

### Отправка контакта

```json
{
  "chat_id": 123456789,
  "attachments": [
    {
      "type": "contact",
      "payload": {
        "name": "Сухейль — Dubai Tours",
        "vcf_phone": "+971501234567"
      }
    }
  ]
}
```

---

## 7. Карусели (Share Attachment)

Карусель позволяет отправить несколько карточек в одном сообщении. Каждая карточка может содержать фото, заголовок, описание и кнопки.

### Пример: карусель экскурсий

```json
{
  "chat_id": 123456789,
  "attachments": [
    {
      "type": "share",
      "payload": {
        "title": "Desert Safari",
        "description": "Джип-сафари по пустыне с BBQ ужином. $80/чел.",
        "image_url": "https://example.com/safari.jpg",
        "buttons": [
          {"type": "callback", "text": "Забронировать", "payload": "book_safari", "intent": "positive"},
          {"type": "link", "text": "Подробнее", "url": "https://example.com/safari"}
        ]
      }
    },
    {
      "type": "share",
      "payload": {
        "title": "Burj Khalifa Tour",
        "description": "Билеты на смотровую площадку. 124+125 этаж. $50/чел.",
        "image_url": "https://example.com/burj.jpg",
        "buttons": [
          {"type": "callback", "text": "Забронировать", "payload": "book_burj", "intent": "positive"}
        ]
      }
    },
    {
      "type": "share",
      "payload": {
        "title": "Yacht Tour",
        "description": "Аренда яхты от 2 часов. Dubai Marina. От $200.",
        "image_url": "https://example.com/yacht.jpg",
        "buttons": [
          {"type": "callback", "text": "Забронировать", "payload": "book_yacht", "intent": "positive"}
        ]
      }
    }
  ]
}
```

---

## 8. Управление чатами

### Получить информацию о чате — GET /chats/{chatId}

```bash
curl -X GET "https://platform-api.max.ru/chats/123456789" \
  -H "Authorization: YOUR_TOKEN"
```

### Список чатов бота — GET /chats

```bash
curl -X GET "https://platform-api.max.ru/chats?count=50&marker=0" \
  -H "Authorization: YOUR_TOKEN"
```

### Редактировать чат — PATCH /chats/{chatId}

```bash
curl -X PATCH "https://platform-api.max.ru/chats/123456789" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dubai Tours VIP Group",
    "pin": "mid.abc123",
    "notify": true
  }'
```

### Действия с участниками

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/chats/{chatId}/members` | Список участников |
| POST | `/chats/{chatId}/members` | Добавить участника |
| DELETE | `/chats/{chatId}/members` | Удалить участника |
| GET | `/chats/{chatId}/members/me` | Информация о боте в чате |

### Типы чатов

| Тип | Описание |
|-----|----------|
| `dialog` | Личный диалог (бот + пользователь) |
| `chat` | Групповой чат |
| `channel` | Канал |

---

## 9. Подписки — Long Polling

### Как работает Long Polling

1. Бот отправляет GET /updates с timeout
2. Сервер держит соединение открытым до появления событий (или до timeout)
3. При появлении событий — возвращает массив updates и marker
4. Бот обрабатывает события и снова запрашивает GET /updates с новым marker

### Базовый цикл

```python
import requests
import time

TOKEN = "YOUR_TOKEN"
BASE_URL = "https://platform-api.max.ru"
HEADERS = {"Authorization": TOKEN}

marker = None

while True:
    params = {"timeout": 30, "limit": 100}
    if marker:
        params["marker"] = marker

    try:
        resp = requests.get(
            f"{BASE_URL}/updates",
            headers=HEADERS,
            params=params,
            timeout=35  # чуть больше чем API timeout
        )
        data = resp.json()
        updates = data.get("updates", [])
        marker = data.get("marker", marker)

        for update in updates:
            handle_update(update)

    except requests.exceptions.Timeout:
        continue
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
```

### GET /subscriptions — проверить подписки

```bash
curl -X GET "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN"
```

---

## 10. Webhooks

### Настройка — POST /subscriptions

```bash
curl -X POST "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook/max",
    "update_types": [
      "message_created",
      "message_callback",
      "bot_started"
    ]
  }'
```

**Требования:**
- Только **HTTPS** (самоподписанные сертификаты допускаются)
- Сервер должен отвечать **200 OK** на входящие POST
- Одновременно активен только один режим (Webhook ИЛИ Long Polling)

### Удаление подписки — DELETE /subscriptions

```bash
curl -X DELETE "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN"
```

### Проверка подписки — GET /subscriptions

```bash
curl -X GET "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN"
```

### Пример обработки webhook (Python + FastAPI)

```python
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/webhook/max")
async def handle_webhook(request: Request):
    data = await request.json()
    update_type = data.get("update_type")

    if update_type == "message_created":
        message = data["message"]
        text = message["body"].get("text", "")
        chat_id = message["recipient"]["chat_id"]
        await process_message(chat_id, text)

    elif update_type == "message_callback":
        callback = data["callback"]
        payload = callback["payload"]
        callback_id = callback["callback_id"]
        await process_callback(callback_id, payload)

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

---

## 11. Состояния диалога (FSM)

### Простая FSM на словаре

```python
# Состояния пользователей
user_states = {}  # {user_id: {"state": "...", "data": {...}}}

STATES = {
    "START": "start",
    "CHOOSE_TOUR": "choose_tour",
    "ENTER_DATE": "enter_date",
    "ENTER_PEOPLE": "enter_people",
    "CONFIRM": "confirm",
}

def handle_update(update):
    if update["update_type"] == "message_created":
        user_id = update["message"]["sender"]["user_id"]
        chat_id = update["message"]["recipient"]["chat_id"]
        text = update["message"]["body"].get("text", "")

        state = user_states.get(user_id, {}).get("state", STATES["START"])

        if state == STATES["START"]:
            send_tour_menu(chat_id)
            user_states[user_id] = {"state": STATES["CHOOSE_TOUR"], "data": {}}

        elif state == STATES["ENTER_DATE"]:
            user_states[user_id]["data"]["date"] = text
            send_message(chat_id, "Сколько человек?")
            user_states[user_id]["state"] = STATES["ENTER_PEOPLE"]

        elif state == STATES["ENTER_PEOPLE"]:
            user_states[user_id]["data"]["people"] = int(text)
            data = user_states[user_id]["data"]
            send_confirmation(chat_id, data)
            user_states[user_id]["state"] = STATES["CONFIRM"]
```

Для продакшена рекомендуется хранить состояния в Redis или БД (не в памяти).

---

## 12. Визуальный конструктор ботов

Max предоставляет **no-code конструктор** для создания простых ботов без программирования.

### Возможности конструктора
- Drag & drop сценарии
- Автоответы на ключевые слова
- Кнопки и меню
- Отправка медиа
- Базовые условия

### Когда использовать конструктор
- FAQ-боты (часто задаваемые вопросы)
- Простые меню с кнопками
- Информационные рассылки

### Когда нужен код (Bot API)
- Интеграция с CRM/базами данных
- Сложная логика (FSM, расчёты)
- Работа с внешними API (платёжные системы)
- Высокие нагрузки

---

## 13. Rate Limits и ошибки

### Лимиты

| Параметр | Значение |
|----------|----------|
| Запросы к API | **30 RPS** (запросов в секунду) |
| Webhook-уведомления от Max | до 100 в секунду |
| Длина текста сообщения | 4000 символов |
| Кнопок в клавиатуре | до 210 (30 рядов x 7) |
| Размер фото | до 50 MB |
| Размер видео | до 2 GB |
| Размер файла | до 100 MB |

### Коды ошибок HTTP

| Код | Описание | Действие |
|-----|----------|----------|
| 200 | Успех | — |
| 400 | Неверный запрос | Проверить параметры |
| 401 | Неавторизован | Проверить токен |
| 403 | Доступ запрещён | Бот не в чате / нет прав |
| 404 | Не найдено | Чат/сообщение не существует |
| 429 | Слишком много запросов | Подождать, снизить частоту |
| 500 | Ошибка сервера | Повторить через 5 секунд |

### Обработка ошибок

```python
import time

def api_request(method, url, **kwargs):
    for attempt in range(3):
        resp = requests.request(method, url, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            time.sleep(2 ** attempt)  # exponential backoff
            continue
        elif resp.status_code >= 500:
            time.sleep(5)
            continue
        else:
            raise Exception(f"API error {resp.status_code}: {resp.text}")
    raise Exception("Max retries reached")
```

### Загрузка файлов — ошибка 400

При загрузке медиа файл обрабатывается асинхронно. Если файл ещё не обработан, отправка сообщения с этим вложением вернёт **400**. Решение — повторить запрос через 1-2 секунды.

---

## 14. Примеры для туризма ОАЭ

### Полноценный бот-каталог экскурсий

```python
import asyncio
import logging
from dataclasses import dataclass

# Каталог экскурсий
TOURS = {
    "safari": {
        "name": "Desert Safari",
        "price_usd": 80,
        "price_aed": 295,
        "duration": "6 часов",
        "description": "Джип-сафари, сэндбординг, катание на верблюдах, BBQ ужин",
    },
    "burj": {
        "name": "Burj Khalifa 124+125",
        "price_usd": 50,
        "price_aed": 185,
        "duration": "2 часа",
        "description": "Смотровая площадка At The Top, 124 и 125 этаж",
    },
    "yacht": {
        "name": "Yacht Tour",
        "price_usd": 200,
        "price_aed": 735,
        "duration": "2 часа",
        "description": "Аренда яхты, Dubai Marina, напитки включены",
    },
    "abudhabi": {
        "name": "Abu Dhabi Day Trip",
        "price_usd": 65,
        "price_aed": 240,
        "duration": "10 часов",
        "description": "Sheikh Zayed Mosque, Louvre, Corniche, обед",
    },
    "city": {
        "name": "Dubai City Tour",
        "price_usd": 60,
        "price_aed": 220,
        "duration": "4 часа",
        "description": "Old Dubai, Gold Souk, Jumeirah Mosque, Dubai Frame",
    },
}

def build_main_menu():
    """Главное меню бота"""
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": [
                [
                    {"type": "callback", "text": "Экскурсии", "payload": "menu_tours"},
                    {"type": "callback", "text": "Яхты", "payload": "menu_yachts"},
                ],
                [
                    {"type": "callback", "text": "Трансферы", "payload": "menu_transfers"},
                    {"type": "callback", "text": "Аренда авто", "payload": "menu_cars"},
                ],
                [
                    {"type": "callback", "text": "Контакты", "payload": "menu_contacts", "intent": "positive"},
                ],
            ]
        },
    }

def build_tour_detail(tour_key):
    """Детальная карточка экскурсии"""
    tour = TOURS[tour_key]
    text = (
        f"**{tour['name']}**\n\n"
        f"{tour['description']}\n\n"
        f"Длительность: {tour['duration']}\n"
        f"Цена: ${tour['price_usd']} / {tour['price_aed']} AED\n\n"
        f"Для бронирования нажмите кнопку ниже:"
    )
    keyboard = {
        "type": "inline_keyboard",
        "payload": {
            "buttons": [
                [
                    {"type": "callback", "text": "Забронировать", "payload": f"book_{tour_key}", "intent": "positive"},
                    {"type": "callback", "text": "Назад", "payload": "menu_tours"},
                ],
            ]
        },
    }
    return text, keyboard
```

### Шаблон приветственного сообщения

```python
WELCOME_TEXT = """Добро пожаловать в Dubai Tours!

Мы организуем лучшие экскурсии, яхт-туры и трансферы в ОАЭ.

Наши цены ниже, чем на кассе и у конкурентов.

Оплата: AED, USD, RUB (Сбер), KZT (Kaspi).

Выберите раздел:"""
```

### Обработка бронирования

```python
def handle_booking(user_id, chat_id, tour_key):
    """Начать процесс бронирования"""
    tour = TOURS[tour_key]
    user_states[user_id] = {
        "state": "enter_date",
        "data": {"tour": tour_key}
    }
    send_message(
        chat_id,
        f"Вы выбрали: {tour['name']}\n"
        f"Цена: ${tour['price_usd']}/чел.\n\n"
        f"Введите желаемую дату (например: 15.03.2026):"
    )
```

---

## 15. Деплой

### Python — с max-botapi-python

**Установка:**
```bash
pip install git+https://github.com/max-messenger/max-botapi-python.git
```

**Минимальный бот:**
```python
import asyncio
import logging
from max_botapi import Bot, Dispatcher
from max_botapi.types import MessageCreated

logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.bot_started()
async def on_start(event):
    await event.chat.send_text("Добро пожаловать в Dubai Tours Bot!")

@dp.message_created()
async def on_message(event: MessageCreated):
    text = event.message.body.text or ""
    if "цена" in text.lower() or "price" in text.lower():
        await event.message.answer("Desert Safari: $80\nBurj Khalifa: $50\nYacht: от $200")
    else:
        await event.message.answer("Напишите 'цена' для просмотра прайса")

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
```

### Node.js / TypeScript — с @maxhub/max-bot-api

**Установка:**
```bash
npm install @maxhub/max-bot-api
```

**Минимальный бот:**
```typescript
import { Bot, Keyboard, Context } from '@maxhub/max-bot-api';

const bot = new Bot('YOUR_TOKEN');
const dp = bot.dispatcher;

dp.botStarted((ctx: Context) => {
  ctx.reply('Добро пожаловать в Dubai Tours Bot!');
});

dp.messageCreated((ctx: Context) => {
  const text = ctx.message?.body?.text?.toLowerCase() || '';
  if (text.includes('цена') || text.includes('price')) {
    const keyboard = Keyboard.inlineKeyboard([
      [
        Keyboard.button.callback('Desert Safari $80', {payload: 'tour_safari'}),
        Keyboard.button.callback('Burj Khalifa $50', {payload: 'tour_burj'}),
      ],
      [
        Keyboard.button.callback('Yacht от $200', {payload: 'tour_yacht'}),
      ],
    ]);
    ctx.reply('Наши экскурсии:', {attachments: [keyboard]});
  } else {
    ctx.reply('Напишите "цена" для просмотра экскурсий');
  }
});

bot.startPolling();
```

### Go — с max-bot-api-client-go

```bash
go get github.com/max-messenger/max-bot-api-client-go
```

### Java — с max-bot-api-client-java

```xml
<dependency>
  <groupId>ru.max</groupId>
  <artifactId>max-bot-api-client-java</artifactId>
</dependency>
```

### PHP — с max-bot-api-client-php

```bash
composer require bushlanovdev/max-bot-api-client-php
```

### Деплой в продакшен

| Платформа | Стоимость | Особенности |
|-----------|-----------|-------------|
| VPS (Timeweb, Beget) | от 200 руб/мес | Полный контроль |
| Heroku | от $7/мес | Просто, но дороже |
| Railway | от $5/мес | Git deploy |
| Docker | — | Универсально |

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

---

## 16. Библиотеки и инструменты

### Официальные и верифицированные

| Язык | Библиотека | Ссылка |
|------|------------|--------|
| Python | max-botapi-python | github.com/max-messenger/max-botapi-python |
| TypeScript | @maxhub/max-bot-api | github.com/max-messenger/max-bot-api-client-ts |
| Go | max-bot-api-client-go | github.com/max-messenger/max-bot-api-client-go |
| Java | max-bot-api-client-java | github.com/max-messenger/max-bot-api-client-java |
| PHP | max-bot-api-client-php | github.com/BushlanovDev/max-bot-api-client-php |

### Сторонние

| Язык | Библиотека | Описание |
|------|------------|----------|
| Python | maxgram | Альтернативный клиент (github.com/KayumovRu/maxgram) |
| Python | aiomax | Async-обёртка |

### Инструменты

| Инструмент | Описание |
|------------|----------|
| @MasterBot | Регистрация и управление ботами в Max |
| No-code конструктор | Визуальный конструктор ботов (встроен в Max) |
| BotMother | Мультиплатформенный конструктор (поддерживает Max) |
| BotHelp | Платформа для чат-ботов (поддерживает Max) |

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы по Max Bot API |
| references/troubleshooting.md | Решение типичных проблем |
| references/cheatsheet.md | Шпаргалка: все endpoints, типы, лимиты |
