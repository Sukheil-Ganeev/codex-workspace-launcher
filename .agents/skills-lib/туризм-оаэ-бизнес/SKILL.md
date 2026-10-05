---
name: туризм-оаэ-бизнес
description: "CRM, документы, операции туристического бизнеса ОАЭ. Профили клиентов, инвойсы, контракты, интеграции. Используй для бизнес-операций туризма."
---
# Туризм ОАЭ - Бизнес

## Quick Start Guide (5 минут)

### 1. Проверьте данные
```bash
ls D:/Downloads/Chats/_база/json/
# Должны быть: contacts.json, profiles.json, operations.json
```

### 2. Классифицируйте контакты
```bash
python scripts/business/classify_contacts.py --dry-run  # Тест
python scripts/business/classify_contacts.py            # Запуск
```

### 3. Постройте профили клиентов
```bash
python scripts/business/build_profiles.py
```

### 4. Экспортируйте в Airtable
```bash
python scripts/export/export_for_airtable.py
# Результат: D:/Downloads/Chats/_база/csv/
```

### 5. Синхронизируйте с Bitrix24 (опционально)
```bash
export BITRIX24_DOMAIN="your-domain"
export BITRIX24_WEBHOOK_KEY="your-key"
python scripts/integrations/bitrix24_integration.py --sync-all
```

**Готово!** Теперь у вас есть классифицированные контакты и профили клиентов.

---

## Назначение

Ежедневные операции туристического бизнеса ОАЭ: CRM профили клиентов, автоклассификация контактов, генерация документов, аналитика продаж, интеграции с внешними системами (Bitrix24, Google Sheets, Notion, Airtable).

---

## Исходные данные

| Источник | Путь | Описание |
|----------|------|----------|
| Контакты | `D:/Downloads/Chats/_база/json/contacts.json` | 3050 контактов |
| Сообщения | `D:/Downloads/Chats/_база/raw/all_messages.jsonl` | ~887k сообщений |
| VCF контакты | `D:/Downloads/Chats/_база/json/vcf_contacts.json` | Из карточек |

---

## Результаты

```
D:/Downloads/Chats/_база/
├── json/
│   ├── contacts.json       # 3050 контактов (с type/subtype)
│   ├── profiles.json       # Профили клиентов
│   ├── operations.json     # Операции/сделки
│   ├── referrals.json      # Рефералы
│   ├── metrics.json        # Бизнес-метрики
│   └── requisites.json     # Банковские реквизиты
├── csv/                    # Для Airtable импорта
│   ├── contacts.csv
│   ├── profiles.csv
│   ├── operations.csv
│   └── referrals.csv
├── airtable/
│   ├── IMPORT_README.md    # Инструкция импорта
│   └── base_schema.json    # Схема базы Airtable
└── md/                     # Отчёты в Markdown
```

---

## Конфигурация путей (config.py)

```python
from pathlib import Path

# Корневые директории
CHATS_DIR = Path("D:/Downloads/Chats")
BASE_DIR = CHATS_DIR / "_база"

# Поддиректории для AI-агента
JSON_DIR = BASE_DIR / "json"
CSV_DIR = BASE_DIR / "csv"
MD_DIR = BASE_DIR / "md"
AIRTABLE_DIR = BASE_DIR / "airtable"
RAW_DIR = BASE_DIR / "raw"

# Источники экспортированных чатов
EXPORT_DIRS = [
    Path("D:/Downloads/экспорт чатов с ватсапа"),
    Path("D:/Downloads/экспорт чатов с ватсап бизнеса")
]

# API ключи (из переменных окружения)
API_KEYS = {
    'notion': os.getenv('NOTION_API_KEY', ''),
    'google_sheets': os.getenv('GOOGLE_SHEETS_CREDENTIALS', ''),
    'bitrix24_domain': os.getenv('BITRIX24_DOMAIN', ''),
    'bitrix24_webhook_key': os.getenv('BITRIX24_WEBHOOK_KEY', ''),
    'telegram_bot': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
}
```

---

## JSON Схемы

### Contact (контакт)

```json
{
  "contact_id": "uuid-v4",
  "jid": "971501234567@s.whatsapp.net",
  "phone": "+971501234567",
  "phone_clean": "971501234567",
  "country_code": "971",
  "name": "Марсель Ганеев",
  "display_name": "Марсель",
  "chat_folder": "Марсель_971507705321",
  "source": "wa_business",
  "is_group": false,
  "first_message_date": "2024-01-15T10:30:00",
  "last_message_date": "2026-01-26T12:00:00",
  "total_messages": 1547,
  "messages_sent": 720,
  "messages_received": 827,
  "language": "ru",
  "type": "клиенты",
  "subtype": "VIP",
  "tags": ["постоянный", "яхты"],
  "notes": "Предпочитает luxury услуги",
  "classification_scores": {
    "клиенты": 15,
    "агенты": 2,
    "поставщики": 0,
    "сотрудники": 0
  },
  "classified_at": "2026-01-26T18:00:00"
}
```

