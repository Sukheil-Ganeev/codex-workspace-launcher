# FAQ — Telegram Bot API

## 1. Как получить chat_id пользователя?

Способ 1: Пользователь пишет боту → `getUpdates` → в ответе `message.chat.id`.

Способ 2: Через бота @userinfobot — пересылаете сообщение, он показывает ID.

Способ 3: В коде при обработке любого сообщения:
```python
@dp.message()
async def any_message(message: types.Message):
    chat_id = message.chat.id  # Это и есть chat_id
    user_id = message.from_user.id  # ID пользователя
```

В личных чатах `chat_id == user_id`. В группах `chat_id` — отрицательное число.

---

## 2. Webhook или Long Polling — что выбрать?

| Критерий | Long Polling | Webhook |
|----------|-------------|---------|
| Настройка | Просто | Нужен HTTPS-сервер |
| Задержка | До 30 сек | < 1 сек |
| Serverless | Нет | Да (Vercel, Lambda) |
| Разработка | Идеально | Нужен ngrok |
| Production | Допустимо для малой нагрузки | Рекомендуется |

**Правило:** разработка = polling, production = webhook.

---

## 3. Как отправить сообщение с кнопками?

**Inline-кнопки** (под сообщением):
```python
kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кнопка", callback_data="action")]
])
await message.answer("Текст", reply_markup=kb)
```

**Reply-кнопки** (вместо клавиатуры):
```python
kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Кнопка 1"), KeyboardButton(text="Кнопка 2")]
], resize_keyboard=True)
await message.answer("Текст", reply_markup=kb)
```

**Убрать reply-клавиатуру:**
```python
await message.answer("Текст", reply_markup=ReplyKeyboardRemove())
```

---

## 4. Как обработать нажатие inline-кнопки?

```python
@dp.callback_query(F.data == "action")
async def handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Кнопка нажата!")
    await callback.answer()  # ОБЯЗАТЕЛЬНО! Убирает "часики"
```

`callback.answer()` можно вызвать с текстом (alert или toast):
```python
await callback.answer("Готово!", show_alert=False)  # Toast (маленькое уведомление)
await callback.answer("Внимание!", show_alert=True)  # Popup (модальное окно)
```

---

## 5. Как принимать оплату через бота?

**Telegram Stars** (цифровые товары, без провайдера):
```python
await bot.send_invoice(chat_id, title="Товар", description="Описание",
    payload="id_123", currency="XTR", prices=[LabeledPrice(label="Товар", amount=50)])
```

**Stripe/YooKassa** (физические товары):
```python
await bot.send_invoice(chat_id, title="Товар", description="Описание",
    payload="id_123", provider_token="STRIPE_TOKEN",
    currency="USD", prices=[LabeledPrice(label="Товар", amount=7000)])  # $70 в центах
```

Обработка: `@dp.pre_checkout_query()` → `query.answer(ok=True)`, затем `@dp.message(F.successful_payment)`.

---

## 6. Как сделать мультиязычного бота?

```python
TEXTS = {
    "ru": {"welcome": "Привет!", "help": "Помощь"},
    "en": {"welcome": "Hello!", "help": "Help"},
}

def t(user: types.User, key: str) -> str:
    lang = user.language_code or "en"
    lang = lang if lang in TEXTS else "en"
    return TEXTS[lang][key]

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(t(message.from_user, "welcome"))
```

Для полноценной i18n в aiogram есть middleware `aiogram.utils.i18n` с gettext (.po/.mo файлы).

---

## 7. Как ограничить доступ к боту (только для админов)?

```python
ADMINS = [123456789, 987654321]  # ID админов

@dp.message(CommandStart())
async def admin_only(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Доступ запрещён.")
        return
    await message.answer("Панель администратора")
```

В aiogram 3 лучше через middleware или фильтр:
```python
class AdminFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in ADMINS

@dp.message(AdminFilter(), Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer("Админ-панель")
```

---

## 8. Как отправлять массовые рассылки без блокировки?

```python
import asyncio

async def broadcast(user_ids: list, text: str):
    success, failed = 0, 0
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
            success += 1
        except TelegramForbiddenError:
            failed += 1  # Заблокировал бота
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await bot.send_message(user_id, text)
            success += 1
        await asyncio.sleep(0.05)  # 20 сообщений/сек (безопасный лимит)

    return success, failed
```

Лимит: 30 сообщений/сек разным чатам. Безопасно: 20/сек с паузой 0.05 сек.

---

## 9. Как хранить данные пользователей?

**Для простых ботов** — SQLite:
```python
import aiosqlite

async def save_user(user_id, name, language):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (id, name, lang) VALUES (?, ?, ?)",
            (user_id, name, language)
        )
        await db.commit()
```

**Для production** — PostgreSQL (asyncpg) или MongoDB.

**Для состояний FSM** — Redis (RedisStorage в aiogram).

---

## 10. Как создать Mini App (Web App)?

1. Создайте веб-приложение (React, Vue, plain HTML/JS)
2. Задеплойте на HTTPS (Vercel, Netlify, любой хостинг)
3. Подключите к боту:

```python
# Через inline-кнопку
kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Открыть", web_app=WebAppInfo(url="https://your-app.com"))]
])
```

Или через BotFather: `/setmenubutton` → URL приложения.

В Mini App подключите `telegram-web-app.js` и используйте `Telegram.WebApp.sendData()` для передачи данных боту.

---

## 11. Как бот может работать в группах?

1. Добавьте бота в группу
2. Настройте Privacy Mode через @BotFather (`/setprivacy`):
   - **Enabled** (по умолчанию) — бот видит только команды `/`, упоминания `@bot`, и ответы на его сообщения
   - **Disabled** — бот видит все сообщения

3. Для работы как админ: дайте боту права администратора в группе

```python
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message(message: types.Message):
    # Обработка сообщений в группе
    pass
```

---

## 12. Какой максимальный размер файлов?

| Операция | Лимит |
|----------|-------|
| Скачивание (getFile) | 20 MB |
| Отправка (sendDocument) | 50 MB |
| Фото (sendPhoto) | 10 MB |
| Через Local Bot API Server | 2000 MB (2 GB) |

Для файлов > 50 MB используйте Telegram Bot API Server (self-hosted).

---

## 13. Как тестировать бота локально с webhook?

Используйте ngrok:
```bash
ngrok http 3000
# Получаете: https://abc123.ngrok-free.app

# Устанавливаете webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://abc123.ngrok-free.app/webhook"
```

Альтернативы: Cloudflare Tunnel (бесплатный), localtunnel.

---

## 14. Можно ли использовать один токен для нескольких серверов?

Нет. Один токен = один получатель обновлений (один polling процесс ИЛИ один webhook URL). Если запустить два процесса с одним токеном — ошибка 409 Conflict.

Решение для масштабирования: webhook + load balancer (все запросы приходят на один URL, LB распределяет).

---

## 15. Как обновить бота без downtime?

**Для webhook:**
1. Задеплойте новую версию
2. Telegram автоматически отправит обновления на тот же URL
3. Пропущенные обновления (если сервер был недоступен < 24 часов) придут повторно

**Для polling:**
1. Остановите старый процесс
2. Запустите новый
3. Обновления за время простоя придут через `getUpdates` (хранятся 24 часа)

**Blue-green деплой:** два сервера за LB, переключаете трафик.

---

**Версия:** 1.0
**Дата:** 12.02.2026
