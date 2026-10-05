#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ изображений через Claude Vision API.

Функции:
- Классификация изображений по категориям
- Извлечение текста, объектов, локаций
- Специальный анализ платежей, туров, прайсов
- Batch processing с rate limiting и кэшированием
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    CHATS_DIR, MEDIA_DIR, ANALYTICS_DIR, EXPORT_DIRS,
    ensure_directories, get_export_chat_folders
)

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ
# ═══════════════════════════════════════════════════════════════

# API ключ из переменных окружения
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Поддерживаемые форматы изображений
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Категории изображений
IMAGE_CATEGORIES = {
    'document': {
        'name': 'Документ',
        'subtypes': ['passport', 'visa', 'receipt', 'ticket', 'contract', 'certificate'],
        'keywords_ru': ['паспорт', 'виза', 'чек', 'билет', 'договор', 'сертификат'],
        'keywords_en': ['passport', 'visa', 'receipt', 'ticket', 'contract', 'certificate']
    },
    'screenshot': {
        'name': 'Скриншот',
        'subtypes': ['chat', 'booking', 'payment', 'map', 'website', 'app'],
        'keywords_ru': ['переписка', 'бронирование', 'платёж', 'карта', 'сайт', 'приложение'],
        'keywords_en': ['chat', 'booking', 'payment', 'map', 'website', 'app']
    },
    'tour_photo': {
        'name': 'Фото тура',
        'subtypes': ['landmark', 'hotel', 'transport', 'restaurant', 'activity', 'nature'],
        'keywords_ru': ['достопримечательность', 'отель', 'транспорт', 'ресторан', 'активность', 'природа'],
        'keywords_en': ['landmark', 'hotel', 'transport', 'restaurant', 'activity', 'nature']
    },
    'promo': {
        'name': 'Промо материал',
        'subtypes': ['flyer', 'banner', 'price_list', 'menu', 'catalog'],
        'keywords_ru': ['флаер', 'баннер', 'прайс', 'меню', 'каталог'],
        'keywords_en': ['flyer', 'banner', 'price', 'menu', 'catalog']
    },
    'personal': {
        'name': 'Личное фото',
        'subtypes': ['selfie', 'group', 'portrait'],
        'keywords_ru': ['селфи', 'группа', 'портрет'],
        'keywords_en': ['selfie', 'group', 'portrait']
    },
    'meme': {
        'name': 'Мем/стикер',
        'subtypes': ['meme', 'sticker', 'gif', 'reaction'],
        'keywords_ru': ['мем', 'стикер', 'гифка', 'реакция'],
        'keywords_en': ['meme', 'sticker', 'gif', 'reaction']
    },
    'other': {
        'name': 'Другое',
        'subtypes': ['unknown'],
        'keywords_ru': ['другое'],
        'keywords_en': ['other']
    }
}

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 50
RATE_LIMIT_TOKENS_PER_MINUTE = 100000

# Кэш директория
CACHE_DIR = ANALYTICS_DIR / "image_cache"


# ═══════════════════════════════════════════════════════════════
# ANTHROPIC CLIENT
# ═══════════════════════════════════════════════════════════════

class ClaudeVisionClient:
    """Клиент для работы с Claude Vision API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY не установлен. "
                "Установите переменную окружения ANTHROPIC_API_KEY"
            )

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Библиотека anthropic не установлена. "
                "Выполните: pip install anthropic"
            )

        self.request_count = 0
        self.last_request_time = 0
        self.token_count = 0

    def _rate_limit(self):
        """Применить rate limiting."""
        current_time = time.time()

        # Сброс счётчиков каждую минуту
        if current_time - self.last_request_time > 60:
            self.request_count = 0
            self.token_count = 0
            self.last_request_time = current_time

        # Ждём если превышен лимит
        if self.request_count >= RATE_LIMIT_REQUESTS_PER_MINUTE:
            wait_time = 60 - (current_time - self.last_request_time)
            if wait_time > 0:
                print(f"  Rate limit: ожидание {wait_time:.1f}с...")
                time.sleep(wait_time)
                self.request_count = 0
                self.token_count = 0
                self.last_request_time = time.time()

        self.request_count += 1

    def analyze_image(
        self,
        image_path: Path,
        prompt: str,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Анализировать изображение через Claude Vision.

        Args:
            image_path: Путь к изображению
            prompt: Промпт для анализа
            max_tokens: Максимум токенов в ответе

        Returns:
            Результат анализа
        """
        self._rate_limit()

        # Читаем и кодируем изображение
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Определяем media type
        suffix = image_path.suffix.lower()
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_types.get(suffix, 'image/jpeg')

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            self.token_count += response.usage.input_tokens + response.usage.output_tokens

            return {
                'success': True,
                'content': response.content[0].text,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None
            }


