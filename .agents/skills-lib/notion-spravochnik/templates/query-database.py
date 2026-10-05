"""
Запрос к базе данных Notion с фильтрами и сортировкой.
Пример: получение бронирований на сегодня/завтра для туристического бизнеса ОАЭ.

Требования:
    pip install notion-client

Переменные окружения:
    NOTION_TOKEN - токен Internal Integration (ntn_***)
    NOTION_BOOKINGS_DB - ID базы данных Bookings

Использование:
    NOTION_TOKEN=ntn_*** NOTION_BOOKINGS_DB=abc123 python query-database.py
"""

import os
from datetime import datetime, timedelta
from notion_client import Client
from notion_client.helpers import collect_paginated_api

notion = Client(auth=os.environ["NOTION_TOKEN"])
BOOKINGS_DB = os.environ["NOTION_BOOKINGS_DB"]


def query_today_bookings():
    """Получить все бронирования на сегодня."""
    today = datetime.now().strftime("%Y-%m-%d")

    results = notion.databases.query(
        database_id=BOOKINGS_DB,
        filter={
            "and": [
                {"property": "Date", "date": {"equals": today}},
                {
                    "property": "Status",
                    "select": {"does_not_equal": "Cancelled"},
                },
            ]
        },
        sorts=[{"property": "Date", "direction": "ascending"}],
    )

    return results["results"]


def query_upcoming_bookings(days=7):
    """Получить бронирования на ближайшие N дней."""
    today = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    results = notion.databases.query(
        database_id=BOOKINGS_DB,
        filter={
            "and": [
                {"property": "Date", "date": {"on_or_after": today}},
                {"property": "Date", "date": {"on_or_before": end_date}},
                {"property": "Status", "select": {"equals": "Confirmed"}},
            ]
        },
        sorts=[{"property": "Date", "direction": "ascending"}],
    )

    return results["results"]


def query_unpaid_bookings():
    """Получить неоплаченные подтвержденные бронирования."""
    results = notion.databases.query(
        database_id=BOOKINGS_DB,
        filter={
            "and": [
                {"property": "Status", "select": {"equals": "Confirmed"}},
                {
                    "property": "Status",
                    "select": {"does_not_equal": "Paid"},
                },
            ]
        },
        sorts=[{"property": "Date", "direction": "ascending"}],
    )

    return results["results"]


def query_all_with_pagination():
    """Получить ВСЕ записи с автопагинацией (cursor-based)."""
    all_pages = collect_paginated_api(
        notion.databases.query, database_id=BOOKINGS_DB
    )
    return all_pages


def extract_booking_info(page):
    """Извлечь ключевые данные из записи бронирования."""
    props = page["properties"]

    title_arr = props.get("Booking Name", {}).get("title", [])
    name = title_arr[0]["plain_text"] if title_arr else "N/A"

    date_obj = props.get("Date", {}).get("date")
    date = date_obj["start"] if date_obj else "No date"

    status_obj = props.get("Status", {}).get("select")
    status = status_obj["name"] if status_obj else "N/A"

    price = props.get("Price AED", {}).get("number", 0) or 0

    pax = props.get("Pax", {}).get("number", 0) or 0

    category_obj = props.get("Category", {}).get("select")
    category = category_obj["name"] if category_obj else "N/A"

    return {
        "id": page["id"],
        "name": name,
        "date": date,
        "status": status,
        "price_aed": price,
        "pax": pax,
        "category": category,
    }


if __name__ == "__main__":
    print("=== Бронирования на сегодня ===")
    today_bookings = query_today_bookings()
    for page in today_bookings:
        info = extract_booking_info(page)
        print(f"  {info['name']} | {info['date']} | {info['status']} | "
              f"{info['price_aed']} AED | {info['pax']} pax | {info['category']}")

    print(f"\nВсего на сегодня: {len(today_bookings)}")

    print("\n=== Ближайшие 7 дней (подтверждённые) ===")
    upcoming = query_upcoming_bookings(7)
    for page in upcoming:
        info = extract_booking_info(page)
        print(f"  {info['name']} | {info['date']} | {info['price_aed']} AED")

    print(f"\nВсего подтверждённых: {len(upcoming)}")
