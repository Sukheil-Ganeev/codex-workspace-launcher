"""
Tour Booking Search System
Пример поиска и бронирования туров через API

Функционал:
1. Поиск туров по параметрам
2. Проверка доступности
3. Создание бронирования
4. Получение ваучера

Использование:
    python booking_search.py
"""

import os
import requests
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import date, datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= Configuration =============

# Viator API (пример)
VIATOR_API_KEY = os.getenv("VIATOR_API_KEY", "your_api_key")
VIATOR_BASE_URL = "https://api.viator.com/partner"

# ============= Data Classes =============

@dataclass
class Tour:
    id: str
    name: str
    description: str
    price: float
    currency: str
    duration_hours: float
    rating: float
    review_count: int
    images: List[str]
    included: List[str]
    excluded: List[str]

@dataclass
class Availability:
    date: str
    available: bool
    slots: int
    price: float

@dataclass
class Booking:
    id: str
    tour_id: str
    date: str
    status: str
    total_price: float
    voucher_url: Optional[str] = None

# ============= API Client =============

class TourAPIClient:
    """Клиент для работы с API туристических платформ"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "exp-api-key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Выполнить запрос к API"""
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"{method} {url}")

        response = self.session.request(method, url, **kwargs)

        if response.status_code == 429:
            logger.warning("Rate limit exceeded, waiting...")
            import time
            time.sleep(60)
            response = self.session.request(method, url, **kwargs)

        response.raise_for_status()
        return response.json()

    def search_tours(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "TRAVELER_RATING"
    ) -> List[Tour]:
        """
        Поиск туров по параметрам

        Args:
            destination: Город/регион (например "dubai")
            start_date: Дата начала (YYYY-MM-DD)
            end_date: Дата окончания (YYYY-MM-DD)
            category: Категория (например "outdoor-activities")
            min_price: Минимальная цена
            max_price: Максимальная цена
            sort_by: Сортировка (TRAVELER_RATING, PRICE, DURATION)
        """

        search_params = {
            "destId": destination,
            "startDate": start_date,
            "endDate": end_date,
            "sortOrder": sort_by,
            "currencyCode": "AED"
        }

        if category:
            search_params["categoryId"] = category

        if min_price:
            search_params["priceFrom"] = min_price

        if max_price:
            search_params["priceTo"] = max_price

        data = self._request("POST", "/search/products", json=search_params)

        tours = []
        for item in data.get("products", []):
            tour = Tour(
                id=item["productCode"],
                name=item["title"],
                description=item.get("description", ""),
                price=item["price"]["fromPrice"],
                currency=item["price"]["currencyCode"],
                duration_hours=item.get("duration", {}).get("hours", 0),
                rating=item.get("rating", 0),
                review_count=item.get("reviewCount", 0),
                images=[img["url"] for img in item.get("images", [])],
                included=item.get("inclusions", []),
                excluded=item.get("exclusions", [])
            )
            tours.append(tour)

        logger.info(f"Found {len(tours)} tours in {destination}")
        return tours

    def get_tour_details(self, tour_id: str) -> Tour:
        """Получить детали тура"""

        data = self._request("GET", f"/products/{tour_id}")

        product = data["product"]
        return Tour(
            id=product["productCode"],
            name=product["title"],
            description=product.get("fullDescription", ""),
            price=product["price"]["fromPrice"],
            currency=product["price"]["currencyCode"],
            duration_hours=product.get("duration", {}).get("hours", 0),
            rating=product.get("rating", 0),
            review_count=product.get("reviewCount", 0),
            images=[img["url"] for img in product.get("images", [])],
            included=product.get("inclusions", []),
            excluded=product.get("exclusions", [])
        )

    def check_availability(
        self,
        tour_id: str,
        date: str,
        travelers: int
    ) -> Availability:
        """
        Проверить доступность тура на дату

        Args:
            tour_id: ID тура
            date: Дата (YYYY-MM-DD)
            travelers: Количество путешественников
        """

        params = {
            "productCode": tour_id,
            "travelDate": date,
            "paxMix": [{"ageBand": "ADULT", "numberOfTravelers": travelers}]
        }

        data = self._request("POST", "/availability/check", json=params)

        availability = data.get("availability", {})
        return Availability(
            date=date,
            available=availability.get("available", False),
            slots=availability.get("availableSlots", 0),
            price=availability.get("totalPrice", 0)
        )

    def create_booking(
        self,
        tour_id: str,
        date: str,
        adults: int,
        children: int = 0,
        customer_name: str = "",
        customer_email: str = "",
        customer_phone: str = ""
    ) -> Booking:
        """
        Создать бронирование

        Args:
            tour_id: ID тура
            date: Дата (YYYY-MM-DD)
            adults: Количество взрослых
            children: Количество детей
            customer_name: Имя клиента
            customer_email: Email клиента
            customer_phone: Телефон клиента
        """

        booking_data = {
            "productCode": tour_id,
            "travelDate": date,
            "paxMix": [
                {"ageBand": "ADULT", "numberOfTravelers": adults}
            ],
            "bookerInfo": {
                "firstName": customer_name.split()[0] if customer_name else "Guest",
                "lastName": customer_name.split()[-1] if customer_name else "Guest",
                "email": customer_email,
                "phone": customer_phone
            }
        }

        if children > 0:
            booking_data["paxMix"].append({
                "ageBand": "CHILD",
                "numberOfTravelers": children
            })

        data = self._request("POST", "/bookings", json=booking_data)

        booking = data.get("booking", {})
        return Booking(
            id=booking.get("bookingRef", ""),
            tour_id=tour_id,
            date=date,
            status=booking.get("status", "PENDING"),
            total_price=booking.get("totalPrice", 0),
            voucher_url=booking.get("voucherUrl")
        )

    def get_booking(self, booking_id: str) -> Booking:
        """Получить информацию о бронировании"""

        data = self._request("GET", f"/bookings/{booking_id}")

        booking = data.get("booking", {})
        return Booking(
            id=booking.get("bookingRef", ""),
            tour_id=booking.get("productCode", ""),
            date=booking.get("travelDate", ""),
            status=booking.get("status", ""),
            total_price=booking.get("totalPrice", 0),
            voucher_url=booking.get("voucherUrl")
        )

    def cancel_booking(self, booking_id: str, reason: str = "") -> bool:
        """Отменить бронирование"""

        data = self._request(
            "POST",
            f"/bookings/{booking_id}/cancel",
            json={"reason": reason}
        )

        return data.get("status") == "CANCELLED"

