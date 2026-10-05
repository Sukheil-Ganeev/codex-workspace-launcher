#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение GPS локаций из WhatsApp чатов.

Вход: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выход:
  - D:/Downloads/Chats/_база/json/locations.json
  - D:/Downloads/Chats/_база/json/locations_clusters.json
  - D:/Downloads/Chats/_аналитика/locations_map.html
  - D:/Downloads/Chats/_база/csv/locations.csv
  - D:/Downloads/Chats/_база/json/locations.geojson
  - D:/Downloads/Chats/_база/json/locations.kml

Функции:
- Парсинг shared locations из WhatsApp (maps.google.com/?q=lat,lng)
- Извлечение координат из текста сообщений
- Reverse geocoding (координаты -> адрес)
- Кластеризация частых мест (DBSCAN)
- Интерактивная карта (Folium)
- Связь локаций с контактами
- Экспорт: GeoJSON, KML, CSV

Использование:
    python extract_locations.py [--geocode] [--cluster] [--map]
    python extract_locations.py --all
"""

import json
import re
import sys
import csv
import math
import hashlib
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse, parse_qs
import argparse

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    RAW_DIR, JSON_DIR, CSV_DIR, ANALYTICS_DIR,
    ensure_directories
)

# Настройка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

INPUT_FILE = RAW_DIR / "all_messages.jsonl"

# Выходные файлы
OUTPUT_JSON = JSON_DIR / "locations.json"
OUTPUT_CLUSTERS = JSON_DIR / "locations_clusters.json"
OUTPUT_MAP = ANALYTICS_DIR / "locations_map.html"
OUTPUT_CSV = CSV_DIR / "locations.csv"
OUTPUT_GEOJSON = JSON_DIR / "locations.geojson"
OUTPUT_KML = JSON_DIR / "locations.kml"

# Границы ОАЭ для валидации координат
UAE_BOUNDS = {
    'min_lat': 22.5,
    'max_lat': 26.5,
    'min_lng': 51.0,
    'max_lng': 56.5
}

# Расширенные границы (включая соседние страны)
EXTENDED_BOUNDS = {
    'min_lat': 20.0,
    'max_lat': 30.0,
    'min_lng': 45.0,
    'max_lng': 60.0
}

# Параметры кластеризации
CLUSTER_RADIUS_KM = 0.5  # Радиус кластера в км
MIN_CLUSTER_POINTS = 2   # Минимум точек для кластера


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ИЗВЛЕЧЕНИЯ ЛОКАЦИЙ
# ═══════════════════════════════════════════════════════════════

# Google Maps ссылки
GOOGLE_MAPS_PATTERNS = [
    # https://maps.google.com/?q=25.2048,55.2708
    re.compile(r'https?://(?:www\.)?maps\.google\.com/?\?q=(-?\d+\.?\d*),(-?\d+\.?\d*)'),
    # https://www.google.com/maps?q=25.2048,55.2708
    re.compile(r'https?://(?:www\.)?google\.com/maps\?q=(-?\d+\.?\d*),(-?\d+\.?\d*)'),
    # https://www.google.com/maps/place/.../@25.2048,55.2708
    re.compile(r'https?://(?:www\.)?google\.com/maps/place/[^@]*@(-?\d+\.?\d*),(-?\d+\.?\d*)'),
    # https://goo.gl/maps/... (короткая ссылка - нужен запрос)
    re.compile(r'(https?://goo\.gl/maps/[A-Za-z0-9]+)'),
    # https://maps.app.goo.gl/...
    re.compile(r'(https?://maps\.app\.goo\.gl/[A-Za-z0-9]+)'),
]

# WhatsApp location format
WHATSAPP_LOCATION_PATTERN = re.compile(
    r'\[ЛОКАЦИЯ\]\s*https?://maps\.google\.com/?\?q=(-?\d+\.?\d*),(-?\d+\.?\d*)'
)

# Координаты в тексте
COORDS_IN_TEXT_PATTERNS = [
    # "25.2048, 55.2708" или "25.2048,55.2708"
    re.compile(r'\b(-?\d{1,2}\.\d{4,8})\s*,\s*(-?\d{1,3}\.\d{4,8})\b'),
    # "lat: 25.2048, lng: 55.2708"
    re.compile(r'lat[:\s]+(-?\d+\.?\d*)\s*[,;]\s*l(?:ng|on)[:\s]+(-?\d+\.?\d*)'),
    # GPS: 25.2048, 55.2708
    re.compile(r'GPS[:\s]+(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)'),
]

# Известные адреса/места в ОАЭ
UAE_LOCATION_KEYWORDS = {
    'dubai': (25.2048, 55.2708),
    'abu dhabi': (24.4539, 54.3773),
    'sharjah': (25.3573, 55.4033),
    'ajman': (25.4052, 55.5136),
    'ras al khaimah': (25.7895, 55.9432),
    'fujairah': (25.1288, 56.3265),
    'umm al quwain': (25.5647, 55.5553),
    'burj khalifa': (25.1972, 55.2744),
    'dubai mall': (25.1985, 55.2796),
    'atlantis': (25.1304, 55.1171),
    'palm jumeirah': (25.1124, 55.1390),
    'jbr': (25.0769, 55.1337),
    'marina': (25.0762, 55.1400),
    'deira': (25.2712, 55.3156),
    'airport': (25.2528, 55.3644),  # DXB
    'dxb': (25.2528, 55.3644),
}


# ═══════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class Location:
    """Извлечённая локация."""
    location_id: str
    lat: float
    lng: float
    source_type: str  # whatsapp_shared, google_maps_link, text_coords, inferred
    raw_text: str = ""
    address: str = ""
    place_name: str = ""
    timestamp: str = ""
    jid: str = ""
    contact_name: str = ""
    message_id: str = ""
    is_from_me: bool = False
    cluster_id: Optional[int] = None
    geocoded: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LocationCluster:
    """Кластер локаций (частое место)."""
    cluster_id: int
    center_lat: float
    center_lng: float
    locations_count: int
    address: str = ""
    place_name: str = ""
    contacts: List[str] = field(default_factory=list)
    first_visit: str = ""
    last_visit: str = ""
    visit_count_by_contact: Dict[str, int] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def generate_location_id(lat: float, lng: float, timestamp: str) -> str:
    """Генерация уникального ID для локации."""
    data = f"{lat:.6f},{lng:.6f},{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()[:12]


def is_valid_coordinate(lat: float, lng: float, strict: bool = False) -> bool:
    """Проверка валидности координат."""
    # Базовая проверка
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return False

    # Проверка на нулевые координаты
    if lat == 0 and lng == 0:
        return False

    bounds = UAE_BOUNDS if strict else EXTENDED_BOUNDS

    return (bounds['min_lat'] <= lat <= bounds['max_lat'] and
            bounds['min_lng'] <= lng <= bounds['max_lng'])


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Расстояние между двумя точками в километрах (формула Хаверсина)."""
    R = 6371  # Радиус Земли в км

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lng / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def parse_datetime(date_str: str) -> Optional[datetime]:
    """Парсинг даты из разных форматов."""
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


