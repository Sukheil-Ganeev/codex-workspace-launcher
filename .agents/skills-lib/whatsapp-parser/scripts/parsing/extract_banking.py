#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенное извлечение банковских реквизитов из чатов WhatsApp.

Функции:
- Извлечение IBAN (международный формат, все страны)
- Извлечение номеров карт (полных и маскированных)
- Извлечение SWIFT/BIC кодов
- Извлечение номеров счетов (RU, UAE, EU)
- Валидация IBAN checksum (ISO 13616)
- Валидация карт по алгоритму Luhn
- Определение банка по BIN и IBAN
- Маскирование в логах
- Шифрование при сохранении (опционально, Fernet)
- Связь с контактами (чьи реквизиты)
- Экспорт: JSON (зашифрованный опционально), Markdown

Автор: Claude Code
Версия: 2.0
"""

import sys
import os
import re
import json
import glob
import argparse
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any

sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import CHATS_DIR, CONTACT_TYPES, JSON_DIR
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]
    JSON_DIR = CHATS_DIR / "_база" / "json"

sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════════════
# БАЗА BIN КОДОВ (первые 6 цифр карты -> банк)
# ═══════════════════════════════════════════════════════════════════════

BIN_DATABASE = {
    # Россия - Сбербанк
    "427683": {"bank": "Сбербанк", "country": "RU", "type": "Visa"},
    "427644": {"bank": "Сбербанк", "country": "RU", "type": "Visa"},
    "427601": {"bank": "Сбербанк", "country": "RU", "type": "Visa"},
    "427631": {"bank": "Сбербанк", "country": "RU", "type": "Visa"},
    "427901": {"bank": "Сбербанк", "country": "RU", "type": "Visa"},
    "546901": {"bank": "Сбербанк", "country": "RU", "type": "MasterCard"},
    "546925": {"bank": "Сбербанк", "country": "RU", "type": "MasterCard"},
    "220220": {"bank": "Сбербанк", "country": "RU", "type": "МИР"},

    # Россия - Тинькофф
    "437773": {"bank": "Тинькофф", "country": "RU", "type": "Visa"},
    "521324": {"bank": "Тинькофф", "country": "RU", "type": "MasterCard"},
    "553691": {"bank": "Тинькофф", "country": "RU", "type": "MasterCard"},
    "220070": {"bank": "Тинькофф", "country": "RU", "type": "МИР"},

    # Россия - Альфа-Банк
    "415428": {"bank": "Альфа-Банк", "country": "RU", "type": "Visa"},
    "477964": {"bank": "Альфа-Банк", "country": "RU", "type": "Visa"},
    "548673": {"bank": "Альфа-Банк", "country": "RU", "type": "MasterCard"},
    "548601": {"bank": "Альфа-Банк", "country": "RU", "type": "MasterCard"},

    # Россия - ВТБ
    "427229": {"bank": "ВТБ", "country": "RU", "type": "Visa"},
    "447520": {"bank": "ВТБ", "country": "RU", "type": "Visa"},
    "524468": {"bank": "ВТБ", "country": "RU", "type": "MasterCard"},

    # Россия - Газпромбанк
    "461919": {"bank": "Газпромбанк", "country": "RU", "type": "Visa"},

    # Россия - Райффайзен
    "462729": {"bank": "Райффайзен", "country": "RU", "type": "Visa"},
    "462730": {"bank": "Райффайзен", "country": "RU", "type": "Visa"},

    # ОАЭ - Emirates NBD
    "428178": {"bank": "Emirates NBD", "country": "AE", "type": "Visa"},
    "489458": {"bank": "Emirates NBD", "country": "AE", "type": "Visa"},

    # ОАЭ - ADIB
    "418388": {"bank": "ADIB", "country": "AE", "type": "Visa"},
    "422817": {"bank": "ADIB", "country": "AE", "type": "Visa"},

    # ОАЭ - Mashreq
    "429689": {"bank": "Mashreq Bank", "country": "AE", "type": "Visa"},

    # ОАЭ - FAB
    "405660": {"bank": "First Abu Dhabi Bank", "country": "AE", "type": "Visa"},

    # ОАЭ - RAK Bank
    "428930": {"bank": "RAK Bank", "country": "AE", "type": "Visa"},

    # Казахстан - Kaspi
    "440563": {"bank": "Kaspi Bank", "country": "KZ", "type": "Visa"},
    "400629": {"bank": "Kaspi Bank", "country": "KZ", "type": "Visa"},
    "517792": {"bank": "Kaspi Bank", "country": "KZ", "type": "MasterCard"},

    # Казахстан - Халык
    "417790": {"bank": "Halyk Bank", "country": "KZ", "type": "Visa"},
}


# ═══════════════════════════════════════════════════════════════════════
# БАЗА IBAN КОДОВ БАНКОВ (по странам)
# ═══════════════════════════════════════════════════════════════════════

IBAN_BANK_CODES = {
    "AE": {
        # Формат IBAN ОАЭ: AE + 2 контрольных + 3 код банка + 16 номер счёта
        "033": "Emirates NBD",
        "030": "Abu Dhabi Commercial Bank (ADCB)",
        "035": "First Abu Dhabi Bank (FAB)",
        "038": "ADIB (Abu Dhabi Islamic Bank)",
        "040": "Mashreq Bank",
        "046": "Commercial Bank of Dubai",
        "050": "Dubai Islamic Bank",
        "060": "RAK Bank",
        "070": "National Bank of Fujairah",
    },
    "RU": {
        # БИК код банка (первые 3 цифры после 04)
        "4525": "Сбербанк (Москва)",
        "4452": "Сбербанк",
        "4493": "Альфа-Банк",
        "4501": "ВТБ",
        "4525": "Газпромбанк",
        "4474": "Тинькофф",
        "4442": "Райффайзен",
    },
    "KZ": {
        "722": "Kaspi Bank",
        "319": "Halyk Bank",
        "551": "Forte Bank",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# ДЛИНЫ IBAN ПО СТРАНАМ
# ═══════════════════════════════════════════════════════════════════════

IBAN_LENGTHS = {
    "AL": 28, "AD": 24, "AT": 20, "AZ": 28, "BH": 22, "BY": 28, "BE": 16,
    "BA": 20, "BR": 29, "BG": 22, "CR": 22, "HR": 21, "CY": 28, "CZ": 24,
    "DK": 18, "DO": 28, "EE": 20, "EG": 29, "FO": 18, "FI": 18, "FR": 27,
    "GE": 22, "DE": 22, "GI": 23, "GR": 27, "GL": 18, "GT": 28, "HU": 28,
    "IS": 26, "IQ": 23, "IE": 22, "IL": 23, "IT": 27, "JO": 30, "KZ": 20,
    "XK": 20, "KW": 30, "LV": 21, "LB": 28, "LI": 21, "LT": 20, "LU": 20,
    "MK": 19, "MT": 31, "MR": 27, "MU": 30, "MD": 24, "MC": 27, "ME": 22,
    "NL": 18, "NO": 15, "PK": 24, "PS": 29, "PL": 28, "PT": 25, "QA": 29,
    "RO": 24, "LC": 32, "SM": 27, "ST": 25, "SA": 24, "RS": 22, "SC": 31,
    "SK": 24, "SI": 19, "ES": 24, "SE": 24, "CH": 21, "TL": 23, "TN": 24,
    "TR": 26, "UA": 29, "AE": 23, "GB": 22, "VA": 22, "VG": 24,
}


# ═══════════════════════════════════════════════════════════════════════
# АЛГОРИТМЫ ВАЛИДАЦИИ
# ═══════════════════════════════════════════════════════════════════════

def luhn_checksum(card_number: str) -> bool:
    """
    Проверка номера карты по алгоритму Luhn (ISO/IEC 7812).

    Возвращает True если номер карты валиден.
    """
    # Убираем все кроме цифр
    digits = re.sub(r'\D', '', card_number)

    if not digits or len(digits) < 13 or len(digits) > 19:
        return False

    def digits_of(n):
        return [int(d) for d in str(n)]

    digits_list = digits_of(digits)
    odd_digits = digits_list[-1::-2]
    even_digits = digits_list[-2::-2]

    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))

    return checksum % 10 == 0


def validate_iban(iban: str) -> Tuple[bool, str]:
    """
    Проверка IBAN по стандарту ISO 13616.

    Возвращает (is_valid, error_message).
    """
    # Убираем пробелы и приводим к верхнему регистру
    iban = re.sub(r'\s', '', iban).upper()

    # Проверка формата
    if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
        return False, "Неверный формат IBAN"

    country_code = iban[:2]

    # Проверка длины по стране
    expected_length = IBAN_LENGTHS.get(country_code)
    if expected_length and len(iban) != expected_length:
        return False, f"Неверная длина IBAN для {country_code}: ожидается {expected_length}, получено {len(iban)}"

    # Проверка контрольной суммы (mod 97)
    rearranged = iban[4:] + iban[:4]

    # Преобразуем буквы в числа (A=10, B=11, ..., Z=35)
    numeric = ''
    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - ord('A') + 10)

    if int(numeric) % 97 != 1:
        return False, "Неверная контрольная сумма IBAN"

    return True, "OK"


def get_bank_from_bin(card_number: str) -> Optional[Dict]:
    """
    Определить банк по BIN (первые 6 цифр карты).
    """
    digits = re.sub(r'\D', '', card_number)
    if len(digits) < 6:
        return None

    bin_code = digits[:6]
    return BIN_DATABASE.get(bin_code)


def get_bank_from_iban(iban: str) -> Optional[str]:
    """
    Определить банк по коду в IBAN.
    """
    iban = re.sub(r'\s', '', iban).upper()

    if len(iban) < 7:
        return None

    country_code = iban[:2]

    if country_code == "AE" and len(iban) >= 7:
        # ОАЭ: позиции 4-6 - код банка
        bank_code = iban[4:7]
        banks = IBAN_BANK_CODES.get("AE", {})
        return banks.get(bank_code)

    return None


# ═══════════════════════════════════════════════════════════════════════
# МАСКИРОВАНИЕ ДЛЯ ЛОГОВ
# ═══════════════════════════════════════════════════════════════════════

def mask_card(card: str) -> str:
    """Маскировать номер карты для логов: 4276****9012"""
    digits = re.sub(r'\D', '', card)
    if len(digits) >= 12:
        return digits[:4] + '****' + digits[-4:]
    return '****'


def mask_iban(iban: str) -> str:
    """Маскировать IBAN для логов: AE72***584"""
    clean = re.sub(r'\s', '', iban)
    if len(clean) >= 8:
        return clean[:4] + '***' + clean[-4:]
    return '****'


def mask_account(account: str) -> str:
    """Маскировать номер счёта для логов: 408***5678"""
    digits = re.sub(r'\D', '', account)
    if len(digits) >= 8:
        return digits[:4] + '***' + digits[-4:]
    return '****'


# ═══════════════════════════════════════════════════════════════════════
# ШИФРОВАНИЕ (ОПЦИОНАЛЬНО)
# ═══════════════════════════════════════════════════════════════════════

class SimpleCrypto:
    """
    Простое шифрование для хранения реквизитов.
    Использует Fernet (AES-128-CBC) если доступен cryptography,
    иначе простой XOR с base64.
    """

    def __init__(self, password: str):
        self.password = password
        self._fernet = None

        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'banking_salt_2024',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self._fernet = Fernet(key)
            self.method = "fernet"
        except ImportError:
            self.method = "xor"

    def encrypt(self, data: str) -> str:
        """Зашифровать строку."""
        if self._fernet:
            return self._fernet.encrypt(data.encode()).decode()
        else:
            # Простой XOR как fallback
            key_bytes = hashlib.sha256(self.password.encode()).digest()
            data_bytes = data.encode('utf-8')
            encrypted = bytes(a ^ key_bytes[i % len(key_bytes)]
                            for i, a in enumerate(data_bytes))
            return base64.b64encode(encrypted).decode()

    def decrypt(self, data: str) -> str:
        """Расшифровать строку."""
        if self._fernet:
            return self._fernet.decrypt(data.encode()).decode()
        else:
            key_bytes = hashlib.sha256(self.password.encode()).digest()
            encrypted = base64.b64decode(data.encode())
            decrypted = bytes(a ^ key_bytes[i % len(key_bytes)]
                            for i, a in enumerate(encrypted))
            return decrypted.decode('utf-8')


# ═══════════════════════════════════════════════════════════════════════
# РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════

PATTERNS = {
    # IBAN - международный формат (все страны)
    'iban': r'\b([A-Z]{2}\d{2}[A-Z0-9]{4,30})\b',

    # Номера карт (полные, 13-19 цифр)
    'card_full': r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b',
    'card_full_13': r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{1,4})\b',

    # Маскированные карты (XXXX-XXXX-XXXX-1234 или ****1234)
    'card_masked': r'\b([Xx*]{4}[\s\-]?[Xx*]{4}[\s\-]?[Xx*]{4}[\s\-]?\d{4})\b',
    'card_masked_short': r'\b([*]{4,6}\s?\d{4})\b',

    # SWIFT/BIC (8 или 11 символов)
    'swift': r'\b([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?)\b',

    # Номера счетов
    'account_ru': r'\b(408\d{17})\b',  # Российский счёт физлица
    'account_ru_org': r'\b(407\d{17})\b',  # Российский счёт юрлица
    'account_ae': r'\b(\d{12,16})\b',  # Счёт ОАЭ (в контексте)

    # БИК (Россия)
    'bik': r'\b(04\d{7})\b',

    # ИНН
    'inn_org': r'\b(\d{10})\b',  # ИНН юрлица
    'inn_person': r'\b(\d{12})\b',  # ИНН физлица

    # КПП
    'kpp': r'\b(\d{9})\b',

    # Телефоны для СБП
    'phone_ru': r'(\+7[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',
    'phone_uae': r'(\+971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4})',
    'phone_kz': r'(\+7[\s\-]?7\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',
}


# ═══════════════════════════════════════════════════════════════════════
# ИЗВЛЕЧЕНИЕ РЕКВИЗИТОВ
# ═══════════════════════════════════════════════════════════════════════

class BankingExtractor:
    """
    Извлечение и валидация банковских реквизитов из текста.
    """

    def __init__(self, mask_logs: bool = True, encryption_password: str = None):
        """
        Args:
            mask_logs: Маскировать реквизиты в логах
            encryption_password: Пароль для шифрования (если None - без шифрования)
        """
        self.mask_logs = mask_logs
        self.crypto = SimpleCrypto(encryption_password) if encryption_password else None
        self.stats = defaultdict(int)

    def log(self, message: str, data: str = None, data_type: str = None):
        """Логирование с маскированием."""
        if data and self.mask_logs:
            if data_type == 'card':
                data = mask_card(data)
            elif data_type == 'iban':
                data = mask_iban(data)
            elif data_type == 'account':
                data = mask_account(data)

        if data:
            print(f"  {message}: {data}")
        else:
            print(f"  {message}")

    def extract_ibans(self, text: str) -> List[Dict]:
        """
        Извлечь все IBAN с валидацией.
        """
        results = []
        matches = re.findall(PATTERNS['iban'], text, re.IGNORECASE)

        for match in matches:
            iban = match.upper()

            # Проверяем что это похоже на IBAN (есть код страны в базе)
            country_code = iban[:2]
            if country_code not in IBAN_LENGTHS:
                continue

            is_valid, error = validate_iban(iban)
            bank_name = get_bank_from_iban(iban)

            result = {
                'value': iban,
                'country': country_code,
                'is_valid': is_valid,
                'validation_error': error if not is_valid else None,
                'bank': bank_name,
                'type': 'iban'
            }

            results.append(result)
            self.stats['ibans_found'] += 1
            if is_valid:
                self.stats['ibans_valid'] += 1

        return results

    def extract_cards(self, text: str) -> List[Dict]:
        """
        Извлечь номера карт (полные и маскированные).
        """
        results = []

        # Полные номера карт
        for pattern_key in ['card_full', 'card_full_13']:
            matches = re.findall(PATTERNS[pattern_key], text)

            for match in matches:
                card = re.sub(r'\D', '', match)

                if len(card) < 13 or len(card) > 19:
                    continue

                is_valid = luhn_checksum(card)
                bank_info = get_bank_from_bin(card)

                result = {
                    'value': card,
                    'value_formatted': ' '.join([card[i:i+4] for i in range(0, len(card), 4)]),
                    'is_masked': False,
                    'is_valid': is_valid,
                    'bank': bank_info.get('bank') if bank_info else None,
                    'card_type': bank_info.get('type') if bank_info else None,
                    'country': bank_info.get('country') if bank_info else None,
                    'type': 'card'
                }

                # Избегаем дубликатов
                if not any(r['value'] == card for r in results):
                    results.append(result)
                    self.stats['cards_found'] += 1
                    if is_valid:
                        self.stats['cards_valid'] += 1

        # Маскированные карты
        for pattern_key in ['card_masked', 'card_masked_short']:
            matches = re.findall(PATTERNS[pattern_key], text)

            for match in matches:
                last_digits = re.sub(r'\D', '', match)[-4:]

                result = {
                    'value': match,
                    'last_digits': last_digits,
                    'is_masked': True,
                    'is_valid': None,  # Нельзя проверить маскированную карту
                    'type': 'card_masked'
                }

                if not any(r.get('last_digits') == last_digits and r['is_masked'] for r in results):
                    results.append(result)
                    self.stats['cards_masked_found'] += 1

        return results

    def extract_swift(self, text: str) -> List[Dict]:
        """
        Извлечь SWIFT/BIC коды.
        """
        results = []
        matches = re.findall(PATTERNS['swift'], text)

        for match in matches:
            swift = match.upper()

            # Проверка базового формата SWIFT
            if not re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', swift):
                continue

            country_code = swift[4:6]
            bank_code = swift[:4]

            result = {
                'value': swift,
                'bank_code': bank_code,
                'country': country_code,
                'branch': swift[8:] if len(swift) == 11 else None,
                'type': 'swift'
            }

            if not any(r['value'] == swift for r in results):
                results.append(result)
                self.stats['swift_found'] += 1

        return results

    def extract_accounts(self, text: str) -> List[Dict]:
        """
        Извлечь номера счетов (российские, ОАЭ).
        """
        results = []

        # Российские счета физлиц (408...)
        matches = re.findall(PATTERNS['account_ru'], text)
        for match in matches:
            result = {
                'value': match,
                'country': 'RU',
                'account_type': 'personal',
                'type': 'account'
            }
            if not any(r['value'] == match for r in results):
                results.append(result)
                self.stats['accounts_found'] += 1

        # Российские счета юрлиц (407...)
        matches = re.findall(PATTERNS['account_ru_org'], text)
        for match in matches:
            result = {
                'value': match,
                'country': 'RU',
                'account_type': 'business',
                'type': 'account'
            }
            if not any(r['value'] == match for r in results):
                results.append(result)
                self.stats['accounts_found'] += 1

        return results

    def extract_bik(self, text: str) -> List[Dict]:
        """
        Извлечь БИК (Россия).
        """
        results = []
        matches = re.findall(PATTERNS['bik'], text)

        for match in matches:
            result = {
                'value': match,
                'country': 'RU',
                'type': 'bik'
            }
            if not any(r['value'] == match for r in results):
                results.append(result)
                self.stats['bik_found'] += 1

        return results

    def extract_phones_sbp(self, text: str) -> List[Dict]:
        """
        Извлечь телефоны для СБП переводов (в контексте платежей).
        """
        results = []

        # Ключевые слова контекста СБП
        sbp_context = ['сбп', 'sbp', 'сбер', 'тиньк', 'альфа', 'втб',
                      'перевод', 'переведи', 'скинь', 'на карту', 'на счёт']

        # Проверяем наличие контекста СБП
        has_sbp_context = any(kw in text.lower() for kw in sbp_context)

        if has_sbp_context:
            matches = re.findall(PATTERNS['phone_ru'], text)
            for match in matches:
                phone = re.sub(r'\D', '', match)
                result = {
                    'value': '+' + phone,
                    'country': 'RU',
                    'purpose': 'sbp',
                    'type': 'phone_sbp'
                }
                if not any(r['value'] == result['value'] for r in results):
                    results.append(result)
                    self.stats['phones_sbp_found'] += 1

        return results

    def extract_all(self, text: str) -> Dict[str, List[Dict]]:
        """
        Извлечь все типы банковских реквизитов из текста.
        """
        return {
            'ibans': self.extract_ibans(text),
            'cards': self.extract_cards(text),
            'swift_codes': self.extract_swift(text),
            'accounts': self.extract_accounts(text),
            'bik_codes': self.extract_bik(text),
            'phones_sbp': self.extract_phones_sbp(text),
        }

    def extract_blocks_with_context(self, content: str) -> List[Dict]:
        """
        Извлечь блоки реквизитов с контекстом (2 строки до и после).
        Совместимость с extract_requisites.py.
        """
        blocks = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Проверяем наличие банковских данных в строке
            has_banking = False

            # IBAN
            if re.search(PATTERNS['iban'], line, re.IGNORECASE):
                has_banking = True
            # Карты
            if re.search(PATTERNS['card_full'], line):
                has_banking = True
            # SWIFT
            if re.search(PATTERNS['swift'], line):
                has_banking = True
            # Счета
            if re.search(PATTERNS['account_ru'], line):
                has_banking = True

            if has_banking:
                # Берём контекст: 2 строки до и 2 после
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])

                # Извлекаем все реквизиты из контекста
                extracted = self.extract_all(context)

                block = {
                    'raw': context,
                    'line_number': i + 1,
                    'extracted': extracted,
                    'has_valid_iban': any(x['is_valid'] for x in extracted['ibans']),
                    'has_valid_card': any(x.get('is_valid') for x in extracted['cards'] if not x.get('is_masked')),
                }

                # Проверяем что блок не дублируется
                is_duplicate = any(
                    b['raw'] == block['raw'] or
                    abs(b['line_number'] - block['line_number']) < 3
                    for b in blocks
                )

                if not is_duplicate:
                    blocks.append(block)

        return blocks


# ═══════════════════════════════════════════════════════════════════════
# ОБРАБОТКА ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════════════

def extract_from_file(filepath: Path, extractor: BankingExtractor) -> Dict:
    """
    Извлечь реквизиты из файла чата.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Ошибка чтения {filepath}: {e}")
        return None

    # Информация о контакте из имени файла
    filename = filepath.name
    parts = filename.replace('.md', '').split('_')

    contact_info = {
        'type': parts[0] if len(parts) > 0 else "unknown",
        'name': parts[1] if len(parts) > 1 else "unknown",
        'topic': parts[2] if len(parts) > 2 else "",
        'file': filename,
        'path': str(filepath)
    }

    # Извлекаем блоки с контекстом
    blocks = extractor.extract_blocks_with_context(content)

    # Также извлекаем общий список всех реквизитов
    all_extracted = extractor.extract_all(content)

    return {
        'contact': contact_info,
        'blocks': blocks,
        'summary': {
            'total_ibans': len(all_extracted['ibans']),
            'valid_ibans': sum(1 for x in all_extracted['ibans'] if x['is_valid']),
            'total_cards': len(all_extracted['cards']),
            'valid_cards': sum(1 for x in all_extracted['cards'] if x.get('is_valid') and not x.get('is_masked')),
            'masked_cards': sum(1 for x in all_extracted['cards'] if x.get('is_masked')),
            'swift_codes': len(all_extracted['swift_codes']),
            'accounts': len(all_extracted['accounts']),
        },
        'all_requisites': all_extracted
    }


