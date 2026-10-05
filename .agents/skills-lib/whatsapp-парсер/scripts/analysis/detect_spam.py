#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детекция спама в WhatsApp чатах.

Функции:
1. Детекция повторяющихся сообщений
2. Детекция массовых рассылок
3. Признаки спама (ссылки, призывы, капс, шаблоны)
4. Детекция ботов
5. Whitelist/Blacklist
6. Spam score (0-100)
7. Автоматическая маркировка
8. Статистика спама
9. Экспорт JSON с метками
"""

import sys
import os
import re
import json
import hashlib
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Set

sys.stdout.reconfigure(encoding='utf-8')

# === КОНФИГУРАЦИЯ ===

# Веса для расчета spam score
WEIGHTS = {
    'duplicate': 25,           # Повторяющееся сообщение
    'mass_broadcast': 30,      # Массовая рассылка
    'many_links': 15,          # Много ссылок
    'call_to_action': 10,      # Призывы к действию
    'caps_abuse': 8,           # Злоупотребление капсом
    'exclamation_abuse': 5,    # Много восклицаний
    'template_phrase': 12,     # Шаблонные фразы
    'bot_pattern': 20,         # Паттерны бота
    'blacklist_sender': 50,    # Отправитель в черном списке
    'suspicious_phone': 10,    # Подозрительный номер
}

# === ПАТТЕРНЫ ДЛЯ ДЕТЕКЦИИ ===

# URL паттерны
URL_PATTERNS = [
    r'https?://[^\s<>"{}|\\^`\[\]]+',
    r'www\.[^\s<>"{}|\\^`\[\]]+',
    r't\.me/[^\s]+',
    r'wa\.me/[^\s]+',
    r'bit\.ly/[^\s]+',
    r'goo\.gl/[^\s]+',
    r'tinyurl\.com/[^\s]+',
]

# Призывы к действию
CALL_TO_ACTION_PATTERNS = [
    r'\b(купи|покупай|закажи|заказывай|оформи|оформляй)\b',
    r'\b(подпишись|подписывайся|вступай|присоединяйся)\b',
    r'\b(жми|нажми|кликай|переходи|перейди)\b',
    r'\b(зарегистрируйся|регистрируйся|авторизуйся)\b',
    r'\b(скачай|скачивай|установи|устанавливай)\b',
    r'\b(голосуй|проголосуй|поддержи|лайкни)\b',
    r'\b(репост|перешли|отправь|поделись)\b',
    r'\b(успей|торопись|не пропусти|не упусти)\b',
    r'\b(бесплатно|даром|без оплаты|в подарок)\b',
    r'\b(акция|скидка|распродажа|sale)\b',
    r'\b(limited|exclusive|hurry|buy now|order now)\b',
]

# Шаблонные спам-фразы
TEMPLATE_PHRASES = [
    r'заработок\s+(?:в\s+)?(?:интернете?|сети|онлайн)',
    r'пассивный\s+доход',
    r'финансовая\s+(?:свобода|независимость)',
    r'без\s+(?:вложений|опыта|риска)',
    r'работа\s+на\s+дому',
    r'удаленная\s+работа',
    r'легкие?\s+деньги',
    r'быстрый\s+заработок',
    r'гарантированный\s+доход',
    r'инвестиц\w+\s+(?:проект|платформа|возможность)',
    r'крипто(?:валют|биржа|инвест)',
    r'бинарн\w+\s+опцион',
    r'форекс\s+(?:брокер|торговля|сигналы)',
    r'(?:mlm|сетевой|многоуровневый)\s+маркетинг',
    r'партнерская\s+программа',
    r'привлечение\s+рефералов',
    r'приглашаю\s+в\s+(?:проект|команду|бизнес)',
    r'уникальная\s+возможность',
    r'только\s+сегодня',
    r'осталось\s+(?:\d+|мало)\s+мест',
    r'(?:казино|ставки|букмекер)\s+онлайн',
    r'выигрыш\s+(?:гарантирован|обеспечен)',
    r'вы\s+(?:выиграли|получили|стали\s+победителем)',
    r'поздравляем\s+с\s+(?:выигрышем|победой)',
    r'(?:iphone|samsung|приз)\s+(?:бесплатно|в\s+подарок)',
]

# Паттерны ботов
BOT_PATTERNS = [
    r'(?:auto[-\s]?reply|автоответ)',
    r'(?:i\'?m|я)\s+(?:a\s+)?bot',
    r'(?:this\s+is\s+)?(?:an?\s+)?automated\s+(?:message|response)',
    r'(?:please\s+)?do\s+not\s+reply',
    r'(?:сообщение|ответ)\s+сгенерирован\s+автоматически',
    r'бот[-\s]?(?:помощник|ассистент|консультант)',
    r'виртуальный\s+(?:помощник|ассистент)',
    r'нажмите\s+\d+\s+для',
    r'(?:press|type)\s+\d+\s+(?:for|to)',
    r'menu\s*:\s*\n.*\d+\s*[-\.]\s*\w+',
    r'выберите\s+(?:пункт|опцию|вариант)',
    r'отправьте\s+(?:цифру|\d+)\s+для',
]

# Подозрительные номера телефонов (короткие, сервисные)
SUSPICIOUS_PHONE_PATTERNS = [
    r'^\+?\d{1,5}$',  # Слишком короткие
    r'^900\d*$',       # Сервисные номера
    r'^8800\d*$',      # Бесплатные линии
]


def load_lists(lists_path: str) -> Tuple[Set[str], Set[str]]:
    """Загружает whitelist и blacklist из файла."""
    whitelist = set()
    blacklist = set()

    if not os.path.exists(lists_path):
        return whitelist, blacklist

    try:
        with open(lists_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            whitelist = set(data.get('whitelist', []))
            blacklist = set(data.get('blacklist', []))
    except Exception as e:
        print(f"Ошибка загрузки списков: {e}")

    return whitelist, blacklist


def save_lists(lists_path: str, whitelist: Set[str], blacklist: Set[str]):
    """Сохраняет whitelist и blacklist в файл."""
    data = {
        'whitelist': list(whitelist),
        'blacklist': list(blacklist),
        'updated_at': datetime.now().isoformat()
    }

    os.makedirs(os.path.dirname(lists_path), exist_ok=True)
    with open(lists_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_messages(messages_path: str) -> List[Dict]:
    """Загружает сообщения из JSONL файла."""
    messages = []

    if not os.path.exists(messages_path):
        print(f"Файл не найден: {messages_path}")
        return messages

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
    except Exception as e:
        print(f"Ошибка загрузки: {e}")

    return messages


def normalize_text(text: str) -> str:
    """Нормализует текст для сравнения."""
    if not text:
        return ""

    # Приводим к нижнему регистру
    text = text.lower()

    # Убираем множественные пробелы
    text = re.sub(r'\s+', ' ', text)

    # Убираем эмодзи и спецсимволы для хеширования
    text = re.sub(r'[^\w\s]', '', text)

    return text.strip()


def get_text_hash(text: str) -> str:
    """Возвращает хеш нормализованного текста."""
    normalized = normalize_text(text)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def count_urls(text: str) -> int:
    """Подсчитывает количество URL в тексте."""
    if not text:
        return 0

    count = 0
    for pattern in URL_PATTERNS:
        count += len(re.findall(pattern, text, re.IGNORECASE))

    return count


def count_call_to_action(text: str) -> int:
    """Подсчитывает призывы к действию."""
    if not text:
        return 0

    count = 0
    for pattern in CALL_TO_ACTION_PATTERNS:
        count += len(re.findall(pattern, text, re.IGNORECASE))

    return count


def check_caps_abuse(text: str) -> float:
    """Проверяет злоупотребление капсом. Возвращает долю заглавных букв."""
    if not text:
        return 0.0

    letters = re.findall(r'[a-zA-Zа-яА-ЯёЁ]', text)
    if not letters:
        return 0.0

    upper_letters = re.findall(r'[A-ZА-ЯЁ]', text)
    return len(upper_letters) / len(letters)


def count_exclamations(text: str) -> int:
    """Подсчитывает восклицательные знаки."""
    if not text:
        return 0

    return text.count('!') + text.count('!!!') * 2


def check_template_phrases(text: str) -> List[str]:
    """Ищет шаблонные спам-фразы."""
    if not text:
        return []

    found = []
    for pattern in TEMPLATE_PHRASES:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found.extend(matches)

    return found


def check_bot_patterns(text: str) -> List[str]:
    """Ищет паттерны бота."""
    if not text:
        return []

    found = []
    for pattern in BOT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found.extend(matches)

    return found


def is_suspicious_phone(phone: str) -> bool:
    """Проверяет, является ли номер подозрительным."""
    if not phone:
        return False

    # Очищаем номер
    cleaned = re.sub(r'[^\d+]', '', phone)

    for pattern in SUSPICIOUS_PHONE_PATTERNS:
        if re.match(pattern, cleaned):
            return True

    return False


def detect_duplicates(messages: List[Dict]) -> Dict[str, List[Dict]]:
    """Находит дубликаты сообщений."""
    hash_to_messages = defaultdict(list)

    for msg in messages:
        text = msg.get('content', '') or msg.get('text', '')
        if not text or len(text) < 20:
            continue

        text_hash = get_text_hash(text)
        hash_to_messages[text_hash].append(msg)

    # Оставляем только те, где больше 1 сообщения
    duplicates = {h: msgs for h, msgs in hash_to_messages.items() if len(msgs) > 1}

    return duplicates


def detect_mass_broadcasts(messages: List[Dict]) -> Dict[str, Dict]:
    """Находит массовые рассылки (одно сообщение разным контактам)."""
    # Группируем по хешу текста и отправителю
    broadcasts = defaultdict(lambda: {'contacts': set(), 'messages': []})

    for msg in messages:
        text = msg.get('content', '') or msg.get('text', '')
        if not text or len(text) < 30:
            continue

        sender_id = msg.get('sender_id') or msg.get('from_id') or ''
        contact_id = msg.get('contact_id') or msg.get('chat_id') or ''

        if not sender_id:
            continue

        text_hash = get_text_hash(text)
        key = f"{sender_id}:{text_hash}"

        broadcasts[key]['contacts'].add(contact_id)
        broadcasts[key]['messages'].append(msg)
        broadcasts[key]['sender'] = sender_id
        broadcasts[key]['text_sample'] = text[:200]

    # Оставляем только рассылки на 3+ контактов
    mass = {k: v for k, v in broadcasts.items()
            if len(v['contacts']) >= 3}

    # Конвертируем set в list для JSON
    for k, v in mass.items():
        v['contacts'] = list(v['contacts'])

    return mass


def calculate_spam_score(
    msg: Dict,
    duplicates: Dict[str, List[Dict]],
    broadcasts: Dict[str, Dict],
    whitelist: Set[str],
    blacklist: Set[str]
) -> Tuple[int, List[str], str]:
    """
    Вычисляет spam score для сообщения.
    Возвращает (score, reasons, category).
    """
    text = msg.get('content', '') or msg.get('text', '')
    sender_id = msg.get('sender_id') or msg.get('from_id') or ''
    sender_phone = msg.get('sender_phone', '') or msg.get('phone', '')

    score = 0
    reasons = []

    # Проверка whitelist
    if sender_id in whitelist or sender_phone in whitelist:
        return (0, ['whitelist'], 'clean')

    # Проверка blacklist
    if sender_id in blacklist or sender_phone in blacklist:
        score += WEIGHTS['blacklist_sender']
        reasons.append('blacklist_sender')

    # Проверка на дубликаты
    if text and len(text) >= 20:
        text_hash = get_text_hash(text)
        if text_hash in duplicates:
            dup_count = len(duplicates[text_hash])
            score += WEIGHTS['duplicate'] * min(dup_count / 2, 2)
            reasons.append(f'duplicate_x{dup_count}')

    # Проверка на массовую рассылку
    if sender_id:
        text_hash = get_text_hash(text) if text else ''
        broadcast_key = f"{sender_id}:{text_hash}"
        if broadcast_key in broadcasts:
            contact_count = len(broadcasts[broadcast_key]['contacts'])
            score += WEIGHTS['mass_broadcast'] * min(contact_count / 3, 2)
            reasons.append(f'mass_broadcast_to_{contact_count}')

    # Подсчет ссылок
    url_count = count_urls(text)
    if url_count >= 3:
        score += WEIGHTS['many_links'] * min(url_count / 3, 2)
        reasons.append(f'links_x{url_count}')

    # Призывы к действию
    cta_count = count_call_to_action(text)
    if cta_count >= 2:
        score += WEIGHTS['call_to_action'] * min(cta_count / 2, 2)
        reasons.append(f'cta_x{cta_count}')

    # Злоупотребление капсом
    caps_ratio = check_caps_abuse(text)
    if caps_ratio > 0.5 and len(text) > 30:
        score += WEIGHTS['caps_abuse'] * (caps_ratio / 0.5)
        reasons.append(f'caps_{caps_ratio:.0%}')

    # Много восклицаний
    excl_count = count_exclamations(text)
    if excl_count >= 5:
        score += WEIGHTS['exclamation_abuse'] * min(excl_count / 5, 2)
        reasons.append(f'exclamations_x{excl_count}')

    # Шаблонные фразы
    templates = check_template_phrases(text)
    if templates:
        score += WEIGHTS['template_phrase'] * min(len(templates), 3)
        reasons.append(f'template_phrases_x{len(templates)}')

    # Паттерны бота
    bot_matches = check_bot_patterns(text)
    if bot_matches:
        score += WEIGHTS['bot_pattern']
        reasons.append('bot_pattern')

    # Подозрительный номер
    if is_suspicious_phone(sender_phone):
        score += WEIGHTS['suspicious_phone']
        reasons.append('suspicious_phone')

    # Ограничиваем score до 100
    score = min(int(score), 100)

    # Определяем категорию
    if score >= 70:
        category = 'spam'
    elif score >= 40:
        category = 'suspicious'
    elif score >= 20:
        category = 'low_risk'
    else:
        category = 'clean'

    return (score, reasons, category)


def analyze_messages(
    messages: List[Dict],
    whitelist: Set[str],
    blacklist: Set[str]
) -> List[Dict]:
    """Анализирует все сообщения на спам."""

    print("\nПоиск дубликатов...")
    duplicates = detect_duplicates(messages)
    print(f"  Найдено {len(duplicates)} групп дубликатов")

    print("\nПоиск массовых рассылок...")
    broadcasts = detect_mass_broadcasts(messages)
    print(f"  Найдено {len(broadcasts)} рассылок")

    print("\nАнализ сообщений...")
    results = []

    for i, msg in enumerate(messages):
        if (i + 1) % 1000 == 0:
            print(f"  Обработано {i + 1}/{len(messages)}")

        score, reasons, category = calculate_spam_score(
            msg, duplicates, broadcasts, whitelist, blacklist
        )

        result = {
            'message_id': msg.get('id', msg.get('message_id', '')),
            'sender_id': msg.get('sender_id', msg.get('from_id', '')),
            'sender_name': msg.get('sender_name', msg.get('from_name', '')),
            'contact_id': msg.get('contact_id', msg.get('chat_id', '')),
            'date': msg.get('date', msg.get('timestamp', '')),
            'text_preview': (msg.get('content', '') or msg.get('text', ''))[:100],
            'spam_score': score,
            'spam_reasons': reasons,
            'spam_category': category,
            'original_message': msg
        }

        results.append(result)

    return results


def generate_statistics(results: List[Dict]) -> Dict:
    """Генерирует статистику по спаму."""

    stats = {
        'total_messages': len(results),
        'by_category': defaultdict(int),
        'by_reason': defaultdict(int),
        'top_spammers': defaultdict(lambda: {'count': 0, 'total_score': 0}),
        'score_distribution': {
            '0-19': 0,
            '20-39': 0,
            '40-69': 0,
            '70-100': 0
        },
        'spam_rate': 0.0,
        'avg_spam_score': 0.0
    }

    total_score = 0

    for r in results:
        score = r['spam_score']
        category = r['spam_category']
        sender_id = r['sender_id']

        stats['by_category'][category] += 1
        total_score += score

        for reason in r['spam_reasons']:
            # Извлекаем базовую причину без счетчика
            base_reason = re.sub(r'_x\d+$', '', reason)
            base_reason = re.sub(r'_to_\d+$', '', base_reason)
            stats['by_reason'][base_reason] += 1

        if sender_id:
            stats['top_spammers'][sender_id]['count'] += 1
            stats['top_spammers'][sender_id]['total_score'] += score
            stats['top_spammers'][sender_id]['name'] = r['sender_name']

        # Распределение score
        if score < 20:
            stats['score_distribution']['0-19'] += 1
        elif score < 40:
            stats['score_distribution']['20-39'] += 1
        elif score < 70:
            stats['score_distribution']['40-69'] += 1
        else:
            stats['score_distribution']['70-100'] += 1

    # Вычисляем средние значения
    if results:
        spam_count = stats['by_category'].get('spam', 0)
        stats['spam_rate'] = spam_count / len(results) * 100
        stats['avg_spam_score'] = total_score / len(results)

    # Топ спамеров (по среднему score)
    top_spammers = []
    for sender_id, data in stats['top_spammers'].items():
        if data['count'] >= 3:  # Минимум 3 сообщения
            avg_score = data['total_score'] / data['count']
            if avg_score >= 30:  # Минимальный средний score
                top_spammers.append({
                    'sender_id': sender_id,
                    'sender_name': data['name'],
                    'message_count': data['count'],
                    'avg_score': round(avg_score, 1)
                })

    top_spammers.sort(key=lambda x: x['avg_score'], reverse=True)
    stats['top_spammers'] = top_spammers[:20]

    # Конвертируем defaultdict в dict
    stats['by_category'] = dict(stats['by_category'])
    stats['by_reason'] = dict(stats['by_reason'])

    return stats


def detect_spam(
    messages_path: str,
    output_path: str,
    lists_path: str,
    threshold: int = 40
):
    """
    Основная функция детекции спама.

    Args:
        messages_path: Путь к JSONL файлу сообщений
        output_path: Путь для сохранения результата
        lists_path: Путь к файлу whitelist/blacklist
        threshold: Порог для отметки как спам (по умолчанию 40)
    """
    print("=" * 60)
    print("Детекция спама в WhatsApp чатах")
    print("=" * 60)
    print()

    # Загрузка данных
    messages = load_messages(messages_path)
    if not messages:
        print("Нет сообщений для анализа")
        return

    whitelist, blacklist = load_lists(lists_path)
    print(f"Whitelist: {len(whitelist)} контактов")
    print(f"Blacklist: {len(blacklist)} контактов")

    # Анализ
    results = analyze_messages(messages, whitelist, blacklist)

    # Статистика
    stats = generate_statistics(results)

    # Фильтруем только подозрительные и спам
    flagged = [r for r in results if r['spam_score'] >= threshold]

    # Формируем результат
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_analyzed': len(messages),
            'threshold': threshold,
            'flagged_count': len(flagged)
        },
        'statistics': stats,
        'flagged_messages': sorted(flagged, key=lambda x: x['spam_score'], reverse=True),
        'all_results': results  # Полные данные
    }

    # Сохранение
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    # Выводим статистику
    print("\n" + "=" * 60)
    print("Результаты анализа")
    print("=" * 60)
    print(f"\nВсего сообщений: {stats['total_messages']}")
    print(f"Средний spam score: {stats['avg_spam_score']:.1f}")
    print(f"Уровень спама: {stats['spam_rate']:.1f}%")
    print()

    print("По категориям:")
    for cat, count in sorted(stats['by_category'].items()):
        pct = count / stats['total_messages'] * 100 if stats['total_messages'] else 0
        print(f"  {cat}: {count} ({pct:.1f}%)")
    print()

    print("Распределение score:")
    for range_name, count in stats['score_distribution'].items():
        pct = count / stats['total_messages'] * 100 if stats['total_messages'] else 0
        bar = '#' * int(pct / 2)
        print(f"  {range_name}: {count} ({pct:.1f}%) {bar}")
    print()

    if stats['by_reason']:
        print("Топ причин:")
        for reason, count in sorted(stats['by_reason'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {reason}: {count}")
        print()

    if stats['top_spammers']:
        print("Топ подозрительных отправителей:")
        for spammer in stats['top_spammers'][:10]:
            print(f"  {spammer['sender_name'] or spammer['sender_id']}: "
                  f"avg={spammer['avg_score']}, msgs={spammer['message_count']}")
        print()

    print(f"Отмечено подозрительных (score >= {threshold}): {len(flagged)}")
    print(f"\nРезультат сохранен: {output_path}")


def add_to_list(lists_path: str, contact_id: str, list_type: str):
    """Добавляет контакт в whitelist или blacklist."""
    whitelist, blacklist = load_lists(lists_path)

    if list_type == 'whitelist':
        whitelist.add(contact_id)
        blacklist.discard(contact_id)  # Удаляем из blacklist если был
        print(f"Добавлен в whitelist: {contact_id}")
    elif list_type == 'blacklist':
        blacklist.add(contact_id)
        whitelist.discard(contact_id)  # Удаляем из whitelist если был
        print(f"Добавлен в blacklist: {contact_id}")

    save_lists(lists_path, whitelist, blacklist)


def remove_from_list(lists_path: str, contact_id: str, list_type: str):
    """Удаляет контакт из whitelist или blacklist."""
    whitelist, blacklist = load_lists(lists_path)

    if list_type == 'whitelist':
        whitelist.discard(contact_id)
        print(f"Удален из whitelist: {contact_id}")
    elif list_type == 'blacklist':
        blacklist.discard(contact_id)
        print(f"Удален из blacklist: {contact_id}")

    save_lists(lists_path, whitelist, blacklist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Детекция спама в WhatsApp чатах"
    )
    parser.add_argument(
        "--messages",
        default="D:/Downloads/Chats/_база/raw/all_messages.jsonl",
        help="Путь к файлу сообщений"
    )
    parser.add_argument(
        "-o", "--output",
        default="D:/Downloads/Chats/_база/json/spam_analysis.json",
        help="Путь для сохранения результата"
    )
    parser.add_argument(
        "--lists",
        default="D:/Downloads/Chats/_база/json/spam_lists.json",
        help="Путь к файлу whitelist/blacklist"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=40,
        help="Порог spam score для отметки (по умолчанию 40)"
    )
    parser.add_argument(
        "--add-whitelist",
        metavar="CONTACT_ID",
        help="Добавить контакт в whitelist"
    )
    parser.add_argument(
        "--add-blacklist",
        metavar="CONTACT_ID",
        help="Добавить контакт в blacklist"
    )
    parser.add_argument(
        "--remove-whitelist",
        metavar="CONTACT_ID",
        help="Удалить контакт из whitelist"
    )
    parser.add_argument(
        "--remove-blacklist",
        metavar="CONTACT_ID",
        help="Удалить контакт из blacklist"
    )

    args = parser.parse_args()

    # Операции со списками
    if args.add_whitelist:
        add_to_list(args.lists, args.add_whitelist, 'whitelist')
    elif args.add_blacklist:
        add_to_list(args.lists, args.add_blacklist, 'blacklist')
    elif args.remove_whitelist:
        remove_from_list(args.lists, args.remove_whitelist, 'whitelist')
    elif args.remove_blacklist:
        remove_from_list(args.lists, args.remove_blacklist, 'blacklist')
    else:
        # Основной анализ
        detect_spam(
            messages_path=args.messages,
            output_path=args.output,
            lists_path=args.lists,
            threshold=args.threshold
        )
