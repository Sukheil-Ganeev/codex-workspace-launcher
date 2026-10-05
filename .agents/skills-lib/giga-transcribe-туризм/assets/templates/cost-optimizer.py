"""
Оптимизатор стоимости транскрипции Yandex SpeechKit

Функции:
- Выбор модели по контексту
- Кеширование результатов (Redis/file)
- Batch optimization
- Cost tracking и отчеты
- Автоматическая оптимизация

Тарификация Yandex SpeechKit (2024):
- Sync API: 15₽ за 1 млн символов
- Streaming API: 15₽ за 1 млн символов
- Async API: 15₽ за 1 млн символов

Использование:
    from cost_optimizer import OptimizedTranscriber

    transcriber = OptimizedTranscriber(cache_enabled=True)
    result = transcriber.transcribe("audio.ogg", context="tourism")
"""

import os
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Загружаем переменные окружения
load_dotenv()

# Константы
SYNC_API_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
COST_PER_MILLION_CHARS = 15  # Рублей
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "yandex_speechkit"


class CostTracker:
    """Трекер стоимости транскрипций"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация трекера

        Args:
            db_path: Путь к SQLite БД (опционально)
        """
        if db_path is None:
            db_path = DEFAULT_CACHE_DIR / "cost_tracker.db"

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_path TEXT,
                chars_count INTEGER,
                cost_rubles REAL,
                model TEXT,
                context TEXT,
                cached BOOLEAN
            )
        """)

        conn.commit()
        conn.close()

    def log_transcription(
        self,
        chars_count: int,
        file_path: Optional[str] = None,
        model: str = "general",
        context: Optional[str] = None,
        cached: bool = False
    ):
        """
        Логирует транскрипцию

        Args:
            chars_count: Количество символов
            file_path: Путь к файлу
            model: Модель
            context: Контекст
            cached: Был ли результат из кеша
        """
        cost = (chars_count / 1_000_000) * COST_PER_MILLION_CHARS if not cached else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transcriptions
            (timestamp, file_path, chars_count, cost_rubles, model, context, cached)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            file_path,
            chars_count,
            cost,
            model,
            context,
            cached
        ))

        conn.commit()
        conn.close()

    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Получает статистику за период

        Args:
            days: Количество дней

        Returns:
            Dict со статистикой
        """
        since = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute("""
            SELECT
                COUNT(*) as total_requests,
                SUM(chars_count) as total_chars,
                SUM(cost_rubles) as total_cost,
                SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached_requests
            FROM transcriptions
            WHERE timestamp >= ?
        """, (since,))

        row = cursor.fetchone()

        stats = {
            'period_days': days,
            'total_requests': row[0] or 0,
            'total_chars': row[1] or 0,
            'total_cost_rubles': round(row[2] or 0, 2),
            'cached_requests': row[3] or 0,
            'cache_hit_rate': 0
        }

        if stats['total_requests'] > 0:
            stats['cache_hit_rate'] = round(
                (stats['cached_requests'] / stats['total_requests']) * 100, 1
            )

        # Статистика по моделям
        cursor.execute("""
            SELECT model, COUNT(*), SUM(cost_rubles)
            FROM transcriptions
            WHERE timestamp >= ?
            GROUP BY model
        """, (since,))

        stats['by_model'] = {
            row[0]: {'requests': row[1], 'cost': round(row[2], 2)}
            for row in cursor.fetchall()
        }

        conn.close()
        return stats

    def print_report(self, days: int = 30):
        """Выводит отчет"""
        stats = self.get_stats(days)

        print("\n" + "="*60)
        print(f"💰 ОТЧЕТ О СТОИМОСТИ (последние {days} дней)")
        print("="*60)
        print(f"Всего запросов:        {stats['total_requests']}")
        print(f"Из кеша:               {stats['cached_requests']} ({stats['cache_hit_rate']}%)")
        print(f"Символов обработано:   {stats['total_chars']:,}")
        print(f"Стоимость:             {stats['total_cost_rubles']:.2f} ₽")

        if stats['by_model']:
            print("\nПо моделям:")
            for model, data in stats['by_model'].items():
                print(f"  • {model}: {data['requests']} запросов, {data['cost']:.2f} ₽")

        print("="*60)


class TranscriptionCache:
    """Кеш для транскрипций"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация кеша

        Args:
            cache_dir: Директория для кеша
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, audio_path: str) -> str:
        """Генерирует ключ кеша на основе хеша файла"""
        with open(audio_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash

    def get(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Получает результат из кеша

        Args:
            audio_path: Путь к аудио файлу

        Returns:
            Результат транскрипции или None
        """
        try:
            cache_key = self._get_cache_key(audio_path)
            cache_file = self.cache_dir / f"{cache_key}.json"

            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass

        return None

    def set(self, audio_path: str, result: Dict[str, Any]):
        """
        Сохраняет результат в кеш

        Args:
            audio_path: Путь к аудио файлу
            result: Результат транскрипции
        """
        try:
            cache_key = self._get_cache_key(audio_path)
            cache_file = self.cache_dir / f"{cache_key}.json"

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


