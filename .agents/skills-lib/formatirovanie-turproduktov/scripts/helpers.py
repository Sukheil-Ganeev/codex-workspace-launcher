#!/usr/bin/env python3
"""Вспомогательные функции для форматирования турпродуктов."""

import re

def generate_separator(platform: str) -> str:
    """Генерирует разделитель для указанной платформы."""
    if platform.lower() == 'whatsapp':
        return '─' * 15
    elif platform.lower() == 'telegram':
        return '─' * 18
    else:
        raise ValueError(f"Неизвестная платформа: {platform}")

def format_price(adult: int, child: int = None) -> str:
    """Форматирует цену в стандартном формате."""
    if child:
        return f"{adult}$ взр / {child}$ реб"
    return f"{adult}$"

def format_category_whatsapp(category: str, price: str) -> str:
    """Форматирует категорию цены для WhatsApp."""
    return f"```{category}```  {price}"  # ДВА пробела!

def format_category_telegram(category: str, price: str) -> str:
    """Форматирует категорию цены для Telegram."""
    return f"**{category}** — {price}"

def convert_whatsapp_to_telegram(text: str) -> str:
    """Конвертирует текст из формата WhatsApp в Telegram."""
    # Заменяем одинарные на двойные
    result = text

    # *текст* -> **текст**
    result = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'**\1**', result)

    # _текст_ -> __текст__
    result = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'__\1__', result)

    # ```категория```  цена -> **категория** — цена
    result = re.sub(r'```([^`]+)```\s{2}(\d+\$)', r'**\1** — \2', result)

    # Разделитель 15 -> 18 тире
    result = re.sub(r'─{15}', '─' * 18, result)

    return result

if __name__ == "__main__":
    # Тестирование
    print("WhatsApp separator:", generate_separator('whatsapp'))
    print("Telegram separator:", generate_separator('telegram'))
    print("Price:", format_price(50, 35))
    print("Category WA:", format_category_whatsapp("Базовая", "50$ взр / 35$ реб"))
    print("Category TG:", format_category_telegram("Базовая", "50$ взр / 35$ реб"))
