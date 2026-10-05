---
name: voicebot-справочник
description: "Справочник VoiceTranscriptionBot v6.1.0 - Telegram + WhatsApp + Admin, Python 3.13. Транскрипция голосовых сообщений, OCR, мультиплатформенность."
---
# VoiceTranscriptionBot -- Справочник

**Версия:** v6.1.0 | **Платформы:** Telegram + WhatsApp + Admin | **Язык:** Python 3.13
**Расположение проекта:** `D:/Downloads/VoiceTranscriptionBot/`

## Триггеры активации

Ключевые слова: `voicebot`, `голосовой бот`, `транскрипция`, `whisper`, `STT`, `voice transcription`, `VoiceTranscriptionBot`, `voice pipeline`, `распознавание речи`, `голосовые сообщения`, `admin bot`, `task routing`, `llm client`, `TaskType`

---

## Архитектура: полный пайплайн

```
Audio/Voice ─────────────────────────────────────────────────────────────────────
  │
  ▼
[1] STT Transcription ───── faster-whisper GPU ──▶ Groq Whisper API ──▶ ERROR
  │                          (local, large-v3)      (cloud fallback)
  ▼
[1b] Duplicate Detection ── services.db.find_duplicate (optional)
  │
[1c] Dictation Check ────── duration > 180s → is_dictation=True
  │
  ▼
[2] Auto-Correction ─────── LLMClient.generate_for_task(TRANSFORMATION)
  │                          gemini-2.5-flash → Groq Llama → original text
  ▼
[2b] Key Facts ──────────── LLMClient.generate_for_task(ANALYSIS)
  │                          dates, amounts, names, phones
[2c] Client Detection ───── substring/prefix matching in clients.json
  │
  ▼
[3] Note Detection ──────── regex (9 trigger words, local, no LLM)
  │                          if is_note=True → SKIP steps 4,5,7,8
  ▼
[4] Sentiment ───────────── LLMClient.generate_for_task(CLASSIFICATION)
  │                          gemini-2.5-flash-lite → Groq Llama → "neutral"
  ▼
[5] Summarization ───────── LLMClient.generate_for_task(ANALYSIS)
  │                          (skipped if dictation; adaptive prompt by duration)
  ▼
[7] Urgency ─────────────── regex keywords (RU/EN/AR, local, no LLM)
  │
[8] Translation ─────────── LLMClient.generate_for_task(TRANSFORMATION)
  │                          if lang != "ru": gemini-2.5-flash → Groq Llama
  ▼
[9] Categorization ──────── keyword matching (9 categories, local, no LLM)
  │
  ▼
[10] Save to DB ─────────── SQLite + FTS5 full-text search
  │
  ▼
PipelineResult (dataclass) ──▶ format_transcription() ──▶ Telegram/WhatsApp
```

**Параллельные пайплайны:** Image (OCR вместо STT), Video (yt-dlp + extract audio), PDF (PyMuPDF → OCR per page)

> Подробности: `references/stt-pipeline.md`, `references/llm-cascade.md`

---

## Структура проекта

