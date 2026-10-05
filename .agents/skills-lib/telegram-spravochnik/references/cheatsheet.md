# Cheatsheet — Telegram Platform

> Боты: шпаргалка по Bot API см. в `telegram-bot-справочник`

---

## Установка библиотек

```bash
# Telethon (рекомендуемый)
pip install telethon

# Pyrogram (альтернатива)
pip install pyrogram tgcrypto

# GramJS (Node.js)
npm install telegram
```

---

## Авторизация

### Telethon
```python
from telethon import TelegramClient

client = TelegramClient('session_name', api_id, api_hash)
await client.start()  # Запросит телефон + код
```

### Pyrogram
```python
from pyrogram import Client

app = Client("session_name", api_id=api_id, api_hash=api_hash)
async with app:
    me = await app.get_me()
```

---

## Каналы

### Создание
```python
# Telethon
from telethon.tl.functions.channels import CreateChannelRequest
await client(CreateChannelRequest(title="Название", about="Описание", megagroup=False))
```

### Публикация
```python
# Telethon — текст
await client.send_message("@channel", "Текст поста", parse_mode='html')

# Telethon — фото
await client.send_file("@channel", "photo.jpg", caption="Подпись")

# Telethon — альбом
await client.send_file("@channel", ['1.jpg', '2.jpg', '3.jpg'])

# Telethon — запланированный пост
from datetime import datetime, timedelta
await client.send_message("@channel", "Текст", schedule=datetime.now() + timedelta(hours=2))
```

### Pyrogram — публикация
```python
await app.send_message("@channel", "Текст")
await app.send_photo("@channel", "photo.jpg", caption="Подпись")
await app.send_media_group("@channel", [InputMediaPhoto("1.jpg"), InputMediaPhoto("2.jpg")])
```

### Управление
```python
# Telethon
from telethon.tl.functions.channels import EditAboutRequest, GetFullChannelRequest

# Изменить описание
await client(EditAboutRequest(channel="@ch", about="Новое описание"))

# Получить инфо
full = await client(GetFullChannelRequest("@ch"))
print(full.full_chat.participants_count)

# Закрепить сообщение
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
await client(UpdatePinnedMessageRequest(peer="@ch", id=msg_id, silent=True))
```

---

## Группы

### Создание супергруппы
```python
await client(CreateChannelRequest(title="Название", about="Описание", megagroup=True))
```

### Права по умолчанию
```python
from telethon.tl.types import ChatBannedRights
rights = ChatBannedRights(until_date=None, send_stickers=True, send_gifs=True)
# Применить через EditChatDefaultBannedRightsRequest
```

### Модерация
```python
# Бан
from telethon.tl.functions.channels import EditBannedRequest
ban = ChatBannedRights(until_date=None, view_messages=True)
await client(EditBannedRequest(channel="@group", participant=user_id, banned_rights=ban))

# Назначение админа
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
rights = ChatAdminRights(post_messages=True, delete_messages=True, ban_users=True)
await client(EditAdminRequest(channel="@group", user_id=user_id, admin_rights=rights, rank="Модератор"))
```

### Slow mode
```python
from telethon.tl.functions.channels import ToggleSlowModeRequest
await client(ToggleSlowModeRequest(channel="@group", seconds=30))
# Допустимые: 0 (выкл), 10, 30, 60, 300, 900, 3600
```

### Участники
```python
# Telethon
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
result = await client(GetParticipantsRequest(channel="@group", filter=ChannelParticipantsSearch(''), offset=0, limit=200, hash=0))

# Pyrogram
async for member in app.get_chat_members("@group"):
    print(member.user.first_name)
```

---

## Stories

```python
# Telethon — публикация Story
from telethon.tl.functions.stories import SendStoryRequest
await client(SendStoryRequest(peer='me', media=media, caption="Текст", period=86400))
```

---

## Статистика

```python
# Telethon — статистика канала (от 50 подписчиков)
from telethon.tl.functions.stats import GetBroadcastStatsRequest
stats = await client(GetBroadcastStatsRequest(channel="@channel"))

# Атрибуты: followers, views_per_post, shares_per_post, reactions_per_post
```

