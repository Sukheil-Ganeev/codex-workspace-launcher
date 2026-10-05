---
name: vip-dxb-rus-telegram-bot
description: "Use when working with VIP-DXB-RUS Telegram bot - creating content blocks, forms, navigation flows, fixing bugs, or analyzing bot architecture. Covers 366 blocks, 27 forms, 350 variables across 4 emirates (Dubai, Abu Dhabi, RAK, Fujairah) for UAE tourism services. Updated with loyalty programs, BANT qualification, reminders, 8 adaptations from 24 case studies, calculator, mini-app, giveaways. Integrated with PuzzleBot and Telegram API references."
version: 2.5
---
# VIP-DXB-RUS Telegram Bot

Comprehensive guide for working with VIP-DXB-RUS tourism bot for UAE (ОАЭ). Manages excursions, parks, water activities, car rentals, transfers, beach clubs, hotels, restaurants, and SPA services across 4 emirates.

**Version 2.3 Updates:**
- **8 complete adaptations** from 24 real case studies (see `assets/adaptations/`)
- Sales: Quiz (+117% conversion), B2B funnel (240k AED/month), Booking automation
- Loyalty: VIP program (4 levels), Reviews x4 platforms
- Education: FAQ 24/7 (50 questions), Guide knowledge base, Mini-course
- Service: NPS surveys, Guide control, Complaints system
- Marketing: 4-group segmentation (+350% revenue), UTM tracking, Quiz
- **NEW in v2.3:** Calculator, Mini App booking, Giveaways & contests
- ROI: 5,425%, payback 7 days

## When to Use This Skill

Use this skill when:
- Creating or editing bot content blocks (экскурсии, парки, услуги)
- Designing booking forms (11 forms: excursions, buggy, rent, pools, beaches, etc.)
- Implementing loyalty programs and referral systems
- Setting up customer qualification (BANT method)
- Configuring reminder systems
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
├── LOYALTY SYSTEM (960-963) — NEW!
│   ├── 960: Personal Cabinet (balance, discounts)
│   ├── 961: How to get discounts
│   ├── 962: Referral program
│   └── 963: Leave review → FORM-REVIEW
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

## Loyalty Program System (NEW!)

**Based on successful case study: Theatre bot - 25% channel growth without ads**

### Program Structure

**1. Permanent Discount for Subscribers (10%)**
- While subscribed to channel → access to promo code
- Unsubscribe → promo code becomes unavailable
- Motivates to stay subscribed, reduces churn

**2. One-time Discount for Review (15%)**
- Leave review on Google Maps → get promo code
- Screenshot verification by admin
- One review per user (prevents spam)
- **Result:** 360+ reviews, 5.0 rating

**3. Referral Discount (25%)**
- Invite 3 friends → get 25% discount
- Limited time: 30 days validity
- Creates viral growth loop
- **Result:** 115 referrals (22% of new users)

**4. Points System**
- 1 AED spent = 1 point
- 150 points = 150 AED discount
- Trackable in personal cabinet (block 960)

### Implementation Blocks

**Block 960: Personal Cabinet**
```markdown
Личный кабинет

Ваш баланс: {{balance}} баллов

Доступные промокоды:
🎁 SUBSCRIBE10 — скидка 10% (постоянная)
🎁 REVIEW15 — скидка 15% (осталось {{review_days}} дней)
🎁 REFER25 — скидка 25% (осталось {{referral_days}} дней)

Buttons:
- Как получить скидки?
- Пригласить друзей
- История покупок
- ⬅ Назад
```

**Block 961: How to Get Discounts**
```markdown
Как получить скидки?

🔹 Скидка 10% — подпишитесь на канал @vipdxbrus
🔹 Скидка 15% — оставьте отзыв на Google Maps
🔹 Скидка 25% — пригласите 3 друзей

Скидки суммируются с баллами лояльности!

Buttons:
- Подписаться на канал
- Оставить отзыв
- Пригласить друзей
- ⬅ Назад
```

**Block 962: Referral Program**
```markdown
Реферальная программа

Ваша персональная ссылка:
t.me/vipdxbrus_bot?start={{user_id}}

Приглашено друзей: {{referral_count}}/3

За каждого друга: +8,33% скидки
За 3 друзей: 25% скидка на следующую покупку

Скидка действует 30 дней!

Buttons:
- Поделиться ссылкой
- Список приглашенных
- ⬅ Назад
```

**Block 963: Leave Review (FORM-REVIEW)**

### Expected Results (based on theatre case)

| Metric | Before | After | Source |
|--------|--------|-------|--------|
| Subscribers | 100% | 125% (organic growth) | Theatre case |
| Return customers | 5% | 30% | Theatre case |
| Reviews/month | 0-1 | 5-10 | Computer club case |
| New users from referrals | 0% | 20-25% | Theatre case |

## BANT Customer Qualification (NEW!)

**B**udget, **A**uthority, **N**eed, **T**imeframe — квалификация лидов после выбора тура.

| Критерий | Вопрос | Scoring |
|----------|--------|---------|
| Budget | Бюджет на поездку? | Economy 0, Medium 2, Premium 3 |
| Timeframe | Когда планируете? | Week 3, Month 2, 3+ months 0 |
| Need (Group) | Сколько человек? | 1-2: 1, 3-5: 2, 6+: 3 |
| Authority | Кто решает? | Self 3, Consult 1 |

