# Шпаргалка — Yandex SpeechKit

> Быстрый справочник для транскрипции голосовых сообщений

---

## Переменные окружения

```bash
# В .env файле
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f
```

```python
# В коде
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
FOLDER_ID = os.getenv("YANDEX_CLOUD_FOLDER_ID")
```

---

## Быстрый старт

### Базовая транскрипция (<30 сек)

```python
import requests
import os

def transcribe(audio_path: str, lang: str = "ru-RU") -> str:
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": lang,
            "format": "oggopus",
            "sampleRateHertz": 48000
        },
        headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        },
        data=open(audio_path, "rb")
    )
    return response.json().get("result", "")

# Использование
text = transcribe("voice.ogg")
print(text)
```

---

### Универсальная транскрипция (любая длина)

```python
import subprocess
import math

def transcribe_any(audio_path: str, lang: str = "ru-RU") -> str:
    duration = get_duration(audio_path)

    if duration <= 29:
        return transcribe(audio_path, lang)

    # Делим на части
    num_chunks = math.ceil(duration / 29.0)
    transcripts = []

    for i in range(num_chunks):
        chunk = f"{audio_path}_chunk_{i:03d}.ogg"
        subprocess.run([
            'ffmpeg', '-i', audio_path,
            '-ss', str(i * 29), '-t', '29',
            '-c', 'copy', chunk, '-y'
        ], capture_output=True)

        text = transcribe(chunk, lang)
        transcripts.append(text)
        os.remove(chunk)

    return " ".join(transcripts)

def get_duration(audio_path: str) -> float:
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())
```

---

## API Endpoints

| API | URL | Описание |
|-----|-----|----------|
| **Sync** | `https://stt.api.cloud.yandex.net/speech/v1/stt:recognize` | До 30 сек, 1 МБ |
| **Async** | `https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize` | До 4 часов |
| **Streaming** | `wss://stt.api.cloud.yandex.net/speech/v1/stt:recognize` | Real-time |

---

## Языки

| Язык | Код | Использование в туризме ОАЭ |
|------|-----|----------------------------|
| Русский | `ru-RU` | **80%** — основной язык клиентов СНГ |
| Английский | `en-US` | 15% — европейцы, арабы (второй язык) |
| Арабский | `ar-AE` | 3% — местные жители |
| Турецкий | `tr-TR` | 1% — туристы из Турции |
| Казахский | `kk-KK` | 1% — клиенты из Казахстана |
| Узбекский | `uz-UZ` | <1% — клиенты из Узбекистана |

---

## Форматы аудио

| Формат | Параметр | Источник | Sample Rate |
|--------|----------|----------|-------------|
| OGG Opus | `oggopus` | WhatsApp, Telegram | 48000 Hz |
| MP3 | `mp3` | Универсальный | 44100 Hz |
| WAV/LPCM | `lpcm` | Без сжатия | 8000-48000 Hz |

**Рекомендация:** Для WhatsApp/Telegram используйте `oggopus` + `48000 Hz`

---

## Параметры запроса

### Обязательные

| Параметр | Значение | Описание |
|----------|----------|----------|
| `folderId` | `b1gvu3q8k1kafqd3sk5f` | ID каталога Yandex Cloud |
| `lang` | `ru-RU` | Язык распознавания |
| `format` | `oggopus` | Формат аудио |

### Опциональные

| Параметр | Значение | Описание |
|----------|----------|----------|
| `sampleRateHertz` | `48000` | Sample rate (для LPCM/Opus) |
| `model` | `general` | Модель: general, numbers, dates, names, phone |
| `profanityFilter` | `false` | Фильтр мата |
| `rawResults` | `false` | Альтернативные варианты |

---

## Headers

```python
headers = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "audio/ogg"  # или audio/mpeg для MP3
}
```

---

## Коды ошибок

| Код | Причина | Решение |
|-----|---------|---------|
| 400 | Неверный формат | Проверьте параметр `format` |
| 401 | Неверный API key | Проверьте `YANDEX_CLOUD_API_KEY` |
| 403 | Недостаточно прав | Проверьте разрешения сервисного аккаунта |
| 413 | Файл слишком большой | Используйте Async API или делите на части |
| 429 | Rate limit | Добавьте rate limiting (max 20 RPS) |
| 500 | Внутренняя ошибка | Retry с exponential backoff |

---

## Лимиты

| Параметр | Sync API | Async API |
|----------|----------|-----------|
| **Размер файла** | 1 МБ | 1 ГБ |
| **Длительность** | 30 сек | 4 часа |
| **Rate limit** | 20 RPS | 10 операций одновременно |
| **Результат** | Сразу | 30 сек - 5 мин |

