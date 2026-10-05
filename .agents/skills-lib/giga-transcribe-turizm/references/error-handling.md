# Error Handling — Обработка ошибок

> Типичные ошибки Yandex SpeechKit и стратегии их обработки

---

## Типичные ошибки API

### HTTP Status Codes

| Код | Название | Причина | Решение |
|-----|----------|---------|---------|
| **400** | Bad Request | Неверные параметры | Проверить format, lang, folderId |
| **401** | Unauthorized | Неверный API ключ | Проверить YANDEX_CLOUD_API_KEY |
| **403** | Forbidden | Нет прав | Проверить scope ключа |
| **413** | Payload Too Large | Файл >1 МБ | Compress или использовать Async API |
| **429** | Too Many Requests | Rate limit | Exponential backoff |
| **500** | Internal Server Error | Проблема на стороне Yandex | Retry с задержкой |
| **503** | Service Unavailable | Сервис недоступен | Retry или fallback |

---

## 401 Unauthorized

### Причины

1. API ключ не задан
2. Неверный формат ключа
3. Ключ отозван или истёк
4. Неверный header (Api-Key vs Bearer)

### Диагностика

```python
import requests
import os

def test_auth():
    """Проверка аутентификации."""
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")

    if not api_key:
        print("❌ YANDEX_CLOUD_API_KEY не задан в .env")
        return False

    print(f"✓ API ключ найден: {api_key[:10]}...")

    # Тестовый запрос
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        headers={"Authorization": f"Api-Key {api_key}"},
        params={"folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID")},
        data=b""  # Пустой payload для теста
    )

    if response.status_code == 401:
        print("❌ 401 Unauthorized - проверьте ключ")
        return False
    elif response.status_code == 400:
        print("✓ Аутентификация OK (400 = нет аудио, но ключ правильный)")
        return True
    else:
        print(f"✓ Статус {response.status_code}")
        return True
```

### Решение

```python
def transcribe_with_auth_check(audio_path: str) -> str:
    """Транскрипция с проверкой auth."""
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")

    if not api_key:
        raise ValueError(
            "YANDEX_CLOUD_API_KEY не задан. "
            "Добавьте в .env: YANDEX_CLOUD_API_KEY=ваш_ключ"
        )

    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        headers={"Authorization": f"Api-Key {api_key}"},
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": "ru-RU",
            "format": "oggopus"
        },
        data=open(audio_path, "rb")
    )

    if response.status_code == 401:
        raise Exception(
            "401 Unauthorized. Проверьте:\n"
            "1. YANDEX_CLOUD_API_KEY в .env корректный\n"
            "2. Ключ не отозван в консоли Yandex Cloud\n"
            "3. Scope включает yc.ai.speechkitStt.execute"
        )

    return response.json().get("result", "")
```

---

## 429 Too Many Requests

### Проблема

Yandex SpeechKit имеет rate limit: **20 запросов в секунду**.

**Когда возникает:**
- Batch обработка множества файлов
- Параллельная обработка (threading/asyncio)
- Деление длинных аудио на части

### Exponential Backoff

```python
import time
import random

def transcribe_with_retry(
    audio_path: str,
    max_retries: int = 5,
    initial_delay: float = 1.0
) -> str:
    """
    Транскрипция с exponential backoff.

    Args:
        audio_path: Путь к аудио
        max_retries: Максимум попыток
        initial_delay: Начальная задержка (сек)

    Returns:
        str: Распознанный текст

    Raises:
        Exception: Если все попытки исчерпаны
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
                params={
                    "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
                    "lang": "ru-RU",
                    "format": "oggopus"
                },
                headers={
                    "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
                },
                data=open(audio_path, "rb")
            )

            if response.status_code == 200:
                return response.json().get("result", "")

            elif response.status_code == 429:
                # Rate limit — ждём и повторяем
                jitter = random.uniform(0, 0.3)  # Случайная задержка
                wait_time = delay + jitter

                print(f"429 Too Many Requests. Ждём {wait_time:.1f} сек...")
                time.sleep(wait_time)

                # Увеличиваем задержку (exponential)
                delay *= 2  # 1s → 2s → 4s → 8s → 16s

                continue

            else:
                # Другая ошибка — бросаем исключение
                raise Exception(f"SpeechKit error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            # Сетевая ошибка
            if attempt < max_retries - 1:
                print(f"Сетевая ошибка: {e}. Повтор {attempt+1}/{max_retries}...")
                time.sleep(delay)
                delay *= 2
                continue
            else:
                raise

    raise Exception(f"Исчерпаны попытки ({max_retries}). Последняя ошибка: 429 Rate Limit")
```

