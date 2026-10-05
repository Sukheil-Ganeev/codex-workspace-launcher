#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мультиязычный парсинг сообщений WhatsApp.

Вход: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выход: D:/Downloads/Chats/_база/json/multilingual_analysis.json

Функции:
- Определение языка (русский, английский, арабский, транслит)
- Конвертация транслита в кириллицу
- Нормализация арабских цифр
- Определение языковых предпочтений клиента
- Отслеживание смены языка в диалогах
"""

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import RAW_DIR, JSON_DIR, ensure_directories

# Настройка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')


# ===================================================================
# КОНСТАНТЫ И СЛОВАРИ
# ===================================================================

INPUT_FILE = RAW_DIR / "all_messages.jsonl"
OUTPUT_FILE = JSON_DIR / "multilingual_analysis.json"

# Regex паттерны для определения языка
RUSSIAN_PATTERN = re.compile(r'[а-яА-ЯёЁ]+')
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]+')
ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F]+')

# RTL маркеры Unicode
RTL_MARKERS = ['\u200f', '\u200e', '\u202b', '\u202c']

# Арабские (восточно-арабские/индийские) цифры -> стандартные
ARABIC_NUMERALS = {
    '\u0660': '0', '\u0661': '1', '\u0662': '2', '\u0663': '3', '\u0664': '4',
    '\u0665': '5', '\u0666': '6', '\u0667': '7', '\u0668': '8', '\u0669': '9'
}

# Словарь транслита (латиница -> кириллица)
TRANSLIT_WORDS = {
    # Приветствия
    'privet': 'привет',
    'zdravstvuyte': 'здравствуйте',
    'poka': 'пока',
    'do svidaniya': 'до свидания',
    'spasibo': 'спасибо',
    'spasiba': 'спасибо',
    'pasibo': 'спасибо',
    'pozhaluysta': 'пожалуйста',
    'pojalusta': 'пожалуйста',
    'pazhalusta': 'пожалуйста',

    # Вопросы
    'skolko': 'сколько',
    'scolko': 'сколько',
    'stoit': 'стоит',
    'kogda': 'когда',
    'gde': 'где',
    'kak': 'как',
    'chto': 'что',
    'pochemu': 'почему',

    # Бронирование и заказ
    'zakazat': 'заказать',
    'zabronirovat': 'забронировать',
    'hochu': 'хочу',
    'xochu': 'хочу',
    'khochu': 'хочу',
    'nado': 'надо',
    'mozhno': 'можно',
    'nuzhno': 'нужно',

    # Туризм
    'ekskursiya': 'экскурсия',
    'tur': 'тур',
    'otel': 'отель',
    'bilet': 'билет',
    'transfer': 'трансфер',
    'safari': 'сафари',
    'mashina': 'машина',
    'avto': 'авто',

    # Время
    'segodnya': 'сегодня',
    'segodnja': 'сегодня',
    'sivodnya': 'сегодня',
    'zavtra': 'завтра',
    'zaftra': 'завтра',
    'vchera': 'вчера',
    'utrom': 'утром',
    'vecherom': 'вечером',

    # Числа словами
    'odin': 'один',
    'dva': 'два',
    'tri': 'три',
    'chetyre': 'четыре',
    'pyat': 'пять',

    # Разное
    'da': 'да',
    'net': 'нет',
    'ok': 'ок',
    'khorosho': 'хорошо',
    'xorosho': 'хорошо',
    'otlichno': 'отлично',
    'super': 'супер',
    'chelovek': 'человек',
    'vzroslyh': 'взрослых',
    'detey': 'детей',
}

# Паттерны транслита для детекции
TRANSLIT_DETECT_PATTERNS = [
    r'\bprivet\b', r'\bspasibo\b', r'\bskolko\b', r'\bstoit\b',
    r'\bkak\b', r'\bzakazat\b', r'\bhochu\b', r'\bmozhno\b',
    r'\bsegodnya\b', r'\bzavtra\b', r'\bekskursiya\b', r'\botel\b',
]

# Русские месяцы
RUSSIAN_MONTHS = {
    'января': 1, 'янв': 1,
    'февраля': 2, 'фев': 2,
    'марта': 3, 'мар': 3,
    'апреля': 4, 'апр': 4,
    'мая': 5,
    'июня': 6, 'июн': 6,
    'июля': 7, 'июл': 7,
    'августа': 8, 'авг': 8,
    'сентября': 9, 'сен': 9,
    'октября': 10, 'окт': 10,
    'ноября': 11, 'ноя': 11,
    'декабря': 12, 'дек': 12,
}

# Английские месяцы
ENGLISH_MONTHS = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}

# Арабские месяцы
ARABIC_MONTHS = {
    'يناير': 1,    # январь
    'فبراير': 2,   # февраль
    'مارس': 3,     # март
    'أبريل': 4,    # апрель
    'مايو': 5,     # май
    'يونيو': 6,    # июнь
    'يوليو': 7,    # июль
    'أغسطس': 8,    # август
    'سبتمبر': 9,   # сентябрь
    'أكتوبر': 10,  # октябрь
    'نوفمبر': 11,  # ноябрь
    'ديسمبر': 12,  # декабрь
}

# Арабские фразы для туризма (для справки)
ARABIC_TOURISM_PHRASES = {
    'مرحبا': 'marhaba / привет',
    'السلام عليكم': 'as-salamu alaykum / мир вам',
    'شكرا': 'shukran / спасибо',
    'كم السعر': 'kam al-si\'r / какая цена',
    'حجز': 'hajz / бронирование',
    'أريد': 'urid / я хочу',
    'درهم': 'dirham / дирхам',
}


# ===================================================================
# КЛАССЫ ДАННЫХ
# ===================================================================

@dataclass
class LanguageDetection:
    """Результат определения языка сообщения."""
    primary_language: str
    languages_found: List[str]
    has_translit: bool
    has_arabic_numerals: bool
    confidence: float
    char_counts: Dict[str, int]


@dataclass
class LanguageSwitch:
    """Событие смены языка в диалоге."""
    from_lang: str
    to_lang: str
    message_index: int
    trigger_text: str
    timestamp: Optional[str]


@dataclass
class ClientLanguageProfile:
    """Языковой профиль клиента."""
    jid: str
    name: str
    preferred_language: str
    response_language: str
    languages_used: Dict[str, int]
    translit_usage: bool
    translit_count: int
    mixed_messages_count: int
    language_switches: List[Dict]
    total_messages: int
    first_message_date: Optional[str]
    last_message_date: Optional[str]


# ===================================================================
# ФУНКЦИИ ОБРАБОТКИ
# ===================================================================

def normalize_rtl_text(text: str) -> str:
    """Удаляет RTL/LTR маркеры из текста."""
    for marker in RTL_MARKERS:
        text = text.replace(marker, '')
    return text


def normalize_arabic_numbers(text: str) -> str:
    """Конвертирует восточно-арабские цифры в стандартные."""
    for arabic, standard in ARABIC_NUMERALS.items():
        text = text.replace(arabic, standard)
    return text


def detect_translit(text: str) -> bool:
    """Определяет наличие транслита в тексте."""
    text_lower = text.lower()
    for pattern in TRANSLIT_DETECT_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def translit_to_cyrillic(text: str) -> str:
    """Конвертирует транслит в кириллицу."""
    result = text

    # Сортируем по длине (сначала длинные фразы)
    sorted_translit = sorted(TRANSLIT_WORDS.keys(), key=len, reverse=True)

    for translit in sorted_translit:
        cyrillic = TRANSLIT_WORDS[translit]
        # Замена с сохранением регистра первой буквы
        pattern = r'\b' + re.escape(translit) + r'\b'
        result = re.sub(pattern, cyrillic, result, flags=re.IGNORECASE)

    return result


def detect_languages(text: str) -> LanguageDetection:
    """
    Определяет все языки в сообщении.

    Returns:
        LanguageDetection с информацией о языках
    """
    if not text:
        return LanguageDetection(
            primary_language='unknown',
            languages_found=[],
            has_translit=False,
            has_arabic_numerals=False,
            confidence=0.0,
            char_counts={}
        )

    # Нормализуем текст
    text = normalize_rtl_text(text)

    languages = []
    char_counts = {}

    # Подсчёт символов кириллицы
    cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', text))
    char_counts['cyrillic'] = cyrillic_chars
    if cyrillic_chars > 0:
        languages.append('russian')

    # Подсчёт латинских символов
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    char_counts['latin'] = latin_chars
    if latin_chars > 0:
        languages.append('english')

    # Подсчёт арабских символов
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    char_counts['arabic'] = arabic_chars
    if arabic_chars > 0:
        languages.append('arabic')

    # Проверка на транслит
    has_translit = detect_translit(text)
    if has_translit and 'russian' not in languages:
        languages.append('translit_russian')

    # Проверка на арабские цифры
    arabic_numerals_count = sum(1 for c in text if c in ARABIC_NUMERALS)
    has_arabic_numerals = arabic_numerals_count > 0
    char_counts['arabic_numerals'] = arabic_numerals_count

    # Определение основного языка
    total_significant = cyrillic_chars + latin_chars + arabic_chars
    if total_significant == 0:
        primary_language = 'unknown'
        confidence = 0.0
    elif cyrillic_chars >= max(latin_chars, arabic_chars):
        primary_language = 'russian'
        confidence = cyrillic_chars / total_significant if total_significant > 0 else 0
    elif arabic_chars >= latin_chars:
        primary_language = 'arabic'
        confidence = arabic_chars / total_significant if total_significant > 0 else 0
    else:
        # Если латиница преобладает, проверяем транслит
        if has_translit:
            primary_language = 'translit_russian'
            confidence = 0.7  # Средняя уверенность для транслита
        else:
            primary_language = 'english'
            confidence = latin_chars / total_significant if total_significant > 0 else 0

    return LanguageDetection(
        primary_language=primary_language,
        languages_found=languages,
        has_translit=has_translit,
        has_arabic_numerals=has_arabic_numerals,
        confidence=confidence,
        char_counts=char_counts
    )


def detect_language_switches(messages: List[Dict]) -> List[LanguageSwitch]:
    """
    Находит моменты смены языка в диалоге.

    Args:
        messages: Список сообщений с 'text' и опционально 'timestamp'

    Returns:
        Список событий смены языка
    """
    switches = []
    prev_lang = None

    for i, msg in enumerate(messages):
        text = msg.get('text') or msg.get('message') or msg.get('content', '')
        if not text:
            continue

        detection = detect_languages(text)
        current_primary = detection.primary_language

        if current_primary == 'unknown':
            continue

        if prev_lang and current_primary != prev_lang:
            switches.append(LanguageSwitch(
                from_lang=prev_lang,
                to_lang=current_primary,
                message_index=i,
                trigger_text=text[:50] + '...' if len(text) > 50 else text,
                timestamp=msg.get('timestamp') or msg.get('date')
            ))

        prev_lang = current_primary

    return switches


def choose_response_language(
    client_language: str,
    last_message_language: str,
    operator_languages: List[str] = None
) -> str:
    """
    Выбирает язык для ответа клиенту.

    Args:
        client_language: Предпочтительный язык клиента
        last_message_language: Язык последнего сообщения
        operator_languages: Языки, которыми владеет оператор

    Returns:
        Рекомендованный язык для ответа
    """
    if operator_languages is None:
        operator_languages = ['russian', 'english']

    # Нормализуем транслит в русский
    if last_message_language == 'translit_russian':
        last_message_language = 'russian'
    if client_language == 'translit_russian':
        client_language = 'russian'

    # Приоритет: язык последнего сообщения
    if last_message_language in operator_languages:
        return last_message_language

    # Иначе: основной язык клиента
    if client_language in operator_languages:
        return client_language

    # Fallback: первый язык оператора
    return operator_languages[0]


# ===================================================================
# КЛАСС АНАЛИЗАТОРА
# ===================================================================

class MultilingualAnalyzer:
    """Анализатор мультиязычных сообщений."""

    def __init__(self):
        # Хранилище данных по JID
        self.contacts_data = defaultdict(lambda: {
            'jid': None,
            'name': None,
            'messages': [],  # Для анализа смен языка
            'languages_count': Counter(),
            'translit_count': 0,
            'mixed_count': 0,
            'first_date': None,
            'last_date': None,
            'total_messages': 0,
        })

        # Глобальная статистика
        self.global_stats = {
            'total_messages': 0,
            'by_language': Counter(),
            'translit_messages': 0,
            'mixed_messages': 0,
            'arabic_numerals_messages': 0,
        }

    def process_message(self, msg: Dict[str, Any]):
        """Обрабатывает одно сообщение."""
        jid = msg.get('jid') or msg.get('chat_jid') or msg.get('contact_jid')
        if not jid:
            return

        text = msg.get('text') or msg.get('message') or msg.get('content')
        if not text:
            return

        # Определяем язык
        detection = detect_languages(text)

        # Обновляем глобальную статистику
        self.global_stats['total_messages'] += 1
        self.global_stats['by_language'][detection.primary_language] += 1

        if detection.has_translit:
            self.global_stats['translit_messages'] += 1
        if len(detection.languages_found) > 1:
            self.global_stats['mixed_messages'] += 1
        if detection.has_arabic_numerals:
            self.global_stats['arabic_numerals_messages'] += 1

        # Обновляем данные контакта
        data = self.contacts_data[jid]
        data['jid'] = jid

        # Имя
        name = msg.get('name') or msg.get('chat_name') or msg.get('contact_name')
        if name and not data['name']:
            data['name'] = name

        # Языки
        data['languages_count'][detection.primary_language] += 1
        data['total_messages'] += 1

        if detection.has_translit:
            data['translit_count'] += 1
        if len(detection.languages_found) > 1:
            data['mixed_count'] += 1

        # Даты
        msg_date = msg.get('timestamp') or msg.get('date')
        if msg_date:
            if data['first_date'] is None or msg_date < data['first_date']:
                data['first_date'] = msg_date
            if data['last_date'] is None or msg_date > data['last_date']:
                data['last_date'] = msg_date

        # Сохраняем сообщение для анализа смен языка (ограничиваем для памяти)
        if len(data['messages']) < 500:
            data['messages'].append({
                'text': text,
                'timestamp': msg_date,
                'language': detection.primary_language,
            })

    def build_profiles(self) -> List[Dict]:
        """Создаёт языковые профили контактов."""
        profiles = []

        for jid, data in self.contacts_data.items():
            if data['total_messages'] == 0:
                continue

            # Определяем предпочтительный язык
            if data['languages_count']:
                preferred = data['languages_count'].most_common(1)[0][0]
            else:
                preferred = 'unknown'

            # Анализируем смены языка
            switches = detect_language_switches(data['messages'])

            # Определяем язык для ответа
            last_msg_lang = data['messages'][-1]['language'] if data['messages'] else preferred
            response_lang = choose_response_language(preferred, last_msg_lang)

            profile = ClientLanguageProfile(
                jid=jid,
                name=data['name'] or jid.split('@')[0],
                preferred_language=preferred,
                response_language=response_lang,
                languages_used=dict(data['languages_count']),
                translit_usage=data['translit_count'] > 0,
                translit_count=data['translit_count'],
                mixed_messages_count=data['mixed_count'],
                language_switches=[asdict(s) for s in switches],
                total_messages=data['total_messages'],
                first_message_date=data['first_date'],
                last_message_date=data['last_date'],
            )
            profiles.append(asdict(profile))

        # Сортируем по количеству сообщений
        profiles.sort(key=lambda x: x['total_messages'], reverse=True)

        return profiles

    def build_metadata(self, profiles: List[Dict]) -> Dict:
        """Создаёт метаданные анализа."""
        by_preferred = Counter(p['preferred_language'] for p in profiles)
        by_response = Counter(p['response_language'] for p in profiles)
        with_translit = sum(1 for p in profiles if p['translit_usage'])
        with_switches = sum(1 for p in profiles if p['language_switches'])

        return {
            'total_contacts': len(profiles),
            'total_messages_analyzed': self.global_stats['total_messages'],
            'messages_by_language': dict(self.global_stats['by_language']),
            'translit_messages_count': self.global_stats['translit_messages'],
            'mixed_messages_count': self.global_stats['mixed_messages'],
            'arabic_numerals_messages_count': self.global_stats['arabic_numerals_messages'],
            'contacts_by_preferred_language': dict(by_preferred),
            'contacts_by_response_language': dict(by_response),
            'contacts_with_translit': with_translit,
            'contacts_with_language_switches': with_switches,
            'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        }


# ===================================================================
# УТИЛИТЫ
# ===================================================================

def process_text_with_normalization(text: str) -> Dict[str, str]:
    """
    Обрабатывает текст с нормализацией.

    Returns:
        Словарь с оригиналом, нормализованным и конвертированным текстом
    """
    original = text

    # Нормализуем RTL
    normalized = normalize_rtl_text(text)

    # Нормализуем арабские цифры
    normalized = normalize_arabic_numbers(normalized)

    # Конвертируем транслит
    converted = translit_to_cyrillic(normalized)

    return {
        'original': original,
        'normalized': normalized,
        'converted': converted if converted != normalized else None,
    }


# ===================================================================
# MAIN
# ===================================================================

def main():
    """Основная функция."""
    print("=" * 60)
    print("Мультиязычный анализ сообщений WhatsApp")
    print("=" * 60)

    # Создаём директории
    ensure_directories()

    # Проверяем входной файл
    if not INPUT_FILE.exists():
        print(f"\n[ОШИБКА] Входной файл не найден: {INPUT_FILE}")
        print("\nСначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    print(f"\nВходной файл: {INPUT_FILE}")
    print(f"Выходной файл: {OUTPUT_FILE}")

    # Создаём анализатор
    analyzer = MultilingualAnalyzer()

    # Читаем и обрабатываем JSONL
    print("\n[1/3] Анализ языков в сообщениях...")
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
                analyzer.process_message(msg)
            except json.JSONDecodeError as e:
                error_count += 1
                if error_count <= 5:
                    print(f"  [Ошибка JSON] Строка {line_count}: {e}")

    print(f"  Всего строк: {line_count:,}")
    if error_count:
        print(f"  Ошибок парсинга: {error_count}")

    # Создаём профили
    print("\n[2/3] Создание языковых профилей...")
    profiles = analyzer.build_profiles()
    print(f"  Профилей создано: {len(profiles):,}")

    # Метаданные
    metadata = analyzer.build_metadata(profiles)

    # Формируем выходные данные
    output_data = {
        'language_profiles': profiles,
        'metadata': metadata,
        'dictionaries': {
            'translit_words_count': len(TRANSLIT_WORDS),
            'russian_months_count': len(RUSSIAN_MONTHS),
            'english_months_count': len(ENGLISH_MONTHS),
            'arabic_months_count': len(ARABIC_MONTHS),
            'arabic_tourism_phrases_count': len(ARABIC_TOURISM_PHRASES),
        }
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
    print(f"Всего сообщений проанализировано: {metadata['total_messages_analyzed']:,}")
    print(f"Контактов с профилями: {metadata['total_contacts']:,}")
    print(f"\nСообщений по языкам:")
    for lang, count in sorted(metadata['messages_by_language'].items(), key=lambda x: -x[1]):
        percent = count / metadata['total_messages_analyzed'] * 100 if metadata['total_messages_analyzed'] > 0 else 0
        print(f"  - {lang}: {count:,} ({percent:.1f}%)")
    print(f"\nСообщений с транслитом: {metadata['translit_messages_count']:,}")
    print(f"Смешанных сообщений: {metadata['mixed_messages_count']:,}")
    print(f"С арабскими цифрами: {metadata['arabic_numerals_messages_count']:,}")
    print(f"\nКонтактов по предпочтительному языку:")
    for lang, count in sorted(metadata['contacts_by_preferred_language'].items(), key=lambda x: -x[1]):
        print(f"  - {lang}: {count:,}")
    print(f"\nКонтактов с транслитом: {metadata['contacts_with_translit']:,}")
    print(f"Контактов со сменой языка: {metadata['contacts_with_language_switches']:,}")

    print("\n" + "=" * 60)
    print("Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
