# Troubleshooting — Решение проблем

> Топ-10 проблем при работе с Yandex SpeechKit и их решения

---

## Проблема 1: 401 Unauthorized

### Симптомы

```
Error 401: Unauthorized
{"error": "Invalid API key"}
```

### Причины

1. API ключ не задан в `.env`
2. Неверный формат ключа
3. Ключ отозван в Yandex Cloud
4. Неверный header (Api-Key вместо Bearer)

### Диагностика

```python
import os
import requests

def diagnose_401():
    """Диагностика 401 ошибки."""
    print("=== Диагностика 401 Unauthorized ===\n")

    # 1. Проверка переменных окружения
    api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    folder_id = os.getenv("YANDEX_CLOUD_FOLDER_ID")

    if not api_key:
        print("❌ YANDEX_CLOUD_API_KEY не задан")
        print("Решение: Добавьте в .env файл:")
        print("  YANDEX_CLOUD_API_KEY=ваш_ключ")
        return

    print(f"✓ API ключ найден: {api_key[:15]}...")

    if not folder_id:
        print("❌ YANDEX_CLOUD_FOLDER_ID не задан")
        return

    print(f"✓ Folder ID: {folder_id}")

    # 2. Тестовый запрос
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        headers={"Authorization": f"Api-Key {api_key}"},
        params={"folderId": folder_id},
        data=b""
    )

    if response.status_code == 401:
        print("\n❌ 401 Unauthorized")
        print("Возможные причины:")
        print("1. Ключ неверный или отозван")
        print("2. Проверьте консоль: https://console.cloud.yandex.ru/")
        print("3. Пересоздайте API ключ")
    elif response.status_code == 400:
        print("\n✓ Аутентификация успешна (400 = нет аудио, но ключ OK)")
    else:
        print(f"\n✓ Статус {response.status_code}")

diagnose_401()
```

### Решение

**Шаг 1:** Проверить наличие ключа
```bash
# .env
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f
```

**Шаг 2:** Проверить формат header
```python
# ✓ Правильно
headers = {"Authorization": f"Api-Key {api_key}"}

# ❌ Неправильно
headers = {"Authorization": f"Bearer {api_key}"}  # Bearer для IAM токена!
```

**Шаг 3:** Пересоздать ключ
```
Yandex Cloud Console → IAM → Сервисные аккаунты
→ speechkit-bot → Создать новый ключ → API-ключ
→ Scope: yc.ai.speechkitStt.execute
```

---

## Проблема 2: Файл слишком большой (413 Payload Too Large)

### Симптомы

```
Error 413: Payload Too Large
File size exceeds 1 MB limit
```

### Причины

Sync API имеет лимит 1 МБ на файл.

### Диагностика

```python
def check_file_size(audio_path: str):
    """Проверка размера файла."""
    size_bytes = os.path.getsize(audio_path)
    size_mb = size_bytes / (1024 * 1024)

    print(f"Файл: {audio_path}")
    print(f"Размер: {size_mb:.2f} МБ")

    if size_mb > 1:
        print("❌ Файл больше 1 МБ (лимит Sync API)")
        print("\nРешения:")
        print("1. Компрессия до 32 kbps")
        print("2. Использовать Async API")
        print("3. Деление на части")
    else:
        print("✓ Размер OK для Sync API")
```

### Решение 1: Компрессия

```python
import subprocess

def compress_audio(input_path: str) -> str:
    """Компрессия аудио до <1 МБ."""
    output_path = input_path.replace(".ogg", "_compressed.ogg")

    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-c:a', 'libopus',
        '-b:a', '32k',  # 32 kbps (достаточно для речи)
        '-ar', '16000',  # 16 kHz
        output_path, '-y'
    ], capture_output=True, check=True)

    # Проверка
    original_size = os.path.getsize(input_path) / (1024 * 1024)
    compressed_size = os.path.getsize(output_path) / (1024 * 1024)

    print(f"✓ Компрессия: {original_size:.2f} МБ → {compressed_size:.2f} МБ")

    return output_path
```

