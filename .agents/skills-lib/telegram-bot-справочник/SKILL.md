---
name: telegram-bot-справочник
description: "Production-ready руководство по Telegram Bot API для создания и деплоя ботов. Охватывает Bot API 7.x-9.x, aiogram, grammY, платежи Stars. Используй когда нужно создать Telegram бота, настроить webhook, обработку сообщений, FSM, платежи."
---
# Telegram Bot API — Production Guide

## 1. Quick Start: бот за 10 минут

### Шаг 1: Получить токен через @BotFather

```
В Telegram: @BotFather → /newbot → имя "Dubai Tours Bot" → username "dubai_tours_bot"
Токен: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Формат токена: `<bot_id>:<secret_key>`. Хранить ТОЛЬКО в переменных окружения.

### Шаг 2: Первый бот на Python (aiogram 3)

```python
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
import asyncio

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в Dubai Tours Bot!",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Экскурсии", callback_data="tours")],
            [types.InlineKeyboardButton(text="Яхты", callback_data="yachts")],
            [types.InlineKeyboardButton(text="Трансферы", callback_data="transfers")]
        ])
    )

@dp.callback_query(F.data == "tours")
async def tours(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите экскурсию:")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
```

### Шаг 2b: Первый бот на Node.js (grammY)

```javascript
const { Bot, InlineKeyboard } = require("grammy");

const bot = new Bot(process.env.BOT_TOKEN);

bot.command("start", async (ctx) => {
  const keyboard = new InlineKeyboard()
    .text("Экскурсии", "tours").row()
    .text("Яхты", "yachts").row()
    .text("Трансферы", "transfers");

  await ctx.reply("Добро пожаловать в Dubai Tours Bot!", {
    reply_markup: keyboard,
  });
});

bot.callbackQuery("tours", async (ctx) => {
  await ctx.editMessageText("Выберите экскурсию:");
  await ctx.answerCallbackQuery();
});

bot.start();
```

---

## 2. Архитектура: Webhook vs Long Polling

### Long Polling (getUpdates)

Бот опрашивает сервер Telegram: "Есть обновления?"

```
Бот → Telegram: getUpdates (timeout=30)
Telegram → Бот: [update1, update2, ...]
```

**Когда использовать:** разработка, тестирование, простые боты, нет сервера.

### Webhook (setWebhook)

Telegram отправляет POST-запрос на ваш сервер при каждом обновлении.

```
Пользователь → Telegram → HTTPS POST → Ваш сервер
```

**Требования:** публичный HTTPS, SSL (порты 443/80/88/8443).

**Когда использовать:** production, высокая нагрузка, serverless.

### Настройка webhook

```bash
# Установить
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://yourdomain.com/webhook" \
  -d "secret_token=MY_SECRET_123" \
  -d "max_connections=40"

# Проверить
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Удалить (переключиться на polling)
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

Параметр `secret_token` — Telegram отправляет его в заголовке `X-Telegram-Bot-Api-Secret-Token`. Проверяйте на сервере для защиты от подделки.

### Webhook на Express (Node.js)

```javascript
const express = require("express");
const { Bot, webhookCallback } = require("grammy");

const bot = new Bot(process.env.BOT_TOKEN);
const app = express();

// grammY обрабатывает webhook автоматически
app.use(express.json());
app.post("/webhook", webhookCallback(bot, "express"));

app.listen(3000);
```

### Webhook на aiohttp (Python, aiogram 3)

```python
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

WEBHOOK_URL = "https://yourdomain.com/webhook"

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL, secret_token="MY_SECRET_123")

app = web.Application()
app.on_startup.append(on_startup)
SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token="MY_SECRET_123").register(app, path="/webhook")
web.run_app(app, host="0.0.0.0", port=3000)
```

---

## 3. Обработка сообщений

### Объект Update

Каждое обновление от Telegram — JSON с одним из полей:

| Поле | Описание |
|------|----------|
| `message` | Новое сообщение (текст, фото, видео...) |
| `callback_query` | Нажатие inline-кнопки |
| `inline_query` | Inline-запрос (@bot запрос) |
| `pre_checkout_query` | Подтверждение оплаты |
| `my_chat_member` | Бот добавлен/удалён из чата |

### Отправка сообщений

```python
# Текст с HTML-форматированием
await bot.send_message(chat_id, "<b>Жирный</b>, <i>курсив</i>, <code>код</code>",
                       parse_mode="HTML")

# Фото
await bot.send_photo(chat_id, photo="https://example.com/tour.jpg",
                     caption="Desert Safari — $70")

# Документ (ваучер)
await bot.send_document(chat_id, document=open("voucher.pdf", "rb"),
                        caption="Ваш ваучер")

# Локация (офис в Дубае)
await bot.send_location(chat_id, latitude=25.0997, longitude=55.1724)

# Группа медиа
from aiogram.types import InputMediaPhoto
media = [
    InputMediaPhoto(media="photo1_file_id", caption="Тур 1"),
    InputMediaPhoto(media="photo2_file_id"),
]
await bot.send_media_group(chat_id, media=media)
```

### Форматирование

**HTML** (рекомендуется):
```html
<b>жирный</b>  <i>курсив</i>  <u>подчёркнутый</u>
<s>зачёркнутый</s>  <code>моноширинный</code>
<pre language="python">блок кода</pre>
<a href="https://example.com">ссылка</a>
<tg-spoiler>спойлер</tg-spoiler>
<blockquote>цитата</blockquote>
```

**MarkdownV2** — нужно экранировать спецсимволы (`_*[]()~>#+-=|{}.!`). HTML проще.

---

## 4. Клавиатуры и кнопки

### InlineKeyboardMarkup — кнопки под сообщением

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Типы кнопок
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # callback_data — данные для обработки (до 64 байт)
    [InlineKeyboardButton(text="Забронировать", callback_data="book_safari_70")],
    # url — открывает ссылку
    [InlineKeyboardButton(text="Наш сайт", url="https://example.com")],
    # web_app — открывает Mini App
    [InlineKeyboardButton(text="Каталог", web_app=WebAppInfo(url="https://app.example.com"))],
    # pay — кнопка оплаты (только первая кнопка в первом ряду)
    [InlineKeyboardButton(text="Оплатить $70", pay=True)],
])
```

### ReplyKeyboardMarkup — кнопки вместо клавиатуры

```python
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Экскурсии"), KeyboardButton(text="Яхты")],
        [KeyboardButton(text="Трансферы"), KeyboardButton(text="Контакты")],
        # Специальные кнопки
        [KeyboardButton(text="Отправить номер", request_contact=True)],
        [KeyboardButton(text="Отправить геолокацию", request_location=True)],
    ],
    resize_keyboard=True,  # Уменьшить размер
    one_time_keyboard=True  # Скрыть после нажатия
)
```

### Обработка callback_query

```python
@dp.callback_query(F.data.startswith("book_"))
async def handle_booking(callback: types.CallbackQuery):
    _, tour, price = callback.data.split("_")  # "book_safari_70"
    await callback.message.edit_text(
        f"Бронирование: {tour}, ${price}\nПодтвердите:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{tour}_{price}")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ])
    )
    await callback.answer()  # Убрать "часики"
