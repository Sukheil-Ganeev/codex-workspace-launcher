# Cheatsheet - Быстрая справка VIP-DXB-RUS Bot

Шпаргалка для быстрого доступа к ключевой информации.

---

## Block ID Ranges (1-999)

```
001-003   Commands (/start, /balls, /staff)
010-013   Main Menus (Dubai, Abu Dhabi, RAK, Fujairah)

100-199   Dubai Services
  100-113   Dubai Excursions (13)

200-299   Abu Dhabi Services
  200-208   Abu Dhabi Excursions (8)

300-399   RAK Services
  300-313   RAK Excursions (13)

400-499   Fujairah Services
  400-409   Fujairah Excursions (9)

500-699   Parks & Entertainment
  500-560   Dubai Parks (18 subcategories)
  600-607   Abu Dhabi Parks (14 subcategories)

700-799   Cruises & Water
  700-709   Cruises Dubai
  710-719   Water Activities Dubai
  720-729   Water Activities Abu Dhabi
  730-739   Water Activities Fujairah

800-899   Activities & Lifestyle
  800-809   General Activities Menu
  810-819   Buggy/Safari
  820-829   Infinity Pools
  850       Beach Clubs (by emirate)
  860       Hotels (by emirate)
  870       Restaurants (by emirate)
  880       SPA (by emirate)

900-949   Reserved

950-999   Service Blocks
  950-953   Captcha (group entry)
  960-965   Loyalty System
  970-972   Thank You Messages
  980-995   Payment Confirmations (16 variants)
```

---

## Variable Prefixes

| Prefix | Form | Description |
|--------|------|-------------|
| `gt_` | FORM-GT | Group excursions (8 fields) |
| `pt_` | FORM-PT | Private excursions (9 fields) |
| `buggy_` | FORM-BUGGY | Buggy & safari (10 fields) |
| `rent_` | FORM-RENT | Car rental (13 fields) |
| `pool_` | FORM-POOL | Infinity pools (11 fields) |
| `beach_` | FORM-BEACH | Beach clubs (12 fields) |
| `spa_` | FORM-SPA | SPA services (13 fields) |
| `tr_` | FORM-TRANSFER | Airport transfer (12 fields) |
| `yacht_` | FORM-YACHT | Yacht rental (13 fields) |
| `rest_` | FORM-REST | Restaurant booking (9 fields) |
| `cruise_` | FORM-CRUISE | Cruises (NEW - was empty) |
| `review_` | FORM-REVIEW | Customer reviews (7 fields) |
| `ticket_` | FORM-TICKETS | Park tickets (8 fields) |
| `loyalty_` | — | Loyalty program variables |
| `bant_` | — | BANT qualification |
| `reminder_` | — | Reminder system |

---

## Form Names & Fields

| Form | Fields | Status | Use For |
|------|--------|--------|---------|
| FORM-GT | 8 | OK | Group excursions |
| FORM-PT | 9 | OK | Private excursions |
| FORM-BUGGY | 10 | OK | Buggy & jeep safari |
| FORM-RENT | 13 | OK | Car rental (with docs) |
| FORM-POOL | 11 | OK | Infinity pools |
| FORM-CRUISE | 0→7 | FIX! | Yacht cruises |
| FORM-BEACH | 12 | OK | Beach clubs |
| FORM-SPA | 13 | OK | SPA & wellness |
| FORM-TRANSFER | 12 | OK | Airport transfer |
| FORM-YACHT | 13 | OK | Yacht rental |
| FORM-REST | 9 | OK | Restaurant booking |
| FORM-REVIEW | 7 | NEW | Customer reviews |
| FORM-TICKETS | 8 | NEW | Park tickets |
| FORM-HOTEL | 10 | HIDDEN | Hotels (need access) |

---

## Emoji Standards

### Emirates
```
🕌 Abu Dhabi (mosque)
🌆 Dubai (skyscrapers)
🏖️ Ras Al Khaimah (beach)
🌊 Fujairah (water)
```

### Service Categories
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

### Excursion Types
```
🏙️ Modern cities      🕌 Mosques/culture
🌊 Sea cruises        🏜️ Desert safari
🦁 Zoos              🌸 Gardens/parks
🎡 Entertainment      🏰 Historic sites
🎣 Fishing           🦀 Crab hunting
🏎️ Car tours         🏔️ Mountains
```

