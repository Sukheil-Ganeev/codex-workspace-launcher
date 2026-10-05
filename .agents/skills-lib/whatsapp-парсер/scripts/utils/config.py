#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Централизованная конфигурация скилла экспорта WhatsApp чатов."""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# ПУТИ
# ═══════════════════════════════════════════════════════════════
CHATS_DIR = Path("D:/Downloads/Chats")
BASE_DIR = CHATS_DIR / "_база"
INDEX_DIR = CHATS_DIR / "_индекс"
ANALYTICS_DIR = CHATS_DIR / "_аналитика"
TASKS_DIR = CHATS_DIR / "_задачи"
TEMPLATES_DIR = CHATS_DIR / "_шаблоны"
HISTORY_DIR = CHATS_DIR / "_история"
MEDIA_DIR = CHATS_DIR / "_медиа"

# Пути для AI-агента
JSON_DIR = BASE_DIR / "json"
CSV_DIR = BASE_DIR / "csv"
MD_DIR = BASE_DIR / "md"
AIRTABLE_DIR = BASE_DIR / "airtable"
RAW_DIR = BASE_DIR / "raw"

# Источники экспортированных чатов (основной путь)
EXPORT_DIRS = [
    Path("D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Личный"),
    Path("D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Бизнес"),
]

# Legacy пути (старые, не используются)
LEGACY_EXPORT_DIRS = [
    Path("D:/Downloads/экспорт чатов с ватсапа"),
    Path("D:/Downloads/экспорт чатов с ватсап бизнеса"),
]

# Результаты парсинга
PARSING_OUTPUT_DIR = Path("D:/Downloads/Туризм-ОАЭ-Данные/_парсинг")

# Типы контактов (подпапки)
CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]

# Подтипы контактов
CONTACT_SUBTYPES = {
    "клиенты": ["турист", "VIP", "корпоративный"],
    "агенты": ["турагент", "туроператор", "B2B"],
    "поставщики": ["обменник", "водитель", "гид", "яхтсмен", "кейтеринг"],
    "сотрудники": ["менеджер", "водитель_штат", "админ"]
}

# ═══════════════════════════════════════════════════════════════
# API КЛЮЧИ (из переменных окружения)
# ═══════════════════════════════════════════════════════════════
API_KEYS = {
    'notion': os.getenv('NOTION_API_KEY', ''),
    'google_sheets': os.getenv('GOOGLE_SHEETS_CREDENTIALS', ''),
    'telegram_bot': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    'google_calendar': os.getenv('GOOGLE_CALENDAR_CREDENTIALS', ''),
    'claude': os.getenv('ANTHROPIC_API_KEY', '') or os.getenv('CLAUDE_API_KEY', ''),
    'openai': os.getenv('OPENAI_API_KEY', ''),
    # OCR API ключи
    'google_vision': os.getenv('GOOGLE_VISION_KEY', ''),
    'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
}

# ═══════════════════════════════════════════════════════════════
# OCR КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════
OCR_CONFIG = {
    # Провайдер OCR: tesseract | google | claude
    "provider": os.getenv("OCR_PROVIDER", "tesseract"),
    # Путь к Tesseract (Windows)
    "tesseract_path": os.getenv("TESSERACT_PATH", r"D:\Downloads\tesseract.exe"),
    # Безопасность
    "mask_sensitive_data": True,   # Маскирование в логах
    "encrypt_output": False,       # Шифрование выходных файлов
    "encryption_key": os.getenv("OCR_ENCRYPTION_KEY", ""),
}

# Директории для OCR результатов
OCR_OUTPUT_DIR = JSON_DIR / "ocr"
PASSPORT_DATA_FILE = OCR_OUTPUT_DIR / "passport_data.json"
RECEIPTS_FILE = OCR_OUTPUT_DIR / "receipts.json"
DOCUMENTS_FILE = OCR_OUTPUT_DIR / "documents.json"

# ═══════════════════════════════════════════════════════════════
# OPENAI WHISPER API НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_API_MODEL = "whisper-1"
WHISPER_MAX_FILE_SIZE_MB = 25  # Ограничение OpenAI API

# ═══════════════════════════════════════════════════════════════
# CLAUDE API КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════
CLAUDE_CONFIG = {
    "api_key": os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("CLAUDE_API_KEY", ""),
    "model": "claude-sonnet-4-20250514",  # Экономичная модель для массовой обработки
    "max_tokens": 1024,
    "batch_size": 50,  # Сообщений в одном батче
    "max_retries": 3,
    "retry_delay": 2,  # секунд
}

