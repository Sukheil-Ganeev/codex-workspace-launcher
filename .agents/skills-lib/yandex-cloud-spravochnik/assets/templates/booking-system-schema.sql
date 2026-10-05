-- Booking System Schema для туристического бизнеса ОАЭ
-- PostgreSQL 15+
-- Yandex Cloud Managed PostgreSQL

-- Туры
CREATE TABLE tours (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    name_ar VARCHAR(255),
    description TEXT,
    description_en TEXT,
    description_ar TEXT,
    price_aed DECIMAL(10,2) NOT NULL,
    price_usd DECIMAL(10,2),
    duration_hours INTEGER,
    max_capacity INTEGER,
    category VARCHAR(50), -- desert-safari, city-tour, water-activities, etc.
    location VARCHAR(255),
    active BOOLEAN DEFAULT true,
    featured BOOLEAN DEFAULT false,
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tours_active ON tours(active);
CREATE INDEX idx_tours_category ON tours(category);
CREATE INDEX idx_tours_featured ON tours(featured);

-- Бронирования
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER REFERENCES tours(id),
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    customer_country VARCHAR(50),
    booking_date DATE NOT NULL,
    booking_time TIME,
    participants INTEGER DEFAULT 1,
    adults INTEGER,
    children INTEGER,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, cancelled, completed
    payment_method VARCHAR(50), -- cash, card, transfer, crypto
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid, partial, paid, refunded
    notes TEXT,
    source VARCHAR(50), -- website, whatsapp, telegram, phone
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_tour_id ON bookings(tour_id);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_customer_email ON bookings(customer_email);

-- Платежи
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, refunded
    paid_at TIMESTAMP,
    refunded_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_booking_id ON payments(booking_id);
CREATE INDEX idx_payments_status ON payments(status);

-- Клиенты (CRM)
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    country VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en', -- en, ru, ar
    total_bookings INTEGER DEFAULT 0,
    total_spent_aed DECIMAL(10,2) DEFAULT 0,
    first_booking_date DATE,
    last_booking_date DATE,
    vip BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_vip ON customers(vip);

-- Availability (доступность туров по датам)
CREATE TABLE tour_availability (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER REFERENCES tours(id),
    date DATE NOT NULL,
    available_slots INTEGER NOT NULL,
    booked_slots INTEGER DEFAULT 0,
    price_override DECIMAL(10,2), -- Специальная цена для этой даты
    active BOOLEAN DEFAULT true,
    UNIQUE(tour_id, date)
);

CREATE INDEX idx_availability_tour_date ON tour_availability(tour_id, date);

-- Reviews (отзывы)
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    customer_name VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_booking_id ON reviews(booking_id);
CREATE INDEX idx_reviews_approved ON reviews(approved);

-- Views для аналитики

-- Статистика по турам
CREATE VIEW tour_stats AS
SELECT
    t.id,
    t.name,
    COUNT(b.id) as total_bookings,
    SUM(b.participants) as total_participants,
    SUM(CASE WHEN b.currency = 'AED' THEN b.total_amount ELSE b.total_amount * 3.67 END) as total_revenue_aed,
    AVG(CASE WHEN r.rating IS NOT NULL THEN r.rating END) as avg_rating,
    COUNT(r.id) as review_count
FROM tours t
LEFT JOIN bookings b ON t.id = b.tour_id
LEFT JOIN reviews r ON b.id = r.booking_id
GROUP BY t.id, t.name;

-- Ежедневная статистика
CREATE VIEW daily_stats AS
SELECT
    booking_date,
    COUNT(*) as total_bookings,
    SUM(participants) as total_participants,
    SUM(CASE WHEN currency = 'AED' THEN total_amount ELSE total_amount * 3.67 END) as total_revenue_aed,
    COUNT(DISTINCT customer_email) as unique_customers
FROM bookings
WHERE status != 'cancelled'
GROUP BY booking_date
ORDER BY booking_date DESC;

-- Triggers для автоматического обновления

-- Обновить updated_at при изменении
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tours_updated_at BEFORE UPDATE ON tours
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Sample data
INSERT INTO tours (name, name_en, name_ar, description, price_aed, price_usd, duration_hours, max_capacity, category, location) VALUES
('Desert Safari Dubai', 'Desert Safari Dubai', 'سفاري صحراوية دبي', 'Exciting desert adventure with dune bashing, camel ride, and BBQ dinner', 250.00, 68.00, 6, 50, 'desert-safari', 'Dubai Desert'),
('Dubai City Tour', 'Dubai City Tour', 'جولة في مدينة دبي', 'Explore iconic landmarks: Burj Khalifa, Dubai Mall, Gold Souk', 150.00, 41.00, 4, 30, 'city-tour', 'Dubai'),
('Burj Khalifa At The Top', 'Burj Khalifa At The Top', 'برج خليفة في القمة', 'Visit the observation deck of the tallest building in the world', 180.00, 49.00, 2, 100, 'attraction', 'Downtown Dubai'),
('Abu Dhabi City Tour', 'Abu Dhabi City Tour', 'جولة في مدينة أبوظبي', 'Visit Sheikh Zayed Mosque, Emirates Palace, Louvre Abu Dhabi', 200.00, 54.00, 8, 40, 'city-tour', 'Abu Dhabi');
