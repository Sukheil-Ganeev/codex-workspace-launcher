-- 02-Booking System Schema
-- Система бронирований туров, яхт, и автомобилей в ОАЭ
-- Production-ready PostgreSQL

-- Таблица типов туров
CREATE TABLE tour_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- city-tour, desert-safari, yacht, car-rental, adventure
    min_participants INTEGER DEFAULT 1,
    max_participants INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица бронирований
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    booking_code VARCHAR(50) NOT NULL UNIQUE,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL ON UPDATE CASCADE,
    tour_type_id INTEGER REFERENCES tour_types(id) ON DELETE SET NULL ON UPDATE CASCADE,
    booking_date TIMESTAMPTZ NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    number_of_participants INTEGER NOT NULL DEFAULT 1,
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    currency VARCHAR(3) DEFAULT 'AED', -- AED, USD, RUB, KZT
    discount_percent NUMERIC(5, 2) DEFAULT 0,
    discount_reason VARCHAR(255),
    final_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, confirmed, cancelled, completed
    payment_status VARCHAR(50) DEFAULT 'unpaid', -- unpaid, partial, paid, refunded
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_dates CHECK (end_date >= start_date),
    CONSTRAINT check_participants CHECK (number_of_participants > 0)
);

-- Таблица линий услуг бронирования (tour items)
CREATE TABLE booking_items (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    item_type VARCHAR(50) NOT NULL, -- accommodation, transportation, activity, meal, guide
    description VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_price NUMERIC(12, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_quantity CHECK (quantity > 0)
);

-- Таблица участников тура
CREATE TABLE booking_participants (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    passport_number VARCHAR(50),
    nationality VARCHAR(100),
    date_of_birth DATE,
    special_requirements TEXT, -- dietary, mobility, allergies
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица платежей по бронированиям
CREATE TABLE booking_payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    payment_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'AED',
    payment_method VARCHAR(50), -- cash, credit-card, bank-transfer, check, crypto
    transaction_id VARCHAR(100),
    payment_gateway VARCHAR(100), -- stripe, paypal, 2checkout, adyen
    status VARCHAR(50) DEFAULT 'completed', -- pending, completed, failed, refunded
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица возвратов платежей
CREATE TABLE booking_refunds (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    refund_amount NUMERIC(12, 2) NOT NULL CHECK (refund_amount > 0),
    currency VARCHAR(3) DEFAULT 'AED',
    reason VARCHAR(255) NOT NULL,
    refund_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed
    original_payment_id INTEGER REFERENCES booking_payments(id) ON DELETE SET NULL ON UPDATE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица изменений в бронировании
CREATE TABLE booking_changes (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    change_type VARCHAR(50) NOT NULL, -- date, participants, amount, status, cancellation
    old_value TEXT,
    new_value TEXT,
    reason VARCHAR(255),
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица отмены и выгод от отмены
CREATE TABLE booking_cancellations (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    cancellation_date DATE NOT NULL,
    cancellation_reason VARCHAR(255),
    refund_policy VARCHAR(50), -- full, partial, none
    refund_amount NUMERIC(12, 2),
    cancellation_fee NUMERIC(12, 2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица промокодов и скидок
CREATE TABLE promo_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    discount_type VARCHAR(20), -- percentage, fixed
    discount_value NUMERIC(10, 2) NOT NULL CHECK (discount_value > 0),
    max_uses INTEGER,
    current_uses INTEGER DEFAULT 0,
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    applicable_to VARCHAR(50), -- all, specific_tours, specific_groups
    applicable_tours TEXT, -- JSON array of tour IDs
    min_booking_amount NUMERIC(12, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_discount_dates CHECK (valid_until >= valid_from)
);

-- Таблица использования промокодов
CREATE TABLE promo_code_usage (
    id SERIAL PRIMARY KEY,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    discount_applied NUMERIC(12, 2),
    used_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(booking_id)
);

-- Таблица уведомлений о бронировании
CREATE TABLE booking_notifications (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    notification_type VARCHAR(50), -- confirmation, reminder, payment-due, cancellation
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    sent_date TIMESTAMPTZ,
    is_sent BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица рейтингов и отзывов о бронировании
CREATE TABLE booking_reviews (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL ON UPDATE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    comment TEXT,
    would_recommend BOOLEAN,
    visited_date DATE,
    review_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Таблица зарезервированных мест на экскурсиях
CREATE TABLE tour_availability (
    id SERIAL PRIMARY KEY,
    tour_type_id INTEGER NOT NULL REFERENCES tour_types(id) ON DELETE CASCADE ON UPDATE CASCADE,
    tour_date DATE NOT NULL,
    total_capacity INTEGER NOT NULL,
    available_slots INTEGER NOT NULL,
    price_per_person NUMERIC(10, 2) NOT NULL CHECK (price_per_person >= 0),
    guide_name VARCHAR(100),
    vehicle_type VARCHAR(100), -- yacht, jeep, minibus, limousine
    meeting_point VARCHAR(255),
    meeting_time TIME,
    estimated_duration INTERVAL,
    status VARCHAR(50) DEFAULT 'open', -- open, full, cancelled
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_capacity CHECK (available_slots <= total_capacity)
);

-- Таблица страны происхождения клиентов
CREATE TABLE booking_sources (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    source_country VARCHAR(100), -- страна откуда турист
    referrer_type VARCHAR(50), -- agency, direct, online, social, recommendation
    referrer_name VARCHAR(255),
    initial_contact_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