### Решение 2: Async API

См. `references/sync-vs-async.md` → Async API для больших файлов.

---

## Проблема 3: Плохое качество распознавания

### Симптомы

```
Результат: "кбр ть сфр на трх днх"
Ожидалось: "забронировать сафари на пятого марта"
```

### Причины

1. Плохое качество аудио (шум, тихий голос)
2. Неверный язык (указали ru-RU, клиент говорит по-английски)
3. Неверный формат (указали oggopus для mp3)
4. Повреждённый файл

### Диагностика

```python
import subprocess
import json

def diagnose_audio_quality(audio_path: str):
    """Диагностика качества аудио."""
    print("=== Диагностика аудио ===\n")

    # 1. Проверка формата через ffprobe
    result = subprocess.run([
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', '-show_streams',
        audio_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Не удалось прочитать файл (повреждён?)")
        return

    info = json.loads(result.stdout)
    format_info = info["format"]
    audio_stream = info["streams"][0]

    # Параметры
    duration = float(format_info["duration"])
    bitrate = int(format_info.get("bit_rate", 0)) / 1000  # kbps
    sample_rate = int(audio_stream.get("sample_rate", 0))
    codec = audio_stream["codec_name"]

    print(f"Длительность: {duration:.1f} сек")
    print(f"Формат: {format_info['format_name']}")
    print(f"Кодек: {codec}")
    print(f"Битрейт: {bitrate:.0f} kbps")
    print(f"Sample rate: {sample_rate} Hz")

    # Предупреждения
    if bitrate < 20:
        print("\n⚠ Низкий битрейт (<20 kbps) — качество может быть плохим")

    if sample_rate < 8000:
        print("\n⚠ Низкий sample rate (<8 kHz) — качество STT пострадает")

    if codec not in ["opus", "mp3", "pcm_s16le"]:
        print(f"\n⚠ Необычный кодек: {codec}")

diagnose_audio_quality("audio.ogg")
```

### Решение 1: Проверка языка

```python
def fix_language_detection(audio_path: str) -> str:
    """Попытка нескольких языков."""
    languages = ["ru-RU", "en-US", "ar-AE"]

    best_result = None
    best_score = 0

    for lang in languages:
        text = transcribe_direct(audio_path, lang)
        score = len(text.split())  # Больше слов = лучше

        print(f"{lang}: {score} слов — {text[:50]}...")

        if score > best_score:
            best_score = score
            best_result = {"lang": lang, "text": text}

    return best_result["text"]
```

### Решение 2: Улучшение аудио (noise reduction)

```python
def enhance_audio(input_path: str) -> str:
    """Улучшение аудио (noise reduction)."""
    output_path = input_path.replace(".ogg", "_enhanced.ogg")

    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-af', 'highpass=f=200,lowpass=f=3000',  # Фильтр речевых частот
        '-c:a', 'libopus',
        output_path, '-y'
    ], capture_output=True, check=True)

    return output_path
```

---

## Проблема 4: 429 Too Many Requests (Rate Limit)

### Симптомы

```
Error 429: Too Many Requests
Rate limit exceeded: 20 RPS
```

### Причины

Превышение лимита 20 запросов в секунду.

### Решение

```python
import time
from collections import deque

class RateLimiter:
    """Rate limiter для 20 RPS."""

    def __init__(self, max_rps: int = 20):
        self.max_rps = max_rps
        self.requests = deque(maxlen=max_rps)

    def wait_if_needed(self):
        """Ждёт если превышен лимит."""
        now = time.time()

        if len(self.requests) >= self.max_rps:
            oldest = self.requests[0]
            elapsed = now - oldest

            if elapsed < 1.0:
                wait_time = 1.0 - elapsed + 0.01  # +10ms запас
                print(f"Rate limit: ждём {wait_time:.2f} сек...")
                time.sleep(wait_time)

        self.requests.append(time.time())


# Использование
limiter = RateLimiter(max_rps=15)  # 15 для запаса

for audio_path in audio_files:
    limiter.wait_if_needed()
    text = transcribe_direct(audio_path)
```

