#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Анализ времени активности контактов в WhatsApp чатах.

Функции:
1. Распределение сообщений по часам
2. Распределение по дням недели
3. Тепловая карта (час x день)
4. Определение "активных часов" контакта
5. Лучшее время для связи
6. Выходные vs будни
7. Сезонность (месяцы)
8. Визуализация (heatmap, bar charts)
9. Экспорт: JSON, PNG, HTML

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl

Выходные файлы:
- D:/Downloads/Chats/_база/json/activity_time_analysis.json
- D:/Downloads/Chats/_база/md/анализ_времени_активности.md
- D:/Downloads/Chats/_аналитика/activity_heatmap.png
- D:/Downloads/Chats/_аналитика/activity_hours.png
- D:/Downloads/Chats/_аналитика/activity_weekdays.png
- D:/Downloads/Chats/_аналитика/activity_monthly.png
- D:/Downloads/Chats/_аналитика/activity_dashboard.html
"""

import json
import sys
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import RAW_DIR, JSON_DIR, MD_DIR, ANALYTICS_DIR, ensure_directories
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")
    ANALYTICS_DIR = Path("D:/Downloads/Chats/_аналитика")

    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        MD_DIR.mkdir(parents=True, exist_ok=True)
        ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

# Попытка импорта библиотек визуализации
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("[ПРЕДУПРЕЖДЕНИЕ] pandas не установлен. pip install pandas")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[ПРЕДУПРЕЖДЕНИЕ] numpy не установлен. pip install numpy")

try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Для работы без GUI
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    print("[ПРЕДУПРЕЖДЕНИЕ] seaborn/matplotlib не установлены. pip install seaborn matplotlib")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[ПРЕДУПРЕЖДЕНИЕ] plotly не установлен. pip install plotly")


# ===============================================================================
# КОНСТАНТЫ
# ===============================================================================

WEEKDAYS_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

WEEKDAYS_SHORT = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс",
}

MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}

# Часовые пояса
TIMEZONE_OFFSET = 4  # UTC+4 для Дубая


# ===============================================================================
# ЗАГРУЗКА ДАННЫХ
# ===============================================================================

def load_messages(filepath: Path) -> List[Dict]:
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
        print(f"[ОШИБКА] Чтение файла: {e}")

    print(f"  Всего загружено: {len(messages):,} сообщений")
    return messages


def parse_datetime(msg: Dict) -> Optional[datetime]:
    """Извлечь datetime из сообщения."""
    dt_str = msg.get("datetime")
    if not dt_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%YT%H:%M:%S",
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


# ===============================================================================
# АНАЛИЗ ДАННЫХ
# ===============================================================================

def analyze_activity(messages: List[Dict], contact_jid: Optional[str] = None) -> Dict:
    """
    Анализ временной активности.

    Args:
        messages: список сообщений
        contact_jid: опционально - фильтр по конкретному контакту
    """
    print("\nАнализ временной активности...")

    # Структуры для накопления
    by_hour = defaultdict(lambda: {"total": 0, "from_me": 0, "from_them": 0})
    by_weekday = defaultdict(lambda: {"total": 0, "from_me": 0, "from_them": 0})
    by_month = defaultdict(lambda: {"total": 0, "from_me": 0, "from_them": 0})
    by_hour_weekday = defaultdict(lambda: defaultdict(int))  # heatmap data

    # Для анализа ответов
    response_times_by_hour = defaultdict(list)  # час -> список времен ответа
    last_message_by_jid = {}

    # Контакт-специфичный анализ
    contacts_activity = defaultdict(lambda: {
        "by_hour": defaultdict(int),
        "by_weekday": defaultdict(int),
        "total_messages": 0,
        "first_message": None,
        "last_message": None,
    })

    total = len(messages)
    processed = 0

    for msg in messages:
        # Фильтр по контакту
        jid = msg.get("jid", "")
        if contact_jid and jid != contact_jid:
            continue

        dt = parse_datetime(msg)
        if not dt:
            continue

        processed += 1
        is_from_me = msg.get("is_from_me", False)

        hour = dt.hour
        weekday = dt.weekday()
        month_key = dt.strftime("%Y-%m")

        # По часам
        by_hour[hour]["total"] += 1
        if is_from_me:
            by_hour[hour]["from_me"] += 1
        else:
            by_hour[hour]["from_them"] += 1

        # По дням недели
        by_weekday[weekday]["total"] += 1
        if is_from_me:
            by_weekday[weekday]["from_me"] += 1
        else:
            by_weekday[weekday]["from_them"] += 1

        # По месяцам
        by_month[month_key]["total"] += 1
        if is_from_me:
            by_month[month_key]["from_me"] += 1
        else:
            by_month[month_key]["from_them"] += 1

        # Тепловая карта
        by_hour_weekday[weekday][hour] += 1

        # Активность по контактам
        if jid:
            contacts_activity[jid]["by_hour"][hour] += 1
            contacts_activity[jid]["by_weekday"][weekday] += 1
            contacts_activity[jid]["total_messages"] += 1

            if contacts_activity[jid]["first_message"] is None:
                contacts_activity[jid]["first_message"] = dt
            contacts_activity[jid]["last_message"] = dt

        # Анализ времени ответа
        if jid:
            if jid in last_message_by_jid:
                last = last_message_by_jid[jid]
                # Если это ответ (смена направления)
                if last["is_from_me"] != is_from_me:
                    time_diff = (dt - last["dt"]).total_seconds() / 60  # минуты
                    if 0 < time_diff < 1440:  # < 24 часов
                        response_times_by_hour[hour].append(time_diff)

            last_message_by_jid[jid] = {"dt": dt, "is_from_me": is_from_me}

        if processed % 100000 == 0:
            print(f"  Обработано {processed:,}/{total:,}...")

    print(f"  Обработано всего: {processed:,} сообщений")

    return {
        "by_hour": dict(by_hour),
        "by_weekday": dict(by_weekday),
        "by_month": dict(by_month),
        "by_hour_weekday": {k: dict(v) for k, v in by_hour_weekday.items()},
        "response_times_by_hour": dict(response_times_by_hour),
        "contacts_activity": dict(contacts_activity),
        "total_processed": processed,
    }


def calculate_best_contact_time(analysis: Dict) -> Dict:
    """Определить лучшее время для связи."""

    by_hour = analysis["by_hour"]
    response_times = analysis["response_times_by_hour"]

    best_hours = []

    for hour in range(24):
        hour_data = by_hour.get(hour, {})
        from_them = hour_data.get("from_them", 0)

        # Среднее время ответа в этот час
        resp_times = response_times.get(hour, [])
        avg_response = sum(resp_times) / len(resp_times) if resp_times else None

        # Рейтинг = активность клиентов / время ответа
        # Чем выше активность и ниже время ответа - тем лучше
        if from_them > 0:
            response_factor = 1 / (avg_response + 1) if avg_response else 0.5
            score = from_them * response_factor
        else:
            score = 0

        best_hours.append({
            "hour": hour,
            "client_messages": from_them,
            "avg_response_min": round(avg_response, 1) if avg_response else None,
            "score": round(score, 2),
        })

    # Сортировка по рейтингу
    best_hours.sort(key=lambda x: x["score"], reverse=True)

    # Top-3 лучших часа
    top_3 = best_hours[:3]

    # Определение "активных окон"
    active_windows = []
    current_window = None

    for hour in range(24):
        from_them = by_hour.get(hour, {}).get("from_them", 0)
        avg_hourly = sum(h.get("from_them", 0) for h in by_hour.values()) / 24 if by_hour else 0

        if from_them > avg_hourly * 1.2:  # > 120% от среднего
            if current_window is None:
                current_window = {"start": hour, "end": hour}
            else:
                current_window["end"] = hour
        else:
            if current_window is not None:
                active_windows.append(current_window)
                current_window = None

    if current_window is not None:
        active_windows.append(current_window)

    return {
        "best_hours": top_3,
        "all_hours_ranked": best_hours,
        "active_windows": active_windows,
        "recommendation": format_recommendation(top_3, active_windows),
    }


def format_recommendation(top_3: List, windows: List) -> str:
    """Форматировать рекомендацию."""
    if not top_3:
        return "Недостаточно данных"

    hours_str = ", ".join(f"{h['hour']}:00" for h in top_3)

    if windows:
        windows_str = ", ".join(f"{w['start']}:00-{w['end']+1}:00" for w in windows)
        return f"Лучшие часы для связи: {hours_str}. Активные окна: {windows_str}"

    return f"Лучшие часы для связи: {hours_str}"


def analyze_weekday_patterns(analysis: Dict) -> Dict:
    """Анализ паттернов по дням недели."""

    by_weekday = analysis["by_weekday"]

    # Будни vs выходные
    weekday_total = sum(by_weekday.get(d, {}).get("total", 0) for d in range(5))
    weekend_total = sum(by_weekday.get(d, {}).get("total", 0) for d in [5, 6])

    weekday_avg = weekday_total / 5 if weekday_total else 0
    weekend_avg = weekend_total / 2 if weekend_total else 0

    if weekday_avg > 0:
        weekend_vs_weekday = round(weekend_avg / weekday_avg, 2)
    else:
        weekend_vs_weekday = 0

    # Самый активный день
    max_day = max(range(7), key=lambda d: by_weekday.get(d, {}).get("total", 0))
    min_day = min(range(7), key=lambda d: by_weekday.get(d, {}).get("total", 0))

    return {
        "weekday_total": weekday_total,
        "weekend_total": weekend_total,
        "weekday_avg_daily": round(weekday_avg, 1),
        "weekend_avg_daily": round(weekend_avg, 1),
        "weekend_vs_weekday_ratio": weekend_vs_weekday,
        "most_active_day": {
            "index": max_day,
            "name": WEEKDAYS_RU[max_day],
            "messages": by_weekday.get(max_day, {}).get("total", 0),
        },
        "least_active_day": {
            "index": min_day,
            "name": WEEKDAYS_RU[min_day],
            "messages": by_weekday.get(min_day, {}).get("total", 0),
        },
    }


def analyze_monthly_patterns(analysis: Dict) -> Dict:
    """Анализ сезонности по месяцам."""

    by_month = analysis["by_month"]

    if not by_month:
        return {"months": [], "trend": "unknown"}

    # Группировка по месяцам года (1-12)
    by_month_of_year = defaultdict(list)
    for month_key, data in by_month.items():
        month_num = int(month_key.split("-")[1])
        by_month_of_year[month_num].append(data["total"])

    # Средняя активность по месяцам года
    monthly_avg = {}
    for month, values in by_month_of_year.items():
        monthly_avg[month] = round(sum(values) / len(values), 1)

    # Тренд (последние 6 месяцев)
    sorted_months = sorted(by_month.keys())
    if len(sorted_months) >= 6:
        first_half = sum(by_month[m]["total"] for m in sorted_months[:3])
        second_half = sum(by_month[m]["total"] for m in sorted_months[-3:])

        if first_half > 0:
            trend_pct = round((second_half - first_half) / first_half * 100, 1)
            trend = "growing" if trend_pct > 10 else "declining" if trend_pct < -10 else "stable"
        else:
            trend_pct = 0
            trend = "unknown"
    else:
        trend_pct = 0
        trend = "unknown"

    # Сезоны
    high_season_months = [10, 11, 12, 1, 2, 3, 4]  # Туристический сезон ОАЭ
    low_season_months = [5, 6, 7, 8, 9]

    high_season_avg = sum(monthly_avg.get(m, 0) for m in high_season_months) / len(high_season_months)
    low_season_avg = sum(monthly_avg.get(m, 0) for m in low_season_months) / len(low_season_months)

    seasonality_ratio = round(high_season_avg / low_season_avg, 2) if low_season_avg > 0 else 0

    return {
        "monthly_average": {MONTHS_RU[m]: v for m, v in monthly_avg.items()},
        "trend": trend,
        "trend_percentage": trend_pct,
        "high_season_avg": round(high_season_avg, 1),
        "low_season_avg": round(low_season_avg, 1),
        "seasonality_ratio": seasonality_ratio,
        "all_months": {k: v for k, v in sorted(by_month.items())},
    }


def analyze_contacts_activity(contacts_activity: Dict, top_n: int = 20) -> List[Dict]:
    """Анализ активности по контактам."""

    result = []

    for jid, data in contacts_activity.items():
        # Top-3 часа для этого контакта
        hours = data["by_hour"]
        top_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]

        # Top-3 дня для этого контакта
        weekdays = data["by_weekday"]
        top_days = sorted(weekdays.items(), key=lambda x: x[1], reverse=True)[:3]

        result.append({
            "jid": jid,
            "total_messages": data["total_messages"],
            "active_hours": [{"hour": h, "count": c} for h, c in top_hours],
            "active_days": [{"day": WEEKDAYS_RU[d], "count": c} for d, c in top_days],
            "first_message": data["first_message"].isoformat() if data["first_message"] else None,
            "last_message": data["last_message"].isoformat() if data["last_message"] else None,
        })

    # Сортировка по активности
    result.sort(key=lambda x: x["total_messages"], reverse=True)

    return result[:top_n]


# ===============================================================================
# ВИЗУАЛИЗАЦИЯ
# ===============================================================================

def create_heatmap_seaborn(analysis: Dict, output_path: Path) -> bool:
    """Создать тепловую карту с seaborn."""

    if not SEABORN_AVAILABLE or not PANDAS_AVAILABLE or not NUMPY_AVAILABLE:
        print("[ПРОПУСК] Heatmap: seaborn/pandas/numpy не установлены")
        return False

    print(f"Создание heatmap: {output_path}")

    by_hour_weekday = analysis["by_hour_weekday"]

    # Создание матрицы
    data = np.zeros((7, 24))
    for weekday in range(7):
        for hour in range(24):
            data[weekday][hour] = by_hour_weekday.get(weekday, {}).get(hour, 0)

    # DataFrame
    df = pd.DataFrame(
        data,
        index=[WEEKDAYS_SHORT[i] for i in range(7)],
        columns=[f"{h:02d}" for h in range(24)]
    )

    # Создание графика
    plt.figure(figsize=(16, 6))
    sns.heatmap(
        df,
        cmap="YlOrRd",
        annot=False,
        fmt="d",
        linewidths=0.5,
        cbar_kws={"label": "Количество сообщений"}
    )
    plt.title("Активность по часам и дням недели", fontsize=14, pad=20)
    plt.xlabel("Час", fontsize=12)
    plt.ylabel("День недели", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Сохранено: {output_path}")
    return True


def create_hourly_chart(analysis: Dict, output_path: Path) -> bool:
    """Создать график распределения по часам."""

    if not SEABORN_AVAILABLE or not PANDAS_AVAILABLE:
        print("[ПРОПУСК] Hourly chart: библиотеки не установлены")
        return False

    print(f"Создание графика по часам: {output_path}")

    by_hour = analysis["by_hour"]

    hours = list(range(24))
    from_me = [by_hour.get(h, {}).get("from_me", 0) for h in hours]
    from_them = [by_hour.get(h, {}).get("from_them", 0) for h in hours]

    x = np.arange(24)
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6))
    bars1 = ax.bar(x - width/2, from_them, width, label='От клиентов', color='#2196F3')
    bars2 = ax.bar(x + width/2, from_me, width, label='Наши ответы', color='#4CAF50')

    ax.set_xlabel('Час', fontsize=12)
    ax.set_ylabel('Количество сообщений', fontsize=12)
    ax.set_title('Распределение сообщений по часам', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{h:02d}" for h in hours])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Сохранено: {output_path}")
    return True


def create_weekday_chart(analysis: Dict, output_path: Path) -> bool:
    """Создать график распределения по дням недели."""

    if not SEABORN_AVAILABLE or not PANDAS_AVAILABLE:
        print("[ПРОПУСК] Weekday chart: библиотеки не установлены")
        return False

    print(f"Создание графика по дням недели: {output_path}")

    by_weekday = analysis["by_weekday"]

    days = list(range(7))
    from_me = [by_weekday.get(d, {}).get("from_me", 0) for d in days]
    from_them = [by_weekday.get(d, {}).get("from_them", 0) for d in days]

    x = np.arange(7)
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, from_them, width, label='От клиентов', color='#2196F3')
    bars2 = ax.bar(x + width/2, from_me, width, label='Наши ответы', color='#4CAF50')

    ax.set_xlabel('День недели', fontsize=12)
    ax.set_ylabel('Количество сообщений', fontsize=12)
    ax.set_title('Распределение сообщений по дням недели', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([WEEKDAYS_SHORT[d] for d in days])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Сохранено: {output_path}")
    return True


def create_monthly_chart(analysis: Dict, output_path: Path) -> bool:
    """Создать график по месяцам."""

    if not SEABORN_AVAILABLE or not PANDAS_AVAILABLE:
        print("[ПРОПУСК] Monthly chart: библиотеки не установлены")
        return False

    print(f"Создание графика по месяцам: {output_path}")

    by_month = analysis["by_month"]
    if not by_month:
        print("  Нет данных по месяцам")
        return False

    months = sorted(by_month.keys())
    totals = [by_month[m]["total"] for m in months]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(months, totals, marker='o', linewidth=2, markersize=6, color='#2196F3')
    ax.fill_between(months, totals, alpha=0.3, color='#2196F3')

    ax.set_xlabel('Месяц', fontsize=12)
    ax.set_ylabel('Количество сообщений', fontsize=12)
    ax.set_title('Динамика активности по месяцам', fontsize=14, pad=20)
    plt.xticks(rotation=45)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Сохранено: {output_path}")
    return True


def create_plotly_dashboard(analysis: Dict, best_time: Dict, weekday_patterns: Dict,
                           monthly_patterns: Dict, output_path: Path) -> bool:
    """Создать интерактивный HTML дашборд с plotly."""

    if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE or not NUMPY_AVAILABLE:
        print("[ПРОПУСК] Plotly dashboard: библиотеки не установлены")
        return False

    print(f"Создание HTML дашборда: {output_path}")

    # Подготовка данных
    by_hour = analysis["by_hour"]
    by_weekday = analysis["by_weekday"]
    by_month = analysis["by_month"]
    by_hour_weekday = analysis["by_hour_weekday"]

    # Создание subplot
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Тепловая карта активности',
            'Распределение по часам',
            'Распределение по дням недели',
            'Динамика по месяцам',
            'Выходные vs Будни',
            'Лучшее время для связи'
        ),
        specs=[
            [{"type": "heatmap"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "pie"}, {"type": "bar"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    # 1. Heatmap
    heatmap_data = np.zeros((7, 24))
    for weekday in range(7):
        for hour in range(24):
            heatmap_data[weekday][hour] = by_hour_weekday.get(weekday, {}).get(hour, 0)

    fig.add_trace(
        go.Heatmap(
            z=heatmap_data,
            x=[f"{h:02d}:00" for h in range(24)],
            y=[WEEKDAYS_SHORT[i] for i in range(7)],
            colorscale='YlOrRd',
            showscale=True,
            colorbar=dict(title="Сообщений", len=0.3, y=0.85),
        ),
        row=1, col=1
    )

    # 2. По часам
    hours = list(range(24))
    from_them = [by_hour.get(h, {}).get("from_them", 0) for h in hours]
    from_me = [by_hour.get(h, {}).get("from_me", 0) for h in hours]

    fig.add_trace(
        go.Bar(name='От клиентов', x=[f"{h:02d}" for h in hours], y=from_them,
               marker_color='#2196F3', showlegend=True),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(name='Наши ответы', x=[f"{h:02d}" for h in hours], y=from_me,
               marker_color='#4CAF50', showlegend=True),
        row=1, col=2
    )

    # 3. По дням недели
    days = list(range(7))
    from_them_days = [by_weekday.get(d, {}).get("from_them", 0) for d in days]
    from_me_days = [by_weekday.get(d, {}).get("from_me", 0) for d in days]

    fig.add_trace(
        go.Bar(name='От клиентов', x=[WEEKDAYS_SHORT[d] for d in days], y=from_them_days,
               marker_color='#2196F3', showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name='Наши ответы', x=[WEEKDAYS_SHORT[d] for d in days], y=from_me_days,
               marker_color='#4CAF50', showlegend=False),
        row=2, col=1
    )

    # 4. По месяцам
    if by_month:
        months = sorted(by_month.keys())
        totals = [by_month[m]["total"] for m in months]
        fig.add_trace(
            go.Scatter(x=months, y=totals, mode='lines+markers', name='Сообщения',
                      line=dict(color='#2196F3', width=2),
                      marker=dict(size=8), showlegend=False),
            row=2, col=2
        )

    # 5. Выходные vs Будни (pie)
    weekday_total = weekday_patterns.get("weekday_total", 0)
    weekend_total = weekday_patterns.get("weekend_total", 0)

    fig.add_trace(
        go.Pie(
            labels=['Будни (Пн-Пт)', 'Выходные (Сб-Вс)'],
            values=[weekday_total, weekend_total],
            marker_colors=['#2196F3', '#FF9800'],
            hole=0.4,
            showlegend=False,
        ),
        row=3, col=1
    )

    # 6. Лучшее время для связи
    best_hours = best_time.get("all_hours_ranked", [])[:12]
    if best_hours:
        hours_labels = [f"{h['hour']:02d}:00" for h in best_hours]
        scores = [h['score'] for h in best_hours]

        fig.add_trace(
            go.Bar(x=hours_labels, y=scores, marker_color='#9C27B0',
                  showlegend=False, name='Рейтинг'),
            row=3, col=2
        )

    # Настройка layout
    fig.update_layout(
        title_text='Анализ времени активности WhatsApp',
        title_font_size=20,
        height=1200,
        width=1400,
        barmode='group',
        template='plotly_white',
    )

    # Сохранение
    fig.write_html(output_path)
    print(f"  Сохранено: {output_path}")
    return True


# ===============================================================================
# ГЕНЕРАЦИЯ ОТЧЕТОВ
# ===============================================================================

def generate_markdown_report(
    analysis: Dict,
    best_time: Dict,
    weekday_patterns: Dict,
    monthly_patterns: Dict,
    top_contacts: List[Dict],
) -> str:
    """Генерация Markdown отчёта."""

    lines = []
    lines.append("# Анализ времени активности")
    lines.append("")
    lines.append(f"*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")

    # Сводка
    lines.append("## Сводка")
    lines.append("")
    lines.append(f"- **Всего обработано:** {analysis['total_processed']:,} сообщений")
    lines.append("")

    # Лучшее время для связи
    lines.append("## Лучшее время для связи")
    lines.append("")
    lines.append(f"**Рекомендация:** {best_time.get('recommendation', 'Нет данных')}")
    lines.append("")

    best_hours = best_time.get("best_hours", [])
    if best_hours:
        lines.append("### Топ-3 часа")
        lines.append("")
        lines.append("| Час | Сообщений от клиентов | Ср. время ответа (мин) | Рейтинг |")
        lines.append("|-----|----------------------|------------------------|---------|")
        for h in best_hours:
            resp = h['avg_response_min'] if h['avg_response_min'] else '-'
            lines.append(f"| {h['hour']:02d}:00 | {h['client_messages']:,} | {resp} | {h['score']} |")
        lines.append("")

    # Активные окна
    windows = best_time.get("active_windows", [])
    if windows:
        lines.append("### Активные окна")
        lines.append("")
        for w in windows:
            lines.append(f"- {w['start']:02d}:00 - {w['end']+1:02d}:00")
        lines.append("")

    # Выходные vs Будни
    lines.append("## Выходные vs Будни")
    lines.append("")
    lines.append(f"- **Будни (Пн-Пт):** {weekday_patterns['weekday_total']:,} сообщений "
                f"(~{weekday_patterns['weekday_avg_daily']:.0f}/день)")
    lines.append(f"- **Выходные (Сб-Вс):** {weekday_patterns['weekend_total']:,} сообщений "
                f"(~{weekday_patterns['weekend_avg_daily']:.0f}/день)")
    lines.append(f"- **Соотношение:** x{weekday_patterns['weekend_vs_weekday_ratio']}")
    lines.append("")

    most_active = weekday_patterns.get("most_active_day", {})
    least_active = weekday_patterns.get("least_active_day", {})
    if most_active:
        lines.append(f"- **Самый активный день:** {most_active['name']} ({most_active['messages']:,} сообщ.)")
    if least_active:
        lines.append(f"- **Наименее активный:** {least_active['name']} ({least_active['messages']:,} сообщ.)")
    lines.append("")

    # Распределение по часам
    lines.append("## Распределение по часам")
    lines.append("")

    by_hour = analysis.get("by_hour", {})
    if by_hour:
        max_total = max(h.get("total", 0) for h in by_hour.values()) or 1
        for hour in range(24):
            h_data = by_hour.get(hour, {})
            total = h_data.get("total", 0)
            bar_len = int(total / max_total * 25)
            bar = "#" * bar_len
            lines.append(f"`{hour:02d}:00` {bar} {total:,}")
        lines.append("")

    # Распределение по дням недели
    lines.append("## Распределение по дням недели")
    lines.append("")
    lines.append("| День | Всего | От клиентов | Наши |")
    lines.append("|------|-------|-------------|------|")

    by_weekday = analysis.get("by_weekday", {})
    for d in range(7):
        d_data = by_weekday.get(d, {})
        lines.append(
            f"| {WEEKDAYS_RU[d]} | {d_data.get('total', 0):,} | "
            f"{d_data.get('from_them', 0):,} | {d_data.get('from_me', 0):,} |"
        )
    lines.append("")

    # Сезонность
    lines.append("## Сезонность")
    lines.append("")
    lines.append(f"- **Тренд:** {monthly_patterns.get('trend', 'unknown')} "
                f"({monthly_patterns.get('trend_percentage', 0):+.1f}%)")
    lines.append(f"- **Высокий сезон (окт-апр):** ~{monthly_patterns.get('high_season_avg', 0):.0f} сообщ./мес")
    lines.append(f"- **Низкий сезон (май-сен):** ~{monthly_patterns.get('low_season_avg', 0):.0f} сообщ./мес")
    lines.append(f"- **Коэффициент сезонности:** x{monthly_patterns.get('seasonality_ratio', 0)}")
    lines.append("")

    # Активность по месяцам
    monthly_avg = monthly_patterns.get("monthly_average", {})
    if monthly_avg:
        lines.append("### Средняя активность по месяцам года")
        lines.append("")
        lines.append("| Месяц | Среднее сообщений |")
        lines.append("|-------|-------------------|")
        for month_name, avg in monthly_avg.items():
            lines.append(f"| {month_name} | {avg:.0f} |")
        lines.append("")

    # Топ контактов
    if top_contacts:
        lines.append("## Топ-10 контактов по активности")
        lines.append("")
        lines.append("| # | JID | Сообщений | Активные часы | Активные дни |")
        lines.append("|---|-----|-----------|---------------|--------------|")

        for i, c in enumerate(top_contacts[:10], 1):
            jid_short = c['jid'][:25] + "..." if len(c['jid']) > 28 else c['jid']
            hours_str = ", ".join(f"{h['hour']}:00" for h in c['active_hours'][:2])
            days_str = ", ".join(d['day'][:3] for d in c['active_days'][:2])
            lines.append(f"| {i} | {jid_short} | {c['total_messages']:,} | {hours_str} | {days_str} |")
        lines.append("")

    # Подвал
    lines.append("---")
    lines.append("")
    lines.append("*Отчёт сгенерирован скриптом analyze_activity_time.py*")

    return "\n".join(lines)


def build_output_json(
    analysis: Dict,
    best_time: Dict,
    weekday_patterns: Dict,
    monthly_patterns: Dict,
    top_contacts: List[Dict],
) -> Dict:
    """Сформировать выходной JSON."""

    # Преобразование by_hour_weekday для JSON (ключи должны быть строками)
    heatmap_data = {}
    for weekday, hours in analysis.get("by_hour_weekday", {}).items():
        heatmap_data[str(weekday)] = {str(h): v for h, v in hours.items()}

    # Преобразование by_hour
    by_hour_json = {}
    for h, data in analysis.get("by_hour", {}).items():
        by_hour_json[str(h)] = data

    # Преобразование by_weekday
    by_weekday_json = {}
    for d, data in analysis.get("by_weekday", {}).items():
        by_weekday_json[WEEKDAYS_RU[d]] = data

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_messages_processed": analysis["total_processed"],
            "unique_contacts": len(analysis.get("contacts_activity", {})),
        },
        "by_hour": by_hour_json,
        "by_weekday": by_weekday_json,
        "by_month": analysis.get("by_month", {}),
        "heatmap_data": heatmap_data,
        "best_contact_time": best_time,
        "weekday_patterns": weekday_patterns,
        "monthly_patterns": {
            "trend": monthly_patterns.get("trend"),
            "trend_percentage": monthly_patterns.get("trend_percentage"),
            "high_season_avg": monthly_patterns.get("high_season_avg"),
            "low_season_avg": monthly_patterns.get("low_season_avg"),
            "seasonality_ratio": monthly_patterns.get("seasonality_ratio"),
            "monthly_average": monthly_patterns.get("monthly_average", {}),
        },
        "top_contacts": top_contacts,
    }


# ===============================================================================
# MAIN
# ===============================================================================

def main():
    parser = argparse.ArgumentParser(description="Анализ времени активности WhatsApp чатов")
    parser.add_argument("--input", "-i", help="Путь к JSONL файлу сообщений")
    parser.add_argument("--contact", "-c", help="JID конкретного контакта для анализа")
    parser.add_argument("--no-charts", action="store_true", help="Не создавать графики")
    parser.add_argument("--no-html", action="store_true", help="Не создавать HTML дашборд")
    args = parser.parse_args()

    print("=" * 60)
    print("АНАЛИЗ ВРЕМЕНИ АКТИВНОСТИ WHATSAPP")
    print("=" * 60)

    # Создание директорий
    ensure_directories()

    # Пути
    input_file = Path(args.input) if args.input else RAW_DIR / "all_messages.jsonl"
    output_json = JSON_DIR / "activity_time_analysis.json"
    output_md = MD_DIR / "анализ_времени_активности.md"

    # Графики
    heatmap_png = ANALYTICS_DIR / "activity_heatmap.png"
    hours_png = ANALYTICS_DIR / "activity_hours.png"
    weekdays_png = ANALYTICS_DIR / "activity_weekdays.png"
    monthly_png = ANALYTICS_DIR / "activity_monthly.png"
    dashboard_html = ANALYTICS_DIR / "activity_dashboard.html"

    print(f"\nВходной файл: {input_file}")
    print(f"Фильтр по контакту: {args.contact or 'все контакты'}")

    # Загрузка данных
    messages = load_messages(input_file)
    if not messages:
        print("\n[ОШИБКА] Сообщения не найдены!")
        print("Сначала запустите parse_all_chats.py для создания all_messages.jsonl")
        return

    # Анализ
    analysis = analyze_activity(messages, args.contact)

    # Дополнительный анализ
    best_time = calculate_best_contact_time(analysis)
    weekday_patterns = analyze_weekday_patterns(analysis)
    monthly_patterns = analyze_monthly_patterns(analysis)
    top_contacts = analyze_contacts_activity(analysis.get("contacts_activity", {}))

    # Визуализация
    if not args.no_charts:
        print("\n" + "=" * 60)
        print("СОЗДАНИЕ ГРАФИКОВ")
        print("=" * 60)

        ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

        create_heatmap_seaborn(analysis, heatmap_png)
        create_hourly_chart(analysis, hours_png)
        create_weekday_chart(analysis, weekdays_png)
        create_monthly_chart(analysis, monthly_png)

    # HTML дашборд
    if not args.no_html:
        create_plotly_dashboard(
            analysis, best_time, weekday_patterns, monthly_patterns, dashboard_html
        )

    # Экспорт JSON
    print("\n" + "=" * 60)
    print("ЭКСПОРТ")
    print("=" * 60)

    output_data = build_output_json(
        analysis, best_time, weekday_patterns, monthly_patterns, top_contacts
    )

    JSON_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"JSON: {output_json}")

    # Экспорт Markdown
    md_content = generate_markdown_report(
        analysis, best_time, weekday_patterns, monthly_patterns, top_contacts
    )

    MD_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Markdown: {output_md}")

    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)

    print(f"\nЛучшее время для связи:")
    print(f"  {best_time.get('recommendation', 'Нет данных')}")

    print(f"\nВыходные vs Будни:")
    print(f"  Соотношение: x{weekday_patterns.get('weekend_vs_weekday_ratio', 0)}")
    print(f"  Самый активный день: {weekday_patterns.get('most_active_day', {}).get('name', 'N/A')}")

    print(f"\nСезонность:")
    print(f"  Тренд: {monthly_patterns.get('trend', 'unknown')} "
          f"({monthly_patterns.get('trend_percentage', 0):+.1f}%)")
    print(f"  Коэффициент: x{monthly_patterns.get('seasonality_ratio', 0)}")

    print(f"\nФайлы сохранены:")
    print(f"  - {output_json}")
    print(f"  - {output_md}")
    if not args.no_charts:
        print(f"  - {heatmap_png}")
        print(f"  - {hours_png}")
        print(f"  - {weekdays_png}")
        print(f"  - {monthly_png}")
    if not args.no_html:
        print(f"  - {dashboard_html}")


if __name__ == "__main__":
    main()
