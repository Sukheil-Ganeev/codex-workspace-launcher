#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
source_conversion.py - Анализ конверсии по источникам трафика

Определяет источник привлечения клиента по первому сообщению и рассчитывает:
- Конверсию по источникам (Leads -> Bookings)
- Средний чек по источникам
- ROI источников
- UTM-подобные метки
- Модели атрибуции
- Воронку по источникам
- Визуализацию (funnel, pie)

Использование:
    python source_conversion.py                     # Полный анализ
    python source_conversion.py --source instagram  # Только Instagram
    python source_conversion.py --funnel            # Показать воронку
    python source_conversion.py --export-csv        # Экспорт в CSV
    python source_conversion.py --visualize         # Генерация графиков

Источники:
- instagram: "нашёл/а в Instagram", "инстаграм", "инста"
- referral: "от друга", "по рекомендации", "знакомый посоветовал"
- advertising: "видел рекламу", "реклама", "по рекламе"
- google: "нашёл в Google", "гуглил", "поиск"
- agent: B2B, турагент, агентство
- direct: прямой контакт, без указания источника
- repeat: повторный клиент
- other: неопределённый источник
"""

import sys
import os
import json
import re
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any
import statistics

sys.stdout.reconfigure(encoding='utf-8')

# === КОНФИГУРАЦИЯ ===

BASE_DIR = Path("D:/Downloads/Chats/_база")
JSON_DIR = BASE_DIR / "json"
RAW_DIR = BASE_DIR / "raw"
MD_DIR = BASE_DIR / "md"
CHARTS_DIR = BASE_DIR / "charts"

# Входные файлы
CONTACTS_FILE = JSON_DIR / "contacts.json"
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
OPERATIONS_FILE = JSON_DIR / "operations.json"
PROFILES_FILE = JSON_DIR / "profiles.json"

# Выходные файлы
OUTPUT_JSON = JSON_DIR / "source_conversion.json"
OUTPUT_CSV = JSON_DIR / "source_conversion.csv"
OUTPUT_MD = MD_DIR / "конверсия_по_источникам.md"

# === ПАТТЕРНЫ ОПРЕДЕЛЕНИЯ ИСТОЧНИКОВ ===

SOURCE_PATTERNS = {
    "instagram": {
        "patterns": [
            r"(?:нашёл|нашла|нашел|нашли|увидел|увидела|видел|видела)\s+(?:вас\s+)?(?:в\s+)?инстаграм",
            r"(?:нашёл|нашла|нашел|нашли|увидел|увидела)\s+(?:в\s+)?(?:инсте|инста)",
            r"(?:из|через|с)\s+инстаграм",
            r"(?:из|через|с)\s+инст(?:ы|а)",
            r"(?:пишу|написал|пишем)\s+(?:из|с)\s+инст(?:а|ы|аграм)",
            r"instagram",
            r"@\w+\s+(?:инста|инстаграм)",
            r"(?:ваш|вашу)\s+(?:страницу|профиль|аккаунт)\s+(?:в\s+)?инст",
            r"сторис",
            r"reels",
        ],
        "name_ru": "Instagram",
        "icon": "IG",
        "channel_type": "social",
        "avg_cost_per_lead": 50,  # AED
    },
    "referral": {
        "patterns": [
            r"по\s+рекомендации",
            r"(?:друг|подруга|знакомый|знакомая|коллега)\s+(?:посоветовал|рекомендовал|дал|дала)",
            r"от\s+(?:друга|подруги|знакомого|знакомой|коллеги)",
            r"(?:мне|нам)\s+(?:рекомендовали|посоветовали|дали\s+контакт)",
            r"знакомые\s+(?:ездили|были|рекомендовали)",
            r"(?:ваш|твой)\s+(?:контакт|номер)\s+(?:дал|дала)",
            r"(?:друзья|знакомые|коллеги)\s+(?:были|ездили)\s+(?:у\s+вас|с\s+вами)",
            r"порекомендовал[аи]?",
            r"передали\s+(?:ваш\s+)?(?:контакт|номер)",
        ],
        "name_ru": "Рекомендация",
        "icon": "REF",
        "channel_type": "organic",
        "avg_cost_per_lead": 0,  # Бесплатно
    },
    "advertising": {
        "patterns": [
            r"(?:видел|видела|увидел|увидела)\s+(?:вашу\s+)?рекламу",
            r"(?:по|из)\s+реклам[ыеа]",
            r"рекламу\s+(?:видел|увидел|видела|увидела)",
            r"(?:таргет|таргетинг|таргетирован)",
            r"рекламное\s+(?:объявление|предложение)",
            r"(?:yandex|яндекс)\s+(?:директ|реклама)",
            r"(?:facebook|фейсбук)\s+(?:ads|реклама)",
            r"баннер",
            r"промо(?:акция|код)?",
        ],
        "name_ru": "Реклама",
        "icon": "ADS",
        "channel_type": "paid",
        "avg_cost_per_lead": 150,  # AED
    },
    "google": {
        "patterns": [
            r"(?:нашёл|нашла|нашел|нашли)\s+(?:вас\s+)?(?:в\s+)?(?:google|гугл)",
            r"(?:из|через|в)\s+(?:google|гугл)",
            r"(?:гуглил|гуглила|погуглил|погуглила)",
            r"поиск\s+(?:google|гугл)",
            r"(?:google|гугл)\s+поиск",
            r"(?:нашёл|нашла|нашел)\s+(?:в\s+)?(?:интернете|сети)",
            r"(?:search|поисков)",
            r"(?:яндекс|yandex)\s+(?:поиск|искал)",
            r"(?:искал|искала)\s+(?:в\s+)?(?:интернете|гугле)",
        ],
        "name_ru": "Поиск Google",
        "icon": "GGL",
        "channel_type": "organic",
        "avg_cost_per_lead": 30,  # SEO costs distributed
    },
    "agent": {
        "patterns": [
            r"(?:я|мы)\s+(?:турагент|агент|агентство)",
            r"(?:от|из)\s+(?:турагент|агентств)",
            r"(?:b2b|B2B|Б2Б)",
            r"(?:партнёр|партнер)",
            r"(?:туроператор|турфирма)",
            r"(?:нетто|брутто|комисси)",
            r"(?:wholesale|оптов)",
            r"(?:агентский|партнёрский)\s+(?:запрос|договор)",
            r"(?:travel\s+)?agency",
        ],
        "name_ru": "Агент (B2B)",
        "icon": "B2B",
        "channel_type": "b2b",
        "avg_cost_per_lead": 0,  # Партнёрский канал
    },
    "telegram": {
        "patterns": [
            r"(?:нашёл|нашла|нашел|увидел)\s+(?:в\s+)?telegram",
            r"(?:из|через|с)\s+(?:телеграм|telegram)",
            r"(?:ваш|вашу)\s+(?:канал|группу|чат)\s+(?:в\s+)?telegram",
            r"телеграм(?:\s+канал)?",
            r"тг(?:\s+канал)?",
            r"@\w+\s+(?:телеграм|telegram)",
        ],
        "name_ru": "Telegram",
        "icon": "TG",
        "channel_type": "social",
        "avg_cost_per_lead": 20,  # AED
    },
    "website": {
        "patterns": [
            r"(?:с|на)\s+(?:вашего\s+)?сайт[аеу]",
            r"(?:нашёл|нашла|нашел)\s+(?:на\s+)?сайт[еу]",
            r"(?:форму\s+)?(?:заполнил|оставил)\s+(?:на\s+)?сайт[еу]",
            r"(?:заявк[ауе]|форм[ауе])\s+(?:с|на)\s+сайт",
            r"(?:viator|tripadvisor|trip\s*advisor|get\s*your\s*guide)",
            r"(?:booking|airbnb|expedia)",
        ],
        "name_ru": "Сайт",
        "icon": "WEB",
        "channel_type": "organic",
        "avg_cost_per_lead": 40,  # AED
    },
    "whatsapp_business": {
        "patterns": [
            r"(?:whatsapp|ватсап)\s+(?:business|бизнес|каталог)",
            r"(?:каталог|catalog)\s+(?:whatsapp|ватсап)",
            r"wa\.me",
            r"(?:кнопк[ауе]|ссылк[ауе])\s+(?:в\s+)?(?:whatsapp|ватсап)",
        ],
        "name_ru": "WhatsApp Business",
        "icon": "WAB",
        "channel_type": "direct",
        "avg_cost_per_lead": 10,  # AED
    },
    "repeat": {
        "patterns": [
            r"(?:снова|опять|ещё\s+раз|еще\s+раз)\s+(?:обращаюсь|пишу|хочу)",
            r"(?:были|ездили|заказывали)\s+(?:у\s+вас|раньше|в\s+прошлом)",
            r"(?:помните\s+)?(?:меня|нас)",
            r"(?:прошлый|предыдущий)\s+(?:раз|заказ|тур)",
            r"(?:постоянный|повторный)\s+клиент",
            r"(?:вернулись|возвращаемся)",
        ],
        "name_ru": "Повторный клиент",
        "icon": "RPT",
        "channel_type": "retention",
        "avg_cost_per_lead": 0,  # Бесплатно
    },
}

# Паттерны для UTM-подобных меток в сообщениях
UTM_PATTERNS = {
    "utm_source": [
        r"источник[:\s]+(\w+)",
        r"source[:\s]+(\w+)",
        r"от[:\s]+(\w+)",
    ],
    "utm_medium": [
        r"канал[:\s]+(\w+)",
        r"medium[:\s]+(\w+)",
    ],
    "utm_campaign": [
        r"кампания[:\s]+(\w+)",
        r"campaign[:\s]+(\w+)",
        r"акция[:\s]+(\w+)",
        r"промо[:\s]+(\w+)",
    ],
    "utm_content": [
        r"контент[:\s]+(\w+)",
        r"content[:\s]+(\w+)",
    ],
}

# Стадии воронки
FUNNEL_STAGES = ["lead", "inquiry", "quote", "booking", "payment", "completed"]

# Паттерны стадий (упрощённые)
STAGE_PATTERNS = {
    "inquiry": [
        r"сколько\s+стоит", r"какая\s+цена", r"интересует",
        r"хочу\s+узнать", r"подскажите", r"нужен\s+(?:тур|трансфер)",
    ],
    "quote": [
        r"стоимость\s+составит", r"цена[:\s]*\d", r"расчёт", r"прайс",
        r"\d+\s*(?:AED|дирхам|руб)", r"итого",
    ],
    "booking": [
        r"бронируем", r"заказываем", r"подтверждаем", r"берём",
        r"согласны", r"подходит", r"оформляйте",
    ],
    "payment": [
        r"оплатил", r"перевёл", r"отправил\s+(?:деньги|оплату)",
        r"чек", r"квитанция", r"оплата\s+(?:получена|поступила)",
    ],
    "completed": [
        r"спасибо\s+за\s+(?:экскурсию|тур|трансфер)",
        r"(?:всё|все)\s+(?:понравилось|супер|отлично)",
        r"остались\s+довольны", r"будем\s+обращаться",
    ],
}


# === ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ ===

def load_json(filepath: Path) -> Any:
    """Загрузка JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and "contacts" in data:
        return data["contacts"]
    return data


