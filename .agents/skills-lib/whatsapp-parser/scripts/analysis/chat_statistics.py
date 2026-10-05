#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерация статистики для чата

Включает:
- Базовая статистика сообщений и медиа
- Метрики качества обслуживания (FRT, ART)
- Статистика по языкам
- Финансовые данные
"""

import sys
import os
import re
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ ДЛЯ МЕТРИК КАЧЕСТВА
# ═══════════════════════════════════════════════════════════════

# Рабочие часы для расчёта FRT/ART (UTC+4 Dubai)
BUSINESS_HOURS_START = 9   # 09:00
BUSINESS_HOURS_END = 21    # 21:00
BUSINESS_DAYS = [0, 1, 2, 3, 4, 5, 6]  # Пн-Вс (в ОАЭ работают все дни)

# Пороги SLA (в минутах)
SLA_FRT_EXCELLENT = 5      # Отличный FRT < 5 мин
SLA_FRT_GOOD = 15          # Хороший FRT < 15 мин
SLA_FRT_ACCEPTABLE = 60    # Приемлемый FRT < 60 мин
SLA_ART_EXCELLENT = 10     # Отличный ART < 10 мин
SLA_ART_GOOD = 30          # Хороший ART < 30 мин

def calculate_statistics(filepath):
    """Вычисляет статистику для файла чата"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    stats = {
        'total_messages': 0,
        'voice_messages': 0,
        'photos': 0,
        'pdfs': 0,
        'contacts_vcf': 0,
        'days_active': 0,
        'first_date': '',
        'last_date': '',
        'messages_by_sender': defaultdict(int),
        'messages_by_date': defaultdict(int),
        'avg_messages_per_day': 0,
        'most_active_day': '',
        'total_rub': 0,
        'total_aed': 0,
        'operations_count': 0,
    }

    # Подсчёт сообщений
    message_pattern = r'\*\*([👤👨👩][^*]+)\*\*\s*\[(\d{2}:\d{2}:\d{2})\]'
    messages = re.findall(message_pattern, content)
    stats['total_messages'] = len(messages)

    # Подсчёт по отправителям
    for sender, time in messages:
        sender_clean = sender.strip()
        stats['messages_by_sender'][sender_clean] += 1

    # Подсчёт медиа
    stats['voice_messages'] = len(re.findall(r'🎤 \*\*Голосовое', content))
    stats['photos'] = len(re.findall(r'📷 \*\*(?:Фото|Изображение)', content))
    stats['pdfs'] = len(re.findall(r'📄 \*\*(?:PDF|Документ)', content))
    stats['contacts_vcf'] = len(re.findall(r'📇 \*\*Контакт', content))

    # Даты
    dates = re.findall(r'### (\d{2}\.\d{2}\.\d{4})', content)
    if dates:
        stats['first_date'] = dates[0]
        stats['last_date'] = dates[-1]
        stats['days_active'] = len(set(dates))

        # Сообщения по датам
        current_date = None
        for line in content.split('\n'):
            date_match = re.match(r'### (\d{2}\.\d{2}\.\d{4})', line)
            if date_match:
                current_date = date_match.group(1)
            elif current_date and re.match(r'\*\*[👤👨👩]', line):
                stats['messages_by_date'][current_date] += 1

        if stats['messages_by_date']:
            stats['most_active_day'] = max(stats['messages_by_date'], key=stats['messages_by_date'].get)
            stats['avg_messages_per_day'] = stats['total_messages'] / max(stats['days_active'], 1)

    # Финансы
    rub_amounts = re.findall(r'Сумма[:\s]*(\d{1,3}(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(?:RUB|руб|₽)', content, re.IGNORECASE)
    for amount in rub_amounts:
        try:
            stats['total_rub'] += float(amount.replace(' ', '').replace(',', ''))
            stats['operations_count'] += 1
        except:
            pass

    aed_amounts = re.findall(r'Сумма[:\s]*(\d{1,3}(?:[\s,]\d{3})*(?:\.\d{2})?)\s*(?:AED|дирхам)', content, re.IGNORECASE)
    for amount in aed_amounts:
        try:
            stats['total_aed'] += float(amount.replace(' ', '').replace(',', ''))
        except:
            pass

    return stats


