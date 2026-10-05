#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
average_check.py - Анализ среднего чека по типам клиентов

Анализирует:
1. Извлечение сумм из сообщений (5000 AED, $500, 5000 дирхам)
2. Средний чек по типу клиента (agent, direct)
3. Средний чек по типу тура/услуги
4. Сезонный анализ среднего чека
5. Анализ по источникам
6. Медиана vs среднее
7. Распределение чеков (гистограмма)
8. Upsell анализ (рост чека повторных клиентов)
9. Динамика среднего чека по месяцам
10. Прогноз выручки

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/operations.json
- D:/Downloads/Chats/_база/json/contacts.json

Выходные файлы:
- D:/Downloads/Chats/_база/json/average_check_analysis.json
- D:/Downloads/Chats/_база/csv/average_check_by_client.csv
- D:/Downloads/Chats/_база/csv/average_check_by_tour.csv
- D:/Downloads/Chats/_база/md/средний_чек.md

Использование:
    python average_check.py                    # Полный анализ
    python average_check.py --by-client        # Только по типу клиента
    python average_check.py --by-tour          # Только по типу тура
    python average_check.py --period 2024-01   # За конкретный период
    python average_check.py --export-csv       # Экспорт в CSV
"""

import json
import re
import csv
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict, Tuple
from decimal import Decimal, ROUND_HALF_UP
import statistics

sys.stdout.reconfigure(encoding='utf-8')

# === КОНФИГУРАЦИЯ ===

try:
    from config import (
        RAW_DIR, JSON_DIR, CSV_DIR, MD_DIR,
        ensure_directories, CONTACT_TYPES, CONTACT_SUBTYPES,
        OPERATION_KEYWORDS
    )
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    CSV_DIR = Path("D:/Downloads/Chats/_база/csv")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")

    CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]
    CONTACT_SUBTYPES = {
        "клиенты": ["турист", "VIP", "корпоративный"],
        "агенты": ["турагент", "туроператор", "B2B"],
        "поставщики": ["обменник", "водитель", "гид", "яхтсмен", "кейтеринг"],
        "сотрудники": ["менеджер", "водитель_штат", "админ"]
    }
    OPERATION_KEYWORDS = {
        "tour": ["экскурсия", "тур", "сафари", "museum", "абу-даби", "дубай", "обзорная"],
        "transfer": ["трансфер", "встреча", "аэропорт", "transfer", "проводы"],
        "yacht": ["яхта", "yacht", "катер", "лодка", "рыбалка"],
        "tickets": ["билет", "парк", "ferrari", "aquaventure", "ticket", "вход"],
        "exchange": ["обмен", "курс", "дирхам", "рубл", "exchange", "валюта"],
        "car_rental": ["аренда", "машина", "авто", "rental", "car", "прокат"],
        "catering": ["кейтеринг", "еда", "catering", "food", "ресторан"]
    }

    def ensure_directories():
        for d in [RAW_DIR, JSON_DIR, CSV_DIR, MD_DIR]:
            d.mkdir(parents=True, exist_ok=True)


# =====================================================================
# ПАТТЕРНЫ ИЗВЛЕЧЕНИЯ СУММ
# =====================================================================

# Расширенные паттерны для извлечения сумм из сообщений
AMOUNT_PATTERNS = [
    # AED форматы
    (r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*(?:AED|aed|дирхам[ов]?|дрх|Dhs?)', 'AED'),
    (r'(?:AED|aed|дирхам[ов]?)\s*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)', 'AED'),

    # USD форматы
    (r'\$\s*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)', 'USD'),
    (r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*(?:USD|usd|долл(?:ар)?[ов]?|\$)', 'USD'),
    (r'(?:USD|usd|долл(?:ар)?[ов]?)\s*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)', 'USD'),

    # RUB форматы
    (r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*(?:RUB|rub|руб(?:л)?[ейь]?|₽)', 'RUB'),
    (r'(?:RUB|rub|руб(?:л)?[ейь]?|₽)\s*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)', 'RUB'),

    # USDT форматы
    (r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*(?:USDT|usdt|тезер|tether)', 'USDT'),

    # EUR форматы
    (r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*(?:EUR|eur|евро)', 'EUR'),
    (r'(?:EUR|eur|евро)\s*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)', 'EUR'),
]

# Курсы конвертации в AED
CONVERSION_RATES = {
    'AED': Decimal('1'),
    'USD': Decimal('3.67'),
    'USDT': Decimal('3.67'),
    'RUB': Decimal('0.038'),
    'EUR': Decimal('4.0'),
    'KZT': Decimal('0.0075'),
}

# Категории туров с ключевыми словами
TOUR_CATEGORIES = {
    'desert_safari': {
        'name': 'Сафари в пустыне',
        'keywords': ['сафари', 'safari', 'пустын', 'desert', 'дюн', 'dune', 'джип', 'квадроцикл'],
        'avg_check_benchmark': 250,  # AED
    },
    'city_tour': {
        'name': 'Обзорные экскурсии',
        'keywords': ['обзорная', 'city tour', 'экскурсия', 'дубай тур', 'абу-даби тур', 'шарджа'],
        'avg_check_benchmark': 200,
    },
    'yacht': {
        'name': 'Яхты и круизы',
        'keywords': ['яхта', 'yacht', 'катер', 'boat', 'круиз', 'cruise', 'марина', 'marina'],
        'avg_check_benchmark': 800,
    },
    'theme_park': {
        'name': 'Парки развлечений',
        'keywords': ['ferrari', 'aquaventure', 'waterpark', 'аквапарк', 'legoland', 'motiongate', 'warner'],
        'avg_check_benchmark': 350,
    },
    'observation': {
        'name': 'Смотровые площадки',
        'keywords': ['burj khalifa', 'at the top', 'бурдж халифа', 'sky views', 'observation', 'смотров'],
        'avg_check_benchmark': 200,
    },
    'transfer': {
        'name': 'Трансферы',
        'keywords': ['трансфер', 'transfer', 'аэропорт', 'airport', 'встреча', 'проводы'],
        'avg_check_benchmark': 150,
    },
    'museum': {
        'name': 'Музеи',
        'keywords': ['музей', 'museum', 'лувр', 'louvre', 'expo', 'future museum'],
        'avg_check_benchmark': 180,
    },
    'adventure': {
        'name': 'Экстрим и приключения',
        'keywords': ['skydive', 'парашют', 'zipline', 'xline', 'balloon', 'воздушный шар', 'прыжок'],
        'avg_check_benchmark': 1500,
    },
    'car_rental': {
        'name': 'Аренда авто',
        'keywords': ['аренда', 'прокат', 'rental', 'машин', 'авто', 'lamborghini', 'ferrari', 'porsche'],
        'avg_check_benchmark': 2000,
    },
    'dining': {
        'name': 'Рестораны и кейтеринг',
        'keywords': ['ресторан', 'restaurant', 'кейтеринг', 'catering', 'бранч', 'brunch', 'dinner'],
        'avg_check_benchmark': 400,
    },
    'other': {
        'name': 'Прочее',
        'keywords': [],
        'avg_check_benchmark': 300,
    }
}

# Сезоны ОАЭ
SEASONS = {
    'high': {
        'months': [10, 11, 12, 1, 2, 3, 4],
        'name': 'Высокий сезон',
        'multiplier': 1.2,
    },
    'low': {
        'months': [5, 6, 7, 8, 9],
        'name': 'Низкий сезон',
        'multiplier': 0.8,
    }
}

# Распределение чеков (бакеты для гистограммы)
CHECK_BUCKETS = [
    (0, 100, '0-100'),
    (100, 250, '100-250'),
    (250, 500, '250-500'),
    (500, 1000, '500-1000'),
    (1000, 2500, '1000-2500'),
    (2500, 5000, '2500-5000'),
    (5000, 10000, '5000-10000'),
    (10000, float('inf'), '10000+'),
]


# =====================================================================
# ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
# =====================================================================

def load_json(filepath: Path) -> list:
    """Загрузка JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Ошибка загрузки {filepath}: {e}")
        return []


