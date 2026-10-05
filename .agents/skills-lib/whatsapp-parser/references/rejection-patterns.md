# Паттерны отказов и жалоб

Справочник regex-паттернов для классификации отказов, жалоб, благодарностей, срочных сообщений и ответов менеджеров в WhatsApp-переписке туристического бизнеса.

---

## Зачем это нужно

1. **Анализ причин потерь клиентов** - понимание почему сделка не состоялась
2. **Приоритизация обработки** - срочные жалобы требуют немедленного ответа
3. **Оценка качества сервиса** - соотношение благодарностей к жалобам
4. **Воронка продаж** - отслеживание на каком этапе клиенты уходят
5. **Обучение менеджеров** - выявление паттернов успешных/неуспешных коммуникаций

---

## Паттерны отказов

### По цене (REJECTION_PRICE)

Клиент отказывается из-за стоимости услуги.

```python
REJECTION_PRICE = r'''(?ix)
    (?:
        дорог[оа](?:вато)?|
        слишком\s+дорог|
        не\s+(?:укладываемся|вписываемся)\s+в\s+бюджет|
        цена\s+не\s+устраивает|
        выше\s+бюджета|
        превышает\s+бюджет|
        не\s+потянем
    )
'''
```

**Примеры сообщений:**
- "Дорого"
- "Слишком дорого для нас"
- "Не укладываемся в бюджет"
- "Дороговато"
- "Цена не устраивает"

**Категория:** `REJECTION_PRICE`
**Приоритет:** LOW
**Рекомендуемое действие:** Предложить альтернативу дешевле или скидку

---

### Общий отказ (REJECTION_GENERAL)

Клиент отказывается без указания конкретной причины.

```python
REJECTION_GENERAL = r'''(?ix)
    (?:
        не\s+подходит|
        передумал[иа]?|
        отменя(?:ем|йте)|
        не\s+надо|
        отказываемся|
        уже\s+(?:забронировали|нашли|взяли)|
        нашли\s+(?:дешевле|другое|альтернативу)|
        в\s+друго[йм]\s+мест[ео]
    )
'''
```

**Примеры сообщений:**
- "Не подходит"
- "Передумали"
- "Отменяем"
- "Не надо"
- "Уже забронировали в другом месте"
- "Нашли дешевле"

**Категория:** `REJECTION_GENERAL`
**Приоритет:** LOW

---

### Отказ по датам (REJECTION_DATE)

Клиент отказывается из-за несовпадения дат.

```python
REJECTION_DATE = r'''(?ix)
    (?:
        дат[аы]\s+не\s+подход[яи]т|
        не\s+успеваем|
        улетаем\s+раньше|
        в\s+эти\s+дат[аы]\s+не\s+(?:можем|получится)|
        не\s+совпадает\s+(?:по\s+)?дат[ам]|
        расписание\s+не\s+подходит
    )
'''
```

**Примеры сообщений:**
- "Даты не подходят"
- "Не успеваем"
- "Улетаем раньше"
- "В эти даты не можем"

**Категория:** `REJECTION_DATE`
**Приоритет:** LOW

---

### Отложенное решение (DELAYED_DECISION)

Клиент откладывает решение на потом.

```python
DELAYED_DECISION = r'''(?ix)
    (?:
        подумаю|
        подумаем|
        перезвон[юи]|
        напишу\s*позже|
        посоветуюсь|
        позже\s+(?:напишу|скажу|отвечу)|
        нужно\s+(?:подумать|посоветоваться)|
        (?:дай|дайте)\s+время|
        ещё\s+не\s+решил[иа]?|
        пока\s+не\s+знаю|
        отложим|
        (?:в\s+)?другой\s+раз
    )
'''
```

**Примеры сообщений:**
- "Подумаю"
- "Перезвоню"
- "Напишу позже"
- "Посоветуюсь с женой"
- "Дайте время подумать"
- "Ещё не решили"

**Категория:** `DELAYED_DECISION`
**Приоритет:** MEDIUM
**Рекомендуемое действие:** Запланировать follow-up через 1-2 дня

---

## Паттерны жалоб

### Сильные жалобы (COMPLAINT_SEVERE)

