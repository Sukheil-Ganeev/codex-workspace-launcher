#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф связей контактов WhatsApp.

Функции:
1. Построение графа связей (узлы = контакты, рёбра = взаимодействия)
2. Типы связей: пересылки, упоминания, общие группы, рефералы, VCF
3. Метрики: degree centrality, betweenness, PageRank, кластеры
4. Визуализация: NetworkX + Pyvis (интерактивный HTML)
5. Поиск influencers (ключевых фигур)
6. Экспорт: GEXF, JSON, HTML

Использование:
    # Построить граф
    python contact_graph.py --build

    # Найти influencers
    python contact_graph.py --influencers --top 20

    # Интерактивный HTML
    python contact_graph.py --html --output graph.html

    # Анализ конкретного контакта
    python contact_graph.py --analyze --phone +971501234567

    # Экспорт в GEXF (для Gephi)
    python contact_graph.py --export-gexf --output contacts.gexf

    # Поиск кластеров
    python contact_graph.py --clusters --min-size 3
"""

import sys
import os
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict

# Добавляем путь к скриптам
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import JSON_DIR, RAW_DIR, ANALYTICS_DIR, BASE_DIR, ensure_directories

# Настройка кодировки
sys.stdout.reconfigure(encoding='utf-8')

# Опциональные импорты
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("[!] networkx не установлен. pip install networkx")

try:
    from pyvis.network import Network
    HAS_PYVIS = True
except ImportError:
    HAS_PYVIS = False
    print("[!] pyvis не установлен. pip install pyvis")

try:
    from community import community_louvain
    HAS_COMMUNITY = True
except ImportError:
    HAS_COMMUNITY = False
    print("[i] python-louvain не установлен (для кластеризации). pip install python-louvain")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

# Файлы данных
CONTACTS_FILE = JSON_DIR / "contacts.json"
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
REFERRALS_FILE = JSON_DIR / "referrals.json"
GROUPS_FILE = JSON_DIR / "groups.json"

# Выходные файлы
OUTPUT_DIR = ANALYTICS_DIR / "graph"
GRAPH_JSON = OUTPUT_DIR / "contact_graph.json"
GRAPH_GEXF = OUTPUT_DIR / "contact_graph.gexf"
GRAPH_HTML = OUTPUT_DIR / "contact_graph.html"
INFLUENCERS_JSON = OUTPUT_DIR / "influencers.json"
CLUSTERS_JSON = OUTPUT_DIR / "clusters.json"

# Цвета для типов контактов
NODE_COLORS = {
    "клиенты": "#4CAF50",       # Зеленый
    "агенты": "#2196F3",        # Синий
    "поставщики": "#FF9800",    # Оранжевый
    "сотрудники": "#9C27B0",    # Фиолетовый
    "группы": "#607D8B",        # Серый
    "unknown": "#9E9E9E",       # Серый светлый
}

# Цвета для типов связей
EDGE_COLORS = {
    "forward": "#F44336",       # Красный - пересылки
    "mention": "#FF9800",       # Оранжевый - упоминания
    "group": "#9E9E9E",         # Серый - общие группы
    "referral": "#4CAF50",      # Зеленый - рефералы
    "vcf": "#2196F3",           # Синий - VCF карточки
    "reply": "#795548",         # Коричневый - ответы
}

# Паттерны для поиска упоминаний
MENTION_PATTERNS = [
    r'@([A-Za-zА-ЯЁа-яё][A-Za-zА-ЯЁа-яё0-9_]{2,30})',  # @username
    r'от\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',      # от Ивана / от Ивана Петрова
    r'([А-ЯЁ][а-яё]+)\s+(?:рекомендовал|посоветовал|направил)',  # Иван рекомендовал
]


# ═══════════════════════════════════════════════════════════════════════════════
# КЛАССЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContactNode:
    """Узел графа - контакт."""
    id: str
    name: str
    phone: Optional[str] = None
    contact_type: str = "unknown"
    is_group: bool = False
    message_count: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

    # Метрики (заполняются после построения графа)
    degree: int = 0
    in_degree: int = 0
    out_degree: int = 0
    betweenness: float = 0.0
    pagerank: float = 0.0
    cluster_id: int = -1

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContactEdge:
    """Ребро графа - связь между контактами."""
    source: str
    target: str
    edge_type: str  # forward, mention, group, referral, vcf, reply
    weight: int = 1
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

    # Детали связи
    messages: List[str] = field(default_factory=list)  # ID сообщений

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['messages'] = len(self.messages)  # Только количество для экспорта
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# КЛАСС ГРАФА КОНТАКТОВ
# ═══════════════════════════════════════════════════════════════════════════════

class ContactGraph:
    """Граф связей контактов WhatsApp."""

    def __init__(self):
        """Инициализация графа."""
        if not HAS_NETWORKX:
            raise ImportError("networkx не установлен. pip install networkx")

        self.graph = nx.DiGraph()  # Направленный граф
        self.nodes: Dict[str, ContactNode] = {}
        self.edges: Dict[Tuple[str, str, str], ContactEdge] = {}  # (source, target, type) -> edge

        # Индексы для быстрого поиска
        self.phone_to_id: Dict[str, str] = {}
        self.name_to_ids: Dict[str, List[str]] = defaultdict(list)
        self.group_members: Dict[str, Set[str]] = defaultdict(set)  # group_id -> member_ids

        # Данные
        self.contacts: List[Dict] = []
        self.messages: List[Dict] = []
        self.referrals: List[Dict] = []

        logger.info("ContactGraph инициализирован")

    # ═══════════════════════════════════════════════════════════════════════════
    # ЗАГРУЗКА ДАННЫХ
    # ═══════════════════════════════════════════════════════════════════════════

    def load_contacts(self, filepath: Path = CONTACTS_FILE) -> int:
        """Загрузка контактов из JSON."""
        if not filepath.exists():
            logger.warning(f"Файл контактов не найден: {filepath}")
            return 0

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        contacts = data.get('contacts', data) if isinstance(data, dict) else data
        self.contacts = contacts

        for contact in contacts:
            contact_id = contact.get('id') or contact.get('jid') or contact.get('contact_id')
            if not contact_id:
                continue

            name = contact.get('name') or contact.get('display_name') or contact_id
            phone = contact.get('phone') or self._extract_phone_from_jid(contact_id)
            contact_type = contact.get('type') or contact.get('contact_type') or 'unknown'
            is_group = '@g.us' in str(contact_id) or contact.get('is_group', False)

            node = ContactNode(
                id=contact_id,
                name=name,
                phone=phone,
                contact_type=contact_type,
                is_group=is_group,
                message_count=contact.get('message_count', 0),
                first_seen=contact.get('first_seen'),
                last_seen=contact.get('last_seen'),
            )

            self.nodes[contact_id] = node

            if phone:
                self.phone_to_id[phone] = contact_id

            # Индекс по именам (для поиска упоминаний)
            name_lower = name.lower()
            self.name_to_ids[name_lower].append(contact_id)

            # Также добавляем первое слово имени (для "от Ивана")
            first_name = name.split()[0].lower() if name else ""
            if first_name and first_name != name_lower:
                self.name_to_ids[first_name].append(contact_id)

        logger.info(f"Загружено {len(self.nodes)} контактов")
        return len(self.nodes)

    def load_messages(self, filepath: Path = MESSAGES_FILE, limit: int = 0) -> int:
        """Загрузка сообщений из JSONL."""
        if not filepath.exists():
            logger.warning(f"Файл сообщений не найден: {filepath}")
            return 0

        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if limit and count >= limit:
                    break
                try:
                    msg = json.loads(line.strip())
                    self.messages.append(msg)
                    count += 1
                except json.JSONDecodeError:
                    continue

        logger.info(f"Загружено {count} сообщений")
        return count

    def load_referrals(self, filepath: Path = REFERRALS_FILE) -> int:
        """Загрузка реферальных связей."""
        if not filepath.exists():
            logger.info("Файл рефералов не найден (опционально)")
            return 0

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.referrals = data.get('referrals', data) if isinstance(data, dict) else data
        logger.info(f"Загружено {len(self.referrals)} рефералов")
        return len(self.referrals)

    def _extract_phone_from_jid(self, jid: str) -> Optional[str]:
        """Извлечение номера телефона из JID."""
        if not jid or '@' not in jid:
            return None
        phone = jid.split('@')[0]
        if phone.isdigit() and len(phone) >= 10:
            return f"+{phone}"
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # ПОСТРОЕНИЕ ГРАФА
    # ═══════════════════════════════════════════════════════════════════════════

    def build_graph(self):
        """Построение графа из загруженных данных."""
        logger.info("Построение графа...")

        # 1. Добавляем узлы
        for node_id, node in self.nodes.items():
            self.graph.add_node(
                node_id,
                label=node.name,
                phone=node.phone,
                type=node.contact_type,
                is_group=node.is_group,
                messages=node.message_count,
            )

        # 2. Анализируем сообщения и строим рёбра
        self._build_edges_from_messages()

        # 3. Добавляем реферальные связи
        self._build_referral_edges()

        # 4. Строим связи по общим группам
        self._build_group_edges()

        # 5. Вычисляем метрики
        self._calculate_metrics()

        logger.info(f"Граф построен: {self.graph.number_of_nodes()} узлов, {self.graph.number_of_edges()} рёбер")

    def _build_edges_from_messages(self):
        """Построение рёбер из сообщений."""
        logger.info("Анализ сообщений для построения рёбер...")

        # Группируем сообщения по чатам
        chats: Dict[str, List[Dict]] = defaultdict(list)
        for msg in self.messages:
            chat_id = msg.get('chat_id') or msg.get('jid')
            if chat_id:
                chats[chat_id].append(msg)

        for chat_id, messages in chats.items():
            # Если это группа - добавляем участников
            is_group = '@g.us' in str(chat_id)

            for msg in messages:
                sender = msg.get('sender') or msg.get('from')
                if not sender:
                    continue

                # Добавляем отправителя как узел если его нет
                self._ensure_node(sender, msg)

                if is_group:
                    # Добавляем в участники группы
                    self.group_members[chat_id].add(sender)

                # 1. Проверяем пересылки
                if msg.get('is_forwarded') or msg.get('forwarded'):
                    forwarded_from = msg.get('forwarded_from') or msg.get('forward_from')
                    if forwarded_from:
                        self._ensure_node(forwarded_from, msg)
                        self._add_edge(forwarded_from, sender, 'forward', msg)

                # 2. Проверяем ответы (replies)
                reply_to = msg.get('reply_to') or msg.get('quoted_message_sender')
                if reply_to:
                    self._ensure_node(reply_to, msg)
                    self._add_edge(sender, reply_to, 'reply', msg)

                # 3. Проверяем VCF (отправка контакта)
                if msg.get('type') == 'vcard' or msg.get('has_vcard'):
                    vcard_phone = self._extract_vcard_phone(msg)
                    if vcard_phone and vcard_phone in self.phone_to_id:
                        vcf_contact_id = self.phone_to_id[vcard_phone]
                        self._add_edge(sender, vcf_contact_id, 'vcf', msg)

                # 4. Поиск упоминаний в тексте
                text = msg.get('text') or msg.get('body') or ''
                mentioned_ids = self._find_mentions(text)
                for mentioned_id in mentioned_ids:
                    if mentioned_id != sender:
                        self._add_edge(sender, mentioned_id, 'mention', msg)

    def _build_referral_edges(self):
        """Построение рёбер из реферальных связей."""
        for ref in self.referrals:
            referrer = ref.get('referrer_phone') or ref.get('referrer_id')
            referred = ref.get('referred_phone') or ref.get('referred_id')

            if referrer and referred:
                referrer_id = self.phone_to_id.get(referrer, referrer)
                referred_id = self.phone_to_id.get(referred, referred)

                self._ensure_node(referrer_id)
                self._ensure_node(referred_id)

                self._add_edge(referrer_id, referred_id, 'referral')

    def _build_group_edges(self):
        """Построение рёбер для участников общих групп."""
        logger.info("Построение связей по общим группам...")

        for group_id, members in self.group_members.items():
            members_list = list(members)

            # Связываем всех участников группы между собой
            for i, member1 in enumerate(members_list):
                for member2 in members_list[i+1:]:
                    # Добавляем двунаправленную связь (оба в одной группе)
                    self._add_edge(member1, member2, 'group')
                    self._add_edge(member2, member1, 'group')

    def _ensure_node(self, node_id: str, msg: Optional[Dict] = None):
        """Добавление узла если его нет."""
        if node_id not in self.nodes:
            phone = self._extract_phone_from_jid(node_id)
            is_group = '@g.us' in str(node_id)

            node = ContactNode(
                id=node_id,
                name=msg.get('sender_name', node_id) if msg else node_id,
                phone=phone,
                contact_type='группы' if is_group else 'unknown',
                is_group=is_group,
            )
            self.nodes[node_id] = node

            self.graph.add_node(
                node_id,
                label=node.name,
                phone=phone,
                type=node.contact_type,
                is_group=is_group,
            )

            if phone:
                self.phone_to_id[phone] = node_id

    def _add_edge(self, source: str, target: str, edge_type: str, msg: Optional[Dict] = None):
        """Добавление или обновление ребра."""
        edge_key = (source, target, edge_type)

        if edge_key in self.edges:
            # Обновляем существующее ребро
            edge = self.edges[edge_key]
            edge.weight += 1
            if msg:
                msg_id = msg.get('id') or msg.get('message_id')
                if msg_id:
                    edge.messages.append(msg_id)

                msg_date = msg.get('timestamp') or msg.get('date')
                if msg_date:
                    if not edge.first_seen or msg_date < edge.first_seen:
                        edge.first_seen = msg_date
                    if not edge.last_seen or msg_date > edge.last_seen:
                        edge.last_seen = msg_date
        else:
            # Создаём новое ребро
            edge = ContactEdge(
                source=source,
                target=target,
                edge_type=edge_type,
                weight=1,
            )

            if msg:
                msg_id = msg.get('id') or msg.get('message_id')
                if msg_id:
                    edge.messages.append(msg_id)
                edge.first_seen = msg.get('timestamp') or msg.get('date')
                edge.last_seen = edge.first_seen

            self.edges[edge_key] = edge

        # Обновляем NetworkX граф
        if self.graph.has_edge(source, target):
            # Увеличиваем вес
            self.graph[source][target]['weight'] = self.graph[source][target].get('weight', 0) + 1
            # Добавляем тип связи
            types = self.graph[source][target].get('types', set())
            types.add(edge_type)
            self.graph[source][target]['types'] = types
        else:
            self.graph.add_edge(
                source, target,
                weight=1,
                types={edge_type},
                color=EDGE_COLORS.get(edge_type, '#999999'),
            )

    def _find_mentions(self, text: str) -> List[str]:
        """Поиск упоминаний контактов в тексте."""
        mentioned_ids = []

        for pattern in MENTION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match_lower = match.lower().strip()

                # Ищем в индексе имён
                if match_lower in self.name_to_ids:
                    mentioned_ids.extend(self.name_to_ids[match_lower])

        return list(set(mentioned_ids))

    def _extract_vcard_phone(self, msg: Dict) -> Optional[str]:
        """Извлечение телефона из VCF карточки."""
        vcard = msg.get('vcard') or msg.get('vcard_data') or ''

        # Ищем номер телефона в формате TEL:+XXX...
        tel_match = re.search(r'TEL[^:]*:([+\d\s-]+)', vcard, re.IGNORECASE)
        if tel_match:
            phone = re.sub(r'[\s-]', '', tel_match.group(1))
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # РАСЧЁТ МЕТРИК
    # ═══════════════════════════════════════════════════════════════════════════

    def _calculate_metrics(self):
        """Вычисление метрик графа."""
        logger.info("Расчёт метрик...")

        # Степени узлов
        in_degrees = dict(self.graph.in_degree())
        out_degrees = dict(self.graph.out_degree())

        for node_id in self.nodes:
            self.nodes[node_id].in_degree = in_degrees.get(node_id, 0)
            self.nodes[node_id].out_degree = out_degrees.get(node_id, 0)
            self.nodes[node_id].degree = self.nodes[node_id].in_degree + self.nodes[node_id].out_degree

        # Betweenness centrality
        try:
            betweenness = nx.betweenness_centrality(self.graph, normalized=True)
            for node_id, value in betweenness.items():
                if node_id in self.nodes:
                    self.nodes[node_id].betweenness = round(value, 6)
        except Exception as e:
            logger.warning(f"Ошибка расчёта betweenness: {e}")

        # PageRank
        try:
            pagerank = nx.pagerank(self.graph, alpha=0.85)
            for node_id, value in pagerank.items():
                if node_id in self.nodes:
                    self.nodes[node_id].pagerank = round(value, 6)
        except Exception as e:
            logger.warning(f"Ошибка расчёта PageRank: {e}")

        # Кластеризация (Louvain)
        if HAS_COMMUNITY:
            try:
                # Конвертируем в ненаправленный граф для кластеризации
                undirected = self.graph.to_undirected()
                partition = community_louvain.best_partition(undirected)

                for node_id, cluster_id in partition.items():
                    if node_id in self.nodes:
                        self.nodes[node_id].cluster_id = cluster_id

                n_clusters = len(set(partition.values()))
                logger.info(f"Найдено {n_clusters} кластеров")
            except Exception as e:
                logger.warning(f"Ошибка кластеризации: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # АНАЛИЗ
    # ═══════════════════════════════════════════════════════════════════════════

    def get_influencers(self, top_n: int = 20, metric: str = 'pagerank') -> List[Dict]:
        """Получение топ influencers по метрике."""
        nodes_list = list(self.nodes.values())

        # Фильтруем группы
        nodes_list = [n for n in nodes_list if not n.is_group]

        # Сортируем по выбранной метрике
        if metric == 'pagerank':
            nodes_list.sort(key=lambda x: x.pagerank, reverse=True)
        elif metric == 'betweenness':
            nodes_list.sort(key=lambda x: x.betweenness, reverse=True)
        elif metric == 'degree':
            nodes_list.sort(key=lambda x: x.degree, reverse=True)
        elif metric == 'in_degree':
            nodes_list.sort(key=lambda x: x.in_degree, reverse=True)
        elif metric == 'out_degree':
            nodes_list.sort(key=lambda x: x.out_degree, reverse=True)

        return [n.to_dict() for n in nodes_list[:top_n]]

    def get_clusters(self, min_size: int = 3) -> List[Dict]:
        """Получение кластеров контактов."""
        clusters: Dict[int, List[ContactNode]] = defaultdict(list)

        for node in self.nodes.values():
            if node.cluster_id >= 0 and not node.is_group:
                clusters[node.cluster_id].append(node)

        # Фильтруем по размеру и форматируем
        result = []
        for cluster_id, members in clusters.items():
            if len(members) >= min_size:
                # Определяем доминирующий тип
                types_count = Counter(m.contact_type for m in members)
                dominant_type = types_count.most_common(1)[0][0] if types_count else 'unknown'

                result.append({
                    'cluster_id': cluster_id,
                    'size': len(members),
                    'dominant_type': dominant_type,
                    'types_distribution': dict(types_count),
                    'members': [m.to_dict() for m in sorted(members, key=lambda x: x.pagerank, reverse=True)],
                    'top_influencer': members[0].name if members else None,
                })

        # Сортируем по размеру
        result.sort(key=lambda x: x['size'], reverse=True)
        return result

    def analyze_contact(self, phone_or_id: str) -> Optional[Dict]:
        """Детальный анализ конкретного контакта."""
        # Находим контакт
        contact_id = self.phone_to_id.get(phone_or_id, phone_or_id)

        if contact_id not in self.nodes:
            return None

        node = self.nodes[contact_id]

        # Собираем связи
        incoming = []
        outgoing = []

        for (src, tgt, etype), edge in self.edges.items():
            if tgt == contact_id:
                incoming.append({
                    'from': src,
                    'from_name': self.nodes[src].name if src in self.nodes else src,
                    'type': etype,
                    'weight': edge.weight,
                })
            elif src == contact_id:
                outgoing.append({
                    'to': tgt,
                    'to_name': self.nodes[tgt].name if tgt in self.nodes else tgt,
                    'type': etype,
                    'weight': edge.weight,
                })

        # Группы контакта
        groups = []
        for group_id, members in self.group_members.items():
            if contact_id in members:
                groups.append({
                    'group_id': group_id,
                    'group_name': self.nodes[group_id].name if group_id in self.nodes else group_id,
                    'members_count': len(members),
                })

        # Кластер
        cluster_members = []
        if node.cluster_id >= 0:
            cluster_members = [
                {'id': n.id, 'name': n.name}
                for n in self.nodes.values()
                if n.cluster_id == node.cluster_id and n.id != contact_id and not n.is_group
            ][:10]  # Топ 10 из кластера

        return {
            'contact': node.to_dict(),
            'incoming_connections': len(incoming),
            'outgoing_connections': len(outgoing),
            'incoming': sorted(incoming, key=lambda x: x['weight'], reverse=True)[:20],
            'outgoing': sorted(outgoing, key=lambda x: x['weight'], reverse=True)[:20],
            'groups': groups,
            'cluster_members': cluster_members,
            'connection_types': {
                'forwards_received': sum(1 for e in incoming if e['type'] == 'forward'),
                'forwards_sent': sum(1 for e in outgoing if e['type'] == 'forward'),
                'mentions_received': sum(1 for e in incoming if e['type'] == 'mention'),
                'mentions_sent': sum(1 for e in outgoing if e['type'] == 'mention'),
                'referrals_made': sum(1 for e in outgoing if e['type'] == 'referral'),
                'referred_by': sum(1 for e in incoming if e['type'] == 'referral'),
            }
        }

    def get_graph_stats(self) -> Dict:
        """Статистика графа."""
        nodes_by_type = Counter(n.contact_type for n in self.nodes.values())
        edges_by_type = Counter(e.edge_type for e in self.edges.values())

        # Плотность графа
        n = self.graph.number_of_nodes()
        m = self.graph.number_of_edges()
        density = m / (n * (n - 1)) if n > 1 else 0

        return {
            'total_nodes': n,
            'total_edges': m,
            'density': round(density, 6),
            'nodes_by_type': dict(nodes_by_type),
            'edges_by_type': dict(edges_by_type),
            'groups_count': sum(1 for n in self.nodes.values() if n.is_group),
            'average_degree': round(sum(n.degree for n in self.nodes.values()) / len(self.nodes), 2) if self.nodes else 0,
            'clusters_count': len(set(n.cluster_id for n in self.nodes.values() if n.cluster_id >= 0)),
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # ВИЗУАЛИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_html(self, filepath: Path = GRAPH_HTML, height: str = "900px",
                      max_nodes: int = 500, filter_type: Optional[str] = None) -> Path:
        """Генерация интерактивного HTML графа с Pyvis."""
        if not HAS_PYVIS:
            raise ImportError("pyvis не установлен. pip install pyvis")

        logger.info("Генерация HTML графа...")

        # Создаём Pyvis сеть
        net = Network(
            height=height,
            width="100%",
            bgcolor="#ffffff",
            font_color="#333333",
            directed=True,
            notebook=False,
        )

        # Опции физики
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            },
            "nodes": {
                "font": {"size": 14},
                "scaling": {"min": 10, "max": 50}
            },
            "edges": {
                "smooth": {"type": "continuous"},
                "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}}
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 100,
                "hideEdgesOnDrag": true
            }
        }
        """)

        # Фильтруем и ограничиваем узлы
        nodes_to_show = list(self.nodes.values())

        if filter_type:
            nodes_to_show = [n for n in nodes_to_show if n.contact_type == filter_type]

        # Сортируем по PageRank и берём топ
        nodes_to_show.sort(key=lambda x: x.pagerank, reverse=True)
        nodes_to_show = nodes_to_show[:max_nodes]
        node_ids = {n.id for n in nodes_to_show}

        # Добавляем узлы
        for node in nodes_to_show:
            color = NODE_COLORS.get(node.contact_type, NODE_COLORS['unknown'])

            # Размер пропорционален PageRank
            size = 10 + node.pagerank * 1000
            size = min(50, max(10, size))

            title = f"""
            <b>{node.name}</b><br>
            Тип: {node.contact_type}<br>
            Телефон: {node.phone or 'N/A'}<br>
            Связей: {node.degree}<br>
            PageRank: {node.pagerank:.4f}<br>
            Кластер: {node.cluster_id}
            """

            net.add_node(
                node.id,
                label=node.name[:20] + '...' if len(node.name) > 20 else node.name,
                title=title,
                color=color,
                size=size,
                shape='dot' if not node.is_group else 'square',
            )

        # Добавляем рёбра
        for (src, tgt, etype), edge in self.edges.items():
            if src in node_ids and tgt in node_ids:
                color = EDGE_COLORS.get(etype, '#999999')
                width = min(5, 1 + edge.weight * 0.2)

                net.add_edge(
                    src, tgt,
                    color=color,
                    width=width,
                    title=f"{etype}: {edge.weight}",
                )

        # Создаём директорию
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Сохраняем
        net.save_graph(str(filepath))

        # Добавляем легенду
        self._add_legend_to_html(filepath)

        logger.info(f"HTML граф сохранён: {filepath}")
        return filepath

    def _add_legend_to_html(self, filepath: Path):
        """Добавление легенды в HTML файл."""
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        legend_html = """
        <div id="legend" style="position: fixed; top: 10px; right: 10px; background: white;
             padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 1000;">
            <h4 style="margin: 0 0 10px 0;">Легенда</h4>
            <div style="margin-bottom: 8px;"><b>Узлы (контакты):</b></div>
            <div style="margin-left: 10px;">
                <span style="display: inline-block; width: 12px; height: 12px; background: #4CAF50; border-radius: 50%; margin-right: 5px;"></span>Клиенты<br>
                <span style="display: inline-block; width: 12px; height: 12px; background: #2196F3; border-radius: 50%; margin-right: 5px;"></span>Агенты<br>
                <span style="display: inline-block; width: 12px; height: 12px; background: #FF9800; border-radius: 50%; margin-right: 5px;"></span>Поставщики<br>
                <span style="display: inline-block; width: 12px; height: 12px; background: #9C27B0; border-radius: 50%; margin-right: 5px;"></span>Сотрудники<br>
                <span style="display: inline-block; width: 12px; height: 12px; background: #607D8B; border-radius: 50%; margin-right: 5px;"></span>Группы<br>
            </div>
            <div style="margin: 10px 0 8px 0;"><b>Связи:</b></div>
            <div style="margin-left: 10px;">
                <span style="display: inline-block; width: 20px; height: 3px; background: #F44336; margin-right: 5px;"></span>Пересылки<br>
                <span style="display: inline-block; width: 20px; height: 3px; background: #FF9800; margin-right: 5px;"></span>Упоминания<br>
                <span style="display: inline-block; width: 20px; height: 3px; background: #4CAF50; margin-right: 5px;"></span>Рефералы<br>
                <span style="display: inline-block; width: 20px; height: 3px; background: #2196F3; margin-right: 5px;"></span>VCF карточки<br>
                <span style="display: inline-block; width: 20px; height: 3px; background: #9E9E9E; margin-right: 5px;"></span>Общие группы<br>
            </div>
        </div>
        """

        # Вставляем легенду перед </body>
        html = html.replace('</body>', legend_html + '</body>')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    # ═══════════════════════════════════════════════════════════════════════════
    # ЭКСПОРТ
    # ═══════════════════════════════════════════════════════════════════════════

    def export_json(self, filepath: Path = GRAPH_JSON) -> Path:
        """Экспорт графа в JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'meta': {
                'generated_at': datetime.now().isoformat(),
                'stats': self.get_graph_stats(),
            },
            'nodes': [n.to_dict() for n in self.nodes.values()],
            'edges': [e.to_dict() for e in self.edges.values()],
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON экспортирован: {filepath}")
        return filepath

    def export_gexf(self, filepath: Path = GRAPH_GEXF) -> Path:
        """Экспорт графа в GEXF (для Gephi)."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Создаём копию графа для GEXF (чтобы не портить оригинал)
        gexf_graph = nx.DiGraph()

        # Копируем узлы с нужными атрибутами
        for node_id, node in self.nodes.items():
            gexf_graph.add_node(
                node_id,
                label=node.name,
                contact_type=node.contact_type,
                pagerank=float(node.pagerank),
                betweenness=float(node.betweenness),
                cluster=int(node.cluster_id),
                degree=int(node.degree),
            )

        # Копируем рёбра (конвертируем set в строку)
        for (src, tgt, etype), edge in self.edges.items():
            gexf_graph.add_edge(
                src, tgt,
                weight=float(edge.weight),
                edge_type=etype,
            )

        nx.write_gexf(gexf_graph, str(filepath))

        logger.info(f"GEXF экспортирован: {filepath}")
        return filepath

    def export_influencers(self, filepath: Path = INFLUENCERS_JSON, top_n: int = 50) -> Path:
        """Экспорт списка influencers."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'generated_at': datetime.now().isoformat(),
            'by_pagerank': self.get_influencers(top_n, 'pagerank'),
            'by_betweenness': self.get_influencers(top_n, 'betweenness'),
            'by_degree': self.get_influencers(top_n, 'degree'),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Influencers экспортированы: {filepath}")
        return filepath

    def export_clusters(self, filepath: Path = CLUSTERS_JSON, min_size: int = 3) -> Path:
        """Экспорт кластеров."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'generated_at': datetime.now().isoformat(),
            'clusters': self.get_clusters(min_size),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Кластеры экспортированы: {filepath}")
        return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description='Граф связей контактов WhatsApp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Построить граф и экспортировать всё
  python contact_graph.py --build --export-all

  # Только интерактивный HTML
  python contact_graph.py --build --html

  # Найти influencers
  python contact_graph.py --build --influencers --top 30

  # Анализ конкретного контакта
  python contact_graph.py --build --analyze --phone +971501234567

  # Экспорт для Gephi
  python contact_graph.py --build --export-gexf
        """
    )

    # Основные команды
    parser.add_argument('--build', action='store_true', help='Построить граф')
    parser.add_argument('--html', action='store_true', help='Сгенерировать интерактивный HTML')
    parser.add_argument('--influencers', action='store_true', help='Найти influencers')
    parser.add_argument('--clusters', action='store_true', help='Найти кластеры')
    parser.add_argument('--analyze', action='store_true', help='Анализ конкретного контакта')
    parser.add_argument('--stats', action='store_true', help='Показать статистику графа')

    # Экспорт
    parser.add_argument('--export-json', action='store_true', help='Экспорт в JSON')
    parser.add_argument('--export-gexf', action='store_true', help='Экспорт в GEXF (для Gephi)')
    parser.add_argument('--export-all', action='store_true', help='Экспорт всех форматов')

    # Параметры
    parser.add_argument('--phone', type=str, help='Телефон контакта для анализа')
    parser.add_argument('--top', type=int, default=20, help='Количество top influencers')
    parser.add_argument('--min-size', type=int, default=3, help='Минимальный размер кластера')
    parser.add_argument('--max-nodes', type=int, default=500, help='Максимум узлов в HTML')
    parser.add_argument('--filter-type', type=str, choices=['клиенты', 'агенты', 'поставщики', 'сотрудники'],
                        help='Фильтр по типу контакта')
    parser.add_argument('--output', '-o', type=str, help='Путь выходного файла')
    parser.add_argument('--limit', type=int, default=0, help='Лимит загрузки сообщений (0 = все)')

    args = parser.parse_args()

    # Проверяем зависимости
    if not HAS_NETWORKX:
        print("[!] Установите networkx: pip install networkx")
        sys.exit(1)

    # Создаём директории
    ensure_directories()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Инициализируем граф
    graph = ContactGraph()

    # Загружаем данные
    if args.build or args.html or args.influencers or args.clusters or args.analyze or args.stats or args.export_all:
        print("\n" + "="*60)
        print("ЗАГРУЗКА ДАННЫХ")
        print("="*60)

        graph.load_contacts()
        graph.load_messages(limit=args.limit)
        graph.load_referrals()

        print("\n" + "="*60)
        print("ПОСТРОЕНИЕ ГРАФА")
        print("="*60)

        graph.build_graph()

    # Статистика
    if args.stats or args.build:
        print("\n" + "="*60)
        print("СТАТИСТИКА ГРАФА")
        print("="*60)

        stats = graph.get_graph_stats()
        print(f"\nВсего узлов: {stats['total_nodes']}")
        print(f"Всего рёбер: {stats['total_edges']}")
        print(f"Плотность: {stats['density']:.4f}")
        print(f"Средняя степень: {stats['average_degree']}")
        print(f"Кластеров: {stats['clusters_count']}")
        print(f"\nУзлы по типам:")
        for t, c in stats['nodes_by_type'].items():
            print(f"  {t}: {c}")
        print(f"\nРёбра по типам:")
        for t, c in stats['edges_by_type'].items():
            print(f"  {t}: {c}")

    # Influencers
    if args.influencers:
        print("\n" + "="*60)
        print(f"TOP {args.top} INFLUENCERS (по PageRank)")
        print("="*60)

        influencers = graph.get_influencers(args.top, 'pagerank')
        for i, inf in enumerate(influencers, 1):
            print(f"\n{i}. {inf['name']}")
            print(f"   Тип: {inf['contact_type']}")
            print(f"   Связей: {inf['degree']} (входящих: {inf['in_degree']}, исходящих: {inf['out_degree']})")
            print(f"   PageRank: {inf['pagerank']:.4f}")
            print(f"   Betweenness: {inf['betweenness']:.4f}")

        # Экспорт
        output = Path(args.output) if args.output else INFLUENCERS_JSON
        graph.export_influencers(output, args.top)

    # Кластеры
    if args.clusters:
        print("\n" + "="*60)
        print(f"КЛАСТЕРЫ (минимум {args.min_size} участников)")
        print("="*60)

        clusters = graph.get_clusters(args.min_size)
        for cluster in clusters:
            print(f"\nКластер #{cluster['cluster_id']}: {cluster['size']} участников")
            print(f"  Доминирующий тип: {cluster['dominant_type']}")
            print(f"  Топ influencer: {cluster['top_influencer']}")
            print(f"  Участники (топ 5):")
            for m in cluster['members'][:5]:
                print(f"    - {m['name']} ({m['contact_type']})")

        # Экспорт
        output = Path(args.output) if args.output else CLUSTERS_JSON
        graph.export_clusters(output, args.min_size)

    # Анализ контакта
    if args.analyze and args.phone:
        print("\n" + "="*60)
        print(f"АНАЛИЗ КОНТАКТА: {args.phone}")
        print("="*60)

        analysis = graph.analyze_contact(args.phone)
        if analysis:
            c = analysis['contact']
            print(f"\nИмя: {c['name']}")
            print(f"Телефон: {c['phone']}")
            print(f"Тип: {c['contact_type']}")
            print(f"Кластер: {c['cluster_id']}")
            print(f"\nМетрики:")
            print(f"  Степень: {c['degree']} (вх: {c['in_degree']}, исх: {c['out_degree']})")
            print(f"  PageRank: {c['pagerank']:.4f}")
            print(f"  Betweenness: {c['betweenness']:.4f}")

            print(f"\nСвязи:")
            ct = analysis['connection_types']
            print(f"  Пересылки получено: {ct['forwards_received']}")
            print(f"  Пересылки отправлено: {ct['forwards_sent']}")
            print(f"  Упоминаний получено: {ct['mentions_received']}")
            print(f"  Рефералов привёл: {ct['referrals_made']}")
            print(f"  Приведён рефералом: {ct['referred_by']}")

            print(f"\nТоп входящие связи ({analysis['incoming_connections']}):")
            for conn in analysis['incoming'][:10]:
                print(f"  <- {conn['from_name']} ({conn['type']}: {conn['weight']})")

            print(f"\nТоп исходящие связи ({analysis['outgoing_connections']}):")
            for conn in analysis['outgoing'][:10]:
                print(f"  -> {conn['to_name']} ({conn['type']}: {conn['weight']})")

            if analysis['groups']:
                print(f"\nГруппы ({len(analysis['groups'])}):")
                for g in analysis['groups'][:10]:
                    print(f"  - {g['group_name']} ({g['members_count']} участников)")

            if analysis['cluster_members']:
                print(f"\nУчастники того же кластера:")
                for m in analysis['cluster_members']:
                    print(f"  - {m['name']}")
        else:
            print(f"Контакт не найден: {args.phone}")

    # HTML
    if args.html:
        output = Path(args.output) if args.output else GRAPH_HTML
        graph.generate_html(output, max_nodes=args.max_nodes, filter_type=args.filter_type)
        print(f"\n[OK] HTML граф: {output}")

    # Экспорт JSON
    if args.export_json or args.export_all:
        output = Path(args.output) if args.output and not args.export_all else GRAPH_JSON
        graph.export_json(output)
        print(f"\n[OK] JSON: {output}")

    # Экспорт GEXF
    if args.export_gexf or args.export_all:
        output = GRAPH_GEXF
        graph.export_gexf(output)
        print(f"\n[OK] GEXF: {output}")

    # Экспорт всего
    if args.export_all:
        graph.export_influencers(INFLUENCERS_JSON)
        graph.export_clusters(CLUSTERS_JSON)
        graph.generate_html(GRAPH_HTML, max_nodes=args.max_nodes)

        print(f"\n" + "="*60)
        print("ВСЕ ФАЙЛЫ ЭКСПОРТИРОВАНЫ")
        print("="*60)
        print(f"  JSON:        {GRAPH_JSON}")
        print(f"  GEXF:        {GRAPH_GEXF}")
        print(f"  HTML:        {GRAPH_HTML}")
        print(f"  Influencers: {INFLUENCERS_JSON}")
        print(f"  Clusters:    {CLUSTERS_JSON}")

    print("\n[OK] Готово!")


if __name__ == '__main__':
    main()