# ═══════════════════════════════════════════════════════════════
# КЭШИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

class ImageCache:
    """Кэш результатов анализа изображений."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = cache_dir / "cache_index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Загрузить индекс кэша."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_index(self):
        """Сохранить индекс кэша."""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _get_file_hash(self, file_path: Path) -> str:
        """Получить хэш файла."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get(self, image_path: Path, analysis_type: str) -> Optional[Dict]:
        """Получить результат из кэша."""
        file_hash = self._get_file_hash(image_path)
        cache_key = f"{file_hash}_{analysis_type}"

        if cache_key in self.index:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        return None

    def set(self, image_path: Path, analysis_type: str, result: Dict):
        """Сохранить результат в кэш."""
        file_hash = self._get_file_hash(image_path)
        cache_key = f"{file_hash}_{analysis_type}"

        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        self.index[cache_key] = {
            'file': str(image_path),
            'type': analysis_type,
            'timestamp': datetime.now().isoformat()
        }
        self._save_index()

    def clear(self):
        """Очистить кэш."""
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
        self.index = {}
        self._save_index()


# ═══════════════════════════════════════════════════════════════
# АНАЛИЗАТОРЫ
# ═══════════════════════════════════════════════════════════════

class ImageAnalyzer:
    """Основной класс анализа изображений."""

    def __init__(self, api_key: str = None, use_cache: bool = True):
        self.client = ClaudeVisionClient(api_key)
        self.cache = ImageCache() if use_cache else None

    def classify_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Классифицировать изображение.

        Returns:
            {
                'category': str,      # Основная категория
                'subtype': str,       # Подтип
                'confidence': float,  # Уверенность 0-1
                'description': str    # Краткое описание
            }
        """
        if self.cache:
            cached = self.cache.get(image_path, 'classify')
            if cached:
                return cached

        prompt = """Проанализируй это изображение и классифицируй его.

Категории:
1. document - Документ (паспорт, виза, чек, билет, договор)
2. screenshot - Скриншот (переписка, бронирование, платёж, карта, сайт)
3. tour_photo - Фото тура (достопримечательность, отель, транспорт, ресторан)
4. promo - Промо материал (флаер, баннер, прайс-лист, меню)
5. personal - Личное фото (селфи, групповое, портрет)
6. meme - Мем/стикер
7. other - Другое

Ответь СТРОГО в JSON формате:
{
    "category": "категория из списка",
    "subtype": "подтип",
    "confidence": 0.95,
    "description": "краткое описание на русском (1-2 предложения)"
}"""

        result = self.client.analyze_image(image_path, prompt)

        if result['success']:
            try:
                # Извлекаем JSON из ответа
                content = result['content']
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    parsed['raw_response'] = content

                    if self.cache:
                        self.cache.set(image_path, 'classify', parsed)

                    return parsed
            except json.JSONDecodeError:
                pass

        return {
            'category': 'other',
            'subtype': 'unknown',
            'confidence': 0.0,
            'description': 'Не удалось классифицировать',
            'error': result.get('error')
        }

    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """
        Извлечь текст с изображения (OCR).

        Returns:
            {
                'has_text': bool,
                'text': str,
                'language': str,
                'text_type': str  # printed, handwritten, mixed
            }
        """
        if self.cache:
            cached = self.cache.get(image_path, 'text')
            if cached:
                return cached

        prompt = """Извлеки весь видимый текст с этого изображения.

Ответь в JSON формате:
{
    "has_text": true/false,
    "text": "весь текст с изображения",
    "language": "ru/en/ar/mixed",
    "text_type": "printed/handwritten/mixed"
}

