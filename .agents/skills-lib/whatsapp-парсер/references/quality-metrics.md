# Метрики качества обслуживания

Документация по оценке качества обслуживания клиентов на основе анализа WhatsApp-переписки.

---

## 1. Метрики времени ответа

### FRT (First Response Time) - Время первого ответа

**Формула:**
```
FRT = timestamp_первого_ответа_менеджера - timestamp_первого_сообщения_клиента
```

**Измерение:** минуты

**Пример расчета:**
```python
def calculate_first_response_time(messages):
    """
    Находит время от первого сообщения клиента до первого ответа менеджера
    """
    client_first = None
    manager_first = None

    for msg in messages:
        if msg['sender_type'] == 'client' and client_first is None:
            client_first = msg['timestamp']
        elif msg['sender_type'] == 'manager' and client_first and manager_first is None:
            manager_first = msg['timestamp']
            break

    if client_first and manager_first:
        return (manager_first - client_first).total_seconds() / 60
    return None
```

---

### ART (Average Response Time) - Среднее время ответа

**Формула:**
```
ART = SUM(время_ответа_i) / COUNT(ответы)
```

**Пример расчета:**
```python
def calculate_avg_response_time(messages, sender_type='manager'):
    """
    Среднее время ответа указанного типа отправителя
    """
    response_times = []
    last_other_msg = None

    for msg in messages:
        if msg['sender_type'] != sender_type:
            last_other_msg = msg['timestamp']
        elif last_other_msg:
            delta = (msg['timestamp'] - last_other_msg).total_seconds() / 60
            response_times.append(delta)
            last_other_msg = None

    return sum(response_times) / len(response_times) if response_times else 0
```

---

### SLA пороги

| Метрика | SLA цель | Warning | Critical |
|---------|----------|---------|----------|
| First Response Time | < 15 мин | 15-30 мин | > 30 мин |
| Regular Response | < 60 мин | 60-120 мин | > 120 мин |
| Urgent Response | < 5 мин | 5-15 мин | > 15 мин |
| Non-working hours | < 4 часа | 4-8 часов | > 8 часов |

**Рабочие часы:**
- Начало: 09:00
- Конец: 21:00
- Часовой пояс: GST (UTC+4)

---

### JSON структура метрик времени

```json
{
  "response_time_metrics": {
    "first_response_time_minutes": 12.5,
    "average_response_time_minutes": 45.3,
    "max_response_time_minutes": 180,
    "min_response_time_minutes": 2,
    "median_response_time_minutes": 25,
    "p90_response_time_minutes": 90,
    "sla_violations_count": 3,
    "sla_compliance_percent": 87.5,
    "within_15min_percent": 65.0,
    "within_1hour_percent": 90.0,
    "working_hours_only": true
  }
}
```

---

## 2. Маркеры жалоб

### Strong (Сильные) - Вес: 10

```python
COMPLAINT_MARKERS_STRONG = [
    r'ужасн[оы]й?',
    r'кошмар',
    r'скандал',
    r'обман',
    r'мошенни',
    r'верн[иу]те\s+деньги',
    r'жалоб[ау]',
    r'суд',
    r'юрист',
]
```

**Примеры:**
- "Это ужасный сервис!"
- "Верните мне деньги!"
- "Буду писать жалобу"
- "Обратимся к юристу"

---

### Medium (Средние) - Вес: 5

```python
COMPLAINT_MARKERS_MEDIUM = [
    r'проблем[аы]',
    r'плохо',
    r'недовол[ье]н',
    r'не\s+устраивает',
    r'разочарован',
    r'ошибк[аи]',
    r'не\s+работает',
    r'сломан',
    r'испорчен',
]
```

**Примеры:**
- "У нас проблема с бронированием"
- "Качество плохое"
- "Меня это не устраивает"
- "Очень разочарован сервисом"

---

### Weak (Слабые) - Вес: 2

```python
COMPLAINT_MARKERS_WEAK = [
    r'не\s+понял',
    r'не\s+ясно',
    r'запутал',
    r'долго\s+ждать',
    r'где\s+мой',
    r'почему\s+так\s+долго',
    r'когда\s+уже',
]
```

**Примеры:**
- "Не понял, когда пикап?"
- "Долго ждём ответа"
- "Где мой ваучер?"
- "Почему так долго отвечаете?"

---

### Единый regex для всех жалоб

```regex
(?i)(ужасн|кошмар|скандал|обман|мошенни|верн[иу]те\s+деньги|жалоб|проблем|плохо|недовол|не\s+устраивает|разочарован|ошибк|не\s+работает|сломан|испорчен)
```

---

### Формула Complaint Score

```
Complaint_Score = SUM(count_strong * 10 + count_medium * 5 + count_weak * 2)
Max = 100
```

