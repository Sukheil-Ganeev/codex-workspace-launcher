#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ воронки продаж из WhatsApp чатов.

Этапы воронки:
- ЗАПРОС (REQUEST) - первое обращение клиента
- ИНТЕРЕС (INTEREST) - уточнение деталей
- ПРЕДЛОЖЕНИЕ (PROPOSAL) - отправлено коммерческое предложение
- БРОНЬ (BOOKING) - подтверждение намерения
- ОПЛАТА (PAYMENT) - деньги получены
- ВЫПОЛНЕНО (COMPLETED) - услуга оказана

Причины выхода:
- price_too_high - дорого
- dates_unavailable - даты не подходят
- competitor_chosen - выбрали конкурента
- trip_cancelled - отменили поездку
- no_response - нет ответа (ghosted)
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any

# Добавляем путь к utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import ANALYTICS_DIR, JSON_DIR, ensure_directories

sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# ЭТАПЫ ВОРОНКИ
# ═══════════════════════════════════════════════════════════════

class FunnelStage(Enum):
    """Этапы воронки продаж"""
    REQUEST = 1       # Запрос
    INTEREST = 2      # Интерес
    PROPOSAL = 3      # Предложение
    BOOKING = 4       # Бронь
    PAYMENT = 5       # Оплата
    COMPLETED = 6     # Выполнено
    LOST = -1         # Потерян (отказ)
    GHOSTED = -2      # Пропал (нет ответа)


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ОПРЕДЕЛЕНИЯ ЭТАПОВ
# ═══════════════════════════════════════════════════════════════

STAGE_PATTERNS = {
    "REQUEST": {
        "patterns": [
            r"(?i)(хотел|хочу|хотим|интересует|нужен|нужна|ищу|подскажите)",
            r"(?i)(сколько стоит|какая цена|прайс|тариф)",
            r"(?i)(есть ли|можно ли|доступн)",
            r"(?i)(добрый день|здравствуйте|привет).*\?",
            r"(?i)(на какие даты|когда можно|свободн)",
        ],
        "weight": 1.0
    },

    "INTEREST": {
        "patterns": [
            r"(?i)(а если|а можно|а как насчет|а что если)",
            r"(?i)(подробнее|детальнее|расскажите больше)",
            r"(?i)(какие варианты|что предложите|альтернатив)",
            r"(?i)(входит ли|включено ли|есть ли в комплекте)",
            r"(?i)(на \d+ (человек|персон|взрослых|детей))",
            r"(?i)(групп\w+ скидк|оптов\w+ цен)",
        ],
        "weight": 1.2
    },

    "PROPOSAL": {
        "patterns": [
            r"(?i)(предлагаю|предлагаем|могу предложить)",
            r"(?i)(стоимость составит|цена будет|итого)",
            r"(?i)(вот варианты|на выбор|опции)",
            r"(?i)(\d+\s*(AED|USD|EUR|руб|дирхам))",
            r"(?i)(включает в себя|в стоимость входит)",
            r"(?i)(отправляю (счет|инвойс|предложение))",
        ],
        "weight": 1.5
    },

    "BOOKING": {
        "patterns": [
            r"(?i)(бронирую|забронируйте|резервирую|подтверждаю)",
            r"(?i)(давайте|договорились|согласен|согласна|берем|беру)",
            r"(?i)(оформляйте|оформите|оформляем)",
            r"(?i)(фиксируем|закрепляем|держите)",
            r"(?i)(подтверждение брони|бронь подтверждена)",
            r"(?i)(номер брони|код бронирования)",
        ],
        "weight": 2.0
    },

    "PAYMENT": {
        "patterns": [
            r"(?i)(оплатил|оплачено|перевел|перевела|отправил деньги)",
            r"(?i)(чек|квитанция|подтверждение оплаты)",
            r"(?i)(деньги поступили|платеж получен|оплата прошла)",
            r"(?i)(скрин (оплаты|перевода|платежа))",
            r"(?i)(transaction|payment confirmed)",
            r"(?i)(реквизиты для оплаты|куда переводить)",
        ],
        "weight": 2.5
    },

    "COMPLETED": {
        "patterns": [
            r"(?i)(спасибо за|благодарю|было здорово|понравилось)",
            r"(?i)(все прошло|все было|отлично провели)",
            r"(?i)(рекомендую|посоветую|обратимся еще)",
            r"(?i)(оставлю отзыв|напишу отзыв)",
            r"(?i)(услуга оказана|заказ выполнен|тур завершен)",
            r"(?i)(до свидания|до встречи|всего доброго).*(!|спасибо)",
        ],
        "weight": 3.0
    }
}

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ВЫХОДА ИЗ ВОРОНКИ (ПРИЧИНЫ ОТКАЗА)
# ═══════════════════════════════════════════════════════════════

