#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Загрузка истории WhatsApp в таймлайн контактов Битрикс24 и синхронизация с календарём.

Функционал:
- Добавление истории чата в таймлайн контакта (summary/important/full)
- Синхронизация бронирований и прилётов с календарём Б24
- Создание follow-up задач на основе анализа чатов

Использование:
    python bitrix24_timeline.py --sync-timeline --mode summary  # AI-саммари переписки
    python bitrix24_timeline.py --sync-timeline --contact-id 123  # Для конкретного контакта
    python bitrix24_timeline.py --sync-calendar                  # Синхронизировать календарь
    python bitrix24_timeline.py --create-tasks                   # Создать задачи
    python bitrix24_timeline.py --sync-all                       # Всё вместе
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

import requests

# Добавляем путь к скриптам
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import JSON_DIR, RAW_DIR

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

BITRIX24_CONFIG = {
    "domain": os.getenv("BITRIX24_DOMAIN", ""),
    "user_id": os.getenv("BITRIX24_USER_ID", ""),
    "webhook_key": os.getenv("BITRIX24_WEBHOOK_KEY", ""),
}

# Пути к входным файлам
INPUT_FILES = {
    "messages": RAW_DIR / "all_messages.jsonl",
    "contacts": JSON_DIR / "contacts.json",
    "operations": JSON_DIR / "operations.json",
    "travel_dates": JSON_DIR / "travel_dates.json",
}

# Rate limiting
RATE_LIMIT_REQUESTS = 2
REQUEST_TIMEOUT = 30

# Паттерны для извлечения важной информации
PRICE_PATTERN = re.compile(r'(\d[\d\s]*)\s*(AED|USD|RUB|дирхам|руб|доллар)', re.IGNORECASE)
BOOKING_KEYWORDS = ['бронь', 'бронирование', 'подтверждаю', 'оплата', 'оплачено', 'забронировано']
COMPLAINT_KEYWORDS = ['проблема', 'жалоба', 'недоволен', 'плохо', 'отмена', 'возврат', 'обман']

# ═══════════════════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

LOG_DIR = JSON_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "bitrix24_timeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# КЛАССЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ChatSummary:
    """Саммари чата с клиентом."""
    jid: str
    contact_name: str
    period_start: str
    period_end: str
    total_messages: int
    messages_from_client: int
    messages_from_us: int
    key_requests: list = field(default_factory=list)
    total_spent: float = 0
    currency: str = "AED"
    operations_count: int = 0
    last_messages: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    sentiment: str = "neutral"  # positive/negative/neutral
    has_complaints: bool = False
    days_since_last_message: int = 0


@dataclass
class SyncResult:
    """Результат синхронизации."""
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    details: list = field(default_factory=list)

    def add_created(self, item_id: int, name: str):
        self.created += 1
        self.details.append({"action": "created", "id": item_id, "name": name})

    def add_updated(self, item_id: int, name: str):
        self.updated += 1
        self.details.append({"action": "updated", "id": item_id, "name": name})

    def add_skipped(self, name: str, reason: str):
        self.skipped += 1
        self.details.append({"action": "skipped", "name": name, "reason": reason})

    def add_error(self, name: str, error: str):
        self.errors += 1
        self.details.append({"action": "error", "name": name, "error": error})

    def to_dict(self) -> dict:
        return {
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "errors": self.errors,
            "total": self.created + self.updated + self.skipped + self.errors,
            "details": self.details
        }


# ═══════════════════════════════════════════════════════════════════════════
# BITRIX24 API КЛИЕНТ (расширенный)
# ═══════════════════════════════════════════════════════════════════════════

