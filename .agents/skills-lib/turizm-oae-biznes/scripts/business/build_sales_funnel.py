#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Построение воронки продаж на основе анализа чатов WhatsApp.

Стадии воронки:
1. inquiry   - Запрос (сколько стоит, интересует)
2. quote     - Расчёт отправлен
3. booking   - Бронирование
4. payment   - Оплата
5. completed - Выполнено
6. lost      - Потеряно

Входные файлы:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/contacts.json
- D:/Downloads/Chats/_база/json/operations.json (опционально)

Выходные файлы:
- D:/Downloads/Chats/_база/json/sales_funnel.json
- D:/Downloads/Chats/_база/md/воронка_продаж.md
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

MESSAGES_FILE = Path("D:/Downloads/Chats/_база/raw/all_messages.jsonl")
CONTACTS_FILE = Path("D:/Downloads/Chats/_база/json/contacts.json")
OPERATIONS_FILE = Path("D:/Downloads/Chats/_база/json/operations.json")

OUTPUT_JSON = Path("D:/Downloads/Chats/_база/json/sales_funnel.json")
OUTPUT_MD = Path("D:/Downloads/Chats/_база/md/воронка_продаж.md")

# Порог неактивности для "lost" (дней)
INACTIVITY_THRESHOLD_DAYS = 7

