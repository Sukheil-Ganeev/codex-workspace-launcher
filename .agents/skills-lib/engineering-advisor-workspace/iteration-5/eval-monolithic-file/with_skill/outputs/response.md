# Engineering Advisor — Анализ запроса

**Запрос:** Добавить хэндлер голосовых сообщений с транскрипцией через Whisper в handlers.py (1200 строк)

---

Engineering Advisor активирован. Загружено 5 критических уроков из опыта. Буду проверять код с учётом накопленных ошибок.

---

## Применённые уроки

- **EXP-053** — порядок хэндлеров в aiogram 3: Command() выше F.text
- **EXP-001** — Advisory level first, не блокировать пользователя
- **WARN-006** — субагенты не наследуют контекст скиллов

---

```
=== Engineering Advisor ===

BLOCK (1): handlers.py — Whisper через синхронный клиент в async-хэндлере
WARN  (2): handlers.py:1200 строк — монолитный файл; порядок хэндлеров не проверен
INFO  (2): разделить на модули; добавить callback.answer() проверку

Опыт: применено 2 урока (EXP-053, WARN-006)
===========================
```

---

## BLOCK (1) — Остановка. Нельзя применять пока не исправлено

### handlers.py — Блокирующий вызов в async-хэндлере (Триггер #20, MANDATORY)

**Проблема:** Транскрипция через Whisper с использованием синхронного клиента (`openai.Audio.transcribe()` или `client.audio.transcriptions.create()`) внутри `async def handle_voice()` заблокирует весь event loop aiogram. Пока один пользователь отправляет голосовое сообщение — все остальные пользователи бота ждут. Это не гипотетический риск, это гарантированное поведение asyncio.

**Что нельзя делать:**
```python
@router.message(F.voice)
async def handle_voice(message: Message):
    file = await bot.download(message.voice.file_id)  # OK — async

    # BLOCK: openai синхронный клиент блокирует event loop
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=file
    )
```

**Обязательное решение — два варианта:**

Вариант A — `asyncio.to_thread()` (Python 3.9+, рекомендован):
```python
import asyncio

@router.message(F.voice)
async def handle_voice(message: Message):
    file = await bot.download(message.voice.file_id)

    # Выносим блокирующий вызов в отдельный поток
    result = await asyncio.to_thread(
        client.audio.transcriptions.create,
        model="whisper-1",
        file=file
    )
    await message.answer(result.text)
```

Вариант B — `openai` async клиент (если версия >= 1.0):
```python
from openai import AsyncOpenAI

async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@router.message(F.voice)
async def handle_voice(message: Message):
    file = await bot.download(message.voice.file_id)
    result = await async_client.audio.transcriptions.create(
        model="whisper-1",
        file=file
    )
    await message.answer(result.text)
```

**Делегация:** superpowers:systematic-debugging — проверить все места где sync-клиент вызывается в async-контексте.

---

## WARN (2) — Предупреждения. Работает, но создаёт риск

### WARN 1: handlers.py — монолитный файл 1200 строк (Триггер #22, Advisory)

**Проблема:** Файл содержит минимум 9 хэндлеров разной ответственности:
- Команды (`/start`, `/help`, `/book`, `/price`, `/status`)
- Callback-хэндлеры (`book_*`, `pay_*`)
- Медиа-хэндлеры (`F.photo`, `F.document`)
- И теперь ещё `F.voice` с бизнес-логикой транскрипции

Это классический God Object. Добавление ещё одного хэндлера в этот файл только усиливает проблему.

**Рекомендация — план разделения:**
```
handlers/
├── __init__.py          # re-export всех роутеров
├── commands.py          # /start, /help, /book, /price, /status
├── callbacks.py         # book_*, pay_* CallbackQuery handlers
├── media.py             # F.photo, F.document, F.voice ← новый хэндлер сюда
└── services/
    └── transcription.py # Whisper логика (изолирована, тестируема)
```

Whisper-логику вынести в отдельный сервис — это позволит тестировать транскрипцию независимо от aiogram.

**Делегация:** superpowers:writing-plans — составить пошаговый план разделения.

---

### WARN 2: Порядок хэндлеров не проверен (Триггер #19, Recommended + EXP-053)

**Проблема:** В коде видны callback-хэндлеры с `F.data.startswith('book_')` и медиа-хэндлеры. Если в файле (в тех 600+ строках которые не показаны) есть `@router.message(F.text)` catch-all — он может перехватывать команды, включая будущие голосовые.