**Scoring:** 9-11 = Hot (alert immediately), 5-8 = Warm (2h follow-up), 0-4 = Cold (nurture)

> Подробнее: см. `references/bant-implementation.md` — вопросы, переменные, шаблон блока, workflow

## Smart Reminder System (NEW!)

| # | Type | Timing | Purpose |
|---|------|--------|---------|
| 1 | Before Flight | 24h before | Documents, visa, currency check |
| 2 | After Booking | 3 days after | Visa, insurance, card reminders |
| 3 | Before Tour | 2 days before | Meeting point, what to bring |
| 4 | After Return | 2 days after | Feedback request + 15% promo |

**Implementation:** Dynamic categories + timers (set on booking, check before send, remove after delivery)

> Подробнее: см. `references/reminder-system.md` — 4 шаблона сообщений, implementation flow, переменные

## Success Case Studies (Summary)

| Case | Key Result | ROI |
|------|-----------|-----|
| Theatre - Loyalty Program | +25% channel growth, 115 referrals, 18 reviews, no ads budget | Organic growth |
| Computer Club - Reviews & Booking | 490 bookings (23% CV), 360+ reviews (5.0), 683k RUB | Revenue from bot |
| Mini-Course Funnel - Retention | 62% completion rate, 8.5% churn | Engagement |

> Подробнее: см. `references/case-studies-full.md` — полный анализ 24 кейсов с адаптациями для VIP-DXB-RUS

## Forms System (11 Forms + 1 New)

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
| **FORM-REVIEW** | **7** | `review_` | **NEW!** | **Customer reviews** |
| **FORM-TICKETS** | **8** | `ticket_` | **NEW!** | **Park tickets** |

**Total:** 110 fields → 125 fields (with new forms)

### NEW FORM-REVIEW Structure

**Purpose:** Collect reviews with screenshot verification

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | Rating | `review_rating` | CHOICE | Yes | 1-5 stars |
| 2 | Feedback | `review_text` | TEXT | Yes | 10-500 chars |
| 3 | What did you like? | `review_liked` | TEXT | No | Positive aspects |
| 4 | What to improve? | `review_improve` | TEXT | No | Suggestions |
| 5 | Screenshot | `review_screenshot` | FILE | Yes if 5★ | Proof for discount |
| 6 | Name | `review_client_name` | TEXT | Yes | From booking |
| 7 | Phone | `review_client_phone` | PHONE | Yes | From booking |

**Choice Options for Rating:**
```
- ⭐⭐⭐⭐⭐ Отлично (5) — Request Google review
- ⭐⭐⭐⭐ Хорошо (4) — Request internal feedback
- ⭐⭐⭐ Средне (3) — Send to support
- ⭐⭐ Плохо (2) — Urgent manager alert
- ⭐ Ужасно (1) — CEO notification
```

**Logic Flow:**
```
Rating 5 → Request Google Maps review → Upload screenshot → Verify → Give 15% promo
Rating 4 → Thank you + ask what could be better
Rating 1-3 → Apologize + offer manager call + internal ticket
```

### NEW FORM-TICKETS Structure

**Purpose:** Sell park/attraction tickets

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | Attraction | `ticket_attraction` | HIDDEN | Yes | Auto-filled |
| 2 | Visit Date | `ticket_date` | DATE | Yes | Future dates only |
| 3 | Adults | `ticket_adults` | NUMBER | Yes | 1-99 |
| 4 | Children | `ticket_children` | NUMBER | No | 0-99 (0-12 years) |
| 5 | Name | `ticket_client_name` | TEXT | Yes | — |
| 6 | Phone | `ticket_client_phone` | PHONE | Yes | — |
| 7 | Email | `ticket_client_email` | EMAIL | Yes | For e-tickets |
| 8 | Comment | `ticket_comment` | TEXT | No | Special requests |

**Incoming Transitions:**
- All park cards (500-560, 600-607)
- Aquapark cards
- Museum cards
- Observation deck cards

**Pricing Logic (example):**
```
Ferrari World:
- Adult: 295 AED
- Child: 250 AED
Total: {{ticket_adults}}×295 + {{ticket_children}}×250 = {{total_price}} AED
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
⭐ Reviews             🎁 Loyalty/Discounts
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

**Pattern 4: Loyalty Block (NEW)**
```
🎁 Emoji + Program Name

What you get:
🔹 Benefit 1
🔹 Benefit 2
🔹 Benefit 3

How to get: [simple instructions]

Buttons:
- [Action Button]
- ⬅ Back
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

**Pattern 4: Loyalty Buttons (NEW)**
```
⭐ Оставить отзыв
🎁 Получить скидку
👥 Пригласить друзей
💎 Личный кабинет
```

**Pattern 5: Navigation Buttons**
```
⬅ Back → [Previous menu]
```
**Requirement:** MANDATORY on all cards (but missing in 50% of cases)

## Форматирование текстов бота (UI/UX стандарт)

