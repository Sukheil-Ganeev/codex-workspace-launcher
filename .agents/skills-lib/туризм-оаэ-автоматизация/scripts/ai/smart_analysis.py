#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Умный анализ чатов.
Поиск аномалий, паттернов, рекомендации.
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, ANALYTICS_DIR, CONTACT_TYPES, ensure_directories

# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ АНОМАЛИЙ
# ═══════════════════════════════════════════════════════════════

def detect_unusual_amounts(operations: List[Dict], threshold_multiplier: float = 3.0) -> List[Dict]:
    """
    Найти необычно большие суммы.

    Args:
        operations: Список операций
        threshold_multiplier: Множитель для определения аномалии (3x от среднего)
    """
    anomalies = []

    # Группируем по валютам
    by_currency = defaultdict(list)
    for op in operations:
        by_currency[op['currency']].append(op['amount'])

    # Для каждой валюты ищем аномалии
    for currency, amounts in by_currency.items():
        if len(amounts) < 3:
            continue

        avg = sum(amounts) / len(amounts)
        threshold = avg * threshold_multiplier

        for op in operations:
            if op['currency'] == currency and op['amount'] > threshold:
                anomalies.append({
                    'type': 'unusual_amount',
                    'operation': op,
                    'average': avg,
                    'threshold': threshold,
                    'deviation': op['amount'] / avg,
                    'message': f"Сумма {op['amount']:,.0f} {currency} в {op['amount']/avg:.1f}x выше среднего ({avg:,.0f})"
                })

    return anomalies


def detect_time_gaps(messages: List[Dict], gap_days: int = 30) -> List[Dict]:
    """
    Найти большие перерывы в общении.
    """
    anomalies = []

    # Сортируем по дате
    sorted_msgs = sorted(messages, key=lambda x: x.get('date', datetime.min))

    prev_date = None
    prev_contact = None

    for msg in sorted_msgs:
        if prev_date and msg.get('date'):
            gap = (msg['date'] - prev_date).days

            if gap > gap_days:
                anomalies.append({
                    'type': 'time_gap',
                    'contact': msg.get('contact', 'Unknown'),
                    'gap_days': gap,
                    'from_date': prev_date,
                    'to_date': msg['date'],
                    'message': f"Перерыв {gap} дней с {prev_contact or 'контактом'}"
                })

        prev_date = msg.get('date')
        prev_contact = msg.get('contact')

    return anomalies


def detect_missing_responses(content: str, max_unanswered: int = 3) -> List[Dict]:
    """
    Найти вопросы без ответов.
    """
    anomalies = []
    lines = content.split('\n')

    unanswered = []

    for i, line in enumerate(lines):
        if '?' in line and len(line) > 10:
            unanswered.append({
                'line': i + 1,
                'text': line.strip()[:100]
            })
        elif unanswered and line.strip() and not line.startswith('**'):
            # Есть ответ - очищаем
            unanswered = []

    if len(unanswered) >= max_unanswered:
        anomalies.append({
            'type': 'missing_responses',
            'count': len(unanswered),
            'questions': unanswered[:5],
            'message': f"Найдено {len(unanswered)} вопросов без ответа"
        })

    return anomalies


def detect_duplicate_operations(operations: List[Dict]) -> List[Dict]:
    """
    Найти возможные дубликаты операций.
    """
    anomalies = []
    seen = defaultdict(list)

    for op in operations:
        key = (
            op.get('date', ''),
            op.get('amount', 0),
            op.get('currency', '')
        )
        seen[key].append(op)

    for key, ops in seen.items():
        if len(ops) > 1:
            anomalies.append({
                'type': 'duplicate_operation',
                'count': len(ops),
                'operations': ops,
                'message': f"Возможный дубликат: {key[1]:,.0f} {key[2]} на {key[0]}"
            })

    return anomalies


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ ПАТТЕРНОВ
# ═══════════════════════════════════════════════════════════════

