#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоклассификация контактов на основе анализа сообщений.

Входные файлы:
- D:/Downloads/Chats/_база/json/contacts.json
- D:/Downloads/Chats/_база/raw/all_messages.jsonl

Выходной файл:
- Обновляет contacts.json, заполняя поля type и subtype

Алгоритм:
1. Загрузить контакты из contacts.json
2. Для каждого контакта собрать все его сообщения из JSONL
3. Подсчитать частоту ключевых слов по категориям
4. Категория с максимальным весом -> type
5. Подтип определить по подкатегориям
6. Если нет совпадений -> type="клиенты", subtype="турист"
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import (
        JSON_DIR, RAW_DIR, CLASSIFICATION_RULES,
        CONTACT_TYPES, CONTACT_SUBTYPES
    )
except ImportError:
    # Fallback если config.py не найден
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")

    CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]

    CONTACT_SUBTYPES = {
        "клиенты": ["турист", "VIP", "корпоративный"],
        "агенты": ["турагент", "туроператор", "B2B"],
        "поставщики": ["обменник", "водитель", "гид", "яхтсмен", "кейтеринг"],
        "сотрудники": ["менеджер", "водитель_штат", "админ"]
    }

    CLASSIFICATION_RULES = {
        "агенты": {
            "keywords": [
                "турагент", "турагентство", "агентство", "туроператор",
                "партнёр", "комиссия", "%", "нетто", "брутто",
                "travel", "tour", "agency"
            ],
            "jid_patterns": [r".*@g\.us$"],
            "name_patterns": [r".*tour.*", r".*travel.*", r".*agency.*"],
            "subtypes": {
                "турагент": ["турагент", "agency", "travel"],
                "туроператор": ["туроператор", "operator"],
                "B2B": ["B2B", "партнёр", "wholesale"]
            }
        },
        "поставщики": {
            "keywords": [
                "обменник", "курс", "валюта", "exchange",
                "водитель", "driver", "трансфер",
                "гид", "guide", "экскурсовод",
                "яхта", "yacht", "капитан",
                "кейтеринг", "catering"
            ],
            "subtypes": {
                "обменник": ["обмен", "курс", "exchange", "валюта"],
                "водитель": ["водитель", "driver", "трансфер"],
                "гид": ["гид", "guide", "экскурсовод"],
                "яхтсмен": ["яхта", "yacht", "капитан"],
                "кейтеринг": ["кейтеринг", "catering", "еда"]
            }
        },
        "сотрудники": {
            "keywords": [
                "офис", "зарплата", "отпуск", "рабочий",
                "смена", "график", "meeting"
            ],
            "phone_prefixes": ["971507705321"],
            "subtypes": {
                "менеджер": ["менеджер", "manager"],
                "водитель_штат": ["водитель", "наш"],
                "админ": ["админ", "бухгалтер", "HR"]
            }
        },
        "клиенты": {
            "default": True,
            "keywords": [
                "бронирование", "экскурсия", "тур", "билет",
                "хочу", "сколько стоит", "цена"
            ],
            "subtypes": {
                "турист": ["экскурсия", "тур", "отель"],
                "VIP": ["VIP", "люкс", "premium", "private"],
                "корпоративный": ["компания", "корпоратив", "team building"]
            }
        }
    }


