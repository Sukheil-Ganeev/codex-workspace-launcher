#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ использования эмодзи в переписке WhatsApp.

Функции:
1. Извлечение всех эмодзи из сообщений
2. Частотный анализ по контактам
3. Sentiment mapping (позитив/негатив/вопрос/нейтрал)
4. Эмодзи-профиль контакта
5. Тренды использования по времени
6. Корреляция эмодзи с исходом сделки
7. Визуализация (word cloud из эмодзи)
8. Экспорт: JSON, PNG

ВАЖНЫЙ ПРИНЦИП: Никакие данные НЕ теряются! Сохранять ВСЕ данные полностью.
"""

import sys
import os
import re
import json
import argparse
import glob
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

sys.stdout.reconfigure(encoding='utf-8')

# Попытка импорта emoji библиотеки
try:
    import emoji
    EMOJI_LIB_AVAILABLE = True
except ImportError:
    EMOJI_LIB_AVAILABLE = False
    print("ПРЕДУПРЕЖДЕНИЕ: Библиотека 'emoji' не установлена. Установите: pip install emoji")

# Попытка импорта matplotlib и wordcloud для визуализации
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Импорт путей из config.py если доступен
try:
    from config import (
        CHATS_DIR, JSON_DIR, ANALYTICS_DIR,
        CONTACT_TYPES
    )
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    JSON_DIR = CHATS_DIR / "_база" / "json"
    ANALYTICS_DIR = CHATS_DIR / "_аналитика"
    CONTACT_TYPES = ["клиенты", "агенты", "поставщики", "сотрудники"]

# Директория для результатов эмодзи-анализа
EMOJI_OUTPUT_DIR = ANALYTICS_DIR / "emoji"

# ═══════════════════════════════════════════════════════════════
# SENTIMENT MAPPING - РАСШИРЕННЫЙ СЛОВАРЬ
# ═══════════════════════════════════════════════════════════════

# Позитивные эмодзи
POSITIVE_EMOJI = {
    # Улыбки и радость
    "😊": 0.8, "😃": 0.85, "😄": 0.85, "😁": 0.8, "🙂": 0.5, "😀": 0.8,
    "😆": 0.75, "☺️": 0.7, "☺": 0.7, "🤗": 0.8, "😍": 0.9, "🥰": 0.9,
    "😘": 0.85, "😗": 0.6, "😙": 0.6, "😚": 0.7, "🥲": 0.5,
    # Смех
    "😂": 0.7, "🤣": 0.7, "😹": 0.7, "😸": 0.7,
    # Позитивные жесты
    "👍": 0.7, "👍🏻": 0.7, "👍🏼": 0.7, "👍🏽": 0.7, "👍🏾": 0.7, "👍🏿": 0.7,
    "👌": 0.6, "👌🏻": 0.6, "✌️": 0.6, "✌": 0.6, "🤝": 0.7, "👏": 0.75,
    "🙌": 0.8, "💪": 0.7, "💪🏻": 0.7, "🤙": 0.6, "🤙🏻": 0.6,
    "👋": 0.5, "👋🏻": 0.5, "🙏": 0.7, "🙏🏻": 0.7,
    # Сердца
    "❤️": 0.85, "❤": 0.85, "💕": 0.8, "💗": 0.8, "💖": 0.85, "💓": 0.8,
    "💞": 0.8, "💘": 0.8, "🧡": 0.8, "💛": 0.8, "💚": 0.8, "💙": 0.8,
    "💜": 0.8, "🖤": 0.6, "🤍": 0.7, "🤎": 0.7, "💝": 0.85, "💟": 0.8,
    # Звёзды и праздник
    "⭐": 0.7, "🌟": 0.75, "✨": 0.7, "💫": 0.7, "🎉": 0.85, "🎊": 0.85,
    "🥳": 0.9, "🎁": 0.7, "🎈": 0.7, "🎄": 0.7, "🎂": 0.75,
    # Успех и подтверждение
    "✅": 0.8, "✓": 0.7, "☑️": 0.7, "💯": 0.85, "🔥": 0.75, "⚡": 0.6,
    "🏆": 0.85, "🥇": 0.9, "🥈": 0.8, "🥉": 0.75, "🎯": 0.7,
    # Природа и красота
    "🌈": 0.75, "☀️": 0.7, "🌸": 0.65, "🌺": 0.65, "🌹": 0.7, "💐": 0.7,
    "🌻": 0.65, "🌷": 0.65, "🌼": 0.6,
    # Еда (позитивные ассоциации)
    "☕": 0.5, "🍰": 0.6, "🍾": 0.75, "🥂": 0.8, "🍻": 0.7,
    # Другие позитивные
    "😎": 0.6, "🤩": 0.85, "😇": 0.7, "🤪": 0.6, "😜": 0.55, "😋": 0.6,
    "🙃": 0.4, "🤭": 0.5, "😏": 0.4, "🤓": 0.5,
}

# Негативные эмодзи
NEGATIVE_EMOJI = {
    # Грусть
    "😢": -0.7, "😭": -0.8, "😿": -0.7, "🥺": -0.5, "😞": -0.6, "😔": -0.6,
    "😕": -0.4, "🙁": -0.5, "☹️": -0.6, "☹": -0.6, "😩": -0.65, "😫": -0.65,
    "😥": -0.5, "😰": -0.5, "😓": -0.4,
    # Злость
    "😠": -0.8, "😡": -0.9, "🤬": -0.95, "😤": -0.7, "💢": -0.7,
    "👿": -0.8, "😈": -0.3,  # Может быть шуточным
    # Страх и шок
    "😱": -0.6, "😨": -0.5, "😰": -0.5, "🫣": -0.4, "😬": -0.4,
    # Негативные жесты
    "👎": -0.7, "👎🏻": -0.7, "👎🏼": -0.7, "👎🏽": -0.7, "👎🏾": -0.7, "👎🏿": -0.7,
    # Болезнь и плохое самочувствие
    "🤢": -0.7, "🤮": -0.8, "😵": -0.6, "🤕": -0.5, "🤒": -0.5,
    "😷": -0.3, "🥴": -0.4,
    # Смерть и опасность
    "💀": -0.5, "☠️": -0.5, "⚰️": -0.6,
    # Запреты и отмены
    "❌": -0.6, "❎": -0.5, "⛔": -0.6, "🚫": -0.5, "🛑": -0.5,
    "⚠️": -0.4, "🔴": -0.3,
    # Разочарование
    "😒": -0.5, "🙄": -0.4, "😑": -0.3, "😐": -0.2, "🫤": -0.3,
    # Сломанное
    "💔": -0.7, "🖤": -0.2,
}

# Вопросительные/неопределённые эмодзи
QUESTION_EMOJI = {
    "🤔": 0, "❓": 0, "❔": 0, "⁉️": 0, "🧐": 0,
    "🤷": 0, "🤷‍♂️": 0, "🤷‍♀️": 0, "🤷🏻": 0, "🤷🏻‍♂️": 0, "🤷🏻‍♀️": 0,
    "🙋": 0, "🙋‍♂️": 0, "🙋‍♀️": 0,
    "💭": 0, "🔍": 0, "👀": 0,
}

# Нейтральные эмодзи
NEUTRAL_EMOJI = {
    "😶": 0, "😐": 0, "🫡": 0, "🫠": 0,
    # Информационные
    "📷": 0, "📹": 0, "🎤": 0, "📍": 0, "📎": 0, "📄": 0, "📁": 0,
    "📱": 0, "💻": 0, "⌚": 0, "🕐": 0, "📅": 0, "📆": 0,
    # Транспорт (для туризма)
    "🚗": 0, "🚙": 0, "🚕": 0, "✈️": 0, "🛫": 0, "🛬": 0, "🚢": 0, "🛥️": 0,
    "🚁": 0, "🏎️": 0, "🏍️": 0,
    # Деньги и бизнес
    "💰": 0, "💵": 0, "💴": 0, "💶": 0, "💷": 0, "💳": 0, "🏦": 0,
    "📊": 0, "📈": 0, "📉": 0,
    # Места и туризм
    "🏨": 0, "🏖️": 0, "🏝️": 0, "🏜️": 0, "🗺️": 0, "🧭": 0,
    "🕌": 0, "🕋": 0, "🏛️": 0, "🗼": 0,
    # Флаги
    "🇦🇪": 0, "🇷🇺": 0, "🇺🇸": 0, "🇬🇧": 0, "🇩🇪": 0, "🇫🇷": 0,
    "🇮🇹": 0, "🇪🇸": 0, "🇨🇳": 0, "🇯🇵": 0, "🇰🇷": 0, "🇮🇳": 0,
    "🇰🇿": 0, "🇺🇿": 0, "🇧🇾": 0, "🇺🇦": 0,
}

# Категории эмодзи для профилирования
EMOJI_CATEGORIES = {
    "радость": ["😊", "😃", "😄", "😁", "🥳", "🎉", "🎊", "😍", "🥰", "🤗"],
    "благодарность": ["🙏", "🙏🏻", "❤️", "💕", "👏", "🤝"],
    "согласие": ["👍", "👍🏻", "👌", "✅", "☑️", "💯", "🔥"],
    "приветствие": ["👋", "👋🏻", "🤗", "😊", "🙂"],
    "грусть": ["😢", "😭", "😞", "😔", "🥺", "💔"],
    "злость": ["😠", "😡", "🤬", "😤", "💢"],
    "разочарование": ["😒", "🙄", "😕", "🙁", "☹️"],
    "вопрос": ["🤔", "❓", "🤷", "🤷‍♂️", "🤷‍♀️", "🧐"],
    "деньги": ["💰", "💵", "💳", "🏦", "💸"],
    "путешествия": ["✈️", "🚗", "🏨", "🏖️", "🗺️", "🧳"],
    "время": ["⏰", "🕐", "📅", "⏳", "⌚"],
    "документы": ["📄", "📎", "📁", "📋", "✍️"],
}


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ИЗВЛЕЧЕНИЯ ЭМОДЗИ
# ═══════════════════════════════════════════════════════════════

def extract_emoji_with_library(text: str) -> List[str]:
    """Извлекает эмодзи используя библиотеку emoji."""
    if not EMOJI_LIB_AVAILABLE:
        return extract_emoji_regex(text)

    emoji_list = []
    for char in text:
        if emoji.is_emoji(char):
            emoji_list.append(char)

    # Также извлекаем составные эмодзи (с модификаторами)
    emoji_data = emoji.emoji_list(text)
    for item in emoji_data:
        emoji_char = item['emoji']
        if emoji_char not in emoji_list:
            emoji_list.append(emoji_char)

    return emoji_list


def extract_emoji_regex(text: str) -> List[str]:
    """Извлекает эмодзи используя регулярные выражения (fallback)."""
    # Unicode диапазоны для эмодзи
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(text)


def extract_all_emoji(text: str) -> List[str]:
    """Основная функция извлечения эмодзи."""
    if EMOJI_LIB_AVAILABLE:
        return extract_emoji_with_library(text)
    return extract_emoji_regex(text)


# ═══════════════════════════════════════════════════════════════
# SENTIMENT АНАЛИЗ
# ═══════════════════════════════════════════════════════════════

def get_emoji_sentiment(emoji_char: str) -> Tuple[str, float]:
    """Определяет sentiment для конкретного эмодзи."""
    if emoji_char in POSITIVE_EMOJI:
        return "positive", POSITIVE_EMOJI[emoji_char]
    elif emoji_char in NEGATIVE_EMOJI:
        return "negative", NEGATIVE_EMOJI[emoji_char]
    elif emoji_char in QUESTION_EMOJI:
        return "question", 0.0
    elif emoji_char in NEUTRAL_EMOJI:
        return "neutral", 0.0
    else:
        return "unknown", 0.0


def analyze_message_emoji_sentiment(text: str) -> Dict[str, Any]:
    """Анализирует sentiment эмодзи в сообщении."""
    emojis = extract_all_emoji(text)

    if not emojis:
        return {
            "emoji_count": 0,
            "emojis": [],
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "categories": {}
        }

    sentiment_scores = []
    categories = defaultdict(int)
    emoji_details = []

    for em in emojis:
        sentiment, score = get_emoji_sentiment(em)
        sentiment_scores.append(score)
        emoji_details.append({
            "emoji": em,
            "sentiment": sentiment,
            "score": score
        })

        # Определяем категорию
        for cat, cat_emojis in EMOJI_CATEGORIES.items():
            if em in cat_emojis:
                categories[cat] += 1

    # Общий sentiment
    avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    if avg_score > 0.2:
        overall_sentiment = "positive"
    elif avg_score < -0.2:
        overall_sentiment = "negative"
    elif any(em in QUESTION_EMOJI for em in emojis):
        overall_sentiment = "question"
    else:
        overall_sentiment = "neutral"

    return {
        "emoji_count": len(emojis),
        "emojis": emoji_details,
        "sentiment": overall_sentiment,
        "sentiment_score": round(avg_score, 3),
        "categories": dict(categories)
    }


# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_messages_jsonl(filepath: str) -> List[Dict]:
    """Загружает сообщения из JSONL файла."""
    messages = []

    if not os.path.exists(filepath):
        return messages

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")

    return messages


def load_chat_markdown(filepath: str) -> List[Dict]:
    """Загружает сообщения из Markdown файла чата."""
    messages = []

    if not os.path.exists(filepath):
        return messages

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")
        return messages

    # Паттерн для сообщений: **👤 Имя** [HH:MM:SS]
    # или **👨 Владелец** [HH:MM:SS]
    message_pattern = re.compile(
        r'\*\*([👤👨👩][^*]+)\*\*\s*\[(\d{2}:\d{2}:\d{2})\]\s*\n(.*?)(?=\*\*[👤👨👩]|\Z|---|\n###)',
        re.DOTALL
    )

    current_date = None
    date_pattern = re.compile(r'### (\d{2}\.\d{2}\.\d{4})')

    # Находим все даты
    date_positions = []
    for match in date_pattern.finditer(content):
        date_positions.append((match.start(), match.group(1)))

    # Находим все сообщения
    for match in message_pattern.finditer(content):
        sender = match.group(1).strip()
        time = match.group(2)
        text = match.group(3).strip()

        # Определяем дату по позиции
        msg_pos = match.start()
        msg_date = None
        for pos, date in reversed(date_positions):
            if pos < msg_pos:
                msg_date = date
                break

        # Парсим дату и время
        timestamp = None
        if msg_date:
            try:
                dt = datetime.strptime(f"{msg_date} {time}", "%d.%m.%Y %H:%M:%S")
                timestamp = dt.isoformat()
            except:
                pass

        messages.append({
            "sender": sender,
            "time": time,
            "date": msg_date,
            "timestamp": timestamp,
            "text": text,
            "source_file": filepath
        })

    return messages


def load_operations_data(filepath: str) -> List[Dict]:
    """Загружает данные об операциях для корреляции."""
    operations = []

    if not os.path.exists(filepath):
        return operations

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                operations = data
            elif isinstance(data, dict) and 'operations' in data:
                operations = data['operations']
    except:
        pass

    return operations


# ═══════════════════════════════════════════════════════════════
# ЧАСТОТНЫЙ АНАЛИЗ
# ═══════════════════════════════════════════════════════════════

def frequency_analysis(messages: List[Dict]) -> Dict[str, Any]:
    """Частотный анализ эмодзи по всем сообщениям."""
    total_counter = Counter()
    by_sender = defaultdict(Counter)
    by_date = defaultdict(Counter)
    by_hour = defaultdict(Counter)

    for msg in messages:
        text = msg.get('text', '') or msg.get('message', '') or msg.get('content', '')
        sender = msg.get('sender', 'Unknown')
        date = msg.get('date', '')
        time = msg.get('time', '')

        emojis = extract_all_emoji(text)

        for em in emojis:
            total_counter[em] += 1
            by_sender[sender][em] += 1

            if date:
                by_date[date][em] += 1

            if time:
                try:
                    hour = int(time.split(':')[0])
                    by_hour[hour][em] += 1
                except:
                    pass

    return {
        "total": dict(total_counter.most_common(100)),
        "by_sender": {
            sender: dict(counter.most_common(20))
            for sender, counter in by_sender.items()
        },
        "by_date": {
            date: dict(counter.most_common(10))
            for date, counter in sorted(by_date.items())[-30:]  # Последние 30 дней
        },
        "by_hour": {
            str(hour): dict(counter.most_common(10))
            for hour, counter in sorted(by_hour.items())
        },
        "unique_emoji_count": len(total_counter),
        "total_emoji_count": sum(total_counter.values())
    }


# ═══════════════════════════════════════════════════════════════
# ЭМОДЗИ-ПРОФИЛЬ КОНТАКТА
# ═══════════════════════════════════════════════════════════════

def build_contact_profile(messages: List[Dict], contact_name: str = None) -> Dict[str, Any]:
    """Создаёт эмодзи-профиль для контакта."""
    # Фильтруем по контакту если указан
    if contact_name:
        contact_messages = [
            m for m in messages
            if contact_name.lower() in m.get('sender', '').lower()
        ]
    else:
        contact_messages = messages

    if not contact_messages:
        return {}

    # Собираем статистику
    emoji_counter = Counter()
    sentiment_counts = defaultdict(int)
    category_counts = defaultdict(int)
    timeline = []

    for msg in contact_messages:
        text = msg.get('text', '') or msg.get('message', '') or msg.get('content', '')
        analysis = analyze_message_emoji_sentiment(text)

        if analysis['emoji_count'] > 0:
            for em_detail in analysis['emojis']:
                emoji_counter[em_detail['emoji']] += 1
                sentiment_counts[em_detail['sentiment']] += 1

            for cat, count in analysis['categories'].items():
                category_counts[cat] += count

            timeline.append({
                "date": msg.get('date', ''),
                "time": msg.get('time', ''),
                "emoji_count": analysis['emoji_count'],
                "sentiment": analysis['sentiment'],
                "score": analysis['sentiment_score']
            })

    # Топ эмодзи
    top_emoji = emoji_counter.most_common(10)

    # Доминирующий sentiment
    total_sentiments = sum(sentiment_counts.values())
    sentiment_distribution = {
        k: round(v / total_sentiments, 3) if total_sentiments > 0 else 0
        for k, v in sentiment_counts.items()
    }

    # Определяем тип профиля
    if sentiment_distribution.get('positive', 0) > 0.6:
        profile_type = "позитивный"
    elif sentiment_distribution.get('negative', 0) > 0.4:
        profile_type = "негативный"
    elif sentiment_distribution.get('question', 0) > 0.3:
        profile_type = "вопросительный"
    else:
        profile_type = "нейтральный"

    # Топ категории
    top_categories = sorted(
        category_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return {
        "contact": contact_name or "all",
        "total_messages": len(contact_messages),
        "messages_with_emoji": len(timeline),
        "emoji_usage_rate": round(len(timeline) / len(contact_messages), 3) if contact_messages else 0,
        "top_emoji": [{"emoji": e, "count": c} for e, c in top_emoji],
        "sentiment_distribution": sentiment_distribution,
        "profile_type": profile_type,
        "top_categories": [{"category": c, "count": n} for c, n in top_categories],
        "timeline_sample": timeline[:20]  # Первые 20 для примера
    }


# ═══════════════════════════════════════════════════════════════
# ТРЕНДЫ ИСПОЛЬЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════

def analyze_trends(messages: List[Dict]) -> Dict[str, Any]:
    """Анализирует тренды использования эмодзи по времени."""
    daily_stats = defaultdict(lambda: {
        "total_messages": 0,
        "messages_with_emoji": 0,
        "emoji_count": 0,
        "sentiment_sum": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "question": 0
    })

    weekly_emoji = defaultdict(Counter)

    for msg in messages:
        date = msg.get('date', '')
        text = msg.get('text', '') or msg.get('message', '') or msg.get('content', '')

        if not date:
            continue

        daily_stats[date]["total_messages"] += 1

        analysis = analyze_message_emoji_sentiment(text)

        if analysis['emoji_count'] > 0:
            daily_stats[date]["messages_with_emoji"] += 1
            daily_stats[date]["emoji_count"] += analysis['emoji_count']
            daily_stats[date]["sentiment_sum"] += analysis['sentiment_score']
            daily_stats[date][analysis['sentiment']] += 1

            for em_detail in analysis['emojis']:
                weekly_emoji[date[:7]][em_detail['emoji']] += 1  # YYYY-MM

    # Формируем тренды
    trends = []
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        with_emoji = stats["messages_with_emoji"]

        trends.append({
            "date": date,
            "total_messages": stats["total_messages"],
            "messages_with_emoji": with_emoji,
            "emoji_per_message": round(stats["emoji_count"] / with_emoji, 2) if with_emoji > 0 else 0,
            "avg_sentiment": round(stats["sentiment_sum"] / with_emoji, 3) if with_emoji > 0 else 0,
            "sentiment_breakdown": {
                "positive": stats["positive"],
                "negative": stats["negative"],
                "neutral": stats["neutral"],
                "question": stats["question"]
            }
        })

    # Месячные топ эмодзи
    monthly_top = {
        month: dict(counter.most_common(5))
        for month, counter in sorted(weekly_emoji.items())
    }

    return {
        "daily_trends": trends[-30:],  # Последние 30 дней
        "monthly_top_emoji": monthly_top,
        "total_days_analyzed": len(trends)
    }


# ═══════════════════════════════════════════════════════════════
# КОРРЕЛЯЦИЯ С ИСХОДОМ СДЕЛКИ
# ═══════════════════════════════════════════════════════════════

def correlate_with_deals(messages: List[Dict], operations: List[Dict] = None) -> Dict[str, Any]:
    """Анализирует корреляцию эмодзи с исходом сделок."""

    # Ключевые слова успешных сделок
    SUCCESS_KEYWORDS = [
        "оплачено", "оплатил", "оплатила", "получили", "подтверждаю",
        "готово", "сделано", "забронировано", "бронь подтверждена",
        "спасибо за заказ", "ждём вас", "до встречи", "приятного",
        "successfully", "confirmed", "paid", "booked"
    ]

    # Ключевые слова отменённых сделок
    CANCEL_KEYWORDS = [
        "отмена", "отменили", "отменить", "не получится", "не подходит",
        "передумал", "передумала", "cancelled", "cancel", "refund",
        "возврат", "не можем", "не будем", "отказываюсь"
    ]

    success_emoji = Counter()
    cancel_emoji = Counter()
    neutral_emoji = Counter()

    for msg in messages:
        text = msg.get('text', '') or msg.get('message', '') or msg.get('content', '')
        text_lower = text.lower()

        emojis = extract_all_emoji(text)
        if not emojis:
            continue

        # Определяем контекст сообщения
        is_success = any(kw in text_lower for kw in SUCCESS_KEYWORDS)
        is_cancel = any(kw in text_lower for kw in CANCEL_KEYWORDS)

        for em in emojis:
            if is_success:
                success_emoji[em] += 1
            elif is_cancel:
                cancel_emoji[em] += 1
            else:
                neutral_emoji[em] += 1

    # Анализ операций если есть
    deal_analysis = None
    if operations:
        completed_ops = [op for op in operations if op.get('status') in ['completed', 'Исполнен', 'Выполнен']]
        cancelled_ops = [op for op in operations if op.get('status') in ['cancelled', 'Отменён', 'Отклонён']]

        deal_analysis = {
            "total_operations": len(operations),
            "completed": len(completed_ops),
            "cancelled": len(cancelled_ops),
            "completion_rate": round(len(completed_ops) / len(operations), 3) if operations else 0
        }

    return {
        "success_context_emoji": dict(success_emoji.most_common(10)),
        "cancel_context_emoji": dict(cancel_emoji.most_common(10)),
        "neutral_context_emoji": dict(neutral_emoji.most_common(10)),
        "success_emoji_count": sum(success_emoji.values()),
        "cancel_emoji_count": sum(cancel_emoji.values()),
        "deal_analysis": deal_analysis,
        "insights": generate_correlation_insights(success_emoji, cancel_emoji)
    }


def generate_correlation_insights(success: Counter, cancel: Counter) -> List[str]:
    """Генерирует инсайты из корреляционного анализа."""
    insights = []

    # Топ успешные
    if success:
        top_success = success.most_common(3)
        emojis_str = " ".join([e for e, _ in top_success])
        insights.append(f"Эмодзи успешных сделок: {emojis_str}")

    # Топ отмены
    if cancel:
        top_cancel = cancel.most_common(3)
        emojis_str = " ".join([e for e, _ in top_cancel])
        insights.append(f"Эмодзи отменённых сделок: {emojis_str}")

    # Соотношение
    total_success = sum(success.values())
    total_cancel = sum(cancel.values())
    if total_success + total_cancel > 0:
        ratio = total_success / (total_success + total_cancel)
        if ratio > 0.7:
            insights.append("Высокий уровень позитивных эмодзи в контексте сделок")
        elif ratio < 0.3:
            insights.append("Много негативных эмодзи в контексте сделок - требует внимания")

    return insights


# ═══════════════════════════════════════════════════════════════
# ВИЗУАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

def create_emoji_wordcloud(emoji_counts: Dict[str, int], output_path: str, title: str = "Emoji Cloud") -> bool:
    """Создаёт word cloud из эмодзи."""
    if not MATPLOTLIB_AVAILABLE or not WORDCLOUD_AVAILABLE:
        print("Для визуализации требуются: pip install matplotlib wordcloud")
        return False

    if not emoji_counts:
        print("Нет данных для визуализации")
        return False

    try:
        # Создаём текст из эмодзи (повторяем по частоте)
        emoji_text = " ".join([
            " ".join([em] * count)
            for em, count in emoji_counts.items()
        ])

        # Находим шрифт с поддержкой эмодзи
        # Windows: Segoe UI Emoji, macOS: Apple Color Emoji
        font_paths = [
            "C:/Windows/Fonts/seguiemj.ttf",  # Windows
            "C:/Windows/Fonts/segoe ui emoji.ttf",
            "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
        ]

        font_path = None
        for fp in font_paths:
            if os.path.exists(fp):
                font_path = fp
                break

        # Создаём WordCloud
        wc = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            font_path=font_path,
            max_words=100,
            prefer_horizontal=0.9,
            min_font_size=10,
            max_font_size=100,
            colormap='viridis'
        )

        # Генерируем из частот напрямую
        wc.generate_from_frequencies(emoji_counts)

        # Создаём график
        plt.figure(figsize=(15, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=20, pad=20)

        # Сохраняем
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"Word cloud сохранён: {output_path}")
        return True

    except Exception as e:
        print(f"Ошибка создания word cloud: {e}")
        return False


def create_sentiment_chart(trends: List[Dict], output_path: str) -> bool:
    """Создаёт график динамики sentiment."""
    if not MATPLOTLIB_AVAILABLE:
        print("Для визуализации требуется: pip install matplotlib")
        return False

    if not trends:
        return False

    try:
        dates = [t['date'] for t in trends]
        sentiments = [t['avg_sentiment'] for t in trends]
        emoji_counts = [t['messages_with_emoji'] for t in trends]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # График sentiment
        colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiments]
        ax1.bar(range(len(dates)), sentiments, color=colors, alpha=0.7)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_ylabel('Средний Sentiment Score')
        ax1.set_title('Динамика Emoji Sentiment')
        ax1.set_ylim(-1, 1)

        # График количества
        ax2.plot(range(len(dates)), emoji_counts, 'b-o', markersize=4)
        ax2.fill_between(range(len(dates)), emoji_counts, alpha=0.3)
        ax2.set_ylabel('Сообщений с эмодзи')
        ax2.set_xlabel('Дата')

        # Подписи дат (каждая 5-я)
        step = max(1, len(dates) // 10)
        ax2.set_xticks(range(0, len(dates), step))
        ax2.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45, ha='right')

        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"График sentiment сохранён: {output_path}")
        return True

    except Exception as e:
        print(f"Ошибка создания графика: {e}")
        return False


def create_contact_comparison_chart(profiles: List[Dict], output_path: str) -> bool:
    """Создаёт сравнительный график профилей контактов."""
    if not MATPLOTLIB_AVAILABLE:
        return False

    if not profiles:
        return False

    try:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # График 1: Использование эмодзи
        contacts = [p['contact'][:15] for p in profiles[:10]]
        usage_rates = [p['emoji_usage_rate'] * 100 for p in profiles[:10]]

        ax1 = axes[0]
        bars = ax1.barh(contacts, usage_rates, color='steelblue', alpha=0.7)
        ax1.set_xlabel('% сообщений с эмодзи')
        ax1.set_title('Частота использования эмодзи')
        ax1.invert_yaxis()

        # График 2: Распределение sentiment
        ax2 = axes[1]

        positive = [p['sentiment_distribution'].get('positive', 0) * 100 for p in profiles[:10]]
        negative = [p['sentiment_distribution'].get('negative', 0) * 100 for p in profiles[:10]]
        neutral = [p['sentiment_distribution'].get('neutral', 0) * 100 for p in profiles[:10]]

        y_pos = range(len(contacts))
        ax2.barh(y_pos, positive, label='Позитив', color='green', alpha=0.7)
        ax2.barh(y_pos, negative, left=positive, label='Негатив', color='red', alpha=0.7)
        ax2.barh(y_pos, neutral, left=[p+n for p,n in zip(positive, negative)],
                 label='Нейтрал', color='gray', alpha=0.7)

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(contacts)
        ax2.set_xlabel('% от всех эмодзи')
        ax2.set_title('Sentiment распределение')
        ax2.legend(loc='lower right')
        ax2.invert_yaxis()

        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"График сравнения сохранён: {output_path}")
        return True

    except Exception as e:
        print(f"Ошибка создания графика: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════════════════════════════

def export_results(
    frequency: Dict,
    profiles: List[Dict],
    trends: Dict,
    correlations: Dict,
    output_dir: Path
) -> Dict[str, str]:
    """Экспортирует все результаты в JSON."""
    os.makedirs(output_dir, exist_ok=True)

    exported_files = {}

    # Частотный анализ
    freq_path = output_dir / "emoji_frequency.json"
    with open(freq_path, 'w', encoding='utf-8') as f:
        json.dump(frequency, f, ensure_ascii=False, indent=2)
    exported_files['frequency'] = str(freq_path)

    # Профили контактов
    profiles_path = output_dir / "emoji_profiles.json"
    with open(profiles_path, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)
    exported_files['profiles'] = str(profiles_path)

    # Тренды
    trends_path = output_dir / "emoji_trends.json"
    with open(trends_path, 'w', encoding='utf-8') as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)
    exported_files['trends'] = str(trends_path)

    # Корреляции
    corr_path = output_dir / "emoji_correlations.json"
    with open(corr_path, 'w', encoding='utf-8') as f:
        json.dump(correlations, f, ensure_ascii=False, indent=2)
    exported_files['correlations'] = str(corr_path)

    # Сводный отчёт
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_unique_emoji": frequency.get('unique_emoji_count', 0),
        "total_emoji_used": frequency.get('total_emoji_count', 0),
        "contacts_analyzed": len(profiles),
        "days_analyzed": trends.get('total_days_analyzed', 0),
        "top_10_emoji": list(frequency.get('total', {}).items())[:10],
        "insights": correlations.get('insights', [])
    }

    summary_path = output_dir / "emoji_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    exported_files['summary'] = str(summary_path)

    return exported_files


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def analyze_chat_emoji(
    input_path: str,
    output_dir: str = None,
    create_visuals: bool = True
) -> Dict[str, Any]:
    """
    Полный анализ эмодзи для чата или папки чатов.

    Args:
        input_path: Путь к файлу чата (.md/.jsonl) или папке
        output_dir: Папка для результатов (по умолчанию EMOJI_OUTPUT_DIR)
        create_visuals: Создавать визуализации

    Returns:
        Словарь с результатами анализа
    """
    output_path = Path(output_dir) if output_dir else EMOJI_OUTPUT_DIR
    os.makedirs(output_path, exist_ok=True)

    print(f"\n{'='*60}")
    print("АНАЛИЗ ЭМОДЗИ В ПЕРЕПИСКЕ")
    print(f"{'='*60}")

    # Загружаем сообщения
    messages = []
    input_p = Path(input_path)

    if input_p.is_file():
        print(f"\nЗагрузка файла: {input_path}")
        if input_p.suffix == '.jsonl':
            messages = load_messages_jsonl(str(input_p))
        else:
            messages = load_chat_markdown(str(input_p))
    elif input_p.is_dir():
        print(f"\nСканирование папки: {input_path}")
        # Ищем все .md и .jsonl файлы
        for pattern in ['**/*.md', '**/*.jsonl']:
            for fp in input_p.glob(pattern):
                if fp.suffix == '.jsonl':
                    messages.extend(load_messages_jsonl(str(fp)))
                else:
                    messages.extend(load_chat_markdown(str(fp)))
    else:
        print(f"Путь не найден: {input_path}")
        return {}

    print(f"Загружено сообщений: {len(messages)}")

    if not messages:
        print("Нет сообщений для анализа")
        return {}

    # 1. Частотный анализ
    print("\n[1/5] Частотный анализ...")
    frequency = frequency_analysis(messages)
    print(f"  Уникальных эмодзи: {frequency['unique_emoji_count']}")
    print(f"  Всего использований: {frequency['total_emoji_count']}")

    # 2. Профили контактов
    print("\n[2/5] Построение профилей контактов...")
    senders = set()
    for msg in messages:
        sender = msg.get('sender', '')
        if sender and sender != 'Unknown':
            senders.add(sender)

    profiles = []
    for sender in senders:
        profile = build_contact_profile(messages, sender)
        if profile and profile.get('messages_with_emoji', 0) > 0:
            profiles.append(profile)

    # Сортируем по количеству эмодзи
    profiles.sort(key=lambda x: x.get('messages_with_emoji', 0), reverse=True)
    print(f"  Контактов с эмодзи: {len(profiles)}")

    # 3. Тренды
    print("\n[3/5] Анализ трендов...")
    trends = analyze_trends(messages)
    print(f"  Проанализировано дней: {trends['total_days_analyzed']}")

    # 4. Корреляции
    print("\n[4/5] Корреляция с исходами сделок...")
    correlations = correlate_with_deals(messages)
    for insight in correlations.get('insights', []):
        print(f"  - {insight}")

    # 5. Экспорт JSON
    print("\n[5/5] Экспорт результатов...")
    exported = export_results(frequency, profiles, trends, correlations, output_path)
    for name, path in exported.items():
        print(f"  {name}: {path}")

    # Визуализации
    if create_visuals:
        print("\n[ВИЗУАЛИЗАЦИЯ]")

        # Word Cloud
        wc_path = output_path / "emoji_wordcloud.png"
        create_emoji_wordcloud(frequency.get('total', {}), str(wc_path), "Emoji Word Cloud")

        # Sentiment Chart
        if trends.get('daily_trends'):
            chart_path = output_path / "emoji_sentiment_chart.png"
            create_sentiment_chart(trends['daily_trends'], str(chart_path))

        # Сравнение контактов
        if profiles:
            comp_path = output_path / "emoji_contacts_comparison.png"
            create_contact_comparison_chart(profiles, str(comp_path))

    print(f"\n{'='*60}")
    print(f"АНАЛИЗ ЗАВЕРШЁН")
    print(f"Результаты: {output_path}")
    print(f"{'='*60}\n")

    return {
        "frequency": frequency,
        "profiles": profiles,
        "trends": trends,
        "correlations": correlations,
        "exported_files": exported
    }


def process_all_chats(chats_dir: str = None) -> Dict[str, Any]:
    """Обрабатывает все чаты в директории."""
    chats_path = Path(chats_dir) if chats_dir else CHATS_DIR

    all_messages = []

    for contact_type in CONTACT_TYPES:
        type_dir = chats_path / contact_type
        if type_dir.exists():
            for chat_file in type_dir.glob("*.md"):
                messages = load_chat_markdown(str(chat_file))
                for msg in messages:
                    msg['contact_type'] = contact_type
                all_messages.extend(messages)

    if all_messages:
        return analyze_chat_emoji(
            str(chats_path),
            str(EMOJI_OUTPUT_DIR),
            create_visuals=True
        )

    return {}


# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Анализ эмодзи в переписке WhatsApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python analyze_emoji.py chat.md                  # Анализ одного файла
  python analyze_emoji.py D:/Downloads/Chats       # Анализ папки
  python analyze_emoji.py --all                    # Все чаты в стандартной папке
  python analyze_emoji.py chat.md --no-visuals     # Без визуализаций
  python analyze_emoji.py chat.md -o ./results     # Указать папку для результатов
        """
    )

    parser.add_argument(
        "input",
        nargs='?',
        help="Путь к файлу чата (.md/.jsonl) или папке с чатами"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Обработать все чаты в стандартной папке"
    )

    parser.add_argument(
        "-o", "--output",
        help="Папка для сохранения результатов"
    )

    parser.add_argument(
        "--no-visuals",
        action="store_true",
        help="Не создавать визуализации (только JSON)"
    )

    parser.add_argument(
        "--chats-dir",
        default=str(CHATS_DIR),
        help=f"Папка с чатами (по умолчанию: {CHATS_DIR})"
    )

    args = parser.parse_args()

    # Проверка зависимостей
    if not EMOJI_LIB_AVAILABLE:
        print("\n⚠️  РЕКОМЕНДАЦИЯ: Установите библиотеку emoji для точного извлечения:")
        print("   pip install emoji\n")

    # Выполнение
    if args.all:
        result = process_all_chats(args.chats_dir)
    elif args.input:
        result = analyze_chat_emoji(
            args.input,
            args.output,
            create_visuals=not args.no_visuals
        )
    else:
        parser.print_help()
        sys.exit(1)

    # Вывод краткой статистики
    if result:
        freq = result.get('frequency', {})
        print("\n📊 КРАТКАЯ СТАТИСТИКА:")
        print(f"   Уникальных эмодзи: {freq.get('unique_emoji_count', 0)}")
        print(f"   Всего использований: {freq.get('total_emoji_count', 0)}")

        top5 = list(freq.get('total', {}).items())[:5]
        if top5:
            print(f"   Топ-5: {' '.join([e for e, _ in top5])}")
