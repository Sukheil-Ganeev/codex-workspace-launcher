# Sync vs Async — Выбор между синхронным и асинхронным API

> Сравнение трех способов распознавания речи в Yandex SpeechKit

---

## Три способа распознавания

Yandex SpeechKit предлагает три API для разных сценариев:

| API | Макс. длина | Латентность | Сложность интеграции | Стоимость |
|-----|-------------|-------------|---------------------|-----------|
| **Sync** | 30 сек | < 1 сек | Простая | 0.80₽ / 15 сек |
| **Async** | 4 часа | 5-10 мин | Средняя | 0.48₽ / 15 сек |
| **Streaming** | Неограничено | Real-time | Сложная | 0.96₽ / 15 сек |

---

## Synchronous API (Sync)

### Характеристики

**Endpoint:**
```
POST https://stt.api.cloud.yandex.net/speech/v1/stt:recognize
```

**Ограничения:**
- Максимальная длительность: 30 секунд
- Максимальный размер: 1 МБ
- Латентность: < 1 секунда

**Преимущества:**
- Простейшая интеграция (один HTTP запрос)
- Мгновенный результат
- Не нужно настраивать Cloud Storage
- Идеален для webhook

**Недостатки:**
- Лимит 30 секунд (жесткий!)
- Нет timestamps (только текст)
- Нет продвинутых фич (profanity filter, speaker diarization)

### Когда использовать Sync API

**Идеальные сценарии:**
1. WhatsApp/Telegram голосовые ≤29 секунд (большинство случаев)
2. Webhook обработка (Make.com, n8n)
3. Прототипирование и тестирование
4. Простые скрипты

**Пример:**
```python
import requests
import os

def transcribe_sync(audio_path: str) -> str:
    """Быстрая транскрипция короткого аудио."""
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": "ru-RU",
            "format": "oggopus",
            "sampleRateHertz": 48000
        },
        headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        },
        data=open(audio_path, "rb")
    )

    return response.json().get("result", "")
```

---

## Asynchronous API (Async)

### Характеристики

**Endpoint:**
```
POST https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize
```

**Ограничения:**
- Максимальная длительность: 4 часа
- Файл должен быть доступен по URL (S3/Cloud Storage)
- Время обработки: ~5-10 минут на 1 час аудио

**Преимущества:**
- Длинные аудио (до 4 часов!)
- Timestamps для каждого слова
- Профанити-фильтр
- Выбор моделей (general, numbers, dates, names)
- Дешевле (0.48₽ vs 0.80₽)

**Недостатки:**
- Нужно загрузить файл в Cloud Storage
- Асинхронность (polling статуса)
- Сложнее интеграция
- Латентность 5-10 минут

### Когда использовать Async API

**Идеальные сценарии:**
1. Длинные записи (>30 сек до 4 часов)
2. Batch обработка больших объемов
3. Нужны timestamps (субтитры, анализ)
4. Важна стоимость (дешевле на 40%)
5. Нужен profanity filter

**НЕ использовать для:** WhatsApp/Telegram голосовых 1-2 минуты (лучше деление на части через Sync)

### Пример Async API

```python
import requests
import time
import os

def transcribe_async(audio_url: str) -> str:
    """
    Асинхронная транскрипция длинного аудио.

    Args:
        audio_url: URL файла в Yandex Object Storage или S3

    Returns:
        str: Распознанный текст
    """
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    folder_id = os.getenv("YANDEX_CLOUD_FOLDER_ID")

    # 1. Запуск задачи
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

    # 2. Polling статуса (до 5 минут)
    for _ in range(60):
        status = requests.get(
            f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
            headers={"Authorization": f"Api-Key {api_key}"}
        ).json()

        if status.get("done"):
            # Извлекаем текст из chunks
            chunks = status.get("response", {}).get("chunks", [])
            text = " ".join(
                alt["text"]
                for chunk in chunks
                for alt in chunk.get("alternatives", [])[:1]
            )
            return text

        time.sleep(5)

    raise Exception("Transcription timeout (5 minutes)")
```

### Загрузка файла в Cloud Storage

