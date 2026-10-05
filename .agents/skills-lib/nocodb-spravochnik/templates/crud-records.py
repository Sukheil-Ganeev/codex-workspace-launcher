"""
NocoDB API v2 -- Полный CRUD на Python (requests)
=================================================
Использование:
  1. Установить: pip install requests
  2. Заполнить настройки ниже (BASE_URL, API_TOKEN, TABLE_ID)
  3. python crud-records.py

Функции: Create, Read (с фильтрами), Update, Delete, Bulk-операции, Пагинация.
"""

import requests
import json
import sys
from typing import Any

# =============================================================================
# Настройки (ОБЯЗАТЕЛЬНО заполнить)
# =============================================================================
BASE_URL = "https://app.nocodb.com"       # URL вашего NocoDB
API_TOKEN = "YOUR_API_TOKEN_HERE"          # API Token из Settings -> Tokens
TABLE_ID = "YOUR_TABLE_ID_HERE"            # ID таблицы (формат: tbl_xxxxxxxx)

# Заголовки для всех запросов
HEADERS = {
    "xc-token": API_TOKEN,
    "Content-Type": "application/json",
}

# Базовый URL для работы с записями
RECORDS_URL = f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records"


# =============================================================================
# Вспомогательные функции
# =============================================================================

def handle_response(response: requests.Response, operation: str) -> dict | list | None:
    """Обработка ответа API с проверкой ошибок."""
    if response.status_code in (200, 201):
        return response.json()
    else:
        print(f"ОШИБКА [{operation}]: HTTP {response.status_code}")
        print(f"Ответ: {response.text}")
        return None


# =============================================================================
# CREATE -- Создание записей
# =============================================================================

def create_record(data: dict) -> dict | None:
    """Создать одну запись."""
    response = requests.post(RECORDS_URL, headers=HEADERS, json=data)
    result = handle_response(response, "CREATE")
    if result:
        print(f"Запись создана. ID: {result.get('Id')}")
    return result


def create_records_bulk(records: list[dict]) -> list | None:
    """Массовое создание записей (bulk)."""
    response = requests.post(RECORDS_URL, headers=HEADERS, json=records)
    result = handle_response(response, "BULK CREATE")
    if result:
        print(f"Создано записей: {len(result)}")
    return result


# =============================================================================
# READ -- Чтение записей
# =============================================================================

def get_record(record_id: int) -> dict | None:
    """Получить одну запись по ID."""
    url = f"{RECORDS_URL}/{record_id}"
    response = requests.get(url, headers=HEADERS)
    return handle_response(response, "GET")


def get_records(
    where: str = "",
    sort: str = "",
    fields: str = "",
    limit: int = 25,
    offset: int = 0,
    view_id: str = "",
) -> dict | None:
    """
    Получить список записей с фильтрами.

    Аргументы:
        where:   Фильтр, например "(Status,eq,Active)~and(Price,gt,100)"
        sort:    Сортировка, например "-CreatedAt,Price" (- = DESC)
        fields:  Поля через запятую, например "Title,Status,Price"
        limit:   Количество записей (макс. 1000)
        offset:  Смещение для пагинации
        view_id: ID представления (view)
    """
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if where:
        params["where"] = where
    if sort:
        params["sort"] = sort
    if fields:
        params["fields"] = fields
    if view_id:
        params["viewId"] = view_id

    response = requests.get(RECORDS_URL, headers=HEADERS, params=params)
    result = handle_response(response, "LIST")
    if result:
        page_info = result.get("pageInfo", {})
        print(
            f"Записей: {len(result.get('list', []))} "
            f"из {page_info.get('totalRows', '?')} "
            f"(стр. {page_info.get('page', '?')})"
        )
    return result


def get_all_records(where: str = "", sort: str = "", fields: str = "") -> list[dict]:
    """
    Получить ВСЕ записи с автоматической пагинацией.

    Обходит лимит в 1000 записей за запрос.
    """
    all_records = []
    offset = 0
    limit = 1000  # Максимальный лимит на запрос

    while True:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if where:
            params["where"] = where
        if sort:
            params["sort"] = sort
        if fields:
            params["fields"] = fields

        response = requests.get(RECORDS_URL, headers=HEADERS, params=params)
        result = handle_response(response, "PAGINATE")

        if not result:
            break

        records = result.get("list", [])
        all_records.extend(records)

        page_info = result.get("pageInfo", {})
        is_last = page_info.get("isLastPage", True)

        print(f"  Загружено: {len(all_records)} / {page_info.get('totalRows', '?')}")

        if is_last or len(records) == 0:
            break

        offset += limit

    print(f"Всего получено записей: {len(all_records)}")
    return all_records


# =============================================================================
# UPDATE -- Обновление записей
# =============================================================================

