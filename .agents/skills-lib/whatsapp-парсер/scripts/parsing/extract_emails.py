#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение и валидация email адресов из чатов WhatsApp.

Вход:
- D:/Downloads/Chats/_база/raw/all_messages.jsonl
- D:/Downloads/Chats/_база/json/contacts.json

Выход:
- D:/Downloads/Chats/_база/json/emails.json
- D:/Downloads/Chats/_база/csv/emails_for_mailing.csv

Функции:
1. Regex извлечение email из сообщений
2. Валидация email (формат, MX записи)
3. Категоризация (личные, корпоративные, временные)
4. Связь email с контактами
5. Дедупликация
6. Статистика по доменам
7. Экспорт: CSV для рассылок, JSON
"""

import json
import re
import sys
import csv
import socket
import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional
import dns.resolver

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent))
from config import RAW_DIR, JSON_DIR, CSV_DIR, ensure_directories

# Настройка кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ
# ═══════════════════════════════════════════════════════════════

INPUT_MESSAGES = RAW_DIR / "all_messages.jsonl"
INPUT_CONTACTS = JSON_DIR / "contacts.json"
OUTPUT_JSON = JSON_DIR / "emails.json"
OUTPUT_CSV = CSV_DIR / "emails_for_mailing.csv"

# Regex для извлечения email
EMAIL_PATTERN = re.compile(
    r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    re.IGNORECASE
)

# Строгий паттерн для валидации
EMAIL_STRICT_PATTERN = re.compile(
    r'^[a-zA-Z0-9]'                      # Начинается с буквы/цифры
    r'[a-zA-Z0-9._%+-]*'                 # Допустимые символы
    r'@'
    r'[a-zA-Z0-9]'                       # Домен начинается с буквы/цифры
    r'[a-zA-Z0-9.-]*'                    # Допустимые символы в домене
    r'\.'
    r'[a-zA-Z]{2,}$',                    # TLD минимум 2 символа
    re.IGNORECASE
)

# ═══════════════════════════════════════════════════════════════
# ДОМЕНЫ ДЛЯ КАТЕГОРИЗАЦИИ
# ═══════════════════════════════════════════════════════════════

# Личные почтовые сервисы
PERSONAL_DOMAINS = {
    # Gmail и Google
    'gmail.com', 'googlemail.com',
    # Яндекс
    'yandex.ru', 'yandex.com', 'yandex.ua', 'yandex.kz', 'yandex.by',
    'ya.ru', 'narod.ru',
    # Mail.ru Group
    'mail.ru', 'inbox.ru', 'list.ru', 'bk.ru', 'internet.ru',
    # Рамблер
    'rambler.ru', 'lenta.ru', 'autorambler.ru', 'myrambler.ru', 'ro.ru',
    # Другие русскоязычные
    'email.ru', 'pochta.ru', 'i.ua', 'ukr.net', 'meta.ua', 'bigmir.net',
    # Microsoft
    'outlook.com', 'hotmail.com', 'live.com', 'msn.com',
    'hotmail.ru', 'outlook.ru',
    # Yahoo
    'yahoo.com', 'yahoo.co.uk', 'yahoo.fr', 'yahoo.de',
    # iCloud
    'icloud.com', 'me.com', 'mac.com',
    # Proton
    'protonmail.com', 'proton.me', 'pm.me',
    # Другие международные
    'aol.com', 'zoho.com', 'gmx.com', 'gmx.de', 'gmx.net',
    'mail.com', 'email.com', 'usa.com', 'europe.com',
    # ОАЭ
    'emirates.net.ae', 'eim.ae',
}

# Временные/одноразовые почтовые сервисы
DISPOSABLE_DOMAINS = {
    # Популярные одноразовые
    'tempmail.com', 'temp-mail.org', 'temp-mail.ru',
    'guerrillamail.com', 'guerrillamail.org', 'guerrillamail.net',
    'mailinator.com', 'maildrop.cc', 'throwaway.email',
    '10minutemail.com', '10minutemail.net', 'minutemail.com',
    'fakeinbox.com', 'trashmail.com', 'trashmail.net',
    'sharklasers.com', 'guerrillamailblock.com', 'pokemail.net',
    'spam4.me', 'spamgourmet.com', 'mytemp.email',
    'tempail.com', 'tempr.email', 'discard.email',
    'discardmail.com', 'disposablemail.com', 'disposemail.com',
    'yopmail.com', 'yopmail.fr', 'yopmail.net',
    'mailnesia.com', 'getnada.com', 'mohmal.com',
    'fakemailgenerator.com', 'emailondeck.com',
    'getairmail.com', 'jetable.org', 'mailcatch.com',
    'mailnull.com', 'mailsac.com', 'maildrop.cc',
    'tempsky.com', 'tempmailaddress.com', 'emailfake.com',
    'crazymailing.com', 'fakeinbox.net', 'tempinbox.com',
    # Русскоязычные одноразовые
    'dispostable.com', 'mailforspam.com', 'spambox.us',
}

# Известные корпоративные домены партнёров (можно расширять)
KNOWN_CORPORATE_DOMAINS = {
    # Туризм ОАЭ
    'visitdubai.com', 'dubaitourism.ae',
    # Авиакомпании
    'emirates.com', 'etihad.com', 'flydubai.com',
    # Отели
    'jumeirah.com', 'atlantisthepalm.com', 'rotana.com',
    # Турагентства
    'viator.com', 'getyourguide.com', 'klook.com',
}


# ═══════════════════════════════════════════════════════════════
# КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class EmailExtractor:
    """Извлекает и валидирует email адреса из чатов."""

    def __init__(self, check_mx: bool = True, mx_timeout: float = 3.0):
        """
        Args:
            check_mx: Проверять MX-записи доменов
            mx_timeout: Таймаут DNS запросов (секунды)
        """
        self.check_mx = check_mx
        self.mx_timeout = mx_timeout

        # Кэш результатов MX-проверок
        self.mx_cache: dict[str, bool] = {}

        # Хранилище извлечённых email
        self.emails: dict[str, dict] = {}  # email -> данные

        # Связь email с контактами
        self.email_to_contacts: dict[str, set] = defaultdict(set)

        # Контакты из contacts.json
        self.contacts: dict[str, dict] = {}  # jid -> контакт

        # Статистика
        self.stats = {
            'total_messages': 0,
            'messages_with_email': 0,
            'total_emails_found': 0,
            'unique_emails': 0,
            'valid_emails': 0,
            'invalid_format': 0,
            'invalid_mx': 0,
            'disposable': 0,
        }

    def load_contacts(self) -> bool:
        """Загружает контакты из contacts.json."""
        if not INPUT_CONTACTS.exists():
            print(f"[!] Файл контактов не найден: {INPUT_CONTACTS}")
            return False

        try:
            with open(INPUT_CONTACTS, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Поддержка двух форматов: список или объект с ключом 'contacts'
            if isinstance(data, list):
                contacts_list = data
            elif isinstance(data, dict):
                contacts_list = data.get('contacts', [])
            else:
                contacts_list = []

            for contact in contacts_list:
                jid = contact.get('jid')
                if jid:
                    self.contacts[jid] = contact

            print(f"  Загружено контактов: {len(self.contacts):,}")
            return True
        except Exception as e:
            print(f"[!] Ошибка загрузки контактов: {e}")
            return False

    def validate_format(self, email: str) -> bool:
        """Проверяет формат email."""
        if not email or len(email) > 254:
            return False

        # Базовая проверка структуры
        if email.count('@') != 1:
            return False

        local, domain = email.rsplit('@', 1)

        # Проверка локальной части
        if not local or len(local) > 64:
            return False

        # Проверка домена
        if not domain or len(domain) > 253:
            return False

        # Строгая проверка regex
        return bool(EMAIL_STRICT_PATTERN.match(email))

    def check_mx_record(self, domain: str) -> bool:
        """Проверяет наличие MX-записей домена."""
        if not self.check_mx:
            return True

        # Проверяем кэш
        if domain in self.mx_cache:
            return self.mx_cache[domain]

        try:
            # Настраиваем резолвер
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.mx_timeout
            resolver.lifetime = self.mx_timeout

            # Пробуем получить MX-записи
            try:
                mx_records = resolver.resolve(domain, 'MX')
                result = len(mx_records) > 0
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                # Если нет MX, пробуем A-запись
                try:
                    a_records = resolver.resolve(domain, 'A')
                    result = len(a_records) > 0
                except:
                    result = False
            except dns.resolver.NoNameservers:
                result = False

        except Exception:
            result = False

        self.mx_cache[domain] = result
        return result

    def categorize_email(self, email: str) -> dict:
        """
        Категоризирует email.

        Returns:
            dict с полями:
                - category: 'personal' | 'corporate' | 'disposable'
                - is_valid: bool
                - mx_valid: bool
                - domain_info: dict
        """
        result = {
            'category': 'unknown',
            'is_valid': False,
            'format_valid': False,
            'mx_valid': None,
            'domain': '',
            'domain_type': '',
        }

        # Нормализуем email
        email = email.lower().strip()

        # Проверяем формат
        if not self.validate_format(email):
            result['format_valid'] = False
            self.stats['invalid_format'] += 1
            return result

        result['format_valid'] = True

        # Извлекаем домен
        domain = email.rsplit('@', 1)[1]
        result['domain'] = domain

        # Определяем категорию по домену
        if domain in DISPOSABLE_DOMAINS:
            result['category'] = 'disposable'
            result['domain_type'] = 'disposable'
            self.stats['disposable'] += 1
            # Одноразовые email считаем невалидными для рассылок
            result['is_valid'] = False
            return result

        if domain in PERSONAL_DOMAINS:
            result['category'] = 'personal'
            result['domain_type'] = 'free_email'
        elif domain in KNOWN_CORPORATE_DOMAINS:
            result['category'] = 'corporate'
            result['domain_type'] = 'known_corporate'
        else:
            # Если домен не в списках - считаем корпоративным
            result['category'] = 'corporate'
            result['domain_type'] = 'custom_domain'

        # Проверяем MX-записи
        if self.check_mx:
            mx_valid = self.check_mx_record(domain)
            result['mx_valid'] = mx_valid

            if not mx_valid:
                result['is_valid'] = False
                self.stats['invalid_mx'] += 1
                return result

        # Email валиден
        result['is_valid'] = True
        self.stats['valid_emails'] += 1

        return result

    def extract_from_text(self, text: str) -> list[str]:
        """Извлекает все email из текста."""
        if not text:
            return []

        matches = EMAIL_PATTERN.findall(text)

        # Нормализация и дедупликация
        emails = []
        seen = set()
        for email in matches:
            email_lower = email.lower().strip()
            if email_lower not in seen:
                seen.add(email_lower)
                emails.append(email_lower)

        return emails

    def process_message(self, msg: dict):
        """Обрабатывает одно сообщение."""
        self.stats['total_messages'] += 1

        # Получаем текст сообщения
        text = msg.get('text') or msg.get('message') or msg.get('content') or ''

        # Извлекаем email
        found_emails = self.extract_from_text(text)

        if not found_emails:
            return

        self.stats['messages_with_email'] += 1
        self.stats['total_emails_found'] += len(found_emails)

        # Получаем JID контакта
        jid = msg.get('jid') or msg.get('chat_jid') or ''
        timestamp = msg.get('timestamp') or msg.get('date') or ''
        is_from_me = msg.get('is_from_me', False)

        for email in found_emails:
            # Категоризируем email
            if email not in self.emails:
                category_info = self.categorize_email(email)

                self.emails[email] = {
                    'email': email,
                    'domain': category_info['domain'],
                    'category': category_info['category'],
                    'domain_type': category_info['domain_type'],
                    'format_valid': category_info['format_valid'],
                    'mx_valid': category_info['mx_valid'],
                    'is_valid': category_info['is_valid'],
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'mention_count': 0,
                    'contact_jids': [],
                    'sent_by_me': False,
                    'sent_by_contact': False,
                }

            # Обновляем данные
            email_data = self.emails[email]
            email_data['mention_count'] += 1

            if timestamp:
                if not email_data['first_seen'] or timestamp < email_data['first_seen']:
                    email_data['first_seen'] = timestamp
                if not email_data['last_seen'] or timestamp > email_data['last_seen']:
                    email_data['last_seen'] = timestamp

            if is_from_me:
                email_data['sent_by_me'] = True
            else:
                email_data['sent_by_contact'] = True

            # Связываем с контактом
            if jid and jid not in email_data['contact_jids']:
                email_data['contact_jids'].append(jid)
                self.email_to_contacts[email].add(jid)

    def enrich_with_contacts(self):
        """Обогащает данные email информацией о контактах."""
        for email, email_data in self.emails.items():
            contacts_info = []

            for jid in email_data['contact_jids']:
                if jid in self.contacts:
                    contact = self.contacts[jid]
                    contacts_info.append({
                        'contact_id': contact.get('contact_id'),
                        'name': contact.get('name'),
                        'phone': contact.get('phone'),
                        'type': contact.get('type'),
                        'language': contact.get('language'),
                    })

            email_data['contacts'] = contacts_info

            # Определяем основного контакта (тот у кого больше сообщений)
            if contacts_info:
                email_data['primary_contact'] = contacts_info[0]
            else:
                email_data['primary_contact'] = None

    def build_statistics(self) -> dict:
        """Собирает статистику по извлечённым email."""
        # Статистика по доменам
        domain_counter = Counter()
        category_counter = Counter()
        domain_type_counter = Counter()

        for email_data in self.emails.values():
            domain_counter[email_data['domain']] += 1
            category_counter[email_data['category']] += 1
            domain_type_counter[email_data['domain_type']] += 1

        self.stats['unique_emails'] = len(self.emails)

        return {
            'summary': self.stats,
            'by_domain': dict(domain_counter.most_common(50)),
            'by_category': dict(category_counter),
            'by_domain_type': dict(domain_type_counter),
            'top_domains': domain_counter.most_common(20),
            'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        }

    def export_json(self) -> Path:
        """Экспортирует результаты в JSON."""
        # Формируем список email
        emails_list = sorted(
            self.emails.values(),
            key=lambda x: (not x['is_valid'], -x['mention_count'], x['email'])
        )

        output_data = {
            'emails': emails_list,
            'statistics': self.build_statistics(),
        }

        JSON_DIR.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return OUTPUT_JSON

    def export_csv_for_mailing(self) -> Path:
        """Экспортирует валидные email в CSV для рассылок."""
        # Фильтруем только валидные email
        valid_emails = [
            e for e in self.emails.values()
            if e['is_valid'] and e['category'] != 'disposable'
        ]

        # Сортируем: сначала корпоративные, потом личные
        valid_emails.sort(
            key=lambda x: (
                x['category'] != 'corporate',
                -x['mention_count'],
                x['email']
            )
        )

        CSV_DIR.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Заголовки
            writer.writerow([
                'email',
                'domain',
                'category',
                'domain_type',
                'contact_name',
                'contact_phone',
                'contact_type',
                'language',
                'mention_count',
                'first_seen',
                'last_seen',
            ])

            for email_data in valid_emails:
                contact = email_data.get('primary_contact') or {}

                writer.writerow([
                    email_data['email'],
                    email_data['domain'],
                    email_data['category'],
                    email_data['domain_type'],
                    contact.get('name', ''),
                    contact.get('phone', ''),
                    contact.get('type', ''),
                    contact.get('language', ''),
                    email_data['mention_count'],
                    email_data['first_seen'],
                    email_data['last_seen'],
                ])

        return OUTPUT_CSV


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Основная функция."""
    print("=" * 60)
    print("Извлечение email адресов из чатов WhatsApp")
    print("=" * 60)

    # Проверяем/создаём директории
    ensure_directories()

    # Проверяем входной файл
    if not INPUT_MESSAGES.exists():
        print(f"\n[ОШИБКА] Файл сообщений не найден: {INPUT_MESSAGES}")
        print("\nСначала запустите parse_all_chats.py для создания all_messages.jsonl")
        sys.exit(1)

    print(f"\nВходные файлы:")
    print(f"  - Сообщения: {INPUT_MESSAGES}")
    print(f"  - Контакты:  {INPUT_CONTACTS}")
    print(f"\nВыходные файлы:")
    print(f"  - JSON: {OUTPUT_JSON}")
    print(f"  - CSV:  {OUTPUT_CSV}")

    # Проверяем доступность DNS для MX-проверок
    check_mx = True
    try:
        import dns.resolver
        # Тестовый запрос
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2
        resolver.resolve('gmail.com', 'MX')
        print("\n[i] MX-проверка доменов: включена")
    except ImportError:
        print("\n[!] Библиотека dnspython не установлена")
        print("    Установите: pip install dnspython")
        print("    MX-проверка отключена")
        check_mx = False
    except Exception as e:
        print(f"\n[!] DNS недоступен: {e}")
        print("    MX-проверка отключена")
        check_mx = False

    # Создаём экстрактор
    extractor = EmailExtractor(check_mx=check_mx)

    # Загружаем контакты
    print("\n[1/5] Загрузка контактов...")
    extractor.load_contacts()

    # Читаем и обрабатываем сообщения
    print("\n[2/5] Обработка сообщений...")
    line_count = 0
    error_count = 0

    with open(INPUT_MESSAGES, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            if line_count % 100000 == 0:
                print(f"  Обработано: {line_count:,} строк, "
                      f"найдено: {extractor.stats['total_emails_found']:,} email")

            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
                extractor.process_message(msg)
            except json.JSONDecodeError as e:
                error_count += 1
                if error_count <= 5:
                    print(f"  [Ошибка JSON] Строка {line_count}: {e}")

    print(f"  Всего строк: {line_count:,}")
    if error_count:
        print(f"  Ошибок парсинга: {error_count}")

    # Обогащаем данными контактов
    print("\n[3/5] Обогащение данными контактов...")
    extractor.enrich_with_contacts()

    # Экспорт JSON
    print("\n[4/5] Экспорт в JSON...")
    json_path = extractor.export_json()
    print(f"  Сохранено: {json_path}")

    # Экспорт CSV
    print("\n[5/5] Экспорт CSV для рассылок...")
    csv_path = extractor.export_csv_for_mailing()
    print(f"  Сохранено: {csv_path}")

    # Итоговая статистика
    stats = extractor.stats
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    print(f"Обработано сообщений: {stats['total_messages']:,}")
    print(f"Сообщений с email: {stats['messages_with_email']:,}")
    print(f"Найдено упоминаний email: {stats['total_emails_found']:,}")
    print(f"Уникальных email: {stats['unique_emails']:,}")
    print(f"\nВалидация:")
    print(f"  - Валидных: {stats['valid_emails']:,}")
    print(f"  - Невалидный формат: {stats['invalid_format']:,}")
    if check_mx:
        print(f"  - Нет MX-записей: {stats['invalid_mx']:,}")
    print(f"  - Одноразовых: {stats['disposable']:,}")

    # Статистика по категориям
    category_stats = Counter()
    domain_stats = Counter()
    for email_data in extractor.emails.values():
        category_stats[email_data['category']] += 1
        domain_stats[email_data['domain']] += 1

    print(f"\nПо категориям:")
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        cat_label = {
            'personal': 'Личные',
            'corporate': 'Корпоративные',
            'disposable': 'Одноразовые',
            'unknown': 'Неизвестно',
        }.get(cat, cat)
        print(f"  - {cat_label}: {count:,}")

    print(f"\nТоп-10 доменов:")
    for domain, count in domain_stats.most_common(10):
        print(f"  - {domain}: {count:,}")

    # Статистика для рассылок
    valid_for_mailing = sum(
        1 for e in extractor.emails.values()
        if e['is_valid'] and e['category'] != 'disposable'
    )
    print(f"\n[CSV] Email для рассылок: {valid_for_mailing:,}")

    print("\n" + "=" * 60)
    print("Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
