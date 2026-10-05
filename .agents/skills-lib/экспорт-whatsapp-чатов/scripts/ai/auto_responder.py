#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Система автоматических ответов на частые вопросы.
Анализирует входящие сообщения и генерирует подходящие ответы.

Функции:
- Keyword matching (точное совпадение ключевых слов)
- Fuzzy matching (нечёткое сравнение с помощью fuzzywuzzy)
- Intent-based matching (классификация намерений)
- Персонализация ответов (имя, язык, время суток)
- Интеграция с WhatsApp API (формат ответа)
- Логирование и метрики
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    CHATS_DIR, TEMPLATES_DIR, ANALYTICS_DIR,
    ensure_directories
)

# Опциональные зависимости
try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("Внимание: fuzzywuzzy не установлен. pip install fuzzywuzzy python-Levenshtein")

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ И ПУТИ
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
TEMPLATES_FILE = SCRIPT_DIR / "templates" / "auto_responses.json"
PRODUCTS_FILE = SCRIPT_DIR.parent / "assets" / "bitrix24_products.json"
OUTPUT_DIR = ANALYTICS_DIR if ANALYTICS_DIR.exists() else CHATS_DIR / "_аналитика"
LOGS_DIR = OUTPUT_DIR / "logs"

# Пороги совпадения
KEYWORD_THRESHOLD = 0.6      # Минимум для keyword matching
FUZZY_THRESHOLD = 70         # Минимум для fuzzy matching (0-100)
INTENT_THRESHOLD = 0.5       # Минимум для intent matching

# Временные периоды для приветствий
TIME_PERIODS = {
    "morning": (5, 12),    # 05:00 - 11:59
    "afternoon": (12, 17), # 12:00 - 16:59
    "evening": (17, 23),   # 17:00 - 22:59
}


# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_templates() -> Dict:
    """Загрузить шаблоны ответов."""
    if not TEMPLATES_FILE.exists():
        print(f"Файл шаблонов не найден: {TEMPLATES_FILE}")
        return {}

    with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_products() -> Dict:
    """Загрузить каталог продуктов для цен."""
    if not PRODUCTS_FILE.exists():
        return {}

    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════
# ОПРЕДЕЛЕНИЕ ЯЗЫКА
# ═══════════════════════════════════════════════════════════════

def detect_language(text: str) -> str:
    """Определить язык сообщения (ru/en/ar)."""
    text_lower = text.lower()

    # Арабские символы
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    if arabic_pattern.search(text):
        return "ar"

    # Кириллица
    cyrillic_pattern = re.compile(r'[а-яА-ЯёЁ]')
    cyrillic_count = len(cyrillic_pattern.findall(text))

    # Латиница
    latin_pattern = re.compile(r'[a-zA-Z]')
    latin_count = len(latin_pattern.findall(text))

    if cyrillic_count > latin_count:
        return "ru"
    elif latin_count > 0:
        return "en"

    return "ru"  # По умолчанию русский


def get_time_period() -> str:
    """Получить текущий период дня."""
    hour = datetime.now().hour

    for period, (start, end) in TIME_PERIODS.items():
        if start <= hour < end:
            return period

    return "default"


# ═══════════════════════════════════════════════════════════════
# KEYWORD MATCHING
# ═══════════════════════════════════════════════════════════════

def keyword_match(text: str, keywords: List[str]) -> Tuple[bool, float]:
    """
    Проверить совпадение по ключевым словам.

    Returns:
        (matched, score) - флаг совпадения и оценка (0-1)
    """
    text_lower = text.lower()
    text_words = set(re.findall(r'\b\w+\b', text_lower))

    matches = 0
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Точное вхождение подстроки
        if keyword_lower in text_lower:
            matches += 1
        # Или совпадение слова
        elif keyword_lower in text_words:
            matches += 0.5

    if matches == 0:
        return False, 0.0

    # Нормализуем оценку
    score = min(matches / 2, 1.0)  # Максимум при 2+ совпадениях

    return score >= KEYWORD_THRESHOLD, score


# ═══════════════════════════════════════════════════════════════
# FUZZY MATCHING
# ═══════════════════════════════════════════════════════════════

