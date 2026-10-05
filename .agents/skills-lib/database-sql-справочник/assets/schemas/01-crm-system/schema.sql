-- 01-CRM System Schema
-- Управление клиентами, контактами, компаниями и историей взаимодействия
-- Production-ready PostgreSQL

-- Таблица компаний
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(100),
    website VARCHAR(255),
    country VARCHAR(100),
    city VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(255) UNIQUE,
    annual_revenue NUMERIC(15, 2),
    employees_count INTEGER,
    tax_id VARCHAR(50) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица контактов (физических лиц)
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL ON UPDATE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    mobile VARCHAR(50),
    position VARCHAR(100),
    department VARCHAR(100),
    birth_date DATE,
    country VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    postal_code VARCHAR(20),
    language VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Таблица источников контактов
CREATE TABLE contact_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- website, referral, event, social, advertising, cold-call
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица истории контактов
CREATE TABLE contact_history (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    source_id INTEGER REFERENCES contact_sources(id) ON DELETE SET NULL ON UPDATE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- call, email, meeting, message, visit
    notes TEXT,
    duration_minutes INTEGER,
    next_follow_up DATE,
    status VARCHAR(50), -- completed, pending, cancelled
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_duration CHECK (duration_minutes >= 0)
);

-- Таблица сегментов клиентов
CREATE TABLE customer_segments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица классификации контактов
CREATE TABLE contact_classifications (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    segment_id INTEGER NOT NULL REFERENCES customer_segments(id) ON DELETE CASCADE ON UPDATE CASCADE,
    priority VARCHAR(20), -- hot, warm, cold, vip
    lifetime_value NUMERIC(15, 2),
    classification_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contact_id, segment_id)
);

-- Таблица задач и напоминаний
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20), -- low, medium, high, critical
    status VARCHAR(50), -- open, in-progress, completed, cancelled
    due_date DATE NOT NULL,
    assigned_to VARCHAR(100),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица документов и приложений
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(100), -- contract, invoice, proposal, agreement
    file_path VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    document_date DATE,
    expiration_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица тегов для контактов
CREATE TABLE contact_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(20),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Связующая таблица контактов и тегов
CREATE TABLE contact_tag_assignments (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES contact_tags(id) ON DELETE CASCADE ON UPDATE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contact_id, tag_id)
);

-- Таблица коммуникационных предпочтений
CREATE TABLE communication_preferences (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL UNIQUE REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    prefers_email BOOLEAN DEFAULT TRUE,
    prefers_phone BOOLEAN DEFAULT TRUE,
    prefers_sms BOOLEAN DEFAULT FALSE,
    prefers_whatsapp BOOLEAN DEFAULT FALSE,
    do_not_call BOOLEAN DEFAULT FALSE,
    do_not_email BOOLEAN DEFAULT FALSE,
    do_not_sms BOOLEAN DEFAULT FALSE,
    preferred_contact_time VARCHAR(50),
    timezone VARCHAR(50),
    language_preference VARCHAR(50),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица добавления контактов в списки рассылок
CREATE TABLE mailing_lists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    purpose VARCHAR(100), -- marketing, newsletter, announcements
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Связующая таблица контактов и списков рассылок
CREATE TABLE mailing_list_subscriptions (
    id SERIAL PRIMARY KEY,
    mailing_list_id INTEGER NOT NULL REFERENCES mailing_lists(id) ON DELETE CASCADE ON UPDATE CASCADE,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    subscribed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(mailing_list_id, contact_id)
);
