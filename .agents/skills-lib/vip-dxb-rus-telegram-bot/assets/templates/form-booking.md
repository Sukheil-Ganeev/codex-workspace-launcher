# FORM-[NAME] — [Тип услуги]

**File:** `forms/_детали/[CATEGORY]/FORM-[NAME].md`

**Purpose:** [Описание назначения формы]

**Complexity:** [⭐⭐⭐⭐⭐ рейтинг 1-5 звёзд]

---

## Structure

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | [Название поля] | `[prefix]_[field_name]` | [TEXT/PHONE/EMAIL/DATE/TIME/NUMBER/CHOICE/FILE] | [Yes/No] | [Детали] |
| 2 | [Название поля] | `[prefix]_[field_name]` | [Type] | [Yes/No] | [Детали] |
| 3 | [Название поля] | `[prefix]_[field_name]` | [Type] | [Yes/No] | [Детали] |
| ... | ... | ... | ... | ... | ... |

**Total fields:** [X]

---

## Required Fields (Always Present)

| Field | Variable | Type | Validation |
|-------|----------|------|------------|
| Full Name | `[prefix]_client_name` / `[prefix]_name` | TEXT | 1-100 chars, no special codes |
| Phone | `[prefix]_phone` | PHONE | Format: +971-XX-XXX-XXXX |
| Email | `[prefix]_email` | EMAIL | Format: name@domain.ext |
| Date | `[prefix]_date` | DATE | Format: YYYY-MM-DD, future date |

---

## Choice Fields Details

**[Название поля]** (`[prefix]_[variable]`):
```
- Option 1 — [описание]
- Option 2 — [описание]
- Option 3 — [описание]
- Skip — [если опционально]
```

**[Название поля 2]** (`[prefix]_[variable2]`):
```
- Option A — [описание]
- Option B — [описание]
- Option C — [описание]
```

---

## File Upload Fields (если есть)

| Field | Variable | Accepted Formats | Max Size | Required |
|-------|----------|------------------|----------|----------|
| [Документ 1] | `[prefix]_doc_[name]` | JPG, PNG, PDF | 10 MB | Yes |
| [Документ 2] | `[prefix]_doc_[name2]` | JPG, PNG, PDF | 10 MB | Yes |

---

## Incoming Transitions

Форма вызывается из следующих блоков:

| # | Block ID | Block Name | Button Text |
|---|----------|------------|-------------|
| 1 | [ID] | [Название услуги] | Забронировать [Услугу] |
| 2 | [ID] | [Название услуги 2] | Забронировать [Услугу] |
| ... | ... | ... | ... |

---

## Outgoing Actions

1. **Data saved** to variables `[prefix]_*`
2. **Notification sent** to manager (Telegram/Email)
3. **User receives** confirmation message
4. **Redirect** to payment confirmation block ([ID блока из диапазона 980-995])

---

## Notes

- [Уникальные особенности формы]
- [Обязательные документы, если есть]
- [Специальные правила валидации]
- [Связь с другими формами]

---

## Validation Rules

### Field Types & Limits

| Type | Format | Validation | Examples |
|------|--------|------------|----------|
| TEXT | String | 0-500 chars | Name, comment, address |
| PHONE | Phone | Digits, +, -, space | +971-50-123-4567 |
| EMAIL | Email | name@domain.ext | user@example.com |
| DATE | Date | YYYY-MM-DD, future | 2026-02-15 |
| TIME | Time | HH:MM (24-hour) | 14:00 |
| NUMBER | Integer | 1-999 | 5 |
| CHOICE | Choice | Only options | "14:00" |
| FILE | File | Image/PDF, max size | document.jpg |

### Recommended Limits

```
Adults count:    1-99
Children count:  0-99
Infants count:   0-10
Guests count:    1-500 (for yacht)
Duration hours:  1-24
Days count:      1-365 (for car rental)
```

---

## Template Variables by Service Type

### Excursions (GT/PT prefix):
```
gt_client_name, gt_client_phone, gt_client_email
gt_tour_date, gt_pickup_loc
gt_count_adults, gt_count_children, gt_count_infants

pt_client_name, pt_client_phone, pt_client_email
pt_start_time (14:00 or 16:00), pt_tour_date, pt_pickup_loc
pt_count_adults, pt_count_children, pt_count_infants
```

### Buggy (buggy_ prefix):
```
buggy_vehicle_type, buggy_model, buggy_duration
buggy_time, buggy_date, buggy_pax
buggy_client_name, buggy_client_phone, buggy_email
buggy_comment
```

### Car Rental (rent_ prefix):
```
rent_client_name, rent_phone, rent_email
rent_car_name, rent_start_date, rent_days
rent_pickup_loc, rent_delivery_addr
rent_doc_passport (FILE), rent_doc_license (FILE)
rent_security_type, rent_comment
```

### Pools (pool_ prefix):
```
pool_venue_name, pool_date, pool_session
pool_view, pool_row
pool_client_name, pool_phone, pool_email
pool_occasion, pool_comment
```

### Beach Clubs (beach_ prefix):
```
beach_venue_name, beach_date
beach_zone, beach_bed_type
beach_kids, beach_guests, beach_occasion
beach_client_name, beach_phone, beach_email
beach_comment
```

### SPA (spa_ prefix):
```
spa_location, spa_service_type, spa_technique
spa_duration, spa_therapist_sex
spa_date, spa_time, spa_address
spa_client_name, spa_phone, spa_email
spa_comment
```

### Transfer (tr_ prefix):
```
tr_pickup, tr_flight_num, tr_dropoff
tr_date, tr_time, tr_car_class, tr_pax
tr_phone, tr_email, tr_comment
```

### Yacht (yacht_ prefix):
```
yacht_client_name, yacht_phone
yacht_date, yacht_start_time, yacht_duration
yacht_guests, yacht_kids
yacht_route, yacht_occasion
yacht_food, yacht_extras
yacht_comment
```

### Restaurant (rest_ prefix):
```
rest_client_name, rest_phone, rest_email
rest_date, rest_time, rest_guests
rest_seating, rest_occasion
rest_wishes
```

---

## Checkpoint

- [ ] Все поля задокументированы
- [ ] Переменные с правильным префиксом
- [ ] Required поля отмечены
- [ ] Choice опции расписаны
- [ ] Валидация определена
- [ ] Входящие переходы указаны
- [ ] Исходящие действия описаны
- [ ] Связь с блоками подтверждения
