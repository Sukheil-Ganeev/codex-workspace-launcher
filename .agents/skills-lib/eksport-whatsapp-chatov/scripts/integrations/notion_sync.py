#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notion Sync - Синхронизация контактов и операций с Notion.

Использование:
    python notion_sync.py --sync-all       # Полная синхронизация
    python notion_sync.py --contacts       # Только контакты
    python notion_sync.py --operations     # Только операции
    python notion_sync.py --setup          # Создать базы данных
    python notion_sync.py --sync-all --dry-run  # Тестовый режим

Переменные окружения:
    NOTION_API_KEY       - API ключ интеграции Notion
    NOTION_CONTACTS_DB   - ID базы данных контактов
    NOTION_OPERATIONS_DB - ID базы данных операций
    NOTION_PARENT_PAGE   - ID родительской страницы для создания баз

Автор: WhatsApp Export Skill
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Добавляем путь к config.py
sys.path.insert(0, str(Path(__file__).parent))

try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    print("[!] notion-client не установлен. Установите: pip install notion-client")

# ═══════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

# Пути к данным
DATA_DIR = Path("D:/Downloads/Chats/_база/json")
CONTACTS_FILE = DATA_DIR / "contacts.json"
PROFILES_FILE = DATA_DIR / "profiles.json"
OPERATIONS_FILE = DATA_DIR / "operations.json"

# Notion API
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_CONTACTS_DB = os.getenv("NOTION_CONTACTS_DB", "")
NOTION_OPERATIONS_DB = os.getenv("NOTION_OPERATIONS_DB", "")
NOTION_PARENT_PAGE = os.getenv("NOTION_PARENT_PAGE", "")

# Rate limiting (Notion limit: 3 requests/sec)
RATE_LIMIT_DELAY = 0.35  # секунды между запросами

# Маппинг типов контактов
TYPE_MAPPING = {
    "клиенты": "Клиент",
    "агенты": "Агент",
    "поставщики": "Поставщик",
    "сотрудники": "Сотрудник",
    # English variants
    "client": "Клиент",
    "agent": "Агент",
    "supplier": "Поставщик",
    "employee": "Сотрудник",
}

# Маппинг источников
SOURCE_MAPPING = {
    "whatsapp": "WhatsApp",
    "wa_business": "WA Business",
    "both": "Both",
}

# Маппинг типов операций
OPERATION_TYPE_MAPPING = {
    "tour": "tour",
    "transfer": "transfer",
    "yacht": "yacht",
    "tickets": "tickets",
    "exchange": "exchange",
    "car_rental": "car_rental",
    "catering": "catering",
    "other": "other",
}

