#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Parser - Парсер для анализа конкурентов в туристической сфере ОАЭ.

Использует instaloader для сбора данных о постах конкурентов,
анализа цен, хэштегов и engagement metrics.

Зависимости:
    pip install instaloader pandas schedule python-dotenv requests

Использование:
    from instagram_parser import InstagramParser

    parser = InstagramParser()
    parser.add_competitor("dubaidesertsafari")
    report = parser.analyze_all_competitors()
"""

import os
import re
import json
import time
import random
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter
import threading
from functools import wraps

try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False
    print("Warning: instaloader not installed. Run: pip install instaloader")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not installed. Run: pip install pandas")

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Warning: schedule not installed. Run: pip install schedule")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Post:
    """Данные о посте Instagram."""
    shortcode: str
    caption: str
    likes: int
    comments: int
    timestamp: datetime
    hashtags: List[str]
    mentions: List[str]
    is_video: bool
    video_view_count: Optional[int] = None
    location: Optional[str] = None
    extracted_prices: List[Dict[str, Any]] = field(default_factory=list)
    url: str = ""

    def __post_init__(self):
        if not self.url:
            self.url = f"https://www.instagram.com/p/{self.shortcode}/"


@dataclass
class CompetitorProfile:
    """Профиль конкурента."""
    username: str
    full_name: str = ""
    biography: str = ""
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    is_business: bool = False
    business_category: str = ""
    external_url: str = ""
    posts: List[Post] = field(default_factory=list)
    last_updated: Optional[datetime] = None

    @property
    def engagement_rate(self) -> float:
        """Рассчитать engagement rate."""
        if not self.posts or self.followers == 0:
            return 0.0

        total_engagement = sum(p.likes + p.comments for p in self.posts)
        avg_engagement = total_engagement / len(self.posts)
        return (avg_engagement / self.followers) * 100


@dataclass
class PriceEntry:
    """Запись о цене."""
    competitor: str
    product: str
    price: float
    currency: str
    post_url: str
    extracted_at: datetime
    raw_text: str


@dataclass
class PriceAlert:
    """Алерт об изменении цены."""
    competitor: str
    product: str
    old_price: float
    new_price: float
    change_percent: float
    currency: str
    detected_at: datetime
    post_url: str


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """Rate limiter для безопасного парсинга."""

    def __init__(
        self,
        requests_per_minute: int = 10,
        requests_per_hour: int = 100,
        min_delay: float = 3.0,
        max_delay: float = 10.0
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.minute_requests: List[datetime] = []
        self.hour_requests: List[datetime] = []
        self._lock = threading.Lock()

    def wait(self):
        """Ожидание перед следующим запросом."""
        with self._lock:
            now = datetime.now()

            # Очистка старых записей
            self.minute_requests = [
                t for t in self.minute_requests
                if now - t < timedelta(minutes=1)
            ]
            self.hour_requests = [
                t for t in self.hour_requests
                if now - t < timedelta(hours=1)
            ]

            # Проверка лимитов
            if len(self.minute_requests) >= self.requests_per_minute:
                wait_time = 60 - (now - self.minute_requests[0]).seconds
                logger.info(f"Rate limit: waiting {wait_time}s (minute limit)")
                time.sleep(wait_time + random.uniform(1, 3))

            if len(self.hour_requests) >= self.requests_per_hour:
                wait_time = 3600 - (now - self.hour_requests[0]).seconds
                logger.warning(f"Rate limit: waiting {wait_time}s (hour limit)")
                time.sleep(wait_time + random.uniform(1, 5))

            # Случайная задержка
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)

            # Запись запроса
            self.minute_requests.append(datetime.now())
            self.hour_requests.append(datetime.now())

    def __call__(self, func):
        """Декоратор для rate limiting."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


# =============================================================================
# Price Extractor
# =============================================================================

