# STT Pipeline -- Speech-to-Text Architecture

> Справочник по системе распознавания речи VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Основной файл: `bot/transcriber.py`

---

## Общая архитектура

STT (Speech-to-Text) система построена на каскадном принципе: сначала пытается использовать локальную GPU-модель, при неудаче переключается на облачный API.

```
Audio File (.ogg)
    |
    v
Transcriber.transcribe(file_path)
    |
    +--[1] transcribe_local()  -- faster-whisper на GPU (CUDA)
    |       (пропускается если FORCE_GROQ_STT=true или faster-whisper не загружен)
    |
    +--[2] transcribe_groq()   -- Groq Whisper API (облако)
    |
    +--[X] RuntimeError если оба бэкенда упали
```

Обе функции выполняются в отдельном потоке через `asyncio.to_thread()`, чтобы не блокировать event loop.

---

## Класс Transcriber

```python
# bot/transcriber.py

class Transcriber:
    def __init__(self) -> None:
        """Инициализация: загрузка модели faster-whisper (если доступна) и Groq клиента."""
        ...

    async def transcribe_local(self, file_path: str) -> TranscriptionResult:
        """Локальная транскрипция через faster-whisper на GPU."""
        ...

    async def transcribe_groq(self, file_path: str) -> TranscriptionResult:
        """Облачная транскрипция через Groq Whisper API."""
        ...

    async def transcribe(self, file_path: str) -> TranscriptionResult:
        """Главный метод: каскад local -> groq."""
        ...
```

---

## Результат транскрипции

```python
@dataclass
class TranscriptionResult:
    text: str                        # Распознанный текст
    language: str                    # Обнаруженный язык ("ru", "en", "ar")
    duration: float                  # Длительность аудио в секундах
    method: str                      # "local" или "groq"
    confidence: float | None = None  # 0.0-1.0 (None для Groq)
```

---

## Primary: faster-whisper (Локальная GPU)

### Инициализация модели

```python
from faster_whisper import WhisperModel

self._model = WhisperModel(
    config.WHISPER_MODEL,      # default: "large-v3"
    device=config.WHISPER_DEVICE,  # default: "cuda"
    compute_type="float16" if device == "cuda" else "int8",
)
```

### Параметры модели

| Параметр | Значение | Описание |
|----------|----------|----------|
| `model` | `large-v3` | Лучшая модель для русского/английского/арабского |
| `device` | `cuda` | NVIDIA GPU через CUDA |
| `compute_type` | `float16` (GPU) / `int8` (CPU) | Точность вычислений |
| `beam_size` | `5` | Ширина луча для beam search |
| `language` | `None` | Автоопределение языка |

### Вызов транскрипции

```python
segments, info = self._model.transcribe(
    file_path,
    beam_size=5,
    language=None,  # автодетект
)

# Сбор текста из сегментов
text = " ".join(segment.text for segment in segments_list)
```

### Расчёт уверенности (confidence)

```python
avg_logprob = sum(s.avg_logprob for s in segments) / len(segments)
confidence = math.exp(avg_logprob)   # log-prob -> probability
confidence = max(0.0, min(1.0, confidence))  # clamp [0.0, 1.0]
```

Интерпретация:
- `>= 0.85` -- высокая уверенность (зелёный индикатор)
- `>= 0.70` -- средняя уверенность (жёлтый индикатор)
- `< 0.70` -- низкая уверенность (красный индикатор)

### Метод (method string)

Возвращает `"local"`.

---

## Fallback: Groq Whisper API

### Инициализация клиента

```python
from groq import Groq

self._groq_client = Groq(api_key=config.GROQ_API_KEY)
```

### Вызов API

```python
response = self._groq_client.audio.transcriptions.create(
    file=("audio.ogg", f),
    model="whisper-large-v3",
    response_format="verbose_json",
)
```

### Особенности Groq API

