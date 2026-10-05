#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Сезонный анализ активности WhatsApp чатов.

Анализирует:
- Активность по месяцам
- Активность по дням недели
- Активность по часам
- Тренды (месяц к месяцу, год к году)
- Праздники ОАЭ и РФ

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/operations.json (опционально)
- D:/Downloads/Chats/_база/json/contacts.json (опционально)

Выходные файлы:
- D:/Downloads/Chats/_база/json/seasonal_analysis.json
- D:/Downloads/Chats/_база/md/сезонный_анализ.md
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import RAW_DIR, JSON_DIR, MD_DIR, ensure_directories
except ImportError:
    # Fallback если config.py недоступен
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")

    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        MD_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ПРАЗДНИКИ
# ═══════════════════════════════════════════════════════════════════════════════

# Праздники ОАЭ (фиксированные)
UAE_HOLIDAYS = {
    "01-01": "Новый год",
    "12-02": "День памяти",
    "12-03": "День памяти",
    "12-02": "Национальный день ОАЭ",
    "12-03": "Национальный день ОАЭ",
}

# Праздники РФ (фиксированные)
RU_HOLIDAYS = {
    "01-01": "Новый год",
    "01-02": "Новогодние каникулы",
    "01-03": "Новогодние каникулы",
    "01-04": "Новогодние каникулы",
    "01-05": "Новогодние каникулы",
    "01-06": "Новогодние каникулы",
    "01-07": "Рождество",
    "01-08": "Новогодние каникулы",
    "02-23": "День защитника Отечества",
    "03-08": "Международный женский день",
    "05-01": "Праздник Весны и Труда",
    "05-09": "День Победы",
    "06-12": "День России",
    "11-04": "День народного единства",
}

# Исламские праздники (приблизительные даты, меняются каждый год)
# Формат: (месяц, день, длительность_дней)
ISLAMIC_HOLIDAYS_2024 = [
    {"name": "Рамадан", "start": "2024-03-10", "end": "2024-04-09"},
    {"name": "Eid al-Fitr", "start": "2024-04-10", "end": "2024-04-12"},
    {"name": "Eid al-Adha", "start": "2024-06-16", "end": "2024-06-19"},
]

ISLAMIC_HOLIDAYS_2025 = [
    {"name": "Рамадан", "start": "2025-02-28", "end": "2025-03-29"},
    {"name": "Eid al-Fitr", "start": "2025-03-30", "end": "2025-04-01"},
    {"name": "Eid al-Adha", "start": "2025-06-06", "end": "2025-06-09"},
]

ISLAMIC_HOLIDAYS_2026 = [
    {"name": "Рамадан", "start": "2026-02-17", "end": "2026-03-19"},
    {"name": "Eid al-Fitr", "start": "2026-03-20", "end": "2026-03-22"},
    {"name": "Eid al-Adha", "start": "2026-05-26", "end": "2026-05-29"},
]

# Туристические сезоны в ОАЭ
UAE_SEASONS = {
    "high": [10, 11, 12, 1, 2, 3, 4],  # Октябрь - Апрель (высокий сезон)
    "low": [5, 6, 7, 8, 9],  # Май - Сентябрь (низкий сезон, жара)
}

# Дни недели на русском
WEEKDAYS_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

WEEKDAYS_EN = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}


def is_holiday(date: datetime) -> Optional[str]:
    """Проверить, является ли дата праздником."""
    date_key = date.strftime("%m-%d")

    # Проверка фиксированных праздников
    if date_key in UAE_HOLIDAYS:
        return UAE_HOLIDAYS[date_key]
    if date_key in RU_HOLIDAYS:
        return RU_HOLIDAYS[date_key]

    # Проверка исламских праздников
    date_str = date.strftime("%Y-%m-%d")
    all_islamic = ISLAMIC_HOLIDAYS_2024 + ISLAMIC_HOLIDAYS_2025 + ISLAMIC_HOLIDAYS_2026
    for holiday in all_islamic:
        if holiday["start"] <= date_str <= holiday["end"]:
            return holiday["name"]

    return None


def get_season(month: int) -> str:
    """Определить туристический сезон по месяцу."""
    if month in UAE_SEASONS["high"]:
        return "high"
    return "low"


