---
name: telegram-spravochnik
description: "Production-ready руководство по платформе Telegram для туристического бизнеса ОАЭ. Каналы, группы, контент, Premium, Ads, Mini Apps, аналитика. Используй когда нужно работать с каналами, группами, рекламой Telegram (НЕ боты)."
---
# Telegram Platform — Production Guide для туризма ОАЭ

> Боты: см. `telegram-bot-справочник` — полный справочник по Telegram Bot API (BotFather, webhooks, inline-кнопки, платежи, деплой)

---

## 1. Обзор API — MTProto vs Bot API vs TDLib

### Три уровня доступа к Telegram

| Параметр | Bot API | TDLib | MTProto (raw) |
|----------|---------|-------|---------------|
| Назначение | Боты | Клиентские приложения | Низкоуровневый протокол |
| Язык | REST/JSON | C++, обёртки для всех ЯП | Любой (ручная реализация) |
| Авторизация | Токен от BotFather | api_id + api_hash + сессия | api_id + api_hash |
| Возможности | Ограничены ботовым контекстом | Полный доступ к платформе | Полный, но сырой |
| Каналы/группы | Только если бот — админ | Полный контроль | Полный контроль |
| Stories | Только через бот-бизнес | Полный доступ | Полный доступ |
| Сложность | Низкая | Средняя | Очень высокая |

### Когда что использовать

- **Bot API** — автоматизация через бота: уведомления, бронирования, каталоги. См. `telegram-bot-справочник`
- **TDLib / Telethon / Pyrogram** — управление каналами, публикация контента, автопостинг, аналитика, парсинг
- **Raw MTProto** — разработка собственного Telegram-клиента (не рекомендуется для бизнеса)

**Для туристического бизнеса:** TDLib-обёртки (Telethon, Pyrogram) для контент-менеджмента каналов + Bot API для клиентского бота.

---

## 2. Аутентификация — API ID, сессии, 2FA

### Получение API ID и Hash

1. Перейти на https://my.telegram.org
2. Войти по номеру телефона (придёт код в Telegram)
3. Раздел "API development tools"
4. Заполнить форму: App title, Short name, Platform
5. Получить `api_id` (число) и `api_hash` (строка)

**Важно:** Один номер = один api_id. Не делитесь api_hash публично.

### Авторизация через Telethon (Python)

```python
from telethon import TelegramClient

api_id = 12345678
api_hash = 'your_api_hash_here'

# Сессия сохраняется в файл dubai_tours.session
client = TelegramClient('dubai_tours', api_id, api_hash)

async def main():
    await client.start()  # Запросит номер телефона и код при первом запуске
    me = await client.get_me()
    print(f"Авторизован как: {me.first_name}")

with client:
    client.loop.run_until_complete(main())
```

### Авторизация через Pyrogram

```python
from pyrogram import Client

app = Client(
    "dubai_tours",
    api_id=12345678,
    api_hash="your_api_hash_here"
)

async def main():
    async with app:
        me = await app.get_me()
        print(f"Авторизован как: {me.first_name}")

app.run(main())
```

### Двухфакторная аутентификация (2FA)

Если на аккаунте включена 2FA, библиотеки запросят пароль при авторизации:

```python
# Telethon — 2FA обрабатывается автоматически при client.start()
# Pyrogram — аналогично, пароль запрашивается в интерактивном режиме

# Для автоматизации можно передать пароль:
await client.start(password="your_2fa_password")
```

### Управление сессиями

- Сессия — это привязка устройства к аккаунту
- Файл `.session` хранит ключи авторизации, не удаляйте его
- Можно иметь несколько сессий (до 10 устройств)
- Просмотр активных сессий: Настройки > Устройства
- Неактивные сессии автоматически завершаются через 6 месяцев (Premium: настраиваемый)

---

## 3. Каналы — создание, контент, управление

### Создание канала через API

```python
# Telethon — создание канала
from telethon.tl.functions.channels import CreateChannelRequest

result = await client(CreateChannelRequest(
    title="Dubai Tours | Экскурсии ОАЭ",
    about="Лучшие экскурсии по Дубаю и ОАЭ. Цены ниже кассы!",
    megagroup=False  # False = канал, True = супергруппа
))
channel = result.chats[0]
print(f"Канал создан: ID {channel.id}")
```

### Публикация контента

