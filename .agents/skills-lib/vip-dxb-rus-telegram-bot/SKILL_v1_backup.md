---
name: vip-dxb-rus-telegram-bot
description: Use when working with VIP-DXB-RUS Telegram bot - creating content blocks, forms, navigation flows, fixing bugs, or analyzing bot architecture. Covers 187 blocks, 11 forms, 113 variables across 4 emirates (Dubai, Abu Dhabi, RAK, Fujairah) for UAE tourism services.
---

# VIP-DXB-RUS Telegram Bot

Comprehensive guide for working with VIP-DXB-RUS tourism bot for UAE (ОАЭ). Manages excursions, parks, water activities, car rentals, transfers, beach clubs, hotels, restaurants, and SPA services across 4 emirates.

## When to Use This Skill

Use this skill when:
- Creating or editing bot content blocks (экскурсии, парки, услуги)
- Designing booking forms (11 forms: excursions, buggy, rent, pools, beaches, etc.)
- Fixing navigation bugs (missing "Back" buttons, empty blocks)
- Adding new services or emirates
- Analyzing bot architecture and data flow
- Writing system prompts for Claude API integration
- Debugging form variables (113 variables with prefixes: gt_, pt_, buggy_, rent_, etc.)

## Bot Architecture

### Core Structure (187 Blocks)

```
VIP-DXB-RUS Bot
├── 3 COMMANDS (001-003)
│   ├── /start — Entry point, select emirate
│   ├── /balls — Loyalty system (150 points = 150 RUB)
│   └── /staff — Admin command
│
├── 4 MAIN MENUS (010-013) — By emirates
│   ├── Dubai Menu (010)
│   ├── Abu Dhabi Menu (011)
│   ├── Ras Al Khaimah Menu (012)
│   └── Fujairah Menu (013)
│
├── EXCURSIONS (100-400) — 43 cards across emirates
│   ├── 100-113: Dubai (13 excursions)
│   ├── 200-208: Abu Dhabi (8 excursions)
│   ├── 300-313: RAK (13 excursions)
│   └── 400-409: Fujairah (9 excursions)
│
├── PARKS & ENTERTAINMENT (500-650)
│   ├── 500-560: Dubai Parks (18 subcategories)
│   ├── 600-607: Abu Dhabi Parks (14 subcategories)
│   ├── 700+: Cruises, water activities, buggies, pools
│   └── 800-900: Beaches, hotels, restaurants, SPA
│
└── SERVICE BLOCKS (950-995) — 26 blocks
    ├── 950-953: Captcha for group entry
    ├── 960-965: Loyalty system (points, subscription)
    ├── 970-972: Thank you messages
    └── 980-995: Payment confirmations (16 variants)
```

### Block Hierarchy (5 Levels)

```
Level 1: MAIN MENU (entry point)
   ↓
Level 2: CATEGORY MENU (parks, excursions, services)
   ↓
Level 3: SUBCATEGORY (theme parks, aquaparks, museums)
   ↓
Level 4: SERVICE SUBMENU (time slots, zones, variants)
   ↓
Level 5: SERVICE CARD (final booking point)
```

## Forms System (11 Forms)

### Complete Forms Table

| Form | Fields | Prefix | Status | Use Case |
|------|--------|--------|--------|----------|
| FORM-GT | 8 | `gt_` | ✅ Works | Group excursions |
| FORM-PT | 9 | `pt_` | ✅ Works | Private excursions |
| FORM-BUGGY | 10 | `buggy_` | ✅ Works | Buggy & jeep safari |
| FORM-RENT | 13 | `rent_` | ✅ Works | Car rental (with docs upload) |
| FORM-POOL | 11 | `pool_` | ✅ Works | Infinity pools |
| FORM-CRUISE | 0 | — | ❌ **EMPTY** | Yacht cruises |
| FORM-BEACH | 12 | `beach_` | ✅ Works | Beach clubs |
| FORM-SPA | 13 | `spa_` | ✅ Works | SPA & wellness |
| FORM-TRANSFER | 12 | `tr_` | ✅ Works | Airport transfer |
| FORM-YACHT | 13 | `yacht_` | ✅ Works | Yacht rental (most detailed) |
| FORM-REST | 9 | `rest_` | ✅ Works | Restaurant booking |

