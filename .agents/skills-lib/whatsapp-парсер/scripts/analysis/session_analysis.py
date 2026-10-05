#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ сессий (диалогов) из WhatsApp чатов.

Функции:
- Разбиение на сессии (gap > 4 часов = новый диалог)
- Определение результата диалога (sale, rejection, pending)
- Определение темы диалога
- Парсинг reply-to цепочек
- Анализ паттернов диалогов
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple, Any

# Добавляем путь к utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import ANALYTICS_DIR, JSON_DIR, ensure_directories

sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ СЕССИЙ
# ═══════════════════════════════════════════════════════════════

SESSION_CONFIG = {
    "gap_hours": 4,           # Пауза в часах для разделения сессий
    "min_messages": 2,        # Минимум сообщений для сессии
    "max_session_days": 30,   # Максимальная длительность сессии в днях
}


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ОПРЕДЕЛЕНИЯ РЕЗУЛЬТАТА
# ═══════════════════════════════════════════════════════════════

RESULT_PATTERNS = {
    "sale": {
        "patterns": [
            r"(?i)(бронь\s+подтвержден|подтверждаю\s+бронь)",
            r"(?i)(оплата\s+получен|оплачено|деньги\s+получен)",
            r"(?i)(заказ\s+принят|заказ\s+подтверждён)",
            r"(?i)(ваучер\s+отправлен|билеты\s+отправлен)",
            r"(?i)(услуга\s+оказана|всё\s+прошло\s+отлично)",
            r"(?i)(спасибо\s+за\s+заказ|благодарим\s+за\s+выбор)",
        ],
        "weight": 3.0
    },
    "rejection": {
        "patterns": [
            r"(?i)(дорого|слишком\s+дорого|не\s+подходит\s+цена)",
            r"(?i)(передумал|отказываюсь|не\s+нужно)",
            r"(?i)(уже\s+забронировали\s+в\s+другом|нашли\s+дешевле)",
            r"(?i)(даты\s+не\s+подходят|не\s+успеваем)",
            r"(?i)(отменяем|отмена\s+брони)",
            r"(?i)(не\s+едем|поездка\s+отменена)",
        ],
        "weight": 2.5
    },
    "pending": {
        "patterns": [
            r"(?i)(подумаю|подумаем|посоветуюсь)",
            r"(?i)(перезвоню|напишу\s+позже|свяжусь)",
            r"(?i)(пока\s+не\s+решили|ещё\s+думаем)",
            r"(?i)(жду\s+ответ|ожидаю\s+подтверждения)",
        ],
        "weight": 1.5
    }
}


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ОПРЕДЕЛЕНИЯ ТЕМЫ
# ═══════════════════════════════════════════════════════════════

