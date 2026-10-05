"""
Модуль анализа WhatsApp чатов.

Скрипты:
- analyze_emoji: Анализ использования эмодзи
- analyze_words: Анализ частоты слов
- analyze_activity_time: Анализ времени активности
- analyze_message_length: Анализ длины сообщений
- analyze_trends: Анализ трендов
- detect_language: Определение языка
- detect_spam: Детекция спама
- detect_groups: Детекция групп
- find_duplicates: Поиск дубликатов
- contact_graph: Граф контактов
- chat_statistics: Статистика чатов
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