### Rate Limiting для batch обработки

```python
import time

def transcribe_batch(audio_files: list, rps_limit: int = 15) -> list:
    """
    Batch обработка с соблюдением rate limit.

    Args:
        audio_files: Список путей к аудио
        rps_limit: Запросов в секунду (меньше 20 для запаса)

    Returns:
        list: Список результатов [{text, file}, ...]
    """
    results = []
    delay_between_requests = 1.0 / rps_limit  # 15 RPS = 0.067 сек

    for i, audio_path in enumerate(audio_files):
        print(f"Обработка {i+1}/{len(audio_files)}: {audio_path}")

        try:
            text = transcribe_with_retry(audio_path)
            results.append({"file": audio_path, "text": text, "success": True})
        except Exception as e:
            results.append({"file": audio_path, "error": str(e), "success": False})

        # Задержка между запросами
        if i < len(audio_files) - 1:  # Не ждём после последнего
            time.sleep(delay_between_requests)

    return results
```

---

## 500 Internal Server Error

### Причины

- Проблема на стороне Yandex Cloud
- Перегрузка сервиса
- Повреждённый аудиофайл

### Стратегия retry

```python
def transcribe_with_500_retry(audio_path: str) -> str:
    """Retry для 500 ошибок."""
    max_retries = 3
    delay = 2  # 2 секунды между попытками

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
                params={
                    "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
                    "lang": "ru-RU",
                    "format": "oggopus"
                },
                headers={
                    "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
                },
                data=open(audio_path, "rb"),
                timeout=10  # Таймаут 10 сек
            )

            if response.status_code == 200:
                return response.json().get("result", "")

            elif response.status_code == 500:
                if attempt < max_retries - 1:
                    print(f"500 Internal Server Error. Повтор {attempt+1}/{max_retries}...")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception("500 Internal Server Error (после 3 попыток)")

            else:
                raise Exception(f"Error {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout. Повтор {attempt+1}/{max_retries}...")
                time.sleep(delay)
                continue
            else:
                raise Exception("Timeout после 3 попыток")

    raise Exception("Неожиданная ошибка")
```

---

## 413 Payload Too Large

### Проблема

Файл больше 1 МБ для Sync API.

### Решение 1: Проверка размера

```python
import os

def transcribe_check_size(audio_path: str) -> str:
    """Транскрипция с проверкой размера."""
    file_size = os.path.getsize(audio_path)
    max_size = 1 * 1024 * 1024  # 1 МБ

    if file_size > max_size:
        raise ValueError(
            f"Файл слишком большой ({file_size / 1024 / 1024:.1f} МБ > 1 МБ). "
            f"Используйте Async API или compress аудио."
        )

    # Обычная транскрипция
    return transcribe_direct(audio_path)
```

### Решение 2: Компрессия

```python
import subprocess

def compress_audio(input_path: str, output_path: str = None) -> str:
    """
    Компрессия аудио до <1 МБ.

    Args:
        input_path: Исходный файл
        output_path: Выходной файл (или auto)

    Returns:
        str: Путь к сжатому файлу
    """
    if output_path is None:
        output_path = input_path.replace(".ogg", "_compressed.ogg")

    # Снижение битрейта до 32 kbps (обычно достаточно для речи)
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-c:a', 'libopus',
        '-b:a', '32k',  # 32 kbps
        output_path, '-y'
    ], capture_output=True, check=True)

    return output_path


def transcribe_with_compression(audio_path: str) -> str:
    """Транскрипция с автокомпрессией при необходимости."""
    file_size = os.path.getsize(audio_path)
    max_size = 1 * 1024 * 1024

    if file_size > max_size:
        print(f"Файл {file_size / 1024 / 1024:.1f} МБ > 1 МБ. Компрессия...")
        compressed_path = compress_audio(audio_path)

        try:
            return transcribe_direct(compressed_path)
        finally:
            # Cleanup
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
    else:
        return transcribe_direct(audio_path)
```

