# экспорт-whatsapp-чатов

## Описание
Автоматизирует экспорт и документирование WhatsApp чатов. Два режима: (1) ZIP-архив -- один чат с Whisper расшифровкой, (2) iTunes бэкап iPhone -- массовый экспорт ВСЕХ чатов (3000+) с медиа. Главный принцип: никакие данные НЕ теряются.

## Структура
```
экспорт-whatsapp-чатов/
├── SKILL.md                                  # Основной справочник
├── README.md                                 # Этот файл
├── assets/
│   └── templates/
│       └── output-template.md                # Шаблон выходного документа
├── experience/
│   ├── _index.md                             # Критические уроки (читать при активации!)
│   ├── fixes/
│   │   ├── F001_unicode_windows.md           # Юникод на Windows
│   │   └── F002_duplicates_check.md          # Проверка дубликатов
│   ├── improvements/
│   │   ├── I001_async_workers.md             # Асинхронные воркеры
│   │   └── I002_auto_backups.md              # Автобэкапы
│   ├── patterns/
│   │   ├── P001_session_handoff.md           # Передача сессий
│   │   └── P002_monitoring.md                # Мониторинг
│   └── warnings/
│       ├── W001_subagents_limit.md           # Лимиты субагентов
│       └── W002_json_vs_jsonl.md             # JSON vs JSONL
├── integrations/                             # Интеграции с внешними сервисами
│   ├── calendar.py                           # Google Calendar
│   ├── google_sheets.py                      # Google Sheets
│   ├── notion.py                             # Notion
│   └── telegram_bot.py                       # Telegram Bot
├── references/
│   ├── checklist.md                          # Чек-лист экспорта
│   ├── troubleshooting.md                    # Решение проблем
│   └── whisper-setup.md                      # Настройка Whisper
└── scripts/
    ├── config.py                             # Общая конфигурация
    ├── ai/                                   # AI-модули
    │   ├── auto_followup.py                  # Автоматические follow-up
    │   ├── auto_responder.py                 # Автоответчик
    │   ├── claude_classifier.py              # Классификация (Claude)
    │   ├── demand_forecast.py                # Прогноз спроса
    │   ├── sentiment_analysis.py             # Анализ тональности
    │   ├── smart_analysis.py                 # Умный анализ
    │   └── summarize_dialog.py               # Суммаризация диалогов
    ├── analysis/                             # Анализ чатов
    │   ├── analyze_activity_time.py          # Анализ времени активности
    │   ├── analyze_emoji.py                  # Анализ эмодзи
    │   ├── analyze_message_length.py         # Длина сообщений
    │   ├── analyze_trends.py                 # Тренды
    │   ├── analyze_words.py                  # Анализ слов
    │   ├── chat_statistics.py                # Статистика чатов
    │   ├── contact_graph.py                  # Граф контактов
    │   ├── detect_groups.py                  # Обнаружение групп
    │   ├── detect_language.py                # Определение языка
    │   ├── detect_spam.py                    # Обнаружение спама
    │   └── find_duplicates.py                # Поиск дубликатов
    ├── business/                             # Бизнес-аналитика
    │   ├── average_check.py                  # Средний чек
    │   ├── build_profiles.py                 # Профили клиентов
    │   ├── build_sales_funnel.py             # Воронка продаж
    │   ├── calculate_ltv.py                  # LTV
    │   ├── calculate_response_time.py        # Время ответа
    │   ├── classify_contacts.py              # Классификация контактов
    │   ├── detect_referrals.py               # Рефералы
    │   ├── dialog_duration.py                # Длительность диалогов
    │   ├── extract_complaints.py             # Жалобы
    │   ├── first_response_time.py            # Время первого ответа
    │   ├── manager_efficiency.py             # Эффективность менеджеров
    │   ├── rejection_analysis.py             # Анализ отказов
    │   ├── repeat_customers.py               # Повторные клиенты
    │   ├── seasonal_analysis.py              # Сезонный анализ
    │   └── source_conversion.py              # Конверсия по источникам
    ├── documents/                            # Генерация документов
    │   ├── contract_generator.py             # Контракты
    │   ├── generate_report.py                # Отчёты
    │   ├── invoice_generator.py              # Инвойсы
    │   └── voucher_generator.py              # Ваучеры
    ├── export/                               # Экспорт
    │   ├── build_document.py                 # Сборка документа
    │   ├── build_index.py                    # Индекс
    │   ├── export_for_airtable.py            # Airtable
    │   └── generate_templates.py             # Шаблоны
    ├── geo/                                  # Геоаналитика
    │   ├── client_heatmap.py                 # Тепловая карта
    │   ├── driver_routes.py                  # Маршруты
    │   └── pickup_optimizer.py               # Оптимизация пикапов
    ├── integrations/                         # Интеграции
    │   ├── bitrix24_integration.py           # Bitrix24
    │   ├── bitrix24_products.py              # Bitrix24 продукты
    │   ├── bitrix24_timeline.py              # Bitrix24 таймлайн
    │   ├── email_sync.py                     # Email
    │   ├── google_calendar_sync.py           # Google Calendar
    │   ├── google_sheets_export.py           # Google Sheets
    │   ├── notion_sync.py                    # Notion
    │   ├── telegram_bot.py                   # Telegram Bot
    │   └── whatsapp_api.py                   # WhatsApp API
    ├── lib/                                  # Библиотеки (JS)
    │   ├── bindings/utils.js
    │   ├── tom-select/                       # Tom Select (UI)
    │   └── vis-9.1.2/                        # vis-network (визуализация графов)
    ├── marketing/                            # Маркетинг
    │   ├── email_marketing.py                # Email-рассылки
    │   ├── instagram_parser.py               # Парсер Instagram
    │   ├── referral_program.py               # Реферальная программа
    │   └── sms_twilio.py                     # SMS (Twilio)
    ├── media/                                # Обработка медиа
    │   ├── document_ocr.py                   # OCR
    │   ├── image_analyzer.py                 # Анализ изображений
    │   ├── organize_media.py                 # Организация медиа
    │   ├── transcribe_whisper.py             # Whisper транскрипция
    │   ├── voice_transcriber.py              # Транскрипция голоса
    │   └── whisper_postprocess.py            # Постобработка Whisper
    ├── parsing/                              # Парсинг данных из чатов
    │   ├── extract_banking.py                # Банковские реквизиты
    │   ├── extract_contacts.py               # Контакты
    │   ├── extract_datetime.py               # Даты и время
    │   ├── extract_emails.py                 # Email-адреса
    │   ├── extract_forwarded.py              # Пересланные сообщения
    │   ├── extract_locations.py              # Локации
    │   ├── extract_operations.py             # Операции
    │   ├── extract_patterns.py               # Паттерны
    │   ├── extract_price_inquiries.py        # Ценовые запросы
    │   ├── extract_requisites.py             # Реквизиты
    │   ├── extract_todos.py                  # Задачи (TODO)
    │   ├── extract_travel_dates.py           # Даты поездок
    │   ├── extract_urls.py                   # URL-ссылки
    │   ├── parse_all_chats.py                # Парсинг всех чатов
    │   ├── parse_vcf.py                      # Парсинг VCF
    │   └── parse_vcf_advanced.py             # Расширенный парсинг VCF
    ├── partners/                             # Партнёры
    │   ├── agent_portal.py                   # Портал агентов
    │   ├── partner_api.py                    # API партнёров
    │   └── white_label.py                    # White-label
    ├── templates/                            # Шаблоны данных
    │   ├── auto_responses.json               # Автоответы
    │   └── contracts/                        # Шаблоны контрактов
    │       ├── agent_contract_template.json
    │       ├── car_rental_template.json
    │       ├── tour_template.json
    │       └── yacht_charter_template.json
    ├── utils/                                # Утилиты
    │   ├── diff_chats.py                     # Сравнение чатов
    │   ├── mask_data.py                      # Маскирование данных
    │   ├── process_all.py                    # Пакетная обработка
    │   └── search.py                         # Поиск по чатам
    └── visualization/                        # Визуализация
        ├── activity_heatmap.py               # Тепловая карта
        ├── dashboard.py                      # Дашборд
        └── financial_reports.py              # Финансовые отчёты
```

## Использование
Скилл активируется автоматически по триггерам в description: прикрепление ZIP-архива WhatsApp, запросы "экспортируй чат", "расшифруй переписку", "экспорт из бэкапа iPhone", "экспорт из iTunes", "все чаты WhatsApp".
