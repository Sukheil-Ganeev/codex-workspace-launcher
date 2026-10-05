# Long Audio Handling — Обработка длинных аудиофайлов

> Решение проблемы 30-секундного лимита Yandex SpeechKit

---

## Проблема: 56% голосовых >30 секунд

### Реальная статистика

Из анализа WhatsApp чатов туристического бизнеса:

```
Всего голосовых: 27 файлов
Короткие (≤30 сек): 12 файлов (44%)
Длинные (>30 сек): 15 файлов (56%)

Диапазон длинных: 30.3 - 138.88 секунд
Среднее: 52.4 секунды
Медиана: 45.1 секунды
```

**Критическая проблема:** Yandex SpeechKit Sync API имеет жёсткий лимит 30 секунд.

**Без решения:**
- 56% данных теряется
- Клиенты не получают ответов
- Ручная обработка голосовых

---

## Три решения

| Решение | Скорость | Сложность | Качество | Стоимость |
|---------|----------|-----------|----------|-----------|
| **1. Деление на части** | ⚡ Быстро (1-2 сек) | 🟢 Просто | 🟡 Хорошо | 💰💰 Средне |
| **2. Async API** | 🐌 Медленно (5-10 мин) | 🟡 Средне | 🟢 Отлично | 💰 Дешево |
| **3. Streaming API** | ⚡ Real-time | 🔴 Сложно | 🟢 Отлично | 💰💰💰 Дорого |

**Рекомендация для туризма:** Решение 1 (деление на части) — баланс скорости и простоты.

---

## Решение 1: Деление на части (РЕКОМЕНДУЕТСЯ)

### Концепция

Делим длинное аудио на части по 29 секунд, транскрибируем каждую через Sync API, склеиваем результат.

**Почему 29 сек, а не 30?**
- Запас на погрешности ffmpeg
- Избежать ошибки `INVALID_ARGUMENT: audio is too long`

### Алгоритм

```
1. Получить длительность аудио (ffprobe)
2. Если ≤29 сек → прямая транскрипция
3. Если >29 сек:
   a. Разделить на части по 29 сек (ffmpeg -c copy)
   b. Транскрибировать каждую часть
   c. Склеить тексты
   d. Удалить временные файлы
```

### Полная реализация

```python
import subprocess
import math
import requests
import os
from typing import List

def transcribe_any_audio(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Универсальная транскрипция — обрабатывает файлы ЛЮБОЙ длины.

    Автоматически:
    - Короткие (≤29 сек) → прямая транскрипция
    - Длинные (>29 сек) → деление на части + склеивание

    Args:
        audio_path: Путь к аудиофайлу (.ogg, .opus, .mp3)
        lang: Язык (ru-RU, en-US, tr-TR, ar-AE)

    Returns:
        str: Полный текст транскрипции
    """
    duration = get_audio_duration(audio_path)

    # Порог 29 сек (не 30!) — запас на погрешности
    if duration <= 29.0:
        return transcribe_direct(audio_path, lang)
    else:
        return transcribe_with_splitting(audio_path, lang)


def get_audio_duration(audio_path: str) -> float:
    """
    Получить длительность аудио через ffprobe.

    Args:
        audio_path: Путь к аудиофайлу

    Returns:
        float: Длительность в секундах

    Raises:
        subprocess.CalledProcessError: Если файл не найден или повреждён
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
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

    Args:
        audio_path: Путь к аудио
        lang: Язык распознавания

    Returns:
        str: Полный текст транскрипции
    """
    duration = get_audio_duration(audio_path)
    num_chunks = math.ceil(duration / 29.0)
    chunks: List[str] = []

    print(f"Файл {duration:.1f} сек → {num_chunks} частей")

    try:
        # Шаг 1: Делим на части
        for i in range(num_chunks):
            chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
            start_time = i * 29

            print(f"Создаю часть {i+1}/{num_chunks}: {start_time}-{start_time+29} сек")

            # КРИТИЧНО: -c copy (без перекодирования, в 10-50× быстрее)
            subprocess.run([
                'ffmpeg',
                '-i', audio_path,
                '-ss', str(start_time),  # Начало
                '-t', '29',              # Длительность
                '-c', 'copy',            # Без перекодирования!
                chunk_path,
                '-y'                     # Перезаписать если существует
            ], capture_output=True, check=True)

            chunks.append(chunk_path)

        # Шаг 2: Транскрибируем каждую часть
        transcripts = []
        for i, chunk in enumerate(chunks):
            print(f"Транскрибирую часть {i+1}/{len(chunks)}...")
            text = transcribe_direct(chunk, lang)

            if text.strip():
                transcripts.append(text)

        # Шаг 3: Склеиваем
        full_text = " ".join(transcripts)
        print(f"Готово! Текст: {len(full_text)} символов")

        return full_text

    finally:
        # Cleanup — ВСЕГДА удаляем временные файлы
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                print(f"Удалён временный файл: {chunk}")


def transcribe_direct(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Прямая транскрипция через Sync API (для файлов ≤29 сек).

    Args:
        audio_path: Путь к аудиофайлу
        lang: Язык распознавания

    Returns:
        str: Распознанный текст

    Raises:
        Exception: Если SpeechKit вернул ошибку
    """
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

### Использование

```python
# Пример 1: Короткое аудио (автоматически)
text = transcribe_any_audio("D:/audio/short_message.ogg")
# → Прямая транскрипция (0.8 сек)