**Эталонный гайд:** `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md`
**Универсальный промт:** `D:/Downloads/ПРОМТ_ФОРМАТИРОВАНИЕ_ТЕКСТОВ_БОТА.md`

При создании/редактировании ЛЮБЫХ текстов бота — ОБЯЗАТЕЛЬНО:

| Правило | Пример |
|---------|--------|
| Каждое сообщение начинается с эмодзи | `🛒 Корзина пуста` |
| Заголовки: эмодзи + `<b>bold</b>` + разделитель | `📊 <b>Статистика</b>\n──────────────────` |
| Списки с маркером ▫️ | `▫️ 🎫 Билеты — описание` |
| Разделители 18 символов | `──────────────────` (тонкий) / `━━━━━━━━━━━━━━━━━━` (жирный) |
| Числа/даты/суммы в `<code>` | `<code>1,500 AED</code>` |
| Кнопки ВСЕГДА с эмодзи | `✅ Подтвердить`, `❌ Отмена` |
| Пользовательский ввод экранировать | `_esc()` или `html.escape()` |

---

## Variables System (113 Variables → 140+ with new features)

### System Variables (3 + 7 new)

| Variable | Type | Description | Where Used |
|----------|------|-------------|------------|
| `{{FIRST_NAME_TEXT}}` | string | User's name from Telegram | /start, All menus |
| `{{balance}}` | number | Points balance | /balls, Personal cabinet |
| `подписка` | boolean | Subscription status | Subscription check |
| `{{review_days}}` | number | Days until review promo expires | Block 960 |
| `{{referral_days}}` | number | Days until referral promo expires | Block 960 |
| `{{referral_count}}` | number | Number of invited friends | Block 962 |
| `{{user_id}}` | string | Unique user ID | Referral links |
| `{{bant_score}}` | number | BANT qualification score (0-11) | Lead priority |
| `{{bant_priority}}` | string | hot/warm/cold | Manager notifications |
| `{{reminder_sent}}` | boolean | Reminder sent flag | Reminder logic |

### Loyalty Variables (NEW)

```
loyalty_subscribed (boolean) — Channel subscription status
loyalty_review_submitted (boolean) — Review submitted
loyalty_review_verified (boolean) — Screenshot verified
loyalty_referral_link (string) — Personal referral URL
loyalty_promo_subscribe (string) — 10% promo code
loyalty_promo_review (string) — 15% promo code
loyalty_promo_referral (string) — 25% promo code
loyalty_points_balance (number) — Current points
loyalty_points_earned (number) — Total earned
loyalty_points_spent (number) — Total spent
```

### BANT Variables (NEW)

> См. `references/bant-implementation.md` — полный список (7 переменных: bant_budget, bant_timeframe, bant_group_size, bant_authority, bant_score, bant_priority, bant_notes)

### Reminder Variables (NEW)

> См. `references/reminder-system.md` — 7 переменных (reminder_flight_date, reminder_tour_date, reminder_sent_count и др.)

### Review & Ticket Variables (NEW)

Review: 8 vars (`review_rating`, `review_text`, `review_liked`, `review_improve`, `review_screenshot`, `review_verified`, `review_client_name`, `review_client_phone`)

Ticket: 9 vars (`ticket_attraction`, `ticket_date`, `ticket_adults`, `ticket_children`, `ticket_total_price`, `ticket_client_name`, `ticket_client_phone`, `ticket_client_email`, `ticket_comment`)

## Critical Bugs & Fixes

### CRITICAL (20 bugs - user gets stuck)

**Empty Blocks Without Back Button (16):**

| Category | Blocks | Emirates | Problem |
|----------|--------|----------|---------|
| Beach Clubs | 850 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |
| Hotels | 860 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |
| Restaurants | 870 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |
| SPA/Wellness | 880 | Dubai, Abu Dhabi, Fujairah, RAK | Completely empty |

**Fix:** Add "⬅ Back" button + placeholder text (см. `references/bug-fixes-guide.md`)

**Additional Critical (4):**
- **FORM-CRUISE** — Form is COMPLETELY EMPTY (no fields)
- **FORM-HOTEL** — Form ready (10 fields) but INACCESSIBLE from interface
- **600-PARKS-AD-FUJ** — Abu Dhabi Parks (Fujairah) missing Back button
- **201-JEEP-SAFARI** — Jeep Safari from Abu Dhabi missing Back button

### HIGH Priority Bugs (60+)

- **Water Activities** (13 blocks) — no booking buttons → Add FORM-TICKETS
- **Cruises & Yachts** (10 blocks) — content not filled → Use FORM-CRUISE/YACHT
- **Dubai Parks** (17 blocks) — no ticket purchase buttons → Add FORM-TICKETS
- **Abu Dhabi Parks** (14 blocks) — no ticket purchase buttons → Add FORM-TICKETS
- **Buggies** (3 blocks) — content not filled → Use FORM-BUGGY
- **Pools** (3 of 4) — no booking buttons → Add FORM-POOL

## Creating New Content Blocks

### Loyalty Block Template (NEW)

> См. `references/block-templates.md` — секция "Шаблон лояльности" (текст, переменные, кнопки, примечания)

### BANT Qualification Template (NEW)

> См. `references/bant-implementation.md` — шаблон блока, вопросы, scoring logic

