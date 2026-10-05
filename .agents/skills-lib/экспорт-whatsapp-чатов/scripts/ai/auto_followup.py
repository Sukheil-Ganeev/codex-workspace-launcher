#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система автоматических follow-up напоминаний.

Определяет "холодных" контактов и генерирует персонализированные
напоминания для реактивации клиентов.

Функции:
1. Определение "холодных" контактов (нет ответа N дней)
2. Генерация персонализированных follow-up текстов
3. Создание задач в Bitrix24
4. Планирование в Google Calendar
5. Формирование очереди для WhatsApp API

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/contacts.json
- D:/Downloads/Chats/_база/json/profiles.json
- D:/Downloads/Chats/_база/json/sales_funnel.json
- D:/Downloads/Chats/_база/json/operations.json

Выходные файлы:
- D:/Downloads/Chats/_база/json/followup_queue.json
- D:/Downloads/Chats/_база/json/followup_history.json
- D:/Downloads/Chats/_база/json/followup_stats.json

Использование:
    python auto_followup.py --analyze          # Анализ холодных контактов
    python auto_followup.py --generate         # Генерация follow-up
    python auto_followup.py --create-tasks     # Создать задачи в Б24
    python auto_followup.py --schedule         # Запланировать в календаре
    python auto_followup.py --all              # Всё вместе
    python auto_followup.py --dry-run          # Тестовый режим
