# Автоматизация -- Workflow, уведомления, шаблоны

Подробные workflow, шаблоны уведомлений, автоправила, динамическое ценообразование и генерация документов.

---

## Workflow входящего сообщения (развёрнутый)

```
┌─────────────────┐
│  WhatsApp       │
│  Incoming       │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────────────┐
│  Claude AI Classification                    │
│  - type: inquiry/booking/complaint           │
│  - priority: critical/high/medium/low        │
│  - sentiment: positive/neutral/negative      │
└────────────────────┬────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    v                v                v
┌────────┐      ┌────────┐      ┌────────┐
│ Auto   │      │ Notify │      │Escalate│
│ Reply  │      │ Team   │      │ Urgent │
└────────┘      └────────┘      └────────┘
```

---

## Автоматическая генерация документов

```python
# Триггер: оплата получена
trigger = "payment.success"

# Действия:
actions = [
    "generate_voucher_pdf",      # Генерация ваучера с QR-кодом
    "create_calendar_event",     # События в Google Calendar
    "notify_driver",             # Уведомление водителю
    "send_whatsapp_voucher",     # Отправка клиенту
    "update_crm_status"          # Обновление CRM
]
```

---

## Типовые автоответы

```python
AUTO_RULES = [
    {
        'triggers': ['график работы', 'режим работы'],
        'response': 'Мы работаем ежедневно с 9:00 до 22:00 по времени ОАЭ (UTC+4)',
        'confidence_threshold': 0.8
    },
    {
        'triggers': ['способ оплаты', 'как оплатить'],
        'response': 'Способы оплаты: банковский перевод, карты Visa/Mastercard, наличные, USDT',
        'confidence_threshold': 0.85
    },
    {
        'triggers': ['отмена', 'вернуть деньги'],
        'response': 'По вопросам отмены свяжитесь с менеджером: +971-XX-XXX-XXXX',
        'escalate': True
    }
]
```

---

## Telegram уведомления команде

```python
NOTIFICATION_TEMPLATES = {
    'new_lead': """
НОВЫЙ ЗАПРОС

Клиент: {name}
Телефон: {phone}
Страна: {country}
Сообщение: {message}

Score: {score}/100
SLA: ответить до {deadline}
""",
    'complaint': """
ЖАЛОБА!

{name}
{phone}
{message}

Требуется немедленная реакция!
"""
}
```

---

## Ежедневный отчёт

```
ЕЖЕДНЕВНЫЙ ОТЧЁТ | {date}
═══════════════════════════════════
ЛИДЫ
• Новых: 23 (+15% к вчера)
• Конверсия в бронь: 8 (35%)

ФИНАНСЫ
• Выручка: $3,450
• Средний чек: $431

ЗАВТРА
• Туров: 12, Клиентов: 47

ВНИМАНИЕ
• 2 неотвеченных запроса > 2 часов
═══════════════════════════════════
```

---

## Динамическое ценообразование

```python
# Факторы
demand_score = bookings / capacity  # 0-100
time_score = days_to_tour < 3 ? 20 : 0
season_score = is_peak_season ? 30 : 0

# Расчёт
adjustment = (demand_score * 0.4 + time_score * 0.2 + season_score * 0.3) / 100
final_price = base_price * (1 + adjustment * 0.3)  # ±30% max
```

---

## Lead Scoring (развёрнутый)

```
┌─────────────────────────────────────┐
│  Факторы scoring:                   │
│  - dates_confirmed: +25             │
│  - group_size > 4: +20              │
│  - budget_mentioned: +20            │
│  - repeat_client: +15               │
│  - engagement_level: +20            │
└─────────────────────────────────────┘
         │
         v
┌────────┬────────┬────────┐
│  HOT   │  WARM  │  COLD  │
│  >80   │ 40-80  │  <40   │
│Срочно! │Nurture │Рассылка│
└────────┴────────┴────────┘
```

---

## Workflow статусов заказа (развёрнутый)

```
NEW_REQUEST → QUOTED → BOOKED → PAID → CONFIRMED → COMPLETED
     │           │        │                           │
     v           v        v                           v
  EXPIRED    EXPIRED  CANCELLED                   REFUNDED
  (24ч)      (48ч)    (24ч без оплаты)           (если отмена)
```
