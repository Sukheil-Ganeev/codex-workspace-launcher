#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Расширенный анализ времени первого ответа (First Response Time / FRT).

Входные файлы:
  - D:/Downloads/Chats/_база/raw/all_messages.jsonl
  - D:/Downloads/Chats/_база/json/contacts.json (для классификации)
  - D:/Downloads/Chats/_база/json/sales_funnel.json (для конверсии)

Выходные файлы:
  - D:/Downloads/Chats/_база/json/first_response_time.json
  - D:/Downloads/Chats/_база/csv/first_response_time.csv
  - D:/Downloads/Chats/_база/md/время_первого_ответа.md

Функции:
  1. Время от первого сообщения клиента до первого ответа
  2. Сегментация по типу клиента (agent, direct)
  3. Сегментация по времени суток и дню недели
  4. SLA метрики (% < 5 мин, < 1 час, < 24 часа)
  5. Влияние на конверсию (корреляция FRT с продажами)
  6. Benchmarks по отрасли туризма
  7. Алерты (долгие ответы, нарушения SLA)
  8. Визуализация (ASCII графики, данные для charts)
  9. Экспорт: JSON, CSV
"""

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import RAW_DIR, JSON_DIR, CSV_DIR, MD_DIR, ensure_directories, CONTACT_TYPES
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    CSV_DIR = Path("D:/Downloads/Chats/_база/csv")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")
    CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]

    def ensure_directories():
        for d in [RAW_DIR, JSON_DIR, CSV_DIR, MD_DIR]:
            d.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ И КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# SLA Пороги (в минутах)
SLA_THRESHOLDS = {
    "excellent": 5,       # < 5 минут - отлично
    "good": 30,           # < 30 минут - хорошо
    "acceptable": 60,     # < 1 час - приемлемо
    "warning": 240,       # < 4 часа - предупреждение
    "critical": 1440,     # < 24 часа - критично
}

# Industry Benchmarks (туризм/travel, в минутах)
INDUSTRY_BENCHMARKS = {
    "travel_agency": {
        "median_frt": 60,              # Медиана 1 час
        "p90_frt": 240,                # 90-й процентиль 4 часа
        "response_rate": 0.85,         # 85% отвечают
        "under_5min_rate": 0.15,       # 15% < 5 мин
        "under_1hr_rate": 0.55,        # 55% < 1 час
        "under_24hr_rate": 0.90,       # 90% < 24 часа
        "source": "Zendesk Benchmark Report 2024"
    },
    "premium_travel": {
        "median_frt": 15,
        "p90_frt": 60,
        "response_rate": 0.95,
        "under_5min_rate": 0.40,
        "under_1hr_rate": 0.80,
        "under_24hr_rate": 0.98,
        "source": "Premium Travel Industry Standards"
    },
    "b2b_agents": {
        "median_frt": 120,
        "p90_frt": 480,
        "response_rate": 0.90,
        "under_5min_rate": 0.10,
        "under_1hr_rate": 0.40,
        "under_24hr_rate": 0.85,
        "source": "B2B Travel Partner Expectations"
    }
}

# Дни недели
DAY_NAMES_RU = {
    0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг",
    4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}
DAY_NAMES_EN = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday"
}

# Периоды суток
TIME_PERIODS = {
    "night": (0, 6),      # 00:00 - 06:00
    "morning": (6, 12),   # 06:00 - 12:00
    "afternoon": (12, 18),# 12:00 - 18:00
    "evening": (18, 24),  # 18:00 - 24:00
}
TIME_PERIODS_RU = {
    "night": "Ночь (00-06)",
    "morning": "Утро (06-12)",
    "afternoon": "День (12-18)",
    "evening": "Вечер (18-24)",
}


# ═══════════════════════════════════════════════════════════════
# КЛАССЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class FirstResponseRecord:
    """Запись о первом ответе для контакта."""
    jid: str
    chat_name: Optional[str]
    contact_type: str  # direct, agent, supplier, etc.
    first_client_msg_time: datetime
    first_response_time: Optional[datetime]
    frt_minutes: Optional[float]
    sla_level: str
    day_of_week: str
    hour: int
    time_period: str
    converted: bool = False  # Связь с воронкой продаж
    revenue: float = 0.0


@dataclass
class Alert:
    """Алерт о проблеме с временем ответа."""
    jid: str
    chat_name: str
    alert_type: str  # slow_response, no_response, sla_violation
    severity: str    # warning, critical
    frt_minutes: Optional[float]
    message: str
    first_msg_time: str


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Преобразовать ISO строку в datetime."""
    if not dt_str:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d.%m.%Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str[:19], fmt[:19] if len(fmt) > 19 else fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def load_messages(input_file: Path) -> List[Dict]:
    """Загрузить сообщения из JSONL файла."""
    messages = []
    if not input_file.exists():
        print(f"[ОШИБКА] Файл не найден: {input_file}")
        return messages

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return messages