"""

import sys
import os
import json
import re
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import (
        JSON_DIR, ANALYTICS_DIR, CONTACT_SUBTYPES,
        FOLLOWUP_INTERVALS as CFG_FOLLOWUP_INTERVALS,
        MAX_FOLLOWUPS_PER_CONTACT as CFG_MAX_FOLLOWUPS,
        MIN_FOLLOWUP_INTERVAL_HOURS as CFG_MIN_INTERVAL,
        CLIENT_PRIORITY as CFG_CLIENT_PRIORITY,
        FOLLOWUP_EXCLUDED_TYPES as CFG_EXCLUDED_TYPES,
    )
    # Используем значения из config.py
    _USE_CONFIG = True
except ImportError:
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    ANALYTICS_DIR = Path("D:/Downloads/Chats/_аналитика")
    CONTACT_SUBTYPES = {
        "клиенты": ["турист", "VIP", "корпоративный"],
        "агенты": ["турагент", "туроператор", "B2B"],
    }
    _USE_CONFIG = False

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ FOLLOW-UP
# ═══════════════════════════════════════════════════════════════

# Временные интервалы для follow-up (дни)
# Значения по умолчанию (переопределяются из config.py если доступен)
FOLLOWUP_INTERVALS = {
    "soft_reminder": 1,      # Мягкое напоминание
    "repeat_offer": 3,       # Повторное предложение
    "special_offer": 7,      # Специальное предложение/скидка
    "last_attempt": 14,      # Последняя попытка
    "reactivation": 30,      # Реактивация
    "cold_threshold": 60,    # Полностью холодный контакт
}

# Максимальное количество follow-up на контакт
MAX_FOLLOWUPS_PER_CONTACT = 5

# Минимальный интервал между follow-up (часы)
MIN_FOLLOWUP_INTERVAL_HOURS = 24

# Типы клиентов и приоритеты
CLIENT_PRIORITY = {
    "VIP": 1,           # Высший приоритет
    "корпоративный": 2,
    "турагент": 2,
    "туроператор": 2,
    "B2B": 2,
    "турист": 3,        # Обычный приоритет
}

# Исключить из follow-up
EXCLUDED_TYPES = ["поставщики", "сотрудники"]

# Переопределяем значениями из config.py если доступен
if _USE_CONFIG:
    FOLLOWUP_INTERVALS = CFG_FOLLOWUP_INTERVALS
    MAX_FOLLOWUPS_PER_CONTACT = CFG_MAX_FOLLOWUPS
    MIN_FOLLOWUP_INTERVAL_HOURS = CFG_MIN_INTERVAL
    CLIENT_PRIORITY = CFG_CLIENT_PRIORITY
    EXCLUDED_TYPES = CFG_EXCLUDED_TYPES

# ═══════════════════════════════════════════════════════════════
# ПУТИ К ФАЙЛАМ
# ═══════════════════════════════════════════════════════════════

MESSAGES_FILE = Path("D:/Downloads/Chats/_база/raw/all_messages.jsonl")
CONTACTS_FILE = JSON_DIR / "contacts.json"
PROFILES_FILE = JSON_DIR / "profiles.json"
SALES_FUNNEL_FILE = JSON_DIR / "sales_funnel.json"
OPERATIONS_FILE = JSON_DIR / "operations.json"

OUTPUT_QUEUE = JSON_DIR / "followup_queue.json"
OUTPUT_HISTORY = JSON_DIR / "followup_history.json"
OUTPUT_STATS = JSON_DIR / "followup_stats.json"

# ═══════════════════════════════════════════════════════════════
# ШАБЛОНЫ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

# Шаблоны для разных типов follow-up
FOLLOWUP_TEMPLATES = {
    "soft_reminder": {
        "ru": {
            "default": "Здравствуйте, {name}! Хотели уточнить - рассматриваете ли вы ещё наше предложение по {product}? Буду рад ответить на любые вопросы.",
            "VIP": "Добрый день, {name}! Надеюсь, у вас всё хорошо. Хотел лично уточнить - актуально ли для вас наше предложение по {product}? Готов обсудить любые детали.",
            "agent": "Привет! Как дела с клиентом по {product}? Есть какие-то вопросы по расчёту?",
        },
        "en": {
            "default": "Hello {name}! Just wanted to check if you're still considering our offer for {product}? Happy to answer any questions.",
            "VIP": "Good day, {name}! I hope you're doing well. I wanted to personally follow up on our {product} proposal. Please let me know if you have any questions.",
        }
    },
    "repeat_offer": {
        "ru": {
            "default": "Добрый день, {name}! Напоминаю о нашем предложении по {product}. Даты ещё актуальны? Могу помочь с бронированием.",
            "VIP": "{name}, добрый день! Возвращаюсь к нашему разговору о {product}. Если есть сомнения - готов обсудить индивидуальные условия.",
            "agent": "Привет! Напоминаю по расчёту на {product}. Клиент определился? Могу пересчитать если нужно.",
        },
        "en": {
            "default": "Hello {name}! Just a friendly reminder about our {product} offer. Are the dates still suitable? I can help with the booking.",
        }
    },
    "special_offer": {
        "ru": {
            "default": "Здравствуйте, {name}! У нас сейчас специальные условия на {product}. Хотите узнать подробности?",
            "VIP": "{name}, для вас у нас есть эксклюзивное предложение по {product}. Готов обсудить персональные условия.",
            "agent": "Привет! Есть промо на {product} - можем предложить лучшую цену для твоего клиента. Интересно?",
        },
        "en": {
            "default": "Hello {name}! We have a special offer for {product} right now. Would you like to know more?",
        }
    },
    "last_attempt": {
        "ru": {
            "default": "Добрый день, {name}! Понимаю, что вы заняты. Просто хотел уточнить - вы ещё планируете {product}? Если нет - не буду беспокоить.",
            "VIP": "{name}, добрый день! Не хочу быть навязчивым. Просто дайте знать, актуален ли ещё {product}? Готов возобновить работу в любой момент.",
            "agent": "Привет! Последний раз спрашиваю по {product} - актуально ещё? Если нет - закрою заявку.",
        },
        "en": {
            "default": "Hello {name}! I understand you're busy. Just wanted to check one last time - are you still planning {product}? If not, no worries at all.",
        }
    },
    "reactivation": {
        "ru": {
            "default": "Здравствуйте, {name}! Давно не общались. Планируете поездку в ОАЭ? У нас появились интересные новинки.",
            "VIP": "{name}, добрый день! Рад был работать с вами в прошлый раз. Планируете ещё визит в ОАЭ? Буду рад снова помочь с организацией.",
            "agent": "Привет! Как дела? Давно не было заявок от тебя. Появились новые туры - могу скинуть прайс?",
        },
        "en": {
            "default": "Hello {name}! It's been a while. Are you planning a trip to UAE? We have some exciting new offerings.",
        }
    },
}

# Продукты для подстановки
PRODUCT_NAMES = {
    "tour": "экскурсии",
    "transfer": "трансферу",
    "yacht": "аренде яхты",
    "tickets": "билетам",
    "car_rental": "аренде авто",
    "catering": "кейтерингу",
    "other": "вашему запросу",
}

# ═══════════════════════════════════════════════════════════════
# КЛАССЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

class FollowupType(str, Enum):
    """Типы follow-up."""
    SOFT_REMINDER = "soft_reminder"
    REPEAT_OFFER = "repeat_offer"
    SPECIAL_OFFER = "special_offer"
    LAST_ATTEMPT = "last_attempt"
    REACTIVATION = "reactivation"


class FollowupReason(str, Enum):
    """Причины для follow-up."""
    NO_RESPONSE = "no_response"           # Нет ответа после нашего сообщения
    INCOMPLETE_DEAL = "incomplete_deal"   # Незавершённая сделка
    ABANDONED_CART = "abandoned_cart"     # Брошенная корзина
    INACTIVE_CLIENT = "inactive_client"   # Неактивный клиент
    LOST_DEAL = "lost_deal"              # Потерянная сделка


@dataclass
class ColdContact:
    """Холодный контакт для follow-up."""
    contact_id: str
    name: str
    phone: str
    contact_type: str
    subtype: str
    language: str

    # Данные о последней активности
    last_our_message: str  # Дата нашего последнего сообщения
    last_their_message: str  # Дата их последнего сообщения
    days_inactive: int

    # Контекст
    last_product: str
    last_stage: str  # Стадия воронки
    reason: str

    # Приоритет и метаданные
    priority: int = 3
    followup_count: int = 0
    last_followup: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FollowupItem:
    """Элемент очереди follow-up."""
    id: str
    contact_id: str
    name: str
    phone: str

    followup_type: str
    reason: str
    message: str

    scheduled_at: str
    priority: int

    # Метаданные
    product: str = ""
    language: str = "ru"
    contact_type: str = ""
    subtype: str = ""

    # Статус
    status: str = "pending"  # pending, sent, failed, cancelled
    sent_at: str = ""
    result: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FollowupStats:
    """Статистика follow-up."""
    total_cold_contacts: int = 0
    total_followups_generated: int = 0
    total_followups_sent: int = 0

    # По типам
    by_type: Dict[str, int] = field(default_factory=dict)
    by_reason: Dict[str, int] = field(default_factory=dict)
    by_priority: Dict[int, int] = field(default_factory=dict)

    # Конверсия
    responses_received: int = 0
    deals_recovered: int = 0
    conversion_rate: float = 0.0

    # Время
    generated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

LOG_DIR = JSON_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "auto_followup.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_json(filepath: Path) -> Any:
    """Загрузка JSON файла."""
    if not filepath.exists():
        logger.warning(f"Файл не найден: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга {filepath}: {e}")
        return None


def load_messages(filepath: Path) -> List[Dict]:
    """Загрузка сообщений из JSONL."""
    messages = []

    if not filepath.exists():
        logger.warning(f"Файл сообщений не найден: {filepath}")
        return messages

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Ошибка загрузки сообщений: {e}")

    return messages


def save_json(data: Any, filepath: Path):
    """Сохранение в JSON файл."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Сохранено: {filepath}")


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ХОЛОДНЫХ КОНТАКТОВ
# ═══════════════════════════════════════════════════════════════