Если текста нет, верни has_text: false и пустой text."""

        result = self.client.analyze_image(image_path, prompt, max_tokens=2048)

        if result['success']:
            try:
                content = result['content']
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())

                    if self.cache:
                        self.cache.set(image_path, 'text', parsed)

                    return parsed
            except json.JSONDecodeError:
                pass

        return {
            'has_text': False,
            'text': '',
            'language': 'unknown',
            'text_type': 'unknown',
            'error': result.get('error')
        }

    def extract_objects_and_location(self, image_path: Path) -> Dict[str, Any]:
        """
        Извлечь объекты и определить локацию.

        Returns:
            {
                'objects': ['object1', 'object2'],
                'location': {
                    'detected': bool,
                    'place': str,
                    'city': str,
                    'country': str,
                    'landmarks': []
                },
                'faces_count': int,
                'mood': str
            }
        """
        if self.cache:
            cached = self.cache.get(image_path, 'objects')
            if cached:
                return cached

        prompt = """Проанализируй изображение и определи:

1. Основные объекты на фото
2. Локацию (если можно определить)
3. Количество лиц (БЕЗ идентификации личностей)
4. Общее настроение/атмосферу фото

Ответь в JSON формате:
{
    "objects": ["объект1", "объект2", "..."],
    "location": {
        "detected": true/false,
        "place": "название места если известно",
        "city": "город",
        "country": "страна",
        "landmarks": ["достопримечательность1", "..."]
    },
    "faces_count": 0,
    "mood": "настроение/атмосфера"
}"""

        result = self.client.analyze_image(image_path, prompt)

        if result['success']:
            try:
                content = result['content']
                # Ищем JSON в ответе
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(content[json_start:json_end])

                    if self.cache:
                        self.cache.set(image_path, 'objects', parsed)

                    return parsed
            except json.JSONDecodeError:
                pass

        return {
            'objects': [],
            'location': {'detected': False},
            'faces_count': 0,
            'mood': 'unknown',
            'error': result.get('error')
        }

    def analyze_payment_screenshot(self, image_path: Path) -> Dict[str, Any]:
        """
        Специальный анализ скриншота платежа.

        Returns:
            {
                'is_payment': bool,
                'amount': float,
                'currency': str,
                'date': str,
                'status': str,  # completed, pending, failed
                'sender': str,
                'recipient': str,
                'bank': str,
                'reference': str
            }
        """
        if self.cache:
            cached = self.cache.get(image_path, 'payment')
            if cached:
                return cached

        prompt = """Это скриншот платежа/перевода. Извлеки информацию:

Ответь в JSON формате:
{
    "is_payment": true/false,
    "amount": 1000.00,
    "currency": "RUB/AED/USD/EUR",
    "date": "дата в формате DD.MM.YYYY",
    "time": "время HH:MM",
    "status": "completed/pending/failed",
    "sender": "имя отправителя",
    "recipient": "имя получателя",
    "bank": "название банка",
    "reference": "номер транзакции если есть",
    "card_last4": "последние 4 цифры карты если видны"
}

Если это не платёж, верни is_payment: false."""

        result = self.client.analyze_image(image_path, prompt)

        if result['success']:
            try:
                content = result['content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(content[json_start:json_end])

                    if self.cache:
                        self.cache.set(image_path, 'payment', parsed)

                    return parsed
            except json.JSONDecodeError:
                pass

        return {
            'is_payment': False,
            'error': result.get('error')
        }

    def analyze_tour_photo(self, image_path: Path) -> Dict[str, Any]:
        """
        Специальный анализ фото тура - определение локации.

        Returns:
            {
                'is_tour_photo': bool,
                'location': str,
                'city': str,
                'country': str,
                'landmarks': [],
                'tour_type': str,  # city_tour, safari, beach, etc.
                'suggested_caption': str
            }
        """
        if self.cache:
            cached = self.cache.get(image_path, 'tour')
            if cached:
                return cached

        prompt = """Это фото из тура по ОАЭ или другой стране. Определи локацию.

Особое внимание на достопримечательности ОАЭ:
- Burj Khalifa, Dubai Mall, Dubai Frame, Palm Jumeirah
- Sheikh Zayed Mosque, Louvre Abu Dhabi, Ferrari World
- Desert Safari, Dubai Marina, JBR Beach
- Gold Souk, Miracle Garden, Global Village

