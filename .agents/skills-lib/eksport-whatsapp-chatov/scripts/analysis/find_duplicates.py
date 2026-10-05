#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск и объединение дубликатов контактов в базе WhatsApp чатов.

Функции:
1. Детекция одного человека с разных номеров:
   - Похожие имена (fuzzy matching)
   - Одинаковый email
   - Похожий стиль общения
2. Нормализация телефонов (+7 vs 8)
3. Группировка дубликатов
4. Merge suggestions
5. Автоматическое объединение (с подтверждением)
6. Конфликты данных
7. История номеров контакта
8. Экспорт: JSON с группами

Вход: D:/Downloads/Chats/_база/json/contacts.json
Выход: D:/Downloads/Chats/_база/json/duplicates.json
"""

import sys
import json
import re
import uuid
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Set, Any

# Настройка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent))
from config import JSON_DIR, RAW_DIR, ensure_directories

# Библиотеки для fuzzy matching и телефонов
try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("[!] fuzzywuzzy не установлен. Установите: pip install fuzzywuzzy python-Levenshtein")

try:
    import phonenumbers
    from phonenumbers import PhoneNumberFormat, NumberParseException
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    print("[!] phonenumbers не установлен. Установите: pip install phonenumbers")


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ И КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

CONTACTS_FILE = JSON_DIR / "contacts.json"
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
OUTPUT_FILE = JSON_DIR / "duplicates.json"
MERGED_CONTACTS_FILE = JSON_DIR / "contacts_merged.json"

# Пороги для детекции дубликатов
THRESHOLDS = {
    "name_exact": 100,        # Точное совпадение имени
    "name_high": 90,          # Высокая похожесть имени
    "name_medium": 80,        # Средняя похожесть имени
    "name_low": 70,           # Минимальный порог имени
    "style_similarity": 0.6,  # Похожесть стиля общения
    "common_words": 5,        # Минимум общих уникальных слов
}

# Веса для расчёта confidence score
WEIGHTS = {
    "name_match": 0.30,
    "phone_normalized": 0.25,
    "email_match": 0.20,
    "style_similarity": 0.15,
    "metadata_match": 0.10,
}

# Страны СНГ с альтернативными кодами
CIS_PHONE_CODES = {
    "7": "RU",      # Россия
    "77": "KZ",     # Казахстан (77xx)
    "375": "BY",    # Беларусь
    "380": "UA",    # Украина
    "998": "UZ",    # Узбекистан
    "996": "KG",    # Кыргызстан
    "992": "TJ",    # Таджикистан
    "374": "AM",    # Армения
    "995": "GE",    # Грузия
    "994": "AZ",    # Азербайджан
}


# ═══════════════════════════════════════════════════════════════
# НОРМАЛИЗАЦИЯ ТЕЛЕФОНОВ
# ═══════════════════════════════════════════════════════════════

def normalize_phone(phone: str, default_region: str = "RU") -> Dict[str, str]:
    """
    Нормализует телефонный номер в международный формат.

    Возвращает:
    {
        "original": "+79123456789",
        "normalized": "+79123456789",
        "e164": "+79123456789",
        "national": "8 912 345-67-89",
        "country_code": "7",
        "country": "RU",
        "is_valid": True
    }
    """
    result = {
        "original": phone,
        "normalized": "",
        "e164": "",
        "national": "",
        "country_code": "",
        "country": "",
        "is_valid": False
    }

    if not phone:
        return result

    # Убираем все символы кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Специальная обработка российских номеров
    # 8xxxxxxxxxx -> +7xxxxxxxxxx
    if cleaned.startswith('8') and len(cleaned) == 11:
        cleaned = '+7' + cleaned[1:]

    # Добавляем + если нет
    if not cleaned.startswith('+'):
        # Если начинается с 7 и длина 11 - это Россия
        if cleaned.startswith('7') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        # Если 10 цифр - предполагаем Россию
        elif len(cleaned) == 10:
            cleaned = '+7' + cleaned
        else:
            cleaned = '+' + cleaned

    result["normalized"] = cleaned

    # Используем phonenumbers для валидации
    if PHONENUMBERS_AVAILABLE:
        try:
            parsed = phonenumbers.parse(cleaned, default_region)

            if phonenumbers.is_valid_number(parsed):
                result["is_valid"] = True
                result["e164"] = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
                result["national"] = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
                result["country_code"] = str(parsed.country_code)

                # Определяем страну
                country_code = str(parsed.country_code)
                if country_code in CIS_PHONE_CODES:
                    result["country"] = CIS_PHONE_CODES[country_code]
                else:
                    # Пробуем получить регион
                    from phonenumbers import geocoder
                    region = phonenumbers.region_code_for_number(parsed)
                    result["country"] = region or ""
        except NumberParseException:
            pass
    else:
        # Простая нормализация без phonenumbers
        result["e164"] = cleaned

        # Определяем страну по префиксу
        digits = cleaned.lstrip('+')
        for prefix, country in sorted(CIS_PHONE_CODES.items(), key=lambda x: -len(x[0])):
            if digits.startswith(prefix):
                result["country_code"] = prefix
                result["country"] = country
                result["is_valid"] = True
                break

    return result


def phones_are_same_person(phone1: str, phone2: str) -> Tuple[bool, float]:
    """
    Проверяет, могут ли два номера принадлежать одному человеку.

    Возвращает: (is_same, confidence)
    """
    if not phone1 or not phone2:
        return False, 0.0

    norm1 = normalize_phone(phone1)
    norm2 = normalize_phone(phone2)

    # Точное совпадение e164
    if norm1["e164"] and norm2["e164"]:
        if norm1["e164"] == norm2["e164"]:
            return True, 1.0

    # Совпадение нормализованных
    if norm1["normalized"] == norm2["normalized"]:
        return True, 0.95

    # Проверка для российских номеров (+7 vs 8)
    digits1 = re.sub(r'\D', '', phone1)
    digits2 = re.sub(r'\D', '', phone2)

    # Убираем первую цифру (7 или 8) и сравниваем
    if len(digits1) == 11 and len(digits2) == 11:
        if digits1[0] in '78' and digits2[0] in '78':
            if digits1[1:] == digits2[1:]:
                return True, 0.95

    # Номера из одной страны, но разные
    if norm1["country"] and norm1["country"] == norm2["country"]:
        # Проверяем последние 7-9 цифр (может быть один номер без кода города)
        last_digits1 = digits1[-9:] if len(digits1) >= 9 else digits1
        last_digits2 = digits2[-9:] if len(digits2) >= 9 else digits2

        if last_digits1 == last_digits2:
            return True, 0.7

    return False, 0.0


# ═══════════════════════════════════════════════════════════════
# FUZZY MATCHING ИМЁН
# ═══════════════════════════════════════════════════════════════

def clean_name(name: str) -> str:
    """Очищает имя для сравнения."""
    if not name:
        return ""

    # Приводим к нижнему регистру
    name = name.lower().strip()

    # Убираем эмодзи и спецсимволы
    name = re.sub(r'[\U0001F000-\U0001FFFF]', '', name)  # emoji
    name = re.sub(r'[^\w\s\-]', ' ', name)  # спецсимволы

    # Убираем типичные префиксы из WhatsApp
    prefixes_to_remove = [
        r'^\+\d+',      # +79123456789
        r'^whatsapp',   # WhatsApp ...
        r'^wa\s',       # WA ...
    ]
    for pattern in prefixes_to_remove:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # Нормализуем пробелы
    name = ' '.join(name.split())

    return name


def extract_name_parts(name: str) -> Dict[str, str]:
    """
    Извлекает части имени.

    Возвращает:
    {
        "full": "Иван Петров",
        "first": "Иван",
        "last": "Петров",
        "initials": "ИП"
    }
    """
    cleaned = clean_name(name)
    parts = cleaned.split()

    result = {
        "full": cleaned,
        "first": "",
        "last": "",
        "initials": ""
    }

    if parts:
        result["first"] = parts[0]
        if len(parts) > 1:
            result["last"] = parts[-1]

        # Инициалы
        initials = ''.join(p[0].upper() for p in parts if p)
        result["initials"] = initials

    return result


def names_similarity(name1: str, name2: str) -> Dict[str, Any]:
    """
    Вычисляет похожесть имён.

    Возвращает:
    {
        "score": 85,
        "match_type": "partial",  # exact, partial, initials, none
        "details": {...}
    }
    """
    result = {
        "score": 0,
        "match_type": "none",
        "details": {}
    }

    if not name1 or not name2:
        return result

    clean1 = clean_name(name1)
    clean2 = clean_name(name2)

    if not clean1 or not clean2:
        return result

    # Точное совпадение
    if clean1 == clean2:
        result["score"] = 100
        result["match_type"] = "exact"
        return result

    # Используем fuzzywuzzy
    if FUZZYWUZZY_AVAILABLE:
        # Разные методы сравнения
        ratio = fuzz.ratio(clean1, clean2)
        partial_ratio = fuzz.partial_ratio(clean1, clean2)
        token_sort = fuzz.token_sort_ratio(clean1, clean2)
        token_set = fuzz.token_set_ratio(clean1, clean2)

        # Берём лучший результат
        best_score = max(ratio, partial_ratio, token_sort, token_set)

        result["score"] = best_score
        result["details"] = {
            "ratio": ratio,
            "partial_ratio": partial_ratio,
            "token_sort": token_sort,
            "token_set": token_set
        }

        if best_score >= THRESHOLDS["name_exact"]:
            result["match_type"] = "exact"
        elif best_score >= THRESHOLDS["name_high"]:
            result["match_type"] = "high"
        elif best_score >= THRESHOLDS["name_medium"]:
            result["match_type"] = "partial"
        elif best_score >= THRESHOLDS["name_low"]:
            result["match_type"] = "low"
    else:
        # Простое сравнение без fuzzywuzzy
        parts1 = extract_name_parts(name1)
        parts2 = extract_name_parts(name2)

        # Проверяем совпадение частей
        if parts1["first"] == parts2["first"]:
            result["score"] = 70
            result["match_type"] = "partial"
        elif parts1["initials"] == parts2["initials"] and len(parts1["initials"]) >= 2:
            result["score"] = 50
            result["match_type"] = "initials"

    return result


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ СТИЛЯ ОБЩЕНИЯ
# ═══════════════════════════════════════════════════════════════

def extract_writing_style(messages: List[Dict]) -> Dict[str, Any]:
    """
    Извлекает характеристики стиля письма из сообщений.

    Анализирует:
    - Типичные приветствия
    - Характерные слова и фразы
    - Пунктуация
    - Средняя длина сообщений
    - Время активности
    """
    if not messages:
        return {}

    style = {
        "greetings": set(),
        "signature_words": set(),
        "avg_message_length": 0,
        "uses_emoji": False,
        "uses_caps": False,
        "punctuation_style": "",
        "active_hours": [],
        "common_words": set(),
        "language": "unknown"
    }

    total_length = 0
    all_words = []
    hour_counts = defaultdict(int)

    for msg in messages:
        text = msg.get("text", "") or msg.get("message", "") or ""

        if not text:
            continue

        # Длина сообщений
        total_length += len(text)

        # Слова
        words = re.findall(r'\b[а-яёa-z]{3,}\b', text.lower())
        all_words.extend(words)

        # Эмодзи
        if re.search(r'[\U0001F000-\U0001FFFF]', text):
            style["uses_emoji"] = True

        # КАПС
        if re.search(r'[A-ZА-ЯЁ]{3,}', text):
            style["uses_caps"] = True

        # Приветствия
        greetings = re.findall(
            r'\b(привет|здравствуйте|добрый\s+день|доброе\s+утро|hello|hi|hey)\b',
            text.lower()
        )
        style["greetings"].update(greetings)

        # Время активности
        timestamp = msg.get("timestamp") or msg.get("datetime")
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    if 'T' in timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        # Пробуем разные форматы
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S']:
                            try:
                                dt = datetime.strptime(timestamp, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            continue
                    hour_counts[dt.hour] += 1
            except (ValueError, AttributeError):
                pass

    # Статистика
    if messages:
        style["avg_message_length"] = total_length / len(messages)

    # Частые слова (исключая стоп-слова)
    stop_words = {
        'это', 'как', 'для', 'что', 'при', 'или', 'если', 'есть', 'был', 'была',
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had'
    }
    word_counts = defaultdict(int)
    for word in all_words:
        if word not in stop_words and len(word) > 3:
            word_counts[word] += 1

    # Топ-20 частых слов
    top_words = sorted(word_counts.items(), key=lambda x: -x[1])[:20]
    style["common_words"] = set(w for w, _ in top_words)

    # Часы активности (топ-3)
    if hour_counts:
        top_hours = sorted(hour_counts.items(), key=lambda x: -x[1])[:3]
        style["active_hours"] = [h for h, _ in top_hours]

    # Определяем язык по частотности
    ru_words = sum(1 for w in all_words if re.match(r'^[а-яё]+$', w))
    en_words = sum(1 for w in all_words if re.match(r'^[a-z]+$', w))

    if ru_words > en_words:
        style["language"] = "ru"
    elif en_words > 0:
        style["language"] = "en"

    # Конвертируем set в list для JSON
    style["greetings"] = list(style["greetings"])
    style["common_words"] = list(style["common_words"])

    return style


def styles_similarity(style1: Dict, style2: Dict) -> float:
    """
    Вычисляет похожесть двух стилей общения.

    Возвращает значение от 0.0 до 1.0
    """
    if not style1 or not style2:
        return 0.0

    score = 0.0
    factors = 0

    # Общие частые слова
    words1 = set(style1.get("common_words", []))
    words2 = set(style2.get("common_words", []))

    if words1 and words2:
        common = words1 & words2
        total = words1 | words2
        if total:
            jaccard = len(common) / len(total)
            score += jaccard
            factors += 1

    # Похожая длина сообщений (допуск 30%)
    len1 = style1.get("avg_message_length", 0)
    len2 = style2.get("avg_message_length", 0)

    if len1 > 0 and len2 > 0:
        ratio = min(len1, len2) / max(len1, len2)
        if ratio > 0.7:
            score += ratio
        factors += 1

    # Использование эмодзи
    emoji1 = style1.get("uses_emoji", False)
    emoji2 = style2.get("uses_emoji", False)
    if emoji1 == emoji2:
        score += 0.5
    factors += 0.5

    # Язык
    lang1 = style1.get("language", "unknown")
    lang2 = style2.get("language", "unknown")
    if lang1 == lang2 and lang1 != "unknown":
        score += 1.0
        factors += 1

    # Похожие часы активности
    hours1 = set(style1.get("active_hours", []))
    hours2 = set(style2.get("active_hours", []))

    if hours1 and hours2:
        common_hours = hours1 & hours2
        if common_hours:
            score += len(common_hours) / 3  # Максимум 3 часа
        factors += 1

    if factors > 0:
        return score / factors

    return 0.0


# ═══════════════════════════════════════════════════════════════
# ПОИСК ДУБЛИКАТОВ
# ═══════════════════════════════════════════════════════════════

class DuplicateFinder:
    """Класс для поиска и группировки дубликатов контактов."""

    def __init__(self, contacts: List[Dict], messages_by_jid: Dict[str, List[Dict]] = None):
        self.contacts = contacts
        self.messages_by_jid = messages_by_jid or {}

        # Индексы для быстрого поиска
        self.by_phone = defaultdict(list)      # normalized_phone -> [contact_ids]
        self.by_email = defaultdict(list)      # email -> [contact_ids]
        self.by_name = defaultdict(list)       # cleaned_name -> [contact_ids]

        # Результаты
        self.duplicate_groups = []             # Группы дубликатов
        self.styles_cache = {}                 # JID -> style

        self._build_indexes()

    def _build_indexes(self):
        """Строит индексы для быстрого поиска."""
        for contact in self.contacts:
            contact_id = contact.get("contact_id") or contact.get("id")
            jid = contact.get("jid", "")

            if not contact_id:
                continue

            # Индекс по телефону
            phone = contact.get("phone", "")
            if phone:
                norm = normalize_phone(phone)
                if norm["e164"]:
                    self.by_phone[norm["e164"]].append(contact_id)
                elif norm["normalized"]:
                    self.by_phone[norm["normalized"]].append(contact_id)

            # Индекс по email
            # Email может быть в notes или tags
            notes = contact.get("notes", "")
            tags = contact.get("tags", [])

            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

            for text in [notes, ' '.join(str(t) for t in tags)]:
                emails = re.findall(email_pattern, text)
                for email in emails:
                    self.by_email[email.lower()].append(contact_id)

            # Индекс по имени
            name = contact.get("name") or contact.get("display_name") or ""
            if name:
                cleaned = clean_name(name)
                if cleaned and len(cleaned) >= 3:
                    self.by_name[cleaned].append(contact_id)

    def _get_contact_style(self, contact: Dict) -> Dict:
        """Получает или вычисляет стиль общения контакта."""
        jid = contact.get("jid", "")

        if jid in self.styles_cache:
            return self.styles_cache[jid]

        messages = self.messages_by_jid.get(jid, [])
        style = extract_writing_style(messages)

        self.styles_cache[jid] = style
        return style

    def _calculate_similarity(self, contact1: Dict, contact2: Dict) -> Dict[str, Any]:
        """
        Вычисляет общую похожесть двух контактов.

        Возвращает:
        {
            "is_duplicate": True,
            "confidence": 0.85,
            "reasons": ["similar_name", "same_country"],
            "details": {...}
        }
        """
        result = {
            "is_duplicate": False,
            "confidence": 0.0,
            "reasons": [],
            "details": {}
        }

        score = 0.0

        # 1. Сравнение телефонов
        phone1 = contact1.get("phone", "")
        phone2 = contact2.get("phone", "")

        if phone1 and phone2:
            is_same, phone_conf = phones_are_same_person(phone1, phone2)
            result["details"]["phone"] = {
                "phone1": phone1,
                "phone2": phone2,
                "is_same": is_same,
                "confidence": phone_conf
            }

            if is_same:
                score += WEIGHTS["phone_normalized"] * phone_conf
                result["reasons"].append("same_phone")

        # 2. Сравнение имён
        name1 = contact1.get("name") or contact1.get("display_name") or ""
        name2 = contact2.get("name") or contact2.get("display_name") or ""

        if name1 and name2:
            name_sim = names_similarity(name1, name2)
            result["details"]["name"] = name_sim

            if name_sim["score"] >= THRESHOLDS["name_low"]:
                score += WEIGHTS["name_match"] * (name_sim["score"] / 100)
                result["reasons"].append(f"similar_name_{name_sim['match_type']}")

        # 3. Сравнение email (из notes/tags)
        # Уже проиндексировано, проверяем наличие общих email
        contact1_id = contact1.get("contact_id") or contact1.get("id")
        contact2_id = contact2.get("contact_id") or contact2.get("id")

        for email, contact_ids in self.by_email.items():
            if contact1_id in contact_ids and contact2_id in contact_ids:
                score += WEIGHTS["email_match"]
                result["reasons"].append(f"same_email:{email}")
                result["details"]["email"] = email
                break

        # 4. Сравнение стиля общения (если есть сообщения)
        if self.messages_by_jid:
            style1 = self._get_contact_style(contact1)
            style2 = self._get_contact_style(contact2)

            if style1 and style2:
                style_sim = styles_similarity(style1, style2)
                result["details"]["style_similarity"] = style_sim

                if style_sim >= THRESHOLDS["style_similarity"]:
                    score += WEIGHTS["style_similarity"] * style_sim
                    result["reasons"].append("similar_style")

        # 5. Метаданные (страна, язык)
        country1 = contact1.get("country_code", "")
        country2 = contact2.get("country_code", "")
        lang1 = contact1.get("language", "")
        lang2 = contact2.get("language", "")

        metadata_score = 0.0
        if country1 and country1 == country2:
            metadata_score += 0.5
            result["reasons"].append("same_country")
        if lang1 and lang1 == lang2 and lang1 != "unknown":
            metadata_score += 0.5
            result["reasons"].append("same_language")

        score += WEIGHTS["metadata_match"] * metadata_score

        # Итоговая оценка
        result["confidence"] = min(score, 1.0)

        # Определяем, является ли дубликатом
        # Требуем хотя бы 2 совпадения или высокую уверенность
        if len(result["reasons"]) >= 2 or result["confidence"] >= 0.6:
            if any(r.startswith("same_phone") or r.startswith("same_email") for r in result["reasons"]):
                result["is_duplicate"] = True
            elif result["confidence"] >= 0.5 and len(result["reasons"]) >= 2:
                result["is_duplicate"] = True

        return result

    def find_duplicates(self, min_confidence: float = 0.4) -> List[Dict]:
        """
        Находит все группы дубликатов.

        Возвращает список групп:
        [
            {
                "group_id": "uuid",
                "contacts": [...],
                "confidence": 0.85,
                "reasons": [...],
                "suggested_primary": "contact_id"
            }
        ]
        """
        print("\n[1/4] Поиск по телефонам...")

        # Используем Union-Find для группировки
        parent = {}

        def find(x):
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Связи между контактами
        links = []  # (contact1_id, contact2_id, similarity_info)

        # Контакты по ID для быстрого доступа
        contacts_by_id = {
            c.get("contact_id") or c.get("id"): c
            for c in self.contacts
            if c.get("contact_id") or c.get("id")
        }

        # 1. Быстрый поиск по индексам
        checked_pairs = set()

        # По телефону
        for phone, contact_ids in self.by_phone.items():
            if len(contact_ids) > 1:
                for i, cid1 in enumerate(contact_ids):
                    for cid2 in contact_ids[i+1:]:
                        pair = tuple(sorted([cid1, cid2]))
                        if pair not in checked_pairs:
                            checked_pairs.add(pair)

                            c1 = contacts_by_id.get(cid1)
                            c2 = contacts_by_id.get(cid2)

                            if c1 and c2:
                                sim = self._calculate_similarity(c1, c2)
                                if sim["confidence"] >= min_confidence:
                                    links.append((cid1, cid2, sim))
                                    union(cid1, cid2)

        print(f"    Найдено связей по телефонам: {len(links)}")

        # По email
        print("\n[2/4] Поиск по email...")
        email_links = 0

        for email, contact_ids in self.by_email.items():
            if len(contact_ids) > 1:
                for i, cid1 in enumerate(contact_ids):
                    for cid2 in contact_ids[i+1:]:
                        pair = tuple(sorted([cid1, cid2]))
                        if pair not in checked_pairs:
                            checked_pairs.add(pair)

                            c1 = contacts_by_id.get(cid1)
                            c2 = contacts_by_id.get(cid2)

                            if c1 and c2:
                                sim = self._calculate_similarity(c1, c2)
                                if sim["confidence"] >= min_confidence:
                                    links.append((cid1, cid2, sim))
                                    union(cid1, cid2)
                                    email_links += 1

        print(f"    Найдено связей по email: {email_links}")

        # По имени (fuzzy)
        print("\n[3/4] Поиск по именам (fuzzy matching)...")
        name_links = 0

        if FUZZYWUZZY_AVAILABLE:
            # Группируем контакты с похожими именами
            all_names = list(self.by_name.keys())

            for i, name1 in enumerate(all_names):
                contact_ids1 = self.by_name[name1]

                # Ищем похожие имена
                for name2 in all_names[i+1:]:
                    name_sim = names_similarity(name1, name2)

                    if name_sim["score"] >= THRESHOLDS["name_medium"]:
                        contact_ids2 = self.by_name[name2]

                        for cid1 in contact_ids1:
                            for cid2 in contact_ids2:
                                pair = tuple(sorted([cid1, cid2]))
                                if pair not in checked_pairs:
                                    checked_pairs.add(pair)

                                    c1 = contacts_by_id.get(cid1)
                                    c2 = contacts_by_id.get(cid2)

                                    if c1 and c2:
                                        sim = self._calculate_similarity(c1, c2)
                                        if sim["confidence"] >= min_confidence:
                                            links.append((cid1, cid2, sim))
                                            union(cid1, cid2)
                                            name_links += 1

        print(f"    Найдено связей по именам: {name_links}")

        # Группируем по Union-Find
        print("\n[4/4] Группировка дубликатов...")

        groups_dict = defaultdict(list)
        for contact_id in contacts_by_id:
            root = find(contact_id)
            groups_dict[root].append(contact_id)

        # Формируем результат
        self.duplicate_groups = []

        for root, contact_ids in groups_dict.items():
            if len(contact_ids) > 1:
                # Собираем информацию о группе
                contacts = [contacts_by_id[cid] for cid in contact_ids if cid in contacts_by_id]

                # Находим все связи внутри группы
                group_links = [
                    link for link in links
                    if link[0] in contact_ids and link[1] in contact_ids
                ]

                # Агрегируем причины
                all_reasons = set()
                total_confidence = 0.0

                for _, _, sim in group_links:
                    all_reasons.update(sim.get("reasons", []))
                    total_confidence += sim.get("confidence", 0)

                avg_confidence = total_confidence / len(group_links) if group_links else 0.5

                # Выбираем primary контакт (с наибольшим количеством сообщений)
                primary = max(
                    contacts,
                    key=lambda c: c.get("total_messages", 0),
                    default=contacts[0]
                )

                group = {
                    "group_id": str(uuid.uuid4()),
                    "contacts": contacts,
                    "contact_ids": contact_ids,
                    "confidence": round(avg_confidence, 3),
                    "reasons": sorted(list(all_reasons)),
                    "suggested_primary": primary.get("contact_id") or primary.get("id"),
                    "primary_name": primary.get("name") or primary.get("display_name"),
                    "phone_numbers": list(set(
                        c.get("phone", "") for c in contacts if c.get("phone")
                    ))
                }

                self.duplicate_groups.append(group)

        # Сортируем по уверенности
        self.duplicate_groups.sort(key=lambda x: -x["confidence"])

        print(f"    Найдено групп дубликатов: {len(self.duplicate_groups)}")

        return self.duplicate_groups


# ═══════════════════════════════════════════════════════════════
# ОБЪЕДИНЕНИЕ КОНТАКТОВ
# ═══════════════════════════════════════════════════════════════

def merge_contacts(primary: Dict, duplicates: List[Dict]) -> Tuple[Dict, Dict]:
    """
    Объединяет дубликаты в один контакт.

    Возвращает: (merged_contact, conflicts)
    """
    merged = primary.copy()
    conflicts = {}

    # Собираем историю номеров
    all_phones = [primary.get("phone", "")]
    all_names = [primary.get("name", ""), primary.get("display_name", "")]
    all_tags = list(primary.get("tags", []))
    all_notes = [primary.get("notes", "")]

    # Накопители для статистики
    total_messages = primary.get("total_messages", 0)
    messages_sent = primary.get("messages_sent", 0)
    messages_received = primary.get("messages_received", 0)

    # Даты
    first_date = primary.get("first_message_date")
    last_date = primary.get("last_message_date")

    # Обрабатываем дубликаты
    for dup in duplicates:
        if dup.get("contact_id") == primary.get("contact_id"):
            continue

        # Телефоны
        phone = dup.get("phone", "")
        if phone and phone not in all_phones:
            all_phones.append(phone)

        # Имена
        name = dup.get("name", "")
        display_name = dup.get("display_name", "")
        if name and name not in all_names:
            all_names.append(name)
        if display_name and display_name not in all_names:
            all_names.append(display_name)

        # Теги
        for tag in dup.get("tags", []):
            if tag not in all_tags:
                all_tags.append(tag)

        # Заметки
        notes = dup.get("notes", "")
        if notes and notes not in all_notes:
            all_notes.append(notes)

        # Статистика
        total_messages += dup.get("total_messages", 0)
        messages_sent += dup.get("messages_sent", 0)
        messages_received += dup.get("messages_received", 0)

        # Даты
        dup_first = dup.get("first_message_date")
        dup_last = dup.get("last_message_date")

        if dup_first and (not first_date or dup_first < first_date):
            first_date = dup_first
        if dup_last and (not last_date or dup_last > last_date):
            last_date = dup_last

        # Проверяем конфликты
        for field in ["type", "subtype", "language", "country_code"]:
            primary_val = primary.get(field)
            dup_val = dup.get(field)

            if primary_val and dup_val and primary_val != dup_val:
                if field not in conflicts:
                    conflicts[field] = {
                        "primary": primary_val,
                        "alternatives": []
                    }
                if dup_val not in conflicts[field]["alternatives"]:
                    conflicts[field]["alternatives"].append(dup_val)

    # Обновляем merged контакт
    merged["total_messages"] = total_messages
    merged["messages_sent"] = messages_sent
    merged["messages_received"] = messages_received
    merged["first_message_date"] = first_date
    merged["last_message_date"] = last_date
    merged["tags"] = all_tags

    # Объединяем заметки
    merged["notes"] = "\n---\n".join(n for n in all_notes if n)

    # Добавляем историю номеров
    merged["phone_history"] = [p for p in all_phones if p]

    # Альтернативные имена
    merged["name_alternatives"] = [n for n in all_names if n and n != merged.get("name")]

    # Список объединённых контактов
    merged["merged_from"] = [
        dup.get("contact_id") or dup.get("id")
        for dup in duplicates
        if dup.get("contact_id") != primary.get("contact_id")
    ]

    return merged, conflicts


def apply_merge(contacts: List[Dict], group: Dict, confirm: bool = False) -> Tuple[List[Dict], Dict]:
    """
    Применяет объединение группы дубликатов.

    Возвращает: (updated_contacts, merge_info)
    """
    primary_id = group["suggested_primary"]
    contact_ids = set(group["contact_ids"])

    # Находим primary и duplicates
    primary = None
    duplicates = []
    other_contacts = []

    for contact in contacts:
        cid = contact.get("contact_id") or contact.get("id")

        if cid == primary_id:
            primary = contact
        elif cid in contact_ids:
            duplicates.append(contact)
        else:
            other_contacts.append(contact)

    if not primary:
        return contacts, {"error": "Primary contact not found"}

    # Объединяем
    merged, conflicts = merge_contacts(primary, duplicates)

    merge_info = {
        "primary_id": primary_id,
        "merged_ids": [d.get("contact_id") or d.get("id") for d in duplicates],
        "conflicts": conflicts,
        "merged_at": datetime.now().isoformat()
    }

    # Обновляем список контактов
    updated_contacts = other_contacts + [merged]

    return updated_contacts, merge_info


# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ И ОТЧЁТЫ
# ═══════════════════════════════════════════════════════════════

def generate_report(duplicate_groups: List[Dict]) -> str:
    """Генерирует текстовый отчёт о найденных дубликатах."""
    lines = [
        "=" * 70,
        "ОТЧЁТ О ДУБЛИКАТАХ КОНТАКТОВ",
        "=" * 70,
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Найдено групп дубликатов: {len(duplicate_groups)}",
        ""
    ]

    total_duplicates = sum(len(g["contacts"]) - 1 for g in duplicate_groups)
    lines.append(f"Всего дубликатов: {total_duplicates}")
    lines.append("")

    # Статистика по причинам
    reason_counts = defaultdict(int)
    for group in duplicate_groups:
        for reason in group.get("reasons", []):
            reason_counts[reason.split(":")[0]] += 1

    lines.append("Причины дубликатов:")
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  - {reason}: {count}")

    lines.append("")
    lines.append("-" * 70)

    # Детали по группам
    for i, group in enumerate(duplicate_groups[:20], 1):  # Топ-20
        lines.append(f"\nГруппа #{i} (уверенность: {group['confidence']:.0%})")
        lines.append(f"Причины: {', '.join(group['reasons'])}")
        lines.append(f"Предлагаемый основной: {group['primary_name']}")
        lines.append("Контакты:")

        for contact in group["contacts"]:
            name = contact.get("name") or contact.get("display_name") or "N/A"
            phone = contact.get("phone", "N/A")
            msgs = contact.get("total_messages", 0)
            is_primary = "PRIMARY" if contact.get("contact_id") == group["suggested_primary"] else ""
            lines.append(f"  - {name} | {phone} | {msgs} сообщ. {is_primary}")

        lines.append("-" * 70)

    if len(duplicate_groups) > 20:
        lines.append(f"\n... и ещё {len(duplicate_groups) - 20} групп")

    return "\n".join(lines)


def export_duplicates_json(duplicate_groups: List[Dict], output_file: Path):
    """Экспортирует дубликаты в JSON."""
    result = {
        "generated_at": datetime.now().isoformat(),
        "total_groups": len(duplicate_groups),
        "total_duplicates": sum(len(g["contacts"]) - 1 for g in duplicate_groups),
        "groups": []
    }

    for group in duplicate_groups:
        # Упрощаем контакты для экспорта
        simplified_contacts = []
        for contact in group["contacts"]:
            simplified_contacts.append({
                "contact_id": contact.get("contact_id") or contact.get("id"),
                "jid": contact.get("jid"),
                "name": contact.get("name"),
                "display_name": contact.get("display_name"),
                "phone": contact.get("phone"),
                "total_messages": contact.get("total_messages", 0),
                "language": contact.get("language"),
                "country_code": contact.get("country_code"),
            })

        result["groups"].append({
            "group_id": group["group_id"],
            "confidence": group["confidence"],
            "reasons": group["reasons"],
            "suggested_primary": group["suggested_primary"],
            "primary_name": group["primary_name"],
            "phone_numbers": group["phone_numbers"],
            "contacts": simplified_contacts
        })

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Экспортировано в: {output_file}")


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def load_contacts(filepath: Path) -> List[Dict]:
    """Загружает контакты из JSON."""
    if not filepath.exists():
        print(f"[!] Файл контактов не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get("contacts", [])


def load_messages_by_jid(filepath: Path) -> Dict[str, List[Dict]]:
    """Загружает сообщения и группирует по JID."""
    messages_by_jid = defaultdict(list)

    if not filepath.exists():
        print(f"[!] Файл сообщений не найден: {filepath}")
        return messages_by_jid

    print(f"Загрузка сообщений из {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    jid = msg.get("jid") or msg.get("chat_jid")
                    if jid:
                        messages_by_jid[jid].append(msg)
                except json.JSONDecodeError:
                    continue

    print(f"Загружено JID: {len(messages_by_jid)}")
    return messages_by_jid


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Поиск дубликатов контактов в базе WhatsApp чатов"
    )
    parser.add_argument(
        "--contacts", "-c",
        default=str(CONTACTS_FILE),
        help=f"Путь к файлу контактов (default: {CONTACTS_FILE})"
    )
    parser.add_argument(
        "--messages", "-m",
        default=str(MESSAGES_FILE),
        help=f"Путь к файлу сообщений для анализа стиля (default: {MESSAGES_FILE})"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(OUTPUT_FILE),
        help=f"Путь к выходному файлу (default: {OUTPUT_FILE})"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.4,
        help="Минимальный порог уверенности (default: 0.4)"
    )
    parser.add_argument(
        "--skip-style-analysis",
        action="store_true",
        help="Пропустить анализ стиля общения (быстрее, но менее точно)"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Интерактивное объединение найденных дубликатов"
    )
    parser.add_argument(
        "--auto-merge",
        type=float,
        default=None,
        help="Автоматически объединить дубликаты с уверенностью >= порога"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("ПОИСК ДУБЛИКАТОВ КОНТАКТОВ")
    print("=" * 70)

    # Проверяем зависимости
    if not FUZZYWUZZY_AVAILABLE:
        print("\n[!] ПРЕДУПРЕЖДЕНИЕ: fuzzywuzzy не установлен.")
        print("    Fuzzy matching имён будет ограничен.")
        print("    Установите: pip install fuzzywuzzy python-Levenshtein\n")

    if not PHONENUMBERS_AVAILABLE:
        print("\n[!] ПРЕДУПРЕЖДЕНИЕ: phonenumbers не установлен.")
        print("    Валидация телефонов будет ограничена.")
        print("    Установите: pip install phonenumbers\n")

    # Загрузка данных
    contacts_file = Path(args.contacts)
    messages_file = Path(args.messages)
    output_file = Path(args.output)

    print(f"\nФайл контактов: {contacts_file}")
    print(f"Файл сообщений: {messages_file}")
    print(f"Выходной файл: {output_file}")

    contacts = load_contacts(contacts_file)
    print(f"\nЗагружено контактов: {len(contacts)}")

    # Загружаем сообщения для анализа стиля
    messages_by_jid = {}
    if not args.skip_style_analysis and messages_file.exists():
        messages_by_jid = load_messages_by_jid(messages_file)

    # Фильтруем только персональные чаты (не группы)
    personal_contacts = [c for c in contacts if not c.get("is_group", False)]
    print(f"Персональных контактов: {len(personal_contacts)}")

    # Поиск дубликатов
    print("\n" + "=" * 70)
    print("ПОИСК ДУБЛИКАТОВ")
    print("=" * 70)

    finder = DuplicateFinder(personal_contacts, messages_by_jid)
    duplicate_groups = finder.find_duplicates(min_confidence=args.min_confidence)

    # Отчёт
    print("\n" + "=" * 70)
    report = generate_report(duplicate_groups)
    print(report)

    # Экспорт в JSON
    export_duplicates_json(duplicate_groups, output_file)

    # Автоматическое объединение
    if args.auto_merge is not None and duplicate_groups:
        print("\n" + "=" * 70)
        print("АВТОМАТИЧЕСКОЕ ОБЪЕДИНЕНИЕ")
        print("=" * 70)

        threshold = args.auto_merge
        groups_to_merge = [g for g in duplicate_groups if g["confidence"] >= threshold]

        print(f"Групп для объединения (confidence >= {threshold}): {len(groups_to_merge)}")

        if groups_to_merge:
            updated_contacts = contacts
            merge_history = []

            for group in groups_to_merge:
                updated_contacts, merge_info = apply_merge(updated_contacts, group)
                merge_history.append(merge_info)
                print(f"  Объединена группа: {group['primary_name']}")

            # Сохраняем объединённые контакты
            merged_output = {
                "contacts": updated_contacts,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_contacts": len(updated_contacts),
                    "merged_groups": len(groups_to_merge),
                    "merge_history": merge_history
                }
            }

            MERGED_CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(MERGED_CONTACTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(merged_output, f, ensure_ascii=False, indent=2)

            print(f"\nОбъединённые контакты сохранены: {MERGED_CONTACTS_FILE}")

    # Интерактивное объединение
    elif args.merge and duplicate_groups:
        print("\n" + "=" * 70)
        print("ИНТЕРАКТИВНОЕ ОБЪЕДИНЕНИЕ")
        print("=" * 70)

        updated_contacts = contacts
        merge_count = 0

        for group in duplicate_groups:
            print(f"\nГруппа: {group['primary_name']}")
            print(f"Уверенность: {group['confidence']:.0%}")
            print(f"Причины: {', '.join(group['reasons'])}")
            print("Контакты:")

            for contact in group["contacts"]:
                name = contact.get("name") or contact.get("display_name") or "N/A"
                phone = contact.get("phone", "N/A")
                msgs = contact.get("total_messages", 0)
                is_primary = "*" if contact.get("contact_id") == group["suggested_primary"] else " "
                print(f"  {is_primary} {name} | {phone} | {msgs} сообщ.")

            response = input("\nОбъединить? [y/n/q]: ").lower().strip()

            if response == 'q':
                print("Прервано пользователем.")
                break
            elif response == 'y':
                updated_contacts, merge_info = apply_merge(updated_contacts, group)
                merge_count += 1
                print(f"  Объединено. Конфликты: {merge_info.get('conflicts', {})}")

        if merge_count > 0:
            # Сохраняем результат
            merged_output = {
                "contacts": updated_contacts,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_contacts": len(updated_contacts),
                    "merged_groups": merge_count
                }
            }

            with open(MERGED_CONTACTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(merged_output, f, ensure_ascii=False, indent=2)

            print(f"\nОбъединено групп: {merge_count}")
            print(f"Сохранено: {MERGED_CONTACTS_FILE}")

    # Итоги
    print("\n" + "=" * 70)
    print("ИТОГИ")
    print("=" * 70)
    print(f"Найдено групп дубликатов: {len(duplicate_groups)}")
    print(f"Всего потенциальных дубликатов: {sum(len(g['contacts']) - 1 for g in duplicate_groups)}")
    print(f"Результат сохранён: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
