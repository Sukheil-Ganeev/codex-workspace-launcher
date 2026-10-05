# Мультиязычный парсинг

Документация по парсингу сообщений на русском, английском и арабском языках.

---

## 1. Определение языка

### Regex для языков

```python
# Русский текст
RUSSIAN_PATTERN = r'[а-яА-ЯёЁ]+'

# Английский текст
ENGLISH_PATTERN = r'[a-zA-Z]+'

# Арабский текст
ARABIC_PATTERN = r'[\u0600-\u06FF\u0750-\u077F]+'
```

### Функция определения языков

```python
def detect_languages(text):
    """Определяет все языки в сообщении"""
    languages = []

    if re.search(r'[а-яА-ЯёЁ]', text):
        languages.append('russian')
    if re.search(r'[a-zA-Z]', text):
        languages.append('english')
    if re.search(r'[\u0600-\u06FF]', text):
        languages.append('arabic')

    return languages
```

### Примеры определения

| Сообщение | Языки |
|-----------|-------|
| "Привет, сколько стоит экскурсия?" | ['russian'] |
| "Hello, how much for the tour?" | ['english'] |
| "مرحبا كم السعر؟" | ['arabic'] |
| "Привет! Book desert safari please" | ['russian', 'english'] |
| "Hello مرحبا Привет" | ['english', 'arabic', 'russian'] |
| "Хочу Ferrari на 3 days" | ['russian', 'english'] |

---

## 2. Словарь транслита

### Основной словарь (латиница -> кириллица)

```python
TRANSLIT_WORDS = {
    # Приветствия
    'privet': 'привет',
    'zdravstvuyte': 'здравствуйте',
    'poka': 'пока',
    'do svidaniya': 'до свидания',
    'spasibo': 'спасибо',
    'pozhaluysta': 'пожалуйста',

    # Вопросы
    'skolko': 'сколько',
    'stoit': 'стоит',
    'kogda': 'когда',
    'gde': 'где',
    'kak': 'как',
    'chto': 'что',
    'pochemu': 'почему',

    # Бронирование
    'zakazat': 'заказать',
    'zabronirovat': 'забронировать',
    'hochu': 'хочу',
    'nado': 'надо',
    'mozhno': 'можно',
    'nuzhno': 'нужно',

    # Туризм
    'ekskursiya': 'экскурсия',
    'tur': 'тур',
    'otel': 'отель',
    'bilet': 'билет',
    'transfer': 'трансфер',
    'safari': 'сафари',
    'mashina': 'машина',
    'avto': 'авто',

    # Время
    'segodnya': 'сегодня',
    'zavtra': 'завтра',
    'vchera': 'вчера',
    'utrom': 'утром',
    'vecherom': 'вечером',

    # Числа (словами)
    'odin': 'один',
    'dva': 'два',
    'tri': 'три',
    'chetyre': 'четыре',
    'pyat': 'пять',

    # Разное
    'da': 'да',
    'net': 'нет',
    'ok': 'ок',
    'khorosho': 'хорошо',
    'otlichno': 'отлично',
    'super': 'супер',
    'chelovek': 'человек',
    'vzroslyh': 'взрослых',
    'detey': 'детей',
}
```

### Вариации написания

```python
TRANSLIT_VARIATIONS = {
    # Разные написания одного слова
    ('skolko', "skol'ko", 'scolko'): 'сколько',
    ('stoit', "stoit'", 'stojt'): 'стоит',
    ('hochu', 'xochu', 'khochu'): 'хочу',
    ('zavtra', 'zaftra'): 'завтра',
    ('segodnya', 'segodnja', 'sivodnya'): 'сегодня',
    ('spasibo', 'spasiba', 'pasibo'): 'спасибо',
    ('pozhaluysta', 'pojalusta', 'pazhalusta'): 'пожалуйста',
}
```

### Посимвольная транслитерация