def load_messages(filepath: Path) -> List[Dict]:
    """Загрузка сообщений из JSONL файла."""
    messages = []

    if not filepath.exists():
        print(f"[!] Файл сообщений не найден: {filepath}")
        return messages

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue

    return messages


def save_json(data: Dict, filepath: Path):
    """Сохранение JSON файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"[+] JSON сохранён: {filepath}")


def save_csv(data: List[Dict], filepath: Path, fieldnames: List[str]):
    """Сохранение CSV файла."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] CSV сохранён: {filepath}")


# === ФУНКЦИИ ОПРЕДЕЛЕНИЯ ИСТОЧНИКА ===

def detect_source_from_text(text: str) -> Tuple[str, float]:
    """
    Определяет источник по тексту сообщения.
    Возвращает (source_key, confidence).
    """
    if not text:
        return "direct", 0.3

    text_lower = text.lower()

    best_source = "direct"
    best_confidence = 0.3
    best_match_count = 0

    for source_key, source_data in SOURCE_PATTERNS.items():
        match_count = 0
        for pattern in source_data["patterns"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                match_count += 1

        if match_count > best_match_count:
            best_match_count = match_count
            best_source = source_key
            # Confidence зависит от количества совпадений
            best_confidence = min(0.5 + match_count * 0.2, 1.0)

    return best_source, best_confidence


def detect_source_for_contact(
    jid: str,
    messages: List[Dict],
    contact_info: Dict
) -> Dict:
    """
    Определяет источник для контакта по первым сообщениям.
    """
    # Фильтруем и сортируем сообщения контакта
    contact_messages = [
        m for m in messages
        if (m.get("jid") == jid or
            m.get("chat_jid") == jid or
            m.get("contact_jid") == jid or
            m.get("remote_jid") == jid)
    ]

    contact_messages.sort(key=lambda x: x.get("timestamp", "") or x.get("date", ""))

    if not contact_messages:
        return {
            "source": "direct",
            "confidence": 0.2,
            "detected_by": "no_messages",
            "first_message": None,
            "utm": {}
        }

    # Анализируем первые 5 сообщений
    first_messages = contact_messages[:5]
    combined_text = " ".join(
        m.get("text", "") or m.get("body", "") or m.get("content", "")
        for m in first_messages
    )

    # Определяем источник
    source, confidence = detect_source_from_text(combined_text)

    # Извлекаем UTM метки
    utm_data = extract_utm_tags(combined_text)

    # Проверяем тип контакта (агент)
    contact_type = contact_info.get("type", "")
    if contact_type in ["агенты", "agents", "agent", "b2b"]:
        source = "agent"
        confidence = 0.9

    # Проверяем повторность
    orders_count = contact_info.get("ltv", {}).get("orders_count", 0)
    if orders_count > 1 and source == "direct":
        source = "repeat"
        confidence = 0.8

    # Первое сообщение
    first_msg = first_messages[0] if first_messages else None
    first_message_data = None
    if first_msg:
        first_message_data = {
            "date": first_msg.get("timestamp") or first_msg.get("date"),
            "text": (first_msg.get("text", "") or first_msg.get("body", ""))[:200],
            "sender": first_msg.get("sender", "")
        }

    return {
        "source": source,
        "confidence": confidence,
        "detected_by": "pattern_match" if confidence > 0.3 else "default",
        "first_message": first_message_data,
        "utm": utm_data
    }


def extract_utm_tags(text: str) -> Dict[str, str]:
    """Извлекает UTM-подобные метки из текста."""
    utm = {}

    for utm_key, patterns in UTM_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                utm[utm_key] = match.group(1)
                break

    return utm


# === ФУНКЦИИ АНАЛИЗА ВОРОНКИ ===

def detect_funnel_stage(messages: List[Dict], operations: List[Dict]) -> str:
    """Определяет текущую стадию воронки для контакта."""

    # Проверяем операции
    completed_ops = [op for op in operations if op.get("status") == "completed"]
    if completed_ops:
        return "completed"

    paid_ops = [op for op in operations if op.get("status") in ["paid", "payment"]]
    if paid_ops:
        return "payment"

    booked_ops = [op for op in operations if op.get("status") in ["booked", "booking", "confirmed"]]
    if booked_ops:
        return "booking"

    # Анализируем сообщения
    combined_text = " ".join(
        (m.get("text", "") or m.get("body", "")).lower()
        for m in messages
    )

    # Проверяем стадии от конца к началу
    for stage in reversed(FUNNEL_STAGES[1:]):  # Пропускаем lead
        if stage in STAGE_PATTERNS:
            for pattern in STAGE_PATTERNS[stage]:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return stage

    # По умолчанию - inquiry (если есть сообщения) или lead
    if messages:
        return "inquiry"
    return "lead"


def calculate_conversion_by_source(
    contacts: List[Dict],
    messages: List[Dict],
    operations: List[Dict]
) -> Dict:
    """
    Рассчитывает конверсию по источникам.
    """
    # Группируем сообщения по JID
    messages_by_jid = defaultdict(list)
    for msg in messages:
        jid = (msg.get("jid") or msg.get("chat_jid") or
               msg.get("contact_jid") or msg.get("remote_jid", ""))
        if jid:
            messages_by_jid[jid].append(msg)

    # Группируем операции по телефону
    operations_by_phone = defaultdict(list)
    for op in operations:
        phone = op.get("phone", "")
        if phone:
            operations_by_phone[phone].append(op)

    # Анализируем каждый контакт
    source_data = defaultdict(lambda: {
        "contacts": [],
        "leads": 0,
        "inquiries": 0,
        "quotes": 0,
        "bookings": 0,
        "payments": 0,
        "completed": 0,
        "revenue_aed": 0,
        "avg_check": 0,
        "total_orders": 0,
    })

    contacts_with_source = []

    for contact in contacts:
        jid = contact.get("jid", "")
        phone = contact.get("phone", "")

        if not jid and not phone:
            continue

        # Получаем сообщения контакта
        contact_messages = messages_by_jid.get(jid, [])

        # Определяем источник
        source_info = detect_source_for_contact(jid, messages, contact)
        source = source_info["source"]

        # Получаем операции контакта
        contact_ops = operations_by_phone.get(phone, [])

        # Определяем стадию воронки
        stage = detect_funnel_stage(contact_messages, contact_ops)

        # Рассчитываем выручку
        revenue = sum(
            op.get("amount", 0) * (3.67 if op.get("currency") == "USD" else 1)
            for op in contact_ops
            if op.get("status") == "completed"
        )

        orders_count = len([op for op in contact_ops if op.get("status") == "completed"])

        # Обновляем статистику источника
        source_data[source]["contacts"].append({
            "jid": jid,
            "phone": phone,
            "name": contact.get("name", phone),
            "stage": stage,
            "revenue": revenue,
            "orders": orders_count,
            "source_confidence": source_info["confidence"],
            "utm": source_info["utm"]
        })

        source_data[source]["leads"] += 1
        source_data[source]["revenue_aed"] += revenue
        source_data[source]["total_orders"] += orders_count

        # Считаем стадии воронки
        stage_index = FUNNEL_STAGES.index(stage) if stage in FUNNEL_STAGES else 0
        if stage_index >= 1:
            source_data[source]["inquiries"] += 1
        if stage_index >= 2:
            source_data[source]["quotes"] += 1
        if stage_index >= 3:
            source_data[source]["bookings"] += 1
        if stage_index >= 4:
            source_data[source]["payments"] += 1
        if stage_index >= 5:
            source_data[source]["completed"] += 1

        # Сохраняем данные контакта
        contact_with_source = {
            **contact,
            "source": source,
            "source_confidence": source_info["confidence"],
            "funnel_stage": stage,
            "utm": source_info["utm"],
            "revenue_from_source": revenue
        }
        contacts_with_source.append(contact_with_source)

    # Рассчитываем средний чек
    for source, data in source_data.items():
        if data["total_orders"] > 0:
            data["avg_check"] = data["revenue_aed"] / data["total_orders"]

    return {
        "by_source": dict(source_data),
        "contacts": contacts_with_source
    }


def calculate_source_roi(source_data: Dict) -> Dict:
    """
    Рассчитывает ROI для каждого источника.
    """
    roi_data = {}

    for source, data in source_data.items():
        source_config = SOURCE_PATTERNS.get(source, {})
        cost_per_lead = source_config.get("avg_cost_per_lead", 0)

        leads = data.get("leads", 0)
        revenue = data.get("revenue_aed", 0)

        # Общие затраты на источник
        total_cost = leads * cost_per_lead

        # ROI = (Revenue - Cost) / Cost * 100%
        if total_cost > 0:
            roi = (revenue - total_cost) / total_cost * 100
        else:
            roi = float('inf') if revenue > 0 else 0

        # CAC (Customer Acquisition Cost)
        completed = data.get("completed", 0)
        cac = total_cost / completed if completed > 0 else 0

        # Конверсия Lead -> Completed
        conversion_rate = completed / leads * 100 if leads > 0 else 0

        roi_data[source] = {
            "leads": leads,
            "completed": completed,
            "conversion_rate": round(conversion_rate, 2),
            "revenue_aed": round(revenue, 2),
            "cost_per_lead": cost_per_lead,
            "total_cost": round(total_cost, 2),
            "cac": round(cac, 2),
            "roi_percent": round(roi, 2) if roi != float('inf') else "infinite",
            "channel_type": source_config.get("channel_type", "unknown"),
            "name_ru": source_config.get("name_ru", source),
        }

    return roi_data


def calculate_attribution(
    contacts_with_source: List[Dict],
    model: str = "first_touch"
) -> Dict:
    """
    Рассчитывает атрибуцию конверсий.

    Модели:
    - first_touch: 100% первому источнику
    - last_touch: 100% последнему источнику
    - linear: равномерное распределение
    - position_based: 40% первому, 40% последнему, 20% средним
    """
    attribution = defaultdict(lambda: {"revenue": 0, "conversions": 0})

    for contact in contacts_with_source:
        revenue = contact.get("revenue_from_source", 0)
        source = contact.get("source", "direct")
        stage = contact.get("funnel_stage", "lead")

        if stage not in ["payment", "completed"]:
            continue

        # Для простоты используем first_touch
        # (можно расширить для multi-touch атрибуции)
        if model == "first_touch":
            attribution[source]["revenue"] += revenue
            attribution[source]["conversions"] += 1

    return dict(attribution)


# === ФУНКЦИИ ГЕНЕРАЦИИ ОТЧЁТОВ ===

def build_funnel_by_source(source_data: Dict) -> Dict:
    """Строит воронку по каждому источнику."""
    funnel = {}

    for source, data in source_data.items():
        source_config = SOURCE_PATTERNS.get(source, {})

        funnel[source] = {
            "name": source_config.get("name_ru", source),
            "icon": source_config.get("icon", ""),
            "stages": {
                "lead": data.get("leads", 0),
                "inquiry": data.get("inquiries", 0),
                "quote": data.get("quotes", 0),
                "booking": data.get("bookings", 0),
                "payment": data.get("payments", 0),
                "completed": data.get("completed", 0),
            },
            "conversion_rates": {}
        }

        # Рассчитываем конверсии между стадиями
        stages = funnel[source]["stages"]
        for i, stage in enumerate(FUNNEL_STAGES[1:], 1):
            prev_stage = FUNNEL_STAGES[i - 1]
            prev_count = stages.get(prev_stage, 0)
            curr_count = stages.get(stage, 0)

            if prev_count > 0:
                rate = curr_count / prev_count * 100
            else:
                rate = 0

            funnel[source]["conversion_rates"][f"{prev_stage}_to_{stage}"] = round(rate, 1)

    return funnel


def generate_markdown_report(analysis: Dict) -> str:
    """Генерирует Markdown отчёт."""
    lines = []
    lines.append("# Анализ конверсии по источникам")
    lines.append("")
    lines.append(f"*Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    # Общая статистика
    overall = analysis.get("overall", {})
    lines.append("## Общие показатели")
    lines.append("")
    lines.append("| Метрика | Значение |")
    lines.append("|---------|----------|")
    lines.append(f"| Всего лидов | {overall.get('total_leads', 0)} |")
    lines.append(f"| Всего конверсий | {overall.get('total_completed', 0)} |")
    lines.append(f"| Общая выручка | {overall.get('total_revenue', 0):,.0f} AED |")
    lines.append(f"| Средняя конверсия | {overall.get('avg_conversion_rate', 0):.1f}% |")
    lines.append(f"| Средний чек | {overall.get('avg_check', 0):,.0f} AED |")
    lines.append("")

    # ROI по источникам
    roi_data = analysis.get("roi_by_source", {})
    lines.append("## ROI по источникам")
    lines.append("")
    lines.append("| Источник | Лидов | Конверсий | Конверсия | Выручка | CAC | ROI |")
    lines.append("|----------|-------|-----------|-----------|---------|-----|-----|")

    for source, data in sorted(roi_data.items(), key=lambda x: x[1].get("revenue_aed", 0), reverse=True):
        roi_str = f"{data['roi_percent']}%" if isinstance(data['roi_percent'], (int, float)) else data['roi_percent']
        lines.append(
            f"| {data['name_ru']} | {data['leads']} | {data['completed']} | "
            f"{data['conversion_rate']}% | {data['revenue_aed']:,.0f} | "
            f"{data['cac']:,.0f} | {roi_str} |"
        )
    lines.append("")

    # Воронка продаж по источникам
    funnel_data = analysis.get("funnel_by_source", {})
    lines.append("## Воронка по источникам")
    lines.append("")

    for source, funnel in sorted(funnel_data.items(), key=lambda x: x[1]["stages"]["lead"], reverse=True):
        if funnel["stages"]["lead"] == 0:
            continue

        lines.append(f"### {funnel['icon']} {funnel['name']}")
        lines.append("")
        lines.append("```")

        stages = funnel["stages"]
        max_val = max(stages.values()) or 1
        bar_width = 40

        stage_names = {
            "lead": "Лид",
            "inquiry": "Запрос",
            "quote": "Расчёт",
            "booking": "Бронь",
            "payment": "Оплата",
            "completed": "Выполнено"
        }

        for stage in FUNNEL_STAGES:
            count = stages.get(stage, 0)
            bar_len = int((count / max_val) * bar_width)
            bar = "#" * bar_len + "-" * (bar_width - bar_len)
            lines.append(f"{stage_names.get(stage, stage):12} [{bar}] {count}")

        lines.append("```")
        lines.append("")

    # Топ контактов по источникам
    contacts = analysis.get("top_contacts_by_source", {})
    if contacts:
        lines.append("## Топ клиентов по источникам")
        lines.append("")

        for source, contact_list in contacts.items():
            if not contact_list:
                continue

            source_name = SOURCE_PATTERNS.get(source, {}).get("name_ru", source)
            lines.append(f"### {source_name}")
            lines.append("")
            lines.append("| Имя | Выручка | Заказов | Стадия |")
            lines.append("|-----|---------|---------|--------|")

            for c in contact_list[:5]:
                lines.append(
                    f"| {c['name'][:25]} | {c['revenue']:,.0f} AED | "
                    f"{c['orders']} | {c['stage']} |"
                )
            lines.append("")

    # Рекомендации
    lines.append("## Рекомендации")
    lines.append("")

    # Находим лучшие и худшие источники
    if roi_data:
        sorted_by_roi = sorted(
            [(s, d) for s, d in roi_data.items() if isinstance(d.get("roi_percent"), (int, float))],
            key=lambda x: x[1]["roi_percent"],
            reverse=True
        )

        if sorted_by_roi:
            best = sorted_by_roi[0]
            lines.append(f"1. **Лучший источник:** {best[1]['name_ru']} (ROI: {best[1]['roi_percent']}%)")

        sorted_by_conversion = sorted(
            roi_data.items(),
            key=lambda x: x[1]["conversion_rate"],
            reverse=True
        )
        if sorted_by_conversion:
            best_conv = sorted_by_conversion[0]
            lines.append(f"2. **Лучшая конверсия:** {best_conv[1]['name_ru']} ({best_conv[1]['conversion_rate']}%)")

        # Источники с низкой конверсией
        low_conv = [s for s, d in roi_data.items() if d["conversion_rate"] < 5 and d["leads"] > 10]
        if low_conv:
            lines.append(f"3. **Требуют внимания:** {', '.join(SOURCE_PATTERNS.get(s, {}).get('name_ru', s) for s in low_conv)}")

    lines.append("")

    return "\n".join(lines)


def generate_visualization(analysis: Dict, output_dir: Path):
    """
    Генерирует визуализации (ASCII art, так как matplotlib может быть недоступен).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # ASCII воронка
    funnel_lines = []
    funnel_lines.append("=" * 60)
    funnel_lines.append("ВОРОНКА КОНВЕРСИИ ПО ИСТОЧНИКАМ")
    funnel_lines.append("=" * 60)
    funnel_lines.append("")

    funnel_data = analysis.get("funnel_by_source", {})

    for source, data in sorted(funnel_data.items(), key=lambda x: x[1]["stages"]["lead"], reverse=True)[:5]:
        stages = data["stages"]
        name = data["name"]

        funnel_lines.append(f"\n--- {name} ---")

        max_val = stages["lead"] or 1
        for stage in FUNNEL_STAGES:
            count = stages.get(stage, 0)
            pct = count / max_val * 100 if max_val > 0 else 0
            bar_len = int(pct / 2)
            bar = "#" * bar_len
            funnel_lines.append(f"  {stage:10} | {bar:50} | {count:4} ({pct:.0f}%)")

    funnel_txt = "\n".join(funnel_lines)
    with open(output_dir / "funnel_ascii.txt", 'w', encoding='utf-8') as f:
        f.write(funnel_txt)

    print(f"[+] ASCII воронка: {output_dir / 'funnel_ascii.txt'}")

    # Pie chart (ASCII)
    pie_lines = []
    pie_lines.append("=" * 60)
    pie_lines.append("РАСПРЕДЕЛЕНИЕ ЛИДОВ ПО ИСТОЧНИКАМ")
    pie_lines.append("=" * 60)
    pie_lines.append("")

    roi_data = analysis.get("roi_by_source", {})
    total_leads = sum(d.get("leads", 0) for d in roi_data.values())

    if total_leads > 0:
        for source, data in sorted(roi_data.items(), key=lambda x: x[1]["leads"], reverse=True):
            leads = data.get("leads", 0)
            pct = leads / total_leads * 100
            bar_len = int(pct / 2)
            bar = "*" * bar_len
            pie_lines.append(f"  {data['name_ru']:20} | {bar:50} | {leads:4} ({pct:.1f}%)")

    pie_txt = "\n".join(pie_lines)
    with open(output_dir / "pie_ascii.txt", 'w', encoding='utf-8') as f:
        f.write(pie_txt)

    print(f"[+] ASCII pie: {output_dir / 'pie_ascii.txt'}")


# === ОСНОВНАЯ ФУНКЦИЯ ===

def analyze_source_conversion(
    contacts_file: Path = CONTACTS_FILE,
    messages_file: Path = MESSAGES_FILE,
    operations_file: Path = OPERATIONS_FILE,
    filter_source: Optional[str] = None
) -> Dict:
    """
    Выполняет полный анализ конверсии по источникам.
    """
    print("[*] Загрузка данных...")

    contacts = load_json(contacts_file)
    messages = load_messages(messages_file)
    operations = load_json(operations_file)

    print(f"    Контактов: {len(contacts)}")
    print(f"    Сообщений: {len(messages)}")
    print(f"    Операций: {len(operations)}")

    print("\n[*] Анализ источников...")

    # Рассчитываем конверсию
    conversion_data = calculate_conversion_by_source(contacts, messages, operations)
    source_data = conversion_data["by_source"]
    contacts_with_source = conversion_data["contacts"]

    # Фильтрация по источнику
    if filter_source:
        source_data = {k: v for k, v in source_data.items() if k == filter_source}
        contacts_with_source = [c for c in contacts_with_source if c["source"] == filter_source]

    # ROI
    print("[*] Расчёт ROI...")
    roi_data = calculate_source_roi(source_data)

    # Воронка
    print("[*] Построение воронки...")
    funnel_data = build_funnel_by_source(source_data)

    # Атрибуция
    print("[*] Расчёт атрибуции...")
    attribution = calculate_attribution(contacts_with_source)

    # Общие метрики
    total_leads = sum(d.get("leads", 0) for d in source_data.values())
    total_completed = sum(d.get("completed", 0) for d in source_data.values())
    total_revenue = sum(d.get("revenue_aed", 0) for d in source_data.values())
    total_orders = sum(d.get("total_orders", 0) for d in source_data.values())

    overall = {
        "total_leads": total_leads,
        "total_completed": total_completed,
        "total_revenue": round(total_revenue, 2),
        "avg_conversion_rate": round(total_completed / total_leads * 100, 2) if total_leads > 0 else 0,
        "avg_check": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
    }

    # Топ контактов по источникам
    top_contacts = {}
    for source in source_data.keys():
        source_contacts = [c for c in contacts_with_source if c["source"] == source]
        sorted_contacts = sorted(source_contacts, key=lambda x: x.get("revenue_from_source", 0), reverse=True)
        top_contacts[source] = [
            {
                "name": c.get("name", c.get("phone", "")),
                "revenue": c.get("revenue_from_source", 0),
                "orders": c.get("ltv", {}).get("orders_count", 0),
                "stage": c.get("funnel_stage", "lead")
            }
            for c in sorted_contacts[:10]
        ]

    # Формируем результат
    analysis = {
        "generated_at": datetime.now().isoformat(),
        "overall": overall,
        "by_source": source_data,
        "roi_by_source": roi_data,
        "funnel_by_source": funnel_data,
        "attribution": attribution,
        "top_contacts_by_source": top_contacts,
        "contacts_with_source": contacts_with_source,
    }

    return analysis


def main():
    parser = argparse.ArgumentParser(description="Анализ конверсии по источникам")
    parser.add_argument("--contacts", default=str(CONTACTS_FILE),
                        help="Путь к файлу контактов")
    parser.add_argument("--messages", default=str(MESSAGES_FILE),
                        help="Путь к файлу сообщений")
    parser.add_argument("--operations", default=str(OPERATIONS_FILE),
                        help="Путь к файлу операций")
    parser.add_argument("--source", type=str,
                        help="Фильтр по источнику (instagram, referral, etc.)")
    parser.add_argument("--funnel", action="store_true",
                        help="Показать воронку")
    parser.add_argument("--export-csv", action="store_true",
                        help="Экспортировать в CSV")
    parser.add_argument("--visualize", action="store_true",
                        help="Генерировать визуализации")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Минимальный вывод")
    parser.add_argument("--output-json", default=str(OUTPUT_JSON),
                        help="Путь к выходному JSON")
    parser.add_argument("--output-md", default=str(OUTPUT_MD),
                        help="Путь к выходному MD")

    args = parser.parse_args()

    print("=" * 60)
    print("АНАЛИЗ КОНВЕРСИИ ПО ИСТОЧНИКАМ")
    print("=" * 60)
    print()

    # Выполняем анализ
    analysis = analyze_source_conversion(
        contacts_file=Path(args.contacts),
        messages_file=Path(args.messages),
        operations_file=Path(args.operations),
        filter_source=args.source
    )

    # Сохраняем JSON
    save_json(analysis, Path(args.output_json))

    # Генерируем Markdown
    md_report = generate_markdown_report(analysis)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_md, 'w', encoding='utf-8') as f:
        f.write(md_report)
    print(f"[+] Markdown отчёт: {args.output_md}")

    # Экспорт в CSV
    if args.export_csv:
        csv_data = []
        for contact in analysis.get("contacts_with_source", []):
            csv_data.append({
                "jid": contact.get("jid", ""),
                "phone": contact.get("phone", ""),
                "name": contact.get("name", ""),
                "source": contact.get("source", ""),
                "source_confidence": contact.get("source_confidence", 0),
                "funnel_stage": contact.get("funnel_stage", ""),
                "revenue": contact.get("revenue_from_source", 0),
                "utm_source": contact.get("utm", {}).get("utm_source", ""),
                "utm_campaign": contact.get("utm", {}).get("utm_campaign", ""),
            })

        fieldnames = ["jid", "phone", "name", "source", "source_confidence",
                      "funnel_stage", "revenue", "utm_source", "utm_campaign"]
        save_csv(csv_data, OUTPUT_CSV, fieldnames)

    # Визуализация
    if args.visualize:
        generate_visualization(analysis, CHARTS_DIR)

    # Вывод результатов
    if not args.quiet:
        overall = analysis.get("overall", {})
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 60)

        print(f"\nВсего лидов: {overall.get('total_leads', 0)}")
        print(f"Конверсий: {overall.get('total_completed', 0)}")
        print(f"Общая выручка: {overall.get('total_revenue', 0):,.0f} AED")
        print(f"Средняя конверсия: {overall.get('avg_conversion_rate', 0):.1f}%")
        print(f"Средний чек: {overall.get('avg_check', 0):,.0f} AED")

        print("\nПо источникам:")
        roi_data = analysis.get("roi_by_source", {})
        for source, data in sorted(roi_data.items(), key=lambda x: x[1]["revenue_aed"], reverse=True):
            print(f"  {data['name_ru']:20} | Лидов: {data['leads']:4} | "
                  f"Конв: {data['conversion_rate']:5.1f}% | "
                  f"Выручка: {data['revenue_aed']:10,.0f} AED")

        if args.funnel:
            print("\n" + "=" * 60)
            print("ВОРОНКА")
            print("=" * 60)

            funnel_data = analysis.get("funnel_by_source", {})
            for source, data in funnel_data.items():
                print(f"\n{data['name']}:")
                stages = data["stages"]
                for stage in FUNNEL_STAGES:
                    print(f"  {stage:12}: {stages.get(stage, 0)}")

    print("\n[+] Анализ завершён!")


if __name__ == "__main__":
    main()
