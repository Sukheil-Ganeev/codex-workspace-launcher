---
name: viber-bot-справочник
description: "Production-ready руководство по Viber Bot API для туристического бизнеса ОАЭ. REST API, клавиатуры, Rich Media, broadcast, карусели. Используй когда нужно создать бота в Viber."
---
# Viber Bot API — Полный справочник

## 1. Quick Start

### Регистрация бота

С 5 февраля 2024 года боты в Viber создаются **только на коммерческих условиях**. Порядок:

1. **Подать заявку** — через [Viber for Business](https://www.forbusiness.viber.com/en/chatbots/) или через верифицированного партнёра Rakuten Viber
2. **Пройти квалификацию** — Viber проверяет бизнес
3. **Подписать контракт** — согласие с условиями и ценообразованием
4. **Получить доступ** — в Viber Admin Panel появится раздел управления ботом
5. **Настроить бота** — имя, аватар, уникальный URI, категория, описание
6. **Получить токен** — More > Settings > Bots > Edit Info > Your App Key

### Коммерческая модель (2025)

| Параметр | Значение |
|----------|----------|
| Публикация бота | Бесплатно |
| Welcome message | Бесплатно (1 сообщение до подписки) |
| Бесплатный лимит | 10,000 chatbot-initiated сообщений/месяц |
| Сверх лимита | Оплата за каждое доставленное сообщение |
| Тариф | Зависит от страны телефона подписчика |
| Сообщения от пользователя | Бесплатно для подписчика |

### Первое сообщение (curl)

```bash
curl -X POST https://chatapi.viber.com/pa/send_message \
  -H "X-Viber-Auth-Token: YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "USER_ID",
    "min_api_version": 7,
    "type": "text",
    "text": "Добро пожаловать в Dubai Tours! Чем могу помочь?"
  }'
```

### Установка webhook

```bash
curl -X POST https://chatapi.viber.com/pa/set_webhook \
  -H "X-Viber-Auth-Token: YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/viber/webhook",
    "event_types": [
      "delivered", "seen", "failed",
      "subscribed", "unsubscribed",
      "conversation_started", "message"
    ],
    "send_name": true,
    "send_photo": true
  }'
```

---

## 2. Архитектура

### Принципиальная схема

```
Пользователь Viber
      |
      v
Viber Server (chatapi.viber.com)
      |
      v (HTTPS POST — webhook callback)
Ваш сервер (HTTPS обязателен)
      |
      v (HTTPS POST — REST API)
chatapi.viber.com/pa/{method}
```

### Ключевые особенности

- **Только webhook** — Viber НЕ поддерживает long polling (в отличие от Telegram)
- **REST API** — все запросы через `https://chatapi.viber.com/pa/`
- **HTTPS обязателен** — для webhook нужен доверенный SSL-сертификат (не self-signed)
- **JSON** — все запросы и ответы в формате JSON
- **Webhook-first** — сначала set_webhook, потом всё остальное

### Base URL

```
https://chatapi.viber.com/pa/
```

### Доступные методы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| set_webhook | `/pa/set_webhook` | Установка webhook URL |
| send_message | `/pa/send_message` | Отправка сообщения пользователю |
| broadcast_message | `/pa/broadcast_message` | Рассылка подписчикам |
| get_account_info | `/pa/get_account_info` | Информация о боте |
| get_user_details | `/pa/get_user_details` | Данные пользователя |
| get_online | `/pa/get_online` | Онлайн-статус подписчиков |
| post | `/pa/post` | Публикация в публичный аккаунт |

---

## 3. Аутентификация

### Auth Token

Каждый запрос к API должен содержать HTTP-заголовок:

```
X-Viber-Auth-Token: YOUR_AUTH_TOKEN
```

| Параметр | Описание |
|----------|----------|
| Где получить | Viber Admin Panel > Bots > Edit Info > Your App Key |
| Формат | Строка (hex) |
| Область действия | Один бот = один токен |
| Безопасность | Хранить в переменных окружения, НЕ в коде |

### Проверка подлинности webhook

Viber подписывает каждый callback хешем HMAC SHA256. Заголовок:

```
X-Viber-Content-Signature: <HMAC-SHA256>
```

Проверка (Python):

```python
import hashlib
import hmac

def verify_signature(request_data, signature, auth_token):
    calculated = hmac.new(
        auth_token.encode('utf-8'),
        request_data,
        hashlib.sha256
    ).hexdigest()
    return calculated == signature
```

---

## 4. Webhook

### Установка (set_webhook)

```json
POST https://chatapi.viber.com/pa/set_webhook

{
  "url": "https://your-server.com/viber/webhook",
  "event_types": ["delivered", "seen", "failed", "subscribed",
                   "unsubscribed", "conversation_started", "message"],
  "send_name": true,
  "send_photo": true
}
```

**Требования к URL:**
- Только HTTPS
- Доверенный SSL-сертификат (CA-signed, НЕ self-signed)
- Сервер должен отвечать HTTP 200 на каждый callback

### Типы событий (callback types)

| Событие | Когда срабатывает |
|---------|-------------------|
| `message` | Пользователь отправил сообщение боту |
| `subscribed` | Пользователь подписался на бота |
| `unsubscribed` | Пользователь отписался |
| `conversation_started` | Пользователь открыл чат с ботом впервые |
| `delivered` | Сообщение доставлено на устройство |
| `seen` | Сообщение прочитано |
| `failed` | Ошибка доставки |
| `webhook` | Подтверждение установки webhook (приходит один раз) |

### Структура callback (message)

```json
{
  "event": "message",
  "timestamp": 1707123456789,
  "chat_hostname": "SN-CHAT-01_",
  "message_token": 5912661846655238145,
  "sender": {
    "id": "01234567890A=",
    "name": "Турист Иван",
    "avatar": "https://...",
    "language": "ru",
    "country": "RU",
    "api_version": 8
  },
  "message": {
    "text": "Хочу экскурсию по Дубаю",
    "type": "text",
    "tracking_data": "state:main_menu"
  }
}
```

### Структура callback (conversation_started)

```json
{
  "event": "conversation_started",
  "timestamp": 1707123456789,
  "type": "open",
  "context": "from_instagram_ad",
  "user": {
    "id": "01234567890A=",
    "name": "Турист Мария",
    "avatar": "https://...",
    "language": "ru",
    "country": "KZ"
  },
  "subscribed": false
}
```

**Важно:** `context` появляется только при переходе через deep link с параметром context. Событие `subscribed` удаляет весь tracking_data и context.

---

## 5. Отправка сообщений (send_message)

### Базовая структура

```json
POST https://chatapi.viber.com/pa/send_message

{
  "receiver": "USER_ID",
  "min_api_version": 7,
  "sender": {
    "name": "Dubai Tours Bot",
    "avatar": "https://your-server.com/bot-avatar.jpg"
  },
  "tracking_data": "state:catalog",
  "type": "text",
  "text": "Выберите категорию экскурсий:"
}
```

### Типы сообщений

| Тип | type | Обязательные поля | Описание |
|-----|------|-------------------|----------|
| Текст | `text` | `text` | Текстовое сообщение (до 7000 символов) |
| Картинка | `picture` | `text`, `media` | Изображение с подписью |
| Видео | `video` | `media`, `size` | Видео (до 26 МБ, только .mp4) |
| Файл | `file` | `media`, `size`, `file_name` | Документ (до 50 МБ) |
| Контакт | `contact` | `contact.name`, `contact.phone_number` | Контактная карточка |
| Локация | `location` | `location.lat`, `location.lon` | Точка на карте |
| Стикер | `sticker` | `sticker_id` | Viber-стикер по ID |
| URL | `url` | `media` | Ссылка с превью |
| Rich Media | `rich_media` | `rich_media` | Карусель (см. раздел 7) |

### Пример: картинка

```json
{
  "receiver": "USER_ID",
  "min_api_version": 7,
  "type": "picture",
  "text": "Desert Safari - незабываемые впечатления!",
  "media": "https://your-server.com/images/desert-safari.jpg",
  "thumbnail": "https://your-server.com/images/desert-safari-thumb.jpg"
}
```

### Пример: локация (офис в Дубае)

```json
{
  "receiver": "USER_ID",
  "min_api_version": 7,
  "type": "location",
  "location": {
    "lat": 25.0982,
    "lon": 55.1780
  }
}
```

### Пример: контакт

```json
{
  "receiver": "USER_ID",
  "min_api_version": 7,
  "type": "contact",
  "contact": {
    "name": "Dubai Tours Support",
    "phone_number": "+971501234567"
  }
}
```

---

## 6. Клавиатуры (Keyboard)

### Структура клавиатуры

Клавиатура — это JSON-объект, который прикрепляется к **любому** типу сообщения. Сетка: **6 колонок**, кнопка от 1 до 6 колонок в ширину.

```json
{
  "receiver": "USER_ID",
  "min_api_version": 7,
  "type": "text",
  "text": "Выберите категорию:",
  "keyboard": {
    "Type": "keyboard",
    "DefaultHeight": false,
    "BgColor": "#FFFFFF",
    "Buttons": [
      {
        "Columns": 3,
        "Rows": 1,
        "BgColor": "#2db9b9",
        "ActionType": "reply",
        "ActionBody": "excursions",
        "Text": "<font color=\"#FFFFFF\"><b>Экскурсии</b></font>",
        "TextSize": "regular",
        "TextHAlign": "center",
        "TextVAlign": "middle"
      },
      {
        "Columns": 3,
        "Rows": 1,
        "BgColor": "#e6a019",
        "ActionType": "reply",
        "ActionBody": "tickets",
        "Text": "<font color=\"#FFFFFF\"><b>Билеты</b></font>",
        "TextSize": "regular",
        "TextHAlign": "center",
        "TextVAlign": "middle"
      },
      {
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#7c4dff",
        "ActionType": "reply",
        "ActionBody": "contact_us",
        "Text": "<font color=\"#FFFFFF\"><b>Связаться с нами</b></font>",
        "TextSize": "regular",
        "TextHAlign": "center",
        "TextVAlign": "middle"
      }
    ]
  }
}
```

### Свойства кнопок

| Свойство | Тип | Описание |
|----------|-----|----------|
| `Columns` | int (1-6) | Ширина кнопки (из 6 колонок) |
| `Rows` | int (1-7) | Высота кнопки |
| `BgColor` | string | Цвет фона (#HEX) |
| `BgMedia` | string | URL фонового изображения |
| `BgMediaType` | string | `picture` или `gif` |
| `ActionType` | string | `reply`, `open-url`, `none` |
| `ActionBody` | string | Значение действия |
| `Text` | string | HTML-текст на кнопке |
| `TextSize` | string | `small`, `regular`, `large` |
| `TextHAlign` | string | `left`, `center`, `right` |
| `TextVAlign` | string | `top`, `middle`, `bottom` |
| `Image` | string | URL иконки на кнопке |
| `Silent` | bool | Не отправлять reply в чат |

### ActionType — типы действий

| ActionType | Поведение |
|------------|-----------|
| `reply` | Отправляет ActionBody как текстовое сообщение боту |
| `open-url` | Открывает URL из ActionBody в браузере |
| `none` | Никакого действия (декоративная кнопка) |
| `location-picker` | Открывает выбор геолокации |
| `share-phone` | Отправляет номер телефона пользователя |

### HTML в тексте кнопок

Viber поддерживает HTML-разметку в `Text`:

```html
<font color="#FFFFFF" size="18"><b>Забронировать</b></font>
<br><font color="#CCCCCC" size="14">Desert Safari</font>
```

Поддерживаемые теги: `<b>`, `<i>`, `<u>`, `<s>`, `<font>`, `<br>`.

---

## 7. Rich Media (Карусели)

### Концепция

Rich Media — карусельный формат сообщения. Пользователь листает карточки горизонтально. Каждая карточка — набор кнопок в группе.

**Ограничения:**
- Поддержка: Viber 6.7+
- Максимум 7 строк на кнопку
- Пересылка не поддерживается
- `location-picker` и `share-phone` НЕ работают в Rich Media

### Структура

```json
{
  "receiver": "USER_ID",
  "min_api_version": 7,
  "type": "rich_media",
  "rich_media": {
    "Type": "rich_media",
    "ButtonsGroupColumns": 6,
    "ButtonsGroupRows": 7,
    "BgColor": "#FFFFFF",
    "Buttons": [
      {
        "Columns": 6,
        "Rows": 3,
        "ActionType": "open-url",
        "ActionBody": "https://your-site.com/desert-safari",
        "Image": "https://your-server.com/images/desert-safari.jpg"
      },
      {
        "Columns": 6,
        "Rows": 2,
        "ActionType": "none",
        "ActionBody": "none",
        "Text": "<font color=\"#323232\"><b>Desert Safari</b></font><br><font color=\"#777777\">Джип, BBQ-ужин, шоу</font><br><font color=\"#2db9b9\"><b>250 AED</b></font>",
        "TextSize": "regular",
        "TextVAlign": "middle",
        "TextHAlign": "left"
      },
      {
        "Columns": 6,
        "Rows": 1,
        "ActionType": "reply",
        "ActionBody": "book_desert_safari",
        "Text": "<font color=\"#FFFFFF\"><b>Забронировать</b></font>",
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "middle",
        "BgColor": "#2db9b9"
      },
      {
        "Columns": 6,
        "Rows": 3,
        "ActionType": "open-url",
        "ActionBody": "https://your-site.com/city-tour",
        "Image": "https://your-server.com/images/city-tour.jpg"
      },
      {
        "Columns": 6,
        "Rows": 2,
        "ActionType": "none",
        "ActionBody": "none",
        "Text": "<font color=\"#323232\"><b>City Tour Dubai</b></font><br><font color=\"#777777\">Бурдж Халифа, Марина, Old Dubai</font><br><font color=\"#2db9b9\"><b>200 AED</b></font>",
        "TextSize": "regular",
        "TextVAlign": "middle",
        "TextHAlign": "left"
      },
      {
        "Columns": 6,
        "Rows": 1,
        "ActionType": "reply",
        "ActionBody": "book_city_tour",
        "Text": "<font color=\"#FFFFFF\"><b>Забронировать</b></font>",
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "middle",
        "BgColor": "#2db9b9"
      }
    ]
  }
}
```

**Логика группировки:** `ButtonsGroupRows` = 7 означает, что каждые 7 строк (3 + 2 + 1 + 1 padding или 3 + 2 + 2) — отдельная карточка в карусели. Viber автоматически делит массив Buttons на группы.

---

## 8. Broadcast (Рассылки)

### Отправка рассылки

```json
POST https://chatapi.viber.com/pa/broadcast_message

{
  "broadcast_list": ["USER_ID_1", "USER_ID_2", "USER_ID_3"],
  "min_api_version": 7,
  "sender": {
    "name": "Dubai Tours",
    "avatar": "https://your-server.com/avatar.jpg"
  },
  "type": "text",
  "text": "Новогодняя акция! Скидка 20% на все экскурсии до 15 января!"
}
```

### Лимиты broadcast

| Параметр | Значение |
|----------|----------|
| Получателей на запрос | Максимум **300** подписчиков |
| Rate limit | **500 запросов** за 10 секунд |
| Размер сообщения | Максимум **30 КБ** |
| Получатели | Только **подписанные** пользователи |

### Рассылка Rich Media (каталог экскурсий)

```json
{
  "broadcast_list": ["USER_ID_1", "USER_ID_2"],
  "min_api_version": 7,
  "type": "rich_media",
  "rich_media": {
    "Type": "rich_media",
    "ButtonsGroupColumns": 6,
    "ButtonsGroupRows": 6,
    "Buttons": [
      {
        "Columns": 6, "Rows": 3,
        "ActionType": "open-url",
        "ActionBody": "https://your-site.com/winter-special",
        "Image": "https://your-server.com/winter-promo.jpg"
      },
      {
        "Columns": 6, "Rows": 2,
        "ActionType": "none", "ActionBody": "none",
        "Text": "<b>Зимний спецпредложение!</b><br>Desert Safari + City Tour<br><b>400 AED</b> <s>500 AED</s>"
      },
      {
        "Columns": 6, "Rows": 1,
        "ActionType": "reply",
        "ActionBody": "book_winter_special",
        "Text": "<font color=\"#FFF\"><b>Забронировать со скидкой</b></font>",
        "BgColor": "#FF6B35"
      }
    ]
  }
}
```

---

## 9. Conversation Started (Приветственное сообщение)

### Механизм

Когда пользователь **впервые** открывает чат с ботом:

1. Viber отправляет `conversation_started` callback на webhook
2. Бот должен ответить в течение **5 минут** через `send_message`
3. Пользователь ещё **НЕ подписан** — он видит сообщение, но бот не может инициировать переписку
4. Пользователь подписывается, когда **отправляет первое сообщение** или нажимает кнопку

### Welcome Message (Python)

```python
@app.route('/viber/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if data['event'] == 'conversation_started':
        user = data['user']
        context = data.get('context', '')

        # Приветственное сообщение с клавиатурой
        welcome = {
            "receiver": user['id'],
            "min_api_version": 7,
            "type": "text",
            "text": f"Здравствуйте, {user['name']}! Добро пожаловать в Dubai Tours!\n\nМы организуем экскурсии и продаём билеты в парки ОАЭ по лучшим ценам.",
            "keyboard": {
                "Type": "keyboard",
                "DefaultHeight": false,
                "Buttons": [
                    {
                        "Columns": 3, "Rows": 1,
                        "ActionType": "reply",
                        "ActionBody": "catalog",
                        "Text": "<b>Каталог</b>",
                        "BgColor": "#2db9b9"
                    },
                    {
                        "Columns": 3, "Rows": 1,
                        "ActionType": "reply",
                        "ActionBody": "contact",
                        "Text": "<b>Связаться</b>",
                        "BgColor": "#e6a019"
                    }
                ]
            }
        }

        # Отправляем welcome
        send_message(welcome)

    return Response(status=200)
```

### Deep Links с контекстом

Формат: `viber://pa?chatURI=YOUR_BOT_URI&context=YOUR_CONTEXT`

Примеры для маркетинга:

```
viber://pa?chatURI=dubaitorurs&context=instagram_ad
viber://pa?chatURI=dubaitours&context=website_header
viber://pa?chatURI=dubaitours&context=safari_promo
```

Контекст приходит в `conversation_started` callback → позволяет отслеживать источник трафика.

**Ограничения:** работает только на Android и iOS (НЕ Desktop).

---

## 10. User Details и Online Status

### get_user_details

```json
POST https://chatapi.viber.com/pa/get_user_details

{
  "id": "USER_ID"
}
```

**Ответ:**

```json
{
  "status": 0,
  "status_message": "ok",
  "user": {
    "id": "01234567890A=",
    "name": "Турист Иван",
    "avatar": "https://...",
    "language": "ru",
    "country": "RU",
    "primary_device_os": "Android 14",
    "api_version": 8,
    "viber_version": "21.5.0",
    "mcc": 250,
    "mnc": 1,
    "device_type": "Samsung Galaxy S24"
  }
}
```

**Ограничение:** максимум **2 запроса за 12 часов** на каждый user ID.

### get_online

```json
POST https://chatapi.viber.com/pa/get_online

{
  "ids": ["USER_ID_1", "USER_ID_2"]
}
```

**Ответ:**

```json
{
  "status": 0,
  "users": [
    {
      "id": "USER_ID_1",
      "online_status": 0,
      "online_status_message": "online"
    },
    {
      "id": "USER_ID_2",
      "online_status": 1,
      "online_status_message": "offline",
      "last_online": 1707123456789
    }
  ]
}
```

**Статусы:** 0 = online, 1 = offline, 2 = undisclosed, 3 = internal error, 4 = not a subscriber.

---

## 11. Состояния диалога (tracking_data — FSM)

### Уникальная фича Viber

`tracking_data` — это строка (до 4000 символов), встроенная в КАЖДОЕ сообщение. Viber автоматически возвращает её в callback при ответе пользователя. Это **встроенный механизм состояний** без внешней БД.

### Как работает

```
Бот отправляет сообщение с tracking_data: "state:choose_date|tour:safari"
    ↓
Пользователь нажимает кнопку
    ↓
Viber callback приходит с тем же tracking_data: "state:choose_date|tour:safari"
    ↓
Бот знает текущее состояние и обрабатывает ответ
```

### Реализация FSM (Python)

```python
import json

def handle_message(data):
    sender_id = data['sender']['id']
    text = data['message']['text']
    tracking = data['message'].get('tracking_data', '')

    # Парсим состояние
    state = parse_tracking(tracking)

    if state.get('step') == 'choose_tour':
        # Пользователь выбирает экскурсию
        if text == 'desert_safari':
            send_date_picker(sender_id, tour='desert_safari')
        elif text == 'city_tour':
            send_date_picker(sender_id, tour='city_tour')

    elif state.get('step') == 'choose_date':
        # Пользователь выбирает дату
        tour = state.get('tour')
        send_confirmation(sender_id, tour=tour, date=text)

    elif state.get('step') == 'confirm':
        # Подтверждение бронирования
        if text == 'yes':
            create_booking(sender_id, state)
            send_success(sender_id)
        else:
            send_main_menu(sender_id)

    else:
        # Главное меню
        send_main_menu(sender_id)

def send_date_picker(receiver, tour):
    message = {
        "receiver": receiver,
        "min_api_version": 7,
        "type": "text",
        "text": "Выберите дату:",
        "tracking_data": json.dumps({
            "step": "choose_date",
            "tour": tour
        }),
        "keyboard": {
            "Type": "keyboard",
            "Buttons": [
                {"Columns": 3, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "today", "Text": "<b>Сегодня</b>",
                 "BgColor": "#2db9b9"},
                {"Columns": 3, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "tomorrow", "Text": "<b>Завтра</b>",
                 "BgColor": "#2db9b9"}
            ]
        }
    }
    send_to_viber(message)

def parse_tracking(tracking_str):
    try:
        return json.loads(tracking_str)
    except (json.JSONDecodeError, TypeError):
        return {}
```

### Важные нюансы tracking_data

- Максимум **4000 символов**
- Событие `subscribed` **удаляет** все tracking_data (сброс состояния)
- JSON-строка — оптимальный формат (удобный парсинг)
- Для сложных сценариев — комбинируй с внешней БД (Redis/PostgreSQL)

---

## 12. Account Info

### get_account_info

```json
POST https://chatapi.viber.com/pa/get_account_info

{}
```

**Ответ:**

```json
{
  "status": 0,
  "status_message": "ok",
  "id": "pa:1234567890",
  "name": "Dubai Tours Bot",
  "uri": "dubaitours",
  "icon": "https://...",
  "background": "https://...",
  "category": "Travel & Tourism",
  "subcategory": "Tours & Sightseeing",
  "location": {
    "lat": 25.0982,
    "lon": 55.1780
  },
  "country": "AE",
  "webhook": "https://your-server.com/viber/webhook",
  "event_types": ["delivered", "seen", "message"],
  "subscribers_count": 1500,
  "members": [
    {
      "id": "ADMIN_ID",
      "name": "Сухейль",
      "avatar": "https://...",
      "role": "admin"
    }
  ]
}
```

**Применение:** проверка webhook, количество подписчиков, диагностика.

---

## 13. Rate Limits

### Лимиты API

| Метод | Лимит |
|-------|-------|
| `send_message` | Без жёсткого лимита (fair use) |
| `broadcast_message` | 500 запросов / 10 секунд |
| `broadcast_message` (получатели) | 300 подписчиков / запрос |
| `broadcast_message` (размер) | 30 КБ / сообщение |
| `get_user_details` | 2 запроса / 12 часов / user ID |
| `get_online` | Без жёсткого лимита |
| `get_account_info` | Без жёсткого лимита |

### Бесплатные сообщения (коммерческая модель)

| Тип | Лимит |
|-----|-------|
| Welcome message | Бесплатно (1 на пользователя) |
| Bot-initiated | 10,000 / месяц бесплатно |
| User-initiated ответы | Бесплатно |
| Сверх лимита | Оплата по тарифу страны |

### Рекомендации

- Собирай подписчиков в локальную БД (нет API для получения списка всех подписчиков)
- Для рассылки >300 человек — разбивай на батчи по 300
- Между батчами — пауза для соблюдения rate limit
- Мониторь `failed` callback для очистки невалидных ID

---

## 14. Примеры для туризма ОАЭ

### Каталог экскурсий (Rich Media карусель)

```python
def send_tour_catalog(receiver_id):
    tours = [
        {
            "name": "Desert Safari Premium",
            "desc": "Джип 4x4, сэндбординг, BBQ-ужин, шоу",
            "price": "250 AED",
            "image": "https://cdn.example.com/desert-safari.jpg",
            "action": "book_desert_safari"
        },
        {
            "name": "Dubai City Tour",
            "desc": "Burj Khalifa, Dubai Mall, Marina, Old Dubai",
            "price": "200 AED",
            "image": "https://cdn.example.com/city-tour.jpg",
            "action": "book_city_tour"
        },
        {
            "name": "Abu Dhabi Full Day",
            "desc": "Sheikh Zayed Mosque, Louvre, Yas Island",
            "price": "300 AED",
            "image": "https://cdn.example.com/abu-dhabi.jpg",
            "action": "book_abu_dhabi"
        },
        {
            "name": "Burj Khalifa Tickets",
            "desc": "124+125 этаж, приоритетный вход",
            "price": "220 AED",
            "image": "https://cdn.example.com/burj-khalifa.jpg",
            "action": "book_burj_khalifa"
        }
    ]

    buttons = []
    for tour in tours:
        # Изображение (3 строки)
        buttons.append({
            "Columns": 6, "Rows": 3,
            "ActionType": "open-url",
            "ActionBody": f"https://your-site.com/{tour['action']}",
            "Image": tour["image"]
        })
        # Описание (2 строки)
        buttons.append({
            "Columns": 6, "Rows": 2,
            "ActionType": "none", "ActionBody": "none",
            "Text": f"<b>{tour['name']}</b><br>"
                    f"<font color='#777'>{tour['desc']}</font><br>"
                    f"<font color='#2db9b9'><b>{tour['price']}</b></font>",
            "TextVAlign": "middle", "TextHAlign": "left"
        })
        # Кнопка бронирования (1 строка)
        buttons.append({
            "Columns": 6, "Rows": 1,
            "ActionType": "reply",
            "ActionBody": tour["action"],
            "Text": "<font color='#FFF'><b>Забронировать</b></font>",
            "BgColor": "#2db9b9",
            "TextHAlign": "center", "TextVAlign": "middle"
        })

    message = {
        "receiver": receiver_id,
        "min_api_version": 7,
        "type": "rich_media",
        "rich_media": {
            "Type": "rich_media",
            "ButtonsGroupColumns": 6,
            "ButtonsGroupRows": 6,
            "BgColor": "#FFFFFF",
            "Buttons": buttons
        }
    }
    send_to_viber(message)
```

### Сценарий бронирования (FSM через tracking_data)

```python
BOOKING_FLOW = {
    "start": {
        "text": "Какую экскурсию хотите забронировать?",
        "next": "choose_date",
        "options": ["Desert Safari", "City Tour", "Abu Dhabi", "Burj Khalifa"]
    },
    "choose_date": {
        "text": "На какую дату?",
        "next": "choose_people",
        "options": ["Сегодня", "Завтра", "Выбрать дату"]
    },
    "choose_people": {
        "text": "Сколько человек?",
        "next": "confirm",
        "options": ["1", "2", "3-4", "5+"]
    },
    "confirm": {
        "text": "Подтвердите бронирование:\n{summary}\n\nВсё верно?",
        "next": "done",
        "options": ["Подтвердить", "Изменить", "Отмена"]
    }
}

def process_booking(sender_id, text, tracking_data):
    state = json.loads(tracking_data) if tracking_data else {"step": "start"}
    step = state["step"]

    if step == "start":
        state["tour"] = text
        state["step"] = "choose_date"
    elif step == "choose_date":
        state["date"] = text
        state["step"] = "choose_people"
    elif step == "choose_people":
        state["people"] = text
        state["step"] = "confirm"
    elif step == "confirm":
        if text == "Подтвердить":
            # Создать бронирование
            notify_manager(state)
            send_text(sender_id, "Бронирование принято! Менеджер свяжется с вами в течение 15 минут.", "")
            return
        elif text == "Отмена":
            send_main_menu(sender_id)
            return

    flow = BOOKING_FLOW[state["step"]]
    buttons = [
        {
            "Columns": 3 if len(flow["options"]) > 2 else 6,
            "Rows": 1,
            "ActionType": "reply",
            "ActionBody": opt,
            "Text": f"<b>{opt}</b>",
            "BgColor": "#2db9b9"
        }
        for opt in flow["options"]
    ]

    text_msg = flow["text"]
    if "{summary}" in text_msg:
        text_msg = text_msg.format(summary=format_summary(state))

    send_keyboard_message(sender_id, text_msg, buttons, json.dumps(state))
```

### Welcome Message для туристов

```python
def send_welcome(user):
    lang = user.get('language', 'en')
    name = user.get('name', 'Гость')

    if lang == 'ru':
        text = (f"Здравствуйте, {name}!\n\n"
                "Dubai Tours — экскурсии и билеты по ОАЭ.\n"
                "Цены ниже, чем на кассе и у конкурентов.\n\n"
                "Что вас интересует?")
    else:
        text = (f"Hello, {name}!\n\n"
                "Dubai Tours — excursions & tickets across UAE.\n"
                "Best prices guaranteed.\n\n"
                "What are you looking for?")

    message = {
        "receiver": user['id'],
        "min_api_version": 7,
        "type": "text",
        "text": text,
        "keyboard": {
            "Type": "keyboard",
            "DefaultHeight": False,
            "Buttons": [
                {"Columns": 3, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "catalog_excursions",
                 "Text": "<b>Экскурсии</b>", "BgColor": "#2db9b9"},
                {"Columns": 3, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "catalog_tickets",
                 "Text": "<b>Билеты</b>", "BgColor": "#e6a019"},
                {"Columns": 3, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "catalog_yachts",
                 "Text": "<b>Яхты</b>", "BgColor": "#7c4dff"},
                {"Columns": 3, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "catalog_cars",
                 "Text": "<b>Авто</b>", "BgColor": "#FF6B35"},
                {"Columns": 6, "Rows": 1, "ActionType": "reply",
                 "ActionBody": "contact_manager",
                 "Text": "<b>Связаться с менеджером</b>", "BgColor": "#333333"}
            ]
        }
    }
    send_to_viber(message)
```

---

## 15. Деплой

### Node.js (Express + viber-bot)

```javascript
const express = require('express');
const ViberBot = require('viber-bot').Bot;
const BotEvents = require('viber-bot').Events;
const TextMessage = require('viber-bot').Message.Text;

const app = express();
const PORT = process.env.PORT || 8080;

const bot = new ViberBot({
    authToken: process.env.VIBER_AUTH_TOKEN,
    name: "Dubai Tours",
    avatar: "https://your-server.com/avatar.jpg"
});

// Обработка сообщений
bot.on(BotEvents.MESSAGE_RECEIVED, (message, response) => {
    const text = message.text;
    const trackingData = message.trackingData;

    // Логика обработки
    if (text === 'catalog') {
        sendCatalog(response);
    } else {
        response.send(new TextMessage('Напишите "catalog" для просмотра экскурсий'));
    }
});

// Conversation started
bot.on(BotEvents.CONVERSATION_STARTED, (response, isSubscribed, context) => {
    response.send(new TextMessage('Добро пожаловать в Dubai Tours!'));
});

// Subscribed
bot.on(BotEvents.SUBSCRIBED, (response) => {
    response.send(new TextMessage('Спасибо за подписку!'));
});

// Middleware
app.use('/viber/webhook', bot.middleware());

// Запуск
app.listen(PORT, () => {
    bot.setWebhook(`https://your-server.com/viber/webhook`);
    console.log(`Viber bot running on port ${PORT}`);
});
```

### Python (Flask + viberbot)

```python
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberConversationStartedRequest,
    ViberSubscribedRequest
)
import os
import json
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