---

## 400 Bad Request

### Причины

1. Неверный `format` (например, указали oggopus для mp3)
2. Неверный `lang` код
3. Неверный `folderId`
4. Повреждённый аудиофайл

### Диагностика

```python
def diagnose_400_error(audio_path: str):
    """Диагностика 400 ошибки."""
    print("=== Диагностика 400 Bad Request ===\n")

    # 1. Проверка файла
    if not os.path.exists(audio_path):
        print(f"❌ Файл не найден: {audio_path}")
        return

    print(f"✓ Файл существует: {audio_path}")
    print(f"  Размер: {os.path.getsize(audio_path) / 1024:.1f} КБ")

    # 2. Проверка формата
    import subprocess
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        import json
        info = json.loads(result.stdout)
        format_name = info["format"]["format_name"]
        print(f"✓ Формат: {format_name}")

        # Проверка на соответствие
        if "ogg" in format_name:
            print("  → Используйте format=oggopus")
        elif "mp3" in format_name:
            print("  → Используйте format=mp3")
        else:
            print("  ⚠ Неподдерживаемый формат")
    else:
        print("❌ Не удалось определить формат (ffprobe ошибка)")

    # 3. Проверка переменных окружения
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    folder_id = os.getenv("YANDEX_CLOUD_FOLDER_ID")

    if not api_key:
        print("❌ YANDEX_CLOUD_API_KEY не задан")
    else:
        print(f"✓ API ключ: {api_key[:10]}...")

    if not folder_id:
        print("❌ YANDEX_CLOUD_FOLDER_ID не задан")
    else:
        print(f"✓ Folder ID: {folder_id}")
```

---

## Fallback на Whisper API

### Стратегия

Если SpeechKit недоступен или выдаёт ошибки — используем OpenAI Whisper как fallback.

```python
def transcribe_with_fallback(audio_path: str) -> dict:
    """
    Транскрипция с fallback на Whisper API.

    Returns:
        dict: {
            "text": str,
            "source": "speechkit" | "whisper_fallback",
            "success": bool
        }
    """
    try:
        # Попытка SpeechKit
        text = transcribe_with_retry(audio_path, max_retries=3)
        return {
            "text": text,
            "source": "speechkit",
            "success": True
        }

    except Exception as speechkit_error:
        print(f"SpeechKit ошибка: {speechkit_error}")
        print("Fallback на Whisper API...")

        try:
            # Fallback на Whisper
            import openai

            client = openai.OpenAI()

            with open(audio_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="ru"  # или auto-detect
                )

            return {
                "text": transcript.text,
                "source": "whisper_fallback",
                "success": True
            }

        except Exception as whisper_error:
            print(f"Whisper ошибка: {whisper_error}")
            return {
                "text": "",
                "source": "none",
                "success": False,
                "error": f"Both APIs failed: SpeechKit={speechkit_error}, Whisper={whisper_error}"
            }
```

---

## Logging и мониторинг

### Структурированный logging

```python
import logging
import json
from datetime import datetime

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("speechkit.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("speechkit")


def transcribe_with_logging(audio_path: str) -> dict:
    """Транскрипция с детальным логированием."""
    start_time = datetime.now()

    log_data = {
        "timestamp": start_time.isoformat(),
        "file": audio_path,
        "file_size": os.path.getsize(audio_path)
    }

    try:
        logger.info(f"Начало транскрипции: {audio_path}")

        text = transcribe_with_retry(audio_path)

        elapsed = (datetime.now() - start_time).total_seconds()
        log_data.update({
            "success": True,
            "text_length": len(text),
            "elapsed": elapsed
        })

        logger.info(f"Успех: {elapsed:.2f} сек, {len(text)} символов")

        return {"success": True, "text": text}

    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        log_data.update({
            "success": False,
            "error": str(e),
            "elapsed": elapsed
        })

        logger.error(f"Ошибка: {e}")

        return {"success": False, "error": str(e)}

    finally:
        # Запись в JSON лог для аналитики
        with open("speechkit_analytics.jsonl", "a") as f:
            f.write(json.dumps(log_data) + "\n")
```