# ═══════════════════════════════════════════════════════════════
# ИЗВЛЕЧЕНИЕ ЛОКАЦИЙ
# ═══════════════════════════════════════════════════════════════

class LocationExtractor:
    """Извлечение локаций из сообщений."""

    def __init__(self):
        self.locations: List[Location] = []
        self.stats = {
            'total_messages': 0,
            'whatsapp_shared': 0,
            'google_maps_links': 0,
            'text_coords': 0,
            'short_links': 0,
            'invalid_coords': 0,
            'duplicates': 0,
        }
        self.seen_coords: set = set()

    def extract_from_message(self, msg: dict) -> List[Location]:
        """Извлечение локаций из одного сообщения."""
        locations = []

        text = msg.get('text') or msg.get('message') or msg.get('content') or ''
        jid = msg.get('jid') or msg.get('chat_jid') or ''
        contact_name = msg.get('name') or msg.get('contact_name') or ''
        timestamp = msg.get('timestamp') or msg.get('date') or ''
        message_id = msg.get('message_id') or msg.get('id') or ''
        is_from_me = msg.get('is_from_me', False)

        # 1. WhatsApp shared location
        match = WHATSAPP_LOCATION_PATTERN.search(text)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            if is_valid_coordinate(lat, lng):
                loc = self._create_location(
                    lat, lng, 'whatsapp_shared', text,
                    timestamp, jid, contact_name, message_id, is_from_me
                )
                if loc:
                    locations.append(loc)
                    self.stats['whatsapp_shared'] += 1

        # 2. Google Maps ссылки
        for pattern in GOOGLE_MAPS_PATTERNS:
            for match in pattern.finditer(text):
                groups = match.groups()

                # Проверка на короткие ссылки (goo.gl)
                if len(groups) == 1 and ('goo.gl' in groups[0] or 'maps.app' in groups[0]):
                    self.stats['short_links'] += 1
                    continue

                if len(groups) >= 2:
                    try:
                        lat, lng = float(groups[0]), float(groups[1])
                        if is_valid_coordinate(lat, lng):
                            loc = self._create_location(
                                lat, lng, 'google_maps_link', match.group(0),
                                timestamp, jid, contact_name, message_id, is_from_me
                            )
                            if loc:
                                locations.append(loc)
                                self.stats['google_maps_links'] += 1
                    except (ValueError, IndexError):
                        pass

        # 3. Координаты в тексте
        for pattern in COORDS_IN_TEXT_PATTERNS:
            for match in pattern.finditer(text):
                try:
                    lat, lng = float(match.group(1)), float(match.group(2))

                    # Проверяем, не перепутаны ли lat и lng
                    if not is_valid_coordinate(lat, lng):
                        lat, lng = lng, lat  # Пробуем поменять местами

                    if is_valid_coordinate(lat, lng):
                        loc = self._create_location(
                            lat, lng, 'text_coords', match.group(0),
                            timestamp, jid, contact_name, message_id, is_from_me
                        )
                        if loc:
                            locations.append(loc)
                            self.stats['text_coords'] += 1
                except (ValueError, IndexError):
                    pass

        return locations

    def _create_location(
        self,
        lat: float,
        lng: float,
        source_type: str,
        raw_text: str,
        timestamp: str,
        jid: str,
        contact_name: str,
        message_id: str,
        is_from_me: bool
    ) -> Optional[Location]:
        """Создание объекта Location с проверкой на дубликаты."""
        # Округляем координаты для дедупликации
        coord_key = f"{lat:.5f},{lng:.5f}"

        if coord_key in self.seen_coords:
            self.stats['duplicates'] += 1
            # Всё равно создаём, но помечаем

        self.seen_coords.add(coord_key)

        location_id = generate_location_id(lat, lng, timestamp)

        return Location(
            location_id=location_id,
            lat=lat,
            lng=lng,
            source_type=source_type,
            raw_text=raw_text[:500],  # Ограничиваем длину
            timestamp=timestamp,
            jid=jid,
            contact_name=contact_name,
            message_id=message_id,
            is_from_me=is_from_me
        )

    def process_jsonl(self, filepath: Path) -> List[Location]:
        """Обработка JSONL файла."""
        print(f"\n[1/5] Чтение сообщений из {filepath}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                self.stats['total_messages'] += 1

                if self.stats['total_messages'] % 100000 == 0:
                    print(f"  Обработано: {self.stats['total_messages']:,}")

                line = line.strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                    locations = self.extract_from_message(msg)
                    self.locations.extend(locations)
                except json.JSONDecodeError:
                    pass

        print(f"  Всего сообщений: {self.stats['total_messages']:,}")
        print(f"  Найдено локаций: {len(self.locations):,}")

        return self.locations


# ═══════════════════════════════════════════════════════════════
# REVERSE GEOCODING
# ═══════════════════════════════════════════════════════════════

class ReverseGeocoder:
    """Reverse geocoding координат в адреса."""

    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self._load_cache()

        # Опциональные зависимости
        self.nominatim_available = False
        self.googlemaps_available = False

        try:
            from geopy.geocoders import Nominatim
            self.nominatim = Nominatim(user_agent="whatsapp_location_extractor")
            self.nominatim_available = True
        except ImportError:
            pass

        try:
            import googlemaps
            import os
            api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
            if api_key:
                self.gmaps = googlemaps.Client(key=api_key)
                self.googlemaps_available = True
        except (ImportError, Exception):
            pass

    def _load_cache(self):
        """Загрузка кеша геокодирования."""
        cache_file = JSON_DIR / "geocode_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception:
                pass

    def _save_cache(self):
        """Сохранение кеша геокодирования."""
        cache_file = JSON_DIR / "geocode_cache.json"
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def geocode(self, lat: float, lng: float) -> dict:
        """Получение адреса по координатам."""
        cache_key = f"{lat:.5f},{lng:.5f}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        result = {
            'address': '',
            'place_name': '',
            'country': '',
            'city': '',
            'district': ''
        }

        # Попытка через Google Maps API
        if self.googlemaps_available:
            try:
                response = self.gmaps.reverse_geocode((lat, lng))
                if response:
                    result['address'] = response[0].get('formatted_address', '')

                    for component in response[0].get('address_components', []):
                        types = component.get('types', [])
                        if 'locality' in types:
                            result['city'] = component['long_name']
                        elif 'country' in types:
                            result['country'] = component['long_name']
                        elif 'sublocality' in types or 'neighborhood' in types:
                            result['district'] = component['long_name']

                    self.cache[cache_key] = result
                    return result
            except Exception:
                pass

        # Попытка через Nominatim (бесплатный)
        if self.nominatim_available:
            try:
                import time
                time.sleep(1)  # Ограничение API

                location = self.nominatim.reverse(f"{lat}, {lng}", language='ru')
                if location:
                    result['address'] = location.address
                    raw = location.raw.get('address', {})
                    result['city'] = raw.get('city', raw.get('town', ''))
                    result['country'] = raw.get('country', '')
                    result['district'] = raw.get('suburb', raw.get('district', ''))

                    self.cache[cache_key] = result
                    return result
            except Exception:
                pass

        # Локальное определение по известным местам
        result = self._local_geocode(lat, lng)
        if result['place_name']:
            self.cache[cache_key] = result

        return result

    def _local_geocode(self, lat: float, lng: float) -> dict:
        """Локальное определение места без API."""
        result = {
            'address': '',
            'place_name': '',
            'country': 'UAE',
            'city': '',
            'district': ''
        }

        # Проверка близости к известным местам
        min_distance = float('inf')
        closest_place = None

        for place_name, (place_lat, place_lng) in UAE_LOCATION_KEYWORDS.items():
            distance = haversine_distance(lat, lng, place_lat, place_lng)
            if distance < min_distance:
                min_distance = distance
                closest_place = place_name

        if min_distance < 5:  # В пределах 5 км
            result['place_name'] = closest_place.title()

            # Определение города
            if lat > 25.0 and lat < 25.5 and lng > 54.9 and lng < 55.6:
                result['city'] = 'Dubai'
            elif lat > 24.2 and lat < 24.6 and lng > 54.2 and lng < 54.8:
                result['city'] = 'Abu Dhabi'
            elif lat > 25.2 and lat < 25.5 and lng > 55.3 and lng < 55.6:
                result['city'] = 'Sharjah'

        return result

    def geocode_locations(self, locations: List[Location], limit: int = 100) -> List[Location]:
        """Геокодирование списка локаций."""
        print(f"\n[2/5] Reverse geocoding ({min(len(locations), limit)} локаций)...")

        geocoded_count = 0

        for i, loc in enumerate(locations[:limit]):
            if loc.geocoded:
                continue

            result = self.geocode(loc.lat, loc.lng)
            loc.address = result.get('address', '')
            loc.place_name = result.get('place_name', '')
            loc.geocoded = True
            geocoded_count += 1

            if geocoded_count % 10 == 0:
                print(f"  Геокодировано: {geocoded_count}")

        self._save_cache()
        print(f"  Всего геокодировано: {geocoded_count}")

        return locations


