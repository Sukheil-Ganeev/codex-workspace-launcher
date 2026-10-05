# ERD: Booking System — VIP-DXB-RUS Tourism Website

**Mode:** `diagram` (type: `erDiagram`)
**Date:** 2026-03-14
**Project:** vipdxbrus.com — booking system for tourism services

---

## Context

The tourism website needs a booking database layer to move from WhatsApp-only bookings to calendar-based availability. Five core tables cover the full lifecycle: a **services** catalog, **availability_slots** per date, **users** who browse and book, **bookings** that link users to slots, and **user_favorites** for wishlists.

---

## ERD Diagram

```mermaid
erDiagram
    services {
        bigserial id PK
        varchar slug UK "URL-friendly identifier"
        varchar title_ru "Service name (Russian)"
        varchar title_en "Service name (English)"
        varchar category "excursions | tickets | yachts | transfers | etc"
        varchar city "dubai | abu-dhabi | sharjah"
        numeric price "Base price in AED"
        numeric old_price "Strike-through price in AED"
        varchar currency "AED by default"
        text description_ru
        text description_en
        varchar image_url "R2 CDN thumbnail URL"
        boolean is_active "Published on site"
        int sort_order "Display ordering"
        timestamptz created_at
        timestamptz updated_at
    }

    availability_slots {
        bigserial id PK
        bigint service_id FK "References services.id"
        date slot_date "Available date"
        time slot_time "Start time (nullable for full-day)"
        int capacity "Max participants per slot"
        int booked_count "Currently booked"
        numeric price_override "Slot-specific price (nullable)"
        varchar status "open | full | closed"
        timestamptz created_at
        timestamptz updated_at
    }

    users {
        bigserial id PK
        varchar phone UK "WhatsApp / contact phone"
        varchar name "Client display name"
        varchar email "Optional email"
        varchar language "ru | en"
        varchar source "website | whatsapp | telegram | agent"
        varchar wa_chat_id "WhatsApp chat identifier (nullable)"
        timestamptz created_at
        timestamptz last_active
    }

    bookings {
        bigserial id PK
        bigint user_id FK "References users.id"
        bigint slot_id FK "References availability_slots.id"
        bigint service_id FK "References services.id (denormalized for speed)"
        date tour_date "Booked date"
        int adults "Number of adults"
        int children "Number of children"
        numeric total_price "Final price in AED"
        varchar currency "AED"
        varchar status "pending | confirmed | cancelled | completed | refunded"
        varchar payment_method "cash_aed | cash_usd | transfer_rub | transfer_kzt | crypto"
        text comment "Client notes (optional)"
        varchar promo_code "Applied promo code (nullable)"
        timestamptz created_at
        timestamptz updated_at
    }

    user_favorites {
        bigserial id PK
        bigint user_id FK "References users.id"
        bigint service_id FK "References services.id"
        timestamptz created_at
    }

    services ||--o{ availability_slots : "has available dates"
    services ||--o{ bookings : "is booked via"
    services ||--o{ user_favorites : "is favorited by"
    users ||--o{ bookings : "makes"
    users ||--o{ user_favorites : "saves"
    availability_slots ||--o{ bookings : "is reserved in"
```

---

## Relationship Summary

| From | To | Cardinality | Meaning |
|------|----|-------------|---------|
| `services` | `availability_slots` | one-to-many | Each service has zero or more date/time slots |
| `services` | `bookings` | one-to-many | Each service can have many bookings (denormalized FK for fast queries) |
| `services` | `user_favorites` | one-to-many | Each service can be favorited by many users |
| `users` | `bookings` | one-to-many | Each user can make many bookings |
| `users` | `user_favorites` | one-to-many | Each user can favorite many services |
| `availability_slots` | `bookings` | one-to-many | Each slot can have multiple bookings (up to capacity) |

## Key Indexes (recommended)

```sql
-- availability_slots: fast lookup by service + date
CREATE INDEX idx_slots_service_date ON availability_slots(service_id, slot_date);

-- bookings: user history
CREATE INDEX idx_bookings_user ON bookings(user_id);

-- bookings: status filtering
CREATE INDEX idx_bookings_status ON bookings(status);

-- user_favorites: unique pair (no duplicate favorites)
CREATE UNIQUE INDEX idx_favorites_unique ON user_favorites(user_id, service_id);

-- users: phone lookup
CREATE UNIQUE INDEX idx_users_phone ON users(phone);

-- services: category + city filtering
CREATE INDEX idx_services_category_city ON services(category, city);
```

## Design Decisions

1. **`bookings.service_id` is denormalized** — duplicated from `availability_slots.service_id` to avoid an extra JOIN on the most common query (user booking history). Kept in sync at application level.
2. **`availability_slots.booked_count`** — counter cache avoids `COUNT(*)` on bookings per slot. Updated via transaction when booking is created/cancelled.
3. **`user_favorites`** uses a junction table (not JSONB array) for proper indexing and referential integrity.
4. **`users.source`** tracks acquisition channel — critical for marketing analytics (WhatsApp vs website vs Telegram).
5. **Prices stored as `numeric`** (not float) to avoid rounding errors with AED amounts.
