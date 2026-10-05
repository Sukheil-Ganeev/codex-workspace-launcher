# VK Bot API: Cheatsheet

## API Endpoint

```
POST https://api.vk.com/method/{METHOD}
```

Обязательные параметры: `access_token`, `v=5.199`

---

## Токены

| Тип | Получение | Rate Limit |
|-----|-----------|-----------|
| Community | Настройки сообщества -> API -> Создать ключ | 20 req/sec |
| User | OAuth Implicit Flow | 3 req/sec |
| Service | Настройки приложения -> Сервисный ключ | 10 req/sec |

---

## Методы сообщений

### messages.send

```python
vk.messages.send(
    user_id=123,              # ID пользователя
    # peer_id=2000000001,     # Для бесед
    message="Текст",          # До 4096 символов
    random_id=0,              # 0 = автогенерация
    keyboard=kb_json,         # JSON клавиатуры
    template=tpl_json,        # JSON карусели
    attachment="photo-1_2",   # Вложения
    reply_to=456,             # Ответ на сообщение
    lat=25.2, long=55.3,      # Геолокация
    dont_parse_links=1,       # Не парсить ссылки
    disable_mentions=1,       # Не уведомлять @
)
```

### messages.sendMessageEventAnswer

```python
vk.messages.send_message_event_answer(
    event_id="abc",
    user_id=123,
    peer_id=123,
    event_data=json.dumps({
        "type": "show_snackbar",  # или "open_link", "open_app"
        "text": "Текст уведомления"  # для snackbar
        # "link": "https://..."     # для open_link
        # "app_id": 123, "hash": "" # для open_app
    })
)
```

### messages.edit

```python
vk.messages.edit(
    peer_id=123,
    message_id=456,
    message="Новый текст",
    keyboard=new_kb_json,      # Можно обновить клавиатуру
    attachment="photo-1_2",    # Можно обновить вложения
)
```

### messages.delete

```python
vk.messages.delete(
    message_ids="123,456",
    delete_for_all=1,          # Удалить для всех
)
```

### messages.getConversations

```python
vk.messages.getConversations(
    offset=0,
    count=20,
    filter="unread",  # all, unread, important, unanswered
)
```

---

## Long Poll

### groups.getLongPollServer

```python
lp = vk.groups.getLongPollServer(group_id=123456)
# -> {server, key, ts}
```

### Запрос обновлений

```
GET {server}?act=a_check&key={key}&ts={ts}&wait=25
```

### Коды failed

| Код | Действие |
|-----|---------|
| 1 | Использовать ts из ответа |
| 2 | Запросить новый key |
| 3 | Запросить новые key + ts |

---

## Клавиатуры

### JSON структура Reply Keyboard

```json
{
  "one_time": false,
  "buttons": [
    [
      {"action": {"type": "text", "label": "Кнопка", "payload": "{\"cmd\":\"test\"}"}, "color": "primary"},
      {"action": {"type": "text", "label": "Кнопка 2"}, "color": "positive"}
    ],
    [
      {"action": {"type": "open_link", "label": "Сайт", "link": "https://example.com"}}
    ]
  ]
}
```

### JSON структура Inline Keyboard

```json
{
  "inline": true,
  "buttons": [
    [
      {"action": {"type": "callback", "label": "Нажми", "payload": "{\"cmd\":\"click\"}"}},
      {"action": {"type": "open_link", "label": "Ссылка", "link": "https://example.com"}}
    ]
  ]
}
```

### Типы кнопок

| type | Параметры | Описание |
|------|-----------|----------|
| `text` | label, payload, color | Отправляет текст |
| `callback` | label, payload | Событие message_event |
| `open_link` | label, link | Открывает URL |
| `location` | payload | Запрос геолокации |
| `vkpay` | hash | Платеж VK Pay |
| `open_app` | app_id, owner_id, label, hash | Открывает Mini App |

### Цвета (color)

| Значение | Вид |
|----------|-----|
| `primary` | Синий |
| `positive` | Зеленый |
| `negative` | Красный |
| `secondary` | Белый |

### Убрать клавиатуру

```json
{"buttons": [], "one_time": true}
```

---

## Карусель (template)

```json
{
  "type": "carousel",
  "elements": [
    {
      "title": "Заголовок",
      "description": "Описание",
      "photo_id": "-123_456",
      "action": {"type": "open_link", "link": "https://..."},
      "buttons": [
        {"action": {"type": "callback", "label": "Кнопка", "payload": "{}"}}
      ]
    }
  ]
}
```

**Лимиты:** 1-10 элементов, title до 80 симв., description до 80 симв., до 3 кнопок.

---

## Загрузка медиа

### Фото в сообщение

