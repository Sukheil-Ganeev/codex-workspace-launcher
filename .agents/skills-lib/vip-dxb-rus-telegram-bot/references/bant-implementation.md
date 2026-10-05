# BANT Customer Qualification — Полная реализация

**Источник:** SKILL.md v2.3, перенесено для экономии места

---

## Что такое BANT?

**B**udget, **A**uthority, **N**eed, **T**imeframe

Квалифицирует лиды как:
- Hot (high budget, <1 month, decision-maker)
- Warm (medium budget, 1-3 months)
- Cold (economy budget, 3+ months)

**Основано на кейсе:** Computer club — 490 bookings, 23% conversion, 683k RUB revenue

---

## Qualification Questions (Подробные блоки)

### 1. Budget (B):
```
Какой у вас бюджет на поездку?

Buttons:
- Эконом (до 500 AED/чел) — 0 points
- Средний (500-1500 AED/чел) — 2 points
- Премиум (1500+ AED/чел) — 3 points
```

### 2. Timeframe (T):
```
Когда планируете поездку?

Buttons:
- Через неделю — 3 points
- Через месяц — 2 points
- Через 3+ месяца — 0 points
```

### 3. Group Size (N):
```
Сколько человек?

Buttons:
- 1-2 человека — 1 point
- 3-5 человек — 2 points
- 6+ человек — 3 points
```

### 4. Authority (A):
```
Кто принимает решение?

Buttons:
- Я сам решаю — 3 points
- Нужно согласовать — 1 point
```

---

## Lead Scoring & Priority

**Total points:**
- **9-11 points** → Hot (notify manager immediately)
- **5-8 points** → Warm (follow up within 2 hours)
- **0-4 points** → Cold (nurture sequence, follow up next day)

---

## Variables for BANT

```
bant_budget (choice: economy/medium/premium)
bant_timeframe (choice: week/month/3months)
bant_group_size (number: 1-99)
bant_authority (choice: self/consult)
bant_score (number: 0-11, calculated)
bant_priority (text: hot/warm/cold)
bant_notes (text) — Additional info
```

---

## Manager Notification

**Hot Lead Alert:**
```
🔥 ГОРЯЧАЯ ЗАЯВКА!

Клиент: {{gt_client_name}}
Телефон: {{gt_client_phone}}
Тур: {{tour_name}}

Бюджет: Премиум
Сроки: Через неделю
Группа: 5 человек
Решение: Сам принимает

Баллы: 11/11
Приоритет: МАКСИМАЛЬНЫЙ

⏰ Обработать в течение 30 минут!
```

---

## BANT Qualification Template (для создания блоков)

```markdown
# [ID] BANT Question: [Budget/Authority/Need/Timeframe]

**Type:** Qualification
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Question text]

[Brief explanation why we ask]
```

---

## Variables

**Uses (reads):** None

**Sets (writes):**
- {{bant_[field]}} — User's answer
- {{bant_score}} — +[points]

---

## Buttons

| # | Button Text | Points | Leads to | Type |
|---|------------|--------|----------|------|
| 1 | [Option 1] | +3 | Next Question | inline |
| 2 | [Option 2] | +2 | Next Question | inline |
| 3 | [Option 3] | +0 | Next Question | inline |

---

## Logic

After 4 questions, calculate:
- 9-11 points → Hot lead → Immediate manager alert
- 5-8 points → Warm lead → 2-hour follow-up
- 0-4 points → Cold lead → Nurture sequence
```

---

## Adding BANT Qualification (Workflow)

```flow
1. Identify high-value service (500+ AED)
2. Create 4 question blocks:
   - Budget (economy/medium/premium)
   - Timeframe (week/month/3months)
   - Group size (1-2/3-5/6+)
   - Authority (self/consult)
3. Assign points to each answer (0-3)
4. Calculate total score (0-11)
5. Set priority:
   - 9-11 → Hot → Immediate alert
   - 5-8 → Warm → 2h follow-up
   - 0-4 → Cold → Nurture sequence
6. Customize manager notifications
7. Test scoring logic
```
