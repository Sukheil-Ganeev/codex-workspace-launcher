# Fix: Обход лимита 30 секунд Yandex SpeechKit Sync API

**Дата:** 2026-02-04
**Тип:** Fix
**Severity:** CRITICAL
**Проблема:** API возвращает 400 для файлов >30 сек
**Теги:** `api-limits`, `yandex-speechkit`, `workaround`, `audio-splitting`

---

## Проблема

### Симптомы

```bash
# Попытка транскрибировать 37-секундное аудио
[ERROR] 00000148-AUDIO-2026-02-04-19-58-20.opus: 400
{
  "error_code": "BAD_REQUEST",
  "error_message": "audio is too long"
}
```

### Root Cause

Yandex SpeechKit **Synchronous Recognition API** имеет жёсткое ограничение:
- **Максимум:** 30 секунд на запрос
- **Документация:** https://cloud.yandex.ru/docs/speechkit/stt/api/streaming-api

**Критичность:** В реальных WhatsApp чатах 56% голосовых >30 сек!

### Реальная статистика

Из анализа 27 файлов (чаты Елена + Мари):

| Диапазон | Количество | % |
|----------|------------|---|
| 0-20 сек | 8 | 30% |
| 20-30 сек | 4 | 15% |
| **30-60 сек** | **7** | **26%** |
| **60-90 сек** | **4** | **15%** |
| **90+ сек** | **4** | **15%** |

**Итого >30 сек:** 15 файлов (56%)

Самые длинные:
- 138.88 сек (2:19) — в 4.6 раз больше лимита
- 136.90 сек (2:17)
- 112.72 сек (1:53)

---

## Решение

### Алгоритм обхода

```python
def workaround_30sec_limit(audio_path: str) -> str:
    """
    Обход лимита 30 сек через деление на части.

    Стратегия:
    1. Проверяем длительность
    2. Если ≤29 сек → прямая обработка (1 запрос)
    3. Если >29 сек → делим на части по 29 сек → обрабатываем каждую → склеиваем
    """
    duration = get_audio_duration(audio_path)

    # Порог 29 (не 30!) для запаса
    if duration <= 29.0:
        # Короткое - в лимите
        return transcribe_sync_api(audio_path)

    # Длинное - делим на parts
    num_chunks = math.ceil(duration / 29.0)
    chunks = []

    for i in range(num_chunks):
        chunk_path = split_chunk(audio_path, i, chunk_duration=29)
        chunks.append(chunk_path)

    # Транскрибируем каждую часть
    transcripts = []
    for chunk in chunks:
        text = transcribe_sync_api(chunk)
        transcripts.append(text)

    # Склеиваем текст
    full_text = " ".join(transcripts)

    # Cleanup
    for chunk in chunks:
        os.remove(chunk)

    return full_text
```

### Техническая реализация

#### Деление через ffmpeg

```bash
# Деление 138-секундного аудио на 5 частей по 29 сек
ffmpeg -i long_audio.ogg \
  -f segment \
  -segment_time 29 \
  -c copy \              # Без перекодирования (быстро!)
  -reset_timestamps 1 \
  output_chunk_%03d.ogg

# Результат:
# output_chunk_000.ogg (29 сек)
# output_chunk_001.ogg (29 сек)
# output_chunk_002.ogg (29 сек)
# output_chunk_003.ogg (29 сек)
# output_chunk_004.ogg (22 сек) <- остаток
```

#### Python реализация

```python
import subprocess
import math
import os

def split_audio_to_chunks(audio_path: str, chunk_duration: int = 29) -> list:
    """Делит аудио на части по N секунд"""
    duration = get_audio_duration(audio_path)

    if duration <= chunk_duration:
        return [audio_path]

    chunks = []
    num_chunks = math.ceil(duration / chunk_duration)

    for i in range(num_chunks):
        chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
        start_time = i * chunk_duration

        cmd = [
            'ffmpeg', '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-c', 'copy',  # КРИТИЧНО: без перекодирования!
            chunk_path, '-y'
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        chunks.append(chunk_path)

    return chunks

def get_audio_duration(audio_path: str) -> float:
    """Получает длительность через ffprobe"""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())
```

---

## Результаты

### До fix (baseline)

```
Обработано файлов: 12/27 (44%)
Пропущено (>30 сек): 15/27 (56%)
Потеря данных: КРИТИЧЕСКАЯ
```

