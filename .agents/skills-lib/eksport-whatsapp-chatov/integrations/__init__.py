#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интеграции с внешними сервисами.
Notion, Google Sheets, Telegram, Calendar.
"""

from pathlib import Path
import sys

# Добавляем путь к scripts
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from .notion import NotionIntegration
from .google_sheets import GoogleSheetsIntegration
from .telegram_bot import TelegramBotIntegration
from .calendar import CalendarIntegration

__all__ = [
    'NotionIntegration',
    'GoogleSheetsIntegration',
    'TelegramBotIntegration',
    'CalendarIntegration',
]
