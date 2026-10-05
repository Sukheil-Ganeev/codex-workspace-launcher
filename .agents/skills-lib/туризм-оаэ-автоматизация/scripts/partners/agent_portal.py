#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Веб-портал для туристических агентов.

Функционал:
- Авторизация с JWT tokens и уровнями доступа
- Каталог туров с ценами для агентов
- Система бронирования
- Личный кабинет агента
- Отчёты и аналитика
- Admin панель

Использование:
    python agent_portal.py [--host HOST] [--port PORT] [--reload]

Запуск: uvicorn agent_portal:app --reload
"""

import os
import sys
import json
import hashlib
import secrets
from datetime import datetime, timedelta, date
from decimal import Decimal
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import logging

# FastAPI и зависимости
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Query, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# JWT
from jose import JWTError, jwt
from passlib.context import CryptContext

# SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Date, Enum as SQLEnum, Numeric, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Pydantic
from pydantic import BaseModel, EmailStr, Field, validator

# ═══════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

# Директории
SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR / "templates" / "portal"
STATIC_DIR = SCRIPT_DIR / "static"
DATABASE_DIR = SCRIPT_DIR / "data"

# Создаём директории
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# JWT настройки
SECRET_KEY = os.getenv("PORTAL_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

# База данных
DATABASE_URL = os.getenv("PORTAL_DATABASE_URL", f"sqlite:///{DATABASE_DIR}/agent_portal.db")

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# БАЗА ДАННЫХ - МОДЕЛИ
# ═══════════════════════════════════════════════════════════════════════════════

Base = declarative_base()


class UserRole(str, Enum):
    AGENT = "agent"
    MANAGER = "manager"
    ADMIN = "admin"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CommissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"


class User(Base):
    """Пользователь (агент/менеджер/админ)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(50))
    company_name = Column(String(255))
    role = Column(String(20), default=UserRole.AGENT)
    commission_rate = Column(Float, default=10.0)  # Процент комиссии
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Связи
    bookings = relationship("Booking", back_populates="agent")
    commissions = relationship("Commission", back_populates="agent")


class TourCategory(Base):
    """Категория туров."""
    __tablename__ = "tour_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_ru = Column(String(100))
    description = Column(Text)
    icon = Column(String(50))  # FontAwesome icon
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    tours = relationship("Tour", back_populates="category")


class Tour(Base):
    """Тур/экскурсия."""
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("tour_categories.id"))
    code = Column(String(50), unique=True)  # Артикул
    name = Column(String(255), nullable=False)
    name_ru = Column(String(255))
    description = Column(Text)
    description_ru = Column(Text)

    # Цены
    price_adult = Column(Numeric(10, 2), nullable=False)  # Цена для взрослого
    price_child = Column(Numeric(10, 2))  # Цена для ребёнка
    price_infant = Column(Numeric(10, 2), default=0)  # Цена для младенца
    currency = Column(String(3), default="AED")

    # Агентская цена (нетто)
    agent_price_adult = Column(Numeric(10, 2))
    agent_price_child = Column(Numeric(10, 2))

    # Параметры
    duration_hours = Column(Float)  # Длительность в часах
    min_participants = Column(Integer, default=1)
    max_participants = Column(Integer, default=20)
    pickup_included = Column(Boolean, default=True)
    meals_included = Column(String(100))  # "breakfast,lunch"

    # Медиа
    image_url = Column(String(500))
    gallery = Column(Text)  # JSON array of URLs

    # Доступность
    available_days = Column(String(50), default="1,2,3,4,5,6,7")  # Дни недели
    start_times = Column(String(200), default="09:00")  # Возможные времена
    advance_booking_hours = Column(Integer, default=24)  # За сколько часов до

    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    category = relationship("TourCategory", back_populates="tours")
    bookings = relationship("Booking", back_populates="tour")
    availability = relationship("TourAvailability", back_populates="tour")


class TourAvailability(Base):
    """Доступность тура на конкретную дату."""
    __tablename__ = "tour_availability"

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"))
    date = Column(Date, nullable=False)
    time_slot = Column(String(10))  # "09:00"
    total_slots = Column(Integer, default=20)
    booked_slots = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    special_price_adult = Column(Numeric(10, 2))  # Спеццена на дату
    special_price_child = Column(Numeric(10, 2))

    tour = relationship("Tour", back_populates="availability")


class Booking(Base):
    """Бронирование."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_number = Column(String(20), unique=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id"))
    tour_id = Column(Integer, ForeignKey("tours.id"))

    # Дата и время
    tour_date = Column(Date, nullable=False)
    tour_time = Column(String(10))

    # Участники
    adults = Column(Integer, default=1)
    children = Column(Integer, default=0)
    infants = Column(Integer, default=0)

    # Данные клиента
    client_name = Column(String(255), nullable=False)
    client_phone = Column(String(50))
    client_email = Column(String(255))
    hotel_name = Column(String(255))
    room_number = Column(String(20))
    pickup_location = Column(Text)
    special_requests = Column(Text)

    # Цены
    total_price = Column(Numeric(10, 2))  # Общая цена (брутто)
    agent_price = Column(Numeric(10, 2))  # Агентская цена (нетто)
    commission_amount = Column(Numeric(10, 2))  # Комиссия агента
    currency = Column(String(3), default="AED")

    # Статус
    status = Column(String(20), default=BookingStatus.PENDING)
    payment_status = Column(String(20), default="unpaid")

    # Метаданные
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)

    agent = relationship("User", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")


class Commission(Base):
    """Комиссия агента."""
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id"))
    booking_id = Column(Integer, ForeignKey("bookings.id"))

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="AED")
    rate = Column(Float)  # Процент комиссии

    status = Column(String(20), default=CommissionStatus.PENDING)

    accrued_at = Column(DateTime, default=datetime.utcnow)  # Когда начислена
    approved_at = Column(DateTime)  # Когда подтверждена
    paid_at = Column(DateTime)  # Когда выплачена

    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    notes = Column(Text)

    agent = relationship("User", back_populates="commissions")
    booking = relationship("Booking")


class AuditLog(Base):
    """Лог действий."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC СХЕМЫ
# ═══════════════════════════════════════════════════════════════════════════════

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    company_name: Optional[str]
    role: str
    commission_rate: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TourResponse(BaseModel):
    id: int
    code: Optional[str]
    name: str
    name_ru: Optional[str]
    description: Optional[str]
    price_adult: float
    price_child: Optional[float]
    agent_price_adult: Optional[float]
    agent_price_child: Optional[float]
    currency: str
    duration_hours: Optional[float]
    image_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    tour_id: int
    tour_date: date
    tour_time: Optional[str] = "09:00"
    adults: int = Field(ge=1, default=1)
    children: int = Field(ge=0, default=0)
    infants: int = Field(ge=0, default=0)
    client_name: str
    client_phone: Optional[str]
    client_email: Optional[EmailStr]
    hotel_name: Optional[str]
    room_number: Optional[str]
    pickup_location: Optional[str]
    special_requests: Optional[str]


class BookingResponse(BaseModel):
    id: int
    booking_number: str
    tour_date: date
    tour_time: Optional[str]
    adults: int
    children: int
    infants: int
    client_name: str
    total_price: float
    agent_price: float
    commission_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# БЕЗОПАСНОСТЬ
# ═══════════════════════════════════════════════════════════════════════════════

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Захешировать пароль."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создать JWT токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    """Декодировать JWT токен."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return None
        return TokenData(username=username, role=role)
    except JWTError:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# БАЗА ДАННЫХ - ПОДКЛЮЧЕНИЕ
