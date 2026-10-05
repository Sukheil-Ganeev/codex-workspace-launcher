"""
Модуль визуализации и отчетности.

Содержит инструменты для построения тепловых карт активности,
дашбордов и финансовых отчетов.
"""

from .activity_heatmap import *
from .dashboard import *
from .financial_reports import *

__all__ = [
    'activity_heatmap',
    'dashboard',
    'financial_reports',
]
