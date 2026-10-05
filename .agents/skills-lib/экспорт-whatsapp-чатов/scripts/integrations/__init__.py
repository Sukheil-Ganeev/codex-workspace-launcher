"""
Модуль интеграций WhatsApp с внешними сервисами.

Скрипты:
- bitrix24_integration: Интеграция с Битрикс24
- bitrix24_products: Продукты Битрикс24
- bitrix24_timeline: Таймлайн Битрикс24
- google_sheets_export: Экспорт в Google Sheets
- google_calendar_sync: Синхронизация с Google Calendar
- notion_sync: Синхронизация с Notion
- telegram_bot: Telegram бот
- whatsapp_api: WhatsApp Business API
- email_sync: Синхронизация с email
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
