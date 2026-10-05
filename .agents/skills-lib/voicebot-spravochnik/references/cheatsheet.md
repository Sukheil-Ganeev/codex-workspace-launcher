# Cheatsheet -- Быстрая справочная карта

> Шпаргалка VoiceTranscriptionBot -- copy-paste ready
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`

---

## Все команды Telegram (30)

> handlers.py = хаб-маршрутизатор (258 строк) + 12 доменных модулей

```
/start          -- Начать работу
/help           -- Справка
/stats          -- Статистика и дашборд
/digest         -- AI-резюме дня (выбор периода)
/history        -- История записей (пагинация)
/search <query> -- Полнотекстовый поиск
/notes [#тег]   -- Голосовые заметки
/merge [N]      -- Объединить голосовые
/export [fmt]   -- Экспорт (pdf/xlsx/md/txt)
/date <дата>    -- Поиск по дате
/compare        -- Сравнение неделя vs неделя
/clients        -- База клиентов
/price [query]  -- Прайс-лист
/expenses [per] -- Расходы (today/week/month/stats)
/report [per]   -- Финансовый отчёт (week/month)
/settings       -- Настройки
/health         -- Здоровье системы
/archive        -- Архивация старых записей
/calc           -- Калькулятор (валюты/туры/агент)
/rate           -- Текущие курсы валют
/route          -- Маршруты Google Maps
/improve        -- Улучшить текст (4 получателя, 3 тона)
/templates      -- Шаблоны быстрых ответов
/add_expense    -- Ручной расход: /add_expense 150 бензин
/lessons        -- Уроки бота
/fix            -- Исправить расход: /fix EID field VALUE
/pending        -- Ожидающие подтверждения
/approvals      -- История подтверждений
/approve        -- Одобрить: /approve OPT-XXXX-XX-XX-XXXX
/reject         -- Отклонить: /reject OPT-ID [причина]
```

---

## Все команды WhatsApp (35+)

```
привет / help / старт                    -- Помощь
история / history                        -- Последние 5
поиск <запрос> / search <query>          -- FTS поиск
дата <дата> / date <date>                -- По дате
закладки / bookmarks                     -- Закладки
сохрани <ID>                             -- Toggle закладка
статус / stats                           -- Статистика
кабинет / cabinet                        -- Личный кабинет
команда / team                           -- Доска команды
сравни / compare                         -- Сравнение периодов
дашборд / dashboard                      -- Бизнес-пульс
здоровье / health                        -- Здоровье системы
объедини [N]                             -- Объединить
дайджест                                 -- Период дайджеста
дайджест за неделю/месяц                 -- Прямой дайджест
экспорт / export                         -- Меню экспорта
экспорт pdf/xlsx/md/txt                  -- Прямой экспорт
клиенты / clients                        -- Список клиентов
добавить клиент <phone> <name> [type]    -- Добавить
удалить клиент <phone>                   -- Удалить (approval)
расходы [today|week|month|стат]          -- Расходы
добавить расход <сумма> <описание>       -- Ручной расход
отчёт / report [месяц]                  -- Финансовый отчёт
исправить <ID> <field> <value>           -- Коррекция + урок
заметки / notes                          -- Заметки
уроки / lessons [стат]                   -- Уроки бота
ожидающие / pending                      -- Pending approvals
подтверждения / approvals                -- История
одобрить <ID> / approve                  -- Одобрить
отклонить <ID> / reject                  -- Отклонить
архив / archive                          -- Архивация
настройки / settings                     -- Настройки
назад / back                             -- Навигация назад
```

---

## Все .env переменные

```bash
# === Обязательные ===
TELEGRAM_BOT_TOKEN=7123456789:AAH...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
ALLOWED_USER_IDS=6905404901,5939002952,1336041242

# === WhatsApp (если нужен) ===
WHATSAPP_TOKEN=EAAxxxxxx...
WHATSAPP_PHONE_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=my_secret_verify_token
WHATSAPP_APP_SECRET=abc123...
WHATSAPP_ALLOWED_PHONES=971553096985,971525007780

# === Админ-бот (если нужен) ===
ADMIN_BOT_TOKEN=7123456789:BBH...
ADMIN_USER_IDS=6905404901
ADMIN_API_TOKEN=my_webhook_secret
ENFORCE_HTTPS=true

# === Google APIs ===
GOOGLE_VISION_API_KEY=AIza...
GOOGLE_MAPS_API_KEY=AIza...
GOOGLE_TRANSLATE_API_KEY=AIza...
GOOGLE_DRIVE_CREDENTIALS=data/google_credentials.json
GOOGLE_DRIVE_FOLDER_ID=1ABC...
GOOGLE_SHEETS_CREDENTIALS=data/google_sheets_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=1ABC...

# === Облачные сервисы ===
YANDEX_DISK_TOKEN=y0_AgAAAABk5...
BITRIX24_DOMAIN=xxx.bitrix24.ru
BITRIX24_USER_ID=1
BITRIX24_WEBHOOK_KEY=abc123...

# === Опциональные ===
WHISPER_MODEL=large-v3
WHISPER_DEVICE=cuda
FORCE_GROQ_STT=false
DB_PATH=data/transcriptions.db
TEMP_DIR=temp/
WEBHOOK_URL=https://webhook.vipdxbrus.com
ENABLE_DIARIZATION=false
EXCHANGE_RATE_API_KEY=abc123...
```

---

## Команды админ-бота (47+)

> Отдельный Telegram-бот для мониторинга переписок. 8 модулей: handlers, notifier, scheduler, console, suggester, monitor, spam_guard, api

```
/start                  -- Статус всех ботов
/chats [tg|wa]          -- Список чатов + фильтр
/chat <id>              -- Открыть чат
/reply <id> <текст>     -- Ответить клиенту
/broadcast <текст>      -- Рассылка команде
/health                 -- Здоровье всех ботов
/stats                  -- Общая статистика
/errors                 -- Последние ошибки
/find <запрос>          -- Поиск клиента
/unread                 -- Непрочитанные
/alerts                 -- Негатив за 24ч
/sla                    -- Время ответа
/audit                  -- История действий
/note <id> <текст>      -- Заметка к чату
/tag <id> <тег>         -- Тег к чату
/tags                   -- Все теги
/assign <id> <имя>      -- Назначить ответственного
/ban / /unban           -- Чёрный список
/heatmap                -- Тепловая карта
/top                    -- Топ-10 клиентов
/funnel                 -- Воронка
/lost                   -- Потерянные клиенты
/revenue                -- Анализ доходов
/season                 -- Сезонный анализ
/phone <номер>          -- Карточка клиента
/access                 -- Управление доступом
/templates              -- Шаблоны ответов
/spam_status            -- Статус антиспама
```

---

## TaskType (LLM routing)

> `core/llm_client.py` — маршрутизация задач по моделям

| TaskType | Описание | Каскад |
|----------|----------|--------|
| `summarize` | Резюме | gemini-2.5-flash → 2.0-flash → lite → Groq |
| `correct` | Коррекция | gemini-2.5-flash → 2.0-flash → lite → Groq |
| `sentiment` | Настроение | gemini-2.0-flash → lite → Groq |
| `translate` | Перевод | gemini-2.0-flash → lite → Groq |
| `categorize` | Категория | gemini-2.0-flash → lite → Groq |
| `improve` | Улучшение | gemini-2.5-flash → 2.0-flash → Groq |
| `format` | Форматирование | gemini-2.0-flash → lite → Groq |

---

## 9 бизнес-категорий

| Ключ | Название | Ответственный |
|------|----------|---------------|
| `excursions` | Экскурсии | Сухейль |
| `tickets` | Билеты | Сухейль |
| `parks` | Парки развлечений | Сухейль |
| `cars` | Автомобили | Марсель |
| `transfer` | Трансфер | Марсель |
| `mvu` | МВУ | Марсель |
| `yachts` | Яхты | Мухаммад-Амин |
| `water` | Водные развлечения | Мухаммад-Амин |
| `abayas` | Абаи/Одежда | Камила |
| `general` | Общее | Сухейль (fallback) |

---

## 11 категорий расходов

| ID | Название | Emoji keywords |
|----|----------|----------------|
| `fuel` | Топливо | бензин, adnoc, enoc |
| `maintenance` | Обслуживание | ремонт, сервис, шина |
| `carwash` | Мойка | мойка, полировка |
| `insurance` | Страховка | страховка, полис |
| `parking` | Парковка | парковка, mawaqif |
| `tolls` | Дорожные сборы | salik, штраф |
| `office` | Офис | офис, канцелярия |
| `food` | Еда | еда, обед, ресторан |
| `communication` | Связь | sim, etisalat, du |
| `transport` | Транспорт | такси, uber, metro |
| `other` | Прочее | (default) |

---

## Callback Prefixes (основные)

```
back:           -- Навигация назад
hist:           -- История (пагинация)
hist_full:      -- Детали записи
hist_cat_menu   -- Меню категорий
srch:           -- Поиск (пагинация)
dig:            -- Дайджест (период)
mrg:            -- Объединение (режим)
mrg_confirm:    -- Подтверждение объединения
exp_p:          -- Экспорт (период)
exp_f:          -- Экспорт (формат)
cl:             -- Клиент (карточка)
cl_hist:        -- История клиента
cl_del:         -- Удаление клиента
pin:            -- Toggle pin
bookmark:       -- Toggle bookmark
fix_voice_cat:  -- Коррекция категории
fix_voice_sent: -- Коррекция тональности
fix_rcpt:       -- Коррекция чека
approve:        -- Одобрить
reject:         -- Отклонить
vid_action:     -- Видео действие
vid_quality:    -- Видео качество
vid_format:     -- Видео формат
cloud_up:       -- Облачная загрузка
exp_e:          -- Расходы (период)
team_filter_    -- Фильтр команды
settings_       -- Настройки toggle
```

---

## Ключевые файлы проекта

```
D:/Downloads/VoiceTranscriptionBot/
├── bot/
│   ├── main.py              # Entry point Telegram
│   ├── handlers.py          # Хаб-маршрутизатор (258 строк) + 12 доменных модулей
│   ├── handlers_voice.py    # Голосовые + аудио
│   ├── handlers_video.py    # Видео-ссылки
│   ├── handlers_export.py   # Экспорт (PDF/Excel/MD/TXT)
│   ├── handlers_calc.py     # Калькулятор, маршруты
│   ├── handlers_callbacks.py # Inline-кнопки
│   ├── handlers_stats.py    # Статистика, дайджест, история
│   ├── handlers_clients.py  # Клиенты, расходы, уроки
│   ├── handlers_admin_commands.py # Approve/reject/archive
│   ├── handlers_text.py     # Текстовые триггеры
│   ├── handlers_common.py   # /start, /help, /settings
│   ├── handlers_templates.py # Шаблоны ответов
│   ├── config.py            # .env loader
│   ├── transcriber.py       # STT (faster-whisper + Groq)
│   ├── summarizer.py        # LLM (Gemini + Groq)
│   ├── database.py          # SQLite + FTS5 (~1764 строк)
│   └── auto_delete.py       # Auto-delete сервисных сообщений
├── whatsapp/
│   ├── app.py               # FastAPI entry point
│   ├── handlers.py          # WA команды (~2465 строк)
│   ├── client.py            # WhatsApp API wrapper
│   └── security.py          # HMAC + timestamp verification
├── core/
│   ├── pipeline.py          # Voice/Image/Video pipeline
│   ├── categories.py        # 9 категорий + keyword matching
│   ├── urgency.py           # Urgency detection (regex)
│   ├── sentiment.py         # Sentiment analysis (LLM)
│   ├── corrector.py         # Auto-correction (LLM)
│   ├── key_facts.py         # Facts extraction (LLM + regex)
│   ├── translator.py        # Translation to Russian
│   ├── note_detector.py     # Voice note detection
│   ├── combiner.py          # Multi-voice combiner
│   ├── reminders.py         # Date extraction for reminders
│   ├── accounting.py        # Receipt parser (Gemini Vision)
│   ├── expense_categories.py # 11 expense categories
│   ├── export_expenses.py   # PDF + Excel reports
│   ├── ocr.py               # OCR pipeline
│   ├── video_downloader.py  # yt-dlp wrapper
│   ├── video_manager.py     # Video SQLite tracking
│   ├── cloud_storage.py     # Google Drive + Yandex Disk
│   ├── clients.py           # Client management (JSON)
│   ├── client_detector.py   # Client detection from text
│   ├── team.py              # Team profiles + routing
│   ├── prices.py            # Price list manager
│   ├── templates.py         # Quick reply templates
│   ├── lessons.py           # Self-learning system
│   ├── approval.py          # 2-level approval system
│   ├── digest.py            # Digest generation
│   ├── scheduler.py         # Background tasks
│   ├── services.py          # DI container (singletons)
│   ├── navigation.py        # Screen stack
│   ├── formatter.py         # 42+ format functions (~2490 строк)
│   ├── json_utils.py        # LLM JSON parser
│   ├── retry.py             # Async retry with backoff
│   ├── export_pdf.py        # PDF transcription reports
│   ├── export_xlsx.py       # Excel transcription reports
│   ├── export_md.py         # Markdown export
│   ├── exporter.py          # TXT export
│   ├── calculator.py        # Tour calculator, currencies
│   ├── router.py            # Google Maps routes, TSP
│   ├── improver.py          # AI text improvement
│   ├── llm_client.py        # Unified LLM client (TaskType)
│   ├── response_builder.py  # Build voice response (TG/WA)
│   ├── expiring_dict.py     # Dict with TTL + size limit
│   ├── log_sanitizer.py     # API key masking in logs
│   ├── validators.py        # .env validation at startup
│   ├── health.py            # Healthcheck (ports 8081/8082)
│   ├── backup.py            # Auto DB backups (daily 04:00)
│   ├── api_monitor.py       # API token usage tracking
│   ├── logging_config.py    # Log rotation (10MB x 5)
│   ├── bitrix24.py          # Bitrix24 auto-leads
│   └── db_security.py       # SQLite encryption prep
├── data/
│   ├── transcriptions.db    # SQLite (auto-created)
│   ├── clients.json         # Client database
│   ├── team.json            # Team profiles
│   ├── prices.json          # Price list
│   ├── templates.json       # Templates
│   ├── lessons.json         # Learned lessons
│   ├── pending_approvals.json # Approval requests
│   └── fonts/               # DejaVu for PDF Cyrillic
├── admin/
│   ├── main.py              # Entry point Admin bot
│   ├── handlers.py          # Команды + inline-кнопки
│   ├── notifier.py          # Пересылка + автоответчик
│   ├── scheduler.py         # Ежедневный отчёт 22:00
│   ├── console.py           # CLI-интерфейс
│   ├── suggester.py         # AI-суфлёр (3 модели)
│   ├── monitor.py           # Heartbeat, API, диск, логи
│   ├── spam_guard.py        # Антиспам (50 msg/min)
│   ├── handlers_analytics.py # /lost, /revenue, /season
│   ├── handlers_crm.py      # /phone, карточка, воронка
│   ├── handlers_security.py # FULL/VIEW доступ, /audit
│   ├── handlers_integrations.py # /export_contacts, /notification_mode
│   └── api.py               # Webhook API (POST /api/admin/notify)
├── scripts/
│   ├── start_telegram.bat   # Windows launcher TG
│   ├── start_whatsapp.bat   # Windows launcher WA
│   ├── start_admin.bat      # Windows launcher Admin
│   ├── start_both.bat       # Windows launcher TG+WA
│   ├── start_all.bat        # Windows launcher all 3
│   ├── install_autostart.bat # Автозапуск Windows
│   ├── voice_bot.service    # systemd Telegram
│   ├── whatsapp_bot.service # systemd WhatsApp
│   ├── nginx_whatsapp.conf  # nginx config
│   └── start_tunnel.sh/bat  # Cloudflare Tunnel
├── .github/workflows/
│   ├── tests.yml            # CI: автотесты
│   └── lint.yml             # CI: линтинг
├── Dockerfile               # Multi-stage (Python 3.13)
├── docker-compose.yml       # 3 сервиса
├── .env                     # Secrets (not in git)
├── .env.example             # Template
├── requirements.txt         # Full (with GPU)
└── requirements-server.txt  # Server (no GPU)
```

---

## Ключевые функции

### Pipeline

```python
process_voice(audio_path, user_id, platform, method_prefix, progress_callback) -> PipelineResult
process_image(image_path, user_id, platform, method_prefix, source_type, progress_callback) -> PipelineResult
process_video_for_transcription(url, services_container, user_id, temp_dir) -> PipelineResult
```

### STT

```python
Transcriber.transcribe(file_path) -> TranscriptionResult
Transcriber.transcribe_local(file_path) -> TranscriptionResult
Transcriber.transcribe_groq(file_path) -> TranscriptionResult
```

### LLM

```python
Summarizer.summarize(text, duration) -> SummaryResult
Summarizer.summarize_gemini(text, duration) -> SummaryResult
Summarizer.summarize_groq(text, duration) -> SummaryResult
correct_transcription(text, summarizer) -> (corrected_text, fixes)
analyze_sentiment(text, summarizer) -> (sentiment, reason)
translate_to_russian(text, language, summarizer) -> str | None
```

### Business

```python
categorize(text) -> (category, confidence, team_category)
detect_urgency(text) -> (is_urgent, matched_keywords)
detect_note(text) -> (is_note, clean_text, tags)
extract_key_facts(text) -> dict
parse_receipt(image_path) -> dict
```

### Services

```python
await init_services()        # Инициализация всех сервисов
services.transcriber         # STT
services.summarizer          # LLM
services.llm                 # Unified LLM client (TaskType routing)
services.db                  # Database
services.approval            # Approvals
services.lessons             # Lessons
services.prices              # Price list manager
services.video_downloader    # Video
services.yandex_disk         # Yandex Disk (optional)
services.google_drive        # Google Drive (optional)
services.cloud_tracker       # Cloud upload tracking
```

---

## Модели (hardcoded)

| Компонент | Model ID |
|-----------|----------|
| STT local | `large-v3` (config) |
| STT cloud | `whisper-large-v3` |
| LLM #1 | `gemini-2.5-flash` |
| LLM #2 | `gemini-2.0-flash` |
| LLM #3 | `gemini-2.0-flash-lite` |
| LLM fallback | `llama-3.3-70b-versatile` |

---

## Константы

| Константа | Значение |
|-----------|----------|
| Dictation threshold | 180 сек (3 мин) |
| beam_size | 5 |
| retry max_retries | 2 |
| retry backoff_base | 1.0 сек |
| Min text for correction | 10 chars |
| Min text for sentiment | 10 chars |
| FTS text truncation | 200 chars |
| Max lessons per prompt | 7 |
| Stale lessons | 90 дней |
| Archive transcriptions | 180 дней |
| Cloud expires | 2 дня |
| Approval Level A | 24 часа |
| Approval Level B | 48 часов |
| DELAY_CONFIRM | 15 сек |
| DELAY_ERROR | 20 сек |
| DELAY_HINT | 25 сек |
| Nav stack max | 20 |
| Queue display threshold | 5 |
| Digest default time | 21:00 Dubai |
| Telegram file limit | 50 MB |
| Google Drive chunk | 5 MB |
| WA button title max | 20 chars |
| WA list row title max | 24 chars |
| WA text max | 4096 chars |

---

## Тесты

```bash
cd D:/Downloads/VoiceTranscriptionBot
python -m pytest tests/ -v          # Все ~2138 тестов
python -m pytest tests/ -x          # Стоп на первой ошибке
python -m pytest tests/test_X.py    # Один файл
```

---

## Быстрый запуск

### Windows (с GPU) — все 3 бота

```batch
cd /d D:\Downloads\VoiceTranscriptionBot
pip install -r requirements.txt
scripts\start_all.bat
```

### Windows — по отдельности

```batch
scripts\start_telegram.bat    # Только Telegram
scripts\start_whatsapp.bat    # Только WhatsApp
scripts\start_admin.bat       # Только Admin
```

### Сервер (без GPU)

```bash
pip install -r requirements-server.txt
# В .env: FORCE_GROQ_STT=true
sudo systemctl start voice_bot whatsapp_bot admin_bot
```

### Docker

```bash
docker-compose up -d           # Все 3 сервиса
docker-compose logs -f         # Логи
docker-compose restart telegram # Перезапуск одного
```
