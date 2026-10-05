# Cheatsheet -- PuzzleBot Project

## Команды запуска

### Chat Analysis

```bash
# Полный pipeline
python pipelines/chat-analysis/run_pipeline.py

# Verbose (DEBUG-логи)
python pipelines/chat-analysis/run_pipeline.py --verbose

# Без pickle-кеша
python pipelines/chat-analysis/run_pipeline.py --skip-cache

# Только один шаг
python pipelines/chat-analysis/run_pipeline.py --only-step loader
python pipelines/chat-analysis/run_pipeline.py --only-step threads
python pipelines/chat-analysis/run_pipeline.py --only-step qa
python pipelines/chat-analysis/run_pipeline.py --only-step experts
python pipelines/chat-analysis/run_pipeline.py --only-step faq
python pipelines/chat-analysis/run_pipeline.py --only-step report
```

### Video-to-Knowledge

```bash
# Одно видео (локальный файл)
python pipelines/video-to-knowledge/video_to_knowledge.py input/video.mp4 --single

# Папка с видео
python pipelines/video-to-knowledge/video_to_knowledge.py input/

# YouTube URL
python pipelines/video-to-knowledge/video_to_knowledge.py "https://youtube.com/watch?v=XXX" --single

# Пакетная транскрипция
python pipelines/video-to-knowledge/transcribe_batch.py

# Валидация покрытия
python pipelines/video-to-knowledge/validate_coverage.py
```

### Telegram экспорт

```bash
# Полный экспорт группы
python scripts/telegram_exporter.py

# Экспорт конкретного топика
python scripts/telegram_exporter_topic.py 424978   # Взаимопомощь
python scripts/telegram_exporter_topic.py 425001   # Топик 2
python scripts/telegram_exporter_topic.py 425057   # Топик 3
```

## Структуры данных

### Message
```
id: int, date: str, text: str, reply_to: int|None,
topic_id: int|None, sender_id: int, media_type: str|None, media_file: str|None
```

### Thread
```
root_id: int, message_ids: list[int], participants: list[int],
depth: int, duration_seconds: int, topic_id: int|None
```

### QAPair
```
question_id: int, question_text: str, question_sender: int,
answer_id: int, answer_text: str, answer_sender: int,
topic_id: int|None, confidence: float
```

### Expert
```
sender_id: int, total_messages: int, answers_count: int,
questions_count: int, unique_topics: int, avg_answer_length: float,
helpfulness_score: float, first_seen: str, last_seen: str
```

### FAQEntry
```
category: str, question: str, answer: str,
source_question_id: int, source_answer_id: int, confidence: float
```

## Формулы

### Helpfulness Score (Expert)
```
helpfulness = answers_count * 2 + unique_topics * 3 + avg_answer_length / 100
```

### QA Confidence
```
1.0 -- вопрос с "?" + ответ > 100 символов
0.8 -- вопрос с "?" + ответ > 50 символов
0.5 -- все остальные
```

### SSIM Threshold Guide
```
0.85 -- динамичное видео (много переключений)
0.88 -- стандартный скринкаст (по умолчанию)
0.92 -- статичное видео (мало изменений)
```

## Параметры конфигурации

### Chat Analysis (config.py)

| Параметр | Значение | Описание |
|----------|---------|---------|
| `BASE_DIR` | `D:/Downloads/PuzzleBot-Project` | Корень проекта |
| `DATA_DIR` | `D:/Downloads/PuzzleBot-Project/data/telegram/full-export` | Входные данные |
| `MIN_TEXT_LENGTH` | 5 | Мин. длина текста для валидации |
| `QUESTION_MARKERS` | `["?"]` | Маркеры вопросов |

### Video-to-Knowledge (config.py)

| Параметр | Значение | Описание |
|----------|---------|---------|
| `whisper_model` | large-v3 | Модель транскрипции |
| `whisper_device` | cuda | Устройство (cuda/cpu) |
| `whisper_compute_type` | int8 | Квантизация |
| `ssim_threshold` | 0.88 | Порог изменения кадра |
| `min_interval` | 1.5 | Мин. интервал между кадрами (сек) |
| `max_interval` | 20 | Макс. интервал без кадров (сек) |
| `dedup_threshold` | 0.95 | Порог дедупликации |
| `stability_wait` | 0.5 | Ожидание стабилизации (сек) |
| `check_fps` | 2 | Частота проверки (кадров/сек) |
| `ocr_lang` | rus+eng | Языки OCR |
| `chapter_min_gap` | 3.0 | Пауза для новой главы (сек) |
| `chapter_min_length` | 60 | Мин. длина главы (сек) |

## Topic Mapping

| Topic ID | Название | Доля сообщений |
|----------|---------|---------------|
| 424978 | Взаимопомощь | ~92% |
| 425001 | Топик 2 | <3% |
| 425057 | Топик 3 | <2% |
| 425226 | Топик 4 | <1% |
| 425177 | Топик 5 | <1% |
| 425163 | Топик 6 | <1% |

## FAQ категории (ключевые слова)

```
Кнопки:       кнопк, клавиатур, инлайн
Оплата:       оплат, платёж, донат, pay
Рассылки:     рассылк, массов, broadcast
Переменные:   переменн, перем, variable
Настройка:    бот, создат, настрои, запуст
Интеграции:   webhook, api, интеграц, http
Сообщения:    текст, сообщен, ответ
Группы:       группа, канал, чат
Общие:        (по умолчанию)
```

## Question Starters (17)

```
как, почему, где, что, кто, когда, можно ли,
подскажите, помогите, а если, не могу, не работает,
ошибка, скажите, кто-нибудь, есть ли, возможно ли
```

