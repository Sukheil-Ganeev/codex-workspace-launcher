#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерация статистики для чата
"""

import sys
import os
import re
import argparse
from datetime import datetime
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

def calculate_statistics(filepath):
    """Вычисляет статистику для файла чата"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    stats = {
        'total_messages': 0,
        'voice_messages': 0,
        'photos': 0,
        'pdfs': 0,
        'contacts_vcf': 0,
        'days_active': 0,
        'first_date': '',
        'last_date': '',
        'messages_by_sender': defaultdict(int),
        'messages_by_date': defaultdict(int),
        'avg_messages_per_day': 0,
        'most_active_day': '',
        'total_rub': 0,
        'total_aed': 0,
        'operations_count': 0,
    }

    # Подсчёт сообщений
    message_pattern = r'\*\*([👤👨👩][^*]+)\*\*\s*\[(\d{2}:\d{2}:\d{2})\]'
    messages = re.findall(message_pattern, content)
    stats['total_messages'] = len(messages)

    # Подсчёт по отправителям
    for sender, time in messages:
        sender_clean = sender.strip()
        stats['messages_by_sender'][sender_clean] += 1

    # Подсчёт медиа
    stats['voice_messages'] = len(re.findall(r'🎤 \*\*Голосовое', content))
    stats['photos'] = len(re.findall(r'📷 \*\*(?:Фото|Изображение)', content))
    stats['pdfs'] = len(re.findall(r'📄 \*\*(?:PDF|Документ)', content))
    stats['contacts_vcf'] = len(re.findall(r'📇 \*\*Контакт', content))

    # Даты
    dates = re.findall(r'### (\d{2}\.\d{2}\.\d{4})', content)
    if dates:
        stats['first_date'] = dates[0]
        stats['last_date'] = dates[-1]
        stats['days_active'] = len(set(dates))

        # Сообщения по датам
        current_date = None
        for line in content.split('\n'):
            date_match = re.match(r'### (\d{2}\.\d{2}\.\d{4})', line)
            if date_match:
                current_date = date_match.group(1)
            elif current_date and re.match(r'\*\*[👤👨👩]', line):
                stats['messages_by_date'][current_date] += 1

        if stats['messages_by_date']:
            stats['most_active_day'] = max(stats['messages_by_date'], key=stats['messages_by_date'].get)
            stats['avg_messages_per_day'] = stats['total_messages'] / max(stats['days_active'], 1)

    # Финансы
    rub_amounts = re.findall(r'Сумма[:\s]*(\d{1,3}(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(?:RUB|руб|₽)', content, re.IGNORECASE)
    for amount in rub_amounts:
        try:
            stats['total_rub'] += float(amount.replace(' ', '').replace(',', ''))
            stats['operations_count'] += 1
        except:
            pass

    aed_amounts = re.findall(r'Сумма[:\s]*(\d{1,3}(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(?:AED|дирхам)', content, re.IGNORECASE)
    for amount in aed_amounts:
        try:
            stats['total_aed'] += float(amount.replace(' ', '').replace(',', ''))
        except:
            pass

    return stats

def generate_statistics_section(stats):
    """Генерирует Markdown секцию со статистикой"""

    output = []
    output.append("## Статистика переписки")
    output.append("")
    output.append("| Метрика | Значение |")
    output.append("|---------|----------|")
    output.append(f"| Всего сообщений | {stats['total_messages']} |")
    output.append(f"| Голосовых | {stats['voice_messages']} |")
    output.append(f"| Фото | {stats['photos']} |")
    output.append(f"| PDF документов | {stats['pdfs']} |")
    output.append(f"| Контактов VCF | {stats['contacts_vcf']} |")
    output.append(f"| Дней переписки | {stats['days_active']} |")
    output.append(f"| Период | {stats['first_date']} — {stats['last_date']} |")
    output.append(f"| Среднее сообщ./день | {stats['avg_messages_per_day']:.1f} |")

    if stats['most_active_day']:
        output.append(f"| Самый активный день | {stats['most_active_day']} ({stats['messages_by_date'].get(stats['most_active_day'], 0)} сообщ.) |")

    output.append("")

    # Распределение по отправителям
    if stats['messages_by_sender']:
        output.append("### По отправителям")
        output.append("")
        total = stats['total_messages']
        for sender, count in sorted(stats['messages_by_sender'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            output.append(f"- {sender}: {count} ({pct:.0f}%)")
        output.append("")

    # Финансы
    if stats['total_rub'] > 0 or stats['total_aed'] > 0:
        output.append("### Финансы")
        output.append("")
        if stats['total_rub'] > 0:
            output.append(f"- **Оборот RUB:** {stats['total_rub']:,.0f} ₽")
        if stats['total_aed'] > 0:
            output.append(f"- **Оборот AED:** {stats['total_aed']:,.0f} AED")
        output.append(f"- **Операций:** {stats['operations_count']}")
        output.append("")

    return '\n'.join(output)

def add_statistics_to_chat(filepath, output_path=None):
    """Добавляет секцию статистики в файл чата"""

    stats = calculate_statistics(filepath)
    if not stats:
        print(f"Не удалось вычислить статистику для {filepath}")
        return

    stats_section = generate_statistics_section(stats)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Проверяем, есть ли уже статистика
    if '## Статистика переписки' in content:
        # Обновляем существующую
        content = re.sub(
            r'## Статистика переписки.*?(?=## |$)',
            stats_section + '\n',
            content,
            flags=re.DOTALL
        )
    else:
        # Добавляем перед "## История переписки" или в конец
        if '## История переписки' in content:
            content = content.replace(
                '## История переписки',
                stats_section + '\n---\n\n## История переписки'
            )
        else:
            content = content + '\n\n---\n\n' + stats_section

    output_file = output_path or filepath
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Статистика добавлена: {output_file}")

def process_all_chats(chats_dir):
    """Добавляет статистику во все чаты"""

    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern = os.path.join(chats_dir, subdir, '*.md')
        for filepath in glob.glob(pattern):
            add_statistics_to_chat(filepath)

if __name__ == "__main__":
    import glob

    parser = argparse.ArgumentParser(description="Генерация статистики чата")
    parser.add_argument("input", nargs='?', help="Путь к файлу чата или папке")
    parser.add_argument("--all", action="store_true", help="Обработать все чаты")
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")

    args = parser.parse_args()

    if args.all:
        process_all_chats(args.chats_dir)
    elif args.input:
        if os.path.isfile(args.input):
            add_statistics_to_chat(args.input)
        else:
            print(f"Файл не найден: {args.input}")
    else:
        print("Укажите файл или используйте --all для обработки всех чатов")