---

## Проблема 5: CORS ошибки (в браузере)

### Симптомы

```
Access to XMLHttpRequest has been blocked by CORS policy
```

### Причина

Yandex SpeechKit API не поддерживает CORS (вызовы из браузера).

### Решение

**НЕ вызывай API напрямую из браузера!** Используй backend proxy.

```python
# Backend (Flask)
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Разрешаем CORS

@app.route("/api/transcribe", methods=["POST"])
def proxy_transcribe():
    """Proxy для SpeechKit (обходит CORS)."""
    audio_data = request.files["audio"].read()

    # Вызываем SpeechKit от имени backend
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
        data=audio_data
    )

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5000)
```

Frontend:
```javascript
// Отправка на proxy (без CORS проблем)
const formData = new FormData();
formData.append('audio', audioBlob);

fetch('http://localhost:5000/api/transcribe', {
    method: 'POST',
    body: formData
})
.then(r => r.json())
.then(data => console.log(data.result));
```

---

## Проблема 6: Timeout (запрос зависает)

### Симптомы

```
Запрос висит >30 секунд, потом timeout
```

### Причины

1. Медленный интернет (upload большого файла)
2. Перегрузка SpeechKit API
3. Проблема с сетью

### Решение

```python
import requests

def transcribe_with_timeout(audio_path: str, timeout: int = 30) -> str:
    """
    Транскрипция с timeout.

    Args:
        audio_path: Путь к аудио
        timeout: Максимальное время ожидания (сек)

    Returns:
        str: Транскрипция

    Raises:
        requests.exceptions.Timeout: Если timeout
    """
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
            timeout=timeout  # Таймаут!
        )

        return response.json().get("result", "")

    except requests.exceptions.Timeout:
        print(f"❌ Timeout ({timeout} сек)")
        print("Решения:")
        print("1. Увеличить timeout")
        print("2. Compress аудио")
        print("3. Проверить интернет")
        raise
```

---

## Проблема 7: Неверный формат аудио (400 Bad Request)

### Симптомы

```
Error 400: Bad Request
Unsupported audio format
```

### Причины

Указали неверный `format` параметр (например, oggopus для mp3).

### Диагностика

```python
def detect_audio_format(audio_path: str) -> str:
    """Определение формата аудио."""
    result = subprocess.run([
        'ffprobe', '-v', 'quiet',
        '-show_entries', 'format=format_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ], capture_output=True, text=True, check=True)

    format_name = result.stdout.strip()

    # Маппинг на SpeechKit параметры
    format_map = {
        "ogg": "oggopus",
        "mp3": "mp3",
        "wav": "lpcm"
    }

    for key, value in format_map.items():
        if key in format_name:
            return value

    return "unknown"

# Использование
detected_format = detect_audio_format("audio.ogg")
print(f"Формат: {detected_format}")

# Транскрибировать с правильным форматом
transcribe_direct(audio_path, format=detected_format)
```

---

## Проблема 8: Деление на части обрезает слова

### Симптомы

```
Часть 1: "...хочу забронировать са"
Часть 2: "фари на пятого марта..."
Результат: "са фари" вместо "сафари"
```

### Причина

Слово попало на стык частей (29-30 секунда).

### Решение 1: Перекрытие (overlap)