viber = Api(BotConfiguration(
    name='Dubai Tours',
    avatar='https://your-server.com/avatar.jpg',
    auth_token=os.environ['VIBER_AUTH_TOKEN']
))

@app.route('/viber/webhook', methods=['POST'])
def incoming():
    logger.debug(f"Received: {request.get_data()}")

    # Проверка подписи
    if not viber.verify_signature(
        request.get_data(),
        request.headers.get('X-Viber-Content-Signature')
    ):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        sender_id = viber_request.sender.id
        text = message.text if hasattr(message, 'text') else ''
        tracking = message.tracking_data or ''

        handle_message(sender_id, text, tracking)

    elif isinstance(viber_request, ViberConversationStartedRequest):
        user = viber_request.user
        viber.send_messages(user.id, [
            TextMessage(text=f"Добро пожаловать, {user.name}!")
        ])

    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Спасибо за подписку! Каталог: /catalog")
        ])

    return Response(status=200)

def handle_message(sender_id, text, tracking_data):
    # Основная логика бота
    if text.lower() in ['catalog', 'каталог', 'start']:
        send_catalog(sender_id)
    elif text.lower() in ['help', 'помощь']:
        viber.send_messages(sender_id, [
            TextMessage(text="Напишите 'каталог' для просмотра экскурсий")
        ])
    else:
        process_with_tracking(sender_id, text, tracking_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Serverless (AWS Lambda + API Gateway)

```python
import json
import os
import requests

VIBER_TOKEN = os.environ['VIBER_AUTH_TOKEN']
API_URL = 'https://chatapi.viber.com/pa'

def lambda_handler(event, context):
    body = json.loads(event['body'])
    event_type = body.get('event')

    if event_type == 'webhook':
        return {'statusCode': 200, 'body': 'ok'}

    if event_type == 'message':
        sender_id = body['sender']['id']
        text = body['message'].get('text', '')
        tracking = body['message'].get('tracking_data', '')

        handle_message(sender_id, text, tracking)

    elif event_type == 'conversation_started':
        user_id = body['user']['id']
        send_welcome(user_id, body['user'])

    return {'statusCode': 200, 'body': 'ok'}

def send_viber_message(payload):
    headers = {
        'X-Viber-Auth-Token': VIBER_TOKEN,
        'Content-Type': 'application/json'
    }
    requests.post(f'{API_URL}/send_message',
                  json=payload, headers=headers)
```

---

## 16. Библиотеки

### Официальные SDK

| Библиотека | Язык | Установка | GitHub |
|------------|------|-----------|--------|
| `viber-bot` | Node.js | `npm install viber-bot` | [Viber/viber-bot-node](https://github.com/Viber/viber-bot-node) |
| `viberbot` | Python | `pip install viberbot` | [Viber/viber-bot-python](https://github.com/Viber/viber-bot-python) |
| Viber Java Bot API | Java | Maven | [Viber/viber-bot-java](https://github.com/Viber/viber-bot-java) |

### Node.js — основные классы

```javascript
const ViberBot = require('viber-bot').Bot;
const BotEvents = require('viber-bot').Events;

// Типы сообщений
const TextMessage = require('viber-bot').Message.Text;
const PictureMessage = require('viber-bot').Message.Picture;
const VideoMessage = require('viber-bot').Message.Video;
const FileMessage = require('viber-bot').Message.File;
const ContactMessage = require('viber-bot').Message.Contact;
const LocationMessage = require('viber-bot').Message.Location;
const StickerMessage = require('viber-bot').Message.Sticker;
const UrlMessage = require('viber-bot').Message.Url;
const RichMediaMessage = require('viber-bot').Message.RichMedia;
const KeyboardMessage = require('viber-bot').Message.Keyboard;

// События
BotEvents.MESSAGE_RECEIVED
BotEvents.SUBSCRIBED
BotEvents.UNSUBSCRIBED
BotEvents.CONVERSATION_STARTED
BotEvents.ERROR
```

### Python — основные классы

```python
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

# Типы сообщений
from viberbot.api.messages import (
    TextMessage,
    PictureMessage,
    VideoMessage,
    FileMessage,
    ContactMessage,
    LocationMessage,
    StickerMessage,
    URLMessage,
    RichMediaMessage,
    KeyboardMessage
)

# Типы запросов
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberSubscribedRequest,
    ViberUnsubscribedRequest,
    ViberConversationStartedRequest,
    ViberFailedRequest,
    ViberDeliveredRequest,
    ViberSeenRequest
)
```

---

## 17. Production Implementation Patterns (VIP-DXB-CatalogBot, Phase 21)

Ниже -- паттерны из реального Viber-бота для туристического бизнеса ОАЭ (CatalogBot). FastAPI + httpx + SQLite, без viberbot SDK.

### 17.1. AsyncIO REST Client (без SDK)

Вместо `viberbot` Python SDK (sync, Flask-ориентированный) -- прямые HTTP-вызовы через httpx:

```python
import httpx

class ViberAPI:
    """Async client for Viber REST Bot API."""

    MAX_TEXT_LENGTH = 7000
    MAX_RICH_MEDIA_ROWS = 7

    def __init__(self, auth_token: str, bot_name: str = "VIP DXB Tours"):
        self.auth_token = auth_token
        self._sender = {"name": bot_name}
        self._client = httpx.AsyncClient(
            timeout=10.0,
            headers={
                "X-Viber-Auth-Token": auth_token,   # НЕ Bearer token!
                "Content-Type": "application/json",
            },
        )

    async def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"https://chatapi.viber.com/pa{endpoint}"
        resp = await self._client.post(url, json=payload)
        data = resp.json()
        if data.get("status") != 0:
            logger.warning("Viber API %s: %s", endpoint, data.get("status_message"))
        return data

    async def send_text(self, receiver, text, keyboard=None, tracking_data=None):
        payload = {
            "receiver": receiver,
            "type": "text",
            "sender": self._sender,
            "text": text[:self.MAX_TEXT_LENGTH],
            "min_api_version": 7,
        }
        if keyboard:
            payload["keyboard"] = keyboard
        if tracking_data:
            payload["tracking_data"] = tracking_data[:4096]
        return await self._post("/send_message", payload)

    async def send_rich_media(self, receiver, rich_media, keyboard=None, tracking_data=None):
        payload = {
            "receiver": receiver,
            "type": "rich_media",
            "sender": self._sender,
            "rich_media": rich_media,
            "min_api_version": 7,
        }
        if keyboard:
            payload["keyboard"] = keyboard
        if tracking_data:
            payload["tracking_data"] = tracking_data[:4096]
        return await self._post("/send_message", payload)

    async def set_webhook(self, url: str):
        """Must be called on startup (Viber != Meta where portal config)."""
        return await self._post("/set_webhook", {
            "url": url,
            "send_name": True,
            "send_photo": True,
            "event_types": [
                "delivered", "seen", "failed",
                "subscribed", "unsubscribed", "conversation_started",
            ],
        })
```

**Почему без SDK:** viberbot SDK -- sync-only, Flask-ориентированный. Для FastAPI + asyncio нужен async client. httpx дешевле всех зависимостей.

### 17.2. HMAC-SHA256 Webhook Verification

```python
import hashlib
import hmac as hmac_module

def verify_viber_signature(body: bytes, signature: str, auth_token: str) -> bool:
    """Verify Viber webhook HMAC-SHA256.

    КЛЮЧЕВОЕ ОТЛИЧИЕ: HMAC ключ = auth_token (НЕ app_secret как у Meta!).
    Заголовок: X-Viber-Content-Signature (НЕ sha256= prefix как у Meta).
    """
    if not signature or not auth_token:
        return False
    expected = hmac_module.new(
        auth_token.encode("utf-8"),   # Ключ = bot auth token
        body,                          # Raw bytes тела запроса
        hashlib.sha256,
    ).hexdigest()
    return hmac_module.compare_digest(expected, signature)
```

| Платформа | HMAC-ключ | Заголовок | Префикс |
|-----------|-----------|-----------|---------|
| **Viber** | `auth_token` | `X-Viber-Content-Signature` | нет |
| **Meta (IG/WA)** | `app_secret` | `X-Hub-Signature-256` | `sha256=` |
| **Telegram** | n/a (token в URL) | n/a | n/a |

### 17.3. FastAPI Webhook Server + Auto set_webhook

```python
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Init DB, API client, auto-register webhook on startup."""
    db = CatalogDB(DB_PATH)
    await db.init()

    viber_api = ViberAPI(auth_token=VIBER_AUTH_TOKEN)
    fsm = FSMManager()

    app.state.db = db
    app.state.viber_api = viber_api
    app.state.fsm = fsm

    # Auto set_webhook (Viber requires API call, NOT portal config like Meta)
    if VIBER_WEBHOOK_URL:
        result = await viber_api.set_webhook(VIBER_WEBHOOK_URL)
        if result.get("status") == 0:
            logger.info("Viber webhook registered: %s", VIBER_WEBHOOK_URL)
    yield
    await viber_api.close()
    await db.close()

app = FastAPI(title="VIP-DXB Viber Bot", lifespan=lifespan)

@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Viber-Content-Signature", "")
    if not verify_viber_signature(body, signature, VIBER_AUTH_TOKEN):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = json.loads(body)
    await process_webhook(data, app.state.db, app.state.viber_api, app.state.fsm)
    return {"status": "ok"}  # Must return 200 quickly
```

**Конвенция портов:** TG (polling), IG=8081, WA=8082, FB=8083, Viber=8084.

### 17.4. tracking_data Hybrid FSM (Novel Pattern)

tracking_data -- уникальная фича Viber (до 4096 символов), возвращается с каждым ответом пользователя. Позволяет **stateless FSM** без серверной сессии.

**Гибридный подход:** tracking_data (primary) + in-memory dict (fallback).

```python
import json, time
from enum import Enum, auto

class ViberState(Enum):
    IDLE = auto()
    SEARCH = auto()
    BOOKING_NAME = auto()
    BOOKING_PHONE = auto()
    BOOKING_DATE = auto()
    BOOKING_ADULTS = auto()
    BOOKING_CHILDREN = auto()
    BOOKING_PROMO = auto()
    BOOKING_CONFIRM = auto()

class FSMManager:
    """Hybrid FSM: tracking_data (stateless) + in-memory (fallback)."""

    def __init__(self, timeout: int = 3600):
        self._sessions = {}  # user_id -> {state, data, last_active}
        self._timeout = timeout

    def encode_tracking_data(self, user_id, state, data=None) -> str:
        """Encode FSM state into JSON for tracking_data field.

        Format: {"s": "booking_phone", "d": {"name": "John", "block_id": 42}}
        Compact keys "s"/"d" to save space (4096 char limit).
        """
        payload = {"s": state.name.lower()}
        if data:
            payload["d"] = data
        # Also store in memory as fallback
        self._sessions[user_id] = {"state": state, "data": data or {}, "ts": time.time()}
        return json.dumps(payload, ensure_ascii=False)[:4096]

    def decode_tracking_data(self, user_id, tracking_data=None):
        """Decode state from tracking_data, fallback to in-memory if missing."""
        if tracking_data:
            try:
                payload = json.loads(tracking_data)
                state = _STATE_BY_NAME.get(payload.get("s", "idle"), ViberState.IDLE)
                data = payload.get("d", {})
                self._sessions[user_id] = {"state": state, "data": data, "ts": time.time()}
                return state, data
            except (json.JSONDecodeError, ValueError):
                pass
        # Fallback: in-memory session
        session = self._sessions.get(user_id)
        if session and (time.time() - session["ts"]) < self._timeout:
            return session["state"], dict(session["data"])
        return ViberState.IDLE, {}
```

**Когда нужен fallback:**
- Пользователь вводит текст (без кнопки) -- tracking_data может быть пустым
- JSON слишком большой (>4096) -- обрезается
- Переподписка (subscribed event) -- Viber сбрасывает tracking_data

### 17.5. Rich Media Carousel (6-column Grid, 8 Rows per Card)

```python
def _build_card_buttons(block: dict) -> list:
    """Build one catalog card (8 rows = image 3 + text 2 + buttons 2x1 + separator 1)."""
    block_id = block["id"]
    buttons = []

    # Image: 6 cols x 3 rows (ActionType: "none")
    buttons.append({
        "Columns": 6, "Rows": 3,
        "ActionType": "none", "ActionBody": "none",
        "Image": block.get("photo_url", ""),
    })

    # Text: 6 cols x 2 rows (HTML: <b>, <br>, <font>)
    buttons.append({
        "Columns": 6, "Rows": 2,
        "ActionType": "none", "ActionBody": "none",
        "Text": f"<b>{block['title']}</b><br>💰 {block['price_adult']:,.0f} AED",
        "TextVAlign": "middle", "TextHAlign": "left",
    })

    # Book button: 3 cols x 1 row
    buttons.append({
        "Columns": 3, "Rows": 1,
        "ActionType": "reply", "ActionBody": f"book:{block_id}",
        "Text": "<b>📝 Book</b>", "BgColor": "#4CAF50",
        "TextHAlign": "center", "TextVAlign": "middle",
        "Silent": True,  # Don't show ActionBody in chat
    })

    # Info button: 3 cols x 1 row
    buttons.append({
        "Columns": 3, "Rows": 1,
        "ActionType": "reply", "ActionBody": f"detail:{block_id}",
        "Text": "<b>ℹ️ Info</b>", "BgColor": "#2196F3",
        "TextHAlign": "center", "TextVAlign": "middle",
        "Silent": True,
    })

    # Separator: 6 cols x 1 row
    buttons.append({
        "Columns": 6, "Rows": 1,
        "ActionType": "none", "ActionBody": "none",
        "Text": " ", "BgColor": "#F5F5F5",
    })
    return buttons  # Total: 3+2+1+1+1 = 8 rows


def build_catalog_carousel(blocks: list, page: int = 0) -> dict:
    PAGE_SIZE = 5  # Conservative: 5 cards * 8 rows = 40 rows (max ~42)
    page_blocks = blocks[page * PAGE_SIZE : (page+1) * PAGE_SIZE]

    all_buttons = []
    for block in page_blocks:
        all_buttons.extend(_build_card_buttons(block))

    # "Next page" card if more blocks exist
    if (page+1) * PAGE_SIZE < len(blocks):
        all_buttons.append({
            "Columns": 6, "Rows": 3,
            "ActionType": "reply", "ActionBody": f"page:{page+1}",
            "Text": f"<b>➡️ More ({len(blocks) - (page+1)*PAGE_SIZE} left)</b>",
            "BgColor": "#FF9800",
        })

    return {
        "Type": "rich_media",
        "ButtonsGroupColumns": 6,
        "ButtonsGroupRows": 7,  # Viber groups buttons into cards by this count
        "BgColor": "#FFFFFF",
        "Buttons": all_buttons,
    }
```

**PAGE_SIZE = 5** (консервативно): 5 карточек x 8 строк = 40 строк (макс ~42 ряда).
**ButtonsGroupRows** определяет, сколько строк Viber отнесет к одной карточке при горизонтальной прокрутке.

### 17.6. Message Routing Pattern

```python
async def handle_text(sender_id, text, tracking_data, name, user, db, api, fsm):
    """Route text messages and button taps.

    Priority:
    1. Booking FSM states (check first -- intercepts free text during booking)
    2. Search FSM state
    3. Structured action bodies from buttons (emirate:DXB, book:42, etc.)
    4. Text commands (привет, search, каталог)
    5. Default: treat unknown text as search query
    """
    state, fsm_data = fsm.decode_tracking_data(sender_id, tracking_data)

    # 1. Booking FSM
    if state.name.startswith("BOOKING_"):
        if text.lower() in ("cancel", "отмена", "/cancel"):
            fsm.reset(sender_id)
            await api.send_text(sender_id, "❌ Booking cancelled.")
            return
        await handle_booking_step(sender_id, text, db, api, fsm)
        return

    # 2. Search FSM
    if state == ViberState.SEARCH:
        await handle_search_query(sender_id, text, db, api, fsm)
        return

    # 3. Structured actions from button ActionBody
    if text.startswith("emirate:"):      ...
    elif text.startswith("cat:"):        ...  # cat:DXB:excursions
    elif text.startswith("book:"):       ...
    elif text.startswith("detail:"):     ...
    elif text.startswith("page:"):       ...  # Pagination
    elif text == "search":               ...
    elif text == "help":                 ...
    elif text in ("menu", "start"):      ...

    # 4. Text commands
    elif text.lower() in ("привет", "hi", "hello", ...): send_main_menu(...)

    # 5. Default: search
    else: await handle_search_query(sender_id, text, ...)
```

### 17.7. Keyboard (Persistent, 6-column Grid)

```python
def build_main_keyboard():
    """Main menu keyboard (stays until explicitly replaced).

    Layout (6 columns):
    Row 1: Dubai (3) | Abu Dhabi (3)
    Row 2: RAK (3)   | Fujairah (3)
    Row 3: Search (3) | Help (3)
    """
    return {
        "Type": "keyboard",
        "DefaultHeight": False,  # Compact layout
        "Buttons": [
            {"Columns": 3, "Rows": 1, "ActionType": "reply",
             "ActionBody": "emirate:DXB", "Text": "<b>🏙 Dubai</b>",
             "BgColor": "#E8F5E9", "Silent": True},
            {"Columns": 3, "Rows": 1, "ActionType": "reply",
             "ActionBody": "emirate:AD", "Text": "<b>🕌 Abu Dhabi</b>",
             "BgColor": "#E8F5E9", "Silent": True},
            # ...
        ],
    }
```

### 17.8. Event Types -- Gotchas

| Событие | Поведение | Gotcha |
|---------|-----------|--------|
| `conversation_started` | Первое открытие чата. Можно отправить 1 welcome. Пользователь **НЕ подписан**! | **Нельзя** слать follow-up сообщения пока не подпишется |
| `subscribed` | Нажал кнопку/отправил первое сообщение | **Сбрасывает** tracking_data! Обнуляет FSM |
| `unsubscribed` | Покинул чат | Только `user_id` (без полного объекта `user`) |
| `message` | Текст, картинка, видео, локация, стикер | Кнопка ActionBody приходит как `message.text` |
| `delivered`/`seen`/`failed` | Delivery reports | Log-only, не отвечать |
| `webhook` | Подтверждение set_webhook | Приходит один раз при установке |

### 17.9. Synthetic user_id Pattern (Multi-Platform DB)

Viber user_id -- opaque Base64 string (не число). Для переиспользования CatalogDB:

```
Telegram:  user_id как есть (до 10^10)
VK:       +10,000,000,000  (VK_ID_OFFSET)
WhatsApp: +20,000,000,000  (WA_ID_OFFSET, string wa_id)
Instagram: -1 .. -999       (synthetic, negative)
WhatsApp:  -1000 .. -2999   (synthetic, negative)
Viber:     -3000 .. -N      (synthetic, negative)
```

```python
async def get_or_create_viber_user(self, viber_id: str, viber_name: str = ""):
    """viber_users table: viber_id (PK), viber_name, synthetic_user_id (UNIQUE)."""
    # SELECT or INSERT with autoincrement synthetic_user_id
    # form_type = "VB_GT" for Viber bookings
```

Все DB-методы (add_booking, get_loyalty, analytics_events) работают с synthetic_user_id.

### 17.10. Gotchas & Best Practices (Checklist)

**Gotchas:**
- `conversation_started` != `subscribed` -- пользователь может прочитать welcome и уйти
- Viber location использует `"lon"` (НЕ `"lng"`) для долготы
- Rich Media ButtonsGroupRows x кол-во карточек <= ~42 строк (иначе обрезка)
- Keyboard **персистентная** -- остается до явной замены другой клавиатурой
- HMAC ключ = `auth_token` (НЕ `sha256=` prefix как у Meta)
- `subscribed` event сбрасывает tracking_data (FSM обнуляется)
- `unsubscribed` присылает только `user_id` (не полный `user` объект)
- picture.text максимум 120 символов (НЕ 7000 как у text)
- `Silent: True` на кнопках -- не показывает ActionBody в чате

**Best Practices:**
- Auto `set_webhook` on app startup (не ручная настройка через портал)
- tracking_data для stateless FSM (меньше серверного state)
- Гибридный FSM: tracking_data primary + in-memory fallback
- `min_api_version: 7` для Rich Media поддержки
- FastAPI + httpx для async (НЕ sync Flask + viberbot SDK)
- One FastAPI app per platform, shared SQLite DB с WAL mode
- Порт 8084 (IG=8081, WA=8082, FB=8083, Viber=8084)
- `compare_digest()` для timing-safe HMAC сравнения

### 17.11. No 24h Messaging Window (vs Meta)

| Платформа | Ограничение на отправку |
|-----------|------------------------|
| **Viber** | 10,000 bot-initiated/месяц (free tier), подписчикам -- в любое время |
| **Instagram** | 24h window от последнего сообщения пользователя |
| **WhatsApp** | 24h window, после -- только Template Messages |
| **Telegram** | Без ограничений |

НО: `conversation_started` позволяет отправить только 1 сообщение (пользователь еще не подписан).

### 17.12. Telegram Manager Notification

При бронировании из Viber -- уведомление в Telegram менеджеру через прямой HTTP POST (без aiogram):

```python
async def _notify_telegram_manager(booking_id, data, viber_id):
    """Direct HTTP POST to Bot API (no aiogram dependency in Viber process)."""
    import httpx
    text = (
        f"📱 <b>New Viber Booking #{booking_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 {data.get('block_title')}\n"
        f"👤 {data.get('name')}\n"
        f"📱 {data.get('phone')}\n"
        f"📅 {data.get('date')}\n"
        f"💬 Viber ID: {viber_id}\n"
    )
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            f"https://api.telegram.org/bot{CATALOG_BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"},
        )
```

### 17.13. .env Variables

```bash
VIBER_AUTH_TOKEN=your_viber_bot_auth_token
VIBER_BOT_NAME="VIP DXB Tours"
VIBER_BOT_AVATAR=https://your-server.com/avatar.jpg
VIBER_WEBHOOK_URL=https://your-server.com/webhook
VIBER_WEBHOOK_PORT=8084
```

---

## Таблица ресурсов

| Ресурс | URL |
|--------|-----|
| REST Bot API (документация) | https://developers.viber.com/docs/api/rest-bot-api/ |
| Node.js SDK | https://developers.viber.com/docs/api/nodejs-bot-api/ |
| Python SDK | https://developers.viber.com/docs/api/python-bot-api/ |
| Java SDK | https://developers.viber.com/docs/api/java-bot-api/ |
| Клавиатуры (дока) | https://developers.viber.com/docs/tools/keyboards/ |
| Примеры клавиатур | https://developers.viber.com/docs/tools/keyboard-examples/ |
| Deep Links | https://developers.viber.com/docs/tools/deep-links/ |
| Broadcast Guide | https://developers.viber.com/docs/guides/broadcast-rest-api/ |
| FAQ для разработчиков | https://developers.viber.com/docs/faq/ |
| Viber for Business | https://www.forbusiness.viber.com/en/chatbots/ |
| GitHub: viber-bot-node | https://github.com/Viber/viber-bot-node |
| GitHub: viber-bot-python | https://github.com/Viber/viber-bot-python |
| npm: viber-bot | https://www.npmjs.com/package/viber-bot |
| PyPI: viberbot | https://pypi.org/project/viberbot/ |
| Коммерческая модель | https://help.viber.com/hc/en-us/articles/15247629658525-Bot-commercial-model |
| Creators Hub (новая дока) | https://creators.viber.com/docs/bots-api/getting-started/web-hooks |
| API Access White Paper | https://developers.viber.com/docs/general/api-access-white-paper/ |