Требуют немедленной реакции - клиент очень недоволен.

```python
COMPLAINT_SEVERE = r'''(?ix)
    (?:
        обман(?:ули)?|
        мошенник|
        кошмар|
        безобразие|
        ужасно|
        отвратительно|
        возмущ[её]н|
        немедленно\s+(?:верните|требую)|
        буду\s+жаловаться|
        напишу\s+(?:отзыв|в\s+суд)|
        это\s+(?:обман|грабёж)
    )
'''
```

**Примеры сообщений:**
- "Обманули!"
- "Это мошенники!"
- "Кошмар, ужасный сервис!"
- "Безобразие, немедленно верните деньги!"
- "Буду жаловаться в Роспотребнадзор"

**Категория:** `COMPLAINT_SEVERE`
**Приоритет:** CRITICAL
**Время ответа:** < 5 минут

---

### Средние жалобы (COMPLAINT_MEDIUM)

Клиент недоволен, но настроен на диалог.

```python
COMPLAINT_MEDIUM = r'''(?ix)
    (?:
        не\s+понравил(?:ось|ась)|
        (?:гид|водитель|сервис)\s+(?:был[аи]?\s+)?(?:плох\w+)|
        не\s+соответствует\s+описанию|
        разочарован[аы]?|
        жалоба|
        претензия|
        недовол[ьн]
    )
'''
```

**Примеры сообщений:**
- "Экскурсия не понравилась"
- "Гид был плохой"
- "Не соответствует описанию"
- "Разочарованы сервисом"
- "У меня претензия"

**Категория:** `COMPLAINT_MEDIUM`
**Приоритет:** HIGH
**Время ответа:** < 30 минут

---

### Слабые жалобы (COMPLAINT_LIGHT)

Замечания и мелкие претензии.

```python
COMPLAINT_LIGHT = r'''(?ix)
    (?:
        могло\s+бы\s+быть\s+лучше|
        немного\s+(?:не\s+то|разочарован)|
        мелкие\s+недочёты|
        было\s+бы\s+(?:неплохо|лучше)|
        пожелание|
        замечание|
        не\s+критично[,\s]+но
    )
'''
```

**Примеры сообщений:**
- "Могло бы быть лучше"
- "Немного не то, что ожидали"
- "Есть мелкие недочёты"
- "Было бы неплохо улучшить..."
- "Не критично, но..."

**Категория:** `COMPLAINT_LIGHT`
**Приоритет:** LOW
**Время ответа:** < 24 часа

---

### Проблемы с водителем/трансфером (PROBLEM_DRIVER)

Срочные проблемы, требующие немедленного решения.

```python
PROBLEM_DRIVER = r'''(?ix)
    (?:
        водитель\s+(?:не\s+приехал|опаздывает|не\s+отвечает)|
        где\s+водитель|
        машина\s+не\s+(?:приехала|пришла)|
        никто\s+не\s+(?:встретил|приехал)|
        опаздыва(?:ет|ют)\s+(?:уже\s+)?(?P<minutes>\d+)?
    )
'''
```

**Примеры сообщений:**
- "Водитель не приехал"
- "Где водитель??"
- "Опаздывает уже 20 минут"
- "Машина не пришла"
- "Никто не встретил"

**Категория:** `PROBLEM_DRIVER`
**Приоритет:** CRITICAL
**Время ответа:** < 5 минут

---

### Запрос возврата (PROBLEM_REFUND)

Клиент хочет вернуть деньги.

```python
PROBLEM_REFUND = r'''(?ix)
    (?:
        (?:хочу|можно)\s+вернуть\s+(?:деньги|оплату)|
        возврат(?:\s+возможен)?|
        верните\s+(?:деньги|оплату)|
        отмена\s+с\s+возвратом|
        refund
    )
'''
```

**Примеры сообщений:**
- "Хочу вернуть деньги"
- "Возврат возможен?"
- "Верните оплату"
- "Отмена с возвратом"

**Категория:** `PROBLEM_REFUND`
**Приоритет:** HIGH
**Время ответа:** < 1 час

---

## Паттерны благодарности (GRATITUDE)

