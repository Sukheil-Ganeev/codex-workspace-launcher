# Troubleshooting — Telegram Bot API

## 1. Ошибка 409 Conflict: "terminated by other getUpdates request"

**Причина:** Два процесса одновременно вызывают `getUpdates` с одним токеном. Или webhook установлен, но вы запускаете polling.

**Решение:**
```bash
# Удалить webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook?drop_pending_updates=true"
```
Убедитесь, что запущен только один экземпляр бота.

---

## 2. Ошибка 401 Unauthorized

**Причина:** Неверный токен бота.

**Решение:**
- Проверьте токен: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Если токен отозван: получите новый в @BotFather (`/revoke`)
- Проверьте переменные окружения — нет лишних пробелов/переносов

---

## 3. Бот не получает сообщения в группе

**Причина:** Включен Privacy Mode (по умолчанию). Бот видит только команды `/`, упоминания и ответы на свои сообщения.

**Решение:**
- @BotFather → `/setprivacy` → Disable
- Или сделать бота администратором группы (видит всё без отключения Privacy Mode)

**Важно:** После изменения Privacy Mode удалите бота из группы и добавьте заново.

---

## 4. Webhook не работает — бот молчит

**Диагностика:**
```bash
# Проверить статус webhook
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**Типичные проблемы:**

| Поле в ответе | Проблема | Решение |
|---------------|----------|---------|
| `last_error_message`: "SSL error" | Невалидный SSL | Используйте Let's Encrypt / Cloudflare |
| `last_error_message`: "Connection timed out" | Сервер не отвечает | Проверьте firewall, порт |
| `pending_update_count` растёт | Сервер не возвращает 200 | Всегда отвечайте 200 OK |
| `url` пустой | Webhook не установлен | Вызовите `setWebhook` |

**Важно:** Webhook-сервер должен ответить 200 OK в течение 60 секунд, иначе Telegram повторит запрос.

---

## 5. Ошибка 429 Too Many Requests

**Причина:** Превышен rate limit.

**Решение:**
```python
except TelegramRetryAfter as e:
    await asyncio.sleep(e.retry_after)  # Ждать указанное количество секунд
    # Повторить запрос
```

**Профилактика:**
- Рассылки: не более 20-25 сообщений/сек
- Один чат: не более 1 сообщения/сек
- Группы: не более 20 сообщений/мин
- Используйте `asyncio.sleep(0.05)` между сообщениями

---

## 6. callback_query: "Bad Request: message is not modified"

**Причина:** Вы пытаетесь `editMessageText` с тем же текстом, что уже в сообщении.

**Решение:**
```python
@dp.callback_query()
async def handle(callback: types.CallbackQuery):
    new_text = "Новый текст"
    if callback.message.text != new_text:
        await callback.message.edit_text(new_text)
    await callback.answer()
```

Или просто перехватите исключение:
```python
from aiogram.exceptions import TelegramBadRequest

try:
    await callback.message.edit_text(new_text)
except TelegramBadRequest:
    pass  # Текст уже такой
```

---

## 7. Фото/видео не отправляется — "Bad Request: wrong file identifier"

**Причина:** Невалидный `file_id`, истёкший URL, или файл > лимита.

**Решение:**
- `file_id` валиден только в рамках одного бота (нельзя переиспользовать между ботами)
- URL должен быть публичным HTTPS
- Лимиты: фото до 10 MB, видео/документы до 50 MB
- Для больших файлов: используйте Local Bot API Server

```python
# Правильная отправка файла
with open("photo.jpg", "rb") as f:
    await bot.send_photo(chat_id, photo=BufferedInputFile(f.read(), "photo.jpg"))
```

---

## 8. aiogram: "Update is not handled"

**Причина:** Нет обработчика для данного типа обновления.

**Решение:**
```python
# Добавьте catch-all обработчик для отладки
@dp.message()
async def unhandled_message(message: types.Message):
    print(f"Необработанное: {message.text}")

@dp.callback_query()
async def unhandled_callback(callback: types.CallbackQuery):
    print(f"Необработанный callback: {callback.data}")
    await callback.answer("Кнопка устарела")
