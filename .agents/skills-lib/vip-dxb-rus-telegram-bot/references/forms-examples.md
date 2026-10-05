# Forms Examples for VIP-DXB-RUS Telegram Bot

Real-world booking form examples with best practices, validation, and success patterns.

## Table of Contents

1. [FORM-REVIEW: Customer Feedback](#form-review-customer-feedback)
2. [FORM-TICKETS: Park & Attraction Tickets](#form-tickets-park--attraction-tickets)
3. [FORM-BANT: Customer Qualification](#form-bant-customer-qualification)
4. [FORM-GT: Group Excursion (Reference)](#form-gt-group-excursion-reference)
5. [FORM-YACHT: Complex Multi-Field (Reference)](#form-yacht-complex-multi-field-reference)
6. [Form Optimization Patterns](#form-optimization-patterns)

---

## FORM-REVIEW: Customer Feedback

### Purpose
Collect customer reviews with routing (positive to public, negative to internal) and incentivize Google Maps reviews with screenshot verification.

### Complexity
⭐⭐⭐ (7 fields, conditional logic, file upload, admin verification)

### Full Structure

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | Rating | `review_rating` | CHOICE | Yes | 1-5 stars, determines flow |
| 2 | Feedback Text | `review_text` | TEXT | Yes | 10-500 chars |
| 3 | What did you like? | `review_liked` | TEXT | No | Positive aspects |
| 4 | What to improve? | `review_improve` | TEXT | No | Constructive criticism |
| 5 | Screenshot | `review_screenshot` | FILE | Conditional | Required if 5★ for promo |
| 6 | Name | `review_client_name` | TEXT | Yes | Pre-filled from booking |
| 7 | Phone | `review_client_phone` | PHONE | Yes | Pre-filled from booking |

### Choice Options for Rating

```markdown
Оцените вашу поездку:

Buttons:
⭐⭐⭐⭐⭐ Отлично (5)
⭐⭐⭐⭐ Хорошо (4)
⭐⭐⭐ Средне (3)
⭐⭐ Плохо (2)
⭐ Ужасно (1)
```

### Conditional Logic

**If Rating = 5:**
```markdown
Спасибо за высокую оценку! 🎉

Поделитесь впечатлениями на Google Maps?

За отзыв дарим:
🎁 Скидку 15% на следующую поездку (промокод действует 30 дней)

Как получить скидку:
1. Нажмите "Оставить отзыв" → откроется Google Maps
2. Напишите отзыв (2-3 предложения)
3. Сделайте скриншот отзыва
4. Загрузите скриншот в бот
5. Получите промокод REVIEW15

Buttons:
- Оставить отзыв на Google Maps (https://g.page/r/...)
- Пропустить
```

**If Rating = 4:**
```markdown
Спасибо за отзыв! 😊

Расскажите, что можно улучшить?

[Text input field]

Ваше мнение поможет нам стать лучше!
```

**If Rating = 1-3:**
```markdown
Извините, что не оправдали ожидания 😔

Расскажите, что пошло не так?

[Text input field]

Хотите, чтобы менеджер позвонил и помог решить ситуацию?

Buttons:
- Да, жду звонка в течение часа
- Да, позвоните завтра
- Нет, спасибо
```

### Screenshot Verification Flow

**User uploads screenshot:**
```markdown
Загрузите скриншот отзыва

[File upload field]

Скриншот должен включать:
✅ Интерфейс Google Maps
✅ Ваш username
✅ Текст отзыва
✅ 5 звёзд

После проверки (до 24 часов) вы получите промокод.
```

**Admin receives notification:**
```markdown
🆕 Новый отзыв на проверку

ID: #{{review_id}}
Пользователь: {{review_client_name}}
Телефон: {{review_client_phone}}
Рейтинг: 5 звёзд
Тур: {{tour_name}}
Дата тура: {{tour_date}}

Screenshot: [View Image]

Проверить:
✅ Google Maps interface visible
✅ Username matches our records
✅ Review is new (not old screenshot)
✅ Review in Russian
✅ No offensive content

Actions:
[✅ Одобрить] → Send promo REVIEW15
[❌ Отклонить] → Ask for new screenshot
[🚫 Бан] → Suspicious activity
```

**If approved:**
```markdown
✅ Отзыв проверен!

Ваш промокод: REVIEW15

Скидка: 15%
Действует: {{expiry_date}} (30 дней)
Применяется: На любой тур

Спасибо за отзыв! 🎉

Buttons:
- Выбрать следующий тур
- Личный кабинет
```

**If rejected:**
```markdown
❌ Скриншот отклонён

Причина: {{rejection_reason}}

Пожалуйста, загрузите новый скриншот:
- Убедитесь, что виден интерфейс Google Maps
- Проверьте, что отзыв от вашего имени
- Скриншот должен быть чётким

Buttons:
- Загрузить новый скриншот
- Связаться с поддержкой
```

### Anti-Fraud Protection

**One Review Per User:**
```python
# Check if user already submitted review
existing_review = db.reviews.find_one({
    "user_id": user.id,
    "verified": True,
    "created_at": {"$gt": now() - timedelta(days=365)}
})

if existing_review:
    send_message(
        "Вы уже получили скидку за отзыв в этом году.\n"
        "Следующий отзыв можно оставить через {{days_until}} дней."
    )
else:
    allow_review_submission()
```

**Screenshot Validation:**
```python
def validate_screenshot(image):
    # OCR to extract text
    text = ocr_extract(image)

    checks = {
        "has_google_maps_ui": "Google" in text or "Карты" in text,
        "has_stars": "★" in text or "⭐" in text,
        "has_user_name": user.name in text,
        "min_length": len(text) > 50,  # Real review, not just rating
    }

    return all(checks.values()), checks
```

### Variables Summary

```python
review_rating = CHOICE([1, 2, 3, 4, 5])
review_text = TEXT(min=10, max=500)
review_liked = TEXT(optional=True, max=500)
review_improve = TEXT(optional=True, max=500)
review_screenshot = FILE(
    types=["image/jpeg", "image/png"],
    max_size=5_000_000,  # 5MB
    required_if=lambda: review_rating == 5
)
review_client_name = TEXT(prefilled=True)
review_client_phone = PHONE(prefilled=True)

# Internal (set by system)
review_verified = BOOLEAN(default=False)
review_promo_sent = BOOLEAN(default=False)
review_rejection_reason = TEXT(optional=True)
```

### Expected Metrics

| Metric | Target | Actual (Computer Club) |
|--------|--------|------------------------|
| Review request open rate | 40-60% | 52% |
| 5-star submission rate | 60-80% | 71% |
| Screenshot upload rate | 80-90% | 85% |
| Admin approval rate | 90-95% | 93% |
| Public review conversion | 50-70% | 65% |

---

## FORM-TICKETS: Park & Attraction Tickets

### Purpose
Sell tickets to parks, museums, observation decks, aquaparks with dynamic pricing calculation.

### Complexity
⭐⭐ (8 fields, price calculation)

### Full Structure

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | Attraction Name | `ticket_attraction` | HIDDEN | Yes | Auto-filled from button |
| 2 | Visit Date | `ticket_date` | DATE | Yes | Future dates only |
| 3 | Adults (13+ years) | `ticket_adults` | NUMBER | Yes | 1-99 |
| 4 | Children (3-12 years) | `ticket_children` | NUMBER | No | 0-99, default 0 |
| 5 | Infants (0-2 years) | `ticket_infants` | HIDDEN | No | Always free, not shown |
| 6 | Client Name | `ticket_client_name` | TEXT | Yes | Full name |
| 7 | Phone | `ticket_client_phone` | PHONE | Yes | +971-XX-XXX-XXXX |
| 8 | Email | `ticket_client_email` | EMAIL | Yes | For e-tickets |
| 9 | Special Requests | `ticket_comment` | TEXT | No | Max 500 chars |

### Attraction Name (Hidden Field)

**Set automatically from button context:**

```markdown
User in Block 501: Ferrari World
↓
Clicks "Купить билет"
↓
Form opens with:
  ticket_attraction = "Ferrari World"
  (hidden from user, pre-filled)
```

**Why hidden:**
- User already knows which attraction (they clicked from that card)
- Reduces form fields from 9 to 8 (less friction)
- Prevents user from changing attraction mid-form

### Date Selection

```markdown
Выберите дату посещения:

[Calendar widget]

Доступные даты: от {{tomorrow}} до {{3_months_from_now}}

⚠️ Билеты нельзя купить на сегодня (нужно минимум 24 часа на обработку)

Buttons:
- Завтра ({{tomorrow_date}})
- Через неделю ({{next_week_date}})
- Выбрать другую дату (opens calendar)
```

**Validation:**
```python
def validate_date(selected_date):
    tomorrow = date.today() + timedelta(days=1)
    max_date = date.today() + timedelta(days=90)

    if selected_date < tomorrow:
        return False, "Минимум 24 часа на обработку. Выберите завтра или позже."

    if selected_date > max_date:
        return False, "Можно бронировать максимум на 3 месяца вперёд."

    return True, None
```

### Adults & Children Count

```markdown
Количество взрослых (13+ лет):

[Number input, default = 2]

Buttons:
- 1
- 2 (selected)
- 3
- 4
- 5
- Другое (manual input)

---

Количество детей (3-12 лет):

[Number input, default = 0]

Buttons:
- 0 (selected)
- 1
- 2
- 3
- Другое (manual input)

💡 Дети до 3 лет — бесплатно (не нужно указывать)
```

### Price Calculation (Live)

**After user enters adults & children:**

```markdown
💰 Предварительная стоимость:

Ferrari World:
Adults: {{ticket_adults}} × 295 AED = {{adults_subtotal}} AED
Children: {{ticket_children}} × 250 AED = {{children_subtotal}} AED

Итого: {{total_price}} AED

*Точная цена подтвердится менеджером

Buttons:
- Продолжить
- Изменить количество
```

**Price Table (internal):**

```python
ATTRACTION_PRICES = {
    "Ferrari World": {"adult": 295, "child": 250},
    "Warner Bros": {"adult": 290, "child": 240},
    "IMG Worlds": {"adult": 280, "child": 230},
    "Aquaventure": {"adult": 270, "child": 220},
    "Burj Khalifa": {"adult": 150, "child": 120},
    "Dubai Frame": {"adult": 50, "child": 20},
}

def calculate_price(attraction, adults, children):
    prices = ATTRACTION_PRICES[attraction]
    subtotal_adults = adults * prices["adult"]
    subtotal_children = children * prices["child"]
    total = subtotal_adults + subtotal_children

    return {
        "adults": adults,
        "children": children,
        "adult_price": prices["adult"],
        "child_price": prices["child"],
        "subtotal_adults": subtotal_adults,
        "subtotal_children": subtotal_children,
        "total": total,
    }
```

### Contact Fields

**Pre-fill if user previously booked:**

```python
# Check if user has previous bookings
previous = db.bookings.find_one(
    {"user_id": user.id},
    sort=[("created_at", -1)]  # Most recent
)

if previous:
    # Pre-fill form
    ticket_client_name = previous.get("client_name")
    ticket_client_phone = previous.get("client_phone")
    ticket_client_email = previous.get("client_email")

    show_message(
        "Мы заполнили ваши данные из предыдущего бронирования.\n"
        "Проверьте и при необходимости измените."
    )
```

**Email for e-tickets:**

```markdown
Email для отправки билетов:

[Email input, pre-filled if available]

📧 На этот email придут:
- Электронные билеты (QR-коды)
- Подтверждение бронирования
- Инструкции по посещению

Кнопки:
- Продолжить
```

**Validation:**
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Неверный формат. Пример: name@example.com"

    if email.endswith("@mail.ru") or email.endswith("@yandex.ru"):
        # Russian emails common for tourists
        return True, None

    return True, None
```

### Special Requests (Optional)

```markdown
Особые пожелания (необязательно):

[Text area, max 500 chars]

Например:
- Нужна коляска для ребёнка
- Есть аллергия на орехи
- Нужен русскоговорящий сопровождающий
- Отмечаем День Рождения

Buttons:
- Пропустить
- Продолжить
```

### Confirmation Message

```markdown
✅ Заявка принята!

Номер бронирования: #{{booking_id}}

Детали:
🎢 {{ticket_attraction}}
📅 {{ticket_date}}
👥 {{ticket_adults}} взрослых, {{ticket_children}} детей
💰 {{total_price}} AED

Контакты:
{{ticket_client_name}}
📞 {{ticket_client_phone}}
📧 {{ticket_client_email}}

Что дальше:
1. Менеджер свяжется в течение 2 часов
2. Подтвердит бронь и цену
3. Отправит ссылку на оплату
4. После оплаты — электронные билеты на email

Пока ждёте:
🎁 Получите 10% скидку — подпишитесь на @vipdxbrus
📍 Как добраться до {{ticket_attraction}} → /directions

Buttons:
- Мои бронирования
- Добавить ещё билеты
- Связаться с менеджером
- ⬅ Главное меню
```

### Manager Notification

```markdown
🎫 Новое бронирование билетов

ID: #{{booking_id}}

Клиент:
{{ticket_client_name}}
📞 {{ticket_client_phone}}
📧 {{ticket_client_email}}

Заказ:
🎢 {{ticket_attraction}}
📅 {{ticket_date}}
👥 {{ticket_adults}} взрослых, {{ticket_children}} детей

💰 Стоимость: {{total_price}} AED

Комментарий:
{{ticket_comment}}

⏰ Обработать в течение 2 часов

Actions:
[Подтвердить] → Send payment link
[Позвонить клиенту]
[Изменить детали]
```

### Variables Summary

```python
ticket_attraction = TEXT(hidden=True, required=True)
ticket_date = DATE(
    min=date.today() + timedelta(days=1),
    max=date.today() + timedelta(days=90),
    required=True
)
ticket_adults = NUMBER(min=1, max=99, default=2, required=True)
ticket_children = NUMBER(min=0, max=99, default=0, required=False)
ticket_client_name = TEXT(min=2, max=100, required=True)
ticket_client_phone = PHONE(pattern=r'^\+971-\d{2}-\d{3}-\d{4}$', required=True)
ticket_client_email = EMAIL(required=True)
ticket_comment = TEXT(max=500, required=False)

# Calculated (not input by user)
ticket_total_price = NUMBER(calculated=True)
ticket_adult_price = NUMBER(calculated=True)
ticket_child_price = NUMBER(calculated=True)
```

### Incoming Transitions

**From park cards:**
- Block 501: Ferrari World → "Купить билет"
- Block 502: Warner Bros → "Купить билет"
- Block 503: IMG Worlds → "Купить билет"
- Block 504: Aquaventure → "Купить билет"
- Block 510: Burj Khalifa → "Купить билет"
- Block 520: Dubai Frame → "Купить билет"
- ... (62 total park blocks)

### Expected Metrics

| Metric | Target |
|--------|--------|
| Form start rate | 70-80% (from "Buy" button) |
| Form completion rate | 60-70% |
| Average time to complete | 2-3 minutes |
| Conversion to payment | 80-90% (after manager call) |

---

## FORM-BANT: Customer Qualification

### Purpose
Qualify leads as Hot/Warm/Cold based on Budget, Authority, Need, Timeframe to prioritize manager outreach.

### Complexity
⭐⭐⭐ (4 questions, scoring logic, conditional routing)

### Full Structure

| # | Question | Variable | Type | Points | Required |
|---|----------|----------|------|--------|----------|
| 1 | Budget | `bant_budget` | CHOICE | 0-3 | Yes |
| 2 | Timeframe | `bant_timeframe` | CHOICE | 0-3 | Yes |
| 3 | Group Size | `bant_group_size` | CHOICE | 0-3 | Yes |
| 4 | Authority | `bant_authority` | CHOICE | 0-3 | Yes |
| — | **Total Score** | `bant_score` | NUMBER | **0-11** | Calculated |
| — | **Priority** | `bant_priority` | TEXT | hot/warm/cold | Calculated |

### Question 1: Budget

```markdown
Какой у вас бюджет на поездку?

Buttons:
💰 Эконом (до 500 AED/чел) → 0 points
💰💰 Средний (500-1500 AED/чел) → 2 points
💰💰💰 Премиум (1500+ AED/чел) → 3 points
```

**Why we ask:**
```
Low budget → Likely to haggle, ask for discounts, choose cheapest options
Medium budget → Reasonable customer, willing to pay for quality
High budget → VIP customer, wants premium service, high LTV
```

### Question 2: Timeframe

```markdown
Когда планируете поездку?

Buttons:
🔥 Через неделю → 3 points (urgent, ready to book)
📅 Через месяц → 2 points (planned, likely to book)
📆 Через 3+ месяца → 0 points (research phase, may not book)
```

**Why we ask:**
```
<1 week → Hot lead, needs immediate assistance
1 month → Warm lead, actively planning
3+ months → Cold lead, just researching, may change plans
```

### Question 3: Group Size / Need

```markdown
Сколько человек?

Buttons:
👤 1-2 человека → 1 point
👥 3-5 человек → 2 points
👨‍👩‍👧‍👦 6+ человек → 3 points
```

**Why we ask:**
```
1-2 → Low value booking
3-5 → Medium value, typical family
6+ → High value, group tour, potential repeat customer
```

### Question 4: Authority (Decision-maker)

```markdown
Кто принимает решение о покупке?

Buttons:
✅ Я сам решаю → 3 points
❓ Нужно согласовать (с семьёй/друзьями) → 1 point
🏢 Решает компания/турагент → 0 points
```

**Why we ask:**
```
Self → Can close deal on call
Need approval → Longer sales cycle
Company → B2B lead, different process
```

### Scoring Logic

```python
def calculate_bant_score(budget, timeframe, group_size, authority):
    points = {
        "budget": {
            "economy": 0,
            "medium": 2,
            "premium": 3,
        },
        "timeframe": {
            "week": 3,
            "month": 2,
            "3months": 0,
        },
        "group_size": {
            "1-2": 1,
            "3-5": 2,
            "6+": 3,
        },
        "authority": {
            "self": 3,
            "consult": 1,
            "company": 0,
        },
    }

    score = (
        points["budget"][budget] +
        points["timeframe"][timeframe] +
        points["group_size"][group_size] +
        points["authority"][authority]
    )

    # Determine priority
    if score >= 9:
        priority = "hot"
    elif score >= 5:
        priority = "warm"
    else:
        priority = "cold"

    return score, priority
```

### Example Scores

**Example 1: VIP Customer**
- Budget: Premium (3)
- Timeframe: Week (3)
- Group: 6+ people (3)
- Authority: Self (3)
- **Total: 11/11 → 🔥 HOT**

**Example 2: Typical Family**
- Budget: Medium (2)
- Timeframe: Month (2)
- Group: 3-5 people (2)
- Authority: Self (3)
- **Total: 9/11 → 🔥 HOT**

**Example 3: Budget Traveler**
- Budget: Economy (0)
- Timeframe: 3+ months (0)
- Group: 1-2 people (1)
- Authority: Consult (1)
- **Total: 2/11 → ❄️ COLD**

### Manager Notification (Hot Lead)

```markdown
🔥 ГОРЯЧАЯ ЗАЯВКА #{{booking_id}}

BANT Score: {{bant_score}}/11
Priority: HOT 🔥

Клиент:
{{gt_client_name}}
📞 {{gt_client_phone}}
📧 {{gt_client_email}}

Детали:
🎯 Тур: {{tour_name}}
📅 Дата: {{gt_tour_date}}

📊 BANT Анализ:
💰 Бюджет: Премиум (1500+ AED/чел)
⏰ Сроки: Через неделю 🔥
👥 Группа: 6+ человек (высокий чек)
✅ Решение: Сам принимает

Ожидаемая выручка: ~{{estimated_revenue}} AED

⏰ СРОЧНО: Обработать в течение 30 минут!

Actions:
[📞 Позвонить сейчас]
[📧 Отправить предложение]
[📝 Посмотреть детали]
```

### Manager Notification (Warm Lead)

```markdown
🌡️ Тёплая заявка #{{booking_id}}

BANT Score: {{bant_score}}/11
Priority: WARM 🌡️

Клиент:
{{gt_client_name}}
📞 {{gt_client_phone}}

Детали:
🎯 Тур: {{tour_name}}
📅 Планируется: через месяц

📊 BANT Анализ:
💰 Бюджет: Средний (500-1500 AED/чел)
⏰ Сроки: Через месяц
👥 Группа: 3-5 человек
✅ Решение: Сам принимает

⏰ Обработать в течение 2 часов

Actions:
[📞 Позвонить]
[📧 Отправить предложение]
```

### Manager Notification (Cold Lead)

```markdown
❄️ Холодная заявка #{{booking_id}}

BANT Score: {{bant_score}}/11
Priority: COLD ❄️

Клиент:
{{gt_client_name}}
📧 {{gt_client_email}}

Детали:
🎯 Тур: {{tour_name}}
📅 Планируется: через 3+ месяца

📊 BANT Анализ:
💰 Бюджет: Эконом (до 500 AED/чел)
⏰ Сроки: Через 3+ месяца
👥 Группа: 1-2 человека
❓ Решение: Нужно согласовать

→ Добавлен в прогревающую цепочку
→ Email-рассылка раз в 2 недели

⏰ Обработать завтра

Actions:
[📧 Добавить в nurture campaign]
[📝 Посмотреть детали]
```

### Nurture Campaign (for Cold Leads)

```markdown
Day 0: Welcome email
  "Спасибо за интерес к турам в Дубай!"
  "Вот 5 советов по планированию поездки..."

Day 7: Value content
  "Топ-10 мест в Дубае (с фото)"

Day 14: Social proof
  "Как Анна с семьёй отдохнула в Дубае (реальный отзыв)"

Day 30: Offer
  "Специальное предложение: скидка 15% на ранее бронирование"

Day 60: Reminder
  "Ещё думаете о Дубае? Ответим на вопросы!"
```

### Variables Summary

```python
bant_budget = CHOICE(["economy", "medium", "premium"], required=True)
bant_timeframe = CHOICE(["week", "month", "3months"], required=True)
bant_group_size = CHOICE(["1-2", "3-5", "6+"], required=True)
bant_authority = CHOICE(["self", "consult", "company"], required=True)
bant_score = NUMBER(min=0, max=11, calculated=True)
bant_priority = TEXT(calculated=True)  # "hot", "warm", or "cold"
bant_estimated_revenue = NUMBER(calculated=True)
```

### Expected Conversion Rates

| Priority | % of Leads | Conversion to Booking | Average Revenue |
|----------|------------|-----------------------|-----------------|
| Hot (9-11) | 15-20% | 50-70% | 2,000+ AED |
| Warm (5-8) | 40-50% | 25-40% | 1,000-2,000 AED |
| Cold (0-4) | 30-40% | 10-20% | 500-1,000 AED |

**ROI:**
- Hot leads: 5-7x more likely to convert than cold
- Warm leads: 2-3x more likely to convert than cold
- Managers should spend 70% time on hot, 25% on warm, 5% on cold

---

## FORM-GT: Group Excursion (Reference)

### Purpose
Book group excursions (standard, non-private tours)

### Structure (Existing)

| # | Field | Variable | Type | Required |
|---|-------|----------|------|----------|
| 1 | Client Name | `gt_client_name` | TEXT | Yes |
| 2 | Phone | `gt_client_phone` | PHONE | Yes |
| 3 | Email | `gt_client_email` | EMAIL | Yes |
| 4 | Tour Date | `gt_tour_date` | DATE | Yes |
| 5 | Pickup Location | `gt_pickup_loc` | CHOICE | Yes |
| 6 | Adults | `gt_count_adults` | NUMBER | Yes |
| 7 | Children | `gt_count_children` | NUMBER | No |
| 8 | Infants | `gt_count_infants` | NUMBER | No |

**Pickup Location Choices:**
```
- Hotel (укажите название в комментарии)
- Airport DXB
- Airport DWC
- Dubai Mall
- Burj Khalifa
- Dubai Marina
- JBR Beach
- Другое (укажите адрес)
```

---

## FORM-YACHT: Complex Multi-Field (Reference)

### Purpose
Rent private yacht with full customization (route, food, extras)

### Structure (Existing - Most Complex Form)

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | Client Name | `yacht_client_name` | TEXT | Yes | — |
| 2 | Phone | `yacht_phone` | PHONE | Yes | — |
| 3 | Date | `yacht_date` | DATE | Yes | Future only |
| 4 | Start Time | `yacht_start_time` | TIME | Yes | 09:00-21:00 |
| 5 | Duration | `yacht_duration` | CHOICE | Yes | 2h/3h/4h/5+h |
| 6 | Guests | `yacht_guests` | NUMBER | Yes | 1-500 |
| 7 | Kids | `yacht_kids` | NUMBER | No | 0-99 |
| 8 | Route | `yacht_route` | CHOICE | Yes | 6 options |
| 9 | Occasion | `yacht_occasion` | CHOICE | No | Birthday/Wedding/etc |
| 10 | Food | `yacht_food` | CHOICE | Yes | Own/Grill/Catering/None |
| 11 | Extras | `yacht_extras` | MULTI-CHOICE | No | Jet Ski/Fishing/etc |
| 12 | Comment | `yacht_comment` | TEXT | No | Special requests |

**Route Choices:**
```
- Dubai Marina → Palm → Marina (classic loop)
- Dubai Marina → Burj Al Arab → Marina
- Dubai Marina → Atlantis → Marina
- Dubai Canal (urban views)
- Open sea (swimming & fishing)
- Custom route (describe in comments)
```

**Food Choices:**
```
- Принесём своё (free)
- Барбекю на борту (+500 AED)
- Кейтеринг (от +800 AED, укажите предпочтения)
- Не нужно
```

**Extras (Multi-Select):**
```
- Jet Ski (+300 AED)
- Рыбалка (+200 AED)
- Декор (День Рождения/Свадьба) (+500 AED)
- Трансфер до марины (+100 AED)
- Пропустить
```

**Complexity:**
- 13 fields (most in system)
- Multi-choice (extras)
- Conditional pricing (food, extras)
- Complex validation (guests vs yacht capacity)

---

## Form Optimization Patterns

### 1. Progressive Disclosure

**Bad (All at Once):**
```
Page 1:
[13 fields shown immediately]
User overwhelmed → abandons
```

**Good (Step by Step):**
```
Step 1: What & When (3 fields)
  - Attraction
  - Date
  - Time

Step 2: Who (2 fields)
  - Adults
  - Children

Step 3: Contact (3 fields)
  - Name
  - Phone
  - Email

Step 4: Confirmation
  - Review & submit
```

### 2. Smart Defaults

```python
defaults = {
    "date": tomorrow,  # Most book next day
    "time": "14:00",   # Afternoon popular
    "adults": 2,       # Average couple
    "children": 0,     # Most don't have kids
    "pickup": "Hotel", # Most common
}
```

### 3. Validation Messages

**Bad:**
```
"Invalid input"
"Error"
"Wrong format"
```

**Good:**
```
Phone: "Формат: +971-50-123-4567"
Email: "Пример: name@example.com"
Date: "Выберите дату в будущем (минимум завтра)"
```

### 4. Pre-fill from Previous Bookings

```python
if user.has_previous_booking():
    prefill({
        "name": user.last_booking.name,
        "phone": user.last_booking.phone,
        "email": user.last_booking.email,
        "pickup": user.last_booking.pickup,
    })

    show_message(
        "Мы заполнили ваши данные из предыдущего бронирования.\n"
        "Проверьте и при необходимости измените."
    )
```

### 5. Conditional Fields

```markdown
User selects "Birthday" occasion
↓
Show new field: "Birthday person's name"
Show new field: "Age (for cake candles)"

User selects "None" for occasion
↓
Hide extra fields
```

### 6. Real-time Calculation

```markdown
User changes:
  Adults: 2 → 3
↓
Instantly update:
  Price: 590 AED → 885 AED
```

### 7. Progress Indicator

```markdown
Шаг 2 из 4

███████░░░ 50%

[Visual bar showing progress]
```

---

## NocoDB Integration for Admin Processing

### Purpose
Process booking requests through admin Mini-App with direct NocoDB database integration.

### Source
Based on case study: "Обработка заявок с NocoDB" (PuzzleBot)

### NocoDB Table Structure

| Field | Type | Description |
|-------|------|-------------|
| user_id | Number | Telegram user ID ({{USER_ID_TEXT}}) |
| name | Text | Client full name ({{FIRST_NAME_AND_LAST_NAME_TEXT}}) |
| about | Long Text | Booking details (collected from user) |
| phone | Text | Client phone number |
| tour | Text | Tour/service name |
| date | Date | Requested date |
| status | Text | "new", "processing", "confirmed", "cancelled" |

### Setup in PuzzleBot

**Step 1: Configure NocoDB Integration**
```
Settings > Integrations > NocoDB
↓
Enter your NocoDB token
↓
Select database and table
```

**Step 2: Create Variables**
```
1. about (text) - User input storage

2. get_id (NocoDB integrated)
   - Integration: NocoDB
   - Database: Your DB
   - Table: Bookings
   - Output column: user_id

3. get_name (NocoDB integrated)
   - Same as above
   - Output column: name

4. get_about (NocoDB integrated)
   - Same as above
   - Output column: about
```

### User Flow (Booking Submission)

**Mini-App: "Leave Booking Request"**
```markdown
📝 Оставить заявку

Заполните информацию о себе:

[Form: Name, Phone, Tour, Date, Comments]

↓ On Submit ↓

Actions:
1. Create NocoDB row:
   - user_id: {{USER_ID_TEXT}}
   - name: {{FIRST_NAME_AND_LAST_NAME_TEXT}}
   - about: {{about}}

2. Send command to admin:
   - Command: /new_booking
   - Target: @admin_username (another user)
```

**Confirmation to User:**
```markdown
✅ Заявка отправлена!

Номер: #{{USER_ID_TEXT}}-{{timestamp}}

Менеджер рассмотрит вашу заявку и свяжется с вами в течение 30 минут.

Buttons:
- Мои заявки
- ⬅ Главное меню
```

### Admin Flow (Process Booking)

**Mini-App: "View Booking"**
```markdown
📋 Новая заявка

ID: {{get_id}}
Имя: {{get_name}}
Детали: {{get_about}}

---

Buttons (Fixed Keyboard):
[✅ Принять] (green)
[❌ Отклонить] (red)
```

**Condition: "Accept Booking"**
```
Check: No check (always execute)

Actions:
1. Send command "Booking Accepted" to user {{get_id}}
2. Delete NocoDB row where user_id = {{get_id}}
3. Go to Condition "Next Booking"
```

**Condition: "Reject Booking"**
```
Check: No check (always execute)

Actions:
1. Send command "Booking Rejected" to user {{get_id}}
2. Delete NocoDB row where user_id = {{get_id}}
3. Go to Condition "Next Booking"
```

**Condition: "Next Booking"**
```
Check: Variable {{get_id}} has value?
  Yes → Go to Mini-App "View Booking"
  No → Go to Block "All Processed"
```

**Block: "All Processed"**
```markdown
✅ Все заявки обработаны!

На данный момент новых заявок нет.

Buttons:
- Обновить список
- ⬅ Главное меню
```

### Notifications

**To User (Accepted):**
```markdown
✅ Ваша заявка принята!

Детали:
{{about}}

Менеджер свяжется с вами для подтверждения деталей.

📞 Телефон поддержки: +971-XX-XXX-XXXX

Buttons:
- Мои бронирования
- ⬅ Главное меню
```

**To User (Rejected):**
```markdown
❌ К сожалению, заявка отклонена

Возможные причины:
- Нет свободных мест на выбранную дату
- Тур временно недоступен
- Требуется уточнение деталей

Попробуйте выбрать другую дату или свяжитесь с нами:
📞 +971-XX-XXX-XXXX

Buttons:
- Выбрать другую дату
- Связаться с менеджером
- ⬅ Главное меню
```

### Alternative: Google Sheets Instead of NocoDB

If NocoDB is not available, the same structure works with Google Sheets:

```
1. Create Google Sheet with columns:
   user_id | name | about | phone | tour | date | status

2. PuzzleBot Integration:
   Settings > Integrations > Google Sheets

3. Variables:
   Same structure, select "Google Sheets" instead of "NocoDB"
```

### Variables Summary

```python
# User input
about = TEXT(max=1000)  # Booking details from form

# NocoDB integrated (for admin)
get_id = NOCODB_INTEGRATED(column="user_id")
get_name = NOCODB_INTEGRATED(column="name")
get_about = NOCODB_INTEGRATED(column="about")

# Status tracking
booking_status = TEXT(options=["new", "processing", "confirmed", "cancelled"])
```

### Expected Workflow Time

| Step | Time |
|------|------|
| User submits form | 2-3 min |
| Admin receives notification | Instant |
| Admin processes booking | 30 sec |
| User receives result | Instant |
| **Total** | **~3 min** |

### Benefits

- No need to switch between bot and spreadsheet
- Process multiple bookings in sequence
- Automatic removal of processed rows
- Full audit trail in NocoDB/Sheets
- Scalable for multiple admins

---

**Version:** 2.1
**Last Updated:** 2026-02-02
**Forms Documented:** 3 new (REVIEW, TICKETS, BANT) + 2 reference (GT, YACHT) + 1 admin flow (NocoDB)
