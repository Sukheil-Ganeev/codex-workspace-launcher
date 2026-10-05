#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизация маршрутов водителей по точкам пикапа.

Функционал:
1. Извлечение адресов из чатов (отели, районы)
2. Геокодинг через Google Maps API
3. Оптимизация маршрута (TSP)
4. Визуализация карты (Folium)
5. Экспорт для водителей
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

# Установка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')

# Опциональные импорты
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    print("Предупреждение: googlemaps не установлен. pip install googlemaps")

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("Предупреждение: ortools не установлен. pip install ortools")

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Предупреждение: folium не установлен. pip install folium")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Предупреждение: reportlab не установлен. pip install reportlab")

# Локальная конфигурация
try:
    from config import (
        CHATS_DIR, BASE_DIR, JSON_DIR, ANALYTICS_DIR,
        API_KEYS, CONTACT_TYPES
    )
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    BASE_DIR = CHATS_DIR / "_база"
    JSON_DIR = BASE_DIR / "json"
    ANALYTICS_DIR = CHATS_DIR / "_аналитика"
    API_KEYS = {
        'google_maps': os.getenv('GOOGLE_MAPS_API_KEY', ''),
    }
    CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]

# Директории для вывода
ROUTES_DIR = ANALYTICS_DIR / "routes"
MAPS_DIR = ANALYTICS_DIR / "maps"

# ═══════════════════════════════════════════════════════════════
# БАЗА ПОПУЛЯРНЫХ ОТЕЛЕЙ DUBAI/ABU DHABI
# ═══════════════════════════════════════════════════════════════

