#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение банковских реквизитов из чатов в единую базу.

ВАЖНО: Никакие данные НЕ теряются!
Все реквизиты сохраняются ПОЛНОСТЬЮ как в исходном чате.
"""

import sys
import os
import re
import glob
import argparse
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')


def extract_full_requisite_blocks(content):
    """
    Извлекает ПОЛНЫЕ блоки банковских реквизитов.
    НЕ теряет никакую информацию — сохраняет блоки целиком.
    """
    blocks = []

    # === Паттерн 1: Международные реквизиты (BANK, IBAN, NAME, SWIFT, Account) ===
    # Ищем блоки которые содержат несколько строк с реквизитами подряд
    intl_pattern = r'''
        (?:^|\n)                                    # Начало строки
        (?P<block>
            (?:.*?(?:BANK|Bank|Банк)[:\s]*[^\n]+\n)?           # Bank name (опционально)
            (?:.*?(?:Account\s*(?:Holder\s*)?Name|NAME|Name|Имя|Получатель)[:\s]*[^\n]+\n)?  # Account holder
            (?:.*?(?:Account\s*Number|ACCOUNT|Номер\s*счёта)[:\s]*[^\n]+\n)?   # Account number
            (?:.*?(?:IBAN|IBAN\s*Number|IBAN\s*NUMBER)[:\s]*[^\n]+\n)?         # IBAN
            (?:.*?(?:SWIFT|BIC)[:\s]*[^\n]+\n)?               # SWIFT
            (?:.*?(?:Correspondent|Корр)[^\n]*\n)?            # Correspondent account
        )
    '''

    # === Паттерн 2: Форматированные блоки из WhatsApp (с * и :) ===
    # Пример: 💳 BANK : *ADIB BANK*
    wa_block_pattern = r'''
        (
            (?:💳\s*)?                                  # Эмодзи (опционально)
            (?:BANK|Bank)[:\s]*\*?[^*\n]+\*?\s*\n      # Bank name
            (?:[^\n]*(?:ACCOUNT|Account|NAME|Name|IBAN|SWIFT|BIC)[:\s]*\*?[^*\n]+\*?\s*\n)+  # Остальные поля
        )
    '''

    # Поиск блоков формата WhatsApp
    matches = re.findall(wa_block_pattern, content, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    for match in matches:
        if match.strip():
            blocks.append({
                'type': 'international',
                'raw': match.strip(),
                'parsed': parse_requisite_block(match)
            })

    # === Паттерн 3: Российские реквизиты (БИК, ИНН, КПП, Счёт) ===
    ru_pattern = r'''
        (
            (?:Получатель|Recipient)[:\s]*[^\n]+\n
            (?:[^\n]*(?:Account|Счёт|БИК|BIK|ИНН|INN|КПП|KPP|Банк|Bank)[:\s]*[^\n]+\n)+
        )
    '''

    matches = re.findall(ru_pattern, content, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    for match in matches:
        if match.strip():
            blocks.append({
                'type': 'russian',
                'raw': match.strip(),
                'parsed': parse_requisite_block(match)
            })

    # === Паттерн 4: Отдельные IBAN с контекстом ===
    # Берём 2 строки до и после IBAN для сохранения контекста
    iban_pattern = r'((?:[^\n]*\n){0,2}[^\n]*(?:IBAN|AE\d{21})[^\n]*(?:\n[^\n]*){0,2})'
    matches = re.findall(iban_pattern, content, re.IGNORECASE)
    for match in matches:
        if match.strip() and 'AE' in match.upper():
            # Проверяем что этот блок ещё не добавлен
            already_exists = any(match.strip() in b['raw'] for b in blocks)
            if not already_exists:
                blocks.append({
                    'type': 'iban_context',
                    'raw': match.strip(),
                    'parsed': parse_requisite_block(match)
                })

    # === Паттерн 5: Российские телефоны для переводов (СБП) ===
    # +7 XXX XXX-XX-XX с контекстом
    phone_pattern = r'((?:[^\n]*\n){0,1}[^\n]*\+7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}[^\n]*(?:\n[^\n]*){0,1})'
    matches = re.findall(phone_pattern, content)
    for match in matches:
        # Только если это похоже на реквизиты (есть слова "перевод", "сбер", "втб" и т.д.)
        if any(word in match.lower() for word in ['сбер', 'втб', 'тиньк', 'альфа', 'перевод', 'карт', 'счёт', 'счет']):
            already_exists = any(match.strip() in b['raw'] for b in blocks)
            if not already_exists:
                blocks.append({
                    'type': 'russian_phone',
                    'raw': match.strip(),
                    'parsed': parse_requisite_block(match)
                })

    return blocks


def parse_requisite_block(text):
    """
    Парсит блок реквизитов и извлекает структурированные поля.
    Сохраняет ВСЕ найденные данные.
    """
    parsed = {}

    # Очистка от markdown форматирования
    clean_text = re.sub(r'\*+', '', text)

    # Bank name
    match = re.search(r'(?:BANK|Bank|Банк)[:\s]*([^\n]+)', clean_text, re.IGNORECASE)
    if match:
        parsed['bank'] = match.group(1).strip()

    # Account holder name
    match = re.search(r'(?:Account\s*Holder\s*Name|NAME|Name|Имя|Получатель|Recipient)[:\s]*([^\n]+)', clean_text, re.IGNORECASE)
    if match:
        parsed['holder'] = match.group(1).strip()

    # Account number
    match = re.search(r'(?:Account\s*Number|ACCOUNT\s*NUMBER|Номер\s*счёта)[:\s]*([^\n]+)', clean_text, re.IGNORECASE)
    if match:
        parsed['account'] = match.group(1).strip()

    # IBAN
    match = re.search(r'(?:IBAN(?:\s*Number)?)[:\s]*([A-Z]{2}\d{2}[A-Z0-9]+)', clean_text, re.IGNORECASE)
    if match:
        parsed['iban'] = match.group(1).strip()
    else:
        # Попробуем найти просто IBAN формат
        match = re.search(r'\b(AE\d{21})\b', clean_text)
        if match:
            parsed['iban'] = match.group(1)

    # SWIFT/BIC
    match = re.search(r'(?:SWIFT|BIC)[:\s]*([A-Z]{6}[A-Z0-9]{2,5})', clean_text, re.IGNORECASE)
    if match:
        parsed['swift'] = match.group(1).strip()

    # БИК (Россия)
    match = re.search(r'БИК[:\s]*(\d{9})', clean_text, re.IGNORECASE)
    if match:
        parsed['bik'] = match.group(1)

    # ИНН
    match = re.search(r'ИНН[:\s]*(\d{10,12})', clean_text, re.IGNORECASE)
    if match:
        parsed['inn'] = match.group(1)

    # КПП
    match = re.search(r'КПП[:\s]*(\d{9})', clean_text, re.IGNORECASE)
    if match:
        parsed['kpp'] = match.group(1)

    # Корр. счёт
    match = re.search(r'(?:Корр|Correspondent)[^\d]*(\d{20})', clean_text, re.IGNORECASE)
    if match:
        parsed['corr_account'] = match.group(1)

    # Телефон
    match = re.search(r'(\+7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})', clean_text)
    if match:
        parsed['phone'] = match.group(1)

    # Российский счёт (20 цифр, начинается с 408)
    match = re.search(r'\b(408\d{17})\b', clean_text)
    if match:
        parsed['ru_account'] = match.group(1)

    return parsed


def extract_from_file(filepath):
    """Извлекает все реквизиты из файла чата"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Ошибка чтения {filepath}: {e}")
        return []

    # Извлекаем информацию о контакте из имени файла
    filename = os.path.basename(filepath)
    parts = filename.replace('.md', '').split('_')

    contact_info = {
        'type': parts[0] if len(parts) > 0 else "неизвестно",
        'name': parts[1] if len(parts) > 1 else "неизвестно",
        'topic': parts[2] if len(parts) > 2 else "",
        'file': filename
    }

    # Извлекаем блоки реквизитов
    blocks = extract_full_requisite_blocks(content)

    # Добавляем информацию о контакте к каждому блоку
    for block in blocks:
        block['contact'] = contact_info

    return blocks


