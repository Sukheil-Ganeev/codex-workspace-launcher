#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repeat_customers.py - Анализ повторных обращений клиентов

Определяет повторных клиентов, рассчитывает retention метрики,
RFM сегментацию, churn prediction и программу лояльности.

Использование:
    python repeat_customers.py                    # Полный анализ
    python repeat_customers.py --rfm              # Только RFM сегментация
    python repeat_customers.py --cohorts          # Только когортный анализ
    python repeat_customers.py --vip              # Показать VIP клиентов
    python repeat_customers.py --churn            # Клиенты с риском оттока
    python repeat_customers.py --loyalty          # Рекомендации по лояльности
    python repeat_customers.py --export-csv       # Экспорт в CSV
    python repeat_customers.py --export-json      # Экспорт в JSON
"""

import json
import argparse
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict, Any, Tuple
import statistics
import sys

sys.stdout.reconfigure(encoding='utf-8')

# === КОНФИГУРАЦИЯ ===

BASE_DIR = Path("D:/Downloads/Chats/_база")
JSON_DIR = BASE_DIR / "json"
MD_DIR = BASE_DIR / "md"
CSV_DIR = BASE_DIR / "csv"

# Входные файлы
CONTACTS_FILE = JSON_DIR / "contacts.json"
OPERATIONS_FILE = JSON_DIR / "operations.json"
PROFILES_FILE = JSON_DIR / "profiles.json"

# Выходные файлы
OUTPUT_JSON = JSON_DIR / "repeat_customers.json"
OUTPUT_CSV = CSV_DIR / "repeat_customers.csv"
OUTPUT_MD = MD_DIR / "repeat_customers.md"

# Параметры анализа
MIN_GAP_DAYS = 30  # Минимальный gap между заказами для "нового" обращения
MIN_ORDERS_REPEAT = 2  # Минимум заказов для повторного клиента

# RFM пороги (квантили будут рассчитаны автоматически)
RFM_SEGMENTS = {
    "Champions": {"R": [4, 5], "F": [4, 5], "M": [4, 5]},
    "Loyal": {"R": [2, 5], "F": [3, 5], "M": [3, 5]},
    "Potential Loyal": {"R": [3, 5], "F": [1, 3], "M": [1, 3]},
    "New Customers": {"R": [4, 5], "F": [1, 1], "M": [1, 5]},
    "Promising": {"R": [3, 4], "F": [1, 1], "M": [1, 5]},
    "Need Attention": {"R": [2, 3], "F": [2, 3], "M": [2, 3]},
    "About to Sleep": {"R": [2, 3], "F": [1, 2], "M": [1, 5]},
    "At Risk": {"R": [1, 2], "F": [2, 5], "M": [2, 5]},
    "Cant Lose": {"R": [1, 1], "F": [4, 5], "M": [4, 5]},
    "Hibernating": {"R": [1, 2], "F": [1, 2], "M": [1, 2]},
    "Lost": {"R": [1, 1], "F": [1, 1], "M": [1, 5]},
}

# Churn risk пороги
CHURN_THRESHOLDS = {
    "critical": 90,   # >90 дней без заказов
    "high": 60,       # 60-90 дней
    "medium": 30,     # 30-60 дней
    "low": 0          # <30 дней
}

# VIP порог (топ N% по LTV)
VIP_PERCENTILE = 10

# Текущая дата
TODAY = datetime.now().date()


def load_json(filepath: Path) -> list:
    """Загрузка JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Если это словарь с ключом contacts/profiles/operations
        if isinstance(data, dict):
            for key in ['contacts', 'profiles', 'operations', 'data']:
                if key in data:
                    return data[key]
        return data if isinstance(data, list) else []


