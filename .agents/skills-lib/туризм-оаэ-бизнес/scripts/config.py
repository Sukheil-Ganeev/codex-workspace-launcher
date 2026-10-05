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

# Источники экспортированных чатов
EXPORT_DIRS = [
    Path("D:/Downloads/экспорт чатов с ватсапа"),
    Path("D:/Downloads/экспорт чатов с ватсап бизнеса")
]

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
                        folders.append({
                            "folder": chat_folder,
                            "chat_file": chat_file,
                            "source": "whatsapp" if "ватсапа" in str(export_dir) else "wa_business"
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