# ═══════════════════════════════════════════════════════════════
# TELEGRAM BOT КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════
TELEGRAM_CONFIG = {
    # Основной бот для владельца/менеджеров
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),

    # Список chat_id администраторов (через запятую)
    "admin_ids": [
        int(x.strip()) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
        if x.strip().isdigit()
    ],

    # Бот для агентов (опционально)
    "agent_bot_token": os.getenv("TELEGRAM_AGENT_BOT_TOKEN", ""),

    # Webhook (если не polling)
    "webhook_url": os.getenv("TELEGRAM_WEBHOOK_URL", ""),
    "webhook_port": int(os.getenv("TELEGRAM_WEBHOOK_PORT", "8443")),

    # Пороги уведомлений
    "big_deal_threshold": 5000,  # AED - порог крупной сделки

    # Время дайджеста (часы UTC)
    "digest_morning_hour": 6,   # 10:00 Dubai (UTC+4)
    "digest_evening_hour": 17,  # 21:00 Dubai (UTC+4)
}

# ═══════════════════════════════════════════════════════════════
# BITRIX24 CRM КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════
BITRIX24_CONFIG = {
    "domain": os.getenv("BITRIX24_DOMAIN", ""),      # Домен: example.bitrix24.ru -> example
    "user_id": os.getenv("BITRIX24_USER_ID", ""),    # ID пользователя вебхука
    "webhook_key": os.getenv("BITRIX24_WEBHOOK_KEY", ""),  # Ключ вебхука
}

# Маппинг типов контактов на пользовательские поля Б24
BITRIX24_CONTACT_TYPE_MAPPING = {
    "клиенты": "CLIENT",
    "агенты": "AGENT",
    "поставщики": "SUPPLIER",
    "сотрудники": "EMPLOYEE",
}

# Маппинг статусов операций на стадии сделок Б24
BITRIX24_DEAL_STAGE_MAPPING = {
    "pending": "NEW",
    "confirmed": "PREPARATION",
    "in_progress": "EXECUTING",
    "completed": "WON",
    "cancelled": "LOSE",
}

def check_api_key(service: str) -> bool:
    """Проверить наличие API ключа для сервиса."""
    return bool(API_KEYS.get(service))

def get_api_key(service: str) -> str:
    """Получить API ключ с проверкой."""
    key = API_KEYS.get(service, '')
    if not key:
        raise ValueError(f"API ключ для '{service}' не настроен. "
                        f"Установите переменную окружения.")
    return key

# ═══════════════════════════════════════════════════════════════
# WHISPER НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════
WHISPER_MODEL = "medium"  # tiny, base, small, medium, large
WHISPER_DEVICE = "cuda"   # cuda или cpu
WHISPER_LANGUAGE = "ru"
WHISPER_FP16 = True       # Экономия VRAM

# ═══════════════════════════════════════════════════════════════
# СЛОВАРИ ИСПРАВЛЕНИЙ WHISPER
# ═══════════════════════════════════════════════════════════════
BANK_CORRECTIONS = {
    # Российские банки
    "сбер банк": "Сбербанк",
    "сбербанке": "Сбербанк",
    "тинькоф": "Тинькофф",
    "тинькофф": "Тинькофф",
    "тиньков": "Тинькофф",
    "втб": "ВТБ",
    "альфа банк": "Альфа-Банк",
    "альфабанк": "Альфа-Банк",
    "райффайзен": "Райффайзен",
    "газпромбанк": "Газпромбанк",

    # Банки ОАЭ
    "эмирейтс нбд": "Emirates NBD",
    "эмирейтс энбиди": "Emirates NBD",
    "машрек": "Mashreq",
    "машрэк": "Mashreq",
    "адиб": "ADIB",
    "фаб": "FAB",
    "энбд": "ENBD",
    "раб": "RAK Bank",
    "рак банк": "RAK Bank",
}

NAME_CORRECTIONS = {
    # Распространённые имена
    "марсель": "Марсель",
    "сухейль": "Сухейль",
    "суухейль": "Сухейль",
    "гульназ": "Гульназ",
    "анна": "Анна",
    "ахмед": "Ахмед",
}

