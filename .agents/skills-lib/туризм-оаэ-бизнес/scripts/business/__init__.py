"""
Модуль бизнес-аналитики туристического агентства.

Содержит инструменты для анализа продаж, клиентов и эффективности:
средний чек, профили клиентов, воронка продаж, LTV, время ответа,
классификация контактов, рефералы, длительность диалогов, жалобы,
время первого ответа, эффективность менеджеров, анализ отказов,
повторные клиенты, сезонность и конверсия источников.
"""

from .average_check import *
from .build_profiles import *
from .build_sales_funnel import *
from .calculate_ltv import *
from .calculate_response_time import *
from .classify_contacts import *
from .detect_referrals import *
from .dialog_duration import *
from .extract_complaints import *
from .first_response_time import *
from .manager_efficiency import *
from .rejection_analysis import *
from .repeat_customers import *
from .seasonal_analysis import *
from .source_conversion import *

__all__ = [
    'average_check',
    'build_profiles',
    'build_sales_funnel',
    'calculate_ltv',
    'calculate_response_time',
    'classify_contacts',
    'detect_referrals',
    'dialog_duration',
    'extract_complaints',
    'first_response_time',
    'manager_efficiency',
    'rejection_analysis',
    'repeat_customers',
    'seasonal_analysis',
    'source_conversion',
]