EXIT_PATTERNS = {
    "price_too_high": {
        "patterns": [
            r"(?i)(дорого|дороговато|не потянем|выше бюджета)",
            r"(?i)(нашли дешевле|есть дешевле|у других дешевле)",
            r"(?i)(цена не устраивает|не укладываемся в бюджет)",
        ],
        "weight": 2.0
    },

    "dates_unavailable": {
        "patterns": [
            r"(?i)(на эти даты.*нет|не подходят даты|заняты)",
            r"(?i)(планы изменились|перенесли|сдвинулись даты)",
            r"(?i)(в эти даты не можем|не успеваем)",
        ],
        "weight": 1.5
    },

    "competitor_chosen": {
        "patterns": [
            r"(?i)(уже забронировали|выбрали друг|нашли друг)",
            r"(?i)(у других|в другом месте|альтернатив)",
            r"(?i)(забронировали в другом|другая компания)",
        ],
        "weight": 2.0
    },

    "trip_cancelled": {
        "patterns": [
            r"(?i)(отмен\w+ (поездк|тур|путешеств))",
            r"(?i)(не едем|не летим|не поедем)",
            r"(?i)(визу.*отказ|не дали визу)",
        ],
        "weight": 1.8
    },

    "general_rejection": {
        "patterns": [
            r"(?i)(передумал|передумали|отказываюсь)",
            r"(?i)(не надо|не нужно|отменяем)",
            r"(?i)(не актуально|не в этот раз)",
            r"(?i)(спасибо,?\s*(не надо|не нужно|откажусь))",
        ],
        "weight": 1.5
    }
}


# ═══════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class StageDetection:
    """Результат определения этапа"""
    stage: str
    confidence: float
    matched_patterns: List[str]
    timestamp: str
    message_index: int
    message_preview: str


@dataclass
class ExitDetection:
    """Результат определения причины выхода"""
    reason: str
    confidence: float
    matched_patterns: List[str]
    timestamp: str
    message_preview: str


@dataclass
class ChatFunnelAnalysis:
    """Результат анализа воронки для одного чата"""
    chat_id: str
    contact_name: str
    current_stage: str
    max_stage_reached: str
    stage_history: List[Dict]
    exit_reason: Optional[str]
    exit_details: Optional[Dict]
    first_message_date: str
    last_message_date: str
    days_in_funnel: int
    total_messages: int
    conversion_probability: float


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ ЭТАПОВ
# ═══════════════════════════════════════════════════════════════

def detect_stage(message_text: str) -> Tuple[Optional[str], float, List[str]]:
    """
    Определяет этап воронки по тексту сообщения.

    Returns:
        Tuple[stage_name, confidence, matched_patterns]
    """
    best_stage = None
    best_score = 0.0
    matched = []

    for stage_name, stage_config in STAGE_PATTERNS.items():
        stage_score = 0.0
        stage_matches = []

        for pattern in stage_config["patterns"]:
            if re.search(pattern, message_text):
                stage_score += stage_config["weight"]
                stage_matches.append(pattern[:50])  # Обрезаем для читаемости

        if stage_score > best_score:
            best_score = stage_score
            best_stage = stage_name
            matched = stage_matches

    confidence = min(best_score / 5.0, 1.0)  # Нормализация
    return best_stage, confidence, matched