```

---

## 5. Inline Mode

Inline-режим: пользователь вводит `@yourbot запрос` в любом чате, бот показывает результаты.

### Включение

В @BotFather: `/setinline` → задать placeholder.

### Обработка

```python
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

@dp.inline_query()
async def inline_handler(query: types.InlineQuery):
    tours = search_tours(query.query)  # Поиск по каталогу

    results = []
    for i, tour in enumerate(tours[:50]):  # Макс. 50 результатов
        results.append(InlineQueryResultArticle(
            id=str(i),
            title=tour["name"],
            description=f"${tour['price']} — {tour['description'][:100]}",
            thumbnail_url=tour.get("photo_url"),
            input_message_content=InputTextMessageContent(
                message_text=f"<b>{tour['name']}</b>\nЦена: ${tour['price']}\n{tour['description']}",
                parse_mode="HTML"
            )
        ))

    await query.answer(results, cache_time=300)
```

---

## 6. Состояния диалога (FSM)

FSM (Finite State Machine) управляет многошаговыми диалогами: бронирование, анкеты, формы.

### aiogram 3 — встроенный FSM

```python
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class BookingForm(StatesGroup):
    choose_tour = State()
    choose_date = State()
    choose_people = State()
    confirm = State()

@dp.message(CommandStart())
async def start_booking(message: types.Message, state: FSMContext):
    await state.set_state(BookingForm.choose_tour)
    await message.answer("Выберите тур:", reply_markup=tour_keyboard)

