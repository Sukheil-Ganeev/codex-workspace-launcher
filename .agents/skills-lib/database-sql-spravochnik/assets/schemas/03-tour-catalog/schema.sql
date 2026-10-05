-- 03-Tour Catalog Schema
-- Каталог всех туров и услуг с описанием, изображениями, ценами и маршрутами

CREATE TABLE tour_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) UNIQUE,
    description TEXT,
    icon_url VARCHAR(500),
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tours (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    category_id INTEGER NOT NULL REFERENCES tour_categories(id) ON DELETE CASCADE ON UPDATE CASCADE,
    description TEXT NOT NULL,
    long_description TEXT,
    duration_hours DECIMAL(5,2),
    duration_days INTEGER,
    difficulty_level VARCHAR(20), -- easy, moderate, hard, extreme
    min_participants INTEGER DEFAULT 1,
    max_participants INTEGER DEFAULT 50,
    price_per_person NUMERIC(10,2) NOT NULL CHECK (price_per_person > 0),
    currency VARCHAR(3) DEFAULT 'AED',
    included_items TEXT[], -- array of included services
    not_included_items TEXT[],
    languages VARCHAR(100)[], -- array: English, Russian, Arabic
    meeting_point VARCHAR(255),
    meeting_time TIME,
    return_time TIME,
    highlights TEXT[],
    age_restrictions VARCHAR(100),
    special_requirements VARCHAR(255),
    cancellation_policy TEXT,
    refund_policy VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_images (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    caption VARCHAR(255),
    display_order INTEGER,
    is_featured BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_routes (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    stop_order INTEGER NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    description TEXT,
    duration_minutes INTEGER,
    stop_type VARCHAR(50), -- pickup, activity, meal, photo, rest
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_schedules (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday, 6=Saturday
    available_date DATE,
    is_available BOOLEAN DEFAULT TRUE,
    guide_id VARCHAR(100),
    max_capacity INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_pricing (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    price_type VARCHAR(50), -- per_person, group_fixed, seasonal
    min_quantity INTEGER,
    max_quantity INTEGER,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    season VARCHAR(50), -- high, low, peak
    valid_from DATE,
    valid_until DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_reviews (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL ON UPDATE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    comment TEXT,
    date_visited DATE,
    is_verified BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_faqs (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    question VARCHAR(500) NOT NULL,
    answer TEXT NOT NULL,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_guides (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    languages VARCHAR(100)[],
    license_number VARCHAR(50) UNIQUE,
    license_expiry DATE,
    experience_years INTEGER,
    rating NUMERIC(3,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_vehicles (
    id SERIAL PRIMARY KEY,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    vehicle_type VARCHAR(100), -- yacht, jeep, minibus, limousine, helicopter
    model VARCHAR(100),
    year INTEGER,
    capacity INTEGER NOT NULL,
    fuel_type VARCHAR(50),
    license_expiry DATE,
    insurance_expiry DATE,
    last_maintenance DATE,
    next_maintenance_due DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_inclusions (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    inclusion_type VARCHAR(50), -- transportation, meal, activity, guide, equipment
    description VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_type VARCHAR(50), -- per_person, fixed, days
    display_order INTEGER
);

CREATE TABLE tour_exclusions (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    description VARCHAR(255) NOT NULL,
    display_order INTEGER
);

CREATE TABLE tour_recommendations (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    recommended_season VARCHAR(50),
    recommended_duration VARCHAR(100),
    recommended_group_size VARCHAR(100),
    best_time_to_visit TEXT,
    tips_and_recommendations TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tour_tag_assignments (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE ON UPDATE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tour_tags(id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(tour_id, tag_id)
);
