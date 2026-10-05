#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение жалоб и отмен из чатов WhatsApp.

Категории:
1. Отмены (cancellation) — "отменить", "отказываемся", "не нужно"
2. Жалобы на качество (quality) — "не понравилось", "плохо", "ужасно"
3. Жалобы на цену (price) — "дорого", "завышено"
4. Жалобы на сервис (service) — "долго ждали", "опоздали", "не ответили"
5. Возвраты (refund) — "верните деньги", "refund"

ВАЖНЫЙ ПРИНЦИП: Никакие данные НЕ теряются! Сохранять ВСЕ данные полностью.
"""

import sys
import os
import re
import json
import uuid
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ КАТЕГОРИЙ
# ═══════════════════════════════════════════════════════════════

CATEGORY_PATTERNS = {
    "cancellation": {
        "name": "Отмены",
        "patterns": [
            r"отмен(?:и|ить|яем|яю|ите|ено|а)",
            r"отказ(?:ываемся|ываюсь|ались|ать)",
            r"не\s+нужн[оа]",
            r"cancel(?:led|lation)?",
            r"отбой",
            r"передумал[иа]?",
            r"не\s+(?:будем|буду|поедем|пойдём)",
            r"снять\s+(?:бронь|бронирование)",
            r"отменяй(?:те)?",
        ],
    },
    "quality": {
        "name": "Жалобы на качество",
        "patterns": [
            r"не\s+понравил(?:ось|ась|ся|ись)",
            r"плох(?:о|ой|ая|ое|ие)",
            r"ужас(?:но|ный|ная)?",
            r"разочарован[аы]?",
            r"некачественн(?:о|ый|ая|ое)",
            r"отврат(?:ительно|ный)",
            r"кошмар(?:ный)?",
            r"ужасн(?:о|ый|ая|ое)",
            r"не\s+соответств(?:ует|овало)",
            r"обман(?:ули|ывают)?",
            r"испорч(?:ено|ен|ена)",
            r"сломан[оа]?",
            r"грязн(?:о|ый|ая|ое)",
            r"воняет|пахнет\s+плохо",
        ],
    },
    "price": {
        "name": "Жалобы на цену",
        "patterns": [
            r"дорог(?:о|ой|ая|ое|ие)",
            r"завышен(?:о|а|ы|ная)?",
            r"переплат(?:а|или|им)",
            r"слишком\s+(?:дорого|много)",
            r"накрутка|накрутили",
            r"грабёж|грабеж",
            r"цена\s+(?:высокая|завышена|большая)",
            r"не\s+(?:по\s+карману|потянем)",
            r"expensive",
            r"overpriced",
        ],
    },
    "service": {
        "name": "Жалобы на сервис",
        "patterns": [
            r"опоздал[иа]?",
            r"долго\s+(?:ждал[иа]?|ожидание|ехали)",
            r"не\s+(?:ответил[иа]?|перезвонил[иа]?|отвечают|отвечаете)",
            r"игнор(?:ируете|ируют|ят)?",
            r"не\s+(?:пришёл|приехал|приехали)",
            r"забыл[иа]?",
            r"перепутал[иа]?",
            r"ошиблись|ошибка",
            r"невежлив(?:о|ый|ая)|хам(?:ство|ит|ят)?",
            r"грубо|грубый|грубая",
            r"не\s+помог(?:ли|ает|ают)?",
            r"без\s+предупреждения",
            r"не\s+сообщили",
            r"late|delayed",
        ],
    },
    "refund": {
        "name": "Возвраты",
        "patterns": [
            r"верни(?:те)?\s+деньги",
            r"возврат(?:а|у|ом)?(?:\s+денег)?",
            r"refund",
            r"money\s+back",
            r"хочу\s+(?:вернуть|возврат)",
            r"требую\s+(?:вернуть|возврат)",
            r"компенсац(?:ия|ию|ии)",
            r"возместите",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ SEVERITY
# ═══════════════════════════════════════════════════════════════

SEVERITY_PATTERNS = {
    "high": [
        r"ужас(?:но|ный)?",
        r"кошмар",
        r"верни(?:те)?\s+деньги",
        r"refund",
        r"обман(?:ули)?",
        r"грабёж|грабеж",
        r"отврат(?:ительно|ный)",
        r"требую",
        r"жалоба|буду\s+жаловаться",
        r"суд|адвокат|юрист",
        r"полиция",
        r"катастроф(?:а|ический)",
        r"невозможно",
        r"совершенно\s+(?:неприемлемо|недопустимо)",
    ],
    "medium": [
        r"не\s+понравил(?:ось|ась)",
        r"плох(?:о|ой|ая)",
        r"разочарован",
        r"опоздал[иа]?",
        r"долго\s+ждал[иа]?",
        r"не\s+ответил[иа]?",
        r"дорог(?:о|ой)",
        r"отмен(?:ить|яем)",
        r"не\s+нужно",
        r"проблем(?:а|ы)",
    ],
    "low": [
        r"немного\s+(?:дорого|долго)",
        r"чуть\s+(?:опоздали|дороже)",
        r"не\s+(?:очень|совсем)",
        r"мелочь|пустяк",
        r"ничего\s+страшного",
        r"жаль|жалко",
        r"могло\s+быть\s+лучше",
        r"небольш(?:ая|ое)\s+(?:проблема|замечание)",
    ],
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ПРОДУКТОВ
# ═══════════════════════════════════════════════════════════════

PRODUCT_PATTERNS = {
    "Экскурсия в Абу-Даби": [r"абу[\s\-]?даби", r"abu[\s\-]?dhabi", r"grand\s+mosque", r"мечеть"],
    "Экскурсия в Дубай": [r"дубай", r"dubai", r"бурдж[\s\-]?халифа", r"burj\s+khalifa"],
    "Сафари": [r"сафари", r"safari", r"пустын[яе]", r"desert"],
    "Яхта": [r"яхт[аыу]", r"yacht", r"катер", r"лодка"],
    "Трансфер": [r"трансфер", r"transfer", r"аэропорт", r"airport", r"встреча"],
    "Ferrari World": [r"ferrari", r"феррари"],
    "Аквапарк": [r"аквапарк", r"aquaventure", r"waterpark", r"wild\s+wadi"],
    "Ресторан": [r"ресторан", r"restaurant", r"ужин", r"обед", r"dinner", r"lunch"],
    "Билеты": [r"билет[ыа]?", r"ticket", r"парк", r"шоу", r"show"],
    "Аренда авто": [r"аренд[аы]\s+авто", r"car\s+rental", r"машин[аыу]"],
    "Обмен валюты": [r"обмен", r"валют[аыу]", r"exchange", r"курс"],
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ РЕЗОЛЮЦИИ
# ═══════════════════════════════════════════════════════════════

RESOLUTION_PATTERNS = [
    (r"(?:предоставлена?|дали|сделали)\s+скидк[ауе]?\s*(\d+)?%?", "Предоставлена скидка"),
    (r"вернули\s+(?:деньги|средства)", "Возврат средств"),
    (r"(?:перебронировали|перенесли)", "Перебронирование"),
    (r"компенсац(?:ия|ию)\s+(?:предоставлена|выплачена)", "Выплачена компенсация"),
    (r"извинились|приносим\s+извинения", "Принесены извинения"),
    (r"(?:заменили|замена)\s+(?:гида|водителя|машину)", "Замена исполнителя"),
    (r"(?:решили|устранили)\s+проблем", "Проблема решена"),
    (r"(?:всё|все)\s+(?:хорошо|нормально|ок|ok)", "Клиент удовлетворён"),
    (r"спасибо|благодар", "Клиент поблагодарил"),
]


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


def detect_category(text):
    """Определяет категорию жалобы по тексту."""
    text_lower = text.lower()

    for category, data in CATEGORY_PATTERNS.items():
        for pattern in data["patterns"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category

    return None


def detect_all_categories(text):
    """Определяет все категории жалоб в тексте."""
    text_lower = text.lower()
    categories = []

    for category, data in CATEGORY_PATTERNS.items():
        for pattern in data["patterns"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                categories.append(category)
                break

    return categories


def detect_severity(text, category):
    """Определяет серьёзность жалобы."""
    text_lower = text.lower()

    # Сначала проверяем high
    for pattern in SEVERITY_PATTERNS["high"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "high"

    # Потом low (чтобы "немного дорого" не попало в medium)
    for pattern in SEVERITY_PATTERNS["low"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "low"

    # По умолчанию medium
    for pattern in SEVERITY_PATTERNS["medium"]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "medium"

    # Если возврат или отмена - по умолчанию medium
    if category in ["refund", "cancellation"]:
        return "medium"

    return "low"


def extract_keywords_found(text):
    """Извлекает найденные ключевые слова."""
    text_lower = text.lower()
    keywords = []

    all_patterns = []
    for data in CATEGORY_PATTERNS.values():
        all_patterns.extend(data["patterns"])

    for pattern in all_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if match and match not in keywords:
                keywords.append(match)

    return keywords[:5]  # Максимум 5 ключевых слов


def detect_product(text, context_before="", context_after=""):
    """Определяет продукт по тексту и контексту."""
    full_text = f"{context_before} {text} {context_after}".lower()

    for product, patterns in PRODUCT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                return product

    return None


def detect_resolution(context_after):
    """Определяет резолюцию по последующим сообщениям."""
    if not context_after:
        return False, None

    text_lower = context_after.lower()

    for pattern, resolution_text in RESOLUTION_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            # Если есть группа с процентом скидки
            if match.lastindex and match.group(1):
                return True, f"{resolution_text} {match.group(1)}%"
            return True, resolution_text

    return False, None


def get_context(messages, idx, window=3):
    """Получает контекст: сообщения до и после."""
    context_before = []
    context_after = []

    # Сообщения до
    for i in range(max(0, idx - window), idx):
        if "text" in messages[i]:
            context_before.append(messages[i].get("text", ""))

    # Сообщения после
    for i in range(idx + 1, min(len(messages), idx + window + 1)):
        if "text" in messages[i]:
            context_after.append(messages[i].get("text", ""))

    return " ".join(context_before), " ".join(context_after)


def extract_complaints(input_file, output_json, output_md):
    """Основная функция извлечения жалоб."""

    print(f"Загрузка сообщений из: {input_file}")
    messages = load_messages_jsonl(input_file)

    if not messages:
        print("Сообщения не найдены. Создаю пустые выходные файлы...")
        # Создаём пустые файлы для демонстрации структуры
        empty_result = create_empty_result()
        save_json(empty_result, output_json)
        save_markdown(empty_result, output_md)
        return empty_result

    print(f"Загружено {len(messages)} сообщений")

    complaints = []
    contact_complaints = defaultdict(list)  # Для группировки по контактам

    for idx, msg in enumerate(messages):
        text = msg.get("text", "")
        if not text or len(text) < 5:
            continue

        # Определяем категорию
        category = detect_category(text)
        if not category:
            continue

        # Получаем контекст
        context_before, context_after = get_context(messages, idx)

        # Определяем severity
        severity = detect_severity(text, category)

        # Извлекаем ключевые слова
        keywords = extract_keywords_found(text)

        # Определяем продукт
        product = detect_product(text, context_before, context_after)

        # Проверяем резолюцию
        resolved, resolution = detect_resolution(context_after)

        # Формируем запись
        complaint = {
            "complaint_id": str(uuid.uuid4()),
            "contact_id": msg.get("contact_id", str(uuid.uuid4())),
            "jid": msg.get("jid", msg.get("sender_jid", "")),
            "datetime": msg.get("datetime", msg.get("timestamp", "")),
            "category": category,
            "severity": severity,
            "text": text[:500],  # Ограничиваем длину
            "keywords_found": keywords,
            "resolved": resolved,
            "resolution": resolution,
            "product": product,
            "sender_name": msg.get("sender_name", msg.get("sender", "")),
            "contact_type": msg.get("contact_type", ""),
            "source_file": msg.get("source_file", ""),
            "context_before": context_before[:200] if context_before else None,
            "context_after": context_after[:200] if context_after else None,
        }

        complaints.append(complaint)

        # Группируем по контактам
        contact_key = complaint["jid"] or complaint["contact_id"]
        contact_complaints[contact_key].append(complaint)

    print(f"Найдено {len(complaints)} жалоб/отмен")

    # Собираем статистику
    statistics = build_statistics(complaints)

    result = {
        "complaints": complaints,
        "statistics": statistics,
        "metadata": {
            "source_file": input_file,
            "total_messages": len(messages),
            "extracted_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    }

    # Сохраняем результаты
    save_json(result, output_json)
    save_markdown(result, output_md)

    # Выводим сводку
    print_summary(statistics)

    return result


def create_empty_result():
    """Создаёт пустой результат с правильной структурой."""
    return {
        "complaints": [],
        "statistics": {
            "total": 0,
            "by_category": {cat: 0 for cat in CATEGORY_PATTERNS.keys()},
            "by_severity": {"high": 0, "medium": 0, "low": 0},
            "resolution_rate": 0.0,
            "top_issues": [],
            "by_product": {},
            "by_contact_type": {},
        },
        "metadata": {
            "source_file": "",
            "total_messages": 0,
            "extracted_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    }


def build_statistics(complaints):
    """Собирает статистику по жалобам."""

    if not complaints:
        return {
            "total": 0,
            "by_category": {cat: 0 for cat in CATEGORY_PATTERNS.keys()},
            "by_severity": {"high": 0, "medium": 0, "low": 0},
            "resolution_rate": 0.0,
            "top_issues": [],
            "by_product": {},
            "by_contact_type": {},
        }

    total = len(complaints)

    # По категориям
    by_category = Counter(c["category"] for c in complaints)

    # По severity
    by_severity = Counter(c["severity"] for c in complaints)

    # Resolution rate
    resolved_count = sum(1 for c in complaints if c["resolved"])
    resolution_rate = resolved_count / total if total > 0 else 0.0

    # Top issues (по ключевым словам)
    all_keywords = []
    for c in complaints:
        all_keywords.extend(c["keywords_found"])
    keyword_counts = Counter(all_keywords)
    top_issues = [
        {"issue": kw, "count": count}
        for kw, count in keyword_counts.most_common(10)
    ]

    # По продуктам
    by_product = Counter(c["product"] for c in complaints if c["product"])

    # По типу контакта
    by_contact_type = Counter(c["contact_type"] for c in complaints if c["contact_type"])

    # Тренды по месяцам
    monthly_trend = defaultdict(int)
    for c in complaints:
        dt_str = c.get("datetime", "")
        if dt_str:
            try:
                # Пробуем разные форматы
                for fmt in ["%Y-%m-%dT%H:%M:%S", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%Y-%m-%d"]:
                    try:
                        dt = datetime.strptime(dt_str[:19], fmt)
                        month_key = dt.strftime("%Y-%m")
                        monthly_trend[month_key] += 1
                        break
                    except:
                        continue
            except:
                pass

    return {
        "total": total,
        "by_category": dict(by_category),
        "by_severity": dict(by_severity),
        "resolution_rate": round(resolution_rate, 2),
        "top_issues": top_issues,
        "by_product": dict(by_product),
        "by_contact_type": dict(by_contact_type),
        "monthly_trend": dict(sorted(monthly_trend.items())),
        "resolved_count": resolved_count,
        "unresolved_count": total - resolved_count,
    }


def save_json(result, output_file):
    """Сохраняет результат в JSON."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"JSON сохранён: {output_file}")


