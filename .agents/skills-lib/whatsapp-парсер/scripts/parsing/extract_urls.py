#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение и категоризация URL из WhatsApp чатов.

Функции:
- Извлечение всех URL из JSONL чатов
- Категоризация по типам (бронирования, карты, соцсети, банки и т.д.)
- Резолвинг коротких ссылок (bit.ly, t.me, goo.gl)
- Извлечение метаданных (title страницы)
- Статистика по доменам
- Экспорт в JSON и CSV

Использование:
    python extract_urls.py                          # Все URL из all_messages.jsonl
    python extract_urls.py --resolve                # С резолвингом коротких ссылок
    python extract_urls.py --fetch-titles           # С получением title страниц
    python extract_urls.py --category booking       # Только бронирования
    python extract_urls.py --domain booking.com     # Только конкретный домен
    python extract_urls.py --chat "Иван Петров"     # Только из конкретного чата
    python extract_urls.py --output json csv        # Формат вывода
"""

import sys
import os
import re
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse, parse_qs, unquote
import time

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import JSON_DIR, ANALYTICS_DIR, CHATS_DIR
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    JSON_DIR = CHATS_DIR / "_база" / "json"
    ANALYTICS_DIR = CHATS_DIR / "_аналитика"

# ═══════════════════════════════════════════════════════════════════════════════
# КАТЕГОРИИ URL
# ═══════════════════════════════════════════════════════════════════════════════

URL_CATEGORIES = {
    # Бронирование жилья
    'booking': {
        'name': 'Бронирование жилья',
        'domains': [
            'booking.com', 'www.booking.com',
            'airbnb.com', 'www.airbnb.com', 'airbnb.ru',
            'hotels.com', 'www.hotels.com',
            'expedia.com', 'www.expedia.com',
            'agoda.com', 'www.agoda.com',
            'vrbo.com', 'www.vrbo.com',
            'hostelworld.com', 'www.hostelworld.com',
            'trivago.com', 'www.trivago.com',
        ],
        'patterns': [
            r'booking\.com/hotel',
            r'airbnb\.\w+/rooms/',
        ]
    },

    # Карты и локации
    'maps': {
        'name': 'Карты и локации',
        'domains': [
            'maps.google.com', 'www.google.com/maps', 'goo.gl/maps',
            'maps.app.goo.gl',
            'yandex.ru/maps', 'maps.yandex.ru',
            '2gis.ru', '2gis.com',
            'waze.com', 'www.waze.com',
            'what3words.com',
        ],
        'patterns': [
            r'google\.\w+/maps',
            r'maps\.google',
            r'goo\.gl/maps',
            r'maps\.app\.goo\.gl',
        ]
    },

    # Видео
    'video': {
        'name': 'Видео',
        'domains': [
            'youtube.com', 'www.youtube.com', 'm.youtube.com',
            'youtu.be',
            'vimeo.com', 'www.vimeo.com',
            'tiktok.com', 'www.tiktok.com', 'vm.tiktok.com',
            'rutube.ru', 'www.rutube.ru',
            'vk.com/video',
        ],
        'patterns': [
            r'youtu\.be/',
            r'youtube\.com/watch',
            r'youtube\.com/shorts',
            r'tiktok\.com/@',
        ]
    },

    # Социальные сети
    'social': {
        'name': 'Социальные сети',
        'domains': [
            'instagram.com', 'www.instagram.com',
            'facebook.com', 'www.facebook.com', 'm.facebook.com', 'fb.com',
            'twitter.com', 'www.twitter.com', 'x.com',
            'linkedin.com', 'www.linkedin.com',
            'vk.com', 'www.vk.com', 'm.vk.com',
            'ok.ru', 'www.ok.ru',
            'threads.net', 'www.threads.net',
        ],
        'patterns': [
            r'instagram\.com/p/',
            r'instagram\.com/reel/',
            r'fb\.me/',
        ]
    },

    # Мессенджеры
    'messenger': {
        'name': 'Мессенджеры',
        'domains': [
            't.me', 'telegram.me', 'telegram.org',
            'wa.me', 'api.whatsapp.com', 'chat.whatsapp.com',
            'viber.com',
        ],
        'patterns': [
            r't\.me/',
            r'wa\.me/',
            r'chat\.whatsapp\.com',
        ]
    },

    # Финансы и банки
    'finance': {
        'name': 'Финансы и переводы',
        'domains': [
            'paypal.com', 'www.paypal.com', 'paypal.me',
            'wise.com', 'www.wise.com', 'transferwise.com',
            'revolut.com', 'www.revolut.com',
            'tinkoff.ru', 'www.tinkoff.ru',
            'sberbank.ru', 'www.sberbank.ru', 'online.sberbank.ru',
            'alfabank.ru', 'www.alfabank.ru',
            'vtb.ru', 'www.vtb.ru',
            'raiffeisen.ru', 'www.raiffeisen.ru',
        ],
        'patterns': [
            r'paypal\.me/',
            r'tinkoff\.ru/cf/',  # Tinkoff перевод
        ]
    },

    # Документы
    'documents': {
        'name': 'Документы',
        'domains': [
            'docs.google.com', 'drive.google.com',
            'sheets.google.com', 'forms.google.com',
            'dropbox.com', 'www.dropbox.com',
            'onedrive.live.com', '1drv.ms',
            'yadi.sk', 'disk.yandex.ru',
            'cloud.mail.ru',
            'notion.so', 'www.notion.so',
        ],
        'patterns': [
            r'docs\.google\.com/document',
            r'docs\.google\.com/spreadsheets',
            r'drive\.google\.com/file',
            r'drive\.google\.com/open',
            r'\.pdf$',
        ]
    },

    # Транспорт и билеты
    'transport': {
        'name': 'Транспорт и билеты',
        'domains': [
            'aviasales.ru', 'www.aviasales.ru',
            'skyscanner.com', 'www.skyscanner.com', 'skyscanner.ru',
            'tutu.ru', 'www.tutu.ru',
            'rzd.ru', 'www.rzd.ru',
            'aeroflot.ru', 'www.aeroflot.ru',
            'emirates.com', 'www.emirates.com',
            'flydubai.com', 'www.flydubai.com',
            'uber.com', 'www.uber.com',
            'careem.com', 'www.careem.com',
            'bolt.eu',
        ],
        'patterns': []
    },

    # Туризм и экскурсии
    'tourism': {
        'name': 'Туризм и экскурсии',
        'domains': [
            'tripadvisor.com', 'www.tripadvisor.com', 'tripadvisor.ru',
            'viator.com', 'www.viator.com',
            'getyourguide.com', 'www.getyourguide.com',
            'klook.com', 'www.klook.com',
            'tourister.ru',
            'sputnik8.com',
        ],
        'patterns': []
    },

    # Интернет-магазины
    'ecommerce': {
        'name': 'Интернет-магазины',
        'domains': [
            'amazon.com', 'www.amazon.com', 'amazon.ae',
            'noon.com', 'www.noon.com',
            'aliexpress.com', 'www.aliexpress.com', 'aliexpress.ru',
            'ozon.ru', 'www.ozon.ru',
            'wildberries.ru', 'www.wildberries.ru',
        ],
        'patterns': []
    },

    # Короткие ссылки (для резолвинга)
    'shortener': {
        'name': 'Короткие ссылки',
        'domains': [
            'bit.ly', 'bitly.com',
            'goo.gl',
            'tinyurl.com',
            'is.gd', 'v.gd',
            'ow.ly',
            'buff.ly',
            'clck.ru',
            'cutt.ly',
            'rb.gy',
            'short.io',
        ],
        'patterns': []
    },
}

# Паттерн для извлечения URL
URL_PATTERN = re.compile(
    r'https?://[^\s<>"{}|\\^`\[\]]+|'
    r'www\.[^\s<>"{}|\\^`\[\]]+',
    re.IGNORECASE
)

# Паттерн для очистки URL от trailing символов
URL_CLEANUP_PATTERN = re.compile(r'[.,;:!?\)}\]]+$')


# ═══════════════════════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def extract_urls_from_text(text: str) -> list[str]:
    """Извлекает все URL из текста."""
    if not text:
        return []

    urls = URL_PATTERN.findall(text)
    cleaned_urls = []

    for url in urls:
        # Очищаем от trailing punctuation
        url = URL_CLEANUP_PATTERN.sub('', url)
        # Добавляем http если начинается с www
        if url.startswith('www.'):
            url = 'http://' + url
        if url and len(url) > 10:  # Минимальная длина URL
            cleaned_urls.append(url)

    return cleaned_urls


def get_domain(url: str) -> str:
    """Извлекает домен из URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Убираем www. для унификации
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ''


