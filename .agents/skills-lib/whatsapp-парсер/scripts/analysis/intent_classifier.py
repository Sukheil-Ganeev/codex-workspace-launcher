#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Классификация интентов (намерений) в сообщениях WhatsApp чатов.

Интенты:
- PRICE_REQUEST - запрос цены
- AVAILABILITY_REQUEST - проверка наличия
- BOOKING_CONFIRM - подтверждение бронирования
- BOOKING_CANCEL - отмена бронирования
- INFO_REQUEST - запрос информации
- PAYMENT_CONFIRM - подтверждение оплаты
- PAYMENT_REQUEST - запрос реквизитов
- COMPLAINT - жалоба/проблема
- LOGISTICS - информация о логистике
- GREETING - приветствие
- GOODBYE - прощание
- GRATITUDE - благодарность
- NEGOTIATION - торг/скидка
- OTHER - прочее
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any

# Добавляем путь к utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import ANALYTICS_DIR, JSON_DIR, ensure_directories

sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# ОПРЕДЕЛЕНИЯ ИНТЕНТОВ
# ═══════════════════════════════════════════════════════════════

INTENT_PATTERNS = {
    "PRICE_REQUEST": {
        "description": "Запрос цены/стоимости",
        "patterns": [
            r"(?i)(скольк[оа]\s+сто[ия]т|как[ая]+\s+цен[ау]|поч[её]м)",
            r"(?i)(прайс|стоимость|цен[ау]\s+на|тариф\w*)",
            r"(?i)(во\s+сколько\s+обойд[её]тся|сколько\s+будет\s+стоить)",
            r"(?i)(какая\s+цена\s+за|почём\s+у\s+вас)",
        ],
        "weight": 2.0,
        "priority": 1,
        "requires_response": True,
        "response_sla_minutes": 60
    },

    "AVAILABILITY_REQUEST": {
        "description": "Проверка наличия/доступности",
        "patterns": [
            r"(?i)(есть\s+ли|доступн[аоы]|свободн[аоы])",
            r"(?i)(можно\s+(?:ли\s+)?забронировать)",
            r"(?i)(наличие|в\s+наличии|есть\s+места)",
            r"(?i)(когда\s+(?:есть|можно|доступно))",
            r"(?i)(на\s+какие\s+даты\s+есть)",
        ],
        "weight": 1.8,
        "priority": 2,
        "requires_response": True,
        "response_sla_minutes": 60
    },

    "BOOKING_CONFIRM": {
        "description": "Подтверждение бронирования",
        "patterns": [
            r"(?i)(бронирую|забронируйте|резервирую)",
            r"(?i)(подтверждаю\s+(?:бронь|заказ))",
            r"(?i)(давайте|договорились|согласен|согласна)",
            r"(?i)(беру|берём|оформляйте)",
            r"(?i)(всё\s+устраивает|подходит)",
            r"(?i)(да[,\s]+(?:бронируем|забронируйте))",
        ],
        "weight": 2.5,
        "priority": 1,
        "requires_response": True,
        "response_sla_minutes": 15
    },

    "BOOKING_CANCEL": {
        "description": "Отмена бронирования",
        "patterns": [
            r"(?i)(отмен(?:яю|яем|ите)\s+(?:бронь|заказ|бронирование))",
            r"(?i)(отказыва(?:юсь|емся))",
            r"(?i)(не\s+нужно|больше\s+не\s+нужно)",
            r"(?i)(передумал[иа]?)",
            r"(?i)(снимите\s+бронь|аннулируйте)",
        ],
        "weight": 2.5,
        "priority": 1,
        "requires_response": True,
        "response_sla_minutes": 15
    },

    "INFO_REQUEST": {
        "description": "Запрос информации",
        "patterns": [
            r"(?i)(расскажите|подробнее|информаци[яю])",
            r"(?i)(что\s+включен[оа]|что\s+входит)",
            r"(?i)(какие\s+(?:есть|бывают)\s+(?:варианты|опции))",
            r"(?i)(опишите|детали|подробности)",
            r"(?i)(как\s+(?:это|оно)\s+работает)",
            r"(?i)(объясните|уточните)",
        ],
        "weight": 1.5,
        "priority": 3,
        "requires_response": True,
        "response_sla_minutes": 60
    },

    "PAYMENT_CONFIRM": {
        "description": "Подтверждение оплаты",
        "patterns": [
            r"(?i)(оплатил[аи]?|перев[её]л[аи]?|отправил[аи]?\s+(?:деньги|оплату))",
            r"(?i)(деньги\s+(?:отправил|перевёл|ушли))",
            r"(?i)(оплата\s+(?:прошла|отправлена))",
            r"(?i)(скинул[аи]?\s+(?:на\s+карту)?)",
            r"(?i)(чек|квитанция|подтверждение\s+оплаты)",
        ],
        "weight": 2.5,
        "priority": 1,
        "requires_response": True,
        "response_sla_minutes": 15
    },

    "PAYMENT_REQUEST": {
        "description": "Запрос реквизитов для оплаты",
        "patterns": [
            r"(?i)(куда\s+(?:платить|переводить|перевести))",
            r"(?i)(реквизит[ыа])",
            r"(?i)(как\s+оплатить|способы?\s+оплаты)",
            r"(?i)(на\s+как[уо][йю]\s+карт[уа])",
            r"(?i)(счёт\s+(?:на\s+оплату|выставьте)|инвойс)",
            r"(?i)(iban|номер\s+(?:карты|счёта))",
        ],
        "weight": 2.0,
        "priority": 2,
        "requires_response": True,
        "response_sla_minutes": 15
    },

    "COMPLAINT": {
        "description": "Жалоба/проблема",
        "patterns": [
            r"(?i)(проблем[аы]|жалоб[ау])",
            r"(?i)(не\s+работает|сломан|испорчен)",
            r"(?i)(недовол[ье]н|разочарован)",
            r"(?i)(ужасн[оый]|кошмар|плохо)",
            r"(?i)(верн[иу]те\s+деньги|возврат)",
            r"(?i)(водитель\s+(?:не\s+приехал|опаздывает))",
            r"(?i)(где\s+(?:мой|наш)\s+(?:заказ|водитель))",
        ],
        "weight": 3.0,
        "priority": 0,  # Высший приоритет!
        "requires_response": True,
        "response_sla_minutes": 5
    },

    "LOGISTICS": {
        "description": "Информация о логистике (пикап, время, место)",
        "patterns": [
            r"(?i)(забер[ия]те|пикап|pick[\s-]?up)",
            r"(?i)(встреч(?:айте|а)|заеха(?:ть|ли))",
            r"(?i)(адрес|место\s+встречи|точка\s+сбора)",
            r"(?i)(во\s+сколько|в\s+какое\s+время)",
            r"(?i)(отел[ья]|hotel|живём\s+в)",
            r"(?i)(аэропорт|терминал|рейс)",
        ],
        "weight": 1.5,
        "priority": 2,
        "requires_response": True,
        "response_sla_minutes": 30
    },

    "GREETING": {
        "description": "Приветствие",
        "patterns": [
            r"(?i)^(привет|здравствуйте?|добр[ыо][йе]\s+(?:день|утро|вечер)|салам|hi|hello)[\s!.,]*$",
            r"(?i)^(доброе\s+время\s+суток|приветствую)[\s!.,]*$",
        ],
        "weight": 0.5,
        "priority": 10,
        "requires_response": False,
        "response_sla_minutes": None
    },

    "GOODBYE": {
        "description": "Прощание",
        "patterns": [
            r"(?i)(до\s+свидания|пока|всего\s+(?:доброго|хорошего))",
            r"(?i)(до\s+встречи|до\s+связи|увидимся)",
            r"(?i)(хорошего\s+дня|удачи)",
        ],
        "weight": 0.5,
        "priority": 10,
        "requires_response": False,
        "response_sla_minutes": None
    },

    "GRATITUDE": {
        "description": "Благодарность",
        "patterns": [
            r"(?i)(спасибо|благодарю|thanks|thank\s+you)",
            r"(?i)(признателен|очень\s+благодарны)",
            r"(?i)(огромное\s+спасибо|большое\s+спасибо)",
        ],
        "weight": 0.8,
        "priority": 8,
        "requires_response": False,
        "response_sla_minutes": None
    },

    "NEGOTIATION": {
        "description": "Торг/запрос скидки",
        "patterns": [
            r"(?i)(скидк[ауи]|можно\s+(?:по)?дешевле)",
            r"(?i)(скин(?:ьте|ете)\s+цен[у]|уступите)",
            r"(?i)(торг\s+(?:уместен|возможен)|последняя\s+цена)",
            r"(?i)(если\s+(?:оптом|больше|много))",
            r"(?i)(акци[яи]|промокод|special\s+offer)",
        ],
        "weight": 1.8,
        "priority": 3,
        "requires_response": True,
        "response_sla_minutes": 60
    },

    "CONFIRMATION_REQUEST": {
        "description": "Запрос подтверждения",
        "patterns": [
            r"(?i)(подтверд(?:ите|ите\s+пожалуйста))",
            r"(?i)(всё\s+(?:верно|правильно)\?)",
            r"(?i)(можете\s+подтвердить)",
            r"(?i)(ждём\s+подтверждения)",
        ],
        "weight": 1.5,
        "priority": 2,
        "requires_response": True,
        "response_sla_minutes": 30
    },

    "STATUS_REQUEST": {
        "description": "Запрос статуса",
        "patterns": [
            r"(?i)(как[ой]?\s+статус|что\s+(?:с|по)\s+(?:моим?|нашим?))",
            r"(?i)(когда\s+будет\s+(?:готово|ответ))",
            r"(?i)(есть\s+(?:новости|обновления))",
            r"(?i)(что\s+(?:там|по\s+заказу))",
        ],
        "weight": 1.5,
        "priority": 3,
        "requires_response": True,
        "response_sla_minutes": 60
    }
}