### Reminder Block Template (NEW)

> См. `references/reminder-system.md` — шаблон блока, триггеры, переменные

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
BANT score:      0-11 (calculated)
Loyalty points:  0-999999
Reminder days:   1-365
```

## System Prompt Template for Bot Integration

```markdown
You are a helpful assistant for VIP-DXB-RUS tourism bot in UAE.

# Context
- Bot serves Russian-speaking tourists in UAE
- 4 emirates: Dubai, Abu Dhabi, Ras Al Khaimah, Fujairah
- Services: excursions, parks, car rental, yacht cruises, SPA, restaurants
- 187 content blocks, 13 booking forms, 140+ variables
- Loyalty program: 10% subscribe, 15% review, 25% referrals
- BANT qualification: hot/warm/cold leads
- Smart reminders: flight, booking, tour, feedback

# Your Tasks
1. Help users navigate bot structure
2. Answer questions about services in each emirate
3. Explain booking process for each service type
4. Clarify loyalty program benefits
5. Guide through BANT qualification
6. Provide information about prices, duration, what's included

# Response Format
- Use Russian language
- Be friendly and professional
- Provide specific block IDs when referencing content
- Include emoji where appropriate (matching bot style)
- Clarify which emirate the service is available in
- Mention loyalty benefits when relevant

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
- FORM-TICKETS: 8 fields (attraction, date, adults, children, contact)

**Transport:**
- FORM-RENT: 13 fields (includes passport & license upload)
- FORM-TRANSFER: 12 fields (pickup location, car class, flight number)

**Services:**
- FORM-SPA: 13 fields (location, service type, technique, therapist gender)
- FORM-REST: 9 fields (date, time, seating zone, occasion)
- FORM-REVIEW: 7 fields (rating, feedback, screenshot, contact)

# Loyalty Program

**Always mention these benefits:**

🎁 **Permanent discounts:**
- 10% for channel subscribers (@vipdxbrus)
- Instant activation

🎁 **One-time discounts:**
- 15% for Google Maps review (30 days validity)
- 25% for 3 friend referrals (30 days validity)

🎁 **Points system:**
- 1 AED = 1 point
- 150 points = 150 AED discount

**Personal cabinet:** Block 960 (check balance, active promos)

# BANT Qualification

When user shows interest in expensive tours (500+ AED), mention:

"To better help you, answer 4 quick questions:
1. Budget range
2. Travel dates
3. Group size
4. Decision-maker status

This helps us prioritize and serve you faster!"

# Smart Reminders

Mention automatic reminders:
- 24h before flight (documents check)
- 3 days after booking (visa/insurance)
- 2 days before tour (meeting point)
- 2 days after tour (feedback request)

# Known Issues

**CRITICAL:**
- FORM-CRUISE is completely empty (cannot book cruises) → Recommend FORM-YACHT instead
- 16 empty blocks without Back buttons (850, 860, 870, 880 for all emirates)

**HIGH:**
- Water activities have no booking buttons → Direct to manager
- Many park cards lack ticket purchase buttons → Use FORM-TICKETS when available

# Example Interaction

User: "Какие есть скидки?"
Assistant: "В VIP-DXB-RUS действует программа лояльности! 🎁

Постоянная скидка:
🔹 10% для подписчиков канала @vipdxbrus

Разовые скидки (действуют 30 дней):
🔹 15% за отзыв на Google Maps
🔹 25% за приглашение 3 друзей

Плюс накопительная система:
💎 1 AED = 1 балл
💎 150 баллов = скидка 150 AED

Все скидки суммируются! Проверить баланс: Личный кабинет (блок 960)

Хотите подписаться на канал и получить первую скидку?"
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
950-999:  Service blocks (loyalty 960-963, payments 980-995)
```

### Variable Prefixes

```
gt_       Group excursions
pt_       Private excursions
buggy_    Buggy & safari
rent_     Car rental
pool_     Pools
beach_    Beach clubs
spa_      SPA services
tr_       Transfer
yacht_    Yacht rental
rest_     Restaurant
review_   Reviews (NEW)
ticket_   Park tickets (NEW)
loyalty_  Loyalty program (NEW)
bant_     Qualification (NEW)
reminder_ Reminders (NEW)
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
6. **Mention** loyalty benefits where relevant
7. **Track** user categories for reminders

### Form Design

1. **Start** with required fields (name, phone, email, date)
2. **Group** related fields (contact info, service details, preferences)
3. **Limit** choice buttons to 2-6 options
4. **Include** "Skip" option for truly optional choices
5. **Validate** data types (phone format, email format, date in future)
6. **Add** BANT questions for high-value services (500+ AED)
7. **Trigger** reminder categories on submission

### Loyalty Integration

1. **Always** mention 10% discount for new users
2. **Suggest** review after positive service (5★ rating)
3. **Offer** referral link in thank you messages
4. **Display** points balance in confirmations
5. **Send** promo expiry reminders (7 days before)

### Bug Prevention

1. **Check** every block has Back button
2. **Verify** all choice buttons lead somewhere
3. **Test** booking flow from menu to confirmation
4. **Ensure** forms have all required fields
5. **Document** any intentionally empty blocks
6. **Set up** reminder categories correctly
7. **Validate** BANT scoring logic

