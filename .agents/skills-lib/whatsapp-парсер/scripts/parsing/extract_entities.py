#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение сущностей из сообщений WhatsApp.

Вход: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выход: D:/Downloads/Chats/_база/json/entities.json

Функции:
- Словарь отелей ОАЭ (Atlantis, Burj Al Arab, Emirates Palace...)
- Типы номеров (Standard, Deluxe, Suite, Sea View...)
- Туристические продукты (desert safari, ferrari world, dhow cruise...)
- Даты заезда/выезда
- Количество гостей (PAX)
- Рейсы и аэропорты
"""

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, date
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
OUTPUT_FILE = JSON_DIR / "entities.json"

# Словарь отелей ОАЭ
HOTELS_UAE = {
    # Luxury 5* Dubai
    "atlantis": {"canonical": "Atlantis The Palm", "city": "Dubai", "stars": 5},
    "atlantis the palm": {"canonical": "Atlantis The Palm", "city": "Dubai", "stars": 5},
    "атлантис": {"canonical": "Atlantis The Palm", "city": "Dubai", "stars": 5},
    "atlantis royal": {"canonical": "Atlantis The Royal", "city": "Dubai", "stars": 5},
    "атлантис роял": {"canonical": "Atlantis The Royal", "city": "Dubai", "stars": 5},
    "burj al arab": {"canonical": "Burj Al Arab", "city": "Dubai", "stars": 5},
    "бурдж аль араб": {"canonical": "Burj Al Arab", "city": "Dubai", "stars": 5},
    "парус": {"canonical": "Burj Al Arab", "city": "Dubai", "stars": 5},
    "jumeirah beach hotel": {"canonical": "Jumeirah Beach Hotel", "city": "Dubai", "stars": 5},
    "jbh": {"canonical": "Jumeirah Beach Hotel", "city": "Dubai", "stars": 5},
    "armani hotel": {"canonical": "Armani Hotel Dubai", "city": "Dubai", "stars": 5},
    "армани": {"canonical": "Armani Hotel Dubai", "city": "Dubai", "stars": 5},
    "four seasons difc": {"canonical": "Four Seasons DIFC", "city": "Dubai", "stars": 5},
    "four seasons jumeirah": {"canonical": "Four Seasons Jumeirah", "city": "Dubai", "stars": 5},
    "фор сизонс": {"canonical": "Four Seasons", "city": "Dubai", "stars": 5},
    "one and only": {"canonical": "One&Only The Palm", "city": "Dubai", "stars": 5},
    "one&only": {"canonical": "One&Only The Palm", "city": "Dubai", "stars": 5},
    "palazzo versace": {"canonical": "Palazzo Versace", "city": "Dubai", "stars": 5},
    "версаче": {"canonical": "Palazzo Versace", "city": "Dubai", "stars": 5},
    "ritz carlton": {"canonical": "The Ritz-Carlton", "city": "Dubai", "stars": 5},
    "риц карлтон": {"canonical": "The Ritz-Carlton", "city": "Dubai", "stars": 5},
    "w dubai": {"canonical": "W Dubai", "city": "Dubai", "stars": 5},
    "address downtown": {"canonical": "Address Downtown", "city": "Dubai", "stars": 5},
    "address marina": {"canonical": "Address Dubai Marina", "city": "Dubai", "stars": 5},
    "address sky view": {"canonical": "Address Sky View", "city": "Dubai", "stars": 5},
    "адрес": {"canonical": "Address Hotel", "city": "Dubai", "stars": 5},
    "mandarin oriental": {"canonical": "Mandarin Oriental Jumeira", "city": "Dubai", "stars": 5},
    "мандарин": {"canonical": "Mandarin Oriental Jumeira", "city": "Dubai", "stars": 5},

    # Abu Dhabi
    "emirates palace": {"canonical": "Emirates Palace", "city": "Abu Dhabi", "stars": 5},
    "эмирейтс палас": {"canonical": "Emirates Palace", "city": "Abu Dhabi", "stars": 5},
    "st regis saadiyat": {"canonical": "St. Regis Saadiyat", "city": "Abu Dhabi", "stars": 5},
    "сент реджис": {"canonical": "St. Regis", "city": "Abu Dhabi", "stars": 5},
    "yas hotel": {"canonical": "W Abu Dhabi - Yas Island", "city": "Abu Dhabi", "stars": 5},
    "яс отель": {"canonical": "W Abu Dhabi - Yas Island", "city": "Abu Dhabi", "stars": 5},
    "conrad abu dhabi": {"canonical": "Conrad Abu Dhabi Etihad Towers", "city": "Abu Dhabi", "stars": 5},
    "shangri-la abu dhabi": {"canonical": "Shangri-La Abu Dhabi", "city": "Abu Dhabi", "stars": 5},

    # Массовые 4-5*
    "jw marriott": {"canonical": "JW Marriott Marquis", "city": "Dubai", "stars": 5},
    "marriott marquis": {"canonical": "JW Marriott Marquis", "city": "Dubai", "stars": 5},
    "марриотт": {"canonical": "Marriott", "city": "Dubai", "stars": 5},
    "hilton": {"canonical": "Hilton Dubai", "city": "Dubai", "stars": 5},
    "хилтон": {"canonical": "Hilton Dubai", "city": "Dubai", "stars": 5},
    "sofitel": {"canonical": "Sofitel Dubai", "city": "Dubai", "stars": 5},
    "софитель": {"canonical": "Sofitel Dubai", "city": "Dubai", "stars": 5},
    "sheraton": {"canonical": "Sheraton Grand Dubai", "city": "Dubai", "stars": 5},
    "шератон": {"canonical": "Sheraton Grand Dubai", "city": "Dubai", "stars": 5},
    "intercontinental": {"canonical": "InterContinental Dubai", "city": "Dubai", "stars": 5},
    "интерконтиненталь": {"canonical": "InterContinental Dubai", "city": "Dubai", "stars": 5},
    "grand hyatt": {"canonical": "Grand Hyatt Dubai", "city": "Dubai", "stars": 5},
    "hyatt regency": {"canonical": "Hyatt Regency Dubai", "city": "Dubai", "stars": 5},
    "хаятт": {"canonical": "Hyatt", "city": "Dubai", "stars": 5},
    "radisson blu": {"canonical": "Radisson Blu", "city": "Dubai", "stars": 5},
    "радиссон": {"canonical": "Radisson Blu", "city": "Dubai", "stars": 5},
    "movenpick": {"canonical": "Movenpick", "city": "Dubai", "stars": 5},
    "мовенпик": {"canonical": "Movenpick", "city": "Dubai", "stars": 5},
    "crowne plaza": {"canonical": "Crowne Plaza", "city": "Dubai", "stars": 5},
    "краун плаза": {"canonical": "Crowne Plaza", "city": "Dubai", "stars": 5},
    "fairmont": {"canonical": "Fairmont Dubai", "city": "Dubai", "stars": 5},
    "фэрмонт": {"canonical": "Fairmont Dubai", "city": "Dubai", "stars": 5},
    "kempinski": {"canonical": "Kempinski", "city": "Dubai", "stars": 5},
    "кемпински": {"canonical": "Kempinski", "city": "Dubai", "stars": 5},

    # Бюджетные
    "ibis": {"canonical": "Ibis", "city": "Dubai", "stars": 3},
    "ибис": {"canonical": "Ibis", "city": "Dubai", "stars": 3},
    "premier inn": {"canonical": "Premier Inn", "city": "Dubai", "stars": 3},
    "citymax": {"canonical": "Citymax", "city": "Dubai", "stars": 3},
    "rove": {"canonical": "Rove Hotel", "city": "Dubai", "stars": 3},
    "рове": {"canonical": "Rove Hotel", "city": "Dubai", "stars": 3},
    "holiday inn": {"canonical": "Holiday Inn", "city": "Dubai", "stars": 4},
    "холидей инн": {"canonical": "Holiday Inn", "city": "Dubai", "stars": 4},
}

# Типы номеров
ROOM_TYPES = {
    # Стандартные
    "std": "Standard Room",
    "standard": "Standard Room",
    "стандарт": "Standard Room",
    "sup": "Superior Room",
    "superior": "Superior Room",
    "супериор": "Superior Room",
    "dlx": "Deluxe Room",
    "deluxe": "Deluxe Room",
    "делюкс": "Deluxe Room",
    "премиум": "Premium Room",
    "premium": "Premium Room",

    # Люксы
    "jrs": "Junior Suite",
    "junior suite": "Junior Suite",
    "джуниор сьют": "Junior Suite",
    "suite": "Suite",
    "сьют": "Suite",
    "люкс": "Suite",
    "executive suite": "Executive Suite",
    "presidential": "Presidential Suite",
    "royal suite": "Royal Suite",
    "роял сьют": "Royal Suite",

    # По виду
    "sea view": "Sea View Room",
    "sv": "Sea View Room",
    "сивью": "Sea View Room",
    "вид на море": "Sea View Room",
    "ocean view": "Ocean View Room",
    "garden view": "Garden View Room",
    "pool view": "Pool View Room",
    "city view": "City View Room",
    "burj view": "Burj Khalifa View",
    "вид на бурдж": "Burj Khalifa View",
    "fountain view": "Fountain View Room",
    "вид на фонтан": "Fountain View Room",
    "palm view": "Palm View Room",
    "вид на пальму": "Palm View Room",

    # Специальные
    "connecting": "Connecting Rooms",
    "смежные": "Connecting Rooms",
    "family room": "Family Room",
    "семейный": "Family Room",
    "club room": "Club Room",
    "клубный": "Club Room",
    "beach access": "Beach Access Room",
    "private pool": "Private Pool Room",
    "с бассейном": "Private Pool Room",
}

# Туристические продукты - Экскурсии
TOURS_UAE = {
    # Обзорные туры
    "abu dhabi tour": {"canonical": "Abu Dhabi City Tour", "type": "city_tour", "duration": 8},
    "тур абу даби": {"canonical": "Abu Dhabi City Tour", "type": "city_tour", "duration": 8},
    "абу даби экскурсия": {"canonical": "Abu Dhabi City Tour", "type": "city_tour", "duration": 8},
    "экскурсия в абу даби": {"canonical": "Abu Dhabi City Tour", "type": "city_tour", "duration": 8},
    "dubai city tour": {"canonical": "Dubai City Tour", "type": "city_tour", "duration": 4},
    "обзорка дубай": {"canonical": "Dubai City Tour", "type": "city_tour", "duration": 4},
    "обзорная дубай": {"canonical": "Dubai City Tour", "type": "city_tour", "duration": 4},
    "old dubai tour": {"canonical": "Old Dubai Walking Tour", "type": "walking_tour", "duration": 3},
    "старый дубай": {"canonical": "Old Dubai Walking Tour", "type": "walking_tour", "duration": 3},

    # Пустыня
    "desert safari": {"canonical": "Desert Safari", "type": "adventure", "duration": 6},
    "сафари": {"canonical": "Desert Safari", "type": "adventure", "duration": 6},
    "дезерт сафари": {"canonical": "Desert Safari", "type": "adventure", "duration": 6},
    "в пустыню": {"canonical": "Desert Safari", "type": "adventure", "duration": 6},
    "дюны": {"canonical": "Desert Safari", "type": "adventure", "duration": 6},
    "morning safari": {"canonical": "Morning Desert Safari", "type": "adventure", "duration": 4},
    "утренне сафари": {"canonical": "Morning Desert Safari", "type": "adventure", "duration": 4},
    "overnight safari": {"canonical": "Overnight Desert Safari", "type": "adventure", "duration": 18},
    "ночное сафари": {"canonical": "Overnight Desert Safari", "type": "adventure", "duration": 18},
    "camel ride": {"canonical": "Camel Riding Experience", "type": "adventure", "duration": 2},
    "на верблюдах": {"canonical": "Camel Riding Experience", "type": "adventure", "duration": 2},
    "quad bike": {"canonical": "Quad Biking", "type": "adventure", "duration": 1},
    "квадроциклы": {"canonical": "Quad Biking", "type": "adventure", "duration": 1},
    "квадрики": {"canonical": "Quad Biking", "type": "adventure", "duration": 1},
    "buggy": {"canonical": "Dune Buggy", "type": "adventure", "duration": 2},
    "багги": {"canonical": "Dune Buggy", "type": "adventure", "duration": 2},

    # Морские
    "dubai marina cruise": {"canonical": "Dubai Marina Cruise", "type": "cruise", "duration": 2},
    "круиз марина": {"canonical": "Dubai Marina Cruise", "type": "cruise", "duration": 2},
    "dhow cruise": {"canonical": "Dhow Cruise Dinner", "type": "cruise", "duration": 2},
    "дау круиз": {"canonical": "Dhow Cruise Dinner", "type": "cruise", "duration": 2},
    "доу круиз": {"canonical": "Dhow Cruise Dinner", "type": "cruise", "duration": 2},
    "ужин на лодке": {"canonical": "Dhow Cruise Dinner", "type": "cruise", "duration": 2},
    "musandam": {"canonical": "Musandam Day Trip", "type": "day_trip", "duration": 10},
    "мусандам": {"canonical": "Musandam Day Trip", "type": "day_trip", "duration": 10},

    # Однодневные поездки
    "al ain": {"canonical": "Al Ain Day Trip", "type": "day_trip", "duration": 8},
    "аль айн": {"canonical": "Al Ain Day Trip", "type": "day_trip", "duration": 8},
    "hatta": {"canonical": "Hatta Mountain Tour", "type": "day_trip", "duration": 8},
    "хатта": {"canonical": "Hatta Mountain Tour", "type": "day_trip", "duration": 8},
    "fujairah": {"canonical": "Fujairah East Coast Tour", "type": "day_trip", "duration": 9},
    "фуджейра": {"canonical": "Fujairah East Coast Tour", "type": "day_trip", "duration": 9},
    "ras al khaimah": {"canonical": "Ras Al Khaimah Tour", "type": "day_trip", "duration": 8},
    "рас аль хайма": {"canonical": "Ras Al Khaimah Tour", "type": "day_trip", "duration": 8},
}

# Аттракционы и билеты
ATTRACTIONS_UAE = {
    # Тематические парки
    "ferrari world": {"canonical": "Ferrari World Abu Dhabi", "city": "Abu Dhabi", "type": "theme_park"},
    "феррари": {"canonical": "Ferrari World Abu Dhabi", "city": "Abu Dhabi", "type": "theme_park"},
    "феррари ворлд": {"canonical": "Ferrari World Abu Dhabi", "city": "Abu Dhabi", "type": "theme_park"},
    "img worlds": {"canonical": "IMG Worlds of Adventure", "city": "Dubai", "type": "theme_park"},
    "имг": {"canonical": "IMG Worlds of Adventure", "city": "Dubai", "type": "theme_park"},
    "имджи": {"canonical": "IMG Worlds of Adventure", "city": "Dubai", "type": "theme_park"},
    "legoland": {"canonical": "LEGOLAND Dubai", "city": "Dubai", "type": "theme_park"},
    "леголенд": {"canonical": "LEGOLAND Dubai", "city": "Dubai", "type": "theme_park"},
    "motiongate": {"canonical": "Motiongate Dubai", "city": "Dubai", "type": "theme_park"},
    "моушнгейт": {"canonical": "Motiongate Dubai", "city": "Dubai", "type": "theme_park"},
    "bollywood parks": {"canonical": "Bollywood Parks Dubai", "city": "Dubai", "type": "theme_park"},
    "болливуд": {"canonical": "Bollywood Parks Dubai", "city": "Dubai", "type": "theme_park"},
    "warner bros": {"canonical": "Warner Bros World Abu Dhabi", "city": "Abu Dhabi", "type": "theme_park"},
    "варнер": {"canonical": "Warner Bros World Abu Dhabi", "city": "Abu Dhabi", "type": "theme_park"},
    "варнер брос": {"canonical": "Warner Bros World Abu Dhabi", "city": "Abu Dhabi", "type": "theme_park"},

    # Аквапарки
    "yas waterworld": {"canonical": "Yas Waterworld", "city": "Abu Dhabi", "type": "water_park"},
    "яс вотерворлд": {"canonical": "Yas Waterworld", "city": "Abu Dhabi", "type": "water_park"},
    "aquaventure": {"canonical": "Aquaventure Waterpark", "city": "Dubai", "type": "water_park"},
    "аквавенчур": {"canonical": "Aquaventure Waterpark", "city": "Dubai", "type": "water_park"},
    "аквавентура": {"canonical": "Aquaventure Waterpark", "city": "Dubai", "type": "water_park"},
    "wild wadi": {"canonical": "Wild Wadi Waterpark", "city": "Dubai", "type": "water_park"},
    "вайлд вади": {"canonical": "Wild Wadi Waterpark", "city": "Dubai", "type": "water_park"},
    "вилд вади": {"canonical": "Wild Wadi Waterpark", "city": "Dubai", "type": "water_park"},

    # Смотровые площадки
    "burj khalifa": {"canonical": "Burj Khalifa At The Top", "city": "Dubai", "type": "observation"},
    "бурдж халифа": {"canonical": "Burj Khalifa At The Top", "city": "Dubai", "type": "observation"},
    "бурж халифа": {"canonical": "Burj Khalifa At The Top", "city": "Dubai", "type": "observation"},
    "at the top": {"canonical": "Burj Khalifa At The Top", "city": "Dubai", "type": "observation"},
    "at the top sky": {"canonical": "Burj Khalifa At The Top Sky", "city": "Dubai", "type": "observation"},
    "dubai frame": {"canonical": "Dubai Frame", "city": "Dubai", "type": "observation"},
    "дубай фрейм": {"canonical": "Dubai Frame", "city": "Dubai", "type": "observation"},
    "рамка": {"canonical": "Dubai Frame", "city": "Dubai", "type": "observation"},
    "view at the palm": {"canonical": "The View at The Palm", "city": "Dubai", "type": "observation"},
    "вью на пальме": {"canonical": "The View at The Palm", "city": "Dubai", "type": "observation"},
    "ain dubai": {"canonical": "Ain Dubai", "city": "Dubai", "type": "observation"},
    "колесо обозрения": {"canonical": "Ain Dubai", "city": "Dubai", "type": "observation"},

    # Музеи
    "louvre": {"canonical": "Louvre Abu Dhabi", "city": "Abu Dhabi", "type": "museum"},
    "лувр": {"canonical": "Louvre Abu Dhabi", "city": "Abu Dhabi", "type": "museum"},
    "museum of the future": {"canonical": "Museum of the Future", "city": "Dubai", "type": "museum"},
    "музей будущего": {"canonical": "Museum of the Future", "city": "Dubai", "type": "museum"},
    "motf": {"canonical": "Museum of the Future", "city": "Dubai", "type": "museum"},
    "global village": {"canonical": "Global Village", "city": "Dubai", "type": "entertainment"},
    "глобал вилладж": {"canonical": "Global Village", "city": "Dubai", "type": "entertainment"},
    "глобал виллаж": {"canonical": "Global Village", "city": "Dubai", "type": "entertainment"},
    "miracle garden": {"canonical": "Dubai Miracle Garden", "city": "Dubai", "type": "garden"},
    "миракл гарден": {"canonical": "Dubai Miracle Garden", "city": "Dubai", "type": "garden"},
    "сад чудес": {"canonical": "Dubai Miracle Garden", "city": "Dubai", "type": "garden"},

    # Аквариумы
    "dubai aquarium": {"canonical": "Dubai Aquarium & Underwater Zoo", "city": "Dubai", "type": "aquarium"},
    "аквариум": {"canonical": "Dubai Aquarium & Underwater Zoo", "city": "Dubai", "type": "aquarium"},
    "lost chambers": {"canonical": "The Lost Chambers Aquarium", "city": "Dubai", "type": "aquarium"},
    "лост чамберс": {"canonical": "The Lost Chambers Aquarium", "city": "Dubai", "type": "aquarium"},
    "sea world": {"canonical": "SeaWorld Abu Dhabi", "city": "Abu Dhabi", "type": "aquarium"},
    "сиворлд": {"canonical": "SeaWorld Abu Dhabi", "city": "Abu Dhabi", "type": "aquarium"},
}

# Типы питания
MEAL_PLANS = {
    "ro": "Room Only",
    "room only": "Room Only",
    "без питания": "Room Only",
    "bb": "Bed & Breakfast",
    "bed and breakfast": "Bed & Breakfast",
    "завтрак": "Bed & Breakfast",
    "с завтраком": "Bed & Breakfast",
    "hb": "Half Board",
    "half board": "Half Board",
    "полупансион": "Half Board",
    "fb": "Full Board",
    "full board": "Full Board",
    "полный пансион": "Full Board",
    "трёхразовое": "Full Board",
    "ai": "All Inclusive",
    "all inclusive": "All Inclusive",
    "всё включено": "All Inclusive",
    "все включено": "All Inclusive",
    "олл инклюзив": "All Inclusive",
    "uai": "Ultra All Inclusive",
    "ультра": "Ultra All Inclusive",
}

# Коды авиакомпаний
AIRLINE_CODES = {
    "EK": "Emirates",
    "EY": "Etihad Airways",
    "FZ": "flydubai",
    "G9": "Air Arabia",
    "SU": "Aeroflot",
    "S7": "S7 Airlines",
    "KC": "Air Astana",
    "QR": "Qatar Airways",
    "TK": "Turkish Airlines",
}

# Аэропорты
AIRPORTS = {
    "DXB": {"name": "Dubai International Airport", "city": "Dubai"},
    "DWC": {"name": "Al Maktoum International Airport", "city": "Dubai"},
    "AUH": {"name": "Abu Dhabi International Airport", "city": "Abu Dhabi"},
    "SHJ": {"name": "Sharjah International Airport", "city": "Sharjah"},
    "SVO": {"name": "Sheremetyevo", "city": "Moscow"},
    "DME": {"name": "Domodedovo", "city": "Moscow"},
    "VKO": {"name": "Vnukovo", "city": "Moscow"},
    "LED": {"name": "Pulkovo", "city": "St. Petersburg"},
    "ALA": {"name": "Almaty International Airport", "city": "Almaty"},
}

# Месяцы на русском
RUSSIAN_MONTHS = {
    'января': 1, 'янв': 1, 'февраля': 2, 'фев': 2,
    'марта': 3, 'мар': 3, 'апреля': 4, 'апр': 4,
    'мая': 5, 'июня': 6, 'июн': 6, 'июля': 7, 'июл': 7,
    'августа': 8, 'авг': 8, 'сентября': 9, 'сен': 9,
    'октября': 10, 'окт': 10, 'ноября': 11, 'ноя': 11,
    'декабря': 12, 'дек': 12,
}


# ===================================================================
# REGEX ПАТТЕРНЫ
# ===================================================================

PATTERNS = {
    # Даты
    'date_dot': re.compile(r'(\d{1,2})[./](\d{1,2})[./]?(\d{2,4})?'),
    'date_ru': re.compile(
        r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|'
        r'июля|августа|сентября|октября|ноября|декабря|'
        r'янв|фев|мар|апр|июн|июл|авг|сен|окт|ноя|дек)(?:\s*(\d{4}))?',
        re.IGNORECASE
    ),
    'date_range': re.compile(
        r'с\s*(\d{1,2})\s*(?:по|-)\s*(\d{1,2})\s*'
        r'(января|февраля|марта|апреля|мая|июня|июля|августа|'
        r'сентября|октября|ноября|декабря)',
        re.IGNORECASE
    ),
    'date_iso': re.compile(r'(\d{4})-(\d{2})-(\d{2})'),
    'nights': re.compile(r'(\d+)\s*(ноч[еиь]й?|nights?|n(?:ts)?)', re.IGNORECASE),
    'checkin_checkout': re.compile(
        r'(?:check[\s-]?in|заезд)[:\s]*(\d{1,2}[./]\d{1,2}[./]?\d{0,4})'
        r'.*?(?:check[\s-]?out|выезд)[:\s]*(\d{1,2}[./]\d{1,2}[./]?\d{0,4})',
        re.IGNORECASE | re.DOTALL
    ),

    # PAX
    'pax_adults': re.compile(r'(\d+)\s*(?:взросл\w*|adult|pax)', re.IGNORECASE),
    'pax_children': re.compile(r'(\d+)\s*(?:реб[её]н\w*|child|kid|дет\w*)', re.IGNORECASE),
    'pax_infants': re.compile(r'(\d+)\s*(?:infant|младен\w*|грудн\w*)', re.IGNORECASE),
    'pax_format': re.compile(r'(\d+)\s*\+\s*(\d+)(?:\s*\+\s*(\d+))?'),
    'pax_total': re.compile(r'(\d+)\s*(?:чел\w*|человек|гост\w*|pax)', re.IGNORECASE),
    'pax_family': re.compile(r'семь[яи]\s*(?:из\s*)?(\d+)', re.IGNORECASE),

    # Рейсы
    'flight_code': re.compile(r'\b([A-Z]{2})\s*(\d{1,4})\b'),
    'flight_time': re.compile(
        r'(?:прил[её]т|вылет|arrival|departure|arr|dep)[:\s]*(\d{1,2}):(\d{2})',
        re.IGNORECASE
    ),
    'airport': re.compile(r'\b(DXB|DWC|AUH|SHJ|SVO|DME|VKO|LED|ALA)\b'),
    'terminal': re.compile(r'(?:терминал|terminal|Т|T)\s*(\d|[ABC])', re.IGNORECASE),
}


# ===================================================================
# КЛАССЫ ДАННЫХ
# ===================================================================

@dataclass
class HotelExtraction:
    """Извлечённый отель."""
    canonical_name: str
    city: str
    stars: int
    room_type: Optional[str]
    meal_plan: Optional[str]
    original_text: str


@dataclass
class TourExtraction:
    """Извлечённая экскурсия/тур."""
    canonical_name: str
    tour_type: str
    duration_hours: Optional[int]
    original_text: str


@dataclass
class AttractionExtraction:
    """Извлечённый аттракцион/билет."""
    canonical_name: str
    city: str
    attraction_type: str
    original_text: str


@dataclass
class DateExtraction:
    """Извлечённая дата."""
    date_str: str  # YYYY-MM-DD или текст
    date_type: str  # checkin, checkout, single, range_start, range_end
    nights: Optional[int]
    original_text: str


@dataclass
class PaxExtraction:
    """Извлечённое количество гостей."""
    adults: int
    children: int
    infants: int
    total: int
    original_text: str


@dataclass
class FlightExtraction:
    """Извлечённый рейс."""
    flight_number: str
    airline_code: str
    airline_name: Optional[str]
    airport: Optional[str]
    terminal: Optional[str]
    time: Optional[str]
    original_text: str


@dataclass
class EntityMessage:
    """Сущности из сообщения."""
    jid: str
    timestamp: Optional[str]
    hotels: List[Dict]
    tours: List[Dict]
    attractions: List[Dict]
    dates: List[Dict]
    pax: Optional[Dict]
    flights: List[Dict]


# ===================================================================
# ФУНКЦИИ ИЗВЛЕЧЕНИЯ
# ===================================================================

def extract_hotels(text: str) -> List[HotelExtraction]:
    """Извлекает отели из текста."""
    hotels = []
    text_lower = text.lower()

    for alias, info in HOTELS_UAE.items():
        if alias in text_lower:
            # Ищем тип номера
            room_type = None
            for room_alias, room_name in ROOM_TYPES.items():
                if room_alias in text_lower:
                    room_type = room_name
                    break

            # Ищем тип питания
            meal_plan = None
            for meal_alias, meal_name in MEAL_PLANS.items():
                if meal_alias in text_lower:
                    meal_plan = meal_name
                    break

            hotels.append(HotelExtraction(
                canonical_name=info["canonical"],
                city=info["city"],
                stars=info["stars"],
                room_type=room_type,
                meal_plan=meal_plan,
                original_text=alias
            ))
            break  # Один отель на сообщение

    return hotels


def extract_tours(text: str) -> List[TourExtraction]:
    """Извлекает экскурсии из текста."""
    tours = []
    text_lower = text.lower()

    for alias, info in TOURS_UAE.items():
        if alias in text_lower:
            tours.append(TourExtraction(
                canonical_name=info["canonical"],
                tour_type=info["type"],
                duration_hours=info.get("duration"),
                original_text=alias
            ))

    return tours


def extract_attractions(text: str) -> List[AttractionExtraction]:
    """Извлекает аттракционы из текста."""
    attractions = []
    text_lower = text.lower()

    for alias, info in ATTRACTIONS_UAE.items():
        if alias in text_lower:
            attractions.append(AttractionExtraction(
                canonical_name=info["canonical"],
                city=info.get("city", "Dubai"),
                attraction_type=info["type"],
                original_text=alias
            ))

    return attractions


def extract_dates(text: str) -> List[DateExtraction]:
    """Извлекает даты из текста."""
    dates = []
    current_year = datetime.now().year

    # Диапазон дат (с X по Y месяца)
    for match in PATTERNS['date_range'].finditer(text):
        day_start = int(match.group(1))
        day_end = int(match.group(2))
        month_name = match.group(3).lower()
        month = RUSSIAN_MONTHS.get(month_name, 1)

        dates.append(DateExtraction(
            date_str=f"{current_year}-{month:02d}-{day_start:02d}",
            date_type="checkin",
            nights=day_end - day_start,
            original_text=match.group(0)
        ))
        dates.append(DateExtraction(
            date_str=f"{current_year}-{month:02d}-{day_end:02d}",
            date_type="checkout",
            nights=None,
            original_text=match.group(0)
        ))

    # Check-in / Check-out
    for match in PATTERNS['checkin_checkout'].finditer(text):
        dates.append(DateExtraction(
            date_str=match.group(1),
            date_type="checkin",
            nights=None,
            original_text=match.group(0)
        ))
        dates.append(DateExtraction(
            date_str=match.group(2),
            date_type="checkout",
            nights=None,
            original_text=match.group(0)
        ))

    # Русская дата (15 января)
    for match in PATTERNS['date_ru'].finditer(text):
        day = int(match.group(1))
        month_name = match.group(2).lower()
        month = RUSSIAN_MONTHS.get(month_name, 1)
        year = int(match.group(3)) if match.group(3) else current_year

        dates.append(DateExtraction(
            date_str=f"{year}-{month:02d}-{day:02d}",
            date_type="single",
            nights=None,
            original_text=match.group(0)
        ))

    # Количество ночей
    for match in PATTERNS['nights'].finditer(text):
        nights = int(match.group(1))
        # Добавляем к последней дате если есть
        if dates:
            dates[-1] = DateExtraction(
                date_str=dates[-1].date_str,
                date_type=dates[-1].date_type,
                nights=nights,
                original_text=dates[-1].original_text
            )
        else:
            dates.append(DateExtraction(
                date_str="",
                date_type="nights_only",
                nights=nights,
                original_text=match.group(0)
            ))

    return dates


def extract_pax(text: str) -> Optional[PaxExtraction]:
    """Извлекает количество гостей."""
    adults = 0
    children = 0
    infants = 0

    # Ищем взрослых
    match = PATTERNS['pax_adults'].search(text)
    if match:
        adults = int(match.group(1))

    # Ищем детей
    match = PATTERNS['pax_children'].search(text)
    if match:
        children = int(match.group(1))

    # Ищем младенцев
    match = PATTERNS['pax_infants'].search(text)
    if match:
        infants = int(match.group(1))

    # Формат "2+1+0"
    if adults == 0:
        match = PATTERNS['pax_format'].search(text)
        if match:
            adults = int(match.group(1))
            children = int(match.group(2))
            if match.group(3):
                infants = int(match.group(3))

    # Семья из N
    if adults == 0:
        match = PATTERNS['pax_family'].search(text)
        if match:
            adults = int(match.group(1))

    # Общее количество
    if adults == 0:
        match = PATTERNS['pax_total'].search(text)
        if match:
            adults = int(match.group(1))

    total = adults + children + infants

    if total > 0:
        return PaxExtraction(
            adults=adults,
            children=children,
            infants=infants,
            total=total,
            original_text=f"{adults}+{children}+{infants}"
        )

    return None


def extract_flights(text: str) -> List[FlightExtraction]:
    """Извлекает информацию о рейсах."""
    flights = []

    for match in PATTERNS['flight_code'].finditer(text):
        code = match.group(1).upper()
        number = match.group(2)

        # Проверяем, известный ли код авиакомпании
        airline_name = AIRLINE_CODES.get(code)
        if not airline_name:
            continue  # Пропускаем неизвестные коды

        # Ищем аэропорт
        airport = None
        airport_match = PATTERNS['airport'].search(text)
        if airport_match:
            airport = airport_match.group(1)

        # Ищем терминал
        terminal = None
        terminal_match = PATTERNS['terminal'].search(text)
        if terminal_match:
            terminal = terminal_match.group(1)

        # Ищем время
        time = None
        time_match = PATTERNS['flight_time'].search(text)
        if time_match:
            time = f"{time_match.group(1)}:{time_match.group(2)}"

        flights.append(FlightExtraction(
            flight_number=f"{code}{number}",
            airline_code=code,
            airline_name=airline_name,
            airport=airport,
            terminal=terminal,
            time=time,
            original_text=match.group(0)
        ))

    return flights


# ===================================================================
# КЛАСС АНАЛИЗАТОРА
# ===================================================================

class EntityAnalyzer:
    """Анализатор сущностей в сообщениях."""

    def __init__(self):
        self.entity_messages = []

        # Статистика
        self.stats = {
            'total_messages': 0,
            'messages_with_entities': 0,
            'hotels_found': Counter(),
            'tours_found': Counter(),
            'attractions_found': Counter(),
            'airlines_found': Counter(),
            'room_types_found': Counter(),
            'meal_plans_found': Counter(),
        }

        # Агрегация по контактам
        self.contacts_entities = defaultdict(lambda: {
            'jid': None,
            'name': None,
            'hotels_mentioned': Counter(),
            'tours_mentioned': Counter(),
            'attractions_mentioned': Counter(),
            'flights_count': 0,
            'message_count': 0,
        })

    def process_message(self, msg: Dict[str, Any]):
        """Обрабатывает одно сообщение."""
        jid = msg.get('jid') or msg.get('chat_jid') or msg.get('contact_jid')
        if not jid:
            return

        text = msg.get('text') or msg.get('message') or msg.get('content')
        if not text:
            return

        self.stats['total_messages'] += 1

        # Извлекаем все сущности
        hotels = extract_hotels(text)
        tours = extract_tours(text)
        attractions = extract_attractions(text)
        dates = extract_dates(text)
        pax = extract_pax(text)
        flights = extract_flights(text)

        # Проверяем, есть ли сущности
        has_entities = hotels or tours or attractions or dates or pax or flights

        if not has_entities:
            return

        self.stats['messages_with_entities'] += 1

        # Обновляем статистику
        for h in hotels:
            self.stats['hotels_found'][h.canonical_name] += 1
            if h.room_type:
                self.stats['room_types_found'][h.room_type] += 1
            if h.meal_plan:
                self.stats['meal_plans_found'][h.meal_plan] += 1

        for t in tours:
            self.stats['tours_found'][t.canonical_name] += 1

        for a in attractions:
            self.stats['attractions_found'][a.canonical_name] += 1

        for f in flights:
            self.stats['airlines_found'][f.airline_name or f.airline_code] += 1

        # Создаём запись
        entity_msg = EntityMessage(
            jid=jid,
            timestamp=msg.get('timestamp') or msg.get('date'),
            hotels=[asdict(h) for h in hotels],
            tours=[asdict(t) for t in tours],
            attractions=[asdict(a) for a in attractions],
            dates=[asdict(d) for d in dates],
            pax=asdict(pax) if pax else None,
            flights=[asdict(f) for f in flights],
        )

        self.entity_messages.append(asdict(entity_msg))

        # Обновляем данные контакта
        contact_data = self.contacts_entities[jid]
        contact_data['jid'] = jid
        contact_data['message_count'] += 1

        name = msg.get('name') or msg.get('chat_name')
        if name and not contact_data['name']:
            contact_data['name'] = name

        for h in hotels:
            contact_data['hotels_mentioned'][h.canonical_name] += 1
        for t in tours:
            contact_data['tours_mentioned'][t.canonical_name] += 1
        for a in attractions:
            contact_data['attractions_mentioned'][a.canonical_name] += 1
        contact_data['flights_count'] += len(flights)

    def build_contacts_summary(self) -> List[Dict]:
        """Создаёт сводку по контактам."""
        summaries = []

        for jid, data in self.contacts_entities.items():
            if data['message_count'] == 0:
                continue

            summaries.append({
                'jid': jid,
                'name': data['name'] or jid.split('@')[0],
                'entity_messages_count': data['message_count'],
                'hotels_mentioned': dict(data['hotels_mentioned']),
                'tours_mentioned': dict(data['tours_mentioned']),
                'attractions_mentioned': dict(data['attractions_mentioned']),
                'flights_count': data['flights_count'],
            })

        summaries.sort(key=lambda x: x['entity_messages_count'], reverse=True)
        return summaries

    def build_metadata(self) -> Dict:
        """Создаёт метаданные анализа."""
        return {
            'total_messages_analyzed': self.stats['total_messages'],
            'messages_with_entities': self.stats['messages_with_entities'],
            'top_hotels': dict(self.stats['hotels_found'].most_common(20)),
            'top_tours': dict(self.stats['tours_found'].most_common(20)),
            'top_attractions': dict(self.stats['attractions_found'].most_common(20)),
            'airlines': dict(self.stats['airlines_found']),
            'room_types': dict(self.stats['room_types_found']),
            'meal_plans': dict(self.stats['meal_plans_found']),
            'contacts_with_entities': len(self.contacts_entities),
            'dictionaries': {
                'hotels_count': len(HOTELS_UAE),
                'tours_count': len(TOURS_UAE),
                'attractions_count': len(ATTRACTIONS_UAE),
                'room_types_count': len(ROOM_TYPES),
                'meal_plans_count': len(MEAL_PLANS),
            },
            'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        }


# ===================================================================
# MAIN
# ===================================================================

def main():
    """Основная функция."""
    print("=" * 60)
    print("Извлечение сущностей из сообщений WhatsApp")
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
    analyzer = EntityAnalyzer()

    # Читаем и обрабатываем JSONL
    print("\n[1/3] Извлечение сущностей...")
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

    # Создаём сводку по контактам
    print("\n[2/3] Создание сводки по контактам...")
    contacts_summary = analyzer.build_contacts_summary()
    print(f"  Контактов с сущностями: {len(contacts_summary):,}")

    # Метаданные
    metadata = analyzer.build_metadata()

    # Формируем выходные данные
    output_data = {
        'entity_messages': analyzer.entity_messages[:10000],  # Ограничиваем
        'contacts_summary': contacts_summary,
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
    print(f"Всего сообщений проанализировано: {metadata['total_messages_analyzed']:,}")
    print(f"Сообщений с сущностями: {metadata['messages_with_entities']:,}")
    print(f"\nТоп-10 отелей:")
    for hotel, count in list(metadata['top_hotels'].items())[:10]:
        print(f"  - {hotel}: {count}")
    print(f"\nТоп-10 экскурсий:")
    for tour, count in list(metadata['top_tours'].items())[:10]:
        print(f"  - {tour}: {count}")
    print(f"\nТоп-10 аттракционов:")
    for attr, count in list(metadata['top_attractions'].items())[:10]:
        print(f"  - {attr}: {count}")
    print(f"\nАвиакомпании:")
    for airline, count in metadata['airlines'].items():
        print(f"  - {airline}: {count}")
    print(f"\nСловари:")
    print(f"  - Отелей: {metadata['dictionaries']['hotels_count']}")
    print(f"  - Экскурсий: {metadata['dictionaries']['tours_count']}")
    print(f"  - Аттракционов: {metadata['dictionaries']['attractions_count']}")
    print(f"  - Типов номеров: {metadata['dictionaries']['room_types_count']}")
    print(f"  - Типов питания: {metadata['dictionaries']['meal_plans_count']}")

    print("\n" + "=" * 60)
    print("Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