```python
TRANSLIT_CHARS = {
    'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д',
    'e': 'е', 'yo': 'ё', 'zh': 'ж', 'z': 'з', 'i': 'и',
    'y': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
    'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т',
    'u': 'у', 'f': 'ф', 'kh': 'х', 'ts': 'ц', 'ch': 'ч',
    'sh': 'ш', 'sch': 'щ', '"': 'ъ', "'": 'ь',
    'yu': 'ю', 'ya': 'я',
}

# Порядок важен: сначала длинные комбинации
TRANSLIT_ORDER = ['sch', 'zh', 'kh', 'ts', 'ch', 'sh', 'yo', 'yu', 'ya']
```

### Regex паттерны транслита

```python
TRANSLIT_PATTERNS = [
    r'\bprivet\b',
    r'\bspasibo\b',
    r'\bskolko\b',
    r'\bstoit\b',
    r'\bkak\b',
    r'\bzakazat\b',
    r'\bhochu\b',
    r'\bmozhno\b',
]
```

### Примеры транслита

| Транслит | Конвертация |
|----------|-------------|
| "privet, skolko stoit safari?" | "привет, сколько стоит safari?" |
| "spasibo, vse super" | "спасибо, все супер" |
| "zavtra na 2 chelovek" | "завтра на 2 человек" |

---

## 3. Арабские цифры

### Восточно-арабские (индийские) цифры

```python
ARABIC_NUMERALS = {
    '٠': '0',  # 0
    '١': '1',  # 1
    '٢': '2',  # 2
    '٣': '3',  # 3
    '٤': '4',  # 4
    '٥': '5',  # 5
    '٦': '6',  # 6
    '٧': '7',  # 7
    '٨': '8',  # 8
    '٩': '9',  # 9
}

def normalize_arabic_numbers(text):
    """Конвертирует восточно-арабские цифры в стандартные"""
    for arabic, standard in ARABIC_NUMERALS.items():
        text = text.replace(arabic, standard)
    return text
```

### Примеры конвертации

| Арабское | Стандартное | Значение |
|----------|-------------|----------|
| ٥٠٠ درهم | 500 درهم | 500 дирхам |
| ١٥ يناير | 15 يناير | 15 января |
| ١٢:٣٠ | 12:30 | 12:30 |

### Regex для арабских чисел

```python
ARABIC_NUMERALS_PATTERN = r'[٠-٩]+'
```

---

## 4. Даты на разных языках

### Русские месяцы

```python
RUSSIAN_MONTHS = {
    'января': 1, 'янв': 1,
    'февраля': 2, 'фев': 2,
    'марта': 3, 'мар': 3,
    'апреля': 4, 'апр': 4,
    'мая': 5,
    'июня': 6, 'июн': 6,
    'июля': 7, 'июл': 7,
    'августа': 8, 'авг': 8,
    'сентября': 9, 'сен': 9,
    'октября': 10, 'окт': 10,
    'ноября': 11, 'ноя': 11,
    'декабря': 12, 'дек': 12,
}
```

### Английские месяцы

```python
ENGLISH_MONTHS = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}
```

### Арабские месяцы

```python
ARABIC_MONTHS = {
    'يناير': 1,    # январь
    'فبراير': 2,   # февраль
    'مارس': 3,     # март
    'أبريل': 4,    # апрель
    'مايو': 5,     # май
    'يونيو': 6,    # июнь
    'يوليو': 7,    # июль
    'أغسطس': 8,    # август
    'سبتمبر': 9,   # сентябрь
    'أكتوبر': 10,  # октябрь
    'نوفمبر': 11,  # ноябрь
    'ديسمبر': 12,  # декабрь
}
```

### Regex паттерны дат

```python
# Русский: "15 января"
RUSSIAN_DATE_PATTERN = r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)'

# Английский: "January 15"
ENGLISH_DATE_PATTERN = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s*(\d{1,2})'

# Арабский: "١٥ يناير"
ARABIC_DATE_PATTERN = r'(\d{1,2})\s*(يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)'

# ISO: "2025-01-15"
ISO_DATE_PATTERN = r'(\d{4})-(\d{2})-(\d{2})'

# DD.MM.YYYY или DD/MM/YYYY
NUMERIC_DATE_PATTERN = r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})'
```

