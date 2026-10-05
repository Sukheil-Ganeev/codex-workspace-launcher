#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Анализ длительности диалогов (сессий) в WhatsApp чатах.

Входной файл: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходные файлы:
  - D:/Downloads/Chats/_база/json/dialog_duration.json
  - D:/Downloads/Chats/_база/md/длительность_диалогов.md

Функции:
  1. Определение диалога (сессии): gap > 4 часов = новый диалог
  2. Метрики диалога: длительность, кол-во сообщений, кол-во сессий
  3. Lifecycle контакта: первый/последний контакт, длительность отношений
  4. Паттерны: быстрые сделки vs долгие, реактивация
  5. Визуализация: таблицы, гистограммы
  6. Экспорт: JSON
"""

import argparse
import json
import statistics
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
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    MD_DIR = Path("D:/Downloads/Chats/_база/md")

    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        MD_DIR.mkdir(parents=True, exist_ok=True)


# ===============================================================
# КОНСТАНТЫ
# ===============================================================
DEFAULT_SESSION_GAP_HOURS = 4       # Порог для разделения сессий
DEFAULT_REACTIVATION_DAYS = 14      # Порог для реактивации
DEFAULT_FAST_DEAL_HOURS = 24        # Порог "быстрой сделки"

DAY_NAMES_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}


# ===============================================================
# ФУНКЦИИ ПАРСИНГА
# ===============================================================
def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Преобразовать ISO строку в datetime."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        try:
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
                if line_num <= 10:
                    print(f"  [ПРЕДУПРЕЖДЕНИЕ] Строка {line_num}: ошибка JSON - {e}")

    print(f"  Загружено сообщений: {len(messages):,}")
    return messages


# ===============================================================
# ГРУППИРОВКА СООБЩЕНИЙ
# ===============================================================
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


# ===============================================================
# ОПРЕДЕЛЕНИЕ СЕССИЙ
# ===============================================================
def identify_sessions(
    messages: list[dict],
    session_gap_hours: int
) -> list[dict]:
    """
    Разбить сообщения на сессии (диалоги).

    Сессия заканчивается, если между сообщениями прошло > session_gap_hours.

    Возвращает список сессий:
    {
        "session_id": int,
        "start_time": datetime,
        "end_time": datetime,
        "duration_minutes": float,
        "message_count": int,
        "messages": list[dict]
    }
    """
    if not messages:
        return []

    sessions = []
    session_gap = timedelta(hours=session_gap_hours)

    current_session = {
        "session_id": 1,
        "messages": [],
        "start_time": None,
        "end_time": None,
    }

    prev_dt = None

    for msg in messages:
        msg_dt = parse_datetime(msg.get("datetime"))
        if not msg_dt:
            continue

        # Первое сообщение
        if prev_dt is None:
            current_session["start_time"] = msg_dt
            current_session["messages"].append(msg)
            prev_dt = msg_dt
            continue

        # Проверяем gap
        gap = msg_dt - prev_dt

        if gap > session_gap:
            # Завершаем текущую сессию
            current_session["end_time"] = prev_dt
            sessions.append(current_session)

            # Начинаем новую
            current_session = {
                "session_id": len(sessions) + 1,
                "messages": [msg],
                "start_time": msg_dt,
                "end_time": None,
            }
        else:
            current_session["messages"].append(msg)

        prev_dt = msg_dt

    # Завершаем последнюю сессию
    if current_session["messages"]:
        current_session["end_time"] = prev_dt
        sessions.append(current_session)

    # Рассчитываем метрики каждой сессии
    for session in sessions:
        start = session["start_time"]
        end = session["end_time"]

        if start and end:
            duration = (end - start).total_seconds() / 60
        else:
            duration = 0

        session["duration_minutes"] = round(duration, 2)
        session["message_count"] = len(session["messages"])

    return sessions


# ===============================================================
# АНАЛИЗ LIFECYCLE КОНТАКТА
# ===============================================================
def analyze_contact_lifecycle(
    sessions: list[dict],
    reactivation_days: int
) -> dict:
    """
    Анализ жизненного цикла контакта.

    Возвращает:
    {
        "first_contact": datetime,
        "last_contact": datetime,
        "relationship_days": int,
        "active_days": int,
        "total_sessions": int,
        "total_messages": int,
        "reactivations": list[dict],
        "avg_session_duration_minutes": float,
        "avg_messages_per_session": float,
        "avg_gap_between_sessions_days": float
    }
    """
    if not sessions:
        return {
            "first_contact": None,
            "last_contact": None,
            "relationship_days": 0,
            "active_days": 0,
            "total_sessions": 0,
            "total_messages": 0,
            "reactivations": [],
            "avg_session_duration_minutes": 0,
            "avg_messages_per_session": 0,
            "avg_gap_between_sessions_days": 0,
        }

    first_contact = sessions[0]["start_time"]
    last_contact = sessions[-1]["end_time"]

    # Общая длительность отношений
    relationship_days = 0
    if first_contact and last_contact:
        relationship_days = (last_contact - first_contact).days

    # Активные дни (уникальные даты сообщений)
    active_dates = set()
    total_messages = 0

    for session in sessions:
        for msg in session["messages"]:
            msg_dt = parse_datetime(msg.get("datetime"))
            if msg_dt:
                active_dates.add(msg_dt.date())
            total_messages += 1

    active_days = len(active_dates)

    # Средняя длительность сессии
    durations = [s["duration_minutes"] for s in sessions if s["duration_minutes"] > 0]
    avg_session_duration = statistics.mean(durations) if durations else 0

    # Среднее количество сообщений в сессии
    msg_counts = [s["message_count"] for s in sessions]
    avg_messages_per_session = statistics.mean(msg_counts) if msg_counts else 0

    # Gaps между сессиями и реактивации
    gaps_days = []
    reactivations = []
    reactivation_threshold = timedelta(days=reactivation_days)

    for i in range(1, len(sessions)):
        prev_end = sessions[i-1]["end_time"]
        curr_start = sessions[i]["start_time"]

        if prev_end and curr_start:
            gap = curr_start - prev_end
            gap_days = gap.total_seconds() / (24 * 3600)
            gaps_days.append(gap_days)

            # Реактивация
            if gap >= reactivation_threshold:
                reactivations.append({
                    "session_before": sessions[i-1]["session_id"],
                    "session_after": sessions[i]["session_id"],
                    "gap_days": round(gap_days, 1),
                    "reactivation_date": curr_start.isoformat() if curr_start else None,
                })

    avg_gap = statistics.mean(gaps_days) if gaps_days else 0

    return {
        "first_contact": first_contact.isoformat() if first_contact else None,
        "last_contact": last_contact.isoformat() if last_contact else None,
        "relationship_days": relationship_days,
        "active_days": active_days,
        "total_sessions": len(sessions),
        "total_messages": total_messages,
        "reactivations": reactivations,
        "reactivation_count": len(reactivations),
        "avg_session_duration_minutes": round(avg_session_duration, 2),
        "avg_messages_per_session": round(avg_messages_per_session, 2),
        "avg_gap_between_sessions_days": round(avg_gap, 2),
    }


# ===============================================================
# АНАЛИЗ ПАТТЕРНОВ
# ===============================================================
def analyze_patterns(
    sessions: list[dict],
    fast_deal_hours: int
) -> dict:
    """
    Анализ паттернов поведения.

    - Быстрые сделки (< fast_deal_hours от первого сообщения до последнего)
    - Долгие переговоры
    - Типичная длительность сессии
    """
    if not sessions:
        return {
            "pattern_type": "unknown",
            "fast_sessions_count": 0,
            "long_sessions_count": 0,
            "session_length_distribution": {},
        }

    fast_deal_minutes = fast_deal_hours * 60

    fast_sessions = 0
    long_sessions = 0

    # Распределение длительности сессий
    # < 5 мин, 5-30 мин, 30-60 мин, 1-4 ч, 4-24 ч, > 24 ч
    length_buckets = {
        "< 5 мин": 0,
        "5-30 мин": 0,
        "30-60 мин": 0,
        "1-4 часа": 0,
        "4-24 часа": 0,
        "> 24 часов": 0,
    }

    for session in sessions:
        duration = session["duration_minutes"]

        # Быстрая или долгая
        if duration <= fast_deal_minutes:
            fast_sessions += 1
        else:
            long_sessions += 1

        # Распределение
        if duration < 5:
            length_buckets["< 5 мин"] += 1
        elif duration < 30:
            length_buckets["5-30 мин"] += 1
        elif duration < 60:
            length_buckets["30-60 мин"] += 1
        elif duration < 240:
            length_buckets["1-4 часа"] += 1
        elif duration < 1440:
            length_buckets["4-24 часа"] += 1
        else:
            length_buckets["> 24 часов"] += 1

    # Определяем паттерн
    total = len(sessions)
    fast_ratio = fast_sessions / total if total > 0 else 0

    if fast_ratio > 0.7:
        pattern_type = "fast_dealer"  # Быстрые решения
    elif fast_ratio < 0.3:
        pattern_type = "long_negotiator"  # Долгие переговоры
    else:
        pattern_type = "mixed"

    return {
        "pattern_type": pattern_type,
        "fast_sessions_count": fast_sessions,
        "long_sessions_count": long_sessions,
        "fast_sessions_ratio": round(fast_ratio, 3),
        "session_length_distribution": length_buckets,
    }


# ===============================================================
# АНАЛИЗ ВСЕХ ЧАТОВ
# ===============================================================
def analyze_all_chats(
    chats: dict[str, list[dict]],
    session_gap_hours: int,
    reactivation_days: int,
    fast_deal_hours: int,
) -> dict:
    """
    Анализ всех чатов.

    Возвращает структуру для JSON экспорта.
    """
    results = {
        "contacts": [],
        "summary": {
            "total_contacts": 0,
            "total_sessions": 0,
            "total_messages": 0,
            "total_reactivations": 0,
            "avg_sessions_per_contact": 0,
            "avg_relationship_days": 0,
            "pattern_distribution": {
                "fast_dealer": 0,
                "long_negotiator": 0,
                "mixed": 0,
                "unknown": 0,
            },
            "session_length_overall": {
                "< 5 мин": 0,
                "5-30 мин": 0,
                "30-60 мин": 0,
                "1-4 часа": 0,
                "4-24 часа": 0,
                "> 24 часов": 0,
            },
        },
    }

    all_relationship_days = []
    all_sessions_count = []

    for jid, messages in chats.items():
        # Пропускаем групповые чаты
        if jid and jid.endswith("@g.us"):
            continue

        chat_name = messages[0].get("chat_name") if messages else None

        # Определяем сессии
        sessions = identify_sessions(messages, session_gap_hours)

        if not sessions:
            continue

        # Анализ lifecycle
        lifecycle = analyze_contact_lifecycle(sessions, reactivation_days)

        # Анализ паттернов
        patterns = analyze_patterns(sessions, fast_deal_hours)

        # Сериализуем сессии (без полного списка сообщений для экономии)
        sessions_summary = []
        for s in sessions:
            sessions_summary.append({
                "session_id": s["session_id"],
                "start_time": s["start_time"].isoformat() if s["start_time"] else None,
                "end_time": s["end_time"].isoformat() if s["end_time"] else None,
                "duration_minutes": s["duration_minutes"],
                "message_count": s["message_count"],
            })

        contact_data = {
            "jid": jid,
            "name": chat_name,
            "lifecycle": lifecycle,
            "patterns": patterns,
            "sessions": sessions_summary,
        }

        results["contacts"].append(contact_data)

        # Обновляем сводку
        results["summary"]["total_sessions"] += len(sessions)
        results["summary"]["total_messages"] += lifecycle["total_messages"]
        results["summary"]["total_reactivations"] += lifecycle["reactivation_count"]
        results["summary"]["pattern_distribution"][patterns["pattern_type"]] += 1

        # Суммируем распределение длительности
        for bucket, count in patterns["session_length_distribution"].items():
            results["summary"]["session_length_overall"][bucket] += count

        if lifecycle["relationship_days"] > 0:
            all_relationship_days.append(lifecycle["relationship_days"])
        all_sessions_count.append(len(sessions))

    # Финализируем сводку
    results["summary"]["total_contacts"] = len(results["contacts"])

    if all_sessions_count:
        results["summary"]["avg_sessions_per_contact"] = round(
            statistics.mean(all_sessions_count), 2
        )

    if all_relationship_days:
        results["summary"]["avg_relationship_days"] = round(
            statistics.mean(all_relationship_days), 2
        )

    # Сортируем контакты по количеству сессий
    results["contacts"].sort(
        key=lambda x: x["lifecycle"]["total_sessions"],
        reverse=True
    )

    return results


# ===============================================================
# ГЕНЕРАЦИЯ MARKDOWN ОТЧЁТА
# ===============================================================
def generate_histogram(distribution: dict, max_width: int = 30) -> str:
    """Генерация ASCII-гистограммы."""
    lines = []
    max_value = max(distribution.values()) if distribution.values() else 1

    for label, value in distribution.items():
        bar_len = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "#" * bar_len
        lines.append(f"  {label:15} | {bar} ({value})")

    return "\n".join(lines)


def generate_markdown_report(
    results: dict,
    session_gap_hours: int,
    reactivation_days: int,
    fast_deal_hours: int,
) -> str:
    """Генерация Markdown отчёта."""
    summary = results["summary"]
    contacts = results["contacts"]

    lines = [
        "# Анализ длительности диалогов",
        "",
        f"_Сгенерировано: {datetime.now().isoformat()}_",
        "",
        "## Общая статистика",
        "",
        "| Метрика | Значение |",
        "|---------|----------|",
        f"| Всего контактов | **{summary['total_contacts']:,}** |",
        f"| Всего сессий | **{summary['total_sessions']:,}** |",
        f"| Всего сообщений | **{summary['total_messages']:,}** |",
        f"| Всего реактиваций | **{summary['total_reactivations']:,}** |",
        f"| Сред. сессий на контакт | **{summary['avg_sessions_per_contact']:.1f}** |",
        f"| Сред. длительность отношений | **{summary['avg_relationship_days']:.0f} дней** |",
        "",
    ]

    # Паттерны поведения
    lines.extend([
        "## Паттерны поведения клиентов",
        "",
        "| Паттерн | Количество | Описание |",
        "|---------|------------|----------|",
        f"| Fast Dealer | **{summary['pattern_distribution']['fast_dealer']}** | Быстрые решения (<{fast_deal_hours}ч) |",
        f"| Long Negotiator | **{summary['pattern_distribution']['long_negotiator']}** | Долгие переговоры |",
        f"| Mixed | **{summary['pattern_distribution']['mixed']}** | Смешанный паттерн |",
        "",
    ])

    # Распределение длительности сессий
    lines.extend([
        "## Распределение длительности сессий",
        "",
        "```",
        generate_histogram(summary["session_length_overall"]),
        "```",
        "",
    ])

    # Топ контактов по количеству сессий
    lines.extend([
        "## Топ-20 контактов по количеству сессий",
        "",
        "| Контакт | Сессий | Сообщ. | Отношения (дн.) | Реактив. | Паттерн |",
        "|---------|--------|--------|-----------------|----------|---------|",
    ])

    for contact in contacts[:20]:
        name = (contact["name"] or contact["jid"] or "Неизвестно")[:25]
        sessions = contact["lifecycle"]["total_sessions"]
        messages = contact["lifecycle"]["total_messages"]
        rel_days = contact["lifecycle"]["relationship_days"]
        react = contact["lifecycle"]["reactivation_count"]
        pattern = contact["patterns"]["pattern_type"]

        lines.append(
            f"| {name} | {sessions} | {messages} | {rel_days} | {react} | {pattern} |"
        )

    lines.append("")

    # Контакты с реактивациями
    contacts_with_reactivations = [
        c for c in contacts
        if c["lifecycle"]["reactivation_count"] > 0
    ]

    if contacts_with_reactivations:
        lines.extend([
            "## Контакты с реактивациями",
            "",
            f"_Реактивация = возврат через {reactivation_days}+ дней_",
            "",
            "| Контакт | Реактиваций | Макс. перерыв (дн.) | Последняя реактив. |",
            "|---------|-------------|---------------------|---------------------|",
        ])

        # Сортируем по количеству реактиваций
        contacts_with_reactivations.sort(
            key=lambda x: x["lifecycle"]["reactivation_count"],
            reverse=True
        )

        for contact in contacts_with_reactivations[:15]:
            name = (contact["name"] or contact["jid"] or "Неизвестно")[:25]
            react_count = contact["lifecycle"]["reactivation_count"]

            reactivations = contact["lifecycle"]["reactivations"]
            max_gap = max(r["gap_days"] for r in reactivations) if reactivations else 0
            last_react = reactivations[-1]["reactivation_date"][:10] if reactivations else "-"

            lines.append(
                f"| {name} | {react_count} | {max_gap:.0f} | {last_react} |"
            )

        lines.append("")

    # Долгие отношения
    long_relationships = sorted(
        contacts,
        key=lambda x: x["lifecycle"]["relationship_days"],
        reverse=True
    )[:15]

    lines.extend([
        "## Самые долгие отношения",
        "",
        "| Контакт | Дней | Первый контакт | Последний контакт | Сессий |",
        "|---------|------|----------------|-------------------|--------|",
    ])

    for contact in long_relationships:
        if contact["lifecycle"]["relationship_days"] == 0:
            continue

        name = (contact["name"] or contact["jid"] or "Неизвестно")[:25]
        days = contact["lifecycle"]["relationship_days"]
        first = contact["lifecycle"]["first_contact"][:10] if contact["lifecycle"]["first_contact"] else "-"
        last = contact["lifecycle"]["last_contact"][:10] if contact["lifecycle"]["last_contact"] else "-"
        sessions = contact["lifecycle"]["total_sessions"]

        lines.append(f"| {name} | {days} | {first} | {last} | {sessions} |")

    lines.append("")

    # Настройки анализа
    lines.extend([
        "---",
        "",
        "### Настройки анализа",
        "",
        f"- Порог новой сессии: **{session_gap_hours} часов**",
        f"- Порог реактивации: **{reactivation_days} дней**",
        f"- Порог быстрой сделки: **{fast_deal_hours} часов**",
        "",
    ])

    return "\n".join(lines)


# ===============================================================
# MAIN
# ===============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Анализ длительности диалогов (сессий) в WhatsApp чатах",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python dialog_duration.py
  python dialog_duration.py --input custom_messages.jsonl
  python dialog_duration.py --session-gap 6 --reactivation 21
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
        default=JSON_DIR / "dialog_duration.json",
        help="Путь к выходному JSON файлу"
    )
    parser.add_argument(
        "--output-md", "-om",
        type=Path,
        default=MD_DIR / "длительность_диалогов.md",
        help="Путь к выходному Markdown файлу"
    )
    parser.add_argument(
        "--session-gap",
        type=int,
        default=DEFAULT_SESSION_GAP_HOURS,
        help=f"Порог разделения сессий в часах (по умолчанию: {DEFAULT_SESSION_GAP_HOURS})"
    )
    parser.add_argument(
        "--reactivation",
        type=int,
        default=DEFAULT_REACTIVATION_DAYS,
        help=f"Порог реактивации в днях (по умолчанию: {DEFAULT_REACTIVATION_DAYS})"
    )
    parser.add_argument(
        "--fast-deal",
        type=int,
        default=DEFAULT_FAST_DEAL_HOURS,
        help=f"Порог быстрой сделки в часах (по умолчанию: {DEFAULT_FAST_DEAL_HOURS})"
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

    # Параметры
    session_gap_hours = args.session_gap
    reactivation_days = args.reactivation
    fast_deal_hours = args.fast_deal

    print("=" * 60)
    print("АНАЛИЗ ДЛИТЕЛЬНОСТИ ДИАЛОГОВ")
    print("=" * 60)
    print(f"Порог новой сессии: {session_gap_hours} ч")
    print(f"Порог реактивации: {reactivation_days} дн")
    print(f"Порог быстрой сделки: {fast_deal_hours} ч")

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

    # Анализ
    print("\nАнализ диалогов...")
    results = analyze_all_chats(
        chats,
        session_gap_hours,
        reactivation_days,
        fast_deal_hours,
    )

    # Ограничить количество контактов
    results["contacts"] = results["contacts"][:args.top_contacts]

    # Добавляем метаданные
    results["metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "settings": {
            "session_gap_hours": session_gap_hours,
            "reactivation_days": reactivation_days,
            "fast_deal_hours": fast_deal_hours,
        },
    }

    # Вывод ключевых метрик
    print("\n" + "-" * 40)
    print("КЛЮЧЕВЫЕ МЕТРИКИ:")
    print("-" * 40)
    summary = results["summary"]
    print(f"  Всего контактов:          {summary['total_contacts']:,}")
    print(f"  Всего сессий:             {summary['total_sessions']:,}")
    print(f"  Всего сообщений:          {summary['total_messages']:,}")
    print(f"  Сред. сессий на контакт:  {summary['avg_sessions_per_contact']:.1f}")
    print(f"  Сред. длит. отношений:    {summary['avg_relationship_days']:.0f} дней")
    print(f"  Реактиваций:              {summary['total_reactivations']:,}")
    print("\nПаттерны поведения:")
    for pattern, count in summary["pattern_distribution"].items():
        if count > 0:
            print(f"  {pattern}: {count}")

    # Сохранить JSON
    print(f"\nСохранение JSON: {args.output_json}")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Сохранить Markdown
    print(f"Сохранение Markdown: {args.output_md}")
    md_report = generate_markdown_report(
        results,
        session_gap_hours,
        reactivation_days,
        fast_deal_hours,
    )
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md_report)

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)
    print(f"  JSON: {args.output_json}")
    print(f"  Markdown: {args.output_md}")


if __name__ == "__main__":
    main()
