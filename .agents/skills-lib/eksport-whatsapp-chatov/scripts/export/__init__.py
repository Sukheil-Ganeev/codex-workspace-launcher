"""
Модуль экспорта данных.

Скрипты:
- export_for_airtable: Экспорт для Airtable
- build_document: Построение документа
- build_index: Построение индекса
- generate_templates: Генерация шаблонов
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
