---
name: puzzlebot-project
description: "Полный проект анализа Telegram-сообщества PuzzleBot. Транскрипция видео, извлечение кадров, OCR, анализ чатов, Q&A, FAQ, скоринг экспертов, экспорт Telegram. Триггеры: puzzlebot, транскрибировать видео, извлечь кадры, анализ чата, FAQ из telegram, обработать видео, экспорт telegram"
---
# PuzzleBot Project

Проект для анализа Telegram-сообщества PuzzleBot и конвертации видео-туториалов в структурированную базу знаний. Два основных pipeline: Chat Analysis (анализ чатов) и Video-to-Knowledge (обработка видео).

## Обзор проекта

**Цель:** Извлечь полезные знания из трёх источников:
1. Сообщения Telegram-форума PuzzleBot (68,659 сообщений из 3 топиков) -- FAQ, Q&A-пары, рейтинг экспертов
2. Видео-туториалы -- транскрипции, ключевые кадры, OCR, Obsidian-статьи
3. Community-статьи Telegram-канала (47 статей от 9 авторов) -- Obsidian-статьи, каталог, кросс-ссылки

**Структура проекта:**

```
PuzzleBot-Project/
  pipelines/
    chat-analysis/       # Pipeline 1: анализ чатов (8 модулей)
    video-to-knowledge/  # Pipeline 2: обработка видео (6+ скриптов)
  scripts/               # Экспорт из Telegram (Telethon)
  data/                  # Входные данные (messages.json, видео)
  output/                # Результаты всех pipeline
    video-knowledge/
      community-articles/  # 47 community-статей (Pipeline 3)
  docs/research/         # Исследования (Whisper, SSIM, OCR)
  skill/                 # Этот скилл
```

## Pipeline 1: Chat Analysis

Анализ экспортированных сообщений Telegram-форума. 6 последовательных этапов, оркестрируемых `run_pipeline.py`.

### Архитектура

```
config.py           Конфигурация (пути, топики, эвристики)
    |
loader.py           messages.json -> list[Message]  (валидация, кеш)
    |
thread_builder.py   Построение цепочек (BFS) -> list[Thread]
    |
qa_extractor.py     Извлечение Q&A -> list[QAPair]
    |
expert_scorer.py    Скоринг экспертов -> list[Expert]
    |
faq_generator.py    Категоризация FAQ -> list[FAQEntry]
    |
report_generator.py Markdown-отчёт -> REPORT.md
```

### Модули

**config.py** -- центральная конфигурация:
- Пути: `BASE_DIR`, `DATA_DIR`, `OUTPUT_DIR`, `MESSAGES_FILE`, `CACHE_FILE`
- Topic mapping: 6 топиков форума PuzzleBot (`TOPIC_MAP`, `TOPIC_IDS`)
- Эвристики вопросов: `MIN_TEXT_LENGTH=5`, `QUESTION_MARKERS=["?"]`, 17 стартеров (`QUESTION_STARTERS`)
- Логирование: `setup_logging(verbose)` -- INFO или DEBUG

**loader.py** -- загрузка и валидация:
- Вход: `data/telegram/full-export/messages.json` (Telegram Desktop export, ~7 MB, ~61,000 записей)
- Критическая проверка: `reply_to in TOPIC_IDS` -> `reply_to = None` (корневое сообщение, не ответ)
- Pickle-кеш (`messages_cache.pkl`) -- повторная загрузка ~0.5 сек вместо ~2 сек
- Функции: `load_messages()`, `build_index()`, `get_stats()`

**thread_builder.py** -- цепочки диалогов (BFS):
- Построение `children: dict[int, list[int]]`
- BFS от каждого корневого сообщения
- Метрики: размер, глубина, участники, длительность
- Сироты (reply_to -> несуществующее сообщение) -- одиночные цепочки