### Profile (профиль клиента)

```json
{
  "profile_id": "uuid-v4",
  "contact_id": "uuid-v4",
  "biography": {
    "occupation": "Предприниматель",
    "city": "Москва",
    "family_status": "married",
    "children": 2
  },
  "personality": {
    "communication_style": "formal",
    "price_sensitivity": "low",
    "decision_speed": "fast",
    "preferred_time": "morning"
  },
  "preferences": {
    "tour_types": ["yacht", "desert_safari", "helicopter"],
    "interests": ["luxury", "photography", "adventure"],
    "budget_category": "premium",
    "preferred_transport": "private"
  },
  "statistics": {
    "total_orders": 12,
    "total_spent_aed": 45000.00,
    "avg_order_value": 3750.00,
    "last_order_date": "2026-01-15"
  },
  "special_dates": {
    "birthday": "15.03",
    "anniversary": null
  },
  "extracted_from_chat": true
}
```

### Operation (операция/сделка)

```json
{
  "operation_id": "uuid-v4",
  "contact_id": "uuid-v4",
  "contact_phone": "+971501234567",
  "date": "2026-01-20",
  "type": "yacht",
  "description": "Аренда яхты 65ft на 4 часа",
  "amount": 3500.00,
  "currency": "AED",
  "status": "completed",
  "pax": 8,
  "pickup_location": "Dubai Marina",
  "pickup_time": "14:00",
  "notes": "День рождения клиента",
  "created_at": "2026-01-18T10:00:00",
  "completed_at": "2026-01-20T18:00:00"
}
```

### Referral (реферал)

```json
{
  "referral_id": "uuid-v4",
  "referrer_contact_id": "uuid-referrer",
  "referrer_name": "Анна Петрова",
  "referrer_phone": "+79161234567",
  "referred_contact_id": "uuid-referred",
  "referred_name": "Иван Сидоров",
  "referred_phone": "+79169876543",
  "source": "vcf",
  "detected_date": "2026-01-15",
  "confidence": 0.85,
  "context": "VCF карточка: Иван Сидоров (+79169876543)",
  "total_operations": 3,
  "total_revenue_aed": 12500.00,
  "commission_percent": 10,
  "commission_paid": false
}
```

### Requisites (банковские реквизиты)

```json
{
  "requisite_id": "uuid-v4",
  "contact_id": "uuid-v4",
  "type": "iban_uae",
  "value": "AE070331234567890123456",
  "bank_name": "Emirates NBD",
  "holder_name": "IVAN PETROV",
  "currency": "AED",
  "detected_date": "2026-01-10",
  "source_message_id": "msg-uuid",
  "verified": false
}
```

### Metrics (бизнес-метрики)

```json
{
  "generated_at": "2026-01-26T18:00:00",
  "period": {
    "from": "2026-01-01",
    "to": "2026-01-26"
  },
  "summary": {
    "total_contacts": 3050,
    "active_contacts": 450,
    "total_operations": 234,
    "total_revenue_aed": 185000.00,
    "avg_check_aed": 790.60
  },
  "by_type": {
    "tour": { "count": 85, "revenue": 42500 },
    "transfer": { "count": 67, "revenue": 13400 },
    "yacht": { "count": 23, "revenue": 69000 },
    "tickets": { "count": 45, "revenue": 22500 },
    "exchange": { "count": 12, "revenue": 36000 },
    "car_rental": { "count": 2, "revenue": 1600 }
  },
  "funnel": {
    "leads": 120,
    "qualified": 85,
    "proposal_sent": 65,
    "negotiation": 40,
    "won": 30,
    "lost": 10,
    "conversion_rate": 0.25
  },
  "response_time": {
    "avg_minutes": 15,
    "median_minutes": 8,
    "p95_minutes": 45
  }
}
```

---

## Правила автоклассификации контактов

### Диаграмма процесса классификации

```
Входящий контакт
     │
     ▼
┌─────────────────────────┐
│ [Проверка ключевых слов]│
└─────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│ "комиссия", "нетто" → Агент       │
│ "обмен", "курс" → Поставщик       │
│ "офис", "зарплата" → Сотрудник    │
│ иначе → Клиент                    │
└────────────────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│  [Определение подтипа]  │
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ Сохранение в            │
│ contacts.json           │
└─────────────────────────┘
```

### Алгоритм классификации (детали)

1. Загрузить все сообщения контакта
2. Подсчитать частоту ключевых слов по категориям
3. Проверить паттерны JID (группы)
4. Проверить паттерны имени
5. Проверить известные телефоны (сотрудники)
6. Категория с максимальным весом -> `type`
7. Подтип определить по подкатегориям
8. Если нет совпадений -> `type="клиенты"`, `subtype="турист"`