TERM_CORRECTIONS = {
    # Финансовые термины
    "дирхамы": "дирхамы",
    "дирхам": "дирхам",
    "аед": "AED",
    "руб": "RUB",
    "юсд": "USD",
    "усд": "USD",
    "ибан": "IBAN",
    "айбан": "IBAN",
    "свифт": "SWIFT",

    # Туристические термины
    "экскурсия": "экскурсия",
    "трансфер": "трансфер",
    "сафари": "сафари",
    "дубай": "Дубай",
    "абу даби": "Абу-Даби",
    "абу-даби": "Абу-Даби",
}

# Все исправления объединены
ALL_CORRECTIONS = {**BANK_CORRECTIONS, **NAME_CORRECTIONS, **TERM_CORRECTIONS}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ИЗВЛЕЧЕНИЯ
# ═══════════════════════════════════════════════════════════════
PATTERNS = {
    'iban_uae': r'AE\d{21}',
    'card_ru': r'\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
    'phone_ru': r'\+7[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    'phone_uae': r'\+971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4}',
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'account_ru': r'\b408\d{17}\b',
    'bik': r'\b04\d{7}\b',
    'swift': r'\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
    'amount_rub': r'\b\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?\s*(?:руб|₽|RUB)\b',
    'amount_aed': r'\b\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?\s*(?:дирхам|AED)\b',
    'amount_usd': r'\b\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?\s*(?:долл|USD|\$)\b',
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ЦЕН И ЗАПРОСОВ
# ═══════════════════════════════════════════════════════════════

# Паттерны для определения запроса цены
PRICE_PATTERNS = [
    r'сколько\s*(?:стоит|будет)',
    r'какая\s*цена',
    r'цена\s*(?:на|за)',
    r'прайс',
    r'стоимость',
    r'расчёт|расчет',
    r'котировка',
    r'how\s*much',
    r'price\s*(?:for|of)',
    r'quote\s*(?:for|me)',
    r'cost\s*(?:of|for)',
    r'كم\s*(?:السعر|سعر)',  # Арабский: "какая цена"
    r'ما\s*هو\s*السعر',     # Арабский: "какова цена"
]

# Паттерны для определения бронирования
BOOKING_PATTERNS = [
    r'(?:хочу|хотим)\s*(?:забронировать|заказать|взять)',
    r'бронирую|бронируем',
    r'(?:можно|давайте)\s*(?:забронировать|заказать)',
    r'оформ(?:ить|ляем|ляю)\s*(?:бронь|заказ)',
    r'подтвердите\s*бронь',
    r'резервирую|резервируем',
    r'(?:want|would like)\s*to\s*book',
    r'(?:please|pls)\s*book',
    r'confirm(?:ing)?\s*(?:booking|reservation)',
    r'reserve\s*(?:for|me)',
    r'أريد\s*(?:حجز|الحجز)',    # Арабский: "хочу забронировать"
    r'احجز\s*(?:لي|لنا)',       # Арабский: "забронируй"
]

# Паттерны жалоб и негатива
COMPLAINT_PATTERNS = [
    r'недоволен|недовольна|недовольны',
    r'плохо|ужасно|отвратительно',
    r'жалоба|претензия',
    r'возврат\s*(?:денег|средств)',
    r'компенсация',
    r'опоздал|опоздали|задержка',
    r'не\s*(?:приехал|пришёл|пришел|явился)',
    r'обман|обманули|мошенники',
    r'разочарован|разочарована',
    r'верните\s*деньги',
    r'unhappy|disappointed|terrible',
    r'refund|compensation',
    r'complaint|complain',
    r'late|delayed|no\s*show',
    r'غير\s*راضي',           # Арабский: "недоволен"
    r'شكوى',                 # Арабский: "жалоба"
    r'استرداد',              # Арабский: "возврат"
]

# Паттерны позитивных отзывов
POSITIVE_PATTERNS = [
    r'спасибо\s*(?:большое|огромное)?',
    r'благодарю|благодарим',
    r'отлично|превосходно|замечательно',
    r'всё\s*(?:супер|класс|отлично)',
    r'рекомендую|посоветую',
    r'понравилось|понравилась',
    r'довольны|доволен|довольна',
    r'5\s*(?:звёзд|звезд|stars)',
    r'best|excellent|amazing|wonderful',
    r'thank\s*you\s*(?:so\s*much|very\s*much)?',
    r'highly\s*recommend',
    r'great\s*(?:service|experience|job)',
    r'شكرا\s*(?:جزيلا)?',     # Арабский: "спасибо"
    r'ممتاز|رائع',           # Арабский: "отлично/прекрасно"
]