@dp.callback_query(BookingForm.choose_tour)
async def tour_chosen(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(tour=callback.data)
    await state.set_state(BookingForm.choose_date)
    await callback.message.edit_text("Введите дату (ДД.ММ.ГГГГ):")
    await callback.answer()

@dp.message(BookingForm.choose_date)
async def date_chosen(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(BookingForm.choose_people)
    await message.answer("Сколько человек? (1-10)")

@dp.message(BookingForm.choose_people)
async def people_chosen(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(people=int(message.text))
    await state.set_state(BookingForm.confirm)
    await message.answer(
        f"Тур: {data['tour']}\nДата: {data['date']}\nЧеловек: {message.text}\n\nПодтвердить?",
        reply_markup=confirm_keyboard
    )
```

### Хранение состояний

| Хранилище | Плюсы | Минусы |
|-----------|-------|--------|
| MemoryStorage | Просто, без зависимостей | Теряется при рестарте |
| RedisStorage | Быстро, персистентно | Нужен Redis |
| База данных | Полный контроль | Медленнее Redis |

```python
# Redis
from aiogram.fsm.storage.redis import RedisStorage
storage = RedisStorage.from_url("redis://localhost:6379/0")
dp = Dispatcher(storage=storage)
```

---

## 7. Команды бота

### Регистрация команд

```python
from aiogram.types import BotCommand, BotCommandScopeDefault

commands = [
    BotCommand(command="start", description="Запуск бота"),
    BotCommand(command="tours", description="Каталог экскурсий"),
    BotCommand(command="booking", description="Мои бронирования"),
    BotCommand(command="help", description="Помощь"),
    BotCommand(command="language", description="Сменить язык"),
]
await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
```

### BotCommandScope — разные команды для разных контекстов

```python
from aiogram.types import BotCommandScopeChat

# Команды только для админа
admin_commands = [
    BotCommand(command="stats", description="Статистика"),
    BotCommand(command="broadcast", description="Рассылка"),
]
await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
```

---

## 8. Платежи

### Telegram Stars (цифровые товары)

Stars — встроенная валюта Telegram (тег `XTR`). Для цифровых товаров и услуг. Провайдер не нужен (`provider_token` пустой).

```python
# Отправка счёта в Stars
await bot.send_invoice(
    chat_id=chat_id,
    title="VIP-гид по Дубаю (PDF)",
    description="Электронный путеводитель: 50 мест, карты, скидки",
    payload="guide_dubai_vip",
    currency="XTR",          # Telegram Stars
    prices=[LabeledPrice(label="VIP-гид", amount=100)],  # 100 Stars
    # provider_token НЕ указываем для Stars
)
```

**Вывод Stars:** минимум 1000 Stars, доступно через 21 день. Конвертация в TON. 1000 Stars ~ $13 USD.

### Платежи через провайдера (Stripe, YooKassa)

```python
await bot.send_invoice(
    chat_id=chat_id,
    title="Desert Safari Tour",
    description="2 часа в пустыне, ужин, шоу",
    payload="order_12345",
    provider_token="STRIPE_TOKEN",
    currency="USD",
    prices=[
        LabeledPrice(label="Desert Safari", amount=7000),  # $70.00 (в центах!)
        LabeledPrice(label="Трансфер", amount=1500),        # $15.00
    ],
    need_name=True,
    need_phone_number=True,
)
```

### Обработка оплаты

```python
@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    # Проверяем: есть ли места, корректна ли цена
    await query.answer(ok=True)  # или ok=False, error_message="Места закончились"

@dp.message(F.successful_payment)
async def payment_success(message: types.Message):
    payment = message.successful_payment
    # payment.total_amount, payment.currency, payment.invoice_payload
    await message.answer(f"Оплата получена: {payment.total_amount // 100} {payment.currency}")
    # Создать бронирование в БД, отправить ваучер
```

---

## 9. Mini Apps (Web Apps)

Mini Apps — полноценные веб-приложения внутри Telegram. HTML/CSS/JS, любой фреймворк.

### Запуск Mini App

```python
from aiogram.types import WebAppInfo

# Кнопка в inline-клавиатуре
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="Открыть каталог",
        web_app=WebAppInfo(url="https://tours.example.com")
    )]
])

