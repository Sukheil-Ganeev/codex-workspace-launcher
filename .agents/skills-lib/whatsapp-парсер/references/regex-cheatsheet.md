# Regex Cheatsheet - Регулярные выражения

## Телефоны

### ОАЭ (+971)
```python
UAE_PHONE = re.compile(r'\+?971\s?5[0-9]\s?\d{3}\s?\d{4}')
# Примеры: +971 50 123 4567, 971501234567, +971-50-123-4567
```

### Россия (+7)
```python
RU_PHONE = re.compile(r'\+?7\s?[\(\-]?\d{3}[\)\-]?\s?\d{3}[\-]?\d{2}[\-]?\d{2}')
# Примеры: +7 (905) 123-45-67, +79051234567, 8-905-123-45-67
```

### Казахстан (+7)
```python
KZ_PHONE = re.compile(r'\+?7\s?7[0-9]{2}\s?\d{3}\s?\d{2}\s?\d{2}')
# Примеры: +7 707 123 45 67, +77071234567
```

### Международный формат (любой)
```python
INTL_PHONE = re.compile(r'\+\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3}[\s\-]?\d{2,4}[\s\-]?\d{0,4}')
# Примеры: +1 (555) 123-4567, +44 20 7123 4567
```

### Универсальный (все форматы)
```python
ANY_PHONE = re.compile(r'''
    (?:\+?\d{1,3})?          # Код страны (опционально)
    [\s\-\.]?                # Разделитель
    \(?\d{2,4}\)?            # Код города/оператора
    [\s\-\.]?
    \d{3}
    [\s\-\.]?
    \d{2}
    [\s\-\.]?
    \d{2}
''', re.VERBOSE)
```

---

## Банковские данные

### IBAN (ОАЭ)
```python
UAE_IBAN = re.compile(r'AE\d{21}')
# Пример: AE070331234567890123456
```

### IBAN (международный)
```python
IBAN = re.compile(r'[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}')
# Примеры: DE89370400440532013000, GB82WEST12345698765432
```

### Банковская карта (16 цифр)
```python
CARD_16 = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')
# Примеры: 4276 1234 5678 9012, 4276-1234-5678-9012, 4276123456789012
```

### Карта с валидацией (Visa/Mastercard/Mir)
```python
CARD_VALID = re.compile(r'\b(4\d{3}|5[1-5]\d{2}|220[0-4]|2[3-6]\d{2}|27[0-1]\d|2720)\s?\d{4}\s?\d{4}\s?\d{4}\b')
# Visa: 4xxx, Mastercard: 51-55xx, Mir: 2200-2204
```

### SWIFT/BIC код
```python
SWIFT = re.compile(r'[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?')
# Пример: EABORUAE, EABORUAEXXX
```

---

## Email

### Стандартный email
```python
EMAIL = re.compile(r'[\w\.\-\+]+@[\w\.\-]+\.[a-zA-Z]{2,}')
# Примеры: user@example.com, user.name+tag@sub.domain.co.uk
```

### Строгая валидация
```python
EMAIL_STRICT = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
```

---

## Даты

### DD.MM.YYYY (русский формат)
```python
DATE_RU = re.compile(r'\b(0?[1-9]|[12]\d|3[01])\.(0?[1-9]|1[0-2])\.(\d{4}|\d{2})\b')
# Примеры: 26.01.2026, 1.1.26
```

### DD/MM/YYYY (европейский)
```python
DATE_EU = re.compile(r'\b(0?[1-9]|[12]\d|3[01])/(0?[1-9]|1[0-2])/(\d{4}|\d{2})\b')
# Примеры: 26/01/2026, 1/1/26
```

### ISO формат (YYYY-MM-DD)
```python
DATE_ISO = re.compile(r'\b\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b')
# Пример: 2026-01-26
```