**qa_extractor.py** -- извлечение Q&A:
- Определение вопросов: `"?"` в тексте или начало с вопросительных слов/фраз
- Лучший ответ = самый длинный валидный (>50 символов, не вопрос, другой отправитель)
- Confidence: 1.0 (вопрос с "?" + ответ >100), 0.8 (>50), 0.5 (остальные)
- Дедупликация по нормализованному тексту

**expert_scorer.py** -- рейтинг экспертов:
- Метрики: answers_count, questions_count, unique_topics, avg_answer_length
- Формула: `helpfulness = answers_count * 2 + unique_topics * 3 + avg_answer_length / 100`

**faq_generator.py** -- 9 категорий FAQ:
- Кнопки и клавиатуры, Оплата и платежи, Рассылки, Переменные, Настройка бота, Интеграции, Сообщения и тексты, Группы и каналы, Общие вопросы
- Категоризация по ключевым словам в вопросе

**report_generator.py** -- Markdown-отчёт (7 секций):
- Обзор, Топики, Диалоги, Q&A, Эксперты, FAQ, Рекомендации

### Запуск Chat Analysis

```bash
# Полный pipeline
python pipelines/chat-analysis/run_pipeline.py

# С подробным логом
python pipelines/chat-analysis/run_pipeline.py --verbose

# Без pickle-кеша (перечитать JSON заново)
python pipelines/chat-analysis/run_pipeline.py --skip-cache

# Только конкретный шаг (loader/threads/qa/experts/faq/report)
python pipelines/chat-analysis/run_pipeline.py --only-step qa
```

### Выходные файлы (output/)

| Файл | Содержание |
|------|-----------|
| `threads.json` | Цепочки диалогов (root_id, message_ids, depth) |
| `qa_pairs.json` | Пары вопрос-ответ (question_text, answer_text, confidence) |
| `experts.json` | Эксперты с метриками (helpfulness_score) |
| `faq.json` | FAQ по категориям (category, question, answer) |
| `REPORT.md` | Аналитический отчёт (7 секций) |
| `messages_cache.pkl` | Pickle-кеш загруженных сообщений |

## Pipeline 2: Video-to-Knowledge

Конвертация видео-туториалов в структурированную базу знаний (Obsidian Markdown).

### Этапы обработки

1. **Скачивание видео** -- yt-dlp (YouTube, другие источники) или локальный файл
2. **Транскрипция** -- faster-whisper (large-v3, int8, CUDA/CPU)
3. **Извлечение кадров** -- адаптивный SSIM-алгоритм (GPU kornia или CPU scikit-image)
4. **OCR** -- Tesseract 5 (rus+eng) распознавание текста с экрана
5. **Определение глав** -- по паузам в речи (chapter_min_gap, chapter_min_length)
6. **Генерация Markdown** -- Obsidian-формат с frontmatter, главами, вложениями

### Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `config.py` | Конфигурация (Whisper, SSIM, OCR, главы) |
| `video_to_knowledge.py` | Основной скрипт pipeline |
| `adaptive_keyframes.py` | SSIM-извлечение кадров (CPU, scikit-image) |
| `adaptive_keyframes_gpu.py` | SSIM-извлечение кадров (GPU, kornia) |
| `transcribe_batch.py` | Пакетная транскрипция |
| `validate_coverage.py` | Валидация покрытия видео |
| `process_batch*.py` | Пакетная обработка (batch 2-5) |
| `repair_outputs.py` | Smart repair for incomplete output folders |
| `process_batch6.py` | Batch processing videos #40-#49 (10 videos) |
| `process_batch7.py` | Batch processing videos #50-#59 (10 videos) |
| `process_batch8.py` | Batch processing videos #60-#69 (10 videos) |
| `process_batch9.py` | Batch processing videos #70-#79 (10 videos) |
| `process_batch10.py` | Batch processing videos #80-#110 (31 videos) |

### Конфигурация Video-to-Knowledge

