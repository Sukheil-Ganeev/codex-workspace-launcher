#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Управление каталогом товаров/услуг в Битрикс24.

Создание категорий и товаров для туристических услуг в ОАЭ.

Использование:
    python bitrix24_products.py --setup           # Создать весь каталог
    python bitrix24_products.py --list            # Показать текущий каталог
    python bitrix24_products.py --update-prices prices.json  # Обновить цены
    python bitrix24_products.py --export          # Выгрузить каталог в JSON
    python bitrix24_products.py --setup --dry-run # Тестовый режим
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
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
sys.path.insert(0, str(SCRIPT_DIR))

from config import JSON_DIR, BITRIX24_CONFIG

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

# Путь к файлу каталога
CATALOG_FILE = ASSETS_DIR / "bitrix24_products.json"

# Rate limiting
RATE_LIMIT_REQUESTS = 2  # запросов в секунду (Б24 ограничение)
RATE_LIMIT_BATCH = 50  # максимум команд в batch запросе
REQUEST_TIMEOUT = 30  # секунд

# ═══════════════════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

LOG_DIR = JSON_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "bitrix24_products.log", encoding="utf-8"),
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

class Bitrix24ProductClient:
    """Клиент для работы с каталогом товаров Битрикс24."""

    def __init__(self, domain: str, user_id: str, webhook_key: str, dry_run: bool = False):
        self.domain = domain
        self.user_id = user_id
        self.webhook_key = webhook_key
        self.dry_run = dry_run
        self.base_url = f"https://{domain}.bitrix24.ru/rest/{user_id}/{webhook_key}"
        self.last_request_time = 0
        self.session = requests.Session()

        # Кэш для маппинга
        self._sections_cache: dict[str, int] = {}  # code -> section_id
        self._products_cache: dict[str, int] = {}  # code -> product_id

    def _rate_limit(self):
        """Соблюдение rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0 / RATE_LIMIT_REQUESTS:
            time.sleep(1.0 / RATE_LIMIT_REQUESTS - elapsed)
        self.last_request_time = time.time()

    def _call(self, method: str, params: Optional[dict] = None) -> dict:
        """Выполнение REST API запроса."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] {method}: {json.dumps(params, ensure_ascii=False, indent=2)[:500]}")
            # Возвращаем корректный формат для dry-run
            if method.endswith(".add"):
                return {"result": 999999}
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

    # ─────────────────────────────────────────────────────────────────────
    # СЕКЦИИ (КАТЕГОРИИ) ТОВАРОВ
    # ─────────────────────────────────────────────────────────────────────

    def get_sections(self) -> list[dict]:
        """Получить все секции каталога."""
        if self.dry_run:
            return []

        all_sections = []
        start = 0

        while True:
            result = self._call("crm.productsection.list", {
                "select": ["ID", "NAME", "CODE", "SORT", "SECTION_ID"],
                "start": start
            })

            sections = result.get("result", [])
            if not sections:
                break

            all_sections.extend(sections)

            if result.get("next"):
                start = result["next"]
            else:
                break

        # Заполняем кэш
        for section in all_sections:
            if section.get("CODE"):
                self._sections_cache[section["CODE"]] = int(section["ID"])

        logger.info(f"Загружено {len(all_sections)} секций каталога")
        return all_sections

    def find_section_by_code(self, code: str) -> Optional[int]:
        """Найти секцию по коду."""
        if code in self._sections_cache:
            return self._sections_cache[code]

        if self.dry_run:
            return None

        result = self._call("crm.productsection.list", {
            "filter": {"CODE": code},
            "select": ["ID"]
        })

        sections = result.get("result", [])
        if sections:
            section_id = int(sections[0]["ID"])
            self._sections_cache[code] = section_id
            return section_id

        return None

    def create_section(self, category: dict) -> int:
        """
        Создать секцию (категорию) товаров.

        Args:
            category: данные категории

        Returns:
            ID созданной секции
        """
        params = {
            "fields": {
                "NAME": category["name"],
                "CODE": category.get("code", ""),
                "SORT": category.get("sort", 500),
                "DESCRIPTION": category.get("description", ""),
            }
        }

        result = self._call("crm.productsection.add", params)
        section_id = int(result.get("result", 0))

        if section_id and category.get("code"):
            self._sections_cache[category["code"]] = section_id

        return section_id

    def update_section(self, section_id: int, category: dict) -> bool:
        """Обновить секцию."""
        params = {
            "id": section_id,
            "fields": {
                "NAME": category["name"],
                "SORT": category.get("sort", 500),
                "DESCRIPTION": category.get("description", ""),
            }
        }

        result = self._call("crm.productsection.update", params)
        return bool(result.get("result"))

    # ─────────────────────────────────────────────────────────────────────
    # ТОВАРЫ
    # ─────────────────────────────────────────────────────────────────────

    def get_products(self, section_id: Optional[int] = None) -> list[dict]:
        """Получить все товары (опционально по секции)."""
        if self.dry_run:
            return []

        all_products = []
        start = 0

        filter_params = {}
        if section_id:
            filter_params["SECTION_ID"] = section_id

        while True:
            result = self._call("crm.product.list", {
                "filter": filter_params,
                "select": [
                    "ID", "NAME", "CODE", "PRICE", "CURRENCY_ID",
                    "SECTION_ID", "SORT", "ACTIVE", "DESCRIPTION",
                    "MEASURE", "PREVIEW_TEXT"
                ],
                "start": start
            })

            products = result.get("result", [])
            if not products:
                break

            all_products.extend(products)

            if result.get("next"):
                start = result["next"]
            else:
                break

        # Заполняем кэш
        for product in all_products:
            if product.get("CODE"):
                self._products_cache[product["CODE"]] = int(product["ID"])

        logger.info(f"Загружено {len(all_products)} товаров")
        return all_products

    def find_product_by_code(self, code: str) -> Optional[int]:
        """Найти товар по коду."""
        if code in self._products_cache:
            return self._products_cache[code]

        if self.dry_run:
            return None

        result = self._call("crm.product.list", {
            "filter": {"CODE": code},
            "select": ["ID"]
        })

        products = result.get("result", [])
        if products:
            product_id = int(products[0]["ID"])
            self._products_cache[code] = product_id
            return product_id

        return None

    def create_product(self, product: dict, section_id: Optional[int] = None) -> int:
        """
        Создать товар.

        Args:
            product: данные товара
            section_id: ID секции (если не указан, берётся из product)

        Returns:
            ID созданного товара
        """
        # Определяем секцию
        if section_id is None:
            category_code = product.get("category_code")
            if category_code:
                section_id = self._sections_cache.get(category_code)

        params = {
            "fields": {
                "NAME": product["name"],
                "CODE": product.get("code", ""),
                "PRICE": product.get("price", 0),
                "CURRENCY_ID": product.get("currency", "AED"),
                "SORT": product.get("sort", 500),
                "ACTIVE": "Y" if product.get("active", True) else "N",
                "DESCRIPTION": product.get("description_full", product.get("description", "")),
                "PREVIEW_TEXT": product.get("description", ""),
            }
        }

        if section_id:
            params["fields"]["SECTION_ID"] = section_id

        # Единица измерения
        unit_mapping = {
            "чел": 796,  # штуки/человек
            "поездка": 796,
            "час": 356,  # часы
            "аренда": 796,
            "билет": 796,
        }
        unit = product.get("unit", "чел")
        params["fields"]["MEASURE"] = unit_mapping.get(unit, 796)

        result = self._call("crm.product.add", params)
        product_id = int(result.get("result", 0))

        if product_id and product.get("code"):
            self._products_cache[product["code"]] = product_id

        return product_id

    def update_product(self, product_id: int, product: dict) -> bool:
        """Обновить товар."""
        params = {
            "id": product_id,
            "fields": {
                "NAME": product["name"],
                "PRICE": product.get("price", 0),
                "CURRENCY_ID": product.get("currency", "AED"),
                "SORT": product.get("sort", 500),
                "ACTIVE": "Y" if product.get("active", True) else "N",
                "DESCRIPTION": product.get("description_full", product.get("description", "")),
                "PREVIEW_TEXT": product.get("description", ""),
            }
        }

        result = self._call("crm.product.update", params)
        return bool(result.get("result"))

    def update_product_price(self, product_id: int, price: float, currency: str = "AED") -> bool:
        """Обновить только цену товара."""
        params = {
            "id": product_id,
            "fields": {
                "PRICE": price,
                "CURRENCY_ID": currency,
            }
        }

        result = self._call("crm.product.update", params)
        return bool(result.get("result"))

    # ─────────────────────────────────────────────────────────────────────
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ─────────────────────────────────────────────────────────────────────

    def test_connection(self) -> bool:
        """Проверка подключения к API."""
        if self.dry_run:
            logger.info("[DRY-RUN] Пропуск проверки подключения")
            return True

        try:
            result = self._call("crm.product.list", {"select": ["ID"], "start": 0})
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
# ФУНКЦИИ РАБОТЫ С КАТАЛОГОМ
# ═══════════════════════════════════════════════════════════════════════════