def detect_exit_reason(message_text: str) -> Tuple[Optional[str], float, List[str]]:
    """
    Определяет причину выхода из воронки.

    Returns:
        Tuple[reason, confidence, matched_patterns]
    """
    best_reason = None
    best_score = 0.0
    matched = []

    for reason, config in EXIT_PATTERNS.items():
        reason_score = 0.0
        reason_matches = []

        for pattern in config["patterns"]:
            if re.search(pattern, message_text):
                reason_score += config["weight"]
                reason_matches.append(pattern[:50])

        if reason_score > best_score:
            best_score = reason_score
            best_reason = reason
            matched = reason_matches

    confidence = min(best_score / 3.0, 1.0)
    return best_reason, confidence, matched


def get_stage_value(stage_name: str) -> int:
    """Возвращает числовое значение этапа для сравнения"""
    stage_values = {
        "REQUEST": 1,
        "INTEREST": 2,
        "PROPOSAL": 3,
        "BOOKING": 4,
        "PAYMENT": 5,
        "COMPLETED": 6,
        "LOST": -1,
        "GHOSTED": -2
    }
    return stage_values.get(stage_name, 0)


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ЧАТА
# ═══════════════════════════════════════════════════════════════

def analyze_chat_funnel(messages: List[Dict], chat_id: str = "", contact_name: str = "") -> ChatFunnelAnalysis:
    """
    Анализирует воронку для одного чата.

    Args:
        messages: Список сообщений [{timestamp, sender, text, sender_type}, ...]
        chat_id: ID чата
        contact_name: Имя контакта

    Returns:
        ChatFunnelAnalysis с результатами анализа
    """
    stage_history = []
    current_stage = "REQUEST"
    max_stage_value = 1
    exit_reason = None
    exit_details = None

    # Обрабатываем сообщения
    for i, msg in enumerate(messages):
        text = msg.get("text", "")
        timestamp = msg.get("timestamp", "")
        sender_type = msg.get("sender_type", "unknown")

        # Определяем этап
        stage, confidence, patterns = detect_stage(text)

        if stage and confidence > 0.3:
            stage_value = get_stage_value(stage)

            # Фиксируем продвижение по воронке
            if stage_value > max_stage_value:
                max_stage_value = stage_value
                current_stage = stage

                stage_history.append({
                    "stage": stage,
                    "confidence": round(confidence, 2),
                    "timestamp": timestamp,
                    "message_index": i,
                    "matched_patterns": patterns,
                    "message_preview": text[:100] if text else ""
                })

        # Проверяем выход из воронки (только от клиента)
        if sender_type == "client":
            reason, reason_conf, reason_patterns = detect_exit_reason(text)

            if reason and reason_conf > 0.4:
                exit_reason = reason
                exit_details = {
                    "confidence": round(reason_conf, 2),
                    "timestamp": timestamp,
                    "matched_patterns": reason_patterns,
                    "message_preview": text[:150] if text else ""
                }
                current_stage = "LOST"
                break

    # Проверяем ghosting (нет ответа > 7 дней)
    if messages and not exit_reason:
        last_msg = messages[-1]
        last_timestamp = last_msg.get("timestamp", "")
        last_sender_type = last_msg.get("sender_type", "")

        if last_sender_type == "manager" and last_timestamp:
            try:
                last_date = datetime.fromisoformat(last_timestamp.replace("Z", "+00:00"))
                days_since = (datetime.now(last_date.tzinfo) - last_date).days if last_date.tzinfo else (datetime.now() - last_date).days

                if days_since > 7 and current_stage not in ["COMPLETED", "PAYMENT"]:
                    exit_reason = "no_response"
                    exit_details = {
                        "days_inactive": days_since,
                        "last_manager_message": last_timestamp
                    }
                    current_stage = "GHOSTED"
            except (ValueError, TypeError):
                pass

    # Определяем даты
    first_date = messages[0].get("timestamp", "") if messages else ""
    last_date = messages[-1].get("timestamp", "") if messages else ""

    # Вычисляем дни в воронке
    days_in_funnel = 0
    if first_date and last_date:
        try:
            first_dt = datetime.fromisoformat(first_date.replace("Z", "+00:00"))
            last_dt = datetime.fromisoformat(last_date.replace("Z", "+00:00"))
            days_in_funnel = max(1, (last_dt - first_dt).days)
        except (ValueError, TypeError):
            pass

    # Вычисляем вероятность конверсии
    stage_probabilities = {
        "REQUEST": 0.12,
        "INTEREST": 0.22,
        "PROPOSAL": 0.45,
        "BOOKING": 0.82,
        "PAYMENT": 0.95,
        "COMPLETED": 1.0,
        "LOST": 0.0,
        "GHOSTED": 0.05
    }
    conversion_probability = stage_probabilities.get(current_stage, 0.0)

    # Получаем максимальный достигнутый этап
    max_stage_names = {1: "REQUEST", 2: "INTEREST", 3: "PROPOSAL", 4: "BOOKING", 5: "PAYMENT", 6: "COMPLETED"}
    max_stage_reached = max_stage_names.get(max_stage_value, "REQUEST")

    return ChatFunnelAnalysis(
        chat_id=chat_id,
        contact_name=contact_name,
        current_stage=current_stage,
        max_stage_reached=max_stage_reached,
        stage_history=stage_history,
        exit_reason=exit_reason,
        exit_details=exit_details,
        first_message_date=first_date,
        last_message_date=last_date,
        days_in_funnel=days_in_funnel,
        total_messages=len(messages),
        conversion_probability=conversion_probability
    )


