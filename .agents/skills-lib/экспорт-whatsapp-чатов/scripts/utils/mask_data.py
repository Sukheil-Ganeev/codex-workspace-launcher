#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Маскирование конфиденциальных данных в чатах.
Поддерживает карты, телефоны, IBAN, счета.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Dict

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, PATTERNS

# ═══════════════════════════════════════════════════════════════
# УРОВНИ МАСКИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

MASK_LEVELS = {
    'minimal': {
        'card': lambda m: m[:4] + ' **** ' + m[-4:],           # 4276 **** 9012
        'phone_ru': lambda m: m[:3] + ' *** **-' + m[-2:],     # +7 *** **-81
        'phone_uae': lambda m: m[:4] + ' ** *** ' + m[-2:],    # +971 ** *** 67
        'iban': lambda m: m[:4] + '***' + m[-3:],              # AE72***584
        'account': lambda m: m[:3] + '***' + m[-4:],           # 408***5651
        'email': lambda m: m.split('@')[0][:2] + '***@' + m.split('@')[1],  # an***@mail.ru
    },
    'standard': {
        'card': lambda m: m[:4] + ' **** **** ' + m[-4:],
        'phone_ru': lambda m: '+7 *** ***-**-' + m[-2:],
        'phone_uae': lambda m: '+971 ** ***-' + m[-4:],
        'iban': lambda m: m[:4] + '********' + m[-3:],
        'account': lambda m: m[:3] + '*' * 13 + m[-4:],
        'email': lambda m: m[0] + '***@' + m.split('@')[1],
    },
    'strict': {
        'card': lambda m: '**** **** **** ****',
        'phone_ru': lambda m: '+7 *** ***-**-**',
        'phone_uae': lambda m: '+971 ** ***-****',
        'iban': lambda m: '*' * len(m),
        'account': lambda m: '*' * len(m),
        'email': lambda m: '***@***',
    },
}


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ МАСКИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

def normalize_card(card: str) -> str:
    """Нормализовать номер карты (убрать пробелы/дефисы)."""
    return re.sub(r'[\s\-]', '', card)


def mask_cards(text: str, level: str = 'standard') -> str:
    """Маскировать номера карт."""
    mask_func = MASK_LEVELS[level]['card']

    # Паттерн для российских карт (16 цифр)
    pattern = r'\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'

    def replacer(match):
        card = normalize_card(match.group())
        return mask_func(card)

    return re.sub(pattern, replacer, text)


def mask_phones(text: str, level: str = 'standard') -> str:
    """Маскировать телефоны."""
    # Российские телефоны
    ru_pattern = r'\+7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
    ru_mask = MASK_LEVELS[level]['phone_ru']

    def ru_replacer(match):
        phone = re.sub(r'[\s\-\(\)]', '', match.group())
        return ru_mask(phone)

    text = re.sub(ru_pattern, ru_replacer, text)

    # Телефоны ОАЭ
    uae_pattern = r'\+971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4}'
    uae_mask = MASK_LEVELS[level]['phone_uae']

    def uae_replacer(match):
        phone = re.sub(r'[\s\-]', '', match.group())
        return uae_mask(phone)

    text = re.sub(uae_pattern, uae_replacer, text)

    return text


def mask_ibans(text: str, level: str = 'standard') -> str:
    """Маскировать IBAN."""
    mask_func = MASK_LEVELS[level]['iban']
    pattern = r'\bAE\d{21}\b'

    def replacer(match):
        return mask_func(match.group())

    return re.sub(pattern, replacer, text)


def mask_accounts(text: str, level: str = 'standard') -> str:
    """Маскировать номера счетов."""
    mask_func = MASK_LEVELS[level]['account']
    pattern = r'\b408\d{17}\b'

    def replacer(match):
        return mask_func(match.group())

    return re.sub(pattern, replacer, text)


def mask_emails(text: str, level: str = 'standard') -> str:
    """Маскировать email."""
    mask_func = MASK_LEVELS[level]['email']
    pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

    def replacer(match):
        return mask_func(match.group())

    return re.sub(pattern, replacer, text)


def mask_all(text: str, level: str = 'standard') -> str:
    """Маскировать все типы данных."""
    text = mask_cards(text, level)
    text = mask_phones(text, level)
    text = mask_ibans(text, level)
    text = mask_accounts(text, level)
    text = mask_emails(text, level)
    return text


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТКА ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════