# ═══════════════════════════════════════════════════════════════
# МЕТРИКИ КАЧЕСТВА ОБСЛУЖИВАНИЯ
# ═══════════════════════════════════════════════════════════════

def parse_message_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """Парсит дату и время сообщения."""
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        except ValueError:
            return None


def is_business_hours(dt: datetime) -> bool:
    """Проверяет, попадает ли время в рабочие часы."""
    if dt.weekday() not in BUSINESS_DAYS:
        return False
    return BUSINESS_HOURS_START <= dt.hour < BUSINESS_HOURS_END


def calculate_response_time(client_dt: datetime, response_dt: datetime, business_hours_only: bool = False) -> float:
    """
    Вычисляет время ответа в минутах.

    Args:
        client_dt: Время сообщения клиента
        response_dt: Время ответа
        business_hours_only: Учитывать только рабочие часы

    Returns:
        Время ответа в минутах
    """
    if response_dt <= client_dt:
        return 0.0

    if not business_hours_only:
        delta = response_dt - client_dt
        return delta.total_seconds() / 60

    # Расчёт только рабочих минут
    business_minutes = 0
    current = client_dt

    while current < response_dt:
        if is_business_hours(current):
            business_minutes += 1
        current += timedelta(minutes=1)

    return float(business_minutes)