class ColdContactAnalyzer:
    """Анализатор холодных контактов."""

    def __init__(self):
        self.contacts: List[Dict] = []
        self.profiles: Dict[str, Dict] = {}
        self.sales_funnel: List[Dict] = []
        self.operations: List[Dict] = []
        self.messages_by_contact: Dict[str, List[Dict]] = defaultdict(list)

        self.cold_contacts: List[ColdContact] = []
        self.followup_history: List[Dict] = []

    def load_data(self):
        """Загрузка всех данных."""
        logger.info("Загрузка данных...")

        # Контакты
        contacts_data = load_json(CONTACTS_FILE)
        if contacts_data:
            if isinstance(contacts_data, list):
                self.contacts = contacts_data
            elif isinstance(contacts_data, dict):
                self.contacts = contacts_data.get('contacts', [])
        logger.info(f"  Контакты: {len(self.contacts)}")

        # Профили
        profiles_data = load_json(PROFILES_FILE)
        if profiles_data:
            if isinstance(profiles_data, list):
                for p in profiles_data:
                    if p.get('contact_id'):
                        self.profiles[p['contact_id']] = p
            elif isinstance(profiles_data, dict):
                self.profiles = profiles_data
        logger.info(f"  Профили: {len(self.profiles)}")

        # Воронка продаж
        funnel_data = load_json(SALES_FUNNEL_FILE)
        if funnel_data:
            if isinstance(funnel_data, list):
                self.sales_funnel = funnel_data
            elif isinstance(funnel_data, dict):
                self.sales_funnel = funnel_data.get('funnel', [])
        logger.info(f"  Записи воронки: {len(self.sales_funnel)}")

        # Операции
        operations_data = load_json(OPERATIONS_FILE)
        if operations_data:
            if isinstance(operations_data, list):
                self.operations = operations_data
            elif isinstance(operations_data, dict):
                self.operations = operations_data.get('operations', [])
        logger.info(f"  Операции: {len(self.operations)}")

        # Сообщения
        messages = load_messages(MESSAGES_FILE)
        for msg in messages:
            contact_id = msg.get('contact_id') or msg.get('jid')
            if contact_id:
                self.messages_by_contact[contact_id].append(msg)
        logger.info(f"  Сообщения: {len(messages)} в {len(self.messages_by_contact)} чатах")

        # История follow-up
        history_data = load_json(OUTPUT_HISTORY)
        if history_data:
            self.followup_history = history_data.get('history', [])
        logger.info(f"  История follow-up: {len(self.followup_history)}")

    def _get_last_messages(self, contact_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Получить даты последних сообщений.

        Returns:
            (last_our_message, last_their_message, last_product)
        """
        messages = self.messages_by_contact.get(contact_id, [])
        if not messages:
            return None, None, None

        # Сортируем по дате
        sorted_msgs = sorted(
            messages,
            key=lambda x: x.get('datetime', x.get('date', '')),
            reverse=True
        )

        last_our = None
        last_their = None
        last_product = None

        # Определяем продукт из последних сообщений
        product_keywords = {
            "tour": ["экскурси", "тур", "сафари", "обзорн"],
            "transfer": ["трансфер", "встреч", "аэропорт"],
            "yacht": ["яхт", "катер", "морск"],
            "tickets": ["билет", "ferrari", "aquaventure", "парк"],
            "car_rental": ["аренд", "авто", "машин"],
            "catering": ["кейтеринг", "ресторан", "ужин"],
        }

        for msg in sorted_msgs:
            sender = msg.get('sender', '')
            is_outgoing = msg.get('is_outgoing', False) or sender.lower() in ['я', 'me', 'marsel']
            msg_date = msg.get('datetime', msg.get('date', ''))
            text = msg.get('text', '').lower()

            if is_outgoing and not last_our:
                last_our = msg_date
            elif not is_outgoing and not last_their:
                last_their = msg_date

            # Определяем продукт
            if not last_product and text:
                for product, keywords in product_keywords.items():
                    if any(kw in text for kw in keywords):
                        last_product = product
                        break

            if last_our and last_their and last_product:
                break

        return last_our, last_their, last_product or "other"

    def _get_funnel_stage(self, contact_id: str) -> str:
        """Получить стадию воронки для контакта."""
        for record in self.sales_funnel:
            if record.get('contact_id') == contact_id or record.get('jid') == contact_id:
                return record.get('stage', 'unknown')
        return 'unknown'

    def _get_followup_count(self, contact_id: str) -> Tuple[int, str]:
        """Получить количество follow-up и дату последнего."""
        count = 0
        last_date = ""

        for item in self.followup_history:
            if item.get('contact_id') == contact_id:
                count += 1
                item_date = item.get('scheduled_at', '')
                if item_date > last_date:
                    last_date = item_date

        return count, last_date

    def _determine_reason(
        self,
        contact: Dict,
        last_our: Optional[str],
        last_their: Optional[str],
        stage: str,
        days_inactive: int
    ) -> str:
        """Определить причину для follow-up."""
        # Нет ответа после нашего сообщения
        if last_our and (not last_their or last_our > last_their):
            return FollowupReason.NO_RESPONSE.value

        # Незавершённая сделка (есть запрос, но нет оплаты)
        if stage in ['inquiry', 'quote', 'booking']:
            return FollowupReason.INCOMPLETE_DEAL.value

        # Потерянная сделка
        if stage == 'lost':
            return FollowupReason.LOST_DEAL.value

        # Просто неактивный клиент
        if days_inactive >= FOLLOWUP_INTERVALS['reactivation']:
            return FollowupReason.INACTIVE_CLIENT.value

        return FollowupReason.NO_RESPONSE.value

    def _calculate_priority(self, contact: Dict, reason: str, days_inactive: int) -> int:
        """Рассчитать приоритет контакта."""
        # Базовый приоритет по типу клиента
        subtype = contact.get('subtype', '')
        priority = CLIENT_PRIORITY.get(subtype, 3)

        # Повышаем приоритет для незавершённых сделок
        if reason == FollowupReason.INCOMPLETE_DEAL.value:
            priority = max(1, priority - 1)

        # Понижаем для очень холодных контактов
        if days_inactive > FOLLOWUP_INTERVALS['cold_threshold']:
            priority = min(5, priority + 1)

        return priority

    def analyze(self) -> List[ColdContact]:
        """
        Анализ контактов и выявление холодных.

        Returns:
            Список холодных контактов
        """
        logger.info("Анализ холодных контактов...")

        now = datetime.now()
        self.cold_contacts = []

        for contact in self.contacts:
            contact_id = contact.get('contact_id') or contact.get('jid') or contact.get('phone')
            if not contact_id:
                continue

            # Пропускаем исключённые типы
            contact_type = contact.get('type', '')
            if contact_type in EXCLUDED_TYPES:
                continue

            # Получаем даты последних сообщений
            last_our, last_their, last_product = self._get_last_messages(contact_id)

            if not last_our:
                continue  # Нет наших сообщений - пропускаем

            # Вычисляем дни неактивности
            try:
                # Парсим дату
                date_str = last_their or last_our
                if 'T' in date_str:
                    last_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    last_date = datetime.strptime(date_str[:10], '%Y-%m-%d')

                days_inactive = (now - last_date.replace(tzinfo=None)).days
            except (ValueError, TypeError):
                days_inactive = 999

            # Проверяем порог неактивности
            if days_inactive < FOLLOWUP_INTERVALS['soft_reminder']:
                continue  # Ещё активен

            # Получаем данные о воронке
            stage = self._get_funnel_stage(contact_id)

            # Определяем причину
            reason = self._determine_reason(contact, last_our, last_their, stage, days_inactive)

            # Проверяем количество follow-up
            followup_count, last_followup = self._get_followup_count(contact_id)

            if followup_count >= MAX_FOLLOWUPS_PER_CONTACT:
                logger.debug(f"Пропуск {contact_id}: достигнут лимит follow-up")
                continue

            # Проверяем минимальный интервал
            if last_followup:
                try:
                    last_fu_date = datetime.fromisoformat(last_followup)
                    hours_since = (now - last_fu_date).total_seconds() / 3600
                    if hours_since < MIN_FOLLOWUP_INTERVAL_HOURS:
                        continue
                except ValueError:
                    pass

            # Рассчитываем приоритет
            priority = self._calculate_priority(contact, reason, days_inactive)

            # Создаём запись
            cold_contact = ColdContact(
                contact_id=contact_id,
                name=contact.get('name', 'Клиент'),
                phone=contact.get('phone', ''),
                contact_type=contact_type,
                subtype=contact.get('subtype', ''),
                language=contact.get('language', 'ru'),
                last_our_message=last_our or '',
                last_their_message=last_their or '',
                days_inactive=days_inactive,
                last_product=last_product,
                last_stage=stage,
                reason=reason,
                priority=priority,
                followup_count=followup_count,
                last_followup=last_followup,
            )

            self.cold_contacts.append(cold_contact)

        # Сортируем по приоритету и дням неактивности
        self.cold_contacts.sort(key=lambda x: (x.priority, -x.days_inactive))

        logger.info(f"Найдено холодных контактов: {len(self.cold_contacts)}")

        return self.cold_contacts


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАТОР FOLLOW-UP
# ═══════════════════════════════════════════════════════════════

class FollowupGenerator:
    """Генератор follow-up сообщений."""

    def __init__(self, cold_contacts: List[ColdContact]):
        self.cold_contacts = cold_contacts
        self.queue: List[FollowupItem] = []

    def _determine_followup_type(self, contact: ColdContact) -> FollowupType:
        """Определить тип follow-up по дням неактивности."""
        days = contact.days_inactive

        if days < FOLLOWUP_INTERVALS['repeat_offer']:
            return FollowupType.SOFT_REMINDER
        elif days < FOLLOWUP_INTERVALS['special_offer']:
            return FollowupType.REPEAT_OFFER
        elif days < FOLLOWUP_INTERVALS['last_attempt']:
            return FollowupType.SPECIAL_OFFER
        elif days < FOLLOWUP_INTERVALS['reactivation']:
            return FollowupType.LAST_ATTEMPT
        else:
            return FollowupType.REACTIVATION

    def _get_template(
        self,
        followup_type: FollowupType,
        language: str,
        subtype: str,
        contact_type: str
    ) -> str:
        """Получить шаблон сообщения."""
        templates = FOLLOWUP_TEMPLATES.get(followup_type.value, {})
        lang_templates = templates.get(language, templates.get('ru', {}))

        # Выбираем шаблон по подтипу
        if subtype == 'VIP':
            template = lang_templates.get('VIP', lang_templates.get('default', ''))
        elif contact_type in ['агенты'] or subtype in ['турагент', 'туроператор', 'B2B']:
            template = lang_templates.get('agent', lang_templates.get('default', ''))
        else:
            template = lang_templates.get('default', '')

        return template

    def _format_message(
        self,
        template: str,
        name: str,
        product: str,
        language: str
    ) -> str:
        """Форматирование сообщения с подстановкой переменных."""
        # Получаем название продукта
        product_name = PRODUCT_NAMES.get(product, PRODUCT_NAMES['other'])

        # Используем только имя (без фамилии)
        first_name = name.split()[0] if name else 'Клиент'

        # Подставляем переменные
        message = template.format(
            name=first_name,
            product=product_name,
        )

        return message

    def _generate_id(self, contact_id: str, followup_type: str) -> str:
        """Генерация уникального ID для follow-up."""
        data = f"{contact_id}:{followup_type}:{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def generate(self) -> List[FollowupItem]:
        """
        Генерация follow-up для всех холодных контактов.

        Returns:
            Список элементов очереди
        """
        logger.info("Генерация follow-up сообщений...")

        self.queue = []
        now = datetime.now()

        for contact in self.cold_contacts:
            # Определяем тип follow-up
            followup_type = self._determine_followup_type(contact)

            # Получаем шаблон
            template = self._get_template(
                followup_type,
                contact.language,
                contact.subtype,
                contact.contact_type
            )

            if not template:
                logger.warning(f"Нет шаблона для {followup_type.value}/{contact.language}")
                continue

            # Форматируем сообщение
            message = self._format_message(
                template,
                contact.name,
                contact.last_product,
                contact.language
            )

            # Планируем время отправки (учитываем приоритет)
            # Высокий приоритет - раньше
            delay_hours = contact.priority * 2  # 2, 4, 6, ... часов
            scheduled_at = now + timedelta(hours=delay_hours)

            # Создаём элемент очереди
            item = FollowupItem(
                id=self._generate_id(contact.contact_id, followup_type.value),
                contact_id=contact.contact_id,
                name=contact.name,
                phone=contact.phone,
                followup_type=followup_type.value,
                reason=contact.reason,
                message=message,
                scheduled_at=scheduled_at.isoformat(),
                priority=contact.priority,
                product=contact.last_product,
                language=contact.language,
                contact_type=contact.contact_type,
                subtype=contact.subtype,
            )

            self.queue.append(item)

        logger.info(f"Сгенерировано follow-up: {len(self.queue)}")

        return self.queue


# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИИ
# ═══════════════════════════════════════════════════════════════

class Bitrix24TaskCreator:
    """Создание задач в Bitrix24."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = None

    def connect(self) -> bool:
        """Подключение к Bitrix24."""
        if self.dry_run:
            logger.info("[DRY-RUN] Пропуск подключения к Bitrix24")
            return True

        try:
            from bitrix24_integration import Bitrix24Client, BITRIX24_CONFIG

            if not all([BITRIX24_CONFIG.get('domain'),
                       BITRIX24_CONFIG.get('user_id'),
                       BITRIX24_CONFIG.get('webhook_key')]):
                logger.warning("Bitrix24 не настроен")
                return False

            self.client = Bitrix24Client(
                domain=BITRIX24_CONFIG['domain'],
                user_id=BITRIX24_CONFIG['user_id'],
                webhook_key=BITRIX24_CONFIG['webhook_key'],
                dry_run=self.dry_run
            )

            return self.client.test_connection()

        except ImportError:
            logger.warning("Модуль bitrix24_integration не найден")
            return False
        except Exception as e:
            logger.error(f"Ошибка подключения к Bitrix24: {e}")
            return False

    def create_activity(self, item: FollowupItem) -> Optional[int]:
        """
        Создание CRM активности для follow-up.

        Returns:
            ID созданной активности или None
        """
        if self.dry_run:
            logger.info(f"[DRY-RUN] Создание активности: {item.name}")
            return 999999

        if not self.client:
            return None

        try:
            # Находим контакт в Б24
            contact_id = self.client.find_contact_by_phone(item.phone)

            if not contact_id:
                logger.warning(f"Контакт не найден в Б24: {item.phone}")
                return None

            # Создаём активность
            params = {
                "fields": {
                    "OWNER_TYPE_ID": 3,  # Контакт
                    "OWNER_ID": contact_id,
                    "TYPE_ID": 2,  # Звонок
                    "SUBJECT": f"Follow-up: {item.name}",
                    "DESCRIPTION": item.message,
                    "PRIORITY": 4 - item.priority,  # Инвертируем (1=высокий)
                    "RESPONSIBLE_ID": 1,  # Ответственный
                    "START_TIME": item.scheduled_at,
                    "END_TIME": item.scheduled_at,
                    "COMPLETED": "N",
                    "DIRECTION": 2,  # Исходящий
                }
            }

            result = self.client._call("crm.activity.add", params)
            return int(result.get('result', 0))

        except Exception as e:
            logger.error(f"Ошибка создания активности: {e}")
            return None

    def create_tasks(self, queue: List[FollowupItem]) -> int:
        """
        Создание задач для всех элементов очереди.

        Returns:
            Количество созданных задач
        """
        if not self.connect():
            logger.error("Не удалось подключиться к Bitrix24")
            return 0

        created = 0

        for item in queue:
            activity_id = self.create_activity(item)
            if activity_id:
                created += 1
                logger.debug(f"Создана активность {activity_id} для {item.name}")

        logger.info(f"Создано активностей в Bitrix24: {created}")
        return created


class GoogleCalendarScheduler:
    """Планирование в Google Calendar."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.sync = None

    def connect(self) -> bool:
        """Подключение к Google Calendar."""
        if self.dry_run:
            logger.info("[DRY-RUN] Пропуск подключения к Google Calendar")
            return True

        try:
            from google_calendar_sync import GoogleCalendarSync

            self.sync = GoogleCalendarSync(dry_run=self.dry_run)
            return self.sync.connect()

        except ImportError:
            logger.warning("Модуль google_calendar_sync не найден")
            return False
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Calendar: {e}")
            return False

    def schedule_followup(self, item: FollowupItem) -> Optional[str]:
        """
        Создание события для follow-up.

        Returns:
            ID события или None
        """
        if self.dry_run:
            logger.info(f"[DRY-RUN] Планирование: {item.name}")
            return "dry-run-id"

        if not self.sync:
            return None

        try:
            # Парсим дату
            scheduled = datetime.fromisoformat(item.scheduled_at)
            date_str = scheduled.strftime('%Y-%m-%d')
            time_str = scheduled.strftime('%H:%M')

            # Эмодзи по типу
            emoji = {
                'soft_reminder': '💬',
                'repeat_offer': '🔄',
                'special_offer': '🎁',
                'last_attempt': '⚠️',
                'reactivation': '🔔',
            }.get(item.followup_type, '📋')

            title = f"{emoji} Follow-up: {item.name}"

            # Описание
            desc_parts = [
                f"Тип: {item.followup_type}",
                f"Причина: {item.reason}",
                f"Телефон: {item.phone}",
                "",
                "Сообщение:",
                item.message,
            ]
            description = "\n".join(desc_parts)

            # Создаём событие
            event_id = self.sync.create_event(
                title=title,
                date=date_str,
                time=time_str,
                duration_hours=0.5,
                description=description,
                color_id="6",  # Оранжевый
            )

            return event_id

        except Exception as e:
            logger.error(f"Ошибка планирования: {e}")
            return None

    def schedule_all(self, queue: List[FollowupItem]) -> int:
        """
        Планирование всех follow-up.

        Returns:
            Количество запланированных
        """
        if not self.connect():
            logger.error("Не удалось подключиться к Google Calendar")
            return 0

        scheduled = 0

        for item in queue:
            event_id = self.schedule_followup(item)
            if event_id:
                scheduled += 1
                logger.debug(f"Запланировано: {item.name}")

        logger.info(f"Запланировано в Google Calendar: {scheduled}")
        return scheduled


# ═══════════════════════════════════════════════════════════════
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════════════════════════════

def save_queue(queue: List[FollowupItem]):
    """Сохранение очереди follow-up."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_items": len(queue),
        "queue": [item.to_dict() for item in queue]
    }
    save_json(data, OUTPUT_QUEUE)


