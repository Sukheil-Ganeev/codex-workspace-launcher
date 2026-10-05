#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенный парсер VCF (vCard) контактов

Функции:
- Полный парсинг всех стандартных полей VCF (FN, N, TEL, EMAIL, ORG, TITLE, ADR, BDAY, NOTE)
- Извлечение фото контактов (base64 -> файлы)
- Парсинг нестандартных полей (X-WHATSAPP, X-TELEGRAM и т.д.)
- Поддержка множественных номеров и email
- Связь контактов с чатами WhatsApp
- Обогащение профилей данными из чатов
- Экспорт в JSON и CSV

Автор: Claude AI
Версия: 2.0
"""

import sys
import os
import glob
import re
import json
import csv
import base64
import hashlib
import argparse
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class PhoneNumber:
    """Телефонный номер с типом и нормализованной формой"""
    raw: str
    normalized: str
    type: str = "OTHER"  # HOME, WORK, CELL, FAX, PAGER, OTHER
    is_preferred: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EmailAddress:
    """Email адрес с типом"""
    address: str
    type: str = "OTHER"  # HOME, WORK, OTHER
    is_preferred: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Address:
    """Почтовый адрес"""
    po_box: str = ""
    extended: str = ""
    street: str = ""
    city: str = ""
    region: str = ""
    postal_code: str = ""
    country: str = ""
    type: str = "OTHER"  # HOME, WORK, OTHER
    formatted: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VCardContact:
    """Полная информация о контакте из VCF"""
    # Идентификаторы
    uid: str = ""
    source_file: str = ""

    # Имена
    full_name: str = ""  # FN
    family_name: str = ""  # N: фамилия
    given_name: str = ""  # N: имя
    middle_name: str = ""  # N: отчество
    prefix: str = ""  # N: префикс (Mr., Dr.)
    suffix: str = ""  # N: суффикс (Jr., PhD)
    nickname: str = ""

    # Контакты
    phones: List[PhoneNumber] = field(default_factory=list)
    emails: List[EmailAddress] = field(default_factory=list)

    # Организация
    organization: str = ""
    department: str = ""
    title: str = ""  # Должность
    role: str = ""  # Роль

    # Адреса
    addresses: List[Address] = field(default_factory=list)

    # Даты
    birthday: str = ""
    anniversary: str = ""

    # Заметки и фото
    note: str = ""
    photo_base64: str = ""
    photo_type: str = ""  # JPEG, PNG, GIF
    photo_file: str = ""  # Путь к извлеченному фото

    # URL и социальные сети
    url: str = ""
    social_profiles: Dict[str, str] = field(default_factory=dict)  # X-TWITTER, X-WHATSAPP и т.д.

    # Нестандартные поля
    custom_fields: Dict[str, str] = field(default_factory=dict)

    # Связь с чатами WhatsApp
    whatsapp_chat_folder: str = ""
    chat_statistics: Dict[str, Any] = field(default_factory=dict)

    # Метаданные
    version: str = ""
    rev: str = ""  # Дата последнего изменения
    categories: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Конвертация в словарь для JSON"""
        result = {
            "uid": self.uid,
            "source_file": self.source_file,
            "full_name": self.full_name,
            "family_name": self.family_name,
            "given_name": self.given_name,
            "middle_name": self.middle_name,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "nickname": self.nickname,
            "phones": [p.to_dict() for p in self.phones],
            "emails": [e.to_dict() for e in self.emails],
            "organization": self.organization,
            "department": self.department,
            "title": self.title,
            "role": self.role,
            "addresses": [a.to_dict() for a in self.addresses],
            "birthday": self.birthday,
            "anniversary": self.anniversary,
            "note": self.note,
            "photo_file": self.photo_file,
            "url": self.url,
            "social_profiles": self.social_profiles,
            "custom_fields": self.custom_fields,
            "whatsapp_chat_folder": self.whatsapp_chat_folder,
            "chat_statistics": self.chat_statistics,
            "version": self.version,
            "rev": self.rev,
            "categories": self.categories
        }
        return result

    def to_csv_row(self) -> dict:
        """Конвертация в плоский формат для CSV"""
        phones_str = "; ".join([f"{p.type}: {p.raw}" for p in self.phones])
        emails_str = "; ".join([f"{e.type}: {e.address}" for e in self.emails])
        addresses_str = "; ".join([a.formatted for a in self.addresses if a.formatted])

        return {
            "full_name": self.full_name,
            "family_name": self.family_name,
            "given_name": self.given_name,
            "middle_name": self.middle_name,
            "phones": phones_str,
            "primary_phone": self.phones[0].raw if self.phones else "",
            "emails": emails_str,
            "primary_email": self.emails[0].address if self.emails else "",
            "organization": self.organization,
            "title": self.title,
            "addresses": addresses_str,
            "birthday": self.birthday,
            "note": self.note,
            "url": self.url,
            "whatsapp_chat_folder": self.whatsapp_chat_folder,
            "has_photo": "Yes" if self.photo_file else "No",
            "source_file": self.source_file
        }