def load_contacts(contacts_file: Path) -> Dict[str, Dict]:
    """Загрузить контакты из JSON файла."""
    if not contacts_file.exists():
        return {}

    with open(contacts_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    contacts = data if isinstance(data, list) else data.get("contacts", [])
    return {c.get("jid", ""): c for c in contacts if c.get("jid")}


def load_sales_funnel(funnel_file: Path) -> Dict[str, str]:
    """Загрузить данные воронки продаж (jid -> stage)."""
    if not funnel_file.exists():
        return {}

    with open(funnel_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # contacts_by_stage: {stage: [jid1, jid2, ...]}
    result = {}
    for stage, jids in data.get("contacts_by_stage", {}).items():
        for jid in jids:
            result[jid] = stage

    return result


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ АНАЛИЗА
# ═══════════════════════════════════════════════════════════════

def classify_contact_type(jid: str, contacts: Dict[str, Dict]) -> str:
    """Классифицировать тип контакта."""
    contact = contacts.get(jid, {})
    contact_type = contact.get("type", "").lower()

    if contact_type in ["агенты", "agents", "agent", "турагент", "туроператор", "b2b"]:
        return "agent"
    elif contact_type in ["поставщики", "suppliers", "supplier"]:
        return "supplier"
    elif contact_type in ["сотрудники", "employees", "employee"]:
        return "employee"
    else:
        return "direct"  # Прямой клиент


def get_time_period(hour: int) -> str:
    """Определить период суток по часу."""
    for period, (start, end) in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    return "night"


def get_sla_level(frt_minutes: Optional[float]) -> str:
    """Определить уровень SLA по времени ответа."""
    if frt_minutes is None:
        return "no_response"
    if frt_minutes <= SLA_THRESHOLDS["excellent"]:
        return "excellent"
    elif frt_minutes <= SLA_THRESHOLDS["good"]:
        return "good"
    elif frt_minutes <= SLA_THRESHOLDS["acceptable"]:
        return "acceptable"
    elif frt_minutes <= SLA_THRESHOLDS["warning"]:
        return "warning"
    elif frt_minutes <= SLA_THRESHOLDS["critical"]:
        return "critical"
    else:
        return "exceeded"


def calculate_first_response_times(
    messages: List[Dict],
    contacts: Dict[str, Dict],
    funnel_stages: Dict[str, str],
    max_wait_hours: int = 72
) -> Tuple[List[FirstResponseRecord], List[Alert]]:
    """
    Рассчитать время первого ответа для каждого контакта.

    Returns:
        (records, alerts)
    """
    # Группировка сообщений по чатам
    chats = defaultdict(list)
    for msg in messages:
        jid = msg.get("jid")
        if jid and not jid.endswith("@g.us"):  # Пропускаем группы
            chats[jid].append(msg)

    # Сортировка сообщений в каждом чате
    for jid in chats:
        chats[jid].sort(key=lambda m: m.get("datetime", ""))

    records = []
    alerts = []
    max_wait_minutes = max_wait_hours * 60

    for jid, chat_messages in chats.items():
        if not chat_messages:
            continue

        chat_name = chat_messages[0].get("chat_name", jid)
        contact_type = classify_contact_type(jid, contacts)

        # Находим первое сообщение от клиента
        first_client_msg = None
        first_client_dt = None

        for msg in chat_messages:
            if not msg.get("is_from_me", False):
                first_client_msg = msg
                first_client_dt = parse_datetime(msg.get("datetime"))
                break

        if not first_client_dt:
            continue

        # Находим первый ответ после первого сообщения клиента
        first_response_dt = None
        for msg in chat_messages:
            msg_dt = parse_datetime(msg.get("datetime"))
            if not msg_dt:
                continue

            if msg_dt > first_client_dt and msg.get("is_from_me", False):
                first_response_dt = msg_dt
                break

        # Расчёт FRT
        frt_minutes = None
        if first_response_dt:
            delta = (first_response_dt - first_client_dt).total_seconds() / 60
            if delta <= max_wait_minutes:
                frt_minutes = delta

        # Определение параметров
        sla_level = get_sla_level(frt_minutes)
        day_of_week = DAY_NAMES_EN[first_client_dt.weekday()]
        hour = first_client_dt.hour
        time_period = get_time_period(hour)

        # Конверсия
        funnel_stage = funnel_stages.get(jid, "")
        converted = funnel_stage in ["completed", "payment"]

        record = FirstResponseRecord(
            jid=jid,
            chat_name=chat_name,
            contact_type=contact_type,
            first_client_msg_time=first_client_dt,
            first_response_time=first_response_dt,
            frt_minutes=frt_minutes,
            sla_level=sla_level,
            day_of_week=day_of_week,
            hour=hour,
            time_period=time_period,
            converted=converted,
        )
        records.append(record)

        # Генерация алертов
        if sla_level == "no_response":
            alerts.append(Alert(
                jid=jid,
                chat_name=chat_name or "",
                alert_type="no_response",
                severity="critical",
                frt_minutes=None,
                message=f"Нет ответа на сообщение от {first_client_dt.strftime('%d.%m.%Y %H:%M')}",
                first_msg_time=first_client_dt.isoformat()
            ))
        elif sla_level == "exceeded":
            alerts.append(Alert(
                jid=jid,
                chat_name=chat_name or "",
                alert_type="sla_violation",
                severity="critical",
                frt_minutes=frt_minutes,
                message=f"Ответ через {frt_minutes/60:.1f} часов (SLA нарушен)",
                first_msg_time=first_client_dt.isoformat()
            ))
        elif sla_level in ["warning", "critical"]:
            alerts.append(Alert(
                jid=jid,
                chat_name=chat_name or "",
                alert_type="slow_response",
                severity="warning" if sla_level == "warning" else "critical",
                frt_minutes=frt_minutes,
                message=f"Медленный ответ: {frt_minutes:.1f} мин",
                first_msg_time=first_client_dt.isoformat()
            ))

    return records, alerts


# ═══════════════════════════════════════════════════════════════
# АГРЕГАЦИЯ И СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

def calculate_percentile(data: List[float], p: float) -> float:
    """Рассчитать процентиль."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def aggregate_statistics(records: List[FirstResponseRecord]) -> Dict[str, Any]:
    """Агрегировать статистику по записям FRT."""

    # Фильтруем записи с ответом
    with_response = [r for r in records if r.frt_minutes is not None]
    frt_values = [r.frt_minutes for r in with_response]

    # Общая статистика
    overall = {
        "total_contacts": len(records),
        "with_response": len(with_response),
        "no_response": len(records) - len(with_response),
        "response_rate": len(with_response) / len(records) if records else 0,
    }

    if frt_values:
        overall.update({
            "avg_frt_minutes": round(statistics.mean(frt_values), 2),
            "median_frt_minutes": round(statistics.median(frt_values), 2),
            "min_frt_minutes": round(min(frt_values), 2),
            "max_frt_minutes": round(max(frt_values), 2),
            "p90_frt_minutes": round(calculate_percentile(frt_values, 90), 2),
            "p95_frt_minutes": round(calculate_percentile(frt_values, 95), 2),
            "std_dev": round(statistics.stdev(frt_values), 2) if len(frt_values) > 1 else 0,
        })
    else:
        overall.update({
            "avg_frt_minutes": 0,
            "median_frt_minutes": 0,
            "min_frt_minutes": 0,
            "max_frt_minutes": 0,
            "p90_frt_minutes": 0,
            "p95_frt_minutes": 0,
            "std_dev": 0,
        })

    # SLA Метрики
    sla_metrics = {
        "under_5min": sum(1 for v in frt_values if v <= 5),
        "under_30min": sum(1 for v in frt_values if v <= 30),
        "under_1hr": sum(1 for v in frt_values if v <= 60),
        "under_4hr": sum(1 for v in frt_values if v <= 240),
        "under_24hr": sum(1 for v in frt_values if v <= 1440),
    }
    total = len(with_response) or 1
    sla_rates = {
        "under_5min_rate": round(sla_metrics["under_5min"] / total, 4),
        "under_30min_rate": round(sla_metrics["under_30min"] / total, 4),
        "under_1hr_rate": round(sla_metrics["under_1hr"] / total, 4),
        "under_4hr_rate": round(sla_metrics["under_4hr"] / total, 4),
        "under_24hr_rate": round(sla_metrics["under_24hr"] / total, 4),
    }

    # SLA уровни
    sla_levels = defaultdict(int)
    for r in records:
        sla_levels[r.sla_level] += 1

    # По типу клиента
    by_contact_type = defaultdict(lambda: {"frt_values": [], "converted": 0, "total": 0})
    for r in records:
        by_contact_type[r.contact_type]["total"] += 1
        if r.frt_minutes is not None:
            by_contact_type[r.contact_type]["frt_values"].append(r.frt_minutes)
        if r.converted:
            by_contact_type[r.contact_type]["converted"] += 1

    by_type_stats = {}
    for ct, data in by_contact_type.items():
        vals = data["frt_values"]
        by_type_stats[ct] = {
            "total": data["total"],
            "with_response": len(vals),
            "avg_frt": round(statistics.mean(vals), 2) if vals else 0,
            "median_frt": round(statistics.median(vals), 2) if vals else 0,
            "converted": data["converted"],
            "conversion_rate": round(data["converted"] / data["total"], 4) if data["total"] else 0,
        }

    # По времени суток
    by_time_period = defaultdict(lambda: {"frt_values": [], "total": 0})
    for r in records:
        by_time_period[r.time_period]["total"] += 1
        if r.frt_minutes is not None:
            by_time_period[r.time_period]["frt_values"].append(r.frt_minutes)

    time_period_stats = {}
    for period, data in by_time_period.items():
        vals = data["frt_values"]
        time_period_stats[period] = {
            "name_ru": TIME_PERIODS_RU.get(period, period),
            "total": data["total"],
            "with_response": len(vals),
            "avg_frt": round(statistics.mean(vals), 2) if vals else 0,
            "median_frt": round(statistics.median(vals), 2) if vals else 0,
        }

    # По дню недели
    by_day = defaultdict(lambda: {"frt_values": [], "total": 0})
    for r in records:
        by_day[r.day_of_week]["total"] += 1
        if r.frt_minutes is not None:
            by_day[r.day_of_week]["frt_values"].append(r.frt_minutes)

    day_stats = {}
    for day, data in by_day.items():
        vals = data["frt_values"]
        day_num = [k for k, v in DAY_NAMES_EN.items() if v == day][0] if day in DAY_NAMES_EN.values() else 0
        day_stats[day] = {
            "name_ru": DAY_NAMES_RU.get(day_num, day),
            "total": data["total"],
            "with_response": len(vals),
            "avg_frt": round(statistics.mean(vals), 2) if vals else 0,
            "median_frt": round(statistics.median(vals), 2) if vals else 0,
        }

    # По часам
    by_hour = defaultdict(lambda: {"frt_values": [], "total": 0})
    for r in records:
        by_hour[r.hour]["total"] += 1
        if r.frt_minutes is not None:
            by_hour[r.hour]["frt_values"].append(r.frt_minutes)

    hour_stats = {}
    for hour in range(24):
        data = by_hour[hour]
        vals = data["frt_values"]
        hour_stats[str(hour)] = {
            "total": data["total"],
            "with_response": len(vals),
            "avg_frt": round(statistics.mean(vals), 2) if vals else 0,
            "median_frt": round(statistics.median(vals), 2) if vals else 0,
        }

    # Влияние FRT на конверсию
    converted_frt = [r.frt_minutes for r in with_response if r.converted]
    not_converted_frt = [r.frt_minutes for r in with_response if not r.converted]

    conversion_impact = {
        "converted_avg_frt": round(statistics.mean(converted_frt), 2) if converted_frt else 0,
        "converted_median_frt": round(statistics.median(converted_frt), 2) if converted_frt else 0,
        "not_converted_avg_frt": round(statistics.mean(not_converted_frt), 2) if not_converted_frt else 0,
        "not_converted_median_frt": round(statistics.median(not_converted_frt), 2) if not_converted_frt else 0,
        "converted_count": len(converted_frt),
        "not_converted_count": len(not_converted_frt),
    }

    # Корреляция FRT с конверсией (по квартилям)
    if frt_values:
        q1 = calculate_percentile(frt_values, 25)
        q2 = calculate_percentile(frt_values, 50)
        q3 = calculate_percentile(frt_values, 75)

        quartile_conversion = {
            "q1_fast": {"range": f"< {q1:.0f} мин", "total": 0, "converted": 0},
            "q2": {"range": f"{q1:.0f}-{q2:.0f} мин", "total": 0, "converted": 0},
            "q3": {"range": f"{q2:.0f}-{q3:.0f} мин", "total": 0, "converted": 0},
            "q4_slow": {"range": f"> {q3:.0f} мин", "total": 0, "converted": 0},
        }

        for r in with_response:
            frt = r.frt_minutes
            if frt <= q1:
                q = "q1_fast"
            elif frt <= q2:
                q = "q2"
            elif frt <= q3:
                q = "q3"
            else:
                q = "q4_slow"

            quartile_conversion[q]["total"] += 1
            if r.converted:
                quartile_conversion[q]["converted"] += 1

        for q in quartile_conversion:
            t = quartile_conversion[q]["total"]
            c = quartile_conversion[q]["converted"]
            quartile_conversion[q]["conversion_rate"] = round(c / t, 4) if t else 0
    else:
        quartile_conversion = {}

    return {
        "overall": overall,
        "sla_metrics": sla_metrics,
        "sla_rates": sla_rates,
        "sla_levels": dict(sla_levels),
        "by_contact_type": by_type_stats,
        "by_time_period": time_period_stats,
        "by_day_of_week": day_stats,
        "by_hour": hour_stats,
        "conversion_impact": conversion_impact,
        "quartile_conversion": quartile_conversion,
    }


def compare_with_benchmarks(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Сравнить результаты с отраслевыми бенчмарками."""
    overall = stats.get("overall", {})
    sla_rates = stats.get("sla_rates", {})

    comparison = {}

    for benchmark_name, benchmark in INDUSTRY_BENCHMARKS.items():
        comp = {
            "benchmark_name": benchmark_name,
            "source": benchmark["source"],
            "metrics": {}
        }

        # Медиана FRT
        our_median = overall.get("median_frt_minutes", 0)
        bench_median = benchmark["median_frt"]
        comp["metrics"]["median_frt"] = {
            "our_value": our_median,
            "benchmark": bench_median,
            "difference": round(our_median - bench_median, 2),
            "better": our_median <= bench_median,
            "percent_diff": round((our_median - bench_median) / bench_median * 100, 1) if bench_median else 0
        }

        # Response rate
        our_rr = overall.get("response_rate", 0)
        bench_rr = benchmark["response_rate"]
        comp["metrics"]["response_rate"] = {
            "our_value": round(our_rr, 4),
            "benchmark": bench_rr,
            "difference": round(our_rr - bench_rr, 4),
            "better": our_rr >= bench_rr,
        }

        # < 5 min rate
        our_5min = sla_rates.get("under_5min_rate", 0)
        bench_5min = benchmark["under_5min_rate"]
        comp["metrics"]["under_5min_rate"] = {
            "our_value": round(our_5min, 4),
            "benchmark": bench_5min,
            "difference": round(our_5min - bench_5min, 4),
            "better": our_5min >= bench_5min,
        }

        # < 1 hour rate
        our_1hr = sla_rates.get("under_1hr_rate", 0)
        bench_1hr = benchmark["under_1hr_rate"]
        comp["metrics"]["under_1hr_rate"] = {
            "our_value": round(our_1hr, 4),
            "benchmark": bench_1hr,
            "difference": round(our_1hr - bench_1hr, 4),
            "better": our_1hr >= bench_1hr,
        }

        # Общая оценка
        better_count = sum(1 for m in comp["metrics"].values() if m.get("better"))
        total_metrics = len(comp["metrics"])
        comp["overall_score"] = f"{better_count}/{total_metrics}"
        comp["meets_benchmark"] = better_count >= total_metrics / 2

        comparison[benchmark_name] = comp

    return comparison


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТОВ
# ═══════════════════════════════════════════════════════════════

def generate_ascii_chart(data: Dict[str, int], title: str, width: int = 40) -> str:
    """Генерировать ASCII столбчатую диаграмму."""
    if not data:
        return ""

    lines = [title, "=" * len(title), ""]
    max_val = max(data.values()) if data.values() else 1

    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_len = int((value / max_val) * width) if max_val else 0
        bar = "█" * bar_len
        lines.append(f"{label:15} {bar} {value}")

    return "\n".join(lines)


def generate_markdown_report(
    stats: Dict[str, Any],
    alerts: List[Alert],
    benchmarks: Dict[str, Any]
) -> str:
    """Сгенерировать Markdown отчёт."""
    lines = []
    overall = stats.get("overall", {})
    sla_rates = stats.get("sla_rates", {})

    lines.extend([
        "# Анализ времени первого ответа (FRT)",
        "",
        f"_Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}_",
        "",
        "## Общая статистика",
        "",
        "| Метрика | Значение |",
        "|---------|----------|",
        f"| Всего контактов | {overall.get('total_contacts', 0):,} |",
        f"| С ответом | {overall.get('with_response', 0):,} |",
        f"| Без ответа | {overall.get('no_response', 0):,} |",
        f"| **Response Rate** | **{overall.get('response_rate', 0)*100:.1f}%** |",
        f"| Среднее FRT | {overall.get('avg_frt_minutes', 0):.1f} мин |",
        f"| **Медиана FRT** | **{overall.get('median_frt_minutes', 0):.1f} мин** |",
        f"| Минимум FRT | {overall.get('min_frt_minutes', 0):.1f} мин |",
        f"| Максимум FRT | {overall.get('max_frt_minutes', 0):.1f} мин |",
        f"| P90 FRT | {overall.get('p90_frt_minutes', 0):.1f} мин |",
        f"| P95 FRT | {overall.get('p95_frt_minutes', 0):.1f} мин |",
        "",
    ])

    # SLA метрики
    lines.extend([
        "## SLA Метрики",
        "",
        "| Порог | Количество | Процент |",
        "|-------|------------|---------|",
        f"| < 5 мин (отлично) | {stats.get('sla_metrics', {}).get('under_5min', 0)} | **{sla_rates.get('under_5min_rate', 0)*100:.1f}%** |",
        f"| < 30 мин (хорошо) | {stats.get('sla_metrics', {}).get('under_30min', 0)} | {sla_rates.get('under_30min_rate', 0)*100:.1f}% |",
        f"| < 1 час (приемлемо) | {stats.get('sla_metrics', {}).get('under_1hr', 0)} | **{sla_rates.get('under_1hr_rate', 0)*100:.1f}%** |",
        f"| < 4 часа | {stats.get('sla_metrics', {}).get('under_4hr', 0)} | {sla_rates.get('under_4hr_rate', 0)*100:.1f}% |",
        f"| < 24 часа | {stats.get('sla_metrics', {}).get('under_24hr', 0)} | **{sla_rates.get('under_24hr_rate', 0)*100:.1f}%** |",
        "",
    ])

    # По типу клиента
    by_type = stats.get("by_contact_type", {})
    if by_type:
        lines.extend([
            "## По типу клиента",
            "",
            "| Тип | Всего | Среднее FRT | Медиана FRT | Конверсия |",
            "|-----|-------|-------------|-------------|-----------|",
        ])
        type_names = {
            "direct": "Прямой клиент",
            "agent": "Турагент",
            "supplier": "Поставщик",
            "employee": "Сотрудник",
        }
        for ct, data in sorted(by_type.items()):
            name = type_names.get(ct, ct)
            lines.append(
                f"| {name} | {data['total']} | {data['avg_frt']:.1f} мин | "
                f"{data['median_frt']:.1f} мин | {data['conversion_rate']*100:.1f}% |"
            )
        lines.append("")

    # По времени суток
    by_period = stats.get("by_time_period", {})
    if by_period:
        lines.extend([
            "## По времени суток",
            "",
            "| Период | Запросов | Среднее FRT | Медиана FRT |",
            "|--------|----------|-------------|-------------|",
        ])
        period_order = ["morning", "afternoon", "evening", "night"]
        for period in period_order:
            if period in by_period:
                data = by_period[period]
                lines.append(
                    f"| {data['name_ru']} | {data['total']} | "
                    f"{data['avg_frt']:.1f} мин | {data['median_frt']:.1f} мин |"
                )
        lines.append("")

    # По дню недели
    by_day = stats.get("by_day_of_week", {})
    if by_day:
        lines.extend([
            "## По дню недели",
            "",
            "| День | Запросов | Среднее FRT | Медиана FRT |",
            "|------|----------|-------------|-------------|",
        ])
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in day_order:
            if day in by_day:
                data = by_day[day]
                lines.append(
                    f"| {data['name_ru']} | {data['total']} | "
                    f"{data['avg_frt']:.1f} мин | {data['median_frt']:.1f} мин |"
                )
        lines.append("")

    # Влияние на конверсию
    conv_impact = stats.get("conversion_impact", {})
    if conv_impact:
        lines.extend([
            "## Влияние FRT на конверсию",
            "",
            "| Показатель | Сконвертированные | Не сконвертированные |",
            "|------------|-------------------|----------------------|",
            f"| Количество | {conv_impact.get('converted_count', 0)} | {conv_impact.get('not_converted_count', 0)} |",
            f"| Среднее FRT | {conv_impact.get('converted_avg_frt', 0):.1f} мин | {conv_impact.get('not_converted_avg_frt', 0):.1f} мин |",
            f"| Медиана FRT | {conv_impact.get('converted_median_frt', 0):.1f} мин | {conv_impact.get('not_converted_median_frt', 0):.1f} мин |",
            "",
        ])

    # Конверсия по квартилям FRT
    quartiles = stats.get("quartile_conversion", {})
    if quartiles:
        lines.extend([
            "### Конверсия по скорости ответа",
            "",
            "| Квартиль | Диапазон FRT | Всего | Конверсия |",
            "|----------|--------------|-------|-----------|",
        ])
        for q_name, q_data in quartiles.items():
            lines.append(
                f"| {q_name} | {q_data.get('range', '')} | "
                f"{q_data.get('total', 0)} | {q_data.get('conversion_rate', 0)*100:.1f}% |"
            )
        lines.append("")

    # Сравнение с бенчмарками
    if benchmarks:
        lines.extend([
            "## Сравнение с Industry Benchmarks",
            "",
        ])
        for bench_name, bench_data in benchmarks.items():
            status = "PASS" if bench_data.get("meets_benchmark") else "FAIL"
            lines.append(f"### {bench_name.replace('_', ' ').title()} [{status}]")
            lines.append(f"_Источник: {bench_data.get('source', 'N/A')}_")
            lines.append("")
            lines.append("| Метрика | Наше значение | Бенчмарк | Разница |")
            lines.append("|---------|---------------|----------|---------|")

            for metric_name, metric in bench_data.get("metrics", {}).items():
                better_mark = "+" if metric.get("better") else "-"
                our_val = metric.get("our_value", 0)
                bench_val = metric.get("benchmark", 0)
                diff = metric.get("difference", 0)

                # Форматирование значений
                if "rate" in metric_name:
                    our_str = f"{our_val*100:.1f}%"
                    bench_str = f"{bench_val*100:.1f}%"
                    diff_str = f"{diff*100:+.1f}%"
                else:
                    our_str = f"{our_val:.1f} мин"
                    bench_str = f"{bench_val:.1f} мин"
                    diff_str = f"{diff:+.1f} мин"

                lines.append(f"| {metric_name} | {our_str} | {bench_str} | {better_mark} {diff_str} |")

            lines.append("")

    # Алерты
    if alerts:
        lines.extend([
            "## Алерты",
            "",
            f"Всего алертов: **{len(alerts)}**",
            "",
        ])

        critical_alerts = [a for a in alerts if a.severity == "critical"]
        warning_alerts = [a for a in alerts if a.severity == "warning"]

        if critical_alerts:
            lines.append("### Критические")
            lines.append("")
            for a in critical_alerts[:20]:  # Топ-20
                lines.append(f"- **{a.chat_name or a.jid}**: {a.message}")
            if len(critical_alerts) > 20:
                lines.append(f"- _...и ещё {len(critical_alerts) - 20} алертов_")
            lines.append("")

        if warning_alerts:
            lines.append("### Предупреждения")
            lines.append("")
            for a in warning_alerts[:20]:
                lines.append(f"- {a.chat_name or a.jid}: {a.message}")
            if len(warning_alerts) > 20:
                lines.append(f"- _...и ещё {len(warning_alerts) - 20} алертов_")
            lines.append("")

    # Рекомендации
    lines.extend([
        "## Рекомендации",
        "",
    ])

    median_frt = overall.get("median_frt_minutes", 0)
    response_rate = overall.get("response_rate", 0)
    under_5min = sla_rates.get("under_5min_rate", 0)

    if median_frt > 60:
        lines.append("1. **Медиана FRT > 1 часа** - рассмотрите автоответчики или увеличение штата")
    if response_rate < 0.85:
        lines.append("2. **Response Rate < 85%** - настройте напоминания о неотвеченных сообщениях")
    if under_5min < 0.15:
        lines.append("3. **Мало быстрых ответов** - используйте шаблоны для типовых вопросов")

    # Лучшие практики
    lines.extend([
        "",
        "### Общие рекомендации:",
        "- Настройте автоответ для нерабочего времени",
        "- Используйте шаблоны для частых вопросов",
        "- Приоритизируйте агентские запросы (B2B)",
        "- Отслеживайте SLA метрики еженедельно",
        "",
    ])

    lines.append("---")
    lines.append(f"_SLA пороги: отлично < {SLA_THRESHOLDS['excellent']} мин, "
                 f"приемлемо < {SLA_THRESHOLDS['acceptable']} мин, "
                 f"критично < {SLA_THRESHOLDS['critical']} мин_")

    return "\n".join(lines)


def export_to_csv(records: List[FirstResponseRecord], output_path: Path):
    """Экспортировать записи в CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "jid", "chat_name", "contact_type",
        "first_client_msg_time", "first_response_time",
        "frt_minutes", "sla_level", "day_of_week", "hour",
        "time_period", "converted"
    ]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in records:
            row = {
                "jid": r.jid,
                "chat_name": r.chat_name or "",
                "contact_type": r.contact_type,
                "first_client_msg_time": r.first_client_msg_time.isoformat() if r.first_client_msg_time else "",
                "first_response_time": r.first_response_time.isoformat() if r.first_response_time else "",
                "frt_minutes": round(r.frt_minutes, 2) if r.frt_minutes else "",
                "sla_level": r.sla_level,
                "day_of_week": r.day_of_week,
                "hour": r.hour,
                "time_period": r.time_period,
                "converted": "Yes" if r.converted else "No",
            }
            writer.writerow(row)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Анализ времени первого ответа (First Response Time)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python first_response_time.py
  python first_response_time.py --max-wait 48
  python first_response_time.py --output-json custom.json --output-csv custom.csv
        """
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=RAW_DIR / "all_messages.jsonl",
        help="Путь к входному JSONL файлу"
    )
    parser.add_argument(
        "--contacts", "-c",
        type=Path,
        default=JSON_DIR / "contacts.json",
        help="Путь к файлу контактов"
    )
    parser.add_argument(
        "--funnel", "-f",
        type=Path,
        default=JSON_DIR / "sales_funnel.json",
        help="Путь к файлу воронки продаж"
    )
    parser.add_argument(
        "--output-json", "-oj",
        type=Path,
        default=JSON_DIR / "first_response_time.json",
        help="Путь к выходному JSON файлу"
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=CSV_DIR / "first_response_time.csv",
        help="Путь к выходному CSV файлу"
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=MD_DIR / "время_первого_ответа.md",
        help="Путь к выходному Markdown файлу"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=72,
        help="Макс. время ожидания ответа в часах (по умолчанию: 72)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("АНАЛИЗ ВРЕМЕНИ ПЕРВОГО ОТВЕТА (FRT)")
    print("=" * 60)

    # Создать директории
    ensure_directories()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)

    # Загрузка данных
    print("\n[1] Загрузка данных...")
    messages = load_messages(args.input)
    print(f"    Сообщений: {len(messages):,}")

    contacts = load_contacts(args.contacts)
    print(f"    Контактов: {len(contacts):,}")

    funnel_stages = load_sales_funnel(args.funnel)
    print(f"    Данных воронки: {len(funnel_stages):,}")

    if not messages:
        print("[ОШИБКА] Нет сообщений для анализа")
        sys.exit(1)

    # Расчёт FRT
    print("\n[2] Расчёт времени первого ответа...")
    records, alerts = calculate_first_response_times(
        messages, contacts, funnel_stages, args.max_wait
    )
    print(f"    Записей: {len(records):,}")
    print(f"    Алертов: {len(alerts):,}")

    # Агрегация статистики
    print("\n[3] Агрегация статистики...")
    stats = aggregate_statistics(records)

    # Сравнение с бенчмарками
    print("\n[4] Сравнение с бенчмарками...")
    benchmarks = compare_with_benchmarks(stats)

    # Вывод ключевых метрик
    overall = stats.get("overall", {})
    sla_rates = stats.get("sla_rates", {})

    print("\n" + "-" * 40)
    print("КЛЮЧЕВЫЕ МЕТРИКИ:")
    print("-" * 40)
    print(f"  Всего контактов:     {overall.get('total_contacts', 0):,}")
    print(f"  Response Rate:       {overall.get('response_rate', 0)*100:.1f}%")
    print(f"  Медиана FRT:         {overall.get('median_frt_minutes', 0):.1f} мин")
    print(f"  < 5 мин:             {sla_rates.get('under_5min_rate', 0)*100:.1f}%")
    print(f"  < 1 час:             {sla_rates.get('under_1hr_rate', 0)*100:.1f}%")
    print(f"  < 24 часа:           {sla_rates.get('under_24hr_rate', 0)*100:.1f}%")

    # Проверка бенчмарков
    for bench_name, bench_data in benchmarks.items():
        status = "PASS" if bench_data.get("meets_benchmark") else "FAIL"
        print(f"  {bench_name}: [{status}]")

    # Подготовка данных для JSON
    output_data = {
        "statistics": stats,
        "benchmarks": benchmarks,
        "alerts": [asdict(a) for a in alerts],
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "input_file": str(args.input),
            "total_records": len(records),
            "total_alerts": len(alerts),
            "max_wait_hours": args.max_wait,
            "sla_thresholds": SLA_THRESHOLDS,
        }
    }

    # Сохранение JSON
    print(f"\n[5] Сохранение JSON: {args.output_json}")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Сохранение CSV
    print(f"    Сохранение CSV: {args.output_csv}")
    export_to_csv(records, args.output_csv)

    # Сохранение Markdown
    print(f"    Сохранение Markdown: {args.output_md}")
    md_report = generate_markdown_report(stats, alerts, benchmarks)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md_report)

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)
    print(f"  JSON: {args.output_json}")
    print(f"  CSV:  {args.output_csv}")
    print(f"  MD:   {args.output_md}")


if __name__ == "__main__":
    main()