```python
def split_with_overlap(audio_path: str, chunk_size: int = 29, overlap: int = 2):
    """
    Деление с перекрытием.

    Args:
        audio_path: Путь к аудио
        chunk_size: Размер части (сек)
        overlap: Перекрытие (сек)
    """
    duration = get_audio_duration(audio_path)
    effective_chunk = chunk_size - overlap
    num_chunks = math.ceil(duration / effective_chunk)

    chunks = []

    for i in range(num_chunks):
        start = max(0, i * effective_chunk - overlap)
        chunk_path = f"{audio_path}_chunk_{i}.ogg"

        subprocess.run([
            'ffmpeg', '-i', audio_path,
            '-ss', str(start),
            '-t', str(chunk_size),
            '-c', 'copy',
            chunk_path, '-y'
        ], capture_output=True, check=True)

        chunks.append(chunk_path)

    return chunks
```

### Решение 2: Умное склеивание

```python
def merge_transcripts_smart(transcripts: list) -> str:
    """
    Умное склеивание (убирает обрезанные слова).

    Логика:
    - Первая часть: берём все слова
    - Средние части: пропускаем первое и последнее слово
    - Последняя часть: пропускаем первое слово
    """
    if len(transcripts) <= 1:
        return transcripts[0] if transcripts else ""

    result = []

    for i, text in enumerate(transcripts):
        words = text.split()

        if i == 0:
            # Первая часть
            result.extend(words)
        elif i == len(transcripts) - 1:
            # Последняя часть
            result.extend(words[1:])
        else:
            # Средние части
            result.extend(words[1:-1])

    return " ".join(result)
```

---

## Проблема 9: Не установлен ffmpeg

### Симптомы

```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

### Причина

ffmpeg не установлен или не в PATH.

### Решение

**Windows:**
```bash
# Через winget
winget install ffmpeg

# Или скачать: https://ffmpeg.org/download.html
# Добавить в PATH: C:\ffmpeg\bin
```

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Проверка:**
```bash
ffmpeg -version
```

### Проверка в Python

```python
import shutil

def check_ffmpeg():
    """Проверка наличия ffmpeg."""
    if shutil.which("ffmpeg"):
        print("✓ ffmpeg установлен")
        return True
    else:
        print("❌ ffmpeg не найден")
        print("Установите: https://ffmpeg.org/")
        return False

check_ffmpeg()
```

---

## Проблема 10: Медленная обработка batch файлов

### Симптомы

```
100 файлов → 180 секунд (1.8 сек/файл)
Ожидалось: <1 минуты
```

### Причины

1. Последовательная обработка (не параллельная)
2. Нет кеширования
3. Медленное деление (без `-c copy`)

### Решение

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_batch_optimized(audio_files: list) -> list:
    """
    Оптимизированная batch обработка.

    Фичи:
    - Параллелизация (5 потоков)
    - Кеширование результатов
    - Rate limiting
    - Обработка ошибок
    """
    limiter = RateLimiter(max_rps=15)
    results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(process_one_file, audio_path, limiter): audio_path
            for audio_path in audio_files
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results


def process_one_file(audio_path: str, limiter: RateLimiter) -> dict:
    """Обработка одного файла."""
    # Проверка кеша
    cached = check_cache(audio_path)
    if cached:
        return {"file": audio_path, "text": cached, "cached": True}

    # Rate limiting
    limiter.wait_if_needed()

    # Транскрипция
    try:
        text = transcribe_any_audio(audio_path)
        save_to_cache(audio_path, text)

        return {"file": audio_path, "text": text, "success": True}

    except Exception as e:
        return {"file": audio_path, "error": str(e), "success": False}
```

**Результат:**
- Было: 180 сек (последовательно)
- Стало: 45 сек (параллельно + кеш)
- Ускорение: 4×

---

## Чеклист диагностики

Когда что-то не работает, проверь по порядку:

**1. Переменные окружения**
- [ ] `YANDEX_CLOUD_API_KEY` задан и правильный
- [ ] `YANDEX_CLOUD_FOLDER_ID` задан

**2. Файл**
- [ ] Файл существует (`os.path.exists`)
- [ ] Размер < 1 МБ (для Sync API)
- [ ] Формат поддерживается (ogg/mp3/wav)
- [ ] Файл не повреждён (`ffprobe` успешно)