# ═══════════════════════════════════════════════════════════════
# СЛОВАРИ ОАЭ
# ═══════════════════════════════════════════════════════════════

# Отели ОАЭ (ключ - варианты написания, значение - официальное название)
HOTELS_UAE = {
    # Дубай - 5 звёзд
    "burj al arab": "Burj Al Arab Jumeirah",
    "бурдж аль араб": "Burj Al Arab Jumeirah",
    "бурж аль араб": "Burj Al Arab Jumeirah",
    "atlantis the palm": "Atlantis The Palm",
    "atlantis palm": "Atlantis The Palm",
    "атлантис палм": "Atlantis The Palm",
    "атлантис": "Atlantis The Palm",
    "armani hotel": "Armani Hotel Dubai",
    "армани": "Armani Hotel Dubai",
    "address downtown": "Address Downtown",
    "адрес даунтаун": "Address Downtown",
    "one&only the palm": "One&Only The Palm",
    "one only palm": "One&Only The Palm",
    "waldorf astoria palm": "Waldorf Astoria Dubai Palm Jumeirah",
    "волдорф астория": "Waldorf Astoria Dubai Palm Jumeirah",
    "jumeirah beach hotel": "Jumeirah Beach Hotel",
    "джумейра бич": "Jumeirah Beach Hotel",
    "madinat jumeirah": "Madinat Jumeirah",
    "мадинат джумейра": "Madinat Jumeirah",
    "four seasons dubai": "Four Seasons Resort Dubai at Jumeirah Beach",
    "фор сизонс дубай": "Four Seasons Resort Dubai at Jumeirah Beach",
    "ritz carlton dubai": "The Ritz-Carlton Dubai",
    "ритц карлтон дубай": "The Ritz-Carlton Dubai",
    "sofitel the palm": "Sofitel Dubai The Palm",
    "софитель палм": "Sofitel Dubai The Palm",
    "raffles dubai": "Raffles Dubai",
    "раффлз дубай": "Raffles Dubai",
    "palazzo versace": "Palazzo Versace Dubai",
    "версаче": "Palazzo Versace Dubai",
    "bulgari dubai": "Bulgari Resort Dubai",
    "булгари дубай": "Bulgari Resort Dubai",
    "w dubai palm": "W Dubai - The Palm",
    "w палм": "W Dubai - The Palm",
    "caesars palace dubai": "Caesars Palace Dubai",
    "цезарь палас": "Caesars Palace Dubai",
    "five palm": "FIVE Palm Jumeirah Dubai",
    "файв палм": "FIVE Palm Jumeirah Dubai",
    "nikki beach": "Nikki Beach Resort & Spa Dubai",
    "никки бич": "Nikki Beach Resort & Spa Dubai",

    # Абу-Даби - 5 звёзд
    "emirates palace": "Emirates Palace Mandarin Oriental",
    "эмирейтс палас": "Emirates Palace Mandarin Oriental",
    "эмираты палас": "Emirates Palace Mandarin Oriental",
    "louvre abu dhabi": "Louvre Abu Dhabi (рядом отели)",
    "yas viceroy": "W Abu Dhabi - Yas Island",
    "яс вайсрой": "W Abu Dhabi - Yas Island",
    "shangri-la abu dhabi": "Shangri-La Abu Dhabi",
    "шангри ла абу даби": "Shangri-La Abu Dhabi",
    "st regis abu dhabi": "The St. Regis Abu Dhabi",
    "сент реджис абу даби": "The St. Regis Abu Dhabi",
    "st regis saadiyat": "The St. Regis Saadiyat Island Resort",
    "сент реджис саадият": "The St. Regis Saadiyat Island Resort",
    "park hyatt abu dhabi": "Park Hyatt Abu Dhabi Hotel and Villas",
    "парк хаятт абу даби": "Park Hyatt Abu Dhabi Hotel and Villas",
    "four seasons abu dhabi": "Four Seasons Hotel Abu Dhabi",
    "фор сизонс абу даби": "Four Seasons Hotel Abu Dhabi",
    "ritz carlton abu dhabi": "The Ritz-Carlton Abu Dhabi Grand Canal",
    "ритц карлтон абу даби": "The Ritz-Carlton Abu Dhabi Grand Canal",
    "jumeirah saadiyat": "Jumeirah at Saadiyat Island Resort",
    "джумейра саадият": "Jumeirah at Saadiyat Island Resort",
    "anantara abu dhabi": "Anantara Eastern Mangroves Abu Dhabi",
    "анантара абу даби": "Anantara Eastern Mangroves Abu Dhabi",

    # Рас-эль-Хайма
    "waldorf astoria rak": "Waldorf Astoria Ras Al Khaimah",
    "волдорф рак": "Waldorf Astoria Ras Al Khaimah",
    "ritz carlton rak": "The Ritz-Carlton Ras Al Khaimah Al Wadi Desert",
    "ритц рак": "The Ritz-Carlton Ras Al Khaimah Al Wadi Desert",
    "anantara rak": "Anantara Mina Al Arab Ras Al Khaimah Resort",
    "intercontinental rak": "InterContinental Ras Al Khaimah Mina Al Arab Resort",

    # Фуджейра
    "intercontinental fujairah": "InterContinental Fujairah Resort",
    "fairmont fujairah": "Fairmont Fujairah Beach Resort",
    "фэрмонт фуджейра": "Fairmont Fujairah Beach Resort",

    # Шарджа/Аджман
    "sheraton sharjah": "Sheraton Sharjah Beach Resort & Spa",
    "шератон шарджа": "Sheraton Sharjah Beach Resort & Spa",
}