def build_requisites_database(chats_dir, output_file):
    """
    Собирает ВСЕ реквизиты в единую базу.
    НИЧЕГО НЕ ТЕРЯЕТСЯ — все данные сохраняются полностью.
    """

    all_blocks = []

    # Поиск всех MD файлов
    md_files = []
    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern = os.path.join(chats_dir, subdir, '*.md')
        md_files.extend(glob.glob(pattern))

    print(f"Найдено {len(md_files)} файлов чатов")

    for filepath in md_files:
        blocks = extract_from_file(filepath)
        if blocks:
            print(f"  {os.path.basename(filepath)}: {len(blocks)} блоков реквизитов")
        all_blocks.extend(blocks)

    print(f"\nВсего найдено {len(all_blocks)} блоков реквизитов")

    # === Генерация MD файла ===
    output = []
    output.append("# 🏦 База банковских реквизитов")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append(f"*Источник: {len(md_files)} файлов чатов*")
    output.append(f"*Всего блоков реквизитов: {len(all_blocks)}*")
    output.append("")
    output.append("> ⚠️ **ВАЖНО:** Все реквизиты сохранены ПОЛНОСТЬЮ без потери данных.")
    output.append("> Оригинальный текст сохранён в блоках \"Исходный текст\".")
    output.append("")
    output.append("---")
    output.append("")

    # Группировка по владельцам счетов (holder)
    by_holder = defaultdict(list)
    without_holder = []

    for block in all_blocks:
        holder = block['parsed'].get('holder', '')
        if holder:
            by_holder[holder].append(block)
        else:
            without_holder.append(block)

    # === Раздел 1: По владельцам счетов ===
    output.append("## 👤 По владельцам счетов")
    output.append("")

    for holder, blocks in sorted(by_holder.items()):
        output.append(f"### {holder}")
        output.append("")

        for i, block in enumerate(blocks, 1):
            parsed = block['parsed']
            contact = block['contact']

            # Структурированные данные
            if parsed.get('bank'):
                output.append(f"**Банк:** {parsed['bank']}")
            if parsed.get('account'):
                output.append(f"**Account Number:** {parsed['account']}")
            if parsed.get('iban'):
                output.append(f"**IBAN:** {parsed['iban']}")
            if parsed.get('swift'):
                output.append(f"**SWIFT/BIC:** {parsed['swift']}")
            if parsed.get('bik'):
                output.append(f"**БИК:** {parsed['bik']}")
            if parsed.get('inn'):
                output.append(f"**ИНН:** {parsed['inn']}")
            if parsed.get('kpp'):
                output.append(f"**КПП:** {parsed['kpp']}")
            if parsed.get('corr_account'):
                output.append(f"**Корр. счёт:** {parsed['corr_account']}")
            if parsed.get('ru_account'):
                output.append(f"**Счёт РФ:** {parsed['ru_account']}")
            if parsed.get('phone'):
                output.append(f"**Телефон:** {parsed['phone']}")

            output.append("")
            output.append(f"*Источник: {contact['name']} ({contact['type']}, {contact['topic']})*")
            output.append("")

            # Исходный текст — ПОЛНОСТЬЮ
            output.append("<details>")
            output.append("<summary>📋 Исходный текст (полностью)</summary>")
            output.append("")
            output.append("```")
            output.append(block['raw'])
            output.append("```")
            output.append("</details>")
            output.append("")

        output.append("---")
        output.append("")

    # === Раздел 2: Реквизиты без явного владельца ===
    if without_holder:
        output.append("## 📱 Прочие реквизиты")
        output.append("")

        # Группируем по контакту
        by_contact = defaultdict(list)
        for block in without_holder:
            contact_key = f"{block['contact']['name']} ({block['contact']['type']})"
            by_contact[contact_key].append(block)

        for contact_key, blocks in sorted(by_contact.items()):
            output.append(f"### {contact_key}")
            output.append("")

            for block in blocks:
                parsed = block['parsed']

                # Все найденные поля
                for key, value in parsed.items():
                    if value:
                        key_display = {
                            'bank': 'Банк',
                            'account': 'Account Number',
                            'iban': 'IBAN',
                            'swift': 'SWIFT/BIC',
                            'bik': 'БИК',
                            'inn': 'ИНН',
                            'kpp': 'КПП',
                            'corr_account': 'Корр. счёт',
                            'ru_account': 'Счёт РФ',
                            'phone': 'Телефон',
                            'holder': 'Владелец'
                        }.get(key, key)
                        output.append(f"- **{key_display}:** {value}")

                output.append("")

                # Исходный текст
                output.append("<details>")
                output.append("<summary>📋 Исходный текст</summary>")
                output.append("")
                output.append("```")
                output.append(block['raw'])
                output.append("```")
                output.append("</details>")
                output.append("")

            output.append("---")
            output.append("")

    # === Раздел 3: Быстрый справочник ===
    output.append("## 📋 Быстрый справочник")
    output.append("")
    output.append("| Владелец | Банк | IBAN/Счёт | Контакт |")
    output.append("|----------|------|-----------|---------|")

    for block in all_blocks:
        parsed = block['parsed']
        contact = block['contact']

        holder = parsed.get('holder', '-')
        bank = parsed.get('bank', '-')
        account = parsed.get('iban') or parsed.get('account') or parsed.get('ru_account') or parsed.get('phone') or '-'
        contact_str = f"{contact['name']}"

        # Сокращаем длинные значения для таблицы
        if len(account) > 30:
            account = account[:27] + '...'

        output.append(f"| {holder} | {bank} | {account} | {contact_str} |")

    output.append("")

    # Сохранение
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n✅ База реквизитов сохранена: {output_file}")
    print(f"   Владельцев счетов: {len(by_holder)}")
    print(f"   Прочих блоков: {len(without_holder)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Извлечение банковских реквизитов из чатов. НИЧЕГО НЕ ТЕРЯЕТСЯ!"
    )
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")
    parser.add_argument("-o", "--output", default="D:/Downloads/Chats/_база/реквизиты.md")

    args = parser.parse_args()
    build_requisites_database(args.chats_dir, args.output)