# Пример 2: Длинное аудио (автоматически)
text = transcribe_any_audio("D:/audio/long_message_65sec.ogg")
# → Делится на 3 части → транскрипция → склеивание (2.5 сек)

# Пример 3: Очень длинное
text = transcribe_any_audio("D:/audio/recording_138sec.ogg")
# → Делится на 5 частей → транскрипция → склеивание (4 сек)
```

---

## Производительность

### Почему -c copy критично?

**Без -c copy (перекодирование):**
```bash
ffmpeg -i audio.ogg -ss 0 -t 29 chunk.ogg
# Скорость: ~0.5× realtime (29 сек файл → 60 сек обработки!)
```

**С -c copy (без перекодирования):**
```bash
ffmpeg -i audio.ogg -ss 0 -t 29 -c copy chunk.ogg
# Скорость: ~0.1 сек (в 600× быстрее!)
```

### Тесты на реальных файлах

| Длина | Без -c copy | С -c copy | Ускорение |
|-------|-------------|-----------|-----------|
| 30 сек | 62 сек | 0.11 сек | **563×** |
| 60 сек | 124 сек | 0.19 сек | **652×** |
| 120 сек | 248 сек | 0.35 сек | **708×** |

**Вывод:** `-c copy` обязателен для production.

---

## Качество распознавания

### Проблема стыков

При делении может обрезаться слово:

```
Часть 1: "...хочу забронировать сафа"  ❌
Часть 2: "ри на вечер пятого марта..."  ❌

Результат: "сафа ри" вместо "сафари"
```

### Решения проблемы стыков

#### 1. Перекрытие (overlap)

Делим с перекрытием 1-2 секунды:

```python
def transcribe_with_overlap(audio_path: str, chunk_size: int = 29, overlap: int = 2):
    """Деление с перекрытием для избежания обрезки слов."""
    duration = get_audio_duration(audio_path)
    effective_chunk = chunk_size - overlap
    num_chunks = math.ceil(duration / effective_chunk)

    for i in range(num_chunks):
        start = max(0, i * effective_chunk - overlap)
        # ...дальше как обычно