class Bitrix24TimelineClient:
    """Клиент для работы с таймлайном, календарём и задачами Битрикс24."""

    def __init__(self, domain: str, user_id: str, webhook_key: str, dry_run: bool = False):
        self.domain = domain
        self.user_id = user_id
        self.webhook_key = webhook_key
        self.dry_run = dry_run
        self.base_url = f"https://{domain}.bitrix24.ru/rest/{user_id}/{webhook_key}"
        self.last_request_time = 0
        self.session = requests.Session()

        # Кэш
        self._calendar_id: Optional[int] = None
        self._contacts_cache: dict[str, dict] = {}  # jid -> contact_data

    def _rate_limit(self):
        """Соблюдение rate limiting."""
        import time
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0 / RATE_LIMIT_REQUESTS:
            time.sleep(1.0 / RATE_LIMIT_REQUESTS - elapsed)
        self.last_request_time = time.time()

    def _call(self, method: str, params: Optional[dict] = None) -> dict:
        """Выполнение REST API запроса."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] {method}: {json.dumps(params, ensure_ascii=False)[:200]}...")
            if method.endswith(".add"):
                return {"result": 999999}
            elif method.endswith(".update"):
                return {"result": True}
            elif method.endswith(".list") or method.endswith(".get"):
                return {"result": []}
            return {"result": True}

        self._rate_limit()

        url = f"{self.base_url}/{method}"
        try:
            response = self.session.post(
                url,
                json=params or {},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise Bitrix24Error(data["error"], data.get("error_description", ""))

            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP ошибка при вызове {method}: {e}")
            raise

    # ─────────────────────────────────────────────────────────────────────
    # ТАЙМЛАЙН
    # ─────────────────────────────────────────────────────────────────────

    def add_timeline_comment(
        self,
        entity_type: str,
        entity_id: int,
        comment: str,
        author_id: Optional[int] = None
    ) -> int:
        """
        Добавить комментарий в таймлайн сущности CRM.

        Args:
            entity_type: тип сущности (CONTACT, DEAL, LEAD)
            entity_id: ID сущности
            comment: текст комментария (HTML поддерживается)
            author_id: ID автора (по умолчанию текущий пользователь)

        Returns:
            ID созданного комментария
        """
        params = {
            "fields": {
                "ENTITY_ID": entity_id,
                "ENTITY_TYPE": entity_type,
                "COMMENT": comment,
            }
        }

        if author_id:
            params["fields"]["AUTHOR_ID"] = author_id

        result = self._call("crm.timeline.comment.add", params)
        return int(result.get("result", 0))

    def get_timeline_comments(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50
    ) -> list:
        """Получить комментарии из таймлайна."""
        params = {
            "filter": {
                "ENTITY_TYPE": entity_type,
                "ENTITY_ID": entity_id,
            },
            "order": {"ID": "DESC"},
            "select": ["ID", "COMMENT", "CREATED", "AUTHOR_ID"],
        }

        result = self._call("crm.timeline.comment.list", params)
        return result.get("result", [])[:limit]

    def delete_timeline_comment(self, comment_id: int) -> bool:
        """Удалить комментарий из таймлайна."""
        result = self._call("crm.timeline.comment.delete", {"id": comment_id})
        return bool(result.get("result"))

    # ─────────────────────────────────────────────────────────────────────
    # КАЛЕНДАРЬ
    # ─────────────────────────────────────────────────────────────────────

    def get_calendar_sections(self) -> list:
        """Получить список секций (календарей)."""
        params = {
            "type": "user",
            "ownerId": self.user_id
        }
        result = self._call("calendar.section.get", params)
        return result.get("result", [])

    def get_or_create_crm_calendar(self, name: str = "WhatsApp Бронирования") -> int:
        """
        Получить ID календаря для CRM событий или создать новый.

        Args:
            name: название календаря

        Returns:
            ID календаря
        """
        if self._calendar_id:
            return self._calendar_id

        # Ищем существующий
        sections = self.get_calendar_sections()
        for section in sections:
            if section.get("NAME") == name:
                self._calendar_id = int(section["ID"])
                logger.info(f"Найден календарь: {name} (ID: {self._calendar_id})")
                return self._calendar_id

        # Создаём новый
        if self.dry_run:
            self._calendar_id = 999999
            return self._calendar_id

        params = {
            "type": "user",
            "ownerId": self.user_id,
            "name": name,
            "description": "Бронирования и события из WhatsApp",
            "color": "#FF5722",  # Оранжевый
            "access": {"U": self.user_id}
        }

        result = self._call("calendar.section.add", params)
        self._calendar_id = int(result.get("result", 0))
        logger.info(f"Создан календарь: {name} (ID: {self._calendar_id})")
        return self._calendar_id

    def add_calendar_event(
        self,
        name: str,
        description: str,
        date_from: str,
        date_to: Optional[str] = None,
        section_id: Optional[int] = None,
        is_meeting: bool = False,
        attendees: Optional[list] = None,
        location: str = "",
        importance: str = "normal"
    ) -> int:
        """
        Добавить событие в календарь.

        Args:
            name: название события
            description: описание
            date_from: дата/время начала (YYYY-MM-DD HH:MM:SS)
            date_to: дата/время окончания (если None - целый день)
            section_id: ID секции календаря
            is_meeting: это встреча (приглашение участников)
            attendees: список участников [user_id, ...]
            location: место
            importance: важность (high/normal/low)

        Returns:
            ID события
        """
        if section_id is None:
            section_id = self.get_or_create_crm_calendar()

        # Парсим дату
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")

        if date_to:
            try:
                dt_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt_to = datetime.strptime(date_to, "%Y-%m-%d")
        else:
            # Событие на целый день
            dt_to = dt_from + timedelta(hours=1)

        params = {
            "type": "user",
            "ownerId": self.user_id,
            "name": name,
            "description": description,
            "from": dt_from.strftime("%Y-%m-%dT%H:%M:%S"),
            "to": dt_to.strftime("%Y-%m-%dT%H:%M:%S"),
            "section": section_id,
            "skip_time": "N" if date_to else "Y",
            "importance": importance,
        }

        if location:
            params["location"] = location

        if is_meeting and attendees:
            params["is_meeting"] = "Y"
            params["attendees"] = attendees

        result = self._call("calendar.event.add", params)
        return int(result.get("result", 0))

    def find_calendar_events(
        self,
        date_from: str,
        date_to: str,
        section_id: Optional[int] = None
    ) -> list:
        """Поиск событий в календаре за период."""
        if section_id is None:
            section_id = self.get_or_create_crm_calendar()

        params = {
            "type": "user",
            "ownerId": self.user_id,
            "from": date_from,
            "to": date_to,
            "section": [section_id]
        }

        result = self._call("calendar.event.get", params)
        return result.get("result", [])

    # ─────────────────────────────────────────────────────────────────────
    # ЗАДАЧИ
    # ─────────────────────────────────────────────────────────────────────

    def create_task(
        self,
        title: str,
        description: str = "",
        responsible_id: Optional[int] = None,
        deadline: Optional[str] = None,
        priority: int = 1,
        crm_entity: Optional[tuple[str, int]] = None,
        tags: Optional[list] = None
    ) -> int:
        """
        Создать задачу.

        Args:
            title: заголовок задачи
            description: описание
            responsible_id: ответственный (по умолчанию текущий пользователь)
            deadline: срок выполнения (YYYY-MM-DD HH:MM:SS)
            priority: приоритет (0=низкий, 1=средний, 2=высокий)
            crm_entity: связь с CRM (тип, id), например ("C", 123) для контакта
            tags: теги

        Returns:
            ID задачи
        """
        params = {
            "fields": {
                "TITLE": title,
                "DESCRIPTION": description,
                "RESPONSIBLE_ID": responsible_id or self.user_id,
                "CREATED_BY": self.user_id,
                "PRIORITY": priority,
            }
        }

        if deadline:
            params["fields"]["DEADLINE"] = deadline

        if crm_entity:
            entity_type, entity_id = crm_entity
            params["fields"]["UF_CRM_TASK"] = [f"{entity_type}_{entity_id}"]

        if tags:
            params["fields"]["TAGS"] = tags

        result = self._call("tasks.task.add", params)
        task_result = result.get("result", {})
        if isinstance(task_result, dict):
            return int(task_result.get("task", {}).get("id", 0))
        return 0

    def get_tasks(
        self,
        filter_params: Optional[dict] = None,
        limit: int = 50
    ) -> list:
        """Получить список задач."""
        params = {
            "select": ["ID", "TITLE", "STATUS", "DEADLINE", "UF_CRM_TASK"],
            "order": {"DEADLINE": "asc"},
            "limit": limit
        }

        if filter_params:
            params["filter"] = filter_params

        result = self._call("tasks.task.list", params)
        # Обработка разных форматов ответа
        res = result.get("result", {})
        if isinstance(res, dict):
            return res.get("tasks", [])
        return []

    # ─────────────────────────────────────────────────────────────────────
    # КОНТАКТЫ (для связывания)
    # ─────────────────────────────────────────────────────────────────────

    def find_contact_by_phone(self, phone: str) -> Optional[dict]:
        """Поиск контакта по телефону."""
        normalized = self._normalize_phone(phone)

        if self.dry_run:
            return None

        result = self._call("crm.contact.list", {
            "filter": {"PHONE": phone},
            "select": ["ID", "NAME", "LAST_NAME", "PHONE", "UF_CRM_WHATSAPP_JID"]
        })

        contacts = result.get("result", [])
        if contacts:
            return contacts[0]

        return None

    def find_contact_by_jid(self, jid: str) -> Optional[dict]:
        """Поиск контакта по WhatsApp JID."""
        if self.dry_run:
            return None

        result = self._call("crm.contact.list", {
            "filter": {"UF_CRM_WHATSAPP_JID": jid},
            "select": ["ID", "NAME", "LAST_NAME", "PHONE", "UF_CRM_WHATSAPP_JID"]
        })

        contacts = result.get("result", [])
        if contacts:
            return contacts[0]

        return None

    def get_all_contacts_with_jid(self) -> dict[str, dict]:
        """Получить все контакты с WhatsApp JID."""
        if self.dry_run:
            return {}

        all_contacts = []
        start = 0

        while True:
            result = self._call("crm.contact.list", {
                "filter": {"!UF_CRM_WHATSAPP_JID": ""},
                "select": ["ID", "NAME", "LAST_NAME", "PHONE", "UF_CRM_WHATSAPP_JID"],
                "start": start
            })

            contacts = result.get("result", [])
            if not contacts:
                break

            all_contacts.extend(contacts)

            if result.get("next"):
                start = result["next"]
            else:
                break

        # Индексируем по JID
        self._contacts_cache = {
            c.get("UF_CRM_WHATSAPP_JID"): c
            for c in all_contacts
            if c.get("UF_CRM_WHATSAPP_JID")
        }

        logger.info(f"Загружено {len(self._contacts_cache)} контактов с WhatsApp JID")
        return self._contacts_cache

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Нормализация номера телефона."""
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
        if cleaned.startswith("8") and len(cleaned) == 11:
            cleaned = "+7" + cleaned[1:]
        if not cleaned.startswith("+"):
            if cleaned.startswith("7") and len(cleaned) == 11:
                cleaned = "+" + cleaned
            elif len(cleaned) == 10:
                cleaned = "+7" + cleaned
        return cleaned

    def test_connection(self) -> bool:
        """Проверка подключения."""
        if self.dry_run:
            logger.info("[DRY-RUN] Пропуск проверки подключения")
            return True

        try:
            self._call("crm.contact.list", {"select": ["ID"], "start": 0})
            logger.info("Подключение к Bitrix24 успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            return False


class Bitrix24Error(Exception):
    """Ошибка API Битрикс24."""

    def __init__(self, error_code: str, error_description: str):
        self.error_code = error_code
        self.error_description = error_description
        super().__init__(f"{error_code}: {error_description}")


# ═══════════════════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════

def load_json_file(file_path: Path) -> list:
    """Загрузка JSON файла."""
    if not file_path.exists():
        logger.warning(f"Файл не найден: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON {file_path}: {e}")
        return []


def load_messages_by_jid(messages_file: Path) -> dict[str, list]:
    """
    Загрузить сообщения, сгруппированные по JID.

    Returns:
        dict: jid -> список сообщений
    """
    if not messages_file.exists():
        logger.warning(f"Файл сообщений не найден: {messages_file}")
        return {}

    messages_by_jid = defaultdict(list)

    try:
        with open(messages_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    jid = msg.get("jid", "")
                    if jid:
                        messages_by_jid[jid].append(msg)
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.error(f"Ошибка чтения сообщений: {e}")

    # Сортируем по дате
    for jid in messages_by_jid:
        messages_by_jid[jid].sort(key=lambda m: m.get("datetime", ""))

    logger.info(f"Загружено сообщений для {len(messages_by_jid)} чатов")
    return dict(messages_by_jid)


# ═══════════════════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ САММАРИ
# ═══════════════════════════════════════════════════════════════════════════

def generate_chat_summary(
    jid: str,
    messages: list,
    contact: Optional[dict] = None,
    operations: Optional[list] = None
) -> ChatSummary:
    """
    Сгенерировать саммари переписки.

    Args:
        jid: WhatsApp JID
        messages: список сообщений
        contact: данные контакта
        operations: операции по этому контакту

    Returns:
        ChatSummary
    """
    if not messages:
        return ChatSummary(
            jid=jid,
            contact_name="Неизвестный",
            period_start="",
            period_end="",
            total_messages=0,
            messages_from_client=0,
            messages_from_us=0
        )

    # Базовая статистика
    contact_name = messages[0].get("chat_name", "Неизвестный")
    if contact and contact.get("name"):
        contact_name = contact["name"]

    period_start = messages[0].get("datetime", "")[:10]
    period_end = messages[-1].get("datetime", "")[:10]

    messages_from_client = sum(1 for m in messages if not m.get("is_from_me"))
    messages_from_us = sum(1 for m in messages if m.get("is_from_me"))

    # Извлекаем ключевые запросы (упоминания продуктов и цен)
    key_requests = []
    prices_mentioned = []
    has_complaints = False

    for msg in messages:
        text = msg.get("text", "").lower()

        # Ищем цены
        price_matches = PRICE_PATTERN.findall(msg.get("text", ""))
        for price, currency in price_matches:
            prices_mentioned.append({
                "amount": int("".join(price.split())),
                "currency": currency.upper(),
                "context": msg.get("text", "")[:100]
            })

        # Ищем бронирования
        for keyword in BOOKING_KEYWORDS:
            if keyword in text:
                key_requests.append({
                    "type": "booking",
                    "text": msg.get("text", "")[:150],
                    "date": msg.get("datetime", "")[:10]
                })
                break

        # Ищем жалобы
        for keyword in COMPLAINT_KEYWORDS:
            if keyword in text:
                has_complaints = True
                key_requests.append({
                    "type": "complaint",
                    "text": msg.get("text", "")[:150],
                    "date": msg.get("datetime", "")[:10]
                })
                break

    # Финансы из операций
    total_spent = 0
    operations_count = 0
    currency = "AED"

    if operations:
        phone = jid.replace("@s.whatsapp.net", "")
        contact_ops = [
            op for op in operations
            if phone in op.get("phone", "")
        ]
        operations_count = len(contact_ops)
        for op in contact_ops:
            if op.get("status") == "completed":
                total_spent += op.get("amount", 0)
        if contact_ops:
            currency = contact_ops[0].get("currency", "AED")

    # Последние сообщения
    last_messages = []
    for msg in messages[-5:]:
        sender = "Клиент" if not msg.get("is_from_me") else "Мы"
        date = msg.get("datetime", "")[:10]
        text = msg.get("text", "")[:100]
        if text:
            last_messages.append({
                "date": date,
                "sender": sender,
                "text": text
            })

    # Теги из контакта
    tags = []
    if contact and contact.get("tags"):
        tags = contact["tags"]

    # Определяем настроение
    sentiment = "neutral"
    if has_complaints:
        sentiment = "negative"
    elif total_spent > 5000:
        sentiment = "positive"
    elif messages_from_client > messages_from_us * 2:
        sentiment = "positive"  # Активный клиент

    # Дней с последнего сообщения
    days_since_last = 0
    if period_end:
        try:
            last_date = datetime.strptime(period_end, "%Y-%m-%d")
            days_since_last = (datetime.now() - last_date).days
        except ValueError:
            pass

    return ChatSummary(
        jid=jid,
        contact_name=contact_name,
        period_start=period_start,
        period_end=period_end,
        total_messages=len(messages),
        messages_from_client=messages_from_client,
        messages_from_us=messages_from_us,
        key_requests=key_requests[:10],  # Максимум 10
        total_spent=total_spent,
        currency=currency,
        operations_count=operations_count,
        last_messages=last_messages,
        tags=tags,
        sentiment=sentiment,
        has_complaints=has_complaints,
        days_since_last_message=days_since_last
    )


def format_timeline_comment(summary: ChatSummary, mode: str = "summary") -> str:
    """
    Форматировать саммари в комментарий для таймлайна.

    Args:
        summary: ChatSummary
        mode: режим (summary/important/full)

    Returns:
        HTML строка для комментария
    """
    # Форматируем период
    period_str = f"{summary.period_start} — {summary.period_end}"

    # Базовый заголовок
    html = f"""<b>История WhatsApp</b>

<b>Период:</b> {period_str}
<b>Сообщений:</b> {summary.total_messages} (от клиента: {summary.messages_from_client}, наших: {summary.messages_from_us})
"""

    # Ключевые запросы (только для summary и important)
    if mode in ["summary", "important"] and summary.key_requests:
        html += "\n<b>Ключевые запросы:</b>\n"
        for req in summary.key_requests[:5]:
            status = "!" if req["type"] == "complaint" else "-"
            html += f"  {status} {req['text'][:80]}...\n"

    # Финансы
    if summary.total_spent > 0:
        html += f"""
<b>Финансы:</b>
  - Всего потрачено: {summary.total_spent:,.0f} {summary.currency}
  - Операций: {summary.operations_count}
"""

    # Последние сообщения (только для summary)
    if mode == "summary" and summary.last_messages:
        html += "\n<b>Последние сообщения:</b>\n"
        for msg in summary.last_messages[-3:]:
            html += f"[{msg['date']}] {msg['sender']}: \"{msg['text'][:60]}...\"\n"

    # Теги
    if summary.tags:
        tags_str = " ".join(f"#{t}" for t in summary.tags)
        html += f"\n<b>Теги:</b> {tags_str}\n"

    # Предупреждения
    if summary.has_complaints:
        html += "\n<span style='color:red'><b>ВНИМАНИЕ:</b> Есть жалобы в переписке!</span>\n"

    if summary.days_since_last_message > 30:
        html += f"\n<span style='color:orange'><b>Давно не писали:</b> {summary.days_since_last_message} дней</span>\n"

    return html


def format_important_messages(messages: list) -> str:
    """
    Форматировать только важные сообщения.

    Args:
        messages: список всех сообщений

    Returns:
        HTML строка с важными сообщениями
    """
    important = []

    for msg in messages:
        text = msg.get("text", "").lower()
        is_important = False

        # Проверяем на важность
        if PRICE_PATTERN.search(msg.get("text", "")):
            is_important = True
        for kw in BOOKING_KEYWORDS + COMPLAINT_KEYWORDS:
            if kw in text:
                is_important = True
                break

        if is_important:
            important.append(msg)

    if not important:
        return "<i>Важных сообщений не найдено</i>"

    html = "<b>Важные сообщения:</b>\n\n"

    for msg in important[:20]:  # Максимум 20
        sender = "Клиент" if not msg.get("is_from_me") else "Мы"
        date = msg.get("datetime", "")[:16]
        text = msg.get("text", "")[:200]
        html += f"<b>[{date}] {sender}:</b>\n{text}\n\n"

    return html


def format_full_history(messages: list) -> str:
    """
    Форматировать полную историю (осторожно, может быть большой!).

    Args:
        messages: список сообщений

    Returns:
        HTML строка
    """
    if len(messages) > 100:
        logger.warning(f"Слишком много сообщений ({len(messages)}), обрезаем до 100")
        messages = messages[-100:]  # Последние 100

    html = f"<b>История чата ({len(messages)} сообщений):</b>\n\n"

    for msg in messages:
        sender = "Клиент" if not msg.get("is_from_me") else "Мы"
        date = msg.get("datetime", "")[:16]
        text = msg.get("text", "")[:300] or "[медиа]"
        html += f"<b>[{date}] {sender}:</b> {text}\n"

    return html


# ═══════════════════════════════════════════════════════════════════════════
# СИНХРОНИЗАЦИЯ ТАЙМЛАЙНА
# ═══════════════════════════════════════════════════════════════════════════

def sync_timeline(
    client: Bitrix24TimelineClient,
    contact_b24_id: int,
    jid: str,
    messages: list,
    contact: Optional[dict] = None,
    operations: Optional[list] = None,
    mode: str = "summary"
) -> bool:
    """
    Добавить историю WhatsApp в таймлайн контакта Б24.

    Args:
        client: клиент Б24
        contact_b24_id: ID контакта в Б24
        jid: WhatsApp JID
        messages: список сообщений
        contact: данные контакта
        operations: операции
        mode: режим (summary/important/full)

    Returns:
        True если успешно
    """
    try:
        if mode == "summary":
            summary = generate_chat_summary(jid, messages, contact, operations)
            comment = format_timeline_comment(summary, mode)
        elif mode == "important":
            comment = format_important_messages(messages)
        elif mode == "full":
            comment = format_full_history(messages)
        else:
            logger.error(f"Неизвестный режим: {mode}")
            return False

        comment_id = client.add_timeline_comment(
            entity_type="CONTACT",
            entity_id=contact_b24_id,
            comment=comment
        )

        if comment_id:
            logger.info(f"Добавлен комментарий {comment_id} для контакта {contact_b24_id}")
            return True

    except Exception as e:
        logger.error(f"Ошибка синхронизации таймлайна для {jid}: {e}")

    return False


def sync_all_timelines(
    client: Bitrix24TimelineClient,
    messages_by_jid: dict,
    contacts: list,
    operations: list,
    mode: str = "summary",
    contact_id: Optional[int] = None
) -> SyncResult:
    """
    Синхронизировать таймлайны для всех контактов.

    Args:
        client: клиент Б24
        messages_by_jid: сообщения по JID
        contacts: контакты
        operations: операции
        mode: режим
        contact_id: если указан - только для этого контакта

    Returns:
        SyncResult
    """
    result = SyncResult()

    # Загружаем контакты с JID из Б24
    b24_contacts = client.get_all_contacts_with_jid()

    # Индексируем локальные контакты по JID
    local_contacts = {c.get("jid"): c for c in contacts if c.get("jid")}

    # Если указан конкретный контакт
    if contact_id:
        # Ищем контакт по ID
        target_jid = None
        for jid, c in b24_contacts.items():
            if int(c.get("ID", 0)) == contact_id:
                target_jid = jid
                break

        if not target_jid:
            result.add_error(f"ID:{contact_id}", "Контакт не найден в Б24")
            return result

        if target_jid not in messages_by_jid:
            result.add_skipped(f"ID:{contact_id}", "Нет сообщений")
            return result

        success = sync_timeline(
            client=client,
            contact_b24_id=contact_id,
            jid=target_jid,
            messages=messages_by_jid[target_jid],
            contact=local_contacts.get(target_jid),
            operations=operations,
            mode=mode
        )

        if success:
            result.add_created(contact_id, target_jid)
        else:
            result.add_error(target_jid, "Ошибка синхронизации")

        return result

    # Синхронизируем все
    for jid, b24_contact in b24_contacts.items():
        b24_id = int(b24_contact.get("ID", 0))
        name = f"{b24_contact.get('NAME', '')} {b24_contact.get('LAST_NAME', '')}".strip()

        if jid not in messages_by_jid:
            result.add_skipped(name, "Нет сообщений")
            continue

        try:
            success = sync_timeline(
                client=client,
                contact_b24_id=b24_id,
                jid=jid,
                messages=messages_by_jid[jid],
                contact=local_contacts.get(jid),
                operations=operations,
                mode=mode
            )

            if success:
                result.add_created(b24_id, name)
            else:
                result.add_error(name, "Ошибка синхронизации")

        except Exception as e:
            result.add_error(name, str(e))

    return result


# ═══════════════════════════════════════════════════════════════════════════
# СИНХРОНИЗАЦИЯ КАЛЕНДАРЯ
# ═══════════════════════════════════════════════════════════════════════════

def sync_calendar(
    client: Bitrix24TimelineClient,
    operations: list,
    travel_dates: list,
    contacts: list
) -> SyncResult:
    """
    Создать события в календаре Б24 из операций и travel_dates.

    Args:
        client: клиент Б24
        operations: операции/бронирования
        travel_dates: даты прилётов/вылетов
        contacts: контакты

    Returns:
        SyncResult
    """
    result = SyncResult()

    # Индексируем контакты по телефону
    contacts_by_phone = {}
    for c in contacts:
        phone = c.get("phone", "")
        if phone:
            normalized = client._normalize_phone(phone)
            contacts_by_phone[normalized] = c

    # Получаем или создаём календарь
    calendar_id = client.get_or_create_crm_calendar()

    # Проверяем существующие события (чтобы не дублировать)
    today = datetime.now()
    existing_events = client.find_calendar_events(
        date_from=(today - timedelta(days=30)).strftime("%Y-%m-%d"),
        date_to=(today + timedelta(days=365)).strftime("%Y-%m-%d"),
        section_id=calendar_id
    )
    existing_titles = {e.get("NAME", "") for e in existing_events}

    # Создаём события из операций
    logger.info(f"Синхронизация {len(operations)} операций в календарь...")

    for op in operations:
        phone = op.get("phone", "")
        normalized_phone = client._normalize_phone(phone) if phone else ""
        contact = contacts_by_phone.get(normalized_phone, {})
        contact_name = contact.get("name", phone or "Клиент")

        # Формируем название события
        op_type = op.get("type", "tour")
        type_emoji = {
            "tour": "🎯",
            "yacht": "🛥️",
            "transfer": "🚗",
            "tickets": "🎟️",
            "car_rental": "🚙",
            "catering": "🍽️",
            "exchange": "💱",
        }.get(op_type, "📋")

        title = f"{type_emoji} {op.get('description', op_type)} - {contact_name}"

        # Пропускаем если уже есть
        if title in existing_titles:
            result.add_skipped(title, "Уже существует")
            continue

        # Описание
        description = f"""Клиент: {contact_name}
Телефон: {phone}
Сумма: {op.get('amount', 0)} {op.get('currency', 'AED')}
Статус: {op.get('status', 'pending')}

{op.get('notes', '')}
"""

        # Дата
        event_date = op.get("date", "")
        if not event_date:
            result.add_skipped(title, "Нет даты")
            continue

        try:
            event_id = client.add_calendar_event(
                name=title,
                description=description,
                date_from=f"{event_date} 10:00:00",
                section_id=calendar_id,
                importance="high" if op.get("status") == "confirmed" else "normal"
            )

            if event_id:
                result.add_created(event_id, title)
                existing_titles.add(title)
            else:
                result.add_error(title, "Ошибка создания")

        except Exception as e:
            result.add_error(title, str(e))

    # Создаём события из travel_dates
    logger.info(f"Синхронизация {len(travel_dates)} travel_dates в календарь...")

    for td in travel_dates:
        phone = td.get("phone", "")
        normalized_phone = client._normalize_phone(phone) if phone else ""
        contact = contacts_by_phone.get(normalized_phone, {})
        contact_name = contact.get("name", phone or "Клиент")

        # Формируем название
        td_type = td.get("type", "arrival")  # arrival/departure
        emoji = "✈️" if td_type == "arrival" else "🛫"
        action = "Прилёт" if td_type == "arrival" else "Вылет"

        title = f"{emoji} {action} - {contact_name}"

        if title in existing_titles:
            result.add_skipped(title, "Уже существует")
            continue

        # Описание
        description = f"""Клиент: {contact_name}
Телефон: {phone}
Количество человек: {td.get('pax', '?')}
Отель: {td.get('hotel', '?')}
Рейс: {td.get('flight', '?')}

Комментарий: {td.get('notes', '')}
"""

        event_date = td.get("date", "")
        if not event_date:
            result.add_skipped(title, "Нет даты")
            continue

        try:
            event_id = client.add_calendar_event(
                name=title,
                description=description,
                date_from=f"{event_date} 12:00:00",
                section_id=calendar_id,
                importance="high"
            )

            if event_id:
                result.add_created(event_id, title)
                existing_titles.add(title)
            else:
                result.add_error(title, "Ошибка создания")

        except Exception as e:
            result.add_error(title, str(e))

    return result


# ═══════════════════════════════════════════════════════════════════════════
# СОЗДАНИЕ ЗАДАЧ
# ═══════════════════════════════════════════════════════════════════════════

def create_followup_tasks(
    client: Bitrix24TimelineClient,
    messages_by_jid: dict,
    contacts: list,
    operations: list
) -> SyncResult:
    """
    Создать follow-up задачи на основе анализа чатов.

    Типы задач:
    - Перезвонить (давно не отвечали)
    - Напомнить о туре (за день до)
    - Обработать жалобу

    Args:
        client: клиент Б24
        messages_by_jid: сообщения по JID
        contacts: контакты
        operations: операции

    Returns:
        SyncResult
    """
    result = SyncResult()
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    # Загружаем контакты из Б24
    b24_contacts = client.get_all_contacts_with_jid()

    # Индексируем локальные контакты
    local_contacts = {c.get("jid"): c for c in contacts if c.get("jid")}

    # Индексируем операции по телефону
    ops_by_phone = defaultdict(list)
    for op in operations:
        phone = op.get("phone", "")
        if phone:
            ops_by_phone[client._normalize_phone(phone)].append(op)

    # Получаем существующие задачи (чтобы не дублировать)
    existing_tasks = client.get_tasks(limit=200)
    existing_titles = {t.get("title", "") for t in existing_tasks}

    logger.info("Анализ чатов для создания задач...")

    for jid, messages in messages_by_jid.items():
        if not messages:
            continue

        b24_contact = b24_contacts.get(jid)
        if not b24_contact:
            continue

        b24_id = int(b24_contact.get("ID", 0))
        contact_name = f"{b24_contact.get('NAME', '')} {b24_contact.get('LAST_NAME', '')}".strip()

        local_contact = local_contacts.get(jid, {})
        phone = local_contact.get("phone", "")

        # Анализируем чат
        summary = generate_chat_summary(jid, messages, local_contact, operations)

        # 1. Задача "Перезвонить" - если давно не отвечали
        if summary.days_since_last_message >= 3:
            last_msg = messages[-1]
            if not last_msg.get("is_from_me"):
                # Последнее сообщение от клиента, мы не ответили
                title = f"Перезвонить клиенту {contact_name} (не отвечали {summary.days_since_last_message} дней)"

                if title not in existing_titles:
                    try:
                        task_id = client.create_task(
                            title=title,
                            description=f"Клиент написал {summary.days_since_last_message} дней назад.\n\nПоследнее сообщение:\n{last_msg.get('text', '')[:300]}",
                            deadline=(today + timedelta(days=1)).strftime("%Y-%m-%d 12:00:00"),
                            priority=2,  # Высокий
                            crm_entity=("C", b24_id),
                            tags=["followup", "whatsapp"]
                        )

                        if task_id:
                            result.add_created(task_id, title)
                            existing_titles.add(title)
                        else:
                            result.add_error(title, "Ошибка создания")

                    except Exception as e:
                        result.add_error(title, str(e))

        # 2. Задача "Напомнить о туре" - за день до
        if phone:
            normalized_phone = client._normalize_phone(phone)
            contact_ops = ops_by_phone.get(normalized_phone, [])

            for op in contact_ops:
                if op.get("status") != "confirmed":
                    continue

                op_date_str = op.get("date", "")
                if not op_date_str:
                    continue

                try:
                    op_date = datetime.strptime(op_date_str, "%Y-%m-%d")
                    if op_date.date() == tomorrow.date():
                        title = f"Напомнить о туре завтра - {contact_name}"

                        if title not in existing_titles:
                            task_id = client.create_task(
                                title=title,
                                description=f"Завтра ({op_date_str}) у клиента:\n{op.get('description', '')}\n\nСумма: {op.get('amount', 0)} {op.get('currency', 'AED')}",
                                deadline=today.strftime("%Y-%m-%d 18:00:00"),
                                priority=2,
                                crm_entity=("C", b24_id),
                                tags=["reminder", "whatsapp"]
                            )

                            if task_id:
                                result.add_created(task_id, title)
                                existing_titles.add(title)

                except ValueError:
                    continue

        # 3. Задача "Обработать жалобу"
        if summary.has_complaints:
            title = f"Обработать жалобу - {contact_name}"

            if title not in existing_titles:
                # Находим жалобу
                complaint_text = ""
                for req in summary.key_requests:
                    if req.get("type") == "complaint":
                        complaint_text = req.get("text", "")
                        break

                try:
                    task_id = client.create_task(
                        title=title,
                        description=f"В чате обнаружена жалоба:\n\n{complaint_text}",
                        deadline=(today + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
                        priority=2,  # Высокий
                        crm_entity=("C", b24_id),
                        tags=["complaint", "urgent", "whatsapp"]
                    )

                    if task_id:
                        result.add_created(task_id, title)
                        existing_titles.add(title)

                except Exception as e:
                    result.add_error(title, str(e))

    return result


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def validate_config() -> bool:
    """Проверка конфигурации."""
    missing = []

    if not BITRIX24_CONFIG["domain"]:
        missing.append("BITRIX24_DOMAIN")
    if not BITRIX24_CONFIG["user_id"]:
        missing.append("BITRIX24_USER_ID")
    if not BITRIX24_CONFIG["webhook_key"]:
        missing.append("BITRIX24_WEBHOOK_KEY")

    if missing:
        logger.error(
            f"Не настроены переменные окружения: {', '.join(missing)}\n"
            "Установите их или создайте .env файл:\n"
            "  BITRIX24_DOMAIN=your-domain\n"
            "  BITRIX24_USER_ID=1\n"
            "  BITRIX24_WEBHOOK_KEY=your-webhook-key"
        )
        return False

    return True


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Синхронизация WhatsApp с таймлайном и календарём Битрикс24",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --sync-timeline --mode summary     Загрузить саммари для всех контактов
  %(prog)s --sync-timeline --contact-id 123   Только для конкретного контакта
  %(prog)s --sync-timeline --mode important   Только важные сообщения
  %(prog)s --sync-timeline --mode full        Полная история (осторожно!)
  %(prog)s --sync-calendar                    Синхронизировать календарь
  %(prog)s --create-tasks                     Создать follow-up задачи
  %(prog)s --sync-all                         Всё вместе

Режимы таймлайна:
  summary   - AI-саммари переписки (по умолчанию)
  important - Только важные сообщения (цены, бронирования)
  full      - Все сообщения (много данных!)

Переменные окружения:
  BITRIX24_DOMAIN      Домен Б24 (example.bitrix24.ru -> example)
  BITRIX24_USER_ID     ID пользователя вебхука
  BITRIX24_WEBHOOK_KEY Ключ вебхука
        """
    )

    parser.add_argument(
        "--sync-timeline", action="store_true",
        help="Загрузить историю WhatsApp в таймлайн контактов"
    )
    parser.add_argument(
        "--mode", choices=["summary", "important", "full"], default="summary",
        help="Режим таймлайна (default: summary)"
    )
    parser.add_argument(
        "--contact-id", type=int,
        help="Синхронизировать только для контакта с указанным ID в Б24"
    )
    parser.add_argument(
        "--sync-calendar", action="store_true",
        help="Синхронизировать календарь Б24"
    )
    parser.add_argument(
        "--create-tasks", action="store_true",
        help="Создать follow-up задачи"
    )
    parser.add_argument(
        "--sync-all", action="store_true",
        help="Выполнить все операции"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Тестовый режим (без реальных изменений)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Подробный вывод"
    )
    parser.add_argument(
        "--output", "-o", type=str,
        help="Сохранить результат в JSON файл"
    )

    args = parser.parse_args()

    # Настройка логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Проверка что выбрана хотя бы одна операция
    if not any([args.sync_timeline, args.sync_calendar, args.create_tasks, args.sync_all]):
        parser.print_help()
        print("\nОшибка: Укажите хотя бы одну операцию")
        sys.exit(1)

    # Проверка конфигурации
    if not args.dry_run and not validate_config():
        sys.exit(1)

    # Создание клиента
    client = Bitrix24TimelineClient(
        domain=BITRIX24_CONFIG["domain"] or "test",
        user_id=BITRIX24_CONFIG["user_id"] or "1",
        webhook_key=BITRIX24_CONFIG["webhook_key"] or "test",
        dry_run=args.dry_run
    )

    # Проверка подключения
    if not args.dry_run and not client.test_connection():
        logger.error("Не удалось подключиться к Bitrix24")
        sys.exit(1)

    # Загрузка данных
    contacts = load_json_file(INPUT_FILES["contacts"])
    operations = load_json_file(INPUT_FILES["operations"])
    travel_dates = load_json_file(INPUT_FILES["travel_dates"])
    messages_by_jid = load_messages_by_jid(INPUT_FILES["messages"])

    results = {}

    # Выполнение операций
    try:
        if args.sync_all or args.sync_timeline:
            logger.info(f"Синхронизация таймлайна (режим: {args.mode})...")
            results["timeline"] = sync_all_timelines(
                client=client,
                messages_by_jid=messages_by_jid,
                contacts=contacts,
                operations=operations,
                mode=args.mode,
                contact_id=args.contact_id
            ).to_dict()

        if args.sync_all or args.sync_calendar:
            logger.info("Синхронизация календаря...")
            results["calendar"] = sync_calendar(
                client=client,
                operations=operations,
                travel_dates=travel_dates,
                contacts=contacts
            ).to_dict()

        if args.sync_all or args.create_tasks:
            logger.info("Создание задач...")
            results["tasks"] = create_followup_tasks(
                client=client,
                messages_by_jid=messages_by_jid,
                contacts=contacts,
                operations=operations
            ).to_dict()

    except KeyboardInterrupt:
        logger.warning("Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

    # Вывод итогов
    print("\n" + "=" * 60)
    print("ИТОГИ СИНХРОНИЗАЦИИ")
    print("=" * 60)

    for entity, data in results.items():
        print(f"\n{entity.upper()}:")
        print(f"  Создано:   {data['created']}")
        print(f"  Обновлено: {data['updated']}")
        print(f"  Пропущено: {data['skipped']}")
        print(f"  Ошибок:    {data['errors']}")
        print(f"  Всего:     {data['total']}")

    # Сохранение результата
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "dry_run": args.dry_run,
                "mode": args.mode,
                "results": results
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"Результат сохранён в {output_path}")

    # Код возврата
    total_errors = sum(r.get("errors", 0) for r in results.values())
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
