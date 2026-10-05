#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Детекция и анализ групповых чатов WhatsApp.

Функции:
1. Определение группового чата (по JID и количеству участников)
2. Извлечение и анализ участников
3. Определение ролей (Admin, Активные, Читатели)
4. Анализ тематики группы
5. Статистика по группам
6. Сравнение групп
7. Экспорт в JSON

Использование:
    python detect_groups.py                      # Анализ всех групп
    python detect_groups.py --chat "Путь/к/chat.txt"  # Анализ одного чата
    python detect_groups.py --export groups.json      # Экспорт в JSON
    python detect_groups.py --compare                 # Сравнение групп
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# Импорт конфигурации
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    CHATS_DIR, ANALYTICS_DIR, RAW_DIR,
    EXPORT_DIRS, CONTACT_TYPES, OPERATION_KEYWORDS,
    MESSAGE_RE, CHAT_HEADER_RE, CHAT_JID_RE,
    ensure_directories, get_export_chat_folders
)


# ================================================================
# КОНСТАНТЫ
# ================================================================

# Паттерн группового JID
GROUP_JID_PATTERN = re.compile(r'.*@g\.us$')

# Паттерн личного JID
PERSONAL_JID_PATTERN = re.compile(r'^\d+@s\.whatsapp\.net$')

# Системные сообщения WhatsApp (определяют админа/создателя)
SYSTEM_MESSAGES = {
    'group_created': [
        r'создал(а)? (эту )?групп',
        r'created (this )?group',
        r'Вы создали эту группу',
        r'You created this group',
    ],
    'admin_added': [
        r'теперь админ',
        r'is now an admin',
        r'назначен(а)? администратор',
    ],
    'user_added': [
        r'добавил(а)?\s+',
        r'added\s+',
        r'присоединил(ся|ась)',
        r'joined',
    ],
    'user_left': [
        r'покинул(а)?\s+групп',
        r'left\s+',
        r'вышел из группы',
    ],
    'name_changed': [
        r'изменил(а)? название группы',
        r'changed the group name',
        r'изменил(а)? тему группы',
    ],
}

# Пороги для ролей участников
ROLE_THRESHOLDS = {
    'active': 0.20,      # >20% сообщений = активный
    'moderate': 0.05,    # 5-20% = умеренно активный
    'reader': 0.01,      # <5% = читатель
    'silent': 0.0,       # 0 = молчун (только читает)
}

# Ключевые слова для определения тематики
TOPIC_KEYWORDS = {
    'туры_экскурсии': [
        'экскурсия', 'тур', 'сафари', 'museum', 'абу-даби', 'дубай',
        'поездка', 'гид', 'маршрут', 'достопримечательност'
    ],
    'трансферы': [
        'трансфер', 'встреча', 'аэропорт', 'transfer', 'pickup',
        'машина', 'водитель', 'driver'
    ],
    'яхты': [
        'яхта', 'yacht', 'катер', 'лодка', 'boat', 'marina',
        'круиз', 'fishing', 'рыбалка'
    ],
    'билеты_парки': [
        'билет', 'парк', 'ferrari', 'aquaventure', 'ticket',
        'аквапарк', 'attraction', 'zoo'
    ],
    'обмен_валюты': [
        'обмен', 'курс', 'дирхам', 'рубл', 'exchange', 'валюта',
        'usdt', 'криптовалют'
    ],
    'аренда_авто': [
        'аренда', 'rental', 'car', 'прокат', 'автомобиль',
        'машина на прокат', 'суперкар'
    ],
    'недвижимость': [
        'квартира', 'апартамент', 'вилла', 'apartment', 'villa',
        'rent', 'снять', 'аренда жилья', 'property'
    ],
    'рестораны_кейтеринг': [
        'ресторан', 'кейтеринг', 'catering', 'food', 'еда',
        'обед', 'ужин', 'банкет'
    ],
    'агентская_работа': [
        'комиссия', 'нетто', 'брутто', 'партнёр', 'агент',
        'турагент', 'туроператор', 'b2b'
    ],
    'общий_чат': [
        'общий', 'general', 'команда', 'team', 'работа',
        'офис', 'коллеги'
    ],
}


# ================================================================
# КЛАСС УЧАСТНИКА ГРУППЫ
# ================================================================