def save_json(data: dict, filepath: Path):
    """Сохранение JSON файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"[+] JSON сохранён: {filepath}")


def parse_date(date_str: str) -> Optional[datetime]:
    """Парсинг даты из разных форматов."""
    if not date_str:
        return None

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d.%m.%Y",
        "%d/%m/%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str)[:19], fmt)
        except (ValueError, TypeError):
            continue

    return None


def get_month_key(date: datetime) -> str:
    """Получить ключ месяца YYYY-MM."""
    return date.strftime("%Y-%m")


def get_quarter_key(date: datetime) -> str:
    """Получить ключ квартала YYYY-QN."""
    quarter = (date.month - 1) // 3 + 1
    return f"{date.year}-Q{quarter}"


# === ОСНОВНЫЕ ФУНКЦИИ АНАЛИЗА ===

def identify_repeat_customers(operations: list) -> Dict[str, Dict]:
    """
    Определение повторных клиентов.

    Критерии:
    - > 1 бронирования
    - Gap между контактами > MIN_GAP_DAYS дней
    """
    customers = defaultdict(lambda: {
        "orders": [],
        "total_amount_aed": 0,
        "order_dates": [],
        "contact_sessions": []  # Группы заказов с gap > MIN_GAP_DAYS
    })

    # Конвертация валют в AED
    conversion_rates = {"AED": 1, "USD": 3.67, "RUB": 0.038, "EUR": 4.0}

    # Группируем операции по телефону
    for op in operations:
        if op.get("status") != "completed":
            continue

        phone = op.get("phone")
        if not phone:
            continue

        amount = op.get("amount", 0) or 0
        currency = op.get("currency", "AED")
        rate = conversion_rates.get(currency, 1)
        amount_aed = amount * rate

        date = parse_date(op.get("date"))

        customers[phone]["orders"].append(op)
        customers[phone]["total_amount_aed"] += amount_aed
        if date:
            customers[phone]["order_dates"].append(date)

    # Определяем сессии контактов и повторных клиентов
    result = {}

    for phone, data in customers.items():
        if not data["order_dates"]:
            continue

        # Сортируем даты
        dates = sorted(data["order_dates"])

        # Группируем по сессиям (gap > MIN_GAP_DAYS)
        sessions = []
        current_session = [dates[0]]

        for i in range(1, len(dates)):
            gap = (dates[i].date() - dates[i-1].date()).days
            if gap > MIN_GAP_DAYS:
                sessions.append(current_session)
                current_session = [dates[i]]
            else:
                current_session.append(dates[i])
        sessions.append(current_session)

        # Определяем статус
        is_repeat = len(data["orders"]) >= MIN_ORDERS_REPEAT
        has_gap_sessions = len(sessions) > 1

        # Расчёт метрик
        first_order = min(dates)
        last_order = max(dates)
        lifetime_days = (last_order.date() - first_order.date()).days
        days_since_last = (TODAY - last_order.date()).days

        # Интервалы между заказами
        intervals = []
        for i in range(1, len(dates)):
            intervals.append((dates[i].date() - dates[i-1].date()).days)

        avg_interval = statistics.mean(intervals) if intervals else 0

        result[phone] = {
            "phone": phone,
            "orders_count": len(data["orders"]),
            "total_amount_aed": round(data["total_amount_aed"], 2),
            "first_order_date": first_order.strftime("%Y-%m-%d"),
            "last_order_date": last_order.strftime("%Y-%m-%d"),
            "lifetime_days": lifetime_days,
            "days_since_last_order": days_since_last,
            "sessions_count": len(sessions),
            "is_repeat_customer": is_repeat,
            "has_gap_sessions": has_gap_sessions,
            "avg_interval_days": round(avg_interval, 1),
            "order_intervals": intervals,
            "first_order_month": get_month_key(first_order)
        }

    return result


def calculate_repeat_metrics(customer_data: Dict[str, Dict]) -> Dict:
    """Расчёт метрик повторных обращений."""

    total_customers = len(customer_data)
    if total_customers == 0:
        return {
            "total_customers": 0,
            "repeat_customers": 0,
            "repeat_rate": 0,
            "avg_orders_per_customer": 0,
            "avg_interval_days": 0
        }

    repeat_customers = [c for c in customer_data.values() if c["is_repeat_customer"]]
    repeat_count = len(repeat_customers)

    # Средние
    all_orders = [c["orders_count"] for c in customer_data.values()]
    all_intervals = []
    for c in repeat_customers:
        all_intervals.extend(c.get("order_intervals", []))

    return {
        "total_customers": total_customers,
        "repeat_customers": repeat_count,
        "one_time_customers": total_customers - repeat_count,
        "repeat_rate": round(repeat_count / total_customers * 100, 2),
        "avg_orders_per_customer": round(statistics.mean(all_orders), 2),
        "avg_orders_repeat_customer": round(
            statistics.mean([c["orders_count"] for c in repeat_customers]), 2
        ) if repeat_customers else 0,
        "median_orders": statistics.median(all_orders),
        "avg_interval_days": round(statistics.mean(all_intervals), 1) if all_intervals else 0,
        "median_interval_days": statistics.median(all_intervals) if all_intervals else 0,
        "max_orders": max(all_orders),
        "customers_3plus_orders": len([c for c in customer_data.values() if c["orders_count"] >= 3]),
        "customers_5plus_orders": len([c for c in customer_data.values() if c["orders_count"] >= 5]),
    }


def calculate_retention_cohorts(customer_data: Dict[str, Dict], operations: list) -> Dict:
    """
    Расчёт retention когорт по месяцу первой покупки.

    Показывает % клиентов, вернувшихся в месяц N после первой покупки.
    """
    # Группируем клиентов по когортам (месяц первой покупки)
    cohorts = defaultdict(lambda: {
        "customers": [],
        "phones": set()
    })

    for phone, data in customer_data.items():
        cohort_month = data.get("first_order_month")
        if cohort_month:
            cohorts[cohort_month]["customers"].append(data)
            cohorts[cohort_month]["phones"].add(phone)

    # Создаём словарь операций по телефону и дате
    ops_by_phone = defaultdict(list)
    for op in operations:
        if op.get("status") == "completed":
            phone = op.get("phone")
            date = parse_date(op.get("date"))
            if phone and date:
                ops_by_phone[phone].append(date)

    # Расчёт retention для каждой когорты
    result = {}

    for cohort_month, cohort_data in sorted(cohorts.items()):
        cohort_start = datetime.strptime(cohort_month + "-01", "%Y-%m-%d")
        cohort_size = len(cohort_data["customers"])

        # Retention по месяцам (до 12 месяцев)
        retention = {}

        for month_offset in range(1, 13):
            target_month_start = cohort_start + timedelta(days=30 * month_offset)
            target_month_end = target_month_start + timedelta(days=30)

            # Сколько клиентов когорты сделали заказ в этом месяце
            active_customers = 0

            for phone in cohort_data["phones"]:
                dates = ops_by_phone.get(phone, [])
                for d in dates:
                    if target_month_start <= d < target_month_end:
                        active_customers += 1
                        break

            retention[f"M{month_offset}"] = {
                "active": active_customers,
                "rate": round(active_customers / cohort_size * 100, 1) if cohort_size > 0 else 0
            }

        # Общий % вернувшихся (хотя бы 1 раз после первого месяца)
        returned_ever = len([c for c in cohort_data["customers"] if c["orders_count"] > 1])

        result[cohort_month] = {
            "cohort_size": cohort_size,
            "returned_customers": returned_ever,
            "overall_return_rate": round(returned_ever / cohort_size * 100, 1) if cohort_size > 0 else 0,
            "monthly_retention": retention
        }

    return result


def calculate_rfm_scores(customer_data: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    RFM сегментация клиентов.

    R - Recency (дней с последнего заказа)
    F - Frequency (количество заказов)
    M - Monetary (общая сумма в AED)

    Каждый параметр получает оценку 1-5 (5 = лучший)
    """
    if not customer_data:
        return {}

    # Собираем значения для расчёта квантилей
    recency_values = [c["days_since_last_order"] for c in customer_data.values()]
    frequency_values = [c["orders_count"] for c in customer_data.values()]
    monetary_values = [c["total_amount_aed"] for c in customer_data.values()]

    def get_quantiles(values: list, q: int = 5) -> list:
        """Расчёт квантилей для разбиения на q групп."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        return [sorted_values[int(n * i / q)] for i in range(1, q)]

    def score_value(value: float, quantiles: list, reverse: bool = False) -> int:
        """Присвоение оценки 1-5 на основе квантилей."""
        for i, q in enumerate(quantiles):
            if value <= q:
                return (5 - i) if reverse else (i + 1)
        return 1 if reverse else 5

    # Квантили
    r_quantiles = get_quantiles(recency_values)
    f_quantiles = get_quantiles(frequency_values)
    m_quantiles = get_quantiles(monetary_values)

    result = {}

    for phone, data in customer_data.items():
        # R - чем меньше дней, тем лучше (reverse=True)
        r_score = score_value(data["days_since_last_order"], r_quantiles, reverse=True)
        # F - чем больше заказов, тем лучше
        f_score = score_value(data["orders_count"], f_quantiles)
        # M - чем больше сумма, тем лучше
        m_score = score_value(data["total_amount_aed"], m_quantiles)

        rfm_score = f"{r_score}{f_score}{m_score}"
        rfm_sum = r_score + f_score + m_score

        # Определение сегмента
        segment = determine_rfm_segment(r_score, f_score, m_score)

        result[phone] = {
            **data,
            "rfm_r": r_score,
            "rfm_f": f_score,
            "rfm_m": m_score,
            "rfm_score": rfm_score,
            "rfm_sum": rfm_sum,
            "rfm_segment": segment
        }

    return result


def determine_rfm_segment(r: int, f: int, m: int) -> str:
    """Определение RFM сегмента по оценкам."""

    for segment, rules in RFM_SEGMENTS.items():
        r_match = rules["R"][0] <= r <= rules["R"][1]
        f_match = rules["F"][0] <= f <= rules["F"][1]
        m_match = rules["M"][0] <= m <= rules["M"][1]

        if r_match and f_match and m_match:
            return segment

    return "Other"


def calculate_churn_prediction(rfm_data: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Прогноз оттока клиентов.

    На основе:
    - Дней с последнего заказа
    - Тренда частоты заказов
    - RFM сегмента
    """
    result = {}

    for phone, data in rfm_data.items():
        days_inactive = data["days_since_last_order"]

        # Базовый риск на основе дней без активности
        if days_inactive > CHURN_THRESHOLDS["critical"]:
            risk_level = "critical"
            base_probability = 0.9
        elif days_inactive > CHURN_THRESHOLDS["high"]:
            risk_level = "high"
            base_probability = 0.7
        elif days_inactive > CHURN_THRESHOLDS["medium"]:
            risk_level = "medium"
            base_probability = 0.4
        else:
            risk_level = "low"
            base_probability = 0.1

        # Корректировка на основе RFM
        rfm_segment = data.get("rfm_segment", "Other")

        segment_adjustment = {
            "Champions": -0.3,
            "Loyal": -0.2,
            "Potential Loyal": -0.1,
            "New Customers": 0,
            "Promising": 0,
            "Need Attention": 0.1,
            "About to Sleep": 0.15,
            "At Risk": 0.2,
            "Cant Lose": 0.25,
            "Hibernating": 0.3,
            "Lost": 0.4,
        }.get(rfm_segment, 0)

        churn_probability = max(0, min(1, base_probability + segment_adjustment))

        # Рекомендуемое действие
        if churn_probability > 0.7:
            action = "urgent_reactivation"
            action_ru = "Срочная реактивация с персональным предложением"
        elif churn_probability > 0.5:
            action = "special_offer"
            action_ru = "Специальное предложение/скидка"
        elif churn_probability > 0.3:
            action = "engagement"
            action_ru = "Вовлечение: новости, акции"
        else:
            action = "maintain"
            action_ru = "Поддержание контакта"

        result[phone] = {
            **data,
            "churn_risk_level": risk_level,
            "churn_probability": round(churn_probability, 2),
            "recommended_action": action,
            "recommended_action_ru": action_ru
        }

    return result


