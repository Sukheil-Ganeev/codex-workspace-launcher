# Ответ: почему /start и /help не работают

## Engineering Advisor активирован

Загружено 15+ уроков из опыта. Применяю EXP-053 (критический урок).

---

## Диагноз: Триггер #19 — Порядок хэндлеров (Recommended)

```
=== Engineering Advisor ===
WARN (1): router.py:строка 7 — F.text catch-all объявлен ВЫШЕ Command() хэндлеров.
          Перехватывает /start и /help до того, как до них доходит очередь.
          EXP-053 применён.
===========================
```

---

## Что происходит

В aiogram 3.x хэндлеры проверяются строго в порядке регистрации — сверху вниз.

Твой `router.py` сейчас:

```python
@router.message(F.text)          # ← ПЕРВЫЙ. Ловит ВСЁ включая /start, /help
async def handle_text(message):
    await message.answer(...)
    return                        # ← return = "обработано", дальше не идёт

@router.message(Command("start"))  # ← Никогда не достигается
@router.message(Command("help"))   # ← Никогда не достигается
```

Когда пользователь пишет `/start`:
1. aiogram проверяет первый хэндлер: `F.text` — `/start` это текст? ДА.
2. `handle_text` срабатывает, выдаёт "Вы написали: /start", делает `return`.
3. Поиск завершён. `cmd_start` никогда не вызывается.

Аналогия из EXP-053: «Турникеты в метро: "пропускай всех" перед "проверяй билет" — контроль бесполезен».

---

## Исправление

Поменяй порядок: конкретные фильтры сверху, общие снизу. Как воронка.

```python
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

# СНАЧАЛА — конкретные команды
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Справка по командам...")

# ПОТОМ — общий catch-all
@router.message(F.text)
async def handle_text(message: Message):
    await message.answer(f"Вы написали: {message.text}")
```

Теперь `/start` проверяется первым против `Command("start")` — совпадает, вызывается `cmd_start`. До `F.text` дело не доходит.

---

## Правило на будущее

**Порядок в router.py всегда:**
1. Команды (`Command("start")`, `Command("help")`, ...)
2. Специфичные фильтры (`F.text.startswith(...)`, `F.photo`, ...)
3. Общий catch-all (`F.text`) — всегда последним

---

## Проверки после исправления

- Отправь `/start` — должен ответить "Привет! Я бот."
- Отправь `/help` — должен ответить "Справка по командам..."
- Отправь обычный текст "привет" — должен ответить "Вы написали: привет"

---

## Что затронуто / Что проверить

**Затронуто:** только `router.py` — перестановка блоков, логика не меняется.

**Side effects:** нет. Это чисто структурное исправление.

✅ Проверено: логика каждого хэндлера не изменилась, только порядок регистрации.
⚠️ Не проверено: если в проекте есть другие файлы с роутерами — проверить их на тот же паттерн `F.text` выше `Command()`.

---

## Опыт применён

**EXP-053** (критический) — aiogram 3: порядок хэндлеров = приоритет команд.
Этот урок был записан после точно такой же проблемы в VoiceTranscriptionBot v5.4.0, где `/calc`, `/rate`, `/route` молча не работали при зелёных тестах.

---

```
=== Engineering Advisor Summary ===
Файлы изменены: 0 (диагностика без правок)
Триггеры сработали: #19 (порядок хэндлеров — F.text до Command())
BLOCK: 0
WARN: 1 — F.text catch-all перехватывает Command() хэндлеры
INFO: 0
Опыт применён: EXP-053
Новый опыт: нет (урок уже записан)
===================================
```