```python
def calculate_complaint_score(complaints):
    """
    Рассчитывает общий балл жалоб (0-100, где 0 = нет жалоб)
    """
    weights = {'strong': 10, 'medium': 5, 'weak': 2}
    total_score = sum(weights[c['severity']] for c in complaints)
    return min(total_score, 100)
```

---

## 3. Позитивные маркеры

### Gratitude (Благодарность)

```python
POSITIVE_GRATITUDE = [
    r'спасибо',
    r'благодар',
    r'thank',
    r'признателен',
]
```

### Satisfaction (Удовлетворение)

```python
POSITIVE_SATISFACTION = [
    r'отлично',
    r'замечательно',
    r'прекрасно',
    r'супер',
    r'класс',
    r'великолепно',
    r'идеально',
    r'perfect',
    r'excellent',
]
```

### Recommendation (Рекомендация)

```python
POSITIVE_RECOMMENDATION = [
    r'рекомендую',
    r'посоветую',
    r'расскажу\s+друзьям',
    r'порекоменд',
]
```

### Loyalty (Лояльность)

```python
POSITIVE_LOYALTY = [
    r'обращусь\s+ещё',
    r'вернусь',
    r'буду\s+работать\s+с\s+вами',
    r'постоянн\w*\s+клиент',
]
```

---

### Единый regex позитивных маркеров

```regex
(?i)(спасибо|благодар|отлично|замечательно|прекрасно|супер|класс|рекомендую|посоветую|обращусь\s+ещё|вернусь)
```

---

### Формула Satisfaction Score

```python
def calculate_satisfaction_score(messages):
    """
    Рассчитывает индекс удовлетворённости (0-100)
    """
    positive_count = 0
    negative_count = 0

    for msg in messages:
        if msg['sender_type'] == 'client':
            positive_count += len(re.findall(POSITIVE_PATTERN, msg['text'], re.I))
            negative_count += len(re.findall(NEGATIVE_PATTERN, msg['text'], re.I))

    total = positive_count + negative_count
    if total == 0:
        return 50  # Нейтрально

    return int((positive_count / total) * 100)
```

---

## 4. Грейды качества

### Шкала грейдов

| Балл | Грейд | Описание | Действие |
|------|-------|----------|----------|
| 90-100 | A+ | Превосходное обслуживание | Похвала, бонус |
| 85-89 | A | Отличное обслуживание | Поддержание уровня |
| 80-84 | A- | Очень хорошее обслуживание | Мониторинг |
| 75-79 | B+ | Хорошее обслуживание | Мелкие улучшения |
| 70-74 | B | Удовлетворительное обслуживание | Коучинг |
| 65-69 | B- | Приемлемое обслуживание | Обучение |
| 60-64 | C | Требует улучшения | Срочные меры |
| < 60 | D | Критические проблемы | Эскалация |

---

### Формула общего индекса качества

```
Quality_Score = (
    Response_Score * 0.25 +
    Conversion_Score * 0.25 +
    Problem_Score * 0.20 +
    Satisfaction_Score * 0.30
)
```

**Компоненты:**

```
Response_Score = 100 - (avg_response_time / SLA_target * 50)
    - SLA_target = 60 мин для обычных сообщений
    - Максимум 100, минимум 0

Conversion_Score = (conversion_rate / benchmark_rate) * 100
    - benchmark_rate = 0.20 (20% общая конверсия)
    - Максимум 100

Problem_Score = 100 - complaint_score
    - complaint_score из расчета маркеров жалоб

Satisfaction_Score = из формулы выше
```

---

### JSON структура качества

```json
{
  "quality_metrics": {
    "chat_id": "chat_12345",
    "analysis_date": "2025-01-26",
    "period": "2025-01-01 to 2025-01-26",

    "response_time": {
      "first_response_minutes": 12.5,
      "average_response_minutes": 45.3,
      "sla_compliance_percent": 87.5,
      "response_score": 85
    },

    "conversion": {
      "messages_to_booking": 15,
      "days_to_payment": 2,
      "benchmark_rating": "good",
      "conversion_score": 78
    },

    "problems": {
      "complaint_score": 25,
      "escalations": 0,
      "repeated_questions": 2,
      "risk_level": "medium",
      "problem_score": 75
    },

    "satisfaction": {
      "score": 78,
      "positive_signals": 12,
      "negative_signals": 3,
      "repeat_order": true,
      "referral": true,
      "nps_category": "promoter"
    },

    "overall_quality_score": 82,
    "quality_grade": "A-"
  }
}
```

---

## 5. Метрики менеджера

### Показатели эффективности

