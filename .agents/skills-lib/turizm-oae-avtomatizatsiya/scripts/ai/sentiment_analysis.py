#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ настроения клиентов в переписке WhatsApp.

Функции:
1. Определение sentiment для каждого сообщения (positive/neutral/negative)
2. Анализ на уровне чата (общий score, динамика, точки падения)
3. Методы: rule-based словари (ru/en/ar), emoji, пунктуация
4. Отчёты: sentiment_by_contact.json, sentiment_trends.json, alerts.json
5. Визуализация: графики sentiment по времени, heatmap по дням недели

ВАЖНЫЙ ПРИНЦИП: Никакие данные НЕ теряются! Сохранять ВСЕ данные полностью.
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# СЛОВАРИ НАСТРОЕНИЙ (RU/EN/AR)
# ═══════════════════════════════════════════════════════════════

# Русский язык - позитивные слова
POSITIVE_WORDS_RU = {
    # Благодарность
    "спасибо": 0.8, "благодарю": 0.9, "благодарим": 0.9, "признателен": 0.85,
    "признательна": 0.85, "благодарность": 0.85,
    # Удовлетворение
    "отлично": 0.9, "превосходно": 0.95, "замечательно": 0.9, "великолепно": 0.95,
    "прекрасно": 0.9, "чудесно": 0.9, "восхитительно": 0.95, "потрясающе": 0.95,
    "супер": 0.85, "класс": 0.8, "круто": 0.8, "здорово": 0.8, "шикарно": 0.9,
    # Согласие/одобрение
    "хорошо": 0.6, "да": 0.3, "конечно": 0.5, "согласен": 0.5, "согласна": 0.5,
    "договорились": 0.6, "идёт": 0.4, "подходит": 0.5, "устраивает": 0.6,
    # Радость
    "рад": 0.7, "рада": 0.7, "рады": 0.7, "счастлив": 0.9, "счастлива": 0.9,
    "доволен": 0.8, "довольна": 0.8, "довольны": 0.8,
    # Комплименты
    "молодец": 0.8, "молодцы": 0.8, "умница": 0.8, "профессионал": 0.85,
    "профессионально": 0.85, "качественно": 0.7,
    # Интерес
    "интересно": 0.6, "понравилось": 0.8, "нравится": 0.7, "впечатлило": 0.85,
    "впечатляет": 0.8, "удивили": 0.7,
    # Рекомендации
    "рекомендую": 0.85, "советую": 0.8, "буду советовать": 0.85,
    # Позитивные фразы
    "всё отлично": 0.9, "всё хорошо": 0.7, "всё супер": 0.85,
    "очень понравилось": 0.9, "очень довольны": 0.9,
}

# Русский язык - негативные слова
NEGATIVE_WORDS_RU = {
    # Недовольство
    "плохо": -0.7, "ужасно": -0.9, "отвратительно": -0.95, "кошмар": -0.9,
    "катастрофа": -0.95, "провал": -0.8, "разочарование": -0.8,
    "разочарован": -0.8, "разочарована": -0.8,
    # Жалобы
    "жалоба": -0.8, "жалуюсь": -0.75, "недоволен": -0.7, "недовольна": -0.7,
    "недовольны": -0.7, "возмущён": -0.85, "возмущена": -0.85,
    # Проблемы
    "проблема": -0.5, "проблемы": -0.5, "сложности": -0.4, "трудности": -0.4,
    "неприятности": -0.6, "беда": -0.7, "ошибка": -0.5, "ошибки": -0.5,
    # Качество
    "некачественно": -0.7, "некачественный": -0.7, "брак": -0.7,
    "испорчено": -0.7, "сломано": -0.6, "не работает": -0.6,
    # Сервис
    "опоздали": -0.6, "опоздание": -0.55, "долго": -0.4, "ждать": -0.3,
    "задержка": -0.5, "не ответили": -0.6, "игнорируют": -0.7,
    # Отмены/возвраты
    "отмена": -0.5, "отменить": -0.4, "возврат": -0.5, "вернуть деньги": -0.7,
    # Цена
    "дорого": -0.5, "переплата": -0.6, "завышено": -0.6, "грабёж": -0.8,
    # Обман
    "обман": -0.9, "обманули": -0.9, "мошенники": -0.95, "развод": -0.85,
    # Эмоции
    "злой": -0.7, "злая": -0.7, "злость": -0.7, "бесит": -0.8, "раздражает": -0.7,
    "надоело": -0.6, "достало": -0.7, "устал": -0.4, "устала": -0.4,
    # Отрицание
    "нет": -0.2, "не хочу": -0.4, "не буду": -0.4, "отказываюсь": -0.5,
    "не нужно": -0.4, "не надо": -0.3, "не могу": -0.3,
    # Негативные фразы
    "не понравилось": -0.7, "не устраивает": -0.6, "не подходит": -0.5,
    "не соответствует": -0.6, "хуже некуда": -0.9,
}

