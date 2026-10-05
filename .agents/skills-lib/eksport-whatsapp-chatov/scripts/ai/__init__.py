"""
Модуль AI и ML анализа WhatsApp чатов.

Скрипты:
- claude_classifier: Классификатор на Claude
- sentiment_analysis: Анализ тональности
- summarize_dialog: Суммаризация диалогов
- auto_responder: Автоответчик
- auto_followup: Автоматические follow-up
- smart_analysis: Умный анализ
- demand_forecast: Прогноз спроса
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