# Типы продуктов для анализа
PRODUCT_TYPES = {
    "tour": ["экскурсия", "тур", "сафари", "обзорная", "абу-даби", "абу даби"],
    "transfer": ["трансфер", "transfer", "встреча", "аэропорт", "проводы"],
    "yacht": ["яхта", "yacht", "катер", "морская прогулка"],
    "tickets": ["билет", "ticket", "ferrari", "aquaventure", "парк"],
    "car_rental": ["аренда", "авто", "машина", "rental", "car"],
    "catering": ["кейтеринг", "catering", "ресторан", "ужин"],
    "other": []
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ОПРЕДЕЛЕНИЯ СТАДИЙ
# ═══════════════════════════════════════════════════════════════

# Паттерны для определения стадий (от клиента)
STAGE_PATTERNS = {
    "inquiry": {
        "client": [
            r"сколько\s+стоит",
            r"какая\s+цена",
            r"интересует",
            r"хочу\s+узнать",
            r"подскажите\s+(?:цену|стоимость)",
            r"можно\s+узнать",
            r"нужен\s+(?:тур|трансфер|экскурсия)",
            r"хотим\s+(?:заказать|забронировать|съездить)",
            r"планируем",
            r"рассматриваем",
            r"есть\s+ли\s+у\s+вас",
            r"можете\s+(?:организовать|предложить)",
            r"ищем",
            r"нам\s+нужно",
            r"какие\s+варианты",
        ],
        "agent": []
    },
    "quote": {
        "client": [],
        "agent": [
            r"стоимость\s+составит",
            r"цена\s*[-:]\s*\d",
            r"прайс",
            r"расчёт",
            r"расчет",
            r"\d+\s*(?:AED|дирхам|руб|RUB|\$|USD)",
            r"стоит\s+\d+",
            r"будет\s+стоить",
            r"по\s+цене",
            r"со\s+скидкой",
            r"итого",
            r"total",
        ]
    },
    "booking": {
        "client": [
            r"бронируем",
            r"заказываем",
            r"подтверждаем",
            r"берём",
            r"берем",
            r"давайте\s+(?:этот|эту|это)",
            r"хотим\s+забронировать",
            r"да,\s*(?:бронируем|заказываем|берём|берем)",
            r"согласны",
            r"подходит",
            r"устраивает",
            r"оформляйте",
            r"записывайте",
            r"бронь",
        ],
        "agent": [
            r"бронирование\s+(?:подтверждено|оформлено)",
            r"заявка\s+принята",
            r"забронировано",
            r"записал",
            r"оформила?\s+(?:бронь|заявку)",
        ]
    },
    "payment": {
        "client": [
            r"оплатил[аи]?",
            r"перевёл[аи]?",
            r"перевел[аи]?",
            r"отправил[аи]?\s+(?:деньги|оплату|перевод)",
            r"чек",
            r"квитанция",
            r"скрин\s+(?:оплаты|перевода)",
            r"скинул[аи]?\s+(?:деньги|оплату)",
        ],
        "agent": [
            r"оплата\s+(?:получена|поступила|прошла)",
            r"деньги\s+(?:получили|пришли|поступили)",
            r"спасибо\s+за\s+оплату",
            r"платёж\s+подтверждён",
            r"платеж\s+подтвержден",
        ]
    },
    "completed": {
        "client": [
            r"спасибо\s+за\s+(?:экскурсию|тур|трансфер|поездку)",
            r"всё\s+(?:понравилось|супер|отлично|класс)",
            r"все\s+(?:понравилось|супер|отлично|класс)",
            r"было\s+(?:здорово|круто|классно|отлично)",
            r"остались\s+довольны",
            r"рекомендуем",
            r"будем\s+обращаться",
            r"обратимся\s+ещё",
            r"обратимся\s+еще",
            r"благодарим",
            r"очень\s+довольны",
        ],
        "agent": [
            r"рады,?\s+что\s+понравилось",
            r"спасибо,?\s+что\s+выбрали",
            r"до\s+(?:новых\s+встреч|скорой\s+встречи)",
            r"ждём\s+(?:вас\s+)?снова",
            r"ждем\s+(?:вас\s+)?снова",
        ]
    },
    "lost": {
        "client": [
            r"дорого",
            r"дороговато",
            r"передумал[аи]?",
            r"отменяем",
            r"отмена",
            r"в\s+другой\s+раз",
            r"не\s+(?:подходит|устраивает)",
            r"нашли\s+(?:дешевле|другое)",
            r"уже\s+(?:забронировали|заказали)\s+(?:в\s+)?(?:другом|другой)",
            r"не\s+(?:нужно|актуально)",
            r"планы\s+изменились",
            r"не\s+получится",
            r"к\s+сожалению",
        ],
        "agent": []
    }
}

# Причины потери
LOST_REASONS_PATTERNS = {
    "price": [
        r"дорого", r"дороговато", r"цена\s+(?:высокая|не\s+устраивает)",
        r"нашли\s+дешевле", r"бюджет", r"не\s+(?:потянем|укладываемся)"
    ],
    "no_response": [],  # Определяется по времени
    "competitor": [
        r"(?:забронировали|заказали|нашли)\s+(?:в\s+)?(?:другом|другой|у\s+других)",
        r"другое\s+(?:агентство|компания)",
        r"через\s+(?:другую|другое|других)"
    ],
    "cancelled": [
        r"отмена", r"отменяем", r"отменить",
        r"передумал", r"планы\s+изменились", r"не\s+получится"
    ],
    "timing": [
        r"в\s+другой\s+раз", r"не\s+в\s+(?:эти|эту)\s+(?:даты|дату)",
        r"перенести", r"позже", r"не\s+(?:успеваем|успеем)"
    ]
}


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_contacts(filepath: Path) -> List[Dict]:
    """Загрузка контактов из JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл контактов не найден: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Поддержка разных форматов: список или {"contacts": [...]}
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "contacts" in data:
        return data["contacts"]
    return []


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


def load_operations(filepath: Path) -> List[Dict]:
    """Загрузка операций из JSON файла."""
    if not filepath.exists():
        print(f"[i] Файл операций не найден: {filepath} (будет использован анализ сообщений)")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    return []


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ АНАЛИЗА
# ═══════════════════════════════════════════════════════════════

def detect_stage_in_message(text: str, is_from_client: bool) -> Optional[str]:
    """
    Определяет стадию воронки по тексту сообщения.

    Args:
        text: Текст сообщения
        is_from_client: True если сообщение от клиента, False если от агента

    Returns:
        Название стадии или None
    """
    text_lower = text.lower()
    sender_key = "client" if is_from_client else "agent"

    # Проверяем стадии в порядке приоритета (от завершающих к начальным)
    stage_priority = ["completed", "payment", "booking", "lost", "quote", "inquiry"]

    for stage in stage_priority:
        patterns = STAGE_PATTERNS[stage].get(sender_key, [])
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return stage

    return None


def detect_lost_reason(messages: List[Dict]) -> str:
    """Определяет причину потери клиента."""
    combined_text = " ".join(m.get("text", "") for m in messages).lower()

    for reason, patterns in LOST_REASONS_PATTERNS.items():
        if reason == "no_response":
            continue  # Обрабатывается отдельно
        for pattern in patterns:
            if re.search(pattern, combined_text):
                return reason

    return "no_response"


def detect_product_type(messages: List[Dict]) -> str:
    """Определяет тип продукта из сообщений."""
    combined_text = " ".join(m.get("text", "") for m in messages).lower()

    for product, keywords in PRODUCT_TYPES.items():
        for keyword in keywords:
            if keyword in combined_text:
                return product

    return "other"


def get_month_key(date_str: str) -> str:
    """Преобразует дату в ключ месяца YYYY-MM."""
    if not date_str:
        return "unknown"

    # Поддержка разных форматов даты
    formats = ["%Y-%m-%d", "%d.%m.%Y", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y"]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str[:10], fmt[:min(len(fmt), 10)])
            return dt.strftime("%Y-%m")
        except ValueError:
            continue

    return "unknown"


def analyze_contact_funnel(
    contact: Dict,
    messages: List[Dict],
    operations: List[Dict],
    today: datetime
) -> Tuple[str, Optional[str], str]:
    """
    Анализирует воронку для одного контакта.

    Returns:
        (stage, lost_reason, product_type)
    """
    if not messages:
        return "inquiry", None, "other"

    # Сортируем сообщения по дате
    sorted_messages = sorted(messages, key=lambda m: m.get("timestamp", "") or m.get("date", ""))

    # Определяем достигнутые стадии
    reached_stages = set()
    last_message_date = None

    for msg in sorted_messages:
        text = msg.get("text", "")
        is_from_client = msg.get("is_from_me", False) is False or msg.get("sender_type") == "client"

        # Пробуем определить отправителя
        sender = msg.get("sender", "")
        if sender and contact.get("name"):
            is_from_client = contact.get("name") in sender

        stage = detect_stage_in_message(text, is_from_client)
        if stage:
            reached_stages.add(stage)

        # Запоминаем дату последнего сообщения
        msg_date = msg.get("timestamp") or msg.get("date")
        if msg_date:
            last_message_date = msg_date

    # Проверяем операции (если есть completed операции)
    contact_phone = contact.get("phone", "")
    contact_jid = contact.get("jid", "")

    for op in operations:
        op_phone = op.get("phone", "")
        if op_phone and (op_phone == contact_phone or contact_phone in op_phone):
            op_status = op.get("status", "").lower()
            if op_status == "completed":
                reached_stages.add("completed")
                reached_stages.add("payment")
            elif op_status in ["paid", "payment"]:
                reached_stages.add("payment")
            elif op_status in ["booked", "booking", "confirmed"]:
                reached_stages.add("booking")

    # Определяем финальную стадию
    stage_hierarchy = ["completed", "payment", "booking", "quote", "inquiry"]

    final_stage = "inquiry"
    for stage in stage_hierarchy:
        if stage in reached_stages:
            final_stage = stage
            break

    # Проверяем на потерю
    lost_reason = None
    if "lost" in reached_stages:
        final_stage = "lost"
        lost_reason = detect_lost_reason(sorted_messages)
    elif final_stage not in ["completed", "payment"] and last_message_date:
        # Проверяем неактивность
        try:
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y"]:
                try:
                    last_dt = datetime.strptime(last_message_date[:10], fmt[:10])
                    if (today - last_dt).days > INACTIVITY_THRESHOLD_DAYS:
                        final_stage = "lost"
                        lost_reason = "no_response"
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    # Определяем тип продукта
    product_type = detect_product_type(sorted_messages)

    return final_stage, lost_reason, product_type


def group_messages_by_contact(messages: List[Dict], contacts: List[Dict]) -> Dict[str, List[Dict]]:
    """Группирует сообщения по контактам."""
    grouped = defaultdict(list)

    # Создаём индекс для быстрого поиска
    jid_to_contact = {}
    phone_to_contact = {}

    for contact in contacts:
        jid = contact.get("jid", "")
        phone = contact.get("phone", "")
        if jid:
            jid_to_contact[jid] = contact
        if phone:
            phone_to_contact[phone] = contact

    for msg in messages:
        # Пробуем найти контакт по разным полям
        contact_id = msg.get("contact_id") or msg.get("jid") or msg.get("chat_jid")

        if contact_id:
            grouped[contact_id].append(msg)
        else:
            # Пробуем по телефону
            phone = msg.get("phone")
            if phone and phone in phone_to_contact:
                contact = phone_to_contact[phone]
                grouped[contact.get("jid", phone)].append(msg)

    return grouped


# ═══════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def build_sales_funnel(
    contacts: List[Dict],
    messages: List[Dict],
    operations: List[Dict]
) -> Dict:
    """
    Строит воронку продаж.

    Returns:
        Словарь с данными воронки
    """
    today = datetime.now()

    # Группируем сообщения по контактам
    messages_by_contact = group_messages_by_contact(messages, contacts)

    # Инициализация структур данных
    funnel_counts = defaultdict(int)
    lost_reasons = defaultdict(int)
    by_product = defaultdict(lambda: defaultdict(int))
    by_month = defaultdict(lambda: defaultdict(int))
    contacts_by_stage = defaultdict(list)

    # Обрабатываем только клиентов
    client_contacts = [c for c in contacts if c.get("type") in ["клиенты", "clients", "customer"]]

    if not client_contacts:
        # Если нет фильтра по типу, берём всех
        client_contacts = contacts

    print(f"[i] Анализ {len(client_contacts)} контактов...")

    for contact in client_contacts:
        jid = contact.get("jid", "")
        phone = contact.get("phone", "")
        contact_id = jid or phone

        if not contact_id:
            continue

        # Получаем сообщения контакта
        contact_messages = messages_by_contact.get(jid, [])
        if not contact_messages and phone:
            contact_messages = messages_by_contact.get(phone, [])

        # Анализируем воронку
        stage, lost_reason, product_type = analyze_contact_funnel(
            contact, contact_messages, operations, today
        )

        # Обновляем счётчики
        funnel_counts[stage] += 1

        if stage == "lost" and lost_reason:
            lost_reasons[lost_reason] += 1

        # По продуктам
        by_product[product_type][stage] += 1

        # По месяцам (используем дату первого сообщения)
        first_date = contact.get("first_message", "")
        if not first_date and contact_messages:
            first_date = contact_messages[0].get("timestamp") or contact_messages[0].get("date", "")
        month_key = get_month_key(first_date)
        if month_key != "unknown":
            by_month[month_key][stage] += 1

        # Сохраняем контакт в стадию
        contacts_by_stage[stage].append(contact_id)

    # Формируем итоговую структуру
    total_inquiry = sum(funnel_counts.values())

    # Расчёт показателей воронки
    funnel = {}
    prev_count = total_inquiry
    stage_order = ["inquiry", "quote", "booking", "payment", "completed", "lost"]

    for stage in stage_order:
        count = funnel_counts.get(stage, 0)
        rate = count / total_inquiry if total_inquiry > 0 else 0

        funnel[stage] = {
            "count": count,
            "rate": round(rate, 4)
        }

        # Конверсия относительно предыдущей стадии
        if stage not in ["inquiry", "lost"] and prev_count > 0:
            conversion = count / prev_count if prev_count > 0 else 0
            funnel[stage]["conversion"] = round(conversion, 4)
            prev_count = count

    # Форматируем by_product
    by_product_formatted = {}
    for product, stages in by_product.items():
        by_product_formatted[product] = dict(stages)

    # Форматируем by_month
    by_month_formatted = {}
    for month, stages in sorted(by_month.items()):
        by_month_formatted[month] = dict(stages)

    result = {
        "funnel": funnel,
        "lost_reasons": dict(lost_reasons),
        "by_product": by_product_formatted,
        "by_month": by_month_formatted,
        "contacts_by_stage": {k: v for k, v in contacts_by_stage.items()},
        "meta": {
            "generated_at": today.isoformat(),
            "total_contacts": len(client_contacts),
            "total_messages": len(messages),
            "inactivity_threshold_days": INACTIVITY_THRESHOLD_DAYS
        }
    }

    return result


def generate_markdown_report(funnel_data: Dict) -> str:
    """Генерирует Markdown отчёт по воронке."""
    lines = []
    lines.append("# Воронка продаж")
    lines.append("")
    lines.append(f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    lines.append("")

    # Основная воронка
    lines.append("## Стадии воронки")
    lines.append("")
    lines.append("```")

    funnel = funnel_data.get("funnel", {})
    stage_names = {
        "inquiry": "Запрос",
        "quote": "Расчёт",
        "booking": "Бронь",
        "payment": "Оплата",
        "completed": "Выполнено",
        "lost": "Потеряно"
    }

    max_count = max((v.get("count", 0) for v in funnel.values()), default=1)
    bar_width = 40

    for stage in ["inquiry", "quote", "booking", "payment", "completed"]:
        data = funnel.get(stage, {})
        count = data.get("count", 0)
        rate = data.get("rate", 0)
        conversion = data.get("conversion")

        bar_len = int((count / max_count) * bar_width) if max_count > 0 else 0
        bar = "█" * bar_len + "░" * (bar_width - bar_len)

        conv_str = f" (конв. {conversion:.0%})" if conversion else ""
        lines.append(f"{stage_names[stage]:12} {bar} {count:5} ({rate:6.1%}){conv_str}")

    lines.append("```")
    lines.append("")

    # Потерянные
    lost_data = funnel.get("lost", {})
    lost_count = lost_data.get("count", 0)
    lost_rate = lost_data.get("rate", 0)
    lines.append(f"**Потеряно:** {lost_count} ({lost_rate:.1%})")
    lines.append("")

    # Причины потерь
    lost_reasons = funnel_data.get("lost_reasons", {})
    if lost_reasons:
        lines.append("### Причины потерь")
        lines.append("")
        lines.append("| Причина | Количество | % |")
        lines.append("|---------|------------|---|")

        reason_names = {
            "price": "Цена",
            "no_response": "Нет ответа",
            "competitor": "Конкурент",
            "cancelled": "Отмена",
            "timing": "Неподходящее время"
        }

        total_lost = sum(lost_reasons.values()) or 1
        for reason, count in sorted(lost_reasons.items(), key=lambda x: x[1], reverse=True):
            name = reason_names.get(reason, reason)
            pct = count / total_lost * 100
            lines.append(f"| {name} | {count} | {pct:.0f}% |")
        lines.append("")

    # По продуктам
    by_product = funnel_data.get("by_product", {})
    if by_product:
        lines.append("## По продуктам")
        lines.append("")
        lines.append("| Продукт | Запросов | Выполнено | Конверсия |")
        lines.append("|---------|----------|-----------|-----------|")

        product_names = {
            "tour": "Экскурсии",
            "transfer": "Трансферы",
            "yacht": "Яхты",
            "tickets": "Билеты",
            "car_rental": "Аренда авто",
            "catering": "Кейтеринг",
            "other": "Другое"
        }

        for product, stages in sorted(by_product.items()):
            name = product_names.get(product, product)
            inquiry = stages.get("inquiry", 0) + stages.get("quote", 0) + stages.get("booking", 0) + stages.get("payment", 0) + stages.get("completed", 0) + stages.get("lost", 0)
            completed = stages.get("completed", 0)
            conv = completed / inquiry * 100 if inquiry > 0 else 0
            lines.append(f"| {name} | {inquiry} | {completed} | {conv:.0f}% |")
        lines.append("")

    # По месяцам
    by_month = funnel_data.get("by_month", {})
    if by_month:
        lines.append("## По месяцам")
        lines.append("")
        lines.append("| Месяц | Запросов | Выполнено | Конверсия |")
        lines.append("|-------|----------|-----------|-----------|")

        for month, stages in sorted(by_month.items(), reverse=True)[:12]:  # Последние 12 месяцев
            inquiry = sum(stages.values())
            completed = stages.get("completed", 0)
            conv = completed / inquiry * 100 if inquiry > 0 else 0
            lines.append(f"| {month} | {inquiry} | {completed} | {conv:.0f}% |")
        lines.append("")

    # Метаданные
    meta = funnel_data.get("meta", {})
    lines.append("---")
    lines.append("")
    lines.append(f"*Всего контактов: {meta.get('total_contacts', 0)}*")
    lines.append(f"*Порог неактивности: {meta.get('inactivity_threshold_days', 7)} дней*")

    return "\n".join(lines)


def save_results(funnel_data: Dict, json_path: Path, md_path: Path):
    """Сохраняет результаты в файлы."""
    # Создаём директории если нужно
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    # JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(funnel_data, f, ensure_ascii=False, indent=2)
    print(f"[+] JSON сохранён: {json_path}")

    # Markdown
    md_content = generate_markdown_report(funnel_data)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"[+] MD сохранён: {md_path}")


def main():
    global INACTIVITY_THRESHOLD_DAYS

    parser = argparse.ArgumentParser(
        description="Построение воронки продаж из WhatsApp чатов"
    )
    parser.add_argument(
        "--messages", "-m",
        default=str(MESSAGES_FILE),
        help="Путь к файлу сообщений (JSONL)"
    )
    parser.add_argument(
        "--contacts", "-c",
        default=str(CONTACTS_FILE),
        help="Путь к файлу контактов (JSON)"
    )
    parser.add_argument(
        "--operations", "-p",
        default=str(OPERATIONS_FILE),
        help="Путь к файлу операций (JSON)"
    )
    parser.add_argument(
        "--output-json", "-o",
        default=str(OUTPUT_JSON),
        help="Путь к выходному JSON файлу"
    )
    parser.add_argument(
        "--output-md",
        default=str(OUTPUT_MD),
        help="Путь к выходному MD файлу"
    )
    parser.add_argument(
        "--inactivity-days", "-d",
        type=int,
        default=INACTIVITY_THRESHOLD_DAYS,
        help=f"Порог неактивности для 'lost' (дней, по умолчанию {INACTIVITY_THRESHOLD_DAYS})"
    )

    args = parser.parse_args()

    # Обновляем порог неактивности
    INACTIVITY_THRESHOLD_DAYS = args.inactivity_days

    print("=" * 60)
    print("ПОСТРОЕНИЕ ВОРОНКИ ПРОДАЖ")
    print("=" * 60)

    # Загрузка данных
    print("\n[1] Загрузка данных...")
    contacts = load_contacts(Path(args.contacts))
    print(f"    Контактов: {len(contacts)}")

    messages = load_messages(Path(args.messages))
    print(f"    Сообщений: {len(messages)}")

    operations = load_operations(Path(args.operations))
    print(f"    Операций: {len(operations)}")

    if not contacts:
        print("\n[!] Нет контактов для анализа. Проверьте файл контактов.")
        return

    # Построение воронки
    print("\n[2] Анализ воронки...")
    funnel_data = build_sales_funnel(contacts, messages, operations)

    # Вывод статистики
    print("\n[3] Результаты:")
    funnel = funnel_data.get("funnel", {})
    for stage, data in funnel.items():
        count = data.get("count", 0)
        rate = data.get("rate", 0)
        print(f"    {stage:12}: {count:5} ({rate:.1%})")

    # Сохранение
    print("\n[4] Сохранение...")
    save_results(
        funnel_data,
        Path(args.output_json),
        Path(args.output_md)
    )

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)


if __name__ == "__main__":
    main()