def load_contacts(contacts_path: Path) -> list:
    """Загрузить контакты из JSON файла."""
    if not contacts_path.exists():
        print(f"ОШИБКА: Файл контактов не найден: {contacts_path}")
        return []

    try:
        with open(contacts_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Поддержка разных форматов JSON
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'contacts' in data:
            return data['contacts']
        else:
            print(f"ВНИМАНИЕ: Неожиданный формат JSON в {contacts_path}")
            return []
    except json.JSONDecodeError as e:
        print(f"ОШИБКА: Невозможно разобрать JSON: {e}")
        return []


def load_messages_for_contact(messages_path: Path, jid: str) -> list:
    """Загрузить все сообщения для конкретного контакта из JSONL файла."""
    messages = []

    if not messages_path.exists():
        return messages

    try:
        with open(messages_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    # Проверяем соответствие JID
                    msg_jid = msg.get('jid', '') or msg.get('chat_jid', '') or msg.get('contact_jid', '')
                    if msg_jid == jid:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"ОШИБКА при чтении сообщений: {e}")

    return messages


def load_all_messages_grouped(messages_path: Path) -> dict:
    """Загрузить все сообщения и сгруппировать по JID."""
    messages_by_jid = defaultdict(list)

    if not messages_path.exists():
        print(f"ВНИМАНИЕ: Файл сообщений не найден: {messages_path}")
        return messages_by_jid

    try:
        with open(messages_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    # Поддержка разных ключей для JID
                    jid = (msg.get('jid') or
                           msg.get('chat_jid') or
                           msg.get('contact_jid') or
                           msg.get('remote_jid', ''))
                    if jid:
                        messages_by_jid[jid].append(msg)
                except json.JSONDecodeError as e:
                    if line_num <= 5:  # Показываем только первые ошибки
                        print(f"  Строка {line_num}: ошибка парсинга JSON")
                    continue
    except Exception as e:
        print(f"ОШИБКА при чтении {messages_path}: {e}")

    return messages_by_jid


def extract_text_from_messages(messages: list) -> str:
    """Извлечь весь текст из списка сообщений."""
    texts = []

    for msg in messages:
        # Поддержка разных форматов сообщений
        text = (msg.get('text') or
                msg.get('body') or
                msg.get('message') or
                msg.get('content', ''))
        if text:
            texts.append(text.lower())

    return ' '.join(texts)


def count_keyword_matches(text: str, keywords: list) -> int:
    """Подсчитать количество совпадений ключевых слов в тексте."""
    count = 0
    text_lower = text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Используем word boundary для более точного поиска
        # но для коротких слов типа "%" просто ищем вхождение
        if len(keyword) <= 2:
            count += text_lower.count(keyword_lower)
        else:
            # Регулярное выражение для поиска слова
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            count += len(re.findall(pattern, text_lower))

    return count


def check_jid_patterns(jid: str, patterns: list) -> bool:
    """Проверить соответствие JID паттернам."""
    for pattern in patterns:
        if re.match(pattern, jid, re.IGNORECASE):
            return True
    return False


def check_name_patterns(name: str, patterns: list) -> bool:
    """Проверить соответствие имени паттернам."""
    name_lower = name.lower()
    for pattern in patterns:
        if re.match(pattern, name_lower, re.IGNORECASE):
            return True
    return False


def check_phone_prefixes(jid: str, phone: str, prefixes: list) -> bool:
    """Проверить соответствие телефона известным префиксам."""
    # Извлекаем номер из JID
    phone_from_jid = re.sub(r'@.*$', '', jid)

    for prefix in prefixes:
        if phone_from_jid.startswith(prefix) or phone.startswith(prefix):
            return True
    return False


def determine_subtype(text: str, subtypes: dict, contact_type: str) -> str:
    """Определить подтип контакта на основе ключевых слов."""
    max_count = 0
    best_subtype = None

    for subtype, keywords in subtypes.items():
        count = count_keyword_matches(text, keywords)
        if count > max_count:
            max_count = count
            best_subtype = subtype

    # Если не нашли подходящий подтип, используем первый по умолчанию
    if best_subtype is None:
        default_subtypes = CONTACT_SUBTYPES.get(contact_type, [])
        if default_subtypes:
            best_subtype = default_subtypes[0]

    return best_subtype


def classify_contact(contact: dict, messages_text: str) -> tuple:
    """
    Классифицировать контакт на основе его сообщений.

    Возвращает: (type, subtype, confidence_scores)
    """
    jid = contact.get('jid', '')
    name = contact.get('name', '') or contact.get('display_name', '')
    phone = contact.get('phone', '') or contact.get('number', '')

    scores = {}

    # Подсчитываем очки для каждой категории
    for category, rules in CLASSIFICATION_RULES.items():
        score = 0

        # Проверка ключевых слов
        keywords = rules.get('keywords', [])
        keyword_score = count_keyword_matches(messages_text, keywords)
        score += keyword_score

        # Бонус за паттерны JID (группы часто агентские)
        jid_patterns = rules.get('jid_patterns', [])
        if jid_patterns and check_jid_patterns(jid, jid_patterns):
            score += 5  # Повышенный вес для групп

        # Бонус за паттерны имени
        name_patterns = rules.get('name_patterns', [])
        if name_patterns and check_name_patterns(name, name_patterns):
            score += 3

        # Автоматическое присвоение для известных номеров
        phone_prefixes = rules.get('phone_prefixes', [])
        if phone_prefixes and check_phone_prefixes(jid, phone, phone_prefixes):
            score += 100  # Гарантированное присвоение

        scores[category] = score

    # Находим категорию с максимальным весом
    max_score = 0
    best_type = "клиенты"  # По умолчанию

    for category, score in scores.items():
        if score > max_score:
            max_score = score
            best_type = category

    # Если все очки = 0, используем default категорию (клиенты)
    if max_score == 0:
        best_type = "клиенты"

    # Определяем подтип
    subtypes = CLASSIFICATION_RULES.get(best_type, {}).get('subtypes', {})
    best_subtype = determine_subtype(messages_text, subtypes, best_type)

    # Если подтип не определён, используем "турист" для клиентов
    if best_subtype is None:
        if best_type == "клиенты":
            best_subtype = "турист"
        else:
            best_subtype = CONTACT_SUBTYPES.get(best_type, [""])[0]

    return best_type, best_subtype, scores


def save_contacts(contacts: list, contacts_path: Path):
    """Сохранить обновлённые контакты в JSON файл."""
    # Создаём директорию, если не существует
    contacts_path.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем с красивым форматированием
    with open(contacts_path, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

    print(f"\nКонтакты сохранены в: {contacts_path}")


def print_statistics(stats: dict):
    """Вывести статистику классификации."""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА КЛАССИФИКАЦИИ")
    print("=" * 60)

    total = stats['total']
    classified = stats['classified']

    print(f"\nВсего контактов: {total}")
    print(f"Классифицировано: {classified}")

    print("\nРаспределение по типам:")
    print("-" * 40)

    for contact_type in CONTACT_TYPES:
        count = stats['by_type'].get(contact_type, 0)
        percent = (count / total * 100) if total > 0 else 0
        print(f"  {contact_type:15} : {count:4} ({percent:5.1f}%)")

    print("\nРаспределение по подтипам:")
    print("-" * 40)

    for contact_type in CONTACT_TYPES:
        subtypes = stats['by_subtype'].get(contact_type, {})
        if subtypes:
            print(f"\n  {contact_type}:")
            for subtype, count in sorted(subtypes.items(), key=lambda x: -x[1]):
                print(f"    - {subtype:15} : {count}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Автоклассификация контактов на основе анализа сообщений"
    )
    parser.add_argument(
        "--contacts",
        default=str(JSON_DIR / "contacts.json"),
        help="Путь к файлу contacts.json"
    )
    parser.add_argument(
        "--messages",
        default=str(RAW_DIR / "all_messages.jsonl"),
        help="Путь к файлу all_messages.jsonl"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать результаты, не сохранять"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )

    args = parser.parse_args()

    contacts_path = Path(args.contacts)
    messages_path = Path(args.messages)

    print("=" * 60)
    print("АВТОКЛАССИФИКАЦИЯ КОНТАКТОВ")
    print("=" * 60)
    print(f"\nФайл контактов: {contacts_path}")
    print(f"Файл сообщений: {messages_path}")
    print(f"Режим: {'тестовый (без сохранения)' if args.dry_run else 'рабочий'}")
    print()

    # Загрузка контактов
    print("Загрузка контактов...")
    contacts = load_contacts(contacts_path)

    if not contacts:
        print("ОШИБКА: Контакты не загружены. Проверьте файл.")
        sys.exit(1)

    print(f"Загружено контактов: {len(contacts)}")

    # Загрузка всех сообщений
    print("\nЗагрузка сообщений...")
    messages_by_jid = load_all_messages_grouped(messages_path)

    total_messages = sum(len(msgs) for msgs in messages_by_jid.values())
    print(f"Загружено сообщений: {total_messages}")
    print(f"Уникальных JID: {len(messages_by_jid)}")

    # Статистика
    stats = {
        'total': len(contacts),
        'classified': 0,
        'by_type': defaultdict(int),
        'by_subtype': defaultdict(lambda: defaultdict(int))
    }

    # Классификация каждого контакта
    print("\nКлассификация контактов...")

    for i, contact in enumerate(contacts):
        jid = contact.get('jid', '')
        name = contact.get('name', '') or contact.get('display_name', '') or jid

        # Получаем сообщения для этого контакта
        messages = messages_by_jid.get(jid, [])
        messages_text = extract_text_from_messages(messages)

        # Классифицируем
        contact_type, subtype, scores = classify_contact(contact, messages_text)

        # Обновляем контакт
        contact['type'] = contact_type
        contact['subtype'] = subtype
        contact['classification_scores'] = scores
        contact['messages_count'] = len(messages)
        contact['classified_at'] = datetime.now().isoformat()

        # Статистика
        stats['classified'] += 1
        stats['by_type'][contact_type] += 1
        stats['by_subtype'][contact_type][subtype] += 1

        # Вывод прогресса
        if args.verbose or (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(contacts)}] {name[:30]:30} -> {contact_type}/{subtype} "
                  f"(сообщений: {len(messages)}, очки: {max(scores.values()) if scores else 0})")

    # Вывод статистики
    print_statistics(stats)

    # Сохранение результатов
    if not args.dry_run:
        save_contacts(contacts, contacts_path)
        print("\nКлассификация завершена успешно!")
    else:
        print("\nТестовый режим: результаты НЕ сохранены.")
        print("Для сохранения запустите без флага --dry-run")


if __name__ == "__main__":
    main()