def load_messages(filepath: Path) -> list:
    """Загрузить сообщения из JSONL файла."""
    messages = []

    if not filepath.exists():
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Файл не найден: {filepath}")
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
                    if line_num <= 10:  # Показывать только первые ошибки
                        print(f"[ОШИБКА] Строка {line_num}: {e}")

                # Прогресс каждые 100,000 сообщений
                if line_num % 100000 == 0:
                    print(f"  Загружено {line_num:,} сообщений...")
    except Exception as e:
        print(f"[ОШИБКА] Не удалось прочитать файл: {e}")

    print(f"  Всего загружено: {len(messages):,} сообщений")
    return messages


def load_operations(filepath: Path) -> list:
    """Загрузить операции из JSON файла."""
    if not filepath.exists():
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Файл операций не найден: {filepath}")
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Загружено операций: {len(data)}")
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить операции: {e}")
        return []


def load_contacts(filepath: Path) -> list:
    """Загрузить контакты из JSON файла."""
    if not filepath.exists():
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Файл контактов не найден: {filepath}")
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Загружено контактов: {len(data)}")
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить контакты: {e}")
        return []


def parse_message_datetime(msg: dict) -> Optional[datetime]:
    """Извлечь datetime из сообщения."""
    dt_str = msg.get("datetime")
    if not dt_str:
        return None

    # Попробовать разные форматы
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

    # Попробовать только дату
    try:
        return datetime.strptime(dt_str[:10], "%Y-%m-%d")
    except ValueError:
        return None


def analyze_messages(messages: list, operations: list, contacts: list) -> dict:
    """Основной анализ сообщений."""

    print("\nАнализ данных...")

    # Структуры для накопления данных
    by_month = defaultdict(lambda: {
        "messages": 0,
        "from_me": 0,
        "from_clients": 0,
        "unique_contacts": set(),
        "new_contacts": set(),
        "by_hour": defaultdict(int),
        "by_weekday": defaultdict(int),
        "response_times": [],
    })

    by_day_of_week = defaultdict(lambda: {
        "messages": 0,
        "from_me": 0,
        "from_clients": 0,
        "response_times": [],
    })

    by_hour = defaultdict(lambda: {
        "messages": 0,
        "from_me": 0,
        "from_clients": 0,
    })

    holidays_activity = defaultdict(lambda: {
        "messages": 0,
        "holiday_name": "",
        "dates": set(),
    })

    # Для отслеживания новых контактов
    first_message_by_jid = {}

    # Для расчёта времени ответа
    last_message_by_jid = {}

    # Обработка сообщений
    total = len(messages)
    processed = 0

    for msg in messages:
        dt = parse_message_datetime(msg)
        if not dt:
            continue

        processed += 1

        # Ключи для агрегации
        month_key = dt.strftime("%Y-%m")
        weekday = dt.weekday()
        hour = dt.hour
        jid = msg.get("jid", "")
        is_from_me = msg.get("is_from_me", False)

        # По месяцам
        by_month[month_key]["messages"] += 1
        by_month[month_key]["by_hour"][hour] += 1
        by_month[month_key]["by_weekday"][weekday] += 1

        if is_from_me:
            by_month[month_key]["from_me"] += 1
        else:
            by_month[month_key]["from_clients"] += 1

        if jid:
            by_month[month_key]["unique_contacts"].add(jid)

            # Отслеживание первого сообщения от контакта
            if jid not in first_message_by_jid:
                first_message_by_jid[jid] = dt
                by_month[month_key]["new_contacts"].add(jid)

        # По дням недели
        by_day_of_week[weekday]["messages"] += 1
        if is_from_me:
            by_day_of_week[weekday]["from_me"] += 1
        else:
            by_day_of_week[weekday]["from_clients"] += 1

        # По часам
        by_hour[hour]["messages"] += 1
        if is_from_me:
            by_hour[hour]["from_me"] += 1
        else:
            by_hour[hour]["from_clients"] += 1

        # Расчёт времени ответа
        if jid:
            if jid in last_message_by_jid:
                last_msg = last_message_by_jid[jid]
                time_diff = (dt - last_msg["dt"]).total_seconds() / 60  # в минутах

                # Если это ответ (смена отправителя) и прошло < 24 часов
                if last_msg["is_from_me"] != is_from_me and 0 < time_diff < 1440:
                    if is_from_me:  # Наш ответ клиенту
                        by_day_of_week[weekday]["response_times"].append(time_diff)
                        by_month[month_key]["response_times"].append(time_diff)

            last_message_by_jid[jid] = {"dt": dt, "is_from_me": is_from_me}

        # Праздники
        holiday = is_holiday(dt)
        if holiday:
            date_str = dt.strftime("%Y-%m-%d")
            holidays_activity[holiday]["messages"] += 1
            holidays_activity[holiday]["holiday_name"] = holiday
            holidays_activity[holiday]["dates"].add(date_str)

        # Прогресс
        if processed % 100000 == 0:
            print(f"  Обработано {processed:,}/{total:,} сообщений...")

    print(f"  Обработано всего: {processed:,} сообщений")

    return {
        "by_month": by_month,
        "by_day_of_week": by_day_of_week,
        "by_hour": by_hour,
        "holidays_activity": holidays_activity,
        "first_message_by_jid": first_message_by_jid,
    }


