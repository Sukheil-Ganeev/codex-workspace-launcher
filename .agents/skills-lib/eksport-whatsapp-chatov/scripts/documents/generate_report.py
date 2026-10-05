#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Генерация аналитических отчётов по чатам.
Создаёт отчёты за период, обороты, топ контактов.
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, ANALYTICS_DIR, CONTACT_TYPES, ensure_directories

# ═══════════════════════════════════════════════════════════════
# ИЗВЛЕЧЕНИЕ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def extract_operations_from_file(file_path: Path) -> List[Dict]:
    """Извлечь операции из файла чата."""
    operations = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Паттерн для таблицы операций
    table_pattern = r'\| (\d{1,2}\.\d{1,2}\.\d{4}) \| ([^|]+) \| ([\d\s,]+)\s*(RUB|AED|USD|руб|₽) \|'

    for match in re.finditer(table_pattern, content, re.IGNORECASE):
        date_str, operation, amount_str, currency = match.groups()

        try:
            date = datetime.strptime(date_str, '%d.%m.%Y')
            amount = float(amount_str.replace(' ', '').replace(',', ''))

            curr = currency.upper()
            if curr in ['РУБ', '₽']:
                curr = 'RUB'

            operations.append({
                'date': date,
                'operation': operation.strip(),
                'amount': amount,
                'currency': curr,
                'file': str(file_path),
                'contact': file_path.stem,
            })
        except (ValueError, AttributeError):
            continue

    return operations


def get_all_operations() -> List[Dict]:
    """Получить все операции из всех чатов."""
    all_operations = []

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                ops = extract_operations_from_file(file_path)
                all_operations.extend(ops)

    return all_operations


def get_chat_statistics() -> Dict:
    """Собрать статистику по всем чатам."""
    stats = {
        'total_chats': 0,
        'by_type': defaultdict(int),
        'by_topic': defaultdict(int),
        'total_messages': 0,
        'total_audio': 0,
        'total_images': 0,
        'total_pdfs': 0,
    }

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                stats['total_chats'] += 1
                stats['by_type'][contact_type] += 1

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Тематика
                topic_match = re.search(r'\*\*Тематика:\*\*\s*(.+)', content)
                if topic_match:
                    stats['by_topic'][topic_match.group(1).strip()] += 1

                # Статистика из файла
                msgs_match = re.search(r'Всего сообщений\s*\|\s*(\d+)', content)
                if msgs_match:
                    stats['total_messages'] += int(msgs_match.group(1))

                audio_match = re.search(r'Голосовых\s*\|\s*(\d+)', content)
                if audio_match:
                    stats['total_audio'] += int(audio_match.group(1))

    return stats


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТОВ
# ═══════════════════════════════════════════════════════════════

