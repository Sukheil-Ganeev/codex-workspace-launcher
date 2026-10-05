#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Google Sheets Export - Экспорт данных из WhatsApp аналитики в Google Sheets.

Использование:
    python google_sheets_export.py --all
    python google_sheets_export.py --contacts
    python google_sheets_export.py --all --spreadsheet-id "1abc..."
    python google_sheets_export.py --all --create "UAE Tourism Data"

Требуется установка:
    pip install gspread google-auth google-auth-oauthlib

Переменные окружения:
    GOOGLE_SHEETS_CREDENTIALS - путь к credentials.json (Service Account)
    GOOGLE_SHEETS_SPREADSHEET_ID - ID таблицы из URL (опционально)
"""

import argparse
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Установка UTF-8 для вывода в Windows консоль
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("ОШИБКА: Требуются библиотеки gspread и google-auth")
    print("Установите: pip install gspread google-auth google-auth-oauthlib")
    sys.exit(1)

# Импорт конфигурации
try:
    from config import JSON_DIR, API_KEYS
except ImportError:
    # Fallback если запускается из другой директории
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    API_KEYS = {
        'google_sheets': os.getenv('GOOGLE_SHEETS_CREDENTIALS', ''),
    }

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ
# ═══════════════════════════════════════════════════════════════

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Пути к JSON файлам
CONTACTS_JSON = JSON_DIR / "contacts.json"
OPERATIONS_JSON = JSON_DIR / "operations.json"
PROFILES_JSON = JSON_DIR / "profiles.json"
SALES_FUNNEL_JSON = JSON_DIR / "sales_funnel.json"
LTV_ANALYSIS_JSON = JSON_DIR / "ltv_analysis.json"

# Цвета для форматирования (RGB 0-1)
HEADER_COLOR = {"red": 0.2, "green": 0.4, "blue": 0.7}  # Синий
HEADER_TEXT_COLOR = {"red": 1, "green": 1, "blue": 1}    # Белый


# ═══════════════════════════════════════════════════════════════
# АВТОРИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

def get_credentials_path() -> str:
    """Получить путь к credentials.json."""
    # 1. Из переменной окружения
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS', '')
    if creds_path and Path(creds_path).exists():
        return creds_path

    # 2. Из config.py
    if API_KEYS.get('google_sheets') and Path(API_KEYS['google_sheets']).exists():
        return API_KEYS['google_sheets']

    # 3. Стандартные расположения
    standard_paths = [
        Path.home() / ".config" / "gspread" / "credentials.json",
        Path.home() / ".config" / "gspread" / "service_account.json",
        Path("credentials.json"),
        Path("service_account.json"),
        Path("D:/Downloads/credentials.json"),
    ]

    for path in standard_paths:
        if path.exists():
            return str(path)

    return ""


def authorize_gspread() -> gspread.Client:
    """Авторизация в Google Sheets API через Service Account."""
    creds_path = get_credentials_path()

    if not creds_path:
        print("\n" + "=" * 60)
        print("ОШИБКА: Не найден файл credentials.json")
        print("=" * 60)
        print_setup_instructions()
        sys.exit(1)

    print(f"Используем credentials: {creds_path}")

    try:
        credentials = Credentials.from_service_account_file(
            creds_path,
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        print("Авторизация успешна!")
        return client
    except Exception as e:
        print(f"ОШИБКА авторизации: {e}")
        print_setup_instructions()
        sys.exit(1)


def print_setup_instructions():
    """Вывести инструкции по настройке Google API."""
    instructions = """
