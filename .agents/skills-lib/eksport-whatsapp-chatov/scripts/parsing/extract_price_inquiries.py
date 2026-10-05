#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Извлечение ценовых запросов из чатов.

Входной файл: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходной файл: D:/Downloads/Chats/_база/json/price_inquiries.json

Задача: Найти все сообщения где клиенты спрашивают о ценах и связать их
с ответами, содержащими цену.
"""

import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import JSON_DIR, RAW_DIR, ensure_directories
except ImportError:
    # Fallback пути
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")

    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ПОИСКА ЦЕНОВЫХ ЗАПРОСОВ
# ═══════════════════════════════════════════════════════════════
PRICE_INQUIRY_PATTERNS = [
    r'сколько\s+стоит',
    r'какая\s+цена',
    r'почём',
    r'почем',
    r'прайс',
    r'стоимость',
    r'цена\s+на',
    r'расценки',
    r'сколько\s+будет\s+стоить',
    r'во\s+сколько\s+обойдётся',
    r'во\s+сколько\s+обойдется',
    r'по\s+какой\s+цене',
    r'ценник',
    r'тариф',
    r'сколько\s+за',
    r'какой\s+прайс',
    r'цены\s+на',
    r'стоит\s+ли',  # "стоит ли это столько"
    r'сколько\s+выйдет',
    r'почём\s+выйдет',
    r'почем\s+выйдет',
    r'какая\s+стоимость',
    r'узнать\s+(?:цену|стоимость)',
    r'скинь(?:те)?\s+(?:цену|стоимость|прайс)',
    r'пришли(?:те)?\s+(?:цену|стоимость|прайс)',
]

# Скомпилированный паттерн для поиска
PRICE_INQUIRY_RE = re.compile(
    '|'.join(f'({p})' for p in PRICE_INQUIRY_PATTERNS),
    re.IGNORECASE
)

# ═══════════════════════════════════════════════════════════════
# КАТЕГОРИИ ПРОДУКТОВ
# ═══════════════════════════════════════════════════════════════
CATEGORY_KEYWORDS = {
    'tour': [
        'экскурсия', 'экскурсию', 'тур', 'сафари', 'абу-даби', 'абу даби',
        'дубай', 'шарджа', 'фуджейра', 'аль-айн', 'аль айн', 'рас-аль-хайма',
        'музей', 'мечеть', 'burj', 'бурдж', 'пустыня', 'desert', 'city tour',
        'обзорная', 'miracle garden', 'global village', 'frame', 'creek',
        'marina', 'palm', 'atlantis', 'louvre', 'лувр', 'ferrari world',
        'warner bros', 'legoland', 'motiongate', 'bollywood', 'aquarium',
        'аквариум', 'dubai mall', 'дубай молл', 'старый город', 'gold souk',
        'spice souk', 'deira', 'дейра', 'бастакия', 'al fahidi', 'jumeirah',
        'джумейра', 'miracle', 'миракл', 'glow garden', 'хатта', 'hatta',
    ],
    'transfer': [
        'трансфер', 'встреча', 'аэропорт', 'airport', 'transfer', 'проводы',
        'встретить', 'забрать', 'отвезти', 'доставка', 'dxb', 'dwc', 'auh',
        'терминал', 'terminal', 'прилёт', 'прилет', 'вылет', 'рейс',
    ],
    'yacht': [
        'яхта', 'яхту', 'yacht', 'катер', 'лодка', 'boat', 'круиз', 'cruise',
        'рыбалка', 'fishing', 'marina', 'марина', 'морская прогулка',
        'закат', 'sunset', 'завтрак на яхте', 'ужин на яхте',
    ],
    'tickets': [
        'билет', 'билеты', 'ticket', 'входной', 'парк', 'park', 'theme park',
        'aquaventure', 'waterpark', 'аквапарк', 'wild wadi', 'ski dubai',
        'img worlds', 'кидзания', 'kidzania', 'observation deck', 'смотровая',
        'at the top', 'view', 'ain dubai', 'колесо', 'sky views', 'zipline',
        'xline', 'прыжок', 'skydive', 'парашют', 'balloon', 'шар', 'вход',
    ],
    'exchange': [
        'обмен', 'обменять', 'курс', 'валюта', 'exchange', 'дирхам', 'рубль',
        'рубли', 'доллар', 'dollar', 'usd', 'aed', 'rub', 'usdt', 'крипта',
        'crypto', 'tether', 'перевод', 'конвертация',
    ],
    'car_rental': [
        'аренда', 'машина', 'авто', 'автомобиль', 'car', 'rental', 'rent',
        'прокат', 'взять машину', 'снять машину', 'lamborghini', 'ferrari',
        'porsche', 'rolls', 'bentley', 'mercedes', 'bmw', 'range rover',
        'суперкар', 'supercar', 'спорткар', 'люкс авто', 'luxury car',
        'водитель', 'с водителем', 'without driver', 'self drive',
    ],
    'catering': [
        'кейтеринг', 'catering', 'еда', 'food', 'банкет', 'фуршет', 'обед',
        'ужин', 'завтрак', 'пикник', 'picnic', 'барбекю', 'bbq', 'шашлык',
    ],
    'restaurant': [
        'ресторан', 'restaurant', 'бронь столика', 'столик', 'reservation',
        'кафе', 'cafe', 'lounge', 'лаунж', 'бар', 'bar', 'бранч', 'brunch',
        'dinner', 'lunch', 'меню', 'menu',
    ],
    'visa': [
        'виза', 'visa', 'визу', 'оформление визы', 'transit', 'транзит',
        'резидент', 'resident', 'tourist visa', 'туристическая виза',
    ],
    'hotel': [
        'отель', 'hotel', 'гостиница', 'бронирование', 'номер', 'room',
        'ночь', 'проживание', 'accommodation', 'заселение', 'check-in',
    ],
    'photo': [
        'фото', 'photo', 'съёмка', 'съемка', 'фотосессия', 'photoshoot',
        'фотограф', 'photographer', 'видео', 'video', 'drone', 'дрон',
    ],
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ИЗВЛЕЧЕНИЯ ЦЕН ИЗ ОТВЕТОВ
# ═══════════════════════════════════════════════════════════════
PRICE_EXTRACTION_PATTERNS = [
    # Форматы с валютой после числа
    r'(\d{1,3}(?:[\s,\.]\d{3})*(?:[.,]\d{1,2})?)\s*(AED|дирхам[ов]?|₽|руб(?:лей)?|RUB|\$|USD|долл(?:аров)?)',
    # Форматы с валютой перед числом
    r'(AED|дирхам[ов]?|₽|руб(?:лей)?|RUB|\$|USD|долл(?:аров)?)\s*(\d{1,3}(?:[\s,\.]\d{3})*(?:[.,]\d{1,2})?)',
    # Просто число с "стоит/цена"
    r'(?:стоит|цена|стоимость)[:\s]*(\d{1,3}(?:[\s,\.]\d{3})*(?:[.,]\d{1,2})?)',
    # Число с "за человека/за пару/за машину"
    r'(\d{1,3}(?:[\s,\.]\d{3})*)\s*(?:за\s+(?:человека|персону|пару|группу|машину|авто))',
]

CURRENCY_MAPPING = {
    'aed': 'AED',
    'дирхам': 'AED',
    'дирхамов': 'AED',
    '₽': 'RUB',
    'руб': 'RUB',
    'рублей': 'RUB',
    'rub': 'RUB',
    '$': 'USD',
    'usd': 'USD',
    'долл': 'USD',
    'долларов': 'USD',
}


def normalize_currency(currency: str) -> str:
    """Нормализовать название валюты."""
    if not currency:
        return 'AED'  # По умолчанию в ОАЭ
    return CURRENCY_MAPPING.get(currency.lower().strip(), currency.upper())


def parse_price(text: str) -> tuple[Optional[float], Optional[str]]:
    """Извлечь цену и валюту из текста."""
    for pattern in PRICE_EXTRACTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()

            # Определяем, какая группа - число, какая - валюта
            price_str = None
            currency = None

            for g in groups:
                if g is None:
                    continue
                # Если это число
                if re.match(r'[\d\s,\.]+$', g):
                    price_str = g
                else:
                    currency = g

            if price_str:
                # Очистка и преобразование числа
                price_str = price_str.replace(' ', '').replace(',', '.')
                # Убираем лишние точки (тысячные разделители)
                parts = price_str.split('.')
                if len(parts) > 2:
                    price_str = ''.join(parts[:-1]) + '.' + parts[-1]
                elif len(parts) == 2 and len(parts[1]) == 3:
                    # 1.500 -> 1500 (тысячный разделитель)
                    price_str = ''.join(parts)

                try:
                    price = float(price_str)
                    currency = normalize_currency(currency)
                    return price, currency
                except ValueError:
                    continue

    return None, None


def determine_category(text: str) -> str:
    """Определить категорию продукта по тексту."""
    text_lower = text.lower()

    # Подсчитываем совпадения для каждой категории
    category_scores = defaultdict(int)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                category_scores[category] += 1

    if category_scores:
        # Возвращаем категорию с максимальным счётом
        return max(category_scores.items(), key=lambda x: x[1])[0]

    return 'other'


def extract_product_name(text: str, category: str) -> str:
    """Извлечь название продукта из запроса."""
    text_lower = text.lower()

    # Удаляем стандартные фразы запроса цены
    cleaned = text_lower
    for pattern in PRICE_INQUIRY_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Удаляем знаки вопроса и лишние пробелы
    cleaned = re.sub(r'[?!]+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Ищем ключевые слова категории
    keywords_found = []
    if category in CATEGORY_KEYWORDS:
        for keyword in CATEGORY_KEYWORDS[category]:
            if keyword.lower() in text_lower:
                keywords_found.append(keyword)

    if keywords_found:
        # Берём самое длинное ключевое слово
        return max(keywords_found, key=len)

    # Возвращаем очищенный текст, но не более 100 символов
    if len(cleaned) > 100:
        cleaned = cleaned[:100] + '...'

    return cleaned if cleaned else 'не указано'


def is_price_inquiry(text: str) -> bool:
    """Проверить, является ли сообщение запросом цены."""
    if not text:
        return False
    return bool(PRICE_INQUIRY_RE.search(text))


def load_contacts_mapping() -> dict:
    """Загрузить маппинг JID -> contact_id из файла контактов."""
    contacts_file = JSON_DIR / "contacts.json"
    mapping = {}

    if contacts_file.exists():
        try:
            with open(contacts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for contact in data.get('contacts', []):
                    jid = contact.get('jid')
                    contact_id = contact.get('contact_id')
                    if jid and contact_id:
                        mapping[jid] = contact_id
        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось загрузить contacts.json: {e}")

    return mapping


def process_messages(input_file: Path, output_file: Path):
    """Обработать все сообщения и извлечь ценовые запросы."""
    print("=" * 60)
    print("ИЗВЛЕЧЕНИЕ ЦЕНОВЫХ ЗАПРОСОВ ИЗ ЧАТОВ")
    print("=" * 60)

    ensure_directories()

    if not input_file.exists():
        print(f"[ОШИБКА] Входной файл не найден: {input_file}")
        print("Сначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    print(f"\nВходной файл: {input_file}")
    print(f"Выходной файл: {output_file}")

    # Загружаем маппинг контактов
    contacts_mapping = load_contacts_mapping()
    print(f"Загружено контактов: {len(contacts_mapping)}")

    # Структуры данных
    price_inquiries = []
    messages_by_chat = defaultdict(list)  # jid -> [messages] для поиска ответов

    # Первый проход: загрузка всех сообщений и группировка по чатам
    print("\nПервый проход: загрузка сообщений...")
    total_messages = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                msg = json.loads(line)
                total_messages += 1
                jid = msg.get('jid', 'unknown')
                messages_by_chat[jid].append(msg)
            except json.JSONDecodeError:
                continue

    print(f"Загружено сообщений: {total_messages:,}")
    print(f"Уникальных чатов: {len(messages_by_chat)}")

    # Второй проход: поиск ценовых запросов и связывание с ответами
    print("\nВторой проход: поиск ценовых запросов...")

    for jid, messages in messages_by_chat.items():
        # Сортируем сообщения по времени
        messages.sort(key=lambda x: x.get('datetime', ''))

        for i, msg in enumerate(messages):
            text = msg.get('text', '')
            is_from_me = msg.get('is_from_me', False)

            # Ищем только запросы от клиентов (не от меня)
            if is_from_me or not text:
                continue

            if not is_price_inquiry(text):
                continue

            # Нашли запрос цены!
            category = determine_category(text)
            product_mentioned = extract_product_name(text, category)

            # Ищем ответ (следующие сообщения от "Я" в течение 24 часов)
            responded = False
            response_text = None
            price_quoted = None
            currency = None

            inquiry_datetime = msg.get('datetime', '')

            # Просматриваем следующие сообщения
            for j in range(i + 1, min(i + 20, len(messages))):  # Ищем в следующих 20 сообщениях
                next_msg = messages[j]

                # Проверяем, что это ответ от "Я"
                if not next_msg.get('is_from_me', False):
                    continue

                next_text = next_msg.get('text', '')
                if not next_text:
                    continue

                # Нашли ответ
                responded = True
                response_text = next_text[:500]  # Ограничиваем длину

                # Пытаемся извлечь цену из ответа
                price_quoted, currency = parse_price(next_text)

                # Если нашли цену, прекращаем поиск
                if price_quoted:
                    break

            # Создаём запись о ценовом запросе
            inquiry = {
                'inquiry_id': str(uuid.uuid4()),
                'contact_id': contacts_mapping.get(jid),
                'jid': jid,
                'chat_name': msg.get('chat_name'),
                'source': msg.get('source'),
                'datetime': inquiry_datetime,
                'text': text[:500],  # Ограничиваем длину
                'product_mentioned': product_mentioned,
                'category': category,
                'responded': responded,
                'response_text': response_text,
                'price_quoted': price_quoted,
                'currency': currency,
            }

            price_inquiries.append(inquiry)

    print(f"Найдено ценовых запросов: {len(price_inquiries)}")

    # Вычисляем статистику
    print("\nВычисление статистики...")

    # По категориям
    by_category = defaultdict(int)
    for inquiry in price_inquiries:
        by_category[inquiry['category']] += 1

    # Топ продукты
    product_counts = defaultdict(int)
    for inquiry in price_inquiries:
        product = inquiry['product_mentioned']
        if product and product != 'не указано':
            product_counts[product] += 1

    top_products = sorted(
        [{'name': name, 'count': count} for name, count in product_counts.items()],
        key=lambda x: x['count'],
        reverse=True
    )[:50]  # Топ-50 продуктов

    # Конверсия (ответили / всего)
    responded_count = sum(1 for i in price_inquiries if i['responded'])
    conversion_rate = responded_count / len(price_inquiries) if price_inquiries else 0

    # Среди ответов - сколько с ценой
    with_price_count = sum(1 for i in price_inquiries if i['price_quoted'])
    price_rate = with_price_count / responded_count if responded_count else 0

    # По источникам
    by_source = defaultdict(int)
    for inquiry in price_inquiries:
        source = inquiry.get('source', 'unknown')
        by_source[source] += 1

    # Формируем результат
    result = {
        'generated_at': datetime.now().isoformat(),
        'input_file': str(input_file),
        'price_inquiries': price_inquiries,
        'statistics': {
            'total_inquiries': len(price_inquiries),
            'responded': responded_count,
            'with_price_quoted': with_price_count,
            'by_category': dict(by_category),
            'by_source': dict(by_source),
            'top_products': top_products,
            'conversion_rate': round(conversion_rate, 3),
            'price_quote_rate': round(price_rate, 3),
        }
    }

    # Сохраняем результат
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Выводим статистику
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"Всего запросов о цене: {len(price_inquiries)}")
    print(f"Получили ответ: {responded_count} ({conversion_rate*100:.1f}%)")
    print(f"С указанием цены: {with_price_count} ({price_rate*100:.1f}% от ответов)")

    print(f"\nПо категориям:")
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

    print(f"\nТоп-10 продуктов:")
    for item in top_products[:10]:
        print(f"  {item['name']}: {item['count']}")

    print(f"\nПо источникам:")
    for source, count in by_source.items():
        print(f"  {source}: {count}")

    print(f"\nРезультат сохранён: {output_file}")
    print(f"Размер файла: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    """Основная функция."""
    input_file = RAW_DIR / "all_messages.jsonl"
    output_file = JSON_DIR / "price_inquiries.json"

    process_messages(input_file, output_file)


if __name__ == "__main__":
    main()
