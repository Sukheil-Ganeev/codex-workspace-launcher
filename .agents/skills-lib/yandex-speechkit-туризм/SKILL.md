---
name: yandex-speechkit-туризм
description: |
  Yandex SpeechKit для туризма ОАЭ — транскрипция голосовых сообщений.

  ТРИГГЕРЫ (активируй при любом из них):
  - "транскрипция", "транскрибировать", "транскрибация"
  - "голосовое", "голосовые сообщения", "voice message"
  - "распознавание речи", "speech-to-text", "STT"
  - "opus", ".ogg", "аудио в текст"
  - "speechkit", "yandex speech"
  - Фаза парсинга с голосовыми (whatsapp-парсер Фаза 2.5)
  - Любое упоминание конвертации аудио/голоса в текст

  API ключ уже настроен в скилле (см. раздел "Переменные окружения").
---

# Yandex SpeechKit для туризма ОАЭ

> **Production-ready справочник по транскрипции голосовых сообщений**

**Версия:** 2.0 Extended Edition
**Дата:** 2026-02-05
**Размер:** 668 KB (49 файлов)
**Автор:** Сухейль, VIP Dubai Tours

---

## 📚 Навигация по справочнику

### Quick Start (начните отсюда!)

**Сценарий A — Простая транскрипция (5 минут):**
```python
# Копируйте и запускайте:
from assets.templates.basic_transcription import transcribe
text = transcribe("voice.ogg", lang="ru-RU")
```
→ См. раздел [Быстрый старт](#быстрый-старт)

**Сценарий B — Длинные аудио >30 сек (10 минут):**
```python
# Автоматически делит на части:
from assets.templates.long_audio_handler import transcribe_any_audio
text = transcribe_any_audio("long_voice.ogg")  # Работает с ЛЮБОЙ длиной!
```
→ См. [Универсальная транскрипция](#-универсальная-транскрипция-рекомендуется)

**Сценарий C — Интеграция с WhatsApp/Telegram (30 минут):**
```bash
# Копируйте готовый пример:
cp -r assets/examples/telegram-bot-integration/ my_bot/
cd my_bot/ && pip install -r requirements.txt
python main.py
```
→ См. `assets/examples/`

### Структура справочника

```
yandex-speechkit-туризм/  (668 KB)
├── SKILL.md            ← Вы здесь (главный справочник)
├── references/         ← 11 детальных модулей
├── assets/
│   ├── templates/      ← 8 шаблонов для копирования
│   └── examples/       ← 6 полных проектов
├── scripts/            ← 6 automation скриптов
└── experience/         ← Накопленный опыт
```

### References (справочные модули)

| Модуль | Размер | Когда читать |
|--------|--------|--------------|
| [speechkit-basics.md](references/speechkit-basics.md) | 16 KB | Основы API, аутентификация, форматы |
| [sync-vs-async.md](references/sync-vs-async.md) | 16 KB | Выбор между Sync/Async/Streaming API |
| [long-audio-handling.md](references/long-audio-handling.md) | 21 KB | **Обработка >30 сек (56% файлов!)** |
| [language-detection.md](references/language-detection.md) | 22 KB | Автоопределение языков (ru/en/ar) |
| [error-handling.md](references/error-handling.md) | 22 KB | Retry logic, fallbacks, мониторинг |
| [integrations.md](references/integrations.md) | 19 KB | WhatsApp, Telegram, Make.com |
| [performance-optimization.md](references/performance-optimization.md) | 20 KB | Batch processing, кеширование |
| [faq.md](references/faq.md) | **26 KB** | **30 вопросов — прочитай первым!** |
| [cheatsheet.md](references/cheatsheet.md) | 17 KB | Быстрый доступ к коду и командам |
| [skill-integrations.md](references/skill-integrations.md) | 26 KB | Связь с 10+ вашими скиллами |

### Templates (готовые шаблоны)

| Файл | Описание |
|------|----------|
| `basic-transcription.py` | Базовая транскрипция (≤30 сек) |
| `long-audio-handler.py` | **Обработка длинных файлов (>30 сек)** |
| `batch-processing.py` | Массовая обработка с progress bar |
| `webhook-handler.py` | Flask webhook для Make.com |
| `telegram-integration.py` | Telegram бот обработчик |
| `whatsapp-parser.py` | Парсинг WhatsApp голосовых |
| `error-handler.py` | Централизованная обработка ошибок |
| `cost-optimizer.py` | Оптимизация затрат |

**Как использовать:**
```bash
cp assets/templates/long-audio-handler.py my_project/
# Замените API ключи в .env и запускайте!
```

### Examples (полные проекты)

| Пример | Технологии |
|--------|------------|
| `whatsapp-voice-transcriber/` | WhatsApp экспорт → транскрипция |
| `telegram-bot-integration/` | Telegram бот с транскрипцией |
| `make-com-webhook/` | Netlify Function для Make.com |
| `batch-audio-processor/` | CLI для массовой обработки |
| `hybrid-speechkit-whisper/` | SpeechKit + Whisper гибрид |
| `multi-language-detector/` | Автодетект языков (ru/en/ar) |

**Каждый пример содержит:** README.md, main.py, requirements.txt, .env.example

### Scripts (автоматизация)

```bash
python scripts/validate-audio.py voice.ogg      # Валидация формата
python scripts/batch-transcribe.py folder/      # Массовая транскрипция
python scripts/cost-calculator.py --duration 120 # Подсчёт стоимости
python scripts/benchmark.py                      # Тестирование моделей
```

---

## 🎯 Топ-10 типичных проблем и решений

### 1. ❌ Файл >30 сек → Ошибка
**Проблема:** 56% WhatsApp голосовых превышают лимит 30 сек.

**Решение:**
```python
# ❌ НЕ ТАК:
text = transcribe_speechkit("long.ogg")  # Упадёт на >30 сек

# ✅ ТАК:
text = transcribe_any_audio("long.ogg")  # Автоматически делит на части
```
→ См. `references/long-audio-handling.md`

### 2. ❌ Неправильный формат аудио
**Проблема:** Указали `format=mp3`, но файл OGG Opus.

**Решение:**
```python
# WhatsApp/Telegram → всегда OGG Opus:
params = {"format": "oggopus", "sampleRateHertz": 48000}
```

### 3. ❌ Ошибка 401 Unauthorized
**Проблема:** Неверный API ключ или Folder ID.

**Решение:**
```bash
echo $YANDEX_CLOUD_API_KEY  # Проверьте наличие
echo $YANDEX_CLOUD_FOLDER_ID
```

### 4. ❌ Плохое качество распознавания
**Проблема:** Неправильный язык или шум в аудио.

**Решение:**
```python
# Используйте автодетект языка:
result = transcribe_auto_detect(audio_path)
# Добавьте пост-коррекцию туристических терминов:
text = correct_tourism_terms(result["text"])
```

### 5. ❌ Ошибка 429 Rate Limit
**Проблема:** Превышен лимит 20 запросов/сек.

**Решение:**
```python
from templates.batch_processing import rate_limited_transcribe
# Автоматический rate limiting
```

### 6. ❌ CORS ошибки в браузере
**Проблема:** Прямой запрос к API из JavaScript.

**Решение:** Используйте Netlify Function как прокси:
```bash
cp assets/examples/make-com-webhook/ netlify/functions/
```

### 7. ❌ Туристические термины неправильно
**Проблема:** "бурч халифа" вместо "Burj Khalifa".

**Решение:**
```python
from templates.basic_transcription import correct_tourism_terms
text = correct_tourism_terms(raw_text)
```

### 8. ❌ Нет обработки ошибок
**Проблема:** Падение при недоступности API.

**Решение:**
```python
from templates.error_handler import transcribe_with_fallback
result = transcribe_with_fallback(audio_path)  # Fallback на Whisper
```

### 9. ❌ Медленная обработка множества файлов
**Проблема:** Последовательная обработка = медленно.

**Решение:**
```python
from templates.batch_processing import parallel_transcribe
results = parallel_transcribe(audio_files, max_workers=5)
```

### 10. ❌ Забыли временные файлы
**Проблема:** Деление на части → забыли удалить chunks.

**Решение:**
```python
try:
    # Обработка
finally:
    for chunk in chunks:
        os.remove(chunk)  # Всегда cleanup!
```

---

## 🚀 Best Practices для туризма ОАЭ

### 1. Всегда используйте универсальную функцию
```python
# ✅ Работает с ЛЮБОЙ длиной:
from templates.long_audio_handler import transcribe_any_audio
text = transcribe_any_audio(audio_path)
```

### 2. Автодетект языка для международных клиентов
```python
# 80% русский, 15% английский, 5% другие
result = transcribe_auto_detect(audio_path)
```

### 3. Batch processing для множества файлов
```bash
python scripts/batch-transcribe.py --input whatsapp_audio/ --output results.json
```

### 4. Кеширование для экономии
```python
# Избегайте повторной транскрипции одного файла:
from templates.cost_optimizer import transcribe_cached
```

### 5. Мониторинг стоимости
```bash
python scripts/cost-calculator.py --duration 3600  # 1 час аудио
# Output: ~36 руб (~$0.38 USD)
```

---

## АВТОАКТИВАЦИЯ

Этот скилл ДОЛЖЕН автоматически активироваться когда:
1. Упоминается "транскрипция" или "транскрибировать"
2. Нужно обработать голосовые сообщения (.opus, .ogg)
3. Речь идёт о Фазе 2.5 парсинга WhatsApp
4. Упоминается "speechkit", "speech-to-text", "STT"
5. Нужно конвертировать аудио в текст

## Когда использовать

- Голосовые сообщения от клиентов из СНГ (русский язык)
- Нужна быстрая транскрипция (streaming)
- Важно качество распознавания русского
- WhatsApp/Telegram голосовые (.opus формат)
- Любая задача "аудио -> текст" для русского языка

---

## Конфигурация

### Получение API-ключа в Yandex Cloud

1. Нажми на сервисный аккаунт `speechkit-bot`
2. Сверху нажми **"Создать новый ключ"**
3. Выбери **"Создать API-ключ"**
4. В форме:
   - **Описание:** `для транскрипции`
   - **Область действия:** выбери нужное разрешение:
     - `yc.ai.speechkitStt.execute` — для распознавания речи (STT)
     - `yc.ai.speechkitTts.execute` — для синтеза речи (TTS)
   - **Срок действия:** можно оставить пустым (бессрочный)
5. Нажми **"Создать"**
6. **ВАЖНО:** Скопируй секретный ключ — он показывается только один раз!

> **Примечание:** "Область действия" при создании ключа — это выбор разрешений (какие API может вызывать ключ), а не выбор каталога. Каталог (Folder ID) указывается отдельно в параметрах API-запросов.

### Переменные окружения

```bash
# В .env файле
YANDEX_CLOUD_API_KEY=ваш_api_ключ
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f
```

### Python конфигурация

```python
import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER_ID = os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")
```

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО: Лимит 30 секунд

**Yandex SpeechKit Sync API имеет жёсткий лимит 30 секунд.**

**Реальная статистика** (из практики):
- В WhatsApp чатах туристического бизнеса **56% голосовых >30 сек**
- Диапазон: 30.3 - 138.88 сек (до 4.6× превышение лимита)
- Без обработки длинных файлов = **56% потери данных**

📖 **См. опыт:** `experience/_index.md` → топ-5 критических уроков

---

## Быстрый старт

### Установка

```bash
pip install requests python-dotenv
```

### Базовая транскрипция (≤30 сек)

```python
import requests
import os

def transcribe_speechkit(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Транскрипция аудио через Yandex SpeechKit.

    Args:
        audio_path: Путь к аудиофайлу (ogg opus, mp3, wav)
        lang: Язык распознавания (ru-RU, en-US, tr-TR)

    Returns:
        str: Распознанный текст
    """
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": lang,
            "format": "oggopus",  # или lpcm, mp3
            "sampleRateHertz": 48000
        },
        headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        },
        data=open(audio_path, "rb")
    )

    if response.status_code == 200:
        return response.json().get("result", "")
    else:
        raise Exception(f"SpeechKit error: {response.status_code} - {response.text}")
```

### Транскрипция с определением языка

```python
def transcribe_auto_detect(audio_path: str) -> dict:
    """
    Транскрипция с автоопределением языка.
    Пробует русский, английский, арабский.
    """
    languages = ["ru-RU", "en-US", "ar-AE"]
    results = []

    for lang in languages:
        try:
            text = transcribe_speechkit(audio_path, lang)
            if text.strip():
                results.append({
                    "language": lang,
                    "text": text,
                    "confidence": estimate_confidence(text, lang)
                })
        except Exception:
            continue

    # Выбираем лучший результат
    if results:
        best = max(results, key=lambda x: x["confidence"])
        return best

    return {"language": "unknown", "text": "", "confidence": 0}


def estimate_confidence(text: str, lang: str) -> float:
    """Эвристическая оценка качества распознавания."""
    if not text:
        return 0

    # Больше слов = выше уверенность
    word_count = len(text.split())
    base_score = min(word_count / 10, 0.8)

    # Проверка на типичные ошибки
    error_markers = ["[неразборчиво]", "???", "..."]
    for marker in error_markers:
        if marker in text:
            base_score *= 0.7

    return round(base_score, 2)
```

---

## 🎯 Универсальная транскрипция (РЕКОМЕНДУЕТСЯ)

**Для WhatsApp/Telegram голосовых используй этот подход — обрабатывает файлы ЛЮБОЙ длины.**

```python
import subprocess
import math
import requests
import os

def transcribe_any_audio(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Универсальная транскрипция — обрабатывает файлы ЛЮБОЙ длины.

    Автоматически:
    - Короткие (≤29 сек) → прямая транскрипция
    - Длинные (>29 сек) → деление на части + склеивание

    Args:
        audio_path: Путь к аудиофайлу (.ogg, .opus, .mp3)
        lang: Язык (ru-RU, en-US, tr-TR)

    Returns:
        str: Полный текст транскрипции
    """
    duration = get_audio_duration(audio_path)

    # Порог 29 сек (не 30!) — запас на погрешности
    if duration <= 29.0:
        # Короткое — прямая обработка
        return transcribe_direct(audio_path, lang)
    else:
        # Длинное — делим на части
        return transcribe_with_splitting(audio_path, lang)


def get_audio_duration(audio_path: str) -> float:
    """Получить длительность через ffprobe."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def transcribe_with_splitting(audio_path: str, lang: str) -> str:
    """
    Обработка длинных аудио (>29 сек).

    Алгоритм:
    1. Делит на части по 29 сек (без перекодирования!)
    2. Транскрибирует каждую часть
    3. Склеивает текст
    4. Удаляет временные файлы
    """
    duration = get_audio_duration(audio_path)
    num_chunks = math.ceil(duration / 29.0)
    chunks = []

    try:
        # Делим на части
        for i in range(num_chunks):
            chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
            start_time = i * 29

            # КРИТИЧНО: -c copy (без перекодирования, в 10-50× быстрее)
            subprocess.run([
                'ffmpeg', '-i', audio_path,
                '-ss', str(start_time),
                '-t', '29',
                '-c', 'copy',  # Без перекодирования!
                chunk_path, '-y'
            ], capture_output=True, check=True)

            chunks.append(chunk_path)

        # Транскрибируем каждую часть
        transcripts = []
        for chunk in chunks:
            text = transcribe_direct(chunk, lang)
            if text.strip():
                transcripts.append(text)

        # Склеиваем
        return " ".join(transcripts)

    finally:
        # Cleanup — всегда удаляем временные файлы
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)


def transcribe_direct(audio_path: str, lang: str = "ru-RU") -> str:
    """Прямая транскрипция через Sync API (для файлов ≤29 сек)."""
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

    if response.status_code == 200:
        return response.json().get("result", "")
    else:
        raise Exception(f"SpeechKit error: {response.status_code} - {response.text}")
```

**Использование:**

```python
# Работает с файлами ЛЮБОЙ длины (от 1 сек до 2+ минут)
text = transcribe_any_audio("D:/audio/long_voice_message.ogg")
print(text)
```

**Результаты из практики:**
- Было: 12/27 файлов (44%), 15 пропущено
- Стало: 27/27 файлов (100%), 0 пропущено
- Улучшение: +127% эффективности

---

## Streaming API (Async для очень длинных)

Для **очень** длинных аудио (>3 минуты) можно использовать асинхронное распознавание.

**НО:** Для WhatsApp/Telegram голосовых (обычно <2 мин) универсальный подход выше быстрее и проще.

```python
import requests
import time

def transcribe_long_audio(audio_url: str) -> str:
    """
    Асинхронная транскрипция длинного аудио.

    Args:
        audio_url: URL аудиофайла (S3, Cloud Storage)

    Returns:
        str: Полный текст транскрипции
    """
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    folder_id = os.getenv("YANDEX_CLOUD_FOLDER_ID")

    # 1. Запуск задачи распознавания
    response = requests.post(
        "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize",
        headers={
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "config": {
                "specification": {
                    "languageCode": "ru-RU",
                    "model": "general",
                    "profanityFilter": False,
                    "audioEncoding": "OGG_OPUS",
                    "sampleRateHertz": 48000
                },
                "folderId": folder_id
            },
            "audio": {
                "uri": audio_url
            }
        }
    )

    if response.status_code != 200:
        raise Exception(f"Failed to start: {response.text}")

    operation_id = response.json()["id"]

    # 2. Ожидание результата
    for _ in range(60):  # Max 5 минут
        status = requests.get(
            f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
            headers={"Authorization": f"Api-Key {api_key}"}
        ).json()

        if status.get("done"):
            chunks = status.get("response", {}).get("chunks", [])
            return " ".join(
                alt.get("text", "")
                for chunk in chunks
                for alt in chunk.get("alternatives", [])[:1]
            )

        time.sleep(5)

    raise Exception("Transcription timeout")
```

---

## Интеграция с make.com

### Webhook для голосовых сообщений

```json
{
  "name": "SpeechKit Transcription",
  "modules": [
    {
      "name": "Download Audio",
      "type": "http.download",
      "config": {
        "url": "{{input.media_url}}"
      }
    },
    {
      "name": "Upload to Yandex Storage",
      "type": "http.upload",
      "config": {
        "url": "https://storage.yandexcloud.net/bucket/{{filename}}",
        "headers": {
          "Authorization": "AWS {{env.YANDEX_S3_KEY}}:{{env.YANDEX_S3_SECRET}}"
        }
      }
    },
    {
      "name": "SpeechKit Recognize",
      "type": "http.request",
      "config": {
        "url": "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        "method": "POST",
        "headers": {
          "Authorization": "Api-Key {{env.YANDEX_CLOUD_API_KEY}}"
        },
        "qs": {
          "folderId": "{{env.YANDEX_CLOUD_FOLDER_ID}}",
          "lang": "ru-RU",
          "format": "oggopus"
        },
        "body": "{{1.data}}"
      }
    },
    {
      "name": "Return Result",
      "type": "response",
      "config": {
        "body": {
          "text": "{{3.result}}",
          "source": "speechkit"
        }
      }
    }
  ]
}
```

---

## Сравнение с Whisper

| Параметр | SpeechKit | Whisper API |
|----------|-----------|-------------|
| Русский язык | Отлично | Очень хорошо |
| Английский | Очень хорошо | Отлично |
| Арабский | Хорошо | Очень хорошо |
| Streaming | Да | Нет |
| Max длина | Неограничено | 25 МБ |
| Стоимость | ~$0.01/мин | $0.006/мин |
| Latency | < 1 сек | 3-5 сек |
| Туристические термины (русские) | Отлично | Хорошо |

### Когда использовать SpeechKit

- Клиент говорит на русском языке
- Нужен streaming (real-time)
- Голосовые > 1 минуты
- Важна скорость отклика

### Когда использовать Whisper

- Клиент говорит на английском/арабском
- Нужен мультиязычный контекст
- Важна экономия

---

## Гибридный подход

```python
def transcribe_hybrid(audio_path: str, client_language: str = None) -> dict:
    """
    Гибридная транскрипция: выбор API по языку.

    Args:
        audio_path: Путь к аудио
        client_language: Язык клиента (ru, en, ar) или None для автодетекта

    Returns:
        dict: {text, source, language}
    """
    # Определяем язык
    if client_language is None:
        # Можно определить по профилю клиента в CRM
        client_language = "ru"  # default для СНГ

    # Выбор API
    if client_language in ["ru", "kz", "by", "ua"]:
        # Yandex SpeechKit для русскоязычных
        text = transcribe_speechkit(audio_path, "ru-RU")
        return {
            "text": text,
            "source": "speechkit",
            "language": "ru-RU"
        }
    else:
        # Whisper для остальных
        text = transcribe_whisper(audio_path, client_language)
        return {
            "text": text,
            "source": "whisper",
            "language": client_language
        }


def transcribe_whisper(audio_path: str, language: str = "en") -> str:
    """Whisper API транскрипция (из скилла туризм-оаэ-автоматизация)."""
    import openai

    client = openai.OpenAI()

    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language=language
        )

    return transcript.text
```

---

## Туристический контекст

### Словарь для улучшения распознавания

При использовании SpeechKit можно подать hints для улучшения распознавания:

```python
TOURISM_HINTS = [
    # Локации
    "Дубай", "Абу-Даби", "Шарджа", "Аджман", "Рас-эль-Хайма",
    "Бурдж Халифа", "Пальма Джумейра", "Марина", "Даунтаун",

    # Достопримечательности
    "Феррари Ворлд", "Аквавенчер", "Атлантис", "Дубай Молл",
    "Голд Сук", "Спайс Сук", "Глобал Вилладж",

    # Услуги
    "сафари", "трансфер", "экскурсия", "яхта", "виза",
    "фотосессия", "квадроцикл", "багги", "верблюд",

    # Деньги
    "дирхам", "доллар", "рубль", "тенге", "USDT",

    # Время
    "пикап", "дропофф", "утренний", "вечерний"
]

def transcribe_with_hints(audio_path: str) -> str:
    """Транскрипция с туристическими подсказками."""
    # Примечание: SpeechKit не поддерживает hints напрямую,
    # но можно использовать пост-обработку для коррекции

    text = transcribe_speechkit(audio_path)
    text = correct_tourism_terms(text)

    return text


def correct_tourism_terms(text: str) -> str:
    """Пост-коррекция туристических терминов."""
    corrections = {
        "бурч халифа": "Бурдж Халифа",
        "бурж халифа": "Бурдж Халифа",
        "феррари ворлд": "Ferrari World",
        "дубай молл": "Dubai Mall",
        "абудаби": "Абу-Даби",
        "дубаи": "Дубай",
        "саффари": "сафари",
        "дирхамы": "дирхамов"
    }

    result = text.lower()
    for wrong, correct in corrections.items():
        result = result.replace(wrong, correct)

    return result
```

---

## Обработка ошибок

```python
class SpeechKitError(Exception):
    pass

def transcribe_safe(audio_path: str) -> dict:
    """Безопасная транскрипция с обработкой ошибок."""
    try:
        text = transcribe_speechkit(audio_path)
        return {
            "success": True,
            "text": text,
            "source": "speechkit"
        }
    except requests.exceptions.Timeout:
        # Fallback на Whisper
        try:
            text = transcribe_whisper(audio_path)
            return {
                "success": True,
                "text": text,
                "source": "whisper_fallback"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Both APIs failed: {str(e)}",
                "text": ""
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "text": ""
        }
```

---

## Переменные окружения

Добавить в `.env`:

```bash
# === YANDEX CLOUD ===

# SpeechKit (распознавание речи)
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE

# Folder ID
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f

# Опционально: Yandex Object Storage (для длинных аудио)
YANDEX_S3_KEY=...
YANDEX_S3_SECRET=...
YANDEX_S3_BUCKET=tourism-audio
```

---

## Мониторинг и стоимость

### Стоимость

| Операция | Цена |
|----------|------|
| Распознавание (синхронное) | 0.80 руб / 15 сек |
| Распознавание (асинхронное) | 0.48 руб / 15 сек |
| Streaming | 0.96 руб / 15 сек |

Примерно: **~0.01 USD за минуту** аудио.

### Лимиты

| Параметр | Значение |
|----------|----------|
| Max размер (синхронный) | 1 МБ |
| Max длина (синхронный) | 30 сек |
| Max длина (асинхронный) | 4 часа |
| Rate limit | 20 RPS |

---

## Документация

- Полное руководство по настройке: `D:/Downloads/Идеи-туризм-автоматизация/YANDEX_SPEECHKIT_SETUP.md`
- Официальная документация: https://cloud.yandex.ru/docs/speechkit/
- API Reference: https://cloud.yandex.ru/docs/speechkit/stt/api/request-api
- Примеры кода: https://github.com/yandex-cloud/docs/tree/master/ru/speechkit

---

## Альтернативные методы

Текущее решение использует Yandex SpeechKit. Вот альтернативы на случай если нужно:

| Метод | Когда использовать | Плюсы | Минусы |
|-------|-------------------|-------|--------|
| **Yandex SpeechKit** | Русский язык (основной) | Лучшее качество для русского, streaming | Платный (~$0.01/мин) |
| **Whisper API (OpenAI)** | Английский/арабский | Отличное качество, мультиязычность | Платный ($0.006/мин) |
| **Whisper локально** | Большие объёмы, экономия | Бесплатно | Нужен GPU, медленнее |
| **faster-whisper** | Оптимизированный Whisper | Бесплатно, быстрее Whisper | Нужен GPU |
| **Google Speech-to-Text** | Альтернатива облачная | Хорошее качество | Сложнее настройка |
| **Vosk** | Офлайн, легковесный | Бесплатно, работает на CPU | Хуже качество |

### Когда переключиться на альтернативу:

| Ситуация | Рекомендация |
|----------|--------------|
| Клиент говорит по-английски | Whisper API |
| Бюджет ограничен | Whisper локально или Vosk |
| Большие объёмы (>1000 мин/день) | faster-whisper на GPU |
| Нет интернета | Vosk или Whisper локально |
| Нужен real-time | SpeechKit streaming |

### Установка альтернатив:

```bash
# Whisper локально
pip install openai-whisper

# faster-whisper (оптимизированный)
pip install faster-whisper

# Vosk (офлайн, легковесный)
pip install vosk
```

### Пример Whisper локально:

```python
import whisper

def transcribe_whisper_local(audio_path: str) -> str:
    """Бесплатная локальная транскрипция через Whisper."""
    model = whisper.load_model("medium")  # или "small", "large"
    result = model.transcribe(audio_path, language="ru")
    return result["text"]
```

### Пример faster-whisper:

```python
from faster_whisper import WhisperModel

def transcribe_faster(audio_path: str) -> str:
    """Оптимизированный Whisper (в 4 раза быстрее)."""
    model = WhisperModel("medium", device="cuda")  # или "cpu"
    segments, _ = model.transcribe(audio_path, language="ru")
    return " ".join(s.text for s in segments)
```

**Подробнее об альтернативах:** `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_МЕДИА.md`

---

## Связанные скиллы

| Скилл | Связь |
|-------|-------|
| **ocr-туризм** | OCR для туризма ОАЭ — распознавание текста на изображениях (чеки, паспорта) |
| **туризм-оаэ-автоматизация** | Основной скилл, использует Whisper + SpeechKit |
| **whatsapp-парсер** | Источник голосовых сообщений |
| **обработка-запросов-турагентов** | Обработка транскрибированных запросов |

---

## Дополнительные ресурсы

| Ресурс | Описание |
|--------|----------|
| [references/faq.md](references/faq.md) | Часто задаваемые вопросы |
| [references/troubleshooting.md](references/troubleshooting.md) | Решение проблем и ошибок |
| [references/cheatsheet.md](references/cheatsheet.md) | Шпаргалка для быстрой работы |