def calculate_trends(by_month: dict) -> dict:
    """Рассчитать тренды (MoM, YoY)."""

    trends = {
        "messages": {"direction": "stable", "change": 0.0, "mom_changes": []},
        "new_contacts": {"direction": "stable", "change": 0.0, "mom_changes": []},
        "monthly_data": [],
    }

    # Сортируем месяцы
    sorted_months = sorted(by_month.keys())

    if len(sorted_months) < 2:
        return trends

    # Данные по месяцам
    for i, month in enumerate(sorted_months):
        data = by_month[month]
        msg_count = data["messages"]
        new_contacts = len(data["new_contacts"])

        mom_msg_change = 0.0
        yoy_msg_change = 0.0

        # Month-over-Month
        if i > 0:
            prev_month = sorted_months[i - 1]
            prev_msg = by_month[prev_month]["messages"]
            if prev_msg > 0:
                mom_msg_change = (msg_count - prev_msg) / prev_msg

        # Year-over-Year
        year, mon = map(int, month.split("-"))
        yoy_month = f"{year - 1}-{mon:02d}"
        if yoy_month in by_month:
            yoy_msg = by_month[yoy_month]["messages"]
            if yoy_msg > 0:
                yoy_msg_change = (msg_count - yoy_msg) / yoy_msg

        trends["monthly_data"].append({
            "month": month,
            "messages": msg_count,
            "new_contacts": new_contacts,
            "mom_change": mom_msg_change,
            "yoy_change": yoy_msg_change,
        })

        trends["messages"]["mom_changes"].append(mom_msg_change)

    # Общий тренд за последние 3 месяца
    if len(trends["messages"]["mom_changes"]) >= 3:
        recent_changes = trends["messages"]["mom_changes"][-3:]
        avg_change = sum(recent_changes) / len(recent_changes)
        trends["messages"]["change"] = avg_change

        if avg_change > 0.05:
            trends["messages"]["direction"] = "up"
        elif avg_change < -0.05:
            trends["messages"]["direction"] = "down"
        else:
            trends["messages"]["direction"] = "stable"

    return trends


