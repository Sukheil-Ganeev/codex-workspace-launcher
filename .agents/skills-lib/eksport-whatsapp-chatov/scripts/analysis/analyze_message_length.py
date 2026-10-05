#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ длины сообщений WhatsApp.

Функции:
1. Статистика длины (средняя, медиана, мода) по контактам и времени
2. Категоризация: короткие/средние/длинные
3. Соотношение входящие/исходящие
4. Определение типа общения контакта
5. Корреляция с конверсией
6. Визуализация (гистограммы)
7. Экспорт: JSON, PNG
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple, Any
from statistics import mean, median, mode, stdev, StatisticsError

sys.stdout.reconfigure(encoding='utf-8')

# Добавляем путь к config
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    CHATS_DIR, ANALYTICS_DIR, JSON_DIR, RAW_DIR,
    CONTACT_TYPES, ensure_directories
)

# ===================================================================
# КОНФИГУРАЦИЯ
# ===================================================================

# Пороги категорий длины (в символах)
LENGTH_THRESHOLDS = {
    "short": 20,      # < 20 символов - короткие ("ок", "да", emoji)
    "medium": 100,    # 20-100 - обычные
    "long": 100       # > 100 - детальные
}

# Файлы данных
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
CONTACTS_FILE = JSON_DIR / "contacts.json"
OUTPUT_DIR = ANALYTICS_DIR / "message_length"

# ===================================================================
# ЗАГРУЗКА ДАННЫХ
# ===================================================================

def load_messages_jsonl(filepath: Path) -> List[Dict]:
    """Загрузка сообщений из JSONL файла."""
    messages = []

    if not filepath.exists():
        print(f"[!] Файл сообщений не найден: {filepath}")
        return messages

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue

    return messages


def load_messages_from_md(chats_dir: Path) -> List[Dict]:
    """Загрузка сообщений напрямую из MD файлов чатов."""
    messages = []

    # Паттерн для парсинга сообщений из MD
    # **SENDER** [HH:MM:SS]
    msg_pattern = re.compile(r'\*\*(.+?)\*\*\s*\[(\d{2}:\d{2}:\d{2})\]')
    date_pattern = re.compile(r'^### (\d{2}\.\d{2}\.\d{4})')

    for contact_type in CONTACT_TYPES:
        type_dir = chats_dir / contact_type
        if not type_dir.exists():
            continue

        for md_file in type_dir.glob("*.md"):
            contact_name = md_file.stem
            current_date = None

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"[!] Ошибка чтения {md_file}: {e}")
                continue

            lines = content.split('\n')
            current_sender = None
            current_text_lines = []

            for i, line in enumerate(lines):
                # Проверяем дату
                date_match = date_pattern.match(line)
                if date_match:
                    current_date = date_match.group(1)
                    continue

                # Проверяем начало сообщения
                msg_match = msg_pattern.match(line)
                if msg_match:
                    # Сохраняем предыдущее сообщение
                    if current_sender and current_text_lines:
                        text = '\n'.join(current_text_lines).strip()
                        if text:
                            messages.append({
                                'contact': contact_name,
                                'contact_type': contact_type,
                                'sender': current_sender,
                                'date': current_date,
                                'text': text,
                                'length': len(text)
                            })

                    # Начинаем новое сообщение
                    current_sender = msg_match.group(1).strip()
                    current_text_lines = []

                    # Текст после времени на той же строке
                    rest = line[msg_match.end():].strip()
                    if rest:
                        current_text_lines.append(rest)

                elif current_sender and line.strip():
                    # Продолжение текста сообщения
                    if not line.startswith('##') and not line.startswith('---'):
                        current_text_lines.append(line.strip())

            # Сохраняем последнее сообщение
            if current_sender and current_text_lines:
                text = '\n'.join(current_text_lines).strip()
                if text:
                    messages.append({
                        'contact': contact_name,
                        'contact_type': contact_type,
                        'sender': current_sender,
                        'date': current_date,
                        'text': text,
                        'length': len(text)
                    })

    return messages


def load_contacts(filepath: Path) -> Dict[str, Dict]:
    """Загрузка контактов в словарь по ID/имени."""
    contacts = {}

    if not filepath.exists():
        return contacts

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Поддержка разных форматов: список или объект с ключом "contacts"
        if isinstance(data, list):
            contact_list = data
        elif isinstance(data, dict):
            contact_list = data.get('contacts', [])
        else:
            contact_list = []

        for contact in contact_list:
            if not isinstance(contact, dict):
                continue
            contact_id = contact.get('contact_id') or contact.get('id') or contact.get('name')
            if contact_id:
                contacts[contact_id] = contact
                # Также по имени
                name = contact.get('name')
                if name:
                    contacts[name] = contact
    except Exception as e:
        print(f"[!] Ошибка загрузки контактов: {e}")

    return contacts