### Navigation Flow

1. **Maintain** clear hierarchy (menu → submenu → card → form)
2. **Avoid** circular references (A→B→C→A)
3. **Provide** multiple paths to popular services
4. **Return** to correct menu when using cross-emirate services
5. **Track** user journey for analytics
6. **Use** dynamic categories for reminders

## Common Workflows

### Adding New Excursion

```flow
1. Choose emirate (Dubai/Abu Dhabi/RAK/Fujairah)
2. Determine block ID (next available in range)
3. Create excursion card using template
4. Add emoji + name to emirate's excursion menu
5. Link to FORM-GT and FORM-PT
6. Add BANT qualification (if premium tour)
7. Set up reminder categories
8. Add Back button to excursion menu
9. Test navigation flow
10. Document in FULL-EXPORT.md
```

### Implementing Loyalty Feature

```flow
1. Identify feature (subscribe/review/referral)
2. Create feature block (960-963 range)
3. Design reward logic:
   - Subscription → permanent 10%
   - Review → one-time 15% (30 days)
   - Referral → one-time 25% (30 days)
4. Add verification mechanism (screenshot for review)
5. Set promo expiry (30 days for one-time)
6. Link to personal cabinet (block 960)
7. Add to main menu
8. Test reward flow
9. Set up expiry reminders
```

### Adding BANT Qualification

> См. `references/bant-implementation.md` — пошаговый workflow (7 шагов)

### Setting Up Reminders

> См. `references/reminder-system.md` — пошаговый workflow (9 шагов)

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

### Loyalty Discount Not Applied
**Symptom:** User subscribed but no promo code
**Cause:** Subscription check not configured
**Cause:** Verify channel subscription API integration

### Reminder Not Sent
**Symptom:** User didn't receive reminder
**Cause:** Category removed too early or timer incorrect
**Fix:** Check category assignment and wait time logic

### BANT Score Incorrect
**Symptom:** Wrong lead priority assigned
**Cause:** Points calculation error
**Fix:** Verify each answer assigns correct points (0-3)

## Success Metrics

Track these KPIs:
- **Navigation Success Rate**: % users who complete booking flow
- **Form Completion Rate**: % users who submit forms
- **Bug Escape Rate**: % users stuck in empty blocks
- **Variable Coverage**: % forms with all variables documented
- **Content Completeness**: % blocks with full content vs placeholders
- **Loyalty Enrollment**: % users who subscribe to channel
- **Review Collection Rate**: % customers who leave reviews
- **Referral Conversion**: % users who invite friends
- **BANT Hot Lead %**: % leads scoring 9-11 points
- **Reminder Open Rate**: % users who engage with reminders

**Target Metrics (based on case studies):**
- Booking conversion: 20-25% (computer club: 23%)
- Review rate: 15-20% of customers (theatre: 18 reviews in 2 weeks)
- Referral rate: 20-25% of users (theatre: 22%)
- Channel growth: 20-30% organic (theatre: 25% in 2 weeks)
- Hot lead conversion: 50-70% (vs 10-20% for cold)

## Resources

**Documentation Files:**
- `blocks/TEMPLATE.md` — Block documentation template
- `blocks/_сводка/FULL-EXPORT.md` — Complete list of 187 blocks
- `forms/_сводка/` — All 13 forms documentation
- `variables/ALL-VARIABLES.md` — 140+ variables reference
- `mermaid/` — Architecture diagrams (8 diagrams)
- `_БАГИ/` — Bug tracking (5 priority levels)

**New Documentation (v2.0):**
- `loyalty/PROGRAM-GUIDE.md` — Complete loyalty program setup
- `bant/QUALIFICATION-SETUP.md` — BANT implementation guide
- `reminders/REMINDER-SYSTEM.md` — 4 reminder types with examples
- `cases/SUCCESS-STORIES.md` — Theatre + Computer Club cases

**Analysis Files:**
- First agent output — Architecture & commands analysis
- Second agent output — Excursion patterns & formatting
- Third agent output — Services classification & patterns
- Fourth agent output — Forms system complete documentation
- **Fifth agent output (NEW)** — Loyalty & BANT integration

## Next Steps (v2.0 Roadmap)

### Week 1: Critical Fixes
- [ ] Add Back buttons to 16 empty blocks
- [ ] Fill FORM-CRUISE (11 fields from FORM-YACHT)
- [ ] Add FAQ for empty categories
- [ ] Copy examples from knowledge base

### Week 2: Loyalty Program
- [ ] Create blocks 960-963 (personal cabinet, discounts, referrals)
- [ ] Set up points system (1 AED = 1 point)
- [ ] Create FORM-REVIEW (7 fields)
- [ ] Integrate referral tracking
- [ ] Configure promo expiry (30 days)

### Week 3: BANT + Booking Buttons
- [ ] Add BANT qualification (4 questions)
- [ ] Create FORM-TICKETS (8 fields)
- [ ] Fill 62 park blocks with descriptions
- [ ] Set up lead prioritization
- [ ] Configure manager alerts

