# Интеграция скиллов — Yandex SpeechKit

> Как объединить yandex-speechkit-туризм с другими скиллами для создания автоматизированных workflows

---

## Философия интеграции

Yandex SpeechKit — это **промежуточный этап** в обработке данных:
1. **Вход:** Голосовое сообщение (аудио файл)
2. **Обработка:** Транскрипция в текст
3. **Выход:** Текстовая версия для дальнейшего анализа

Скилл работает как **мост** между:
- Источниками аудио (WhatsApp, Telegram, Make.com)
- Обработчиками текста (обработка запросов, NLP, классификация)
- Системами ответа (Telegram боты, email, CRM)

---

## Workflow 1: Обработка запросов клиентов из WhatsApp

**Задача:** Клиент отправляет голосовое в WhatsApp группу, агент получает текстовую транскрипцию с автоматическим ответом.

```
┌─────────────────────┐
│ 1. WhatsApp голосовое│
│    от клиента        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ whatsapp-парсер     │
│ - Экспорт чата      │
│ - Извлечение аудио  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ yandex-speechkit    │ ← ВЫ ЗДЕСЬ
│ - Транскрибация     │
│ - Текст из голоса   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ обработка-запросов  │
│ - Анализ текста     │
│ - Определение тура  │
│ - Расчёт цены       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ создание-карточек   │
│ - Форматирование    │
│ - Каталог туров     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ vip-dxb-rus-bot     │
│ - Отправка в        │
│   Telegram          │
└─────────────────────┘
```

**Код интеграции:**

```python
# Step 1: Извлечение аудио из WhatsApp
from whatsapp_parser import parse_chat, extract_audio

chat = parse_chat("WhatsApp Chat.txt")
audio_files = extract_audio(chat, media_folder="_chat/")

# Step 2: Транскрибация
from yandex_speechkit import transcribe_any_audio

for audio in audio_files:
    text = transcribe_any_audio(audio.path, lang="ru-RU")

    # Step 3: Анализ запроса
    from processing import analyze_request
    request = analyze_request(text)
    # {'type': 'tour_request', 'tour': 'desert safari', 'pax': 4, 'date': '2026-03-15'}

    # Step 4: Создание ответа
    from catalog import create_tour_card
    response = create_tour_card(request['tour'])

    # Step 5: Отправка в Telegram
    from telegram_bot import send_message
    await send_message(chat_id=audio.sender_id, text=response)
```

**Время выполнения:** ~5 секунд от голосового до ответа в Telegram

**Настройка:** `assets/examples/whatsapp-voice-transcriber/`

---

## Workflow 2: Telegram бот с транскрипцией

**Задача:** Клиент отправляет голосовое в Telegram бота, получает транскрипцию + ответ.

```
┌─────────────────────┐
│ Telegram Bot API    │
│ Голосовое сообщение │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ vip-dxb-rus-bot     │
│ - Получение voice   │
│ - Скачивание .ogg   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ yandex-speechkit    │ ← ВЫ ЗДЕСЬ
│ - Транскрибация     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ обработка-запросов  │
│ - Claude API        │
│ - Классификация     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ vip-dxb-rus-bot     │
│ - Отправка ответа   │
└─────────────────────┘
```

**Код:**

```python
# telegram-bot/handlers/voice.py
from telegram import Update
from telegram.ext import ContextTypes
from yandex_speechkit import transcribe_any_audio
from processing import process_client_request

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Скачиваем голосовое
    voice = update.message.voice
    file = await voice.get_file()
    audio_path = f"temp_{voice.file_id}.ogg"
    await file.download_to_drive(audio_path)

    # 2. Транскрибируем
    await update.message.reply_text("🎤 Обрабатываю ваше голосовое...")
    text = transcribe_any_audio(audio_path, lang="ru-RU")

    # 3. Показываем транскрипцию
    await update.message.reply_text(f"📝 Вы сказали:\n\n{text}")

    # 4. Обрабатываем запрос
    response = await process_client_request(text, user=update.effective_user)

    # 5. Отправляем ответ
    await update.message.reply_text(response)

    # Cleanup
    os.remove(audio_path)
```

**Пример:** `assets/examples/telegram-bot-integration/`

---

## Workflow 3: Make.com → SpeechKit → Notion

**Задача:** Голосовые заметки из мобильного → Make.com → транскрипция → сохранение в Notion.

```
┌─────────────────────┐
│ Голосовая заметка   │
│ (iOS/Android)       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Make.com Webhook    │
│ - Получает аудио URL│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Netlify Function    │
│ с yandex-speechkit  │
│ - Скачивает аудио   │
│ - Транскрибирует    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Make.com HTTP       │
│ - Получает текст    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Notion API          │
│ - Создаёт страницу  │
│ - Сохраняет текст   │
└─────────────────────┘
```

