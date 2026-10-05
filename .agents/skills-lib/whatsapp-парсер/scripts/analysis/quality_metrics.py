#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Метрики качества обслуживания из WhatsApp чатов.

Метрики:
- FRT (First Response Time) - время первого ответа
- ART (Average Response Time) - среднее время ответа
- SLA нарушения - превышение пороговых значений
- Индикаторы проблем - жалобы, эскалации
- Индекс удовлетворённости - соотношение позитивных/негативных сигналов
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
from typing import List, Dict, Optional, Tuple, Any

# Добавляем путь к utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import ANALYTICS_DIR, JSON_DIR, ensure_directories

sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# SLA КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

SLA_CONFIG = {
    "first_response_minutes": 15,       # FRT < 15 минут
    "regular_response_minutes": 60,     # Обычный ответ < 1 час
    "working_hours_start": 9,           # Рабочие часы 9:00
    "working_hours_end": 21,            # до 21:00
    "working_days": [0, 1, 2, 3, 4, 5, 6],  # Все дни (0=понедельник)
}

BENCHMARKS = {
    "excellent": {
        "first_response_minutes": 5,
        "avg_response_minutes": 15,
        "sla_compliance_percent": 95
    },
    "good": {
        "first_response_minutes": 15,
        "avg_response_minutes": 30,
        "sla_compliance_percent": 85
    },
    "acceptable": {
        "first_response_minutes": 60,
        "avg_response_minutes": 120,
        "sla_compliance_percent": 70
    },
    "poor": {
        "first_response_minutes": 180,
        "avg_response_minutes": 240,
        "sla_compliance_percent": 50
    }
}


# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ОПРЕДЕЛЕНИЯ ПРОБЛЕМ
# ═══════════════════════════════════════════════════════════════

COMPLAINT_MARKERS = {
    "strong": [
        r"(?i)ужасн[оы]й?",
        r"(?i)кошмар",
        r"(?i)скандал",
        r"(?i)обман",
        r"(?i)мошенни",
        r"(?i)верн[иу]те\s+деньги",
        r"(?i)жалоб[ау]",
        r"(?i)суд",
        r"(?i)юрист",
    ],
    "medium": [
        r"(?i)проблем[аы]",
        r"(?i)плохо",
        r"(?i)недовол[ье]н",
        r"(?i)не\s+устраивает",
        r"(?i)разочарован",
        r"(?i)ошибк[аи]",
        r"(?i)не\s+работает",
        r"(?i)сломан",
        r"(?i)испорчен",
    ],
    "weak": [
        r"(?i)не\s+понял",
        r"(?i)не\s+ясно",
        r"(?i)запутал",
        r"(?i)долго\s+ждать",
        r"(?i)где\s+мой",
        r"(?i)почему\s+так\s+долго",
        r"(?i)когда\s+уже",
    ]
}

ESCALATION_MARKERS = [
    r"(?i)руководител",
    r"(?i)директор",
    r"(?i)начальни[кц]",
    r"(?i)главн",
    r"(?i)старши[йм]",
    r"(?i)ответственн",
    r"(?i)кто\s+главный",
    r"(?i)позови[те]?\s+\w+",
    r"(?i)хочу\s+говорить\s+с",
    r"(?i)передай[те]?",
]

POSITIVE_MARKERS = {
    "gratitude": [
        r"(?i)спасибо",
        r"(?i)благодар",
        r"(?i)thank",
        r"(?i)признателен",
    ],
    "satisfaction": [
        r"(?i)отлично",
        r"(?i)замечательно",
        r"(?i)прекрасно",
        r"(?i)супер",
        r"(?i)класс",
        r"(?i)великолепно",
        r"(?i)идеально",
        r"(?i)perfect",
        r"(?i)excellent",
    ],
    "recommendation": [
        r"(?i)рекомендую",
        r"(?i)посоветую",
        r"(?i)расскажу\s+друзьям",
        r"(?i)порекоменд",
    ],
    "loyalty": [
        r"(?i)обращусь\s+ещё",
        r"(?i)вернусь",
        r"(?i)буду\s+работать\s+с\s+вами",
        r"(?i)постоянн\w*\s+клиент",
    ]
}


