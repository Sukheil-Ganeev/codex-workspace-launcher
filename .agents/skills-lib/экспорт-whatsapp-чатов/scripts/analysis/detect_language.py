#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детекция языка сообщений в WhatsApp переписке.

Функции:
1. Определение языка каждого сообщения (RU, EN, AR, DE, FR, IT, ES, ZH, HI)
2. Профиль языков контакта (% каждого языка)
3. Обнаружение смешанных сообщений (code-switching)
4. Автоматический выбор языка для ответа
5. Статистика по языкам в базе
6. Определение транслитерации
7. Экспорт JSON с языковыми метками

Использует: langdetect, lingua-py

ВАЖНЫЙ ПРИНЦИП: Никакие данные НЕ теряются! Сохранять ВСЕ данные полностью.
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# ИМПОРТ БИБЛИОТЕК ДЕТЕКЦИИ
# ═══════════════════════════════════════════════════════════════

# langdetect - быстрый, но менее точный для коротких текстов
try:
    from langdetect import detect, detect_langs, LangDetectException
    from langdetect import DetectorFactory
    DetectorFactory.seed = 0  # Для воспроизводимости
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("[!] langdetect не установлен. Установите: pip install langdetect")

# lingua-py - высокая точность для коротких текстов
try:
    from lingua import Language, LanguageDetectorBuilder
    LINGUA_AVAILABLE = True
except ImportError:
    LINGUA_AVAILABLE = False
    print("[!] lingua-py не установлен. Установите: pip install lingua-language-detector")


# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Импорт путей из конфига
try:
    from config import (
        RAW_DIR,
        JSON_DIR,
        ANALYTICS_DIR,
        ensure_directories,
    )
except ImportError:
    # Fallback пути
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    ANALYTICS_DIR = Path("D:/Downloads/Chats/_аналитика")
    def ensure_directories():
        for d in [RAW_DIR, JSON_DIR, ANALYTICS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

# Выходные файлы
LANGUAGE_DIR = JSON_DIR / "language"
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
LANGUAGE_STATS_FILE = LANGUAGE_DIR / "language_statistics.json"
CONTACT_PROFILES_FILE = LANGUAGE_DIR / "contact_language_profiles.json"
MESSAGES_WITH_LANG_FILE = LANGUAGE_DIR / "messages_with_language.jsonl"


# ═══════════════════════════════════════════════════════════════
# ПОДДЕРЖИВАЕМЫЕ ЯЗЫКИ
# ═══════════════════════════════════════════════════════════════

SUPPORTED_LANGUAGES = {
    "ru": {"name": "Russian", "name_ru": "Русский", "script": "cyrillic"},
    "en": {"name": "English", "name_ru": "Английский", "script": "latin"},
    "ar": {"name": "Arabic", "name_ru": "Арабский", "script": "arabic"},
    "de": {"name": "German", "name_ru": "Немецкий", "script": "latin"},
    "fr": {"name": "French", "name_ru": "Французский", "script": "latin"},
    "it": {"name": "Italian", "name_ru": "Итальянский", "script": "latin"},
    "es": {"name": "Spanish", "name_ru": "Испанский", "script": "latin"},
    "zh": {"name": "Chinese", "name_ru": "Китайский", "script": "chinese"},
    "hi": {"name": "Hindi", "name_ru": "Хинди", "script": "devanagari"},
}

# Маппинг lingua Language enum
if LINGUA_AVAILABLE:
    LINGUA_LANGUAGES = [
        Language.RUSSIAN,
        Language.ENGLISH,
        Language.ARABIC,
        Language.GERMAN,
        Language.FRENCH,
        Language.ITALIAN,
        Language.SPANISH,
        Language.CHINESE,
        Language.HINDI,
    ]

    LINGUA_TO_CODE = {
        Language.RUSSIAN: "ru",
        Language.ENGLISH: "en",
        Language.ARABIC: "ar",
        Language.GERMAN: "de",
        Language.FRENCH: "fr",
        Language.ITALIAN: "it",
        Language.SPANISH: "es",
        Language.CHINESE: "zh",
        Language.HINDI: "hi",
    }


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ТРАНСЛИТЕРАЦИИ
# ═══════════════════════════════════════════════════════════════

# Русская транслитерация латиницей
TRANSLIT_RU_PATTERNS = [
    # Типичные сочетания
    r"\b(privet|spasibo|poka|da|net|horosho|normalno)\b",
    r"\b(zdorovo|kak dela|vsyo|ok|ladno|potom|segodnya)\b",
    r"\b(zavtra|vchera|seychas|skoro|uzhe|davay|poshli)\b",
    r"\b(skolko|kogda|gde|kto|chto|pochemu|kuda)\b",
    # Туристические термины
    r"\b(ekskursiya|transfer|safari|otel|bilet|tur)\b",
    r"\b(dirham|rubl|dollar|kurs|obmen)\b",
    # Характерные окончания
    r"\w+(shiy|chiy|niy|skiy|cky)\b",  # -ший, -чий, -ний, -ский
    r"\w+(atsiya|enie|anie|ost)\b",     # -ация, -ение, -ание, -ость
    # Характерные сочетания букв
    r"\b\w*(zh|kh|ch|sh|sch|ts|ya|yu|yo)\w*\b",
]

# Арабская транслитерация латиницей
TRANSLIT_AR_PATTERNS = [
    r"\b(shukran|marhaba|habibi|yalla|inshallah|mashallah)\b",
    r"\b(sabah|masa|ahlan|mabrook|khalas)\b",
    r"\b(bukra|hala|akhi|ukht|wallah)\b",
]

# Хинди транслитерация латиницей
TRANSLIT_HI_PATTERNS = [
    r"\b(namaste|dhanyavad|theek|accha|bahut|kya)\b",
    r"\b(aap|hum|yeh|woh|kaise|kyun)\b",
]


# ═══════════════════════════════════════════════════════════════
# РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ ДЛЯ СКРИПТОВ
# ═══════════════════════════════════════════════════════════════

# Unicode диапазоны для определения скрипта
SCRIPT_PATTERNS = {
    "cyrillic": re.compile(r'[\u0400-\u04FF\u0500-\u052F]'),  # Кириллица
    "latin": re.compile(r'[A-Za-z\u00C0-\u024F]'),            # Латиница (включая диакритику)
    "arabic": re.compile(r'[\u0600-\u06FF\u0750-\u077F]'),    # Арабский
    "chinese": re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]'),   # Китайский (CJK)
    "devanagari": re.compile(r'[\u0900-\u097F]'),             # Деванагари (Хинди)
    "emoji": re.compile(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]'),
}