## Выходные файлы

### Chat Analysis (output/chat-analysis/)
```
threads.json         -- цепочки диалогов
qa_pairs.json        -- пары вопрос-ответ
experts.json         -- эксперты с метриками
faq.json             -- FAQ по категориям
REPORT.md            -- аналитический отчёт
messages_cache.pkl   -- pickle-кеш
```

### Video-to-Knowledge (output/video-knowledge/videos/)
```
{NN_Video_Name}/
  {Video_Name}.md         -- Obsidian Markdown статья
  transcription.json      -- полная транскрипция (сегменты + timestamps)
  transcription.srt       -- субтитры SRT
  transcription.txt       -- чистый текст
  metadata.json           -- метаданные видео (ffprobe)
  frames_transcript.json  -- корреляция кадров с речью
  frames/                 -- извлечённые кадры (*.jpg)
    frames_index.json     -- индекс кадров (time, ssim, stats)
```

## Зависимости (pip install)

```bash
# Chat Analysis
pip install tqdm

# Video-to-Knowledge
pip install faster-whisper opencv-python scikit-image tqdm pytesseract yt-dlp

# GPU SSIM (опционально)
pip install kornia torch

# Telegram экспорт
pip install telethon
```

## Системные зависимости

```
Tesseract OCR 5   -- https://github.com/tesseract-ocr/tesseract
FFmpeg             -- https://ffmpeg.org/
CUDA Toolkit       -- https://developer.nvidia.com/cuda-toolkit (для GPU)
```

## Форматирование текста в конструкторе PuzzleBot

### ВАЖНО: как работает форматирование

PuzzleBot НЕ принимает HTML-теги как текст. Форматирование применяется
только через визуальный редактор:

1. Напиши чистый текст (без тегов)
2. Выдели нужный фрагмент мышкой
3. Нажми горячую клавишу или кнопку на панели
4. Текст станет жирным/курсивным визуально

### Горячие клавиши в редакторе

| Комбинация | Действие | Кнопка на панели |
|------------|----------|------------------|
| Ctrl+B | Жирный | B |
| Ctrl+I | Курсив | I |
| Ctrl+U | Подчёркнутый | U |
| Ctrl+Shift+S | Зачёркнутый | ~~S~~ |
| Ctrl+Shift+M | Моноширинный (код) | </> |
| Ctrl+K | Вставить ссылку | 🔗 |
| — | Надстрочный | ᴬᴮ |
| — | Подстрочный | ₐᵦ |
| — | Спойлер, цитата | ✱ (доп. меню) |

### Паттерн: карточка со скидками

Ниже — готовый текст для вставки в PuzzleBot.
Пометки [ЖИРНЫЙ] и [КУРСИВ] означают: выдели этот текст → примени формат.
Сами пометки после форматирования удали.

```
🎁 [ЖИРНЫЙ: Как получить скидки?]

📢 [ЖИРНЫЙ: Скидка 10%] — подпишитесь на канал @vipdxbrus
[КУРСИВ: Постоянная скидка, пока вы подписаны!] ♾

⭐ [ЖИРНЫЙ: Скидка 15%] — оставьте отзыв на Google Maps
[КУРСИВ: Одноразовый промокод на 30 дней] 🕐

👥 [ЖИРНЫЙ: Скидка 25%] — пригласите 3 друзей
[КУРСИВ: Промокод на 30 дней после приглашения 3 человек] 🎉

✨ [ЖИРНЫЙ: Скидки суммируются с баллами лояльности!]
```

### Порядок действий для Claude в Chrome

При форматировании текста в PuzzleBot через браузерную автоматизацию:
1. Вставить чистый текст без тегов в поле редактора
2. Для каждого фрагмента, который нужно сделать жирным:
   — выделить текст (click + shift+click или drag)
   — нажать Ctrl+B
3. Для каждого фрагмента курсивом:
   — выделить текст
   — нажать Ctrl+I
4. Проверить результат визуально — теги не должны быть видны

---

## WSL2 Batch Processing

```bash
# Activate venv
source /mnt/d/Downloads/PuzzleBot-Project/venv/bin/activate

# Run all batches
cd /mnt/d/Downloads/PuzzleBot-Project/pipelines/video-to-knowledge/
for i in 4 5 6 7 8 9 10; do echo "=== BATCH $i ===" && python3 process_batch$i.py; done

# Run single batch
python3 process_batch10.py
```

## repair_outputs.py

```bash
python3 repair_outputs.py                    # fix all incomplete folders
python3 repair_outputs.py --dry-run          # preview only
python3 repair_outputs.py --folder 75        # fix one folder
python3 repair_outputs.py --no-regenerate-md # skip .md regeneration
python3 repair_outputs.py --verbose          # debug output
```

## Path Conversion (WSL <-> Windows)

| Windows | WSL |
|---------|-----|
| D:\Downloads\PuzzleBot-Project | /mnt/d/Downloads/PuzzleBot-Project |
| C:\Users\londo | /mnt/c/Users/londo |

## Batch Stats (2026-02-14)

| Batch | Videos | GPU Time | Total Frames | Total Segments |
|-------|--------|----------|-------------|---------------|
| 4 | 3 | 13 min | 56 | 221 |
| 5 | 10 | 25 min | 132 | 130 |
| 6 | 10 | 54 min | 333 | 730 |
| 7 | 10 | 76 min | 534 | 1332 |
| 8 | 10 | 110 min | 342 | 841 |
| 9 | 10 | 112 min | 244 | 705 |
| 10 | 31 | 187 min | 975 | 2159 |
