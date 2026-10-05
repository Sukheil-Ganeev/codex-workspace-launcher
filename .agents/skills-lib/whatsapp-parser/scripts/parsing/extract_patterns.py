#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение паттернов из чатов: контакты, адреса, события, связи

ВАЖНЫЙ ПРИНЦИП: Никакие данные НЕ теряются! Сохранять ВСЕ данные полностью.
"""

import sys
import os
import re
import glob
import argparse
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# Паттерны
PATTERNS = {
    'phone_ru': r'(\+7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',
    'phone_uae': r'(\+971[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4})',
    'phone_intl': r'(\+\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{2,4}[\s\-]?\d{0,4})',
    'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    'time_event': r'((?:завтра|сегодня|послезавтра|в понедельник|во вторник|в среду|в четверг|в пятницу|в субботу|в воскресенье)?\s*(?:в|на|к)?\s*\d{1,2}[:.]\d{2})',
    'date_event': r'(\d{1,2}[\./]\d{1,2}(?:[\./]\d{2,4})?)',
    'address': r'(?:адрес|address|находится|location|место|офис|дом|квартира)[:\s]+([^\n]{10,100})',
    'coordinates': r'((?:\d{1,2}\.\d+),\s*(?:\d{1,3}\.\d+))',
    'mention': r'(?:@|упомянул|говорил про|рекомендовал|знакомый|друг|коллега|партнер)\s*([А-Яа-яA-Za-z][А-Яа-яA-Za-z\s]{2,30})',
}

# Типы событий
EVENT_KEYWORDS = {
    'встреча': ['встреча', 'встретимся', 'увидимся', 'meeting', 'meet'],
    'дедлайн': ['дедлайн', 'срок', 'deadline', 'до', 'крайний срок'],
    'напоминание': ['напомни', 'не забудь', 'remind', 'reminder'],
    'звонок': ['позвони', 'созвон', 'call', 'перезвони'],
    'доставка': ['доставка', 'привезут', 'delivery', 'приедет'],
}

# Типы адресов
ADDRESS_KEYWORDS = {
    'офис': ['офис', 'office', 'работа', 'компания'],
    'дом': ['дом', 'home', 'квартира', 'жилье'],
    'место встречи': ['встретимся', 'подъезжай', 'приезжай', 'локация'],
    'ресторан': ['ресторан', 'кафе', 'restaurant', 'cafe'],
    'отель': ['отель', 'hotel', 'гостиница'],
}

# Типы связей
RELATION_KEYWORDS = {
    'рекомендация': ['рекомендую', 'советую', 'порекомендовал', 'recommend'],
    'бенефициар': ['бенефициар', 'владелец', 'owner', 'beneficiary'],
    'общий контакт': ['общий знакомый', 'через него', 'познакомил'],
    'коллега': ['коллега', 'работает', 'colleague'],
    'родственник': ['брат', 'сестра', 'муж', 'жена', 'родственник'],
}


def parse_vcf_block(vcf_text):
    """
    Парсит VCF блок и извлекает ВСЕ данные контакта.
    Возвращает словарь с полными данными.
    """
    contact_data = {
        'full_name': '',
        'phones': [],
        'emails': [],
        'organization': '',
        'address': '',
        'notes': '',
        'raw_vcf': vcf_text  # Сохраняем исходный текст VCF
    }

    lines = vcf_text.split('\n')

    for line in lines:
        line = line.strip()

        # Полное имя
        if line.startswith('FN:') or line.startswith('FN;'):
            contact_data['full_name'] = line.split(':', 1)[-1].strip()

        # Телефоны (может быть несколько)
        if line.startswith('TEL') or 'TEL;' in line:
            phone = line.split(':')[-1].strip()
            if phone and phone not in contact_data['phones']:
                contact_data['phones'].append(phone)

        # Email (может быть несколько)
        if line.startswith('EMAIL') or 'EMAIL;' in line:
            email = line.split(':')[-1].strip()
            if email and email not in contact_data['emails']:
                contact_data['emails'].append(email)

        # Организация
        if line.startswith('ORG:') or line.startswith('ORG;'):
            contact_data['organization'] = line.split(':', 1)[-1].strip()

        # Адрес
        if line.startswith('ADR') or 'ADR;' in line:
            addr = line.split(':')[-1].strip()
            # VCF адрес разделен точками с запятой
            addr_parts = [p.strip() for p in addr.split(';') if p.strip()]
            if addr_parts:
                contact_data['address'] = ', '.join(addr_parts)

        # Заметки
        if line.startswith('NOTE:') or line.startswith('NOTE;'):
            contact_data['notes'] = line.split(':', 1)[-1].strip()

    return contact_data


def extract_vcf_contacts(filepath):
    """
    Извлекает ВСЕ контакты из VCF файлов, упомянутых в чате.
    Сохраняет полные данные включая исходный VCF блок.
    """
    contacts = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return contacts

    # Ищем VCF блоки в тексте (могут быть встроены или как отдельные секции)
    vcf_pattern = r'(BEGIN:VCARD.*?END:VCARD)'
    vcf_blocks = re.findall(vcf_pattern, content, re.DOTALL | re.IGNORECASE)

    for vcf_block in vcf_blocks:
        contact_data = parse_vcf_block(vcf_block)
        if contact_data['full_name'] or contact_data['phones']:
            contacts.append(contact_data)

    return contacts


def extract_events_with_context(filepath):
    """
    Извлекает события с полным контекстом.
    Сохраняет: дата/время, контекст (2-3 строки), тип события, исходная строка.
    """
    events = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return events

    content = ''.join(lines)

    # Паттерны для дат и времени
    time_pattern = PATTERNS['time_event']
    date_pattern = PATTERNS['date_event']

    for i, line in enumerate(lines):
        # Ищем время
        time_matches = re.findall(time_pattern, line, re.IGNORECASE)
        date_matches = re.findall(date_pattern, line)

        if time_matches or date_matches:
            # Контекст: 2 строки до и 2 после
            context_start = max(0, i - 2)
            context_end = min(len(lines), i + 3)
            context = ''.join(lines[context_start:context_end]).strip()

            # Определяем тип события
            event_type = 'неизвестно'
            line_lower = line.lower()
            for etype, keywords in EVENT_KEYWORDS.items():
                if any(kw in line_lower for kw in keywords):
                    event_type = etype
                    break

            event = {
                'datetime': ', '.join(time_matches + date_matches),
                'context': context,
                'event_type': event_type,
                'original_line': line.strip(),
                'line_number': i + 1
            }
            events.append(event)

    return events


def extract_addresses_with_context(filepath):
    """
    Извлекает адреса с полным контекстом.
    Сохраняет: полный адрес, контекст, тип, координаты.
    """
    addresses = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return addresses

    content = ''.join(lines)

    # Ищем адреса
    addr_pattern = PATTERNS['address']
    coord_pattern = PATTERNS['coordinates']

    for i, line in enumerate(lines):
        addr_matches = re.findall(addr_pattern, line, re.IGNORECASE)
        coord_matches = re.findall(coord_pattern, line)

        if addr_matches or coord_matches:
            # Контекст
            context_start = max(0, i - 1)
            context_end = min(len(lines), i + 2)
            context = ''.join(lines[context_start:context_end]).strip()

            # Тип адреса
            addr_type = 'неизвестно'
            line_lower = line.lower()
            for atype, keywords in ADDRESS_KEYWORDS.items():
                if any(kw in line_lower for kw in keywords):
                    addr_type = atype
                    break

            for addr in addr_matches:
                address_data = {
                    'full_address': addr.strip(),
                    'context': context,
                    'address_type': addr_type,
                    'coordinates': coord_matches[0] if coord_matches else '',
                    'original_line': line.strip()
                }
                addresses.append(address_data)

            # Если есть только координаты без текстового адреса
            if coord_matches and not addr_matches:
                address_data = {
                    'full_address': f'Координаты: {coord_matches[0]}',
                    'context': context,
                    'address_type': addr_type,
                    'coordinates': coord_matches[0],
                    'original_line': line.strip()
                }
                addresses.append(address_data)

    return addresses


def extract_relations_with_context(filepath, contact_name, all_contacts):
    """
    Извлекает связи между контактами с полным контекстом.
    Сохраняет: кто упомянул, кого, контекст (полная цитата), тип связи.
    """
    relations = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return relations

    content_lower = ''.join(lines).lower()

    for other_contact in all_contacts:
        if other_contact.lower() == contact_name.lower():
            continue

        # Ищем упоминания в тексте
        for i, line in enumerate(lines):
            if other_contact.lower() in line.lower():
                # Контекст: полная цитата + окружение
                context_start = max(0, i - 1)
                context_end = min(len(lines), i + 2)
                context = ''.join(lines[context_start:context_end]).strip()

                # Определяем тип связи
                relation_type = 'упоминание'
                line_lower = line.lower()
                for rtype, keywords in RELATION_KEYWORDS.items():
                    if any(kw in line_lower for kw in keywords):
                        relation_type = rtype
                        break

                relation = {
                    'who_mentioned': contact_name,
                    'whom_mentioned': other_contact,
                    'context': context,
                    'relation_type': relation_type,
                    'original_line': line.strip()
                }
                relations.append(relation)

    # Также ищем по паттерну упоминаний
    mention_pattern = PATTERNS['mention']
    for i, line in enumerate(lines):
        mentions = re.findall(mention_pattern, line, re.IGNORECASE)
        for mention in mentions:
            mention = mention.strip()
            if len(mention) > 2:
                context_start = max(0, i - 1)
                context_end = min(len(lines), i + 2)
                context = ''.join(lines[context_start:context_end]).strip()

                relation_type = 'упоминание'
                line_lower = line.lower()
                for rtype, keywords in RELATION_KEYWORDS.items():
                    if any(kw in line_lower for kw in keywords):
                        relation_type = rtype
                        break

                relation = {
                    'who_mentioned': contact_name,
                    'whom_mentioned': mention,
                    'context': context,
                    'relation_type': relation_type,
                    'original_line': line.strip()
                }
                relations.append(relation)

    return relations


def extract_quick_replies_with_context(filepath):
    """
    Извлекает быстрые ответы с контекстом.
    Сохраняет: полный текст ответа, контекст (на что отвечали), частота.
    """
    replies = []
    reply_counts = defaultdict(int)
    reply_contexts = defaultdict(list)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return replies

    # Паттерн для сообщений контакта
    contact_msg_pattern = r'\*\*[👤👩][^*]+\*\*'

    for i, line in enumerate(lines):
        # Проверяем, это ли сообщение контакта
        if re.search(contact_msg_pattern, line):
            # Следующая строка - текст сообщения
            if i + 1 < len(lines):
                reply_text = lines[i + 1].strip()

                # Фильтруем короткие ответы (до 100 символов, не ссылки, не служебные)
                if (len(reply_text) > 2 and len(reply_text) < 100 and
                    not reply_text.startswith('[') and
                    not reply_text.startswith('http') and
                    not reply_text.startswith('🎤') and
                    not reply_text.startswith('📷') and
                    not reply_text.startswith('📄')):

                    reply_counts[reply_text] += 1

                    # Сохраняем контекст (предыдущее сообщение = на что отвечали)
                    if i >= 2:
                        prev_context = lines[i - 2].strip() if i >= 2 else ''
                        if prev_context and prev_context not in reply_contexts[reply_text]:
                            reply_contexts[reply_text].append(prev_context)

    # Формируем результат с полными данными
    for reply_text, count in sorted(reply_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        reply_data = {
            'text': reply_text,
            'frequency': count,
            'contexts': reply_contexts[reply_text][:3]  # До 3 примеров контекста
        }
        replies.append(reply_data)

    return replies


def extract_patterns_from_file(filepath):
    """Извлекает базовые паттерны из файла"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {}

    results = defaultdict(set)

    for pattern_name, pattern in PATTERNS.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            cleaned = match.strip()
            if len(cleaned) > 3:
                results[pattern_name].add(cleaned)

    return results