def build_database(
    chats_dir: Path,
    output_json: Path = None,
    output_md: Path = None,
    mask_logs: bool = True,
    encrypt: bool = False,
    encryption_password: str = None
) -> Dict:
    """
    Собрать базу всех банковских реквизитов из чатов.
    """
    extractor = BankingExtractor(
        mask_logs=mask_logs,
        encryption_password=encryption_password if encrypt else None
    )

    all_results = []

    # Поиск файлов
    md_files = []
    for contact_type in CONTACT_TYPES:
        pattern = chats_dir / contact_type / '*.md'
        md_files.extend(glob.glob(str(pattern)))

    print(f"Найдено {len(md_files)} файлов чатов")

    for filepath in md_files:
        result = extract_from_file(Path(filepath), extractor)
        if result and (result['blocks'] or any(result['summary'].values())):
            all_results.append(result)
            print(f"  {Path(filepath).name}: {result['summary']}")

    # Статистика
    total_stats = {
        'files_processed': len(md_files),
        'files_with_requisites': len(all_results),
        'total_ibans': sum(r['summary']['total_ibans'] for r in all_results),
        'valid_ibans': sum(r['summary']['valid_ibans'] for r in all_results),
        'total_cards': sum(r['summary']['total_cards'] for r in all_results),
        'valid_cards': sum(r['summary']['valid_cards'] for r in all_results),
        'masked_cards': sum(r['summary']['masked_cards'] for r in all_results),
        'swift_codes': sum(r['summary']['swift_codes'] for r in all_results),
        'accounts': sum(r['summary']['accounts'] for r in all_results),
        'extraction_date': datetime.now().isoformat(),
    }

    print(f"\n=== Итоги ===")
    print(f"Файлов с реквизитами: {total_stats['files_with_requisites']}")
    print(f"IBAN: {total_stats['total_ibans']} (валидных: {total_stats['valid_ibans']})")
    print(f"Карты: {total_stats['total_cards']} (валидных: {total_stats['valid_cards']}, маскированных: {total_stats['masked_cards']})")
    print(f"SWIFT: {total_stats['swift_codes']}")
    print(f"Счета: {total_stats['accounts']}")

    database = {
        'metadata': total_stats,
        'results': all_results
    }

    # Сохранение в JSON
    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)

        json_content = json.dumps(database, ensure_ascii=False, indent=2)

        if encrypt and extractor.crypto:
            json_content = extractor.crypto.encrypt(json_content)
            output_json = output_json.with_suffix('.json.enc')
            print(f"\nJSON зашифрован методом: {extractor.crypto.method}")

        with open(output_json, 'w', encoding='utf-8') as f:
            f.write(json_content)

        print(f"JSON сохранён: {output_json}")

    # Сохранение в Markdown
    if output_md:
        output_md.parent.mkdir(parents=True, exist_ok=True)

        md_content = generate_markdown_report(database)

        with open(output_md, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Markdown сохранён: {output_md}")

    return database


def generate_markdown_report(database: Dict) -> str:
    """
    Генерация Markdown отчёта из базы реквизитов.
    """
    lines = []
    meta = database['metadata']

    lines.append("# Банковские реквизиты")
    lines.append("")
    lines.append(f"*Дата извлечения: {meta['extraction_date'][:10]}*")
    lines.append("")
    lines.append("## Статистика")
    lines.append("")
    lines.append(f"- Обработано файлов: {meta['files_processed']}")
    lines.append(f"- Файлов с реквизитами: {meta['files_with_requisites']}")
    lines.append(f"- IBAN: {meta['total_ibans']} (валидных: {meta['valid_ibans']})")
    lines.append(f"- Карты: {meta['total_cards']} (валидных: {meta['valid_cards']})")
    lines.append(f"- SWIFT: {meta['swift_codes']}")
    lines.append(f"- Счета: {meta['accounts']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Группировка по контактам
    lines.append("## По контактам")
    lines.append("")

    for result in database['results']:
        contact = result['contact']
        lines.append(f"### {contact['name']} ({contact['type']})")
        lines.append("")

        # IBAN
        for iban in result['all_requisites']['ibans']:
            status = 'Valid' if iban['is_valid'] else 'Invalid'
            bank = iban.get('bank', 'Unknown')
            lines.append(f"- **IBAN**: `{mask_iban(iban['value'])}` [{status}] {bank}")

        # Карты
        for card in result['all_requisites']['cards']:
            if card.get('is_masked'):
                lines.append(f"- **Карта (маск.)**: `{card['value']}`")
            else:
                status = 'Valid' if card.get('is_valid') else 'Invalid'
                bank = card.get('bank', 'Unknown')
                lines.append(f"- **Карта**: `{mask_card(card['value'])}` [{status}] {bank}")

        # SWIFT
        for swift in result['all_requisites']['swift_codes']:
            lines.append(f"- **SWIFT**: `{swift['value']}` ({swift['country']})")

        # Счета
        for account in result['all_requisites']['accounts']:
            lines.append(f"- **Счёт**: `{mask_account(account['value'])}` ({account['country']})")

        lines.append("")
        lines.append(f"*Файл: {contact['file']}*")
        lines.append("")
        lines.append("---")
        lines.append("")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Извлечение банковских реквизитов из чатов WhatsApp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python extract_banking.py                          # Базовое извлечение
  python extract_banking.py --encrypt --password secret  # С шифрованием
  python extract_banking.py --validate-only "AE070331234567890123456"  # Только проверка IBAN
  python extract_banking.py --check-card "4276 1234 5678 9012"         # Только проверка карты
        """
    )

    parser.add_argument('--chats-dir', type=Path, default=CHATS_DIR,
                       help='Директория с чатами')
    parser.add_argument('-o', '--output-json', type=Path,
                       default=JSON_DIR / 'banking_requisites.json',
                       help='Путь для JSON файла')
    parser.add_argument('--output-md', type=Path,
                       default=CHATS_DIR / '_база' / 'banking_requisites.md',
                       help='Путь для Markdown файла')
    parser.add_argument('--no-mask', action='store_true',
                       help='Не маскировать реквизиты в логах')
    parser.add_argument('--encrypt', action='store_true',
                       help='Шифровать JSON файл')
    parser.add_argument('--password', type=str, default='',
                       help='Пароль для шифрования')
    parser.add_argument('--validate-only', type=str, metavar='IBAN',
                       help='Только проверить IBAN')
    parser.add_argument('--check-card', type=str, metavar='CARD',
                       help='Только проверить номер карты')
    parser.add_argument('--decrypt', type=Path,
                       help='Расшифровать файл .json.enc')

    args = parser.parse_args()

    # Режим валидации IBAN
    if args.validate_only:
        is_valid, message = validate_iban(args.validate_only)
        bank = get_bank_from_iban(args.validate_only)

        print(f"IBAN: {args.validate_only}")
        print(f"Валиден: {'Да' if is_valid else 'Нет'}")
        print(f"Сообщение: {message}")
        if bank:
            print(f"Банк: {bank}")
        return

    # Режим проверки карты
    if args.check_card:
        card = args.check_card
        is_valid = luhn_checksum(card)
        bank_info = get_bank_from_bin(card)

        print(f"Карта: {mask_card(card)}")
        print(f"Валидна (Luhn): {'Да' if is_valid else 'Нет'}")
        if bank_info:
            print(f"Банк: {bank_info['bank']}")
            print(f"Тип: {bank_info['type']}")
            print(f"Страна: {bank_info['country']}")
        return

    # Режим расшифровки
    if args.decrypt:
        if not args.password:
            print("Ошибка: укажите --password для расшифровки")
            return

        crypto = SimpleCrypto(args.password)

        with open(args.decrypt, 'r', encoding='utf-8') as f:
            encrypted = f.read()

        try:
            decrypted = crypto.decrypt(encrypted)
            data = json.loads(decrypted)

            output_path = args.decrypt.with_suffix('').with_suffix('.decrypted.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Расшифровано в: {output_path}")
        except Exception as e:
            print(f"Ошибка расшифровки: {e}")
        return

    # Основной режим - извлечение из чатов
    if args.encrypt and not args.password:
        args.password = input("Введите пароль для шифрования: ")

    build_database(
        chats_dir=args.chats_dir,
        output_json=args.output_json,
        output_md=args.output_md,
        mask_logs=not args.no_mask,
        encrypt=args.encrypt,
        encryption_password=args.password
    )


if __name__ == "__main__":
    main()