```python
CONFIG = {
    # Whisper
    "whisper_model": "large-v3",        # Модель транскрипции
    "whisper_device": "cuda",           # "cuda" или "cpu"
    "whisper_compute_type": "int8",     # Квантизация
    "whisper_language": "ru",
    "whisper_beam_size": 5,
    "whisper_vad_filter": True,         # Voice Activity Detection

    # Адаптивное извлечение кадров
    "check_fps": 2,                     # Частота проверки (кадров/сек)
    "ssim_threshold": 0.88,             # Порог значимого изменения
    "min_interval": 1.5,               # Мин. пауза между кадрами (сек)
    "max_interval": 20,                # Макс. пауза без кадров (сек)
    "dedup_threshold": 0.95,           # Порог дедупликации
    "stability_wait": 0.5,            # Ожидание стабилизации (сек)

    # OCR
    "ocr_enabled": True,
    "ocr_lang": "rus+eng",
    "ocr_min_text_length": 10,

    # Главы
    "chapter_min_gap": 3.0,            # Пауза для новой главы (сек)
    "chapter_min_length": 60,          # Мин. длина главы (сек)
}
```

### Адаптивный алгоритм SSIM

Разработан для скринкастов (стандартный FFmpeg scene detection не подходит):

1. Проверка кадров с частотой `check_fps` (2 раза/сек)
2. Вычисление SSIM с последним принятым кадром
3. Если `SSIM < ssim_threshold` -- обнаружено изменение
4. Проверка `min_interval` (защита от анимаций и скролла)
5. Stability check -- ожидание `stability_wait`, подтверждение стабилизации
6. `max_interval` -- принудительный кадр при долгой статике
7. Финальная дедупликация по `dedup_threshold`

GPU-версия использует kornia SSIM (быстрее на CUDA), CPU -- scikit-image. Выбор автоматический.

### Запуск Video-to-Knowledge

```bash
# Одно видео
python pipelines/video-to-knowledge/video_to_knowledge.py input/video.mp4 --single

# Папка с видео
python pipelines/video-to-knowledge/video_to_knowledge.py input/

# Пакетная транскрипция
python pipelines/video-to-knowledge/transcribe_batch.py

# Валидация покрытия
python pipelines/video-to-knowledge/validate_coverage.py

# Repair incomplete outputs
python3 repair_outputs.py --dry-run    # check what needs fixing
python3 repair_outputs.py              # fix everything
python3 repair_outputs.py --folder 75  # fix one folder
```

**Batch skip-if-exists logic:** Batch scripts have built-in skip logic:
- `frames_index.json` exists -> skip frame extraction
- `transcription.json` exists -> skip transcription
- This means re-running batches is safe and fast for already-processed videos

### Формат вывода (Obsidian Markdown)

```markdown
---
title: Название видео
source: URL или путь
duration: "1:48"
date_processed: 2026-01-15
tags: [bitrix24, admin]
---

# Название видео

## Глава 1: Введение (00:00 - 00:30)
Текст транскрипции...

![[frame_0010.jpg]]
*OCR: текст с экрана*

## Глава 2: Настройка (00:30 - 01:15)
...
```

## Community Articles

Третий источник данных проекта -- статьи из Telegram-канала PuzzleBot Сообщество. Посты от участников комьюнити: текстовые статьи, фото-инструкции, видео-заметки, интервью, кейсы. Обработаны и конвертированы в Obsidian Markdown.

### Статистика

| Метрика | Значение |
|---------|---------|
| Всего статей | 159 |
| Категорий | 10 |
| Уникальных авторов | 15+ |
| Типов контента | 5 (video-tutorial, photo-article, text-article, interview, case-study) |

### Структура папки

```
output/video-knowledge/community-articles/
  community_articles_catalog.json   # Машиночитаемый каталог (JSON)
  community_articles_index.md       # Obsidian-индекс с кросс-ссылками
  NN_Transliterated_Title/
    article.md                      # Markdown-статья (Obsidian frontmatter)
    frames/                         # Извлечённые кадры (если видео)
    images/                         # Фото из поста (если фото)
    frames_index.json / images_index.json  # Индекс с OCR
```

