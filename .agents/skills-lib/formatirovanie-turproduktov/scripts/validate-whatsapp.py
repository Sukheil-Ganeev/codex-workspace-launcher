#!/usr/bin/env python3
"""Валидация форматирования текста для WhatsApp."""

import sys
import re

def validate_whatsapp_format(text):
    """Проверяет корректность WhatsApp форматирования."""
    errors = []
    warnings = []

    # 1. Проверка двух пробелов после категории
    # Паттерн: ```текст``` + один пробел + не-пробел
    if re.search(r'```[^`]+```\s[^\s]', text):
        errors.append("❌ Ошибка: нужно ДВА пробела после ```категории``` перед ценой")

    # 2. Проверка эмодзи перед заголовком (не после)
    if re.search(r'\*[💰➕⚠️]', text):
        errors.append("❌ Ошибка: эмодзи должен быть ПЕРЕД звёздочкой: '💰 *ЦЕНЫ*', не '*💰 ЦЕНЫ*'")

    # 3. Проверка разрешённых эмодзи
    emoji_pattern = r'[^\x00-\x7F]+'
    emojis_found = re.findall(emoji_pattern, text)
    allowed_emojis = {'💰', '➕', '⚠️', '─', '→', '—', '★'}
    for emoji in emojis_found:
        for char in emoji:
            if char not in allowed_emojis and ord(char) > 127:
                warnings.append(f"⚠️ Предупреждение: найден недопустимый эмодзи '{char}'")

    # 4. Проверка пробелов вокруг разделителей
    if re.search(r'\S\|\S', text):
        errors.append("❌ Ошибка: нужны пробелы вокруг | (правильно: 'A | B')")

    if re.search(r'\S→\S', text):
        errors.append("❌ Ошибка: нужны пробелы вокруг → (правильно: 'A → B')")

    # 5. Проверка длины разделителя (должно быть 15 тире для WhatsApp)
    separators = re.findall(r'─+', text)
    for sep in separators:
        if len(sep) != 15:
            warnings.append(f"⚠️ Предупреждение: разделитель {len(sep)} тире (рекомендуется 15 для WhatsApp)")

    # 6. Проверка формата цен
    if re.search(r'\d+\s\$', text):
        errors.append("❌ Ошибка: пробел перед $ (правильно: '50$', не '50 $')")

    # 7. Проверка двойных символов (должны быть одинарные для WhatsApp)
    if re.search(r'\*\*[^*]+\*\*', text):
        errors.append("❌ Ошибка: используются двойные ** (это Telegram синтаксис, для WhatsApp нужны одинарные *)")

    if re.search(r'__[^_]+__', text):
        errors.append("❌ Ошибка: используются двойные __ (это Telegram синтаксис, для WhatsApp нужны одинарные _)")

    return errors, warnings

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    errors, warnings = validate_whatsapp_format(text)

    if errors:
        print("\n".join(errors))
    if warnings:
        print("\n".join(warnings))

    if not errors and not warnings:
        print("✅ Форматирование WhatsApp корректно!")
        sys.exit(0)
    elif errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
