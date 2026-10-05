"""
Модуль работы с партнёрами.

Скрипты:
- agent_portal: Портал агентов
- partner_api: API для партнёров
- white_label: White label решения
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