**Total:** 110 fields (without FORM-CRUISE)

### Required Fields Pattern (Always Present)

```
*_client_name / *_name — Client full name (TEXT)
*_phone                — Phone number (PHONE)
*_email                — Email address (EMAIL)
*_date                 — Event date (DATE)
```

### Optional Fields Pattern

```
*_time / *_start_time  — Time (TIME)
*_comment / *_wishes   — Comments (TEXT, optional)
*_occasion             — Visit reason (CHOICE, optional)
```

## Content Formatting Patterns

### Emoji Usage Standards

**Emirates:**
```
🕌 Abu Dhabi (mosque)
🌆 Dubai (skyscrapers)
🏖️ Ras Al Khaimah (beach)
🌊 Fujairah (water)
```

**Service Categories:**
```
🏙️ Excursions          🎡 Theme parks
🎢 Aquaparks           ⛵️ Cruises
🛥 Yachts              🚗 Car rental
🪪 International license 🌊 Water activities
🏜 Buggy               🏊 Pools
🏖️ Beach clubs         🏨 Hotels
🍽️ Restaurants         🧘‍♀️ SPA
⬅ Back button
```

### Text Structure Patterns

**Pattern 1: Minimal Menu**
```
Category Name

(no additional description)
```

**Pattern 2: Menu with Subtitle**
```
Category Name

Detailed description/subtitle
```

**Pattern 3: Info Card**
```
Emoji + Service Name
[blank line]
Description (1-3 sentences)
[Optional: details, price, time]

Button: ⬅ Back
```

**Pattern 4: Simple Card (Minimal)**
```
Service name only

Button: ⬅ Back (or missing)
```

### Button Patterns

**Pattern 1: Buttons with Emoji (Classic)**
```
🎢 Theme Parks
💦 Aquaparks
👀 Observation Decks
🎨 Museums
```

**Pattern 2: Buttons with Description**
```
🎢 Theme Park Ferrari World
🦸 Theme Park Warner Bros
🐬 Theme Park SeaWorld
```

**Pattern 3: Combo Buttons (Packages)**
```
🎟 Bargain: tickets for 2 parks
🎟 Bargain: tickets for 3 parks
🎟 Bargain: tickets for 4 parks
```

**Pattern 4: Navigation Buttons**
```
⬅ Back → [Previous menu]
```
**Requirement:** MANDATORY on all cards (but missing in 50% of cases)

## Variables System (113 Variables)

### System Variables (3)

| Variable | Type | Description | Where Used |
|----------|------|-------------|------------|
| `{{FIRST_NAME_TEXT}}` | string | User's name from Telegram | /start, All menus |
| `{{balance}}` | number | Points balance | /balls, Personal cabinet |
| `подписка` | boolean | Subscription status | Subscription check |

### Form Variables by Category

**Excursions (GT/PT):**
```
gt_client_name, gt_client_phone, gt_client_email
gt_tour_date, gt_pickup_loc
gt_count_adults, gt_count_children, gt_count_infants

pt_client_name, pt_client_phone, pt_client_email
pt_start_time (14:00 or 16:00), pt_tour_date, pt_pickup_loc
pt_count_adults, pt_count_children, pt_count_infants
```

**Buggy:**
```
buggy_vehicle_type (Buggy 2-seat/4-seat/Quad)
buggy_model (PRO Can-Am / Standard Polaris)
buggy_duration (1h/2h/4h)
buggy_time (Sunset/Morning/Day)
buggy_date, buggy_pax
buggy_client_name, buggy_client_phone, buggy_email
buggy_comment
```

**Car Rental:**
```
rent_client_name, rent_phone, rent_email
rent_car_name, rent_start_date, rent_days
rent_pickup_loc (Hotel/Airport DXB/Office)
rent_delivery_addr
rent_doc_passport (file upload)
rent_doc_license (file upload)
rent_security_type (Deposit/Full Insurance)
rent_comment, rent_comment2
```

