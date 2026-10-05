# Engineering Advisor v4.0 — Aiogram-специфичный чеклист

> 10 авто-проверяемых правил для Telegram-ботов на aiogram 3.x
> Источник: EXP-035, EXP-053, EXP-SPY-001 + веб-исследование aiogram 3.25 docs

---

## Быстрая проверка (копируй и запускай)

```bash
# Проверка всех 10 правил одной командой:
echo "=== Aiogram Checklist ==="
echo "1. Блокирующие вызовы:" && grep -rn "time\.sleep\|requests\.get\|requests\.post" --include="*.py" || echo "   OK"
echo "2. Deprecated bot['key']:" && grep -rn "bot\[" --include="*.py" | grep -v "# " || echo "   OK"
echo "3. Старый синтаксис v2:" && grep -rn "message_handler\|callback_query_handler" --include="*.py" || echo "   OK"
echo "4. Большие файлы:" && wc -l *.py **/*.py 2>/dev/null | sort -rn | head -5
echo "========================"
```

---

## 10 правил

| # | Правило | Grep-паттерн | Авто | Severity |
|---|---------|-------------|------|----------|
| 1 | Command() хэндлеры до F.text catch-all | Порядок декораторов в файле | Да | 🔴 BLOCK |
| 2 | Нет time.sleep в async | `time.sleep` в .py | Да | 🔴 BLOCK |
| 3 | Нет requests.get/post в async | `requests.get\|requests.post` в async def | Да | 🔴 BLOCK |
| 4 | callback.answer() в каждом CallbackQuery handler | CallbackQuery без .answer() | Да | 🟡 WARN |
| 5 | html.escape() на пользовательский ввод | f-строки с {message.text} без escape | Частично | 🟡 WARN |
| 6 | Нет Bot["key"] (aiogram 3.25+) | `bot[` в .py | Да | 🟡 WARN |
| 7 | Нет @dp.message_handler (v2 синтаксис) | `message_handler\|callback_query_handler` | Да | 🟡 WARN |
| 8 | await на всех async-вызовах | async def без парного await | Частично | 🟡 WARN |
| 9 | dp.include_router() порядок задокументирован | Комментарии у include_router | Нет | 🟢 INFO |
| 10 | Монолитный файл >1500 строк → разделение | wc -l на .py файлах | Да | 🟢 INFO |

---

## Подробности по каждому правилу

### Правило 1: Command() хэндлеры до F.text catch-all

**Проблема:** В aiogram 3 хэндлеры обрабатываются в порядке регистрации. Если `F.text` catch-all зарегистрирован ДО `Command("calc")` -- команда /calc молча не работает.

**Пример плохого кода:**
```python
# ❌ НЕПРАВИЛЬНО — catch-all перехватывает ВСЁ
router.message(F.text)(handle_text)           # catch-all ПЕРВЫЙ
router.message(Command("calc"))(handle_calc)  # команда НИКОГДА не сработает
```

**Пример правильного кода:**
```python
# ✅ ПРАВИЛЬНО — специфичные до общих
router.message(Command("calc"))(handle_calc)  # команда ПЕРВАЯ
router.message(Command("help"))(handle_help)  # другие команды
router.message(F.text)(handle_text)           # catch-all ПОСЛЕДНИЙ
```

**Проверка:**
```bash
grep -n "F\.text\|Command(" handlers/*.py | sort -t: -k2 -n
# Все Command() должны быть с МЕНЬШИМИ номерами строк чем F.text
```

**Источник:** EXP-053 -- /calc, /rate, /route молча не работали.

---

### Правило 2: Нет time.sleep в async

**Проблема:** `time.sleep(N)` блокирует весь event loop. Бот замирает для ВСЕХ пользователей на N секунд.

**Замена:** `await asyncio.sleep(N)`

**Проверка:**
```bash
grep -rn "time\.sleep" --include="*.py"
# Должно быть 0 результатов в async-коде
```

---

### Правило 3: Нет requests.get/post в async

**Проблема:** `requests` — синхронная библиотека. Один запрос на 3 секунды = бот мёртв 3 секунды для всех.

**Замена:** `aiohttp.ClientSession` с `async with`

**Пример:**
```python
# ❌ НЕПРАВИЛЬНО
import requests
response = requests.get("https://api.example.com/data")

# ✅ ПРАВИЛЬНО
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com/data") as response:
        data = await response.json()
```

**Проверка:**
```bash
grep -rn "requests\.get\|requests\.post" --include="*.py"
```

**Источник:** EXP-035 -- 92 пропущенных await при миграции sync→async.

---

### Правило 4: callback.answer() в каждом CallbackQuery handler