Ответь в JSON формате:
{
    "is_tour_photo": true/false,
    "location": "конкретное место",
    "city": "Дубай/Абу-Даби/Шарджа/...",
    "country": "ОАЭ",
    "landmarks": ["Burj Khalifa", "..."],
    "tour_type": "city_tour/safari/beach/museum/shopping/...",
    "suggested_caption": "краткое описание для подписи к фото"
}"""

        result = self.client.analyze_image(image_path, prompt)

        if result['success']:
            try:
                content = result['content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(content[json_start:json_end])

                    if self.cache:
                        self.cache.set(image_path, 'tour', parsed)

                    return parsed
            except json.JSONDecodeError:
                pass

        return {
            'is_tour_photo': False,
            'error': result.get('error')
        }

    def analyze_price_list(self, image_path: Path) -> Dict[str, Any]:
        """
        Извлечь цены из прайс-листа/меню.

        Returns:
            {
                'is_price_list': bool,
                'items': [
                    {'name': str, 'price': float, 'currency': str}
                ],
                'business_name': str,
                'total_items': int
            }
        """
        if self.cache:
            cached = self.cache.get(image_path, 'price')
            if cached:
                return cached

        prompt = """Это прайс-лист или меню. Извлеки все цены.

Ответь в JSON формате:
{
    "is_price_list": true/false,
    "business_name": "название заведения/компании",
    "items": [
        {"name": "название товара/услуги", "price": 100.00, "currency": "AED"},
        {"name": "...", "price": ..., "currency": "..."}
    ],
    "total_items": 5,
    "notes": "дополнительная информация"
}

