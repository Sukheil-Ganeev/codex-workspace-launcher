#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Парсинг всех chat.txt из двух источников в единый JSONL файл.

Обрабатывает ~3050 чатов:
- D:/Downloads/экспорт чатов с ватсапа/ (1063 чата, source="whatsapp")
- D:/Downloads/экспорт чатов с ватсап бизнеса/ (1987 чатов, source="wa_business")

Результат: D:/Downloads/Chats/_база/raw/all_messages.jsonl
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Импорт конфигурации из того же каталога
from config import (
    RAW_DIR,
    EXPORT_DIRS,
    MESSAGE_RE,
    MEDIA_RE,
    LOCATION_RE,
    CONTACT_RE,
    DELETED_RE,
    CHAT_HEADER_RE,
    CHAT_JID_RE,
    CHAT_MSG_COUNT_RE,
    CHAT_EXPORT_DATE_RE,
    get_export_chat_folders,
    ensure_directories,
)


def parse_datetime(date_str: str, time_str: str) -> str:
    """Преобразовать DD.MM.YYYY и HH:MM:SS в ISO формат."""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")
        return dt.isoformat()
    except ValueError:
        return f"{date_str}T{time_str}"


def parse_chat_header(content: str) -> dict:
    """Извлечь метаданные из заголовка чата."""
    metadata = {
        "chat_name": None,
        "jid": None,
        "message_count": 0,
        "export_date": None,
    }

    match = CHAT_HEADER_RE.search(content)
    if match:
        metadata["chat_name"] = match.group(1).strip()

    match = CHAT_JID_RE.search(content)
    if match:
        metadata["jid"] = match.group(1).strip()

    match = CHAT_MSG_COUNT_RE.search(content)
    if match:
        metadata["message_count"] = int(match.group(1))

    match = CHAT_EXPORT_DATE_RE.search(content)
    if match:
        try:
            dt = datetime.strptime(match.group(1), "%d.%m.%Y %H:%M:%S")
            metadata["export_date"] = dt.isoformat()
        except ValueError:
            metadata["export_date"] = match.group(1)

    return metadata


def parse_chat_file(chat_file: Path, source: str, chat_folder: Path) -> tuple[list[dict], dict]:
    """
    Парсить один файл chat.txt.

    Returns:
        tuple: (список сообщений, метаданные чата)
    """
    messages = []

    try:
        content = chat_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Попробуем с другой кодировкой
        try:
            content = chat_file.read_text(encoding="utf-8-sig")
        except Exception as e:
            print(f"[ОШИБКА] Не удалось прочитать {chat_file}: {e}")
            return [], {"error": str(e)}

    # Извлечь метаданные чата
    metadata = parse_chat_header(content)
    metadata["source"] = source
    metadata["chat_folder"] = chat_folder.name
    metadata["file_path"] = str(chat_file)

    # Текущее сообщение
    current_msg = None
    text_lines = []
    media_items = []
    location = None
    contact = None

    def save_current_message():
        """Сохранить текущее сообщение в список."""
        nonlocal current_msg, text_lines, media_items, location, contact

        if current_msg:
            # Собрать текст сообщения
            text = "\n".join(text_lines).strip()

            msg = {
                "jid": metadata.get("jid"),
                "chat_name": metadata.get("chat_name"),
                "source": source,
                "chat_folder": chat_folder.name,
                "datetime": current_msg["datetime"],
                "sender": current_msg["sender"],
                "is_from_me": current_msg["sender"] == "Я",
                "text": text if text else None,
                "media": media_items if media_items else None,
                "location": location,
                "contact": contact,
            }
            messages.append(msg)

        # Сброс
        current_msg = None
        text_lines = []
        media_items = []
        location = None
        contact = None

    # Парсинг строк
    lines = content.split("\n")
    in_header = True

    for line in lines:
        # Пропустить заголовок (до пустой строки после разделителя)
        if in_header:
            if line.startswith("=") or line.startswith("ЧАТ:") or line.startswith("JID:") or \
               line.startswith("Сообщений:") or line.startswith("Экспорт:"):
                continue
            if line.strip() == "":
                in_header = False
                continue
            continue

        # Новое сообщение?
        msg_match = MESSAGE_RE.match(line)
        if msg_match:
            save_current_message()

            date_str = msg_match.group(1)
            time_str = msg_match.group(2)
            sender = msg_match.group(3)

            current_msg = {
                "datetime": parse_datetime(date_str, time_str),
                "sender": sender,
            }
            continue

        # Медиа?
        media_match = MEDIA_RE.match(line)
        if media_match and current_msg:
            media_type = media_match.group(1)
            media_path = media_match.group(2)
            media_items.append({
                "type": media_type,
                "path": f"media/{media_path}",
            })
            continue

        # Локация?
        loc_match = LOCATION_RE.match(line)
        if loc_match and current_msg:
            location = {
                "lat": loc_match.group(1),
                "lon": loc_match.group(2),
            }
            continue

        # Контакт?
        contact_match = CONTACT_RE.match(line)
        if contact_match and current_msg:
            contact = contact_match.group(1)
            continue

        # Удалённое медиа?
        if DELETED_RE.match(line):
            continue

        # Обычный текст сообщения
        if current_msg and line.startswith("  "):
            text_lines.append(line[2:])  # Убрать 2 пробела отступа
        elif current_msg and line.strip():
            # Строка без отступа, но есть текущее сообщение - добавить как текст
            text_lines.append(line.strip())

    # Сохранить последнее сообщение
    save_current_message()

    return messages, metadata