```python
# Telethon — публикация поста с фото
await client.send_message(
    "your_channel_username",
    "🏙 **Бурдж Халифа — At The Top**\n\n"
    "Билеты дешевле кассы!\n"
    "▫️ 124+125 этаж: от **250 AED**\n"
    "▫️ 148 этаж (SKY): от **550 AED**\n\n"
    "📍 Downtown Dubai\n"
    "🕐 Ежедневно 10:00–22:00",
    parse_mode='md',
    file='burj_khalifa.jpg'  # Фото к посту
)
```

```python
# Pyrogram — публикация с фото
await app.send_photo(
    chat_id="your_channel_username",
    photo="burj_khalifa.jpg",
    caption=(
        "🏙 **Бурдж Халифа — At The Top**\n\n"
        "Билеты дешевле кассы!\n"
        "▫️ 124+125 этаж: от **250 AED**\n"
        "▫️ 148 этаж (SKY): от **550 AED**"
    ),
    parse_mode="md"  # Поддержка: md, html
)
```

### Медиагруппы (альбомы)

```python
# Telethon — отправка альбома из нескольких фото
await client.send_file(
    "your_channel_username",
    file=['safari1.jpg', 'safari2.jpg', 'safari3.jpg'],
    caption="🏜 Пустынное сафари — лучшие моменты!"
)
```

### Запланированные посты

```python
from datetime import datetime, timedelta

# Telethon — пост через 2 часа
schedule_time = datetime.now() + timedelta(hours=2)
await client.send_message(
    "your_channel_username",
    "🌅 Закат в пустыне — бронируйте Evening Safari!",
    schedule=schedule_time
)
```

### Управление каналом

```python
# Telethon — изменение описания
from telethon.tl.functions.channels import EditAboutRequest

await client(EditAboutRequest(
    channel="your_channel_username",
    about="Экскурсии, билеты, яхты, авто в ОАЭ. Семейный бизнес с 2021 года."
))

# Получение информации о канале
from telethon.tl.functions.channels import GetFullChannelRequest

full = await client(GetFullChannelRequest("your_channel_username"))
print(f"Подписчики: {full.full_chat.participants_count}")
print(f"Описание: {full.full_chat.about}")
```

### Закреплённые сообщения

```python
# Telethon — закрепить сообщение
from telethon.tl.functions.messages import UpdatePinnedMessageRequest

await client(UpdatePinnedMessageRequest(
    peer="your_channel_username",
    id=message_id,
    silent=True  # Без уведомления подписчикам
))
```

---

## 4. Группы и супергруппы

### Типы групп

| Тип | Лимит участников | Особенности |
|-----|-----------------|-------------|
| Базовая группа | 200 | Простой чат, минимум настроек |
| Супергруппа | 200,000 | Полная модерация, топики, slow mode |
| Гигагруппа | 200,000 | Только админы пишут (broadcast) |

### Создание супергруппы

```python
# Telethon
result = await client(CreateChannelRequest(
    title="Dubai Tours — Обсуждение",
    about="Обсуждаем экскурсии, делимся отзывами",
    megagroup=True  # True = супергруппа
))
```

### Права участников и модерация

```python
# Telethon — установка прав по умолчанию
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

# Запретить отправку стикеров и GIF для всех участников
rights = ChatBannedRights(
    until_date=None,  # Бессрочно
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=False,   # Опросы разрешены
    send_messages=False  # Сообщения разрешены
)
await client(EditChatDefaultBannedRightsRequest(
    peer="group_username",
    banned_rights=rights
))
```

### Топики (форум-режим)

С 2022 года супергруппы поддерживают форум-режим — разделение чата на топики (темы).

```python
# Pyrogram — создание топика
from pyrogram.raw.functions.channels import CreateForumTopic

topic = await app.invoke(CreateForumTopic(
    channel=await app.resolve_peer("group_username"),
    title="Отзывы об экскурсиях",
    icon_color=0x6FB9F0  # Голубой
))
```

### Slow Mode

```python
# Telethon — включить slow mode (30 сек между сообщениями)
from telethon.tl.functions.channels import ToggleSlowModeRequest

await client(ToggleSlowModeRequest(
    channel="group_username",
    seconds=30  # 0 = выкл, допустимые: 10, 30, 60, 300, 900, 3600
))
```

---

## 5. Контент и медиа

### Форматирование сообщений