def categorize_url(url: str) -> str:
    """Определяет категорию URL."""
    domain = get_domain(url)
    url_lower = url.lower()

    for category, config in URL_CATEGORIES.items():
        # Проверяем домен
        for cat_domain in config['domains']:
            if cat_domain in domain or domain.endswith('.' + cat_domain):
                return category

        # Проверяем паттерны
        for pattern in config.get('patterns', []):
            if re.search(pattern, url_lower):
                return category

    return 'other'


def resolve_short_url(url: str, timeout: int = 5) -> dict:
    """
    Резолвит короткую ссылку в полную.
    Возвращает dict с resolved_url и статусом.
    """
    try:
        import requests

        response = requests.head(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        final_url = response.url

        return {
            'original': url,
            'resolved': final_url,
            'status': 'resolved' if final_url != url else 'no_redirect',
            'status_code': response.status_code
        }
    except ImportError:
        return {
            'original': url,
            'resolved': url,
            'status': 'requests_not_installed',
            'error': 'pip install requests'
        }
    except Exception as e:
        return {
            'original': url,
            'resolved': url,
            'status': 'error',
            'error': str(e)
        }


def fetch_page_title(url: str, timeout: int = 5) -> str | None:
    """Получает title страницы по URL."""
    try:
        import requests
        from html.parser import HTMLParser

        class TitleParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_title = False
                self.title = None

            def handle_starttag(self, tag, attrs):
                if tag.lower() == 'title':
                    self.in_title = True

            def handle_endtag(self, tag):
                if tag.lower() == 'title':
                    self.in_title = False

            def handle_data(self, data):
                if self.in_title:
                    self.title = data.strip()

        response = requests.get(
            url,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        if response.status_code == 200:
            # Парсим только первые 50KB для скорости
            content = response.text[:50000]
            parser = TitleParser()
            parser.feed(content)
            return parser.title
    except:
        pass

    return None


def extract_url_metadata(url: str) -> dict:
    """Извлекает метаданные из URL без HTTP запросов."""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    metadata = {
        'domain': get_domain(url),
        'path': parsed.path,
        'query_params': {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
    }

    # Специфичная обработка для разных сервисов
    domain = metadata['domain']

    # YouTube - извлекаем video ID
    if 'youtube.com' in domain or 'youtu.be' in domain:
        if 'v' in query_params:
            metadata['video_id'] = query_params['v'][0]
        elif 'youtu.be' in url:
            path_parts = parsed.path.split('/')
            if len(path_parts) > 1:
                metadata['video_id'] = path_parts[1].split('?')[0]

    # Instagram - извлекаем тип контента и ID
    if 'instagram.com' in domain:
        path_parts = [p for p in parsed.path.split('/') if p]
        if len(path_parts) >= 2:
            if path_parts[0] == 'p':
                metadata['content_type'] = 'post'
                metadata['post_id'] = path_parts[1]
            elif path_parts[0] == 'reel':
                metadata['content_type'] = 'reel'
                metadata['reel_id'] = path_parts[1]
            elif path_parts[0] == 'stories':
                metadata['content_type'] = 'story'
                metadata['username'] = path_parts[1]
            else:
                metadata['content_type'] = 'profile'
                metadata['username'] = path_parts[0]

    # Telegram - извлекаем username или invite
    if 't.me' in domain or 'telegram' in domain:
        path_parts = [p for p in parsed.path.split('/') if p]
        if path_parts:
            if path_parts[0] == 'joinchat' or path_parts[0].startswith('+'):
                metadata['type'] = 'invite'
                metadata['invite_hash'] = path_parts[-1]
            else:
                metadata['type'] = 'channel_or_user'
                metadata['username'] = path_parts[0]
                if len(path_parts) > 1 and path_parts[1].isdigit():
                    metadata['message_id'] = path_parts[1]

    # Google Maps - координаты
    if 'google' in domain and 'maps' in url:
        # Паттерн @lat,lng,zoom
        coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if coords_match:
            metadata['latitude'] = float(coords_match.group(1))
            metadata['longitude'] = float(coords_match.group(2))
        # Place ID
        if 'place/' in url:
            place_match = re.search(r'place/([^/]+)', url)
            if place_match:
                metadata['place_name'] = unquote(place_match.group(1))

    # Booking.com - hotel info
    if 'booking.com' in domain:
        hotel_match = re.search(r'/hotel/\w+/([^.]+)\.', url)
        if hotel_match:
            metadata['hotel_slug'] = hotel_match.group(1)

    # Airbnb - listing ID
    if 'airbnb' in domain:
        listing_match = re.search(r'/rooms/(\d+)', url)
        if listing_match:
            metadata['listing_id'] = listing_match.group(1)

    return metadata


def process_jsonl_file(file_path: Path, filters: dict = None) -> list[dict]:
    """
    Обрабатывает JSONL файл и извлекает все URL с контекстом.

    Args:
        file_path: Путь к JSONL файлу
        filters: Словарь фильтров (chat, sender, date_from, date_to)

    Returns:
        Список словарей с URL и контекстом
    """
    filters = filters or {}
    results = []

    if not file_path.exists():
        print(f"[!] Файл не найден: {file_path}")
        return results

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                msg = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            # Применяем фильтры
            if filters.get('chat'):
                chat_name = msg.get('chat_name', '')
                if filters['chat'].lower() not in chat_name.lower():
                    continue

            if filters.get('sender'):
                sender = msg.get('sender', '')
                if filters['sender'].lower() not in sender.lower():
                    continue

            # Извлекаем URL из текста
            text = msg.get('text', '')
            urls = extract_urls_from_text(text)

            for url in urls:
                category = categorize_url(url)

                # Фильтр по категории
                if filters.get('category') and category != filters['category']:
                    continue

                # Фильтр по домену
                domain = get_domain(url)
                if filters.get('domain') and filters['domain'].lower() not in domain:
                    continue

                result = {
                    'url': url,
                    'domain': domain,
                    'category': category,
                    'category_name': URL_CATEGORIES.get(category, {}).get('name', 'Прочее'),
                    'chat_name': msg.get('chat_name', ''),
                    'sender': msg.get('sender', ''),
                    'datetime': msg.get('datetime', ''),
                    'is_from_me': msg.get('is_from_me', False),
                    'message_preview': text[:200] if len(text) > 200 else text,
                    'jid': msg.get('jid', ''),
                    'metadata': extract_url_metadata(url),
                }

                results.append(result)

    return results


def calculate_statistics(urls: list[dict]) -> dict:
    """Подсчитывает статистику по URL."""
    stats = {
        'total_urls': len(urls),
        'unique_urls': len(set(u['url'] for u in urls)),
        'by_category': defaultdict(int),
        'by_domain': defaultdict(int),
        'by_chat': defaultdict(int),
        'by_sender': defaultdict(int),
        'categories_detail': {},
        'top_domains': [],
        'from_me': 0,
        'from_others': 0,
    }

    domains_detail = defaultdict(lambda: {'count': 0, 'urls': []})

    for u in urls:
        stats['by_category'][u['category']] += 1
        stats['by_domain'][u['domain']] += 1
        stats['by_chat'][u['chat_name']] += 1
        stats['by_sender'][u['sender']] += 1

        if u['is_from_me']:
            stats['from_me'] += 1
        else:
            stats['from_others'] += 1

        domains_detail[u['domain']]['count'] += 1
        if len(domains_detail[u['domain']]['urls']) < 5:  # Храним только 5 примеров
            domains_detail[u['domain']]['urls'].append(u['url'])

    # Сортируем домены по количеству
    stats['top_domains'] = sorted(
        [{'domain': k, 'count': v['count'], 'examples': v['urls']}
         for k, v in domains_detail.items()],
        key=lambda x: x['count'],
        reverse=True
    )[:50]  # Top 50

    # Детали по категориям
    for cat, count in stats['by_category'].items():
        cat_urls = [u for u in urls if u['category'] == cat]
        unique_domains = list(set(u['domain'] for u in cat_urls))
        stats['categories_detail'][cat] = {
            'name': URL_CATEGORIES.get(cat, {}).get('name', 'Прочее'),
            'count': count,
            'unique_urls': len(set(u['url'] for u in cat_urls)),
            'domains': unique_domains[:10],  # Top 10 доменов в категории
        }

    # Преобразуем defaultdict в обычные dict
    stats['by_category'] = dict(stats['by_category'])
    stats['by_domain'] = dict(stats['by_domain'])
    stats['by_chat'] = dict(stats['by_chat'])
    stats['by_sender'] = dict(stats['by_sender'])

    return stats


def export_to_json(urls: list[dict], stats: dict, output_path: Path):
    """Экспортирует результаты в JSON."""
    output = {
        'exported_at': datetime.now().isoformat(),
        'statistics': stats,
        'urls': urls,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[+] JSON экспортирован: {output_path}")


def export_to_csv(urls: list[dict], output_path: Path):
    """Экспортирует URL в CSV."""
    if not urls:
        print("[!] Нет данных для экспорта в CSV")
        return

    fieldnames = [
        'url', 'domain', 'category', 'category_name',
        'chat_name', 'sender', 'datetime', 'is_from_me',
        'message_preview'
    ]

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for url in urls:
            writer.writerow(url)

    print(f"[+] CSV экспортирован: {output_path}")


def export_domains_csv(stats: dict, output_path: Path):
    """Экспортирует статистику по доменам в CSV."""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Domain', 'Count', 'Examples'])
        for d in stats['top_domains']:
            writer.writerow([d['domain'], d['count'], ' | '.join(d['examples'][:3])])

    print(f"[+] Домены экспортированы: {output_path}")


def print_statistics(stats: dict):
    """Выводит статистику в консоль."""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ИЗВЛЕЧЕННЫХ URL")
    print("=" * 60)

    print(f"\nВсего URL: {stats['total_urls']}")
    print(f"Уникальных URL: {stats['unique_urls']}")
    print(f"От меня: {stats['from_me']}")
    print(f"От других: {stats['from_others']}")

    print("\n--- По категориям ---")
    for cat, detail in sorted(stats['categories_detail'].items(),
                               key=lambda x: x[1]['count'], reverse=True):
        print(f"  {detail['name']}: {detail['count']} (уникальных: {detail['unique_urls']})")

    print("\n--- Top 20 доменов ---")
    for i, d in enumerate(stats['top_domains'][:20], 1):
        print(f"  {i:2}. {d['domain']}: {d['count']}")

    print("\n--- По чатам (top 10) ---")
    sorted_chats = sorted(stats['by_chat'].items(), key=lambda x: x[1], reverse=True)[:10]
    for chat, count in sorted_chats:
        print(f"  {chat}: {count}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Извлечение и категоризация URL из WhatsApp чатов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python extract_urls.py                          # Базовый запуск
  python extract_urls.py --resolve                # С резолвингом коротких ссылок
  python extract_urls.py --fetch-titles           # С получением title страниц
  python extract_urls.py --category booking       # Только бронирования
  python extract_urls.py --category maps          # Только карты
  python extract_urls.py --domain youtube.com     # Только YouTube
  python extract_urls.py --chat "Иван"            # Из чатов с Иваном
  python extract_urls.py --output json csv        # Экспорт в оба формата

Категории: booking, maps, video, social, messenger, finance, documents,
           transport, tourism, ecommerce, shortener, other
        """
    )

    parser.add_argument('--input', '-i', type=Path,
                        help='Путь к JSONL файлу (по умолчанию: all_messages.jsonl)')
    parser.add_argument('--output-dir', '-o', type=Path,
                        help='Папка для результатов')
    parser.add_argument('--output', nargs='+', choices=['json', 'csv', 'both'],
                        default=['json', 'csv'],
                        help='Формат вывода (по умолчанию: json csv)')

    # Фильтры
    parser.add_argument('--category', '-c',
                        choices=list(URL_CATEGORIES.keys()) + ['other'],
                        help='Фильтр по категории URL')
    parser.add_argument('--domain', '-d',
                        help='Фильтр по домену (частичное совпадение)')
    parser.add_argument('--chat',
                        help='Фильтр по имени чата (частичное совпадение)')
    parser.add_argument('--sender',
                        help='Фильтр по отправителю')

    # Опции обогащения данных
    parser.add_argument('--resolve', '-r', action='store_true',
                        help='Резолвить короткие ссылки (bit.ly, goo.gl и т.д.)')
    parser.add_argument('--fetch-titles', '-t', action='store_true',
                        help='Получать title страниц (медленно!)')
    parser.add_argument('--timeout', type=int, default=5,
                        help='Таймаут для HTTP запросов (секунды)')

    # Другие опции
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Минимальный вывод')
    parser.add_argument('--list-categories', action='store_true',
                        help='Показать все категории и выйти')

    args = parser.parse_args()

    # Показать категории и выйти
    if args.list_categories:
        print("\nДоступные категории URL:\n")
        for cat, config in URL_CATEGORIES.items():
            print(f"  {cat:12} - {config['name']}")
            if config['domains'][:3]:
                print(f"               Домены: {', '.join(config['domains'][:5])}...")
        return

    # Определяем пути
    if args.input:
        input_file = args.input
    else:
        raw_dir = CHATS_DIR / "_база" / "raw"
        input_file = raw_dir / "all_messages.jsonl"

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = ANALYTICS_DIR / "urls"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.quiet:
        print(f"[*] Входной файл: {input_file}")
        print(f"[*] Папка результатов: {output_dir}")

    # Применяем фильтры
    filters = {}
    if args.category:
        filters['category'] = args.category
        if not args.quiet:
            print(f"[*] Фильтр по категории: {args.category}")
    if args.domain:
        filters['domain'] = args.domain
        if not args.quiet:
            print(f"[*] Фильтр по домену: {args.domain}")
    if args.chat:
        filters['chat'] = args.chat
        if not args.quiet:
            print(f"[*] Фильтр по чату: {args.chat}")
    if args.sender:
        filters['sender'] = args.sender
        if not args.quiet:
            print(f"[*] Фильтр по отправителю: {args.sender}")

    # Извлекаем URL
    if not args.quiet:
        print("\n[*] Извлечение URL из сообщений...")

    urls = process_jsonl_file(input_file, filters)

    if not urls:
        print("[!] URL не найдены")
        return

    if not args.quiet:
        print(f"[+] Найдено URL: {len(urls)}")

    # Резолвинг коротких ссылок
    if args.resolve:
        shortener_urls = [u for u in urls if u['category'] == 'shortener']
        if shortener_urls:
            print(f"\n[*] Резолвинг {len(shortener_urls)} коротких ссылок...")
            for i, u in enumerate(shortener_urls, 1):
                if not args.quiet:
                    print(f"  [{i}/{len(shortener_urls)}] {u['url'][:50]}...", end=' ')

                result = resolve_short_url(u['url'], args.timeout)
                u['resolved_url'] = result['resolved']
                u['resolve_status'] = result['status']

                # Обновляем категорию если резолвнули
                if result['status'] == 'resolved' and result['resolved'] != u['url']:
                    u['original_url'] = u['url']
                    u['url'] = result['resolved']
                    u['domain'] = get_domain(result['resolved'])
                    u['category'] = categorize_url(result['resolved'])
                    u['category_name'] = URL_CATEGORIES.get(u['category'], {}).get('name', 'Прочее')
                    u['metadata'] = extract_url_metadata(result['resolved'])
                    if not args.quiet:
                        print(f"-> {u['domain']}")
                else:
                    if not args.quiet:
                        print(f"({result['status']})")

                time.sleep(0.3)  # Пауза между запросами

    # Получение title страниц
    if args.fetch_titles:
        print(f"\n[*] Получение title страниц (это может занять время)...")
        for i, u in enumerate(urls, 1):
            if not args.quiet and i % 10 == 0:
                print(f"  Обработано: {i}/{len(urls)}")

            title = fetch_page_title(u['url'], args.timeout)
            if title:
                u['page_title'] = title

            time.sleep(0.2)  # Пауза между запросами

    # Статистика
    stats = calculate_statistics(urls)

    if not args.quiet:
        print_statistics(stats)

    # Экспорт
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    output_formats = args.output
    if 'both' in output_formats:
        output_formats = ['json', 'csv']

    if 'json' in output_formats:
        json_path = output_dir / f"urls_{timestamp}.json"
        export_to_json(urls, stats, json_path)

    if 'csv' in output_formats:
        csv_path = output_dir / f"urls_{timestamp}.csv"
        export_to_csv(urls, csv_path)

        domains_csv_path = output_dir / f"domains_{timestamp}.csv"
        export_domains_csv(stats, domains_csv_path)

    # Последний экспорт без timestamp для удобства
    latest_json = output_dir / "urls_latest.json"
    export_to_json(urls, stats, latest_json)

    print(f"\n[+] Готово! Результаты в: {output_dir}")


if __name__ == '__main__':
    main()
