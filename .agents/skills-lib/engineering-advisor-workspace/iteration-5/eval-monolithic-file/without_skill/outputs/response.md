# Ответ: добавление хэндлера голосовых сообщений

Вот хэндлер для голосовых сообщений с транскрипцией через Whisper. Добавь его в `handlers.py` после `handle_document`:

```python
import io
import openai
from aiogram.types import Voice

@router.message(F.voice)
async def handle_voice(message: Message):
    # Лог входящего события
    print(f"[handlers] handle_voice: user_id={message.from_user.id}, duration={message.voice.duration}s")

    # Скачиваем голосовое сообщение
    voice: Voice = message.voice
    file = await message.bot.get_file(voice.file_id)
    file_bytes = await message.bot.download_file(file.file_path)

    # Транскрибируем через Whisper
    try:
        audio_buffer = io.BytesIO(file_bytes.read())
        audio_buffer.name = "voice.ogg"

        client = openai.AsyncOpenAI()  # берёт OPENAI_API_KEY из окружения
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_buffer,
            language="ru"  # или убери этот параметр для автодетекта
        )

        text = transcription.text
        print(f"[handlers] handle_voice: transcription done, chars={len(text)}")

        await message.answer(
            f"Распознанный текст:\n\n{text}"
        )

    except openai.OpenAIError as e:
        print(f"[handlers] handle_voice: error={e}")
        await message.answer("Не удалось распознать голосовое сообщение. Попробуй ещё раз.")
```

## Что нужно добавить в импорты (в начало файла)

```python
import io
import openai
```

## Зависимости

Если `openai` ещё не установлен:

```bash
pip install openai
```

## Как это работает

1. Фильтр `F.voice` ловит только голосовые сообщения
2. Скачиваем файл через Bot API
3. Кладём в `BytesIO` — Whisper принимает file-like объект
4. Ставим `.name = "voice.ogg"` — Whisper смотрит на расширение для формата
5. Отправляем в Whisper, получаем текст, возвращаем пользователю

## Примечания

- `language="ru"` — фиксирует язык транскрипции, убери если нужен автодетект
- Модель `whisper-1` — стандартная, дешевле чем `whisper-large`
- Добавь обработку `asyncio.TimeoutError` если голосовые бывают длинными (>1 мин)
- Если хочешь не просто вернуть текст, а обработать его как команду — добавь логику после получения `text`