**3. Сеть**
- [ ] Интернет работает
- [ ] API endpoint доступен
- [ ] Нет firewall блокировок

**4. ffmpeg**
- [ ] ffmpeg установлен
- [ ] Доступен в PATH
- [ ] Версия актуальная

**5. Логи**
- [ ] Включено логирование
- [ ] Читаешь ошибки полностью (не только status code)

---

## Полезные команды

### Проверка аудио

```bash
# Информация о файле
ffprobe -v quiet -print_format json -show_format audio.ogg

# Длительность
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.ogg

# Формат
ffprobe -v quiet -show_entries format=format_name -of default=noprint_wrappers=1:nokey=1 audio.ogg
```

### Конвертация форматов

```bash
# OGG → MP3
ffmpeg -i audio.ogg -c:a libmp3lame audio.mp3

# MP3 → OGG
ffmpeg -i audio.mp3 -c:a libopus audio.ogg

# Любой → WAV (для LPCM)
ffmpeg -i audio.ogg -f s16le -ar 16000 -ac 1 audio.raw
```

### Тестирование API

```bash
# curl тест
curl -X POST \
  "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId=b1gvu3q8k1kafqd3sk5f&lang=ru-RU&format=oggopus" \
  -H "Authorization: Api-Key YOUR_API_KEY" \
  --data-binary "@audio.ogg"
```

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/speechkit-basics.md` | Основы API, форматы, аутентификация |
| `references/error-handling.md` | Retry логика, fallback стратегии |
| `references/long-audio-handling.md` | Обработка длинных файлов |
| `references/performance-optimization.md` | Оптимизация скорости и стоимости |

---

## Получение помощи

**Официальные каналы:**
- Документация: https://cloud.yandex.ru/docs/speechkit/
- Техподдержка: https://console.cloud.yandex.ru/support

**Сообщество:**
- Telegram: @yandexcloud
- GitHub Issues: https://github.com/yandex-cloud/docs/issues

**Логи для support:**
```python
# При обращении в support приложите:
# 1. Request ID (из заголовков ответа)
# 2. Timestamp
# 3. Размер и формат файла
# 4. Полный текст ошибки

import json
from datetime import datetime

def create_support_report(audio_path: str, error: Exception):
    """Создание отчёта для support."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "file": {
            "path": audio_path,
            "size": os.path.getsize(audio_path),
            "format": detect_audio_format(audio_path)
        },
        "error": {
            "type": type(error).__name__,
            "message": str(error)
        },
        "env": {
            "api_key_present": bool(os.getenv("YANDEX_CLOUD_API_KEY")),
            "folder_id": os.getenv("YANDEX_CLOUD_FOLDER_ID")
        }
    }

    with open("support_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Отчёт сохранён: support_report.json")
```

---

## Emergency Checklist

Когда ничего не помогает:

1. **Restart from scratch**
   ```bash
   # Пересоздай .env
   # Получи новый API ключ
   # Проверь ffmpeg
   ```

2. **Test с минимальным примером**
   ```python
   # Самый простой код
   import requests
   import os

   response = requests.post(
       "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
       params={
           "folderId": "b1gvu3q8k1kafqd3sk5f",
           "lang": "ru-RU",
           "format": "oggopus"
       },
       headers={"Authorization": "Api-Key YOUR_KEY"},
       data=open("test.ogg", "rb")
   )
   print(response.json())
   ```

3. **Fallback на Whisper**
   ```python
   # Если SpeechKit не работает
   import openai
   client = openai.OpenAI()
   with open("audio.ogg", "rb") as f:
       transcript = client.audio.transcriptions.create(
           model="whisper-1", file=f
       )
   print(transcript.text)
   ```

4. **Обратись за помощью**
   - Техподдержка Yandex Cloud
   - Сообщество в Telegram
   - GitHub Issues