# Кнопка в меню бота (через BotFather)
# /setmenubutton → URL вашего Mini App
```

### Обмен данными бот <-> Mini App

**В Mini App (JavaScript):**
```javascript
const tg = window.Telegram.WebApp;

// Данные пользователя
const user = tg.initDataUnsafe.user;

// Отправить данные боту
tg.sendData(JSON.stringify({
  action: "book",
  tour_id: "safari_01",
  date: "2026-02-15",
  people: 2
}));

// Закрыть Mini App
tg.close();
```

**В боте (Python):**
```python
@dp.message(F.web_app_data)
async def handle_webapp(message: types.Message):
    data = json.loads(message.web_app_data.data)
    # data = {"action": "book", "tour_id": "safari_01", ...}
    await message.answer(f"Бронирование: {data['tour_id']}, дата {data['date']}")
```

### Возможности Mini Apps (2025-2026)

- **Полноэкранный режим** (Bot API 8.0+)
- **Ярлык на домашний экран** — запуск как нативное приложение
- **DeviceStorage / SecureStorage** — локальное хранение данных
- **Геолокация** — запрос координат пользователя
- **shareMessage** — шаринг медиа из Mini App в чаты
- **Подписки** — встроенные планы подписок

---

## 10. Rate Limits и ошибки

### Лимиты отправки

| Операция | Лимит |
|----------|-------|
| Разным чатам | 30 сообщений/сек |
| Одному чату | 1 сообщение/сек (20/мин в группах) |
| Массовая рассылка | ~30 чатов/сек |
| Webhook соединения | 1-100 одновременных (по умолчанию 40) |
| getUpdates хранение | 24 часа |
| Inline-результаты | до 50 за ответ |

### Адаптивные лимиты (2026)

С января 2026 — система "репутации бота". Хорошая репутация = повышенные лимиты. Факторы: доставляемость, блокировки, активность, жалобы.

### Коды ошибок

| Код | Описание | Действие |
|-----|----------|----------|
| 400 | Неверные параметры | Исправить запрос |
| 401 | Неверный токен | Проверить токен |
| 403 | Бот заблокирован | Удалить из рассылки |
| 409 | Конфликт (polling+webhook) | Удалить webhook или остановить polling |
| 429 | Rate limit | Подождать `retry_after` секунд |

### Обработка 429 с exponential backoff

```python
import asyncio

async def send_with_retry(chat_id, text, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id, text)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramForbiddenError:
            return None  # Бот заблокирован
    return None