# Типы номеров (ключ - варианты, значение - стандартное название)
ROOM_TYPES = {
    # Стандартные категории
    "standard": "Standard Room",
    "стандарт": "Standard Room",
    "standard room": "Standard Room",
    "superior": "Superior Room",
    "супериор": "Superior Room",
    "deluxe": "Deluxe Room",
    "делюкс": "Deluxe Room",
    "premium": "Premium Room",
    "премиум": "Premium Room",

    # С видом
    "sea view": "Sea View Room",
    "сивью": "Sea View Room",
    "вид на море": "Sea View Room",
    "ocean view": "Ocean View Room",
    "city view": "City View Room",
    "вид на город": "City View Room",
    "garden view": "Garden View Room",
    "вид на сад": "Garden View Room",
    "pool view": "Pool View Room",
    "вид на бассейн": "Pool View Room",
    "burj view": "Burj Khalifa View Room",
    "вид на бурдж": "Burj Khalifa View Room",

    # Люксы
    "junior suite": "Junior Suite",
    "джуниор сьют": "Junior Suite",
    "junior сьют": "Junior Suite",
    "suite": "Suite",
    "сьют": "Suite",
    "executive suite": "Executive Suite",
    "executive сьют": "Executive Suite",
    "presidential suite": "Presidential Suite",
    "президентский": "Presidential Suite",
    "royal suite": "Royal Suite",
    "королевский": "Royal Suite",

    # Особые категории
    "villa": "Villa",
    "вилла": "Villa",
    "beach villa": "Beach Villa",
    "overwater villa": "Overwater Villa",
    "над водой": "Overwater Villa",
    "penthouse": "Penthouse",
    "пентхаус": "Penthouse",
    "residence": "Residence",
    "резиденция": "Residence",
    "apartment": "Apartment",
    "апартамент": "Apartment",

    # По размеру кровати
    "king": "King Bed Room",
    "кинг": "King Bed Room",
    "twin": "Twin Beds Room",
    "твин": "Twin Beds Room",
    "double": "Double Room",
    "дабл": "Double Room",
    "family": "Family Room",
    "семейный": "Family Room",
    "connecting": "Connecting Rooms",
    "смежные": "Connecting Rooms",
}

