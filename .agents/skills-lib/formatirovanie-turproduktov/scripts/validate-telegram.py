#!/usr/bin/env python3
"""Валидация форматирования текста для Telegram."""

import sys
import re

def validate_telegram_format(text):
    """Проверяет корректность Telegram форматирования."""
    errors = []
    warnings = []

    # 1. Проверка использования моноширинного для категорий (ЗАПРЕЩЕНО в Telegram)
    if re.search(r'```[^`]+```\s{0,2}\d+\$', text):
        errors.append("❌ Ошибка: в Telegram нельзя использовать ```моноширинный``` для категорий цен. Используй **жирный**")

    # 2. Проверка одинарных символов (должны быть двойные для Telegram)
    # Одинарный * не внутри **
    if re.search(r'(?<!\*)\*[^*]+\*(?!\*)', text):
        errors.append("❌ Ошибка: используются одинарные * (это WhatsApp синтаксис, для Telegram нужны двойные **)")

    # Одинарный _ не внутри __
    if re.search(r'(?<!_)_[^_]+_(?!_)', text):
        errors.append("❌ Ошибка: используются одинарные _ (это WhatsApp синтаксис, для Telegram нужны двойные __)")

    # 3. Проверка эмодзи перед заголовком
    if re.search(r'\*\*[💰➕⚠️]', text):
        errors.append("❌ Ошибка: эмодзи должен быть ПЕРЕД звёздочками: '💰 **ЦЕНЫ**'")

    # 4. Проверка длины разделителя (должно быть 18 тире для Telegram)
    separators = re.findall(r'─+', text)
    for sep in separators:
        if len(sep) != 18:
            warnings.append(f"⚠️ Предупреждение: разделитель {len(sep)} тире (рекомендуется 18 для Telegram)")

    # 5. Проверка пробелов вокруг разделителей
    if re.search(r'\S\|\S', text):
        errors.append("❌ Ошибка: нужны пробелы вокруг |")

    if re.search(r'\S→\S', text):
        errors.append("❌ Ошибка: нужны пробелы вокруг →")

    # 6. Проверка формата категорий (должно быть **Категория** — цена)
    if re.search(r'\*\*[^*]+\*\*\s{2,}\d+\$', text):
        warnings.append("⚠️ Предупреждение: в Telegram после категории используй ' — ' (тире), не пробелы")

    return errors, warnings

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    errors, warnings = validate_telegram_format(text)

    if errors:
        print("\n".join(errors))
    if warnings:
        print("\n".join(warnings))

    if not errors and not warnings:
        print("✅ Форматирование Telegram корректно!")
        sys.exit(0)
    elif errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
