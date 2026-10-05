#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка полного MD документа из всех источников
"""

import sys
import os
import re
import argparse
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_analysis_file(filepath):
    """Парсит файл анализа в словарь {filename: content}"""
    if not os.path.exists(filepath):
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {}
    parts = re.split(r'===\s*(.+?)\s*===', content)

    for i in range(1, len(parts), 2):
        filename = parts[i].strip()
        text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        result[filename] = text

    return result

def parse_chat_message(line):
    """Парсит строку чата WhatsApp"""
    pattern = r'\[(\d{2}\.\d{2}\.\d{4}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
    match = re.match(pattern, line)

    if match:
        return {
            'date': match.group(1),
            'time': match.group(2),
            'sender': match.group(3).strip(),
            'message': match.group(4)
        }
    return None

def replace_attachments(message, transcripts, images, pdfs):
    """Заменяет ссылки на файлы расшифровками"""

    # Голосовые сообщения
    voice_pattern = r'(PTT-\d{8}-WA\d{4}\.opus)\s*\(file attached\)'
    for match in re.finditer(voice_pattern, message):
        filename = match.group(1)
        if filename in transcripts:
            replacement = f"\n🎤 **Голосовое:**\n> {transcripts[filename]}\n"
            message = message.replace(match.group(0), replacement)

    # Изображения
    img_pattern = r'(IMG-\d{8}-WA\d{4}\.jpg)\s*\(file attached\)'
    for match in re.finditer(img_pattern, message):
        filename = match.group(1)
        if filename in images:
            replacement = f"\n📷 **Фото:** {images[filename]}\n"
            message = message.replace(match.group(0), replacement)

    # PDF
    pdf_pattern = r'([^/\\]+\.pdf)\s*\(file attached\)'
    for match in re.finditer(pdf_pattern, message):
        filename = match.group(1)
        if filename in pdfs:
            replacement = f"\n📄 **PDF:** {pdfs[filename]}\n"
            message = message.replace(match.group(0), replacement)

    # VCF
    vcf_pattern = r'([^/\\]+\.vcf)\s*\(file attached\)'
    for match in re.finditer(vcf_pattern, message):
        message = message.replace(match.group(0), "\n📇 **Контакт прикреплён**\n")

    return message

def build_document(base_dir, output_file, contact_name, contact_type, topic, notes=""):
    """Собирает полный MD документ"""

    # Загрузка данных
    transcripts = parse_analysis_file(os.path.join(base_dir, "transcripts.txt"))
    images = parse_analysis_file(os.path.join(base_dir, "images_analysis.txt"))
    pdfs = parse_analysis_file(os.path.join(base_dir, "pdf_analysis.txt"))

    # Чтение оригинального чата
    chat_file = os.path.join(base_dir, "_chat.txt")
    if not os.path.exists(chat_file):
        chat_files = [f for f in os.listdir(base_dir) if f.endswith('.txt') and 'transcript' not in f.lower()]
        if chat_files:
            chat_file = os.path.join(base_dir, chat_files[0])

    with open(chat_file, 'r', encoding='utf-8') as f:
        chat_lines = f.readlines()

    # Определение периода
    dates = []
    for line in chat_lines:
        parsed = parse_chat_message(line)
        if parsed:
            dates.append(parsed['date'])

    period_start = dates[0] if dates else "N/A"
    period_end = dates[-1] if dates else "N/A"

    # Сборка документа
    output = []

    # Заголовок
    type_ru = {"клиент": "Клиент", "агент": "Агент", "поставщик": "Поставщик", "сотрудник": "Сотрудник"}
    output.append(f"# {type_ru.get(contact_type, contact_type)}: {contact_name}")
    output.append("")
    output.append("## Метаданные")
    output.append(f"- **Тип:** {contact_type}")
    output.append(f"- **Период:** {period_start} — {period_end}")
    output.append(f"- **Тематика:** {topic}")
    if notes:
        output.append(f"- **Заметки:** {notes}")
    output.append("")
    output.append("---")
    output.append("")

    # История переписки
    output.append("## История переписки")
    output.append("")

    current_date = None

    for line in chat_lines:
        parsed = parse_chat_message(line)

        if parsed:
            if parsed['date'] != current_date:
                current_date = parsed['date']
                output.append(f"### {current_date}")
                output.append("")

            message = replace_attachments(
                parsed['message'],
                transcripts,
                images,
                pdfs
            )

            sender_icon = "👤" if contact_name.lower() in parsed['sender'].lower() else "👨"
            output.append(f"**{sender_icon} {parsed['sender']}** [{parsed['time']}]")
            output.append(message)
            output.append("")

    # Сохранение
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"Документ сохранён: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сборка документа переписки")
    parser.add_argument("directory", help="Папка с обработанными файлами")
    parser.add_argument("-o", "--output", required=True, help="Путь к итоговому файлу")
    parser.add_argument("-n", "--name", required=True, help="Имя контакта")
    parser.add_argument("-t", "--type", required=True, choices=["клиент", "агент", "поставщик", "сотрудник"])
    parser.add_argument("--topic", required=True, help="Тематика переписки")
    parser.add_argument("--notes", default="", help="Заметки")

    args = parser.parse_args()

    build_document(args.directory, args.output, args.name, args.type, args.topic, args.notes)