### Actions
```
✅ Confirm            ❌ Cancel
📅 Date              🕐 Time
👤 Person            📱 Phone
📧 Email             💰 Price
🎫 Ticket            🔙 Back
```

---

## Loyalty Program

### Discount Types

| Type | Discount | Condition | Duration |
|------|----------|-----------|----------|
| Subscribe | 10% | Channel @vipdxbrus | Permanent |
| Review | 15% | Google Maps review | 30 days |
| Referral | 25% | Invite 3 friends | 30 days |
| Points | 150 AED | Earn 150 points | Permanent |

### Loyalty Blocks
```
960 - Personal Cabinet (balance, promos)
961 - How to Get Discounts
962 - Referral Program
963 - Leave Review → FORM-REVIEW
```

### Loyalty Variables
```
loyalty_subscribed (boolean)
loyalty_review_submitted (boolean)
loyalty_review_verified (boolean)
loyalty_referral_link (string)
loyalty_promo_subscribe (string)
loyalty_promo_review (string)
loyalty_promo_referral (string)
loyalty_points_balance (number)
```

---

## BANT Qualification

### Questions & Scoring

| Question | Field | Options | Points |
|----------|-------|---------|--------|
| Budget? | bant_budget | Economy/Medium/Premium | 0/2/3 |
| When? | bant_timeframe | Week/Month/3+ months | 3/2/0 |
| Group size? | bant_group_size | 1-2/3-5/6+ | 1/2/3 |
| Decision? | bant_authority | Self/Consult | 3/1 |

### Lead Priority

| Score | Priority | Action |
|-------|----------|--------|
| 9-11 | HOT | Call immediately |
| 5-8 | WARM | Response in 2h |
| 0-4 | COLD | Nurture sequence |

---

## Reminders

### Types

| Type | Trigger | Timing | Content |
|------|---------|--------|---------|
| Flight | Flight date | -24h | Documents check |
| Booking | Booking made | +3 days | Visa, insurance |
| Tour | Tour date | -2 days | Meeting point |
| Feedback | Tour completed | +2 days | Review request |

### Variables
```
reminder_flight_date (date)
reminder_tour_date (date)
reminder_sent_count (number)
reminder_responded (boolean)
```

---

## Quick Workflows

### Add New Excursion
```
1. Choose emirate (DXB/AD/RAK/FUJ)
2. Get next block ID (100-113, 200-208, etc.)
3. Create excursion card (use template)
4. Add button to emirate excursion menu
5. Link to FORM-GT and FORM-PT
6. Add ⬅ Назад to excursion menu
7. Test navigation
8. Document in FULL-EXPORT.md
```

### Fix Empty Block
```
1. Find block in constructor
2. Add placeholder text:
   "[EMOJI] [Category] - [Emirate]
    Раздел в разработке.
    Свяжитесь с менеджером."
3. Add buttons:
   - Contact manager
   - ⬅ Назад → emirate menu
4. Test navigation
```

### Add Booking Button
```
1. Find service block
2. Choose form:
   - Parks → FORM-TICKETS
   - Water → FORM-TICKETS
   - Yacht → FORM-YACHT
   - Cruise → FORM-CRUISE
   - Beach → FORM-BEACH
   - Pool → FORM-POOL
   - SPA → FORM-SPA
   - Restaurant → FORM-REST
3. Add button with variable preset:
   set: ticket_attraction = "[Name]"
4. Test form submission
```

### Implement Loyalty
```
1. Create blocks 960-963
2. Add to main menu
3. Set up points (1 AED = 1 point)
4. Create FORM-REVIEW
5. Add referral tracking
6. Set promo expiry (30 days)
7. Test discount application
```

### Add BANT Qualification
```
1. Identify high-value service (500+ AED)
2. Create 4 question blocks
3. Assign points (0-3 per answer)
4. Calculate total (0-11)
5. Set priority (hot/warm/cold)
6. Configure manager alerts
7. Test scoring
```

---

## Common Variables

### System Variables
```
{{FIRST_NAME_TEXT}}  - User's Telegram name
{{balance}}          - Points balance
подписка             - Subscription status (boolean)
{{user_id}}          - Unique user ID
```

### Form Variables Pattern
```
[prefix]_client_name
[prefix]_phone
[prefix]_email
[prefix]_date
[prefix]_[specific_field]
[prefix]_comment
```