def main():
    """Основная функция."""
    print("=" * 60)
    print("ПАРСИНГ ВСЕХ WHATSAPP ЧАТОВ В JSONL")
    print("=" * 60)

    # Создать директории
    ensure_directories()

    # Получить список всех чатов
    print("\nСканирование папок...")
    chat_folders = get_export_chat_folders()
    total_chats = len(chat_folders)
    print(f"Найдено чатов: {total_chats}")

    if total_chats == 0:
        print("[ОШИБКА] Чаты не найдены!")
        print(f"Проверьте папки:")
        for d in EXPORT_DIRS:
            print(f"  - {d}")
        sys.exit(1)

    # Статистика по источникам
    wa_count = sum(1 for c in chat_folders if c["source"] == "whatsapp")
    wa_biz_count = sum(1 for c in chat_folders if c["source"] == "wa_business")
    print(f"  - WhatsApp: {wa_count}")
    print(f"  - WA Business: {wa_biz_count}")

    # Выходные файлы
    output_file = RAW_DIR / "all_messages.jsonl"
    metadata_file = RAW_DIR / "chat_metadata.json"

    print(f"\nВыходной файл: {output_file}")
    print(f"Метаданные: {metadata_file}")
    print("\nНачинаю парсинг...\n")

    # Счётчики
    total_messages = 0
    processed_chats = 0
    failed_chats = 0
    all_metadata = []

    start_time = datetime.now()

    # Открыть файл для записи
    with open(output_file, "w", encoding="utf-8") as f:
        for chat_info in chat_folders:
            chat_file = chat_info["chat_file"]
            source = chat_info["source"]
            chat_folder = chat_info["folder"]

            try:
                messages, metadata = parse_chat_file(chat_file, source, chat_folder)

                # Записать сообщения
                for msg in messages:
                    f.write(json.dumps(msg, ensure_ascii=False) + "\n")

                total_messages += len(messages)
                processed_chats += 1

                # Сохранить метаданные
                metadata["parsed_messages"] = len(messages)
                all_metadata.append(metadata)

                # Прогресс каждые 100 чатов
                if processed_chats % 100 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    speed = total_messages / elapsed if elapsed > 0 else 0
                    print(f"[{processed_chats:4d}/{total_chats}] "
                          f"Сообщений: {total_messages:,} | "
                          f"Скорость: {speed:,.0f} msg/sec")

                # Дополнительный прогресс каждые 100,000 сообщений
                if total_messages > 0 and total_messages % 100000 < len(messages):
                    print(f"  >>> Достигнуто {total_messages:,} сообщений!")

            except Exception as e:
                failed_chats += 1
                print(f"[ОШИБКА] {chat_folder.name}: {e}")
                all_metadata.append({
                    "chat_folder": chat_folder.name,
                    "source": source,
                    "error": str(e),
                })

    # Сохранить метаданные
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_chats": total_chats,
            "processed_chats": processed_chats,
            "failed_chats": failed_chats,
            "total_messages": total_messages,
            "sources": {
                "whatsapp": wa_count,
                "wa_business": wa_biz_count,
            },
            "chats": all_metadata,
        }, f, ensure_ascii=False, indent=2)

    # Итоги
    elapsed = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"Обработано чатов: {processed_chats}/{total_chats}")
    print(f"Ошибок: {failed_chats}")
    print(f"Всего сообщений: {total_messages:,}")
    print(f"Время: {elapsed:.1f} сек")
    print(f"Скорость: {total_messages/elapsed:,.0f} msg/sec" if elapsed > 0 else "")
    print(f"\nФайлы:")
    print(f"  - {output_file}")
    print(f"  - {metadata_file}")
    print(f"\nРазмер: {output_file.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
