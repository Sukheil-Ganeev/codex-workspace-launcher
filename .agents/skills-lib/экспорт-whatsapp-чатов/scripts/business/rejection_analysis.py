#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ причин отказов клиентов в WhatsApp переписке.

Функции:
1. Детекция отказов по ключевым словам (RU/EN)
2. Категоризация причин:
   - Цена (price)
   - Конкуренты (competitor)
   - Timing (timing)
   - Качество/сервис (quality_service)
   - Личные обстоятельства (personal)
3. Статистика по причинам
4. Тренды отказов (по месяцам, дням недели, сезонам)
5. Сегментация (тип клиента, тип продукта/тура)
6. Рекомендации по улучшению
7. Экспорт: JSON, CSV

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/contacts.json (опционально)

Выходные файлы:
- D:/Downloads/Chats/_база/json/rejections.json
- D:/Downloads/Chats/_база/csv/rejections.csv
- D:/Downloads/Chats/_база/md/анализ_отказов.md
"""

import sys
import os
import re
import json
import csv
import uuid
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

MESSAGES_FILE = Path("D:/Downloads/Chats/_база/raw/all_messages.jsonl")
CONTACTS_FILE = Path("D:/Downloads/Chats/_база/json/contacts.json")

OUTPUT_JSON = Path("D:/Downloads/Chats/_база/json/rejections.json")
OUTPUT_CSV = Path("D:/Downloads/Chats/_база/csv/rejections.csv")
OUTPUT_MD = Path("D:/Downloads/Chats/_база/md/анализ_отказов.md")

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЕТЕКЦИИ ОТКАЗОВ
# ═══════════════════════════════════════════════════════════════

# Общие паттерны отказа (без категории)
REJECTION_PATTERNS = {
    "ru": [
        # Прямые отказы
        r"отказ(?:ываемся|ываюсь|ались)?",
        r"не\s+(?:будем|буду|поедем|пойдём|берём|берем|нужно|надо|хотим)",
        r"передумал[иа]?",
        r"отменя(?:ем|ю|йте)",
        r"отмена",
        r"отбой",
        r"не\s+актуально",
        r"не\s+интересно",
        r"(?:к\s+)?сожалению",
        r"(?:пока\s+)?(?:не\s+)?(?:будем|буду)\s+(?:брать|заказывать|бронировать)",
        r"(?:наверное|видимо|скорее\s+всего)\s+(?:не|нет)",
        r"решили\s+(?:не|отказаться)",
        r"воздержимся",
        r"пропустим",
        r"в\s+(?:этот|другой)\s+раз",
        r"не\s+(?:получится|выйдет|сложится)",
        r"планы\s+(?:изменились|поменялись)",
        r"обстоятельства\s+(?:изменились|поменялись)",
    ],
    "en": [
        # Direct rejections
        r"no\s+(?:thanks|thank\s+you)",
        r"(?:we|i)\s+(?:will\s+)?(?:pass|skip|decline)",
        r"(?:not|no\s+longer)\s+interested",
        r"changed?\s+(?:my|our)\s+mind",
        r"cancel(?:led|lation)?",
        r"(?:we|i)\s+(?:don'?t|won'?t)\s+(?:need|want|take)",
        r"(?:unfortunately|sorry)",
        r"(?:we|i)\s+(?:have\s+to\s+)?(?:refuse|reject|decline)",
        r"not\s+(?:going|gonna)\s+(?:to\s+)?(?:book|order|take)",
        r"plans?\s+changed",
        r"circumstances?\s+changed",
        r"(?:can'?t|cannot)\s+(?:make\s+it|do\s+it|proceed)",
        r"have\s+to\s+(?:cancel|pass)",
    ],
}

# ═══════════════════════════════════════════════════════════════
# КАТЕГОРИИ ПРИЧИН ОТКАЗА
# ═══════════════════════════════════════════════════════════════

REJECTION_CATEGORIES = {
    "price": {
        "name_ru": "Цена",
        "name_en": "Price",
        "patterns_ru": [
            r"дорого",
            r"дороговато",
            r"цена\s+(?:высокая|не\s+устраивает|большая|кусается)",
            r"(?:слишком|очень)\s+(?:дорого|много)",
            r"не\s+(?:по\s+карману|потянем|укладываемся)",
            r"(?:не\s+)?(?:в|вписывается\s+в)\s+бюджет",
            r"бюджет\s+(?:ограничен|маленький|не\s+позволяет)",
            r"(?:нашли|есть|видели)\s+(?:дешевле|выгоднее)",
            r"(?:за\s+такие|за\s+эти)\s+деньги",
            r"переплат[аы]",
            r"накрут(?:ка|или)",
            r"завышен(?:о|а|ы)",
            r"(?:можно|нельзя\s+ли)\s+(?:скидку|дешевле)",
            r"expensive",
        ],
        "patterns_en": [
            r"(?:too\s+)?expensive",
            r"(?:price|cost)\s+(?:is\s+)?(?:too\s+)?(?:high|much)",
            r"(?:over|out\s+of)\s+(?:our\s+)?budget",
            r"(?:can'?t|cannot)\s+afford",
            r"found\s+(?:it\s+)?cheaper",
            r"(?:better|lower)\s+price",
            r"(?:need|want)\s+(?:a\s+)?discount",
            r"pricey",
            r"overpriced",
            r"(?:not\s+)?worth\s+(?:the\s+)?(?:price|money)",
        ],
        "weight": 1.0,
    },
    "competitor": {
        "name_ru": "Конкуренты",
        "name_en": "Competitors",
        "patterns_ru": [
            r"(?:уже\s+)?(?:забронировал[иа]?|заказал[иа]?|нашли)\s+(?:в\s+)?(?:друг(?:ом|ой)|у\s+друг(?:их|ого))",
            r"(?:через|у)\s+друг(?:ое|ую|их|ого)\s+(?:агентств[оа]?|компани[юя]|туроператор[аы]?)",
            r"друг(?:ое|ая)\s+(?:предложение|компания|агентство)",
            r"(?:нам|нашли)\s+предложили\s+(?:лучше|дешевле|выгоднее)",
            r"(?:взяли|берём|возьмём)\s+(?:у|в|через)\s+друг",
            r"(?:обратились|пошли|идём)\s+(?:к|в)\s+друг",
            r"(?:знакомые|друзья)\s+(?:порекомендовали|посоветовали|предложили)",
            r"(?:лучше|выгоднее)\s+(?:условия|предложение|цена)\s+(?:в|у)\s+друг",
        ],
        "patterns_en": [
            r"(?:already\s+)?(?:booked|ordered|found)\s+(?:with|from|through)\s+(?:another|other|different)",
            r"(?:going\s+)?(?:with|to)\s+(?:another|different)\s+(?:company|agency|provider)",
            r"(?:better|cheaper)\s+(?:offer|deal|price)\s+(?:from|with)\s+(?:another|other)",
            r"(?:found|got)\s+(?:a\s+)?(?:better|cheaper)\s+(?:option|alternative)",
            r"(?:friend|colleague)\s+(?:recommended|suggested)\s+(?:another|different)",
            r"(?:switching|moved)\s+to\s+(?:another|different)",
        ],
        "weight": 1.0,
    },
    "timing": {
        "name_ru": "Время/даты",
        "name_en": "Timing",
        "patterns_ru": [
            r"(?:не\s+)?(?:подходит|устраивает)\s+(?:дата|время|день|число)",
            r"(?:в\s+)?(?:эт[иу]|другой|эту)\s+дат[уы]?\s+(?:не\s+)?(?:можем|получится)",
            r"(?:нужно|надо)\s+(?:перенести|сдвинуть|изменить)\s+(?:дату|время)",
            r"(?:изменились|поменялись)\s+(?:даты|планы|время)",
            r"(?:не\s+)?(?:успеваем|успеем|успею)",
            r"(?:слишком\s+)?(?:рано|поздно|далеко)",
            r"(?:нет\s+)?(?:свободного\s+)?времени",
            r"(?:занят[ыа]?|заняты)",
            r"(?:в\s+)?(?:другой|следующий)\s+раз",
            r"(?:позже|потом|после)",
            r"(?:отложить|перенести)\s+(?:на\s+)?(?:потом|позже)",
            r"(?:сейчас|пока)\s+(?:не\s+)?(?:можем|получается|выходит)",
            r"(?:рейс|самолёт|вылет)\s+(?:изменился|отменён|перенесён)",
            r"(?:не\s+)?(?:совпадает|попадает)\s+(?:по\s+)?(?:датам|времени)",
        ],
        "patterns_en": [
            r"(?:date|time|day)\s+(?:doesn'?t|does\s+not)\s+(?:work|suit|fit)",
            r"(?:can'?t|cannot)\s+(?:make\s+it|do\s+it)\s+(?:on|at)\s+(?:that|this)",
            r"(?:need\s+to\s+)?(?:reschedule|postpone|change)\s+(?:the\s+)?(?:date|time)",
            r"(?:dates?|plans?|schedule)\s+(?:changed|conflict)",
            r"(?:no|not\s+enough)\s+time",
            r"(?:too\s+)?(?:busy|occupied)",
            r"(?:maybe\s+)?(?:later|next\s+time|another\s+time)",
            r"(?:postpone|delay|put\s+off)",
            r"(?:flight|plane)\s+(?:changed|cancelled|delayed)",
            r"(?:schedule|timing)\s+(?:conflict|issue|problem)",
        ],
        "weight": 0.9,
    },
    "quality_service": {
        "name_ru": "Качество/сервис",
        "name_en": "Quality/Service",
        "patterns_ru": [
            r"(?:плохие|негативные)\s+(?:отзывы|рейтинг|рекомендации)",
            r"(?:не\s+)?(?:доверяю|доверяем|верю|верим)",
            r"(?:сомневаюсь|сомневаемся)",
            r"(?:не\s+)?(?:уверен[аы]?|убеждён[аы]?)",
            r"(?:слышали?|читали?)\s+(?:что|о)\s+(?:плохо|негатив)",
            r"(?:не\s+)?(?:понравил(?:ось|ся|ась)|устроил[оа]?)\s+(?:сервис|обслуживание|качество)",
            r"(?:прошлый\s+)?(?:опыт|раз)\s+(?:был|оказался)\s+(?:плохой|негативный|неудачный)",
            r"(?:были?\s+)?(?:проблемы|накладки|ошибки)",
            r"(?:не\s+)?(?:оправдали|оправдывает)\s+(?:ожидания|надежды)",
            r"(?:разочарован[ыа]?|недовольн[ыа]?)",
            r"(?:качество|сервис|обслуживание)\s+(?:не\s+)?(?:устраивает|подходит)",
        ],
        "patterns_en": [
            r"(?:bad|negative|poor)\s+(?:reviews?|ratings?|feedback)",
            r"(?:don'?t|do\s+not)\s+(?:trust|believe)",
            r"(?:not\s+)?(?:sure|confident|convinced)",
            r"(?:heard|read)\s+(?:bad|negative)\s+(?:things?|reviews?)",
            r"(?:didn'?t|did\s+not)\s+(?:like|enjoy)\s+(?:the\s+)?(?:service|quality)",
            r"(?:previous|last)\s+(?:experience|time)\s+(?:was\s+)?(?:bad|poor|negative)",
            r"(?:had\s+)?(?:problems?|issues?|troubles?)",
            r"(?:didn'?t|did\s+not)\s+(?:meet|match)\s+(?:expectations?)",
            r"(?:disappointed|unsatisfied|unhappy)",
            r"(?:quality|service)\s+(?:issues?|problems?|concerns?)",
        ],
        "weight": 0.95,
    },
    "personal": {
        "name_ru": "Личные обстоятельства",
        "name_en": "Personal circumstances",
        "patterns_ru": [
            r"(?:заболел[иа]?|болеем|болею|болезнь)",
            r"(?:семейные|личные)\s+(?:обстоятельства|причины|дела)",
            r"(?:срочные|неотложные)\s+дела",
            r"(?:работа|командировка|проект)",
            r"(?:не\s+)?(?:отпустили|могу\s+уйти)\s+(?:с\s+)?работы",
            r"(?:виза|документы)\s+(?:не\s+)?(?:готов[аы]?|получили)",
            r"(?:проблемы|сложности)\s+(?:с\s+)?(?:визой|документами|паспортом)",
            r"(?:дети|ребёнок|семья)",
            r"(?:форс-мажор|непредвиденн[ыеое])",
            r"(?:по\s+)?(?:личным|семейным)\s+(?:причинам|обстоятельствам)",
            r"(?:муж|жена|родители|родственники)\s+(?:не\s+)?(?:может|могут|хотят)",
            r"(?:изменились|поменялись)\s+(?:планы|обстоятельства)",
            r"(?:финансовые|денежные)\s+(?:проблемы|трудности|сложности)",
        ],
        "patterns_en": [
            r"(?:got\s+)?(?:sick|ill|unwell)",
            r"(?:family|personal)\s+(?:circumstances?|reasons?|matters?|issues?)",
            r"(?:urgent|emergency)\s+(?:matters?|business|work)",
            r"(?:work|business\s+trip|project)",
            r"(?:can'?t\s+)?(?:get\s+)?(?:time\s+)?off\s+(?:work)?",
            r"(?:visa|documents?)\s+(?:not\s+)?(?:ready|approved|issued)",
            r"(?:problems?|issues?)\s+(?:with\s+)?(?:visa|documents?|passport)",
            r"(?:kids?|children|family)",
            r"(?:force\s+majeure|unforeseen|unexpected)",
            r"(?:for\s+)?(?:personal|family)\s+(?:reasons?)",
            r"(?:husband|wife|parents?|relatives?)\s+(?:can'?t|don'?t\s+want)",
            r"(?:plans?|circumstances?)\s+(?:changed|different)",
            r"(?:financial|money)\s+(?:problems?|difficulties?|issues?)",
        ],
        "weight": 0.85,
    },
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ПРОДУКТОВ
# ═══════════════════════════════════════════════════════════════

PRODUCT_PATTERNS = {
    "tour_abu_dhabi": {
        "name": "Экскурсия в Абу-Даби",
        "patterns": [r"абу[\s\-]?даби", r"abu[\s\-]?dhabi", r"grand\s+mosque", r"мечеть\s+шейха"],
    },
    "tour_dubai": {
        "name": "Экскурсия в Дубай",
        "patterns": [r"дубай", r"dubai", r"бурдж[\s\-]?халифа", r"burj", r"обзорн(?:ая|ый)"],
    },
    "safari": {
        "name": "Сафари",
        "patterns": [r"сафари", r"safari", r"пустын[яе]", r"desert", r"джип"],
    },
    "yacht": {
        "name": "Яхта/катер",
        "patterns": [r"яхт[аыу]", r"yacht", r"катер", r"лодк[аи]", r"морск(?:ая|ой)"],
    },
    "transfer": {
        "name": "Трансфер",
        "patterns": [r"трансфер", r"transfer", r"аэропорт", r"airport", r"встреча", r"проводы"],
    },
    "tickets": {
        "name": "Билеты/парки",
        "patterns": [r"билет", r"ticket", r"ferrari", r"феррари", r"aquaventure", r"аквапарк", r"парк"],
    },
    "restaurant": {
        "name": "Рестораны",
        "patterns": [r"ресторан", r"restaurant", r"ужин", r"dinner", r"обед", r"lunch", r"бранч", r"brunch"],
    },
    "car_rental": {
        "name": "Аренда авто",
        "patterns": [r"аренд[аы]\s+(?:авто|машин)", r"car\s+rental", r"прокат", r"rent\s+a\s+car"],
    },
    "visa": {
        "name": "Виза",
        "patterns": [r"виз[аыу]", r"visa"],
    },
    "hotel": {
        "name": "Отель",
        "patterns": [r"отел[ья]", r"hotel", r"гостиниц[аы]", r"номер", r"room"],
    },
}

# ═══════════════════════════════════════════════════════════════
# SEVERITY ПАТТЕРНЫ
# ═══════════════════════════════════════════════════════════════

SEVERITY_INDICATORS = {
    "high": {
        "patterns_ru": [
            r"категорически",
            r"точно\s+(?:не|нет)",
            r"однозначно\s+(?:не|нет)",
            r"никогда",
            r"ни\s+за\s+что",
            r"больше\s+(?:не|никогда)",
            r"забудьте",
            r"не\s+(?:пишите|звоните|беспокойте)",
        ],
        "patterns_en": [
            r"absolutely\s+(?:not|no)",
            r"definitely\s+(?:not|no)",
            r"never",
            r"no\s+way",
            r"forget\s+(?:it|about)",
            r"stop\s+(?:contacting|messaging|calling)",
        ],
    },
    "low": {
        "patterns_ru": [
            r"может\s+быть\s+(?:позже|потом)",
            r"(?:пока|на\s+данный\s+момент)\s+(?:не|нет)",
            r"возможно\s+(?:позже|в\s+другой\s+раз)",
            r"подумаем",
            r"(?:ещё|еще)\s+(?:не\s+)?решили",
            r"не\s+уверен[ыа]?",
        ],
        "patterns_en": [
            r"maybe\s+(?:later|next\s+time)",
            r"(?:for\s+)?now\s+(?:not|no)",
            r"perhaps\s+(?:later|another\s+time)",
            r"(?:we'?ll|will)\s+think\s+(?:about\s+it)?",
            r"(?:haven'?t|not)\s+decided\s+yet",
            r"not\s+sure",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════
# ТИПЫ КЛИЕНТОВ
# ═══════════════════════════════════════════════════════════════

CLIENT_TYPE_PATTERNS = {
    "b2b": {
        "name": "B2B (агенты)",
        "patterns": [
            r"агент", r"agent", r"партнёр", r"partner",
            r"туроператор", r"tour\s+operator",
            r"компания", r"company", r"фирма",
            r"корпоратив", r"corporate",
            r"для\s+клиент(?:а|ов)",
        ],
    },
    "b2c": {
        "name": "B2C (конечные клиенты)",
        "patterns": [
            r"(?:мы|я)\s+(?:с\s+)?(?:семьёй|женой|мужем|детьми|друзьями)",
            r"(?:для\s+)?(?:себя|нас)",
            r"(?:в\s+)?(?:отпуск|отпуске|путешестви)",
            r"(?:на\s+)?(?:медовый\s+месяц|свадебное)",
            r"(?:день|юбилей|праздник)",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_messages_jsonl(filepath: Path) -> List[Dict]:
    """Загружает сообщения из JSONL файла."""
    messages = []

    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
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
                    if line_num <= 10:  # Показываем только первые ошибки
                        print(f"  Ошибка JSON в строке {line_num}: {e}")
    except Exception as e:
        print(f"[!] Ошибка чтения файла: {e}")

    return messages


def load_contacts(filepath: Path) -> Dict[str, Dict]:
    """Загружает контакты из JSON файла."""
    contacts = {}

    if not filepath.exists():
        print(f"[i] Файл контактов не найден: {filepath}")
        return contacts

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Поддержка разных форматов
        if isinstance(data, list):
            for c in data:
                contact_id = c.get("jid") or c.get("phone") or c.get("id")
                if contact_id:
                    contacts[contact_id] = c
        elif isinstance(data, dict):
            if "contacts" in data:
                for c in data["contacts"]:
                    contact_id = c.get("jid") or c.get("phone") or c.get("id")
                    if contact_id:
                        contacts[contact_id] = c
            else:
                contacts = data
    except Exception as e:
        print(f"[!] Ошибка загрузки контактов: {e}")

    return contacts


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ДЕТЕКЦИИ
# ═══════════════════════════════════════════════════════════════

def is_rejection_message(text: str) -> bool:
    """Проверяет, является ли сообщение отказом."""
    text_lower = text.lower()

    # Проверяем русские паттерны
    for pattern in REJECTION_PATTERNS["ru"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True

    # Проверяем английские паттерны
    for pattern in REJECTION_PATTERNS["en"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True

    return False


def detect_rejection_category(text: str) -> Tuple[Optional[str], float, List[str]]:
    """
    Определяет категорию причины отказа.

    Returns:
        (category, confidence, matched_keywords)
    """
    text_lower = text.lower()

    category_scores = defaultdict(float)
    category_keywords = defaultdict(list)

    for category, config in REJECTION_CATEGORIES.items():
        weight = config.get("weight", 1.0)

        # Проверяем русские паттерны
        for pattern in config.get("patterns_ru", []):
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                category_scores[category] += weight
                category_keywords[category].append(match.group())

        # Проверяем английские паттерны
        for pattern in config.get("patterns_en", []):
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                category_scores[category] += weight
                category_keywords[category].append(match.group())

    if not category_scores:
        return None, 0.0, []

    # Находим категорию с максимальным score
    best_category = max(category_scores, key=category_scores.get)
    max_score = category_scores[best_category]

    # Нормализуем confidence (0-1)
    confidence = min(max_score / 3.0, 1.0)

    return best_category, confidence, category_keywords[best_category]


def detect_severity(text: str) -> str:
    """Определяет серьёзность/окончательность отказа."""
    text_lower = text.lower()

    # Проверяем high severity
    for pattern in SEVERITY_INDICATORS["high"]["patterns_ru"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "high"
    for pattern in SEVERITY_INDICATORS["high"]["patterns_en"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "high"

    # Проверяем low severity
    for pattern in SEVERITY_INDICATORS["low"]["patterns_ru"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "low"
    for pattern in SEVERITY_INDICATORS["low"]["patterns_en"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "low"

    return "medium"


def detect_product(text: str, context: str = "") -> Optional[str]:
    """Определяет продукт по тексту."""
    full_text = f"{context} {text}".lower()

    for product_id, config in PRODUCT_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, full_text, re.IGNORECASE):
                return product_id

    return None


def detect_client_type(text: str, contact_info: Optional[Dict] = None) -> str:
    """Определяет тип клиента (B2B/B2C)."""
    # Сначала проверяем контакт
    if contact_info:
        contact_type = contact_info.get("type", "").lower()
        if contact_type in ["агенты", "agents", "partners", "партнёры", "b2b"]:
            return "b2b"
        if contact_type in ["клиенты", "clients", "customers", "b2c"]:
            return "b2c"

    text_lower = text.lower()

    # B2B паттерны
    for pattern in CLIENT_TYPE_PATTERNS["b2b"]["patterns"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "b2b"

    # B2C паттерны
    for pattern in CLIENT_TYPE_PATTERNS["b2c"]["patterns"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "b2c"

    return "unknown"


def get_context(messages: List[Dict], idx: int, window: int = 3) -> str:
    """Получает контекст (соседние сообщения)."""
    context_parts = []

    # Сообщения до
    for i in range(max(0, idx - window), idx):
        if "text" in messages[i]:
            context_parts.append(messages[i].get("text", ""))

    # Сообщения после
    for i in range(idx + 1, min(len(messages), idx + window + 1)):
        if "text" in messages[i]:
            context_parts.append(messages[i].get("text", ""))

    return " ".join(context_parts)


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Парсит дату из различных форматов."""
    if not dt_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str[:len(fmt.replace('%', '').replace('-', '').replace(':', '').replace(' ', '').replace('.', '').replace('/', '').replace('T', '')) + dt_str.count('-') + dt_str.count(':') + dt_str.count(' ') + dt_str.count('.') + dt_str.count('/') + dt_str.count('T')], fmt)
        except ValueError:
            continue

    # Пробуем более гибкий подход
    try:
        # ISO format
        if 'T' in dt_str:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00').split('+')[0])
        # Простой формат
        parts = dt_str.split()
        if len(parts) >= 1:
            date_part = parts[0]
            if '.' in date_part:
                d, m, y = date_part.split('.')
                return datetime(int(y), int(m), int(d))
            elif '-' in date_part:
                y, m, d = date_part.split('-')
                return datetime(int(y), int(m), int(d))
    except:
        pass

    return None


