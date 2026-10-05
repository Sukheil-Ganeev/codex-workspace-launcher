#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Организация медиафайлов из экспортов чатов
"""

import sys
import os
import re
import glob
import shutil
import argparse
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def categorize_file(filename, description=""):
    """Определяет категорию файла по имени и описанию"""

    filename_lower = filename.lower()
    description_lower = description.lower()

    # PDF файлы
    if filename_lower.endswith('.pdf'):
        if any(word in description_lower for word in ['чек', 'квитанция', 'перевод', 'receipt', 'transaction']):
            return 'чеки'
        elif any(word in description_lower for word in ['счёт', 'invoice', 'билет', 'ticket']):
            return 'счета'
        else:
            return 'документы'

    # Изображения
    if filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        if any(word in description_lower for word in ['курс', 'конвертер', 'google', 'калькулятор']):
            return 'скриншоты/курсы'
        elif any(word in description_lower for word in ['чек', 'перевод', 'банк', 'receipt']):
            return 'скриншоты/переводы'
        elif any(word in description_lower for word in ['ошибка', 'error', 'недоступен']):
            return 'скриншоты/ошибки'
        elif any(word in description_lower for word in ['открытка', 'поздравлени']):
            return 'открытки'
        else:
            return 'фото'

    return 'прочее'

def extract_media_info_from_chat(chat_file):
    """Извлекает информацию о медиафайлах из файла чата"""

    media_info = []

    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return media_info

    # Ищем блоки с медиа
    # Формат: 📄 **PDF (filename):** или 📷 **Фото (filename):**
    patterns = [
        (r'📄 \*\*(?:PDF|Документ)[^(]*\(([^)]+)\)[^:]*:\*\*\s*([^📷🎤📄]*?)(?=📷|🎤|📄|###|\n\n\n|$)', 'pdf'),
        (r'📷 \*\*(?:Фото|Изображение)[^(]*\(([^)]+)\)[^:]*:\*\*\s*([^📷🎤📄]*?)(?=📷|🎤|📄|###|\n\n\n|$)', 'image'),
    ]

    for pattern, media_type in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for filename, description in matches:
            # Извлекаем дату из имени файла если есть
            date_match = re.search(r'(\d{4})-?(\d{2})-?(\d{2})', filename)
            date_str = f"{date_match.group(3)}.{date_match.group(2)}.{date_match.group(1)}" if date_match else ""

            media_info.append({
                'filename': filename.strip(),
                'description': description.strip()[:200],
                'type': media_type,
                'date': date_str,
                'category': categorize_file(filename, description)
            })

    return media_info

def organize_media_files(chats_dir, extracted_dir, output_dir):
    """
    Организует медиафайлы из папок извлечённых чатов

    Args:
        chats_dir: папка с готовыми MD файлами чатов
        extracted_dir: папка с извлечёнными файлами (PDF, JPG и т.д.)
        output_dir: папка для организованных медиафайлов
    """

    # Создаём структуру папок
    categories = ['чеки', 'счета', 'документы', 'скриншоты/курсы', 'скриншоты/переводы',
                  'скриншоты/ошибки', 'открытки', 'фото', 'прочее']

    for category in categories:
        os.makedirs(os.path.join(output_dir, category), exist_ok=True)

    # Сбор информации о медиа из чатов
    all_media = {}

    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern = os.path.join(chats_dir, subdir, '*.md')
        for chat_file in glob.glob(pattern):
            media_info = extract_media_info_from_chat(chat_file)
            for info in media_info:
                all_media[info['filename']] = info

    print(f"Найдено {len(all_media)} медиафайлов в чатах")

    # Поиск и копирование файлов
    copied = 0
    not_found = []

    # Ищем файлы в папке extracted
    if os.path.exists(extracted_dir):
        for root, dirs, files in os.walk(extracted_dir):
            for filename in files:
                src_path = os.path.join(root, filename)

                # Определяем категорию
                info = all_media.get(filename, {})
                description = info.get('description', '')
                category = categorize_file(filename, description)

                # Формируем новое имя с датой
                date_prefix = info.get('date', '').replace('.', '-')
                if date_prefix:
                    new_filename = f"{date_prefix}_{filename}"
                else:
                    new_filename = filename

                # Копируем файл
                dst_path = os.path.join(output_dir, category, new_filename)

                try:
                    shutil.copy2(src_path, dst_path)
                    copied += 1
                except Exception as e:
                    print(f"Ошибка копирования {filename}: {e}")

    # Создаём индекс медиафайлов
    index_content = []
    index_content.append("# Индекс медиафайлов")
    index_content.append("")
    index_content.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    index_content.append("")

    for category in categories:
        category_path = os.path.join(output_dir, category)
        if os.path.exists(category_path):
            files = os.listdir(category_path)
            if files:
                index_content.append(f"## {category} ({len(files)})")
                index_content.append("")
                for f in sorted(files)[:20]:  # Показываем первые 20
                    index_content.append(f"- {f}")
                if len(files) > 20:
                    index_content.append(f"- ... и ещё {len(files) - 20} файлов")
                index_content.append("")

    with open(os.path.join(output_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_content))

    print(f"Скопировано файлов: {copied}")
    print(f"Медиа организованы в: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Организация медиафайлов")
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")
    parser.add_argument("--extracted-dir", default="D:/Downloads", help="Папка с извлечёнными файлами")
    parser.add_argument("-o", "--output-dir", default="D:/Downloads/Chats/_медиа")

    args = parser.parse_args()
    organize_media_files(args.chats_dir, args.extracted_dir, args.output_dir)