def normalize_phone(phone: str) -> str:
    """Нормализация номера телефона: только цифры, начиная с +"""
    # Убираем все кроме цифр и +
    digits = re.sub(r'[^\d+]', '', phone)

    # Если начинается с 8 и длина 11 - это Россия, меняем на +7
    if digits.startswith('8') and len(digits) == 11:
        digits = '+7' + digits[1:]

    # Добавляем + если нет
    if not digits.startswith('+') and len(digits) >= 10:
        # Проверяем код страны
        if digits.startswith('7') and len(digits) == 11:
            digits = '+' + digits
        elif digits.startswith('971') and len(digits) >= 12:  # ОАЭ
            digits = '+' + digits
        elif digits.startswith('1') and len(digits) == 11:  # США/Канада
            digits = '+' + digits
        else:
            digits = '+' + digits

    return digits


def parse_phone_type(type_str: str) -> Tuple[str, bool]:
    """Парсинг типа телефона из VCF"""
    type_str = type_str.upper()
    is_preferred = 'PREF' in type_str

    if 'CELL' in type_str or 'MOBILE' in type_str:
        return 'CELL', is_preferred
    elif 'HOME' in type_str:
        return 'HOME', is_preferred
    elif 'WORK' in type_str:
        return 'WORK', is_preferred
    elif 'FAX' in type_str:
        return 'FAX', is_preferred
    elif 'PAGER' in type_str:
        return 'PAGER', is_preferred
    else:
        return 'OTHER', is_preferred


def parse_email_type(type_str: str) -> Tuple[str, bool]:
    """Парсинг типа email из VCF"""
    type_str = type_str.upper()
    is_preferred = 'PREF' in type_str

    if 'HOME' in type_str:
        return 'HOME', is_preferred
    elif 'WORK' in type_str:
        return 'WORK', is_preferred
    else:
        return 'OTHER', is_preferred


def parse_address_type(type_str: str) -> str:
    """Парсинг типа адреса"""
    type_str = type_str.upper()
    if 'HOME' in type_str:
        return 'HOME'
    elif 'WORK' in type_str:
        return 'WORK'
    return 'OTHER'


def decode_quoted_printable(text: str) -> str:
    """Декодирование QUOTED-PRINTABLE"""
    try:
        # Убираем мягкие переносы строк
        text = text.replace('=\n', '').replace('=\r\n', '')
        # Декодируем =XX последовательности
        result = re.sub(
            r'=([0-9A-Fa-f]{2})',
            lambda m: chr(int(m.group(1), 16)),
            text
        )
        return result
    except Exception:
        return text


def unfold_vcard(content: str) -> str:
    """Разворачивание многострочных значений VCF (unfolding)"""
    # VCF использует пробел или таб в начале строки для продолжения
    content = re.sub(r'\r?\n[ \t]', '', content)
    return content


