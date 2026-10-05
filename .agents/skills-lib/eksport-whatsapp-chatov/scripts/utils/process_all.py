#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Единый пайплайн обработки WhatsApp чата.
Автоматически определяет тип контакта и тематику.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (CHATS_DIR, CONTACT_TYPES, WHISPER_MODEL,
                    WHISPER_DEVICE, WHISPER_LANGUAGE, ensure_directories)

# ═══════════════════════════════════════════════════════════════
# АВТООПРЕДЕЛЕНИЕ
# ═══════════════════════════════════════════════════════════════

def auto_detect_contact_type(content: str, filename: str = "") -> str:
    """
    Автоматически определить тип контакта по содержимому чата.

    Returns:
        клиент | агент | поставщик | сотрудник
    """
    content_lower = content.lower()
    filename_lower = filename.lower()

    # Паттерны для агентов
    agent_patterns = [
        r'турагент', r'агентск', r'комисси[яю]', r'ваш процент',
        r'тураге?нтств', r'партнёр', r'субагент',
        r'agency', r'travel agent', r'commission',
    ]

    # Паттерны для поставщиков
    supplier_patterns = [
        r'обмен(?:ник)?', r'курс\s+(?:на\s+)?(?:сегодня|завтра)',
        r'водител[ья]', r'трансфер\s+(?:из|в|до)',
        r'гид[а-я]*\s', r'яхт[аы]', r'supplier',
        r'реквизит', r'перевод(?:а|ы)?\s+(?:на|в)',
    ]

    # Паттерны для сотрудников
    employee_patterns = [
        r'коллег', r'офис', r'работ[ау]', r'зарплат',
        r'отпуск', r'смен[аы]', r'график',
    ]

    # Паттерны для клиентов
    client_patterns = [
        r'бронирован', r'хоч[уе]\s+(?:заказать|забронировать)',
        r'экскурси[яю]', r'тур\s+(?:в|на|по)',
        r'сколько\s+(?:стоит|будет)', r'цен[ау]',
        r'билет[ыа]?', r'отел[ья]',
    ]

    scores = {
        'агент': sum(1 for p in agent_patterns if re.search(p, content_lower)),
        'поставщик': sum(1 for p in supplier_patterns if re.search(p, content_lower)),
        'сотрудник': sum(1 for p in employee_patterns if re.search(p, content_lower)),
        'клиент': sum(1 for p in client_patterns if re.search(p, content_lower)),
    }

    # Возвращаем тип с наибольшим счётом
    max_type = max(scores, key=scores.get)
    if scores[max_type] > 0:
        return max_type + 'ы' if max_type != 'клиент' else 'клиенты'

    # По умолчанию - клиент
    return 'клиенты'


def auto_detect_topic(content: str) -> str:
    """
    Автоматически определить тематику переписки.

    Returns:
        Строка тематики (обмен-валюты, туры, трансферы и т.д.)
    """
    content_lower = content.lower()

    topic_patterns = {
        'обмен-валюты': [r'обмен', r'курс', r'руб', r'дирхам', r'aed', r'usd', r'валют'],
        'туры': [r'экскурси', r'тур\b', r'safari', r'сафари', r'desert', r'пустын'],
        'трансферы': [r'трансфер', r'встреч[ау]', r'аэропорт', r'transfer', r'pickup'],
        'билеты': [r'билет', r'ticket', r'парк', r'аттракцион', r'музей'],
        'аренда-авто': [r'аренд', r'машин', r'авто', r'car\s+rent', r'прокат'],
        'яхты': [r'яхт', r'yacht', r'катер', r'boat', r'круиз', r'marina'],
        'рестораны': [r'ресторан', r'ужин', r'dinner', r'кафе', r'брunch', r'обед'],
        'отели': [r'отел[ья]', r'hotel', r'номер', r'бронирован', r'booking'],
        'визы': [r'виз[ау]', r'visa', r'документ', r'паспорт'],
        'общее': [],
    }

    scores = {}
    for topic, patterns in topic_patterns.items():
        scores[topic] = sum(1 for p in patterns if re.search(p, content_lower))

    max_topic = max(scores, key=scores.get)
    if scores[max_topic] > 0:
        return max_topic

    return 'общее'


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТКА АРХИВА
# ═══════════════════════════════════════════════════════════════