# Английский язык - позитивные слова
POSITIVE_WORDS_EN = {
    # Gratitude
    "thanks": 0.7, "thank you": 0.8, "appreciate": 0.8, "grateful": 0.85,
    # Satisfaction
    "excellent": 0.9, "amazing": 0.9, "wonderful": 0.9, "fantastic": 0.9,
    "great": 0.8, "good": 0.6, "nice": 0.6, "perfect": 0.95, "awesome": 0.85,
    "brilliant": 0.9, "superb": 0.9, "outstanding": 0.95,
    # Agreement
    "yes": 0.3, "ok": 0.3, "okay": 0.3, "sure": 0.4, "agreed": 0.5,
    "fine": 0.4, "alright": 0.4,
    # Happiness
    "happy": 0.8, "glad": 0.7, "pleased": 0.75, "satisfied": 0.75,
    "delighted": 0.85, "thrilled": 0.9, "excited": 0.8,
    # Compliments
    "professional": 0.8, "helpful": 0.75, "friendly": 0.7, "kind": 0.7,
    # Interest
    "interesting": 0.6, "love": 0.85, "like": 0.6, "enjoy": 0.7, "enjoyed": 0.75,
    # Recommendations
    "recommend": 0.8, "highly recommend": 0.9,
}

# Английский язык - негативные слова
NEGATIVE_WORDS_EN = {
    # Dissatisfaction
    "bad": -0.7, "terrible": -0.9, "horrible": -0.9, "awful": -0.85,
    "worst": -0.95, "poor": -0.6, "disappointing": -0.7, "disappointed": -0.75,
    # Complaints
    "complaint": -0.7, "complain": -0.65, "unhappy": -0.7, "unsatisfied": -0.7,
    "frustrated": -0.75, "angry": -0.8, "upset": -0.7,
    # Problems
    "problem": -0.5, "issue": -0.45, "trouble": -0.5, "difficulty": -0.4,
    "error": -0.5, "mistake": -0.5, "wrong": -0.5,
    # Service
    "late": -0.5, "delay": -0.5, "delayed": -0.5, "slow": -0.4,
    "waiting": -0.3, "ignored": -0.7, "no response": -0.6,
    # Cancellation
    "cancel": -0.4, "cancelled": -0.5, "refund": -0.5,
    # Price
    "expensive": -0.5, "overpriced": -0.6, "ripoff": -0.8,
    # Scam
    "scam": -0.9, "fraud": -0.9, "fake": -0.8, "cheated": -0.9,
    # Emotions
    "hate": -0.9, "annoying": -0.7, "annoyed": -0.7, "irritating": -0.7,
    # Negation
    "no": -0.2, "not": -0.1, "don't": -0.2, "won't": -0.3, "can't": -0.2,
}

# Арабский язык - позитивные слова
POSITIVE_WORDS_AR = {
    # Благодарность
    "شكرا": 0.8, "شكراً": 0.8, "مشكور": 0.75, "جزاك الله خيرا": 0.9,
    # Удовлетворение
    "ممتاز": 0.9, "رائع": 0.9, "جميل": 0.8, "حلو": 0.7, "تمام": 0.6,
    "مبسوط": 0.8, "زين": 0.6, "طيب": 0.5,
    # Согласие
    "نعم": 0.3, "أيوه": 0.3, "ايوا": 0.3, "اوكي": 0.3, "موافق": 0.5,
    # Радость
    "سعيد": 0.8, "فرحان": 0.8, "مرتاح": 0.7,
}

# Арабский язык - негативные слова
NEGATIVE_WORDS_AR = {
    # Недовольство
    "سيء": -0.7, "سيئ": -0.7, "مو زين": -0.6, "مش كويس": -0.6,
    "زفت": -0.8, "خربان": -0.7,
    # Проблемы
    "مشكلة": -0.5, "مشكله": -0.5, "غلط": -0.5,
    # Отмена
    "الغاء": -0.4, "إلغاء": -0.4, "كنسل": -0.4,
    # Эмоции
    "زعلان": -0.7, "متضايق": -0.7, "غضبان": -0.8,
    # Нет
    "لا": -0.2, "لأ": -0.2,
}

# ═══════════════════════════════════════════════════════════════
# EMOJI SENTIMENT
# ═══════════════════════════════════════════════════════════════

