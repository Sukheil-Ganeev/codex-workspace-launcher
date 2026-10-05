#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Partner API - REST API для партнёров туристической компании.

Предоставляет endpoints для:
- Просмотра каталога туров
- Проверки наличия и цен
- Создания и управления бронированиями
- Webhook callbacks для уведомлений

Использует: FastAPI, Pydantic, SlowAPI (rate limiting)
"""

import os
import sys
import json
import hashlib
import hmac
import secrets
import sqlite3
import logging
import asyncio
import httpx
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pathlib import Path
from contextlib import asynccontextmanager
from functools import wraps
import uuid

# FastAPI и связанные библиотеки
from fastapi import FastAPI, HTTPException, Depends, Request, Query, Path as PathParam, Header, BackgroundTasks
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

# Pydantic для валидации
from pydantic import BaseModel, Field, validator, EmailStr, HttpUrl
from pydantic.functional_validators import field_validator

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('partner_api')

# =============================================================================
# Конфигурация
# =============================================================================

class Settings:
    """Настройки API"""

    # База данных
    DATABASE_PATH: str = os.getenv('PARTNER_API_DB', 'partner_api.db')

    # API настройки
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Partner Tourism API"
    API_DESCRIPTION: str = """
    REST API для партнёров туристической компании.

    ## Возможности

    * **Туры** - просмотр каталога туров и деталей
    * **Наличие** - проверка доступности на даты
    * **Бронирования** - создание, просмотр, отмена
    * **Цены** - актуальный прайс-лист
    * **Webhooks** - уведомления об изменениях

    ## Аутентификация

    Используйте API Key в заголовке `X-API-Key`.

    ## Rate Limits

    - Стандартный план: 100 запросов/минуту
    - Premium план: 1000 запросов/минуту
    """

    # Rate limiting по умолчанию
    DEFAULT_RATE_LIMIT: str = "100/minute"
    PREMIUM_RATE_LIMIT: str = "1000/minute"

    # Webhook настройки
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_COUNT: int = 3
    WEBHOOK_RETRY_DELAY: int = 60

    # IP Whitelist (опционально)
    ENABLE_IP_WHITELIST: bool = os.getenv('ENABLE_IP_WHITELIST', 'false').lower() == 'true'

    # Sandbox режим
    SANDBOX_MODE: bool = os.getenv('SANDBOX_MODE', 'true').lower() == 'true'


settings = Settings()

# =============================================================================
# Enums и константы
# =============================================================================

class TourCategory(str, Enum):
    """Категории туров"""
    DESERT_SAFARI = "desert_safari"
    CITY_TOUR = "city_tour"
    BOAT_TRIP = "boat_trip"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    WATER_PARK = "water_park"
    THEME_PARK = "theme_park"
    HELICOPTER = "helicopter"
    VIP = "vip"


class BookingStatus(str, Enum):
    """Статусы бронирования"""
    PENDING = "pending"           # Ожидает подтверждения
    CONFIRMED = "confirmed"       # Подтверждено
    CANCELLED = "cancelled"       # Отменено
    COMPLETED = "completed"       # Завершено
    NO_SHOW = "no_show"          # Неявка
    REFUNDED = "refunded"        # Возвращено


class WebhookEvent(str, Enum):
    """Типы webhook событий"""
    BOOKING_CREATED = "booking.created"
    BOOKING_CONFIRMED = "booking.confirmed"
    BOOKING_CANCELLED = "booking.cancelled"
    BOOKING_COMPLETED = "booking.completed"
    PRICE_CHANGED = "price.changed"
    AVAILABILITY_CHANGED = "availability.changed"


class PartnerTier(str, Enum):
    """Уровни партнёров"""
    STANDARD = "standard"
    PREMIUM = "premium"
    VIP = "vip"


# =============================================================================
# Pydantic Models
# =============================================================================

# --- Tour Models ---

class TourBase(BaseModel):
    """Базовая модель тура"""
    name: str = Field(..., min_length=1, max_length=200, description="Название тура")
    name_en: Optional[str] = Field(None, max_length=200, description="Название на английском")
    category: TourCategory = Field(..., description="Категория тура")
    description: str = Field(..., description="Описание тура")
    description_en: Optional[str] = Field(None, description="Описание на английском")
    duration_hours: float = Field(..., gt=0, description="Продолжительность в часах")
    included: List[str] = Field(default_factory=list, description="Что включено")
    excluded: List[str] = Field(default_factory=list, description="Что не включено")
    meeting_point: Optional[str] = Field(None, description="Место встречи")
    max_participants: int = Field(default=20, ge=1, description="Максимум участников")
    min_participants: int = Field(default=1, ge=1, description="Минимум участников")
    images: List[str] = Field(default_factory=list, description="URL изображений")
    is_active: bool = Field(default=True, description="Активен ли тур")


class TourCreate(TourBase):
    """Модель для создания тура"""
    pass


class TourResponse(TourBase):
    """Модель ответа тура"""
    id: str = Field(..., description="ID тура")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    class Config:
        from_attributes = True


class TourListResponse(BaseModel):
    """Список туров с пагинацией"""
    items: List[TourResponse]
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Всего страниц")


# --- Price Models ---

class PriceType(str, Enum):
    """Типы цен"""
    ADULT = "adult"
    CHILD = "child"
    INFANT = "infant"
    PRIVATE = "private"
    GROUP = "group"


class PriceItem(BaseModel):
    """Элемент прайс-листа"""
    tour_id: str = Field(..., description="ID тура")
    tour_name: str = Field(..., description="Название тура")
    price_type: PriceType = Field(..., description="Тип цены")
    currency: str = Field(default="AED", description="Валюта")
    amount: float = Field(..., ge=0, description="Сумма")
    commission_percent: float = Field(default=10.0, ge=0, le=50, description="Комиссия партнёра %")
    valid_from: date = Field(..., description="Действует с")
    valid_until: date = Field(..., description="Действует до")
    notes: Optional[str] = Field(None, description="Примечания")


class PriceListResponse(BaseModel):
    """Прайс-лист"""
    items: List[PriceItem]
    currency: str = Field(default="AED", description="Валюта")
    updated_at: datetime = Field(..., description="Дата обновления")


# --- Availability Models ---

class TimeSlot(BaseModel):
    """Временной слот"""
    time: str = Field(..., description="Время начала (HH:MM)")
    available_spots: int = Field(..., ge=0, description="Доступные места")
    total_spots: int = Field(..., ge=0, description="Всего мест")
    price_adult: float = Field(..., ge=0, description="Цена взрослый")
    price_child: float = Field(..., ge=0, description="Цена ребёнок")


class AvailabilityResponse(BaseModel):
    """Ответ о наличии"""
    tour_id: str = Field(..., description="ID тура")
    tour_name: str = Field(..., description="Название тура")
    date: date = Field(..., description="Дата")
    is_available: bool = Field(..., description="Доступен ли тур")
    time_slots: List[TimeSlot] = Field(default_factory=list, description="Доступные слоты")
    notes: Optional[str] = Field(None, description="Примечания")


# --- Booking Models ---

class PassengerInfo(BaseModel):
    """Информация о пассажире"""
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    date_of_birth: Optional[date] = Field(None, description="Дата рождения")
    passport_number: Optional[str] = Field(None, max_length=50, description="Номер паспорта")
    nationality: Optional[str] = Field(None, max_length=50, description="Гражданство")
    special_requests: Optional[str] = Field(None, description="Особые пожелания")


class BookingCreate(BaseModel):
    """Создание бронирования"""
    tour_id: str = Field(..., description="ID тура")
    date: date = Field(..., description="Дата тура")
    time_slot: str = Field(..., description="Временной слот (HH:MM)")
    adults: int = Field(..., ge=1, description="Количество взрослых")
    children: int = Field(default=0, ge=0, description="Количество детей")
    infants: int = Field(default=0, ge=0, description="Количество младенцев")
    passengers: List[PassengerInfo] = Field(default_factory=list, description="Информация о пассажирах")
    contact_name: str = Field(..., min_length=1, description="Контактное лицо")
    contact_phone: str = Field(..., min_length=5, description="Телефон")
    contact_email: Optional[EmailStr] = Field(None, description="Email")
    pickup_location: Optional[str] = Field(None, description="Место подбора")
    notes: Optional[str] = Field(None, description="Примечания")
    partner_reference: Optional[str] = Field(None, max_length=100, description="Референс партнёра")

    @field_validator('date')
    @classmethod
    def date_not_in_past(cls, v):
        if v < date.today():
            raise ValueError('Дата не может быть в прошлом')
        return v


class BookingResponse(BaseModel):
    """Ответ бронирования"""
    id: str = Field(..., description="ID бронирования")
    partner_id: str = Field(..., description="ID партнёра")
    partner_reference: Optional[str] = Field(None, description="Референс партнёра")
    tour_id: str = Field(..., description="ID тура")
    tour_name: str = Field(..., description="Название тура")
    date: date = Field(..., description="Дата тура")
    time_slot: str = Field(..., description="Временной слот")
    status: BookingStatus = Field(..., description="Статус")
    adults: int = Field(..., description="Взрослых")
    children: int = Field(..., description="Детей")
    infants: int = Field(..., description="Младенцев")
    passengers: List[PassengerInfo] = Field(default_factory=list, description="Пассажиры")
    contact_name: str = Field(..., description="Контактное лицо")
    contact_phone: str = Field(..., description="Телефон")
    contact_email: Optional[str] = Field(None, description="Email")
    pickup_location: Optional[str] = Field(None, description="Место подбора")
    pickup_time: Optional[str] = Field(None, description="Время подбора")
    notes: Optional[str] = Field(None, description="Примечания")
    total_amount: float = Field(..., description="Общая сумма")
    commission_amount: float = Field(..., description="Сумма комиссии")
    net_amount: float = Field(..., description="Чистая сумма")
    currency: str = Field(default="AED", description="Валюта")
    voucher_url: Optional[str] = Field(None, description="URL ваучера")
    created_at: datetime = Field(..., description="Создано")
    updated_at: datetime = Field(..., description="Обновлено")
    confirmed_at: Optional[datetime] = Field(None, description="Подтверждено")
    cancelled_at: Optional[datetime] = Field(None, description="Отменено")
    cancellation_reason: Optional[str] = Field(None, description="Причина отмены")


class BookingListResponse(BaseModel):
    """Список бронирований"""
    items: List[BookingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class BookingCancelRequest(BaseModel):
    """Запрос на отмену бронирования"""
    reason: str = Field(..., min_length=1, description="Причина отмены")


# --- Webhook Models ---

class WebhookConfig(BaseModel):
    """Конфигурация webhook"""
    url: HttpUrl = Field(..., description="URL для вызова")
    events: List[WebhookEvent] = Field(..., description="События для подписки")
    secret: Optional[str] = Field(None, description="Секрет для подписи")
    is_active: bool = Field(default=True, description="Активен")


class WebhookPayload(BaseModel):
    """Payload webhook"""
    event: WebhookEvent = Field(..., description="Тип события")
    timestamp: datetime = Field(..., description="Время события")
    data: Dict[str, Any] = Field(..., description="Данные события")
    webhook_id: str = Field(..., description="ID webhook")


class WebhookResponse(BaseModel):
    """Ответ webhook конфигурации"""
    id: str = Field(..., description="ID webhook")
    url: str = Field(..., description="URL")
    events: List[WebhookEvent] = Field(..., description="События")
    is_active: bool = Field(..., description="Активен")
    created_at: datetime = Field(..., description="Создан")
    last_triggered: Optional[datetime] = Field(None, description="Последний вызов")
    success_count: int = Field(default=0, description="Успешных вызовов")
    failure_count: int = Field(default=0, description="Неудачных вызовов")


# --- Partner Models ---

class PartnerInfo(BaseModel):
    """Информация о партнёре"""
    id: str = Field(..., description="ID партнёра")
    name: str = Field(..., description="Название")
    tier: PartnerTier = Field(..., description="Уровень")
    contact_email: str = Field(..., description="Email")
    contact_phone: Optional[str] = Field(None, description="Телефон")
    commission_rate: float = Field(..., description="Комиссия %")
    rate_limit: str = Field(..., description="Rate limit")
    ip_whitelist: List[str] = Field(default_factory=list, description="IP whitelist")
    is_active: bool = Field(..., description="Активен")
    created_at: datetime = Field(..., description="Создан")


# --- API Response Models ---

class APIError(BaseModel):
    """Модель ошибки API"""
    error: str = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение")
    details: Optional[Dict[str, Any]] = Field(None, description="Детали")


class APISuccess(BaseModel):
    """Успешный ответ"""
    success: bool = Field(default=True)
    message: str = Field(..., description="Сообщение")
    data: Optional[Dict[str, Any]] = Field(None, description="Данные")


# =============================================================================
# База данных
# =============================================================================

class Database:
    """Менеджер базы данных"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Инициализация схемы БД"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Таблица партнёров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partners (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api_key_hash TEXT NOT NULL UNIQUE,
                tier TEXT DEFAULT 'standard',
                contact_email TEXT NOT NULL,
                contact_phone TEXT,
                commission_rate REAL DEFAULT 10.0,
                rate_limit TEXT DEFAULT '100/minute',
                ip_whitelist TEXT DEFAULT '[]',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Таблица туров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tours (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_en TEXT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                description_en TEXT,
                duration_hours REAL NOT NULL,
                included TEXT DEFAULT '[]',
                excluded TEXT DEFAULT '[]',
                meeting_point TEXT,
                max_participants INTEGER DEFAULT 20,
                min_participants INTEGER DEFAULT 1,
                images TEXT DEFAULT '[]',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Таблица цен
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id TEXT PRIMARY KEY,
                tour_id TEXT NOT NULL,
                price_type TEXT NOT NULL,
                currency TEXT DEFAULT 'AED',
                amount REAL NOT NULL,
                commission_percent REAL DEFAULT 10.0,
                valid_from TEXT NOT NULL,
                valid_until TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (tour_id) REFERENCES tours(id)
            )
        ''')

        # Таблица доступности
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS availability (
                id TEXT PRIMARY KEY,
                tour_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                total_spots INTEGER NOT NULL,
                booked_spots INTEGER DEFAULT 0,
                price_adult REAL NOT NULL,
                price_child REAL NOT NULL,
                notes TEXT,
                FOREIGN KEY (tour_id) REFERENCES tours(id),
                UNIQUE (tour_id, date, time_slot)
            )
        ''')

        # Таблица бронирований
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                partner_id TEXT NOT NULL,
                partner_reference TEXT,
                tour_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                adults INTEGER NOT NULL,
                children INTEGER DEFAULT 0,
                infants INTEGER DEFAULT 0,
                passengers TEXT DEFAULT '[]',
                contact_name TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                contact_email TEXT,
                pickup_location TEXT,
                pickup_time TEXT,
                notes TEXT,
                total_amount REAL NOT NULL,
                commission_amount REAL NOT NULL,
                net_amount REAL NOT NULL,
                currency TEXT DEFAULT 'AED',
                voucher_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                confirmed_at TEXT,
                cancelled_at TEXT,
                cancellation_reason TEXT,
                FOREIGN KEY (partner_id) REFERENCES partners(id),
                FOREIGN KEY (tour_id) REFERENCES tours(id)
            )
        ''')

        # Таблица webhooks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id TEXT PRIMARY KEY,
                partner_id TEXT NOT NULL,
                url TEXT NOT NULL,
                events TEXT NOT NULL,
                secret TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_triggered TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                FOREIGN KEY (partner_id) REFERENCES partners(id)
            )
        ''')

        # Таблица логов API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_logs (
                id TEXT PRIMARY KEY,
                partner_id TEXT,
                method TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                request_body TEXT,
                response_body TEXT,
                ip_address TEXT,
                user_agent TEXT,
                duration_ms REAL,
                created_at TEXT NOT NULL
            )
        ''')

        # Таблица логов webhooks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_logs (
                id TEXT PRIMARY KEY,
                webhook_id TEXT NOT NULL,
                event TEXT NOT NULL,
                payload TEXT NOT NULL,
                status_code INTEGER,
                response TEXT,
                attempt INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
            )
        ''')

        # Индексы
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_partner ON bookings(partner_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_availability_date ON availability(tour_id, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_logs_partner ON api_logs(partner_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_logs_created ON api_logs(created_at)')

        conn.commit()
        conn.close()

        # Создать тестовые данные если пусто
        self._seed_test_data()

    def _seed_test_data(self):
        """Заполнить тестовыми данными"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Проверить есть ли данные
        cursor.execute('SELECT COUNT(*) FROM partners')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        now = datetime.utcnow().isoformat()

        # Тестовый партнёр
        test_api_key = "test_api_key_12345"
        api_key_hash = hashlib.sha256(test_api_key.encode()).hexdigest()

        cursor.execute('''
            INSERT INTO partners (id, name, api_key_hash, tier, contact_email, commission_rate, rate_limit, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('partner_001', 'Test Travel Agency', api_key_hash, 'premium', 'test@agency.com', 15.0, '1000/minute', now, now))

        # Тестовые туры
        tours = [
            ('tour_001', 'Desert Safari Premium', 'Premium Desert Safari', 'desert_safari',
             'Незабываемое приключение в пустыне с ужином под звёздами',
             'Unforgettable desert adventure with dinner under the stars',
             6.0, '["Трансфер", "Ужин BBQ", "Шоу", "Катание на верблюдах"]',
             '["Персональные расходы", "Фото"]', 'Отель', 30, 2,
             '["https://example.com/desert1.jpg"]', 1, now, now),

            ('tour_002', 'Dubai City Tour', 'Dubai City Sightseeing', 'city_tour',
             'Обзорная экскурсия по Дубаю с посещением основных достопримечательностей',
             'Sightseeing tour of Dubai visiting main attractions',
             4.0, '["Трансфер", "Гид", "Входные билеты"]',
             '["Питание", "Личные расходы"]', 'Отель', 40, 1,
             '["https://example.com/city1.jpg"]', 1, now, now),

            ('tour_003', 'Yacht Cruise Marina', 'Marina Yacht Cruise', 'boat_trip',
             'Круиз на яхте по Dubai Marina с завтраком или ужином',
             'Yacht cruise around Dubai Marina with breakfast or dinner',
             3.0, '["Трансфер", "Питание", "Напитки"]',
             '["Алкоголь"]', 'Dubai Marina', 20, 2,
             '["https://example.com/yacht1.jpg"]', 1, now, now),

            ('tour_004', 'Abu Dhabi Day Trip', 'Abu Dhabi Full Day', 'city_tour',
             'Однодневная экскурсия в Абу-Даби с посещением мечети и Лувра',
             'Full day trip to Abu Dhabi including Grand Mosque and Louvre',
             10.0, '["Трансфер", "Гид", "Входные билеты", "Обед"]',
             '["Личные расходы"]', 'Отель', 35, 1,
             '["https://example.com/abudhabi1.jpg"]', 1, now, now),

            ('tour_005', 'Helicopter Tour', 'Dubai Helicopter Tour', 'helicopter',
             'Вертолётная экскурсия над Дубаем - Palm Jumeirah и Burj Khalifa',
             'Helicopter tour over Dubai - Palm Jumeirah and Burj Khalifa',
             0.5, '["Полёт 12-15 минут", "Фото", "Сертификат"]',
             '["Трансфер"]', 'Atlantis Helipad', 5, 1,
             '["https://example.com/heli1.jpg"]', 1, now, now),
        ]

        cursor.executemany('''
            INSERT INTO tours (id, name, name_en, category, description, description_en,
                             duration_hours, included, excluded, meeting_point,
                             max_participants, min_participants, images, is_active,
                             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tours)

        # Цены
        today = date.today()
        valid_until = today + timedelta(days=365)

        prices = [
            ('price_001', 'tour_001', 'adult', 'AED', 250.0, 15.0, today.isoformat(), valid_until.isoformat(), None, now),
            ('price_002', 'tour_001', 'child', 'AED', 200.0, 15.0, today.isoformat(), valid_until.isoformat(), '3-11 лет', now),
            ('price_003', 'tour_002', 'adult', 'AED', 150.0, 15.0, today.isoformat(), valid_until.isoformat(), None, now),
            ('price_004', 'tour_002', 'child', 'AED', 100.0, 15.0, today.isoformat(), valid_until.isoformat(), '3-11 лет', now),
            ('price_005', 'tour_003', 'adult', 'AED', 350.0, 15.0, today.isoformat(), valid_until.isoformat(), None, now),
            ('price_006', 'tour_003', 'child', 'AED', 250.0, 15.0, today.isoformat(), valid_until.isoformat(), '3-11 лет', now),
            ('price_007', 'tour_004', 'adult', 'AED', 280.0, 15.0, today.isoformat(), valid_until.isoformat(), None, now),
            ('price_008', 'tour_004', 'child', 'AED', 220.0, 15.0, today.isoformat(), valid_until.isoformat(), '3-11 лет', now),
            ('price_009', 'tour_005', 'adult', 'AED', 750.0, 10.0, today.isoformat(), valid_until.isoformat(), 'Мин. 2 пассажира', now),
            ('price_010', 'tour_005', 'private', 'AED', 3500.0, 10.0, today.isoformat(), valid_until.isoformat(), 'Приватный полёт', now),
        ]

        cursor.executemany('''
            INSERT INTO prices (id, tour_id, price_type, currency, amount, commission_percent,
                              valid_from, valid_until, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', prices)

        # Доступность на ближайшие 30 дней
        availability_records = []
        for i in range(30):
            avail_date = (today + timedelta(days=i)).isoformat()

            # Desert Safari - 2 слота в день
            for time_slot in ['15:00', '15:30']:
                availability_records.append(
                    (str(uuid.uuid4()), 'tour_001', avail_date, time_slot, 30, 0, 250.0, 200.0, None)
                )

            # City Tour - 2 слота
            for time_slot in ['08:00', '14:00']:
                availability_records.append(
                    (str(uuid.uuid4()), 'tour_002', avail_date, time_slot, 40, 0, 150.0, 100.0, None)
                )

            # Yacht - 3 слота
            for time_slot in ['10:00', '14:00', '18:00']:
                availability_records.append(
                    (str(uuid.uuid4()), 'tour_003', avail_date, time_slot, 20, 0, 350.0, 250.0, None)
                )

            # Abu Dhabi - 1 слот
            availability_records.append(
                (str(uuid.uuid4()), 'tour_004', avail_date, '07:00', 35, 0, 280.0, 220.0, None)
            )

            # Helicopter - каждый час
            for hour in range(9, 18):
                time_slot = f'{hour:02d}:00'
                availability_records.append(
                    (str(uuid.uuid4()), 'tour_005', avail_date, time_slot, 5, 0, 750.0, 750.0, None)
                )

        cursor.executemany('''
            INSERT INTO availability (id, tour_id, date, time_slot, total_spots, booked_spots,
                                     price_adult, price_child, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', availability_records)

        conn.commit()
        conn.close()

        logger.info(f"Seeded test data. Test API Key: {test_api_key}")

    # CRUD операции

    def get_partner_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Найти партнёра по API ключу"""
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM partners WHERE api_key_hash = ? AND is_active = 1', (api_key_hash,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_tours(self, category: Optional[str] = None, is_active: bool = True,
                  page: int = 1, page_size: int = 20) -> Dict:
        """Получить список туров"""
        conn = self._get_connection()
        cursor = conn.cursor()

        where_clauses = []
        params = []

        if is_active:
            where_clauses.append('is_active = 1')

        if category:
            where_clauses.append('category = ?')
            params.append(category)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        # Подсчёт
        cursor.execute(f'SELECT COUNT(*) FROM tours WHERE {where_sql}', params)
        total = cursor.fetchone()[0]

        # Данные
        offset = (page - 1) * page_size
        cursor.execute(
            f'SELECT * FROM tours WHERE {where_sql} ORDER BY name LIMIT ? OFFSET ?',
            params + [page_size, offset]
        )

        items = []
        for row in cursor.fetchall():
            item = dict(row)
            item['included'] = json.loads(item['included'])
            item['excluded'] = json.loads(item['excluded'])
            item['images'] = json.loads(item['images'])
            items.append(item)

        conn.close()

        pages = (total + page_size - 1) // page_size
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': pages
        }

    def get_tour(self, tour_id: str) -> Optional[Dict]:
        """Получить тур по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tours WHERE id = ?', (tour_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            item = dict(row)
            item['included'] = json.loads(item['included'])
            item['excluded'] = json.loads(item['excluded'])
            item['images'] = json.loads(item['images'])
            return item
        return None

    def get_availability(self, tour_id: str, date_str: str) -> Dict:
        """Получить доступность тура на дату"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Получить тур
        cursor.execute('SELECT id, name FROM tours WHERE id = ?', (tour_id,))
        tour = cursor.fetchone()

        if not tour:
            conn.close()
            return None

        # Получить слоты
        cursor.execute('''
            SELECT time_slot, total_spots, booked_spots, price_adult, price_child
            FROM availability
            WHERE tour_id = ? AND date = ?
            ORDER BY time_slot
        ''', (tour_id, date_str))

        slots = []
        is_available = False
        for row in cursor.fetchall():
            available = row['total_spots'] - row['booked_spots']
            if available > 0:
                is_available = True
            slots.append({
                'time': row['time_slot'],
                'available_spots': available,
                'total_spots': row['total_spots'],
                'price_adult': row['price_adult'],
                'price_child': row['price_child']
            })

        conn.close()

        return {
            'tour_id': tour['id'],
            'tour_name': tour['name'],
            'date': date_str,
            'is_available': is_available,
            'time_slots': slots,
            'notes': None
        }

    def get_prices(self, tour_id: Optional[str] = None) -> List[Dict]:
        """Получить прайс-лист"""
        conn = self._get_connection()
        cursor = conn.cursor()

        today = date.today().isoformat()

        if tour_id:
            cursor.execute('''
                SELECT p.*, t.name as tour_name
                FROM prices p
                JOIN tours t ON p.tour_id = t.id
                WHERE p.tour_id = ? AND p.valid_from <= ? AND p.valid_until >= ?
                ORDER BY t.name, p.price_type
            ''', (tour_id, today, today))
        else:
            cursor.execute('''
                SELECT p.*, t.name as tour_name
                FROM prices p
                JOIN tours t ON p.tour_id = t.id
                WHERE p.valid_from <= ? AND p.valid_until >= ? AND t.is_active = 1
                ORDER BY t.name, p.price_type
            ''', (today, today))

        items = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return items

    def create_booking(self, partner_id: str, data: Dict) -> Dict:
        """Создать бронирование"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Проверить наличие
        cursor.execute('''
            SELECT id, total_spots, booked_spots, price_adult, price_child
            FROM availability
            WHERE tour_id = ? AND date = ? AND time_slot = ?
        ''', (data['tour_id'], data['date'], data['time_slot']))

        avail = cursor.fetchone()
        if not avail:
            conn.close()
            raise ValueError('Слот недоступен')

        total_guests = data['adults'] + data['children']
        available = avail['total_spots'] - avail['booked_spots']

        if total_guests > available:
            conn.close()
            raise ValueError(f'Недостаточно мест. Доступно: {available}')

        # Получить тур
        cursor.execute('SELECT name FROM tours WHERE id = ?', (data['tour_id'],))
        tour = cursor.fetchone()

        # Получить комиссию партнёра
        cursor.execute('SELECT commission_rate FROM partners WHERE id = ?', (partner_id,))
        partner = cursor.fetchone()
        commission_rate = partner['commission_rate'] if partner else 10.0

        # Расчёт цены
        total_amount = (data['adults'] * avail['price_adult'] +
                       data['children'] * avail['price_child'])
        commission_amount = total_amount * commission_rate / 100
        net_amount = total_amount - commission_amount

        # Создать бронирование
        booking_id = f"BK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(4).upper()}"
        now = datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO bookings (id, partner_id, partner_reference, tour_id, date, time_slot,
                                 status, adults, children, infants, passengers,
                                 contact_name, contact_phone, contact_email,
                                 pickup_location, notes, total_amount, commission_amount,
                                 net_amount, currency, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking_id, partner_id, data.get('partner_reference'),
            data['tour_id'], data['date'], data['time_slot'],
            'pending', data['adults'], data['children'], data.get('infants', 0),
            json.dumps([p.dict() if hasattr(p, 'dict') else p for p in data.get('passengers', [])]),
            data['contact_name'], data['contact_phone'], data.get('contact_email'),
            data.get('pickup_location'), data.get('notes'),
            total_amount, commission_amount, net_amount, 'AED', now, now
        ))

        # Обновить доступность
        cursor.execute('''
            UPDATE availability SET booked_spots = booked_spots + ?
            WHERE id = ?
        ''', (total_guests, avail['id']))

        conn.commit()

        # Получить созданную запись
        cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        booking = dict(cursor.fetchone())
        booking['tour_name'] = tour['name']
        booking['passengers'] = json.loads(booking['passengers'])

        conn.close()

        return booking

    def get_booking(self, booking_id: str, partner_id: str) -> Optional[Dict]:
        """Получить бронирование"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT b.*, t.name as tour_name
            FROM bookings b
            JOIN tours t ON b.tour_id = t.id
            WHERE b.id = ? AND b.partner_id = ?
        ''', (booking_id, partner_id))

        row = cursor.fetchone()
        conn.close()

        if row:
            booking = dict(row)
            booking['passengers'] = json.loads(booking['passengers'])
            return booking
        return None

    def get_partner_bookings(self, partner_id: str, status: Optional[str] = None,
                            date_from: Optional[str] = None, date_to: Optional[str] = None,
                            page: int = 1, page_size: int = 20) -> Dict:
        """Получить бронирования партнёра"""
        conn = self._get_connection()
        cursor = conn.cursor()

        where_clauses = ['b.partner_id = ?']
        params = [partner_id]

        if status:
            where_clauses.append('b.status = ?')
            params.append(status)

        if date_from:
            where_clauses.append('b.date >= ?')
            params.append(date_from)

        if date_to:
            where_clauses.append('b.date <= ?')
            params.append(date_to)

        where_sql = ' AND '.join(where_clauses)

        # Подсчёт
        cursor.execute(f'SELECT COUNT(*) FROM bookings b WHERE {where_sql}', params)
        total = cursor.fetchone()[0]

        # Данные
        offset = (page - 1) * page_size
        cursor.execute(f'''
            SELECT b.*, t.name as tour_name
            FROM bookings b
            JOIN tours t ON b.tour_id = t.id
            WHERE {where_sql}
            ORDER BY b.created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [page_size, offset])

        items = []
        for row in cursor.fetchall():
            item = dict(row)
            item['passengers'] = json.loads(item['passengers'])
            items.append(item)

        conn.close()

        pages = (total + page_size - 1) // page_size
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': pages
        }

    def cancel_booking(self, booking_id: str, partner_id: str, reason: str) -> Optional[Dict]:
        """Отменить бронирование"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Получить бронирование
        cursor.execute('''
            SELECT b.*, t.name as tour_name
            FROM bookings b
            JOIN tours t ON b.tour_id = t.id
            WHERE b.id = ? AND b.partner_id = ?
        ''', (booking_id, partner_id))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        booking = dict(row)

        if booking['status'] in ['cancelled', 'completed', 'refunded']:
            conn.close()
            raise ValueError(f"Бронирование уже {booking['status']}")

        # Проверить можно ли отменить (за 24 часа)
        tour_datetime = datetime.strptime(f"{booking['date']} {booking['time_slot']}", '%Y-%m-%d %H:%M')
        if tour_datetime - datetime.utcnow() < timedelta(hours=24):
            conn.close()
            raise ValueError('Отмена возможна минимум за 24 часа до тура')

        now = datetime.utcnow().isoformat()

        # Отменить
        cursor.execute('''
            UPDATE bookings
            SET status = 'cancelled', cancelled_at = ?, cancellation_reason = ?, updated_at = ?
            WHERE id = ?
        ''', (now, reason, now, booking_id))

        # Вернуть места
        total_guests = booking['adults'] + booking['children']
        cursor.execute('''
            UPDATE availability
            SET booked_spots = booked_spots - ?
            WHERE tour_id = ? AND date = ? AND time_slot = ?
        ''', (total_guests, booking['tour_id'], booking['date'], booking['time_slot']))

        conn.commit()

        # Получить обновлённую запись
        cursor.execute('''
            SELECT b.*, t.name as tour_name
            FROM bookings b
            JOIN tours t ON b.tour_id = t.id
            WHERE b.id = ?
        ''', (booking_id,))

        booking = dict(cursor.fetchone())
        booking['passengers'] = json.loads(booking['passengers'])

        conn.close()

        return booking

    # Webhooks

    def get_partner_webhooks(self, partner_id: str) -> List[Dict]:
        """Получить webhooks партнёра"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM webhooks WHERE partner_id = ?', (partner_id,))
        items = []
        for row in cursor.fetchall():
            item = dict(row)
            item['events'] = json.loads(item['events'])
            items.append(item)

        conn.close()
        return items

    def create_webhook(self, partner_id: str, url: str, events: List[str], secret: Optional[str] = None) -> Dict:
        """Создать webhook"""
        conn = self._get_connection()
        cursor = conn.cursor()

        webhook_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO webhooks (id, partner_id, url, events, secret, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (webhook_id, partner_id, url, json.dumps(events), secret, now))

        conn.commit()

        cursor.execute('SELECT * FROM webhooks WHERE id = ?', (webhook_id,))
        webhook = dict(cursor.fetchone())
        webhook['events'] = json.loads(webhook['events'])

        conn.close()
        return webhook

    def delete_webhook(self, webhook_id: str, partner_id: str) -> bool:
        """Удалить webhook"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM webhooks WHERE id = ? AND partner_id = ?', (webhook_id, partner_id))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def get_webhooks_for_event(self, partner_id: str, event: str) -> List[Dict]:
        """Получить webhooks для события"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM webhooks
            WHERE partner_id = ? AND is_active = 1
        ''', (partner_id,))

        webhooks = []
        for row in cursor.fetchall():
            item = dict(row)
            events = json.loads(item['events'])
            if event in events:
                item['events'] = events
                webhooks.append(item)

        conn.close()
        return webhooks

    def log_webhook(self, webhook_id: str, event: str, payload: str,
                   status_code: Optional[int] = None, response: Optional[str] = None,
                   attempt: int = 1):
        """Логировать вызов webhook"""
        conn = self._get_connection()
        cursor = conn.cursor()

        log_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO webhook_logs (id, webhook_id, event, payload, status_code, response, attempt, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (log_id, webhook_id, event, payload, status_code, response, attempt, now))

        # Обновить счётчики
        if status_code and 200 <= status_code < 300:
            cursor.execute('''
                UPDATE webhooks SET success_count = success_count + 1, last_triggered = ? WHERE id = ?
            ''', (now, webhook_id))
        else:
            cursor.execute('''
                UPDATE webhooks SET failure_count = failure_count + 1, last_triggered = ? WHERE id = ?
            ''', (now, webhook_id))

        conn.commit()
        conn.close()

    # API Logging

    def log_api_request(self, partner_id: Optional[str], method: str, endpoint: str,
                       status_code: int, request_body: Optional[str] = None,
                       response_body: Optional[str] = None, ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None, duration_ms: Optional[float] = None):
        """Логировать API запрос"""
        conn = self._get_connection()
        cursor = conn.cursor()

        log_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO api_logs (id, partner_id, method, endpoint, status_code,
                                 request_body, response_body, ip_address, user_agent,
                                 duration_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (log_id, partner_id, method, endpoint, status_code,
              request_body, response_body, ip_address, user_agent, duration_ms, now))

        conn.commit()
        conn.close()

    def get_api_stats(self, partner_id: str, days: int = 30) -> Dict:
        """Получить статистику API"""
        conn = self._get_connection()
        cursor = conn.cursor()

        since = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Общее количество запросов
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 ELSE 0 END) as success,
                   SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors,
                   AVG(duration_ms) as avg_duration
            FROM api_logs
            WHERE partner_id = ? AND created_at >= ?
        ''', (partner_id, since))

        stats = dict(cursor.fetchone())

        # По endpoint
        cursor.execute('''
            SELECT endpoint, COUNT(*) as count
            FROM api_logs
            WHERE partner_id = ? AND created_at >= ?
            GROUP BY endpoint
            ORDER BY count DESC
            LIMIT 10
        ''', (partner_id, since))

        stats['by_endpoint'] = [dict(row) for row in cursor.fetchall()]

        # По дням
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM api_logs
            WHERE partner_id = ? AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''', (partner_id, since))

        stats['by_date'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return stats


# Глобальный экземпляр БД
db = Database(settings.DATABASE_PATH)

# =============================================================================
# Rate Limiting
# =============================================================================

def get_partner_rate_limit(request: Request) -> str:
    """Получить rate limit для партнёра"""
    api_key = request.headers.get('X-API-Key')
    if api_key:
        partner = db.get_partner_by_api_key(api_key)
        if partner:
            return partner.get('rate_limit', settings.DEFAULT_RATE_LIMIT)
    return settings.DEFAULT_RATE_LIMIT


limiter = Limiter(key_func=get_remote_address, default_limits=[settings.DEFAULT_RATE_LIMIT])

# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("Starting Partner API...")
    yield
    logger.info("Shutting down Partner API...")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# =============================================================================
# Dependencies
# =============================================================================

async def get_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header)
) -> str:
    """Валидация API ключа"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={"error": "unauthorized", "message": "API Key required"}
        )

    partner = db.get_partner_by_api_key(api_key)
    if not partner:
        raise HTTPException(
            status_code=401,
            detail={"error": "unauthorized", "message": "Invalid API Key"}
        )

    # IP whitelist проверка
    if settings.ENABLE_IP_WHITELIST:
        ip_whitelist = json.loads(partner.get('ip_whitelist', '[]'))
        if ip_whitelist:
            client_ip = request.client.host
            if client_ip not in ip_whitelist:
                raise HTTPException(
                    status_code=403,
                    detail={"error": "forbidden", "message": "IP address not in whitelist"}
                )

    return api_key


async def get_current_partner(api_key: str = Depends(get_api_key)) -> Dict:
    """Получить текущего партнёра"""
    partner = db.get_partner_by_api_key(api_key)
    return partner


# =============================================================================
# Webhook Service
# =============================================================================

class WebhookService:
    """Сервис для отправки webhook уведомлений"""

    @staticmethod
    async def send_webhook(webhook: Dict, event: WebhookEvent, data: Dict):
        """Отправить webhook"""
        payload = WebhookPayload(
            event=event,
            timestamp=datetime.utcnow(),
            data=data,
            webhook_id=webhook['id']
        )

        payload_json = payload.model_dump_json()

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Event': event.value,
            'X-Webhook-ID': webhook['id']
        }

        # Подпись если есть секрет
        if webhook.get('secret'):
            signature = hmac.new(
                webhook['secret'].encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = f"sha256={signature}"

        for attempt in range(1, settings.WEBHOOK_RETRY_COUNT + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT) as client:
                    response = await client.post(
                        webhook['url'],
                        content=payload_json,
                        headers=headers
                    )

                    db.log_webhook(
                        webhook['id'], event.value, payload_json,
                        response.status_code, response.text[:1000], attempt
                    )

                    if 200 <= response.status_code < 300:
                        logger.info(f"Webhook sent successfully: {webhook['url']}")
                        return

                    logger.warning(f"Webhook returned {response.status_code}: {webhook['url']}")

            except Exception as e:
                logger.error(f"Webhook error (attempt {attempt}): {e}")
                db.log_webhook(
                    webhook['id'], event.value, payload_json,
                    None, str(e), attempt
                )

            if attempt < settings.WEBHOOK_RETRY_COUNT:
                await asyncio.sleep(settings.WEBHOOK_RETRY_DELAY)

    @staticmethod
    async def trigger_event(partner_id: str, event: WebhookEvent, data: Dict):
        """Триггер события для всех подписанных webhooks"""
        webhooks = db.get_webhooks_for_event(partner_id, event.value)

        for webhook in webhooks:
            asyncio.create_task(WebhookService.send_webhook(webhook, event, data))


webhook_service = WebhookService()

# =============================================================================
# Logging Middleware
# =============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех запросов"""
    import time
    start_time = time.time()

    # Получить тело запроса
    body = None
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            body = await request.body()
            body = body.decode()[:5000]  # Ограничить размер
        except:
            pass

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000

    # Логирование
    api_key = request.headers.get('X-API-Key')
    partner_id = None
    if api_key:
        partner = db.get_partner_by_api_key(api_key)
        if partner:
            partner_id = partner['id']

    # Логируем только API запросы
    if request.url.path.startswith('/api/'):
        db.log_api_request(
            partner_id=partner_id,
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            request_body=body,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get('User-Agent'),
            duration_ms=duration_ms
        )

    return response

# =============================================================================
# API Endpoints
# =============================================================================

# --- Health Check ---

@app.get("/health", tags=["System"])
async def health_check():
    """Проверка состояния API"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# --- Tours ---

@app.get("/api/v1/tours", response_model=TourListResponse, tags=["Tours"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def list_tours(
    request: Request,
    category: Optional[TourCategory] = Query(None, description="Фильтр по категории"),
    page: int = Query(1, ge=1, description="Страница"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить список доступных туров.

    Возвращает пагинированный список активных туров с возможностью фильтрации по категории.
    """
    result = db.get_tours(
        category=category.value if category else None,
        page=page,
        page_size=page_size
    )

    return TourListResponse(
        items=[TourResponse(**item) for item in result['items']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        pages=result['pages']
    )


@app.get("/api/v1/tours/{tour_id}", response_model=TourResponse, tags=["Tours"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def get_tour(
    request: Request,
    tour_id: str = PathParam(..., description="ID тура"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить детальную информацию о туре.

    Возвращает полную информацию о туре включая описание, что включено/не включено и т.д.
    """
    tour = db.get_tour(tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Tour not found"}
        )

    return TourResponse(**tour)


# --- Availability ---

@app.get("/api/v1/availability", response_model=AvailabilityResponse, tags=["Availability"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def check_availability(
    request: Request,
    tour_id: str = Query(..., description="ID тура"),
    date: date = Query(..., description="Дата (YYYY-MM-DD)"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Проверить наличие мест на тур.

    Возвращает доступные временные слоты с количеством мест и ценами.
    """
    if date < date.today():
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_date", "message": "Date cannot be in the past"}
        )

    result = db.get_availability(tour_id, date.isoformat())

    if not result:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Tour not found"}
        )

    return AvailabilityResponse(**result)


# --- Prices ---

@app.get("/api/v1/prices", response_model=PriceListResponse, tags=["Prices"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def get_prices(
    request: Request,
    tour_id: Optional[str] = Query(None, description="Фильтр по туру"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить актуальный прайс-лист.

    Возвращает текущие цены на все туры или конкретный тур.
    """
    items = db.get_prices(tour_id)

    return PriceListResponse(
        items=[PriceItem(**item) for item in items],
        currency="AED",
        updated_at=datetime.utcnow()
    )


# --- Bookings ---

@app.post("/api/v1/bookings", response_model=BookingResponse, status_code=201, tags=["Bookings"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def create_booking(
    request: Request,
    booking: BookingCreate,
    background_tasks: BackgroundTasks,
    partner: Dict = Depends(get_current_partner)
):
    """
    Создать новое бронирование.

    Создаёт бронирование в статусе "pending". После подтверждения оператором
    статус изменится на "confirmed" и будет отправлен webhook.
    """
    try:
        result = db.create_booking(partner['id'], booking.model_dump())

        # Отправить webhook
        background_tasks.add_task(
            webhook_service.trigger_event,
            partner['id'],
            WebhookEvent.BOOKING_CREATED,
            result
        )

        return BookingResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "booking_error", "message": str(e)}
        )


@app.get("/api/v1/bookings", response_model=BookingListResponse, tags=["Bookings"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def list_bookings(
    request: Request,
    status: Optional[BookingStatus] = Query(None, description="Фильтр по статусу"),
    date_from: Optional[date] = Query(None, description="Дата с"),
    date_to: Optional[date] = Query(None, description="Дата по"),
    page: int = Query(1, ge=1, description="Страница"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить список бронирований партнёра.

    Возвращает пагинированный список с возможностью фильтрации.
    """
    result = db.get_partner_bookings(
        partner_id=partner['id'],
        status=status.value if status else None,
        date_from=date_from.isoformat() if date_from else None,
        date_to=date_to.isoformat() if date_to else None,
        page=page,
        page_size=page_size
    )

    return BookingListResponse(
        items=[BookingResponse(**item) for item in result['items']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        pages=result['pages']
    )


@app.get("/api/v1/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def get_booking(
    request: Request,
    booking_id: str = PathParam(..., description="ID бронирования"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить детали бронирования.

    Возвращает полную информацию о бронировании включая статус и цены.
    """
    booking = db.get_booking(booking_id, partner['id'])

    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Booking not found"}
        )

    return BookingResponse(**booking)


@app.delete("/api/v1/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def cancel_booking(
    request: Request,
    booking_id: str = PathParam(..., description="ID бронирования"),
    cancel_request: BookingCancelRequest = None,
    background_tasks: BackgroundTasks = None,
    partner: Dict = Depends(get_current_partner)
):
    """
    Отменить бронирование.

    Отмена возможна минимум за 24 часа до начала тура.
    После отмены места возвращаются в доступность.
    """
    reason = cancel_request.reason if cancel_request else "Cancelled by partner"

    try:
        result = db.cancel_booking(booking_id, partner['id'], reason)

        if not result:
            raise HTTPException(
                status_code=404,
                detail={"error": "not_found", "message": "Booking not found"}
            )

        # Отправить webhook
        if background_tasks:
            background_tasks.add_task(
                webhook_service.trigger_event,
                partner['id'],
                WebhookEvent.BOOKING_CANCELLED,
                result
            )

        return BookingResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "cancellation_error", "message": str(e)}
        )


# --- Webhooks ---

@app.get("/api/v1/webhooks", response_model=List[WebhookResponse], tags=["Webhooks"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def list_webhooks(
    request: Request,
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить список webhook подписок.
    """
    webhooks = db.get_partner_webhooks(partner['id'])
    return [WebhookResponse(**w) for w in webhooks]


@app.post("/api/v1/webhooks", response_model=WebhookResponse, status_code=201, tags=["Webhooks"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def create_webhook(
    request: Request,
    config: WebhookConfig,
    partner: Dict = Depends(get_current_partner)
):
    """
    Создать webhook подписку.

    Укажите URL для получения уведомлений и список событий для подписки.
    Опционально можно указать секрет для подписи payload.
    """
    webhook = db.create_webhook(
        partner_id=partner['id'],
        url=str(config.url),
        events=[e.value for e in config.events],
        secret=config.secret
    )

    return WebhookResponse(**webhook)


@app.delete("/api/v1/webhooks/{webhook_id}", response_model=APISuccess, tags=["Webhooks"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def delete_webhook(
    request: Request,
    webhook_id: str = PathParam(..., description="ID webhook"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Удалить webhook подписку.
    """
    deleted = db.delete_webhook(webhook_id, partner['id'])

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Webhook not found"}
        )

    return APISuccess(message="Webhook deleted successfully")


# --- Partner Info ---

@app.get("/api/v1/me", response_model=PartnerInfo, tags=["Partner"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def get_partner_info(
    request: Request,
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить информацию о текущем партнёре.
    """
    return PartnerInfo(
        id=partner['id'],
        name=partner['name'],
        tier=PartnerTier(partner['tier']),
        contact_email=partner['contact_email'],
        contact_phone=partner.get('contact_phone'),
        commission_rate=partner['commission_rate'],
        rate_limit=partner['rate_limit'],
        ip_whitelist=json.loads(partner.get('ip_whitelist', '[]')),
        is_active=bool(partner['is_active']),
        created_at=datetime.fromisoformat(partner['created_at'])
    )


@app.get("/api/v1/me/stats", tags=["Partner"])
@limiter.limit(dynamic_limits=get_partner_rate_limit)
async def get_partner_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Период в днях"),
    partner: Dict = Depends(get_current_partner)
):
    """
    Получить статистику использования API.
    """
    stats = db.get_api_stats(partner['id'], days)
    return stats


# --- Sandbox ---

@app.post("/api/v1/sandbox/reset", response_model=APISuccess, tags=["Sandbox"])
@limiter.limit("10/hour")
async def reset_sandbox(
    request: Request,
    partner: Dict = Depends(get_current_partner)
):
    """
    Сбросить тестовые данные в sandbox.

    Доступно только в sandbox режиме.
    """
    if not settings.SANDBOX_MODE:
        raise HTTPException(
            status_code=403,
            detail={"error": "forbidden", "message": "Only available in sandbox mode"}
        )

    # Удалить бронирования партнёра
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookings WHERE partner_id = ?', (partner['id'],))
    cursor.execute('DELETE FROM webhook_logs WHERE webhook_id IN (SELECT id FROM webhooks WHERE partner_id = ?)', (partner['id'],))
    cursor.execute('DELETE FROM api_logs WHERE partner_id = ?', (partner['id'],))

    # Сбросить доступность
    cursor.execute('UPDATE availability SET booked_spots = 0')

    conn.commit()
    conn.close()

    return APISuccess(message="Sandbox data reset successfully")


# =============================================================================
# OpenAPI Customization
# =============================================================================

def custom_openapi():
    """Кастомная OpenAPI схема"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        routes=app.routes,
    )

    # Добавить security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key для аутентификации"
        }
    }

    # Применить ко всем endpoints
    for path in openapi_schema["paths"]:
        if path.startswith("/api/"):
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"ApiKeyAuth": []}]

    # Добавить примеры
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }

    # Webhook events описание
    openapi_schema["webhooks"] = {
        "bookingCreated": {
            "post": {
                "summary": "Бронирование создано",
                "description": "Отправляется при создании нового бронирования",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/WebhookPayload"}
                        }
                    }
                }
            }
        },
        "bookingConfirmed": {
            "post": {
                "summary": "Бронирование подтверждено",
                "description": "Отправляется при подтверждении бронирования оператором"
            }
        },
        "bookingCancelled": {
            "post": {
                "summary": "Бронирование отменено",
                "description": "Отправляется при отмене бронирования"
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# =============================================================================
# CLI
# =============================================================================

def main():
    """Запуск API сервера"""
    import argparse

    parser = argparse.ArgumentParser(description='Partner Tourism API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--generate-key', action='store_true', help='Generate new API key')
    parser.add_argument('--partner-name', help='Partner name for key generation')

    args = parser.parse_args()

    if args.generate_key:
        # Генерация нового API ключа
        if not args.partner_name:
            print("Error: --partner-name required for key generation")
            sys.exit(1)

        api_key = f"pk_{secrets.token_hex(24)}"
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        partner_id = f"partner_{secrets.token_hex(8)}"
        now = datetime.utcnow().isoformat()

        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO partners (id, name, api_key_hash, contact_email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (partner_id, args.partner_name, api_key_hash, 'partner@example.com', now, now))
        conn.commit()
        conn.close()

        print(f"\n{'='*50}")
        print("New Partner Created")
        print(f"{'='*50}")
        print(f"Partner ID: {partner_id}")
        print(f"Partner Name: {args.partner_name}")
        print(f"API Key: {api_key}")
        print(f"{'='*50}")
        print("IMPORTANT: Save this API key securely!")
        print("It cannot be retrieved after this point.")
        print(f"{'='*50}\n")
        return

    # Запуск сервера
    import uvicorn

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    Partner Tourism API                        ║
╠══════════════════════════════════════════════════════════════╣
║  Docs:    http://{args.host}:{args.port}/docs                           ║
║  ReDoc:   http://{args.host}:{args.port}/redoc                          ║
║  OpenAPI: http://{args.host}:{args.port}/openapi.json                   ║
╠══════════════════════════════════════════════════════════════╣
║  Test API Key: test_api_key_12345                             ║
║  Sandbox Mode: {str(settings.SANDBOX_MODE).ljust(43)}║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "partner_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level="info"
    )


if __name__ == "__main__":
    main()