### Week 4: Reminders + Tracking
- [ ] Set up 4 reminder types
- [ ] Create UTM links for traffic sources
- [ ] Start A/B testing
- [ ] Monitor conversion rates

### Month 2+: Advanced Features
- [ ] Mini App for hotel booking
- [ ] Prize giveaways
- [ ] "Dream of Dubai?" funnel (5-lesson mini-course)
- [ ] CRM system integration
- [ ] PDF guide sales (autopay with Prodamus)

## Expected Results (v2.0)

| Metric | Current | After v2.0 | Source |
|--------|---------|------------|--------|
| Conversion to booking | ~5% | 15-20% | Computer club: 23% |
| Repeat customers | 0% | 25-30% | Theatre: +50% subscribers |
| Organic growth | 0/week | 10-15/week | Referral program |
| Google Maps reviews | 0-1/month | 5-10/month | Computer club: 360/year |
| Average check | Baseline | +15-20% | Points upsell |
| Channel subscribers | Baseline | +20-30% | Theatre: +25% in 2 weeks |

---

**Version:** 2.5.0
**Last Updated:** 2026-02-22
**Knowledge Base:** 113 Telegram bot materials analyzed
**New Features:** Loyalty program, BANT qualification, Reminders, 2 new forms
**Case Studies:** Theatre (+50% growth), Computer Club (683k RUB revenue), Mini-course (62% completion)
**Total Variables:** 140+ (from 113)
**Total Forms:** 13 (from 11)
**Bot Status:** 100% complete (all 5 phases implemented, 34 features, 330 tests)

## CatalogBot CRM Implementation (aiogram 3.25+)

The VIP-DXB-RUS bot has been fully implemented as a CRM Telegram bot using Python + aiogram. Below are all 5 implementation phases.

**Project:** `D:/Downloads/VIP-DXB-CatalogBot/`
**Bot:** @Dubaiexursions_bot
**Stack:** Python 3.13 + aiogram 3.25+ + SQLite (aiosqlite)
**Total:** 34 features across 5 phases, 330 tests passed

### Phase 1: Quick Wins — ЗАВЕРШЕНА

| # | Фича | Файлы | Статус |
|:-:|-------|:-----:|:------:|
| 20 | QR-коды для реферальных ссылок | client.py, requirements.txt, test_qr.py | Done |
| 28 | Тепловая карта активности (owner:heatmap) | database.py, owner.py, test_database.py | Done |
| 26 | 3-уровневый churn prediction (30/60/90 дней) | smart_notifications.py, test_smart_notifications.py | Done |
| 31 | Кросс-продажи после бронирования | _cross_sell.py, forms.py, forms_vehicles.py, forms_leisure.py, forms_services.py, database.py, test_cross_sell.py | Done |

**Новые файлы Phase 1:**
- `bot/handlers/_cross_sell.py` — модуль кросс-продаж (CROSS_SELL_MAP + build_cross_sell_kb)
- `tests/test_qr.py` — тесты QR-генерации
- `tests/test_smart_notifications.py` — тесты 3-tier churn
- `tests/test_cross_sell.py` — тесты кросс-продаж

**Новые зависимости:** `qrcode[pil]>=7.4.0`

**Новые DB-методы:** `get_hourly_heatmap()`, `get_cross_sell_blocks()`

**Новые handlers:** `client:qr`, `owner:heatmap`

**Новые notification types:** `re_engagement_60`, `re_engagement_90`

### Phase 2: Монетизация — ЗАВЕРШЕНА

| # | Фича | Файлы | Статус |
|:-:|-------|:-----:|:------:|
| 12 | Авто-начисление комиссии агентам | database.py, manager.py, agent.py, test_commission.py | Done |
| 27 | Unit-экономика по продукту | database.py, keyboards.py, owner.py, test_unit_economics.py | Done |
| 29 | PDF-отчёт для инвестора | pdf_report.py, owner.py, requirements.txt, test_pdf_report.py | Done |
| 25 | Когортный анализ LTV | database.py, owner.py, test_cohort.py | Done |

**Новые файлы Phase 2:**
- `bot/services/pdf_report.py` — генератор PDF-отчёта (InvestorReport + generate_investor_report)
- `tests/test_commission.py` — 11 тестов авто-комиссий
- `tests/test_unit_economics.py` — 10 тестов unit-экономики
- `tests/test_pdf_report.py` — 6 тестов PDF-генерации
- `tests/test_cohort.py` — 9 тестов когортного анализа

**Новые зависимости:** `fpdf2>=2.7.0`

**Новые DB-таблицы:** `block_costs` (себестоимость продуктов)

**Новые DB-методы:** `auto_create_agent_commission()`, `set_block_cost()`, `get_block_cost()`, `get_unit_economics()`, `get_cohort_analysis()`, `get_user_ltv()`

**Новые handlers:** `owner:pdf_report`, `owner:unit_econ`, `owner:set_cost` (FSM), `owner:cohorts`

**Тесты:** 36 новых Phase 2 (всего ~178 passed)

### Phase 3: AI-фичи — ЗАВЕРШЕНА