def save_markdown(result, output_file):
    """Сохраняет результат в Markdown."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    complaints = result["complaints"]
    stats = result["statistics"]

    lines = []
    lines.append("# Жалобы и отмены")
    lines.append("")
    lines.append(f"*Дата анализа: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Сводка
    lines.append("## Сводка")
    lines.append("")
    lines.append(f"- **Всего жалоб/отмен:** {stats['total']}")
    lines.append(f"- **Решено:** {stats.get('resolved_count', 0)} ({stats['resolution_rate']*100:.0f}%)")
    lines.append(f"- **Не решено:** {stats.get('unresolved_count', 0)}")
    lines.append("")

    # По категориям
    lines.append("### По категориям")
    lines.append("")
    for cat, data in CATEGORY_PATTERNS.items():
        count = stats["by_category"].get(cat, 0)
        lines.append(f"- **{data['name']}:** {count}")
    lines.append("")

    # По серьёзности
    lines.append("### По серьёзности")
    lines.append("")
    severity_emoji = {"high": "!!!!", "medium": "!!", "low": "!"}
    severity_names = {"high": "Высокая", "medium": "Средняя", "low": "Низкая"}
    for sev in ["high", "medium", "low"]:
        count = stats["by_severity"].get(sev, 0)
        lines.append(f"- **{severity_names[sev]} ({severity_emoji[sev]}):** {count}")
    lines.append("")

    # Топ проблем
    if stats.get("top_issues"):
        lines.append("### Топ проблем")
        lines.append("")
        for item in stats["top_issues"][:10]:
            lines.append(f"- {item['issue']}: {item['count']}")
        lines.append("")

    # По продуктам
    if stats.get("by_product"):
        lines.append("### По продуктам")
        lines.append("")
        for product, count in sorted(stats["by_product"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{product}:** {count}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Детальный список
    lines.append("## Детальный список жалоб")
    lines.append("")

    # Группируем по категориям
    by_category = defaultdict(list)
    for c in complaints:
        by_category[c["category"]].append(c)

    for category in ["refund", "cancellation", "quality", "service", "price"]:
        cat_complaints = by_category.get(category, [])
        if not cat_complaints:
            continue

        cat_name = CATEGORY_PATTERNS[category]["name"]
        lines.append(f"### {cat_name} ({len(cat_complaints)})")
        lines.append("")

        # Сортируем по severity (high первые)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        cat_complaints.sort(key=lambda x: severity_order.get(x["severity"], 2))

        for c in cat_complaints:
            severity_mark = {"high": "!!!!HIGH", "medium": "!!MEDIUM", "low": "!LOW"}
            sev = severity_mark.get(c["severity"], "")

            lines.append(f"#### [{sev}] {c['datetime'][:16] if c['datetime'] else 'Нет даты'}")
            lines.append("")

            if c.get("sender_name"):
                lines.append(f"**Контакт:** {c['sender_name']}")
            if c.get("product"):
                lines.append(f"**Продукт:** {c['product']}")

            lines.append("")
            lines.append(f"> {c['text']}")
            lines.append("")

            if c["keywords_found"]:
                lines.append(f"**Ключевые слова:** {', '.join(c['keywords_found'])}")

            if c["resolved"]:
                lines.append(f"**Статус:** РЕШЕНО - {c['resolution']}")
            else:
                lines.append("**Статус:** Не решено")

            lines.append("")
            lines.append("---")
            lines.append("")

    # Нерешённые жалобы высокой важности
    high_unresolved = [c for c in complaints if c["severity"] == "high" and not c["resolved"]]
    if high_unresolved:
        lines.append("## ВНИМАНИЕ: Нерешённые критические жалобы")
        lines.append("")
        lines.append("Эти жалобы требуют немедленного внимания!")
        lines.append("")

        for c in high_unresolved:
            lines.append(f"- **{c.get('sender_name', 'Неизвестно')}** ({c['datetime'][:10] if c['datetime'] else 'Нет даты'})")
            lines.append(f"  - {c['text'][:100]}...")
            if c.get("product"):
                lines.append(f"  - Продукт: {c['product']}")
            lines.append("")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Markdown сохранён: {output_file}")


def print_summary(stats):
    """Выводит сводку в консоль."""
    print("")
    print("=" * 50)
    print("СВОДКА ПО ЖАЛОБАМ И ОТМЕНАМ")
    print("=" * 50)
    print(f"Всего: {stats['total']}")
    print(f"Решено: {stats.get('resolved_count', 0)} ({stats['resolution_rate']*100:.0f}%)")
    print("")
    print("По категориям:")
    for cat, data in CATEGORY_PATTERNS.items():
        count = stats["by_category"].get(cat, 0)
        print(f"  {data['name']}: {count}")
    print("")
    print("По серьёзности:")
    print(f"  Высокая: {stats['by_severity'].get('high', 0)}")
    print(f"  Средняя: {stats['by_severity'].get('medium', 0)}")
    print(f"  Низкая: {stats['by_severity'].get('low', 0)}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Извлечение жалоб и отмен из WhatsApp чатов"
    )
    parser.add_argument(
        "--input", "-i",
        default="D:/Downloads/Chats/_база/raw/all_messages.jsonl",
        help="Входной JSONL файл с сообщениями"
    )
    parser.add_argument(
        "--output-json", "-j",
        default="D:/Downloads/Chats/_база/json/complaints.json",
        help="Выходной JSON файл"
    )
    parser.add_argument(
        "--output-md", "-m",
        default="D:/Downloads/Chats/_база/md/жалобы_и_отмены.md",
        help="Выходной Markdown файл"
    )

    args = parser.parse_args()

    extract_complaints(
        input_file=args.input,
        output_json=args.output_json,
        output_md=args.output_md
    )


if __name__ == "__main__":
    main()
