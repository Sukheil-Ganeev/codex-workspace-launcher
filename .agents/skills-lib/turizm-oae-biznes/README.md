# туризм-оаэ-бизнес

## Описание
CRM, документы, операции туристического бизнеса ОАЭ. Профили клиентов, инвойсы, контракты, интеграции. Ежедневные бизнес-операции: автоклассификация контактов, генерация документов, аналитика продаж, интеграции с внешними системами (Bitrix24, Google Sheets, Notion, Airtable).

## Структура
```
туризм-оаэ-бизнес/
├── SKILL.md                                  # Основной справочник
├── WORKFLOW.md                               # Рабочий процесс
├── README.md                                 # Этот файл
├── assets/
│   ├── examples/
│   │   ├── client-profile.json               # Пример профиля клиента
│   │   └── operation.json                    # Пример операции
│   └── templates/
├── experience/
│   ├── _index.md                             # Критические уроки (читать при активации!)
│   ├── fixes/
│   ├── improvements/
│   ├── patterns/
│   └── warnings/
├── references/
│   ├── airtable-schema.md                    # Схема Airtable базы
│   ├── faq.md                                # Часто задаваемые вопросы
│   └── troubleshooting.md                    # Решение проблем
└── scripts/
    ├── config.py                             # Общая конфигурация
    ├── business/                             # Бизнес-аналитика
    │   ├── average_check.py                  # Средний чек
    │   ├── build_profiles.py                 # Построение профилей клиентов
    │   ├── build_sales_funnel.py             # Воронка продаж
    │   ├── calculate_ltv.py                  # Расчёт LTV
    │   ├── calculate_response_time.py        # Время ответа
    │   ├── classify_contacts.py              # Классификация контактов
    │   ├── detect_referrals.py               # Обнаружение рефералов
    │   ├── dialog_duration.py                # Длительность диалогов
    │   ├── extract_complaints.py             # Извлечение жалоб
    │   ├── first_response_time.py            # Время первого ответа
    │   ├── manager_efficiency.py             # Эффективность менеджеров
    │   ├── rejection_analysis.py             # Анализ отказов
    │   ├── repeat_customers.py               # Повторные клиенты
    │   ├── seasonal_analysis.py              # Сезонный анализ
    │   └── source_conversion.py              # Конверсия по источникам
    ├── documents/                            # Генерация документов
    │   ├── contract_generator.py             # Генератор контрактов
    │   ├── generate_report.py                # Генератор отчётов
    │   ├── invoice_generator.py              # Генератор инвойсов
    │   └── voucher_generator.py              # Генератор ваучеров
    ├── export/                               # Экспорт данных
    │   ├── build_document.py                 # Сборка документа
    │   ├── build_index.py                    # Построение индекса
    │   ├── export_for_airtable.py            # Экспорт в Airtable
    │   └── generate_templates.py             # Генерация шаблонов
    ├── geo/                                  # Геоаналитика
    │   ├── client_heatmap.py                 # Тепловая карта клиентов
    │   ├── driver_routes.py                  # Маршруты водителей
    │   └── pickup_optimizer.py               # Оптимизация пикапов
    └── integrations/                         # Интеграции
        ├── bitrix24_integration.py           # Bitrix24 CRM
        ├── bitrix24_products.py              # Bitrix24 продукты
        ├── bitrix24_timeline.py              # Bitrix24 таймлайн
        ├── email_sync.py                     # Синхронизация email
        ├── google_calendar_sync.py           # Google Calendar
        ├── google_sheets_export.py           # Google Sheets
        └── notion_sync.py                    # Notion
```

## Использование
Скилл активируется автоматически по триггерам в description: бизнес-операции туризма, CRM профили, инвойсы, контракты, интеграции с внешними системами.