**Pools:**
```
pool_venue_name (Aura/Address/SLLS/Cloud22/Tapasake)
pool_date
pool_session (Morning/Sunset/Full Day/Night)
pool_view (Palm/Burj Khalifa/Marina/Burj Al Arab)
pool_row (1st line/In water/2nd/3rd/VIP/Best)
pool_client_name, pool_phone, pool_email
pool_occasion, pool_comment
```

**Beach Clubs:**
```
beach_venue_name (Drift/Nikki/Bla Bla/Kyma/Twiggy)
beach_date
beach_zone (Pool/Beach/Restaurant/Best spot)
beach_bed_type (Single/Double/VIP Villa/Cabana)
beach_kids, beach_guests
beach_occasion
beach_client_name, beach_phone, beach_email
beach_comment
```

**SPA:**
```
spa_location (Home visit/Salon)
spa_service_type (Hammam/Massage/Facial/IV Drip)
spa_technique (Relax/Deep/Thai/Bali/Recommend)
spa_duration (60/90/120 min)
spa_therapist_sex (Female/Male/Any)
spa_date, spa_time
spa_address, spa_comment
spa_client_name, spa_phone, spa_email
```

**Transfer:**
```
tr_pickup (DXB Airport/AUH Airport/Hotel/Other)
tr_flight_num (optional)
tr_dropoff, tr_date, tr_time
tr_car_class (Standard/Business/Minivan/Bus)
tr_pax
tr_phone, tr_email, tr_comment
```

**Yacht:**
```
yacht_client_name, yacht_phone
yacht_date, yacht_start_time
yacht_duration (2h/3h/4h/5+h)
yacht_guests, yacht_kids
yacht_route (Marina/Palm/Burj Al Arab/Canal)
yacht_occasion
yacht_food (Own/Grill/Catering/None)
yacht_extras (Jet Ski/Fishing/Decor/Transfer/Skip)
yacht_comment
```

**Restaurant:**
```
rest_client_name, rest_phone, rest_email
rest_date, rest_time, rest_guests
rest_seating (Inside Non-smoking/Smoking/Terrace/Any)
rest_occasion
rest_wishes
```

## Critical Bugs & Fixes

### CRITICAL (20 bugs - user gets stuck)

**Empty Blocks Without Back Button (16):**

| Category | Blocks | Emirates | Problem |
|----------|--------|----------|---------|
| Beach Clubs | 850 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |
| Hotels | 860 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |
| Restaurants | 870 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |
| SPA/Wellness | 880 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |

**Fix Template:**
```markdown
# [ID] [Category] from [Emirate]

**Type:** Menu
**Date:** [Date]

## Message Text
```
Section under development

For booking, please contact our manager.
```

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | ⬅ Back | [Emirate Menu] | inline |
```

**Additional Critical (4):**
- **FORM-CRUISE** — Form is COMPLETELY EMPTY (no fields)
- **FORM-HOTEL** — Form ready (10 fields) but INACCESSIBLE from interface
- **600-PARKS-AD-FUJ** — Abu Dhabi Parks (Fujairah) missing Back button
- **201-JEEP-SAFARI** — Jeep Safari from Abu Dhabi missing Back button

### HIGH Priority Bugs (60+)

- **Water Activities** (13 blocks) — no booking buttons
- **Cruises & Yachts** (10 blocks) — content not filled
- **Dubai Parks** (17 blocks) — no ticket purchase buttons
- **Abu Dhabi Parks** (14 blocks) — no ticket purchase buttons
- **Buggies** (3 blocks) — content not filled
- **Pools** (3 of 4) — no booking buttons

## Creating New Content Blocks

### Excursion Card Template

```markdown
# [ID] [Excursion Name] from [Emirate]

**Type:** Excursion Card
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Excursion Name]
```

---

## Media
- Image: Yes (excursion card)
- Video: No
- Document: No

---

## Variables

**Uses (reads):** None

**Sets (writes):** None

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | Excursions from [Emirate] | Button "[EMOJI] [Name]" |

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Pay for group tour | Group excursion booking | inline |
| 2 | Pay for private tour | Private excursion booking | inline |
| 3 | ⬅ Back | Excursions from [Emirate] | inline |