### Сильная благодарность

```python
GRATITUDE_STRONG = r'''(?ix)
    (?:
        спасибо\s+(?:большое|огромное|вам)|
        благодар(?:им|ю|ны)|
        очень\s+(?:понравилось|доволен|рады)|
        рекоменду(?:ем|ю)|
        5\s*(?:звёзд|баллов|\+)|
        обязательно\s+(?:вернёмся|обратимся)|
        лучший\s+(?:сервис|тур|экскурсия)
    )
'''
```

**Примеры сообщений:**
- "Спасибо большое!"
- "Огромное спасибо, всё было супер!"
- "Очень понравилось, рекомендуем!"
- "5 звёзд, обязательно вернёмся!"

---

### Обычная благодарность

```python
GRATITUDE_NORMAL = r'''(?ix)
    (?:
        спасибо|
        (?:всё\s+)?супер|
        (?:очень\s+)?понравил(?:ось|ась)|
        отличн(?:о|ый)|
        класс(?:но)?|
        молодцы|
        хорошо|
        здорово|
        круто
    )
'''
```

**Примеры сообщений:**
- "Спасибо"
- "Всё супер"
- "Понравилось"
- "Отлично!"
- "Класс"

**Категория:** `GRATITUDE`
**Приоритет:** LOW
**Рекомендуемое действие:** Запросить отзыв/фото

---

## Паттерны срочности (URGENCY)

### Критическая срочность

```python
URGENCY_CRITICAL = r'''(?ix)
    (?:
        срочно|
        urgent|
        asap|
        немедленно|
        экстренно|
        sos|
        помогите
    )
'''

# Индикаторы критической срочности
URGENCY_INDICATORS = [
    r'!!!+',           # Много восклицательных знаков
    r'СРОЧНО',         # Капс
    r'[🚨🔴⚠️❗‼️]'    # Emoji срочности
]
```

**Примеры сообщений:**
- "СРОЧНО!!!"
- "Urgent! Need help now"
- "SOS, помогите!"
- "Немедленно перезвоните!"

**Категория:** `URGENCY_CRITICAL`
**Приоритет:** CRITICAL
**Время ответа:** < 5 минут

---

### Высокая срочность

```python
URGENCY_HIGH = r'''(?ix)
    (?:
        быстро|быстрее|
        скорее|
        сегодня\s*(?:же|обязательно)|
        как\s*можно\s*скорее|
        очень\s*нужно|
        прямо\s*сейчас
    )
'''
```

**Примеры сообщений:**
- "Нужно быстро решить"
- "Сегодня же, пожалуйста"
- "Как можно скорее"
- "Очень нужно!"

**Категория:** `URGENCY_HIGH`
**Приоритет:** HIGH
**Время ответа:** < 15 минут

---

### Нормальная / Низкая срочность

```python
URGENCY_NORMAL = r'''(?ix)
    (?:
        когда\s*будет\s*удобно|
        не\s*срочно|
        без\s*спешки
    )
'''

URGENCY_LOW = r'''(?ix)
    (?:
        когда[-\s]нибудь|
        если\s*будет\s*время|
        не\s*горит
    )
'''
```

---

## Классификация интентов

### Функция classify_message_intent()