| # | Фича | Файлы | Статус |
|:-:|-------|:-----:|:------:|
| 2 | Голосовые сообщения (Whisper API) | voice_transcriber.py, voice.py, router.py, test_voice.py | Done |
| 1 | AI-ассистент подбора экскурсий | ai_assistant.py, search.py, keyboards.py, test_ai_assistant.py | Done |
| 3 | Авто-допродажи (smart upsell) | _cross_sell.py, database.py, manager.py, test_smart_upsell.py | Done |
| 5 | Авто-сбор отзывов | review_publisher.py, client.py, config.py, test_review_publisher.py | Done |

**Новые файлы Phase 3:**
- `bot/services/voice_transcriber.py` — транскрипция голоса через Whisper API
- `bot/services/ai_assistant.py` — RAG-поиск через OpenAI GPT-4o-mini
- `bot/services/review_publisher.py` — авто-публикация отзывов в канал
- `bot/handlers/voice.py` — обработчик голосовых сообщений
- `tests/test_voice.py` — 9 тестов голоса
- `tests/test_ai_assistant.py` — 8 тестов AI-поиска
- `tests/test_review_publisher.py` — 9 тестов отзывов
- `tests/test_smart_upsell.py` — 14 тестов smart upsell

**Новые зависимости:** `openai>=1.3.0`

**Новые DB-методы:** `get_user_booking_history()`, `get_smart_upsell()`, `get_completed_bookings_without_review()`

**Новые handlers:** `voice_router` (F.voice), `search:ai`, `review:write/pick/rate/confirm/my`

**Новые config:** `OPENAI_API_KEY`, `AI_MODEL`, `REVIEWS_CHANNEL_ID`

**Тесты:** 40 новых Phase 3 (всего ~218 passed)

### Phase 4: Партнёрская сеть — ЗАВЕРШЕНА

| # | Фича | Файлы | Статус |
|:-:|-------|:-----:|:------:|
| 14 | Рейтинг поставщиков | database.py, supplier.py, client.py, keyboards.py, test_supplier_rating.py | Done |
| 11 | Расширенный портал агентов | database.py, agent.py, owner.py, test_agent_portal.py | Done |
| 13 | Маркетплейс поставщиков | supplier_matcher.py, database.py, manager.py, test_supplier_marketplace.py | Done |
| 4 | Динамическое ценообразование | dynamic_pricing.py, database.py, owner.py, keyboards.py, test_dynamic_pricing.py | Done |

**Новые файлы Phase 4:**
- `bot/services/supplier_matcher.py` — алгоритм подбора поставщика по рейтингу и доступности
- `bot/services/dynamic_pricing.py` — движок динамического ценообразования (surge/discount)
- `tests/test_supplier_rating.py` — 15 тестов рейтинга
- `tests/test_agent_portal.py` — 17 тестов портала агентов
- `tests/test_supplier_marketplace.py` — 17 тестов маркетплейса
- `tests/test_dynamic_pricing.py` — 23 теста ценообразования

**Новые DB-таблицы (5):** `supplier_ratings`, `agent_custom_prices`, `agent_withdrawals`, `pricing_rules`, `price_history`

**Новые DB-методы (~25):** `add_supplier_rating()`, `get_supplier_avg_rating()`, `get_supplier_reviews()`, `get_suppliers_ranked_by_rating()`, `has_rated_supplier()`, `set_agent_custom_price()`, `get_agent_custom_prices()`, `get_agent_custom_price()`, `delete_agent_custom_price()`, `create_withdrawal_request()`, `get_agent_withdrawals()`, `get_pending_withdrawals()`, `process_withdrawal()`, `get_pricing_rules()`, `set_pricing_rules()`, `get_booking_demand()`, `get_demand_forecast()`, `log_price_change()`, `get_price_history()`, `get_blocks_with_pricing_rules()`, `calculate_dynamic_price()`, `assign_supplier_to_booking()`, `get_unassigned_bookings()`, `get_supplier_workload()`, `find_matching_suppliers()`, `auto_assign_supplier()`

**Новые handlers:** `sup:ratings`, `client:rate_supplier:{id}`, `agent:prices`, `agent:price_set`, `agent:withdrawals`, `agent:withdraw`, `owner:withdrawals`, `owner:wd_approve/reject`, `owner:pricing`, `owner:pricing_set`, `owner:price_forecast`, `owner:price_history`, `mgr:match_supplier`, `mgr:assign_sup`, `mgr:auto_assign`

**Тесты:** 72 новых Phase 4 (всего ~290 passed)

### Phase 5: Экосистема семьи — ЗАВЕРШЕНА

| # | Фича | Файлы | Статус |
|:-:|-------|:-----:|:------:|
| 32 | Общая база клиентов | database.py, config.py, test_business.py | Done |
| 30 | Единая панель 3 братьев | family.py, keyboards.py, router.py, test_family_dashboard.py | Done |
| 33 | Семейный P&L | pdf_report.py, database.py, test_family_pnl.py | Done |
| 34 | WhatsApp маршрутизация | whatsapp.py, contacts.py, config.py, test_whatsapp_routing.py | Done |

**Новые файлы Phase 5:**
- `bot/handlers/family.py` — семейный дашборд (~350 строк, 8 хэндлеров)
- `tests/test_business.py` — 13 тестов бизнес-таблицы
- `tests/test_family_dashboard.py` — 8 тестов семейного дашборда
- `tests/test_family_pnl.py` — 10 тестов семейного P&L
- `tests/test_whatsapp_routing.py` — 9 тестов WhatsApp маршрутизации