def parse_vcard_block(vcard_text: str, source_file: str) -> VCardContact:
    """Парсинг одного блока vCard"""
    contact = VCardContact(source_file=source_file)

    # Разворачиваем многострочные значения
    vcard_text = unfold_vcard(vcard_text)

    lines = vcard_text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('BEGIN:') or line.startswith('END:'):
            continue

        # Разделяем на имя поля и значение
        if ':' not in line:
            continue

        # Парсим имя поля с параметрами
        field_part, value = line.split(':', 1)

        # Разделяем имя поля и параметры
        field_parts = field_part.split(';')
        field_name = field_parts[0].upper()
        params = ';'.join(field_parts[1:]) if len(field_parts) > 1 else ''

        # Проверяем кодировку
        if 'ENCODING=QUOTED-PRINTABLE' in params.upper():
            value = decode_quoted_printable(value)
        elif 'CHARSET=UTF-8' in params.upper() or 'ENCODING=BASE64' in params.upper():
            pass  # Обрабатываем отдельно для PHOTO

        # Обработка полей
        if field_name == 'VERSION':
            contact.version = value.strip()

        elif field_name == 'UID':
            contact.uid = value.strip()

        elif field_name == 'FN':
            contact.full_name = value.strip()

        elif field_name == 'N':
            # N:Фамилия;Имя;Отчество;Префикс;Суффикс
            parts = value.split(';')
            if len(parts) >= 1:
                contact.family_name = parts[0].strip()
            if len(parts) >= 2:
                contact.given_name = parts[1].strip()
            if len(parts) >= 3:
                contact.middle_name = parts[2].strip()
            if len(parts) >= 4:
                contact.prefix = parts[3].strip()
            if len(parts) >= 5:
                contact.suffix = parts[4].strip()

        elif field_name == 'NICKNAME':
            contact.nickname = value.strip()

        elif field_name == 'TEL':
            phone_type, is_preferred = parse_phone_type(params)
            raw_phone = value.strip()
            normalized = normalize_phone(raw_phone)
            contact.phones.append(PhoneNumber(
                raw=raw_phone,
                normalized=normalized,
                type=phone_type,
                is_preferred=is_preferred
            ))

        elif field_name == 'EMAIL':
            email_type, is_preferred = parse_email_type(params)
            contact.emails.append(EmailAddress(
                address=value.strip(),
                type=email_type,
                is_preferred=is_preferred
            ))

        elif field_name == 'ORG':
            # ORG:Компания;Отдел
            parts = value.split(';')
            contact.organization = parts[0].strip() if parts else ''
            if len(parts) > 1:
                contact.department = parts[1].strip()

        elif field_name == 'TITLE':
            contact.title = value.strip()

        elif field_name == 'ROLE':
            contact.role = value.strip()

        elif field_name == 'ADR':
            # ADR:;;Улица;Город;Регион;Индекс;Страна
            addr_type = parse_address_type(params)
            parts = value.split(';')

            addr = Address(type=addr_type)
            if len(parts) >= 1:
                addr.po_box = parts[0].strip()
            if len(parts) >= 2:
                addr.extended = parts[1].strip()
            if len(parts) >= 3:
                addr.street = parts[2].strip()
            if len(parts) >= 4:
                addr.city = parts[3].strip()
            if len(parts) >= 5:
                addr.region = parts[4].strip()
            if len(parts) >= 6:
                addr.postal_code = parts[5].strip()
            if len(parts) >= 7:
                addr.country = parts[6].strip()

            # Формируем читаемый адрес
            addr_parts = [p for p in [addr.street, addr.city, addr.region, addr.postal_code, addr.country] if p]
            addr.formatted = ', '.join(addr_parts)

            if addr.formatted:
                contact.addresses.append(addr)

        elif field_name == 'BDAY':
            contact.birthday = value.strip()

        elif field_name == 'ANNIVERSARY':
            contact.anniversary = value.strip()

        elif field_name == 'NOTE':
            contact.note = value.strip()

        elif field_name == 'PHOTO':
            # Определяем тип фото
            if 'TYPE=JPEG' in params.upper() or 'TYPE=JPG' in params.upper():
                contact.photo_type = 'JPEG'
            elif 'TYPE=PNG' in params.upper():
                contact.photo_type = 'PNG'
            elif 'TYPE=GIF' in params.upper():
                contact.photo_type = 'GIF'
            else:
                contact.photo_type = 'JPEG'  # По умолчанию

            # Сохраняем base64 данные
            if 'ENCODING=BASE64' in params.upper() or 'ENCODING=B' in params.upper():
                contact.photo_base64 = value.strip()
            elif value.startswith('data:'):
                # data:image/jpeg;base64,/9j/...
                match = re.match(r'data:image/(\w+);base64,(.+)', value)
                if match:
                    contact.photo_type = match.group(1).upper()
                    contact.photo_base64 = match.group(2)
            else:
                contact.photo_base64 = value.strip()

        elif field_name == 'URL':
            contact.url = value.strip()

        elif field_name == 'REV':
            contact.rev = value.strip()

        elif field_name == 'CATEGORIES':
            contact.categories = [c.strip() for c in value.split(',')]

        elif field_name.startswith('X-'):
            # Нестандартные поля
            x_name = field_name[2:]  # Убираем X-

            # Социальные сети
            social_keywords = ['TWITTER', 'FACEBOOK', 'INSTAGRAM', 'LINKEDIN',
                             'WHATSAPP', 'TELEGRAM', 'SKYPE', 'VIBER', 'WECHAT']

            is_social = False
            for social in social_keywords:
                if social in x_name.upper():
                    contact.social_profiles[social] = value.strip()
                    is_social = True
                    break

            if not is_social:
                contact.custom_fields[x_name] = value.strip()

    # Генерируем UID если нет
    if not contact.uid:
        contact.uid = hashlib.md5(
            (contact.full_name + str(contact.phones)).encode()
        ).hexdigest()[:16]

    return contact