---

## Стоимость

| Операция | Цена (руб за 15 сек) | Цена (USD за мин) |
|----------|----------------------|-------------------|
| Синхронное | 0.80 руб | ~$0.01 |
| Асинхронное | 0.48 руб | ~$0.006 |
| Streaming | 0.96 руб | ~$0.012 |

**Сравнение с конкурентами:**
- Whisper API: $0.006/мин (дешевле на 40%)
- Google Speech-to-Text: $0.006/мин
- Azure Speech: $0.001/мин (самый дешёвый)

---

## Типичные команды

### Получить длительность аудио

```bash
ffprobe -v quiet -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 audio.ogg
```

### Разделить на части (без перекодирования!)

```bash
# Часть 0-29 сек
ffmpeg -i audio.ogg -ss 0 -t 29 -c copy part_000.ogg -y

# Часть 29-58 сек
ffmpeg -i audio.ogg -ss 29 -t 29 -c copy part_001.ogg -y
```

### Конвертировать MP3 → OGG Opus

```bash
ffmpeg -i audio.mp3 -c:a libopus -b:a 24k audio.ogg
```

### Сжать OGG Opus (уменьшить размер)

```bash
ffmpeg -i audio.ogg -c:a libopus -b:a 16k audio_compressed.ogg
```

---

## Python snippets

### Автодетект языка

```python
def auto_detect(audio_path: str) -> dict:
    languages = ["ru-RU", "en-US", "ar-AE"]
    best = {"lang": None, "text": "", "confidence": 0}

    for lang in languages:
        try:
            text = transcribe(audio_path, lang)
            conf = len(text.split()) / 10  # Эвристика
            if conf > best["confidence"]:
                best = {"lang": lang, "text": text, "confidence": conf}
        except:
            continue

    return best
```

### Error handling с retry

```python
import time

def transcribe_with_retry(audio_path: str, max_retries=3):
    for attempt in range(max_retries):
        try:
            return transcribe(audio_path)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            time.sleep(wait_time)
```

### Batch processing с progress bar

```python
from tqdm import tqdm
import concurrent.futures

def batch_transcribe(audio_files: list) -> list:
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(transcribe, audio): audio
                   for audio in audio_files}

        for future in tqdm(concurrent.futures.as_completed(futures),
                          total=len(audio_files)):
            audio = futures[future]
            try:
                text = future.result()
                results.append({"file": audio, "text": text})
            except Exception as e:
                results.append({"file": audio, "error": str(e)})

    return results
```

### Кеширование результатов

```python
import hashlib
import json

def cache_key(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def transcribe_cached(audio_path: str) -> str:
    cache_file = "transcription_cache.json"
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}

    key = cache_key(audio_path)

    if key in cache:
        return cache[key]

    text = transcribe(audio_path)
    cache[key] = text
    json.dump(cache, open(cache_file, "w"))

    return text
```

---

## Интеграция с Telegram Bot

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

async def voice_handler(update: Update, context):
    voice = update.message.voice
    file = await voice.get_file()
    audio_path = f"temp_{voice.file_id}.ogg"
    await file.download_to_drive(audio_path)

    text = transcribe(audio_path)
    await update.message.reply_text(f"📝 {text}")

    os.remove(audio_path)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, voice_handler))
app.run_polling()
```

---

## Интеграция с WhatsApp (через webhook)

```python
from flask import Flask, request
import requests as req

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json

    if data.get('type') == 'audio':
        audio_url = data['media_url']

        # Скачиваем
        audio = req.get(audio_url).content
        with open('temp.ogg', 'wb') as f:
            f.write(audio)

        # Транскрибируем
        text = transcribe('temp.ogg')

        # Отправляем обратно (через Twilio/WhatsApp API)
        # ...

        os.remove('temp.ogg')

    return {'status': 'ok'}

app.run(port=5000)
```

---

## Make.com / n8n webhook

```javascript
// Netlify Function
exports.handler = async (event) => {
  const { audio_url } = JSON.parse(event.body);

  // Скачиваем аудио
  const audioBuffer = await fetch(audio_url).then(r => r.arrayBuffer());

  // Транскрибируем (через Python subprocess или прямой HTTP)
  const text = await transcribe(audioBuffer);

  return {
    statusCode: 200,
    body: JSON.stringify({ text })
  };
};
```

---

## Пост-обработка: коррекция туристических терминов

```python
CORRECTIONS = {
    # Достопримечательности
    "бурч халифа": "Burj Khalifa",
    "бурж халифа": "Burj Khalifa",
    "феррари ворлд": "Ferrari World",
    "дубай молл": "Dubai Mall",
    "пальма джумейра": "Palm Jumeirah",

    # Города
    "абудаби": "Абу-Даби",
    "дубаи": "Дубай",
    "рас аль хайма": "Рас-эль-Хайма",

    # Туры
    "саффари": "сафари",
    "квадрацикл": "квадроцикл",

    # Валюта
    "дирхамы": "дирхамов",
    "юсдт": "USDT"
}

