---
name: vk-bot-справочник
description: "Production-ready руководство по VK Bot API для туристического бизнеса ОАЭ. Long Poll, Callback API, клавиатуры, карусели, рассылки, VKPay. Используй когда нужно создать бота ВКонтакте."
---
# VK Bot API: Production-Ready руководство

## Содержание

1. [Quick Start](#quick-start)
2. [Архитектура: Long Poll vs Callback](#архитектура-long-poll-vs-callback)
3. [Аутентификация и токены](#аутентификация-и-токены)
4. [Long Poll API](#long-poll-api)
5. [Callback API](#callback-api)
6. [Обработка сообщений](#обработка-сообщений)
7. [Клавиатуры](#клавиатуры)
8. [Карусели](#карусели)
9. [Медиа и вложения](#медиа-и-вложения)
10. [Состояния диалога (State Machine)](#состояния-диалога)
11. [VK Pay](#vk-pay)
12. [VK Mini Apps](#vk-mini-apps)
13. [Рассылки](#рассылки)
14. [Rate Limits и execute](#rate-limits-и-execute)
15. [Примеры для туризма ОАЭ](#примеры-для-туризма-оаэ)
16. [Деплой](#деплой)
17. [Библиотеки](#библиотеки)

---

## Quick Start

### Создание бота сообщества за 5 минут

**Шаг 1: Подготовка сообщества**

1. Создайте или откройте ваше VK-сообщество
2. **Управление** -> **Настройки** -> **Сообщения** -> Включить "Сообщения сообщества"
3. **Управление** -> **Настройки** -> **Работа с API** -> **Создать ключ**
4. Выберите права: управление, сообщения, фотографии, документы
5. Скопируйте токен (Community Token)

**Шаг 2: Включить Long Poll**

1. **Работа с API** -> **Long Poll API** -> Включить
2. **Версия API:** 5.199
3. **Типы событий:** message_new, message_event, message_allow, message_deny

**Шаг 3: Первый бот (Python, vkbottle)**

```bash
pip install vkbottle
```

```python
from vkbottle.bot import Bot, Message

bot = Bot("YOUR_COMMUNITY_TOKEN")

@bot.on.message(text="привет")
async def greet(message: Message):
    await message.answer("Добро пожаловать в Dubai Tours! Напишите /tours")

@bot.on.message(text="/tours")
async def tours(message: Message):
    await message.answer(
        "Наши экскурсии:\n"
        "1. Desert Safari - 250 AED\n"
        "2. City Tour - 150 AED\n"
        "3. Yacht Marina - 300 AED\n\n"
        "Напишите номер для подробностей"
    )

bot.run_forever()
```

**Шаг 4: Первый бот (Node.js, vk-io)**

```bash
npm install vk-io
```

```javascript
const { VK } = require('vk-io');

const vk = new VK({ token: 'YOUR_COMMUNITY_TOKEN' });

vk.updates.on('message_new', async (context) => {
  if (context.text === 'привет') {
    await context.send('Добро пожаловать в Dubai Tours!');
  }
});

vk.updates.start().then(() => console.log('Bot started'));
```

---

## Архитектура: Long Poll vs Callback

### Сравнение

| Критерий | Long Poll API | Callback API |
|----------|--------------|--------------|
| **Принцип** | Бот опрашивает сервер VK | VK отправляет POST на ваш URL |
| **Сервер** | Не нужен публичный IP | Нужен HTTPS-сервер |
| **Задержка** | Мгновенная (~100ms) | Мгновенная (~100ms) |
| **Масштабирование** | Сложно (одно соединение) | Легко (load balancer) |
| **Разработка** | Идеально для localhost | Нужен ngrok/домен |
| **Надежность** | Автореконнект при обрыве | VK повторяет запрос 3 раза |
| **Serverless** | Невозможно | AWS Lambda, Cloud Functions |

### Когда что использовать

**Long Poll API:**
- Разработка и отладка
- Один сервер, малая/средняя нагрузка
- Быстрый запуск, MVP
- До ~1000 сообщений/мин

**Callback API:**
- Production с высокой нагрузкой
- Serverless-архитектура (Lambda, Cloud Functions)
- Множественные серверы с балансировкой
- Интеграция с существующим web-сервером

**Рекомендация для туризма:** Long Poll для старта, переход на Callback при масштабировании.

---

## Аутентификация и токены

### Типы токенов

| Тип | Rate Limit | Применение |
|-----|-----------|------------|
| **Community Token** | 20 req/sec | Бот сообщества, сообщения, стена |
| **User Token** | 3 req/sec | Действия от имени пользователя |
| **Service Token** | 10 req/sec | Серверные запросы без авторизации пользователя |

### Community Token (основной для ботов)

```
Настройки сообщества -> Работа с API -> Создать ключ
```

Права доступа:
- `messages` - отправка/чтение сообщений
- `photos` - работа с фотографиями
- `docs` - работа с документами
- `manage` - управление сообществом
- `wall` - работа с записями на стене

### User Token (Implicit Flow)

```
https://oauth.vk.com/authorize?
  client_id=APP_ID&
  display=page&
  redirect_uri=https://oauth.vk.com/blank.html&
  scope=messages,photos,wall,groups&
  response_type=token&
  v=5.199
```

### Service Token

```
Настройки приложения -> Сервисный ключ доступа
```

Используется для публичных данных без авторизации пользователя.

---

## Long Poll API

### Принцип работы

```
Бот -> GET /groups.getLongPollServer -> {server, key, ts}
Бот -> GET {server}?act=a_check&key={key}&ts={ts}&wait=25
VK  -> (ждёт события до 25 сек) -> [{events}] + new_ts
Бот -> обрабатывает события -> повторяет с new_ts
```

### Подключение (низкоуровневое)

```python
import requests
import vk_api

vk_session = vk_api.VkApi(token='YOUR_TOKEN')
vk = vk_session.get_api()

# Получить сервер Long Poll
lp = vk.groups.getLongPollServer(group_id=123456)
server, key, ts = lp['server'], lp['key'], lp['ts']

while True:
    response = requests.get(
        f"{server}?act=a_check&key={key}&ts={ts}&wait=25"
    ).json()

    if 'failed' in response:
        if response['failed'] == 1:
            ts = response['ts']  # Обновить ts
        elif response['failed'] in (2, 3):
            lp = vk.groups.getLongPollServer(group_id=123456)
            server, key, ts = lp['server'], lp['key'], lp['ts']
        continue

    ts = response['ts']
    for event in response.get('updates', []):
        if event['type'] == 'message_new':
            msg = event['object']['message']
            print(f"From {msg['from_id']}: {msg['text']}")
```

### Коды ошибок Long Poll

| Код | Причина | Решение |
|-----|---------|---------|
| `failed: 1` | Устаревший ts | Использовать ts из ответа |
| `failed: 2` | Устаревший key | Запросить новый key через getLongPollServer |
| `failed: 3` | Утеряны key и ts | Запросить оба заново |

### Подключение через vkbottle (рекомендуется)

```python
from vkbottle.bot import Bot, Message

bot = Bot("YOUR_TOKEN")

@bot.on.message(text="начать")
async def start(message: Message):
    await message.answer("Привет! Выберите экскурсию.")

@bot.on.message()
async def fallback(message: Message):
    await message.answer("Напишите 'начать' для главного меню.")

bot.run_forever()  # Автоматически: Long Poll + reconnect + error handling
```

### Подключение через vk-io (Node.js)

```javascript
const { VK } = require('vk-io');
const vk = new VK({ token: 'YOUR_TOKEN' });

vk.updates.on('message_new', async (context) => {
  if (context.text === 'начать') {
    await context.send('Привет! Выберите экскурсию.');
  }
});

// Автоматически Long Poll с реконнектом
vk.updates.start().catch(console.error);
```

---

## Callback API

### Настройка сервера

**Шаг 1:** Указать URL в настройках Callback API сообщества.

**Шаг 2:** Реализовать confirmation endpoint.

**Шаг 3:** Выбрать типы событий для получения.

**Шаг 4:** Установить Secret Key для проверки подлинности.

### Flask-сервер (Python)

```python
from flask import Flask, request, jsonify
import vk_api

app = Flask(__name__)

CONFIRMATION_TOKEN = 'abc123def'  # Из настроек Callback API
SECRET_KEY = 'my_secret_key'
VK_TOKEN = 'YOUR_COMMUNITY_TOKEN'

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()

    # Проверка Secret Key
    if data.get('secret') != SECRET_KEY:
        return 'Forbidden', 403

    # Подтверждение сервера
    if data['type'] == 'confirmation':
        return CONFIRMATION_TOKEN

    # Новое сообщение
    if data['type'] == 'message_new':
        msg = data['object']['message']
        user_id = msg['from_id']
        text = msg['text']

        vk.messages.send(
            user_id=user_id,
            message=f"Вы написали: {text}",
            random_id=0
        )

    # Нажатие callback-кнопки
    if data['type'] == 'message_event':
        event = data['object']
        payload = event.get('payload', {})
        # Обработка event...

    return 'ok'  # Обязательно вернуть "ok"!

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Express-сервер (Node.js)

```javascript
const express = require('express');
const { VK } = require('vk-io');

const app = express();
const vk = new VK({ token: 'YOUR_TOKEN' });

app.use(express.json());

const CONFIRMATION = 'abc123def';
const SECRET = 'my_secret_key';

app.post('/callback', (req, res) => {
  const { type, object, secret } = req.body;

  if (secret !== SECRET) return res.status(403).send('Forbidden');
  if (type === 'confirmation') return res.send(CONFIRMATION);

  if (type === 'message_new') {
    const { from_id, text } = object.message;
    vk.api.messages.send({
      user_id: from_id,
      message: `Вы написали: ${text}`,
      random_id: 0
    });
  }

  res.send('ok');
});

app.listen(5000, () => console.log('Callback server on :5000'));
```

### Типы событий Callback API

| Событие | Описание |
|---------|----------|
| `message_new` | Новое входящее сообщение |
| `message_reply` | Исходящее сообщение бота |
| `message_edit` | Сообщение отредактировано |
| `message_allow` | Пользователь разрешил сообщения |
| `message_deny` | Пользователь запретил сообщения |
| `message_event` | Нажатие callback-кнопки |
| `message_typing_state` | Пользователь печатает |
| `wall_post_new` | Новая запись на стене |
| `wall_reply_new` | Новый комментарий на стене |
| `group_join` | Вступление в группу |
| `group_leave` | Выход из группы |

---

## Обработка сообщений

### messages.send - основной метод

```python
vk.messages.send(
    user_id=123456,          # ID получателя
    # peer_id=2000000001,    # Для бесед (2000000000 + chat_id)
    message="Текст",         # Текст сообщения (до 4096 символов)
    random_id=0,             # Уникальный ID (0 = автогенерация)
    keyboard=keyboard_json,  # Клавиатура (JSON строка)
    template=template_json,  # Карусель (JSON строка)
    attachment="photo-123_456",  # Вложения (через запятую)
    reply_to=789,            # ID сообщения для ответа
    forward_messages="1,2,3", # Пересланные сообщения
    lat=25.2048,             # Широта (геолокация)
    long=55.2708,            # Долгота
)
```

### Вложения (attachments)

Формат: `{type}{owner_id}_{media_id}`, через запятую для нескольких.

```python
# Одно вложение
attachment = "photo-123456_789012"

# Несколько вложений
attachment = "photo-123_456,video-123_789,doc-123_012"

# Отправка
vk.messages.send(
    user_id=user_id,
    message="Фото экскурсии",
    attachment=attachment,
    random_id=0
)
```

### Пересланные сообщения и ответы

```python
# Ответ на конкретное сообщение
vk.messages.send(
    user_id=user_id,
    message="Ответ на ваш вопрос...",
    reply_to=original_message_id,
    random_id=0
)

# Пересылка сообщений
vk.messages.send(
    user_id=user_id,
    message="Пересылаю вам информацию:",
    forward_messages="12345,12346",
    random_id=0
)
```

### Структура входящего сообщения

```json
{
  "type": "message_new",
  "object": {
    "message": {
      "id": 123,
      "date": 1738876800,
      "from_id": 123456789,
      "peer_id": 123456789,
      "text": "Привет",
      "attachments": [],
      "fwd_messages": [],
      "payload": "{\"command\":\"start\"}",
      "ref": "",
      "ref_source": ""
    },
    "client_info": {
      "button_actions": ["text", "vkpay", "open_app", "location", "open_link", "callback"],
      "keyboard": true,
      "inline_keyboard": true,
      "carousel": true,
      "lang_id": 0
    }
  },
  "group_id": 12345678
}
```

**client_info** - показывает какие возможности поддерживает клиент пользователя. Проверяйте перед отправкой клавиатур и каруселей.

---

## Клавиатуры

### Два типа клавиатур

1. **Reply Keyboard** (стандартная) - заменяет панель ввода, до 10 строк, 5 кнопок в строке
2. **Inline Keyboard** - встраивается в сообщение, до 6 строк, 5 кнопок в строке

### Типы кнопок

| Тип | Описание | Параметры |
|-----|----------|-----------|
| `text` | Отправляет текст + payload | label, payload, color |
| `callback` | Отправляет event (без текста в чат) | label, payload |
| `open_link` | Открывает URL | label, link |
| `location` | Запрашивает геолокацию | payload |
| `vkpay` | Открывает VK Pay | hash |
| `open_app` | Открывает VK Mini App | app_id, owner_id, label, hash |

### Reply Keyboard (Python, vkbottle)

```python
from vkbottle import Keyboard, KeyboardButtonColor, Text

keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Text("Desert Safari", payload={"cmd": "desert"}), color=KeyboardButtonColor.POSITIVE)
    .add(Text("City Tour", payload={"cmd": "city"}), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Yacht Tour", payload={"cmd": "yacht"}), color=KeyboardButtonColor.PRIMARY)
    .add(Text("Контакты", payload={"cmd": "contacts"}), color=KeyboardButtonColor.NEGATIVE)
)

@bot.on.message(text="начать")
async def start(message: Message):
    await message.answer("Выберите экскурсию:", keyboard=keyboard)
```

### Inline Keyboard (Python, vkbottle)

```python
from vkbottle import Keyboard, Callback, OpenLink

inline_kb = (
    Keyboard(inline=True)
    .add(Callback("Забронировать", payload={"cmd": "book", "tour": "desert"}))
    .add(Callback("Подробнее", payload={"cmd": "details", "tour": "desert"}))
    .row()
    .add(OpenLink("Наш сайт", link="https://dubaitours.ae"))
)

await message.answer("Desert Safari - 250 AED", keyboard=inline_kb)
```

### Обработка callback-кнопок (message_event)

```python
from vkbottle.bot import Bot, Message
from vkbottle import GroupEventType, GroupTypes

bot = Bot("YOUR_TOKEN")

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, GroupTypes.MessageEvent)
async def handle_callback(event: GroupTypes.MessageEvent):
    payload = event.object.payload
    user_id = event.object.user_id
    peer_id = event.object.peer_id
    event_id = event.object.event_id

    if payload.get("cmd") == "book":
        # Показать snackbar (всплывающее уведомление)
        await bot.api.messages.send_message_event_answer(
            event_id=event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data='{"type":"show_snackbar","text":"Заявка принята!"}'
        )

    elif payload.get("cmd") == "details":
        # Открыть ссылку
        await bot.api.messages.send_message_event_answer(
            event_id=event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data='{"type":"open_link","link":"https://dubaitours.ae/desert"}'
        )
```

### Inline Keyboard (Node.js, vk-io)

```javascript
const { Keyboard } = require('vk-io');

const keyboard = Keyboard.builder()
  .callbackButton({ label: 'Забронировать', payload: { cmd: 'book' }, color: 'positive' })
  .callbackButton({ label: 'Подробнее', payload: { cmd: 'details' } })
  .row()
  .urlButton({ label: 'Наш сайт', url: 'https://dubaitours.ae' })
  .inline();

await context.send({ message: 'Desert Safari - 250 AED', keyboard });

// Обработка callback
vk.updates.on('message_event', async (context) => {
  const { payload } = context.eventPayload;
  if (payload.cmd === 'book') {
    await context.answer({ type: 'show_snackbar', text: 'Заявка принята!' });
  }
});
```

### Цвета кнопок

| Цвет | vkbottle | vk-io | Применение |
|------|----------|-------|------------|
| Синий | `PRIMARY` | `primary` | Основные действия |
| Зеленый | `POSITIVE` | `positive` | Подтверждение |
| Красный | `NEGATIVE` | `negative` | Отмена, важное |
| Белый | `SECONDARY` | `secondary` | Дополнительные |

---

## Карусели

### Что такое карусель

Горизонтально прокручиваемый набор карточек (1-10 элементов). Каждая карточка: фото + заголовок + описание + кнопки.

### Структура карусели

```python
template = {
    "type": "carousel",
    "elements": [
        {
            "title": "Desert Safari",
            "description": "Джипы по дюнам, ужин BBQ, шоу",
            "photo_id": "-123456_789012",  # Или "photo_id": None без фото
            "action": {
                "type": "open_link",
                "link": "https://dubaitours.ae/desert"
            },
            "buttons": [
                {
                    "action": {
                        "type": "callback",
                        "label": "250 AED - Забронировать",
                        "payload": "{\"cmd\":\"book\",\"tour\":\"desert\"}"
                    }
                }
            ]
        },
        {
            "title": "City Tour",
            "description": "Burj Khalifa, Dubai Mall, Old Dubai",
            "photo_id": "-123456_789013",
            "buttons": [
                {
                    "action": {
                        "type": "callback",
                        "label": "150 AED - Забронировать",
                        "payload": "{\"cmd\":\"book\",\"tour\":\"city\"}"
                    }
                }
            ]
        }
    ]
}
```

### Отправка карусели

```python
import json

vk.messages.send(
    user_id=user_id,
    message="Наши экскурсии:",
    template=json.dumps(template),
    random_id=0
)
```

### Карусель через vkbottle

```python
from vkbottle import template_gen

carousel = template_gen(
    [
        {
            "title": "Desert Safari",
            "description": "250 AED | 6 часов",
            "photo_id": "-123_456",
            "buttons": [{"action": {"type": "callback", "label": "Забронировать",
                        "payload": "{\"cmd\":\"book\",\"tour\":\"desert\"}"}}]
        },
        {
            "title": "City Tour",
            "description": "150 AED | 4 часа",
            "photo_id": "-123_789",
            "buttons": [{"action": {"type": "callback", "label": "Забронировать",
                        "payload": "{\"cmd\":\"book\",\"tour\":\"city\"}"}}]
        }
    ]
)

await message.answer("Выберите экскурсию:", template=carousel)
```

### Ограничения каруселей

- Элементов: 1-10
- Заголовок: до 80 символов
- Описание: до 80 символов
- Кнопок на элемент: до 3
- Проверяйте `client_info.carousel == true` перед отправкой

---

## Медиа и вложения

### Загрузка фото в сообщение

Трехшаговый процесс: получить URL -> загрузить файл -> сохранить.

```python
import requests

# 1. Получить upload URL
upload_info = vk.photos.getMessagesUploadServer(peer_id=user_id)
upload_url = upload_info['upload_url']

# 2. Загрузить файл
with open('desert_safari.jpg', 'rb') as f:
    response = requests.post(upload_url, files={'photo': f}).json()

# 3. Сохранить фото
saved = vk.photos.saveMessagesPhoto(
    server=response['server'],
    photo=response['photo'],
    hash=response['hash']
)[0]

attachment = f"photo{saved['owner_id']}_{saved['id']}"

# 4. Отправить
vk.messages.send(
    user_id=user_id,
    message="Фото с Desert Safari",
    attachment=attachment,
    random_id=0
)
```

### Загрузка документов

```python
# 1. Получить upload URL
upload_info = vk.docs.getMessagesUploadServer(
    type='doc',  # 'doc', 'audio_message', 'graffiti'
    peer_id=user_id
)

# 2. Загрузить
with open('price_list.pdf', 'rb') as f:
    response = requests.post(upload_info['upload_url'], files={'file': f}).json()

# 3. Сохранить
saved = vk.docs.save(file=response['file'], title="Прайс-лист Dubai Tours")
doc = saved['doc']
attachment = f"doc{doc['owner_id']}_{doc['id']}"

# 4. Отправить
vk.messages.send(user_id=user_id, attachment=attachment, random_id=0)
```

### Голосовые сообщения

```python
upload_info = vk.docs.getMessagesUploadServer(type='audio_message', peer_id=user_id)
with open('welcome.ogg', 'rb') as f:
    response = requests.post(upload_info['upload_url'], files={'file': f}).json()
saved = vk.docs.save(file=response['file'])
doc = saved['audio_message']
attachment = f"doc{doc['owner_id']}_{doc['id']}"
vk.messages.send(user_id=user_id, attachment=attachment, random_id=0)
```

---

## Состояния диалога

### State Machine для многошаговых диалогов

```python
from enum import Enum

class State(Enum):
    START = 0
    SELECT_TOUR = 1
    SELECT_DATE = 2
    SELECT_PEOPLE = 3
    CONFIRM = 4

# Хранилище состояний (в продакшене: Redis/DB)
user_states = {}
user_data = {}

@bot.on.message()
async def handler(message: Message):
    uid = message.from_id
    state = user_states.get(uid, State.START)

    if state == State.START:
        user_states[uid] = State.SELECT_TOUR
        user_data[uid] = {}
        await message.answer("Выберите экскурсию:", keyboard=tours_keyboard)

    elif state == State.SELECT_TOUR:
        user_data[uid]['tour'] = message.text
        user_states[uid] = State.SELECT_DATE
        await message.answer("Укажите дату (ДД.ММ.ГГГГ):")

    elif state == State.SELECT_DATE:
        user_data[uid]['date'] = message.text
        user_states[uid] = State.SELECT_PEOPLE
        await message.answer("Сколько человек? (1-20)")

    elif state == State.SELECT_PEOPLE:
        user_data[uid]['people'] = int(message.text)
        user_states[uid] = State.CONFIRM
        data = user_data[uid]
        await message.answer(
            f"Подтвердите бронирование:\n"
            f"Тур: {data['tour']}\n"
            f"Дата: {data['date']}\n"
            f"Человек: {data['people']}\n\n"
            f"Отправьте 'да' для подтверждения",
            keyboard=confirm_keyboard
        )

    elif state == State.CONFIRM:
        if message.text.lower() == 'да':
            # Сохранить в БД, уведомить менеджера
            await message.answer("Заявка принята! Менеджер свяжется с вами.")
        user_states.pop(uid, None)
        user_data.pop(uid, None)
```

### State Machine через vkbottle (FSM)

```python
from vkbottle.bot import Bot, Message
from vkbottle import BaseStateGroup
from vkbottle.dispatch.rules.bot import StateRule

class BookingState(BaseStateGroup):
    TOUR = "tour"
    DATE = "date"
    PEOPLE = "people"

@bot.on.message(text="/book")
async def start_booking(message: Message):
    await bot.state_dispenser.set(message.peer_id, BookingState.TOUR)
    await message.answer("Какую экскурсию выбираете?")

@bot.on.message(StateRule(BookingState.TOUR))
async def select_tour(message: Message):
    await bot.state_dispenser.set(message.peer_id, BookingState.DATE, tour=message.text)
    await message.answer("На какую дату?")

@bot.on.message(StateRule(BookingState.DATE))
async def select_date(message: Message):
    ctx = await bot.state_dispenser.get(message.peer_id)
    await bot.state_dispenser.set(message.peer_id, BookingState.PEOPLE,
                                   tour=ctx.payload.get("tour"), date=message.text)
    await message.answer("Сколько человек?")

@bot.on.message(StateRule(BookingState.PEOPLE))
async def confirm(message: Message):
    ctx = await bot.state_dispenser.get(message.peer_id)
    await bot.state_dispenser.delete(message.peer_id)
    await message.answer(
        f"Бронирование:\n{ctx.payload['tour']}\n{ctx.payload['date']}\n{message.text} чел.\nПринято!"
    )
```

---

## VK Pay

### Кнопка VK Pay в клавиатуре

```python
keyboard_json = {
    "one_time": False,
    "buttons": [[
        {
            "action": {
                "type": "vkpay",
                "hash": "action=pay-to-group&amount=250&description=Desert+Safari&group_id=123456&aid=789"
            }
        }
    ]]
}

vk.messages.send(
    user_id=user_id,
    message="Оплатите экскурсию Desert Safari (250 AED):",
    keyboard=json.dumps(keyboard_json),
    random_id=0
)
```

### Параметры hash

| Параметр | Описание |
|----------|----------|
| `action=pay-to-group` | Перевод в сообщество |
| `amount` | Сумма (целое число) |
| `description` | Описание платежа |
| `group_id` | ID сообщества |
| `aid` | ID приложения |
| `action=pay-to-user` | Перевод пользователю |
| `action=pay-to-service` | Оплата сервиса |

### Проверка поддержки VK Pay

```python
# Проверить client_info перед отправкой кнопки VK Pay
if 'vkpay' in event.object.client_info.button_actions:
    # Клиент поддерживает VK Pay
    send_vkpay_keyboard()
else:
    send_alternative_payment_link()
```

---

## VK Mini Apps

### Запуск Mini App из бота

```python
keyboard_json = {
    "one_time": False,
    "buttons": [[
        {
            "action": {
                "type": "open_app",
                "app_id": 7654321,
                "owner_id": -123456,
                "label": "Бронирование онлайн",
                "hash": "tour=desert&date=2026-03-01"
            }
        }
    ]]
}
```

### Обмен данными: Mini App -> Бот

Mini App может отправлять данные через VK Bridge:

```javascript
// Внутри Mini App (JavaScript)
import bridge from '@vkontakte/vk-bridge';

// Отправить сообщение от имени пользователя
bridge.send('VKWebAppAllowMessagesFromGroup', { group_id: 123456 })
  .then(() => {
    // Пользователь разрешил сообщения
    bridge.send('VKWebAppSendPayload', {
      group_id: 123456,
      payload: { action: 'booking', tour: 'desert', date: '2026-03-01' }
    });
  });
```

---

## Рассылки

### Получение разрешения

Пользователь должен явно разрешить сообщения от сообщества. Отслеживается через события:

- `message_allow` - разрешил
- `message_deny` - запретил

```python
@bot.on.raw_event(GroupEventType.MESSAGE_ALLOW, GroupTypes.MessageAllow)
async def on_allow(event: GroupTypes.MessageAllow):
    user_id = event.object.user_id
    # Добавить в список рассылки (БД)
    save_subscriber(user_id)

@bot.on.raw_event(GroupEventType.MESSAGE_DENY, GroupTypes.MessageDeny)
async def on_deny(event: GroupTypes.MessageDeny):
    user_id = event.object.user_id
    # Удалить из рассылки
    remove_subscriber(user_id)
```

### Массовая рассылка

```python
import asyncio

async def broadcast(user_ids: list, message: str):
    """Рассылка с учётом rate limit (20 req/sec)."""
    for i in range(0, len(user_ids), 20):
        batch = user_ids[i:i+20]
        tasks = [
            bot.api.messages.send(
                user_id=uid, message=message, random_id=0
            ) for uid in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for uid, result in zip(batch, results):
            if isinstance(result, Exception):
                print(f"Error sending to {uid}: {result}")
        await asyncio.sleep(1)  # Пауза между батчами
```

### Лимиты рассылок

- Отправка **только подписчикам**, давшим разрешение
- При массовой отправке учитывайте rate limit (20 req/sec)
- Используйте `execute` для пакетной отправки (до 25 messages.send за 1 вызов)
- VK может ограничить бота при жалобах на спам

---

## Rate Limits и execute

### Ограничения

| Тип токена | Лимит | Примечание |
|-----------|-------|------------|
| Community Token | 20 req/sec | Для бота сообщества |
| User Token | 3 req/sec | Для действий от имени пользователя |
| execute | 25 вызовов за 1 запрос | Считается как 1 запрос к лимиту |

### Метод execute (пакетные запросы)

```python
# Отправить 25 сообщений за 1 запрос
code = """
var users = [1001, 1002, 1003, 1004, 1005];
var i = 0;
var results = [];
while (i < users.length) {
    results.push(API.messages.send({
        "user_id": users[i],
        "message": "Акция! Desert Safari со скидкой 20%!",
        "random_id": 0
    }));
    i = i + 1;
}
return results;
"""

vk.execute(code=code)
```

### Обработка ошибок

| Код | Ошибка | Решение |
|-----|--------|---------|
| 6 | Too many requests per second | Пауза 0.5-1 сек, retry |
| 7 | Permission denied | Проверить права токена |
| 9 | Flood control | Слишком много однотипных действий, пауза 5 сек |
| 10 | Internal server error | Retry через 1 сек |
| 14 | Captcha needed | Обработать captcha (captcha_sid + captcha_key) |
| 100 | Invalid parameter | Проверить параметры запроса |
| 901 | Can't send to user from blacklist | Пользователь заблокировал бота |
| 902 | Can't send due to privacy settings | Нет разрешения на сообщения |

```python
import time
from vk_api.exceptions import ApiError

def safe_send(vk, user_id, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return vk.messages.send(
                user_id=user_id, message=message, random_id=0
            )
        except ApiError as e:
            if e.code == 6:  # Rate limit
                time.sleep(1)
                continue
            elif e.code in (901, 902):  # User blocked/denied
                return None  # Пропустить
            else:
                raise
    raise Exception("Max retries exceeded")
```

---

## Примеры для туризма ОАЭ

### Бот-каталог экскурсий (полный пример)

```python
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Callback, Text, KeyboardButtonColor, GroupEventType, GroupTypes
import json

bot = Bot("YOUR_TOKEN")

TOURS = {
    "desert": {"name": "Desert Safari", "price": 250, "duration": "6ч (15:00-21:00)",
               "desc": "Джипы по дюнам, верблюды, ужин BBQ, шоу"},
    "city": {"name": "City Tour", "price": 150, "duration": "4ч (09:00-13:00)",
             "desc": "Burj Khalifa, Dubai Mall, Old Dubai, Gold Souk"},
    "yacht": {"name": "Yacht Marina", "price": 300, "duration": "3ч (17:00-20:00)",
              "desc": "Яхта, напитки, закуски, виды на Marina"},
    "abudhabi": {"name": "Abu Dhabi Tour", "price": 200, "duration": "10ч (08:00-18:00)",
                 "desc": "Sheikh Zayed Mosque, Louvre, Qasr Al Watan"},
}

def main_menu():
    return (
        Keyboard(one_time=False)
        .add(Text("Desert Safari"), color=KeyboardButtonColor.POSITIVE)
        .add(Text("City Tour"), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Yacht Marina"), color=KeyboardButtonColor.PRIMARY)
        .add(Text("Abu Dhabi"), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Контакты"), color=KeyboardButtonColor.NEGATIVE)
        .add(Text("FAQ"), color=KeyboardButtonColor.SECONDARY)
    )

def tour_inline(tour_id):
    return (
        Keyboard(inline=True)
        .add(Callback("Забронировать", payload={"cmd": "book", "tour": tour_id}))
        .add(Callback("Назад", payload={"cmd": "menu"}))
    )

@bot.on.message(text=["начать", "привет", "старт", "/start"])
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в Dubai Tours!\nВыберите экскурсию из меню:",
        keyboard=main_menu()
    )

@bot.on.message(text=["desert safari", "desert", "пустыня", "сафари"])
async def desert(message: Message):
    t = TOURS["desert"]
    await message.answer(
        f"{t['name']}\n\nЦена: {t['price']} AED/чел\n"
        f"Время: {t['duration']}\n\n{t['desc']}",
        keyboard=tour_inline("desert")
    )

# Аналогично для city, yacht, abudhabi...

@bot.on.message(text=["контакты", "контакт"])
async def contacts(message: Message):
    await message.answer(
        "Dubai Tours\n"
        "Тел: +971 50 XXX XXXX\n"
        "WhatsApp: +971 50 XXX XXXX\n"
        "Локация: Dubai, Tecom (Barsha Heights)\n"
        "Метро: Dubai Internet City"
    )

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, GroupTypes.MessageEvent)
async def callback_handler(event: GroupTypes.MessageEvent):
    payload = event.object.payload
    if payload.get("cmd") == "book":
        tour = TOURS.get(payload.get("tour"))
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=json.dumps({
                "type": "show_snackbar",
                "text": f"Заявка на {tour['name']} принята! Менеджер свяжется."
            })
        )
        # Отправить подтверждение в чат
        await bot.api.messages.send(
            user_id=event.object.user_id,
            message=f"Заявка принята!\n{tour['name']} - {tour['price']} AED\n"
                    f"Менеджер свяжется в течение 10 минут.",
            random_id=0
        )

bot.run_forever()
```

---

## Деплой

### Python (vkbottle / vk_api)

```bash
# Установка
pip install vkbottle   # Асинхронный фреймворк (рекомендуется)
pip install vk_api     # Синхронная библиотека (проще)

# Запуск Long Poll
python bot.py

# Production с systemd
sudo nano /etc/systemd/system/vkbot.service
```

```ini
[Unit]
Description=VK Bot
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/vkbot
ExecStart=/opt/vkbot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Node.js (vk-io)

```bash
npm install vk-io
node bot.js

# Production с pm2
npm install -g pm2
pm2 start bot.js --name vkbot
pm2 startup
pm2 save
```

### Serverless (Callback API)

**Yandex Cloud Functions:**

```python
import json
import vk_api

CONFIRMATION = 'abc123'
VK_TOKEN = 'YOUR_TOKEN'

def handler(event, context):
    body = json.loads(event['body'])

    if body['type'] == 'confirmation':
        return {'statusCode': 200, 'body': CONFIRMATION}

    if body['type'] == 'message_new':
        vk = vk_api.VkApi(token=VK_TOKEN).get_api()
        msg = body['object']['message']
        vk.messages.send(
            user_id=msg['from_id'],
            message="Привет из Cloud Functions!",
            random_id=0
        )

    return {'statusCode': 200, 'body': 'ok'}
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

---

## Библиотеки

### Python

| Библиотека | Тип | GitHub Stars | Особенности |
|-----------|-----|-------------|-------------|
| **vkbottle** | Async framework | 600+ | FSM, middleware, правила, типы |
| **vk_api** | Sync library | 1200+ | Простота, широкое комьюнити |
| **vk-botting** | Discord.py-style | 50+ | Привычный API для Discord-разработчиков |

**Рекомендация:** vkbottle для новых проектов (async, типы, FSM из коробки).

### Node.js

| Библиотека | Тип | Особенности |
|-----------|-----|-------------|
| **vk-io** | Modern SDK | TypeScript, middleware, polling+callback |
| **node-vk-bot-api** | Lightweight | Простой API, Long Poll + Callback |

**Рекомендация:** vk-io (активно поддерживается, TypeScript).

### Другие языки

| Язык | Библиотека |
|------|-----------|
| PHP | vk-php-sdk (официальная) |
| Go | govkbot |
| Rust | vk-bot |
| C# | VkNet |

---

## Ссылки на references

- **[faq.md](references/faq.md)** - 15 частых вопросов по VK ботам
- **[troubleshooting.md](references/troubleshooting.md)** - 15 типичных проблем и решений
- **[cheatsheet.md](references/cheatsheet.md)** - Шпаргалка: методы, параметры, лимиты

---

**Версия:** 1.0 | **Дата:** 2026-02-12 | **API:** VK API v5.199
**Автор:** Claude Code Agent для туристического бизнеса в Дубае/ОАЭ

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
