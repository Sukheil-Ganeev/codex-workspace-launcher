#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Полнотекстовый поиск по чатам WhatsApp.
Поддерживает поиск по тексту, суммам, датам, контактам.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, CONTACT_TYPES, PATTERNS

# ═══════════════════════════════════════════════════════════════
# ИНДЕКСАЦИЯ
# ═══════════════════════════════════════════════════════════════

def get_all_chat_files() -> List[Path]:
    """Получить все файлы чатов."""
    files = []
    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            files.extend(type_dir.glob("*.md"))
    return files


def parse_chat_metadata(content: str) -> Dict:
    """Извлечь метаданные из чата."""
    metadata = {}

    # Тип контакта
    type_match = re.search(r'\*\*Тип:\*\*\s*(.+)', content)
    if type_match:
        metadata['type'] = type_match.group(1).strip()

    # Телефон
    phone_match = re.search(r'\*\*Телефон:\*\*\s*(.+)', content)
    if phone_match:
        metadata['phone'] = phone_match.group(1).strip()

    # Период
    period_match = re.search(r'\*\*Период:\*\*\s*(.+)', content)
    if period_match:
        metadata['period'] = period_match.group(1).strip()

    # Тематика
    topic_match = re.search(r'\*\*Тематика:\*\*\s*(.+)', content)
    if topic_match:
        metadata['topic'] = topic_match.group(1).strip()

    return metadata


# ═══════════════════════════════════════════════════════════════
# ПОИСК
# ═══════════════════════════════════════════════════════════════

def search_text(query: str, case_sensitive: bool = False) -> List[Dict]:
    """
    Поиск по тексту во всех чатах.

    Returns:
        Список найденных совпадений с контекстом
    """
    results = []
    files = get_all_chat_files()

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(query), flags)

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = list(pattern.finditer(content))
        if matches:
            metadata = parse_chat_metadata(content)

            for match in matches:
                # Контекст: 100 символов до и после
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]

                # Номер строки
                line_num = content[:match.start()].count('\n') + 1

                results.append({
                    'file': str(file_path),
                    'filename': file_path.name,
                    'contact_type': file_path.parent.name,
                    'metadata': metadata,
                    'match': match.group(),
                    'context': context.replace('\n', ' '),
                    'line': line_num,
                    'position': match.start(),
                })

    return results


def search_amount(
    min_amount: float = None,
    max_amount: float = None,
    currency: str = None
) -> List[Dict]:
    """
    Поиск по сумме.

    Args:
        min_amount: Минимальная сумма
        max_amount: Максимальная сумма
        currency: Валюта (RUB, AED, USD)
    """
    results = []
    files = get_all_chat_files()

    # Паттерн для сумм
    amount_pattern = r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)\s*(руб|₽|RUB|AED|дирхам|USD|\$|долл)'

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for match in re.finditer(amount_pattern, content, re.IGNORECASE):
            amount_str = match.group(1).replace(' ', '').replace(',', '')
            try:
                amount = float(amount_str)
            except ValueError:
                continue

            curr = match.group(2).upper()
            if curr in ['РУБ', '₽']:
                curr = 'RUB'
            elif curr in ['ДИРХАМ']:
                curr = 'AED'
            elif curr in ['$', 'ДОЛЛ']:
                curr = 'USD'

            # Фильтрация
            if currency and curr != currency.upper():
                continue
            if min_amount and amount < min_amount:
                continue
            if max_amount and amount > max_amount:
                continue

            # Контекст
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]

            results.append({
                'file': str(file_path),
                'filename': file_path.name,
                'amount': amount,
                'currency': curr,
                'context': context.replace('\n', ' '),
                'line': content[:match.start()].count('\n') + 1,
            })

    return results


def search_date(
    year: int = None,
    month: int = None,
    day: int = None,
    date_from: str = None,
    date_to: str = None
) -> List[Dict]:
    """
    Поиск по дате в чатах.
    """
    results = []
    files = get_all_chat_files()

    # Паттерн для дат
    date_pattern = r'(\d{1,2})[./](\d{1,2})[./](\d{4}|\d{2})'

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for match in re.finditer(date_pattern, content):
            d, m, y = match.groups()
            d, m = int(d), int(m)
            y = int(y) if len(y) == 4 else 2000 + int(y)

            # Фильтрация
            if year and y != year:
                continue
            if month and m != month:
                continue
            if day and d != day:
                continue

            try:
                date = datetime(y, m, d)

                if date_from:
                    from_date = datetime.strptime(date_from, '%Y-%m-%d')
                    if date < from_date:
                        continue

                if date_to:
                    to_date = datetime.strptime(date_to, '%Y-%m-%d')
                    if date > to_date:
                        continue
            except ValueError:
                continue

            # Контекст
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]

            results.append({
                'file': str(file_path),
                'filename': file_path.name,
                'date': f"{d:02d}.{m:02d}.{y}",
                'context': context.replace('\n', ' '),
                'line': content[:match.start()].count('\n') + 1,
            })

    return results