def update_history(queue: List[FollowupItem]):
    """Обновление истории follow-up."""
    # Загружаем существующую историю
    existing = load_json(OUTPUT_HISTORY) or {"history": []}
    history = existing.get('history', [])

    # Добавляем новые записи
    for item in queue:
        history.append(item.to_dict())

    # Сохраняем
    data = {
        "updated_at": datetime.now().isoformat(),
        "total_items": len(history),
        "history": history
    }
    save_json(data, OUTPUT_HISTORY)


def calculate_stats(
    cold_contacts: List[ColdContact],
    queue: List[FollowupItem]
) -> FollowupStats:
    """Расчёт статистики."""
    stats = FollowupStats(
        total_cold_contacts=len(cold_contacts),
        total_followups_generated=len(queue),
        generated_at=datetime.now().isoformat(),
    )

    # По типам
    for item in queue:
        stats.by_type[item.followup_type] = stats.by_type.get(item.followup_type, 0) + 1
        stats.by_reason[item.reason] = stats.by_reason.get(item.reason, 0) + 1
        stats.by_priority[item.priority] = stats.by_priority.get(item.priority, 0) + 1

    # Загружаем историю для расчёта конверсии
    history = load_json(OUTPUT_HISTORY) or {"history": []}
    sent_items = [h for h in history.get('history', []) if h.get('status') == 'sent']
    responded_items = [h for h in sent_items if h.get('result') == 'responded']

    stats.total_followups_sent = len(sent_items)
    stats.responses_received = len(responded_items)

    if stats.total_followups_sent > 0:
        stats.conversion_rate = round(
            stats.responses_received / stats.total_followups_sent * 100, 2
        )

    return stats