### Правила по категориям

```python
CLASSIFICATION_RULES = {
    "агенты": {
        "keywords": [
            "турагент", "турагентство", "агентство", "туроператор",
            "партнёр", "комиссия", "%", "нетто", "брутто",
            "travel", "tour", "agency"
        ],
        "jid_patterns": [r".*@g\.us$"],  # Группы часто агентские
        "name_patterns": [r".*tour.*", r".*travel.*", r".*agency.*"],
        "subtypes": {
            "турагент": ["турагент", "agency", "travel"],
            "туроператор": ["туроператор", "operator"],
            "B2B": ["B2B", "партнёр", "wholesale"]
        },
        "weight_multiplier": 1.0
    },
    "поставщики": {
        "keywords": [
            "обменник", "курс", "валюта", "exchange",
            "водитель", "driver", "трансфер",
            "гид", "guide", "экскурсовод",
            "яхта", "yacht", "капитан",
            "кейтеринг", "catering"
        ],
        "subtypes": {
            "обменник": ["обмен", "курс", "exchange", "валюта"],
            "водитель": ["водитель", "driver", "трансфер"],
            "гид": ["гид", "guide", "экскурсовод"],
            "яхтсмен": ["яхта", "yacht", "капитан"],
            "кейтеринг": ["кейтеринг", "catering", "еда"]
        },
        "weight_multiplier": 1.0
    },
    "сотрудники": {
        "keywords": [
            "офис", "зарплата", "отпуск", "рабочий",
            "смена", "график", "meeting"
        ],
        "phone_prefixes": ["971507705321"],  # Известные номера
        "subtypes": {
            "менеджер": ["менеджер", "manager"],
            "водитель_штат": ["водитель", "наш"],
            "админ": ["админ", "бухгалтер", "HR"]
        },
        "weight_multiplier": 100.0  # Гарантированное присвоение
    },
    "клиенты": {
        "default": True,
        "keywords": [
            "бронирование", "экскурсия", "тур", "билет",
            "хочу", "сколько стоит", "цена"
        ],
        "subtypes": {
            "турист": ["экскурсия", "тур", "отель"],
            "VIP": ["VIP", "люкс", "premium", "private"],
            "корпоративный": ["компания", "корпоратив", "team building"]
        },
        "weight_multiplier": 1.0
    }
}
```

### Типы и подтипы контактов

| Тип | Подтипы | Признаки |
|-----|---------|----------|
| **клиенты** | турист, VIP, корпоративный | Заказывает услуги, спрашивает цены |
| **агенты** | турагент, туроператор, B2B | Партнёр с комиссией, группы |
| **поставщики** | обменник, водитель, гид, яхтсмен, кейтеринг | Оказывает услуги |
| **сотрудники** | менеджер, водитель_штат, админ | Известные номера, офисные темы |

### Типы операций

| Тип | Ключевые слова |
|-----|----------------|
| `tour` | экскурсия, тур, сафари, museum, абу-даби |
| `transfer` | трансфер, встреча, аэропорт, transfer |
| `yacht` | яхта, yacht, катер, лодка |
| `tickets` | билет, парк, ferrari, aquaventure |
| `exchange` | обмен, курс, дирхам, рубль |
| `car_rental` | аренда, машина, авто, rental |
| `catering` | кейтеринг, еда, catering, food |

### Алгоритм расчёта LTV (Lifetime Value)

```
LTV = Средний чек × Частота заказов × Время жизни клиента × Маржа

Где:
- Средний чек = SUM(orders) / COUNT(orders)
- Частота = COUNT(orders) / месяцев_активности
- Время жизни = 24 месяца (средний показатель)
- Маржа = 0.20 (20%)
```

**Пример расчёта:**
```python
# Клиент за 12 месяцев сделал 6 заказов на общую сумму 30,000 AED
avg_check = 30000 / 6  # = 5000 AED
frequency = 6 / 12     # = 0.5 заказа/месяц
lifetime = 24          # месяцев
margin = 0.20          # 20%

LTV = 5000 * 0.5 * 24 * 0.20  # = 12,000 AED
```

**Категории LTV:**
| Категория | LTV (AED) | Рекомендуемые действия |
|-----------|-----------|------------------------|
| VIP | > 20,000 | Персональный менеджер, приоритет |
| Premium | 10,000 - 20,000 | Программа лояльности |
| Standard | 3,000 - 10,000 | Email-маркетинг |
| Low | < 3,000 | Автоматические рассылки |

---

## Скрипты