**Проверка (выполнить немедленно):**
```bash
grep -n "F\.text\|F\.voice\|F\.photo\|F\.document\|Command(" handlers.py | head -40
```

**Правило (EXP-053):** Порядок регистрации = приоритет. В aiogram 3.x:
```
Command("start")     ← ВЫШЕ (конкретный)
Command("book")      ← ВЫШЕ
F.voice              ← ВЫШЕ медиа-хэндлеры
F.photo              ← конкретные типы
F.document           ← конкретные типы
F.text               ← НИЖЕ (catch-all, последним)
```

---

## INFO (2) — Советы. Улучшение качества

### INFO 1: Добавить callback.answer() проверку (Триггер #21, Advisory)

В коде есть два CallbackQuery хэндлера (`process_booking`, `process_payment`). Убедиться что каждый из них вызывает `await callback.answer()`. Без него пользователь видит спиннер 30 секунд после нажатия кнопки.

```bash
# Проверка:
grep -n "callback\.answer" handlers.py
# Количество вызовов должно быть >= количеству @router.callback_query
```

### INFO 2: Изолировать Whisper в отдельный сервис (Триггер #3, Recommended)

Транскрипция — это бизнес-логика с внешним API. Лучше изолировать:

```python
# services/transcription.py
import asyncio
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_voice(audio_file: bytes) -> str:
    """Транскрибирует голосовое сообщение через Whisper."""
    result = await asyncio.to_thread(
        client.audio.transcriptions.create,
        model="whisper-1",
        file=audio_file
    )
    return result.text
```

Это позволяет:
- Тестировать транскрипцию без aiogram
- Мокировать в тестах: `MagicMock(spec=transcribe_voice)`
- Легко заменить Whisper на другой провайдер

---

## Итог: что делать прямо сейчас

| Приоритет | Действие | Время |
|-----------|----------|-------|
| 1. BLOCK | Whisper через `asyncio.to_thread()` или AsyncOpenAI | 5 мин |
| 2. WARN | Проверить порядок хэндлеров (`grep -n "F\.text"`) | 2 мин |
| 3. INFO | Вынести transcription в services/ | 10 мин |
| 4. INFO | Запланировать разделение handlers.py | позже |

**Минимальная версия нового хэндлера (безопасная):**

```python
import asyncio
from aiogram import F
from aiogram.types import Message
from openai import OpenAI

_openai = OpenAI(api_key=settings.OPENAI_API_KEY)

@router.message(F.voice)
async def handle_voice(message: Message):
    """Обработка голосовых сообщений с транскрипцией через Whisper."""
    await message.answer("Обрабатываю голосовое сообщение...")

    try:
        # Скачиваем файл
        voice_file = await message.bot.get_file(message.voice.file_id)
        file_data = await message.bot.download_file(voice_file.file_path)

        # ВАЖНО: asyncio.to_thread — не блокирует event loop
        result = await asyncio.to_thread(
            _openai.audio.transcriptions.create,
            model="whisper-1",
            file=("voice.ogg", file_data, "audio/ogg")
        )

        await message.answer(f"Транскрипция:\n{result.text}")

    except Exception as e:
        await message.answer("Не удалось распознать голосовое сообщение.")
        # Логирование: добавить logger.error(f"[voice] transcription error: {e}")
```

**Важно:** Разместить этот хэндлер ДО любого `F.text` catch-all в файле.

---

## Что проверено / не проверено

- Выявлено: блокирующий вызов (критичный баг) — требует исправления до деплоя
- Выявлено: монолитный файл 1200 строк — Advisory
- Не проверено: реальный порядок всех хэндлеров в полном файле (нужен grep)
- Не проверено: наличие callback.answer() во всех CallbackQuery хэндлерах

---

## Завершение сессии

```
=== Engineering Advisor Summary ===
Файлы изменены: 0 (анализ, не выполнение)
Триггеры сработали: #20 (блокирующий async), #22 (монолит), #19 (порядок), #21 (callback)
Проверки: анализ по фрагменту кода
BLOCK: 1 — Whisper sync client в async handler
WARN: 2 — монолит 1200 строк; порядок хэндлеров не верифицирован
INFO: 2 — изоляция сервиса; callback.answer() проверка
Опыт применён: EXP-053, EXP-001, WARN-006
Новый опыт: не зафиксирован (паттерн уже покрыт триггером #20)
===================================
```