| Параметр | Значение |
|----------|----------|
| Модель | `whisper-large-v3` |
| Формат ответа | `verbose_json` (включает длительность и язык) |
| Confidence | `None` (API не возвращает confidence) |
| Лимит файла | ~25 MB |
| Скорость | ~10-50x быстрее реального времени |
| Стоимость | Бесплатный tier (на момент v4.3) |

### Метод (method string)

Возвращает `"groq"`.

---

## Логика выбора бэкенда

| Сценарий | Используемый бэкенд |
|----------|---------------------|
| GPU доступен, faster-whisper загружен | **local** (primary) |
| `FORCE_GROQ_STT=true` в .env | **groq** (local полностью пропущен) |
| faster-whisper не удалось импортировать/загрузить | **groq** (fallback) |
| Локальная транскрипция выбросила исключение | **groq** (fallback) |
| Оба бэкенда упали | `RuntimeError` (pipeline записывает error) |

---

## Флаг FORCE_GROQ_STT

### Назначение

Принудительное использование облачного Groq API вместо локальной модели. Критически важен для серверного развёртывания на ARM-процессорах (Oracle Cloud), где нет GPU.

### Настройка

В файле `.env`:
```
FORCE_GROQ_STT=true
```

### Парсинг в коде

```python
# bot/config.py
FORCE_GROQ_STT = os.environ.get("FORCE_GROQ_STT", "").lower() in ("true", "1", "yes")
```

Принимает значения: `true`, `1`, `yes` (case-insensitive).

### Когда использовать

| Окружение | FORCE_GROQ_STT | Причина |
|-----------|----------------|---------|
| Windows + RTX 3060 | `false` (default) | Есть GPU, local быстрее |
| Oracle Cloud ARM | `true` | Нет GPU, CPU-транскрипция слишком медленная |
| CI/CD тесты | `true` | Нет GPU в CI |
| Любой сервер без GPU | `true` | Экономия CPU, быстрее |

---

## Автоматическое определение языка

Оба бэкенда автоматически определяют язык аудио:

- **faster-whisper**: `info.language` из метаданных после транскрипции (ISO 639-1 код)
- **Groq API**: `response.language` из verbose_json ответа

Поддерживаемые языки (основные для бота):
- `ru` -- русский
- `en` -- английский
- `ar` -- арабский

Язык используется далее в pipeline для:
1. Определения необходимости перевода (`needs_translation()`)
2. Записи в БД (поле `language`)
3. Статистики по языкам

---

## Обработка аудиоформатов

### Входной формат

Telegram отправляет голосовые сообщения в формате OGG Opus (`.ogg`). WhatsApp также использует OGG.

### Путь временного файла

```python
temp_path = os.path.join(config.TEMP_DIR, f"voice_{user_id}_{timestamp}.ogg")
```

### Поддерживаемые форматы

faster-whisper и Groq API принимают большинство аудиоформатов:
- OGG (Opus) -- основной для мессенджеров
- WAV, MP3, FLAC, M4A -- для видео-транскрипции
- MP3 192kbps -- для извлечённого из видео аудио

### Очистка

Временные файлы удаляются в `finally` блоке обработчика:
```python
try:
    result = await process_voice(audio_path, ...)
finally:
    if os.path.exists(audio_path):
        os.remove(audio_path)
```

---

## Retry механизм

Транскрипция обёрнута в `retry_async()`:

```python
from core.retry import retry_async

tr_result = await retry_async(
    services.transcriber.transcribe,
    audio_path,
    max_retries=2,
    backoff_base=1.0,
)
```

| Попытка | Задержка |
|---------|----------|
| 0 (первая) | -- |
| 1 (первый retry) | 1.0 сек |
| 2 (второй retry) | 2.0 сек |

Итого: до 3 попыток (1 оригинальная + 2 retry).

---

## Интеграция с pipeline

### Вызов из process_voice()