POSITIVE_EMOJI = {
    # Улыбки
    "😊": 0.8, "😃": 0.85, "😄": 0.85, "😁": 0.8, "🙂": 0.5, "😀": 0.8,
    "😆": 0.75, "☺️": 0.7, "☺": 0.7, "🤗": 0.8, "😍": 0.9, "🥰": 0.9,
    "😘": 0.85, "😗": 0.6, "😙": 0.6, "😚": 0.7,
    # Смех
    "😂": 0.7, "🤣": 0.7, "😹": 0.7,
    # Позитивные жесты
    "👍": 0.7, "👍🏻": 0.7, "👍🏼": 0.7, "👍🏽": 0.7, "👍🏾": 0.7, "👍🏿": 0.7,
    "👌": 0.6, "👌🏻": 0.6, "✌️": 0.6, "✌": 0.6, "🤝": 0.7, "👏": 0.75,
    "🙌": 0.8, "💪": 0.7,
    # Сердца
    "❤️": 0.85, "❤": 0.85, "💕": 0.8, "💗": 0.8, "💖": 0.85, "💓": 0.8,
    "💞": 0.8, "💘": 0.8, "🧡": 0.8, "💛": 0.8, "💚": 0.8, "💙": 0.8,
    "💜": 0.8, "🖤": 0.6, "🤍": 0.7, "🤎": 0.7,
    # Звёзды/праздник
    "⭐": 0.7, "🌟": 0.75, "✨": 0.7, "💫": 0.7, "🎉": 0.85, "🎊": 0.85,
    "🥳": 0.9, "🎁": 0.7,
    # Природа/позитив
    "🌈": 0.75, "☀️": 0.7, "🌸": 0.65, "🌺": 0.65, "🌹": 0.7, "💐": 0.7,
    # Еда (позитив)
    "☕": 0.5, "🍰": 0.6,
    # Другое
    "🙏": 0.7, "🙏🏻": 0.7, "😎": 0.6, "🤩": 0.85, "💯": 0.8, "🔥": 0.7,
    "✅": 0.6, "✓": 0.5,
}

NEGATIVE_EMOJI = {
    # Грустные
    "😢": -0.7, "😭": -0.8, "😿": -0.7, "🥺": -0.5, "😞": -0.6, "😔": -0.6,
    "😕": -0.4, "🙁": -0.5, "☹️": -0.6, "☹": -0.6,
    # Злые
    "😠": -0.8, "😡": -0.9, "🤬": -0.95, "😤": -0.7, "💢": -0.7,
    # Страх/шок
    "😱": -0.6, "😨": -0.5, "😰": -0.5, "😥": -0.5,
    # Негативные жесты
    "👎": -0.7, "👎🏻": -0.7, "👎🏼": -0.7, "👎🏽": -0.7, "👎🏾": -0.7, "👎🏿": -0.7,
    # Болезнь/плохо
    "🤢": -0.7, "🤮": -0.8, "😵": -0.6, "💀": -0.5, "☠️": -0.5,
    # Другое
    "❌": -0.5, "❎": -0.5, "⛔": -0.6, "🚫": -0.5,
    "😒": -0.5, "🙄": -0.4, "😑": -0.3, "😐": -0.2,
}

NEUTRAL_EMOJI = {
    "🤔": 0, "😶": 0, "😐": 0, "🤷": 0, "🤷‍♂️": 0, "🤷‍♀️": 0,
    "📷": 0, "📹": 0, "🎤": 0, "📍": 0, "📎": 0, "📄": 0,
    "👀": 0, "👁": 0, "💬": 0, "💭": 0,
}

# ═══════════════════════════════════════════════════════════════
# EMOTION TAGS
# ═══════════════════════════════════════════════════════════════

EMOTION_PATTERNS = {
    "happy": {
        "words_ru": ["рад", "рада", "рады", "счастлив", "счастлива", "доволен", "довольна",
                    "весело", "радость", "ура", "йеху", "вау"],
        "words_en": ["happy", "glad", "joy", "delighted", "cheerful", "yay", "wow", "woohoo"],
        "emoji": ["😊", "😃", "😄", "😁", "🥳", "🎉", "🎊", "😍", "🥰", "🤗"],
    },
    "angry": {
        "words_ru": ["злой", "злая", "злость", "бешусь", "ненавижу", "бесит", "разозлил",
                    "в ярости", "взбешён"],
        "words_en": ["angry", "furious", "mad", "hate", "rage", "outraged", "infuriated"],
        "emoji": ["😠", "😡", "🤬", "😤", "💢"],
    },
    "frustrated": {
        "words_ru": ["раздражает", "раздражён", "достало", "надоело", "устал", "устала",
                    "невозможно", "опять", "снова", "сколько можно"],
        "words_en": ["frustrated", "annoyed", "irritated", "fed up", "tired of", "again"],
        "emoji": ["😒", "🙄", "😤", "😫", "😩"],
    },
    "grateful": {
        "words_ru": ["спасибо", "благодарю", "признателен", "признательна", "благодарность"],
        "words_en": ["thanks", "thank you", "grateful", "appreciate", "thankful"],
        "emoji": ["🙏", "🙏🏻", "❤️", "💕", "🤗"],
    },
    "confused": {
        "words_ru": ["не понимаю", "непонятно", "что", "как", "почему", "зачем", "странно",
                    "запутался", "запуталась", "не ясно"],
        "words_en": ["confused", "don't understand", "unclear", "what", "why", "how", "strange"],
        "emoji": ["🤔", "😕", "❓", "❔", "🤷"],
    },
    "excited": {
        "words_ru": ["не могу дождаться", "жду с нетерпением", "ждём", "предвкушаю",
                    "в восторге", "восхищён", "невероятно", "потрясающе"],
        "words_en": ["excited", "can't wait", "looking forward", "thrilled", "amazing",
                    "incredible", "awesome"],
        "emoji": ["🤩", "😱", "🔥", "💫", "✨", "⭐", "🎉"],
    },
}