**HTML:**
```html
<b>жирный</b>  <i>курсив</i>  <u>подчёркнутый</u>
<s>зачёркнутый</s>  <code>моноширинный</code>
<a href="https://example.com">ссылка</a>
<pre language="python">блок кода</pre>
<blockquote>цитата</blockquote>
<tg-spoiler>спойлер</tg-spoiler>
<tg-emoji emoji-id="5368324170671202286">кастомный эмодзи</tg-emoji>
```

**Markdown v2 (MarkdownV2):**
```
*жирный*  _курсив_  __подчёркнутый__
~зачёркнутый~  `моноширинный`  ||спойлер||
[ссылка](https://example.com)
```

### Лимиты медиафайлов

| Тип | Макс. размер | Примечания |
|-----|-------------|------------|
| Фото | 10 MB | Сжимается, если >1280px по стороне |
| Видео | 2 GB (4 GB Premium) | Поддержка потокового воспроизведения |
| Аудио | 2 GB (4 GB Premium) | MP3, OGG, WAV |
| Документ | 2 GB (4 GB Premium) | Любой формат |
| Голосовое | 2 GB | OGG Opus |
| Видеосообщение | 2 GB | Круглое видео (до 60 сек) |
| Стикер | 512 KB | WebP, TGS (анимация), WebM (видео) |
| Альбом | 10 файлов | Фото/видео/документы |

### Кастомные эмодзи (Premium)

Premium-пользователи могут использовать кастомные эмодзи в сообщениях. Для каналов — кастомные эмодзи доступны в любых постах.

```python
# Telethon — отправка с кастомным эмодзи (через HTML)
await client.send_message(
    "your_channel_username",
    '<tg-emoji emoji-id="5368324170671202286">🎯</tg-emoji> Новое предложение!',
    parse_mode='html'
)
```

---

## 6. Telegram Stories

### Возможности Stories

- Публикация фото и видео (до 60 сек)
- Срок жизни: 6 / 12 / 24 / 48 часов (Premium: бессрочные)
- Premium: до 100 Stories в день (без Premium: 3)
- Интерактивные виджеты: ссылки, реакции, местоположение
- Аналитика просмотров: кто смотрел, реакции
- Каналы тоже могут публиковать Stories

### Публикация Stories через API

```python
# Telethon — публикация Story
from telethon.tl.functions.stories import SendStoryRequest
from telethon.tl.types import InputMediaUploadedPhoto

# Загрузка фото
file = await client.upload_file('story_desert_sunset.jpg')
media = InputMediaUploadedPhoto(file=file)

await client(SendStoryRequest(
    peer='me',  # или канал
    media=media,
    caption="Закат в пустыне #DubaiSafari",
    period=86400,  # 24 часа в секундах
    privacy_rules=[...]  # Правила видимости
))
```

### Бизнес-применение Stories

- **Ежедневные анонсы:** фото и видео с экскурсий в реальном времени
- **Срочные акции:** "Только сегодня -20% на Desert Safari!"
- **Закулисье:** офис, подготовка к туру, водители, яхты
- **Отзывы:** скриншоты благодарностей от клиентов
- **Ссылки** (Premium): кнопка "Забронировать" ведёт на сайт/бот

### Поиск Stories (2025)

С 2025 года Stories доступны для поиска по хэштегам и геолокации — дополнительный канал органического охвата.

---

## 7. Telegram Premium

### Лимиты: Premium vs Обычный

| Параметр | Обычный | Premium |
|----------|---------|---------|
| Размер файла | 2 GB | 4 GB |
| Скорость загрузки | Ограничена | Без лимита |
| Каналов/групп | 500 | 1,000 |
| Папки чатов | 10 | 30 |
| Чатов в папке | 100 | 200 |
| Закреплённые чаты | 5 | 10 |
| Избранные стикеры | 5 | 10 |
| Stories в день | 3 | 100 |
| Подпись Stories | Нет | Да (ссылки, виджеты) |
| Транскрипция голосовых | Нет | Да |
| Реакции на сообщение | 1 | 3 |
| Кастомные эмодзи | Нет | Да |
| Аккаунтов в приложении | 3 | 4 |
| Bio-ссылки | 1 | 5 |
| Публичные @username | 1 | Коллекционные |

### Стоимость

- iOS / Android: $4.99/мес
- Telegram Stars: оплата через внутреннюю валюту
- Годовая подписка со скидкой

### Бизнес-выгода Premium