def identify_peak_periods(by_month: dict, holidays_activity: dict) -> list:
    """Определить пиковые периоды активности."""

    peaks = []

    if not by_month:
        return peaks

    # Средняя активность
    avg_messages = sum(d["messages"] for d in by_month.values()) / len(by_month)

    # Новогодний период
    ny_months = []
    for month in by_month:
        if month.endswith("-12") or month.endswith("-01"):
            ny_months.append(month)

    if ny_months:
        ny_messages = sum(by_month[m]["messages"] for m in ny_months)
        ny_avg = ny_messages / len(ny_months)
        if ny_avg > avg_messages:
            multiplier = round(ny_avg / avg_messages, 2) if avg_messages > 0 else 1.0
            peaks.append({
                "period": "Новый год",
                "dates": "декабрь - январь",
                "multiplier": multiplier,
                "messages": int(ny_avg),
            })

    # Высокий туристический сезон
    high_season_months = [m for m in by_month if int(m.split("-")[1]) in UAE_SEASONS["high"]]
    low_season_months = [m for m in by_month if int(m.split("-")[1]) in UAE_SEASONS["low"]]

    if high_season_months and low_season_months:
        high_avg = sum(by_month[m]["messages"] for m in high_season_months) / len(high_season_months)
        low_avg = sum(by_month[m]["messages"] for m in low_season_months) / len(low_season_months)

        if low_avg > 0:
            peaks.append({
                "period": "Высокий сезон ОАЭ",
                "dates": "октябрь - апрель",
                "multiplier": round(high_avg / low_avg, 2),
                "messages": int(high_avg),
            })

            peaks.append({
                "period": "Низкий сезон ОАЭ",
                "dates": "май - сентябрь",
                "multiplier": round(low_avg / high_avg, 2) if high_avg > 0 else 0,
                "messages": int(low_avg),
            })

    # Рамадан
    ramadan_messages = holidays_activity.get("Рамадан", {}).get("messages", 0)
    if ramadan_messages > 0:
        ramadan_dates = holidays_activity["Рамадан"].get("dates", set())
        if ramadan_dates:
            daily_avg = ramadan_messages / len(ramadan_dates)
            normal_daily_avg = avg_messages / 30 if avg_messages > 0 else 1
            multiplier = round(daily_avg / normal_daily_avg, 2) if normal_daily_avg > 0 else 1.0

            peaks.append({
                "period": "Рамадан",
                "dates": "март (даты меняются)",
                "multiplier": multiplier,
                "messages": ramadan_messages,
            })

    return peaks


def generate_recommendations(analysis: dict) -> list:
    """Генерация рекомендаций на основе анализа."""

    recommendations = []

    by_day_of_week = analysis["by_day_of_week"]
    by_hour = analysis["by_hour"]

    # Анализ дней недели
    if by_day_of_week:
        weekday_msgs = {d: data["messages"] for d, data in by_day_of_week.items()}
        avg_daily = sum(weekday_msgs.values()) / 7 if weekday_msgs else 0

        # Выходные vs будни
        weekend_msgs = (weekday_msgs.get(5, 0) + weekday_msgs.get(6, 0)) / 2
        weekday_avg = sum(weekday_msgs.get(d, 0) for d in range(5)) / 5 if avg_daily > 0 else 0

        if weekend_msgs > weekday_avg * 1.3:
            pct = int((weekend_msgs / weekday_avg - 1) * 100) if weekday_avg > 0 else 0
            recommendations.append(
                f"Увеличить штат в выходные (активность +{pct}%)"
            )

        # Самый активный день
        if weekday_msgs:
            max_day = max(weekday_msgs, key=weekday_msgs.get)
            max_msgs = weekday_msgs[max_day]
            if max_msgs > avg_daily * 1.2:
                recommendations.append(
                    f"Пик активности - {WEEKDAYS_RU[max_day]}: планировать важные задачи на другие дни"
                )

        # Время ответа
        for day, data in by_day_of_week.items():
            response_times = data.get("response_times", [])
            if response_times:
                avg_response = sum(response_times) / len(response_times)
                if avg_response > 30:  # > 30 минут
                    recommendations.append(
                        f"{WEEKDAYS_RU[day]}: среднее время ответа {int(avg_response)} мин - рассмотреть дополнительного сотрудника"
                    )

    # Анализ часов
    if by_hour:
        hour_msgs = {h: data["messages"] for h, data in by_hour.items()}
        avg_hourly = sum(hour_msgs.values()) / 24 if hour_msgs else 0

        # Низкая активность ночью
        night_hours = [22, 23, 0, 1, 2, 3, 4, 5]
        night_msgs = sum(hour_msgs.get(h, 0) for h in night_hours)
        night_avg = night_msgs / len(night_hours)

        if night_avg < avg_hourly * 0.3:
            recommendations.append(
                "Автоответы после 22:00 (низкая активность, можно обрабатывать утром)"
            )

        # Пиковые часы
        peak_hours = [h for h, msgs in hour_msgs.items() if msgs > avg_hourly * 1.5]
        if peak_hours:
            peak_str = ", ".join(f"{h}:00" for h in sorted(peak_hours))
            recommendations.append(
                f"Пиковые часы: {peak_str} - обеспечить максимальную доступность"
            )

        # Обеденное время
        lunch_hours = [12, 13, 14]
        lunch_msgs = sum(hour_msgs.get(h, 0) for h in lunch_hours) / len(lunch_hours)
        if lunch_msgs > avg_hourly * 1.2:
            recommendations.append(
                "Высокая активность в обед (12:00-15:00): сдвинуть обеденный перерыв"
            )

    # Ограничиваем количество рекомендаций
    if len(recommendations) > 10:
        recommendations = recommendations[:10]

    # Если нет данных
    if not recommendations:
        recommendations.append("Недостаточно данных для генерации рекомендаций")

    return recommendations