```python
import boto3

def upload_to_storage(local_path: str) -> str:
    """Загрузка аудио в Yandex Object Storage."""
    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv("YANDEX_S3_KEY"),
        aws_secret_access_key=os.getenv("YANDEX_S3_SECRET")
    )

    bucket = "tourism-audio"
    filename = os.path.basename(local_path)

    s3.upload_file(local_path, bucket, filename)

    return f"https://storage.yandexcloud.net/{bucket}/{filename}"
```

---

## Streaming API (WebSocket)

### Характеристики

**Endpoint:**
```
wss://stt.api.cloud.yandex.net/speech/v1/stt:streamingRecognize
```

**Особенности:**
- Real-time распознавание
- Результаты по мере поступления аудио
- WebSocket протокол
- Самый дорогой (0.96₽ / 15 сек)

### Когда использовать Streaming API

**Идеальные сценарии:**
1. Телефонные звонки (call center)
2. Живые трансляции
3. Voice assistants (Алиса-подобные)
4. Интерактивные приложения

**НЕ использовать для:** WhatsApp/Telegram голосовых (оверкилл)

### Пример Streaming API

```python
import asyncio
import websockets
import json

async def transcribe_streaming(audio_stream):
    """Real-time транскрипция через WebSocket."""
    uri = "wss://stt.api.cloud.yandex.net/speech/v1/stt:streamingRecognize"

    async with websockets.connect(
        uri,
        extra_headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        }
    ) as ws:
        # Отправка конфигурации
        await ws.send(json.dumps({
            "config": {
                "specification": {
                    "languageCode": "ru-RU",
                    "model": "general",
                    "audioEncoding": "LINEAR16_PCM",
                    "sampleRateHertz": 8000
                }
            }
        }))

        # Отправка аудио чанками
        for chunk in audio_stream:
            await ws.send(chunk)

        # Получение результатов
        async for message in ws:
            result = json.loads(message)
            if result.get("final"):
                return result["alternatives"][0]["text"]
```

---

## Таблица принятия решений

### По длине аудио

| Длина | Рекомендация | Обоснование |
|-------|--------------|-------------|
| **≤29 сек** | Sync API | Быстро, просто, достаточно |
| **30-120 сек** | Деление + Sync | Быстрее чем Async (1 сек vs 5 мин) |
| **2-10 мин** | Async API | Деление на 20+ частей неудобно |
| **>10 мин** | Async API | Единственный вариант |
| **Real-time** | Streaming | По определению |

### По типу приложения

| Тип приложения | Рекомендация |
|----------------|--------------|
| WhatsApp бот | Sync + деление на части |
| Telegram бот | Sync + деление на части |
| Make.com webhook | Sync API |
| Batch обработка | Async API |
| Call center | Streaming API |
| Voice assistant | Streaming API |

### По требованиям к фичам

| Требование | Sync | Async | Streaming |
|------------|------|-------|-----------|
| Мгновенный результат | ✅ | ❌ | ✅ |
| Длинное аудио (>30 сек) | ❌ | ✅ | ✅ |
| Timestamps | ❌ | ✅ | ❌ |
| Профанити-фильтр | ❌ | ✅ | ❌ |
| Простота интеграции | ✅ | ❌ | ❌ |
| Низкая стоимость | ⚠️ | ✅ | ❌ |

---

## Практика: туристический бизнес ОАЭ

### Статистика голосовых сообщений

Из анализа реальных WhatsApp чатов:
- **44% голосовых ≤29 сек** → Sync API
- **56% голосовых >30 сек** (до 138 сек) → Нужно решение

**Проблема:** Sync не подходит для 56% файлов!

### Решения для длинных голосовых

#### Вариант 1: Деление на части (Рекомендуется)

**Плюсы:**
- Быстро (1-2 секунды на весь файл)
- Не нужен Cloud Storage
- Простая интеграция

**Минусы:**
- Может обрезаться слово на стыке частей
- Нужен ffmpeg