```

---

## 11. Новинки Bot API 8.0-9.x (2025-2026)

### Bot API 8.0 (2025)

- Mini Apps: полноэкранный режим, запуск с домашнего экрана
- Подписки через Mini Apps

### Bot API 9.0-9.2 (август 2025)

- **Channel Direct Messages** — боты отправляют и читают ЛС каналов
- **Suggested Posts** — управление предложенными постами (approve/decline)
- **Business Accounts** — боты управляют названием, username, bio, фото бизнеса
- **Paid Gifts** — конвертация, трансфер, апгрейд подарков
- **Stars balance** — проверка баланса Stars и трансфер из бизнеса
- **Чтение/удаление** бизнес-сообщений

### Bot API 9.1 (июль 2025)

- **Checklists** — нативные чек-листы, бизнес-боты создают и редактируют
- Расширение polls — до 12 вариантов

### Другие обновления 2025

- Реакции на сервисные сообщения
- Транзакции с чатами
- Подарок Telegram Premium за Stars
- `sendMessageDraft` — потоковая отправка (генерация в реальном времени)

---

## 12. Примеры для туризма ОАЭ

### Каталог экскурсий с inline-навигацией

```python
TOURS = {
    "city": [
        {"id": "burj", "name": "Burj Khalifa At The Top", "price": 80, "emoji": "🏙"},
        {"id": "oldtown", "name": "Old Dubai Walking Tour", "price": 45, "emoji": "🕌"},
        {"id": "abudhabi", "name": "Abu Dhabi Full Day", "price": 95, "emoji": "🏛"},
    ],
    "desert": [
        {"id": "safari", "name": "Desert Safari + BBQ", "price": 70, "emoji": "🏜"},
    ],
    "yacht": [
        {"id": "yacht2h", "name": "Yacht Cruise 2h", "price": 150, "emoji": "⛵"},
    ],
}

@dp.callback_query(F.data == "menu_tours")
async def show_categories(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏙 Городские", callback_data="cat_city")],
        [InlineKeyboardButton(text="🏜 Пустыня", callback_data="cat_desert")],
        [InlineKeyboardButton(text="⛵ Яхты", callback_data="cat_yacht")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")],
    ])
    await callback.message.edit_text("Выберите категорию:", reply_markup=kb)
    await callback.answer()
```

### Мультиязычность (RU/EN/AR)

```python
TEXTS = {
    "ru": {"welcome": "Добро пожаловать!", "choose": "Выберите:"},
    "en": {"welcome": "Welcome!", "choose": "Choose:"},
    "ar": {"welcome": "!مرحبا", "choose": ":اختر"},
}

def get_lang(user: types.User) -> str:
    code = user.language_code or "en"
    return code if code in TEXTS else "en"

@dp.message(CommandStart())
async def start(message: types.Message):
    lang = get_lang(message.from_user)
    await message.answer(TEXTS[lang]["welcome"])
```

### Уведомления о бронированиях

```python
async def send_booking_notification(chat_id, booking):
    text = (
        f"<b>Бронирование #{booking['id']}</b>\n\n"
        f"Тур: {booking['tour']}\n"
        f"Дата: {booking['date']}\n"
        f"Гостей: {booking['people']}\n"
        f"Сумма: ${booking['total']}\n\n"
        f"Трансфер: {booking.get('pickup', 'уточняется')}"
    )
    await bot.send_message(chat_id, text, parse_mode="HTML")

    # Напоминание за 24 часа (scheduler)
    # Информация о водителе за 2 часа
    # Запрос отзыва через сутки после тура
```

---

## 13. Деплой

### Railway (рекомендуется для начала)

```bash
# 1. Procfile
echo "worker: python bot.py" > Procfile

# 2. requirements.txt
echo "aiogram>=3.4" > requirements.txt

# 3. Деплой
railway login && railway init && railway up

# 4. Переменные окружения
railway variables set BOT_TOKEN=123456:ABC
```

### Vercel (serverless, webhook)

```javascript
// api/webhook.js
const { Bot, webhookCallback } = require("grammy");
const bot = new Bot(process.env.BOT_TOKEN);

// ... настройка хэндлеров ...

module.exports = webhookCallback(bot, "https");
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

```bash
docker build -t tour-bot . && docker run -d -e BOT_TOKEN=xxx tour-bot
```

### VPS (systemd)

```ini
# /etc/systemd/system/tourbot.service
[Unit]
Description=Dubai Tours Telegram Bot
After=network.target

[Service]
User=botuser
WorkingDirectory=/opt/tourbot
ExecStart=/opt/tourbot/venv/bin/python bot.py
Restart=always
EnvironmentFile=/opt/tourbot/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tourbot && sudo systemctl start tourbot
```