- Быстрая загрузка файлов до 4 GB (ваучеры, каталоги PDF)
- 1,000 каналов — мониторинг конкурентов без ограничений
- Транскрипция голосовых — быстрая обработка аудио-запросов клиентов
- 100 Stories в день — агрессивный контент-маркетинг

---

## 8. Telegram Business

### Обзор

Telegram Business — набор инструментов для бизнес-аккаунтов, доступный подписчикам Premium ($4.99/мес).

### Функции Telegram Business

**Бизнес-профиль:**
- Часы работы (Business Hours) — отображаются в профиле
- Местоположение (Business Location) — адрес с картой
- Ссылка на начало чата (Intro) — кастомная приветственная страница

**Автоматизация сообщений:**
- Приветственные сообщения (Greeting Messages) — автоответ новым контактам
- Сообщения об отсутствии (Away Messages) — автоответ в нерабочие часы
- Быстрые ответы (Quick Replies) — шаблоны по ярлыкам (/price, /tours, /yacht)

**Интеграция с ботом:**
- Chatbot Connection — привязка бота к бизнес-аккаунту
- Бот обрабатывает запросы от имени бизнес-профиля
- Чат-теги (Chat Tags) — категоризация диалогов

### Настройка через API

```python
# Pyrogram — установка бизнес-часов (через raw API)
# Telegram Business настраивается через клиентское приложение
# API-доступ: через MTProto / TDLib

# Пример: проверка бизнес-профиля пользователя
user = await app.get_users("username")
if user.business:
    print(f"Часы работы: {user.business.opening_hours}")
    print(f"Локация: {user.business.location}")
```

### Применение для туризма ОАЭ

- **Business Hours:** 09:00–21:00 GST (UTC+4), показываем клиентам из СНГ
- **Away Message:** "Спасибо за обращение! Мы ответим в рабочие часы (09:00–21:00 по Дубаю). Срочно: +971-XX-XXX-XXXX"
- **Quick Replies:** /price — прайс-лист, /safari — Desert Safari, /yacht — каталог яхт
- **Greeting:** "Добро пожаловать! Мы — семейная компания в Дубае. Экскурсии, яхты, авто. Чем помочь?"

---

## 9. Telegram Ads — рекламная платформа

### Обзор платформы

- Официальная площадка: https://ads.telegram.org
- Реклама показывается в публичных каналах с 1,000+ подписчиков
- Формат: спонсированное сообщение (до 160 символов + кнопка)
- Модель оплаты: CPM (cost per 1,000 показов)

### Стоимость

| Параметр | Значение |
|----------|----------|
| Минимальный CPM | 0.1 TON (~$0.30–$0.50) |
| Средний CPM (крипто-дашборд) | 0.1–0.5 TON |
| Средний CPM (стандартный) | EUR 1–2 |
| Медиа-формат наценка | 50–80% |
| Минимальный бюджет | От 50 EUR (через реселлеров) |

### Таргетинг

- **По каналам:** Указать конкретные каналы для показа (например, туристические каналы)
- **По языку:** RU, EN, AR и другие
- **По тематике:** Travel, Lifestyle, Business
- **По стране:** Таргетинг через язык аудитории (не по IP)
- **Исключения:** Блокировка нежелательных каналов

**Важно:** Таргетинг в Telegram основан на подписках пользователей, а не на cookies или поисковых запросах — высокая релевантность.

### Форматы рекламы (2026)

1. **Спонсированное сообщение** — текст до 160 символов + кнопка
2. **Медиа-реклама** — фото/видео + текст (повышенный CPM)
3. **Мини-приложение** — кнопка открывает Mini App

### Пример для туризма ОАЭ

```
Текст: Экскурсии по Дубаю от $50. Билеты дешевле кассы! Сафари, Бурдж Халифа, яхты.
Кнопка: "Посмотреть каталог" → @your_bot или t.me/your_channel

Таргетинг:
- Каналы: туристические RU-каналы про ОАЭ, travel-блоги
- Язык: Русский
- Бюджет: 100–500 EUR/неделя (тестовый запуск)
```

---

## 10. Mini Apps (платформенная часть)

### Обзор

Mini Apps (ранее Web Apps) — веб-приложения внутри Telegram с доступом к нативным функциям.

### Масштаб платформы (2026)

