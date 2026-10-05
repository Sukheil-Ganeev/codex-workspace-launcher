# туризм-оаэ-автоматизация

## Описание
AI, боты, рассылки, автоматизация туристического бизнеса ОАЭ. Claude классификация, автоответы, дашборды. Скилл охватывает полный стек автоматизации: от классификации входящих сообщений через Anthropic API до визуализации финансовых отчётов.

## Структура
```
туризм-оаэ-автоматизация/
├── SKILL.md                                # Основной справочник
├── WORKFLOW.md                             # Рабочий процесс
├── README.md                               # Этот файл
├── assets/
│   ├── examples/
│   │   └── classified-message.json         # Пример классифицированного сообщения
│   └── templates/
├── experience/
│   ├── _index.md                           # Критические уроки (читать при активации!)
│   ├── fixes/
│   ├── improvements/
│   ├── patterns/
│   └── warnings/
├── references/
│   ├── api-costs.md                        # Стоимость API (Claude, OpenAI, Whisper)
│   ├── faq.md                              # Часто задаваемые вопросы
│   ├── security.md                         # Безопасность и ключи
│   └── troubleshooting.md                  # Решение проблем
└── scripts/
    ├── config.py                           # Общая конфигурация
    ├── ai/                                 # AI-модули
    │   ├── auto_followup.py                # Автоматические follow-up
    │   ├── auto_responder.py               # Автоответчик
    │   ├── claude_classifier.py            # Классификация сообщений (Claude)
    │   ├── demand_forecast.py              # Прогноз спроса
    │   ├── sentiment_analysis.py           # Анализ тональности
    │   ├── smart_analysis.py               # Умный анализ
    │   └── summarize_dialog.py             # Суммаризация диалогов
    ├── marketing/                          # Маркетинг
    │   ├── email_marketing.py              # Email-рассылки
    │   ├── instagram_parser.py             # Парсер Instagram
    │   ├── referral_program.py             # Реферальная программа
    │   └── sms_twilio.py                   # SMS через Twilio
    ├── media/                              # Обработка медиа
    │   ├── document_ocr.py                 # OCR документов
    │   ├── image_analyzer.py               # Анализ изображений
    │   ├── organize_media.py               # Организация медиафайлов
    │   ├── transcribe_whisper.py           # Транскрипция (Whisper)
    │   ├── voice_transcriber.py            # Транскрипция голоса
    │   └── whisper_postprocess.py          # Постобработка Whisper
    ├── partners/                           # Партнёрские интеграции
    │   ├── agent_portal.py                 # Портал агентов
    │   ├── partner_api.py                  # API партнёров
    │   └── white_label.py                  # White-label решение
    └── visualization/                      # Визуализация
        ├── activity_heatmap.py             # Тепловая карта активности
        ├── dashboard.py                    # Дашборд
        └── financial_reports.py            # Финансовые отчёты
```

## Использование
Скилл активируется автоматически по триггерам в description: автоматизация процессов, AI-классификация, боты, рассылки, дашборды для туристического бизнеса ОАЭ.