TOPIC_PATTERNS = {
    "desert_safari": {
        "patterns": [
            r"(?i)(сафари|пустын|джип|desert|safari)",
            r"(?i)(дюн|quad|квадроцикл|camel|верблюд)",
            r"(?i)(барбекю\s+в\s+пустыне|bbq\s+desert)",
        ],
        "keywords": ["сафари", "пустыня", "desert", "safari"]
    },
    "city_tour": {
        "patterns": [
            r"(?i)(экскурси[яю]|city\s+tour|обзорн)",
            r"(?i)(достопримечательност|museum|музей)",
            r"(?i)(абу[\s-]?даби|abu[\s-]?dhabi)",
            r"(?i)(бурдж\s+халифа|burj\s+khalifa)",
        ],
        "keywords": ["экскурсия", "тур", "city tour", "достопримечательности"]
    },
    "yacht": {
        "patterns": [
            r"(?i)(яхт[ау]|yacht|катер|boat)",
            r"(?i)(марин[ау]|marina|морск)",
            r"(?i)(рыбалк[ау]|fishing)",
        ],
        "keywords": ["яхта", "yacht", "катер", "лодка"]
    },
    "transfer": {
        "patterns": [
            r"(?i)(трансфер|transfer|такси|taxi)",
            r"(?i)(аэропорт|airport|встреча|проводы)",
            r"(?i)(машин[ау]\s+с\s+водителем|chauffeur)",
        ],
        "keywords": ["трансфер", "аэропорт", "transfer", "такси"]
    },
    "tickets": {
        "patterns": [
            r"(?i)(билет[ы]?|ticket)",
            r"(?i)(парк\s+развлечений|theme\s+park)",
            r"(?i)(ferrari\s+world|aquaventure|аквапарк)",
            r"(?i)(img\s+world|global\s+village)",
        ],
        "keywords": ["билет", "парк", "аттракцион"]
    },
    "hotel": {
        "patterns": [
            r"(?i)(отел[ья]|hotel|гостиниц)",
            r"(?i)(бронирование\s+номер|room\s+booking)",
            r"(?i)(проживание|accommodation)",
        ],
        "keywords": ["отель", "hotel", "проживание"]
    },
    "visa": {
        "patterns": [
            r"(?i)(виз[ау]|visa)",
            r"(?i)(оформление\s+визы|visa\s+processing)",
        ],
        "keywords": ["виза", "visa"]
    },
    "exchange": {
        "patterns": [
            r"(?i)(обмен|exchange|курс\s+валют)",
            r"(?i)(дирхам[ы]?|рубл[иь]|доллар)",
            r"(?i)(наличн\w+|cash)",
        ],
        "keywords": ["обмен", "курс", "валюта"]
    },
    "general_inquiry": {
        "patterns": [
            r"(?i)(что\s+есть|какие\s+услуги|прайс|каталог)",
            r"(?i)(расскажите|подробнее|информация)",
        ],
        "keywords": ["информация", "прайс", "каталог"]
    }
}


# ═══════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class Session:
    """Одна сессия (диалог)"""
    session_id: str
    chat_id: str
    start_time: str
    end_time: str
    duration_hours: float
    message_count: int
    messages: List[Dict] = field(default_factory=list)
    initiator: str = ""           # client / manager
    result: str = "unknown"       # sale / rejection / pending / unknown
    result_confidence: float = 0.0
    topics: List[str] = field(default_factory=list)
    primary_topic: str = ""
    has_price_discussion: bool = False
    has_booking_attempt: bool = False
    reply_chains: List[Dict] = field(default_factory=list)


