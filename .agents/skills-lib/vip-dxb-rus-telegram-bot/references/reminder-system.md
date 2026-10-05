# Smart Reminder System — Полная реализация

**Источник:** SKILL.md v2.3, перенесено для экономии места

---

## 4 типа напоминаний (Based on proven scenarios)

### 1. Before Flight (24 hours)
```markdown
Завтра ваш рейс в Дубай!

Проверьте:
✅ Документы (паспорт, виза)
✅ Страховку
✅ Валюту (AED или USD)
✅ Бронирования отелей
✅ Список экскурсий

Удачного полета! 🛫

Variables:
- {{flight_date}}
- {{flight_time}}
- {{flight_number}}
```

### 2. After Booking (3 days)
```markdown
Спасибо за бронирование!

Напоминаем оформить:
📋 Визу в ОАЭ (если ещё не сделали)
💊 Страховку (рекомендуем)
💳 Международную карту

Нужна помощь? Пишите в поддержку!

Variables:
- {{booking_date}}
- {{tour_name}}
```

### 3. Before Tour (2 days)
```markdown
Напоминание об экскурсии!

📅 Дата: {{tour_date}}
🕐 Время: {{tour_time}}
📍 Место встречи: {{pickup_location}}

Что взять с собой:
- Удобная обувь
- Вода
- Солнцезащитный крем
- Камера 📸

До встречи!

Variables:
- {{tour_name}}
- {{tour_date}}
- {{tour_time}}
- {{pickup_location}}
```

### 4. After Return (2 days after tour)
```markdown
Как прошла поездка? 😊

Поделитесь впечатлениями!

За отзыв на Google Maps дарим:
🎁 Скидку 15% на следующую поездку

Buttons:
- ⭐ Оставить отзыв (5 баллов)
- 👍 Всё отлично (4 балла)
- 😐 Средне (3 балла)
- 👎 Плохо (1-2 балла)

Variables:
- {{tour_name}}
- {{tour_date}}
```

---

## Reminder Implementation

**Using Dynamic Categories (Воронка арабского алфавита case):**

1. **Set category on booking:**
```
Action: Change category → "booked_tour_{{tour_id}}"
```

2. **Start timer:**
```
Wait: 2 days
```

3. **Check if still in category:**
```
Condition: Has category "booked_tour_{{tour_id}}"
   Yes → Send reminder
   No → Skip (already took tour)
```

4. **Remove category after tour:**
```
Action: Remove category → "booked_tour_{{tour_id}}"
```

---

## Variables for Reminders

```
reminder_flight_date (date)
reminder_flight_time (time)
reminder_tour_date (date)
reminder_tour_time (time)
reminder_sent_count (number)
reminder_last_sent (datetime)
reminder_responded (boolean)
```

---

## Reminder Block Template

```markdown
# [ID] Reminder: [Type]

**Type:** Automated Reminder
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Reminder headline]

[Details with variables]
{{variable_1}}
{{variable_2}}

[What to do next]
```

---

## Trigger

**Category check:** Has category "{{reminder_category}}"
**Wait time:** [X hours/days] after [event]

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | [Action Button] | [Form/Block] | inline |
| 2 | Напомнить позже | Snooze Logic | inline |
| 3 | ⬅ Назад | Main Menu | inline |

---

## Variables

**Uses (reads):**
- {{reminder_date}}
- {{reminder_time}}
- {{user_name}}

**Sets (writes):**
- {{reminder_sent}} → true
- {{reminder_count}} +1
```

---

## Setting Up Reminders (Workflow)

```flow
1. Identify reminder trigger (booking/tour/etc)
2. Create reminder category (e.g., "booked_tour_123")
3. Assign category on trigger event
4. Create wait block (X hours/days)
5. Create check block (still has category?)
6. Create reminder message
7. Remove category after delivery
8. Test reminder timing
9. Monitor delivery rate
```