# ═══════════════════════════════════════════════════════════════
# ПУНКТУАЦИЯ
# ═══════════════════════════════════════════════════════════════

def analyze_punctuation(text):
    """Анализирует пунктуацию для определения настроения."""
    score_mod = 0.0
    signals = []

    # Много восклицательных знаков - усиление эмоции
    exclamation_count = text.count('!')
    if exclamation_count >= 3:
        score_mod += 0.2  # Может быть и позитивно и негативно
        signals.append(f"exclamation_marks:{exclamation_count}")

    # Много вопросительных знаков - возможная фрустрация
    question_count = text.count('?')
    if question_count >= 3:
        score_mod -= 0.15
        signals.append(f"question_marks:{question_count}")

    # CAPS LOCK - сильная эмоция
    words = text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(caps_words) >= 2:
        score_mod -= 0.2  # Обычно негатив в caps
        signals.append(f"caps_words:{len(caps_words)}")

    # Многоточие может указывать на недосказанность/негатив
    if '...' in text or '…' in text:
        ellipsis_count = text.count('...') + text.count('…')
        if ellipsis_count >= 2:
            score_mod -= 0.1
            signals.append("ellipsis")

    return score_mod, signals


# ═══════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ФУНКЦИИ АНАЛИЗА
# ═══════════════════════════════════════════════════════════════

def load_messages_jsonl(filepath):
    """Загружает сообщения из JSONL файла."""
    messages = []

    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return messages

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError as e:
                    print(f"  Ошибка JSON в строке {line_num}: {e}")
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")

    return messages


def calculate_word_sentiment(text, language="auto"):
    """Вычисляет sentiment на основе словарей."""
    text_lower = text.lower()
    score = 0.0
    matched_words = []

    # Определяем язык если auto
    if language == "auto":
        # Простая эвристика по наличию символов
        if re.search(r'[а-яё]', text_lower):
            language = "ru"
        elif re.search(r'[\u0600-\u06FF]', text_lower):
            language = "ar"
        else:
            language = "en"

    # Выбираем словари
    if language == "ru":
        positive_dict = POSITIVE_WORDS_RU
        negative_dict = NEGATIVE_WORDS_RU
    elif language == "ar":
        positive_dict = POSITIVE_WORDS_AR
        negative_dict = NEGATIVE_WORDS_AR
    else:
        positive_dict = POSITIVE_WORDS_EN
        negative_dict = NEGATIVE_WORDS_EN

    # Также проверяем английские слова в русском тексте
    all_positive = {**positive_dict, **POSITIVE_WORDS_EN}
    all_negative = {**negative_dict, **NEGATIVE_WORDS_EN}

    # Ищем позитивные слова
    for word, word_score in all_positive.items():
        if word in text_lower:
            score += word_score
            matched_words.append((word, word_score))

    # Ищем негативные слова
    for word, word_score in all_negative.items():
        if word in text_lower:
            score += word_score  # word_score уже отрицательный
            matched_words.append((word, word_score))

    return score, matched_words


def calculate_emoji_sentiment(text):
    """Вычисляет sentiment на основе emoji."""
    score = 0.0
    matched_emoji = []

    for emoji, emoji_score in POSITIVE_EMOJI.items():
        count = text.count(emoji)
        if count > 0:
            score += emoji_score * count
            matched_emoji.append((emoji, emoji_score, count))

    for emoji, emoji_score in NEGATIVE_EMOJI.items():
        count = text.count(emoji)
        if count > 0:
            score += emoji_score * count
            matched_emoji.append((emoji, emoji_score, count))

    return score, matched_emoji


def detect_emotions(text):
    """Определяет эмоциональные теги в тексте."""
    text_lower = text.lower()
    emotions = []

    for emotion, patterns in EMOTION_PATTERNS.items():
        found = False

        # Проверяем русские слова
        for word in patterns.get("words_ru", []):
            if word in text_lower:
                found = True
                break

        # Проверяем английские слова
        if not found:
            for word in patterns.get("words_en", []):
                if word in text_lower:
                    found = True
                    break

        # Проверяем emoji
        if not found:
            for emoji in patterns.get("emoji", []):
                if emoji in text:
                    found = True
                    break

        if found:
            emotions.append(emotion)

    return emotions