### business/ - Бизнес-логика (15 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `classify_contacts.py` | contacts.json, all_messages.jsonl | contacts.json (обновлён) | **Автоклассификация** контактов по type/subtype |
| `build_profiles.py` | contacts.json, all_messages.jsonl | profiles.json | **Построение профилей** клиентов из переписки |
| `build_sales_funnel.py` | operations.json | funnel.json | Воронка продаж по стадиям |
| `detect_referrals.py` | contacts.json, all_messages.jsonl | referrals.json | Обнаружение рефералов (VCF, упоминания) |
| `calculate_ltv.py` | profiles.json, operations.json | ltv.json | Расчёт LTV клиентов |
| `calculate_response_time.py` | all_messages.jsonl | response_time.json | Среднее время ответа менеджера |
| `first_response_time.py` | all_messages.jsonl | first_response.json | Время первого ответа |
| `repeat_customers.py` | operations.json | repeat.json | Анализ повторных клиентов |
| `average_check.py` | operations.json | avg_check.json | Средний чек по типам услуг |
| `seasonal_analysis.py` | operations.json | seasonal.json | Сезонность продаж |
| `source_conversion.py` | contacts.json, operations.json | conversion.json | Конверсия по источникам |
| `manager_efficiency.py` | all_messages.jsonl | efficiency.json | Эффективность менеджеров |
| `dialog_duration.py` | all_messages.jsonl | dialog_duration.json | Длительность диалогов |
| `rejection_analysis.py` | all_messages.jsonl | rejections.json | Анализ отказов |
| `extract_complaints.py` | all_messages.jsonl | complaints.json | Извлечение жалоб |

### integrations/ - Интеграции (7 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `bitrix24_integration.py` | contacts.json, operations.json | Bitrix24 CRM | **Синхронизация с Б24**: контакты, сделки, лиды |
| `bitrix24_products.py` | - | Bitrix24 | Создание товаров/услуг в Б24 |
| `bitrix24_timeline.py` | all_messages.jsonl | Bitrix24 | Добавление событий в таймлайн |
| `google_sheets_export.py` | *.json | Google Sheets | Экспорт данных в таблицы Google |
| `google_calendar_sync.py` | operations.json | Google Calendar | Синхронизация бронирований с календарём |
| `notion_sync.py` | contacts.json, operations.json | Notion | Синхронизация с базами Notion |
| `email_sync.py` | - | Gmail | Синхронизация email переписки |

### documents/ - Генерация документов (4 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `invoice_generator.py` | операция (CLI/JSON) | PDF/HTML инвойс | Генерация инвойсов |
| `contract_generator.py` | операция (CLI/JSON) | PDF/DOCX контракт | Генерация контрактов |
| `voucher_generator.py` | операция (CLI/JSON) | PDF ваучер | Генерация ваучеров |
| `generate_report.py` | metrics.json | PDF/MD отчёт | Генерация отчётов |

### geo/ - Геоаналитика (3 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `client_heatmap.py` | contacts.json (с локациями) | heatmap.html | Тепловая карта клиентов |
| `pickup_optimizer.py` | operations.json | optimized_routes.json | Оптимизация пикапов |
| `driver_routes.py` | operations.json | routes.json | Маршруты водителей |

