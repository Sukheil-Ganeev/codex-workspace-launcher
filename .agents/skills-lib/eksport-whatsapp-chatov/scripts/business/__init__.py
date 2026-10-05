"""
Модуль бизнес-аналитики WhatsApp чатов.

Скрипты:
- build_profiles: Построение профилей клиентов
- build_sales_funnel: Построение воронки продаж
- classify_contacts: Классификация контактов
- detect_referrals: Детекция рефералов
- calculate_ltv: Расчёт LTV
- calculate_response_time: Расчёт времени ответа
- first_response_time: Время первого ответа
- dialog_duration: Длительность диалогов
- source_conversion: Конверсия по источникам
- rejection_analysis: Анализ отказов
- repeat_customers: Повторные клиенты
- average_check: Средний чек
- manager_efficiency: Эффективность менеджеров
- seasonal_analysis: Сезонный анализ
- extract_complaints: Извлечение жалоб
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
