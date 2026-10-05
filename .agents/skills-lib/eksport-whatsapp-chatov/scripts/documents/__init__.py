"""
Модуль генерации документов.

Скрипты:
- invoice_generator: Генератор счетов
- contract_generator: Генератор контрактов
- voucher_generator: Генератор ваучеров
- generate_report: Генератор отчётов
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
