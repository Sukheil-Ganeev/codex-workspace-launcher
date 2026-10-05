#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Генерация шаблонов сообщений на основе анализа чатов.
Находит часто используемые фразы и создаёт шаблоны.
"""

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, TEMPLATES_DIR, CONTACT_TYPES, ensure_directories

# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

def extract_messages(content: str, sender: str = None) -> List[str]:
    """Извлечь сообщения из чата."""
    messages = []

    # Паттерн для сообщений: **HH:MM Имя:** или **Имя** [HH:MM:SS]
    pattern = r'\*\*(?:\d{1,2}:\d{2}\s+)?([^*]+)\*\*(?:\s*\[\d{2}:\d{2}:\d{2}\])?\s*\n(.+?)(?=\n\*\*|\n##|\Z)'

    for match in re.finditer(pattern, content, re.DOTALL):
        name = match.group(1).strip()
        text = match.group(2).strip()

        if sender and sender.lower() not in name.lower():
            continue

        # Убираем медиа-маркеры
        if text.startswith('🎤') or text.startswith('📷') or text.startswith('📄'):
            continue

        # Убираем слишком короткие
        if len(text) < 5:
            continue

        messages.append(text)

    return messages


def find_frequent_phrases(messages: List[str], min_count: int = 2) -> List[tuple]:
    """Найти часто используемые фразы."""
    # Считаем полные сообщения
    counter = Counter(messages)

    # Фильтруем по минимальному количеству
    frequent = [(phrase, count) for phrase, count in counter.items() if count >= min_count]

    return sorted(frequent, key=lambda x: -x[1])


def categorize_templates(messages: List[str]) -> Dict[str, List[str]]:
    """Категоризировать шаблоны по типам."""
    categories = {
        'приветствия': [],
        'прощания': [],
        'подтверждения': [],
        'вопросы': [],
        'благодарности': [],
        'отказы': [],
        'цены': [],
        'прочее': [],
    }

    patterns = {
        'приветствия': [r'^(привет|здравствуй|добр|hi|hello)', r'^доброе утро', r'^добрый день'],
        'прощания': [r'(до свидания|пока|всего доброго|до связи)', r'спасибо.*до'],
        'подтверждения': [r'^(да|ok|ок|хорошо|договорились|принято|понял)', r'^done', r'^готово'],
        'вопросы': [r'\?$', r'^(как|когда|сколько|где|что|какой)'],
        'благодарности': [r'^спасибо', r'^благодар'],
        'отказы': [r'^(нет|не могу|к сожалению|извини)', r'не получится'],
        'цены': [r'\d+\s*(руб|aed|usd|\$|₽)', r'курс', r'стоимость'],
    }

    for msg in messages:
        msg_lower = msg.lower()
        categorized = False

        for category, cat_patterns in patterns.items():
            for pattern in cat_patterns:
                if re.search(pattern, msg_lower):
                    if msg not in categories[category]:
                        categories[category].append(msg)
                    categorized = True
                    break
            if categorized:
                break

        if not categorized and msg not in categories['прочее']:
            categories['прочее'].append(msg)

    return categories


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТА
# ═══════════════════════════════════════════════════════════════

def generate_templates_report(
    all_messages: List[str],
    frequent: List[tuple],
    categories: Dict[str, List[str]]
) -> str:
    """Сгенерировать отчёт с шаблонами."""
    from datetime import datetime

    report = f"""# Шаблоны сообщений

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*
*Проанализировано сообщений: {len(all_messages)}*

---

## Часто используемые фразы

| Фраза | Раз |
|-------|-----|
"""

    for phrase, count in frequent[:30]:
        # Обрезаем длинные фразы
        short = phrase[:50] + '...' if len(phrase) > 50 else phrase
        report += f"| {short} | {count} |\n"

    report += "\n---\n\n## По категориям\n\n"

    for category, templates in categories.items():
        if templates:
            report += f"### {category.title()}\n\n"
            for tmpl in templates[:10]:
                short = tmpl[:80] + '...' if len(tmpl) > 80 else tmpl
                report += f"- {short}\n"
            report += "\n"

    return report


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТКА
# ═══════════════════════════════════════════════════════════════

def process_all_chats(sender_filter: str = None) -> tuple:
    """Обработать все чаты."""
    all_messages = []

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                messages = extract_messages(content, sender_filter)
                all_messages.extend(messages)

    frequent = find_frequent_phrases(all_messages)
    categories = categorize_templates(all_messages)

    return all_messages, frequent, categories


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Генерация шаблонов сообщений',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python generate_templates.py                    # Все чаты
  python generate_templates.py --sender Сухейль   # Только мои сообщения
  python generate_templates.py -o templates.md    # Сохранить
        """
    )

    parser.add_argument('input', nargs='?', help='Входной файл (или все чаты)')
    parser.add_argument('--sender', help='Фильтр по отправителю')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('--min-count', type=int, default=2, help='Минимум повторений')

    args = parser.parse_args()

    ensure_directories()

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()

        messages = extract_messages(content, args.sender)
        frequent = find_frequent_phrases(messages, args.min_count)
        categories = categorize_templates(messages)
    else:
        messages, frequent, categories = process_all_chats(args.sender)

    report = generate_templates_report(messages, frequent, categories)

    if args.output:
        output_path = Path(args.output)
    else:
        from datetime import datetime
        output_path = TEMPLATES_DIR / f"шаблоны_{datetime.now().strftime('%Y-%m-%d')}.md"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ Сохранено: {output_path}")
    print(f"  Сообщений: {len(messages)}")
    print(f"  Частых фраз: {len(frequent)}")


if __name__ == "__main__":
    main()
