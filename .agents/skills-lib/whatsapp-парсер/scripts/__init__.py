"""
WhatsApp парсер - пакет скриптов.

Основной пакет для парсинга и анализа WhatsApp переписок.
Включает модули parsing (извлечение данных) и utils (утилиты).
"""

from . import parsing
from . import utils

__all__ = [
    'parsing',
    'utils',
]
