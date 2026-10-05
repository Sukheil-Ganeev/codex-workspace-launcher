#!/usr/bin/env python3
"""
Вспомогательные функции для работы с форматированием.
"""

import re

def generate_separator(platform='whatsapp'):
    """Генерирует разделитель для указанной платформы."""
    if platform == 'whatsapp':
        return '─' * 15  # ───────────────
    elif platform == 'telegram':
        return '─' * 18  # ──────────────────
    else:
        raise ValueError(f"Неизвестная платформа: {platform}")

def format_price(adult, child=None):
    """Форматирует цену."""
    if child:
        return f"{adult}$ взр / {child}$ реб"
    return f"{adult}$"

def format_category_whatsapp(name, price):
    """Форматирует категорию для WhatsApp."""
    return f"```{name}```  {price}"  # 2 пробела!

def format_category_telegram(name, price):
    """Форматирует категорию для Telegram."""
    return f"**{name}** — {price}"

def convert_whatsapp_to_telegram(text):
    """Конвертирует текст из формата WhatsApp в Telegram."""
    # Заменяем одинарные * на **
    result = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'**\1**', text)
    # Заменяем _ на __
    result = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'__\1__', result)
    # Заменяем разделители
    result = result.replace('─' * 15, '─' * 18)
    # Заменяем категории
    result = re.sub(r'```([^`]+)```  ', r'**\1** — ', result)
    return result

def convert_telegram_to_whatsapp(text):
    """Конвертирует текст из формата Telegram в WhatsApp."""
    # Заменяем ** на *
    result = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', text)
    # Заменяем __ на _
    result = re.sub(r'__([^_]+)__', r'_\1_', result)
    # Заменяем разделители
    result = result.replace('─' * 18, '─' * 15)
    # Заменяем категории
    result = re.sub(r'\*\*([^*]+)\*\* — ', r'```\1```  ', result)
    return result

def wrap_bold(text, platform='whatsapp'):
    """Оборачивает текст в жирное форматирование."""
    if platform == 'whatsapp':
        return f'*{text}*'
    elif platform == 'telegram':
        return f'**{text}**'
    else:
        raise ValueError(f"Неизвестная платформа: {platform}")

def wrap_italic(text, platform='whatsapp'):
    """Оборачивает текст в курсивное форматирование."""
    if platform == 'whatsapp':
        return f'_{text}_'
    elif platform == 'telegram':
        return f'__{text}__'
    else:
        raise ValueError(f"Неизвестная платформа: {platform}")

def wrap_mono(text):
    """Оборачивает текст в моноширинное форматирование (только WhatsApp)."""
    return f'```{text}```'

def format_time_range(start, end):
    """Форматирует временной диапазон."""
    return f"{start} – {end}"

def format_duration(hours=0, minutes=0):
    """Форматирует длительность."""
    parts = []
    if hours:
        parts.append(f"{hours} ч")
    if minutes:
        parts.append(f"{minutes} мин")
    return ' '.join(parts) if parts else "0 мин"

if __name__ == '__main__':
    # Примеры использования
    print("=" * 40)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 40)

    print("\n--- Разделители ---")
    print("WhatsApp:", generate_separator('whatsapp'))
    print("Telegram:", generate_separator('telegram'))

    print("\n--- Цены ---")
    print("Полная:", format_price(85, 60))
    print("Только взрослый:", format_price(85))

    print("\n--- Категории ---")
    print("WhatsApp:", format_category_whatsapp("Базовая", "85$ взр / 60$ реб"))
    print("Telegram:", format_category_telegram("Базовая", "85$ взр / 60$ реб"))

    print("\n--- Форматирование текста ---")
    print("Жирный WA:", wrap_bold("важно", 'whatsapp'))
    print("Жирный TG:", wrap_bold("важно", 'telegram'))
    print("Курсив WA:", wrap_italic("примечание", 'whatsapp'))
    print("Курсив TG:", wrap_italic("примечание", 'telegram'))
    print("Моно:", wrap_mono("категория"))

    print("\n--- Время ---")
    print("Диапазон:", format_time_range("09:00", "18:00"))
    print("Длительность:", format_duration(2, 30))

    print("\n--- Конвертация ---")
    wa_text = "*Важно*: ```Базовая```  85$ взр / 60$ реб\n───────────────"
    print("Исходный WA:")
    print(wa_text)
    print("\nКонвертированный в TG:")
    print(convert_whatsapp_to_telegram(wa_text))