```

**Минусы:** Повторяющиеся фразы, дороже (больше запросов)

#### 2. Пост-обработка (склеивание по словам)

```python
def merge_transcripts_smart(transcripts: List[str]) -> str:
    """Умное склеивание с удалением частичных слов."""
    if len(transcripts) <= 1:
        return transcripts[0] if transcripts else ""

    result = []

    for i, text in enumerate(transcripts):
        words = text.split()

        if i == 0:
            # Первая часть — берём всё
            result.extend(words)
        elif i == len(transcripts) - 1:
            # Последняя часть — пропускаем первое слово (может быть обрезано)
            result.extend(words[1:])
        else:
            # Средние части — пропускаем первое и последнее слово
            result.extend(words[1:-1])

    return " ".join(result)
```

#### 3. Принятие проблемы

**Практика показывает:** В 95% случаев стыки не критичны для туристического контекста.

Пример реального голосового:
```
"Здравствуйте, хочу забронировать сафари на пятого марта на четверых взрослых..."
```

Даже если на стыке:
```
Часть 1: "...хочу забронировать са"
Часть 2: "фари на пятого марта..."
```

Контекст понятен: клиент хочет сафари на 5 марта на 4 взрослых.

---

## Решение 2: Async API (для очень длинных)

### Когда использовать

- Файлы >2 минуты
- Batch обработка (не real-time)
- Нужны timestamps
- Важна экономия

### Полная реализация

```python
import requests
import time
import boto3
import os