POPULAR_HOTELS = {
    # Dubai - Palm Jumeirah
    "atlantis the palm": {"lat": 25.1304, "lng": 55.1171, "area": "Palm Jumeirah"},
    "atlantis": {"lat": 25.1304, "lng": 55.1171, "area": "Palm Jumeirah"},
    "one&only the palm": {"lat": 25.1089, "lng": 55.1399, "area": "Palm Jumeirah"},
    "fairmont the palm": {"lat": 25.1122, "lng": 55.1389, "area": "Palm Jumeirah"},
    "sofitel the palm": {"lat": 25.1087, "lng": 55.1327, "area": "Palm Jumeirah"},
    "raffles the palm": {"lat": 25.1127, "lng": 55.1361, "area": "Palm Jumeirah"},
    "waldorf astoria palm": {"lat": 25.0986, "lng": 55.1475, "area": "Palm Jumeirah"},
    "anantara the palm": {"lat": 25.1050, "lng": 55.1413, "area": "Palm Jumeirah"},
    "jumeirah zabeel saray": {"lat": 25.1069, "lng": 55.1314, "area": "Palm Jumeirah"},
    "rixos the palm": {"lat": 25.1154, "lng": 55.1367, "area": "Palm Jumeirah"},
    "five palm jumeirah": {"lat": 25.1179, "lng": 55.1351, "area": "Palm Jumeirah"},
    "viceroy palm jumeirah": {"lat": 25.1179, "lng": 55.1351, "area": "Palm Jumeirah"},
    "kempinski palm jumeirah": {"lat": 25.1087, "lng": 55.1395, "area": "Palm Jumeirah"},

    # Dubai - JBR / Marina
    "jbr": {"lat": 25.0777, "lng": 55.1340, "area": "JBR"},
    "jumeirah beach residence": {"lat": 25.0777, "lng": 55.1340, "area": "JBR"},
    "le royal meridien jbr": {"lat": 25.0797, "lng": 55.1334, "area": "JBR"},
    "hilton jbr": {"lat": 25.0760, "lng": 55.1322, "area": "JBR"},
    "ritz carlton jbr": {"lat": 25.0755, "lng": 55.1305, "area": "JBR"},
    "sofitel jbr": {"lat": 25.0768, "lng": 55.1315, "area": "JBR"},
    "sheraton jbr": {"lat": 25.0808, "lng": 55.1340, "area": "JBR"},
    "ja ocean view": {"lat": 25.0792, "lng": 55.1342, "area": "JBR"},
    "address jbr": {"lat": 25.0765, "lng": 55.1313, "area": "JBR"},
    "grosvenor house": {"lat": 25.0848, "lng": 55.1448, "area": "Marina"},
    "address marina": {"lat": 25.0791, "lng": 55.1413, "area": "Marina"},
    "intercontinental marina": {"lat": 25.0812, "lng": 55.1428, "area": "Marina"},
    "marina walk": {"lat": 25.0776, "lng": 55.1405, "area": "Marina"},

    # Dubai - Downtown / Business Bay
    "burj khalifa": {"lat": 25.1972, "lng": 55.2744, "area": "Downtown"},
    "address downtown": {"lat": 25.1958, "lng": 55.2797, "area": "Downtown"},
    "address sky view": {"lat": 25.1893, "lng": 55.2669, "area": "Downtown"},
    "address fountain views": {"lat": 25.1964, "lng": 55.2787, "area": "Downtown"},
    "armani hotel": {"lat": 25.1972, "lng": 55.2744, "area": "Downtown"},
    "palace downtown": {"lat": 25.1959, "lng": 55.2773, "area": "Downtown"},
    "vida downtown": {"lat": 25.1921, "lng": 55.2807, "area": "Downtown"},
    "rove downtown": {"lat": 25.1935, "lng": 55.2651, "area": "Downtown"},
    "sofitel downtown": {"lat": 25.2063, "lng": 55.2704, "area": "Downtown"},
    "shangri-la dubai": {"lat": 25.2078, "lng": 55.2666, "area": "Downtown"},
    "jw marriott marquis": {"lat": 25.1852, "lng": 55.2622, "area": "Business Bay"},
    "oberoi dubai": {"lat": 25.1862, "lng": 55.2649, "area": "Business Bay"},
    "the st. regis downtown": {"lat": 25.1889, "lng": 55.2702, "area": "Downtown"},

    # Dubai - Jumeirah Beach
    "burj al arab": {"lat": 25.1413, "lng": 55.1852, "area": "Jumeirah Beach"},
    "madinat jumeirah": {"lat": 25.1333, "lng": 55.1849, "area": "Jumeirah Beach"},
    "jumeirah beach hotel": {"lat": 25.1410, "lng": 55.1912, "area": "Jumeirah Beach"},
    "al qasr": {"lat": 25.1330, "lng": 55.1847, "area": "Jumeirah Beach"},
    "mina a'salam": {"lat": 25.1342, "lng": 55.1844, "area": "Jumeirah Beach"},
    "four seasons jumeirah": {"lat": 25.2019, "lng": 55.2407, "area": "Jumeirah Beach"},
    "mandarin oriental jumeirah": {"lat": 25.2018, "lng": 55.2401, "area": "Jumeirah Beach"},
    "bulgari resort dubai": {"lat": 25.2012, "lng": 55.2385, "area": "Jumeirah Beach"},
    "one&only royal mirage": {"lat": 25.0943, "lng": 55.1587, "area": "Jumeirah Beach"},
    "le meridien mina seyahi": {"lat": 25.0926, "lng": 55.1550, "area": "Jumeirah Beach"},
    "westin mina seyahi": {"lat": 25.0936, "lng": 55.1569, "area": "Jumeirah Beach"},

    # Dubai - Creek / Deira / Old Dubai
    "creek": {"lat": 25.2616, "lng": 55.3253, "area": "Creek"},
    "deira": {"lat": 25.2744, "lng": 55.3107, "area": "Deira"},
    "bur dubai": {"lat": 25.2559, "lng": 55.2903, "area": "Bur Dubai"},
    "hilton creek": {"lat": 25.2463, "lng": 55.3235, "area": "Creek"},
    "sheraton creek": {"lat": 25.2479, "lng": 55.3253, "area": "Creek"},
    "park hyatt creek": {"lat": 25.2386, "lng": 55.3395, "area": "Creek"},
    "raffles dubai": {"lat": 25.2289, "lng": 55.3231, "area": "Creek"},

    # Dubai - Other areas
    "city walk": {"lat": 25.2073, "lng": 55.2536, "area": "City Walk"},
    "la mer": {"lat": 25.2300, "lng": 55.2588, "area": "La Mer"},
    "al barsha": {"lat": 25.1138, "lng": 55.1997, "area": "Al Barsha"},
    "mall of emirates": {"lat": 25.1181, "lng": 55.2006, "area": "Al Barsha"},
    "ibn battuta": {"lat": 25.0464, "lng": 55.1183, "area": "Jebel Ali"},

    # Dubai - Airports
    "dxb": {"lat": 25.2532, "lng": 55.3657, "area": "Airport"},
    "dubai airport": {"lat": 25.2532, "lng": 55.3657, "area": "Airport"},
    "dwc": {"lat": 24.8961, "lng": 55.1613, "area": "Airport"},
    "al maktoum airport": {"lat": 24.8961, "lng": 55.1613, "area": "Airport"},

    # Abu Dhabi - Main
    "emirates palace": {"lat": 24.4615, "lng": 54.3174, "area": "Corniche"},
    "louvre abu dhabi": {"lat": 24.5339, "lng": 54.3981, "area": "Saadiyat"},
    "st regis abu dhabi": {"lat": 24.4985, "lng": 54.3877, "area": "Nation Towers"},
    "four seasons abu dhabi": {"lat": 24.5025, "lng": 54.3914, "area": "Al Maryah"},
    "rosewood abu dhabi": {"lat": 24.5015, "lng": 54.3935, "area": "Al Maryah"},
    "shangri-la abu dhabi": {"lat": 24.4612, "lng": 54.3236, "area": "Qaryat al Beri"},
    "ritz carlton abu dhabi": {"lat": 24.4543, "lng": 54.3154, "area": "Grand Canal"},
    "conrad abu dhabi": {"lat": 24.4956, "lng": 54.3854, "area": "Etihad Towers"},
    "jumeirah at etihad towers": {"lat": 24.4963, "lng": 54.3859, "area": "Etihad Towers"},
    "intercontinental abu dhabi": {"lat": 24.4671, "lng": 54.3277, "area": "Corniche"},
    "hilton abu dhabi": {"lat": 24.4656, "lng": 54.3265, "area": "Corniche"},
    "grand hyatt abu dhabi": {"lat": 24.4963, "lng": 54.4102, "area": "West Corniche"},
    "yas island": {"lat": 24.4667, "lng": 54.6017, "area": "Yas Island"},
    "yas viceroy": {"lat": 24.4692, "lng": 54.6055, "area": "Yas Island"},
    "w abu dhabi": {"lat": 24.4667, "lng": 54.6017, "area": "Yas Island"},
    "saadiyat island": {"lat": 24.5437, "lng": 54.4206, "area": "Saadiyat"},
    "park hyatt abu dhabi": {"lat": 24.5499, "lng": 54.4261, "area": "Saadiyat"},
    "st regis saadiyat": {"lat": 24.5480, "lng": 54.4157, "area": "Saadiyat"},

    # Abu Dhabi - Airport
    "auh": {"lat": 24.4330, "lng": 54.6511, "area": "Airport"},
    "abu dhabi airport": {"lat": 24.4330, "lng": 54.6511, "area": "Airport"},
}

# Паттерны для извлечения адресов
ADDRESS_PATTERNS = [
    # Отели
    r'(?:hotel|отель|гостиница)[:\s]*([A-Za-zА-Яа-яёЁ\s\-\']+?)(?:\n|,|\.|\d)',
    r'(?:stay(?:ing)?|живу?т?|проживает?|остановились?)[:\s]+(?:at|в|на)?\s*([A-Za-zА-Яа-яёЁ\s\-\']+?)(?:\n|,|\.|\d)',
    r'(?:from|из|от|с)\s*(?:hotel|отеля?)\s*([A-Za-zА-Яа-яёЁ\s\-\']+?)(?:\n|,|\.|\d)',

    # Прямое упоминание отелей
    r'\b(atlantis(?:\s+the\s+palm)?)\b',
    r'\b(burj\s+al\s+arab)\b',
    r'\b(address\s+(?:downtown|sky\s*view|marina|jbr))\b',
    r'\b((?:jw\s+)?marriott\s+[a-z\s]+)\b',
    r'\b(hilton\s+[a-z\s]+)\b',
    r'\b(sheraton\s+[a-z\s]+)\b',
    r'\b(sofitel\s+[a-z\s]+)\b',
    r'\b(ritz\s+carlton\s+[a-z\s]+)\b',
    r'\b(four\s+seasons\s+[a-z\s]+)\b',
    r'\b(raffles\s+[a-z\s]+)\b',

    # Районы
    r'\b(jbr|jumeirah\s+beach\s+residence)\b',
    r'\b(palm\s+jumeirah|the\s+palm)\b',
    r'\b(marina(?:\s+walk)?)\b',
    r'\b(downtown(?:\s+dubai)?)\b',
    r'\b(business\s+bay)\b',
    r'\b(city\s+walk)\b',
    r'\b(la\s+mer)\b',
    r'\b(deira)\b',
    r'\b(bur\s+dubai)\b',

    # Достопримечательности как точки пикапа
    r'\b(mall\s+of\s+(?:the\s+)?emirates)\b',
    r'\b(dubai\s+mall)\b',
    r'\b(ibn\s+battuta)\b',
    r'\b(global\s+village)\b',
    r'\b(miracle\s+garden)\b',

    # Аэропорты
    r'\b(dxb|dubai\s+(?:international\s+)?airport)\b',
    r'\b(dwc|al\s+maktoum\s+airport)\b',
    r'\b(auh|abu\s+dhabi\s+(?:international\s+)?airport)\b',

    # Адреса с номером здания
    r'(?:building|здание|дом)[:\s]*(\d+[A-Za-z]?)[,\s]+([A-Za-zА-Яа-яёЁ\s\-]+)',

    # Google Maps ссылки
    r'maps\.google\.com/\?q=([\d\.\-]+),([\d\.\-]+)',
    r'goo\.gl/maps/([A-Za-z0-9]+)',
]