def extract_zip(zip_path: str, extract_dir: str = None) -> Path:
    """Распаковать ZIP архив."""
    zip_path = Path(zip_path)

    if extract_dir is None:
        extract_dir = zip_path.parent / f"{zip_path.stem}_extracted"
    else:
        extract_dir = Path(extract_dir)

    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)

    print(f"✓ Распаковано в: {extract_dir}")
    return extract_dir


def find_chat_file(extract_dir: Path) -> Path:
    """Найти файл чата в распакованной папке."""
    patterns = ['_chat.txt', 'WhatsApp Chat*.txt', '*.txt']

    for pattern in patterns:
        files = list(extract_dir.glob(pattern))
        if files:
            return files[0]

    raise FileNotFoundError(f"Файл чата не найден в {extract_dir}")


def transcribe_audio_files(extract_dir: Path) -> dict:
    """Расшифровать все аудиофайлы через Whisper."""
    audio_extensions = ['.opus', '.ogg', '.m4a', '.mp3', '.wav']
    audio_files = []

    for ext in audio_extensions:
        audio_files.extend(extract_dir.glob(f"*{ext}"))

    if not audio_files:
        print("  Аудиофайлы не найдены")
        return {}

    print(f"  Найдено аудиофайлов: {len(audio_files)}")

    transcripts = {}
    try:
        import whisper
        model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)

        for i, audio_file in enumerate(audio_files, 1):
            print(f"  [{i}/{len(audio_files)}] {audio_file.name}...", end=" ")
            try:
                result = model.transcribe(
                    str(audio_file),
                    language=WHISPER_LANGUAGE,
                    fp16=(WHISPER_DEVICE == "cuda")
                )
                transcripts[audio_file.name] = result["text"]
                print("✓")
            except Exception as e:
                print(f"✗ {e}")
                transcripts[audio_file.name] = f"[Ошибка расшифровки: {e}]"

    except ImportError:
        print("  ⚠ Whisper не установлен. Пропускаем расшифровку.")

    return transcripts