```python
# core/pipeline.py

async def process_voice(
    audio_path: str,
    user_id: int,
    platform: str = "telegram",
    method_prefix: str = "",
    progress_callback = None,
) -> PipelineResult:

    # Шаг 1: STT
    tr_result = await retry_async(
        services.transcriber.transcribe,
        audio_path,
        max_retries=2,
    )

    result.transcription = tr_result.text
    result.language = tr_result.language
    result.duration = tr_result.duration
    result.method = method_prefix + tr_result.method  # "local", "groq", "video_local", etc.
    result.confidence = tr_result.confidence
    result.tr_result = tr_result
```

### Видео-транскрипция

Для видео аудио извлекается через yt-dlp в MP3, затем вызывается тот же `process_voice()` с `method_prefix="video_"`:

```python
result = await process_voice(mp3_path, user_id, method_prefix="video_")
# result.method будет "video_local" или "video_groq"
```

---

## Диктовка (Dictation Mode)

Если длительность аудио > 180 секунд (3 минуты), pipeline активирует режим диктовки:

```python
DICTATION_THRESHOLD = 180  # секунд

if tr_result.duration > DICTATION_THRESHOLD:
    result.is_dictation = True
    # Пропускается: summarization (шаг 5)
    # Остальные шаги выполняются
```

---

## Детекция дубликатов

После STT проверяется дубликат по длительности аудио:

```python
is_dup = await services.db.find_duplicate(user_id, tr_result.duration, within_seconds=60)
```

Если дубликат найден (аудио той же длительности от того же юзера за последние 60 секунд), логируется предупреждение, но pipeline продолжает работу.

---

## Конфигурация (.env переменные)

| Переменная | Default | Описание |
|------------|---------|----------|
| `GROQ_API_KEY` | `""` | API ключ Groq (обязательный) |
| `WHISPER_MODEL` | `"large-v3"` | Модель faster-whisper |
| `WHISPER_DEVICE` | `"cuda"` | Устройство: `cuda` или `cpu` |
| `FORCE_GROQ_STT` | `false` | Принудительно использовать Groq |

### Вычисляемые значения

```python
compute_type = "float16" if WHISPER_DEVICE == "cuda" else "int8"
```

---

## Модели в кодовой базе

| Компонент | Model ID | Файл |
|-----------|----------|------|
| faster-whisper local | `config.WHISPER_MODEL` (default `large-v3`) | `bot/transcriber.py` |
| Groq STT cloud | `whisper-large-v3` (hardcoded) | `bot/transcriber.py` |

---

## Паттерн "Shared Transcriber"

`Transcriber` -- синглтон в `core/services.py`:

```python
# core/services.py
transcriber: Transcriber | None = None

async def init_services():
    global transcriber
    transcriber = Transcriber()
```

Все модули обращаются к нему через `services.transcriber`:

```python
import core.services as services
tr_result = await services.transcriber.transcribe(file_path)
```

---

## Обработка ошибок

| Ситуация | Поведение |
|----------|-----------|
| STT оба бэкенда упали | `RuntimeError`, pipeline записывает `result.error`, возвращает result |
| STT вернул пустой текст | `result.error = "Empty transcription"`, ранний возврат |
| GPU недоступен при старте | Логирование warning, автопереключение на Groq |
| Файл повреждён | Исключение перехватывается retry, при провале -- fallback на Groq |
| Groq API rate limit | Retry с backoff (1s, 2s) |

---

## Требования к окружению

### Для локальной GPU-модели

- NVIDIA GPU с CUDA поддержкой (минимум GTX 1070, рекомендуется RTX 3060+)
- CUDA Toolkit 11.8+ или 12.x
- cuDNN 8.x
- `faster-whisper >= 1.2.0` в `requirements.txt`
- ~6 GB VRAM для модели `large-v3` с `float16`

### Для облачного Groq API

- Интернет-подключение
- Валидный `GROQ_API_KEY`
- `groq >= 1.0.0` в `requirements.txt`
- Бесплатный tier: достаточно для малого/среднего бизнеса

### Для серверного развёртывания

- `FORCE_GROQ_STT=true` в `.env`
- `requirements-server.txt` (без `faster-whisper`)
- Нет требований к GPU