# ═══════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class IntentDetection:
    """Результат определения интента"""
    intent: str
    confidence: float
    matched_patterns: List[str]
    requires_response: bool
    response_sla_minutes: Optional[int]
    priority: int


@dataclass
class MessageIntentAnalysis:
    """Анализ интента одного сообщения"""
    message_index: int
    timestamp: str
    sender: str
    sender_type: str
    text_preview: str
    primary_intent: str
    primary_confidence: float
    all_intents: List[Dict]
    requires_response: bool
    response_sla_minutes: Optional[int]


@dataclass
class ChatIntentAnalysis:
    """Анализ интентов для одного чата"""
    chat_id: str
    contact_name: str
    total_messages: int
    intents_summary: Dict[str, int]
    messages_by_intent: Dict[str, List[Dict]]
    unresponded_intents: List[Dict]
    first_message_date: str
    last_message_date: str


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ КЛАССИФИКАЦИИ
# ═══════════════════════════════════════════════════════════════

def classify_intent(text: str) -> List[IntentDetection]:
    """
    Классифицирует интент сообщения.

    Args:
        text: Текст сообщения

    Returns:
        Список обнаруженных интентов, отсортированный по confidence
    """
    detections = []

    for intent_name, config in INTENT_PATTERNS.items():
        score = 0.0
        matched = []

        for pattern in config["patterns"]:
            if re.search(pattern, text):
                score += config["weight"]
                matched.append(pattern[:40])

        if score > 0:
            confidence = min(score / 4.0, 1.0)  # Нормализация

            detections.append(IntentDetection(
                intent=intent_name,
                confidence=round(confidence, 2),
                matched_patterns=matched,
                requires_response=config.get("requires_response", True),
                response_sla_minutes=config.get("response_sla_minutes"),
                priority=config.get("priority", 5)
            ))

    # Сортируем по priority (меньше = важнее), затем по confidence
    detections.sort(key=lambda x: (x.priority, -x.confidence))

    return detections