def correct_text(text: str) -> str:
    result = text.lower()
    for wrong, correct in CORRECTIONS.items():
        result = result.replace(wrong, correct)
    return result
```

---

## CLI скрипты

### Транскрибировать файл

```bash
python scripts/batch-transcribe.py \
  --input voice.ogg \
  --lang ru-RU \
  --output transcription.txt
```

### Транскрибировать папку

```bash
python scripts/batch-transcribe.py \
  --input ./audio_folder/ \
  --output results.json \
  --parallel 5
```

### Валидировать аудио

```bash
python scripts/validate-audio.py voice.ogg
# ✅ Format: OGG Opus
# ✅ Duration: 25.3 sec (OK)
# ✅ Size: 450 KB (OK)
# ⚠️  Sample rate: 44100 Hz (recommended: 48000 Hz)
```

### Посчитать стоимость

```bash
python scripts/cost-calculator.py \
  --duration 120 \
  --api sync
# Duration: 120 sec (2 min)
# Segments: 8 × 15 sec
# Cost: 6.40 руб (~0.067 USD)
```

---

## Отладка

### Проверить API key

```bash
curl "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId=$FOLDER_ID&lang=ru-RU" \
  -H "Authorization: Api-Key $API_KEY" \
  --data-binary "@voice.ogg"
```

### Логирование запросов

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def transcribe_debug(audio_path: str) -> str:
    logger.info(f"Transcribing: {audio_path}")
    logger.debug(f"API Key: {API_KEY[:10]}...")

    response = requests.post(...)

    logger.debug(f"Status: {response.status_code}")
    logger.debug(f"Response: {response.text[:200]}")

    return response.json().get("result", "")
```

---

## Связанные команды

### Показать структуру скилла

```bash
ls -R C:/Users/londo/.claude/skills/yandex-speechkit-туризм/
```

### Скопировать шаблон

```bash
cp C:/Users/londo/.claude/skills/yandex-speechkit-туризм/assets/templates/basic-transcription.py \
   ./my_project/transcribe.py
```

### Запустить пример

```bash
cd C:/Users/londo/.claude/skills/yandex-speechkit-туризм/assets/examples/telegram-bot-integration/
python main.py
```

---

## Полезные ссылки

| Ресурс | URL |
|--------|-----|
| **Официальная документация** | https://cloud.yandex.ru/docs/speechkit/ |
| **API Reference** | https://cloud.yandex.ru/docs/speechkit/stt/api/request-api |
| **Yandex Cloud Console** | https://console.cloud.yandex.com |
| **Калькулятор стоимости** | https://cloud.yandex.ru/prices#speechkit |
| **GitHub примеры** | https://github.com/yandex-cloud/docs/tree/master/ru/speechkit |

---

## Связанные скиллы

- `whatsapp-парсер` — извлечение аудио из WhatsApp экспортов
- `обработка-запросов-турагентов` — анализ транскрибированного текста
- `vip-dxb-rus-telegram-bot` — Telegram бот для уведомлений
- `туризм-оаэ-автоматизация` — общая автоматизация бизнеса
- `api-туризм-оаэ` — работа с различными API

---

## Расположение ресурсов

```
C:/Users/londo/.claude/skills/yandex-speechkit-туризм/
├── SKILL.md                    # Главный справочник (2000+ слов)
├── README.md                   # Краткое описание
├── references/                 # Детальные модули
│   ├── speechkit-basics.md
│   ├── sync-vs-async.md
│   ├── long-audio-handling.md
│   ├── language-detection.md
│   ├── error-handling.md
│   ├── integrations.md
│   ├── performance-optimization.md
│   ├── troubleshooting.md
│   ├── faq.md                  # 30 вопросов
│   └── cheatsheet.md           # Эта шпаргалка
├── assets/
│   ├── templates/              # 8 шаблонов для копирования
│   └── examples/               # 6 полных примеров
├── scripts/                    # 6 automation скриптов
└── experience/                 # Накопленный опыт
    ├── _index.md               # Критические уроки (топ-5)
    ├── fixes/
    ├── improvements/
    └── patterns/
```

---

**Последнее обновление:** 2026-02-05
**Версия:** 2.0 Extended Edition
**Скилл:** yandex-speechkit-туризм
**Автор:** Сухейль, VIP Dubai Tours
