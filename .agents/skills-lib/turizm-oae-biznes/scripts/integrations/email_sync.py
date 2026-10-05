#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Синхронизация email переписки (Gmail/Outlook).

Функции:
- Gmail интеграция через OAuth2
- Outlook интеграция через Microsoft Graph API
- Парсинг email в структурированные данные
- Извлечение вложений и бронирований
- Синхронизация с Bitrix24
- Дедупликация с WhatsApp

Использование:
    python email_sync.py --gmail --days 30
    python email_sync.py --outlook --days 30
    python email_sync.py --sync-all
    python email_sync.py --gmail --search "from:booking@example.com"
    python email_sync.py --extract-bookings
    python email_sync.py --link-contacts
    python email_sync.py --dry-run
"""

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime, timedelta
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import (
        JSON_DIR, BASE_DIR, CHATS_DIR,
        BITRIX24_CONFIG, PATTERNS
    )
except ImportError:
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    BASE_DIR = Path("D:/Downloads/Chats/_база")
    CHATS_DIR = Path("D:/Downloads/Chats")
    BITRIX24_CONFIG = {}
    PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    }

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Пути к выходным файлам
EMAIL_DIR = BASE_DIR / "email"
EMAILS_FILE = EMAIL_DIR / "emails.jsonl"
EMAIL_CONTACTS_FILE = EMAIL_DIR / "email_contacts.json"
ATTACHMENTS_DIR = EMAIL_DIR / "email_attachments"
SYNC_STATE_FILE = EMAIL_DIR / ".sync_state.json"

# Пути для интеграции
CONTACTS_FILE = JSON_DIR / "contacts.json"
OPERATIONS_FILE = JSON_DIR / "operations.json"

# Переменные окружения
GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', '')
GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', str(EMAIL_DIR / 'gmail_token.json'))

OUTLOOK_CLIENT_ID = os.getenv('OUTLOOK_CLIENT_ID', '')
OUTLOOK_CLIENT_SECRET = os.getenv('OUTLOOK_CLIENT_SECRET', '')
OUTLOOK_TENANT_ID = os.getenv('OUTLOOK_TENANT_ID', 'common')
OUTLOOK_TOKEN_FILE = os.getenv('OUTLOOK_TOKEN_FILE', str(EMAIL_DIR / 'outlook_token.json'))

# Период синхронизации
EMAIL_SYNC_DAYS = int(os.getenv('EMAIL_SYNC_DAYS', '365'))

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
]

# Microsoft Graph API scopes
OUTLOOK_SCOPES = [
    'https://graph.microsoft.com/Mail.Read',
    'https://graph.microsoft.com/User.Read',
]

# Метки Gmail для синхронизации
GMAIL_LABELS_SYNC = ['INBOX', 'SENT', 'IMPORTANT']

# Паттерны для извлечения бронирований
BOOKING_PATTERNS = {
    'confirmation_number': [
        r'(?:confirmation|booking|reference|order)\s*(?:number|#|no\.?|id)?[:\s]*([A-Z0-9]{6,20})',
        r'(?:номер\s+(?:брони|заказа|бронирования))[:\s]*([A-Z0-9]{6,20})',
        r'Ref[:\s]*([A-Z0-9]{6,20})',
    ],
    'date': [
        r'(?:date|дата)[:\s]*(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
    ],
    'time': [
        r'(?:time|время|pickup)[:\s]*(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
        r'at\s+(\d{1,2}:\d{2})',
    ],
    'amount': [
        r'(?:total|amount|сумма|итого)[:\s]*(?:AED|USD|EUR|RUB|₽|\$|€)?\s*([\d,\.]+)',
        r'([\d,\.]+)\s*(?:AED|USD|EUR|RUB|дирхам|рубл)',
    ],
    'hotel': [
        r'(?:hotel|отель)[:\s]*([A-Za-zА-Яа-я\s]{3,50})',
        r'(?:pick\s*up\s*(?:from|at)|встреча)[:\s]*([A-Za-zА-Яа-я\s]{3,50})',
    ],
    'guests': [
        r'(?:guests?|pax|чел|человек|гостей)[:\s]*(\d+)',
        r'(\d+)\s*(?:adults?|взросл)',
        r'(\d+)\s*(?:children?|детей|ребён)',
    ],
}

# Известные отправители бронирований
BOOKING_SENDERS = [
    'viator.com',
    'getyourguide.com',
    'booking.com',
    'expedia.com',
    'klook.com',
    'tiqets.com',
    'headout.com',
    'civitatis.com',
    'musement.com',
]


# ═══════════════════════════════════════════════════════════════
# GMAIL ИНТЕГРАЦИЯ
# ═══════════════════════════════════════════════════════════════

class GmailClient:
    """Клиент для работы с Gmail API."""

    def __init__(self, dry_run: bool = False):
        """
        Инициализация Gmail клиента.

        Args:
            dry_run: Режим тестирования без записи
        """
        self.dry_run = dry_run
        self.service = None
        self.user_email = None

    def authenticate(self) -> bool:
        """
        Аутентификация через OAuth2.

        Returns:
            True если аутентификация успешна
        """
        if not GMAIL_CREDENTIALS_FILE:
            print("[X] GMAIL_CREDENTIALS_FILE не установлен")
            print("    Установите путь к credentials.json:")
            print("    set GMAIL_CREDENTIALS_FILE=C:/path/to/credentials.json")
            return False

        if not Path(GMAIL_CREDENTIALS_FILE).exists():
            print(f"[X] Файл credentials не найден: {GMAIL_CREDENTIALS_FILE}")
            return False

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = None
            token_path = Path(GMAIL_TOKEN_FILE)

            # Проверяем существующий токен
            if token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(
                        str(token_path), GMAIL_SCOPES
                    )
                except Exception as e:
                    print(f"[!] Ошибка загрузки токена: {e}")

            # Если токен недействителен - обновляем или запрашиваем новый
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("[~] Обновление токена...")
                    creds.refresh(Request())
                else:
                    print("[~] Запуск OAuth2 авторизации...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Сохраняем токен
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                print(f"[OK] Токен сохранён: {token_path}")

            # Создаём сервис
            self.service = build('gmail', 'v1', credentials=creds)

            # Получаем email пользователя
            profile = self.service.users().getProfile(userId='me').execute()
            self.user_email = profile.get('emailAddress', '')

            print(f"[OK] Подключено к Gmail: {self.user_email}")
            return True

        except ImportError:
            print("[X] Не установлены зависимости Google API")
            print("    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False
        except Exception as e:
            print(f"[X] Ошибка аутентификации: {e}")
            return False

    def get_labels(self) -> List[dict]:
        """Получить список меток Gmail."""
        if not self.service:
            return []

        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except Exception as e:
            print(f"[X] Ошибка получения меток: {e}")
            return []

    def search_messages(
        self,
        query: str = '',
        label_ids: List[str] = None,
        max_results: int = 500,
        after_date: datetime = None
    ) -> List[dict]:
        """
        Поиск писем.

        Args:
            query: Поисковый запрос Gmail
            label_ids: Список меток для фильтрации
            max_results: Максимальное количество результатов
            after_date: Дата начала поиска

        Returns:
            Список сообщений (id, threadId)
        """
        if not self.service:
            return []

        # Добавляем фильтр по дате
        if after_date:
            date_str = after_date.strftime('%Y/%m/%d')
            query = f"after:{date_str} {query}".strip()

        print(f"[~] Поиск: {query or '(все письма)'}")

        messages = []
        page_token = None

        try:
            while True:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    labelIds=label_ids,
                    maxResults=min(max_results - len(messages), 100),
                    pageToken=page_token
                ).execute()

                batch = results.get('messages', [])
                messages.extend(batch)

                if len(messages) >= max_results:
                    break

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            print(f"[OK] Найдено писем: {len(messages)}")
            return messages

        except Exception as e:
            print(f"[X] Ошибка поиска: {e}")
            return messages

    def get_message(self, message_id: str, format: str = 'full') -> Optional[dict]:
        """
        Получить содержимое письма.

        Args:
            message_id: ID сообщения
            format: Формат (minimal, full, raw, metadata)

        Returns:
            Данные сообщения
        """
        if not self.service:
            return None

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            ).execute()
            return message
        except Exception as e:
            print(f"  [!] Ошибка получения письма {message_id}: {e}")
            return None

    def get_attachment(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """
        Получить содержимое вложения.

        Args:
            message_id: ID сообщения
            attachment_id: ID вложения

        Returns:
            Байты вложения
        """
        if not self.service:
            return None

        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            data = attachment.get('data', '')
            return base64.urlsafe_b64decode(data)

        except Exception as e:
            print(f"  [!] Ошибка получения вложения: {e}")
            return None

    def parse_message(self, message: dict) -> dict:
        """
        Распарсить сообщение в структурированные данные.

        Args:
            message: Данные сообщения от API

        Returns:
            Структурированные данные письма
        """
        headers = {}
        payload = message.get('payload', {})

        # Парсим заголовки
        for header in payload.get('headers', []):
            name = header.get('name', '').lower()
            value = header.get('value', '')
            headers[name] = value

        # Получаем тело письма
        body_text = ''
        body_html = ''
        attachments = []

        def extract_parts(part):
            nonlocal body_text, body_html, attachments

            mime_type = part.get('mimeType', '')
            body = part.get('body', {})

            if mime_type == 'text/plain':
                data = body.get('data', '')
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            elif mime_type == 'text/html':
                data = body.get('data', '')
                if data:
                    body_html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            elif body.get('attachmentId'):
                attachments.append({
                    'id': body.get('attachmentId'),
                    'filename': part.get('filename', 'attachment'),
                    'mime_type': mime_type,
                    'size': body.get('size', 0)
                })

            # Рекурсивно обрабатываем части
            for sub_part in part.get('parts', []):
                extract_parts(sub_part)

        extract_parts(payload)

        # Парсим даты
        date_str = headers.get('date', '')
        try:
            date_parsed = parsedate_to_datetime(date_str)
            date_iso = date_parsed.isoformat()
        except Exception:
            date_iso = ''
            date_parsed = None

        # Парсим отправителя/получателя
        from_name, from_email = parseaddr(headers.get('from', ''))
        to_name, to_email = parseaddr(headers.get('to', ''))

        # Определяем направление
        is_incoming = self.user_email and to_email.lower() == self.user_email.lower()
        is_outgoing = self.user_email and from_email.lower() == self.user_email.lower()

        # Формируем результат
        result = {
            'id': message.get('id', ''),
            'thread_id': message.get('threadId', ''),
            'date': date_iso,
            'date_str': date_str,
            'subject': headers.get('subject', ''),
            'from_name': from_name,
            'from_email': from_email,
            'to_name': to_name,
            'to_email': to_email,
            'direction': 'incoming' if is_incoming else ('outgoing' if is_outgoing else 'unknown'),
            'body_text': body_text,
            'body_html': body_html,
            'body_preview': body_text[:500] if body_text else '',
            'attachments': attachments,
            'labels': message.get('labelIds', []),
            'snippet': message.get('snippet', ''),
            'source': 'gmail',
            'synced_at': datetime.now().isoformat()
        }

        return result


# ═══════════════════════════════════════════════════════════════
# OUTLOOK ИНТЕГРАЦИЯ
# ═══════════════════════════════════════════════════════════════

class OutlookClient:
    """Клиент для работы с Microsoft Graph API (Outlook)."""

    def __init__(self, dry_run: bool = False):
        """
        Инициализация Outlook клиента.

        Args:
            dry_run: Режим тестирования без записи
        """
        self.dry_run = dry_run
        self.access_token = None
        self.user_email = None

    def authenticate(self) -> bool:
        """
        Аутентификация через OAuth2.

        Returns:
            True если аутентификация успешна
        """
        if not OUTLOOK_CLIENT_ID:
            print("[X] OUTLOOK_CLIENT_ID не установлен")
            print("    Установите переменные окружения:")
            print("    set OUTLOOK_CLIENT_ID=your-client-id")
            print("    set OUTLOOK_CLIENT_SECRET=your-client-secret")
            return False

        try:
            import msal

            # Конфигурация приложения
            authority = f"https://login.microsoftonline.com/{OUTLOOK_TENANT_ID}"

            app = msal.ConfidentialClientApplication(
                OUTLOOK_CLIENT_ID,
                authority=authority,
                client_credential=OUTLOOK_CLIENT_SECRET,
            )

            # Пробуем получить токен из кэша
            token_path = Path(OUTLOOK_TOKEN_FILE)
            accounts = []

            if token_path.exists():
                try:
                    with open(token_path, 'r') as f:
                        token_cache = json.load(f)
                        # Восстанавливаем кэш
                        pass  # MSAL управляет кэшем сам
                except Exception:
                    pass

            # Если нет кэша - запрашиваем токен
            result = app.acquire_token_for_client(scopes=OUTLOOK_SCOPES)

            if 'access_token' in result:
                self.access_token = result['access_token']

                # Сохраняем токен
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, 'w') as f:
                    json.dump(result, f)

                print("[OK] Подключено к Outlook/Microsoft Graph")
                return True
            else:
                print(f"[X] Ошибка получения токена: {result.get('error_description', result)}")
                return False

        except ImportError:
            print("[X] Не установлен MSAL")
            print("    pip install msal")
            return False
        except Exception as e:
            print(f"[X] Ошибка аутентификации: {e}")
            return False

    def _make_request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """
        Выполнить запрос к Microsoft Graph API.

        Args:
            endpoint: Endpoint API
            params: Параметры запроса

        Returns:
            JSON ответ
        """
        if not self.access_token:
            return None

        try:
            import requests

            url = f"https://graph.microsoft.com/v1.0{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"  [!] Ошибка запроса: {e}")
            return None

    def search_messages(
        self,
        query: str = '',
        folder: str = 'inbox',
        max_results: int = 500,
        after_date: datetime = None
    ) -> List[dict]:
        """
        Поиск писем.

        Args:
            query: Поисковый запрос
            folder: Папка (inbox, sentitems, drafts)
            max_results: Максимальное количество результатов
            after_date: Дата начала поиска

        Returns:
            Список сообщений
        """
        messages = []

        # Формируем фильтр
        filters = []
        if after_date:
            date_str = after_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            filters.append(f"receivedDateTime ge {date_str}")

        params = {
            '$top': min(max_results, 100),
            '$select': 'id,subject,from,toRecipients,receivedDateTime,bodyPreview,hasAttachments',
            '$orderby': 'receivedDateTime desc'
        }

        if filters:
            params['$filter'] = ' and '.join(filters)
        if query:
            params['$search'] = f'"{query}"'

        print(f"[~] Поиск в {folder}: {query or '(все письма)'}")

        # Запрашиваем письма
        endpoint = f"/me/mailFolders/{folder}/messages"
        next_link = None

        while True:
            if next_link:
                # Используем next link для пагинации
                result = self._make_request(next_link.replace('https://graph.microsoft.com/v1.0', ''))
            else:
                result = self._make_request(endpoint, params)

            if not result:
                break

            batch = result.get('value', [])
            messages.extend(batch)

            if len(messages) >= max_results:
                break

            next_link = result.get('@odata.nextLink')
            if not next_link:
                break

        print(f"[OK] Найдено писем: {len(messages)}")
        return messages[:max_results]

    def get_message(self, message_id: str) -> Optional[dict]:
        """
        Получить полное содержимое письма.

        Args:
            message_id: ID сообщения

        Returns:
            Данные сообщения
        """
        endpoint = f"/me/messages/{message_id}"
        params = {
            '$select': 'id,subject,from,toRecipients,ccRecipients,receivedDateTime,body,hasAttachments,attachments'
        }
        return self._make_request(endpoint, params)

    def get_attachment(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """
        Получить содержимое вложения.

        Args:
            message_id: ID сообщения
            attachment_id: ID вложения

        Returns:
            Байты вложения
        """
        endpoint = f"/me/messages/{message_id}/attachments/{attachment_id}"
        result = self._make_request(endpoint)

        if result and 'contentBytes' in result:
            return base64.b64decode(result['contentBytes'])

        return None

    def parse_message(self, message: dict, full_message: dict = None) -> dict:
        """
        Распарсить сообщение в структурированные данные.

        Args:
            message: Краткие данные сообщения
            full_message: Полные данные сообщения

        Returns:
            Структурированные данные письма
        """
        if full_message:
            message = full_message

        # Парсим даты
        date_str = message.get('receivedDateTime', '')
        try:
            date_parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_iso = date_parsed.isoformat()
        except Exception:
            date_iso = date_str
            date_parsed = None

        # Парсим отправителя
        from_data = message.get('from', {}).get('emailAddress', {})
        from_name = from_data.get('name', '')
        from_email = from_data.get('address', '')

        # Парсим получателей
        to_recipients = message.get('toRecipients', [])
        to_data = to_recipients[0].get('emailAddress', {}) if to_recipients else {}
        to_name = to_data.get('name', '')
        to_email = to_data.get('address', '')

        # Тело письма
        body = message.get('body', {})
        body_content = body.get('content', '')
        body_type = body.get('contentType', 'text')

        if body_type == 'html':
            body_html = body_content
            # Простое извлечение текста из HTML
            body_text = re.sub(r'<[^>]+>', '', body_content)
            body_text = re.sub(r'\s+', ' ', body_text).strip()
        else:
            body_text = body_content
            body_html = ''

        # Вложения
        attachments = []
        for att in message.get('attachments', []):
            attachments.append({
                'id': att.get('id', ''),
                'filename': att.get('name', 'attachment'),
                'mime_type': att.get('contentType', ''),
                'size': att.get('size', 0)
            })

        result = {
            'id': message.get('id', ''),
            'thread_id': message.get('conversationId', ''),
            'date': date_iso,
            'date_str': date_str,
            'subject': message.get('subject', ''),
            'from_name': from_name,
            'from_email': from_email,
            'to_name': to_name,
            'to_email': to_email,
            'direction': 'unknown',  # Определяется позже
            'body_text': body_text,
            'body_html': body_html,
            'body_preview': message.get('bodyPreview', body_text[:500]),
            'attachments': attachments,
            'labels': [],
            'snippet': message.get('bodyPreview', ''),
            'source': 'outlook',
            'synced_at': datetime.now().isoformat()
        }

        return result


# ═══════════════════════════════════════════════════════════════
# ИЗВЛЕЧЕНИЕ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

class EmailDataExtractor:
    """Извлечение структурированных данных из email."""

    def __init__(self):
        """Инициализация экстрактора."""
        self.contacts_map: Dict[str, dict] = {}
        self._load_contacts()

    def _load_contacts(self):
        """Загрузить контакты для привязки."""
        if CONTACTS_FILE.exists():
            try:
                with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
                    contacts = json.load(f)
                    for c in contacts:
                        # Индекс по email
                        for email in c.get('emails', []):
                            self.contacts_map[email.lower()] = c
                        # Индекс по имени
                        name = c.get('name', '').lower()
                        if name:
                            self.contacts_map[name] = c
                print(f"[OK] Загружено контактов: {len(contacts)}")
            except Exception as e:
                print(f"[!] Ошибка загрузки контактов: {e}")

    def find_contact(self, email: str = None, name: str = None) -> Optional[dict]:
        """
        Найти контакт по email или имени.

        Args:
            email: Email адрес
            name: Имя контакта

        Returns:
            Данные контакта или None
        """
        if email:
            contact = self.contacts_map.get(email.lower())
            if contact:
                return contact

        if name:
            contact = self.contacts_map.get(name.lower())
            if contact:
                return contact

            # Поиск по частичному совпадению
            name_lower = name.lower()
            for key, contact in self.contacts_map.items():
                if name_lower in key or key in name_lower:
                    return contact

        return None

    def extract_booking(self, email_data: dict) -> Optional[dict]:
        """
        Извлечь данные бронирования из письма.

        Args:
            email_data: Данные письма

        Returns:
            Данные бронирования или None
        """
        subject = email_data.get('subject', '')
        body = email_data.get('body_text', '')
        from_email = email_data.get('from_email', '')

        # Проверяем, что это письмо о бронировании
        is_booking = False

        # По отправителю
        for sender in BOOKING_SENDERS:
            if sender in from_email.lower():
                is_booking = True
                break

        # По теме
        booking_keywords = [
            'booking', 'confirmation', 'reservation', 'order',
            'бронирование', 'подтверждение', 'заказ', 'ваучер'
        ]
        for keyword in booking_keywords:
            if keyword in subject.lower():
                is_booking = True
                break

        if not is_booking:
            return None

        # Извлекаем данные
        booking = {
            'email_id': email_data.get('id', ''),
            'source': from_email,
            'date_received': email_data.get('date', ''),
            'subject': subject,
        }

        text = f"{subject}\n{body}"

        # Извлекаем по паттернам
        for field, patterns in BOOKING_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    booking[field] = match.group(1).strip()
                    break

        # Привязываем к контакту
        contact = self.find_contact(email=email_data.get('to_email'))
        if contact:
            booking['contact_id'] = contact.get('id')
            booking['contact_name'] = contact.get('name')
            booking['contact_phone'] = contact.get('phone')

        return booking

    def extract_emails_from_text(self, text: str) -> List[str]:
        """
        Извлечь все email адреса из текста.

        Args:
            text: Текст для поиска

        Returns:
            Список email адресов
        """
        pattern = PATTERNS.get('email', r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        matches = re.findall(pattern, text, re.IGNORECASE)
        return list(set(matches))


# ═══════════════════════════════════════════════════════════════
# СИНХРОНИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

class EmailSync:
    """Главный класс синхронизации email."""

    def __init__(self, dry_run: bool = False):
        """
        Инициализация.

        Args:
            dry_run: Режим тестирования
        """
        self.dry_run = dry_run
        self.gmail_client = None
        self.outlook_client = None
        self.extractor = EmailDataExtractor()
        self.sync_state = self._load_sync_state()
        self.email_hashes: Set[str] = set()

        # Создаём директории
        self._ensure_directories()

    def _ensure_directories(self):
        """Создать необходимые директории."""
        EMAIL_DIR.mkdir(parents=True, exist_ok=True)
        ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_sync_state(self) -> dict:
        """Загрузить состояние синхронизации."""
        if SYNC_STATE_FILE.exists():
            try:
                with open(SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'gmail_last_sync': None,
            'outlook_last_sync': None,
            'total_synced': 0,
        }

    def _save_sync_state(self):
        """Сохранить состояние синхронизации."""
        if self.dry_run:
            return

        try:
            with open(SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.sync_state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Ошибка сохранения состояния: {e}")

    def _email_hash(self, email_data: dict) -> str:
        """
        Вычислить хеш письма для дедупликации.

        Args:
            email_data: Данные письма

        Returns:
            MD5 хеш
        """
        key = f"{email_data.get('date', '')}{email_data.get('from_email', '')}{email_data.get('subject', '')}"
        return md5(key.encode()).hexdigest()

    def _load_existing_hashes(self):
        """Загрузить хеши существующих писем."""
        if not EMAILS_FILE.exists():
            return

        try:
            with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        email_data = json.loads(line.strip())
                        hash_val = self._email_hash(email_data)
                        self.email_hashes.add(hash_val)
                    except Exception:
                        continue
            print(f"[OK] Загружено существующих писем: {len(self.email_hashes)}")
        except Exception as e:
            print(f"[!] Ошибка загрузки существующих писем: {e}")

    def _save_email(self, email_data: dict):
        """
        Сохранить письмо в JSONL файл.

        Args:
            email_data: Данные письма
        """
        if self.dry_run:
            return

        try:
            with open(EMAILS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(email_data, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"  [!] Ошибка сохранения письма: {e}")

    def _save_attachment(
        self,
        email_id: str,
        attachment: dict,
        content: bytes
    ) -> Optional[str]:
        """
        Сохранить вложение.

        Args:
            email_id: ID письма
            attachment: Данные вложения
            content: Содержимое файла

        Returns:
            Путь к сохранённому файлу
        """
        if self.dry_run or not content:
            return None

        try:
            # Безопасное имя файла
            filename = attachment.get('filename', 'attachment')
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

            # Путь с ID письма
            file_path = ATTACHMENTS_DIR / f"{email_id[:8]}_{safe_filename}"

            with open(file_path, 'wb') as f:
                f.write(content)

            return str(file_path)

        except Exception as e:
            print(f"  [!] Ошибка сохранения вложения: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════
    # GMAIL СИНХРОНИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════════

    def sync_gmail(
        self,
        days: int = None,
        query: str = '',
        save_attachments: bool = True
    ) -> Tuple[int, int]:
        """
        Синхронизировать Gmail.

        Args:
            days: За сколько дней синхронизировать
            query: Дополнительный поисковый запрос
            save_attachments: Сохранять вложения

        Returns:
            (synced, skipped)
        """
        print("\n" + "=" * 60)
        print("СИНХРОНИЗАЦИЯ GMAIL")
        print("=" * 60)

        # Подключаемся
        self.gmail_client = GmailClient(dry_run=self.dry_run)
        if not self.gmail_client.authenticate():
            return 0, 0

        # Загружаем существующие хеши
        self._load_existing_hashes()

        # Определяем период
        if days is None:
            days = EMAIL_SYNC_DAYS

        after_date = datetime.now() - timedelta(days=days)
        print(f"Период: с {after_date.strftime('%Y-%m-%d')} ({days} дней)")

        # Поиск писем
        messages = self.gmail_client.search_messages(
            query=query,
            label_ids=GMAIL_LABELS_SYNC,
            after_date=after_date
        )

        synced = 0
        skipped = 0

        for i, msg_ref in enumerate(messages):
            msg_id = msg_ref.get('id')

            # Получаем полное содержимое
            message = self.gmail_client.get_message(msg_id)
            if not message:
                skipped += 1
                continue

            # Парсим
            email_data = self.gmail_client.parse_message(message)

            # Проверяем дубликат
            hash_val = self._email_hash(email_data)
            if hash_val in self.email_hashes:
                skipped += 1
                continue

            # Сохраняем вложения
            if save_attachments and email_data.get('attachments'):
                saved_attachments = []
                for att in email_data['attachments']:
                    content = self.gmail_client.get_attachment(msg_id, att['id'])
                    if content:
                        path = self._save_attachment(msg_id, att, content)
                        if path:
                            att['local_path'] = path
                            saved_attachments.append(att)
                email_data['attachments'] = saved_attachments

            # Извлекаем бронирование
            booking = self.extractor.extract_booking(email_data)
            if booking:
                email_data['booking'] = booking

            # Привязываем к контакту
            contact_email = email_data.get('from_email') if email_data.get('direction') == 'incoming' else email_data.get('to_email')
            contact = self.extractor.find_contact(email=contact_email)
            if contact:
                email_data['linked_contact'] = {
                    'id': contact.get('id'),
                    'name': contact.get('name'),
                    'phone': contact.get('phone'),
                }

            # Сохраняем
            self._save_email(email_data)
            self.email_hashes.add(hash_val)
            synced += 1

            # Прогресс
            if (i + 1) % 50 == 0:
                print(f"  Обработано: {i + 1}/{len(messages)}")

        print(f"\n[OK] Gmail: синхронизировано {synced}, пропущено {skipped}")

        # Обновляем состояние
        self.sync_state['gmail_last_sync'] = datetime.now().isoformat()
        self.sync_state['total_synced'] = self.sync_state.get('total_synced', 0) + synced
        self._save_sync_state()

        return synced, skipped

    # ═══════════════════════════════════════════════════════════════
    # OUTLOOK СИНХРОНИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════════

    def sync_outlook(
        self,
        days: int = None,
        query: str = '',
        save_attachments: bool = True
    ) -> Tuple[int, int]:
        """
        Синхронизировать Outlook.

        Args:
            days: За сколько дней синхронизировать
            query: Дополнительный поисковый запрос
            save_attachments: Сохранять вложения

        Returns:
            (synced, skipped)
        """
        print("\n" + "=" * 60)
        print("СИНХРОНИЗАЦИЯ OUTLOOK")
        print("=" * 60)

        # Подключаемся
        self.outlook_client = OutlookClient(dry_run=self.dry_run)
        if not self.outlook_client.authenticate():
            return 0, 0

        # Загружаем существующие хеши
        self._load_existing_hashes()

        # Определяем период
        if days is None:
            days = EMAIL_SYNC_DAYS

        after_date = datetime.now() - timedelta(days=days)
        print(f"Период: с {after_date.strftime('%Y-%m-%d')} ({days} дней)")

        # Синхронизируем inbox и sent
        synced = 0
        skipped = 0

        for folder in ['inbox', 'sentitems']:
            print(f"\n[~] Папка: {folder}")

            messages = self.outlook_client.search_messages(
                query=query,
                folder=folder,
                after_date=after_date
            )

            for i, msg_ref in enumerate(messages):
                msg_id = msg_ref.get('id')

                # Получаем полное содержимое
                full_message = self.outlook_client.get_message(msg_id)

                # Парсим
                email_data = self.outlook_client.parse_message(msg_ref, full_message)
                email_data['direction'] = 'outgoing' if folder == 'sentitems' else 'incoming'

                # Проверяем дубликат
                hash_val = self._email_hash(email_data)
                if hash_val in self.email_hashes:
                    skipped += 1
                    continue

                # Сохраняем вложения
                if save_attachments and email_data.get('attachments'):
                    saved_attachments = []
                    for att in email_data['attachments']:
                        content = self.outlook_client.get_attachment(msg_id, att['id'])
                        if content:
                            path = self._save_attachment(msg_id, att, content)
                            if path:
                                att['local_path'] = path
                                saved_attachments.append(att)
                    email_data['attachments'] = saved_attachments

                # Извлекаем бронирование
                booking = self.extractor.extract_booking(email_data)
                if booking:
                    email_data['booking'] = booking

                # Привязываем к контакту
                contact_email = email_data.get('from_email') if email_data.get('direction') == 'incoming' else email_data.get('to_email')
                contact = self.extractor.find_contact(email=contact_email)
                if contact:
                    email_data['linked_contact'] = {
                        'id': contact.get('id'),
                        'name': contact.get('name'),
                        'phone': contact.get('phone'),
                    }

                # Сохраняем
                self._save_email(email_data)
                self.email_hashes.add(hash_val)
                synced += 1

        print(f"\n[OK] Outlook: синхронизировано {synced}, пропущено {skipped}")

        # Обновляем состояние
        self.sync_state['outlook_last_sync'] = datetime.now().isoformat()
        self.sync_state['total_synced'] = self.sync_state.get('total_synced', 0) + synced
        self._save_sync_state()

        return synced, skipped

    # ═══════════════════════════════════════════════════════════════
    # СВЯЗИ EMAIL-КОНТАКТ
    # ═══════════════════════════════════════════════════════════════

    def build_email_contacts(self) -> dict:
        """
        Построить связи email-контакт.

        Returns:
            Статистика
        """
        print("\n" + "=" * 60)
        print("ПОСТРОЕНИЕ СВЯЗЕЙ EMAIL-КОНТАКТ")
        print("=" * 60)

        if not EMAILS_FILE.exists():
            print(f"[!] Файл не найден: {EMAILS_FILE}")
            return {'contacts': 0, 'emails': 0}

        # Собираем все email адреса
        email_stats: Dict[str, dict] = {}

        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    email_data = json.loads(line.strip())

                    # Email отправителя
                    from_email = email_data.get('from_email', '').lower()
                    if from_email:
                        if from_email not in email_stats:
                            email_stats[from_email] = {
                                'email': from_email,
                                'names': set(),
                                'message_count': 0,
                                'last_message': '',
                                'linked_contact': None,
                            }
                        email_stats[from_email]['message_count'] += 1
                        if email_data.get('from_name'):
                            email_stats[from_email]['names'].add(email_data['from_name'])
                        if email_data.get('date', '') > email_stats[from_email]['last_message']:
                            email_stats[from_email]['last_message'] = email_data['date']

                    # Email получателя
                    to_email = email_data.get('to_email', '').lower()
                    if to_email:
                        if to_email not in email_stats:
                            email_stats[to_email] = {
                                'email': to_email,
                                'names': set(),
                                'message_count': 0,
                                'last_message': '',
                                'linked_contact': None,
                            }
                        email_stats[to_email]['message_count'] += 1
                        if email_data.get('to_name'):
                            email_stats[to_email]['names'].add(email_data['to_name'])

                    # Связанный контакт
                    linked = email_data.get('linked_contact')
                    if linked:
                        if from_email:
                            email_stats[from_email]['linked_contact'] = linked
                        if to_email:
                            email_stats[to_email]['linked_contact'] = linked

                except Exception:
                    continue

        # Конвертируем для сохранения
        contacts_list = []
        for email, stats in email_stats.items():
            stats['names'] = list(stats['names'])
            contacts_list.append(stats)

        # Сортируем по количеству сообщений
        contacts_list.sort(key=lambda x: x['message_count'], reverse=True)

        # Сохраняем
        if not self.dry_run:
            with open(EMAIL_CONTACTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(contacts_list, f, indent=2, ensure_ascii=False)
            print(f"[OK] Сохранено: {EMAIL_CONTACTS_FILE}")

        linked_count = sum(1 for c in contacts_list if c['linked_contact'])
        print(f"Всего email адресов: {len(contacts_list)}")
        print(f"Связано с контактами: {linked_count}")

        return {'contacts': len(contacts_list), 'linked': linked_count}

    # ═══════════════════════════════════════════════════════════════
    # ИЗВЛЕЧЕНИЕ БРОНИРОВАНИЙ
    # ═══════════════════════════════════════════════════════════════

    def extract_bookings(self) -> List[dict]:
        """
        Извлечь все бронирования из писем.

        Returns:
            Список бронирований
        """
        print("\n" + "=" * 60)
        print("ИЗВЛЕЧЕНИЕ БРОНИРОВАНИЙ ИЗ EMAIL")
        print("=" * 60)

        if not EMAILS_FILE.exists():
            print(f"[!] Файл не найден: {EMAILS_FILE}")
            return []

        bookings = []

        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    email_data = json.loads(line.strip())
                    booking = email_data.get('booking')
                    if booking:
                        bookings.append(booking)
                except Exception:
                    continue

        print(f"[OK] Найдено бронирований: {len(bookings)}")

        # Сохраняем
        if not self.dry_run and bookings:
            bookings_file = EMAIL_DIR / "email_bookings.json"
            with open(bookings_file, 'w', encoding='utf-8') as f:
                json.dump(bookings, f, indent=2, ensure_ascii=False)
            print(f"[OK] Сохранено: {bookings_file}")

        return bookings

    # ═══════════════════════════════════════════════════════════════
    # BITRIX24 ИНТЕГРАЦИЯ
    # ═══════════════════════════════════════════════════════════════

    def sync_to_bitrix24(self) -> dict:
        """
        Синхронизировать email активности с Bitrix24.

        Returns:
            Статистика синхронизации
        """
        print("\n" + "=" * 60)
        print("СИНХРОНИЗАЦИЯ С BITRIX24")
        print("=" * 60)

        # Проверяем конфигурацию
        if not BITRIX24_CONFIG.get('domain') or not BITRIX24_CONFIG.get('webhook_key'):
            print("[!] Bitrix24 не настроен")
            print("    Установите переменные окружения:")
            print("    BITRIX24_DOMAIN, BITRIX24_USER_ID, BITRIX24_WEBHOOK_KEY")
            return {'synced': 0, 'failed': 0}

        if not EMAILS_FILE.exists():
            print(f"[!] Файл не найден: {EMAILS_FILE}")
            return {'synced': 0, 'failed': 0}

        try:
            import requests
        except ImportError:
            print("[X] Не установлен requests")
            print("    pip install requests")
            return {'synced': 0, 'failed': 0}

        # Формируем URL вебхука
        domain = BITRIX24_CONFIG['domain']
        user_id = BITRIX24_CONFIG['user_id']
        webhook_key = BITRIX24_CONFIG['webhook_key']
        base_url = f"https://{domain}.bitrix24.ru/rest/{user_id}/{webhook_key}"

        synced = 0
        failed = 0

        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    email_data = json.loads(line.strip())

                    # Пропускаем письма без привязки к контакту
                    linked = email_data.get('linked_contact')
                    if not linked:
                        continue

                    # Ищем контакт в Bitrix24 по телефону
                    phone = linked.get('phone', '')
                    if not phone:
                        continue

                    # Поиск контакта
                    search_url = f"{base_url}/crm.contact.list"
                    search_params = {
                        'filter': {'PHONE': phone},
                        'select': ['ID', 'NAME', 'LAST_NAME']
                    }

                    if self.dry_run:
                        print(f"  [DRY-RUN] Поиск контакта: {phone}")
                        continue

                    response = requests.post(search_url, json=search_params)
                    result = response.json()

                    contacts = result.get('result', [])
                    if not contacts:
                        continue

                    contact_id = contacts[0]['ID']

                    # Создаём активность (email)
                    activity_url = f"{base_url}/crm.activity.add"
                    activity_data = {
                        'fields': {
                            'OWNER_TYPE_ID': 3,  # Контакт
                            'OWNER_ID': contact_id,
                            'TYPE_ID': 4,  # Email
                            'DIRECTION': 1 if email_data.get('direction') == 'incoming' else 2,
                            'SUBJECT': email_data.get('subject', 'Email'),
                            'DESCRIPTION': email_data.get('body_preview', ''),
                            'COMPLETED': 'Y',
                            'PROVIDER_ID': 'EMAIL',
                            'PROVIDER_TYPE_ID': 'EMAIL',
                        }
                    }

                    response = requests.post(activity_url, json=activity_data)
                    result = response.json()

                    if result.get('result'):
                        synced += 1
                    else:
                        failed += 1
                        print(f"  [!] Ошибка: {result.get('error_description', 'Unknown')}")

                except Exception as e:
                    failed += 1
                    print(f"  [!] Ошибка обработки: {e}")

        print(f"\n[OK] Bitrix24: синхронизировано {synced}, ошибок {failed}")
        return {'synced': synced, 'failed': failed}

    # ═══════════════════════════════════════════════════════════════
    # ДЕДУПЛИКАЦИЯ С WHATSAPP
    # ═══════════════════════════════════════════════════════════════

    def deduplicate_with_whatsapp(self) -> dict:
        """
        Найти пересечения email и WhatsApp сообщений.

        Returns:
            Статистика дедупликации
        """
        print("\n" + "=" * 60)
        print("ДЕДУПЛИКАЦИЯ С WHATSAPP")
        print("=" * 60)

        if not EMAILS_FILE.exists():
            print(f"[!] Файл не найден: {EMAILS_FILE}")
            return {'duplicates': 0}

        # Загружаем контакты с телефонами и email
        contacts_with_both = []

        if CONTACTS_FILE.exists():
            with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
                for c in contacts:
                    if c.get('phone') and c.get('emails'):
                        contacts_with_both.append(c)

        print(f"Контактов с телефоном и email: {len(contacts_with_both)}")

        # Анализируем пересечения
        duplicates = []

        for contact in contacts_with_both:
            # Ищем сообщения об одном и том же бронировании
            phone = contact.get('phone', '')
            emails = contact.get('emails', [])

            # Загружаем операции из WhatsApp
            if OPERATIONS_FILE.exists():
                with open(OPERATIONS_FILE, 'r', encoding='utf-8') as f:
                    operations = json.load(f)

                whatsapp_ops = [
                    op for op in operations
                    if op.get('phone') == phone
                ]

                # Ищем совпадения в email
                with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            email_data = json.loads(line.strip())
                            from_email = email_data.get('from_email', '').lower()

                            if from_email in [e.lower() for e in emails]:
                                booking = email_data.get('booking')
                                if booking:
                                    # Проверяем совпадение дат
                                    booking_date = booking.get('date', '')
                                    for op in whatsapp_ops:
                                        if op.get('date') == booking_date:
                                            duplicates.append({
                                                'contact': contact.get('name'),
                                                'date': booking_date,
                                                'email_id': email_data.get('id'),
                                                'whatsapp_op': op.get('id'),
                                            })
                        except Exception:
                            continue

        print(f"Найдено возможных дубликатов: {len(duplicates)}")

        # Сохраняем
        if not self.dry_run and duplicates:
            duplicates_file = EMAIL_DIR / "email_whatsapp_duplicates.json"
            with open(duplicates_file, 'w', encoding='utf-8') as f:
                json.dump(duplicates, f, indent=2, ensure_ascii=False)
            print(f"[OK] Сохранено: {duplicates_file}")

        return {'duplicates': len(duplicates)}

    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════

    def print_stats(self):
        """Вывести статистику синхронизации."""
        print("\n" + "=" * 60)
        print("СТАТИСТИКА EMAIL СИНХРОНИЗАЦИИ")
        print("=" * 60)

        # Состояние синхронизации
        print("\nПоследняя синхронизация:")
        print(f"  Gmail:   {self.sync_state.get('gmail_last_sync', 'никогда')}")
        print(f"  Outlook: {self.sync_state.get('outlook_last_sync', 'никогда')}")

        # Подсчёт писем
        total_emails = 0
        by_source = {'gmail': 0, 'outlook': 0}
        by_direction = {'incoming': 0, 'outgoing': 0, 'unknown': 0}
        with_attachments = 0
        with_bookings = 0
        linked_to_contacts = 0

        if EMAILS_FILE.exists():
            with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        email_data = json.loads(line.strip())
                        total_emails += 1

                        source = email_data.get('source', 'unknown')
                        by_source[source] = by_source.get(source, 0) + 1

                        direction = email_data.get('direction', 'unknown')
                        by_direction[direction] = by_direction.get(direction, 0) + 1

                        if email_data.get('attachments'):
                            with_attachments += 1

                        if email_data.get('booking'):
                            with_bookings += 1

                        if email_data.get('linked_contact'):
                            linked_to_contacts += 1

                    except Exception:
                        continue

        print(f"\nВсего писем: {total_emails}")
        print(f"\nПо источнику:")
        for source, count in by_source.items():
            print(f"  {source}: {count}")

        print(f"\nПо направлению:")
        for direction, count in by_direction.items():
            print(f"  {direction}: {count}")

        print(f"\nС вложениями: {with_attachments}")
        print(f"С бронированиями: {with_bookings}")
        print(f"Связано с контактами: {linked_to_contacts}")

        # Размер файлов
        if EMAILS_FILE.exists():
            size_mb = EMAILS_FILE.stat().st_size / (1024 * 1024)
            print(f"\nРазмер emails.jsonl: {size_mb:.2f} MB")

        if ATTACHMENTS_DIR.exists():
            att_count = len(list(ATTACHMENTS_DIR.iterdir()))
            print(f"Вложений сохранено: {att_count}")


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Синхронизация email переписки (Gmail/Outlook)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python email_sync.py --gmail --days 30
  python email_sync.py --outlook --days 30
  python email_sync.py --sync-all
  python email_sync.py --gmail --search "from:booking@example.com"
  python email_sync.py --extract-bookings
  python email_sync.py --link-contacts
  python email_sync.py --bitrix24
  python email_sync.py --deduplicate
  python email_sync.py --stats
  python email_sync.py --dry-run --gmail

Настройка Gmail:
  1. Создайте OAuth2 credentials в Google Cloud Console
  2. Включите Gmail API
  3. Скачайте credentials.json
  4. Установите переменную окружения:
     set GMAIL_CREDENTIALS_FILE=C:/path/to/credentials.json

Настройка Outlook:
  1. Зарегистрируйте приложение в Azure Portal
  2. Установите переменные окружения:
     set OUTLOOK_CLIENT_ID=your-client-id
     set OUTLOOK_CLIENT_SECRET=your-client-secret

Выходные файлы:
  - emails.jsonl: все синхронизированные письма
  - email_contacts.json: связи email-контакт
  - email_attachments/: сохранённые вложения
        """
    )

    # Режимы синхронизации
    sync_group = parser.add_argument_group('Синхронизация')
    sync_group.add_argument(
        '--gmail', '-g',
        action='store_true',
        help='Синхронизировать Gmail'
    )
    sync_group.add_argument(
        '--outlook', '-o',
        action='store_true',
        help='Синхронизировать Outlook'
    )
    sync_group.add_argument(
        '--sync-all', '-a',
        action='store_true',
        help='Синхронизировать все источники'
    )

    # Параметры синхронизации
    params_group = parser.add_argument_group('Параметры')
    params_group.add_argument(
        '--days', '-d',
        type=int,
        default=None,
        help=f'За сколько дней синхронизировать (по умолчанию {EMAIL_SYNC_DAYS})'
    )
    params_group.add_argument(
        '--search', '-s',
        type=str,
        default='',
        help='Поисковый запрос (Gmail query syntax)'
    )
    params_group.add_argument(
        '--no-attachments',
        action='store_true',
        help='Не сохранять вложения'
    )

    # Обработка данных
    process_group = parser.add_argument_group('Обработка')
    process_group.add_argument(
        '--extract-bookings', '-b',
        action='store_true',
        help='Извлечь бронирования из писем'
    )
    process_group.add_argument(
        '--link-contacts', '-l',
        action='store_true',
        help='Построить связи email-контакт'
    )
    process_group.add_argument(
        '--deduplicate',
        action='store_true',
        help='Найти дубликаты с WhatsApp'
    )
    process_group.add_argument(
        '--bitrix24',
        action='store_true',
        help='Синхронизировать с Bitrix24'
    )

    # Дополнительно
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Показать статистику'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Режим тестирования (без записи)'
    )

    args = parser.parse_args()

    # Если ничего не указано - показываем справку
    if not any([
        args.gmail, args.outlook, args.sync_all,
        args.extract_bookings, args.link_contacts,
        args.deduplicate, args.bitrix24, args.stats
    ]):
        parser.print_help()
        return

    print("=" * 60)
    print("EMAIL SYNC")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.dry_run:
        print("[DRY-RUN] Режим тестирования - данные НЕ будут сохранены")

    # Создаём синхронизатор
    sync = EmailSync(dry_run=args.dry_run)

    save_attachments = not args.no_attachments

    # Выполняем действия
    if args.gmail or args.sync_all:
        sync.sync_gmail(
            days=args.days,
            query=args.search,
            save_attachments=save_attachments
        )

    if args.outlook or args.sync_all:
        sync.sync_outlook(
            days=args.days,
            query=args.search,
            save_attachments=save_attachments
        )

    if args.extract_bookings:
        sync.extract_bookings()

    if args.link_contacts:
        sync.build_email_contacts()

    if args.deduplicate:
        sync.deduplicate_with_whatsapp()

    if args.bitrix24:
        sync.sync_to_bitrix24()

    if args.stats:
        sync.print_stats()

    print("\n[OK] Готово!")


if __name__ == "__main__":
    main()