def analyze_message_sentiment(text):
    """Полный анализ sentiment для одного сообщения."""
    if not text or len(text.strip()) < 2:
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "confidence": 0.0,
            "emotions": [],
            "details": {}
        }

    # Словарный анализ
    word_score, matched_words = calculate_word_sentiment(text)

    # Emoji анализ
    emoji_score, matched_emoji = calculate_emoji_sentiment(text)

    # Пунктуация
    punct_mod, punct_signals = analyze_punctuation(text)

    # Определяем эмоции
    emotions = detect_emotions(text)

    # Общий score (нормализуем)
    raw_score = word_score + emoji_score + punct_mod

    # Нормализуем в диапазон [-1, 1]
    if raw_score > 0:
        normalized_score = min(raw_score / 3.0, 1.0)
    elif raw_score < 0:
        normalized_score = max(raw_score / 3.0, -1.0)
    else:
        normalized_score = 0.0

    # Определяем sentiment category
    if normalized_score > 0.2:
        sentiment = "positive"
    elif normalized_score < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # Confidence на основе количества найденных индикаторов
    indicators_count = len(matched_words) + len(matched_emoji) + len(punct_signals)
    confidence = min(indicators_count * 0.15 + 0.3, 1.0)

    # Если ничего не нашли, низкая уверенность
    if indicators_count == 0:
        confidence = 0.1

    return {
        "sentiment": sentiment,
        "score": round(normalized_score, 3),
        "confidence": round(confidence, 3),
        "emotions": emotions,
        "details": {
            "word_score": round(word_score, 3),
            "emoji_score": round(emoji_score, 3),
            "punct_mod": round(punct_mod, 3),
            "matched_words": matched_words[:5],  # Топ 5
            "matched_emoji": matched_emoji[:5],
            "punct_signals": punct_signals,
        }
    }


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ НА УРОВНЕ ЧАТА
# ═══════════════════════════════════════════════════════════════

def analyze_chat_sentiment(messages, contact_id=None):
    """Анализирует sentiment для всего чата."""
    results = []
    scores = []

    for msg in messages:
        # Фильтруем по контакту если указан
        if contact_id and msg.get("contact_id") != contact_id:
            continue

        text = msg.get("text", "")
        if not text:
            continue

        analysis = analyze_message_sentiment(text)

        result = {
            "message_id": msg.get("message_id", ""),
            "contact_id": msg.get("contact_id", ""),
            "datetime": msg.get("datetime", msg.get("timestamp", "")),
            "sender": msg.get("sender_name", msg.get("sender", "")),
            "text_preview": text[:100],
            **analysis
        }

        results.append(result)
        scores.append(analysis["score"])

    # Общая статистика
    if scores:
        avg_score = sum(scores) / len(scores)
        positive_count = sum(1 for s in scores if s > 0.2)
        negative_count = sum(1 for s in scores if s < -0.2)
        neutral_count = len(scores) - positive_count - negative_count
    else:
        avg_score = 0
        positive_count = negative_count = neutral_count = 0

    return {
        "messages": results,
        "summary": {
            "total_messages": len(results),
            "average_score": round(avg_score, 3),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_ratio": round(positive_count / len(results), 3) if results else 0,
            "negative_ratio": round(negative_count / len(results), 3) if results else 0,
        }
    }


def find_sentiment_drops(messages_analysis, threshold=-0.3, window=3):
    """Находит точки падения настроения (потенциальные проблемы)."""
    drops = []
    messages = messages_analysis.get("messages", [])

    if len(messages) < window:
        return drops

    for i in range(window, len(messages)):
        # Среднее за предыдущие сообщения
        prev_scores = [messages[j]["score"] for j in range(i - window, i)]
        prev_avg = sum(prev_scores) / len(prev_scores)

        current_score = messages[i]["score"]

        # Резкое падение
        if current_score - prev_avg < threshold:
            drops.append({
                "index": i,
                "datetime": messages[i]["datetime"],
                "message": messages[i]["text_preview"],
                "previous_avg": round(prev_avg, 3),
                "current_score": current_score,
                "drop": round(current_score - prev_avg, 3),
                "emotions": messages[i].get("emotions", []),
            })

    return drops


# ═══════════════════════════════════════════════════════════════
# ГРУППИРОВКА И ТРЕНДЫ
# ═══════════════════════════════════════════════════════════════

def group_by_contact(messages):
    """Группирует сообщения по контактам."""
    by_contact = defaultdict(list)

    for msg in messages:
        contact_id = msg.get("contact_id", msg.get("jid", "unknown"))
        by_contact[contact_id].append(msg)

    return dict(by_contact)


def calculate_trends(messages_analysis, period="day"):
    """Вычисляет тренды sentiment по периодам."""
    trends = defaultdict(lambda: {"scores": [], "count": 0, "positive": 0, "negative": 0})

    for msg in messages_analysis.get("messages", []):
        dt_str = msg.get("datetime", "")
        if not dt_str:
            continue

        # Парсим дату
        dt = None
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(dt_str[:19], fmt)
                break
            except:
                continue

        if not dt:
            continue

        # Определяем ключ периода
        if period == "day":
            key = dt.strftime("%Y-%m-%d")
        elif period == "week":
            # ISO неделя
            key = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
        elif period == "month":
            key = dt.strftime("%Y-%m")
        elif period == "weekday":
            key = dt.strftime("%A")  # День недели
        elif period == "hour":
            key = dt.strftime("%H")  # Час
        else:
            key = dt.strftime("%Y-%m-%d")

        score = msg.get("score", 0)
        trends[key]["scores"].append(score)
        trends[key]["count"] += 1

        if score > 0.2:
            trends[key]["positive"] += 1
        elif score < -0.2:
            trends[key]["negative"] += 1

    # Вычисляем средние
    result = {}
    for key, data in sorted(trends.items()):
        avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        result[key] = {
            "average_score": round(avg_score, 3),
            "message_count": data["count"],
            "positive_count": data["positive"],
            "negative_count": data["negative"],
            "sentiment": "positive" if avg_score > 0.2 else ("negative" if avg_score < -0.2 else "neutral"),
        }

    return result