### Мониторинг метрик

```python
def analyze_logs(log_file: str = "speechkit_analytics.jsonl"):
    """Анализ метрик из логов."""
    import json

    successes = 0
    failures = 0
    total_time = 0
    errors = {}

    with open(log_file, "r") as f:
        for line in f:
            data = json.loads(line)

            if data["success"]:
                successes += 1
                total_time += data["elapsed"]
            else:
                failures += 1
                error = data["error"]
                errors[error] = errors.get(error, 0) + 1

    total = successes + failures

    print(f"=== Метрики SpeechKit ===")
    print(f"Всего запросов: {total}")
    print(f"Успешных: {successes} ({successes/total*100:.1f}%)")
    print(f"Ошибок: {failures} ({failures/total*100:.1f}%)")
    print(f"Среднее время: {total_time/successes:.2f} сек")
    print(f"\nТоп ошибок:")
    for error, count in sorted(errors.items(), key=lambda x: -x[1])[:5]:
        print(f"  {count}× {error[:50]}...")
```

---

## Best Practices

### 1. Комбинированная обработка ошибок

```python
def transcribe_production(audio_path: str) -> dict:
    """
    Production-ready транскрипция.

    Включает:
    - Проверку файла
    - Retry с exponential backoff
    - Fallback на Whisper
    - Логирование
    """
    # 1. Валидация
    if not os.path.exists(audio_path):
        return {"success": False, "error": "File not found"}

    file_size = os.path.getsize(audio_path)
    if file_size > 1024 * 1024:  # >1 МБ
        logger.warning(f"Файл большой ({file_size/1024/1024:.1f} МБ), компрессия...")
        audio_path = compress_audio(audio_path)

    # 2. Попытка SpeechKit с retry
    try:
        text = transcribe_with_retry(audio_path, max_retries=3)
        return {"success": True, "text": text, "source": "speechkit"}

    except Exception as e:
        logger.error(f"SpeechKit failed: {e}")

        # 3. Fallback на Whisper
        try:
            import openai
            client = openai.OpenAI()

            with open(audio_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )

            return {
                "success": True,
                "text": transcript.text,
                "source": "whisper_fallback"
            }

        except Exception as whisper_error:
            logger.error(f"Whisper failed: {whisper_error}")
            return {
                "success": False,
                "error": f"Both APIs failed",
                "details": {
                    "speechkit": str(e),
                    "whisper": str(whisper_error)
                }
            }
```

### 2. Circuit Breaker Pattern

```python
import time

class CircuitBreaker:
    """Circuit breaker для защиты от перегрузки API."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        """Вызов функции через circuit breaker."""
        if self.state == "open":
            # Проверяем, прошло ли время timeout
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker OPEN - API недоступен")

        try:
            result = func(*args, **kwargs)

            # Успех — сбрасываем счётчик
            if self.state == "half-open":
                self.state = "closed"
            self.failures = 0

            return result

        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = "open"

            raise


# Использование
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def transcribe_with_breaker(audio_path: str) -> str:
    """Транскрипция с circuit breaker."""
    return breaker.call(transcribe_with_retry, audio_path)
```

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/speechkit-basics.md` | Основы API, endpoints, аутентификация |
| `references/sync-vs-async.md` | Выбор между Sync и Async API |
| `references/performance-optimization.md` | Оптимизация производительности |
| `references/troubleshooting.md` | Топ-10 проблем и решений |

---

## Официальная документация

- API Errors: https://cloud.yandex.ru/docs/speechkit/stt/api/response
- Rate Limits: https://cloud.yandex.ru/docs/speechkit/concepts/limits
- HTTP Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