# Служебные сообщения WhatsApp
SYSTEM_MESSAGE_PATTERNS = [
    r'^<Media omitted>$',
    r'^\(медиа не сохранено\)',
    r'^\[ЛОКАЦИЯ\]',
    r'^\[КОНТАКТ\]',
    r'^\[.+?\] media/',
    r'^This message was deleted',
    r'^Сообщение удалено',
    r'^https?://',  # Просто ссылка
]
SYSTEM_MESSAGE_RE = re.compile('|'.join(SYSTEM_MESSAGE_PATTERNS), re.IGNORECASE)


# ═══════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ ДЕТЕКТОРОВ
# ═══════════════════════════════════════════════════════════════

# Глобальный детектор lingua (ленивая инициализация)
_lingua_detector = None

def get_lingua_detector():
    """Получить или создать lingua детектор (singleton)."""
    global _lingua_detector
    if _lingua_detector is None and LINGUA_AVAILABLE:
        print("Инициализация lingua детектора...")
        _lingua_detector = LanguageDetectorBuilder.from_languages(*LINGUA_LANGUAGES).build()
        print("Lingua детектор готов.")
    return _lingua_detector


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ СКРИПТА
# ═══════════════════════════════════════════════════════════════

def detect_script(text: str) -> Dict[str, int]:
    """
    Определить количество символов каждого скрипта в тексте.

    Returns:
        Dict с количеством символов каждого скрипта
    """
    counts = {script: 0 for script in SCRIPT_PATTERNS}

    for script, pattern in SCRIPT_PATTERNS.items():
        counts[script] = len(pattern.findall(text))

    return counts


def get_dominant_script(text: str) -> Tuple[str, float]:
    """
    Определить доминирующий скрипт в тексте.

    Returns:
        Tuple (script_name, ratio)
    """
    counts = detect_script(text)

    # Исключаем emoji из подсчёта
    total = sum(v for k, v in counts.items() if k != "emoji")

    if total == 0:
        return "unknown", 0.0

    # Находим скрипт с максимальным количеством символов
    dominant_script = max(
        [(k, v) for k, v in counts.items() if k != "emoji"],
        key=lambda x: x[1]
    )
    return dominant_script[0], dominant_script[1] / total