**Make.com Scenario:**

1. **Webhook Module:** Получает аудио URL
2. **HTTP Request Module:**
   ```
   URL: https://your-function.netlify.app/.netlify/functions/transcribe
   Method: POST
   Body: {"audio_url": "{{webhook.audio_url}}"}
   ```
3. **Notion Create Page Module:**
   ```
   Database: Voice Notes
   Title: {{currentDate}}
   Content: {{2.data.text}}
   ```

**Netlify Function:**

```javascript
// netlify/functions/transcribe.js
const fetch = require('node-fetch');
const FormData = require('form-data');

exports.handler = async (event) => {
  const { audio_url } = JSON.parse(event.body);

  // Скачиваем аудио
  const audioResponse = await fetch(audio_url);
  const audioBuffer = await audioResponse.buffer();

  // Транскрибируем через Yandex SpeechKit
  const formData = new FormData();
  formData.append('audio', audioBuffer, 'voice.ogg');

  const speechResponse = await fetch(
    `https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId=${process.env.YANDEX_CLOUD_FOLDER_ID}&lang=ru-RU&format=oggopus`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Api-Key ${process.env.YANDEX_CLOUD_API_KEY}`
      },
      body: audioBuffer
    }
  );

  const result = await speechResponse.json();

  return {
    statusCode: 200,
    body: JSON.stringify({ text: result.result })
  };
};
```

**Пример:** `assets/examples/make-com-webhook/`

---

## Workflow 4: Парсинг WhatsApp → Notion CRM

**Задача:** Все голосовые из WhatsApp чата с клиентами автоматически транскрибируются и сохраняются в Notion CRM.

```
┌─────────────────────┐
│ WhatsApp экспорт    │
│ "_chat.txt"         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ whatsapp-парсер     │
│ - Извлечение аудио  │
│ - Метаданные        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ yandex-speechkit    │ ← ВЫ ЗДЕСЬ
│ - Batch processing  │
│ - Параллельно       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ туризм-оаэ-бизнес   │
│ - Профиль клиента   │
│ - История общения   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Notion API          │
│ - CRM Database      │
│ - Voice Notes       │
└─────────────────────┘
```

**Код:**

```python
# whatsapp_to_notion.py
from whatsapp_parser import parse_chat, extract_audio
from yandex_speechkit import transcribe_any_audio
from notion_client import Client

# 1. Парсим WhatsApp
chat = parse_chat("_chat.txt")
audio_files = extract_audio(chat)

# 2. Транскрибируем все аудио (параллельно)
from concurrent.futures import ThreadPoolExecutor

def process_audio(audio):
    text = transcribe_any_audio(audio.path)
    return {
        "sender": audio.sender,
        "date": audio.date,
        "text": text,
        "audio_path": audio.path
    }

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_audio, audio_files))

# 3. Сохраняем в Notion
notion = Client(auth=NOTION_TOKEN)

for result in results:
    notion.pages.create(
        parent={"database_id": NOTION_CRM_DB_ID},
        properties={
            "Name": {"title": [{"text": {"content": result["sender"]}}]},
            "Date": {"date": {"start": result["date"]}},
            "Type": {"select": {"name": "Voice Message"}},
            "Transcription": {"rich_text": [{"text": {"content": result["text"]}}]}
        }
    )

print(f"✅ Processed {len(results)} voice messages")
```

---

## Workflow 5: Автоответы в WhatsApp через туризм-оаэ-автоматизация

**Задача:** Голосовое от клиента → транскрипция → Claude классификация → автоответ.

```
┌─────────────────────┐
│ WhatsApp Business   │
│ API Webhook         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ yandex-speechkit    │ ← ВЫ ЗДЕСЬ
│ - Транскрибация     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ туризм-оаэ-         │
│ автоматизация       │
│ - Claude API        │
│ - Классификация     │
│ - Извлечение данных │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ обработка-запросов  │
│ - Определение тура  │
│ - Расчёт цены       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ WhatsApp Business   │
│ API - Отправка      │
│ ответа клиенту      │
└─────────────────────┘
```

**Код:**

```python
# whatsapp_webhook.py
from flask import Flask, request
from yandex_speechkit import transcribe_any_audio
from claude_classifier import classify_request
from processing import create_response

app = Flask(__name__)

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json

    # 1. Получаем голосовое
    if data.get('message', {}).get('type') == 'audio':
        audio_url = data['message']['audio']['url']

        # Скачиваем
        import requests
        audio = requests.get(audio_url).content
        with open('temp.ogg', 'wb') as f:
            f.write(audio)

        # 2. Транскрибируем
        text = transcribe_any_audio('temp.ogg')

        # 3. Классифицируем через Claude
        classification = classify_request(text)
        # {'intent': 'tour_booking', 'tour': 'desert_safari', 'pax': 4}

        # 4. Создаём ответ
        response = create_response(classification)

        # 5. Отправляем обратно
        send_whatsapp_message(
            to=data['message']['from'],
            text=response
        )

        os.remove('temp.ogg')

    return {'status': 'ok'}
