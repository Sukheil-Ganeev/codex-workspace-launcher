#!/usr/bin/env python3
"""
Валидатор форматирования карточек для WhatsApp.
Использование: python validate-whatsapp.py файл.txt
"""

import sys
import re

def validate_whatsapp(text):
    errors = []
    warnings = []

    # 1. Проверка разделителей (должно быть ровно 15 тире)
    separators = re.findall(r'[─━\-]{10,}', text)
    for sep in separators:
        if len(sep) != 15:
            errors.append(f"Разделитель неправильной длины: {len(sep)} (должно быть 15)")
        if '━' in sep or '-' in sep:
            errors.append("Используйте символ ─ (U+2500), не ━ или обычное тире")

    # 2. Проверка 2 пробелов после категории
    categories = re.findall(r'```[^`]+```( *)\d', text)
    for spaces in categories:
        if len(spaces) != 2:
            errors.append(f"После категории должно быть 2 пробела, найдено: {len(spaces)}")

    # 3. Проверка эмодзи
    allowed_emoji = ['💰', '➕', '⚠️']
    # Найти все эмодзи в тексте
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]')
    found_emoji = emoji_pattern.findall(text)
    for emoji in found_emoji:
        if emoji not in allowed_emoji:
            warnings.append(f"Неразрешённый эмодзи: {emoji}")

    # 4. Проверка позиции эмодзи (должен быть перед *)
    wrong_emoji = re.findall(r'\*[💰➕⚠️]', text)
    if wrong_emoji:
        errors.append("Эмодзи должен быть ПЕРЕД звёздочкой, не после")

    # 5. Проверка двойных символов (это Telegram)
    if '**' in text or '__' in text:
        errors.append("Двойные ** или __ — это формат Telegram, не WhatsApp")

    # 6. Проверка слова "аттракции"
    if 'аттракции' in text.lower():
        errors.append("Используйте 'аттракционы', не 'аттракции'")

    return errors, warnings

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Читаем из stdin
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()

    errors, warnings = validate_whatsapp(text)

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