def is_mixed_script(text: str, threshold: float = 0.2) -> bool:
    """
    Проверить, содержит ли текст смешанные скрипты (code-switching).

    Args:
        text: Текст для анализа
        threshold: Минимальная доля второго скрипта для признания смешанным

    Returns:
        True если текст содержит значимое смешение скриптов
    """
    counts = detect_script(text)
    total = sum(v for k, v in counts.items() if k != "emoji")

    if total < 5:  # Слишком короткий текст
        return False

    # Сортируем по убыванию
    sorted_counts = sorted(
        [(k, v) for k, v in counts.items() if k != "emoji"],
        key=lambda x: x[1],
        reverse=True
    )

    if len(sorted_counts) < 2:
        return False

    # Проверяем, есть ли второй значимый скрипт
    second_ratio = sorted_counts[1][1] / total if total > 0 else 0

    return second_ratio >= threshold


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ ТРАНСЛИТЕРАЦИИ
# ═══════════════════════════════════════════════════════════════

def detect_transliteration(text: str) -> Optional[Dict[str, Any]]:
    """
    Определить, является ли текст транслитерацией.

    Returns:
        Dict с информацией о транслитерации или None
    """
    text_lower = text.lower()

    # Проверяем арабскую транслитерацию ПЕРВОЙ (более специфичные паттерны)
    ar_matches = []
    for pattern in TRANSLIT_AR_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        ar_matches.extend(matches)

    if len(ar_matches) >= 1:
        return {
            "type": "ar_translit",
            "original_language": "ar",
            "matches": ar_matches[:5],
            "confidence": min(len(ar_matches) * 0.25 + 0.4, 0.95),
        }

    # Проверяем хинди транслитерацию
    hi_matches = []
    for pattern in TRANSLIT_HI_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        hi_matches.extend(matches)

    if len(hi_matches) >= 1:
        return {
            "type": "hi_translit",
            "original_language": "hi",
            "matches": hi_matches[:5],
            "confidence": min(len(hi_matches) * 0.25 + 0.4, 0.95),
        }

    # Проверяем русскую транслитерацию ПОСЛЕДНЕЙ (менее специфичные паттерны)
    ru_matches = []
    for pattern in TRANSLIT_RU_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        ru_matches.extend(matches)

    if len(ru_matches) >= 2 or (len(ru_matches) == 1 and len(text.split()) <= 3):
        return {
            "type": "ru_translit",
            "original_language": "ru",
            "matches": ru_matches[:5],
            "confidence": min(len(ru_matches) * 0.2 + 0.3, 0.95),
        }

    return None


# ═══════════════════════════════════════════════════════════════
# ОСНОВНАЯ ФУНКЦИЯ ДЕТЕКЦИИ ЯЗЫКА
# ═══════════════════════════════════════════════════════════════