╔══════════════════════════════════════════════════════════════════════╗
║           ИНСТРУКЦИЯ ПО НАСТРОЙКЕ GOOGLE SHEETS API                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. СОЗДАНИЕ ПРОЕКТА В GOOGLE CLOUD                                  ║
║     - Перейдите: https://console.cloud.google.com/                   ║
║     - Создайте новый проект или выберите существующий                ║
║                                                                      ║
║  2. ВКЛЮЧЕНИЕ API                                                    ║
║     - APIs & Services -> Library                                     ║
║     - Найдите и включите:                                            ║
║       * Google Sheets API                                            ║
║       * Google Drive API                                             ║
║                                                                      ║
║  3. СОЗДАНИЕ SERVICE ACCOUNT                                         ║
║     - APIs & Services -> Credentials                                 ║
║     - Create Credentials -> Service Account                          ║
║     - Дайте имя (например: sheets-export)                            ║
║     - Роль: Editor                                                   ║
║                                                                      ║
║  4. ГЕНЕРАЦИЯ КЛЮЧА                                                  ║
║     - Нажмите на созданный Service Account                           ║
║     - Keys -> Add Key -> Create new key -> JSON                      ║
║     - Сохраните файл как: credentials.json                           ║
║                                                                      ║
║  5. НАСТРОЙКА ПЕРЕМЕННОЙ ОКРУЖЕНИЯ                                   ║
║     Windows (PowerShell):                                            ║
║       $env:GOOGLE_SHEETS_CREDENTIALS = "D:/path/credentials.json"    ║
║                                                                      ║
║     Windows (CMD):                                                   ║
║       set GOOGLE_SHEETS_CREDENTIALS=D:/path/credentials.json         ║
║                                                                      ║
║     Или добавьте в системные переменные окружения                    ║
║                                                                      ║
║  6. ДОСТУП К ТАБЛИЦЕ (если используете существующую)                 ║
║     - Откройте Google Sheets таблицу                                 ║
║     - Поделитесь с email Service Account (из credentials.json)       ║
║     - Дайте права на редактирование                                  ║
║                                                                      ║
║  EMAIL Service Account можно найти в credentials.json:               ║
║    "client_email": "xxx@project.iam.gserviceaccount.com"             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(instructions)


# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_json(file_path: Path) -> Any:
    """Загрузить JSON файл."""
    if not file_path.exists():
        print(f"ВНИМАНИЕ: Файл не найден: {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def safe_get(d: dict, *keys, default=""):
    """Безопасное получение вложенных значений из словаря."""
    result = d
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default


# ═══════════════════════════════════════════════════════════════
# ФОРМАТИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

def format_header(worksheet: gspread.Worksheet, num_cols: int):
    """Форматировать заголовок (первая строка) - жирный + цвет."""
    try:
        worksheet.format(f"A1:{chr(64 + num_cols)}1", {
            "backgroundColor": HEADER_COLOR,
            "textFormat": {
                "foregroundColor": HEADER_TEXT_COLOR,
                "bold": True,
                "fontSize": 11
            },
            "horizontalAlignment": "CENTER"
        })
    except Exception as e:
        print(f"  Не удалось форматировать заголовок: {e}")


def auto_resize_columns(worksheet: gspread.Worksheet, num_cols: int):
    """Автоматическая ширина колонок (через batch_update)."""
    try:
        spreadsheet = worksheet.spreadsheet
        sheet_id = worksheet.id

        requests = [{
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": num_cols
                }
            }
        }]

        spreadsheet.batch_update({"requests": requests})
    except Exception as e:
        print(f"  Не удалось изменить ширину колонок: {e}")


def freeze_header(worksheet: gspread.Worksheet):
    """Заморозить первую строку."""
    try:
        worksheet.freeze(rows=1)
    except Exception as e:
        print(f"  Не удалось заморозить строку: {e}")


def add_timestamp(worksheet: gspread.Worksheet, row: int, col: int = 1):
    """Добавить timestamp последнего обновления."""
    try:
        timestamp = datetime.now().strftime("Обновлено: %Y-%m-%d %H:%M:%S")
        worksheet.update_cell(row, col, timestamp)
        worksheet.format(f"{chr(64 + col)}{row}", {
            "textFormat": {"italic": True, "fontSize": 9},
            "horizontalAlignment": "LEFT"
        })
    except Exception as e:
        print(f"  Не удалось добавить timestamp: {e}")


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def get_or_create_worksheet(spreadsheet: gspread.Spreadsheet,
                           name: str,
                           rows: int = 1000,
                           cols: int = 20) -> gspread.Worksheet:
    """Получить существующий лист или создать новый."""
    try:
        worksheet = spreadsheet.worksheet(name)
        print(f"  Найден существующий лист: {name}")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=name, rows=rows, cols=cols)
        print(f"  Создан новый лист: {name}")

    return worksheet