```
VoiceTranscriptionBot/
├── bot/                    # 17 файлов — Telegram-бот (aiogram 3.x)
│   ├── main.py             # Entry point, polling, scheduler
│   ├── config.py           # .env loader, настройки
│   ├── handlers.py         # Хаб-маршрутизатор (258 строк, регистрация 12 модулей)
│   ├── handlers_voice.py   # Обработка голосовых и аудио
│   ├── handlers_video.py   # Обработка видео-ссылок
│   ├── handlers_export.py  # Экспорт транскрипций (PDF, Excel, Markdown, TXT)
│   ├── handlers_calc.py    # Калькулятор и маршруты (FSM, конвертация, туры)
│   ├── handlers_callbacks.py # Inline-кнопки и callback-хендлеры
│   ├── handlers_stats.py   # Статистика, дайджест, история, поиск
│   ├── handlers_clients.py # Клиенты, расходы, уроки, здоровье
│   ├── handlers_admin_commands.py # Админские команды (approve, reject, archive)
│   ├── handlers_text.py    # Текстовые триггеры (переводчик, улучшение, форматирование)
│   ├── handlers_common.py  # Общие команды (/start, /help, /settings, /quick)
│   ├── handlers_templates.py # Шаблоны быстрых ответов
│   ├── transcriber.py      # STT cascade: faster-whisper → Groq
│   ├── summarizer.py       # LLM cascade: Gemini → Groq Llama (legacy, see llm_client.py)
│   ├── database.py         # ~1764 строк: async SQLite, 7 таблиц, FTS5
│   └── auto_delete.py      # Auto-delete сервисных сообщений (15-25с)
│
├── core/                   # ~60 файлов — бизнес-логика
│   ├── pipeline.py         # process_voice(), process_image(), process_video()
│   ├── llm_client.py       # Unified LLM client: generate_for_task(prompt, TaskType), GEMINI_MODELS
│   ├── corrector.py        # Auto-correction после STT
│   ├── sentiment.py        # Анализ тональности (positive/neutral/negative)
│   ├── categories.py       # 9 категорий + keyword matching + smart (LLM)
│   ├── key_facts.py        # Извлечение дат, сумм, имён, телефонов
│   ├── urgency.py          # Детектор срочности (22 ключевых слова)
│   ├── note_detector.py    # Распознавание заметок (9 триггеров)
│   ├── translator.py       # Перевод (Google Translate + Gemini AI, 4 языка, 32 триггера)
│   ├── ocr.py              # OCR: Google Vision → Gemini Vision
│   ├── accounting.py       # Парсер чеков (Gemini Vision)
│   ├── expense_categories.py # 11 категорий расходов
│   ├── clients.py          # CRUD клиентов (data/clients.json)
│   ├── client_detector.py  # Определение клиента в тексте
│   ├── team.py             # 4 члена команды, маршрутизация по категориям
│   ├── prices.py           # Прайс-лист (22 позиции, 7 категорий)
│   ├── templates.py        # 9 шаблонов быстрых ответов (6 категорий)
│   ├── lessons.py          # Система самообучения (12 типов уроков)
│   ├── approval.py         # 2-уровневая система подтверждений
│   ├── digest.py           # AI-дайджест (день/неделя/месяц)
│   ├── combiner.py         # Объединение голосовых (3 режима)
│   ├── reminders.py        # Извлечение дат напоминаний
│   ├── improver.py         # AI-улучшение сообщений (4 получателя, 3 тона, 20 триггеров)
│   ├── calculator.py       # Tour calculator (currencies, tours, agent commissions)
│   ├── router.py           # Route builder (Google Maps, TSP, transit, Salik, ~150 алиасов)
│   ├── formatter.py        # Реэкспорт-хаб форматирования
│   ├── formatter_common.py # Общие константы и хелперы
│   ├── formatter_transcription.py # Форматирование транскрипций
│   ├── formatter_stats.py  # Форматирование статистики и дашбордов
│   ├── formatter_admin.py  # Форматирование админских экранов
│   ├── formatter_video.py  # Форматирование видео-контента
│   ├── formatter_tour.py   # AI-форматирование турпродуктов (WA/TG)
│   ├── response_builder.py # Конструктор ответов из PipelineResult
│   ├── navigation.py       # Стек экранов для кнопки "Назад"
│   ├── scheduler.py        # ~668 строк: 12 фоновых задач
│   ├── services.py         # DI-контейнер (module-level singletons)
│   ├── video_downloader.py # yt-dlp wrapper
│   ├── video_manager.py    # SQLite tracking видео
│   ├── video_utils.py      # Утилиты: detect_platform, is_video_url
│   ├── cloud_storage.py    # Google Drive + Yandex Disk
│   ├── export_pdf.py       # PDF-отчёты (fpdf2 + Cyrillic)
│   ├── export_xlsx.py      # Excel-отчёты (openpyxl)
│   ├── export_md.py        # Markdown-отчёты
│   ├── exporter.py         # TXT-экспорт
│   ├── export_expenses.py  # Отчёты расходов (PDF + Excel)
│   ├── json_utils.py       # 3-stage LLM JSON parser
│   ├── retry.py            # Retry с exponential backoff
│   ├── expiring_dict.py    # Универсальный dict с TTL и size limit
│   ├── log_sanitizer.py    # Маскировка API-ключей в логах
│   ├── validators.py       # Валидация .env при старте
│   ├── logging_config.py   # Ротация логов (RotatingFileHandler, JSON, 10MB x 5)
│   ├── health.py           # Healthcheck endpoints (порты 8081/8082)
│   ├── api_monitor.py      # Мониторинг расхода API-токенов
│   ├── backup.py           # Автобэкапы БД (ежедневно 04:00, ротация 7 дней)
│   ├── auto_followup.py    # Авто follow-up напоминания из key_facts
│   ├── bitrix24.py         # Bitrix24 авто-создание лидов
│   ├── language_detector.py # Авто-определение языка
│   ├── google_sheets.py    # Экспорт статистики в Google Sheets
│   ├── diarization.py      # Speaker diarization — определение говорящих
│   └── db_security.py      # Подготовка к шифрованию SQLite
│
├── whatsapp/               # 5 файлов — WhatsApp-бот (FastAPI + webhook)
│   ├── app.py              # FastAPI, uvicorn :8000, HMAC verification
│   ├── handlers.py         # ~2465 строк: 35+ текстовых команд
│   ├── client.py           # WhatsApp Cloud API wrapper (httpx)
│   └── security.py         # HMAC-SHA256, replay protection, phone masking
│
├── admin/                  # 14 файлов — Админ-бот (мониторинг переписок)
│   ├── __init__.py         # Пакет
│   ├── main.py             # Запуск админ-бота (aiogram polling + scheduler)
│   ├── handlers.py         # Основные команды + inline-кнопки
│   ├── notifier.py         # Пересылка уведомлений + автоответчик + авто-теги
│   ├── scheduler.py        # Планировщик (ежедневный отчёт 22:00, эскалация, heartbeat)
│   ├── console.py          # CLI-интерфейс для просмотра чатов
│   ├── suggester.py        # AI-суфлёр (Gemini варианты ответов, каскад 3 моделей)
│   ├── monitor.py          # Мониторинг (heartbeat TG, API health, диск, логи)
│   ├── spam_guard.py       # Антиспам (50 msg/min порог, авто-разблокировка 5 мин)
│   ├── handlers_analytics.py # Аналитика (/lost, /revenue, /season, /sla_platforms)
│   ├── handlers_crm.py     # CRM (/phone, карточка клиента, воронка, фолоуап)
│   ├── handlers_security.py # Безопасность (FULL/VIEW доступ, /access, /audit_full)
│   ├── handlers_integrations.py # Интеграции (/export_contacts, /notification_mode)
│   └── api.py              # Webhook API (POST /api/admin/notify для Bitrix/Make)
│
├── tests/                  # 55+ файлов — ~2138 тестов (pytest)
├── data/                   # JSON-хранилища + SQLite + шрифты
├── docs/                   # Документация (Oracle deploy, cloud setup, guides)
├── scripts/                # 12 файлов: .bat/.sh/.service/.conf
├── .github/                # CI/CD (tests.yml + lint.yml)
├── Dockerfile              # Docker-образ (Python 3.13, multi-stage)
├── docker-compose.yml      # Docker Compose: 3 сервиса (Telegram + WhatsApp + Admin)
├── .env                    # Секреты (не в git)
├── requirements.txt        # Зависимости (GPU)
└── requirements-server.txt # Зависимости (сервер, без GPU)
```

