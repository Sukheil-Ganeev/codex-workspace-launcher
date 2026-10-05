#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Извлечение дат поездок клиентов из чатов.

Паттерны поиска:
- "прилетаем/прилетаю [дата]"
- "улетаем/улетаю [дата]"
- "будем в Дубае с [дата] по [дата]"
- "приезжаем [дата]"
- "в ОАЭ с [дата]"

Входной файл: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходной файл: D:/Downloads/Chats/_база/json/travel_dates.json
"""

import json
import re
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import JSON_DIR, RAW_DIR, ensure_directories
except ImportError:
    # Запасные пути если конфиг недоступен
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# СЛОВАРИ МЕСЯЦЕВ
# ═══════════════════════════════════════════════════════════════

MONTHS_RU = {
    'январ': 1, 'феврал': 2, 'март': 3, 'апрел': 4,
    'ма': 5, 'июн': 6, 'июл': 7, 'август': 8,
    'сентябр': 9, 'октябр': 10, 'ноябр': 11, 'декабр': 12,
    # Полные формы
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
    'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
    'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
}

MONTHS_EN = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ДАТ
# ═══════════════════════════════════════════════════════════════

# Числовые даты
DATE_NUMERIC_PATTERNS = [
    # DD.MM.YYYY или DD.MM.YY
    r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})',
    # DD.MM (без года)
    r'(\d{1,2})[./](\d{1,2})(?!\d)',
]

# Текстовые даты (русские)
DATE_TEXT_RU_PATTERN = r'(\d{1,2})\s*(?:-?(?:го|ого|ое|е))?\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])'

# Текстовые даты (английские)
DATE_TEXT_EN_PATTERN = r'(\d{1,2})(?:st|nd|rd|th)?\s*(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)'

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ПРИЛЁТА/ОТЛЁТА
# ═══════════════════════════════════════════════════════════════

ARRIVAL_PATTERNS = [
    # Прилетаем/прилетаю + дата
    r'прилета[еюи][мт]?\s+(.{5,40})',
    r'прилёт\s+(.{5,40})',
    r'приезжа[еюи][мт]?\s+(.{5,40})',
    r'приед[у|ем|ут]\s+(.{5,40})',
    r'будем?\s+(?:в\s+)?(?:дубае?|оаэ|эмират[ыах]?)\s+(?:с\s+)?(.{5,40})',
    r'в\s+(?:дубае?|оаэ|эмират[ыах]?)\s+(?:с\s+)?(.{5,40})',
    r'прибыва[еюи][мт]?\s+(.{5,40})',
    r'заселя[еюи][мт]?ся\s+(.{5,40})',
    r'заезд\s+(.{5,40})',
    r'въезд\s+(.{5,40})',
    r'arrival\s+(.{5,40})',
    r'check[- ]?in\s+(.{5,40})',
]

DEPARTURE_PATTERNS = [
    # Улетаем/улетаю + дата
    r'улета[еюи][мт]?\s+(.{5,40})',
    r'улёт\s+(.{5,40})',
    r'уезжа[еюи][мт]?\s+(.{5,40})',
    r'выезжа[еюи][мт]?\s+(.{5,40})',
    r'уед[у|ем|ут]\s+(.{5,40})',
    r'(?:по|до)\s+(.{5,40})',  # "будем с 15 по 20"
    r'выселя[еюи][мт]?ся\s+(.{5,40})',
    r'выезд\s+(.{5,40})',
    r'departure\s+(.{5,40})',
    r'check[- ]?out\s+(.{5,40})',
]

# Диапазон дат
DATE_RANGE_PATTERNS = [
    # "с 15 по 20 января"
    r'с\s+(\d{1,2})\s*(?:-?(?:го|ого))?\s*по\s+(\d{1,2})\s*(?:-?(?:го|ого))?\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])',
    # "с 15.01 по 20.01"
    r'с\s+(\d{1,2})[./](\d{1,2})(?:[./]\d{2,4})?\s*(?:по|до|-)\s*(\d{1,2})[./](\d{1,2})(?:[./]\d{2,4})?',
    # "15-20 января"
    r'(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])',
    # "15 января - 20 января"
    r'(\d{1,2})\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])\s*[-–]\s*(\d{1,2})\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])',
]

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ КОЛИЧЕСТВА ЧЕЛОВЕК
# ═══════════════════════════════════════════════════════════════

PAX_PATTERNS = [
    # "нас 4 человека"
    r'(?:нас|всего)\s+(\d+)\s*(?:человек[аи]?|чел\.?|персон[ыа]?|взросл|гост[ейя])',
    # "4 человека", "5 гостей"
    r'(\d+)\s*(?:человек[аи]?|чел\.?|персон[ыа]?|взросл|гост[ейя])',
    # "для 4х", "на 4х"
    r'(?:для|на)\s+(\d+)[хx]?(?:\s|$)',
    # "2+2", "2 взрослых + 2 детей"
    r'(\d+)\s*\+\s*(\d+)',
    # "семья из 4 человек"
    r'(?:семья|группа|компания)\s+(?:из\s+)?(\d+)',
    # "pax 4", "4 pax"
    r'(?:pax|PAX)\s*[:=]?\s*(\d+)|(\d+)\s*(?:pax|PAX)',
    # Словесные числительные
    r'(двое|трое|четверо|пятеро|шестеро|семеро|восьмеро|девятеро|десятеро)',
]

PAX_WORDS = {
    'двое': 2, 'трое': 3, 'четверо': 4, 'пятеро': 5,
    'шестеро': 6, 'семеро': 7, 'восьмеро': 8, 'девятеро': 9, 'десятеро': 10,
}

# Детализация PAX
PAX_DETAILS_PATTERNS = [
    # "2 взрослых, 2 детей"
    r'(\d+)\s*взросл[ыхой]*\s*[,и+]\s*(\d+)\s*(?:дет[ейи]|ребён[окка])',
    # "2 взрослых и 1 ребёнок"
    r'(\d+)\s*взросл[ыхой]*\s*(?:и\s+)?(\d+)\s*(?:дет[ейи]|ребён[окка])',
    # "2 adults, 2 kids"
    r'(\d+)\s*adult[s]?\s*[,+and]+\s*(\d+)\s*(?:kid[s]?|child(?:ren)?)',
]

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ОТЕЛЕЙ
# ═══════════════════════════════════════════════════════════════

HOTEL_PATTERNS = [
    # "отель JW Marriott"
    r'(?:отел[ьие]|hotel|гостиниц[аеы]|живём? в|остановились? в|проживани[ея] в)\s*[:\-]?\s*(.{3,50})',
    # "JW Marriott", "Atlantis", "Burj" - известные отели
    r'\b((?:JW\s+)?Marriott|Atlantis|Burj\s+(?:Al\s+Arab|Khalifa)|Jumeirah|Hilton|Sheraton|Sofitel|Fairmont|Ritz[- ]Carlton|Four\s+Seasons|Waldorf|W\s+Hotel|Address|Armani|Palazzo|Kempinski|Anantara|St\.?\s*Regis|Mandarin|Conrad|Intercontinental|Hyatt|Radisson|Mövenpick|Movenpick|Rixos|One&Only|Caesars|Wyndham)\b.{0,30}',
    # "в Марина" (район как ориентир)
    r'(?:в|около|рядом с)\s+(Dubai\s+Marina|JBR|Palm\s+Jumeirah|Downtown|Business\s+Bay|Creek|Deira|Bur\s+Dubai)',
]

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ПАРСИНГА ДАТ
# ═══════════════════════════════════════════════════════════════

def get_month_number(month_str: str) -> Optional[int]:
    """Получить номер месяца по названию."""
    month_lower = month_str.lower().strip()

    # Русские месяцы
    for prefix, num in MONTHS_RU.items():
        if month_lower.startswith(prefix) or prefix.startswith(month_lower[:3]):
            return num

    # Английские месяцы
    for name, num in MONTHS_EN.items():
        if month_lower.startswith(name) or name.startswith(month_lower):
            return num

    return None


def parse_date_from_text(text: str, reference_date: Optional[datetime] = None) -> Optional[str]:
    """
    Извлечь дату из текстового фрагмента.

    Returns:
        Дата в формате YYYY-MM-DD или None
    """
    if not text:
        return None

    text_lower = text.lower().strip()

    if reference_date is None:
        reference_date = datetime.now()

    ref_year = reference_date.year
    ref_month = reference_date.month

    # 1. Попробовать числовой формат DD.MM.YYYY или DD.MM.YY
    for pattern in DATE_NUMERIC_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            day = int(groups[0])
            month = int(groups[1])

            if len(groups) >= 3 and groups[2]:
                year = int(groups[2])
                if year < 100:
                    year = 2000 + year
            else:
                # Без года - определяем по контексту
                year = ref_year
                # Если месяц уже прошёл в этом году, возможно имеется в виду следующий год
                if month < ref_month:
                    year += 1

            # Валидация
            if 1 <= day <= 31 and 1 <= month <= 12:
                try:
                    dt = datetime(year, month, day)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    pass

    # 2. Попробовать текстовый формат "15 января"
    match = re.search(DATE_TEXT_RU_PATTERN, text_lower, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month = get_month_number(match.group(2))

        if month and 1 <= day <= 31:
            year = ref_year
            if month < ref_month:
                year += 1
            try:
                dt = datetime(year, month, day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

    # 3. Попробовать английский формат "January 15"
    match = re.search(DATE_TEXT_EN_PATTERN, text_lower, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month = get_month_number(match.group(2))

        if month and 1 <= day <= 31:
            year = ref_year
            if month < ref_month:
                year += 1
            try:
                dt = datetime(year, month, day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

    # 4. Обратный порядок для английского "January 15"
    match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})', text_lower, re.IGNORECASE)
    if match:
        month = get_month_number(match.group(1))
        day = int(match.group(2))

        if month and 1 <= day <= 31:
            year = ref_year
            if month < ref_month:
                year += 1
            try:
                dt = datetime(year, month, day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

    return None


def parse_date_range(text: str, reference_date: Optional[datetime] = None) -> tuple[Optional[str], Optional[str]]:
    """
    Извлечь диапазон дат из текста.

    Returns:
        (arrival_date, departure_date) в формате YYYY-MM-DD
    """
    if not text:
        return None, None

    text_lower = text.lower().strip()

    if reference_date is None:
        reference_date = datetime.now()

    ref_year = reference_date.year
    ref_month = reference_date.month

    # Паттерн 1: "с 15 по 20 января"
    match = re.search(DATE_RANGE_PATTERNS[0], text_lower, re.IGNORECASE)
    if match:
        day1 = int(match.group(1))
        day2 = int(match.group(2))
        month = get_month_number(match.group(3))

        if month and 1 <= day1 <= 31 and 1 <= day2 <= 31:
            year = ref_year
            if month < ref_month:
                year += 1
            try:
                dt1 = datetime(year, month, day1)
                dt2 = datetime(year, month, day2)
                return dt1.strftime('%Y-%m-%d'), dt2.strftime('%Y-%m-%d')
            except ValueError:
                pass

    # Паттерн 2: "с 15.01 по 20.01"
    match = re.search(DATE_RANGE_PATTERNS[1], text_lower)
    if match:
        day1 = int(match.group(1))
        month1 = int(match.group(2))
        day2 = int(match.group(3))
        month2 = int(match.group(4))

        if 1 <= day1 <= 31 and 1 <= month1 <= 12 and 1 <= day2 <= 31 and 1 <= month2 <= 12:
            year1 = ref_year
            year2 = ref_year
            if month1 < ref_month:
                year1 += 1
            if month2 < ref_month:
                year2 += 1
            try:
                dt1 = datetime(year1, month1, day1)
                dt2 = datetime(year2, month2, day2)
                return dt1.strftime('%Y-%m-%d'), dt2.strftime('%Y-%m-%d')
            except ValueError:
                pass

    # Паттерн 3: "15-20 января"
    match = re.search(DATE_RANGE_PATTERNS[2], text_lower, re.IGNORECASE)
    if match:
        day1 = int(match.group(1))
        day2 = int(match.group(2))
        month = get_month_number(match.group(3))

        if month and 1 <= day1 <= 31 and 1 <= day2 <= 31:
            year = ref_year
            if month < ref_month:
                year += 1
            try:
                dt1 = datetime(year, month, day1)
                dt2 = datetime(year, month, day2)
                return dt1.strftime('%Y-%m-%d'), dt2.strftime('%Y-%m-%d')
            except ValueError:
                pass

    # Паттерн 4: "15 января - 20 февраля"
    match = re.search(DATE_RANGE_PATTERNS[3], text_lower, re.IGNORECASE)
    if match:
        day1 = int(match.group(1))
        month1 = get_month_number(match.group(2))
        day2 = int(match.group(3))
        month2 = get_month_number(match.group(4))

        if month1 and month2:
            year1 = ref_year
            year2 = ref_year
            if month1 < ref_month:
                year1 += 1
            if month2 < ref_month or (month2 < month1 and month1 >= ref_month):
                year2 += 1
            try:
                dt1 = datetime(year1, month1, day1)
                dt2 = datetime(year2, month2, day2)
                return dt1.strftime('%Y-%m-%d'), dt2.strftime('%Y-%m-%d')
            except ValueError:
                pass

    return None, None


def extract_pax(text: str) -> tuple[Optional[int], Optional[str]]:
    """
    Извлечь количество человек и детали.

    Returns:
        (pax, pax_details)
    """
    if not text:
        return None, None

    text_lower = text.lower()
    pax = None
    pax_details = None

    # Детализация (взрослые + дети)
    for pattern in PAX_DETAILS_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            adults = int(match.group(1))
            children = int(match.group(2))
            pax = adults + children

            # Формирование описания
            adult_word = 'взрослый' if adults == 1 else 'взрослых'
            if children == 1:
                child_word = 'ребёнок'
            elif children < 5:
                child_word = 'ребёнка'
            else:
                child_word = 'детей'

            pax_details = f"{adults} {adult_word}, {children} {child_word}"
            return pax, pax_details

    # Общее количество
    for pattern in PAX_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            groups = match.groups()
            for g in groups:
                if g:
                    if g in PAX_WORDS:
                        pax = PAX_WORDS[g]
                    else:
                        try:
                            pax = int(g)
                        except ValueError:
                            continue
                    if pax and 1 <= pax <= 50:  # Разумные пределы
                        return pax, None

    # Формат "2+2"
    match = re.search(r'(\d+)\s*\+\s*(\d+)', text)
    if match:
        pax = int(match.group(1)) + int(match.group(2))
        pax_details = f"{match.group(1)} + {match.group(2)}"
        return pax, pax_details

    return pax, pax_details


def extract_hotel(text: str) -> Optional[str]:
    """Извлечь название отеля из текста."""
    if not text:
        return None

    for pattern in HOTEL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            hotel = match.group(1).strip()
            # Очистка от мусора
            hotel = re.sub(r'[,.]$', '', hotel)
            hotel = re.sub(r'\s+', ' ', hotel)
            if len(hotel) > 2:
                return hotel

    return None


# ═══════════════════════════════════════════════════════════════
# ОСНОВНОЙ ЭКСТРАКТОР
# ═══════════════════════════════════════════════════════════════

def extract_travel_info_from_message(msg: dict) -> Optional[dict]:
    """
    Извлечь информацию о поездке из сообщения.

    Returns:
        Словарь с информацией о поездке или None
    """
    text = msg.get('text')
    if not text:
        return None

    text_lower = text.lower()

    # Быстрая проверка - есть ли ключевые слова
    keywords = [
        'прилет', 'прилёт', 'улет', 'улёт', 'приезж', 'уезж',
        'будем в', 'в дубае', 'в оаэ', 'в эмират',
        'заезд', 'выезд', 'заселя', 'выселя',
        'arrival', 'departure', 'check-in', 'check-out', 'checkin', 'checkout'
    ]

    if not any(kw in text_lower for kw in keywords):
        return None

    # Парсинг даты сообщения для контекста
    msg_datetime = msg.get('datetime')
    if msg_datetime:
        try:
            reference_date = datetime.fromisoformat(msg_datetime.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            reference_date = datetime.now()
    else:
        reference_date = datetime.now()

    arrival_date = None
    departure_date = None

    # 1. Сначала ищем диапазон дат
    range_arrival, range_departure = parse_date_range(text, reference_date)
    if range_arrival and range_departure:
        arrival_date = range_arrival
        departure_date = range_departure
    else:
        # 2. Ищем отдельные даты прилёта/отлёта

        # Прилёт
        for pattern in ARRIVAL_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                date_fragment = match.group(1)
                parsed = parse_date_from_text(date_fragment, reference_date)
                if parsed:
                    arrival_date = parsed
                    break

        # Отлёт
        for pattern in DEPARTURE_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                date_fragment = match.group(1)
                parsed = parse_date_from_text(date_fragment, reference_date)
                if parsed:
                    departure_date = parsed
                    break

    # Если не нашли ни одной даты - пропускаем
    if not arrival_date and not departure_date:
        return None

    # Извлекаем дополнительную информацию
    pax, pax_details = extract_pax(text)
    hotel = extract_hotel(text)

    # Вычисляем длительность
    duration_days = None
    if arrival_date and departure_date:
        try:
            dt1 = datetime.strptime(arrival_date, '%Y-%m-%d')
            dt2 = datetime.strptime(departure_date, '%Y-%m-%d')
            duration_days = (dt2 - dt1).days
            if duration_days < 0:
                duration_days = None  # Некорректный диапазон
        except ValueError:
            pass

    return {
        'record_id': str(uuid.uuid4()),
        'contact_id': None,  # Будет заполнено позже если есть маппинг
        'jid': msg.get('jid'),
        'chat_name': msg.get('chat_name'),
        'message_date': msg.get('datetime'),
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'duration_days': duration_days,
        'pax': pax,
        'pax_details': pax_details,
        'hotel': hotel,
        'original_text': text[:500] if len(text) > 500 else text,
        'source': msg.get('source'),
    }


def build_calendar(travel_dates: list) -> dict:
    """
    Построить календарь загрузки по месяцам.

    Returns:
        Словарь с статистикой по месяцам
    """
    calendar = defaultdict(lambda: {
        'arrivals': 0,
        'departures': 0,
        'arrival_days': defaultdict(int),
        'departure_days': defaultdict(int),
    })

    for record in travel_dates:
        arrival = record.get('arrival_date')
        departure = record.get('departure_date')

        if arrival:
            try:
                dt = datetime.strptime(arrival, '%Y-%m-%d')
                month_key = dt.strftime('%Y-%m')
                calendar[month_key]['arrivals'] += 1
                calendar[month_key]['arrival_days'][arrival] += 1
            except ValueError:
                pass

        if departure:
            try:
                dt = datetime.strptime(departure, '%Y-%m-%d')
                month_key = dt.strftime('%Y-%m')
                calendar[month_key]['departures'] += 1
                calendar[month_key]['departure_days'][departure] += 1
            except ValueError:
                pass

    # Определяем пиковые дни
    result = {}
    for month, data in calendar.items():
        # Топ-5 дней по прибытиям
        all_days = {}
        for day, count in data['arrival_days'].items():
            all_days[day] = all_days.get(day, 0) + count
        for day, count in data['departure_days'].items():
            all_days[day] = all_days.get(day, 0) + count

        peak_days = sorted(all_days.items(), key=lambda x: x[1], reverse=True)[:5]

        result[month] = {
            'arrivals': data['arrivals'],
            'departures': data['departures'],
            'peak_days': [day for day, _ in peak_days],
        }

    return result


def main():
    """Основная функция."""
    print("=" * 60)
    print("ИЗВЛЕЧЕНИЕ ДАТ ПОЕЗДОК ИЗ ЧАТОВ")
    print("=" * 60)

    # Создать директории
    ensure_directories()

    # Входной файл
    input_file = RAW_DIR / "all_messages.jsonl"
    output_file = JSON_DIR / "travel_dates.json"

    print(f"\nВходной файл: {input_file}")
    print(f"Выходной файл: {output_file}")

    if not input_file.exists():
        print(f"\n[ОШИБКА] Файл не найден: {input_file}")
        print("Сначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    print("\nЧитаю сообщения...")

    travel_dates = []
    total_messages = 0
    processed = 0

    start_time = datetime.now()

    # Читаем и обрабатываем сообщения
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            total_messages += 1

            try:
                msg = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            # Извлекаем информацию о поездке
            travel_info = extract_travel_info_from_message(msg)
            if travel_info:
                travel_dates.append(travel_info)
                processed += 1

            # Прогресс каждые 100,000 сообщений
            if total_messages % 100000 == 0:
                print(f"  Обработано: {total_messages:,} сообщений, найдено: {processed:,} дат")

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\nОбработано сообщений: {total_messages:,}")
    print(f"Найдено записей о поездках: {len(travel_dates):,}")
    print(f"Время: {elapsed:.1f} сек")

    # Удаление дубликатов (по jid + arrival_date + departure_date)
    seen = set()
    unique_dates = []
    for record in travel_dates:
        key = (
            record.get('jid'),
            record.get('arrival_date'),
            record.get('departure_date'),
        )
        if key not in seen:
            seen.add(key)
            unique_dates.append(record)

    print(f"После удаления дубликатов: {len(unique_dates):,}")

    # Сортировка по дате прилёта
    unique_dates.sort(
        key=lambda x: x.get('arrival_date') or x.get('departure_date') or '9999-99-99'
    )

    # Строим календарь
    calendar = build_calendar(unique_dates)

    # Формируем итоговый JSON
    result = {
        'generated_at': datetime.now().isoformat(),
        'total_messages_scanned': total_messages,
        'total_records': len(unique_dates),
        'travel_dates': unique_dates,
        'calendar': dict(sorted(calendar.items())),
    }

    # Статистика
    with_arrival = sum(1 for r in unique_dates if r.get('arrival_date'))
    with_departure = sum(1 for r in unique_dates if r.get('departure_date'))
    with_both = sum(1 for r in unique_dates if r.get('arrival_date') and r.get('departure_date'))
    with_pax = sum(1 for r in unique_dates if r.get('pax'))
    with_hotel = sum(1 for r in unique_dates if r.get('hotel'))

    result['statistics'] = {
        'with_arrival_date': with_arrival,
        'with_departure_date': with_departure,
        'with_both_dates': with_both,
        'with_pax_info': with_pax,
        'with_hotel_info': with_hotel,
    }

    # Сохраняем
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"Всего записей: {len(unique_dates):,}")
    print(f"  - С датой прилёта: {with_arrival:,}")
    print(f"  - С датой отлёта: {with_departure:,}")
    print(f"  - С обеими датами: {with_both:,}")
    print(f"  - С количеством человек: {with_pax:,}")
    print(f"  - С информацией об отеле: {with_hotel:,}")
    print(f"\nКалендарь:")
    for month, data in sorted(calendar.items())[-6:]:  # Последние 6 месяцев
        print(f"  {month}: {data['arrivals']} прибытий, {data['departures']} отъездов")
    print(f"\nСохранено: {output_file}")
    print(f"Размер: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
