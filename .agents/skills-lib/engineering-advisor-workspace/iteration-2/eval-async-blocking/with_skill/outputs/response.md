# Ответ Engineering Advisor — eval-async-blocking

**Дата:** 2026-03-05
**Скилл:** engineering-advisor v4.1
**Запрос:** Добавить логирование в aiogram voice handler

---

## Активация скилла

Engineering Advisor активирован. Загружено 5 критических уроков из опыта. Применяются уроки EXP-053 (порядок хэндлеров), EXP-040 (dataclass fields), WARN-006 (субагенты).

---

## Анализ кода

=== Engineering Advisor ===

**BLOCK (2):**

1. `handle_voice:9` — `time.sleep(2)` в async-функции. Блокирующий вызов, замораживает весь event loop aiogram. Триггер #20: **MANDATORY**.

2. `handle_voice:10` — `requests.post(...)` в async-функции. Синхронная библиотека, блокирует event loop на время HTTP-запроса. Триггер #20: **MANDATORY**.

**WARN (1):**

3. `handle_voice:5-7` — `openai_client.audio.transcriptions.create(...)` — потенциально синхронный вызов OpenAI SDK. Нужно уточнить: `openai.AsyncOpenAI` или `openai.OpenAI`?

Опыт: применено 1 урок (EXP-053 aiogram async pattern)

===========================

---

## Объяснение проблемы (на пальцах)

Aiogram работает на одном async event loop. Когда хэндлер вызывает `time.sleep(2)` — весь бот "засыпает". Это как поставить заглушку на дорогу: пока одна машина стоит, все остальные стоят за ней. При 10 одновременных пользователях бот станет недоступен на 20 секунд.

---

## Почему я не добавил логирование как есть

Добавить `logging.info("начало")` в функцию с `time.sleep()` — это как поставить красивые перила на сломанный мост. Лог будет, бот будет замороженным.

---

## Исправления перед добавлением логирования

```python
# БЫЛО (блокирующий код):
import time
import requests

time.sleep(2)
requests.post("https://api.example.com/log", json={"text": result.text})

# СТАЛО (async-варианты):
import asyncio
import aiohttp

await asyncio.sleep(2)  # если sleep вообще нужен
async with aiohttp.ClientSession() as session:
    await session.post("https://api.example.com/log", json={"text": result.text})
```

Для OpenAI — заменить `openai.OpenAI` на `openai.AsyncOpenAI`:
```python
# БЫЛО:
result = openai_client.audio.transcriptions.create(...)

# СТАЛО:
result = await openai_client.audio.transcriptions.create(...)
# где openai_client = AsyncOpenAI(api_key=...)
```

---

## Исправленная версия с логированием (полная)

```python
import logging
import asyncio
import aiohttp
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
openai_client = AsyncOpenAI(api_key="...")

@router.message(F.voice)
async def handle_voice(message: Message):
    logger.info("[voice] входящее: user_id=%s, file_id=%s", message.from_user.id, message.voice.file_id)

    try:
        file = await bot.get_file(message.voice.file_id)
        voice_path = f"voices/{message.voice.file_id}.ogg"
        await bot.download_file(file.file_path, voice_path)

        # Транскрипция через OpenAI (async)
        result = await openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=open(voice_path, "rb")
        )

        # Async HTTP вместо requests
        async with aiohttp.ClientSession() as session:
            await session.post("https://api.example.com/log", json={"text": result.text})

        await message.answer(f"Транскрипция: {result.text}")
        logger.info("[voice] успех: user_id=%s, длина=%d символов", message.from_user.id, len(result.text))

    except Exception as e:
        logger.error("[voice] ошибка: user_id=%s, error=%s", message.from_user.id, str(e))
        raise
```

Изменения:
- `time.sleep(2)` удалён (зачем ждать перед ответом?)
- `requests.post` → `aiohttp` (async HTTP)
- `OpenAI` → `AsyncOpenAI`
- Логирование входящего события + результата + ошибок

---

## Что проверено / не проверено

Проверено:
- Блокирующие вызовы устранены
- Логирование добавлено в начало и конец
- Ошибки логируются с re-raise

Не проверено вручную:
- Совместимость версии aiohttp с проектом
- Правильный путь к voice файлу (нет проверки что папка `voices/` существует)
- Что происходит если OpenAI API недоступен (timeout handling)

---

## Вердикт скилла

Запрос был: "просто добавь логирование". Но код содержал 2 BLOCK-проблемы (блокирующие вызовы в async), которые делают бот нерабочим под нагрузкой. Скилл обнаружил это и предложил исправить вместе с логированием.

**Триггеры:** #20 (блокирующие вызовы в async) — MANDATORY x2
**Применённый опыт:** EXP-053 (aiogram async patterns)
