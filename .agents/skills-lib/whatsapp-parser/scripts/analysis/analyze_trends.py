#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Анализ трендов активности WhatsApp чатов.

Функции:
1. Агрегация по периодам (дни, недели, месяцы)
2. Метрики: сообщения, новые контакты, активные контакты
3. Рост/падение (% изменения)
4. Выявление сезонности
5. Прогноз (скользящее среднее, линейная экстраполяция)
6. Сравнение периодов (YoY, MoM, WoW)
7. Визуализация (line charts)
8. Экспорт: JSON, PNG, CSV

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/contacts.json (опционально)

Выходные файлы:
- D:/Downloads/Chats/_база/json/trends_analysis.json
- D:/Downloads/Chats/_база/csv/trends_daily.csv
- D:/Downloads/Chats/_база/csv/trends_weekly.csv
- D:/Downloads/Chats/_база/csv/trends_monthly.csv
- D:/Downloads/Chats/_аналитика/trends_*.png
- D:/Downloads/Chats/_база/md/тренды_активности.md

Использование:
    python analyze_trends.py
    python analyze_trends.py --forecast 3  # Прогноз на 3 месяца
    python analyze_trends.py --period weekly  # Только недельный анализ
"""

import json
import sys
import csv
import argparse
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import statistics

sys.stdout.reconfigure(encoding='utf-8')

# Попытка импорта matplotlib для графиков
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import MaxNLocator
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[ПРЕДУПРЕЖДЕНИЕ] matplotlib не установлен. Графики не будут создаваться.")
    print("  Установите: pip install matplotlib")

# Импорт конфигурации
try:
    from config import RAW_DIR, JSON_DIR, CSV_DIR, MD_DIR, ANALYTICS_DIR, ensure_directories
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    CSV_DIR = Path("D:/Downloads/Chats/_база/csv")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")
    ANALYTICS_DIR = Path("D:/Downloads/Chats/_аналитика")

    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        MD_DIR.mkdir(parents=True, exist_ok=True)
        ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


# Константы
MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}

WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def load_messages(filepath: Path) -> List[dict]:
    """Загрузить сообщения из JSONL файла."""
    messages = []

    if not filepath.exists():
        print(f"[ОШИБКА] Файл не найден: {filepath}")
        return messages

    print(f"Загрузка сообщений из {filepath}...")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError as e:
                    if line_num <= 5:
                        print(f"[ОШИБКА] Строка {line_num}: {e}")

                if line_num % 100000 == 0:
                    print(f"  Загружено {line_num:,} строк...")
    except Exception as e:
        print(f"[ОШИБКА] Не удалось прочитать файл: {e}")

    print(f"  Всего загружено: {len(messages):,} сообщений")
    return messages


def load_contacts(filepath: Path) -> List[dict]:
    """Загрузить контакты из JSON файла."""
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def parse_datetime(msg: dict) -> Optional[datetime]:
    """Извлечь datetime из сообщения."""
    dt_str = msg.get("datetime")
    if not dt_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    try:
        return datetime.strptime(dt_str[:10], "%Y-%m-%d")
    except ValueError:
        return None


def get_week_key(dt: datetime) -> str:
    """Получить ключ недели (ISO формат: YYYY-Wxx)."""
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def aggregate_by_period(messages: List[dict]) -> Dict[str, Dict[str, Any]]:
    """
    Агрегация сообщений по периодам.

    Возвращает:
    {
        "daily": { "2024-01-15": {...}, ... },
        "weekly": { "2024-W03": {...}, ... },
        "monthly": { "2024-01": {...}, ... }
    }
    """
    print("\nАгрегация данных по периодам...")

    daily = defaultdict(lambda: {
        "messages": 0,
        "from_me": 0,
        "from_clients": 0,
        "unique_contacts": set(),
        "new_contacts": set(),
    })

    weekly = defaultdict(lambda: {
        "messages": 0,
        "from_me": 0,
        "from_clients": 0,
        "unique_contacts": set(),
        "new_contacts": set(),
    })

    monthly = defaultdict(lambda: {
        "messages": 0,
        "from_me": 0,
        "from_clients": 0,
        "unique_contacts": set(),
        "new_contacts": set(),
    })

    # Отслеживание первого появления контакта
    first_contact_date = {}

    total = len(messages)
    for i, msg in enumerate(messages, 1):
        dt = parse_datetime(msg)
        if not dt:
            continue

        jid = msg.get("jid", "")
        is_from_me = msg.get("is_from_me", False)

        day_key = dt.strftime("%Y-%m-%d")
        week_key = get_week_key(dt)
        month_key = dt.strftime("%Y-%m")

        # Обновляем счётчики для всех периодов
        for period_data, key in [(daily, day_key), (weekly, week_key), (monthly, month_key)]:
            period_data[key]["messages"] += 1
            if is_from_me:
                period_data[key]["from_me"] += 1
            else:
                period_data[key]["from_clients"] += 1

            if jid:
                period_data[key]["unique_contacts"].add(jid)

                # Новый контакт?
                if jid not in first_contact_date:
                    first_contact_date[jid] = day_key
                    period_data[key]["new_contacts"].add(jid)

        if i % 100000 == 0:
            print(f"  Обработано {i:,}/{total:,} сообщений...")

    print(f"  Дней: {len(daily)}, Недель: {len(weekly)}, Месяцев: {len(monthly)}")

    return {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "first_contact_date": first_contact_date,
    }


def calculate_changes(data: Dict[str, dict], sorted_keys: List[str]) -> List[dict]:
    """
    Рассчитать изменения между периодами.

    Возвращает список с данными и % изменений.
    """
    result = []

    for i, key in enumerate(sorted_keys):
        period = data[key]

        entry = {
            "period": key,
            "messages": period["messages"],
            "from_me": period["from_me"],
            "from_clients": period["from_clients"],
            "unique_contacts": len(period["unique_contacts"]),
            "new_contacts": len(period["new_contacts"]),
            "change_pct": 0.0,
            "change_abs": 0,
        }

        # Изменение относительно предыдущего периода
        if i > 0:
            prev_key = sorted_keys[i - 1]
            prev_msgs = data[prev_key]["messages"]
            if prev_msgs > 0:
                entry["change_pct"] = round((period["messages"] - prev_msgs) / prev_msgs * 100, 1)
            entry["change_abs"] = period["messages"] - prev_msgs

        result.append(entry)

    return result


def calculate_yoy(data: Dict[str, dict], sorted_keys: List[str]) -> Dict[str, float]:
    """
    Рассчитать Year-over-Year изменения для месячных данных.

    Возвращает словарь {month_key: yoy_change_pct}.
    """
    yoy = {}

    for key in sorted_keys:
        if "-" not in key or len(key) != 7:  # Формат YYYY-MM
            continue

        year, month = key.split("-")
        prev_year_key = f"{int(year) - 1}-{month}"

        if prev_year_key in data:
            current = data[key]["messages"]
            prev = data[prev_year_key]["messages"]
            if prev > 0:
                yoy[key] = round((current - prev) / prev * 100, 1)
            else:
                yoy[key] = None
        else:
            yoy[key] = None

    return yoy


def calculate_wow(data: Dict[str, dict], sorted_keys: List[str]) -> Dict[str, float]:
    """
    Рассчитать Week-over-Week изменения для недельных данных.

    Возвращает словарь {week_key: wow_change_pct}.
    """
    wow = {}

    for i, key in enumerate(sorted_keys):
        if i > 0:
            prev_key = sorted_keys[i - 1]
            current = data[key]["messages"]
            prev = data[prev_key]["messages"]
            if prev > 0:
                wow[key] = round((current - prev) / prev * 100, 1)
            else:
                wow[key] = None
        else:
            wow[key] = None

    return wow


def detect_seasonality(monthly_data: Dict[str, dict]) -> Dict[str, Any]:
    """
    Выявить сезонные паттерны.

    Анализирует среднюю активность по месяцам года.
    """
    print("\nАнализ сезонности...")

    by_month_of_year = defaultdict(list)

    for key, data in monthly_data.items():
        if "-" in key and len(key) == 7:
            month_num = int(key.split("-")[1])
            by_month_of_year[month_num].append(data["messages"])

    # Средняя активность по месяцам
    avg_by_month = {}
    for month_num in range(1, 13):
        values = by_month_of_year.get(month_num, [])
        if values:
            avg_by_month[month_num] = {
                "avg": round(statistics.mean(values), 0),
                "min": min(values),
                "max": max(values),
                "samples": len(values),
            }
        else:
            avg_by_month[month_num] = None

    # Определение пиковых и низких месяцев
    valid_months = {k: v for k, v in avg_by_month.items() if v is not None}

    if not valid_months:
        return {"error": "Недостаточно данных"}

    avg_values = [v["avg"] for v in valid_months.values()]
    overall_avg = statistics.mean(avg_values)

    peak_months = [m for m, v in valid_months.items() if v["avg"] > overall_avg * 1.2]
    low_months = [m for m, v in valid_months.items() if v["avg"] < overall_avg * 0.8]

    # Индекс сезонности (отношение к среднему)
    seasonality_index = {}
    for month_num, data in valid_months.items():
        seasonality_index[month_num] = round(data["avg"] / overall_avg, 2)

    return {
        "by_month": avg_by_month,
        "overall_avg": round(overall_avg, 0),
        "peak_months": [MONTHS_RU.get(m, m) for m in peak_months],
        "low_months": [MONTHS_RU.get(m, m) for m in low_months],
        "seasonality_index": seasonality_index,
    }


def calculate_moving_average(values: List[float], window: int = 3) -> List[Optional[float]]:
    """Рассчитать скользящее среднее."""
    result = []

    for i in range(len(values)):
        if i < window - 1:
            result.append(None)
        else:
            window_values = values[i - window + 1:i + 1]
            result.append(round(statistics.mean(window_values), 0))

    return result


def forecast_linear(values: List[float], periods: int = 3) -> List[float]:
    """
    Простой линейный прогноз на основе последних данных.

    Использует линейную регрессию по последним 6 точкам.
    """
    if len(values) < 3:
        return []

    # Берём последние 6 значений для расчёта тренда
    recent = values[-6:] if len(values) >= 6 else values
    n = len(recent)

    # Простая линейная регрессия: y = a + b*x
    x_mean = (n - 1) / 2
    y_mean = statistics.mean(recent)

    numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        b = 0
    else:
        b = numerator / denominator

    a = y_mean - b * x_mean

    # Прогноз
    forecast = []
    for i in range(periods):
        predicted = a + b * (n + i)
        forecast.append(max(0, round(predicted, 0)))  # Не меньше 0

    return forecast


def forecast_moving_average(values: List[float], periods: int = 3) -> List[float]:
    """
    Прогноз на основе скользящего среднего.
    """
    if len(values) < 3:
        return []

    # Берём среднее последних 3 значений
    recent_avg = statistics.mean(values[-3:])

    # Рост за последние 3 периода
    if len(values) >= 6:
        prev_avg = statistics.mean(values[-6:-3])
        growth_rate = (recent_avg - prev_avg) / prev_avg if prev_avg > 0 else 0
    else:
        growth_rate = 0

    # Умеренный прогноз с затуханием роста
    forecast = []
    last_value = recent_avg
    for i in range(periods):
        # Затухание роста со временем
        dampening = 0.7 ** i
        growth = growth_rate * dampening
        predicted = last_value * (1 + growth)
        forecast.append(max(0, round(predicted, 0)))
        last_value = predicted

    return forecast


def compare_periods(
    data: Dict[str, dict],
    period1_keys: List[str],
    period2_keys: List[str]
) -> Dict[str, Any]:
    """
    Сравнить два набора периодов.

    Возвращает статистику сравнения.
    """
    def get_totals(keys):
        total_msgs = sum(data[k]["messages"] for k in keys if k in data)
        total_contacts = len(set().union(*[data[k]["unique_contacts"] for k in keys if k in data]))
        total_new = len(set().union(*[data[k]["new_contacts"] for k in keys if k in data]))
        return {
            "messages": total_msgs,
            "unique_contacts": total_contacts,
            "new_contacts": total_new,
            "avg_messages": round(total_msgs / len(keys), 0) if keys else 0,
        }

    p1 = get_totals(period1_keys)
    p2 = get_totals(period2_keys)

    # Расчёт изменений
    changes = {}
    for metric in ["messages", "unique_contacts", "new_contacts"]:
        if p1[metric] > 0:
            changes[metric] = round((p2[metric] - p1[metric]) / p1[metric] * 100, 1)
        else:
            changes[metric] = None

    return {
        "period1": p1,
        "period2": p2,
        "changes": changes,
    }


def generate_trend_charts(
    aggregated: Dict[str, Dict[str, Any]],
    output_dir: Path,
    forecast_months: int = 3
):
    """Генерация графиков трендов."""
    if not MATPLOTLIB_AVAILABLE:
        print("\n[ПРОПУСК] Графики не генерируются (matplotlib не установлен)")
        return

    print(f"\nГенерация графиков в {output_dir}...")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Настройка стиля
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'ggplot')
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['figure.dpi'] = 100

    # 1. График по месяцам
    monthly = aggregated["monthly"]
    sorted_months = sorted(monthly.keys())

    if len(sorted_months) >= 3:
        dates = [datetime.strptime(k, "%Y-%m") for k in sorted_months]
        messages = [monthly[k]["messages"] for k in sorted_months]
        new_contacts = [len(monthly[k]["new_contacts"]) for k in sorted_months]

        # Скользящее среднее
        ma = calculate_moving_average(messages, window=3)

        # Прогноз
        forecast = forecast_moving_average(messages, periods=forecast_months)
        forecast_dates = [dates[-1] + timedelta(days=30 * (i + 1)) for i in range(len(forecast))]

        fig, ax1 = plt.subplots()

        # Сообщения
        ax1.plot(dates, messages, 'b-', linewidth=2, label='Сообщения', marker='o', markersize=4)
        ax1.plot(dates, ma, 'b--', linewidth=1, alpha=0.7, label='MA(3)')

        # Прогноз
        if forecast:
            ax1.plot(forecast_dates, forecast, 'b:', linewidth=2, alpha=0.5, label='Прогноз')
            ax1.scatter(forecast_dates, forecast, color='blue', alpha=0.3, s=50)

        ax1.set_xlabel('Месяц')
        ax1.set_ylabel('Сообщения', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(MaxNLocator(nbins=12))
        plt.xticks(rotation=45)

        # Новые контакты (вторая ось)
        ax2 = ax1.twinx()
        ax2.bar(dates, new_contacts, alpha=0.3, color='green', width=20, label='Новые контакты')
        ax2.set_ylabel('Новые контакты', color='green')
        ax2.tick_params(axis='y', labelcolor='green')

        plt.title('Тренды активности (по месяцам)')

        # Объединённая легенда
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.tight_layout()
        plt.savefig(output_dir / "trends_monthly.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Сохранён: trends_monthly.png")

    # 2. График по неделям (последние 12 недель)
    weekly = aggregated["weekly"]
    sorted_weeks = sorted(weekly.keys())[-12:]

    if len(sorted_weeks) >= 4:
        # Преобразуем недельные ключи в даты (понедельник недели)
        week_dates = []
        for wk in sorted_weeks:
            year, week_num = wk.split("-W")
            # Первый день ISO недели
            first_day = datetime.strptime(f"{year}-W{week_num}-1", "%Y-W%W-%w")
            week_dates.append(first_day)

        messages = [weekly[k]["messages"] for k in sorted_weeks]

        fig, ax = plt.subplots()
        ax.bar(week_dates, messages, width=5, color='steelblue', alpha=0.8)
        ax.plot(week_dates, messages, 'r-', linewidth=1.5, marker='o', markersize=4)

        ax.set_xlabel('Неделя')
        ax.set_ylabel('Сообщения')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.xticks(rotation=45)
        plt.title('Активность по неделям (последние 12 недель)')
        plt.tight_layout()
        plt.savefig(output_dir / "trends_weekly.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Сохранён: trends_weekly.png")

    # 3. График сезонности
    seasonality = detect_seasonality(monthly)

    if "by_month" in seasonality and not seasonality.get("error"):
        months = list(range(1, 13))
        month_names = [MONTHS_RU[m][:3] for m in months]

        avgs = []
        for m in months:
            data = seasonality["by_month"].get(m)
            avgs.append(data["avg"] if data else 0)

        fig, ax = plt.subplots()
        bars = ax.bar(month_names, avgs, color='coral', alpha=0.8)

        # Выделение пиковых месяцев
        overall_avg = seasonality.get("overall_avg", 0)
        for i, bar in enumerate(bars):
            if avgs[i] > overall_avg * 1.2:
                bar.set_color('crimson')
            elif avgs[i] < overall_avg * 0.8:
                bar.set_color('lightcoral')

        ax.axhline(y=overall_avg, color='gray', linestyle='--', label=f'Среднее: {overall_avg:,.0f}')
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Среднее кол-во сообщений')
        ax.legend()
        plt.title('Сезонность активности')
        plt.tight_layout()
        plt.savefig(output_dir / "trends_seasonality.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Сохранён: trends_seasonality.png")

    # 4. График YoY изменений
    sorted_months = sorted(monthly.keys())
    yoy = calculate_yoy(monthly, sorted_months)

    valid_yoy = [(k, v) for k, v in yoy.items() if v is not None]
    if len(valid_yoy) >= 3:
        yoy_months = [k for k, v in valid_yoy]
        yoy_values = [v for k, v in valid_yoy]
        yoy_dates = [datetime.strptime(k, "%Y-%m") for k in yoy_months]

        fig, ax = plt.subplots()

        colors = ['green' if v >= 0 else 'red' for v in yoy_values]
        ax.bar(yoy_dates, yoy_values, width=25, color=colors, alpha=0.7)
        ax.axhline(y=0, color='black', linewidth=0.5)

        ax.set_xlabel('Месяц')
        ax.set_ylabel('Изменение YoY (%)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        plt.title('Год к году (YoY) изменения')
        plt.tight_layout()
        plt.savefig(output_dir / "trends_yoy.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Сохранён: trends_yoy.png")


def export_csv(aggregated: Dict[str, Dict[str, Any]], output_dir: Path):
    """Экспорт данных в CSV файлы."""
    print(f"\nЭкспорт CSV в {output_dir}...")
    output_dir.mkdir(parents=True, exist_ok=True)

    headers = ["period", "messages", "from_me", "from_clients", "unique_contacts", "new_contacts", "change_pct"]

    for period_name in ["daily", "weekly", "monthly"]:
        data = aggregated[period_name]
        sorted_keys = sorted(data.keys())

        if not sorted_keys:
            continue

        rows = calculate_changes(data, sorted_keys)

        filepath = output_dir / f"trends_{period_name}.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in headers})

        print(f"  Сохранён: trends_{period_name}.csv ({len(rows)} записей)")


def build_output_json(
    aggregated: Dict[str, Dict[str, Any]],
    forecast_months: int = 3
) -> Dict[str, Any]:
    """Сформировать итоговый JSON."""

    monthly = aggregated["monthly"]
    weekly = aggregated["weekly"]
    daily = aggregated["daily"]

    sorted_months = sorted(monthly.keys())
    sorted_weeks = sorted(weekly.keys())
    sorted_days = sorted(daily.keys())

    # Расчёт изменений
    monthly_changes = calculate_changes(monthly, sorted_months)
    weekly_changes = calculate_changes(weekly, sorted_weeks)

    # YoY и WoW
    yoy = calculate_yoy(monthly, sorted_months)
    wow = calculate_wow(weekly, sorted_weeks)

    # Сезонность
    seasonality = detect_seasonality(monthly)

    # Прогноз
    messages_monthly = [monthly[k]["messages"] for k in sorted_months]
    forecast_linear_values = forecast_linear(messages_monthly, forecast_months)
    forecast_ma_values = forecast_moving_average(messages_monthly, forecast_months)

    # Даты прогноза
    if sorted_months:
        last_month = datetime.strptime(sorted_months[-1], "%Y-%m")
        forecast_periods = []
        for i in range(forecast_months):
            next_month = last_month + timedelta(days=30 * (i + 1))
            forecast_periods.append(next_month.strftime("%Y-%m"))
    else:
        forecast_periods = []

    # Общая статистика
    total_messages = sum(d["messages"] for d in monthly.values())
    total_contacts = len(aggregated.get("first_contact_date", {}))

    # Тренд (направление)
    if len(monthly_changes) >= 3:
        recent_changes = [c["change_pct"] for c in monthly_changes[-3:]]
        avg_change = statistics.mean(recent_changes)
        if avg_change > 5:
            trend_direction = "up"
        elif avg_change < -5:
            trend_direction = "down"
        else:
            trend_direction = "stable"
    else:
        trend_direction = "unknown"
        avg_change = 0

    # Сравнение периодов
    comparisons = {}

    # Последний месяц vs предыдущий
    if len(sorted_months) >= 2:
        comparisons["mom"] = compare_periods(
            monthly,
            [sorted_months[-2]],
            [sorted_months[-1]]
        )

    # Последние 3 месяца vs предыдущие 3
    if len(sorted_months) >= 6:
        comparisons["quarter"] = compare_periods(
            monthly,
            sorted_months[-6:-3],
            sorted_months[-3:]
        )

    # YoY за последний месяц
    if sorted_months:
        last_month = sorted_months[-1]
        year, mon = last_month.split("-")
        prev_year_month = f"{int(year) - 1}-{mon}"
        if prev_year_month in monthly:
            comparisons["yoy_last_month"] = compare_periods(
                monthly,
                [prev_year_month],
                [last_month]
            )

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_messages": total_messages,
            "total_contacts": total_contacts,
            "date_range": {
                "from": sorted_days[0] if sorted_days else None,
                "to": sorted_days[-1] if sorted_days else None,
            },
            "trend": {
                "direction": trend_direction,
                "avg_monthly_change_pct": round(avg_change, 1),
            },
        },
        "monthly": {
            "data": monthly_changes[-24:],  # Последние 24 месяца
            "yoy": {k: yoy.get(k) for k in sorted_months[-12:]},  # Последние 12 месяцев
        },
        "weekly": {
            "data": weekly_changes[-12:],  # Последние 12 недель
            "wow": {k: wow.get(k) for k in sorted_weeks[-12:]},
        },
        "seasonality": seasonality,
        "forecast": {
            "periods": forecast_periods,
            "linear": forecast_linear_values,
            "moving_average": forecast_ma_values,
            "method": "moving_average_with_dampening",
        },
        "comparisons": comparisons,
    }


def generate_markdown(output: Dict[str, Any]) -> str:
    """Генерация Markdown отчёта."""
    lines = []

    lines.append("# Анализ трендов активности")
    lines.append("")
    lines.append(f"*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")

    # Сводка
    summary = output.get("summary", {})
    trend = summary.get("trend", {})

    lines.append("## Сводка")
    lines.append("")
    lines.append(f"- **Всего сообщений:** {summary.get('total_messages', 0):,}")
    lines.append(f"- **Контактов:** {summary.get('total_contacts', 0):,}")

    date_range = summary.get("date_range", {})
    if date_range.get("from") and date_range.get("to"):
        lines.append(f"- **Период данных:** {date_range['from']} - {date_range['to']}")

    direction_text = {"up": "^ Рост", "down": "v Падение", "stable": "= Стабильно", "unknown": "? Неизвестно"}
    lines.append(f"- **Тренд:** {direction_text.get(trend.get('direction', 'unknown'), '?')} ({trend.get('avg_monthly_change_pct', 0):+.1f}% в месяц)")
    lines.append("")

    # Тренды по месяцам
    lines.append("## Тренды по месяцам")
    lines.append("")
    lines.append("| Месяц | Сообщения | Новые контакты | Изменение | YoY |")
    lines.append("|-------|-----------|----------------|-----------|-----|")

    monthly_data = output.get("monthly", {}).get("data", [])
    yoy_data = output.get("monthly", {}).get("yoy", {})

    for entry in reversed(monthly_data[-12:]):
        period = entry["period"]
        msgs = entry["messages"]
        new_contacts = entry.get("new_contacts", 0)
        change = entry.get("change_pct", 0)
        change_str = f"{change:+.1f}%" if change != 0 else "-"

        yoy_val = yoy_data.get(period)
        yoy_str = f"{yoy_val:+.1f}%" if yoy_val is not None else "-"

        lines.append(f"| {period} | {msgs:,} | {new_contacts} | {change_str} | {yoy_str} |")

    lines.append("")

    # Прогноз
    forecast = output.get("forecast", {})
    if forecast.get("periods"):
        lines.append("## Прогноз")
        lines.append("")
        lines.append("| Период | Прогноз (MA) | Прогноз (Linear) |")
        lines.append("|--------|--------------|------------------|")

        for i, period in enumerate(forecast["periods"]):
            ma_val = forecast.get("moving_average", [])[i] if i < len(forecast.get("moving_average", [])) else "-"
            linear_val = forecast.get("linear", [])[i] if i < len(forecast.get("linear", [])) else "-"

            ma_str = f"{ma_val:,.0f}" if isinstance(ma_val, (int, float)) else "-"
            linear_str = f"{linear_val:,.0f}" if isinstance(linear_val, (int, float)) else "-"

            lines.append(f"| {period} | {ma_str} | {linear_str} |")

        lines.append("")
        lines.append(f"*Метод: {forecast.get('method', 'n/a')}*")
        lines.append("")

    # Сезонность
    seasonality = output.get("seasonality", {})
    if seasonality and not seasonality.get("error"):
        lines.append("## Сезонность")
        lines.append("")

        peak = seasonality.get("peak_months", [])
        low = seasonality.get("low_months", [])

        if peak:
            lines.append(f"- **Пиковые месяцы:** {', '.join(peak)}")
        if low:
            lines.append(f"- **Низкие месяцы:** {', '.join(low)}")

        lines.append(f"- **Средняя активность:** {seasonality.get('overall_avg', 0):,.0f} сообщений/месяц")
        lines.append("")

        # Индекс сезонности
        lines.append("### Индекс сезонности")
        lines.append("")
        lines.append("| Месяц | Индекс |")
        lines.append("|-------|--------|")

        index = seasonality.get("seasonality_index", {})
        for m in range(1, 13):
            idx = index.get(m)
            idx_str = f"{idx:.2f}" if idx else "-"
            bar = "#" * int((idx or 0) * 10) if idx else ""
            lines.append(f"| {MONTHS_RU[m]} | {idx_str} {bar} |")

        lines.append("")

    # Сравнение периодов
    comparisons = output.get("comparisons", {})
    if comparisons:
        lines.append("## Сравнение периодов")
        lines.append("")

        for comp_name, comp_data in comparisons.items():
            if comp_name == "mom":
                title = "Месяц к месяцу (MoM)"
            elif comp_name == "quarter":
                title = "Квартал к кварталу"
            elif comp_name == "yoy_last_month":
                title = "Год к году (YoY) за последний месяц"
            else:
                title = comp_name

            lines.append(f"### {title}")
            lines.append("")

            changes = comp_data.get("changes", {})
            p1 = comp_data.get("period1", {})
            p2 = comp_data.get("period2", {})

            lines.append(f"- Сообщения: {p1.get('messages', 0):,} -> {p2.get('messages', 0):,} ({changes.get('messages', 0):+.1f}%)")
            lines.append(f"- Контакты: {p1.get('unique_contacts', 0):,} -> {p2.get('unique_contacts', 0):,}")
            lines.append(f"- Новые: {p1.get('new_contacts', 0)} -> {p2.get('new_contacts', 0)}")
            lines.append("")

    # Графики
    lines.append("## Графики")
    lines.append("")
    lines.append("Графики сохранены в папке `_аналитика/`:")
    lines.append("")
    lines.append("- `trends_monthly.png` - Тренды по месяцам с прогнозом")
    lines.append("- `trends_weekly.png` - Активность по неделям")
    lines.append("- `trends_seasonality.png` - Сезонность")
    lines.append("- `trends_yoy.png` - Изменения год к году")
    lines.append("")

    # Подвал
    lines.append("---")
    lines.append("")
    lines.append("*Отчёт сгенерирован скриптом analyze_trends.py*")

    return "\n".join(lines)


def main():
    """Основная функция."""

    parser = argparse.ArgumentParser(description="Анализ трендов активности WhatsApp чатов")
    parser.add_argument("--forecast", type=int, default=3, help="Количество месяцев для прогноза (по умолчанию: 3)")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly", "all"], default="all",
                        help="Какие периоды анализировать")
    parser.add_argument("--no-charts", action="store_true", help="Не генерировать графики")
    args = parser.parse_args()

    print("=" * 60)
    print("АНАЛИЗ ТРЕНДОВ АКТИВНОСТИ")
    print("=" * 60)

    # Создание директорий
    ensure_directories()

    # Пути к файлам
    messages_file = RAW_DIR / "all_messages.jsonl"
    contacts_file = JSON_DIR / "contacts.json"

    output_json = JSON_DIR / "trends_analysis.json"
    output_md = MD_DIR / "тренды_активности.md"
    charts_dir = ANALYTICS_DIR
    csv_dir = CSV_DIR

    print(f"\nВходные файлы:")
    print(f"  - Сообщения: {messages_file}")
    print(f"  - Контакты: {contacts_file}")

    print(f"\nВыходные файлы:")
    print(f"  - JSON: {output_json}")
    print(f"  - Markdown: {output_md}")
    print(f"  - CSV: {csv_dir}/trends_*.csv")
    print(f"  - Графики: {charts_dir}/trends_*.png")
    print()

    # Загрузка данных
    messages = load_messages(messages_file)

    if not messages:
        print("\n[ОШИБКА] Сообщения не найдены!")
        print("Сначала запустите parse_all_chats.py для создания all_messages.jsonl")
        return

    contacts = load_contacts(contacts_file)

    # Агрегация
    aggregated = aggregate_by_period(messages)

    # Генерация выходных данных
    output = build_output_json(aggregated, forecast_months=args.forecast)

    # Сохранение JSON
    print(f"\nСохранение JSON: {output_json}")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Экспорт CSV
    export_csv(aggregated, csv_dir)

    # Генерация графиков
    if not args.no_charts:
        generate_trend_charts(aggregated, charts_dir, forecast_months=args.forecast)

    # Генерация Markdown
    print(f"\nГенерация Markdown: {output_md}")
    md_content = generate_markdown(output)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)

    summary = output.get("summary", {})
    trend = summary.get("trend", {})

    print(f"Сообщений обработано: {summary.get('total_messages', 0):,}")
    print(f"Контактов: {summary.get('total_contacts', 0):,}")
    print(f"Тренд: {trend.get('direction', 'unknown')} ({trend.get('avg_monthly_change_pct', 0):+.1f}%/мес)")

    forecast = output.get("forecast", {})
    if forecast.get("moving_average"):
        print(f"\nПрогноз на {args.forecast} мес.: {forecast['moving_average']}")

    print(f"\nФайлы сохранены:")
    print(f"  - {output_json}")
    print(f"  - {output_md}")
    for period in ["daily", "weekly", "monthly"]:
        csv_file = csv_dir / f"trends_{period}.csv"
        if csv_file.exists():
            print(f"  - {csv_file}")

    if not args.no_charts and MATPLOTLIB_AVAILABLE:
        for chart in ["monthly", "weekly", "seasonality", "yoy"]:
            chart_file = charts_dir / f"trends_{chart}.png"
            if chart_file.exists():
                print(f"  - {chart_file}")


if __name__ == "__main__":
    main()