### Категории

| Категория | Кол-во |
|-----------|--------|
| Настройка бота | 20 |
| Маркетинг и кейсы | 5 |
| AI и нейросети | 4 |
| Мини-приложения | 4 |
| Кнопки и клавиатуры | 4 |
| Рассылки | 3 |
| Интервью | 3 |
| Переменные | 2 |
| Оплата и платежи | 1 |
| Интеграции | 1 |

### Pipeline добавления новых community-статей

1. Создать папку `NN_Transliterated_Title/` в `community-articles/`
2. Скопировать медиа (видео → корень, фото → `images/`)
3. Видео: извлечь кадры (`ffmpeg -i video.mp4 -vf fps=1 -q:v 2 frames/frame_%04d.jpg`)
4. OCR: Tesseract rus+eng на кадрах/фото
5. Создать `article.md` с Obsidian frontmatter
6. Обновить `community_articles_catalog.json` и `community_articles_index.md`

## Экспорт из Telegram

Два скрипта на Telethon для экспорта сообщений из группы PuzzleBot.

### telegram_exporter.py (полный экспорт)

Экспорт всех сообщений и медиа из всей группы:
- Группа: `PuzzleBot Сообщество` (ID: -1001488984670)
- Выход: `telegram_export/messages.json` + `telegram_export/media/`
- Параметры: `DOWNLOAD_MEDIA=True`, `TOPIC_ID=None` (все топики)

### telegram_exporter_topic.py (по топику)

Экспорт сообщений конкретного топика:

```bash
python scripts/telegram_exporter_topic.py 425001
python scripts/telegram_exporter_topic.py 425057
```

- Отдельная Telethon-сессия для каждого топика (без конфликтов)
- Выход: `telegram_export_topic_{ID}/`

## Структуры данных

### Chat Analysis

```python
# Message (frozen dataclass)
Message(id, date, text, reply_to, topic_id, sender_id, media_type, media_file)

# Thread
Thread(root_id, message_ids, participants, depth, duration_seconds, topic_id)

# QAPair
QAPair(question_id, question_text, question_sender,
       answer_id, answer_text, answer_sender, topic_id, confidence)

# Expert
Expert(sender_id, total_messages, answers_count, questions_count,
       unique_topics, avg_answer_length, helpfulness_score, first_seen, last_seen)

# FAQEntry
FAQEntry(category, question, answer, source_question_id, source_answer_id, confidence)
```

### Video-to-Knowledge

```python
# frames_index.json -- индекс извлечённых кадров
{
    "video": "path/to/video.mp4",
    "total_frames_checked": 216,
    "keyframes_saved": 15,
    "frames": [
        {
            "filename": "frame_0010.jpg",
            "time_sec": 5.0,
            "ssim_with_prev": 0.72,
            "ocr_text": "распознанный текст"
        }
    ]
}
```

## Параметры и эвристики

### SSIM (извлечение кадров)

| Параметр | Значение | Эффект |
|----------|---------|--------|
| `ssim_threshold` | 0.88 | Ниже = больше кадров. 0.85 для динамичного, 0.92 для статичного |
| `min_interval` | 1.5 сек | Защита от анимаций. Меньше = больше кадров из переходов |
| `max_interval` | 20 сек | Принудительный кадр. Меньше = больше кадров при статике |
| `dedup_threshold` | 0.95 | Финальная дедупликация. Выше = агрессивнее |
| `stability_wait` | 0.5 сек | Ожидание стабилизации. Больше = пропуск анимаций |
| `check_fps` | 2 | Частота проверки. Больше = точнее, но медленнее |

### Whisper (транскрипция)

| Параметр | Значение | Примечание |
|----------|---------|-----------|
| `whisper_model` | large-v3 | Лучшее качество для русского (WER ~5-8%) |
| `whisper_device` | cuda | CPU как fallback |
| `whisper_compute_type` | int8 | Баланс скорости/памяти (~5 GB VRAM) |
| `whisper_beam_size` | 5 | Стандарт. Больше = точнее, медленнее |
| `whisper_vad_filter` | True | Пропуск тишины |

