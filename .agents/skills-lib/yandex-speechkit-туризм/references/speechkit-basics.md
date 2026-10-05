# SpeechKit Basics — Основы работы с Yandex SpeechKit

> Базовые концепции, endpoints, аутентификация, форматы аудио

---

## API Endpoints

Yandex SpeechKit предоставляет 3 основных способа распознавания речи:

### 1. Synchronous Recognition (Sync API)

**Endpoint:**
```
POST https://stt.api.cloud.yandex.net/speech/v1/stt:recognize
```

**Назначение:** Быстрое распознавание коротких аудио

**Лимиты:**
- Максимальная длина: **30 секунд**
- Максимальный размер: **1 МБ**
- Latency: **< 1 секунда**

**Когда использовать:**
- WhatsApp/Telegram голосовые сообщения ≤29 сек
- Нужен немедленный результат
- Простая интеграция

**Пример:**
```python
import requests
import os

response = requests.post(
    "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
    params={
        "folderId": "b1gvu3q8k1kafqd3sk5f",
        "lang": "ru-RU",
        "format": "oggopus",
        "sampleRateHertz": 48000
    },
    headers={
        "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
    },
    data=open("audio.ogg", "rb")
)

text = response.json().get("result", "")
```

---

### 2. Asynchronous Recognition (Async API)

**Endpoint:**
```
POST https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize
```

**Назначение:** Обработка длинных аудиозаписей

**Лимиты:**
- Максимальная длина: **4 часа**
- Файл должен быть в Cloud Storage (S3/Yandex Object Storage)
- Время обработки: 5-10 минут для 1 часа аудио

**Когда использовать:**
- Длинные записи (>30 сек до 4 часов)
- Не критична скорость (можно подождать)
- Нужны timestamps (начало/конец каждого слова)
- Нужен профанити-фильтр или другие продвинутые настройки

**Пример:**
```python
import requests
import time

# 1. Запуск распознавания
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
                "audioEncoding": "OGG_OPUS"
            },
            "folderId": "b1gvu3q8k1kafqd3sk5f"
        },
        "audio": {
            "uri": "https://storage.yandexcloud.net/bucket/audio.ogg"
        }
    }
)

operation_id = response.json()["id"]

# 2. Ожидание результата
while True:
    status = requests.get(
        f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
        headers={"Authorization": f"Api-Key {api_key}"}
    ).json()

    if status.get("done"):
        chunks = status["response"]["chunks"]
        text = " ".join(
            alt["text"]
            for chunk in chunks
            for alt in chunk["alternatives"][:1]
        )
        break

    time.sleep(5)
```

---

### 3. Streaming Recognition (WebSocket)

**Endpoint:**
```
wss://stt.api.cloud.yandex.net/speech/v1/stt:streamingRecognize
```

**Назначение:** Real-time распознавание потокового аудио

**Когда использовать:**
- Телефонные звонки
- Живые трансляции
- Voice assistant
- Интерактивные приложения

**НЕ нужен для:** WhatsApp/Telegram голосовых (используй Sync или деление на части)

---

## Аутентификация

Yandex Cloud поддерживает 3 способа аутентификации:

### 1. API Key (Рекомендуется для туризма)

**Как получить:**
1. Консоль Yandex Cloud → IAM → Сервисные аккаунты
2. Выбери `speechkit-bot`
3. "Создать новый ключ" → "API-ключ"
4. Scope: `yc.ai.speechkitStt.execute`

**Использование:**
```python
headers = {
    "Authorization": f"Api-Key {YANDEX_CLOUD_API_KEY}"
}
```

**Плюсы:**
- Простота
- Бессрочный (не нужно обновлять)
- Идеален для скриптов/webhook

**Минусы:**
- Меньше контроля (не можем отозвать для конкретного запроса)

**Хранение:**
```bash
# .env
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f
```

---

### 2. IAM Token

