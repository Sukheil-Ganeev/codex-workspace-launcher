#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обнаружение рефералов в чатах WhatsApp.

Источники рефералов:
1. VCF контакты - когда один контакт отправляет карточку другого
2. Упоминания - "от Марины", "Марина порекомендовала", "по рекомендации"
3. Прямые указания - "моя знакомая", "мой друг", "коллега"

Выходной формат: JSON со списком рефералов и метаданными.
"""

import sys
import os
import re
import json
import uuid
import argparse
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

# === ПАТТЕРНЫ ДЛЯ ПОИСКА РЕФЕРАЛОВ ===

# Паттерны упоминаний с именем
MENTION_PATTERNS = [
    # "по рекомендации [имя]"
    r'по\s+рекомендации\s+(?:от\s+)?([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "от [имя]" в начале или после точки/запятой
    r'(?:^|[,.\s])от\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "[имя] посоветовал/а/и"
    r'([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)\s+(?:посоветовал[аи]?|порекомендовал[аи]?|рекомендовал[аи]?)',

    # "знакомый/знакомая [имя]"
    r'(?:знакомый|знакомая|знакомые)\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "коллега [имя]"
    r'коллега\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "друг/подруга [имя]"
    r'(?:друг|подруга|друзья)\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "[имя] дал/а ваш номер/контакт"
    r'([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)\s+(?:дал[аи]?\s+(?:ваш|твой)\s+(?:номер|контакт|телефон))',

    # "нашел/нашла вас через [имя]"
    r'(?:нашел|нашла|нашли|узнал[аи]?)\s+(?:вас|о вас|про вас)\s+(?:через|от|у)\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "меня направил/а [имя]"
    r'меня\s+(?:направил[аи]?|послал[аи]?|отправил[аи]?)\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',

    # "ваш контакт от [имя]"
    r'(?:ваш|твой)\s+(?:контакт|номер)\s+(?:от|дал[аи]?)\s+([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\s]{1,30}?)(?:\s*[,.\n!?]|$)',
]

# Паттерны прямых указаний без конкретного имени
DIRECT_PATTERNS = [
    r'(моя?\s+знакомая?\s+(?:рекомендовал[аи]?|посоветовал[аи]?|дал[аи]?\s+контакт))',
    r'(мой\s+(?:друг|коллега|партнер)\s+(?:рекомендовал|посоветовал|дал\s+контакт))',
    r'(моя\s+(?:подруга|коллега|партнер)\s+(?:рекомендовала|посоветовала|дала\s+контакт))',
    r'(по\s+рекомендации\s+(?:друзей|знакомых|коллег))',
    r'(знакомые\s+(?:рекомендовали|посоветовали|дали\s+контакт))',
    r'(друзья\s+(?:рекомендовали|посоветовали|дали\s+контакт))',
]

# Стоп-слова для фильтрации ложных срабатываний
STOP_WORDS = {
    'вас', 'вам', 'вами', 'них', 'нас', 'нам', 'меня', 'мне', 'тебя', 'тебе',
    'здравствуйте', 'привет', 'добрый', 'день', 'вечер', 'утро',
    'спасибо', 'пожалуйста', 'хорошо', 'отлично', 'да', 'нет',
    'можно', 'нужно', 'надо', 'когда', 'куда', 'откуда', 'где',
}


def load_contacts(contacts_path):
    """Загружает контакты из JSON файла."""
    if not os.path.exists(contacts_path):
        print(f"Файл контактов не найден: {contacts_path}")
        return {}

    try:
        with open(contacts_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Создаем индекс по именам для быстрого поиска
        contacts_index = {}
        contacts_list = data if isinstance(data, list) else data.get('contacts', [])

        for contact in contacts_list:
            contact_id = contact.get('id') or contact.get('contact_id') or str(uuid.uuid4())
            name = contact.get('name') or contact.get('display_name', '')

            if name:
                # Индексируем по полному имени
                contacts_index[name.lower()] = {
                    'id': contact_id,
                    'name': name,
                    'contact': contact
                }

                # Индексируем по частям имени
                name_parts = name.split()
                for part in name_parts:
                    if len(part) > 2:
                        key = part.lower()
                        if key not in contacts_index:
                            contacts_index[key] = {
                                'id': contact_id,
                                'name': name,
                                'contact': contact
                            }

        print(f"Загружено {len(contacts_list)} контактов, {len(contacts_index)} записей в индексе")
        return contacts_index

    except Exception as e:
        print(f"Ошибка загрузки контактов: {e}")
        return {}


def load_messages(messages_path):
    """Загружает сообщения из JSONL файла."""
    if not os.path.exists(messages_path):
        print(f"Файл сообщений не найден: {messages_path}")
        return []

    messages = []
    try:
        with open(messages_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue

        print(f"Загружено {len(messages)} сообщений")
        return messages

    except Exception as e:
        print(f"Ошибка загрузки сообщений: {e}")
        return []


def fuzzy_match(name, contacts_index, threshold=0.7):
    """
    Fuzzy поиск имени в индексе контактов.
    Возвращает (contact_id, contact_name, confidence) или None.
    """
    name_lower = name.lower().strip()

    # Фильтруем стоп-слова
    if name_lower in STOP_WORDS or len(name_lower) < 3:
        return None

    # Точное совпадение
    if name_lower in contacts_index:
        return (
            contacts_index[name_lower]['id'],
            contacts_index[name_lower]['name'],
            1.0
        )

    # Fuzzy поиск
    best_match = None
    best_score = 0

    for key, data in contacts_index.items():
        # SequenceMatcher для fuzzy matching
        score = SequenceMatcher(None, name_lower, key).ratio()

        # Также проверяем начало имени
        if key.startswith(name_lower) or name_lower.startswith(key):
            score = max(score, 0.85)

        if score > best_score and score >= threshold:
            best_score = score
            best_match = (data['id'], data['name'], score)

    return best_match


def extract_vcf_referrals(messages, contacts_index):
    """
    Извлекает рефералы из VCF контактов.
    Когда один контакт отправляет карточку другого.
    """
    referrals = []

    for msg in messages:
        # Проверяем наличие VCF
        has_vcf = (
            msg.get('has_vcf') or
            msg.get('media_type') == 'vcf' or
            msg.get('attachment_type') == 'vcf' or
            'BEGIN:VCARD' in msg.get('content', '') or
            'BEGIN:VCARD' in msg.get('text', '')
        )

        if not has_vcf:
            continue

        # Извлекаем данные из VCF
        content = msg.get('content', '') or msg.get('text', '')
        vcf_name = None
        vcf_phone = None

        # Парсим имя из VCF
        fn_match = re.search(r'FN[;:]([^\n]+)', content)
        if fn_match:
            vcf_name = fn_match.group(1).strip()

        # Парсим телефон из VCF
        tel_match = re.search(r'TEL[^:]*:([^\n]+)', content)
        if tel_match:
            vcf_phone = tel_match.group(1).strip()

        if not vcf_name:
            continue

        # Определяем отправителя (referrer)
        sender_id = msg.get('sender_id') or msg.get('contact_id') or msg.get('from_id')
        sender_name = msg.get('sender_name') or msg.get('contact_name') or msg.get('from_name', '')

        # Ищем переданный контакт в базе
        referred_match = fuzzy_match(vcf_name, contacts_index, threshold=0.6)

        referral = {
            'referral_id': str(uuid.uuid4()),
            'referrer_contact_id': sender_id or '',
            'referrer_name': sender_name,
            'referred_contact_id': referred_match[0] if referred_match else '',
            'referred_name': vcf_name,
            'referred_phone': vcf_phone,
            'source': 'vcf',
            'detected_date': msg.get('date', msg.get('timestamp', '')),
            'confidence': referred_match[2] if referred_match else 0.5,
            'context': f"VCF карточка: {vcf_name}" + (f" ({vcf_phone})" if vcf_phone else ''),
            'total_operations': 0,
            'total_revenue_aed': 0,
            'message_id': msg.get('id', msg.get('message_id', ''))
        }

        referrals.append(referral)

    return referrals


def extract_mention_referrals(messages, contacts_index):
    """
    Извлекает рефералы из упоминаний в тексте.
    "от Марины", "Марина порекомендовала", и т.д.
    """
    referrals = []

    for msg in messages:
        content = msg.get('content', '') or msg.get('text', '')
        if not content or len(content) < 10:
            continue

        # Определяем автора сообщения (это referred, т.к. он упоминает referrer)
        referred_id = msg.get('sender_id') or msg.get('contact_id') or msg.get('from_id')
        referred_name = msg.get('sender_name') or msg.get('contact_name') or msg.get('from_name', '')

        # Ищем упоминания
        for pattern in MENTION_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                mentioned_name = match.strip() if isinstance(match, str) else match[0].strip()

                # Фильтруем мусор
                if len(mentioned_name) < 3 or mentioned_name.lower() in STOP_WORDS:
                    continue

                # Убираем лишние символы
                mentioned_name = re.sub(r'[,.\n!?]+$', '', mentioned_name).strip()

                if len(mentioned_name) < 2:
                    continue

                # Ищем упомянутого в базе контактов (это referrer)
                referrer_match = fuzzy_match(mentioned_name, contacts_index, threshold=0.6)

                referral = {
                    'referral_id': str(uuid.uuid4()),
                    'referrer_contact_id': referrer_match[0] if referrer_match else '',
                    'referrer_name': referrer_match[1] if referrer_match else mentioned_name,
                    'referred_contact_id': referred_id or '',
                    'referred_name': referred_name,
                    'source': 'mention',
                    'detected_date': msg.get('date', msg.get('timestamp', '')),
                    'confidence': referrer_match[2] if referrer_match else 0.4,
                    'context': content[:200] + ('...' if len(content) > 200 else ''),
                    'total_operations': 0,
                    'total_revenue_aed': 0,
                    'message_id': msg.get('id', msg.get('message_id', ''))
                }

                referrals.append(referral)

    return referrals


def extract_direct_referrals(messages, contacts_index):
    """
    Извлекает рефералы из прямых указаний без конкретного имени.
    "моя знакомая", "мой друг порекомендовал", и т.д.
    """
    referrals = []

    for msg in messages:
        content = msg.get('content', '') or msg.get('text', '')
        if not content or len(content) < 10:
            continue

        # Определяем автора сообщения (это referred)
        referred_id = msg.get('sender_id') or msg.get('contact_id') or msg.get('from_id')
        referred_name = msg.get('sender_name') or msg.get('contact_name') or msg.get('from_name', '')

        # Ищем прямые указания
        for pattern in DIRECT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                context_text = match if isinstance(match, str) else match[0]

                referral = {
                    'referral_id': str(uuid.uuid4()),
                    'referrer_contact_id': '',  # Неизвестен
                    'referrer_name': 'Неизвестно (упоминание без имени)',
                    'referred_contact_id': referred_id or '',
                    'referred_name': referred_name,
                    'source': 'direct',
                    'detected_date': msg.get('date', msg.get('timestamp', '')),
                    'confidence': 0.6,
                    'context': content[:200] + ('...' if len(content) > 200 else ''),
                    'total_operations': 0,
                    'total_revenue_aed': 0,
                    'message_id': msg.get('id', msg.get('message_id', ''))
                }

                referrals.append(referral)

    return referrals


def deduplicate_referrals(referrals):
    """Удаляет дубликаты рефералов."""
    seen = set()
    unique = []

    for ref in referrals:
        # Ключ уникальности: referrer + referred + source
        key = (
            ref.get('referrer_contact_id', '') or ref.get('referrer_name', ''),
            ref.get('referred_contact_id', '') or ref.get('referred_name', ''),
            ref.get('source', '')
        )

        if key not in seen:
            seen.add(key)
            unique.append(ref)

    return unique


def detect_referrals(contacts_path, messages_path, output_path):
    """
    Основная функция обнаружения рефералов.
    """
    print("=" * 60)
    print("Обнаружение рефералов")
    print("=" * 60)
    print()

    # Загрузка данных
    contacts_index = load_contacts(contacts_path)
    messages = load_messages(messages_path)

    if not messages:
        print("Нет сообщений для анализа")
        return

    # Извлечение рефералов из разных источников
    print("\nПоиск VCF контактов...")
    vcf_referrals = extract_vcf_referrals(messages, contacts_index)
    print(f"  Найдено: {len(vcf_referrals)}")

    print("\nПоиск упоминаний...")
    mention_referrals = extract_mention_referrals(messages, contacts_index)
    print(f"  Найдено: {len(mention_referrals)}")

    print("\nПоиск прямых указаний...")
    direct_referrals = extract_direct_referrals(messages, contacts_index)
    print(f"  Найдено: {len(direct_referrals)}")

    # Объединение и дедупликация
    all_referrals = vcf_referrals + mention_referrals + direct_referrals
    unique_referrals = deduplicate_referrals(all_referrals)

    # Сортировка по confidence
    unique_referrals.sort(key=lambda x: x.get('confidence', 0), reverse=True)

    # Формирование результата
    result = {
        'referrals': unique_referrals,
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_messages_analyzed': len(messages),
            'total_contacts': len(contacts_index),
            'stats': {
                'vcf': len(vcf_referrals),
                'mention': len(mention_referrals),
                'direct': len(direct_referrals),
                'total_unique': len(unique_referrals)
            }
        }
    }

    # Сохранение результата
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Статистика
    print("\n" + "=" * 60)
    print("Результаты")
    print("=" * 60)
    print(f"Всего уникальных рефералов: {len(unique_referrals)}")
    print(f"  - VCF контакты: {len(vcf_referrals)}")
    print(f"  - Упоминания: {len(mention_referrals)}")
    print(f"  - Прямые указания: {len(direct_referrals)}")
    print()

    # Топ рефереров
    referrer_counts = defaultdict(int)
    for ref in unique_referrals:
        referrer = ref.get('referrer_name', 'Неизвестно')
        if referrer and referrer != 'Неизвестно (упоминание без имени)':
            referrer_counts[referrer] += 1

    if referrer_counts:
        print("Топ рефереров:")
        for referrer, count in sorted(referrer_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {referrer}: {count} рефералов")

    print()
    print(f"Результат сохранен: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Обнаружение рефералов в WhatsApp чатах"
    )
    parser.add_argument(
        "--contacts",
        default="D:/Downloads/Chats/_база/json/contacts.json",
        help="Путь к файлу контактов"
    )
    parser.add_argument(
        "--messages",
        default="D:/Downloads/Chats/_база/raw/all_messages.jsonl",
        help="Путь к файлу сообщений"
    )
    parser.add_argument(
        "-o", "--output",
        default="D:/Downloads/Chats/_база/json/referrals.json",
        help="Путь для сохранения результата"
    )

    args = parser.parse_args()

    detect_referrals(
        contacts_path=args.contacts,
        messages_path=args.messages,
        output_path=args.output
    )
