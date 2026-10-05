#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Универсальный извлекатель дат и времени из чатов.

Возможности:
- Парсинг различных форматов дат (числовые, текстовые, относительные)
- Относительные даты: "завтра", "послезавтра", "через неделю", "next Monday"
- Определение контекста: дата тура, прилёт/вылет, дедлайн оплаты
- Временные зоны (Dubai UTC+4, Moscow UTC+3, Almaty UTC+5)
- Экспорт: iCal (.ics), JSON

Зависимости:
    pip install dateparser parsedatetime pytz icalendar

Входной файл: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходные файлы:
    - D:/Downloads/Chats/_база/json/datetime_extracted.json
    - D:/Downloads/Chats/_база/export/calendar_events.ics
"""

import json
import re
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

sys.stdout.reconfigure(encoding='utf-8')

# Опциональные импорты
try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False
    print("[!] dateparser не установлен. pip install dateparser")

try:
    import parsedatetime
    PARSEDATETIME_AVAILABLE = True
except ImportError:
    PARSEDATETIME_AVAILABLE = False
    print("[!] parsedatetime не установлен. pip install parsedatetime")

try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    print("[!] pytz не установлен. pip install pytz")

try:
    from icalendar import Calendar, Event as ICalEvent
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False
    print("[!] icalendar не установлен. pip install icalendar")

# Импорт конфигурации
try:
    from config import JSON_DIR, RAW_DIR, EXPORT_DIR, ensure_directories
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    EXPORT_DIR = Path("D:/Downloads/Chats/_база/export")
    def ensure_directories():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ И НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

class DateContext(Enum):
    """Тип контекста даты."""
    ARRIVAL = "arrival"              # Прилёт/приезд
    DEPARTURE = "departure"          # Вылет/отъезд
    TOUR_DATE = "tour_date"          # Дата тура/экскурсии
    BOOKING = "booking"              # Бронирование
    PAYMENT_DEADLINE = "payment"     # Дедлайн оплаты
    TRANSFER = "transfer"            # Трансфер
    MEETING = "meeting"              # Встреча
    REMINDER = "reminder"            # Напоминание
    UNKNOWN = "unknown"              # Неизвестно


@dataclass
class ExtractedDateTime:
    """Извлечённая дата/время."""
    record_id: str
    datetime_value: str              # ISO формат
    date_only: str                   # YYYY-MM-DD
    time_only: Optional[str]         # HH:MM
    context: str                     # Тип контекста
    confidence: float                # Уверенность 0-1
    original_text: str               # Исходный фрагмент
    timezone: str                    # Временная зона
    # Метаданные сообщения
    jid: Optional[str] = None
    chat_name: Optional[str] = None
    message_date: Optional[str] = None
    source: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# ВРЕМЕННЫЕ ЗОНЫ
# ═══════════════════════════════════════════════════════════════

TIMEZONES = {
    'dubai': 'Asia/Dubai',           # UTC+4
    'uae': 'Asia/Dubai',
    'moscow': 'Europe/Moscow',       # UTC+3
    'msk': 'Europe/Moscow',
    'almaty': 'Asia/Almaty',         # UTC+5
    'astana': 'Asia/Almaty',
    'tashkent': 'Asia/Tashkent',     # UTC+5
    'baku': 'Asia/Baku',             # UTC+4
    'london': 'Europe/London',       # UTC+0/+1
    'utc': 'UTC',
}

DEFAULT_TIMEZONE = 'Asia/Dubai'  # UTC+4


def get_timezone(tz_name: str = None):
    """Получить объект временной зоны."""
    if not PYTZ_AVAILABLE:
        return None

    if tz_name:
        tz_lower = tz_name.lower().strip()
        tz_id = TIMEZONES.get(tz_lower, tz_name)
    else:
        tz_id = DEFAULT_TIMEZONE

    try:
        return pytz.timezone(tz_id)
    except:
        return pytz.timezone(DEFAULT_TIMEZONE)


# ═══════════════════════════════════════════════════════════════
# СЛОВАРИ
# ═══════════════════════════════════════════════════════════════

# Месяцы (русские)
MONTHS_RU = {
    'январ': 1, 'феврал': 2, 'март': 3, 'апрел': 4,
    'ма': 5, 'май': 5, 'июн': 6, 'июл': 7, 'август': 8,
    'сентябр': 9, 'октябр': 10, 'ноябр': 11, 'декабр': 12,
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
    'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
    'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
}

# Месяцы (английские)
MONTHS_EN = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

# Дни недели (русские)
WEEKDAYS_RU = {
    'понедельник': 0, 'вторник': 1, 'сред': 2, 'среду': 2,
    'четверг': 3, 'пятниц': 4, 'пятницу': 4,
    'суббот': 5, 'субботу': 5, 'воскресень': 6, 'воскресенье': 6,
    'пн': 0, 'вт': 1, 'ср': 2, 'чт': 3, 'пт': 4, 'сб': 5, 'вс': 6,
}

# Дни недели (английские)
WEEKDAYS_EN = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
    'friday': 4, 'saturday': 5, 'sunday': 6,
    'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6,
}

# Относительные даты (русские)
RELATIVE_RU = {
    'сегодня': 0,
    'завтра': 1,
    'послезавтра': 2,
    'вчера': -1,
    'позавчера': -2,
}

# Относительные даты (английские)
RELATIVE_EN = {
    'today': 0,
    'tomorrow': 1,
    'yesterday': -1,
}

# Времена суток
TIME_OF_DAY = {
    # Русские
    'утром': '09:00',
    'утра': '09:00',
    'днём': '14:00',
    'дня': '14:00',
    'вечером': '19:00',
    'вечера': '19:00',
    'ночью': '23:00',
    'ночи': '23:00',
    'полдень': '12:00',
    'полночь': '00:00',
    # Английские
    'morning': '09:00',
    'noon': '12:00',
    'afternoon': '14:00',
    'evening': '19:00',
    'night': '22:00',
    'midnight': '00:00',
}


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ОПРЕДЕЛЕНИЯ КОНТЕКСТА
# ═══════════════════════════════════════════════════════════════

CONTEXT_PATTERNS = {
    DateContext.ARRIVAL: [
        r'прилета[еюи]', r'прилёт', r'приезжа[еюи]', r'приед[у|ем]',
        r'прибыва[еюи]', r'заезд', r'заселя', r'въезд',
        r'arrival', r'check[- ]?in', r'arriving', r'land(?:ing)?',
    ],
    DateContext.DEPARTURE: [
        r'улета[еюи]', r'улёт', r'уезжа[еюи]', r'уед[у|ем]',
        r'выезд', r'выселя', r'вылет',
        r'departure', r'check[- ]?out', r'leaving', r'depart',
    ],
    DateContext.TOUR_DATE: [
        r'экскурси[яю]', r'тур\b', r'поездк[аи]', r'сафари',
        r'дезерт', r'абу[- ]?даби', r'шарджа', r'аквапарк',
        r'tour', r'excursion', r'safari', r'trip',
    ],
    DateContext.PAYMENT_DEADLINE: [
        r'оплат[аиу]', r'оплатить', r'заплатить', r'внести',
        r'предоплат', r'аванс', r'депозит', r'deadline',
        r'до\s+\d', r'крайний срок', r'не позднее',
        r'payment', r'pay by', r'due', r'deadline',
    ],
    DateContext.TRANSFER: [
        r'трансфер', r'встрет', r'забр[ао]', r'подвез',
        r'привез', r'отвез', r'аэропорт',
        r'transfer', r'pickup', r'pick[- ]?up', r'drop[- ]?off',
    ],
    DateContext.BOOKING: [
        r'бронирован', r'брониру[юе]', r'забронир', r'резерв',
        r'booking', r'reserv', r'book(?:ed)?',
    ],
    DateContext.MEETING: [
        r'встреч[аиу]', r'увидимся', r'созвон', r'звонок',
        r'meeting', r'meet', r'call',
    ],
    DateContext.REMINDER: [
        r'напомни', r'напоминание', r'не забудь', r'не забыть',
        r'remind', r'reminder', r'don\'t forget',
    ],
}


# ═══════════════════════════════════════════════════════════════
# РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ ДЛЯ ДАТ
# ═══════════════════════════════════════════════════════════════

# Числовые форматы
DATE_NUMERIC_PATTERNS = [
    # DD.MM.YYYY или DD/MM/YYYY или DD-MM-YYYY
    (r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})', 'dmy_full'),
    # DD.MM.YY
    (r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{2})(?!\d)', 'dmy_short'),
    # DD.MM (без года)
    (r'(\d{1,2})[./\-](\d{1,2})(?![./\-\d])', 'dm'),
    # YYYY-MM-DD (ISO)
    (r'(\d{4})-(\d{2})-(\d{2})', 'iso'),
]

# Время
TIME_PATTERNS = [
    # HH:MM или H:MM
    (r'(\d{1,2}):(\d{2})(?:\s*(am|pm|AM|PM))?', 'hm'),
    # "в 10" или "в 10:30"
    (r'в\s+(\d{1,2})(?::(\d{2}))?(?:\s+час[оа]?в?)?', 'ru_time'),
    # "at 10" или "at 10:30 am"
    (r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)?', 'en_time'),
    # "10 утра", "5 вечера"
    (r'(\d{1,2})\s+(утра|дня|вечера|ночи)', 'ru_period'),
]

# Русские текстовые даты
DATE_TEXT_RU = r'(\d{1,2})\s*(?:-?(?:го|ого|ое|е))?\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])'

# Английские текстовые даты
DATE_TEXT_EN = r'(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)'
DATE_TEXT_EN_REV = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(?:st|nd|rd|th)?'

# Относительные выражения
RELATIVE_PATTERNS = [
    # "через N дней/недель/месяцев"
    (r'через\s+(\d+)\s*(дн[ейя]|день|недел[юиь]|месяц[аев]?)', 'ru_in'),
    # "in N days/weeks"
    (r'in\s+(\d+)\s*(day[s]?|week[s]?|month[s]?)', 'en_in'),
    # "N дней назад"
    (r'(\d+)\s*(дн[ейя]|день|недел[юиь])\s+назад', 'ru_ago'),
    # "N days ago"
    (r'(\d+)\s*(day[s]?|week[s]?)\s+ago', 'en_ago'),
    # "на следующей неделе"
    (r'(?:на\s+)?следующ[ейую]+\s+недел[еюи]', 'ru_next_week'),
    # "next week"
    (r'next\s+week', 'en_next_week'),
    # "в этот/следующий понедельник"
    (r'(?:в\s+)?(?:этот|следующий|ближайший)?\s*(понедельник|вторник|сред[уа]|четверг|пятниц[уа]|суббот[уа]|воскресень[ея])', 'ru_weekday'),
    # "next Monday", "this Friday"
    (r'(?:this|next)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', 'en_weekday'),
]

# Диапазоны дат
DATE_RANGE_PATTERNS = [
    # "с 15 по 20 января"
    r'с\s+(\d{1,2})\s*(?:[-]?(?:го|ого))?\s*(?:по|до|-)\s+(\d{1,2})\s*(?:[-]?(?:го|ого))?\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])',
    # "15-20 января"
    r'(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(январ[яьи]|феврал[яьи]|март[аеи]?|апрел[яьи]|ма[яйи]|июн[яьи]|июл[яьи]|август[аеи]?|сентябр[яьи]|октябр[яьи]|ноябр[яьи]|декабр[яьи])',
    # "с 15.01 по 20.01"
    r'с\s+(\d{1,2})[./](\d{1,2})(?:[./]\d{2,4})?\s*(?:по|до|-)\s*(\d{1,2})[./](\d{1,2})(?:[./]\d{2,4})?',
]


# ═══════════════════════════════════════════════════════════════
# КЛАСС ПАРСЕРА
# ═══════════════════════════════════════════════════════════════

class DateTimeExtractor:
    """Универсальный парсер дат и времени."""

    def __init__(self, default_timezone: str = DEFAULT_TIMEZONE):
        self.default_tz = default_timezone
        self.tz = get_timezone(default_timezone)

        # Инициализация parsedatetime
        if PARSEDATETIME_AVAILABLE:
            self.pdt_cal = parsedatetime.Calendar()
        else:
            self.pdt_cal = None

    def _get_month_number(self, month_str: str) -> Optional[int]:
        """Получить номер месяца."""
        month_lower = month_str.lower().strip()

        # Русские
        for prefix, num in MONTHS_RU.items():
            if month_lower.startswith(prefix) or prefix.startswith(month_lower[:3]):
                return num

        # Английские
        for name, num in MONTHS_EN.items():
            if month_lower.startswith(name) or name.startswith(month_lower):
                return num

        return None

    def _get_weekday(self, day_str: str) -> Optional[int]:
        """Получить номер дня недели (0=понедельник)."""
        day_lower = day_str.lower().strip()

        # Русские
        for name, num in WEEKDAYS_RU.items():
            if day_lower.startswith(name) or name.startswith(day_lower):
                return num

        # Английские
        for name, num in WEEKDAYS_EN.items():
            if day_lower.startswith(name) or name.startswith(day_lower):
                return num

        return None

    def _determine_context(self, text: str) -> DateContext:
        """Определить контекст даты по тексту."""
        text_lower = text.lower()

        for context, patterns in CONTEXT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return context

        return DateContext.UNKNOWN

    def _parse_numeric_date(
        self,
        text: str,
        reference: datetime
    ) -> Optional[Tuple[datetime, float]]:
        """Парсинг числовых дат."""

        for pattern, format_type in DATE_NUMERIC_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()

                try:
                    if format_type == 'iso':
                        year = int(groups[0])
                        month = int(groups[1])
                        day = int(groups[2])
                    elif format_type == 'dmy_full':
                        day = int(groups[0])
                        month = int(groups[1])
                        year = int(groups[2])
                    elif format_type == 'dmy_short':
                        day = int(groups[0])
                        month = int(groups[1])
                        year = 2000 + int(groups[2])
                    elif format_type == 'dm':
                        day = int(groups[0])
                        month = int(groups[1])
                        year = reference.year
                        # Если месяц прошёл - следующий год
                        if month < reference.month or (month == reference.month and day < reference.day):
                            year += 1
                    else:
                        continue

                    # Валидация
                    if 1 <= day <= 31 and 1 <= month <= 12:
                        dt = datetime(year, month, day)
                        return dt, 0.9

                except (ValueError, IndexError):
                    continue

        return None

    def _parse_text_date(
        self,
        text: str,
        reference: datetime
    ) -> Optional[Tuple[datetime, float]]:
        """Парсинг текстовых дат."""
        text_lower = text.lower()

        # Русские даты "15 января"
        match = re.search(DATE_TEXT_RU, text_lower, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month = self._get_month_number(match.group(2))
            if month and 1 <= day <= 31:
                year = reference.year
                if month < reference.month or (month == reference.month and day < reference.day):
                    year += 1
                try:
                    dt = datetime(year, month, day)
                    return dt, 0.85
                except ValueError:
                    pass

        # Английские даты "15 January" или "January 15"
        for pattern in [DATE_TEXT_EN, DATE_TEXT_EN_REV]:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                if pattern == DATE_TEXT_EN_REV:
                    month = self._get_month_number(groups[0])
                    day = int(groups[1])
                else:
                    day = int(groups[0])
                    month = self._get_month_number(groups[1])

                if month and 1 <= day <= 31:
                    year = reference.year
                    if month < reference.month or (month == reference.month and day < reference.day):
                        year += 1
                    try:
                        dt = datetime(year, month, day)
                        return dt, 0.85
                    except ValueError:
                        pass

        return None

    def _parse_relative_date(
        self,
        text: str,
        reference: datetime
    ) -> Optional[Tuple[datetime, float]]:
        """Парсинг относительных дат."""
        text_lower = text.lower().strip()

        # Простые относительные (сегодня, завтра...)
        for word, days in {**RELATIVE_RU, **RELATIVE_EN}.items():
            if word in text_lower:
                dt = reference + timedelta(days=days)
                return dt, 0.95

        # Сложные относительные выражения
        for pattern, format_type in RELATIVE_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()

                try:
                    if format_type in ('ru_in', 'en_in'):
                        num = int(groups[0])
                        unit = groups[1].lower()

                        if 'дн' in unit or 'день' in unit or 'day' in unit:
                            delta = timedelta(days=num)
                        elif 'недел' in unit or 'week' in unit:
                            delta = timedelta(weeks=num)
                        elif 'месяц' in unit or 'month' in unit:
                            delta = timedelta(days=num * 30)
                        else:
                            continue

                        dt = reference + delta
                        return dt, 0.8

                    elif format_type in ('ru_ago', 'en_ago'):
                        num = int(groups[0])
                        unit = groups[1].lower()

                        if 'дн' in unit or 'день' in unit or 'day' in unit:
                            delta = timedelta(days=num)
                        elif 'недел' in unit or 'week' in unit:
                            delta = timedelta(weeks=num)
                        else:
                            continue

                        dt = reference - delta
                        return dt, 0.8

                    elif format_type in ('ru_next_week', 'en_next_week'):
                        # Начало следующей недели (понедельник)
                        days_ahead = 7 - reference.weekday()
                        dt = reference + timedelta(days=days_ahead)
                        return dt, 0.7

                    elif format_type in ('ru_weekday', 'en_weekday'):
                        weekday = self._get_weekday(groups[0])
                        if weekday is not None:
                            current_weekday = reference.weekday()
                            days_ahead = weekday - current_weekday
                            if days_ahead <= 0:
                                days_ahead += 7
                            dt = reference + timedelta(days=days_ahead)
                            return dt, 0.75

                except (ValueError, IndexError):
                    continue

        return None

    def _parse_time(self, text: str) -> Optional[str]:
        """Извлечь время из текста."""
        text_lower = text.lower()

        for pattern, format_type in TIME_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()

                try:
                    if format_type == 'hm':
                        hour = int(groups[0])
                        minute = int(groups[1])
                        ampm = groups[2].lower() if groups[2] else None

                        if ampm == 'pm' and hour < 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0

                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            return f"{hour:02d}:{minute:02d}"

                    elif format_type in ('ru_time', 'en_time'):
                        hour = int(groups[0])
                        minute = int(groups[1]) if groups[1] else 0

                        # AM/PM для английского
                        if len(groups) > 2 and groups[2]:
                            ampm = groups[2].lower()
                            if ampm == 'pm' and hour < 12:
                                hour += 12
                            elif ampm == 'am' and hour == 12:
                                hour = 0

                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            return f"{hour:02d}:{minute:02d}"

                    elif format_type == 'ru_period':
                        hour = int(groups[0])
                        period = groups[1].lower()

                        if 'вечера' in period and hour < 12:
                            hour += 12
                        elif 'дня' in period and hour < 12:
                            hour += 12
                        elif 'ночи' in period and hour < 12:
                            hour += 12

                        if 0 <= hour <= 23:
                            return f"{hour:02d}:00"

                except (ValueError, IndexError):
                    continue

        # Времена суток
        for word, time_str in TIME_OF_DAY.items():
            if word in text_lower:
                return time_str

        return None

    def parse_with_dateparser(
        self,
        text: str,
        reference: datetime
    ) -> Optional[Tuple[datetime, float]]:
        """Парсинг через dateparser."""
        if not DATEPARSER_AVAILABLE:
            return None

        try:
            settings = {
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': reference,
                'TIMEZONE': self.default_tz,
                'RETURN_AS_TIMEZONE_AWARE': False,
            }

            result = dateparser.parse(
                text,
                languages=['ru', 'en'],
                settings=settings
            )

            if result:
                return result, 0.7
        except Exception:
            pass

        return None

    def parse_with_parsedatetime(
        self,
        text: str,
        reference: datetime
    ) -> Optional[Tuple[datetime, float]]:
        """Парсинг через parsedatetime."""
        if not self.pdt_cal:
            return None

        try:
            time_struct, parse_status = self.pdt_cal.parse(text, reference)
            if parse_status > 0:
                dt = datetime(*time_struct[:6])
                # Уверенность зависит от статуса парсинга
                confidence = 0.6 if parse_status == 1 else 0.5
                return dt, confidence
        except Exception:
            pass

        return None

    def extract(
        self,
        text: str,
        reference: datetime = None,
        context_hint: str = None
    ) -> Optional[ExtractedDateTime]:
        """
        Извлечь дату/время из текста.

        Args:
            text: Текст для парсинга
            reference: Опорная дата (по умолчанию - сейчас)
            context_hint: Подсказка для контекста

        Returns:
            ExtractedDateTime или None
        """
        if not text or len(text) < 3:
            return None

        if reference is None:
            reference = datetime.now()

        result_dt = None
        confidence = 0.0

        # 1. Пробуем числовые форматы (высшая точность)
        parsed = self._parse_numeric_date(text, reference)
        if parsed:
            result_dt, confidence = parsed

        # 2. Пробуем текстовые форматы
        if not result_dt:
            parsed = self._parse_text_date(text, reference)
            if parsed:
                result_dt, confidence = parsed

        # 3. Пробуем относительные даты
        if not result_dt:
            parsed = self._parse_relative_date(text, reference)
            if parsed:
                result_dt, confidence = parsed

        # 4. Пробуем dateparser
        if not result_dt:
            parsed = self.parse_with_dateparser(text, reference)
            if parsed:
                result_dt, confidence = parsed

        # 5. Пробуем parsedatetime
        if not result_dt:
            parsed = self.parse_with_parsedatetime(text, reference)
            if parsed:
                result_dt, confidence = parsed

        if not result_dt:
            return None

        # Извлекаем время
        time_str = self._parse_time(text)
        if time_str:
            hour, minute = map(int, time_str.split(':'))
            result_dt = result_dt.replace(hour=hour, minute=minute)
            confidence = min(confidence + 0.05, 1.0)

        # Определяем контекст
        context = self._determine_context(text) if not context_hint else DateContext(context_hint)

        return ExtractedDateTime(
            record_id=str(uuid.uuid4()),
            datetime_value=result_dt.isoformat(),
            date_only=result_dt.strftime('%Y-%m-%d'),
            time_only=time_str,
            context=context.value,
            confidence=round(confidence, 2),
            original_text=text[:200],
            timezone=self.default_tz,
        )

    def extract_all(
        self,
        text: str,
        reference: datetime = None
    ) -> List[ExtractedDateTime]:
        """Извлечь все даты из текста."""
        if not text:
            return []

        if reference is None:
            reference = datetime.now()

        results = []
        seen_dates = set()

        # Разбиваем на предложения/фрагменты
        fragments = re.split(r'[.!?\n;]', text)

        for fragment in fragments:
            fragment = fragment.strip()
            if len(fragment) < 5:
                continue

            result = self.extract(fragment, reference)
            if result and result.date_only not in seen_dates:
                seen_dates.add(result.date_only)
                results.append(result)

        return results

    def parse_date_range(
        self,
        text: str,
        reference: datetime = None
    ) -> Tuple[Optional[ExtractedDateTime], Optional[ExtractedDateTime]]:
        """Извлечь диапазон дат."""
        if not text:
            return None, None

        if reference is None:
            reference = datetime.now()

        text_lower = text.lower()

        for pattern in DATE_RANGE_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()

                try:
                    # Паттерн "с 15 по 20 января"
                    if len(groups) == 3:
                        day1 = int(groups[0])
                        day2 = int(groups[1])
                        month = self._get_month_number(groups[2])

                        if month and 1 <= day1 <= 31 and 1 <= day2 <= 31:
                            year = reference.year
                            if month < reference.month:
                                year += 1

                            dt1 = datetime(year, month, day1)
                            dt2 = datetime(year, month, day2)

                            start = ExtractedDateTime(
                                record_id=str(uuid.uuid4()),
                                datetime_value=dt1.isoformat(),
                                date_only=dt1.strftime('%Y-%m-%d'),
                                time_only=None,
                                context=DateContext.ARRIVAL.value,
                                confidence=0.85,
                                original_text=text[:200],
                                timezone=self.default_tz,
                            )

                            end = ExtractedDateTime(
                                record_id=str(uuid.uuid4()),
                                datetime_value=dt2.isoformat(),
                                date_only=dt2.strftime('%Y-%m-%d'),
                                time_only=None,
                                context=DateContext.DEPARTURE.value,
                                confidence=0.85,
                                original_text=text[:200],
                                timezone=self.default_tz,
                            )

                            return start, end

                    # Паттерн "с 15.01 по 20.01"
                    elif len(groups) == 4:
                        day1 = int(groups[0])
                        month1 = int(groups[1])
                        day2 = int(groups[2])
                        month2 = int(groups[3])

                        if 1 <= day1 <= 31 and 1 <= month1 <= 12:
                            year1 = reference.year
                            year2 = reference.year

                            if month1 < reference.month:
                                year1 += 1
                            if month2 < reference.month:
                                year2 += 1

                            dt1 = datetime(year1, month1, day1)
                            dt2 = datetime(year2, month2, day2)

                            start = ExtractedDateTime(
                                record_id=str(uuid.uuid4()),
                                datetime_value=dt1.isoformat(),
                                date_only=dt1.strftime('%Y-%m-%d'),
                                time_only=None,
                                context=DateContext.ARRIVAL.value,
                                confidence=0.85,
                                original_text=text[:200],
                                timezone=self.default_tz,
                            )

                            end = ExtractedDateTime(
                                record_id=str(uuid.uuid4()),
                                datetime_value=dt2.isoformat(),
                                date_only=dt2.strftime('%Y-%m-%d'),
                                time_only=None,
                                context=DateContext.DEPARTURE.value,
                                confidence=0.85,
                                original_text=text[:200],
                                timezone=self.default_tz,
                            )

                            return start, end

                except (ValueError, IndexError):
                    continue

        return None, None


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ В iCAL
# ═══════════════════════════════════════════════════════════════

def export_to_ical(
    events: List[Dict[str, Any]],
    output_path: Path,
    calendar_name: str = "WhatsApp Events"
) -> bool:
    """
    Экспорт событий в iCal формат (.ics).

    Args:
        events: Список событий [{title, date, time, description, location}]
        output_path: Путь для сохранения .ics файла
        calendar_name: Название календаря

    Returns:
        True если успешно
    """
    if not ICALENDAR_AVAILABLE:
        print("[X] icalendar не установлен. pip install icalendar")
        return False

    try:
        cal = Calendar()
        cal.add('prodid', '-//WhatsApp Chat Parser//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', calendar_name)
        cal.add('x-wr-timezone', DEFAULT_TIMEZONE)

        tz = get_timezone()

        for event_data in events:
            event = ICalEvent()

            # Название
            title = event_data.get('title', 'Event')
            event.add('summary', title)

            # Дата и время
            date_str = event_data.get('date')
            time_str = event_data.get('time', '10:00')

            if date_str:
                try:
                    if 'T' in date_str:
                        dt = datetime.fromisoformat(date_str)
                    else:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                        if time_str:
                            hour, minute = map(int, time_str.split(':'))
                            dt = dt.replace(hour=hour, minute=minute)

                    # Добавляем временную зону
                    if PYTZ_AVAILABLE and tz:
                        dt = tz.localize(dt)

                    event.add('dtstart', dt)

                    # Длительность (1 час по умолчанию)
                    duration = event_data.get('duration_hours', 1)
                    event.add('dtend', dt + timedelta(hours=duration))

                except (ValueError, TypeError):
                    continue

            # Описание
            description = event_data.get('description', '')
            if description:
                event.add('description', description)

            # Место
            location = event_data.get('location', '')
            if location:
                event.add('location', location)

            # Уникальный ID
            uid = event_data.get('uid', str(uuid.uuid4()))
            event.add('uid', f"{uid}@whatsapp-parser")

            # Время создания
            event.add('dtstamp', datetime.now())

            # Категория/контекст
            context = event_data.get('context', '')
            if context:
                event.add('categories', [context])

            cal.add_component(event)

        # Сохраняем
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(cal.to_ical())

        return True

    except Exception as e:
        print(f"[X] Ошибка экспорта iCal: {e}")
        return False


def events_from_extracted_dates(
    extracted: List[ExtractedDateTime],
    include_context: bool = True
) -> List[Dict[str, Any]]:
    """Преобразовать ExtractedDateTime в события для iCal."""
    events = []

    for item in extracted:
        title_prefix = ""
        if include_context and item.context != "unknown":
            context_names = {
                'arrival': 'Arrival',
                'departure': 'Departure',
                'tour_date': 'Tour',
                'payment': 'Payment deadline',
                'transfer': 'Transfer',
                'booking': 'Booking',
                'meeting': 'Meeting',
                'reminder': 'Reminder',
            }
            title_prefix = f"{context_names.get(item.context, 'Event')}: "

        event = {
            'title': f"{title_prefix}{item.original_text[:50]}...",
            'date': item.date_only,
            'time': item.time_only or '10:00',
            'description': f"Extracted from chat\n\nOriginal: {item.original_text}",
            'context': item.context,
            'uid': item.record_id,
        }

        if item.chat_name:
            event['description'] += f"\nChat: {item.chat_name}"

        events.append(event)

    return events


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТКА СООБЩЕНИЙ ИЗ ЧАТА
# ═══════════════════════════════════════════════════════════════

def process_message(
    msg: dict,
    extractor: DateTimeExtractor
) -> List[ExtractedDateTime]:
    """Обработать одно сообщение."""
    text = msg.get('text')
    if not text or len(text) < 5:
        return []

    # Получаем дату сообщения как reference
    msg_datetime = msg.get('datetime')
    if msg_datetime:
        try:
            reference = datetime.fromisoformat(msg_datetime.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            reference = datetime.now()
    else:
        reference = datetime.now()

    # Извлекаем все даты
    results = extractor.extract_all(text, reference)

    # Добавляем метаданные
    for result in results:
        result.jid = msg.get('jid')
        result.chat_name = msg.get('chat_name')
        result.message_date = msg_datetime
        result.source = msg.get('source')

    return results


def main():
    """Основная функция."""
    print("=" * 60)
    print("ИЗВЛЕЧЕНИЕ ДАТ И ВРЕМЕНИ ИЗ ЧАТОВ")
    print("=" * 60)

    # Проверка зависимостей
    print("\nПроверка зависимостей:")
    print(f"  - dateparser: {'OK' if DATEPARSER_AVAILABLE else 'НЕ УСТАНОВЛЕН'}")
    print(f"  - parsedatetime: {'OK' if PARSEDATETIME_AVAILABLE else 'НЕ УСТАНОВЛЕН'}")
    print(f"  - pytz: {'OK' if PYTZ_AVAILABLE else 'НЕ УСТАНОВЛЕН'}")
    print(f"  - icalendar: {'OK' if ICALENDAR_AVAILABLE else 'НЕ УСТАНОВЛЕН'}")

    # Создать директории
    ensure_directories()

    # Пути
    input_file = RAW_DIR / "all_messages.jsonl"
    output_json = JSON_DIR / "datetime_extracted.json"
    output_ical = EXPORT_DIR / "calendar_events.ics"

    print(f"\nВходной файл: {input_file}")
    print(f"Выходной JSON: {output_json}")
    print(f"Выходной iCal: {output_ical}")

    if not input_file.exists():
        print(f"\n[ОШИБКА] Файл не найден: {input_file}")
        print("Сначала запустите parse_all_chats.py для создания all_messages.jsonl")

        # Демо-режим
        print("\n" + "=" * 60)
        print("ДЕМО-РЕЖИМ: Тестирование парсера")
        print("=" * 60)

        demo_texts = [
            "Прилетаем 15 января в 10:00",
            "Завтра в 14:30 экскурсия в Абу-Даби",
            "Оплатить до 25.01.2026",
            "next Monday at 3 PM",
            "будем в Дубае с 20 по 25 февраля",
            "через 3 дня встреча в отеле",
            "January 15th arrival",
            "вылет 30.01 в 23:45",
        ]

        extractor = DateTimeExtractor()

        for text in demo_texts:
            print(f"\n> {text}")
            result = extractor.extract(text)
            if result:
                print(f"  Date: {result.date_only}")
                print(f"  Time: {result.time_only or 'N/A'}")
                print(f"  Context: {result.context}")
                print(f"  Confidence: {result.confidence}")
            else:
                print("  [No date found]")

        return

    # Инициализация
    extractor = DateTimeExtractor(default_timezone=DEFAULT_TIMEZONE)

    print("\nЧитаю сообщения...")

    all_extracted = []
    total_messages = 0
    start_time = datetime.now()

    # Обработка
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            total_messages += 1

            try:
                msg = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            results = process_message(msg, extractor)
            all_extracted.extend(results)

            # Прогресс
            if total_messages % 50000 == 0:
                print(f"  Обработано: {total_messages:,}, найдено дат: {len(all_extracted):,}")

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\nОбработано сообщений: {total_messages:,}")
    print(f"Найдено дат: {len(all_extracted):,}")
    print(f"Время: {elapsed:.1f} сек")

    # Удаление дубликатов
    seen = set()
    unique = []
    for item in all_extracted:
        key = (item.jid, item.date_only, item.context)
        if key not in seen:
            seen.add(key)
            unique.append(item)

    print(f"После удаления дубликатов: {len(unique):,}")

    # Сортировка
    unique.sort(key=lambda x: x.datetime_value)

    # Статистика по контекстам
    context_stats = defaultdict(int)
    for item in unique:
        context_stats[item.context] += 1

    # Формируем результат
    result = {
        'generated_at': datetime.now().isoformat(),
        'total_messages_scanned': total_messages,
        'total_dates_found': len(unique),
        'timezone': DEFAULT_TIMEZONE,
        'context_statistics': dict(context_stats),
        'dates': [asdict(item) for item in unique],
    }

    # Сохраняем JSON
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nСохранено JSON: {output_json}")
    print(f"Размер: {output_json.stat().st_size / 1024:.1f} KB")

    # Экспорт в iCal
    if ICALENDAR_AVAILABLE and unique:
        events = events_from_extracted_dates(unique)

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        if export_to_ical(events, output_ical):
            print(f"\nСохранено iCal: {output_ical}")
            print(f"Событий: {len(events)}")

    # Итоги
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПО КОНТЕКСТАМ")
    print("=" * 60)
    for context, count in sorted(context_stats.items(), key=lambda x: -x[1]):
        print(f"  {context}: {count:,}")


def interactive_test():
    """Интерактивный режим тестирования парсера."""
    print("=" * 60)
    print("ИНТЕРАКТИВНЫЙ ТЕСТ ПАРСЕРА ДАТ")
    print("=" * 60)
    print("Введите текст для парсинга (или 'exit' для выхода)")
    print("Примеры:")
    print("  - завтра в 10:00")
    print("  - 15 января")
    print("  - next Monday at 3 PM")
    print("  - через 3 дня")
    print("  - с 20 по 25 февраля")
    print("=" * 60)

    extractor = DateTimeExtractor()
    reference = datetime.now()

    while True:
        try:
            text = input("\n> ").strip()
            if text.lower() in ('exit', 'quit', 'q'):
                break

            if not text:
                continue

            # Пробуем обычный парсинг
            result = extractor.extract(text, reference)
            if result:
                print(f"  Date: {result.date_only}")
                print(f"  Time: {result.time_only or 'N/A'}")
                print(f"  Context: {result.context}")
                print(f"  Confidence: {result.confidence}")
                print(f"  Timezone: {result.timezone}")
            else:
                # Пробуем диапазон
                start, end = extractor.parse_date_range(text, reference)
                if start and end:
                    print(f"  Range detected:")
                    print(f"    Start: {start.date_only}")
                    print(f"    End: {end.date_only}")
                else:
                    print("  [No date found]")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  [Error: {e}]")

    print("\nВыход.")


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ИМПОРТА
# ═══════════════════════════════════════════════════════════════

def parse_date_simple(text: str, timezone: str = DEFAULT_TIMEZONE) -> Optional[str]:
    """
    Простая функция для парсинга даты.

    Args:
        text: Текст с датой
        timezone: Временная зона

    Returns:
        Дата в формате YYYY-MM-DD или None
    """
    extractor = DateTimeExtractor(timezone)
    result = extractor.extract(text)
    return result.date_only if result else None


def parse_datetime_simple(text: str, timezone: str = DEFAULT_TIMEZONE) -> Optional[str]:
    """
    Простая функция для парсинга даты и времени.

    Args:
        text: Текст с датой/временем
        timezone: Временная зона

    Returns:
        Datetime в ISO формате или None
    """
    extractor = DateTimeExtractor(timezone)
    result = extractor.extract(text)
    return result.datetime_value if result else None


def get_context(text: str) -> str:
    """
    Определить контекст даты.

    Args:
        text: Текст для анализа

    Returns:
        Контекст (arrival, departure, tour_date, payment, etc.)
    """
    extractor = DateTimeExtractor()
    return extractor._determine_context(text).value


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--test' or sys.argv[1] == '-t':
            interactive_test()
        elif sys.argv[1] == '--demo' or sys.argv[1] == '-d':
            # Демо с примерами
            demo_texts = [
                "Прилетаем 15 января в 10:00",
                "Завтра в 14:30 экскурсия в Абу-Даби",
                "Оплатить до 25.01.2026",
                "next Monday at 3 PM",
                "будем в Дубае с 20 по 25 февраля",
                "через 3 дня встреча в отеле",
                "January 15th arrival",
                "вылет 30.01 в 23:45",
                "послезавтра утром",
                "в следующий понедельник",
            ]

            extractor = DateTimeExtractor()
            print("=" * 60)
            print("ДЕМО: Тестирование парсера")
            print("=" * 60)

            for text in demo_texts:
                print(f"\n> {text}")
                result = extractor.extract(text)
                if result:
                    print(f"  Date: {result.date_only}")
                    print(f"  Time: {result.time_only or 'N/A'}")
                    print(f"  Context: {result.context}")
                    print(f"  Confidence: {result.confidence}")
                else:
                    # Пробуем диапазон
                    start, end = extractor.parse_date_range(text)
                    if start and end:
                        print(f"  Range: {start.date_only} - {end.date_only}")
                    else:
                        print("  [No date found]")
        else:
            # Парсинг переданного текста
            text = ' '.join(sys.argv[1:])
            extractor = DateTimeExtractor()

            # Сначала пробуем диапазон (более специфичный паттерн)
            start, end = extractor.parse_date_range(text)
            if start and end:
                print(json.dumps({
                    'type': 'range',
                    'start': asdict(start),
                    'end': asdict(end),
                }, ensure_ascii=False, indent=2))
            else:
                # Затем обычный парсинг
                result = extractor.extract(text)
                if result:
                    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
                else:
                    print('{"error": "No date found"}')
    else:
        main()