```

Проверьте порядок регистрации хэндлеров — aiogram использует первый подходящий.

---

## 9. Webhook получает обновления дважды

**Причина:** Сервер не возвращает 200 OK вовремя, и Telegram повторяет запрос.

**Решение:**
```javascript
// Express: сначала ответить 200, потом обрабатывать
app.post("/webhook", (req, res) => {
    res.sendStatus(200);  // СРАЗУ ответить!
    processUpdate(req.body);  // Обработать асинхронно
});
```

```python
# aiohttp: то же самое
async def webhook(request):
    data = await request.json()
    asyncio.create_task(process_update(data))  # Фоновая обработка
    return web.Response(status=200)
```

---

## 10. FSM: состояние теряется после рестарта бота

**Причина:** Используется `MemoryStorage` (хранит в RAM).

**Решение:**
```python
# Перейти на Redis
from aiogram.fsm.storage.redis import RedisStorage

storage = RedisStorage.from_url("redis://localhost:6379/0")
dp = Dispatcher(storage=storage)
```

Или MongoDB/PostgreSQL для полного контроля.

---

## 11. "Bad Request: can't parse entities"

**Причина:** Ошибка в HTML/Markdown разметке (незакрытый тег, спецсимволы).

**Решение для HTML:**
```python
from html import escape

user_input = "<script>alert('xss')</script>"
safe_text = escape(user_input)  # "&lt;script&gt;..."
await message.answer(f"Вы написали: {safe_text}", parse_mode="HTML")
```

**Решение для MarkdownV2:** Экранируйте все спецсимволы:
```python
import re

def escape_md(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', text)
```

**Рекомендация:** Используйте HTML — проще и надёжнее.

---

## 12. Mini App: "WebAppInitData is invalid"

**Причина:** Неверная валидация `initData` или использование неправильного токена.

**Решение:**
```python
import hashlib, hmac

def validate_init_data(init_data: str, bot_token: str) -> bool:
    params = dict(p.split("=", 1) for p in init_data.split("&"))
    received_hash = params.pop("hash", "")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, received_hash)
```

Убедитесь: используется тот же токен, что и у бота.

---

## 13. Платёж: "Pre-checkout query is not answered"

**Причина:** Бот не ответил на `pre_checkout_query` в течение 10 секунд.

**Решение:**
```python
@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    # ОБЯЗАТЕЛЬНО ответить за 10 секунд!
    await query.answer(ok=True)

# Если нужно отклонить:
# await query.answer(ok=False, error_message="Товар закончился")
```

Убедитесь, что хэндлер зарегистрирован и не блокируется долгой операцией.

---

## 14. Бот не запускается: "Event loop is already running"

**Причина:** Конфликт event loop (Jupyter, IPython, или вложенный asyncio.run).

**Решение:**
```python
# Вместо asyncio.run() в Jupyter:
import nest_asyncio
nest_asyncio.apply()

# Или используйте:
if __name__ == "__main__":
    asyncio.run(main())
```

Для production: один `asyncio.run(main())` в точке входа, без вложенных event loop.

---

## 15. Массовая рассылка: большая часть не доставлена

**Причины и решения:**

| Причина | Решение |
|---------|---------|
| Пользователь заблокировал бота (403) | Удалить из списка рассылки |
| Rate limit (429) | Уменьшить скорость, обработать `retry_after` |
| Невалидный chat_id | Проверить базу, удалить мёртвые ID |
| Бот деактивирован | Проверить статус через `getMe` |

```python
async def safe_broadcast(users, text):
    results = {"ok": 0, "blocked": 0, "error": 0}
    for uid in users:
        try:
            await bot.send_message(uid, text)
            results["ok"] += 1
        except TelegramForbiddenError:
            results["blocked"] += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await bot.send_message(uid, text)
            results["ok"] += 1
        except Exception:
            results["error"] += 1
        await asyncio.sleep(0.05)  # ~20 msg/sec
    return results
```

---

**Версия:** 1.0
**Дата:** 12.02.2026
