#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Расчёт метрик времени отклика на сообщения клиентов.

Входной файл: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходные файлы:
  - D:/Downloads/Chats/_база/json/response_times.json
  - D:/Downloads/Chats/_база/md/метрики_отклика.md

Метрики:
  1. Время до первого ответа
  2. Среднее время ответа
  3. Медианное время ответа
  4. P95 время ответа (95-й процентиль)
  5. Процент ответов < 5 мин (быстрые ответы)
  6. Процент без ответа (неотвеченные)
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import RAW_DIR, JSON_DIR, MD_DIR, ensure_directories
except ImportError:
    # Fallback, если запускается отдельно
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")

    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        MD_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ (по умолчанию)
# ═══════════════════════════════════════════════════════════════
DEFAULT_FAST_THRESHOLD = 5  # Порог "быстрого" ответа в минутах
DEFAULT_MAX_WAIT_HOURS = 24  # Максимальное время ожидания ответа

DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}
DAY_NAMES_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ПАРСИНГА
# ═══════════════════════════════════════════════════════════════
def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Преобразовать ISO строку в datetime."""
    if not dt_str:
        return None
    try:
        # ISO формат: 2024-01-15T14:30:00
        return datetime.fromisoformat(dt_str)
    except ValueError:
        try:
            # Попробовать другой формат
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None


def load_messages(input_file: Path) -> list[dict]:
    """Загрузить сообщения из JSONL файла."""
    messages = []

    if not input_file.exists():
        print(f"[ОШИБКА] Файл не найден: {input_file}")
        return messages

    print(f"Загрузка сообщений из {input_file}...")

    with open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                messages.append(msg)
            except json.JSONDecodeError as e:
                if line_num <= 10:  # Показать первые 10 ошибок
                    print(f"  [ПРЕДУПРЕЖДЕНИЕ] Строка {line_num}: ошибка JSON - {e}")

    print(f"  Загружено сообщений: {len(messages):,}")
    return messages


# ═══════════════════════════════════════════════════════════════
# РАСЧЁТ МЕТРИК
# ═══════════════════════════════════════════════════════════════
def group_messages_by_chat(messages: list[dict]) -> dict[str, list[dict]]:
    """Группировать сообщения по чатам (JID)."""
    chats = defaultdict(list)

    for msg in messages:
        jid = msg.get("jid")
        if jid:
            chats[jid].append(msg)

    # Сортировать сообщения в каждом чате по времени
    for jid in chats:
        chats[jid].sort(key=lambda m: m.get("datetime", ""))

    return chats


def calculate_response_times(chats: dict[str, list[dict]], max_wait_hours: int) -> dict:
    """
    Рассчитать время отклика для всех чатов.

    Алгоритм:
    1. Для каждого входящего сообщения (is_from_me=False) найти следующее исходящее
    2. Рассчитать дельту в минутах
    3. Если ответа нет в течение max_wait_hours, считать неотвеченным
    """
    all_response_times = []  # Все времена отклика в минутах
    response_times_by_contact = defaultdict(lambda: {
        "response_times": [],
        "messages_received": 0,
        "messages_responded": 0,
        "first_response_time": None,
        "chat_name": None,
    })
    response_times_by_hour = defaultdict(lambda: {"times": [], "count": 0})
    response_times_by_day = defaultdict(lambda: {"times": [], "count": 0})
    response_times_by_month = defaultdict(lambda: {"times": [], "count": 0})

    total_incoming = 0
    total_responded = 0
    total_no_response = 0

    max_wait_minutes = max_wait_hours * 60

    for jid, messages in chats.items():
        # Пропустить групповые чаты (заканчиваются на @g.us)
        if jid and jid.endswith("@g.us"):
            continue

        chat_name = messages[0].get("chat_name") if messages else None
        contact_data = response_times_by_contact[jid]
        contact_data["chat_name"] = chat_name

        i = 0
        while i < len(messages):
            msg = messages[i]
            is_from_me = msg.get("is_from_me", False)

            # Ищем входящее сообщение (от клиента)
            if not is_from_me:
                total_incoming += 1
                contact_data["messages_received"] += 1

                msg_dt = parse_datetime(msg.get("datetime"))
                if not msg_dt:
                    i += 1
                    continue

                # Ищем следующее исходящее сообщение (наш ответ)
                response_found = False
                for j in range(i + 1, len(messages)):
                    next_msg = messages[j]

                    if next_msg.get("is_from_me", False):
                        next_dt = parse_datetime(next_msg.get("datetime"))
                        if not next_dt:
                            continue

                        # Рассчитать время отклика
                        delta = next_dt - msg_dt
                        delta_minutes = delta.total_seconds() / 60

                        # Проверить, не слишком ли поздно
                        if delta_minutes <= max_wait_minutes:
                            all_response_times.append(delta_minutes)
                            contact_data["response_times"].append(delta_minutes)
                            contact_data["messages_responded"] += 1

                            # Первый ответ
                            if contact_data["first_response_time"] is None:
                                contact_data["first_response_time"] = delta_minutes

                            # По часам (когда получено сообщение)
                            hour = msg_dt.hour
                            response_times_by_hour[hour]["times"].append(delta_minutes)
                            response_times_by_hour[hour]["count"] += 1

                            # По дням недели
                            day = DAY_NAMES[msg_dt.weekday()]
                            response_times_by_day[day]["times"].append(delta_minutes)
                            response_times_by_day[day]["count"] += 1

                            # По месяцам
                            month_key = msg_dt.strftime("%Y-%m")
                            response_times_by_month[month_key]["times"].append(delta_minutes)
                            response_times_by_month[month_key]["count"] += 1

                            total_responded += 1
                            response_found = True
                        break

                    # Если следующее сообщение тоже входящее, продолжаем искать ответ

                if not response_found:
                    total_no_response += 1

            i += 1

    return {
        "all_response_times": all_response_times,
        "by_contact": response_times_by_contact,
        "by_hour": response_times_by_hour,
        "by_day": response_times_by_day,
        "by_month": response_times_by_month,
        "total_incoming": total_incoming,
        "total_responded": total_responded,
        "total_no_response": total_no_response,
    }


def calculate_percentile(data: list[float], percentile: float) -> float:
    """Рассчитать процентиль."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (len(sorted_data) - 1) * percentile / 100
    lower = int(index)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[-1]
    weight = index - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