def analyze_media_files(extract_dir: Path) -> dict:
    """Получить список медиафайлов для анализа."""
    media = {
        'images': list(extract_dir.glob("*.jpg")) + list(extract_dir.glob("*.jpeg")) + list(extract_dir.glob("*.png")),
        'pdfs': list(extract_dir.glob("*.pdf")),
        'vcfs': list(extract_dir.glob("*.vcf")),
        'videos': list(extract_dir.glob("*.mp4")) + list(extract_dir.glob("*.3gp")),
    }

    print(f"  Изображений: {len(media['images'])}")
    print(f"  PDF: {len(media['pdfs'])}")
    print(f"  VCF: {len(media['vcfs'])}")
    print(f"  Видео: {len(media['videos'])}")

    return media


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def process_chat(
    zip_path: str,
    contact_name: str = None,
    contact_type: str = None,
    topic: str = None,
    extract_dir: str = None,
    skip_whisper: bool = False,
    keep_extracted: bool = False
) -> dict:
    """
    Полный пайплайн обработки WhatsApp чата.

    Args:
        zip_path: Путь к ZIP архиву
        contact_name: Имя контакта (автоопределение из имени файла)
        contact_type: Тип контакта (автоопределение из содержимого)
        topic: Тематика (автоопределение из содержимого)
        extract_dir: Папка для распаковки
        skip_whisper: Пропустить расшифровку аудио
        keep_extracted: Сохранить распакованную папку

    Returns:
        Словарь с результатами обработки
    """
    zip_path = Path(zip_path)
    ensure_directories()

    print(f"\n{'='*60}")
    print(f"Обработка: {zip_path.name}")
    print(f"{'='*60}")

    # 1. Распаковка
    print("\n[1/5] Распаковка архива...")
    extracted = extract_zip(zip_path, extract_dir)

    # 2. Чтение чата
    print("\n[2/5] Чтение чата...")
    chat_file = find_chat_file(extracted)
    with open(chat_file, 'r', encoding='utf-8') as f:
        chat_content = f.read()
    print(f"✓ Прочитано {len(chat_content)} символов")

    # 3. Автоопределение
    print("\n[3/5] Автоопределение параметров...")

    if contact_name is None:
        # Извлекаем имя из названия архива
        name_match = re.search(r'(?:Chat|Чат)\s+(?:с\s+)?(.+?)(?:\s+\d|\s*\.zip)',
                              zip_path.name, re.IGNORECASE)
        if name_match:
            contact_name = name_match.group(1).strip()
        else:
            contact_name = zip_path.stem.replace("_", " ")
    print(f"  Имя: {contact_name}")

    if contact_type is None:
        contact_type = auto_detect_contact_type(chat_content, zip_path.name)
    print(f"  Тип: {contact_type}")

    if topic is None:
        topic = auto_detect_topic(chat_content)
    print(f"  Тематика: {topic}")

    # 4. Расшифровка аудио
    transcripts = {}
    if not skip_whisper:
        print("\n[4/5] Расшифровка аудиофайлов...")
        transcripts = transcribe_audio_files(extracted)
    else:
        print("\n[4/5] Расшифровка пропущена (--skip-whisper)")

    # 5. Анализ медиа
    print("\n[5/5] Анализ медиафайлов...")
    media = analyze_media_files(extracted)

    # Результат
    result = {
        'zip_path': str(zip_path),
        'extract_dir': str(extracted),
        'chat_file': str(chat_file),
        'contact_name': contact_name,
        'contact_type': contact_type,
        'topic': topic,
        'chat_content': chat_content,
        'transcripts': transcripts,
        'media': {k: [str(f) for f in v] for k, v in media.items()},
        'output_filename': f"{contact_type[:-1]}_{contact_name.replace(' ', '_')}_{topic}.md",
        'output_dir': str(CHATS_DIR / contact_type),
    }

    # Удаление временной папки
    if not keep_extracted:
        print(f"\n  Удаляем временную папку: {extracted}")
        # shutil.rmtree(extracted)  # Раскомментировать для авто-удаления

    print(f"\n{'='*60}")
    print(f"✓ Готово! Следующий шаг: создать MD документ")
    print(f"  Файл: {result['output_dir']}/{result['output_filename']}")
    print(f"{'='*60}")

    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Единый пайплайн обработки WhatsApp чата',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python process_all.py "Чат WhatsApp с Anna.zip"
  python process_all.py chat.zip --name "Anna" --type поставщики
  python process_all.py chat.zip --skip-whisper --keep-extracted
        """
    )

    parser.add_argument('zip_path', nargs='?', help='Путь к ZIP архиву')
    parser.add_argument('-n', '--name', dest='contact_name', help='Имя контакта')
    parser.add_argument('-t', '--type', dest='contact_type',
                        choices=CONTACT_TYPES, help='Тип контакта')
    parser.add_argument('--topic', help='Тематика переписки')
    parser.add_argument('-o', '--output', dest='extract_dir',
                        help='Папка для распаковки')
    parser.add_argument('--skip-whisper', action='store_true',
                        help='Пропустить расшифровку аудио')
    parser.add_argument('--keep-extracted', action='store_true',
                        help='Сохранить распакованную папку')
    parser.add_argument('--dry-run', action='store_true',
                        help='Только показать параметры')

    args = parser.parse_args()

    if not args.zip_path:
        parser.print_help()
        return

    if args.dry_run:
        print("Режим --dry-run: только показать параметры")
        print(f"  ZIP: {args.zip_path}")
        print(f"  Имя: {args.contact_name or '(авто)'}")
        print(f"  Тип: {args.contact_type or '(авто)'}")
        print(f"  Тема: {args.topic or '(авто)'}")
        return

    result = process_chat(
        zip_path=args.zip_path,
        contact_name=args.contact_name,
        contact_type=args.contact_type,
        topic=args.topic,
        extract_dir=args.extract_dir,
        skip_whisper=args.skip_whisper,
        keep_extracted=args.keep_extracted
    )

    # Сохраняем результат для дальнейшей обработки
    import json
    result_file = Path(result['extract_dir']) / '_process_result.json'

    # Убираем большие данные из JSON
    result_for_json = {k: v for k, v in result.items() if k != 'chat_content'}

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result_for_json, f, ensure_ascii=False, indent=2)

    print(f"\nРезультат сохранён: {result_file}")


if __name__ == "__main__":
    main()
