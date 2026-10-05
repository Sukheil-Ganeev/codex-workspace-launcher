#!/usr/bin/env python3
"""
Валидатор форматирования карточек для Telegram.
Использование: python validate-telegram.py файл.txt
"""

import sys
import re

def validate_telegram(text):
    errors = []
    warnings = []

    # 1. Проверка разделителей (должно быть ровно 18 тире)
    separators = re.findall(r'[─━\-]{10,}', text)
    for sep in separators:
        if len(sep) != 18:
            errors.append(f"Разделитель неправильной длины: {len(sep)} (должно быть 18)")
        if '━' in sep or '-' in sep:
            errors.append("Используйте символ ─ (U+2500), не ━ или обычное тире")

    # 2. Проверка двойных ** и __ (должны использоваться в Telegram)
    single_bold = re.findall(r'(?<!\*)\*([^*]+)\*(?!\*)', text)
    if single_bold:
        errors.append("Используйте ** для жирного текста в Telegram, не одинарные *")

    single_italic = re.findall(r'(?<!_)_([^_]+)_(?!_)', text)
    if single_italic:
        errors.append("Используйте __ для курсива в Telegram, не одинарные _")

    # 3. Проверка отсутствия моноширинного для категорий
    if '```' in text:
        errors.append("Не используйте ``` для категорий в Telegram, используйте **Категория** —")

    # 4. Проверка формата категорий (должно быть **Категория** —)
    # Ищем строки с ценами, которые должны начинаться с категории
    price_lines = re.findall(r'^(.+\d+\$.*(?:взр|реб|чел)).*$', text, re.MULTILINE)
    for line in price_lines:
        # Проверяем, что строка начинается с **Категория** —
        if not re.match(r'\*\*[^*]+\*\* —', line.strip()):
            # Это может быть просто строка с ценой без категории, проверяем
            if re.match(r'[А-Яа-яA-Za-z]', line.strip()):
                warnings.append(f"Возможно неправильный формат категории: {line[:50]}...")

    # 5. Проверка эмодзи
    allowed_emoji = ['💰', '➕', '⚠️']
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]')
    found_emoji = emoji_pattern.findall(text)
    for emoji in found_emoji:
        if emoji not in allowed_emoji:
            warnings.append(f"Неразрешённый эмодзи: {emoji}")

    # 6. Проверка позиции эмодзи (должен быть перед **)
    wrong_emoji = re.findall(r'\*\*[💰➕⚠️]', text)
    if wrong_emoji:
        errors.append("Эмодзи должен быть ПЕРЕД **, не после")

    # 7. Проверка слова "аттракции"
    if 'аттракции' in text.lower():
        errors.append("Используйте 'аттракционы', не 'аттракции'")

    # 8. Проверка наличия тире после категории
    categories_without_dash = re.findall(r'\*\*[^*]+\*\*\s+\d', text)
    if categories_without_dash:
        errors.append("После категории должно быть тире (—), например: **Базовая** — 85$")

    return errors, warnings

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Читаем из stdin
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()

    errors, warnings = validate_telegram(text)

    if errors:
        print("❌ ОШИБКИ:")
        for e in errors:
            print(f"  • {e}")

    if warnings:
        print("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        for w in warnings:
            print(f"  • {w}")

    if not errors and not warnings:
        print("✅ Форматирование корректно!")

    sys.exit(1 if errors else 0)
