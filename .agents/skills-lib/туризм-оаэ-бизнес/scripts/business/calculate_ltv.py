#!/usr/bin/env python3
"""
calculate_ltv.py - Расчёт LTV (Lifetime Value) клиентов

Анализирует операции клиентов и рассчитывает:
- Исторический LTV (сумма всех покупок)
- Средний чек
- Частота покупок
- Срок жизни клиента
- Прогнозный LTV
- Сегментация (VIP/Regular/One-time/Churned)

Использование:
    python calculate_ltv.py                    # Полный анализ
    python calculate_ltv.py --update-contacts  # Обновить contacts.json с LTV
    python calculate_ltv.py --segment VIP      # Показать только VIP
    python calculate_ltv.py --top 20           # Показать топ-20 по LTV
    python calculate_ltv.py --export-csv       # Экспорт в CSV
"""

import json
import argparse
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import statistics
import csv

# === КОНФИГУРАЦИЯ ===

BASE_DIR = Path("D:/Downloads/Chats/_база")
JSON_DIR = BASE_DIR / "json"
MD_DIR = BASE_DIR / "md"

# Входные файлы
CONTACTS_FILE = JSON_DIR / "contacts.json"
OPERATIONS_FILE = JSON_DIR / "operations.json"
PROFILES_FILE = JSON_DIR / "profiles.json"

# Выходные файлы
LTV_OUTPUT_FILE = JSON_DIR / "ltv_analysis.json"
LTV_MD_FILE = MD_DIR / "ltv_клиентов.md"

# Параметры сегментации
SEGMENT_THRESHOLDS = {
    "VIP": {"min_ltv": 10000, "min_orders": 5},
    "Regular": {"min_ltv": 1000, "max_ltv": 10000, "min_orders": 2, "max_orders": 5},
    "One-time": {"max_orders": 1},
    "Churned": {"days_inactive": 180}
}

# Параметры churn risk
CHURN_RISK_THRESHOLDS = {
    "high": 90,   # >90 дней без заказов
    "medium": 30, # 30-90 дней
    "low": 0      # <30 дней
}

# Текущая дата для расчётов
TODAY = datetime.now().date()


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
    print(f"[+] Сохранено: {filepath}")


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


def get_quarter(date: datetime) -> str:
    """Получить квартал из даты."""
    quarter = (date.month - 1) // 3 + 1
    return f"{date.year}-Q{quarter}"