@dataclass
class ChatSessionAnalysis:
    """Результат анализа сессий для одного чата"""
    chat_id: str
    contact_name: str
    total_sessions: int
    sessions: List[Dict]
    topics_summary: Dict[str, int]
    results_summary: Dict[str, int]
    avg_session_duration_hours: float
    avg_messages_per_session: float
    total_messages: int
    first_contact_date: str
    last_contact_date: str


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Парсит timestamp в datetime"""
    if not ts_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(ts_str.replace("Z", "+00:00"), fmt)
        except ValueError:
            continue

    return None


# ═══════════════════════════════════════════════════════════════
# РАЗБИЕНИЕ НА СЕССИИ
# ═══════════════════════════════════════════════════════════════

def split_into_sessions(messages: List[Dict], chat_id: str = "") -> List[Session]:
    """
    Разбивает сообщения на сессии.

    Критерий: пауза более SESSION_CONFIG['gap_hours'] часов = новая сессия.

    Args:
        messages: Отсортированный по времени список сообщений
        chat_id: ID чата

    Returns:
        Список сессий
    """
    if not messages:
        return []

    sessions = []
    current_session_messages = []
    last_timestamp = None
    gap_threshold = timedelta(hours=SESSION_CONFIG["gap_hours"])
    session_counter = 0

    for msg in messages:
        timestamp = parse_timestamp(msg.get("timestamp", ""))

        if not timestamp:
            if current_session_messages:
                current_session_messages.append(msg)
            continue

        # Проверяем, нужно ли начать новую сессию
        if last_timestamp:
            gap = timestamp - last_timestamp

            if gap > gap_threshold:
                # Завершаем текущую сессию
                if len(current_session_messages) >= SESSION_CONFIG["min_messages"]:
                    session = create_session(
                        current_session_messages,
                        chat_id,
                        session_counter
                    )
                    sessions.append(session)
                    session_counter += 1

                # Начинаем новую сессию
                current_session_messages = []

        current_session_messages.append(msg)
        last_timestamp = timestamp

    # Завершаем последнюю сессию
    if len(current_session_messages) >= SESSION_CONFIG["min_messages"]:
        session = create_session(
            current_session_messages,
            chat_id,
            session_counter
        )
        sessions.append(session)

    return sessions


def create_session(messages: List[Dict], chat_id: str, index: int) -> Session:
    """Создаёт объект сессии из списка сообщений"""
    start_time = messages[0].get("timestamp", "")
    end_time = messages[-1].get("timestamp", "")

    # Вычисляем длительность
    start_dt = parse_timestamp(start_time)
    end_dt = parse_timestamp(end_time)
    duration_hours = 0.0

    if start_dt and end_dt:
        duration_hours = (end_dt - start_dt).total_seconds() / 3600

    # Определяем инициатора
    first_sender_type = messages[0].get("sender_type", "unknown")

    # Определяем результат
    result, confidence = detect_session_result(messages)

    # Определяем темы
    topics = detect_session_topics(messages)
    primary_topic = topics[0] if topics else "unknown"

    # Проверяем обсуждение цены и попытки бронирования
    has_price = any(
        re.search(r"(?i)(цена|стоимость|сколько\s+стоит|\d+\s*(AED|USD|руб))", msg.get("text", ""))
        for msg in messages
    )
    has_booking = any(
        re.search(r"(?i)(брон|забронировать|подтверждаю)", msg.get("text", ""))
        for msg in messages
    )

    # Парсим reply-to цепочки
    reply_chains = parse_reply_chains(messages)

    return Session(
        session_id=f"{chat_id}_session_{index}",
        chat_id=chat_id,
        start_time=start_time,
        end_time=end_time,
        duration_hours=round(duration_hours, 2),
        message_count=len(messages),
        messages=messages,  # Можно убрать для экономии памяти
        initiator=first_sender_type,
        result=result,
        result_confidence=confidence,
        topics=topics,
        primary_topic=primary_topic,
        has_price_discussion=has_price,
        has_booking_attempt=has_booking,
        reply_chains=reply_chains
    )


# ═══════════════════════════════════════════════════════════════
# ОПРЕДЕЛЕНИЕ РЕЗУЛЬТАТА СЕССИИ
# ═══════════════════════════════════════════════════════════════

def detect_session_result(messages: List[Dict]) -> Tuple[str, float]:
    """
    Определяет результат сессии (диалога).

    Returns:
        Tuple[result, confidence]
    """
    scores = {"sale": 0.0, "rejection": 0.0, "pending": 0.0}

    for msg in messages:
        text = msg.get("text", "")

        for result_type, config in RESULT_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, text):
                    scores[result_type] += config["weight"]

    # Определяем победителя
    if max(scores.values()) == 0:
        return "unknown", 0.0

    best_result = max(scores, key=scores.get)
    best_score = scores[best_result]

    # Нормализуем confidence
    confidence = min(best_score / 5.0, 1.0)

    return best_result, round(confidence, 2)


# ═══════════════════════════════════════════════════════════════
# ОПРЕДЕЛЕНИЕ ТЕМЫ СЕССИИ
# ═══════════════════════════════════════════════════════════════

def detect_session_topics(messages: List[Dict]) -> List[str]:
    """
    Определяет темы, обсуждаемые в сессии.

    Returns:
        Список тем, отсортированный по релевантности
    """
    topic_scores = defaultdict(float)

    for msg in messages:
        text = msg.get("text", "")

        for topic, config in TOPIC_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, text):
                    topic_scores[topic] += 1.0

            # Бонус за ключевые слова
            for keyword in config.get("keywords", []):
                if keyword.lower() in text.lower():
                    topic_scores[topic] += 0.5

    # Сортируем по релевантности
    sorted_topics = sorted(
        topic_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [topic for topic, score in sorted_topics if score > 0]


# ═══════════════════════════════════════════════════════════════
# ПАРСИНГ REPLY-TO ЦЕПОЧЕК
# ═══════════════════════════════════════════════════════════════

def parse_reply_chains(messages: List[Dict]) -> List[Dict]:
    """
    Парсит reply-to цепочки в сообщениях.

    Ищет паттерны:
    - Цитирование с ">" в начале строки
    - Упоминание "в ответ на" или "replying to"
    - Структурные цитаты

    Returns:
        Список цепочек ответов
    """
    reply_chains = []

    # Паттерны для reply-to
    reply_patterns = [
        r"(?i)^>(.+)$",                         # Цитирование с >
        r"(?i)в\s+ответ\s+на[:\s]+(.+)",        # "В ответ на"
        r"(?i)replying\s+to[:\s]+(.+)",         # "Replying to"
        r"(?i)^\"(.+)\"\s*-\s*(.+)",            # "Цитата" - имя
    ]

    for i, msg in enumerate(messages):
        text = msg.get("text", "")

        for pattern in reply_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                reply_chains.append({
                    "message_index": i,
                    "timestamp": msg.get("timestamp", ""),
                    "sender": msg.get("sender", ""),
                    "quoted_text": match.group(1)[:100] if match.groups() else "",
                    "reply_text": text[:150]
                })
                break

    return reply_chains


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ЧАТА
# ═══════════════════════════════════════════════════════════════

def analyze_chat_sessions(messages: List[Dict], chat_id: str = "", contact_name: str = "") -> ChatSessionAnalysis:
    """
    Полный анализ сессий для одного чата.
    """
    # Разбиваем на сессии
    sessions = split_into_sessions(messages, chat_id)

    # Подсчёт тем
    topics_summary = defaultdict(int)
    for session in sessions:
        for topic in session.topics:
            topics_summary[topic] += 1

    # Подсчёт результатов
    results_summary = defaultdict(int)
    for session in sessions:
        results_summary[session.result] += 1

    # Средние значения
    avg_duration = 0.0
    avg_messages = 0.0

    if sessions:
        avg_duration = sum(s.duration_hours for s in sessions) / len(sessions)
        avg_messages = sum(s.message_count for s in sessions) / len(sessions)

    # Даты
    first_date = messages[0].get("timestamp", "") if messages else ""
    last_date = messages[-1].get("timestamp", "") if messages else ""

    # Сериализуем сессии (без полного списка сообщений)
    sessions_data = []
    for s in sessions:
        session_dict = asdict(s)
        session_dict.pop("messages", None)  # Убираем полный список сообщений
        sessions_data.append(session_dict)

    return ChatSessionAnalysis(
        chat_id=chat_id,
        contact_name=contact_name,
        total_sessions=len(sessions),
        sessions=sessions_data,
        topics_summary=dict(topics_summary),
        results_summary=dict(results_summary),
        avg_session_duration_hours=round(avg_duration, 2),
        avg_messages_per_session=round(avg_messages, 1),
        total_messages=len(messages),
        first_contact_date=first_date,
        last_contact_date=last_date
    )


# ═══════════════════════════════════════════════════════════════
# АГРЕГИРОВАННАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

def calculate_aggregate_statistics(analyses: List[ChatSessionAnalysis]) -> Dict[str, Any]:
    """Вычисляет агрегированную статистику по всем чатам"""
    if not analyses:
        return {}

    total_chats = len(analyses)
    total_sessions = sum(a.total_sessions for a in analyses)
    total_messages = sum(a.total_messages for a in analyses)

    # Агрегация тем
    all_topics = defaultdict(int)
    for a in analyses:
        for topic, count in a.topics_summary.items():
            all_topics[topic] += count

    # Агрегация результатов
    all_results = defaultdict(int)
    for a in analyses:
        for result, count in a.results_summary.items():
            all_results[result] += count

    # Средние значения
    avg_sessions_per_chat = total_sessions / total_chats if total_chats > 0 else 0
    avg_duration = sum(a.avg_session_duration_hours for a in analyses) / total_chats if total_chats > 0 else 0
    avg_messages = sum(a.avg_messages_per_session for a in analyses) / total_chats if total_chats > 0 else 0

    # Конверсия сессий
    sales = all_results.get("sale", 0)
    total_outcomes = sales + all_results.get("rejection", 0) + all_results.get("pending", 0)
    conversion_rate = (sales / total_outcomes * 100) if total_outcomes > 0 else 0

    return {
        "summary": {
            "total_chats": total_chats,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "avg_sessions_per_chat": round(avg_sessions_per_chat, 1),
            "avg_session_duration_hours": round(avg_duration, 2),
            "avg_messages_per_session": round(avg_messages, 1),
            "session_conversion_rate": round(conversion_rate, 2)
        },
        "topics_distribution": dict(sorted(all_topics.items(), key=lambda x: x[1], reverse=True)),
        "results_distribution": dict(all_results),
        "top_topics": list(sorted(all_topics.items(), key=lambda x: x[1], reverse=True))[:5],
        "generated_at": datetime.now().isoformat()
    }


# ═══════════════════════════════════════════════════════════════
# ЧТЕНИЕ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_messages_jsonl(filepath: Path) -> List[Dict]:
    """Загружает сообщения из JSONL файла"""
    messages = []

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


def group_messages_by_chat(messages: List[Dict]) -> Dict[str, List[Dict]]:
    """Группирует сообщения по чатам"""
    chats = defaultdict(list)

    for msg in messages:
        chat_id = msg.get("jid", msg.get("chat_id", "unknown"))
        chats[chat_id].append(msg)

    return dict(chats)


def determine_sender_type(msg: Dict) -> str:
    """Определяет тип отправителя"""
    sender = msg.get("sender", "")
    if sender == "Я" or sender.lower() in ["я", "me", "i"]:
        return "manager"
    return "client"


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Главная функция анализа сессий"""
    parser = argparse.ArgumentParser(description="Анализ сессий (диалогов) из WhatsApp чатов")
    parser.add_argument("--input", "-i", default=str(JSON_DIR / "all_messages.jsonl"),
                        help="Путь к JSONL файлу с сообщениями")
    parser.add_argument("--output", "-o", default=str(ANALYTICS_DIR / "session_analysis.json"),
                        help="Путь для сохранения результатов")
    parser.add_argument("--detailed", "-d", action="store_true",
                        help="Включить детальный анализ каждого чата")
    parser.add_argument("--gap-hours", type=float, default=4.0,
                        help="Пауза в часах для разделения сессий (по умолчанию 4)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Ограничить количество чатов для анализа")

    args = parser.parse_args()

    # Обновляем конфигурацию
    SESSION_CONFIG["gap_hours"] = args.gap_hours

    # Проверяем входной файл
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Файл не найден: {input_path}")
        print("Создаю демо-анализ...")

        # Демо-данные
        demo_analysis = ChatSessionAnalysis(
            chat_id="demo_1",
            contact_name="Демо клиент",
            total_sessions=3,
            sessions=[
                {
                    "session_id": "demo_1_session_0",
                    "chat_id": "demo_1",
                    "start_time": "2026-01-01T10:00:00",
                    "end_time": "2026-01-01T12:30:00",
                    "duration_hours": 2.5,
                    "message_count": 15,
                    "initiator": "client",
                    "result": "pending",
                    "result_confidence": 0.6,
                    "topics": ["desert_safari", "transfer"],
                    "primary_topic": "desert_safari",
                    "has_price_discussion": True,
                    "has_booking_attempt": False,
                    "reply_chains": []
                },
                {
                    "session_id": "demo_1_session_1",
                    "chat_id": "demo_1",
                    "start_time": "2026-01-02T14:00:00",
                    "end_time": "2026-01-02T15:45:00",
                    "duration_hours": 1.75,
                    "message_count": 20,
                    "initiator": "client",
                    "result": "sale",
                    "result_confidence": 0.85,
                    "topics": ["desert_safari"],
                    "primary_topic": "desert_safari",
                    "has_price_discussion": True,
                    "has_booking_attempt": True,
                    "reply_chains": []
                }
            ],
            topics_summary={"desert_safari": 2, "transfer": 1},
            results_summary={"pending": 1, "sale": 1, "unknown": 1},
            avg_session_duration_hours=1.8,
            avg_messages_per_session=12.0,
            total_messages=45,
            first_contact_date="2026-01-01T10:00:00",
            last_contact_date="2026-01-15T18:30:00"
        )

        result = {
            "aggregate_statistics": calculate_aggregate_statistics([demo_analysis]),
            "chat_analyses": [asdict(demo_analysis)],
            "demo_mode": True
        }

        ensure_directories()
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"Демо-результат сохранён: {output_path}")
        return

    print(f"Загрузка сообщений из {input_path}...")
    messages = load_messages_jsonl(input_path)
    print(f"Загружено {len(messages)} сообщений")

    # Группируем по чатам
    chats = group_messages_by_chat(messages)
    print(f"Найдено {len(chats)} чатов")

    # Анализируем каждый чат
    analyses = []
    chat_items = list(chats.items())

    if args.limit > 0:
        chat_items = chat_items[:args.limit]

    for chat_id, chat_messages in chat_items:
        # Добавляем тип отправителя
        for msg in chat_messages:
            msg["sender_type"] = determine_sender_type(msg)

        # Сортируем по времени
        chat_messages.sort(key=lambda x: x.get("timestamp", ""))

        # Анализируем
        contact_name = chat_messages[0].get("sender", "") if chat_messages else ""
        analysis = analyze_chat_sessions(chat_messages, chat_id, contact_name)
        analyses.append(analysis)

    print(f"Проанализировано {len(analyses)} чатов")

    # Вычисляем агрегированную статистику
    aggregate = calculate_aggregate_statistics(analyses)

    # Формируем результат
    result = {
        "aggregate_statistics": aggregate,
        "chat_analyses": [asdict(a) for a in analyses] if args.detailed else [],
        "total_chats": len(analyses),
        "session_gap_hours": SESSION_CONFIG["gap_hours"]
    }

    # Сохраняем
    ensure_directories()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nРезультат сохранён: {output_path}")

    # Выводим краткую статистику
    print("\n" + "=" * 50)
    print("АНАЛИЗ СЕССИЙ (ДИАЛОГОВ)")
    print("=" * 50)

    summary = aggregate.get("summary", {})
    print(f"Всего чатов: {summary.get('total_chats', 0)}")
    print(f"Всего сессий: {summary.get('total_sessions', 0)}")
    print(f"Всего сообщений: {summary.get('total_messages', 0)}")
    print(f"Среднее сессий на чат: {summary.get('avg_sessions_per_chat', 0)}")
    print(f"Средняя длительность сессии: {summary.get('avg_session_duration_hours', 0)} часов")
    print(f"Среднее сообщений в сессии: {summary.get('avg_messages_per_session', 0)}")
    print(f"Конверсия сессий: {summary.get('session_conversion_rate', 0)}%")

    print("\nРаспределение результатов:")
    for result, count in aggregate.get("results_distribution", {}).items():
        print(f"  {result}: {count}")

    print("\nТоп-5 тем:")
    for topic, count in aggregate.get("top_topics", []):
        print(f"  {topic}: {count}")


if __name__ == "__main__":
    main()