**Как получить:**
```bash
# Через Yandex CLI
yc iam create-token
```

**Использование:**
```python
headers = {
    "Authorization": f"Bearer {IAM_TOKEN}"
}
```

**Плюсы:**
- Больше контроля
- Можно отозвать

**Минусы:**
- Живет **12 часов** (нужно обновлять!)
- Сложнее для автоматизации

**Когда использовать:** Production приложения с долгоживущими процессами

---

### 3. Service Account Key (для серверных приложений)

**Использование:** OAuth 2.0 для обмена ключа на IAM токен

**Когда использовать:** Сложные enterprise решения

---

## Форматы аудио

SpeechKit поддерживает популярные форматы:

### Поддерживаемые форматы

| Формат | Параметр `format` | Типичное использование |
|--------|------------------|------------------------|
| **OGG Opus** | `oggopus` | WhatsApp, Telegram голосовые |
| **LPCM** | `lpcm` | Сырое аудио (WAV без заголовка) |
| **MP3** | `mp3` | Общее аудио |

---

### OGG Opus (WhatsApp/Telegram)

**Параметры:**
```python
params = {
    "format": "oggopus",
    "sampleRateHertz": 48000  # 48 kHz для Opus
}
```

**Факты:**
- WhatsApp сохраняет голосовые как `.opus` (контейнер OGG)
- Telegram аналогично
- Высокое сжатие (экономит трафик)

---

### LPCM (Linear PCM)

**Параметры:**
```python
params = {
    "format": "lpcm",
    "sampleRateHertz": 8000  # или 16000, 48000
}
```

**Когда использовать:**
- Конвертировал WAV в RAW
- Телефония (часто 8 kHz)
- Нужен точный контроль над качеством

**Пример конвертации:**
```bash
# WAV → LPCM
ffmpeg -i audio.wav -f s16le -ar 16000 -ac 1 audio.raw
```

---

### MP3

**Параметры:**
```python
params = {
    "format": "mp3",
    # sampleRateHertz не требуется (берется из файла)
}
```

**Когда использовать:**
- Общие аудиозаписи
- Скачанные файлы из интернета

---

## Языки

SpeechKit поддерживает 17+ языков, но для туризма ОАЭ важны:

### Основные языки

| Язык | Код | Когда использовать |
|------|-----|-------------------|
| **Русский** | `ru-RU` | Клиенты из СНГ (основной!) |
| **Английский** | `en-US` | Международные туристы |
| **Арабский** | `ar-AE` | Местные жители, официальные документы |
| **Турецкий** | `tr-TR` | Турецкие туристы |
| **Казахский** | `kk-KZ` | Клиенты из Казахстана |

### Автоопределение языка

SpeechKit **НЕ** определяет язык автоматически. Нужно указывать вручную.

**Решение:** Попробовать несколько языков и выбрать лучший результат:

```python
def transcribe_auto_detect(audio_path):
    languages = ["ru-RU", "en-US", "ar-AE"]
    results = []

    for lang in languages:
        try:
            text = transcribe(audio_path, lang)
            confidence = estimate_confidence(text)
            results.append({"lang": lang, "text": text, "confidence": confidence})
        except:
            continue

    # Выбираем результат с максимальной уверенностью
    best = max(results, key=lambda x: x["confidence"])
    return best
```

**Эвристики определения качества:**
- Длина текста (больше слов = лучше)
- Отсутствие ошибок типа `[неразборчиво]`
- Словарный анализ (проверка типичных слов языка)

📖 **Подробнее:** `references/language-detection.md`

---

## Модели распознавания

SpeechKit предлагает специализированные модели:

### Доступные модели

| Модель | Параметр `model` | Назначение |
|--------|-----------------|------------|
| **General** | `general` | Общая речь (по умолчанию) |
| **Numbers** | `numbers` | Числа, телефоны, суммы |
| **Dates** | `dates` | Даты и время |
| **Names** | `names` | Имена и фамилии |
| **Phone** | `phone` | Телефонные звонки |