def identify_vip_customers(churn_data: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Определение VIP клиентов (топ N% по LTV).
    """
    if not churn_data:
        return {}

    # Сортируем по сумме
    sorted_customers = sorted(
        churn_data.items(),
        key=lambda x: x[1]["total_amount_aed"],
        reverse=True
    )

    # Топ N%
    vip_count = max(1, len(sorted_customers) * VIP_PERCENTILE // 100)
    vip_phones = set(phone for phone, _ in sorted_customers[:vip_count])

    # Добавляем VIP статус
    result = {}
    for phone, data in churn_data.items():
        result[phone] = {
            **data,
            "is_vip": phone in vip_phones,
            "vip_rank": None
        }

        # Добавляем ранг для VIP
        if phone in vip_phones:
            for i, (p, _) in enumerate(sorted_customers[:vip_count]):
                if p == phone:
                    result[phone]["vip_rank"] = i + 1
                    break

    return result


def generate_loyalty_recommendations(vip_data: Dict[str, Dict]) -> Dict:
    """
    Генерация рекомендаций по программе лояльности.
    """
    # Статистика по сегментам
    segment_stats = defaultdict(lambda: {"count": 0, "total_ltv": 0, "customers": []})

    for phone, data in vip_data.items():
        segment = data.get("rfm_segment", "Other")
        segment_stats[segment]["count"] += 1
        segment_stats[segment]["total_ltv"] += data["total_amount_aed"]
        segment_stats[segment]["customers"].append(phone)

    # Рекомендации по сегментам
    recommendations = {
        "Champions": {
            "strategy": "Retention & Referral",
            "actions": [
                "Персональный менеджер",
                "Эксклюзивные предложения первым",
                "Программа рефералов с бонусами",
                "VIP события и приглашения",
                "Подарки на День рождения"
            ],
            "discount_level": "15-20%",
            "priority": 1
        },
        "Loyal": {
            "strategy": "Upsell & Cross-sell",
            "actions": [
                "Предложения премиум-услуг",
                "Бонусная программа накопления",
                "Ранний доступ к новинкам",
                "Персонализированные рекомендации"
            ],
            "discount_level": "10-15%",
            "priority": 2
        },
        "Potential Loyal": {
            "strategy": "Conversion to Loyal",
            "actions": [
                "Прогрессивная скидка за частоту",
                "Бонус за следующий заказ",
                "Напоминания о новых турах"
            ],
            "discount_level": "7-10%",
            "priority": 3
        },
        "At Risk": {
            "strategy": "Win-back",
            "actions": [
                "Личное обращение менеджера",
                "Значительная скидка на следующий заказ",
                "Опрос о причинах ухода",
                "Специальное предложение с дедлайном"
            ],
            "discount_level": "20-25%",
            "priority": 1
        },
        "Cant Lose": {
            "strategy": "Urgent Win-back",
            "actions": [
                "Срочный звонок от менеджера",
                "Максимальная скидка",
                "Компенсация за неудобства (если были)",
                "Персональный тур"
            ],
            "discount_level": "25-30%",
            "priority": 1
        },
        "Lost": {
            "strategy": "Reactivation Campaign",
            "actions": [
                "Email/WhatsApp кампания реактивации",
                "Разовое супер-предложение",
                "Информация о новых продуктах"
            ],
            "discount_level": "20%",
            "priority": 4
        },
        "New Customers": {
            "strategy": "Onboarding & Second Purchase",
            "actions": [
                "Welcome-бонус на второй заказ",
                "Персональные рекомендации на основе первого заказа",
                "Подписка на рассылку"
            ],
            "discount_level": "5-10%",
            "priority": 2
        }
    }

    # Итоговые рекомендации
    result = {
        "segment_analysis": {},
        "priority_actions": [],
        "loyalty_tiers": [],
        "overall_strategy": []
    }

    # Анализ по сегментам
    for segment, stats in segment_stats.items():
        rec = recommendations.get(segment, {
            "strategy": "Standard",
            "actions": ["Стандартные предложения"],
            "discount_level": "5%",
            "priority": 5
        })

        result["segment_analysis"][segment] = {
            "count": stats["count"],
            "total_ltv": round(stats["total_ltv"], 2),
            "avg_ltv": round(stats["total_ltv"] / stats["count"], 2) if stats["count"] > 0 else 0,
            "strategy": rec["strategy"],
            "actions": rec["actions"],
            "discount_level": rec["discount_level"],
            "priority": rec["priority"]
        }

    # Приоритетные действия
    priority_segments = ["Cant Lose", "At Risk", "Champions"]
    for seg in priority_segments:
        if seg in segment_stats:
            rec = recommendations.get(seg, {})
            result["priority_actions"].append({
                "segment": seg,
                "customers_count": segment_stats[seg]["count"],
                "strategy": rec.get("strategy", ""),
                "first_action": rec.get("actions", [""])[0] if rec.get("actions") else ""
            })

    # Уровни лояльности
    result["loyalty_tiers"] = [
        {
            "tier": "Platinum",
            "criteria": "LTV > 50,000 AED или > 10 заказов",
            "benefits": ["Скидка 20%", "Персональный менеджер", "Приоритетное бронирование", "Бесплатный апгрейд"]
        },
        {
            "tier": "Gold",
            "criteria": "LTV > 20,000 AED или > 5 заказов",
            "benefits": ["Скидка 15%", "Ранний доступ", "Бонус на ДР"]
        },
        {
            "tier": "Silver",
            "criteria": "LTV > 5,000 AED или > 2 заказов",
            "benefits": ["Скидка 10%", "Накопительные бонусы"]
        },
        {
            "tier": "Bronze",
            "criteria": "Первый заказ",
            "benefits": ["Welcome-бонус 5%"]
        }
    ]

    # Общая стратегия
    result["overall_strategy"] = [
        "1. Внедрить CRM с автоматическими триггерами",
        "2. Запустить WhatsApp рассылку по сегментам",
        "3. Создать программу рефералов для Champions",
        "4. Автоматические follow-up для At Risk",
        "5. Персонализированные предложения на основе истории"
    ]

    return result


def generate_markdown_report(analysis: Dict) -> str:
    """Генерация Markdown отчёта."""
    md = []
    md.append("# Анализ повторных обращений клиентов")
    md.append(f"\n*Дата отчёта: {TODAY.strftime('%Y-%m-%d')}*\n")

    # Основные метрики
    metrics = analysis.get("repeat_metrics", {})
    md.append("## Основные метрики\n")
    md.append("| Метрика | Значение |")
    md.append("|---------|----------|")
    md.append(f"| Всего клиентов | {metrics.get('total_customers', 0)} |")
    md.append(f"| Повторных клиентов | {metrics.get('repeat_customers', 0)} |")
    md.append(f"| Одноразовых клиентов | {metrics.get('one_time_customers', 0)} |")
    md.append(f"| **% повторных** | **{metrics.get('repeat_rate', 0)}%** |")
    md.append(f"| Среднее заказов на клиента | {metrics.get('avg_orders_per_customer', 0)} |")
    md.append(f"| Среднее заказов (повторные) | {metrics.get('avg_orders_repeat_customer', 0)} |")
    md.append(f"| Средний интервал (дни) | {metrics.get('avg_interval_days', 0)} |")
    md.append(f"| Клиентов с 3+ заказами | {metrics.get('customers_3plus_orders', 0)} |")
    md.append(f"| Клиентов с 5+ заказами | {metrics.get('customers_5plus_orders', 0)} |")
    md.append("")

    # RFM сегментация
    rfm_segments = analysis.get("rfm_segment_summary", {})
    if rfm_segments:
        md.append("## RFM Сегментация\n")
        md.append("| Сегмент | Клиентов | % | Общий LTV | Ср. LTV |")
        md.append("|---------|----------|---|-----------|---------|")

        total = sum(s.get("count", 0) for s in rfm_segments.values())
        for segment in ["Champions", "Loyal", "Potential Loyal", "New Customers",
                       "At Risk", "Cant Lose", "Hibernating", "Lost"]:
            if segment in rfm_segments:
                s = rfm_segments[segment]
                pct = round(s["count"] / total * 100, 1) if total > 0 else 0
                md.append(f"| {segment} | {s['count']} | {pct}% | {s['total_ltv']:,.0f} | {s['avg_ltv']:,.0f} |")
        md.append("")

    # Churn риски
    churn_summary = analysis.get("churn_summary", {})
    if churn_summary:
        md.append("## Риск оттока\n")
        md.append("| Уровень риска | Клиентов | % |")
        md.append("|---------------|----------|---|")

        for level in ["critical", "high", "medium", "low"]:
            if level in churn_summary:
                data = churn_summary[level]
                md.append(f"| {level.upper()} | {data['count']} | {data['percentage']}% |")
        md.append("")

    # VIP клиенты
    vip_customers = analysis.get("vip_customers", [])
    if vip_customers:
        md.append("## VIP Клиенты (топ 10%)\n")
        md.append("| # | Телефон | Заказов | LTV (AED) | Сегмент |")
        md.append("|---|---------|---------|-----------|---------|")

        for i, c in enumerate(vip_customers[:20], 1):
            md.append(f"| {i} | {c['phone']} | {c['orders_count']} | {c['total_amount_aed']:,.0f} | {c.get('rfm_segment', '-')} |")
        md.append("")

    # Retention когорты
    cohorts = analysis.get("retention_cohorts", {})
    if cohorts:
        md.append("## Retention по когортам\n")
        md.append("| Когорта | Размер | Вернулось | % | M1 | M3 | M6 | M12 |")
        md.append("|---------|--------|-----------|---|----|----|----|----|")

        for cohort, data in sorted(cohorts.items(), reverse=True)[:12]:
            m1 = data.get("monthly_retention", {}).get("M1", {}).get("rate", 0)
            m3 = data.get("monthly_retention", {}).get("M3", {}).get("rate", 0)
            m6 = data.get("monthly_retention", {}).get("M6", {}).get("rate", 0)
            m12 = data.get("monthly_retention", {}).get("M12", {}).get("rate", 0)
            md.append(f"| {cohort} | {data['cohort_size']} | {data['returned_customers']} | {data['overall_return_rate']}% | {m1}% | {m3}% | {m6}% | {m12}% |")
        md.append("")

    # Рекомендации по лояльности
    loyalty = analysis.get("loyalty_recommendations", {})
    if loyalty:
        md.append("## Программа лояльности\n")

        md.append("### Уровни лояльности\n")
        for tier in loyalty.get("loyalty_tiers", []):
            md.append(f"**{tier['tier']}**")
            md.append(f"- Критерий: {tier['criteria']}")
            md.append(f"- Бонусы: {', '.join(tier['benefits'])}")
            md.append("")

        md.append("### Приоритетные действия\n")
        for action in loyalty.get("priority_actions", []):
            md.append(f"- **{action['segment']}** ({action['customers_count']} клиентов): {action['first_action']}")
        md.append("")

        md.append("### Общая стратегия\n")
        for s in loyalty.get("overall_strategy", []):
            md.append(s)
        md.append("")

    return "\n".join(md)


def export_to_csv(data: Dict[str, Dict], filepath: Path):
    """Экспорт в CSV."""
    if not data:
        print("[!] Нет данных для экспорта")
        return

    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "phone", "orders_count", "total_amount_aed",
        "first_order_date", "last_order_date", "lifetime_days",
        "days_since_last_order", "is_repeat_customer", "sessions_count",
        "avg_interval_days", "rfm_r", "rfm_f", "rfm_m",
        "rfm_score", "rfm_segment", "churn_risk_level",
        "churn_probability", "is_vip", "vip_rank",
        "recommended_action_ru"
    ]

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data.values())

    print(f"[+] CSV экспортирован: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Анализ повторных обращений клиентов")
    parser.add_argument("--rfm", action="store_true", help="Показать RFM сегментацию")
    parser.add_argument("--cohorts", action="store_true", help="Показать retention когорты")
    parser.add_argument("--vip", action="store_true", help="Показать VIP клиентов")
    parser.add_argument("--churn", action="store_true", help="Показать клиентов с риском оттока")
    parser.add_argument("--loyalty", action="store_true", help="Показать рекомендации по лояльности")
    parser.add_argument("--export-csv", action="store_true", help="Экспорт в CSV")
    parser.add_argument("--export-json", action="store_true", help="Экспорт в JSON")
    parser.add_argument("--min-gap", type=int, default=MIN_GAP_DAYS,
                       help=f"Минимальный gap между сессиями (дни, default: {MIN_GAP_DAYS})")
    parser.add_argument("--quiet", "-q", action="store_true", help="Минимальный вывод")

    args = parser.parse_args()

    # Загрузка данных
    print("[*] Загрузка данных...")
    contacts = load_json(CONTACTS_FILE)
    operations = load_json(OPERATIONS_FILE)
    profiles = load_json(PROFILES_FILE)

    if not operations:
        print("[!] Нет операций для анализа. Убедитесь, что файл operations.json существует.")
        return

    print(f"[*] Загружено операций: {len(operations)}")
    print(f"[*] Загружено контактов: {len(contacts)}")

    # Определение повторных клиентов
    print("\n[*] Определение повторных клиентов...")
    customer_data = identify_repeat_customers(operations)
    print(f"[*] Найдено клиентов с заказами: {len(customer_data)}")

    # Расчёт метрик
    print("[*] Расчёт метрик...")
    repeat_metrics = calculate_repeat_metrics(customer_data)

    # Retention когорты
    print("[*] Расчёт retention когорт...")
    retention_cohorts = calculate_retention_cohorts(customer_data, operations)

    # RFM сегментация
    print("[*] RFM сегментация...")
    rfm_data = calculate_rfm_scores(customer_data)

    # Churn prediction
    print("[*] Прогноз оттока...")
    churn_data = calculate_churn_prediction(rfm_data)

    # VIP клиенты
    print("[*] Определение VIP клиентов...")
    final_data = identify_vip_customers(churn_data)

    # Рекомендации по лояльности
    print("[*] Генерация рекомендаций...")
    loyalty_recommendations = generate_loyalty_recommendations(final_data)

    # Сводки
    rfm_segment_summary = defaultdict(lambda: {"count": 0, "total_ltv": 0})
    churn_summary = defaultdict(lambda: {"count": 0})
    vip_customers = []

    for phone, data in final_data.items():
        # RFM
        seg = data.get("rfm_segment", "Other")
        rfm_segment_summary[seg]["count"] += 1
        rfm_segment_summary[seg]["total_ltv"] += data["total_amount_aed"]

        # Churn
        risk = data.get("churn_risk_level", "unknown")
        churn_summary[risk]["count"] += 1

        # VIP
        if data.get("is_vip"):
            vip_customers.append(data)

    # Добавляем средние в RFM сводку
    for seg, stats in rfm_segment_summary.items():
        stats["avg_ltv"] = round(stats["total_ltv"] / stats["count"], 2) if stats["count"] > 0 else 0

    # Проценты для churn
    total_for_churn = sum(s["count"] for s in churn_summary.values())
    for level, stats in churn_summary.items():
        stats["percentage"] = round(stats["count"] / total_for_churn * 100, 1) if total_for_churn > 0 else 0

    # Сортируем VIP по LTV
    vip_customers.sort(key=lambda x: x["total_amount_aed"], reverse=True)

    # Формирование результата
    analysis = {
        "generated_at": datetime.now().isoformat(),
        "parameters": {
            "min_gap_days": args.min_gap,
            "min_orders_repeat": MIN_ORDERS_REPEAT,
            "vip_percentile": VIP_PERCENTILE
        },
        "repeat_metrics": repeat_metrics,
        "retention_cohorts": retention_cohorts,
        "rfm_segment_summary": dict(rfm_segment_summary),
        "churn_summary": dict(churn_summary),
        "vip_customers": vip_customers[:50],  # Топ 50
        "loyalty_recommendations": loyalty_recommendations,
        "customers_detail": final_data
    }

    # Сохранение
    if args.export_json or not (args.rfm or args.cohorts or args.vip or args.churn or args.loyalty):
        save_json(analysis, OUTPUT_JSON)

    if args.export_csv:
        export_to_csv(final_data, OUTPUT_CSV)

    # Markdown отчёт
    md_report = generate_markdown_report(analysis)
    MD_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_report)
    print(f"[+] Markdown отчёт: {OUTPUT_MD}")

    # Вывод результатов
    if not args.quiet:
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА ПОВТОРНЫХ ОБРАЩЕНИЙ")
        print("="*60)

        print(f"\n{'='*30} МЕТРИКИ {'='*30}")
        print(f"Всего клиентов: {repeat_metrics['total_customers']}")
        print(f"Повторных клиентов: {repeat_metrics['repeat_customers']} ({repeat_metrics['repeat_rate']}%)")
        print(f"Одноразовых: {repeat_metrics['one_time_customers']}")
        print(f"Среднее заказов на клиента: {repeat_metrics['avg_orders_per_customer']}")
        print(f"Средний интервал между заказами: {repeat_metrics['avg_interval_days']} дней")

        if args.rfm or not (args.cohorts or args.vip or args.churn or args.loyalty):
            print(f"\n{'='*30} RFM СЕГМЕНТЫ {'='*30}")
            for seg in ["Champions", "Loyal", "At Risk", "Cant Lose", "Lost"]:
                if seg in rfm_segment_summary:
                    s = rfm_segment_summary[seg]
                    print(f"  {seg}: {s['count']} клиентов, LTV {s['total_ltv']:,.0f} AED")

        if args.churn or not (args.rfm or args.cohorts or args.vip or args.loyalty):
            print(f"\n{'='*30} РИСК ОТТОКА {'='*30}")
            for level in ["critical", "high", "medium", "low"]:
                if level in churn_summary:
                    print(f"  {level.upper()}: {churn_summary[level]['count']} ({churn_summary[level]['percentage']}%)")

        if args.vip or not (args.rfm or args.cohorts or args.churn or args.loyalty):
            print(f"\n{'='*30} VIP КЛИЕНТЫ (топ 10) {'='*30}")
            for i, c in enumerate(vip_customers[:10], 1):
                print(f"  {i}. {c['phone']}: {c['orders_count']} заказов, {c['total_amount_aed']:,.0f} AED")

        if args.cohorts:
            print(f"\n{'='*30} RETENTION КОГОРТЫ {'='*30}")
            for cohort, data in sorted(retention_cohorts.items(), reverse=True)[:6]:
                print(f"  {cohort}: {data['cohort_size']} клиентов, {data['overall_return_rate']}% вернулись")

        if args.loyalty:
            print(f"\n{'='*30} ПРОГРАММА ЛОЯЛЬНОСТИ {'='*30}")
            for tier in loyalty_recommendations.get("loyalty_tiers", []):
                print(f"\n  {tier['tier']}:")
                print(f"    Критерий: {tier['criteria']}")
                print(f"    Бонусы: {', '.join(tier['benefits'])}")

    print("\n[+] Анализ завершён!")


if __name__ == "__main__":
    main()