def detect_alerts(sentiment_by_contact, threshold_score=-0.3, min_messages=5):
    """Определяет контакты с негативным трендом для алертов."""
    alerts = []

    for contact_id, data in sentiment_by_contact.items():
        summary = data.get("summary", {})

        # Проверяем критерии
        total = summary.get("total_messages", 0)
        avg_score = summary.get("average_score", 0)
        negative_ratio = summary.get("negative_ratio", 0)

        if total < min_messages:
            continue

        alert = None

        # Критический негатив
        if avg_score < threshold_score:
            alert = {
                "contact_id": contact_id,
                "severity": "high" if avg_score < -0.5 else "medium",
                "reason": "negative_average",
                "average_score": avg_score,
                "negative_ratio": negative_ratio,
                "total_messages": total,
                "recommendation": "Требуется внимание менеджера",
            }
        # Много негативных сообщений
        elif negative_ratio > 0.4:
            alert = {
                "contact_id": contact_id,
                "severity": "medium",
                "reason": "high_negative_ratio",
                "average_score": avg_score,
                "negative_ratio": negative_ratio,
                "total_messages": total,
                "recommendation": "Проверить историю переписки",
            }

        # Проверяем drops
        drops = data.get("drops", [])
        if drops and len(drops) >= 2:
            if alert:
                alert["drops_count"] = len(drops)
            else:
                alert = {
                    "contact_id": contact_id,
                    "severity": "low",
                    "reason": "multiple_sentiment_drops",
                    "drops_count": len(drops),
                    "average_score": avg_score,
                    "total_messages": total,
                    "recommendation": "Возможные точки конфликта в переписке",
                }

        if alert:
            alerts.append(alert)

    # Сортируем по severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda x: (severity_order.get(x["severity"], 3), x.get("average_score", 0)))

    return alerts


# ═══════════════════════════════════════════════════════════════
# ВИЗУАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

def generate_ascii_chart(trends_by_day, width=60):
    """Генерирует ASCII график sentiment по дням."""
    if not trends_by_day:
        return "Нет данных для графика"

    lines = []
    lines.append("Sentiment по дням")
    lines.append("=" * width)
    lines.append("")
    lines.append("      -1.0    -0.5     0.0    +0.5    +1.0")
    lines.append("        |       |       |       |       |")

    # Берём последние 14 дней
    days = list(trends_by_day.items())[-14:]

    for date, data in days:
        score = data.get("average_score", 0)
        sentiment = data.get("sentiment", "neutral")

        # Позиция на шкале (0-40 символов для диапазона -1 до +1)
        pos = int((score + 1) * 20)  # 0-40
        pos = max(0, min(40, pos))

        # Символ в зависимости от sentiment
        if sentiment == "positive":
            char = "+"
        elif sentiment == "negative":
            char = "-"
        else:
            char = "o"

        # Строим строку
        bar = [" "] * 41
        bar[20] = "|"  # Центр (0)
        bar[pos] = char

        date_short = date[-5:] if len(date) >= 5 else date  # MM-DD
        count = data.get("message_count", 0)

        lines.append(f"{date_short:>5} {''.join(bar)} ({count:>3})")

    lines.append("")
    lines.append("Легенда: + позитив, o нейтрал, - негатив")
    lines.append("В скобках - количество сообщений")

    return "\n".join(lines)


def generate_weekday_heatmap(trends_by_weekday):
    """Генерирует heatmap по дням недели (ASCII)."""
    if not trends_by_weekday:
        return "Нет данных для heatmap"

    # Порядок дней
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_names_ru = {
        "Monday": "Пн", "Tuesday": "Вт", "Wednesday": "Ср",
        "Thursday": "Чт", "Friday": "Пт", "Saturday": "Сб", "Sunday": "Вс"
    }

    lines = []
    lines.append("Sentiment по дням недели")
    lines.append("=" * 50)
    lines.append("")
    lines.append("День    Score    Сообщ.  Визуализация")
    lines.append("-" * 50)

    for weekday in weekday_order:
        data = trends_by_weekday.get(weekday, {})
        score = data.get("average_score", 0)
        count = data.get("message_count", 0)

        # Визуализация score
        if score > 0.5:
            viz = "[+++++]"
        elif score > 0.2:
            viz = "[+++ ]"
        elif score > -0.2:
            viz = "[ === ]"
        elif score > -0.5:
            viz = "[ ---]"
        else:
            viz = "[-----]"

        day_ru = weekday_names_ru.get(weekday, weekday[:2])
        lines.append(f"{day_ru:>4}    {score:>+.2f}    {count:>5}   {viz}")

    lines.append("-" * 50)

    return "\n".join(lines)