```

**Пример:** `assets/examples/whatsapp-voice-transcriber/`

---

## Интеграция с другими скиллами

### 1. whatsapp-парсер

**Что получаем:**
- Список аудио файлов из WhatsApp экспорта
- Метаданные: отправитель, дата, время
- Путь к файлам .opus

**Что отдаём:**
- Транскрибированный текст для каждого аудио
- Замена в тексте чата: `[voice message]` → `📝 "Текст транскрипции"`

**Связь:**
```python
from whatsapp_parser import parse_chat, extract_audio

audio_files = extract_audio(parse_chat("chat.txt"))

for audio in audio_files:
    text = transcribe_any_audio(audio.path)  # yandex-speechkit
    audio.transcription = text
```

---

### 2. обработка-запросов-турагентов

**Что получаем:**
- Текст транскрипции голосового

**Что отдаём:**
- Структурированные данные запроса:
  ```python
  {
    'tour': 'Desert Safari',
    'pax': 4,
    'date': '2026-03-15',
    'language': 'ru'
  }
  ```

**Связь:**
```python
# 1. Транскрибируем
text = transcribe_any_audio("voice.ogg")  # yandex-speechkit

# 2. Анализируем запрос
from request_processor import analyze_client_request
request = analyze_client_request(text)  # обработка-запросов-турагентов

# 3. Формируем ответ
response = create_tour_offer(request)
```

---

### 3. создание-карточек-каталога

**Что получаем:**
- Структурированные данные тура

**Что отдаём:**
- Отформатированная карточка для WhatsApp/Telegram

**Связь:**
```python
# 1. Транскрипция
text = transcribe("voice.ogg")

# 2. Извлечение тура
tour_name = extract_tour_name(text)  # "desert safari"

# 3. Создание карточки
from catalog import create_tour_card
card = create_tour_card(tour_name)  # создание-карточек-каталога

# 4. Отправка
send_to_client(card)
```

---

### 4. vip-dxb-rus-telegram-bot

**Что получаем:**
- Voice message от Telegram Bot API

**Что отдаём:**
- Транскрипцию для обработки ботом

**Связь:**
```python
# В боте (vip-dxb-rus-telegram-bot)
async def voice_handler(update, context):
    voice = update.message.voice

    # Скачиваем
    file = await voice.get_file()
    await file.download_to_drive("temp.ogg")

    # Транскрибируем (yandex-speechkit)
    from yandex_speechkit import transcribe_any_audio
    text = transcribe_any_audio("temp.ogg")

    # Обрабатываем как обычное текстовое сообщение
    await process_text_message(update, context, text)
```

---

### 5. туризм-оаэ-автоматизация

**Что получаем:**
- Голосовые сообщения из разных источников

**Что отдаём:**
- Текст для Claude API классификации

**Связь:**
```python
# Workflow автоматизации
def process_voice_request(audio_path: str):
    # 1. Транскрибируем (yandex-speechkit)
    text = transcribe_any_audio(audio_path)

    # 2. Классифицируем (Claude API - туризм-оаэ-автоматизация)
    from automation import classify_with_claude
    classification = classify_with_claude(text)

    # 3. Автоответ
    if classification['confidence'] > 0.8:
        response = generate_auto_response(classification)
        send_to_client(response)
    else:
        # Передаём агенту
        notify_agent(text, classification)
```

---

### 6. api-туризм-оаэ

**Что получаем:**
- Webhook endpoints для интеграций

**Что отдаём:**
- Транскрибированный текст через API

**Связь:**
```python
# FastAPI endpoint (api-туризм-оаэ)
from fastapi import FastAPI, UploadFile
from yandex_speechkit import transcribe_any_audio

app = FastAPI()

@app.post("/api/v1/transcribe")
async def transcribe_endpoint(audio: UploadFile):
    # Сохраняем временно
    temp_path = f"temp_{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(await audio.read())

    # Транскрибируем
    text = transcribe_any_audio(temp_path)

    # Cleanup
    os.remove(temp_path)

    return {"text": text, "language": "ru-RU"}
```

---

### 7. ocr-туризм

**Связь:** Параллельные задачи распознавания.

- **OCR-туризм:** Изображения → текст (чеки, паспорта)
- **Yandex SpeechKit:** Аудио → текст (голосовые)

**Комбинированный workflow:**
```python
from ocr import extract_text_from_image
from yandex_speechkit import transcribe_any_audio

