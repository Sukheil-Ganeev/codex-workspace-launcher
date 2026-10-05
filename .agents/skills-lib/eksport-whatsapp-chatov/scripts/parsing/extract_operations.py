#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение финансовых операций из чатов в CSV и MD
ВАЖНЫЙ ПРИНЦИП: Никакие данные НЕ теряются! Сохраняем ВСЕ поля из исходных PDF/чеков.
"""

import sys
import os
import re
import glob
import csv
import argparse
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Расширенные паттерны для извлечения данных
PATTERNS = {
    # Суммы
    'amount': [
        r'(?:Сумма|СУММА|Amount)[:\s]*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)\s*(RUB|руб|₽|рублей|AED|дирхам|USD|\$)',
        r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)\s*(RUB|руб|₽|рублей|AED|дирхам|USD|\$)',
    ],
    # Комиссия
    'fee': [
        r'(?:Комиссия|Commission|Fee)[:\s]*(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)\s*(RUB|руб|₽|AED|USD|\$)?',
        r'(?:без комиссии|комиссия\s*0|0\s*₽\s*комиссия)',
    ],
    # Дата и время
    'datetime': [
        r'(\d{2}[./]\d{2}[./]\d{4})\s+(\d{2}:\d{2}(?::\d{2})?)',
        r'(\d{2}[./]\d{2}[./]\d{4})',
        r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}(?::\d{2})?)',
    ],
    # Отправитель
    'sender_name': [
        r'(?:Отправитель|От кого|Sender|От)[:\s]*([А-ЯЁа-яёA-Za-z\s\.\-]+?)(?:\n|Счёт|Карта|$)',
        r'(?:ФИО отправителя)[:\s]*([А-ЯЁа-яё\s\.\-]+)',
    ],
    'sender_account': [
        r'(?:Счёт отправителя|Со счёта|From account)[:\s]*(\d{20}|\*{4}\s*\d{4}|\d{4}\s*\*{4}\s*\*{4}\s*\d{4})',
        r'(?:Карта)[:\s]*(\d{4}\s*\*{4}\s*\*{4}\s*\d{4}|\*+\d{4})',
    ],
    'sender_bank': [
        r'(?:Банк отправителя|Банк списания)[:\s]*([А-ЯЁа-яёA-Za-z\s\-]+?)(?:\n|$)',
    ],
    # Получатель
    'recipient_name': [
        r'(?:Получатель|Кому|Recipient|To)[:\s]*([А-ЯЁа-яёA-Za-z\s\.\-]+?)(?:\n|Счёт|Карта|Телефон|$)',
        r'(?:ФИО получателя)[:\s]*([А-ЯЁа-яё\s\.\-]+)',
    ],
    'recipient_account': [
        r'(?:Счёт получателя|На счёт|To account)[:\s]*(\d{20}|\*{4}\s*\d{4})',
        r'(?:На карту)[:\s]*(\d{4}\s*\*{4}\s*\*{4}\s*\d{4}|\*+\d{4})',
    ],
    'recipient_phone': [
        r'(?:Телефон получателя|Телефон|Phone)[:\s]*(\+?\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',
        r'(?:На номер)[:\s]*(\+?\d{11})',
    ],
    'recipient_bank': [
        r'(?:Банк получателя|Банк зачисления)[:\s]*([А-ЯЁа-яёA-Za-z\s\-]+?)(?:\n|$)',
    ],
    # Идентификаторы
    'transaction_id': [
        r'(?:Номер операции|№ операции|Transaction ID|ID операции|Номер транзакции)[:\s]*(\d+)',
        r'(?:Операция №)[:\s]*(\d+)',
    ],
    'sbp_id': [
        r'(?:Идентификатор СБП|СБП ID|SBP ID)[:\s]*([A-Za-z0-9\-]+)',
        r'(?:ID в СБП)[:\s]*([A-Za-z0-9\-]+)',
    ],
    'auth_code': [
        r'(?:Код авторизации|Auth code|Authorization)[:\s]*([A-Za-z0-9]+)',
    ],
    'reference': [
        r'(?:Reference|Референс|RRN)[:\s]*([A-Za-z0-9\-]+)',
    ],
    # Статус
    'status': [
        r'(?:Статус|Status)[:\s]*(Исполнен|Выполнен|Успешно|Completed|Success|В обработке|Pending|Отклонён|Declined)',
        r'(Перевод выполнен|Операция успешна|Успешно)',
    ],
    # Тип операции
    'type': [
        r'(?:Тип операции|Тип перевода|Type)[:\s]*([^\n]+)',
        r'(Перевод по СБП|СБП|Внутрибанковский перевод|Международный перевод|P2P|Перевод на карту)',
    ],
}


def normalize_currency(currency):
    """Нормализация названия валюты"""
    if not currency:
        return ''
    currency = currency.upper().strip()
    mapping = {
        'РУБ': 'RUB', '₽': 'RUB', 'РУБЛЕЙ': 'RUB', 'РУБЛЬ': 'RUB',
        'ДИРХАМ': 'AED', 'ДИРХАМОВ': 'AED',
        '$': 'USD', 'ДОЛЛАРОВ': 'USD', 'ДОЛЛАР': 'USD',
    }
    return mapping.get(currency, currency)


def extract_field(text, field_name):
    """Извлекает поле из текста по паттернам"""
    patterns = PATTERNS.get(field_name, [])
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip() if match.lastindex else match.group(0).strip()
    return ''


def extract_amount_with_currency(text):
    """Извлекает сумму и валюту"""
    for pattern in PATTERNS['amount']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(' ', '').replace(',', '.')
            # Убираем лишние точки кроме последней (разделитель копеек)
            parts = amount_str.split('.')
            if len(parts) > 2:
                amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
            try:
                amount = float(amount_str)
                currency = normalize_currency(match.group(2))
                return amount, currency
            except ValueError:
                continue
    return None, ''


def extract_fee(text):
    """Извлекает комиссию"""
    # Проверяем "без комиссии"
    if re.search(r'без комиссии|комиссия\s*0|0\s*₽\s*комиссия', text, re.IGNORECASE):
        return 0.0, ''

    for pattern in PATTERNS['fee'][:1]:  # Только первый паттерн с суммой
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fee_str = match.group(1).replace(' ', '').replace(',', '.')
            try:
                fee = float(fee_str)
                currency = normalize_currency(match.group(2)) if match.lastindex >= 2 else ''
                return fee, currency
            except (ValueError, IndexError):
                continue
    return None, ''


def extract_datetime(text):
    """Извлекает дату и время"""
    for pattern in PATTERNS['datetime']:
        match = re.search(pattern, text)
        if match:
            date = match.group(1)
            time = match.group(2) if match.lastindex >= 2 else ''
            return date, time
    return '', ''


def extract_status(text):
    """Извлекает статус операции"""
    # Сначала ищем явные паттерны
    status = extract_field(text, 'status')
    if status:
        return status

    # Ищем индикаторы успеха
    if re.search(r'успешно|выполнен|исполнен|✅|completed', text, re.IGNORECASE):
        return 'Исполнен'
    if re.search(r'отклонён|отклонен|declined|❌', text, re.IGNORECASE):
        return 'Отклонён'
    if re.search(r'в обработке|pending|ожидание', text, re.IGNORECASE):
        return 'В обработке'

    return ''


def extract_type(text):
    """Определяет тип операции"""
    type_val = extract_field(text, 'type')
    if type_val:
        return type_val

    # Автоопределение по содержимому
    if re.search(r'СБП|SBP|Система быстрых платежей', text, re.IGNORECASE):
        return 'Перевод по СБП'
    if re.search(r'внутрибанковский|внутренний перевод', text, re.IGNORECASE):
        return 'Внутрибанковский перевод'
    if re.search(r'международный|swift|foreign', text, re.IGNORECASE):
        return 'Международный перевод'
    if re.search(r'P2P|на карту|card to card', text, re.IGNORECASE):
        return 'Перевод на карту'

    return 'Перевод'


def clean_text_for_csv(text):
    """Очищает текст для записи в CSV"""
    if not text:
        return ''
    # Заменяем переносы строк на пробелы или специальный разделитель
    text = re.sub(r'\n+', ' | ', text)
    # Убираем множественные пробелы
    text = re.sub(r'\s+', ' ', text)
    # Убираем эмодзи для CSV (оставляем текст)
    text = re.sub(r'[📄📷🎤✅❌⚠️💰🏦📱]', '', text)
    return text.strip()


def extract_operation_from_block(block, contact_name='', contact_type='', source_file=''):
    """Извлекает полную информацию об операции из блока текста"""

    # Извлекаем все поля
    date, time = extract_datetime(block)
    amount, currency = extract_amount_with_currency(block)
    fee, fee_currency = extract_fee(block)

    operation = {
        'date': date,
        'time': time,
        'amount': amount if amount else '',
        'currency': currency,
        'fee': fee if fee is not None else '',
        'fee_currency': fee_currency,
        'sender_name': extract_field(block, 'sender_name'),
        'sender_account': extract_field(block, 'sender_account'),
        'sender_bank': extract_field(block, 'sender_bank'),
        'recipient_name': extract_field(block, 'recipient_name'),
        'recipient_account': extract_field(block, 'recipient_account'),
        'recipient_phone': extract_field(block, 'recipient_phone'),
        'recipient_bank': extract_field(block, 'recipient_bank'),
        'transaction_id': extract_field(block, 'transaction_id'),
        'sbp_id': extract_field(block, 'sbp_id'),
        'auth_code': extract_field(block, 'auth_code'),
        'status': extract_status(block),
        'type': extract_type(block),
        'reference': extract_field(block, 'reference'),
        'contact_name': contact_name,
        'contact_type': contact_type,
        'source_file': source_file,
        'raw_text': clean_text_for_csv(block),
    }

    return operation


def extract_operations_from_file(filepath):
    """Извлекает операции из одного файла чата"""
    operations = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Ошибка чтения {filepath}: {e}")
        return operations

    # Извлечение информации о контакте из имени файла
    filename = os.path.basename(filepath)
    parts = filename.replace('.md', '').split('_')
    contact_type = parts[0] if len(parts) > 0 else ""
    contact_name = parts[1] if len(parts) > 1 else ""

    # Поиск операций в PDF блоках (несколько форматов)
    pdf_patterns = [
        # Формат: 📄 **PDF: название** содержимое
        r'📄\s*\*\*(?:PDF|Документ|Чек)[^*]*\*\*[:\s]*(.*?)(?=📷|🎤|📄|###|\n\n\n|\Z)',
        # Формат: ### PDF содержимое
        r'###\s*(?:PDF|Документ|Чек)[^\n]*\n(.*?)(?=###|\n\n\n|\Z)',
        # Формат: > цитата с чеком
        r'>\s*(?:Чек|Перевод|Операция)[^\n]*\n((?:>.*\n?)+)',
        # Формат: блоки с "Сумма" и другими финансовыми полями
        r'(?:Сумма|СУММА|Amount)[:\s]*\d.*?(?:Статус|Status|Исполнен|Выполнен).*?(?=\n\n|\Z)',
    ]

    for pattern in pdf_patterns:
        blocks = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for block in blocks:
            if not block.strip():
                continue

            operation = extract_operation_from_block(
                block,
                contact_name=contact_name,
                contact_type=contact_type,
                source_file=filename
            )

            # Добавляем только если есть хотя бы дата или сумма
            if operation['date'] or operation['amount']:
                operations.append(operation)

    # Поиск упоминаний переводов в тексте сообщений
    transfer_patterns = [
        r'\[(\d{2}\.\d{2}\.\d{4})[^\]]*\].*?(?:перев[ёе]л|отправил|получил|оплатил)[^📄📷🎤\n]*?(\d{1,3}(?:[\s,]\d{3})*)\s*(RUB|руб|₽|AED|дирхам|USD|\$)',
    ]

    for pattern in transfer_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            date, amount_str, currency = match
            amount = float(amount_str.replace(' ', '').replace(',', ''))
            currency = normalize_currency(currency)

            operations.append({
                'date': date,
                'time': '',
                'amount': amount,
                'currency': currency,
                'fee': '',
                'fee_currency': '',
                'sender_name': '',
                'sender_account': '',
                'sender_bank': '',
                'recipient_name': '',
                'recipient_account': '',
                'recipient_phone': '',
                'recipient_bank': '',
                'transaction_id': '',
                'sbp_id': '',
                'auth_code': '',
                'status': '',
                'type': 'Упоминание в чате',
                'reference': '',
                'contact_name': contact_name,
                'contact_type': contact_type,
                'source_file': filename,
                'raw_text': f'Упоминание перевода {amount} {currency} в сообщении',
            })

    return operations


def build_operations_csv(chats_dir, output_file):
    """Собирает все операции в CSV"""

    all_operations = []

    # Поиск всех MD файлов
    md_files = []
    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники', '']:
        pattern = os.path.join(chats_dir, subdir, '*.md') if subdir else os.path.join(chats_dir, '*.md')
        md_files.extend(glob.glob(pattern))

    print(f"Найдено {len(md_files)} файлов чатов")

    for filepath in md_files:
        operations = extract_operations_from_file(filepath)
        all_operations.extend(operations)
        if operations:
            print(f"  {os.path.basename(filepath)}: {len(operations)} операций")

    # Удаление дубликатов (по ключевым полям)
    seen = set()
    unique_operations = []
    for op in all_operations:
        # Уникальный ключ: дата + сумма + валюта + transaction_id (или контакт если нет ID)
        key = (
            op['date'],
            str(op['amount']),
            op['currency'],
            op['transaction_id'] or op['contact_name']
        )
        if key not in seen:
            seen.add(key)
            unique_operations.append(op)

    # Сортировка по дате
    def parse_date(date_str):
        for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        return datetime.min

    unique_operations.sort(key=lambda x: parse_date(x['date']))

    # Создаём директорию если нужно
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Поля для CSV (полный набор)
    fieldnames = [
        'date', 'time', 'amount', 'currency', 'fee',
        'sender_name', 'sender_account', 'sender_bank',
        'recipient_name', 'recipient_account', 'recipient_phone', 'recipient_bank',
        'transaction_id', 'sbp_id', 'auth_code', 'status', 'type', 'reference',
        'contact_name', 'contact_type', 'source_file', 'raw_text'
    ]

    # Запись в CSV
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(unique_operations)

    # Создаём MD файл с человекочитаемым форматом
    md_output = output_file.replace('.csv', '.md')
    write_operations_md(unique_operations, md_output)

    # Статистика
    total_rub = sum(float(op['amount']) for op in unique_operations if op['currency'] == 'RUB' and op['amount'])
    total_aed = sum(float(op['amount']) for op in unique_operations if op['currency'] == 'AED' and op['amount'])
    total_usd = sum(float(op['amount']) for op in unique_operations if op['currency'] == 'USD' and op['amount'])

    print(f"\n{'='*50}")
    print(f"Всего операций: {len(unique_operations)}")
    print(f"Сумма RUB: {total_rub:,.0f} ₽")
    print(f"Сумма AED: {total_aed:,.0f} AED")
    if total_usd:
        print(f"Сумма USD: {total_usd:,.0f} $")
    print(f"{'='*50}")
    print(f"\nCSV сохранён: {output_file}")
    print(f"MD сохранён: {md_output}")


def write_operations_md(operations, output_file):
    """Создаёт MD файл с человекочитаемым форматом операций"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Финансовые операции\n\n")
        f.write(f"Всего операций: {len(operations)}\n\n")
        f.write(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        f.write("---\n\n")

        # Группируем по месяцам
        by_month = {}
        for op in operations:
            if op['date']:
                try:
                    for fmt in ['%d.%m.%Y', '%d/%m/%Y']:
                        try:
                            dt = datetime.strptime(op['date'], fmt)
                            month_key = dt.strftime('%Y-%m')
                            break
                        except:
                            continue
                    else:
                        month_key = 'Без даты'
                except:
                    month_key = 'Без даты'
            else:
                month_key = 'Без даты'

            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(op)

        # Выводим по месяцам
        for month in sorted(by_month.keys(), reverse=True):
            ops = by_month[month]
            if month != 'Без даты':
                try:
                    dt = datetime.strptime(month, '%Y-%m')
                    month_name = dt.strftime('%B %Y')
                except:
                    month_name = month
            else:
                month_name = month

            f.write(f"## {month_name} ({len(ops)} операций)\n\n")

            for i, op in enumerate(ops, 1):
                f.write(f"### Операция #{i}\n\n")

                # Основные данные
                if op['date']:
                    f.write(f"**Дата:** {op['date']}")
                    if op['time']:
                        f.write(f" {op['time']}")
                    f.write("\n")

                if op['amount']:
                    f.write(f"**Сумма:** {op['amount']} {op['currency']}\n")

                if op['fee']:
                    f.write(f"**Комиссия:** {op['fee']} {op.get('fee_currency', '')}\n")

                if op['type']:
                    f.write(f"**Тип:** {op['type']}\n")

                if op['status']:
                    f.write(f"**Статус:** {op['status']}\n")

                f.write("\n")

                # Отправитель
                if op['sender_name'] or op['sender_account'] or op['sender_bank']:
                    f.write("**Отправитель:**\n")
                    if op['sender_name']:
                        f.write(f"- Имя: {op['sender_name']}\n")
                    if op['sender_account']:
                        f.write(f"- Счёт/карта: {op['sender_account']}\n")
                    if op['sender_bank']:
                        f.write(f"- Банк: {op['sender_bank']}\n")
                    f.write("\n")

                # Получатель
                if op['recipient_name'] or op['recipient_account'] or op['recipient_phone'] or op['recipient_bank']:
                    f.write("**Получатель:**\n")
                    if op['recipient_name']:
                        f.write(f"- Имя: {op['recipient_name']}\n")
                    if op['recipient_account']:
                        f.write(f"- Счёт/карта: {op['recipient_account']}\n")
                    if op['recipient_phone']:
                        f.write(f"- Телефон: {op['recipient_phone']}\n")
                    if op['recipient_bank']:
                        f.write(f"- Банк: {op['recipient_bank']}\n")
                    f.write("\n")

                # Идентификаторы
                ids = []
                if op['transaction_id']:
                    ids.append(f"№ операции: {op['transaction_id']}")
                if op['sbp_id']:
                    ids.append(f"СБП ID: {op['sbp_id']}")
                if op['auth_code']:
                    ids.append(f"Код авторизации: {op['auth_code']}")
                if op['reference']:
                    ids.append(f"Reference: {op['reference']}")

                if ids:
                    f.write("**Идентификаторы:** " + " | ".join(ids) + "\n\n")

                # Контакт
                if op['contact_name']:
                    f.write(f"**Контакт:** {op['contact_name']} ({op['contact_type']})\n")

                if op['source_file']:
                    f.write(f"**Источник:** {op['source_file']}\n")

                # Исходный текст (в раскрывающемся блоке)
                if op['raw_text'] and len(op['raw_text']) > 50:
                    f.write("\n<details>\n<summary>Исходный текст</summary>\n\n")
                    f.write("```\n")
                    # Восстанавливаем переносы строк
                    raw = op['raw_text'].replace(' | ', '\n')
                    f.write(raw)
                    f.write("\n```\n\n</details>\n")

                f.write("\n---\n\n")

        # Итоги
        f.write("## Итого\n\n")

        total_rub = sum(float(op['amount']) for op in operations if op['currency'] == 'RUB' and op['amount'])
        total_aed = sum(float(op['amount']) for op in operations if op['currency'] == 'AED' and op['amount'])
        total_usd = sum(float(op['amount']) for op in operations if op['currency'] == 'USD' and op['amount'])

        f.write(f"- **RUB:** {total_rub:,.0f} ₽\n")
        f.write(f"- **AED:** {total_aed:,.0f} AED\n")
        if total_usd:
            f.write(f"- **USD:** {total_usd:,.0f} $\n")
        f.write(f"\nВсего операций: {len(operations)}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Извлечение финансовых операций в CSV и MD")
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")
    parser.add_argument("-o", "--output", default="D:/Downloads/Chats/_база/операции.csv")

    args = parser.parse_args()
    build_operations_csv(args.chats_dir, args.output)