# ═══════════════════════════════════════════════════════════════
# ОСНОВНАЯ ФУНКЦИЯ АНАЛИЗА
# ═══════════════════════════════════════════════════════════════

def analyze_rejections(
    messages: List[Dict],
    contacts: Dict[str, Dict]
) -> Dict[str, Any]:
    """
    Анализирует отказы в сообщениях.

    Returns:
        Словарь с результатами анализа
    """
    rejections = []
    stats = {
        "total_messages": len(messages),
        "total_rejections": 0,
        "by_category": defaultdict(int),
        "by_severity": defaultdict(int),
        "by_product": defaultdict(int),
        "by_client_type": defaultdict(int),
        "by_month": defaultdict(int),
        "by_weekday": defaultdict(int),
        "by_season": defaultdict(int),
        "category_by_product": defaultdict(lambda: defaultdict(int)),
        "category_by_client_type": defaultdict(lambda: defaultdict(int)),
    }

    # Для тренд-анализа
    monthly_rejections = defaultdict(list)

    print(f"[i] Анализ {len(messages)} сообщений...")

    for idx, msg in enumerate(messages):
        text = msg.get("text", "")
        if not text or len(text) < 5:
            continue

        # Проверяем, является ли сообщение отказом
        if not is_rejection_message(text):
            continue

        # Получаем контекст
        context = get_context(messages, idx)

        # Определяем категорию
        category, confidence, keywords = detect_rejection_category(text)
        if not category:
            category = "other"
            confidence = 0.3
            keywords = []

        # Определяем severity
        severity = detect_severity(text)

        # Определяем продукт
        product = detect_product(text, context)

        # Информация о контакте
        contact_id = msg.get("contact_id") or msg.get("jid") or msg.get("sender_jid", "")
        contact_info = contacts.get(contact_id, {})

        # Определяем тип клиента
        client_type = detect_client_type(text, contact_info)

        # Парсим дату
        dt_str = msg.get("datetime") or msg.get("timestamp") or msg.get("date", "")
        dt = parse_datetime(dt_str)

        # Формируем запись
        rejection = {
            "rejection_id": str(uuid.uuid4()),
            "message_id": msg.get("message_id", ""),
            "contact_id": contact_id,
            "contact_name": contact_info.get("name") or msg.get("sender_name") or msg.get("sender", ""),
            "datetime": dt_str,
            "date": dt.strftime("%Y-%m-%d") if dt else "",
            "month": dt.strftime("%Y-%m") if dt else "",
            "weekday": dt.strftime("%A") if dt else "",
            "weekday_num": dt.weekday() if dt else -1,
            "text": text[:500],
            "category": category,
            "category_name_ru": REJECTION_CATEGORIES.get(category, {}).get("name_ru", category),
            "confidence": round(confidence, 3),
            "keywords": keywords[:5],
            "severity": severity,
            "product": product,
            "product_name": PRODUCT_PATTERNS.get(product, {}).get("name", "") if product else "",
            "client_type": client_type,
            "source_file": msg.get("source_file", ""),
        }

        rejections.append(rejection)

        # Обновляем статистику
        stats["total_rejections"] += 1
        stats["by_category"][category] += 1
        stats["by_severity"][severity] += 1

        if product:
            stats["by_product"][product] += 1
            stats["category_by_product"][product][category] += 1

        stats["by_client_type"][client_type] += 1
        stats["category_by_client_type"][client_type][category] += 1

        if dt:
            month_key = dt.strftime("%Y-%m")
            stats["by_month"][month_key] += 1
            monthly_rejections[month_key].append(rejection)

            # День недели
            stats["by_weekday"][dt.strftime("%A")] += 1

            # Сезон
            month = dt.month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "autumn"
            stats["by_season"][season] += 1

    print(f"[+] Найдено {stats['total_rejections']} отказов")

    # Преобразуем defaultdict в обычные dict
    stats["by_category"] = dict(stats["by_category"])
    stats["by_severity"] = dict(stats["by_severity"])
    stats["by_product"] = dict(stats["by_product"])
    stats["by_client_type"] = dict(stats["by_client_type"])
    stats["by_month"] = dict(sorted(stats["by_month"].items()))
    stats["by_weekday"] = dict(stats["by_weekday"])
    stats["by_season"] = dict(stats["by_season"])
    stats["category_by_product"] = {k: dict(v) for k, v in stats["category_by_product"].items()}
    stats["category_by_client_type"] = {k: dict(v) for k, v in stats["category_by_client_type"].items()}

    # Вычисляем тренды
    trends = calculate_trends(stats, monthly_rejections)

    # Генерируем рекомендации
    recommendations = generate_recommendations(stats, trends)

    return {
        "rejections": rejections,
        "statistics": stats,
        "trends": trends,
        "recommendations": recommendations,
        "metadata": {
            "analyzed_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "total_rejections": stats["total_rejections"],
            "rejection_rate": round(stats["total_rejections"] / len(messages) * 100, 2) if messages else 0,
            "version": "1.0.0",
        }
    }


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ТРЕНДОВ
# ═══════════════════════════════════════════════════════════════

