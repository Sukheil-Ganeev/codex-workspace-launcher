#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
financial_reports.py - Финансовая отчётность для туристического бизнеса

Генерирует отчёты:
1. P&L (Profit & Loss) - выручка, себестоимость, прибыль по категориям
2. Cash Flow - поступления, ожидаемые платежи, дебиторка, прогноз
3. Unit Economics - CAC, LTV/CAC, средний чек, маржинальность
4. Агентские отчёты - выручка от агентов, комиссии, топ агенты

Форматы вывода: JSON, CSV, PDF, Markdown

Использование:
    python financial_reports.py                      # Все отчёты
    python financial_reports.py --report pnl         # Только P&L
    python financial_reports.py --report cashflow    # Cash Flow
    python financial_reports.py --report unit        # Unit Economics
    python financial_reports.py --report agents      # Агентские
    python financial_reports.py --period 2024-01     # За январь 2024
    python financial_reports.py --compare-yoy        # Сравнение год к году
    python financial_reports.py --format pdf         # Только PDF
    python financial_reports.py --format all         # Все форматы (default)
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, List, Any
from decimal import Decimal, ROUND_HALF_UP
import calendar

# Опциональный импорт reportlab для PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image
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
REPORTS_DIR = BASE_DIR / "reports"

# Входные файлы
OPERATIONS_FILE = JSON_DIR / "operations.json"
CONTACTS_FILE = JSON_DIR / "contacts.json"

# Категории операций для P&L
REVENUE_CATEGORIES = {
    "tours": {
        "name": "Туры и экскурсии",
        "keywords": ["tour", "экскурсия", "сафари", "тур", "museum", "city tour"],
        "margin": 0.25  # Средняя маржинальность
    },
    "transfers": {
        "name": "Трансферы",
        "keywords": ["transfer", "трансфер", "airport", "аэропорт", "встреча"],
        "margin": 0.35
    },
    "yachts": {
        "name": "Яхты",
        "keywords": ["yacht", "яхта", "boat", "катер", "лодка"],
        "margin": 0.20
    },
    "tickets": {
        "name": "Билеты и парки",
        "keywords": ["ticket", "билет", "park", "парк", "ferrari", "aquaventure"],
        "margin": 0.15
    },
    "exchange": {
        "name": "Обмен валюты",
        "keywords": ["exchange", "обмен", "валюта", "курс"],
        "margin": 0.02
    },
    "car_rental": {
        "name": "Аренда авто",
        "keywords": ["car", "rental", "аренда", "авто", "машина"],
        "margin": 0.30
    },
    "catering": {
        "name": "Кейтеринг",
        "keywords": ["catering", "кейтеринг", "еда", "ресторан", "food"],
        "margin": 0.25
    },
    "other": {
        "name": "Прочее",
        "keywords": [],
        "margin": 0.20
    }
}