### Example: FORM-GT Variables
```
gt_client_name
gt_client_phone
gt_client_email
gt_tour_date
gt_pickup_loc
gt_count_adults
gt_count_children
gt_count_infants
```

---

## Validation Rules

### Field Types

| Type | Format | Example |
|------|--------|---------|
| TEXT | 0-500 chars | Name, comment |
| PHONE | +971-XX-XXX-XXXX | +971-50-123-4567 |
| EMAIL | name@domain.ext | user@example.com |
| DATE | YYYY-MM-DD | 2026-02-15 |
| TIME | HH:MM (24h) | 14:00 |
| NUMBER | 1-999 | 5 |
| CHOICE | Options only | "14:00" |
| FILE | Image/PDF | document.jpg |

### Recommended Limits
```
Adults:     1-99
Children:   0-99
Infants:    0-10
Guests:     1-500 (yacht)
Days:       1-365 (rental)
Luggage:    0-20
BANT score: 0-11
Points:     0-999999
```

---

## Emirates Quick Codes

| Code | Emirate | Menu ID | Excursions Range |
|------|---------|---------|------------------|
| DXB | Dubai | 010 | 100-113 (13) |
| AD | Abu Dhabi | 011 | 200-208 (8) |
| RAK | Ras Al Khaimah | 012 | 300-313 (13) |
| FUJ | Fujairah | 013 | 400-409 (9) |

---

## Critical Bugs Summary

### MUST FIX (20 Critical)
```
16x Empty blocks (850/860/870/880 × 4 emirates)
1x  FORM-CRUISE empty (0 fields)
1x  FORM-HOTEL inaccessible
1x  600-PARKS-AD-FUJ no Back
1x  201-JEEP-SAFARI no Back
```

### HIGH Priority (60+)
```
13x Water Activities - no booking
10x Cruises & Yachts - empty content
17x Dubai Parks - no tickets
14x Abu Dhabi Parks - no tickets
3x  Buggy - empty content
3x  Pools - no booking
```

---

## Button Patterns

### Standard Service Card
```yaml
buttons:
  - text: "🎫 Забронировать"
    screen: FORM-[TYPE]
  - text: "⬅ Назад"
    screen: [PARENT_MENU_ID]
```

### Excursion Card
```yaml
buttons:
  - text: "Оплатить групповой тур"
    screen: FORM-GT
  - text: "Оплатить приватный тур"
    screen: FORM-PT
  - text: "⬅ Назад"
    screen: [EXCURSION_MENU_ID]
```

### Menu
```yaml
buttons:
  - text: "[EMOJI] [Service 1]"
    screen: [BLOCK_ID_1]
  - text: "[EMOJI] [Service 2]"
    screen: [BLOCK_ID_2]
  - text: "⬅ Назад"
    screen: [PARENT_MENU_ID]
```

### Loyalty
```yaml
buttons:
  - text: "⭐ Оставить отзыв"
    screen: FORM-REVIEW
  - text: "🎁 Получить скидку"
    screen: 961
  - text: "👥 Пригласить друзей"
    screen: 962
  - text: "💎 Личный кабинет"
    screen: 960
  - text: "⬅ Назад"
    screen: [MAIN_MENU]
```

---

## Text Patterns

### Minimal Menu
```
[Category Name]
```

### Menu with Subtitle
```
[Category Name]

[Description/subtitle]
```

### Service Card
```
[EMOJI] [Service Name]

[Description 1-3 sentences]
[Optional: price, duration, included]
```

### Placeholder (for empty blocks)
```
[EMOJI] [Category] - [Emirate]

Раздел в разработке.

Для бронирования свяжитесь с менеджером.
```

---

## Success Metrics Targets

| Metric | Target |
|--------|--------|
| Booking conversion | 20-25% |
| Review rate | 15-20% |
| Referral rate | 20-25% |
| Channel growth | 20-30% organic |
| Hot lead conversion | 50-70% |

---

## File References

| File | Purpose |
|------|---------|
| `../SKILL.md` | Main documentation |
| `troubleshooting.md` | Problem solving |
| `block-templates.md` | Block templates |
| `bug-fixes-guide.md` | Bug fixing guide |
| `faq.md` | FAQ |

---

**Version:** 2.0
**Last Updated:** 2026-02-02