def analyze_message_intent(msg: Dict, index: int) -> MessageIntentAnalysis:
    """
    Анализирует интент одного сообщения.
    """
    text = msg.get("text", "")
    detections = classify_intent(text)

    # Определяем основной интент
    if detections:
        primary = detections[0]
        primary_intent = primary.intent
        primary_confidence = primary.confidence
        requires_response = primary.requires_response
        response_sla = primary.response_sla_minutes
    else:
        primary_intent = "OTHER"
        primary_confidence = 0.0
        requires_response = False
        response_sla = None

    all_intents = [
        {
            "intent": d.intent,
            "confidence": d.confidence,
            "priority": d.priority
        }
        for d in detections
    ]

    return MessageIntentAnalysis(
        message_index=index,
        timestamp=msg.get("timestamp", ""),
        sender=msg.get("sender", ""),
        sender_type=msg.get("sender_type", "unknown"),
        text_preview=text[:100] if text else "",
        primary_intent=primary_intent,
        primary_confidence=primary_confidence,
        all_intents=all_intents,
        requires_response=requires_response,
        response_sla_minutes=response_sla
    )


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ЧАТА
# ═══════════════════════════════════════════════════════════════

def analyze_chat_intents(messages: List[Dict], chat_id: str = "", contact_name: str = "") -> ChatIntentAnalysis:
    """
    Анализирует все интенты в чате.
    """
    intents_summary = defaultdict(int)
    messages_by_intent = defaultdict(list)
    unresponded_intents = []

    # Анализируем каждое сообщение
    last_client_intent = None
    last_client_time = None

    for i, msg in enumerate(messages):
        analysis = analyze_message_intent(msg, i)

        # Подсчитываем интенты
        intents_summary[analysis.primary_intent] += 1

        # Группируем по интентам
        messages_by_intent[analysis.primary_intent].append({
            "message_index": analysis.message_index,
            "timestamp": analysis.timestamp,
            "sender": analysis.sender,
            "text_preview": analysis.text_preview,
            "confidence": analysis.primary_confidence
        })

        # Отслеживаем неотвеченные интенты клиента
        if analysis.sender_type == "client" and analysis.requires_response:
            last_client_intent = analysis
            last_client_time = analysis.timestamp
        elif analysis.sender_type == "manager":
            last_client_intent = None
            last_client_time = None

    # Если последний интент клиента без ответа
    if last_client_intent:
        unresponded_intents.append({
            "intent": last_client_intent.primary_intent,
            "timestamp": last_client_intent.timestamp,
            "text_preview": last_client_intent.text_preview,
            "response_sla_minutes": last_client_intent.response_sla_minutes
        })

    # Даты
    first_date = messages[0].get("timestamp", "") if messages else ""
    last_date = messages[-1].get("timestamp", "") if messages else ""

    # Ограничиваем списки сообщений
    for intent in messages_by_intent:
        messages_by_intent[intent] = messages_by_intent[intent][:20]

    return ChatIntentAnalysis(
        chat_id=chat_id,
        contact_name=contact_name,
        total_messages=len(messages),
        intents_summary=dict(intents_summary),
        messages_by_intent=dict(messages_by_intent),
        unresponded_intents=unresponded_intents,
        first_message_date=first_date,
        last_message_date=last_date
    )