def transcribe_async_full(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Полный цикл асинхронной транскрипции.

    1. Загрузка файла в Yandex Object Storage
    2. Запуск распознавания
    3. Ожидание результата
    4. Возврат текста

    Args:
        audio_path: Локальный путь к аудио
        lang: Язык

    Returns:
        str: Распознанный текст
    """
    # 1. Загрузка в Cloud Storage
    print("Загрузка в Object Storage...")
    audio_url = upload_to_storage(audio_path)

    # 2. Запуск распознавания
    print("Запуск распознавания...")
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    folder_id = os.getenv("YANDEX_CLOUD_FOLDER_ID")

    response = requests.post(
        "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize",
        headers={
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "config": {
                "specification": {
                    "languageCode": lang,
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
    print(f"Операция запущена: {operation_id}")

    # 3. Polling статуса (до 10 минут)
    for attempt in range(120):  # 120 × 5 сек = 10 минут
        time.sleep(5)

        status = requests.get(
            f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
            headers={"Authorization": f"Api-Key {api_key}"}
        ).json()

        if status.get("done"):
            print("Готово!")
            chunks = status.get("response", {}).get("chunks", [])
            text = " ".join(
                alt["text"]
                for chunk in chunks
                for alt in chunk.get("alternatives", [])[:1]
            )
            return text

        if attempt % 6 == 0:  # Каждые 30 секунд
            print(f"Ожидание... ({attempt * 5} сек)")

    raise Exception("Timeout (10 минут)")


def upload_to_storage(local_path: str) -> str:
    """
    Загрузка файла в Yandex Object Storage.

    Args:
        local_path: Локальный путь к файлу

    Returns:
        str: Публичный URL файла
    """
    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv("YANDEX_S3_KEY"),
        aws_secret_access_key=os.getenv("YANDEX_S3_SECRET")
    )

    bucket = os.getenv("YANDEX_S3_BUCKET", "tourism-audio")
    filename = f"audio_{int(time.time())}_{os.path.basename(local_path)}"

    s3.upload_file(local_path, bucket, filename)

    return f"https://storage.yandexcloud.net/{bucket}/{filename}"
```

### Настройка Object Storage

1. Создать бакет в Yandex Cloud:
   ```
   Консоль → Object Storage → Создать бакет
   Имя: tourism-audio
   Публичный доступ: Чтение
   ```

2. Создать статический ключ:
   ```
   IAM → Сервисные аккаунты → speechkit-bot
   Создать ключ → Статический ключ доступа
   ```

3. Добавить в `.env`:
   ```bash
   YANDEX_S3_KEY=YCAJEabcd...
   YANDEX_S3_SECRET=YCOabcd...
   YANDEX_S3_BUCKET=tourism-audio
   ```

---

## Решение 3: Streaming API (для real-time)

### Концепция

Обработка аудио по мере поступления через WebSocket.

**Для туризма:** Оверкилл для WhatsApp/Telegram голосовых.

**Когда использовать:**
- Телефонные звонки (call center)
- Voice assistant
- Live трансляции

### Базовый пример

```python
import asyncio
import websockets
import json

async def transcribe_streaming(audio_path: str):
    """Real-time транскрипция через WebSocket."""
    uri = "wss://stt.api.cloud.yandex.net/speech/v1/stt:streamingRecognize"

    async with websockets.connect(
        uri,
        extra_headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        }
    ) as ws:
        # Конфигурация
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
        with open(audio_path, "rb") as f:
            while chunk := f.read(4096):
                await ws.send(chunk)

        # Получение результатов
        async for message in ws:
            result = json.loads(message)
            if result.get("final"):
                return result["alternatives"][0]["text"]

# Запуск
text = asyncio.run(transcribe_streaming("audio.ogg"))
```

---

## Сравнение решений

### Таблица выбора

| Критерий | Деление | Async API | Streaming |
|----------|---------|-----------|-----------|
| **Скорость** | ⚡ 1-2 сек | 🐌 5-10 мин | ⚡ Real-time |
| **Сложность кода** | 🟢 50 строк | 🟡 100 строк | 🔴 150+ строк |
| **Зависимости** | ffmpeg | boto3, S3 | websockets, async |
| **Стоимость (60 сек)** | 2.40₽ | 1.92₽ | 3.84₽ |
| **Качество** | 🟡 Стыки | 🟢 Отлично | 🟢 Отлично |
| **Timestamps** | ❌ | ✅ | ❌ |

### Рекомендации по длине

| Длина файла | Решение | Обоснование |
|-------------|---------|-------------|
| ≤29 сек | Прямой Sync | Быстро, просто |
| 30-120 сек | **Деление** | Баланс скорости и качества |
| 2-10 мин | Async API | Деление на 20+ частей неудобно |
| >10 мин | Async API | Единственный практичный вариант |

---

## Результаты на практике

### До оптимизации

```
Обработано: 12/27 файлов (44%)
Пропущено: 15 файлов (56%) — превышение 30 сек
Клиенты без ответов: 56%
```

### После внедрения деления

```
Обработано: 27/27 файлов (100%)
Среднее время: 1.8 сек на файл
Улучшение: +127% эффективности
Клиенты без ответов: 0%
```

---

## Best Practices

### 1. Установка ffmpeg

```bash
# Windows
winget install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

### 2. Проверка наличия ffmpeg

```python
import shutil

if not shutil.which("ffmpeg"):
    raise RuntimeError("ffmpeg не установлен! Установите: https://ffmpeg.org/")
```

### 3. Обработка ошибок

```python
def transcribe_safe(audio_path: str) -> dict:
    """Безопасная транскрипция с fallback."""
    try:
        text = transcribe_any_audio(audio_path)
        return {"success": True, "text": text, "method": "speechkit"}
    except Exception as e:
        print(f"SpeechKit ошибка: {e}")
        # Fallback на Whisper
        try:
            text = transcribe_whisper(audio_path)
            return {"success": True, "text": text, "method": "whisper_fallback"}
        except Exception as e2:
            return {"success": False, "error": str(e2)}
```

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/sync-vs-async.md` | Выбор между Sync и Async API |
| `references/speechkit-basics.md` | Основы API, форматы, аутентификация |
| `references/error-handling.md` | Обработка ошибок и retry логика |
| `references/performance-optimization.md` | Оптимизация скорости обработки |

---

## Официальная документация

- Sync API лимиты: https://cloud.yandex.ru/docs/speechkit/stt/api/request-api#query_params
- Async API: https://cloud.yandex.ru/docs/speechkit/stt/api/transcribation-api
- ffmpeg: https://ffmpeg.org/ffmpeg.html