def build_output(analysis: dict, operations: list, contacts: list) -> dict:
    """Сформировать выходной JSON."""

    by_month = analysis["by_month"]
    by_day_of_week = analysis["by_day_of_week"]
    by_hour = analysis["by_hour"]
    holidays_activity = analysis["holidays_activity"]

    # Расчёт трендов
    trends = calculate_trends(by_month)

    # Определение пиковых периодов
    peak_periods = identify_peak_periods(by_month, holidays_activity)

    # Генерация рекомендаций
    recommendations = generate_recommendations(analysis)

    # Операции по месяцам
    operations_by_month = defaultdict(lambda: {"count": 0, "revenue_aed": 0})
    for op in operations:
        op_date = op.get("date", "")
        if op_date:
            try:
                dt = datetime.strptime(op_date, "%Y-%m-%d")
                month_key = dt.strftime("%Y-%m")
                operations_by_month[month_key]["count"] += 1

                amount = op.get("amount", 0)
                currency = op.get("currency", "")
                if currency == "AED":
                    operations_by_month[month_key]["revenue_aed"] += amount
            except ValueError:
                pass

    # Формирование by_month
    output_by_month = {}
    for month, data in sorted(by_month.items()):
        # Расчёт YoY
        year, mon = map(int, month.split("-"))
        yoy_month = f"{year - 1}-{mon:02d}"
        yoy_growth = 0.0
        if yoy_month in by_month:
            prev_msgs = by_month[yoy_month]["messages"]
            if prev_msgs > 0:
                yoy_growth = round((data["messages"] - prev_msgs) / prev_msgs, 2)

        # Среднее время ответа
        response_times = data.get("response_times", [])
        avg_response = round(sum(response_times) / len(response_times), 1) if response_times else None

        output_by_month[month] = {
            "messages": data["messages"],
            "from_me": data["from_me"],
            "from_clients": data["from_clients"],
            "unique_contacts": len(data["unique_contacts"]),
            "new_contacts": len(data["new_contacts"]),
            "operations": operations_by_month[month]["count"],
            "revenue_aed": operations_by_month[month]["revenue_aed"],
            "yoy_growth": yoy_growth,
            "avg_response_min": avg_response,
            "season": get_season(int(month.split("-")[1])),
        }

    # Формирование by_day_of_week
    output_by_weekday = {}
    for weekday in range(7):
        data = by_day_of_week.get(weekday, {"messages": 0, "from_me": 0, "from_clients": 0, "response_times": []})
        response_times = data.get("response_times", [])
        avg_response = round(sum(response_times) / len(response_times), 1) if response_times else None

        output_by_weekday[WEEKDAYS_EN[weekday]] = {
            "messages": data["messages"],
            "from_me": data.get("from_me", 0),
            "from_clients": data.get("from_clients", 0),
            "avg_response_min": avg_response,
        }

    # Формирование by_hour
    output_by_hour = {}
    if by_hour:
        avg_hourly = sum(d["messages"] for d in by_hour.values()) / 24
        for hour in range(24):
            data = by_hour.get(hour, {"messages": 0, "from_me": 0, "from_clients": 0})
            is_peak = data["messages"] > avg_hourly * 1.5

            output_by_hour[str(hour)] = {
                "messages": data["messages"],
                "from_me": data.get("from_me", 0),
                "from_clients": data.get("from_clients", 0),
                "peak": is_peak,
            }

    # Формирование trends
    output_trends = {
        "messages": {
            "direction": trends["messages"]["direction"],
            "change": round(trends["messages"]["change"], 2),
        },
        "monthly_summary": trends.get("monthly_data", [])[-6:],  # Последние 6 месяцев
    }

    # Добавление выручки в тренды если есть данные
    if operations:
        total_revenue = sum(op.get("amount", 0) for op in operations if op.get("currency") == "AED")
        output_trends["revenue"] = {
            "total_aed": total_revenue,
            "avg_per_operation": round(total_revenue / len(operations), 2) if operations else 0,
        }

    # Итоговый JSON
    output = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_messages": sum(d["messages"] for d in by_month.values()),
            "total_contacts": len(analysis["first_message_by_jid"]),
            "total_operations": len(operations),
            "date_range": {
                "from": min(by_month.keys()) if by_month else None,
                "to": max(by_month.keys()) if by_month else None,
            },
        },
        "by_month": output_by_month,
        "by_day_of_week": output_by_weekday,
        "by_hour": output_by_hour,
        "peak_periods": peak_periods,
        "trends": output_trends,
        "recommendations": recommendations,
    }

    return output