def save_stats(stats: FollowupStats):
    """Сохранение статистики."""
    save_json(stats.to_dict(), OUTPUT_STATS)


# ═══════════════════════════════════════════════════════════════
# ВЫВОД ОТЧЁТА
# ═══════════════════════════════════════════════════════════════

def print_report(
    cold_contacts: List[ColdContact],
    queue: List[FollowupItem],
    stats: FollowupStats
):
    """Вывод отчёта в консоль."""
    print("\n" + "=" * 60)
    print("ОТЧЁТ ПО FOLLOW-UP")
    print("=" * 60)

    print(f"\nХолодных контактов: {stats.total_cold_contacts}")
    print(f"Сгенерировано follow-up: {stats.total_followups_generated}")

    if stats.by_type:
        print("\nПо типам:")
        for ftype, count in sorted(stats.by_type.items()):
            print(f"  {ftype}: {count}")

    if stats.by_reason:
        print("\nПо причинам:")
        for reason, count in sorted(stats.by_reason.items()):
            print(f"  {reason}: {count}")

    if stats.by_priority:
        print("\nПо приоритету:")
        for priority, count in sorted(stats.by_priority.items()):
            print(f"  Приоритет {priority}: {count}")

    if stats.total_followups_sent > 0:
        print(f"\nКонверсия:")
        print(f"  Отправлено: {stats.total_followups_sent}")
        print(f"  Ответов: {stats.responses_received}")
        print(f"  Конверсия: {stats.conversion_rate}%")

    # Топ-10 контактов для follow-up
    if queue:
        print("\n" + "-" * 40)
        print("ТОП-10 КОНТАКТОВ ДЛЯ FOLLOW-UP:")
        print("-" * 40)

        for i, item in enumerate(queue[:10], 1):
            print(f"\n{i}. {item.name} ({item.phone})")
            print(f"   Тип: {item.followup_type}")
            print(f"   Причина: {item.reason}")
            print(f"   Приоритет: {item.priority}")
            print(f"   Сообщение: {item.message[:80]}...")

    print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Система автоматических follow-up напоминаний',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python auto_followup.py --analyze          Анализ холодных контактов
  python auto_followup.py --generate         Генерация follow-up
  python auto_followup.py --create-tasks     Создать задачи в Bitrix24
  python auto_followup.py --schedule         Запланировать в Google Calendar
  python auto_followup.py --all              Всё вместе
  python auto_followup.py --all --dry-run    Тестовый режим