### Использование моделей

**В Sync API:**
```python
# Модель указывается через параметр "topic"
params = {
    "folderId": "b1gvu3q8k1kafqd3sk5f",
    "lang": "ru-RU",
    "topic": "general",  # или numbers, dates, names
    "format": "oggopus"
}
```

**В Async API:**
```json
{
  "config": {
    "specification": {
      "model": "general"
    }
  }
}
```

### Рекомендации для туризма

| Контекст | Модель | Причина |
|----------|--------|---------|
| Общие запросы | `general` | Универсальная |
| Бронирование с суммами | `numbers` | Лучше распознает "450 дирхамов" |
| Даты заезда | `dates` | Лучше распознает "15 марта" |
| Имена туристов | `names` | Меньше ошибок в именах |

---

## Дополнительные параметры

### profanityFilter (цензура)

```python
# Только в Async API
"specification": {
    "profanityFilter": True  # Заменяет мат на ***
}
```

**Для туризма:** Можно оставить `False` (клиенты иногда ругаются при задержках)

---

### rawResults (необработанные результаты)

```python
# Sync API
params = {
    "rawResults": True
}
```

**Что дает:** Возвращает несколько альтернативных вариантов распознавания

**Когда использовать:** Если нужно выбрать лучший вариант вручную или по алгоритму

---

## Практические примеры

### Базовая транскрипция (туристический контекст)

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def transcribe_tourist_message(audio_path: str) -> str:
    """
    Транскрипция голосового от клиента.
    Предполагается русский язык, общая модель.
    """
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": "ru-RU",
            "topic": "general",
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

---

### Транскрипция с выбором модели

```python
def transcribe_with_context(audio_path: str, context: str = "general") -> str:
    """
    Транскрипция с учетом контекста запроса.

    Args:
        audio_path: Путь к аудио
        context: "general", "booking", "dates", "names"
    """
    # Выбираем модель по контексту
    model_map = {
        "general": "general",
        "booking": "numbers",  # В брони часто суммы
        "dates": "dates",
        "names": "names"
    }

    topic = model_map.get(context, "general")

    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": "ru-RU",
            "topic": topic,
            "format": "oggopus",
            "sampleRateHertz": 48000
        },
        headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        },
        data=open(audio_path, "rb")
    )

    if response.ok:
        return response.json().get("result", "")
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
```

---

## Стоимость

### Цены (актуально на 2025)

| Тип распознавания | Цена |
|------------------|------|
| Синхронное | 0.80 руб / 15 сек |
| Асинхронное | 0.48 руб / 15 сек |
| Streaming | 0.96 руб / 15 сек |

**Примерно:** ~0.01 USD за минуту аудио

### Оптимизация затрат

1. **Используй Sync API когда возможно** (самый дешевый для коротких аудио)
2. **Деление на части** вместо Async API (если файл 1-2 минуты)
3. **Кеширование результатов** (если один файл обрабатывается несколько раз)

---

## Rate Limits

| Параметр | Значение |
|----------|----------|
| Запросов в секунду (RPS) | 20 |
| Одновременных соединений | 10 |

**Если превышен лимит:** 429 Too Many Requests

**Решение:** Exponential backoff (см. `references/error-handling.md`)

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/sync-vs-async.md` | Выбор между Sync и Async API |
| `references/long-audio-handling.md` | Обработка файлов >30 сек |
| `references/language-detection.md` | Автоопределение языка |
| `references/error-handling.md` | Обработка ошибок и retry |

---

## Официальная документация

- API Reference: https://cloud.yandex.ru/docs/speechkit/stt/api/request-api
- Форматы аудио: https://cloud.yandex.ru/docs/speechkit/formats
- Список языков: https://cloud.yandex.ru/docs/speechkit/stt/models#languages
- Модели: https://cloud.yandex.ru/docs/speechkit/stt/models
