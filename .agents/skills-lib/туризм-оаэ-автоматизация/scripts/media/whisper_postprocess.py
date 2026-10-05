#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Пост-обработка транскрипций Whisper: исправление банков, имён, терминов."""

import re
import sys
from pathlib import Path

# Добавляем путь к config
sys.path.insert(0, str(Path(__file__).parent))
from config import ALL_CORRECTIONS, BANK_CORRECTIONS, NAME_CORRECTIONS, TERM_CORRECTIONS

def correct_text(text: str, corrections: dict = None) -> str:
    """
    Исправить ошибки в тексте по словарю.

    Args:
        text: Исходный текст
        corrections: Словарь исправлений {ошибка: правильно}

    Returns:
        Исправленный текст
    """
    if corrections is None:
        corrections = ALL_CORRECTIONS

    result = text
    for wrong, correct in corrections.items():
        # Регистронезависимая замена
        pattern = re.compile(re.escape(wrong), re.IGNORECASE)
        result = pattern.sub(correct, result)

    return result

def correct_banks(text: str) -> str:
    """Исправить названия банков."""
    return correct_text(text, BANK_CORRECTIONS)

def correct_names(text: str) -> str:
    """Исправить имена."""
    return correct_text(text, NAME_CORRECTIONS)

def correct_terms(text: str) -> str:
    """Исправить термины."""
    return correct_text(text, TERM_CORRECTIONS)

def normalize_numbers(text: str) -> str:
    """
    Нормализовать числа в тексте.
    Примеры: "сто тысяч" -> "100 000", "пять тысяч" -> "5 000"
    """
    number_words = {
        'ноль': '0', 'один': '1', 'одна': '1', 'два': '2', 'две': '2',
        'три': '3', 'четыре': '4', 'пять': '5', 'шесть': '6',
        'семь': '7', 'восемь': '8', 'девять': '9', 'десять': '10',
        'одиннадцать': '11', 'двенадцать': '12', 'тринадцать': '13',
        'четырнадцать': '14', 'пятнадцать': '15', 'шестнадцать': '16',
        'семнадцать': '17', 'восемнадцать': '18', 'девятнадцать': '19',
        'двадцать': '20', 'тридцать': '30', 'сорок': '40',
        'пятьдесят': '50', 'шестьдесят': '60', 'семьдесят': '70',
        'восемьдесят': '80', 'девяносто': '90', 'сто': '100',
        'двести': '200', 'триста': '300', 'четыреста': '400',
        'пятьсот': '500', 'шестьсот': '600', 'семьсот': '700',
        'восемьсот': '800', 'девятьсот': '900',
    }

    multipliers = {
        'тысяч': 1000, 'тысячи': 1000, 'тысячу': 1000, 'тысяча': 1000,
        'миллион': 1000000, 'миллиона': 1000000, 'миллионов': 1000000,
    }

    # Простая замена отдельных числительных
    result = text
    for word, digit in number_words.items():
        result = re.sub(rf'\b{word}\b', digit, result, flags=re.IGNORECASE)

    return result

def format_currency_amounts(text: str) -> str:
    """
    Форматировать суммы с разделителями.
    Пример: "100000 рублей" -> "100 000 рублей"
    """
    def add_spaces(match):
        num = match.group(1)
        # Добавляем пробелы каждые 3 цифры справа
        formatted = ""
        for i, c in enumerate(reversed(num)):
            if i > 0 and i % 3 == 0:
                formatted = " " + formatted
            formatted = c + formatted
        return formatted + match.group(2)

    # Числа перед валютами
    result = re.sub(r'(\d{4,})(\s*(?:руб|₽|RUB|AED|дирхам|USD|\$|долл))',
                    add_spaces, text, flags=re.IGNORECASE)
    return result

def postprocess_transcript(text: str) -> str:
    """
    Полная пост-обработка транскрипции.

    Args:
        text: Сырая транскрипция от Whisper

    Returns:
        Исправленный и отформатированный текст
    """
    # 1. Исправить ошибки по словарям
    result = correct_text(text)

    # 2. Нормализовать числительные
    result = normalize_numbers(result)

    # 3. Форматировать суммы
    result = format_currency_amounts(result)

    # 4. Удалить лишние пробелы
    result = re.sub(r'\s+', ' ', result).strip()

    # 5. Первая буква заглавная после точки
    result = re.sub(r'(\.\s+)([а-яa-z])',
                    lambda m: m.group(1) + m.group(2).upper(), result)

    return result

def process_file(input_path: str, output_path: str = None) -> str:
    """
    Обработать файл с транскрипциями.

    Args:
        input_path: Путь к файлу
        output_path: Путь для сохранения (если None - перезаписать)

    Returns:
        Обработанный текст
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    result = postprocess_transcript(text)

    save_path = output_path or input_path
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(result)

    return result

# ═══════════════════════════════════════════════════════════════
# CUSTOM CORRECTIONS (добавьте свои исправления)
# ═══════════════════════════════════════════════════════════════
CUSTOM_CORRECTIONS = {
    # Добавьте свои исправления здесь
    # "ошибка": "правильно",
}

def add_custom_corrections(corrections: dict):
    """Добавить пользовательские исправления."""
    ALL_CORRECTIONS.update(corrections)

# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Пост-обработка Whisper транскрипций')
    parser.add_argument('input', nargs='?', help='Входной файл или текст')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('-t', '--text', action='store_true',
                        help='Входной аргумент - текст, не файл')

    args = parser.parse_args()

    if not args.input:
        # Интерактивный режим
        print("Введите текст для обработки (Ctrl+D для завершения):")
        text = sys.stdin.read()
        print("\n--- Результат ---")
        print(postprocess_transcript(text))
    elif args.text:
        # Обработка текста напрямую
        print(postprocess_transcript(args.input))
    else:
        # Обработка файла
        result = process_file(args.input, args.output)
        print(f"Файл обработан: {args.output or args.input}")
