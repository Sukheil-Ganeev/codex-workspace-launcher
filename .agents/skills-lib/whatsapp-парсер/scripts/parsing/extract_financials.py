#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсинг финансовых данных из сообщений WhatsApp.

Вход: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выход: D:/Downloads/Chats/_база/json/financials.json

Функции:
- Извлечение цен и валют (AED, USD, RUB, EUR, USDT, KZT)
- Парсинг скидок (%, фиксированные)
- Парсинг оплат (оплатил, перевёл, получил)
- Парсинг комиссий (нетто/брутто)
- Валютные операции и курсы
"""

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import RAW_DIR, JSON_DIR, ensure_directories

# Настройка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')


# ===================================================================
# КОНСТАНТЫ И ПАТТЕРНЫ
# ===================================================================

INPUT_FILE = RAW_DIR / "all_messages.jsonl"
OUTPUT_FILE = JSON_DIR / "financials.json"

# Символы и названия валют
CURRENCY_SYMBOLS = {
    '$': 'USD',
    '€': 'EUR',
    '£': 'GBP',
    '₽': 'RUB',
    '₸': 'KZT',
    'د.إ': 'AED',
    '﷼': 'SAR',
}

CURRENCY_NAMES = {
    # Русский
    'доллар': 'USD', 'долларов': 'USD', 'баксов': 'USD', 'долл': 'USD',
    'евро': 'EUR',
    'рубль': 'RUB', 'рублей': 'RUB', 'руб': 'RUB',
    'дирхам': 'AED', 'дирхамов': 'AED',
    'тенге': 'KZT',
    'юсдт': 'USDT', 'тезер': 'USDT',

    # Английский
    'dollar': 'USD', 'dollars': 'USD', 'usd': 'USD',
    'euro': 'EUR', 'eur': 'EUR',
    'ruble': 'RUB', 'rubles': 'RUB', 'rub': 'RUB',
    'dirham': 'AED', 'dirhams': 'AED', 'aed': 'AED',
    'usdt': 'USDT', 'tether': 'USDT',
    'kzt': 'KZT',

    # Арабский
    'درهم': 'AED',
    'دولار': 'USD',
    'يورو': 'EUR',
    'روبل': 'RUB',
}

# Типичные курсы валют (для валидации)
TYPICAL_RATES = {
    ('USD', 'AED'): (3.65, 3.70),
    ('EUR', 'AED'): (3.95, 4.20),
    ('RUB', 'AED'): (0.035, 0.050),
    ('KZT', 'AED'): (0.007, 0.010),
    ('USD', 'RUB'): (85.0, 105.0),
    ('EUR', 'RUB'): (95.0, 115.0),
}

# Regex паттерны
PATTERNS = {
    # Цены
    'price_with_currency': re.compile(
        r'(\d+(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*'
        r'(AED|USD|EUR|RUB|KZT|USDT|\$|€|₽|₸|'
        r'долл(?:ар(?:ов)?)?|руб(?:лей|ль)?|дирхам(?:ов)?|евро|тенге|درهم|دولار)',
        re.IGNORECASE
    ),
    'currency_with_price': re.compile(
        r'(AED|USD|EUR|RUB|\$|€|₽|د\.إ)\s*(\d+(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)',
        re.IGNORECASE
    ),
    'price_per_unit': re.compile(
        r'(\d+(?:[\s,]\d{3})*)\s*(AED|USD|\$|дирхам|руб)\s*'
        r'(?:за|per|/)\s*(чел(?:овек)?|pax|человека|группу|group|машину|car)',
        re.IGNORECASE
    ),

    # Скидки
    'discount_percent': re.compile(
        r'(?:скидка|discount|минус|-)[\s:]*(\d+)[\s]*%',
        re.IGNORECASE
    ),
    'discount_fixed': re.compile(
        r'(?:скидка|discount|минус)[\s:]*(\d+(?:[\s,]\d{3})*)\s*'
        r'(AED|USD|\$|руб|дирхам)?',
        re.IGNORECASE
    ),
    'special_price': re.compile(
        r'(?:специальн\w+\s+цен\w+|special\s+price|промо|promo)[\s:]*'
        r'(\d+(?:[\s,]\d{3})*)',
        re.IGNORECASE
    ),
    'conditional_discount': re.compile(
        r'(?:при|if|от)\s+(\d+)\s+(?:чел|pax|человек)\s+'
        r'(?:скидка|discount|-)?[\s]*(\d+)\s*%?',
        re.IGNORECASE
    ),

    # Оплаты
    'payment_fact': re.compile(
        r'(?:оплатил\w*|оплачено|paid|перев[её]л\w*|'
        r'получил\w*\s+оплату|внес\w*|deposited)[\s:]*'
        r'(\d+(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)\s*'
        r'(AED|USD|\$|€|₽|руб|дирхам)?',
        re.IGNORECASE
    ),
    'payment_method': re.compile(
        r'(?:на\s+карту|card|cash|наличн\w+|переводом|банк\w*|'
        r'USDT|крипт\w+|сбер\w*|тиньк\w*)',
        re.IGNORECASE
    ),
    'prepayment': re.compile(
        r'(?:предоплата|аванс|deposit|частичн\w+\s+оплат\w*)[\s:]*'
        r'(\d+(?:[\s,]\d{3})*)\s*(%|AED|USD|\$|руб)?',
        re.IGNORECASE
    ),
    'remaining': re.compile(
        r'(?:остаток|осталось|balance|доплата)[\s:]*'
        r'(\d+(?:[\s,]\d{3})*)\s*(AED|USD|\$|руб)?',
        re.IGNORECASE
    ),

    # Комиссии
    'commission_percent': re.compile(
        r'(?:комисс\w+|commission|ваш\w*\s*%|агентск\w+)[\s:]*(\d+)[\s]*%',
        re.IGNORECASE
    ),
    'net_gross': re.compile(
        r'(?:нетто|net|netto)[\s:]*(\d+(?:[\s,]\d{3})*).*?'
        r'(?:брутто|gross)[\s:]*(\d+(?:[\s,]\d{3})*)',
        re.IGNORECASE | re.DOTALL
    ),
    'gross_net': re.compile(
        r'(?:брутто|gross)[\s:]*(\d+(?:[\s,]\d{3})*).*?'
        r'(?:нетто|net|netto)[\s:]*(\d+(?:[\s,]\d{3})*)',
        re.IGNORECASE | re.DOTALL
    ),
    'agent_fee': re.compile(
        r'(?:ваш\w*|агентск\w+)[\s:]*(\d+(?:[\s,]\d{3})*)\s*'
        r'(AED|USD|\$|руб)?',
        re.IGNORECASE
    ),

    # Валютные операции
    'exchange_rate': re.compile(
        r'(?:курс|rate|по курсу)[\s:]*(\d+(?:[.,]\d+)?)',
        re.IGNORECASE
    ),
    'currency_pair': re.compile(
        r'(USD|EUR|RUB|AED|\$|€|₽)[\s/]*(AED|RUB|USD|руб|дирхам)[\s:=]*'
        r'(\d+(?:[.,]\d+)?)',
        re.IGNORECASE
    ),
    'conversion': re.compile(
        r'(\d+(?:[\s,]\d{3})*)\s*(USD|\$|AED|EUR)\s*[=~≈]\s*'
        r'(\d+(?:[\s,]\d{3})*(?:[.,]\d+)?)\s*(AED|RUB|руб)',
        re.IGNORECASE
    ),

    # Дебиторка
    'unpaid': re.compile(
        r'(?:не\s*оплач\w+|pending\s+payment|ожидает\s+оплат\w+|долг)',
        re.IGNORECASE
    ),
    'reminder': re.compile(
        r'(?:напомн\w+|remind|когда\s+оплат\w+|жд[её]м\s+оплат\w+)',
        re.IGNORECASE
    ),
    'overdue': re.compile(
        r'(?:просроч\w+|overdue|задерж\w+\s+оплат\w+)',
        re.IGNORECASE
    ),
}


# ===================================================================
# КЛАССЫ ДАННЫХ
# ===================================================================

@dataclass
class PriceExtraction:
    """Извлечённая цена."""
    amount: float
    currency: str
    unit: Optional[str]  # per person, per group, etc.
    original_text: str
    confidence: float


@dataclass
class DiscountExtraction:
    """Извлечённая скидка."""
    discount_type: str  # percentage, fixed, conditional
    value: float
    currency: Optional[str]
    condition: Optional[str]
    original_text: str


@dataclass
class PaymentExtraction:
    """Извлечённая оплата."""
    amount: float
    currency: Optional[str]
    payment_type: str  # full, partial, deposit, remaining
    method: Optional[str]  # card, cash, crypto, bank
    original_text: str


@dataclass
class CommissionExtraction:
    """Извлечённая комиссия."""
    commission_type: str  # percentage, fixed, net_gross
    rate: Optional[float]  # процент
    net_price: Optional[float]
    gross_price: Optional[float]
    commission_amount: Optional[float]
    currency: Optional[str]
    original_text: str


@dataclass
class ExchangeRateExtraction:
    """Извлечённый курс обмена."""
    from_currency: str
    to_currency: str
    rate: float
    original_amount: Optional[float]
    converted_amount: Optional[float]
    original_text: str


@dataclass
class FinancialMessage:
    """Финансовые данные из сообщения."""
    message_id: Optional[str]
    jid: str
    timestamp: Optional[str]
    text: str
    prices: List[Dict]
    discounts: List[Dict]
    payments: List[Dict]
    commissions: List[Dict]
    exchange_rates: List[Dict]
    has_unpaid_mention: bool
    has_reminder: bool
    has_overdue: bool


# ===================================================================
# ФУНКЦИИ ИЗВЛЕЧЕНИЯ
# ===================================================================

def parse_amount(amount_str: str) -> float:
    """Парсит строку суммы в число."""
    # Убираем пробелы и запятые как разделители тысяч
    cleaned = re.sub(r'[\s,]', '', amount_str)
    # Заменяем запятую на точку для десятичных
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def normalize_currency(currency_str: str) -> str:
    """Нормализует название валюты в код."""
    if not currency_str:
        return 'UNKNOWN'

    currency_str = currency_str.strip().lower()

    # Проверяем символы
    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in currency_str:
            return code

    # Проверяем названия
    for name, code in CURRENCY_NAMES.items():
        if name in currency_str:
            return code

    # Проверяем коды валют
    upper = currency_str.upper()
    if upper in ['USD', 'EUR', 'AED', 'RUB', 'KZT', 'USDT', 'GBP', 'SAR']:
        return upper

    return 'UNKNOWN'


def extract_prices(text: str) -> List[PriceExtraction]:
    """Извлекает цены из текста."""
    prices = []

    # Паттерн: сумма + валюта
    for match in PATTERNS['price_with_currency'].finditer(text):
        amount = parse_amount(match.group(1))
        currency = normalize_currency(match.group(2))

        if amount > 0:
            prices.append(PriceExtraction(
                amount=amount,
                currency=currency,
                unit=None,
                original_text=match.group(0),
                confidence=0.9
            ))

    # Паттерн: валюта + сумма
    for match in PATTERNS['currency_with_price'].finditer(text):
        currency = normalize_currency(match.group(1))
        amount = parse_amount(match.group(2))

        if amount > 0:
            # Проверяем, не дубликат ли
            is_dup = any(
                p.amount == amount and p.currency == currency
                for p in prices
            )
            if not is_dup:
                prices.append(PriceExtraction(
                    amount=amount,
                    currency=currency,
                    unit=None,
                    original_text=match.group(0),
                    confidence=0.9
                ))

    # Паттерн: цена за единицу
    for match in PATTERNS['price_per_unit'].finditer(text):
        amount = parse_amount(match.group(1))
        currency = normalize_currency(match.group(2))
        unit = match.group(3).lower()

        # Нормализуем unit
        if unit in ['чел', 'человек', 'человека', 'pax']:
            unit = 'person'
        elif unit in ['группу', 'group']:
            unit = 'group'
        elif unit in ['машину', 'car']:
            unit = 'vehicle'

        if amount > 0:
            prices.append(PriceExtraction(
                amount=amount,
                currency=currency,
                unit=unit,
                original_text=match.group(0),
                confidence=0.95
            ))

    return prices


def extract_discounts(text: str) -> List[DiscountExtraction]:
    """Извлекает скидки из текста."""
    discounts = []

    # Процентные скидки
    for match in PATTERNS['discount_percent'].finditer(text):
        value = float(match.group(1))
        if 0 < value <= 100:
            discounts.append(DiscountExtraction(
                discount_type='percentage',
                value=value,
                currency=None,
                condition=None,
                original_text=match.group(0)
            ))

    # Фиксированные скидки
    for match in PATTERNS['discount_fixed'].finditer(text):
        value = parse_amount(match.group(1))
        currency = normalize_currency(match.group(2)) if match.group(2) else None

        if value > 0:
            discounts.append(DiscountExtraction(
                discount_type='fixed',
                value=value,
                currency=currency,
                condition=None,
                original_text=match.group(0)
            ))

    # Условные скидки
    for match in PATTERNS['conditional_discount'].finditer(text):
        min_pax = int(match.group(1))
        discount_value = float(match.group(2))

        discounts.append(DiscountExtraction(
            discount_type='conditional',
            value=discount_value,
            currency=None,
            condition=f'from {min_pax} pax',
            original_text=match.group(0)
        ))

    # Специальные цены
    for match in PATTERNS['special_price'].finditer(text):
        value = parse_amount(match.group(1))
        if value > 0:
            discounts.append(DiscountExtraction(
                discount_type='special_price',
                value=value,
                currency=None,
                condition='promo',
                original_text=match.group(0)
            ))

    return discounts


def extract_payments(text: str) -> List[PaymentExtraction]:
    """Извлекает информацию об оплатах."""
    payments = []

    # Факт оплаты
    for match in PATTERNS['payment_fact'].finditer(text):
        amount = parse_amount(match.group(1))
        currency = normalize_currency(match.group(2)) if match.group(2) else None

        # Определяем метод оплаты
        method = None
        method_match = PATTERNS['payment_method'].search(text)
        if method_match:
            method_text = method_match.group(0).lower()
            if 'карт' in method_text or 'card' in method_text:
                method = 'card'
            elif 'наличн' in method_text or 'cash' in method_text:
                method = 'cash'
            elif 'usdt' in method_text or 'крипт' in method_text:
                method = 'crypto'
            elif 'сбер' in method_text or 'тиньк' in method_text or 'банк' in method_text:
                method = 'bank_transfer'

        if amount > 0:
            payments.append(PaymentExtraction(
                amount=amount,
                currency=currency,
                payment_type='full',
                method=method,
                original_text=match.group(0)
            ))

    # Предоплата
    for match in PATTERNS['prepayment'].finditer(text):
        amount = parse_amount(match.group(1))
        unit = match.group(2) if match.group(2) else None

        payment_type = 'deposit'
        currency = None

        if unit == '%':
            # Это процент предоплаты
            payment_type = f'deposit_{int(amount)}%'
            amount = 0  # Реальную сумму не знаем
        else:
            currency = normalize_currency(unit) if unit else None

        payments.append(PaymentExtraction(
            amount=amount,
            currency=currency,
            payment_type=payment_type,
            method=None,
            original_text=match.group(0)
        ))

    # Остаток
    for match in PATTERNS['remaining'].finditer(text):
        amount = parse_amount(match.group(1))
        currency = normalize_currency(match.group(2)) if match.group(2) else None

        if amount > 0:
            payments.append(PaymentExtraction(
                amount=amount,
                currency=currency,
                payment_type='remaining',
                method=None,
                original_text=match.group(0)
            ))

    return payments


def extract_commissions(text: str) -> List[CommissionExtraction]:
    """Извлекает информацию о комиссиях."""
    commissions = []

    # Процент комиссии
    for match in PATTERNS['commission_percent'].finditer(text):
        rate = float(match.group(1))
        if 0 < rate <= 50:  # Разумный диапазон комиссий
            commissions.append(CommissionExtraction(
                commission_type='percentage',
                rate=rate,
                net_price=None,
                gross_price=None,
                commission_amount=None,
                currency=None,
                original_text=match.group(0)
            ))

    # Нетто/Брутто
    for match in PATTERNS['net_gross'].finditer(text):
        net = parse_amount(match.group(1))
        gross = parse_amount(match.group(2))

        if net > 0 and gross > 0 and gross > net:
            commission_amount = gross - net
            rate = (commission_amount / gross) * 100

            commissions.append(CommissionExtraction(
                commission_type='net_gross',
                rate=round(rate, 2),
                net_price=net,
                gross_price=gross,
                commission_amount=commission_amount,
                currency=None,  # Определяем из контекста если нужно
                original_text=match.group(0)
            ))

    for match in PATTERNS['gross_net'].finditer(text):
        gross = parse_amount(match.group(1))
        net = parse_amount(match.group(2))

        if net > 0 and gross > 0 and gross > net:
            commission_amount = gross - net
            rate = (commission_amount / gross) * 100

            commissions.append(CommissionExtraction(
                commission_type='net_gross',
                rate=round(rate, 2),
                net_price=net,
                gross_price=gross,
                commission_amount=commission_amount,
                currency=None,
                original_text=match.group(0)
            ))

    # Фиксированная комиссия агента
    for match in PATTERNS['agent_fee'].finditer(text):
        amount = parse_amount(match.group(1))
        currency = normalize_currency(match.group(2)) if match.group(2) else None

        if amount > 0:
            commissions.append(CommissionExtraction(
                commission_type='fixed',
                rate=None,
                net_price=None,
                gross_price=None,
                commission_amount=amount,
                currency=currency,
                original_text=match.group(0)
            ))

    return commissions


def extract_exchange_rates(text: str) -> List[ExchangeRateExtraction]:
    """Извлекает курсы обмена валют."""
    rates = []

    # Прямой курс
    for match in PATTERNS['exchange_rate'].finditer(text):
        rate = float(match.group(1).replace(',', '.'))

        # Пытаемся определить валюты из контекста
        from_curr = 'USD'  # По умолчанию
        to_curr = 'AED'

        if 'руб' in text.lower() or 'rub' in text.lower():
            to_curr = 'RUB'
        if 'дирхам' in text.lower() or 'aed' in text.lower():
            to_curr = 'AED'

        rates.append(ExchangeRateExtraction(
            from_currency=from_curr,
            to_currency=to_curr,
            rate=rate,
            original_amount=None,
            converted_amount=None,
            original_text=match.group(0)
        ))

    # Валютная пара с курсом
    for match in PATTERNS['currency_pair'].finditer(text):
        from_curr = normalize_currency(match.group(1))
        to_curr = normalize_currency(match.group(2))
        rate = float(match.group(3).replace(',', '.'))

        rates.append(ExchangeRateExtraction(
            from_currency=from_curr,
            to_currency=to_curr,
            rate=rate,
            original_amount=None,
            converted_amount=None,
            original_text=match.group(0)
        ))

    # Конверсия
    for match in PATTERNS['conversion'].finditer(text):
        orig_amount = parse_amount(match.group(1))
        from_curr = normalize_currency(match.group(2))
        conv_amount = parse_amount(match.group(3))
        to_curr = normalize_currency(match.group(4))

        if orig_amount > 0 and conv_amount > 0:
            rate = conv_amount / orig_amount

            rates.append(ExchangeRateExtraction(
                from_currency=from_curr,
                to_currency=to_curr,
                rate=round(rate, 4),
                original_amount=orig_amount,
                converted_amount=conv_amount,
                original_text=match.group(0)
            ))

    return rates


def check_debt_indicators(text: str) -> Tuple[bool, bool, bool]:
    """Проверяет индикаторы дебиторки."""
    has_unpaid = bool(PATTERNS['unpaid'].search(text))
    has_reminder = bool(PATTERNS['reminder'].search(text))
    has_overdue = bool(PATTERNS['overdue'].search(text))
    return has_unpaid, has_reminder, has_overdue


# ===================================================================
# КЛАСС АНАЛИЗАТОРА
# ===================================================================

class FinancialAnalyzer:
    """Анализатор финансовых данных в сообщениях."""

    def __init__(self):
        self.financial_messages = []

        # Статистика
        self.stats = {
            'total_messages': 0,
            'messages_with_prices': 0,
            'messages_with_discounts': 0,
            'messages_with_payments': 0,
            'messages_with_commissions': 0,
            'messages_with_exchange_rates': 0,
            'messages_with_debt_indicators': 0,
            'currencies_found': Counter(),
            'total_prices_extracted': 0,
            'total_payments_extracted': 0,
        }

        # Агрегация по контактам
        self.contacts_financials = defaultdict(lambda: {
            'jid': None,
            'name': None,
            'total_prices': [],
            'total_payments': [],
            'currencies_used': Counter(),
            'has_debt_mentions': False,
            'message_count': 0,
        })

    def process_message(self, msg: Dict[str, Any]):
        """Обрабатывает одно сообщение."""
        jid = msg.get('jid') or msg.get('chat_jid') or msg.get('contact_jid')
        if not jid:
            return

        text = msg.get('text') or msg.get('message') or msg.get('content')
        if not text:
            return

        self.stats['total_messages'] += 1

        # Извлекаем все финансовые данные
        prices = extract_prices(text)
        discounts = extract_discounts(text)
        payments = extract_payments(text)
        commissions = extract_commissions(text)
        exchange_rates = extract_exchange_rates(text)
        has_unpaid, has_reminder, has_overdue = check_debt_indicators(text)

        # Проверяем, есть ли финансовые данные
        has_financial_data = (
            prices or discounts or payments or commissions or
            exchange_rates or has_unpaid or has_reminder or has_overdue
        )

        if not has_financial_data:
            return

        # Обновляем статистику
        if prices:
            self.stats['messages_with_prices'] += 1
            self.stats['total_prices_extracted'] += len(prices)
            for p in prices:
                self.stats['currencies_found'][p.currency] += 1

        if discounts:
            self.stats['messages_with_discounts'] += 1

        if payments:
            self.stats['messages_with_payments'] += 1
            self.stats['total_payments_extracted'] += len(payments)

        if commissions:
            self.stats['messages_with_commissions'] += 1

        if exchange_rates:
            self.stats['messages_with_exchange_rates'] += 1

        if has_unpaid or has_reminder or has_overdue:
            self.stats['messages_with_debt_indicators'] += 1

        # Создаём запись
        fin_msg = FinancialMessage(
            message_id=msg.get('message_id'),
            jid=jid,
            timestamp=msg.get('timestamp') or msg.get('date'),
            text=text[:500] + '...' if len(text) > 500 else text,
            prices=[asdict(p) for p in prices],
            discounts=[asdict(d) for d in discounts],
            payments=[asdict(p) for p in payments],
            commissions=[asdict(c) for c in commissions],
            exchange_rates=[asdict(r) for r in exchange_rates],
            has_unpaid_mention=has_unpaid,
            has_reminder=has_reminder,
            has_overdue=has_overdue,
        )

        self.financial_messages.append(asdict(fin_msg))

        # Обновляем данные контакта
        contact_data = self.contacts_financials[jid]
        contact_data['jid'] = jid
        contact_data['message_count'] += 1

        name = msg.get('name') or msg.get('chat_name')
        if name and not contact_data['name']:
            contact_data['name'] = name

        for p in prices:
            contact_data['total_prices'].append({
                'amount': p.amount,
                'currency': p.currency
            })
            contact_data['currencies_used'][p.currency] += 1

        for p in payments:
            if p.amount > 0:
                contact_data['total_payments'].append({
                    'amount': p.amount,
                    'currency': p.currency,
                    'type': p.payment_type
                })

        if has_unpaid or has_reminder or has_overdue:
            contact_data['has_debt_mentions'] = True

    def build_contacts_summary(self) -> List[Dict]:
        """Создаёт сводку по контактам."""
        summaries = []

        for jid, data in self.contacts_financials.items():
            if data['message_count'] == 0:
                continue

            # Суммируем по валютам
            totals_by_currency = defaultdict(float)
            for p in data['total_prices']:
                totals_by_currency[p['currency']] += p['amount']

            payments_by_currency = defaultdict(float)
            for p in data['total_payments']:
                if p['currency']:
                    payments_by_currency[p['currency']] += p['amount']

            summaries.append({
                'jid': jid,
                'name': data['name'] or jid.split('@')[0],
                'financial_messages_count': data['message_count'],
                'currencies_used': dict(data['currencies_used']),
                'total_mentioned_amounts': dict(totals_by_currency),
                'total_payments_recorded': dict(payments_by_currency),
                'has_debt_mentions': data['has_debt_mentions'],
            })

        # Сортируем по количеству финансовых сообщений
        summaries.sort(key=lambda x: x['financial_messages_count'], reverse=True)

        return summaries

    def build_metadata(self) -> Dict:
        """Создаёт метаданные анализа."""
        return {
            'total_messages_analyzed': self.stats['total_messages'],
            'messages_with_financial_data': len(self.financial_messages),
            'messages_with_prices': self.stats['messages_with_prices'],
            'messages_with_discounts': self.stats['messages_with_discounts'],
            'messages_with_payments': self.stats['messages_with_payments'],
            'messages_with_commissions': self.stats['messages_with_commissions'],
            'messages_with_exchange_rates': self.stats['messages_with_exchange_rates'],
            'messages_with_debt_indicators': self.stats['messages_with_debt_indicators'],
            'total_prices_extracted': self.stats['total_prices_extracted'],
            'total_payments_extracted': self.stats['total_payments_extracted'],
            'currencies_found': dict(self.stats['currencies_found']),
            'contacts_with_financials': len(self.contacts_financials),
            'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        }


# ===================================================================
# MAIN
# ===================================================================

def main():
    """Основная функция."""
    print("=" * 60)
    print("Парсинг финансовых данных из сообщений WhatsApp")
    print("=" * 60)

    # Создаём директории
    ensure_directories()

    # Проверяем входной файл
    if not INPUT_FILE.exists():
        print(f"\n[ОШИБКА] Входной файл не найден: {INPUT_FILE}")
        print("\nСначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    print(f"\nВходной файл: {INPUT_FILE}")
    print(f"Выходной файл: {OUTPUT_FILE}")

    # Создаём анализатор
    analyzer = FinancialAnalyzer()

    # Читаем и обрабатываем JSONL
    print("\n[1/3] Извлечение финансовых данных...")
    line_count = 0
    error_count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            if line_count % 100000 == 0:
                print(f"  Обработано строк: {line_count:,}")

            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
                analyzer.process_message(msg)
            except json.JSONDecodeError as e:
                error_count += 1
                if error_count <= 5:
                    print(f"  [Ошибка JSON] Строка {line_count}: {e}")

    print(f"  Всего строк: {line_count:,}")
    if error_count:
        print(f"  Ошибок парсинга: {error_count}")

    # Создаём сводку по контактам
    print("\n[2/3] Создание сводки по контактам...")
    contacts_summary = analyzer.build_contacts_summary()
    print(f"  Контактов с финансами: {len(contacts_summary):,}")

    # Метаданные
    metadata = analyzer.build_metadata()

    # Формируем выходные данные
    output_data = {
        'financial_messages': analyzer.financial_messages[:10000],  # Ограничиваем для размера файла
        'contacts_summary': contacts_summary,
        'metadata': metadata,
    }

    # Сохраняем
    print("\n[3/3] Сохранение результата...")
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  Сохранено: {OUTPUT_FILE}")

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Всего сообщений проанализировано: {metadata['total_messages_analyzed']:,}")
    print(f"Сообщений с финансовыми данными: {metadata['messages_with_financial_data']:,}")
    print(f"\nДетализация:")
    print(f"  - С ценами: {metadata['messages_with_prices']:,}")
    print(f"  - Со скидками: {metadata['messages_with_discounts']:,}")
    print(f"  - С оплатами: {metadata['messages_with_payments']:,}")
    print(f"  - С комиссиями: {metadata['messages_with_commissions']:,}")
    print(f"  - С курсами валют: {metadata['messages_with_exchange_rates']:,}")
    print(f"  - С упоминанием долгов: {metadata['messages_with_debt_indicators']:,}")
    print(f"\nВсего извлечено цен: {metadata['total_prices_extracted']:,}")
    print(f"Всего извлечено оплат: {metadata['total_payments_extracted']:,}")
    print(f"\nВалюты (по частоте упоминаний):")
    for currency, count in sorted(metadata['currencies_found'].items(), key=lambda x: -x[1]):
        print(f"  - {currency}: {count:,}")
    print(f"\nКонтактов с финансовой активностью: {metadata['contacts_with_financials']:,}")

    print("\n" + "=" * 60)
    print("Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