def mask_file(
    input_path: str,
    output_path: str = None,
    level: str = 'standard',
    types: list = None
) -> str:
    """
    Маскировать данные в файле.

    Args:
        input_path: Входной файл
        output_path: Выходной файл (если None - добавить _masked к имени)
        level: Уровень маскирования (minimal, standard, strict)
        types: Типы данных для маскирования (cards, phones, ibans, accounts, emails)

    Returns:
        Путь к выходному файлу
    """
    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_masked{input_path.suffix}"
    else:
        output_path = Path(output_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Определяем какие типы маскировать
    if types is None:
        masked = mask_all(content, level)
    else:
        masked = content
        if 'cards' in types:
            masked = mask_cards(masked, level)
        if 'phones' in types:
            masked = mask_phones(masked, level)
        if 'ibans' in types:
            masked = mask_ibans(masked, level)
        if 'accounts' in types:
            masked = mask_accounts(masked, level)
        if 'emails' in types:
            masked = mask_emails(masked, level)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(masked)

    return str(output_path)


def mask_directory(
    dir_path: str,
    level: str = 'standard',
    types: list = None,
    output_dir: str = None
) -> list:
    """Маскировать все файлы в директории."""
    dir_path = Path(dir_path)
    output_dir = Path(output_dir) if output_dir else dir_path / '_masked'
    output_dir.mkdir(parents=True, exist_ok=True)

    processed = []

    for file_path in dir_path.glob("*.md"):
        if '_masked' in file_path.name:
            continue

        output_path = output_dir / file_path.name
        mask_file(str(file_path), str(output_path), level, types)
        processed.append(str(output_path))
        print(f"✓ {file_path.name}")

    return processed


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ (без маскирования)
# ═══════════════════════════════════════════════════════════════

def analyze_sensitive_data(text: str) -> Dict:
    """Найти все конфиденциальные данные без маскирования."""
    findings = {
        'cards': re.findall(r'\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', text),
        'phones_ru': re.findall(r'\+7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', text),
        'phones_uae': re.findall(r'\+971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4}', text),
        'ibans': re.findall(r'\bAE\d{21}\b', text),
        'accounts': re.findall(r'\b408\d{17}\b', text),
        'emails': re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text),
    }
    return findings


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Маскирование конфиденциальных данных',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Уровни маскирования:
  minimal  - показывает начало и конец: 4276 **** 9012
  standard - показывает только начало: 4276 **** **** ****
  strict   - полное маскирование: **** **** **** ****

Примеры:
  python mask_data.py chat.md                     # Стандартное маскирование
  python mask_data.py chat.md -l strict           # Строгое маскирование
  python mask_data.py chat.md -t cards phones     # Только карты и телефоны
  python mask_data.py --dir D:/Downloads/Chats/   # Вся директория
  python mask_data.py --analyze chat.md           # Только анализ
        """
    )

    parser.add_argument('input', nargs='?', help='Входной файл')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('-l', '--level', choices=['minimal', 'standard', 'strict'],
                        default='standard', help='Уровень маскирования')
    parser.add_argument('-t', '--types', nargs='+',
                        choices=['cards', 'phones', 'ibans', 'accounts', 'emails'],
                        help='Типы данных для маскирования')
    parser.add_argument('--dir', help='Обработать директорию')
    parser.add_argument('--output-dir', help='Выходная директория')
    parser.add_argument('--analyze', action='store_true', help='Только анализ')
    parser.add_argument('--text', help='Маскировать текст напрямую')

    args = parser.parse_args()

    if args.text:
        print(mask_all(args.text, args.level))
        return

    if args.dir:
        files = mask_directory(args.dir, args.level, args.types, args.output_dir)
        print(f"\n✓ Обработано файлов: {len(files)}")
        return

    if not args.input:
        parser.print_help()
        return

    if args.analyze:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()

        findings = analyze_sensitive_data(content)

        print(f"\nАнализ файла: {args.input}\n")
        for data_type, items in findings.items():
            if items:
                print(f"{data_type}: {len(items)}")
                for item in items[:5]:
                    print(f"  - {item}")
                if len(items) > 5:
                    print(f"  ... и ещё {len(items) - 5}")
        return

    output = mask_file(args.input, args.output, args.level, args.types)
    print(f"✓ Сохранено: {output}")


if __name__ == "__main__":
    main()
