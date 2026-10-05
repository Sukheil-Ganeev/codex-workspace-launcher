#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Экспорт JSON данных в CSV для импорта в Airtable.

Входные файлы:
- contacts.json, profiles.json, referrals.json, operations.json (если есть)

Выходные файлы:
- contacts.csv, profiles.csv, referrals.csv, operations.csv
- IMPORT_README.md, base_schema.json
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from config import JSON_DIR, CSV_DIR, AIRTABLE_DIR, ensure_directories

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ
# ═══════════════════════════════════════════════════════════════

UTF8_BOM = '\ufeff'

# Колонки для каждой таблицы
CONTACTS_COLUMNS = [
    'Name', 'Phone', 'JID', 'Type', 'Subtype', 'Source',
    'First_Message', 'Last_Message', 'Total_Messages',
    'Language', 'Country', 'Tags', 'Notes'
]

PROFILES_COLUMNS = [
    'Contact_Phone', 'Occupation', 'City', 'Communication_Style',
    'Price_Sensitivity', 'Tour_Types', 'Budget_Category', 'Total_Spent_AED'
]

REFERRALS_COLUMNS = [
    'Referrer_Phone', 'Referred_Phone', 'Source', 'Date', 'Confidence', 'Context'
]

OPERATIONS_COLUMNS = [
    'ID', 'Contact_Phone', 'Date', 'Type', 'Description',
    'Amount', 'Currency', 'Status', 'Notes'
]


# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def format_date(value: Any) -> str:
    """Преобразовать дату в формат YYYY-MM-DD."""
    if not value:
        return ''

    if isinstance(value, str):
        # Пробуем разные форматы
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%Y-%m-%dT%H:%M:%S', '%d.%m.%Y %H:%M:%S']:
            try:
                dt = datetime.strptime(value.split('.')[0] if 'T' in value else value, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return value  # Возвращаем как есть если не распознали

    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')

    return str(value)


def format_array(value: Any) -> str:
    """Преобразовать массив в строку для Airtable Multiple Select."""
    if not value:
        return ''

    if isinstance(value, list):
        # Убираем пустые значения и приводим к строкам
        items = [str(item).strip() for item in value if item]
        return ', '.join(items)

    return str(value)


def format_number(value: Any) -> str:
    """Форматировать число."""
    if value is None or value == '':
        return ''

    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return f'{num:.2f}'
    except (ValueError, TypeError):
        return str(value)


def clean_text(value: Any) -> str:
    """Очистить текст для CSV."""
    if value is None:
        return ''

    text = str(value)
    # Заменяем переносы строк на пробелы
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Убираем лишние пробелы
    text = ' '.join(text.split())
    return text


def load_json(file_path: Path) -> Optional[List[Dict]]:
    """Загрузить JSON файл."""
    if not file_path.exists():
        print(f"  [!] Файл не найден: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            # Возможно данные в обёртке
            for key in ['data', 'items', 'records', 'contacts', 'profiles', 'referrals', 'operations']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # Возвращаем как единственный элемент
            return [data]

        return data

    except json.JSONDecodeError as e:
        print(f"  [!] Ошибка парсинга JSON: {file_path} - {e}")
        return None


def save_csv(file_path: Path, columns: List[str], rows: List[Dict]):
    """Сохранить данные в CSV с UTF-8 BOM."""
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ CONTACTS
# ═══════════════════════════════════════════════════════════════

def export_contacts(input_path: Path, output_path: Path) -> int:
    """Экспортировать контакты в CSV."""
    data = load_json(input_path)
    if not data:
        return 0

    rows = []
    for item in data:
        row = {
            'Name': clean_text(item.get('name', '')),
            'Phone': clean_text(item.get('phone', '')),
            'JID': clean_text(item.get('jid', '')),
            'Type': clean_text(item.get('type', '')),
            'Subtype': clean_text(item.get('subtype', '')),
            'Source': clean_text(item.get('source', '')),
            'First_Message': format_date(item.get('first_message', item.get('firstMessage', ''))),
            'Last_Message': format_date(item.get('last_message', item.get('lastMessage', ''))),
            'Total_Messages': format_number(item.get('total_messages', item.get('totalMessages', item.get('message_count', 0)))),
            'Language': clean_text(item.get('language', '')),
            'Country': clean_text(item.get('country', '')),
            'Tags': format_array(item.get('tags', [])),
            'Notes': clean_text(item.get('notes', item.get('comment', ''))),
        }
        rows.append(row)

    save_csv(output_path, CONTACTS_COLUMNS, rows)
    return len(rows)


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ PROFILES
# ═══════════════════════════════════════════════════════════════

def export_profiles(input_path: Path, output_path: Path) -> int:
    """Экспортировать профили в CSV."""
    data = load_json(input_path)
    if not data:
        return 0

    rows = []
    for item in data:
        row = {
            'Contact_Phone': clean_text(item.get('phone', item.get('contact_phone', ''))),
            'Occupation': clean_text(item.get('occupation', '')),
            'City': clean_text(item.get('city', '')),
            'Communication_Style': clean_text(item.get('communication_style', item.get('communicationStyle', ''))),
            'Price_Sensitivity': clean_text(item.get('price_sensitivity', item.get('priceSensitivity', ''))),
            'Tour_Types': format_array(item.get('tour_types', item.get('tourTypes', item.get('preferred_tours', [])))),
            'Budget_Category': clean_text(item.get('budget_category', item.get('budgetCategory', ''))),
            'Total_Spent_AED': format_number(item.get('total_spent_aed', item.get('totalSpentAED', item.get('total_spent', 0)))),
        }
        rows.append(row)

    save_csv(output_path, PROFILES_COLUMNS, rows)
    return len(rows)


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ REFERRALS
# ═══════════════════════════════════════════════════════════════

def export_referrals(input_path: Path, output_path: Path) -> int:
    """Экспортировать рефералы в CSV."""
    data = load_json(input_path)
    if not data:
        return 0

    rows = []
    for item in data:
        row = {
            'Referrer_Phone': clean_text(item.get('referrer_phone', item.get('referrerPhone', item.get('referrer', '')))),
            'Referred_Phone': clean_text(item.get('referred_phone', item.get('referredPhone', item.get('referred', '')))),
            'Source': clean_text(item.get('source', '')),
            'Date': format_date(item.get('date', '')),
            'Confidence': clean_text(item.get('confidence', '')),
            'Context': clean_text(item.get('context', item.get('note', ''))),
        }
        rows.append(row)

    save_csv(output_path, REFERRALS_COLUMNS, rows)
    return len(rows)


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ OPERATIONS
# ═══════════════════════════════════════════════════════════════

def export_operations(input_path: Path, output_path: Path) -> int:
    """Экспортировать операции в CSV."""
    data = load_json(input_path)
    if not data:
        return 0

    rows = []
    for idx, item in enumerate(data, 1):
        row = {
            'ID': str(item.get('id', idx)),
            'Contact_Phone': clean_text(item.get('phone', item.get('contact_phone', item.get('contact', '')))),
            'Date': format_date(item.get('date', '')),
            'Type': clean_text(item.get('type', item.get('operation_type', ''))),
            'Description': clean_text(item.get('description', item.get('operation', ''))),
            'Amount': format_number(item.get('amount', 0)),
            'Currency': clean_text(item.get('currency', 'AED')),
            'Status': clean_text(item.get('status', '')),
            'Notes': clean_text(item.get('notes', item.get('comment', ''))),
        }
        rows.append(row)

    save_csv(output_path, OPERATIONS_COLUMNS, rows)
    return len(rows)


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ README
# ═══════════════════════════════════════════════════════════════

def generate_readme(output_path: Path, stats: Dict[str, int]):
    """Создать инструкцию по импорту в Airtable."""
    readme = f"""# Инструкция по импорту в Airtable

## UAE Tourism AI Agent

*Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

---

## Статистика экспорта

| Таблица | Записей |
|---------|---------|
| Contacts | {stats.get('contacts', 0)} |
| Profiles | {stats.get('profiles', 0)} |
| Operations | {stats.get('operations', 0)} |
| Referrals | {stats.get('referrals', 0)} |

---

## Шаг 1: Создание базы

1. Перейдите на [airtable.com](https://airtable.com)
2. Нажмите **Add a base** > **Start from scratch**
3. Назовите базу: `UAE Tourism AI Agent`

---

## Шаг 2: Создание таблиц

**ВАЖНО:** Создавайте таблицы в указанном порядке для правильной настройки связей.

### 2.1. Таблица Contacts (главная)

1. Переименуйте первую таблицу в `Contacts`
2. Импортируйте `contacts.csv`:
   - Нажмите **+** справа от вкладки
   - Выберите **Import data** > **CSV file**
   - Загрузите `contacts.csv`
3. Настройте типы полей:

| Поле | Тип в Airtable |
|------|----------------|
| Name | Single line text (Primary) |
| Phone | Phone number |
| JID | Single line text |
| Type | Single select |
| Subtype | Single select |
| Source | Single select |
| First_Message | Date |
| Last_Message | Date |
| Total_Messages | Number (Integer) |
| Language | Single select |
| Country | Single select |
| Tags | Multiple select |
| Notes | Long text |

### 2.2. Таблица Profiles

1. Создайте таблицу `Profiles`
2. Импортируйте `profiles.csv`
3. Настройте типы полей:

| Поле | Тип в Airtable |
|------|----------------|
| Contact_Phone | **Link to Contacts** (по полю Phone) |
| Occupation | Single line text |
| City | Single select |
| Communication_Style | Single select |
| Price_Sensitivity | Single select |
| Tour_Types | Multiple select |
| Budget_Category | Single select |
| Total_Spent_AED | Currency (AED) |

### 2.3. Таблица Operations

1. Создайте таблицу `Operations`
2. Импортируйте `operations.csv`
3. Настройте типы полей:

| Поле | Тип в Airtable |
|------|----------------|
| ID | Autonumber |
| Contact_Phone | **Link to Contacts** (по полю Phone) |
| Date | Date |
| Type | Single select |
| Description | Single line text |
| Amount | Number (Decimal, 2 places) |
| Currency | Single select |
| Status | Single select |
| Notes | Long text |

### 2.4. Таблица Referrals

1. Создайте таблицу `Referrals`
2. Импортируйте `referrals.csv`
3. Настройте типы полей:

| Поле | Тип в Airtable |
|------|----------------|
| Referrer_Phone | **Link to Contacts** (Кто привёл) |
| Referred_Phone | **Link to Contacts** (Кого привели) |
| Source | Single line text |
| Date | Date |
| Confidence | Single select |
| Context | Long text |

---

## Шаг 3: Настройка связей

После импорта всех таблиц настройте связи:

### Contacts ↔ Profiles
- В таблице `Profiles` поле `Contact_Phone` преобразуйте в **Link to another record**
- Выберите таблицу `Contacts`
- Создайте lookup поле для имени контакта

### Contacts ↔ Operations
- В таблице `Operations` поле `Contact_Phone` преобразуйте в **Link to another record**
- Выберите таблицу `Contacts`
- Создайте rollup для суммы операций

### Contacts ↔ Referrals (двойная связь)
- `Referrer_Phone` → связь с `Contacts` (кто привёл)
- `Referred_Phone` → связь с `Contacts` (кого привели)

---

## Шаг 4: Создание представлений (Views)

### Рекомендуемые представления для Contacts:
- **Все контакты** (Grid view) - по умолчанию
- **Клиенты** (Grid view) - фильтр: Type = "клиенты"
- **Агенты** (Grid view) - фильтр: Type = "агенты"
- **Поставщики** (Grid view) - фильтр: Type = "поставщики"
- **Недавняя активность** (Grid view) - сортировка по Last_Message DESC
- **Kanban по типам** (Kanban view) - группировка по Type

### Рекомендуемые представления для Operations:
- **Все операции** (Grid view)
- **По дате** (Calendar view) - по полю Date
- **По типу** (Kanban view) - группировка по Type
- **Сводка** (Pivot table) - Amount по Type и Currency

---

## Шаг 5: Автоматизации (опционально)

### Уведомления о VIP клиентах
1. Trigger: When record updated (Contacts)
2. Condition: Type = "VIP"
3. Action: Send Slack/Email notification

### Расчёт LTV
1. В Contacts создайте Rollup поле
2. Выберите связь с Operations
3. Функция: SUM(Amount) where Currency = "AED"

---

## Файлы в экспорте

```
D:/Downloads/Chats/_база/
├── csv/
│   ├── contacts.csv
│   ├── profiles.csv
│   ├── referrals.csv
│   └── operations.csv
└── airtable/
    ├── IMPORT_README.md   (этот файл)
    └── base_schema.json   (схема базы)
```

---

## Возможные проблемы

### Кодировка
CSV файлы сохранены в UTF-8 с BOM. Если при импорте видите кракозябры:
1. Откройте CSV в текстовом редакторе
2. Пересохраните с кодировкой UTF-8

### Связи не работают
Убедитесь, что:
1. Phone в обеих таблицах совпадает точно
2. Нет пробелов или спецсимволов в телефонах

### Даты не распознаются
Все даты в формате YYYY-MM-DD (ISO 8601). Если Airtable не распознаёт:
1. Измените формат дат в настройках поля
2. Выберите ISO format

---

*Создано автоматически скриптом export_for_airtable.py*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme)


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ СХЕМЫ
# ═══════════════════════════════════════════════════════════════

def generate_schema(output_path: Path):
    """Создать JSON схему базы Airtable."""
    schema = {
        "name": "UAE Tourism AI Agent",
        "description": "База данных туристического AI-агента для работы с контактами, профилями, операциями и рефералами",
        "created": datetime.now().isoformat(),
        "tables": [
            {
                "name": "Contacts",
                "description": "Основная таблица контактов",
                "primaryField": "Name",
                "fields": [
                    {"name": "Name", "type": "singleLineText", "description": "Имя контакта"},
                    {"name": "Phone", "type": "phoneNumber", "description": "Номер телефона"},
                    {"name": "JID", "type": "singleLineText", "description": "WhatsApp JID"},
                    {"name": "Type", "type": "singleSelect", "options": ["клиенты", "агенты", "поставщики", "сотрудники"]},
                    {"name": "Subtype", "type": "singleSelect", "options": ["турист", "VIP", "корпоративный", "турагент", "туроператор", "B2B", "обменник", "водитель", "гид", "яхтсмен", "кейтеринг", "менеджер"]},
                    {"name": "Source", "type": "singleSelect", "options": ["whatsapp", "wa_business", "vcf", "manual"]},
                    {"name": "First_Message", "type": "date", "description": "Дата первого сообщения"},
                    {"name": "Last_Message", "type": "date", "description": "Дата последнего сообщения"},
                    {"name": "Total_Messages", "type": "number", "description": "Количество сообщений"},
                    {"name": "Language", "type": "singleSelect", "options": ["ru", "en", "ar", "mixed"]},
                    {"name": "Country", "type": "singleSelect", "options": ["RU", "UAE", "KZ", "BY", "UZ", "other"]},
                    {"name": "Tags", "type": "multipleSelects", "description": "Теги для фильтрации"},
                    {"name": "Notes", "type": "multilineText", "description": "Заметки"}
                ]
            },
            {
                "name": "Profiles",
                "description": "Расширенные профили контактов",
                "fields": [
                    {"name": "Contact_Phone", "type": "link", "linkedTable": "Contacts", "description": "Связь с контактом"},
                    {"name": "Occupation", "type": "singleLineText", "description": "Профессия/занятие"},
                    {"name": "City", "type": "singleSelect", "description": "Город проживания"},
                    {"name": "Communication_Style", "type": "singleSelect", "options": ["formal", "informal", "business", "friendly"]},
                    {"name": "Price_Sensitivity", "type": "singleSelect", "options": ["high", "medium", "low"]},
                    {"name": "Tour_Types", "type": "multipleSelects", "options": ["safari", "city_tour", "yacht", "tickets", "transfer", "vip"]},
                    {"name": "Budget_Category", "type": "singleSelect", "options": ["budget", "standard", "premium", "luxury"]},
                    {"name": "Total_Spent_AED", "type": "currency", "currencySymbol": "AED", "description": "Общая сумма покупок"}
                ]
            },
            {
                "name": "Operations",
                "description": "Финансовые операции и сделки",
                "fields": [
                    {"name": "ID", "type": "autoNumber"},
                    {"name": "Contact_Phone", "type": "link", "linkedTable": "Contacts"},
                    {"name": "Date", "type": "date"},
                    {"name": "Type", "type": "singleSelect", "options": ["tour", "transfer", "yacht", "tickets", "exchange", "car_rental", "catering", "other"]},
                    {"name": "Description", "type": "singleLineText"},
                    {"name": "Amount", "type": "number", "precision": 2},
                    {"name": "Currency", "type": "singleSelect", "options": ["AED", "USD", "RUB", "EUR"]},
                    {"name": "Status", "type": "singleSelect", "options": ["pending", "confirmed", "completed", "cancelled"]},
                    {"name": "Notes", "type": "multilineText"}
                ]
            },
            {
                "name": "Referrals",
                "description": "Реферальные связи между контактами",
                "fields": [
                    {"name": "Referrer_Phone", "type": "link", "linkedTable": "Contacts", "description": "Кто привёл"},
                    {"name": "Referred_Phone", "type": "link", "linkedTable": "Contacts", "description": "Кого привели"},
                    {"name": "Source", "type": "singleLineText", "description": "Источник информации"},
                    {"name": "Date", "type": "date"},
                    {"name": "Confidence", "type": "singleSelect", "options": ["high", "medium", "low"]},
                    {"name": "Context", "type": "multilineText", "description": "Контекст/цитата"}
                ]
            }
        ],
        "relationships": [
            {
                "from": {"table": "Profiles", "field": "Contact_Phone"},
                "to": {"table": "Contacts", "field": "Phone"},
                "type": "many-to-one"
            },
            {
                "from": {"table": "Operations", "field": "Contact_Phone"},
                "to": {"table": "Contacts", "field": "Phone"},
                "type": "many-to-one"
            },
            {
                "from": {"table": "Referrals", "field": "Referrer_Phone"},
                "to": {"table": "Contacts", "field": "Phone"},
                "type": "many-to-one"
            },
            {
                "from": {"table": "Referrals", "field": "Referred_Phone"},
                "to": {"table": "Contacts", "field": "Phone"},
                "type": "many-to-one"
            }
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Экспорт JSON в CSV для Airtable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python export_for_airtable.py                    # Экспортировать все
  python export_for_airtable.py --only contacts   # Только контакты
  python export_for_airtable.py --input /path     # Указать входную директорию
  python export_for_airtable.py --output /path    # Указать выходную директорию
        """
    )

    parser.add_argument('--input', '-i', type=Path, default=JSON_DIR,
                        help=f'Директория с JSON файлами (default: {JSON_DIR})')
    parser.add_argument('--output', '-o', type=Path, default=CSV_DIR,
                        help=f'Директория для CSV файлов (default: {CSV_DIR})')
    parser.add_argument('--airtable-dir', type=Path, default=AIRTABLE_DIR,
                        help=f'Директория для README и схемы (default: {AIRTABLE_DIR})')
    parser.add_argument('--only', choices=['contacts', 'profiles', 'referrals', 'operations'],
                        help='Экспортировать только указанную таблицу')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Минимальный вывод')

    args = parser.parse_args()

    # Создаём директории
    ensure_directories()
    args.output.mkdir(parents=True, exist_ok=True)
    args.airtable_dir.mkdir(parents=True, exist_ok=True)

    if not args.quiet:
        print("=" * 60)
        print("ЭКСПОРТ ДЛЯ AIRTABLE")
        print("=" * 60)
        print(f"Входная директория:  {args.input}")
        print(f"Выходная директория: {args.output}")
        print("-" * 60)

    stats = {}

    # Экспорт таблиц
    tables = [
        ('contacts', 'contacts.json', 'contacts.csv', export_contacts),
        ('profiles', 'profiles.json', 'profiles.csv', export_profiles),
        ('referrals', 'referrals.json', 'referrals.csv', export_referrals),
        ('operations', 'operations.json', 'operations.csv', export_operations),
    ]

    for name, json_file, csv_file, export_func in tables:
        if args.only and args.only != name:
            continue

        input_path = args.input / json_file
        output_path = args.output / csv_file

        if not args.quiet:
            print(f"\n[{name.upper()}]")
            print(f"  Вход:  {input_path}")
            print(f"  Выход: {output_path}")

        count = export_func(input_path, output_path)
        stats[name] = count

        if not args.quiet:
            if count > 0:
                print(f"  [OK] Экспортировано {count} записей")
            else:
                print(f"  [--] Нет данных для экспорта")

    # Генерация документации
    if not args.only:
        readme_path = args.airtable_dir / 'IMPORT_README.md'
        schema_path = args.airtable_dir / 'base_schema.json'

        if not args.quiet:
            print(f"\n[ДОКУМЕНТАЦИЯ]")

        generate_readme(readme_path, stats)
        if not args.quiet:
            print(f"  [OK] {readme_path}")

        generate_schema(schema_path)
        if not args.quiet:
            print(f"  [OK] {schema_path}")

    # Итоги
    if not args.quiet:
        print("\n" + "=" * 60)
        print("ИТОГИ")
        print("=" * 60)
        total = sum(stats.values())
        print(f"Всего экспортировано: {total} записей")
        for name, count in stats.items():
            print(f"  {name}: {count}")
        print("\nФайлы готовы к импорту в Airtable!")
        print(f"Инструкция: {args.airtable_dir / 'IMPORT_README.md'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