def calculate_customer_ltv(phone: str, operations: list, contact_info: dict, profile_info: dict) -> dict:
    """Расчёт LTV для одного клиента."""

    # Фильтруем операции клиента (только completed)
    customer_ops = [
        op for op in operations
        if op.get("phone") == phone and op.get("status") == "completed"
    ]

    if not customer_ops:
        return None

    # Сортируем по дате
    customer_ops.sort(key=lambda x: x.get("date", ""))

    # Суммируем по валюте (конвертируем в AED если нужно)
    total_amount_aed = 0
    conversion_rates = {"AED": 1, "USD": 3.67, "RUB": 0.038, "EUR": 4.0}

    order_dates = []
    for op in customer_ops:
        amount = op.get("amount", 0)
        currency = op.get("currency", "AED")
        rate = conversion_rates.get(currency, 1)
        total_amount_aed += amount * rate

        date = parse_date(op.get("date"))
        if date:
            order_dates.append(date)

    orders_count = len(customer_ops)
    avg_order_value = total_amount_aed / orders_count if orders_count > 0 else 0

    # Даты
    first_order_date = min(order_dates) if order_dates else None
    last_order_date = max(order_dates) if order_dates else None

    # Срок жизни
    if first_order_date and last_order_date:
        lifetime_days = (last_order_date.date() - first_order_date.date()).days
        if lifetime_days == 0:
            lifetime_days = 1  # Минимум 1 день
    else:
        lifetime_days = 0

    # Дней с последнего заказа
    if last_order_date:
        days_since_last = (TODAY - last_order_date.date()).days
    else:
        days_since_last = 9999

    # Частота покупок (заказов в год)
    if lifetime_days > 0 and orders_count > 1:
        orders_per_year = (orders_count / lifetime_days) * 365
    elif orders_count == 1:
        orders_per_year = 1.0
    else:
        orders_per_year = 0

    # Сегментация
    segment = determine_segment(total_amount_aed, orders_count, days_since_last)

    # Churn risk
    churn_risk = determine_churn_risk(days_since_last)

    # Прогнозный LTV на следующий год
    predicted_ltv = calculate_predicted_ltv(
        total_amount_aed, orders_count, lifetime_days,
        orders_per_year, avg_order_value, segment
    )

    # Генерируем или используем существующий ID
    contact_id = contact_info.get("id") or str(uuid.uuid4())

    return {
        "contact_id": contact_id,
        "jid": contact_info.get("jid", f"{phone.replace('+', '')}@s.whatsapp.net"),
        "phone": phone,
        "name": contact_info.get("name", phone),
        "type": contact_info.get("type", "клиент"),
        "historical_ltv_aed": round(total_amount_aed, 2),
        "orders_count": orders_count,
        "avg_order_value": round(avg_order_value, 2),
        "first_order_date": first_order_date.strftime("%Y-%m-%d") if first_order_date else None,
        "last_order_date": last_order_date.strftime("%Y-%m-%d") if last_order_date else None,
        "lifetime_days": lifetime_days,
        "orders_per_year": round(orders_per_year, 2),
        "predicted_ltv_next_year": round(predicted_ltv, 2),
        "segment": segment,
        "churn_risk": churn_risk,
        "days_since_last_order": days_since_last,
        # Дополнительные данные из профиля
        "budget_category": profile_info.get("budget_category"),
        "price_sensitivity": profile_info.get("price_sensitivity"),
        "tour_types": profile_info.get("tour_types", [])
    }


def determine_segment(ltv: float, orders: int, days_inactive: int) -> str:
    """Определение сегмента клиента."""

    # Churned проверяем первым
    if days_inactive >= SEGMENT_THRESHOLDS["Churned"]["days_inactive"]:
        return "Churned"

    # VIP
    if ltv >= SEGMENT_THRESHOLDS["VIP"]["min_ltv"] or orders >= SEGMENT_THRESHOLDS["VIP"]["min_orders"]:
        return "VIP"

    # Regular
    if (orders >= SEGMENT_THRESHOLDS["Regular"]["min_orders"] and
        SEGMENT_THRESHOLDS["Regular"]["min_ltv"] <= ltv <= SEGMENT_THRESHOLDS["Regular"]["max_ltv"]):
        return "Regular"

    # One-time
    if orders <= SEGMENT_THRESHOLDS["One-time"]["max_orders"]:
        return "One-time"

    # По умолчанию Regular
    return "Regular"


def determine_churn_risk(days_inactive: int) -> str:
    """Определение риска оттока."""
    if days_inactive > CHURN_RISK_THRESHOLDS["high"]:
        return "high"
    elif days_inactive > CHURN_RISK_THRESHOLDS["medium"]:
        return "medium"
    else:
        return "low"


def calculate_predicted_ltv(
    historical_ltv: float,
    orders_count: int,
    lifetime_days: int,
    orders_per_year: float,
    avg_order_value: float,
    segment: str
) -> float:
    """Прогноз LTV на следующий год."""

    if segment == "Churned":
        # Для ушедших клиентов - низкий прогноз с учётом возможного возврата
        return avg_order_value * 0.2

    if orders_count == 1:
        # Для одноразовых - 30% вероятность повторной покупки
        return avg_order_value * 0.3

    # Для активных клиентов - на основе частоты и среднего чека
    base_prediction = orders_per_year * avg_order_value

    # Корректировка по сегменту
    if segment == "VIP":
        # VIP клиенты обычно увеличивают расходы
        return base_prediction * 1.1
    elif segment == "Regular":
        # Стабильные клиенты
        return base_prediction * 0.9

    return base_prediction