def build_patterns_database(chats_dir, output_dir):
    """Собирает все паттерны в базу с ПОЛНЫМ сохранением данных"""

    os.makedirs(output_dir, exist_ok=True)

    all_contacts_data = {}  # Полные данные контактов
    all_events = defaultdict(list)
    all_addresses = defaultdict(list)
    all_relations = []
    all_quick_replies = {}
    all_vcf_contacts = defaultdict(list)
    all_contact_names = []

    # Первый проход - собираем имена контактов
    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern = os.path.join(chats_dir, subdir, '*.md')
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)
            parts = filename.replace('.md', '').split('_')
            if len(parts) > 1:
                all_contact_names.append(parts[1])

    # Второй проход - извлекаем ВСЕ данные
    for subdir in ['клиенты', 'агенты', 'поставщики', 'сотрудники']:
        pattern_path = os.path.join(chats_dir, subdir, '*.md')
        for filepath in glob.glob(pattern_path):
            filename = os.path.basename(filepath)
            parts = filename.replace('.md', '').split('_')
            contact_key = parts[1] if len(parts) > 1 else filename.replace('.md', '')

            # Базовые паттерны (телефоны, email)
            patterns = extract_patterns_from_file(filepath)
            all_contacts_data[contact_key] = {
                'phones': list(patterns.get('phone_ru', set()) |
                              patterns.get('phone_uae', set()) |
                              patterns.get('phone_intl', set())),
                'emails': list(patterns.get('email', set())),
                'source_file': filepath
            }

            # VCF контакты
            vcf_contacts = extract_vcf_contacts(filepath)
            all_vcf_contacts[contact_key] = vcf_contacts

            # События с контекстом
            events = extract_events_with_context(filepath)
            all_events[contact_key] = events

            # Адреса с контекстом
            addresses = extract_addresses_with_context(filepath)
            all_addresses[contact_key] = addresses

            # Связи с контекстом
            other_contacts = [c for c in all_contact_names if c != contact_key]
            relations = extract_relations_with_context(filepath, contact_key, other_contacts)
            all_relations.extend(relations)

            # Быстрые ответы с контекстом
            quick_replies = extract_quick_replies_with_context(filepath)
            all_quick_replies[contact_key] = quick_replies

    # === контакты.md (ПОЛНЫЕ данные) ===
    output = []
    output.append("# Контакты")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append("")
    output.append("ВАЖНО: Сохранены ВСЕ данные без потерь, включая исходные VCF блоки.")
    output.append("")
    output.append("---")
    output.append("")

    # Сначала контакты из чатов
    for contact_key, data in sorted(all_contacts_data.items()):
        phones = data.get('phones', [])
        emails = data.get('emails', [])

        if phones or emails:
            output.append(f"## {contact_key}")
            output.append("")

            if phones:
                output.append("### Телефоны")
                for phone in phones:
                    output.append(f"- {phone}")
                output.append("")

            if emails:
                output.append("### Email")
                for email in emails:
                    output.append(f"- {email}")
                output.append("")

            output.append(f"*Источник: {data.get('source_file', '')}*")
            output.append("")
            output.append("---")
            output.append("")

    # VCF контакты с полными данными
    output.append("# Контакты из VCF")
    output.append("")

    for contact_key, vcf_list in sorted(all_vcf_contacts.items()):
        if vcf_list:
            output.append(f"## Переданы от: {contact_key}")
            output.append("")

            for vcf_data in vcf_list:
                output.append(f"### {vcf_data.get('full_name', 'Без имени')}")
                output.append("")

                if vcf_data.get('phones'):
                    output.append("**Телефоны:**")
                    for phone in vcf_data['phones']:
                        output.append(f"- {phone}")
                    output.append("")

                if vcf_data.get('emails'):
                    output.append("**Email:**")
                    for email in vcf_data['emails']:
                        output.append(f"- {email}")
                    output.append("")

                if vcf_data.get('organization'):
                    output.append(f"**Организация:** {vcf_data['organization']}")
                    output.append("")

                if vcf_data.get('address'):
                    output.append(f"**Адрес:** {vcf_data['address']}")
                    output.append("")

                if vcf_data.get('notes'):
                    output.append(f"**Заметки:** {vcf_data['notes']}")
                    output.append("")

                # Исходный VCF блок
                output.append("<details>")
                output.append("<summary>Исходный VCF</summary>")
                output.append("")
                output.append("```")
                output.append(vcf_data.get('raw_vcf', ''))
                output.append("```")
                output.append("</details>")
                output.append("")
                output.append("---")
                output.append("")

    with open(os.path.join(output_dir, 'контакты.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # === события.md (с контекстом) ===
    output = []
    output.append("# События и даты")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append("")
    output.append("Сохранены: дата/время, контекст, тип события, исходная строка.")
    output.append("")
    output.append("---")
    output.append("")

    for contact_key, events in sorted(all_events.items()):
        if events:
            output.append(f"## {contact_key}")
            output.append("")

            for event in events:
                event_type = event.get('event_type', 'неизвестно')
                datetime_str = event.get('datetime', '')

                output.append(f"### {event_type.upper()} - {datetime_str}")
                output.append("")
                output.append(f"**Исходная строка:**")
                output.append(f"> {event.get('original_line', '')}")
                output.append("")
                output.append(f"**Контекст (строки вокруг):**")
                output.append("```")
                output.append(event.get('context', ''))
                output.append("```")
                output.append("")
                output.append("---")
                output.append("")

    with open(os.path.join(output_dir, 'события.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # === адреса.md (с контекстом и координатами) ===
    output = []
    output.append("# Адреса и локации")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append("")
    output.append("Сохранены: полный адрес, контекст, тип, координаты.")
    output.append("")
    output.append("---")
    output.append("")

    for contact_key, addresses in sorted(all_addresses.items()):
        if addresses:
            output.append(f"## {contact_key}")
            output.append("")

            for addr in addresses:
                addr_type = addr.get('address_type', 'неизвестно')

                output.append(f"### {addr_type.upper()}")
                output.append("")
                output.append(f"**Полный адрес:** {addr.get('full_address', '')}")
                output.append("")

                if addr.get('coordinates'):
                    output.append(f"**Координаты:** {addr['coordinates']}")
                    output.append("")

                output.append(f"**Контекст упоминания:**")
                output.append("```")
                output.append(addr.get('context', ''))
                output.append("```")
                output.append("")
                output.append(f"**Исходная строка:**")
                output.append(f"> {addr.get('original_line', '')}")
                output.append("")
                output.append("---")
                output.append("")

    with open(os.path.join(output_dir, 'адреса.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # === связи.md (с полным контекстом) ===
    output = []
    output.append("# Связи между контактами")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append("")
    output.append("Сохранены: кто упомянул, кого, контекст (полная цитата), тип связи.")
    output.append("")

    # Граф связей
    output.append("## Граф связей")
    output.append("")
    output.append("```mermaid")
    output.append("graph LR")

    unique_links = set()
    for rel in all_relations:
        link = f"    {rel['who_mentioned']} --> {rel['whom_mentioned']}"
        if link not in unique_links:
            unique_links.add(link)
            output.append(link)

    output.append("```")
    output.append("")
    output.append("---")
    output.append("")

    # Детализация с полным контекстом
    output.append("## Детализация связей")
    output.append("")

    # Группируем по тому, кто упомянул
    relations_by_who = defaultdict(list)
    for rel in all_relations:
        relations_by_who[rel['who_mentioned']].append(rel)

    for who, relations in sorted(relations_by_who.items()):
        output.append(f"### {who}")
        output.append("")

        for rel in relations:
            output.append(f"#### Упоминает: {rel['whom_mentioned']}")
            output.append("")
            output.append(f"**Тип связи:** {rel['relation_type']}")
            output.append("")
            output.append(f"**Контекст (полная цитата):**")
            output.append("```")
            output.append(rel.get('context', ''))
            output.append("```")
            output.append("")
            output.append(f"**Исходная строка:**")
            output.append(f"> {rel.get('original_line', '')}")
            output.append("")
            output.append("---")
            output.append("")

    with open(os.path.join(output_dir, 'связи.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # === быстрые_ответы.md (с контекстом) ===
    output = []
    output.append("# Быстрые ответы контактов")
    output.append("")
    output.append(f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
    output.append("")
    output.append("Частые короткие ответы для шаблонов.")
    output.append("Сохранены: полный текст, контекст (на что отвечали), частота.")
    output.append("")
    output.append("---")
    output.append("")

    for contact_key, replies in sorted(all_quick_replies.items()):
        if replies:
            output.append(f"## {contact_key}")
            output.append("")

            for reply in replies:
                output.append(f"### \"{reply['text']}\"")
                output.append("")
                output.append(f"**Частота использования:** {reply['frequency']} раз")
                output.append("")

                if reply.get('contexts'):
                    output.append("**На что отвечали (примеры контекста):**")
                    for ctx in reply['contexts']:
                        output.append(f"> {ctx}")
                    output.append("")

                output.append("---")
                output.append("")

    with open(os.path.join(output_dir, 'быстрые_ответы.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"База паттернов сохранена в: {output_dir}")
    print(f"  - контакты.md (включая VCF с исходными блоками)")
    print(f"  - события.md (с контекстом и типами)")
    print(f"  - адреса.md (с координатами и типами)")
    print(f"  - связи.md (с полными цитатами)")
    print(f"  - быстрые_ответы.md (с контекстом)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Извлечение паттернов с ПОЛНЫМ сохранением данных")
    parser.add_argument("--chats-dir", default="D:/Downloads/Chats", help="Папка с чатами")
    parser.add_argument("-o", "--output-dir", default="D:/Downloads/Chats/_база")

    args = parser.parse_args()
    build_patterns_database(args.chats_dir, args.output_dir)
