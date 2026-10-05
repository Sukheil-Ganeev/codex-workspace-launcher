"""
Модуль маркетинговых инструментов.

Скрипты:
- referral_program: Реферальная программа
- email_marketing: Email маркетинг
- sms_twilio: SMS через Twilio
- instagram_parser: Парсер Instagram
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