# ═══════════════════════════════════════════════════════════════
# АГРЕГИРОВАННАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

def calculate_aggregate_statistics(analyses: List[ChatIntentAnalysis]) -> Dict[str, Any]:
    """Вычисляет агрегированную статистику интентов"""
    if not analyses:
        return {}

    total_chats = len(analyses)
    total_messages = sum(a.total_messages for a in analyses)

    # Агрегация интентов
    all_intents = defaultdict(int)
    for a in analyses:
        for intent, count in a.intents_summary.items():
            all_intents[intent] += count

    # Неотвеченные интенты
    total_unresponded = sum(len(a.unresponded_intents) for a in analyses)
    unresponded_by_intent = defaultdict(int)
    for a in analyses:
        for ui in a.unresponded_intents:
            unresponded_by_intent[ui["intent"]] += 1

    # Процент сообщений по интентам
    intent_percentages = {}
    for intent, count in all_intents.items():
        intent_percentages[intent] = round(count / total_messages * 100, 2) if total_messages > 0 else 0

    # Топ интентов
    top_intents = sorted(all_intents.items(), key=lambda x: x[1], reverse=True)[:10]

    # Распределение приоритетов
    priority_distribution = defaultdict(int)
    for intent, count in all_intents.items():
        priority = INTENT_PATTERNS.get(intent, {}).get("priority", 5)
        priority_distribution[f"priority_{priority}"] += count

    return {
        "summary": {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "unique_intents_found": len(all_intents),
            "total_unresponded": total_unresponded,
            "unresponded_rate": round(total_unresponded / total_chats * 100, 2) if total_chats > 0 else 0
        },
        "intents_distribution": dict(sorted(all_intents.items(), key=lambda x: x[1], reverse=True)),
        "intent_percentages": intent_percentages,
        "top_intents": top_intents,
        "unresponded_by_intent": dict(unresponded_by_intent),
        "priority_distribution": dict(priority_distribution),
        "intent_descriptions": {
            intent: config["description"]
            for intent, config in INTENT_PATTERNS.items()
        },
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
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def classify_single_message(text: str) -> Dict[str, Any]:
    """
    Утилита для классификации одного сообщения.

    Полезно для тестирования и интерактивного использования.
    """
    detections = classify_intent(text)

    if not detections:
        return {
            "text": text,
            "primary_intent": "OTHER",
            "confidence": 0.0,
            "all_intents": []
        }

    return {
        "text": text,
        "primary_intent": detections[0].intent,
        "confidence": detections[0].confidence,
        "all_intents": [
            {
                "intent": d.intent,
                "confidence": d.confidence,
                "description": INTENT_PATTERNS.get(d.intent, {}).get("description", ""),
                "requires_response": d.requires_response,
                "sla_minutes": d.response_sla_minutes
            }
            for d in detections
        ]
    }


def get_intent_info(intent_name: str) -> Dict[str, Any]:
    """Возвращает информацию об интенте"""
    config = INTENT_PATTERNS.get(intent_name, {})

    return {
        "intent": intent_name,
        "description": config.get("description", "Неизвестный интент"),
        "priority": config.get("priority", 5),
        "requires_response": config.get("requires_response", True),
        "response_sla_minutes": config.get("response_sla_minutes"),
        "patterns_count": len(config.get("patterns", []))
    }


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Главная функция классификации интентов"""
    parser = argparse.ArgumentParser(description="Классификация интентов в WhatsApp сообщениях")
    parser.add_argument("--input", "-i", default=str(JSON_DIR / "all_messages.jsonl"),
                        help="Путь к JSONL файлу с сообщениями")
    parser.add_argument("--output", "-o", default=str(ANALYTICS_DIR / "intent_analysis.json"),
                        help="Путь для сохранения результатов")
    parser.add_argument("--detailed", "-d", action="store_true",
                        help="Включить детальный анализ каждого чата")
    parser.add_argument("--test", "-t", type=str,
                        help="Протестировать классификацию на одном сообщении")
    parser.add_argument("--limit", type=int, default=0,
                        help="Ограничить количество чатов для анализа")

    args = parser.parse_args()

    # Режим тестирования одного сообщения
    if args.test:
        result = classify_single_message(args.test)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Проверяем входной файл
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Файл не найден: {input_path}")
        print("Создаю демо-анализ...")

        # Демо-данные
        demo_analysis = ChatIntentAnalysis(
            chat_id="demo_1",
            contact_name="Демо клиент",
            total_messages=45,
            intents_summary={
                "PRICE_REQUEST": 5,
                "AVAILABILITY_REQUEST": 3,
                "BOOKING_CONFIRM": 2,
                "INFO_REQUEST": 8,
                "GREETING": 3,
                "GRATITUDE": 4,
                "OTHER": 20
            },
            messages_by_intent={
                "PRICE_REQUEST": [
                    {"message_index": 2, "timestamp": "2026-01-01T10:05:00", "text_preview": "Сколько стоит сафари?"}
                ],
                "BOOKING_CONFIRM": [
                    {"message_index": 25, "timestamp": "2026-01-02T14:30:00", "text_preview": "Бронирую на 4 человек"}
                ]
            },
            unresponded_intents=[],
            first_message_date="2026-01-01T10:00:00",
            last_message_date="2026-01-15T18:30:00"
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
        analysis = analyze_chat_intents(chat_messages, chat_id, contact_name)
        analyses.append(analysis)

    print(f"Проанализировано {len(analyses)} чатов")

    # Вычисляем агрегированную статистику
    aggregate = calculate_aggregate_statistics(analyses)

    # Формируем результат
    result = {
        "aggregate_statistics": aggregate,
        "chat_analyses": [asdict(a) for a in analyses] if args.detailed else [],
        "total_chats": len(analyses)
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
    print("КЛАССИФИКАЦИЯ ИНТЕНТОВ")
    print("=" * 50)

    summary = aggregate.get("summary", {})
    print(f"Всего чатов: {summary.get('total_chats', 0)}")
    print(f"Всего сообщений: {summary.get('total_messages', 0)}")
    print(f"Уникальных интентов: {summary.get('unique_intents_found', 0)}")
    print(f"Неотвеченных интентов: {summary.get('total_unresponded', 0)}")

    print("\nТоп-10 интентов:")
    for intent, count in aggregate.get("top_intents", []):
        desc = INTENT_PATTERNS.get(intent, {}).get("description", "")
        pct = aggregate.get("intent_percentages", {}).get(intent, 0)
        print(f"  {intent}: {count} ({pct}%) - {desc}")

    print("\nНеотвеченные интенты по типам:")
    for intent, count in aggregate.get("unresponded_by_intent", {}).items():
        print(f"  {intent}: {count}")


if __name__ == "__main__":
    main()