Настройки временных интервалов в config.py:
  FOLLOWUP_INTERVALS = {
      "soft_reminder": 1,    # день
      "repeat_offer": 3,     # дня
      "special_offer": 7,    # дней
      "last_attempt": 14,    # дней
      "reactivation": 30,    # дней
  }
        """
    )

    # Режимы работы
    mode_group = parser.add_argument_group('Режимы')
    mode_group.add_argument(
        '--analyze', '-a',
        action='store_true',
        help='Анализ холодных контактов'
    )
    mode_group.add_argument(
        '--generate', '-g',
        action='store_true',
        help='Генерация follow-up сообщений'
    )
    mode_group.add_argument(
        '--create-tasks',
        action='store_true',
        help='Создать задачи в Bitrix24'
    )
    mode_group.add_argument(
        '--schedule',
        action='store_true',
        help='Запланировать в Google Calendar'
    )
    mode_group.add_argument(
        '--all',
        action='store_true',
        help='Выполнить все операции'
    )

    # Опции
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Тестовый режим (без реальных действий)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=0,
        help='Ограничить количество контактов'
    )
    parser.add_argument(
        '--priority', '-p',
        type=int,
        choices=[1, 2, 3, 4, 5],
        help='Фильтр по приоритету'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Путь для сохранения очереди'
    )

    args = parser.parse_args()

    # Если ничего не указано - показываем справку
    if not any([args.analyze, args.generate, args.create_tasks, args.schedule, args.all]):
        parser.print_help()
        return

    # Настройка логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("=" * 60)
    print("AUTO FOLLOW-UP SYSTEM")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.dry_run:
        print("[DRY-RUN] Тестовый режим - реальные действия НЕ выполняются")

    # 1. Анализ холодных контактов
    if args.all or args.analyze or args.generate:
        analyzer = ColdContactAnalyzer()
        analyzer.load_data()
        cold_contacts = analyzer.analyze()

        # Применяем фильтры
        if args.priority:
            cold_contacts = [c for c in cold_contacts if c.priority == args.priority]

        if args.limit > 0:
            cold_contacts = cold_contacts[:args.limit]
    else:
        cold_contacts = []

    # 2. Генерация follow-up
    queue = []
    if args.all or args.generate:
        generator = FollowupGenerator(cold_contacts)
        queue = generator.generate()

        # Сохраняем очередь
        output_path = Path(args.output) if args.output else OUTPUT_QUEUE
        save_queue(queue)

        if not args.dry_run:
            update_history(queue)

    # 3. Создание задач в Bitrix24
    if args.all or args.create_tasks:
        if queue:
            creator = Bitrix24TaskCreator(dry_run=args.dry_run)
            creator.create_tasks(queue)
        else:
            logger.warning("Очередь пуста, задачи не созданы")

    # 4. Планирование в Google Calendar
    if args.all or args.schedule:
        if queue:
            scheduler = GoogleCalendarScheduler(dry_run=args.dry_run)
            scheduler.schedule_all(queue)
        else:
            logger.warning("Очередь пуста, события не запланированы")

    # 5. Статистика и отчёт
    stats = calculate_stats(cold_contacts, queue)
    save_stats(stats)
    print_report(cold_contacts, queue, stats)

    print("\n[OK] Готово!")


if __name__ == "__main__":
    main()