# ═══════════════════════════════════════════════════════════════
# АГРЕГИРОВАННАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

def calculate_funnel_metrics(analyses: List[ChatFunnelAnalysis]) -> Dict[str, Any]:
    """
    Вычисляет агрегированные метрики воронки.

    Args:
        analyses: Список результатов анализа чатов

    Returns:
        Dict с метриками воронки
    """
    if not analyses:
        return {}

    # Подсчёт по этапам
    stage_counts = defaultdict(int)
    for a in analyses:
        stage_counts[a.max_stage_reached] += 1

    # Подсчёт причин выхода
    exit_reasons = defaultdict(int)
    for a in analyses:
        if a.exit_reason:
            exit_reasons[a.exit_reason] += 1

    total = len(analyses)

    # Конверсия по этапам
    stages_order = ["REQUEST", "INTEREST", "PROPOSAL", "BOOKING", "PAYMENT", "COMPLETED"]
    cumulative = 0
    stage_metrics = {}

    for stage in stages_order:
        count = sum(1 for a in analyses if get_stage_value(a.max_stage_reached) >= get_stage_value(stage))
        conversion_from_start = count / total if total > 0 else 0

        stage_metrics[stage] = {
            "count": count,
            "percent_of_total": round(conversion_from_start * 100, 1)
        }

    # Конверсия между этапами
    stage_transitions = {}
    for i in range(len(stages_order) - 1):
        from_stage = stages_order[i]
        to_stage = stages_order[i + 1]

        from_count = stage_metrics[from_stage]["count"]
        to_count = stage_metrics[to_stage]["count"]

        conversion = to_count / from_count if from_count > 0 else 0
        stage_transitions[f"{from_stage}_to_{to_stage}"] = round(conversion * 100, 1)

    # Общая конверсия
    completed_count = stage_metrics.get("COMPLETED", {}).get("count", 0)
    overall_conversion = completed_count / total if total > 0 else 0

    # Среднее время в воронке
    avg_days = sum(a.days_in_funnel for a in analyses) / total if total > 0 else 0

    # Потери по этапам
    lost_by_stage = defaultdict(int)
    for a in analyses:
        if a.current_stage in ["LOST", "GHOSTED"]:
            lost_by_stage[a.max_stage_reached] += 1

    return {
        "summary": {
            "total_chats_analyzed": total,
            "overall_conversion_rate": round(overall_conversion * 100, 2),
            "avg_days_in_funnel": round(avg_days, 1),
            "total_completed": completed_count,
            "total_lost": sum(1 for a in analyses if a.current_stage in ["LOST", "GHOSTED"])
        },
        "stages": stage_metrics,
        "stage_conversions": stage_transitions,
        "exit_reasons": dict(exit_reasons),
        "lost_by_stage": dict(lost_by_stage),
        "generated_at": datetime.now().isoformat()
    }