Если это не прайс, верни is_price_list: false."""

        result = self.client.analyze_image(image_path, prompt, max_tokens=2048)

        if result['success']:
            try:
                content = result['content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(content[json_start:json_end])

                    if self.cache:
                        self.cache.set(image_path, 'price', parsed)

                    return parsed
            except json.JSONDecodeError:
                pass

        return {
            'is_price_list': False,
            'error': result.get('error')
        }

    def full_analysis(self, image_path: Path) -> Dict[str, Any]:
        """
        Полный анализ изображения.

        Включает классификацию и специфический анализ в зависимости от типа.
        """
        result = {
            'file': str(image_path),
            'filename': image_path.name,
            'analyzed_at': datetime.now().isoformat()
        }

        # Шаг 1: Классификация
        classification = self.classify_image(image_path)
        result['classification'] = classification

        category = classification.get('category', 'other')

        # Шаг 2: Базовое извлечение текста
        text_result = self.extract_text(image_path)
        result['text'] = text_result

        # Шаг 3: Специфический анализ по категории
        if category == 'screenshot':
            subtype = classification.get('subtype', '')
            if 'payment' in subtype or 'платёж' in classification.get('description', '').lower():
                result['payment_analysis'] = self.analyze_payment_screenshot(image_path)

        elif category == 'tour_photo':
            result['tour_analysis'] = self.analyze_tour_photo(image_path)

        elif category == 'promo':
            subtype = classification.get('subtype', '')
            if 'price' in subtype or 'menu' in subtype:
                result['price_analysis'] = self.analyze_price_list(image_path)

        # Шаг 4: Объекты и локация (для фото)
        if category in ['tour_photo', 'personal', 'other']:
            result['objects'] = self.extract_objects_and_location(image_path)

        return result


# ═══════════════════════════════════════════════════════════════
# BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════

def find_images_in_chat_folder(chat_folder: Path) -> List[Path]:
    """Найти все изображения в папке чата."""
    images = []

    # Проверяем папку media
    media_folder = chat_folder / "media"
    if media_folder.exists():
        for ext in IMAGE_EXTENSIONS:
            images.extend(media_folder.glob(f"*{ext}"))
            images.extend(media_folder.glob(f"*{ext.upper()}"))

    # Проверяем корень папки
    for ext in IMAGE_EXTENSIONS:
        images.extend(chat_folder.glob(f"*{ext}"))
        images.extend(chat_folder.glob(f"*{ext.upper()}"))

    return sorted(images)


def process_chat_folder(
    analyzer: ImageAnalyzer,
    chat_folder: Path,
    output_dir: Path,
    full_analysis: bool = False
) -> Dict[str, Any]:
    """
    Обработать все изображения в папке чата.

    Args:
        analyzer: Экземпляр ImageAnalyzer
        chat_folder: Папка с экспортом чата
        output_dir: Папка для результатов
        full_analysis: Полный анализ или только классификация

    Returns:
        Статистика обработки
    """
    images = find_images_in_chat_folder(chat_folder)

    if not images:
        return {'images_found': 0, 'processed': 0}

    results = []
    stats = defaultdict(int)

    print(f"\n  Обработка {len(images)} изображений из {chat_folder.name}...")

    for i, image_path in enumerate(images, 1):
        print(f"    [{i}/{len(images)}] {image_path.name}...", end=" ")

        try:
            if full_analysis:
                result = analyzer.full_analysis(image_path)
            else:
                result = {
                    'file': str(image_path),
                    'filename': image_path.name,
                    'classification': analyzer.classify_image(image_path),
                    'analyzed_at': datetime.now().isoformat()
                }

            results.append(result)

            category = result.get('classification', {}).get('category', 'other')
            stats[category] += 1

            print(f"OK ({category})")

        except Exception as e:
            print(f"ОШИБКА: {e}")
            results.append({
                'file': str(image_path),
                'filename': image_path.name,
                'error': str(e)
            })
            stats['error'] += 1

    # Сохраняем результаты
    chat_name = chat_folder.name
    output_dir.mkdir(parents=True, exist_ok=True)

    # image_analysis.json - все результаты
    analysis_file = output_dir / f"{chat_name}_image_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return {
        'chat': chat_name,
        'images_found': len(images),
        'processed': len(results),
        'by_category': dict(stats),
        'output_file': str(analysis_file)
    }


def batch_process_all_chats(
    output_dir: Path = None,
    full_analysis: bool = False,
    limit: int = None
) -> Dict[str, Any]:
    """
    Batch обработка всех экспортированных чатов.

    Args:
        output_dir: Папка для результатов
        full_analysis: Полный анализ или только классификация
        limit: Лимит чатов для обработки

    Returns:
        Общая статистика
    """
    if not ANTHROPIC_API_KEY:
        print("ОШИБКА: ANTHROPIC_API_KEY не установлен")
        return {'error': 'No API key'}

    output_dir = output_dir or (ANALYTICS_DIR / "images")
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer = ImageAnalyzer(use_cache=True)

    # Получаем список папок с чатами
    chat_folders = get_export_chat_folders()

    if limit:
        chat_folders = chat_folders[:limit]

    print(f"Найдено {len(chat_folders)} чатов для обработки")

    all_stats = {
        'total_chats': len(chat_folders),
        'total_images': 0,
        'processed': 0,
        'by_category': defaultdict(int),
        'chats_processed': []
    }

    for i, chat_info in enumerate(chat_folders, 1):
        chat_folder = chat_info['folder']
        print(f"\n[{i}/{len(chat_folders)}] {chat_folder.name}")

        stats = process_chat_folder(
            analyzer,
            chat_folder,
            output_dir,
            full_analysis
        )

        all_stats['total_images'] += stats.get('images_found', 0)
        all_stats['processed'] += stats.get('processed', 0)

        for cat, count in stats.get('by_category', {}).items():
            all_stats['by_category'][cat] += count

        all_stats['chats_processed'].append(stats)

    # Сохраняем общую статистику
    all_stats['by_category'] = dict(all_stats['by_category'])
    stats_file = output_dir / "image_categories.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)

    # Собираем все фото туров
    tour_photos = []
    for chat_stats in all_stats['chats_processed']:
        if 'output_file' in chat_stats:
            try:
                with open(chat_stats['output_file'], 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    for r in results:
                        if r.get('classification', {}).get('category') == 'tour_photo':
                            tour_photos.append(r)
            except:
                pass

    if tour_photos:
        tour_file = output_dir / "tour_photos.json"
        with open(tour_file, 'w', encoding='utf-8') as f:
            json.dump(tour_photos, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Обработка завершена!")
    print(f"  Чатов: {all_stats['total_chats']}")
    print(f"  Изображений: {all_stats['total_images']}")
    print(f"  Обработано: {all_stats['processed']}")
    print(f"\nПо категориям:")
    for cat, count in sorted(all_stats['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print(f"\nРезультаты: {output_dir}")

    return all_stats


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Анализ изображений через Claude Vision API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Анализ одного изображения
  python image_analyzer.py -i photo.jpg

  # Полный анализ одного изображения
  python image_analyzer.py -i photo.jpg --full

  # Обработка папки чата
  python image_analyzer.py --chat "D:/Downloads/экспорт чатов/Имя контакта"

  # Batch обработка всех чатов
  python image_analyzer.py --batch

  # Batch с полным анализом (медленнее, но больше данных)
  python image_analyzer.py --batch --full

  # Очистить кэш
  python image_analyzer.py --clear-cache
        """
    )

    parser.add_argument('-i', '--image', help='Путь к изображению')
    parser.add_argument('--chat', help='Путь к папке чата')
    parser.add_argument('--batch', action='store_true', help='Batch обработка всех чатов')
    parser.add_argument('--full', action='store_true', help='Полный анализ (дольше)')
    parser.add_argument('-o', '--output', help='Папка для результатов')
    parser.add_argument('--limit', type=int, help='Лимит чатов для batch')
    parser.add_argument('--no-cache', action='store_true', help='Не использовать кэш')
    parser.add_argument('--clear-cache', action='store_true', help='Очистить кэш')
    parser.add_argument('--json', action='store_true', help='JSON вывод')

    args = parser.parse_args()

    ensure_directories()

    # Очистка кэша
    if args.clear_cache:
        cache = ImageCache()
        cache.clear()
        print("Кэш очищен")
        return

    # Проверка API ключа
    if not ANTHROPIC_API_KEY and not args.clear_cache:
        print("ОШИБКА: ANTHROPIC_API_KEY не установлен")
        print("Установите переменную окружения:")
        print("  set ANTHROPIC_API_KEY=sk-ant-...")
        return

    # Анализ одного изображения
    if args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            print(f"Файл не найден: {args.image}")
            return

        analyzer = ImageAnalyzer(use_cache=not args.no_cache)

        if args.full:
            result = analyzer.full_analysis(image_path)
        else:
            result = analyzer.classify_image(image_path)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\nАнализ: {image_path.name}")
            print("-" * 40)

            if 'classification' in result:
                cls = result['classification']
            else:
                cls = result

            print(f"Категория: {cls.get('category', 'N/A')}")
            print(f"Подтип: {cls.get('subtype', 'N/A')}")
            print(f"Уверенность: {cls.get('confidence', 0):.0%}")
            print(f"Описание: {cls.get('description', 'N/A')}")

            if 'payment_analysis' in result:
                pa = result['payment_analysis']
                if pa.get('is_payment'):
                    print(f"\nПлатёж:")
                    print(f"  Сумма: {pa.get('amount')} {pa.get('currency')}")
                    print(f"  Дата: {pa.get('date')}")
                    print(f"  Статус: {pa.get('status')}")

            if 'tour_analysis' in result:
                ta = result['tour_analysis']
                if ta.get('is_tour_photo'):
                    print(f"\nТур:")
                    print(f"  Локация: {ta.get('location')}")
                    print(f"  Город: {ta.get('city')}")
                    print(f"  Landmarks: {', '.join(ta.get('landmarks', []))}")

        return

    # Обработка папки чата
    if args.chat:
        chat_folder = Path(args.chat)
        if not chat_folder.exists():
            print(f"Папка не найдена: {args.chat}")
            return

        output_dir = Path(args.output) if args.output else (ANALYTICS_DIR / "images")
        analyzer = ImageAnalyzer(use_cache=not args.no_cache)

        stats = process_chat_folder(analyzer, chat_folder, output_dir, args.full)

        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print(f"\nОбработано: {stats['processed']} изображений")
            print(f"Результаты: {stats.get('output_file')}")

        return

    # Batch обработка
    if args.batch:
        output_dir = Path(args.output) if args.output else None
        batch_process_all_chats(output_dir, args.full, args.limit)
        return

    # Если ничего не указано - показать справку
    parser.print_help()


if __name__ == "__main__":
    main()