def fuzzy_match(text: str, keywords: List[str]) -> Tuple[bool, float, str]:
    """
    Нечёткое сравнение с ключевыми словами.

    Returns:
        (matched, score, best_match) - флаг, оценка и лучшее совпадение
    """
    if not FUZZY_AVAILABLE:
        return False, 0.0, ""

    text_lower = text.lower()
    best_score = 0
    best_match = ""

    for keyword in keywords:
        # Partial ratio лучше для подстрок
        score = fuzz.partial_ratio(keyword.lower(), text_lower)
        if score > best_score:
            best_score = score
            best_match = keyword

    matched = best_score >= FUZZY_THRESHOLD
    normalized_score = best_score / 100.0

    return matched, normalized_score, best_match


# ═══════════════════════════════════════════════════════════════
# INTENT-BASED MATCHING
# ═══════════════════════════════════════════════════════════════

# Простой классификатор намерений на основе паттернов
INTENT_PATTERNS = {
    "ask_price": [
        r"сколько\s+стоит",
        r"какая\s+цена",
        r"price",
        r"how\s+much",
        r"cost",
        r"прайс",
        r"\bцена\b",
        r"стоимость",
    ],
    "request_booking": [
        r"забронир",
        r"заказ",
        r"хочу\s+записать",
        r"book",
        r"reserve",
        r"можно\s+оформ",
    ],
    "ask_availability": [
        r"есть\s+места",
        r"свободн",
        r"доступн",
        r"available",
        r"можно\s+на\s+\d",  # "можно на 15 января"
        r"когда\s+можно\s+(?!оплат)",  # "когда можно" но не "когда можно оплатить"
    ],
    "ask_payment": [
        r"как\s+(можно\s+)?оплат",
        r"можно\s+оплат",
        r"куда\s+перев",
        r"способ\s+оплат",
        r"payment",
        r"\bpay\b",
        r"карт[аыу]",
        r"\bоплат",
        r"перевод",
        r"реквизит",
    ],
    "cancel_request": [
        r"отмен",
        r"возврат",
        r"перенес",
        r"cancel",
        r"refund",
        r"reschedule",
        r"can\s+i\s+cancel",
        r"want\s+to\s+cancel",
    ],
    "greeting": [
        r"^привет",
        r"^здравств",
        r"^добр",
        r"^hi\b",
        r"^hello",
        r"^hey\b",
    ],
    "farewell": [
        r"пока",
        r"до свидания",
        r"до связи",
        r"bye",
        r"goodbye",
    ],
    "thanks": [
        r"спасибо",
        r"благодар",
        r"thank",
    ],
}


def intent_match(text: str) -> Tuple[str, float]:
    """
    Определить намерение пользователя.

    Returns:
        (intent, confidence) - намерение и уверенность
    """
    text_lower = text.lower()

    intent_scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 1

        if score > 0:
            intent_scores[intent] = score / len(patterns)

    if not intent_scores:
        return "unknown", 0.0

    best_intent = max(intent_scores, key=intent_scores.get)
    confidence = intent_scores[best_intent]

    if confidence < INTENT_THRESHOLD:
        return "unknown", confidence

    return best_intent, confidence


# ═══════════════════════════════════════════════════════════════
# ПОИСК ПРОДУКТОВ
# ═══════════════════════════════════════════════════════════════

def find_product(text: str, products_data: Dict) -> Optional[Dict]:
    """Найти упомянутый продукт в сообщении."""
    if not products_data or "products" not in products_data:
        return None

    text_lower = text.lower()

    for product in products_data["products"]:
        name_lower = product["name"].lower()

        # Точное упоминание названия
        if name_lower in text_lower:
            return product

        # Проверка тегов
        tags = product.get("tags", [])
        for tag in tags:
            if tag.lower() in text_lower:
                return product

        # Fuzzy matching для названия
        if FUZZY_AVAILABLE:
            score = fuzz.partial_ratio(name_lower, text_lower)
            if score >= 80:
                return product

    return None