def analyze_activity_patterns(operations: List[Dict]) -> Dict:
    """
    Анализ паттернов активности.
    """
    patterns = {
        'by_weekday': defaultdict(int),
        'by_hour': defaultdict(int),
        'by_month': defaultdict(int),
        'peak_days': [],
        'quiet_days': [],
    }

    for op in operations:
        date = op.get('date')
        if isinstance(date, datetime):
            patterns['by_weekday'][date.weekday()] += 1
            patterns['by_hour'][date.hour] += 1
            patterns['by_month'][date.month] += 1

    # Пиковые дни
    if patterns['by_weekday']:
        max_day = max(patterns['by_weekday'], key=patterns['by_weekday'].get)
        min_day = min(patterns['by_weekday'], key=patterns['by_weekday'].get)

        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        patterns['peak_day'] = weekdays[max_day]
        patterns['quiet_day'] = weekdays[min_day]

    return patterns


def analyze_contact_patterns(chats_data: List[Dict]) -> Dict:
    """
    Анализ паттернов по контактам.
    """
    patterns = {
        'most_active': [],
        'highest_volume': [],
        'frequent_topics': defaultdict(int),
    }

    for chat in chats_data:
        patterns['frequent_topics'][chat.get('topic', 'общее')] += 1

    return patterns


# ═══════════════════════════════════════════════════════════════
# РЕКОМЕНДАЦИИ
# ═══════════════════════════════════════════════════════════════

def generate_recommendations(anomalies: List[Dict], patterns: Dict) -> List[str]:
    """
    Сгенерировать рекомендации на основе анализа.
    """
    recommendations = []

    # По аномалиям
    for a in anomalies:
        if a['type'] == 'unusual_amount':
            recommendations.append(
                f"⚠️ Проверьте операцию на {a['operation'].get('amount'):,.0f} "
                f"{a['operation'].get('currency')} - сумма значительно выше обычной"
            )

        elif a['type'] == 'time_gap':
            recommendations.append(
                f"📅 Возобновите контакт с {a['contact']} - перерыв {a['gap_days']} дней"
            )

        elif a['type'] == 'missing_responses':
            recommendations.append(
                f"❓ Проверьте {a['count']} неотвеченных вопросов"
            )

        elif a['type'] == 'duplicate_operation':
            recommendations.append(
                f"🔄 Проверьте возможный дубликат операции: {a['message']}"
            )

    # По паттернам
    if patterns.get('peak_day'):
        recommendations.append(
            f"📊 Пиковая активность в {patterns['peak_day']} - планируйте важные операции на этот день"
        )

    if patterns.get('quiet_day'):
        recommendations.append(
            f"💤 {patterns['quiet_day']} - самый тихий день, хорош для административных задач"
        )

    return recommendations


# ═══════════════════════════════════════════════════════════════
# СБОР ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def extract_operations_from_all_chats() -> List[Dict]:
    """Извлечь все операции из чатов."""
    operations = []

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Извлекаем операции из таблиц
                table_pattern = r'\| (\d{1,2}\.\d{1,2}\.\d{4}) \| ([^|]+) \| ([\d\s,]+)\s*(RUB|AED|USD) \|'

                for match in re.finditer(table_pattern, content, re.IGNORECASE):
                    date_str, operation, amount_str, currency = match.groups()

                    try:
                        date = datetime.strptime(date_str, '%d.%m.%Y')
                        amount = float(amount_str.replace(' ', '').replace(',', ''))

                        operations.append({
                            'date': date,
                            'operation': operation.strip(),
                            'amount': amount,
                            'currency': currency.upper(),
                            'contact': file_path.stem,
                            'file': str(file_path),
                        })
                    except ValueError:
                        continue

    return operations


def collect_chat_metadata() -> List[Dict]:
    """Собрать метаданные всех чатов."""
    chats = []

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Извлекаем метаданные
                topic_match = re.search(r'\*\*Тематика:\*\*\s*(.+)', content)
                phone_match = re.search(r'\*\*Телефон:\*\*\s*(.+)', content)

                chats.append({
                    'file': str(file_path),
                    'name': file_path.stem,
                    'type': contact_type,
                    'topic': topic_match.group(1).strip() if topic_match else 'общее',
                    'phone': phone_match.group(1).strip() if phone_match else '',
                    'size': file_path.stat().st_size,
                })

    return chats


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТА
# ═══════════════════════════════════════════════════════════════