def generate_markdown(output: dict) -> str:
    """Генерация Markdown отчёта."""

    lines = []

    lines.append("# Сезонный анализ активности")
    lines.append("")
    lines.append(f"*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")

    # Сводка
    summary = output.get("summary", {})
    lines.append("## Сводка")
    lines.append("")
    lines.append(f"- **Всего сообщений:** {summary.get('total_messages', 0):,}")
    lines.append(f"- **Контактов:** {summary.get('total_contacts', 0):,}")
    lines.append(f"- **Операций:** {summary.get('total_operations', 0):,}")

    date_range = summary.get("date_range", {})
    if date_range.get("from") and date_range.get("to"):
        lines.append(f"- **Период:** {date_range['from']} - {date_range['to']}")
    lines.append("")

    # По месяцам
    lines.append("## Активность по месяцам")
    lines.append("")
    lines.append("| Месяц | Сообщения | Новые контакты | Операции | Выручка AED | YoY |")
    lines.append("|-------|-----------|----------------|----------|-------------|-----|")

    by_month = output.get("by_month", {})
    for month in sorted(by_month.keys(), reverse=True)[:12]:  # Последние 12 месяцев
        data = by_month[month]
        yoy = data.get("yoy_growth", 0)
        yoy_str = f"+{int(yoy*100)}%" if yoy > 0 else f"{int(yoy*100)}%" if yoy < 0 else "-"

        lines.append(
            f"| {month} | {data['messages']:,} | {data['new_contacts']} | "
            f"{data['operations']} | {data['revenue_aed']:,.0f} | {yoy_str} |"
        )
    lines.append("")

    # По дням недели
    lines.append("## Активность по дням недели")
    lines.append("")
    lines.append("| День | Сообщения | От клиентов | Наши | Ср. ответ (мин) |")
    lines.append("|------|-----------|-------------|------|-----------------|")

    by_weekday = output.get("by_day_of_week", {})
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day_en in weekday_order:
        if day_en in by_weekday:
            data = by_weekday[day_en]
            day_ru = WEEKDAYS_RU[weekday_order.index(day_en)]
            response = data.get("avg_response_min")
            response_str = f"{response:.0f}" if response else "-"

            lines.append(
                f"| {day_ru} | {data['messages']:,} | {data['from_clients']:,} | "
                f"{data['from_me']:,} | {response_str} |"
            )
    lines.append("")

    # По часам
    lines.append("## Активность по часам")
    lines.append("")

    by_hour = output.get("by_hour", {})
    if by_hour:
        # Графическое представление
        max_msgs = max(d["messages"] for d in by_hour.values()) if by_hour else 1

        for hour in range(24):
            hour_str = str(hour)
            if hour_str in by_hour:
                data = by_hour[hour_str]
                msgs = data["messages"]
                bar_len = int(msgs / max_msgs * 30) if max_msgs > 0 else 0
                bar = "#" * bar_len
                peak_mark = " [PEAK]" if data.get("peak") else ""
                lines.append(f"`{hour:02d}:00` {bar} {msgs:,}{peak_mark}")
        lines.append("")

    # Пиковые периоды
    lines.append("## Пиковые периоды")
    lines.append("")

    peak_periods = output.get("peak_periods", [])
    if peak_periods:
        for peak in peak_periods:
            mult = peak.get("multiplier", 1)
            mult_str = f"x{mult:.1f}" if mult >= 1 else f"x{mult:.2f}"
            lines.append(f"- **{peak['period']}** ({peak['dates']}): {mult_str}")
    else:
        lines.append("*Недостаточно данных*")
    lines.append("")

    # Тренды
    lines.append("## Тренды")
    lines.append("")

    trends = output.get("trends", {})
    msg_trend = trends.get("messages", {})
    direction = msg_trend.get("direction", "stable")
    change = msg_trend.get("change", 0)

    direction_emoji = {"up": "^", "down": "v", "stable": "="}
    direction_text = {"up": "рост", "down": "падение", "stable": "стабильно"}

    lines.append(
        f"- **Сообщения:** {direction_emoji.get(direction, '=')} {direction_text.get(direction, 'стабильно')} "
        f"({change:+.0%} за последние 3 месяца)"
    )

    if "revenue" in trends:
        revenue = trends["revenue"]
        lines.append(f"- **Выручка:** {revenue.get('total_aed', 0):,.0f} AED всего")
        lines.append(f"- **Средний чек:** {revenue.get('avg_per_operation', 0):,.0f} AED")
    lines.append("")

    # Рекомендации
    lines.append("## Рекомендации")
    lines.append("")

    recommendations = output.get("recommendations", [])
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    # Подвал
    lines.append("---")
    lines.append("")
    lines.append("*Отчёт сгенерирован автоматически скриптом seasonal_analysis.py*")

    return "\n".join(lines)