# ===================================================================
# СТАТИСТИКА ДЛИНЫ
# ===================================================================

def categorize_length(length: int) -> str:
    """Категоризация по длине сообщения."""
    if length < LENGTH_THRESHOLDS["short"]:
        return "short"
    elif length <= LENGTH_THRESHOLDS["medium"]:
        return "medium"
    else:
        return "long"


def calculate_basic_stats(lengths: List[int]) -> Dict:
    """Базовая статистика для списка длин."""
    if not lengths:
        return {
            "count": 0,
            "mean": 0,
            "median": 0,
            "mode": 0,
            "std": 0,
            "min": 0,
            "max": 0,
            "total_chars": 0
        }

    try:
        mode_val = mode(lengths)
    except StatisticsError:
        # Нет уникальной моды - берём первый из наиболее частых
        mode_val = Counter(lengths).most_common(1)[0][0] if lengths else 0

    try:
        std_val = stdev(lengths) if len(lengths) > 1 else 0
    except StatisticsError:
        std_val = 0

    return {
        "count": len(lengths),
        "mean": round(mean(lengths), 2),
        "median": round(median(lengths), 2),
        "mode": mode_val,
        "std": round(std_val, 2),
        "min": min(lengths),
        "max": max(lengths),
        "total_chars": sum(lengths)
    }


def calculate_category_distribution(lengths: List[int]) -> Dict:
    """Распределение по категориям длины."""
    categories = {"short": 0, "medium": 0, "long": 0}

    for length in lengths:
        cat = categorize_length(length)
        categories[cat] += 1

    total = len(lengths) if lengths else 1

    return {
        "counts": categories,
        "percentages": {
            k: round(v / total * 100, 1) for k, v in categories.items()
        }
    }


def analyze_by_contact(messages: List[Dict]) -> Dict[str, Dict]:
    """Статистика длины по контактам."""
    by_contact = defaultdict(list)

    for msg in messages:
        contact = msg.get('contact') or msg.get('contact_id') or 'Unknown'
        length = msg.get('length') or len(msg.get('text', ''))
        by_contact[contact].append(length)

    results = {}
    for contact, lengths in by_contact.items():
        stats = calculate_basic_stats(lengths)
        distribution = calculate_category_distribution(lengths)

        # Определяем тип общения
        short_pct = distribution['percentages']['short']
        long_pct = distribution['percentages']['long']

        if short_pct > 70:
            comm_type = "laconic"  # Лаконичный
        elif long_pct > 30:
            comm_type = "detailed"  # Детальный
        else:
            comm_type = "balanced"  # Сбалансированный

        results[contact] = {
            "stats": stats,
            "distribution": distribution,
            "communication_type": comm_type
        }

    return results


def analyze_by_time(messages: List[Dict]) -> Dict:
    """Статистика длины по времени (дни, месяцы)."""
    by_date = defaultdict(list)
    by_month = defaultdict(list)

    for msg in messages:
        date_str = msg.get('date')
        length = msg.get('length') or len(msg.get('text', ''))

        if date_str:
            by_date[date_str].append(length)

            # Извлекаем месяц (формат DD.MM.YYYY)
            try:
                parts = date_str.split('.')
                if len(parts) == 3:
                    month_key = f"{parts[1]}.{parts[2]}"  # MM.YYYY
                    by_month[month_key].append(length)
            except:
                pass

    # Статистика по дням
    daily_stats = {}
    for date, lengths in sorted(by_date.items()):
        daily_stats[date] = calculate_basic_stats(lengths)

    # Статистика по месяцам
    monthly_stats = {}
    for month, lengths in sorted(by_month.items()):
        monthly_stats[month] = calculate_basic_stats(lengths)

    return {
        "daily": daily_stats,
        "monthly": monthly_stats
    }


# ===================================================================
# АНАЛИЗ ВХОДЯЩИЕ/ИСХОДЯЩИЕ
# ===================================================================