class GroupParticipant:
    """Участник групповой переписки."""

    def __init__(self, name: str):
        self.name = name
        self.messages_count = 0
        self.first_message_date: Optional[datetime] = None
        self.last_message_date: Optional[datetime] = None
        self.voice_messages = 0
        self.photos = 0
        self.links = 0
        self.questions = 0
        self.responses = 0
        self.message_lengths: List[int] = []
        self.active_hours: Counter = Counter()
        self.active_days: Counter = Counter()
        self.role: str = 'reader'
        self.is_admin: bool = False
        self.is_creator: bool = False
        self.joined_date: Optional[datetime] = None
        self.left_date: Optional[datetime] = None
        self.keywords_used: Counter = Counter()

    def add_message(self, date: datetime, text: str):
        """Добавить сообщение участника."""
        self.messages_count += 1

        if self.first_message_date is None or date < self.first_message_date:
            self.first_message_date = date
        if self.last_message_date is None or date > self.last_message_date:
            self.last_message_date = date

        self.active_hours[date.hour] += 1
        self.active_days[date.weekday()] += 1
        self.message_lengths.append(len(text))

        # Анализ контента
        if '?' in text:
            self.questions += 1
        if text.strip().startswith(('да', 'нет', 'ок', 'ok', 'yes', 'no', 'хорошо', 'понял')):
            self.responses += 1
        if re.search(r'https?://', text):
            self.links += 1
        if '[ГОЛОС]' in text or 'PTT-' in text or '.opus' in text:
            self.voice_messages += 1
        if '[ФОТО]' in text or 'IMG-' in text or '.jpg' in text:
            self.photos += 1

    @property
    def avg_message_length(self) -> float:
        """Средняя длина сообщения."""
        if not self.message_lengths:
            return 0
        return sum(self.message_lengths) / len(self.message_lengths)

    @property
    def days_active(self) -> int:
        """Количество дней активности."""
        if not self.first_message_date or not self.last_message_date:
            return 0
        return (self.last_message_date - self.first_message_date).days + 1

    @property
    def peak_hour(self) -> Optional[int]:
        """Пиковый час активности."""
        if not self.active_hours:
            return None
        return self.active_hours.most_common(1)[0][0]

    def to_dict(self) -> dict:
        """Сериализация в словарь."""
        return {
            'name': self.name,
            'messages_count': self.messages_count,
            'first_message': self.first_message_date.isoformat() if self.first_message_date else None,
            'last_message': self.last_message_date.isoformat() if self.last_message_date else None,
            'voice_messages': self.voice_messages,
            'photos': self.photos,
            'links': self.links,
            'questions': self.questions,
            'responses': self.responses,
            'avg_message_length': round(self.avg_message_length, 1),
            'days_active': self.days_active,
            'peak_hour': self.peak_hour,
            'role': self.role,
            'is_admin': self.is_admin,
            'is_creator': self.is_creator,
            'activity_by_hour': dict(self.active_hours),
            'activity_by_day': dict(self.active_days),
        }


# ================================================================
# КЛАСС ГРУППОВОГО ЧАТА
# ================================================================

