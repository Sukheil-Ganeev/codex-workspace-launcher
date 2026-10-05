# AI-агент: Подробная архитектура данных

Система данных для AI-агента туристического бизнеса.

---

## Компоненты системы

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Автоматизация | make.com | Сценарии обработки сообщений |
| База данных | Airtable | CRM + операции + метрики |
| AI-обработка | Claude API | Классификация, ответы, анализ |
| Коммуникация | WhatsApp Business API | Входящие/исходящие сообщения |

## Расположение данных

```
D:/Downloads/Chats/_база/
├── json/           # Машиночитаемые данные (для make.com)
│   ├── contacts.json
│   ├── profiles.json
│   ├── interactions.json
│   ├── operations.json
│   ├── referrals.json
│   ├── requisites.json
│   └── metrics.json
├── csv/            # Для импорта в Airtable
│   ├── contacts.csv
│   ├── profiles.csv
│   ├── operations.csv
│   └── referrals.csv
├── md/             # Человекочитаемые отчёты
├── airtable/       # Схема и инструкции
│   ├── IMPORT_README.md
│   └── base_schema.json
└── raw/            # Исходные JSONL
    ├── all_messages.jsonl
    └── chat_metadata.json
```

## Скрипты извлечения для AI-агента

| Скрипт | Вход | Выход |
|--------|------|-------|
| `parse_all_chats.py` | 3050 chat.txt | all_messages.jsonl |
| `extract_contacts.py` | all_messages.jsonl | contacts.json |
| `classify_contacts.py` | contacts.json | contacts.json (обновлённый) |
| `build_profiles.py` | all_messages.jsonl | profiles.json |
| `extract_interactions.py` | all_messages.jsonl | interactions.json |
| `detect_referrals.py` | all_messages.jsonl + VCF | referrals.json |
| `calculate_metrics.py` | все JSON | metrics.json |
| `export_for_airtable.py` | все JSON | *.csv |

## Формат chat.txt (экспортированный)

```
============================================================
ЧАТ: [Имя чата]
JID: [jid]@s.whatsapp.net или @g.us
Сообщений: [число]
Экспорт: DD.MM.YYYY HH:MM:SS
[ИСПРАВЛЕНО: имена участников группы]  # только для групп
============================================================

[DD.MM.YYYY HH:MM:SS] [Отправитель]:
  [текст сообщения]
  [медиа] media/filename или (медиа не сохранено в бэкапе)
```

---

## JSON-схемы сущностей

### contacts.json

```json
{
  "contacts": [{
    "contact_id": "uuid",
    "jid": "971501234567@s.whatsapp.net",
    "phone": "+971501234567",
    "name": "Имя из адресной книги",
    "type": "клиент|агент|поставщик|сотрудник",
    "subtype": "турист|VIP|турагент|обменник|водитель",
    "source": "whatsapp|wa_business|both",
    "first_message_date": "2024-01-15T10:30:00",
    "last_message_date": "2026-01-26T12:00:00",
    "total_messages": 127,
    "messages_sent": 59,
    "messages_received": 68,
    "language": "ru|en|ar",
    "country_code": "971|7|1",
    "tags": ["обмен_валюты", "VIP"],
    "chat_folder": "Anna_79614598181"
  }]
}
```

### profiles.json

```json
{
  "profiles": [{
    "profile_id": "uuid",
    "contact_id": "uuid",
    "biography": {
      "occupation": "Бизнесмен",
      "city": "Москва"
    },
    "personality": {
      "communication_style": "formal|informal",
      "price_sensitivity": "low|medium|high"
    },
    "preferences": {
      "tour_types": ["индивидуальные", "VIP"],
      "budget_category": "premium"
    },
    "statistics": {
      "total_orders": 5,
      "total_spent_aed": 25000
    }
  }]
}
```

### operations.json

```json
{
  "operations": [{
    "operation_id": "uuid",
    "contact_id": "uuid",
    "type": "tour|transfer|yacht|tickets|exchange",
    "description": "Экскурсия в Абу-Даби",
    "date": "2026-01-25",
    "pax": 4,
    "amount": 2000,
    "currency": "AED",
    "status": "inquiry|booked|confirmed|completed",
    "payment_status": "unpaid|partial|paid"
  }]
}
```

---

## Airtable схема

**База:** "UAE Tourism AI Agent"

**Таблицы:**
1. Contacts (основная) — связь 1:N с Operations
2. Profiles (1:1 с Contacts)
3. Operations (N:1 с Contacts)
4. Interactions (N:1 с Contacts)
5. Requisites (N:1 с Contacts)
6. Metrics (месячные агрегаты)

---

## Правила автоклассификации

```python
CLASSIFICATION_RULES = {
    "агенты": {
        "keywords": ["турагент", "комиссия", "%", "нетто", "партнёр"],
        "subtypes": {"турагент": ["agency", "travel"], "B2B": ["wholesale"]}
    },
    "поставщики": {
        "keywords": ["обменник", "курс", "водитель", "гид", "яхта"],
        "subtypes": {"обменник": ["exchange"], "водитель": ["driver"]}
    },
    "сотрудники": {
        "keywords": ["офис", "зарплата", "отпуск", "смена"],
        "phone_prefixes": ["971507705321"]
    },
    "клиенты": {
        "default": True,
        "keywords": ["бронирование", "экскурсия", "сколько стоит"],
        "subtypes": {"турист": ["экскурсия"], "VIP": ["premium", "private"]}
    }
}
```

---

## Аналитические скрипты

| Скрипт | Назначение | Выход |
|--------|------------|-------|
| `extract_price_inquiries.py` | Ценовые запросы клиентов | price_inquiries.json |
| `extract_travel_dates.py` | Даты прилёта/отлёта | travel_dates.json |
| `calculate_response_time.py` | Метрики времени отклика | response_times.json |
| `build_sales_funnel.py` | Воронка продаж | sales_funnel.json |
| `extract_complaints.py` | Жалобы и отмены | complaints.json |
| `seasonal_analysis.py` | Сезонный анализ | seasonal_analysis.json |
| `calculate_ltv.py` | LTV клиентов | ltv_analysis.json |

---

## Полный пайплайн обработки

```bash
cd C:/Users/londo/.claude/skills/экспорт-whatsapp-чатов/scripts

# Фаза 1: Парсинг
python parse_all_chats.py           # 3050 чатов → JSONL

# Фаза 2: Извлечение сущностей
python extract_contacts.py          # Контакты
python classify_contacts.py         # Классификация
python build_profiles.py            # Профили
python detect_referrals.py          # Рефералы

# Фаза 3: Аналитика
python extract_price_inquiries.py   # Ценовые запросы
python extract_travel_dates.py      # Даты поездок
python calculate_response_time.py   # Время отклика
python build_sales_funnel.py        # Воронка продаж
python extract_complaints.py        # Жалобы
python seasonal_analysis.py         # Сезонность
python calculate_ltv.py             # LTV клиентов

# Фаза 4: Экспорт
python export_for_airtable.py       # CSV для Airtable
python bitrix24_integration.py --sync-all  # Б24
```

---

## Интеграции

| Система | Скрипт | Описание |
|---------|--------|----------|
| **Airtable** | `export_for_airtable.py` | Экспорт CSV + схема |
| **Битрикс24** | `bitrix24_integration.py` | Синхронизация CRM |