def detect_language(text: str, use_lingua: bool = True) -> Dict[str, Any]:
    """
    Определить язык текста с использованием нескольких методов.

    Args:
        text: Текст для анализа
        use_lingua: Использовать lingua-py (более точный, но медленнее)

    Returns:
        Dict с результатами детекции:
        - language: код языка (ru, en, ar, etc.)
        - confidence: уверенность (0.0-1.0)
        - method: метод детекции
        - alternatives: альтернативные языки
        - is_transliteration: информация о транслитерации
        - is_mixed: смешанный текст (code-switching)
        - scripts: обнаруженные скрипты
    """
    result = {
        "language": "unknown",
        "confidence": 0.0,
        "method": "none",
        "alternatives": [],
        "is_transliteration": None,
        "is_mixed": False,
        "scripts": {},
    }

    # Очистка текста
    text = text.strip()

    # Пропускаем слишком короткие или служебные сообщения
    if len(text) < 2:
        result["method"] = "too_short"
        return result

    if SYSTEM_MESSAGE_RE.match(text):
        result["method"] = "system_message"
        return result

    # Определяем скрипты
    scripts = detect_script(text)
    result["scripts"] = {k: v for k, v in scripts.items() if v > 0}

    # Проверяем смешение скриптов
    result["is_mixed"] = is_mixed_script(text)

    # Проверяем транслитерацию
    translit = detect_transliteration(text)
    if translit:
        result["is_transliteration"] = translit
        # Если транслитерация уверенная, используем её как основной язык
        if translit["confidence"] > 0.7:
            result["language"] = translit["original_language"]
            result["confidence"] = translit["confidence"]
            result["method"] = "transliteration"
            return result

    # Быстрая эвристика по скрипту
    dominant_script, script_ratio = get_dominant_script(text)

    # Если текст почти полностью на одном не-латинском скрипте
    if script_ratio > 0.8:
        if dominant_script == "cyrillic":
            result["language"] = "ru"
            result["confidence"] = 0.9
            result["method"] = "script_cyrillic"
            return result
        elif dominant_script == "arabic":
            result["language"] = "ar"
            result["confidence"] = 0.9
            result["method"] = "script_arabic"
            return result
        elif dominant_script == "chinese":
            result["language"] = "zh"
            result["confidence"] = 0.9
            result["method"] = "script_chinese"
            return result
        elif dominant_script == "devanagari":
            result["language"] = "hi"
            result["confidence"] = 0.9
            result["method"] = "script_devanagari"
            return result

    # Используем lingua для латинских текстов (более точный)
    if use_lingua and LINGUA_AVAILABLE and dominant_script == "latin":
        detector = get_lingua_detector()
        if detector:
            try:
                # Получаем все вероятности
                confidence_values = detector.compute_language_confidence_values(text)

                if confidence_values:
                    # Берём топ результаты
                    top_results = []
                    for lang, conf in confidence_values[:5]:
                        code = LINGUA_TO_CODE.get(lang)
                        if code:
                            top_results.append({"language": code, "confidence": round(conf, 3)})

                    if top_results:
                        result["language"] = top_results[0]["language"]
                        result["confidence"] = top_results[0]["confidence"]
                        result["method"] = "lingua"
                        result["alternatives"] = top_results[1:4]
                        return result
            except Exception as e:
                pass  # Fallback к langdetect

    # Fallback на langdetect
    if LANGDETECT_AVAILABLE:
        try:
            # Получаем вероятности
            lang_probs = detect_langs(text)

            if lang_probs:
                # Фильтруем только поддерживаемые языки
                supported_results = []
                for lp in lang_probs:
                    if lp.lang in SUPPORTED_LANGUAGES:
                        supported_results.append({
                            "language": lp.lang,
                            "confidence": round(lp.prob, 3)
                        })

                if supported_results:
                    result["language"] = supported_results[0]["language"]
                    result["confidence"] = supported_results[0]["confidence"]
                    result["method"] = "langdetect"
                    result["alternatives"] = supported_results[1:4]
                    return result

                # Если язык не поддерживается, берём как есть
                result["language"] = lang_probs[0].lang
                result["confidence"] = round(lang_probs[0].prob, 3)
                result["method"] = "langdetect_unsupported"
                return result

        except LangDetectException:
            pass

    # Если ничего не сработало, пробуем по скрипту
    if dominant_script == "latin" and script_ratio > 0.5:
        result["language"] = "en"  # Default для латиницы
        result["confidence"] = 0.3
        result["method"] = "default_latin"

    return result


def detect_message_language(message: Dict) -> Dict[str, Any]:
    """
    Определить язык сообщения (обёртка для структуры сообщения).

    Args:
        message: Словарь сообщения с полем 'text'

    Returns:
        Исходное сообщение с добавленной информацией о языке
    """
    text = message.get("text", "")

    # Также проверяем транскрипт голосового
    voice_text = message.get("voice_transcript", "")

    # Используем основной текст или транскрипт
    analysis_text = text if text else voice_text

    if not analysis_text:
        message["language_detection"] = {
            "language": "unknown",
            "confidence": 0.0,
            "method": "no_text",
        }
        return message

    # Детектируем язык
    detection = detect_language(analysis_text)
    message["language_detection"] = detection

    return message


# ═══════════════════════════════════════════════════════════════
# ПРОФИЛЬ ЯЗЫКОВ КОНТАКТА
# ═══════════════════════════════════════════════════════════════