def export_contacts(spreadsheet: gspread.Spreadsheet,
                   worksheet_name: str = "Контакты") -> bool:
    """
    Экспорт контактов в Google Sheets.

    Колонки: Name, Phone, Type, Subtype, Source, Messages, Language,
             Country, Tags, Notes, LTV (AED), Orders, Segment
    """
    print(f"\n[КОНТАКТЫ] Экспорт в лист '{worksheet_name}'...")

    contacts = load_json(CONTACTS_JSON)
    if not contacts:
        print("  Нет данных для экспорта")
        return False

    # Заголовки
    headers = [
        "Имя", "Телефон", "Тип", "Подтип", "Источник",
        "Сообщений", "Язык", "Страна", "Теги", "Заметки",
        "LTV (AED)", "Заказов", "Сегмент", "Риск оттока"
    ]

    # Данные
    rows = [headers]
    for contact in contacts:
        ltv_data = contact.get('ltv', {})
        row = [
            contact.get('name', ''),
            contact.get('phone', ''),
            contact.get('type', ''),
            contact.get('subtype', ''),
            contact.get('source', ''),
            contact.get('total_messages', 0),
            contact.get('language', ''),
            contact.get('country', ''),
            ', '.join(contact.get('tags', [])),
            contact.get('notes', ''),
            ltv_data.get('historical_ltv_aed', 0) if ltv_data else 0,
            ltv_data.get('orders_count', 0) if ltv_data else 0,
            ltv_data.get('segment', '') if ltv_data else '',
            ltv_data.get('churn_risk', '') if ltv_data else ''
        ]
        rows.append(row)

    # Запись в Google Sheets
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_name)
    worksheet.clear()
    worksheet.update(range_name='A1', values=rows)

    # Форматирование
    format_header(worksheet, len(headers))
    freeze_header(worksheet)
    auto_resize_columns(worksheet, len(headers))
    add_timestamp(worksheet, len(rows) + 2)

    print(f"  Экспортировано контактов: {len(contacts)}")
    return True


def export_operations(spreadsheet: gspread.Spreadsheet,
                     worksheet_name: str = "Операции") -> bool:
    """
    Экспорт операций в Google Sheets.

    Колонки: ID, Date, Phone, Type, Description, Amount, Currency, Status, Notes
    """
    print(f"\n[ОПЕРАЦИИ] Экспорт в лист '{worksheet_name}'...")

    operations = load_json(OPERATIONS_JSON)
    if not operations:
        print("  Нет данных для экспорта")
        return False

    # Загрузим контакты для сопоставления имен
    contacts = load_json(CONTACTS_JSON) or []
    phone_to_name = {c.get('phone', ''): c.get('name', '') for c in contacts}

    # Заголовки
    headers = [
        "ID", "Дата", "Телефон", "Имя", "Тип",
        "Описание", "Сумма", "Валюта", "Статус", "Заметки"
    ]

    # Данные
    rows = [headers]
    for op in operations:
        phone = op.get('phone', '')
        row = [
            op.get('id', ''),
            op.get('date', ''),
            phone,
            phone_to_name.get(phone, ''),
            op.get('type', ''),
            op.get('description', ''),
            op.get('amount', 0),
            op.get('currency', 'AED'),
            op.get('status', ''),
            op.get('notes', '')
        ]
        rows.append(row)

    # Запись в Google Sheets
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_name)
    worksheet.clear()
    worksheet.update(range_name='A1', values=rows)

    # Форматирование
    format_header(worksheet, len(headers))
    freeze_header(worksheet)
    auto_resize_columns(worksheet, len(headers))
    add_timestamp(worksheet, len(rows) + 2)

    print(f"  Экспортировано операций: {len(operations)}")
    return True