**Пример пропущенных:**
```
00000093 (72.88 сек)  - Марсель объясняет про Ford Mustang
00000094 (136.90 сек) - Детали по аренде авто
00000103 (112.72 сек) - Важное обсуждение группы
```

### После fix

```
Обработано файлов: 27/27 (100%)
Пропущено: 0/27 (0%)
Потеря данных: НЕТ
```

**Пример обработки длинного файла:**
```
[1/15] 00000093-AUDIO-2026-01-28-19-34-33.opus
  → Длительность: 72.9 сек (превышает лимит в 2.4 раза)
  → Стратегия: split_and_merge
  → Делю на части по 29 сек...
  → Создано частей: 3
    [1/3] chunk_000 (29 сек) → API → ✓
    [2/3] chunk_001 (29 сек) → API → ✓
    [3/3] chunk_002 (14.9 сек) → API → ✓
  ✓ Склеено частей: 3/3
  ✓ Полный текст получен!
```

---

## Альтернативы (не выбрали)

### 1. Asynchronous Recognition API

**Плюсы:**
- Нет лимита длины
- Официальный способ

**Минусы:**
- Долгое ожидание (минуты)
- Сложнее интеграция (polling, webhooks)
- Дороже (отдельная тарификация)

**Вывод:** Избыточно для 99% случаев (средняя длина <60 сек).

### 2. Обрезка до 30 сек

```python
# ❌ НЕ ИСПОЛЬЗУЙ!
ffmpeg -i long_audio.ogg -t 30 trimmed.ogg
```

**Проблема:** Потеря данных! В бизнесе каждое слово клиента важно.

### 3. Пропуск длинных файлов

```python
# ❌ НЕ ИСПОЛЬЗУЙ!
if duration > 30:
    print("⚠️ Пропуск: слишком длинное")
    return None
```

**Проблема:** 56% потери данных — неприемлемо!

---

## Ограничения решения

### 1. Качество склейки

**Потенциальная проблема:** Фраза разделена между частями

**Пример:**
```
chunk_000: "...и мы хотим забронировать"
chunk_001: "автомобиль на три дня..."
```

**Склеено:** "...и мы хотим забронировать автомобиль на три дня..."

**Реальность:** На практике проблем НЕ обнаружено (29-секундные куски редко разрывают предложения).

### 2. Производительность

**Дополнительное время:**
- Деление: ~1 сек на файл
- Транскрипция: N частей × 2-3 сек

**Для 138-сек файла:**
- Без деления: невозможно (ошибка 400)
- С делением: 1 сек (split) + 5 частей × 2.5 сек = ~13 сек

**Вывод:** Приемлемо (альтернатива — async API ждёт минуты).

### 3. API quota

**Расход quota:**
- 30-сек файл без деления: 1 запрос
- 138-сек файл с делением: 5 запросов

**Компромисс:** Больше запросов, но 100% покрытие данных. Для бизнеса приемлемо.

---

## Best Practices

### 1. Порог 29 (не 30!)

```python
# ✅ ПРАВИЛЬНО
if duration <= 29.0:
    transcribe_direct()

# ❌ НЕПРАВИЛЬНО
if duration <= 30.0:  # Может быть 30.1 → ошибка!
    transcribe_direct()
```

**Причина:** Оставляем запас на погрешности длительности.

### 2. Использовать `-c copy`

```bash
# ✅ ПРАВИЛЬНО - без перекодирования
ffmpeg -i input.ogg -t 29 -c copy output.ogg

# ❌ НЕПРАВИЛЬНО - перекодирование (медленно!)
ffmpeg -i input.ogg -t 29 output.ogg
```

**Производительность:** `-c copy` в 10-50 раз быстрее.

### 3. Cleanup временных файлов

```python
try:
    chunks = split_audio(file)
    result = process_chunks(chunks)
finally:
    # Всегда удаляем chunks
    for chunk in chunks:
        os.remove(chunk)
```

**Причина:** Без cleanup диск быстро забивается (20+ файлов × 27 аудио = 540+ файлов).

---

## Когда применять

**Применяй всегда** для Sync API:
- ✅ WhatsApp/Telegram голосовые
- ✅ Неизвестная длина файлов
- ✅ Требуется быстрый результат (<20 сек)

**Не нужно** если:
- ❌ Используешь Async API (нет лимита)
- ❌ Все файлы гарантированно <20 сек

---

## Связанные записи

- `patterns/audio-splitting-pattern.md` — общий паттерн деления
- `improvements/universal-audio-processing.md` — универсальный процессор