---

## Telegram-команды (30)

### Меню бота (19 команд)

| # | Команда | Описание |
|---|---------|----------|
| 1 | `/start` | Приветствие и начало работы |
| 2 | `/help` | Справка по всем командам |
| 3 | `/stats` | Статистика: сегодня/неделя/месяц + тренды + команда |
| 4 | `/digest` | AI-дайджест за день/неделю/месяц + PDF |
| 5 | `/history` | Пагинированная история (5/стр, фильтры, закладки) |
| 6 | `/search <запрос>` | Полнотекстовый поиск FTS5 с пагинацией |
| 7 | `/notes` | Голосовые заметки (фильтр по #тегу) |
| 8 | `/merge` | Объединить голосовые: по кол-ву / за сегодня / по категории |
| 9 | `/export` | Экспорт: PDF / Excel / Markdown / TXT / все форматы |
| 10 | `/date <дата>` | Поиск по дате (сегодня/вчера/DD.MM.YYYY) |
| 11 | `/compare` | Сравнение текущей и прошлой недели |
| 12 | `/clients` | База клиентов: карточки, история, заметки |
| 13 | `/price` | Прайс-лист (22 позиции, fuzzy-поиск) |
| 14 | `/expenses` | Расходы: список / статистика / по периодам |
| 15 | `/report` | Финансовый PDF/Excel-отчёт (неделя/месяц) |
| 16 | `/settings` | Настройки: дайджест, уведомления, язык, пересылка |
| 17 | `/health` | Здоровье системы: БД, temp, уроки, approvals |
| 18 | `/archive` | Архивация записей старше 6 месяцев (через approval) |
| 19 | `/translate` | Перевод текста: реплай на сообщение + выбор языка (рус/англ/араб/кит) |

### Дополнительные команды (11)

| # | Команда | Описание |
|---|---------|----------|
| 20 | `/add_expense СУММА описание` | Ручное добавление расхода (авто-категория) |
| 21 | `/lessons [list\|stats]` | Уроки бота (самообучение) |
| 22 | `/fix EID field VALUE` | Исправить расход + записать урок |
| 23 | `/pending` | Ожидающие подтверждения |
| 24 | `/approvals` | История подтверждений |
| 25 | `/approve OPT-ID` | Одобрить запрос (только admin) |
| 26 | `/reject OPT-ID [причина]` | Отклонить запрос |
| 27 | `/calc` | Калькулятор (конвертация, стоимость тура, агентский расчёт) |
| 28 | `/rate` | Текущие курсы валют |
| 29 | `/route` | Маршруты (между точками, план дня, транзит) |
| 30 | `/improve` | Улучшить текст сообщения (получатель + стиль) |

> Также: `/templates` — шаблоны быстрых ответов с подстановкой переменных, `/quick` — повтор последней команды

> Полный справочник: `references/telegram-commands.md`, `references/whatsapp-commands.md`

---

## 9 бизнес-категорий

| # | Ключ | Название | Emoji | Ответственный | Группа |
|---|------|----------|-------|---------------|--------|
| 1 | `excursions` | Экскурсии | 🏛️ | Сухейль | excursions |
| 2 | `tickets` | Билеты | 🎫 | Сухейль | tickets |
| 3 | `parks` | Парки развлечений | 🎢 | Сухейль | **tickets** |
| 4 | `cars` | Автомобили | 🚗 | Марсель | cars |
| 5 | `transfer` | Трансфер | 🚐 | Марсель | transfer |
| 6 | `mvu` | МВУ | 🪪 | Марсель | mvu |
| 7 | `yachts` | Яхты | ⛵ | Мухаммад-Амин | yachts |
| 8 | `water` | Водные развлечения | 🌊 | Мухаммад-Амин | water |
| 9 | `abayas` | Абаи/Одежда | 👗 | Камила | abayas |

**Fallback:** `general` (confidence 0.0) -- маршрутизация на admin (Сухейль)

---

## Переменные окружения

### Обязательные

| Переменная | Назначение |
|-----------|-----------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота от @BotFather |
| `GROQ_API_KEY` | Groq API: fallback STT (Whisper) + LLM (Llama 3.3 70B) |
| `GEMINI_API_KEY` | Google Gemini API: primary LLM (summaries, correction, sentiment) |
| `ALLOWED_USER_IDS` | Whitelist Telegram user IDs (через запятую) |

### WhatsApp (если запускается WA-бот)

| Переменная | Назначение |
|-----------|-----------|
| `WHATSAPP_TOKEN` | Bearer token Cloud API (Meta Business -> System Users) |
| `WHATSAPP_PHONE_ID` | Phone Number ID (Meta API Setup) |
| `WHATSAPP_VERIFY_TOKEN` | Shared secret для webhook verification |
| `WHATSAPP_APP_SECRET` | App Secret для HMAC-SHA256 signature verification |
| `WHATSAPP_ALLOWED_PHONES` | Whitelist телефонов (через запятую, без +) |

### Admin-бот

| Переменная | Назначение |
|-----------|-----------|
| `ADMIN_BOT_TOKEN` | Токен админ-бота Telegram |
| `ADMIN_USER_IDS` | Whitelist админов (через запятую) |
| `ADMIN_API_TOKEN` | Токен для внешнего webhook API (Bitrix/Make) |

### Опциональные

| Переменная | Default | Назначение |
|-----------|---------|-----------|
| `WHISPER_MODEL` | `large-v3` | Модель faster-whisper для локального STT |
| `WHISPER_DEVICE` | `cuda` | Устройство: `cuda` (GPU) или `cpu` |
| `FORCE_GROQ_STT` | `false` | Пропустить локальный Whisper, использовать только Groq |
| `DB_PATH` | `data/transcriptions.db` | Путь к SQLite базе |
| `TEMP_DIR` | `temp/` | Директория временных файлов |
| `GOOGLE_VISION_API_KEY` | -- | Google Cloud Vision для OCR |
| `YANDEX_DISK_TOKEN` | -- | Yandex Disk для больших видео (>50 МБ) |
| `GOOGLE_DRIVE_CREDENTIALS` | -- | Google Drive service account JSON |
| `GOOGLE_MAPS_API_KEY` | -- | Google Maps API для маршрутов |
| `GOOGLE_TRANSLATE_API_KEY` | -- | Google Translate API для переводчика |
| `GOOGLE_SHEETS_CREDENTIALS` | -- | Google Sheets service account JSON |
| `BITRIX24_DOMAIN` | -- | Домен Битрикс24 (xxx.bitrix24.ru) |
| `ENFORCE_HTTPS` | `true` | Принудительный HTTPS для admin API |
| `ENABLE_DIARIZATION` | `false` | Определение говорящих в аудио |

---

## Карта модулей

### Core Pipeline

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `core/pipeline.py` | Главный пайплайн: process_voice, process_image, process_video | `references/stt-pipeline.md` |
| `core/llm_client.py` | Unified LLM client: generate_for_task(prompt, TaskType), GEMINI_MODELS | `references/llm-cascade.md` |
| `bot/transcriber.py` | STT cascade: faster-whisper GPU -> Groq Whisper | `references/stt-pipeline.md` |
| `bot/summarizer.py` | LLM cascade (legacy): Gemini -> Groq Llama | `references/llm-cascade.md` |
| `core/corrector.py` | Auto-correction транскрипции (Gemini -> Groq -> original) | `references/llm-cascade.md` |
| `core/sentiment.py` | Анализ тональности: positive/neutral/negative | `references/llm-cascade.md` |
| `core/categories.py` | 9 категорий: keyword matching + LLM smart | `references/business-modules.md` |
| `core/key_facts.py` | Извлечение дат, сумм, имён, телефонов | `references/llm-cascade.md` |
| `core/urgency.py` | Детектор срочности: 22 ключевых слова (RU/EN/AR) | `references/business-modules.md` |
| `core/note_detector.py` | Заметки: 9 триггеров + auto-tags | `references/business-modules.md` |
| `core/translator.py` | Перевод 4 языка + AI-метки engine_used | `references/llm-cascade.md` |
| `core/improver.py` | AI-улучшение сообщений (4 получателя, 3 тона, 20 триггеров) | `references/llm-cascade.md` |
| `core/json_utils.py` | 3-stage JSON parser для ответов LLM | `references/llm-cascade.md` |
| `core/retry.py` | retry_async: max 2 retries, exponential backoff | `references/infrastructure.md` |
| `core/response_builder.py` | Конструктор ответов из PipelineResult (TG и WA) | `references/infrastructure.md` |

### Business Logic

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `core/ocr.py` | OCR: Google Vision -> Gemini Vision + PDF OCR | `references/business-modules.md` |
| `core/accounting.py` | Receipt parser (Gemini Vision) + auto-categorize | `references/business-modules.md` |
| `core/expense_categories.py` | 11 категорий расходов с ключевыми словами | `references/business-modules.md` |
| `core/clients.py` | CRUD клиентов: data/clients.json | `references/business-modules.md` |
| `core/client_detector.py` | Определение клиента в тексте: имя/diminutive match | `references/business-modules.md` |
| `core/team.py` | 4 члена команды, маршрутизация по категориям | `references/business-modules.md` |
| `core/prices.py` | Прайс-лист: 22 позиции, 7 категорий, fuzzy search | `references/business-modules.md` |
| `core/templates.py` | 9 шаблонов быстрых ответов (6 категорий) | `references/business-modules.md` |
| `core/lessons.py` | Самообучение: 12 типов уроков, scoring, injection | `references/business-modules.md` |
| `core/approval.py` | 2-уровневая система (A/B), 8 типов запросов | `references/infrastructure.md` |
| `core/calculator.py` | Tour calculator: конвертация AED/RUB/USD/KZT/EUR, стоимость туров, агент | `references/business-modules.md` |
| `core/router.py` | Route builder: Google Maps, TSP, transit, Salik, ~150 алиасов | `references/business-modules.md` |

### Content & Export

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `core/digest.py` | AI-дайджест + top-3 scoring + PDF auto-gen | `references/business-modules.md` |
| `core/combiner.py` | Merge голосовых: by count / period / category | `references/business-modules.md` |
| `core/export_pdf.py` | PDF-отчёты: fpdf2 + DejaVu Cyrillic | `references/infrastructure.md` |
| `core/export_xlsx.py` | Excel-отчёты: openpyxl, 3 листа | `references/infrastructure.md` |
| `core/export_md.py` | Markdown-экспорт | `references/infrastructure.md` |
| `core/exporter.py` | TXT-экспорт | `references/infrastructure.md` |
| `core/export_expenses.py` | Отчёты расходов: PDF + Excel | `references/infrastructure.md` |

### Video & Cloud

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `core/video_downloader.py` | yt-dlp wrapper: info, download, quality presets, thumbnail_url | `references/business-modules.md` |
| `core/video_manager.py` | SQLite tracking: status, expiry, cleanup, find_by_url() дедупликация | `references/business-modules.md` |
| `core/video_utils.py` | Утилиты: detect_platform, is_video_url, format_duration | `references/business-modules.md` |
| `core/cloud_storage.py` | Google Drive + Yandex Disk upload (>50 МБ) | `references/business-modules.md` |

### Infrastructure

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `bot/database.py` | Async SQLite: 7 таблиц, FTS5, 50+ методов | `references/infrastructure.md` |
| `core/formatter.py` | Реэкспорт-хаб (formatter_common/transcription/stats/admin/video/tour) | `references/infrastructure.md` |
| `core/formatter_common.py` | Общие константы, хелперы, разделители | `references/infrastructure.md` |
| `core/formatter_transcription.py` | Форматирование транскрипций | `references/infrastructure.md` |
| `core/formatter_stats.py` | Форматирование статистики и дашбордов | `references/infrastructure.md` |
| `core/formatter_admin.py` | Форматирование админских экранов | `references/infrastructure.md` |
| `core/formatter_video.py` | Форматирование видео-контента | `references/infrastructure.md` |
| `core/formatter_tour.py` | AI-форматирование турпродуктов (WA/TG) | `references/infrastructure.md` |
| `core/navigation.py` | Screen stack: push/pop, max 20, back detection | `references/infrastructure.md` |
| `core/scheduler.py` | 12 фоновых задач: digest, cleanup, archive, reports | `references/infrastructure.md` |
| `core/services.py` | DI-контейнер: module-level singletons + download_semaphore (5 параллельных) | `references/infrastructure.md` |
| `core/expiring_dict.py` | Универсальный dict с TTL и size limit | `references/infrastructure.md` |
| `core/log_sanitizer.py` | Маскировка API-ключей в логах | `references/security.md` |
| `core/validators.py` | Валидация .env при старте (обязательные/опциональные) | `references/security.md` |
| `core/logging_config.py` | Ротация логов: RotatingFileHandler, JSON, 10MB x 5 | `references/infrastructure.md` |
| `core/health.py` | Healthcheck endpoints (порты 8081/8082) | `references/infrastructure.md` |
| `core/api_monitor.py` | Мониторинг API-вызовов с лимитами и алертами | `references/infrastructure.md` |
| `core/backup.py` | Автобэкапы БД: ежедневно 04:00, ротация 7 дней | `references/infrastructure.md` |
| `core/auto_followup.py` | Авто follow-up напоминания из key_facts | `references/business-modules.md` |
| `core/bitrix24.py` | Bitrix24 авто-создание лидов | `references/infrastructure.md` |
| `core/language_detector.py` | Авто-определение языка входящего сообщения | `references/business-modules.md` |
| `core/google_sheets.py` | Экспорт статистики в Google Sheets | `references/infrastructure.md` |
| `core/diarization.py` | Speaker diarization -- определение говорящих | `references/stt-pipeline.md` |
| `core/db_security.py` | Подготовка к шифрованию SQLite | `references/security.md` |

### Platforms

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `bot/handlers.py` | Telegram: хаб-маршрутизатор (258 строк, 12 модулей) | `references/telegram-commands.md` |
| `bot/handlers_voice.py` | Обработка голосовых и аудио | `references/telegram-commands.md` |
| `bot/handlers_video.py` | Обработка видео-ссылок | `references/telegram-commands.md` |
| `bot/handlers_calc.py` | Калькулятор и маршруты (FSM) | `references/telegram-commands.md` |
| `bot/handlers_callbacks.py` | Inline-кнопки и callback routing | `references/telegram-commands.md` |
| `bot/handlers_text.py` | Текстовые триггеры (переводчик, улучшение, форматирование) | `references/telegram-commands.md` |
| `bot/main.py` | Telegram entry point: polling, startup, shutdown | `references/telegram-commands.md` |
| `whatsapp/app.py` | FastAPI: webhook endpoints, HMAC, lifespan | `references/whatsapp-commands.md` |
| `whatsapp/handlers.py` | WhatsApp: 35+ текстовых команд, interactive buttons | `references/whatsapp-commands.md` |
| `whatsapp/client.py` | WhatsApp Cloud API: send_text, send_image, buttons, list, media | `references/whatsapp-commands.md` |
| `whatsapp/security.py` | HMAC-SHA256, replay protection, phone masking | `references/security.md` |

### Admin Bot

| Модуль | Назначение | Ссылка |
|--------|-----------|--------|
| `admin/main.py` | Entry point: aiogram polling + scheduler | `references/security.md` |
| `admin/handlers.py` | 47+ команд, inline-кнопки, CRM | `references/security.md` |
| `admin/notifier.py` | Пересылка уведомлений + автоответчик + авто-теги | `references/security.md` |
| `admin/scheduler.py` | Ежедневный отчёт 22:00, эскалация, heartbeat | `references/infrastructure.md` |
| `admin/suggester.py` | AI-суфлёр (Gemini каскад 3 моделей) | `references/llm-cascade.md` |
| `admin/monitor.py` | Heartbeat TG, API health, диск, логи | `references/infrastructure.md` |
| `admin/spam_guard.py` | Антиспам (50 msg/min, авто-разблокировка 5 мин) | `references/security.md` |
| `admin/api.py` | Webhook API: POST /api/admin/notify (Bitrix/Make) | `references/security.md` |

---

## Индекс reference-файлов

| Файл | Содержимое |
|------|-----------|
| `references/stt-pipeline.md` | STT cascade, Transcriber class, faster-whisper config, Groq STT, confidence, diarization |
| `references/llm-cascade.md` | LLMClient, TaskType routing, Gemini models, Groq Llama, correction, sentiment, summarization, key_facts, translation, improver, JSON parsing |
| `references/business-modules.md` | Категории, OCR, accounting, клиенты, команда, прайс, шаблоны, уроки, видео, дайджест, combiner, заметки, калькулятор, маршруты, follow-up |
| `references/telegram-commands.md` | 30 команд, callback data patterns, inline keyboards, middleware, navigation, FSM states |
| `references/whatsapp-commands.md` | 35+ команд, interactive buttons, list menus, reactions, screen stack |
| `references/infrastructure.md` | Database schema (7 таблиц), FTS5, export formats, formatter (6 модулей), scheduler, approval, retry, healthcheck, backup, logging, dependencies |
| `references/security.md` | HMAC-SHA256, whitelist, approval levels, .env validation, log sanitizer, admin bot security, nginx, deploy |
| `references/cheatsheet.md` | Быстрые рецепты: добавить команду, новый модуль, тесты |
| `references/troubleshooting.md` | Частые ошибки и решения |
| `references/faq.md` | Часто задаваемые вопросы |

---

## Безопасность -- чеклист

| Паттерн | Где реализовано |
|---------|----------------|
| **HMAC-SHA256** webhook verification | `whatsapp/security.py` -- timing-safe `hmac.compare_digest()` |
| **Whitelist (deny-by-default)** | Telegram: `ALLOWED_USER_IDS` + `WhitelistMiddleware`; WhatsApp: `WHATSAPP_ALLOWED_PHONES`; Admin: `ADMIN_USER_IDS` |
| **Approval для деструктивных операций** | `core/approval.py` -- 2 уровня (A: 24h, B: 48h), 8 типов |
| **Маскировка секретов в логах** | `core/log_sanitizer.py` -- API-ключи, телефоны |
| **Валидация .env при старте** | `core/validators.py` -- обязательные/опциональные переменные с подсказками |
| **Replay protection** | `whatsapp/security.py` -- ExpiringDict nonce, 5-мин окно |
| **HTTPS enforcement** | Middleware для admin API принудительно требует HTTPS |
| **API docs отключены** | FastAPI: `docs_url=None, redoc_url=None` |
| **nginx: минимальная поверхность** | Только `/webhook` проксируется, rate limit 10 req/s |
| **SSL termination** | Let's Encrypt через nginx, FastAPI на localhost:8000 |
| **Unprivileged execution** | systemd: `User=ubuntu`, не root |
| **Secrets в .env** | Не в коде, загружаются через `EnvironmentFile` в systemd |
| **Rate limiting API** | asyncio.Semaphore для Gemini/Groq/Google Maps/Vision |
| **File size validation** | Лимиты: audio 25MB, photo 10MB, video 100MB, PDF 20MB |
| **Двухуровневый доступ (Admin)** | FULL / VIEW уровни в admin bot (`admin/handlers_security.py`) |
| **Антиспам** | `admin/spam_guard.py` -- 50 msg/min порог, авто-разблокировка |
| **Temp file cleanup** | `try/finally` в обработчиках + hourly scheduler cleanup |

> Подробности: `references/security.md`

---

## Когда использовать этот скилл

- Нужно понять, как работает голосовой пайплайн (STT -> LLM -> DB)
- Добавить новую команду в Telegram или WhatsApp бот
- Разобраться в LLMClient и TaskType routing
- Найти нужный модуль или функцию в проекте
- Посмотреть схему базы данных или env-переменные
- Понять систему категорий и маршрутизацию по команде
- Разобраться с системой уроков (self-learning)
- Настроить deploy на Oracle Cloud ARM
- Отладить проблему с безопасностью (HMAC, whitelist, approval, log sanitizer)
- Добавить новый формат экспорта или расширить существующий
- Работа с видео pipeline (download, transcribe, cloud upload)
- Работа с админ-ботом (мониторинг, CRM, аналитика, суфлёр)
- Работа с калькулятором и маршрутами

---

## Quick Start

```bash
# 1. Установить зависимости
cd D:/Downloads/VoiceTranscriptionBot
pip install -r requirements.txt          # GPU (CUDA)
# или: pip install -r requirements-server.txt  # Сервер (без GPU)

# 2. Настроить .env (минимум 4 переменных)
# TELEGRAM_BOT_TOKEN, GROQ_API_KEY, GEMINI_API_KEY, ALLOWED_USER_IDS

# 3. Запустить
python -m bot.main                       # Только Telegram
python -m whatsapp.app                   # Только WhatsApp (:8000)
python -m admin.main                     # Только Admin-бот
scripts/start_all.bat                    # Все 3 бота (Windows)
```

**Сервер (Oracle ARM):**
```bash
sudo systemctl start voice_bot           # Telegram
sudo systemctl start whatsapp_bot        # WhatsApp (за nginx :443)
sudo systemctl start admin_bot           # Admin
```

---

## LLM-модели и TaskType routing

| Модель | Использование | Temperature | TaskType |
|--------|--------------|-------------|----------|
| `gemini-2.5-flash` | Primary (через LLMClient) | per TaskType | ANALYSIS, CREATIVE, VISION, TRANSFORMATION, PLANNING |
| `gemini-2.5-flash-lite` | Лёгкие задачи | 0.1 | CLASSIFICATION |
| `llama-3.3-70b-versatile` | Groq fallback (все задачи) | 0.3 | all (emergency) |
| `whisper-large-v3` | Groq STT (cloud) | -- | -- |
| `faster-whisper large-v3` | Локальный GPU STT | -- | -- |

**TaskType routing (core/llm_client.py):**
- `CLASSIFICATION` (sentiment, categories) -- cheapest model (flash-lite), temperature 0.1
- `ANALYSIS` (summarization, key_facts, correction) -- primary model, temperature 0.3
- `CREATIVE` (improver, suggester) -- primary model, high temperature 0.7
- `TRANSFORMATION` (translator, formatter_tour) -- primary model, temperature 0.3
- `VISION` (OCR, receipt parsing) -- primary model with image support
- `PLANNING` (calculator, router) -- primary model, low temperature 0.2 for precise JSON

**Изменение модели = 1 строка в `core/llm_client.py`**

---

## Команда

| Имя | Роль | Telegram ID | Категории |
|-----|------|-------------|-----------|
| **Сухейль** | admin | 6905404901 | excursions, tickets, parks |
| **Марсель** | member | 5939002952 | cars, transfer, mvu |
| **Мухаммад-Амин** | member | 1336041242 | yachts, water |
| **Камила** | member | -- | abayas |

---

## Data Files

| Файл | Формат | Содержимое |
|------|--------|-----------|
| `data/transcriptions.db` | SQLite | 7 таблиц: transcriptions, _fts, _archive, reminders, expenses, video_downloads, cloud_uploads |
| `data/clients.json` | JSON | Клиенты: phone -> {name, type, notes} |
| `data/team.json` | JSON | 4 члена команды: roles, phones, categories |
| `data/prices.json` | JSON | Прайс-лист: 22 позиции, 7 категорий |
| `data/templates.json` | JSON | 9 шаблонов быстрых ответов |
| `data/lessons.json` | JSON | Уроки самообучения: 12 типов |
| `data/pending_approvals.json` | JSON | Запросы на подтверждение |
| `data/admin_templates.json` | JSON | Шаблоны быстрых ответов админа (5 шаблонов) |
| `data/fonts/` | TTF | DejaVuSans для PDF Cyrillic |

---

## Зависимости

| Пакет | Версия | Назначение |
|-------|--------|-----------|
| `aiogram` | >= 3.25.0 | Telegram-бот |
| `groq` | >= 1.0.0 | Groq API (STT + LLM fallback) |
| `google-genai` | >= 1.0.0 | Gemini API (primary LLM) |
| `aiosqlite` | >= 0.22.0 | Async SQLite |
| `faster-whisper` | >= 1.2.0 | Локальный GPU STT (не на сервере) |
| `fastapi` | >= 0.115.0 | WhatsApp webhook |
| `uvicorn[standard]` | >= 0.34.0 | ASGI-сервер |
| `httpx` | >= 0.28.0 | Async HTTP (WhatsApp API, cloud uploads) |
| `fpdf2` | >= 2.8.0 | PDF-генерация (кириллица) |
| `openpyxl` | >= 3.1.0 | Excel-генерация |
| `yt-dlp` | >= 2026.2.4 | Скачивание видео (1700+ платформ) |
| `google-auth` | >= 2.0.0 | Google Drive auth |

---

## История версий

| Версия | Дата | Что нового |
|--------|------|-----------|
| **v6.1.0** | 2026-02-28 | AI Architecture: LLMClient consolidation, TaskType routing, deprecated model migration |
| **v6.0.0** | 2026-02-23 | Split handlers (12 modules), Security (log sanitizer, .env validation, replay protection), Infra (CI/CD, Docker, log rotation, healthcheck, DB backup, API monitor), ~2138 tests |
| **v5.8.0** | 2026-02-22 | UX (onboarding, compact buttons, /quick) + Stability (rate limiting, DB versioning, graceful shutdown, ExpiringDict) |
| **v5.7.0** | 2026-02-22 | Calculator FSM states, route place normalization (150 aliases), admin chat button fix |
| **v5.6.0** | 2026-02-22 | Message Improver: AI text polishing (4 recipients, 3 tones, 20 triggers); Colored inline buttons (~230, Bot API 9.4) |
| **v5.5.0** | 2026-02-22 | Admin v5.5: AI-suggester, CRM, analytics, monitoring, security, integrations, UX; 8 new modules |
| **v5.4.0** | 2026-02-22 | Tour Calculator + Route Builder: currencies, tours, Google Maps, TSP, Salik; /calc, /rate, /route |
| **v5.0.0** | 2026-02-21 | Admin bot + terminal console + Russian logs; conversations/messages tables; 56 new tests |
| **v4.5.0** | 2026-02-20 | Обложки видео, дедупликация, параллелизм, AI-метки в переводе, фикс F.text хендлеров |
| **v4.4.0** | 2026-02-20 | Переводчик v1.0 (4 языка, 32 триггера, кнопки), облачные улучшения, ~1307+ тестов |
| **v4.3.0** | 2026-02-20 | Полное форматирование текстов: стайл-гайд, 42 HTML замены, 52+ эмодзи, 27+ кнопок |
| **v4.0.0** | 2026-02-20 | Скачивание видео + транскрипция по ссылке, умное удаление, 1700+ платформ |
| **v3.7.0** | 2026-02-19 | Голосовые заметки с тегами: 9 триггеров, авто-теги, /notes |
| v3.5.0 | 2026-02-18 | Система уроков: 12 типов, интеграция в 6 модулей, /lessons, /fix |
| v3.3.0 | 2026-02-18 | Система подтверждений (approval-before-delete), мягкое удаление |
| v3.0.0 | 2026-02-18 | Личные кабинеты, авто-категоризация, пересылка, прайс-лист, общий pipeline |
| v2.0.0 | 2026-02-18 | Форматирование, inline-кнопки, закладки, экспорт, confidence, retry |
| v1.0.0 | 2026-02-17 | WhatsApp бот |

---

## Форматирование текстов бота (UI/UX стандарт)

**Эталонный гайд:** `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md`
**Универсальный промт:** `D:/Downloads/ПРОМТ_ФОРМАТИРОВАНИЕ_ТЕКСТОВ_БОТА.md`

При создании/редактировании ЛЮБЫХ текстов бота — ОБЯЗАТЕЛЬНО:

| Правило | Пример |
|---------|--------|
| Каждое сообщение начинается с эмодзи | `🛒 Корзина пуста` |
| Заголовки: эмодзи + `<b>bold</b>` + разделитель | `📊 <b>Статистика</b>\n──────────────────` |
| Списки с маркером ▫️ | `▫️ 🎫 Билеты — описание` |
| Разделители 18 символов | `──────────────────` (тонкий) / `━━━━━━━━━━━━━━━━━━` (жирный) |
| Числа/даты/суммы в `<code>` | `<code>1,500 AED</code>` |
| Кнопки ВСЕГДА с эмодзи | `✅ Подтвердить`, `❌ Отмена` |
| Пользовательский ввод экранировать | `_esc()` или `html.escape()` |

---

## Известные проблемы

| Проблема | Влияние | Статус |
|----------|---------|--------|
| `whatsapp/client._split_text()` -- бесконечный цикл при `max_len` < длина слова | Не проявляется на практике (лимит 4096) | Низкий приоритет |
| `telegram_id` Камилы в `data/team.json` = null | Кабинет/пересылка не работают до /start | Нужна активация |