def export_funnel(spreadsheet: gspread.Spreadsheet,
                 worksheet_name: str = "Воронка") -> bool:
    """
    Экспорт воронки продаж в Google Sheets.

    Создает сводную таблицу стадий воронки.
    """
    print(f"\n[ВОРОНКА] Экспорт в лист '{worksheet_name}'...")

    funnel_data = load_json(SALES_FUNNEL_JSON)
    if not funnel_data:
        print("  Нет данных для экспорта")
        return False

    funnel = funnel_data.get('funnel', {})

    # Заголовки
    headers = ["Стадия", "Количество", "Доля (%)", "Конверсия (%)"]

    # Названия стадий на русском
    stage_names = {
        'inquiry': 'Запрос',
        'quote': 'Расчет',
        'booking': 'Бронь',
        'payment': 'Оплата',
        'completed': 'Завершено',
        'lost': 'Потеряно'
    }

    # Данные
    rows = [headers]
    for stage_key, stage_name in stage_names.items():
        stage_data = funnel.get(stage_key, {})
        row = [
            stage_name,
            stage_data.get('count', 0),
            round(stage_data.get('rate', 0) * 100, 1),
            round(stage_data.get('conversion', 0) * 100, 1) if 'conversion' in stage_data else ''
        ]
        rows.append(row)

    # Добавляем раздел "По продуктам"
    rows.append([])
    rows.append(["По продуктам"])
    rows.append(["Продукт", "Запросов", "Расчетов", "Бронь"])

    by_product = funnel_data.get('by_product', {})
    for product, stages in by_product.items():
        row = [
            product,
            stages.get('inquiry', 0),
            stages.get('quote', 0),
            stages.get('booking', 0)
        ]
        rows.append(row)

    # Добавляем раздел "По месяцам"
    rows.append([])
    rows.append(["По месяцам"])
    rows.append(["Месяц", "Запросов", "Расчетов", "Бронь"])

    by_month = funnel_data.get('by_month', {})
    for month, stages in sorted(by_month.items()):
        row = [
            month,
            stages.get('inquiry', 0),
            stages.get('quote', 0),
            stages.get('booking', 0)
        ]
        rows.append(row)

    # Запись в Google Sheets
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_name)
    worksheet.clear()
    worksheet.update(range_name='A1', values=rows)

    # Форматирование
    format_header(worksheet, len(headers))
    freeze_header(worksheet)
    auto_resize_columns(worksheet, 10)
    add_timestamp(worksheet, len(rows) + 2)

    print(f"  Экспортировано стадий: {len(funnel)}")
    return True


