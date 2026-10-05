"""
REST API Endpoint Template (FastAPI)
Шаблон для создания REST API endpoints

Использование:
    uvicorn rest_endpoint:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import os

app = FastAPI(
    title="Tourism API",
    description="API для туристического бизнеса ОАЭ",
    version="1.0.0"
)

# ============= Models =============

class Customer(BaseModel):
    name: str = Field(..., example="Иван Иванов")
    email: str = Field(..., example="ivan@example.com")
    phone: str = Field(..., example="+971501234567")

class BookingCreate(BaseModel):
    tour_id: str = Field(..., example="dubai-safari-001")
    date: date = Field(..., example="2026-03-15")
    adults: int = Field(..., ge=1, le=20, example=2)
    children: int = Field(default=0, ge=0, le=10, example=1)
    customer: Customer

class BookingResponse(BaseModel):
    id: str
    tour_id: str
    date: date
    adults: int
    children: int
    status: str
    total_price: float
    currency: str = "AED"

class Tour(BaseModel):
    id: str
    name: str
    description: str
    price: float
    currency: str = "AED"
    duration_hours: float
    available: bool

# ============= Fake Database =============

fake_tours = {
    "dubai-safari-001": Tour(
        id="dubai-safari-001",
        name="Дубай Сафари",
        description="Захватывающее приключение в пустыне",
        price=150.0,
        duration_hours=6,
        available=True
    ),
    "abu-dhabi-tour-001": Tour(
        id="abu-dhabi-tour-001",
        name="Абу-Даби Тур",
        description="Однодневная экскурсия в Абу-Даби",
        price=200.0,
        duration_hours=10,
        available=True
    )
}

fake_bookings = {}
booking_counter = 0

# ============= API Key Auth =============

def verify_api_key(api_key: str = Query(..., alias="api_key")):
    """Простая проверка API ключа через query parameter"""
    valid_key = os.getenv("API_KEY", "demo_key_12345")
    if api_key != valid_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# ============= Endpoints =============

@app.get("/tours", response_model=List[Tour], tags=["Tours"])
async def list_tours(
    city: Optional[str] = Query(None, example="dubai"),
    available_only: bool = Query(True)
):
    """Получить список туров"""
    tours = list(fake_tours.values())
    if available_only:
        tours = [t for t in tours if t.available]
    return tours

@app.get("/tours/{tour_id}", response_model=Tour, tags=["Tours"])
async def get_tour(tour_id: str):
    """Получить информацию о туре"""
    if tour_id not in fake_tours:
        raise HTTPException(status_code=404, detail="Tour not found")
    return fake_tours[tour_id]

@app.post("/bookings", response_model=BookingResponse, status_code=201, tags=["Bookings"])
async def create_booking(
    booking: BookingCreate,
    api_key: str = Depends(verify_api_key)
):
    """Создать новое бронирование"""
    global booking_counter

    # Проверить что тур существует
    if booking.tour_id not in fake_tours:
        raise HTTPException(status_code=400, detail="Tour not found")

    tour = fake_tours[booking.tour_id]

    # Создать бронирование
    booking_counter += 1
    booking_id = f"BK-{booking_counter:06d}"

    total_price = tour.price * booking.adults + (tour.price * 0.5) * booking.children

    booking_response = BookingResponse(
        id=booking_id,
        tour_id=booking.tour_id,
        date=booking.date,
        adults=booking.adults,
        children=booking.children,
        status="confirmed",
        total_price=total_price
    )

    fake_bookings[booking_id] = booking_response
    return booking_response

@app.get("/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
async def get_booking(
    booking_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Получить информацию о бронировании"""
    if booking_id not in fake_bookings:
        raise HTTPException(status_code=404, detail="Booking not found")
    return fake_bookings[booking_id]

@app.patch("/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
async def update_booking(
    booking_id: str,
    new_date: Optional[date] = None,
    api_key: str = Depends(verify_api_key)
):
    """Обновить бронирование"""
    if booking_id not in fake_bookings:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking = fake_bookings[booking_id]
    if new_date:
        booking.date = new_date

    return booking

@app.delete("/bookings/{booking_id}", status_code=204, tags=["Bookings"])
async def cancel_booking(
    booking_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Отменить бронирование"""
    if booking_id not in fake_bookings:
        raise HTTPException(status_code=404, detail="Booking not found")

    fake_bookings[booking_id].status = "cancelled"
    return None

# ============= Health Check =============

@app.get("/health", tags=["System"])
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
