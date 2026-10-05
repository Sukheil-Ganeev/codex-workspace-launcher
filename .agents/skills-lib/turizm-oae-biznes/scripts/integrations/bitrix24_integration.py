#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интеграция с Битрикс24 CRM.

Синхронизация контактов, создание сделок и лидов из данных WhatsApp чатов.
Настройка воронок продаж и смарт-процессов.

Использование:
    # Синхронизация данных
    python bitrix24_integration.py --sync-all          # Полная синхронизация
    python bitrix24_integration.py --contacts          # Только контакты
    python bitrix24_integration.py --deals             # Только сделки
    python bitrix24_integration.py --leads             # Только лиды
    python bitrix24_integration.py --sync-all --dry-run  # Тестовый режим

    # Настройка структуры Б24
    python bitrix24_integration.py --setup-categories  # Создать воронки продаж
    python bitrix24_integration.py --setup-smart       # Создать смарт-процессы
    python bitrix24_integration.py --setup-all         # Создать всю структуру

    # Синхронизация смарт-процессов
    python bitrix24_integration.py --sync-referrals    # Синхронизировать рефералы
    python bitrix24_integration.py --sync-complaints   # Синхронизировать жалобы
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, field

import requests

# Добавляем путь к скриптам
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import JSON_DIR

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
    "contacts": JSON_DIR / "contacts.json",
    "profiles": JSON_DIR / "profiles.json",
    "operations": JSON_DIR / "operations.json",
}

# Rate limiting
RATE_LIMIT_REQUESTS = 2  # запросов в секунду (Б24 ограничение)
RATE_LIMIT_BATCH = 50  # максимум команд в batch запросе
REQUEST_TIMEOUT = 30  # секунд

# Маппинг типов контактов на пользовательские поля Б24
CONTACT_TYPE_MAPPING = {
    "клиенты": "CLIENT",
    "агенты": "AGENT",
    "поставщики": "SUPPLIER",
    "сотрудники": "EMPLOYEE",
}

# Маппинг статусов операций на стадии сделок
DEAL_STAGE_MAPPING = {
    "pending": "NEW",
    "confirmed": "PREPARATION",
    "in_progress": "EXECUTING",
    "completed": "WON",
    "cancelled": "LOSE",
}

# Маппинг типов операций на направления сделок
DEAL_CATEGORY_MAPPING = {
    "tour": "0",  # Основная воронка
    "yacht": "0",
    "transfer": "0",
    "tickets": "0",
    "exchange": "0",
    "car_rental": "0",
    "catering": "0",
}

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ ВОРОНОК ПРОДАЖ
# ═══════════════════════════════════════════════════════════════════════════

DEAL_CATEGORIES_CONFIG = [
    {
        "NAME": "Туры и экскурсии",
        "SORT": 100,
        "STAGES": [
            {"NAME": "Запрос", "SORT": 10, "STATUS_ID": "C1:NEW", "SEMANTICS": "process"},
            {"NAME": "Расчёт отправлен", "SORT": 20, "STATUS_ID": "C1:PREPARATION", "SEMANTICS": "process"},
            {"NAME": "Бронь", "SORT": 30, "STATUS_ID": "C1:PREPAYMENT_INVOICE", "SEMANTICS": "process"},
            {"NAME": "Оплачено", "SORT": 40, "STATUS_ID": "C1:EXECUTING", "SEMANTICS": "process"},
            {"NAME": "Выполнено", "SORT": 50, "STATUS_ID": "C1:WON", "SEMANTICS": "success"},
            {"NAME": "Отменено", "SORT": 60, "STATUS_ID": "C1:LOSE", "SEMANTICS": "failure"},
        ]
    },
    {
        "NAME": "Трансферы",
        "SORT": 200,
        "STAGES": [
            {"NAME": "Заявка", "SORT": 10, "STATUS_ID": "C2:NEW", "SEMANTICS": "process"},
            {"NAME": "Подтверждено", "SORT": 20, "STATUS_ID": "C2:CONFIRMED", "SEMANTICS": "process"},
            {"NAME": "Выполнено", "SORT": 30, "STATUS_ID": "C2:WON", "SEMANTICS": "success"},
            {"NAME": "Отменено", "SORT": 40, "STATUS_ID": "C2:LOSE", "SEMANTICS": "failure"},
        ]
    },
    {
        "NAME": "Яхты",
        "SORT": 300,
        "STAGES": [
            {"NAME": "Запрос", "SORT": 10, "STATUS_ID": "C3:NEW", "SEMANTICS": "process"},
            {"NAME": "Договор", "SORT": 20, "STATUS_ID": "C3:CONTRACT", "SEMANTICS": "process"},
            {"NAME": "Предоплата", "SORT": 30, "STATUS_ID": "C3:PREPAYMENT", "SEMANTICS": "process"},
            {"NAME": "Аренда", "SORT": 40, "STATUS_ID": "C3:RENTAL", "SEMANTICS": "process"},
            {"NAME": "Закрыто", "SORT": 50, "STATUS_ID": "C3:WON", "SEMANTICS": "success"},
            {"NAME": "Отменено", "SORT": 60, "STATUS_ID": "C3:LOSE", "SEMANTICS": "failure"},
        ]
    },
    {
        "NAME": "Билеты и парки",
        "SORT": 400,
        "STAGES": [
            {"NAME": "Запрос", "SORT": 10, "STATUS_ID": "C4:NEW", "SEMANTICS": "process"},
            {"NAME": "Оплата", "SORT": 20, "STATUS_ID": "C4:PAYMENT", "SEMANTICS": "process"},
            {"NAME": "Отправлено", "SORT": 30, "STATUS_ID": "C4:WON", "SEMANTICS": "success"},
            {"NAME": "Отменено", "SORT": 40, "STATUS_ID": "C4:LOSE", "SEMANTICS": "failure"},
        ]
    }
]

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ СМАРТ-ПРОЦЕССОВ
# ═══════════════════════════════════════════════════════════════════════════