def export_ltv(spreadsheet: gspread.Spreadsheet,
              worksheet_name: str = "LTV") -> bool:
    """
    Экспорт LTV анализа в Google Sheets.

    Топ клиентов по LTV + сводка по сегментам.
    """
    print(f"\n[LTV] Экспорт в лист '{worksheet_name}'...")

    ltv_data = load_json(LTV_ANALYSIS_JSON)
    if not ltv_data:
        print("  Нет данных для экспорта")
        return False

    # Заголовки для клиентов
    headers = [
        "Имя", "Телефон", "Тип", "LTV (AED)", "Заказов",
        "Ср. чек", "Сегмент", "Риск оттока", "Прогноз LTV (год)",
        "Бюджет", "Дней без заказов"
    ]

    # Данные по клиентам
    rows = [headers]
    ltv_by_contact = ltv_data.get('ltv_by_contact', [])

    # Сортируем по LTV (по убыванию)
    sorted_contacts = sorted(ltv_by_contact,
                            key=lambda x: x.get('historical_ltv_aed', 0),
                            reverse=True)

    for contact in sorted_contacts:
        row = [
            contact.get('name', ''),
            contact.get('phone', ''),
            contact.get('type', ''),
            contact.get('historical_ltv_aed', 0),
            contact.get('orders_count', 0),
            contact.get('avg_order_value', 0),
            contact.get('segment', ''),
            contact.get('churn_risk', ''),
            contact.get('predicted_ltv_next_year', 0),
            contact.get('budget_category', ''),
            contact.get('days_since_last_order', '')
        ]
        rows.append(row)

    # Сводка по сегментам
    rows.append([])
    rows.append(["СВОДКА ПО СЕГМЕНТАМ"])
    rows.append(["Сегмент", "Клиентов", "Общий LTV", "Средний LTV"])

    segments = ltv_data.get('segments', {})
    for segment_name, segment_data in segments.items():
        row = [
            segment_name,
            segment_data.get('count', 0),
            segment_data.get('total_ltv', 0),
            round(segment_data.get('avg_ltv', 0), 2)
        ]
        rows.append(row)

    # Общие метрики
    rows.append([])
    rows.append(["ОБЩИЕ МЕТРИКИ"])
    overall = ltv_data.get('overall', {})
    rows.append(["Общая выручка (AED)", overall.get('total_revenue', 0)])
    rows.append(["Всего клиентов", overall.get('total_customers', 0)])
    rows.append(["Средний LTV", overall.get('avg_ltv', 0)])
    rows.append(["Максимальный LTV", overall.get('max_ltv', 0)])
    rows.append(["Всего заказов", overall.get('total_orders', 0)])

    # Когорты
    rows.append([])
    rows.append(["КОГОРТЫ"])
    rows.append(["Когорта", "Клиентов", "Ср. LTV", "LTV 6м", "LTV 12м", "Ср. заказов"])

    cohorts = ltv_data.get('cohorts', {})
    for cohort_name, cohort_data in sorted(cohorts.items()):
        row = [
            cohort_name,
            cohort_data.get('customers', 0),
            round(cohort_data.get('avg_ltv', 0), 2),
            round(cohort_data.get('ltv_6m', 0), 2),
            round(cohort_data.get('ltv_12m', 0), 2),
            round(cohort_data.get('avg_orders', 0), 2)
        ]
        rows.append(row)

    # Запись в Google Sheets
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_name)
    worksheet.clear()
    worksheet.update(range_name='A1', values=rows)

    # Форматирование
    format_header(worksheet, len(headers))
    freeze_header(worksheet)
    auto_resize_columns(worksheet, len(headers))
    add_timestamp(worksheet, len(rows) + 2)

    print(f"  Экспортировано клиентов: {len(sorted_contacts)}")
    return True


def export_profiles(spreadsheet: gspread.Spreadsheet,
                   worksheet_name: str = "Профили") -> bool:
    """
    Экспорт профилей клиентов в Google Sheets.
    """
    print(f"\n[ПРОФИЛИ] Экспорт в лист '{worksheet_name}'...")

    profiles = load_json(PROFILES_JSON)
    if not profiles:
        print("  Нет данных для экспорта")
        return False

    # Заголовки
    headers = [
        "Телефон", "Профессия", "Город", "Стиль общения",
        "Чувствительность к цене", "Типы туров", "Бюджет", "Потрачено (AED)"
    ]

    # Данные
    rows = [headers]
    for profile in profiles:
        row = [
            profile.get('phone', ''),
            profile.get('occupation', ''),
            profile.get('city', ''),
            profile.get('communication_style', ''),
            profile.get('price_sensitivity', ''),
            ', '.join(profile.get('tour_types', [])),
            profile.get('budget_category', ''),
            profile.get('total_spent_aed', 0)
        ]
        rows.append(row)

    # Запись в Google Sheets
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_name)
    worksheet.clear()
    worksheet.update(range_name='A1', values=rows)

    # Форматирование
    format_header(worksheet, len(headers))
    freeze_header(worksheet)
    auto_resize_columns(worksheet, len(headers))
    add_timestamp(worksheet, len(rows) + 2)

    print(f"  Экспортировано профилей: {len(profiles)}")
    return True


# ═══════════════════════════════════════════════════════════════
# СОЗДАНИЕ ТАБЛИЦЫ
# ═══════════════════════════════════════════════════════════════

def create_spreadsheet(client: gspread.Client, title: str) -> gspread.Spreadsheet:
    """Создать новую Google Sheets таблицу."""
    print(f"\nСоздание новой таблицы: {title}")

    spreadsheet = client.create(title)

    # Получаем email из credentials для вывода
    creds_path = get_credentials_path()
    if creds_path:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
            service_email = creds_data.get('client_email', 'unknown')
            print(f"Таблица создана! Владелец: {service_email}")

    print(f"URL: {spreadsheet.url}")
    print(f"ID: {spreadsheet.id}")

    return spreadsheet