def generate_monthly_report(year: int, month: int) -> str:
    """Сгенерировать месячный отчёт."""
    operations = get_all_operations()

    # Фильтруем операции за месяц
    month_ops = [
        op for op in operations
        if op['date'].year == year and op['date'].month == month
    ]

    # Группируем по валютам
    by_currency = defaultdict(list)
    for op in month_ops:
        by_currency[op['currency']].append(op)

    # Группируем по контактам
    by_contact = defaultdict(lambda: defaultdict(float))
    for op in month_ops:
        by_contact[op['contact']][op['currency']] += op['amount']

    # Формируем отчёт
    month_names = [
        '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    report = f"""# Отчёт за {month_names[month]} {year}

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*

---

## Сводка

| Показатель | Значение |
|------------|----------|
| Операций | {len(month_ops)} |
"""

    for curr, ops in by_currency.items():
        total = sum(op['amount'] for op in ops)
        report += f"| Оборот {curr} | {total:,.2f} |\n"

    # Топ контактов
    report += "\n---\n\n## Топ контактов по объёму\n\n"
    report += "| Контакт | RUB | AED | USD |\n"
    report += "|---------|-----|-----|-----|\n"

    # Сортируем по общему объёму (приводим к условным единицам)
    def contact_volume(c):
        return (by_contact[c].get('RUB', 0) +
                by_contact[c].get('AED', 0) * 25 +
                by_contact[c].get('USD', 0) * 90)

    sorted_contacts = sorted(by_contact.keys(), key=contact_volume, reverse=True)[:10]

    for contact in sorted_contacts:
        rub = by_contact[contact].get('RUB', 0)
        aed = by_contact[contact].get('AED', 0)
        usd = by_contact[contact].get('USD', 0)
        report += f"| {contact} | {rub:,.0f} | {aed:,.0f} | {usd:,.0f} |\n"

    # Детальные операции
    report += "\n---\n\n## Все операции\n\n"
    report += "| Дата | Контакт | Операция | Сумма |\n"
    report += "|------|---------|----------|-------|\n"

    for op in sorted(month_ops, key=lambda x: x['date']):
        date_str = op['date'].strftime('%d.%m')
        report += f"| {date_str} | {op['contact']} | {op['operation'][:30]} | {op['amount']:,.0f} {op['currency']} |\n"

    return report


def generate_overview_report() -> str:
    """Сгенерировать общий обзор."""
    stats = get_chat_statistics()
    operations = get_all_operations()

    # Обороты по валютам
    by_currency = defaultdict(float)
    for op in operations:
        by_currency[op['currency']] += op['amount']

    report = f"""# Общий обзор базы чатов

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*

---

## Статистика чатов

| Показатель | Значение |
|------------|----------|
| Всего чатов | {stats['total_chats']} |
| Сообщений | {stats['total_messages']} |
| Голосовых | {stats['total_audio']} |

### По типам контактов

| Тип | Количество |
|-----|------------|
"""

    for t, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        report += f"| {t} | {count} |\n"

    report += "\n### По тематикам\n\n| Тематика | Количество |\n|----------|------------|\n"

    for topic, count in sorted(stats['by_topic'].items(), key=lambda x: -x[1])[:10]:
        report += f"| {topic} | {count} |\n"

    report += "\n---\n\n## Финансовые обороты\n\n| Валюта | Общий оборот |\n|--------|-------------|\n"

    for curr, total in sorted(by_currency.items()):
        report += f"| {curr} | {total:,.2f} |\n"

    return report


def generate_activity_report() -> str:
    """Сгенерировать отчёт об активности."""
    operations = get_all_operations()

    # Группируем по дням недели
    by_weekday = defaultdict(int)
    for op in operations:
        by_weekday[op['date'].weekday()] += 1

    # По месяцам
    by_month = defaultdict(int)
    for op in operations:
        key = op['date'].strftime('%Y-%m')
        by_month[key] += 1

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    report = f"""# Отчёт об активности

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*

---

## По дням недели

| День | Операций |
|------|----------|
"""

    for i, name in enumerate(weekdays):
        report += f"| {name} | {by_weekday[i]} |\n"

    report += "\n---\n\n## По месяцам\n\n| Месяц | Операций |\n|-------|----------|\n"

    for month, count in sorted(by_month.items()):
        report += f"| {month} | {count} |\n"

    return report


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Генерация аналитических отчётов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python generate_report.py --month 2025-01    # Отчёт за январь 2025
  python generate_report.py --overview         # Общий обзор
  python generate_report.py --activity         # Отчёт активности
  python generate_report.py --all              # Все отчёты
        """
    )

    parser.add_argument('--month', help='Месячный отчёт (YYYY-MM)')
    parser.add_argument('--overview', action='store_true', help='Общий обзор')
    parser.add_argument('--activity', action='store_true', help='Отчёт активности')
    parser.add_argument('--all', action='store_true', help='Все отчёты')
    parser.add_argument('-o', '--output', help='Папка для сохранения')
    parser.add_argument('--print', action='store_true', help='Вывести в консоль')

    args = parser.parse_args()

    ensure_directories()
    output_dir = Path(args.output) if args.output else ANALYTICS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    reports = []

    if args.month or args.all:
        if args.all:
            # Генерируем за последние 3 месяца
            now = datetime.now()
            for i in range(3):
                date = now - timedelta(days=30*i)
                report = generate_monthly_report(date.year, date.month)
                filename = f"{date.year}-{date.month:02d}_отчёт.md"
                reports.append((filename, report))
        else:
            year, month = map(int, args.month.split('-'))
            report = generate_monthly_report(year, month)
            reports.append((f"{year}-{month:02d}_отчёт.md", report))

    if args.overview or args.all:
        report = generate_overview_report()
        reports.append(("обзор.md", report))

    if args.activity or args.all:
        report = generate_activity_report()
        reports.append(("активность.md", report))

    if not reports:
        parser.print_help()
        return

    # Сохранение/вывод
    for filename, content in reports:
        if args.print:
            print(f"\n{'='*60}")
            print(f"# {filename}")
            print('='*60)
            print(content)
        else:
            file_path = output_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Сохранён: {file_path}")


if __name__ == "__main__":
    main()
