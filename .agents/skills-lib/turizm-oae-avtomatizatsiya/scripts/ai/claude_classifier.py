#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Умная классификация сообщений и намерений через Claude API.

Функции:
1. Классификация типа контакта (клиент/агент/поставщик/сотрудник)
2. Определение намерения сообщения (запрос цены, бронирование, жалоба, благодарность, вопрос, spam)
3. Извлечение сущностей (даты, суммы, названия туров, имена)
4. Определение срочности (urgent/normal/low)
5. Рекомендация следующего действия

Входные данные: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходные данные: classified_messages.jsonl, contact_classifications.json
"""

import sys
import os
import json
import re
import argparse
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Импорт конфигурации из config.py
try:
    from config import RAW_DIR, JSON_DIR, ANALYTICS_DIR
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    ANALYTICS_DIR = Path("D:/Downloads/Chats/_аналитика")

# Claude API ключ
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY', '') or os.getenv('CLAUDE_API_KEY', '')

# Настройки API
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Экономичная модель для массовой обработки
CLAUDE_MAX_TOKENS = 1024
BATCH_SIZE = 50  # Сообщений в одном батче для экономии токенов
MAX_RETRIES = 3
RETRY_DELAY = 2  # секунд

# Пути к файлам кэша
CACHE_DIR = RAW_DIR / ".cache"
CACHE_FILE = CACHE_DIR / "classification_cache.json"


# ═══════════════════════════════════════════════════════════════
# ТИПЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class MessageClassification:
    """Результат классификации одного сообщения."""
    message_id: str
    intent: str  # price_inquiry, booking, complaint, gratitude, question, spam, other
    urgency: str  # urgent, normal, low
    entities: Dict[str, List[str]]  # dates, amounts, tours, names
    recommended_action: str
    confidence: float


@dataclass
class ContactClassification:
    """Результат классификации контакта."""
    jid: str
    contact_type: str  # клиент, агент, поставщик, сотрудник
    subtype: str
    confidence: float
    key_indicators: List[str]
    message_count: int
    classified_at: str


# ═══════════════════════════════════════════════════════════════
# КЭШИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

class ClassificationCache:
    """Кэш результатов классификации для экономии токенов."""

    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Загрузить кэш из файла."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"Кэш загружен: {len(self.cache)} записей")
            except (json.JSONDecodeError, IOError) as e:
                print(f"ВНИМАНИЕ: Не удалось загрузить кэш: {e}")
                self.cache = {}

    def _save(self):
        """Сохранить кэш в файл."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _hash_text(self, text: str) -> str:
        """Создать хэш текста для использования как ключа."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_message(self, text: str) -> Optional[Dict]:
        """Получить кэшированную классификацию сообщения."""
        key = f"msg:{self._hash_text(text)}"
        return self.cache.get(key)

    def set_message(self, text: str, classification: Dict):
        """Сохранить классификацию сообщения в кэш."""
        key = f"msg:{self._hash_text(text)}"
        self.cache[key] = classification
        # Сохраняем после каждых 100 новых записей
        if len(self.cache) % 100 == 0:
            self._save()

    def get_contact(self, jid: str, messages_hash: str) -> Optional[Dict]:
        """Получить кэшированную классификацию контакта."""
        key = f"contact:{jid}:{messages_hash}"
        return self.cache.get(key)

    def set_contact(self, jid: str, messages_hash: str, classification: Dict):
        """Сохранить классификацию контакта в кэш."""
        key = f"contact:{jid}:{messages_hash}"
        self.cache[key] = classification

    def finalize(self):
        """Сохранить кэш при завершении работы."""
        self._save()
        print(f"Кэш сохранён: {len(self.cache)} записей")


# ═══════════════════════════════════════════════════════════════
# CLAUDE API КЛИЕНТ
# ═══════════════════════════════════════════════════════════════

class ClaudeClassifier:
    """Классификатор на основе Claude API."""

    def __init__(self, api_key: str, cache: ClassificationCache):
        self.api_key = api_key
        self.cache = cache
        self.client = None
        self._init_client()

    def _init_client(self):
        """Инициализировать клиент Anthropic."""
        if not self.api_key:
            print("ВНИМАНИЕ: ANTHROPIC_API_KEY не установлен. Используем rules-based fallback.")
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("Claude API клиент инициализирован")
        except ImportError:
            print("ВНИМАНИЕ: anthropic SDK не установлен. Установите: pip install anthropic")
            self.client = None
        except Exception as e:
            print(f"ОШИБКА инициализации Claude API: {e}")
            self.client = None

    def classify_messages_batch(self, messages: List[Dict]) -> List[Dict]:
        """
        Классифицировать батч сообщений.

        Использует batch processing для экономии токенов.
        """
        results = []

        # Проверяем кэш для каждого сообщения
        uncached_messages = []
        uncached_indices = []

        for i, msg in enumerate(messages):
            text = msg.get('text', '')
            cached = self.cache.get_message(text)
            if cached:
                results.append(cached)
            else:
                uncached_messages.append(msg)
                uncached_indices.append(i)
                results.append(None)  # Placeholder

        if not uncached_messages:
            return results

        # Если API недоступен, используем rules-based
        if not self.client:
            for idx, msg in zip(uncached_indices, uncached_messages):
                classification = self._rules_based_message_classification(msg)
                results[idx] = classification
                self.cache.set_message(msg.get('text', ''), classification)
            return results

        # Batch classification через Claude API
        try:
            batch_result = self._call_claude_batch(uncached_messages)
            for idx, msg, classification in zip(uncached_indices, uncached_messages, batch_result):
                results[idx] = classification
                self.cache.set_message(msg.get('text', ''), classification)
        except Exception as e:
            print(f"ОШИБКА Claude API: {e}. Используем rules-based fallback.")
            for idx, msg in zip(uncached_indices, uncached_messages):
                classification = self._rules_based_message_classification(msg)
                results[idx] = classification
                self.cache.set_message(msg.get('text', ''), classification)

        return results

    def _call_claude_batch(self, messages: List[Dict]) -> List[Dict]:
        """Вызвать Claude API для батча сообщений."""

        # Формируем промпт для батч-обработки
        messages_text = "\n".join([
            f"[{i+1}] {msg.get('text', '')[:500]}"  # Ограничиваем длину
            for i, msg in enumerate(messages)
        ])

        prompt = f"""Проанализируй следующие сообщения из WhatsApp переписки туристической компании в ОАЭ.