def load_messages(filepath: Path) -> list:
    """Загрузка сообщений из JSONL."""
    messages = []
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return messages

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue

                if line_num % 100000 == 0:
                    print(f"  Загружено {line_num:,} сообщений...")
    except Exception as e:
        print(f"[!] Ошибка загрузки {filepath}: {e}")

    print(f"  Всего загружено: {len(messages):,} сообщений")
    return messages


def save_json(data: dict, filepath: Path):
    """Сохранение JSON файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"[+] JSON сохранён: {filepath}")


def save_csv(data: list, filepath: Path, fieldnames: list):
    """Сохранение CSV файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] CSV сохранён: {filepath}")


# =====================================================================
# ИЗВЛЕЧЕНИЕ СУММ ИЗ СООБЩЕНИЙ
# =====================================================================

def parse_amount(text: str) -> Optional[float]:
    """Преобразовать строку суммы в число."""
    if not text:
        return None

    # Очистка: убираем пробелы между цифрами, заменяем запятые
    cleaned = text.replace(' ', '').replace(',', '')

    # Обработка точки как десятичного разделителя или разделителя тысяч
    parts = cleaned.split('.')
    if len(parts) == 2:
        if len(parts[1]) == 3:
            # 1.500 -> 1500 (тысячный разделитель)
            cleaned = parts[0] + parts[1]
        # иначе оставляем как десятичную дробь
    elif len(parts) > 2:
        # 1.500.000 -> 1500000
        cleaned = ''.join(parts)

    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_amounts_from_text(text: str) -> List[Tuple[float, str]]:
    """Извлечь все суммы из текста с валютами."""
    if not text:
        return []

    amounts = []
    text_lower = text.lower()

    for pattern, currency in AMOUNT_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1) if match.lastindex else match.group(0)
            amount = parse_amount(amount_str)

            if amount and amount > 0:
                # Фильтруем слишком маленькие суммы (< 10) и слишком большие (> 1,000,000)
                if 10 <= amount <= 1000000:
                    amounts.append((amount, currency))

    return amounts