def parse_vcf_file(filepath: str) -> List[VCardContact]:
    """Парсинг VCF файла (может содержать несколько vCard)"""
    contacts = []
    filename = os.path.basename(filepath)

    # Пробуем разные кодировки
    content = None
    for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        print(f"  [ОШИБКА] Не удалось прочитать: {filename}")
        return []

    # Разбиваем на отдельные vCard блоки
    vcard_pattern = r'BEGIN:VCARD(.*?)END:VCARD'
    matches = re.findall(vcard_pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        try:
            contact = parse_vcard_block(match, filename)
            contacts.append(contact)
        except Exception as e:
            print(f"  [ОШИБКА] Парсинг контакта в {filename}: {e}")

    return contacts


def extract_photos(contacts: List[VCardContact], output_dir: str) -> int:
    """Извлечение фото контактов в файлы"""
    photos_dir = os.path.join(output_dir, 'photos')
    os.makedirs(photos_dir, exist_ok=True)

    extracted = 0

    for contact in contacts:
        if not contact.photo_base64:
            continue

        try:
            # Декодируем base64
            photo_data = base64.b64decode(contact.photo_base64)

            # Определяем расширение
            ext_map = {'JPEG': '.jpg', 'JPG': '.jpg', 'PNG': '.png', 'GIF': '.gif'}
            ext = ext_map.get(contact.photo_type, '.jpg')

            # Генерируем имя файла
            safe_name = re.sub(r'[^\w\s-]', '', contact.full_name)[:50]
            safe_name = safe_name.strip().replace(' ', '_')
            if not safe_name:
                safe_name = contact.uid

            filename = f"{safe_name}{ext}"
            filepath = os.path.join(photos_dir, filename)

            # Если файл существует, добавляем номер
            counter = 1
            while os.path.exists(filepath):
                filename = f"{safe_name}_{counter}{ext}"
                filepath = os.path.join(photos_dir, filename)
                counter += 1

            # Сохраняем
            with open(filepath, 'wb') as f:
                f.write(photo_data)

            contact.photo_file = filepath
            extracted += 1

        except Exception as e:
            print(f"  [ОШИБКА] Извлечение фото для {contact.full_name}: {e}")

    return extracted


def find_whatsapp_chats(contacts: List[VCardContact], chats_dir: str) -> int:
    """Связывание контактов с папками чатов WhatsApp"""
    if not os.path.isdir(chats_dir):
        return 0

    linked = 0

    # Получаем список папок чатов
    chat_folders = [d for d in os.listdir(chats_dir)
                   if os.path.isdir(os.path.join(chats_dir, d))]

    for contact in contacts:
        for phone in contact.phones:
            # Ищем папку с номером телефона
            normalized = phone.normalized.replace('+', '')

            for folder in chat_folders:
                # Папка может называться: +79001234567, 79001234567, WhatsApp Chat +79001234567
                folder_digits = re.sub(r'\D', '', folder)

                if folder_digits and folder_digits in normalized or normalized in folder_digits:
                    contact.whatsapp_chat_folder = os.path.join(chats_dir, folder)
                    linked += 1
                    break

            if contact.whatsapp_chat_folder:
                break

    return linked


def enrich_from_chats(contacts: List[VCardContact]) -> int:
    """Обогащение профилей данными из связанных чатов"""
    enriched = 0

    for contact in contacts:
        if not contact.whatsapp_chat_folder:
            continue

        chat_folder = contact.whatsapp_chat_folder

        # Ищем файл чата
        chat_files = glob.glob(os.path.join(chat_folder, '*.txt'))

        if not chat_files:
            continue

        stats = {
            'messages_count': 0,
            'media_count': 0,
            'first_message_date': None,
            'last_message_date': None
        }

        for chat_file in chat_files:
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Считаем сообщения
                # Формат: DD.MM.YYYY, HH:MM - Author: Message
                date_pattern = r'(\d{1,2}\.\d{1,2}\.\d{4}), \d{1,2}:\d{2}'
                dates = re.findall(date_pattern, content)

                stats['messages_count'] += len(dates)

                if dates:
                    # Парсим даты
                    try:
                        first = datetime.strptime(dates[0], '%d.%m.%Y')
                        last = datetime.strptime(dates[-1], '%d.%m.%Y')

                        if stats['first_message_date'] is None:
                            stats['first_message_date'] = first.isoformat()
                        if stats['last_message_date'] is None or last > datetime.fromisoformat(stats['last_message_date']):
                            stats['last_message_date'] = last.isoformat()
                    except:
                        pass

                # Считаем медиа
                media_pattern = r'<Медиа|<Media|прикреплено|attached'
                stats['media_count'] += len(re.findall(media_pattern, content, re.IGNORECASE))

            except Exception:
                pass

        if stats['messages_count'] > 0:
            contact.chat_statistics = stats
            enriched += 1

    return enriched


def export_to_json(contacts: List[VCardContact], output_file: str):
    """Экспорт в JSON"""
    data = {
        'exported_at': datetime.now().isoformat(),
        'total_contacts': len(contacts),
        'contacts': [c.to_dict() for c in contacts]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSON сохранен: {output_file}")


def export_to_csv(contacts: List[VCardContact], output_file: str):
    """Экспорт в CSV"""
    if not contacts:
        return

    fieldnames = [
        'full_name', 'family_name', 'given_name', 'middle_name',
        'phones', 'primary_phone', 'emails', 'primary_email',
        'organization', 'title', 'addresses', 'birthday', 'note',
        'url', 'whatsapp_chat_folder', 'has_photo', 'source_file'
    ]

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for contact in contacts:
            writer.writerow(contact.to_csv_row())

    print(f"CSV сохранен: {output_file}")


def export_to_text(contacts: List[VCardContact], output_file: str):
    """Экспорт в текстовый формат (совместимость со старым скриптом)"""
    lines = []

    for contact in contacts:
        lines.append(f"{'='*60}")
        lines.append(f"Контакт: {contact.full_name}")
        lines.append(f"{'='*60}")

        if contact.family_name or contact.given_name:
            lines.append(f"  Имя: {contact.given_name} {contact.middle_name} {contact.family_name}".strip())

        if contact.nickname:
            lines.append(f"  Никнейм: {contact.nickname}")

        if contact.phones:
            lines.append(f"  Телефоны ({len(contact.phones)}):")
            for phone in contact.phones:
                pref = " [основной]" if phone.is_preferred else ""
                lines.append(f"    - {phone.type}: {phone.raw}{pref}")
                if phone.normalized != phone.raw:
                    lines.append(f"      (нормализован: {phone.normalized})")

        if contact.emails:
            lines.append(f"  Email ({len(contact.emails)}):")
            for email in contact.emails:
                pref = " [основной]" if email.is_preferred else ""
                lines.append(f"    - {email.type}: {email.address}{pref}")

        if contact.organization:
            lines.append(f"  Организация: {contact.organization}")
            if contact.department:
                lines.append(f"    Отдел: {contact.department}")

        if contact.title:
            lines.append(f"  Должность: {contact.title}")

        if contact.addresses:
            lines.append(f"  Адреса ({len(contact.addresses)}):")
            for addr in contact.addresses:
                lines.append(f"    - {addr.type}: {addr.formatted}")

        if contact.birthday:
            lines.append(f"  День рождения: {contact.birthday}")

        if contact.note:
            lines.append(f"  Заметка: {contact.note[:200]}{'...' if len(contact.note) > 200 else ''}")

        if contact.url:
            lines.append(f"  URL: {contact.url}")

        if contact.social_profiles:
            lines.append(f"  Социальные сети:")
            for network, profile in contact.social_profiles.items():
                lines.append(f"    - {network}: {profile}")

        if contact.custom_fields:
            lines.append(f"  Дополнительные поля:")
            for key, value in contact.custom_fields.items():
                lines.append(f"    - {key}: {value}")

        if contact.photo_file:
            lines.append(f"  Фото: {contact.photo_file}")

        if contact.whatsapp_chat_folder:
            lines.append(f"  WhatsApp чат: {contact.whatsapp_chat_folder}")
            if contact.chat_statistics:
                stats = contact.chat_statistics
                lines.append(f"    Сообщений: {stats.get('messages_count', 0)}")
                if stats.get('first_message_date'):
                    lines.append(f"    Первое: {stats['first_message_date'][:10]}")
                if stats.get('last_message_date'):
                    lines.append(f"    Последнее: {stats['last_message_date'][:10]}")

        lines.append(f"  Источник: {contact.source_file}")
        lines.append("")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"TXT сохранен: {output_file}")


def print_summary(contacts: List[VCardContact]):
    """Вывод сводки"""
    print("\n" + "="*60)
    print("СВОДКА ПАРСИНГА VCF")
    print("="*60)

    print(f"Всего контактов: {len(contacts)}")

    with_phones = sum(1 for c in contacts if c.phones)
    total_phones = sum(len(c.phones) for c in contacts)
    print(f"С телефонами: {with_phones} (всего номеров: {total_phones})")

    with_emails = sum(1 for c in contacts if c.emails)
    print(f"С email: {with_emails}")

    with_photos = sum(1 for c in contacts if c.photo_base64 or c.photo_file)
    print(f"С фото: {with_photos}")

    with_org = sum(1 for c in contacts if c.organization)
    print(f"С организацией: {with_org}")

    with_birthday = sum(1 for c in contacts if c.birthday)
    print(f"С днем рождения: {with_birthday}")

    with_addresses = sum(1 for c in contacts if c.addresses)
    print(f"С адресами: {with_addresses}")

    with_notes = sum(1 for c in contacts if c.note)
    print(f"С заметками: {with_notes}")

    with_social = sum(1 for c in contacts if c.social_profiles)
    print(f"С соцсетями: {with_social}")

    with_chats = sum(1 for c in contacts if c.whatsapp_chat_folder)
    print(f"Связаны с чатами: {with_chats}")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Расширенный парсер VCF контактов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python parse_vcf_advanced.py ./contacts/
  python parse_vcf_advanced.py ./contacts/ --extract-photos
  python parse_vcf_advanced.py ./contacts/ --chats ./chats/ --enrich
  python parse_vcf_advanced.py ./contacts/ -o result --format all
        """
    )

    parser.add_argument("directory", help="Папка с VCF файлами")
    parser.add_argument("-o", "--output", default=None,
                       help="Базовое имя выходного файла (без расширения)")
    parser.add_argument("--format", choices=['json', 'csv', 'txt', 'all'],
                       default='all', help="Формат экспорта (default: all)")
    parser.add_argument("--extract-photos", action="store_true",
                       help="Извлечь фото контактов в файлы")
    parser.add_argument("--chats", default=None,
                       help="Папка с чатами WhatsApp для связывания")
    parser.add_argument("--enrich", action="store_true",
                       help="Обогатить данные из связанных чатов")
    parser.add_argument("-q", "--quiet", action="store_true",
                       help="Минимальный вывод")

    args = parser.parse_args()

    # Проверяем директорию
    if not os.path.isdir(args.directory):
        print(f"Ошибка: директория не существует: {args.directory}")
        sys.exit(1)

    # Ищем VCF файлы
    vcf_files = glob.glob(os.path.join(args.directory, "*.vcf"))
    vcf_files += glob.glob(os.path.join(args.directory, "*.VCF"))
    vcf_files = list(set(vcf_files))  # Убираем дубликаты

    if not vcf_files:
        print(f"VCF файлы не найдены в: {args.directory}")
        sys.exit(1)

    print(f"Найдено {len(vcf_files)} VCF файлов")
    print("-" * 60)

    # Парсим все файлы
    all_contacts = []
    for filepath in vcf_files:
        if not args.quiet:
            print(f"Обработка: {os.path.basename(filepath)}")

        contacts = parse_vcf_file(filepath)
        all_contacts.extend(contacts)

        if not args.quiet:
            print(f"  Найдено контактов: {len(contacts)}")

    print(f"\nВсего контактов: {len(all_contacts)}")

    # Извлекаем фото
    if args.extract_photos:
        print("\nИзвлечение фото...")
        extracted = extract_photos(all_contacts, args.directory)
        print(f"Извлечено фото: {extracted}")

    # Связываем с чатами
    if args.chats:
        print(f"\nСвязывание с чатами из: {args.chats}")
        linked = find_whatsapp_chats(all_contacts, args.chats)
        print(f"Связано с чатами: {linked}")

        # Обогащаем данные
        if args.enrich:
            print("\nОбогащение данными из чатов...")
            enriched = enrich_from_chats(all_contacts)
            print(f"Обогащено профилей: {enriched}")

    # Определяем имя выходного файла
    base_output = args.output or os.path.join(args.directory, "vcf_contacts")

    # Экспортируем
    print("\nЭкспорт данных...")

    if args.format in ['json', 'all']:
        export_to_json(all_contacts, base_output + '.json')

    if args.format in ['csv', 'all']:
        export_to_csv(all_contacts, base_output + '.csv')

    if args.format in ['txt', 'all']:
        export_to_text(all_contacts, base_output + '.txt')

    # Выводим сводку
    if not args.quiet:
        print_summary(all_contacts)

    print("\nГотово!")


if __name__ == "__main__":
    main()
