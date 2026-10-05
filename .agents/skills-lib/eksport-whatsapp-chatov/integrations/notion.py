#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интеграция с Notion.
Синхронизация контактов и операций.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from config import check_api_key, get_api_key

class NotionIntegration:
    """Интеграция с Notion API."""

    def __init__(self):
        self.api_key = None
        self.headers = None
        self.base_url = "https://api.notion.com/v1"

    def connect(self) -> bool:
        """Подключиться к Notion API."""
        if not check_api_key('notion'):
            print("[X] NOTION_API_KEY не настроен")
            print("   Установите: export NOTION_API_KEY='your_key'")
            return False

        self.api_key = get_api_key('notion')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        return True

    def sync_contacts(self, contacts: List[Dict], database_id: str) -> int:
        """
        Синхронизировать контакты в Notion database.

        Args:
            contacts: Список контактов [{name, phone, type, topic}]
            database_id: ID базы данных Notion

        Returns:
            Количество синхронизированных записей
        """
        if not self.connect():
            return 0

        try:
            import requests
        except ImportError:
            print("[X] requests не установлен: pip install requests")
            return 0

        synced = 0
        for contact in contacts:
            properties = {
                "Имя": {"title": [{"text": {"content": contact.get('name', '')}}]},
                "Телефон": {"phone_number": contact.get('phone', '')},
                "Тип": {"select": {"name": contact.get('type', 'клиент')}},
                "Тематика": {"select": {"name": contact.get('topic', 'общее')}},
            }

            data = {
                "parent": {"database_id": database_id},
                "properties": properties
            }

            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=data
            )

            if response.status_code == 200:
                synced += 1
            else:
                print(f"  [!] Ошибка для {contact.get('name')}: {response.status_code}")

        return synced

    def sync_operations(self, operations: List[Dict], database_id: str) -> int:
        """
        Синхронизировать операции в Notion.

        Args:
            operations: Список операций [{date, contact, amount, currency}]
            database_id: ID базы данных Notion
        """
        if not self.connect():
            return 0

        try:
            import requests
        except ImportError:
            print("[X] requests не установлен")
            return 0

        synced = 0
        for op in operations:
            properties = {
                "Дата": {"date": {"start": op.get('date', '')}},
                "Контакт": {"title": [{"text": {"content": op.get('contact', '')}}]},
                "Сумма": {"number": op.get('amount', 0)},
                "Валюта": {"select": {"name": op.get('currency', 'RUB')}},
            }

            data = {
                "parent": {"database_id": database_id},
                "properties": properties
            }

            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=data
            )

            if response.status_code == 200:
                synced += 1

        return synced

    def create_page(self, title: str, content: str, parent_id: str = None) -> Optional[str]:
        """Создать страницу в Notion."""
        if not self.connect():
            return None

        try:
            import requests
        except ImportError:
            return None

        # Конвертируем Markdown в блоки Notion (упрощённо)
        blocks = []
        for line in content.split('\n'):
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"text": {"content": line[2:]}}]}
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"text": {"content": line[3:]}}]}
                })
            elif line.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": line}}]}
                })

        data = {
            "parent": {"page_id": parent_id} if parent_id else {"type": "page_id"},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            },
            "children": blocks[:100]  # Лимит Notion
        }

        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=data
        )

        if response.status_code == 200:
            return response.json().get('id')
        return None


# CLI для тестирования
if __name__ == "__main__":
    notion = NotionIntegration()
    if notion.connect():
        print("[OK] Подключено к Notion")
    else:
        print("Настройте NOTION_API_KEY")