- 500+ млн пользователей ежемесячно взаимодействуют с Mini Apps
- Поддержка полноэкранного режима (2025)
- Подписки через Telegram Stars
- Иконка на домашний экран устройства

### Ключевые возможности

- **Полноэкранный режим** — полное погружение без элементов Telegram
- **Telegram Stars** — оплата внутри Mini App (подписки, покупки)
- **Геолокация** — доступ к GPS пользователя (с разрешением)
- **Гироскоп** — motion tracking для интерактивных элементов
- **Домашний экран** — ярлык Mini App на устройстве пользователя
- **Отправка медиа** — шаринг фото/видео из Mini App в чат

### Telegram Stars — внутренняя валюта

| Параметр | Значение |
|----------|----------|
| Покупка Stars | Через App Store / Google Play |
| Курс | ~$0.013 за Star (зависит от объёма) |
| Комиссия разработчика | 0% (Telegram не берёт комиссию) |
| Вывод | В TON (криптовалюта) через Fragment |
| Подписки | Рекуррентные платежи через Stars |

### Пример для туризма

Mini App "Каталог экскурсий" — веб-приложение с интерактивным каталогом:
- Каталог с фото, ценами, описаниями
- Выбор даты и количества человек
- Оплата через Stars или внешние платёжные системы
- Интеграция с геолокацией: ближайшие достопримечательности

---

## 11. Аналитика — встроенная и внешняя

### Встроенная статистика Telegram

**Доступна:** каналы от 50 подписчиков, группы от 500 участников.

**Метрики каналов:**
- Рост подписчиков (по дням, неделям, месяцам)
- Охват постов (всего просмотров, уникальных)
- Уведомления (% подписчиков с включёнными уведомлениями)
- Источники подписчиков (поиск, ссылки, другие каналы)
- Взаимодействия (реакции, репосты, комментарии)
- Язык и география аудитории

**Метрики постов:**
- Просмотры (с разбивкой по часам)
- Реакции и репосты
- Переходы по ссылкам

**Ограничения:**
- Графики хранятся 90 дней
- Исторический экспорт — до 1 года
- getMessageStatistics: приблизительные данные для постов старше 7 дней

### Получение статистики через API

```python
# Telethon — статистика канала
from telethon.tl.functions.stats import GetBroadcastStatsRequest

stats = await client(GetBroadcastStatsRequest(
    channel="your_channel_username"
))
print(f"Подписчики: {stats.followers.current}")
print(f"Просмотры на пост: {stats.views_per_post.current}")
print(f"Репосты на пост: {stats.shares_per_post.current}")
```

### TGStat — внешняя аналитика

**Охват:** 2.5+ млн каналов, 40+ стран

**Метрики TGStat:**
- ERR (Engagement Rate by Reach) — вовлечённость к охвату
- CI (Citation Index) — индекс цитирования
- Рост подписчиков (почасовой с источниками)
- Охват постов (средний, медиана)
- Сравнение каналов

**API TGStat (платный):**
- Stat API — статистика каналов
- Search API — поиск каналов/постов
- Callback API — уведомления об изменениях

**Точность:** ~95% по подписчикам, ~90% по вовлечённости, обновление каждые 6–12 часов.

### Другие инструменты аналитики

| Сервис | Особенности | Стоимость |
|--------|-------------|-----------|
| TGStat | Крупнейший каталог, API, CIS-фокус | Freemium / от $10/мес |
| Telemetr.io | Детальный анализ, прогнозы | Freemium |
| Popsters | Кросс-платформенная аналитика | от $9.99/мес |
| Brand24 | Мониторинг упоминаний | от $79/мес |
| Combot | Аналитика групп, модерация | Freemium |

### Ключевые метрики для туризма ОАЭ

- **ERR >5%** — хорошая вовлечённость для туристического канала
- **Охват 30–50%** — здоровый канал без ботов
- **Рост 1–5% в месяц** — стабильный органический рост
- **Лучшее время постинга:** 10:00–12:00 и 18:00–20:00 МСК (13:00–15:00 и 21:00–23:00 GST) — пиковая активность аудитории СНГ

---

## 12. Библиотеки — Telethon, Pyrogram, GramJS, TDLib

### Telethon (Python) — рекомендуемый

```bash
pip install telethon
```

- Асинхронный (asyncio)
- Полный доступ к MTProto API
- Отличная документация: https://docs.telethon.dev
- Активное сообщество