def generate_smart_report() -> str:
    """Сгенерировать умный отчёт."""
    operations = extract_operations_from_all_chats()
    chats = collect_chat_metadata()

    # Анализ
    anomalies = []
    anomalies.extend(detect_unusual_amounts(operations))
    anomalies.extend(detect_duplicate_operations(operations))

    patterns = analyze_activity_patterns(operations)
    contact_patterns = analyze_contact_patterns(chats)

    recommendations = generate_recommendations(anomalies, patterns)

    # Формируем отчёт
    report = f"""# Умный анализ чатов

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*
*Проанализировано: {len(chats)} чатов, {len(operations)} операций*

---

## 🚨 Аномалии

"""

    if anomalies:
        for a in anomalies:
            report += f"- **{a['type']}**: {a['message']}\n"
    else:
        report += "*Аномалий не обнаружено*\n"

    report += "\n---\n\n## 📊 Паттерны активности\n\n"

    if patterns.get('peak_day'):
        report += f"- Пиковый день: **{patterns['peak_day']}**\n"
    if patterns.get('quiet_day'):
        report += f"- Тихий день: **{patterns['quiet_day']}**\n"

    report += "\n### Активность по дням недели\n\n"
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    report += "| День | Операций |\n|------|----------|\n"
    for i, day in enumerate(weekdays):
        count = patterns['by_weekday'].get(i, 0)
        report += f"| {day} | {count} |\n"

    report += "\n---\n\n## 💡 Рекомендации\n\n"

    if recommendations:
        for r in recommendations:
            report += f"- {r}\n"
    else:
        report += "*Рекомендаций нет*\n"

    report += "\n---\n\n## 📈 Статистика\n\n"
    report += f"| Показатель | Значение |\n|------------|----------|\n"
    report += f"| Чатов | {len(chats)} |\n"
    report += f"| Операций | {len(operations)} |\n"
    report += f"| Аномалий | {len(anomalies)} |\n"

    return report


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Умный анализ чатов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python smart_analysis.py                     # Полный анализ
  python smart_analysis.py --anomalies         # Только аномалии
  python smart_analysis.py --recommendations   # Только рекомендации
  python smart_analysis.py -o report.md        # Сохранить отчёт
        """
    )

    parser.add_argument('--anomalies', action='store_true', help='Только аномалии')
    parser.add_argument('--recommendations', action='store_true', help='Только рекомендации')
    parser.add_argument('--patterns', action='store_true', help='Только паттерны')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('--json', action='store_true', help='JSON вывод')

    args = parser.parse_args()

    ensure_directories()

    operations = extract_operations_from_all_chats()
    chats = collect_chat_metadata()

    if args.anomalies:
        anomalies = []
        anomalies.extend(detect_unusual_amounts(operations))
        anomalies.extend(detect_duplicate_operations(operations))

        if args.json:
            import json
            # Конвертируем datetime в строки
            for a in anomalies:
                if 'operation' in a and 'date' in a['operation']:
                    a['operation']['date'] = a['operation']['date'].isoformat()
            print(json.dumps(anomalies, ensure_ascii=False, indent=2))
        else:
            print(f"\n🚨 Найдено аномалий: {len(anomalies)}\n")
            for a in anomalies:
                print(f"  - [{a['type']}] {a['message']}")
        return

    if args.recommendations:
        anomalies = detect_unusual_amounts(operations) + detect_duplicate_operations(operations)
        patterns = analyze_activity_patterns(operations)
        recommendations = generate_recommendations(anomalies, patterns)

        print("\n💡 Рекомендации:\n")
        for r in recommendations:
            print(f"  {r}")
        return

    if args.patterns:
        patterns = analyze_activity_patterns(operations)
        print("\n📊 Паттерны активности:")
        print(f"  Пиковый день: {patterns.get('peak_day', 'N/A')}")
        print(f"  Тихий день: {patterns.get('quiet_day', 'N/A')}")
        return

    # Полный отчёт
    report = generate_smart_report()

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = ANALYTICS_DIR / f"анализ_{datetime.now().strftime('%Y-%m-%d')}.md"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ Отчёт сохранён: {output_path}")


if __name__ == "__main__":
    main()
