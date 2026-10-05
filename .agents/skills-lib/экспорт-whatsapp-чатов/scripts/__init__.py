"""
WhatsApp Chat Export Toolkit
90 скриптов для анализа чатов

Использование:
    from scripts.parsing import parse_all_chats
    from scripts.analysis import detect_language
    from scripts.integrations import telegram_bot

Модули:
- parsing: Парсинг и извлечение данных (16 скриптов)
- analysis: Анализ чатов (11 скриптов)
- business: Бизнес-аналитика (15 скриптов)
- ai: AI и ML (7 скриптов)
- media: Работа с медиа (6 скриптов)
- integrations: Интеграции (9 скриптов)
- marketing: Маркетинг (4 скрипта)
- partners: Партнёры (3 скрипта)
- geo: Геолокация (3 скрипта)
- documents: Документы (4 скрипта)
- export: Экспорт (4 скрипта)
- visualization: Визуализация (3 скрипта)
- utils: Утилиты (4 скрипта)
"""

__version__ = "2.0.0"
__author__ = "AI Agent"

# Подмодули
from . import parsing
from . import analysis
from . import business
from . import ai
from . import media
from . import integrations
from . import marketing
from . import partners
from . import geo
from . import documents
from . import export
from . import visualization
from . import utils