| Метрика | Формула | Бенчмарк |
|---------|---------|----------|
| Обработано чатов | count(assigned_chats) | 4-5/день |
| Конверсия | bookings / inquiries * 100 | > 25% |
| Среднее время ответа | avg(response_times) | < 15 мин |
| SLA соблюдение | sla_met / total_responses * 100 | > 90% |
| Удовлетворенность | avg(satisfaction_scores) | > 80 |
| Жалобы | count(complaints) | < 3/месяц |

---

### JSON структура метрик менеджера

```json
{
  "manager_metrics": {
    "manager_name": "Мария",
    "period": "2025-01",
    "chats_handled": 145,
    "chats_per_day": 4.8,
    "total_messages_sent": 1250,
    "conversion_rate": 35.2,
    "avg_response_time_minutes": 12.5,
    "sla_compliance_percent": 92,
    "satisfaction_score": 82,
    "complaints_received": 3,
    "quality_grade": "A-",
    "ranking": 2
  }
}
```

---

## 6. Бенчмарки по длительности диалога

### Messages to Booking

| Рейтинг | Сообщений | Дней до оплаты | FRT (мин) |
|---------|-----------|----------------|-----------|
| Excellent | <= 10 | <= 1 | <= 5 |
| Good | <= 20 | <= 3 | <= 15 |
| Acceptable | <= 35 | <= 7 | <= 60 |
| Poor | > 50 | > 14 | > 180 |

---

### JSON структура длительности

```json
{
  "duration_metrics": {
    "messages_to_booking": 15,
    "client_messages_to_booking": 8,
    "manager_messages_to_booking": 7,
    "days_inquiry_to_payment": 2,
    "hours_inquiry_to_payment": 52,
    "benchmark_rating": "good",
    "comparison_to_average": "+15%"
  }
}
```

---

## 7. Индикаторы проблем

### Эскалация

```python
ESCALATION_MARKERS = [
    r'руководител',
    r'директор',
    r'начальни[кц]',
    r'главн',
    r'старши[йм]',
    r'ответственн',
    r'кто\s+главный',
    r'позови[те]?\s+\w+',
    r'хочу\s+говорить\s+с',
    r'передай[те]?',
]
```

### Повторные вопросы

```python
TOPIC_PATTERNS = {
    'price': r'(сколько|цена|стоимость|прайс)',
    'availability': r'(есть|свобод|доступн)',
    'payment': r'(оплат|перевод|деньги|реквизит)',
    'booking': r'(бронь|бронирован|забронировать)',
    'status': r'(статус|где|когда|как дела)',
}
```

---

### JSON структура проблем

```json
{
  "problem_indicators": {
    "complaint_score": 25,
    "complaints_count": {
      "strong": 0,
      "medium": 3,
      "weak": 5
    },
    "repeated_questions_count": 2,
    "repeated_topics": ["payment", "status"],
    "escalations_count": 0,
    "risk_level": "medium",
    "requires_attention": true
  }
}
```

---

## 8. NPS категории

| Категория | Условие | Описание |
|-----------|---------|----------|
| Promoter | satisfaction >= 80 + (referral OR repeat) | Рекомендует, возвращается |
| Passive | satisfaction 60-79 | Нейтральный |
| Detractor | satisfaction < 60 OR complaints > 0 | Недоволен |

---

## 9. Потерянные клиенты (Churn)

### Признаки ухода

```python
CHURN_SIGNALS = {
    'client_silence': {
        'days_inactive': 3,  # дней без ответа
        'after_manager_message': True
    },
    'price_objection': {
        'pattern': r'(цена|стоимость|сколько)',
        'followed_by_silence': True
    },
    'explicit_refusal': {
        'patterns': [
            r'передумал',
            r'нашёл\s+другой',
            r'дорого',
            r'не\s+подходит',
            r'отменяю',
            r'уже\s+забронировал\s+в\s+другом'
        ]
    }
}
```

### Причины отказа

| Причина | Паттерны | Потенциал восстановления |
|---------|----------|-------------------------|
| Цена | `дорого, бюджет, дешевле` | 35% - предложить скидку |
| Даты | `не успеваем, планы` | 45% - предложить гибкость |
| Конкурент | `нашли другой, забронировали` | 10% - запросить фидбек |
| Сервис | `долго, не понравилось` | 25% - извинение + компенсация |
| Передумал | `отменяем поездку` | 5% - связаться позже |

---

### JSON структура churn

```json
{
  "churn_metrics": {
    "total_lost_leads": 45,
    "reasons_breakdown": {
      "price": 18,
      "timing": 12,
      "competitor": 8,
      "service": 4,
      "changed_mind": 3
    },
    "recovery_potential": {
      "high": 12,
      "medium": 18,
      "low": 15
    },
    "average_days_to_churn": 4.2,
    "churn_rate_percent": 15.5,
    "recoverable_revenue_estimate": 125000
  }
}
```

---

*Документ: quality-metrics.md*
*Версия: 1.0*
*Создан: Январь 2025*