### Примеры дат

| Формат | Пример | Результат |
|--------|--------|-----------|
| Русский | "15 января" | 2025-01-15 |
| Английский | "January 15" | 2025-01-15 |
| Арабский | "١٥ يناير" | 2025-01-15 |
| Числовой | "15.01.2025" | 2025-01-15 |
| ISO | "2025-01-15" | 2025-01-15 |

---

### Дни недели

```python
WEEKDAYS = {
    'russian': {
        'понедельник': 0, 'пн': 0,
        'вторник': 1, 'вт': 1,
        'среда': 2, 'ср': 2,
        'четверг': 3, 'чт': 3,
        'пятница': 4, 'пт': 4,
        'суббота': 5, 'сб': 5,
        'воскресенье': 6, 'вс': 6,
    },
    'english': {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6,
    },
    'arabic': {
        'الاثنين': 0,    # понедельник
        'الثلاثاء': 1,   # вторник
        'الأربعاء': 2,   # среда
        'الخميس': 3,     # четверг
        'الجمعة': 4,     # пятница
        'السبت': 5,      # суббота
        'الأحد': 6,      # воскресенье
    }
}
```

---

## 5. Валюты

### Символы валют

```python
CURRENCY_SYMBOLS = {
    '$': 'USD',
    '€': 'EUR',
    '£': 'GBP',
    '₽': 'RUB',
    '₸': 'KZT',
    'د.إ': 'AED',
    '﷼': 'SAR',
}
```

### Текстовые обозначения (мультиязычные)

```python
CURRENCIES = {
    # USD
    'доллар': 'USD', 'долларов': 'USD', 'баксов': 'USD',
    'dollar': 'USD', 'dollars': 'USD', 'usd': 'USD',
    'دولار': 'USD',

    # EUR
    'евро': 'EUR', 'euro': 'EUR', 'eur': 'EUR',
    'يورو': 'EUR',

    # RUB
    'рубль': 'RUB', 'рублей': 'RUB', 'руб': 'RUB',
    'ruble': 'RUB', 'rub': 'RUB',
    'روبل': 'RUB',

    # AED
    'дирхам': 'AED', 'дирхамов': 'AED', 'aed': 'AED',
    'dirham': 'AED', 'dirhams': 'AED',
    'درهم': 'AED',

    # KZT
    'тенге': 'KZT', 'kzt': 'KZT',

    # USDT
    'usdt': 'USDT', 'тезер': 'USDT', 'tether': 'USDT',
}
```

### Regex для валют

```python
# Общий паттерн: сумма + валюта
CURRENCY_PATTERN = r'(\d+(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(доллар|долларов|евро|рублей|дирхам|درهم|\$|€|₽|د\.إ|AED|USD|EUR|RUB)'

# Примеры совпадений:
# "500 дирхам" -> 500, AED
# "$100" -> 100, USD
# "٥٠٠ درهم" -> 500, AED
# "1000 рублей" -> 1000, RUB
# "1,500 AED" -> 1500, AED
```

### Таблица валют

| Символ | Код | Русский | Английский | Арабский |
|--------|-----|---------|------------|----------|
| $ | USD | доллар | dollar | دولار |
| € | EUR | евро | euro | يورو |
| ₽ | RUB | рубль | ruble | روبل |
| د.إ | AED | дирхам | dirham | درهم |
| ₸ | KZT | тенге | tenge | - |

---

## 6. Арабские фразы для туризма

### Приветствия

| Арабский | Транслит | Русский |
|----------|----------|---------|
| مرحبا | marhaba | привет |
| السلام عليكم | as-salamu alaykum | мир вам |
| شكرا | shukran | спасибо |

### Вопросы о цене

| Арабский | Транслит | Русский |
|----------|----------|---------|
| كم السعر | kam al-si'r | какая цена |
| كم التكلفة | kam at-taklufa | сколько стоит |
| غالي | ghali | дорого |
| رخيص | rakhis | дёшево |