### Эвристики вопросов (Chat Analysis)

**Question starters** (17 фраз): как, почему, где, что, кто, когда, можно ли, подскажите, помогите, а если, не могу, не работает, ошибка, скажите, кто-нибудь, есть ли, возможно ли

**Confidence scoring:**
- 1.0 -- вопрос с "?" + ответ > 100 символов
- 0.8 -- вопрос с "?" + ответ > 50 символов
- 0.5 -- все остальные

### FAQ категории (9)

| Категория | Ключевые слова |
|-----------|---------------|
| Кнопки и клавиатуры | кнопк, клавиатур, инлайн |
| Оплата и платежи | оплат, платёж, донат, pay |
| Рассылки | рассылк, массов, broadcast |
| Переменные | переменн, перем, variable |
| Настройка бота | бот, создат, настрои, запуст |
| Интеграции | webhook, api, интеграц, http |
| Сообщения и тексты | текст, сообщен, ответ |
| Группы и каналы | группа, канал, чат |
| Общие вопросы | (по умолчанию) |

## Зависимости

### Chat Analysis

```
tqdm                    # Прогресс-бары
```

Всё остальное -- стандартная библиотека Python: json, pickle, logging, dataclasses, collections, argparse, re, string, time, datetime, pathlib.

### Video-to-Knowledge

```
faster-whisper          # Транскрипция речи (CTranslate2)
opencv-python           # Работа с видео и кадрами
scikit-image            # SSIM-метрика (CPU-версия)
tqdm                    # Прогресс-бары
pytesseract             # OCR (обёртка над Tesseract)
yt-dlp                  # Скачивание видео
```

Опционально:
```
kornia                  # GPU SSIM (через adaptive_keyframes_gpu.py)
torch                   # Для kornia
```

Системные:
- **Tesseract OCR 5** -- установка отдельно, языки `rus` и `eng`
- **FFmpeg** -- для yt-dlp и обработки видео

### Telegram экспорт

```
telethon                # Telegram API клиент
```

## Критические ловушки

### 1. reply_to == topic_id (Chat Analysis)

В Telegram-экспорте корневые сообщения топика имеют `reply_to`, указывающий на ID самого топика. Без проверки `reply_to in TOPIC_IDS` все корневые сообщения ошибочно объединяются в одну гигантскую цепочку из тысяч сообщений.

**Решение (loader.py):**
```python
if raw_reply_to is not None and raw_reply_to in TOPIC_IDS:
    reply_to = None  # корневое сообщение, а не реальный ответ
```

### 2. Telegram FloodWait

При массовом экспорте Telegram выдаёт FloodWaitError. Telethon обрабатывает автоматически (ждёт указанное время), но на полный экспорт группы может уйти 15-30 минут из-за пауз.

### 3. Кириллица в путях (Windows)

`cv2.VideoCapture()` и `cv2.imread()` не работают с кириллическими путями на Windows. Решение: использовать `numpy.fromfile()` + `cv2.imdecode()` или переименовать файлы в ASCII.

### 4. Pickle-кеш и изменение структур

При изменении полей dataclass `Message` старый `messages_cache.pkl` станет несовместимым. Запуск с `--skip-cache` обязателен после изменения структуры.

### 5. Whisper: GPU fallback

Если CUDA недоступна или не хватает VRAM, `get_whisper_model()` автоматически переключается на CPU. Скорость падает в ~10 раз (large-v3 на CPU: ~1x realtime вместо ~10x).

### 6. SSIM: слишком много или мало кадров

- Слишком много: повысить `ssim_threshold` (0.88 -> 0.92), увеличить `min_interval`
- Слишком мало: понизить `ssim_threshold` (0.88 -> 0.85), уменьшить `max_interval`

### 7. UTF-8 в JSON-выгрузке