def format_product_list(products_data: Dict, category: str = None, limit: int = 10) -> str:
    """Форматировать список продуктов с ценами."""
    if not products_data or "products" not in products_data:
        return "Продукты недоступны"

    lines = []
    count = 0

    for product in products_data["products"]:
        if not product.get("active", True):
            continue

        if category and product.get("category_code", "").lower() != category.lower():
            continue

        name = product["name"]
        price = product["price"]
        unit = product.get("unit", "")
        desc = product.get("description", "")

        lines.append(f"- {name}: {price} AED/{unit}")
        if desc:
            lines.append(f"  ({desc})")

        count += 1
        if count >= limit:
            break

    return "\n".join(lines) if lines else "Продукты не найдены"


# ═══════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС АВТООТВЕТЧИКА
# ═══════════════════════════════════════════════════════════════

class AutoResponder:
    """Система автоматических ответов."""

    def __init__(self):
        self.templates = load_templates()
        self.products = load_products()
        self.usage_stats = Counter()
        self.response_log = []

        # Создаём директории
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def find_category(self, text: str) -> Tuple[str, float, str]:
        """
        Найти подходящую категорию для сообщения.

        Returns:
            (category_key, confidence, method) - категория, уверенность, метод
        """
        if not self.templates or "categories" not in self.templates:
            return "unknown", 0.0, "none"

        # Собираем все совпадения с оценками
        candidates = []

        # 1. Intent-based matching (наивысший приоритет для основных интентов)
        intent, intent_score = intent_match(text)
        if intent != "unknown" and intent_score >= INTENT_THRESHOLD:
            # Маппинг интентов на категории
            intent_to_category = {
                "ask_price": "prices",
                "request_booking": "booking_terms",
                "ask_availability": "availability",
                "ask_payment": "payment",
                "cancel_request": "cancellation",
                "greeting": "greeting",
                "farewell": "farewell",
                "thanks": "thanks",
            }
            if intent in intent_to_category:
                category = intent_to_category[intent]
                # Приветствие имеет низкий приоритет если есть другой intent
                # Intent имеет высокий приоритет (1.5 boost)
                priority = 0.5 if intent == "greeting" else 1.5
                candidates.append((category, intent_score * priority, "intent", intent))

        # 2. Keyword matching для всех категорий
        for cat_key, cat_data in self.templates["categories"].items():
            keywords = cat_data.get("keywords", [])
            if not keywords:
                continue

            matched, score = keyword_match(text, keywords)
            if matched:
                # Приветствие имеет низкий приоритет
                priority = 0.5 if cat_key == "greeting" else 1.0
                candidates.append((cat_key, score * priority, "keyword", None))

        # 3. Fuzzy matching
        if FUZZY_AVAILABLE:
            for cat_key, cat_data in self.templates["categories"].items():
                keywords = cat_data.get("keywords", [])
                if not keywords:
                    continue

                matched, score, _ = fuzzy_match(text, keywords)
                if matched:
                    # Fuzzy имеет чуть меньший приоритет
                    priority = 0.4 if cat_key == "greeting" else 0.9
                    candidates.append((cat_key, score * priority, "fuzzy", None))

        if not candidates:
            return "unknown", 0.0, "none"

        # Убираем дубликаты категорий, оставляя лучший скор
        category_scores = {}
        for cat, score, method, _ in candidates:
            if cat not in category_scores or score > category_scores[cat][0]:
                category_scores[cat] = (score, method)

        # Приоритеты категорий (выше = важнее при конфликте)
        priority_order = ["cancellation", "payment", "prices", "availability", "booking_terms", "thanks", "farewell", "greeting"]

        # Если есть cancellation и booking_terms одновременно - выбираем cancellation
        if "cancellation" in category_scores and "booking_terms" in category_scores:
            del category_scores["booking_terms"]

        # Если есть и greeting и что-то ещё - выбираем не-greeting
        non_greeting = {k: v for k, v in category_scores.items() if k != "greeting"}
        if non_greeting:
            # Сортируем по приоритету при равных скорах
            def sort_key(k):
                score = non_greeting[k][0]
                priority = priority_order.index(k) if k in priority_order else 100
                return (score, -priority)  # Больше скор лучше, меньше индекс приоритета лучше

            best_category = max(non_greeting, key=sort_key)
            best_score, best_method = non_greeting[best_category]
        else:
            best_category = max(category_scores, key=lambda k: category_scores[k][0])
            best_score, best_method = category_scores[best_category]

        return best_category, min(best_score * 1.2, 1.0), best_method  # Немного boost для уверенности

    def personalize_response(
        self,
        template: str,
        client_name: str = None,
        language: str = "ru",
        product: Dict = None,
        **kwargs
    ) -> str:
        """Персонализировать ответ подстановкой переменных."""
        response = template

        # Имя клиента
        name = client_name or ("Dear Customer" if language == "en" else "Уважаемый клиент")
        response = response.replace("{name}", name)

        # Продукт
        if product:
            response = response.replace("{product_name}", product.get("name", ""))
            response = response.replace("{price}", str(product.get("price", "")))
            response = response.replace("{description}", product.get("description_full", product.get("description", "")))
            includes = product.get("includes", [])
            response = response.replace("{includes}", ", ".join(includes) if includes else "")

        # Список продуктов
        if "{product_list}" in response:
            product_list = format_product_list(self.products)
            response = response.replace("{product_list}", product_list)

        # Дополнительные переменные
        for key, value in kwargs.items():
            response = response.replace(f"{{{key}}}", str(value))

        return response

    def get_response(
        self,
        message: str,
        client_name: str = None,
        language: str = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Получить автоматический ответ на сообщение.

        Args:
            message: Текст входящего сообщения
            client_name: Имя клиента (опционально)
            language: Язык ответа (опционально, авто-определение)
            context: Дополнительный контекст (опционально)

        Returns:
            Dict с полями: response, category, confidence, method, language
        """
        context = context or {}

        # Определяем язык
        if not language:
            language = detect_language(message)

        # Находим категорию
        category, confidence, method = self.find_category(message)

        # Получаем шаблоны категории
        cat_data = self.templates.get("categories", {}).get(category, {})
        templates = cat_data.get("templates", {}).get(language, {})

        # Если нет шаблонов для языка - fallback на русский
        if not templates:
            templates = cat_data.get("templates", {}).get("ru", {})

        # Выбираем подходящий шаблон
        template_key = "default"

        # Для приветствий учитываем время суток
        if category == "greeting":
            template_key = get_time_period()

        # Для цен проверяем конкретный продукт
        product = None
        if category == "prices":
            product = find_product(message, self.products)
            if product:
                template_key = "single_product"

        # Получаем шаблон
        template = templates.get(template_key, templates.get("default", ""))

        if not template:
            # Fallback ответ
            template = "{name}, получили ваше сообщение. Ответим в ближайшее время!"

        # Персонализируем
        response = self.personalize_response(
            template,
            client_name=client_name,
            language=language,
            product=product,
            **context
        )

        # Логируем
        self.usage_stats[category] += 1
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message[:100],
            "category": category,
            "confidence": confidence,
            "method": method,
            "language": language,
            "template_key": template_key,
        }
        self.response_log.append(log_entry)

        return {
            "response": response,
            "category": category,
            "category_name": cat_data.get(f"name_{language}", cat_data.get("name_ru", category)),
            "confidence": confidence,
            "method": method,
            "language": language,
            "template_key": template_key,
            "product": product.get("name") if product else None,
        }

    def get_quick_replies(self, language: str = "ru") -> List[Dict]:
        """Получить быстрые ответы для UI."""
        quick = self.templates.get("quick_replies", {}).get(language, [])
        return quick if quick else self.templates.get("quick_replies", {}).get("ru", [])

    def format_for_whatsapp(self, response_data: Dict) -> str:
        """Форматировать ответ для WhatsApp API."""
        text = response_data.get("response", "")

        # WhatsApp форматирование
        # *bold* -> остаётся
        # _italic_ -> остаётся
        # ~strikethrough~ -> остаётся
        # ```code``` -> остаётся

        return text

    def save_metrics(self, output_file: Path = None):
        """Сохранить метрики использования."""
        if not output_file:
            output_file = LOGS_DIR / f"auto_responder_metrics_{datetime.now().strftime('%Y-%m-%d')}.json"

        metrics = {
            "generated_at": datetime.now().isoformat(),
            "total_responses": sum(self.usage_stats.values()),
            "category_usage": dict(self.usage_stats),
            "recent_log": self.response_log[-100:],  # Последние 100
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        return output_file

    def process_batch(self, messages: List[Dict]) -> List[Dict]:
        """
        Обработать пакет сообщений.

        Args:
            messages: Список словарей с полями: text, client_name, language (опц.)

        Returns:
            Список ответов
        """
        results = []

        for msg in messages:
            text = msg.get("text", msg.get("message", ""))
            client_name = msg.get("client_name", msg.get("name"))
            language = msg.get("language")
            context = msg.get("context", {})

            result = self.get_response(
                message=text,
                client_name=client_name,
                language=language,
                context=context
            )

            result["original_message"] = text
            results.append(result)

        return results


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Автоматические ответы на частые вопросы',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python auto_responder.py "Сколько стоит экскурсия в Абу-Даби?"
  python auto_responder.py "Hello, how much for safari?" --name John
  python auto_responder.py --input messages.json --output responses.json
  python auto_responder.py --interactive
        """
    )

    parser.add_argument('message', nargs='?', help='Текст сообщения')
    parser.add_argument('--name', help='Имя клиента')
    parser.add_argument('--lang', choices=['ru', 'en', 'ar'], help='Язык ответа')
    parser.add_argument('--input', '-i', help='JSON файл со списком сообщений')
    parser.add_argument('--output', '-o', help='Выходной файл (JSON)')
    parser.add_argument('--interactive', action='store_true', help='Интерактивный режим')
    parser.add_argument('--metrics', action='store_true', help='Показать метрики')

    args = parser.parse_args()

    ensure_directories()
    responder = AutoResponder()

    # Интерактивный режим
    if args.interactive:
        print("Автоответчик запущен. Введите 'exit' для выхода.\n")
        while True:
            try:
                message = input("Вопрос: ").strip()
                if message.lower() in ['exit', 'quit', 'выход']:
                    break
                if not message:
                    continue

                result = responder.get_response(message, client_name=args.name)
                print(f"\n[{result['category']}] (уверенность: {result['confidence']:.0%}, метод: {result['method']})")
                print(f"Ответ:\n{result['response']}\n")
                print("-" * 50)
            except KeyboardInterrupt:
                break

        # Сохраняем метрики
        metrics_file = responder.save_metrics()
        print(f"\nМетрики сохранены: {metrics_file}")
        return

    # Пакетная обработка
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            messages = json.load(f)

        if isinstance(messages, dict):
            messages = messages.get("messages", [messages])

        results = responder.process_batch(messages)

        output_file = Path(args.output) if args.output else OUTPUT_DIR / "suggested_responses.json"

        output_data = {
            "generated_at": datetime.now().isoformat(),
            "total": len(results),
            "responses": results,
            "usage_stats": dict(responder.usage_stats),
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Обработано: {len(results)} сообщений")
        print(f"Сохранено: {output_file}")

        # Показываем статистику
        print("\nСтатистика по категориям:")
        for cat, count in responder.usage_stats.most_common():
            print(f"  {cat}: {count}")

        return

    # Одиночное сообщение
    if args.message:
        result = responder.get_response(
            message=args.message,
            client_name=args.name,
            language=args.lang
        )

        print(f"Категория: {result['category_name']} ({result['category']})")
        print(f"Уверенность: {result['confidence']:.0%}")
        print(f"Метод: {result['method']}")
        print(f"Язык: {result['language']}")
        if result['product']:
            print(f"Продукт: {result['product']}")
        print(f"\n{result['response']}")

        # Опционально сохраняем
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nСохранено: {args.output}")

        return

    # Показать метрики
    if args.metrics:
        metrics_files = sorted(LOGS_DIR.glob("auto_responder_metrics_*.json"))
        if metrics_files:
            with open(metrics_files[-1], 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            print(json.dumps(metrics, ensure_ascii=False, indent=2))
        else:
            print("Метрики не найдены")
        return

    # Показать справку
    parser.print_help()


if __name__ == "__main__":
    main()