class GroupChat:
    """Групповой чат WhatsApp."""

    def __init__(self, name: str, jid: str = '', source: str = '', file_path: str = ''):
        self.name = name
        self.jid = jid
        self.source = source
        self.file_path = file_path
        self.participants: Dict[str, GroupParticipant] = {}
        self.total_messages = 0
        self.first_message_date: Optional[datetime] = None
        self.last_message_date: Optional[datetime] = None
        self.topics_detected: List[str] = []
        self.topic_scores: Dict[str, int] = {}
        self.creator_name: Optional[str] = None
        self.admins: List[str] = []
        self.message_by_date: Counter = Counter()
        self.is_group: bool = False
        self.detection_method: str = ''

    def add_participant(self, name: str) -> GroupParticipant:
        """Добавить или получить участника."""
        if name not in self.participants:
            self.participants[name] = GroupParticipant(name)
        return self.participants[name]

    def add_message(self, sender: str, date: datetime, text: str):
        """Добавить сообщение в группу."""
        self.total_messages += 1
        participant = self.add_participant(sender)
        participant.add_message(date, text)

        if self.first_message_date is None or date < self.first_message_date:
            self.first_message_date = date
        if self.last_message_date is None or date > self.last_message_date:
            self.last_message_date = date

        date_key = date.strftime('%Y-%m-%d')
        self.message_by_date[date_key] += 1

    def detect_is_group(self) -> bool:
        """Определить, является ли чат групповым."""
        # Метод 1: По JID
        if self.jid and GROUP_JID_PATTERN.match(self.jid):
            self.is_group = True
            self.detection_method = 'jid_pattern'
            return True

        # Метод 2: По количеству участников
        # Исключаем системные сообщения и "Я"
        real_participants = [
            p for p in self.participants.values()
            if p.name not in ('Я', 'You', 'System') and p.messages_count > 0
        ]

        if len(real_participants) > 2:
            self.is_group = True
            self.detection_method = 'participant_count'
            return True

        # Метод 3: Системные сообщения о группе
        for participant in self.participants.values():
            if any(re.search(pattern, participant.name, re.IGNORECASE)
                   for patterns in SYSTEM_MESSAGES.values()
                   for pattern in patterns):
                self.is_group = True
                self.detection_method = 'system_messages'
                return True

        self.is_group = False
        self.detection_method = 'not_a_group'
        return False

    def calculate_roles(self):
        """Рассчитать роли участников."""
        if self.total_messages == 0:
            return

        for participant in self.participants.values():
            ratio = participant.messages_count / self.total_messages

            if ratio >= ROLE_THRESHOLDS['active']:
                participant.role = 'active'
            elif ratio >= ROLE_THRESHOLDS['moderate']:
                participant.role = 'moderate'
            elif ratio > ROLE_THRESHOLDS['silent']:
                participant.role = 'reader'
            else:
                participant.role = 'silent'

    def detect_admins_and_creator(self, raw_content: str = ''):
        """Определить администраторов и создателя группы."""
        # Ищем системные сообщения о создании группы
        for pattern in SYSTEM_MESSAGES['group_created']:
            matches = re.finditer(
                rf'\[.*?\] ([^:]+):\s*.*{pattern}',
                raw_content, re.IGNORECASE | re.MULTILINE
            )
            for match in matches:
                name = match.group(1).strip()
                if name in self.participants:
                    self.participants[name].is_creator = True
                    self.participants[name].is_admin = True
                    self.creator_name = name
                    if name not in self.admins:
                        self.admins.append(name)

        # Ищем назначение админов
        for pattern in SYSTEM_MESSAGES['admin_added']:
            matches = re.finditer(
                rf'([^\[\]]+)\s+{pattern}',
                raw_content, re.IGNORECASE
            )
            for match in matches:
                name = match.group(1).strip()
                if name in self.participants:
                    self.participants[name].is_admin = True
                    if name not in self.admins:
                        self.admins.append(name)

        # Если создатель не найден - предполагаем первого отправителя
        if not self.creator_name and self.participants:
            earliest = min(
                self.participants.values(),
                key=lambda p: p.first_message_date or datetime.max
            )
            if earliest.first_message_date:
                self.creator_name = earliest.name
                earliest.is_creator = True
                earliest.is_admin = True
                if earliest.name not in self.admins:
                    self.admins.append(earliest.name)

    def detect_topics(self, raw_content: str = ''):
        """Определить тематику группы."""
        content_lower = raw_content.lower() if raw_content else ''

        # Также учитываем название группы
        name_lower = self.name.lower()

        for topic, keywords in TOPIC_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Вес от названия группы (x5)
                if keyword.lower() in name_lower:
                    score += 5
                # Вес от контента
                count = content_lower.count(keyword.lower())
                score += min(count, 10)  # Максимум 10 вхождений учитываем

            if score > 0:
                self.topic_scores[topic] = score

        # Сортируем по релевантности
        sorted_topics = sorted(
            self.topic_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Берём топ-3 темы с минимальным порогом
        self.topics_detected = [
            topic for topic, score in sorted_topics[:3]
            if score >= 3
        ]

        if not self.topics_detected:
            self.topics_detected = ['общий_чат']

    @property
    def participant_count(self) -> int:
        """Количество участников."""
        return len([p for p in self.participants.values() if p.messages_count > 0])

    @property
    def active_participants(self) -> List[GroupParticipant]:
        """Активные участники."""
        return [p for p in self.participants.values() if p.role == 'active']

    @property
    def readers(self) -> List[GroupParticipant]:
        """Читатели."""
        return [p for p in self.participants.values() if p.role in ('reader', 'silent')]

    @property
    def duration_days(self) -> int:
        """Продолжительность чата в днях."""
        if not self.first_message_date or not self.last_message_date:
            return 0
        return (self.last_message_date - self.first_message_date).days + 1

    @property
    def avg_messages_per_day(self) -> float:
        """Среднее количество сообщений в день."""
        if self.duration_days == 0:
            return 0
        return self.total_messages / self.duration_days

    @property
    def most_active_day(self) -> Optional[str]:
        """Самый активный день."""
        if not self.message_by_date:
            return None
        return self.message_by_date.most_common(1)[0][0]

    def get_activity_distribution(self) -> Dict[str, float]:
        """Распределение активности по участникам."""
        if self.total_messages == 0:
            return {}

        return {
            name: round(p.messages_count / self.total_messages * 100, 1)
            for name, p in sorted(
                self.participants.items(),
                key=lambda x: x[1].messages_count,
                reverse=True
            )
        }

    def to_dict(self) -> dict:
        """Сериализация в словарь."""
        return {
            'name': self.name,
            'jid': self.jid,
            'source': self.source,
            'file_path': self.file_path,
            'is_group': self.is_group,
            'detection_method': self.detection_method,
            'participant_count': self.participant_count,
            'total_messages': self.total_messages,
            'first_message': self.first_message_date.isoformat() if self.first_message_date else None,
            'last_message': self.last_message_date.isoformat() if self.last_message_date else None,
            'duration_days': self.duration_days,
            'avg_messages_per_day': round(self.avg_messages_per_day, 1),
            'most_active_day': self.most_active_day,
            'topics': self.topics_detected,
            'topic_scores': self.topic_scores,
            'creator': self.creator_name,
            'admins': self.admins,
            'participants': {
                name: p.to_dict()
                for name, p in sorted(
                    self.participants.items(),
                    key=lambda x: x[1].messages_count,
                    reverse=True
                )
            },
            'activity_distribution': self.get_activity_distribution(),
            'roles_summary': {
                'active': len(self.active_participants),
                'moderate': len([p for p in self.participants.values() if p.role == 'moderate']),
                'readers': len(self.readers),
            },
        }


# ================================================================
# ФУНКЦИИ ПАРСИНГА
# ================================================================

def parse_chat_file(file_path: Path) -> Optional[GroupChat]:
    """
    Парсит файл чата и возвращает объект GroupChat.

    Args:
        file_path: Путь к файлу chat.txt

    Returns:
        GroupChat или None при ошибке
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = file_path.read_text(encoding='utf-8-sig')
        except Exception as e:
            print(f"[ОШИБКА] Не удалось прочитать {file_path}: {e}")
            return None

    # Извлекаем метаданные
    name_match = CHAT_HEADER_RE.search(content)
    jid_match = CHAT_JID_RE.search(content)

    chat_name = name_match.group(1).strip() if name_match else file_path.parent.name
    jid = jid_match.group(1).strip() if jid_match else ''

    # Определяем источник
    source = 'whatsapp'
    if 'бизнес' in str(file_path).lower():
        source = 'wa_business'

    group = GroupChat(
        name=chat_name,
        jid=jid,
        source=source,
        file_path=str(file_path)
    )

    # Парсим сообщения
    for line in content.split('\n'):
        msg_match = MESSAGE_RE.match(line)
        if msg_match:
            date_str = msg_match.group(1)
            time_str = msg_match.group(2)
            sender = msg_match.group(3).strip()

            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")
            except ValueError:
                continue

            # Читаем текст сообщения (следующие строки с отступом)
            # Упрощённая версия - берём только эту строку
            text = ''

        elif line.startswith('  ') and group.participants:
            # Текст сообщения с отступом
            text = line.strip()
            if text and group.participants:
                # Добавляем к последнему отправителю
                last_sender = list(group.participants.keys())[-1]
                # Пересоздаём add_message с текстом
                pass

    # Более надёжный парсинг - читаем заново
    current_sender = None
    current_date = None
    current_text_lines = []

    def save_message():
        nonlocal current_sender, current_date, current_text_lines
        if current_sender and current_date:
            text = '\n'.join(current_text_lines)
            group.add_message(current_sender, current_date, text)
        current_text_lines = []

    for line in content.split('\n'):
        msg_match = MESSAGE_RE.match(line)
        if msg_match:
            # Сохраняем предыдущее сообщение
            save_message()

            date_str = msg_match.group(1)
            time_str = msg_match.group(2)
            current_sender = msg_match.group(3).strip()

            try:
                current_date = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")
            except ValueError:
                current_sender = None
                current_date = None

        elif line.startswith('  ') and current_sender:
            current_text_lines.append(line[2:])

        elif line.strip() and not line.startswith('ЧАТ:') and not line.startswith('JID:') \
             and not line.startswith('Сообщений:') and not line.startswith('Экспорт:') \
             and not line.startswith('='):
            if current_sender:
                current_text_lines.append(line.strip())

    # Сохраняем последнее сообщение
    save_message()

    # Определяем тип чата
    group.detect_is_group()

    # Рассчитываем роли
    group.calculate_roles()

    # Определяем админов и создателя
    group.detect_admins_and_creator(content)

    # Определяем тематику
    group.detect_topics(content)

    return group


def scan_all_groups(export_dirs: List[Path] = None) -> List[GroupChat]:
    """
    Сканирует все экспортированные чаты и находит группы.

    Args:
        export_dirs: Список директорий для сканирования

    Returns:
        Список объектов GroupChat для групповых чатов
    """
    if export_dirs is None:
        export_dirs = EXPORT_DIRS

    groups = []
    total_chats = 0

    for export_dir in export_dirs:
        if not export_dir.exists():
            print(f"[ПРОПУСК] Директория не существует: {export_dir}")
            continue

        for chat_folder in export_dir.iterdir():
            if not chat_folder.is_dir():
                continue

            chat_file = chat_folder / "chat.txt"
            if not chat_file.exists():
                continue

            total_chats += 1

            group = parse_chat_file(chat_file)
            if group and group.is_group:
                groups.append(group)

    print(f"Просканировано чатов: {total_chats}")
    print(f"Найдено групп: {len(groups)}")

    return groups


# ================================================================
# АНАЛИЗ И СРАВНЕНИЕ
# ================================================================

def compare_groups(groups: List[GroupChat]) -> Dict:
    """
    Сравнительный анализ групп.

    Args:
        groups: Список групповых чатов

    Returns:
        Словарь со сравнительной аналитикой
    """
    if not groups:
        return {'error': 'Нет групп для сравнения'}

    comparison = {
        'total_groups': len(groups),
        'total_participants_unique': len(set(
            p.name for g in groups for p in g.participants.values()
        )),
        'total_messages': sum(g.total_messages for g in groups),
        'by_size': {
            'largest': max(groups, key=lambda g: g.participant_count).name,
            'smallest': min(groups, key=lambda g: g.participant_count).name,
            'avg_participants': round(
                sum(g.participant_count for g in groups) / len(groups), 1
            ),
        },
        'by_activity': {
            'most_active': max(groups, key=lambda g: g.total_messages).name,
            'least_active': min(groups, key=lambda g: g.total_messages).name,
            'avg_messages_per_group': round(
                sum(g.total_messages for g in groups) / len(groups), 1
            ),
        },
        'by_topic': defaultdict(list),
        'groups_ranked': [],
    }

    # Группировка по тематике
    for group in groups:
        for topic in group.topics_detected:
            comparison['by_topic'][topic].append({
                'name': group.name,
                'messages': group.total_messages,
                'participants': group.participant_count,
            })

    # Рейтинг групп
    comparison['groups_ranked'] = [
        {
            'name': g.name,
            'participants': g.participant_count,
            'messages': g.total_messages,
            'duration_days': g.duration_days,
            'avg_per_day': round(g.avg_messages_per_day, 1),
            'topics': g.topics_detected,
            'score': round(
                g.total_messages * 0.5 +
                g.participant_count * 10 +
                min(g.duration_days, 365) * 0.2,
                1
            ),
        }
        for g in sorted(groups, key=lambda x: x.total_messages, reverse=True)
    ]

    return comparison


def generate_group_report(group: GroupChat) -> str:
    """
    Генерирует текстовый отчёт по группе.

    Args:
        group: Объект GroupChat

    Returns:
        Markdown отчёт
    """
    lines = [
        f"# Анализ группы: {group.name}",
        "",
        f"*Создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}*",
        "",
        "---",
        "",
        "## Основная информация",
        "",
        f"| Параметр | Значение |",
        f"|----------|----------|",
        f"| JID | `{group.jid}` |",
        f"| Источник | {group.source} |",
        f"| Участников | {group.participant_count} |",
        f"| Сообщений | {group.total_messages:,} |",
        f"| Период | {group.first_message_date.strftime('%d.%m.%Y') if group.first_message_date else 'N/A'} — "
        f"{group.last_message_date.strftime('%d.%m.%Y') if group.last_message_date else 'N/A'} |",
        f"| Длительность | {group.duration_days} дней |",
        f"| Сообщ./день | {group.avg_messages_per_day:.1f} |",
        "",
        "---",
        "",
        "## Тематика",
        "",
    ]

    for topic in group.topics_detected:
        score = group.topic_scores.get(topic, 0)
        lines.append(f"- **{topic}** (релевантность: {score})")

    lines.extend([
        "",
        "---",
        "",
        "## Участники и роли",
        "",
        f"- **Создатель:** {group.creator_name or 'Не определён'}",
        f"- **Администраторы:** {', '.join(group.admins) or 'Не определены'}",
        "",
        "### Распределение активности",
        "",
        "| Участник | Сообщений | Доля | Роль |",
        "|----------|-----------|------|------|",
    ])

    for name, participant in sorted(
        group.participants.items(),
        key=lambda x: x[1].messages_count,
        reverse=True
    ):
        share = participant.messages_count / group.total_messages * 100 if group.total_messages > 0 else 0
        role_emoji = {
            'active': '🔥',
            'moderate': '👍',
            'reader': '👀',
            'silent': '🤫',
        }.get(participant.role, '')

        admin_mark = ' [Admin]' if participant.is_admin else ''
        creator_mark = ' [Creator]' if participant.is_creator else ''

        lines.append(
            f"| {name}{creator_mark}{admin_mark} | {participant.messages_count} | "
            f"{share:.1f}% | {role_emoji} {participant.role} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Статистика по ролям",
        "",
        f"- **Активные** (>20% сообщений): {len(group.active_participants)}",
        f"- **Умеренно активные** (5-20%): {len([p for p in group.participants.values() if p.role == 'moderate'])}",
        f"- **Читатели** (<5%): {len(group.readers)}",
        "",
    ])

    return '\n'.join(lines)


# ================================================================
# ЭКСПОРТ
# ================================================================

def export_groups_to_json(groups: List[GroupChat], output_path: Path) -> Path:
    """
    Экспортирует группы в JSON файл.

    Args:
        groups: Список групповых чатов
        output_path: Путь к выходному файлу

    Returns:
        Путь к созданному файлу
    """
    data = {
        'generated_at': datetime.now().isoformat(),
        'total_groups': len(groups),
        'groups': [g.to_dict() for g in groups],
        'comparison': compare_groups(groups),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path


# ================================================================
# CLI
# ================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Детекция и анализ групповых чатов WhatsApp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python detect_groups.py                        # Сканировать все чаты
  python detect_groups.py --chat path/chat.txt  # Анализ одного чата
  python detect_groups.py --export groups.json  # Экспорт в JSON
  python detect_groups.py --compare             # Сравнить группы
  python detect_groups.py --report "Название"   # Отчёт по группе
        """
    )

    parser.add_argument('--chat', type=Path, help='Путь к конкретному файлу chat.txt')
    parser.add_argument('--export', type=Path, help='Экспортировать результаты в JSON')
    parser.add_argument('--compare', action='store_true', help='Показать сравнительный анализ')
    parser.add_argument('--report', type=str, help='Сгенерировать отчёт по группе (имя)')
    parser.add_argument('--list', action='store_true', help='Список всех групп')
    parser.add_argument('--json', action='store_true', help='Вывод в формате JSON')
    parser.add_argument('-o', '--output', type=Path, help='Путь к выходному файлу')

    args = parser.parse_args()

    ensure_directories()

    # Анализ одного чата
    if args.chat:
        if not args.chat.exists():
            print(f"[ОШИБКА] Файл не найден: {args.chat}")
            sys.exit(1)

        group = parse_chat_file(args.chat)
        if not group:
            print("[ОШИБКА] Не удалось распарсить чат")
            sys.exit(1)

        if args.json:
            print(json.dumps(group.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"\nЧат: {group.name}")
            print(f"Тип: {'Групповой' if group.is_group else 'Личный'} ({group.detection_method})")
            print(f"Участников: {group.participant_count}")
            print(f"Сообщений: {group.total_messages}")
            print(f"Темы: {', '.join(group.topics_detected)}")

            if group.is_group:
                print(f"\nСоздатель: {group.creator_name or 'Не определён'}")
                print(f"Админы: {', '.join(group.admins) or 'Нет'}")
                print(f"\nУчастники по активности:")
                for name, p in sorted(
                    group.participants.items(),
                    key=lambda x: x[1].messages_count,
                    reverse=True
                )[:10]:
                    print(f"  - {name}: {p.messages_count} сообщ. ({p.role})")

        return

    # Сканирование всех групп
    print("Сканирование экспортированных чатов...")
    groups = scan_all_groups()

    if not groups:
        print("Групповые чаты не найдены")
        sys.exit(0)

    # Список групп
    if args.list:
        print(f"\n{'='*60}")
        print(f"НАЙДЕНО ГРУПП: {len(groups)}")
        print('='*60)

        for i, g in enumerate(sorted(groups, key=lambda x: x.total_messages, reverse=True), 1):
            print(f"\n{i}. {g.name}")
            print(f"   Участников: {g.participant_count} | Сообщений: {g.total_messages:,}")
            print(f"   Темы: {', '.join(g.topics_detected[:2])}")
        return

    # Экспорт в JSON
    if args.export:
        output_path = export_groups_to_json(groups, args.export)
        print(f"\nЭкспортировано в: {output_path}")
        return

    # Сравнительный анализ
    if args.compare:
        comparison = compare_groups(groups)

        if args.json:
            print(json.dumps(comparison, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ ГРУПП")
            print('='*60)
            print(f"\nВсего групп: {comparison['total_groups']}")
            print(f"Всего уникальных участников: {comparison['total_participants_unique']}")
            print(f"Всего сообщений: {comparison['total_messages']:,}")

            print(f"\n--- По размеру ---")
            print(f"Самая большая: {comparison['by_size']['largest']}")
            print(f"Самая маленькая: {comparison['by_size']['smallest']}")
            print(f"Среднее участников: {comparison['by_size']['avg_participants']}")

            print(f"\n--- По активности ---")
            print(f"Самая активная: {comparison['by_activity']['most_active']}")
            print(f"Наименее активная: {comparison['by_activity']['least_active']}")

            print(f"\n--- Топ-5 групп ---")
            for i, g in enumerate(comparison['groups_ranked'][:5], 1):
                print(f"{i}. {g['name']} ({g['messages']:,} сообщ., {g['participants']} участн.)")
        return

    # Отчёт по конкретной группе
    if args.report:
        target_group = None
        for g in groups:
            if args.report.lower() in g.name.lower():
                target_group = g
                break

        if not target_group:
            print(f"Группа '{args.report}' не найдена")
            print("Доступные группы:")
            for g in groups[:10]:
                print(f"  - {g.name}")
            sys.exit(1)

        report = generate_group_report(target_group)

        if args.output:
            args.output.write_text(report, encoding='utf-8')
            print(f"Отчёт сохранён: {args.output}")
        else:
            print(report)
        return

    # По умолчанию - краткая сводка
    default_output = ANALYTICS_DIR / f"groups_{datetime.now().strftime('%Y-%m-%d')}.json"
    export_groups_to_json(groups, default_output)

    print(f"\n{'='*60}")
    print("СВОДКА ПО ГРУППОВЫМ ЧАТАМ")
    print('='*60)
    print(f"\nНайдено групп: {len(groups)}")
    print(f"Экспорт: {default_output}")

    print(f"\n--- Топ-5 по активности ---")
    for i, g in enumerate(sorted(groups, key=lambda x: x.total_messages, reverse=True)[:5], 1):
        print(f"{i}. {g.name}")
        print(f"   {g.participant_count} участн. | {g.total_messages:,} сообщ. | {', '.join(g.topics_detected[:2])}")


if __name__ == "__main__":
    main()