# ═══════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class ResponseTimeMetrics:
    """Метрики времени ответа"""
    first_response_minutes: Optional[float]
    avg_response_minutes: float
    min_response_minutes: float
    max_response_minutes: float
    median_response_minutes: float
    responses_count: int


@dataclass
class SLAMetrics:
    """Метрики SLA"""
    total_responses: int
    sla_violations_count: int
    sla_compliance_percent: float
    frt_violations: int
    regular_violations: int
    violations_list: List[Dict]


@dataclass
class ProblemIndicators:
    """Индикаторы проблем"""
    complaint_score: int
    complaints_by_severity: Dict[str, int]
    escalations_count: int
    escalations: List[Dict]
    repeated_questions_count: int
    risk_level: str


@dataclass
class SatisfactionMetrics:
    """Метрики удовлетворённости"""
    satisfaction_score: int
    positive_markers_count: int
    negative_markers_count: int
    gratitude_count: int
    praise_count: int
    recommendation_mentions: int
    loyalty_indicators: int
    nps_category: str


@dataclass
class ChatQualityAnalysis:
    """Полный анализ качества для одного чата"""
    chat_id: str
    contact_name: str
    response_time: Dict
    sla: Dict
    problems: Dict
    satisfaction: Dict
    overall_quality_score: int
    quality_grade: str
    first_message_date: str
    last_message_date: str
    total_messages: int


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ АНАЛИЗА ВРЕМЕНИ ОТВЕТА
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


def is_working_hours(dt: datetime) -> bool:
    """Проверяет, находится ли время в рабочих часах"""
    if dt.weekday() not in SLA_CONFIG["working_days"]:
        return False
    if dt.hour < SLA_CONFIG["working_hours_start"] or dt.hour >= SLA_CONFIG["working_hours_end"]:
        return False
    return True


