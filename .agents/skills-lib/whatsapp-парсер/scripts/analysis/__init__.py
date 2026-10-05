"""
Модуль анализа WhatsApp чатов.

Содержит скрипты для статистического анализа,
обнаружения паттернов и визуализации данных.

Новые скрипты бизнес-аналитики:
- funnel_analysis - анализ воронки продаж
- quality_metrics - метрики качества обслуживания
- session_analysis - анализ сессий (диалогов)
- intent_classifier - классификация интентов
"""

from .analyze_activity_time import *
from .analyze_emoji import *
from .analyze_message_length import *
from .analyze_trends import *
from .analyze_words import *
from .chat_statistics import *
from .contact_graph import *
from .detect_groups import *
from .detect_language import *
from .detect_spam import *
from .find_duplicates import *

# Новые модули бизнес-аналитики
from .funnel_analysis import *
from .quality_metrics import *
from .session_analysis import *
from .intent_classifier import *

__all__ = [
    # Базовая аналитика
    'analyze_activity_time',
    'analyze_emoji',
    'analyze_message_length',
    'analyze_trends',
    'analyze_words',
    'chat_statistics',
    'contact_graph',
    'detect_groups',
    'detect_language',
    'detect_spam',
    'find_duplicates',
    # Бизнес-аналитика
    'funnel_analysis',
    'quality_metrics',
    'session_analysis',
    'intent_classifier',
]
