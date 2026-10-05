"""
Туризм ОАЭ Автоматизация - пакет скриптов.

Основной пакет для автоматизации процессов туристического агентства.
Включает модули: ai (ИИ), marketing (маркетинг), partners (партнеры),
media (медиа), visualization (визуализация).
"""

from .config import *
from . import ai
from . import marketing
from . import partners
from . import media
from . import visualization

__all__ = [
    'config',
    'ai',
    'marketing',
    'partners',
    'media',
    'visualization',
]
