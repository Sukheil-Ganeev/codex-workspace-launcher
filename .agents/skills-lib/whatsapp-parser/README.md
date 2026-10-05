# whatsapp-парсер

## Описание
Парсинг и анализ WhatsApp чатов туристического бизнеса ОАЭ. Извлечение контактов, сообщений, медиа, паттернов из 3,050 экспортированных чатов (WhatsApp Personal + Business).

## Структура
```
whatsapp-парсер/
├── SKILL.md              # Основной файл
├── README.md             # Этот файл
├── CONTACTS_TRACKER.md   # Трекер обработки контактов
├── WORKFLOW.md           # Описание рабочего процесса
├── references/           # Справочные материалы
│   ├── faq.md
│   ├── troubleshooting.md
│   ├── regex-cheatsheet.md
│   ├── entities-dictionary.md
│   ├── funnel-patterns.md
│   ├── multilingual.md
│   ├── pii-classification.md
│   ├── quality-metrics.md
│   ├── rejection-patterns.md
│   └── reply-parsing.md
├── assets/
│   ├── examples/
│   │   └── contact.json
│   └── templates/
│       └── message-jsonl.json
├── scripts/
│   ├── parsing/          # 20 скриптов парсинга
│   │   ├── parse_all_chats.py
│   │   ├── extract_contacts.py
│   │   ├── extract_banking.py
│   │   ├── extract_entities.py
│   │   ├── extract_financials.py
│   │   ├── extract_locations.py
│   │   ├── extract_urls.py
│   │   ├── transcribe_voice_messages.py
│   │   └── ... (и другие)
│   ├── analysis/         # 15 скриптов анализа
│   │   ├── chat_statistics.py
│   │   ├── contact_graph.py
│   │   ├── funnel_analysis.py
│   │   ├── intent_classifier.py
│   │   └── ... (и другие)
│   ├── utils/            # Утилиты
│   │   ├── config.py
│   │   ├── search.py
│   │   ├── mask_data.py
│   │   └── diff_chats.py
│   └── lib/              # Внешние библиотеки (vis.js, tom-select)
└── experience/           # Накопленный опыт (18 записей)
    ├── _index.md
    ├── fixes/            # F001-F002
    ├── improvements/     # I001-I002
    ├── patterns/         # P001-P010
    └── warnings/         # W001-W006
```

## Использование
Скилл активируется автоматически по триггерам в description.