def analyze_direction(messages: List[Dict], owner_markers: List[str] = None) -> Dict:
    """
    Анализ соотношения входящих/исходящих сообщений.

    owner_markers - список маркеров для определения "своих" сообщений
    (например, имя владельца аккаунта или эмодзи)
    """
    if owner_markers is None:
        owner_markers = []

    incoming = []  # Входящие (от контакта)
    outgoing = []  # Исходящие (наши)

    for msg in messages:
        sender = msg.get('sender', '')
        length = msg.get('length') or len(msg.get('text', ''))

        # Определяем направление
        is_outgoing = False
        for marker in owner_markers:
            if marker.lower() in sender.lower():
                is_outgoing = True
                break

        if is_outgoing:
            outgoing.append(length)
        else:
            incoming.append(length)

    incoming_stats = calculate_basic_stats(incoming)
    outgoing_stats = calculate_basic_stats(outgoing)

    # Баланс: кто пишет больше
    total_incoming_chars = sum(incoming)
    total_outgoing_chars = sum(outgoing)
    total_chars = total_incoming_chars + total_outgoing_chars

    if total_chars > 0:
        balance_ratio = total_outgoing_chars / total_chars
    else:
        balance_ratio = 0.5

    return {
        "incoming": {
            "stats": incoming_stats,
            "distribution": calculate_category_distribution(incoming)
        },
        "outgoing": {
            "stats": outgoing_stats,
            "distribution": calculate_category_distribution(outgoing)
        },
        "balance": {
            "incoming_chars": total_incoming_chars,
            "outgoing_chars": total_outgoing_chars,
            "outgoing_ratio": round(balance_ratio, 3),
            "who_writes_more": "outgoing" if balance_ratio > 0.5 else "incoming"
        }
    }


# ===================================================================
# КОРРЕЛЯЦИЯ С КОНВЕРСИЕЙ
# ===================================================================

def analyze_conversion_correlation(
    messages: List[Dict],
    contacts: Dict[str, Dict]
) -> Dict:
    """
    Анализ корреляции длины сообщений с конверсией.

    Конверсия определяется по:
    - Наличию заказов/операций в профиле контакта
    - Ключевым словам в сообщениях
    """
    conversion_keywords = [
        "бронирование", "забронировано", "оплата", "оплачено",
        "заказ", "подтверждено", "confirmation", "booking"
    ]

    converted_lengths = []
    not_converted_lengths = []

    # Группируем сообщения по контактам
    by_contact = defaultdict(list)
    for msg in messages:
        contact = msg.get('contact') or msg.get('contact_id')
        if contact:
            by_contact[contact].append(msg)

    for contact, msgs in by_contact.items():
        lengths = [m.get('length') or len(m.get('text', '')) for m in msgs]
        all_text = ' '.join(m.get('text', '') for m in msgs).lower()

        # Проверяем конверсию
        is_converted = False

        # По контакту
        contact_data = contacts.get(contact, {})
        if contact_data:
            orders = contact_data.get('statistics', {}).get('total_orders', 0)
            if orders and orders > 0:
                is_converted = True

        # По ключевым словам
        if not is_converted:
            for kw in conversion_keywords:
                if kw in all_text:
                    is_converted = True
                    break

        if is_converted:
            converted_lengths.extend(lengths)
        else:
            not_converted_lengths.extend(lengths)

    return {
        "converted": {
            "count_contacts": len([c for c, msgs in by_contact.items()
                                   if any(kw in ' '.join(m.get('text', '') for m in msgs).lower()
                                         for kw in conversion_keywords)]),
            "stats": calculate_basic_stats(converted_lengths),
            "distribution": calculate_category_distribution(converted_lengths)
        },
        "not_converted": {
            "stats": calculate_basic_stats(not_converted_lengths),
            "distribution": calculate_category_distribution(not_converted_lengths)
        },
        "comparison": {
            "avg_length_converted": round(mean(converted_lengths), 2) if converted_lengths else 0,
            "avg_length_not_converted": round(mean(not_converted_lengths), 2) if not_converted_lengths else 0,
            "difference_pct": round(
                ((mean(converted_lengths) if converted_lengths else 0) -
                 (mean(not_converted_lengths) if not_converted_lengths else 0)) /
                (mean(not_converted_lengths) if not_converted_lengths else 1) * 100, 1
            )
        }
    }


# ===================================================================
# ОПРЕДЕЛЕНИЕ ТИПА ОБЩЕНИЯ
# ===================================================================

