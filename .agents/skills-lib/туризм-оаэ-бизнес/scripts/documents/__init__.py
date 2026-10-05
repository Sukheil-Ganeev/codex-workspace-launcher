"""
Модуль генерации документов.

Содержит генераторы договоров, отчетов, счетов и ваучеров
для туристического агентства.
"""

from .contract_generator import *
from .generate_report import *
from .invoice_generator import *
from .voucher_generator import *

__all__ = [
    'contract_generator',
    'generate_report',
    'invoice_generator',
    'voucher_generator',
]