def convert_to_aed(amount: float, currency: str) -> Decimal:
    """Конвертация суммы в AED."""
    rate = CONVERSION_RATES.get(currency.upper(), Decimal('1'))
    return Decimal(str(amount)) * rate


# =====================================================================
# ОПРЕДЕЛЕНИЕ КАТЕГОРИЙ
# =====================================================================

def determine_tour_category(text: str) -> str:
    """Определить категорию тура по тексту."""
    if not text:
        return 'other'

    text_lower = text.lower()
    scores = defaultdict(int)

    for category, info in TOUR_CATEGORIES.items():
        if category == 'other':
            continue
        for keyword in info['keywords']:
            if keyword.lower() in text_lower:
                scores[category] += 1

    if scores:
        return max(scores, key=scores.get)
    return 'other'


def get_season(date: datetime) -> str:
    """Определить сезон по дате."""
    month = date.month
    if month in SEASONS['high']['months']:
        return 'high'
    return 'low'


def get_client_type(contact: dict) -> str:
    """Определить тип клиента: agent или direct."""
    contact_type = contact.get('type', '')
    subtype = contact.get('subtype', '')

    if contact_type == 'агенты' or subtype in ['турагент', 'туроператор', 'B2B']:
        return 'agent'
    return 'direct'


# =====================================================================
# ОСНОВНОЙ АНАЛИЗ
# =====================================================================

def analyze_operations(operations: list, contacts: list) -> dict:
    """Анализ операций для расчёта среднего чека."""

    # Индексы
    contacts_by_phone = {c.get('phone'): c for c in contacts if c.get('phone')}
    contacts_by_jid = {c.get('jid'): c for c in contacts if c.get('jid')}

    # Структуры для накопления
    by_client_type = defaultdict(lambda: {
        'amounts': [],
        'count': 0,
        'total_aed': Decimal('0'),
    })

    by_tour_category = defaultdict(lambda: {
        'amounts': [],
        'count': 0,
        'total_aed': Decimal('0'),
    })

    by_season = defaultdict(lambda: {
        'amounts': [],
        'count': 0,
        'total_aed': Decimal('0'),
    })

    by_source = defaultdict(lambda: {
        'amounts': [],
        'count': 0,
        'total_aed': Decimal('0'),
    })

    by_month = defaultdict(lambda: {
        'amounts': [],
        'count': 0,
        'total_aed': Decimal('0'),
    })

    # Для upsell анализа
    orders_by_client = defaultdict(list)  # phone -> [(date, amount), ...]

    # Все суммы для общей статистики
    all_amounts = []

    for op in operations:
        # Только завершённые операции
        if op.get('status') != 'completed':
            continue

        amount = op.get('amount', 0)
        currency = op.get('currency', 'AED')

        if not amount or amount <= 0:
            continue

        # Конвертация в AED
        amount_aed = convert_to_aed(amount, currency)
        amount_aed_float = float(amount_aed)

        all_amounts.append(amount_aed_float)

        # Дата
        date_str = op.get('date', '')
        try:
            date = datetime.strptime(date_str[:10], '%Y-%m-%d') if date_str else None
        except ValueError:
            date = None

        # Контакт
        phone = op.get('phone', '')
        contact = contacts_by_phone.get(phone, {})

        # Тип клиента
        client_type = get_client_type(contact)
        by_client_type[client_type]['amounts'].append(amount_aed_float)
        by_client_type[client_type]['count'] += 1
        by_client_type[client_type]['total_aed'] += amount_aed

        # Категория тура
        op_type = op.get('type', '')
        description = op.get('description', '')
        combined_text = f"{op_type} {description}"
        tour_category = determine_tour_category(combined_text)
        by_tour_category[tour_category]['amounts'].append(amount_aed_float)
        by_tour_category[tour_category]['count'] += 1
        by_tour_category[tour_category]['total_aed'] += amount_aed

        # Сезон
        if date:
            season = get_season(date)
            by_season[season]['amounts'].append(amount_aed_float)
            by_season[season]['count'] += 1
            by_season[season]['total_aed'] += amount_aed

            # По месяцам
            month_key = date.strftime('%Y-%m')
            by_month[month_key]['amounts'].append(amount_aed_float)
            by_month[month_key]['count'] += 1
            by_month[month_key]['total_aed'] += amount_aed

        # Источник
        source = op.get('source', '') or contact.get('source', 'unknown')
        by_source[source]['amounts'].append(amount_aed_float)
        by_source[source]['count'] += 1
        by_source[source]['total_aed'] += amount_aed

        # Для upsell
        if phone and date:
            orders_by_client[phone].append((date, amount_aed_float))

    return {
        'all_amounts': all_amounts,
        'by_client_type': dict(by_client_type),
        'by_tour_category': dict(by_tour_category),
        'by_season': dict(by_season),
        'by_source': dict(by_source),
        'by_month': dict(by_month),
        'orders_by_client': dict(orders_by_client),
    }