def main():
    """Основная функция."""

    print("=" * 60)
    print("СЕЗОННЫЙ АНАЛИЗ АКТИВНОСТИ")
    print("=" * 60)

    # Создание директорий
    ensure_directories()

    # Пути к файлам
    messages_file = RAW_DIR / "all_messages.jsonl"
    operations_file = JSON_DIR / "operations.json"
    contacts_file = JSON_DIR / "contacts.json"

    output_json_file = JSON_DIR / "seasonal_analysis.json"
    output_md_file = MD_DIR / "сезонный_анализ.md"

    print(f"\nВходные файлы:")
    print(f"  - Сообщения: {messages_file}")
    print(f"  - Операции: {operations_file}")
    print(f"  - Контакты: {contacts_file}")

    print(f"\nВыходные файлы:")
    print(f"  - JSON: {output_json_file}")
    print(f"  - Markdown: {output_md_file}")
    print()

    # Загрузка данных
    messages = load_messages(messages_file)
    operations = load_operations(operations_file)
    contacts = load_contacts(contacts_file)

    if not messages:
        print("\n[ОШИБКА] Сообщения не найдены!")
        print("Сначала запустите parse_all_chats.py для создания all_messages.jsonl")

        # Создаём пустой отчёт
        output = {
            "generated_at": datetime.now().isoformat(),
            "error": "Файл сообщений не найден",
            "summary": {"total_messages": 0, "total_contacts": 0, "total_operations": len(operations)},
            "by_month": {},
            "by_day_of_week": {},
            "by_hour": {},
            "peak_periods": [],
            "trends": {},
            "recommendations": ["Запустите parse_all_chats.py для создания базы сообщений"],
        }
    else:
        # Анализ данных
        analysis = analyze_messages(messages, operations, contacts)

        # Формирование выхода
        output = build_output(analysis, operations, contacts)

    # Сохранение JSON
    print(f"\nСохранение JSON: {output_json_file}")
    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Генерация и сохранение Markdown
    print(f"Генерация Markdown: {output_md_file}")
    md_content = generate_markdown(output)
    with open(output_md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)

    summary = output.get("summary", {})
    print(f"Сообщений обработано: {summary.get('total_messages', 0):,}")
    print(f"Контактов: {summary.get('total_contacts', 0):,}")
    print(f"Операций: {summary.get('total_operations', 0):,}")

    print(f"\nФайлы сохранены:")
    print(f"  - {output_json_file}")
    print(f"  - {output_md_file}")

    # Ключевые рекомендации
    recommendations = output.get("recommendations", [])
    if recommendations:
        print(f"\nКлючевые рекомендации:")
        for rec in recommendations[:3]:
            print(f"  * {rec}")


if __name__ == "__main__":
    main()