```python
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class MessageIntent(Enum):
    # Запросы клиента
    INQUIRY_PRICE = 'inquiry_price'
    INQUIRY_AVAILABILITY = 'inquiry_availability'
    INQUIRY_INFO = 'inquiry_info'

    # Подтверждения
    CONFIRMATION_BOOKING = 'confirmation_booking'
    CONFIRMATION_PAYMENT = 'confirmation_payment'

    # Отказы
    REJECTION_PRICE = 'rejection_price'
    REJECTION_GENERAL = 'rejection_general'
    REJECTION_DATE = 'rejection_date'
    DELAYED_DECISION = 'delayed_decision'

    # Переговоры
    NEGOTIATION_DISCOUNT = 'negotiation_discount'
    NEGOTIATION_GROUP = 'negotiation_group'

    # Проблемы
    PROBLEM_DRIVER = 'problem_driver'
    PROBLEM_BOOKING = 'problem_booking'
    PROBLEM_REFUND = 'problem_refund'
    COMPLAINT = 'complaint'

    # Позитивные
    GRATITUDE = 'gratitude'
    FOLLOWUP_POSITIVE = 'followup_positive'

    # Служебные
    URGENCY = 'urgency'
    UNKNOWN = 'unknown'

@dataclass
class IntentResult:
    intent: MessageIntent
    confidence: float
    priority: str
    matched_pattern: str
    requires_action: bool

# Паттерны с приоритетами
INTENT_PATTERNS = {
    MessageIntent.PROBLEM_DRIVER: {
        'patterns': [
            r'(?i)водитель\s+не|где\s+водитель|машина\s+не',
        ],
        'priority': 'CRITICAL',
        'requires_action': True,
    },
    MessageIntent.COMPLAINT: {
        'patterns': [
            r'(?i)обман|мошенник|кошмар|безобразие|ужасно|жалоба',
        ],
        'priority': 'HIGH',
        'requires_action': True,
    },
    MessageIntent.PROBLEM_REFUND: {
        'patterns': [
            r'(?i)вернуть\s+деньги|возврат|верните',
        ],
        'priority': 'HIGH',
        'requires_action': True,
    },
    MessageIntent.CONFIRMATION_BOOKING: {
        'patterns': [
            r'(?i)брон(?:ирую|ируем|ь)|подтвержда[юе]|бер[уём]|давайте.*брон',
        ],
        'priority': 'HIGH',
        'requires_action': True,
    },
    MessageIntent.CONFIRMATION_PAYMENT: {
        'patterns': [
            r'(?i)оплатил|перев[её]л|скинул|деньги\s+отправил',
        ],
        'priority': 'HIGH',
        'requires_action': True,
    },
    MessageIntent.INQUIRY_PRICE: {
        'patterns': [
            r'(?i)скольк[оа]\s+сто[ия]т|как[ая]+\s+цен[ау]|поч[её]м|цен[ау]\s+на',
        ],
        'priority': 'MEDIUM',
        'requires_action': True,
    },
    MessageIntent.REJECTION_PRICE: {
        'patterns': [
            r'(?i)дорог[оа]|не\s+укладываемся|цена\s+не\s+устраивает',
        ],
        'priority': 'LOW',
        'requires_action': False,
    },
    MessageIntent.DELAYED_DECISION: {
        'patterns': [
            r'(?i)подумаю|подумаем|напишу\s+позже|посоветуюсь',
        ],
        'priority': 'MEDIUM',
        'requires_action': True,
    },
    MessageIntent.GRATITUDE: {
        'patterns': [
            r'(?i)спасибо|благодар|супер|понравил|рекоменду',
        ],
        'priority': 'LOW',
        'requires_action': False,
    },
}

def classify_message_intent(text: str) -> IntentResult:
    """
    Классифицирует сообщение и возвращает определённый интент.

    Args:
        text: Текст сообщения

    Returns:
        IntentResult с определённым интентом, confidence и приоритетом
    """
    text = text.strip()

    # Проверка срочности (добавляет приоритет к любому интенту)
    is_urgent = bool(re.search(r'(?i)срочно|urgent|asap|!!!', text))

    # Проходим по паттернам в порядке приоритета
    for intent, config in INTENT_PATTERNS.items():
        for pattern in config['patterns']:
            match = re.search(pattern, text)
            if match:
                priority = config['priority']

                # Повышаем приоритет если срочно
                if is_urgent and priority != 'CRITICAL':
                    priority = 'HIGH' if priority == 'MEDIUM' else 'MEDIUM'

                # Рассчитываем confidence
                match_ratio = len(match.group()) / len(text)
                confidence = min(0.95, 0.6 + match_ratio * 0.4)

                return IntentResult(
                    intent=intent,
                    confidence=confidence,
                    priority=priority,
                    matched_pattern=pattern,
                    requires_action=config['requires_action']
                )

    return IntentResult(
        intent=MessageIntent.UNKNOWN,
        confidence=0.5,
        priority='LOW',
        matched_pattern='',
        requires_action=False
    )


def classify_multiple_intents(text: str) -> List[IntentResult]:
    """
    Возвращает все обнаруженные интенты (для сложных сообщений).
    """
    results = []

    for intent, config in INTENT_PATTERNS.items():
        for pattern in config['patterns']:
            match = re.search(pattern, text)
            if match:
                match_ratio = len(match.group()) / len(text)
                confidence = min(0.95, 0.6 + match_ratio * 0.4)

                results.append(IntentResult(
                    intent=intent,
                    confidence=confidence,
                    priority=config['priority'],
                    matched_pattern=pattern,
                    requires_action=config['requires_action']
                ))
                break

    # Сортируем по приоритету и confidence
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    results.sort(key=lambda x: (priority_order.get(x.priority, 4), -x.confidence))

    return results
```

