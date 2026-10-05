# Booking System ERD

```mermaid
erDiagram
    users {
        int id PK
        string name
        string email UK
        string phone
        string password_hash
        enum role "tourist | agent | admin"
        string preferred_language "ru | en"
        timestamp created_at
        timestamp updated_at
    }

    services {
        int id PK
        string slug UK
        string title_ru
        string title_en
        string description_ru
        string description_en
        enum category "excursions | tickets | restaurants | hotels | pools | beach-clubs | car-rentals | services | yachts | desert-safari | water-sports | vip | combos"
        string city "dubai | abu-dhabi | sharjah"
        decimal price
        decimal old_price "strikethrough price for display"
        string currency "AED"
        int duration_minutes
        string image_url
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    availability_slots {
        int id PK
        int service_id FK
        date slot_date
        time start_time
        time end_time
        int total_capacity
        int booked_count
        decimal price_override "nullable, overrides service price"
        boolean is_available
        timestamp created_at
        timestamp updated_at
    }

    bookings {
        int id PK
        int user_id FK
        int service_id FK
        int slot_id FK "nullable, for time-slotted services"
        string booking_ref UK "e.g. VDR-20260314-A1B2"
        date booking_date
        int guests_adults
        int guests_children
        decimal total_price
        string currency "AED | USD | RUB | KZT"
        enum status "pending | confirmed | paid | completed | cancelled | refunded"
        enum payment_method "cash_aed | cash_usd | transfer_aed | transfer_kzt | transfer_rub | crypto"
        string promo_code "nullable, e.g. WELCOME"
        decimal discount_amount
        text customer_notes
        text admin_notes
        string whatsapp_thread_id "link to WA conversation"
        timestamp confirmed_at
        timestamp cancelled_at
        timestamp created_at
        timestamp updated_at
    }

    user_favorites {
        int id PK
        int user_id FK
        int service_id FK
        timestamp created_at
    }

    users ||--o{ bookings : "places"
    users ||--o{ user_favorites : "saves"
    services ||--o{ availability_slots : "has"
    services ||--o{ bookings : "is booked in"
    services ||--o{ user_favorites : "is favorited in"
    availability_slots |o--o{ bookings : "reserves"
```

## Table Descriptions

| Table | Purpose |
|-------|---------|
| **users** | Registered users: tourists, agents, admins. Role determines access level. |
| **services** | Catalog of tourism products (236 items across 13 categories). Maps to existing `src/data/` files. |
| **availability_slots** | Date/time slots with capacity tracking per service. Enables Calendar Phase B (real slots from DB). |
| **bookings** | Customer reservations with full lifecycle tracking (pending through completed/cancelled). |
| **user_favorites** | Wishlist / saved services. Currently stored in localStorage; this table enables server-side persistence. |

## Relationships & Cardinality

| Relationship | Cardinality | Meaning |
|-------------|-------------|---------|
| users -> bookings | one-to-many | A user can have many bookings; each booking belongs to one user |
| users -> user_favorites | one-to-many | A user can favorite many services |
| services -> availability_slots | one-to-many | A service can have many date/time slots |
| services -> bookings | one-to-many | A service can appear in many bookings |
| services -> user_favorites | one-to-many | A service can be favorited by many users |
| availability_slots -> bookings | zero/one-to-many | A slot can be referenced by many bookings; bookings for date-only services may have no slot |

## Design Notes

- **booking_ref** uses format `VDR-YYYYMMDD-XXXX` for human-readable WhatsApp communication
- **price_override** on slots allows dynamic pricing (weekends, holidays, peak season)
- **slot_id** is nullable because some services (e.g., car rentals) book by date only, not time slot
- **whatsapp_thread_id** links booking to the WhatsApp conversation for context
- **promo_code / discount_amount** supports the existing WELCOME 5% promo and future codes
- **user_favorites** has a unique constraint on (user_id, service_id) to prevent duplicates
- Payment methods match the business reality: AED/USD cash, AED/KZT/RUB transfers, crypto