---

## Поиск сообщений

```python
# Telethon
async for msg in client.iter_messages("@channel", search="сафари", limit=50):
    print(f"[{msg.date}] {msg.text[:100]}")

# Pyrogram
async for msg in app.search_messages("@channel", query="сафари", limit=50):
    print(msg.text[:100])
```

---

## Пересылка и копирование

```python
# Telethon
await client.forward_messages("@target", messages=[msg_id], from_peer="@source")

# Pyrogram
await app.forward_messages("@target", "@source", message_ids=[msg_id])
await app.copy_message("@target", "@source", msg_id)  # Без "Forwarded from"
```

---

## Форматирование

### HTML
```html
<b>жирный</b>  <i>курсив</i>  <u>подчёркнутый</u>
<s>зачёркнутый</s>  <code>моноширинный</code>
<a href="url">ссылка</a>  <tg-spoiler>спойлер</tg-spoiler>
<pre language="python">блок кода</pre>
<blockquote>цитата</blockquote>
<tg-emoji emoji-id="ID">кастомный эмодзи</tg-emoji>
```

### Markdown v2
```
*жирный*  _курсив_  __подчёркнутый__  ~зачёркнутый~
`моноширинный`  ||спойлер||  [ссылка](url)
```

---

## Лимиты платформы

| Параметр | Обычный | Premium |
|----------|---------|---------|
| Размер файла | 2 GB | 4 GB |
| Каналов/групп | 500 | 1,000 |
| Папки чатов | 10 | 30 |
| Stories/день | 3 | 100 |
| Закреплённые чаты | 5 | 10 |
| Bio-ссылки | 1 | 5 |
| Подпись канала | 70 символов | 70 символов |
| Описание канала | 255 символов | 255 символов |
| Участников в группе | 200,000 | 200,000 |
| Фото в альбоме | 10 | 10 |
| Текст сообщения | 4,096 символов | 4,096 символов |
| Подпись медиа | 1,024 символов | 2,048 символов |

---

## FloodWait — обработка

```python
# Telethon
from telethon.errors import FloodWaitError
try:
    await client.send_message(...)
except FloodWaitError as e:
    await asyncio.sleep(e.seconds)
    await client.send_message(...)

# Pyrogram — автоматическая обработка (встроена)
```

---

## Примерные rate limits MTProto

| Действие | Лимит |
|----------|-------|
| Сообщения разным чатам | ~30/сек |
| Сообщения одному чату | ~1/сек |
| Добавление в группу | ~20 за раз |
| Поиск пользователей | ~200/15 мин |
| Создание каналов | ~10/день |
| Присоединение к каналам | ~50/день |

---

## Telegram Ads — ключевое

| Параметр | Значение |
|----------|----------|
| Платформа | https://ads.telegram.org |
| Формат | До 160 символов + кнопка |
| Показ | Каналы 1000+ подписчиков |
| Оплата | CPM (за 1000 показов) |
| Мин. CPM | 0.1 TON (~$0.30–$0.50) |
| Таргетинг | Каналы, язык, тематика |

---

## Telegram Business — Quick Reference

| Функция | Описание |
|---------|----------|
| Business Hours | Часы работы в профиле |
| Business Location | Адрес с картой |
| Greeting Message | Автоответ новым контактам |
| Away Message | Автоответ в нерабочие часы |
| Quick Replies | Шаблоны (/price, /tours) |
| Chatbot Connection | Привязка бота к профилю |
| Chat Tags | Категоризация диалогов |

**Требование:** Telegram Premium ($4.99/мес)

---

## Полезные ссылки

- MTProto API: https://core.telegram.org/api
- TDLib: https://core.telegram.org/tdlib
- Telegram Business: https://core.telegram.org/api/business
- Channel Stats: https://core.telegram.org/api/stats
- Telegram Ads: https://ads.telegram.org
- TGStat: https://tgstat.com
- Telethon Docs: https://docs.telethon.dev
- Pyrogram Docs: https://docs.pyrogram.org
- my.telegram.org: https://my.telegram.org (API credentials)
