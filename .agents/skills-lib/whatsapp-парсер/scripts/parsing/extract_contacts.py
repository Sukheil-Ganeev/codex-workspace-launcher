#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение уникальных контактов из all_messages.jsonl.

Вход: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выход: D:/Downloads/Chats/_база/json/contacts.json

Функции:
- Агрегация всех уникальных контактов по JID
- Определение is_group по JID (@g.us = группа)
- Извлечение телефона из JID
- Определение country_code
- Детекция языка по частотности слов
- Объединение контактов из двух источников (source="both")
"""

import json
import re
import sys
import uuid
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent))
from config import RAW_DIR, JSON_DIR, ensure_directories

# Настройка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ
# ═══════════════════════════════════════════════════════════════

INPUT_FILE = RAW_DIR / "all_messages.jsonl"
OUTPUT_FILE = JSON_DIR / "contacts.json"

# Словари для детекции языка
RUSSIAN_WORDS = {
    'привет', 'здравствуйте', 'добрый', 'день', 'утро', 'вечер',
    'спасибо', 'пожалуйста', 'хорошо', 'ладно', 'понял', 'поняла',
    'да', 'нет', 'ок', 'окей', 'сколько', 'когда', 'где', 'как',
    'нужно', 'можно', 'буду', 'будет', 'есть', 'был', 'была',
    'сегодня', 'завтра', 'вчера', 'сейчас', 'потом', 'скоро',
    'рублей', 'рубль', 'руб', 'дирхам', 'курс', 'перевод',
    'экскурсия', 'тур', 'билет', 'трансфер', 'отель', 'аэропорт',
    'человек', 'взрослых', 'детей', 'группа', 'гости', 'клиент'
}

ENGLISH_WORDS = {
    'hello', 'hi', 'good', 'morning', 'afternoon', 'evening',
    'thanks', 'thank', 'please', 'okay', 'yes', 'no', 'how',
    'much', 'when', 'where', 'what', 'need', 'want', 'have',
    'will', 'can', 'today', 'tomorrow', 'now', 'later', 'soon',
    'tour', 'transfer', 'hotel', 'airport', 'ticket', 'booking',
    'price', 'cost', 'total', 'payment', 'person', 'adult', 'child'
}

ARABIC_WORDS = {
    'مرحبا', 'السلام', 'عليكم', 'شكرا', 'من', 'فضلك', 'نعم', 'لا',
    'كيف', 'متى', 'أين', 'ماذا', 'كم', 'السعر', 'الحجز', 'جولة',
    'فندق', 'مطار', 'تأشيرة', 'درهم', 'دولار', 'اليوم', 'غدا'
}

# Коды стран по префиксам телефонов (расширенный список)
COUNTRY_CODES = {
    # СНГ и Россия
    '7': 'RU',      # Россия, Казахстан (+77 - Казахстан)
    '77': 'KZ',     # Казахстан (приоритет над 7)
    '380': 'UA',    # Украина
    '375': 'BY',    # Беларусь
    '998': 'UZ',    # Узбекистан
    '996': 'KG',    # Кыргызстан
    '992': 'TJ',    # Таджикистан
    '374': 'AM',    # Армения
    '995': 'GE',    # Грузия
    '994': 'AZ',    # Азербайджан
    '373': 'MD',    # Молдова
    '993': 'TM',    # Туркменистан

    # ОАЭ и Ближний Восток
    '971': 'AE',    # ОАЭ
    '966': 'SA',    # Саудовская Аравия
    '965': 'KW',    # Кувейт
    '974': 'QA',    # Катар
    '973': 'BH',    # Бахрейн
    '968': 'OM',    # Оман
    '962': 'JO',    # Иордания
    '961': 'LB',    # Ливан
    '964': 'IQ',    # Ирак
    '963': 'SY',    # Сирия
    '967': 'YE',    # Йемен
    '970': 'PS',    # Палестина
    '972': 'IL',    # Израиль

    # Африка
    '20': 'EG',     # Египет
    '212': 'MA',    # Марокко
    '213': 'DZ',    # Алжир
    '216': 'TN',    # Тунис
    '234': 'NG',    # Нигерия
    '27': 'ZA',     # ЮАР
    '254': 'KE',    # Кения

    # Европа
    '44': 'GB',     # Великобритания
    '49': 'DE',     # Германия
    '33': 'FR',     # Франция
    '39': 'IT',     # Италия
    '34': 'ES',     # Испания
    '31': 'NL',     # Нидерланды
    '32': 'BE',     # Бельгия
    '41': 'CH',     # Швейцария
    '43': 'AT',     # Австрия
    '48': 'PL',     # Польша
    '420': 'CZ',    # Чехия
    '421': 'SK',    # Словакия
    '36': 'HU',     # Венгрия
    '40': 'RO',     # Румыния
    '359': 'BG',    # Болгария
    '30': 'GR',     # Греция
    '90': 'TR',     # Турция
    '351': 'PT',    # Португалия
    '46': 'SE',     # Швеция
    '47': 'NO',     # Норвегия
    '45': 'DK',     # Дания
    '358': 'FI',    # Финляндия
    '372': 'EE',    # Эстония
    '371': 'LV',    # Латвия
    '370': 'LT',    # Литва
    '385': 'HR',    # Хорватия
    '386': 'SI',    # Словения
    '381': 'RS',    # Сербия
    '382': 'ME',    # Черногория
    '387': 'BA',    # Босния

    # Америка
    '1': 'US',      # США, Канада
    '52': 'MX',     # Мексика
    '55': 'BR',     # Бразилия
    '54': 'AR',     # Аргентина

    # Азия
    '86': 'CN',     # Китай
    '91': 'IN',     # Индия
    '81': 'JP',     # Япония
    '82': 'KR',     # Южная Корея
    '65': 'SG',     # Сингапур
    '60': 'MY',     # Малайзия
    '66': 'TH',     # Таиланд
    '62': 'ID',     # Индонезия
    '63': 'PH',     # Филиппины
    '84': 'VN',     # Вьетнам
    '92': 'PK',     # Пакистан
    '880': 'BD',    # Бангладеш
    '94': 'LK',     # Шри-Ланка
    '977': 'NP',    # Непал
    '98': 'IR',     # Иран
    '93': 'AF',     # Афганистан

    # Океания
    '61': 'AU',     # Австралия
    '64': 'NZ',     # Новая Зеландия
}

# Названия стран на русском
COUNTRY_NAMES = {
    'RU': 'Россия', 'KZ': 'Казахстан', 'UA': 'Украина', 'BY': 'Беларусь',
    'UZ': 'Узбекистан', 'KG': 'Кыргызстан', 'TJ': 'Таджикистан',
    'AM': 'Армения', 'GE': 'Грузия', 'AZ': 'Азербайджан', 'MD': 'Молдова',
    'TM': 'Туркменистан',

    'AE': 'ОАЭ', 'SA': 'Саудовская Аравия', 'KW': 'Кувейт', 'QA': 'Катар',
    'BH': 'Бахрейн', 'OM': 'Оман', 'JO': 'Иордания', 'LB': 'Ливан',
    'IQ': 'Ирак', 'SY': 'Сирия', 'YE': 'Йемен', 'PS': 'Палестина', 'IL': 'Израиль',

    'EG': 'Египет', 'MA': 'Марокко', 'DZ': 'Алжир', 'TN': 'Тунис',
    'NG': 'Нигерия', 'ZA': 'ЮАР', 'KE': 'Кения',

    'GB': 'Великобритания', 'DE': 'Германия', 'FR': 'Франция', 'IT': 'Италия',
    'ES': 'Испания', 'NL': 'Нидерланды', 'BE': 'Бельгия', 'CH': 'Швейцария',
    'AT': 'Австрия', 'PL': 'Польша', 'CZ': 'Чехия', 'SK': 'Словакия',
    'HU': 'Венгрия', 'RO': 'Румыния', 'BG': 'Болгария', 'GR': 'Греция',
    'TR': 'Турция', 'PT': 'Португалия', 'SE': 'Швеция', 'NO': 'Норвегия',
    'DK': 'Дания', 'FI': 'Финляндия', 'EE': 'Эстония', 'LV': 'Латвия',
    'LT': 'Литва', 'HR': 'Хорватия', 'SI': 'Словения', 'RS': 'Сербия',
    'ME': 'Черногория', 'BA': 'Босния',

    'US': 'США', 'MX': 'Мексика', 'BR': 'Бразилия', 'AR': 'Аргентина',

    'CN': 'Китай', 'IN': 'Индия', 'JP': 'Япония', 'KR': 'Южная Корея',
    'SG': 'Сингапур', 'MY': 'Малайзия', 'TH': 'Таиланд', 'ID': 'Индонезия',
    'PH': 'Филиппины', 'VN': 'Вьетнам', 'PK': 'Пакистан', 'BD': 'Бангладеш',
    'LK': 'Шри-Ланка', 'NP': 'Непал', 'IR': 'Иран', 'AF': 'Афганистан',

    'AU': 'Австралия', 'NZ': 'Новая Зеландия',
}

# Языковые предпочтения по странам
COUNTRY_LANGUAGE_PREFERENCES = {
    # Русскоязычные
    'RU': ['ru'],
    'KZ': ['ru', 'kk'],
    'UA': ['ru', 'uk'],
    'BY': ['ru', 'be'],
    'UZ': ['ru', 'uz'],
    'KG': ['ru', 'ky'],
    'TJ': ['ru', 'tg'],
    'AM': ['ru', 'hy'],
    'GE': ['ru', 'ka'],
    'AZ': ['ru', 'az'],
    'MD': ['ru', 'ro'],
    'TM': ['ru', 'tk'],

    # Арабоязычные
    'AE': ['ar', 'en'],
    'SA': ['ar'],
    'KW': ['ar', 'en'],
    'QA': ['ar', 'en'],
    'BH': ['ar', 'en'],
    'OM': ['ar'],
    'JO': ['ar'],
    'LB': ['ar', 'fr', 'en'],
    'IQ': ['ar'],
    'SY': ['ar'],
    'YE': ['ar'],
    'PS': ['ar'],
    'EG': ['ar'],
    'MA': ['ar', 'fr'],
    'DZ': ['ar', 'fr'],
    'TN': ['ar', 'fr'],

    # Европа
    'GB': ['en'],
    'US': ['en', 'es'],
    'DE': ['de'],
    'FR': ['fr'],
    'IT': ['it'],
    'ES': ['es'],
    'NL': ['nl', 'en'],
    'CH': ['de', 'fr', 'it'],
    'AT': ['de'],
    'PL': ['pl'],
    'CZ': ['cs'],
    'TR': ['tr'],
    'GR': ['el'],
    'PT': ['pt'],
    'SE': ['sv', 'en'],
    'NO': ['no', 'en'],

    # Азия
    'CN': ['zh'],
    'IN': ['hi', 'en'],
    'JP': ['ja'],
    'KR': ['ko'],
    'TH': ['th', 'en'],
    'VN': ['vi'],
    'PK': ['ur', 'en'],
    'BD': ['bn'],
    'IR': ['fa'],

    # Океания
    'AU': ['en'],
    'NZ': ['en'],
}


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def extract_phone_from_jid(jid: str) -> str:
    """Извлекает номер телефона из JID."""
    if not jid:
        return ""

    # Извлекаем цифры до @
    match = re.match(r'^(\d+)@', jid)
    if match:
        phone = match.group(1)
        # Форматируем с +
        return f"+{phone}"

    return ""


def determine_country_code(phone: str) -> str:
    """Определяет код страны по номеру телефона."""
    if not phone:
        return ""

    # Убираем + в начале
    digits = phone.lstrip('+')

    # Проверяем по убыванию длины префикса (приоритет длинным)
    for prefix_len in [3, 2, 1]:
        prefix = digits[:prefix_len]
        if prefix in COUNTRY_CODES:
            return prefix

    return ""


def get_country_iso(phone: str) -> str:
    """Получить ISO код страны по номеру телефона."""
    prefix = determine_country_code(phone)
    return COUNTRY_CODES.get(prefix, "")


def get_country_name(phone: str) -> str:
    """Получить название страны на русском по номеру телефона."""
    iso_code = get_country_iso(phone)
    return COUNTRY_NAMES.get(iso_code, "")


def get_language_preferences(phone: str) -> list:
    """
    Получить предполагаемые языковые предпочтения по номеру телефона.

    Returns:
        Список кодов языков в порядке приоритета
    """
    iso_code = get_country_iso(phone)
    return COUNTRY_LANGUAGE_PREFERENCES.get(iso_code, ['en'])


def suggest_communication_language(phone: str, detected_language: str = None) -> str:
    """
    Предложить язык для общения на основе телефона и детектированного языка.

    Args:
        phone: Номер телефона
        detected_language: Детектированный язык из сообщений

    Returns:
        Код языка для общения
    """
    # Если язык уже определён из сообщений - используем его
    if detected_language and detected_language != 'unknown':
        return detected_language

    # Иначе смотрим по номеру телефона
    preferences = get_language_preferences(phone)
    return preferences[0] if preferences else 'en'


def is_group_jid(jid: str) -> bool:
    """Определяет, является ли JID групповым чатом."""
    if not jid:
        return False
    return jid.endswith('@g.us')


def detect_language(texts: list) -> str:
    """
    Определяет язык по частотности слов в текстах.

    Returns: 'ru', 'en', 'ar' или 'unknown'
    """
    if not texts:
        return 'unknown'

    # Объединяем все тексты
    combined_text = ' '.join(str(t) for t in texts if t).lower()

    # Токенизация простая (по пробелам и знакам препинания)
    words = re.findall(r'[\w\u0400-\u04FF\u0600-\u06FF]+', combined_text)
    word_set = set(words)

    # Подсчёт совпадений
    ru_count = len(word_set & RUSSIAN_WORDS)
    en_count = len(word_set & ENGLISH_WORDS)
    ar_count = len(word_set & ARABIC_WORDS)

    # Дополнительно: проверка наличия кириллицы
    cyrillic_chars = len(re.findall(r'[\u0400-\u04FF]', combined_text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', combined_text))
    latin_chars = len(re.findall(r'[a-zA-Z]', combined_text))

    # Взвешенный подсчёт
    ru_score = ru_count * 10 + cyrillic_chars
    en_score = en_count * 10 + latin_chars
    ar_score = ar_count * 10 + arabic_chars

    if max(ru_score, en_score, ar_score) == 0:
        return 'unknown'

    if ru_score >= en_score and ru_score >= ar_score:
        return 'ru'
    elif ar_score >= en_score:
        return 'ar'
    else:
        return 'en'


def parse_datetime(date_str: str) -> datetime | None:
    """Парсит дату из разных форматов."""
    if not date_str:
        return None

    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%Y %H:%M',
        '%Y-%m-%d',
        '%d.%m.%Y',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def format_datetime(dt: datetime | None) -> str | None:
    """Форматирует datetime в ISO строку."""
    if dt:
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    return None


# ═══════════════════════════════════════════════════════════════
# ОСНОВНАЯ ЛОГИКА
# ═══════════════════════════════════════════════════════════════

class ContactAggregator:
    """Агрегатор контактов из JSONL сообщений."""

    def __init__(self):
        # Хранилище данных по JID
        self.contacts_data = defaultdict(lambda: {
            'jid': None,
            'names': Counter(),           # Частотность имён
            'display_names': Counter(),   # Частотность display_name
            'sources': set(),             # whatsapp / wa_business
            'chat_folders': set(),        # Папки чатов
            'first_message_date': None,
            'last_message_date': None,
            'total_messages': 0,
            'messages_sent': 0,           # is_from_me = True
            'messages_received': 0,       # is_from_me = False
            'texts': [],                  # Для детекции языка
            'is_group': False,
        })

    def process_message(self, msg: dict):
        """Обрабатывает одно сообщение из JSONL."""
        # Получаем JID из разных возможных полей
        jid = msg.get('jid') or msg.get('chat_jid') or msg.get('contact_jid')

        if not jid:
            return

        data = self.contacts_data[jid]
        data['jid'] = jid

        # Определяем тип (группа или личный)
        data['is_group'] = is_group_jid(jid)

        # Имена
        name = msg.get('name') or msg.get('chat_name') or msg.get('contact_name')
        if name:
            data['names'][name] += 1

        display_name = msg.get('display_name') or msg.get('partner_name')
        if display_name:
            data['display_names'][display_name] += 1

        # Источник (whatsapp / wa_business)
        source = msg.get('source', 'whatsapp')
        data['sources'].add(source)

        # Папка чата
        chat_folder = msg.get('chat_folder') or msg.get('folder')
        if chat_folder:
            data['chat_folders'].add(chat_folder)

        # Даты
        msg_date = msg.get('timestamp') or msg.get('date') or msg.get('message_date')
        dt = parse_datetime(msg_date)

        if dt:
            if data['first_message_date'] is None or dt < data['first_message_date']:
                data['first_message_date'] = dt
            if data['last_message_date'] is None or dt > data['last_message_date']:
                data['last_message_date'] = dt

        # Счётчики сообщений
        data['total_messages'] += 1

        is_from_me = msg.get('is_from_me', False)
        if is_from_me:
            data['messages_sent'] += 1
        else:
            data['messages_received'] += 1

        # Текст для детекции языка (ограничиваем количество)
        text = msg.get('text') or msg.get('message') or msg.get('content')
        if text and len(data['texts']) < 100:  # Ограничиваем для производительности
            data['texts'].append(text)

    def build_contacts(self) -> list:
        """Собирает финальный список контактов."""
        contacts = []

        for jid, data in self.contacts_data.items():
            # Выбираем самое частое имя
            name = data['names'].most_common(1)[0][0] if data['names'] else None
            display_name = data['display_names'].most_common(1)[0][0] if data['display_names'] else name

            # Извлекаем телефон
            phone = extract_phone_from_jid(jid)

            # Определяем код страны и связанные данные
            country_code = determine_country_code(phone)
            country_iso = get_country_iso(phone)
            country_name = get_country_name(phone)
            lang_preferences = get_language_preferences(phone)

            # Определяем источник
            sources = data['sources']
            if 'whatsapp' in sources and 'wa_business' in sources:
                source = 'both'
            elif 'wa_business' in sources:
                source = 'wa_business'
            else:
                source = 'whatsapp'

            # Детектим язык
            language = detect_language(data['texts'])

            # Выбираем первую папку чата (или None)
            chat_folder = list(data['chat_folders'])[0] if data['chat_folders'] else None

            contact = {
                'contact_id': str(uuid.uuid4()),
                'jid': jid,
                'phone': phone,
                'name': name or (phone if phone else jid.split('@')[0]),
                'display_name': display_name or name or (phone if phone else jid.split('@')[0]),
                'type': '',           # Заполняется classify_contacts.py
                'subtype': '',        # Заполняется classify_contacts.py
                'source': source,
                'is_group': data['is_group'],
                'first_message_date': format_datetime(data['first_message_date']),
                'last_message_date': format_datetime(data['last_message_date']),
                'total_messages': data['total_messages'],
                'messages_sent': data['messages_sent'],
                'messages_received': data['messages_received'],
                'language': language,
                'country_code': country_code,
                'country_iso': country_iso,
                'country_name': country_name,
                'language_preferences': lang_preferences,
                'suggested_language': suggest_communication_language(phone, language),
                'referral_from_id': None,  # Заполняется detect_referrals.py
                'tags': [],                # Заполняется classify_contacts.py
                'notes': '',
                'chat_folder': chat_folder,
            }

            contacts.append(contact)

        # Сортируем по дате последнего сообщения (сначала свежие)
        contacts.sort(
            key=lambda x: x['last_message_date'] or '',
            reverse=True
        )

        return contacts


def build_metadata(contacts: list) -> dict:
    """Создаёт метаданные о контактах."""
    by_source = Counter(c['source'] for c in contacts)
    by_type = Counter(c['type'] for c in contacts if c['type'])
    by_language = Counter(c['language'] for c in contacts if c['language'] != 'unknown')
    by_country = Counter(c['country_code'] for c in contacts if c['country_code'])

    groups = sum(1 for c in contacts if c['is_group'])
    personal = len(contacts) - groups

    return {
        'total': len(contacts),
        'groups': groups,
        'personal': personal,
        'by_source': dict(by_source),
        'by_type': dict(by_type),
        'by_language': dict(by_language),
        'by_country': dict(by_country),
        'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    }


def main():
    """Основная функция."""
    print("=" * 60)
    print("Извлечение контактов из all_messages.jsonl")
    print("=" * 60)

    # Проверяем/создаём директории
    ensure_directories()

    # Проверяем входной файл
    if not INPUT_FILE.exists():
        print(f"\n[ОШИБКА] Входной файл не найден: {INPUT_FILE}")
        print("\nСначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    print(f"\nВходной файл: {INPUT_FILE}")
    print(f"Выходной файл: {OUTPUT_FILE}")

    # Создаём агрегатор
    aggregator = ContactAggregator()

    # Читаем и обрабатываем JSONL
    print("\n[1/3] Чтение сообщений...")
    line_count = 0
    error_count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            if line_count % 100000 == 0:
                print(f"  Обработано строк: {line_count:,}")

            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
                aggregator.process_message(msg)
            except json.JSONDecodeError as e:
                error_count += 1
                if error_count <= 5:
                    print(f"  [Ошибка JSON] Строка {line_count}: {e}")

    print(f"  Всего строк: {line_count:,}")
    if error_count:
        print(f"  Ошибок парсинга: {error_count}")

    # Собираем контакты
    print("\n[2/3] Агрегация контактов...")
    contacts = aggregator.build_contacts()
    print(f"  Уникальных контактов: {len(contacts):,}")

    # Статистика
    groups = sum(1 for c in contacts if c['is_group'])
    personal = len(contacts) - groups
    print(f"  Групповых чатов: {groups:,}")
    print(f"  Личных чатов: {personal:,}")

    # Создаём метаданные
    metadata = build_metadata(contacts)

    # Формируем выходной JSON
    output_data = {
        'contacts': contacts,
        'metadata': metadata,
    }

    # Сохраняем
    print("\n[3/3] Сохранение результата...")
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  Сохранено: {OUTPUT_FILE}")

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Всего контактов: {metadata['total']:,}")
    print(f"  - Групповых: {metadata['groups']:,}")
    print(f"  - Личных: {metadata['personal']:,}")
    print(f"\nПо источникам:")
    for src, count in sorted(metadata['by_source'].items()):
        print(f"  - {src}: {count:,}")
    print(f"\nПо языкам:")
    for lang, count in sorted(metadata['by_language'].items(), key=lambda x: -x[1]):
        print(f"  - {lang}: {count:,}")
    print(f"\nТоп-10 стран по коду:")
    for code, count in sorted(metadata['by_country'].items(), key=lambda x: -x[1])[:10]:
        country_name = {
            'RU': 'Россия', 'AE': 'ОАЭ', 'US': 'США', 'UA': 'Украина',
            'BY': 'Беларусь', 'KZ': 'Казахстан', 'UZ': 'Узбекистан',
        }.get(COUNTRY_CODES.get(code, ''), code)
        print(f"  - {code} ({country_name}): {count:,}")

    print("\n" + "=" * 60)
    print("Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
