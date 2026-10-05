"""
Google Maps Route Calculator
Пример работы с Google Maps API для расчёта маршрутов

Функционал:
1. Расчёт маршрута между точками
2. Учёт пробок
3. Расчёт времени прибытия
4. Оптимизация маршрута для нескольких точек

Использование:
    python google_maps_route.py
"""

import os
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= Configuration =============

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "your_api_key")
GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"

# ============= Data Classes =============

@dataclass
class Location:
    name: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None

@dataclass
class RouteStep:
    instruction: str
    distance: str
    duration: str
    start_location: Tuple[float, float]
    end_location: Tuple[float, float]

@dataclass
class Route:
    origin: str
    destination: str
    distance: str
    duration: str
    duration_in_traffic: Optional[str]
    steps: List[RouteStep]
    polyline: str

@dataclass
class DistanceInfo:
    origin: str
    destination: str
    distance: str
    duration: str

# ============= Google Maps Client =============

class GoogleMapsClient:
    """Клиент для работы с Google Maps API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = GOOGLE_MAPS_BASE_URL

    def _request(self, endpoint: str, params: Dict) -> Dict:
        """Выполнить запрос к API"""
        params["key"] = self.api_key

        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            logger.error(f"Google Maps API error: {data.get('status')}")
            raise Exception(f"Google Maps API error: {data.get('error_message', data.get('status'))}")

        return data

    def geocode(self, address: str) -> Location:
        """
        Преобразовать адрес в координаты

        Args:
            address: Адрес для геокодирования
        """
        data = self._request("geocode/json", {
            "address": address,
            "language": "ru"
        })

        if not data.get("results"):
            raise ValueError(f"Address not found: {address}")

        result = data["results"][0]
        location = result["geometry"]["location"]

        return Location(
            name=result.get("formatted_address", address),
            address=result.get("formatted_address", address),
            lat=location["lat"],
            lng=location["lng"]
        )

    def reverse_geocode(self, lat: float, lng: float) -> Location:
        """
        Преобразовать координаты в адрес

        Args:
            lat: Широта
            lng: Долгота
        """
        data = self._request("geocode/json", {
            "latlng": f"{lat},{lng}",
            "language": "ru"
        })

        if not data.get("results"):
            raise ValueError(f"Location not found: {lat}, {lng}")

        result = data["results"][0]

        return Location(
            name=result.get("formatted_address", ""),
            address=result.get("formatted_address", ""),
            lat=lat,
            lng=lng
        )

    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        departure_time: Optional[datetime] = None,
        avoid: Optional[List[str]] = None,
        waypoints: Optional[List[str]] = None
    ) -> Route:
        """
        Получить маршрут между точками

        Args:
            origin: Начальная точка (адрес или координаты)
            destination: Конечная точка
            mode: Способ передвижения (driving, walking, bicycling, transit)
            departure_time: Время отправления (для учёта пробок)
            avoid: Что избегать (tolls, highways, ferries)
            waypoints: Промежуточные точки
        """
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "language": "ru"
        }

        if departure_time:
            params["departure_time"] = int(departure_time.timestamp())
        elif mode == "driving":
            # По умолчанию используем текущее время
            params["departure_time"] = "now"

        if avoid:
            params["avoid"] = "|".join(avoid)

        if waypoints:
            params["waypoints"] = "|".join(waypoints)

        data = self._request("directions/json", params)

        if not data.get("routes"):
            raise ValueError("Route not found")

        route_data = data["routes"][0]
        leg = route_data["legs"][0]

        steps = []
        for step in leg.get("steps", []):
            steps.append(RouteStep(
                instruction=step.get("html_instructions", ""),
                distance=step["distance"]["text"],
                duration=step["duration"]["text"],
                start_location=(
                    step["start_location"]["lat"],
                    step["start_location"]["lng"]
                ),
                end_location=(
                    step["end_location"]["lat"],
                    step["end_location"]["lng"]
                )
            ))

        return Route(
            origin=leg["start_address"],
            destination=leg["end_address"],
            distance=leg["distance"]["text"],
            duration=leg["duration"]["text"],
            duration_in_traffic=leg.get("duration_in_traffic", {}).get("text"),
            steps=steps,
            polyline=route_data["overview_polyline"]["points"]
        )

    def get_distance_matrix(
        self,
        origins: List[str],
        destinations: List[str],
        mode: str = "driving"
    ) -> List[DistanceInfo]:
        """
        Получить матрицу расстояний между несколькими точками

        Args:
            origins: Список начальных точек
            destinations: Список конечных точек
            mode: Способ передвижения
        """
        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": mode,
            "language": "ru",
            "departure_time": "now"
        }

        data = self._request("distancematrix/json", params)

        results = []
        for i, origin in enumerate(data["origin_addresses"]):
            for j, destination in enumerate(data["destination_addresses"]):
                element = data["rows"][i]["elements"][j]
                if element["status"] == "OK":
                    results.append(DistanceInfo(
                        origin=origin,
                        destination=destination,
                        distance=element["distance"]["text"],
                        duration=element.get("duration_in_traffic", element["duration"])["text"]
                    ))

        return results

    def optimize_route(
        self,
        start: str,
        end: str,
        waypoints: List[str]
    ) -> Tuple[Route, List[str]]:
        """
        Оптимизировать маршрут через несколько точек

        Args:
            start: Начальная точка
            end: Конечная точка
            waypoints: Промежуточные точки

        Returns:
            (Route, optimized_order) - маршрут и оптимизированный порядок точек
        """
        params = {
            "origin": start,
            "destination": end,
            "waypoints": "optimize:true|" + "|".join(waypoints),
            "mode": "driving",
            "language": "ru",
            "departure_time": "now"
        }

        data = self._request("directions/json", params)

        if not data.get("routes"):
            raise ValueError("Route not found")

        route_data = data["routes"][0]

        # Получить оптимизированный порядок
        optimized_order = route_data.get("waypoint_order", list(range(len(waypoints))))
        optimized_waypoints = [waypoints[i] for i in optimized_order]

        # Общее расстояние и время
        total_distance = 0
        total_duration = 0
        all_steps = []

        for leg in route_data["legs"]:
            total_distance += leg["distance"]["value"]
            total_duration += leg.get("duration_in_traffic", leg["duration"])["value"]

            for step in leg.get("steps", []):
                all_steps.append(RouteStep(
                    instruction=step.get("html_instructions", ""),
                    distance=step["distance"]["text"],
                    duration=step["duration"]["text"],
                    start_location=(
                        step["start_location"]["lat"],
                        step["start_location"]["lng"]
                    ),
                    end_location=(
                        step["end_location"]["lat"],
                        step["end_location"]["lng"]
                    )
                ))

        route = Route(
            origin=start,
            destination=end,
            distance=f"{total_distance / 1000:.1f} км",
            duration=f"{total_duration // 60} мин",
            duration_in_traffic=f"{total_duration // 60} мин",
            steps=all_steps,
            polyline=route_data["overview_polyline"]["points"]
        )

        return route, optimized_waypoints

# ============= Tourism-specific Functions =============

def calculate_tour_route(
    client: GoogleMapsClient,
    hotel: str,
    attractions: List[str],
    return_to_hotel: bool = True
) -> Dict:
    """
    Рассчитать маршрут тура от отеля через достопримечательности

    Args:
        client: Google Maps клиент
        hotel: Адрес отеля
        attractions: Список достопримечательностей
        return_to_hotel: Вернуться в отель в конце
    """
    end = hotel if return_to_hotel else attractions[-1]
    waypoints = attractions if return_to_hotel else attractions[:-1]

    route, optimized_order = client.optimize_route(
        start=hotel,
        end=end,
        waypoints=waypoints
    )

    return {
        "route": route,
        "optimized_attractions": optimized_order,
        "total_distance": route.distance,
        "total_duration": route.duration_in_traffic or route.duration
    }


def calculate_transfer_eta(
    client: GoogleMapsClient,
    driver_location: str,
    pickup_location: str,
    destination: str
) -> Dict:
    """
    Рассчитать ETA для трансфера

    Args:
        client: Google Maps клиент
        driver_location: Текущее местоположение водителя
        pickup_location: Место посадки клиента
        destination: Пункт назначения
    """
    # Маршрут до клиента
    to_pickup = client.get_directions(driver_location, pickup_location)

    # Маршрут до пункта назначения
    to_destination = client.get_directions(pickup_location, destination)

    return {
        "eta_to_pickup": to_pickup.duration_in_traffic or to_pickup.duration,
        "distance_to_pickup": to_pickup.distance,
        "eta_to_destination": to_destination.duration_in_traffic or to_destination.duration,
        "distance_to_destination": to_destination.distance,
        "total_distance": f"{float(to_pickup.distance.replace(' км', '').replace(',', '.')) + float(to_destination.distance.replace(' км', '').replace(',', '.')):.1f} км"
    }

# ============= Usage Example =============

def main():
    # Создаём клиент (используем демо без реального ключа)
    if GOOGLE_MAPS_API_KEY == "your_api_key":
        print("⚠️  Демо режим (без реального API ключа)")
        print("   Установите GOOGLE_MAPS_API_KEY для реальных запросов")
        print()

        # Демо данные
        print("=" * 50)
        print("Пример: Маршрут тура по Дубаю")
        print("=" * 50)

        print("""