def build_contact_language_profile(messages: List[Dict], contact_id: str = None) -> Dict[str, Any]:
    """
    Построить профиль языков для контакта.

    Args:
        messages: Список сообщений
        contact_id: ID контакта (опционально для фильтрации)

    Returns:
        Dict с профилем языков:
        - primary_language: основной язык
        - language_distribution: распределение языков (%)
        - total_messages: всего сообщений
        - multilingual: многоязычный контакт
        - code_switching_rate: частота переключения языков
    """
    # Фильтруем по контакту если указан
    if contact_id:
        messages = [m for m in messages if m.get("contact_id") == contact_id]

    if not messages:
        return {
            "contact_id": contact_id,
            "primary_language": "unknown",
            "language_distribution": {},
            "total_messages": 0,
            "analyzed_messages": 0,
            "multilingual": False,
            "code_switching_rate": 0.0,
        }

    # Подсчитываем языки
    language_counts = Counter()
    mixed_count = 0
    translit_count = 0
    analyzed_count = 0

    for msg in messages:
        detection = msg.get("language_detection", {})
        lang = detection.get("language", "unknown")

        if lang != "unknown" and detection.get("method") not in ["too_short", "system_message", "no_text"]:
            language_counts[lang] += 1
            analyzed_count += 1

            if detection.get("is_mixed"):
                mixed_count += 1

            if detection.get("is_transliteration"):
                translit_count += 1

    total = sum(language_counts.values())

    # Вычисляем распределение
    distribution = {}
    for lang, count in language_counts.most_common():
        distribution[lang] = {
            "count": count,
            "percentage": round(count / total * 100, 1) if total > 0 else 0,
            "language_name": SUPPORTED_LANGUAGES.get(lang, {}).get("name_ru", lang),
        }

    # Определяем основной язык
    primary_language = language_counts.most_common(1)[0][0] if language_counts else "unknown"

    # Многоязычность (более 20% на втором языке)
    multilingual = False
    if len(language_counts) >= 2:
        top_two = language_counts.most_common(2)
        if top_two[1][1] / total > 0.2:
            multilingual = True

    # Частота code-switching
    code_switching_rate = mixed_count / analyzed_count if analyzed_count > 0 else 0

    return {
        "contact_id": contact_id,
        "primary_language": primary_language,
        "primary_language_name": SUPPORTED_LANGUAGES.get(primary_language, {}).get("name_ru", primary_language),
        "language_distribution": distribution,
        "total_messages": len(messages),
        "analyzed_messages": analyzed_count,
        "multilingual": multilingual,
        "languages_used": len(language_counts),
        "code_switching_rate": round(code_switching_rate, 3),
        "transliteration_rate": round(translit_count / analyzed_count, 3) if analyzed_count > 0 else 0,
        "mixed_messages_count": mixed_count,
        "transliteration_count": translit_count,
    }


# ═══════════════════════════════════════════════════════════════
# АВТОВЫБОР ЯЗЫКА ДЛЯ ОТВЕТА
# ═══════════════════════════════════════════════════════════════

def suggest_response_language(
    contact_profile: Dict,
    last_messages: List[Dict] = None,
    default_language: str = "ru"
) -> Dict[str, Any]:
    """
    Предложить язык для ответа клиенту.

    Args:
        contact_profile: Профиль языков контакта
        last_messages: Последние N сообщений (для контекста)
        default_language: Язык по умолчанию

    Returns:
        Dict с рекомендацией:
        - suggested_language: рекомендуемый язык
        - reason: причина выбора
        - confidence: уверенность
        - alternatives: альтернативные языки
    """
    result = {
        "suggested_language": default_language,
        "reason": "default",
        "confidence": 0.5,
        "alternatives": [],
    }

    # Если есть последние сообщения, смотрим на их язык
    if last_messages and len(last_messages) > 0:
        # Берём последние 3 сообщения от клиента (не от нас)
        client_messages = [
            m for m in last_messages[-5:]
            if m.get("is_outgoing") == False or m.get("sender_type") == "client"
        ]

        if client_messages:
            last_lang = client_messages[-1].get("language_detection", {}).get("language")
            if last_lang and last_lang != "unknown":
                result["suggested_language"] = last_lang
                result["reason"] = "last_message"
                result["confidence"] = 0.85
                return result

    # Используем основной язык из профиля
    primary_lang = contact_profile.get("primary_language", "unknown")

    if primary_lang != "unknown":
        distribution = contact_profile.get("language_distribution", {})
        primary_data = distribution.get(primary_lang, {})

        result["suggested_language"] = primary_lang
        result["confidence"] = min(primary_data.get("percentage", 50) / 100, 0.95)
        result["reason"] = "primary_language"

        # Альтернативы
        for lang, data in distribution.items():
            if lang != primary_lang and data.get("percentage", 0) > 10:
                result["alternatives"].append({
                    "language": lang,
                    "percentage": data["percentage"],
                })

    # Если контакт многоязычный, снижаем уверенность
    if contact_profile.get("multilingual"):
        result["confidence"] *= 0.8
        result["reason"] += "_multilingual"

    return result