# Валюты с символами и кодами
CURRENCIES = {
    # Основные для ОАЭ бизнеса
    "AED": {"symbol": "د.إ", "name_ru": "дирхам", "name_en": "Dirham", "flag": "🇦🇪"},
    "USD": {"symbol": "$", "name_ru": "доллар", "name_en": "Dollar", "flag": "🇺🇸"},
    "EUR": {"symbol": "€", "name_ru": "евро", "name_en": "Euro", "flag": "🇪🇺"},
    "RUB": {"symbol": "₽", "name_ru": "рубль", "name_en": "Ruble", "flag": "🇷🇺"},
    "GBP": {"symbol": "£", "name_ru": "фунт", "name_en": "Pound", "flag": "🇬🇧"},

    # СНГ
    "KZT": {"symbol": "₸", "name_ru": "тенге", "name_en": "Tenge", "flag": "🇰🇿"},
    "UAH": {"symbol": "₴", "name_ru": "гривна", "name_en": "Hryvnia", "flag": "🇺🇦"},
    "BYN": {"symbol": "Br", "name_ru": "бел. рубль", "name_en": "Bel. Ruble", "flag": "🇧🇾"},
    "UZS": {"symbol": "сўм", "name_ru": "сум", "name_en": "Sum", "flag": "🇺🇿"},
    "GEL": {"symbol": "₾", "name_ru": "лари", "name_en": "Lari", "flag": "🇬🇪"},
    "AMD": {"symbol": "֏", "name_ru": "драм", "name_en": "Dram", "flag": "🇦🇲"},
    "AZN": {"symbol": "₼", "name_ru": "манат", "name_en": "Manat", "flag": "🇦🇿"},

    # Ближний Восток
    "SAR": {"symbol": "﷼", "name_ru": "риял", "name_en": "Riyal", "flag": "🇸🇦"},
    "QAR": {"symbol": "ر.ق", "name_ru": "риал", "name_en": "Riyal", "flag": "🇶🇦"},
    "KWD": {"symbol": "د.ك", "name_ru": "динар", "name_en": "Dinar", "flag": "🇰🇼"},
    "BHD": {"symbol": "د.ب", "name_ru": "динар", "name_en": "Dinar", "flag": "🇧🇭"},
    "OMR": {"symbol": "ر.ع", "name_ru": "риал", "name_en": "Rial", "flag": "🇴🇲"},
    "EGP": {"symbol": "ج.م", "name_ru": "фунт", "name_en": "Pound", "flag": "🇪🇬"},
    "TRY": {"symbol": "₺", "name_ru": "лира", "name_en": "Lira", "flag": "🇹🇷"},

    # Азия
    "CNY": {"symbol": "¥", "name_ru": "юань", "name_en": "Yuan", "flag": "🇨🇳"},
    "INR": {"symbol": "₹", "name_ru": "рупия", "name_en": "Rupee", "flag": "🇮🇳"},
    "JPY": {"symbol": "¥", "name_ru": "иена", "name_en": "Yen", "flag": "🇯🇵"},

    # Крипто (условно)
    "USDT": {"symbol": "₮", "name_ru": "тезер", "name_en": "Tether", "flag": "🪙"},
}

# Словарь транслитерации (кириллица -> латиница)
TRANSLIT_WORDS = {
    # Приветствия
    "privet": "привет",
    "zdravstvuyte": "здравствуйте",
    "dobryy den": "добрый день",
    "dobroye utro": "доброе утро",
    "dobryy vecher": "добрый вечер",

    # Базовые слова
    "spasibo": "спасибо",
    "pozhaluysta": "пожалуйста",
    "horosho": "хорошо",
    "da": "да",
    "net": "нет",
    "ok": "ок",
    "ladno": "ладно",
    "ponyal": "понял",
    "ponyatno": "понятно",

    # Вопросы
    "skolko": "сколько",
    "kogda": "когда",
    "gde": "где",
    "kak": "как",
    "chto": "что",
    "kuda": "куда",
    "pochemu": "почему",

    # Время
    "segodnya": "сегодня",
    "zavtra": "завтра",
    "vchera": "вчера",
    "seychas": "сейчас",
    "potom": "потом",
    "skoro": "скоро",

    # Туризм
    "ekskursiya": "экскурсия",
    "tur": "тур",
    "transfer": "трансфер",
    "otel": "отель",
    "bilet": "билет",
    "safari": "сафари",
    "yahta": "яхта",
    "arenda": "аренда",
    "mashina": "машина",
    "avto": "авто",
    "voditel": "водитель",
    "gid": "гид",
    "aeroport": "аэропорт",
    "vstrecha": "встреча",

    # Финансы
    "dirham": "дирхам",
    "rubl": "рубль",
    "dollar": "доллар",
    "kurs": "курс",
    "obmen": "обмен",
    "perevod": "перевод",
    "oplata": "оплата",
    "stoimost": "стоимость",
    "tsena": "цена",
    "skidka": "скидка",

    # Числа (прописью)
    "odin": "один",
    "dva": "два",
    "tri": "три",
    "chetyre": "четыре",
    "pyat": "пять",
    "shest": "шесть",
    "sem": "семь",
    "vosem": "восемь",
    "devyat": "девять",
    "desyat": "десять",

    # Люди
    "chelovek": "человек",
    "vzroslykh": "взрослых",
    "detey": "детей",
    "gruppa": "группа",
    "gosti": "гости",
    "klient": "клиент",

    # География ОАЭ
    "dubay": "Дубай",
    "dubai": "Дубай",
    "abu-dabi": "Абу-Даби",
    "abu dabi": "Абу-Даби",
    "shardzha": "Шарджа",
    "sharjah": "Шарджа",
    "adzman": "Аджман",
    "ajman": "Аджман",
    "ras-al-khayma": "Рас-эль-Хайма",
    "rak": "Рас-эль-Хайма",
    "fudzheyra": "Фуджейра",
    "fujairah": "Фуджейра",
}

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ИНИЦИАЛИЗАЦИИ
# ═══════════════════════════════════════════════════════════════
def ensure_directories():
    """Создать все необходимые директории."""
    dirs = [CHATS_DIR, BASE_DIR, INDEX_DIR, ANALYTICS_DIR,
            TASKS_DIR, TEMPLATES_DIR, HISTORY_DIR, MEDIA_DIR]
    dirs += [CHATS_DIR / t for t in CONTACT_TYPES]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    return True