Для КАЖДОГО сообщения определи:
1. intent (намерение): price_inquiry, booking, complaint, gratitude, question, spam, other
2. urgency (срочность): urgent, normal, low
3. entities (сущности): даты, суммы (в любой валюте), названия туров/экскурсий, имена людей
4. recommended_action: что должен сделать менеджер (на русском, кратко)

СООБЩЕНИЯ:
{messages_text}

Ответь ТОЛЬКО валидным JSON массивом без markdown:
[
  {{"id": 1, "intent": "...", "urgency": "...", "entities": {{"dates": [], "amounts": [], "tours": [], "names": []}}, "recommended_action": "...", "confidence": 0.9}},
  ...
]"""

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=CLAUDE_MAX_TOKENS,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # Парсим ответ
                response_text = response.content[0].text.strip()

                # Убираем возможные markdown-обёртки
                if response_text.startswith("```"):
                    response_text = re.sub(r'^```\w*\n?', '', response_text)
                    response_text = re.sub(r'\n?```$', '', response_text)

                results = json.loads(response_text)

                # Проверяем, что получили нужное количество результатов
                if len(results) != len(messages):
                    print(f"ВНИМАНИЕ: Получено {len(results)} результатов, ожидалось {len(messages)}")
                    # Дополняем недостающие rules-based
                    while len(results) < len(messages):
                        results.append(self._rules_based_message_classification(messages[len(results)]))

                return results

            except json.JSONDecodeError as e:
                print(f"Попытка {attempt + 1}: Ошибка парсинга JSON: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"Попытка {attempt + 1}: Ошибка API: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)

        # Если все попытки неудачны, возвращаем rules-based
        return [self._rules_based_message_classification(msg) for msg in messages]

    def classify_contact(self, jid: str, messages: List[Dict], contact_info: Dict) -> Dict:
        """Классифицировать контакт на основе истории переписки."""

        # Создаём хэш сообщений для кэширования
        messages_hash = hashlib.md5(
            json.dumps([m.get('text', '')[:100] for m in messages[-50:]], ensure_ascii=False).encode()
        ).hexdigest()[:16]

        # Проверяем кэш
        cached = self.cache.get_contact(jid, messages_hash)
        if cached:
            return cached

        # Если API недоступен или мало сообщений
        if not self.client or len(messages) < 3:
            classification = self._rules_based_contact_classification(jid, messages, contact_info)
            self.cache.set_contact(jid, messages_hash, classification)
            return classification

        try:
            classification = self._classify_contact_via_api(jid, messages, contact_info)
            self.cache.set_contact(jid, messages_hash, classification)
            return classification
        except Exception as e:
            print(f"ОШИБКА классификации контакта {jid}: {e}")
            classification = self._rules_based_contact_classification(jid, messages, contact_info)
            self.cache.set_contact(jid, messages_hash, classification)
            return classification

    def _classify_contact_via_api(self, jid: str, messages: List[Dict], contact_info: Dict) -> Dict:
        """Классифицировать контакт через Claude API."""

        # Берём последние 30 сообщений для контекста
        sample_messages = messages[-30:]
        messages_text = "\n".join([
            f"[{'Я' if m.get('is_from_me') else m.get('sender', 'Клиент')}] {m.get('text', '')[:200]}"
            for m in sample_messages
        ])

        name = contact_info.get('name', '') or contact_info.get('chat_name', '')

        prompt = f"""Проанализируй переписку и определи тип контакта для туристической компании в ОАЭ.