# ═══════════════════════════════════════════════════════════════
# КЛАСТЕРИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

class LocationClusterer:
    """Кластеризация локаций для выявления частых мест."""

    def __init__(self, radius_km: float = CLUSTER_RADIUS_KM, min_points: int = MIN_CLUSTER_POINTS):
        self.radius_km = radius_km
        self.min_points = min_points
        self.clusters: List[LocationCluster] = []

    def cluster_locations(self, locations: List[Location]) -> List[LocationCluster]:
        """Кластеризация локаций."""
        print(f"\n[3/5] Кластеризация локаций...")

        if not locations:
            return []

        # Попытка использовать sklearn DBSCAN
        try:
            return self._cluster_sklearn(locations)
        except ImportError:
            print("  sklearn не установлен, используем простой алгоритм")
            return self._cluster_simple(locations)

    def _cluster_sklearn(self, locations: List[Location]) -> List[LocationCluster]:
        """Кластеризация через sklearn DBSCAN."""
        from sklearn.cluster import DBSCAN
        import numpy as np

        # Подготовка координат
        coords = np.array([[loc.lat, loc.lng] for loc in locations])

        # Конвертация км в радианы для haversine
        eps_rad = self.radius_km / 6371.0

        # DBSCAN кластеризация
        clustering = DBSCAN(
            eps=eps_rad,
            min_samples=self.min_points,
            metric='haversine'
        ).fit(np.radians(coords))

        # Присвоение cluster_id
        for i, loc in enumerate(locations):
            label = clustering.labels_[i]
            loc.cluster_id = label if label >= 0 else None

        # Создание кластеров
        cluster_ids = set(clustering.labels_)
        cluster_ids.discard(-1)  # Убираем шум

        for cluster_id in cluster_ids:
            cluster_locs = [loc for loc in locations if loc.cluster_id == cluster_id]
            cluster = self._create_cluster(cluster_id, cluster_locs)
            self.clusters.append(cluster)

        print(f"  Найдено кластеров: {len(self.clusters)}")
        return self.clusters

    def _cluster_simple(self, locations: List[Location]) -> List[LocationCluster]:
        """Простая кластеризация без sklearn."""
        assigned = set()
        cluster_id = 0

        for i, loc1 in enumerate(locations):
            if i in assigned:
                continue

            # Поиск соседей
            neighbors = [i]
            for j, loc2 in enumerate(locations):
                if i != j and j not in assigned:
                    distance = haversine_distance(loc1.lat, loc1.lng, loc2.lat, loc2.lng)
                    if distance <= self.radius_km:
                        neighbors.append(j)

            if len(neighbors) >= self.min_points:
                # Создаём кластер
                cluster_locs = [locations[idx] for idx in neighbors]
                for idx in neighbors:
                    assigned.add(idx)
                    locations[idx].cluster_id = cluster_id

                cluster = self._create_cluster(cluster_id, cluster_locs)
                self.clusters.append(cluster)
                cluster_id += 1

        print(f"  Найдено кластеров: {len(self.clusters)}")
        return self.clusters

    def _create_cluster(self, cluster_id: int, locations: List[Location]) -> LocationCluster:
        """Создание объекта кластера."""
        # Центр кластера
        center_lat = sum(loc.lat for loc in locations) / len(locations)
        center_lng = sum(loc.lng for loc in locations) / len(locations)

        # Контакты
        contacts = list(set(loc.jid for loc in locations if loc.jid))
        visit_count = Counter(loc.jid for loc in locations if loc.jid)

        # Даты
        dates = [parse_datetime(loc.timestamp) for loc in locations if loc.timestamp]
        dates = [d for d in dates if d]

        first_visit = min(dates).isoformat() if dates else ""
        last_visit = max(dates).isoformat() if dates else ""

        # Адрес из первой геокодированной локации
        address = ""
        place_name = ""
        for loc in locations:
            if loc.address:
                address = loc.address
                break
            if loc.place_name:
                place_name = loc.place_name

        return LocationCluster(
            cluster_id=cluster_id,
            center_lat=center_lat,
            center_lng=center_lng,
            locations_count=len(locations),
            address=address,
            place_name=place_name,
            contacts=contacts,
            first_visit=first_visit,
            last_visit=last_visit,
            visit_count_by_contact=dict(visit_count)
        )


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ КАРТЫ
# ═══════════════════════════════════════════════════════════════