---

## Бизнес-паттерны (ответы менеджера)

### Паттерны для определения сообщений менеджера

```python
# Признаки сообщений от агента/менеджера
AGENT_MESSAGE_PATTERNS = [
    r'мои?\s+клиент',
    r'my\s+client',
    r'направляю\s+(?:вам\s+)?клиент',
    r'sending\s+(?:you\s+)?(?:a\s+)?client',
    r'бронирую\s+для',
    r'booking\s+for',
]
```

---

### PRICE_QUOTE - Ответ менеджера с ценой

```python
PRICE_QUOTE = r'''(?ix)
    (?:
        стоимость\s+(?:составляет|будет|равна)|
        цена\s+(?:на|для|за)\s+|
        (?:будет\s+)?(?:стоить|обойдётся)\s+|
        итого[:\s]+|
        total[:\s]+|
        price[:\s]+|
        \d+\s*(?:[$€₽]|AED|дирхам|USD|RUB)\s*(?:с\s+человека|на\s+\d+|за\s+\w+)
    )
'''
```

**Примеры:**
- "Стоимость составляет 500 AED"
- "Цена на сафари: 300$ с человека"
- "Итого: 1500 дирхам за 4 человек"

**Категория:** `PRICE_QUOTE`
**Отправитель:** Менеджер

---

### BOOKING_CONFIRMATION - Подтверждение бронирования от менеджера

```python
BOOKING_CONFIRMATION_AGENT = r'''(?ix)
    (?:
        бронь\s+подтвержден[аы]?|
        бронирование\s+(?:подтверждено|оформлено|создано)|
        забронировано|
        ваучер\s+(?:во\s+вложении|прилагается|отправлен)|
        confirmed|
        booking\s+(?:confirmed|created)|
        подтверждаем\s+(?:вашу\s+)?(?:бронь|бронирование)|
        ваша\s+бронь\s+№
    )
'''
```

**Примеры:**
- "Бронь подтверждена! Ваучер во вложении"
- "Бронирование оформлено, номер заказа: 12345"
- "Confirmed! Your booking #ABC123"
- "Подтверждаем вашу бронь на 15 января"

**Категория:** `BOOKING_CONFIRMATION_AGENT`
**Отправитель:** Менеджер

---

### PAYMENT_REQUEST - Запрос оплаты от менеджера

```python
PAYMENT_REQUEST_AGENT = r'''(?ix)
    (?:
        реквизиты\s+для\s+оплаты|
        для\s+оплаты\s+(?:используйте|переведите)|
        оплатить\s+(?:можно|нужно)|
        ожидаем\s+(?:оплату|платёж)|
        (?:карта|счёт|IBAN)[:\s]+|
        payment\s+details|
        к\s+оплате[:\s]+|
        total[:\s]+\d+
    )
'''
```

**Примеры:**
- "Реквизиты для оплаты: Карта 4276..."
- "К оплате: 500 AED"
- "Ожидаем оплату до 12:00"

---

### INFO_RESPONSE - Информационный ответ менеджера

```python
INFO_RESPONSE = r'''(?ix)
    (?:
        в\s+стоимость\s+(?:входит|включено)|
        программа\s+(?:тура|экскурсии)|
        включает[:\s]|
        includes[:\s]|
        длительность[:\s]|
        duration[:\s]|
        выезд\s+в\s+\d{1,2}[:.]\d{2}|
        pick[\s-]?up\s+at|
        дополнительно\s+можно|
        также\s+доступно
    )
'''
```