def generate_hour_heatmap(trends_by_hour):
    """Генерирует heatmap по часам (ASCII)."""
    if not trends_by_hour:
        return "Нет данных для heatmap"

    lines = []
    lines.append("Sentiment по часам")
    lines.append("=" * 60)
    lines.append("")

    for hour in range(24):
        hour_str = f"{hour:02d}"
        data = trends_by_hour.get(hour_str, {})
        score = data.get("average_score", 0)
        count = data.get("message_count", 0)

        if count == 0:
            bar = "."
        else:
            # Визуализация score блоками
            if score > 0.3:
                bar = "#" * min(count // 5 + 1, 20)  # Позитив
            elif score < -0.3:
                bar = "-" * min(count // 5 + 1, 20)  # Негатив
            else:
                bar = "=" * min(count // 5 + 1, 20)  # Нейтрал

        lines.append(f"{hour_str}:00  {bar:<20} ({count:>3}) score:{score:>+.2f}")

    lines.append("")
    lines.append("Легенда: # позитив, = нейтрал, - негатив")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════════════════════════════

def save_json(data, filepath):
    """Сохраняет данные в JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Сохранено: {filepath}")


def save_markdown_report(analysis_results, output_path):
    """Сохраняет отчёт в Markdown."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    lines = []
    lines.append("# Анализ настроения клиентов")
    lines.append("")
    lines.append(f"*Дата анализа: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Общая статистика
    summary = analysis_results.get("overall_summary", {})
    lines.append("## Общая статистика")
    lines.append("")
    lines.append(f"- **Всего проанализировано сообщений:** {summary.get('total_messages', 0)}")
    lines.append(f"- **Уникальных контактов:** {summary.get('unique_contacts', 0)}")
    lines.append(f"- **Средний sentiment score:** {summary.get('average_score', 0):+.3f}")
    lines.append("")
    lines.append("### Распределение:")
    lines.append(f"- Позитивные: {summary.get('positive_count', 0)} ({summary.get('positive_ratio', 0)*100:.1f}%)")
    lines.append(f"- Нейтральные: {summary.get('neutral_count', 0)} ({summary.get('neutral_ratio', 0)*100:.1f}%)")
    lines.append(f"- Негативные: {summary.get('negative_count', 0)} ({summary.get('negative_ratio', 0)*100:.1f}%)")
    lines.append("")

    # Алерты
    alerts = analysis_results.get("alerts", [])
    if alerts:
        lines.append("---")
        lines.append("")
        lines.append("## ВНИМАНИЕ: Контакты требующие внимания")
        lines.append("")

        severity_emoji = {"high": "!!!!HIGH", "medium": "!!MEDIUM", "low": "!LOW"}

        for alert in alerts[:10]:  # Топ 10
            sev = severity_emoji.get(alert["severity"], "")
            lines.append(f"### [{sev}] {alert['contact_id']}")
            lines.append("")
            lines.append(f"- **Причина:** {alert.get('reason', '')}")
            lines.append(f"- **Средний score:** {alert.get('average_score', 0):+.3f}")
            lines.append(f"- **Доля негатива:** {alert.get('negative_ratio', 0)*100:.1f}%")
            lines.append(f"- **Сообщений:** {alert.get('total_messages', 0)}")
            lines.append(f"- **Рекомендация:** {alert.get('recommendation', '')}")
            lines.append("")

    # Графики
    lines.append("---")
    lines.append("")
    lines.append("## Визуализация")
    lines.append("")

    # График по дням
    trends_by_day = analysis_results.get("trends_by_day", {})
    if trends_by_day:
        lines.append("### Динамика по дням")
        lines.append("")
        lines.append("```")
        lines.append(generate_ascii_chart(trends_by_day))
        lines.append("```")
        lines.append("")

    # Heatmap по дням недели
    trends_by_weekday = analysis_results.get("trends_by_weekday", {})
    if trends_by_weekday:
        lines.append("### По дням недели")
        lines.append("")
        lines.append("```")
        lines.append(generate_weekday_heatmap(trends_by_weekday))
        lines.append("```")
        lines.append("")

    # Топ эмоций
    top_emotions = analysis_results.get("top_emotions", {})
    if top_emotions:
        lines.append("---")
        lines.append("")
        lines.append("## Частые эмоции")
        lines.append("")
        emotion_names_ru = {
            "happy": "Радость", "angry": "Злость", "frustrated": "Фрустрация",
            "grateful": "Благодарность", "confused": "Замешательство", "excited": "Возбуждение"
        }
        for emotion, count in sorted(top_emotions.items(), key=lambda x: x[1], reverse=True):
            name = emotion_names_ru.get(emotion, emotion)
            lines.append(f"- **{name}:** {count}")
        lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Markdown отчёт сохранён: {output_path}")


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def run_sentiment_analysis(input_file, output_dir):
    """Главная функция анализа."""

    print(f"Загрузка сообщений из: {input_file}")
    messages = load_messages_jsonl(input_file)

    if not messages:
        print("Сообщения не найдены!")
        return None

    print(f"Загружено {len(messages)} сообщений")

    # Группируем по контактам
    print("Группировка по контактам...")
    messages_by_contact = group_by_contact(messages)
    print(f"Уникальных контактов: {len(messages_by_contact)}")

    # Анализируем каждый контакт
    print("Анализ sentiment по контактам...")
    sentiment_by_contact = {}
    all_emotions = []
    all_scores = []
    all_messages_analyzed = []

    for contact_id, contact_messages in messages_by_contact.items():
        analysis = analyze_chat_sentiment(contact_messages)
        drops = find_sentiment_drops(analysis)

        sentiment_by_contact[contact_id] = {
            **analysis,
            "drops": drops,
            "contact_id": contact_id,
        }

        # Собираем все эмоции
        for msg in analysis.get("messages", []):
            all_emotions.extend(msg.get("emotions", []))
            all_scores.append(msg.get("score", 0))
            all_messages_analyzed.append(msg)

    # Общая статистика
    total_messages = len(all_scores)
    positive_count = sum(1 for s in all_scores if s > 0.2)
    negative_count = sum(1 for s in all_scores if s < -0.2)
    neutral_count = total_messages - positive_count - negative_count

    overall_summary = {
        "total_messages": total_messages,
        "unique_contacts": len(messages_by_contact),
        "average_score": round(sum(all_scores) / total_messages, 3) if all_scores else 0,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "positive_ratio": round(positive_count / total_messages, 3) if total_messages else 0,
        "negative_ratio": round(negative_count / total_messages, 3) if total_messages else 0,
        "neutral_ratio": round(neutral_count / total_messages, 3) if total_messages else 0,
    }

    # Тренды
    print("Вычисление трендов...")
    dummy_analysis = {"messages": all_messages_analyzed}
    trends_by_day = calculate_trends(dummy_analysis, "day")
    trends_by_week = calculate_trends(dummy_analysis, "week")
    trends_by_weekday = calculate_trends(dummy_analysis, "weekday")
    trends_by_hour = calculate_trends(dummy_analysis, "hour")

    # Алерты
    print("Определение алертов...")
    alerts = detect_alerts(sentiment_by_contact)

    # Топ эмоций
    top_emotions = dict(Counter(all_emotions).most_common(10))

    # Собираем результаты
    results = {
        "overall_summary": overall_summary,
        "trends_by_day": trends_by_day,
        "trends_by_week": trends_by_week,
        "trends_by_weekday": trends_by_weekday,
        "trends_by_hour": trends_by_hour,
        "alerts": alerts,
        "top_emotions": top_emotions,
        "metadata": {
            "source_file": input_file,
            "analyzed_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    }

    # Сохраняем результаты
    os.makedirs(output_dir, exist_ok=True)

    # 1. sentiment_by_contact.json
    save_json(
        {"contacts": sentiment_by_contact, "metadata": results["metadata"]},
        os.path.join(output_dir, "sentiment_by_contact.json")
    )

    # 2. sentiment_trends.json
    save_json(
        {
            "by_day": trends_by_day,
            "by_week": trends_by_week,
            "by_weekday": trends_by_weekday,
            "by_hour": trends_by_hour,
            "metadata": results["metadata"],
        },
        os.path.join(output_dir, "sentiment_trends.json")
    )

    # 3. alerts.json
    save_json(
        {"alerts": alerts, "metadata": results["metadata"]},
        os.path.join(output_dir, "alerts.json")
    )

    # 4. Markdown отчёт
    save_markdown_report(
        results,
        os.path.join(output_dir, "sentiment_report.md")
    )

    # Выводим сводку
    print("")
    print("=" * 60)
    print("АНАЛИЗ НАСТРОЕНИЯ ЗАВЕРШЁН")
    print("=" * 60)
    print(f"Всего сообщений: {total_messages}")
    print(f"Контактов: {len(messages_by_contact)}")
    print(f"Средний sentiment: {overall_summary['average_score']:+.3f}")
    print(f"Позитивных: {positive_count} ({overall_summary['positive_ratio']*100:.1f}%)")
    print(f"Нейтральных: {neutral_count} ({overall_summary['neutral_ratio']*100:.1f}%)")
    print(f"Негативных: {negative_count} ({overall_summary['negative_ratio']*100:.1f}%)")
    print(f"Алертов: {len(alerts)}")
    print("=" * 60)

    # Показываем график
    if trends_by_day:
        print("")
        print(generate_ascii_chart(trends_by_day))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Анализ настроения клиентов в WhatsApp переписке"
    )
    parser.add_argument(
        "--input", "-i",
        default="D:/Downloads/Chats/_база/raw/all_messages.jsonl",
        help="Входной JSONL файл с сообщениями"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="D:/Downloads/Chats/_база/sentiment",
        help="Директория для результатов"
    )
    parser.add_argument(
        "--contact", "-c",
        help="Анализировать только конкретный контакт"
    )

    args = parser.parse_args()

    run_sentiment_analysis(
        input_file=args.input,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