# Паттерны для извлечения времени пикапа
TIME_PATTERNS = [
    r'(?:pickup|пикап|забрать|встреча|pick\s*up)[:\s]*(?:at|в|на)?\s*(\d{1,2}[:\.]?\d{0,2})\s*(?:am|pm|утра|вечера|дня)?',
    r'(?:at|в|на)\s*(\d{1,2}[:\.]?\d{0,2})\s*(?:am|pm|утра|вечера|дня)?\s*(?:pickup|пикап|забрать)?',
    r'(\d{1,2}[:\.]?\d{0,2})\s*(?:am|pm|утра|вечера|дня)',
]

# Паттерны для дат бронирования
DATE_PATTERNS = [
    r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{2,4})',
    r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
    r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(\d{1,2})',
]

MONTH_MAP_RU = {
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
    'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
    'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
}

MONTH_MAP_EN = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
    'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
    'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}


# ═══════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class PickupPoint:
    """Точка пикапа"""
    id: str
    name: str                           # Название (отель/адрес)
    address: str = ""                   # Полный адрес
    lat: float = 0.0                    # Широта
    lng: float = 0.0                    # Долгота
    area: str = ""                      # Район
    pickup_time: Optional[str] = None   # Время пикапа (если указано)
    guests: List[str] = field(default_factory=list)  # Имена гостей
    pax: int = 1                        # Количество человек
    phone: str = ""                     # Телефон контакта
    notes: str = ""                     # Примечания
    source_chat: str = ""               # Исходный чат
    booking_date: Optional[str] = None  # Дата бронирования
    geocoded: bool = False              # Прошёл геокодинг


@dataclass
class Route:
    """Оптимизированный маршрут"""
    id: str
    date: str
    driver: str = ""
    vehicle: str = ""
    start_point: Optional[PickupPoint] = None
    end_point: Optional[PickupPoint] = None
    stops: List[PickupPoint] = field(default_factory=list)
    total_distance_km: float = 0.0
    total_duration_min: int = 0
    departure_time: str = ""
    arrival_times: List[str] = field(default_factory=list)
    google_maps_link: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════
# ОСНОВНОЙ КЛАСС
# ═══════════════════════════════════════════════════════════════