def update_record(record_id: int, data: dict) -> dict | None:
    """Обновить одну запись. В data должен быть 'Id'."""
    data["Id"] = record_id
    response = requests.patch(RECORDS_URL, headers=HEADERS, json=data)
    result = handle_response(response, "UPDATE")
    if result:
        print(f"Запись {record_id} обновлена.")
    return result


def update_records_bulk(records: list[dict]) -> list | None:
    """
    Массовое обновление записей (bulk).

    Каждый элемент должен содержать 'Id' и обновляемые поля.
    Пример: [{"Id": 1, "Status": "Done"}, {"Id": 2, "Status": "Done"}]
    """
    response = requests.patch(RECORDS_URL, headers=HEADERS, json=records)
    result = handle_response(response, "BULK UPDATE")
    if result:
        print(f"Обновлено записей: {len(result)}")
    return result


# =============================================================================
# DELETE -- Удаление записей
# =============================================================================

def delete_record(record_id: int) -> dict | None:
    """Удалить одну запись по ID."""
    response = requests.delete(
        RECORDS_URL, headers=HEADERS, json=[{"Id": record_id}]
    )
    result = handle_response(response, "DELETE")
    if result:
        print(f"Запись {record_id} удалена.")
    return result


def delete_records_bulk(record_ids: list[int]) -> list | None:
    """
    Массовое удаление записей (bulk).

    Аргумент: список ID, например [1, 2, 3]
    """
    payload = [{"Id": rid} for rid in record_ids]
    response = requests.delete(RECORDS_URL, headers=HEADERS, json=payload)
    result = handle_response(response, "BULK DELETE")
    if result:
        print(f"Удалено записей: {len(result)}")
    return result


# =============================================================================
# Демонстрация
# =============================================================================

def demo():
    """Демонстрация всех операций CRUD."""
    print("=" * 60)
    print("NocoDB API v2 -- Демонстрация CRUD")
    print("=" * 60)
    print()

    # --- CREATE ---
    print("--- CREATE: Одна запись ---")
    new_record = create_record({
        "Название": "Desert Safari VIP",
        "Статус": "Заявка",
        "Количество": 4,
        "Цена продажи": 600,
        "Себестоимость": 400,
        "Дата экскурсии": "2026-03-01",
    })
    print()

    # --- CREATE BULK ---
    print("--- CREATE: Массовое создание ---")
    bulk_records = create_records_bulk([
        {"Название": "City Tour Dubai", "Статус": "Подтверждено", "Цена продажи": 200},
        {"Название": "Abu Dhabi Full Day", "Статус": "Заявка", "Цена продажи": 350},
        {"Название": "Yacht Cruise 3h", "Статус": "Оплачено", "Цена продажи": 1500},
    ])
    print()

    # --- READ: С фильтрами ---
    print("--- READ: Активные записи ---")
    get_records(where="(Статус,eq,Заявка)", sort="-CreatedAt", limit=10)
    print()

    # --- READ: Выборочные поля ---
    print("--- READ: Только название и цена ---")
    get_records(fields="Название,Цена продажи", limit=5)
    print()

    # --- READ: Все записи (пагинация) ---
    print("--- READ: Все записи с пагинацией ---")
    all_recs = get_all_records()
    print()

    # --- UPDATE ---
    if new_record and new_record.get("Id"):
        rid = new_record["Id"]
        print(f"--- UPDATE: Запись {rid} ---")
        update_record(rid, {"Статус": "Подтверждено", "Количество": 6})
        print()

    # --- UPDATE BULK ---
    if bulk_records and len(bulk_records) >= 2:
        print("--- UPDATE: Массовое обновление ---")
        update_records_bulk([
            {"Id": bulk_records[0]["Id"], "Статус": "Завершено"},
            {"Id": bulk_records[1]["Id"], "Статус": "Завершено"},
        ])
        print()

    # --- DELETE ---
    if new_record and new_record.get("Id"):
        print(f"--- DELETE: Запись {new_record['Id']} ---")
        delete_record(new_record["Id"])
        print()

    # --- DELETE BULK ---
    if bulk_records and len(bulk_records) >= 2:
        ids_to_delete = [r["Id"] for r in bulk_records]
        print(f"--- DELETE: Массовое удаление {ids_to_delete} ---")
        delete_records_bulk(ids_to_delete)
        print()

    print("=" * 60)
    print("Демонстрация завершена.")
    print("=" * 60)


if __name__ == "__main__":
    # Проверка заполнения настроек
    if "YOUR_" in API_TOKEN or "YOUR_" in TABLE_ID:
        print("ОШИБКА: Заполните настройки API_TOKEN и TABLE_ID в начале файла.")
        print("API Token: Settings -> Tokens в NocoDB")
        print("Table ID: URL таблицы или API Meta endpoints")
        sys.exit(1)

    demo()