📍 Отель: Atlantis The Palm
📍 Достопримечательности:
   1. Burj Khalifa
   2. Dubai Mall
   3. Dubai Marina
   4. Palm Jumeirah

🗺️ Оптимизированный маршрут:
   Atlantis The Palm → Palm Jumeirah → Dubai Marina →
   → Dubai Mall → Burj Khalifa → Atlantis The Palm

📊 Статистика:
   Общее расстояние: 45.3 км
   Время в пути: 1 час 15 мин (с учётом пробок)
""")
        return

    client = GoogleMapsClient(GOOGLE_MAPS_API_KEY)

    print("=" * 50)
    print("Расчёт маршрута тура по Дубаю")
    print("=" * 50)

    # Входные данные
    hotel = "Atlantis The Palm, Dubai"
    attractions = [
        "Burj Khalifa, Dubai",
        "Dubai Mall, Dubai",
        "Dubai Marina, Dubai",
        "Palm Jumeirah, Dubai"
    ]

    # Расчёт оптимального маршрута
    result = calculate_tour_route(client, hotel, attractions)

    print(f"\n📍 Отель: {hotel}")
    print(f"\n📍 Оптимизированный порядок:")
    for i, attr in enumerate(result["optimized_attractions"], 1):
        print(f"   {i}. {attr}")

    print(f"\n📊 Статистика:")
    print(f"   Общее расстояние: {result['total_distance']}")
    print(f"   Время в пути: {result['total_duration']}")

    # Расчёт ETA для трансфера
    print("\n" + "=" * 50)
    print("Расчёт ETA трансфера")
    print("=" * 50)

    eta = calculate_transfer_eta(
        client,
        driver_location="Dubai Internet City, Dubai",
        pickup_location="JBR Beach, Dubai",
        destination="Dubai Marina Yacht Club, Dubai"
    )

    print(f"\n🚗 Водитель → Клиент:")
    print(f"   Расстояние: {eta['distance_to_pickup']}")
    print(f"   Время: {eta['eta_to_pickup']}")

    print(f"\n🚗 Клиент → Пункт назначения:")
    print(f"   Расстояние: {eta['distance_to_destination']}")
    print(f"   Время: {eta['eta_to_destination']}")

if __name__ == "__main__":
    main()