def calculate_segments_summary(ltv_data: list) -> dict:
    """Расчёт сводки по сегментам."""
    segments = defaultdict(lambda: {"count": 0, "total_ltv": 0, "customers": []})

    for customer in ltv_data:
        segment = customer["segment"]
        segments[segment]["count"] += 1
        segments[segment]["total_ltv"] += customer["historical_ltv_aed"]
        segments[segment]["customers"].append(customer["name"])

    # Расчёт средних
    summary = {}
    for segment, data in segments.items():
        summary[segment] = {
            "count": data["count"],
            "total_ltv": round(data["total_ltv"], 2),
            "avg_ltv": round(data["total_ltv"] / data["count"], 2) if data["count"] > 0 else 0
        }

    return summary


def calculate_overall_metrics(ltv_data: list) -> dict:
    """Расчёт общих метрик."""
    if not ltv_data:
        return {
            "total_revenue": 0,
            "total_customers": 0,
            "avg_ltv": 0,
            "median_ltv": 0,
            "top_10_percent_share": 0
        }

    ltv_values = [c["historical_ltv_aed"] for c in ltv_data]
    total_revenue = sum(ltv_values)

    # Топ 10%
    sorted_ltv = sorted(ltv_values, reverse=True)
    top_10_count = max(1, len(sorted_ltv) // 10)
    top_10_revenue = sum(sorted_ltv[:top_10_count])

    return {
        "total_revenue": round(total_revenue, 2),
        "total_customers": len(ltv_data),
        "avg_ltv": round(statistics.mean(ltv_values), 2),
        "median_ltv": round(statistics.median(ltv_values), 2),
        "top_10_percent_share": round(top_10_revenue / total_revenue, 4) if total_revenue > 0 else 0,
        "max_ltv": round(max(ltv_values), 2),
        "min_ltv": round(min(ltv_values), 2),
        "total_orders": sum(c["orders_count"] for c in ltv_data)
    }


def calculate_cohorts(ltv_data: list, operations: list) -> dict:
    """Расчёт когорт по первой покупке."""
    cohorts = defaultdict(lambda: {
        "customers": 0,
        "phones": [],
        "ltv_total": 0,
        "orders_total": 0
    })

    for customer in ltv_data:
        first_date_str = customer.get("first_order_date")
        if not first_date_str:
            continue

        first_date = parse_date(first_date_str)
        if not first_date:
            continue

        quarter = get_quarter(first_date)
        cohorts[quarter]["customers"] += 1
        cohorts[quarter]["phones"].append(customer["phone"])
        cohorts[quarter]["ltv_total"] += customer["historical_ltv_aed"]
        cohorts[quarter]["orders_total"] += customer["orders_count"]

    # Расчёт LTV на 6 и 12 месяцев для каждой когорты
    result = {}
    for quarter, data in sorted(cohorts.items()):
        # Определяем границы квартала
        year, q = quarter.split("-Q")
        year = int(year)
        q = int(q)

        quarter_start = datetime(year, (q-1)*3 + 1, 1)
        quarter_end = datetime(year, q*3 if q < 4 else 12, 28)

        # 6 месяцев после начала когорты
        month_6 = quarter_start + timedelta(days=180)
        month_12 = quarter_start + timedelta(days=365)

        ltv_6m = 0
        ltv_12m = 0

        for phone in data["phones"]:
            customer_ops = [
                op for op in operations
                if op.get("phone") == phone and op.get("status") == "completed"
            ]

            for op in customer_ops:
                op_date = parse_date(op.get("date"))
                if not op_date:
                    continue

                amount = op.get("amount", 0)
                currency = op.get("currency", "AED")
                conversion_rates = {"AED": 1, "USD": 3.67, "RUB": 0.038, "EUR": 4.0}
                amount_aed = amount * conversion_rates.get(currency, 1)

                if op_date <= month_6:
                    ltv_6m += amount_aed
                if op_date <= month_12:
                    ltv_12m += amount_aed

        result[quarter] = {
            "customers": data["customers"],
            "avg_ltv": round(data["ltv_total"] / data["customers"], 2) if data["customers"] > 0 else 0,
            "ltv_6m": round(ltv_6m / data["customers"], 2) if data["customers"] > 0 else 0,
            "ltv_12m": round(ltv_12m / data["customers"], 2) if data["customers"] > 0 else 0,
            "avg_orders": round(data["orders_total"] / data["customers"], 2) if data["customers"] > 0 else 0
        }

    return result


def generate_markdown_report(analysis: dict) -> str:
    """Генерация Markdown отчёта."""
    md = []
    md.append("# LTV Анализ клиентов")
    md.append(f"\n*Дата отчёта: {TODAY.strftime('%Y-%m-%d')}*\n")

    # Общие метрики
    overall = analysis.get("overall", {})
    md.append("## Общие показатели\n")
    md.append(f"| Метрика | Значение |")
    md.append(f"|---------|----------|")
    md.append(f"| Всего клиентов | {overall.get('total_customers', 0)} |")
    md.append(f"| Общая выручка | {overall.get('total_revenue', 0):,.0f} AED |")
    md.append(f"| Средний LTV | {overall.get('avg_ltv', 0):,.0f} AED |")
    md.append(f"| Медианный LTV | {overall.get('median_ltv', 0):,.0f} AED |")
    md.append(f"| Макс. LTV | {overall.get('max_ltv', 0):,.0f} AED |")
    md.append(f"| Доля топ 10% | {overall.get('top_10_percent_share', 0)*100:.1f}% |")
    md.append(f"| Всего заказов | {overall.get('total_orders', 0)} |")
    md.append("")

    # Сегменты
    segments = analysis.get("segments", {})
    md.append("## Сегментация клиентов\n")
    md.append("| Сегмент | Клиентов | Общий LTV | Средний LTV |")
    md.append("|---------|----------|-----------|-------------|")

    segment_order = ["VIP", "Regular", "One-time", "Churned"]
    for seg in segment_order:
        if seg in segments:
            data = segments[seg]
            md.append(f"| {seg} | {data['count']} | {data['total_ltv']:,.0f} AED | {data['avg_ltv']:,.0f} AED |")
    md.append("")

    # Когорты
    cohorts = analysis.get("cohorts", {})
    if cohorts:
        md.append("## Когортный анализ\n")
        md.append("| Когорта | Клиентов | Ср. заказов | LTV 6м | LTV 12м |")
        md.append("|---------|----------|-------------|--------|---------|")

        for quarter, data in sorted(cohorts.items(), reverse=True):
            md.append(f"| {quarter} | {data['customers']} | {data['avg_orders']:.1f} | {data['ltv_6m']:,.0f} | {data['ltv_12m']:,.0f} |")
        md.append("")

    # Топ-20 клиентов
    ltv_by_contact = analysis.get("ltv_by_contact", [])
    if ltv_by_contact:
        md.append("## Топ-20 клиентов по LTV\n")
        md.append("| # | Имя | Тип | LTV | Заказов | Сегмент | Риск оттока |")
        md.append("|---|-----|-----|-----|---------|---------|-------------|")

        sorted_customers = sorted(ltv_by_contact, key=lambda x: x["historical_ltv_aed"], reverse=True)
        for i, c in enumerate(sorted_customers[:20], 1):
            risk_emoji = {"low": "low", "medium": "MEDIUM", "high": "HIGH"}
            md.append(f"| {i} | {c['name'][:30]} | {c['type']} | {c['historical_ltv_aed']:,.0f} | {c['orders_count']} | {c['segment']} | {risk_emoji.get(c['churn_risk'], c['churn_risk'])} |")
        md.append("")

    # Клиенты с высоким риском оттока
    high_risk = [c for c in ltv_by_contact if c["churn_risk"] == "high" and c["segment"] != "Churned"]
    if high_risk:
        md.append("## Клиенты с высоким риском оттока\n")
        md.append("*Активные клиенты без заказов >90 дней*\n")
        md.append("| Имя | LTV | Последний заказ | Дней неактивен |")
        md.append("|-----|-----|-----------------|----------------|")

        for c in sorted(high_risk, key=lambda x: x["historical_ltv_aed"], reverse=True)[:10]:
            md.append(f"| {c['name'][:30]} | {c['historical_ltv_aed']:,.0f} | {c['last_order_date']} | {c['days_since_last_order']} |")
        md.append("")

    # Рекомендации
    md.append("## Рекомендации\n")

    vip_count = segments.get("VIP", {}).get("count", 0)
    churned_count = segments.get("Churned", {}).get("count", 0)
    one_time_count = segments.get("One-time", {}).get("count", 0)

    md.append(f"1. **VIP клиенты ({vip_count})**: Персональные предложения и эксклюзивные услуги")
    md.append(f"2. **Риск оттока ({len(high_risk)})**: Срочно связаться с предложением/скидкой")
    md.append(f"3. **Ушедшие ({churned_count})**: Реактивационная кампания с спецпредложением")
    md.append(f"4. **Одноразовые ({one_time_count})**: Программа лояльности для повторных покупок")
    md.append("")

    return "\n".join(md)


def update_contacts_with_ltv(contacts: list, ltv_data: list) -> list:
    """Обновление contacts.json данными LTV."""

    # Создаём словарь LTV по телефону
    ltv_by_phone = {c["phone"]: c for c in ltv_data}

    updated_contacts = []
    for contact in contacts:
        phone = contact.get("phone")
        if phone and phone in ltv_by_phone:
            ltv = ltv_by_phone[phone]
            contact["ltv"] = {
                "historical_ltv_aed": ltv["historical_ltv_aed"],
                "orders_count": ltv["orders_count"],
                "avg_order_value": ltv["avg_order_value"],
                "segment": ltv["segment"],
                "churn_risk": ltv["churn_risk"],
                "predicted_ltv_next_year": ltv["predicted_ltv_next_year"],
                "last_order_date": ltv["last_order_date"],
                "days_since_last_order": ltv["days_since_last_order"]
            }
        updated_contacts.append(contact)

    return updated_contacts


def export_to_csv(ltv_data: list, filepath: Path):
    """Экспорт в CSV."""
    if not ltv_data:
        print("[!] Нет данных для экспорта")
        return

    fieldnames = [
        "name", "phone", "type", "segment", "historical_ltv_aed",
        "orders_count", "avg_order_value", "first_order_date",
        "last_order_date", "lifetime_days", "orders_per_year",
        "predicted_ltv_next_year", "churn_risk", "days_since_last_order"
    ]

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(ltv_data)

    print(f"[+] CSV экспортирован: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Расчёт LTV клиентов")
    parser.add_argument("--update-contacts", action="store_true",
                        help="Обновить contacts.json с данными LTV")
    parser.add_argument("--segment", type=str, choices=["VIP", "Regular", "One-time", "Churned"],
                        help="Показать только указанный сегмент")
    parser.add_argument("--top", type=int, default=0,
                        help="Показать топ N клиентов по LTV")
    parser.add_argument("--export-csv", action="store_true",
                        help="Экспортировать в CSV")
    parser.add_argument("--min-ltv", type=float, default=0,
                        help="Минимальный LTV для вывода")
    parser.add_argument("--churn-risk", type=str, choices=["low", "medium", "high"],
                        help="Фильтр по риску оттока")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Минимальный вывод")

    args = parser.parse_args()

    # Загрузка данных
    print("[*] Загрузка данных...")
    contacts = load_json(CONTACTS_FILE)
    operations = load_json(OPERATIONS_FILE)
    profiles = load_json(PROFILES_FILE)

    if not operations:
        print("[!] Нет операций для анализа")
        return

    # Создаём словари для быстрого доступа
    contacts_by_phone = {c.get("phone"): c for c in contacts if c.get("phone")}
    profiles_by_phone = {p.get("phone"): p for p in profiles if p.get("phone")}

    # Получаем уникальные телефоны из операций
    unique_phones = set(op.get("phone") for op in operations if op.get("phone"))

    print(f"[*] Найдено {len(unique_phones)} уникальных клиентов с операциями")

    # Расчёт LTV для каждого клиента
    ltv_data = []
    for phone in unique_phones:
        contact_info = contacts_by_phone.get(phone, {})
        profile_info = profiles_by_phone.get(phone, {})

        ltv = calculate_customer_ltv(phone, operations, contact_info, profile_info)
        if ltv:
            ltv_data.append(ltv)

    print(f"[*] Рассчитан LTV для {len(ltv_data)} клиентов")

    # Применение фильтров
    filtered_data = ltv_data

    if args.segment:
        filtered_data = [c for c in filtered_data if c["segment"] == args.segment]
        print(f"[*] Фильтр по сегменту {args.segment}: {len(filtered_data)} клиентов")

    if args.min_ltv > 0:
        filtered_data = [c for c in filtered_data if c["historical_ltv_aed"] >= args.min_ltv]
        print(f"[*] Фильтр по минимальному LTV {args.min_ltv}: {len(filtered_data)} клиентов")

    if args.churn_risk:
        filtered_data = [c for c in filtered_data if c["churn_risk"] == args.churn_risk]
        print(f"[*] Фильтр по риску оттока {args.churn_risk}: {len(filtered_data)} клиентов")

    # Сортировка по LTV
    filtered_data.sort(key=lambda x: x["historical_ltv_aed"], reverse=True)

    if args.top > 0:
        filtered_data = filtered_data[:args.top]
        print(f"[*] Топ-{args.top} клиентов")

    # Расчёт сводных метрик (на полных данных)
    segments_summary = calculate_segments_summary(ltv_data)
    overall_metrics = calculate_overall_metrics(ltv_data)
    cohorts = calculate_cohorts(ltv_data, operations)

    # Формирование результата
    analysis = {
        "generated_at": datetime.now().isoformat(),
        "ltv_by_contact": filtered_data,
        "segments": segments_summary,
        "overall": overall_metrics,
        "cohorts": cohorts
    }

    # Сохранение JSON
    save_json(analysis, LTV_OUTPUT_FILE)

    # Генерация и сохранение Markdown
    md_report = generate_markdown_report(analysis)
    MD_DIR.mkdir(parents=True, exist_ok=True)
    with open(LTV_MD_FILE, 'w', encoding='utf-8') as f:
        f.write(md_report)
    print(f"[+] Markdown отчёт: {LTV_MD_FILE}")

    # Экспорт в CSV
    if args.export_csv:
        csv_file = JSON_DIR / "ltv_export.csv"
        export_to_csv(filtered_data, csv_file)

    # Обновление contacts.json
    if args.update_contacts:
        print("[*] Обновление contacts.json...")
        updated_contacts = update_contacts_with_ltv(contacts, ltv_data)

        # Бэкап
        backup_file = CONTACTS_FILE.with_suffix('.json.bak')
        if CONTACTS_FILE.exists():
            import shutil
            shutil.copy(CONTACTS_FILE, backup_file)
            print(f"[+] Бэкап: {backup_file}")

        save_json(updated_contacts, CONTACTS_FILE)
        print(f"[+] contacts.json обновлён с LTV данными")

    # Вывод результатов
    if not args.quiet:
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА LTV")
        print("="*60)

        print(f"\nОбщая выручка: {overall_metrics['total_revenue']:,.0f} AED")
        print(f"Всего клиентов: {overall_metrics['total_customers']}")
        print(f"Средний LTV: {overall_metrics['avg_ltv']:,.0f} AED")
        print(f"Медианный LTV: {overall_metrics['median_ltv']:,.0f} AED")
        print(f"Топ 10% генерируют: {overall_metrics['top_10_percent_share']*100:.1f}% выручки")

        print("\nСегменты:")
        for segment in ["VIP", "Regular", "One-time", "Churned"]:
            if segment in segments_summary:
                s = segments_summary[segment]
                print(f"  {segment}: {s['count']} клиентов, {s['total_ltv']:,.0f} AED ({s['avg_ltv']:,.0f} avg)")

        if filtered_data and args.top > 0:
            print(f"\nТоп-{min(args.top, len(filtered_data))} клиентов:")
            for i, c in enumerate(filtered_data[:args.top], 1):
                print(f"  {i}. {c['name']}: {c['historical_ltv_aed']:,.0f} AED ({c['orders_count']} заказов, {c['segment']})")

    print("\n[+] Анализ завершён!")


if __name__ == "__main__":
    main()