---

## 14. Библиотеки

### Python

| Библиотека | Стиль | Версия Bot API | Особенности |
|------------|-------|----------------|-------------|
| **aiogram 3** | Async (asyncio) | Актуальная | FSM, middleware, роутеры, i18n |
| python-telegram-bot | Async/sync | Актуальная | Большое сообщество, Job Queue |
| telebot (pyTelegramBotAPI) | Sync/async | Хорошая | Простой, быстрый старт |

**Рекомендация:** aiogram 3 для production — полная асинхронность, встроенный FSM, лучшая архитектура.

### Node.js / TypeScript

| Библиотека | Стиль | Версия Bot API | Особенности |
|------------|-------|----------------|-------------|
| **grammY** | TS-first | Всегда актуальная | Плагины, отличные типы, документация |
| Telegraf | JS/TS | Отстаёт | Популярный, middleware |
| node-telegram-bot-api | JS | Отстаёт | Простой, без лишнего |

**Рекомендация:** grammY — лучшие типы, всегда актуальный Bot API, хорошая документация.

---

## 15. Безопасность

### Хранение токена

```bash
# .env файл (добавить в .gitignore!)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
PAYMENT_TOKEN=stripe_live_xxx

# Python
import os
TOKEN = os.getenv("BOT_TOKEN")

# Node.js
const TOKEN = process.env.BOT_TOKEN;
```

### Валидация webhook (secret_token)

```python
# При setWebhook задали secret_token="MY_SECRET_123"
# Telegram отправляет заголовок X-Telegram-Bot-Api-Secret-Token

@app.post("/webhook")
async def webhook(request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != "MY_SECRET_123":
        return web.Response(status=403)
    # ...
```

### Валидация initData (Mini Apps)

```python
import hashlib, hmac

def validate_init_data(init_data: str, bot_token: str) -> bool:
    params = dict(p.split("=", 1) for p in init_data.split("&"))
    received_hash = params.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return computed == received_hash
```

### Ротация токена

Если токен скомпрометирован: @BotFather → `/revoke` → получить новый токен → обновить на сервере.

---

## Форматирование текстов бота (UI/UX стандарт)

**Эталонный гайд:** `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md`
**Универсальный промт:** `D:/Downloads/ПРОМТ_ФОРМАТИРОВАНИЕ_ТЕКСТОВ_БОТА.md`

При создании/редактировании ЛЮБЫХ текстов бота — ОБЯЗАТЕЛЬНО:

| Правило | Пример |
|---------|--------|
| Каждое сообщение начинается с эмодзи | `🛒 Корзина пуста` |
| Заголовки: эмодзи + `<b>bold</b>` + разделитель | `📊 <b>Статистика</b>\n──────────────────` |
| Списки с маркером ▫️ | `▫️ 🎫 Билеты — описание` |
| Разделители 18 символов | `──────────────────` (тонкий) / `━━━━━━━━━━━━━━━━━━` (жирный) |
| Числа/даты/суммы в `<code>` | `<code>1,500 AED</code>` |
| Кнопки ВСЕГДА с эмодзи | `✅ Подтвердить`, `❌ Отмена` |
| Пользовательский ввод экранировать | `_esc()` или `html.escape()` |

---

## Полезные ссылки

- **Bot API:** https://core.telegram.org/bots/api
- **Payments (Stars):** https://core.telegram.org/bots/payments-stars
- **Payments (провайдеры):** https://core.telegram.org/bots/payments
- **Mini Apps:** https://core.telegram.org/bots/webapps
- **Changelog:** https://core.telegram.org/bots/api-changelog
- **aiogram docs:** https://docs.aiogram.dev/
- **grammY docs:** https://grammy.dev/
- **BotFather:** https://t.me/BotFather

---

**Версия:** 1.0
**Дата:** 12.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль — Dubai Tours)

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