**Проблема:** Без `callback.answer()` Telegram показывает спиннер на кнопке до 30 секунд. Пользователь думает бот завис.

**Пример:**
```python
# ❌ НЕПРАВИЛЬНО — спиннер висит
@router.callback_query(F.data == "confirm")
async def handle_confirm(callback: CallbackQuery):
    await callback.message.answer("Подтверждено!")
    # забыли callback.answer()!

# ✅ ПРАВИЛЬНО
@router.callback_query(F.data == "confirm")
async def handle_confirm(callback: CallbackQuery):
    await callback.message.answer("Подтверждено!")
    await callback.answer()  # спиннер убран
```

**Проверка:**
```bash
# Найти все CallbackQuery handlers
grep -n "CallbackQuery" handlers/*.py
# Для каждого проверить наличие .answer()
```

---

### Правило 5: html.escape() на пользовательский ввод

**Проблема:** Если пользователь отправит `<b>test</b>` или `<script>`, это может сломать HTML-разметку бота или использоваться для XSS-подобных атак в Telegram.

**Замена:** `html.escape(message.text)` перед вставкой в HTML-сообщение.

**Пример:**
```python
import html

# ❌ НЕПРАВИЛЬНО
await message.answer(f"Вы написали: {message.text}", parse_mode="HTML")

# ✅ ПРАВИЛЬНО
safe_text = html.escape(message.text)
await message.answer(f"Вы написали: {safe_text}", parse_mode="HTML")
```

---

### Правило 6: Нет Bot["key"] (aiogram 3.25+)

**Проблема:** В aiogram 3.25 `bot["key"]` deprecated. Бот — не словарь.

**Замена:** Dependency Injection через middleware или `dp["key"]`.

**Пример:**
```python
# ❌ НЕПРАВИЛЬНО (deprecated в 3.25)
db = bot["db"]

# ✅ ПРАВИЛЬНО — через DI
@router.message(Command("start"))
async def handle_start(message: Message, db: Database):
    # db приходит через middleware/DI
    ...
```

**Источник:** EXP-SPY-001

---

### Правило 7: Нет @dp.message_handler (v2 синтаксис)

**Проблема:** Синтаксис aiogram v2 (`@dp.message_handler`, `@dp.callback_query_handler`) не работает в v3.

**Замена:**
| aiogram 2 | aiogram 3 |
|-----------|-----------|
| `@dp.message_handler()` | `@router.message()` |
| `@dp.callback_query_handler()` | `@router.callback_query()` |
| `commands=["start"]` | `Command("start")` |
| `content_types=["photo"]` | `F.photo` |

---

### Правило 8: await на всех async-вызовах

**Проблема:** Вызов async-функции без `await` возвращает coroutine object вместо результата. Код выполняется, но результат теряется.

**Проверка:**
```bash
# Найти async функции
grep -rn "async def " --include="*.py" | wc -l
# Найти await вызовы
grep -rn "await " --include="*.py" | wc -l
# Если async def >> await -- есть пропущенные await
```

**Источник:** EXP-035 -- 92 пропущенных await.

---

### Правило 9: dp.include_router() порядок задокументирован

**Проблема:** Порядок `dp.include_router()` определяет приоритет обработки. Без документации -- неясно почему одни хэндлеры работают, а другие нет.

**Рекомендация:**
```python
# Порядок важен! Первый router имеет приоритет.
dp.include_router(admin_router)      # 1. Админ-команды
dp.include_router(payment_router)    # 2. Оплата
dp.include_router(booking_router)    # 3. Бронирования
dp.include_router(general_router)    # 4. Общие (catch-all последний!)
```

---

### Правило 10: Монолитный файл >1500 строк

**Проблема:** God Object — файл с 10+ функциями разной ответственности. Трудно поддерживать, легко сломать.

**Рекомендация:** Разделить на модули:
```
handlers/
├── __init__.py      # re-exports
├── admin.py         # админ-команды
├── booking.py       # бронирования
├── payment.py       # оплата
├── callback.py      # callback handlers
└── general.py       # catch-all (последний!)
```

**Проверка:**
```bash
wc -l *.py **/*.py 2>/dev/null | sort -rn | head -10
# Файлы >1500 строк — кандидаты на разделение
```

**Источник:** EXP-035 -- handlers.py 2000+ строк → 8 модулей.

---

## Когда запускать

| Событие | Правила для проверки |
|---------|---------------------|
| Создание нового хэндлера | #1, #4, #8 |
| Добавление API-запроса | #2, #3, #8 |
| Отправка текста пользователю | #5 |
| Миграция aiogram 2 → 3 | #6, #7, #8 (все!) |
| Рефакторинг handlers | #1, #9, #10 |
| Перед деплоем | Все 10 правил |