```python
# 1. Upload URL
upload = vk.photos.getMessagesUploadServer(peer_id=UID)
# 2. POST файл
resp = requests.post(upload['upload_url'], files={'photo': open('img.jpg','rb')}).json()
# 3. Сохранить
saved = vk.photos.saveMessagesPhoto(server=resp['server'], photo=resp['photo'], hash=resp['hash'])[0]
# 4. Attachment
att = f"photo{saved['owner_id']}_{saved['id']}"
```

### Документ в сообщение

```python
upload = vk.docs.getMessagesUploadServer(type='doc', peer_id=UID)
resp = requests.post(upload['upload_url'], files={'file': open('doc.pdf','rb')}).json()
saved = vk.docs.save(file=resp['file'], title="Документ")
att = f"doc{saved['doc']['owner_id']}_{saved['doc']['id']}"
```

### Голосовое сообщение

```python
upload = vk.docs.getMessagesUploadServer(type='audio_message', peer_id=UID)
# Далее аналогично документу
```

---

## execute (пакетные запросы)

```python
code = """
var results = [];
var users = [1001, 1002, 1003];
var i = 0;
while (i < users.length) {
    results.push(API.messages.send({
        "user_id": users[i],
        "message": "Привет!",
        "random_id": 0
    }));
    i = i + 1;
}
return results;
"""
vk.execute(code=code)
```

**Лимит:** до 25 вызовов API в одном execute.

---

## События Callback API

| Событие | Описание |
|---------|----------|
| `confirmation` | Подтверждение сервера |
| `message_new` | Новое сообщение |
| `message_reply` | Ответ бота |
| `message_edit` | Редактирование |
| `message_event` | Callback-кнопка |
| `message_allow` | Разрешил сообщения |
| `message_deny` | Запретил сообщения |
| `message_typing_state` | Печатает |
| `wall_post_new` | Новый пост |
| `wall_reply_new` | Новый комментарий |
| `group_join` | Вступление |
| `group_leave` | Выход |

---

## Коды ошибок API

| Код | Описание |
|-----|----------|
| 1 | Unknown error |
| 5 | User authorization failed |
| 6 | Too many requests per second |
| 7 | Permission denied |
| 9 | Flood control |
| 10 | Internal server error |
| 14 | Captcha needed |
| 15 | Access denied |
| 100 | Invalid parameter |
| 901 | User in blacklist |
| 902 | Privacy settings |
| 913 | Message too long |
| 914 | Message forwarding error |
| 917 | Contact not found |
| 936 | Too many forwarded messages |
| 940 | Too many attachments |
| 944 | Message already pinned |
| 945 | Too many keyboards |

---

## Quick Reference: vkbottle

```python
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, Callback, OpenLink, KeyboardButtonColor
from vkbottle import GroupEventType, GroupTypes, BaseStateGroup

bot = Bot("TOKEN")

# Текстовый handler
@bot.on.message(text="привет")
async def hi(m: Message): await m.answer("Привет!")

# Regex handler
@bot.on.message(text=["цена <tour>", "стоимость <tour>"])
async def price(m: Message, tour: str): await m.answer(f"Цена {tour}: 250 AED")

# Callback handler
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, GroupTypes.MessageEvent)
async def cb(event: GroupTypes.MessageEvent):
    await bot.api.messages.send_message_event_answer(...)

# FSM
class S(BaseStateGroup):
    STEP1 = "s1"

bot.run_forever()
```

---

## Quick Reference: vk-io

```javascript
const { VK, Keyboard } = require('vk-io');
const vk = new VK({ token: 'TOKEN' });

// Текстовый handler
vk.updates.on('message_new', async (ctx) => {
  if (ctx.text === 'привет') await ctx.send('Привет!');
});

// Callback handler
vk.updates.on('message_event', async (ctx) => {
  await ctx.answer({ type: 'show_snackbar', text: 'OK!' });
});

// Клавиатура
const kb = Keyboard.builder()
  .textButton({ label: 'Кнопка', color: 'positive', payload: { cmd: 'test' } })
  .row()
  .callbackButton({ label: 'Callback', payload: { cmd: 'cb' } })
  .inline();

await ctx.send({ message: 'Меню', keyboard: kb });

vk.updates.start();
```

---

## VK Pay кнопка

```json
{
  "action": {
    "type": "vkpay",
    "hash": "action=pay-to-group&amount=250&description=Desert+Safari&group_id=123456&aid=789"
  }
}
```

---

## Полезные ссылки

- Методы API: https://dev.vk.com/ru/method
- Клавиатуры: https://dev.vk.com/ru/api/bots/development/keyboard
- Long Poll: https://dev.vk.com/ru/api/bots-long-poll/getting-started
- Callback: https://dev.vk.com/ru/api/callback/getting-started
- vkbottle: https://github.com/vkbottle/vkbottle
- vk_api: https://github.com/python273/vk_api
- vk-io: https://github.com/negezor/vk-io

---

*Часть VK Bot API справочника | Версия 1.0 | 2026-02-12*