**Примеры:**
- "В стоимость входит: трансфер, обед, гид"
- "Программа тура: выезд в 8:00, возвращение в 18:00"
- "Длительность: 6 часов"

---

## Сводная таблица категорий

| Категория | Приоритет | Требует ответа | Время ответа |
|-----------|-----------|----------------|--------------|
| `PROBLEM_DRIVER` | CRITICAL | Да | < 5 мин |
| `COMPLAINT_SEVERE` | CRITICAL | Да | < 5 мин |
| `URGENCY_CRITICAL` | CRITICAL | Да | < 5 мин |
| `PROBLEM_REFUND` | HIGH | Да | < 1 час |
| `PROBLEM_BOOKING` | HIGH | Да | < 30 мин |
| `COMPLAINT_MEDIUM` | HIGH | Да | < 30 мин |
| `CONFIRMATION_PAYMENT` | HIGH | Да | < 15 мин |
| `CONFIRMATION_BOOKING` | HIGH | Да | < 15 мин |
| `DELAYED_DECISION` | MEDIUM | Follow-up | 1-2 дня |
| `REJECTION_PRICE` | LOW | Опционально | - |
| `REJECTION_GENERAL` | LOW | Опционально | - |
| `REJECTION_DATE` | LOW | Опционально | - |
| `GRATITUDE` | LOW | Опционально | < 24 часа |
| `COMPLAINT_LIGHT` | LOW | Опционально | < 24 часа |

---

## Примеры использования

### Базовый парсер

```python
def analyze_customer_feedback(messages: list) -> dict:
    """
    Анализ обратной связи от клиентов.

    Returns:
        Статистика по категориям сообщений
    """
    stats = {
        'total': len(messages),
        'complaints': {'severe': 0, 'medium': 0, 'light': 0},
        'rejections': {'price': 0, 'date': 0, 'general': 0, 'delayed': 0},
        'gratitude': 0,
        'urgent': 0,
    }

    for msg in messages:
        text = msg['text']

        # Жалобы
        if re.search(COMPLAINT_SEVERE, text):
            stats['complaints']['severe'] += 1
        elif re.search(COMPLAINT_MEDIUM, text):
            stats['complaints']['medium'] += 1
        elif re.search(COMPLAINT_LIGHT, text):
            stats['complaints']['light'] += 1

        # Отказы
        if re.search(REJECTION_PRICE, text):
            stats['rejections']['price'] += 1
        elif re.search(REJECTION_DATE, text):
            stats['rejections']['date'] += 1
        elif re.search(DELAYED_DECISION, text):
            stats['rejections']['delayed'] += 1
        elif re.search(REJECTION_GENERAL, text):
            stats['rejections']['general'] += 1

        # Благодарности
        if re.search(GRATITUDE_STRONG, text) or re.search(GRATITUDE_NORMAL, text):
            stats['gratitude'] += 1

        # Срочность
        if re.search(URGENCY_CRITICAL, text):
            stats['urgent'] += 1

    return stats
```

### Приоритизация сообщений

```python
def prioritize_messages(messages: list) -> list:
    """
    Сортировка сообщений по приоритету для обработки.
    """
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}

    for msg in messages:
        result = classify_message_intent(msg['text'])
        msg['intent'] = result.intent.value
        msg['priority'] = result.priority
        msg['requires_action'] = result.requires_action

    # Сортируем: критические первые, потом по времени
    return sorted(
        messages,
        key=lambda m: (
            priority_order.get(m['priority'], 4),
            m['timestamp']
        )
    )
```

---

## Связанные файлы

- [funnel-patterns.md](./funnel-patterns.md) - Паттерны воронки продаж
- [quality-metrics.md](./quality-metrics.md) - Метрики качества обслуживания
- [regex-cheatsheet.md](./regex-cheatsheet.md) - Шпаргалка по regex
- [entities-dictionary.md](./entities-dictionary.md) - Словарь сущностей

---

*Справочник паттернов для анализа WhatsApp-переписки туристического бизнеса ОАЭ*