### "15 января", "15 янв" (русский текст)
```python
MONTHS_RU = r'(?:янв(?:аря)?|фев(?:раля)?|мар(?:та)?|апр(?:еля)?|ма[йя]|июн[яь]?|июл[яь]?|авг(?:уста)?|сен(?:тября)?|окт(?:ября)?|ноя(?:бря)?|дек(?:абря)?)'
DATE_TEXT_RU = re.compile(rf'\b(\d{{1,2}})\s+({MONTHS_RU})(?:\s+(\d{{4}}))?', re.IGNORECASE)
# Примеры: 15 января, 15 янв 2026, 1 мая
```

### Время (HH:MM)
```python
TIME = re.compile(r'\b([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?\b')
# Примеры: 10:30, 23:59, 9:05:30
```

### Дата и время вместе
```python
DATETIME_RU = re.compile(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\b')
# Пример: 26.01.2026 10:30:45
```

---

## Геолокации

### Google Maps ссылка
```python
GMAPS_URL = re.compile(r'https?://(?:www\.)?(?:google\.com/maps|maps\.google\.com|goo\.gl/maps)[^\s]*')
# Примеры:
# https://maps.google.com/?q=25.197197,55.274376
# https://goo.gl/maps/abc123
```

### Координаты из URL
```python
COORDS_FROM_URL = re.compile(r'[?&@]q?=?([-]?\d+\.?\d*)[,\s]+([-]?\d+\.?\d*)')
# Группы: (1) широта, (2) долгота
```

### Координаты (отдельно)
```python
LATITUDE = re.compile(r'[-]?([1-8]?\d(?:\.\d+)?|90(?:\.0+)?)')   # -90 до 90
LONGITUDE = re.compile(r'[-]?(?:1[0-7]\d|[1-9]?\d)(?:\.\d+)?|180(?:\.0+)?')  # -180 до 180
```

### Координаты в тексте
```python
COORDS_TEXT = re.compile(r'([-]?\d{1,3}\.\d{4,})[,\s]+([-]?\d{1,3}\.\d{4,})')
# Пример: 25.197197, 55.274376
```

---

## WhatsApp-специфичные

### JID (идентификатор чата)
```python
JID_PERSONAL = re.compile(r'\d+@s\.whatsapp\.net')       # Личный
JID_GROUP = re.compile(r'\d+@g\.us')                      # Группа
JID_ANY = re.compile(r'[\d\-]+@(?:s\.whatsapp\.net|g\.us)')
```

### Сообщение в chat.txt
```python
MESSAGE_LINE = re.compile(r'^\[(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})\]\s+(.+):$')
# Группы: (1) дата, (2) время, (3) отправитель
```

### Типы медиа
```python
MEDIA_TAG = re.compile(r'^\s+\[(ФОТО|ВИДЕО|АУДИО|ГОЛОСОВОЕ|ДОКУМЕНТ|СТИКЕР|GIF)\]\s+media/(.+)$')
# Группы: (1) тип, (2) путь к файлу
```

---

## Примеры использования

```python
import re

text = """
Привет! Мой номер +971 50 123 4567
Прилечу 15 января в 10:30
Оплатить на карту 4276 1234 5678 9012
IBAN: AE070331234567890123456
Отель: https://maps.google.com/?q=25.197197,55.274376
"""

# Извлечение всех данных
phones = UAE_PHONE.findall(text)
dates = DATE_TEXT_RU.findall(text)
cards = CARD_16.findall(text)
ibans = UAE_IBAN.findall(text)
coords = COORDS_FROM_URL.findall(text)

print(f"Телефоны: {phones}")   # ['+971 50 123 4567']
print(f"Даты: {dates}")        # [('15', 'января', '')]
print(f"Карты: {cards}")       # ['4276 1234 5678 9012']
print(f"IBAN: {ibans}")        # ['AE070331234567890123456']
print(f"Координаты: {coords}") # [('25.197197', '55.274376')]
```

---

## Полезные флаги

```python
# Игнорировать регистр
re.IGNORECASE  # или re.I

# Многострочный режим (^ и $ для каждой строки)
re.MULTILINE   # или re.M

# Verbose (с комментариями)
re.VERBOSE     # или re.X

# Unicode
re.UNICODE     # или re.U

# Комбинирование
pattern = re.compile(r'паттерн', re.I | re.M)
```