# Маппинг статусов операций
STATUS_MAPPING = {
    "inquiry": "inquiry",
    "pending": "inquiry",
    "booked": "booked",
    "confirmed": "booked",
    "completed": "completed",
    "cancelled": "cancelled",
    "canceled": "cancelled",
}

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# NOTION SYNC CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class NotionSync:
    """Класс для синхронизации данных с Notion."""

    def __init__(self, dry_run: bool = False):
        """
        Инициализация синхронизатора.

        Args:
            dry_run: Если True, не выполняет реальных изменений
        """
        self.dry_run = dry_run
        self.client: Optional[Client] = None
        self.contacts_db_id = NOTION_CONTACTS_DB
        self.operations_db_id = NOTION_OPERATIONS_DB
        self.parent_page_id = NOTION_PARENT_PAGE

        # Кэш существующих записей
        self._contacts_cache: Dict[str, str] = {}  # phone -> page_id
        self._jid_cache: Dict[str, str] = {}       # jid -> page_id

        # Статистика
        self.stats = {
            "contacts_created": 0,
            "contacts_updated": 0,
            "contacts_skipped": 0,
            "operations_created": 0,
            "operations_updated": 0,
            "operations_skipped": 0,
            "errors": 0,
        }

    def connect(self) -> bool:
        """Подключиться к Notion API."""
        if not NOTION_CLIENT_AVAILABLE:
            logger.error("notion-client не установлен")
            return False

        if not NOTION_API_KEY:
            logger.error("NOTION_API_KEY не установлен")
            logger.info("Установите: export NOTION_API_KEY='secret_xxx...'")
            return False

        try:
            self.client = Client(auth=NOTION_API_KEY)
            # Проверка подключения
            self.client.users.me()
            logger.info("Подключено к Notion API")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Notion: {e}")
            return False

    def _rate_limit(self):
        """Задержка для соблюдения rate limit."""
        time.sleep(RATE_LIMIT_DELAY)

    def _normalize_phone(self, phone: str) -> str:
        """Нормализовать телефонный номер."""
        if not phone:
            return ""
        # Убираем все кроме цифр и +
        normalized = ''.join(c for c in phone if c.isdigit() or c == '+')
        # Добавляем + если нет
        if normalized and not normalized.startswith('+'):
            normalized = '+' + normalized
        return normalized

    def _extract_phone_from_jid(self, jid: str) -> str:
        """Извлечь телефон из WhatsApp JID."""
        if not jid:
            return ""
        # JID формат: 79123456789@s.whatsapp.net
        phone = jid.split('@')[0]
        return self._normalize_phone(phone)

    # ───────────────────────────────────────────────────────────────────────────
    # РАБОТА С КОНТАКТАМИ
    # ───────────────────────────────────────────────────────────────────────────

    def _build_contacts_cache(self):
        """Построить кэш существующих контактов."""
        if not self.contacts_db_id:
            logger.warning("ID базы контактов не установлен")
            return

        logger.info("Загрузка существующих контактов из Notion...")

        try:
            has_more = True
            start_cursor = None
            count = 0

            while has_more:
                self._rate_limit()

                params = {"database_id": self.contacts_db_id}
                if start_cursor:
                    params["start_cursor"] = start_cursor

                response = self.client.databases.query(**params)

                for page in response.get("results", []):
                    page_id = page["id"]
                    props = page.get("properties", {})

                    # Извлекаем телефон
                    phone_prop = props.get("Phone", {})
                    phone = phone_prop.get("phone_number", "")
                    if phone:
                        normalized = self._normalize_phone(phone)
                        self._contacts_cache[normalized] = page_id

                    # Извлекаем JID
                    jid_prop = props.get("WhatsApp JID", {})
                    if jid_prop.get("rich_text"):
                        jid = jid_prop["rich_text"][0].get("plain_text", "")
                        if jid:
                            self._jid_cache[jid] = page_id

                    count += 1

                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")

            logger.info(f"Загружено {count} существующих контактов")

        except APIResponseError as e:
            logger.error(f"Ошибка загрузки контактов: {e}")

    def _find_contact_page(self, phone: str, jid: str = None) -> Optional[str]:
        """Найти существующую страницу контакта."""
        normalized_phone = self._normalize_phone(phone)

        # Сначала ищем по телефону
        if normalized_phone in self._contacts_cache:
            return self._contacts_cache[normalized_phone]

        # Затем по JID
        if jid and jid in self._jid_cache:
            return self._jid_cache[jid]

        # Пробуем найти по телефону из JID
        if jid:
            phone_from_jid = self._extract_phone_from_jid(jid)
            if phone_from_jid in self._contacts_cache:
                return self._contacts_cache[phone_from_jid]

        return None

    def _build_contact_properties(self, contact: Dict) -> Dict:
        """Построить свойства контакта для Notion."""
        props = {}

        # Name (title) - обязательное поле
        name = contact.get("name", "Unknown")
        props["Name"] = {
            "title": [{"text": {"content": name[:2000]}}]
        }

        # Phone
        phone = self._normalize_phone(contact.get("phone", ""))
        if phone:
            props["Phone"] = {"phone_number": phone}

        # Type (select)
        contact_type = contact.get("type", "клиенты").lower()
        mapped_type = TYPE_MAPPING.get(contact_type, "Клиент")
        props["Type"] = {"select": {"name": mapped_type}}

        # Subtype (select)
        subtype = contact.get("subtype", "")
        if subtype:
            props["Subtype"] = {"select": {"name": subtype[:100]}}

        # Source (select)
        source = contact.get("source", "whatsapp").lower()
        mapped_source = SOURCE_MAPPING.get(source, "WhatsApp")
        props["Source"] = {"select": {"name": mapped_source}}

        # Messages (number)
        messages = contact.get("total_messages", 0)
        if messages:
            props["Messages"] = {"number": int(messages)}

        # LTV (number)
        ltv_data = contact.get("ltv", {})
        if isinstance(ltv_data, dict):
            ltv = ltv_data.get("historical_ltv_aed", 0)
        else:
            ltv = 0
        if ltv:
            props["LTV"] = {"number": float(ltv)}

        # Language (select)
        language = contact.get("language", "").lower()
        if language in ["ru", "en", "ar"]:
            props["Language"] = {"select": {"name": language}}

        # Tags (multi-select)
        tags = contact.get("tags", [])
        if tags and isinstance(tags, list):
            # Ограничиваем количество тегов
            tag_options = [{"name": str(t)[:100]} for t in tags[:10]]
            props["Tags"] = {"multi_select": tag_options}

        # Last Contact (date)
        last_message = contact.get("last_message", "")
        if last_message:
            try:
                # Проверяем формат даты
                datetime.strptime(last_message, "%Y-%m-%d")
                props["Last Contact"] = {"date": {"start": last_message}}
            except ValueError:
                pass

        # WhatsApp JID (text)
        jid = contact.get("jid", "")
        if jid:
            props["WhatsApp JID"] = {
                "rich_text": [{"text": {"content": jid[:2000]}}]
            }

        return props

    def sync_contact(self, contact: Dict) -> Tuple[str, Optional[str]]:
        """
        Синхронизировать один контакт.

        Returns:
            Tuple[action, page_id]: ("created", id), ("updated", id), ("skipped", None), ("error", None)
        """
        phone = contact.get("phone", "")
        jid = contact.get("jid", "")
        name = contact.get("name", "Unknown")

        # Ищем существующий контакт
        existing_page_id = self._find_contact_page(phone, jid)

        properties = self._build_contact_properties(contact)

        if self.dry_run:
            if existing_page_id:
                logger.info(f"[DRY-RUN] Обновление: {name} ({phone})")
                return ("updated", existing_page_id)
            else:
                logger.info(f"[DRY-RUN] Создание: {name} ({phone})")
                return ("created", None)

        try:
            self._rate_limit()

            if existing_page_id:
                # Обновляем существующий
                self.client.pages.update(
                    page_id=existing_page_id,
                    properties=properties
                )
                logger.debug(f"Обновлён: {name}")
                return ("updated", existing_page_id)
            else:
                # Создаём новый
                response = self.client.pages.create(
                    parent={"database_id": self.contacts_db_id},
                    properties=properties
                )
                page_id = response["id"]

                # Добавляем в кэш
                normalized_phone = self._normalize_phone(phone)
                if normalized_phone:
                    self._contacts_cache[normalized_phone] = page_id
                if jid:
                    self._jid_cache[jid] = page_id

                logger.debug(f"Создан: {name}")
                return ("created", page_id)

        except APIResponseError as e:
            logger.error(f"Ошибка для {name}: {e}")
            return ("error", None)

    def sync_contacts(self) -> Dict[str, int]:
        """
        Синхронизировать все контакты.

        Returns:
            Статистика синхронизации
        """
        if not self.contacts_db_id:
            logger.error("NOTION_CONTACTS_DB не установлен")
            return self.stats

        # Загружаем контакты
        if not CONTACTS_FILE.exists():
            logger.error(f"Файл не найден: {CONTACTS_FILE}")
            return self.stats

        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            contacts = json.load(f)

        logger.info(f"Загружено {len(contacts)} контактов из файла")

        # Обогащаем профилями если есть
        profiles_map = {}
        if PROFILES_FILE.exists():
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                for profile in profiles:
                    phone = profile.get("phone", "")
                    if phone:
                        profiles_map[self._normalize_phone(phone)] = profile

        # Строим кэш существующих контактов
        if not self.dry_run:
            self._build_contacts_cache()

        # Дедупликация по телефону
        unique_contacts = {}
        for contact in contacts:
            phone = self._normalize_phone(contact.get("phone", ""))
            jid = contact.get("jid", "")

            # Ключ для дедупликации
            key = phone or jid or contact.get("name", "")

            if key in unique_contacts:
                # Объединяем данные, предпочитая непустые значения
                existing = unique_contacts[key]
                for k, v in contact.items():
                    if v and not existing.get(k):
                        existing[k] = v
            else:
                unique_contacts[key] = contact.copy()

        logger.info(f"После дедупликации: {len(unique_contacts)} уникальных контактов")

        # Синхронизируем
        for i, (key, contact) in enumerate(unique_contacts.items(), 1):
            # Добавляем данные из профиля
            phone = self._normalize_phone(contact.get("phone", ""))
            if phone in profiles_map:
                profile = profiles_map[phone]
                # Дополняем контакт данными профиля
                if not contact.get("ltv"):
                    contact["ltv"] = {"historical_ltv_aed": profile.get("total_spent_aed", 0)}

            action, page_id = self.sync_contact(contact)

            if action == "created":
                self.stats["contacts_created"] += 1
            elif action == "updated":
                self.stats["contacts_updated"] += 1
            elif action == "skipped":
                self.stats["contacts_skipped"] += 1
            else:
                self.stats["errors"] += 1

            # Прогресс каждые 50 контактов
            if i % 50 == 0:
                logger.info(f"Обработано {i}/{len(unique_contacts)} контактов...")

        logger.info(f"Контакты: создано {self.stats['contacts_created']}, "
                   f"обновлено {self.stats['contacts_updated']}, "
                   f"ошибок {self.stats['errors']}")

        return self.stats

    # ───────────────────────────────────────────────────────────────────────────
    # РАБОТА С ОПЕРАЦИЯМИ
    # ───────────────────────────────────────────────────────────────────────────

    def _build_operation_properties(self, operation: Dict, contact_page_id: Optional[str] = None) -> Dict:
        """Построить свойства операции для Notion."""
        props = {}

        # Title (title)
        description = operation.get("description", "")
        op_type = operation.get("type", "other")
        title = description or f"Operation: {op_type}"
        props["Title"] = {
            "title": [{"text": {"content": title[:2000]}}]
        }

        # Date
        date = operation.get("date", "")
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
                props["Date"] = {"date": {"start": date}}
            except ValueError:
                pass

        # Type (select)
        op_type = operation.get("type", "other").lower()
        mapped_type = OPERATION_TYPE_MAPPING.get(op_type, "other")
        props["Type"] = {"select": {"name": mapped_type}}

        # Amount (number)
        amount = operation.get("amount", 0)
        if amount:
            props["Amount"] = {"number": float(amount)}

        # Currency (select)
        currency = operation.get("currency", "AED").upper()
        if currency in ["AED", "RUB", "USD"]:
            props["Currency"] = {"select": {"name": currency}}

        # Status (select)
        status = operation.get("status", "inquiry").lower()
        mapped_status = STATUS_MAPPING.get(status, "inquiry")
        props["Status"] = {"select": {"name": mapped_status}}

        # Contact (relation) - связь с контактом
        if contact_page_id:
            props["Contact"] = {
                "relation": [{"id": contact_page_id}]
            }

        return props

    def sync_operation(self, operation: Dict) -> Tuple[str, Optional[str]]:
        """
        Синхронизировать одну операцию.

        Returns:
            Tuple[action, page_id]
        """
        phone = operation.get("phone", "")
        description = operation.get("description", "Operation")

        # Находим связанный контакт
        contact_page_id = self._find_contact_page(phone)

        properties = self._build_operation_properties(operation, contact_page_id)

        if self.dry_run:
            linked = "с контактом" if contact_page_id else "без связи"
            logger.info(f"[DRY-RUN] Создание операции: {description} ({linked})")
            return ("created", None)

        try:
            self._rate_limit()

            # Создаём операцию (операции обычно не обновляем, только создаём)
            response = self.client.pages.create(
                parent={"database_id": self.operations_db_id},
                properties=properties
            )
            page_id = response["id"]
            logger.debug(f"Создана операция: {description}")
            return ("created", page_id)

        except APIResponseError as e:
            logger.error(f"Ошибка для операции {description}: {e}")
            return ("error", None)

    def sync_operations(self) -> Dict[str, int]:
        """
        Синхронизировать все операции.

        Returns:
            Статистика синхронизации
        """
        if not self.operations_db_id:
            logger.error("NOTION_OPERATIONS_DB не установлен")
            return self.stats

        # Загружаем операции
        if not OPERATIONS_FILE.exists():
            logger.error(f"Файл не найден: {OPERATIONS_FILE}")
            return self.stats

        with open(OPERATIONS_FILE, 'r', encoding='utf-8') as f:
            operations = json.load(f)

        logger.info(f"Загружено {len(operations)} операций из файла")

        # Строим кэш контактов для связей
        if not self.dry_run and not self._contacts_cache:
            self._build_contacts_cache()

        # Синхронизируем
        for i, operation in enumerate(operations, 1):
            action, page_id = self.sync_operation(operation)

            if action == "created":
                self.stats["operations_created"] += 1
            elif action == "updated":
                self.stats["operations_updated"] += 1
            else:
                self.stats["errors"] += 1

            # Прогресс
            if i % 50 == 0:
                logger.info(f"Обработано {i}/{len(operations)} операций...")

        logger.info(f"Операции: создано {self.stats['operations_created']}, "
                   f"ошибок {self.stats['errors']}")

        return self.stats

    # ───────────────────────────────────────────────────────────────────────────
    # СОЗДАНИЕ БАЗ ДАННЫХ
    # ───────────────────────────────────────────────────────────────────────────

    def create_contacts_database(self) -> Optional[str]:
        """Создать базу данных контактов."""
        if not self.parent_page_id:
            logger.error("NOTION_PARENT_PAGE не установлен")
            return None

        properties = {
            "Name": {"title": {}},
            "Phone": {"phone_number": {}},
            "Type": {
                "select": {
                    "options": [
                        {"name": "Клиент", "color": "blue"},
                        {"name": "Агент", "color": "green"},
                        {"name": "Поставщик", "color": "orange"},
                        {"name": "Сотрудник", "color": "purple"},
                    ]
                }
            },
            "Subtype": {"select": {"options": []}},
            "Source": {
                "select": {
                    "options": [
                        {"name": "WhatsApp", "color": "green"},
                        {"name": "WA Business", "color": "blue"},
                        {"name": "Both", "color": "purple"},
                    ]
                }
            },
            "Messages": {"number": {"format": "number"}},
            "LTV": {"number": {"format": "number"}},
            "Language": {
                "select": {
                    "options": [
                        {"name": "ru", "color": "blue"},
                        {"name": "en", "color": "red"},
                        {"name": "ar", "color": "green"},
                    ]
                }
            },
            "Tags": {"multi_select": {"options": []}},
            "Last Contact": {"date": {}},
            "WhatsApp JID": {"rich_text": {}},
        }

        if self.dry_run:
            logger.info("[DRY-RUN] Создание базы 'Контакты'")
            return None

        try:
            self._rate_limit()
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.parent_page_id},
                title=[{"type": "text", "text": {"content": "Контакты"}}],
                properties=properties
            )
            db_id = response["id"]
            logger.info(f"База 'Контакты' создана: {db_id}")
            return db_id
        except APIResponseError as e:
            logger.error(f"Ошибка создания базы контактов: {e}")
            return None

    def create_operations_database(self) -> Optional[str]:
        """Создать базу данных операций."""
        if not self.parent_page_id:
            logger.error("NOTION_PARENT_PAGE не установлен")
            return None

        properties = {
            "Title": {"title": {}},
            "Contact": {
                "relation": {
                    "database_id": self.contacts_db_id,
                    "single_property": {}
                }
            } if self.contacts_db_id else {"rich_text": {}},
            "Date": {"date": {}},
            "Type": {
                "select": {
                    "options": [
                        {"name": "tour", "color": "blue"},
                        {"name": "transfer", "color": "green"},
                        {"name": "yacht", "color": "purple"},
                        {"name": "tickets", "color": "orange"},
                        {"name": "exchange", "color": "yellow"},
                        {"name": "car_rental", "color": "red"},
                        {"name": "catering", "color": "pink"},
                        {"name": "other", "color": "gray"},
                    ]
                }
            },
            "Amount": {"number": {"format": "number"}},
            "Currency": {
                "select": {
                    "options": [
                        {"name": "AED", "color": "green"},
                        {"name": "RUB", "color": "blue"},
                        {"name": "USD", "color": "red"},
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "inquiry", "color": "gray"},
                        {"name": "booked", "color": "yellow"},
                        {"name": "completed", "color": "green"},
                        {"name": "cancelled", "color": "red"},
                    ]
                }
            },
        }

        if self.dry_run:
            logger.info("[DRY-RUN] Создание базы 'Операции'")
            return None

        try:
            self._rate_limit()
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.parent_page_id},
                title=[{"type": "text", "text": {"content": "Операции"}}],
                properties=properties
            )
            db_id = response["id"]
            logger.info(f"База 'Операции' создана: {db_id}")
            return db_id
        except APIResponseError as e:
            logger.error(f"Ошибка создания базы операций: {e}")
            return None

    def setup_databases(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Создать обе базы данных.

        Returns:
            (contacts_db_id, operations_db_id)
        """
        logger.info("Создание баз данных в Notion...")

        # Сначала создаём контакты
        contacts_id = self.create_contacts_database()
        if contacts_id:
            self.contacts_db_id = contacts_id

        # Затем операции (со связью на контакты)
        operations_id = self.create_operations_database()

        return contacts_id, operations_id


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def print_setup_instructions():
    """Вывести инструкции по настройке."""
    instructions = """
================================================================================
                      NASTROYKA NOTION INTEGRATION
================================================================================

  1. Sozdayte Notion Integration:
     - Otkroyte https://www.notion.so/my-integrations
     - Nazhmite "+ New integration"
     - Nazvanie: "WhatsApp Sync"
     - Capabilities: Read/Write content, Read/Update databases
     - Skopiruyte Internal Integration Token (secret_xxx...)

  2. Podelites' stranitsej s integratsiej:
     - Otkroyte stranitsu v Notion gde budut bazy
     - Nazhmite "Share" -> "Invite"
     - Vyberite vashu integratsiyu "WhatsApp Sync"
     - Skopiruyte ID stranitsy iz URL (32 simvola posle /)

  3. Ustanovite peremennye okruzheniya:

     Windows (PowerShell):
     $env:NOTION_API_KEY = "secret_xxx..."
     $env:NOTION_PARENT_PAGE = "page_id_xxx..."

     Windows (CMD):
     set NOTION_API_KEY=secret_xxx...
     set NOTION_PARENT_PAGE=page_id_xxx...

     Linux/macOS:
     export NOTION_API_KEY="secret_xxx..."
     export NOTION_PARENT_PAGE="page_id_xxx..."

  4. Sozdayte bazy dannykh:
     python notion_sync.py --setup

  5. Ustanovite ID sozdannykh baz:
     $env:NOTION_CONTACTS_DB = "contacts_db_id"
     $env:NOTION_OPERATIONS_DB = "operations_db_id"

  6. Zapustite sinkhronizatsiyu:
     python notion_sync.py --sync-all

================================================================================
"""
    print(instructions)


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description="Синхронизация контактов и операций с Notion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python notion_sync.py --sync-all         Полная синхронизация
  python notion_sync.py --contacts         Только контакты
  python notion_sync.py --operations       Только операции
  python notion_sync.py --setup            Создать базы данных
  python notion_sync.py --sync-all --dry-run  Тестовый режим

Переменные окружения:
  NOTION_API_KEY        API ключ интеграции
  NOTION_CONTACTS_DB    ID базы контактов
  NOTION_OPERATIONS_DB  ID базы операций
  NOTION_PARENT_PAGE    ID страницы для создания баз
        """
    )

    parser.add_argument('--sync-all', action='store_true',
                       help='Синхронизировать контакты и операции')
    parser.add_argument('--contacts', action='store_true',
                       help='Синхронизировать только контакты')
    parser.add_argument('--operations', action='store_true',
                       help='Синхронизировать только операции')
    parser.add_argument('--setup', action='store_true',
                       help='Создать базы данных в Notion')
    parser.add_argument('--dry-run', action='store_true',
                       help='Тестовый режим без изменений')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    parser.add_argument('--help-setup', action='store_true',
                       help='Показать инструкции по настройке')

    args = parser.parse_args()

    # Инструкции
    if args.help_setup:
        print_setup_instructions()
        return 0

    # Если нет аргументов - показываем справку
    if not any([args.sync_all, args.contacts, args.operations, args.setup]):
        parser.print_help()
        print("\n[!] Используйте --help-setup для инструкций по настройке")
        return 1

    # Настройка логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Проверка библиотеки
    if not NOTION_CLIENT_AVAILABLE:
        print("[!] Установите библиотеку: pip install notion-client")
        return 1

    # Создаём синхронизатор
    sync = NotionSync(dry_run=args.dry_run)

    if args.dry_run:
        logger.info("=== ТЕСТОВЫЙ РЕЖИМ (dry-run) ===")

    # Подключаемся
    if not sync.connect():
        print_setup_instructions()
        return 1

    # Выполняем действия
    if args.setup:
        contacts_id, operations_id = sync.setup_databases()
        if contacts_id or operations_id:
            print(f"\n[OK] Базы данных созданы!")
            if contacts_id:
                print(f"     NOTION_CONTACTS_DB={contacts_id}")
            if operations_id:
                print(f"     NOTION_OPERATIONS_DB={operations_id}")
            print("\n     Добавьте эти ID в переменные окружения")
        return 0

    if args.contacts or args.sync_all:
        logger.info("=== Синхронизация контактов ===")
        sync.sync_contacts()

    if args.operations or args.sync_all:
        logger.info("=== Синхронизация операций ===")
        sync.sync_operations()

    # Итоговая статистика
    print("\n" + "="*60)
    print("ИТОГО:")
    print(f"  Контакты:  создано {sync.stats['contacts_created']}, "
          f"обновлено {sync.stats['contacts_updated']}")
    print(f"  Операции:  создано {sync.stats['operations_created']}, "
          f"обновлено {sync.stats['operations_updated']}")
    print(f"  Ошибок:    {sync.stats['errors']}")
    print("="*60)

    return 0 if sync.stats['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
