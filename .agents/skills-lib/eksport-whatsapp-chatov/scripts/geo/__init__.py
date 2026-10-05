"""
Модуль геолокации и маршрутизации.

Скрипты:
- client_heatmap: Тепловая карта клиентов
- pickup_optimizer: Оптимизатор точек подачи
- driver_routes: Маршруты водителей
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