def analyze_messages_for_amounts(messages: list, contacts: list) -> dict:
    """Анализ сообщений для извлечения упомянутых сумм (дополнительный источник)."""

    contacts_by_jid = {c.get('jid'): c for c in contacts if c.get('jid')}

    mentioned_amounts = []
    by_client_type = defaultdict(list)
    by_tour_category = defaultdict(list)

    for msg in messages:
        # Только исходящие сообщения (наши цены)
        if not msg.get('is_from_me', False):
            continue

        text = msg.get('text', '')
        if not text:
            continue

        # Извлекаем суммы
        amounts = extract_amounts_from_text(text)
        if not amounts:
            continue

        jid = msg.get('jid', '')
        contact = contacts_by_jid.get(jid, {})
        client_type = get_client_type(contact)
        tour_category = determine_tour_category(text)

        for amount, currency in amounts:
            amount_aed = float(convert_to_aed(amount, currency))
            mentioned_amounts.append(amount_aed)
            by_client_type[client_type].append(amount_aed)
            by_tour_category[tour_category].append(amount_aed)

    return {
        'mentioned_amounts': mentioned_amounts,
        'by_client_type': dict(by_client_type),
        'by_tour_category': dict(by_tour_category),
    }


def calculate_statistics(amounts: list) -> dict:
    """Расчёт статистик для списка сумм."""
    if not amounts:
        return {
            'count': 0,
            'total': 0,
            'mean': 0,
            'median': 0,
            'std_dev': 0,
            'min': 0,
            'max': 0,
            'percentile_25': 0,
            'percentile_75': 0,
            'percentile_90': 0,
        }

    sorted_amounts = sorted(amounts)
    n = len(sorted_amounts)

    return {
        'count': n,
        'total': round(sum(amounts), 2),
        'mean': round(statistics.mean(amounts), 2),
        'median': round(statistics.median(amounts), 2),
        'std_dev': round(statistics.stdev(amounts), 2) if n > 1 else 0,
        'min': round(min(amounts), 2),
        'max': round(max(amounts), 2),
        'percentile_25': round(sorted_amounts[int(n * 0.25)], 2) if n > 4 else sorted_amounts[0],
        'percentile_75': round(sorted_amounts[int(n * 0.75)], 2) if n > 4 else sorted_amounts[-1],
        'percentile_90': round(sorted_amounts[int(n * 0.90)], 2) if n > 10 else sorted_amounts[-1],
    }


def calculate_distribution(amounts: list) -> dict:
    """Расчёт распределения чеков по бакетам."""
    distribution = {}

    for bucket_min, bucket_max, bucket_name in CHECK_BUCKETS:
        count = len([a for a in amounts if bucket_min <= a < bucket_max])
        percentage = (count / len(amounts) * 100) if amounts else 0
        distribution[bucket_name] = {
            'count': count,
            'percentage': round(percentage, 1),
        }

    return distribution


def analyze_upsell(orders_by_client: dict) -> dict:
    """Анализ upsell - рост чека повторных клиентов."""

    first_orders = []
    repeat_orders = []
    growth_rates = []

    repeat_customers = 0
    total_customers = len(orders_by_client)

    for phone, orders in orders_by_client.items():
        if len(orders) < 2:
            if orders:
                first_orders.append(orders[0][1])
            continue

        repeat_customers += 1

        # Сортируем по дате
        sorted_orders = sorted(orders, key=lambda x: x[0])

        first_amount = sorted_orders[0][1]
        first_orders.append(first_amount)

        # Все повторные заказы
        for _, amount in sorted_orders[1:]:
            repeat_orders.append(amount)

        # Средний чек повторных заказов vs первый
        avg_repeat = sum(o[1] for o in sorted_orders[1:]) / (len(sorted_orders) - 1)
        if first_amount > 0:
            growth = (avg_repeat - first_amount) / first_amount
            growth_rates.append(growth)

    # Статистика
    first_stats = calculate_statistics(first_orders)
    repeat_stats = calculate_statistics(repeat_orders)

    avg_growth = statistics.mean(growth_rates) if growth_rates else 0

    return {
        'total_customers': total_customers,
        'repeat_customers': repeat_customers,
        'repeat_rate': round(repeat_customers / total_customers * 100, 1) if total_customers > 0 else 0,
        'first_order_avg': first_stats['mean'],
        'repeat_order_avg': repeat_stats['mean'],
        'avg_check_growth': round(avg_growth * 100, 1),  # В процентах
        'upsell_potential_aed': round(repeat_stats['mean'] - first_stats['mean'], 2) if repeat_stats['mean'] > first_stats['mean'] else 0,
    }


