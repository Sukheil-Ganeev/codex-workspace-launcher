#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Построение профилей клиентов на основе анализа чатов.
Извлекает личностные характеристики, предпочтения и статистику из переписки.
"""

import sys
import os
import json
import re
import uuid
import argparse
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Any

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

CONTACTS_FILE = Path("D:/Downloads/Chats/_база/json/contacts.json")
MESSAGES_FILE = Path("D:/Downloads/Chats/_база/raw/all_messages.jsonl")
OUTPUT_FILE = Path("D:/Downloads/Chats/_база/json/profiles.json")

# Типы контактов для анализа
ALLOWED_TYPES = ["клиенты", "агенты"]

# ═══════════════════════════════════════════════════════════════
# СЛОВАРИ ДЛЯ АНАЛИЗА
# ═══════════════════════════════════════════════════════════════

# Слова для определения стиля общения
FORMAL_WORDS = [
    "здравствуйте", "добрый день", "добрый вечер", "доброе утро",
    "уважаемый", "уважаемая", "прошу", "будьте добры",
    "благодарю", "с уважением", "искренне", "извините",
    "пожалуйста", "не могли бы", "позвольте"
]

INFORMAL_WORDS = [
    "привет", "приветик", "хай", "хей", "здарова", "здорово",
    "пока", "покеда", "спасибки", "ок", "окей", "норм", "ага",
    "круто", "супер", "класс", "огонь", "отлично"
]

# Слова для определения чувствительности к цене
PRICE_SENSITIVE_WORDS = [
    "дорого", "дороговато", "скидка", "скидку", "дёшево", "дешево",
    "недорого", "бюджет", "бюджетный", "экономно", "экономить",
    "акция", "промокод", "подешевле", "подороже", "цена",
    "почём", "почем", "сколько стоит", "какая цена"
]

# Типы туров для извлечения
TOUR_TYPES = {
    "desert_safari": ["сафари", "пустыня", "desert", "safari", "дюны", "джип"],
    "city_tour": ["обзорная", "city tour", "осмотр", "достопримечательности"],
    "abu_dhabi": ["абу-даби", "абу даби", "abu dhabi", "лувр", "мечеть"],
    "yacht": ["яхта", "yacht", "катер", "морская", "прогулка по воде"],
    "ferrari_world": ["феррари", "ferrari", "ferrari world"],
    "aquaventure": ["аквавентур", "aquaventure", "аквапарк", "waterpark"],
    "burj_khalifa": ["бурдж", "burj", "халифа", "khalifa", "at the top"],
    "dubai_frame": ["рамка", "frame", "dubai frame"],
    "miracle_garden": ["сад чудес", "miracle", "garden", "цветы"],
    "museum_future": ["музей будущего", "museum of the future"],
    "helicopter": ["вертолёт", "вертолет", "helicopter", "хели"],
    "dhow_cruise": ["дау", "dhow", "круиз", "dinner cruise", "ужин на корабле"],
    "shopping": ["шоппинг", "shopping", "молл", "mall", "магазины"],
    "transfer": ["трансфер", "transfer", "встреча", "аэропорт"],
}

# Интересы для извлечения
INTERESTS = {
    "adventure": ["экстрим", "адреналин", "приключение", "adventure"],
    "culture": ["культура", "история", "музей", "culture", "исторический"],
    "luxury": ["люкс", "luxury", "vip", "премиум", "premium", "exclusive"],
    "family": ["семья", "дети", "ребёнок", "ребенок", "family", "kids"],
    "photography": ["фото", "фотосессия", "photo", "инстаграм", "instagram"],
    "food": ["еда", "ресторан", "кухня", "food", "ужин", "обед"],
    "nature": ["природа", "nature", "животные", "зоопарк"],
    "nightlife": ["ночной", "night", "клуб", "бар", "вечеринка"],
    "beach": ["пляж", "beach", "море", "sea", "загар"],
    "shopping": ["шоппинг", "покупки", "shopping", "бренды"],
}


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ АНАЛИЗА
# ═══════════════════════════════════════════════════════════════

def load_contacts(filepath: Path) -> Dict[str, Any]:
    """Загрузка контактов из JSON файла."""
    if not filepath.exists():
        print(f"[!] Файл контактов не найден: {filepath}")
        return {"contacts": []}

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

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


def group_messages_by_contact(messages: List[Dict]) -> Dict[str, List[Dict]]:
    """Группировка сообщений по contact_id."""
    grouped = defaultdict(list)

    for msg in messages:
        contact_id = msg.get('contact_id')
        if contact_id:
            grouped[contact_id].append(msg)

    return grouped


def analyze_communication_style(messages: List[Dict]) -> str:
    """
    Определение стиля общения: formal, informal, mixed.
    Анализируется по наличию формальных/неформальных слов.
    """
    formal_count = 0
    informal_count = 0

    for msg in messages:
        text = msg.get('text', '').lower()

        for word in FORMAL_WORDS:
            if word in text:
                formal_count += 1

        for word in INFORMAL_WORDS:
            if word in text:
                informal_count += 1

    total = formal_count + informal_count

    if total == 0:
        return "mixed"

    formal_ratio = formal_count / total

    if formal_ratio > 0.7:
        return "formal"
    elif formal_ratio < 0.3:
        return "informal"
    else:
        return "mixed"


def analyze_price_sensitivity(messages: List[Dict]) -> str:
    """
    Определение чувствительности к цене: low, medium, high.
    По частоте слов о цене/скидках.
    """
    price_mentions = 0
    total_messages = len(messages)

    if total_messages == 0:
        return "medium"

    for msg in messages:
        text = msg.get('text', '').lower()

        for word in PRICE_SENSITIVE_WORDS:
            if word in text:
                price_mentions += 1
                break  # Считаем один раз на сообщение

    # Процент сообщений с упоминанием цены
    ratio = price_mentions / total_messages

    if ratio > 0.15:
        return "high"
    elif ratio > 0.05:
        return "medium"
    else:
        return "low"


def analyze_decision_speed(messages: List[Dict]) -> str:
    """
    Определение скорости принятия решений: fast, slow.
    По времени между запросом и подтверждением бронирования.
    """
    # Ищем паттерны быстрых/медленных решений
    quick_words = ["сразу", "сейчас", "немедленно", "бронируем", "да, берём", "окей, давайте"]
    slow_words = ["подумаю", "посоветуюсь", "позже", "перезвоню", "ещё посмотрю", "сравню"]

    quick_count = 0
    slow_count = 0

    for msg in messages:
        text = msg.get('text', '').lower()

        for word in quick_words:
            if word in text:
                quick_count += 1

        for word in slow_words:
            if word in text:
                slow_count += 1

    if quick_count > slow_count:
        return "fast"
    else:
        return "slow"


def analyze_preferred_time(messages: List[Dict]) -> str:
    """
    Определение предпочтительного времени общения: morning, afternoon, evening.
    По времени отправки сообщений.
    """
    time_counts = {"morning": 0, "afternoon": 0, "evening": 0}

    for msg in messages:
        # Пробуем разные форматы даты/времени
        timestamp = msg.get('timestamp') or msg.get('datetime') or msg.get('time')

        if not timestamp:
            continue

        hour = None

        # Пробуем извлечь час
        if isinstance(timestamp, str):
            # Формат "HH:MM:SS" или "HH:MM"
            time_match = re.search(r'(\d{1,2}):(\d{2})', timestamp)
            if time_match:
                hour = int(time_match.group(1))
            # Формат ISO datetime
            elif 'T' in timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                except:
                    pass
        elif isinstance(timestamp, (int, float)):
            # Unix timestamp
            try:
                dt = datetime.fromtimestamp(timestamp)
                hour = dt.hour
            except:
                pass

        if hour is not None:
            if 6 <= hour < 12:
                time_counts["morning"] += 1
            elif 12 <= hour < 18:
                time_counts["afternoon"] += 1
            else:
                time_counts["evening"] += 1

    # Возвращаем время с максимальным количеством сообщений
    if sum(time_counts.values()) == 0:
        return "afternoon"  # По умолчанию

    return max(time_counts, key=time_counts.get)


def extract_tour_types(messages: List[Dict]) -> List[str]:
    """Извлечение типов туров из сообщений."""
    found_types = set()

    all_text = " ".join(msg.get('text', '') for msg in messages).lower()

    for tour_type, keywords in TOUR_TYPES.items():
        for keyword in keywords:
            if keyword in all_text:
                found_types.add(tour_type)
                break

    return sorted(list(found_types))


def extract_interests(messages: List[Dict]) -> List[str]:
    """Извлечение интересов из сообщений."""
    found_interests = set()

    all_text = " ".join(msg.get('text', '') for msg in messages).lower()

    for interest, keywords in INTERESTS.items():
        for keyword in keywords:
            if keyword in all_text:
                found_interests.add(interest)
                break

    return sorted(list(found_interests))


def extract_amounts_aed(messages: List[Dict]) -> List[float]:
    """Извлечение сумм в AED из сообщений."""
    amounts = []

    # Паттерны для сумм в AED
    patterns = [
        r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)\s*(?:AED|aed|дирхам)',
        r'(?:AED|aed)\s*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)',
    ]

    for msg in messages:
        text = msg.get('text', '')

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.replace(' ', '').replace(',', '.')
                    # Если есть несколько точек, оставляем только последнюю
                    parts = amount_str.split('.')
                    if len(parts) > 2:
                        amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                    amount = float(amount_str)
                    if amount > 0:
                        amounts.append(amount)
                except ValueError:
                    continue

    return amounts


def determine_budget_category(amounts: List[float]) -> str:
    """
    Определение категории бюджета по суммам операций.
    до 1000 AED = economy
    1000-5000 AED = standard
    >5000 AED = premium
    """
    if not amounts:
        return "standard"  # По умолчанию

    avg_amount = sum(amounts) / len(amounts)

    if avg_amount < 1000:
        return "economy"
    elif avg_amount <= 5000:
        return "standard"
    else:
        return "premium"


def extract_occupation(messages: List[Dict]) -> str:
    """Попытка извлечь профессию из сообщений."""
    occupation_patterns = [
        r'(?:работаю|я)\s+([а-яё]+(?:ом|ем|ой|ей|ором|истом|телем))',
        r'(?:по профессии|по специальности)\s+([а-яё]+)',
        r'(?:я|работаю)\s+(врач|учитель|инженер|программист|менеджер|директор|бизнесмен|предприниматель)',
    ]

    all_text = " ".join(msg.get('text', '') for msg in messages).lower()

    for pattern in occupation_patterns:
        match = re.search(pattern, all_text)
        if match:
            return match.group(1).capitalize()

    return ""


def extract_city(messages: List[Dict]) -> str:
    """Попытка извлечь город из сообщений."""
    city_patterns = [
        r'(?:из|живу в|в городе|город)\s+([А-ЯЁ][а-яё]+(?:-[А-ЯЁ]?[а-яё]+)?)',
        r'(?:прилетаем из|вылетаем из|летим из)\s+([А-ЯЁ][а-яё]+)',
    ]

    # Известные города России и СНГ
    known_cities = [
        "Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск",
        "Красноярск", "Самара", "Уфа", "Ростов", "Краснодар", "Воронеж",
        "Пермь", "Волгоград", "Челябинск", "Омск", "Нижний Новгород",
        "Минск", "Киев", "Алматы", "Астана", "Ташкент", "Баку"
    ]

    all_text = " ".join(msg.get('text', '') for msg in messages)

    # Сначала ищем известные города
    for city in known_cities:
        if city.lower() in all_text.lower():
            return city

    # Потом по паттернам
    for pattern in city_patterns:
        match = re.search(pattern, all_text)
        if match:
            return match.group(1)

    return ""


def extract_family_status(messages: List[Dict]) -> str:
    """Попытка извлечь семейное положение."""
    all_text = " ".join(msg.get('text', '') for msg in messages).lower()

    if any(word in all_text for word in ["жена", "муж", "супруг", "женат", "замужем"]):
        return "married"
    elif any(word in all_text for word in ["холост", "не женат", "одна", "один"]):
        return "single"

    return ""


def extract_children_count(messages: List[Dict]) -> Optional[int]:
    """Попытка извлечь количество детей."""
    patterns = [
        r'(\d+)\s*(?:ребёнка|ребенка|детей|деток|ребёнок|ребенок)',
        r'(?:двое|трое|четверо)\s*(?:детей|деток)',
        r'(?:с ребёнком|с ребенком|с детьми)',
    ]

    all_text = " ".join(msg.get('text', '') for msg in messages).lower()

    # Числовые значения
    for pattern in patterns[:1]:
        match = re.search(pattern, all_text)
        if match:
            try:
                return int(match.group(1))
            except:
                pass

    # Словесные значения
    if "двое детей" in all_text or "два ребёнка" in all_text or "два ребенка" in all_text:
        return 2
    if "трое детей" in all_text or "три ребёнка" in all_text or "три ребенка" in all_text:
        return 3
    if "с ребёнком" in all_text or "с ребенком" in all_text:
        return 1
    if "с детьми" in all_text:
        return 2  # Предполагаем минимум двоих

    return None


def extract_birthday(messages: List[Dict]) -> Optional[str]:
    """Попытка извлечь дату рождения."""
    patterns = [
        r'(?:день рождения|др|birthday)\s*(?:у меня|моё|мое)?\s*(\d{1,2})[./](\d{1,2})',
        r'(?:родился|родилась)\s*(\d{1,2})[./](\d{1,2})',
    ]

    all_text = " ".join(msg.get('text', '') for msg in messages).lower()

    for pattern in patterns:
        match = re.search(pattern, all_text)
        if match:
            day, month = match.groups()
            try:
                day = int(day)
                month = int(month)
                if 1 <= day <= 31 and 1 <= month <= 12:
                    return f"{day:02d}.{month:02d}"
            except:
                pass

    return None


def calculate_statistics(messages: List[Dict], amounts: List[float]) -> Dict:
    """Расчёт статистики по заказам."""
    # Поиск дат заказов
    order_dates = []

    order_keywords = ["бронирование", "забронировано", "заказ", "оплата", "оплачено"]

    for msg in messages:
        text = msg.get('text', '').lower()
        timestamp = msg.get('timestamp') or msg.get('datetime')

        if any(kw in text for kw in order_keywords) and timestamp:
            order_dates.append(timestamp)

    total_orders = len(amounts) if amounts else 0
    total_spent = sum(amounts) if amounts else 0
    avg_value = total_spent / total_orders if total_orders > 0 else 0

    # Последняя дата заказа
    last_order = None
    if order_dates:
        last_order = max(order_dates) if isinstance(order_dates[0], str) else None

    return {
        "total_orders": total_orders,
        "total_spent_aed": round(total_spent, 2),
        "avg_order_value": round(avg_value, 2),
        "last_order_date": last_order
    }


def build_profile(contact: Dict, messages: List[Dict]) -> Dict:
    """Построение профиля для одного контакта."""
    contact_id = contact.get('contact_id') or contact.get('id') or str(uuid.uuid4())

    # Извлекаем суммы для анализа
    amounts = extract_amounts_aed(messages)

    profile = {
        "profile_id": str(uuid.uuid4()),
        "contact_id": contact_id,
        "biography": {
            "occupation": extract_occupation(messages),
            "city": extract_city(messages),
            "family_status": extract_family_status(messages),
            "children": extract_children_count(messages)
        },
        "personality": {
            "communication_style": analyze_communication_style(messages),
            "price_sensitivity": analyze_price_sensitivity(messages),
            "decision_speed": analyze_decision_speed(messages),
            "preferred_time": analyze_preferred_time(messages)
        },
        "preferences": {
            "tour_types": extract_tour_types(messages),
            "interests": extract_interests(messages),
            "budget_category": determine_budget_category(amounts),
            "preferred_transport": ""  # Требует дополнительного анализа
        },
        "statistics": calculate_statistics(messages, amounts),
        "special_dates": {
            "birthday": extract_birthday(messages),
            "anniversary": None  # Требует дополнительного анализа
        },
        "extracted_from_chat": True
    }

    return profile


def build_all_profiles(contacts_file: Path, messages_file: Path, output_file: Path):
    """Построение профилей для всех подходящих контактов."""

    print("=" * 60)
    print("ПОСТРОЕНИЕ ПРОФИЛЕЙ КЛИЕНТОВ")
    print("=" * 60)

    # Загрузка данных
    print(f"\n[1] Загрузка контактов из {contacts_file}")
    contacts_data = load_contacts(contacts_file)
    contacts = contacts_data.get('contacts', [])
    print(f"    Загружено контактов: {len(contacts)}")

    print(f"\n[2] Загрузка сообщений из {messages_file}")
    messages = load_messages(messages_file)
    print(f"    Загружено сообщений: {len(messages)}")

    # Группировка сообщений по контактам
    print("\n[3] Группировка сообщений по контактам...")
    messages_by_contact = group_messages_by_contact(messages)
    print(f"    Контактов с сообщениями: {len(messages_by_contact)}")

    # Фильтрация контактов по типу
    print(f"\n[4] Фильтрация по типам: {ALLOWED_TYPES}")
    filtered_contacts = [
        c for c in contacts
        if c.get('type', '').lower() in [t.lower() for t in ALLOWED_TYPES]
    ]
    print(f"    Подходящих контактов: {len(filtered_contacts)}")

    # Построение профилей
    print("\n[5] Построение профилей...")
    profiles = []

    for contact in filtered_contacts:
        contact_id = contact.get('contact_id') or contact.get('id')
        contact_name = contact.get('name', 'Unknown')

        # Получаем сообщения для контакта
        contact_messages = messages_by_contact.get(contact_id, [])

        if not contact_messages:
            # Пробуем найти по имени или телефону
            phone = contact.get('phone', '')
            for cid, msgs in messages_by_contact.items():
                if phone and phone in str(cid):
                    contact_messages = msgs
                    break

        if contact_messages:
            profile = build_profile(contact, contact_messages)
            profiles.append(profile)

            # Вывод прогресса
            style = profile['personality']['communication_style']
            budget = profile['preferences']['budget_category']
            tours = len(profile['preferences']['tour_types'])
            print(f"    + {contact_name}: {style}, {budget}, {tours} типов туров")

    # Сохранение результата
    print(f"\n[6] Сохранение в {output_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "profiles": profiles,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_profiles": len(profiles),
            "source_contacts": str(contacts_file),
            "source_messages": str(messages_file)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Итоговая статистика
    print("\n" + "=" * 60)
    print("СТАТИСТИКА")
    print("=" * 60)

    if profiles:
        # Распределение по стилю общения
        styles = Counter(p['personality']['communication_style'] for p in profiles)
        print(f"\nСтиль общения:")
        for style, count in styles.most_common():
            print(f"  {style}: {count}")

        # Распределение по чувствительности к цене
        sensitivity = Counter(p['personality']['price_sensitivity'] for p in profiles)
        print(f"\nЧувствительность к цене:")
        for sens, count in sensitivity.most_common():
            print(f"  {sens}: {count}")

        # Распределение по бюджету
        budgets = Counter(p['preferences']['budget_category'] for p in profiles)
        print(f"\nКатегория бюджета:")
        for budget, count in budgets.most_common():
            print(f"  {budget}: {count}")

        # Популярные типы туров
        all_tours = []
        for p in profiles:
            all_tours.extend(p['preferences']['tour_types'])
        tour_counts = Counter(all_tours)
        print(f"\nПопулярные туры (топ-5):")
        for tour, count in tour_counts.most_common(5):
            print(f"  {tour}: {count}")

    print(f"\nВсего профилей: {len(profiles)}")
    print(f"Сохранено в: {output_file}")
    print("=" * 60)

    return profiles


def main():
    parser = argparse.ArgumentParser(
        description="Построение профилей клиентов из чатов WhatsApp"
    )
    parser.add_argument(
        "--contacts", "-c",
        default=str(CONTACTS_FILE),
        help=f"Путь к файлу контактов (default: {CONTACTS_FILE})"
    )
    parser.add_argument(
        "--messages", "-m",
        default=str(MESSAGES_FILE),
        help=f"Путь к файлу сообщений (default: {MESSAGES_FILE})"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(OUTPUT_FILE),
        help=f"Путь к выходному файлу (default: {OUTPUT_FILE})"
    )

    args = parser.parse_args()

    build_all_profiles(
        Path(args.contacts),
        Path(args.messages),
        Path(args.output)
    )


if __name__ == "__main__":
    main()