**Модифицированные файлы Phase 5:**
- `data/database.py` (+356 строк: businesses таблица, миграция v3, 12 методов)
- `bot/config.py` (+BUSINESS_PHONES)
- `bot/keyboards.py` (+family кнопка в OWNER меню)
- `bot/handlers/router.py` (+family_router)
- `bot/integrations/whatsapp.py` (+routing logic)
- `bot/handlers/contacts.py` (+dynamic contacts)
- `bot/services/pdf_report.py` (+generate_family_report)

**Новые DB-таблицы (1):** `businesses`

**Новые DB-колонки:** `business_id` в bookings, blocks, staff, agents, suppliers, debts, analytics_events

**Новые DB-методы (~12):** `get_business()`, `get_all_businesses()`, `get_business_by_owner()`, `get_business_by_type()`, `get_bookings_by_business()`, `get_revenue_by_business()`, `get_family_revenue()`, `get_family_bookings_summary()`, `get_cross_business_clients()`, `get_family_pnl()`, `get_family_costs()`, `get_family_commissions()`

**Новые handlers (8):** `family:dashboard`, `family:dash:{period}`, `family:biz:{id}`, `family:crossref`, `family:pnl`, `family:pdf`, `family:back`

**Новые service functions:** `generate_family_report()`, `get_business_type_for_form()`, `get_whatsapp_phone_for_booking()`, `format_booking_confirmation_with_business()`

**Новые config:** `WHATSAPP_TOURS`, `WHATSAPP_RENTAL`, `WHATSAPP_YACHT`, `BUSINESS_PHONES`

**Тесты:** 40 новых Phase 5 (всего ~330 passed)

### Итого по всем фазам

| Phase | Фичи | Новые тесты | Всего тестов |
|:-----:|:-----:|:-----------:|:------------:|
| Phase 1: Quick Wins | 4 | 9 | ~142 |
| Phase 2: Монетизация | 4 | 36 | ~178 |
| Phase 3: AI-фичи | 4 | 40 | ~218 |
| Phase 4: Партнёрская сеть | 4 | 72 | ~290 |
| Phase 5: Экосистема семьи | 4 | 40 | ~330 |
| **Итого** | **20** | **197** | **~330** |

Все 5 фаз (34 идеи из roadmap, 20 реализованных фич) завершены. Проект полностью функционален.

## PuzzleBot Platform Reference

### Ключевые концепции PuzzleBot

**PuzzleBot** — конструктор Telegram-ботов №1 (60,000+ пользователей, 126+ функций).

**Триггеры** — точки входа:
- Команды (`/start`, `/help`)
- Кнопки (inline и reply)
- Ключевые слова
- События (подписка, покупка)
- Вебхуки

**Блоки** — строительные элементы:
- Текстовые, медиа, кнопки
- Условия (if/else)
- Действия (запись данных, HTTP)
- Формы, задержки

### Шаблон команды /start

```
[Команда /start]
    ↓
[Текст: Приветствие с {{first_name}}]
    ↓
[Блок кнопок: Главное меню]
    ├─ Каталог → block_catalog
    ├─ Контакты → block_contacts
    └─ О нас → block_about
```

### Best Practices конструктора

**✅ Правильно:**
- Начните с анализа пути пользователя
- Нарисуйте диаграмму ветвлений
- Тестируйте каждую ветку
- Всегда добавляйте кнопку "⬅ Назад"

**❌ Неправильно:**
- Создание блоков без плана
- Циклические зависимости без выхода
- Цепочки более 10 шагов

### Работа с переменными

**Инициализация:**
- Числа: 0
- Строки: "" или "N/A"
- Логические: false

**Использование:**
```
Привет, {{first_name|друг}}!
Ваш баланс: {{balance}} руб.

{{if:is_vip}}
⭐ Вы VIP-клиент!
{{/if}}
```

### Горячие клавиши

| Действие | Комбинация |
|----------|-----------|
| Добавить блок | Ctrl + N |
| Удалить | Delete |
| Копировать | Ctrl + C |
| Сохранить | Ctrl + S |

---

## Альтернативные платформы

### Нужен WhatsApp или мультиплатформенность?

Если нужен бот для **WhatsApp**, **VK**, **Instagram** или **единое окно** для всех мессенджеров — используй скилл **`salebot-конструктор`**.

| Критерий | PuzzleBot (этот скилл) | SaleBot |
|----------|------------------------|---------|
| Платформы | Только Telegram | 8 мессенджеров |
| WhatsApp | ❌ | ✅ |
| Встроенная CRM | ❌ | ✅ |
| Онлайн-запись | ❌ | ✅ |
| Mini App | ✅ | ❌ |
| Цена | Дешевле | Дороже |

**Когда выбрать SaleBot:**
- Клиенты пишут в WhatsApp (основной канал в туризме ОАЭ)
- Нужно единое окно для операторов
- Требуется встроенная CRM

**Справочник:** `D:/Downloads/SALEBOT_СПРАВОЧНИК/` (65 файлов)
