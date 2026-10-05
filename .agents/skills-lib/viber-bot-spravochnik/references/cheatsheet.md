# Viber Bot API — Cheatsheet

## Base URL
```
https://chatapi.viber.com/pa/
```

## Заголовки (все запросы)
```
X-Viber-Auth-Token: YOUR_TOKEN
Content-Type: application/json
```

---

## Endpoints

| Метод | Endpoint |
|-------|----------|
| Установка webhook | `POST /pa/set_webhook` |
| Отправка сообщения | `POST /pa/send_message` |
| Рассылка | `POST /pa/broadcast_message` |
| Информация о боте | `POST /pa/get_account_info` |
| Данные пользователя | `POST /pa/get_user_details` |
| Онлайн-статус | `POST /pa/get_online` |

---

## Типы сообщений

| type | Ключевые поля |
|------|---------------|
| `text` | `text` (до 7000 символов) |
| `picture` | `text`, `media` (URL), `thumbnail` |
| `video` | `media` (URL .mp4), `size` (до 26 МБ) |
| `file` | `media`, `size` (до 50 МБ), `file_name` |
| `contact` | `contact: {name, phone_number}` |
| `location` | `location: {lat, lon}` |
| `sticker` | `sticker_id` |
| `url` | `media` (URL) |
| `rich_media` | `rich_media: {Type, ButtonsGroupColumns, ButtonsGroupRows, Buttons}` |

---

## Callback Events

| event | Описание |
|-------|----------|
| `message` | Входящее сообщение |
| `subscribed` | Подписка на бота |
| `unsubscribed` | Отписка от бота |
| `conversation_started` | Первое открытие чата |
| `delivered` | Сообщение доставлено |
| `seen` | Сообщение прочитано |
| `failed` | Ошибка доставки |
| `webhook` | Подтверждение webhook (одноразовое) |

---

## Keyboard — быстрый шаблон

```json
{
  "Type": "keyboard",
  "DefaultHeight": false,
  "Buttons": [
    {
      "Columns": 3,
      "Rows": 1,
      "BgColor": "#2db9b9",
      "ActionType": "reply",
      "ActionBody": "action_value",
      "Text": "<b>Текст кнопки</b>",
      "TextSize": "regular",
      "TextHAlign": "center",
      "TextVAlign": "middle"
    }
  ]
}
```

**Сетка:** 6 колонок, 1-7 строк на кнопку.

---

## ActionType

| Тип | Действие |
|-----|----------|
| `reply` | Отправляет ActionBody как сообщение |
| `open-url` | Открывает URL |
| `none` | Ничего (декоративная) |
| `location-picker` | Выбор геолокации |
| `share-phone` | Отправка номера телефона |

---

## Rich Media — быстрый шаблон (1 карточка)

```json
{
  "Type": "rich_media",
  "ButtonsGroupColumns": 6,
  "ButtonsGroupRows": 6,
  "Buttons": [
    {"Columns": 6, "Rows": 3, "ActionType": "open-url",
     "ActionBody": "https://url", "Image": "https://img.jpg"},
    {"Columns": 6, "Rows": 2, "ActionType": "none",
     "ActionBody": "none",
     "Text": "<b>Заголовок</b><br>Описание<br><b>Цена</b>"},
    {"Columns": 6, "Rows": 1, "ActionType": "reply",
     "ActionBody": "book_item",
     "Text": "<font color='#FFF'><b>Купить</b></font>",
     "BgColor": "#2db9b9"}
  ]
}
```

**Формула:** `ButtonsGroupRows` = сумма Rows в одной карточке. Viber делит Buttons на группы автоматически.

---

## tracking_data (FSM)

```python
# Отправка с состоянием
tracking = json.dumps({"step": "choose_date", "tour": "safari"})

# Получение из callback
tracking = data['message'].get('tracking_data', '')
state = json.loads(tracking) if tracking else {}
```

**Лимит:** 4000 символов. Сбрасывается при переподписке.

---

## Deep Links

```
viber://pa?chatURI=BOT_URI&context=SOURCE
```

Контекст приходит в `conversation_started`. Работает Android/iOS (не Desktop).

---

## Rate Limits

| Операция | Лимит |
|----------|-------|
| broadcast_message | 500 req / 10 sec |
| broadcast получатели | 300 / запрос |
| broadcast размер | 30 КБ |
| get_user_details | 2 req / 12h / user |
| Bot-initiated бесплатно | 10,000 / месяц |

---

## curl — шаблоны

### Отправить текст
```bash
curl -X POST https://chatapi.viber.com/pa/send_message \
  -H "X-Viber-Auth-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver":"USER_ID","type":"text","text":"Hello!","min_api_version":7}'
```

### Установить webhook
```bash
curl -X POST https://chatapi.viber.com/pa/set_webhook \
  -H "X-Viber-Auth-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://your-server.com/webhook","event_types":["message","subscribed","conversation_started"]}'
```