# ============= Mock Client for Testing =============

class MockTourAPIClient(TourAPIClient):
    """Мок-клиент для тестирования без реального API"""

    def __init__(self):
        self.api_key = "mock"
        self.base_url = "mock"

    def search_tours(self, destination: str, **kwargs) -> List[Tour]:
        return [
            Tour(
                id="SAFARI001",
                name="Дубай Сафари Делюкс",
                description="Незабываемое приключение в пустыне с ужином под звёздами",
                price=150,
                currency="AED",
                duration_hours=6,
                rating=4.8,
                review_count=1234,
                images=["https://example.com/safari.jpg"],
                included=["Трансфер", "Ужин", "Катание на верблюдах"],
                excluded=["Напитки", "Фото"]
            ),
            Tour(
                id="ABUDHABI001",
                name="Абу-Даби Гранд Тур",
                description="Полный день в столице ОАЭ",
                price=200,
                currency="AED",
                duration_hours=10,
                rating=4.9,
                review_count=567,
                images=["https://example.com/abudhabi.jpg"],
                included=["Трансфер", "Входные билеты", "Обед"],
                excluded=["Личные расходы"]
            )
        ]

    def check_availability(self, tour_id: str, date: str, travelers: int) -> Availability:
        return Availability(
            date=date,
            available=True,
            slots=10,
            price=150 * travelers
        )

    def create_booking(self, tour_id: str, **kwargs) -> Booking:
        import uuid
        return Booking(
            id=f"BK-{uuid.uuid4().hex[:6].upper()}",
            tour_id=tour_id,
            date=kwargs.get("date", "2026-03-15"),
            status="CONFIRMED",
            total_price=kwargs.get("adults", 1) * 150,
            voucher_url="https://example.com/voucher.pdf"
        )

# ============= Usage Example =============

def main():
    # Использовать мок для демо
    client = MockTourAPIClient()

    print("=" * 50)
    print("Поиск туров в Дубае")
    print("=" * 50)

    # 1. Поиск туров
    tours = client.search_tours(
        destination="dubai",
        start_date="2026-03-01",
        end_date="2026-03-31"
    )

    for tour in tours:
        print(f"\n📍 {tour.name}")
        print(f"   Цена: от {tour.price} {tour.currency}")
        print(f"   Длительность: {tour.duration_hours} часов")
        print(f"   Рейтинг: {tour.rating}⭐ ({tour.review_count} отзывов)")
        print(f"   Включено: {', '.join(tour.included[:3])}")

    # 2. Проверка доступности
    print("\n" + "=" * 50)
    print("Проверка доступности")
    print("=" * 50)

    tour_id = tours[0].id
    availability = client.check_availability(
        tour_id=tour_id,
        date="2026-03-15",
        travelers=2
    )

    print(f"\nТур: {tour_id}")
    print(f"Дата: {availability.date}")
    print(f"Доступно: {'Да' if availability.available else 'Нет'}")
    print(f"Мест: {availability.slots}")
    print(f"Цена за 2 чел: {availability.price} AED")

    # 3. Создание бронирования
    if availability.available:
        print("\n" + "=" * 50)
        print("Создание бронирования")
        print("=" * 50)

        booking = client.create_booking(
            tour_id=tour_id,
            date="2026-03-15",
            adults=2,
            children=0,
            customer_name="Иван Иванов",
            customer_email="ivan@example.com",
            customer_phone="+971501234567"
        )

        print(f"\n✅ Бронирование создано!")
        print(f"   Номер: {booking.id}")
        print(f"   Статус: {booking.status}")
        print(f"   Сумма: {booking.total_price} AED")
        if booking.voucher_url:
            print(f"   Ваучер: {booking.voucher_url}")

if __name__ == "__main__":
    main()
