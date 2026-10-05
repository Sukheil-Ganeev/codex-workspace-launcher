#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Синхронизация бронирований с Google Calendar.

Создаёт события из:
- operations.json (подтверждённые бронирования)
- travel_dates.json (прилёты/отлёты клиентов)
- contacts.json (информация о клиентах)

Использование:
    python google_calendar_sync.py --sync-all
    python google_calendar_sync.py --bookings
    python google_calendar_sync.py --travel
    python google_calendar_sync.py --sync-all --dry-run
    python google_calendar_sync.py --cleanup --days 60
    python google_calendar_sync.py --sync-all --calendar-id "xxx@group.calendar.google.com"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import JSON_DIR, check_api_key, get_api_key
except ImportError:
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")

    def check_api_key(service: str) -> bool:
        return bool(os.getenv(f'{service.upper()}_CREDENTIALS'))

    def get_api_key(service: str) -> str:
        key = os.getenv(f'{service.upper()}_CREDENTIALS', '')
        if not key:
            raise ValueError(f"API ключ для '{service}' не настроен")
        return key

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Пути к входным файлам
OPERATIONS_FILE = JSON_DIR / "operations.json"
TRAVEL_DATES_FILE = JSON_DIR / "travel_dates.json"
CONTACTS_FILE = JSON_DIR / "contacts.json"

# Переменные окружения для Google Calendar
# GOOGLE_CALENDAR_CREDENTIALS = путь к credentials.json (Service Account)
# GOOGLE_CALENDAR_ID = "primary" или "xxx@group.calendar.google.com"

DEFAULT_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
DEFAULT_TIMEZONE = 'Asia/Dubai'

# Цвета событий Google Calendar
# https://developers.google.com/calendar/api/v3/reference/colors/get
EVENT_COLORS = {
    "tour": "1",        # Lavender (лавандовый/синий)
    "transfer": "2",    # Sage (шалфей/зелёный)
    "yacht": "3",       # Grape (виноград/фиолетовый)
    "tickets": "5",     # Banana (банан/жёлтый)
    "exchange": "6",    # Tangerine (мандарин/оранжевый)
    "car_rental": "7",  # Peacock (павлин/бирюзовый)
    "catering": "8",    # Graphite (графит/серый)
    "other": "9",       # Blueberry (черника/синий)
    "arrival": "10",    # Basil (базилик/тёмно-зелёный)
    "departure": "11",  # Tomato (томат/красный)
}

# Эмодзи для названий событий
EVENT_EMOJI = {
    "tour": "🏜",
    "transfer": "🚗",
    "yacht": "⛵",
    "tickets": "🎟",
    "exchange": "💱",
    "car_rental": "🚙",
    "catering": "🍽",
    "other": "📋",
    "arrival": "✈️",
    "departure": "🛫",
}

# Статусы операций которые синхронизируем
SYNC_STATUSES = ['booked', 'confirmed', 'pending']

# ═══════════════════════════════════════════════════════════════
# GOOGLE CALENDAR API
# ═══════════════════════════════════════════════════════════════