# Обработка мультимедиа запроса
def process_media(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.jpg', '.png', '.pdf']:
        return extract_text_from_image(file_path)  # ocr-туризм
    elif ext in ['.ogg', '.mp3', '.wav']:
        return transcribe_any_audio(file_path)  # yandex-speechkit
    else:
        raise ValueError(f"Unsupported format: {ext}")
```

---

## Таблица интеграций

| Скилл | Входные данные | Выходные данные | Связь |
|-------|---------------|----------------|-------|
| **whatsapp-парсер** | WhatsApp экспорт | Аудио файлы + метаданные | Источник аудио |
| **обработка-запросов-турагентов** | Транскрипция | Структурированный запрос | Обработчик текста |
| **создание-карточек-каталога** | Название тура | Отформатированная карточка | Генератор ответа |
| **vip-dxb-rus-telegram-bot** | Voice message | Транскрипция | Telegram интеграция |
| **туризм-оаэ-автоматизация** | Транскрипция | Классификация + автоответ | Claude API |
| **api-туризм-оаэ** | HTTP запрос | API ответ | Webhook endpoint |
| **ocr-туризм** | Изображение | Текст | Параллельная задача |

---

## Best Practices интеграции

### 1. Единообразный интерфейс

Все функции транскрипции возвращают единый формат:

```python
def transcribe_any_audio(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Универсальная транскрипция.

    Args:
        audio_path: Путь к аудио
        lang: Язык (ru-RU, en-US, ar-AE)

    Returns:
        str: Транскрибированный текст
    """
    # Обработка длинных файлов автоматически
    # ...
```

---

### 2. Error handling с fallback

```python
def transcribe_with_fallback(audio_path: str) -> dict:
    """Транскрибация с fallback на Whisper."""
    try:
        text = transcribe_any_audio(audio_path)
        return {"text": text, "source": "speechkit"}
    except Exception as e:
        logger.warning(f"SpeechKit failed: {e}, falling back to Whisper")
        from whisper import transcribe_whisper
        text = transcribe_whisper(audio_path)
        return {"text": text, "source": "whisper"}
```

---

### 3. Асинхронная обработка

```python
import asyncio

async def process_voice_queue(audio_files: list):
    """Обработка очереди голосовых сообщений."""
    tasks = [transcribe_async(audio) for audio in audio_files]
    results = await asyncio.gather(*tasks)
    return results
```

---

### 4. Кеширование между скиллами

```python
# Общий кеш для всех скиллов
CACHE_DIR = "C:/Users/londo/.claude/cache/transcriptions/"

def transcribe_cached(audio_path: str) -> str:
    cache_key = hashlib.md5(open(audio_path, "rb").read()).hexdigest()
    cache_file = f"{CACHE_DIR}/{cache_key}.txt"

    if os.path.exists(cache_file):
        return open(cache_file).read()

    text = transcribe_any_audio(audio_path)
    with open(cache_file, "w") as f:
        f.write(text)

    return text
```

---

## Примеры полной интеграции

### Пример 1: WhatsApp → Notion CRM (полный пайплайн)

```python
# full_pipeline.py
from whatsapp_parser import parse_chat, extract_audio
from yandex_speechkit import transcribe_any_audio
from request_processor import analyze_client_request
from notion_client import Client

# 1. Парсим WhatsApp
audio_files = extract_audio(parse_chat("chat.txt"))

# 2. Транскрибируем
transcriptions = [
    {
        "sender": audio.sender,
        "date": audio.date,
        "text": transcribe_any_audio(audio.path)
    }
    for audio in audio_files
]

# 3. Анализируем запросы
for t in transcriptions:
    t["request"] = analyze_client_request(t["text"])

# 4. Сохраняем в Notion
notion = Client(auth=NOTION_TOKEN)
for t in transcriptions:
    notion.pages.create(
        parent={"database_id": CRM_DB_ID},
        properties={
            "Client": {"title": [{"text": {"content": t["sender"]}}]},
            "Date": {"date": {"start": t["date"]}},
            "Transcription": {"rich_text": [{"text": {"content": t["text"]}}]},
            "Tour": {"select": {"name": t["request"]["tour"]}},
            "PAX": {"number": t["request"]["pax"]}
        }
    )
```

---

### Пример 2: Telegram бот с полной автоматизацией

См. `assets/examples/telegram-bot-integration/`

---

## Связанные ресурсы

- **Основной SKILL.md:** Детали API yandex-speechkit
- **references/integrations.md:** Технические детали интеграций
- **assets/examples/:** Полные рабочие примеры
- **Другие скиллы:** Документация по интегрируемым скиллам

---

**Последнее обновление:** 2026-02-05
**Версия:** 1.0
**Скилл:** yandex-speechkit-туризм