def calculate_trends(by_month: dict) -> dict:
    """Расчёт трендов среднего чека по месяцам."""

    monthly_data = []

    for month in sorted(by_month.keys()):
        data = by_month[month]
        amounts = data.get('amounts', [])

        if not amounts:
            continue

        avg_check = statistics.mean(amounts)

        monthly_data.append({
            'month': month,
            'avg_check': round(avg_check, 2),
            'orders_count': len(amounts),
            'total_revenue': round(sum(amounts), 2),
        })

    # Расчёт MoM изменений
    for i in range(1, len(monthly_data)):
        prev_avg = monthly_data[i - 1]['avg_check']
        curr_avg = monthly_data[i]['avg_check']

        if prev_avg > 0:
            change = (curr_avg - prev_avg) / prev_avg
            monthly_data[i]['mom_change'] = round(change * 100, 1)
        else:
            monthly_data[i]['mom_change'] = 0

    if monthly_data:
        monthly_data[0]['mom_change'] = 0

    # Общий тренд за последние 6 месяцев
    recent = monthly_data[-6:] if len(monthly_data) >= 6 else monthly_data

    if len(recent) >= 2:
        first_avg = recent[0]['avg_check']
        last_avg = recent[-1]['avg_check']

        if first_avg > 0:
            overall_change = (last_avg - first_avg) / first_avg
            direction = 'up' if overall_change > 0.05 else 'down' if overall_change < -0.05 else 'stable'
        else:
            overall_change = 0
            direction = 'stable'
    else:
        overall_change = 0
        direction = 'stable'

    return {
        'monthly_data': monthly_data,
        'overall_change': round(overall_change * 100, 1),
        'direction': direction,
    }


def forecast_revenue(by_month: dict, months_ahead: int = 3) -> dict:
    """Прогноз выручки на основе среднего чека и трендов."""

    monthly_data = []

    for month in sorted(by_month.keys()):
        data = by_month[month]
        amounts = data.get('amounts', [])
        if amounts:
            monthly_data.append({
                'avg_check': statistics.mean(amounts),
                'orders_count': len(amounts),
                'revenue': sum(amounts),
            })

    if len(monthly_data) < 3:
        return {
            'forecast': [],
            'confidence': 'low',
            'note': 'Недостаточно данных для прогноза',
        }

    # Средние за последние 3 месяца
    recent = monthly_data[-3:]
    avg_orders = statistics.mean([d['orders_count'] for d in recent])
    avg_check = statistics.mean([d['avg_check'] for d in recent])

    # Тренд среднего чека
    check_trend = (recent[-1]['avg_check'] - recent[0]['avg_check']) / recent[0]['avg_check'] if recent[0]['avg_check'] > 0 else 0

    # Прогноз
    forecast = []
    last_month = sorted(by_month.keys())[-1]
    year, month = map(int, last_month.split('-'))

    for i in range(1, months_ahead + 1):
        month += 1
        if month > 12:
            month = 1
            year += 1

        forecast_month = f"{year}-{month:02d}"

        # Сезонная корректировка
        season_mult = SEASONS['high']['multiplier'] if month in SEASONS['high']['months'] else SEASONS['low']['multiplier']

        # Прогноз с учётом тренда
        projected_check = avg_check * (1 + check_trend * i / 12) * season_mult
        projected_orders = avg_orders * season_mult
        projected_revenue = projected_check * projected_orders

        forecast.append({
            'month': forecast_month,
            'projected_avg_check': round(projected_check, 2),
            'projected_orders': round(projected_orders),
            'projected_revenue': round(projected_revenue, 2),
            'season': 'high' if month in SEASONS['high']['months'] else 'low',
        })

    return {
        'forecast': forecast,
        'confidence': 'medium' if len(monthly_data) >= 6 else 'low',
        'base_avg_check': round(avg_check, 2),
        'base_orders': round(avg_orders),
        'check_trend': round(check_trend * 100, 1),
    }


# =====================================================================
# ГЕНЕРАЦИЯ ОТЧЁТОВ
# =====================================================================

def build_report(analysis: dict, msg_analysis: dict) -> dict:
    """Формирование финального отчёта."""

    all_amounts = analysis['all_amounts']

    # Общая статистика
    overall_stats = calculate_statistics(all_amounts)
    distribution = calculate_distribution(all_amounts)

    # По типу клиента
    client_type_stats = {}
    for client_type, data in analysis['by_client_type'].items():
        stats = calculate_statistics(data['amounts'])
        client_type_stats[client_type] = {
            'name': 'Агенты' if client_type == 'agent' else 'Прямые клиенты',
            **stats,
        }

    # По типу тура
    tour_category_stats = {}
    for category, data in analysis['by_tour_category'].items():
        stats = calculate_statistics(data['amounts'])
        category_info = TOUR_CATEGORIES.get(category, {'name': category, 'avg_check_benchmark': 300})

        # Сравнение с бенчмарком
        benchmark = category_info['avg_check_benchmark']
        variance = ((stats['mean'] - benchmark) / benchmark * 100) if benchmark > 0 else 0

        tour_category_stats[category] = {
            'name': category_info['name'],
            'benchmark': benchmark,
            'variance_from_benchmark': round(variance, 1),
            **stats,
        }

    # По сезону
    season_stats = {}
    for season, data in analysis['by_season'].items():
        stats = calculate_statistics(data['amounts'])
        season_info = SEASONS.get(season, {'name': season})
        season_stats[season] = {
            'name': season_info['name'],
            **stats,
        }

    # По источнику
    source_stats = {}
    for source, data in analysis['by_source'].items():
        stats = calculate_statistics(data['amounts'])
        source_stats[source] = stats

    # Upsell анализ
    upsell = analyze_upsell(analysis['orders_by_client'])

    # Тренды
    trends = calculate_trends(analysis['by_month'])

    # Прогноз
    forecast = forecast_revenue(analysis['by_month'])

    # Сравнение медианы и среднего
    median_mean_diff = overall_stats['median'] - overall_stats['mean'] if overall_stats['count'] > 0 else 0
    skewness = 'positive' if median_mean_diff < -50 else 'negative' if median_mean_diff > 50 else 'normal'

    return {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_operations': overall_stats['count'],
            'total_revenue_aed': overall_stats['total'],
            'average_check_aed': overall_stats['mean'],
            'median_check_aed': overall_stats['median'],
            'median_mean_diff': round(median_mean_diff, 2),
            'distribution_skewness': skewness,
        },
        'overall_statistics': overall_stats,
        'distribution': distribution,
        'by_client_type': client_type_stats,
        'by_tour_category': tour_category_stats,
        'by_season': season_stats,
        'by_source': source_stats,
        'upsell_analysis': upsell,
        'trends': trends,
        'forecast': forecast,
        'message_analysis': {
            'mentioned_amounts_count': len(msg_analysis.get('mentioned_amounts', [])),
            'avg_mentioned_price': round(statistics.mean(msg_analysis['mentioned_amounts']), 2) if msg_analysis.get('mentioned_amounts') else 0,
        },
    }


