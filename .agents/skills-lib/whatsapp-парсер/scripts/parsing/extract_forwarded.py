#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение и анализ пересланных сообщений из WhatsApp чатов

Функции:
1. Детекция пересланных сообщений (RU/EN паттерны)
2. Извлечение оригинального отправителя (если доступно)
3. Статистика: кто пересылает, что чаще всего, цепочки
4. Категоризация: прайсы, каталоги, новости, реклама, мемы
5. Детекция вирусного контента (одинаковое от разных людей)
6. Экспорт: JSON с метаданными + Markdown отчет
"""

import sys
import os
import re
import json
import glob
import argparse
import hashlib
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple, Any

sys.stdout.reconfigure(encoding='utf-8')


# =============================================================================
# ПАТТЕРНЫ ДЛЯ ДЕТЕКЦИИ ПЕРЕСЛАННЫХ СООБЩЕНИЙ
# =============================================================================

# WhatsApp маркирует пересланные сообщения по-разному в зависимости от языка/версии
FORWARDED_PATTERNS = {
    # Русский - явные маркеры WhatsApp
    'ru_explicit': r'(?:^|\n|\s)(?:Переслано|Пересланное сообщение|Пересланное)(?:\s|$|:)',
    'ru_from': r'(?:Переслано от|Переслал\s+от|От\s+кого)\s*[:\-]?\s*([^\n\[\]]{2,50})',
    'ru_forwarded_many': r'Переслано много раз|Пересылалось много раз',

    # Английский - явные маркеры WhatsApp
    'en_explicit': r'(?:^|\n|\s)(?:Forwarded|Forwarded message)(?:\s|$|:)',
    'en_from': r'(?:Forwarded from|Originally from|From)\s*[:\-]?\s*([^\n\[\]]{2,50})',
    'en_forwarded_many': r'Forwarded many times',

    # WhatsApp экспорт специфика (системные сообщения в экспорте)
    'wa_system_forward': r'<attached:\s*\d+-FWD-',  # Прикрепленные пересланные файлы
    'wa_forward_indicator': r'\[Forwarded\]|\(Forwarded\)',

    # Универсальные метки
    'whatsapp_forward_marker': r'⤴️|↩️|🔄|📩',  # Эмодзи пересылки
    'whatsapp_chain': r'(?:>>>|➡️|Fwd:|FW:|RE:|ПС:|Fw:)',

    # Telegram каналы/группы (часто пересылают оттуда)
    'telegram_forward': r'(?:@[a-zA-Z0-9_]{5,32}|t\.me/[a-zA-Z0-9_]+)',
}

# Паттерны для определения оригинального источника
ORIGINAL_SOURCE_PATTERNS = [
    r'(?:Переслано от|Forwarded from|Originally from)\s*[:\-]?\s*([^\n\r]{2,40}?)(?:\s*$|\s*\n)',
    r'(?:Источник|Source)\s*[:\-]?\s*([^\n\r]{2,40}?)(?:\s*$|\s*\n)',
    r'(?:Канал|Channel)\s*[:\-]?\s*(@?[a-zA-Z0-9_]{3,32})',  # Telegram каналы
    r'Forwarded from\s+(@[a-zA-Z0-9_]{3,32})',  # Telegram @channel
]


# =============================================================================
# КАТЕГОРИИ КОНТЕНТА
# =============================================================================

CONTENT_CATEGORIES = {
    'price_catalog': {
        'name_ru': 'Прайсы и каталоги',
        'name_en': 'Prices & Catalogs',
        'keywords': [
            # Цены
            'прайс', 'price', 'стоимость', 'cost', 'тариф', 'tariff', 'rate',
            'цена', 'расценк', 'прейскурант', 'quotation', 'quote',
            # Каталоги
            'каталог', 'catalog', 'catalogue', 'меню', 'menu', 'ассортимент',
            'assortment', 'lineup', 'portfolio',
            # Валюты (часто в прайсах)
            'AED', 'USD', 'EUR', 'RUB', '₽', '$', '€', 'дирхам', 'dirham',
            # Единицы
            'за час', 'per hour', 'в день', 'per day', 'за шт', 'за единиц',
        ],
        'patterns': [
            r'\d+[\s,.]?\d*\s*(?:AED|USD|EUR|RUB|₽|\$|€)',
            r'(?:от|from)\s*\d+',
            r'\d+\s*[-–—]\s*\d+\s*(?:AED|USD|EUR|RUB)',
        ],
    },

    'news_updates': {
        'name_ru': 'Новости и обновления',
        'name_en': 'News & Updates',
        'keywords': [
            # Новости
            'новост', 'news', 'breaking', 'срочно', 'urgent', 'важно', 'important',
            'внимание', 'attention', 'анонс', 'announcement',
            # Обновления
            'обновлен', 'update', 'изменен', 'change', 'нов', 'new',
            # Источники
            'источник', 'source', 'по данным', 'according to', 'сообщает', 'reports',
        ],
        'patterns': [
            r'(?:СРОЧНО|ВАЖНО|BREAKING|URGENT)[!:\s]',
            r'(?:По данным|According to|Источник)',
        ],
    },

    'advertising': {
        'name_ru': 'Реклама и промо',
        'name_en': 'Advertising & Promo',
        'keywords': [
            # Реклама
            'реклам', 'ad', 'advert', 'промо', 'promo', 'акци', 'sale', 'скидк', 'discount',
            'распродаж', 'clearance', 'специальн', 'special', 'эксклюзив', 'exclusive',
            # Призывы
            'успей', 'hurry', 'только сегодня', 'today only', 'ограничен', 'limited',
            'не упусти', 'don\'t miss', 'последний шанс', 'last chance',
            # Контакты для заказа
            'заказ', 'order', 'забронир', 'book', 'свяжитесь', 'contact',
            'написать', 'write', 'позвонить', 'call',
        ],
        'patterns': [
            r'(?:СКИДКА|SALE|АКЦИЯ|PROMO)\s*\d+%?',
            r'(?:только до|until|valid till)\s*\d{1,2}[./]\d{1,2}',
            r'(?:при заказе|when ordering|при покупке)',
        ],
    },

    'entertainment': {
        'name_ru': 'Мемы и развлечения',
        'name_en': 'Memes & Entertainment',
        'keywords': [
            # Развлечения
            'мем', 'meme', 'прикол', 'funny', 'смешн', 'joke', 'анекдот',
            'юмор', 'humor', 'лол', 'lol', 'хаха', 'haha', 'ржу', 'rofl',
            # Вирусное
            'вирусн', 'viral', 'тренд', 'trend', 'хайп', 'hype',
            # Медиа
            'видео', 'video', 'тикток', 'tiktok', 'рилс', 'reels', 'шортс', 'shorts',
        ],
        'patterns': [
            r'[😂🤣😅😆💀☠️]{2,}',  # Много смеющихся эмодзи
            r'(?:https?://)?(?:www\.)?(?:tiktok|instagram|youtube\.com/shorts)',
        ],
    },

    'informational': {
        'name_ru': 'Информационное',
        'name_en': 'Informational',
        'keywords': [
            # Инструкции
            'инструкци', 'instruction', 'руководств', 'guide', 'manual',
            'как сделать', 'how to', 'пошагов', 'step by step',
            # Полезное
            'полезн', 'useful', 'совет', 'tip', 'лайфхак', 'lifehack',
            'рекомендац', 'recommendation',
            # Справочное
            'справк', 'reference', 'информаци', 'information', 'данные', 'data',
        ],
        'patterns': [
            r'(?:Шаг|Step)\s*\d+[.:\s]',
            r'(?:\d+[.)]\s+[А-Яа-яA-Za-z]){3,}',  # Нумерованные списки
        ],
    },

    'business_documents': {
        'name_ru': 'Деловые документы',
        'name_en': 'Business Documents',
        'keywords': [
            # Документы
            'документ', 'document', 'договор', 'contract', 'agreement',
            'счет', 'invoice', 'накладн', 'waybill', 'акт', 'act',
            # Официальное
            'официальн', 'official', 'подпись', 'signature', 'печать', 'stamp',
            'реквизит', 'requisites', 'банк', 'bank',
        ],
        'patterns': [
            r'(?:ИНН|ОГРН|БИК|КПП|TIN|VAT)',
            r'(?:р/с|к/с|account)',
        ],
    },

    'event_invitation': {
        'name_ru': 'Приглашения на события',
        'name_en': 'Event Invitations',
        'keywords': [
            # События
            'приглаша', 'invite', 'событи', 'event', 'мероприяти', 'мероприятие',
            'вечеринк', 'party', 'встреч', 'meeting', 'конференц', 'conference',
            # Детали
            'где', 'where', 'когда', 'when', 'время', 'time', 'место', 'place',
            'адрес', 'address', 'локаци', 'location',
            # Действия
            'регистрац', 'registration', 'записаться', 'sign up', 'участ', 'participate',
        ],
        'patterns': [
            r'\d{1,2}[./]\d{1,2}[./]?\d{0,4}\s*(?:в|at)?\s*\d{1,2}[:.]\d{2}',
        ],
    },
}


# =============================================================================
# ОСНОВНЫЕ КЛАССЫ
# =============================================================================

class ForwardedMessage:
    """Структура пересланного сообщения"""

    def __init__(
        self,
        date: str,
        time: str,
        forwarder: str,  # Кто переслал
        content: str,
        original_source: Optional[str] = None,
        is_many_times_forwarded: bool = False,
        category: Optional[str] = None,
        content_hash: Optional[str] = None,
        line_number: int = 0,
        source_file: str = "",
    ):
        self.date = date
        self.time = time
        self.forwarder = forwarder
        self.content = content
        self.original_source = original_source
        self.is_many_times_forwarded = is_many_times_forwarded
        self.category = category
        self.content_hash = content_hash or self._compute_hash()
        self.line_number = line_number
        self.source_file = source_file

    def _compute_hash(self) -> str:
        """Вычисляет хеш контента для детекции вирусного контента"""
        # Нормализуем текст: lowercase, убираем пробелы, цифры (могут меняться в ценах)
        normalized = re.sub(r'\s+', ' ', self.content.lower().strip())
        normalized = re.sub(r'\d+', '#', normalized)  # Заменяем числа на #
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date,
            'time': self.time,
            'forwarder': self.forwarder,
            'content': self.content[:500],  # Ограничиваем размер
            'content_full_length': len(self.content),
            'original_source': self.original_source,
            'is_many_times_forwarded': self.is_many_times_forwarded,
            'category': self.category,
            'content_hash': self.content_hash,
            'line_number': self.line_number,
            'source_file': self.source_file,
        }


class ForwardedAnalyzer:
    """Анализатор пересланных сообщений"""

    def __init__(self):
        self.messages: List[ForwardedMessage] = []
        self.stats = {
            'total_forwarded': 0,
            'by_forwarder': Counter(),
            'by_category': Counter(),
            'by_date': Counter(),
            'by_original_source': Counter(),
            'viral_content': defaultdict(list),  # hash -> list of messages
            'chains': [],  # Цепочки пересылок
        }

    def detect_forwarded(self, line: str, next_lines: List[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Определяет, является ли сообщение пересланным.
        Возвращает (is_forwarded, original_source)

        Логика: пересланным считается сообщение, которое:
        1. Начинается с явного маркера пересылки (Переслано, Forwarded, Fwd:)
        2. Или содержит "Forwarded from" / "Переслано от" в первых строках
        """
        first_line = line.strip()
        full_text = line + (' ' + ' '.join(next_lines[:3]) if next_lines else '')

        is_forwarded = False
        original_source = None

        # Паттерны, которые должны быть в НАЧАЛЕ сообщения
        START_PATTERNS = {
            'ru_start': r'^(?:Переслано|Пересланное|Fwd:|FW:|ПС:)',
            'en_start': r'^(?:Forwarded|Fwd:|FW:|RE:)',
            'emoji_start': r'^[⤴️↩️🔄📩➡️]',
        }

        # Паттерны, которые могут быть где угодно (но специфичные)
        ANYWHERE_PATTERNS = {
            'ru_from': r'(?:Переслано от|Переслал от)\s*[:\-]?\s*([^\n\[\]]{2,50})',
            'en_from': r'(?:Forwarded from|Originally from)\s*[:\-]?\s*([^\n\[\]]{2,50})',
            'many_times': r'(?:Переслано много раз|Forwarded many times|Пересылалось много раз)',
            'telegram_from': r'Forwarded from\s+@([a-zA-Z0-9_]{5,32})',
        }

        # Проверяем начало сообщения
        for pattern_name, pattern in START_PATTERNS.items():
            if re.match(pattern, first_line, re.IGNORECASE):
                is_forwarded = True
                break

        # Проверяем специфичные паттерны в полном тексте
        if not is_forwarded:
            for pattern_name, pattern in ANYWHERE_PATTERNS.items():
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    is_forwarded = True
                    if match.groups():
                        original_source = match.group(1).strip()
                    break

        # Извлекаем оригинальный источник, если еще не нашли
        if is_forwarded and not original_source:
            for pattern in ORIGINAL_SOURCE_PATTERNS:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    original_source = match.group(1).strip()
                    break

        return is_forwarded, original_source

    def categorize_content(self, content: str) -> str:
        """Категоризирует контент пересланного сообщения"""
        content_lower = content.lower()
        scores = {}

        for cat_id, cat_data in CONTENT_CATEGORIES.items():
            score = 0

            # Проверяем ключевые слова
            for keyword in cat_data['keywords']:
                if keyword.lower() in content_lower:
                    score += 1

            # Проверяем паттерны
            for pattern in cat_data.get('patterns', []):
                if re.search(pattern, content, re.IGNORECASE):
                    score += 2  # Паттерны весят больше

            scores[cat_id] = score

        # Возвращаем категорию с максимальным скором (если > 0)
        if scores:
            best_cat = max(scores, key=scores.get)
            if scores[best_cat] > 0:
                return best_cat

        return 'uncategorized'

    def parse_chat_line(self, line: str) -> Optional[Dict]:
        """Парсит строку чата"""
        # Формат: [DD.MM.YYYY, HH:MM:SS] Sender: Message
        pattern = r'\[(\d{2}\.\d{2}\.\d{4}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
        match = re.match(pattern, line)

        if match:
            return {
                'date': match.group(1),
                'time': match.group(2),
                'sender': match.group(3).strip(),
                'message': match.group(4)
            }
        return None

    def parse_md_line(self, line: str) -> Optional[Dict]:
        """Парсит строку из обработанного MD файла"""
        # Формат: **👤 Sender** [HH:MM:SS]
        pattern = r'\*\*([👤👨👩][^*]+)\*\*\s*\[(\d{2}:\d{2}:\d{2})\]'
        match = re.match(pattern, line)

        if match:
            sender = match.group(1).strip()
            sender = re.sub(r'^[👤👨👩]\s*', '', sender)  # Убираем эмодзи
            return {
                'sender': sender,
                'time': match.group(2),
            }
        return None

    def extract_from_file(self, filepath: str) -> List[ForwardedMessage]:
        """Извлекает пересланные сообщения из файла"""
        messages = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Ошибка чтения {filepath}: {e}")
            return messages

        current_date = None
        current_sender = None
        current_time = None
        message_buffer = []
        line_start = 0

        for i, line in enumerate(lines):
            # Обновляем дату из MD формата
            date_match = re.match(r'###\s*(\d{2}\.\d{2}\.\d{4})', line)
            if date_match:
                current_date = date_match.group(1)
                continue

            # Пробуем парсить как сырой чат
            parsed = self.parse_chat_line(line)
            if parsed:
                # Если был буфер - обрабатываем предыдущее сообщение
                if message_buffer and current_sender:
                    content = '\n'.join(message_buffer)
                    # Передаем только строки самого сообщения, без look-ahead
                    is_forwarded, original_source = self.detect_forwarded(
                        message_buffer[0] if message_buffer else '',
                        message_buffer[1:] if len(message_buffer) > 1 else []
                    )

                    if is_forwarded:
                        msg = ForwardedMessage(
                            date=current_date or parsed['date'],
                            time=current_time,
                            forwarder=current_sender,
                            content=content,
                            original_source=original_source,
                            is_many_times_forwarded=bool(re.search(
                                r'(?:много раз|many times)',
                                content,
                                re.IGNORECASE
                            )),
                            line_number=line_start,
                            source_file=filepath,
                        )
                        msg.category = self.categorize_content(content)
                        messages.append(msg)

                # Начинаем новое сообщение
                current_date = parsed['date']
                current_sender = parsed['sender']
                current_time = parsed['time']
                message_buffer = [parsed['message']]
                line_start = i + 1
                continue

            # Пробуем парсить как MD
            md_parsed = self.parse_md_line(line)
            if md_parsed:
                # Обрабатываем предыдущее
                if message_buffer and current_sender:
                    content = '\n'.join(message_buffer)
                    is_forwarded, original_source = self.detect_forwarded(content)

                    if is_forwarded:
                        msg = ForwardedMessage(
                            date=current_date or '',
                            time=current_time,
                            forwarder=current_sender,
                            content=content,
                            original_source=original_source,
                            is_many_times_forwarded=bool(re.search(
                                r'(?:много раз|many times)',
                                content,
                                re.IGNORECASE
                            )),
                            line_number=line_start,
                            source_file=filepath,
                        )
                        msg.category = self.categorize_content(content)
                        messages.append(msg)

                current_sender = md_parsed['sender']
                current_time = md_parsed['time']
                message_buffer = []
                line_start = i + 1
                continue

            # Добавляем строку в буфер текущего сообщения
            if current_sender and line.strip():
                message_buffer.append(line.strip())

        # Обрабатываем последнее сообщение
        if message_buffer and current_sender:
            content = '\n'.join(message_buffer)
            is_forwarded, original_source = self.detect_forwarded(content)

            if is_forwarded:
                msg = ForwardedMessage(
                    date=current_date or '',
                    time=current_time,
                    forwarder=current_sender,
                    content=content,
                    original_source=original_source,
                    line_number=line_start,
                    source_file=filepath,
                )
                msg.category = self.categorize_content(content)
                messages.append(msg)

        return messages

    def analyze_directory(self, chats_dir: str) -> None:
        """Анализирует все чаты в директории"""
        self.messages = []

        # Файлы и папки для исключения
        EXCLUDED_FILES = {
            'SKILL.md', 'CLAUDE.md', 'README.md', 'LICENSE.md',
            'контакты.md', 'события.md', 'адреса.md', 'связи.md',
            'быстрые_ответы.md', 'forwarded_report.md',
        }
        EXCLUDED_DIRS = {
            '__pycache__', '_база', '_аналитика', '_индекс', '_шаблоны',
            '_медиа', '_задачи', '_история', 'scripts', '.git',
        }

        # Ищем все файлы чатов
        patterns = [
            os.path.join(chats_dir, '**', '*.md'),
            os.path.join(chats_dir, '**', '*.txt'),
            os.path.join(chats_dir, '**', '_chat.txt'),
        ]

        processed_files = set()

        for pattern in patterns:
            for filepath in glob.glob(pattern, recursive=True):
                if filepath in processed_files:
                    continue

                # Пропускаем исключенные файлы
                filename = os.path.basename(filepath)
                if filename in EXCLUDED_FILES:
                    continue

                # Пропускаем исключенные директории
                path_parts = filepath.replace('\\', '/').split('/')
                if any(excluded in path_parts for excluded in EXCLUDED_DIRS):
                    continue

                if 'transcript' in filepath.lower():
                    continue

                processed_files.add(filepath)
                messages = self.extract_from_file(filepath)
                self.messages.extend(messages)

                if messages:
                    print(f"  {os.path.basename(filepath)}: {len(messages)} пересланных")

        self._compute_statistics()

    def _compute_statistics(self) -> None:
        """Вычисляет статистику"""
        self.stats = {
            'total_forwarded': len(self.messages),
            'by_forwarder': Counter(),
            'by_category': Counter(),
            'by_date': Counter(),
            'by_original_source': Counter(),
            'viral_content': defaultdict(list),
            'chains': [],
        }

        for msg in self.messages:
            self.stats['by_forwarder'][msg.forwarder] += 1
            self.stats['by_category'][msg.category] += 1
            self.stats['by_date'][msg.date] += 1

            if msg.original_source:
                self.stats['by_original_source'][msg.original_source] += 1

            # Группируем по хешу для детекции вирусного контента
            self.stats['viral_content'][msg.content_hash].append(msg)

        # Определяем вирусный контент (>= 2 пересылок одного контента)
        self.stats['viral_items'] = [
            {
                'hash': h,
                'count': len(msgs),
                'forwarders': list(set(m.forwarder for m in msgs)),
                'sample': msgs[0].content[:200],
                'category': msgs[0].category,
            }
            for h, msgs in self.stats['viral_content'].items()
            if len(msgs) >= 2
        ]
        self.stats['viral_items'].sort(key=lambda x: x['count'], reverse=True)

    def detect_chains(self) -> List[Dict]:
        """
        Детекция цепочек пересылок.
        Ищет последовательности, где один контент пересылается между контактами.
        """
        chains = []

        for content_hash, msgs in self.stats['viral_content'].items():
            if len(msgs) < 2:
                continue

            # Сортируем по дате/времени
            sorted_msgs = sorted(msgs, key=lambda m: (m.date, m.time))

            chain = {
                'content_hash': content_hash,
                'sample': sorted_msgs[0].content[:200],
                'category': sorted_msgs[0].category,
                'path': [],
            }

            for msg in sorted_msgs:
                chain['path'].append({
                    'forwarder': msg.forwarder,
                    'date': msg.date,
                    'time': msg.time,
                    'original_source': msg.original_source,
                })

            chains.append(chain)

        return chains

    def export_json(self, output_path: str) -> None:
        """Экспортирует результаты в JSON"""
        chains = self.detect_chains()

        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_forwarded_messages': self.stats['total_forwarded'],
                'unique_forwarders': len(self.stats['by_forwarder']),
                'viral_content_count': len(self.stats['viral_items']),
            },
            'statistics': {
                'by_forwarder': dict(self.stats['by_forwarder'].most_common(50)),
                'by_category': dict(self.stats['by_category']),
                'by_date': dict(self.stats['by_date'].most_common(30)),
                'by_original_source': dict(self.stats['by_original_source'].most_common(20)),
            },
            'viral_content': self.stats['viral_items'][:20],
            'forwarding_chains': chains[:20],
            'messages': [msg.to_dict() for msg in self.messages],
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"JSON сохранен: {output_path}")

    def generate_report(self, output_path: str) -> None:
        """Генерирует Markdown отчет"""
        chains = self.detect_chains()

        lines = []
        lines.append("# Анализ пересланных сообщений")
        lines.append("")
        lines.append(f"*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Общая статистика
        lines.append("## Общая статистика")
        lines.append("")
        lines.append("| Метрика | Значение |")
        lines.append("|---------|----------|")
        lines.append(f"| Всего пересланных | {self.stats['total_forwarded']} |")
        lines.append(f"| Уникальных отправителей | {len(self.stats['by_forwarder'])} |")
        lines.append(f"| Вирусного контента | {len(self.stats['viral_items'])} |")
        lines.append(f"| Цепочек пересылок | {len(chains)} |")
        lines.append("")

        # Топ отправителей
        lines.append("## Кто больше всего пересылает")
        lines.append("")
        for forwarder, count in self.stats['by_forwarder'].most_common(15):
            pct = (count / self.stats['total_forwarded'] * 100) if self.stats['total_forwarded'] > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            lines.append(f"- **{forwarder}**: {count} ({pct:.1f}%) `{bar}`")
        lines.append("")

        # По категориям
        lines.append("## Что чаще всего пересылают")
        lines.append("")
        lines.append("| Категория | Количество | % |")
        lines.append("|-----------|------------|---|")
        total = self.stats['total_forwarded']
        for cat_id, count in self.stats['by_category'].most_common():
            cat_name = CONTENT_CATEGORIES.get(cat_id, {}).get('name_ru', cat_id)
            pct = (count / total * 100) if total > 0 else 0
            lines.append(f"| {cat_name} | {count} | {pct:.1f}% |")
        lines.append("")

        # Оригинальные источники
        if self.stats['by_original_source']:
            lines.append("## Популярные источники пересылок")
            lines.append("")
            for source, count in self.stats['by_original_source'].most_common(10):
                lines.append(f"- **{source}**: {count} пересылок")
            lines.append("")

        # Вирусный контент
        if self.stats['viral_items']:
            lines.append("## Вирусный контент")
            lines.append("")
            lines.append("Контент, который пересылался несколько раз разными людьми:")
            lines.append("")

            for i, item in enumerate(self.stats['viral_items'][:10], 1):
                cat_name = CONTENT_CATEGORIES.get(item['category'], {}).get('name_ru', item['category'])
                lines.append(f"### {i}. {cat_name} (переслано {item['count']} раз)")
                lines.append("")
                lines.append(f"**Кто пересылал:** {', '.join(item['forwarders'][:5])}")
                lines.append("")
                lines.append("**Содержимое (отрывок):**")
                lines.append(f"> {item['sample'][:300]}...")
                lines.append("")
                lines.append("---")
                lines.append("")

        # Цепочки пересылок
        if chains:
            lines.append("## Цепочки пересылок")
            lines.append("")
            lines.append("Как контент распространялся между контактами:")
            lines.append("")

            for i, chain in enumerate(chains[:5], 1):
                cat_name = CONTENT_CATEGORIES.get(chain['category'], {}).get('name_ru', chain['category'])
                lines.append(f"### Цепочка {i}: {cat_name}")
                lines.append("")
                lines.append("```mermaid")
                lines.append("graph LR")

                prev_node = None
                for j, step in enumerate(chain['path']):
                    node_id = f"N{j}"
                    node_label = step['forwarder'][:20]
                    if step['original_source']:
                        lines.append(f"    SRC[{step['original_source'][:15]}] --> {node_id}[{node_label}]")
                    elif prev_node:
                        lines.append(f"    {prev_node} --> {node_id}[{node_label}]")
                    else:
                        lines.append(f"    {node_id}[{node_label}]")
                    prev_node = node_id

                lines.append("```")
                lines.append("")
                lines.append(f"**Содержимое:** {chain['sample'][:150]}...")
                lines.append("")
                lines.append("---")
                lines.append("")

        # Динамика по датам
        if self.stats['by_date']:
            lines.append("## Динамика пересылок по датам")
            lines.append("")
            lines.append("| Дата | Количество |")
            lines.append("|------|------------|")
            for date, count in sorted(self.stats['by_date'].items(), reverse=True)[:20]:
                lines.append(f"| {date} | {count} |")
            lines.append("")

        # Примеры по категориям
        lines.append("## Примеры пересланных сообщений по категориям")
        lines.append("")

        by_category = defaultdict(list)
        for msg in self.messages:
            by_category[msg.category].append(msg)

        for cat_id, cat_msgs in by_category.items():
            cat_name = CONTENT_CATEGORIES.get(cat_id, {}).get('name_ru', cat_id)
            lines.append(f"### {cat_name}")
            lines.append("")

            # Показываем до 3 примеров
            for msg in cat_msgs[:3]:
                lines.append(f"**От:** {msg.forwarder} | **Дата:** {msg.date}")
                if msg.original_source:
                    lines.append(f"**Источник:** {msg.original_source}")
                lines.append("")
                lines.append("> " + msg.content[:300].replace('\n', '\n> '))
                lines.append("")
                lines.append("---")
                lines.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Отчет сохранен: {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Извлечение и анализ пересланных сообщений из WhatsApp чатов"
    )
    parser.add_argument(
        "input",
        nargs='?',
        help="Путь к файлу чата или папке с чатами"
    )
    parser.add_argument(
        "--chats-dir",
        default="D:/Downloads/Chats",
        help="Папка с чатами (по умолчанию: D:/Downloads/Chats)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="D:/Downloads/Chats/_анализ",
        help="Папка для результатов"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Экспортировать только JSON (без Markdown отчета)"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Генерировать только Markdown отчет"
    )

    args = parser.parse_args()

    # Определяем входную директорию
    input_path = args.input or args.chats_dir

    if not os.path.exists(input_path):
        print(f"Путь не существует: {input_path}")
        return

    # Создаем выходную директорию
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Анализ пересланных сообщений...")
    print(f"Входной путь: {input_path}")
    print("")

    analyzer = ForwardedAnalyzer()

    if os.path.isfile(input_path):
        # Анализируем один файл
        messages = analyzer.extract_from_file(input_path)
        analyzer.messages = messages
        analyzer._compute_statistics()
        print(f"Найдено пересланных: {len(messages)}")
    else:
        # Анализируем директорию
        analyzer.analyze_directory(input_path)
        print(f"\nВсего найдено пересланных: {analyzer.stats['total_forwarded']}")

    # Экспорт
    if not args.report_only:
        json_path = os.path.join(args.output_dir, "forwarded_messages.json")
        analyzer.export_json(json_path)

    if not args.json_only:
        report_path = os.path.join(args.output_dir, "forwarded_report.md")
        analyzer.generate_report(report_path)

    # Выводим краткую сводку
    print("")
    print("=" * 50)
    print("СВОДКА")
    print("=" * 50)
    print(f"Всего пересланных сообщений: {analyzer.stats['total_forwarded']}")
    print(f"Уникальных отправителей: {len(analyzer.stats['by_forwarder'])}")
    print(f"Вирусного контента: {len(analyzer.stats['viral_items'])}")
    print("")

    if analyzer.stats['by_forwarder']:
        print("Топ-5 по пересылкам:")
        for name, count in analyzer.stats['by_forwarder'].most_common(5):
            print(f"  - {name}: {count}")

    print("")
    print("Результаты сохранены в:", args.output_dir)


if __name__ == "__main__":
    main()