def determine_communication_type(contact_stats: Dict) -> Dict:
    """
    Определение типа общения на основе статистики.

    Возвращает:
    - type: laconic/balanced/detailed
    - description: описание
    - recommendations: рекомендации по работе
    """
    short_pct = contact_stats.get('distribution', {}).get('percentages', {}).get('short', 0)
    long_pct = contact_stats.get('distribution', {}).get('percentages', {}).get('long', 0)
    avg_length = contact_stats.get('stats', {}).get('mean', 0)

    if short_pct > 70:
        return {
            "type": "laconic",
            "type_ru": "Лаконичный",
            "description": "Предпочитает короткие сообщения, быстрые ответы",
            "recommendations": [
                "Формулируйте вопросы чётко и коротко",
                "Избегайте длинных описаний",
                "Используйте списки и пункты",
                "Предлагайте быстрые решения"
            ]
        }
    elif long_pct > 30:
        return {
            "type": "detailed",
            "type_ru": "Детальный",
            "description": "Предпочитает подробные объяснения и описания",
            "recommendations": [
                "Предоставляйте полную информацию сразу",
                "Детализируйте условия и опции",
                "Не торопите с ответами",
                "Отвечайте развёрнуто на вопросы"
            ]
        }
    else:
        return {
            "type": "balanced",
            "type_ru": "Сбалансированный",
            "description": "Гибкий стиль общения, адаптируется к ситуации",
            "recommendations": [
                "Адаптируйтесь под контекст разговора",
                "Начинайте кратко, детализируйте по запросу",
                "Баланс между скоростью и полнотой"
            ]
        }


# ===================================================================
# ВИЗУАЛИЗАЦИЯ
# ===================================================================