class MapGenerator:
    """Генерация интерактивной карты с Folium."""

    def __init__(self):
        self.folium_available = False
        try:
            import folium
            from folium.plugins import MarkerCluster, HeatMap
            self.folium = folium
            self.MarkerCluster = MarkerCluster
            self.HeatMap = HeatMap
            self.folium_available = True
        except ImportError:
            pass

    def generate_map(
        self,
        locations: List[Location],
        clusters: List[LocationCluster],
        output_path: Path
    ) -> bool:
        """Генерация карты с локациями."""
        print(f"\n[4/5] Генерация карты...")

        if not self.folium_available:
            print("  [!] folium не установлен. Установите: pip install folium")
            return False

        if not locations:
            print("  [!] Нет локаций для отображения")
            return False

        # Центр карты
        center_lat = sum(loc.lat for loc in locations) / len(locations)
        center_lng = sum(loc.lng for loc in locations) / len(locations)

        # Создание карты
        m = self.folium.Map(
            location=[center_lat, center_lng],
            zoom_start=10,
            tiles='OpenStreetMap'
        )

        # Добавление слоёв
        locations_layer = self.folium.FeatureGroup(name='Все локации')
        clusters_layer = self.folium.FeatureGroup(name='Кластеры (частые места)')
        heatmap_layer = self.folium.FeatureGroup(name='Тепловая карта')

        # Маркеры локаций
        marker_cluster = self.MarkerCluster()

        for loc in locations:
            popup_html = f"""
            <b>{loc.place_name or 'Локация'}</b><br>
            <small>{loc.address or f'{loc.lat:.5f}, {loc.lng:.5f}'}</small><br>
            <hr>
            Контакт: {loc.contact_name or loc.jid}<br>
            Дата: {loc.timestamp[:10] if loc.timestamp else 'N/A'}<br>
            Источник: {loc.source_type}
            """

            color = 'blue' if not loc.is_from_me else 'green'

            self.folium.Marker(
                location=[loc.lat, loc.lng],
                popup=self.folium.Popup(popup_html, max_width=300),
                icon=self.folium.Icon(color=color, icon='info-sign')
            ).add_to(marker_cluster)

        marker_cluster.add_to(locations_layer)

        # Маркеры кластеров
        for cluster in clusters:
            popup_html = f"""
            <b>{cluster.place_name or f'Кластер #{cluster.cluster_id}'}</b><br>
            <small>{cluster.address or f'{cluster.center_lat:.5f}, {cluster.center_lng:.5f}'}</small><br>
            <hr>
            Посещений: {cluster.locations_count}<br>
            Контактов: {len(cluster.contacts)}<br>
            Первый визит: {cluster.first_visit[:10] if cluster.first_visit else 'N/A'}<br>
            Последний визит: {cluster.last_visit[:10] if cluster.last_visit else 'N/A'}
            """

            self.folium.CircleMarker(
                location=[cluster.center_lat, cluster.center_lng],
                radius=10 + cluster.locations_count,
                popup=self.folium.Popup(popup_html, max_width=300),
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.5
            ).add_to(clusters_layer)

        # Тепловая карта
        heat_data = [[loc.lat, loc.lng] for loc in locations]
        self.HeatMap(heat_data, radius=15, blur=10).add_to(heatmap_layer)

        # Добавление слоёв на карту
        locations_layer.add_to(m)
        clusters_layer.add_to(m)
        heatmap_layer.add_to(m)

        # Контроль слоёв
        self.folium.LayerControl().add_to(m)

        # Сохранение
        output_path.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_path))

        print(f"  Карта сохранена: {output_path}")
        return True


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