class PickupOptimizer:
    """Оптимизатор маршрутов пикапа"""

    def __init__(self, google_api_key: str = None):
        """
        Args:
            google_api_key: API ключ Google Maps (или из env GOOGLE_MAPS_API_KEY)
        """
        self.api_key = google_api_key or os.getenv('GOOGLE_MAPS_API_KEY') or API_KEYS.get('google_maps', '')
        self.gmaps = None

        if self.api_key and GOOGLEMAPS_AVAILABLE:
            try:
                self.gmaps = googlemaps.Client(key=self.api_key)
                print("Google Maps API инициализирован")
            except Exception as e:
                print(f"Ошибка инициализации Google Maps API: {e}")

        # Создаём директории
        ROUTES_DIR.mkdir(parents=True, exist_ok=True)
        MAPS_DIR.mkdir(parents=True, exist_ok=True)

        # Кэш геокодинга
        self.geocode_cache: Dict[str, Dict] = {}
        self._load_geocode_cache()

    def _load_geocode_cache(self):
        """Загрузить кэш геокодинга"""
        cache_file = JSON_DIR / "geocode_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.geocode_cache = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки кэша геокодинга: {e}")

    def _save_geocode_cache(self):
        """Сохранить кэш геокодинга"""
        cache_file = JSON_DIR / "geocode_cache.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.geocode_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения кэша: {e}")

    # ═══════════════════════════════════════════════════════════════
    # 1. ИЗВЛЕЧЕНИЕ АДРЕСОВ ИЗ ЧАТОВ
    # ═══════════════════════════════════════════════════════════════

    def extract_addresses_from_chat(self, chat_content: str, chat_name: str = "") -> List[PickupPoint]:
        """Извлечь адреса из содержимого чата"""
        points = []
        seen_addresses = set()

        # Нормализуем текст
        text_lower = chat_content.lower()

        # 1. Поиск по известным отелям
        for hotel_name, hotel_data in POPULAR_HOTELS.items():
            if hotel_name in text_lower:
                if hotel_name not in seen_addresses:
                    seen_addresses.add(hotel_name)
                    point = PickupPoint(
                        id=f"point_{len(points)+1}",
                        name=hotel_name.title(),
                        lat=hotel_data['lat'],
                        lng=hotel_data['lng'],
                        area=hotel_data['area'],
                        geocoded=True,
                        source_chat=chat_name
                    )
                    points.append(point)

        # 2. Поиск по паттернам
        for pattern in ADDRESS_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Координаты из Google Maps
                    if len(match) == 2 and self._is_coordinate(match[0]):
                        try:
                            lat, lng = float(match[0]), float(match[1])
                            address = f"Координаты: {lat}, {lng}"
                            if address not in seen_addresses:
                                seen_addresses.add(address)
                                points.append(PickupPoint(
                                    id=f"point_{len(points)+1}",
                                    name="Указанная точка",
                                    lat=lat,
                                    lng=lng,
                                    geocoded=True,
                                    source_chat=chat_name
                                ))
                        except ValueError:
                            pass
                    else:
                        address = ' '.join(match).strip()
                else:
                    address = match.strip()

                if address and len(address) > 2 and address not in seen_addresses:
                    # Проверяем в базе отелей
                    normalized = address.lower().strip()
                    if normalized in POPULAR_HOTELS:
                        hotel_data = POPULAR_HOTELS[normalized]
                        seen_addresses.add(normalized)
                        points.append(PickupPoint(
                            id=f"point_{len(points)+1}",
                            name=address.title(),
                            lat=hotel_data['lat'],
                            lng=hotel_data['lng'],
                            area=hotel_data['area'],
                            geocoded=True,
                            source_chat=chat_name
                        ))
                    else:
                        seen_addresses.add(address)
                        points.append(PickupPoint(
                            id=f"point_{len(points)+1}",
                            name=address.title(),
                            address=address,
                            source_chat=chat_name
                        ))

        # 3. Извлечение времени пикапа
        for point in points:
            for pattern in TIME_PATTERNS:
                match = re.search(pattern, chat_content, re.IGNORECASE)
                if match:
                    point.pickup_time = match.group(1)
                    break

        # 4. Извлечение дат
        for point in points:
            for pattern in DATE_PATTERNS:
                match = re.search(pattern, chat_content, re.IGNORECASE)
                if match:
                    try:
                        point.booking_date = self._parse_date(match)
                    except Exception:
                        pass
                    break

        return points

    def _is_coordinate(self, val: str) -> bool:
        """Проверить, является ли строка координатой"""
        try:
            f = float(val)
            return -180 <= f <= 180
        except ValueError:
            return False

    def _parse_date(self, match) -> str:
        """Парсинг даты из match объекта"""
        groups = match.groups()
        if len(groups) >= 2:
            # Проверяем русские месяцы
            if groups[1].lower() in MONTH_MAP_RU:
                day = int(groups[0])
                month = MONTH_MAP_RU[groups[1].lower()]
                year = datetime.now().year
                return f"{year}-{month:02d}-{day:02d}"
            # Английские месяцы
            elif groups[0].lower() in MONTH_MAP_EN:
                month = MONTH_MAP_EN[groups[0].lower()]
                day = int(groups[1])
                year = datetime.now().year
                return f"{year}-{month:02d}-{day:02d}"
            # Числовой формат
            else:
                day = int(groups[0])
                month = int(groups[1])
                year = int(groups[2]) if len(groups) > 2 else datetime.now().year
                if year < 100:
                    year += 2000
                return f"{year}-{month:02d}-{day:02d}"
        return ""

    def extract_from_all_chats(self, date_filter: str = None) -> Dict[str, List[PickupPoint]]:
        """Извлечь адреса из всех чатов"""
        all_points = defaultdict(list)

        for contact_type in CONTACT_TYPES:
            type_dir = CHATS_DIR / contact_type
            if not type_dir.exists():
                continue

            for chat_file in type_dir.glob("*.md"):
                try:
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    points = self.extract_addresses_from_chat(content, chat_file.stem)

                    # Фильтр по дате
                    if date_filter:
                        points = [p for p in points if p.booking_date == date_filter]

                    if points:
                        all_points[chat_file.stem].extend(points)
                except Exception as e:
                    print(f"Ошибка чтения {chat_file}: {e}")

        return dict(all_points)

    # ═══════════════════════════════════════════════════════════════
    # 2. ГЕОКОДИНГ
    # ═══════════════════════════════════════════════════════════════

    def geocode_address(self, address: str, region: str = "ae") -> Optional[Dict]:
        """Геокодинг адреса через Google Maps API"""
        if not address:
            return None

        # Проверяем кэш
        cache_key = address.lower().strip()
        if cache_key in self.geocode_cache:
            return self.geocode_cache[cache_key]

        # Проверяем базу отелей
        if cache_key in POPULAR_HOTELS:
            result = {
                'lat': POPULAR_HOTELS[cache_key]['lat'],
                'lng': POPULAR_HOTELS[cache_key]['lng'],
                'formatted_address': f"{address.title()}, {POPULAR_HOTELS[cache_key]['area']}, UAE",
                'area': POPULAR_HOTELS[cache_key]['area']
            }
            self.geocode_cache[cache_key] = result
            return result

        # API запрос
        if not self.gmaps:
            print(f"Google Maps API недоступен для геокодинга: {address}")
            return None

        try:
            # Добавляем регион для лучших результатов
            search_address = f"{address}, UAE"
            result = self.gmaps.geocode(search_address, region=region)

            if result:
                location = result[0]['geometry']['location']
                geocoded = {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': result[0].get('formatted_address', ''),
                    'place_id': result[0].get('place_id', ''),
                }

                # Кэшируем
                self.geocode_cache[cache_key] = geocoded
                self._save_geocode_cache()

                return geocoded
        except Exception as e:
            print(f"Ошибка геокодинга '{address}': {e}")

        return None

    def geocode_points(self, points: List[PickupPoint]) -> List[PickupPoint]:
        """Геокодинг всех точек"""
        for point in points:
            if point.geocoded:
                continue

            # Пробуем геокодить
            address_to_geocode = point.address or point.name
            result = self.geocode_address(address_to_geocode)

            if result:
                point.lat = result['lat']
                point.lng = result['lng']
                point.address = result.get('formatted_address', point.address)
                point.area = result.get('area', '')
                point.geocoded = True

        return points

    # ═══════════════════════════════════════════════════════════════
    # 3. ОПТИМИЗАЦИЯ МАРШРУТА (TSP)
    # ═══════════════════════════════════════════════════════════════

    def get_distance_matrix(self, points: List[PickupPoint], mode: str = "driving") -> Optional[Dict]:
        """Получить матрицу расстояний через Google Distance Matrix API"""
        if not self.gmaps or not points:
            return None

        # Формируем координаты
        locations = [(p.lat, p.lng) for p in points if p.geocoded]
        if len(locations) < 2:
            return None

        try:
            # Используем departure_time для учёта пробок
            departure_time = datetime.now() + timedelta(hours=1)

            result = self.gmaps.distance_matrix(
                origins=locations,
                destinations=locations,
                mode=mode,
                departure_time=departure_time,
                traffic_model="best_guess"
            )

            return result
        except Exception as e:
            print(f"Ошибка Distance Matrix API: {e}")
            return None

    def _create_distance_matrix_from_api(self, api_result: Dict) -> List[List[int]]:
        """Создать матрицу расстояний из ответа API"""
        matrix = []
        for row in api_result.get('rows', []):
            row_data = []
            for element in row.get('elements', []):
                if element['status'] == 'OK':
                    # Используем duration_in_traffic если доступно
                    duration = element.get('duration_in_traffic', element.get('duration', {}))
                    row_data.append(duration.get('value', 9999999))
                else:
                    row_data.append(9999999)
            matrix.append(row_data)
        return matrix

    def _create_simple_distance_matrix(self, points: List[PickupPoint]) -> List[List[int]]:
        """Создать простую матрицу расстояний (евклидово расстояние)"""
        from math import radians, sin, cos, sqrt, atan2

        def haversine(lat1, lon1, lat2, lon2):
            """Расстояние между точками в метрах"""
            R = 6371000  # Радиус Земли в метрах
            phi1, phi2 = radians(lat1), radians(lat2)
            delta_phi = radians(lat2 - lat1)
            delta_lambda = radians(lon2 - lon1)
            a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        n = len(points)
        matrix = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = haversine(
                        points[i].lat, points[i].lng,
                        points[j].lat, points[j].lng
                    )
                    # Конвертируем в примерное время (секунды) со скоростью 40 км/ч
                    matrix[i][j] = int(dist / 40000 * 3600)

        return matrix

    def solve_tsp(self, points: List[PickupPoint], start_index: int = 0) -> List[int]:
        """Решить задачу коммивояжёра с помощью OR-Tools"""
        if not ORTOOLS_AVAILABLE:
            print("OR-Tools не установлен, возвращаем исходный порядок")
            return list(range(len(points)))

        if len(points) < 2:
            return list(range(len(points)))

        # Получаем матрицу расстояний
        api_result = self.get_distance_matrix(points)
        if api_result:
            distance_matrix = self._create_distance_matrix_from_api(api_result)
        else:
            distance_matrix = self._create_simple_distance_matrix(points)

        # Создаём модель
        manager = pywrapcp.RoutingIndexManager(len(points), 1, start_index)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Параметры поиска
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30

        # Решаем
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            route = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            return route
        else:
            print("Не удалось найти оптимальный маршрут")
            return list(range(len(points)))

    def optimize_route(self, points: List[PickupPoint],
                       start_point: PickupPoint = None,
                       departure_time: str = "08:00") -> Route:
        """Оптимизировать маршрут"""
        # Геокодим точки
        points = self.geocode_points(points)

        # Фильтруем только геокодированные точки
        valid_points = [p for p in points if p.geocoded]
        if not valid_points:
            print("Нет точек с координатами")
            return None

        # Добавляем стартовую точку если указана
        all_points = [start_point] + valid_points if start_point and start_point.geocoded else valid_points

        # Решаем TSP
        order = self.solve_tsp(all_points)

        # Создаём маршрут
        ordered_stops = [all_points[i] for i in order]

        route = Route(
            id=f"route_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            date=datetime.now().strftime('%Y-%m-%d'),
            start_point=ordered_stops[0] if ordered_stops else None,
            stops=ordered_stops[1:] if len(ordered_stops) > 1 else ordered_stops,
            departure_time=departure_time
        )

        # Рассчитываем расстояние и время
        route = self._calculate_route_stats(route)

        # Генерируем Google Maps ссылку
        route.google_maps_link = self._generate_google_maps_link(ordered_stops)

        return route

    def _calculate_route_stats(self, route: Route) -> Route:
        """Рассчитать статистику маршрута"""
        all_stops = [route.start_point] + route.stops if route.start_point else route.stops

        if len(all_stops) < 2 or not self.gmaps:
            return route

        try:
            # Получаем маршрут через Directions API
            waypoints = [(p.lat, p.lng) for p in all_stops[1:-1]] if len(all_stops) > 2 else None

            result = self.gmaps.directions(
                origin=(all_stops[0].lat, all_stops[0].lng),
                destination=(all_stops[-1].lat, all_stops[-1].lng),
                waypoints=waypoints,
                optimize_waypoints=False,  # Уже оптимизировано
                mode="driving",
                departure_time=datetime.now() + timedelta(hours=1)
            )

            if result:
                leg_data = result[0]['legs']
                total_distance = sum(leg['distance']['value'] for leg in leg_data)
                total_duration = sum(leg.get('duration_in_traffic', leg['duration'])['value'] for leg in leg_data)

                route.total_distance_km = round(total_distance / 1000, 1)
                route.total_duration_min = round(total_duration / 60)

                # Рассчитываем время прибытия
                route.arrival_times = self._calculate_arrival_times(
                    route.departure_time,
                    leg_data
                )

        except Exception as e:
            print(f"Ошибка расчёта маршрута: {e}")

        return route

    def _calculate_arrival_times(self, departure: str, legs: List[Dict]) -> List[str]:
        """Рассчитать время прибытия на каждую точку"""
        try:
            # Парсим время отправления
            h, m = map(int, departure.split(':'))
            current_time = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)

            arrival_times = [departure]  # Время старта

            for leg in legs:
                duration = leg.get('duration_in_traffic', leg['duration'])['value']
                current_time += timedelta(seconds=duration)
                arrival_times.append(current_time.strftime('%H:%M'))

            return arrival_times
        except Exception:
            return []

    def _generate_google_maps_link(self, points: List[PickupPoint]) -> str:
        """Генерировать ссылку на Google Maps"""
        if not points:
            return ""

        base_url = "https://www.google.com/maps/dir/"

        coords = []
        for p in points:
            if p.geocoded:
                coords.append(f"{p.lat},{p.lng}")

        if coords:
            return base_url + "/".join(coords)

        return ""

    # ═══════════════════════════════════════════════════════════════
    # 4. ВИЗУАЛИЗАЦИЯ (FOLIUM)
    # ═══════════════════════════════════════════════════════════════

    def create_route_map(self, route: Route, output_file: str = None) -> str:
        """Создать карту маршрута с помощью Folium"""
        if not FOLIUM_AVAILABLE:
            print("Folium не установлен")
            return ""

        all_stops = [route.start_point] + route.stops if route.start_point else route.stops
        if not all_stops:
            return ""

        # Центр карты
        center_lat = sum(p.lat for p in all_stops if p.geocoded) / len(all_stops)
        center_lng = sum(p.lng for p in all_stops if p.geocoded) / len(all_stops)

        # Создаём карту
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=12,
            tiles='cartodbpositron'
        )

        # Цвета для маркеров
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
                  'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue']

        # Добавляем маркеры
        for i, point in enumerate(all_stops):
            if not point.geocoded:
                continue

            # Время прибытия
            arrival = route.arrival_times[i] if i < len(route.arrival_times) else "N/A"

            # Popup содержимое
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0;">#{i+1} {point.name}</h4>
                <p><b>Время прибытия:</b> {arrival}</p>
                <p><b>Район:</b> {point.area or 'N/A'}</p>
                <p><b>Гости:</b> {', '.join(point.guests) if point.guests else 'N/A'}</p>
                <p><b>Кол-во:</b> {point.pax} чел.</p>
                {f'<p><b>Телефон:</b> {point.phone}</p>' if point.phone else ''}
                {f'<p><b>Примечание:</b> {point.notes}</p>' if point.notes else ''}
            </div>
            """

            # Стартовая точка - особый маркер
            if i == 0:
                folium.Marker(
                    location=[point.lat, point.lng],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color='green', icon='play', prefix='fa'),
                    tooltip=f"СТАРТ: {point.name}"
                ).add_to(m)
            else:
                folium.Marker(
                    location=[point.lat, point.lng],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.DivIcon(
                        html=f'<div style="background-color: {colors[i % len(colors)]}; color: white; '
                             f'width: 25px; height: 25px; border-radius: 50%; text-align: center; '
                             f'line-height: 25px; font-weight: bold;">{i}</div>'
                    ),
                    tooltip=f"#{i}: {point.name} ({arrival})"
                ).add_to(m)

        # Линия маршрута
        coords = [(p.lat, p.lng) for p in all_stops if p.geocoded]
        if len(coords) >= 2:
            folium.PolyLine(
                locations=coords,
                weight=4,
                color='blue',
                opacity=0.7,
                dash_array='10'
            ).add_to(m)

            # Стрелки направления
            plugins.AntPath(
                locations=coords,
                color='blue',
                weight=2,
                opacity=0.6,
                dash_array=[10, 20]
            ).add_to(m)

        # Информация о маршруте
        info_html = f"""
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                    background: white; padding: 15px; border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: Arial;">
            <h4 style="margin: 0 0 10px 0;">Маршрут {route.date}</h4>
            <p><b>Водитель:</b> {route.driver or 'Не назначен'}</p>
            <p><b>Отправление:</b> {route.departure_time}</p>
            <p><b>Расстояние:</b> {route.total_distance_km} км</p>
            <p><b>Время в пути:</b> {route.total_duration_min} мин</p>
            <p><b>Остановок:</b> {len(all_stops)}</p>
            <a href="{route.google_maps_link}" target="_blank"
               style="display: block; margin-top: 10px; padding: 8px;
                      background: #4285f4; color: white; text-align: center;
                      text-decoration: none; border-radius: 4px;">
                Открыть в Google Maps
            </a>
        </div>
        """
        m.get_root().html.add_child(folium.Element(info_html))

        # Сохраняем
        if not output_file:
            output_file = str(MAPS_DIR / f"route_{route.id}.html")

        m.save(output_file)
        print(f"Карта сохранена: {output_file}")
        return output_file

    # ═══════════════════════════════════════════════════════════════
    # 5. ЭКСПОРТ
    # ═══════════════════════════════════════════════════════════════

    def export_route_pdf(self, route: Route, output_file: str = None) -> str:
        """Экспорт маршрута в PDF"""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab не установлен")
            return ""

        if not output_file:
            output_file = str(ROUTES_DIR / f"route_{route.id}.pdf")

        # Регистрируем шрифт для кириллицы
        try:
            # Пробуем использовать системный шрифт
            font_path = "C:/Windows/Fonts/arial.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                font_name = 'Arial'
            else:
                font_name = 'Helvetica'
        except Exception:
            font_name = 'Helvetica'

        doc = SimpleDocTemplate(output_file, pagesize=A4)
        story = []

        styles = getSampleStyleSheet()

        # Заголовок
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            spaceAfter=20
        )
        story.append(Paragraph(f"Маршрут на {route.date}", title_style))

        # Информация о маршруте
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            spaceAfter=5
        )

        info_lines = [
            f"<b>Водитель:</b> {route.driver or 'Не назначен'}",
            f"<b>Транспорт:</b> {route.vehicle or 'Не указан'}",
            f"<b>Отправление:</b> {route.departure_time}",
            f"<b>Расстояние:</b> {route.total_distance_km} км",
            f"<b>Примерное время:</b> {route.total_duration_min} мин",
        ]

        for line in info_lines:
            story.append(Paragraph(line, info_style))

        story.append(Spacer(1, 20))

        # Таблица остановок
        all_stops = [route.start_point] + route.stops if route.start_point else route.stops

        table_data = [['#', 'Время', 'Место', 'Гости', 'Телефон']]

        for i, point in enumerate(all_stops):
            arrival = route.arrival_times[i] if i < len(route.arrival_times) else "N/A"
            table_data.append([
                str(i + 1),
                arrival,
                point.name[:30] + ('...' if len(point.name) > 30 else ''),
                ', '.join(point.guests)[:20] if point.guests else '-',
                point.phone or '-'
            ])

        table = Table(table_data, colWidths=[30, 50, 150, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        story.append(table)
        story.append(Spacer(1, 20))

        # Ссылка на карту
        link_style = ParagraphStyle(
            'Link',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.blue
        )
        if route.google_maps_link:
            story.append(Paragraph(
                f'<a href="{route.google_maps_link}">Открыть маршрут в Google Maps</a>',
                link_style
            ))

        # Генерируем PDF
        doc.build(story)
        print(f"PDF сохранён: {output_file}")
        return output_file

    def export_for_whatsapp(self, route: Route) -> str:
        """Экспорт маршрута для WhatsApp"""
        all_stops = [route.start_point] + route.stops if route.start_point else route.stops

        lines = [
            f"*Маршрут на {route.date}*",
            f"",
            f"Водитель: {route.driver or 'Не назначен'}",
            f"Отправление: {route.departure_time}",
            f"Расстояние: {route.total_distance_km} км",
            f"Время в пути: ~{route.total_duration_min} мин",
            f"",
            "*Остановки:*"
        ]

        for i, point in enumerate(all_stops):
            arrival = route.arrival_times[i] if i < len(route.arrival_times) else "N/A"
            line = f"{i+1}. {arrival} - {point.name}"
            if point.pax > 1:
                line += f" ({point.pax} чел.)"
            lines.append(line)

        lines.extend([
            "",
            "*Карта маршрута:*",
            route.google_maps_link
        ])

        return "\n".join(lines)

    def export_for_telegram(self, route: Route) -> str:
        """Экспорт маршрута для Telegram (HTML формат)"""
        all_stops = [route.start_point] + route.stops if route.start_point else route.stops

        lines = [
            f"<b>Маршрут на {route.date}</b>",
            f"",
            f"Водитель: {route.driver or 'Не назначен'}",
            f"Отправление: {route.departure_time}",
            f"Расстояние: {route.total_distance_km} км",
            f"Время в пути: ~{route.total_duration_min} мин",
            f"",
            "<b>Остановки:</b>"
        ]

        for i, point in enumerate(all_stops):
            arrival = route.arrival_times[i] if i < len(route.arrival_times) else "N/A"
            line = f"{i+1}. <code>{arrival}</code> - {point.name}"
            if point.pax > 1:
                line += f" ({point.pax} чел.)"
            if point.phone:
                line += f" 📞 {point.phone}"
            lines.append(line)

        lines.extend([
            "",
            f'<a href="{route.google_maps_link}">📍 Открыть карту</a>'
        ])

        return "\n".join(lines)

    def save_route_json(self, route: Route, output_file: str = None) -> str:
        """Сохранить маршрут в JSON"""
        if not output_file:
            output_file = str(ROUTES_DIR / f"route_{route.id}.json")

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        data = {
            'id': route.id,
            'date': route.date,
            'driver': route.driver,
            'vehicle': route.vehicle,
            'departure_time': route.departure_time,
            'total_distance_km': route.total_distance_km,
            'total_duration_min': route.total_duration_min,
            'google_maps_link': route.google_maps_link,
            'created_at': route.created_at,
            'stops': []
        }

        all_stops = [route.start_point] + route.stops if route.start_point else route.stops
        for i, point in enumerate(all_stops):
            stop_data = asdict(point)
            stop_data['arrival_time'] = route.arrival_times[i] if i < len(route.arrival_times) else None
            stop_data['order'] = i + 1
            data['stops'].append(stop_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"JSON сохранён: {output_file}")
        return output_file

    # ═══════════════════════════════════════════════════════════════
    # 6. ИНТЕГРАЦИЯ С БРОНИРОВАНИЯМИ
    # ═══════════════════════════════════════════════════════════════

    def group_by_date(self, points: List[PickupPoint]) -> Dict[str, List[PickupPoint]]:
        """Группировка точек по датам бронирования"""
        grouped = defaultdict(list)

        for point in points:
            date_key = point.booking_date or "no_date"
            grouped[date_key].append(point)

        return dict(grouped)

    def assign_driver(self, route: Route, driver_name: str, vehicle: str = "") -> Route:
        """Назначить водителя на маршрут"""
        route.driver = driver_name
        route.vehicle = vehicle
        return route

    def create_daily_routes(self, date: str, max_points_per_route: int = 8) -> List[Route]:
        """Создать маршруты на день"""
        # Извлекаем все точки на дату
        all_points_by_chat = self.extract_from_all_chats(date_filter=date)

        # Объединяем все точки
        all_points = []
        for points in all_points_by_chat.values():
            all_points.extend(points)

        if not all_points:
            print(f"Нет точек пикапа на {date}")
            return []

        # Геокодим
        all_points = self.geocode_points(all_points)

        # Фильтруем только геокодированные
        valid_points = [p for p in all_points if p.geocoded]

        # Разбиваем на маршруты если много точек
        routes = []
        for i in range(0, len(valid_points), max_points_per_route):
            chunk = valid_points[i:i + max_points_per_route]
            route = self.optimize_route(chunk)
            if route:
                route.date = date
                routes.append(route)

        return routes


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Оптимизация маршрутов пикапа",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # extract - извлечение адресов
    extract_parser = subparsers.add_parser('extract', help='Извлечь адреса из чатов')
    extract_parser.add_argument('--date', help='Фильтр по дате (YYYY-MM-DD)')
    extract_parser.add_argument('--chat', help='Конкретный файл чата')
    extract_parser.add_argument('-o', '--output', help='Файл для сохранения JSON')

    # optimize - оптимизация маршрута
    optimize_parser = subparsers.add_parser('optimize', help='Оптимизировать маршрут')
    optimize_parser.add_argument('--date', required=True, help='Дата (YYYY-MM-DD)')
    optimize_parser.add_argument('--departure', default='08:00', help='Время отправления (HH:MM)')
    optimize_parser.add_argument('--driver', help='Имя водителя')
    optimize_parser.add_argument('--vehicle', help='Транспортное средство')
    optimize_parser.add_argument('-o', '--output', help='Директория для вывода')

    # map - создание карты
    map_parser = subparsers.add_parser('map', help='Создать карту маршрута')
    map_parser.add_argument('route_json', help='JSON файл маршрута')
    map_parser.add_argument('-o', '--output', help='Файл HTML карты')

    # export - экспорт
    export_parser = subparsers.add_parser('export', help='Экспорт маршрута')
    export_parser.add_argument('route_json', help='JSON файл маршрута')
    export_parser.add_argument('--format', choices=['pdf', 'whatsapp', 'telegram', 'all'],
                               default='all', help='Формат экспорта')
    export_parser.add_argument('-o', '--output', help='Директория/файл вывода')

    # demo - демонстрация
    demo_parser = subparsers.add_parser('demo', help='Демонстрация с тестовыми данными')

    args = parser.parse_args()

    # Инициализация
    optimizer = PickupOptimizer()

    if args.command == 'extract':
        if args.chat:
            # Один чат
            with open(args.chat, 'r', encoding='utf-8') as f:
                content = f.read()
            points = optimizer.extract_addresses_from_chat(content, Path(args.chat).stem)
        else:
            # Все чаты
            all_points = optimizer.extract_from_all_chats(date_filter=args.date)
            points = []
            for chat_points in all_points.values():
                points.extend(chat_points)

        print(f"\nНайдено {len(points)} точек пикапа:")
        for p in points:
            print(f"  - {p.name} ({p.area or 'район неизвестен'})")
            if p.booking_date:
                print(f"    Дата: {p.booking_date}")
            if p.pickup_time:
                print(f"    Время: {p.pickup_time}")

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump([asdict(p) for p in points], f, ensure_ascii=False, indent=2)
            print(f"\nСохранено в {args.output}")

    elif args.command == 'optimize':
        routes = optimizer.create_daily_routes(args.date)

        if not routes:
            print("Не удалось создать маршруты")
            return

        for i, route in enumerate(routes):
            route.departure_time = args.departure
            if args.driver:
                route.driver = args.driver
            if args.vehicle:
                route.vehicle = args.vehicle

            print(f"\n=== Маршрут #{i+1} ===")
            print(f"Дата: {route.date}")
            print(f"Отправление: {route.departure_time}")
            print(f"Расстояние: {route.total_distance_km} км")
            print(f"Время: {route.total_duration_min} мин")

            # Сохраняем
            output_dir = Path(args.output) if args.output else ROUTES_DIR
            output_dir.mkdir(parents=True, exist_ok=True)

            optimizer.save_route_json(route, str(output_dir / f"route_{route.id}.json"))
            optimizer.create_route_map(route, str(output_dir / f"route_{route.id}.html"))
            optimizer.export_route_pdf(route, str(output_dir / f"route_{route.id}.pdf"))

            print(f"\nGoogle Maps: {route.google_maps_link}")

    elif args.command == 'map':
        with open(args.route_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Восстанавливаем Route из JSON
        route = Route(
            id=data['id'],
            date=data['date'],
            driver=data.get('driver', ''),
            vehicle=data.get('vehicle', ''),
            departure_time=data.get('departure_time', ''),
            total_distance_km=data.get('total_distance_km', 0),
            total_duration_min=data.get('total_duration_min', 0),
            google_maps_link=data.get('google_maps_link', ''),
            arrival_times=[s.get('arrival_time') for s in data.get('stops', [])]
        )

        # Восстанавливаем точки
        stops = []
        for stop_data in data.get('stops', []):
            point = PickupPoint(
                id=stop_data.get('id', ''),
                name=stop_data.get('name', ''),
                lat=stop_data.get('lat', 0),
                lng=stop_data.get('lng', 0),
                area=stop_data.get('area', ''),
                geocoded=True
            )
            stops.append(point)

        route.start_point = stops[0] if stops else None
        route.stops = stops[1:] if len(stops) > 1 else []

        output = args.output or str(MAPS_DIR / f"route_{route.id}.html")
        optimizer.create_route_map(route, output)

    elif args.command == 'export':
        with open(args.route_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Восстанавливаем Route
        route = Route(
            id=data['id'],
            date=data['date'],
            driver=data.get('driver', ''),
            vehicle=data.get('vehicle', ''),
            departure_time=data.get('departure_time', ''),
            total_distance_km=data.get('total_distance_km', 0),
            total_duration_min=data.get('total_duration_min', 0),
            google_maps_link=data.get('google_maps_link', ''),
            arrival_times=[s.get('arrival_time') for s in data.get('stops', [])]
        )

        stops = []
        for stop_data in data.get('stops', []):
            point = PickupPoint(
                id=stop_data.get('id', ''),
                name=stop_data.get('name', ''),
                lat=stop_data.get('lat', 0),
                lng=stop_data.get('lng', 0),
                area=stop_data.get('area', ''),
                phone=stop_data.get('phone', ''),
                pax=stop_data.get('pax', 1),
                guests=stop_data.get('guests', []),
                geocoded=True
            )
            stops.append(point)

        route.start_point = stops[0] if stops else None
        route.stops = stops[1:] if len(stops) > 1 else []

        if args.format in ['pdf', 'all']:
            output = args.output if args.output and args.format == 'pdf' else None
            optimizer.export_route_pdf(route, output)

        if args.format in ['whatsapp', 'all']:
            text = optimizer.export_for_whatsapp(route)
            print("\n=== WhatsApp ===")
            print(text)

        if args.format in ['telegram', 'all']:
            text = optimizer.export_for_telegram(route)
            print("\n=== Telegram ===")
            print(text)

    elif args.command == 'demo':
        print("=== Демонстрация оптимизатора маршрутов ===\n")

        # Тестовые точки
        test_points = [
            PickupPoint(id="1", name="Atlantis The Palm", lat=25.1304, lng=55.1171,
                        area="Palm Jumeirah", pax=2, guests=["Иванов А."], geocoded=True),
            PickupPoint(id="2", name="Burj Al Arab", lat=25.1413, lng=55.1852,
                        area="Jumeirah Beach", pax=4, guests=["Петровы"], geocoded=True),
            PickupPoint(id="3", name="Address Downtown", lat=25.1958, lng=55.2797,
                        area="Downtown", pax=2, guests=["Smith J."], geocoded=True),
            PickupPoint(id="4", name="JW Marriott Marquis", lat=25.1852, lng=55.2622,
                        area="Business Bay", pax=3, guests=["Сидоров"], geocoded=True),
            PickupPoint(id="5", name="Le Royal Meridien JBR", lat=25.0797, lng=55.1334,
                        area="JBR", pax=2, guests=["Козлов"], geocoded=True),
        ]

        print(f"Тестовых точек: {len(test_points)}")
        for p in test_points:
            print(f"  - {p.name} ({p.area}): {p.pax} чел.")

        # Оптимизация
        print("\nОптимизация маршрута...")
        route = optimizer.optimize_route(test_points, departure_time="08:30")

        if route:
            route.driver = "Ахмед"
            route.vehicle = "Toyota Hiace"

            print(f"\n=== Результат ===")
            print(f"Расстояние: {route.total_distance_km} км")
            print(f"Время в пути: {route.total_duration_min} мин")

            print("\nПорядок остановок:")
            all_stops = [route.start_point] + route.stops if route.start_point else route.stops
            for i, stop in enumerate(all_stops):
                arrival = route.arrival_times[i] if i < len(route.arrival_times) else "N/A"
                print(f"  {i+1}. {arrival} - {stop.name} ({stop.area})")

            print(f"\nGoogle Maps: {route.google_maps_link}")

            # Сохраняем
            optimizer.save_route_json(route)
            optimizer.create_route_map(route)

            print("\n=== WhatsApp сообщение ===")
            print(optimizer.export_for_whatsapp(route))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