def create_visualizations(
    messages: List[Dict],
    by_contact: Dict[str, Dict],
    output_dir: Path
) -> List[str]:
    """
    Создание визуализаций (гистограммы и графики).
    Возвращает список путей к созданным файлам.
    """
    created_files = []

    try:
        import matplotlib
        matplotlib.use('Agg')  # Без GUI
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[!] matplotlib не установлен. Визуализация пропущена.")
        print("    Установите: pip install matplotlib")
        return created_files

    # Настройка шрифтов для русского языка
    plt.rcParams['font.family'] = 'DejaVu Sans'

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Гистограмма общего распределения длин
    all_lengths = [m.get('length') or len(m.get('text', '')) for m in messages]

    if all_lengths:
        fig, ax = plt.subplots(figsize=(12, 6))

        # Ограничиваем для читаемости (до 500 символов)
        display_lengths = [min(l, 500) for l in all_lengths]

        ax.hist(display_lengths, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
        ax.axvline(x=LENGTH_THRESHOLDS['short'], color='red', linestyle='--',
                   label=f"Короткие (<{LENGTH_THRESHOLDS['short']})")
        ax.axvline(x=LENGTH_THRESHOLDS['medium'], color='orange', linestyle='--',
                   label=f"Длинные (>{LENGTH_THRESHOLDS['medium']})")

        ax.set_xlabel('Длина сообщения (символы)', fontsize=12)
        ax.set_ylabel('Количество сообщений', fontsize=12)
        ax.set_title('Распределение длины сообщений', fontsize=14)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        filepath = output_dir / "histogram_overall.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(str(filepath))
        print(f"    [+] {filepath}")

    # 2. Box plot по типам контактов
    by_type = defaultdict(list)
    for msg in messages:
        contact_type = msg.get('contact_type', 'unknown')
        length = msg.get('length') or len(msg.get('text', ''))
        by_type[contact_type].append(length)

    if by_type:
        fig, ax = plt.subplots(figsize=(10, 6))

        labels = list(by_type.keys())
        data = [by_type[t] for t in labels]

        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for patch, color in zip(bp['boxes'], colors[:len(labels)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        ax.set_xlabel('Тип контакта', fontsize=12)
        ax.set_ylabel('Длина сообщения', fontsize=12)
        ax.set_title('Распределение длины по типам контактов', fontsize=14)
        ax.grid(axis='y', alpha=0.3)

        filepath = output_dir / "boxplot_by_type.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(str(filepath))
        print(f"    [+] {filepath}")

    # 3. Pie chart категорий
    dist = calculate_category_distribution(all_lengths)

    if dist['counts']:
        fig, ax = plt.subplots(figsize=(8, 8))

        labels = ['Короткие\n(<20)', 'Средние\n(20-100)', 'Длинные\n(>100)']
        sizes = [dist['counts']['short'], dist['counts']['medium'], dist['counts']['long']]
        colors_pie = ['#ff6b6b', '#ffd93d', '#6bcb77']
        explode = (0.05, 0, 0)

        ax.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.set_title('Распределение по категориям длины', fontsize=14)

        filepath = output_dir / "pie_categories.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(str(filepath))
        print(f"    [+] {filepath}")

    # 4. Top-10 контактов по средней длине
    if by_contact:
        sorted_contacts = sorted(
            by_contact.items(),
            key=lambda x: x[1]['stats']['mean'],
            reverse=True
        )[:10]

        if sorted_contacts:
            fig, ax = plt.subplots(figsize=(12, 6))

            names = [c[0][:20] + '...' if len(c[0]) > 20 else c[0] for c in sorted_contacts]
            values = [c[1]['stats']['mean'] for c in sorted_contacts]

            bars = ax.barh(names, values, color='steelblue', alpha=0.7)
            ax.set_xlabel('Средняя длина сообщения', fontsize=12)
            ax.set_title('Top-10 контактов по средней длине сообщений', fontsize=14)
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)

            # Добавляем значения
            for bar, val in zip(bars, values):
                ax.text(val + 2, bar.get_y() + bar.get_height()/2,
                       f'{val:.0f}', va='center', fontsize=10)

            filepath = output_dir / "top10_by_avg_length.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            created_files.append(str(filepath))
            print(f"    [+] {filepath}")

    # 5. Распределение типов общения
    comm_types = Counter(
        c['communication_type'] for c in by_contact.values()
    )

    if comm_types:
        fig, ax = plt.subplots(figsize=(8, 6))

        type_labels = {
            'laconic': 'Лаконичный',
            'balanced': 'Сбалансированный',
            'detailed': 'Детальный'
        }

        labels = [type_labels.get(t, t) for t in comm_types.keys()]
        values = list(comm_types.values())
        colors_bar = ['#ff6b6b', '#ffd93d', '#6bcb77']

        ax.bar(labels, values, color=colors_bar[:len(labels)], alpha=0.7, edgecolor='black')
        ax.set_ylabel('Количество контактов', fontsize=12)
        ax.set_title('Распределение типов общения', fontsize=14)
        ax.grid(axis='y', alpha=0.3)

        for i, v in enumerate(values):
            ax.text(i, v + 0.5, str(v), ha='center', fontsize=12, fontweight='bold')

        filepath = output_dir / "communication_types.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        created_files.append(str(filepath))
        print(f"    [+] {filepath}")

    return created_files


# ===================================================================
# ГЛАВНЫЙ АНАЛИЗ
# ===================================================================

def run_full_analysis(
    messages: List[Dict],
    contacts: Dict[str, Dict],
    owner_markers: List[str] = None,
    output_dir: Path = None
) -> Dict:
    """
    Запуск полного анализа длины сообщений.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("АНАЛИЗ ДЛИНЫ СООБЩЕНИЙ")
    print("=" * 60)

    if not messages:
        print("[!] Нет сообщений для анализа")
        return {}

    print(f"\n[1] Загружено сообщений: {len(messages)}")

    # Добавляем длину если её нет
    for msg in messages:
        if 'length' not in msg:
            msg['length'] = len(msg.get('text', ''))

    all_lengths = [m['length'] for m in messages]

    # 1. Общая статистика
    print("\n[2] Вычисление общей статистики...")
    overall_stats = calculate_basic_stats(all_lengths)
    overall_distribution = calculate_category_distribution(all_lengths)

    print(f"    Средняя длина: {overall_stats['mean']:.1f} символов")
    print(f"    Медиана: {overall_stats['median']:.1f}")
    print(f"    Короткие (<20): {overall_distribution['percentages']['short']:.1f}%")
    print(f"    Длинные (>100): {overall_distribution['percentages']['long']:.1f}%")

    # 2. По контактам
    print("\n[3] Анализ по контактам...")
    by_contact = analyze_by_contact(messages)
    print(f"    Проанализировано контактов: {len(by_contact)}")

    # 3. По времени
    print("\n[4] Анализ по времени...")
    time_stats = analyze_by_time(messages)
    print(f"    Дней с данными: {len(time_stats['daily'])}")
    print(f"    Месяцев с данными: {len(time_stats['monthly'])}")

    # 4. Направление (входящие/исходящие)
    print("\n[5] Анализ направления...")
    direction_stats = analyze_direction(messages, owner_markers)
    print(f"    Входящих: {direction_stats['incoming']['stats']['count']}")
    print(f"    Исходящих: {direction_stats['outgoing']['stats']['count']}")

    # 5. Корреляция с конверсией
    print("\n[6] Корреляция с конверсией...")
    conversion_stats = analyze_conversion_correlation(messages, contacts)
    print(f"    Разница в длине: {conversion_stats['comparison']['difference_pct']:.1f}%")

    # 6. Типы общения
    print("\n[7] Определение типов общения...")
    contact_types_summary = Counter(
        c['communication_type'] for c in by_contact.values()
    )
    for ct, count in contact_types_summary.most_common():
        print(f"    {ct}: {count} контактов")

    # 7. Визуализация
    print("\n[8] Создание визуализаций...")
    viz_files = create_visualizations(messages, by_contact, output_dir)

    # Собираем итоговый отчёт
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_messages": len(messages),
        "total_contacts": len(by_contact),
        "overall": {
            "stats": overall_stats,
            "distribution": overall_distribution
        },
        "by_contact": {
            k: {
                **v,
                "communication_info": determine_communication_type(v)
            }
            for k, v in by_contact.items()
        },
        "by_time": time_stats,
        "direction": direction_stats,
        "conversion_correlation": conversion_stats,
        "communication_types_summary": dict(contact_types_summary),
        "visualizations": viz_files,
        "thresholds_used": LENGTH_THRESHOLDS
    }

    # Сохраняем JSON
    json_path = output_dir / "message_length_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n[9] Результаты сохранены:")
    print(f"    JSON: {json_path}")
    for viz in viz_files:
        print(f"    PNG: {viz}")

    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВЕРШЁН")
    print("=" * 60)

    return report


# ===================================================================
# CLI
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Анализ длины сообщений WhatsApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python analyze_message_length.py                    # Полный анализ
  python analyze_message_length.py --source md       # Из MD файлов
  python analyze_message_length.py --source jsonl    # Из JSONL
  python analyze_message_length.py -o /path/to/output
  python analyze_message_length.py --no-viz          # Без графиков
  python analyze_message_length.py --owner "Марсель" # Маркер владельца
        """
    )

    parser.add_argument(
        '--source', '-s',
        choices=['md', 'jsonl', 'auto'],
        default='auto',
        help='Источник данных: md (файлы чатов), jsonl (all_messages.jsonl), auto'
    )
    parser.add_argument(
        '--output', '-o',
        default=str(OUTPUT_DIR),
        help=f'Директория для результатов (default: {OUTPUT_DIR})'
    )
    parser.add_argument(
        '--owner',
        action='append',
        default=[],
        help='Маркер владельца для определения исходящих (можно указать несколько)'
    )
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Без визуализации (только JSON)'
    )
    parser.add_argument(
        '--contact', '-c',
        help='Анализ конкретного контакта'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Вывести JSON в stdout'
    )

    args = parser.parse_args()

    ensure_directories()

    # Загрузка сообщений
    messages = []

    if args.source == 'auto':
        # Сначала пробуем JSONL (быстрее)
        if MESSAGES_FILE.exists():
            print(f"[*] Загрузка из {MESSAGES_FILE}")
            messages = load_messages_jsonl(MESSAGES_FILE)

        # Если нет - из MD
        if not messages:
            print(f"[*] Загрузка из MD файлов в {CHATS_DIR}")
            messages = load_messages_from_md(CHATS_DIR)

    elif args.source == 'jsonl':
        messages = load_messages_jsonl(MESSAGES_FILE)

    elif args.source == 'md':
        messages = load_messages_from_md(CHATS_DIR)

    if not messages:
        print("[!] Сообщения не найдены")
        return

    # Фильтр по контакту
    if args.contact:
        messages = [m for m in messages
                   if args.contact.lower() in (m.get('contact', '') or '').lower()]
        print(f"[*] Отфильтровано для '{args.contact}': {len(messages)} сообщений")

    # Загрузка контактов
    contacts = load_contacts(CONTACTS_FILE)

    # Запуск анализа
    output_dir = Path(args.output)

    if args.no_viz:
        # Без визуализации - модифицируем функцию
        original_create_viz = create_visualizations
        def no_viz(*args, **kwargs):
            return []
        globals()['create_visualizations'] = no_viz

    report = run_full_analysis(
        messages,
        contacts,
        owner_markers=args.owner if args.owner else None,
        output_dir=output_dir
    )

    if args.json:
        print("\n" + json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