# Ставки комиссий агентам
AGENT_COMMISSION_RATES = {
    "default": 0.10,      # 10% по умолчанию
    "турагент": 0.10,
    "туроператор": 0.08,
    "B2B": 0.12,
    "VIP": 0.07
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


def load_json(filepath: Path) -> list:
    """Загрузка JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


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


def parse_date(date_str: str) -> Optional[datetime]:
    """Парсинг даты из разных форматов."""
    if not date_str:
        return None

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d.%m.%Y",
        "%d/%m/%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str[:19], fmt)
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
    elif period_type == "quarter":
        quarter = (date.month - 1) // 3 + 1
        return f"{date.year}-Q{quarter}"
    elif period_type == "year":
        return str(date.year)
    elif period_type == "day":
        return date.strftime("%Y-%m-%d")
    return date.strftime("%Y-%m")


def categorize_operation(operation: dict) -> str:
    """Определить категорию операции."""
    op_type = operation.get("type", "").lower()
    description = operation.get("description", "").lower()
    combined = f"{op_type} {description}"

    for category, info in REVENUE_CATEGORIES.items():
        if category == "other":
            continue
        for keyword in info["keywords"]:
            if keyword.lower() in combined:
                return category

    return "other"


def filter_operations_by_period(operations: list, period: str = None,
                                 start_date: str = None, end_date: str = None) -> list:
    """Фильтрация операций по периоду."""
    if not operations:
        return []

    filtered = []

    for op in operations:
        op_date = parse_date(op.get("date"))
        if not op_date:
            continue

        # Фильтр по указанному периоду (YYYY-MM)
        if period:
            op_period = op_date.strftime("%Y-%m")
            if op_period != period:
                continue

        # Фильтр по диапазону дат
        if start_date:
            start = parse_date(start_date)
            if start and op_date < start:
                continue

        if end_date:
            end = parse_date(end_date)
            if end and op_date > end:
                continue

        filtered.append(op)

    return filtered


# ═══════════════════════════════════════════════════════════════
# P&L (PROFIT & LOSS)
# ═══════════════════════════════════════════════════════════════

def calculate_pnl(operations: list, contacts: list, period: str = None) -> dict:
    """Расчёт P&L отчёта."""

    # Фильтруем операции
    if period:
        ops = filter_operations_by_period(operations, period=period)
    else:
        ops = [op for op in operations if op.get("status") == "completed"]

    # Инициализация структуры
    revenue_by_category = {cat: Decimal("0") for cat in REVENUE_CATEGORIES}
    cost_by_category = {cat: Decimal("0") for cat in REVENUE_CATEGORIES}

    # Агентские комиссии
    contacts_by_phone = {c.get("phone"): c for c in contacts if c.get("phone")}
    agent_commissions = Decimal("0")

    # Группировка по периодам для сравнения
    by_period = defaultdict(lambda: {
        "revenue": Decimal("0"),
        "cost": Decimal("0"),
        "gross_profit": Decimal("0"),
        "commissions": Decimal("0"),
        "net_profit": Decimal("0"),
        "orders_count": 0
    })

    for op in ops:
        if op.get("status") != "completed":
            continue

        amount = to_aed(op.get("amount", 0), op.get("currency", "AED"))
        category = categorize_operation(op)
        margin = Decimal(str(REVENUE_CATEGORIES[category]["margin"]))

        # Выручка
        revenue_by_category[category] += amount

        # Себестоимость (выручка минус маржа)
        cost = amount * (Decimal("1") - margin)
        cost_by_category[category] += cost

        # Комиссия агента (если есть)
        phone = op.get("phone")
        contact = contacts_by_phone.get(phone, {})
        contact_type = contact.get("type", "")
        contact_subtype = contact.get("subtype", "")

        if contact_type == "агенты":
            commission_rate = Decimal(str(
                AGENT_COMMISSION_RATES.get(contact_subtype,
                AGENT_COMMISSION_RATES["default"])
            ))
            commission = amount * commission_rate
            agent_commissions += commission

        # По периодам
        op_date = parse_date(op.get("date"))
        if op_date:
            period_key = get_period_key(op_date, "month")
            by_period[period_key]["revenue"] += amount
            by_period[period_key]["cost"] += cost
            by_period[period_key]["orders_count"] += 1

    # Итоги
    total_revenue = sum(revenue_by_category.values())
    total_cost = sum(cost_by_category.values())
    gross_profit = total_revenue - total_cost
    net_profit = gross_profit - agent_commissions

    # Расчёт маржинальности
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else Decimal("0")
    net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal("0")

    # Расчёт для сравнения периодов
    for period_key, data in by_period.items():
        data["gross_profit"] = data["revenue"] - data["cost"]
        data["commissions"] = data["revenue"] * Decimal("0.08")  # Средняя комиссия
        data["net_profit"] = data["gross_profit"] - data["commissions"]

    # Сравнение MoM и YoY
    periods_sorted = sorted(by_period.keys(), reverse=True)
    comparison = {}

    if len(periods_sorted) >= 2:
        current = periods_sorted[0]
        previous = periods_sorted[1]

        current_data = by_period[current]
        previous_data = by_period[previous]

        if previous_data["revenue"] > 0:
            comparison["mom_revenue_change"] = float(
                ((current_data["revenue"] - previous_data["revenue"]) /
                 previous_data["revenue"] * 100).quantize(Decimal("0.01"))
            )
            comparison["mom_profit_change"] = float(
                ((current_data["net_profit"] - previous_data["net_profit"]) /
                 abs(previous_data["net_profit"]) * 100).quantize(Decimal("0.01"))
            ) if previous_data["net_profit"] != 0 else 0

    # YoY сравнение
    if len(periods_sorted) >= 13:
        current = periods_sorted[0]
        year_ago_key = f"{int(current[:4])-1}{current[4:]}"

        if year_ago_key in by_period:
            year_ago_data = by_period[year_ago_key]
            if year_ago_data["revenue"] > 0:
                comparison["yoy_revenue_change"] = float(
                    ((by_period[current]["revenue"] - year_ago_data["revenue"]) /
                     year_ago_data["revenue"] * 100).quantize(Decimal("0.01"))
                )

    return {
        "period": period or "all_time",
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_revenue_aed": float(total_revenue.quantize(Decimal("0.01"))),
            "total_cost_aed": float(total_cost.quantize(Decimal("0.01"))),
            "gross_profit_aed": float(gross_profit.quantize(Decimal("0.01"))),
            "agent_commissions_aed": float(agent_commissions.quantize(Decimal("0.01"))),
            "net_profit_aed": float(net_profit.quantize(Decimal("0.01"))),
            "gross_margin_percent": float(gross_margin.quantize(Decimal("0.01"))),
            "net_margin_percent": float(net_margin.quantize(Decimal("0.01"))),
            "total_orders": len(ops)
        },
        "by_category": {
            cat: {
                "name": REVENUE_CATEGORIES[cat]["name"],
                "revenue_aed": float(revenue_by_category[cat].quantize(Decimal("0.01"))),
                "cost_aed": float(cost_by_category[cat].quantize(Decimal("0.01"))),
                "profit_aed": float((revenue_by_category[cat] - cost_by_category[cat]).quantize(Decimal("0.01"))),
                "margin_percent": REVENUE_CATEGORIES[cat]["margin"] * 100,
                "share_percent": float(
                    (revenue_by_category[cat] / total_revenue * 100).quantize(Decimal("0.01"))
                ) if total_revenue > 0 else 0
            }
            for cat in REVENUE_CATEGORIES
        },
        "by_period": {
            k: {
                "revenue_aed": float(v["revenue"].quantize(Decimal("0.01"))),
                "cost_aed": float(v["cost"].quantize(Decimal("0.01"))),
                "gross_profit_aed": float(v["gross_profit"].quantize(Decimal("0.01"))),
                "commissions_aed": float(v["commissions"].quantize(Decimal("0.01"))),
                "net_profit_aed": float(v["net_profit"].quantize(Decimal("0.01"))),
                "orders_count": v["orders_count"]
            }
            for k, v in sorted(by_period.items(), reverse=True)[:12]
        },
        "comparison": comparison
    }


# ═══════════════════════════════════════════════════════════════
# CASH FLOW
# ═══════════════════════════════════════════════════════════════

def calculate_cashflow(operations: list, contacts: list, forecast_days: int = 30) -> dict:
    """Расчёт Cash Flow отчёта."""

    today = datetime.now().date()

    # Поступления (завершённые операции)
    completed_ops = [op for op in operations if op.get("status") == "completed"]

    # Ожидаемые платежи (pending)
    pending_ops = [op for op in operations if op.get("status") in ["pending", "confirmed"]]

    # Дебиторская задолженность (выполнено но не оплачено)
    receivables = [op for op in operations if op.get("status") == "completed" and
                   op.get("payment_status") == "pending"]

    # Группировка поступлений по дням
    inflows_by_day = defaultdict(Decimal)
    inflows_by_week = defaultdict(Decimal)

    for op in completed_ops:
        op_date = parse_date(op.get("date"))
        if not op_date:
            continue

        amount = to_aed(op.get("amount", 0), op.get("currency", "AED"))

        day_key = op_date.strftime("%Y-%m-%d")
        week_key = get_period_key(op_date, "week")

        inflows_by_day[day_key] += amount
        inflows_by_week[week_key] += amount

    # Расчёт дебиторки
    total_receivables = Decimal("0")
    receivables_detail = []

    contacts_by_phone = {c.get("phone"): c for c in contacts if c.get("phone")}

    for op in receivables:
        amount = to_aed(op.get("amount", 0), op.get("currency", "AED"))
        total_receivables += amount

        phone = op.get("phone")
        contact = contacts_by_phone.get(phone, {})

        receivables_detail.append({
            "date": op.get("date"),
            "amount_aed": float(amount.quantize(Decimal("0.01"))),
            "customer": contact.get("name", phone),
            "type": op.get("type"),
            "days_overdue": (today - parse_date(op.get("date")).date()).days if parse_date(op.get("date")) else 0
        })

    # Ожидаемые платежи
    expected_payments = Decimal("0")
    expected_detail = []

    for op in pending_ops:
        amount = to_aed(op.get("amount", 0), op.get("currency", "AED"))
        expected_payments += amount

        phone = op.get("phone")
        contact = contacts_by_phone.get(phone, {})

        expected_detail.append({
            "expected_date": op.get("date"),
            "amount_aed": float(amount.quantize(Decimal("0.01"))),
            "customer": contact.get("name", phone),
            "type": op.get("type"),
            "status": op.get("status")
        })

    # Прогноз cash flow на месяц
    # Используем среднее за последние 30 дней
    last_30_days_inflow = Decimal("0")
    cutoff = today - timedelta(days=30)

    for day_key, amount in inflows_by_day.items():
        day_date = parse_date(day_key)
        if day_date and day_date.date() >= cutoff:
            last_30_days_inflow += amount

    avg_daily_inflow = last_30_days_inflow / 30 if last_30_days_inflow > 0 else Decimal("0")

    # Прогноз по неделям
    forecast = []
    for week_offset in range(4):
        week_start = today + timedelta(days=week_offset * 7)
        week_end = week_start + timedelta(days=6)

        # Базовый прогноз на основе среднего
        base_forecast = avg_daily_inflow * 7

        # Корректировка на сезонность (упрощённая)
        month = week_start.month
        seasonality = {
            1: 0.8, 2: 0.85, 3: 0.95, 4: 1.0,
            5: 0.9, 6: 0.7, 7: 0.6, 8: 0.65,
            9: 0.9, 10: 1.1, 11: 1.2, 12: 1.3
        }
        adjusted_forecast = base_forecast * Decimal(str(seasonality.get(month, 1.0)))

        # Добавляем ожидаемые платежи за эту неделю
        expected_this_week = Decimal("0")
        for op in pending_ops:
            op_date = parse_date(op.get("date"))
            if op_date and week_start <= op_date.date() <= week_end:
                expected_this_week += to_aed(op.get("amount", 0), op.get("currency", "AED"))

        forecast.append({
            "week": f"{week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}",
            "forecasted_inflow_aed": float((adjusted_forecast + expected_this_week).quantize(Decimal("0.01"))),
            "expected_payments_aed": float(expected_this_week.quantize(Decimal("0.01"))),
            "confidence": "high" if expected_this_week > 0 else "medium"
        })

    # Итоги за последние 7 и 30 дней
    last_7_days = Decimal("0")
    cutoff_7 = today - timedelta(days=7)

    for day_key, amount in inflows_by_day.items():
        day_date = parse_date(day_key)
        if day_date and day_date.date() >= cutoff_7:
            last_7_days += amount

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_inflows_last_30d_aed": float(last_30_days_inflow.quantize(Decimal("0.01"))),
            "total_inflows_last_7d_aed": float(last_7_days.quantize(Decimal("0.01"))),
            "avg_daily_inflow_aed": float(avg_daily_inflow.quantize(Decimal("0.01"))),
            "total_receivables_aed": float(total_receivables.quantize(Decimal("0.01"))),
            "expected_payments_aed": float(expected_payments.quantize(Decimal("0.01"))),
            "net_position_aed": float((last_30_days_inflow + expected_payments - total_receivables).quantize(Decimal("0.01")))
        },
        "inflows_by_day": {
            k: float(v.quantize(Decimal("0.01")))
            for k, v in sorted(inflows_by_day.items(), reverse=True)[:30]
        },
        "inflows_by_week": {
            k: float(v.quantize(Decimal("0.01")))
            for k, v in sorted(inflows_by_week.items(), reverse=True)[:12]
        },
        "receivables": {
            "total_aed": float(total_receivables.quantize(Decimal("0.01"))),
            "count": len(receivables_detail),
            "detail": sorted(receivables_detail, key=lambda x: x.get("days_overdue", 0), reverse=True)[:20]
        },
        "expected_payments": {
            "total_aed": float(expected_payments.quantize(Decimal("0.01"))),
            "count": len(expected_detail),
            "detail": sorted(expected_detail, key=lambda x: x.get("expected_date", ""))[:20]
        },
        "forecast": forecast
    }


# ═══════════════════════════════════════════════════════════════
# UNIT ECONOMICS
# ═══════════════════════════════════════════════════════════════

def calculate_unit_economics(operations: list, contacts: list) -> dict:
    """Расчёт Unit Economics."""

    # Только клиенты (не агенты, не поставщики)
    client_contacts = {
        c.get("phone"): c for c in contacts
        if c.get("type") == "клиенты" and c.get("phone")
    }

    # Фильтруем операции клиентов
    client_ops = [
        op for op in operations
        if op.get("phone") in client_contacts and op.get("status") == "completed"
    ]

    # Группировка по клиентам
    by_customer = defaultdict(list)
    for op in client_ops:
        by_customer[op.get("phone")].append(op)

    # Расчёт метрик
    total_revenue = Decimal("0")
    total_customers = len(by_customer)
    total_orders = len(client_ops)

    customer_ltv = []
    first_order_dates = []

    for phone, ops in by_customer.items():
        customer_revenue = sum(
            to_aed(op.get("amount", 0), op.get("currency", "AED"))
            for op in ops
        )
        total_revenue += customer_revenue
        customer_ltv.append(float(customer_revenue.quantize(Decimal("0.01"))))

        # Первый заказ
        dates = [parse_date(op.get("date")) for op in ops if parse_date(op.get("date"))]
        if dates:
            first_order_dates.append(min(dates))

    # Средний чек
    avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal("0")

    # LTV
    avg_ltv = total_revenue / total_customers if total_customers > 0 else Decimal("0")

    # CAC (предполагаем затраты на маркетинг)
    # Это упрощённая модель - в реальности нужны данные о затратах
    marketing_spend_estimate = total_revenue * Decimal("0.05")  # 5% от выручки
    cac = marketing_spend_estimate / total_customers if total_customers > 0 else Decimal("0")

    # LTV/CAC ratio
    ltv_cac_ratio = avg_ltv / cac if cac > 0 else Decimal("0")

    # Средний чек по категориям
    avg_by_category = {}
    for category in REVENUE_CATEGORIES:
        category_ops = [op for op in client_ops if categorize_operation(op) == category]
        if category_ops:
            category_revenue = sum(
                to_aed(op.get("amount", 0), op.get("currency", "AED"))
                for op in category_ops
            )
            avg_by_category[category] = {
                "name": REVENUE_CATEGORIES[category]["name"],
                "avg_order_aed": float((category_revenue / len(category_ops)).quantize(Decimal("0.01"))),
                "orders_count": len(category_ops),
                "total_revenue_aed": float(category_revenue.quantize(Decimal("0.01")))
            }

    # Маржинальность по продуктам
    margin_by_product = {}
    for category, info in REVENUE_CATEGORIES.items():
        category_ops = [op for op in client_ops if categorize_operation(op) == category]
        if category_ops:
            category_revenue = sum(
                to_aed(op.get("amount", 0), op.get("currency", "AED"))
                for op in category_ops
            )
            margin = info["margin"]
            gross_profit = category_revenue * Decimal(str(margin))

            margin_by_product[category] = {
                "name": info["name"],
                "revenue_aed": float(category_revenue.quantize(Decimal("0.01"))),
                "margin_percent": margin * 100,
                "gross_profit_aed": float(gross_profit.quantize(Decimal("0.01"))),
                "orders": len(category_ops)
            }

    # Конверсия (клиенты с >1 заказом)
    repeat_customers = len([c for c, ops in by_customer.items() if len(ops) > 1])
    repeat_rate = repeat_customers / total_customers * 100 if total_customers > 0 else 0

    # Частота заказов
    if first_order_dates:
        total_days = sum(
            (datetime.now() - d).days for d in first_order_dates
        )
        avg_customer_age_days = total_days / len(first_order_dates)
        orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
        orders_per_month = (orders_per_customer / avg_customer_age_days * 30) if avg_customer_age_days > 0 else 0
    else:
        avg_customer_age_days = 0
        orders_per_month = 0

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue_aed": float(total_revenue.quantize(Decimal("0.01"))),
            "avg_order_value_aed": float(avg_order_value.quantize(Decimal("0.01"))),
            "avg_ltv_aed": float(avg_ltv.quantize(Decimal("0.01"))),
            "estimated_cac_aed": float(cac.quantize(Decimal("0.01"))),
            "ltv_cac_ratio": float(ltv_cac_ratio.quantize(Decimal("0.01"))),
            "repeat_customer_rate_percent": round(repeat_rate, 2),
            "avg_orders_per_customer": round(total_orders / total_customers, 2) if total_customers > 0 else 0,
            "avg_orders_per_month": round(orders_per_month, 2)
        },
        "avg_order_by_category": avg_by_category,
        "margin_by_product": margin_by_product,
        "ltv_distribution": {
            "min": min(customer_ltv) if customer_ltv else 0,
            "max": max(customer_ltv) if customer_ltv else 0,
            "median": sorted(customer_ltv)[len(customer_ltv)//2] if customer_ltv else 0,
            "percentile_90": sorted(customer_ltv)[int(len(customer_ltv)*0.9)] if len(customer_ltv) > 10 else max(customer_ltv) if customer_ltv else 0
        },
        "benchmarks": {
            "target_ltv_cac_ratio": 3.0,
            "target_repeat_rate": 30.0,
            "target_avg_order_aed": 500,
            "status": "healthy" if ltv_cac_ratio >= 3 else "needs_improvement"
        }
    }


# ═══════════════════════════════════════════════════════════════
# АГЕНТСКИЕ ОТЧЁТЫ
# ═══════════════════════════════════════════════════════════════

def calculate_agent_report(operations: list, contacts: list) -> dict:
    """Расчёт агентского отчёта."""

    # Агенты
    agent_contacts = {
        c.get("phone"): c for c in contacts
        if c.get("type") == "агенты" and c.get("phone")
    }

    # Операции от агентов (клиенты, привлечённые агентами)
    agent_ops = defaultdict(list)

    for op in operations:
        if op.get("status") != "completed":
            continue

        # Определяем агента по referral или agent_phone
        agent_phone = op.get("agent_phone") or op.get("referral_phone")

        # Если нет явного агента, проверяем контакт
        if not agent_phone:
            phone = op.get("phone")
            contact = agent_contacts.get(phone)
            if contact:
                agent_phone = phone

        if agent_phone and agent_phone in agent_contacts:
            agent_ops[agent_phone].append(op)

    # Расчёт по каждому агенту
    agents_data = []
    total_agent_revenue = Decimal("0")
    total_commissions = Decimal("0")

    for agent_phone, ops in agent_ops.items():
        agent = agent_contacts.get(agent_phone, {})
        subtype = agent.get("subtype", "default")
        commission_rate = Decimal(str(
            AGENT_COMMISSION_RATES.get(subtype, AGENT_COMMISSION_RATES["default"])
        ))

        agent_revenue = sum(
            to_aed(op.get("amount", 0), op.get("currency", "AED"))
            for op in ops
        )
        commission = agent_revenue * commission_rate

        total_agent_revenue += agent_revenue
        total_commissions += commission

        # Группировка по месяцам
        by_month = defaultdict(lambda: {"revenue": Decimal("0"), "orders": 0})
        for op in ops:
            op_date = parse_date(op.get("date"))
            if op_date:
                month_key = op_date.strftime("%Y-%m")
                by_month[month_key]["revenue"] += to_aed(op.get("amount", 0), op.get("currency", "AED"))
                by_month[month_key]["orders"] += 1

        agents_data.append({
            "phone": agent_phone,
            "name": agent.get("name", agent_phone),
            "subtype": subtype,
            "commission_rate_percent": float(commission_rate * 100),
            "total_revenue_aed": float(agent_revenue.quantize(Decimal("0.01"))),
            "commission_due_aed": float(commission.quantize(Decimal("0.01"))),
            "orders_count": len(ops),
            "avg_order_aed": float((agent_revenue / len(ops)).quantize(Decimal("0.01"))) if ops else 0,
            "by_month": {
                k: {
                    "revenue_aed": float(v["revenue"].quantize(Decimal("0.01"))),
                    "orders": v["orders"]
                }
                for k, v in sorted(by_month.items(), reverse=True)[:6]
            }
        })

    # Сортировка по выручке
    agents_data.sort(key=lambda x: x["total_revenue_aed"], reverse=True)

    # Топ агенты
    top_agents = agents_data[:10]

    # Агенты с невыплаченными комиссиями
    unpaid_commissions = [
        a for a in agents_data
        if a["commission_due_aed"] > 0
    ]

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_agents": len(agents_data),
            "active_agents": len([a for a in agents_data if a["orders_count"] > 0]),
            "total_revenue_via_agents_aed": float(total_agent_revenue.quantize(Decimal("0.01"))),
            "total_commissions_due_aed": float(total_commissions.quantize(Decimal("0.01"))),
            "avg_commission_rate_percent": float(
                (total_commissions / total_agent_revenue * 100).quantize(Decimal("0.01"))
            ) if total_agent_revenue > 0 else 0
        },
        "top_agents": top_agents,
        "all_agents": agents_data,
        "commissions_to_pay": [
            {
                "agent_name": a["name"],
                "agent_phone": a["phone"],
                "amount_aed": a["commission_due_aed"]
            }
            for a in unpaid_commissions
        ],
        "by_subtype": {
            subtype: {
                "agents_count": len([a for a in agents_data if a["subtype"] == subtype]),
                "total_revenue_aed": sum(
                    a["total_revenue_aed"] for a in agents_data if a["subtype"] == subtype
                ),
                "total_commissions_aed": sum(
                    a["commission_due_aed"] for a in agents_data if a["subtype"] == subtype
                )
            }
            for subtype in set(a["subtype"] for a in agents_data)
        }
    }


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ MARKDOWN
# ═══════════════════════════════════════════════════════════════

def generate_pnl_markdown(pnl: dict) -> str:
    """Генерация Markdown для P&L."""
    md = []
    md.append("# P&L Отчёт (Profit & Loss)")
    md.append(f"\n*Период: {pnl.get('period', 'все время')}*")
    md.append(f"*Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Сводка
    summary = pnl.get("summary", {})
    md.append("## Финансовые результаты\n")
    md.append("| Показатель | Значение |")
    md.append("|------------|----------|")
    md.append(f"| Выручка | {summary.get('total_revenue_aed', 0):,.0f} AED |")
    md.append(f"| Себестоимость | {summary.get('total_cost_aed', 0):,.0f} AED |")
    md.append(f"| **Валовая прибыль** | **{summary.get('gross_profit_aed', 0):,.0f} AED** |")
    md.append(f"| Комиссии агентам | {summary.get('agent_commissions_aed', 0):,.0f} AED |")
    md.append(f"| **Чистая прибыль** | **{summary.get('net_profit_aed', 0):,.0f} AED** |")
    md.append(f"| Валовая маржа | {summary.get('gross_margin_percent', 0):.1f}% |")
    md.append(f"| Чистая маржа | {summary.get('net_margin_percent', 0):.1f}% |")
    md.append(f"| Всего заказов | {summary.get('total_orders', 0)} |")
    md.append("")

    # Сравнение
    comparison = pnl.get("comparison", {})
    if comparison:
        md.append("## Сравнение периодов\n")
        if "mom_revenue_change" in comparison:
            change = comparison["mom_revenue_change"]
            arrow = "+" if change > 0 else ""
            md.append(f"- **MoM выручка:** {arrow}{change:.1f}%")
        if "mom_profit_change" in comparison:
            change = comparison["mom_profit_change"]
            arrow = "+" if change > 0 else ""
            md.append(f"- **MoM прибыль:** {arrow}{change:.1f}%")
        if "yoy_revenue_change" in comparison:
            change = comparison["yoy_revenue_change"]
            arrow = "+" if change > 0 else ""
            md.append(f"- **YoY выручка:** {arrow}{change:.1f}%")
        md.append("")

    # По категориям
    by_category = pnl.get("by_category", {})
    md.append("## Выручка по категориям\n")
    md.append("| Категория | Выручка | Прибыль | Маржа | Доля |")
    md.append("|-----------|---------|---------|-------|------|")

    for cat_key, cat_data in sorted(by_category.items(),
                                     key=lambda x: x[1].get("revenue_aed", 0),
                                     reverse=True):
        if cat_data.get("revenue_aed", 0) > 0:
            md.append(
                f"| {cat_data.get('name', cat_key)} | "
                f"{cat_data.get('revenue_aed', 0):,.0f} | "
                f"{cat_data.get('profit_aed', 0):,.0f} | "
                f"{cat_data.get('margin_percent', 0):.0f}% | "
                f"{cat_data.get('share_percent', 0):.1f}% |"
            )
    md.append("")

    # По периодам
    by_period = pnl.get("by_period", {})
    if by_period:
        md.append("## Динамика по месяцам\n")
        md.append("| Период | Выручка | Прибыль | Заказы |")
        md.append("|--------|---------|---------|--------|")

        for period, data in list(by_period.items())[:6]:
            md.append(
                f"| {period} | "
                f"{data.get('revenue_aed', 0):,.0f} | "
                f"{data.get('net_profit_aed', 0):,.0f} | "
                f"{data.get('orders_count', 0)} |"
            )
        md.append("")

    return "\n".join(md)


def generate_cashflow_markdown(cashflow: dict) -> str:
    """Генерация Markdown для Cash Flow."""
    md = []
    md.append("# Cash Flow Отчёт")
    md.append(f"\n*Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Сводка
    summary = cashflow.get("summary", {})
    md.append("## Текущая позиция\n")
    md.append("| Показатель | Значение |")
    md.append("|------------|----------|")
    md.append(f"| Поступления за 30 дней | {summary.get('total_inflows_last_30d_aed', 0):,.0f} AED |")
    md.append(f"| Поступления за 7 дней | {summary.get('total_inflows_last_7d_aed', 0):,.0f} AED |")
    md.append(f"| Среднее в день | {summary.get('avg_daily_inflow_aed', 0):,.0f} AED |")
    md.append(f"| Дебиторская задолженность | {summary.get('total_receivables_aed', 0):,.0f} AED |")
    md.append(f"| Ожидаемые платежи | {summary.get('expected_payments_aed', 0):,.0f} AED |")
    md.append(f"| **Нетто позиция** | **{summary.get('net_position_aed', 0):,.0f} AED** |")
    md.append("")

    # Прогноз
    forecast = cashflow.get("forecast", [])
    if forecast:
        md.append("## Прогноз на 4 недели\n")
        md.append("| Неделя | Прогноз поступлений | Ожидаемые платежи | Уверенность |")
        md.append("|--------|---------------------|-------------------|-------------|")

        for week in forecast:
            md.append(
                f"| {week.get('week', '')} | "
                f"{week.get('forecasted_inflow_aed', 0):,.0f} | "
                f"{week.get('expected_payments_aed', 0):,.0f} | "
                f"{week.get('confidence', 'medium')} |"
            )
        md.append("")

    # Дебиторка
    receivables = cashflow.get("receivables", {})
    if receivables.get("count", 0) > 0:
        md.append("## Дебиторская задолженность\n")
        md.append(f"**Всего:** {receivables.get('total_aed', 0):,.0f} AED ({receivables.get('count', 0)} позиций)\n")
        md.append("| Клиент | Сумма | Просрочка (дней) |")
        md.append("|--------|-------|------------------|")

        for item in receivables.get("detail", [])[:10]:
            md.append(
                f"| {item.get('customer', '')[:30]} | "
                f"{item.get('amount_aed', 0):,.0f} | "
                f"{item.get('days_overdue', 0)} |"
            )
        md.append("")

    return "\n".join(md)


def generate_unit_economics_markdown(unit: dict) -> str:
    """Генерация Markdown для Unit Economics."""
    md = []
    md.append("# Unit Economics Отчёт")
    md.append(f"\n*Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Сводка
    summary = unit.get("summary", {})
    md.append("## Ключевые метрики\n")
    md.append("| Метрика | Значение | Цель |")
    md.append("|---------|----------|------|")

    ltv_cac = summary.get("ltv_cac_ratio", 0)
    ltv_cac_status = "OK" if ltv_cac >= 3 else "LOW"
    md.append(f"| LTV/CAC Ratio | {ltv_cac:.2f} | >= 3.0 ({ltv_cac_status}) |")
    md.append(f"| Средний LTV | {summary.get('avg_ltv_aed', 0):,.0f} AED | - |")
    md.append(f"| Оценка CAC | {summary.get('estimated_cac_aed', 0):,.0f} AED | - |")
    md.append(f"| Средний чек | {summary.get('avg_order_value_aed', 0):,.0f} AED | >= 500 |")
    md.append(f"| Repeat Rate | {summary.get('repeat_customer_rate_percent', 0):.1f}% | >= 30% |")
    md.append(f"| Заказов на клиента | {summary.get('avg_orders_per_customer', 0):.1f} | - |")
    md.append("")

    # По категориям
    by_category = unit.get("avg_order_by_category", {})
    if by_category:
        md.append("## Средний чек по категориям\n")
        md.append("| Категория | Средний чек | Заказов | Выручка |")
        md.append("|-----------|-------------|---------|---------|")

        for cat_key, cat_data in sorted(by_category.items(),
                                         key=lambda x: x[1].get("total_revenue_aed", 0),
                                         reverse=True):
            md.append(
                f"| {cat_data.get('name', cat_key)} | "
                f"{cat_data.get('avg_order_aed', 0):,.0f} | "
                f"{cat_data.get('orders_count', 0)} | "
                f"{cat_data.get('total_revenue_aed', 0):,.0f} |"
            )
        md.append("")

    # Маржинальность
    margins = unit.get("margin_by_product", {})
    if margins:
        md.append("## Маржинальность по продуктам\n")
        md.append("| Продукт | Выручка | Маржа | Валовая прибыль |")
        md.append("|---------|---------|-------|-----------------|")

        for prod_key, prod_data in sorted(margins.items(),
                                           key=lambda x: x[1].get("gross_profit_aed", 0),
                                           reverse=True):
            md.append(
                f"| {prod_data.get('name', prod_key)} | "
                f"{prod_data.get('revenue_aed', 0):,.0f} | "
                f"{prod_data.get('margin_percent', 0):.0f}% | "
                f"{prod_data.get('gross_profit_aed', 0):,.0f} |"
            )
        md.append("")

    # Рекомендации
    benchmarks = unit.get("benchmarks", {})
    md.append("## Рекомендации\n")

    if ltv_cac < 3:
        md.append("- **ВНИМАНИЕ:** LTV/CAC ниже целевого. Рекомендуется снизить затраты на привлечение или увеличить LTV.")

    if summary.get("repeat_customer_rate_percent", 0) < 30:
        md.append("- Низкий Repeat Rate. Рекомендуется внедрить программу лояльности.")

    if summary.get("avg_order_value_aed", 0) < 500:
        md.append("- Средний чек ниже целевого. Рекомендуется upsell и cross-sell.")

    md.append("")

    return "\n".join(md)


def generate_agents_markdown(agents: dict) -> str:
    """Генерация Markdown для агентского отчёта."""
    md = []
    md.append("# Агентский отчёт")
    md.append(f"\n*Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Сводка
    summary = agents.get("summary", {})
    md.append("## Сводка\n")
    md.append("| Показатель | Значение |")
    md.append("|------------|----------|")
    md.append(f"| Всего агентов | {summary.get('total_agents', 0)} |")
    md.append(f"| Активных агентов | {summary.get('active_agents', 0)} |")
    md.append(f"| Выручка через агентов | {summary.get('total_revenue_via_agents_aed', 0):,.0f} AED |")
    md.append(f"| Комиссии к выплате | {summary.get('total_commissions_due_aed', 0):,.0f} AED |")
    md.append(f"| Средняя ставка комиссии | {summary.get('avg_commission_rate_percent', 0):.1f}% |")
    md.append("")

    # Топ агенты
    top_agents = agents.get("top_agents", [])
    if top_agents:
        md.append("## Топ-10 агентов по объёму\n")
        md.append("| # | Агент | Тип | Выручка | Комиссия | Заказов |")
        md.append("|---|-------|-----|---------|----------|---------|")

        for i, agent in enumerate(top_agents, 1):
            md.append(
                f"| {i} | {agent.get('name', '')[:25]} | "
                f"{agent.get('subtype', '')} | "
                f"{agent.get('total_revenue_aed', 0):,.0f} | "
                f"{agent.get('commission_due_aed', 0):,.0f} | "
                f"{agent.get('orders_count', 0)} |"
            )
        md.append("")

    # Комиссии к выплате
    commissions = agents.get("commissions_to_pay", [])
    if commissions:
        total_to_pay = sum(c.get("amount_aed", 0) for c in commissions)
        md.append(f"## Комиссии к выплате: {total_to_pay:,.0f} AED\n")
        md.append("| Агент | Телефон | Сумма |")
        md.append("|-------|---------|-------|")

        for comm in commissions[:20]:
            md.append(
                f"| {comm.get('agent_name', '')} | "
                f"{comm.get('agent_phone', '')} | "
                f"{comm.get('amount_aed', 0):,.0f} |"
            )
        md.append("")

    # По типам
    by_subtype = agents.get("by_subtype", {})
    if by_subtype:
        md.append("## Статистика по типам агентов\n")
        md.append("| Тип | Агентов | Выручка | Комиссии |")
        md.append("|-----|---------|---------|----------|")

        for subtype, data in by_subtype.items():
            md.append(
                f"| {subtype} | "
                f"{data.get('agents_count', 0)} | "
                f"{data.get('total_revenue_aed', 0):,.0f} | "
                f"{data.get('total_commissions_aed', 0):,.0f} |"
            )
        md.append("")

    return "\n".join(md)


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ PDF
# ═══════════════════════════════════════════════════════════════

def generate_pdf_report(report_data: dict, report_type: str, filepath: Path):
    """Генерация PDF отчёта."""
    if not REPORTLAB_AVAILABLE:
        print(f"[!] PDF генерация недоступна (reportlab не установлен)")
        return

    # Регистрация шрифта с поддержкой кириллицы
    font_registered = False
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]

    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                font_registered = True
                break
            except:
                continue

    if not font_registered:
        print("[!] Шрифт с кириллицей не найден, PDF может отображаться некорректно")

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
    if font_registered:
        styles.add(ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName='CustomFont',
            fontSize=18,
            textColor=HexColor(COLORS["primary"])
        ))
        styles.add(ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName='CustomFont',
            fontSize=14,
            textColor=HexColor(COLORS["secondary"])
        ))
        styles.add(ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName='CustomFont',
            fontSize=10
        ))
    else:
        styles.add(ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=HexColor(COLORS["primary"])
        ))
        styles.add(ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor(COLORS["secondary"])
        ))
        styles.add(ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10
        ))

    elements = []

    # Заголовок
    title_map = {
        "pnl": "P&L Report (Profit & Loss)",
        "cashflow": "Cash Flow Report",
        "unit": "Unit Economics Report",
        "agents": "Agent Performance Report"
    }

    elements.append(Paragraph(title_map.get(report_type, "Financial Report"), styles['CustomTitle']))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['CustomBody']))
    elements.append(Spacer(1, 10*mm))

    # Контент в зависимости от типа отчёта
    if report_type == "pnl":
        _add_pnl_pdf_content(elements, report_data, styles)
    elif report_type == "cashflow":
        _add_cashflow_pdf_content(elements, report_data, styles)
    elif report_type == "unit":
        _add_unit_pdf_content(elements, report_data, styles)
    elif report_type == "agents":
        _add_agents_pdf_content(elements, report_data, styles)

    # Генерация PDF
    filepath.parent.mkdir(parents=True, exist_ok=True)
    doc.build(elements)
    print(f"[+] PDF сохранён: {filepath}")


def _add_pnl_pdf_content(elements, data, styles):
    """Добавление контента P&L в PDF."""
    summary = data.get("summary", {})

    elements.append(Paragraph("Financial Summary", styles['CustomHeading']))
    elements.append(Spacer(1, 5*mm))

    table_data = [
        ["Metric", "Value (AED)"],
        ["Revenue", f"{summary.get('total_revenue_aed', 0):,.0f}"],
        ["Cost of Goods", f"{summary.get('total_cost_aed', 0):,.0f}"],
        ["Gross Profit", f"{summary.get('gross_profit_aed', 0):,.0f}"],
        ["Agent Commissions", f"{summary.get('agent_commissions_aed', 0):,.0f}"],
        ["Net Profit", f"{summary.get('net_profit_aed', 0):,.0f}"],
        ["Gross Margin", f"{summary.get('gross_margin_percent', 0):.1f}%"],
        ["Net Margin", f"{summary.get('net_margin_percent', 0):.1f}%"],
    ]

    table = Table(table_data, colWidths=[100*mm, 60*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLORS["light"])),
        ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10*mm))

    # Категории
    by_category = data.get("by_category", {})
    if by_category:
        elements.append(Paragraph("Revenue by Category", styles['CustomHeading']))
        elements.append(Spacer(1, 5*mm))

        cat_data = [["Category", "Revenue", "Profit", "Margin", "Share"]]
        for cat_key, cat_info in sorted(by_category.items(),
                                         key=lambda x: x[1].get("revenue_aed", 0),
                                         reverse=True):
            if cat_info.get("revenue_aed", 0) > 0:
                cat_data.append([
                    cat_info.get("name", cat_key),
                    f"{cat_info.get('revenue_aed', 0):,.0f}",
                    f"{cat_info.get('profit_aed', 0):,.0f}",
                    f"{cat_info.get('margin_percent', 0):.0f}%",
                    f"{cat_info.get('share_percent', 0):.1f}%"
                ])

        if len(cat_data) > 1:
            table = Table(cat_data, colWidths=[50*mm, 35*mm, 35*mm, 25*mm, 25*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["secondary"])),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
            ]))
            elements.append(table)


def _add_cashflow_pdf_content(elements, data, styles):
    """Добавление контента Cash Flow в PDF."""
    summary = data.get("summary", {})

    elements.append(Paragraph("Cash Position", styles['CustomHeading']))
    elements.append(Spacer(1, 5*mm))

    table_data = [
        ["Metric", "Value (AED)"],
        ["Inflows (30 days)", f"{summary.get('total_inflows_last_30d_aed', 0):,.0f}"],
        ["Inflows (7 days)", f"{summary.get('total_inflows_last_7d_aed', 0):,.0f}"],
        ["Daily Average", f"{summary.get('avg_daily_inflow_aed', 0):,.0f}"],
        ["Receivables", f"{summary.get('total_receivables_aed', 0):,.0f}"],
        ["Expected Payments", f"{summary.get('expected_payments_aed', 0):,.0f}"],
        ["Net Position", f"{summary.get('net_position_aed', 0):,.0f}"],
    ]

    table = Table(table_data, colWidths=[100*mm, 60*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
    ]))
    elements.append(table)


def _add_unit_pdf_content(elements, data, styles):
    """Добавление контента Unit Economics в PDF."""
    summary = data.get("summary", {})

    elements.append(Paragraph("Key Metrics", styles['CustomHeading']))
    elements.append(Spacer(1, 5*mm))

    ltv_cac = summary.get("ltv_cac_ratio", 0)
    status = "OK" if ltv_cac >= 3 else "LOW"

    table_data = [
        ["Metric", "Value", "Target"],
        ["LTV/CAC Ratio", f"{ltv_cac:.2f}", f">= 3.0 ({status})"],
        ["Average LTV", f"{summary.get('avg_ltv_aed', 0):,.0f} AED", "-"],
        ["Estimated CAC", f"{summary.get('estimated_cac_aed', 0):,.0f} AED", "-"],
        ["Average Order", f"{summary.get('avg_order_value_aed', 0):,.0f} AED", ">= 500"],
        ["Repeat Rate", f"{summary.get('repeat_customer_rate_percent', 0):.1f}%", ">= 30%"],
    ]

    table = Table(table_data, colWidths=[60*mm, 50*mm, 50*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
    ]))
    elements.append(table)


def _add_agents_pdf_content(elements, data, styles):
    """Добавление контента агентского отчёта в PDF."""
    summary = data.get("summary", {})

    elements.append(Paragraph("Summary", styles['CustomHeading']))
    elements.append(Spacer(1, 5*mm))

    table_data = [
        ["Metric", "Value"],
        ["Total Agents", str(summary.get('total_agents', 0))],
        ["Active Agents", str(summary.get('active_agents', 0))],
        ["Revenue via Agents", f"{summary.get('total_revenue_via_agents_aed', 0):,.0f} AED"],
        ["Commissions Due", f"{summary.get('total_commissions_due_aed', 0):,.0f} AED"],
        ["Avg Commission Rate", f"{summary.get('avg_commission_rate_percent', 0):.1f}%"],
    ]

    table = Table(table_data, colWidths=[100*mm, 60*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
    ]))
    elements.append(table)

    # Топ агенты
    top_agents = data.get("top_agents", [])
    if top_agents:
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph("Top Agents", styles['CustomHeading']))
        elements.append(Spacer(1, 5*mm))

        agent_data = [["#", "Agent", "Revenue", "Commission", "Orders"]]
        for i, agent in enumerate(top_agents[:10], 1):
            agent_data.append([
                str(i),
                agent.get("name", "")[:20],
                f"{agent.get('total_revenue_aed', 0):,.0f}",
                f"{agent.get('commission_due_aed', 0):,.0f}",
                str(agent.get("orders_count", 0))
            ])

        table = Table(agent_data, colWidths=[10*mm, 60*mm, 35*mm, 35*mm, 25*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["secondary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["muted"])),
        ]))
        elements.append(table)


# ═══════════════════════════════════════════════════════════════
# ОСНОВНАЯ ЛОГИКА
# ═══════════════════════════════════════════════════════════════

def generate_all_reports(operations: list, contacts: list,
                         period: str = None, formats: list = None) -> dict:
    """Генерация всех отчётов."""

    if formats is None:
        formats = ["json", "csv", "md"]

    reports = {}

    # Создаём директорию для отчётов
    report_dir = REPORTS_DIR / (period or "all_time")
    report_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Генерация отчётов за период: {period or 'все время'}")
    print(f"[*] Директория: {report_dir}")
    print(f"[*] Форматы: {', '.join(formats)}\n")

    # 1. P&L
    print("[*] Расчёт P&L...")
    pnl = calculate_pnl(operations, contacts, period)
    reports["pnl"] = pnl

    if "json" in formats:
        save_json(pnl, report_dir / "pnl.json")
    if "md" in formats:
        md_content = generate_pnl_markdown(pnl)
        (report_dir / "pnl.md").write_text(md_content, encoding="utf-8")
        print(f"[+] Markdown: {report_dir / 'pnl.md'}")
    if "csv" in formats:
        # CSV для категорий
        categories = [
            {"category": k, **v}
            for k, v in pnl.get("by_category", {}).items()
        ]
        save_csv(categories, report_dir / "pnl_categories.csv",
                 ["category", "name", "revenue_aed", "cost_aed", "profit_aed", "margin_percent", "share_percent"])
    if "pdf" in formats:
        generate_pdf_report(pnl, "pnl", report_dir / "pnl.pdf")

    # 2. Cash Flow
    print("[*] Расчёт Cash Flow...")
    cashflow = calculate_cashflow(operations, contacts)
    reports["cashflow"] = cashflow

    if "json" in formats:
        save_json(cashflow, report_dir / "cashflow.json")
    if "md" in formats:
        md_content = generate_cashflow_markdown(cashflow)
        (report_dir / "cashflow.md").write_text(md_content, encoding="utf-8")
        print(f"[+] Markdown: {report_dir / 'cashflow.md'}")
    if "csv" in formats:
        # CSV для прогноза
        save_csv(cashflow.get("forecast", []), report_dir / "cashflow_forecast.csv",
                 ["week", "forecasted_inflow_aed", "expected_payments_aed", "confidence"])
    if "pdf" in formats:
        generate_pdf_report(cashflow, "cashflow", report_dir / "cashflow.pdf")

    # 3. Unit Economics
    print("[*] Расчёт Unit Economics...")
    unit = calculate_unit_economics(operations, contacts)
    reports["unit_economics"] = unit

    if "json" in formats:
        save_json(unit, report_dir / "unit_economics.json")
    if "md" in formats:
        md_content = generate_unit_economics_markdown(unit)
        (report_dir / "unit_economics.md").write_text(md_content, encoding="utf-8")
        print(f"[+] Markdown: {report_dir / 'unit_economics.md'}")
    if "pdf" in formats:
        generate_pdf_report(unit, "unit", report_dir / "unit_economics.pdf")

    # 4. Агентский отчёт
    print("[*] Расчёт агентского отчёта...")
    agents = calculate_agent_report(operations, contacts)
    reports["agents"] = agents

    if "json" in formats:
        save_json(agents, report_dir / "agents.json")
    if "md" in formats:
        md_content = generate_agents_markdown(agents)
        (report_dir / "agents.md").write_text(md_content, encoding="utf-8")
        print(f"[+] Markdown: {report_dir / 'agents.md'}")
    if "csv" in formats:
        save_csv(agents.get("all_agents", []), report_dir / "agents.csv",
                 ["name", "phone", "subtype", "total_revenue_aed", "commission_due_aed",
                  "orders_count", "avg_order_aed", "commission_rate_percent"])
    if "pdf" in formats:
        generate_pdf_report(agents, "agents", report_dir / "agents.pdf")

    # Сводный отчёт
    summary = {
        "generated_at": datetime.now().isoformat(),
        "period": period or "all_time",
        "pnl_summary": pnl.get("summary"),
        "cashflow_summary": cashflow.get("summary"),
        "unit_economics_summary": unit.get("summary"),
        "agents_summary": agents.get("summary")
    }

    if "json" in formats:
        save_json(summary, report_dir / "summary.json")

    return reports


def main():
    parser = argparse.ArgumentParser(
        description="Финансовая отчётность для туристического бизнеса"
    )
    parser.add_argument(
        "--report", "-r",
        choices=["pnl", "cashflow", "unit", "agents", "all"],
        default="all",
        help="Тип отчёта (default: all)"
    )
    parser.add_argument(
        "--period", "-p",
        type=str,
        help="Период в формате YYYY-MM (например, 2024-01)"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Начальная дата (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="Конечная дата (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv", "md", "pdf", "all"],
        default="all",
        help="Формат вывода (default: all)"
    )
    parser.add_argument(
        "--compare-yoy",
        action="store_true",
        help="Сравнение год к году"
    )
    parser.add_argument(
        "--compare-mom",
        action="store_true",
        help="Сравнение месяц к месяцу"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="Директория для отчётов"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Минимальный вывод"
    )

    args = parser.parse_args()

    # Определяем форматы
    if args.format == "all":
        formats = ["json", "csv", "md"]
        if REPORTLAB_AVAILABLE:
            formats.append("pdf")
    else:
        formats = [args.format]

    # Загрузка данных
    print("[*] Загрузка данных...")
    operations = load_json(OPERATIONS_FILE)
    contacts = load_json(CONTACTS_FILE)

    if not operations:
        print("[!] Нет операций для анализа. Создайте файл operations.json")
        return

    print(f"[*] Загружено операций: {len(operations)}")
    print(f"[*] Загружено контактов: {len(contacts)}")

    # Изменяем директорию вывода если указана
    global REPORTS_DIR
    if args.output_dir:
        REPORTS_DIR = Path(args.output_dir)

    # Генерация отчётов
    if args.report == "all":
        generate_all_reports(operations, contacts, args.period, formats)
    else:
        # Отдельный отчёт
        report_dir = REPORTS_DIR / (args.period or "all_time")
        report_dir.mkdir(parents=True, exist_ok=True)

        if args.report == "pnl":
            pnl = calculate_pnl(operations, contacts, args.period)
            if "json" in formats:
                save_json(pnl, report_dir / "pnl.json")
            if "md" in formats:
                md = generate_pnl_markdown(pnl)
                (report_dir / "pnl.md").write_text(md, encoding="utf-8")
                print(f"[+] Markdown: {report_dir / 'pnl.md'}")
            if "pdf" in formats:
                generate_pdf_report(pnl, "pnl", report_dir / "pnl.pdf")

        elif args.report == "cashflow":
            cashflow = calculate_cashflow(operations, contacts)
            if "json" in formats:
                save_json(cashflow, report_dir / "cashflow.json")
            if "md" in formats:
                md = generate_cashflow_markdown(cashflow)
                (report_dir / "cashflow.md").write_text(md, encoding="utf-8")
                print(f"[+] Markdown: {report_dir / 'cashflow.md'}")
            if "pdf" in formats:
                generate_pdf_report(cashflow, "cashflow", report_dir / "cashflow.pdf")

        elif args.report == "unit":
            unit = calculate_unit_economics(operations, contacts)
            if "json" in formats:
                save_json(unit, report_dir / "unit_economics.json")
            if "md" in formats:
                md = generate_unit_economics_markdown(unit)
                (report_dir / "unit_economics.md").write_text(md, encoding="utf-8")
                print(f"[+] Markdown: {report_dir / 'unit_economics.md'}")
            if "pdf" in formats:
                generate_pdf_report(unit, "unit", report_dir / "unit_economics.pdf")

        elif args.report == "agents":
            agents = calculate_agent_report(operations, contacts)
            if "json" in formats:
                save_json(agents, report_dir / "agents.json")
            if "md" in formats:
                md = generate_agents_markdown(agents)
                (report_dir / "agents.md").write_text(md, encoding="utf-8")
                print(f"[+] Markdown: {report_dir / 'agents.md'}")
            if "pdf" in formats:
                generate_pdf_report(agents, "agents", report_dir / "agents.pdf")

    print("\n[+] Отчёты сгенерированы!")
    print(f"[+] Директория: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
