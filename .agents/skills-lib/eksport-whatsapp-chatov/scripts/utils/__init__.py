"""
Модуль утилит.

Скрипты:
- mask_data: Маскирование данных
- search: Поиск по чатам
- diff_chats: Сравнение чатов
- process_all: Обработка всех чатов
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