class PriceExtractor:
    """Извлечение цен из текста."""

    # Паттерны для разных валют
    PRICE_PATTERNS = [
        # AED patterns
        (r'(?:AED|aed|Aed)\s*(\d+(?:[,.]?\d+)*)', 'AED'),
        (r'(\d+(?:[,.]?\d+)*)\s*(?:AED|aed|Aed)', 'AED'),
        (r'(\d+(?:[,.]?\d+)*)\s*(?:dirhams?|дирхам)', 'AED'),

        # USD patterns
        (r'\$\s*(\d+(?:[,.]?\d+)*)', 'USD'),
        (r'(?:USD|usd)\s*(\d+(?:[,.]?\d+)*)', 'USD'),
        (r'(\d+(?:[,.]?\d+)*)\s*(?:USD|usd|\$)', 'USD'),
        (r'(\d+(?:[,.]?\d+)*)\s*(?:dollars?|долларов)', 'USD'),

        # Euro patterns
        (r'(\d+(?:[,.]?\d+)*)\s*(?:EUR|eur|\u20ac)', 'EUR'),
        (r'(?:EUR|eur|\u20ac)\s*(\d+(?:[,.]?\d+)*)', 'EUR'),

        # Generic price indicators
        (r'(?:price|Price|PRICE)[:\s]*(\d+(?:[,.]?\d+)*)', 'AED'),
        (r'(?:from|From|FROM)[:\s]*(\d+(?:[,.]?\d+)*)', 'AED'),
        (r'(?:starting|Starting)[:\s]*(\d+(?:[,.]?\d+)*)', 'AED'),
        (r'(?:only|Only|ONLY)[:\s]*(\d+(?:[,.]?\d+)*)', 'AED'),
    ]

    # Контекст для определения продукта
    PRODUCT_KEYWORDS = {
        'desert_safari': [
            'desert safari', 'сафари', 'safari', 'dune bashing',
            'camel ride', 'bbq dinner', 'desert tour'
        ],
        'city_tour': [
            'city tour', 'dubai tour', 'abu dhabi tour', 'экскурсия',
            'sightseeing', 'city sightseeing'
        ],
        'yacht': [
            'yacht', 'яхта', 'boat', 'cruise', 'marina'
        ],
        'helicopter': [
            'helicopter', 'вертолет', 'heli tour', 'aerial'
        ],
        'aquarium': [
            'aquarium', 'аквариум', 'underwater zoo', 'dubai aquarium'
        ],
        'burj_khalifa': [
            'burj khalifa', 'бурдж халифа', 'at the top', 'observation deck'
        ],
        'ferrari_world': [
            'ferrari world', 'феррари', 'yas island'
        ],
        'transfer': [
            'transfer', 'трансфер', 'airport', 'pickup'
        ],
    }

    def extract_prices(self, text: str) -> List[Dict[str, Any]]:
        """Извлечь все цены из текста."""
        if not text:
            return []

        prices = []
        text_lower = text.lower()

        for pattern, currency in self.PRICE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Парсинг числа
                    price_str = match.group(1).replace(',', '').replace(' ', '')
                    price = float(price_str)

                    # Фильтрация нереалистичных цен
                    if price < 10 or price > 100000:
                        continue

                    # Определение продукта
                    product = self._detect_product(text_lower)

                    prices.append({
                        'price': price,
                        'currency': currency,
                        'product': product,
                        'raw_match': match.group(0),
                        'context': self._get_context(text, match.start(), match.end())
                    })
                except (ValueError, IndexError):
                    continue

        # Удаление дубликатов
        seen = set()
        unique_prices = []
        for p in prices:
            key = (p['price'], p['currency'])
            if key not in seen:
                seen.add(key)
                unique_prices.append(p)

        return unique_prices

    def _detect_product(self, text: str) -> str:
        """Определить тип продукта по тексту."""
        for product, keywords in self.PRODUCT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return product
        return 'unknown'

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Получить контекст вокруг найденной цены."""
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        return text[ctx_start:ctx_end].strip()


# =============================================================================
# Session Manager
# =============================================================================

class SessionManager:
    """Управление сессиями Instagram."""

    def __init__(self, sessions_dir: str = None):
        self.sessions_dir = Path(sessions_dir or os.path.expanduser("~/.instagram_sessions"))
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._current_session: Optional[str] = None

    def get_session_file(self, username: str) -> Path:
        """Получить путь к файлу сессии."""
        return self.sessions_dir / f"{username}_session"

    def save_session(self, loader: 'instaloader.Instaloader', username: str):
        """Сохранить сессию."""
        if not INSTALOADER_AVAILABLE:
            return

        session_file = self.get_session_file(username)
        loader.save_session_to_file(str(session_file))
        logger.info(f"Session saved for {username}")

    def load_session(self, loader: 'instaloader.Instaloader', username: str) -> bool:
        """Загрузить сессию."""
        if not INSTALOADER_AVAILABLE:
            return False

        session_file = self.get_session_file(username)
        if session_file.exists():
            try:
                loader.load_session_from_file(username, str(session_file))
                logger.info(f"Session loaded for {username}")
                self._current_session = username
                return True
            except Exception as e:
                logger.warning(f"Failed to load session: {e}")
        return False

    def login(
        self,
        loader: 'instaloader.Instaloader',
        username: str,
        password: str
    ) -> bool:
        """Войти в аккаунт и сохранить сессию."""
        if not INSTALOADER_AVAILABLE:
            return False

        try:
            loader.login(username, password)
            self.save_session(loader, username)
            self._current_session = username
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False


# =============================================================================
# Proxy Manager
# =============================================================================

class ProxyManager:
    """Управление прокси для обхода блокировок."""

    def __init__(self, proxies: List[str] = None):
        """
        Args:
            proxies: Список прокси в формате "protocol://user:pass@host:port"
        """
        self.proxies = proxies or []
        self._current_index = 0
        self._failed_proxies: set = set()

    def add_proxy(self, proxy: str):
        """Добавить прокси."""
        if proxy not in self.proxies:
            self.proxies.append(proxy)

    def get_proxy(self) -> Optional[str]:
        """Получить следующий рабочий прокси."""
        if not self.proxies:
            return None

        available = [p for p in self.proxies if p not in self._failed_proxies]
        if not available:
            # Сброс списка нерабочих прокси
            self._failed_proxies.clear()
            available = self.proxies

        proxy = available[self._current_index % len(available)]
        self._current_index += 1
        return proxy

    def mark_failed(self, proxy: str):
        """Пометить прокси как нерабочий."""
        self._failed_proxies.add(proxy)
        logger.warning(f"Proxy marked as failed: {proxy}")

    def configure_loader(self, loader: 'instaloader.Instaloader'):
        """Настроить instaloader для использования прокси."""
        proxy = self.get_proxy()
        if proxy:
            # instaloader использует requests под капотом
            loader.context._session.proxies = {
                'http': proxy,
                'https': proxy
            }
            logger.info(f"Using proxy: {proxy[:30]}...")


# =============================================================================
# Main Instagram Parser
# =============================================================================

class InstagramParser:
    """Основной парсер Instagram для анализа конкурентов."""

    # Список конкурентов по умолчанию (туризм в ОАЭ)
    DEFAULT_COMPETITORS = [
        # Desert Safari
        "dubaidesertsafari",
        "desertsafaridubai",
        "arabian_adventures",
        "platinumheritage",

        # Tours & Activities
        "visitdubai",
        "dubai_tourism",
        "dubaitourism",
        "exploredubai",

        # Luxury Tours
        "luxurytourdubai",
        "vip_dubai_tours",
        "dubai_luxury_travel",

        # Specific Activities
        "dubaimarina.yacht",
        "dubai_helicopter_tour",
        "skydive_dubai",
    ]

    # Популярные хэштеги для мониторинга
    TARGET_HASHTAGS = [
        "dubaitour",
        "dubaisafari",
        "desertsafari",
        "dubaicitytour",
        "dubaitrip",
        "visitdubai",
        "dubaiactivities",
        "dubaiexperience",
        "aaborates",
        "exploredubai",
    ]

    def __init__(
        self,
        data_dir: str = None,
        login_username: str = None,
        login_password: str = None,
        use_proxy: bool = False,
        proxies: List[str] = None
    ):
        """
        Инициализация парсера.

        Args:
            data_dir: Директория для хранения данных
            login_username: Username для входа (опционально)
            login_password: Password для входа (опционально)
            use_proxy: Использовать прокси
            proxies: Список прокси
        """
        self.data_dir = Path(data_dir or os.path.expanduser("~/.instagram_parser"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Поддиректории
        self.cache_dir = self.data_dir / "cache"
        self.reports_dir = self.data_dir / "reports"
        self.prices_dir = self.data_dir / "prices"

        for d in [self.cache_dir, self.reports_dir, self.prices_dir]:
            d.mkdir(exist_ok=True)

        # Компоненты
        self.rate_limiter = RateLimiter()
        self.price_extractor = PriceExtractor()
        self.session_manager = SessionManager(str(self.data_dir / "sessions"))
        self.proxy_manager = ProxyManager(proxies) if use_proxy else None

        # Данные
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.price_history: List[PriceEntry] = []
        self.alerts: List[PriceAlert] = []

        # Наши цены для сравнения
        self.our_prices: Dict[str, Dict[str, float]] = {}

        # Инициализация instaloader
        self.loader = None
        self._init_loader(login_username, login_password)

        # Загрузка кэшированных данных
        self._load_cached_data()

    def _init_loader(self, username: str = None, password: str = None):
        """Инициализация instaloader."""
        if not INSTALOADER_AVAILABLE:
            logger.warning("instaloader not available, running in limited mode")
            return

        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True
        )

        # Настройка прокси
        if self.proxy_manager:
            self.proxy_manager.configure_loader(self.loader)

        # Попытка загрузить сессию или войти
        if username:
            if not self.session_manager.load_session(self.loader, username):
                if password:
                    self.session_manager.login(self.loader, username, password)

    def _load_cached_data(self):
        """Загрузить кэшированные данные."""
        # Загрузка конкурентов
        competitors_file = self.cache_dir / "competitors.json"
        if competitors_file.exists():
            try:
                with open(competitors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for username, profile_data in data.items():
                        profile_data['last_updated'] = (
                            datetime.fromisoformat(profile_data['last_updated'])
                            if profile_data.get('last_updated') else None
                        )
                        profile_data['posts'] = [
                            Post(
                                **{**p, 'timestamp': datetime.fromisoformat(p['timestamp'])}
                            ) for p in profile_data.get('posts', [])
                        ]
                        self.competitors[username] = CompetitorProfile(**profile_data)
            except Exception as e:
                logger.warning(f"Failed to load cached competitors: {e}")

        # Загрузка истории цен
        prices_file = self.prices_dir / "price_history.json"
        if prices_file.exists():
            try:
                with open(prices_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.price_history = [
                        PriceEntry(
                            **{**p, 'extracted_at': datetime.fromisoformat(p['extracted_at'])}
                        ) for p in data
                    ]
            except Exception as e:
                logger.warning(f"Failed to load price history: {e}")

    def _save_cached_data(self):
        """Сохранить данные в кэш."""
        # Сохранение конкурентов
        competitors_file = self.cache_dir / "competitors.json"
        try:
            data = {}
            for username, profile in self.competitors.items():
                profile_dict = asdict(profile)
                profile_dict['last_updated'] = (
                    profile.last_updated.isoformat()
                    if profile.last_updated else None
                )
                profile_dict['posts'] = [
                    {**asdict(p), 'timestamp': p.timestamp.isoformat()}
                    for p in profile.posts
                ]
                data[username] = profile_dict

            with open(competitors_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save competitors cache: {e}")

        # Сохранение истории цен
        prices_file = self.prices_dir / "price_history.json"
        try:
            data = [
                {**asdict(p), 'extracted_at': p.extracted_at.isoformat()}
                for p in self.price_history
            ]
            with open(prices_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save price history: {e}")

    # =========================================================================
    # Competitor Management
    # =========================================================================

    def add_competitor(self, username: str) -> bool:
        """Добавить конкурента для мониторинга."""
        username = username.lower().strip().lstrip('@')

        if username in self.competitors:
            logger.info(f"Competitor {username} already added")
            return True

        self.competitors[username] = CompetitorProfile(username=username)
        logger.info(f"Added competitor: {username}")
        return True

    def remove_competitor(self, username: str):
        """Удалить конкурента из мониторинга."""
        username = username.lower().strip()
        if username in self.competitors:
            del self.competitors[username]
            logger.info(f"Removed competitor: {username}")

    def add_default_competitors(self):
        """Добавить конкурентов по умолчанию."""
        for username in self.DEFAULT_COMPETITORS:
            self.add_competitor(username)

    # =========================================================================
    # Data Collection
    # =========================================================================

    @RateLimiter(requests_per_minute=5, min_delay=5.0, max_delay=15.0)
    def fetch_profile(self, username: str) -> Optional[CompetitorProfile]:
        """Получить профиль конкурента."""
        if not self.loader:
            logger.error("Instaloader not initialized")
            return None

        username = username.lower().strip()

        try:
            profile = instaloader.Profile.from_username(
                self.loader.context, username
            )

            competitor = CompetitorProfile(
                username=profile.username,
                full_name=profile.full_name or "",
                biography=profile.biography or "",
                followers=profile.followers,
                following=profile.followees,
                posts_count=profile.mediacount,
                is_business=profile.is_business_account,
                business_category=profile.business_category_name or "",
                external_url=profile.external_url or "",
                last_updated=datetime.now()
            )

            self.competitors[username] = competitor
            logger.info(f"Fetched profile: {username} ({profile.followers} followers)")

            return competitor

        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Profile not found: {username}")
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error for {username}: {e}")
            if self.proxy_manager:
                self.proxy_manager.mark_failed(
                    self.proxy_manager.get_proxy()
                )
        except Exception as e:
            logger.error(f"Error fetching profile {username}: {e}")

        return None

    def fetch_posts(
        self,
        username: str,
        max_posts: int = 30,
        since: datetime = None
    ) -> List[Post]:
        """Получить посты конкурента."""
        if not self.loader:
            logger.error("Instaloader not initialized")
            return []

        username = username.lower().strip()

        try:
            profile = instaloader.Profile.from_username(
                self.loader.context, username
            )

            posts = []
            since = since or datetime.now() - timedelta(days=30)

            for post in profile.get_posts():
                # Rate limiting
                self.rate_limiter.wait()

                if len(posts) >= max_posts:
                    break

                if post.date_utc < since:
                    break

                # Извлечение хэштегов
                hashtags = list(post.caption_hashtags) if post.caption_hashtags else []

                # Извлечение упоминаний
                mentions = list(post.caption_mentions) if post.caption_mentions else []

                # Извлечение цен
                caption = post.caption or ""
                extracted_prices = self.price_extractor.extract_prices(caption)

                post_data = Post(
                    shortcode=post.shortcode,
                    caption=caption,
                    likes=post.likes,
                    comments=post.comments,
                    timestamp=post.date_utc,
                    hashtags=hashtags,
                    mentions=mentions,
                    is_video=post.is_video,
                    video_view_count=post.video_view_count if post.is_video else None,
                    location=post.location.name if post.location else None,
                    extracted_prices=extracted_prices
                )

                posts.append(post_data)

                # Сохранение цен
                for price_info in extracted_prices:
                    self._record_price(
                        competitor=username,
                        product=price_info['product'],
                        price=price_info['price'],
                        currency=price_info['currency'],
                        post_url=post_data.url,
                        raw_text=price_info['context']
                    )

            # Обновление профиля
            if username in self.competitors:
                self.competitors[username].posts = posts
                self.competitors[username].last_updated = datetime.now()

            logger.info(f"Fetched {len(posts)} posts from {username}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching posts from {username}: {e}")
            return []

    def fetch_hashtag_posts(
        self,
        hashtag: str,
        max_posts: int = 50
    ) -> List[Post]:
        """Получить посты по хэштегу."""
        if not self.loader:
            logger.error("Instaloader not initialized")
            return []

        hashtag = hashtag.lower().strip().lstrip('#')

        try:
            posts = []

            for post in instaloader.Hashtag.from_name(
                self.loader.context, hashtag
            ).get_posts():
                self.rate_limiter.wait()

                if len(posts) >= max_posts:
                    break

                hashtags = list(post.caption_hashtags) if post.caption_hashtags else []
                mentions = list(post.caption_mentions) if post.caption_mentions else []
                caption = post.caption or ""
                extracted_prices = self.price_extractor.extract_prices(caption)

                post_data = Post(
                    shortcode=post.shortcode,
                    caption=caption,
                    likes=post.likes,
                    comments=post.comments,
                    timestamp=post.date_utc,
                    hashtags=hashtags,
                    mentions=mentions,
                    is_video=post.is_video,
                    video_view_count=post.video_view_count if post.is_video else None,
                    location=post.location.name if post.location else None,
                    extracted_prices=extracted_prices
                )

                posts.append(post_data)

            logger.info(f"Fetched {len(posts)} posts for #{hashtag}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching hashtag {hashtag}: {e}")
            return []

    # =========================================================================
    # Price Tracking
    # =========================================================================

    def _record_price(
        self,
        competitor: str,
        product: str,
        price: float,
        currency: str,
        post_url: str,
        raw_text: str
    ):
        """Записать цену и проверить на изменения."""
        entry = PriceEntry(
            competitor=competitor,
            product=product,
            price=price,
            currency=currency,
            post_url=post_url,
            extracted_at=datetime.now(),
            raw_text=raw_text
        )

        # Проверка на изменение цены
        previous = self._get_previous_price(competitor, product, currency)
        if previous and abs(previous.price - price) > 0.01:
            change_percent = ((price - previous.price) / previous.price) * 100

            alert = PriceAlert(
                competitor=competitor,
                product=product,
                old_price=previous.price,
                new_price=price,
                change_percent=change_percent,
                currency=currency,
                detected_at=datetime.now(),
                post_url=post_url
            )

            self.alerts.append(alert)
            logger.warning(
                f"Price change alert: {competitor} - {product}: "
                f"{previous.price} -> {price} {currency} ({change_percent:+.1f}%)"
            )

        self.price_history.append(entry)

    def _get_previous_price(
        self,
        competitor: str,
        product: str,
        currency: str
    ) -> Optional[PriceEntry]:
        """Получить предыдущую цену для сравнения."""
        relevant = [
            p for p in self.price_history
            if p.competitor == competitor
            and p.product == product
            and p.currency == currency
        ]

        if not relevant:
            return None

        # Последняя запись
        return max(relevant, key=lambda x: x.extracted_at)

    def set_our_prices(self, prices: Dict[str, Dict[str, float]]):
        """
        Установить наши цены для сравнения.

        Args:
            prices: {product: {currency: price}}
        """
        self.our_prices = prices

    def compare_with_our_prices(self) -> List[Dict[str, Any]]:
        """Сравнить цены конкурентов с нашими."""
        comparisons = []

        for entry in self.price_history:
            if entry.product not in self.our_prices:
                continue

            our_price = self.our_prices[entry.product].get(entry.currency)
            if our_price is None:
                continue

            diff = entry.price - our_price
            diff_percent = (diff / our_price) * 100

            comparisons.append({
                'competitor': entry.competitor,
                'product': entry.product,
                'competitor_price': entry.price,
                'our_price': our_price,
                'currency': entry.currency,
                'difference': diff,
                'difference_percent': diff_percent,
                'post_url': entry.post_url,
                'extracted_at': entry.extracted_at
            })

        return comparisons

    # =========================================================================
    # Analysis
    # =========================================================================

    def analyze_competitor(self, username: str) -> Dict[str, Any]:
        """Полный анализ конкурента."""
        username = username.lower().strip()

        if username not in self.competitors:
            self.fetch_profile(username)

        if username not in self.competitors:
            return {'error': f'Could not fetch profile: {username}'}

        profile = self.competitors[username]

        # Получение постов если нет
        if not profile.posts:
            self.fetch_posts(username)
            profile = self.competitors[username]

        # Анализ хэштегов
        all_hashtags = []
        for post in profile.posts:
            all_hashtags.extend(post.hashtags)

        hashtag_counter = Counter(all_hashtags)

        # Анализ частоты постов
        if profile.posts:
            dates = [p.timestamp for p in profile.posts]
            date_range = (max(dates) - min(dates)).days or 1
            posts_per_day = len(profile.posts) / date_range
            posts_per_week = posts_per_day * 7
        else:
            posts_per_day = 0
            posts_per_week = 0

        # Средние метрики
        avg_likes = sum(p.likes for p in profile.posts) / len(profile.posts) if profile.posts else 0
        avg_comments = sum(p.comments for p in profile.posts) / len(profile.posts) if profile.posts else 0

        # Все извлеченные цены
        all_prices = []
        for post in profile.posts:
            all_prices.extend(post.extracted_prices)

        return {
            'username': username,
            'full_name': profile.full_name,
            'followers': profile.followers,
            'following': profile.following,
            'posts_count': profile.posts_count,
            'is_business': profile.is_business,
            'business_category': profile.business_category,
            'external_url': profile.external_url,
            'engagement_rate': profile.engagement_rate,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'posts_per_week': posts_per_week,
            'top_hashtags': hashtag_counter.most_common(20),
            'prices_found': all_prices,
            'analyzed_posts': len(profile.posts),
            'last_updated': profile.last_updated.isoformat() if profile.last_updated else None
        }

    def analyze_all_competitors(self) -> Dict[str, Any]:
        """Анализ всех конкурентов."""
        results = {}

        for username in list(self.competitors.keys()):
            logger.info(f"Analyzing competitor: {username}")
            results[username] = self.analyze_competitor(username)

        # Сохранение кэша
        self._save_cached_data()

        return results

    def get_popular_hashtags(self, top_n: int = 30) -> List[Tuple[str, int]]:
        """Получить популярные хэштеги среди конкурентов."""
        all_hashtags = []

        for profile in self.competitors.values():
            for post in profile.posts:
                all_hashtags.extend(post.hashtags)

        return Counter(all_hashtags).most_common(top_n)

    def get_posting_patterns(self) -> Dict[str, Any]:
        """Анализ паттернов публикации."""
        patterns = {
            'by_weekday': Counter(),
            'by_hour': Counter(),
            'by_competitor': {}
        }

        for username, profile in self.competitors.items():
            competitor_patterns = {
                'weekdays': Counter(),
                'hours': Counter()
            }

            for post in profile.posts:
                weekday = post.timestamp.strftime('%A')
                hour = post.timestamp.hour

                patterns['by_weekday'][weekday] += 1
                patterns['by_hour'][hour] += 1

                competitor_patterns['weekdays'][weekday] += 1
                competitor_patterns['hours'][hour] += 1

            patterns['by_competitor'][username] = competitor_patterns

        return patterns

    # =========================================================================
    # Reports
    # =========================================================================

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Генерация еженедельного отчета."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'period': 'weekly',
            'competitors_summary': [],
            'price_changes': [],
            'top_hashtags': [],
            'recommendations': []
        }

        # Сбор данных за последнюю неделю
        week_ago = datetime.now() - timedelta(days=7)

        for username, profile in self.competitors.items():
            weekly_posts = [
                p for p in profile.posts
                if p.timestamp >= week_ago
            ]

            if weekly_posts:
                total_likes = sum(p.likes for p in weekly_posts)
                total_comments = sum(p.comments for p in weekly_posts)

                report['competitors_summary'].append({
                    'username': username,
                    'posts_this_week': len(weekly_posts),
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'engagement_rate': profile.engagement_rate,
                    'followers': profile.followers
                })

        # Изменения цен
        for alert in self.alerts:
            if alert.detected_at >= week_ago:
                report['price_changes'].append({
                    'competitor': alert.competitor,
                    'product': alert.product,
                    'old_price': alert.old_price,
                    'new_price': alert.new_price,
                    'change_percent': alert.change_percent,
                    'currency': alert.currency,
                    'post_url': alert.post_url
                })

        # Топ хэштеги
        report['top_hashtags'] = self.get_popular_hashtags(15)

        # Рекомендации
        report['recommendations'] = self._generate_recommendations(report)

        # Сохранение отчета
        report_file = self.reports_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"Weekly report saved: {report_file}")

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций на основе анализа."""
        recommendations = []

        # Анализ engagement rate
        engagement_rates = [
            (c['username'], c['engagement_rate'])
            for c in report['competitors_summary']
            if c['engagement_rate'] > 0
        ]

        if engagement_rates:
            avg_er = sum(er for _, er in engagement_rates) / len(engagement_rates)
            best_performer = max(engagement_rates, key=lambda x: x[1])

            recommendations.append(
                f"Average competitor engagement rate: {avg_er:.2f}%. "
                f"Best performer: @{best_performer[0]} ({best_performer[1]:.2f}%)"
            )

        # Анализ частоты постинга
        posting_frequencies = [
            c['posts_this_week'] for c in report['competitors_summary']
        ]

        if posting_frequencies:
            avg_posts = sum(posting_frequencies) / len(posting_frequencies)
            recommendations.append(
                f"Competitors post an average of {avg_posts:.1f} times per week. "
                f"Consider matching or exceeding this frequency."
            )

        # Рекомендации по хэштегам
        if report['top_hashtags']:
            top_tags = [f"#{tag}" for tag, _ in report['top_hashtags'][:5]]
            recommendations.append(
                f"Top performing hashtags: {', '.join(top_tags)}"
            )

        # Рекомендации по ценам
        if report['price_changes']:
            decreased = [p for p in report['price_changes'] if p['change_percent'] < 0]
            increased = [p for p in report['price_changes'] if p['change_percent'] > 0]

            if decreased:
                recommendations.append(
                    f"{len(decreased)} competitor(s) decreased prices. "
                    f"Review your pricing strategy."
                )

            if increased:
                recommendations.append(
                    f"{len(increased)} competitor(s) increased prices. "
                    f"Opportunity to capture price-sensitive customers."
                )

        return recommendations

    def generate_price_trend_report(
        self,
        product: str = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Отчет по трендам цен."""
        since = datetime.now() - timedelta(days=days)

        relevant_prices = [
            p for p in self.price_history
            if p.extracted_at >= since
            and (product is None or p.product == product)
        ]

        # Группировка по продуктам и конкурентам
        trends = {}

        for entry in relevant_prices:
            key = (entry.competitor, entry.product, entry.currency)
            if key not in trends:
                trends[key] = []
            trends[key].append({
                'price': entry.price,
                'date': entry.extracted_at.isoformat()
            })

        # Расчет статистики
        report = {
            'period_days': days,
            'product_filter': product,
            'trends': []
        }

        for (competitor, prod, currency), prices in trends.items():
            if len(prices) < 2:
                continue

            price_values = [p['price'] for p in prices]

            report['trends'].append({
                'competitor': competitor,
                'product': prod,
                'currency': currency,
                'min_price': min(price_values),
                'max_price': max(price_values),
                'avg_price': sum(price_values) / len(price_values),
                'price_volatility': max(price_values) - min(price_values),
                'data_points': len(prices),
                'history': prices
            })

        return report

    def export_to_dataframe(self) -> Optional['pd.DataFrame']:
        """Экспорт данных в pandas DataFrame."""
        if not PANDAS_AVAILABLE:
            logger.error("pandas not available")
            return None

        data = []

        for username, profile in self.competitors.items():
            for post in profile.posts:
                data.append({
                    'competitor': username,
                    'shortcode': post.shortcode,
                    'timestamp': post.timestamp,
                    'likes': post.likes,
                    'comments': post.comments,
                    'hashtags': ','.join(post.hashtags),
                    'is_video': post.is_video,
                    'video_views': post.video_view_count,
                    'location': post.location,
                    'url': post.url,
                    'caption_length': len(post.caption),
                    'prices_found': len(post.extracted_prices)
                })

        df = pd.DataFrame(data)
        return df

    def export_prices_to_dataframe(self) -> Optional['pd.DataFrame']:
        """Экспорт истории цен в DataFrame."""
        if not PANDAS_AVAILABLE:
            logger.error("pandas not available")
            return None

        data = [asdict(p) for p in self.price_history]
        return pd.DataFrame(data)

    # =========================================================================
    # Scheduling
    # =========================================================================

    def schedule_daily_update(self, time_str: str = "08:00"):
        """Запланировать ежедневное обновление."""
        if not SCHEDULE_AVAILABLE:
            logger.error("schedule not available")
            return

        def job():
            logger.info("Running scheduled daily update...")
            for username in list(self.competitors.keys()):
                try:
                    self.fetch_posts(username, max_posts=10)
                except Exception as e:
                    logger.error(f"Error updating {username}: {e}")
            self._save_cached_data()

        schedule.every().day.at(time_str).do(job)
        logger.info(f"Daily update scheduled at {time_str}")

    def schedule_weekly_report(self, day: str = "monday", time_str: str = "09:00"):
        """Запланировать еженедельный отчет."""
        if not SCHEDULE_AVAILABLE:
            logger.error("schedule not available")
            return

        def job():
            logger.info("Generating scheduled weekly report...")
            self.generate_weekly_report()

        getattr(schedule.every(), day).at(time_str).do(job)
        logger.info(f"Weekly report scheduled for {day} at {time_str}")

    def run_scheduler(self):
        """Запустить планировщик (блокирующий)."""
        if not SCHEDULE_AVAILABLE:
            logger.error("schedule not available")
            return

        logger.info("Scheduler started. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Точка входа для CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Instagram Parser for Competitor Analysis"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Команда: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analyze competitor')
    analyze_parser.add_argument('username', help='Instagram username')
    analyze_parser.add_argument('--posts', type=int, default=30, help='Max posts to fetch')

    # Команда: report
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('--type', choices=['weekly', 'prices'], default='weekly')

    # Команда: hashtag
    hashtag_parser = subparsers.add_parser('hashtag', help='Analyze hashtag')
    hashtag_parser.add_argument('hashtag', help='Hashtag to analyze')
    hashtag_parser.add_argument('--posts', type=int, default=50, help='Max posts')

    # Команда: add
    add_parser = subparsers.add_parser('add', help='Add competitor')
    add_parser.add_argument('username', help='Instagram username')

    # Команда: list
    list_parser = subparsers.add_parser('list', help='List competitors')

    # Команда: run
    run_parser = subparsers.add_parser('run', help='Run scheduler')

    args = parser.parse_args()

    # Инициализация парсера
    ig_parser = InstagramParser(
        login_username=os.getenv('INSTAGRAM_USERNAME'),
        login_password=os.getenv('INSTAGRAM_PASSWORD')
    )

    if args.command == 'analyze':
        result = ig_parser.analyze_competitor(args.username)
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False))

    elif args.command == 'report':
        if args.type == 'weekly':
            report = ig_parser.generate_weekly_report()
        else:
            report = ig_parser.generate_price_trend_report()
        print(json.dumps(report, indent=2, default=str, ensure_ascii=False))

    elif args.command == 'hashtag':
        posts = ig_parser.fetch_hashtag_posts(args.hashtag, max_posts=args.posts)
        for post in posts:
            print(f"[{post.timestamp}] {post.likes} likes - {post.url}")

    elif args.command == 'add':
        ig_parser.add_competitor(args.username)
        ig_parser._save_cached_data()
        print(f"Added competitor: {args.username}")

    elif args.command == 'list':
        for username in ig_parser.competitors:
            profile = ig_parser.competitors[username]
            print(f"@{username} - {profile.followers} followers")

    elif args.command == 'run':
        ig_parser.add_default_competitors()
        ig_parser.schedule_daily_update("08:00")
        ig_parser.schedule_weekly_report("monday", "09:00")
        ig_parser.run_scheduler()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