# ═══════════════════════════════════════════════════════════════════════════════

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Получить сессию БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализировать базу данных."""
    Base.metadata.create_all(bind=engine)

    # Создаём админа по умолчанию
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                email="admin@portal.local",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            logger.info("Created default admin user: admin / admin123")

        # Создаём категории туров
        if db.query(TourCategory).count() == 0:
            categories = [
                TourCategory(name="City Tours", name_ru="Обзорные экскурсии", icon="fa-city", sort_order=1),
                TourCategory(name="Desert Safari", name_ru="Сафари", icon="fa-sun", sort_order=2),
                TourCategory(name="Yacht & Boat", name_ru="Яхты и катера", icon="fa-ship", sort_order=3),
                TourCategory(name="Theme Parks", name_ru="Парки развлечений", icon="fa-ticket-alt", sort_order=4),
                TourCategory(name="Water Activities", name_ru="Водные активности", icon="fa-water", sort_order=5),
                TourCategory(name="Transfers", name_ru="Трансферы", icon="fa-car", sort_order=6),
            ]
            db.add_all(categories)
            db.commit()
            logger.info("Created default tour categories")

        # Создаём демо-туры
        if db.query(Tour).count() == 0:
            city_cat = db.query(TourCategory).filter(TourCategory.name == "City Tours").first()
            safari_cat = db.query(TourCategory).filter(TourCategory.name == "Desert Safari").first()
            yacht_cat = db.query(TourCategory).filter(TourCategory.name == "Yacht & Boat").first()

            tours = [
                Tour(
                    category_id=city_cat.id,
                    code="DBX-CITY-01",
                    name="Dubai City Tour",
                    name_ru="Обзорная экскурсия по Дубаю",
                    description="Discover Dubai's iconic landmarks",
                    description_ru="Откройте для себя знаковые достопримечательности Дубая",
                    price_adult=150,
                    price_child=100,
                    agent_price_adult=120,
                    agent_price_child=80,
                    duration_hours=6,
                    pickup_included=True,
                    meals_included="lunch",
                    is_featured=True
                ),
                Tour(
                    category_id=city_cat.id,
                    code="ABD-CITY-01",
                    name="Abu Dhabi City Tour",
                    name_ru="Обзорная экскурсия по Абу-Даби",
                    description="Full day tour of UAE capital",
                    description_ru="Полный день в столице ОАЭ",
                    price_adult=200,
                    price_child=150,
                    agent_price_adult=160,
                    agent_price_child=120,
                    duration_hours=10,
                    pickup_included=True,
                    meals_included="lunch",
                    is_featured=True
                ),
                Tour(
                    category_id=safari_cat.id,
                    code="SAF-EVE-01",
                    name="Evening Desert Safari",
                    name_ru="Вечернее сафари",
                    description="Dune bashing, BBQ dinner, entertainment",
                    description_ru="Катание по дюнам, ужин BBQ, развлечения",
                    price_adult=180,
                    price_child=130,
                    agent_price_adult=140,
                    agent_price_child=100,
                    duration_hours=6,
                    start_times="14:00,15:00",
                    pickup_included=True,
                    meals_included="dinner",
                    is_featured=True
                ),
                Tour(
                    category_id=safari_cat.id,
                    code="SAF-MOR-01",
                    name="Morning Desert Safari",
                    name_ru="Утреннее сафари",
                    description="Sunrise dune bashing, camel ride, sandboarding",
                    description_ru="Восход в пустыне, катание на верблюдах, сэндбординг",
                    price_adult=150,
                    price_child=100,
                    agent_price_adult=120,
                    agent_price_child=80,
                    duration_hours=4,
                    start_times="05:00,06:00",
                    pickup_included=True
                ),
                Tour(
                    category_id=yacht_cat.id,
                    code="YHT-PVT-01",
                    name="Private Yacht Cruise",
                    name_ru="Частная яхта",
                    description="3-hour private yacht experience",
                    description_ru="3-часовая аренда частной яхты",
                    price_adult=2500,
                    agent_price_adult=2000,
                    duration_hours=3,
                    min_participants=1,
                    max_participants=10,
                    pickup_included=False
                ),
            ]
            db.add_all(tours)
            db.commit()
            logger.info("Created demo tours")

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Agent Portal",
    description="Веб-портал для туристических агентов",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Шаблоны
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ═══════════════════════════════════════════════════════════════════════════════
# ЗАВИСИМОСТИ
# ═══════════════════════════════════════════════════════════════════════════════

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Получить текущего пользователя из токена или cookie."""
    # Пробуем из заголовка
    if not token:
        # Пробуем из cookie
        token = request.cookies.get("access_token")

    if not token:
        return None

    # Убираем "Bearer " если есть
    if token.startswith("Bearer "):
        token = token[7:]

    token_data = decode_token(token)
    if not token_data:
        return None

    user = db.query(User).filter(User.username == token_data.username).first()
    if not user or not user.is_active:
        return None

    return user