class GoogleCalendarSync:
    """Класс для синхронизации с Google Calendar."""

    def __init__(self, calendar_id: str = None, dry_run: bool = False):
        """
        Инициализация.

        Args:
            calendar_id: ID календаря (по умолчанию из переменной окружения)
            dry_run: Режим тестирования без создания событий
        """
        self.calendar_id = calendar_id or DEFAULT_CALENDAR_ID
        self.dry_run = dry_run
        self.service = None
        self.contacts_map: Dict[str, dict] = {}

        # Загрузка контактов для обогащения данных
        self._load_contacts()

    def _load_contacts(self):
        """Загрузить контакты для обогащения данных."""
        if CONTACTS_FILE.exists():
            try:
                with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
                    contacts = json.load(f)
                    for c in contacts:
                        phone = c.get('phone', '')
                        if phone:
                            self.contacts_map[phone] = c
                        jid = c.get('jid', '')
                        if jid:
                            self.contacts_map[jid] = c
                print(f"[OK] Загружено контактов: {len(self.contacts_map)}")
            except Exception as e:
                print(f"[!] Ошибка загрузки контактов: {e}")

    def connect(self) -> bool:
        """
        Подключиться к Google Calendar API.

        Returns:
            True если подключение успешно
        """
        if self.dry_run:
            print("[DRY-RUN] Пропускаю подключение к API")
            return True

        # Проверяем наличие credentials
        credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS', '')

        if not credentials_path:
            print("[X] GOOGLE_CALENDAR_CREDENTIALS не установлен")
            print("    Установите путь к credentials.json:")
            print("    set GOOGLE_CALENDAR_CREDENTIALS=C:/path/to/credentials.json")
            return False

        if not Path(credentials_path).exists():
            print(f"[X] Файл credentials не найден: {credentials_path}")
            return False

        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/calendar']

            creds = Credentials.from_service_account_file(
                credentials_path,
                scopes=SCOPES
            )

            self.service = build('calendar', 'v3', credentials=creds)

            # Проверка доступа к календарю
            calendar = self.service.calendars().get(
                calendarId=self.calendar_id
            ).execute()

            print(f"[OK] Подключено к календарю: {calendar.get('summary', self.calendar_id)}")
            return True

        except ImportError:
            print("[X] Не установлены зависимости Google API")
            print("    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False
        except Exception as e:
            print(f"[X] Ошибка подключения: {e}")
            return False

    def get_contact_info(self, phone: str = None, jid: str = None) -> Tuple[str, str]:
        """
        Получить имя и телефон контакта.

        Returns:
            (name, phone)
        """
        contact = None

        if phone and phone in self.contacts_map:
            contact = self.contacts_map[phone]
        elif jid and jid in self.contacts_map:
            contact = self.contacts_map[jid]

        if contact:
            name = contact.get('name', 'Неизвестный')
            phone_num = contact.get('phone', phone or '')
            return name, phone_num

        return 'Неизвестный', phone or ''

    def find_existing_event(
        self,
        title_prefix: str,
        event_date: str,
        time_min: datetime = None,
        time_max: datetime = None
    ) -> Optional[str]:
        """
        Найти существующее событие по названию и дате.

        Args:
            title_prefix: Начало названия события
            event_date: Дата события (YYYY-MM-DD)
            time_min: Начало периода поиска
            time_max: Конец периода поиска

        Returns:
            ID события или None
        """
        if self.dry_run or not self.service:
            return None

        try:
            # Определяем диапазон поиска
            if not time_min:
                dt = datetime.strptime(event_date, '%Y-%m-%d')
                time_min = dt.replace(hour=0, minute=0, second=0)
            if not time_max:
                time_max = time_min + timedelta(days=1)

            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                maxResults=100
            ).execute()

            events = events_result.get('items', [])

            for event in events:
                summary = event.get('summary', '')
                if summary.startswith(title_prefix):
                    return event.get('id')

            return None

        except Exception as e:
            print(f"  [!] Ошибка поиска события: {e}")
            return None

    def create_event(
        self,
        title: str,
        date: str,
        time: str = "10:00",
        duration_hours: float = 2,
        description: str = "",
        location: str = "",
        color_id: str = None,
        all_day: bool = False
    ) -> Optional[str]:
        """
        Создать событие в календаре.

        Args:
            title: Название события
            date: Дата (YYYY-MM-DD)
            time: Время начала (HH:MM)
            duration_hours: Длительность в часах
            description: Описание
            location: Место
            color_id: ID цвета (1-11)
            all_day: Событие на весь день

        Returns:
            ID созданного события или None
        """
        if self.dry_run:
            print(f"  [DRY-RUN] Создание: {title} | {date} {time}")
            return "dry-run-id"

        if not self.service:
            print("[X] Не подключено к API")
            return None

        try:
            # Парсим дату и время
            dt = datetime.strptime(date, '%Y-%m-%d')

            if all_day:
                # Событие на весь день
                event = {
                    'summary': title,
                    'description': description,
                    'location': location,
                    'start': {
                        'date': date,
                        'timeZone': DEFAULT_TIMEZONE,
                    },
                    'end': {
                        'date': date,
                        'timeZone': DEFAULT_TIMEZONE,
                    },
                }
            else:
                # Событие с временем
                hour, minute = map(int, time.split(':'))
                start_dt = dt.replace(hour=hour, minute=minute)
                end_dt = start_dt + timedelta(hours=duration_hours)

                event = {
                    'summary': title,
                    'description': description,
                    'location': location,
                    'start': {
                        'dateTime': start_dt.isoformat(),
                        'timeZone': DEFAULT_TIMEZONE,
                    },
                    'end': {
                        'dateTime': end_dt.isoformat(),
                        'timeZone': DEFAULT_TIMEZONE,
                    },
                }

            # Цвет события
            if color_id:
                event['colorId'] = color_id

            # Напоминания
            event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},  # За 1 день
                    {'method': 'popup', 'minutes': 2 * 60},   # За 2 часа
                ],
            }

            result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            return result.get('id')

        except Exception as e:
            print(f"  [X] Ошибка создания события: {e}")
            return None

    def update_event(
        self,
        event_id: str,
        title: str = None,
        description: str = None,
        color_id: str = None
    ) -> bool:
        """
        Обновить существующее событие.

        Returns:
            True если обновление успешно
        """
        if self.dry_run:
            print(f"  [DRY-RUN] Обновление: {event_id}")
            return True

        if not self.service:
            return False

        try:
            # Получаем текущее событие
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            # Обновляем поля
            if title:
                event['summary'] = title
            if description:
                event['description'] = description
            if color_id:
                event['colorId'] = color_id

            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            return True

        except Exception as e:
            print(f"  [X] Ошибка обновления: {e}")
            return False

    def delete_event(self, event_id: str) -> bool:
        """Удалить событие."""
        if self.dry_run:
            print(f"  [DRY-RUN] Удаление: {event_id}")
            return True

        if not self.service:
            return False

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"  [X] Ошибка удаления: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════
    # СИНХРОНИЗАЦИЯ БРОНИРОВАНИЙ
    # ═══════════════════════════════════════════════════════════════

    def sync_bookings(self) -> Tuple[int, int, int]:
        """
        Синхронизировать бронирования из operations.json.

        Returns:
            (created, updated, skipped)
        """
        print("\n" + "=" * 60)
        print("СИНХРОНИЗАЦИЯ БРОНИРОВАНИЙ")
        print("=" * 60)

        if not OPERATIONS_FILE.exists():
            print(f"[!] Файл не найден: {OPERATIONS_FILE}")
            return 0, 0, 0

        # Загружаем операции
        with open(OPERATIONS_FILE, 'r', encoding='utf-8') as f:
            operations = json.load(f)

        print(f"Загружено операций: {len(operations)}")

        created = 0
        updated = 0
        skipped = 0

        for op in operations:
            # Фильтр по статусу
            status = op.get('status', '')
            if status not in SYNC_STATUSES:
                skipped += 1
                continue

            # Данные операции
            op_type = op.get('type', 'other')
            date = op.get('date', '')
            description = op.get('description', '')
            amount = op.get('amount', 0)
            currency = op.get('currency', 'AED')
            notes = op.get('notes', '')
            phone = op.get('phone', '')

            if not date:
                skipped += 1
                continue

            # Получаем информацию о клиенте
            client_name, client_phone = self.get_contact_info(phone=phone)

            # Формируем название события
            emoji = EVENT_EMOJI.get(op_type, '📋')
            type_name = {
                'tour': 'Экскурсия',
                'transfer': 'Трансфер',
                'yacht': 'Яхта',
                'tickets': 'Билеты',
                'exchange': 'Обмен',
                'car_rental': 'Аренда авто',
                'catering': 'Кейтеринг',
            }.get(op_type, 'Услуга')

            title = f"{emoji} {type_name} - {client_name}"

            # Описание
            desc_parts = [description]
            if notes:
                desc_parts.append(f"Заметки: {notes}")
            if amount:
                desc_parts.append(f"Сумма: {amount} {currency}")
            if client_phone:
                desc_parts.append(f"Телефон: {client_phone}")
            desc_parts.append(f"Статус: {status}")

            full_description = "\n".join(desc_parts)

            # Цвет события
            color_id = EVENT_COLORS.get(op_type, '9')

            # Проверяем существование события
            title_prefix = f"{emoji} {type_name}"
            existing_id = self.find_existing_event(title_prefix, date)

            if existing_id:
                # Обновляем существующее
                if self.update_event(existing_id, title, full_description, color_id):
                    updated += 1
                    print(f"  [~] Обновлено: {title} | {date}")
                else:
                    skipped += 1
            else:
                # Создаём новое
                event_id = self.create_event(
                    title=title,
                    date=date,
                    time="10:00",
                    duration_hours=3,
                    description=full_description,
                    color_id=color_id
                )

                if event_id:
                    created += 1
                    print(f"  [+] Создано: {title} | {date}")
                else:
                    skipped += 1

        print(f"\nИтого: создано {created}, обновлено {updated}, пропущено {skipped}")
        return created, updated, skipped

    # ═══════════════════════════════════════════════════════════════
    # СИНХРОНИЗАЦИЯ ПРИЛЁТОВ/ОТЛЁТОВ
    # ═══════════════════════════════════════════════════════════════

    def sync_arrivals(self) -> Tuple[int, int, int]:
        """
        Синхронизировать прилёты из travel_dates.json.

        Returns:
            (created, updated, skipped)
        """
        print("\n" + "=" * 60)
        print("СИНХРОНИЗАЦИЯ ПРИЛЁТОВ")
        print("=" * 60)

        if not TRAVEL_DATES_FILE.exists():
            print(f"[!] Файл не найден: {TRAVEL_DATES_FILE}")
            print("    Запустите extract_travel_dates.py для создания файла")
            return 0, 0, 0

        # Загружаем данные
        with open(TRAVEL_DATES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        travel_dates = data.get('travel_dates', [])
        print(f"Загружено записей: {len(travel_dates)}")

        created = 0
        updated = 0
        skipped = 0

        # Фильтруем только будущие даты
        today = datetime.now().strftime('%Y-%m-%d')

        for record in travel_dates:
            arrival_date = record.get('arrival_date')

            if not arrival_date or arrival_date < today:
                skipped += 1
                continue

            # Данные
            jid = record.get('jid', '')
            chat_name = record.get('chat_name', 'Неизвестный')
            pax = record.get('pax')
            pax_details = record.get('pax_details', '')
            hotel = record.get('hotel', '')

            # Получаем информацию о контакте
            client_name, client_phone = self.get_contact_info(jid=jid)
            if client_name == 'Неизвестный' and chat_name:
                client_name = chat_name

            # Формируем название
            emoji = EVENT_EMOJI['arrival']
            pax_str = f" ({pax} чел)" if pax else ""
            hotel_str = f" ({hotel})" if hotel else ""

            title = f"{emoji} Прилёт - {client_name}{pax_str}{hotel_str}"

            # Описание
            desc_parts = []
            if pax:
                desc_parts.append(f"Количество: {pax} чел.")
            if pax_details:
                desc_parts.append(f"Состав: {pax_details}")
            if hotel:
                desc_parts.append(f"Отель: {hotel}")
            if client_phone:
                desc_parts.append(f"Телефон: {client_phone}")

            departure_date = record.get('departure_date')
            if departure_date:
                duration = record.get('duration_days')
                desc_parts.append(f"Отлёт: {departure_date} ({duration} дней)")

            full_description = "\n".join(desc_parts)

            # Проверяем существование
            title_prefix = f"{emoji} Прилёт - {client_name}"
            existing_id = self.find_existing_event(title_prefix, arrival_date)

            if existing_id:
                if self.update_event(existing_id, title, full_description, EVENT_COLORS['arrival']):
                    updated += 1
                    print(f"  [~] Обновлено: {title} | {arrival_date}")
                else:
                    skipped += 1
            else:
                event_id = self.create_event(
                    title=title,
                    date=arrival_date,
                    time="12:00",
                    duration_hours=1,
                    description=full_description,
                    color_id=EVENT_COLORS['arrival'],
                    all_day=True
                )

                if event_id:
                    created += 1
                    print(f"  [+] Создано: {title} | {arrival_date}")
                else:
                    skipped += 1

        print(f"\nИтого: создано {created}, обновлено {updated}, пропущено {skipped}")
        return created, updated, skipped

    def sync_departures(self) -> Tuple[int, int, int]:
        """
        Синхронизировать отлёты из travel_dates.json.

        Returns:
            (created, updated, skipped)
        """
        print("\n" + "=" * 60)
        print("СИНХРОНИЗАЦИЯ ОТЛЁТОВ")
        print("=" * 60)

        if not TRAVEL_DATES_FILE.exists():
            print(f"[!] Файл не найден: {TRAVEL_DATES_FILE}")
            return 0, 0, 0

        # Загружаем данные
        with open(TRAVEL_DATES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        travel_dates = data.get('travel_dates', [])
        print(f"Загружено записей: {len(travel_dates)}")

        created = 0
        updated = 0
        skipped = 0

        today = datetime.now().strftime('%Y-%m-%d')

        for record in travel_dates:
            departure_date = record.get('departure_date')

            if not departure_date or departure_date < today:
                skipped += 1
                continue

            # Данные
            jid = record.get('jid', '')
            chat_name = record.get('chat_name', 'Неизвестный')
            pax = record.get('pax')
            hotel = record.get('hotel', '')

            # Получаем информацию о контакте
            client_name, client_phone = self.get_contact_info(jid=jid)
            if client_name == 'Неизвестный' and chat_name:
                client_name = chat_name

            # Формируем название
            emoji = EVENT_EMOJI['departure']
            pax_str = f" ({pax} чел)" if pax else ""

            title = f"{emoji} Отлёт - {client_name}{pax_str}"

            # Описание
            desc_parts = []
            if pax:
                desc_parts.append(f"Количество: {pax} чел.")
            if hotel:
                desc_parts.append(f"Отель: {hotel}")
            if client_phone:
                desc_parts.append(f"Телефон: {client_phone}")

            arrival_date = record.get('arrival_date')
            if arrival_date:
                duration = record.get('duration_days')
                desc_parts.append(f"Прилёт был: {arrival_date} ({duration} дней)")

            full_description = "\n".join(desc_parts)

            # Проверяем существование
            title_prefix = f"{emoji} Отлёт - {client_name}"
            existing_id = self.find_existing_event(title_prefix, departure_date)

            if existing_id:
                if self.update_event(existing_id, title, full_description, EVENT_COLORS['departure']):
                    updated += 1
                    print(f"  [~] Обновлено: {title} | {departure_date}")
                else:
                    skipped += 1
            else:
                event_id = self.create_event(
                    title=title,
                    date=departure_date,
                    time="10:00",
                    duration_hours=1,
                    description=full_description,
                    color_id=EVENT_COLORS['departure'],
                    all_day=True
                )

                if event_id:
                    created += 1
                    print(f"  [+] Создано: {title} | {departure_date}")
                else:
                    skipped += 1

        print(f"\nИтого: создано {created}, обновлено {updated}, пропущено {skipped}")
        return created, updated, skipped

    # ═══════════════════════════════════════════════════════════════
    # ОЧИСТКА СТАРЫХ СОБЫТИЙ
    # ═══════════════════════════════════════════════════════════════

    def delete_past_events(self, days: int = 30) -> int:
        """
        Удалить события старше указанного количества дней.

        Args:
            days: Количество дней (события старше этого срока будут удалены)

        Returns:
            Количество удалённых событий
        """
        print("\n" + "=" * 60)
        print(f"ОЧИСТКА СОБЫТИЙ СТАРШЕ {days} ДНЕЙ")
        print("=" * 60)

        if self.dry_run:
            print("[DRY-RUN] Режим тестирования")

        if not self.service and not self.dry_run:
            print("[X] Не подключено к API")
            return 0

        # Определяем диапазон дат
        cutoff_date = datetime.now() - timedelta(days=days)
        time_min = (cutoff_date - timedelta(days=365)).isoformat() + 'Z'  # За год назад
        time_max = cutoff_date.isoformat() + 'Z'

        deleted = 0

        try:
            if self.dry_run:
                print(f"  Поиск событий до {cutoff_date.strftime('%Y-%m-%d')}...")
                print("  [DRY-RUN] События будут найдены и удалены в реальном режиме")
                return 0

            # Получаем события
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                maxResults=500
            ).execute()

            events = events_result.get('items', [])
            print(f"Найдено событий: {len(events)}")

            # Фильтруем наши события (по эмодзи в названии)
            our_emoji = set(EVENT_EMOJI.values())

            for event in events:
                summary = event.get('summary', '')

                # Проверяем, что это наше событие
                if any(summary.startswith(emoji) for emoji in our_emoji):
                    event_id = event.get('id')
                    if self.delete_event(event_id):
                        deleted += 1
                        print(f"  [-] Удалено: {summary}")

            print(f"\nИтого удалено: {deleted}")
            return deleted

        except Exception as e:
            print(f"[X] Ошибка: {e}")
            return deleted

    # ═══════════════════════════════════════════════════════════════
    # ГЛАВНЫЕ МЕТОДЫ
    # ═══════════════════════════════════════════════════════════════

    def sync_all(self) -> dict:
        """
        Синхронизировать всё: бронирования, прилёты, отлёты.

        Returns:
            Статистика синхронизации
        """
        stats = {
            'bookings': {'created': 0, 'updated': 0, 'skipped': 0},
            'arrivals': {'created': 0, 'updated': 0, 'skipped': 0},
            'departures': {'created': 0, 'updated': 0, 'skipped': 0},
        }

        # Бронирования
        c, u, s = self.sync_bookings()
        stats['bookings'] = {'created': c, 'updated': u, 'skipped': s}

        # Прилёты
        c, u, s = self.sync_arrivals()
        stats['arrivals'] = {'created': c, 'updated': u, 'skipped': s}

        # Отлёты
        c, u, s = self.sync_departures()
        stats['departures'] = {'created': c, 'updated': u, 'skipped': s}

        # Итоговая статистика
        print("\n" + "=" * 60)
        print("ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 60)

        total_created = sum(s['created'] for s in stats.values())
        total_updated = sum(s['updated'] for s in stats.values())
        total_skipped = sum(s['skipped'] for s in stats.values())

        print(f"Бронирования: +{stats['bookings']['created']} ~{stats['bookings']['updated']}")
        print(f"Прилёты:      +{stats['arrivals']['created']} ~{stats['arrivals']['updated']}")
        print(f"Отлёты:       +{stats['departures']['created']} ~{stats['departures']['updated']}")
        print("-" * 40)
        print(f"ВСЕГО:        +{total_created} создано, ~{total_updated} обновлено, {total_skipped} пропущено")

        return stats


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Синхронизация бронирований с Google Calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python google_calendar_sync.py --sync-all
  python google_calendar_sync.py --bookings
  python google_calendar_sync.py --travel
  python google_calendar_sync.py --sync-all --dry-run
  python google_calendar_sync.py --cleanup --days 60
  python google_calendar_sync.py --sync-all --calendar-id "xxx@group.calendar.google.com"

Настройка:
  1. Создайте Service Account в Google Cloud Console
  2. Включите Google Calendar API
  3. Скачайте credentials.json
  4. Установите переменные окружения:
     set GOOGLE_CALENDAR_CREDENTIALS=C:/path/to/credentials.json
     set GOOGLE_CALENDAR_ID=primary (или ID календаря)
  5. Дайте Service Account доступ к календарю (поделитесь календарём)
        """
    )

    # Режимы синхронизации
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--sync-all', '-a',
        action='store_true',
        help='Синхронизировать всё (бронирования + прилёты/отлёты)'
    )
    mode_group.add_argument(
        '--bookings', '-b',
        action='store_true',
        help='Только бронирования из operations.json'
    )
    mode_group.add_argument(
        '--travel', '-t',
        action='store_true',
        help='Только прилёты/отлёты из travel_dates.json'
    )
    mode_group.add_argument(
        '--arrivals',
        action='store_true',
        help='Только прилёты'
    )
    mode_group.add_argument(
        '--departures',
        action='store_true',
        help='Только отлёты'
    )
    mode_group.add_argument(
        '--cleanup', '-c',
        action='store_true',
        help='Удалить старые события'
    )

    # Опции
    parser.add_argument(
        '--calendar-id',
        type=str,
        default=None,
        help='ID календаря (по умолчанию из GOOGLE_CALENDAR_ID)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Режим тестирования (без создания событий)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Для --cleanup: удалить события старше N дней (по умолчанию 30)'
    )

    args = parser.parse_args()

    # Если ничего не указано - показываем справку
    if not any([args.sync_all, args.bookings, args.travel,
                args.arrivals, args.departures, args.cleanup]):
        parser.print_help()
        return

    print("=" * 60)
    print("GOOGLE CALENDAR SYNC")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.dry_run:
        print("[DRY-RUN] Режим тестирования - события НЕ будут созданы")

    # Создаём синхронизатор
    sync = GoogleCalendarSync(
        calendar_id=args.calendar_id,
        dry_run=args.dry_run
    )

    # Подключаемся к API
    if not sync.connect():
        print("\n[X] Не удалось подключиться к Google Calendar")
        sys.exit(1)

    # Выполняем действие
    if args.sync_all:
        sync.sync_all()
    elif args.bookings:
        sync.sync_bookings()
    elif args.travel:
        sync.sync_arrivals()
        sync.sync_departures()
    elif args.arrivals:
        sync.sync_arrivals()
    elif args.departures:
        sync.sync_departures()
    elif args.cleanup:
        sync.delete_past_events(days=args.days)

    print("\n[OK] Готово!")


if __name__ == "__main__":
    main()