### Бронирование

| Арабский | Транслит | Русский |
|----------|----------|---------|
| حجز | hajz | бронирование |
| أريد | urid | я хочу |
| متى | mata | когда |
| أين | ayna | где |

### Числительные

| Арабский | Транслит | Русский | Число |
|----------|----------|---------|-------|
| واحد | wahid | один | 1 |
| اثنان | ithnan | два | 2 |
| ثلاثة | thalatha | три | 3 |
| أربعة | arba'a | четыре | 4 |
| خمسة | khamsa | пять | 5 |
| ستة | sitta | шесть | 6 |
| سبعة | sab'a | семь | 7 |
| ثمانية | thamaniya | восемь | 8 |
| تسعة | tis'a | девять | 9 |
| عشرة | 'ashara | десять | 10 |

### Regex для арабских фраз

```python
# Вопрос о цене
ARABIC_PRICE_PATTERN = r'(كم|السعر|التكلفة|درهم|دولار)'

# Бронирование
ARABIC_BOOKING_PATTERN = r'(حجز|أريد|احتاج)'
```

---

## 7. Обработка RTL текста

### RTL маркеры Unicode

```python
RTL_MARK = '\u200f'  # Right-to-Left Mark
LTR_MARK = '\u200e'  # Left-to-Right Mark
RLE = '\u202b'       # Right-to-Left Embedding
PDF = '\u202c'       # Pop Directional Formatting
```

### Нормализация RTL текста

```python
def normalize_rtl_text(text):
    """Нормализует RTL текст для обработки"""
    rtl_markers = ['\u200f', '\u200e', '\u202b', '\u202c']
    for marker in rtl_markers:
        text = text.replace(marker, '')
    return text
```

---

## 8. Числа на разных языках

### Числа словами

```python
NUMBERS_RUSSIAN = {
    'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5,
    'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10,
}

NUMBERS_ENGLISH = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
}

NUMBERS_ARABIC_WORDS = {
    'واحد': 1, 'اثنان': 2, 'ثلاثة': 3, 'أربعة': 4, 'خمسة': 5,
    'ستة': 6, 'سبعة': 7, 'ثمانية': 8, 'تسعة': 9, 'عشرة': 10,
}
```

---

## 9. Сводка regex паттернов

```python
PATTERNS = {
    # Языки
    'russian': r'[а-яА-ЯёЁ]+',
    'english': r'[a-zA-Z]+',
    'arabic': r'[\u0600-\u06FF\u0750-\u077F]+',

    # Числа
    'arabic_numerals': r'[٠-٩]+',
    'standard_numerals': r'\d+',

    # Валюты
    'currency_amount': r'(\d+(?:[\s,]\d{3})*(?:\.\d{2})?)\s*([A-Z]{3}|[$€£₽₸]|درهم|дирхам)',

    # Даты
    'date_ru': r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
    'date_en': r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(\d{1,2})',
    'date_iso': r'(\d{4})-(\d{2})-(\d{2})',

    # Время
    'time_24h': r'(\d{1,2}):(\d{2})(?::(\d{2}))?',
    'time_12h': r'(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)',

    # Телефоны
    'phone_intl': r'\+?\d{1,3}[\s\-]?\d{2,3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    'phone_uae': r'\+?971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4}',
}
```

---

## 10. JSON структура мультиязычного сообщения

```json
{
  "multilingual_message": {
    "original": {
      "text": "كم السعر للسفاري؟",
      "language": "ar",
      "entities": {
        "intent": "price_inquiry",
        "product": "safari"
      }
    },
    "translated": {
      "text": "Сколько стоит сафари?",
      "target_language": "ru",
      "entities": {
        "intent": "price_inquiry",
        "product": "сафари"
      },
      "translated_at": "2025-01-26T10:00:00Z"
    },
    "detected_languages": ["arabic"],
    "contains_mixed": false
  }
}
```

---

*Документ: multilingual.md*
*Версия: 1.0*
*Создан: Январь 2025*