Telegram Desktop экспорт иногда содержит невалидные символы. `json.load()` с `encoding="utf-8"` обычно справляется, но при ошибках используйте `errors="replace"`.

### 8. Видео без звука

Если видео не содержит аудиодорожки, faster-whisper выбросит исключение. Обработка: пропуск этапа транскрипции, только кадры + OCR.

### 9. Topic mapping неполный

Если в TOPIC_MAP не указаны все реальные топики форума, часть корневых сообщений будет ошибочно помечена как ответы. Проверяйте JSON-экспорт на наличие новых topic_id.

### 10. WSL Path Bug in Batch Scripts

Batch scripts (process_batch*.py) hardcode Windows paths (D:/Downloads/...) for source and output_dir. Functions like `extract_frames()`, `transcribe_video()`, `generate_summary_md()` call `to_native_path()` internally, converting D:/ -> /mnt/d/ on Linux. BUT direct file writes in batch scripts (`open(os.path.join(output_dir, "metadata.json"))`) do NOT call `to_native_path()`, causing files to be written to wrong relative path. Solution: use `repair_outputs.py` to regenerate missing files in correct locations.

### 11. AV1 Codec Frame Extraction Failure

Some .webm videos encoded with AV1 cannot have frames extracted in WSL2. `cv2.VideoCapture` fails with "AV1 hardware decode not supported". Audio transcription works normally. Affected: video #75 (0 frames, 88 transcription segments). Workaround: re-encode to H.264 with ffmpeg.

### 12. Silent Videos (0 Transcription Segments)

Some short screencast videos have no speech. Whisper VAD removes 100% of audio as silence. Result: 0 segments, 0 chapters. Videos #04, #30, #31-#37, #39, #99 affected. These are valid -- just silent demonstrations.

## Статистика проекта

### Chat Analysis
- 68,659 сообщений из 3 топиков
- 19,315 цепочек диалогов
- 7,962 пары вопрос-ответ
- 6 топиков (92% в "Взаимопомощь")
- 9 FAQ-категорий
- Период: июнь 2025 -- февраль 2026

### Video-to-Knowledge
- Videos processed: 112 output folders
- Videos in pending/: 84 files (all already have output)
- Batch processing: 84 videos in ~9.6 hours GPU (RTX 3060)
- Средняя длина видео: ~5 мин
- Производительность (RTX 3060, large-v3 int8): ~10x realtime
- ~10-15 ключевых кадров на 5-минутное видео

### Community Articles
- 159 статей из Telegram-канала PuzzleBot Сообщество
- 10 категорий (крупнейшие: "Маркетинг и кейсы" ~70, "Настройка бота" ~50)
- 15+ авторов (топ: PuzzleBot Team, Светлана Гизатулина -- 32 видео-статьи)
- 5 типов контента: video-tutorial, photo-article, text-article, interview, case-study
- 9 видео-статей с извлечёнными кадрами (48-56, 202 кадра)
- Период: 2022--2026
- Индексы: catalog.json + index.md (Obsidian)

## Дополнительные ресурсы

| Ресурс | Путь | Описание |
|--------|------|---------|
| FAQ | `references/faq.md` | 15 вопросов по обоим pipeline |
| Troubleshooting | `references/troubleshooting.md` | 10 типичных проблем и решений |
| Cheatsheet | `references/cheatsheet.md` | Все команды, параметры, формулы |
| Research: Whisper/SSIM/OCR | `docs/research/01_research.md` | Сравнение технологий |
| Research: Adaptive SSIM | `docs/research/05_adaptive_algorithm.md` | Блок-схема алгоритма |
| Старый скилл (chat-only) | `docs/skill/SKILL.md` | Предшественник (только chat analysis) |
| Community Articles Catalog | `output/video-knowledge/community-articles/community_articles_catalog.json` | JSON-каталог 47 статей |
| Community Articles Index | `output/video-knowledge/community-articles/community_articles_index.md` | Obsidian-индекс с кросс-ссылками |