# ═══════════════════════════════════════════════════════════════
# ДЕТЕКЦИЯ CODE-SWITCHING
# ═══════════════════════════════════════════════════════════════

def analyze_code_switching(text: str) -> Dict[str, Any]:
    """
    Анализировать смешение языков в одном сообщении (code-switching).

    Returns:
        Dict с результатами:
        - is_code_switching: наличие переключения языков
        - segments: сегменты текста по языкам
        - dominant_language: доминирующий язык
        - secondary_languages: второстепенные языки
    """
    result = {
        "is_code_switching": False,
        "segments": [],
        "dominant_language": "unknown",
        "secondary_languages": [],
        "languages_found": [],
    }

    # Проверяем смешение скриптов
    if not is_mixed_script(text, threshold=0.15):
        detection = detect_language(text, use_lingua=True)
        result["dominant_language"] = detection["language"]
        result["languages_found"] = [detection["language"]]
        return result

    result["is_code_switching"] = True

    # Разбиваем текст на сегменты по скриптам
    scripts = detect_script(text)

    # Определяем языки для каждого скрипта
    languages_found = []

    if scripts.get("cyrillic", 0) > 0:
        languages_found.append("ru")
    if scripts.get("arabic", 0) > 0:
        languages_found.append("ar")
    if scripts.get("chinese", 0) > 0:
        languages_found.append("zh")
    if scripts.get("devanagari", 0) > 0:
        languages_found.append("hi")
    if scripts.get("latin", 0) > 0:
        # Для латиницы нужна дополнительная детекция
        latin_text = ''.join(c for c in text if SCRIPT_PATTERNS["latin"].match(c))
        if len(latin_text) > 3:
            latin_detection = detect_language(latin_text, use_lingua=True)
            if latin_detection["language"] not in languages_found:
                languages_found.append(latin_detection["language"])

    result["languages_found"] = languages_found

    # Определяем доминирующий язык
    if languages_found:
        # Подсчитываем символы для каждого
        lang_chars = {}
        for lang in languages_found:
            script = SUPPORTED_LANGUAGES.get(lang, {}).get("script", "latin")
            lang_chars[lang] = scripts.get(script, 0)

        result["dominant_language"] = max(lang_chars, key=lang_chars.get)
        result["secondary_languages"] = [l for l in languages_found if l != result["dominant_language"]]

    return result


# ═══════════════════════════════════════════════════════════════
# СТАТИСТИКА ПО БАЗЕ
# ═══════════════════════════════════════════════════════════════

def calculate_database_statistics(messages: List[Dict]) -> Dict[str, Any]:
    """
    Вычислить общую статистику по языкам в базе сообщений.

    Returns:
        Dict со статистикой
    """
    total = len(messages)
    language_counts = Counter()
    method_counts = Counter()
    mixed_count = 0
    translit_count = 0
    unknown_count = 0

    for msg in messages:
        detection = msg.get("language_detection", {})
        lang = detection.get("language", "unknown")
        method = detection.get("method", "none")

        language_counts[lang] += 1
        method_counts[method] += 1

        if lang == "unknown":
            unknown_count += 1
        if detection.get("is_mixed"):
            mixed_count += 1
        if detection.get("is_transliteration"):
            translit_count += 1

    # Формируем статистику по языкам
    language_stats = {}
    for lang, count in language_counts.most_common():
        lang_info = SUPPORTED_LANGUAGES.get(lang, {})
        language_stats[lang] = {
            "count": count,
            "percentage": round(count / total * 100, 2) if total > 0 else 0,
            "name": lang_info.get("name", lang),
            "name_ru": lang_info.get("name_ru", lang),
        }

    return {
        "total_messages": total,
        "analyzed_messages": total - unknown_count,
        "unknown_messages": unknown_count,
        "unique_languages": len([l for l in language_counts if l != "unknown"]),
        "language_distribution": language_stats,
        "detection_methods": dict(method_counts.most_common()),
        "mixed_messages": mixed_count,
        "mixed_percentage": round(mixed_count / total * 100, 2) if total > 0 else 0,
        "transliteration_messages": translit_count,
        "transliteration_percentage": round(translit_count / total * 100, 2) if total > 0 else 0,
        "top_languages": [
            {"language": lang, "count": count, "percentage": round(count/total*100, 1)}
            for lang, count in language_counts.most_common(5) if lang != "unknown"
        ],
    }


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ С ЯЗЫКОВЫМИ МЕТКАМИ
# ═══════════════════════════════════════════════════════════════