class LocationExporter:
    """Экспорт локаций в разные форматы."""

    def export_json(self, locations: List[Location], clusters: List[LocationCluster], output_path: Path):
        """Экспорт в JSON."""
        data = {
            'locations': [loc.to_dict() for loc in locations],
            'metadata': {
                'total_locations': len(locations),
                'total_clusters': len(clusters),
                'generated_at': datetime.now().isoformat(),
                'by_source': dict(Counter(loc.source_type for loc in locations)),
                'by_contact': dict(Counter(loc.jid for loc in locations)),
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  JSON: {output_path}")

    def export_clusters_json(self, clusters: List[LocationCluster], output_path: Path):
        """Экспорт кластеров в JSON."""
        data = {
            'clusters': [asdict(c) for c in clusters],
            'metadata': {
                'total_clusters': len(clusters),
                'generated_at': datetime.now().isoformat(),
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  Кластеры JSON: {output_path}")

    def export_csv(self, locations: List[Location], output_path: Path):
        """Экспорт в CSV."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            'location_id', 'lat', 'lng', 'address', 'place_name',
            'source_type', 'timestamp', 'jid', 'contact_name',
            'is_from_me', 'cluster_id'
        ]

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for loc in locations:
                row = {
                    'location_id': loc.location_id,
                    'lat': loc.lat,
                    'lng': loc.lng,
                    'address': loc.address,
                    'place_name': loc.place_name,
                    'source_type': loc.source_type,
                    'timestamp': loc.timestamp,
                    'jid': loc.jid,
                    'contact_name': loc.contact_name,
                    'is_from_me': loc.is_from_me,
                    'cluster_id': loc.cluster_id or ''
                }
                writer.writerow(row)

        print(f"  CSV: {output_path}")

    def export_geojson(self, locations: List[Location], output_path: Path):
        """Экспорт в GeoJSON."""
        features = []

        for loc in locations:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [loc.lng, loc.lat]  # GeoJSON: [lng, lat]
                },
                'properties': {
                    'id': loc.location_id,
                    'name': loc.place_name or f'{loc.lat:.5f}, {loc.lng:.5f}',
                    'address': loc.address,
                    'source_type': loc.source_type,
                    'timestamp': loc.timestamp,
                    'contact': loc.contact_name or loc.jid,
                    'cluster_id': loc.cluster_id
                }
            }
            features.append(feature)

        geojson = {
            'type': 'FeatureCollection',
            'features': features,
            'properties': {
                'total': len(features),
                'generated_at': datetime.now().isoformat()
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)

        print(f"  GeoJSON: {output_path}")

    def export_kml(self, locations: List[Location], output_path: Path):
        """Экспорт в KML (Google Earth)."""
        kml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>WhatsApp Locations</name>
    <description>Локации из WhatsApp чатов</description>
    <Style id="locationStyle">
        <IconStyle>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png</href>
            </Icon>
        </IconStyle>
    </Style>
{placemarks}
</Document>
</kml>'''

        placemark_template = '''    <Placemark>
        <name>{name}</name>
        <description><![CDATA[
            Контакт: {contact}<br>
            Дата: {date}<br>
            Источник: {source}<br>
            Адрес: {address}
        ]]></description>
        <styleUrl>#locationStyle</styleUrl>
        <Point>
            <coordinates>{lng},{lat},0</coordinates>
        </Point>
    </Placemark>'''

        placemarks = []
        for loc in locations:
            pm = placemark_template.format(
                name=loc.place_name or f'Location {loc.location_id[:8]}',
                contact=loc.contact_name or loc.jid or 'Unknown',
                date=loc.timestamp[:10] if loc.timestamp else 'N/A',
                source=loc.source_type,
                address=loc.address or 'N/A',
                lat=loc.lat,
                lng=loc.lng
            )
            placemarks.append(pm)

        kml_content = kml_template.format(placemarks='\n'.join(placemarks))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(kml_content)

        print(f"  KML: {output_path}")

    def export_all(
        self,
        locations: List[Location],
        clusters: List[LocationCluster]
    ):
        """Экспорт во все форматы."""
        print(f"\n[5/5] Экспорт данных...")

        self.export_json(locations, clusters, OUTPUT_JSON)
        self.export_clusters_json(clusters, OUTPUT_CLUSTERS)
        self.export_csv(locations, OUTPUT_CSV)
        self.export_geojson(locations, OUTPUT_GEOJSON)
        self.export_kml(locations, OUTPUT_KML)


# ═══════════════════════════════════════════════════════════════
# ОСНОВНАЯ ЛОГИКА
# ═══════════════════════════════════════════════════════════════

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description='Извлечение GPS локаций из WhatsApp чатов'
    )
    parser.add_argument('--geocode', action='store_true',
                       help='Выполнить reverse geocoding')
    parser.add_argument('--geocode-limit', type=int, default=100,
                       help='Лимит геокодирования (default: 100)')
    parser.add_argument('--cluster', action='store_true',
                       help='Выполнить кластеризацию')
    parser.add_argument('--map', action='store_true',
                       help='Сгенерировать карту')
    parser.add_argument('--all', action='store_true',
                       help='Выполнить все операции')
    parser.add_argument('--input', type=str,
                       help='Входной JSONL файл')

    args = parser.parse_args()

    # Если указан --all, включаем все опции
    if args.all:
        args.geocode = True
        args.cluster = True
        args.map = True

    print("=" * 60)
    print("Извлечение GPS локаций из WhatsApp чатов")
    print("=" * 60)

    # Проверяем директории
    ensure_directories()

    # Входной файл
    input_file = Path(args.input) if args.input else INPUT_FILE

    if not input_file.exists():
        print(f"\n[ОШИБКА] Входной файл не найден: {input_file}")
        print("\nСначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    # 1. Извлечение локаций
    extractor = LocationExtractor()
    locations = extractor.process_jsonl(input_file)

    if not locations:
        print("\n[!] Локации не найдены")
        sys.exit(0)

    # 2. Reverse geocoding (опционально)
    if args.geocode:
        geocoder = ReverseGeocoder()
        locations = geocoder.geocode_locations(locations, limit=args.geocode_limit)

    # 3. Кластеризация (опционально)
    clusters = []
    if args.cluster:
        clusterer = LocationClusterer()
        clusters = clusterer.cluster_locations(locations)

    # 4. Генерация карты (опционально)
    if args.map:
        map_generator = MapGenerator()
        map_generator.generate_map(locations, clusters, OUTPUT_MAP)

    # 5. Экспорт
    exporter = LocationExporter()
    exporter.export_all(locations, clusters)

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Всего локаций: {len(locations):,}")
    print(f"\nПо источникам:")
    for src, count in extractor.stats.items():
        if src.startswith('total') or count == 0:
            continue
        print(f"  - {src}: {count:,}")

    if clusters:
        print(f"\nКластеров (частые места): {len(clusters)}")
        print("\nТоп-5 частых мест:")
        top_clusters = sorted(clusters, key=lambda c: c.locations_count, reverse=True)[:5]
        for c in top_clusters:
            name = c.place_name or c.address or f"Cluster #{c.cluster_id}"
            print(f"  - {name}: {c.locations_count} посещений")

    print("\n" + "=" * 60)
    print("Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