**Реализация:**
```python
import subprocess
import math

def transcribe_long_sync(audio_path: str) -> str:
    """
    Обработка длинных аудио через деление на части.
    Работает для файлов любой длины.
    """
    duration = get_audio_duration(audio_path)

    # Короткие файлы — прямая обработка
    if duration <= 29.0:
        return transcribe_sync(audio_path)

    # Длинные — делим на части по 29 сек
    num_chunks = math.ceil(duration / 29.0)
    chunks = []

    try:
        for i in range(num_chunks):
            chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
            start_time = i * 29

            # КРИТИЧНО: -c copy (без перекодирования)
            subprocess.run([
                'ffmpeg', '-i', audio_path,
                '-ss', str(start_time),
                '-t', '29',
                '-c', 'copy',  # Быстро!
                chunk_path, '-y'
            ], capture_output=True, check=True)

            chunks.append(chunk_path)

        # Транскрибируем каждую часть
        transcripts = []
        for chunk in chunks:
            text = transcribe_sync(chunk)
            if text.strip():
                transcripts.append(text)

        return " ".join(transcripts)

    finally:
        # Cleanup
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
```

#### Вариант 2: Async API

**Плюсы:**
- Нет проблемы стыков (одна обработка)
- Timestamps
- Дешевле на 40%

**Минусы:**
- Нужен Cloud Storage
- Латентность 5-10 минут
- Сложнее код

**Когда использовать:** Batch обработка вечером (не для real-time ответов клиентам)

---

## Гибридный подход (Best practice)

Комбинируй подходы в зависимости от сценария:

```python
def transcribe_smart(audio_path: str, urgent: bool = True) -> str:
    """
    Умный выбор API по контексту.

    Args:
        audio_path: Путь к аудио
        urgent: Нужен ли немедленный результат (клиент ждет)
    """
    duration = get_audio_duration(audio_path)

    # Короткие — всегда Sync
    if duration <= 29.0:
        return transcribe_sync(audio_path)

    # Длинные — выбор по срочности
    if urgent or duration <= 120.0:
        # Клиент ждет ИЛИ файл ≤2 минуты → деление
        return transcribe_long_sync(audio_path)
    else:
        # Batch обработка длинных (>2 мин) → Async
        audio_url = upload_to_storage(audio_path)
        return transcribe_async(audio_url)
```

---

## Сравнение производительности

### Файл 60 секунд

| Метод | Время обработки | Стоимость | Качество |
|-------|----------------|-----------|----------|
| Sync (деление на 3 части) | 1.5 сек | 0.80₽×3 = 2.40₽ | Хорошее (возможны стыки) |
| Async | 5-7 минут | 0.48₽×4 = 1.92₽ | Отличное |
| Streaming | Real-time | 0.96₽×4 = 3.84₽ | Отличное |

### Файл 30 секунд

| Метод | Время обработки | Стоимость |
|-------|----------------|-----------|
| Sync | 0.8 сек | 1.60₽ |
| Async | 5 минут | 0.96₽ |

**Вывод:** Для коротких файлов Sync всегда выгоднее (по времени), даже если дороже на 40%.

---

## Чеклист выбора API

**Используй Sync API если:**
- [ ] Аудио ≤29 секунд
- [ ] Нужен быстрый ответ (webhook, чат-бот)
- [ ] Простое приложение (скрипт, прототип)

**Используй деление на части + Sync если:**
- [ ] Аудио 30-120 секунд
- [ ] Клиент ждет ответа (WhatsApp/Telegram)
- [ ] Не критично качество на стыках

**Используй Async API если:**
- [ ] Аудио >2 минуты
- [ ] Batch обработка (не real-time)
- [ ] Нужны timestamps или profanity filter
- [ ] Важна экономия (большие объемы)

**Используй Streaming API если:**
- [ ] Real-time обработка (звонки, live)
- [ ] Голосовой помощник
- [ ] Call center

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/speechkit-basics.md` | Основы API, форматы, аутентификация |
| `references/long-audio-handling.md` | Детальный разбор обработки длинных файлов |
| `references/error-handling.md` | Обработка ошибок, retry, fallback |
| `references/performance-optimization.md` | Оптимизация скорости и стоимости |

---

## Официальная документация

- Sync API: https://cloud.yandex.ru/docs/speechkit/stt/api/request-api
- Async API: https://cloud.yandex.ru/docs/speechkit/stt/api/transcribation-api
- Streaming API: https://cloud.yandex.ru/docs/speechkit/stt/api/streaming-api