**Ключевые возможности:**
```python
# Получение всех участников группы
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

participants = await client(GetParticipantsRequest(
    channel="group_username",
    filter=ChannelParticipantsSearch(''),
    offset=0,
    limit=200,
    hash=0
))
print(f"Участников: {participants.count}")

# Поиск сообщений в канале
async for message in client.iter_messages("channel_username", search="сафари"):
    print(f"[{message.date}] {message.text[:100]}")
```

### Pyrogram (Python) — альтернатива

```bash
pip install pyrogram tgcrypto
```

- Асинхронный, быстрый (TgCrypto для шифрования)
- Более Pythonic API
- Документация: https://docs.pyrogram.org

```python
# Pyrogram — получение участников
async for member in app.get_chat_members("group_username"):
    print(f"{member.user.first_name} (ID: {member.user.id})")

# Пересылка поста между каналами
await app.forward_messages(
    chat_id="target_channel",
    from_chat_id="source_channel",
    message_ids=[123, 456]
)
```

### GramJS (TypeScript/JavaScript)

```bash
npm install telegram
```

- Для Node.js и браузера
- MTProto API на TypeScript
- GitHub: https://github.com/nicedoc/gramjs

### TDLib (C++ с обёртками)

- Официальная библиотека от Telegram
- Обёртки: Java, Kotlin, C#, Go, PHP, Rust, Dart и другие
- Самая стабильная, но сложнее в настройке
- GitHub: https://github.com/tdlib/td

### Сравнение для бизнеса

| Критерий | Telethon | Pyrogram | GramJS | TDLib |
|----------|----------|----------|--------|-------|
| Язык | Python | Python | TS/JS | C++ |
| Простота | Высокая | Высокая | Средняя | Низкая |
| Производительность | Хорошая | Отличная | Хорошая | Лучшая |
| Документация | Отличная | Хорошая | Средняя | Хорошая |
| Для туризма ОАЭ | Рекомендуем | Рекомендуем | Для веб | Для серверов |

---

## 13. Модерация и безопасность

### Права администраторов

```python
# Telethon — назначение админа с правами
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

rights = ChatAdminRights(
    post_messages=True,      # Публикация в канале
    edit_messages=True,      # Редактирование постов
    delete_messages=True,    # Удаление сообщений
    ban_users=True,          # Бан пользователей
    invite_users=True,       # Приглашение
    pin_messages=True,       # Закрепление
    manage_call=False,       # Управление звонками
    add_admins=False         # Добавление админов
)

await client(EditAdminRequest(
    channel="group_username",
    user_id="new_admin_username",
    admin_rights=rights,
    rank="Менеджер"  # Кастомный титул
))
```

### Антиспам

**Встроенный Aggressive Anti-Spam (группы 200+ участников):**
- Автоматическое удаление спама от новых участников
- Включается: Настройки группы > Разрешения > Aggressive Anti-Spam

**Через API:**
```python
# Telethon — бан пользователя
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

ban_rights = ChatBannedRights(
    until_date=None,       # Бессрочно (0 = бессрочно)
    view_messages=True     # Полный бан (не может видеть)
)

await client(EditBannedRequest(
    channel="group_username",
    participant="spammer_username",
    banned_rights=ban_rights
))
```

### Безопасность аккаунта

- **2FA обязательно** для аккаунтов с автоматизацией
- **Отдельный аккаунт** для автоматизации (не основной)
- **Не парсить массово** — риск бана аккаунта
- **Соблюдать rate limits** — FloodWait = предупреждение
- **Не продавать/передавать сессии** — нарушение ToS

---

## 14. Примеры для туризма ОАЭ

### Автопостинг в канал экскурсий

```python
from telethon import TelegramClient
from datetime import datetime, timedelta
import json

api_id = 12345678
api_hash = 'your_api_hash'
client = TelegramClient('dubai_tours', api_id, api_hash)

CHANNEL = "dubai_tours_channel"

# Каталог экскурсий
tours = [
    {
        "title": "Desert Safari Premium",
        "price": "280 AED",
        "desc": "VIP джип-сафари, ужин BBQ, шоу, верблюды",
        "photo": "photos/safari.jpg",
        "time": "15:00"
    },
    {
        "title": "Burj Khalifa At The Top",
        "price": "250 AED",
        "desc": "124+125 этаж, вид на весь Дубай",
        "photo": "photos/burj.jpg",
        "time": "10:00"
    }
]

async def post_tour(tour):
    text = (
        f"**{tour['title']}**\n\n"
        f"{tour['desc']}\n\n"
        f"Цена: **{tour['price']}** (дешевле кассы!)\n"
        f"Время: {tour['time']}\n\n"
        f"Бронирование: @your_manager"
    )
    await client.send_file(CHANNEL, tour['photo'], caption=text, parse_mode='md')

async def main():
    await client.start()
    for tour in tours:
        await post_tour(tour)
        # Пауза между постами
        import asyncio
        await asyncio.sleep(3600)  # 1 час между постами

with client:
    client.loop.run_until_complete(main())
```