def load_catalog(file_path: Path = CATALOG_FILE) -> dict:
    """Загрузить каталог из JSON файла."""
    if not file_path.exists():
        logger.error(f"Файл каталога не найден: {file_path}")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON {file_path}: {e}")
        return {}


def save_catalog(catalog: dict, file_path: Path = CATALOG_FILE):
    """Сохранить каталог в JSON файл."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    logger.info(f"Каталог сохранён в {file_path}")


def setup_product_catalog(client: Bitrix24ProductClient, catalog: dict) -> dict[str, SyncResult]:
    """
    Создать категории и товары в Битрикс24.

    Args:
        client: клиент Б24
        catalog: данные каталога

    Returns:
        dict с результатами по секциям и товарам
    """
    results = {
        "sections": SyncResult(),
        "products": SyncResult()
    }

    # Загружаем существующие данные в кэш
    if not client.dry_run:
        client.get_sections()
        client.get_products()

    # ─────────────────────────────────────────────────────────────────
    # СЕКЦИИ (КАТЕГОРИИ)
    # ─────────────────────────────────────────────────────────────────
    categories = catalog.get("categories", [])
    logger.info(f"Синхронизация {len(categories)} категорий...")

    for category in categories:
        name = category.get("name", "")
        code = category.get("code", "")

        try:
            existing_id = client.find_section_by_code(code) if code else None

            if existing_id:
                if client.update_section(existing_id, category):
                    results["sections"].add_updated(existing_id, name)
                    logger.debug(f"Обновлена категория: {name} (ID: {existing_id})")
                else:
                    results["sections"].add_error(name, "Ошибка обновления")
            else:
                new_id = client.create_section(category)
                if new_id:
                    results["sections"].add_created(new_id, name)
                    logger.debug(f"Создана категория: {name} (ID: {new_id})")
                else:
                    results["sections"].add_error(name, "Ошибка создания")

        except Bitrix24Error as e:
            results["sections"].add_error(name, str(e))
            logger.error(f"Ошибка при обработке категории {name}: {e}")
        except Exception as e:
            results["sections"].add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при обработке категории {name}: {e}")

    # ─────────────────────────────────────────────────────────────────
    # ТОВАРЫ
    # ─────────────────────────────────────────────────────────────────
    products = catalog.get("products", [])
    logger.info(f"Синхронизация {len(products)} товаров...")

    for product in products:
        name = product.get("name", "")
        code = product.get("code", "")

        try:
            existing_id = client.find_product_by_code(code) if code else None

            if existing_id:
                if client.update_product(existing_id, product):
                    results["products"].add_updated(existing_id, name)
                    logger.debug(f"Обновлён товар: {name} (ID: {existing_id})")
                else:
                    results["products"].add_error(name, "Ошибка обновления")
            else:
                new_id = client.create_product(product)
                if new_id:
                    results["products"].add_created(new_id, name)
                    logger.debug(f"Создан товар: {name} (ID: {new_id})")
                else:
                    results["products"].add_error(name, "Ошибка создания")

        except Bitrix24Error as e:
            results["products"].add_error(name, str(e))
            logger.error(f"Ошибка при обработке товара {name}: {e}")
        except Exception as e:
            results["products"].add_error(name, str(e))
            logger.error(f"Неожиданная ошибка при обработке товара {name}: {e}")

    return results


def list_products(client: Bitrix24ProductClient) -> dict:
    """
    Показать текущий каталог из Битрикс24.

    Returns:
        dict с секциями и товарами
    """
    sections = client.get_sections()
    products = client.get_products()

    # Группируем товары по секциям
    products_by_section: dict[int, list] = {}
    for product in products:
        section_id = int(product.get("SECTION_ID", 0))
        if section_id not in products_by_section:
            products_by_section[section_id] = []
        products_by_section[section_id].append(product)

    return {
        "sections": sections,
        "products": products,
        "products_by_section": products_by_section
    }


def update_prices(client: Bitrix24ProductClient, prices_file: Path) -> SyncResult:
    """
    Обновить цены из JSON файла.

    Args:
        client: клиент Б24
        prices_file: путь к файлу с ценами

    Returns:
        SyncResult с результатами
    """
    result = SyncResult()

    if not prices_file.exists():
        logger.error(f"Файл цен не найден: {prices_file}")
        return result

    try:
        with open(prices_file, "r", encoding="utf-8") as f:
            prices_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON {prices_file}: {e}")
        return result

    # Загружаем существующие товары
    if not client.dry_run:
        client.get_products()

    # Формат файла цен:
    # {"products": [{"code": "TOUR_ABUDHABI_FULL", "price": 550}, ...]}
    # или
    # {"TOUR_ABUDHABI_FULL": 550, "TOUR_DUBAI_CITY": 450, ...}

    if "products" in prices_data:
        price_updates = {p["code"]: p for p in prices_data["products"]}
    else:
        price_updates = {code: {"price": price} for code, price in prices_data.items()}

    logger.info(f"Обновление {len(price_updates)} цен...")

    for code, update_data in price_updates.items():
        try:
            product_id = client.find_product_by_code(code)

            if not product_id:
                result.add_skipped(code, "Товар не найден")
                continue

            price = update_data.get("price") if isinstance(update_data, dict) else update_data
            currency = update_data.get("currency", "AED") if isinstance(update_data, dict) else "AED"

            if client.update_product_price(product_id, price, currency):
                result.add_updated(product_id, f"{code}: {price} {currency}")
                logger.debug(f"Обновлена цена: {code} -> {price} {currency}")
            else:
                result.add_error(code, "Ошибка обновления")

        except Bitrix24Error as e:
            result.add_error(code, str(e))
            logger.error(f"Ошибка при обновлении цены {code}: {e}")
        except Exception as e:
            result.add_error(code, str(e))
            logger.error(f"Неожиданная ошибка при обновлении цены {code}: {e}")

    return result


def export_catalog(client: Bitrix24ProductClient, output_file: Optional[Path] = None) -> dict:
    """
    Выгрузить каталог из Битрикс24 в JSON.

    Args:
        client: клиент Б24
        output_file: путь для сохранения (опционально)

    Returns:
        dict с каталогом
    """
    sections = client.get_sections()
    products = client.get_products()

    # Преобразуем в формат нашего каталога
    catalog = {
        "catalog_name": "Экспорт из Битрикс24",
        "currency": "AED",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "exported_from": f"{client.domain}.bitrix24.ru",
        "categories": [],
        "products": []
    }

    # Секции
    for section in sections:
        catalog["categories"].append({
            "id": int(section["ID"]),
            "name": section.get("NAME", ""),
            "code": section.get("CODE", ""),
            "sort": int(section.get("SORT", 500)),
        })

    # Товары
    for product in products:
        catalog["products"].append({
            "id": int(product["ID"]),
            "category_id": int(product.get("SECTION_ID", 0)),
            "name": product.get("NAME", ""),
            "code": product.get("CODE", ""),
            "price": float(product.get("PRICE", 0)),
            "currency": product.get("CURRENCY_ID", "AED"),
            "description": product.get("PREVIEW_TEXT", ""),
            "description_full": product.get("DESCRIPTION", ""),
            "active": product.get("ACTIVE") == "Y",
            "sort": int(product.get("SORT", 500)),
        })

    # Сохраняем если указан путь
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        logger.info(f"Каталог экспортирован в {output_file}")

    return catalog


def print_catalog_table(data: dict):
    """Вывести каталог в виде таблицы."""
    sections = data.get("sections", [])
    products_by_section = data.get("products_by_section", {})

    print("\n" + "=" * 80)
    print("KATALOG TOVAROV BITRIX24")
    print("=" * 80)

    if not sections:
        print("\nKatalog pust ili nedostupen.")
        return

    for section in sections:
        section_id = int(section["ID"])
        section_name = section.get("NAME", "Bez nazvaniya")
        section_code = section.get("CODE", "")

        print(f"\n{'-' * 80}")
        print(f"[{section_code}] {section_name}")
        print(f"{'-' * 80}")
        print(f"{'Kod':<25} {'Nazvanie':<35} {'Tsena':>10} {'Valuta':>8}")
        print(f"{'-' * 25} {'-' * 35} {'-' * 10} {'-' * 8}")

        section_products = products_by_section.get(section_id, [])
        if not section_products:
            print("  (net tovarov)")
            continue

        for product in sorted(section_products, key=lambda x: int(x.get("SORT", 500))):
            code = product.get("CODE", "")[:24]
            name = product.get("NAME", "")[:34]
            price = float(product.get("PRICE", 0))
            currency = product.get("CURRENCY_ID", "AED")

            print(f"{code:<25} {name:<35} {price:>10.0f} {currency:>8}")

    # Товары без секции
    no_section_products = products_by_section.get(0, [])
    if no_section_products:
        print(f"\n{'-' * 80}")
        print("BEZ KATEGORII")
        print(f"{'-' * 80}")
        for product in no_section_products:
            print(f"  - {product.get('NAME', '')} ({product.get('PRICE', 0)} {product.get('CURRENCY_ID', '')})")

    # Статистика
    total_products = sum(len(p) for p in products_by_section.values())
    print(f"\n{'=' * 80}")
    print(f"Vsego kategoriy: {len(sections)}")
    print(f"Vsego tovarov: {total_products}")
    print("=" * 80)


def print_local_catalog(catalog: dict):
    """Вывести локальный каталог в виде таблицы."""
    print("\n" + "=" * 80)
    print(f"LOCAL CATALOG: {catalog.get('catalog_name', 'No name')}")
    print(f"Currency: {catalog.get('currency', 'N/A')}")
    print(f"Updated: {catalog.get('last_updated', 'N/A')}")
    print("=" * 80)

    categories = {c["id"]: c for c in catalog.get("categories", [])}
    products = catalog.get("products", [])

    # Группируем товары по категориям
    products_by_cat: dict[int, list] = {}
    for product in products:
        cat_id = product.get("category_id", 0)
        if cat_id not in products_by_cat:
            products_by_cat[cat_id] = []
        products_by_cat[cat_id].append(product)

    for cat_id, cat_products in sorted(products_by_cat.items()):
        category = categories.get(cat_id, {"name": "No category", "code": ""})

        print(f"\n{'-' * 80}")
        print(f"[{category.get('code', '')}] {category.get('name', '')}")
        print(f"{'-' * 80}")
        print(f"{'Code':<25} {'Name':<35} {'Price':>10} {'Unit':>8}")
        print(f"{'-' * 25} {'-' * 35} {'-' * 10} {'-' * 8}")

        for product in sorted(cat_products, key=lambda x: x.get("sort", 500)):
            code = product.get("code", "")[:24]
            name = product.get("name", "")[:34]
            price = product.get("price", 0)
            unit = product.get("unit", "")[:7]

            print(f"{code:<25} {name:<35} {price:>10.0f} {unit:>8}")

    print(f"\n{'=' * 80}")
    print(f"Total categories: {len(categories)}")
    print(f"Total products: {len(products)}")
    print("=" * 80)


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
        description="Управление каталогом товаров в Битрикс24",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --setup              Создать весь каталог в Б24
  %(prog)s --list               Показать текущий каталог из Б24
  %(prog)s --list --local       Показать локальный каталог (JSON)
  %(prog)s --update-prices p.json  Обновить цены из файла
  %(prog)s --export             Выгрузить каталог из Б24 в JSON
  %(prog)s --setup --dry-run    Тестовый запуск без изменений

Файл каталога: assets/bitrix24_products.json

Формат файла цен (--update-prices):
  {"TOUR_ABUDHABI_FULL": 550, "TOUR_DUBAI_CITY": 450}
  или
  {"products": [{"code": "TOUR_ABUDHABI_FULL", "price": 550}]}

Переменные окружения:
  BITRIX24_DOMAIN      Домен Б24 (example.bitrix24.ru -> example)
  BITRIX24_USER_ID     ID пользователя вебхука
  BITRIX24_WEBHOOK_KEY Ключ вебхука
        """
    )

    parser.add_argument(
        "--setup", action="store_true",
        help="Создать категории и товары в Б24"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Показать текущий каталог"
    )
    parser.add_argument(
        "--local", action="store_true",
        help="Показать локальный каталог (вместо Б24)"
    )
    parser.add_argument(
        "--update-prices", type=str, metavar="FILE",
        help="Обновить цены из JSON файла"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Выгрузить каталог из Б24 в JSON"
    )
    parser.add_argument(
        "--output", "-o", type=str,
        help="Путь для сохранения результата"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Тестовый режим (без реальных изменений)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Подробный вывод"
    )

    args = parser.parse_args()

    # Настройка логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Проверка что выбрана хотя бы одна операция
    if not any([args.setup, args.list, args.update_prices, args.export]):
        parser.print_help()
        print("\nОшибка: Укажите операцию (--setup, --list, --update-prices, --export)")
        sys.exit(1)

    # Для --list --local не нужно подключение к Б24
    if args.list and args.local:
        catalog = load_catalog()
        if catalog:
            print_local_catalog(catalog)
        else:
            print("Локальный каталог не найден или пуст")
        sys.exit(0)

    # Проверка конфигурации (только если не dry-run)
    if not args.dry_run and not validate_config():
        sys.exit(1)

    # Создание клиента
    client = Bitrix24ProductClient(
        domain=BITRIX24_CONFIG["domain"] or "test",
        user_id=BITRIX24_CONFIG["user_id"] or "1",
        webhook_key=BITRIX24_CONFIG["webhook_key"] or "test",
        dry_run=args.dry_run
    )

    # Проверка подключения
    if not args.dry_run and not client.test_connection():
        logger.error("Не удалось подключиться к Bitrix24")
        sys.exit(1)

    # Выполнение операций
    try:
        if args.setup:
            catalog = load_catalog()
            if not catalog:
                logger.error("Не удалось загрузить каталог")
                sys.exit(1)

            results = setup_product_catalog(client, catalog)

            # Вывод итогов
            print("\n" + "=" * 60)
            print("ИТОГИ СОЗДАНИЯ КАТАЛОГА")
            print("=" * 60)

            for entity, result in results.items():
                data = result.to_dict()
                print(f"\n{entity.upper()}:")
                print(f"  Создано:   {data['created']}")
                print(f"  Обновлено: {data['updated']}")
                print(f"  Пропущено: {data['skipped']}")
                print(f"  Ошибок:    {data['errors']}")

            # Сохранение лога
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "dry_run": args.dry_run,
                        "results": {k: v.to_dict() for k, v in results.items()}
                    }, f, ensure_ascii=False, indent=2)
                logger.info(f"Лог сохранён в {output_path}")

        elif args.list:
            data = list_products(client)
            print_catalog_table(data)

        elif args.update_prices:
            prices_file = Path(args.update_prices)
            result = update_prices(client, prices_file)

            print("\n" + "=" * 60)
            print("ИТОГИ ОБНОВЛЕНИЯ ЦЕН")
            print("=" * 60)
            data = result.to_dict()
            print(f"  Обновлено: {data['updated']}")
            print(f"  Пропущено: {data['skipped']}")
            print(f"  Ошибок:    {data['errors']}")

        elif args.export:
            output_file = Path(args.output) if args.output else JSON_DIR / "bitrix24_catalog_export.json"
            catalog = export_catalog(client, output_file)
            print(f"\nЭкспортировано:")
            print(f"  Категорий: {len(catalog.get('categories', []))}")
            print(f"  Товаров:   {len(catalog.get('products', []))}")
            print(f"  Файл:      {output_file}")

    except KeyboardInterrupt:
        logger.warning("Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
