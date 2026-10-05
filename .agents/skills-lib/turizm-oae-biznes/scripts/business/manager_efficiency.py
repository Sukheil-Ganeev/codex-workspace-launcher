#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manager_efficiency.py - Анализ эффективности менеджеров

Анализирует работу менеджеров на основе WhatsApp переписок:
1. Определение менеджера по номеру телефона / папке экспорта
2. Расчёт метрик эффективности
3. Сравнение менеджеров
4. Рейтинг (leaderboard)
5. Выявление слабых мест
6. Рекомендации по улучшению
7. Отчёт для руководителя
8. Экспорт: JSON, CSV, PDF, Markdown

Использование:
    python manager_efficiency.py                    # Полный анализ всех менеджеров
    python manager_efficiency.py --manager "Марсель"  # Анализ конкретного менеджера
    python manager_efficiency.py --period 2025-01   # За определённый период
    python manager_efficiency.py --compare          # Сравнительный анализ
    python manager_efficiency.py --format pdf       # Только PDF отчёт
    python manager_efficiency.py --export-csv       # Экспорт в CSV
"""

import json
import csv
import argparse
import sys
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, List, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

sys.stdout.reconfigure(encoding='utf-8')

# Опциональный импорт reportlab для PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[!] reportlab не установлен. PDF отчёты будут недоступны.")
    print("    Установите: pip install reportlab")

# === КОНФИГУРАЦИЯ ===

BASE_DIR = Path("D:/Downloads/Chats/_база")
JSON_DIR = BASE_DIR / "json"
MD_DIR = BASE_DIR / "md"
REPORTS_DIR = BASE_DIR / "reports"
RAW_DIR = BASE_DIR / "raw"

# Входные файлы
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
CONTACTS_FILE = JSON_DIR / "contacts.json"
OPERATIONS_FILE = JSON_DIR / "operations.json"

# Выходные файлы
EFFICIENCY_JSON = JSON_DIR / "manager_efficiency.json"
EFFICIENCY_MD = MD_DIR / "эффективность_менеджеров.md"
EFFICIENCY_CSV = JSON_DIR / "manager_efficiency.csv"

# Конфигурация менеджеров
# Формат: phone -> {name, role, export_source}
MANAGERS_CONFIG = {
    # Основные менеджеры (добавьте свои номера)
    "971507705321": {
        "name": "Менеджер 1",
        "role": "senior",
        "export_source": "whatsapp"
    },
    # Пример второго менеджера
    # "971501234567": {
    #     "name": "Менеджер 2",
    #     "role": "junior",
    #     "export_source": "wa_business"
    # }
}

# Папки экспорта -> менеджер
EXPORT_DIRS_TO_MANAGER = {
    "D:/Downloads/экспорт чатов с ватсапа": "whatsapp",
    "D:/Downloads/экспорт чатов с ватсап бизнеса": "wa_business"
}

# Настройки метрик
METRICS_CONFIG = {
    "fast_response_threshold_minutes": 5,   # Порог быстрого ответа
    "max_response_wait_hours": 24,          # Макс. ожидание для учёта ответа
    "conversion_stages": ["inquiry", "quote", "booking", "payment", "completed"],
    "working_hours": {"start": 9, "end": 21},  # Рабочие часы (для анализа)
}

# Курсы конвертации в AED
CONVERSION_RATES = {
    "AED": Decimal("1"),
    "USD": Decimal("3.67"),
    "RUB": Decimal("0.038"),
    "EUR": Decimal("4.0"),
    "KZT": Decimal("0.0075")
}

# Цвета для отчётов
COLORS = {
    "primary": "#1a365d",
    "secondary": "#2d3748",
    "success": "#38a169",
    "danger": "#e53e3e",
    "warning": "#d69e2e",
    "light": "#f7fafc",
    "muted": "#718096"
}

# Бенчмарки (целевые показатели)
BENCHMARKS = {
    "avg_response_time_minutes": 10,        # Целевое среднее время ответа
    "fast_response_rate": 0.70,             # 70% быстрых ответов
    "conversion_rate": 0.30,                # 30% конверсия в оплату
    "messages_per_conversion": 15,          # Сообщений на конверсию
    "avg_order_value_aed": 500,             # Средний чек
    "response_rate": 0.95,                  # 95% отвеченных сообщений
}


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def load_jsonl(filepath: Path) -> List[Dict]:
    """Загрузка JSONL файла."""
    messages = []
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return messages

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return messages


def load_json(filepath: Path) -> List[Dict]:
    """Загрузка JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "contacts" in data:
        return data["contacts"]
    return []