КОНТАКТ: {name}
JID: {jid}
СООБЩЕНИЙ ВСЕГО: {len(messages)}

ПОСЛЕДНИЕ СООБЩЕНИЯ:
{messages_text}

Определи:
1. contact_type: клиент, агент, поставщик, сотрудник
2. subtype:
   - для клиента: турист, VIP, корпоративный
   - для агента: турагент, туроператор, B2B
   - для поставщика: обменник, водитель, гид, яхтсмен, кейтеринг
   - для сотрудника: менеджер, водитель_штат, админ
3. key_indicators: список ключевых признаков (3-5 пунктов)

ТИПИЧНЫЕ ПРИЗНАКИ:
- Агенты: спрашивают нетто-цены, комиссию, оптовые заказы, группы
- Поставщики: предлагают услуги, обсуждают курсы, графики работы
- Сотрудники: внутренние вопросы, зарплата, смены, офис
- Клиенты: спрашивают цены, бронируют туры, уточняют детали

Ответь ТОЛЬКО валидным JSON без markdown:
{{"contact_type": "...", "subtype": "...", "confidence": 0.9, "key_indicators": ["...", "..."]}}"""

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=512,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.content[0].text.strip()

        # Убираем возможные markdown-обёртки
        if response_text.startswith("```"):
            response_text = re.sub(r'^```\w*\n?', '', response_text)
            response_text = re.sub(r'\n?```$', '', response_text)

        result = json.loads(response_text)

        return {
            "jid": jid,
            "contact_type": result.get("contact_type", "клиент"),
            "subtype": result.get("subtype", "турист"),
            "confidence": result.get("confidence", 0.5),
            "key_indicators": result.get("key_indicators", []),
            "message_count": len(messages),
            "classified_at": datetime.now().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════
    # RULES-BASED FALLBACK
    # ═══════════════════════════════════════════════════════════════

    def _rules_based_message_classification(self, msg: Dict) -> Dict:
        """Fallback классификация сообщения на основе правил."""
        text = (msg.get('text', '') or '').lower()

        # Определение намерения
        intent = "other"
        if any(w in text for w in ['цена', 'сколько', 'стоимость', 'стоит', 'прайс', 'price']):
            intent = "price_inquiry"
        elif any(w in text for w in ['бронь', 'забронир', 'заказ', 'оформ', 'booking', 'book']):
            intent = "booking"
        elif any(w in text for w in ['жалоба', 'плохо', 'ужасно', 'недовол', 'претензия', 'complaint']):
            intent = "complaint"
        elif any(w in text for w in ['спасибо', 'благодар', 'отлично', 'супер', 'класс', 'thank']):
            intent = "gratitude"
        elif any(w in text for w in ['?', 'как', 'где', 'когда', 'что', 'можно']):
            intent = "question"
        elif any(w in text for w in ['реклама', 'spam', 'продвижение', 'акция', 'скидка 50%']):
            intent = "spam"

        # Определение срочности
        urgency = "normal"
        if any(w in text for w in ['срочно', 'urgent', 'asap', 'сейчас', 'сегодня', 'завтра']):
            urgency = "urgent"
        elif any(w in text for w in ['когда-нибудь', 'может быть', 'подумаю', 'потом']):
            urgency = "low"

        # Извлечение сущностей
        entities = {
            "dates": re.findall(r'\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?', text),
            "amounts": re.findall(r'\d+(?:\s*(?:aed|дирхам|руб|usd|долл|\$|₽))', text, re.IGNORECASE),
            "tours": [],
            "names": []
        }

        # Поиск названий туров
        tour_keywords = ['сафари', 'safari', 'абу-даби', 'abu dhabi', 'яхта', 'yacht',
                        'ferrari', 'феррари', 'дубай', 'dubai', 'экскурсия', 'тур']
        for kw in tour_keywords:
            if kw in text:
                entities["tours"].append(kw)

        # Рекомендация действия
        action_map = {
            "price_inquiry": "Отправить прайс-лист или рассчитать стоимость",
            "booking": "Подтвердить детали и оформить бронирование",
            "complaint": "СРОЧНО: Связаться и решить проблему",
            "gratitude": "Поблагодарить и предложить другие услуги",
            "question": "Ответить на вопрос",
            "spam": "Игнорировать",
            "other": "Изучить контекст и ответить"
        }

        return {
            "id": msg.get('message_id', hashlib.md5(text.encode()).hexdigest()[:8]),
            "intent": intent,
            "urgency": urgency,
            "entities": entities,
            "recommended_action": action_map.get(intent, "Ответить"),
            "confidence": 0.6  # Низкая уверенность для rules-based
        }

    def _rules_based_contact_classification(self, jid: str, messages: List[Dict], contact_info: Dict) -> Dict:
        """Fallback классификация контакта на основе правил."""

        # Собираем весь текст
        all_text = ' '.join([m.get('text', '') for m in messages]).lower()
        name = (contact_info.get('name', '') or contact_info.get('chat_name', '')).lower()

        # Подсчёт ключевых слов
        scores = {
            "агент": 0,
            "поставщик": 0,
            "сотрудник": 0,
            "клиент": 0
        }

        # Агенты
        agent_keywords = ['турагент', 'агентство', 'комиссия', 'нетто', 'брутто',
                        'оптом', 'группа', 'travel', 'agency', 'b2b']
        for kw in agent_keywords:
            if kw in all_text or kw in name:
                scores["агент"] += 2

        # Поставщики
        supplier_keywords = ['курс', 'обмен', 'exchange', 'водитель', 'driver',
                           'гид', 'guide', 'яхта', 'yacht', 'кейтеринг']
        for kw in supplier_keywords:
            if kw in all_text:
                scores["поставщик"] += 2

        # Сотрудники
        staff_keywords = ['офис', 'зарплата', 'смена', 'график', 'отпуск', 'meeting']
        for kw in staff_keywords:
            if kw in all_text:
                scores["сотрудник"] += 3

        # Клиенты (базовый вес)
        client_keywords = ['хочу', 'интересует', 'сколько', 'экскурсия', 'тур', 'билет']
        for kw in client_keywords:
            if kw in all_text:
                scores["клиент"] += 1

        # Определяем тип с максимальным весом
        contact_type = max(scores, key=scores.get)
        if scores[contact_type] == 0:
            contact_type = "клиент"

        # Подтип
        subtype_map = {
            "клиент": "турист",
            "агент": "турагент",
            "поставщик": "водитель",
            "сотрудник": "менеджер"
        }
        subtype = subtype_map.get(contact_type, "турист")

        # Уточнение подтипа
        if contact_type == "клиент":
            if any(w in all_text for w in ['vip', 'люкс', 'premium', 'private']):
                subtype = "VIP"
            elif any(w in all_text for w in ['компания', 'корпоратив', 'team']):
                subtype = "корпоративный"
        elif contact_type == "поставщик":
            if any(w in all_text for w in ['курс', 'обмен', 'exchange']):
                subtype = "обменник"
            elif any(w in all_text for w in ['гид', 'guide']):
                subtype = "гид"
            elif any(w in all_text for w in ['яхта', 'yacht']):
                subtype = "яхтсмен"

        return {
            "jid": jid,
            "contact_type": contact_type,
            "subtype": subtype,
            "confidence": 0.5,
            "key_indicators": [f"Найдено ключевых слов: {scores[contact_type]}"],
            "message_count": len(messages),
            "classified_at": datetime.now().isoformat()
        }


# ═══════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def load_messages(messages_path: Path) -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Загрузить все сообщения и сгруппировать по JID."""
    messages = []
    messages_by_jid = defaultdict(list)

    if not messages_path.exists():
        print(f"ОШИБКА: Файл не найден: {messages_path}")
        return messages, messages_by_jid

    print(f"Загрузка сообщений из: {messages_path}")

    with open(messages_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                msg['_line_num'] = line_num
                messages.append(msg)

                jid = msg.get('jid', '')
                if jid:
                    messages_by_jid[jid].append(msg)
            except json.JSONDecodeError as e:
                if line_num <= 5:
                    print(f"  Строка {line_num}: ошибка JSON")

    print(f"Загружено: {len(messages)} сообщений, {len(messages_by_jid)} контактов")
    return messages, dict(messages_by_jid)


def save_classified_messages(messages: List[Dict], output_path: Path):
    """Сохранить классифицированные сообщения в JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for msg in messages:
            f.write(json.dumps(msg, ensure_ascii=False) + '\n')

    print(f"Сохранено: {output_path}")


def save_contact_classifications(classifications: List[Dict], output_path: Path):
    """Сохранить классификации контактов в JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Сортируем по типу контакта
    sorted_classifications = sorted(
        classifications,
        key=lambda x: (x.get('contact_type', ''), -x.get('confidence', 0))
    )

    output = {
        "generated_at": datetime.now().isoformat(),
        "total_contacts": len(classifications),
        "by_type": {},
        "contacts": sorted_classifications
    }

    # Подсчёт по типам
    for c in classifications:
        ct = c.get('contact_type', 'unknown')
        if ct not in output["by_type"]:
            output["by_type"][ct] = 0
        output["by_type"][ct] += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Сохранено: {output_path}")


def print_statistics(contact_classifications: List[Dict], message_intents: Dict[str, int]):
    """Вывести статистику классификации."""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА КЛАССИФИКАЦИИ")
    print("=" * 60)

    # Контакты
    print("\nКОНТАКТЫ ПО ТИПАМ:")
    print("-" * 40)
    by_type = defaultdict(int)
    for c in contact_classifications:
        by_type[c.get('contact_type', 'unknown')] += 1

    for ct, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {ct:15}: {count}")

    # Намерения сообщений
    print("\nНАМЕРЕНИЯ СООБЩЕНИЙ:")
    print("-" * 40)
    for intent, count in sorted(message_intents.items(), key=lambda x: -x[1]):
        print(f"  {intent:15}: {count}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Умная классификация сообщений через Claude API"
    )
    parser.add_argument(
        "--input",
        default=str(RAW_DIR / "all_messages.jsonl"),
        help="Путь к all_messages.jsonl"
    )
    parser.add_argument(
        "--output-messages",
        default=str(RAW_DIR / "classified_messages.jsonl"),
        help="Путь для сохранения classified_messages.jsonl"
    )
    parser.add_argument(
        "--output-contacts",
        default=str(JSON_DIR / "contact_classifications.json"),
        help="Путь для сохранения contact_classifications.json"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Размер батча для API (по умолчанию: {BATCH_SIZE})"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Не использовать кэш"
    )
    parser.add_argument(
        "--force-rules",
        action="store_true",
        help="Использовать только rules-based (без API)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Ограничить количество обрабатываемых сообщений (0 = все)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("УМНАЯ КЛАССИФИКАЦИЯ ЧЕРЕЗ CLAUDE API")
    print("=" * 60)
    print(f"\nВходной файл: {args.input}")
    print(f"Выходные файлы:")
    print(f"  - {args.output_messages}")
    print(f"  - {args.output_contacts}")
    print(f"API ключ: {'настроен' if CLAUDE_API_KEY else 'НЕ НАСТРОЕН (rules-based режим)'}")

    # Инициализация кэша
    cache = ClassificationCache(CACHE_FILE) if not args.no_cache else ClassificationCache(Path("/dev/null"))

    # Инициализация классификатора
    api_key = "" if args.force_rules else CLAUDE_API_KEY
    classifier = ClaudeClassifier(api_key, cache)

    # Загрузка данных
    messages, messages_by_jid = load_messages(Path(args.input))

    if not messages:
        print("ОШИБКА: Нет сообщений для обработки")
        sys.exit(1)

    # Ограничение количества
    if args.limit > 0:
        messages = messages[:args.limit]
        print(f"\nОграничено до {args.limit} сообщений")

    # ═══════════════════════════════════════════════════════════
    # КЛАССИФИКАЦИЯ СООБЩЕНИЙ
    # ═══════════════════════════════════════════════════════════

    print(f"\n[1/2] Классификация сообщений (батч: {args.batch_size})...")

    classified_messages = []
    message_intents = defaultdict(int)

    for i in range(0, len(messages), args.batch_size):
        batch = messages[i:i + args.batch_size]

        if args.verbose:
            print(f"  Батч {i // args.batch_size + 1}: {i+1}-{min(i+args.batch_size, len(messages))}")

        classifications = classifier.classify_messages_batch(batch)

        for msg, classification in zip(batch, classifications):
            # Объединяем исходное сообщение с классификацией
            classified_msg = {**msg}
            classified_msg['classification'] = classification
            classified_messages.append(classified_msg)

            # Статистика
            intent = classification.get('intent', 'other')
            message_intents[intent] += 1

    # ═══════════════════════════════════════════════════════════
    # КЛАССИФИКАЦИЯ КОНТАКТОВ
    # ═══════════════════════════════════════════════════════════

    print(f"\n[2/2] Классификация контактов ({len(messages_by_jid)} шт.)...")

    contact_classifications = []

    for i, (jid, jid_messages) in enumerate(messages_by_jid.items()):
        if args.verbose and (i + 1) % 50 == 0:
            print(f"  Обработано: {i + 1}/{len(messages_by_jid)}")

        # Информация о контакте из первого сообщения
        contact_info = {
            'name': jid_messages[0].get('chat_name', ''),
            'jid': jid
        }

        classification = classifier.classify_contact(jid, jid_messages, contact_info)
        contact_classifications.append(classification)

    # Сохранение кэша
    cache.finalize()

    # ═══════════════════════════════════════════════════════════
    # СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
    # ═══════════════════════════════════════════════════════════

    print("\nСохранение результатов...")

    save_classified_messages(classified_messages, Path(args.output_messages))
    save_contact_classifications(contact_classifications, Path(args.output_contacts))

    # Статистика
    print_statistics(contact_classifications, message_intents)

    print("\nКлассификация завершена!")


if __name__ == "__main__":
    main()