SMART_PROCESSES_CONFIG = {
    "bookings": {
        "TITLE": "Бронирования",
        "CODE": "BOOKINGS",
        "FIELDS": [
            {"FIELD_NAME": "UF_DATE", "USER_TYPE_ID": "date", "EDIT_FORM_LABEL": {"ru": "Дата"}},
            {"FIELD_NAME": "UF_PAX", "USER_TYPE_ID": "integer", "EDIT_FORM_LABEL": {"ru": "Кол-во человек"}},
            {"FIELD_NAME": "UF_HOTEL", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Отель"}},
            {"FIELD_NAME": "UF_PICKUP_TIME", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Время пикапа"}},
            {"FIELD_NAME": "UF_AMOUNT", "USER_TYPE_ID": "double", "EDIT_FORM_LABEL": {"ru": "Сумма"}},
            {"FIELD_NAME": "UF_CURRENCY", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Валюта"}},
            {"FIELD_NAME": "UF_NOTES", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Примечания"}},
            {"FIELD_NAME": "UF_EXTERNAL_ID", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Внешний ID"}},
        ],
        "STAGES": [
            {"NAME": "Новое", "SORT": 10, "SEMANTICS": "process"},
            {"NAME": "Подтверждено", "SORT": 20, "SEMANTICS": "process"},
            {"NAME": "Выполнено", "SORT": 30, "SEMANTICS": "success"},
            {"NAME": "Отменено", "SORT": 40, "SEMANTICS": "failure"},
        ]
    },
    "referrals": {
        "TITLE": "Рефералы",
        "CODE": "REFERRALS",
        "FIELDS": [
            {"FIELD_NAME": "UF_REFERRER_NAME", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Кто привёл (имя)"}},
            {"FIELD_NAME": "UF_REFERRER_PHONE", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Телефон реферера"}},
            {"FIELD_NAME": "UF_REFERRED_NAME", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Кого привёл (имя)"}},
            {"FIELD_NAME": "UF_REFERRED_PHONE", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Телефон реферала"}},
            {"FIELD_NAME": "UF_SOURCE", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Источник"}},
            {"FIELD_NAME": "UF_REVENUE", "USER_TYPE_ID": "double", "EDIT_FORM_LABEL": {"ru": "Выручка"}},
            {"FIELD_NAME": "UF_COMMISSION", "USER_TYPE_ID": "double", "EDIT_FORM_LABEL": {"ru": "Комиссия"}},
            {"FIELD_NAME": "UF_DATE", "USER_TYPE_ID": "date", "EDIT_FORM_LABEL": {"ru": "Дата"}},
            {"FIELD_NAME": "UF_NOTES", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Примечания"}},
        ],
        "STAGES": [
            {"NAME": "Новый", "SORT": 10, "SEMANTICS": "process"},
            {"NAME": "Активный", "SORT": 20, "SEMANTICS": "process"},
            {"NAME": "Выплачено", "SORT": 30, "SEMANTICS": "success"},
        ]
    },
    "complaints": {
        "TITLE": "Жалобы",
        "CODE": "COMPLAINTS",
        "FIELDS": [
            {"FIELD_NAME": "UF_CATEGORY", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Категория"}},
            {"FIELD_NAME": "UF_SEVERITY", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Серьёзность"}},
            {"FIELD_NAME": "UF_DESCRIPTION", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Описание"}},
            {"FIELD_NAME": "UF_CLIENT_NAME", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Имя клиента"}},
            {"FIELD_NAME": "UF_CLIENT_PHONE", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Телефон клиента"}},
            {"FIELD_NAME": "UF_RESOLVED", "USER_TYPE_ID": "boolean", "EDIT_FORM_LABEL": {"ru": "Решено"}},
            {"FIELD_NAME": "UF_RESOLUTION", "USER_TYPE_ID": "string", "EDIT_FORM_LABEL": {"ru": "Решение"}},
            {"FIELD_NAME": "UF_DATE", "USER_TYPE_ID": "date", "EDIT_FORM_LABEL": {"ru": "Дата жалобы"}},
            {"FIELD_NAME": "UF_RESOLVED_DATE", "USER_TYPE_ID": "date", "EDIT_FORM_LABEL": {"ru": "Дата решения"}},
        ],
        "STAGES": [
            {"NAME": "Новая", "SORT": 10, "SEMANTICS": "process"},
            {"NAME": "В работе", "SORT": 20, "SEMANTICS": "process"},
            {"NAME": "Решена", "SORT": 30, "SEMANTICS": "success"},
            {"NAME": "Отклонена", "SORT": 40, "SEMANTICS": "failure"},
        ]
    }
}

# Маппинг категорий жалоб
COMPLAINT_CATEGORY_MAPPING = {
    "service": "Качество услуги",
    "driver": "Водитель",
    "guide": "Гид",
    "timing": "Опоздание",
    "price": "Цена",
    "communication": "Коммуникация",
    "other": "Другое",
}

# Маппинг серьёзности жалоб
COMPLAINT_SEVERITY_MAPPING = {
    "low": "Низкая",
    "medium": "Средняя",
    "high": "Высокая",
    "critical": "Критическая",
}

# ═══════════════════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

LOG_DIR = JSON_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "bitrix24.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# КЛАССЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════

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
# BITRIX24 API КЛИЕНТ
# ═══════════════════════════════════════════════════════════════════════════

class Bitrix24Client:
    """Клиент для работы с REST API Битрикс24."""

    def __init__(self, domain: str, user_id: str, webhook_key: str, dry_run: bool = False):
        self.domain = domain
        self.user_id = user_id
        self.webhook_key = webhook_key
        self.dry_run = dry_run
        self.base_url = f"https://{domain}.bitrix24.ru/rest/{user_id}/{webhook_key}"
        self.last_request_time = 0
        self.session = requests.Session()

        # Кэш для дедупликации
        self._contacts_cache: dict[str, int] = {}  # phone -> contact_id
        self._deals_cache: dict[str, int] = {}  # unique_key -> deal_id

    def _rate_limit(self):
        """Соблюдение rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0 / RATE_LIMIT_REQUESTS:
            time.sleep(1.0 / RATE_LIMIT_REQUESTS - elapsed)
        self.last_request_time = time.time()

    def _call(self, method: str, params: Optional[dict] = None) -> dict:
        """Выполнение REST API запроса."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] {method}: {json.dumps(params, ensure_ascii=False, indent=2)}")
            # Возвращаем корректный формат для dry-run
            if method.endswith(".add"):
                return {"result": 999999}  # Фиктивный ID
            elif method.endswith(".update"):
                return {"result": True}
            elif method.endswith(".list"):
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

    def batch(self, commands: dict, halt_on_error: bool = False) -> dict:
        """
        Батчевый запрос (до 50 команд за раз).

        Args:
            commands: словарь {cmd_id: [method, params]}
            halt_on_error: остановить при первой ошибке

        Returns:
            dict с результатами по каждой команде
        """
        if not commands:
            return {"result": {"result": {}, "result_error": {}}}

        # Разбиваем на части по RATE_LIMIT_BATCH
        all_results = {"result": {}, "result_error": {}}
        cmd_items = list(commands.items())

        for i in range(0, len(cmd_items), RATE_LIMIT_BATCH):
            batch_chunk = dict(cmd_items[i:i + RATE_LIMIT_BATCH])

            # Формируем batch запрос
            batch_params = {
                "halt": 1 if halt_on_error else 0,
                "cmd": {}
            }

            for cmd_id, (method, params) in batch_chunk.items():
                # Формируем строку параметров
                param_parts = []
                for k, v in (params or {}).items():
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            param_parts.append(f"{k}[{sub_k}]={sub_v}")
                    elif isinstance(v, list):
                        for idx, item in enumerate(v):
                            if isinstance(item, dict):
                                for sub_k, sub_v in item.items():
                                    param_parts.append(f"{k}[{idx}][{sub_k}]={sub_v}")
                            else:
                                param_parts.append(f"{k}[{idx}]={item}")
                    else:
                        param_parts.append(f"{k}={v}")

                batch_params["cmd"][cmd_id] = f"{method}?{'&'.join(param_parts)}"

            if self.dry_run:
                logger.info(f"[DRY-RUN] batch: {len(batch_chunk)} команд")
                for cmd_id, (method, params) in batch_chunk.items():
                    logger.debug(f"  {cmd_id}: {method}")
                continue

            result = self._call("batch", batch_params)

            if "result" in result:
                all_results["result"].update(result["result"].get("result", {}))
                all_results["result_error"].update(result["result"].get("result_error", {}))

        return {"result": all_results}

    # ─────────────────────────────────────────────────────────────────────
    # КОНТАКТЫ
    # ─────────────────────────────────────────────────────────────────────

    def find_contact_by_phone(self, phone: str) -> Optional[int]:
        """Поиск контакта по телефону."""
        # Сначала проверяем кэш
        normalized = self._normalize_phone(phone)
        if normalized in self._contacts_cache:
            return self._contacts_cache[normalized]

        if self.dry_run:
            return None

        result = self._call("crm.contact.list", {
            "filter": {"PHONE": phone},
            "select": ["ID", "NAME", "PHONE"]
        })

        contacts = result.get("result", [])
        if contacts:
            contact_id = int(contacts[0]["ID"])
            self._contacts_cache[normalized] = contact_id
            return contact_id

        return None

    def create_contact(self, contact: dict) -> int:
        """
        Создание контакта в CRM.

        Args:
            contact: данные контакта из contacts.json

        Returns:
            ID созданного контакта
        """
        # Разбираем имя на части
        name_parts = (contact.get("name") or "Неизвестный").split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        params = {
            "fields": {
                "NAME": first_name,
                "LAST_NAME": last_name,
                "PHONE": [{"VALUE": contact.get("phone", ""), "VALUE_TYPE": "WORK"}],
                "SOURCE_ID": "SELF",  # Собственный источник
                "COMMENTS": contact.get("notes", ""),
            }
        }

        # Пользовательские поля
        if contact.get("type"):
            params["fields"]["UF_CRM_TYPE"] = CONTACT_TYPE_MAPPING.get(
                contact["type"], contact["type"].upper()
            )

        if contact.get("language"):
            params["fields"]["UF_CRM_LANGUAGE"] = contact["language"].upper()

        if contact.get("country"):
            params["fields"]["UF_CRM_COUNTRY"] = contact["country"]

        if contact.get("subtype"):
            params["fields"]["UF_CRM_SUBTYPE"] = contact["subtype"]

        if contact.get("tags"):
            params["fields"]["UF_CRM_TAGS"] = ", ".join(contact["tags"])

        if contact.get("jid"):
            params["fields"]["UF_CRM_WHATSAPP_JID"] = contact["jid"]

        if contact.get("first_message"):
            params["fields"]["UF_CRM_FIRST_CONTACT"] = contact["first_message"]

        if contact.get("last_message"):
            params["fields"]["UF_CRM_LAST_CONTACT"] = contact["last_message"]

        result = self._call("crm.contact.add", params)
        res = result.get("result", 0)
        contact_id = int(res) if isinstance(res, (int, str)) else 0

        # Добавляем в кэш
        if contact_id and contact.get("phone"):
            self._contacts_cache[self._normalize_phone(contact["phone"])] = contact_id

        return contact_id

    def update_contact(self, contact_id: int, contact: dict) -> bool:
        """Обновление существующего контакта."""
        params = {
            "id": contact_id,
            "fields": {
                "COMMENTS": contact.get("notes", ""),
            }
        }

        # Обновляем пользовательские поля
        if contact.get("tags"):
            params["fields"]["UF_CRM_TAGS"] = ", ".join(contact["tags"])

        if contact.get("last_message"):
            params["fields"]["UF_CRM_LAST_CONTACT"] = contact["last_message"]

        if contact.get("total_messages"):
            params["fields"]["UF_CRM_TOTAL_MESSAGES"] = contact["total_messages"]

        result = self._call("crm.contact.update", params)
        return bool(result.get("result"))

    def get_all_contacts(self) -> list[dict]:
        """Получение всех контактов для построения кэша."""
        if self.dry_run:
            return []

        all_contacts = []
        start = 0

        while True:
            result = self._call("crm.contact.list", {
                "select": ["ID", "NAME", "PHONE"],
                "start": start
            })

            contacts = result.get("result", [])
            if not contacts:
                break

            all_contacts.extend(contacts)

            # Проверяем есть ли ещё
            if result.get("next"):
                start = result["next"]
            else:
                break

        # Заполняем кэш
        for contact in all_contacts:
            phones = contact.get("PHONE", [])
            if phones:
                for phone in phones:
                    if phone.get("VALUE"):
                        normalized = self._normalize_phone(phone["VALUE"])
                        self._contacts_cache[normalized] = int(contact["ID"])

        logger.info(f"Загружено {len(all_contacts)} контактов в кэш")
        return all_contacts

    # ─────────────────────────────────────────────────────────────────────
    # СДЕЛКИ
    # ─────────────────────────────────────────────────────────────────────

    def create_deal(self, operation: dict, contact_id: Optional[int] = None) -> int:
        """
        Создание сделки из операции.

        Args:
            operation: данные операции из operations.json
            contact_id: ID связанного контакта в Б24

        Returns:
            ID созданной сделки
        """
        # Формируем название сделки
        title = operation.get("description", "Сделка без названия")
        if operation.get("date"):
            title = f"{title} ({operation['date']})"

        params = {
            "fields": {
                "TITLE": title,
                "OPPORTUNITY": operation.get("amount", 0),
                "CURRENCY_ID": self._map_currency(operation.get("currency", "RUB")),
                "STAGE_ID": DEAL_STAGE_MAPPING.get(
                    operation.get("status", "pending"), "NEW"
                ),
                "CATEGORY_ID": DEAL_CATEGORY_MAPPING.get(
                    operation.get("type", "other"), "0"
                ),
                "COMMENTS": operation.get("notes", ""),
                "SOURCE_ID": "SELF",
            }
        }

        if contact_id:
            params["fields"]["CONTACT_ID"] = contact_id

        # Пользовательские поля
        if operation.get("type"):
            params["fields"]["UF_CRM_OPERATION_TYPE"] = operation["type"]

        if operation.get("date"):
            params["fields"]["UF_CRM_OPERATION_DATE"] = operation["date"]

        if operation.get("id"):
            params["fields"]["UF_CRM_EXTERNAL_ID"] = str(operation["id"])

        result = self._call("crm.deal.add", params)
        return int(result.get("result", 0))

    def find_deal_by_external_id(self, external_id: str) -> Optional[int]:
        """Поиск сделки по внешнему ID."""
        if self.dry_run:
            return None

        result = self._call("crm.deal.list", {
            "filter": {"UF_CRM_EXTERNAL_ID": external_id},
            "select": ["ID"]
        })

        deals = result.get("result", [])
        if deals:
            return int(deals[0]["ID"])

        return None

    def update_deal(self, deal_id: int, operation: dict) -> bool:
        """Обновление существующей сделки."""
        params = {
            "id": deal_id,
            "fields": {
                "OPPORTUNITY": operation.get("amount", 0),
                "STAGE_ID": DEAL_STAGE_MAPPING.get(
                    operation.get("status", "pending"), "NEW"
                ),
                "COMMENTS": operation.get("notes", ""),
            }
        }

        result = self._call("crm.deal.update", params)
        return bool(result.get("result"))

    # ─────────────────────────────────────────────────────────────────────
    # ЛИДЫ
    # ─────────────────────────────────────────────────────────────────────

    def create_lead(self, contact: dict) -> int:
        """
        Создание лида для нового контакта.

        Args:
            contact: данные контакта

        Returns:
            ID созданного лида
        """
        title = f"Лид: {contact.get('name', 'Неизвестный')}"

        params = {
            "fields": {
                "TITLE": title,
                "NAME": contact.get("name", ""),
                "PHONE": [{"VALUE": contact.get("phone", ""), "VALUE_TYPE": "WORK"}],
                "SOURCE_ID": "SELF",
                "STATUS_ID": "NEW",
                "COMMENTS": contact.get("notes", ""),
            }
        }

        # Пользовательские поля
        if contact.get("type"):
            params["fields"]["UF_CRM_TYPE"] = CONTACT_TYPE_MAPPING.get(
                contact["type"], contact["type"].upper()
            )

        if contact.get("language"):
            params["fields"]["UF_CRM_LANGUAGE"] = contact["language"].upper()

        result = self._call("crm.lead.add", params)
        return int(result.get("result", 0))

    def find_lead_by_phone(self, phone: str) -> Optional[int]:
        """Поиск лида по телефону."""
        if self.dry_run:
            return None

        result = self._call("crm.lead.list", {
            "filter": {"PHONE": phone},
            "select": ["ID"]
        })

        leads = result.get("result", [])
        if leads:
            return int(leads[0]["ID"])

        return None

    # ─────────────────────────────────────────────────────────────────────
    # ВОРОНКИ ПРОДАЖ (DEAL CATEGORIES)
    # ─────────────────────────────────────────────────────────────────────

    def get_deal_categories(self) -> list[dict]:
        """Получение списка воронок продаж."""
        if self.dry_run:
            return []

        result = self._call("crm.dealcategory.list", {})
        return result.get("result", [])

    def create_deal_category(self, name: str, sort: int = 100) -> int:
        """
        Создание воронки продаж.

        Args:
            name: Название воронки
            sort: Порядок сортировки

        Returns:
            ID созданной воронки
        """
        params = {
            "fields": {
                "NAME": name,
                "SORT": sort,
            }
        }

        result = self._call("crm.dealcategory.add", params)
        return int(result.get("result", 0))

    def get_deal_category_stages(self, category_id: int) -> list[dict]:
        """Получение стадий воронки."""
        if self.dry_run:
            return []

        result = self._call("crm.dealcategory.stage.list", {
            "id": category_id
        })
        return result.get("result", [])

    def set_deal_category_stages(self, category_id: int, stages: list[dict]) -> bool:
        """
        Установка стадий для воронки.

        Args:
            category_id: ID воронки
            stages: Список стадий с полями NAME, SORT, STATUS_ID, SEMANTICS

        Returns:
            True при успехе
        """
        # Формируем стадии с корректными STATUS_ID
        formatted_stages = []
        for i, stage in enumerate(stages):
            stage_id = stage.get("STATUS_ID", f"C{category_id}:STAGE_{i}")
            formatted_stages.append({
                "NAME": stage["NAME"],
                "SORT": stage.get("SORT", (i + 1) * 10),
                "STATUS_ID": stage_id,
                "SEMANTICS": stage.get("SEMANTICS", "process"),
            })

        params = {
            "id": category_id,
            "stages": formatted_stages
        }

        result = self._call("crm.dealcategory.stage.set", params)
        return bool(result.get("result"))

    def find_deal_category_by_name(self, name: str) -> Optional[int]:
        """Поиск воронки по названию."""
        categories = self.get_deal_categories()
        for cat in categories:
            if cat.get("NAME") == name:
                return int(cat["ID"])
        return None

    # ─────────────────────────────────────────────────────────────────────
    # СМАРТ-ПРОЦЕССЫ (CRM TYPES)
    # ─────────────────────────────────────────────────────────────────────

    def get_smart_process_types(self) -> list[dict]:
        """Получение списка смарт-процессов."""
        if self.dry_run:
            return []

        result = self._call("crm.type.list", {})
        return result.get("result", {}).get("types", [])

    def create_smart_process_type(self, title: str, code: str) -> int:
        """
        Создание смарт-процесса.

        Args:
            title: Название смарт-процесса
            code: Код (латиницей)

        Returns:
            ID созданного смарт-процесса (entityTypeId)
        """
        params = {
            "fields": {
                "title": title,
                "code": code,
                "isAutomationEnabled": "Y",
                "isBizProcEnabled": "Y",
                "isRecyclebinEnabled": "Y",
            }
        }

        result = self._call("crm.type.add", params)
        type_data = result.get("result", {}).get("type", {})
        return int(type_data.get("entityTypeId", 0))

    def find_smart_process_by_code(self, code: str) -> Optional[dict]:
        """
        Поиск смарт-процесса по коду.

        Returns:
            Словарь с данными смарт-процесса или None
        """
        types = self.get_smart_process_types()
        for t in types:
            if t.get("code") == code:
                return t
        return None

    def add_smart_process_field(
        self,
        entity_type_id: int,
        field_name: str,
        user_type_id: str,
        label: dict
    ) -> bool:
        """
        Добавление пользовательского поля в смарт-процесс.

        Args:
            entity_type_id: ID типа сущности
            field_name: Имя поля (UF_xxx)
            user_type_id: Тип поля (string, integer, double, date, boolean и т.д.)
            label: Метки {"ru": "Название"}

        Returns:
            True при успехе
        """
        params = {
            "entityTypeId": entity_type_id,
            "fields": {
                "FIELD_NAME": field_name,
                "USER_TYPE_ID": user_type_id,
                "EDIT_FORM_LABEL": label,
                "LIST_COLUMN_LABEL": label,
                "LIST_FILTER_LABEL": label,
                "SHOW_IN_LIST": "Y",
                "EDIT_IN_LIST": "Y",
                "IS_SEARCHABLE": "Y",
            }
        }

        try:
            result = self._call("crm.item.fields.add", params)
            return bool(result.get("result"))
        except Bitrix24Error as e:
            if "already exists" in str(e).lower() or "уже существует" in str(e).lower():
                logger.debug(f"Поле {field_name} уже существует")
                return True
            raise

    def get_smart_process_stages(self, entity_type_id: int) -> list[dict]:
        """Получение стадий смарт-процесса."""
        if self.dry_run:
            return []

        result = self._call("crm.status.list", {
            "filter": {"ENTITY_ID": f"DYNAMIC_{entity_type_id}_STAGE"}
        })
        return result.get("result", [])

    def add_smart_process_stage(
        self,
        entity_type_id: int,
        name: str,
        sort: int,
        semantics: str = "process"
    ) -> int:
        """
        Добавление стадии в смарт-процесс.

        Args:
            entity_type_id: ID типа сущности
            name: Название стадии
            sort: Порядок сортировки
            semantics: Семантика (process, success, failure)

        Returns:
            ID созданной стадии
        """
        params = {
            "fields": {
                "ENTITY_ID": f"DYNAMIC_{entity_type_id}_STAGE",
                "NAME": name,
                "SORT": sort,
                "SEMANTICS": semantics[0].upper() if semantics else "P",
            }
        }

        result = self._call("crm.status.add", params)
        return int(result.get("result", 0))

    def create_smart_process_item(
        self,
        entity_type_id: int,
        fields: dict
    ) -> int:
        """
        Создание элемента смарт-процесса.

        Args:
            entity_type_id: ID типа сущности
            fields: Поля элемента

        Returns:
            ID созданного элемента
        """
        params = {
            "entityTypeId": entity_type_id,
            "fields": fields
        }

        result = self._call("crm.item.add", params)
        item_data = result.get("result", {}).get("item", {})
        return int(item_data.get("id", 0))

    def find_smart_process_item(
        self,
        entity_type_id: int,
        filter_fields: dict
    ) -> Optional[dict]:
        """
        Поиск элемента смарт-процесса.

        Args:
            entity_type_id: ID типа сущности
            filter_fields: Фильтр поиска

        Returns:
            Данные элемента или None
        """
        if self.dry_run:
            return None

        params = {
            "entityTypeId": entity_type_id,
            "filter": filter_fields,
            "select": ["*", "UF_*"]
        }

        result = self._call("crm.item.list", params)
        items = result.get("result", {}).get("items", [])
        return items[0] if items else None

    def update_smart_process_item(
        self,
        entity_type_id: int,
        item_id: int,
        fields: dict
    ) -> bool:
        """
        Обновление элемента смарт-процесса.

        Args:
            entity_type_id: ID типа сущности
            item_id: ID элемента
            fields: Поля для обновления

        Returns:
            True при успехе
        """
        params = {
            "entityTypeId": entity_type_id,
            "id": item_id,
            "fields": fields
        }

        result = self._call("crm.item.update", params)
        return bool(result.get("result"))

    # ─────────────────────────────────────────────────────────────────────
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Нормализация номера телефона."""
        # Убираем всё кроме цифр и +
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
        # Если начинается с 8, меняем на +7
        if cleaned.startswith("8") and len(cleaned) == 11:
            cleaned = "+7" + cleaned[1:]
        # Если нет +, добавляем
        if not cleaned.startswith("+"):
            if cleaned.startswith("7") and len(cleaned) == 11:
                cleaned = "+" + cleaned
            elif len(cleaned) == 10:
                cleaned = "+7" + cleaned
        return cleaned

    @staticmethod
    def _map_currency(currency: str) -> str:
        """Маппинг валюты на код Б24."""
        mapping = {
            "RUB": "RUB",
            "руб": "RUB",
            "AED": "AED",
            "дирхам": "AED",
            "USD": "USD",
            "EUR": "EUR",
        }
        return mapping.get(currency, currency.upper())

    def test_connection(self) -> bool:
        """Проверка подключения к API."""
        if self.dry_run:
            logger.info("[DRY-RUN] Пропуск проверки подключения")
            return True

        try:
            result = self._call("crm.contact.list", {"select": ["ID"], "start": 0})
            logger.info("Подключение к Bitrix24 успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Bitrix24: {e}")
            return False


class Bitrix24Error(Exception):
    """Ошибка API Битрикс24."""

    def __init__(self, error_code: str, error_description: str):
        self.error_code = error_code
        self.error_description = error_description
        super().__init__(f"{error_code}: {error_description}")


# ═══════════════════════════════════════════════════════════════════════════
# ФУНКЦИИ СИНХРОНИЗАЦИИ
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


def sync_contacts(client: Bitrix24Client, contacts: list) -> SyncResult:
    """
    Синхронизация контактов с Битрикс24.

    Args:
        client: клиент Б24
        contacts: список контактов из contacts.json

    Returns:
        SyncResult с результатами синхронизации
    """
    result = SyncResult()
    logger.info(f"Синхронизация {len(contacts)} контактов...")

    # Загружаем существующие контакты в кэш
    if not client.dry_run:
        client.get_all_contacts()

    for contact in contacts:
        name = contact.get("name", "Неизвестный")
        phone = contact.get("phone", "")

        if not phone:
            result.add_skipped(name, "Нет телефона")
            continue

        try:
            # Проверяем существование
            existing_id = client.find_contact_by_phone(phone)

            if existing_id:
                # Обновляем существующий
                if client.update_contact(existing_id, contact):
                    result.add_updated(existing_id, name)
                    logger.debug(f"Обновлён контакт: {name} (ID: {existing_id})")
                else:
                    result.add_error(name, "Ошибка обновления")
            else:
                # Создаём новый
                new_id = client.create_contact(contact)
                if new_id:
                    result.add_created(new_id, name)
                    logger.debug(f"Создан контакт: {name} (ID: {new_id})")
                else:
                    result.add_error(name, "Ошибка создания")

        except Bitrix24Error as e:
            result.add_error(name, str(e))
            logger.error(f"Ошибка при обработке контакта {name}: {e}")
        except Exception as e:
            result.add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при обработке контакта {name}: {e}")

    logger.info(
        f"Контакты: создано {result.created}, обновлено {result.updated}, "
        f"пропущено {result.skipped}, ошибок {result.errors}"
    )

    return result


def sync_deals(
    client: Bitrix24Client,
    operations: list,
    contact_mapping: Optional[dict[str, int]] = None
) -> SyncResult:
    """
    Создание сделок из операций.

    Args:
        client: клиент Б24
        operations: список операций из operations.json
        contact_mapping: маппинг phone -> contact_id

    Returns:
        SyncResult с результатами синхронизации
    """
    result = SyncResult()
    logger.info(f"Синхронизация {len(operations)} операций в сделки...")

    # Если маппинг не передан, строим из кэша клиента
    if contact_mapping is None:
        contact_mapping = client._contacts_cache

    for operation in operations:
        description = operation.get("description", "Сделка")
        op_id = operation.get("id")
        phone = operation.get("phone", "")

        try:
            # Проверяем существование по внешнему ID
            if op_id:
                existing_id = client.find_deal_by_external_id(str(op_id))
                if existing_id:
                    # Обновляем
                    if client.update_deal(existing_id, operation):
                        result.add_updated(existing_id, description)
                        logger.debug(f"Обновлена сделка: {description} (ID: {existing_id})")
                    else:
                        result.add_error(description, "Ошибка обновления")
                    continue

            # Ищем связанный контакт
            contact_id = None
            if phone:
                normalized = client._normalize_phone(phone)
                contact_id = contact_mapping.get(normalized)

            # Создаём новую сделку
            new_id = client.create_deal(operation, contact_id)
            if new_id:
                result.add_created(new_id, description)
                logger.debug(f"Создана сделка: {description} (ID: {new_id})")
            else:
                result.add_error(description, "Ошибка создания")

        except Bitrix24Error as e:
            result.add_error(description, str(e))
            logger.error(f"Ошибка при создании сделки {description}: {e}")
        except Exception as e:
            result.add_error(description, str(e))
            logger.error(f"Неожиданная ошибка при создании сделки {description}: {e}")

    logger.info(
        f"Сделки: создано {result.created}, обновлено {result.updated}, "
        f"ошибок {result.errors}"
    )

    return result


def create_leads(client: Bitrix24Client, contacts: list, operations: list) -> SyncResult:
    """
    Создание лидов для новых контактов без сделок.

    Args:
        client: клиент Б24
        contacts: список контактов
        operations: список операций (для определения кто уже клиент)

    Returns:
        SyncResult с результатами
    """
    result = SyncResult()

    # Собираем телефоны, по которым уже есть операции
    phones_with_deals = {
        client._normalize_phone(op.get("phone", ""))
        for op in operations
        if op.get("phone")
    }

    # Контакты без сделок - потенциальные лиды
    new_contacts = [
        c for c in contacts
        if c.get("phone") and
        client._normalize_phone(c["phone"]) not in phones_with_deals
    ]

    logger.info(f"Создание лидов для {len(new_contacts)} контактов без сделок...")

    for contact in new_contacts:
        name = contact.get("name", "Неизвестный")
        phone = contact.get("phone", "")

        try:
            # Проверяем существование лида
            existing_id = client.find_lead_by_phone(phone)
            if existing_id:
                result.add_skipped(name, "Лид уже существует")
                continue

            # Проверяем существование контакта (уже клиент)
            existing_contact = client.find_contact_by_phone(phone)
            if existing_contact:
                result.add_skipped(name, "Уже есть контакт в CRM")
                continue

            # Создаём лид
            new_id = client.create_lead(contact)
            if new_id:
                result.add_created(new_id, name)
                logger.debug(f"Создан лид: {name} (ID: {new_id})")
            else:
                result.add_error(name, "Ошибка создания лида")

        except Bitrix24Error as e:
            result.add_error(name, str(e))
            logger.error(f"Ошибка при создании лида {name}: {e}")
        except Exception as e:
            result.add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при создании лида {name}: {e}")

    logger.info(
        f"Лиды: создано {result.created}, пропущено {result.skipped}, "
        f"ошибок {result.errors}"
    )

    return result


def sync_contacts_batch(client: Bitrix24Client, contacts: list) -> SyncResult:
    """
    Батчевая синхронизация контактов (оптимизированная версия).

    Args:
        client: клиент Б24
        contacts: список контактов

    Returns:
        SyncResult с результатами
    """
    result = SyncResult()
    logger.info(f"Батчевая синхронизация {len(contacts)} контактов...")

    # Загружаем существующие контакты
    if not client.dry_run:
        client.get_all_contacts()

    # Разделяем на новые и существующие
    to_create = []
    to_update = []

    for contact in contacts:
        phone = contact.get("phone", "")
        if not phone:
            result.add_skipped(contact.get("name", "?"), "Нет телефона")
            continue

        normalized = client._normalize_phone(phone)
        existing_id = client._contacts_cache.get(normalized)

        if existing_id:
            to_update.append((existing_id, contact))
        else:
            to_create.append(contact)

    # Батчевое создание
    if to_create and not client.dry_run:
        commands = {}
        for i, contact in enumerate(to_create):
            name_parts = (contact.get("name") or "Неизвестный").split(maxsplit=1)
            commands[f"create_{i}"] = ("crm.contact.add", {
                "fields": {
                    "NAME": name_parts[0],
                    "LAST_NAME": name_parts[1] if len(name_parts) > 1 else "",
                    "PHONE": [{"VALUE": contact.get("phone", ""), "VALUE_TYPE": "WORK"}],
                }
            })

        batch_result = client.batch(commands)

        for cmd_id, res in batch_result["result"].get("result", {}).items():
            idx = int(cmd_id.split("_")[1])
            contact = to_create[idx]
            if res:
                result.add_created(int(res), contact.get("name", "?"))
            else:
                result.add_error(contact.get("name", "?"), "Ошибка создания")
    elif to_create:
        # Dry-run: просто логируем
        for contact in to_create:
            result.add_created(0, contact.get("name", "?"))

    # Батчевое обновление
    if to_update and not client.dry_run:
        commands = {}
        for i, (contact_id, contact) in enumerate(to_update):
            commands[f"update_{i}"] = ("crm.contact.update", {
                "id": contact_id,
                "fields": {
                    "COMMENTS": contact.get("notes", ""),
                }
            })

        batch_result = client.batch(commands)

        for cmd_id, res in batch_result["result"].get("result", {}).items():
            idx = int(cmd_id.split("_")[1])
            _, contact = to_update[idx]
            if res:
                result.add_updated(to_update[idx][0], contact.get("name", "?"))
            else:
                result.add_error(contact.get("name", "?"), "Ошибка обновления")
    elif to_update:
        # Dry-run
        for contact_id, contact in to_update:
            result.add_updated(contact_id, contact.get("name", "?"))

    logger.info(
        f"Контакты (batch): создано {result.created}, обновлено {result.updated}, "
        f"пропущено {result.skipped}, ошибок {result.errors}"
    )

    return result


# ═══════════════════════════════════════════════════════════════════════════
# НАСТРОЙКА ВОРОНОК И СМАРТ-ПРОЦЕССОВ
# ═══════════════════════════════════════════════════════════════════════════

def setup_deal_categories(client: Bitrix24Client) -> SyncResult:
    """
    Создать воронки продаж для разных типов услуг.

    Args:
        client: клиент Б24

    Returns:
        SyncResult с результатами создания
    """
    result = SyncResult()
    logger.info("Настройка воронок продаж...")

    # Создаём глобальный маппинг для обновления DEAL_CATEGORY_MAPPING
    category_ids = {}

    for category_config in DEAL_CATEGORIES_CONFIG:
        name = category_config["NAME"]
        sort = category_config.get("SORT", 100)
        stages = category_config.get("STAGES", [])

        try:
            # Проверяем существование воронки
            existing_id = client.find_deal_category_by_name(name)

            if existing_id:
                logger.info(f"Воронка '{name}' уже существует (ID: {existing_id})")
                category_id = existing_id
                result.add_skipped(name, "Уже существует")
            else:
                # Создаём новую воронку
                category_id = client.create_deal_category(name, sort)
                if category_id:
                    logger.info(f"Создана воронка '{name}' (ID: {category_id})")
                    result.add_created(category_id, name)
                else:
                    result.add_error(name, "Ошибка создания воронки")
                    continue

            # Сохраняем ID для маппинга
            category_ids[name] = category_id

            # Устанавливаем стадии
            if stages and category_id:
                # Обновляем STATUS_ID с реальным ID воронки
                updated_stages = []
                for stage in stages:
                    updated_stage = stage.copy()
                    # Заменяем C1, C2, etc. на реальный ID
                    if "STATUS_ID" in updated_stage:
                        old_id = updated_stage["STATUS_ID"]
                        # Извлекаем часть после двоеточия
                        if ":" in old_id:
                            suffix = old_id.split(":")[1]
                            updated_stage["STATUS_ID"] = f"C{category_id}:{suffix}"
                    updated_stages.append(updated_stage)

                if client.set_deal_category_stages(category_id, updated_stages):
                    logger.info(f"  Установлено {len(stages)} стадий для '{name}'")
                else:
                    logger.warning(f"  Не удалось установить стадии для '{name}'")

        except Bitrix24Error as e:
            result.add_error(name, str(e))
            logger.error(f"Ошибка при создании воронки '{name}': {e}")
        except Exception as e:
            result.add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при создании воронки '{name}': {e}")

    # Выводим маппинг для обновления конфигурации
    if category_ids:
        logger.info("\nМаппинг воронок (обновите DEAL_CATEGORY_MAPPING):")
        for name, cat_id in category_ids.items():
            logger.info(f"  '{name}': {cat_id}")

    logger.info(
        f"Воронки: создано {result.created}, пропущено {result.skipped}, "
        f"ошибок {result.errors}"
    )

    return result


def setup_smart_processes(client: Bitrix24Client) -> SyncResult:
    """
    Создать смарт-процессы для кастомных сущностей.

    Args:
        client: клиент Б24

    Returns:
        SyncResult с результатами создания
    """
    result = SyncResult()
    logger.info("Настройка смарт-процессов...")

    smart_process_ids = {}

    for process_key, config in SMART_PROCESSES_CONFIG.items():
        title = config["TITLE"]
        code = config["CODE"]
        fields = config.get("FIELDS", [])
        stages = config.get("STAGES", [])

        try:
            # Проверяем существование
            existing = client.find_smart_process_by_code(code)

            if existing:
                entity_type_id = int(existing.get("entityTypeId", 0))
                logger.info(f"Смарт-процесс '{title}' уже существует (entityTypeId: {entity_type_id})")
                result.add_skipped(title, "Уже существует")
            else:
                # Создаём новый смарт-процесс
                entity_type_id = client.create_smart_process_type(title, code)
                if entity_type_id:
                    logger.info(f"Создан смарт-процесс '{title}' (entityTypeId: {entity_type_id})")
                    result.add_created(entity_type_id, title)
                else:
                    result.add_error(title, "Ошибка создания смарт-процесса")
                    continue

            smart_process_ids[process_key] = entity_type_id

            # Добавляем пользовательские поля
            if fields and entity_type_id:
                for field_config in fields:
                    field_name = field_config["FIELD_NAME"]
                    user_type_id = field_config["USER_TYPE_ID"]
                    label = field_config.get("EDIT_FORM_LABEL", {"ru": field_name})

                    try:
                        if client.add_smart_process_field(entity_type_id, field_name, user_type_id, label):
                            logger.debug(f"  Добавлено поле '{field_name}' в '{title}'")
                    except Bitrix24Error as e:
                        logger.warning(f"  Не удалось добавить поле '{field_name}': {e}")

                logger.info(f"  Обработано {len(fields)} полей для '{title}'")

            # Добавляем стадии
            if stages and entity_type_id:
                existing_stages = client.get_smart_process_stages(entity_type_id)
                existing_stage_names = {s.get("NAME") for s in existing_stages}

                added_stages = 0
                for stage_config in stages:
                    stage_name = stage_config["NAME"]
                    if stage_name not in existing_stage_names:
                        try:
                            client.add_smart_process_stage(
                                entity_type_id,
                                stage_name,
                                stage_config.get("SORT", 10),
                                stage_config.get("SEMANTICS", "process")
                            )
                            added_stages += 1
                        except Bitrix24Error as e:
                            logger.warning(f"  Не удалось добавить стадию '{stage_name}': {e}")

                if added_stages:
                    logger.info(f"  Добавлено {added_stages} стадий для '{title}'")

        except Bitrix24Error as e:
            result.add_error(title, str(e))
            logger.error(f"Ошибка при создании смарт-процесса '{title}': {e}")
        except Exception as e:
            result.add_error(title, str(e))
            logger.error(f"Неожиданная ошибка при создании смарт-процесса '{title}': {e}")

    # Выводим маппинг для использования в коде
    if smart_process_ids:
        logger.info("\nМаппинг смарт-процессов (entityTypeId):")
        for key, type_id in smart_process_ids.items():
            logger.info(f"  '{key}': {type_id}")

    logger.info(
        f"Смарт-процессы: создано {result.created}, пропущено {result.skipped}, "
        f"ошибок {result.errors}"
    )

    return result


def sync_referrals(client: Bitrix24Client) -> SyncResult:
    """
    Синхронизировать рефералы из referrals.json в смарт-процесс.

    Args:
        client: клиент Б24

    Returns:
        SyncResult с результатами синхронизации
    """
    result = SyncResult()

    # Путь к файлу рефералов
    referrals_file = JSON_DIR / "referrals.json"
    referrals = load_json_file(referrals_file)

    if not referrals:
        logger.warning(f"Файл рефералов не найден или пуст: {referrals_file}")
        return result

    logger.info(f"Синхронизация {len(referrals)} рефералов...")

    # Получаем entityTypeId смарт-процесса "Рефералы"
    referrals_sp = client.find_smart_process_by_code("REFERRALS")
    if not referrals_sp:
        logger.error("Смарт-процесс 'Рефералы' не найден. Сначала выполните --setup-smart")
        result.add_error("sync_referrals", "Смарт-процесс не найден")
        return result

    entity_type_id = int(referrals_sp.get("entityTypeId", 0))
    logger.info(f"Используется смарт-процесс entityTypeId: {entity_type_id}")

    for referral in referrals:
        # Формируем название для идентификации
        referrer_name = referral.get("referrer_name", referral.get("referrer", ""))
        referred_name = referral.get("referred_name", referral.get("referred", ""))
        name = f"{referrer_name} -> {referred_name}"

        try:
            # Проверяем существование по телефонам
            referrer_phone = referral.get("referrer_phone", "")
            referred_phone = referral.get("referred_phone", "")

            existing = None
            if referrer_phone and referred_phone:
                existing = client.find_smart_process_item(
                    entity_type_id,
                    {
                        "ufReferrerPhone": referrer_phone,
                        "ufReferredPhone": referred_phone
                    }
                )

            # Подготавливаем поля
            fields = {
                "title": name,
                "ufReferrerName": referrer_name,
                "ufReferrerPhone": referrer_phone,
                "ufReferredName": referred_name,
                "ufReferredPhone": referred_phone,
                "ufSource": referral.get("source", ""),
                "ufRevenue": referral.get("revenue", 0),
                "ufCommission": referral.get("commission", 0),
                "ufNotes": referral.get("notes", ""),
            }

            if referral.get("date"):
                fields["ufDate"] = referral["date"]

            if existing:
                # Обновляем
                item_id = int(existing.get("id", 0))
                if client.update_smart_process_item(entity_type_id, item_id, fields):
                    result.add_updated(item_id, name)
                    logger.debug(f"Обновлён реферал: {name} (ID: {item_id})")
                else:
                    result.add_error(name, "Ошибка обновления")
            else:
                # Создаём
                item_id = client.create_smart_process_item(entity_type_id, fields)
                if item_id:
                    result.add_created(item_id, name)
                    logger.debug(f"Создан реферал: {name} (ID: {item_id})")
                else:
                    result.add_error(name, "Ошибка создания")

        except Bitrix24Error as e:
            result.add_error(name, str(e))
            logger.error(f"Ошибка при синхронизации реферала '{name}': {e}")
        except Exception as e:
            result.add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при синхронизации реферала '{name}': {e}")

    logger.info(
        f"Рефералы: создано {result.created}, обновлено {result.updated}, "
        f"ошибок {result.errors}"
    )

    return result


def sync_complaints(client: Bitrix24Client) -> SyncResult:
    """
    Синхронизировать жалобы из complaints.json в смарт-процесс.

    Args:
        client: клиент Б24

    Returns:
        SyncResult с результатами синхронизации
    """
    result = SyncResult()

    # Путь к файлу жалоб
    complaints_file = JSON_DIR / "complaints.json"
    complaints = load_json_file(complaints_file)

    if not complaints:
        logger.warning(f"Файл жалоб не найден или пуст: {complaints_file}")
        return result

    logger.info(f"Синхронизация {len(complaints)} жалоб...")

    # Получаем entityTypeId смарт-процесса "Жалобы"
    complaints_sp = client.find_smart_process_by_code("COMPLAINTS")
    if not complaints_sp:
        logger.error("Смарт-процесс 'Жалобы' не найден. Сначала выполните --setup-smart")
        result.add_error("sync_complaints", "Смарт-процесс не найден")
        return result

    entity_type_id = int(complaints_sp.get("entityTypeId", 0))
    logger.info(f"Используется смарт-процесс entityTypeId: {entity_type_id}")

    for complaint in complaints:
        # Формируем название для идентификации
        client_name = complaint.get("client_name", complaint.get("client", ""))
        category = complaint.get("category", "other")
        category_ru = COMPLAINT_CATEGORY_MAPPING.get(category, category)
        date = complaint.get("date", "")
        name = f"{category_ru}: {client_name} ({date})"

        try:
            # Проверяем существование по ID если есть
            existing = None
            if complaint.get("id"):
                existing = client.find_smart_process_item(
                    entity_type_id,
                    {"title": name}  # Ищем по названию
                )

            # Подготавливаем поля
            severity = complaint.get("severity", "medium")
            severity_ru = COMPLAINT_SEVERITY_MAPPING.get(severity, severity)

            fields = {
                "title": name,
                "ufCategory": category_ru,
                "ufSeverity": severity_ru,
                "ufDescription": complaint.get("description", ""),
                "ufClientName": client_name,
                "ufClientPhone": complaint.get("client_phone", ""),
                "ufResolved": "Y" if complaint.get("resolved", False) else "N",
                "ufResolution": complaint.get("resolution", ""),
            }

            if date:
                fields["ufDate"] = date

            if complaint.get("resolved_date"):
                fields["ufResolvedDate"] = complaint["resolved_date"]

            if existing:
                # Обновляем
                item_id = int(existing.get("id", 0))
                if client.update_smart_process_item(entity_type_id, item_id, fields):
                    result.add_updated(item_id, name)
                    logger.debug(f"Обновлена жалоба: {name} (ID: {item_id})")
                else:
                    result.add_error(name, "Ошибка обновления")
            else:
                # Создаём
                item_id = client.create_smart_process_item(entity_type_id, fields)
                if item_id:
                    result.add_created(item_id, name)
                    logger.debug(f"Создана жалоба: {name} (ID: {item_id})")
                else:
                    result.add_error(name, "Ошибка создания")

        except Bitrix24Error as e:
            result.add_error(name, str(e))
            logger.error(f"Ошибка при синхронизации жалобы '{name}': {e}")
        except Exception as e:
            result.add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при синхронизации жалобы '{name}': {e}")

    logger.info(
        f"Жалобы: создано {result.created}, обновлено {result.updated}, "
        f"ошибок {result.errors}"
    )

    return result


def setup_all(client: Bitrix24Client) -> dict:
    """
    Настроить всю структуру Б24 (воронки + смарт-процессы).

    Args:
        client: клиент Б24

    Returns:
        Словарь с результатами всех операций
    """
    logger.info("=" * 60)
    logger.info("ПОЛНАЯ НАСТРОЙКА СТРУКТУРЫ BITRIX24")
    logger.info("=" * 60)

    results = {}

    # Шаг 1: Воронки продаж
    logger.info("\n[1/2] Настройка воронок продаж...")
    results["deal_categories"] = setup_deal_categories(client).to_dict()

    # Шаг 2: Смарт-процессы
    logger.info("\n[2/2] Настройка смарт-процессов...")
    results["smart_processes"] = setup_smart_processes(client).to_dict()

    logger.info("\n" + "=" * 60)
    logger.info("НАСТРОЙКА ЗАВЕРШЕНА")
    logger.info("=" * 60)

    return results


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
        description="Интеграция с Битрикс24 CRM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --sync-all           Синхронизация всего (контакты + сделки + лиды)
  %(prog)s --contacts           Только синхронизация контактов
  %(prog)s --deals              Только создание сделок
  %(prog)s --leads              Только создание лидов
  %(prog)s --sync-all --dry-run Тестовый запуск без реальных изменений
  %(prog)s --contacts --batch   Батчевая синхронизация контактов

Настройка структуры:
  %(prog)s --setup-categories   Создать воронки продаж
  %(prog)s --setup-smart        Создать смарт-процессы
  %(prog)s --setup-all          Создать всю структуру Б24
  %(prog)s --sync-referrals     Синхронизировать рефералы
  %(prog)s --sync-complaints    Синхронизировать жалобы

Переменные окружения:
  BITRIX24_DOMAIN      Домен Б24 (example.bitrix24.ru -> example)
  BITRIX24_USER_ID     ID пользователя вебхука
  BITRIX24_WEBHOOK_KEY Ключ вебхука
        """
    )

    # Группа синхронизации данных
    sync_group = parser.add_argument_group("Синхронизация данных")
    sync_group.add_argument(
        "--sync-all", action="store_true",
        help="Полная синхронизация (контакты + сделки + лиды)"
    )
    sync_group.add_argument(
        "--contacts", action="store_true",
        help="Синхронизация только контактов"
    )
    sync_group.add_argument(
        "--deals", action="store_true",
        help="Создание только сделок"
    )
    sync_group.add_argument(
        "--leads", action="store_true",
        help="Создание только лидов"
    )

    # Группа настройки структуры
    setup_group = parser.add_argument_group("Настройка структуры Б24")
    setup_group.add_argument(
        "--setup-categories", action="store_true",
        help="Создать воронки продаж"
    )
    setup_group.add_argument(
        "--setup-smart", action="store_true",
        help="Создать смарт-процессы"
    )
    setup_group.add_argument(
        "--setup-all", action="store_true",
        help="Создать всю структуру Б24 (воронки + смарт-процессы)"
    )

    # Группа синхронизации смарт-процессов
    smart_sync_group = parser.add_argument_group("Синхронизация смарт-процессов")
    smart_sync_group.add_argument(
        "--sync-referrals", action="store_true",
        help="Синхронизировать рефералы из referrals.json"
    )
    smart_sync_group.add_argument(
        "--sync-complaints", action="store_true",
        help="Синхронизировать жалобы из complaints.json"
    )

    # Общие параметры
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Тестовый режим (без реальных изменений)"
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="Использовать батчевые запросы (быстрее)"
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

    # Собираем все операции для проверки
    all_operations = [
        args.sync_all, args.contacts, args.deals, args.leads,
        args.setup_categories, args.setup_smart, args.setup_all,
        args.sync_referrals, args.sync_complaints
    ]

    # Проверка что выбрана хотя бы одна операция
    if not any(all_operations):
        parser.print_help()
        print("\nОшибка: Укажите хотя бы одну операцию")
        sys.exit(1)

    # Проверка конфигурации (только если не dry-run)
    if not args.dry_run and not validate_config():
        sys.exit(1)

    # Создание клиента
    client = Bitrix24Client(
        domain=BITRIX24_CONFIG["domain"] or "test",
        user_id=BITRIX24_CONFIG["user_id"] or "1",
        webhook_key=BITRIX24_CONFIG["webhook_key"] or "test",
        dry_run=args.dry_run
    )

    # Проверка подключения
    if not args.dry_run and not client.test_connection():
        logger.error("Не удалось подключиться к Bitrix24")
        sys.exit(1)

    results = {}

    # Выполнение операций
    try:
        # ─────────────────────────────────────────────────────────────────
        # НАСТРОЙКА СТРУКТУРЫ
        # ─────────────────────────────────────────────────────────────────

        if args.setup_all:
            # Полная настройка структуры
            results.update(setup_all(client))

        else:
            # Отдельные операции настройки
            if args.setup_categories:
                results["deal_categories"] = setup_deal_categories(client).to_dict()

            if args.setup_smart:
                results["smart_processes"] = setup_smart_processes(client).to_dict()

        # ─────────────────────────────────────────────────────────────────
        # СИНХРОНИЗАЦИЯ СМАРТ-ПРОЦЕССОВ
        # ─────────────────────────────────────────────────────────────────

        if args.sync_referrals:
            results["referrals"] = sync_referrals(client).to_dict()

        if args.sync_complaints:
            results["complaints"] = sync_complaints(client).to_dict()

        # ─────────────────────────────────────────────────────────────────
        # СИНХРОНИЗАЦИЯ ОСНОВНЫХ ДАННЫХ
        # ─────────────────────────────────────────────────────────────────

        # Загрузка данных только если нужна синхронизация
        if any([args.sync_all, args.contacts, args.deals, args.leads]):
            contacts = load_json_file(INPUT_FILES["contacts"])
            operations = load_json_file(INPUT_FILES["operations"])

            if not contacts and not operations:
                logger.warning("Нет данных для синхронизации")
            else:
                if args.sync_all or args.contacts:
                    if args.batch:
                        results["contacts"] = sync_contacts_batch(client, contacts).to_dict()
                    else:
                        results["contacts"] = sync_contacts(client, contacts).to_dict()

                if args.sync_all or args.deals:
                    results["deals"] = sync_deals(client, operations).to_dict()

                if args.sync_all or args.leads:
                    results["leads"] = create_leads(client, contacts, operations).to_dict()

    except KeyboardInterrupt:
        logger.warning("Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

    # Вывод итогов
    if results:
        print("\n" + "=" * 60)
        print("ИТОГИ ОПЕРАЦИЙ")
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
                "results": results
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"Результат сохранён в {output_path}")

    # Код возврата
    total_errors = sum(r.get("errors", 0) for r in results.values())
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