def export_messages_with_language(
    messages: List[Dict],
    output_file: Path,
    format: str = "jsonl"
) -> int:
    """
    Экспортировать сообщения с языковыми метками.

    Args:
        messages: Список сообщений с детекцией языка
        output_file: Путь к выходному файлу
        format: Формат (jsonl, json)

    Returns:
        Количество экспортированных сообщений
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if format == "jsonl":
        with open(output_file, 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    print(f"Экспортировано {len(messages)} сообщений в {output_file}")
    return len(messages)


def export_language_tagged_json(
    messages: List[Dict],
    output_dir: Path
) -> Dict[str, Path]:
    """
    Экспортировать сообщения сгруппированные по языкам.

    Returns:
        Dict с путями к файлам по языкам
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Группируем по языкам
    by_language = defaultdict(list)

    for msg in messages:
        lang = msg.get("language_detection", {}).get("language", "unknown")
        by_language[lang].append(msg)

    # Сохраняем каждый язык в отдельный файл
    output_files = {}

    for lang, lang_messages in by_language.items():
        output_file = output_dir / f"messages_{lang}.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for msg in lang_messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        output_files[lang] = output_file
        print(f"  {lang}: {len(lang_messages)} сообщений -> {output_file}")

    return output_files


# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_messages_jsonl(filepath: Path) -> List[Dict]:
    """Загрузить сообщения из JSONL файла."""
    messages = []
    filepath = Path(filepath)

    if not filepath.exists():
        print(f"Файл не найден: {filepath}")
        return messages

    print(f"Загрузка сообщений из {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                messages.append(msg)
            except json.JSONDecodeError as e:
                if line_num <= 5:
                    print(f"  Ошибка JSON в строке {line_num}: {e}")

    print(f"Загружено {len(messages)} сообщений")
    return messages


def save_json(data: Any, filepath: Path):
    """Сохранить данные в JSON."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Сохранено: {filepath}")


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def run_language_detection(
    input_file: Path,
    output_dir: Path,
    use_lingua: bool = True,
    export_by_language: bool = False,
    limit: int = 0
) -> Dict[str, Any]:
    """
    Главная функция детекции языков.

    Args:
        input_file: Входной JSONL файл с сообщениями
        output_dir: Директория для результатов
        use_lingua: Использовать lingua-py
        export_by_language: Экспортировать сообщения по языкам
        limit: Ограничение количества сообщений (0 = без ограничения)

    Returns:
        Dict с результатами и статистикой
    """
    # Загружаем сообщения
    messages = load_messages_jsonl(input_file)

    if not messages:
        print("Сообщения не найдены!")
        return None

    if limit > 0:
        messages = messages[:limit]
        print(f"Ограничено до {limit} сообщений")

    # Создаём директории
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Детекция языков
    print(f"\nОпределение языков для {len(messages)} сообщений...")
    print(f"  Используем lingua: {use_lingua and LINGUA_AVAILABLE}")
    print(f"  Используем langdetect: {LANGDETECT_AVAILABLE}")

    processed = 0
    for i, msg in enumerate(messages):
        detect_message_language(msg)
        processed += 1

        if (i + 1) % 10000 == 0:
            print(f"  Обработано: {i + 1}/{len(messages)}")

    print(f"Обработано: {processed} сообщений")

    # Статистика
    print("\nВычисление статистики...")
    stats = calculate_database_statistics(messages)

    # Профили контактов
    print("Построение профилей контактов...")
    contacts = set(m.get("contact_id", m.get("jid", "unknown")) for m in messages)
    contact_profiles = {}

    for contact_id in contacts:
        contact_messages = [m for m in messages if m.get("contact_id", m.get("jid")) == contact_id]
        profile = build_contact_language_profile(contact_messages, contact_id)
        contact_profiles[contact_id] = profile

    # Сохраняем результаты
    print("\nСохранение результатов...")

    # 1. Статистика
    save_json(
        {
            "statistics": stats,
            "metadata": {
                "source_file": str(input_file),
                "analyzed_at": datetime.now().isoformat(),
                "total_contacts": len(contacts),
                "lingua_used": use_lingua and LINGUA_AVAILABLE,
                "langdetect_used": LANGDETECT_AVAILABLE,
            }
        },
        output_dir / "language_statistics.json"
    )

    # 2. Профили контактов
    save_json(
        {
            "profiles": contact_profiles,
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_contacts": len(contacts),
            }
        },
        output_dir / "contact_language_profiles.json"
    )

    # 3. Сообщения с языковыми метками
    export_messages_with_language(
        messages,
        output_dir / "messages_with_language.jsonl",
        format="jsonl"
    )

    # 4. Опционально: экспорт по языкам
    if export_by_language:
        print("\nЭкспорт по языкам...")
        export_language_tagged_json(
            messages,
            output_dir / "by_language"
        )

    # Выводим сводку
    print("\n" + "=" * 60)
    print("ДЕТЕКЦИЯ ЯЗЫКОВ ЗАВЕРШЕНА")
    print("=" * 60)
    print(f"Всего сообщений: {stats['total_messages']}")
    print(f"Проанализировано: {stats['analyzed_messages']}")
    print(f"Уникальных языков: {stats['unique_languages']}")
    print(f"Смешанных сообщений: {stats['mixed_messages']} ({stats['mixed_percentage']}%)")
    print(f"Транслитерация: {stats['transliteration_messages']} ({stats['transliteration_percentage']}%)")
    print("")
    print("Топ языков:")
    for lang_data in stats['top_languages']:
        lang_name = SUPPORTED_LANGUAGES.get(lang_data['language'], {}).get('name_ru', lang_data['language'])
        print(f"  {lang_name}: {lang_data['count']} ({lang_data['percentage']}%)")
    print("=" * 60)

    return {
        "statistics": stats,
        "contact_profiles": contact_profiles,
        "messages_count": len(messages),
        "output_dir": str(output_dir),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Детекция языка сообщений WhatsApp"
    )
    parser.add_argument(
        "--input", "-i",
        default=str(MESSAGES_FILE),
        help="Входной JSONL файл с сообщениями"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=str(LANGUAGE_DIR),
        help="Директория для результатов"
    )
    parser.add_argument(
        "--no-lingua",
        action="store_true",
        help="Не использовать lingua-py (быстрее, но менее точно)"
    )
    parser.add_argument(
        "--export-by-language",
        action="store_true",
        help="Экспортировать сообщения сгруппированные по языкам"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Ограничить количество сообщений для обработки"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Тестовый режим (детекция примеров)"
    )

    args = parser.parse_args()

    if args.test:
        # Тестовые примеры
        print("=" * 60)
        print("ТЕСТИРОВАНИЕ ДЕТЕКЦИИ ЯЗЫКОВ")
        print("=" * 60)

        test_texts = [
            "Привет, как дела?",
            "Hello, how are you?",
            "مرحبا كيف حالك",
            "Guten Tag, wie geht es Ihnen?",
            "Bonjour, comment allez-vous?",
            "Ciao, come stai?",
            "Hola, como estas?",
            "你好，你好吗？",
            "नमस्ते, आप कैसे हैं?",
            "Privet kak dela?",  # Транслитерация
            "Shukran habibi",     # Арабская транслитерация
            "Hello привет mix",   # Смешанный
            "Экскурсия в Dubai tomorrow",  # Code-switching
            "👍🏻",                # Только emoji
            "https://google.com", # Ссылка
        ]

        for text in test_texts:
            result = detect_language(text)
            print(f"\nТекст: {text}")
            print(f"  Язык: {result['language']} ({result['confidence']:.2f})")
            print(f"  Метод: {result['method']}")
            if result.get('is_transliteration'):
                print(f"  Транслитерация: {result['is_transliteration']['type']}")
            if result.get('is_mixed'):
                print(f"  Смешанный текст: да")
            if result.get('alternatives'):
                print(f"  Альтернативы: {result['alternatives']}")

        print("\n" + "=" * 60)
        return

    # Основной запуск
    run_language_detection(
        input_file=Path(args.input),
        output_dir=Path(args.output_dir),
        use_lingua=not args.no_lingua,
        export_by_language=args.export_by_language,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