def calculate_quality_metrics(filepath: str) -> Dict:
    """
    Вычисляет метрики качества обслуживания.

    Returns:
        Dict с метриками:
        - frt_avg: Среднее First Response Time (мин)
        - frt_median: Медиана FRT
        - frt_min: Минимальный FRT
        - frt_max: Максимальный FRT
        - art_avg: Среднее Average Response Time (мин)
        - art_median: Медиана ART
        - sla_frt_met: % ответов в рамках SLA
        - response_rate: % сообщений с ответом
        - conversations_count: Количество "диалогов"
    """
    metrics = {
        'frt_avg': None,
        'frt_median': None,
        'frt_min': None,
        'frt_max': None,
        'frt_samples': 0,
        'art_avg': None,
        'art_median': None,
        'art_min': None,
        'art_max': None,
        'art_samples': 0,
        'sla_frt_excellent': 0,
        'sla_frt_good': 0,
        'sla_frt_acceptable': 0,
        'sla_frt_met_percent': 0,
        'response_rate': 0,
        'conversations_count': 0,
        'unanswered_messages': 0,
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return metrics

    # Парсим сообщения с датами и отправителями
    # Формат: ### DD.MM.YYYY и **Emoji Name** [HH:MM:SS]
    messages = []
    current_date = None

    for line in content.split('\n'):
        # Дата
        date_match = re.match(r'### (\d{2}\.\d{2}\.\d{4})', line)
        if date_match:
            current_date = date_match.group(1)
            continue

        # Сообщение с отправителем
        msg_match = re.match(r'\*\*([👤👨👩][^*]+)\*\*\s*\[(\d{2}:\d{2}:\d{2})\]', line)
        if msg_match and current_date:
            sender = msg_match.group(1).strip()
            time_str = msg_match.group(2)
            dt = parse_message_datetime(current_date, time_str)

            if dt:
                # Определяем, это клиент или менеджер
                is_manager = sender.startswith('👨') or sender.startswith('👩')
                messages.append({
                    'datetime': dt,
                    'sender': sender,
                    'is_manager': is_manager,
                    'is_client': not is_manager,
                })

    if len(messages) < 2:
        return metrics

    # Вычисляем FRT и ART
    first_response_times = []
    all_response_times = []
    conversation_started = False
    last_client_msg_dt = None
    unanswered = 0

    for i, msg in enumerate(messages):
        if msg['is_client']:
            last_client_msg_dt = msg['datetime']
            conversation_started = True

            # Проверяем, был ли ответ
            has_response = False
            for j in range(i + 1, len(messages)):
                if messages[j]['is_manager']:
                    has_response = True
                    break
                if messages[j]['is_client']:
                    # Новое сообщение клиента без ответа
                    break

            if not has_response and i == len(messages) - 1:
                unanswered += 1

        elif msg['is_manager'] and last_client_msg_dt:
            response_time = calculate_response_time(last_client_msg_dt, msg['datetime'])

            if response_time > 0:
                # Первый ответ в диалоге
                if conversation_started:
                    first_response_times.append(response_time)
                    conversation_started = False

                all_response_times.append(response_time)

            last_client_msg_dt = None

    metrics['unanswered_messages'] = unanswered

    # FRT статистика
    if first_response_times:
        metrics['frt_samples'] = len(first_response_times)
        metrics['frt_avg'] = round(sum(first_response_times) / len(first_response_times), 1)
        metrics['frt_min'] = round(min(first_response_times), 1)
        metrics['frt_max'] = round(max(first_response_times), 1)

        sorted_frt = sorted(first_response_times)
        mid = len(sorted_frt) // 2
        metrics['frt_median'] = round(sorted_frt[mid], 1)

        # SLA соблюдение
        excellent = sum(1 for t in first_response_times if t <= SLA_FRT_EXCELLENT)
        good = sum(1 for t in first_response_times if t <= SLA_FRT_GOOD)
        acceptable = sum(1 for t in first_response_times if t <= SLA_FRT_ACCEPTABLE)

        metrics['sla_frt_excellent'] = excellent
        metrics['sla_frt_good'] = good
        metrics['sla_frt_acceptable'] = acceptable
        metrics['sla_frt_met_percent'] = round(acceptable / len(first_response_times) * 100, 1)

    # ART статистика
    if all_response_times:
        metrics['art_samples'] = len(all_response_times)
        metrics['art_avg'] = round(sum(all_response_times) / len(all_response_times), 1)
        metrics['art_min'] = round(min(all_response_times), 1)
        metrics['art_max'] = round(max(all_response_times), 1)

        sorted_art = sorted(all_response_times)
        mid = len(sorted_art) // 2
        metrics['art_median'] = round(sorted_art[mid], 1)

    # Response rate
    client_messages = sum(1 for m in messages if m['is_client'])
    if client_messages > 0:
        metrics['response_rate'] = round((client_messages - unanswered) / client_messages * 100, 1)
        metrics['conversations_count'] = len(first_response_times)

    return metrics


# ═══════════════════════════════════════════════════════════════
# СТАТИСТИКА ПО ЯЗЫКАМ
# ═══════════════════════════════════════════════════════════════

# Языковые маркеры
LANGUAGE_MARKERS = {
    'ru': {
        'chars': re.compile(r'[\u0400-\u04FF]'),  # Кириллица
        'words': {'привет', 'спасибо', 'здравствуйте', 'хорошо', 'сколько', 'когда', 'да', 'нет'},
    },
    'en': {
        'chars': re.compile(r'[a-zA-Z]'),
        'words': {'hello', 'thanks', 'please', 'okay', 'yes', 'no', 'how', 'much'},
    },
    'ar': {
        'chars': re.compile(r'[\u0600-\u06FF]'),  # Арабский
        'words': {'مرحبا', 'شكرا', 'نعم', 'لا', 'كم', 'متى'},
    },
    'de': {
        'chars': re.compile(r'[äöüßÄÖÜ]'),
        'words': {'danke', 'bitte', 'guten', 'tag', 'ja', 'nein'},
    },
    'fr': {
        'chars': re.compile(r'[àâçéèêëïîôùûü]'),
        'words': {'merci', 'bonjour', 'oui', 'non', 'comment'},
    },
}


def detect_message_language(text: str) -> str:
    """Быстрая детекция языка сообщения."""
    if not text or len(text) < 2:
        return 'unknown'

    text_lower = text.lower()

    # Подсчёт символов каждого скрипта
    scores = {}

    for lang, markers in LANGUAGE_MARKERS.items():
        char_count = len(markers['chars'].findall(text))
        word_count = sum(1 for word in markers['words'] if word in text_lower)
        scores[lang] = char_count + word_count * 10

    if not scores or max(scores.values()) == 0:
        return 'unknown'

    return max(scores, key=scores.get)


def calculate_language_statistics(filepath: str) -> Dict:
    """
    Вычисляет статистику по языкам в переписке.

    Returns:
        Dict с данными о языках
    """
    stats = {
        'languages_detected': {},
        'primary_language': 'unknown',
        'multilingual': False,
        'language_by_sender': {},
        'total_analyzed': 0,
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return stats

    # Парсим сообщения
    current_sender = None
    language_counts = Counter()
    sender_languages = defaultdict(Counter)

    for line in content.split('\n'):
        # Отправитель
        sender_match = re.match(r'\*\*([👤👨👩][^*]+)\*\*', line)
        if sender_match:
            current_sender = sender_match.group(1).strip()
            continue

        # Текст сообщения (строки с отступом после отправителя)
        if line.startswith('  ') and current_sender:
            text = line.strip()
            # Пропускаем медиа-маркеры
            if text.startswith('[') or text.startswith('🎤') or text.startswith('📷'):
                continue

            lang = detect_message_language(text)
            if lang != 'unknown':
                language_counts[lang] += 1
                sender_languages[current_sender][lang] += 1
                stats['total_analyzed'] += 1

    # Формируем статистику
    if language_counts:
        total = sum(language_counts.values())
        stats['languages_detected'] = {
            lang: {
                'count': count,
                'percentage': round(count / total * 100, 1)
            }
            for lang, count in language_counts.most_common()
        }

        stats['primary_language'] = language_counts.most_common(1)[0][0]
        stats['multilingual'] = len(language_counts) > 1 and language_counts.most_common(2)[1][1] > total * 0.1

    # Языки по отправителям
    for sender, langs in sender_languages.items():
        total_sender = sum(langs.values())
        stats['language_by_sender'][sender] = {
            'primary': langs.most_common(1)[0][0] if langs else 'unknown',
            'distribution': {
                lang: round(count / total_sender * 100, 1)
                for lang, count in langs.most_common(3)
            }
        }

    return stats


def generate_statistics_section(stats, quality_metrics: Dict = None, language_stats: Dict = None):
    """
    Генерирует Markdown секцию со статистикой.

    Args:
        stats: Базовая статистика
        quality_metrics: Метрики качества (FRT, ART)
        language_stats: Статистика по языкам
    """

    output = []
    output.append("## Статистика переписки")
    output.append("")
    output.append("| Метрика | Значение |")
    output.append("|---------|----------|")
    output.append(f"| Всего сообщений | {stats['total_messages']} |")
    output.append(f"| Голосовых | {stats['voice_messages']} |")
    output.append(f"| Фото | {stats['photos']} |")
    output.append(f"| PDF документов | {stats['pdfs']} |")
    output.append(f"| Контактов VCF | {stats['contacts_vcf']} |")
    output.append(f"| Дней переписки | {stats['days_active']} |")
    output.append(f"| Период | {stats['first_date']} — {stats['last_date']} |")
    output.append(f"| Среднее сообщ./день | {stats['avg_messages_per_day']:.1f} |")

    if stats['most_active_day']:
        output.append(f"| Самый активный день | {stats['most_active_day']} ({stats['messages_by_date'].get(stats['most_active_day'], 0)} сообщ.) |")

    output.append("")

    # Распределение по отправителям
    if stats['messages_by_sender']:
        output.append("### По отправителям")
        output.append("")
        total = stats['total_messages']
        for sender, count in sorted(stats['messages_by_sender'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            output.append(f"- {sender}: {count} ({pct:.0f}%)")
        output.append("")

    # Метрики качества (FRT, ART)
    if quality_metrics and quality_metrics.get('frt_avg') is not None:
        output.append("### Метрики качества")
        output.append("")
        output.append("| Метрика | Значение |")
        output.append("|---------|----------|")

        # FRT
        output.append(f"| FRT среднее | {quality_metrics['frt_avg']} мин |")
        output.append(f"| FRT медиана | {quality_metrics['frt_median']} мин |")
        output.append(f"| FRT мин/макс | {quality_metrics['frt_min']} / {quality_metrics['frt_max']} мин |")

        # ART
        if quality_metrics.get('art_avg') is not None:
            output.append(f"| ART среднее | {quality_metrics['art_avg']} мин |")
            output.append(f"| ART медиана | {quality_metrics['art_median']} мин |")

        # SLA
        output.append(f"| SLA соблюдение | {quality_metrics['sla_frt_met_percent']}% |")
        output.append(f"| Response rate | {quality_metrics['response_rate']}% |")

        if quality_metrics['unanswered_messages'] > 0:
            output.append(f"| Без ответа | {quality_metrics['unanswered_messages']} |")

        output.append("")

        # Визуализация SLA
        if quality_metrics['frt_samples'] > 0:
            output.append("**SLA распределение:**")
            output.append(f"- Отлично (<5 мин): {quality_metrics['sla_frt_excellent']}")
            output.append(f"- Хорошо (<15 мин): {quality_metrics['sla_frt_good']}")
            output.append(f"- Приемлемо (<60 мин): {quality_metrics['sla_frt_acceptable']}")
            output.append("")

    # Статистика по языкам
    if language_stats and language_stats.get('languages_detected'):
        output.append("### Языки переписки")
        output.append("")

        lang_names = {
            'ru': 'Русский', 'en': 'Английский', 'ar': 'Арабский',
            'de': 'Немецкий', 'fr': 'Французский', 'unknown': 'Не определён'
        }

        output.append(f"**Основной язык:** {lang_names.get(language_stats['primary_language'], language_stats['primary_language'])}")
        if language_stats['multilingual']:
            output.append("**Многоязычная переписка:** Да")
        output.append("")

        output.append("| Язык | Сообщений | % |")
        output.append("|------|-----------|---|")
        for lang, data in language_stats['languages_detected'].items():
            lang_name = lang_names.get(lang, lang)
            output.append(f"| {lang_name} | {data['count']} | {data['percentage']}% |")
        output.append("")

    # Финансы
    if stats['total_rub'] > 0 or stats['total_aed'] > 0:
        output.append("### Финансы")
        output.append("")
        if stats['total_rub'] > 0:
            output.append(f"- **Оборот RUB:** {stats['total_rub']:,.0f} ₽")
        if stats['total_aed'] > 0:
            output.append(f"- **Оборот AED:** {stats['total_aed']:,.0f} AED")
        output.append(f"- **Операций:** {stats['operations_count']}")
        output.append("")

    return '\n'.join(output)

def add_statistics_to_chat(filepath, output_path=None, include_quality: bool = True, include_language: bool = True):
    """
    Добавляет секцию статистики в файл чата.

    Args:
        filepath: Путь к файлу чата
        output_path: Путь для сохранения (если не указан - перезаписывает исходный)
        include_quality: Включить метрики качества (FRT, ART)
        include_language: Включить статистику по языкам
    """

    stats = calculate_statistics(filepath)
    if not stats:
        print(f"Не удалось вычислить статистику для {filepath}")
        return

    # Дополнительные метрики
    quality_metrics = None
    language_stats = None

    if include_quality:
        quality_metrics = calculate_quality_metrics(filepath)

    if include_language:
        language_stats = calculate_language_statistics(filepath)

    stats_section = generate_statistics_section(stats, quality_metrics, language_stats)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Проверяем, есть ли уже статистика
    if '## Статистика переписки' in content:
        # Обновляем существующую
        content = re.sub(
            r'## Статистика переписки.*?(?=## |$)',
            stats_section + '\n',
            content,
            flags=re.DOTALL
        )
    else:
        # Добавляем перед "## История переписки" или в конец
        if '## История переписки' in content:
            content = content.replace(
                '## История переписки',
                stats_section + '\n---\n\n## История переписки'
            )
        else:
            content = content + '\n\n---\n\n' + stats_section

    output_file = output_path or filepath
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Статистика добавлена: {output_file}")

def process_all_chats(chats_dir):
    """Добавляет статистику во все чаты"""

    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern = os.path.join(chats_dir, subdir, '*.md')
        for filepath in glob.glob(pattern):
            add_statistics_to_chat(filepath)

if __name__ == "__main__":
    import glob

    parser = argparse.ArgumentParser(description="Генерация статистики чата")
    parser.add_argument("input", nargs='?', help="Путь к файлу чата или папке")
    parser.add_argument("--all", action="store_true", help="Обработать все чаты")
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")

    args = parser.parse_args()

    if args.all:
        process_all_chats(args.chats_dir)
    elif args.input:
        if os.path.isfile(args.input):
            add_statistics_to_chat(args.input)
        else:
            print(f"Файл не найден: {args.input}")
    else:
        print("Укажите файл или используйте --all для обработки всех чатов")
