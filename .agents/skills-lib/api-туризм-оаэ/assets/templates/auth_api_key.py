"""
API Key Authentication Template
Шаблон для аутентификации через API Key

Использование:
    from auth_api_key import APIClient
    client = APIClient("https://api.example.com", "your_api_key")
    response = client.get("/tours")
"""

import os
import requests
from typing import Optional, Dict, Any
from functools import wraps
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= API Client with API Key Auth =============

class APIClient:
    """Клиент для работы с API через API Key аутентификацию"""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        key_header: str = "X-API-Key",
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("API_KEY")
        self.key_header = key_header
        self.timeout = timeout
        self.session = requests.Session()

        if not self.api_key:
            raise ValueError("API key is required")

        # Установить header по умолчанию
        self.session.headers.update({
            self.key_header: self.api_key,
            "Content-Type": "application/json"
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """Выполнить HTTP запрос"""
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"{method} {url}")

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data,
            timeout=self.timeout,
            **kwargs
        )

        logger.debug(f"Response: {response.status_code}")

        return response

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """GET запрос"""
        response = self._make_request("GET", endpoint, params=params, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict, **kwargs) -> Dict:
        """POST запрос"""
        response = self._make_request("POST", endpoint, data=data, **kwargs)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, data: Dict, **kwargs) -> Dict:
        """PUT запрос"""
        response = self._make_request("PUT", endpoint, data=data, **kwargs)
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint: str, data: Dict, **kwargs) -> Dict:
        """PATCH запрос"""
        response = self._make_request("PATCH", endpoint, data=data, **kwargs)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str, **kwargs) -> bool:
        """DELETE запрос"""
        response = self._make_request("DELETE", endpoint, **kwargs)
        response.raise_for_status()
        return response.status_code in [200, 204]

# ============= Rate Limiting Decorator =============

def rate_limited(max_per_second: float):
    """Декоратор для ограничения частоты запросов"""
    min_interval = 1.0 / max_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait = min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

# ============= Retry Decorator =============

def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Декоратор для повторных попыток при ошибках"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception
        return wrapper
    return decorator

# ============= Example: Viator API Client =============

class ViatorClient(APIClient):
    """Клиент для Viator API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            base_url="https://api.viator.com/partner",
            api_key=api_key or os.getenv("VIATOR_API_KEY"),
            key_header="exp-api-key"
        )

    @rate_limited(10)  # Max 10 запросов в секунду
    @retry_on_error(max_retries=3)
    def search_tours(self, destination: str, start_date: str, end_date: str) -> Dict:
        """Поиск туров"""
        return self.post("/search/products", {
            "destId": destination,
            "startDate": start_date,
            "endDate": end_date
        })

    def get_tour_details(self, product_code: str) -> Dict:
        """Получить детали тура"""
        return self.get(f"/products/{product_code}")

    def check_availability(self, product_code: str, date: str, travelers: int) -> Dict:
        """Проверить доступность"""
        return self.post("/availability/check", {
            "productCode": product_code,
            "travelDate": date,
            "travelers": travelers
        })

# ============= Example: Google Maps Client =============

class GoogleMapsClient:
    """Клиент для Google Maps API (через query parameter)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api"

        if not self.api_key:
            raise ValueError("Google Maps API key is required")

    def get_directions(self, origin: str, destination: str, mode: str = "driving") -> Dict:
        """Получить маршрут"""
        response = requests.get(
            f"{self.base_url}/directions/json",
            params={
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "language": "ru",
                "key": self.api_key
            }
        )
        response.raise_for_status()
        return response.json()

    def get_distance_matrix(self, origins: list, destinations: list) -> Dict:
        """Получить матрицу расстояний"""
        response = requests.get(
            f"{self.base_url}/distancematrix/json",
            params={
                "origins": "|".join(origins),
                "destinations": "|".join(destinations),
                "language": "ru",
                "key": self.api_key
            }
        )
        response.raise_for_status()
        return response.json()

# ============= Usage Example =============

if __name__ == "__main__":
    # Пример использования базового клиента
    client = APIClient(
        base_url="https://api.example.com",
        api_key="your_api_key"
    )

    try:
        # GET запрос
        tours = client.get("/tours", params={"city": "dubai"})
        print(f"Found {len(tours)} tours")

        # POST запрос
        booking = client.post("/bookings", data={
            "tour_id": "safari-001",
            "date": "2026-03-15",
            "adults": 2
        })
        print(f"Booking created: {booking['id']}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