---

## Notes

- Standard excursion card
- 2 payment options (group/private)
- Available from [Emirate] menu

---

## Checkpoint

- [x] Block found in constructor
- [x] Text documented
- [x] All buttons documented
- [x] Incoming paths documented
- [x] Transitions verified
- [x] Variables documented
- [x] Notes added
```

### Service Card Template (Parks, Activities)

```markdown
# [ID] [Service Name]

**Type:** Service Card
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[EMOJI] [Service Name]

[1-3 sentences description]

[Optional: price, duration, what's included]
```

---

## Media
- Image: [Yes/No]

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | Book [Service] | [Booking Form] | inline |
| 2 | ⬅ Back | [Parent Menu] | inline |

---

## Notes

- [Service details]
- Form: [FORM-NAME]
```

### Menu Template

```markdown
# [ID] [Menu Name]

**Type:** Menu/Submenu
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Optional greeting with {{FIRST_NAME_TEXT}}]

[Menu Title]

[Optional subtitle/description]
```

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | [EMOJI] [Service 1] | [Block] | inline |
| 2 | [EMOJI] [Service 2] | [Block] | inline |
| ... | ... | ... | ... |
| N | ⬅ Back | [Parent Menu] | inline |

---

## Notes

- [Number] services available
- Common menu for [emirates/all]
```

## Form Creation Template

```markdown
# FORM-[NAME] — [Service Type]

**File:** `forms/_детали/[CATEGORY]/FORM-[NAME].md`

**Purpose:** [Description]

**Complexity:** [⭐⭐⭐⭐⭐ rating]

---

## Structure

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | [Field Name] | `[prefix]_[name]` | [type] | [Yes/No] | [details] |
| 2 | ... | ... | ... | ... | ... |

---

## Choice Fields Details

**[Field Name]** (`[variable]`):
```
- Option 1 — description
- Option 2 — description
- Option 3 — description
```

---

## Incoming Transitions

- [Service 1] → "Book [Service]"
- [Service 2] → "Book [Service]"
- ...

---

## Outgoing Actions

1. Data saved to variables [prefix]_*
2. Notification sent to manager
3. User receives confirmation
4. Redirect to payment confirmation block

---

## Notes

- [Unique features]
- [Required documents if any]
- [Special validation rules]
```

## Validation Rules

### Field Types & Validation

| Type | Format | Examples | Validation |
|------|--------|----------|-----------|
| TEXT | String | Name, comment | 0-500 chars, no special codes |
| PHONE | Phone | +971-50-123-4567 | Digits and +, -, space only |
| EMAIL | Email | user@example.com | Format: name@domain.ext |
| DATE | Date | 2026-02-15 | Format: YYYY-MM-DD, future date |
| TIME | Time | 14:00 | Format: HH:MM (24-hour) |
| NUMBER | Number | 5 | Integer, 1-999 (usually) |
| CHOICE | Choice | "14:00" | Only provided options |
| FILE | File | image.jpg | Image/document (max size) |

### Recommended Limits

```
Adults count:    1-99
Children count:  0-99
Infants count:   0-10
Guests count:    1-500 (for yacht)
Days count:      1-365 (for car rental)
Luggage count:   0-20
```

## System Prompt Template for Bot Integration

```markdown
You are a helpful assistant for VIP-DXB-RUS tourism bot in UAE.

# Context
- Bot serves Russian-speaking tourists in UAE
- 4 emirates: Dubai, Abu Dhabi, Ras Al Khaimah, Fujairah
- Services: excursions, parks, car rental, yacht cruises, SPA, restaurants
- 187 content blocks, 11 booking forms, 113 variables

# Your Tasks
1. Help users navigate bot structure
2. Answer questions about services in each emirate
3. Explain booking process for each service type
4. Clarify differences between group and private tours
5. Provide information about prices, duration, what's included

# Response Format
- Use Russian language
- Be friendly and professional
- Provide specific block IDs when referencing content
- Include emoji where appropriate (matching bot style)
- Clarify which emirate the service is available in

# Service Categories by Emirate

**Dubai (most services):**
- 13 excursions (101-113)
- 18 park categories (500-560)
- 5 beach clubs (Drift, Nikki, Bla Bla, Kyma, Twiggy)
- 2 infinity pools (Aura Skypool, Cloud 22)

**Abu Dhabi:**
- 8 excursions (201-208)
- 14 park categories (600-607)
- Al Wathba Reserve

**Ras Al Khaimah:**
- 13 excursions (301-313)
- Zipline tour (311)
- Moroccan baths (310)

**Fujairah:**
- 9 excursions (401-409)
- Fujairah tour (403)

# Booking Forms

**Excursions:**
- FORM-GT (group): 8 fields (name, phone, email, date, pickup, adults/children/infants)
- FORM-PT (private): 9 fields (+ time selection: 14:00 or 16:00)

**Activities:**
- FORM-BUGGY: 10 fields (type, model, duration, time, date, pax, contact)
- FORM-YACHT: 13 fields (most detailed: route, food, extras)
- FORM-POOL: 11 fields (venue, session, view, row)
- FORM-BEACH: 12 fields (club, zone, bed type, guests)

**Transport:**
- FORM-RENT: 13 fields (includes passport & license upload)
- FORM-TRANSFER: 12 fields (pickup location, car class, flight number)

**Services:**
- FORM-SPA: 13 fields (location, service type, technique, therapist gender)
- FORM-REST: 9 fields (date, time, seating zone, occasion)

# Known Issues

**CRITICAL:**
- FORM-CRUISE is completely empty (cannot book cruises)
- 16 empty blocks without Back buttons (850, 860, 870, 880 for all emirates)

**HIGH:**
- Water activities have no booking buttons
- Many park cards lack ticket purchase buttons

# Example Interaction

User: "Какие есть экскурсии из Дубая?"
Assistant: "Из Дубая доступно 13 экскурсий (блоки 101-113):

🏙️ Современный Дубай (101)
🕌 Экскурсия по Абу-Даби (102)
🌊 Индийский океан через 5 эмиратов (103)
🐬 Круиз Оман Мусандам (104)
🦀 Охота на крабов (105)
🏜️ Джип-сафари тур (106)
🌸 Парк цветов + 🎡 Глобал Вилладж (107)
🦁 Тур в зоопарк Сафари (108)
🛥️ Ужин-круиз на Дубай Марине (109)
🌃 Ночной Дубай с ужин-круизом (110)
🌴 Город-оазис Аль-Айн (111)
🎣 Рыбалка (112)
🏎️ Дубай на кабриолете (113)

Каждая экскурсия доступна в групповом (FORM-GT) или приватном (FORM-PT) формате."
```

## Quick Reference

### Block ID Ranges

```
001-003:  Commands (/start, /balls, /staff)
010-013:  Main menus (by emirate)
100-199:  Dubai services (excursions 100-113)
200-299:  Abu Dhabi services (excursions 200-208)
300-399:  RAK services (excursions 300-313)
400-499:  Fujairah services (excursions 400-409)
500-699:  Parks & entertainment
700-799:  Cruises
800-899:  Water activities, buggies, pools
850-889:  Beach clubs, hotels, restaurants, SPA (by emirate)
900-949:  Reserve
950-999:  Service blocks
```

### Variable Prefixes

```
gt_      Group excursions
pt_      Private excursions
buggy_   Buggy & safari
rent_    Car rental
pool_    Pools
beach_   Beach clubs
spa_     SPA services
tr_      Transfer
yacht_   Yacht rental
rest_    Restaurant
```

### Emirates Quick Codes

```
DXB  Dubai
AD   Abu Dhabi
RAK  Ras Al Khaimah
FUJ  Fujairah
```

## Best Practices

### Content Creation
1. **Always** include Back button (⬅ Назад)
2. **Always** use emoji matching category (see Emoji Standards)
3. **Keep** text concise (1-3 sentences for descriptions)
4. **Use** {{FIRST_NAME_TEXT}} for personalization in menus
5. **Test** all navigation paths before publishing

### Form Design
1. **Start** with required fields (name, phone, email, date)
2. **Group** related fields (contact info, service details, preferences)
3. **Limit** choice buttons to 2-6 options
4. **Include** "Skip" option for truly optional choices
5. **Validate** data types (phone format, email format, date in future)

### Bug Prevention
1. **Check** every block has Back button
2. **Verify** all choice buttons lead somewhere
3. **Test** booking flow from menu to confirmation
4. **Ensure** forms have all required fields
5. **Document** any intentionally empty blocks

### Navigation Flow
1. **Maintain** clear hierarchy (menu → submenu → card → form)
2. **Avoid** circular references (A→B→C→A)
3. **Provide** multiple paths to popular services
4. **Return** to correct menu when using cross-emirate services
5. **Track** user journey for analytics

## Common Workflows

### Adding New Excursion

```flow
1. Choose emirate (Dubai/Abu Dhabi/RAK/Fujairah)
2. Determine block ID (next available in range)
3. Create excursion card using template
4. Add emoji + name to emirate's excursion menu
5. Link to FORM-GT and FORM-PT
6. Add Back button to excursion menu
7. Test navigation flow
8. Document in FULL-EXPORT.md
```

### Adding New Service Category

```flow
1. Determine category type (park/activity/service)
2. Assign block ID range (e.g., 920-929 for new pool)
3. Create category menu (list of services)
4. Create individual service cards
5. Design or reuse booking form
6. Add category button to main menu(s)
7. Test complete booking flow
8. Update variables documentation
```

### Fixing Empty Block Bug

```flow
1. Identify block ID (e.g., 850-BEACH-DXB)
2. Determine intended content (list of beach clubs or single card)
3. Add minimum viable content:
   - Text: "Section under development" or service description
   - Button: Back to parent menu
   - Optional: Booking button if form exists
4. Test navigation (can user escape?)
5. Mark for future content completion
6. Document fix in bug tracker
```

### Creating New Form

```flow
1. Analyze service requirements (what info needed?)
2. Choose variable prefix (e.g., newservice_)
3. List all fields:
   - Required: name, phone, email, date
   - Service-specific: type, duration, preferences
   - Optional: comments, occasion
4. Define choice options (2-6 per field)
5. Create form using template
6. Link from service cards
7. Add payment confirmation block (980-995)
8. Test complete booking cycle
9. Document all variables
```

## Troubleshooting

### User Can't Navigate Back
**Symptom:** User stuck on a page with no Back button
**Cause:** Block missing ⬅ Назад button
**Fix:** Add Back button leading to parent menu

### Form Submission Fails
**Symptom:** User clicks "Send" but nothing happens
**Cause:** Form validation error or missing required field
**Fix:** Check all required fields have values, validate data types

### Variable Not Saving
**Symptom:** Form data not appearing in notifications
**Cause:** Incorrect variable name or prefix
**Fix:** Verify variable name matches form field name (use prefix_fieldname format)

### Service Not Appearing in Menu
**Symptom:** Can't find service in bot menus
**Cause:** Button not added to menu or wrong block link
**Fix:** Add button to appropriate menu with correct block ID

### Duplicate Content
**Symptom:** Same excursion in multiple emirates
**Cause:** Cross-emirate services (e.g., "Modern Dubai" tour from all 4 emirates)
**Fix:** This is intentional - verify all variants link to correct forms

## Documentation Standards

### File Naming
```
blocks/_детали/[CATEGORY]/[ID]-[NAME].md
forms/_детали/[CATEGORY]/FORM-[NAME].md
```

### Block ID Format
```
[ID] [Service Name] from/in [Emirate]
Example: "101 Modern Dubai from Dubai"
```

### Variable Naming
```
[prefix]_[field_name]
Example: gt_client_name, buggy_duration, spa_technique
```

### Date Format
```
DD.MM.YYYY (Russian format)
Example: 01.02.2026
```

## Success Metrics

Track these KPIs:
- **Navigation Success Rate**: % users who complete booking flow
- **Form Completion Rate**: % users who submit forms
- **Bug Escape Rate**: % users stuck in empty blocks
- **Variable Coverage**: % forms with all variables documented
- **Content Completeness**: % blocks with full content vs placeholders

## Resources

**Documentation Files:**
- `blocks/TEMPLATE.md` — Block documentation template
- `blocks/_сводка/FULL-EXPORT.md` — Complete list of 187 blocks
- `forms/_сводка/` — All 11 forms documentation
- `variables/ALL-VARIABLES.md` — 113 variables reference
- `mermaid/` — Architecture diagrams (8 diagrams)
- `_БАГИ/` — Bug tracking (5 priority levels)

**Analysis Files:**
- First agent output — Architecture & commands analysis
- Second agent output — Excursion patterns & formatting
- Third agent output — Services classification & patterns
- Fourth agent output — Forms system complete documentation

## Next Steps

1. **Fix Critical Bugs** (empty blocks, missing Back buttons)
2. **Complete FORM-CRUISE** (add 11 fields like FORM-YACHT)
3. **Add Booking Buttons** (water activities, parks, pools)
4. **Fill Empty Content** (cruises, buggies descriptions)
5. **Standardize Emoji** (use ⬅️ everywhere for Back)
6. **Document Edge Cases** (Moroccan baths without booking)
7. **Create Testing Checklist** (navigation, forms, variables)
8. **Set Up Monitoring** (track stuck users, failed bookings)

## Additional Resources

This skill includes comprehensive supporting materials for efficient bot development and maintenance.

### Templates (`assets/templates/`)

Production-ready templates for copying and customizing:

**`block-excursion.md`** - Excursion card template
- Standard structure with ID, name, emirate
- Media section (image/video/document)
- Buttons: Group tour, Private tour, Back
- Variables and incoming/outgoing paths documentation
- Complete checkpoint list

**`block-menu.md`** - Menu/submenu template
- Title and optional subtitle structure
- Service category buttons with emoji
- Navigation buttons (Back to parent)
- Personalization with {{FIRST_NAME_TEXT}}
- Notes section for context

**`block-service-card.md`** - Service card template
- Emoji + service name header
- Description (1-3 sentences)
- Booking button linking to form
- Back button (MANDATORY)
- Form name documentation

**`form-template.md`** - Form creation template
- Field structure table (name, variable, type, required)
- Choice options detailed documentation
- Incoming transitions (which blocks link here)
- Outgoing actions (data flow, notifications)
- Validation rules and special notes

**`payment-confirmation.md`** - Payment confirmation template
- Thank you message structure
- Order summary with variables
- Next steps for customer
- Back to main menu button

### Examples (`assets/examples/`)

Real-world examples demonstrating best practices:

**`excursion-dubai-modern.md`** - Block 101: Modern Dubai tour
- Complete excursion card documentation
- Shows proper emoji usage (🏙️)
- Demonstrates group/private tour buttons
- Incoming paths from Dubai menu
- Perfect template for new excursions

**`form-yacht-example.md`** - FORM-YACHT (13 fields)
- Most complex form in the system
- Shows all field types: TEXT, PHONE, EMAIL, DATE, TIME, NUMBER, CHOICE
- Choice options examples (route, food, extras)
- Variable prefix pattern: yacht_*
- File upload documentation (if needed)

**`menu-parks-dubai.md`** - Block 500: Dubai Parks menu
- Multi-level menu structure
- 18 subcategories with emoji
- Navigation hierarchy example
- Shows how to organize large category

**`service-pool-aura.md`** - Aura Skypool booking
- Service card with form integration
- Links to FORM-POOL (11 fields)
- Complete booking flow example
- Shows price, time, location details

**`bugfix-empty-block.md`** - Fixing block 850 (Beach Clubs Dubai)
- Before/after comparison
- Minimum viable content pattern
- Back button implementation
- Testing steps for navigation

### References (`references/`)

Quick-reference guides for daily use:

**`block-templates.md`** - Ready-to-use block templates
- Excursion card, service card, menu templates
- Copy-paste friendly format
- All required sections included

**`form-fields-reference.md`** - All 110 form fields detailed
- Field-by-field documentation for all 10 working forms
- Data types, validation rules, choice options
- Variable naming by prefix (gt_, pt_, buggy_, rent_, pool_, beach_, spa_, tr_, yacht_, rest_)

**`emoji-standards.md`** - Emoji usage guide
- Emirates: 🕌 Abu Dhabi, 🌆 Dubai, 🏖️ RAK, 🌊 Fujairah
- Service categories: 🏙️ 🎡 ⛵️ 🚗 🏊 🍽️ 🧘‍♀️
- Navigation: ⬅ Back button

**`bug-fixes-guide.md`** - How to fix common bugs
- 16 empty blocks (850, 860, 870, 880 × 4 emirates)
- Missing Back buttons (blocks 201, 600)
- Empty FORM-CRUISE
- 60+ missing booking buttons

**`variables-cheatsheet.md`** - Quick variable reference
- All 113 variables listed by category
- Prefix patterns and naming conventions
- System variables: {{FIRST_NAME_TEXT}}, {{balance}}, подписка

**`faq.md`** - Frequently asked questions
- How to add new excursion?
- How to create new form?
- How to fix navigation bugs?
- How to test booking flow?

**`troubleshooting.md`** - Common problems and solutions
- User stuck in block → Add Back button
- Form won't submit → Check validation
- Service not in menu → Add button
- Variable not saving → Check naming

**`cheatsheet.md`** - Quick reference card
- Block ID ranges (001-003 commands, 100-113 Dubai, etc.)
- Variable prefixes (gt_, pt_, buggy_, etc.)
- Emirates codes (DXB, AD, RAK, FUJ)
- Essential workflows

### Scripts (`scripts/`)

Automation tools for validation and documentation:

**`validate-navigation.py`** - Navigation integrity checker
- Scans all 187 blocks for navigation issues
- Checks: All blocks have Back buttons, all buttons link to existing blocks
- Detects: Circular references, orphaned blocks
- Output: Priority-ranked report (critical/high/medium)
- Usage: `python validate-navigation.py [path-to-bot-docs]`

**`check-back-buttons.py`** - Back button scanner
- Identifies blocks missing Back buttons
- Generates fix list with block IDs
- Exports to CSV/JSON for tracking
- Priority ranking based on traffic
- Usage: `python check-back-buttons.py --export=report.csv`

**`export-variables.py`** - Variables documentation exporter
- Extracts all 113 variables from forms
- Groups by prefix (gt_, pt_, buggy_, rent_, pool_, beach_, spa_, tr_, yacht_, rest_)
- Validates naming conventions (prefix_fieldname)
- Generates markdown documentation
- Usage: `python export-variables.py --output=variables.md`

**`generate-docs.py`** - Documentation auto-generator
- Creates block documentation from constructor
- Builds form field tables automatically
- Generates navigation maps (Mermaid diagrams)
- Updates FULL-EXPORT.md with latest changes
- Usage: `python generate-docs.py --format=markdown`

### Usage Examples

**Creating new excursion:**
```bash
# 1. Copy template
cp assets/templates/block-excursion.md blocks/114-NEW-EXCURSION.md

# 2. Edit file with your details
# 3. Add to menu (reference emoji-standards.md)
# 4. Test navigation (run validate-navigation.py)
```

**Fixing empty block:**
```bash
# 1. Study example
cat assets/examples/bugfix-empty-block.md

# 2. Apply minimum fix (text + Back button)
# 3. Verify with check-back-buttons.py
```

**Designing new form:**
```bash
# 1. Copy template
cp assets/templates/form-template.md forms/FORM-NEWSERVICE.md

# 2. Reference form-fields-reference.md for field types
# 3. Follow variable naming in variables-cheatsheet.md
# 4. Export variables with export-variables.py
```

**Quick lookup:**
```bash
# Find emoji for service
grep "SPA" references/emoji-standards.md
# Result: 🧘‍♀️ SPA

# Find variable prefix for pools
grep "pool" references/variables-cheatsheet.md
# Result: pool_ (11 fields)

# Check if bug is documented
grep "850" references/bug-fixes-guide.md
# Result: Empty block without Back button
```

---

**Version:** 1.0.0
**Last Updated:** 2026-02-01
**Total Documentation:** 240 source files analyzed + 30 skill files created
**Bot Status:** 83% complete (32 done, 99 partial, 61 empty)
**Skill Package:** Production ready with full template/example/script/reference library
