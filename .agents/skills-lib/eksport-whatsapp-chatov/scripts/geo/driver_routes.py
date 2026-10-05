#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Автоматические маршруты для водителей через Google Maps.

Функционал:
- Multi-stop маршруты с оптимизацией
- Deep links для Google Maps и Waze
- Форматы для WhatsApp/Telegram
- Мониторинг позиции и ETA
- Отчёты по пробегу и времени
- База популярных отелей ОАЭ

Использование:
    from driver_routes import DriverRouteManager

    manager = DriverRouteManager()
    route = manager.create_route(
        driver_phone="+971501234567",
        stops=[
            {"name": "JBR", "address": "JBR Walk, Dubai"},
            {"name": "Dubai Mall", "address": "Dubai Mall, Dubai"},
            {"name": "Burj Khalifa", "address": "Burj Khalifa, Dubai"}
        ]
    )
    message = manager.format_for_whatsapp(route)
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from urllib.parse import quote, urlencode
import re

# Опциональные зависимости
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Импорт конфигурации
try:
    from config import (
        CHATS_DIR, JSON_DIR, ANALYTICS_DIR,
        API_KEYS, ensure_directories
    )
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    JSON_DIR = CHATS_DIR / "_база" / "json"
    ANALYTICS_DIR = CHATS_DIR / "_аналитика"
    API_KEYS = {}
    def ensure_directories():
        pass

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Google Maps API ключ
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Директории для данных
ROUTES_DIR = JSON_DIR / "routes"
HOTELS_FILE = JSON_DIR / "hotels_database.json"
DRIVERS_FILE = JSON_DIR / "drivers.json"
ROUTES_HISTORY_FILE = JSON_DIR / "routes_history.json"
DAILY_REPORTS_DIR = ANALYTICS_DIR / "driver_reports"

# Средний расход топлива (л/100км)
DEFAULT_FUEL_CONSUMPTION = 12.0

# Цена топлива AED/л (примерная)
FUEL_PRICE_AED = 3.5

# Часовой пояс ОАЭ
UAE_TIMEZONE_OFFSET = timedelta(hours=4)


# ═══════════════════════════════════════════════════════════════
# БАЗА ПОПУЛЯРНЫХ ОТЕЛЕЙ ОАЭ
# ═══════════════════════════════════════════════════════════════