def save_json(data: dict, filepath: Path):
    """Сохранение JSON файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"[+] JSON сохранён: {filepath}")


def save_csv(data: List[Dict], filepath: Path, fieldnames: List[str]):
    """Сохранение CSV файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] CSV сохранён: {filepath}")


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Парсинг даты из разных форматов."""
    if not dt_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str[:19], fmt)
        except (ValueError, TypeError):
            continue
    return None


def to_aed(amount: float, currency: str) -> Decimal:
    """Конвертация суммы в AED."""
    if amount is None:
        return Decimal("0")
    rate = CONVERSION_RATES.get(currency, Decimal("1"))
    return Decimal(str(amount)) * rate


def get_period_key(date: datetime, period_type: str = "month") -> str:
    """Получить ключ периода."""
    if period_type == "month":
        return date.strftime("%Y-%m")
    elif period_type == "week":
        return date.strftime("%Y-W%W")
    elif period_type == "day":
        return date.strftime("%Y-%m-%d")
    return date.strftime("%Y-%m")


def is_working_hours(dt: datetime) -> bool:
    """Проверка, попадает ли время в рабочие часы."""
    return METRICS_CONFIG["working_hours"]["start"] <= dt.hour < METRICS_CONFIG["working_hours"]["end"]


# ═══════════════════════════════════════════════════════════════
# ОПРЕДЕЛЕНИЕ МЕНЕДЖЕРА
# ═══════════════════════════════════════════════════════════════

def identify_managers(messages: List[Dict]) -> Dict[str, Dict]:
    """
    Определение менеджеров из сообщений.

    Менеджер определяется по:
    1. Номеру телефона из MANAGERS_CONFIG
    2. Исходящим сообщениям (is_from_me=True)
    3. Папке экспорта
    """
    managers = {}

    # Сначала добавляем менеджеров из конфигурации
    for phone, config in MANAGERS_CONFIG.items():
        manager_id = phone
        managers[manager_id] = {
            "id": manager_id,
            "phone": phone,
            "name": config.get("name", f"Менеджер {phone[-4:]}"),
            "role": config.get("role", "manager"),
            "export_source": config.get("export_source", "unknown"),
            "identified_by": "config"
        }

    # Анализируем сообщения для определения дополнительных менеджеров
    outgoing_senders = defaultdict(int)

    for msg in messages:
        if msg.get("is_from_me", False):
            # Пробуем определить отправителя
            sender = msg.get("sender", "")
            source = msg.get("source", "")

            # Если есть source - используем его как идентификатор менеджера
            if source and source not in managers:
                source_name = EXPORT_DIRS_TO_MANAGER.get(source, source)
                managers[source] = {
                    "id": source,
                    "phone": None,
                    "name": f"Менеджер ({source_name})",
                    "role": "manager",
                    "export_source": source_name,
                    "identified_by": "export_source"
                }

            outgoing_senders[source or "default"] += 1

    # Если не нашли менеджеров - создаём дефолтного
    if not managers:
        managers["default"] = {
            "id": "default",
            "phone": None,
            "name": "Основной менеджер",
            "role": "manager",
            "export_source": "unknown",
            "identified_by": "default"
        }

    return managers


def assign_message_to_manager(msg: Dict, managers: Dict[str, Dict]) -> Optional[str]:
    """Присвоить сообщение менеджеру."""

    # Только исходящие сообщения
    if not msg.get("is_from_me", False):
        return None

    # По source
    source = msg.get("source", "")
    if source and source in managers:
        return source

    # По export_source в EXPORT_DIRS_TO_MANAGER
    for export_dir, source_name in EXPORT_DIRS_TO_MANAGER.items():
        if export_dir in source:
            for manager_id, manager in managers.items():
                if manager.get("export_source") == source_name:
                    return manager_id

    # Дефолтный менеджер
    if "default" in managers:
        return "default"

    # Первый доступный менеджер
    return next(iter(managers.keys()), None)


# ═══════════════════════════════════════════════════════════════
# РАСЧЁТ МЕТРИК
# ═══════════════════════════════════════════════════════════════

def calculate_response_times(messages: List[Dict], manager_id: str) -> Dict:
    """
    Расчёт времени отклика для менеджера.

    Алгоритм:
    1. Группируем сообщения по чатам (JID)
    2. Для каждого входящего ищем следующее исходящее
    3. Считаем дельту
    """
    # Группируем по чатам
    chats = defaultdict(list)
    for msg in messages:
        jid = msg.get("jid")
        if jid and not jid.endswith("@g.us"):  # Исключаем группы
            chats[jid].append(msg)

    # Сортируем сообщения в каждом чате
    for jid in chats:
        chats[jid].sort(key=lambda m: m.get("datetime", ""))

    response_times = []
    total_incoming = 0
    total_responded = 0
    total_no_response = 0

    fast_threshold = METRICS_CONFIG["fast_response_threshold_minutes"]
    max_wait_minutes = METRICS_CONFIG["max_response_wait_hours"] * 60

    response_by_hour = defaultdict(lambda: {"times": [], "count": 0})
    response_by_day = defaultdict(lambda: {"times": [], "count": 0})

    for jid, chat_messages in chats.items():
        i = 0
        while i < len(chat_messages):
            msg = chat_messages[i]
            is_from_me = msg.get("is_from_me", False)

            # Ищем входящее сообщение (от клиента)
            if not is_from_me:
                total_incoming += 1
                msg_dt = parse_datetime(msg.get("datetime"))

                if not msg_dt:
                    i += 1
                    continue

                # Ищем следующее исходящее сообщение (ответ менеджера)
                response_found = False
                for j in range(i + 1, len(chat_messages)):
                    next_msg = chat_messages[j]

                    if next_msg.get("is_from_me", False):
                        next_dt = parse_datetime(next_msg.get("datetime"))
                        if not next_dt:
                            continue

                        delta_minutes = (next_dt - msg_dt).total_seconds() / 60

                        if delta_minutes <= max_wait_minutes and delta_minutes >= 0:
                            response_times.append(delta_minutes)
                            total_responded += 1

                            # По часам
                            hour = msg_dt.hour
                            response_by_hour[hour]["times"].append(delta_minutes)
                            response_by_hour[hour]["count"] += 1

                            # По дням недели
                            day = msg_dt.strftime("%A")
                            response_by_day[day]["times"].append(delta_minutes)
                            response_by_day[day]["count"] += 1

                            response_found = True
                        break

                if not response_found:
                    total_no_response += 1

            i += 1

    # Расчёт статистик
    if response_times:
        avg_response = statistics.mean(response_times)
        median_response = statistics.median(response_times)
        p95_response = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 10 else max(response_times)
        fast_responses = sum(1 for t in response_times if t <= fast_threshold)
        fast_response_rate = fast_responses / len(response_times)
    else:
        avg_response = 0
        median_response = 0
        p95_response = 0
        fast_response_rate = 0

    response_rate = total_responded / total_incoming if total_incoming > 0 else 0

    return {
        "total_incoming": total_incoming,
        "total_responded": total_responded,
        "total_no_response": total_no_response,
        "response_rate": round(response_rate, 4),
        "avg_response_minutes": round(avg_response, 2),
        "median_response_minutes": round(median_response, 2),
        "p95_response_minutes": round(p95_response, 2),
        "fast_response_rate": round(fast_response_rate, 4),
        "response_by_hour": {
            str(h): {
                "avg": round(statistics.mean(d["times"]), 2) if d["times"] else 0,
                "count": d["count"]
            }
            for h, d in response_by_hour.items()
        },
        "response_by_day": {
            day: {
                "avg": round(statistics.mean(d["times"]), 2) if d["times"] else 0,
                "count": d["count"]
            }
            for day, d in response_by_day.items()
        }
    }


def calculate_dialogs_metrics(messages: List[Dict], contacts: List[Dict]) -> Dict:
    """Расчёт метрик по диалогам."""

    # Уникальные контакты
    unique_jids = set()
    unique_clients = set()

    contacts_by_jid = {c.get("jid"): c for c in contacts if c.get("jid")}

    for msg in messages:
        jid = msg.get("jid")
        if jid and not jid.endswith("@g.us"):
            unique_jids.add(jid)

            contact = contacts_by_jid.get(jid, {})
            if contact.get("type") in ["клиенты", "clients", "customer", None]:
                unique_clients.add(jid)

    # Сообщения по типам
    total_messages = len(messages)
    outgoing_messages = sum(1 for m in messages if m.get("is_from_me", False))
    incoming_messages = total_messages - outgoing_messages

    # Медиа
    voice_messages = sum(1 for m in messages if m.get("media_type") == "audio" or "audio" in m.get("text", "").lower())
    images = sum(1 for m in messages if m.get("media_type") == "image")
    documents = sum(1 for m in messages if m.get("media_type") == "document")

    return {
        "total_dialogs": len(unique_jids),
        "client_dialogs": len(unique_clients),
        "total_messages": total_messages,
        "outgoing_messages": outgoing_messages,
        "incoming_messages": incoming_messages,
        "avg_messages_per_dialog": round(total_messages / len(unique_jids), 2) if unique_jids else 0,
        "voice_messages": voice_messages,
        "images": images,
        "documents": documents
    }


def calculate_conversion_metrics(
    messages: List[Dict],
    operations: List[Dict],
    contacts: List[Dict]
) -> Dict:
    """Расчёт конверсионных метрик."""

    # Контакты с диалогами (потенциальные лиды)
    unique_jids = set()
    for msg in messages:
        jid = msg.get("jid")
        if jid and not jid.endswith("@g.us"):
            unique_jids.add(jid)

    total_leads = len(unique_jids)

    # Операции по статусам
    contacts_by_jid = {c.get("jid"): c for c in contacts if c.get("jid")}
    contacts_by_phone = {c.get("phone"): c for c in contacts if c.get("phone")}

    # Маппинг JID -> операции
    jid_to_phone = {}
    for jid in unique_jids:
        contact = contacts_by_jid.get(jid, {})
        phone = contact.get("phone")
        if phone:
            jid_to_phone[jid] = phone

    # Считаем конверсии
    quotes_sent = 0
    bookings = 0
    payments = 0
    completed = 0

    total_revenue = Decimal("0")
    order_values = []

    converted_jids = set()

    for op in operations:
        phone = op.get("phone")
        status = op.get("status", "").lower()

        # Проверяем, связана ли операция с нашими диалогами
        is_our_client = False
        for jid, p in jid_to_phone.items():
            if p == phone:
                is_our_client = True
                converted_jids.add(jid)
                break

        if not is_our_client:
            continue

        # Считаем по статусам
        if status in ["quote", "quoted"]:
            quotes_sent += 1
        elif status in ["booking", "booked", "confirmed"]:
            bookings += 1
        elif status in ["paid", "payment"]:
            payments += 1
        elif status == "completed":
            completed += 1
            amount = to_aed(op.get("amount", 0), op.get("currency", "AED"))
            total_revenue += amount
            if amount > 0:
                order_values.append(float(amount))

    # Расчёт конверсий
    lead_to_quote = quotes_sent / total_leads if total_leads > 0 else 0
    quote_to_booking = bookings / quotes_sent if quotes_sent > 0 else 0
    booking_to_payment = payments / bookings if bookings > 0 else 0
    overall_conversion = completed / total_leads if total_leads > 0 else 0

    # Средний чек
    avg_order_value = statistics.mean(order_values) if order_values else 0

    return {
        "total_leads": total_leads,
        "quotes_sent": quotes_sent,
        "bookings": bookings,
        "payments": payments,
        "completed": completed,
        "conversion_rates": {
            "lead_to_quote": round(lead_to_quote, 4),
            "quote_to_booking": round(quote_to_booking, 4),
            "booking_to_payment": round(booking_to_payment, 4),
            "overall": round(overall_conversion, 4)
        },
        "total_revenue_aed": float(total_revenue.quantize(Decimal("0.01"))),
        "avg_order_value_aed": round(avg_order_value, 2),
        "orders_count": len(order_values),
        "converted_clients": len(converted_jids)
    }


def calculate_manager_efficiency(
    manager_id: str,
    manager_info: Dict,
    messages: List[Dict],
    operations: List[Dict],
    contacts: List[Dict],
    period: str = None
) -> Dict:
    """
    Полный расчёт эффективности менеджера.
    """

    # Фильтруем сообщения по периоду
    if period:
        filtered_messages = []
        for msg in messages:
            msg_dt = parse_datetime(msg.get("datetime"))
            if msg_dt and msg_dt.strftime("%Y-%m") == period:
                filtered_messages.append(msg)
        messages = filtered_messages

    # Рассчитываем метрики
    response_metrics = calculate_response_times(messages, manager_id)
    dialog_metrics = calculate_dialogs_metrics(messages, contacts)
    conversion_metrics = calculate_conversion_metrics(messages, operations, contacts)

    # Определяем период анализа
    dates = [parse_datetime(m.get("datetime")) for m in messages if parse_datetime(m.get("datetime"))]
    if dates:
        first_date = min(dates).strftime("%Y-%m-%d")
        last_date = max(dates).strftime("%Y-%m-%d")
        days_analyzed = (max(dates) - min(dates)).days + 1
    else:
        first_date = None
        last_date = None
        days_analyzed = 0

    # Расчёт производительности
    messages_per_day = dialog_metrics["total_messages"] / days_analyzed if days_analyzed > 0 else 0
    dialogs_per_day = dialog_metrics["total_dialogs"] / days_analyzed if days_analyzed > 0 else 0
    revenue_per_day = conversion_metrics["total_revenue_aed"] / days_analyzed if days_analyzed > 0 else 0

    # Эффективность (сколько сообщений на одну конверсию)
    messages_per_conversion = dialog_metrics["total_messages"] / conversion_metrics["completed"] if conversion_metrics["completed"] > 0 else 0

    # Общий скоринг (0-100)
    score = calculate_efficiency_score(response_metrics, conversion_metrics, dialog_metrics)

    return {
        "manager_id": manager_id,
        "manager_name": manager_info.get("name", manager_id),
        "manager_role": manager_info.get("role", "manager"),
        "period": period or "all_time",
        "analysis_period": {
            "first_date": first_date,
            "last_date": last_date,
            "days_analyzed": days_analyzed
        },
        "response_metrics": response_metrics,
        "dialog_metrics": dialog_metrics,
        "conversion_metrics": conversion_metrics,
        "productivity": {
            "messages_per_day": round(messages_per_day, 2),
            "dialogs_per_day": round(dialogs_per_day, 2),
            "revenue_per_day_aed": round(revenue_per_day, 2),
            "messages_per_conversion": round(messages_per_conversion, 2)
        },
        "efficiency_score": score,
        "generated_at": datetime.now().isoformat()
    }


def calculate_efficiency_score(
    response_metrics: Dict,
    conversion_metrics: Dict,
    dialog_metrics: Dict
) -> Dict:
    """
    Расчёт общего скоринга эффективности (0-100).

    Компоненты:
    - Скорость ответа (30%)
    - Конверсия (35%)
    - Активность (20%)
    - Качество (15%)
    """
    scores = {}

    # 1. Скорость ответа (30%)
    # Целевое время ответа - 10 минут
    target_response = BENCHMARKS["avg_response_time_minutes"]
    actual_response = response_metrics.get("avg_response_minutes", 999)

    if actual_response <= target_response:
        response_score = 100
    elif actual_response <= target_response * 2:
        response_score = 100 - (actual_response - target_response) / target_response * 50
    elif actual_response <= target_response * 5:
        response_score = 50 - (actual_response - target_response * 2) / (target_response * 3) * 30
    else:
        response_score = max(0, 20 - (actual_response - target_response * 5) / target_response * 5)

    # Бонус за быстрые ответы
    fast_rate = response_metrics.get("fast_response_rate", 0)
    if fast_rate >= BENCHMARKS["fast_response_rate"]:
        response_score = min(100, response_score + 10)

    scores["response_speed"] = round(response_score, 2)

    # 2. Конверсия (35%)
    target_conversion = BENCHMARKS["conversion_rate"]
    actual_conversion = conversion_metrics.get("conversion_rates", {}).get("overall", 0)

    if actual_conversion >= target_conversion:
        conversion_score = 100
    else:
        conversion_score = (actual_conversion / target_conversion) * 100

    scores["conversion"] = round(conversion_score, 2)

    # 3. Активность (20%)
    response_rate = response_metrics.get("response_rate", 0)
    target_response_rate = BENCHMARKS["response_rate"]

    if response_rate >= target_response_rate:
        activity_score = 100
    else:
        activity_score = (response_rate / target_response_rate) * 100

    scores["activity"] = round(activity_score, 2)

    # 4. Качество / Средний чек (15%)
    target_avg_order = BENCHMARKS["avg_order_value_aed"]
    actual_avg_order = conversion_metrics.get("avg_order_value_aed", 0)

    if actual_avg_order >= target_avg_order:
        quality_score = 100
    elif actual_avg_order > 0:
        quality_score = (actual_avg_order / target_avg_order) * 100
    else:
        quality_score = 0

    scores["quality"] = round(quality_score, 2)

    # Итоговый скор
    total_score = (
        scores["response_speed"] * 0.30 +
        scores["conversion"] * 0.35 +
        scores["activity"] * 0.20 +
        scores["quality"] * 0.15
    )

    # Определение рейтинга
    if total_score >= 90:
        rating = "A+"
    elif total_score >= 80:
        rating = "A"
    elif total_score >= 70:
        rating = "B+"
    elif total_score >= 60:
        rating = "B"
    elif total_score >= 50:
        rating = "C"
    elif total_score >= 40:
        rating = "D"
    else:
        rating = "F"

    return {
        "total": round(total_score, 2),
        "rating": rating,
        "components": scores
    }


# ═══════════════════════════════════════════════════════════════
# СРАВНЕНИЕ МЕНЕДЖЕРОВ
# ═══════════════════════════════════════════════════════════════

def compare_managers(managers_data: List[Dict]) -> Dict:
    """Сравнительный анализ менеджеров."""

    if len(managers_data) < 2:
        return {"comparison_available": False, "reason": "Недостаточно менеджеров для сравнения"}

    # Сортировка по общему скору
    sorted_managers = sorted(
        managers_data,
        key=lambda x: x.get("efficiency_score", {}).get("total", 0),
        reverse=True
    )

    # Лидерборд
    leaderboard = []
    for i, m in enumerate(sorted_managers, 1):
        leaderboard.append({
            "rank": i,
            "manager_name": m.get("manager_name"),
            "manager_id": m.get("manager_id"),
            "score": m.get("efficiency_score", {}).get("total", 0),
            "rating": m.get("efficiency_score", {}).get("rating", "N/A"),
            "total_revenue": m.get("conversion_metrics", {}).get("total_revenue_aed", 0),
            "conversion_rate": m.get("conversion_metrics", {}).get("conversion_rates", {}).get("overall", 0),
            "avg_response": m.get("response_metrics", {}).get("avg_response_minutes", 0)
        })

    # Лучший в каждой категории
    best_in_category = {}

    # Лучший по скорости ответа
    best_response = min(sorted_managers, key=lambda x: x.get("response_metrics", {}).get("avg_response_minutes", 999))
    best_in_category["fastest_response"] = {
        "manager": best_response.get("manager_name"),
        "value": best_response.get("response_metrics", {}).get("avg_response_minutes", 0),
        "unit": "минут"
    }

    # Лучший по конверсии
    best_conversion = max(sorted_managers, key=lambda x: x.get("conversion_metrics", {}).get("conversion_rates", {}).get("overall", 0))
    best_in_category["best_conversion"] = {
        "manager": best_conversion.get("manager_name"),
        "value": best_conversion.get("conversion_metrics", {}).get("conversion_rates", {}).get("overall", 0) * 100,
        "unit": "%"
    }

    # Лучший по выручке
    best_revenue = max(sorted_managers, key=lambda x: x.get("conversion_metrics", {}).get("total_revenue_aed", 0))
    best_in_category["highest_revenue"] = {
        "manager": best_revenue.get("manager_name"),
        "value": best_revenue.get("conversion_metrics", {}).get("total_revenue_aed", 0),
        "unit": "AED"
    }

    # Лучший по среднему чеку
    best_avg_order = max(sorted_managers, key=lambda x: x.get("conversion_metrics", {}).get("avg_order_value_aed", 0))
    best_in_category["highest_avg_order"] = {
        "manager": best_avg_order.get("manager_name"),
        "value": best_avg_order.get("conversion_metrics", {}).get("avg_order_value_aed", 0),
        "unit": "AED"
    }

    # Средние показатели команды
    team_averages = {
        "avg_response_minutes": statistics.mean([
            m.get("response_metrics", {}).get("avg_response_minutes", 0) for m in sorted_managers
        ]),
        "avg_conversion_rate": statistics.mean([
            m.get("conversion_metrics", {}).get("conversion_rates", {}).get("overall", 0) for m in sorted_managers
        ]),
        "avg_score": statistics.mean([
            m.get("efficiency_score", {}).get("total", 0) for m in sorted_managers
        ]),
        "total_revenue": sum([
            m.get("conversion_metrics", {}).get("total_revenue_aed", 0) for m in sorted_managers
        ])
    }

    return {
        "comparison_available": True,
        "managers_count": len(sorted_managers),
        "leaderboard": leaderboard,
        "best_in_category": best_in_category,
        "team_averages": {
            "avg_response_minutes": round(team_averages["avg_response_minutes"], 2),
            "avg_conversion_rate": round(team_averages["avg_conversion_rate"] * 100, 2),
            "avg_score": round(team_averages["avg_score"], 2),
            "total_revenue_aed": round(team_averages["total_revenue"], 2)
        }
    }


# ═══════════════════════════════════════════════════════════════
# ВЫЯВЛЕНИЕ СЛАБЫХ МЕСТ И РЕКОМЕНДАЦИИ
# ═══════════════════════════════════════════════════════════════

def identify_weaknesses(efficiency_data: Dict) -> List[Dict]:
    """Выявление слабых мест менеджера."""

    weaknesses = []
    score_components = efficiency_data.get("efficiency_score", {}).get("components", {})
    response = efficiency_data.get("response_metrics", {})
    conversion = efficiency_data.get("conversion_metrics", {})

    # 1. Медленные ответы
    if score_components.get("response_speed", 100) < 60:
        avg_response = response.get("avg_response_minutes", 0)
        weaknesses.append({
            "area": "Скорость ответа",
            "severity": "high" if avg_response > 30 else "medium",
            "current_value": f"{avg_response:.1f} мин",
            "target_value": f"{BENCHMARKS['avg_response_time_minutes']} мин",
            "impact": "Клиенты могут уходить к конкурентам при долгом ожидании ответа"
        })

    # 2. Низкая конверсия
    if score_components.get("conversion", 100) < 50:
        conv_rate = conversion.get("conversion_rates", {}).get("overall", 0)
        weaknesses.append({
            "area": "Конверсия",
            "severity": "high" if conv_rate < 0.1 else "medium",
            "current_value": f"{conv_rate * 100:.1f}%",
            "target_value": f"{BENCHMARKS['conversion_rate'] * 100}%",
            "impact": "Много потерянных потенциальных клиентов"
        })

    # 3. Низкий процент ответов
    response_rate = response.get("response_rate", 0)
    if response_rate < BENCHMARKS["response_rate"]:
        weaknesses.append({
            "area": "Процент отвеченных сообщений",
            "severity": "high" if response_rate < 0.8 else "medium",
            "current_value": f"{response_rate * 100:.1f}%",
            "target_value": f"{BENCHMARKS['response_rate'] * 100}%",
            "impact": "Клиенты остаются без ответа"
        })

    # 4. Низкий средний чек
    avg_order = conversion.get("avg_order_value_aed", 0)
    if avg_order < BENCHMARKS["avg_order_value_aed"] and avg_order > 0:
        weaknesses.append({
            "area": "Средний чек",
            "severity": "medium",
            "current_value": f"{avg_order:.0f} AED",
            "target_value": f"{BENCHMARKS['avg_order_value_aed']} AED",
            "impact": "Упущенная выручка от апсейла"
        })

    # 5. Низкий процент быстрых ответов
    fast_rate = response.get("fast_response_rate", 0)
    if fast_rate < BENCHMARKS["fast_response_rate"]:
        weaknesses.append({
            "area": "Быстрые ответы",
            "severity": "medium",
            "current_value": f"{fast_rate * 100:.1f}%",
            "target_value": f"{BENCHMARKS['fast_response_rate'] * 100}%",
            "impact": "Клиенты ожидают мгновенного ответа в мессенджерах"
        })

    return weaknesses


def generate_recommendations(efficiency_data: Dict, weaknesses: List[Dict]) -> List[Dict]:
    """Генерация рекомендаций на основе слабых мест."""

    recommendations = []

    for weakness in weaknesses:
        area = weakness["area"]
        severity = weakness["severity"]

        if area == "Скорость ответа":
            recommendations.append({
                "priority": 1 if severity == "high" else 2,
                "area": area,
                "recommendation": "Настроить уведомления о новых сообщениях",
                "actions": [
                    "Включить push-уведомления WhatsApp",
                    "Настроить звуковые оповещения",
                    "Использовать WhatsApp Web для быстрого ответа с компьютера",
                    "Подготовить шаблоны быстрых ответов"
                ],
                "expected_improvement": "Сокращение времени ответа на 50-70%"
            })

        elif area == "Конверсия":
            recommendations.append({
                "priority": 1 if severity == "high" else 2,
                "area": area,
                "recommendation": "Улучшить воронку продаж",
                "actions": [
                    "Анализировать причины отказов",
                    "Подготовить скрипты продаж",
                    "Делать follow-up через 24-48 часов",
                    "Предлагать альтернативы при отказе",
                    "Использовать социальное доказательство (отзывы)"
                ],
                "expected_improvement": "Рост конверсии на 20-40%"
            })

        elif area == "Процент отвеченных сообщений":
            recommendations.append({
                "priority": 1,
                "area": area,
                "recommendation": "Отвечать на все входящие сообщения",
                "actions": [
                    "Проверять чаты каждые 2-3 часа",
                    "Использовать автоответы в нерабочее время",
                    "Не оставлять сообщения без реакции",
                    "Если нет ответа - написать 'Уточню и вернусь'"
                ],
                "expected_improvement": "Увеличение отвеченных до 95%+"
            })

        elif area == "Средний чек":
            recommendations.append({
                "priority": 2,
                "area": area,
                "recommendation": "Увеличить средний чек через апсейл",
                "actions": [
                    "Предлагать комплементарные услуги",
                    "Рассказывать о VIP-опциях",
                    "Создать пакетные предложения",
                    "Предлагать скидку при заказе нескольких услуг"
                ],
                "expected_improvement": "Рост среднего чека на 15-30%"
            })

        elif area == "Быстрые ответы":
            recommendations.append({
                "priority": 2,
                "area": area,
                "recommendation": "Ускорить первичный ответ",
                "actions": [
                    "Отвечать в течение 5 минут в рабочее время",
                    "Подготовить шаблоны приветствий",
                    "Использовать быстрые ответы WhatsApp Business",
                    "Делегировать первичный контакт при загруженности"
                ],
                "expected_improvement": "70%+ ответов менее чем за 5 минут"
            })

    # Сортируем по приоритету
    recommendations.sort(key=lambda x: x["priority"])

    return recommendations


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТОВ
# ═══════════════════════════════════════════════════════════════

def generate_markdown_report(
    managers_data: List[Dict],
    comparison: Dict,
    period: str = None
) -> str:
    """Генерация Markdown отчёта для руководителя."""

    md = []
    md.append("# Отчёт об эффективности менеджеров")
    md.append(f"\n*Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    md.append(f"*Период: {period or 'все время'}*\n")

    # Сводка по команде
    if comparison.get("comparison_available"):
        team = comparison.get("team_averages", {})
        md.append("## Сводка по команде\n")
        md.append("| Показатель | Значение |")
        md.append("|------------|----------|")
        md.append(f"| Менеджеров | {comparison.get('managers_count', 0)} |")
        md.append(f"| Общая выручка | {team.get('total_revenue_aed', 0):,.0f} AED |")
        md.append(f"| Средний скор | {team.get('avg_score', 0):.1f}/100 |")
        md.append(f"| Средняя конверсия | {team.get('avg_conversion_rate', 0):.1f}% |")
        md.append(f"| Среднее время ответа | {team.get('avg_response_minutes', 0):.1f} мин |")
        md.append("")

        # Лидерборд
        leaderboard = comparison.get("leaderboard", [])
        if leaderboard:
            md.append("## Рейтинг менеджеров\n")
            md.append("| # | Менеджер | Скор | Рейтинг | Выручка | Конверсия | Время ответа |")
            md.append("|---|----------|------|---------|---------|-----------|--------------|")

            for entry in leaderboard:
                md.append(
                    f"| {entry['rank']} | {entry['manager_name']} | "
                    f"{entry['score']:.1f} | {entry['rating']} | "
                    f"{entry['total_revenue']:,.0f} | "
                    f"{entry['conversion_rate']*100:.1f}% | "
                    f"{entry['avg_response']:.1f} мин |"
                )
            md.append("")

        # Лучшие в категориях
        best = comparison.get("best_in_category", {})
        if best:
            md.append("## Лидеры в категориях\n")
            category_names = {
                "fastest_response": "Самый быстрый ответ",
                "best_conversion": "Лучшая конверсия",
                "highest_revenue": "Максимальная выручка",
                "highest_avg_order": "Наибольший средний чек"
            }
            for cat_key, cat_data in best.items():
                cat_name = category_names.get(cat_key, cat_key)
                md.append(f"- **{cat_name}:** {cat_data['manager']} ({cat_data['value']:.1f} {cat_data['unit']})")
            md.append("")

    # Детальный анализ по каждому менеджеру
    md.append("---\n")
    md.append("## Детальный анализ\n")

    for manager in managers_data:
        name = manager.get("manager_name", "Неизвестно")
        score = manager.get("efficiency_score", {})
        response = manager.get("response_metrics", {})
        conversion = manager.get("conversion_metrics", {})
        dialog = manager.get("dialog_metrics", {})
        productivity = manager.get("productivity", {})

        md.append(f"### {name}\n")
        md.append(f"**Общий скор: {score.get('total', 0):.1f}/100 ({score.get('rating', 'N/A')})**\n")

        # Таблица метрик
        md.append("| Метрика | Значение | Цель |")
        md.append("|---------|----------|------|")
        md.append(f"| Время ответа | {response.get('avg_response_minutes', 0):.1f} мин | < {BENCHMARKS['avg_response_time_minutes']} мин |")
        md.append(f"| Быстрые ответы | {response.get('fast_response_rate', 0)*100:.1f}% | > {BENCHMARKS['fast_response_rate']*100}% |")
        md.append(f"| Отвечено | {response.get('response_rate', 0)*100:.1f}% | > {BENCHMARKS['response_rate']*100}% |")
        md.append(f"| Конверсия | {conversion.get('conversion_rates', {}).get('overall', 0)*100:.1f}% | > {BENCHMARKS['conversion_rate']*100}% |")
        md.append(f"| Средний чек | {conversion.get('avg_order_value_aed', 0):.0f} AED | > {BENCHMARKS['avg_order_value_aed']} AED |")
        md.append(f"| Выручка | {conversion.get('total_revenue_aed', 0):,.0f} AED | - |")
        md.append(f"| Диалогов | {dialog.get('total_dialogs', 0)} | - |")
        md.append(f"| Сообщений | {dialog.get('total_messages', 0)} | - |")
        md.append("")

        # Слабые места
        weaknesses = identify_weaknesses(manager)
        if weaknesses:
            md.append("**Области для улучшения:**\n")
            for w in weaknesses:
                severity_icon = "!!!" if w["severity"] == "high" else "!"
                md.append(f"- {severity_icon} **{w['area']}**: {w['current_value']} (цель: {w['target_value']})")
            md.append("")

        # Рекомендации
        recommendations = generate_recommendations(manager, weaknesses)
        if recommendations:
            md.append("**Рекомендации:**\n")
            for r in recommendations[:3]:  # Топ-3 рекомендации
                md.append(f"1. **{r['recommendation']}**")
                for action in r["actions"][:3]:
                    md.append(f"   - {action}")
            md.append("")

        md.append("---\n")

    # Итоговые рекомендации для команды
    md.append("## Общие рекомендации для команды\n")
    md.append("1. Установить единые стандарты времени ответа (< 5 минут в рабочее время)")
    md.append("2. Внедрить систему шаблонов и быстрых ответов")
    md.append("3. Проводить еженедельный разбор лучших практик")
    md.append("4. Мотивировать на улучшение показателей через KPI")
    md.append("5. Регулярно анализировать причины отказов клиентов")
    md.append("")

    return "\n".join(md)


def generate_pdf_report(
    managers_data: List[Dict],
    comparison: Dict,
    filepath: Path,
    period: str = None
):
    """Генерация PDF отчёта."""

    if not REPORTLAB_AVAILABLE:
        print("[!] PDF генерация недоступна (reportlab не установлен)")
        return

    # Регистрация шрифта с кириллицей
    font_registered = False
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                font_registered = True
                break
            except:
                continue

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()

    # Кастомные стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName='CustomFont' if font_registered else 'Helvetica',
        fontSize=18,
        textColor=HexColor(COLORS["primary"])
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='CustomFont' if font_registered else 'Helvetica',
        fontSize=14,
        textColor=HexColor(COLORS["secondary"])
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='CustomFont' if font_registered else 'Helvetica',
        fontSize=10
    )

    elements = []

    # Заголовок
    elements.append(Paragraph("Manager Efficiency Report", title_style))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Period: {period or 'All Time'}",
        body_style
    ))
    elements.append(Spacer(1, 10*mm))

    # Сводка команды
    if comparison.get("comparison_available"):
        elements.append(Paragraph("Team Summary", heading_style))
        elements.append(Spacer(1, 5*mm))

        team = comparison.get("team_averages", {})
        summary_data = [
            ["Metric", "Value"],
            ["Total Revenue", f"{team.get('total_revenue_aed', 0):,.0f} AED"],
            ["Average Score", f"{team.get('avg_score', 0):.1f}/100"],
            ["Average Conversion", f"{team.get('avg_conversion_rate', 0):.1f}%"],
            ["Average Response Time", f"{team.get('avg_response_minutes', 0):.1f} min"]
        ]

        table = Table(summary_data, colWidths=[100*mm, 60*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["primary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10*mm))

        # Лидерборд
        leaderboard = comparison.get("leaderboard", [])
        if leaderboard:
            elements.append(Paragraph("Leaderboard", heading_style))
            elements.append(Spacer(1, 5*mm))

            lb_data = [["#", "Manager", "Score", "Rating", "Revenue", "Conversion"]]
            for entry in leaderboard:
                lb_data.append([
                    str(entry["rank"]),
                    entry["manager_name"][:20],
                    f"{entry['score']:.1f}",
                    entry["rating"],
                    f"{entry['total_revenue']:,.0f}",
                    f"{entry['conversion_rate']*100:.1f}%"
                ])

            table = Table(lb_data, colWidths=[10*mm, 45*mm, 25*mm, 20*mm, 35*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["secondary"])),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements.append(table)

    # Сохранение PDF
    filepath.parent.mkdir(parents=True, exist_ok=True)
    doc.build(elements)
    print(f"[+] PDF сохранён: {filepath}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Анализ эффективности менеджеров",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--manager", "-m",
        type=str,
        help="Анализ конкретного менеджера (имя или ID)"
    )
    parser.add_argument(
        "--period", "-p",
        type=str,
        help="Период анализа (YYYY-MM)"
    )
    parser.add_argument(
        "--compare", "-c",
        action="store_true",
        help="Сравнительный анализ менеджеров"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv", "md", "pdf", "all"],
        default="all",
        help="Формат вывода (по умолчанию: all)"
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Экспортировать в CSV"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        help="Директория для сохранения отчётов"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Минимальный вывод"
    )

    args = parser.parse_args()

    # Определяем форматы
    if args.format == "all":
        formats = ["json", "md"]
        if args.export_csv:
            formats.append("csv")
        if REPORTLAB_AVAILABLE:
            formats.append("pdf")
    else:
        formats = [args.format]

    # Директория вывода
    output_dir = args.output_dir or REPORTS_DIR / "managers"
    if args.period:
        output_dir = output_dir / args.period
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("АНАЛИЗ ЭФФЕКТИВНОСТИ МЕНЕДЖЕРОВ")
    print("=" * 60)

    # Загрузка данных
    print("\n[1] Загрузка данных...")
    messages = load_jsonl(MESSAGES_FILE)
    print(f"    Сообщений: {len(messages):,}")

    contacts = load_json(CONTACTS_FILE)
    print(f"    Контактов: {len(contacts):,}")

    operations = load_json(OPERATIONS_FILE)
    print(f"    Операций: {len(operations):,}")

    if not messages:
        print("\n[!] Нет сообщений для анализа.")
        print(f"    Ожидается файл: {MESSAGES_FILE}")
        print("    Запустите сначала parse_all_chats.py для генерации all_messages.jsonl")
        return

    # Определение менеджеров
    print("\n[2] Определение менеджеров...")
    managers = identify_managers(messages)
    print(f"    Найдено менеджеров: {len(managers)}")

    for m_id, m_info in managers.items():
        print(f"    - {m_info['name']} ({m_info['identified_by']})")

    # Фильтрация по конкретному менеджеру
    if args.manager:
        filtered_managers = {
            m_id: m_info for m_id, m_info in managers.items()
            if args.manager.lower() in m_info.get("name", "").lower() or args.manager == m_id
        }
        if not filtered_managers:
            print(f"\n[!] Менеджер '{args.manager}' не найден")
            return
        managers = filtered_managers

    # Анализ каждого менеджера
    print("\n[3] Анализ эффективности...")
    managers_data = []

    for manager_id, manager_info in managers.items():
        print(f"    Анализ: {manager_info['name']}...")

        efficiency = calculate_manager_efficiency(
            manager_id,
            manager_info,
            messages,
            operations,
            contacts,
            args.period
        )

        # Добавляем слабые места и рекомендации
        weaknesses = identify_weaknesses(efficiency)
        recommendations = generate_recommendations(efficiency, weaknesses)

        efficiency["weaknesses"] = weaknesses
        efficiency["recommendations"] = recommendations

        managers_data.append(efficiency)

        # Вывод кратких результатов
        score = efficiency.get("efficiency_score", {})
        print(f"        Скор: {score.get('total', 0):.1f}/100 ({score.get('rating', 'N/A')})")

    # Сравнение менеджеров
    print("\n[4] Сравнительный анализ...")
    comparison = compare_managers(managers_data)

    if comparison.get("comparison_available"):
        print(f"    Лидер: {comparison['leaderboard'][0]['manager_name']} ({comparison['leaderboard'][0]['score']:.1f})")

    # Формирование итогового результата
    result = {
        "generated_at": datetime.now().isoformat(),
        "period": args.period or "all_time",
        "managers_count": len(managers_data),
        "managers": managers_data,
        "comparison": comparison,
        "benchmarks": BENCHMARKS
    }

    # Сохранение отчётов
    print("\n[5] Сохранение отчётов...")

    if "json" in formats:
        json_path = output_dir / "manager_efficiency.json"
        save_json(result, json_path)

    if "md" in formats:
        md_content = generate_markdown_report(managers_data, comparison, args.period)
        md_path = output_dir / "эффективность_менеджеров.md"
        md_path.write_text(md_content, encoding="utf-8")
        print(f"[+] Markdown сохранён: {md_path}")

    if "csv" in formats or args.export_csv:
        csv_data = []
        for m in managers_data:
            csv_data.append({
                "manager_name": m.get("manager_name"),
                "manager_id": m.get("manager_id"),
                "score": m.get("efficiency_score", {}).get("total"),
                "rating": m.get("efficiency_score", {}).get("rating"),
                "avg_response_minutes": m.get("response_metrics", {}).get("avg_response_minutes"),
                "fast_response_rate": m.get("response_metrics", {}).get("fast_response_rate"),
                "response_rate": m.get("response_metrics", {}).get("response_rate"),
                "conversion_rate": m.get("conversion_metrics", {}).get("conversion_rates", {}).get("overall"),
                "total_revenue_aed": m.get("conversion_metrics", {}).get("total_revenue_aed"),
                "avg_order_value_aed": m.get("conversion_metrics", {}).get("avg_order_value_aed"),
                "total_dialogs": m.get("dialog_metrics", {}).get("total_dialogs"),
                "total_messages": m.get("dialog_metrics", {}).get("total_messages"),
            })

        csv_path = output_dir / "manager_efficiency.csv"
        save_csv(csv_data, csv_path, list(csv_data[0].keys()) if csv_data else [])

    if "pdf" in formats:
        pdf_path = output_dir / "manager_efficiency.pdf"
        generate_pdf_report(managers_data, comparison, pdf_path, args.period)

    # Вывод итогов
    if not args.quiet:
        print("\n" + "=" * 60)
        print("ИТОГИ АНАЛИЗА")
        print("=" * 60)

        if comparison.get("comparison_available"):
            team = comparison.get("team_averages", {})
            print(f"\nКоманда ({len(managers_data)} менеджеров):")
            print(f"  Общая выручка: {team.get('total_revenue_aed', 0):,.0f} AED")
            print(f"  Средний скор: {team.get('avg_score', 0):.1f}/100")
            print(f"  Средняя конверсия: {team.get('avg_conversion_rate', 0):.1f}%")
            print(f"  Среднее время ответа: {team.get('avg_response_minutes', 0):.1f} мин")

            print("\nРейтинг:")
            for entry in comparison.get("leaderboard", []):
                print(f"  {entry['rank']}. {entry['manager_name']}: {entry['score']:.1f} ({entry['rating']})")
        else:
            for m in managers_data:
                print(f"\n{m.get('manager_name')}:")
                score = m.get("efficiency_score", {})
                print(f"  Скор: {score.get('total', 0):.1f}/100 ({score.get('rating', 'N/A')})")
                print(f"  Выручка: {m.get('conversion_metrics', {}).get('total_revenue_aed', 0):,.0f} AED")

    print(f"\n[+] Отчёты сохранены в: {output_dir}")
    print("[+] Анализ завершён!")


if __name__ == "__main__":
    main()