def get_chat_files():
    """Получить список всех файлов чатов."""
    files = []
    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            files.extend(type_dir.glob("*.md"))
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

# ═══════════════════════════════════════════════════════════════
# ПРАВИЛА АВТОКЛАССИФИКАЦИИ КОНТАКТОВ
# ═══════════════════════════════════════════════════════════════
CLASSIFICATION_RULES = {
    "агенты": {
        "keywords": [
            "турагент", "турагентство", "агентство", "туроператор",
            "партнёр", "комиссия", "%", "нетто", "брутто",
            "travel", "tour", "agency"
        ],
        "jid_patterns": [r".*@g\.us$"],  # Группы часто агентские
        "name_patterns": [r".*tour.*", r".*travel.*", r".*agency.*"],
        "subtypes": {
            "турагент": ["турагент", "agency", "travel"],
            "туроператор": ["туроператор", "operator"],
            "B2B": ["B2B", "партнёр", "wholesale"]
        }
    },
    "поставщики": {
        "keywords": [
            "обменник", "курс", "валюта", "exchange",
            "водитель", "driver", "трансфер",
            "гид", "guide", "экскурсовод",
            "яхта", "yacht", "капитан",
            "кейтеринг", "catering"
        ],
        "subtypes": {
            "обменник": ["обмен", "курс", "exchange", "валюта"],
            "водитель": ["водитель", "driver", "трансфер"],
            "гид": ["гид", "guide", "экскурсовод"],
            "яхтсмен": ["яхта", "yacht", "капитан"],
            "кейтеринг": ["кейтеринг", "catering", "еда"]
        }
    },
    "сотрудники": {
        "keywords": [
            "офис", "зарплата", "отпуск", "рабочий",
            "смена", "график", "meeting"
        ],
        "phone_prefixes": ["971507705321"],  # Известные номера сотрудников
        "subtypes": {
            "менеджер": ["менеджер", "manager"],
            "водитель_штат": ["водитель", "наш"],
            "админ": ["админ", "бухгалтер", "HR"]
        }
    },
    "клиенты": {
        "default": True,  # Если не подошло ничего другое
        "keywords": [
            "бронирование", "экскурсия", "тур", "билет",
            "хочу", "сколько стоит", "цена"
        ],
        "subtypes": {
            "турист": ["экскурсия", "тур", "отель"],
            "VIP": ["VIP", "люкс", "premium", "private"],
            "корпоративный": ["компания", "корпоратив", "team building"]
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# НАСТРОЙКИ FOLLOW-UP
# ═══════════════════════════════════════════════════════════════

# Временные интервалы для follow-up (в днях)
FOLLOWUP_INTERVALS = {
    "soft_reminder": 1,      # Мягкое напоминание (1 день без ответа)
    "repeat_offer": 3,       # Повторное предложение (3 дня)
    "special_offer": 7,      # Специальное предложение/скидка (7 дней)
    "last_attempt": 14,      # Последняя попытка (14 дней)
    "reactivation": 30,      # Реактивация (30 дней)
    "cold_threshold": 60,    # Порог "холодного" контакта (60 дней)
}

# Максимальное количество follow-up на один контакт
MAX_FOLLOWUPS_PER_CONTACT = 5

# Минимальный интервал между follow-up (в часах)
MIN_FOLLOWUP_INTERVAL_HOURS = 24

# Приоритеты клиентов (1 = высший)
CLIENT_PRIORITY = {
    "VIP": 1,
    "корпоративный": 2,
    "турагент": 2,
    "туроператор": 2,
    "B2B": 2,
    "турист": 3,
}

# Типы контактов, исключённые из follow-up
FOLLOWUP_EXCLUDED_TYPES = ["поставщики", "сотрудники"]

# ═══════════════════════════════════════════════════════════════
# ТИПЫ ОПЕРАЦИЙ
# ═══════════════════════════════════════════════════════════════
OPERATION_TYPES = [
    "tour", "transfer", "yacht", "tickets",
    "exchange", "car_rental", "catering", "other"
]

OPERATION_KEYWORDS = {
    "tour": ["экскурсия", "тур", "сафари", "museum", "абу-даби", "дубай"],
    "transfer": ["трансфер", "встреча", "аэропорт", "transfer"],
    "yacht": ["яхта", "yacht", "катер", "лодка"],
    "tickets": ["билет", "парк", "ferrari", "aquaventure", "ticket"],
    "exchange": ["обмен", "курс", "дирхам", "рубл", "exchange"],
    "car_rental": ["аренда", "машина", "авто", "rental", "car"],
    "catering": ["кейтеринг", "еда", "catering", "food"]
}

# ═══════════════════════════════════════════════════════════════
# РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ ДЛЯ ПАРСИНГА CHAT.TXT
# ═══════════════════════════════════════════════════════════════
import re

# Заголовок чата
CHAT_HEADER_RE = re.compile(r'^ЧАТ: (.+)$', re.MULTILINE)
CHAT_JID_RE = re.compile(r'^JID: (.+)$', re.MULTILINE)
CHAT_MSG_COUNT_RE = re.compile(r'^Сообщений: (\d+)$', re.MULTILINE)
CHAT_EXPORT_DATE_RE = re.compile(r'^Экспорт: (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})$', re.MULTILINE)

# Сообщение
MESSAGE_RE = re.compile(r'^\[(\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2}:\d{2})\] (.+):$')

# Типы контента в сообщениях
MEDIA_RE = re.compile(r'^\s+\[(.+?)\] media/(.+)$')
LOCATION_RE = re.compile(r'^\s+\[ЛОКАЦИЯ\] https://maps\.google\.com/\?q=(.+),(.+)$')
CONTACT_RE = re.compile(r'^\s+\[КОНТАКТ\] (.+)$')
DELETED_RE = re.compile(r'^\s+\(медиа не сохранено в бэкапе\)$')

# Извлечение телефона из JID
PHONE_FROM_JID_RE = re.compile(r'^(\d+)@')


def ensure_directories():
    """Создать все необходимые директории."""
    dirs = [CHATS_DIR, BASE_DIR, INDEX_DIR, ANALYTICS_DIR,
            TASKS_DIR, TEMPLATES_DIR, HISTORY_DIR, MEDIA_DIR,
            JSON_DIR, CSV_DIR, MD_DIR, AIRTABLE_DIR, RAW_DIR]
    dirs += [CHATS_DIR / t for t in CONTACT_TYPES]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    return True


def get_chat_files():
    """Получить список всех файлов чатов."""
    files = []
    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            files.extend(type_dir.glob("*.md"))
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)


def get_export_chat_folders():
    """Получить список всех папок с экспортированными чатами."""
    folders = []
    for export_dir in EXPORT_DIRS:
        if export_dir.exists():
            for chat_folder in export_dir.iterdir():
                if chat_folder.is_dir():
                    chat_file = chat_folder / "chat.txt"
                    if chat_file.exists():
                        # Определяем source по названию папки
                        dir_name = export_dir.name.lower()
                        if "личный" in dir_name or "personal" in dir_name:
                            source = "whatsapp"
                        elif "бизнес" in dir_name or "business" in dir_name:
                            source = "wa_business"
                        else:
                            source = "whatsapp"
                        folders.append({
                            "folder": chat_folder,
                            "chat_file": chat_file,
                            "source": source,
                        })
    return folders


if __name__ == "__main__":
    print("Конфигурация скилла экспорта WhatsApp чатов")
    print(f"CHATS_DIR: {CHATS_DIR}")
    print(f"Whisper модель: {WHISPER_MODEL}")
    print(f"API ключи настроены:")
    for k, v in API_KEYS.items():
        print(f"  {k}: {'✓' if v else '✗'}")

    ensure_directories()
    print("\nДиректории созданы")

    # Проверка экспортов
    folders = get_export_chat_folders()
    print(f"\nНайдено {len(folders)} экспортированных чатов")
