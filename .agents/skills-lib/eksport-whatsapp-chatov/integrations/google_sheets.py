#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интеграция с Google Sheets.
Экспорт операций и контактов в таблицы.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from config import check_api_key, get_api_key

class GoogleSheetsIntegration:
    """Интеграция с Google Sheets API."""

    def __init__(self):
        self.credentials_path = None
        self.service = None

    def connect(self) -> bool:
        """Подключиться к Google Sheets API."""
        if not check_api_key('google_sheets'):
            print("[X] GOOGLE_SHEETS_CREDENTIALS не настроен")
            print("   Укажите путь к credentials.json")
            return False

        self.credentials_path = get_api_key('google_sheets')

        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            self.service = build('sheets', 'v4', credentials=creds)
            return True

        except ImportError:
            print("[X] google-api-python-client не установлен")
            print("   pip install google-api-python-client google-auth")
            return False
        except Exception as e:
            print(f"[X] Ошибка подключения: {e}")
            return False

    def export_to_sheet(
        self,
        spreadsheet_id: str,
        data: List[List],
        sheet_name: str = "Sheet1",
        start_cell: str = "A1"
    ) -> bool:
        """
        Экспортировать данные в Google Sheet.

        Args:
            spreadsheet_id: ID таблицы
            data: Данные [[row1], [row2], ...]
            sheet_name: Имя листа
            start_cell: Начальная ячейка
        """
        if not self.service:
            if not self.connect():
                return False

        try:
            range_name = f"{sheet_name}!{start_cell}"
            body = {'values': data}

            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            return True
        except Exception as e:
            print(f"[X] Ошибка экспорта: {e}")
            return False

    def export_operations(
        self,
        operations: List[Dict],
        spreadsheet_id: str,
        sheet_name: str = "Операции"
    ) -> int:
        """Экспортировать операции в таблицу."""
        # Заголовки
        data = [["Дата", "Контакт", "Операция", "Сумма", "Валюта"]]

        # Данные
        for op in operations:
            data.append([
                op.get('date', ''),
                op.get('contact', ''),
                op.get('operation', ''),
                op.get('amount', 0),
                op.get('currency', 'RUB'),
            ])

        if self.export_to_sheet(spreadsheet_id, data, sheet_name):
            return len(operations)
        return 0

    def export_contacts(
        self,
        contacts: List[Dict],
        spreadsheet_id: str,
        sheet_name: str = "Контакты"
    ) -> int:
        """Экспортировать контакты в таблицу."""
        data = [["Имя", "Телефон", "Тип", "Тематика"]]

        for c in contacts:
            data.append([
                c.get('name', ''),
                c.get('phone', ''),
                c.get('type', ''),
                c.get('topic', ''),
            ])

        if self.export_to_sheet(spreadsheet_id, data, sheet_name):
            return len(contacts)
        return 0

    def create_spreadsheet(self, title: str) -> Optional[str]:
        """Создать новую таблицу."""
        if not self.service:
            if not self.connect():
                return None

        try:
            spreadsheet = self.service.spreadsheets().create(
                body={'properties': {'title': title}}
            ).execute()

            return spreadsheet.get('spreadsheetId')
        except Exception as e:
            print(f"[X] Ошибка создания: {e}")
            return None


if __name__ == "__main__":
    sheets = GoogleSheetsIntegration()
    if sheets.connect():
        print("[OK] Подключено к Google Sheets")
    else:
        print("Настройте GOOGLE_SHEETS_CREDENTIALS")
