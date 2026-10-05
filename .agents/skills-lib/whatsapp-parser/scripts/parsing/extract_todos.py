#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Извлечение TODO, незавершённых операций и напоминаний из чатов.
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, TASKS_DIR, CONTACT_TYPES, ensure_directories

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРНЫ ДЛЯ ЗАДАЧ
# ═══════════════════════════════════════════════════════════════

TODO_PATTERNS = [
    # Прямые TODO
    r'(?:TODO|ЗАДАЧА|СДЕЛАТЬ)[:：]\s*(.+)',

    # Обещания
    r'(?:обещал[аи]?|договорились|нужно)\s+(.+)',

    # Напоминания
    r'(?:напомн|не забы)(?:ить|удь)\s*[:：]?\s*(.+)',

    # Вопросы без ответа
    r'\?\s*$',
]

PENDING_OPERATION_PATTERNS = [
    # Ожидание перевода
    r'(?:жд[уе]|ожида)(?:ть|ю|ем)\s+(?:перевод|оплату|деньги)',

    # Обещанные действия
    r'(?:скину|отправлю|пришлю|перевед[у|ём])\s+(?:позже|завтра|вечером|утром)',

    # Незавершённые обмены
    r'(?:курс|обмен)\s+(?:уточню|скажу|напишу)',
]

DATE_PATTERNS = [
    # Конкретные даты
    r'(\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?)',

    # Относительные даты
    r'(завтра|послезавтра|в понедельник|во вторник|в среду|в четверг|в пятницу|в субботу|в воскресенье)',

    # Время
    r'(?:в\s+)?(\d{1,2}[:．]\d{2})',
]


# ═══════════════════════════════════════════════════════════════
# ИЗВЛЕЧЕНИЕ
# ═══════════════════════════════════════════════════════════════

def extract_todos_from_text(text: str, source: str = "") -> List[Dict]:
    """Извлечь TODO из текста."""
    todos = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        for pattern in TODO_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Определяем контекст (строки вокруг)
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = '\n'.join(lines[context_start:context_end])

                # Ищем дату
                date_match = None
                for date_pattern in DATE_PATTERNS:
                    date_match = re.search(date_pattern, line, re.IGNORECASE)
                    if date_match:
                        break

                todos.append({
                    'type': 'todo',
                    'text': match.group(1) if match.lastindex else line.strip(),
                    'context': context,
                    'line_number': i + 1,
                    'source': source,
                    'date': date_match.group(1) if date_match else None,
                    'extracted_at': datetime.now().isoformat(),
                })

    return todos


def extract_pending_operations(text: str, source: str = "") -> List[Dict]:
    """Извлечь незавершённые операции."""
    pending = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        for pattern in PENDING_OPERATION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = '\n'.join(lines[context_start:context_end])

                # Ищем сумму
                amount_match = re.search(r'(\d[\d\s,]*)\s*(RUB|AED|USD|руб|дирхам|\$)',
                                        line, re.IGNORECASE)

                pending.append({
                    'type': 'pending_operation',
                    'text': line.strip(),
                    'context': context,
                    'line_number': i + 1,
                    'source': source,
                    'amount': amount_match.group(1) if amount_match else None,
                    'currency': amount_match.group(2) if amount_match else None,
                    'extracted_at': datetime.now().isoformat(),
                })

    return pending


def extract_unanswered_questions(text: str, source: str = "") -> List[Dict]:
    """Извлечь вопросы без ответа."""
    questions = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        if '?' in line and len(line) > 10:
            # Проверяем есть ли ответ в следующих строках
            has_answer = False
            for j in range(i + 1, min(len(lines), i + 4)):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('**') and '?' not in next_line:
                    has_answer = True
                    break

            if not has_answer:
                questions.append({
                    'type': 'unanswered_question',
                    'text': line.strip(),
                    'line_number': i + 1,
                    'source': source,
                    'extracted_at': datetime.now().isoformat(),
                })

    return questions


def extract_all_from_file(file_path: Path) -> List[Dict]:
    """Извлечь все задачи из файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    source = file_path.name

    items = []
    items.extend(extract_todos_from_text(content, source))
    items.extend(extract_pending_operations(content, source))
    items.extend(extract_unanswered_questions(content, source))

    return items


def extract_from_all_chats() -> List[Dict]:
    """Извлечь задачи из всех чатов."""
    all_items = []

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                items = extract_all_from_file(file_path)
                for item in items:
                    item['contact_type'] = contact_type
                all_items.extend(items)

    return all_items


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТА
# ═══════════════════════════════════════════════════════════════

def generate_tasks_report(items: List[Dict]) -> str:
    """Сгенерировать отчёт по задачам."""
    report = f"""# Задачи и незавершённые операции

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*
*Найдено элементов: {len(items)}*

---

"""

    # Группируем по типам
    todos = [i for i in items if i['type'] == 'todo']
    pending = [i for i in items if i['type'] == 'pending_operation']
    questions = [i for i in items if i['type'] == 'unanswered_question']

    if todos:
        report += "## TODO / Задачи\n\n"
        for item in todos:
            report += f"- [ ] **{item['source']}** (строка {item['line_number']})\n"
            report += f"  {item['text']}\n"
            if item.get('date'):
                report += f"  📅 Дата: {item['date']}\n"
            report += "\n"

    if pending:
        report += "## Незавершённые операции\n\n"
        for item in pending:
            report += f"- [ ] **{item['source']}** (строка {item['line_number']})\n"
            report += f"  {item['text']}\n"
            if item.get('amount'):
                report += f"  💰 Сумма: {item['amount']} {item.get('currency', '')}\n"
            report += "\n"

    if questions:
        report += "## Вопросы без ответа\n\n"
        for item in questions[:20]:  # Лимит
            report += f"- **{item['source']}** (строка {item['line_number']})\n"
            report += f"  {item['text']}\n\n"

    return report


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Извлечение задач из чатов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python extract_todos.py                       # Все чаты
  python extract_todos.py chat.md               # Один файл
  python extract_todos.py --output tasks.md     # Сохранить отчёт
  python extract_todos.py --json                # JSON вывод
        """
    )

    parser.add_argument('input', nargs='?', help='Входной файл (или все чаты)')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('--json', action='store_true', help='JSON вывод')
    parser.add_argument('--print', action='store_true', help='Вывести в консоль')

    args = parser.parse_args()

    ensure_directories()

    if args.input:
        items = extract_all_from_file(Path(args.input))
    else:
        items = extract_from_all_chats()

    if args.json:
        import json
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return

    report = generate_tasks_report(items)

    if args.print or (not args.output):
        print(report)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = TASKS_DIR / f"задачи_{datetime.now().strftime('%Y-%m-%d')}.md"

    if args.output or not args.print:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Сохранено: {output_path}")


if __name__ == "__main__":
    main()
