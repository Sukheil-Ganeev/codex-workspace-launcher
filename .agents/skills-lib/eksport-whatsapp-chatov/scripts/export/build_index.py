#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание индекса всех чатов
"""

import sys
import os
import re
import glob
import argparse
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def extract_chat_metadata(filepath):
    """Извлекает метаданные из файла чата"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    filename = os.path.basename(filepath)
    parts = filename.replace('.md', '').split('_')

    metadata = {
        'file': filepath,
        'filename': filename,
        'type': parts[0] if len(parts) > 0 else "неизвестно",
        'name': parts[1] if len(parts) > 1 else "неизвестно",
        'topic': parts[2] if len(parts) > 2 else "",
        'period_start': '',
        'period_end': '',
        'messages_count': 0,
        'voice_count': 0,
        'photo_count': 0,
        'pdf_count': 0,
        'total_rub': 0,
        'total_aed': 0,
        'tags': set()
    }

    # Извлечение периода из метаданных
    period_match = re.search(r'\*\*Период:\*\*\s*(\d{2}\.\d{2}\.\d{4})\s*[—-]\s*(\d{2}\.\d{2}\.\d{4})', content)
    if period_match:
        metadata['period_start'] = period_match.group(1)
        metadata['period_end'] = period_match.group(2)

    # Подсчёт сообщений (по паттерну **👤 или **👨)
    metadata['messages_count'] = len(re.findall(r'\*\*[👤👨👩]', content))

    # Подсчёт медиа
    metadata['voice_count'] = len(re.findall(r'🎤 \*\*Голосовое', content))
    metadata['photo_count'] = len(re.findall(r'📷 \*\*(?:Фото|Изображение)', content))
    metadata['pdf_count'] = len(re.findall(r'📄 \*\*(?:PDF|Документ)', content))

    # Подсчёт сумм
    rub_amounts = re.findall(r'(\d{1,3}(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(?:RUB|руб|₽)', content, re.IGNORECASE)
    for amount in rub_amounts:
        try:
            metadata['total_rub'] += float(amount.replace(' ', '').replace(',', ''))
        except:
            pass

    aed_amounts = re.findall(r'(\d{1,3}(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(?:AED|дирхам)', content, re.IGNORECASE)
    for amount in aed_amounts:
        try:
            metadata['total_aed'] += float(amount.replace(' ', '').replace(',', ''))
        except:
            pass

    # Автоматические теги
    if metadata['total_rub'] > 0 or metadata['total_aed'] > 0:
        metadata['tags'].add('финансы')
    if metadata['voice_count'] > 10:
        metadata['tags'].add('много_голосовых')
    if metadata['pdf_count'] > 5:
        metadata['tags'].add('документы')
    if 'обмен' in metadata['topic'].lower():
        metadata['tags'].add('обмен_валюты')
    if 'билет' in metadata['topic'].lower():
        metadata['tags'].add('билеты')
    if 'экскурси' in metadata['topic'].lower():
        metadata['tags'].add('экскурсии')

    return metadata

def build_main_index(chats_dir, output_dir):
    """Создаёт главный индекс"""

    all_metadata = []

    # Сбор метаданных
    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern = os.path.join(chats_dir, subdir, '*.md')
        for filepath in glob.glob(pattern):
            metadata = extract_chat_metadata(filepath)
            if metadata:
                all_metadata.append(metadata)

    print(f"Найдено {len(all_metadata)} чатов")

    os.makedirs(output_dir, exist_ok=True)

    # === index.md ===
    output = []
    output.append("# Индекс чатов")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append("")
    output.append(f"**Всего чатов:** {len(all_metadata)}")
    output.append("")
    output.append("---")
    output.append("")
    output.append("## Все чаты")
    output.append("")
    output.append("| Контакт | Тип | Тематика | Период | Сообщ. | 🎤 | 📷 | 📄 | Сумма RUB | Сумма AED |")
    output.append("|---------|-----|----------|--------|--------|----|----|----|-----------:|----------:|")

    for m in sorted(all_metadata, key=lambda x: x['name']):
        period = f"{m['period_start']}—{m['period_end']}" if m['period_start'] else "N/A"
        rub = f"{m['total_rub']:,.0f}" if m['total_rub'] > 0 else "-"
        aed = f"{m['total_aed']:,.0f}" if m['total_aed'] > 0 else "-"

        output.append(
            f"| [{m['name']}]({m['type']}/{m['filename']}) | {m['type']} | {m['topic']} | "
            f"{period} | {m['messages_count']} | {m['voice_count']} | {m['photo_count']} | "
            f"{m['pdf_count']} | {rub} | {aed} |"
        )

    # Итоги
    total_rub = sum(m['total_rub'] for m in all_metadata)
    total_aed = sum(m['total_aed'] for m in all_metadata)
    total_msg = sum(m['messages_count'] for m in all_metadata)

    output.append("")
    output.append("---")
    output.append("")
    output.append("## Итоги")
    output.append("")
    output.append(f"- **Всего сообщений:** {total_msg:,}")
    output.append(f"- **Общий оборот RUB:** {total_rub:,.0f} ₽")
    output.append(f"- **Общий оборот AED:** {total_aed:,.0f} AED")

    with open(os.path.join(output_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # === по_типам.md ===
    output = []
    output.append("# Чаты по типам контактов")
    output.append("")

    by_type = defaultdict(list)
    for m in all_metadata:
        by_type[m['type']].append(m)

    type_names = {'клиенты': 'Клиенты', 'агенты': 'Агенты', 'поставщики': 'Поставщики', 'сотрудники': 'Сотрудники'}

    for contact_type in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        chats = by_type.get(contact_type, [])
        output.append(f"## {type_names.get(contact_type, contact_type)} ({len(chats)})")
        output.append("")

        if chats:
            for m in sorted(chats, key=lambda x: x['name']):
                output.append(f"- **{m['name']}** — {m['topic']} ({m['messages_count']} сообщ.)")
        else:
            output.append("*Нет чатов*")

        output.append("")

    with open(os.path.join(output_dir, 'по_типам.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # === теги.md ===
    output = []
    output.append("# Теги и категории")
    output.append("")

    all_tags = defaultdict(list)
    for m in all_metadata:
        for tag in m['tags']:
            all_tags[tag].append(m)

    for tag in sorted(all_tags.keys()):
        chats = all_tags[tag]
        output.append(f"## #{tag} ({len(chats)})")
        output.append("")
        for m in chats:
            output.append(f"- {m['name']} ({m['type']})")
        output.append("")

    with open(os.path.join(output_dir, 'теги.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"Индекс создан в: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Создание индекса чатов")
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")
    parser.add_argument("-o", "--output-dir", default="D:/Downloads/Chats/_индекс")

    args = parser.parse_args()
    build_main_index(args.chats_dir, args.output_dir)