### Проверить бота
```bash
curl -X POST https://chatapi.viber.com/pa/get_account_info \
  -H "X-Viber-Auth-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Рассылка
```bash
curl -X POST https://chatapi.viber.com/pa/broadcast_message \
  -H "X-Viber-Auth-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"broadcast_list":["ID1","ID2"],"type":"text","text":"Акция!","min_api_version":7}'
```

---

## Python — быстрый старт

```python
pip install viberbot flask
```

```python
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest
import os

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='MyBot', avatar='https://img.jpg',
    auth_token=os.environ['VIBER_TOKEN']
))

@app.route('/webhook', methods=['POST'])
def incoming():
    if not viber.verify_signature(request.get_data(),
        request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)
    req = viber.parse_request(request.get_data())
    if isinstance(req, ViberMessageRequest):
        viber.send_messages(req.sender.id, [TextMessage(text='Echo: ' + req.message.text)])
    return Response(status=200)

app.run(host='0.0.0.0', port=8080)
```

---

## Node.js — быстрый старт

```bash
npm install viber-bot express
```

```javascript
const express = require('express');
const ViberBot = require('viber-bot').Bot;
const BotEvents = require('viber-bot').Events;
const TextMessage = require('viber-bot').Message.Text;

const app = express();
const bot = new ViberBot({
    authToken: process.env.VIBER_TOKEN,
    name: "MyBot",
    avatar: "https://img.jpg"
});

bot.on(BotEvents.MESSAGE_RECEIVED, (message, response) => {
    response.send(new TextMessage('Echo: ' + message.text));
});

app.use('/webhook', bot.middleware());
app.listen(8080, () => bot.setWebhook('https://your-server.com/webhook'));
```

---

## HTML в кнопках

```html
<b>жирный</b>
<i>курсив</i>
<u>подчёркнутый</u>
<s>зачёркнутый</s>
<font color="#FF0000" size="18">цветной текст</font>
<br> <!-- перенос строки -->
```

---

## Коды ошибок

| status | Описание |
|--------|----------|
| 0 | Успех |
| 1 | Невалидный URL |
| 2 | Невалидный токен |
| 3 | Некорректные данные |
| 4 | Пропущены данные |
| 5 | Получатель не в Viber |
| 6 | Не подписчик |
| 7 | Бот заблокирован |
| 8 | Бот не найден |
| 9 | Бот приостановлен |
| 10 | Webhook не установлен |
| 11 | Устройство не поддерживает |
| 12 | Rate limit |

---

## Библиотеки

| Язык | Пакет | Установка |
|------|-------|-----------|
| Node.js | viber-bot | `npm install viber-bot` |
| Python | viberbot | `pip install viberbot` |
| Java | viber-bot | Maven |

## Ключевые отличия от Telegram

- **Нет long polling** — только webhook
- **tracking_data** — встроенный FSM (нет в Telegram)
- **Rich Media** — нативные карусели
- **HTML в кнопках** — `<b>`, `<font>`, `<br>`
- **Коммерческая модель** — 10K бесплатных msg/месяц
- **CA-signed SSL** — self-signed не работает
- **Нет списка подписчиков** — храните сами

---

## Production Patterns (Phase 21 CatalogBot)

### Async Client (без viberbot SDK)
```python
# httpx AsyncClient вместо sync viberbot SDK
self._client = httpx.AsyncClient(
    timeout=10.0,
    headers={"X-Viber-Auth-Token": auth_token},
)
```

### HMAC — auth_token (НЕ app_secret!)
```python
hmac.new(auth_token.encode(), body, hashlib.sha256).hexdigest()
# Заголовок: X-Viber-Content-Signature (без sha256= prefix!)
```

### Hybrid FSM (tracking_data + in-memory)
```python
# Encode: {"s": "booking_phone", "d": {"name": "John"}}
tracking = json.dumps({"s": state.name.lower(), "d": data})[:4096]
# Decode: try tracking_data -> fallback to in-memory dict
```

### Rich Media: 8 rows/card, PAGE_SIZE=5
```
Image:    6 cols x 3 rows (ActionType: "none")
Text:     6 cols x 2 rows (HTML: <b>, <br>, <font>)
Button 1: 3 cols x 1 row (book:{id})
Button 2: 3 cols x 1 row (detail:{id})
Separator: 6 cols x 1 row
Total: 8 rows x 5 cards = 40 rows (max ~42)
```

### Gotchas
- `location.lon` (НЕ `lng`)
- `conversation_started` != `subscribed` (1 welcome only)
- `subscribed` event сбрасывает tracking_data
- picture.text max 120 chars (НЕ 7000)
- Keyboard stays until replaced
- set_webhook via API (NOT portal config like Meta)

### Port Convention
TG (polling), IG=8081, WA=8082, FB=8083, Viber=8084

### Synthetic User IDs
Viber: -3000, -3001, ... | form_type: "VB_GT"
