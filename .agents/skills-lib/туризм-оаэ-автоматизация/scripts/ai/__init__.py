"""
Модуль AI и машинного обучения.

Содержит инструменты для автоматического follow-up, авто-ответов,
классификации через Claude, прогнозирования спроса, анализа тональности,
умного анализа и суммаризации диалогов.
"""

from .auto_followup import *
from .auto_responder import *
from .claude_classifier import *
from .demand_forecast import *
from .sentiment_analysis import *
from .smart_analysis import *
from .summarize_dialog import *

__all__ = [
    'auto_followup',
    'auto_responder',
    'claude_classifier',
    'demand_forecast',
    'sentiment_analysis',
    'smart_analysis',
    'summarize_dialog',
]