def aggregate_statistics(
    response_data: dict,
    fast_threshold: int,
    max_wait_hours: int
) -> dict:
    """Агрегировать статистику."""
    all_times = response_data["all_response_times"]

    # Общая статистика
    overall = {
        "avg_response_minutes": round(statistics.mean(all_times), 2) if all_times else 0,
        "median_response_minutes": round(statistics.median(all_times), 2) if all_times else 0,
        "p95_response_minutes": round(calculate_percentile(all_times, 95), 2) if all_times else 0,
        "min_response_minutes": round(min(all_times), 2) if all_times else 0,
        "max_response_minutes": round(max(all_times), 2) if all_times else 0,
        "fast_response_rate": round(
            sum(1 for t in all_times if t <= fast_threshold) / len(all_times), 4
        ) if all_times else 0,
        "no_response_rate": round(
            response_data["total_no_response"] / response_data["total_incoming"], 4
        ) if response_data["total_incoming"] > 0 else 0,
        "total_incoming_messages": response_data["total_incoming"],
        "total_responded": response_data["total_responded"],
        "total_no_response": response_data["total_no_response"],
    }

    # По контактам
    by_contact = []
    for jid, data in response_data["by_contact"].items():
        if data["messages_received"] > 0:
            times = data["response_times"]
            by_contact.append({
                "jid": jid,
                "name": data["chat_name"],
                "avg_response_minutes": round(statistics.mean(times), 2) if times else None,
                "median_response_minutes": round(statistics.median(times), 2) if times else None,
                "first_response_minutes": round(data["first_response_time"], 2) if data["first_response_time"] else None,
                "messages_received": data["messages_received"],
                "messages_responded": data["messages_responded"],
                "response_rate": round(data["messages_responded"] / data["messages_received"], 4),
            })

    # Сортировать по количеству сообщений
    by_contact.sort(key=lambda x: x["messages_received"], reverse=True)

    # По часам
    by_hour = {}
    for hour, data in response_data["by_hour"].items():
        times = data["times"]
        by_hour[str(hour)] = {
            "avg": round(statistics.mean(times), 2) if times else 0,
            "median": round(statistics.median(times), 2) if times else 0,
            "count": data["count"],
        }

    # По дням недели
    by_day_of_week = {}
    for day, data in response_data["by_day"].items():
        times = data["times"]
        by_day_of_week[day] = {
            "avg": round(statistics.mean(times), 2) if times else 0,
            "median": round(statistics.median(times), 2) if times else 0,
            "count": data["count"],
        }

    # Тренды по месяцам
    trends = {}
    prev_avg = None
    for month in sorted(response_data["by_month"].keys()):
        data = response_data["by_month"][month]
        times = data["times"]
        avg = statistics.mean(times) if times else 0

        trends[month] = {
            "avg": round(avg, 2),
            "median": round(statistics.median(times), 2) if times else 0,
            "count": data["count"],
            "improved": prev_avg is not None and avg < prev_avg,
        }
        prev_avg = avg

    return {
        "overall": overall,
        "by_contact": by_contact,
        "by_hour": by_hour,
        "by_day_of_week": by_day_of_week,
        "trends": trends,
        "generated_at": datetime.now().isoformat(),
        "settings": {
            "fast_response_threshold_minutes": fast_threshold,
            "max_response_time_hours": max_wait_hours,
        },
    }


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТОВ
# ═══════════════════════════════════════════════════════════════
def generate_markdown_report(stats: dict) -> str:
    """Сгенерировать Markdown отчёт."""
    overall = stats["overall"]
    settings = stats["settings"]
    fast_threshold = settings["fast_response_threshold_minutes"]

    lines = [
        "# Метрики времени отклика",
        "",
        f"_Сгенерировано: {stats['generated_at']}_",
        "",
        "## Общая статистика",
        "",
        "| Метрика | Значение |",
        "|---------|----------|",
        f"| Среднее время ответа | **{overall['avg_response_minutes']:.1f} мин** |",
        f"| Медианное время ответа | **{overall['median_response_minutes']:.1f} мин** |",
        f"| P95 время ответа | **{overall['p95_response_minutes']:.1f} мин** |",
        f"| Минимум | {overall['min_response_minutes']:.1f} мин |",
        f"| Максимум | {overall['max_response_minutes']:.1f} мин |",
        f"| Быстрых ответов (<{fast_threshold} мин) | **{overall['fast_response_rate']*100:.1f}%** |",
        f"| Без ответа | **{overall['no_response_rate']*100:.1f}%** |",
        f"| Всего входящих | {overall['total_incoming_messages']:,} |",
        f"| Отвечено | {overall['total_responded']:,} |",
        f"| Не отвечено | {overall['total_no_response']:,} |",
        "",
    ]

    # По часам
    lines.extend([
        "## Время отклика по часам",
        "",
        "| Час | Среднее (мин) | Медиана (мин) | Сообщений |",
        "|-----|---------------|---------------|-----------|",
    ])

    for hour in range(24):
        hour_str = str(hour)
        if hour_str in stats["by_hour"]:
            data = stats["by_hour"][hour_str]
            lines.append(f"| {hour:02d}:00 | {data['avg']:.1f} | {data['median']:.1f} | {data['count']:,} |")
        else:
            lines.append(f"| {hour:02d}:00 | - | - | 0 |")

    lines.append("")

    # По дням недели
    lines.extend([
        "## Время отклика по дням недели",
        "",
        "| День | Среднее (мин) | Медиана (мин) | Сообщений |",
        "|------|---------------|---------------|-----------|",
    ])

    for day_num, day_name in DAY_NAMES.items():
        if day_name in stats["by_day_of_week"]:
            data = stats["by_day_of_week"][day_name]
            day_ru = DAY_NAMES_RU[day_num]
            lines.append(f"| {day_ru} | {data['avg']:.1f} | {data['median']:.1f} | {data['count']:,} |")

    lines.append("")

    # Тренды
    if stats["trends"]:
        lines.extend([
            "## Тренды по месяцам",
            "",
            "| Месяц | Среднее (мин) | Медиана (мин) | Сообщений | Улучшение |",
            "|-------|---------------|---------------|-----------|-----------|",
        ])

        for month, data in sorted(stats["trends"].items()):
            improved = "+" if data["improved"] else "-"
            lines.append(f"| {month} | {data['avg']:.1f} | {data['median']:.1f} | {data['count']:,} | {improved} |")

        lines.append("")

    # Топ контактов по времени отклика
    lines.extend([
        "## Топ-20 контактов по времени отклика",
        "",
        "### Самые быстрые ответы",
        "",
        "| Контакт | Среднее (мин) | Получено | Отвечено | Rate |",
        "|---------|---------------|----------|----------|------|",
    ])

    # Фильтруем контакты с ответами и сортируем по среднему времени
    contacts_with_responses = [c for c in stats["by_contact"] if c["avg_response_minutes"] is not None]
    fastest = sorted(contacts_with_responses, key=lambda x: x["avg_response_minutes"])[:20]

    for c in fastest:
        name = (c["name"] or c["jid"] or "Неизвестно")[:30]
        lines.append(
            f"| {name} | {c['avg_response_minutes']:.1f} | "
            f"{c['messages_received']} | {c['messages_responded']} | "
            f"{c['response_rate']*100:.0f}% |"
        )

    lines.append("")

    lines.extend([
        "### Самые медленные ответы",
        "",
        "| Контакт | Среднее (мин) | Получено | Отвечено | Rate |",
        "|---------|---------------|----------|----------|------|",
    ])

    slowest = sorted(contacts_with_responses, key=lambda x: x["avg_response_minutes"], reverse=True)[:20]

    for c in slowest:
        name = (c["name"] or c["jid"] or "Неизвестно")[:30]
        lines.append(
            f"| {name} | {c['avg_response_minutes']:.1f} | "
            f"{c['messages_received']} | {c['messages_responded']} | "
            f"{c['response_rate']*100:.0f}% |"
        )

    lines.append("")

    # Контакты с наибольшим количеством неотвеченных
    lines.extend([
        "### Контакты с низким процентом ответов",
        "",
        "| Контакт | Получено | Отвечено | Rate |",
        "|---------|----------|----------|------|",
    ])

    # Контакты с минимум 5 сообщениями и низким response rate
    low_response = sorted(
        [c for c in stats["by_contact"] if c["messages_received"] >= 5],
        key=lambda x: x["response_rate"]
    )[:20]

    for c in low_response:
        name = (c["name"] or c["jid"] or "Неизвестно")[:30]
        lines.append(
            f"| {name} | {c['messages_received']} | "
            f"{c['messages_responded']} | {c['response_rate']*100:.0f}% |"
        )

    lines.append("")
    lines.append("---")
    lines.append(f"_Настройки: порог быстрого ответа = {settings['fast_response_threshold_minutes']} мин, "
                 f"макс. время ожидания = {settings['max_response_time_hours']} ч_")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Расчёт метрик времени отклика на сообщения",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python calculate_response_time.py
  python calculate_response_time.py --input custom_messages.jsonl
  python calculate_response_time.py --fast-threshold 10 --max-wait 48
        """
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=RAW_DIR / "all_messages.jsonl",
        help="Путь к входному JSONL файлу (по умолчанию: _база/raw/all_messages.jsonl)"
    )
    parser.add_argument(
        "--output-json", "-oj",
        type=Path,
        default=JSON_DIR / "response_times.json",
        help="Путь к выходному JSON файлу"
    )
    parser.add_argument(
        "--output-md", "-om",
        type=Path,
        default=MD_DIR / "метрики_отклика.md",
        help="Путь к выходному Markdown файлу"
    )
    parser.add_argument(
        "--fast-threshold",
        type=int,
        default=DEFAULT_FAST_THRESHOLD,
        help=f"Порог быстрого ответа в минутах (по умолчанию: {DEFAULT_FAST_THRESHOLD})"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=DEFAULT_MAX_WAIT_HOURS,
        help=f"Макс. время ожидания ответа в часах (по умолчанию: {DEFAULT_MAX_WAIT_HOURS})"
    )
    parser.add_argument(
        "--top-contacts",
        type=int,
        default=100,
        help="Количество контактов в выходном JSON (по умолчанию: 100)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )

    args = parser.parse_args()

    # Параметры из аргументов
    fast_threshold = args.fast_threshold
    max_wait_hours = args.max_wait

    print("=" * 60)
    print("РАСЧЁТ МЕТРИК ВРЕМЕНИ ОТКЛИКА")
    print("=" * 60)
    print(f"Порог быстрого ответа: {fast_threshold} мин")
    print(f"Макс. ожидание ответа: {max_wait_hours} ч")

    # Создать директории
    ensure_directories()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)

    # Загрузить сообщения
    messages = load_messages(args.input)
    if not messages:
        print("[ОШИБКА] Нет сообщений для анализа")
        sys.exit(1)

    # Группировать по чатам
    print("\nГруппировка сообщений по чатам...")
    chats = group_messages_by_chat(messages)
    print(f"  Чатов: {len(chats):,}")

    # Рассчитать времена отклика
    print("\nРасчёт времени отклика...")
    response_data = calculate_response_times(chats, max_wait_hours)
    print(f"  Входящих сообщений: {response_data['total_incoming']:,}")
    print(f"  С ответом: {response_data['total_responded']:,}")
    print(f"  Без ответа: {response_data['total_no_response']:,}")

    # Агрегировать статистику
    print("\nАгрегирование статистики...")
    stats = aggregate_statistics(response_data, fast_threshold, max_wait_hours)

    # Ограничить количество контактов в выводе
    stats["by_contact"] = stats["by_contact"][:args.top_contacts]

    # Вывести ключевые метрики
    print("\n" + "-" * 40)
    print("КЛЮЧЕВЫЕ МЕТРИКИ:")
    print("-" * 40)
    overall = stats["overall"]
    print(f"  Среднее время ответа:    {overall['avg_response_minutes']:.1f} мин")
    print(f"  Медианное время ответа:  {overall['median_response_minutes']:.1f} мин")
    print(f"  P95 время ответа:        {overall['p95_response_minutes']:.1f} мин")
    print(f"  Быстрых ответов (<{fast_threshold} мин): {overall['fast_response_rate']*100:.1f}%")
    print(f"  Без ответа:              {overall['no_response_rate']*100:.1f}%")

    # Сохранить JSON
    print(f"\nСохранение JSON: {args.output_json}")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # Сохранить Markdown
    print(f"Сохранение Markdown: {args.output_md}")
    md_report = generate_markdown_report(stats)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md_report)

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)
    print(f"  JSON: {args.output_json}")
    print(f"  Markdown: {args.output_md}")


if __name__ == "__main__":
    main()
