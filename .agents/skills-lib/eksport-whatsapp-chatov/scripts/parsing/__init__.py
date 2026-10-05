"""
Модуль парсинга и извлечения данных из WhatsApp чатов.

Скрипты:
- parse_all_chats: Парсинг всех чатов
- parse_vcf: Парсинг VCF контактов
- parse_vcf_advanced: Расширенный парсинг VCF
- extract_contacts: Извлечение контактов
- extract_urls: Извлечение URL
- extract_emails: Извлечение email
- extract_locations: Извлечение локаций
- extract_banking: Извлечение банковских данных
- extract_datetime: Извлечение дат и времени
- extract_forwarded: Извлечение пересланных сообщений
- extract_operations: Извлечение операций
- extract_requisites: Извлечение реквизитов
- extract_todos: Извлечение задач
- extract_patterns: Извлечение паттернов
- extract_price_inquiries: Извлечение ценовых запросов
- extract_travel_dates: Извлечение дат путешествий
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