async def require_auth(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Требовать авторизацию."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_manager(user: User = Depends(require_auth)) -> User:
    """Требовать роль manager или выше."""
    if user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Manager access required")
    return user


async def require_admin(user: User = Depends(require_auth)) -> User:
    """Требовать роль admin."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ═══════════════════════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════════════════════

def generate_booking_number() -> str:
    """Генерировать уникальный номер бронирования."""
    timestamp = datetime.now().strftime("%y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"BK{timestamp}{random_part}"


def calculate_booking_prices(
    tour: Tour,
    adults: int,
    children: int,
    infants: int,
    agent_commission_rate: float
) -> Dict[str, float]:
    """Рассчитать цены бронирования."""
    # Брутто цена (для клиента)
    total_price = float(tour.price_adult or 0) * adults
    if tour.price_child:
        total_price += float(tour.price_child) * children
    if tour.price_infant:
        total_price += float(tour.price_infant) * infants

    # Нетто цена (агентская)
    agent_price = float(tour.agent_price_adult or tour.price_adult or 0) * adults
    if tour.agent_price_child or tour.price_child:
        agent_price += float(tour.agent_price_child or tour.price_child or 0) * children

    # Комиссия агента
    commission = total_price - agent_price

    return {
        "total_price": round(total_price, 2),
        "agent_price": round(agent_price, 2),
        "commission_amount": round(commission, 2)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# API ЭНДПОИНТЫ - АВТОРИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового агента."""
    # Проверяем уникальность
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        company_name=user_data.company_name,
        role=UserRole.AGENT,
        is_active=True  # Можно сделать False и требовать верификацию
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New agent registered: {user.username}")
    return user


@app.post("/api/auth/token", response_model=Token)
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Получить JWT токен."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    # Обновляем время последнего входа
    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/auth/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Вход в систему (для формы)."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(data={"sub": user.username, "role": user.role})

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@app.get("/api/auth/logout")
async def logout():
    """Выход из системы."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_auth)):
    """Получить данные текущего пользователя."""
    return user


# ═══════════════════════════════════════════════════════════════════════════════
# API ЭНДПОИНТЫ - КАТАЛОГ ТУРОВ
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/tours")
async def get_tours(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    """Получить список туров."""
    query = db.query(Tour).filter(Tour.is_active == True)

    if category_id:
        query = query.filter(Tour.category_id == category_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Tour.name.ilike(search_term)) |
            (Tour.name_ru.ilike(search_term)) |
            (Tour.code.ilike(search_term))
        )

    if featured_only:
        query = query.filter(Tour.is_featured == True)

    tours = query.all()

    result = []
    for tour in tours:
        tour_data = {
            "id": tour.id,
            "code": tour.code,
            "name": tour.name,
            "name_ru": tour.name_ru,
            "description": tour.description,
            "description_ru": tour.description_ru,
            "price_adult": float(tour.price_adult) if tour.price_adult else 0,
            "price_child": float(tour.price_child) if tour.price_child else None,
            "currency": tour.currency,
            "duration_hours": tour.duration_hours,
            "image_url": tour.image_url,
            "is_featured": tour.is_featured,
            "pickup_included": tour.pickup_included,
            "meals_included": tour.meals_included,
            "category_id": tour.category_id
        }

        # Показываем агентские цены только авторизованным
        if user:
            tour_data["agent_price_adult"] = float(tour.agent_price_adult) if tour.agent_price_adult else None
            tour_data["agent_price_child"] = float(tour.agent_price_child) if tour.agent_price_child else None
            tour_data["commission"] = tour_data["price_adult"] - (tour_data["agent_price_adult"] or tour_data["price_adult"])

        result.append(tour_data)

    return result


@app.get("/api/tours/{tour_id}")
async def get_tour(
    tour_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    """Получить информацию о туре."""
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    result = {
        "id": tour.id,
        "code": tour.code,
        "name": tour.name,
        "name_ru": tour.name_ru,
        "description": tour.description,
        "description_ru": tour.description_ru,
        "price_adult": float(tour.price_adult) if tour.price_adult else 0,
        "price_child": float(tour.price_child) if tour.price_child else None,
        "price_infant": float(tour.price_infant) if tour.price_infant else 0,
        "currency": tour.currency,
        "duration_hours": tour.duration_hours,
        "min_participants": tour.min_participants,
        "max_participants": tour.max_participants,
        "image_url": tour.image_url,
        "gallery": json.loads(tour.gallery) if tour.gallery else [],
        "available_days": tour.available_days,
        "start_times": tour.start_times.split(",") if tour.start_times else ["09:00"],
        "pickup_included": tour.pickup_included,
        "meals_included": tour.meals_included,
        "advance_booking_hours": tour.advance_booking_hours
    }

    if user:
        result["agent_price_adult"] = float(tour.agent_price_adult) if tour.agent_price_adult else None
        result["agent_price_child"] = float(tour.agent_price_child) if tour.agent_price_child else None

    return result


@app.get("/api/tours/{tour_id}/availability")
async def get_tour_availability(
    tour_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Получить доступность тура на даты."""
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # Получаем записи о доступности
    availability = db.query(TourAvailability).filter(
        TourAvailability.tour_id == tour_id,
        TourAvailability.date >= start_date,
        TourAvailability.date <= end_date
    ).all()

    avail_dict = {(a.date, a.time_slot): a for a in availability}

    # Генерируем список дат
    result = []
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.isoweekday()
        available_days = [int(d) for d in tour.available_days.split(",")]

        if day_of_week in available_days:
            for time_slot in (tour.start_times or "09:00").split(","):
                time_slot = time_slot.strip()
                avail = avail_dict.get((current_date, time_slot))

                if avail:
                    slots_available = avail.total_slots - avail.booked_slots
                    is_available = avail.is_available and slots_available > 0
                else:
                    slots_available = tour.max_participants
                    is_available = True

                result.append({
                    "date": current_date.isoformat(),
                    "time_slot": time_slot,
                    "is_available": is_available,
                    "slots_available": slots_available
                })

        current_date += timedelta(days=1)

    return result


@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Получить список категорий туров."""
    categories = db.query(TourCategory).filter(
        TourCategory.is_active == True
    ).order_by(TourCategory.sort_order).all()

    return [
        {
            "id": cat.id,
            "name": cat.name,
            "name_ru": cat.name_ru,
            "description": cat.description,
            "icon": cat.icon,
            "tour_count": len([t for t in cat.tours if t.is_active])
        }
        for cat in categories
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# API ЭНДПОИНТЫ - БРОНИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/bookings")
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Создать бронирование."""
    tour = db.query(Tour).filter(Tour.id == booking_data.tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    if not tour.is_active:
        raise HTTPException(status_code=400, detail="Tour is not available")

    # Проверяем дату
    min_date = datetime.now() + timedelta(hours=tour.advance_booking_hours)
    if datetime.combine(booking_data.tour_date, datetime.min.time()) < min_date:
        raise HTTPException(
            status_code=400,
            detail=f"Booking must be made at least {tour.advance_booking_hours} hours in advance"
        )

    # Рассчитываем цены
    prices = calculate_booking_prices(
        tour,
        booking_data.adults,
        booking_data.children,
        booking_data.infants,
        user.commission_rate
    )

    booking = Booking(
        booking_number=generate_booking_number(),
        agent_id=user.id,
        tour_id=tour.id,
        tour_date=booking_data.tour_date,
        tour_time=booking_data.tour_time,
        adults=booking_data.adults,
        children=booking_data.children,
        infants=booking_data.infants,
        client_name=booking_data.client_name,
        client_phone=booking_data.client_phone,
        client_email=booking_data.client_email,
        hotel_name=booking_data.hotel_name,
        room_number=booking_data.room_number,
        pickup_location=booking_data.pickup_location,
        special_requests=booking_data.special_requests,
        total_price=prices["total_price"],
        agent_price=prices["agent_price"],
        commission_amount=prices["commission_amount"],
        currency=tour.currency,
        status=BookingStatus.PENDING
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Создаём запись о комиссии
    commission = Commission(
        agent_id=user.id,
        booking_id=booking.id,
        amount=prices["commission_amount"],
        currency=tour.currency,
        rate=user.commission_rate,
        status=CommissionStatus.PENDING
    )
    db.add(commission)
    db.commit()

    logger.info(f"New booking created: {booking.booking_number} by agent {user.username}")

    return {
        "id": booking.id,
        "booking_number": booking.booking_number,
        "tour_name": tour.name,
        "tour_date": booking.tour_date.isoformat(),
        "tour_time": booking.tour_time,
        "total_price": float(booking.total_price),
        "agent_price": float(booking.agent_price),
        "commission_amount": float(booking.commission_amount),
        "status": booking.status
    }


@app.get("/api/bookings")
async def get_bookings(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Получить список бронирований."""
    query = db.query(Booking)

    # Агенты видят только свои бронирования
    if user.role == UserRole.AGENT:
        query = query.filter(Booking.agent_id == user.id)

    if status:
        query = query.filter(Booking.status == status)

    if start_date:
        query = query.filter(Booking.tour_date >= start_date)

    if end_date:
        query = query.filter(Booking.tour_date <= end_date)

    total = query.count()
    bookings = query.order_by(Booking.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": b.id,
                "booking_number": b.booking_number,
                "tour_name": b.tour.name if b.tour else None,
                "tour_date": b.tour_date.isoformat(),
                "tour_time": b.tour_time,
                "client_name": b.client_name,
                "adults": b.adults,
                "children": b.children,
                "total_price": float(b.total_price) if b.total_price else 0,
                "commission_amount": float(b.commission_amount) if b.commission_amount else 0,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None
            }
            for b in bookings
        ]
    }


@app.get("/api/bookings/{booking_id}")
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Получить детали бронирования."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Проверяем доступ
    if user.role == UserRole.AGENT and booking.agent_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": booking.id,
        "booking_number": booking.booking_number,
        "tour": {
            "id": booking.tour.id,
            "name": booking.tour.name,
            "name_ru": booking.tour.name_ru
        } if booking.tour else None,
        "tour_date": booking.tour_date.isoformat(),
        "tour_time": booking.tour_time,
        "adults": booking.adults,
        "children": booking.children,
        "infants": booking.infants,
        "client_name": booking.client_name,
        "client_phone": booking.client_phone,
        "client_email": booking.client_email,
        "hotel_name": booking.hotel_name,
        "room_number": booking.room_number,
        "pickup_location": booking.pickup_location,
        "special_requests": booking.special_requests,
        "total_price": float(booking.total_price) if booking.total_price else 0,
        "agent_price": float(booking.agent_price) if booking.agent_price else 0,
        "commission_amount": float(booking.commission_amount) if booking.commission_amount else 0,
        "currency": booking.currency,
        "status": booking.status,
        "payment_status": booking.payment_status,
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "confirmed_at": booking.confirmed_at.isoformat() if booking.confirmed_at else None
    }


@app.put("/api/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    reason: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Отменить бронирование."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role == UserRole.AGENT and booking.agent_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Cannot cancel this booking")

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = reason

    # Отменяем комиссию
    commission = db.query(Commission).filter(Commission.booking_id == booking_id).first()
    if commission:
        commission.status = CommissionStatus.PENDING
        commission.notes = "Cancelled"

    db.commit()

    return {"status": "cancelled", "booking_number": booking.booking_number}


# ═══════════════════════════════════════════════════════════════════════════════
# API ЭНДПОИНТЫ - КОМИССИИ
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/commissions")
async def get_commissions(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Получить комиссии агента."""
    query = db.query(Commission)

    if user.role == UserRole.AGENT:
        query = query.filter(Commission.agent_id == user.id)

    if status:
        query = query.filter(Commission.status == status)

    if start_date:
        query = query.filter(Commission.accrued_at >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(Commission.accrued_at <= datetime.combine(end_date, datetime.max.time()))

    commissions = query.order_by(Commission.accrued_at.desc()).all()

    # Считаем суммы
    total_pending = sum(float(c.amount) for c in commissions if c.status == CommissionStatus.PENDING)
    total_approved = sum(float(c.amount) for c in commissions if c.status == CommissionStatus.APPROVED)
    total_paid = sum(float(c.amount) for c in commissions if c.status == CommissionStatus.PAID)

    return {
        "summary": {
            "pending": round(total_pending, 2),
            "approved": round(total_approved, 2),
            "paid": round(total_paid, 2),
            "total": round(total_pending + total_approved + total_paid, 2)
        },
        "items": [
            {
                "id": c.id,
                "booking_number": c.booking.booking_number if c.booking else None,
                "amount": float(c.amount),
                "currency": c.currency,
                "status": c.status,
                "accrued_at": c.accrued_at.isoformat() if c.accrued_at else None,
                "paid_at": c.paid_at.isoformat() if c.paid_at else None
            }
            for c in commissions
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# API ЭНДПОИНТЫ - ОТЧЁТЫ
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/reports/sales")
async def get_sales_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Отчёт по продажам за период."""
    query = db.query(Booking).filter(
        Booking.tour_date >= start_date,
        Booking.tour_date <= end_date,
        Booking.status.notin_([BookingStatus.CANCELLED])
    )

    if user.role == UserRole.AGENT:
        query = query.filter(Booking.agent_id == user.id)

    bookings = query.all()

    # Группируем по турам
    tours_stats = {}
    for b in bookings:
        tour_name = b.tour.name if b.tour else "Unknown"
        if tour_name not in tours_stats:
            tours_stats[tour_name] = {
                "count": 0,
                "total_price": 0,
                "commission": 0,
                "participants": 0
            }
        tours_stats[tour_name]["count"] += 1
        tours_stats[tour_name]["total_price"] += float(b.total_price or 0)
        tours_stats[tour_name]["commission"] += float(b.commission_amount or 0)
        tours_stats[tour_name]["participants"] += b.adults + b.children

    # Сортируем по количеству
    top_tours = sorted(tours_stats.items(), key=lambda x: x[1]["count"], reverse=True)

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "total_bookings": len(bookings),
            "total_revenue": sum(float(b.total_price or 0) for b in bookings),
            "total_commission": sum(float(b.commission_amount or 0) for b in bookings),
            "total_participants": sum(b.adults + b.children for b in bookings)
        },
        "top_tours": [
            {"tour": name, **stats}
            for name, stats in top_tours[:10]
        ]
    }


@app.get("/api/reports/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Статистика для дашборда."""
    today = date.today()
    month_start = today.replace(day=1)

    # Базовый запрос
    base_query = db.query(Booking)
    if user.role == UserRole.AGENT:
        base_query = base_query.filter(Booking.agent_id == user.id)

    # Статистика за месяц
    month_bookings = base_query.filter(
        Booking.created_at >= datetime.combine(month_start, datetime.min.time()),
        Booking.status != BookingStatus.CANCELLED
    ).all()

    # Предстоящие экскурсии
    upcoming = base_query.filter(
        Booking.tour_date >= today,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.PAID])
    ).order_by(Booking.tour_date).limit(5).all()

    # Комиссия к выплате
    pending_commission = db.query(Commission).filter(
        Commission.status.in_([CommissionStatus.PENDING, CommissionStatus.APPROVED])
    )
    if user.role == UserRole.AGENT:
        pending_commission = pending_commission.filter(Commission.agent_id == user.id)

    pending_sum = sum(float(c.amount) for c in pending_commission.all())

    return {
        "month_stats": {
            "bookings": len(month_bookings),
            "revenue": sum(float(b.total_price or 0) for b in month_bookings),
            "commission": sum(float(b.commission_amount or 0) for b in month_bookings)
        },
        "pending_commission": pending_sum,
        "upcoming_tours": [
            {
                "booking_number": b.booking_number,
                "tour_name": b.tour.name if b.tour else None,
                "tour_date": b.tour_date.isoformat(),
                "client_name": b.client_name,
                "status": b.status
            }
            for b in upcoming
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# API ЭНДПОИНТЫ - ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/admin/agents")
async def get_agents(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Получить список агентов (только для админа)."""
    query = db.query(User).filter(User.role == UserRole.AGENT)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    agents = query.all()

    result = []
    for agent in agents:
        # Считаем статистику
        bookings = db.query(Booking).filter(Booking.agent_id == agent.id).all()
        commissions = db.query(Commission).filter(Commission.agent_id == agent.id).all()

        result.append({
            "id": agent.id,
            "username": agent.username,
            "email": agent.email,
            "full_name": agent.full_name,
            "company_name": agent.company_name,
            "phone": agent.phone,
            "commission_rate": agent.commission_rate,
            "is_active": agent.is_active,
            "is_verified": agent.is_verified,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "last_login": agent.last_login.isoformat() if agent.last_login else None,
            "stats": {
                "total_bookings": len(bookings),
                "total_revenue": sum(float(b.total_price or 0) for b in bookings if b.status != BookingStatus.CANCELLED),
                "total_commission_earned": sum(float(c.amount) for c in commissions),
                "commission_paid": sum(float(c.amount) for c in commissions if c.status == CommissionStatus.PAID)
            }
        })

    return result


@app.put("/api/admin/agents/{agent_id}")
async def update_agent(
    agent_id: int,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    commission_rate: Optional[float] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Обновить данные агента."""
    agent = db.query(User).filter(User.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if is_active is not None:
        agent.is_active = is_active
    if is_verified is not None:
        agent.is_verified = is_verified
    if commission_rate is not None:
        agent.commission_rate = commission_rate
    if role is not None and role in [r.value for r in UserRole]:
        agent.role = role

    db.commit()

    logger.info(f"Admin {user.username} updated agent {agent.username}")

    return {"status": "updated", "agent_id": agent_id}


@app.put("/api/admin/commissions/{commission_id}/approve")
async def approve_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager)
):
    """Подтвердить комиссию."""
    commission = db.query(Commission).filter(Commission.id == commission_id).first()
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    commission.status = CommissionStatus.APPROVED
    commission.approved_at = datetime.utcnow()
    db.commit()

    return {"status": "approved"}


@app.put("/api/admin/commissions/{commission_id}/pay")
async def pay_commission(
    commission_id: int,
    payment_method: str = Form(...),
    payment_reference: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Отметить комиссию как выплаченную."""
    commission = db.query(Commission).filter(Commission.id == commission_id).first()
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    commission.status = CommissionStatus.PAID
    commission.paid_at = datetime.utcnow()
    commission.payment_method = payment_method
    commission.payment_reference = payment_reference
    db.commit()

    return {"status": "paid"}


@app.post("/api/admin/tours")
async def create_tour(
    name: str = Form(...),
    name_ru: str = Form(None),
    category_id: int = Form(...),
    price_adult: float = Form(...),
    price_child: float = Form(None),
    agent_price_adult: float = Form(None),
    agent_price_child: float = Form(None),
    description: str = Form(None),
    duration_hours: float = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Создать новый тур."""
    code = f"TOUR-{secrets.token_hex(3).upper()}"

    tour = Tour(
        code=code,
        name=name,
        name_ru=name_ru,
        category_id=category_id,
        price_adult=price_adult,
        price_child=price_child,
        agent_price_adult=agent_price_adult or price_adult * 0.8,
        agent_price_child=agent_price_child or (price_child * 0.8 if price_child else None),
        description=description,
        duration_hours=duration_hours,
        is_active=True
    )

    db.add(tour)
    db.commit()
    db.refresh(tour)

    return {"id": tour.id, "code": tour.code}


# ═══════════════════════════════════════════════════════════════════════════════
# HTML СТРАНИЦЫ
# ═══════════════════════════════════════════════════════════════════════════════

def render_template(request: Request, template_name: str, context: dict = None):
    """Рендерить шаблон с базовым контекстом."""
    ctx = {
        "request": request,
        "year": datetime.now().year
    }
    if context:
        ctx.update(context)
    return templates.TemplateResponse(template_name, ctx)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Optional[User] = Depends(get_current_user)):
    """Главная страница."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: Optional[User] = Depends(get_current_user)):
    """Страница входа."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return render_template(request, "login.html")


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации."""
    return render_template(request, "register.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    """Личный кабинет."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return render_template(request, "dashboard.html", {"user": user})


@app.get("/tours", response_class=HTMLResponse)
async def tours_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """Каталог туров."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return render_template(request, "tours.html", {"user": user})


@app.get("/bookings", response_class=HTMLResponse)
async def bookings_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """Мои бронирования."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return render_template(request, "bookings.html", {"user": user})


@app.get("/commissions", response_class=HTMLResponse)
async def commissions_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """Комиссии."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return render_template(request, "commissions.html", {"user": user})


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """Отчёты."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return render_template(request, "reports.html", {"user": user})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """Профиль."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return render_template(request, "profile.html", {"user": user})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """Admin панель."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return render_template(request, "admin.html", {"user": user})


# ═══════════════════════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске."""
    init_db()
    create_default_templates()
    logger.info("Agent Portal started")


def create_default_templates():
    """Создать шаблоны по умолчанию."""

    # Базовый шаблон
    base_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Agent Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #0d6efd;
            --secondary-color: #6c757d;
            --success-color: #198754;
            --sidebar-width: 250px;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: var(--sidebar-width);
            background: linear-gradient(135deg, #1a1c2e 0%, #2d3154 100%);
            padding-top: 20px;
            z-index: 1000;
        }
        .sidebar .logo {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .sidebar .logo h4 {
            color: white;
            margin: 0;
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,0.7);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            transition: all 0.3s;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            color: white;
            background: rgba(255,255,255,0.1);
        }
        .sidebar .nav-link i {
            width: 30px;
            margin-right: 10px;
        }
        .main-content {
            margin-left: var(--sidebar-width);
            padding: 20px;
            min-height: 100vh;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card-header {
            background: white;
            border-bottom: 1px solid #eee;
            font-weight: 600;
        }
        .stat-card {
            background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
            color: white;
        }
        .stat-card.success {
            background: linear-gradient(135deg, var(--success-color) 0%, #146c43 100%);
        }
        .stat-card.warning {
            background: linear-gradient(135deg, #ffc107 0%, #cc9a00 100%);
        }
        .stat-card .stat-value {
            font-size: 2rem;
            font-weight: bold;
        }
        .stat-card .stat-label {
            opacity: 0.8;
        }
        .top-bar {
            background: white;
            padding: 15px 20px;
            margin: -20px -20px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .btn-primary {
            background: var(--primary-color);
            border: none;
        }
        .badge-status {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .badge-pending { background: #ffc107; color: #000; }
        .badge-confirmed { background: #17a2b8; color: #fff; }
        .badge-paid { background: #28a745; color: #fff; }
        .badge-cancelled { background: #dc3545; color: #fff; }
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
            }
            .main-content {
                margin-left: 0;
            }
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if user %}
    <div class="sidebar">
        <div class="logo">
            <h4><i class="fas fa-plane"></i> Agent Portal</h4>
        </div>
        <nav class="nav flex-column">
            <a class="nav-link" href="/dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
            <a class="nav-link" href="/tours"><i class="fas fa-map-marked-alt"></i> Catalog</a>
            <a class="nav-link" href="/bookings"><i class="fas fa-calendar-check"></i> Bookings</a>
            <a class="nav-link" href="/commissions"><i class="fas fa-coins"></i> Commissions</a>
            <a class="nav-link" href="/reports"><i class="fas fa-chart-bar"></i> Reports</a>
            <a class="nav-link" href="/profile"><i class="fas fa-user"></i> Profile</a>
            {% if user.role == 'admin' %}
            <hr style="border-color: rgba(255,255,255,0.2); margin: 10px 20px;">
            <a class="nav-link" href="/admin"><i class="fas fa-cogs"></i> Admin</a>
            {% endif %}
            <hr style="border-color: rgba(255,255,255,0.2); margin: 10px 20px;">
            <a class="nav-link" href="/api/auth/logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
        </nav>
    </div>
    {% endif %}

    <div class="main-content">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script>
        // Axios настройки
        axios.defaults.headers.common['Content-Type'] = 'application/json';

        // Форматирование денег
        function formatMoney(amount, currency = 'AED') {
            return new Intl.NumberFormat('en-AE', {
                style: 'currency',
                currency: currency
            }).format(amount);
        }

        // Форматирование даты
        function formatDate(dateStr) {
            return new Date(dateStr).toLocaleDateString('ru-RU');
        }
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>'''

    # Страница входа
    login_html = '''{% extends "base.html" %}
{% block title %}Login - Agent Portal{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-5">
            <div class="card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-plane fa-3x text-primary mb-3"></i>
                        <h3>Agent Portal</h3>
                        <p class="text-muted">Sign in to your account</p>
                    </div>

                    <form action="/api/auth/login" method="POST">
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" name="username" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>

                    <div class="text-center mt-3">
                        <a href="/register">Create new account</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Страница регистрации
    register_html = '''{% extends "base.html" %}
{% block title %}Register - Agent Portal{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <h3>Agent Registration</h3>
                        <p class="text-muted">Create your agent account</p>
                    </div>

                    <form id="registerForm">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Username *</label>
                                <input type="text" name="username" class="form-control" required minlength="3">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Email *</label>
                                <input type="email" name="email" class="form-control" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Full Name *</label>
                            <input type="text" name="full_name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Company Name</label>
                            <input type="text" name="company_name" class="form-control">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Phone</label>
                            <input type="tel" name="phone" class="form-control">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password *</label>
                            <input type="password" name="password" class="form-control" required minlength="6">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Confirm Password *</label>
                            <input type="password" name="password2" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Register</button>
                    </form>

                    <div class="text-center mt-3">
                        Already have an account? <a href="/login">Login</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
        username: form.username.value,
        email: form.email.value,
        password: form.password.value,
        full_name: form.full_name.value,
        company_name: form.company_name.value || null,
        phone: form.phone.value || null
    };

    if (form.password.value !== form.password2.value) {
        alert('Passwords do not match');
        return;
    }

    try {
        await axios.post('/api/auth/register', data);
        alert('Registration successful! Please login.');
        window.location.href = '/login';
    } catch (err) {
        alert(err.response?.data?.detail || 'Registration failed');
    }
});
</script>
{% endblock %}'''

    # Dashboard
    dashboard_html = '''{% extends "base.html" %}
{% block title %}Dashboard - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">Dashboard</h4>
    <div>
        <span class="text-muted">Welcome, {{ user.full_name or user.username }}</span>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-4 mb-3">
        <div class="card stat-card">
            <div class="card-body">
                <div class="stat-value" id="monthBookings">-</div>
                <div class="stat-label">Bookings this month</div>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card stat-card success">
            <div class="card-body">
                <div class="stat-value" id="monthRevenue">-</div>
                <div class="stat-label">Revenue this month</div>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card stat-card warning">
            <div class="card-body">
                <div class="stat-value" id="pendingCommission">-</div>
                <div class="stat-label">Pending commission</div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8 mb-4">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="fas fa-calendar-alt me-2"></i>Upcoming Tours</span>
                <a href="/bookings" class="btn btn-sm btn-outline-primary">View All</a>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover" id="upcomingTable">
                        <thead>
                            <tr>
                                <th>Booking #</th>
                                <th>Tour</th>
                                <th>Date</th>
                                <th>Client</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div class="col-md-4 mb-4">
        <div class="card">
            <div class="card-header">
                <i class="fas fa-bolt me-2"></i>Quick Actions
            </div>
            <div class="card-body">
                <a href="/tours" class="btn btn-primary w-100 mb-2">
                    <i class="fas fa-plus me-2"></i>New Booking
                </a>
                <a href="/commissions" class="btn btn-outline-primary w-100 mb-2">
                    <i class="fas fa-coins me-2"></i>View Commissions
                </a>
                <a href="/reports" class="btn btn-outline-primary w-100">
                    <i class="fas fa-chart-bar me-2"></i>Reports
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
async function loadDashboard() {
    try {
        const res = await axios.get('/api/reports/dashboard');
        const data = res.data;

        document.getElementById('monthBookings').textContent = data.month_stats.bookings;
        document.getElementById('monthRevenue').textContent = formatMoney(data.month_stats.revenue);
        document.getElementById('pendingCommission').textContent = formatMoney(data.pending_commission);

        const tbody = document.querySelector('#upcomingTable tbody');
        tbody.innerHTML = data.upcoming_tours.map(tour => `
            <tr>
                <td><a href="/bookings?id=${tour.booking_number}">${tour.booking_number}</a></td>
                <td>${tour.tour_name || '-'}</td>
                <td>${formatDate(tour.tour_date)}</td>
                <td>${tour.client_name}</td>
                <td><span class="badge badge-status badge-${tour.status}">${tour.status}</span></td>
            </tr>
        `).join('') || '<tr><td colspan="5" class="text-center">No upcoming tours</td></tr>';

    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}

loadDashboard();
</script>
{% endblock %}'''

    # Каталог туров
    tours_html = '''{% extends "base.html" %}
{% block title %}Tour Catalog - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">Tour Catalog</h4>
    <div>
        <input type="text" id="searchInput" class="form-control form-control-sm" placeholder="Search tours..." style="width: 250px;">
    </div>
</div>

<div class="row mb-4">
    <div class="col-12">
        <div class="btn-group" role="group" id="categoryFilter">
            <button type="button" class="btn btn-outline-primary active" data-category="">All</button>
        </div>
    </div>
</div>

<div class="row" id="toursGrid"></div>

<!-- Booking Modal -->
<div class="modal fade" id="bookingModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">New Booking</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="bookingForm">
                    <input type="hidden" name="tour_id" id="bookingTourId">

                    <div class="mb-3">
                        <h6 id="bookingTourName"></h6>
                        <small class="text-muted" id="bookingTourPrice"></small>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Date *</label>
                            <input type="date" name="tour_date" class="form-control" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Time</label>
                            <select name="tour_time" class="form-select" id="bookingTimeSelect">
                                <option value="09:00">09:00</option>
                            </select>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Adults *</label>
                            <input type="number" name="adults" class="form-control" value="1" min="1" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Children (3-12)</label>
                            <input type="number" name="children" class="form-control" value="0" min="0">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Infants (0-2)</label>
                            <input type="number" name="infants" class="form-control" value="0" min="0">
                        </div>
                    </div>

                    <hr>
                    <h6>Client Information</h6>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Client Name *</label>
                            <input type="text" name="client_name" class="form-control" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Phone</label>
                            <input type="tel" name="client_phone" class="form-control">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="client_email" class="form-control">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Hotel</label>
                            <input type="text" name="hotel_name" class="form-control">
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Special Requests</label>
                        <textarea name="special_requests" class="form-control" rows="2"></textarea>
                    </div>

                    <div class="alert alert-info" id="bookingPriceCalc">
                        <strong>Estimated Total:</strong> <span id="calcTotal">-</span><br>
                        <strong>Your Commission:</strong> <span id="calcCommission">-</span>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="submitBooking()">Create Booking</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let tours = [];
let categories = [];
let selectedTour = null;

async function loadCategories() {
    const res = await axios.get('/api/categories');
    categories = res.data;

    const filterDiv = document.getElementById('categoryFilter');
    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-primary';
        btn.dataset.category = cat.id;
        btn.textContent = `${cat.name_ru || cat.name} (${cat.tour_count})`;
        btn.onclick = () => filterByCategory(cat.id);
        filterDiv.appendChild(btn);
    });
}

async function loadTours(categoryId = null, search = null) {
    let url = '/api/tours?';
    if (categoryId) url += `category_id=${categoryId}&`;
    if (search) url += `search=${encodeURIComponent(search)}`;

    const res = await axios.get(url);
    tours = res.data;
    renderTours();
}

function renderTours() {
    const grid = document.getElementById('toursGrid');
    grid.innerHTML = tours.map(tour => `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-img-top bg-secondary" style="height: 150px; display: flex; align-items: center; justify-content: center;">
                    ${tour.image_url
                        ? `<img src="${tour.image_url}" alt="${tour.name}" style="width: 100%; height: 100%; object-fit: cover;">`
                        : `<i class="fas fa-image fa-3x text-white"></i>`
                    }
                </div>
                <div class="card-body">
                    <h5 class="card-title">${tour.name_ru || tour.name}</h5>
                    <p class="card-text text-muted small">${tour.description_ru || tour.description || ''}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="text-muted small">Retail: ${formatMoney(tour.price_adult)}</div>
                            ${tour.agent_price_adult ? `<div class="text-success"><strong>Agent: ${formatMoney(tour.agent_price_adult)}</strong></div>` : ''}
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="openBooking(${tour.id})">Book</button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function filterByCategory(categoryId) {
    document.querySelectorAll('#categoryFilter button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category == (categoryId || ''));
    });
    loadTours(categoryId);
}

function openBooking(tourId) {
    selectedTour = tours.find(t => t.id === tourId);
    if (!selectedTour) return;

    document.getElementById('bookingTourId').value = tourId;
    document.getElementById('bookingTourName').textContent = selectedTour.name_ru || selectedTour.name;
    document.getElementById('bookingTourPrice').textContent = `Retail: ${formatMoney(selectedTour.price_adult)} | Agent: ${formatMoney(selectedTour.agent_price_adult || selectedTour.price_adult)}`;

    // Set min date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.querySelector('[name="tour_date"]').min = tomorrow.toISOString().split('T')[0];

    updatePriceCalc();

    new bootstrap.Modal(document.getElementById('bookingModal')).show();
}

function updatePriceCalc() {
    if (!selectedTour) return;

    const adults = parseInt(document.querySelector('[name="adults"]').value) || 0;
    const children = parseInt(document.querySelector('[name="children"]').value) || 0;

    const retailTotal = (selectedTour.price_adult * adults) + ((selectedTour.price_child || 0) * children);
    const agentTotal = ((selectedTour.agent_price_adult || selectedTour.price_adult) * adults) +
                       ((selectedTour.agent_price_child || selectedTour.price_child || 0) * children);
    const commission = retailTotal - agentTotal;

    document.getElementById('calcTotal').textContent = formatMoney(retailTotal);
    document.getElementById('calcCommission').textContent = formatMoney(commission);
}

async function submitBooking() {
    const form = document.getElementById('bookingForm');
    const data = {
        tour_id: parseInt(form.tour_id.value),
        tour_date: form.tour_date.value,
        tour_time: form.tour_time.value,
        adults: parseInt(form.adults.value),
        children: parseInt(form.children.value),
        infants: parseInt(form.infants.value),
        client_name: form.client_name.value,
        client_phone: form.client_phone.value || null,
        client_email: form.client_email.value || null,
        hotel_name: form.hotel_name.value || null,
        special_requests: form.special_requests.value || null
    };

    try {
        const res = await axios.post('/api/bookings', data);
        alert(`Booking created: ${res.data.booking_number}`);
        bootstrap.Modal.getInstance(document.getElementById('bookingModal')).hide();
        window.location.href = '/bookings';
    } catch (err) {
        alert(err.response?.data?.detail || 'Failed to create booking');
    }
}

// Event listeners
document.getElementById('searchInput').addEventListener('input', (e) => {
    loadTours(null, e.target.value);
});

document.querySelector('[name="adults"]').addEventListener('change', updatePriceCalc);
document.querySelector('[name="children"]').addEventListener('change', updatePriceCalc);

// Init
loadCategories();
loadTours();
</script>
{% endblock %}'''

    # Бронирования
    bookings_html = '''{% extends "base.html" %}
{% block title %}My Bookings - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">My Bookings</h4>
    <div>
        <select id="statusFilter" class="form-select form-select-sm" style="width: 150px;">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="paid">Paid</option>
            <option value="cancelled">Cancelled</option>
        </select>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover" id="bookingsTable">
                <thead>
                    <tr>
                        <th>Booking #</th>
                        <th>Tour</th>
                        <th>Date</th>
                        <th>Client</th>
                        <th>Pax</th>
                        <th>Total</th>
                        <th>Commission</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>

<!-- Booking Details Modal -->
<div class="modal fade" id="detailsModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Booking Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="detailsContent"></div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-danger" id="cancelBookingBtn" onclick="cancelBooking()">Cancel Booking</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
let currentBookingId = null;

async function loadBookings(status = null) {
    let url = '/api/bookings?limit=100';
    if (status) url += `&status=${status}`;

    const res = await axios.get(url);
    const tbody = document.querySelector('#bookingsTable tbody');

    tbody.innerHTML = res.data.items.map(b => `
        <tr>
            <td><a href="#" onclick="showDetails(${b.id})">${b.booking_number}</a></td>
            <td>${b.tour_name || '-'}</td>
            <td>${formatDate(b.tour_date)}</td>
            <td>${b.client_name}</td>
            <td>${b.adults}A ${b.children > 0 ? b.children + 'C' : ''}</td>
            <td>${formatMoney(b.total_price)}</td>
            <td class="text-success">${formatMoney(b.commission_amount)}</td>
            <td><span class="badge badge-status badge-${b.status}">${b.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showDetails(${b.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('') || '<tr><td colspan="9" class="text-center">No bookings found</td></tr>';
}

async function showDetails(bookingId) {
    currentBookingId = bookingId;
    const res = await axios.get(`/api/bookings/${bookingId}`);
    const b = res.data;

    document.getElementById('detailsContent').innerHTML = `
        <div class="mb-3">
            <strong>Booking Number:</strong> ${b.booking_number}<br>
            <strong>Status:</strong> <span class="badge badge-status badge-${b.status}">${b.status}</span>
        </div>
        <div class="mb-3">
            <strong>Tour:</strong> ${b.tour?.name_ru || b.tour?.name || '-'}<br>
            <strong>Date:</strong> ${formatDate(b.tour_date)} at ${b.tour_time || '-'}
        </div>
        <div class="mb-3">
            <strong>Participants:</strong> ${b.adults} Adults, ${b.children} Children, ${b.infants} Infants
        </div>
        <hr>
        <div class="mb-3">
            <strong>Client:</strong> ${b.client_name}<br>
            <strong>Phone:</strong> ${b.client_phone || '-'}<br>
            <strong>Email:</strong> ${b.client_email || '-'}<br>
            <strong>Hotel:</strong> ${b.hotel_name || '-'} ${b.room_number ? '/ Room ' + b.room_number : ''}
        </div>
        ${b.special_requests ? `<div class="mb-3"><strong>Special Requests:</strong><br>${b.special_requests}</div>` : ''}
        <hr>
        <div>
            <strong>Total Price:</strong> ${formatMoney(b.total_price)}<br>
            <strong>Agent Price:</strong> ${formatMoney(b.agent_price)}<br>
            <strong class="text-success">Your Commission:</strong> ${formatMoney(b.commission_amount)}
        </div>
    `;

    // Показываем/скрываем кнопку отмены
    const cancelBtn = document.getElementById('cancelBookingBtn');
    cancelBtn.style.display = ['pending', 'confirmed'].includes(b.status) ? 'block' : 'none';

    new bootstrap.Modal(document.getElementById('detailsModal')).show();
}

async function cancelBooking() {
    if (!currentBookingId) return;
    if (!confirm('Are you sure you want to cancel this booking?')) return;

    try {
        await axios.put(`/api/bookings/${currentBookingId}/cancel`, new URLSearchParams({reason: 'Cancelled by agent'}));
        alert('Booking cancelled');
        bootstrap.Modal.getInstance(document.getElementById('detailsModal')).hide();
        loadBookings(document.getElementById('statusFilter').value);
    } catch (err) {
        alert(err.response?.data?.detail || 'Failed to cancel');
    }
}

document.getElementById('statusFilter').addEventListener('change', (e) => {
    loadBookings(e.target.value);
});

loadBookings();
</script>
{% endblock %}'''

    # Комиссии
    commissions_html = '''{% extends "base.html" %}
{% block title %}Commissions - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">My Commissions</h4>
</div>

<div class="row mb-4">
    <div class="col-md-4 mb-3">
        <div class="card bg-warning text-dark">
            <div class="card-body text-center">
                <h3 id="pendingAmount">-</h3>
                <div>Pending</div>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card bg-info text-white">
            <div class="card-body text-center">
                <h3 id="approvedAmount">-</h3>
                <div>Approved</div>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card bg-success text-white">
            <div class="card-body text-center">
                <h3 id="paidAmount">-</h3>
                <div>Paid</div>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-header">Commission History</div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table" id="commissionsTable">
                <thead>
                    <tr>
                        <th>Booking #</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Accrued</th>
                        <th>Paid</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
async function loadCommissions() {
    const res = await axios.get('/api/commissions');
    const data = res.data;

    document.getElementById('pendingAmount').textContent = formatMoney(data.summary.pending);
    document.getElementById('approvedAmount').textContent = formatMoney(data.summary.approved);
    document.getElementById('paidAmount').textContent = formatMoney(data.summary.paid);

    const tbody = document.querySelector('#commissionsTable tbody');
    tbody.innerHTML = data.items.map(c => `
        <tr>
            <td>${c.booking_number || '-'}</td>
            <td>${formatMoney(c.amount)}</td>
            <td><span class="badge badge-status badge-${c.status === 'paid' ? 'paid' : c.status === 'approved' ? 'confirmed' : 'pending'}">${c.status}</span></td>
            <td>${c.accrued_at ? formatDate(c.accrued_at) : '-'}</td>
            <td>${c.paid_at ? formatDate(c.paid_at) : '-'}</td>
        </tr>
    `).join('') || '<tr><td colspan="5" class="text-center">No commissions yet</td></tr>';
}

loadCommissions();
</script>
{% endblock %}'''

    # Отчёты
    reports_html = '''{% extends "base.html" %}
{% block title %}Reports - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">Reports</h4>
    <div class="d-flex gap-2">
        <input type="date" id="startDate" class="form-control form-control-sm">
        <input type="date" id="endDate" class="form-control form-control-sm">
        <button class="btn btn-primary btn-sm" onclick="loadReport()">Generate</button>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h3 id="totalBookings">-</h3>
                <div class="text-muted">Total Bookings</div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h3 id="totalRevenue">-</h3>
                <div class="text-muted">Total Revenue</div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h3 id="totalCommission">-</h3>
                <div class="text-muted">Total Commission</div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h3 id="totalPax">-</h3>
                <div class="text-muted">Total Participants</div>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-header">Top Tours</div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table" id="topToursTable">
                <thead>
                    <tr>
                        <th>Tour</th>
                        <th>Bookings</th>
                        <th>Participants</th>
                        <th>Revenue</th>
                        <th>Commission</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Set default dates (last 30 days)
const today = new Date();
const monthAgo = new Date();
monthAgo.setDate(today.getDate() - 30);

document.getElementById('endDate').value = today.toISOString().split('T')[0];
document.getElementById('startDate').value = monthAgo.toISOString().split('T')[0];

async function loadReport() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!startDate || !endDate) {
        alert('Please select date range');
        return;
    }

    const res = await axios.get(`/api/reports/sales?start_date=${startDate}&end_date=${endDate}`);
    const data = res.data;

    document.getElementById('totalBookings').textContent = data.summary.total_bookings;
    document.getElementById('totalRevenue').textContent = formatMoney(data.summary.total_revenue);
    document.getElementById('totalCommission').textContent = formatMoney(data.summary.total_commission);
    document.getElementById('totalPax').textContent = data.summary.total_participants;

    const tbody = document.querySelector('#topToursTable tbody');
    tbody.innerHTML = data.top_tours.map(t => `
        <tr>
            <td>${t.tour}</td>
            <td>${t.count}</td>
            <td>${t.participants}</td>
            <td>${formatMoney(t.total_price)}</td>
            <td class="text-success">${formatMoney(t.commission)}</td>
        </tr>
    `).join('') || '<tr><td colspan="5" class="text-center">No data</td></tr>';
}

loadReport();
</script>
{% endblock %}'''

    # Профиль
    profile_html = '''{% extends "base.html" %}
{% block title %}Profile - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">My Profile</h4>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form id="profileForm">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" value="{{ user.username }}" disabled>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" value="{{ user.email }}" disabled>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Full Name</label>
                        <input type="text" name="full_name" class="form-control" value="{{ user.full_name or '' }}">
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Company</label>
                            <input type="text" name="company_name" class="form-control" value="{{ user.company_name or '' }}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Phone</label>
                            <input type="tel" name="phone" class="form-control" value="{{ user.phone or '' }}">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header">Account Info</div>
            <div class="card-body">
                <p><strong>Role:</strong> {{ user.role }}</p>
                <p><strong>Commission Rate:</strong> {{ user.commission_rate }}%</p>
                <p><strong>Status:</strong>
                    {% if user.is_active %}
                    <span class="badge bg-success">Active</span>
                    {% else %}
                    <span class="badge bg-danger">Inactive</span>
                    {% endif %}
                </p>
                <p><strong>Member Since:</strong> {{ user.created_at.strftime('%d.%m.%Y') if user.created_at else '-' }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Admin панель
    admin_html = '''{% extends "base.html" %}
{% block title %}Admin Panel - Agent Portal{% endblock %}

{% block content %}
<div class="top-bar">
    <h4 class="mb-0">Admin Panel</h4>
</div>

<ul class="nav nav-tabs mb-4" id="adminTabs">
    <li class="nav-item">
        <a class="nav-link active" data-bs-toggle="tab" href="#agents">Agents</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#commissions">Commissions</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#tours">Tours</a>
    </li>
</ul>

<div class="tab-content">
    <!-- Agents Tab -->
    <div class="tab-pane fade show active" id="agents">
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table" id="agentsTable">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Company</th>
                                <th>Email</th>
                                <th>Commission %</th>
                                <th>Bookings</th>
                                <th>Revenue</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Commissions Tab -->
    <div class="tab-pane fade" id="commissions">
        <div class="card">
            <div class="card-header">Pending Commissions for Approval</div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table" id="pendingCommissionsTable">
                        <thead>
                            <tr>
                                <th>Agent</th>
                                <th>Booking</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Tours Tab -->
    <div class="tab-pane fade" id="tours">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span>Tours Management</span>
                <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addTourModal">
                    <i class="fas fa-plus"></i> Add Tour
                </button>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table" id="toursAdminTable">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Name</th>
                                <th>Retail Price</th>
                                <th>Agent Price</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Edit Agent Modal -->
<div class="modal fade" id="editAgentModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Agent</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <input type="hidden" id="editAgentId">
                <div class="mb-3">
                    <label class="form-label">Commission Rate (%)</label>
                    <input type="number" id="editCommissionRate" class="form-control" step="0.1" min="0" max="50">
                </div>
                <div class="mb-3">
                    <label class="form-label">Status</label>
                    <select id="editAgentStatus" class="form-select">
                        <option value="true">Active</option>
                        <option value="false">Disabled</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Role</label>
                    <select id="editAgentRole" class="form-select">
                        <option value="agent">Agent</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="saveAgent()">Save</button>
            </div>
        </div>
    </div>
</div>

<!-- Add Tour Modal -->
<div class="modal fade" id="addTourModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New Tour</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addTourForm">
                    <div class="mb-3">
                        <label class="form-label">Name (EN)</label>
                        <input type="text" name="name" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Name (RU)</label>
                        <input type="text" name="name_ru" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Category</label>
                        <select name="category_id" class="form-select" id="tourCategorySelect" required></select>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Retail Price (Adult)</label>
                            <input type="number" name="price_adult" class="form-control" step="0.01" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Retail Price (Child)</label>
                            <input type="number" name="price_child" class="form-control" step="0.01">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Agent Price (Adult)</label>
                            <input type="number" name="agent_price_adult" class="form-control" step="0.01">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Agent Price (Child)</label>
                            <input type="number" name="agent_price_child" class="form-control" step="0.01">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Duration (hours)</label>
                        <input type="number" name="duration_hours" class="form-control" step="0.5">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea name="description" class="form-control" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="addTour()">Add Tour</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
async function loadAgents() {
    const res = await axios.get('/api/admin/agents');
    const tbody = document.querySelector('#agentsTable tbody');

    tbody.innerHTML = res.data.map(a => `
        <tr>
            <td>${a.username}</td>
            <td>${a.company_name || '-'}</td>
            <td>${a.email}</td>
            <td>${a.commission_rate}%</td>
            <td>${a.stats.total_bookings}</td>
            <td>${formatMoney(a.stats.total_revenue)}</td>
            <td>
                <span class="badge ${a.is_active ? 'bg-success' : 'bg-danger'}">
                    ${a.is_active ? 'Active' : 'Disabled'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editAgent(${a.id}, ${a.commission_rate}, ${a.is_active}, '${a.role}')">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function editAgent(id, rate, isActive, role) {
    document.getElementById('editAgentId').value = id;
    document.getElementById('editCommissionRate').value = rate;
    document.getElementById('editAgentStatus').value = isActive.toString();
    document.getElementById('editAgentRole').value = role;
    new bootstrap.Modal(document.getElementById('editAgentModal')).show();
}

async function saveAgent() {
    const id = document.getElementById('editAgentId').value;
    const params = new URLSearchParams({
        commission_rate: document.getElementById('editCommissionRate').value,
        is_active: document.getElementById('editAgentStatus').value,
        role: document.getElementById('editAgentRole').value
    });

    try {
        await axios.put(`/api/admin/agents/${id}?${params}`);
        bootstrap.Modal.getInstance(document.getElementById('editAgentModal')).hide();
        loadAgents();
    } catch (err) {
        alert(err.response?.data?.detail || 'Failed to save');
    }
}

async function loadPendingCommissions() {
    const res = await axios.get('/api/commissions?status=pending');
    const tbody = document.querySelector('#pendingCommissionsTable tbody');

    tbody.innerHTML = res.data.items.map(c => `
        <tr>
            <td>-</td>
            <td>${c.booking_number || '-'}</td>
            <td>${formatMoney(c.amount)}</td>
            <td><span class="badge badge-status badge-pending">${c.status}</span></td>
            <td>
                <button class="btn btn-sm btn-success" onclick="approveCommission(${c.id})">Approve</button>
            </td>
        </tr>
    `).join('') || '<tr><td colspan="5" class="text-center">No pending commissions</td></tr>';
}

async function approveCommission(id) {
    try {
        await axios.put(`/api/admin/commissions/${id}/approve`);
        loadPendingCommissions();
    } catch (err) {
        alert(err.response?.data?.detail || 'Failed');
    }
}

async function loadToursAdmin() {
    const res = await axios.get('/api/tours');
    const tbody = document.querySelector('#toursAdminTable tbody');

    tbody.innerHTML = res.data.map(t => `
        <tr>
            <td>${t.code || '-'}</td>
            <td>${t.name_ru || t.name}</td>
            <td>${formatMoney(t.price_adult)}</td>
            <td>${t.agent_price_adult ? formatMoney(t.agent_price_adult) : '-'}</td>
            <td><span class="badge ${t.is_active ? 'bg-success' : 'bg-secondary'}">${t.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
            </td>
        </tr>
    `).join('');
}

async function loadCategories() {
    const res = await axios.get('/api/categories');
    const select = document.getElementById('tourCategorySelect');
    select.innerHTML = res.data.map(c => `<option value="${c.id}">${c.name_ru || c.name}</option>`).join('');
}

async function addTour() {
    const form = document.getElementById('addTourForm');
    const formData = new FormData(form);

    try {
        await axios.post('/api/admin/tours', formData, {
            headers: {'Content-Type': 'multipart/form-data'}
        });
        bootstrap.Modal.getInstance(document.getElementById('addTourModal')).hide();
        loadToursAdmin();
        form.reset();
    } catch (err) {
        alert(err.response?.data?.detail || 'Failed to add tour');
    }
}

// Init
loadAgents();
loadPendingCommissions();
loadToursAdmin();
loadCategories();
</script>
{% endblock %}'''

    # Записываем шаблоны
    templates_to_create = {
        "base.html": base_html,
        "login.html": login_html,
        "register.html": register_html,
        "dashboard.html": dashboard_html,
        "tours.html": tours_html,
        "bookings.html": bookings_html,
        "commissions.html": commissions_html,
        "reports.html": reports_html,
        "profile.html": profile_html,
        "admin.html": admin_html,
    }

    for name, content in templates_to_create.items():
        template_path = TEMPLATES_DIR / name
        if not template_path.exists():
            template_path.write_text(content, encoding="utf-8")
            logger.info(f"Created template: {name}")


# ═══════════════════════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Agent Portal")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║           Agent Portal - Tourism Agent Web Portal             ║
╠═══════════════════════════════════════════════════════════════╣
║  URL: http://{args.host}:{args.port}                              ║
║  Default admin: admin / admin123                              ║
║                                                               ║
║  Features:                                                    ║
║  - Agent authentication with JWT                              ║
║  - Tour catalog with agent pricing                            ║
║  - Booking management                                         ║
║  - Commission tracking                                        ║
║  - Sales reports                                              ║
║  - Admin panel                                                ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "agent_portal:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
