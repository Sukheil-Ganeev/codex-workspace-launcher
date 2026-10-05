"""
Модуль визуализации данных.

Скрипты:
- dashboard: Дашборд
- activity_heatmap: Тепловая карта активности
- financial_reports: Финансовые отчёты
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