def search_contact(name: str) -> List[Dict]:
    """Поиск чатов по имени контакта."""
    results = []
    files = get_all_chat_files()

    pattern = re.compile(re.escape(name), re.IGNORECASE)

    for file_path in files:
        if pattern.search(file_path.name):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = parse_chat_metadata(content)

            results.append({
                'file': str(file_path),
                'filename': file_path.name,
                'contact_type': file_path.parent.name,
                'metadata': metadata,
            })

    return results


# ═══════════════════════════════════════════════════════════════
# ВЫВОД РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════════════════════════════

def print_results(results: List[Dict], format: str = 'text'):
    """Вывести результаты поиска."""
    if not results:
        print("Ничего не найдено")
        return

    print(f"\nНайдено: {len(results)} совпадений\n")
    print("=" * 60)

    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.get('filename', r.get('file', 'Unknown'))}")
        print(f"    Папка: {r.get('contact_type', '-')}")

        if 'amount' in r:
            print(f"    Сумма: {r['amount']:,.2f} {r['currency']}")
        if 'date' in r:
            print(f"    Дата: {r['date']}")
        if 'match' in r:
            print(f"    Совпадение: {r['match']}")
        if 'line' in r:
            print(f"    Строка: {r['line']}")

        if 'context' in r:
            context = r['context'][:150] + "..." if len(r['context']) > 150 else r['context']
            print(f"    Контекст: ...{context}...")

        if 'metadata' in r and r['metadata']:
            meta = r['metadata']
            if 'phone' in meta:
                print(f"    Телефон: {meta['phone']}")
            if 'topic' in meta:
                print(f"    Тематика: {meta['topic']}")

    print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Поиск по чатам WhatsApp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python search.py "Emirates NBD"              # Текстовый поиск
  python search.py --amount-min 100000         # Суммы от 100 000
  python search.py --amount-min 100 --currency USD  # USD от $100
  python search.py --date 2025-01              # Январь 2025
  python search.py --contact Anna              # Чаты с Anna
  python search.py --date-from 2025-01-01 --date-to 2025-01-31
        """
    )

    parser.add_argument('query', nargs='?', help='Текст для поиска')

    # Поиск по сумме
    parser.add_argument('--amount-min', type=float, help='Минимальная сумма')
    parser.add_argument('--amount-max', type=float, help='Максимальная сумма')
    parser.add_argument('--currency', choices=['RUB', 'AED', 'USD'], help='Валюта')

    # Поиск по дате
    parser.add_argument('--date', help='Дата (YYYY-MM или YYYY-MM-DD)')
    parser.add_argument('--date-from', help='Дата от (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='Дата до (YYYY-MM-DD)')

    # Поиск по контакту
    parser.add_argument('--contact', help='Имя контакта')

    # Опции
    parser.add_argument('-i', '--case-sensitive', action='store_true',
                        help='Учитывать регистр')
    parser.add_argument('--json', action='store_true', help='Вывод в JSON')
    parser.add_argument('--limit', type=int, default=50, help='Лимит результатов')

    args = parser.parse_args()

    results = []

    # Определяем тип поиска
    if args.contact:
        results = search_contact(args.contact)
    elif args.amount_min or args.amount_max or args.currency:
        results = search_amount(args.amount_min, args.amount_max, args.currency)
    elif args.date or args.date_from or args.date_to:
        year, month, day = None, None, None
        if args.date:
            parts = args.date.split('-')
            year = int(parts[0])
            if len(parts) > 1:
                month = int(parts[1])
            if len(parts) > 2:
                day = int(parts[2])
        results = search_date(year, month, day, args.date_from, args.date_to)
    elif args.query:
        results = search_text(args.query, args.case_sensitive)
    else:
        parser.print_help()
        return

    # Ограничение результатов
    if args.limit and len(results) > args.limit:
        print(f"(показано {args.limit} из {len(results)})")
        results = results[:args.limit]

    # Вывод
    if args.json:
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_results(results)


if __name__ == "__main__":
    main()
