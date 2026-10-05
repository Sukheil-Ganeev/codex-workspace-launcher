# Паттерн: Деление длинных аудио на части

**Дата:** 2026-02-04
**Тип:** Pattern
**Severity:** HIGH
**Теги:** `audio-processing`, `api-limits`, `chunking`, `yandex-speechkit`

---

## Проблема

Yandex SpeechKit Sync API имеет жёсткий лимит **30 секунд** на аудиофайл.

**Реальные данные из практики:**
- Всего аудиофайлов: 27
- Короткие (<30 сек): 12 (44%)
- Длинные (>30 сек): 15 (56%)
- Самое длинное: 138.88 сек (в 4.6 раз больше лимита)

**Результат без деления:** 56% потери данных — критично для бизнеса!

---

## Решение: Автоматическое деление на части

### Паттерн

```python
def transcribe_with_splitting(audio_path: str) -> str:
    """
    Универсальная транскрипция с автоматическим делением.

    Логика:
    - Если ≤29 сек → прямая транскрипция
    - Если >29 сек → делим на части по 29 сек → транскрибируем каждую → склеиваем
    """
    duration = get_duration(audio_path)

    if duration <= 29.0:
        # Короткое аудио - прямая обработка
        return transcribe_direct(audio_path)
    else:
        # Длинное аудио - деление на части
        chunks = split_audio(audio_path, chunk_duration=29.0)
        transcripts = [transcribe_direct(chunk) for chunk in chunks]
        return " ".join(transcripts)
```

### Ключевые моменты

1. **Порог 29 сек (не 30!)** — оставляем запас на погрешности кодирования
2. **Деление без перекодирования** — используем `ffmpeg -c copy` для скорости
3. **Склеивание текста** — простой `" ".join()`, естественные паузы сохраняются

### Реализация через ffmpeg

```bash
# Деление на части по 29 сек
ffmpeg -i long_audio.ogg \
  -f segment \
  -segment_time 29 \
  -c copy \
  output_%03d.ogg
```

---

## Результаты

### До внедрения (v1)
```
✅ Успешно: 12 (44%)
⚠️ Пропущено: 15 (56%)
```

### После внедрения (v2)
```
✅ Успешно: 27 (100%)
⚠️ Пропущено: 0
```

**Улучшение:** С 44% до 100% успешной обработки (+127% эффективности)

---

## Когда применять

**Применяй всегда** для обработки голосовых из WhatsApp/Telegram:
- ✅ Неизвестная длительность файлов
- ✅ Пользовательский контент (может быть любой длины)
- ✅ Критичность каждого сообщения для бизнеса

**Не применяй** если:
- ❌ Гарантированно короткие файлы (<20 сек)
- ❌ Используешь Async API (нет лимита 30 сек)

---

## Альтернативы

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Деление на части** | 100% покрытие, быстро | Небольшое усложнение кода |
| Async API | Без лимита длины | Долгое ожидание (минуты), сложнее |
| Обрезка до 30 сек | Просто | Потеря данных! |
| Пропуск длинных | Очень просто | 56% потери — неприемлемо |

**Вывод:** Деление на части — оптимальный баланс простоты и покрытия.

---

## Код из практики

```python
# Реальный код из transcribe_skipped_only.py
def split_audio_to_chunks(audio_path: str, chunk_duration: int = 29) -> list:
    """Делит аудио на части по N секунд"""
    duration = get_audio_duration(audio_path)

    if duration <= chunk_duration:
        return [audio_path]  # Уже короткое

    chunks = []
    num_chunks = math.ceil(duration / chunk_duration)

    for i in range(num_chunks):
        chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
        start_time = i * chunk_duration

        subprocess.run([
            'ffmpeg', '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-c', 'copy',  # Без перекодирования!
            chunk_path, '-y'
        ], capture_output=True)

        chunks.append(chunk_path)

    return chunks
```

---

## Связанные записи

- `improvements/universal-audio-processing.md` — универсальный процессор
- `fixes/30sec-limit-workaround.md` — обход лимита API