# ═══════════════════════════════════════════════════════════════
# ЧТЕНИЕ И ОБРАБОТКА ДАННЫХ
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


def determine_sender_type(msg: Dict, our_identifiers: List[str] = None) -> str:
    """
    Определяет тип отправителя (client/manager).

    Args:
        msg: Сообщение
        our_identifiers: Список наших идентификаторов
    """
    sender = msg.get("sender", "")

    # Если отправитель "Я" или из списка наших
    if sender == "Я" or sender.lower() in ["я", "me", "i"]:
        return "manager"

    if our_identifiers and sender in our_identifiers:
        return "manager"

    return "client"


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Главная функция анализа воронки"""
    parser = argparse.ArgumentParser(description="Анализ воронки продаж из WhatsApp чатов")
    parser.add_argument("--input", "-i", default=str(JSON_DIR / "all_messages.jsonl"),
                        help="Путь к JSONL файлу с сообщениями")
    parser.add_argument("--output", "-o", default=str(ANALYTICS_DIR / "funnel_analysis.json"),
                        help="Путь для сохранения результатов")
    parser.add_argument("--detailed", "-d", action="store_true",
                        help="Включить детальный анализ каждого чата")
    parser.add_argument("--limit", type=int, default=0,
                        help="Ограничить количество чатов для анализа")

    args = parser.parse_args()

    # Проверяем входной файл
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Файл не найден: {input_path}")
        print("Создаю демо-анализ...")

        # Создаём демо-данные для тестирования
        demo_analyses = [
            ChatFunnelAnalysis(
                chat_id="demo_1",
                contact_name="Демо клиент 1",
                current_stage="COMPLETED",
                max_stage_reached="COMPLETED",
                stage_history=[{"stage": "REQUEST", "timestamp": "2026-01-01"}],
                exit_reason=None,
                exit_details=None,
                first_message_date="2026-01-01",
                last_message_date="2026-01-15",
                days_in_funnel=14,
                total_messages=45,
                conversion_probability=1.0
            ),
            ChatFunnelAnalysis(
                chat_id="demo_2",
                contact_name="Демо клиент 2",
                current_stage="LOST",
                max_stage_reached="PROPOSAL",
                stage_history=[{"stage": "REQUEST", "timestamp": "2026-01-05"}],
                exit_reason="price_too_high",
                exit_details={"confidence": 0.85},
                first_message_date="2026-01-05",
                last_message_date="2026-01-08",
                days_in_funnel=3,
                total_messages=12,
                conversion_probability=0.0
            )
        ]

        metrics = calculate_funnel_metrics(demo_analyses)

        result = {
            "funnel_metrics": metrics,
            "chat_analyses": [asdict(a) for a in demo_analyses] if args.detailed else [],
            "demo_mode": True
        }

        # Сохраняем результат
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
        analysis = analyze_chat_funnel(chat_messages, chat_id, contact_name)
        analyses.append(analysis)

    print(f"Проанализировано {len(analyses)} чатов")

    # Вычисляем метрики
    metrics = calculate_funnel_metrics(analyses)

    # Формируем результат
    result = {
        "funnel_metrics": metrics,
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
    print("ВОРОНКА ПРОДАЖ")
    print("=" * 50)

    summary = metrics.get("summary", {})
    print(f"Всего чатов: {summary.get('total_chats_analyzed', 0)}")
    print(f"Общая конверсия: {summary.get('overall_conversion_rate', 0)}%")
    print(f"Завершённых: {summary.get('total_completed', 0)}")
    print(f"Потерянных: {summary.get('total_lost', 0)}")
    print(f"Среднее время в воронке: {summary.get('avg_days_in_funnel', 0)} дней")

    print("\nПо этапам:")
    for stage, data in metrics.get("stages", {}).items():
        print(f"  {stage}: {data.get('count', 0)} ({data.get('percent_of_total', 0)}%)")

    print("\nПричины отказов:")
    for reason, count in metrics.get("exit_reasons", {}).items():
        print(f"  {reason}: {count}")


if __name__ == "__main__":
    main()