### Мониторинг упоминаний в туристических группах

```python
# Telethon — мониторинг ключевых слов в реальном времени
from telethon import events

KEYWORDS = ['экскурсия дубай', 'сафари дубай', 'яхта дубай', 'dubai tour', 'desert safari']
MONITOR_GROUPS = ['travel_group_1', 'travel_group_2']

@client.on(events.NewMessage(chats=MONITOR_GROUPS))
async def handler(event):
    text = (event.text or '').lower()
    for keyword in KEYWORDS:
        if keyword in text:
            # Уведомление менеджеру
            await client.send_message(
                'me',
                f"Упоминание: {keyword}\n"
                f"Группа: {event.chat.title}\n"
                f"Сообщение: {event.text[:200]}\n"
                f"Ссылка: https://t.me/{event.chat.username}/{event.id}"
            )
            break
```

### Контент-стратегия канала

**Структура недельного контента:**
| День | Тип поста | Пример |
|------|-----------|--------|
| Пн | Каталог с ценами | Актуальный прайс экскурсий |
| Вт | Story — закулисье | Подготовка к сафари |
| Ср | Отзыв клиента | Скриншот + фото |
| Чт | Акция / спецпредложение | "Только сегодня: -15% на яхт-тур" |
| Пт | Видео с экскурсии | 30-сек ролик (Desert Safari) |
| Сб | Полезный контент | "5 лайфхаков для туристов в Дубае" |
| Вс | Анонс недели | Расписание и свободные слоты |

---

## 15. Rate Limits — MTProto и TDLib

### FloodWait

Telegram не публикует точные лимиты MTProto. При превышении — ошибка `FLOOD_WAIT_X` (ждать X секунд).

### Известные ограничения

| Действие | Примерный лимит | Последствие |
|----------|----------------|-------------|
| Отправка сообщений | ~30/сек (разным чатам) | FloodWait 5–600 сек |
| Добавление в группу | ~20 пользователей за раз | FloodWait, бан |
| Поиск пользователей | ~200/15 мин | FloodWait |
| Создание каналов | 10 в день | Временный бан |
| Изменение username | 1 раз в несколько часов | FloodWait |
| Присоединение к каналам | ~50 в день | FloodWait |

### Обработка FloodWait

```python
# Telethon — автоматическая обработка
from telethon.errors import FloodWaitError
import asyncio

async def safe_send(channel, text):
    try:
        await client.send_message(channel, text)
    except FloodWaitError as e:
        print(f"FloodWait: ждём {e.seconds} секунд")
        await asyncio.sleep(e.seconds)
        await client.send_message(channel, text)
```

```python
# Pyrogram — встроенная обработка (auto_sleep)
# Pyrogram автоматически ждёт при FloodWait, если не отключено
```

### FLOOD_PREMIUM_WAIT

С 2025 года введён `FLOOD_PREMIUM_WAIT_X` — лимит, который снимается при наличии Telegram Premium на аккаунте. Рекомендация: использовать Premium-аккаунт для автоматизации.

### Best Practices

1. **Задержки между действиями:** минимум 1–3 сек между сообщениями
2. **Exponential backoff** при повторных FloodWait
3. **Не массовый парсинг** — Telegram банит за скрапинг
4. **Отдельный аккаунт** для автоматизации (не личный)
5. **Premium-аккаунт** для повышенных лимитов
6. **Постепенный "прогрев"** нового аккаунта — не делать всё сразу

---

**Версия:** 2.0
**Дата:** 12.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль — Dubai Tours)

**Смежные справочники:**
- `telegram-bot-справочник` — Bot API, BotFather, webhooks, платежи, inline-кнопки
- `whatsapp-справочник` — WhatsApp Business API
- `instagram-справочник` — Instagram Graph API

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