### export/ - Экспорт данных (4 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `export_for_airtable.py` | *.json | *.csv + README.md | **Экспорт для Airtable** |
| `build_document.py` | шаблон + данные | документ | Сборка документов из шаблонов |
| `build_index.py` | *.json | index.json | Построение поискового индекса |
| `generate_templates.py` | - | templates/*.md | Генерация шаблонов |

---

## Airtable схема

### Таблица Contacts (главная)

| Поле | Тип Airtable | Описание |
|------|--------------|----------|
| Name | Single line text (Primary) | Имя контакта |
| Phone | Phone number | Номер телефона |
| JID | Single line text | WhatsApp JID |
| Type | Single select | клиенты/агенты/поставщики/сотрудники |
| Subtype | Single select | Подтип контакта |
| Source | Single select | whatsapp/wa_business/vcf/manual |
| First_Message | Date | Дата первого сообщения |
| Last_Message | Date | Дата последнего сообщения |
| Total_Messages | Number (Integer) | Количество сообщений |
| Language | Single select | ru/en/ar/mixed |
| Country | Single select | RU/UAE/KZ/BY/UZ/other |
| Tags | Multiple select | Теги для фильтрации |
| Notes | Long text | Заметки |

### Таблица Profiles

| Поле | Тип Airtable | Описание |
|------|--------------|----------|
| Contact_Phone | Link to Contacts | Связь с контактом |
| Occupation | Single line text | Профессия |
| City | Single select | Город |
| Communication_Style | Single select | formal/informal/business/friendly |
| Price_Sensitivity | Single select | high/medium/low |
| Tour_Types | Multiple select | Типы туров |
| Budget_Category | Single select | budget/standard/premium/luxury |
| Total_Spent_AED | Currency (AED) | Общая сумма покупок |

### Таблица Operations

| Поле | Тип Airtable | Описание |
|------|--------------|----------|
| ID | Autonumber | ID операции |
| Contact_Phone | Link to Contacts | Связь с контактом |
| Date | Date | Дата операции |
| Type | Single select | tour/transfer/yacht/tickets/exchange/car_rental |
| Description | Single line text | Описание |
| Amount | Number (Decimal) | Сумма |
| Currency | Single select | AED/USD/RUB/EUR |
| Status | Single select | pending/confirmed/completed/cancelled |
| Notes | Long text | Заметки |

### Таблица Referrals

| Поле | Тип Airtable | Описание |
|------|--------------|----------|
| Referrer_Phone | Link to Contacts | Кто привёл |
| Referred_Phone | Link to Contacts | Кого привели |
| Source | Single line text | vcf/mention/direct |
| Date | Date | Дата |
| Confidence | Single select | high/medium/low |
| Context | Long text | Контекст/цитата |

### Связи между таблицами

```
Contacts (1) ←→ (N) Profiles
Contacts (1) ←→ (N) Operations
Contacts (1) ←→ (N) Referrals (как referrer)
Contacts (1) ←→ (N) Referrals (как referred)
```

---

## Интеграции

### Bitrix24 CRM

**Настройка:**
```bash
export BITRIX24_DOMAIN="your-domain"
export BITRIX24_USER_ID="1"
export BITRIX24_WEBHOOK_KEY="your-webhook-key"
```

**Команды:**
```bash
# Настройка структуры Б24
python scripts/integrations/bitrix24_integration.py --setup-all

# Синхронизация контактов
python scripts/integrations/bitrix24_integration.py --contacts

# Синхронизация сделок
python scripts/integrations/bitrix24_integration.py --deals

# Полная синхронизация
python scripts/integrations/bitrix24_integration.py --sync-all

# Тестовый режим (без реальных изменений)
python scripts/integrations/bitrix24_integration.py --sync-all --dry-run
```

**Маппинг типов контактов:**
```python
CONTACT_TYPE_MAPPING = {
    "клиенты": "CLIENT",
    "агенты": "AGENT",
    "поставщики": "SUPPLIER",
    "сотрудники": "EMPLOYEE",
}
```

**Воронки продаж в Б24:**
- Туры и экскурсии
- Трансферы
- Яхты
- Билеты и парки

**Смарт-процессы:**
- Бронирования
- Рефералы
- Жалобы

### Google Sheets

**Настройка:**
```bash
export GOOGLE_SHEETS_CREDENTIALS="/path/to/credentials.json"
```

**Использование:**
```bash
python scripts/integrations/google_sheets_export.py \
  --input contacts.json \
  --spreadsheet "UAE Tourism CRM"
```

### Notion

**Настройка:**
```bash
export NOTION_API_KEY="secret_xxxxx"
```

**Использование:**
```bash
python scripts/integrations/notion_sync.py \
  --database-id "xxxxx" \
  --sync contacts
```

---

## Примеры использования

### Автоклассификация контактов

```bash
# Полная классификация
python scripts/business/classify_contacts.py

# Тестовый режим (без сохранения)
python scripts/business/classify_contacts.py --dry-run

# С подробным выводом
python scripts/business/classify_contacts.py --verbose
```

### Построение профилей клиентов

```bash
# Стандартный запуск
python scripts/business/build_profiles.py

# С указанием путей
python scripts/business/build_profiles.py \
  --contacts D:/Downloads/Chats/_база/json/contacts.json \
  --messages D:/Downloads/Chats/_база/raw/all_messages.jsonl \
  --output D:/Downloads/Chats/_база/json/profiles.json
```

### Обнаружение рефералов

```bash
python scripts/business/detect_referrals.py \
  --contacts D:/Downloads/Chats/_база/json/contacts.json \
  --messages D:/Downloads/Chats/_база/raw/all_messages.jsonl \
  -o D:/Downloads/Chats/_база/json/referrals.json
```

### Экспорт для Airtable

```bash
# Полный экспорт
python scripts/export/export_for_airtable.py

# Только контакты
python scripts/export/export_for_airtable.py --only contacts

# С указанием директорий
python scripts/export/export_for_airtable.py \
  --input D:/Downloads/Chats/_база/json \
  --output D:/Downloads/Chats/_база/csv
```

### Генерация инвойса

```bash
python scripts/documents/invoice_generator.py \
  --client "Иван Петров" \
  --phone "+971501234567" \
  --service "Desert Safari" \
  --amount 350 \
  --currency AED
```

---

## Полный пайплайн обработки

```bash
# 1. Классификация контактов
python scripts/business/classify_contacts.py

# 2. Построение профилей
python scripts/business/build_profiles.py

# 3. Обнаружение рефералов
python scripts/business/detect_referrals.py

# 4. Расчёт метрик
python scripts/business/calculate_ltv.py
python scripts/business/average_check.py
python scripts/business/calculate_response_time.py

# 5. Экспорт для Airtable
python scripts/export/export_for_airtable.py

# 6. Синхронизация с Bitrix24
python scripts/integrations/bitrix24_integration.py --sync-all
```

---

## Регулярные выражения

```python
import re

# Извлечение данных
PATTERNS = {
    'iban_uae': r'AE\d{21}',
    'card_ru': r'\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
    'phone_ru': r'\+7[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    'phone_uae': r'\+971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4}',
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'account_ru': r'\b408\d{17}\b',
    'bik': r'\b04\d{7}\b',
    'swift': r'\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
    'amount_rub': r'\b\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?\s*(?:руб|₽|RUB)\b',
    'amount_aed': r'\b\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?\s*(?:дирхам|AED)\b',
    'amount_usd': r'\b\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?\s*(?:долл|USD|\$)\b',
}
```

---

## CRM интеграции

### Bitrix24

**Настройка и синхронизация:**
```bash
export BITRIX24_DOMAIN="your-domain.bitrix24.ru"
export BITRIX24_USER_ID="1"
export BITRIX24_WEBHOOK_KEY="your-webhook-key"

# Синхронизация
python scripts/integrations/bitrix24_integration.py --sync-all
```

**Воронка продаж Bitrix24:**
```yaml
Туризм ОАЭ:
  1. NEW - Новый запрос
  2. PREPARATION - Уточнение деталей
  3. PREPAYMENT_INVOICE - Предложение отправлено
  4. EXECUTING - Ожидание оплаты
  5. PARTIAL_PAYMENT - Частичная оплата
  6. FINAL_INVOICE - Полная оплата
  7. IN_PROGRESS - В поездке
  8. WON - Успешно завершено
  9. LOSE - Отказ
```

**Кастомные поля:**
- `UF_CRM_WHATSAPP_ID` - ID чата WhatsApp
- `UF_CRM_TOUR_TYPE` - Тип тура (Экскурсия/Сафари/Яхта/Трансфер)
- `UF_CRM_ARRIVAL_DATE` - Дата приезда
- `UF_CRM_PAX` - Количество гостей

### amoCRM

**Интеграция через API:**
```python
# Создание сделки из WhatsApp
AMOCRM_CONFIG = {
    'subdomain': 'your-company',
    'client_id': 'xxx',
    'client_secret': 'xxx',
    'redirect_uri': 'https://your-server.com/amocrm/callback'
}

# Маппинг статусов воронки
PIPELINE_STAGES = {
    'new': 'Новая заявка',
    'qualified': 'Квалифицирован',
    'proposal': 'Предложение отправлено',
    'negotiation': 'Переговоры',
    'won': 'Успех',
    'lost': 'Отказ'
}
```

### Notion CRM

**Структура баз данных:**
```
📁 Tourism CRM (Notion)
├── 📋 Клиенты - связь с телефоном/WhatsApp ID
├── 📋 Сделки - воронка продаж
├── 📋 Туры - каталог услуг
├── 📋 Оплаты - история платежей
└── 📋 Задачи - канбан по статусу
```

**Свойства базы "Клиенты":**
| Property | Type | Description |
|----------|------|-------------|
| Имя | Title | Имя клиента |
| Телефон | Phone | WhatsApp номер |
| Статус | Select | Новый/Активный/VIP/Архив |
| Менеджер | Person | Ответственный |
| Общая сумма | Rollup | Sum of Сделки.Сумма |
| WhatsApp ID | Text | ID чата |

### Airtable

**Схема базы:**
```
📁 Tourism CRM (Airtable)
├── 📋 Contacts - связь WhatsApp ID → контакт
├── 📋 Deals - этапы воронки
├── 📋 Payments - оплаты
└── 📋 Tasks - задачи
```

**Автоматизации:**
- Новый контакт → уведомление в Slack
- Оплата → обновление статуса сделки
- Брошенная заявка (>2 дней) → задача менеджеру

---

## Маркетинг и реферальная программа

### Обнаружение рефералов из чатов

**Паттерны поиска:**
| Паттерн | Пример | Действие |
|---------|--------|----------|
| "от [имя]" | "Я от Марины" | Связать с клиентом |
| "порекомендовал/а" | "Нас порекомендовала Анна" | Найти в базе |
| "по рекомендации" | "По рекомендации коллеги" | Уточнить имя |

**Regex:**
```regex
(?:от|по рекомендации|посоветовал[аи]?|рекомендовал[аи]?)\s+([А-Яа-яЁё]+)
```

### Структура бонусов рефералов

| Уровень | Условие | Бонус рефереру | Бонус новому |
|---------|---------|----------------|--------------|
| Базовый | 1 реферал | 5% от заказа | Скидка 3% |
| Серебро | 3-5 рефералов | 7% от заказа | Скидка 5% |
| Золото | 6-10 рефералов | 10% от заказа | Скидка 7% |
| Платина | 11+ рефералов | 12% + VIP | Скидка 10% |

### RFM сегментация клиентов

**R** - Recency (давность), **F** - Frequency (частота), **M** - Monetary (сумма)

| Сегмент | RFM | Стратегия |
|---------|-----|-----------|
| **VIP Чемпионы** | 555, 554 | Персональный менеджер, эксклюзивы |
| **Лояльные** | 444, 435 | Программа лояльности, upsell |
| **Перспективные** | 513, 514 | Вовлечение, скидка на 2й заказ |
| **Спящие** | 244, 144 | Реактивация "Мы скучаем" + скидка |
| **В зоне риска** | 154, 155 | Опрос причин + бонус возврата |

### Источники трафика

| Источник | % | CAC | LTV | ROI |
|----------|---|-----|-----|-----|
| Рекомендации | 30% | $0 | $6000 | ∞ |
| Instagram | 40% | $300 | $4000 | 13x |
| Турагенты | 20% | $200 | $3500 | 17x |
| Google | 5% | $800 | $3000 | 3.75x |

### Программа лояльности

**Система баллов:**
| Действие | Баллы |
|----------|-------|
| $1 потрачен | 1 балл |
| Отзыв Google | 50 баллов |
| Успешный реферал | 200 баллов |
| День рождения | 100 баллов |

**Конвертация:** 100 баллов = $1 скидка

---

## Дашборды и отчёты

### Ежедневный дашборд

```
┌─────────────────┬─────────────────┬─────────────────┬───────────────────┐
│ НОВЫЕ ЗАПРОСЫ   │  КОНВЕРСИЯ      │  ВЫРУЧКА ДНЯ    │ ПРОБЛЕМНЫЕ ЧАТЫ   │
│     📥 47       │    🎯 12%       │   💰 $8,450     │      ⚠️ 3         │
│  (+8 vs вчера)  │ (+2% vs вчера)  │ (-$1.2K)        │ (требуют внимания)│
└─────────────────┴─────────────────┴─────────────────┴───────────────────┘
```

### Воронка продаж

| Этап | Конверсия | Цель |
|------|-----------|------|
| Запрос → Интерес | 60% | 70% |
| Интерес → Бронь | 60% | 65% |
| Бронь → Оплата | 80% | 85% |
| Оплата → Выполнено | 95% | 98% |

### Метрики качества

| Метрика | Формула | Цель |
|---------|---------|------|
| Время первого ответа (FRT) | AVG(first_response_time) | < 5 мин |
| Время до бронирования (TTB) | AVG(inquiry_to_booking) | < 2 дня |
| NPS | Promoters% - Detractors% | > 50 |
| CSAT | Довольных (4-5) / Всего | > 85% |

### Streamlit дашборд

```python
import streamlit as st
import plotly.express as px

def daily_dashboard():
    st.title("📊 Ежедневный дашборд")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Новые запросы", 47, 8)
    col2.metric("Конверсия", "12%", "2%")
    col3.metric("Выручка", "$8,450", "-$1,200")
    col4.metric("Проблемные чаты", 3, 1, delta_color="inverse")
```

### Финансовые отчёты

**Ключевые формулы:**
```python
Revenue = SUM(payments) - SUM(refunds)
Gross_Profit = Revenue - COGS
Gross_Margin = (Gross_Profit / Revenue) * 100
AOV = Revenue / Number_of_Orders
ROI = ((Revenue - Total_Costs) / Total_Costs) * 100
```

---

## KPI и показатели

### Показатели по клиентам

| Показатель | Формула | Цель | Частота |
|------------|---------|------|---------|
| Всего клиентов | COUNT(type=client) | Рост 10%/мес | Ежедневно |
| Новые клиенты | COUNT(first_contact THIS_MONTH) | 50+/месяц | Еженедельно |
| Активные (90д) | COUNT(last_message < 90 days) | 200+ | Ежедневно |
| Повторные | COUNT(orders > 1) / COUNT(all) | 30%+ | Ежемесячно |
| Churn rate | COUNT(inactive 90+ days) / COUNT(all) | < 20% | Ежемесячно |

### Показатели по продажам

| Показатель | Формула | Цель |
|------------|---------|------|
| **Конверсия** | bookings / inquiries | 25%+ |
| **Средний чек (AOV)** | SUM(revenue) / COUNT(orders) | 1500 AED |
| **LTV клиента** | AVG(total_spent_per_client) | 5000 AED |
| **CAC** | Marketing spend / New customers | < 500 AED |
| **LTV/CAC** | LTV / CAC | > 3:1 |

### Формулы расчёта

**LTV (Lifetime Value):**
```
LTV = Средний чек × Частота заказов × Время жизни × Маржа
```

**CAC (Customer Acquisition Cost):**
```
CAC = Расходы на маркетинг / Количество новых клиентов
```

**Churn Rate:**
```
Churn = (Клиенты на начало - Клиенты на конец + Новые) / Клиенты на начало
```

**NPS (Net Promoter Score):**
```
NPS = % Промоутеров (9-10) - % Критиков (0-6)
```

### Юнит-экономика

| Метрика | Формула | Пример |
|---------|---------|--------|
| **CAC** | Marketing / New customers | 500 AED |
| **LTV** | Avg order × Avg orders/customer | 4500 AED |
| **LTV/CAC** | LTV / CAC | 9x |
| **Payback** | CAC / (Avg order × Margin) | 1.5 мес |
| **ARPU** | Revenue / Active users | 750 AED/мес |

### Глоссарий KPI

| Термин | Определение |
|--------|-------------|
| **CAC** | Cost of Acquisition - стоимость привлечения |
| **LTV** | Lifetime Value - пожизненная ценность |
| **ARPU** | Average Revenue Per User |
| **Churn** | Отток клиентов |
| **NPS** | Net Promoter Score |
| **RFM** | Recency-Frequency-Monetary |
| **AOV** | Average Order Value |

---

## Связанные скиллы

| Скилл | Использует | Для чего |
|-------|------------|----------|
| **whatsapp-парсер** | Источник: contacts.json, all_messages.jsonl | Парсинг чатов WhatsApp |
| **туризм-оаэ-автоматизация** | Входные данные из этого скилла | AI классификация, автоответы |

---

## Производительность

| Операция | Время | Память |
|----------|-------|--------|
| Классификация 3050 контактов | ~3-5 мин | ~1.5 GB |
| Построение профилей | ~5-10 мин | ~2 GB |
| Обнаружение рефералов | ~2-3 мин | ~1 GB |
| Экспорт в Airtable | ~30 сек | ~500 MB |
| Синхронизация с Bitrix24 | ~10-20 мин | ~500 MB |

**Рекомендации:**
- Используйте SSD для быстрого I/O
- Для Bitrix24 используйте `--batch` флаг для батчевых запросов
- Результаты кэшируются в JSON для повторного использования

---

## Дополнительные ресурсы

Файлы с расширенными идеями и детальной документацией:

| Файл | Путь | Описание |
|------|------|----------|
| **CRM интеграции** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_CRM_ИНТЕГРАЦИИ.md` | Детальные схемы Airtable, Bitrix24, Notion, amoCRM с кодом интеграций |
| **Маркетинг и рефералы** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_МАРКЕТИНГ_РЕФЕРАЛЫ.md` | RFM-анализ, реферальная программа, email-маркетинг, ретаргетинг |
| **Дашборды и отчёты** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_ДАШБОРДЫ_ОТЧЁТЫ.md` | Streamlit код, Plotly графики, SQL запросы, макеты дашбордов |
| **KPI и показатели** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_И_ПОКАЗАТЕЛИ.md` | Полный набор KPI, формулы, чек-листы внедрения, глоссарий |

### Содержимое файлов идей

**ИДЕИ_CRM_ИНТЕГРАЦИИ.md:**
- Структура баз Airtable с формулами и автоматизациями
- PHP код интеграции Bitrix24 (webhooks, роботы, триггеры)
- Notion API синхронизация
- amoCRM воронки продаж
- Google Sheets экспорт

**ИДЕИ_МАРКЕТИНГ_РЕФЕРАЛЫ.md:**
- Многоуровневая реферальная система (до 3 уровней)
- RFM сегментация с примерами
- Email триггеры (welcome-серия, после покупки, ДР)
- Анализ конкурентов из чатов
- ROI маркетинговых каналов

**ИДЕИ_ДАШБОРДЫ_ОТЧЁТЫ.md:**
- 7 типов дашбордов с макетами (daily, funnel, quality, finance, team, customers, seasonality)
- Полный Streamlit код для каждого дашборда
- Plotly визуализации (воронка, gauge, heatmap, когорты)
- Metabase SQL запросы
- Docker деплой дашборда

**ИДЕИ_И_ПОКАЗАТЕЛИ.md:**
- Полный набор KPI по категориям (клиенты, продажи, качество)
- Customer Journey Map
- Юнит-экономика (CAC, LTV, ARPU, Payback)
- Идеи автоматизации (краткосрочные, среднесрочные, долгосрочные)
- Чек-лист внедрения по фазам
