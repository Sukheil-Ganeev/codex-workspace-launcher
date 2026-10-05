#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интеграция с Google Calendar.
Создание событий из чатов.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from config import check_api_key, get_api_key

class CalendarIntegration:
    """Интеграция с Google Calendar API."""

    def __init__(self):
        self.credentials_path = None
        self.service = None
        self.calendar_id = 'primary'

    def connect(self) -> bool:
        """Подключиться к Google Calendar API."""
        if not check_api_key('google_calendar'):
            print("[X] GOOGLE_CALENDAR_CREDENTIALS не настроен")
            return False

        self.credentials_path = get_api_key('google_calendar')

        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            self.service = build('calendar', 'v3', credentials=creds)
            return True

        except ImportError:
            print("[X] google-api-python-client не установлен")
            return False
        except Exception as e:
            print(f"[X] Ошибка: {e}")
            return False

    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime = None,
        description: str = "",
        location: str = ""
    ) -> Optional[str]:
        """
        Создать событие в календаре.

        Returns:
            ID события или None
        """
        if not self.service:
            if not self.connect():
                return None

        if end_time is None:
            end_time = start_time + timedelta(hours=1)

        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Dubai',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Dubai',
            },
        }

        try:
            result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            return result.get('id')
        except Exception as e:
            print(f"[X] Ошибка создания события: {e}")
            return None

    def create_events_from_chat(self, events_data: List[Dict]) -> int:
        """
        Создать события из данных чата.

        Args:
            events_data: [{title, date, time, description}]
        """
        created = 0

        for event in events_data:
            try:
                date_str = event.get('date', '')
                time_str = event.get('time', '10:00')

                # Парсим дату
                if '.' in date_str:
                    date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                else:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

                # Добавляем время
                hour, minute = map(int, time_str.split(':'))
                start_time = date_obj.replace(hour=hour, minute=minute)

                event_id = self.create_event(
                    title=event.get('title', 'Событие из чата'),
                    start_time=start_time,
                    description=event.get('description', ''),
                    location=event.get('location', '')
                )

                if event_id:
                    created += 1

            except (ValueError, KeyError) as e:
                print(f"  [!] Пропущено событие: {e}")

        return created

    def create_reminder(
        self,
        title: str,
        date: datetime,
        contact_name: str = ""
    ) -> Optional[str]:
        """Создать напоминание."""
        description = f"Напоминание из чата с {contact_name}" if contact_name else ""
        return self.create_event(
            title=f"⏰ {title}",
            start_time=date,
            description=description
        )


if __name__ == "__main__":
    cal = CalendarIntegration()
    if cal.connect():
        print("[OK] Подключено к Google Calendar")
    else:
        print("Настройте GOOGLE_CALENDAR_CREDENTIALS")