def calculate_trends(stats: Dict, monthly_rejections: Dict) -> Dict:
    """Вычисляет тренды отказов."""
    trends = {
        "monthly_trend": [],
        "category_trend": {},
        "growing_categories": [],
        "declining_categories": [],
        "peak_months": [],
        "peak_weekdays": [],
        "seasonal_pattern": {},
    }

    # Месячный тренд
    sorted_months = sorted(stats["by_month"].items())
    if len(sorted_months) >= 2:
        for i, (month, count) in enumerate(sorted_months):
            prev_count = sorted_months[i-1][1] if i > 0 else count
            change = count - prev_count
            change_pct = (change / prev_count * 100) if prev_count > 0 else 0

            trends["monthly_trend"].append({
                "month": month,
                "count": count,
                "change": change,
                "change_pct": round(change_pct, 1),
            })

        # Определяем общий тренд
        first_half = sum(m["count"] for m in trends["monthly_trend"][:len(trends["monthly_trend"])//2])
        second_half = sum(m["count"] for m in trends["monthly_trend"][len(trends["monthly_trend"])//2:])

        if second_half > first_half * 1.1:
            trends["overall_trend"] = "growing"
        elif second_half < first_half * 0.9:
            trends["overall_trend"] = "declining"
        else:
            trends["overall_trend"] = "stable"

    # Пиковые месяцы
    if stats["by_month"]:
        avg_monthly = sum(stats["by_month"].values()) / len(stats["by_month"])
        for month, count in stats["by_month"].items():
            if count > avg_monthly * 1.5:
                trends["peak_months"].append({"month": month, "count": count})

    # Пиковые дни недели
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if stats["by_weekday"]:
        avg_weekday = sum(stats["by_weekday"].values()) / len(stats["by_weekday"])
        for weekday in weekday_order:
            count = stats["by_weekday"].get(weekday, 0)
            if count > avg_weekday * 1.3:
                trends["peak_weekdays"].append({"weekday": weekday, "count": count})

    # Сезонный паттерн
    season_names = {
        "winter": "Зима (дек-фев)",
        "spring": "Весна (мар-май)",
        "summer": "Лето (июн-авг)",
        "autumn": "Осень (сен-ноя)",
    }

    if stats["by_season"]:
        total_seasonal = sum(stats["by_season"].values())
        for season, count in stats["by_season"].items():
            trends["seasonal_pattern"][season] = {
                "name": season_names.get(season, season),
                "count": count,
                "percentage": round(count / total_seasonal * 100, 1) if total_seasonal > 0 else 0,
            }

    return trends


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ РЕКОМЕНДАЦИЙ
# ═══════════════════════════════════════════════════════════════

def generate_recommendations(stats: Dict, trends: Dict) -> List[Dict]:
    """Генерирует рекомендации по улучшению."""
    recommendations = []
    total_rejections = stats.get("total_rejections", 0)

    if total_rejections == 0:
        return recommendations

    # Анализ по категориям
    by_category = stats.get("by_category", {})

    # 1. Рекомендации по цене
    price_count = by_category.get("price", 0)
    price_pct = price_count / total_rejections * 100 if total_rejections else 0

    if price_pct > 30:
        recommendations.append({
            "category": "price",
            "priority": "high",
            "issue": f"Высокий процент отказов из-за цены ({price_pct:.0f}%)",
            "recommendations": [
                "Пересмотреть ценовую политику",
                "Внедрить гибкую систему скидок",
                "Предлагать бюджетные альтернативы",
                "Добавить опцию рассрочки/частичной оплаты",
                "Создать пакетные предложения с лучшим соотношением цена/качество",
            ],
        })
    elif price_pct > 15:
        recommendations.append({
            "category": "price",
            "priority": "medium",
            "issue": f"Заметный процент отказов из-за цены ({price_pct:.0f}%)",
            "recommendations": [
                "Рассмотреть сезонные скидки",
                "Предлагать ранее бронирование со скидкой",
                "Подготовить обоснование ценности услуг",
            ],
        })

    # 2. Рекомендации по конкурентам
    competitor_count = by_category.get("competitor", 0)
    competitor_pct = competitor_count / total_rejections * 100 if total_rejections else 0

    if competitor_pct > 20:
        recommendations.append({
            "category": "competitor",
            "priority": "high",
            "issue": f"Высокий процент потерь в пользу конкурентов ({competitor_pct:.0f}%)",
            "recommendations": [
                "Провести анализ конкурентных предложений",
                "Усилить уникальное торговое предложение (УТП)",
                "Улучшить скорость ответа на запросы",
                "Внедрить программу лояльности",
                "Рассмотреть партнёрские программы с агентами",
            ],
        })
    elif competitor_pct > 10:
        recommendations.append({
            "category": "competitor",
            "priority": "medium",
            "issue": f"Заметный процент потерь в пользу конкурентов ({competitor_pct:.0f}%)",
            "recommendations": [
                "Мониторить предложения конкурентов",
                "Подчёркивать преимущества в коммуникации",
            ],
        })

    # 3. Рекомендации по timing
    timing_count = by_category.get("timing", 0)
    timing_pct = timing_count / total_rejections * 100 if total_rejections else 0

    if timing_pct > 25:
        recommendations.append({
            "category": "timing",
            "priority": "medium",
            "issue": f"Высокий процент отказов из-за неудобного времени ({timing_pct:.0f}%)",
            "recommendations": [
                "Предлагать больше дат и временных слотов",
                "Внедрить гибкую политику переноса",
                "Добавить возможность бесплатной отмены/переноса",
                "Напоминать о бронировании заблаговременно",
            ],
        })

    # 4. Рекомендации по качеству/сервису
    quality_count = by_category.get("quality_service", 0)
    quality_pct = quality_count / total_rejections * 100 if total_rejections else 0

    if quality_pct > 15:
        recommendations.append({
            "category": "quality_service",
            "priority": "high",
            "issue": f"Проблемы с восприятием качества/сервиса ({quality_pct:.0f}%)",
            "recommendations": [
                "Собирать и публиковать положительные отзывы",
                "Улучшить обучение персонала",
                "Внедрить контроль качества",
                "Оперативно реагировать на жалобы",
                "Предлагать гарантии возврата",
            ],
        })

    # 5. Рекомендации по продуктам
    by_product = stats.get("by_product", {})
    if by_product:
        total_product_rejections = sum(by_product.values())
        for product, count in sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:3]:
            pct = count / total_product_rejections * 100
            if pct > 30:
                product_name = PRODUCT_PATTERNS.get(product, {}).get("name", product)
                recommendations.append({
                    "category": "product",
                    "priority": "medium",
                    "issue": f"Много отказов по продукту '{product_name}' ({pct:.0f}%)",
                    "recommendations": [
                        f"Пересмотреть предложение по '{product_name}'",
                        "Изучить причины отказов по этому продукту",
                        "Рассмотреть альтернативные варианты",
                    ],
                })

    # 6. Рекомендации по B2B/B2C
    by_client_type = stats.get("by_client_type", {})
    b2b_count = by_client_type.get("b2b", 0)
    b2c_count = by_client_type.get("b2c", 0)

    if b2b_count > b2c_count * 2:
        recommendations.append({
            "category": "client_type",
            "priority": "medium",
            "issue": "Больше отказов от B2B партнёров",
            "recommendations": [
                "Пересмотреть агентские комиссии",
                "Улучшить условия для партнёров",
                "Ускорить обработку агентских запросов",
            ],
        })

    # 7. Сезонные рекомендации
    seasonal = trends.get("seasonal_pattern", {})
    if seasonal:
        max_season = max(seasonal.items(), key=lambda x: x[1].get("count", 0))[0]
        if seasonal[max_season].get("percentage", 0) > 40:
            season_name = seasonal[max_season].get("name", max_season)
            recommendations.append({
                "category": "seasonal",
                "priority": "low",
                "issue": f"Пиковый сезон отказов: {season_name}",
                "recommendations": [
                    f"Подготовить специальные предложения для {season_name}",
                    "Увеличить маркетинговую активность в пиковый период",
                ],
            })

    # Сортируем по приоритету
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations


# ═══════════════════════════════════════════════════════════════
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════════════════════════════

def save_json(data: Dict, filepath: Path):
    """Сохраняет данные в JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[+] JSON сохранён: {filepath}")


def save_csv(rejections: List[Dict], filepath: Path):
    """Сохраняет отказы в CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if not rejections:
        print(f"[i] Нет данных для CSV")
        return

    # Определяем колонки
    columns = [
        "rejection_id",
        "datetime",
        "date",
        "month",
        "weekday",
        "contact_id",
        "contact_name",
        "category",
        "category_name_ru",
        "confidence",
        "severity",
        "product",
        "product_name",
        "client_type",
        "keywords",
        "text",
    ]

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()

        for rejection in rejections:
            row = rejection.copy()
            # Преобразуем списки в строки
            if isinstance(row.get("keywords"), list):
                row["keywords"] = ", ".join(row["keywords"])
            writer.writerow(row)

    print(f"[+] CSV сохранён: {filepath}")


def save_markdown(data: Dict, filepath: Path):
    """Сохраняет отчёт в Markdown."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    stats = data.get("statistics", {})
    trends = data.get("trends", {})
    recommendations = data.get("recommendations", [])
    metadata = data.get("metadata", {})

    lines = []
    lines.append("# Анализ причин отказов")
    lines.append("")
    lines.append(f"*Дата анализа: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Общая статистика
    lines.append("## Общая статистика")
    lines.append("")
    lines.append(f"- **Всего проанализировано сообщений:** {metadata.get('total_messages', 0):,}")
    lines.append(f"- **Выявлено отказов:** {metadata.get('total_rejections', 0):,}")
    lines.append(f"- **Процент отказов:** {metadata.get('rejection_rate', 0):.2f}%")
    lines.append("")

    # По категориям
    lines.append("## Причины отказов")
    lines.append("")
    lines.append("| Категория | Количество | % |")
    lines.append("|-----------|------------|---|")

    total = stats.get("total_rejections", 1)
    category_names = {
        "price": "Цена",
        "competitor": "Конкуренты",
        "timing": "Время/даты",
        "quality_service": "Качество/сервис",
        "personal": "Личные обстоятельства",
        "other": "Другое",
    }

    for category, count in sorted(stats.get("by_category", {}).items(), key=lambda x: x[1], reverse=True):
        name = category_names.get(category, category)
        pct = count / total * 100
        lines.append(f"| {name} | {count} | {pct:.1f}% |")
    lines.append("")

    # Визуализация
    lines.append("### Диаграмма причин")
    lines.append("")
    lines.append("```")
    max_count = max(stats.get("by_category", {}).values()) if stats.get("by_category") else 1
    for category, count in sorted(stats.get("by_category", {}).items(), key=lambda x: x[1], reverse=True):
        name = category_names.get(category, category)
        bar_len = int((count / max_count) * 30)
        bar = "#" * bar_len
        lines.append(f"{name:20} {bar:<30} {count:>4}")
    lines.append("```")
    lines.append("")

    # По серьёзности
    lines.append("## По серьёзности отказа")
    lines.append("")
    severity_names = {"high": "Окончательный", "medium": "Средний", "low": "Мягкий (возможно вернётся)"}
    for severity, count in sorted(stats.get("by_severity", {}).items(), key=lambda x: (0 if x[0]=="high" else 1 if x[0]=="medium" else 2)):
        name = severity_names.get(severity, severity)
        pct = count / total * 100
        lines.append(f"- **{name}:** {count} ({pct:.1f}%)")
    lines.append("")

    # По продуктам
    if stats.get("by_product"):
        lines.append("## По продуктам")
        lines.append("")
        lines.append("| Продукт | Отказов | % |")
        lines.append("|---------|---------|---|")

        total_product = sum(stats["by_product"].values())
        for product, count in sorted(stats["by_product"].items(), key=lambda x: x[1], reverse=True):
            name = PRODUCT_PATTERNS.get(product, {}).get("name", product)
            pct = count / total_product * 100
            lines.append(f"| {name} | {count} | {pct:.1f}% |")
        lines.append("")

    # По типу клиента
    if stats.get("by_client_type"):
        lines.append("## По типу клиента")
        lines.append("")
        client_names = {"b2b": "B2B (агенты/партнёры)", "b2c": "B2C (конечные клиенты)", "unknown": "Не определено"}
        for client_type, count in stats["by_client_type"].items():
            name = client_names.get(client_type, client_type)
            pct = count / total * 100
            lines.append(f"- **{name}:** {count} ({pct:.1f}%)")
        lines.append("")

    # Тренды
    lines.append("## Тренды")
    lines.append("")

    # Общий тренд
    overall_trend = trends.get("overall_trend", "stable")
    trend_text = {
        "growing": "Рост количества отказов",
        "declining": "Снижение количества отказов",
        "stable": "Стабильная динамика",
    }
    lines.append(f"**Общий тренд:** {trend_text.get(overall_trend, overall_trend)}")
    lines.append("")

    # По месяцам
    if stats.get("by_month"):
        lines.append("### По месяцам")
        lines.append("")
        lines.append("```")
        lines.append("Месяц     Отказов  Изменение")
        lines.append("-" * 35)

        for item in trends.get("monthly_trend", [])[-12:]:
            change_str = f"{item['change']:+d}" if item['change'] != 0 else " 0"
            lines.append(f"{item['month']}    {item['count']:>5}    {change_str:>+5} ({item['change_pct']:+.0f}%)")
        lines.append("```")
        lines.append("")

    # Пиковые периоды
    if trends.get("peak_months"):
        lines.append("### Пиковые месяцы")
        lines.append("")
        for peak in trends["peak_months"]:
            lines.append(f"- {peak['month']}: {peak['count']} отказов")
        lines.append("")

    # По дням недели
    if stats.get("by_weekday"):
        lines.append("### По дням недели")
        lines.append("")
        weekday_ru = {
            "Monday": "Понедельник",
            "Tuesday": "Вторник",
            "Wednesday": "Среда",
            "Thursday": "Четверг",
            "Friday": "Пятница",
            "Saturday": "Суббота",
            "Sunday": "Воскресенье",
        }
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for weekday in weekday_order:
            count = stats["by_weekday"].get(weekday, 0)
            name = weekday_ru.get(weekday, weekday)
            lines.append(f"- {name}: {count}")
        lines.append("")

    # Сезонность
    if trends.get("seasonal_pattern"):
        lines.append("### Сезонность")
        lines.append("")
        for season, data in trends["seasonal_pattern"].items():
            lines.append(f"- **{data['name']}:** {data['count']} ({data['percentage']}%)")
        lines.append("")

    # Рекомендации
    if recommendations:
        lines.append("---")
        lines.append("")
        lines.append("## Рекомендации по улучшению")
        lines.append("")

        priority_icons = {"high": "!!!!", "medium": "!!", "low": "!"}

        for i, rec in enumerate(recommendations, 1):
            icon = priority_icons.get(rec["priority"], "")
            lines.append(f"### {i}. [{icon}] {rec['issue']}")
            lines.append("")
            lines.append("**Рекомендации:**")
            for r in rec["recommendations"]:
                lines.append(f"- {r}")
            lines.append("")

    # Детальный список (топ 20)
    rejections = data.get("rejections", [])
    if rejections:
        lines.append("---")
        lines.append("")
        lines.append("## Последние отказы (топ 20)")
        lines.append("")

        # Сортируем по дате (новые первые)
        sorted_rejections = sorted(rejections, key=lambda x: x.get("datetime", ""), reverse=True)[:20]

        for rej in sorted_rejections:
            severity_mark = {"high": "!!!!HIGH", "medium": "!!MEDIUM", "low": "!LOW"}
            sev = severity_mark.get(rej["severity"], "")

            lines.append(f"### [{sev}] {rej.get('datetime', 'Нет даты')[:16]}")
            lines.append("")

            if rej.get("contact_name"):
                lines.append(f"**Контакт:** {rej['contact_name']}")
            lines.append(f"**Причина:** {rej['category_name_ru']}")
            if rej.get("product_name"):
                lines.append(f"**Продукт:** {rej['product_name']}")

            lines.append("")
            lines.append(f"> {rej['text'][:200]}...")
            lines.append("")

            if rej.get("keywords"):
                lines.append(f"*Ключевые слова: {', '.join(rej['keywords'])}*")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"[+] Markdown сохранён: {filepath}")


# ═══════════════════════════════════════════════════════════════
# ВЫВОД СТАТИСТИКИ
# ═══════════════════════════════════════════════════════════════

def print_summary(data: Dict):
    """Выводит сводку в консоль."""
    stats = data.get("statistics", {})
    metadata = data.get("metadata", {})
    recommendations = data.get("recommendations", [])

    print("")
    print("=" * 60)
    print("АНАЛИЗ ПРИЧИН ОТКАЗОВ")
    print("=" * 60)
    print("")
    print(f"Всего сообщений: {metadata.get('total_messages', 0):,}")
    print(f"Выявлено отказов: {metadata.get('total_rejections', 0):,}")
    print(f"Процент отказов: {metadata.get('rejection_rate', 0):.2f}%")
    print("")

    # По категориям
    print("По причинам:")
    category_names = {
        "price": "Цена",
        "competitor": "Конкуренты",
        "timing": "Время/даты",
        "quality_service": "Качество/сервис",
        "personal": "Личные обстоятельства",
        "other": "Другое",
    }

    total = stats.get("total_rejections", 1)
    for category, count in sorted(stats.get("by_category", {}).items(), key=lambda x: x[1], reverse=True):
        name = category_names.get(category, category)
        pct = count / total * 100
        print(f"  {name:25} {count:5} ({pct:5.1f}%)")

    print("")
    print("По серьёзности:")
    severity_names = {"high": "Окончательный", "medium": "Средний", "low": "Мягкий"}
    for severity, count in stats.get("by_severity", {}).items():
        name = severity_names.get(severity, severity)
        pct = count / total * 100
        print(f"  {name:25} {count:5} ({pct:5.1f}%)")

    # Топ рекомендация
    if recommendations:
        print("")
        print("Главная рекомендация:")
        rec = recommendations[0]
        print(f"  {rec['issue']}")
        print(f"  -> {rec['recommendations'][0]}")

    print("")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Анализ причин отказов клиентов в WhatsApp переписке"
    )
    parser.add_argument(
        "--input", "-i",
        default=str(MESSAGES_FILE),
        help="Входной JSONL файл с сообщениями"
    )
    parser.add_argument(
        "--contacts", "-c",
        default=str(CONTACTS_FILE),
        help="Файл контактов (JSON)"
    )
    parser.add_argument(
        "--output-json", "-j",
        default=str(OUTPUT_JSON),
        help="Выходной JSON файл"
    )
    parser.add_argument(
        "--output-csv",
        default=str(OUTPUT_CSV),
        help="Выходной CSV файл"
    )
    parser.add_argument(
        "--output-md", "-m",
        default=str(OUTPUT_MD),
        help="Выходной Markdown файл"
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Не создавать CSV файл"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("АНАЛИЗ ПРИЧИН ОТКАЗОВ")
    print("=" * 60)

    # Загрузка данных
    print("\n[1] Загрузка данных...")
    messages = load_messages_jsonl(Path(args.input))
    print(f"    Сообщений: {len(messages)}")

    contacts = load_contacts(Path(args.contacts))
    print(f"    Контактов: {len(contacts)}")

    if not messages:
        print("\n[!] Нет сообщений для анализа!")
        return

    # Анализ
    print("\n[2] Анализ отказов...")
    results = analyze_rejections(messages, contacts)

    # Сохранение
    print("\n[3] Сохранение результатов...")
    save_json(results, Path(args.output_json))

    if not args.no_csv:
        save_csv(results["rejections"], Path(args.output_csv))

    save_markdown(results, Path(args.output_md))

    # Вывод статистики
    print_summary(results)

    print("\nГОТОВО!")
    print("=" * 60)


if __name__ == "__main__":
    main()
