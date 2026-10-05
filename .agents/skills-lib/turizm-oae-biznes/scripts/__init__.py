"""
Туризм ОАЭ Бизнес - пакет скриптов.

Основной пакет для бизнес-аналитики туристического агентства.
Включает модули: business (аналитика), integrations (интеграции),
documents (документы), geo (геоданные), export (экспорт).
"""

from .config import *
from . import business
from . import integrations
from . import documents
from . import geo
from . import export

__all__ = [
    'config',
    'business',
    'integrations',
    'documents',
    'geo',
    'export',
]