def calculate_response_times(messages: List[Dict]) -> ResponseTimeMetrics:
    """
    Вычисляет метрики времени ответа.

    Args:
        messages: Список сообщений с sender_type и timestamp
    """
    response_times = []
    first_response_time = None
    last_client_msg_time = None

    for i, msg in enumerate(messages):
        sender_type = msg.get("sender_type", "")
        timestamp = parse_timestamp(msg.get("timestamp", ""))

        if not timestamp:
            continue

        if sender_type == "client":
            last_client_msg_time = timestamp
        elif sender_type == "manager" and last_client_msg_time:
            # Вычисляем время ответа
            delta_minutes = (timestamp - last_client_msg_time).total_seconds() / 60

            if delta_minutes >= 0:  # Игнорируем отрицательные значения
                response_times.append(delta_minutes)

                # Первый ответ
                if first_response_time is None:
                    first_response_time = delta_minutes

            last_client_msg_time = None

    if not response_times:
        return ResponseTimeMetrics(
            first_response_minutes=None,
            avg_response_minutes=0,
            min_response_minutes=0,
            max_response_minutes=0,
            median_response_minutes=0,
            responses_count=0
        )

    # Сортируем для медианы
    sorted_times = sorted(response_times)
    median = sorted_times[len(sorted_times) // 2]

    return ResponseTimeMetrics(
        first_response_minutes=round(first_response_time, 2) if first_response_time else None,
        avg_response_minutes=round(sum(response_times) / len(response_times), 2),
        min_response_minutes=round(min(response_times), 2),
        max_response_minutes=round(max(response_times), 2),
        median_response_minutes=round(median, 2),
        responses_count=len(response_times)
    )


def check_sla_violations(messages: List[Dict]) -> SLAMetrics:
    """
    Проверяет нарушения SLA.

    Args:
        messages: Список сообщений
    """
    violations = []
    frt_violations = 0
    regular_violations = 0
    total_responses = 0
    is_first_response = True
    last_client_msg = None

    for i, msg in enumerate(messages):
        sender_type = msg.get("sender_type", "")
        timestamp = parse_timestamp(msg.get("timestamp", ""))

        if not timestamp:
            continue

        if sender_type == "client":
            last_client_msg = msg
        elif sender_type == "manager" and last_client_msg:
            total_responses += 1
            client_time = parse_timestamp(last_client_msg.get("timestamp", ""))

            if client_time:
                response_minutes = (timestamp - client_time).total_seconds() / 60

                # Определяем порог в зависимости от того, первый это ответ или нет
                if is_first_response:
                    threshold = SLA_CONFIG["first_response_minutes"]
                    is_first_response = False
                else:
                    threshold = SLA_CONFIG["regular_response_minutes"]

                # Проверяем нарушение (только в рабочие часы)
                if is_working_hours(client_time) and response_minutes > threshold:
                    violation = {
                        "type": "first_response" if threshold == SLA_CONFIG["first_response_minutes"] else "regular",
                        "expected_minutes": threshold,
                        "actual_minutes": round(response_minutes, 2),
                        "timestamp": msg.get("timestamp", ""),
                        "client_message_time": last_client_msg.get("timestamp", "")
                    }
                    violations.append(violation)

                    if threshold == SLA_CONFIG["first_response_minutes"]:
                        frt_violations += 1
                    else:
                        regular_violations += 1

            last_client_msg = None

    compliance = ((total_responses - len(violations)) / total_responses * 100) if total_responses > 0 else 100

    return SLAMetrics(
        total_responses=total_responses,
        sla_violations_count=len(violations),
        sla_compliance_percent=round(compliance, 2),
        frt_violations=frt_violations,
        regular_violations=regular_violations,
        violations_list=violations[:10]  # Ограничиваем список
    )


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ АНАЛИЗА ПРОБЛЕМ
# ═══════════════════════════════════════════════════════════════

def detect_complaints(messages: List[Dict]) -> Tuple[int, Dict[str, int], List[Dict]]:
    """
    Определяет жалобы в сообщениях.

    Returns:
        Tuple[complaint_score, counts_by_severity, complaints_list]
    """
    weights = {"strong": 10, "medium": 5, "weak": 2}
    complaints = []
    counts = {"strong": 0, "medium": 0, "weak": 0}

    for msg in messages:
        if msg.get("sender_type") != "client":
            continue

        text = msg.get("text", "")

        for severity, patterns in COMPLAINT_MARKERS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    counts[severity] += 1
                    complaints.append({
                        "severity": severity,
                        "pattern": pattern[:30],
                        "message_preview": text[:100],
                        "timestamp": msg.get("timestamp", "")
                    })
                    break  # Одна жалоба на сообщение

    score = sum(weights[s] * c for s, c in counts.items())
    score = min(score, 100)  # Ограничиваем 100

    return score, counts, complaints[:10]


def detect_escalations(messages: List[Dict]) -> Tuple[int, List[Dict]]:
    """
    Определяет эскалации.

    Returns:
        Tuple[count, escalations_list]
    """
    escalations = []

    for msg in messages:
        if msg.get("sender_type") != "client":
            continue

        text = msg.get("text", "")

        for pattern in ESCALATION_MARKERS:
            if re.search(pattern, text):
                escalations.append({
                    "timestamp": msg.get("timestamp", ""),
                    "message_preview": text[:150]
                })
                break

    return len(escalations), escalations[:5]


def detect_repeated_questions(messages: List[Dict], threshold_hours: int = 24) -> int:
    """
    Определяет повторные вопросы по одной теме.
    """
    TOPIC_PATTERNS = {
        "price": r"(?i)(сколько|цена|стоимость|прайс)",
        "availability": r"(?i)(есть|свобод|доступн)",
        "payment": r"(?i)(оплат|перевод|деньги|реквизит)",
        "booking": r"(?i)(бронь|бронирован|забронировать)",
        "status": r"(?i)(статус|где|когда|как дела)",
    }

    topic_last_asked = {}
    repeated_count = 0

    for msg in messages:
        if msg.get("sender_type") != "client":
            continue

        text = msg.get("text", "")
        timestamp = parse_timestamp(msg.get("timestamp", ""))

        if not timestamp:
            continue

        for topic, pattern in TOPIC_PATTERNS.items():
            if re.search(pattern, text):
                if topic in topic_last_asked:
                    hours_since = (timestamp - topic_last_asked[topic]).total_seconds() / 3600
                    if 0 < hours_since < threshold_hours:
                        repeated_count += 1
                topic_last_asked[topic] = timestamp

    return repeated_count


def analyze_problems(messages: List[Dict]) -> ProblemIndicators:
    """Полный анализ проблем в чате"""
    complaint_score, complaints_by_severity, _ = detect_complaints(messages)
    escalations_count, escalations = detect_escalations(messages)
    repeated_questions = detect_repeated_questions(messages)

    # Определяем уровень риска
    total_problems = complaint_score + escalations_count * 15 + repeated_questions * 3

    if total_problems >= 50:
        risk_level = "critical"
    elif total_problems >= 30:
        risk_level = "high"
    elif total_problems >= 15:
        risk_level = "medium"
    else:
        risk_level = "low"

    return ProblemIndicators(
        complaint_score=complaint_score,
        complaints_by_severity=complaints_by_severity,
        escalations_count=escalations_count,
        escalations=escalations,
        repeated_questions_count=repeated_questions,
        risk_level=risk_level
    )


# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ АНАЛИЗА УДОВЛЕТВОРЁННОСТИ
# ═══════════════════════════════════════════════════════════════

def analyze_satisfaction(messages: List[Dict]) -> SatisfactionMetrics:
    """Анализ удовлетворённости клиента"""
    positive_count = 0
    negative_count = 0
    gratitude_count = 0
    praise_count = 0
    recommendation_count = 0
    loyalty_count = 0

    # Собираем все паттерны
    all_positive = []
    for category, patterns in POSITIVE_MARKERS.items():
        all_positive.extend(patterns)

    all_negative = []
    for severity, patterns in COMPLAINT_MARKERS.items():
        all_negative.extend(patterns)

    for msg in messages:
        if msg.get("sender_type") != "client":
            continue

        text = msg.get("text", "")

        # Позитивные
        for pattern in all_positive:
            if re.search(pattern, text):
                positive_count += 1

        # Негативные
        for pattern in all_negative:
            if re.search(pattern, text):
                negative_count += 1

        # Детальные категории
        for pattern in POSITIVE_MARKERS.get("gratitude", []):
            if re.search(pattern, text):
                gratitude_count += 1

        for pattern in POSITIVE_MARKERS.get("satisfaction", []):
            if re.search(pattern, text):
                praise_count += 1

        for pattern in POSITIVE_MARKERS.get("recommendation", []):
            if re.search(pattern, text):
                recommendation_count += 1

        for pattern in POSITIVE_MARKERS.get("loyalty", []):
            if re.search(pattern, text):
                loyalty_count += 1

    # Вычисляем индекс удовлетворённости
    total = positive_count + negative_count
    if total == 0:
        satisfaction_score = 50  # Нейтрально
    else:
        satisfaction_score = int((positive_count / total) * 100)

    # Определяем NPS категорию
    if satisfaction_score >= 80:
        nps_category = "promoter"
    elif satisfaction_score >= 50:
        nps_category = "passive"
    else:
        nps_category = "detractor"

    return SatisfactionMetrics(
        satisfaction_score=satisfaction_score,
        positive_markers_count=positive_count,
        negative_markers_count=negative_count,
        gratitude_count=gratitude_count,
        praise_count=praise_count,
        recommendation_mentions=recommendation_count,
        loyalty_indicators=loyalty_count,
        nps_category=nps_category
    )


# ═══════════════════════════════════════════════════════════════
# ОБЩИЙ ИНДЕКС КАЧЕСТВА
# ═══════════════════════════════════════════════════════════════

def calculate_quality_score(
    response_metrics: ResponseTimeMetrics,
    sla_metrics: SLAMetrics,
    problem_indicators: ProblemIndicators,
    satisfaction_metrics: SatisfactionMetrics
) -> Tuple[int, str]:
    """
    Вычисляет общий индекс качества обслуживания.

    Формула:
    Quality_Score = (
        Response_Score * 0.25 +
        SLA_Score * 0.20 +
        Problem_Score * 0.25 +
        Satisfaction_Score * 0.30
    )

    Returns:
        Tuple[score, grade]
    """
    # Response Score (100 - normalized response time penalty)
    if response_metrics.avg_response_minutes > 0:
        response_score = max(0, 100 - (response_metrics.avg_response_minutes / 60 * 30))
    else:
        response_score = 100

    # SLA Score
    sla_score = sla_metrics.sla_compliance_percent

    # Problem Score (100 - complaint_score)
    problem_score = max(0, 100 - problem_indicators.complaint_score)

    # Satisfaction Score
    satisfaction_score = satisfaction_metrics.satisfaction_score

    # Общий индекс
    quality_score = int(
        response_score * 0.25 +
        sla_score * 0.20 +
        problem_score * 0.25 +
        satisfaction_score * 0.30
    )

    # Определяем грейд
    if quality_score >= 90:
        grade = "A+"
    elif quality_score >= 85:
        grade = "A"
    elif quality_score >= 80:
        grade = "A-"
    elif quality_score >= 75:
        grade = "B+"
    elif quality_score >= 70:
        grade = "B"
    elif quality_score >= 65:
        grade = "B-"
    elif quality_score >= 60:
        grade = "C"
    else:
        grade = "D"

    return quality_score, grade


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ЧАТА
# ═══════════════════════════════════════════════════════════════

def analyze_chat_quality(messages: List[Dict], chat_id: str = "", contact_name: str = "") -> ChatQualityAnalysis:
    """
    Полный анализ качества обслуживания для одного чата.
    """
    # Время ответа
    response_metrics = calculate_response_times(messages)

    # SLA
    sla_metrics = check_sla_violations(messages)

    # Проблемы
    problem_indicators = analyze_problems(messages)

    # Удовлетворённость
    satisfaction_metrics = analyze_satisfaction(messages)

    # Общий индекс
    quality_score, grade = calculate_quality_score(
        response_metrics, sla_metrics, problem_indicators, satisfaction_metrics
    )

    # Даты
    first_date = messages[0].get("timestamp", "") if messages else ""
    last_date = messages[-1].get("timestamp", "") if messages else ""

    return ChatQualityAnalysis(
        chat_id=chat_id,
        contact_name=contact_name,
        response_time=asdict(response_metrics),
        sla=asdict(sla_metrics),
        problems=asdict(problem_indicators),
        satisfaction=asdict(satisfaction_metrics),
        overall_quality_score=quality_score,
        quality_grade=grade,
        first_message_date=first_date,
        last_message_date=last_date,
        total_messages=len(messages)
    )


# ═══════════════════════════════════════════════════════════════
# АГРЕГИРОВАННАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

def calculate_aggregate_metrics(analyses: List[ChatQualityAnalysis]) -> Dict[str, Any]:
    """Вычисляет агрегированные метрики качества"""
    if not analyses:
        return {}

    total = len(analyses)

    # Время ответа
    frt_values = [a.response_time.get("first_response_minutes") for a in analyses
                  if a.response_time.get("first_response_minutes") is not None]
    art_values = [a.response_time.get("avg_response_minutes") for a in analyses
                  if a.response_time.get("avg_response_minutes", 0) > 0]

    avg_frt = sum(frt_values) / len(frt_values) if frt_values else 0
    avg_art = sum(art_values) / len(art_values) if art_values else 0

    # SLA
    total_responses = sum(a.sla.get("total_responses", 0) for a in analyses)
    total_violations = sum(a.sla.get("sla_violations_count", 0) for a in analyses)
    overall_compliance = ((total_responses - total_violations) / total_responses * 100) if total_responses > 0 else 100

    # Проблемы
    risk_counts = defaultdict(int)
    for a in analyses:
        risk_counts[a.problems.get("risk_level", "unknown")] += 1

    # Качество
    avg_quality = sum(a.overall_quality_score for a in analyses) / total
    grade_counts = defaultdict(int)
    for a in analyses:
        grade_counts[a.quality_grade] += 1

    # NPS
    nps_counts = defaultdict(int)
    for a in analyses:
        nps_counts[a.satisfaction.get("nps_category", "unknown")] += 1

    promoters = nps_counts.get("promoter", 0)
    detractors = nps_counts.get("detractor", 0)
    nps_score = ((promoters - detractors) / total * 100) if total > 0 else 0

    return {
        "summary": {
            "total_chats_analyzed": total,
            "avg_quality_score": round(avg_quality, 1),
            "avg_first_response_minutes": round(avg_frt, 2),
            "avg_response_minutes": round(avg_art, 2),
            "overall_sla_compliance": round(overall_compliance, 2),
            "nps_score": round(nps_score, 1)
        },
        "response_time": {
            "avg_first_response_minutes": round(avg_frt, 2),
            "avg_response_minutes": round(avg_art, 2),
            "within_15min_percent": round(sum(1 for v in frt_values if v <= 15) / len(frt_values) * 100 if frt_values else 0, 1),
            "within_1hour_percent": round(sum(1 for v in art_values if v <= 60) / len(art_values) * 100 if art_values else 0, 1)
        },
        "sla": {
            "total_responses": total_responses,
            "total_violations": total_violations,
            "compliance_percent": round(overall_compliance, 2)
        },
        "risk_distribution": dict(risk_counts),
        "grade_distribution": dict(grade_counts),
        "nps_distribution": dict(nps_counts),
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
    """Главная функция анализа качества"""
    parser = argparse.ArgumentParser(description="Анализ качества обслуживания из WhatsApp чатов")
    parser.add_argument("--input", "-i", default=str(JSON_DIR / "all_messages.jsonl"),
                        help="Путь к JSONL файлу с сообщениями")
    parser.add_argument("--output", "-o", default=str(ANALYTICS_DIR / "quality_metrics.json"),
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

        # Демо-данные
        demo_analysis = ChatQualityAnalysis(
            chat_id="demo_1",
            contact_name="Демо клиент",
            response_time={
                "first_response_minutes": 8.5,
                "avg_response_minutes": 25.3,
                "min_response_minutes": 2.0,
                "max_response_minutes": 120.0,
                "median_response_minutes": 15.0,
                "responses_count": 15
            },
            sla={
                "total_responses": 15,
                "sla_violations_count": 2,
                "sla_compliance_percent": 86.67,
                "frt_violations": 0,
                "regular_violations": 2,
                "violations_list": []
            },
            problems={
                "complaint_score": 5,
                "complaints_by_severity": {"strong": 0, "medium": 1, "weak": 0},
                "escalations_count": 0,
                "escalations": [],
                "repeated_questions_count": 1,
                "risk_level": "low"
            },
            satisfaction={
                "satisfaction_score": 78,
                "positive_markers_count": 7,
                "negative_markers_count": 2,
                "gratitude_count": 3,
                "praise_count": 2,
                "recommendation_mentions": 1,
                "loyalty_indicators": 1,
                "nps_category": "passive"
            },
            overall_quality_score=82,
            quality_grade="A-",
            first_message_date="2026-01-01T10:00:00",
            last_message_date="2026-01-15T18:30:00",
            total_messages=45
        )

        result = {
            "aggregate_metrics": calculate_aggregate_metrics([demo_analysis]),
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
        analysis = analyze_chat_quality(chat_messages, chat_id, contact_name)
        analyses.append(analysis)

    print(f"Проанализировано {len(analyses)} чатов")

    # Вычисляем агрегированные метрики
    aggregate = calculate_aggregate_metrics(analyses)

    # Формируем результат
    result = {
        "aggregate_metrics": aggregate,
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
    print("МЕТРИКИ КАЧЕСТВА ОБСЛУЖИВАНИЯ")
    print("=" * 50)

    summary = aggregate.get("summary", {})
    print(f"Всего чатов: {summary.get('total_chats_analyzed', 0)}")
    print(f"Средний индекс качества: {summary.get('avg_quality_score', 0)}")
    print(f"Среднее время первого ответа: {summary.get('avg_first_response_minutes', 0)} мин")
    print(f"Среднее время ответа: {summary.get('avg_response_minutes', 0)} мин")
    print(f"SLA соответствие: {summary.get('overall_sla_compliance', 0)}%")
    print(f"NPS Score: {summary.get('nps_score', 0)}")

    print("\nРаспределение по рискам:")
    for risk, count in aggregate.get("risk_distribution", {}).items():
        print(f"  {risk}: {count}")

    print("\nРаспределение по грейдам:")
    for grade, count in aggregate.get("grade_distribution", {}).items():
        print(f"  {grade}: {count}")


if __name__ == "__main__":
    main()