def generate_markdown(report: dict) -> str:
    """Генерация Markdown отчёта."""

    lines = []
    lines.append("# Анализ среднего чека")
    lines.append("")
    lines.append(f"*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")

    # Сводка
    summary = report.get('summary', {})
    lines.append("## Сводка")
    lines.append("")
    lines.append(f"- **Всего операций:** {summary.get('total_operations', 0):,}")
    lines.append(f"- **Общая выручка:** {summary.get('total_revenue_aed', 0):,.0f} AED")
    lines.append(f"- **Средний чек:** {summary.get('average_check_aed', 0):,.0f} AED")
    lines.append(f"- **Медианный чек:** {summary.get('median_check_aed', 0):,.0f} AED")

    diff = summary.get('median_mean_diff', 0)
    if diff < 0:
        lines.append(f"- **Распределение:** Смещение вправо (есть крупные чеки)")
    elif diff > 0:
        lines.append(f"- **Распределение:** Смещение влево (преобладают мелкие чеки)")
    else:
        lines.append(f"- **Распределение:** Нормальное")
    lines.append("")

    # По типу клиента
    lines.append("## Средний чек по типу клиента")
    lines.append("")
    lines.append("| Тип | Средний чек | Медиана | Заказов | Выручка |")
    lines.append("|-----|-------------|---------|---------|---------|")

    for client_type, stats in report.get('by_client_type', {}).items():
        lines.append(
            f"| {stats.get('name', client_type)} | "
            f"{stats.get('mean', 0):,.0f} | "
            f"{stats.get('median', 0):,.0f} | "
            f"{stats.get('count', 0)} | "
            f"{stats.get('total', 0):,.0f} |"
        )
    lines.append("")

    # По типу тура
    lines.append("## Средний чек по типу услуги")
    lines.append("")
    lines.append("| Услуга | Средний чек | Бенчмарк | Отклонение | Заказов |")
    lines.append("|--------|-------------|----------|------------|---------|")

    for category, stats in sorted(
        report.get('by_tour_category', {}).items(),
        key=lambda x: x[1].get('total', 0),
        reverse=True
    ):
        variance = stats.get('variance_from_benchmark', 0)
        variance_str = f"+{variance:.0f}%" if variance > 0 else f"{variance:.0f}%"

        lines.append(
            f"| {stats.get('name', category)} | "
            f"{stats.get('mean', 0):,.0f} | "
            f"{stats.get('benchmark', 0):,.0f} | "
            f"{variance_str} | "
            f"{stats.get('count', 0)} |"
        )
    lines.append("")

    # По сезону
    lines.append("## Средний чек по сезону")
    lines.append("")
    lines.append("| Сезон | Средний чек | Медиана | Заказов |")
    lines.append("|-------|-------------|---------|---------|")

    for season, stats in report.get('by_season', {}).items():
        lines.append(
            f"| {stats.get('name', season)} | "
            f"{stats.get('mean', 0):,.0f} | "
            f"{stats.get('median', 0):,.0f} | "
            f"{stats.get('count', 0)} |"
        )
    lines.append("")

    # Распределение чеков
    lines.append("## Распределение чеков")
    lines.append("")

    distribution = report.get('distribution', {})
    max_pct = max((d.get('percentage', 0) for d in distribution.values()), default=1)

    for bucket_name, data in distribution.items():
        pct = data.get('percentage', 0)
        bar_len = int(pct / max_pct * 20) if max_pct > 0 else 0
        bar = "#" * bar_len
        lines.append(f"`{bucket_name:12}` {bar} {pct:.1f}% ({data.get('count', 0)})")
    lines.append("")

    # Upsell анализ
    upsell = report.get('upsell_analysis', {})
    lines.append("## Upsell анализ")
    lines.append("")
    lines.append(f"- **Repeat Rate:** {upsell.get('repeat_rate', 0):.1f}%")
    lines.append(f"- **Средний первый заказ:** {upsell.get('first_order_avg', 0):,.0f} AED")
    lines.append(f"- **Средний повторный заказ:** {upsell.get('repeat_order_avg', 0):,.0f} AED")

    growth = upsell.get('avg_check_growth', 0)
    if growth > 0:
        lines.append(f"- **Рост среднего чека:** +{growth:.1f}%")
    elif growth < 0:
        lines.append(f"- **Рост среднего чека:** {growth:.1f}%")
    else:
        lines.append(f"- **Рост среднего чека:** 0%")

    lines.append(f"- **Потенциал upsell:** {upsell.get('upsell_potential_aed', 0):,.0f} AED на клиента")
    lines.append("")

    # Тренды
    trends = report.get('trends', {})
    lines.append("## Динамика среднего чека")
    lines.append("")

    direction = trends.get('direction', 'stable')
    change = trends.get('overall_change', 0)

    direction_emoji = {'up': '^', 'down': 'v', 'stable': '='}
    direction_text = {'up': 'Рост', 'down': 'Падение', 'stable': 'Стабильно'}

    lines.append(f"**Тренд:** {direction_emoji.get(direction, '=')} {direction_text.get(direction, 'стабильно')} ({change:+.1f}%)")
    lines.append("")

    # Таблица по месяцам
    monthly = trends.get('monthly_data', [])[-6:]  # Последние 6 месяцев
    if monthly:
        lines.append("| Месяц | Средний чек | Заказов | MoM |")
        lines.append("|-------|-------------|---------|-----|")

        for m in monthly:
            mom = m.get('mom_change', 0)
            mom_str = f"+{mom:.0f}%" if mom > 0 else f"{mom:.0f}%"
            lines.append(
                f"| {m['month']} | "
                f"{m['avg_check']:,.0f} | "
                f"{m['orders_count']} | "
                f"{mom_str} |"
            )
        lines.append("")

    # Прогноз
    forecast = report.get('forecast', {})
    lines.append("## Прогноз выручки")
    lines.append("")

    forecast_data = forecast.get('forecast', [])
    if forecast_data:
        lines.append(f"*Уровень уверенности: {forecast.get('confidence', 'low')}*")
        lines.append("")
        lines.append("| Месяц | Прогноз ср. чека | Заказов | Выручка |")
        lines.append("|-------|------------------|---------|---------|")

        for f in forecast_data:
            lines.append(
                f"| {f['month']} | "
                f"{f['projected_avg_check']:,.0f} | "
                f"{f['projected_orders']:.0f} | "
                f"{f['projected_revenue']:,.0f} |"
            )
        lines.append("")
    else:
        lines.append("*Недостаточно данных для прогноза*")
        lines.append("")

    # Рекомендации
    lines.append("## Рекомендации")
    lines.append("")

    recommendations = []

    # На основе типа клиента
    client_stats = report.get('by_client_type', {})
    if 'agent' in client_stats and 'direct' in client_stats:
        agent_avg = client_stats['agent'].get('mean', 0)
        direct_avg = client_stats['direct'].get('mean', 0)

        if agent_avg > direct_avg * 1.2:
            recommendations.append(f"Агенты приносят более высокий средний чек (+{(agent_avg/direct_avg-1)*100:.0f}%). Развивать агентскую сеть.")
        elif direct_avg > agent_avg * 1.2:
            recommendations.append(f"Прямые продажи эффективнее (+{(direct_avg/agent_avg-1)*100:.0f}% к среднему чеку). Инвестировать в direct marketing.")

    # На основе upsell
    if upsell.get('avg_check_growth', 0) > 10:
        recommendations.append("Хороший рост чека у повторных клиентов. Фокус на retention программы.")
    elif upsell.get('avg_check_growth', 0) < -10:
        recommendations.append("Снижение чека у повторных клиентов. Внедрить upsell стратегии.")

    # На основе сезона
    season_stats = report.get('by_season', {})
    if 'high' in season_stats and 'low' in season_stats:
        high_avg = season_stats['high'].get('mean', 0)
        low_avg = season_stats['low'].get('mean', 0)

        if high_avg > low_avg * 1.3:
            recommendations.append("Значительная сезонность. Разработать спецпредложения для низкого сезона.")

    # На основе распределения
    if summary.get('distribution_skewness') == 'positive':
        recommendations.append("Много крупных чеков. Рассмотреть VIP-программу для удержания premium клиентов.")

    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")

    if not recommendations:
        lines.append("*Нет значимых отклонений, требующих внимания.*")

    lines.append("")
    lines.append("---")
    lines.append("*Отчёт сгенерирован автоматически скриптом average_check.py*")

    return "\n".join(lines)


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Анализ среднего чека по типам клиентов"
    )
    parser.add_argument(
        "--by-client", action="store_true",
        help="Только анализ по типу клиента"
    )
    parser.add_argument(
        "--by-tour", action="store_true",
        help="Только анализ по типу тура"
    )
    parser.add_argument(
        "--period", type=str,
        help="Период в формате YYYY-MM"
    )
    parser.add_argument(
        "--export-csv", action="store_true",
        help="Экспортировать в CSV"
    )
    parser.add_argument(
        "--skip-messages", action="store_true",
        help="Пропустить анализ сообщений (быстрее)"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Минимальный вывод"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("АНАЛИЗ СРЕДНЕГО ЧЕКА")
    print("=" * 60)

    # Создание директорий
    ensure_directories()

    # Пути к файлам
    operations_file = JSON_DIR / "operations.json"
    contacts_file = JSON_DIR / "contacts.json"
    messages_file = RAW_DIR / "all_messages.jsonl"

    output_json = JSON_DIR / "average_check_analysis.json"
    output_md = MD_DIR / "средний_чек.md"

    print(f"\nВходные файлы:")
    print(f"  - Операции: {operations_file}")
    print(f"  - Контакты: {contacts_file}")
    print(f"  - Сообщения: {messages_file}")

    # Загрузка данных
    print("\n[*] Загрузка данных...")
    operations = load_json(operations_file)
    contacts = load_json(contacts_file)

    if not operations:
        print("[!] Нет операций для анализа!")
        print("Создайте файл operations.json или запустите extract_operations.py")
        sys.exit(1)

    print(f"  Загружено операций: {len(operations)}")
    print(f"  Загружено контактов: {len(contacts)}")

    # Фильтрация по периоду
    if args.period:
        original_count = len(operations)
        operations = [
            op for op in operations
            if op.get('date', '').startswith(args.period)
        ]
        print(f"  После фильтрации по {args.period}: {len(operations)} операций")

    # Анализ операций
    print("\n[*] Анализ операций...")
    analysis = analyze_operations(operations, contacts)

    # Анализ сообщений (опционально)
    if not args.skip_messages and messages_file.exists():
        print("\n[*] Анализ сообщений...")
        messages = load_messages(messages_file)
        msg_analysis = analyze_messages_for_amounts(messages, contacts)
    else:
        msg_analysis = {'mentioned_amounts': [], 'by_client_type': {}, 'by_tour_category': {}}

    # Формирование отчёта
    print("\n[*] Формирование отчёта...")
    report = build_report(analysis, msg_analysis)

    # Сохранение JSON
    save_json(report, output_json)

    # Генерация и сохранение Markdown
    md_content = generate_markdown(report)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"[+] Markdown сохранён: {output_md}")

    # Экспорт CSV
    if args.export_csv:
        # CSV по клиентам
        client_csv = CSV_DIR / "average_check_by_client.csv"
        client_data = [
            {'client_type': ct, **stats}
            for ct, stats in report['by_client_type'].items()
        ]
        if client_data:
            save_csv(client_data, client_csv,
                     ['client_type', 'name', 'count', 'total', 'mean', 'median', 'min', 'max'])

        # CSV по турам
        tour_csv = CSV_DIR / "average_check_by_tour.csv"
        tour_data = [
            {'category': cat, **stats}
            for cat, stats in report['by_tour_category'].items()
        ]
        if tour_data:
            save_csv(tour_data, tour_csv,
                     ['category', 'name', 'count', 'total', 'mean', 'median', 'benchmark', 'variance_from_benchmark'])

        # CSV по месяцам
        monthly_csv = CSV_DIR / "average_check_monthly.csv"
        monthly_data = report.get('trends', {}).get('monthly_data', [])
        if monthly_data:
            save_csv(monthly_data, monthly_csv,
                     ['month', 'avg_check', 'orders_count', 'total_revenue', 'mom_change'])

    # Вывод результатов
    if not args.quiet:
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 60)

        summary = report.get('summary', {})
        print(f"\nОбщая статистика:")
        print(f"  Операций: {summary.get('total_operations', 0):,}")
        print(f"  Выручка: {summary.get('total_revenue_aed', 0):,.0f} AED")
        print(f"  Средний чек: {summary.get('average_check_aed', 0):,.0f} AED")
        print(f"  Медианный чек: {summary.get('median_check_aed', 0):,.0f} AED")

        print(f"\nПо типу клиента:")
        for ct, stats in report.get('by_client_type', {}).items():
            print(f"  {stats.get('name', ct)}: {stats.get('mean', 0):,.0f} AED (n={stats.get('count', 0)})")

        print(f"\nТоп-5 категорий по среднему чеку:")
        sorted_tours = sorted(
            report.get('by_tour_category', {}).items(),
            key=lambda x: x[1].get('mean', 0),
            reverse=True
        )[:5]
        for cat, stats in sorted_tours:
            print(f"  {stats.get('name', cat)}: {stats.get('mean', 0):,.0f} AED")

        upsell = report.get('upsell_analysis', {})
        print(f"\nUpsell:")
        print(f"  Repeat rate: {upsell.get('repeat_rate', 0):.1f}%")
        print(f"  Рост чека: {upsell.get('avg_check_growth', 0):+.1f}%")

    print("\n[+] Анализ завершён!")
    print(f"    JSON: {output_json}")
    print(f"    Markdown: {output_md}")


if __name__ == "__main__":
    main()