def open_spreadsheet(client: gspread.Client,
                    spreadsheet_id: Optional[str] = None) -> Optional[gspread.Spreadsheet]:
    """Открыть существующую таблицу по ID."""
    if not spreadsheet_id:
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '')

    if not spreadsheet_id:
        print("ОШИБКА: Не указан ID таблицы.")
        print("Используйте --spreadsheet-id или переменную GOOGLE_SHEETS_SPREADSHEET_ID")
        print("Или создайте новую таблицу с --create")
        return None

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"Открыта таблица: {spreadsheet.title}")
        print(f"URL: {spreadsheet.url}")
        return spreadsheet
    except gspread.SpreadsheetNotFound:
        print(f"ОШИБКА: Таблица с ID '{spreadsheet_id}' не найдена")
        print("Проверьте что Service Account имеет доступ к этой таблице")
        return None
    except Exception as e:
        print(f"ОШИБКА при открытии таблицы: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Экспорт данных WhatsApp аналитики в Google Sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python google_sheets_export.py --all
  python google_sheets_export.py --contacts --operations
  python google_sheets_export.py --all --spreadsheet-id "1abc..."
  python google_sheets_export.py --all --create "UAE Tourism Data"
  python google_sheets_export.py --setup  # Показать инструкцию настройки
        """
    )

    # Что экспортировать
    parser.add_argument('--all', action='store_true',
                       help='Экспортировать все данные')
    parser.add_argument('--contacts', action='store_true',
                       help='Экспортировать контакты')
    parser.add_argument('--operations', action='store_true',
                       help='Экспортировать операции')
    parser.add_argument('--funnel', action='store_true',
                       help='Экспортировать воронку продаж')
    parser.add_argument('--ltv', action='store_true',
                       help='Экспортировать LTV анализ')
    parser.add_argument('--profiles', action='store_true',
                       help='Экспортировать профили клиентов')

    # Куда экспортировать
    parser.add_argument('--spreadsheet-id', type=str,
                       help='ID существующей Google Sheets таблицы')
    parser.add_argument('--create', type=str, metavar='TITLE',
                       help='Создать новую таблицу с указанным названием')

    # Утилиты
    parser.add_argument('--setup', action='store_true',
                       help='Показать инструкцию по настройке')
    parser.add_argument('--share', type=str, metavar='EMAIL',
                       help='Поделиться таблицей с указанным email')

    args = parser.parse_args()

    # Показать инструкцию
    if args.setup:
        print_setup_instructions()
        return

    # Проверяем что хоть что-то выбрано для экспорта
    export_any = args.all or args.contacts or args.operations or args.funnel or args.ltv or args.profiles

    if not export_any and not args.share:
        parser.print_help()
        return

    # Авторизация
    print("\n" + "=" * 60)
    print("GOOGLE SHEETS EXPORT")
    print("=" * 60)

    client = authorize_gspread()

    # Получаем или создаем таблицу
    if args.create:
        spreadsheet = create_spreadsheet(client, args.create)
    else:
        spreadsheet = open_spreadsheet(client, args.spreadsheet_id)
        if not spreadsheet:
            return

    # Поделиться таблицей
    if args.share:
        try:
            spreadsheet.share(args.share, perm_type='user', role='writer')
            print(f"Таблица расшарена для: {args.share}")
        except Exception as e:
            print(f"ОШИБКА при шаринге: {e}")

    # Экспорт данных
    results = []

    if args.all or args.contacts:
        results.append(("Контакты", export_contacts(spreadsheet)))

    if args.all or args.operations:
        results.append(("Операции", export_operations(spreadsheet)))

    if args.all or args.funnel:
        results.append(("Воронка", export_funnel(spreadsheet)))

    if args.all or args.ltv:
        results.append(("LTV", export_ltv(spreadsheet)))

    if args.all or args.profiles:
        results.append(("Профили", export_profiles(spreadsheet)))

    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ЭКСПОРТА")
    print("=" * 60)

    for name, success in results:
        status = "OK" if success else "ПРОПУЩЕН"
        print(f"  {name}: {status}")

    print(f"\nТаблица: {spreadsheet.url}")
    print("=" * 60)


if __name__ == "__main__":
    main()