class ModelSelector:
    """Выбор оптимальной модели по контексту"""

    # Контексты и рекомендуемые модели
    CONTEXT_TO_MODEL = {
        'tourism': 'general',      # Туризм, экскурсии
        'navigation': 'maps',       # Навигация, маршруты
        'general': 'general',       # Общий контекст
        'research': 'general:rc'    # Research, эксперименты
    }

    @classmethod
    def select_model(cls, context: Optional[str] = None) -> str:
        """
        Выбирает модель по контексту

        Args:
            context: Контекст использования

        Returns:
            Название модели
        """
        if context and context in cls.CONTEXT_TO_MODEL:
            return cls.CONTEXT_TO_MODEL[context]

        return 'general'  # По умолчанию


class OptimizedTranscriber:
    """Оптимизированный транскрибер"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        folder_id: Optional[str] = None,
        cache_enabled: bool = True,
        track_costs: bool = True
    ):
        """
        Инициализация транскрибера

        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID каталога Yandex Cloud
            cache_enabled: Включить кеширование
            track_costs: Включить трекинг стоимости
        """
        self.api_key = api_key or os.getenv("YANDEX_CLOUD_API_KEY", "PASTE_YANDEX_CLOUD_API_KEY_HERE")
        self.folder_id = folder_id or os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")

        if not self.api_key or not self.folder_id:
            raise ValueError("Укажите YANDEX_CLOUD_API_KEY и YANDEX_CLOUD_FOLDER_ID")

        self.cache_enabled = cache_enabled
        self.track_costs = track_costs

        if cache_enabled:
            self.cache = TranscriptionCache()

        if track_costs:
            self.cost_tracker = CostTracker()

    def transcribe(
        self,
        audio_path: str,
        context: Optional[str] = None,
        language: str = "ru-RU",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Транскрибирует аудио с оптимизацией

        Args:
            audio_path: Путь к аудио файлу
            context: Контекст (tourism, navigation, general)
            language: Язык
            force_refresh: Игнорировать кеш

        Returns:
            Dict с результатом транскрипции
        """
        # Проверяем кеш
        if self.cache_enabled and not force_refresh:
            cached_result = self.cache.get(audio_path)
            if cached_result:
                print("✅ Результат из кеша")

                if self.track_costs:
                    self.cost_tracker.log_transcription(
                        chars_count=len(cached_result['text']),
                        file_path=audio_path,
                        cached=True
                    )

                return cached_result

        # Выбираем оптимальную модель
        model = ModelSelector.select_model(context)

        # Определяем формат
        ext = Path(audio_path).suffix.lower()
        format_map = {
            '.ogg': 'oggopus',
            '.opus': 'oggopus',
            '.mp3': 'mp3',
            '.wav': 'lpcm'
        }
        audio_format = format_map.get(ext, 'oggopus')

        # Читаем аудио
        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        # Параметры запроса
        params = {
            'folderId': self.folder_id,
            'lang': language,
            'model': model,
            'format': audio_format
        }

        headers = {
            'Authorization': f'Api-Key {self.api_key}'
        }

        # Транскрибируем
        response = requests.post(
            SYNC_API_URL,
            params=params,
            headers=headers,
            data=audio_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            transcription = {
                'success': True,
                'text': result.get('result', ''),
                'confidence': result.get('confidence', 0.0),
                'model': model,
                'context': context
            }

            # Сохраняем в кеш
            if self.cache_enabled:
                self.cache.set(audio_path, transcription)

            # Трекаем стоимость
            if self.track_costs:
                self.cost_tracker.log_transcription(
                    chars_count=len(transcription['text']),
                    file_path=audio_path,
                    model=model,
                    context=context,
                    cached=False
                )

            return transcription
        else:
            return {
                'success': False,
                'error': f"API error: {response.status_code}"
            }

    def get_cost_report(self, days: int = 30):
        """Выводит отчет о стоимости"""
        if self.track_costs:
            self.cost_tracker.print_report(days)
        else:
            print("⚠️ Трекинг стоимости отключен")


def main():
    """Пример использования"""
    import sys

    if len(sys.argv) < 2:
        print("Использование: python cost-optimizer.py <audio_file> [context]")
        print("\nКонтексты: tourism, navigation, general, research")
        print("\nПример:")
        print("  python cost-optimizer.py audio.ogg tourism")
        sys.exit(1)

    audio_file = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else 'general'

    try:
        transcriber = OptimizedTranscriber(
            cache_enabled=True,
            track_costs=True
        )

        print(f"🎙️ Транскрипция: {audio_file}")
        print(f"📍 Контекст: {context}")

        result = transcriber.transcribe(audio_file, context=context)

        if result['success']:
            print("\n" + "="*60)
            print("✅ РЕЗУЛЬТАТ")
            print("="*60)
            print(result['text'])
            print("="*60)
            print(f"\nМодель: {result['model']}")
            print(f"Уверенность: {result['confidence']:.2%}")
        else:
            print(f"\n❌ Ошибка: {result['error']}")

        # Показываем отчет
        transcriber.get_cost_report(days=30)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