DEFAULT_HOTELS_DATABASE = {
    "dubai": {
        "JBR": [
            {
                "name": "Hilton Dubai Jumeirah",
                "address": "The Walk, JBR, Dubai, UAE",
                "lat": 25.0769,
                "lng": 55.1337,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Ritz-Carlton Dubai JBR",
                "address": "The Walk, JBR, Dubai, UAE",
                "lat": 25.0785,
                "lng": 55.1345,
                "pickup_point": "Lobby entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Sofitel Dubai JBR",
                "address": "The Walk, JBR, Dubai, UAE",
                "lat": 25.0752,
                "lng": 55.1328,
                "pickup_point": "Main lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "JA Ocean View Hotel",
                "address": "The Walk, JBR, Dubai, UAE",
                "lat": 25.0741,
                "lng": 55.1321,
                "pickup_point": "Hotel entrance",
                "default_pickup_time": "09:00",
                "stars": 4
            },
            {
                "name": "Amwaj Rotana JBR",
                "address": "The Walk, JBR, Dubai, UAE",
                "lat": 25.0738,
                "lng": 55.1318,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ],
        "Marina": [
            {
                "name": "Address Dubai Marina",
                "address": "Dubai Marina, Dubai, UAE",
                "lat": 25.0762,
                "lng": 55.1400,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Grosvenor House Dubai",
                "address": "Dubai Marina, Dubai, UAE",
                "lat": 25.0778,
                "lng": 55.1412,
                "pickup_point": "Tower 1 lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "InterContinental Dubai Marina",
                "address": "Dubai Marina, Dubai, UAE",
                "lat": 25.0745,
                "lng": 55.1388,
                "pickup_point": "Hotel lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Marriott Harbour Hotel",
                "address": "Dubai Marina, Dubai, UAE",
                "lat": 25.0815,
                "lng": 55.1456,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ],
        "Palm Jumeirah": [
            {
                "name": "Atlantis The Palm",
                "address": "Crescent Road, Palm Jumeirah, Dubai, UAE",
                "lat": 25.1304,
                "lng": 55.1171,
                "pickup_point": "Main entrance (under the arch)",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Fairmont The Palm",
                "address": "Palm Jumeirah, Dubai, UAE",
                "lat": 25.1128,
                "lng": 55.1389,
                "pickup_point": "Hotel lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "One&Only The Palm",
                "address": "Palm Jumeirah, Dubai, UAE",
                "lat": 25.1089,
                "lng": 55.1352,
                "pickup_point": "Reception",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Sofitel Dubai The Palm",
                "address": "East Crescent, Palm Jumeirah, Dubai, UAE",
                "lat": 25.1156,
                "lng": 55.1421,
                "pickup_point": "Main lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Waldorf Astoria Palm Jumeirah",
                "address": "East Crescent, Palm Jumeirah, Dubai, UAE",
                "lat": 25.1198,
                "lng": 55.1445,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ],
        "Downtown": [
            {
                "name": "Address Downtown",
                "address": "Sheikh Mohammed bin Rashid Boulevard, Downtown Dubai, UAE",
                "lat": 25.1912,
                "lng": 55.2787,
                "pickup_point": "Main entrance near Dubai Mall",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Armani Hotel Dubai",
                "address": "Burj Khalifa, Downtown Dubai, UAE",
                "lat": 25.1972,
                "lng": 55.2744,
                "pickup_point": "Armani entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Address Boulevard",
                "address": "Sheikh Mohammed bin Rashid Boulevard, Downtown Dubai, UAE",
                "lat": 25.1889,
                "lng": 55.2756,
                "pickup_point": "Hotel entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Vida Downtown",
                "address": "Sheikh Mohammed bin Rashid Boulevard, Downtown Dubai, UAE",
                "lat": 25.1945,
                "lng": 55.2812,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 4
            }
        ],
        "Business Bay": [
            {
                "name": "JW Marriott Marquis Dubai",
                "address": "Business Bay, Dubai, UAE",
                "lat": 25.1851,
                "lng": 55.2634,
                "pickup_point": "Tower A entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Oberoi Dubai",
                "address": "Business Bay, Dubai, UAE",
                "lat": 25.1823,
                "lng": 55.2612,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Taj Dubai",
                "address": "Business Bay, Dubai, UAE",
                "lat": 25.1867,
                "lng": 55.2689,
                "pickup_point": "Hotel lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ],
        "Deira": [
            {
                "name": "Hyatt Regency Dubai",
                "address": "Deira Corniche, Dubai, UAE",
                "lat": 25.2712,
                "lng": 55.3156,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Hilton Dubai Creek",
                "address": "Baniyas Road, Deira, Dubai, UAE",
                "lat": 25.2654,
                "lng": 55.3123,
                "pickup_point": "Hotel entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Radisson Blu Hotel Dubai Deira Creek",
                "address": "Baniyas Road, Deira, Dubai, UAE",
                "lat": 25.2634,
                "lng": 55.3098,
                "pickup_point": "Main lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ],
        "Bur Dubai": [
            {
                "name": "Grand Hyatt Dubai",
                "address": "Oud Metha, Bur Dubai, UAE",
                "lat": 25.2289,
                "lng": 55.3156,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Raffles Dubai",
                "address": "Wafi City, Bur Dubai, UAE",
                "lat": 25.2267,
                "lng": 55.3201,
                "pickup_point": "Lobby entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ]
    },
    "abu_dhabi": {
        "Corniche": [
            {
                "name": "Emirates Palace",
                "address": "West Corniche Road, Abu Dhabi, UAE",
                "lat": 24.4615,
                "lng": 54.3175,
                "pickup_point": "Main gate",
                "default_pickup_time": "08:00",
                "stars": 5
            },
            {
                "name": "St. Regis Abu Dhabi",
                "address": "Nation Towers, Corniche, Abu Dhabi, UAE",
                "lat": 24.4678,
                "lng": 54.3245,
                "pickup_point": "Hotel entrance",
                "default_pickup_time": "08:00",
                "stars": 5
            },
            {
                "name": "InterContinental Abu Dhabi",
                "address": "King Abdullah Bin Abdulaziz Al Saud St, Abu Dhabi, UAE",
                "lat": 24.4523,
                "lng": 54.3312,
                "pickup_point": "Main lobby",
                "default_pickup_time": "08:00",
                "stars": 5
            }
        ],
        "Saadiyat Island": [
            {
                "name": "Park Hyatt Abu Dhabi",
                "address": "Saadiyat Island, Abu Dhabi, UAE",
                "lat": 24.5432,
                "lng": 54.4234,
                "pickup_point": "Main entrance",
                "default_pickup_time": "08:00",
                "stars": 5
            },
            {
                "name": "St. Regis Saadiyat Island",
                "address": "Saadiyat Island, Abu Dhabi, UAE",
                "lat": 24.5412,
                "lng": 54.4198,
                "pickup_point": "Lobby",
                "default_pickup_time": "08:00",
                "stars": 5
            }
        ],
        "Yas Island": [
            {
                "name": "W Abu Dhabi - Yas Island",
                "address": "Yas Island, Abu Dhabi, UAE",
                "lat": 24.4678,
                "lng": 54.6123,
                "pickup_point": "Main entrance",
                "default_pickup_time": "08:00",
                "stars": 5
            },
            {
                "name": "Yas Hotel Abu Dhabi",
                "address": "Yas Marina Circuit, Yas Island, Abu Dhabi, UAE",
                "lat": 24.4712,
                "lng": 54.6089,
                "pickup_point": "Hotel lobby",
                "default_pickup_time": "08:00",
                "stars": 5
            }
        ]
    },
    "sharjah": {
        "Corniche": [
            {
                "name": "Sheraton Sharjah Beach Resort",
                "address": "Al Muntazah St, Sharjah, UAE",
                "lat": 25.3456,
                "lng": 55.3923,
                "pickup_point": "Main entrance",
                "default_pickup_time": "09:00",
                "stars": 5
            },
            {
                "name": "Hilton Sharjah",
                "address": "Al Corniche St, Sharjah, UAE",
                "lat": 25.3534,
                "lng": 55.3867,
                "pickup_point": "Lobby",
                "default_pickup_time": "09:00",
                "stars": 5
            }
        ]
    },
    "ras_al_khaimah": {
        "Beach": [
            {
                "name": "Waldorf Astoria Ras Al Khaimah",
                "address": "Al Hamra Island, Ras Al Khaimah, UAE",
                "lat": 25.6812,
                "lng": 55.7823,
                "pickup_point": "Main entrance",
                "default_pickup_time": "08:30",
                "stars": 5
            },
            {
                "name": "Rixos Bab Al Bahr",
                "address": "Al Marjan Island, Ras Al Khaimah, UAE",
                "lat": 25.6934,
                "lng": 55.7612,
                "pickup_point": "Lobby",
                "default_pickup_time": "08:30",
                "stars": 5
            }
        ]
    },
    "fujairah": {
        "Beach": [
            {
                "name": "Fairmont Fujairah Beach Resort",
                "address": "Dibba Road, Fujairah, UAE",
                "lat": 25.4512,
                "lng": 56.3567,
                "pickup_point": "Main entrance",
                "default_pickup_time": "08:00",
                "stars": 5
            },
            {
                "name": "Le Meridien Al Aqah Beach Resort",
                "address": "Al Aqah, Fujairah, UAE",
                "lat": 25.4823,
                "lng": 56.3612,
                "pickup_point": "Hotel entrance",
                "default_pickup_time": "08:00",
                "stars": 5
            }
        ]
    }
}

# Популярные достопримечательности для туров
POPULAR_ATTRACTIONS = {
    "dubai": {
        "Burj Khalifa": {
            "address": "1 Sheikh Mohammed bin Rashid Blvd, Dubai, UAE",
            "lat": 25.1972,
            "lng": 55.2744,
            "visit_duration": 90,  # минут
            "best_time": "morning"
        },
        "Dubai Mall": {
            "address": "Financial Center Road, Downtown Dubai, UAE",
            "lat": 25.1985,
            "lng": 55.2796,
            "visit_duration": 180,
            "best_time": "afternoon"
        },
        "Dubai Frame": {
            "address": "Zabeel Park, Dubai, UAE",
            "lat": 25.2354,
            "lng": 55.2989,
            "visit_duration": 60,
            "best_time": "morning"
        },
        "Miracle Garden": {
            "address": "Al Barsha South 3, Dubai, UAE",
            "lat": 25.0598,
            "lng": 55.2436,
            "visit_duration": 120,
            "best_time": "morning"
        },
        "Global Village": {
            "address": "Sheikh Mohammed Bin Zayed Road, Dubai, UAE",
            "lat": 25.0658,
            "lng": 55.3087,
            "visit_duration": 240,
            "best_time": "evening"
        },
        "Museum of the Future": {
            "address": "Sheikh Zayed Road, Dubai, UAE",
            "lat": 25.2198,
            "lng": 55.2820,
            "visit_duration": 120,
            "best_time": "afternoon"
        },
        "Palm Jumeirah": {
            "address": "Palm Jumeirah, Dubai, UAE",
            "lat": 25.1124,
            "lng": 55.1390,
            "visit_duration": 60,
            "best_time": "anytime"
        },
        "Old Dubai (Al Fahidi)": {
            "address": "Al Fahidi Historical District, Bur Dubai, UAE",
            "lat": 25.2632,
            "lng": 55.2972,
            "visit_duration": 90,
            "best_time": "morning"
        },
        "Gold Souk": {
            "address": "Gold Souk, Deira, Dubai, UAE",
            "lat": 25.2867,
            "lng": 55.2998,
            "visit_duration": 60,
            "best_time": "evening"
        },
        "Spice Souk": {
            "address": "Spice Souk, Deira, Dubai, UAE",
            "lat": 25.2712,
            "lng": 55.2985,
            "visit_duration": 45,
            "best_time": "morning"
        }
    },
    "abu_dhabi": {
        "Sheikh Zayed Mosque": {
            "address": "Sheikh Rashid Bin Saeed Street, Abu Dhabi, UAE",
            "lat": 24.4128,
            "lng": 54.4742,
            "visit_duration": 90,
            "best_time": "morning"
        },
        "Louvre Abu Dhabi": {
            "address": "Saadiyat Island, Abu Dhabi, UAE",
            "lat": 24.5339,
            "lng": 54.3984,
            "visit_duration": 180,
            "best_time": "afternoon"
        },
        "Ferrari World": {
            "address": "Yas Island, Abu Dhabi, UAE",
            "lat": 24.4838,
            "lng": 54.6035,
            "visit_duration": 300,
            "best_time": "anytime"
        },
        "Yas Waterworld": {
            "address": "Yas Island, Abu Dhabi, UAE",
            "lat": 24.4912,
            "lng": 54.6089,
            "visit_duration": 360,
            "best_time": "morning"
        },
        "Warner Bros World": {
            "address": "Yas Island, Abu Dhabi, UAE",
            "lat": 24.4856,
            "lng": 54.6067,
            "visit_duration": 360,
            "best_time": "anytime"
        },
        "Qasr Al Watan": {
            "address": "Presidential Palace, Abu Dhabi, UAE",
            "lat": 24.4612,
            "lng": 54.3098,
            "visit_duration": 120,
            "best_time": "afternoon"
        },
        "Emirates Palace": {
            "address": "West Corniche Road, Abu Dhabi, UAE",
            "lat": 24.4615,
            "lng": 54.3175,
            "visit_duration": 60,
            "best_time": "anytime"
        }
    }
}


# ═══════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class RouteStop:
    """Остановка маршрута."""
    name: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    scheduled_time: Optional[str] = None  # HH:MM
    eta: Optional[str] = None  # Расчётное время прибытия
    duration_minutes: Optional[int] = None  # Время на остановке
    notes: Optional[str] = None
    client_phone: Optional[str] = None
    client_name: Optional[str] = None
    pickup_point: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, skipped


@dataclass
class Route:
    """Полный маршрут."""
    id: str
    driver_phone: str
    driver_name: Optional[str] = None
    stops: List[RouteStop] = field(default_factory=list)
    created_at: str = ""
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_distance_km: float = 0.0
    total_duration_minutes: int = 0
    status: str = "draft"  # draft, active, completed, cancelled
    notes: Optional[str] = None
    vehicle_type: str = "car"
    optimized: bool = False


@dataclass
class DriverPosition:
    """Позиция водителя."""
    driver_phone: str
    lat: float
    lng: float
    timestamp: str
    speed_kmh: Optional[float] = None
    heading: Optional[int] = None  # 0-360 градусов


@dataclass
class DailyReport:
    """Дневной отчёт водителя."""
    driver_phone: str
    date: str
    driver_name: Optional[str] = None
    routes_count: int = 0
    total_distance_km: float = 0.0
    total_duration_minutes: int = 0
    fuel_consumption_liters: float = 0.0
    fuel_cost_aed: float = 0.0
    stops_completed: int = 0
    routes: List[str] = field(default_factory=list)  # route IDs


# ═══════════════════════════════════════════════════════════════
# МЕНЕДЖЕР МАРШРУТОВ
# ═══════════════════════════════════════════════════════════════

class DriverRouteManager:
    """Менеджер маршрутов для водителей."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация менеджера.

        Args:
            api_key: Google Maps API ключ (опционально, берётся из env)
        """
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        self.gmaps = None

        if self.api_key and GOOGLEMAPS_AVAILABLE:
            try:
                self.gmaps = googlemaps.Client(key=self.api_key)
                logger.info("Google Maps client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps: {e}")

        # Загрузка баз данных
        self.hotels = self._load_hotels()
        self.drivers = self._load_drivers()
        self.routes_history: List[Dict] = []

        # Создание директорий
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Создать необходимые директории."""
        ROUTES_DIR.mkdir(parents=True, exist_ok=True)
        DAILY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_hotels(self) -> Dict:
        """Загрузить базу отелей."""
        if HOTELS_FILE.exists():
            try:
                with open(HOTELS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load hotels: {e}")

        # Сохранить дефолтную базу
        self._save_hotels(DEFAULT_HOTELS_DATABASE)
        return DEFAULT_HOTELS_DATABASE

    def _save_hotels(self, hotels: Dict):
        """Сохранить базу отелей."""
        JSON_DIR.mkdir(parents=True, exist_ok=True)
        with open(HOTELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(hotels, f, ensure_ascii=False, indent=2)

    def _load_drivers(self) -> Dict:
        """Загрузить список водителей."""
        if DRIVERS_FILE.exists():
            try:
                with open(DRIVERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load drivers: {e}")
        return {}

    def _save_drivers(self, drivers: Dict):
        """Сохранить список водителей."""
        with open(DRIVERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(drivers, f, ensure_ascii=False, indent=2)

    def _generate_route_id(self) -> str:
        """Генерация уникального ID маршрута."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
        return f"R{timestamp}_{random_part}"

    # ═══════════════════════════════════════════════════════════════
    # СОЗДАНИЕ МАРШРУТОВ
    # ═══════════════════════════════════════════════════════════════

    def create_route(
        self,
        driver_phone: str,
        stops: List[Dict],
        driver_name: Optional[str] = None,
        start_time: Optional[str] = None,
        optimize: bool = True,
        vehicle_type: str = "car"
    ) -> Route:
        """
        Создать маршрут для водителя.

        Args:
            driver_phone: Телефон водителя
            stops: Список остановок [{"name": ..., "address": ..., "lat": ..., "lng": ...}]
            driver_name: Имя водителя
            start_time: Время начала (HH:MM)
            optimize: Оптимизировать порядок остановок
            vehicle_type: Тип транспорта (car, van, bus)

        Returns:
            Route объект
        """
        route = Route(
            id=self._generate_route_id(),
            driver_phone=driver_phone,
            driver_name=driver_name,
            created_at=datetime.now().isoformat(),
            start_time=start_time or datetime.now().strftime("%H:%M"),
            vehicle_type=vehicle_type
        )

        # Создание остановок
        for stop_data in stops:
            stop = RouteStop(
                name=stop_data.get("name", ""),
                address=stop_data.get("address", ""),
                lat=stop_data.get("lat"),
                lng=stop_data.get("lng"),
                scheduled_time=stop_data.get("scheduled_time"),
                duration_minutes=stop_data.get("duration_minutes", 15),
                notes=stop_data.get("notes"),
                client_phone=stop_data.get("client_phone"),
                client_name=stop_data.get("client_name"),
                pickup_point=stop_data.get("pickup_point")
            )
            route.stops.append(stop)

        # Геокодирование остановок без координат
        self._geocode_stops(route)

        # Оптимизация маршрута
        if optimize and len(route.stops) > 2:
            route = self._optimize_route(route)
            route.optimized = True

        # Расчёт расстояний и ETA
        self._calculate_route_details(route)

        # Сохранение
        self._save_route(route)

        return route

    def _geocode_stops(self, route: Route):
        """Геокодирование остановок без координат."""
        if not self.gmaps:
            logger.warning("Google Maps not available for geocoding")
            return

        for stop in route.stops:
            if stop.lat is None or stop.lng is None:
                try:
                    # Поиск в базе отелей
                    hotel = self.find_hotel(stop.name)
                    if hotel:
                        stop.lat = hotel.get("lat")
                        stop.lng = hotel.get("lng")
                        stop.pickup_point = stop.pickup_point or hotel.get("pickup_point")
                        continue

                    # Геокодирование через API
                    result = self.gmaps.geocode(stop.address)
                    if result:
                        location = result[0]["geometry"]["location"]
                        stop.lat = location["lat"]
                        stop.lng = location["lng"]
                        logger.info(f"Geocoded: {stop.name} -> {stop.lat}, {stop.lng}")

                except Exception as e:
                    logger.error(f"Geocoding failed for {stop.name}: {e}")

    def _optimize_route(self, route: Route) -> Route:
        """Оптимизация порядка остановок."""
        if not self.gmaps or len(route.stops) < 3:
            return route

        try:
            # Подготовка waypoints
            origin = f"{route.stops[0].lat},{route.stops[0].lng}"
            destination = f"{route.stops[-1].lat},{route.stops[-1].lng}"
            waypoints = [
                f"{s.lat},{s.lng}" for s in route.stops[1:-1]
                if s.lat and s.lng
            ]

            if not waypoints:
                return route

            # Запрос с оптимизацией
            result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                waypoints=waypoints,
                optimize_waypoints=True,
                mode="driving",
                departure_time=datetime.now()
            )

            if result and "waypoint_order" in result[0]:
                # Перестановка остановок согласно оптимизации
                order = result[0]["waypoint_order"]
                middle_stops = [route.stops[i + 1] for i in order]
                route.stops = [route.stops[0]] + middle_stops + [route.stops[-1]]
                logger.info(f"Route optimized: new order {order}")

        except Exception as e:
            logger.error(f"Route optimization failed: {e}")

        return route

    def _calculate_route_details(self, route: Route):
        """Расчёт деталей маршрута (расстояния, время, ETA)."""
        if not self.gmaps or len(route.stops) < 2:
            return

        try:
            total_distance = 0
            total_duration = 0

            # Время начала
            if route.start_time:
                current_time = datetime.strptime(route.start_time, "%H:%M")
            else:
                current_time = datetime.now()

            # ETA для первой остановки
            route.stops[0].eta = current_time.strftime("%H:%M")

            for i in range(len(route.stops) - 1):
                origin = route.stops[i]
                dest = route.stops[i + 1]

                if not (origin.lat and origin.lng and dest.lat and dest.lng):
                    continue

                # Запрос маршрута между точками
                result = self.gmaps.directions(
                    origin=f"{origin.lat},{origin.lng}",
                    destination=f"{dest.lat},{dest.lng}",
                    mode="driving",
                    departure_time=datetime.now()
                )

                if result:
                    leg = result[0]["legs"][0]
                    distance_m = leg["distance"]["value"]
                    duration_s = leg.get("duration_in_traffic", leg["duration"])["value"]

                    total_distance += distance_m
                    total_duration += duration_s

                    # Расчёт ETA для следующей остановки
                    # Добавляем время на текущей остановке
                    stop_duration = origin.duration_minutes or 15
                    current_time += timedelta(minutes=stop_duration)
                    current_time += timedelta(seconds=duration_s)

                    dest.eta = current_time.strftime("%H:%M")

            route.total_distance_km = round(total_distance / 1000, 1)
            route.total_duration_minutes = round(total_duration / 60)

        except Exception as e:
            logger.error(f"Route calculation failed: {e}")

    def _save_route(self, route: Route):
        """Сохранить маршрут."""
        route_file = ROUTES_DIR / f"{route.id}.json"
        with open(route_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(route), f, ensure_ascii=False, indent=2)

    def load_route(self, route_id: str) -> Optional[Route]:
        """Загрузить маршрут по ID."""
        route_file = ROUTES_DIR / f"{route_id}.json"
        if not route_file.exists():
            return None

        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            route = Route(
                id=data["id"],
                driver_phone=data["driver_phone"],
                driver_name=data.get("driver_name"),
                created_at=data["created_at"],
                start_time=data.get("start_time"),
                end_time=data.get("end_time"),
                total_distance_km=data.get("total_distance_km", 0),
                total_duration_minutes=data.get("total_duration_minutes", 0),
                status=data.get("status", "draft"),
                notes=data.get("notes"),
                vehicle_type=data.get("vehicle_type", "car"),
                optimized=data.get("optimized", False)
            )

            for stop_data in data.get("stops", []):
                stop = RouteStop(**stop_data)
                route.stops.append(stop)

            return route

        except Exception as e:
            logger.error(f"Failed to load route {route_id}: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════
    # ФОРМАТИРОВАНИЕ ДЛЯ МЕССЕНДЖЕРОВ
    # ═══════════════════════════════════════════════════════════════

    def format_for_whatsapp(
        self,
        route: Route,
        include_links: bool = True,
        language: str = "ru"
    ) -> str:
        """
        Форматирование маршрута для WhatsApp.

        Args:
            route: Объект маршрута
            include_links: Включать ссылки на карты
            language: Язык сообщения (ru/en)

        Returns:
            Форматированное сообщение
        """
        if language == "ru":
            header = f"*МАРШРУТ {route.id}*"
            date_label = "Дата"
            start_label = "Старт"
            stops_label = "Остановки"
            total_label = "Итого"
            distance_label = "км"
            duration_label = "мин"
            eta_label = "ETA"
            client_label = "Клиент"
            notes_label = "Заметка"
            maps_label = "Открыть в картах"
        else:
            header = f"*ROUTE {route.id}*"
            date_label = "Date"
            start_label = "Start"
            stops_label = "Stops"
            total_label = "Total"
            distance_label = "km"
            duration_label = "min"
            eta_label = "ETA"
            client_label = "Client"
            notes_label = "Note"
            maps_label = "Open in maps"

        lines = [
            header,
            "",
            f"{date_label}: {datetime.now().strftime('%d.%m.%Y')}",
            f"{start_label}: {route.start_time or 'TBD'}",
            "",
            f"*{stops_label}:*"
        ]

        for i, stop in enumerate(route.stops, 1):
            stop_line = f"{i}. *{stop.name}*"
            if stop.eta:
                stop_line += f" ({eta_label}: {stop.eta})"

            lines.append(stop_line)

            if stop.address:
                lines.append(f"   {stop.address}")

            if stop.pickup_point:
                lines.append(f"   {stop.pickup_point}")

            if stop.client_name:
                lines.append(f"   {client_label}: {stop.client_name}")
                if stop.client_phone:
                    lines.append(f"   {stop.client_phone}")

            if stop.notes:
                lines.append(f"   {notes_label}: {stop.notes}")

            lines.append("")

        # Итого
        lines.append(f"*{total_label}:* {route.total_distance_km} {distance_label}, ~{route.total_duration_minutes} {duration_label}")

        # Ссылки на карты
        if include_links:
            lines.append("")
            lines.append(f"*{maps_label}:*")

            # Google Maps deep link
            gmaps_link = self.generate_google_maps_link(route)
            lines.append(f"Google Maps: {gmaps_link}")

            # Waze deep link
            waze_link = self.generate_waze_link(route)
            lines.append(f"Waze: {waze_link}")

        return "\n".join(lines)

    def format_for_telegram(
        self,
        route: Route,
        include_links: bool = True,
        language: str = "ru"
    ) -> str:
        """
        Форматирование маршрута для Telegram (с HTML).

        Args:
            route: Объект маршрута
            include_links: Включать ссылки на карты
            language: Язык сообщения

        Returns:
            Форматированное сообщение с HTML
        """
        if language == "ru":
            header = f"<b>МАРШРУТ {route.id}</b>"
            date_label = "Дата"
            start_label = "Старт"
            total_label = "Итого"
            eta_label = "ETA"
        else:
            header = f"<b>ROUTE {route.id}</b>"
            date_label = "Date"
            start_label = "Start"
            total_label = "Total"
            eta_label = "ETA"

        lines = [
            header,
            "",
            f"{date_label}: {datetime.now().strftime('%d.%m.%Y')}",
            f"{start_label}: {route.start_time or 'TBD'}",
            ""
        ]

        for i, stop in enumerate(route.stops, 1):
            eta_str = f" ({eta_label}: {stop.eta})" if stop.eta else ""
            lines.append(f"{i}. <b>{stop.name}</b>{eta_str}")

            if stop.address:
                lines.append(f"   <i>{stop.address}</i>")

            if stop.client_name:
                client_info = stop.client_name
                if stop.client_phone:
                    client_info += f" ({stop.client_phone})"
                lines.append(f"   {client_info}")

            lines.append("")

        lines.append(f"<b>{total_label}:</b> {route.total_distance_km} km, ~{route.total_duration_minutes} min")

        if include_links:
            gmaps_link = self.generate_google_maps_link(route)
            waze_link = self.generate_waze_link(route)

            lines.append("")
            lines.append(f'<a href="{gmaps_link}">Google Maps</a> | <a href="{waze_link}">Waze</a>')

        return "\n".join(lines)

    def format_client_notification(
        self,
        route: Route,
        stop_index: int,
        driver_position: Optional[DriverPosition] = None,
        language: str = "ru"
    ) -> str:
        """
        Уведомление клиенту о приближении водителя.

        Args:
            route: Маршрут
            stop_index: Индекс остановки клиента
            driver_position: Текущая позиция водителя
            language: Язык

        Returns:
            Сообщение для клиента
        """
        stop = route.stops[stop_index]

        if language == "ru":
            lines = [
                "Ваш водитель в пути!",
                "",
                f"Время пикапа: *{stop.eta}*" if stop.eta else "",
                f"Место встречи: {stop.pickup_point or stop.address}"
            ]

            if driver_position:
                # Расчёт ETA от текущей позиции
                eta_minutes = self._calculate_eta_from_position(
                    driver_position, stop
                )
                if eta_minutes:
                    lines.append(f"Примерное время прибытия: {eta_minutes} мин")

            if route.driver_name:
                lines.append(f"Водитель: {route.driver_name}")

            lines.append("")
            lines.append("Пожалуйста, будьте готовы к указанному времени.")

        else:
            lines = [
                "Your driver is on the way!",
                "",
                f"Pickup time: *{stop.eta}*" if stop.eta else "",
                f"Meeting point: {stop.pickup_point or stop.address}"
            ]

            if driver_position:
                eta_minutes = self._calculate_eta_from_position(
                    driver_position, stop
                )
                if eta_minutes:
                    lines.append(f"Estimated arrival: {eta_minutes} min")

            if route.driver_name:
                lines.append(f"Driver: {route.driver_name}")

            lines.append("")
            lines.append("Please be ready at the specified time.")

        return "\n".join([l for l in lines if l])

    # ═══════════════════════════════════════════════════════════════
    # DEEP LINKS
    # ═══════════════════════════════════════════════════════════════

    def generate_google_maps_link(self, route: Route) -> str:
        """
        Генерация deep link для Google Maps с маршрутом.

        Args:
            route: Маршрут

        Returns:
            URL для Google Maps
        """
        if not route.stops:
            return ""

        # Формат: https://www.google.com/maps/dir/origin/waypoint1/waypoint2/destination

        base_url = "https://www.google.com/maps/dir/"

        points = []
        for stop in route.stops:
            if stop.lat and stop.lng:
                points.append(f"{stop.lat},{stop.lng}")
            elif stop.address:
                points.append(quote(stop.address))

        return base_url + "/".join(points)

    def generate_waze_link(self, route: Route) -> str:
        """
        Генерация deep link для Waze.

        Args:
            route: Маршрут

        Returns:
            URL для Waze
        """
        if not route.stops:
            return ""

        # Waze поддерживает только одну точку назначения
        # Используем последнюю остановку
        last_stop = route.stops[-1]

        if last_stop.lat and last_stop.lng:
            return f"https://waze.com/ul?ll={last_stop.lat},{last_stop.lng}&navigate=yes"
        elif last_stop.address:
            return f"https://waze.com/ul?q={quote(last_stop.address)}&navigate=yes"

        return ""

    def generate_apple_maps_link(self, route: Route) -> str:
        """
        Генерация deep link для Apple Maps.

        Args:
            route: Маршрут

        Returns:
            URL для Apple Maps
        """
        if len(route.stops) < 2:
            return ""

        origin = route.stops[0]
        dest = route.stops[-1]

        params = {
            "saddr": f"{origin.lat},{origin.lng}" if origin.lat else origin.address,
            "daddr": f"{dest.lat},{dest.lng}" if dest.lat else dest.address,
            "dirflg": "d"  # driving
        }

        return f"https://maps.apple.com/?{urlencode(params)}"

    # ═══════════════════════════════════════════════════════════════
    # МОНИТОРИНГ
    # ═══════════════════════════════════════════════════════════════

    def update_driver_position(
        self,
        driver_phone: str,
        lat: float,
        lng: float,
        speed_kmh: Optional[float] = None,
        heading: Optional[int] = None
    ) -> DriverPosition:
        """
        Обновить позицию водителя.

        Args:
            driver_phone: Телефон водителя
            lat: Широта
            lng: Долгота
            speed_kmh: Скорость
            heading: Направление

        Returns:
            DriverPosition объект
        """
        position = DriverPosition(
            driver_phone=driver_phone,
            lat=lat,
            lng=lng,
            timestamp=datetime.now().isoformat(),
            speed_kmh=speed_kmh,
            heading=heading
        )

        # Сохранение позиции
        positions_file = ROUTES_DIR / "positions.json"
        positions = {}

        if positions_file.exists():
            try:
                with open(positions_file, 'r', encoding='utf-8') as f:
                    positions = json.load(f)
            except Exception:
                pass

        positions[driver_phone] = asdict(position)

        with open(positions_file, 'w', encoding='utf-8') as f:
            json.dump(positions, f, ensure_ascii=False, indent=2)

        return position

    def get_driver_position(self, driver_phone: str) -> Optional[DriverPosition]:
        """Получить последнюю позицию водителя."""
        positions_file = ROUTES_DIR / "positions.json"

        if not positions_file.exists():
            return None

        try:
            with open(positions_file, 'r', encoding='utf-8') as f:
                positions = json.load(f)

            if driver_phone in positions:
                return DriverPosition(**positions[driver_phone])

        except Exception as e:
            logger.error(f"Failed to get driver position: {e}")

        return None

    def _calculate_eta_from_position(
        self,
        position: DriverPosition,
        stop: RouteStop
    ) -> Optional[int]:
        """Расчёт ETA от текущей позиции до остановки."""
        if not self.gmaps or not stop.lat or not stop.lng:
            return None

        try:
            result = self.gmaps.directions(
                origin=f"{position.lat},{position.lng}",
                destination=f"{stop.lat},{stop.lng}",
                mode="driving",
                departure_time=datetime.now()
            )

            if result:
                leg = result[0]["legs"][0]
                duration_s = leg.get("duration_in_traffic", leg["duration"])["value"]
                return round(duration_s / 60)

        except Exception as e:
            logger.error(f"ETA calculation failed: {e}")

        return None

    def check_route_progress(
        self,
        route: Route,
        position: DriverPosition
    ) -> Dict[str, Any]:
        """
        Проверка прогресса маршрута.

        Args:
            route: Маршрут
            position: Позиция водителя

        Returns:
            Информация о прогрессе
        """
        progress = {
            "current_stop_index": 0,
            "next_stop": None,
            "eta_to_next": None,
            "completed_stops": 0,
            "remaining_stops": len(route.stops),
            "estimated_completion_time": None
        }

        # Поиск ближайшей остановки
        min_distance = float('inf')
        closest_index = 0

        for i, stop in enumerate(route.stops):
            if stop.status == "completed":
                progress["completed_stops"] += 1
                continue

            if stop.lat and stop.lng:
                distance = self._haversine_distance(
                    position.lat, position.lng,
                    stop.lat, stop.lng
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_index = i

        progress["current_stop_index"] = closest_index
        progress["remaining_stops"] = len(route.stops) - progress["completed_stops"]

        if closest_index < len(route.stops):
            next_stop = route.stops[closest_index]
            progress["next_stop"] = next_stop.name

            eta = self._calculate_eta_from_position(position, next_stop)
            if eta:
                progress["eta_to_next"] = eta

        return progress

    def _haversine_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Расчёт расстояния между точками (км)."""
        import math

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

    # ═══════════════════════════════════════════════════════════════
    # ОТЧЁТЫ
    # ═══════════════════════════════════════════════════════════════

    def generate_daily_report(
        self,
        driver_phone: str,
        date: Optional[str] = None,
        fuel_consumption: float = DEFAULT_FUEL_CONSUMPTION
    ) -> DailyReport:
        """
        Генерация дневного отчёта водителя.

        Args:
            driver_phone: Телефон водителя
            date: Дата (YYYY-MM-DD), по умолчанию сегодня
            fuel_consumption: Расход топлива л/100км

        Returns:
            DailyReport объект
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        report = DailyReport(
            driver_phone=driver_phone,
            date=date
        )

        # Поиск маршрутов за день
        for route_file in ROUTES_DIR.glob("R*.json"):
            try:
                with open(route_file, 'r', encoding='utf-8') as f:
                    route_data = json.load(f)

                # Проверка даты и водителя
                route_date = route_data.get("created_at", "")[:10]
                if route_date != date:
                    continue
                if route_data.get("driver_phone") != driver_phone:
                    continue

                # Только завершённые маршруты
                if route_data.get("status") != "completed":
                    continue

                report.routes.append(route_data["id"])
                report.routes_count += 1
                report.total_distance_km += route_data.get("total_distance_km", 0)
                report.total_duration_minutes += route_data.get("total_duration_minutes", 0)

                # Подсчёт выполненных остановок
                for stop in route_data.get("stops", []):
                    if stop.get("status") == "completed":
                        report.stops_completed += 1

            except Exception as e:
                logger.error(f"Error processing route file {route_file}: {e}")

        # Расчёт расхода топлива
        report.fuel_consumption_liters = round(
            report.total_distance_km * fuel_consumption / 100, 2
        )
        report.fuel_cost_aed = round(
            report.fuel_consumption_liters * FUEL_PRICE_AED, 2
        )

        # Имя водителя из базы
        if driver_phone in self.drivers:
            report.driver_name = self.drivers[driver_phone].get("name")

        # Сохранение отчёта
        self._save_daily_report(report)

        return report

    def _save_daily_report(self, report: DailyReport):
        """Сохранить дневной отчёт."""
        report_file = DAILY_REPORTS_DIR / f"{report.driver_phone}_{report.date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)

    def format_daily_report(
        self,
        report: DailyReport,
        language: str = "ru"
    ) -> str:
        """
        Форматирование дневного отчёта.

        Args:
            report: Отчёт
            language: Язык

        Returns:
            Форматированный текст
        """
        if language == "ru":
            lines = [
                f"*ОТЧЁТ ВОДИТЕЛЯ*",
                f"Дата: {report.date}",
                f"Водитель: {report.driver_name or report.driver_phone}",
                "",
                f"Маршрутов: {report.routes_count}",
                f"Остановок выполнено: {report.stops_completed}",
                f"Пробег: {report.total_distance_km} км",
                f"Время в пути: {report.total_duration_minutes} мин",
                "",
                f"*Расход топлива:*",
                f"Литров: {report.fuel_consumption_liters}",
                f"Стоимость: {report.fuel_cost_aed} AED"
            ]
        else:
            lines = [
                f"*DRIVER REPORT*",
                f"Date: {report.date}",
                f"Driver: {report.driver_name or report.driver_phone}",
                "",
                f"Routes: {report.routes_count}",
                f"Stops completed: {report.stops_completed}",
                f"Distance: {report.total_distance_km} km",
                f"Time: {report.total_duration_minutes} min",
                "",
                f"*Fuel consumption:*",
                f"Liters: {report.fuel_consumption_liters}",
                f"Cost: {report.fuel_cost_aed} AED"
            ]

        return "\n".join(lines)

    def get_period_statistics(
        self,
        driver_phone: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Статистика за период.

        Args:
            driver_phone: Телефон водителя
            start_date: Начало периода (YYYY-MM-DD)
            end_date: Конец периода (YYYY-MM-DD)

        Returns:
            Словарь со статистикой
        """
        stats = {
            "driver_phone": driver_phone,
            "period": f"{start_date} - {end_date}",
            "total_routes": 0,
            "total_distance_km": 0,
            "total_duration_minutes": 0,
            "total_fuel_liters": 0,
            "total_fuel_cost_aed": 0,
            "total_stops": 0,
            "average_distance_per_route": 0,
            "average_duration_per_route": 0,
            "busiest_day": None,
            "daily_breakdown": []
        }

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        current = start

        max_routes = 0

        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            report = self.generate_daily_report(driver_phone, date_str)

            if report.routes_count > 0:
                stats["daily_breakdown"].append({
                    "date": date_str,
                    "routes": report.routes_count,
                    "distance": report.total_distance_km,
                    "duration": report.total_duration_minutes
                })

                stats["total_routes"] += report.routes_count
                stats["total_distance_km"] += report.total_distance_km
                stats["total_duration_minutes"] += report.total_duration_minutes
                stats["total_fuel_liters"] += report.fuel_consumption_liters
                stats["total_fuel_cost_aed"] += report.fuel_cost_aed
                stats["total_stops"] += report.stops_completed

                if report.routes_count > max_routes:
                    max_routes = report.routes_count
                    stats["busiest_day"] = date_str

            current += timedelta(days=1)

        # Средние значения
        if stats["total_routes"] > 0:
            stats["average_distance_per_route"] = round(
                stats["total_distance_km"] / stats["total_routes"], 1
            )
            stats["average_duration_per_route"] = round(
                stats["total_duration_minutes"] / stats["total_routes"]
            )

        return stats

    # ═══════════════════════════════════════════════════════════════
    # БАЗА ОТЕЛЕЙ
    # ═══════════════════════════════════════════════════════════════

    def find_hotel(
        self,
        query: str,
        city: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Поиск отеля в базе.

        Args:
            query: Название или часть названия
            city: Город (dubai, abu_dhabi, etc.)

        Returns:
            Данные отеля или None
        """
        query_lower = query.lower()

        cities_to_search = [city] if city else self.hotels.keys()

        for city_name in cities_to_search:
            if city_name not in self.hotels:
                continue

            for area, hotels in self.hotels[city_name].items():
                for hotel in hotels:
                    if query_lower in hotel["name"].lower():
                        return {**hotel, "city": city_name, "area": area}

        return None

    def get_hotels_by_area(
        self,
        city: str,
        area: str
    ) -> List[Dict]:
        """
        Получить отели по району.

        Args:
            city: Город
            area: Район

        Returns:
            Список отелей
        """
        if city in self.hotels and area in self.hotels[city]:
            return self.hotels[city][area]
        return []

    def add_hotel(
        self,
        city: str,
        area: str,
        name: str,
        address: str,
        lat: float,
        lng: float,
        pickup_point: str = "Main entrance",
        default_pickup_time: str = "09:00",
        stars: int = 4
    ) -> bool:
        """
        Добавить отель в базу.

        Args:
            city: Город
            area: Район
            name: Название
            address: Адрес
            lat: Широта
            lng: Долгота
            pickup_point: Точка пикапа
            default_pickup_time: Время пикапа по умолчанию
            stars: Звёздность

        Returns:
            True если успешно
        """
        if city not in self.hotels:
            self.hotels[city] = {}

        if area not in self.hotels[city]:
            self.hotels[city][area] = []

        hotel = {
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
            "pickup_point": pickup_point,
            "default_pickup_time": default_pickup_time,
            "stars": stars
        }

        self.hotels[city][area].append(hotel)
        self._save_hotels(self.hotels)

        return True

    def list_all_hotels(self) -> List[Dict]:
        """Получить полный список отелей."""
        all_hotels = []

        for city, areas in self.hotels.items():
            for area, hotels in areas.items():
                for hotel in hotels:
                    all_hotels.append({
                        **hotel,
                        "city": city,
                        "area": area
                    })

        return all_hotels

    # ═══════════════════════════════════════════════════════════════
    # ВОДИТЕЛИ
    # ═══════════════════════════════════════════════════════════════

    def add_driver(
        self,
        phone: str,
        name: str,
        vehicle_type: str = "car",
        vehicle_plate: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Добавить водителя.

        Args:
            phone: Телефон
            name: Имя
            vehicle_type: Тип транспорта
            vehicle_plate: Номер машины
            notes: Заметки

        Returns:
            Данные водителя
        """
        driver = {
            "phone": phone,
            "name": name,
            "vehicle_type": vehicle_type,
            "vehicle_plate": vehicle_plate,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "active": True
        }

        self.drivers[phone] = driver
        self._save_drivers(self.drivers)

        return driver

    def get_driver(self, phone: str) -> Optional[Dict]:
        """Получить данные водителя."""
        return self.drivers.get(phone)

    def list_drivers(self, active_only: bool = True) -> List[Dict]:
        """Список водителей."""
        drivers = list(self.drivers.values())
        if active_only:
            drivers = [d for d in drivers if d.get("active", True)]
        return drivers

    # ═══════════════════════════════════════════════════════════════
    # УТИЛИТЫ
    # ═══════════════════════════════════════════════════════════════

    def get_traffic_conditions(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Получить информацию о трафике.

        Args:
            origin: Начальная точка
            destination: Конечная точка

        Returns:
            Информация о трафике
        """
        if not self.gmaps:
            return {"error": "Google Maps not available"}

        try:
            result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode="driving",
                departure_time=datetime.now()
            )

            if not result:
                return {"error": "No route found"}

            leg = result[0]["legs"][0]

            normal_duration = leg["duration"]["value"]
            traffic_duration = leg.get("duration_in_traffic", {}).get("value", normal_duration)

            traffic_ratio = traffic_duration / normal_duration if normal_duration > 0 else 1

            if traffic_ratio < 1.1:
                traffic_level = "low"
            elif traffic_ratio < 1.3:
                traffic_level = "moderate"
            elif traffic_ratio < 1.5:
                traffic_level = "heavy"
            else:
                traffic_level = "severe"

            return {
                "distance_km": round(leg["distance"]["value"] / 1000, 1),
                "normal_duration_min": round(normal_duration / 60),
                "traffic_duration_min": round(traffic_duration / 60),
                "delay_min": round((traffic_duration - normal_duration) / 60),
                "traffic_level": traffic_level,
                "traffic_ratio": round(traffic_ratio, 2)
            }

        except Exception as e:
            return {"error": str(e)}

    def create_tour_route(
        self,
        driver_phone: str,
        tour_type: str,
        pickup_hotel: str,
        attractions: List[str],
        start_time: str = "09:00"
    ) -> Route:
        """
        Создать маршрут для тура.

        Args:
            driver_phone: Телефон водителя
            tour_type: Тип тура (dubai_city, abu_dhabi, etc.)
            pickup_hotel: Отель пикапа
            attractions: Список достопримечательностей
            start_time: Время начала

        Returns:
            Route объект
        """
        stops = []

        # Пикап из отеля
        hotel = self.find_hotel(pickup_hotel)
        if hotel:
            stops.append({
                "name": f"Pickup: {hotel['name']}",
                "address": hotel["address"],
                "lat": hotel["lat"],
                "lng": hotel["lng"],
                "pickup_point": hotel["pickup_point"],
                "duration_minutes": 10
            })

        # Достопримечательности
        city = "dubai" if tour_type.startswith("dubai") else "abu_dhabi"
        city_attractions = POPULAR_ATTRACTIONS.get(city, {})

        for attr_name in attractions:
            if attr_name in city_attractions:
                attr = city_attractions[attr_name]
                stops.append({
                    "name": attr_name,
                    "address": attr["address"],
                    "lat": attr["lat"],
                    "lng": attr["lng"],
                    "duration_minutes": attr["visit_duration"]
                })

        # Возврат в отель
        if hotel:
            stops.append({
                "name": f"Drop-off: {hotel['name']}",
                "address": hotel["address"],
                "lat": hotel["lat"],
                "lng": hotel["lng"],
                "duration_minutes": 5
            })

        return self.create_route(
            driver_phone=driver_phone,
            stops=stops,
            start_time=start_time,
            optimize=True
        )


# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════

def main():
    """CLI интерфейс."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Управление маршрутами водителей"
    )

    subparsers = parser.add_subparsers(dest="command", help="Команда")

    # Создание маршрута
    create_parser = subparsers.add_parser("create", help="Создать маршрут")
    create_parser.add_argument("--driver", "-d", required=True, help="Телефон водителя")
    create_parser.add_argument("--stops", "-s", required=True, help="JSON файл с остановками")
    create_parser.add_argument("--time", "-t", help="Время начала (HH:MM)")
    create_parser.add_argument("--no-optimize", action="store_true", help="Не оптимизировать")

    # Просмотр маршрута
    view_parser = subparsers.add_parser("view", help="Просмотр маршрута")
    view_parser.add_argument("route_id", help="ID маршрута")
    view_parser.add_argument("--format", "-f", choices=["whatsapp", "telegram", "json"],
                            default="whatsapp", help="Формат вывода")

    # Отчёт водителя
    report_parser = subparsers.add_parser("report", help="Отчёт водителя")
    report_parser.add_argument("--driver", "-d", required=True, help="Телефон водителя")
    report_parser.add_argument("--date", help="Дата (YYYY-MM-DD)")

    # Список отелей
    hotels_parser = subparsers.add_parser("hotels", help="Список отелей")
    hotels_parser.add_argument("--city", "-c", help="Город")
    hotels_parser.add_argument("--area", "-a", help="Район")
    hotels_parser.add_argument("--search", "-s", help="Поиск по названию")

    # Добавление водителя
    driver_parser = subparsers.add_parser("add-driver", help="Добавить водителя")
    driver_parser.add_argument("--phone", "-p", required=True, help="Телефон")
    driver_parser.add_argument("--name", "-n", required=True, help="Имя")
    driver_parser.add_argument("--vehicle", "-v", default="car", help="Тип транспорта")
    driver_parser.add_argument("--plate", help="Номер машины")

    # Проверка трафика
    traffic_parser = subparsers.add_parser("traffic", help="Проверить трафик")
    traffic_parser.add_argument("--from", dest="origin", required=True, help="Откуда")
    traffic_parser.add_argument("--to", dest="destination", required=True, help="Куда")

    args = parser.parse_args()

    manager = DriverRouteManager()

    if args.command == "create":
        with open(args.stops, 'r', encoding='utf-8') as f:
            stops = json.load(f)

        route = manager.create_route(
            driver_phone=args.driver,
            stops=stops,
            start_time=args.time,
            optimize=not args.no_optimize
        )

        print(f"Маршрут создан: {route.id}")
        print(manager.format_for_whatsapp(route))

    elif args.command == "view":
        route = manager.load_route(args.route_id)
        if not route:
            print(f"Маршрут {args.route_id} не найден")
            return

        if args.format == "whatsapp":
            print(manager.format_for_whatsapp(route))
        elif args.format == "telegram":
            print(manager.format_for_telegram(route))
        else:
            print(json.dumps(asdict(route), ensure_ascii=False, indent=2))

    elif args.command == "report":
        report = manager.generate_daily_report(args.driver, args.date)
        print(manager.format_daily_report(report))

    elif args.command == "hotels":
        if args.search:
            hotel = manager.find_hotel(args.search, args.city)
            if hotel:
                print(json.dumps(hotel, ensure_ascii=False, indent=2))
            else:
                print("Отель не найден")
        elif args.city and args.area:
            hotels = manager.get_hotels_by_area(args.city, args.area)
            for h in hotels:
                print(f"- {h['name']} ({h['stars']}*)")
        else:
            hotels = manager.list_all_hotels()
            print(f"Всего отелей в базе: {len(hotels)}")
            for h in hotels[:10]:
                print(f"- {h['name']} ({h['city']}, {h['area']})")
            if len(hotels) > 10:
                print(f"... и ещё {len(hotels) - 10}")

    elif args.command == "add-driver":
        driver = manager.add_driver(
            phone=args.phone,
            name=args.name,
            vehicle_type=args.vehicle,
            vehicle_plate=args.plate
        )
        print(f"Водитель добавлен: {driver['name']}")

    elif args.command == "traffic":
        traffic = manager.get_traffic_conditions(args.origin, args.destination)
        print(json.dumps(traffic, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
